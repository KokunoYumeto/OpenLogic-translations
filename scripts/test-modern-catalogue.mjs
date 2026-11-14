import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {bindModernRecord,verifyReleaseManifest,inspectModernSource,checkPublicRecord} from './modern-catalogue.mjs';

const hash=b=>createHash('sha256').update(b).digest('hex');
function fixture() {
  const row={id:'openlogic-test',locale:'test',repository:'https://github.com/example/test'};
  const input={schema:'openlogic.edition-catalogue.v1',link_base:'https://example.invalid/hub/',edition:{...row,language_tag:'en',name:'Test',scripts:['Latn'],version_doi:'10.1234/retained',source_units_translated:26,standalone_reader_units:7,release_tag:'v1'},release_discovery:'accepted-only',release_selection:null,textbook:null};
  const raw=Buffer.from(JSON.stringify(input));
  const contract={locale:'test',repository:row.repository,language_tag:'en',script:'Latn',public:{title:'Title',description:'Scope',limitations:['Review incomplete'],attribution:'Actual model and effort',license:'CC BY 4.0',catalogue:{path:'publication/catalogue.json',sha256:hash(raw)}}};
  const tagCommit='a'.repeat(40);
  const assets=[{name:'reader.pdf',format:'PDF',bytes:123,sha256:'b'.repeat(64),url:row.repository+'/releases/download/v1/reader.pdf'}];
  const ledgerBytes=Buffer.from('fixture unit ledger');
  const manifest={schema_version:1,edition:'test',product_group:'complete',tag:'v1',commit:tagCommit,pins:{olp:{repository:'https://github.com/OpenLogicProject/OpenLogic',commit:'c'.repeat(40)}},unit_ledger:{path:'units.jsonl',sha256:hash(ledgerBytes)},engine:'xelatex',tool_versions:{xelatex:'fixture version'},source_units:26,reader_units:7,assets,gates:[{id:'coverage',status:'not-run',scope:'Reader'}],attribution:'Actual model and effort',license:'CC BY 4.0'};
  const release={tag_name:'v1',published_at:'2026-11-14T00:00:00Z',html_url:row.repository+'/releases/tag/v1',draft:false,prerelease:false,assets:assets.map(a=>({name:a.name,size:a.bytes,digest:'sha256:'+a.sha256,browser_download_url:a.url}))};
  return {row,input,raw,contract,tagCommit,manifest,release,ledgerBytes};
}
test('modern record preserves historical DOI, distinct source/reader counts and qualifiers',()=>{
  const f=fixture(),r=bindModernRecord(f.row,f.contract,f.raw);
  assert.equal(r.edition.version_doi,'10.1234/retained');assert.equal(r.edition.source_units_translated,26);assert.equal(r.edition.standalone_reader_units,7);
  const preserved=structuredClone(r);delete preserved.edition.public_metadata;
  assert.deepEqual(preserved,f.input);assert.equal(r.edition.public_metadata.attribution,f.contract.public.attribution);
  r.edition.name='Changed';assert.equal(f.input.edition.name,'Test');
});
test('modern record rejects changed bytes and cross-language/repository substitution',()=>{
  const f=fixture();assert.throws(()=>bindModernRecord(f.row,f.contract,Buffer.concat([f.raw,Buffer.from(' ')])),/bytes differ/);
  for(const change of [{locale:'other'},{repository:'https://github.com/example/other'},{language_tag:'fr'},{script:'Arab'}])assert.throws(()=>bindModernRecord(f.row,{...f.contract,...change},f.raw));
  assert.throws(()=>bindModernRecord(f.row,{...f.contract,public:{...f.contract.public,attribution:''}},f.raw),/attribution/);
});
test('modern public record rejects private chat and machine locators without printing their contents',()=>{
  assert.throws(()=>checkPublicRecord({owner_task_id:'secret'}),/Private administrative field/);
  assert.throws(()=>checkPublicRecord({note:'codex://threads/private'}),/Private locator/);
  assert.throws(()=>checkPublicRecord({note:'C:/interlanguage-task-state/private'}),/Private locator/);
  assert.doesNotThrow(()=>checkPublicRecord({author:'Original human author',version_doi:'10.1234/preserved'}));
});
test('release binding requires exact tag, edition, bytes, hashes and asset links',()=>{
  const f=fixture();assert.equal(verifyReleaseManifest(f.manifest,f.release,f.row,f.tagCommit).all_gates_pass,false);
  for(const change of [{tag:'v2'},{edition:'other'},{commit:'d'.repeat(40)},{source_units:-1},{gates:[]},{gates:[...f.manifest.gates,...f.manifest.gates]},{unit_ledger:undefined},{engine:undefined},{tool_versions:{}}])assert.throws(()=>verifyReleaseManifest({...f.manifest,...change},f.release,f.row,f.tagCommit));
  for(const change of [{size:124},{digest:'sha256:'+'d'.repeat(64)},{browser_download_url:'https://example.invalid/wrong'}])assert.throws(()=>verifyReleaseManifest(f.manifest,{...f.release,assets:[{...f.release.assets[0],...change}]},f.row,f.tagCommit),/asset differs/);
});
test('failed or unperformed gates are retained and never become a passed release',()=>{
  const f=fixture();
  for(const status of ['pass','fail','not-run']) {
    f.manifest.gates[0].status=status;
    const r=verifyReleaseManifest(f.manifest,f.release,f.row,f.tagCommit);
    assert.equal(r.all_gates_pass,status==='pass');assert.equal(r.manifest.gates[0].status,status);
  }
});
test('an observed missing contract permits legacy; a network failure does not',async()=>{
  const f=fixture();const transport={parseToml:async()=>f.contract,api:async(path)=>path.endsWith('/commits/HEAD')?{sha:f.tagCommit}:null};
  assert.equal((await inspectModernSource(f.row,transport)).reason,'no-edition-contract');
  await assert.rejects(inspectModernSource(f.row,{...transport,api:async()=>{throw Error('timeout');}}),/timeout/);
});
test('a build-only contract is explicitly incomplete, not a silently modernized edition',async()=>{
  const f=fixture();const raw=Buffer.from('fixture');
  const r=await inspectModernSource(f.row,{api:async path=>path.endsWith('/commits/HEAD')?{sha:f.tagCommit}:{encoding:'base64',size:raw.length,content:raw.toString('base64')},parseToml:async()=>({...f.contract,public:undefined})});
  assert.equal(r.kind,'incomplete');assert.ok(r.missing.includes('public.catalogue'));assert.ok(r.missing.includes('public.attribution'));
});
test('complete source replay verifies contract, metadata and actual release manifest bytes',async()=>{
  const f=fixture(),manifestBytes=Buffer.from(JSON.stringify(f.manifest));
  const manifestAsset={name:'release.json',size:manifestBytes.length,digest:'sha256:'+hash(manifestBytes),browser_download_url:f.row.repository+'/releases/download/v1/release.json'};
  f.release.assets.push(manifestAsset);
  const requests=[];
  const api=async path=>{
    requests.push(path);
    if(path.includes('/commits/'))return {sha:f.tagCommit};
    if(path.includes('/contents/')) {
      const raw=path.includes('olp-edition.toml')?Buffer.from('fixture contract'):path.includes('units.jsonl')?f.ledgerBytes:f.raw;
      return {encoding:'base64',size:raw.length,content:raw.toString('base64')};
    }
    return [f.release];
  };
  const r=await inspectModernSource(f.row,{api,parseToml:async()=>f.contract,bytes:async()=>manifestBytes});
  assert.equal(r.kind,'modern');assert.equal(r.latest_products[0].group,'complete');assert.equal(r.latest_products[0].all_gates_pass,false);
  assert.equal(r.input.edition.products[0].reader_units,7);
  assert.equal(r.input.edition.products[0].all_gates_pass,false);
  assert.equal(r.input.edition.products[0].gates[0].status,'not-run');
  assert.equal(r.input.edition.products[0].manifest.url,manifestAsset.browser_download_url);
  assert.equal(r.input.edition.products[0].manifest.sha256,hash(manifestBytes));
  assert.equal(r.input.edition.metadata_sources.edition_contract.commit,f.tagCommit);
  assert.equal(r.input.edition.metadata_sources.catalogue.sha256,hash(f.raw));
  assert.equal(r.input.edition.version_doi,'10.1234/retained');
  assert.ok(requests.filter(x=>x.includes('/contents/')).every(x=>x.endsWith('?ref='+f.tagCommit)));
  await assert.rejects(inspectModernSource(f.row,{api,parseToml:async()=>f.contract,bytes:async()=>Buffer.concat([manifestBytes,Buffer.from('x')])}),/download differs/);
});
