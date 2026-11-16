"""Open Logic's monthly release identifiers, resolved against the maintainer's Git refs."""
import codecs
import os
from pathlib import Path
import re
import stat
import subprocess
from tempfile import NamedTemporaryFile
import tomllib


UPSTREAM = "https://github.com/OpenLogicProject/OpenLogic"
MONTH = re.compile(r"[0-9]{2}\.(?:0[1-9]|1[0-2])")
COMMIT = re.compile(r"[0-9a-f]{40}")


def monthly_tags(repository=UPSTREAM):
    process = subprocess.run(
        ["git", "ls-remote", "--tags", "--", str(repository), "refs/tags/[0-9][0-9].[0-9][0-9]*"],
        capture_output=True, timeout=45, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    if process.returncode:
        raise ValueError("Could not read the upstream monthly tags")
    direct, peeled = {}, {}
    for line in process.stdout.splitlines():
        oid, ref = line.split(b"\t")
        name = ref.removeprefix(b"refs/tags/").decode("ascii", errors="replace")
        tag = name.removesuffix("^{}")
        if MONTH.fullmatch(tag):
            value = oid.decode("ascii")
            group = direct if name == tag else peeled
            if not COMMIT.fullmatch(value) or tag in group:
                raise ValueError("Invalid upstream Git tag advertisement")
            group[tag] = value
    if peeled.keys() - direct.keys():
        raise ValueError("Incomplete annotated upstream tag advertisement")
    return {tag: peeled.get(tag, oid) for tag, oid in direct.items()}


def tag_for_commit(tags, commit, recorded=None):
    if not COMMIT.fullmatch(commit):
        raise ValueError("Expected a full Open Logic source commit")
    matches = sorted(tag for tag, oid in tags.items() if oid == commit)
    if recorded in matches:
        return recorded
    if matches:
        return matches[-1]
    return "untagged" if tags else "none yet"


def record_tag(directory, tags):
    path = Path(directory) / "olp-edition.toml"
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    edition = tomllib.loads(text)
    upstream = edition["pins"]["olp"]
    if upstream["repository"].removesuffix(".git") != UPSTREAM:
        raise ValueError("Edition does not pin the Open Logic Project repository")
    old = edition.get("upstream_tag")
    tag = tag_for_commit(tags, upstream["commit"], old)
    if tag == old:
        return tag
    if old is None:
        newline = "\r\n" if "\r\n" in text else "\n"
        updated = f'upstream_tag = "{tag}"{newline}' + text
    else:
        # Edit just the existing scalar, retaining comments, unrelated tables and line endings.
        pattern = re.compile(r"""(?m)^([ \t]*(?:upstream_tag|"upstream_tag"|'upstream_tag')[ \t]*=[ \t]*)(["'])([^"'\r\n]*)\2(?=[ \t]*(?:#[^\r\n]*)?\r?$)""")
        for match in pattern.finditer(text):
            proposal = text[:match.start(3)] + tag + text[match.end(3):]
            if tomllib.loads(proposal) == {**edition, "upstream_tag": tag}:
                updated = proposal
                break
        else:
            raise ValueError("Could not update the top-level upstream_tag without changing other settings")
    if tomllib.loads(updated) != {**edition, "upstream_tag": tag}:
        raise ValueError("Unexpected change outside the edition's upstream tag")
    replacement = (codecs.BOM_UTF8 if raw.startswith(codecs.BOM_UTF8) else b"") + updated.encode()
    with NamedTemporaryFile(dir=path.parent, prefix=".olp-tag-", delete=False) as stream:
        temporary = Path(stream.name)
    try:
        temporary.write_bytes(replacement)
        temporary.chmod(stat.S_IMODE(path.stat().st_mode))
        if path.read_bytes() != raw:
            raise ValueError("The edition changed during the upstream tag check")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    return tag
