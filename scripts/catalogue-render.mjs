const text = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])).replaceAll('|','&#124;').replace(/\r?\n/g,' ');
const link = (label,url) => {
  if(!/^https:\/\//.test(url||'') && !/^(?!\/)(?!.*(?:^|\/)\.\.(?:\/|$))[\w./#?%=&+-]+$/.test(url||''))throw Error('Expected a public HTTPS link or safe relative page');
  return `[${text(label)}](${url.replaceAll('(','%28').replaceAll(')','%29')})`;
};
const count = n => Number.isSafeInteger(n) && n>=0 ? String(n) : '—';

export function editionTable(catalogue) {
  const rows=catalogue.editions.map(e=>{
    const assets=e.ordered_downloads?.length ? e.ordered_downloads : [...(e.readers||[]),e.direct_cumulative_source,e.source_archive].filter(Boolean);
    const seen=new Set();const downloads=[];
    for(const a of assets) {
      if(!a.url || seen.has(a.url) || a.scope_kind==='sample')continue;
      seen.add(a.url);downloads.push(link(a.download_label||a.profile||a.format||a.name||'Reader',a.url));
    }
    const resources=[];
    if(e.release)resources.push(link('GitHub',e.release));
    else if(e.repository)resources.push(link(e.ui_labels?.repository||'GitHub',e.repository));
    if(e.public_source_checkpoint_commit)resources.push(link('Source',`${e.repository}/tree/${e.public_source_checkpoint_commit}`));
    for(const item of e.related_editions||[])if(item.url)resources.push(link(item.label||item.name||item.title||'↗',item.url));
    if(e.version_doi)resources.push(link(e.ui_labels?.doi||'DOI',`https://doi.org/${e.version_doi}`));
    const scope=`${count(e.source_units_translated)} | ${count(e.standalone_reader_units)} | ${count(e.epub_reader_units)}`;
    return `| ${text(e.name)} | ${scope} | ${downloads.join(' · ')||'—'} | ${resources.join(' · ')||'—'} |`;
  });
  return '## Read or inspect an edition\n\nCounts refer to tracked source files. Source coverage, standalone-reader coverage and EPUB coverage are separate. A dash means that the catalogue does not establish a count; it does not mean zero. Coverage does not establish linguistic review. See the [language cards](https://kokunoyumeto.github.io/OpenLogic-translations/#languages) for each edition’s scope, variants and limitations.\n\n| Edition | Source files | Reader files | EPUB files | Readers and editable sources | Edition details |\n| --- | ---: | ---: | ---: | --- | --- |\n'+rows.join('\n');
}

export function fillTemplate(template, values) {
  const used=new Set();
  const result=template.replace(/\{\{([a-z_]+)\}\}/g,(_,key)=>{
    if(!Object.hasOwn(values,key))throw Error('Unknown template slot: '+key);
    used.add(key);return values[key];
  });
  for(const key of Object.keys(values))if(!used.has(key))throw Error('Missing template slot: '+key);
  return result;
}

// Retain the public routing endpoint, deriving its facts from the same edition
// records as the reader cards rather than from historical commissioning notes.
export function editionRouting(catalogue) {
  return {schema:'openlogic.edition-routing.v2',editions:catalogue.editions.map(e=>{
    const keys=['id','name','language_tag','metadata_language','repository','release','release_tag','version_doi','concept_doi','source_units_translated','standalone_reader_units','epub_reader_units','total_source_units','profiles','status','limitations','evidence'];
    return Object.fromEntries(keys.filter(k=>Object.hasOwn(e,k)).map(k=>[k,structuredClone(e[k])]));
  })};
}
