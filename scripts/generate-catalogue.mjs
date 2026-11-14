import { readFile, writeFile, mkdtemp, unlink, rmdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { resolve, join } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';

const root = resolve(fileURLToPath(new URL('..', import.meta.url)));
const exec = promisify(execFile);
const json = x => JSON.stringify(x, null, 2) + '\n';
const read = name => readFile(resolve(root, name), 'utf8');
const parse = text => JSON.parse(text.replace(/^\uFEFF/, ''));
const hash = data => createHash('sha256').update(data).digest('hex');
const escape = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const requestCache = new Map();

async function api(path) {
  if (!/^repos\/[\w.-]+\/[\w.-]+\//.test(path)) throw Error('Unsupported GitHub API path');
  if (!requestCache.has(path)) requestCache.set(path, (async () => {
    // gh reads its credential store; neither credentials nor response headers are printed.
    try { return parse((await exec('gh', ['api', path], { maxBuffer: 32 * 1024 * 1024 })).stdout); }
    catch {
      const response = await fetch('https://api.github.com/' + path, { signal: AbortSignal.timeout(60000) });
      if (!response.ok) throw Error(`GitHub API ${response.status}: ${path}`);
      return response.json();
    }
  })());
  return requestCache.get(path);
}

async function bytes(url) {
  const response = await fetch(url, { signal: AbortSignal.timeout(60000) });
  if (!response.ok) throw Error(`Download ${response.status}: ${url}`);
  return Buffer.from(await response.arrayBuffer());
}

function block(text, name, content, before) {
  const begin = `<!-- ${name}:begin -->`, end = `<!-- ${name}:end -->`;
  const generated = `${begin}\n${content.trim()}\n${end}`;
  if (text.includes(begin) !== text.includes(end)) throw Error(`Unpaired ${name} markers`);
  if (text.includes(begin)) return text.slice(0, text.indexOf(begin)) + generated + text.slice(text.indexOf(end) + end.length);
  if (before && text.includes(before)) return text.replace(before, generated + '\n\n' + before);
  return text.trimEnd() + '\n\n' + generated + '\n';
}

async function output(files, check) {
  const changed = [];
  for (const [name, content] of Object.entries(files)) {
    const old = await read(name).catch(error => { if (error.code === 'ENOENT') return null; throw error; });
    if (old !== content) {
      changed.push(name);
      if (!check) await writeFile(resolve(root, name), content, 'utf8');
    }
  }
  if (check && changed.length) throw Error('Generated files differ: ' + changed.join(', '));
  return changed;
}

const pilots = [
  { id:'bn', tag:'bn-Beng-IN', name:'বাংলা', repo:'OpenLogic-bn-Beng-IN' },
  { id:'gu', tag:'gu-Gujr-IN', name:'ગુજરાતી', repo:'OpenLogic-gu-Gujr-IN' },
  { id:'jv', tag:'jv-Latn-ID', name:'Basa Jawa', repo:'OpenLogic-jv-Latn-ID' },
  { id:'mr', tag:'mr-Deva-IN', name:'मराठी', repo:'OpenLogic-mr-Deva-IN' },
];

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
  const repository='KokunoYumeto/'+pilot.repo;
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
    language_tag:pilot.tag,language_name:pilot.name,repository:`https://github.com/${repository}`,
    branch:null,ref:selection.ref,path:selection.path,state:'published',release:release.html_url,release_tag:release.tag_name,
    ...assets,engine,olp_commit:(manifest.sources.open_logic||manifest.sources.olp).commit,slc_commit:manifest.sources.slc.commit,
    epub:null,html:null,manifest:{url:raw('MANIFEST.json'),sha256:hash(manifestBytes)},
    edition_metadata:{url:`https://raw.githubusercontent.com/${repository}/${selection.ref}/olp-edition.toml`,sha256:hash(editionBytes)},
    authors:['Richard Zach','Open Logic Project contributors'],translation:manifest.translation,
    rights:{text:'CC BY 4.0',portraits:'Matthew Leadbeater, CC BY-NC 4.0',photographs:'Individual terms and credits in each source package',fonts:'Individual font licences in each source package'}};
}

async function textbook(pilot, selection) {
  if(selection)return publishedTextbook(pilot,selection);
  const repository = 'KokunoYumeto/' + pilot.repo;
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
    language_tag:pilot.tag, language_name:pilot.name, repository:`https://github.com/${repository}`,
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

async function textbooks(check) {
  const selection=parse(await read('catalogue/textbook-selection.json'));
  const records=[];
  for (const pilot of pilots) records.push(await textbook(pilot,selection[pilot.id]));
  const catalogue={schema:'openlogic.textbooks.v1',textbooks:records};
  const md='## Textbooks\n\n*Sets, Logic, Computation* by Richard Zach uses a selected sequence of Open Logic sections, with its own preface, chapter summaries and glossary. These AI-translated textbook editions follow the book’s chapter plan; the full source collections are listed separately.\n\n| Language | Textbook | Downloads | PDF pages |\n| --- | --- | --- | ---: |\n'+records.map(t=>`| ${t.language_name} · SLC | ${t.title} | ${bookLinks(t)} | ${t.pdf.pages} |`).join('\n')+'\n\nText: CC BY 4.0. Portraits: Matthew Leadbeater, CC BY-NC 4.0. Photographs and fonts retain their individual terms. The linked editions identify the models responsible for their AI translation; no human linguistic review is implied. [Edition and source details](catalogue/textbooks.json).';
  const files={'catalogue/textbooks.json':json(catalogue),'README.md':block(await read('README.md'),'textbooks',md,'## ')};
  for (const name of ['index.html','index.ps.html']) {
    const heading=name==='index.html'?'Textbooks · Sets, Logic, Computation':'Sets, Logic, Computation';
    const cards=records.map(t=>`<article lang="${t.language_tag}"><p class="eyebrow">${escape(t.language_name)}</p><h3>${escape(t.title)}</h3><p>${bookLinks(t,true)}</p><p>${t.pdf.pages} · PDF</p></article>`).join('\n');
    const section=`<section class="method" id="textbooks" aria-labelledby="textbooks-title"><h2 id="textbooks-title">${heading}</h2><div class="method-grid">${cards}</div></section>`;
    files[name]=block(await read(name),'textbooks',section,'    <section class="method" id="accessible-english"');
  }
  await output(files,check);
  console.log(`textbooks: ${records.length} records; committed files equal a fresh generation`);
}

export function selectRelease(edition, releases) {
  // A selected textbook is a separate product, not a replacement for 722-unit readers.
  const published=releases.filter(r=>!r.draft&&!r.prerelease&&!/^slc(?:-|$)/i.test(r.tag_name)).sort((a,b)=>Date.parse(b.published_at)-Date.parse(a.published_at));
  const tag=edition.release_tag || edition.release?.split('/releases/tag/')[1];
  const accepted=published.find(r=>r.tag_name===tag) || null;
  // These repositories hold several distinct works, readers, reviews or constructed languages.
  const fixed=new Set(['openlogic-en-frozen-722','openlogic-ar','openlogic-fa-ir','openlogic-tr','openlogic-interfarsi','openlogic-romance-interlanguage','openlogic-isv']);
  return {accepted,available:fixed.has(edition.id)?accepted:published[0]||null};
}

function releaseFact(release) {
  if (!release) return null;
  return {tag:release.tag_name,date:release.published_at,url:release.html_url,assets:release.assets.map(a=>({name:a.name,url:a.browser_download_url,bytes:a.size,sha256:a.digest?.startsWith('sha256:')?a.digest.slice(7):null})).sort((a,b)=>a.name.localeCompare(b.name,'en'))};
}

async function releases(check) {
  const catalogue=parse(await read('catalogue/editions.json'));
  const policy=parse(await read('catalogue/release-selection.json'));
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
    const selection=selectRelease(edition,list);
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
  let readme=await read('README.md');
  for (const edition of catalogue.editions.filter(e=>policy.promotions[e.id])) {
    const promotion=policy.promotions[edition.id];
    const links=edition.ordered_downloads.map(a=>`[${a.download_label}](${a.url})`).join(' · ');
    const row=`| ${edition.name} | ${links} | ${promotion.readme_note} |`;
    readme=readme.split('\n').map(line=>line.startsWith(`| ${edition.name} |`) && !/^\| .* \| \[.*\]\(.*\) \| \d{4}-\d\d-\d\d \|$/.test(line)?row:line).join('\n');
  }
  const files={'catalogue/editions.json':json(catalogue),'catalogue/releases.json':json({schema:'openlogic.releases.v1',editions:facts}),'README.md':block(readme,'releases',md)};
  for (const name of ['index.html','index.ps.html']) {
    const heading=name==='index.html'?'Published releases':'GitHub';
    const cards=selected.map(f=>`<li lang="${escape(f.language_tag)}"><a href="${escape(f.available.url)}">${escape(f.name)}</a> · <time datetime="${f.available.date.slice(0,10)}">${f.available.date.slice(0,10)}</time></li>`).join('\n');
    const section=`<section class="method" id="published-releases"><details><summary>${heading}</summary><ul>${cards}</ul></details></section>`;
    files[name]=block(await read(name),'releases',section,'  </main>');
  }
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
  if(command==='textbooks')await textbooks(options.includes('--check'));
  else if(command==='releases')await releases(options.includes('--check'));
  else if(command==='urls')await urls();
  else throw Error('Use textbooks, releases or urls, optionally with --check');
}
if (process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  main().catch(error=>{console.error(error.message);process.exitCode=1;});
}
