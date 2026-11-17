import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from olpkit.assembly import digest
from olpkit.epubcheck import verify_cached_dependencies
from olpkit.hubcheck import GENERATOR, hub_checkout
from olpkit.webprofile import load_profile, projected_style_changes, reviewed_projection_changes


class WebProfileTests(unittest.TestCase):
    def test_source_change_requires_matching_frozen_and_reviewed_bytes_and_canon(self):
        filename = "locale/test/content/soundness.tex"
        assembly = {"locale": "test", "book_directory": "book", "sources": {"olp": {"commit": "current"}}}
        unit = {"path": "content/soundness.tex", "unit": "unit1", "assembled_sha256": "new",
                "hashes": {"target_before": "old"}, "canon": ["passage"]}
        receipt = {"schema": "olpkit.sync-accept.v1", "to": "current", "units": [unit]}
        old = {"inputs": {filename: {"sha256": "old"}}}
        new = {"inputs": {filename: {"sha256": "new"}}}
        self.assertEqual(reviewed_projection_changes(assembly, old, new, receipt, [])[0]["decision"], "unit1")
        unit["canon"] = []
        with self.assertRaisesRegex(ValueError, "sync evidence"):
            reviewed_projection_changes(assembly, old, new, receipt, [])
        unit.update(canon=["passage"], assembled_sha256="other")
        with self.assertRaisesRegex(ValueError, "sync evidence"):
            reviewed_projection_changes(assembly, old, new, receipt, [])

    def test_projected_style_requires_the_upstream_blob_and_localized_bytes_at_both_pins(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            repo = root / "OpenLogic.git"
            repo.mkdir()
            def git(*args):
                return subprocess.check_output(["git", "-C", str(repo), *args]).decode().strip()
            git("init", "-q")
            path = "sty/fixture.sty"
            style = repo / path
            style.parent.mkdir()
            row = {"path": path}
            acceptance = {"technical_changes": [row]}
            projections = []
            editions = []
            for side, field in (("before", "from"), ("after", "to")):
                body = side.encode()
                style.write_bytes(body)
                git("add", path)
                git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", side)
                pin = git("rev-parse", "HEAD")
                row[side] = ["100644", "blob", git("rev-parse", "HEAD:" + path)]
                acceptance[field] = pin
                edition = root / (side + ".toml")
                edition.write_text(f'locale="test"\nengine="test"\nscript="test"\n[pins.olp]\ncommit="{pin}"\n')
                editions.append(edition)
                projections.append({"inputs": {path: {"sha256": digest(body)}}})
            def check():
                return projected_style_changes(root, acceptance, *editions, *projections)
            self.assertEqual(check(), {path: row})
            row["after"][2] = row["before"][2]
            with self.assertRaisesRegex(ValueError, "Localized style"):
                check()
            row["after"][2] = git("rev-parse", "HEAD:" + path)
            projections[0]["inputs"][path]["sha256"] = digest(b"another file")
            with self.assertRaisesRegex(ValueError, "Localized style"):
                check()

    def test_witnesses_are_relative_to_profile_location(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve()
            profile = root / "profile.json"
            profile.write_text(json.dumps({
                "witnesses": {"aux": {"path": "native/book.aux"}},
                "packages": {"pkg.sty": {"path": str(root / "tex/pkg.sty")}},
                "figure_exports": [{"directory": "diagrams"}],
                "epubcheck": {"path": "bin/epubcheck.jar"}
            }), encoding="utf-8")
            data = load_profile(profile)
            self.assertEqual(Path(data["witnesses"]["aux"]["path"]), root / "native/book.aux")
            self.assertEqual(Path(data["packages"]["pkg.sty"]["path"]), root / "tex/pkg.sty")
            self.assertEqual(Path(data["figure_exports"][0]["directory"]), root / "diagrams")
            self.assertEqual(Path(data["epubcheck"]["path"]), root / "bin/epubcheck.jar")

    def test_cached_diagram_must_retain_source_and_vector(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "ASSEMBLY.json").write_text('{"book_directory":"book","locale":"jv"}')
            tex, svg = b"source", b"vector"
            (root / "diagram.tex").write_bytes(tex)
            (root / "diagram.svg").write_bytes(svg)
            figures = {"figures": [{"source_file":"diagram.tex","source_sha256":digest(tex),
                                    "asset":"diagram.svg","svg_sha256":digest(svg)}]}
            manifest = json.dumps(figures).encode()
            (root / "NATIVE_FIGURES.json").write_bytes(manifest)
            profile = {"locale":"jv","figure_exports":[{"directory":str(root),"receipt_sha256":digest(manifest)}]}
            verify_cached_dependencies(root, profile)
            for path, original in [(root/"diagram.tex", tex), (root/"diagram.svg", svg),
                                   (root/"NATIVE_FIGURES.json", manifest)]:
                with self.subTest(file=path.name):
                    path.write_bytes(b"changed")
                    with self.assertRaises(ValueError):
                        verify_cached_dependencies(root, profile)
                    path.write_bytes(original)

    def test_public_hub_layout_and_override(self):
        with tempfile.TemporaryDirectory() as name:
            hub = Path(name).resolve()
            (hub / GENERATOR).parent.mkdir()
            (hub / GENERATOR).touch()
            (hub / "registry.toml").touch()
            with patch.dict("os.environ", {"OLPKIT_HUB": ""}):
                self.assertEqual(hub_checkout(hub/"olpkit"), hub)
            with patch.dict("os.environ", {"OLPKIT_HUB": str(hub/"other")}):
                self.assertEqual(hub_checkout(hub/"olpkit"), hub/"other")
