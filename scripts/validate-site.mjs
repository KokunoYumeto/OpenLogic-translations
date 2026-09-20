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
const accessible = catalogue.infrastructure.find(item => item.id === "openlogic-accessible-book");
check(accessible?.language_tag === "en" && accessible.readers.some(item => item.format === "EPUB"), "accessible English needs a selectable language label and explicit EPUB download");
check(accessible.name === "English — accessible / compatibility edition", "compatibility must be explicit in the edition name");
check(catalogue.editions.find(item => item.id === "openlogic-en-frozen-722")?.related_editions?.some(item => item.url === "#openlogic-accessible-book"), "English preservation card must point directly to the compatibility edition");
for (const [id, count] of [["openlogic-fa-ir", 2], ["openlogic-interfarsi", 4]]) {
  const samples = catalogue.editions.find(item => item.id === id)?.readers?.filter(item => item.format === "EPUB") || [];
  check(samples.length === count && samples.every(item => item.scope_kind === "sample" && item.source_units === 1 && item.source_unit_ids?.[0] === "OLP-0005"), `${id}: sample EPUBs must not be presented as complete readers`);
}
check(script.includes("[...accessible, ...data.editions]"), "accessible editions must be first-class selector/card entries");
check(html.includes('href="#openlogic-accessible-book"') && html.includes('class="featured-reader"'), "accessible edition needs prominent top navigation and reading links");
check(script.includes('"Download EPUB"'), "EPUB downloads must be exposed on edition cards");
if (accessible.currentness_checked?.speech_repair_successor_published === true) {
  const delivery = JSON.parse(await read(accessible.evidence.public_readback));
  check(delivery.status === "PASS_PUBLIC_DELIVERY" && delivery.github_downloads.files.length === 9, "published repair claim needs its verified public delivery receipt");
  check(delivery.html.commit === accessible.currentness_checked.html_commit, "online repair claim must match its published reader commit");
  for (const format of accessible.readers.filter(item => item.format === "EPUB" || /\.zip(?:\?|$)/.test(item.url))) {
    check(delivery.github_downloads.files.some(file => file.url === format.url && file.bytes === format.bytes && file.sha256 === format.sha256 && file.matches), "each download must match its public byte receipt");
  }
} else check(accessible.currentness_checked?.speech_repair_successor_published === false, "repair publication status must be explicit");
check(catalogue.editions.every(item => item.id && item.name && item.language_tag), "every edition needs id, name, and language tag");
const french = catalogue.editions.find(item => item.id === "openlogic-fr");
const punjabi = catalogue.editions.find(item => item.id === "openlogic-pnb-arab-pk");
if (punjabi?.release_tag === "v0.2.0") {
  check(punjabi.standalone_reader_units === 7 && punjabi.source_units_translated === 26, "Punjabi reader7/source26 scope must remain distinct");
  check(punjabi.ordered_downloads?.[0]?.format === "PDF" && punjabi.ordered_downloads?.[1]?.format === "TEX" && punjabi.ordered_downloads?.[2]?.format === "ZIP", "Punjabi needs PDF, direct cumulative LaTeX, then full source ZIP");
  check(punjabi.ordered_downloads?.[2]?.sha256 === "64bec0f191b943279e6bfa728c65104c11b871911afa79e941c6a92d92de6a9f", "Punjabi must link the corrected cumulative-source ZIP");
  check(punjabi.readers?.some(item => item.format === "EPUB" && item.source_units === 7 && item.sha256 === "fd8a878c1d6159cd5917444449a6fb56c7551f61719182d010448ad6893fa0ba"), "Punjabi needs its verified seven-unit EPUB");
  const intake = JSON.parse(await read(punjabi.evidence.public_readback));
  const punjabiFiles = intake.files.filter(file => file.lane === "pnb-Arab-PK");
  check(punjabiFiles.length === 13 && punjabiFiles.every(file => file.matches), "Punjabi intake needs eleven Zenodo files and two GitHub masters verified");
  for (const item of punjabi.ordered_downloads) check(intake.files.some(file => file.url === item.url && file.sha256 === item.sha256 && file.bytes === item.bytes), "Punjabi download not in public receipt");
  check(script.includes("orderedDownloads.forEach"), "Renderer must preserve edition download order");
}
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
check(romance?.canon_admitted_units === 55 && romance.canon_pending_units === 667, "Romance admission snapshot must remain 55+667");
check(romance?.canon_admission_snapshot?.event_id === "RSC-EVT-000486", "Romance counts need their exact admission snapshot");
check(romance?.current_local_configured_reader?.source_units_rendered === 722 && romance.current_local_configured_reader.public === false && romance.standalone_reader_units !== 722, "Romance local provisional reader must not be promoted to a public/canon-complete reader");
const romanceIntake = JSON.parse(await read(romance.evidence.local_reader_intake));
check(romanceIntake.checks.length === 15 && romanceIntake.checks.every(item => item.pass) && romanceIntake.deterministic_failures.length === 0, "Romance local reader needs its replayed identity/coverage checks");
check(romanceIntake.structural_coverage.loaded_targets === 722 && romanceIntake.translation_ledger_states.SOURCE_CRITICAL_COMPLETE === 55, "Romance loaded targets and admitted ledger rows must remain separate");
check(romance.current_local_configured_reader.sha256 === romanceIntake.reader.sha256.toLowerCase() && romance.current_local_configured_reader.bytes === romanceIntake.reader.bytes, "Romance catalogue must match current R2 bytes");
check(romance.local_reader_label === "Provisional standalone reader (local)" && script.includes("edition.local_reader_label"), "Romance local standalone-reader status must be visible");
const frGuDelivery = JSON.parse(await read("evidence/FRENCH_GUJARATI_PUBLIC_DELIVERY_20260919.json"));
const frGuSources = JSON.parse(await read("evidence/FRENCH_GUJARATI_SOURCE_PACKAGE_CHECKS_20260919.json"));
const guFulltextDelivery = JSON.parse(await read("evidence/GUJARATI_FULLTEXT_PUBLIC_READBACK_20260919.json"));
const guFulltextChecks = JSON.parse(await read("evidence/GUJARATI_FULLTEXT_SOURCE_CHECKS_20260919.json"));
const guModelsDelivery = JSON.parse(await read("evidence/GUJARATI_MODELS_THEORIES_PUBLIC_READBACK_20260920.json"));
const guModelsChecks = JSON.parse(await read("evidence/GUJARATI_MODELS_THEORIES_PACKAGE_CHECKS_20260920.json"));
const guBeyondDelivery = JSON.parse(await read("evidence/GUJARATI_BEYOND_PUBLIC_READBACK_20260920.json"));
const guBeyondChecks = JSON.parse(await read("evidence/GUJARATI_BEYOND_PACKAGE_CHECKS_20260920.json"));
const guBeyondSample = JSON.parse(await read("evidence/GUJARATI_BEYOND_CANON_SOURCE_SAMPLE_20260920.json"));
const french74 = JSON.parse(await read("evidence/FRENCH_READER74_MANAGER_INTAKE_20260920.json"));
check(french74.files.length === 8 && french74.files.every(file => file.matches), "French74 needs all eight anonymous mirror matches");
check(french74.source_package.static_assembly_matches_direct_tex && french74.source_package.complete_embedded_body_count === 74 && french74.source_package.external_body_imports === 0, "French74 needs complete matching cumulative source");
check(french74.source_package.frozen_english_files_matched === 722 && french74.qa.failures === 0, "French74 needs frozen source and structural checks");
check(french.source_units_translated === 80 && french.reader_excluded_drafts.length === 6, "French source drafts must remain distinct from loaded reader units");
check(frGuDelivery.files.length === 22 && frGuDelivery.files.every(file => file.matches), "French/Gujarati need all22 anonymous release-file checks");
for (const [id, units] of [["openlogic-fr",74],["openlogic-gu-gujr-in",178]]) {
  const edition = catalogue.editions.find(item => item.id === id);
  check(edition.source_units_translated === (id === "openlogic-fr" ? 80 : units) && edition.standalone_reader_units === units, `${id}: source/reader scopes must match the verified package`);
  check(edition.ordered_downloads.slice(0,3).map(item => item.format).join(",") === "PDF,TEX,ZIP", `${id}: retain PDF/TeX/source-ZIP link order`);
  check(edition.readers.some(item => item.format === "EPUB" && item.source_units === units), `${id}: scoped EPUB missing`);
  const delivery = id === "openlogic-gu-gujr-in" ? guBeyondDelivery : french74;
  for (const item of edition.ordered_downloads) check(delivery.files.some(file => file.url === item.url && file.sha256 === item.sha256 && file.bytes === item.bytes && file.matches), `${id}: download lacks matching byte evidence`);
}
check(frGuSources.french.direct_tex_unique_embedded_sources === 51 && frGuSources.french.external_content_imports === 0, "French cumulative LaTeX must contain the51-unit body");
check(french.direct_cumulative_source.sha256 === french.ordered_downloads[1].sha256, "French direct-source metadata must describe the current release");
const gujaratiCurrent = catalogue.editions.find(item => item.id === "openlogic-gu-gujr-in");
check(frGuSources.gujarati.native_content_files === 163 && frGuSources.gujarati.verified_exact_source_target_spans === 3630 && frGuSources.gujarati.ledger_binding_failures.length === 0, "Gujarati package needs163 sources and3630 exact source/target span checks");
check(guFulltextDelivery.files.length === 16 && guFulltextDelivery.files.every(file => file.matches), "Gujarati full-text repair needs all16 public file readbacks");
check(guFulltextChecks.full_text_reconstruction_byte_identical && guFulltextChecks.complete_direct_text_packaging_defect_closed && guFulltextChecks.unresolved_cumulative_body_imports.length === 0, "Gujarati full-text assembly must be verified");
check(guModelsDelivery.complete && guModelsDelivery.files.length === 16 && guModelsDelivery.files.every(file => file.matches), "Gujarati Models and Theories needs all16 public file matches");
check(guModelsChecks.failures.length === 0 && guModelsChecks.source.inventory_entries_verified === 1252 && guModelsChecks.source.frozen_english_sources === 722 && guModelsChecks.source.native_target_files === 170 && guModelsChecks.source.source_target_span_checks === 3738, "Gujarati current package needs complete inventory/source/target bindings");
check(guModelsChecks.source.complete_fulltext_reconstruction && guModelsChecks.source.unresolved_body_imports.length === 0, "Gujarati direct source must be the exact complete text, not the thin master");
check(guModelsChecks.epub.mathml_nodes === 9653 && guModelsChecks.epub.mathml_structures_match_html && guModelsChecks.epub.tex_annotations_exact === 9653 && guModelsChecks.epub.broken_internal_links.length === 0, "Gujarati EPUB math and links must match");
check(guBeyondDelivery.complete && guBeyondDelivery.files.length === 16 && guBeyondDelivery.files.every(file => file.matches), "Gujarati Beyond needs all16 public file matches");
check(guBeyondChecks.failures.length === 0 && guBeyondChecks.source.inventory_entries_verified === 1285 && guBeyondChecks.source.native_target_files === 178 && guBeyondChecks.source.frozen_english_sources === 722 && guBeyondChecks.source.source_target_span_checks === 3882, "Gujarati Beyond needs exact inventory and source-target bindings");
check(guBeyondChecks.source.complete_fulltext_reconstruction && guBeyondChecks.source.unresolved_body_imports.length === 0 && gujaratiCurrent.direct_latex.sha256 === guBeyondChecks.source.direct_fulltext_sha256 && gujaratiCurrent.direct_latex.role === "complete-cumulative-full-text", "Current Gujarati direct cumulative source must match reconstructed text");
check(guBeyondChecks.epub.mathml_nodes === 10000 && guBeyondChecks.epub.mathml_structures_match_html && guBeyondChecks.epub.tex_annotations_exact === 10000 && guBeyondChecks.epub.broken_internal_links.length === 0, "Gujarati Beyond EPUB mathematics and internal links must match");
check(guBeyondSample.checks.length === 48 && guBeyondSample.checks.every(item => item.pass) && guBeyondSample.segments.length === 7 && guBeyondSample.terminology_decision.status === "provisional_contextual", "Gujarati bounded canon/source sample must retain uncertainty");
check(gujaratiCurrent.build_master.role === "build-master-not-cumulative-full-text" && gujaratiCurrent.version_doi === "10.5281/zenodo.22851169" && gujaratiCurrent.readers[0].pages === 231, "Retain labelled build master, correct DOI and231-page current reader");
for (const [id, units, hasEpub] of [["openlogic-ta-taml-in",203,false],["openlogic-jv-latn-id",24,true]]) {
  const edition = catalogue.editions.find(item => item.id === id);
  check(edition.standalone_reader_units === units, `${id}: release reader scope mismatch`);
  check(edition.ordered_downloads.slice(0,3).map(item => item.format).join(",") === "PDF,TEX,ZIP", `${id}: PDF/direct-LaTeX/source-ZIP order required`);
  check(edition.readers.some(item => item.format === "EPUB") === hasEpub, `${id}: EPUB availability misrepresented`);
  const receipt = JSON.parse(await read("evidence/PUBLIC_READER_DELIVERIES_20260919.json"));
  for (const item of edition.ordered_downloads) check(receipt.files.some(file => file.url === item.url && file.sha256 === item.sha256 && file.bytes === item.bytes && file.matches), `${id}: public download not verified`);
}
const newDelivery = JSON.parse(await read("evidence/PASHTO_BENGALI_PUBLIC_DELIVERY_20260919.json"));
const sourceProgress = JSON.parse(await read("evidence/SOURCE_PROGRESS_TE270_MR163_20260919.json"));
check(sourceProgress.source_readbacks.length === 26 && sourceProgress.source_readbacks.every(file => file.match), "Telugu/Marathi source readbacks must all match");
for (const [id, sourceUnits, readerUnits] of [["openlogic-mr-deva-in",187,108]]) {
  const edition = catalogue.editions.find(item => item.id === id);
  check(edition.source_units_translated === sourceUnits && edition.standalone_reader_units === readerUnits, `${id}: cumulative sources must not inflate released reader coverage`);
  check(edition.source_progress.targets_verified === sourceUnits && edition.source_progress.failures === 0, `${id}: public target identity evidence required`);
}
const bengaliRepair = JSON.parse(await read("evidence/BENGALI_SOURCE_REPAIR_20260919.json"));
const telugu276 = catalogue.editions.find(item => item.id === "openlogic-te-telu-in");
const telugu276Evidence = JSON.parse(await read(telugu276.evidence.public_readback));
check(telugu276.source_units_translated === 276 && telugu276.standalone_reader_units === 276, "Telugu cumulative PDF/source coverage must be276");
check(telugu276.readers.find(item => item.format === "EPUB")?.source_units === 23, "Telugu PDF coverage must not inflate its23-unit EPUB");
check(telugu276Evidence.render_scope.reader_units === 276 && telugu276Evidence.render_scope.failures === 0 && telugu276Evidence.files.length === 8 && telugu276Evidence.all_public_assets_match, "Telugu276 requires render/hash evidence and all eight public assets");
check(telugu276Evidence.new_source_batch.missing_passage_mapping.length === 3 && telugu276.source_progress.canon_mapping_gaps === 3, "Keep Telugu canon-mapping gaps explicit");
check(telugu276.source_packaging_status === "incomplete-direct-cumulative-tex-missing" && !telugu276Evidence.source_packaging.direct_cumulative_tex_available, "Do not claim Telugu direct LaTeX before it exists");
for (const file of telugu276.ordered_downloads) check(telugu276Evidence.files.some(item => item.url === file.url && item.bytes === file.bytes && item.sha256 === file.sha256 && item.matches), "Telugu download must match anonymous readback");
const psSource = JSON.parse(await read("evidence/PASHTO_SOURCE247_MANAGER_READBACK_20260920.json"));
const psEdition = catalogue.editions.find(item => item.id === "openlogic-ps-arab-pk");
check(psSource.source_files_verified === 722 && psSource.target_files_verified === 247 && psSource.failures === 0 && psSource.new_batch_exact_block_checks === 376, "Pashto source checkpoint requires frozen-source, target and actual new-batch block checks");
check(psEdition.source_progress.archive_sha256 === psSource.archive.sha256 && psEdition.source_progress.commit === psSource.commit && psSource.reader_units === 82 && psSource.reader_files_changed === false, "Pashto source identity must not inflate or replace its reader");
for (const [id, sources, units] of [["openlogic-ps-arab-pk",247,82],["openlogic-bn-beng-in",299,299]]) {
  const edition = catalogue.editions.find(item => item.id === id);
  check(edition.source_units_translated === sources && edition.standalone_reader_units === units, `${id}: source and reader scope must stay distinct`);
  check(edition.readers.some(item => item.format === "EPUB" && item.source_units === units), `${id}: scoped EPUB missing`);
  for (const item of edition.ordered_downloads) check([...newDelivery.files,...bengaliRepair.files].some(file => file.url === item.url && file.sha256 === item.sha256 && file.bytes === item.bytes && file.matches), `${id}: public download not verified`);
  if (id === "openlogic-ps-arab-pk") check(edition.ordered_downloads.slice(0,3).map(item => item.format).join(",") === "PDF,TEX,ZIP", "Pashto needs PDF/direct cumulative LaTeX/source ZIP order");
  else {
    check(edition.source_packaging_status === "direct-cumulative-LaTeX-and-full-source-ZIP-verified" && edition.pertinent_pdf_exists === false && edition.online_reading_preview, "Bengali needs full cumulative source and its no-PDF online preview");
    check(edition.ordered_downloads.slice(0,2).map(item=>item.format).join(',') === "TEX,ZIP", "Bengali no-PDF source order must be direct LaTeX then ZIP");
    check(bengaliRepair.github_files_matched === 6 && bengaliRepair.static_source_inspection.unique_units === 299, "Bengali repair needs six verified GitHub files and299-unit source inspection");
  }
}
check(newDelivery.files.length === 30 && newDelivery.files.every(item => item.matches), "Pashto/Bengali intake must preserve the thirty matched readbacks");
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
check(css.includes(".edition-card[hidden] { display: none; }"), "card display must respect search/filter hidden state");
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
