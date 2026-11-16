"""Regression checks for source packets and closed advisory replay."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import maintain as m


class PacketTest(unittest.TestCase):
    def test_prior_choice_keeps_exact_segment_and_record_locations(self):
        rows = [{}, {"segments": ["OLP-0001-B04", "OLP-0010-B07", "unassigned"]},
                {"segments": ["OLP-0001-B08"]}]
        links = m.prior_choices_by_unit(rows, "segments")
        self.assertEqual(links["OLP-0001"], [{"termbase_record": 2, "segments": ["OLP-0001-B04"]},
                                             {"termbase_record": 3, "segments": ["OLP-0001-B08"]}])
        self.assertEqual(links["OLP-0010"], [{"termbase_record": 2, "segments": ["OLP-0010-B07"]}])

    def test_source_manifest_checks_original_git_bytes_and_unit_coverage(self):
        with TemporaryDirectory() as scratch:
            tree = Path(scratch)
            m.git("init", "-q", cwd=tree)
            m.git("config", "core.autocrlf", "false", cwd=tree)
            (tree/"content").mkdir()
            # The archive omits one file even though Git tracks its original bytes.
            (tree/".gitattributes").write_bytes(b"content/b.tex export-ignore\n")
            texts = {"content/a.tex": b"first\n", "content/b.tex": b"second\r\n"}
            for path, body in texts.items():
                (tree/path).write_bytes(body)
            m.git("add", ".", cwd=tree)
            m.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                  "commit", "-qm", "source", cwd=tree)
            commit = m.git("rev-parse", "HEAD", cwd=tree).decode().strip()
            rows = [dict(source_path=path, unit_id=f"OLP-{i:04}", source_commit=commit,
                         source_bytes=len(body), source_sha256=m.sha(body))
                    for i, (path, body) in enumerate(texts.items(), start=1)]
            ids = {r["source_path"]: r["unit_id"] for r in rows}
            inventory = {}
            def check(items):
                manifest = "\n".join(json.dumps(row) for row in items).encode()
                return m.source_manifest_pin(manifest, tree, inventory, ids)
            self.assertEqual(check(rows), (commit, 2))
            for invalid in (rows[:1], [*rows, rows[0]], [rows[0], {**rows[1], "source_sha256": "0"*64}],
                            [rows[0], {**rows[1], "source_commit": "0"*40}],
                            [rows[0], {**rows[1], "unit_id": rows[0]["unit_id"]}]):
                with self.assertRaises(ValueError):
                    check(invalid)

    def test_added_removed_renamed_and_technical_inputs(self):
        with TemporaryDirectory() as scratch:
            root = Path(scratch)
            tree = root / "source"
            tree.mkdir()
            def git(*args):
                return m.git(*args, cwd=tree)
            git("init", "-q")
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.invalid")
            git("config", "core.autocrlf", "false")
            (tree/"content").mkdir()
            (tree/"content/old.tex").write_bytes(b"source before\n")
            (tree/"content/retired.tex").write_bytes(b"retired\n")
            (tree/"style.sty").write_bytes(b"old\r\n")
            git("add", ".")
            git("commit", "-qm", "base")
            old = git("rev-parse", "HEAD").decode().strip()
            (tree/"content/old.tex").rename(tree/"content/moved.tex")
            (tree/"content/retired.tex").unlink()
            (tree/"content/new.tex").write_bytes(b"new\n")
            (tree/"style.sty").write_bytes(b"new\r\n")
            git("add", "-A")
            git("commit", "-qm", "changes")
            new = git("rev-parse", "HEAD").decode().strip()
            changes = m.changes(tree, old, new)
            self.assertEqual({row["status"] for row in changes}, {"R100","A","D","M"})
            out = root/"packet"
            out.mkdir()
            move = next(c for c in changes if c["status"]=="R100")
            assets = {"translated/old.tex": b"target\r\n"}
            unit = m.unit_packet(tree, old, new, move, {"content":"translated"},
                                 lambda name,optional:assets[name], {"content/old.tex":"OLP-0001"},
                                 {}, [], out)
            self.assertEqual(unit["unit"], "OLP-0001")
            self.assertEqual((out/"units/OLP-0001/current-target.tex").read_bytes(), b"target\r\n")
            technical = root/"technical"
            m.write_technical_files(tree, old, new, changes, technical)
            row, = json.loads((technical/"files.json").read_bytes())
            self.assertEqual(row["change"]["after"], "style.sty")
            self.assertEqual((technical/row["files"]["after"]["oid"]).read_bytes(), b"new\r\n")

    def test_replay_detects_missing_extra_and_altered_bytes(self):
        with TemporaryDirectory() as scratch:
            left, right = (Path(scratch)/s for s in ("left","right"))
            left.mkdir()
            right.mkdir()
            (right/"a").write_bytes(b"a")
            with self.assertRaises(ValueError):
                m.compare_files(left,right)
            (left/"a").write_bytes(b"b")
            with self.assertRaises(ValueError):
                m.compare_files(left,right)
            (left/"a").write_bytes(b"a")
            self.assertEqual(m.compare_files(left,right),1)
            (left/"extra").touch()
            with self.assertRaises(ValueError):
                m.compare_files(left,right)


class WatchTest(unittest.TestCase):
    def test_closed_verified_marker_only(self):
        commit = "a"*40
        valid = {"title": m.WATCH_TITLE+" "+commit[:12], "state":"closed",
                 "user":{"login":"github-actions[bot]"}, "body": f"<!-- openlogic-upstream:{commit} -->"}
        for issue in ({**valid,"user":{"login":"other"}}, {**valid,"title":m.WATCH_TITLE+" other"},
                      {**valid,"pull_request":{}}):
            self.assertIsNone(m.last_notification(lambda path:[issue]))
        self.assertEqual(m.last_notification(lambda path:[valid]),commit)

    def test_long_delta_links_the_complete_comparison(self):
        rows = [{"before":None,"after":f"content/{i}.tex","status":"A"} for i in range(120)]
        result = m.format_advisory({"target":"a"*40,"editions":[]}, "b"*40, rows)
        self.assertIn("all 120 changed files",result)
        self.assertIn("79.tex",result)
        self.assertNotIn("80.tex",result)


if __name__ == "__main__":
    unittest.main()
