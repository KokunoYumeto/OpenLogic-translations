import { readFile, writeFile, mkdtemp, unlink, rmdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { resolve, join } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';
import { loadCatalogueSources, parseToml } from './catalogue-sources.mjs';
import { editionTable, fillTemplate, editionRouting } from './catalogue-render.mjs';
import { inspectModernSource } from './modern-catalogue.mjs';

const root = resolve(fileURLToPath(new URL('..', import.meta.url)));
const exec = promisify(execFile);
const json = x => JSON.stringify(x, null, 2) + '\n';
const read = name => readFile(resolve(root, name), 'utf8');
const parse = text => JSON.parse(text.replace(/^\uFEFF/, ''));
const hash = data => createHash('sha256').update(data).digest('hex');
const escape = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const requestCache = new Map();

export function gitHubFailureStatus(error) {
  let status;
  try {status=Number(parse(error.stdout).status);} catch {}
  if(!Number.isInteger(status)||status<400||status>599)status=Number(String(error.stderr||'').match(/\(HTTP (\d{3})\)/)?.[1]);
  return Number.isInteger(status)&&status>=400&&status<=599?status:null;
}

export async function api(path, {optional=false}={}) {
  if (!/^repos\/[\w.-]+\/[\w.-]+\//.test(path)) throw Error('Unsupported GitHub API path');
  const key=path+(optional?'#optional':'');
  if (!requestCache.has(key)) requestCache.set(key, (async () => {
    // gh reads its credential store; neither credentials nor response headers are printed.
    try { return parse((await exec('gh', ['api', path], { maxBuffer: 32 * 1024 * 1024 })).stdout); }
    catch (error) {
      const status=gitHubFailureStatus(error);
      if(status===404&&optional)return null;
      // A known HTTP result is authoritative. Do not retry permissions, missing
      // files or quota errors through a second anonymous identity.
      if(status!==null)throw Error(`GitHub API ${status}: ${path}`);
      const response = await fetch('https://api.github.com/' + path, { signal: AbortSignal.timeout(60000) });
      if(response.status===404 && optional)return null;
      if (!response.ok) throw Error(`GitHub API ${response.status}: ${path}`);
      return response.json();
    }
  })());
  return requestCache.get(key);
}

export async function bytes(url,{maxBytes=256*1024*1024}={}) {
  const response = await fetch(url, { signal: AbortSignal.timeout(60000) });
  if (!response.ok) throw Error(`Download ${response.status}: ${url}`);
  const chunks=[];let size=0;
  for await(const chunk of response.body) {
    size+=chunk.length;if(size>maxBytes)throw Error('Download exceeds byte limit');
    chunks.push(chunk);
  }
  return Buffer.concat(chunks);
}

async function loadSources() {
  return loadCatalogueSources(root,{readModern:row=>inspectModernSource(row,{api,bytes,parseToml})});
}

function block(text, name, content, before) {
  const begin = `<!-- ${name}:begin -->`, end = `<!-- ${name}:end -->`;
  const generated = `${begin}\n${content.trim()}\n${end}`;
  if (text.includes(begin) !== text.includes(end)) throw Error(`Unpaired ${name} markers`);
  if (text.includes(begin)) return text.slice(0, text.indexOf(begin)) + generated + text.slice(text.indexOf(end) + end.length);
  if (before && text.includes(before)) return text.replace(before, generated + '\n\n' + before);
  return text.trimEnd() + '\n\n' + generated + '\n';
}

export async function output(files, check, directory=root) {
  const changed = [];
  for (const [name, content] of Object.entries(files)) {
    if(!['README.md','index.html','index.ps.html','catalogue/editions.json','catalogue/ownership.json','catalogue/releases.json','catalogue/textbooks.json','catalogue/release-selection.json','catalogue/textbook-selection.json'].includes(name))throw Error('Unexpected generated output: '+name);
    const old = await readFile(resolve(directory,name),'utf8').catch(error => { if (error.code === 'ENOENT') return null; throw error; });
    if (old !== content) {
      changed.push(name);
      if (!check) await writeFile(resolve(directory, name), content, 'utf8');
    }
  }
  if (check && changed.length) throw Error('Generated files differ: ' + changed.join(', '));
  return changed;
}

function repositoryPath(url) {
  const parts=new URL(url).pathname.split('/').filter(Boolean);
  if(parts.length!==2)throw Error('Textbook requires a canonical repository URL');
  return parts.join('/');
}

export function textbookReleaseAssets(release, id) {
  if (release.draft || release.prerelease) throw Error('Textbook release is not public');
  const result = {};
  for (const [role, pattern] of Object.entries({pdf:`^slc-screen-${id}\\.pdf$`,single_file_latex:`^slc-screen-${id}\\.tex$`,source_zip:`^slc-source-${id}\\.zip$`})) {
    const matches=release.assets.filter(a=>new RegExp(pattern).test(a.name));
    if(matches.length!==1)throw Error(`Textbook ${role} must identify one asset`);
    const asset=matches[0];
    if(!/^sha256:[0-9a-f]{64}$/.test(asset.digest||''))throw Error('Missing textbook asset digest: '+asset.name);
    result[role]={url:asset.browser_download_url,name:asset.name,bytes:asset.size,sha256:asset.digest.slice(7)};
  }
  return result;
}

async function pdfPages(data) {
  const directory=await mkdtemp(join(tmpdir(),'olp-hub-pdf-'));
  const filename=join(directory,'reader.pdf');
  try {
    await writeFile(filename,data);
    const {stdout}=await exec('pdfinfo',[filename],{maxBuffer:1024*1024});
    const pages=Number(stdout.match(/^Pages:\s+(\d+)\s*$/m)?.[1]);
    if(!Number.isSafeInteger(pages)||pages<1)throw Error('Could not read textbook page count');
    return pages;
  } finally {
    await unlink(filename).catch(error=>{if(error.code!=='ENOENT')throw error;});
    await rmdir(directory);
  }
}

async function publishedTextbook(pilot, selection) {
  const repository=repositoryPath(pilot.repository);
  if(!/^[0-9a-f]{40}$/.test(selection.ref)||!/^courses\/[a-z0-9-]+$/.test(selection.path))throw Error('Invalid textbook source identity');
  const release=await api(`repos/${repository}/releases/tags/${encodeURIComponent(selection.release_tag)}`);
  const tagCommit=(await api(`repos/${repository}/commits/${encodeURIComponent(selection.release_tag)}`)).sha;
  if(tagCommit!==selection.ref)throw Error('Textbook tag no longer matches its selected source');
  const raw=file=>`https://raw.githubusercontent.com/${repository}/${selection.ref}/${selection.path}/${file}`;
  const manifestBytes=await bytes(raw('MANIFEST.json'));
  const manifest=parse(manifestBytes.toString('utf8'));
  const assets=textbookReleaseAssets(release,pilot.id);
  for(const [role,asset] of Object.entries(assets)) {
    const data=await bytes(asset.url);
    if(data.length!==asset.bytes||hash(data)!==asset.sha256)throw Error('Textbook release bytes differ: '+asset.name);
    if(role==='pdf')asset.pages=await pdfPages(data);
  }
  const editionBytes=await bytes(`https://raw.githubusercontent.com/${repository}/${selection.ref}/olp-edition.toml`);
  const engineName=editionBytes.toString('utf8').match(/^engine\s*=\s*"([a-z]+)"\s*$/m)?.[1];
  const engine={xelatex:'XeLaTeX',lualatex:'LuaLaTeX',pdflatex:'pdfLaTeX'}[engineName];
  if(!engine)throw Error('Missing textbook engine declaration');
  return {book:'sets-logic-computation',title:manifest.title,original_title:'Sets, Logic, Computation',
    language_tag:pilot.language_tag,language_name:pilot.name,repository:`https://github.com/${repository}`,
    branch:null,ref:selection.ref,path:selection.path,state:'published',release:release.html_url,release_tag:release.tag_name,
    ...assets,engine,olp_commit:(manifest.sources.open_logic||manifest.sources.olp).commit,slc_commit:manifest.sources.slc.commit,
    epub:null,html:null,manifest:{url:raw('MANIFEST.json'),sha256:hash(manifestBytes)},
    edition_metadata:{url:`https://raw.githubusercontent.com/${repository}/${selection.ref}/olp-edition.toml`,sha256:hash(editionBytes)},
    authors:['Richard Zach','Open Logic Project contributors'],translation:manifest.translation,
    rights:{text:'CC BY 4.0',portraits:'Matthew Leadbeater, CC BY-NC 4.0',photographs:'Individual terms and credits in each source package',fonts:'Individual font licences in each source package'}};
}

async function textbook(pilot, selection) {
  if(selection)return publishedTextbook(pilot,selection);
  const repository = repositoryPath(pilot.repository);
  const ref = (await api(`repos/${repository}/commits/textbook-slc`)).sha;
  const directory = await api(`repos/${repository}/contents/textbooks/slc?ref=${ref}`);
  if (!Array.isArray(directory)) throw Error('Missing textbook directory: ' + repository);
  const raw = file => `https://raw.githubusercontent.com/${repository}/${ref}/textbooks/slc/${file}`;
  const manifestBytes = await bytes(raw('MANIFEST.json'));
  const manifest = parse(manifestBytes.toString('utf8'));
  const pdf = manifest.screen?.output || manifest.screen_pdf || manifest.reader_pdf;
  if (!pdf?.sha256 || !pdf.pages) throw Error('PDF manifest incomplete: ' + repository);
  const pdfName = pdf.path || pdf.file;
  const pdfBytes = await bytes(raw(pdfName));
  if (hash(pdfBytes) !== pdf.sha256 || (pdf.bytes && pdf.bytes !== pdfBytes.length)) throw Error('PDF differs from manifest: ' + repository);
  async function optional(extension, declared) {
    const filename = declared?.path || declared?.file || directory.find(x => x.type === 'file' && x.name.match(new RegExp(`^slc-(?:screen|source)[^/]*\\.${extension}$`)))?.name;
    if (!filename) return null;
    if (!directory.some(x => x.name === filename)) throw Error('Declared output absent: ' + filename);
    const data = await bytes(raw(filename));
    if (declared?.sha256 && declared.sha256 !== hash(data)) throw Error('Output differs from manifest: ' + filename);
    return { url:raw(filename), name:filename, bytes:data.length, sha256:hash(data) };
  }
  const sources = manifest.sources;
  const olp = sources.open_logic || sources.olp;
  let engine = manifest.screen?.engine || manifest.screen_pdf?.engine || manifest.build?.engine;
  if (/XeTeX/.test(engine)) engine = 'XeLaTeX';
  return {
    book:'sets-logic-computation', title:manifest.title, original_title:'Sets, Logic, Computation',
    language_tag:pilot.language_tag, language_name:pilot.name, repository:`https://github.com/${repository}`,
    branch:'textbook-slc', ref, path:'textbooks/slc', state:'pilot',
    pdf:{url:raw(pdfName), preview_url:`https://github.com/${repository}/blob/${ref}/textbooks/slc/${pdfName}`, name:pdfName, bytes:pdfBytes.length, sha256:pdf.sha256, pages:pdf.pages},
    engine, olp_commit:olp.commit, slc_commit:sources.slc.commit,
    source_zip:await optional('zip',manifest.source_zip), single_file_latex:await optional('tex',manifest.cumulative_tex),
    epub:await optional('epub',manifest.epub), html:await optional('html',manifest.html),
    manifest:{url:raw('MANIFEST.json'),sha256:hash(manifestBytes)},
    authors:['Richard Zach','Open Logic Project contributors'],
    translation:manifest.translation,
    rights:{text:'CC BY 4.0',portraits:'Matthew Leadbeater, CC BY-NC 4.0',photographs:'Individual terms and credits in each source package',fonts:'Individual font licences in each source package'},
  };
}

function bookLinks(t, html=false) {
  const links = [['PDF', t.pdf], ['LaTeX', t.single_file_latex], ['ZIP',t.source_zip], ['EPUB',t.epub], ['HTML',t.html]].filter(([,asset])=>asset);
  return links.map(([label,asset])=>html ? `<a href="${escape(asset.url)}">${label}</a>` : `[${label}](${asset.url})`).join(' · ');
}

async function textbooks(check, {sources,base={},collect=false}={}) {
  sources??=await loadSources();
  const page=async name=>base[name]??await read(name);
  const selection=sources.textbookSelection;
  const records=[];
  for (const pilot of sources.textbooks) records.push(await textbook(pilot,selection[pilot.id]));
  const catalogue={schema:'openlogic.textbooks.v1',textbooks:records};
  const md='## Textbooks\n\n*Sets, Logic, Computation* by Richard Zach uses a selected sequence of Open Logic sections, with its own preface, chapter summaries and glossary. These AI-translated textbook editions follow the book’s chapter plan; the full source collections are listed separately.\n\n| Language | Textbook | Downloads | PDF pages |\n| --- | --- | --- | ---: |\n'+records.map(t=>`| ${t.language_name} · SLC | ${t.title} | ${bookLinks(t)} | ${t.pdf.pages} |`).join('\n')+'\n\nText: CC BY 4.0. Portraits: Matthew Leadbeater, CC BY-NC 4.0. Photographs and fonts retain their individual terms. The linked editions identify the models responsible for their AI translation; no human linguistic review is implied. [Edition and source details](catalogue/textbooks.json).';
  const files={'catalogue/textbooks.json':json(catalogue),'README.md':block(await page('README.md'),'textbooks',md,'## ')};
  for (const name of ['index.html','index.ps.html']) {
    const heading=name==='index.html'?'Textbooks · Sets, Logic, Computation':'Sets, Logic, Computation';
    const cards=records.map(t=>`<article lang="${t.language_tag}"><p class="eyebrow">${escape(t.language_name)}</p><h3>${escape(t.title)}</h3><p>${bookLinks(t,true)}</p><p>${t.pdf.pages} · PDF</p></article>`).join('\n');
    const section=`<section class="method" id="textbooks" aria-labelledby="textbooks-title"><h2 id="textbooks-title">${heading}</h2><div class="method-grid">${cards}</div></section>`;
    files[name]=block(await page(name),'textbooks',section,'    <section class="method" id="accessible-english"');
  }
  if(collect)return files;
  await output(files,check);
  console.log(`textbooks: ${records.length} records; committed files equal a fresh generation`);
}

export function selectRelease(edition, releases, {discovery='accepted-only'}={}) {
  if(!['accepted-only','latest'].includes(discovery))throw Error('Invalid release discovery policy');
  // A selected textbook is a separate product, not a replacement for 722-unit readers.
  const published=releases.filter(r=>!r.draft&&!r.prerelease&&!/^slc(?:-|$)/i.test(r.tag_name)).sort((a,b)=>Date.parse(b.published_at)-Date.parse(a.published_at));
  const tag=edition.release_tag || edition.release?.split('/releases/tag/')[1];
  const accepted=published.find(r=>r.tag_name===tag) || null;
  // These repositories hold several distinct works, readers, reviews or constructed languages.
  return {accepted,available:discovery==='accepted-only'?accepted:published[0]||null};
}

function releaseFact(release) {
  if (!release) return null;
  return {tag:release.tag_name,date:release.published_at,url:release.html_url,assets:release.assets.map(a=>({name:a.name,url:a.browser_download_url,bytes:a.size,sha256:a.digest?.startsWith('sha256:')?a.digest.slice(7):null})).sort((a,b)=>a.name.localeCompare(b.name,'en'))};
}

async function releases(check, {sources,base={},collect=false}={}) {
  sources??=await loadSources();
  const page=async name=>base[name]??await read(name);
  const catalogue=sources.catalogue;
  const policy=sources.policy;
  const facts=[];
  for (const edition of catalogue.editions) {
    if (!edition.repository?.startsWith('https://github.com/')) continue;
    const repository=new URL(edition.repository).pathname.split('/').filter(Boolean).slice(0,2).join('/');
    const list=await api(`repos/${repository}/releases?per_page=100`);
    const promotion=policy.promotions[edition.id];
    if (promotion) {
      const selected=list.find(r=>r.tag_name===promotion.tag&&!r.draft&&!r.prerelease);
      if (!selected) throw Error('Accepted release is absent: '+edition.id);
      edition.release_tag=selected.tag_name;edition.release=selected.html_url;
      const promotedAsset=spec=>{
        const asset=selected.assets.find(a=>a.name===spec.name);
        if (!asset || asset.digest!=='sha256:'+spec.sha256 || asset.size!==spec.bytes) throw Error('Accepted release asset changed: '+spec.name);
        return {...spec,url:asset.browser_download_url};
      };
      const current=promotion.assets.map(promotedAsset);
      for (const spec of promotion.supplementary_assets || []) {
        const replacement=promotedAsset(spec);
        for (const group of edition.supplementary_downloads || []) {
          group.downloads=group.downloads.map(asset=>asset.name===spec.name?replacement:asset);
        }
      }
      edition.ordered_downloads=current;
      edition.readers=current.filter(a=>['PDF','EPUB','HTML'].includes(a.format));
      edition.source_archive=current.find(a=>a.format==='ZIP');
      edition.direct_cumulative_source=current.find(a=>a.format==='TEX');
      edition.epub_reader_units=722;
      edition.status=edition.status.filter(s=>s!=='full-epub-pending');
      edition.epub_coverage_note=promotion.epub_coverage_note;
      if (promotion.remove_limitation) edition.limitations=edition.limitations.filter(t=>t!==promotion.remove_limitation);
      if (!/^evidence\/[A-Za-z0-9_-]+\.json$/.test(promotion.readback || '')) throw Error('Promotion requires its exact readback: '+edition.id);
      edition.evidence.current_format_readback=promotion.readback;
      if (promotion.profiles) edition.profiles=promotion.profiles;
      if (promotion.coverage_basis) edition.coverage_basis=promotion.coverage_basis;
      if (promotion.evidence) Object.assign(edition.evidence,promotion.evidence);
      if (promotion.historical_doi_label) edition.ui_labels.doi=promotion.historical_doi_label;
    }
    const selection=selectRelease(edition,list,{discovery:sources.witnesses.find(r=>r.id===edition.id).releaseDiscovery});
    if (edition.release && !selection.accepted) throw Error('Listed release missing from API: '+edition.id);
    edition.release_tag=selection.accepted?.tag_name||null;
    edition.release_date=selection.accepted?.published_at||null;
    edition.release_facts=releaseFact(selection.accepted);
    edition.available_release=releaseFact(selection.available);
    facts.push({id:edition.id,name:edition.name,language_tag:edition.language_tag,repository:edition.repository,listed:edition.release_facts,available:edition.available_release});
  }
  const selected=facts.filter(f=>f.available);
  const rows=selected.map(f=>`| ${f.name} | [${f.available.tag}](${f.available.url}) | ${f.available.date.slice(0,10)} |`).join('\n');
  const md='## Published releases\n\nThese links identify the published release for each work and language. The language catalogue retains the scope and limitations established for its listed readers; a newer publication does not itself establish wider coverage or linguistic review.\n\n| Edition | Published release | Date |\n| --- | --- | --- |\n'+rows+'\n\n[Download filenames, sizes and source-provided checksums](catalogue/releases.json).';
  let readme=fillTemplate(await read('templates/README.md'),{editions:editionTable(catalogue)});
  const oldTextbooks=(await page('README.md')).split('<!-- textbooks:begin -->')[1]?.split('<!-- textbooks:end -->')[0];
  if(oldTextbooks)readme=block(readme,'textbooks',oldTextbooks);
  const files={'catalogue/editions.json':json(catalogue),'catalogue/releases.json':json({schema:'openlogic.releases.v1',editions:facts}),'README.md':block(readme,'releases',md)};
  for (const name of ['index.html','index.ps.html']) {
    const heading=name==='index.html'?'Published releases':'GitHub';
    const cards=selected.map(f=>`<li lang="${escape(f.language_tag)}"><a href="${escape(f.available.url)}">${escape(f.name)}</a> · <time datetime="${f.available.date.slice(0,10)}">${f.available.date.slice(0,10)}</time></li>`).join('\n');
    const section=`<section class="method" id="published-releases"><details><summary>${heading}</summary><ul>${cards}</ul></details></section>`;
    files[name]=block(await page(name),'releases',section,'  </main>');
  }
  if(collect)return files;
  await output(files,check);
  console.log('releases: 0 entries differ from the GitHub Releases API');
}

async function urls() {
  const urls=new Set();
  for (const name of ['README.md','index.html','index.ps.html']) {
    const content=await read(name);
    for (const type of ['textbooks','releases']) {
      const section=content.split(`<!-- ${type}:begin -->`)[1]?.split(`<!-- ${type}:end -->`)[0];
      if (!section) throw Error('Missing generated block: '+name+' '+type);
      for (const m of section.matchAll(/https:\/\/[^\s"<>\)]+/g)) urls.add(m[0].replaceAll('&amp;','&'));
    }
  }
  for (const url of urls) {
    const response=await fetch(url,{method:'HEAD',signal:AbortSignal.timeout(60000)});
    if (response.status!==200) throw Error('URL '+response.status+': '+url);
  }
  console.log(`urls: ${urls.size} of ${urls.size} answer 200`);
}

export async function main(args=process.argv.slice(2)) {
  const [command,...options]=args;
  if (options.some(x=>x!=='--check')) throw Error('Only --check is supported');
  if(command==='all') {
    const sources=await loadSources();
    const base={'README.md':fillTemplate(await read('templates/README.md'),{editions:editionTable(sources.catalogue)})};
    for(const name of ['index.html','index.ps.html'])base[name]=await read('templates/'+name);
    const generated=await releases(false,{sources,base,collect:true});
    Object.assign(generated,await textbooks(false,{sources,base:{...base,...generated},collect:true}));
    generated['catalogue/release-selection.json']=json(sources.policy);
    generated['catalogue/textbook-selection.json']=json(sources.textbookSelection);
    generated['catalogue/ownership.json']=json(editionRouting(sources.catalogue));
    const changed=await output(generated,options.includes('--check'));
    console.log(`all: ${sources.registry.editions.length} entries; ${Object.keys(generated).length} generated files; ${changed.length} changed`);
    const pending=sources.migrations.filter(m=>m.kind==='incomplete');
    if(pending.length)console.log(`migration incomplete: ${pending.length} edition contracts; accepted legacy records retained`);
  }
  else if(command==='textbooks')await textbooks(options.includes('--check'));
  else if(command==='releases')await releases(options.includes('--check'));
  else if(command==='urls')await urls();
  else if(command==='migration') {
    const result=await loadSources();
    const rows=result.migrations.map(({id,kind,commit,reason,missing,contract_sha256,catalogue_sha256})=>({id,kind,commit,reason,missing,contract_sha256,catalogue_sha256}));
    console.log(json({schema:'openlogic.metadata-migration.v1',editions:rows}));
    if(options.includes('--check') && rows.some(row=>row.kind==='incomplete'))throw Error('Edition metadata migration is incomplete');
  }
  else if(command==='inputs') {
    const sources=await loadSources();
    await output({'catalogue/release-selection.json':json(sources.policy),'catalogue/textbook-selection.json':json(sources.textbookSelection)},options.includes('--check'));
    console.log(`inputs: ${sources.registry.editions.length} edition records; source partition verified`);
  }
  else throw Error('Use all, migration, inputs, textbooks, releases or urls, optionally with --check');
}
if (process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  main().catch(error=>{console.error(error.message);process.exitCode=1;});
}
