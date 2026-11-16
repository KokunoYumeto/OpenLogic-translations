"""Publish the verified product to its edition repository and read the files back."""
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen
from zipfile import ZipFile

from .assembly import GitSnapshot, digest, json_bytes
from .build import GATES
from .cache import relative_path
from .schemas import validate_schema
from .status import contract
from .syncaccept import save_acceptance
from .upstreamtags import monthly_tags, tag_for_commit


def verify_web_bundle(archive, native, cold, verification):
    with ZipFile(archive) as package, ZipFile(native) as original:
        manifest = json.loads(package.read("WEB-EDITION.json"))
        product = manifest.get("product", "accessible")
        if product not in ("epub", "accessible") or product != verification.get("web_product", "accessible"):
            raise ValueError("source bundle belongs to a different verified web product")
        members = package.namelist()
        if (set(members) != set(manifest["inputs"]) | {"WEB-EDITION.json"}
                or len({n.casefold() for n in members}) != len(members)):
            raise ValueError("unexpected web source inventory")
        for name, expected in manifest["inputs"].items():
            relative_path(name)
            if digest(package.read(name)) != expected:
                raise ValueError("web source member changed: " + name)
        for name in original.namelist():
            if original.read(name) != package.read("source/" + name):
                raise ValueError("the web source bundle must preserve the complete native source: " + name)
        if set(manifest["outputs"]) != {"reader.html", "reader-html.zip", "reader.epub"}:
            raise ValueError("expected all three web outputs")
        for name, expected in manifest["outputs"].items():
            if digest((cold / name).read_bytes()) != expected:
                raise ValueError("cold web build differs: " + name)
            if name in verification["web_assets"] and verification["web_assets"][name]["sha256"] != expected:
                raise ValueError("cold output differs from the verified reader: " + name)
    return manifest


def stage(job_path, out):
    job_path = Path(job_path).resolve()
    job = json.loads(job_path.read_bytes())
    def path(key):
        return (job_path.parent / job[key]).resolve()
    evidence = json.loads(path("verified").read_bytes())
    build_bytes = path("build").read_bytes()
    build = json.loads(build_bytes)
    if (digest(build_bytes) != evidence["native_build_sha256"] or build["pdf"] != evidence["pdf"]
            or {k: v["status"] for k,v in build["gates"].items()} != evidence["gates"]):
        raise ValueError("product verification differs from the native build")
    snapshot = GitSnapshot(path("repo"), evidence["edition_commit"])
    edition = contract(snapshot)
    if (evidence["status"] != "pass" or evidence["gates"] != dict.fromkeys(GATES, "pass")
            or evidence["pins"] != edition["pins"] or evidence["edition"] != edition["locale"]
            or evidence["product"] not in edition["products"]):
        raise ValueError("release requires a verified edition and all native product gates")
    repo_url = edition["repository"].removesuffix(".git")
    if not re.fullmatch(r"https://github\.com/[\w.-]+/[\w.-]+", repo_url):
        raise ValueError("expected the edition's GitHub repository")
    tag = job["tag"]
    if not re.fullmatch(r"[a-z0-9][a-zA-Z0-9.-]*", tag):
        raise ValueError("invalid release tag")
    native = path("native_archive")
    source = path("source_bundle")
    cold = path("cold_web")
    for file in (native, path("tex")):
        if digest(file.read_bytes()) != evidence["source_assets"][file.name]["sha256"]:
            raise ValueError("editable source differs from its cold-build receipt")
    if digest(path("pdf").read_bytes()) != evidence["pdf"]["sha256"]:
        raise ValueError("release PDF differs from its verified build")
    verify_web_bundle(source, native, cold, evidence)
    payloads = {"pdf": (path("pdf"), "PDF"), "tex": (path("tex"), "TEX"), "source": (source, "ZIP"),
                "html": (cold / "reader-html.zip", "HTML"), "epub": (cold / "reader.epub", "EPUB")}
    names = job["filenames"]
    if set(names) != set(payloads) or len({n.casefold() for n in names.values()}) != len(payloads):
        raise ValueError("release needs distinct names for all five products")
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    release = {"schema_version": 1, "edition": edition["locale"], "product_group": evidence["product"],
               "tag": tag, "commit": snapshot.commit, "pins": edition["pins"],
               "source_units": evidence["source_units"], "reader_units": evidence["reader_units"], "assets": [],
               "gates": [{"id": gate, "status": "pass", "scope": job["gate_scopes"][gate]} for gate in sorted(GATES)],
               "attribution": job["attribution"], "license": job["license"], "engine": edition["engine"],
               "unit_ledger": {"path": "units.jsonl", "sha256": digest(snapshot.read_many(["units.jsonl"])["units.jsonl"])},
               "tool_versions": job["tool_versions"]}
    if "upstream_tag" in edition:
        release["upstream_tag"] = edition["upstream_tag"]
    for key, (file, fmt) in payloads.items():
        name = names[key]
        if relative_path(name).name != name or name == "release.json":
            raise ValueError("release asset needs a plain filename")
        data = file.read_bytes()
        save_acceptance(out / name, data)
        row = {"name": name, "format": fmt, "bytes": len(data), "sha256": digest(data),
               "url": repo_url + "/releases/download/" + tag + "/" + quote(name)}
        if key in ("tex", "source"):
            row["source_for"] = ["PDF"] if key == "tex" else ["PDF", "HTML", "EPUB"]
        release["assets"].append(row)
    validate_schema("release", release)
    save_acceptance(out / "release.json", json_bytes(release))
    return job, snapshot, repo_url, release


def gh(*args):
    return subprocess.check_output(["gh", *args], text=True, encoding="utf-8").strip()


def publish(job_path, out, public=False):
    job, snapshot, url, release = stage(job_path, out)
    notes = (Path(job_path).resolve().parent / job["notes"]).read_text("utf-8-sig")
    return publish_staged(snapshot, url, release, out, job["title"], notes, public)


def publish_staged(snapshot, url, release, out, title, notes, public=False):
    """Publish the exact files a product's verifier staged, preserving existing tags and assets."""
    out = Path(out).resolve()
    validate_schema("release", release)
    edition = contract(snapshot)
    if (url != edition["repository"].removesuffix(".git") or snapshot.commit != release["commit"]
            or release.get("upstream_tag") != edition.get("upstream_tag")
            or release["edition"] != edition["locale"] or release["product_group"] not in edition["products"]
            or any(edition["pins"].get(key) != pin for key, pin in release["pins"].items())):
        raise ValueError("Staged release differs from the edition at its commit")
    repo = url.removeprefix("https://github.com/")
    tag = release["tag"]
    if not re.fullmatch(r"https://github\.com/[\w.-]+/[\w.-]+", url) or not re.fullmatch(r"[a-z0-9][a-zA-Z0-9.-]*", tag):
        raise ValueError("Invalid edition release destination or tag")
    if json.loads((out / "release.json").read_bytes()) != release:
        raise ValueError("Staged release manifest differs from the verified record")
    ledger = release["unit_ledger"]
    ledger_name = relative_path(ledger["path"]).as_posix()
    if digest(snapshot.read_many([ledger_name])[ledger_name]) != ledger["sha256"]:
        raise ValueError("Staged release refers to a different unit ledger")
    if any(gate["status"] == "fail" for gate in release["gates"]):
        raise ValueError("A failed release check must be resolved before publication")
    files = {r["name"]: r["sha256"] for r in release["assets"]}
    if len({name.casefold() for name in files}) != len(release["assets"]) or "release.json" in {name.casefold() for name in files}:
        raise ValueError("Duplicate or reserved release asset name")
    for row in release["assets"]:
        name = row["name"]
        if (relative_path(name).name != name or row["url"] != url + "/releases/download/" + tag + "/" + quote(name)
                or row["bytes"] != (out / name).stat().st_size or row["sha256"] != digest((out / name).read_bytes())):
            raise ValueError("File no longer matches the verified release manifest: " + name)
    files["release.json"] = digest((out / "release.json").read_bytes())
    if not public:
        print(f"Staged {len(files)} files for {repo} at {tag}")
        return 0
    endpoint = "repos/" + repo
    info = json.loads(gh("api", endpoint))
    if info["private"] or info["archived"] or info["html_url"].casefold() != url.casefold():
        raise ValueError("the anonymous release destination must be the active public edition")
    hooks = json.loads(gh("api", "--paginate", "--slurp", endpoint + "/hooks?per_page=100"))
    if any("zenodo" in json.dumps(h).lower() for page in hooks for h in page):
        raise ValueError("a Zenodo webhook is configured on the edition repository")
    def find_release():
        pages = json.loads(gh("api", "--paginate", "--slurp", endpoint + "/releases?per_page=100"))
        return next((r for page in pages for r in page if r["tag_name"] == tag), None)
    state = find_release()
    if state is None:
        recorded = release.get("upstream_tag")
        actual = tag_for_commit(monthly_tags(), edition["pins"]["olp"]["commit"], recorded)
        if recorded != actual:
            raise ValueError(f"New release expects upstream_tag = {actual!r}. Run maintain.py upstream-tag "
                             "on the edition before verifying the release commit.")
    remote_tag = "refs/tags/" + tag
    existing = snapshot.run("ls-remote", url, remote_tag, remote_tag + "^{}").decode().splitlines()
    if existing and existing[-1].split()[0] != snapshot.commit:
        raise ValueError("public release tag points to another commit")
    if not existing:
        snapshot.run("push", url, snapshot.commit + ":" + remote_tag)
    snapshot.run("fetch", "--no-tags", url, remote_tag + ":" + remote_tag)
    if snapshot.run("rev-parse", "--verify", remote_tag + "^{commit}").decode().strip() != snapshot.commit:
        raise ValueError("fetched release tag differs from the verified edition")
    if state is None:
        state = find_release()
    if state is None:
        body = {"tag_name": tag, "target_commitish": snapshot.commit, "name": title,
                "body": notes, "draft": True}
        state = json.loads(subprocess.check_output(
            ["gh", "api", "--method", "POST", endpoint + "/releases", "--input", "-"],
            input=json_bytes(body)))
    if (not state or state["name"] != title
            or (state["body"] or "").replace("\r\n", "\n").strip() != notes.replace("\r\n", "\n").strip()):
        raise ValueError("existing release description differs")
    def asset_map():
        pages = json.loads(gh("api", "--paginate", "--slurp", endpoint + f"/releases/{state['id']}/assets?per_page=100"))
        return {row["name"]: row for page in pages for row in page}
    remote = asset_map()
    if set(remote) - set(files):
        raise ValueError("unexpected existing release assets")
    for name, checksum in files.items():
        if name in remote:
            if remote[name].get("digest") != "sha256:" + checksum:
                raise ValueError("different existing release asset: " + name)
        elif state["draft"]:
            gh("release", "upload", tag, str(out / name), "--repo", repo)
        else:
            raise ValueError("published release is missing an expected file: " + name)
    remote = asset_map()
    if {name: row.get("digest") for name, row in remote.items()} != {k: "sha256:"+v for k,v in files.items()}:
        raise ValueError("GitHub asset digests differ")
    if state["draft"]:
        gh("release", "edit", tag, "--repo", repo, "--draft=false")
    readback = []
    for name, checksum in files.items():
        link = url + "/releases/download/" + tag + "/" + quote(name)
        with urlopen(link, timeout=90) as response:
            payload = response.read()
        if digest(payload) != checksum or len(payload) != (out / name).stat().st_size:
            raise ValueError("anonymous public download differs: " + name)
        readback.append({"name": name, "bytes": len(payload), "sha256": checksum, "url": link})
    save_acceptance(out / "PUBLIC-READBACK.json", json_bytes({"url": url + "/releases/tag/" + tag,
                    "tag": tag, "commit": snapshot.commit, "assets": readback}))
    print(f"Verified {len(files)} anonymous downloads at {url}/releases/tag/{tag}")
    return 0
