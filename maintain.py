"""Plan Open Logic edition maintenance using only Python 3.11+, Git and the public repositories."""
import argparse
import csv
from functools import partial
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import tomllib
from urllib.error import HTTPError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen


HUB = Path(__file__).resolve().parent
sys.path.insert(0, str(HUB/"olpkit"))
from olpkit.upstreamtags import MONTH, UPSTREAM, monthly_tags, record_tag, tag_for_commit
from olpkit.canonlinks import compare_canon_spans, segment_index
from olpkit.termmatch import GROUPED, matched_labels, prose_for_matching
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


def upstream_content_inventory(cache, commit):
    """Hash the actual Git blobs, without inheriting working-tree line endings."""
    listing = git("ls-tree", "-r", "-z", commit, "--", "content", cwd=cache)
    objects = {}
    for entry in listing.split(b"\0")[:-1]:
        meta, name = entry.split(b"\t", 1)
        path = name.decode("utf-8")
        if content_unit(path):
            mode, kind, oid = meta.decode().split()
            if kind != "blob" or mode not in ("100644", "100755"):
                raise ValueError("expected a regular upstream source file: " + path)
            objects[path] = oid

    # Archive in one operation so a partial Git clone can prefetch its blobs.
    packed = git("-c", "core.autocrlf=false", "archive", "--format=tar", commit, "--", "content", cwd=cache)
    inventory = {}
    with tarfile.open(fileobj=io.BytesIO(packed)) as archive:
        members = {member.name: member for member in archive if member.isfile()}
        for path, oid in objects.items():
            member = members.get(path)
            body = archive.extractfile(member).read() if member else None
            # Git export attributes can omit or transform a blob in the archive.
            if body is None or hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest() != oid:
                body = git("cat-file", "blob", oid, cwd=cache)
            inventory[path] = (len(body), sha(body))
    return inventory


def source_manifest_pin(raw, cache, inventories, unit_map):
    rows = term_records(raw, "manifest.jsonl")
    commits = {row["source_commit"] for row in rows}
    if len(commits) != 1 or not FULL_SHA.fullmatch(next(iter(commits))):
        raise ValueError("edition source manifest must name one upstream commit")
    commit = commits.pop()
    if commit not in inventories:
        inventories[commit] = upstream_content_inventory(cache, commit)
    expected = inventories[commit]
    seen_paths, seen_ids = set(), set()
    for row in rows:
        path, unit = row["source_path"], row["unit_id"]
        if (path in seen_paths or unit in seen_ids or not unit or unit_map.get(path, unit) != unit
                or path not in expected or expected[path] != (row["source_bytes"], row["source_sha256"].lower())):
            raise ValueError("edition source manifest disagrees with upstream text or unit identity: " + path)
        seen_paths.add(path)
        seen_ids.add(unit)
    if seen_paths != expected.keys():
        raise ValueError("edition source manifest omits upstream content")
    return commit, len(rows)


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


def prior_choices_by_unit(rows, segment_field):
    """Index the edition's own segment associations, independently of English word matching."""
    choices = {}
    for number, row in enumerate(rows, start=1):
        segments = row.get(segment_field, [])
        if not isinstance(segments, list):
            continue
        locations = {}
        for segment in segments:
            match = re.match(r"^(OLP-[0-9]+)(?:$|[-.:])", segment) if isinstance(segment, str) else None
            if match:
                locations.setdefault(match[1], []).append(segment)
        for unit, ids in locations.items():
            choices.setdefault(unit, []).append({"termbase_record": number, "segments": ids})
    return choices


def unit_packet(cache, old, new, change, edition, get, unit_map, indexes, term_rows, root, prior_choices=None, canon=None, term_matching=None):
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
    prose = prose_for_matching(changed) if term_matching == GROUPED else None
    matching = []
    grouped_hits = []
    for number, row in enumerate(term_rows, 1):
        hits = matched_labels(row.get("english"), changed, prose)
        if hits:
            matching.append(row)
            if hits != [row["english"].strip()]:
                grouped_hits.append({"termbase_record": number, "matched_english": hits})
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
    if prior_choices is not None:
        record["prior_segment_choices"] = prior_choices.get(key, [])
    if grouped_hits:
        record["grouped_term_hits"] = grouped_hits
    if canon is not None:
        source = (packet/"before.tex").read_bytes() if "before" in files else None
        target = (packet/"current-target.tex").read_bytes() if "current_target" in files else None
        record["prior_canon"] = compare_canon_spans(canon.get(key, []), source, target)
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
    tags = monthly_tags() if args.summary_only or MONTH.fullmatch(goal) else {}
    if MONTH.fullmatch(goal):
        if goal not in tags:
            raise ValueError("No such upstream monthly release: "+goal)
        goal = tags[goal]
    if not FULL_SHA.fullmatch(goal):
        raise ValueError("--to must be a full upstream commit or a published YY.MM tag")
    git("merge-base","--is-ancestor",goal,current,cwd=cache)
    destination=args.out.resolve()
    if destination.exists():
        raise ValueError("use a fresh output directory; existing packets are preserved")
    destination.parent.mkdir(parents=True,exist_ok=True)
    heads={}; deltas={}; reports=[]; technical={}; inventories={}
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
            elif config_row.get("source_manifest") and not getattr(args, "replay_shared_freeze", False):
                path = config_row["source_manifest"]
                manifest = get(path)
                old, count = source_manifest_pin(manifest, cache, inventories, unit_map)
                result["pin_evidence"] = "edition source manifest checked against upstream Git blobs"
                result["source_manifest"] = {"path": path, "sha256": sha(manifest), "units": count}
                if not args.summary_only:
                    (folder/"source-manifest.jsonl").write_bytes(manifest)
            else:
                old=baseline
                result["pin_evidence"]="shared catalogue freeze only"
                result["issues"].append("verify edition-specific source pin before applying changes")
            result["from"]=old; result["to"]=goal
            if args.summary_only:
                result["from_upstream_tag"] = tag_for_commit(tags, old, data.get("upstream_tag"))
                result["to_upstream_tag"] = tag_for_commit(tags, goal, args.to)
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
                roles = ["termbase", "orthography", "canon_passages", "canon_sources"]
                if paths.get("segment_canon"):
                    roles.append("segment_canon")
                for role in roles:
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
                segment_field = paths.get("termbase_segments")
                prior_choices = None
                if segment_field and not getattr(args, "replay_shared_freeze", False):
                    prior_choices = prior_choices_by_unit(terms, segment_field)
                canon = None
                if all(key in result["resources"] for key in ("segment_canon", "canon_passages", "canon_sources")):
                    canon = segment_index(*((folder/result["resources"][key]["packet_file"]).read_bytes()
                                            for key in ("segment_canon", "canon_passages", "canon_sources")))
                term_matching = getattr(args, "term_matching", GROUPED) if terms else None
                if term_matching is not None:
                    if term_matching != GROUPED:
                        raise ValueError("Unknown term matching rule")
                    result["term_matching"] = term_matching
                result["units"]=[unit_packet(cache,old,goal,c,paths,get,unit_map,indexes,terms,folder,prior_choices,canon,term_matching) for c in units]
                if not paths.get("content"):
                    result["issues"].append("locate the current target sources for this edition")
            (folder/"edition.json").write_bytes(encode(result))
        summary={"upstream":UPSTREAM,"upstream_master":current,"target":goal,"editions":reports}
        (root/"summary.json").write_bytes(encode(summary))
        root.rename(destination)
    return summary


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
                                to=record["to"], cache=args.cache, out=replay, summary_only=False,
                                term_matching=record.get("term_matching"),
                                replay_shared_freeze=record.get("pin_evidence") == "shared catalogue freeze only"))
        count = compare_files(original, replay/identity)
        technical = Path("upstream")/record["from"]
        count += compare_files(original.parent/technical, replay/technical)
    print(f"{identity}: {count} files identical to a new source and edition replay.")


def verify_review(review_path, packet_dir):
    """Bind editorial findings to the source and translated passages they describe."""
    review = json.loads(review_path.read_bytes())
    packet = json.loads((packet_dir / "edition.json").read_bytes())
    for key in ("id", "from", "to", "edition_commit"):
        if review[key] != packet[key]:
            raise ValueError("review and edition packet differ at " + key)
    units = {row["unit"] for row in packet["units"]}
    repository, _, prefix = edition_location(packet["repository"])
    if not review["passages"]:
        raise ValueError("the review contains no passages")
    for passage in review["passages"]:
        unit = passage["unit"]
        if unit not in units or not re.fullmatch(r"(?:OLP-[0-9]+|new-[a-f0-9]{12})", unit):
            raise ValueError("review unit is absent from the packet")
        folder = packet_dir / "units" / unit
        files = json.loads((folder / "unit.json").read_bytes())["files"]
        for filename, hash_field in (("before.tex", "before_sha256"), ("after.tex", "after_sha256"),
                                     ("current-target.tex", "target_sha256")):
            if sha((folder / filename).read_bytes()) != passage[hash_field]:
                raise ValueError(f"{unit}: {filename} differs from the reviewed file")
        lines = (folder / "current-target.tex").read_text(encoding="utf-8").splitlines()
        start, end = passage["target_lines"]
        if not 1 <= start <= end <= len(lines):
            raise ValueError(f"{unit}: invalid target line range")
        excerpt = "\n".join(lines[start - 1:end]).encode("utf-8")
        if sha(excerpt) != passage["excerpt_sha256"]:
            raise ValueError(f"{unit}: target lines differ from the reviewed excerpt")
        for side, pin in (("before", "from"), ("after", "to")):
            url = f"{UPSTREAM}/blob/{packet[pin]}/" + quote(files[side]["path"])
            if passage["source_" + side] != url:
                raise ValueError(f"{unit}: unexpected English {side} link")
        target = (PurePosixPath(prefix) / files["current_target"]["path"]).as_posix()
        url = f"https://github.com/{repository}/blob/{packet['edition_commit']}/{quote(target)}#L{start}-L{end}"
        if passage["target"] != url:
            raise ValueError(f"{unit}: unexpected target link")
    return len(review["passages"])


def notification_repository():
    """Notify the hub in this checkout, including when it is a fork."""
    origin = git("remote", "get-url", "origin", cwd=HUB).decode().strip().rstrip("/")
    for prefix in ("git@github.com:", "ssh://git@github.com/"):
        if origin.startswith(prefix):
            origin = "https://github.com/" + origin.removeprefix(prefix)
            break
    repository, _, _ = edition_location(origin.removesuffix(".git"))
    if origin.removesuffix(".git") != "https://github.com/" + repository:
        raise ValueError("the hub origin must be a GitHub repository URL")
    if repository.casefold() == UPSTREAM.removeprefix("https://github.com/").casefold():
        raise ValueError("set the hub origin to the edition hub; upstream supplies the source")
    if os.environ.get("GITHUB_ACTIONS") == "true":
        if repository.casefold() != os.environ.get("GITHUB_REPOSITORY", "").casefold():
            raise ValueError("the checked-out hub and the workflow repository differ")
    return repository


def hub_api(repository, path, payload=None):
    command=["gh","api","--hostname","github.com","repos/"+repository+"/"+path]
    if payload is not None:
        command.extend(["--method","POST","--input","-"])
    run=subprocess.run(command,input=encode(payload) if payload is not None else None,
                       capture_output=True,timeout=45)
    if run.returncode:
        raise ValueError("GitHub issue request failed in the translations hub")
    return json.loads(run.stdout)


def last_notification(api):
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


def format_advisory(summary, previous, updates, repository):
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
    body.extend(["","Edition coverage","","| Edition | Source comparison | Changed files | Changed content units |",
                 "| --- | --- | ---: | ---: |"])
    for row in summary["editions"]:
        identity=row["id"]
        name=f"[{identity}]({row['repository']})" if row["repository"] else identity
        if "from" not in row:
            body.append(f"| {name} | {row['status']} | — | — |")
            continue
        link=f"[{row['from'][:8]}…{current[:8]}]({UPSTREAM}/compare/{row['from']}...{current})"
        if row["pin_evidence"]=="shared catalogue freeze only":
            link+=" · shared baseline, edition pin to verify"
        body.append(f"| {name} | {link} | {row['changed_files']} | {row['changed_units']} |")
    body.extend(["","[Maintenance guide](https://github.com/"+repository+"/blob/HEAD/MAINTAINING.md)"])
    return "\n".join(body)+"\n"


def watch(args):
    repository = notification_repository()
    api = partial(hub_api, repository)
    observed=git("ls-remote","--exit-code",UPSTREAM+".git","refs/heads/master").decode().split()[0]
    previous=last_notification(api) or json.loads((HUB/"maintenance/editions.json").read_bytes())["monitor_baseline"]
    if observed==previous:
        print("Hub notification already covers upstream master.")
        return
    args.to=observed
    args.edition=None
    args.summary_only=True
    summary=prepare(args)
    updates=changes(args.cache.resolve()/"upstream.git",previous,observed)
    body=format_advisory(summary,previous,updates,repository)
    (args.out/"issue.md").write_text(body,encoding="utf-8",newline="\n")
    if args.publish and last_notification(api)!=observed:
        issue=api("issues",{"title":WATCH_TITLE+" "+observed[:12],"body":body})
        print(issue["html_url"])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest="command",required=True)
    tag=commands.add_parser("upstream-tag",help="record the upstream monthly tag for an edition's pinned commit")
    tag.add_argument("--edition-dir",type=Path,required=True,help="checkout containing olp-edition.toml")
    release=commands.add_parser("release",help="stage a verified textbook or publish it and check the public downloads")
    release.add_argument("--job",required=True,type=Path,help="release metadata and input paths")
    release.add_argument("--out",required=True,type=Path,help="directory for release assets and verified download receipt")
    release.add_argument("--publish",action="store_true")
    plan=commands.add_parser("plan",help="fetch exact sources and prepare one packet per registered edition")
    plan.add_argument("--edition",help="registry ID or locale; omitted selects all")
    plan.add_argument("--edition-commit",help="replay a packet from one immutable edition commit")
    plan.add_argument("--to",help="full upstream commit or published YY.MM tag; defaults to master")
    plan.add_argument("--out",required=True,type=Path)
    plan.add_argument("--cache",type=Path,default=Path(".olp-maintenance/cache"))
    plan.add_argument("--summary-only",action="store_true",help="compute the changes without downloading target units")
    verify=commands.add_parser("verify-packet",help="compare an original packet with a new replay at both pins")
    verify.add_argument("--packet",required=True,type=Path,help="edition directory containing edition.json")
    verify.add_argument("--cache",type=Path,default=Path(".olp-maintenance/cache"))
    review=commands.add_parser("verify-review",help="check the source and target witnesses of a maintenance review")
    review.add_argument("--record",required=True,type=Path)
    review.add_argument("--packet",required=True,type=Path,help="edition directory containing edition.json")
    check=commands.add_parser("watch",help="prepare one hub advisory for a new upstream master")
    check.add_argument("--out",required=True,type=Path)
    check.add_argument("--cache",type=Path,default=Path(".olp-maintenance/cache"))
    check.add_argument("--publish",action="store_true",help="open the advisory in the translations hub")
    args=parser.parse_args()
    if args.command=="upstream-tag":
        print("upstream tag:",record_tag(args.edition_dir, monthly_tags()))
        return 0
    if args.command=="release":
        from olpkit.syncrelease import publish
        return publish(args.job,args.out,args.publish)
    if args.command=="watch":
        watch(args)
        return 0
    if args.command=="verify-packet":
        verify_packet(args)
        return 0
    if args.command=="verify-review":
        count = verify_review(args.record, args.packet)
        print(f"{count} reviewed passages match the pinned source and target files.")
        return 0
    result=prepare(args)
    for row in result["editions"]:
        message = f"{row['id']} {row['status']}"
        if 'changed_files' in row:
            message += f": {row['changed_files']} changed files, {row['changed_units']} changed content units"
        print(message)
    return 0


if __name__=="__main__":
    try:
        sys.exit(main())
    except (ValueError,OSError,subprocess.TimeoutExpired) as error:
        sys.exit(str(error))
