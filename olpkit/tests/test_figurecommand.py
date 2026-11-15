import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from olpkit.nativefigures import figures_command

def sha(data):return hashlib.sha256(data).hexdigest()

class FigureCommandTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.source=self.root/'source';self.source.mkdir()
        assembly=json.dumps({'files':{'book.tex':{'sha256':sha(b'preamble')}}}).encode()
        (self.source/'ASSEMBLY.json').write_bytes(assembly)
        self.context=self.root/'context.tex';self.context.write_bytes(b'\\begin{oltableau}[A[B,close][C]]\\end{oltableau}')
        self.witness=self.root/'source.tex';self.witness.write_bytes(b'canonical witness')
        self.profile=self.root/'profile.json';self.out=self.root/'out'
        self.data={'schema':'olpkit.native-figure-profile.v1','context_sha256':sha(self.context.read_bytes()),
            'assembly_sha256':sha(assembly),'driver':'book.tex','source_date_epoch':123,'engine':'xelatex',
            'environments':['oltableau'],'witnesses':[{'path':str(self.witness),'sha256':sha(self.witness.read_bytes())}],
            'configuration_evidence':{'native_source_checked':True}}
        self.save()
    def save(self):self.profile.write_text(json.dumps(self.data),encoding='utf-8')
    def run_profile(self,**kwargs):return figures_command(self.source,self.context,self.profile,self.out,**kwargs)
    def test_generic_profile_routes_exact_source_and_resume_without_tree_copy(self):
        with patch('olpkit.nativefigures.export_native_figures',return_value={'status':'slot_occupied','tex_runs':0}) as run:
            self.assertEqual(self.run_profile(resume=True),2)
            args,kw=run.call_args
            self.assertEqual(args[2],self.context.read_text());self.assertEqual(kw['environments'],('oltableau',))
            self.assertEqual(kw['engine'],'xelatex');self.assertTrue(kw['resume'])
            self.assertEqual(kw['context_evidence']['profile_sha256'],sha(self.profile.read_bytes()))
            self.assertFalse(self.out.exists())
    def test_changed_source_assembly_and_witness_fail_before_rendering(self):
        for path in [self.context,self.source/'ASSEMBLY.json',self.witness]:
            before=path.read_bytes();path.write_bytes(before+b' changed')
            with patch('olpkit.nativefigures.export_native_figures') as run:
                with self.assertRaisesRegex(ValueError,'changed'):self.run_profile()
                run.assert_not_called()
            path.write_bytes(before)
    def test_unregistered_driver_and_environment_are_rejected(self):
        for key,value,message in [('driver','outside.tex','assembled input'),('environments',['document'],'unsupported native')]:
            before=self.data[key];self.data[key]=value;self.save()
            with self.assertRaisesRegex(ValueError,message):self.run_profile()
            self.assertFalse(self.out.exists());self.data[key]=before;self.save()

if __name__=='__main__':unittest.main()
