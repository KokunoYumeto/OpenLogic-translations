import { readFile } from 'node:fs/promises';
import vm from 'node:vm';
import { resolve } from 'node:path';
const root=resolve(import.meta.dirname,'..');
const read=p=>readFile(resolve(root,p),'utf8');
const src=await read('interface-locales.js');
const context={};vm.createContext(context);
vm.runInContext(src.replaceAll('export ','')+'\nthis.messages=interfaceMessages;',context);
const messages=context.messages;
const en=await read('index.html'),ps=await read('index.ps.html');
const failures=[];const check=(v,s)=>{if(!v)failures.push(s)};
const keys=t=>[...t.matchAll(/data-ui(?:-aria-label|-placeholder|-content)?="([^"]+)"/g)].map(x=>x[1]);
check(JSON.stringify(keys(en))===JSON.stringify(keys(ps)),'identical static binding inventory');
for(const k of keys(en))check(!!messages[k]?.en&&!!messages[k]?.['ps-Arab-PK'],'complete pair '+k);
for(const [k,m] of Object.entries(messages)){
  check(!m['ps-Arab-PK'].includes('\ufffd'),'valid target encoding '+k);
  const placeholders=s=>[...s.matchAll(/\{[a-z]+\}/g)].map(x=>x[0]).sort().join(',');
  check(placeholders(m.en)===placeholders(m['ps-Arab-PK']),'variable parity '+k);
  if(m.html){
    const hrefs=s=>[...s.matchAll(/href="([^"]+)"/g)].map(x=>x[1]);
    check(hrefs(m.en).every(x=>hrefs(m['ps-Arab-PK']).includes(x)),'preserved HTML links '+k);
  }
}
check(ps.includes('<html lang="ps-Arab-PK" dir="rtl">'),'static RTL entry');
check(ps.includes('PASHTO632_REVIEW.ps.html'),'localized no-JS fallback');
const ledger=JSON.parse(await read('evidence/PASHTO_INTERFACE_CHOICES_20260930.json'));
check(ledger.choices.length===Object.keys(messages).length,'every UI choice mapped');
check(ledger.choices.every(x=>x.source===messages[x.id].en&&x.target===messages[x.id]['ps-Arab-PK']&&x.canon_consulted.length&&x.rationale_ps&&x.confidence_ps),'ledger/text exact alignment');
check((await read('site.js')).includes('applyInterfaceLocale(initialInterfaceLocale())'),'locale active before catalogue startup');
check((await read('scripts/build-site.mjs')).includes('interface-locales.js'),'deployment includes module');
check((await read('site.css')).includes('.method-grid article > span'),'decorative numbers do not restyle translated prose');
const review=await read('evidence/PASHTO_INTERFACE_REVIEW.ps.html');
check(ledger.choices.every(c=>review.includes(`id="${c.id}"`)),'human-readable review contains every choice');
check(ledger.choices.every(c=>c.confidence_score>=1&&c.confidence_score<=3&&c.canon_scope_ps),'bounded confidence and evidence limits');
check(new Set(ledger.choices.map(c=>c.rationale_ps)).size===ledger.choices.length,'specific rationales rather than repeated boilerplate');
for(const choice of ledger.choices)for(const where of choice.occurrences){
  if(where.line)check((where.file==='index.html'?en:ps).split('\n')[where.line-1]?.includes(`="${choice.id}"`),'exact occurrence '+choice.id);
}
for(const [url,docLang,expected] of [
  ['https://example.test/index.ps.html','ps-Arab-PK','ps-Arab-PK'],
  ['https://example.test/?lang=ps-Arab-PK','en','ps-Arab-PK'],
  ['https://example.test/index.ps.html?lang=en','ps-Arab-PK','en'],
  ['https://example.test/?lang=invalid','en','en']
]){
  const picker={value:''},fallback={href:''};
  const document={documentElement:{lang:docLang},querySelectorAll:()=>[],querySelector:s=>s==='#interface-language'?picker:fallback};
  const sandbox={URL,location:{href:url},document};vm.createContext(sandbox);
  vm.runInContext(src.replaceAll('export ','')+'\nthis.result=applyInterfaceLocale(initialInterfaceLocale());this.label=interfaceText("summary",{visible:1,total:25});',sandbox);
  check(sandbox.result===expected&&picker.value===expected,'locale precedence '+url);
  check(document.documentElement.dir===(expected==='en'?'ltr':'rtl'),'direction '+url);
  check(fallback.href===(expected==='en'?'README.md#read-or-inspect-an-edition':'evidence/PASHTO632_REVIEW.ps.html'),'localized fallback '+url);
  check(sandbox.label.includes('1')&&sandbox.label.includes('25')&&!sandbox.label.includes('{'),'summary substitution '+url);
}
console.log(JSON.stringify({status:failures.length?'FAIL':'PASS',messages:Object.keys(messages).length,static_bindings:keys(en).length,failures}));
if(failures.length)process.exit(1);
