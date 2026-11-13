from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from olpkit.assembly import digest, json_bytes
from olpkit.build import compile_book, validate_unstarted_attempt


class ResumeBuildTests(unittest.TestCase):
    def setUp(self):
        self.report={'files':{'a.tex':{'sha256':digest(b'input')}},'book_directory':'book'}
        self.previous={'schema':'olpkit.build.v1','status':'slot_occupied','commands':[],
                       'mutex_acquired':False,'passes':0,'assembly_sha256':digest(json_bytes(self.report)),
                       'source_inputs':self.report['files'],'engine':'pdflatex','source_date_epoch':42,
                       'book_directory':'book','build_tree':'source'}

    def stage(self, root):
        source=root/'source';source.mkdir();(source/'a.tex').write_bytes(b'input')
        receipt=json_bytes(self.previous);(root/'BUILD.json').write_bytes(receipt)
        return source,receipt

    def test_resume_archives_exact_receipt_and_reuses_source_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source,receipt=self.stage(root);before=(source/'a.tex').stat()
            with patch('olpkit.build._compile_book',return_value={'status':'test'}) as run:
                result=compile_book(source,self.report,'pdflatex',42,root,resume=True)
            self.assertEqual(result,{'status':'test'});run.assert_called_once()
            self.assertEqual((root/'attempts'/('BUILD-'+digest(receipt)+'.json')).read_bytes(),receipt)
            self.assertEqual((source/'a.tex').stat().st_mtime_ns,before.st_mtime_ns)
            self.assertEqual((source/'a.tex').stat().st_ino,before.st_ino)
            self.assertFalse((root/'.olpkit-build.lock').exists())

    def test_started_failed_or_differently_bound_attempts_are_never_reused(self):
        for key,value in [('status','failed'),('status','compiled_pending_remaining_gates'),
                          ('commands',[{'tool':'pdflatex'}]),('mutex_acquired',True),('passes',1),
                          ('pdf',{'path':'reader.pdf'}),('assembly_sha256','0'*64),
                          ('engine','xelatex'),('source_date_epoch',43),('source_inputs',{}),
                          ('book_directory','elsewhere'),('build_tree','other')]:
            previous=deepcopy(self.previous);previous[key]=value
            with self.subTest(field=key,value=value),self.assertRaises(ValueError):
                validate_unstarted_attempt(previous,self.report,'pdflatex',42)

    def test_changed_source_preserves_receipt_and_starts_no_engine(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source,receipt=self.stage(root);(source/'a.tex').write_bytes(b'changed')
            with patch('olpkit.build._compile_book') as run,self.assertRaisesRegex(ValueError,'assembled input changed'):
                compile_book(source,self.report,'pdflatex',42,root,resume=True)
            run.assert_not_called();self.assertEqual((root/'BUILD.json').read_bytes(),receipt)
            self.assertFalse((root/'attempts').exists());self.assertFalse((root/'.olpkit-build.lock').exists())

    def test_concurrent_invocation_cannot_replace_live_receipt_or_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source,receipt=self.stage(root);lock=root/'.olpkit-build.lock';lock.write_bytes(b'other-process')
            with patch('olpkit.build._compile_book') as run,self.assertRaisesRegex(ValueError,'another invocation'):
                compile_book(source,self.report,'pdflatex',42,root,resume=True)
            run.assert_not_called();self.assertEqual((root/'BUILD.json').read_bytes(),receipt)
            self.assertEqual(lock.read_bytes(),b'other-process')

    def test_reusing_receipt_requires_explicit_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source,receipt=self.stage(root)
            with patch('olpkit.build._compile_book') as run,self.assertRaisesRegex(ValueError,'receipt already exists'):
                compile_book(source,self.report,'pdflatex',42,root)
            run.assert_not_called();self.assertEqual((root/'BUILD.json').read_bytes(),receipt)


if __name__=='__main__':unittest.main()
