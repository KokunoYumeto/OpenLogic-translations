import { test } from 'node:test';
import assert from 'node:assert/strict';
import { selectRelease, textbookReleaseAssets, gitHubFailureStatus } from './generate-catalogue.mjs';

const release=(tag,date='2026-11-13T00:00:00Z',extra={})=>({tag_name:tag,published_at:date,draft:false,prerelease:false,...extra});
test('authenticated HTTP failures are distinguished from an unavailable gh executable',()=>{
  assert.equal(gitHubFailureStatus({stdout:'{"status":"404","message":"Not Found"}'}),404);
  assert.equal(gitHubFailureStatus({stderr:'gh: Forbidden (HTTP 403)'}),403);
  assert.equal(gitHubFailureStatus({stderr:'gh: Unauthorized (HTTP 401)'}),401);
  assert.equal(gitHubFailureStatus({code:'ENOENT'}),null);
  assert.equal(gitHubFailureStatus({stdout:'not JSON',stderr:'connection reset'}),null);
});
test('English preservation cannot become the accessibility product',()=>{
  const old=release('frozen','2026-09-05T00:00:00Z');
  const result=selectRelease({id:'openlogic-en-frozen-722',release_tag:'frozen'},[release('accessible'),old]);
  assert.equal(result.accepted,old);assert.equal(result.available,old);
});
test('Arabic readers cannot become a newer review-only publication',()=>{
  const old=release('readers','2026-09-29T00:00:00Z');
  assert.equal(selectRelease({id:'openlogic-ar',release_tag:'readers'},[release('review'),old]).available,old);
});
test('Shared Interslavic repository cannot advertise Gauss',()=>{
  const result=selectRelease({id:'openlogic-isv'},[release('gauss-german-english')]);
  assert.equal(result.accepted,null);assert.equal(result.available,null);
});
test('Inter-Farsi cannot inherit an Iranian Persian reader release',()=>{
  assert.equal(selectRelease({id:'openlogic-interfarsi'},[release('fa-ir-r11')]).available,null);
});
test('Later ordinary releases are discoverable without overwriting accepted coverage',()=>{
  const earlier=release('v1','2026-09-01T00:00:00Z');const later=release('v2');
  const result=selectRelease({id:'openlogic-fr',release_tag:'v1'},[earlier,later,release('draft',undefined,{draft:true})],{discovery:'latest'});
  assert.equal(result.accepted,earlier);assert.equal(result.available,later);
});
test('Missing accepted release stays absent rather than silently falling back',()=>{
  assert.equal(selectRelease({id:'openlogic-gu-gujr-in',release_tag:'missing'},[release('other')]).accepted,null);
});

test('A textbook release cannot replace the full OpenLogic edition',()=>{
  const complete=release('complete-v1.4','2026-11-13T00:00:00Z');
  const textbook=release('slc-2026-11-14','2026-11-14T00:00:00Z');
  const result=selectRelease({id:'openlogic-mr-deva-in',release_tag:'complete-v1.4'},[textbook,complete],{discovery:'latest'});
  assert.equal(result.accepted,complete);assert.equal(result.available,complete);
});

test('Published textbook requires PDF, direct LaTeX and full source ZIP with digests',()=>{
  const files=['slc-screen-mr.pdf','slc-screen-mr.tex','slc-source-mr.zip'];
  const assets=files.map(name=>({name,size:123,digest:'sha256:'+'a'.repeat(64),browser_download_url:'https://example.invalid/'+name}));
  const record={draft:false,prerelease:false,assets};
  assert.equal(textbookReleaseAssets(record,'mr').single_file_latex.name,files[1]);
  assert.throws(()=>textbookReleaseAssets({...record,assets:assets.slice(0,2)},'mr'),/source_zip/);
  assert.throws(()=>textbookReleaseAssets({...record,assets:[...assets,assets[0]]},'mr'),/pdf/);
  assert.throws(()=>textbookReleaseAssets({...record,draft:true},'mr'),/not public/);
  assert.throws(()=>textbookReleaseAssets({...record,assets:assets.map(a=>({...a,digest:null}))},'mr'),/digest/);
});
