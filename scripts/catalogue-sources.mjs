import { readFile, readdir } from 'node:fs/promises';
import { resolve } from 'node:path';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { checkPublicRecord } from './modern-catalogue.mjs';

const parse = text => JSON.parse(text.replace(/^\uFEFF/, ''));
const digest = data => createHash('sha256').update(data).digest('hex');

export function parseToml(text) {
  return new Promise((done, fail) => {
    const program = "import json,sys,tomllib; print(json.dumps(tomllib.loads(sys.stdin.buffer.read().decode('utf-8-sig'))))";
    const child = spawn(process.env.OLPKIT_PYTHON || 'python', ['-I', '-B', '-c', program], {windowsHide:true});
    let stdout='', stderr='';
    const timer=setTimeout(()=>{child.kill();fail(Error('TOML parser timeout'));},15000);
    child.stdout.on('data', data=>{stdout+=data;if(stdout.length>2*1024*1024){child.kill();fail(Error('Registry exceeds parser limit'));}});
    child.stderr.on('data', data=>{stderr=(stderr+data).slice(-2000);});
    child.on('error', error=>{clearTimeout(timer);fail(error);});
    child.on('close', code=>{clearTimeout(timer);if(code!==0)fail(Error('Invalid registry TOML: '+stderr));else {try{done(parse(stdout));}catch(error){fail(error);}}});
    child.stdin.on('error', error=>{if(error.code!=='EPIPE')fail(error);});
    child.stdin.end(text);
  });
}

export function validateRegistry(registry) {
  if(registry.schema_version!==1 || !Array.isArray(registry.editions) || !registry.editions.length)throw Error('Invalid edition registry');
  const ids=new Set();
  for(const row of registry.editions) {
    if(Object.keys(row).some(k=>!['id','repository','locale'].includes(k)))throw Error('Unsupported registry field');
    if(!/^openlogic-[a-z0-9-]+$/.test(row.id||'') || ids.has(row.id))throw Error('Invalid or duplicate edition id');
    ids.add(row.id);
    if(!/^[A-Za-z0-9-]+$/.test(row.locale||''))throw Error('Invalid edition locale');
    if(typeof row.repository!=='string' || row.repository && !/^https:\/\/github\.com\/[\w.-]+\/[\w.-]+(?:\/tree\/[\w./-]+)?$/.test(row.repository))throw Error('Invalid edition repository');
  }
  return registry;
}

export function assembleLegacyCatalogue(registry, metadata, inputs) {
  validateRegistry(registry);
  checkPublicRecord(metadata);
  if(!Array.isArray(metadata.editions) || metadata.editions.length)throw Error('Shared metadata must contain an empty editions slot');
  const expected=registry.editions.map(r=>r.id);
  if(inputs.size!==expected.length || [...inputs.keys()].some(id=>!expected.includes(id)))throw Error('Registry/source partition differs');
  const editions=[], promotions={}, textbooks=[], witnesses=[];
  for(const row of registry.editions) {
    const input=inputs.get(row.id);
    if(!input || !['openlogic.legacy-edition-input.v1','openlogic.edition-catalogue.v1'].includes(input.schema))throw Error('Missing edition source: '+row.id);
    const edition=input.edition;
    checkPublicRecord(input);
    if(edition.id!==row.id || (edition.repository||'')!==row.repository)throw Error('Edition identity differs from registry: '+row.id);
    if(!['accepted-only','latest'].includes(input.release_discovery))throw Error('Explicit release discovery policy required: '+row.id);
    if(input.release_selection)promotions[row.id]=structuredClone(input.release_selection);
    if(input.textbook) {
      const t=input.textbook;
      if(t.id!==row.locale || t.language_tag!==edition.language_tag || !Number.isInteger(t.order) || t.order<0)throw Error('Textbook identity differs from edition: '+row.id);
      textbooks.push({...structuredClone(t),repository:row.repository});
    }
    editions.push(structuredClone(edition));
    witnesses.push({id:row.id,kind:input.schema==='openlogic.edition-catalogue.v1'?'modern':'legacy',releaseDiscovery:input.release_discovery});
  }
  textbooks.sort((a,b)=>a.order-b.order);
  if(new Set(textbooks.map(t=>t.id)).size!==textbooks.length || new Set(textbooks.map(t=>t.order)).size!==textbooks.length)throw Error('Ambiguous textbook identity/order');
  return {catalogue:{...structuredClone(metadata),editions},
    policy:{schema:'openlogic.release-selection.v1',promotions},
    textbookSelection:Object.fromEntries(textbooks.filter(t=>t.selection).map(t=>[t.id,t.selection])),
    textbooks,witnesses};
}

export async function loadCatalogueSources(root, {readModern}={}) {
  const registryText=await readFile(resolve(root,'registry.toml'),'utf8');
  const registry=validateRegistry(await parseToml(registryText));
  const metadataText=await readFile(resolve(root,'catalogue/catalogue-metadata.json'),'utf8');
  const names=(await readdir(resolve(root,'catalogue/legacy'))).filter(n=>n.endsWith('.json')).sort();
  const expected=registry.editions.map(r=>r.id+'.json').sort();
  if(names.some(name=>!expected.includes(name)))throw Error('Legacy input files differ from registry');
  const inputs=new Map(), migrations=[], sourceFiles=[{path:'registry.toml',sha256:digest(registryText)},{path:'catalogue/catalogue-metadata.json',sha256:digest(metadataText)}];
  for(const row of registry.editions) {
    const modern=readModern?await readModern(row):null;
    if(modern) migrations.push(modern);
    if(modern?.kind==='modern') {
      if(names.includes(row.id+'.json'))throw Error('Both modern and legacy sources present; reconcile before removing legacy: '+row.id);
      inputs.set(row.id,modern.input);
      sourceFiles.push({url:modern.contract_url,sha256:modern.contract_sha256,commit:modern.commit,catalogue_sha256:modern.catalogue_sha256});
      continue;
    }
    if(!names.includes(row.id+'.json'))throw Error('No usable source for edition: '+row.id);
    const name='catalogue/legacy/'+row.id+'.json';const text=await readFile(resolve(root,name),'utf8');
    inputs.set(row.id,parse(text));sourceFiles.push({path:name,sha256:digest(text)});
  }
  return {...assembleLegacyCatalogue(registry,parse(metadataText),inputs),registry,sourceFiles,migrations};
}
