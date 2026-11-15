"""Plan Open Logic edition maintenance using only Python 3.11+, Git and the public repositories."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import tomllib
from urllib.error import HTTPError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen


HUB = Path(__file__).resolve().parent
UPSTREAM = "https://github.com/OpenLogicProject/OpenLogic"
FULL_SHA = re.compile(r"[0-9a-f]{40}")


def sha(body):
    return hashlib.sha256(body).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)+"\n").encode()


def safe(name):
    path = PurePosixPath(name)
    if (not name or path.is_absolute() or path.as_posix()!=name or ".." in path.parts
            or any(c in name for c in "\\\x00\r\n:") or ".git" in path.parts):
        raise ValueError("unsafe repository path")
    return name


def git(*args, cwd=None, input_bytes=None):
    # Raw blob bytes, including original newlines, are used in every receipt.
    run = subprocess.run(["git",*map(str,args)],cwd=cwd,input=input_bytes,capture_output=True,
                         timeout=300,env={**os.environ,"GIT_TERMINAL_PROMPT":"0"})
    if run.returncode:
        raise ValueError("Git operation failed: "+str(args[0]))
    return run.stdout


def remote_file(repo, commit, name, optional=False):
    if not FULL_SHA.fullmatch(commit):
        raise ValueError("immutable edition commit required")
    url="https://raw.githubusercontent.com/"+repo+"/"+commit+"/"+quote(safe(name))
    try:
        with urlopen(Request(url,headers={"User-Agent":"OpenLogic-maintenance"}),timeout=40) as response:
            body=response.read(24*1024*1024+1)
    except HTTPError as error:
        if optional and error.code==404:
            return None
        raise
    if len(body)>24*1024*1024:
        raise ValueError("edition metadata or unit exceeds the single-file limit: "+name)
    return body


def edition_location(url):
    parsed=urlsplit(url)
    parts=parsed.path.strip("/").split("/")
    if (parsed.scheme!="https" or parsed.netloc!="github.com" or parsed.query or parsed.fragment
            or len(parts)<2 or any(not re.fullmatch(r"[A-Za-z0-9_.-]+",p) or p in (".","..") for p in parts)):
        raise ValueError("unsupported edition repository")
    if len(parts)!=2 and (len(parts)<5 or parts[2]!="tree"):
        raise ValueError("expected repository or named branch directory")
    return "/".join(parts[:2]),("refs/heads/"+parts[3] if len(parts)>2 else "HEAD"),"/".join(parts[4:])


def upstream_cache(cache):
    directory=cache/"upstream.git"
    if not directory.exists():
        directory.parent.mkdir(parents=True,exist_ok=True)
        git("init","--bare",directory)
        git("remote","add","origin",UPSTREAM+".git",cwd=directory)
    if git("remote","get-url","origin",cwd=directory).decode().strip()!=UPSTREAM+".git":
        raise ValueError("upstream cache points to a different repository")
    git("fetch","--filter=blob:none","--no-tags","origin",
        "+refs/heads/master:refs/heads/master",cwd=directory)
    return directory


def changes(cache, old, new):
    if not all(FULL_SHA.fullmatch(v) for v in (old,new)):
        raise ValueError("expected two full source commits")
    git("merge-base","--is-ancestor",old,new,cwd=cache)
    data=git("diff","--name-status","-z","-M",old,new,cwd=cache)
    fields=iter(data.decode("utf-8").split("\0")[:-1])
    rows=[]
    for status in fields:
        before=safe(next(fields))
        after=safe(next(fields)) if status.startswith(("R","C")) else before
        rows.append({"status":status,"before":None if status=="A" else before,
                     "after":None if status=="D" else after})
    return rows


def term_records(raw,path):
    text=raw.decode("utf-8-sig")
    if path.endswith(".jsonl"):
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    if path.endswith((".csv",".tsv")):
        return list(csv.DictReader(io.StringIO(text),delimiter="\t" if path.endswith(".tsv") else ","))
    return []


def content_unit(path):
    return bool(path and path.startswith("content/") and path.endswith(".tex"))


def write_technical_files(cache, old, new, delta, folder):
    """Keep build, style and data changes once per source baseline across editions."""
    folder.mkdir(parents=True)
    records = []
    for change in delta:
        if any(content_unit(path) for path in (change["before"], change["after"])):
            continue
        record = {"change": change, "files": {}}
        for label, revision in (("before", old), ("after", new)):
            path = change[label]
            if path is None:
                continue
            entry = git("ls-tree", "-z", revision, "--", path, cwd=cache)
            mode, kind, oid = entry.split(b"\t", 1)[0].decode().split()
            record["files"][label] = {"mode": mode, "kind": kind, "oid": oid}
            if kind == "blob":
                body = git("cat-file", "blob", oid, cwd=cache)
                destination = folder / oid
                if not destination.exists():
                    destination.write_bytes(body)
                record["files"][label]["sha256"] = sha(body)
        records.append(record)
    manifest = encode(records)
    (folder / "files.json").write_bytes(manifest)
    return sha(manifest)


def unit_packet(cache, old, new, change, edition, get, unit_map, indexes, term_rows, root):
    name=change["after"] or change["before"]
    key=unit_map.get(change["before"]) or unit_map.get(name)
    if not key:
        key="new-"+sha(name.encode())[:12]
    packet=root/"units"/key
    packet.mkdir(parents=True)
    files={}
    for label,pin,path in (("before",old,change["before"]),("after",new,change["after"])):
        if path:
            body=git("show",pin+":"+path,cwd=cache)
            (packet/(label+".tex")).write_bytes(body)
            files[label]={"path":path,"sha256":sha(body),
                         "git_blob":git("rev-parse",pin+":"+path,cwd=cache).decode().strip()}
    paths=list(dict.fromkeys(p for p in (change["before"],change["after"]) if p))
    patch=git("diff","--no-ext-diff","--no-textconv","--no-color",old,new,"--",*paths,cwd=cache)
    (packet/"source.diff").write_bytes(patch)
    changed="\n".join(l[1:] for l in patch.decode("utf-8").splitlines()
                      if l.startswith(("+","-")) and not l.startswith(("+++","---")))
    matching=[r for r in term_rows if isinstance(r.get("english"),str) and r["english"].strip()
              and re.search(r"(?<!\w)"+re.escape(r["english"].strip())+r"(?!\w)",changed,re.I)]
    issues=[]
    if content_unit(change["before"]) and edition.get("content"):
        target_path=edition["content"]+"/"+change["before"].removeprefix("content/")
        target=get(target_path,True)
        if target is not None:
            (packet/"current-target.tex").write_bytes(target)
            files["current_target"]={"path":target_path,"sha256":sha(target)}
        else:
            issues.append("current target absent at the edition commit")
        if indexes:
            row=indexes.get(change["before"],{})
            if (not row or row.get("src_blob")!=files["before"]["git_blob"]
                    or row.get("tr_sha256")!=files.get("current_target",{}).get("sha256")):
                issues.append("unit ledger does not match English or current target")
    record={"unit":key,"change":change,"files":files,"diff_sha256":sha(patch),
            "term_rows":matching,"issues":issues}
    (packet/"unit.json").write_bytes(encode(record))
    return {"unit":key,"path":name,"record_sha256":sha(encode(record)),"issues":issues}


def prepare(args):
    registry=tomllib.loads((HUB/"registry.toml").read_text("utf-8"))["editions"]
    config=json.loads((HUB/"maintenance/editions.json").read_bytes())
    published=json.loads((HUB/"catalogue/editions.json").read_bytes())
    catalog={e["id"]:e for e in published["editions"]}
    baseline=published["source_authority"]["commit"]
    unit_map={p:u for u,p in csv.reader((HUB/"olpkit/data/units/olp-units.tsv").read_text().splitlines()[1:],delimiter="\t")}
    selected=[r for r in registry if not args.edition or args.edition in (r["id"],r["locale"])]
    if not selected:
        raise ValueError("unknown edition")
    pinned_head = getattr(args, "edition_commit", None)
    if pinned_head and (len(selected) != 1 or not FULL_SHA.fullmatch(pinned_head)):
        raise ValueError("--edition-commit requires one edition and a full edition commit")
    cache=upstream_cache(args.cache.resolve())
    current=git("rev-parse","refs/heads/master",cwd=cache).decode().strip()
    goal=args.to or current
    if not FULL_SHA.fullmatch(goal):
        raise ValueError("--to must be a full immutable upstream commit")
    git("merge-base","--is-ancestor",goal,current,cwd=cache)
    destination=args.out.resolve()
    if destination.exists():
        raise ValueError("use a fresh output directory; existing packets are preserved")
    destination.parent.mkdir(parents=True,exist_ok=True)
    heads={}; deltas={}; reports=[]; technical={}
    with TemporaryDirectory(dir=destination.parent,prefix="olp-plan-") as scratch:
        root=Path(scratch)/"packets";root.mkdir()
        for row in selected:
            rid=row["id"]; folder=root/rid;folder.mkdir()
            config_row=config["editions"].get(rid,{})
            result={"id":rid,"locale":row["locale"],"repository":row["repository"],"issues":[]}
            reports.append(result)
            if rid=="openlogic-en-frozen-722" or not row["repository"]:
                result["status"]="frozen reference" if row["repository"] else "no edition repository"
                (folder/"edition.json").write_bytes(encode(result))
                continue
            repo,branch,prefix=edition_location(row["repository"])
            if not pinned_head and (repo,branch) not in heads:
                refs=git("ls-remote","--exit-code","https://github.com/"+repo+".git",branch).decode().splitlines()
                if len(refs)!=1:
                    raise ValueError("ambiguous edition revision: "+rid)
                heads[repo,branch]=refs[0].split()[0]
            head=pinned_head or heads[repo,branch];result["edition_commit"]=head
            def get(path,optional=False):
                return remote_file(repo,head,"/".join(x for x in (prefix,path) if x),optional)
            contract=get("olp-edition.toml",True)
            data=tomllib.loads(contract.decode("utf-8-sig")) if contract else {}
            if data.get("locale")!=row["locale"]:
                data={}
            old=catalog[rid].get("source_revision")
            if data:
                upstream=data["pins"]["olp"]
                if upstream["repository"].removesuffix(".git")!=UPSTREAM:
                    raise ValueError("unexpected source authority: "+rid)
                old=upstream["commit"]
                result["pin_evidence"]="olp-edition.toml"
                result["contract_sha256"]=sha(contract)
            elif old and FULL_SHA.fullmatch(old):
                result["pin_evidence"]="edition source_revision in catalogue"
            else:
                old=baseline
                result["pin_evidence"]="shared catalogue freeze only"
                result["issues"].append("verify edition-specific source pin before applying changes")
            result["from"]=old; result["to"]=goal
            if old not in deltas:
                deltas[old]=changes(cache,old,goal)
            delta=deltas[old]
            units=[c for c in delta if any(content_unit(p) for p in (c["before"],c["after"]))]
            result.update(changed_units=len(units),changed_files=len(delta),files=delta)
            result["status"]="current" if old==goal and not result["issues"] else "review"
            if not args.summary_only:
                if old not in technical:
                    technical[old] = write_technical_files(cache,old,goal,delta,root/"upstream"/old)
                result["technical"] = {"path": f"upstream/{old}/files.json", "sha256": technical[old]}
                paths={**config_row,**data.get("paths",{})}
                terms=[]; indexes={}
                if data:
                    ledger=get("units.jsonl")
                    indexes={v["path"]:v for v in term_records(ledger,"units.jsonl") if v.get("src")=="olp" and v.get("state")!="retired"}
                    result["ledger_sha256"]=sha(ledger)
                    (folder/"olp-edition.toml").write_bytes(contract)
                result["resources"]={}
                for role in ("termbase","orthography","canon_passages","canon_sources"):
                    path=paths.get(role)
                    body=get(path,True) if path else None
                    if body is None:
                        result["issues"].append("locate the edition's "+role)
                        continue
                    name=role+PurePosixPath(path).suffix
                    (folder/name).write_bytes(body)
                    result["resources"][role]={"path":path,"packet_file":name,"sha256":sha(body)}
                    if role=="termbase":
                        terms=term_records(body,path)
                result["units"]=[unit_packet(cache,old,goal,c,paths,get,unit_map,indexes,terms,folder) for c in units]
                if not paths.get("content"):
                    result["issues"].append("locate the current target sources for this edition")
            (folder/"edition.json").write_bytes(encode(result))
        summary={"upstream":UPSTREAM,"upstream_master":current,"target":goal,"editions":reports}
        (root/"summary.json").write_bytes(encode(summary))
        root.rename(destination)
    return summary


HUB_REPOSITORY = "KokunoYumeto/OpenLogic-translations"
WATCH_TITLE = "Open Logic source update"
MARKER = re.compile(r"<!-- openlogic-upstream:([0-9a-f]{40}) -->")


def compare_files(original, replay):
    expected = {f.relative_to(replay) for f in replay.rglob("*") if f.is_file()}
    found = {f.relative_to(original) for f in original.rglob("*") if f.is_file()}
    if expected != found:
        raise ValueError("packet file set differs from source replay")
    for path in sorted(expected):
        if (original/path).read_bytes() != (replay/path).read_bytes():
            raise ValueError("packet bytes differ from source replay: " + path.as_posix())
    return len(expected)


def verify_packet(args):
    original = args.packet.resolve()
    record = json.loads((original/"edition.json").read_bytes())
    identity = safe(record["id"])
    if not FULL_SHA.fullmatch(record.get("edition_commit", "")) or "units" not in record:
        raise ValueError("verification needs a full edition packet")
    with TemporaryDirectory(prefix="olp-replay-") as scratch:
        replay = Path(scratch)/"packets"
        prepare(SimpleNamespace(edition=identity, edition_commit=record["edition_commit"],
                                to=record["to"], cache=args.cache, out=replay, summary_only=False))
        count = compare_files(original, replay/identity)
        technical = Path("upstream")/record["from"]
        count += compare_files(original.parent/technical, replay/technical)
    print(f"{identity}: {count} files identical to a new source and edition replay.")


def hub_api(path, payload=None):
    command=["gh","api","repos/"+HUB_REPOSITORY+"/"+path]
    if payload is not None:
        command.extend(["--method","POST","--input","-"])
    run=subprocess.run(command,input=encode(payload) if payload is not None else None,
                       capture_output=True,timeout=45)
    if run.returncode:
        raise ValueError("GitHub issue request failed in the translations hub")
    return json.loads(run.stdout)


def last_notification(api=hub_api):
    page=1
    while True:
        listing=api("issues?state=all&sort=created&direction=desc&per_page=100&page="+str(page))
        for issue in listing:
            if "pull_request" in issue or not issue["title"].startswith(WATCH_TITLE+" "):
                continue
            marker=MARKER.search(issue.get("body") or "")
            trusted = (issue.get("author_association") in {"OWNER", "MEMBER", "COLLABORATOR"} or
                       issue.get("user", {}).get("login") == "github-actions[bot]")
            if marker and trusted and issue["title"] == WATCH_TITLE+" "+marker[1][:12]:
                return marker[1]
        if len(listing)<100:
            return None
        page+=1


def format_advisory(summary, previous, updates):
    current=summary["target"]
    body=[f"<!-- openlogic-upstream:{current} -->",
          f"[Upstream comparison]({UPSTREAM}/compare/{previous}...{current})", "",
          "Changed upstream files", ""]
    for change in updates[:80]:
        path=change["after"] or change["before"]
        at=current if change["after"] else previous
        body.append(f"- {change['status']} [`{path}`]({UPSTREAM}/blob/{at}/{quote(path)})")
    if len(updates)>80:
        body.append(f"\nThe comparison above includes all {len(updates)} changed files.")
    body.extend(["","Edition coverage","","| Edition | Source comparison | Changed content units |",
                 "| --- | --- | ---: |"])
    for row in summary["editions"]:
        identity=row["id"]
        name=f"[{identity}]({row['repository']})" if row["repository"] else identity
        if "from" not in row:
            body.append(f"| {name} | {row['status']} | — |")
            continue
        link=f"[{row['from'][:8]}…{current[:8]}]({UPSTREAM}/compare/{row['from']}...{current})"
        if row["pin_evidence"]=="shared catalogue freeze only":
            link+=" · shared baseline, edition pin to verify"
        body.append(f"| {name} | {link} | {row['changed_units']} |")
    body.extend(["","[Maintenance guide](https://github.com/"+HUB_REPOSITORY+"/blob/main/MAINTAINING.md)"])
    return "\n".join(body)+"\n"


def watch(args):
    if args.publish and os.environ.get("GITHUB_REPOSITORY",HUB_REPOSITORY).casefold()!=HUB_REPOSITORY.casefold():
        raise ValueError("scheduled notifications belong to the translations hub")
    observed=git("ls-remote","--exit-code",UPSTREAM+".git","refs/heads/master").decode().split()[0]
    previous=last_notification() or json.loads((HUB/"maintenance/editions.json").read_bytes())["monitor_baseline"]
    if observed==previous:
        print("Hub notification already covers upstream master.")
        return
    args.to=observed
    args.edition=None
    args.summary_only=True
    summary=prepare(args)
    updates=changes(args.cache.resolve()/"upstream.git",previous,observed)
    body=format_advisory(summary,previous,updates)
    (args.out/"issue.md").write_text(body,encoding="utf-8",newline="\n")
    if args.publish and last_notification()!=observed:
        issue=hub_api("issues",{"title":WATCH_TITLE+" "+observed[:12],"body":body})
        print(issue["html_url"])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest="command",required=True)
    release=commands.add_parser("release",help="stage a verified textbook or publish it and check the public downloads")
    release.add_argument("--job",required=True,type=Path,help="release metadata and input paths")
    release.add_argument("--out",required=True,type=Path,help="directory for release assets and verified download receipt")
    release.add_argument("--publish",action="store_true")
    plan=commands.add_parser("plan",help="fetch exact sources and prepare one packet per registered edition")
    plan.add_argument("--edition",help="registry ID or locale; omitted selects all")
    plan.add_argument("--edition-commit",help="replay a packet from one immutable edition commit")
    plan.add_argument("--to",help="full upstream commit; defaults to master")
    plan.add_argument("--out",required=True,type=Path)
    plan.add_argument("--cache",type=Path,default=Path(".olp-maintenance/cache"))
    plan.add_argument("--summary-only",action="store_true",help="compute the changes without downloading target units")
    verify=commands.add_parser("verify-packet",help="compare an original packet with a new replay at both pins")
    verify.add_argument("--packet",required=True,type=Path,help="edition directory containing edition.json")
    verify.add_argument("--cache",type=Path,default=Path(".olp-maintenance/cache"))
    check=commands.add_parser("watch",help="prepare one hub advisory for a new upstream master")
    check.add_argument("--out",required=True,type=Path)
    check.add_argument("--cache",type=Path,default=Path(".olp-maintenance/cache"))
    check.add_argument("--publish",action="store_true",help="open the advisory in the translations hub")
    args=parser.parse_args()
    if args.command=="release":
        sys.path.insert(0,str(HUB/"olpkit"))
        from olpkit.syncrelease import publish
        return publish(args.job,args.out,args.publish)
    if args.command=="watch":
        watch(args)
        return 0
    if args.command=="verify-packet":
        verify_packet(args)
        return 0
    result=prepare(args)
    for row in result["editions"]:
        print(row["id"],row["status"],row.get("changed_units","—"),"changed units")
    return 0


if __name__=="__main__":
    try:
        sys.exit(main())
    except (ValueError,OSError,subprocess.TimeoutExpired) as error:
        sys.exit(str(error))
