import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
import uuid

from olpkit.process import TeXSlot,run_job,MEMORY_LIMIT
from olpkit.schemas import ROOT


@unittest.skipUnless(os.name=='nt','Windows process containment')
class GuardedProcessTests(unittest.TestCase):
    def setUp(self):
        boundary=ROOT.parent/'out/tests';boundary.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(prefix='process-',dir=boundary)
        self.root=Path(self.tmp.name);self.addCleanup(self.cleanup)

    def cleanup(self):
        if self.root.resolve().parent!=(ROOT.parent/'out/tests').resolve():raise ValueError('unsafe test cleanup')
        self.tmp.cleanup()

    def run_python(self,code,**kwargs):
        return run_job([sys.executable,'-c',code],self.root,self.root/'output.txt',**kwargs)

    def test_hidden_job_has_actual_tree_limit_and_exact_argument_quoting(self):
        value='a path with spaces and "quotes"'
        result=run_job([sys.executable,'-c','import sys;print(sys.argv[1])',value],self.root,self.root/'output.txt')
        self.assertEqual(result['exit_code'],0)
        self.assertEqual(result['memory_limit_bytes'],5_000_000_000)
        self.assertLessEqual(result['enforced_job_memory_bytes'],5_000_000_000)
        self.assertTrue(result['captured_before_resume'])
        self.assertEqual((self.root/'output.txt').read_text().strip(),value)

    def test_memory_cap_prevents_large_allocation(self):
        code='a=bytearray(16*1024*1024)\ntry:\n b=bytearray(128*1024*1024)\n print("UNEXPECTED")\nexcept MemoryError:\n print("CAPPED")'
        result=self.run_python(code,memory_limit=64*1024*1024)
        self.assertEqual(result['exit_code'],0)
        self.assertIn('CAPPED',(self.root/'output.txt').read_text())
        self.assertEqual(result['enforced_job_memory_bytes'],64*1024*1024)

    def test_long_working_directory_keeps_the_correct_build_inputs(self):
        directory = self.root
        while len(str(directory)) < 265:
            directory /= "nested-build-inputs"
        directory.mkdir(parents=True)
        (directory / "witness.txt").write_bytes(b"expected build source")
        try:
            result = run_job([sys.executable, "-c",
                              "from pathlib import Path; print(Path('witness.txt').read_text())"],
                             directory, self.root / "output.txt")
        except ValueError as error:
            # Short-name creation is optional on Windows filesystems.
            self.assertIn("shorter checkout path", str(error))
        else:
            self.assertEqual(result["exit_code"], 0)
            self.assertTrue(result["captured_before_resume"])
            self.assertTrue(result["all_descendants_exited"])
            self.assertEqual((self.root / "output.txt").read_text().strip(), "expected build source")

    def test_job_waits_for_descendant_after_leader_exits(self):
        code='import subprocess,sys;subprocess.Popen([sys.executable,"-c","import time;time.sleep(0.7)"])'
        result=self.run_python(code)
        self.assertEqual(result['exit_code'],0)
        self.assertGreater(result['seconds'],0.6)
        self.assertTrue(result['all_descendants_exited'])

    def test_timeout_kills_descendants_and_returns_bounded_result(self):
        code='import subprocess,sys,time;subprocess.Popen([sys.executable,"-c","import time;time.sleep(10)"]);time.sleep(10)'
        result=self.run_python(code,timeout=0.5)
        self.assertTrue(result['timed_out']);self.assertTrue(result['all_descendants_exited'])
        self.assertLess(result['seconds'],3)

    def test_second_process_cannot_take_held_slot_and_can_after_release(self):
        name='Local\\OLPKit-Test-'+uuid.uuid4().hex
        code='import sys;from olpkit.process import TeXSlot\nwith TeXSlot(sys.argv[1]) as s: print(int(s.acquired))'
        with TeXSlot(name) as first:
            self.assertTrue(first.acquired)
            p=subprocess.run([sys.executable,'-c',code,name],capture_output=True,text=True,timeout=10)
            self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(p.stdout.strip(),'0')
        with TeXSlot(name) as next_slot:self.assertTrue(next_slot.acquired)


if __name__=='__main__':unittest.main()
