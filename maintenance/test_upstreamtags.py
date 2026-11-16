import codecs
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import maintain
from olpkit.upstreamtags import UPSTREAM, monthly_tags, record_tag, tag_for_commit


class UpstreamTagTests(unittest.TestCase):
    def test_real_annotated_and_lightweight_refs_resolve_to_the_source_commit(self):
        with TemporaryDirectory() as directory:
            tree = Path(directory)
            def git(*args):
                return maintain.git(*args, cwd=tree)
            git("init", "-q")
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.invalid")
            git("commit", "--allow-empty", "-qm", "one")
            first = git("rev-parse", "HEAD").decode().strip()
            git("tag", "v1.0-a")
            git("tag", "26.13")
            self.assertEqual(tag_for_commit(monthly_tags(tree), first), "none yet")
            git("tag", "-a", "26.10", "-m", "monthly")
            git("commit", "--allow-empty", "-qm", "two")
            second = git("rev-parse", "HEAD").decode().strip()
            git("tag", "26.11")
            self.assertEqual(monthly_tags(tree), {"26.10": first, "26.11": second})
            git("tag", "26.12")
            tags = monthly_tags(tree)
            self.assertEqual(tag_for_commit(tags, second), "26.12")
            self.assertEqual(tag_for_commit(tags, second, "26.11"), "26.11")
            self.assertEqual(tag_for_commit(tags, "f"*40), "untagged")
            with self.assertRaisesRegex(ValueError, "Could not read"):
                monthly_tags(tree/"absent")

    def test_planner_resolves_named_release_and_keeps_a_replayable_commit(self):
        with TemporaryDirectory() as directory:
            hub = Path(directory)
            (hub/"registry.toml").write_text('[[editions]]\nid="fixture"\nlocale="xx"\nrepository="https://github.com/example/book"\n')
            (hub/"maintenance").mkdir()
            (hub/"maintenance/editions.json").write_text('{"editions":{}}')
            (hub/"catalogue").mkdir()
            ids = hub/"olpkit/data/units"
            ids.mkdir(parents=True)
            (ids/"olp-units.tsv").write_text("id\tpath\n")
            maintain.git("init", "-q", hub/"english")
            def commit():
                maintain.git("-c","user.name=Fixture","-c","user.email=test@example.invalid",
                             "commit","--allow-empty","-qm","fixture",cwd=hub/"english")
                return maintain.git("rev-parse","HEAD",cwd=hub/"english").decode().strip()
            base = commit()
            maintain.git("branch","-M","master",cwd=hub/"english")
            target = commit()
            (hub/"catalogue/editions.json").write_text(json.dumps({
                "source_authority":{"commit":base}, "editions":[{"id":"fixture","source_revision":base}]}))
            args = SimpleNamespace(edition="xx", edition_commit="a"*40, cache=hub/"cache",
                                   to="26.11", out=hub/"packets", summary_only=True)
            with (patch.object(maintain, "HUB", hub),
                  patch.object(maintain, "upstream_cache", return_value=hub/"english"),
                  patch.object(maintain, "monthly_tags", return_value={"26.11":target}),
                  patch.object(maintain, "remote_file", return_value=None)):
                packet, = maintain.prepare(args)["editions"]
                self.assertEqual((packet["from"], packet["from_upstream_tag"]), (base, "untagged"))
                self.assertEqual((packet["to"], packet["to_upstream_tag"]), (target, "26.11"))
                args.to = "26.12"
                with self.assertRaisesRegex(ValueError, "No such upstream monthly release"):
                    maintain.prepare(args)

    def test_record_keeps_owner_formatting_and_preserves_bytes_on_retry(self):
        with TemporaryDirectory() as directory:
            tree = Path(directory)
            path = tree/"olp-edition.toml"
            commit = "d"*40
            content = (f"# edition\r\n[pins.olp]\r\nrepository = '{UPSTREAM}'\r\n"
                       f"commit = '{commit}' # immutable\r\n").encode()
            path.write_bytes(codecs.BOM_UTF8 + content)
            self.assertEqual(record_tag(tree, {}), "none yet")
            expected = codecs.BOM_UTF8 + b'upstream_tag = "none yet"\r\n' + content
            self.assertEqual(path.read_bytes(), expected)
            timestamp = path.stat().st_mtime_ns
            record_tag(tree, {})
            self.assertEqual(path.stat().st_mtime_ns, timestamp)
            expected = expected.replace(b'"none yet"', b"'none yet' # monthly source")
            path.write_bytes(expected)
            self.assertEqual(record_tag(tree, {"26.10": commit}), "26.10")
            self.assertEqual(path.read_bytes(), expected.replace(b"none yet", b"26.10"))
            self.assertEqual(record_tag(tree, {"26.10": "b"*40}), "untagged")
            bad = path.read_bytes().replace(UPSTREAM.encode(), b"https://example.invalid/foreign")
            path.write_bytes(bad)
            with self.assertRaisesRegex(ValueError, "does not pin"):
                record_tag(tree, {})
            self.assertEqual(path.read_bytes(), bad)
