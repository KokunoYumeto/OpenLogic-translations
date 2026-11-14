import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, writeFile, rm, unlink } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve, dirname, basename } from 'node:path';
import { parseToml, validateRegistry, assembleLegacyCatalogue, loadCatalogueSources } from './catalogue-sources.mjs';
import { editionTable, fillTemplate, editionRouting } from './catalogue-render.mjs';
import { output } from './generate-catalogue.mjs';

function fixture() {
  const registry={schema_version:1,editions:[{id:'openlogic-a',repository:'https://github.com/example/a',locale:'aa'}]};
  const edition={id:'openlogic-a',repository:registry.editions[0].repository,language_tag:'aa-Latn',name:'A',version_doi:'10.1234/preserved',source_units_translated:26,standalone_reader_units:7,limitations:['Canon review remains open'],evidence:{source:'original'}};
  return {registry,edition,metadata:{schema:'test',editions:[],infrastructure:[{id:'keep-me'}]},inputs:new Map([['openlogic-a',{schema:'openlogic.legacy-edition-input.v1',edition,release_discovery:'accepted-only',release_selection:null,textbook:null}]])};
}
test('TOML parser accepts UTF-8 and rejects malformed source instead of partial parsing',async()=>{
  assert.deepEqual(await parseToml('\uFEFFtitle = "मराठी"\n'),{title:'मराठी'});
  await assert.rejects(parseToml('[[editions]\n'),/Invalid registry TOML/);
});
test('registry rejects duplicate identities, path escapes and unknown authoring fields',()=>{
  const {registry}=fixture();assert.equal(validateRegistry(registry),registry);
  assert.throws(()=>validateRegistry({...registry,editions:[...registry.editions,...registry.editions]}),/duplicate/);
  for(const patch of [{id:'../bad'},{repository:'https://example.invalid/repo'},{locale:'../aa'},{title:'not a registry fact'}])
    assert.throws(()=>validateRegistry({...registry,editions:[{...registry.editions[0],...patch}]}));
});
test('source assembly preserves exact evidence, DOI, unknown coverage and input immutability',()=>{
  const f=fixture();const result=assembleLegacyCatalogue(f.registry,f.metadata,f.inputs);
  assert.deepEqual(result.catalogue.editions,[f.edition]);
  assert.equal(result.catalogue.editions[0].epub_reader_units,undefined);
  assert.deepEqual(result.catalogue.infrastructure,f.metadata.infrastructure);
  result.catalogue.editions[0].limitations.push('changed downstream');
  assert.deepEqual(f.edition.limitations,['Canon review remains open']);
});
test('missing, extra or mismatched sources and implicit release discovery fail closed',()=>{
  for(const edit of [f=>f.inputs.clear(),f=>f.inputs.set('openlogic-extra',{}),f=>{f.edition.repository='https://github.com/example/wrong';},f=>{delete f.inputs.get('openlogic-a').release_discovery;}]) {
    const f=fixture();edit(f);assert.throws(()=>assembleLegacyCatalogue(f.registry,f.metadata,f.inputs));
  }
});
test('legacy input privacy is enforced and public routing retains exact coverage and lineage',()=>{
  const f=fixture();
  const result=assembleLegacyCatalogue(f.registry,f.metadata,f.inputs);
  const route=editionRouting(result.catalogue).editions[0];
  assert.equal(route.repository,f.edition.repository);assert.equal(route.version_doi,f.edition.version_doi);
  assert.equal(route.source_units_translated,26);assert.equal(route.standalone_reader_units,7);
  assert.deepEqual(route.limitations,['Canon review remains open']);
  f.edition.owner_task_id='private';assert.throws(()=>assembleLegacyCatalogue(f.registry,f.metadata,f.inputs),/Private administrative/);
  delete f.edition.owner_task_id;f.metadata.infrastructure[0].local_path='private';
  assert.throws(()=>assembleLegacyCatalogue(f.registry,f.metadata,f.inputs),/Private administrative/);
});
test('textbook identity comes from registry and must not inherit another language',()=>{
  const f=fixture();const input=f.inputs.get('openlogic-a');
  input.textbook={id:'aa',name:'A',language_tag:'aa-Latn',order:0,selection:{release_tag:'slc-test'}};
  const r=assembleLegacyCatalogue(f.registry,f.metadata,f.inputs);
  assert.equal(r.textbooks[0].repository,f.edition.repository);
  assert.equal(r.textbookSelection.aa.release_tag,'slc-test');
  input.textbook.language_tag='bb';assert.throws(()=>assembleLegacyCatalogue(f.registry,f.metadata,f.inputs),/identity/);
});
test('README separates source, reader and EPUB scope and preserves native labels and DOI',()=>{
  const {edition}=fixture();edition.ordered_downloads=[{url:'https://example.invalid/a.pdf',download_label:'मराठी PDF'},{url:'https://example.invalid/sample.epub',scope_kind:'sample',download_label:'sample'}];
  const rendered=editionTable({editions:[edition]});
  assert.match(rendered,/\| A \| 26 \| 7 \| — \|/);
  assert.ok(rendered.includes('[मराठी PDF](https://example.invalid/a.pdf)'));
  assert.ok(rendered.includes('https://doi.org/10.1234/preserved'));
  assert.ok(!rendered.includes('sample.epub'));
  edition.source_units_translated=0;assert.match(editionTable({editions:[edition]}),/\| A \| 0 \| 7 \| — \|/);
});
test('generated labels cannot insert HTML or extra Markdown table cells',()=>{
  const {edition}=fixture();edition.name='<script>|bad\nrow';
  assert.ok(editionTable({editions:[edition]}).includes('&lt;script&gt;&#124;bad row'));
  edition.ordered_downloads=[{url:'javascript:alert(1)',format:'HTML'}];
  assert.throws(()=>editionTable({editions:[edition]}),/HTTPS/);
});
test('templates reject forgotten and misspelled slots',()=>{
  assert.equal(fillTemplate('a {{editions}} b',{editions:'ok'}),'a ok b');
  assert.throws(()=>fillTemplate('{{typo}}',{editions:'ok'}),/Unknown/);
  assert.throws(()=>fillTemplate('no slot',{editions:'ok'}),/Missing/);
});
test('legacy and modern inputs form an exact partition; incomplete metadata never erases accepted work',async()=>{
  const root=await mkdtemp(join(tmpdir(),'olp-catalogue-test-'));
  try {
    const f=fixture();await mkdir(join(root,'catalogue/legacy'),{recursive:true});
    await writeFile(join(root,'registry.toml'),'schema_version = 1\n[[editions]]\nid = "openlogic-a"\nrepository = "https://github.com/example/a"\nlocale = "aa"\n');
    await writeFile(join(root,'catalogue/catalogue-metadata.json'),JSON.stringify(f.metadata));
    const legacy=join(root,'catalogue/legacy/openlogic-a.json');
    await writeFile(legacy,JSON.stringify(f.inputs.get('openlogic-a')));
    const retained=await loadCatalogueSources(root,{readModern:async()=>({id:'openlogic-a',kind:'incomplete',missing:['release.json']})});
    assert.deepEqual(retained.catalogue.editions,[f.edition]);assert.equal(retained.witnesses[0].kind,'legacy');
    const modern={kind:'modern',id:'openlogic-a',input:{...f.inputs.get('openlogic-a'),schema:'openlogic.edition-catalogue.v1'}};
    await assert.rejects(loadCatalogueSources(root,{readModern:async()=>modern}),/Both modern and legacy/);
    await unlink(legacy);
    const migrated=await loadCatalogueSources(root,{readModern:async()=>modern});
    assert.equal(migrated.witnesses[0].kind,'modern');assert.deepEqual(migrated.catalogue.editions,[f.edition]);
    await assert.rejects(loadCatalogueSources(root,{readModern:async()=>({kind:'incomplete'})}),/No usable source/);
  } finally {
    assert.equal(dirname(resolve(root)),resolve(tmpdir()));assert.ok(basename(root).startsWith('olp-catalogue-test-'));
    await rm(root,{recursive:true,force:true});
  }
});
test('one-character drift in every generated output is detected without writing in check mode',async()=>{
  const root=await mkdtemp(join(tmpdir(),'olp-catalogue-test-'));
  try {
    await mkdir(join(root,'catalogue'));
    const names=['README.md','index.html','index.ps.html','catalogue/editions.json','catalogue/ownership.json','catalogue/releases.json','catalogue/textbooks.json','catalogue/release-selection.json','catalogue/textbook-selection.json'];
    const files=Object.fromEntries(names.map(name=>[name,'expected\n']));
    await output(files,false,root);assert.deepEqual(await output(files,true,root),[]);
    for(const name of names) {
      await writeFile(join(root,name),files[name]+'x');
      await assert.rejects(output(files,true,root),/Generated files differ/);
      assert.equal(await readFile(join(root,name),'utf8'),files[name]+'x');
      await writeFile(join(root,name),files[name]);
    }
    await assert.rejects(output({'accessible/en/index.html':'do not touch'},false,root),/Unexpected generated output/);
  } finally {
    assert.equal(dirname(resolve(root)),resolve(tmpdir()));
    assert.ok(basename(root).startsWith('olp-catalogue-test-'));
    await rm(root,{recursive:true,force:true});
  }
});
