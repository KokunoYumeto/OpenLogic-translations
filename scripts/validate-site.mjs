import { readFile, stat } from "node:fs/promises";
import { createHash } from "node:crypto";
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
  const samples = catalogue.editions.find(item => item.id === id)?.readers?.filter(item => item.format === "EPUB" && item.scope_kind === "sample") || [];
  check(samples.length === count && samples.every(item => item.scope_kind === "sample" && item.source_units === 1 && item.source_unit_ids?.[0] === "OLP-0005"), `${id}: sample EPUBs must not be presented as complete readers`);
}
check(script.includes("[...accessible, ...data.editions]"), "accessible editions must be first-class selector/card entries");
const persian = catalogue.editions.find(item => item.id === "openlogic-fa-ir");
const priorities = await read("PRIORITIES.md");
const persianPriority = priorities.split("\n").find(line => line.startsWith("1. **")) || "";
check(persianPriority.includes(persian.release) && persianPriority.includes(persian.version_doi) && persianPriority.includes("PERSIAN_R10_PUBLIC_MANAGER_AUDIT_20260929.json"), "Persian priority must link its current published reader and evidence");
check(persianPriority.includes("all 722 source units") && persianPriority.includes("۷۲۲") && persianPriority.includes("does not establish full linguistic or human review") && !persianPriority.includes("turn the current 642-unit"), "Persian priority must retain bilingual complete-reader status without overstating linguistic review");
check(persian.download_layout === "compact-grouped" && persian.download_summary.includes("هنوز ادامه دارد"), "Persian compact downloads must retain the localized review caveat");
check(persian.metadata_language === "fa-IR" && persian.metadata_direction === "rtl", "Persian metadata needs language and direction");
check(html.includes('site.js?v=20260930-interface-ps') && script.includes('edition.ui_labels?.complete_edition') && script.includes('edition.ui_labels?.script_samples'), "Localized navigation and current publication evidence must reach browsers with a fresh script URL");
check(persian.search_aliases?.includes("Persian") && persian.search_aliases?.includes("Farsi"), "Localized Persian must remain searchable by its English aliases");
check(persian.ui_labels?.script_samples?.includes("یک واحد") && persian.ui_labels?.publication_and_evidence, "Persian sample and metadata navigation must be localized");
const persianMirror = JSON.parse(await read(persian.evidence.mirror_public_readback)).public_readback;
check(persian.version_doi === persianMirror.version_doi && persianMirror.record_id === 23027811, "Persian version DOI needs exact R10 mirror evidence");
check(persianMirror.anonymous && persianMirror.all_assets_matched && persianMirror.files.length === 7 && persianMirror.files.every(f => f.github_matches && f.zenodo_matches && /^[0-9a-f]{64}$/.test(f.sha256)), "Persian R10 needs seven files verified anonymously on both mirrors");
check(script.includes('item.scope_kind === "sample"') && script.includes('"download-samples"') && script.includes('download.setAttribute("aria-label", fullLabel)'), "Compact downloads need separate samples and full accessible labels");
const persianAudit = JSON.parse(await read(persian.evidence.manager_public_readback));
const persianGuide = await read(persian.reader_guide);
check(persianGuide.includes('lang="fa-IR" dir="rtl"') && persianGuide.includes(persian.release) && persianGuide.includes(persian.evidence.manager_public_readback.split('/').pop()), "Persian reader guide must be localized and bind the current release and evidence");
check(persianAudit.package_checks.namespace_check.pass && persianAudit.package_checks.namespace_check.xhtml_documents === 777 && persianAudit.package_checks.namespace_check.mathml_roots === 42607, "Persian R10 EPUB needs actual MathML namespace evidence");
check(persian.release_tag === persianAudit.release_tag, "Persian release and evidence must agree");
check(persianAudit.public_readback.all_assets_matched && persianAudit.public_readback.files.length === 7, "Persian R10 release requires seven verified headline files");
check(persianAudit.package_checks.passed && persianAudit.package_checks.epub.distinct_units === 722 && persianAudit.package_checks.html.units === 722, "Persian EPUB and HTML need actual 722-unit structural evidence");
check(persian.ordered_downloads.slice(0,3).map(x => x.format).join(',') === 'PDF,TEX,ZIP', "Persian primary PDF needs its matching direct LaTeX and source ZIP");
const persianReflowable = persian.supplementary_downloads?.[0]?.downloads || [];
check(persianReflowable.map(x => x.format).join(',') === 'EPUB,TEX,ZIP,HTML', "Persian reflowable disclosure needs EPUB, matching direct LaTeX, source ZIP, HTML");
const persianCurrentDownloads = [...persian.ordered_downloads.filter(x => x.scope_kind !== 'sample'), ...persianReflowable];
check(persianCurrentDownloads.length === 7, "Persian R10 must expose exactly seven new headline downloads");
for (const download of persianCurrentDownloads) check(persianMirror.files.some(f => f.name === download.name && f.url === download.url && f.bytes === download.bytes && f.sha256 === download.sha256 && f.github_matches && f.zenodo_matches), "Persian R10 download must match both public mirrors");
check(persianAudit.package_checks.source_packages.length === 2 && persianAudit.package_checks.source_packages.every(p => p.crc_passed && p.direct_source_matches.length > 0), "Both Persian source ZIPs must contain their matching cumulative LaTeX");
const persianSampleAudit = JSON.parse(await read(persian.evidence.retained_sample_readback));
const persianSampleMirror = JSON.parse(await read(persian.evidence.retained_sample_mirror));
for (const download of persian.ordered_downloads.filter(x => x.scope_kind === 'sample')) {
  check(persianSampleAudit.public_readback.files.some(f => f.url === download.url && f.bytes === download.bytes && f.sha256 === download.sha256 && f.matches), "Retained Persian sample must retain its original GitHub proof");
  check(persianSampleMirror.files.some(f => f.github_name === download.name && f.bytes === download.bytes && f.sha256 === download.sha256 && f.matches), "Retained Persian sample must retain its original Zenodo proof");
}
check(persian.readers.some(x => x.format === 'EPUB' && x.scope_kind === 'complete' && x.source_units === 722), "Persian needs a separately labelled full EPUB");
check(persianAudit.full_linguistic_certification === false && persian.evidence.complete_linguistic_certification === false, "Persian structural coverage must not imply complete canon review");
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
const romanceReaderIntake = JSON.parse(await read("evidence/ROMANCE_READERS_722_LOCAL_INTAKE_20260920.json"));
const romancePublic = JSON.parse(await read("evidence/ROMANCE_READERS_PUBLIC_20260925.json"));
for (const [id, pages, bytes, sha256] of [
  ["openlogic-es", 1140, 6173137, "7c58463f0e74ebcbb2a17dfd8696a09aae56b29bc8502347a5bd1c2504ae3a46"],
  ["openlogic-pt-br", 1124, 6134799, "1ea7bb4707f6e348336354f2d3444ade6c6829643230db70f2e88d0ea599e534"]
]) {
  const edition = catalogue.editions.find(item => item.id === id);
  const intake = romanceReaderIntake.editions.find(item => item.id === id);
  check(edition?.source_units_translated === 722, `${id}: target-tree count must be 722`);
  check(edition?.standalone_reader_units === 722 && edition.retained_units_outside_reader === 0, `${id}: complete local reader must be listed as 722+0`);
  check(edition?.current_local_configured_reader?.complete_for_configuration === true && edition.current_local_configured_reader.source_units_rendered === 722 && edition.current_local_configured_reader.alternate_units_outside_reader === 0 && edition.current_local_configured_reader.integrates_all_722_units === true, `${id}: local reader must integrate all 722 translated units`);
  check(edition?.current_local_configured_reader?.pages === pages && edition.current_local_configured_reader.bytes === bytes && edition.current_local_configured_reader.sha256 === sha256, `${id}: wrong local complete-reader PDF identity`);
  check(edition?.current_local_reader_recorded_paths === 722 && edition.current_local_reader_missing_paths === 0, `${id}: reader recorder closure must be 722/722`);
  check(edition?.current_local_configured_reader?.public_release_sync_verified === true, `${id}: public722 delivery required`);
  const delivery = romancePublic.editions[id];
  check(delivery.github.complete && delivery.zenodo.complete && delivery.source_units === 722, `${id}: both mirrors verified`);
  check(edition.ordered_downloads.slice(0,3).map(x=>x.format).join(",") === "PDF,TEX,ZIP", `${id}: download order`);
  for (const asset of edition.ordered_downloads) check(delivery.github.public_readback.some(f=>f.url===asset.url && f.bytes===asset.bytes && f.sha256===asset.sha256 && f.matches), `${id}: unmatched download`);
  check(delivery.zenodo.anonymous_public_readback.some(f=>f.sha256===sha256 && f.bytes===bytes && f.matches), `${id}: Zenodo PDF identity`);
  check(delivery.direct_tex_target_files === 722 && edition.public_reader_verification.source_archive_complete, `${id}: complete editable sources required`);
  check(intake?.loaded_target_files === 722 && intake.unloaded_target_paths === 0 && intake.missing_target_files === 0 && intake.ledger_hash_mismatches === 0 && intake.locale_skipped_files === 0, `${id}: exact local closure evidence failed`);
  check(intake?.reader_pages === pages && intake.reader_bytes === bytes && intake.reader_sha256 === sha256 && intake.visual_result.startsWith("PASS"), `${id}: catalogue identity must match the visually checked intake`);
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
const gu199Delivery = JSON.parse(await read("evidence/GUJARATI199_PUBLIC_READBACK_20260921.json"));
const gu199Checks = JSON.parse(await read("evidence/GUJARATI199_SOURCE_PACKAGE_CHECKS_20260921.json"));
const gu270Delivery = JSON.parse(await read("evidence/GUJARATI270_PUBLIC_READBACK_20260927.json"));
const gu270Historical = JSON.parse(await read("evidence/GUJARATI_BEFORE_COMPLETE_20260930.json"));
const gu722 = JSON.parse(await read("evidence/GUJARATI722_MANAGER_INTAKE_20260930.json"));
const gu722Canon = JSON.parse(await read("evidence/GUJARATI722_CANON_SAMPLE_20260930.json"));
const gu270Checks = JSON.parse(await read("evidence/GUJARATI270_PACKAGE_CHECKS_20260927.json"));
const gu270Canon = JSON.parse(await read("evidence/GUJARATI270_CANON_SAMPLE_20260927.json"));
const french74 = JSON.parse(await read("evidence/FRENCH_READER74_MANAGER_INTAKE_20260920.json"));
check(french74.files.length === 8 && french74.files.every(file => file.matches), "French74 needs all eight anonymous mirror matches");
check(french74.source_package.static_assembly_matches_direct_tex && french74.source_package.complete_embedded_body_count === 74 && french74.source_package.external_body_imports === 0, "French74 needs complete matching cumulative source");
check(french74.source_package.frozen_english_files_matched === 722 && french74.qa.failures === 0, "French74 needs frozen source and structural checks");
check(french.source_units_translated === 80 && french.reader_excluded_drafts.length === 6, "French source drafts must remain distinct from loaded reader units");
check(frGuDelivery.files.length === 22 && frGuDelivery.files.every(file => file.matches), "French/Gujarati need all22 anonymous release-file checks");
for (const [id, units] of [["openlogic-fr",74],["openlogic-gu-gujr-in",270]]) {
  const edition = id === "openlogic-gu-gujr-in" ? gu270Historical : catalogue.editions.find(item => item.id === id);
  check(edition.source_units_translated === (id === "openlogic-fr" ? 80 : units) && edition.standalone_reader_units === units, `${id}: source/reader scopes must match the verified package`);
  check(edition.ordered_downloads.slice(0,3).map(item => item.format).join(",") === "PDF,TEX,ZIP", `${id}: retain PDF/TeX/source-ZIP link order`);
  check(edition.readers.some(item => item.format === "EPUB" && item.source_units === units), `${id}: scoped EPUB missing`);
  const delivery = id === "openlogic-gu-gujr-in" ? gu270Delivery : french74;
  for (const item of edition.ordered_downloads) check(delivery.files.some(file => file.url === item.url && file.sha256 === item.sha256 && file.bytes === item.bytes && file.matches), `${id}: download lacks matching byte evidence`);
}
check(frGuSources.french.direct_tex_unique_embedded_sources === 51 && frGuSources.french.external_content_imports === 0, "French cumulative LaTeX must contain the51-unit body");
check(french.direct_cumulative_source.sha256 === french.ordered_downloads[1].sha256, "French direct-source metadata must describe the current release");
const gujaratiCurrent = catalogue.editions.find(item => item.id === "openlogic-gu-gujr-in");
check(gujaratiCurrent.source_units_translated === 722 && gujaratiCurrent.standalone_reader_units === 722 && gujaratiCurrent.readers[0].pages === 960, "Gujarati full reader requires722 units and960 pages");
check(gujaratiCurrent.version_doi === "10.5281/zenodo.23030256" && gujaratiCurrent.release_tag === "full-edition-v1.0.1", "Gujarati current lineage matches intake");
check(gujaratiCurrent.ordered_downloads.map(x=>x.format).join(",") === "PDF,TEX,ZIP", "Gujarati keeps PDF/direct LaTeX/source ZIP order");
check(gu722.files.length === 6 && gu722.files.every(x=>x.matches) && gu722.failures.length === 0, "Gujarati needs six fresh anonymous core matches and no package failures");
for (const item of gujaratiCurrent.ordered_downloads) check(gu722.files.some(x=>x.url===item.url && x.sha256===item.sha256 && x.bytes===item.bytes && x.matches), "Gujarati download requires byte evidence");
check(gu722.package.inventory_members===2829 && gu722.package.frozen_sources===722 && gu722.package.native_targets===722 && gu722.package.materialized_bodies===722 && gu722.package.current_segment_bindings===6732 && gu722.package.binding_failures.length===0, "Gujarati complete source and segment identities required");
check(gujaratiCurrent.epub_reader_units===270 && gujaratiCurrent.readers.find(x=>x.format==="EPUB").source_units===270 && gujaratiCurrent.status.includes("full-epub-pending") && !gu722.package.epub_in_this_release, "Gujarati old EPUB is not full722");
check(gujaratiCurrent.supplementary_downloads[0].downloads.every(x=>x.source_units===270 && x.scope_kind==="partial"), "Gujarati historical digital downloads remain partial");
check(!gu722.independent_full_linguistic_certification && !gu722.tex_rerun && gu722.visual.manager_pdf_pages.length===3, "Gujarati intake is not full linguistic certification or a new build");
check(gu722Canon.segment_id==="OLP-0576-B004" && gu722Canon.passages.every(x=>x.hash_matches && x.substantial_lines_match_original) && gu722Canon.glossary.render_matches && gu722Canon.math_multiset_exact && gu722Canon.references_exact, "Gujarati sample replays canon, source and target");
check(frGuSources.gujarati.native_content_files === 163 && frGuSources.gujarati.verified_exact_source_target_spans === 3630 && frGuSources.gujarati.ledger_binding_failures.length === 0, "Gujarati package needs163 sources and3630 exact source/target span checks");
check(guFulltextDelivery.files.length === 16 && guFulltextDelivery.files.every(file => file.matches), "Gujarati full-text repair needs all16 public file readbacks");
check(guFulltextChecks.full_text_reconstruction_byte_identical && guFulltextChecks.complete_direct_text_packaging_defect_closed && guFulltextChecks.unresolved_cumulative_body_imports.length === 0, "Gujarati full-text assembly must be verified");
check(guModelsDelivery.complete && guModelsDelivery.files.length === 16 && guModelsDelivery.files.every(file => file.matches), "Gujarati Models and Theories needs all16 public file matches");
check(guModelsChecks.failures.length === 0 && guModelsChecks.source.inventory_entries_verified === 1252 && guModelsChecks.source.frozen_english_sources === 722 && guModelsChecks.source.native_target_files === 170 && guModelsChecks.source.source_target_span_checks === 3738, "Gujarati current package needs complete inventory/source/target bindings");
check(guModelsChecks.source.complete_fulltext_reconstruction && guModelsChecks.source.unresolved_body_imports.length === 0, "Gujarati direct source must be the exact complete text, not the thin master");
check(guModelsChecks.epub.mathml_nodes === 9653 && guModelsChecks.epub.mathml_structures_match_html && guModelsChecks.epub.tex_annotations_exact === 9653 && guModelsChecks.epub.broken_internal_links.length === 0, "Gujarati EPUB math and links must match");
check(guBeyondDelivery.complete && guBeyondDelivery.files.length === 16 && guBeyondDelivery.files.every(file => file.matches), "Gujarati Beyond needs all16 public file matches");
check(guBeyondChecks.failures.length === 0 && guBeyondChecks.source.inventory_entries_verified === 1285 && guBeyondChecks.source.native_target_files === 178 && guBeyondChecks.source.frozen_english_sources === 722 && guBeyondChecks.source.source_target_span_checks === 3882, "Gujarati Beyond needs exact inventory and source-target bindings");
check(guBeyondChecks.source.complete_fulltext_reconstruction && guBeyondChecks.source.unresolved_body_imports.length === 0, "Current Gujarati direct cumulative source must match reconstructed text");
check(guBeyondChecks.epub.mathml_nodes === 10000 && guBeyondChecks.epub.mathml_structures_match_html && guBeyondChecks.epub.tex_annotations_exact === 10000 && guBeyondChecks.epub.broken_internal_links.length === 0, "Gujarati Beyond EPUB mathematics and internal links must match");
check(guBeyondSample.checks.length === 48 && guBeyondSample.checks.every(item => item.pass) && guBeyondSample.segments.length === 7 && guBeyondSample.terminology_decision.status === "provisional_contextual", "Gujarati bounded canon/source sample must retain uncertainty");
check(gu270Historical.build_master.role === "build-master-not-cumulative-full-text" && gu270Historical.version_doi === "10.5281/zenodo.22985707" && gu270Historical.readers[0].pages === 333, "Retain labelled build master, correct DOI and333-page historical reader");
check(gujaratiCurrent.metadata_language === 'gu-IN' && gujaratiCurrent.ui_labels.repository === 'પ્રોજેક્ટ' && gujaratiCurrent.search_aliases.includes('Gujarati'), 'Gujarati metadata must be localized and discoverable');
check(gu270Delivery.files.length === 16 && gu270Delivery.files.every(x => x.matches), 'Gujarati270 needs all sixteen anonymous public matches');
check(gu270Checks.status === 'PASS' && gu270Checks.inventory_entries === 1612 && gu270Checks.frozen_english_files === 722 && gu270Checks.native_target_files === 270 && gu270Checks.direct_fulltext_matches && gu270Checks.direct_fulltext_sha256 === gu270Historical.direct_latex.sha256, 'Gujarati270 needs exact package and cumulative-source evidence');
check(gu270Canon.segment_id === 'OLP-0273-B023' && gu270Canon.canon.length === 3 && gu270Canon.canon.every(x => x.passage_matches_original_html), 'Gujarati bounded canon replay must match the actual scholarly originals');
for (const [id, units, hasEpub] of [["openlogic-jv-latn-id",24,true]]) {
  const edition = catalogue.editions.find(item => item.id === id);
  check(edition.standalone_reader_units === units, `${id}: release reader scope mismatch`);
  check(edition.ordered_downloads.slice(0,3).map(item => item.format).join(",") === "PDF,TEX,ZIP", `${id}: PDF/direct-LaTeX/source-ZIP order required`);
  check(edition.readers.some(item => item.format === "EPUB") === hasEpub, `${id}: EPUB availability misrepresented`);
  const receipt = JSON.parse(await read("evidence/PUBLIC_READER_DELIVERIES_20260919.json"));
  for (const item of edition.ordered_downloads) check(receipt.files.some(file => file.url === item.url && file.sha256 === item.sha256 && file.bytes === item.bytes && file.matches), `${id}: public download not verified`);
}
const jv = catalogue.editions.find(item => item.id === "openlogic-jv-latn-id");
const jvAudit = JSON.parse(await read("evidence/JAVANESE722_MANAGER_AUDIT_20260929.json"));
const jvCurrent = JSON.parse(await read(jv.evidence.source_checkpoint_readback));
check(jvCurrent.targets_verified === 722 && jvCurrent.frozen_files_verified === 722 && jvCurrent.public_files_verified === 2173 && jvCurrent.archive_crc_pass && jvCurrent.all_inventory_rows_match && jvCurrent.failures.length === 0, "Javanese current source publication identity");
check(jvCurrent.commit === jv.source_progress.commit && jvCurrent.archive.sha256 === jv.source_progress.archive_sha256 && jvCurrent.archive.bytes === jv.source_progress.archive_bytes, "Javanese current archive pointer");
check(jvCurrent.fresh_reaudit_units === 161 && jvCurrent.remaining_reaudit_units === 561 && jvCurrent.choice_records_with_amendments === 1988 && jvCurrent.current_choice_occurrences === 1620 && !jvCurrent.whole_corpus_semantics_certified && !jvCurrent.new_reader_accepted, "Javanese review/source/reader limits");
check(jv.source_units_translated === 722 && jv.standalone_reader_units === 24 && jv.source_archive.sha256 === "4ec915dcf2d31e00c91f6c0eda6cc2850689c6df7c221e6efd7a7562fa9f5dc9", "Javanese source progress must preserve the24-unit reader");
check(jvAudit.targets_verified === 722 && jvAudit.frozen_files_verified === 722 && jvAudit.public_files_verified === 1953 && jvAudit.archive_crc_pass, "Javanese722 public source identity missing");
check(jvAudit.withdrawn_term_bundles === 444 && jvAudit.withdrawn_segment_bundles === 4143 && !jvAudit.canon_revalidation_complete && !jvAudit.whole_corpus_semantics_certified, "Javanese canon limitations must remain explicit");
check(jvAudit.sample_segment_pairs === 168 && jvAudit.sample_all_source_target_hashes_match && jvAudit.canon_pages.length === 3, "Javanese722 source/canon sample must be replayed");
check(jv.metadata_language === "jv-Latn-ID" && jv.ui_labels.details === "Ragam lan watesan" && jv.evidence.manager_public_readback.endsWith(".html"), "Javanese needs a localized evidence entry point");
check(jv.supplementary_downloads?.[0]?.downloads?.[0]?.url === jvCurrent.archive.url, "Javanese source link must use supplementary_downloads");
const jvPrior = JSON.parse(await read("evidence/JAVANESE671_MANAGER_AUDIT_20260928.json"));
check(jvPrior.manager_corrections_present && jvPrior.OLP0671_all10_source_target_hash_pairs_match && jvAudit.prior_targets_changed.length === 0, "Previously verified Javanese proof repairs must be preserved");
check(jvAudit.attribution_correction_verified && jvAudit.owner_runtime_phases.length === 2, "Javanese primary-task attribution correction must be evidenced");
check(jvAudit.new_language_bearing_segment_delta === 89 && jvAudit.new_formal_only_changes === 1 && jvAudit.new_canon_bindings_checked === 89, "Javanese must distinguish language changes from the formal-only path correction");
const tamil722 = JSON.parse(await read("evidence/TAMIL_BEFORE_UNIFIED_20260929.json"));
const tamil722Audit = JSON.parse(await read("evidence/TAMIL722_MANAGER_AUDIT_20260928.json"));
check(tamil722.source_units_translated === 722 && tamil722.standalone_reader_units === 695 && tamil722.companion_units === 27 && tamil722.combined_reader_units === 722, "Tamil source722 must distinguish main695 and companion27");
check(tamil722Audit.scope.single_standalone_722_reader === false && tamil722Audit.scope.frozen_source_files_verified === 722 && tamil722Audit.scope.target_files_verified === 722 && tamil722Audit.scope.packaged_file_hashes_verified === 1559 && tamil722Audit.scope.direct_tex_exact_archive_matches === 2, "Tamil released source/package identity must be independently replayed");
check(tamil722Audit.files.length === 10 && tamil722.ordered_downloads.map(item => item.format).join(",") === "PDF,TEX,ZIP,PDF,TEX", "Tamil requires ten public matches and paired editable sources");
for (const item of tamil722.ordered_downloads) check(tamil722Audit.files.filter(file => file.name === item.name && file.sha256 === item.sha256 && file.bytes === item.bytes && file.anonymous).length === 2, "Every Tamil download must match on both mirrors");
check(!tamil722.readers.some(item => item.format === "EPUB") && tamil722.epub_status === "in-progress-not-published", "Tamil unpublished EPUB must not be advertised as available");
check(tamil722.metadata_language === "ta-IN" && tamil722.ordered_downloads.every(item => /[\u0B80-\u0BFF]/.test(item.download_label)), "Tamil entry and download labels must be localized");
check(tamil722.limitations.some(item => item.includes("tamil-complete.pdf") && item.includes("tamil-source-companion.pdf")), "Tamil offline PDF filename workaround must remain visible until repaired");
const taUnified = catalogue.editions.find(item => item.id === "openlogic-ta-taml-in");
const taUnifiedAudit = JSON.parse(await read("evidence/TAMIL722_UNIFIED_AUDIT_20260929.json"));
check(["source_units_translated","standalone_reader_units","pdf_reader_units","epub_reader_units","zenodo_reader_units"].every(k=>taUnified[k]===722), "Tamil standalone PDF/EPUB722 scope");
check(taUnified.ordered_downloads.map(x=>x.format).join(",")==="PDF,TEX,ZIP,EPUB", "Tamil direct cumulative source ordering");
check(taUnifiedAudit.files.length===20 && taUnifiedAudit.files.every(x=>x.matches && x.anonymous), "Tamil needs20 exact anonymous matches");
for (const item of taUnified.ordered_downloads) check(taUnifiedAudit.files.filter(x=>x.name===item.name && x.sha256===item.sha256 && x.bytes===item.bytes).length===2, "Tamil current downloads must match both mirrors");
check(taUnifiedAudit.pdf.failures.length===0 && taUnifiedAudit.pdf.annotation_actions_compared===2823 && taUnifiedAudit.pdf.outline_entries_compared===718 && taUnifiedAudit.pdf.pages_compared===1227, "Tamil navigation and page identities need full replay");
check(taUnifiedAudit.source_archive.manifest_hashes_verified===1574 && taUnifiedAudit.source_archive.frozen_hashes_verified===722 && taUnifiedAudit.source_archive.target_hashes_verified===722 && taUnifiedAudit.cumulative_tex.exact_component_unit_blocks===722, "Tamil complete editable source identity");
check(taUnifiedAudit.source_replay.new_component_tex_rebuild.status==="not-run-slot-unavailable" && taUnifiedAudit.manager_whole_language_certification===false, "Tamil audit limits must remain honest");
check(taUnified.metadata_language==="ta-IN" && taUnified.ordered_downloads.every(x=>/[\u0B80-\u0BFF]/.test(x.download_label)) && taUnified.version_doi==="10.5281/zenodo.23025099", "Tamil local-language access and exact DOI");
const newDelivery = JSON.parse(await read("evidence/PASHTO_BENGALI_PUBLIC_DELIVERY_20260919.json"));
const sourceProgress = JSON.parse(await read("evidence/SOURCE_PROGRESS_TE270_MR163_20260919.json"));
check(sourceProgress.source_readbacks.length === 26 && sourceProgress.source_readbacks.every(file => file.match), "Telugu/Marathi source readbacks must all match");
const marathiBeforeComplete = JSON.parse(await read("evidence/MARATHI_BEFORE_COMPLETE_20260929.json"));
check(marathiBeforeComplete.source_units_translated === 270 && marathiBeforeComplete.standalone_reader_units === 194, "Preserve historical Marathi source270/reader194 evidence");
const bengaliRepair = JSON.parse(await read("evidence/BENGALI_SOURCE_REPAIR_20260919.json"));
const marathi194 = marathiBeforeComplete; // Historical edition, not current reader.
const marathi194Evidence = JSON.parse(await read(marathi194.evidence.public_readback));
check(marathi194Evidence.files.length === 8 && marathi194Evidence.files.every(item => item.github_matches && item.zenodo_matches), "Marathi194 needs eight byte-matched assets on both public mirrors");
check(marathi194Evidence.source_archive.manifest_entries_replayed === 2177 && marathi194Evidence.source_archive.translated_target_files_replayed === 194 && marathi194Evidence.source_archive.frozen_source_files_replayed === 722 && marathi194Evidence.source_archive.identity_failures.length === 0, "Marathi194 needs source-package identity replay");
check(marathi194.ordered_downloads.slice(0,4).map(item => item.format).join(",") === "PDF,TEX,ZIP,EPUB" && marathi194.readers[0].pages === 264, "Marathi194 reader identity and editable-source download order");
check(marathi194.ordered_downloads.every(item => /[\u0900-\u097f]/.test(item.download_label || '')), "Every Marathi download label, including HTML-ZIP, must be localized");
for (const item of marathi194.ordered_downloads) check(marathi194Evidence.files.some(file => file.url === item.url && file.bytes === item.bytes && file.sha256 === item.sha256), "Marathi194 download must match readback");
check(marathi194Evidence.full_semantic_reaudit === false && marathi194Evidence.packaging_observations.length === 2, "Marathi194 bounded evidence must retain its limitations");
const marathi722 = catalogue.editions.find(item => item.id === "openlogic-mr-deva-in");
const marathi722Audit = JSON.parse(await read(marathi722.evidence.public_readback));
check(["source_units_translated","standalone_reader_units","pdf_reader_units","html_reader_units","zenodo_reader_units"].every(k=>marathi722[k]===722), "Marathi complete PDF/HTML/source scope");
check(marathi722Audit.files.length===110 && marathi722Audit.files.every(f=>f.match && f.anonymous), "Marathi v1.1 needs16 GitHub and94 Zenodo exact anonymous matches");
check(marathi722Audit.github_reused_78.length===78 && marathi722Audit.github_reused_78.every(f=>f.prior_match && !f.fresh_github_download), "Preserve78 prior GitHub identities without claiming fresh downloads");
check(marathi722Audit.source_routing.disjoint && marathi722Audit.source_routing.exact_source_manifest_union && marathi722Audit.source_routing.units===722, "Marathi reader routing must partition frozen source");
check(marathi722Audit.structural_audit.source_units===722 && marathi722Audit.structural_audit.aligned_segments===6644 && marathi722Audit.structural_audit.failed_checks.length===0, "Marathi source and segment identity");
check(marathi722.ordered_downloads.map(f=>f.format).join(",")==="PDF,TEX,ZIP,EPUB" && marathi722.readers[0].pages===921, "Marathi PDF/direct-TeX/source-ZIP/EPUB order");
for (const f of [...marathi722.ordered_downloads,...marathi722.supplementary_downloads[0].downloads]) {
  check(marathi722Audit.files.filter(r=>r.name===f.name && r.bytes===f.bytes && r.sha256===f.sha256).length===2, "Marathi download must match both mirrors");
  check(/[\u0900-\u097f]/.test(f.download_label), "Marathi localized labels");
}
check(marathi722.readers.find(f=>f.format==="EPUB")?.source_units===722 && marathi722.epub_reader_units===722 && marathi722Audit.epub.complete_available && marathi722Audit.epub.reading_documents===98, "Marathi complete EPUB722 must be the current reader");
check(marathi722.supplementary_downloads[1].downloads[0].source_units===194, "Historical EPUB194 access retained");
check(marathi722Audit.canon.empty_direct_passage_rows===5 && marathi722Audit.canon.retrospective_contexts===101 && !marathi722.evidence.complete_linguistic_certification && !marathi722Audit.pdf.whole_pdf_visual_certification, "Marathi scoped retrospective evidence and audit limits");
check(marathi722.version_doi==="10.5281/zenodo.23044506" && marathi722.current_local_configured_reader.public_release_sync_verified, "Marathi current record and sync");
const marathiGuide = await read(marathi722.evidence.manager_public_readback);
check(marathiGuide.includes('lang="mr"') && marathiGuide.includes("१०१") && marathiGuide.includes("१९४") && marathiGuide.includes("GPT-6 Astra") && marathiGuide.includes("06-openlogic-mr-complete.epub"), "Marathi native current EPUB guide with preserved history and limitations");
const teBeforeComplete = JSON.parse(await read("evidence/TE_BEFORE_COMPLETE_20260928.json"));
const telugu276 = teBeforeComplete; // Historical276-unit scope, not the current release.
const telugu276Evidence = JSON.parse(await read(telugu276.evidence.public_readback));
const teluguPrevious = JSON.parse(await read(telugu276.evidence.previous_276_intake));
check(telugu276.source_units_translated === 410 && telugu276.standalone_reader_units === 276, "Telugu public source410 must remain distinct from reader276");
check(telugu276.readers.find(item => item.format === "EPUB")?.source_units === 276 && telugu276.source_progress.html_reader_units === 23, "Telugu EPUB276 must not inflate HTML23");
check(telugu276Evidence.epub.units === 276 && telugu276Evidence.integrity_failures.length === 0 && telugu276Evidence.files.length === 15 && telugu276Evidence.all_public_assets_match, "Telugu repaired assets require actual package and byte evidence");
check(teluguPrevious.new_source_batch.missing_passage_mapping.length === 3 && telugu276.source_progress.canon_mapping_gaps === 3, "Keep frozen Telugu canon-mapping gaps explicit");
check(telugu276Evidence.source_companion.hashes_verified === 54 && telugu276Evidence.source_companion.unique_units === 276, "Telugu direct TeX and PDF dependencies must be checked");
const teluguRepair = JSON.parse(await read(telugu276.evidence.bounded_repair_readback));
check(telugu276Evidence.bibliography_defects.length === 4, "Preserve the historical bibliography-defect evidence");
check(teluguRepair.all_public_assets_match && teluguRepair.files.length === 16 && teluguRepair.source_entries === 1386, "Telugu repair needs actual public-byte and source-package evidence");
check(telugu276.source_packaging_status === "pdf-epub-direct-LaTeX-and-complete-source-companion-verified" && teluguRepair.new_linguistic_certification === false, "Bounded source repair must not imply new linguistic certification");
check(telugu276.ordered_downloads.slice(0,4).map(x=>x.format).join(",") === "PDF,TEX,ZIP,EPUB", "Telugu download order");
for (const file of telugu276.ordered_downloads) check(teluguRepair.files.some(item => item.url === file.url && item.bytes === file.bytes && item.sha256 === file.sha256 && item.matches), "Telugu download must match current anonymous readback");
const psSource = JSON.parse(await read("evidence/PASHTO_SOURCE247_MANAGER_READBACK_20260920.json"));
const psEdition = catalogue.editions.find(item => item.id === "openlogic-ps-arab-pk");
check(psSource.source_files_verified === 722 && psSource.target_files_verified === 247 && psSource.failures === 0 && psSource.new_batch_exact_block_checks === 376, "Pashto source checkpoint requires frozen-source, target and actual new-batch block checks");
check(psEdition.previous_v051_release_snapshot.source_progress.archive_sha256 === psSource.archive.sha256 && psEdition.previous_v051_release_snapshot.source_progress.commit === psSource.commit && psSource.reader_units === 82 && psSource.reader_files_changed === false, "Retain the historical Pashto source247/reader82 distinction");
const psV070 = JSON.parse(await read("evidence/PASHTO_V070_MANAGER_AUDIT_20260927.json"));
const psV071 = JSON.parse(await read("evidence/PASHTO_V071_MANAGER_AUDIT_20260928.json"));
const psCurrent = JSON.parse(await read("evidence/PASHTO_V060_MANAGER_AUDIT_20260920.json"));
check(psCurrent.files.length === 6 && psCurrent.files.every(item => item.matches) && psCurrent.github_assets_independently_matched === 6, "Pashto v0.6.0 needs six matched GitHub assets");
check(psCurrent.static_package.frozen_sources_checked === 722 && psCurrent.static_package.translated_units === 255 && psCurrent.static_package.aligned_blocks === 4010 && psCurrent.static_package.canon_bound_language_segments === 2549 && psCurrent.static_package.failures.length === 0, "Pashto255 exact source/alignment/canon-reference package check required");
check(psEdition.previous_v060_release_snapshot.source_progress.commit === psCurrent.commit && psEdition.previous_v060_release_snapshot.source_archive.sha256 === psEdition.previous_v060_release_snapshot.source_progress.archive_sha256 && psEdition.previous_v060_release_snapshot.readers[0].pages === 326, "Pashto255 release identity and page count must agree");
check(psCurrent.bounded_language_sample.segment_id === "OLP-0254-B005" && psCurrent.bounded_language_sample.canon_pages_actually_inspected.length === 2 && psCurrent.visual_sample.whole_pdf_visual_certification === false, "Keep the Pashto sample audit bounded");
check(psCurrent.zenodo.manager_anonymous_byte_check.includes("not independently verified") && psEdition.evidence.manager_full_semantic_rereview === false, "Do not promote owner or bounded evidence to independent full certification");
const bnFullReader = JSON.parse(await read("evidence/BN722_HTML_READER_PUBLIC_20260928.json"));
const bnFullEpub = JSON.parse(await read("evidence/BN722_V051_READER_PUBLIC_20260928.json"));
const bnBeforeComplete = JSON.parse(await read("evidence/BN722_BEFORE_COMPLETE_20260928.json"));
const bnComplete = catalogue.editions.find(item => item.id === "openlogic-bn-beng-in");
const bnCompleteEvidence = JSON.parse(await read("evidence/BN722_COMPLETE_MANAGER_20260928.json"));
check(bnComplete.release_tag === "v1.0.0-complete-edition" && bnComplete.version_doi === "10.5281/zenodo.23018795", "Bengali current release identity");
check(bnComplete.source_units_translated === 722 && bnComplete.standalone_reader_units === 722 && bnComplete.pdf_reader_units === 722 && bnComplete.html_reader_units === 722 && bnComplete.epub_reader_units === 722 && bnComplete.zenodo_reader_units === 722, "Bengali complete format scopes");
check(bnComplete.full_pdf_published && bnComplete.pertinent_pdf_exists && bnComplete.ordered_downloads.slice(0,3).map(x=>x.format).join(",") === "PDF,TEX,ZIP", "Bengali PDF/direct-LaTeX/source-ZIP order");
check(bnCompleteEvidence.files.length === 14 && bnCompleteEvidence.files.every(x=>x.matches) && bnCompleteEvidence.public_inventory_unchanged, "Bengali complete assets require fourteen anonymous matches and unchanged current inventory");
for (const asset of bnComplete.ordered_downloads) check(bnCompleteEvidence.files.some(x=>x.host === "github" && x.url === asset.url && x.bytes === asset.bytes && x.sha256 === asset.sha256 && x.matches), "Bengali current download must match exact public bytes");
check(bnCompleteEvidence.source_package.frozen_exact_local_matches === 722 && bnCompleteEvidence.source_package.target_exact_local_matches === 722 && bnCompleteEvidence.source_package.failures.length === 0 && bnCompleteEvidence.source_recheck.source_members === 1528, "Bengali final source package scope");
check(bnCompleteEvidence.source_recheck.unit_ids === 722 && bnCompleteEvidence.source_recheck.direct_tex_matches_archive && bnCompleteEvidence.source_recheck.epub_unique_unit_anchors === 722 && bnCompleteEvidence.source_recheck.crc_failure === null, "Bengali exact cumulative source and EPUB unit containers");
check(bnCompleteEvidence.source_recheck.metadata.revision === 6 && bnCompleteEvidence.source_recheck.metadata.description_sha256 === "db69b4ec91f5988a215f6046961ba283363657f775fc077ba3c8c6c6270488d5" && bnCompleteEvidence.full_linguistic_certification === false, "Bengali localized metadata identity and review limits");
const ps500Evidence = JSON.parse(await read("evidence/PASHTO500_MANAGER_AUDIT_20260928.json"));
const ps515Evidence = JSON.parse(await read("evidence/PASHTO515_MANAGER_AUDIT_20260929.json"));
const ps520Evidence = JSON.parse(await read("evidence/PASHTO520_MANAGER_AUDIT_20260929.json"));
const ps546Evidence = JSON.parse(await read("evidence/PASHTO546_MANAGER_AUDIT_20260929.json"));
const ps586Evidence = JSON.parse(await read("evidence/PASHTO586_MANAGER_AUDIT_20260929.json"));
const ps595Evidence = JSON.parse(await read("evidence/PASHTO595_MANAGER_AUDIT_20260930.json"));
const ps606Evidence = JSON.parse(await read("evidence/PASHTO606_MANAGER_AUDIT_20260930.json"));
const ps608Evidence = JSON.parse(await read("evidence/PASHTO608_REAUDIT_INTAKE_20260930.json"));
const ps612Evidence = JSON.parse(await read("evidence/PASHTO612_PUBLIC_INTAKE_20260930.json"));
const ps622Evidence = JSON.parse(await read("evidence/PASHTO622_PUBLIC_INTAKE_20260930.json"));
const ps632Evidence = JSON.parse(await read("evidence/PASHTO632_PUBLIC_INTAKE_20260930.json"));
const ps635Evidence = JSON.parse(await read("evidence/PASHTO635_PUBLIC_INTAKE_20260930.json"));
const ps638Evidence = JSON.parse(await read("evidence/PASHTO638_PUBLIC_INTAKE_20260930.json"));
const ps642Evidence = JSON.parse(await read("evidence/PASHTO642_PUBLIC_INTAKE_20260930.json"));
const ps644Evidence = JSON.parse(await read("evidence/PASHTO644_PUBLIC_INTAKE_20260930.json"));
const ps648Evidence = JSON.parse(await read("evidence/PASHTO648_PUBLIC_INTAKE_20260930.json"));
check(ps648Evidence.targets_verified === 648 && ps648Evidence.frozen_sources_verified === 722 && ps648Evidence.changed_files.length === 46 && ps648Evidence.changed_files.every(f=>f.matches) && ps648Evidence.failures.length === 0, "Pashto648 public source/archive bytes");
check(ps648Evidence.whole_unit_reaudit_owner_count === 18 && ps648Evidence.whole_unit_reaudit_remaining === 281 && ps648Evidence.reader_units === 321 && !ps648Evidence.reader_accepted && !ps648Evidence.full_semantic_reaudit, "Pashto648 source-only and incomplete review scope");
check(ps648Evidence.aligned_blocks === 9593 && ps648Evidence.canon_records === 6068 && ps648Evidence.canon_sample.pages_actually_viewed.length === 3 && ps648Evidence.reader_guide_choice_records.length === 9, "Pashto648 alignment, actual canon sample and localized guide choices");

check(ps644Evidence.targets_verified === 644 && ps644Evidence.frozen_sources_verified === 722 && ps644Evidence.changed_files.length === 49 && ps644Evidence.changed_files.every(f=>f.matches) && ps644Evidence.failures.length === 0, "Pashto644 public source/archive bytes");
check(ps644Evidence.whole_unit_reaudit_owner_count === 16 && ps644Evidence.whole_unit_reaudit_remaining === 283 && ps644Evidence.reader_units === 321 && !ps644Evidence.manager_full_semantic_rereview && ps644Evidence.metadata_findings.length === 0, "Pashto644 review limits and corrected native arithmetic");
check(ps642Evidence.targets_verified === 642 && ps642Evidence.frozen_sources_verified === 722 && ps642Evidence.changed_files.length === 46 && ps642Evidence.changed_files.every(f=>f.matches) && ps642Evidence.byte_verification_failures.length === 0, "Pashto642 exact source/archive bytes");
check(ps642Evidence.reader_units === 321 && ps642Evidence.whole_unit_reaudit_owner_count === 15 && ps642Evidence.whole_unit_reaudit_remaining === 299-15 && !ps642Evidence.manager_full_semantic_rereview && ps642Evidence.metadata_findings[0].displayed_remaining === 280, "Pashto642 separates accurate hub arithmetic from reported native-status defect");
check(ps638Evidence.targets_verified === 638 && ps638Evidence.frozen_sources_verified === 722 && ps638Evidence.changed_files.length === 38 && ps638Evidence.changed_files.every(f=>f.matches) && ps638Evidence.failures.length === 0, "Pashto638 exact source/archive bytes");
check(ps638Evidence.reader_units === 321 && ps638Evidence.whole_unit_reaudit_owner_count === 14 && ps638Evidence.whole_unit_reaudit_remaining === 285 && !ps638Evidence.manager_full_semantic_rereview && ps638Evidence.independent_replay.canon_linked_language_blocks === 9, "Pashto638 preserves reader and bounded canon-review limits");
check(ps635Evidence.targets_verified === 635 && ps635Evidence.frozen_sources_verified === 722 && ps635Evidence.changed_files.length === 89 && ps635Evidence.changed_files.every(f=>f.matches) && ps635Evidence.failures.length === 0, "Pashto635 exact source/archive bytes");
check(ps635Evidence.reader_units === 321 && ps635Evidence.whole_unit_reaudit_owner_count === 11 && ps635Evidence.whole_unit_reaudit_remaining === 288 && !ps635Evidence.manager_full_semantic_rereview, "Pashto635 preserves reader and review limits");
check(ps632Evidence.source_units===632 && ps632Evidence.source_unit_delta===10 && ps632Evidence.changed_files.length===39 && ps632Evidence.changed_files.every(f=>f.matches) && ps632Evidence.failures.length===0, "Pashto632 public source bytes");
check(ps632Evidence.reader_units===321 && ps632Evidence.whole_sol6_units_reaudited===10 && ps632Evidence.whole_sol6_units_pending===289 && ps632Evidence.canon_sample.pages_actually_viewed.length===2 && !ps632Evidence.full_linguistic_certification, "Pashto632 reader, review and canon scope");
check(ps622Evidence.source_units === 622 && ps622Evidence.source_unit_delta === 10 && ps622Evidence.changed_files.length === 27 && ps622Evidence.changed_files.every(f=>f.matches) && ps622Evidence.aligned_blocks_verified === 9217 && ps622Evidence.canon_record_hash_bindings === 5834 && ps622Evidence.failures.length === 0, "Pashto622 public source/alignment evidence");
check(ps622Evidence.canon_sample.pages_actually_viewed.length === 2 && ps622Evidence.math_sample.new_unit_checks.length === 10 && ps622Evidence.whole_sol6_units_reaudited === 8 && ps622Evidence.whole_sol6_units_pending === 291 && !ps622Evidence.full_linguistic_certification && ps622Evidence.reader_units === 321, "Pashto622 bounded canon/math sample, incomplete full review and reader scope");
check(ps612Evidence.source_units === 612 && ps612Evidence.source_unit_delta === 4 && ps612Evidence.changed_files.length === 45 && ps612Evidence.changed_files.every(f=>f.matches) && ps612Evidence.aligned_blocks_verified === 9074 && ps612Evidence.canon_record_hash_bindings === 5761 && ps612Evidence.failures.length === 0, "Pashto612 needs exact public source/alignment evidence");
check(ps612Evidence.canon_sample.pages_actually_viewed.length === 2 && ps612Evidence.whole_sol6_units_reaudited === 8 && ps612Evidence.whole_sol6_units_pending === 291 && !ps612Evidence.full_linguistic_certification && ps612Evidence.reader_units === 321, "Pashto612 must retain canon sample and incomplete linguistic/reader scope");
check(ps608Evidence.failures.length === 0 && ps608Evidence.source_units === 608 && ps608Evidence.frozen_source_units === 722 && ps608Evidence.all44_archive_members_match_owner_public_receipt.length === 44 && ps608Evidence.all44_archive_members_match_owner_public_receipt.every(f=>f.matches), "Pashto608 needs anonymous archive/source/target and44-member identity evidence");
check(ps608Evidence.owner_new_reaudit_whole_units === 5 && ps608Evidence.owner_new_reaudit_pending === 294 && ps608Evidence.whole_unit_reaudit_segment_records === 43 && !ps608Evidence.whole_corpus_linguistic_certification && ps608Evidence.reader_units === 321, "Five reviewed units must not be promoted to full608 linguistic certification");
check(["OLSTH-024","OLSTH-031","OLSTH-032"].every(id=>ps608Evidence.correction_objects[id].status === "superseded"), "Withdrawn false positives must not remain active source findings");
check(ps606Evidence.failures.length === 0 && ps606Evidence.source_units === 606 && ps606Evidence.source_unit_delta === 11 && ps606Evidence.new_alignment_blocks === 211 && ps606Evidence.new_changed_blocks_with_canon === 153, "Pashto606 needs exact changed-source and alignment evidence");
check(ps606Evidence.archive.source_entries_crc_and_hash_verified === 722 && ps606Evidence.archive.target_entries_crc_and_hash_verified === 606 && ps606Evidence.archive.exact_target_scope_through606 && ps606Evidence.archive.unaccepted607_absent, "Pashto606 archive must preserve frozen722 sources and exclude unaccepted607");
check(ps606Evidence.public_readbacks.length === 28 && ps606Evidence.public_readbacks.every(f=>f.pass) && !ps606Evidence.whole_corpus_translation_certified && ps606Evidence.reader_units === 321, "Pashto606 public bytes do not constitute full linguistic or new-reader certification");
check(ps606Evidence.source_findings.withdrawn === "OLSTH-024" && ps606Evidence.manager.model === "gpt-6-astra" && ps606Evidence.manager.effort === "ultra", "Pashto606 needs the explicit retirement and actual audit model");
check(ps595Evidence.failures.length === 0 && ps595Evidence.source_units === 595 && ps595Evidence.source_unit_delta === 9 && ps595Evidence.new_alignment_blocks === 143 && ps595Evidence.new_changed_blocks_with_canon === 110, "Pashto595 changed-unit and alignment evidence");
check(ps595Evidence.archive_validation.crc_passed && ps595Evidence.archive_validation.frozen_sources_verified === 722 && ps595Evidence.archive_validation.targets_present === 595 && ps595Evidence.archive_validation.exact_through595, "Pashto595 archive must contain exactly the accepted scope and frozen sources");
check(ps595Evidence.previous_targets_unchanged === 585 && ps595Evidence.previous_target_repairs === 1 && ps595Evidence.semantic_repairs_closed.length === 2 && ps595Evidence.semantic_repairs_pending.length === 0, "Pashto595 must distinguish the verified repairs from unchanged targets");
check(ps595Evidence.new_targets.length === 9 && ps595Evidence.new_targets.every(x=>x.source_and_target_match) && ps595Evidence.public_files === 21 && !ps595Evidence.whole_corpus_translation_certified, "Pashto595 readback is bounded, not whole-language certification");
check(ps586Evidence.failures.length === 0 && ps586Evidence.source_units === 586 && ps586Evidence.source_unit_delta === 40 && ps586Evidence.previous_targets_unchanged === 546 && ps586Evidence.new_alignment_blocks === 527 && ps586Evidence.new_changed_blocks_with_canon === 383 && ps586Evidence.public_files === 32, "Pashto586 frozen-source/alignment/public-file delta evidence");
check(ps586Evidence.semantic_repair_pending.length === 2 && !ps586Evidence.whole_corpus_translation_certified && ps586Evidence.reader_units === 321, "Pashto586 must retain pending semantic repairs and reader321 boundary");
check(ps546Evidence.failures.length === 0 && ps546Evidence.source_units === 546 && ps546Evidence.frozen_source_units === 722 && ps546Evidence.source_unit_delta === 10 && ps546Evidence.aligned_block_delta === 121 && ps546Evidence.changed_content_canon_row_delta === 86 && ps546Evidence.previous_targets_unchanged === 536 && ps546Evidence.public_files_replayed === 52 && ps546Evidence.math_spans_verified === 220 && ps546Evidence.staged_units.length === 5, "Pashto546 must have exact changed-source, canon-reference and math evidence");
const ps536Evidence = JSON.parse(await read("evidence/PASHTO536_MANAGER_AUDIT_20260929.json"));
check(ps536Evidence.failures.length === 0 && ps536Evidence.accepted_draft_units === 536 && ps536Evidence.frozen_files === 722 && ps536Evidence.aligned_blocks === 7990 && ps536Evidence.canon_use_rows === 4977 && ps536Evidence.staged_unaccepted_units === 5 && ps536Evidence.delta_since520.units === 16 && ps536Evidence.unchanged_previous_targets === 519 && ps536Evidence.predicativity_repair_verified_exact_two_words, "Pashto536 source checkpoint must retain exact scope and predecessor bytes");
check(ps520Evidence.failures.length === 0 && ps520Evidence.accepted_draft_units === 520 && ps520Evidence.frozen_files === 722 && ps520Evidence.aligned_blocks === 7817 && ps520Evidence.canon_hash_bound_changed_blocks === 4882 && ps520Evidence.unaccepted_staged_units === 5 && ps520Evidence.rule_label_repair.manager_read_full_diff_and_macro_definition, "Pashto520 needs current public identity and concrete label-repair evidence");
const ps500 = catalogue.editions.find(item => item.id === "openlogic-ps-arab-pk");
check(ps500Evidence.failures.length === 0 && ps500Evidence.source_files_verified === 722 && ps500Evidence.accepted_target_files_verified === 500, "Pashto500 requires actual source/target replay");
check(ps500Evidence.aligned_blocks_verified === 7561 && ps500Evidence.changed_blocks_with_canon_hash_references === 4734 && ps500Evidence.staged_unaccepted_files === 4, "Pashto500 alignment and staged scope");
check(ps500.previous_source_checkpoint_500.commit === ps500Evidence.commit, "Preserve historical Pashto500 checkpoint identity");
check(ps515Evidence.failures.length === 0 && ps515Evidence.frozen_files === 722 && ps515Evidence.accepted_draft_units === 515 && ps515Evidence.aligned_blocks === 7765 && ps515Evidence.canon_hash_bound_changed_blocks === 4861 && ps515Evidence.unaccepted_staged_units === 4, "Pashto515 needs exact source/alignment/canon-reference replay");
check(ps500.previous_source_checkpoint_586.commit === ps586Evidence.commit && ps500.previous_source_progress_586.archive_sha256 === ps586Evidence.archive.sha256, "Preserve the historical Pashto586 source snapshot");
check(ps500.previous_source_checkpoint_595.commit === ps595Evidence.commit && ps500.previous_source_progress_595.archive_sha256 === ps595Evidence.archive.sha256, "Preserve historical Pashto595 identity");
check(ps500.public_source_checkpoint.commit === ps648Evidence.commit && ps500.source_progress.archive_sha256 === ps648Evidence.archive.sha256 && ps500.source_progress.archive_bytes === ps648Evidence.archive.bytes, "Pashto648 public source identity");
check(ps500.supplementary_downloads[0].downloads[0].url === ps648Evidence.archive.url && !ps595Evidence.whole_corpus_translation_certified, "Pashto source ZIP needs a usable download and scoped claims");
check((await read("README.md")).includes("PASHTO648_REVIEW.ps.html") && !(await read("README.md")).includes("**پښتو (پاکستان): ۳۹۳"), "Pashto README must not foreground superseded reader defects");
check(ps500.reader_guide === "evidence/PASHTO648_REVIEW.ps.html" && (await read(ps500.reader_guide)).includes('lang="ps-Arab-PK" dir="rtl"') && ps500.status.includes("bounded-terminology-repair-verified") && !ps500.status.includes("terminology-repair-pending"), "Pashto must expose its native guide and verified repair status");
for (const [id, sources, units, epubUnits] of [["openlogic-ps-arab-pk",648,321,321],["openlogic-bn-beng-in",722,722,722]]) {
  const edition = id === "openlogic-bn-beng-in" ? bnBeforeComplete : catalogue.editions.find(item => item.id === id);
  check(edition.source_units_translated === sources && edition.standalone_reader_units === units, `${id}: source and reader scope must stay distinct`);
  check(edition.readers.some(item => item.format === "EPUB" && item.source_units === epubUnits), `${id}: format-specific EPUB scope missing`);
  for (const item of edition.ordered_downloads) check([...newDelivery.files,...bengaliRepair.files,...psCurrent.files,...psV070.files,...psV071.files,...bnFullReader.files,...bnFullEpub.files].some(file => file.url === item.url && file.sha256 === item.sha256 && file.bytes === item.bytes && file.matches), `${id}: public download not verified`);
  if (id === "openlogic-ps-arab-pk") check(edition.ordered_downloads.slice(0,3).map(item => item.format).join(",") === "PDF,TEX,ZIP", "Pashto needs PDF/direct cumulative LaTeX/source ZIP order");
  else {
    check(edition.source_packaging_status === "direct-cumulative-LaTeX-and-full-source-ZIP-verified" && edition.pertinent_pdf_exists === false && edition.online_reading_preview, "Bengali needs full cumulative source and its no-PDF online preview");
    check(edition.ordered_downloads.slice(0,2).map(item=>item.format).join(',') === "TEX,ZIP", "Bengali no-PDF source order must be direct LaTeX then ZIP");
    check(bnFullReader.files.length === 12 && bnFullReader.files.every(f=>f.matches) && bnFullReader.failures.length === 0, "Bengali complete HTML needs twelve matched anonymous public files");
    check(bnFullReader.source_archive.members === 1510 && bnFullReader.source_archive.frozen_source_hash_matches === 722 && bnFullReader.source_archive.target_hash_matches === 722 && bnFullReader.source_archive.direct_tex_matches_archived, "Bengali full source archive must bind all 722 original and translated files and direct LaTeX");
    check(bnFullReader.reader_structure.tex_unique_units === 722 && bnFullReader.reader_structure.tex_properly_nested && bnFullReader.reader_structure.html_unique_units === 722 && bnFullReader.reader_structure.html_order_matches && bnFullReader.reader_structure.broken_internal_links === 0, "Bengali complete reader requires exact unit membership, nested TeX, ordered HTML and working internal links");
    check(edition.html_reader_units === 722 && edition.epub_reader_units === 722 && edition.full_pdf_published === false && edition.full_epub_published === true && edition.zenodo_reader_units === 299, "Bengali HTML/EPUB722 must preserve old Zenodo299 and pending full PDF");
    check(bnFullEpub.files.length === 12 && bnFullEpub.files.every(f=>f.matches) && bnFullEpub.failures.length === 0, "Bengali full EPUB needs anonymous exact public assets and clean bounded checks");
    check(bnFullEpub.epub.source_units === 722 && bnFullEpub.epub.mathml === 43521 && bnFullEpub.epub.epubcheck_messages === 0 && bnFullEpub.reader_structure.tex_properly_nested, "Bengali EPUB must bind all 722 units, MathML, exact EPUBCheck report and properly nested direct LaTeX");
    check(bnFullEpub.source_archive.members === 1515 && bnFullEpub.source_archive.frozen_source_hash_matches === 722 && bnFullEpub.source_archive.nonempty_targets === 722 && bnFullEpub.source_archive.direct_tex_matches_archived, "Bengali current source ZIP must bind the exact direct LaTeX and all sources/targets");
    check(bnFullEpub.ledger.rows === 7825 && bnFullEpub.ledger.exact_spans_checked === 15650 && bnFullEpub.ledger.canon_passage_references_resolve && bnFullEpub.source_archive.changed_targets.length === 5, "Bengali v0.5.1 needs exact segment bindings and bounded typography changes");
    check(bengaliRepair.github_files_matched === 6 && bengaliRepair.static_source_inspection.unique_units === 299, "Preserve historical Bengali299 source-repair evidence");
  }
}
check(newDelivery.files.length === 30 && newDelivery.files.every(item => item.matches), "Pashto/Bengali intake must preserve the thirty matched readbacks");
const currentSources = JSON.parse(await read("evidence/SOURCE_PROGRESS_BN390_TA561_TE344_PS300_20260921.json"));
const updatedBnTe = JSON.parse(await read("evidence/SOURCE_PROGRESS_BN496_TE394_20260926.json"));
const bengali514 = JSON.parse(await read("evidence/BN514_PUBLIC_SOURCE_20260926.json"));
check(bengali514.changed_units === 18 && bengali514.changed_segments === 167 && bengali514.changed_language_segments === 145 && bengali514.failures.length === 0, "Bengali514 requires exact changed-segment replay, not an owner count alone");
check(bengali514.bounded_semantic_check.source_correction_id === 'BN-SRC-411' && bengali514.canon_sample.original_visually_inspected && !bengali514.full_semantic_reaudit, "Keep Bengali source/canon sampling bounded and source-grounded");
const bnMrCurrent = JSON.parse(await read("evidence/BN599_MR270_SOURCE_CHECK_20260927.json"));
const bn722 = JSON.parse(await read("evidence/BN722_PUBLIC_SOURCE_20260928.json"));
const bn722Edition = bnBeforeComplete; // Historical source-only checkpoint, not the current reader.
check(bn722.inventory_objects === 1444 && bn722.unit_ids === 722 && bn722.failures.length === 0, "Bengali722 needs all frozen and target source objects, not an owner count alone");
check(bn722Edition.public_source_checkpoint_commit === bn722.commit && bn722.reader_units === 299 && !bn722.new_reader_release && !bn722.linguistic_certification, "Bengali722 source completion must not inflate reader coverage or linguistic assurance");
check(bnMrCurrent.bn.changed_units === 85 && bnMrCurrent.bn.changed_segments === 844 && bnMrCurrent.bn.changed_language_segments === 798, 'Bengali599 requires actual85-unit /844-segment replay');
check(bnMrCurrent.mr.targets_verified === 270 && bnMrCurrent.mr.reader_units === 194 && bnMrCurrent.mr.changed_segments === 634 && bnMrCurrent.mr.changed_language_segments === null, 'Marathi270 source coverage must not inflate readers or assert an unmeasured linguistic delta');
check(bnMrCurrent.mr_public_tree.selected_local_git_objects_matching_public_blob_ids === 999 && bnMrCurrent.mr_public_tree.anonymous_raw_byte_checks.length === 4, 'Marathi270 needs public Git object identities and bounded raw byte evidence');
check(bnMrCurrent.bn.canon_sample.original_page_visually_inspected && bnMrCurrent.mr.canon_sample.original_page_visually_inspected && !bnMrCurrent.full_semantic_reaudit && !bnMrCurrent.new_reader_release, 'Source/canon samples must retain their bounded scope');
check(bnMrCurrent.mr.pending_reader_defect.released194_contains_sample === false, 'Pending Marathi reader defect must not be attributed to the released194 reader');
for(const lane of ['bn','mr'])check(bnMrCurrent[lane].failures.length===0 && bnMrCurrent[lane].frozen_sources_verified===722, 'Each source checkpoint needs complete frozen-source identity replay');
const telugu410 = JSON.parse(await read("evidence/TE410_PUBLIC_SOURCE_MIRROR_20260926.json"));
check(telugu410.changed_units === 16 && telugu410.changed_segments === 247 && telugu410.changed_linguistic_segments === 141 && telugu410.failures.length === 0, "Telugu410 requires actual changed-segment replay");
check(telugu410.zenodo.latest_record === 22309234 && telugu410.zenodo.reader276_mirror === false, "Preserve the historical Telugu mirror-gap finding");
const teluguZenodoMirror = JSON.parse(await read(telugu276.evidence.zenodo_mirror_readback));
check(telugu276.version_doi === '10.5281/zenodo.22726674' && teluguZenodoMirror.record_id === 22726674 && teluguZenodoMirror.anonymous && teluguZenodoMirror.files.length === 20 && teluguZenodoMirror.files.every(f => f.matches), 'Telugu276 Zenodo mirror requires all twenty exact public matches');
for (const asset of telugu276.ordered_downloads) check(teluguZenodoMirror.files.some(f => f.name === asset.name && f.bytes === asset.bytes && f.sha256 === asset.sha256), 'Telugu mirror must retain the exact reader/source download identities');
const bnTeSegments = JSON.parse(await read("evidence/BN_TE_CHANGED_SEGMENTS_20260926.json"));
for (const [lane, units, segments] of [['bn',106,1123],['te',50,677]]) {
  const replay=bnTeSegments.lanes.find(row=>row.lane===lane);
  check(replay.changed_units===units && replay.segments_checked===segments && replay.failures.length===0, `${lane}: all changed units need a segment and canon-ID replay`);
}
const taBeforeComplete = JSON.parse(await read("evidence/TAMIL_BEFORE_COMPLETE_20260928.json"));
for (const [id, lane] of [["openlogic-bn-beng-in","bn"],["openlogic-ta-taml-in","ta"],["openlogic-te-telu-in","te"],["openlogic-ps-arab-pk","ps"]]) {
  const edition = lane === "ta" ? taBeforeComplete : lane === "bn" ? bnBeforeComplete : lane === "te" ? teBeforeComplete : catalogue.editions.find(item => item.id === id);
  const source = lane === 'ps' ? ps648Evidence : lane === 'te' ? telugu410 : lane === 'bn' ? bn722 : currentSources.checkpoints.find(item => item.lane === lane);
  check(source.failures.length === 0 && source.frozen_sources_verified === 722 && source.targets_verified === edition.source_units_translated, `${id}: source progress requires verified frozen sources and mapped targets`);
  check(source.commit === edition.public_source_checkpoint.commit && (lane === "bn" ? source.reader_units === 299 && edition.html_reader_units === 722 : source.reader_units === edition.standalone_reader_units) && source.full_semantic_reaudit === false, `${id}: preserve historical source checkpoint scope and separately verify newer readers`);
}
const teComplete = catalogue.editions.find(item=>item.id === "openlogic-te-telu-in");
const teCompleteEvidence = JSON.parse(await read("evidence/TE722_COMPLETE_SOURCE_MANAGER_20260928.json"));
check(teComplete.release_tag === "v1.0.1-full-olp0722" && teComplete.version_doi === "10.5281/zenodo.23019353", "Telugu complete release/source-addendum identity");
check(["source_units_translated","standalone_reader_units","pdf_reader_units","html_reader_units","epub_reader_units","zenodo_reader_units"].every(k=>teComplete[k]===722), "Telugu full722 source and reader scopes");
check(teComplete.online_html_reader_units === 23 && teComplete.html_delivery_kind === "offline-ZIP" && teComplete.public_reader === teComplete.readers[0].url && teComplete.readers[0].format === "PDF", "Keep old23-unit online Telugu sample distinct");
check(teComplete.ordered_downloads.slice(0,3).map(x=>x.format).join(",")==="PDF,TEX,ZIP", "Telugu complete reader/source order");
check(teCompleteEvidence.files.length===4 && teCompleteEvidence.files.every(x=>x.matches) && teCompleteEvidence.retained_reader_readbacks.length===16 && teCompleteEvidence.retained_reader_readbacks.every(x=>x.matches) && teCompleteEvidence.inherited_zenodo_files_unchanged===28 && teCompleteEvidence.zenodo_files===30, "Telugu public source bytes and inherited preservation");
for(const asset of teComplete.ordered_downloads) check([...teCompleteEvidence.files,...teCompleteEvidence.retained_reader_readbacks].some(x=>x.host==="github" && x.url===asset.url && x.bytes===asset.bytes && x.sha256===asset.sha256 && x.matches), "Telugu exact proven download");
check(["source_files","target_files","body_spans"].every(k=>teCompleteEvidence.source_replay[k]===722) && teCompleteEvidence.source_replay.members===3328 && teCompleteEvidence.source_replay.figure_files===105 && teCompleteEvidence.source_replay.bad_crc_member===null && Object.values(teCompleteEvidence.source_replay.required_dependencies).every(Boolean) && teCompleteEvidence.failures.length===0, "Telugu complete editable source/dependencies");
check(teCompleteEvidence.source_replay.direct_tex_is_pdf_build_driver===false && teCompleteEvidence.full_linguistic_certification===false && teComplete.evidence.review_localization_status==="identified-localization-defects-closed", "Preserve Telugu build-route and bounded review-closure limits");
const teReviewCheck = JSON.parse(await read(teComplete.evidence.review_localization_check));
check(teReviewCheck.public_file_readbacks.length===12 && teReviewCheck.public_file_readbacks.every(x=>x.matches&&x.anonymous) && teReviewCheck.structure.decisions===1117 && teReviewCheck.structure.occurrences===2446 && teReviewCheck.independent_checks.conservative_confidence_repairs_retained===6, "Telugu review closure needs exact public files and preserved decisions/confidence");
check(teReviewCheck.localization_status==="identified-localization-defects-closed" && teReviewCheck.structure.new_rationales===78 && teReviewCheck.structure.early_alternatives===135 && teReviewCheck.structure.early_authority_uses===578 && teReviewCheck.independent_checks.failed===0 && teReviewCheck.bounds.full_linguistic_certification===false && teComplete.evidence.confidence_reconciliation_verified===true, "Accept the verified Telugu localization repair without claiming full linguistic certification");
const teWebCheck = JSON.parse(await read(teComplete.evidence.review_web_check));
check(teReviewCheck.open_findings.some(f=>f.id==='TE-REVIEW-WEB-01') && teWebCheck.closed_findings.includes('TE-REVIEW-WEB-01') && teComplete.evidence.review_web_access_status==='paginated-native-review-public-verified', "Retain the historical preview finding and its verified web repair");
check(teWebCheck.structure.decisions===1117 && teWebCheck.structure.occurrences===2446 && teWebCheck.structure.priority===70 && teWebCheck.structure.full_pages===23 && teWebCheck.structure.priority_pages===2 && teWebCheck.structure.failures===0, "Telugu web review retains complete decision and locator scope");
check(teWebCheck.public_file_readbacks.length===28 && teWebCheck.public_file_readbacks.every(f=>f.matches&&f.anonymous) && teWebCheck.article_preservation.every(f=>f.articles_unchanged) && teWebCheck.bounds.full_linguistic_certification===false && teWebCheck.rendered_checks.exact_ai_disclosure, "Telugu web review requires public byte identity, unchanged content and honest provenance");
check(teComplete.related_editions.some(x=>x.url===teWebCheck.review_url) && teComplete.limitations.some(t=>t.includes('23 చదవదగిన వెబ్')), "Link the readable Telugu review from the language card");
check(!/[\u0980-\u09ff]/u.test(teComplete.limitations.join(" ")), "No accidental Bengali script in Telugu limitations");
const tamilChapter = catalogue.editions.find(item => item.id === "openlogic-ta-taml-in").supplementary_downloads[0];
const tamilChapterEvidence = JSON.parse(await read("evidence/TAMIL_ORDINALS_SOURCE_COMPANION_20260921.json"));
check(tamilChapter.source_units === 11 && tamilChapter.scope_kind === "chapter", "Tamil Ordinals is a separate eleven-unit chapter");
check(tamilChapter.downloads.map(item => item.format).join(",") === "PDF,TEX,ZIP", "Separate chapter must keep PDF/direct-LaTeX/source-ZIP order");
check(tamilChapterEvidence.failures.length === 0 && tamilChapterEvidence.reader_units.length === 11 && tamilChapterEvidence.support.length === 14 && tamilChapterEvidence.reachable_units === 11 && tamilChapterEvidence.master_inverse_reconstruction_exact, "Tamil chapter requires actual payload, dependency and master checks");
check(tamilChapterEvidence.reader_units.every(item => item.exact_blob_match) && tamilChapterEvidence.support.every(item => item.source_and_declared_rewrite_match), "All Tamil embedded source payloads must match their declared originals");
for (const [index, evidenceKey] of [[0,"pdf"],[1,"direct_tex"],[2,"archive"]]) {
  const actual = tamilChapter.downloads[index], expected = tamilChapterEvidence[evidenceKey];
  check(actual.url === expected.url && actual.bytes === expected.bytes && actual.sha256 === expected.sha256, "Tamil chapter download must match anonymous readback");
}
check(script.includes("edition.supplementary_downloads") && script.includes('chapter.className = "download-supplement"'), "Additional chapter downloads must use a collapsed native disclosure");
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

check(gu199Delivery.files.length === 16 && gu199Delivery.files.every(x => x.matches), "Gujarati199 needs all sixteen mirror matches");
check(gu199Checks.frozen_sources_verified === 722 && gu199Checks.native_targets === 199 && gu199Checks.failures.length === 0, "Gujarati199 source inventory must match its scope");
check(gu199Checks.direct_fulltext_matches_download && gu199Checks.fulltext_unresolved_body_imports.length === 0 && gu199Delivery.files.some(x => x.sha256 === gu199Checks.direct_fulltext_sha256 && x.matches), "Historical Gujarati199 needs exact direct full-text source identity");

const dutchSourcePublication = JSON.parse(await read('evidence/DUTCH_PAIRED160_SOURCE_PUBLIC_20260926.json'));
const dutchPublication = JSON.parse(await read('evidence/DUTCH_READERS160_PUBLIC_20260927.json'));
const arabic = catalogue.editions.find(item => item.id === 'openlogic-ar');
const arPublic = JSON.parse(await read('evidence/ARABIC_COMPLETE_EPUB_PUBLIC_20260926.json'));
const arEpubSuccessor = JSON.parse(await read(arabic.evidence.epub_provenance_correction));
const arCorrectedEpub = JSON.parse(await read(arabic.evidence.corrected_epubs));
check(createHash('sha256').update(await read(arabic.evidence.manager_public_readback)).digest('hex') === arabic.evidence.manager_public_readback_sha256, 'Arabic public evidence hash must identify the exact published JSON bytes');
const arPackages = JSON.parse(await read(arabic.evidence.package_checks));
check(arabic.metadata_language === 'ar' && arabic.metadata_direction === 'rtl' && arabic.search_aliases.includes('Arabic'), 'Arabic native metadata must remain discoverable');
check(arabic.ui_labels.downloads === 'التنزيلات' && script.includes('edition.ui_labels?.downloads'), 'Arabic download-group accessibility names must be localized');
check(arabic.epub_version_doi === arCorrectedEpub.doi && arabic.epub_release_tag === arCorrectedEpub.release_tag, 'Arabic corrected EPUB lineage mismatch');
check(arCorrectedEpub.files.length === 14 && arCorrectedEpub.files.every(f => f.anonymous && f.matches) && arCorrectedEpub.checks.failures.length === 0 && arCorrectedEpub.visual.pass, 'Arabic corrected EPUB/source assets need fourteen mirror matches and resolved independent checks');
check(arCorrectedEpub.inventory.files === 100 && arCorrectedEpub.inventory.unchanged === 93 && arCorrectedEpub.source_package.manifest_members === 2493 && arCorrectedEpub.source_package.source_units_per_msa === 722, 'Arabic new EPUB source package and preserved100-file archive');
check(arPublic.anonymous && arPublic.files.length === 20 && arPublic.files.every(f => f.matches), 'Arabic full EPUB release needs ten exact assets on both mirrors');
const arFull = arabic.readers.filter(r => r.format === 'EPUB' && r.scope_kind === 'complete');
check(arFull.length === 3 && arFull.every(r => r.source_units === 722), 'Arabic requires three explicitly complete EPUB profiles');
check(arPackages.status === 'PASS' && arPackages.failures.length === 0 && Object.keys(arPackages.profiles).length === 3, 'Arabic independent package checks failed');
for (const r of arFull) {
  const q = arPackages.profiles[r.profile];
  check(q.source_units === 722 && q.cumulative_bodies_replayed === 722 && q.cold_replay_matches && q.cold_replay_sha256 === arPublic.files.find(f => f.name === r.name)?.sha256 && q.broken_internal_links.length === 0, `Arabic ${r.profile}: incomplete package proof`);
  if (r.profile !== 'classical') {
    const f = arCorrectedEpub.files.find(x => x.host === 'github' && x.name === r.name);
    const p = arCorrectedEpub.profiles.find(x => x.profile === r.profile);
    check(f?.sha256 === r.sha256 && f.bytes === r.bytes && f.url === r.url && r.mirror_doi === arCorrectedEpub.doi, 'Arabic corrected EPUB identity: '+r.profile);
    check(p?.source_units === 722 && p.spine_items === 812 && p.documents === 812 && p.unchanged_members === 816 && p.changed_members.join(',') === 'OEBPS/modern-reader-3-7-3.xhtml,OEBPS/package.opf,OEBPS/provenance.xhtml' && p.proof_trees_preserved === 6 && p.original_formula_objects_preserved === 73 && p.formula_objects_added === 1 && p.byte_identical_independent_rebuild, 'Arabic bounded correction and exact rebuild: '+r.profile);
    continue;
  }
  const successor = arEpubSuccessor.files.find(f => f.name === r.name);
  const profile = arEpubSuccessor.profiles.find(p => p.profile === r.profile);
  check(successor?.sha256 === r.sha256 && successor.bytes === r.bytes && successor.github.matches && successor.zenodo.matches && successor.github.url === r.url && r.mirror_doi === arEpubSuccessor.doi, 'Arabic successor mirror identity mismatch: '+r.profile);
  check(profile.archive_members === 819 && profile.unchanged_members === 817 && profile.changed_members.join(',') === 'OEBPS/package.opf,OEBPS/provenance.xhtml' && profile.body_and_mathml_changed === false, 'Arabic inherited body preservation not established: '+r.profile);
  check(arEpubSuccessor.source_replay.epub_replays.some(p => p.profile === r.profile && p.sha256 === r.sha256 && p.independent_in_memory_rebuild_matches && p.exact_expanded_source_match), 'Arabic exact source replay missing: '+r.profile);
}
const arCurrent = JSON.parse(await read('evidence/ARABIC_READERS_REVIEW_PUBLIC_20260927.json'));
const arRepair = JSON.parse(await read('evidence/AR_CLASSICAL_REPAIR_20260928.json'));
const arMsa = JSON.parse(await read(arabic.evidence.current_msa_pdf));
check(arMsa.files.length === 26 && arMsa.files.every(f => f.anonymous && f.matches) && arMsa.package_failures.length === 0 && arMsa.scope_failures.length === 0, 'Current MSA readers need exact bytes on both mirrors and passing source replay');
check(arMsa.packages.length === 2 && arMsa.packages.every(p => p.members_verified === 791 && p.effective_source_units_verified === 722) && arMsa.graphs.every(g => g.unique_unit_routes === 722 && g.exact_tex_bodies === 722 && g.partitions.join(',') === '642,80'), 'Each corrected MSA reader needs all722 exact bodies in its complete cumulative source and source ZIP');
check(arMsa.preview.default_preview === '00_OPENLOGIC_ar_R3_MSA_INTERNATIONAL.pdf' && arMsa.inventory.files === 100 && arMsa.inventory.unchanged_since_prior_readback, 'Current MSA archive needs the pertinent PDF preview and preserved inventory');
check(arMsa.visual.physical_pages_each.join(',') === '293,294' && !arMsa.full_linguistic_certification && !arMsa.epub_contains_these_corrections && arMsa.classical_reader_unchanged, 'Bounded visual check must not imply whole-corpus or EPUB revalidation');
check(arRepair.failures.length === 0 && arRepair.files.length === 5 && arRepair.files.every(a => a.anonymous && a.github.matches && a.zenodo.matches), 'Classical repair needs five exact anonymous mirror identities');
check(arRepair.source_package.members_rehashed === 1525 && arRepair.source_package.cumulative_byte_ranges_verified === 722 && arRepair.source_package.direct_tex_identical, 'Classical repair needs complete matching editable sources');
check(arRepair.public_file_count === 98 && arRepair.inherited_files_unchanged === 93 && arRepair.full_linguistic_certification === false, 'Preserve inherited access and bounded audit scope');
check(arCurrent.byte_and_source_package_status === 'PASS' && arCurrent.assets.length === 13 && arCurrent.assets.every(a => a.github.matches && a.zenodo.matches), 'Arabic current assets require exact anonymous mirror identities');
check(arCurrent.packages.length === 3 && arCurrent.packages.every(p => p.direct_tex_identical && p.exact_0001_0722_ids && !p.manifest_mismatches.length), 'Three complete matching PDF source packages required');
check(arabic.ordered_downloads.map(r => r.format).join(',') === 'PDF,TEX,ZIP', 'Arabic primary PDF must have its matching direct TEX and source ZIP immediately after it');
check(arabic.supplementary_downloads.length === 5 && arabic.supplementary_downloads[4].downloads.some(d => d.url.endsWith('ar-olp-0722-complete-dual-notation-r2-20260903')), 'Historical Arabic reader access must be retained');
for (const group of [arabic.ordered_downloads, arabic.supplementary_downloads[1].downloads.slice(0, 3), arabic.supplementary_downloads[2].downloads.slice(0, 3)]) {
  check(group.map(a => a.format).join(',') === 'PDF,TEX,ZIP', 'Each Arabic PDF needs its own source pair in order');
  for (const asset of group) check([...arMsa.files.filter(f => f.host === 'github'), ...arRepair.files].some(a => a.name === asset.name && a.sha256 === asset.sha256 && a.bytes === asset.bytes && (a.url || a.github.url) === asset.url), 'Arabic PDF/source identity mismatch');
}
check(arabic.readers.filter(r => r.format === 'PDF' && r.scope_kind === 'complete').length === 3, 'Three current complete Arabic PDF readers required');
check(arabic.reviewable_decisions === 1095 && arCurrent.review_index.rows === 1095 && arCurrent.review_index.unique_ids === 1095 && arabic.human_review_complete === false, 'Complete Arabic review directory must not imply human approval');
const arReviewRepair = JSON.parse(await read('evidence/ARABIC_REVIEW_CORRECTIONS_20260930.json'));
const arReadable = JSON.parse(await read('evidence/ARABIC_READABLE_REVIEW_20260930.json'));
check(arReadable.files.length === 14 && arReadable.files.every(f=>f.anonymous && f.matches) && arReadable.pages.length === 150 && arReadable.pages.every(f=>f.anonymous && f.matches), 'Arabic readable review needs both asset mirrors and all150 page identities');
check(arReadable.all_1095_rows_preserved && arReadable.all_split_card_payloads_preserved && arReadable.review_decisions === 1095 && arReadable.large_cards_preserved === 37 && arReadable.inherited_inventory_unchanged === 93 && arReadable.public_file_count === 100 && !arReadable.full_linguistic_certification, 'Arabic complete review preservation and bounded semantic claim');
const arFunctions = JSON.parse(await read('evidence/ARABIC_FUNCTION_REVIEW_20260930.json'));
check(arFunctions.files.length === 14 && arFunctions.files.every(f => f.anonymous && f.matches) && arFunctions.failures.length === 0, 'Arabic function review requires exact anonymous mirror readbacks');
check(arFunctions.all_1095_ids_preserved && arFunctions.review_decisions === 1095 && arFunctions.changed_decisions.length === 3 && arFunctions.unchanged_decisions === 1092 && arFunctions.inherited_inventory_unchanged === 93 && arFunctions.public_file_count === 100, 'Arabic function review must preserve prior decisions and inherited inventory');
check(arFunctions.source_files.length === 3 && arFunctions.source_files.every(f => f.matches && f.normalized_snapshot_equal) && arFunctions.canon_sample.physical_pages_viewed.join(',') === '69,361,703' && !arFunctions.full_linguistic_certification && arFunctions.translation_body_edits === 0, 'Arabic bounded source/canon evidence and unchanged reader scope');
const arContext = JSON.parse(await read('evidence/ARABIC_CONTEXT_PROOF_REVIEW_20260930.json'));
check(arabic.version_doi === arCorrectedEpub.doi && arabic.pdf_version_doi === arMsa.doi && arabic.release_tag === arMsa.release_tag && arabic.review_release_tag === arMsa.release_tag && arabic.previous_context_review_release_tag === arContext.release_tag && arabic.previous_function_review_release_tag === arFunctions.release_tag && arabic.previous_readable_review_release_tag === arReadable.release_tag, 'Arabic current and historical review identities');
check(arContext.files.length === 14 && arContext.files.every(f=>f.anonymous && f.matches) && arContext.failures.length === 0, 'Arabic context/proof review requires both anonymous asset mirrors');
check(arContext.all_1095_ids_preserved && arContext.all_original_occurrences_preserved && arContext.changed_decisions.length === 8 && arContext.unchanged_decisions === 1087 && arContext.recorded_locations_checked === 90, 'Arabic bounded review scope and occurrence preservation');
check(arContext.package_files_checked === 828 && arContext.package_crc_passed && arContext.inherited_inventory_unchanged === 93 && arContext.public_file_count === 100, 'Arabic source package and inherited access');
check(arContext.source_prose_corrections === 2 && arContext.source_inverse_reconstruction_passed && arContext.new_pdf_epub_builds === 0 && !arContext.full_linguistic_certification, 'Arabic public source repair is not a new reader build');
check(arabic.supplementary_downloads[3].note.includes('تضم نسختا PDF وEPUB المعياريتان الآن') && arabic.evidence.context_proof_review === 'evidence/ARABIC_CONTEXT_PROOF_REVIEW_20260930.json', 'Current corrected PDF and EPUB status must be reader-facing');
check(arReviewRepair.failures.length === 0 && arReviewRepair.files.length === 7 && arReviewRepair.pinned_source_inputs.length === 44 && arReviewRepair.pinned_source_inputs.every(p => p.anonymous && p.matches), 'Arabic review correction needs exact public assets and pinned source inputs');
check(arabic.previous_review_release_tag === arReviewRepair.release_tag && arReviewRepair.review_decisions === 1095 && arReviewRepair.corrected_explanations === 5 && arReviewRepair.full_linguistic_certification === false, 'Arabic review correction scope must remain explicit');
for (const item of arabic.supplementary_downloads[3].downloads.filter(x => x.name)) check(arMsa.files.some(f => f.host === 'github' && f.name === item.name && f.url === item.url && f.bytes === item.bytes && f.sha256 === item.sha256), 'Arabic corrected review download identity mismatch');
check(arabic.supplementary_downloads[3].downloads.some(d => d.url.endsWith('/SOL6_CORRECTIONS_AR.md')) && arabic.supplementary_downloads[4].downloads.some(d => d.url === arReviewRepair.historical_release), 'Arabic corrected explanations and historical review access both required');

check(arabic.status.includes('classical-fixed-name-repair-verified') && !arabic.status.includes('classical-pdf-rendering-correction-required') && arRepair.inspection.pdf_pages.join(',') === '33,404,1044', 'Repaired classical listing requires inspected pages');
check(arabic.pdf_version_doi === arMsa.doi && arabic.classical_pdf_version_doi === arRepair.doi && arabic.supplementary_downloads[2].downloads.slice(0, 3).every(asset => arRepair.files.some(f => f.name === asset.name && f.sha256 === asset.sha256 && f.github.url === asset.url)), 'Current MSA and classical PDF source pairs must retain their distinct verified lineages');
check(arabic.evidence.manager_public_readback === arabic.evidence.current_msa_pdf && arabic.evidence.epub_provenance_correction, 'Arabic card evidence must expose current PDFs and preserve EPUB evidence');
check(arEpubSuccessor.files.length === 4 && arEpubSuccessor.source_replay.manifest_members_verified === 2485 && arEpubSuccessor.source_replay.matching_direct_source_assets.length === 6, 'Arabic EPUB successor needs four exact changed assets and complete editable sources');
check(arabic.epub_source_text_date === '2026-09-30' && arabic.classical_epub_source_text_date === '2026-09-25' && arCorrectedEpub.full_linguistic_certification === false && arabic.epub_coverage_note.includes('إعادة فحص'), 'Arabic EPUB status must distinguish source dates and unfinished semantic review');
check(arabic.evidence.latest_zenodo_record === `https://zenodo.org/records/${arCorrectedEpub.record_id}`, 'Arabic latest archive pointer must match the verified EPUB successor');
check(!JSON.stringify(arabic.supplementary_downloads).includes('٢٩٧ ميغابايت'), 'Arabic source ZIP must not retain the obsolete 297 MB label');
check(arabic.limitations.slice(0, 5).some(text => text.includes('GPT-6 Sol') && text.includes('GPT-6.1 Sol') && text.includes('Ultra')), 'Rendered Arabic limitations must attribute EPUB conversion and provenance correction separately');
check(arabic.supplementary_downloads[4].downloads.some(d => d.url.endsWith(arPublic.release_tag)), 'Previous Arabic EPUB lineage must remain available');
check(arabic.readers.filter(r => r.scope_kind === 'chapter').length === 2 && arabic.readers.filter(r => r.scope_kind === 'historical' && r.format === 'PDF').length === 3, 'Preserve previous PDF identities and chapter samples');
check(arabic.readers.some(r => r.scope_kind === 'historical' && r.profile === 'classical' && r.known_rendering_issue === 'OLI-AR-CLASSICAL-LEN-RTL-20260927') && arabic.supplementary_downloads[4].downloads.some(d => d.url.endsWith('ar-olp-0722-classical-eastern-rtl-complete-20260926')), 'Historical defective classical release must remain accessible and identified');
const dutchCurrent = JSON.parse(await read('evidence/DUTCH_READERS192_PUBLIC_20260927.json'));
const ownership = JSON.parse(await read('catalogue/ownership.json'));
const dutchOwnership = ownership.commissioned_register_pairs?.find(item => item.pair_id === 'openlogic-nl-dual-register');
check(dutchOwnership?.owner_setup_state === 'established' && dutchOwnership.owner_task_id && dutchOwnership.state === 'partial-readers-published-full-edition-incomplete', 'Dutch ownership must not revert to unassigned or zero-coverage commission state');
check(dutchOwnership?.metadata_language === 'nl-NL' && dutchOwnership.status_label?.includes('192 van 722') && dutchOwnership.completion_verified === false, 'Dutch ownership must retain localized, explicitly partial published scope');
check(dutchOwnership?.evidence === 'evidence/DUTCH_READERS192_PUBLIC_20260927.json' && dutchOwnership.commission_evidence === 'evidence/DUTCH_DUAL_REGISTER_COMMISSION_20260906.json', 'Dutch ownership needs current publication evidence while retaining its historical commission');
check(dutchCurrent.package_checks.failures.length === 0 && dutchCurrent.package_checks.assets.length === 10, 'Dutch192 requires all ten exact package assets');
check(dutchCurrent.github.files.length === 10 && dutchCurrent.zenodo.files.length === 10 && [...dutchCurrent.github.files, ...dutchCurrent.zenodo.files].every(x => x.matches), 'Dutch192 needs ten anonymous matches on both mirrors');
check(dutchCurrent.html.length === 2 && dutchCurrent.html.every(x => x.matches && x.ordered_anchors === 192), 'Dutch192 needs two ordered 192-unit online readers');
check(dutchCurrent.package_checks.assets.filter(x => x.aligned_target_units_verified === 192 && x.direct_tex_identical).length === 2, 'Dutch192 direct LaTeX and paired source archives must match');
check(dutchCurrent.full_linguistic_certification === false && dutchCurrent.review_log.entries === 643, 'Dutch192 review ledger is not linguistic certification');
for (const id of ['openlogic-nl-standard', 'openlogic-nl-gewone-mensentaal']) {
  const edition = catalogue.editions.find(item => item.id === id);
  check(edition.source_units_translated === 192 && edition.standalone_reader_units === 192, `${id}: published reader scope must remain 192/722`);
  check(dutchOwnership?.owner_task_id === edition.owner_task_id && dutchOwnership.repository === edition.repository && dutchOwnership.release === edition.release && dutchOwnership.version_doi === edition.version_doi, `${id}: ownership routing and public lineage must match the edition catalogue`);
  check(dutchOwnership?.published_source_units_each === edition.source_units_translated && dutchOwnership.source_units_translated_each === edition.source_units_translated && dutchOwnership.public_reader_units_each === edition.standalone_reader_units && dutchOwnership.total_source_units === 722, `${id}: ownership published coverage must agree with the actual reader`);
  check(edition.profiles[0] === `${edition.standalone_reader_units} corresponderende broneenheden in twee registers`, `${id}: profile description must match published reader coverage`);
  check(edition.ordered_downloads.map(item => item.format).join(',') === 'TEX,ZIP,HTML,EPUB', `${id}: direct LaTeX, full source ZIP, online reader and EPUB required`);
  check(edition.version_doi === dutchCurrent.zenodo.doi && edition.release === dutchCurrent.github.release, `${id}: public lineage mismatch`);
  for (const asset of edition.ordered_downloads) {
    if (asset.format === 'HTML') check(dutchCurrent.html.some(item => item.url === asset.url && item.matches), `${id}: online-reader readback missing`);
    else for (const mirror of [dutchCurrent.github, dutchCurrent.zenodo]) check(mirror.files.some(item => item.name === asset.name && item.sha256 === asset.sha256 && item.bytes === asset.bytes && item.matches), `${id}: asset mirror identity missing`);
  }
  check(edition.epub_coverage_note.includes('192 van 722') && edition.epub_coverage_note.includes('Er is geen PDF'), `${id}: partial scope and absent PDF must remain explicit`);
  check(edition.readers.length === 2 && edition.readers.every(item => item.source_units === 192 && item.scope_kind === 'partial'), `${id}: no complete-reader claim permitted`);
  check(edition.search_aliases?.includes('Dutch') && edition.search_aliases?.includes('Nederlands'), `${id}: native and English names required`);
  check(edition.metadata_language === 'nl-NL', `${id}: Dutch metadata language required`);
}
check(dutchSourcePublication.github.anonymous_repository_files_verified === 933 && dutchSourcePublication.zenodo.files.length === 6 && dutchSourcePublication.zenodo.inherited_files_metadata_verified === 12, 'Historical Dutch source-publication receipt must remain intact');
check(dutchPublication.github.repository_files_verified === 44 && dutchPublication.github.assets.length === 8 && dutchPublication.zenodo.inherited_files_verified === 18, 'Dutch reader source and preservation evidence missing');
check(dutchPublication.html_compatibility.public_readback.length === 45 && dutchPublication.html_compatibility.qa.files.length === 4 && dutchPublication.html_compatibility.qa.files.every(item => item.text_identical && item.anchors_identical), 'Dutch HTML compatibility must preserve text, anchors and deployed bytes');
check(dutchPublication.github.public_readback.length === 8 && dutchPublication.zenodo.public_readback.length === 8 && dutchPublication.pages.public_readback.length === 42, 'Dutch reader release needs both mirrors and all deployed web files');
check([...dutchPublication.github.public_readback, ...dutchPublication.zenodo.public_readback, ...dutchPublication.pages.public_readback].every(item => item.anonymous && item.matches), 'Dutch public-byte check failed');

check(psV070.files.length === 12 && psV070.files.every(f => f.matches), "Pashto six assets must match on both mirrors");
check(psV070.package_checks.snapshots.source393.target_units_verified === 393 && psV070.package_checks.snapshots.release.target_units_verified === 362, "Pashto source scopes distinct");
check(psV070.package_checks.direct_tex.unit_ids === 321 && psV070.package_checks.epub.unit_ids === 321 && psV070.package_checks.epub.broken_internal_links.length === 0, "Pashto TEX and EPUB321 evidence");
check(psEdition.previous_v070_release_snapshot.limitations[0].includes("!A") && psEdition.metadata_direction === "rtl", "Historical Pashto warning must remain preserved");
check(psEdition.release_tag === psV071.release_tag && psEdition.status.includes("formula-repair-verified") && !psEdition.status.includes("formula-correction-required"), "Current Pashto card must link the verified corrected release");
check(psV071.files.length === 12 && psV071.files.every(f=>f.matches) && psV071.failures.length === 0, "Corrected Pashto assets need twelve anonymous byte matches");
check(psV071.source_package.frozen_matches_current === 722 && psV071.source_package.target_matches_current === 405 && psV071.source_package.direct_tex_matches && psV071.source_package.unit_ids === 321, "Pashto release source and cumulative reader scope must agree");
check(psV071.epub.unit_anchors === 321 && psV071.epub.exact_0001_0321 && psV071.epub.literal_metavariables_in_presentation.length === 0 && psV071.epub.broken_internal_links.length === 0, "Corrected Pashto EPUB needs complete scope and no literal metavariables");
check(psV071.source_checkpoint.public_files.length === 13 && psV071.source_checkpoint.public_files.every(f=>f.matches) && psV071.source_checkpoint.paired_files.length === 7 && psV071.source_checkpoint.paired_files.every(f=>f.matches), "Pashto481 new-source checkpoint needs bounded public/source identity evidence");
check(psV071.visual_sample.physical_pdf_pages.join(',') === '413,414' && psV071.visual_sample.literal_metavariables_absent && psV071.full_linguistic_certification === false, "Pashto repair closure must retain limited visual/linguistic scope");
check(/\.coverage-row strong\s*\{[^}]*direction:\s*ltr;[^}]*unicode-bidi:\s*isolate;/.test(css), "Coverage fractions must not reverse numerator and denominator in RTL cards");
check(psV070.formula_defect.visually_inspected_pdf_pages.join(",") === "413,414" && psV070.formula_defect.epub_presentation_candidates.length > 0, "Pashto warning needs rendered evidence");
for (const [id, tag, label] of [["openlogic-es", "es", "Lector completo"], ["openlogic-pt-br", "pt-BR", "Leitor completo"]]) {
  const edition = catalogue.editions.find(item => item.id === id);
  check(edition.metadata_language === tag && edition.status_label === `${label} · 722/722`, `${id}: localized complete-reader badge required`);
  check(edition.ui_labels?.evidence && edition.source_coverage_label && edition.epub_coverage_note?.includes("722/722"), `${id}: publication, coverage and format labels must remain explicit`);
  check(edition.status.includes("audit-needed") && edition.limitations.some(text => /canon|cânone/.test(text)), `${id}: reader inclusion must not erase review limitations`);
}
check(script.includes("evidence.public_reader_delivery || evidence.local_reader_closure"), "Current public-reader delivery must precede historical local-only evidence");
// Keep the secondary README entry points consistent with the live catalogue.
const currentReadme = await read("README.md");
const pnbReadmeRow = currentReadme.split("\n").find(line => line.startsWith("| Punjabi (Pakistan, Shahmukhi) |"));
check(pnbReadmeRow?.includes(`**${punjabi.source_units_translated}/722**`) && pnbReadmeRow.includes(`**${punjabi.standalone_reader_units}-unit**`), "Punjabi README must distinguish the current rechecked source from the released reader");
check(pnbReadmeRow?.includes(punjabi.release) && pnbReadmeRow.includes(punjabi.version_doi) && pnbReadmeRow.includes(punjabi.public_source_checkpoint_commit), "Punjabi README must link current release, DOI and public source checkpoint");
check(currentReadme.includes("The historical [Punjabi 70-unit replay]") && !currentReadme.includes("The current [Punjabi 70-unit replay]"), "Superseded Punjabi structural evidence must not be presented as current linguistic acceptance");
const guReadmeRow = currentReadme.split("\n").find(line => line.startsWith("| ગુજરાતી |"));
const currentGu = catalogue.editions.find(item => item.id === "openlogic-gu-gujr-in");
check(guReadmeRow?.includes(`${currentGu.standalone_reader_units}/722`) && guReadmeRow.includes(currentGu.version_doi), "Gujarati README must use the current reader scope and DOI");
check(currentGu.ordered_downloads.filter(item => ["PDF", "EPUB"].includes(item.format) || item.role === "complete-cumulative-full-text").every(item => guReadmeRow?.includes(item.url)), "Gujarati README must use the published current reader/direct-source links");
check(currentReadme.includes("Bengali, Telugu and Marathi now have complete 722-unit EPUBs.") && !currentReadme.includes("Javanese, Marathi, Pashto and Punjabi"), "EPUB summary must not call the full Marathi reader partial");
check(currentReadme.includes("https://kokunoyumeto.github.io/OpenLogic-te-Telu-IN/review/") && !currentReadme.includes("పూర్తి నిర్ణయాల తెలుగు సమీక్షా వివరణలు ఇంకా సిద్ధమవుతున్నాయి") && !currentReadme.includes("రెండు నమ్మకస్థాయి అసంగతతల సవరణ ఇంకా అవసరం"), "Telugu README must link the completed native review and retire resolved findings");
check(ps500.status.includes(`partial-source-${ps500.source_units_translated}/722`), "Pashto source status tag must agree with its verified count");
const result = {
  status: failures.length ? "FAIL" : "PASS",
  failures,
  editions: catalogue.editions.length,
  standalone_722_readers: catalogue.editions.filter(item => item.standalone_reader_units === 722).length,
  source_722_editions: catalogue.editions.filter(item => item.source_units_translated === 722).length
};
console.log(JSON.stringify(result));
if (failures.length) process.exit(1);
