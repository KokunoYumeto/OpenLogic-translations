const TOTAL_UNITS = 722;

const nativeNames = {
  "ar": "العربية",
  "fa-IR": "فارسی",
  "hi-Deva-IN": "हिन्दी",
  "id-Latn-ID": "Bahasa Indonesia",
  "zh-Hans-CN": "简体中文",
  "tr": "Türkçe",
  "es": "Español",
  "pt-BR": "Português do Brasil",
  "art-x-interturkic": "Inter-Turkic",
  "isv": "Medžuslovjansky",
  "art-x-interfarsi": "Inter-Farsi",
  "art-x-romance": "Interlingua Romance",
  "pnb-Arab-PK": "پنجابی",
  "jv-Latn-ID": "Basa Jawa",
  "gu-Gujr-IN": "ગુજરાતી",
  "mr-Deva-IN": "मराठी",
  "bn-Beng-IN": "বাংলা",
  "ps-Arab-PK": "پښتو",
  "ta-Taml-IN": "தமிழ்",
  "te-Telu-IN": "తెలుగు"
};

const rtlTags = new Set(["ar", "fa-IR", "art-x-interfarsi", "pnb-Arab-PK", "ps-Arab-PK"]);
const grid = document.querySelector("#edition-grid");
const summary = document.querySelector("#catalogue-summary");
const select = document.querySelector("#language-select");
const search = document.querySelector("#search");
const emptyState = document.querySelector("#empty-state");
const clearFilters = document.querySelector("#clear-filters");
const filterButtons = [...document.querySelectorAll(".filter")];

let editions = [];
let activeFilter = "all";

function safeLink(value) {
  if (!value) return null;
  try {
    const url = new URL(value, window.location.href);
    return ["https:", "http:"].includes(url.protocol) ? url.href : null;
  } catch {
    return null;
  }
}

function editionClass(edition) {
  const statuses = (edition.status || []).join(" ");
  if (edition.standalone_reader_units === TOTAL_UNITS || statuses.includes("published-constructed-722")) {
    return "complete";
  }
  if (edition.source_units_translated === TOTAL_UNITS) return "source-complete";
  if (Number.isFinite(edition.source_units_translated) && edition.source_units_translated > 0) return "partial";
  return "research";
}

function classLabel(edition, state) {
  if ((edition.status || []).join(" ").includes("published-constructed-722")) return "Constructed 722";
  return {
    "complete": "Complete reader",
    "source-complete": "Source complete",
    "partial": "In progress",
    "research": "Research scaffold"
  }[state];
}

function units(value) {
  return Number.isFinite(value) ? value : null;
}

function coverageRow(label, value) {
  const row = document.createElement("div");
  row.className = "coverage-row";
  const name = document.createElement("span");
  name.textContent = label;
  const amount = document.createElement("strong");
  amount.textContent = value === null ? "Not yet claimed" : `${value} / ${TOTAL_UNITS}`;
  const track = document.createElement("span");
  track.className = "track";
  track.setAttribute("role", "progressbar");
  track.setAttribute("aria-label", `${label}: ${amount.textContent}`);
  track.setAttribute("aria-valuemin", "0");
  track.setAttribute("aria-valuemax", String(TOTAL_UNITS));
  track.setAttribute("aria-valuenow", String(value || 0));
  const fill = document.createElement("i");
  fill.style.setProperty("--coverage", `${Math.max(0, Math.min(100, ((value || 0) / TOTAL_UNITS) * 100))}%`);
  track.append(fill);
  row.append(name, amount, track);
  return row;
}

function link(label, href, primary = false) {
  const safe = safeLink(href);
  if (!safe) return null;
  const anchor = document.createElement("a");
  anchor.href = safe;
  anchor.textContent = label;
  anchor.target = "_blank";
  anchor.rel = "noreferrer";
  if (primary) anchor.className = "primary";
  return anchor;
}

function localEvidenceLink(edition) {
  const evidence = edition.evidence || {};
  const relative = evidence.manager_public_readback || evidence.public_readback || evidence.source_checkpoint_readback;
  if (!relative || /^(?:[a-z]+:|\/)/i.test(relative) || relative.includes("..")) return null;
  const anchor = document.createElement("a");
  anchor.href = relative;
  anchor.textContent = "Evidence";
  return anchor;
}

function cardFor(edition) {
  const state = editionClass(edition);
  const card = document.createElement("article");
  card.className = "edition-card";
  card.id = edition.id;
  card.tabIndex = -1;
  card.dataset.state = state;
  card.dataset.script = (edition.scripts || []).join(" · ") || "—";
  card.dataset.search = [
    edition.name,
    edition.language_tag,
    nativeNames[edition.language_tag],
    ...(edition.scripts || []),
    ...(edition.profiles || []),
    edition.semantic_layer
  ].filter(Boolean).join(" ").toLocaleLowerCase();

  const topline = document.createElement("div");
  topline.className = "card-topline";
  const tag = document.createElement("span");
  tag.className = "language-tag";
  tag.textContent = edition.language_tag || "und";
  const badge = document.createElement("span");
  badge.className = `status-badge status-${state}`;
  badge.textContent = classLabel(edition, state);
  topline.append(tag, badge);

  const native = document.createElement("p");
  native.className = "native-name";
  native.lang = edition.language_tag || "und";
  native.dir = rtlTags.has(edition.language_tag) ? "rtl" : "auto";
  native.textContent = nativeNames[edition.language_tag] || "\u00a0";

  const title = document.createElement("h3");
  title.textContent = edition.name;
  const layer = document.createElement("p");
  layer.className = "layer";
  layer.textContent = edition.semantic_layer || (edition.constructed ? "Constructed research register" : "Scholarly translation edition");

  const coverage = document.createElement("div");
  coverage.className = "coverage";
  coverage.append(
    coverageRow("Translated source files", units(edition.source_units_translated)),
    coverageRow("Standalone reader", units(edition.standalone_reader_units))
  );

  const actions = document.createElement("div");
  actions.className = "actions";
  const readerUrl = (edition.readers || []).find(item => item.url)?.url;
  const primary = link(readerUrl ? "Read / download" : "Open release", readerUrl || edition.release, true);
  const repository = link("Repository", edition.repository, !primary);
  const doi = link("DOI", edition.version_doi ? `https://doi.org/${edition.version_doi}` : edition.concept_doi ? `https://doi.org/${edition.concept_doi}` : null);
  const evidence = localEvidenceLink(edition);
  [primary, repository, doi, evidence].filter(Boolean).forEach(item => actions.append(item));

  const details = document.createElement("details");
  const detailsSummary = document.createElement("summary");
  detailsSummary.textContent = "Profiles and known limits";
  details.append(detailsSummary);
  const items = [...(edition.profiles || []), ...(edition.limitations || [])];
  if (items.length) {
    const list = document.createElement("ul");
    items.slice(0, 8).forEach(item => {
      const li = document.createElement("li");
      li.textContent = item;
      list.append(li);
    });
    details.append(list);
  } else {
    const note = document.createElement("p");
    note.textContent = "No additional profile note is recorded in the current catalogue.";
    details.append(note);
  }

  card.append(topline, native, title, layer, coverage, actions, details);
  return card;
}

function render() {
  const query = search.value.trim().toLocaleLowerCase();
  let visible = 0;
  [...grid.children].forEach(card => {
    const matchesFilter = activeFilter === "all" || card.dataset.state === activeFilter;
    const matchesSearch = !query || card.dataset.search.includes(query);
    card.hidden = !(matchesFilter && matchesSearch);
    if (!card.hidden) visible += 1;
  });
  summary.textContent = `${visible} of ${editions.length} editions shown. Coverage is read from the live machine catalogue.`;
  emptyState.hidden = visible !== 0;
}

function selectEdition(id) {
  if (!id) return;
  activeFilter = "all";
  search.value = "";
  filterButtons.forEach(button => {
    const active = button.dataset.filter === "all";
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  render();
  const card = document.getElementById(id);
  if (!card) return;
  document.querySelectorAll(".edition-card.focused").forEach(item => item.classList.remove("focused"));
  card.classList.add("focused");
  card.scrollIntoView({ behavior: "smooth", block: "center" });
  window.setTimeout(() => card.focus({ preventScroll: true }), 350);
  history.replaceState(null, "", `#${id}`);
}

async function start() {
  try {
    const response = await fetch("catalogue/editions.json", { cache: "no-cache" });
    if (!response.ok) throw new Error(`Catalogue request failed: ${response.status}`);
    const data = await response.json();
    if (!Array.isArray(data.editions)) throw new Error("Catalogue has no editions array");
    editions = data.editions;
    editions.forEach(edition => {
      grid.append(cardFor(edition));
      const option = document.createElement("option");
      option.value = edition.id;
      const native = nativeNames[edition.language_tag];
      option.textContent = native && native !== edition.name ? `${edition.name} — ${native}` : edition.name;
      select.append(option);
    });
    grid.setAttribute("aria-busy", "false");
    render();
    if (location.hash) {
      const id = decodeURIComponent(location.hash.slice(1));
      if (editions.some(edition => edition.id === id)) {
        select.value = id;
        window.setTimeout(() => selectEdition(id), 0);
      }
    }
  } catch (error) {
    grid.setAttribute("aria-busy", "false");
    summary.textContent = "The interactive catalogue could not load.";
    const message = document.createElement("div");
    message.className = "noscript-card";
    const heading = document.createElement("h3");
    heading.textContent = "Catalogue temporarily unavailable";
    const paragraph = document.createElement("p");
    paragraph.append("Use the ");
    const plain = document.createElement("a");
    plain.href = "README.md#read-or-inspect-an-edition";
    plain.textContent = "plain-language edition table";
    paragraph.append(plain, " while this view recovers.");
    message.append(heading, paragraph);
    grid.append(message);
    console.error(error);
  }
}

select.addEventListener("change", event => selectEdition(event.target.value));
search.addEventListener("input", render);
filterButtons.forEach(button => {
  button.addEventListener("click", () => {
    activeFilter = button.dataset.filter;
    filterButtons.forEach(item => {
      const active = item === button;
      item.classList.toggle("active", active);
      item.setAttribute("aria-pressed", String(active));
    });
    render();
  });
});
clearFilters.addEventListener("click", () => {
  search.value = "";
  activeFilter = "all";
  filterButtons[0].click();
  search.focus();
});

start();
