import { createHash } from 'node:crypto';

const hash=data=>createHash('sha256').update(data).digest('hex');
const object=x=>x && typeof x==='object' && !Array.isArray(x);
const text=x=>typeof x==='string' && x.trim().length>0;
const sha=x=>typeof x==='string' && /^[a-f0-9]{64}$/.test(x);
const commit=x=>typeof x==='string' && /^[a-f0-9]{40}$/.test(x);
const parse=data=>JSON.parse(Buffer.from(data).toString('utf8').replace(/^\uFEFF/,''));

export function checkPublicRecord(value, path='record') {
  if(Array.isArray(value))value.forEach((x,i)=>checkPublicRecord(x,path+'.'+i));
  else if(object(value))for(const [key,item] of Object.entries(value)) {
    if(/^(?:owner_task_id|task_id|thread_id|host_id|local_path|rollout_path|credential|token|api_key)$/i.test(key))throw Error('Private administrative field in public record: '+path+'.'+key);
    checkPublicRecord(item,path+'.'+key);
  }
  else if(typeof value==='string' && /(?:codex:\/\/threads\/|[A-Z]:[\\/](?:Users|interlanguage-task-state|olp-build)\b)/i.test(value))throw Error('Private locator in public record: '+path);
}

export function bindModernRecord(row, contract, raw) {
  const binding=contract.public?.catalogue;
  if(!binding || !/^(?!\/)(?!.*\.\.)(?!.*[\\:]).+\.json$/.test(binding.path||'') || !sha(binding.sha256))throw Error('Invalid public catalogue binding');
  if(hash(raw)!==binding.sha256)throw Error('Public catalogue bytes differ from contract');
  const input=parse(raw),e=input.edition;
  if(input.schema!=='openlogic.edition-catalogue.v1' || !object(e))throw Error('Invalid edition-owned catalogue record');
  if(contract.locale!==row.locale || contract.repository!==row.repository || e.id!==row.id || e.repository!==row.repository || e.language_tag!==contract.language_tag)throw Error('Modern edition identity does not match registry/contract');
  if(!Array.isArray(e.scripts) || !e.scripts.includes(contract.script))throw Error('Modern edition script differs from contract');
  if(!/^https:\/\/[^\s?#]+\/$/.test(input.link_base||''))throw Error('Explicit public hub link base required');
  for(const key of ['title','description','attribution','license'])if(!text(contract.public[key]))throw Error('Missing localized public field: '+key);
  if(!Array.isArray(contract.public.limitations)||contract.public.limitations.some(x=>!text(x)))throw Error('Explicit public limitations required');
  if(!['accepted-only','latest'].includes(input.release_discovery))throw Error('Explicit release discovery policy required');
  checkPublicRecord(input);
  const result=structuredClone(input);
  result.edition.public_metadata=Object.fromEntries(['title','description','limitations','attribution','license'].map(key=>[key,structuredClone(contract.public[key])]));
  return result;
}

export function verifyReleaseManifest(manifest, release, row, tagCommit) {
  if(release.draft||release.prerelease)throw Error('Manifest belongs to an unpublished release');
  if(manifest.schema_version!==1 || manifest.edition!==row.locale || manifest.tag!==release.tag_name || manifest.commit!==tagCommit || !commit(tagCommit))throw Error('Release identity does not match public tag');
  if(!text(manifest.product_group) || !object(manifest.pins) || !manifest.pins.olp || !commit(manifest.pins.olp.commit))throw Error('Incomplete product group or source pins');
  if(!object(manifest.unit_ledger)||!/^(?!\/)(?!.*\.\.)(?!.*[\\:]).+$/.test(manifest.unit_ledger.path||'')||!sha(manifest.unit_ledger.sha256))throw Error('Exact unit ledger identity required');
  if(!['pdflatex','xelatex','lualatex','none'].includes(manifest.engine)||!object(manifest.tool_versions)||!Object.keys(manifest.tool_versions).length||Object.values(manifest.tool_versions).some(v=>!text(v)))throw Error('Recorded engine and tool versions required');
  for(const key of ['source_units','reader_units'])if(!Number.isSafeInteger(manifest[key])||manifest[key]<0)throw Error('Invalid release coverage');
  if(!text(manifest.attribution)||!text(manifest.license))throw Error('Release authorship and rights required');
  if(!Array.isArray(manifest.assets)||!manifest.assets.length||new Set(manifest.assets.map(a=>a.name)).size!==manifest.assets.length)throw Error('Missing or duplicate manifest assets');
  for(const a of manifest.assets) {
    const matches=release.assets.filter(x=>x.name===a.name);
    if(matches.length!==1||matches[0].size!==a.bytes||!sha(a.sha256)||matches[0].digest!=='sha256:'+a.sha256||matches[0].browser_download_url!==a.url)throw Error('Manifest asset differs from public API: '+a.name);
    if(!['PDF','TEX','ZIP','EPUB','HTML'].includes(a.format))throw Error('Unknown release format');
  }
  if(!Array.isArray(manifest.gates)||!manifest.gates.length||new Set(manifest.gates.map(g=>g.id)).size!==manifest.gates.length)throw Error('Missing or duplicate release gates');
  for(const g of manifest.gates)if(!text(g.id)||!text(g.scope)||!['pass','fail','not-run'].includes(g.status))throw Error('Invalid release gate');
  checkPublicRecord(manifest);
  return {group:manifest.product_group,all_gates_pass:manifest.gates.every(g=>g.status==='pass'),manifest:structuredClone(manifest)};
}

// The transport returns null only for an observed HTTP 404, never on timeout/authentication failure.
export async function inspectModernSource(row, {api,bytes,parseToml}) {
  if(!/^https:\/\/github\.com\/[\w.-]+\/[\w.-]+$/.test(row.repository))return {kind:'legacy',id:row.id,reason:'not-a-single-repository-edition'};
  const repository=new URL(row.repository).pathname.slice(1);
  const head=await api(`repos/${repository}/commits/HEAD`);
  if(!commit(head?.sha))throw Error('Invalid default-branch identity');
  const file=await api(`repos/${repository}/contents/olp-edition.toml?ref=${head.sha}`,{optional:true});
  if(file===null)return {kind:'legacy',id:row.id,reason:'no-edition-contract',commit:head.sha};
  if(file.encoding!=='base64'||file.size>2*1024*1024||typeof file.content!=='string')throw Error('Unsupported edition contract response');
  const raw=Buffer.from(file.content,'base64');
  const contract=await parseToml(raw.toString('utf8'));
  if(contract.locale!==row.locale)return {kind:'legacy',id:row.id,reason:'contract-belongs-to-another-locale',commit:head.sha};
  const witness={id:row.id,commit:head.sha,contract_sha256:hash(raw),contract_url:`https://raw.githubusercontent.com/${repository}/${head.sha}/olp-edition.toml`};
  const missing=['title','description','attribution','license'].filter(k=>!text(contract.public?.[k]));
  if(!Array.isArray(contract.public?.limitations))missing.push('limitations');
  if(!contract.public?.catalogue)missing.push('catalogue');
  if(missing.length)return {...witness,kind:'incomplete',missing:missing.map(k=>'public.'+k)};
  const binding=contract.public.catalogue;
  if(!/^(?!\/)(?!.*\.\.)(?!.*[\\:]).+\.json$/.test(binding.path||''))throw Error('Unsafe metadata path');
  const record=await api(`repos/${repository}/contents/${binding.path.split('/').map(encodeURIComponent).join('/')}?ref=${head.sha}`);
  if(record.encoding!=='base64'||record.size>2*1024*1024||typeof record.content!=='string')throw Error('Unsupported catalogue record response');
  const input=bindModernRecord(row,contract,Buffer.from(record.content,'base64'));
  const releases=await api(`repos/${repository}/releases?per_page=100`);
  if(!Array.isArray(releases))throw Error('Invalid release listing');
  const manifests=[];
  for(const release of releases.filter(r=>!r.draft&&!r.prerelease)) {
    const candidates=release.assets.filter(a=>a.name==='release.json');
    if(!candidates.length)continue;
    if(candidates.length!==1||candidates[0].size>2*1024*1024||candidates[0].size<1)throw Error('Invalid release manifest asset');
    const a=candidates[0],data=await bytes(a.browser_download_url,{maxBytes:2*1024*1024});
    if(data.length!==a.size||a.digest!=='sha256:'+hash(data))throw Error('Release manifest download differs from API');
    const tag=await api(`repos/${repository}/commits/${encodeURIComponent(release.tag_name)}`);
    const verified=verifyReleaseManifest(parse(data),release,row,tag.sha);
    const ledger=verified.manifest.unit_ledger;
    let ledgerFile=await api(`repos/${repository}/contents/${ledger.path.split('/').map(encodeURIComponent).join('/')}?ref=${tag.sha}`);
    if(ledgerFile.size>8*1024*1024)throw Error('Unit ledger exceeds metadata limit');
    if(ledgerFile.encoding==='none' && /^[a-f0-9]{40}$/.test(ledgerFile.sha||''))ledgerFile=await api(`repos/${repository}/git/blobs/${ledgerFile.sha}`);
    if(ledgerFile.encoding!=='base64'||ledgerFile.size>8*1024*1024||typeof ledgerFile.content!=='string'||hash(Buffer.from(ledgerFile.content,'base64'))!==ledger.sha256)throw Error('Unit ledger bytes differ from release manifest');
    manifests.push({...verified,date:release.published_at,url:release.html_url,manifest_url:a.browser_download_url,sha256:hash(data)});
  }
  const required=[input.edition.release_tag,input.textbook?.selection?.release_tag].filter(Boolean);
  const absent=required.filter(tag=>!manifests.some(r=>r.manifest.tag===tag));
  if(!manifests.length||absent.length)return {...witness,kind:'incomplete',missing:absent.length?absent.map(tag=>'release.json:'+tag):['release.json'],catalogue_sha256:binding.sha256};
  const latest=new Map();
  for(const m of manifests.sort((a,b)=>Date.parse(b.date)-Date.parse(a.date)))if(!latest.has(m.group))latest.set(m.group,m);
  // Publish the evidence we actually read, including failed/not-run checks.
  // A newer product remains distinct from the owner's selected reader and
  // cannot silently replace it with a smaller textbook or another register.
  input.edition.products=[...latest.values()].map(m=>({
    ...structuredClone(m.manifest),published_at:m.date,release_url:m.url,
    manifest:{url:m.manifest_url,sha256:m.sha256},all_gates_pass:m.all_gates_pass
  }));
  input.edition.metadata_sources={edition_contract:{url:witness.contract_url,sha256:witness.contract_sha256,commit:head.sha},
    catalogue:{url:`https://raw.githubusercontent.com/${repository}/${head.sha}/${binding.path}`,sha256:binding.sha256}};
  return {...witness,kind:'modern',input,contract,catalogue_sha256:binding.sha256,manifests,latest_products:[...latest.values()]};
}
