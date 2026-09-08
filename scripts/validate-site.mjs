import { readFile, stat } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const failures = [];
const check = (condition, message) => { if (!condition) failures.push(message); };
const read = path => readFile(resolve(root, path), "utf8");

const [html, css, script, rawCatalogue, hosting] = await Promise.all([
  read("index.html"),
  read("site.css"),
  read("site.js"),
  read("catalogue/editions.json"),
  read(".openai/hosting.json")
]);
const catalogue = JSON.parse(rawCatalogue);
const hostingConfig = JSON.parse(hosting);

check(Array.isArray(catalogue.editions), "catalogue.editions must be an array");
check(catalogue.editions.length >= 20, "expected at least 20 edition records");
check(new Set(catalogue.editions.map(item => item.id)).size === catalogue.editions.length, "edition IDs must be unique");
check(catalogue.editions.every(item => item.id && item.name && item.language_tag), "every edition needs id, name, and language tag");
const french = catalogue.editions.find(item => item.id === "openlogic-fr");
check(french?.language_tag === "fr", "French catalogue entry missing");
if (french?.release_tag === "v0.1.0-ensembles") {
  check(french.source_units_translated === 7 && french.standalone_reader_units === 7, "French v0.1.0 contains exactly 7/722 units");
  check(french.status?.includes("partial") && french.readers?.[0]?.pages === 11, "French v0.1.0 is an 11-page partial edition, not a complete reader");
}
if (french?.release_tag === "v0.2.0-ensembles-relations") {
  check(french.source_units_translated === 16 && french.standalone_reader_units === 16, "French v0.2.0 contains exactly 16/722 units");
  check(french.status?.includes("partial") && french.readers?.[0]?.pages === 22, "French v0.2.0 is a 22-page partial edition");
  check(french.evidence?.documented_editorial_choices === 50, "French v0.2.0 bundles 50 editorial choices, not the later private audit");
}
check(script.includes('"fr": "Français"'), "French native-language selector label missing");
if (french?.release_tag === "v0.3.0-ensembles-relations-fonctions") {
  check(french.source_units_translated === 23 && french.standalone_reader_units === 23, "French v0.3.0 contains exactly 23/722 released units");
  check(french.status?.includes("partial") && french.readers?.[0]?.pages === 31, "French v0.3.0 is a 31-page partial edition");
  check(french.evidence?.documented_editorial_choices === 249, "French v0.3.0 bundles 249 editorial choices");
  check(french.readers?.[0]?.sha256 === "b4dd8366ea46b69e7e05183bfba40c968609a799ba7e992eeee8247e814602f7", "French v0.3.0 reader identity mismatch");
  check(french.limitations?.some(text => text.includes("uniqueness")), "French inherited cross-reference finding must remain disclosed");
}
for (const [id, pages] of [["openlogic-es", 992], ["openlogic-pt-br", 972]]) {
  const edition = catalogue.editions.find(item => item.id === id);
  check(edition?.source_units_translated === 722, `${id}: target-tree count must be 722`);
  check(edition?.current_local_configured_reader?.pages === pages, `${id}: wrong local configured PDF identity`);
  check(edition?.current_local_configured_reader?.source_units_rendered === 642 && edition.current_local_configured_reader.alternate_units_outside_reader === 80, `${id}: preserve configured 642+80 distinction`);
  check(edition?.current_local_configured_reader?.integrates_all_722_units === false && edition.standalone_reader_units !== 722, `${id}: configured reader must not become an integrated 722 reader`);
}
const romance = catalogue.editions.find(item => item.id === "openlogic-romance-interlanguage");
check(romance?.canon_admitted_units === 53 && romance.canon_pending_units === 669, "Romance admission snapshot must remain 53+669");
check(romance?.canon_admission_snapshot?.event_id === "RSC-EVT-000388", "Romance counts need their exact admission snapshot");
check(script.includes("Configured reader (local)") && script.includes("Canon-admitted units"), "Reader and canon-admission distinctions must be visible");
check(catalogue.editions.every(item => !item.repository || /^https:\/\//.test(item.repository)), "repository links must use HTTPS");
check(catalogue.editions.every(item => !item.release || /^https:\/\//.test(item.release)), "release links must use HTTPS");
check(catalogue.editions.every(item => item.source_units_translated == null || (item.source_units_translated >= 0 && item.source_units_translated <= 722)), "source counts must stay within 0..722");
check(catalogue.editions.every(item => item.source_units_preserved == null || (item.source_units_preserved >= 0 && item.source_units_preserved <= 722)), "preserved-source counts must stay within 0..722");
check(catalogue.editions.every(item => item.standalone_reader_units == null || (item.standalone_reader_units >= 0 && item.standalone_reader_units <= 722)), "reader counts must stay within 0..722");

for (const needle of [
  '<select id="language-select"',
  'id="edition-grid"',
  'id="search"',
  'data-filter="complete"',
  'href="https://kokunoyumeto.github.io/program-matematika-indonesia/"',
  'href="https://openlogicproject.org/"',
  '<noscript>'
]) check(html.includes(needle), `missing HTML requirement: ${needle}`);

check(script.includes('new URL("catalogue/editions.json"'), "site must read the canonical catalogue");
check(script.includes('cache: "no-store"'), "catalogue reads must bypass stale browser caches");
check(script.includes('window.addEventListener("focus"'), "a returning tab must refresh the catalogue");
check(script.includes("textContent"), "rendering must use textContent for catalogue values");
check(!script.includes("innerHTML"), "catalogue renderer must not inject innerHTML");
check(css.includes(":focus-visible"), "focus-visible styling is required");
check(css.includes("prefers-reduced-motion"), "reduced-motion support is required");
check(hostingConfig.static?.directory === "dist", "Sites static directory must be dist");
check(/^appgprj_/.test(hostingConfig.project_id || ""), "Sites project_id is missing");

const combined = `${html}\n${css}\n${script}\n${rawCatalogue}`;
check(!/[A-Za-z]:[\\/]Users[\\/]/i.test(combined), "public source contains a user-home path");
check(!/\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}/.test(combined), "public source contains a credential-shaped token");
check(!/TODO|PLACEHOLDER_CONTENT|lorem ipsum/i.test(`${html}\n${script}`), "site contains unfinished placeholder text");

for (const path of ["index.html", "site.css", "site.js", "catalogue/editions.json"]) {
  const info = await stat(resolve(root, path));
  check(info.size > 0, `${path} is empty`);
}

const result = {
  status: failures.length ? "FAIL" : "PASS",
  failures,
  editions: catalogue.editions.length,
  standalone_722_readers: catalogue.editions.filter(item => item.standalone_reader_units === 722).length,
  source_722_editions: catalogue.editions.filter(item => item.source_units_translated === 722).length
};
console.log(JSON.stringify(result));
if (failures.length) process.exit(1);
