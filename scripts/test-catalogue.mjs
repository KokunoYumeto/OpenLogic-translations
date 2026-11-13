import { test } from 'node:test';
import assert from 'node:assert/strict';
import { selectRelease } from './generate-catalogue.mjs';

const release=(tag,date='2026-11-13T00:00:00Z',extra={})=>({tag_name:tag,published_at:date,draft:false,prerelease:false,...extra});
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
  const result=selectRelease({id:'openlogic-fr',release_tag:'v1'},[earlier,later,release('draft',undefined,{draft:true})]);
  assert.equal(result.accepted,earlier);assert.equal(result.available,later);
});
test('Missing accepted release stays absent rather than silently falling back',()=>{
  assert.equal(selectRelease({id:'openlogic-gu-gujr-in',release_tag:'missing'},[release('other')]).accepted,null);
});
