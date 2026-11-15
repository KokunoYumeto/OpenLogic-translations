"""Regression checks for source packets and closed advisory replay."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import maintain as m


class PacketTest(unittest.TestCase):
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
