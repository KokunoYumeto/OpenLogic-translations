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

check(script.includes('fetch("catalogue/editions.json"'), "site must read the canonical catalogue");
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
