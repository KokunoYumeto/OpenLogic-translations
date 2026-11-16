import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from olpkit.build import copy_build_input


class ReplayFontInputs(unittest.TestCase):
    def test_font_bytes_and_time_survive_replay(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            for extension in (".otf",".TTF"):
                source=root/("source"+extension)
                target=root/("copy"+extension)
                source.write_bytes(b"test font bytes")
                os.utime(source, ns=(946684800000000000,946684800000000000))
                copy_build_input(source,target)
                self.assertEqual(target.read_bytes(),source.read_bytes())
                self.assertEqual(target.stat().st_mtime_ns,source.stat().st_mtime_ns)
