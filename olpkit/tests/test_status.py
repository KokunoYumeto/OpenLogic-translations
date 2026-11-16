import contextlib
from io import StringIO
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from olpkit.assembly import GitSnapshot, digest
from olpkit.edition import git_blob
from olpkit.status import book_scope, status_command


class StatusTest(unittest.TestCase):
    def git(self, repo, *args):
        return subprocess.check_output(["git","-C",str(repo),*args],stderr=subprocess.DEVNULL).decode().strip()

    def commit(self, repo):
        self.git(repo,"add","-A")
        self.git(repo,"commit","-qm","fixture")
        return self.git(repo,"rev-parse","HEAD")

    def put(self, repo, path, body):
        target=repo/path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(body)

    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)
        self.english=self.root/"upstream"
        self.target=self.root/"edition"
        for path in (self.english,self.target):
            path.mkdir()
            self.git(path,"init","-q")
            self.git(path,"config","user.name","Fixture")
            self.git(path,"config","user.email","fixture@example.invalid")
            self.git(path,"config","core.autocrlf","false")
        paths=["content/a.tex","content/b.tex"]
        self.rows=[]
        for i,p in enumerate(paths,1):
            en=f"English {i}\n".encode()
            tr=f"Target {i}\n".encode()
            self.put(self.english,p,en)
            self.put(self.target,"mr/"+p,tr)
            self.put(self.target,"upstream/"+p,en)
            self.rows.append({"id":f"OLP-{i:04}","src":"olp","path":p,"src_blob":git_blob(en),
                "src_sha256":digest(en),"tr_sha256":digest(tr),"state":"current",
                "by":{"model":None,"effort":None,"date":None,"method":"inherited","evidence":"history.jsonl"}})
        self.pin=self.commit(self.english)
        self.pins={"olp":{"repository":"https://github.com/OpenLogicProject/OpenLogic","commit":self.pin}}
        spec=f'''schema_version = 1
locale = "mr"
language_tag = "mr-Deva-IN"
script = "Deva"
babel = "marathi"
engine = "xelatex"
engine_reason = "Reproduce the fixture's typography."
repository = "https://github.com/example/mr"
products = ["olp-complete", "slc-screen-pdf"]
[paths]
content = "mr/content"
source_content = "upstream/content"
[pins.olp]
repository = "https://github.com/OpenLogicProject/OpenLogic"
commit = "{self.pin}"
[conversion]
source_manifest = "history.jsonl"
source_manifest_sha256 = "{'0'*64}"
attribution_policy = "preserve-recorded-else-unresolved"
'''
        self.put(self.target,"olp-edition.toml",spec.encode())
        self.ledger()
        prefix="courses/sets-logic-computation/"
        self.put(self.target,prefix+"book.toml",b'imports_lock = "imports.lock"\n')
        self.put(self.target,prefix+"imports.lock",b"OLP-0001\tcontent/a.tex\n")
        self.head=self.commit(self.target)
        self.receipts=[]
        for product, count, path in [("olp-complete",2,"units.jsonl"),("slc-screen-pdf",1,prefix+"imports.lock")]:
            self.git(self.target,"tag",product)
            r={"schema_version":1,"edition":"mr","product_group":product,"tag":product,
                "commit":self.head,"pins":self.pins,"source_units":count,"reader_units":count,
                "assets":[],"gates":[],"attribution":"Fixture","license":"CC0",
                "unit_ledger":{"path":path,"sha256":digest((self.target/path).read_bytes())},
                "engine":"xelatex","tool_versions":{"git":"fixture"}}
            receipt=self.root/(product+".json")
            receipt.write_text(json.dumps(r))
            self.receipts.append(receipt)

    def ledger(self):
        self.put(self.target,"units.jsonl",b"".join((json.dumps(row)+"\n").encode() for row in self.rows))

    def status(self,to=None):
        output=StringIO()
        with contextlib.redirect_stdout(output):
            status_command(self.target,"HEAD",self.english,to,self.receipts,True)
        return json.loads(output.getvalue())

    def test_local_correction_only_dirties_its_users(self):
        self.assertEqual([p["state"] for p in self.status()["products"]],["current","current"])
        self.put(self.target,"mr/content/b.tex",b"corrected")
        self.rows[1]["tr_sha256"]=digest(b"corrected")
        self.ledger()
        self.commit(self.target)
        report=self.status()
        self.assertEqual(report["counts"],{"current":2})
        self.assertEqual([p["state"] for p in report["products"]],["stale","current"])
        self.assertEqual(report["products"][0]["changed_units"],["content/b.tex"])

    def test_new_removed_stale_and_style_change(self):
        (self.english/"content/b.tex").unlink()
        self.put(self.english,"content/c.tex",b"new")
        self.put(self.english,"content/a.tex",b"corrected")
        self.put(self.english,"sty/open-logic.sty",b"new style")
        report=self.status(self.commit(self.english))
        self.assertEqual(report["counts"],{"new":1,"stale":1,"removed":1})
        self.assertEqual(report["products"][1]["changed_units"],["content/a.tex"])
        self.assertEqual(report["products"][1]["changed_upstream_support"],["sty/open-logic.sty"])

    def test_path_only_book_imports_resolve_to_unique_edition_units(self):
        filename = "courses/sets-logic-computation/imports.lock"
        rows = {row["path"]:row for row in self.rows}
        def scope(contents):
            self.put(self.target, filename, contents.encode())
            return book_scope("slc-screen-pdf", GitSnapshot(self.target,self.commit(self.target)), rows)
        self.assertEqual(scope("content/b.tex\ncontent/a.tex\n"), set(rows))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            scope("content/a.tex\ncontent/a.tex\n")
        with self.assertRaisesRegex(ValueError, "unrecognized"):
            scope("content/unknown.tex\n")

    def test_current_label_cannot_hide_changed_target_or_forged_source_digest(self):
        self.rows[1]["src_sha256"]="0"*64
        self.ledger()
        self.put(self.target,"mr/content/a.tex",b"unrecorded correction")
        self.commit(self.target)
        r=self.status()
        self.assertEqual(r["counts"],{"stale":2})
        self.assertIn("source hashes differ at the edition pin",r["unit_changes"]["content/b.tex"]["reasons"])
        self.assertIn("target bytes differ from the ledger",r["unit_changes"]["content/a.tex"]["reasons"])

    def test_different_release_tag_rejected(self):
        p=self.receipts[0];r=json.loads(p.read_bytes());r["commit"]="f"*40;p.write_text(json.dumps(r))
        with self.assertRaisesRegex(ValueError,"release commit differs"):
            self.status()

    def test_unmapped_translation_and_unknown_nonunit_impact(self):
        self.put(self.target,"mr/content/unlisted.tex",b"extra target")
        self.put(self.target,"book-configuration.tex",b"new configuration")
        self.commit(self.target)
        report=self.status()
        self.assertEqual(report["counts"],{"current":2,"unmapped":1})
        self.assertEqual(report["products"][0]["state"],"stale")
        self.assertEqual(report["products"][1]["state"],"unverified")
        self.assertIn("book-configuration.tex",report["products"][1]["unresolved_edition_files"])
