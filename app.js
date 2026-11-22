/* Annotationes — the Spiritual Exercises in the twentieth century.
   A static single-page apparatus: the text of the Exercises paragraph by
   paragraph at the centre, the century's glosses in the margin. No server,
   no third-party requests; preferences live in localStorage when available. */
"use strict";

const view = document.getElementById("view");
const narrow = window.matchMedia("(max-width: 980px)");
const D = { works: [], byWork: {}, glosses: [], ex: null, units: {}, sections: [], longridge: null };

const TIERS = {
  A: "Full text here (public domain)",
  B: "Free elsewhere, linked",
  C: "Own copy (anchors only)",
  D: "Reference only",
};
const LANGS = { de: "German", en: "English", es: "Spanish", fr: "French", it: "Italian", la: "Latin" };
const GENRES = {
  commentary: "Commentary", translation: "Translation", magisterium: "Magisterium", journal: "Journal",
  psychology: "Psychology", philosophy: "Philosophy & theory", literature: "Literature", history: "History",
  scholarship: "Later scholarship",
};
const BASIS = {
  read: "passage read and assigned",
  section: "the commentary's own section, mapped onto the grid",
  matched: "placed by matching the author's Spanish text to the autograph",
  page: "placed by the page that carries the note's call (page-exact, not paragraph-exact)",
  toc: "assigned from the table of contents",
  index: "assigned from the book's own index",
  title: "assigned from the article title",
};

/* ---------- small helpers ---------- */
const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
function el(html) { const t = document.createElement("template"); t.innerHTML = html.trim(); return t.content.firstElementChild; }
function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } return null; }
const range = s => s ? (s[0] === s[1] ? `[${s[0]}]` : `[${s[0]}]–[${s[1]}]`) : "the book as a whole";
async function getJSON(p) { const r = await fetch(p); if (!r.ok) throw new Error(p + " " + r.status); return r.json(); }

/* ---------- derived properties of a gloss ---------- */
const workOf = g => D.byWork[g.work] || {};
const gYear = g => g.year || workOf(g).year || 0;
const gLang = g => g.lang || workOf(g).lang;
const gGenre = g => g.scholarship ? "scholarship" : workOf(g).genre;
const gTier = g => workOf(g).tier;
const gDecade = g => Math.floor(gYear(g) / 10) * 10;

/* ---------- filters (persisted) ---------- */
const F = { lang: new Set(), tier: new Set(), genre: new Set(), decade: new Set() };
(function loadFilters() {
  try { const s = JSON.parse(store("annFilters") || "{}"); for (const k in F) (s[k] || []).forEach(v => F[k].add(v)); } catch (e) {}
})();
function saveFilters() { const o = {}; for (const k in F) o[k] = [...F[k]]; store("annFilters", JSON.stringify(o)); }
function passes(g) {
  if (F.lang.size && !F.lang.has(gLang(g))) return false;
  if (F.tier.size && !F.tier.has(gTier(g))) return false;
  if (F.genre.size && !F.genre.has(gGenre(g))) return false;
  if (F.decade.size && !F.decade.has(String(gDecade(g)))) return false;
  return true;
}
const visible = () => D.glosses.filter(passes);

/* ---------- boot ---------- */
async function boot() {
  view.innerHTML = `<p class="fine">Loading…</p>`;
  try {
    const [w, g, ex, pl] = await Promise.all([getJSON("data/works.json"), getJSON("data/glosses.json"), getJSON("data/exercitia.json"),
      getJSON("data/plates.json").catch(() => ({}))]);
    D.plates = pl;
    D.works = w.works; D.works.forEach(x => D.byWork[x.id] = x);
    D.glosses = g.glosses; D.ex = ex; D.sections = ex.sections;
    for (const s of ex.sections) for (const u of s.units) D.units[u.n] = { ...u, sec: s.id };
  } catch (e) {
    view.innerHTML = `<div class="panel"><h2>The data could not be loaded</h2><p class="readable">${esc(e.message)}. The site has to be served over http(s), not opened as a local file.</p></div>`;
    return;
  }
  window.addEventListener("hashchange", route);
  route();
}

function route() {
  const h = location.hash.replace(/^#\/?/, "");
  const [r, a] = h.split("/");
  document.querySelectorAll("#nav a").forEach(x => x.classList.toggle("on", x.dataset.r === (r || "home")));
  view.innerHTML = "";
  const fn = { "": viewHome, spex: () => viewReader(+a || 23), book: viewBook, works: () => a ? viewWork(decodeURIComponent(a)) : viewWorks,
    paths: () => viewPaths(a && decodeURIComponent(a)), intro: viewIntro,
    atlas: () => viewAtlas(a && decodeURIComponent(a)), bibliography: viewBibliography, timeline: viewTimeline,
    method: viewMethod, imprint: viewImprint, privacy: viewPrivacy }[r];
  if (!fn) { viewHome(); return; }
  const res = fn();
  if (typeof res === "function") res();
  if (r !== "spex" && !(r === "atlas" && a)) window.scrollTo(0, 0);
  if (r !== "atlas" && NET) { NET.stop(); NET = null; }
}

/* ============================================================ HOME */
function viewHome() {
  const tiers = { A: 0, B: 0, C: 0, D: 0 };
  D.works.forEach(w => tiers[w.tier]++);
  const placed = D.glosses.filter(g => g.spex).length;
  view.append(el(`<div>
    <div class="viewhead"><span class="tag">A research apparatus · in the orbit of Ignatiana</span>
      <h1>Annotationes</h1>
      <p class="lede">The <em>Spiritual Exercises</em> of Ignatius of Loyola and what the twentieth century made of
      them: the text paragraph by paragraph at the centre, the century's commentaries, translations, papal documents,
      journals and literary readings in the margin, each where it touches the book.</p></div>
    <div class="grid2">
      <div class="panel"><h2>Start reading</h2>
        <p class="readable">The reader opens on the Principle and Foundation [23]. The strip on the left shows, for the
        whole book, where the glosses gather under the current filters; click anywhere on it to jump.</p>
        <p><a href="#/spex/23">Principle and Foundation [23]</a> · <a href="#/spex/65">Meditation on hell [65]</a> ·
        <a href="#/spex/313">Rules for discernment [313]</a> · <a href="#/spex/365">The thirteenth rule [365]</a></p>
        <p><a href="#/intro">Introduction</a> · <a href="#/paths">Reading paths</a> ·
        <a href="#/book">Glosses on the book as a whole</a> · <a href="#/works">All works</a></p>
      </div>
      <div class="panel"><h2>What is here</h2>
        <p><span class="stat">${D.works.length}</span> works &nbsp; <span class="stat">${D.glosses.length}</span> glosses
        (${placed} tied to paragraphs)</p>
        <p class="readable">${Object.keys(TIERS).map(t => `<span class="tier ${t}">${t}</span> ${tiers[t]} ${esc(TIERS[t].toLowerCase())}`).join("<br>")}</p>
        <p class="fine">Stage 1 of the build. What is in and what is pending is listed under <a href="#/works">Works</a> and <a href="#/method">Method</a>.</p>
      </div>
    </div>
    <div class="panel"><h2>Three things the margin is meant to show</h2>
      <ol class="readable">
        <li><strong>The century read the book unevenly.</strong> Outside the running commentaries, reception gathers on
        a few places: the Foundation, the meditation on hell, the Kingdom, the Contemplation to Attain Love and the
        rules for discernment. See the <a href="#/intro">introduction</a>.</li>
        <li><strong>The citation grid is itself a twentieth-century artefact.</strong> The numbers [1]–[370] that every
        modern commentary cites date from 1928. Longridge (1919) and Feder (1922) wrote before them; their sections are
        mapped onto the grid here by hand.</li>
        <li><strong>The book crossed out of the Church.</strong> A novelist (Joyce, 1916), a psychologist (Jung,
        1939–40) and a critic (Barthes, 1971) read it beside the theologians, and the margin keeps them on the same
        paragraph.</li>
      </ol>
    </div>
    <h2 style="margin-top:1.6rem">Plates</h2>
    <div class="plates">${["spex", "rickaby-1915", "joyce-1916", "longridge-1919", "pius11-1922", "pius11-1929", "ryf", "codina-1926", "torti-1909", "marcos-1923"].map(plateFig).join("")}</div>
  </div>`));
}

function plateFig(id) {
  const p = (D.plates || {})[id]; if (!p) return "";
  return `<figure class="plate"><img src="assets/plates/${id}.jpg" alt="${esc(p.caption)}" loading="lazy">
    <figcaption>${esc(p.caption)}<span class="fine">${esc(p.credit)}</span></figcaption></figure>`;
}

/* ============================================================ READER */
let exLang = store("annLang") || "en";
function viewReader(n) {
  if (!D.units[n]) n = 23;
  const u = D.units[n];
  const sec = D.sections.find(s => s.id === u.sec);
  const si = D.sections.indexOf(sec);
  const wrap = el(`<div class="reader">
    <nav class="density" aria-label="Density of glosses across [1]–[370]"></nav>
    <div class="textcol">
      <div class="toolbar">
        <div class="seg" role="group" aria-label="Language of the text">
          ${["es", "la", "en", "rk", "de", "all"].map(l => `<button type="button" data-l="${l}" ${l === "de" ? 'title="German: Feder 1922"' : l === "rk" ? 'title="English: Rickaby 1923"' : l === "en" ? 'title="English: Mullan 1914"' : ""}>${l === "rk" ? "en · Rickaby" : l}</button>`).join("")}
        </div>
        <div class="secnav">
          ${si > 0 ? `<a href="#/spex/${D.sections[si - 1].von}">← ${esc(short(D.sections[si - 1]))}</a>` : ""}
          ${si < D.sections.length - 1 ? `<a href="#/spex/${D.sections[si + 1].von}">${esc(short(D.sections[si + 1]))} →</a>` : ""}
        </div>
      </div>
      <h2 class="sectitle">${esc(sec.titel_en)}</h2>
      <div class="secrange">[${sec.von}]–[${sec.bis}] · ${esc(sec.titel_es)}</div>
      <div class="paras"></div>
      <p class="fine" style="margin-top:1.5rem">${esc(D.ex.nummerierung)} ${esc(D.ex.vorlage_status)}</p>
      ${(exLang === "de" || exLang === "all") && D.feder ? `<p class="fine">German: ${esc(D.feder.quelle)} ${esc(D.feder.vorlage_status)} ${esc(D.feder.hinweis)}
        Its paragraphs were put on the 1928 grid with the editorial anchor table in <span class="mono">tools/feder_anchors.json</span>.
        <a href="#/works/feder-1922">About this translation</a>.</p>` : ""}
      ${(exLang === "rk" || exLang === "all") && D.rick ? `<p class="fine">English (Rickaby): ${esc(D.rick.quelle)} ${esc(D.rick.hinweis)}
        <a href="#/works/rickaby-1915">About this edition</a>.</p>` : ""}
    </div>
    <aside class="margin" aria-label="Glosses"></aside>
  </div>`);
  view.append(wrap);

  wrap.querySelectorAll(".seg button").forEach(b => {
    b.classList.toggle("on", b.dataset.l === exLang);
    b.onclick = () => { exLang = b.dataset.l; store("annLang", exLang); route(); };
  });
  // The German layer is a separate file, loaded the first time it is asked for.
  if ((exLang === "de" || exLang === "all") && !D.feder) {
    getJSON("data/feder.json").then(f => {
      D.feder = f; D.federUnits = {}; f.units.forEach(u => D.federUnits[u.n] = u);
      if (location.hash.startsWith("#/spex")) route();
    }).catch(() => {});
  }

  // Rickaby's translation likewise.
  if ((exLang === "rk" || exLang === "all") && !D.rick) {
    getJSON("data/rickaby_text.json").then(f => {
      D.rick = f; D.rickUnits = {}; f.units.forEach(u => D.rickUnits[u.n] = u);
      if (location.hash.startsWith("#/spex")) route();
    }).catch(() => {});
  }

  const paras = wrap.querySelector(".paras");
  for (const p of sec.units) {
    const d = el(`<div class="para${p.n === n ? " sel" : ""}" id="p${p.n}" tabindex="0">
      <div class="pn"><b>[${p.n}]</b></div><div class="pt">${paraText(p)}</div></div>`);
    d.onclick = () => select(p.n);
    d.onkeydown = e => { if (e.key === "Enter") select(p.n); };
    paras.append(d);
  }
  drawDensity(wrap.querySelector(".density"), n);
  drawMargin(wrap.querySelector(".margin"), n);
  placeMargin(n);
  const target = wrap.querySelector("#p" + n);
  if (target) requestAnimationFrame(() => target.scrollIntoView({ block: "center" }));
}
const short = s => s.titel_en.split(/[,:;]/)[0].slice(0, 34);
function paraText(p) {
  const de = () => {
    if (!D.federUnits) return `<span class="fine">Loading the German…</span>`;
    const u = D.federUnits[p.n];
    if (!u || !u.de) return `<span class="fine">Not in Feder's text as scanned.</span>`;
    const pg = u.pages.length > 1 ? `pp. ${u.pages[0]}–${u.pages[u.pages.length - 1]}` : `p. ${u.pages[0]}`;
    return esc(u.de) + ` <span class="fine">(Feder 1922, ${pg})</span>`;
  };
  const rk = () => {
    if (!D.rickUnits) return `<span class="fine">Loading Rickaby's English…</span>`;
    const u = D.rickUnits[p.n];
    if (!u || !u.en) return `<span class="fine">Not in Rickaby's text as read.</span>`;
    const pg = u.pages[0] === u.pages[1] ? `p. ${u.pages[0]}` : `pp. ${u.pages[0]}–${u.pages[1]}`;
    return esc(u.en) + ` <span class="fine">(Rickaby 1923, ${pg})</span>`;
  };
  const one = l => {
    if (l === "de") return de();
    if (l === "rk") return rk();
    const t = p[l] || "", L = p["label_" + l];
    const norm = s => s.toLowerCase().replace(/[^a-záéíóúñ0-9]/g, "");
    const lab = L && !norm(t).startsWith(norm(L)) ? `<span class="plabel">${esc(L)}</span>` : "";
    return lab + esc(t);
  };
  if (exLang === "all") return ["es", "la", "en", "rk", "de"].map(l => `<span class="lang">${l === "rk" ? "en · Rickaby" : l}</span>${one(l)}`).join("");
  return one(exLang);
}
function select(n) {
  history.replaceState(null, "", "#/spex/" + n);
  document.querySelectorAll(".para.sel").forEach(x => x.classList.remove("sel"));
  const p = document.getElementById("p" + n); if (p) p.classList.add("sel");
  drawDensity(document.querySelector(".density"), n);
  drawMargin(document.querySelector(".margin"), n);
  placeMargin(n);
}
/* On narrow screens the margin follows the selected paragraph instead of
   the whole section, so the glosses are where the reader is. */
function placeMargin(n) {
  const m = document.querySelector(".margin"), reader = document.querySelector(".reader");
  if (!m || !reader) return;
  if (narrow.matches) { const p = document.getElementById("p" + n); if (p) p.after(m); }
  else if (m.parentElement !== reader) reader.append(m);
}
narrow.addEventListener("change", () => { const m = location.hash.match(/spex\/(\d+)/); if (m) placeMargin(+m[1]); });

function densityCounts() {
  const c = new Array(371).fill(0);
  for (const g of visible()) if (g.spex) for (let i = g.spex[0]; i <= g.spex[1]; i++) c[i]++;
  return c;
}
function drawDensity(box, n) {
  const c = densityCounts();
  const max = Math.max(1, ...c);
  const starts = new Set(D.sections.map(s => s.von));
  box.innerHTML = "";
  for (let i = 1; i <= 370; i++) {
    const b = document.createElement("button");
    b.type = "button";
    b.style.setProperty("--h", c[i] ? (0.12 + 0.88 * Math.sqrt(c[i] / max)).toFixed(3) : 0);
    if (i === n) b.className = "sel";
    else if (starts.has(i)) b.className = "secstart";
    b.title = `[${i}] · ${c[i]} gloss${c[i] === 1 ? "" : "es"}`;
    b.setAttribute("aria-label", b.title);
    b.onclick = () => { if (D.units[i] && D.units[i].sec === (D.units[n] || {}).sec) select(i); else location.hash = "#/spex/" + i; };
    box.append(b);
  }
}

function filterPanel(onChange) {
  const all = D.glosses;
  const opts = {
    lang: [...new Set(all.map(gLang))].sort().map(v => [v, LANGS[v] || v]),
    tier: Object.keys(TIERS).map(v => [v, v]),
    genre: [...new Set(all.map(gGenre))].sort().map(v => [v, GENRES[v] || v]),
    decade: [...new Set(all.map(g => String(gDecade(g))))].sort().map(v => [v, v + "s"]),
  };
  const names = { lang: "Language", tier: "Access", genre: "Genre", decade: "Decade" };
  const active = Object.values(F).reduce((a, s) => a + s.size, 0);
  const box = el(`<details class="filters" ${narrow.matches && !active ? "" : "open"}><summary>Filters${active ? ` (${active} active)` : ""}</summary>${Object.keys(opts).map(k => `<div class="row"><span>${names[k]}</span>${opts[k].map(([v, l]) =>
    `<button type="button" class="fbtn${F[k].has(v) ? " on" : ""}" data-k="${k}" data-v="${esc(v)}" ${k === "tier" ? `title="${esc(TIERS[v])}"` : ""}>${esc(l)}</button>`).join("")}</div>`).join("")}
    ${active ? `<div class="row"><span></span><button type="button" class="fbtn" data-clear="1">clear filters</button></div>` : ""}</details>`);
  box.querySelectorAll("button").forEach(b => b.onclick = () => {
    if (b.dataset.clear) { for (const k in F) F[k].clear(); }
    else { const s = F[b.dataset.k]; s.has(b.dataset.v) ? s.delete(b.dataset.v) : s.add(b.dataset.v); }
    saveFilters(); onChange();
  });
  return box;
}

function drawMargin(box, n) {
  const here = visible().filter(g => g.spex && g.spex[0] <= n && n <= g.spex[1])
    .sort((a, b) => gYear(a) - gYear(b) || (a.spex[1] - a.spex[0]) - (b.spex[1] - b.spex[0]));
  const total = D.glosses.filter(g => g.spex && g.spex[0] <= n && n <= g.spex[1]).length;
  const whole = visible().filter(g => !g.spex).length;
  box.innerHTML = "";
  box.append(el(`<div class="marginhead"><h2>[${n}]</h2><span class="fine">${here.length} of ${total} gloss${total === 1 ? "" : "es"} shown</span></div>`));
  box.append(filterPanel(() => { drawDensity(document.querySelector(".density"), n); drawMargin(box, n); }));
  if (!here.length) box.append(el(`<p class="empty">No gloss on this paragraph${total ? " under the current filters" : " yet"}.</p>`));
  here.forEach(g => box.append(glossCard(g)));
  box.append(el(`<p class="fine"><a href="#/book">${whole} gloss${whole === 1 ? "" : "es"} on the book as a whole</a> are not tied to a paragraph.</p>`));
}

function glossCard(g, opts = {}) {
  const w = workOf(g);
  const who = g.author || w.author || "";
  const wt = String(w.title || "").split(/(?<!\bSt)\. |: /)[0];   // short title on cards; the full one is on the work page
  const head = g.title ? `${esc(g.title)} <span class="fine">in <a href="#/works/${esc(w.id)}">${esc(wt)}</a></span>`
                       : `<a href="#/works/${esc(w.id)}">${esc(wt)}</a>`;
  const card = el(`<article class="gloss ${esc(w.tier)}">
    <div class="who"><span class="tier ${esc(w.tier)}" title="${esc(TIERS[w.tier])}">${esc(w.tier)}</span>
      <strong>${esc(who)}</strong><span class="fine">${gYear(g) || ""}</span></div>
    <div class="meta">${head}</div>
    <div class="meta">${[opts.showRange ? range(g.spex) : "", g.loc, LANGS[gLang(g)], GENRES[gGenre(g)], BASIS[g.basis]].filter(Boolean).map(esc).join(" · ")}</div>
    ${g.label && g.label !== g.loc ? `<p class="note"><em>${esc(g.label)}</em></p>` : ""}
    ${g.note ? `<p class="note">${esc(g.note)}</p>` : ""}
    ${g.quote ? `<blockquote>${esc(g.quote)}</blockquote>` : ""}
    ${g.url ? `<p class="note"><a href="${esc(g.url)}" target="_blank" rel="noopener">${esc(g.linkLabel || (w.tier === "A" ? "Read the scan" : "Read on the publisher's site"))} ↗</a></p>` : ""}
    ${g.ref ? `<button type="button" class="more">${esc(moreLabel(g))}</button><div class="body" hidden></div>` : ""}
  </article>`);
  const more = card.querySelector(".more");
  if (more) more.onclick = async () => {
    const body = card.querySelector(".body");
    if (!body.hidden) { body.hidden = true; more.textContent = moreLabel(g); return; }
    more.textContent = "Loading…";
    try {
      D.files = D.files || {};
      if (!D.files[g.ref.file]) D.files[g.ref.file] = await getJSON("data/" + g.ref.file);
      body.innerHTML = g.ref.file === "longridge_exx.json" ? longridgeHTML(g.ref) : notesHTML(D.files[g.ref.file], g.ref);
      body.hidden = false; more.textContent = "Hide text";
    } catch (e) { more.textContent = "Could not load the text"; }
  };
  return card;
}
const moreLabel = g => ({ "rickaby-1915": "Show Rickaby's notes", "feder-1922": "Show the whole note" })[g.work] || "Show Longridge's text";
function notesHTML(doc, ref) {
  const e = doc.entries[ref.index];
  return e ? e.paras.map(p => `<p>${esc(p)}</p>`).join("") + `<p class="fine">${esc(doc.hinweis)}</p>` : "";
}
function longridgeHTML(ref) {
  const L = D.files["longridge_exx.json"];
  if (ref.note) {
    const n = L.notes.find(x => x.id === ref.note);
    return n ? n.paras.map(p => `<p>${esc(p)}</p>`).join("") : "";
  }
  const b = (L.sections[ref.section] || [])[ref.index];
  if (!b) return "";
  return b.paras.map(p => `<p class="${p.t === "note" ? "nt" : ""}">${esc(p.s)}</p>`).join("") +
    `<p class="fine">${esc(L.hinweis)}</p>`;
}

/* ============================================================ BOOK AS A WHOLE */
function viewBook() {
  const box = el(`<div>
    <div class="viewhead"><span class="tag">The book as a whole</span><h1>Glosses not tied to a paragraph</h1>
      <p class="lede">Papal documents, prefaces, overviews and later scholarship that speak of the Exercises as one
      book. They are counted here rather than smeared across all 370 paragraphs of the density strip.</p></div>
    <div class="grid2"><div class="list"></div><div class="side"></div></div></div>`);
  view.append(box);
  const draw = () => {
    const list = box.querySelector(".list"); list.innerHTML = "";
    const gs = visible().filter(g => !g.spex).sort((a, b) => gYear(a) - gYear(b));
    if (!gs.length) list.append(el(`<p class="empty">Nothing under the current filters.</p>`));
    gs.forEach(g => list.append(glossCard(g)));
    const side = box.querySelector(".side"); side.innerHTML = ""; side.append(filterPanel(draw));
  };
  draw();
}

/* ============================================================ WORKS */
function viewWorks() {
  const counts = {};
  D.glosses.forEach(g => counts[g.work] = (counts[g.work] || 0) + 1);
  const groups = Object.keys(TIERS).map(t => {
    const ws = D.works.filter(w => w.tier === t).sort((a, b) => a.year - b.year);
    return `<div class="panel"><h2><span class="tier ${t}">${t}</span> ${esc(TIERS[t])}</h2>
      <ul class="worklist">${ws.map(w => `<li><span class="fine">${w.year}</span>
        <div><a class="wt" href="#/works/${esc(w.id)}">${esc(w.author ? w.author + ", " : "")}${esc(w.title)}</a>
          <div class="ws">${esc(w.status)}</div></div>
        <span class="fine">${counts[w.id] ? counts[w.id] + " gloss" + (counts[w.id] === 1 ? "" : "es") : "–"}</span></li>`).join("")}</ul></div>`;
  }).join("");
  view.append(el(`<div><div class="viewhead"><span class="tag">Works</span><h1>The works of the reception</h1>
    <p class="lede">Every work the apparatus knows of, by access tier. The tier follows from the rights position,
    not from importance: the protected commentaries are the core of the century, and they are present as anchors and
    references only.</p></div>${groups}</div>`));
}

function viewWork(id) {
  const w = D.byWork[id];
  if (!w) { view.append(el(`<div class="panel"><h2>Unknown work</h2><p><a href="#/works">All works</a></p></div>`)); return; }
  const gs = D.glosses.filter(g => g.work === id).sort((a, b) => (a.spex ? a.spex[0] : 0) - (b.spex ? b.spex[0] : 0));
  const cov = new Array(371).fill(false);
  gs.forEach(g => { if (g.spex) for (let i = g.spex[0]; i <= g.spex[1]; i++) cov[i] = true; });
  const starts = new Set(D.sections.map(s => s.von));
  const ncov = cov.filter(Boolean).length;
  const box = el(`<div>
    <div class="viewhead"><span class="tag"><span class="tier ${esc(w.tier)}">${esc(w.tier)}</span> ${esc(TIERS[w.tier])}</span>
      <h1>${esc(w.title)}</h1><p class="lede">${esc(w.author)}${w.author ? ", " : ""}${w.year}${w.yearEnd ? "–" + w.yearEnd : ""}</p></div>
    <div class="panel"><dl class="kv">
      ${w.imprint ? `<dt>Edition</dt><dd>${esc(w.imprint)}</dd>` : ""}
      <dt>Language</dt><dd>${esc(LANGS[w.lang] || w.lang)}</dd>
      <dt>Genre</dt><dd>${esc(GENRES[w.genre] || w.genre)}</dd>
      <dt>Status</dt><dd>${esc(w.status)}</dd>
      <dt>Rights</dt><dd>${esc(w.rights)}</dd>
      ${w.sources && w.sources.length ? `<dt>Sources</dt><dd>${w.sources.map(s => `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.label)} ↗</a>`).join("<br>")}</dd>` : ""}
      ${w.note ? `<dt>Note</dt><dd>${esc(w.note)}</dd>` : ""}
    </dl></div>
    ${(D.plates || {})[w.id] ? `<div style="max-width:30rem">${plateFig(w.id)}</div>` : ""}
    <div class="panel"><h2>Coverage of [1]–[370]</h2>
      <div class="coverage">${cov.slice(1).map((on, i) => `<i class="${on ? "on" : ""}${starts.has(i + 1) ? " secstart" : ""}" title="[${i + 1}]"></i>`).join("")}</div>
      <p class="fine">${ncov} of 370 paragraphs touched by ${gs.filter(g => g.spex).length} placed gloss${gs.filter(g => g.spex).length === 1 ? "" : "es"};
      ${gs.filter(g => !g.spex).length} on the book as a whole.</p></div>
    <div class="list"></div></div>`);
  view.append(box);
  const list = box.querySelector(".list");
  gs.slice(0, 400).forEach(g => list.append(glossCard(g, { showRange: true })));
}

/* ============================================================ TIMELINE */
/* After the timeline of Ignatiana: the works of the apparatus in time, in five lines, with the
   crossings the apparatus itself documents. Dates are editorial anchors: the year of the work,
   spans where it appeared over years. Editorial matter, CC BY 4.0. */
const TL_LINES = [
  ["church", "The popes", "--fam-church"],
  ["comm", "Commentaries and translations", "--fam-commentary"],
  ["journ", "Journals", "--fam-journal"],
  ["hist", "History and sources", "--fam-history"],
  ["thought", "Psychology, philosophy, literature", "--fam-psychology"],
];
const TL = [
  { id: "ryf", l: "journ", y: 1901, jahr: "1901–", kurz: "Razón y Fe" },
  { id: "watrigant", l: "hist", y: 1906, jahr: "1906–", kurz: "Bibliothèque des Exercices" },
  { id: "torti-1909", l: "comm", y: 1909, jahr: "1909", kurz: "Torti" },
  { id: "rickaby-1915", l: "comm", y: 1915, jahr: "1915/1923", kurz: "Rickaby" },
  { id: "joyce-1916", l: "thought", y: 1916, jahr: "1916", kurz: "Joyce, Portrait" },
  { id: "monumenta", l: "hist", y: 1919, jahr: "1919", kurz: "Monumenta: the critical text", href: "#/method" },
  { id: "longridge-1919", l: "comm", y: 1919.5, jahr: "1919", kurz: "Longridge" },
  { id: "ram", l: "journ", y: 1920, jahr: "1920–", kurz: "Revue d'ascétique" },
  { id: "feder-1922", l: "comm", y: 1922, jahr: "1922", kurz: "Feder" },
  { id: "pius11-1922", l: "church", y: 1922.5, jahr: "1922", kurz: "Summorum Pontificum" },
  { id: "marcos-1923", l: "thought", y: 1923, jahr: "1923", kurz: "Marcos" },
  { id: "przywara-1925", l: "comm", y: 1925, jahr: "1925", kurz: "Przywara, Majestas Divina" },
  { id: "codina-1926", l: "hist", y: 1926, jahr: "1926", kurz: "Codina, Orígenes" },
  { id: "zam", l: "journ", y: 1926.5, jahr: "1926–1944", kurz: "Zeitschrift für Aszese und Mystik" },
  { id: "numbering", l: "hist", y: 1928, jahr: "1928", kurz: "The numbers [1]–[370]", href: "#/method" },
  { id: "pius11-1929", l: "church", y: 1929, jahr: "1929", kurz: "Mens nostra" },
  { id: "przywara-dsm", l: "comm", y: 1938, jahr: "1938–1940", kurz: "Przywara, Deus semper maior" },
  { id: "jung-eth", l: "thought", y: 1939, jahr: "1939–40", kurz: "Jung, ETH lectures" },
  { id: "balthasar-1946", l: "comm", y: 1946, jahr: "1946", kurz: "Balthasar" },
  { id: "iparraguirre", l: "hist", y: 1946.5, jahr: "1946–1973", kurz: "Iparraguirre, Historia" },
  { id: "gul", l: "journ", y: 1947, jahr: "1947–", kurz: "Geist und Leben" },
  { id: "hrahner-1947", l: "hist", y: 1947.5, jahr: "1947", kurz: "Hugo Rahner" },
  { id: "puhl-1951", l: "comm", y: 1951, jahr: "1951", kurz: "Puhl" },
  { id: "jung-cw", l: "thought", y: 1953, jahr: "1935–57", kurz: "Jung, Collected Works" },
  { id: "krahner-1956", l: "thought", y: 1956, jahr: "1956", kurz: "Karl Rahner, Logik" },
  { id: "fessard-1956", l: "thought", y: 1956.5, jahr: "1956–1966", kurz: "Fessard, Dialectique" },
  { id: "hopkins", l: "thought", y: 1959, jahr: "1880–81 (pr. 1959)", kurz: "Hopkins" },
  { id: "theway", l: "journ", y: 1961, jahr: "1961–", kurz: "The Way" },
  { id: "krahner-1965", l: "comm", y: 1965, jahr: "1965", kurz: "Karl Rahner, Betrachtungen" },
  { id: "peters-1967", l: "comm", y: 1967, jahr: "1967", kurz: "Peters" },
  { id: "studies", l: "journ", y: 1969, jahr: "1969–", kurz: "Studies" },
  { id: "barthes-1971", l: "thought", y: 1971, jahr: "1971", kurz: "Barthes" },
  { id: "certeau-1973", l: "thought", y: 1973, jahr: "1973", kurz: "Certeau" },
  { id: "fleming-1978", l: "comm", y: 1978, jahr: "1978", kurz: "Fleming" },
];
const TL_ERAS = [
  { until: 1928, titel: "Before the numbering (to 1927)" },
  { until: 1946, titel: "The interwar journals and the war (1928–1945)" },
  { until: 1965, titel: "After the war (1946–1964)" },
  { until: 9999, titel: "The Council and after (1965–1978)" },
];
/* Crossings the apparatus documents; each names the gloss or record that carries it. */
const TL_CROSS = [
  { from: "watrigant", to: "ryf", href: "#/works/ryf", titel: "Razón y Fe (1909) reports on Watrigant's library of the Exercises at Enghien" },
  { from: "monumenta", to: "ram", href: "#/works/ram", titel: "The Revue d'ascétique (1920) greets the critical edition of the Exercises" },
  { from: "ryf", to: "codina-1926", href: "#/paths/sources", titel: "Arturo Codina writes on the sources in Razón y Fe (1915–17) before his book on the origins of 1926" },
  { from: "rickaby-1915", to: "jung-cw", href: "#/works/jung-cw", titel: "Jung quotes the Exercises in Rickaby's second edition (1923)" },
  { from: "pius11-1929", to: "zam", href: "#/paths/king", titel: "Mens nostra translated and introduced in the Zeitschrift (Bleienstein, 1930)" },
  { from: "przywara-dsm", to: "zam", href: "#/works/przywara-dsm", titel: "Engert discusses Przywara's Theologie der Exerzitien in the Zeitschrift (1941)" },
];
function viewTimeline() {
  const CX = { church: 140, comm: 300, journ: 470, hist: 640, thought: 820 };
  const W = 960, ROW = 40, ERAROW = 42, TOP = 46;
  const rows = [...TL].sort((a, b) => a.y - b.y);
  let yy = TOP, eraIdx = -1;
  const bands = [], pos = {};
  for (const r of rows) {
    const e = TL_ERAS.findIndex(x => r.y < x.until);
    if (e !== eraIdx) { eraIdx = e; bands.push({ y: yy, titel: TL_ERAS[e].titel }); yy += ERAROW; }
    pos[r.id] = { x: CX[r.l], y: yy + ROW / 2 };
    yy += ROW;
  }
  const H = yy + 16;
  const colour = Object.fromEntries(TL_LINES.map(([l, , c]) => [l, c]));
  const spines = TL_LINES.map(([l]) => { const ys = rows.filter(r => r.l === l).map(r => pos[r.id].y);
    return `<line x1="${CX[l]}" x2="${CX[l]}" y1="${Math.min(...ys)}" y2="${Math.max(...ys)}" stroke="var(${colour[l]})" stroke-width="2" stroke-opacity=".3"/>`; }).join("");
  const bandSvg = bands.map(b => `<text x="20" y="${b.y + 28}" font-family="var(--serif)" font-size="14" font-style="italic" fill="var(--fg3)">${esc(b.titel)}</text>
    <line x1="20" x2="${W - 20}" y1="${b.y + 36}" y2="${b.y + 36}" stroke="var(--line)"/>`).join("");
  const crossSvg = TL_CROSS.map(c => { const a = pos[c.from], b = pos[c.to];
    const bow = a.x === b.x ? a.x - 78 : (a.x + b.x) / 2;
    return `<a href="${c.href}"><path d="M ${a.x} ${a.y} C ${bow} ${a.y + (b.y - a.y) * .25}, ${bow} ${a.y + (b.y - a.y) * .75}, ${b.x} ${b.y}"
      fill="none" stroke="var(--fg3)" stroke-width="1.4" stroke-dasharray="4 4" stroke-opacity=".75"><title>${esc(c.titel)}</title></path></a>`; }).join("");
  const dotSvg = rows.map(r => { const p = pos[r.id], right = r.l !== "thought", w = D.byWork[r.id] || {};
    return `<a href="${r.href || "#/works/" + r.id}"><title>${esc(w.author ? w.author + " — " : "")}${esc(w.title || r.kurz)}</title>
      <text x="96" y="${p.y + 4}" text-anchor="end" font-family="var(--mono)" font-size="11" fill="var(--fg3)">${esc(r.jahr)}</text>
      <circle cx="${p.x}" cy="${p.y}" r="5.5" fill="var(${colour[r.l]})" stroke="var(--bg)" stroke-width="1.5"/>
      <text x="${p.x + (right ? 14 : -14)}" y="${p.y + 4.5}" text-anchor="${right ? "start" : "end"}" font-family="var(--serif)" font-size="13.5"
        fill="var(--fg)" paint-order="stroke" stroke="var(--bg)" stroke-width="4" stroke-linejoin="round">${esc(r.kurz)}</text></a>`; }).join("");
  const headSvg = TL_LINES.map(([l, t]) => `<text x="${CX[l]}" y="24" text-anchor="middle" font-size="12" font-weight="600" fill="var(--fg2)">${esc(t)}</text>`).join("");
  view.append(el(`<div>
    <div class="viewhead"><span class="tag">Chronology</span><h1>Timeline — five lines, 1901–1978</h1>
      <p class="lede">The apparatus in time, after the timeline of Ignatiana. The century opens with journals and commentaries written
      without paragraph numbers; the critical text of 1919 and the numbering of 1928 give the readings a common grid; the German journal
      carries the interwar years and the war; after 1945 the Exercises pass to theology, psychology and the critics. Dashed arcs mark
      crossings the apparatus itself documents; every station opens its record.</p></div>
    <div class="tlwrap panel" style="padding:1rem .4rem">
      <svg class="tl" viewBox="0 0 ${W} ${H}" role="img" aria-label="Chronological chart of the works of the apparatus in five lines, 1901 to 1978">
        ${headSvg}${bandSvg}${spines}${crossSvg}${dotSvg}</svg></div>
    <div class="panel"><h2 style="margin-top:0">The documented crossings</h2>
      <ul style="margin:.4rem 0 0;padding-left:1.2rem">${TL_CROSS.map(c => `<li style="margin-bottom:.45rem"><a href="${c.href}">${esc(TL.find(x => x.id === c.from).kurz)}
        → ${esc(TL.find(x => x.id === c.to).kurz)}</a>: ${esc(c.titel)}.</li>`).join("")}</ul>
      <p class="fine" style="margin:.8rem 0 0">Dates are editorial anchors: the year of a work, a span where it appeared over years, the
      founding year of a journal. The chart spaces stations by order, not by elapsed time. Two stations are not works but events of the
      grid: the critical text of the Monumenta (1919) and the paragraph numbers of 1928.</p></div></div>`));
}

/* ============================================================ ATLAS */
/* After the atlas of the Woodstock Letters edition: a co-occurrence network, here of a fixed
   lexicon of concepts (tools/build_atlas.py), drawn by net.js. */
const FAMILY_LABEL = { commentary: "commentaries", journal: "journals and papal documents", history: "history and philosophy", psychology: "psychology and literature" };
let NET = null;
function viewAtlas(sel) {
  view.append(el(`<p class="fine">Loading…</p>`));
  (D.atlas ? Promise.resolve(D.atlas) : getJSON("data/atlas.json")).then(A => {
    D.atlas = A;
    view.innerHTML = "";
    const node = new Map(A.nodes.map(n => [n.id, n]));
    const nb = new Map(A.nodes.map(n => [n.id, []]));
    for (const e of A.edges) if (nb.has(e.s) && nb.has(e.t)) { nb.get(e.s).push([e.t, e]); nb.get(e.t).push([e.s, e]); }
    const short = n => n.label.replace(/\s*\(.*\)$/, "");
    const bridges = A.nodes.map(n => ({ id: n.id, span: new Set(nb.get(n.id).map(([m]) => node.get(m).sec)).size, deg: nb.get(n.id).length }))
      .filter(b => b.deg >= 4).sort((a, b) => b.span - a.span || b.deg - a.deg).slice(0, 16);
    const bars = (vals, labels, href) => { const mx = Math.max(1, ...vals);
      return `<table class="dist">${vals.map((v, i) => `<tr><td>${href ? `<a href="${href(i)}">${esc(labels[i])}</a>` : esc(labels[i])}</td>
        <td class="num">${v}</td><td class="barcell"><div class="bar"><i style="width:${Math.round(100 * v / mx)}%"></i></div></td></tr>`).join("")}</table>`; };
    function panel(id) {
      const n = node.get(id);
      if (!n) return `<h3>Selection</h3><p class="fine">Click a concept for its neighbours, its place in the book and the glosses that use it.</p>`;
      const gl = n.glosses.map(g => D.glosses.find(x => x.id === g)).filter(Boolean);
      const wname = g => { const w = workOf(g); return `${esc(g.author || (w.author || "").replace(/,.*$/, ""))} ${esc(g.year || w.year || "")}`; };
      return `<h3>${esc(n.label)}</h3>
        <p class="fine">${n.f} units · most at home in the ${FAMILY_LABEL[n.sec]}</p>
        <h4>Strongest neighbours</h4>
        <p>${nb.get(id).sort((a, b) => b[1].pmi * Math.log(1 + b[1].f) - a[1].pmi * Math.log(1 + a[1].f)).slice(0, 14)
          .map(([m, e]) => `<button class="achip" type="button" data-n="${esc(m)}" title="${e.f} shared units · PMI ${e.pmi}">${esc(short(node.get(m)))}</button>`).join("")}</p>
        <h4>Where in the book</h4>
        ${bars(n.sdist, A.sections.map(s => `[${s.von}]–[${s.bis}] ${s.title.split(/[,:;]/)[0]}`), i => `#/spex/${A.sections[i].von}`)}
        <p class="fine">Units that touch each part of the book. Most often at:
          ${n.paras.map(p => `<a href="#/spex/${p}">[${p}]</a>`).join(" ")}</p>
        <h4>By decade</h4>
        ${bars(n.ddist, A.decades.map(d => d + "s"))}
        <h4>Glosses</h4>
        <ul class="aglist">${gl.slice(0, 12).map(g => `<li><a href="${g.spex ? "#/spex/" + g.spex[0] : "#/works/" + g.work}">${wname(g)}</a>
          <span class="fine">${esc(g.title || g.note || "").slice(0, 110)}</span></li>`).join("")}</ul>
        ${gl.length > 12 ? `<p class="fine">and ${gl.length - 12} more; the commentaries held in full (Longridge, Rickaby, Feder's notes) count by paragraph and are not listed.</p>` : ""}
        <p class="fine">Looked for as: <span class="mono">${esc(A.lexicon[id].patterns.join(" · "))}</span></p>`;
    }
    const wrap = el(`<div>
      <div class="viewhead"><span class="tag">Atlas</span><h1>What stands next to what</h1>
        <p class="lede">Two concepts are joined when they occur in the same gloss, or the same paragraph of a commentary, more often than
        chance allows. The concepts are a fixed lexicon of the Exercises and their reception, each looked for in six languages.
        Colour marks the family of works in which a concept is most at home. Scroll or double-click to zoom, drag to pan.</p></div>
      <div class="panel chartbox">
        <div class="atools">
          <button class="btn" id="reheat" type="button">Re-arrange</button>
          <button class="btn" id="zin" type="button" aria-label="Zoom in">+</button>
          <button class="btn" id="zout" type="button" aria-label="Zoom out">−</button>
          <button class="btn" id="zreset" type="button">Reset</button>
        </div>
        <canvas id="net" aria-label="Co-occurrence network of the concepts of the apparatus"></canvas>
        <div class="alegend">${A.families.map((f, i) => `<span><i style="background:var(--fam-${f})"></i>${FAMILY_LABEL[f]} (${A.famUnits[i]} units)</span>`).join("")}</div>
      </div>
      <div class="grid2">
        <div class="panel" id="sel">${panel(sel)}</div>
        <div class="panel"><h3>Concepts that bridge the families</h3>
          <p class="fine">Concepts whose neighbours are at home in the most families of works: the vocabulary that holds the century's readings together.</p>
          <p>${bridges.map(b => `<button class="achip" type="button" data-n="${esc(b.id)}">${esc(short(node.get(b.id)))}<span class="n">${b.deg}</span></button>`).join("")}</p></div>
      </div>
      <p class="fine">${A.nodes.length} concepts and ${A.edges.length} links from ${A.units.toLocaleString("en")} units. Built by
        <span class="mono">tools/build_atlas.py</span>; the network code is that of the Woodstock Letters edition. The lexicon is editorial:
        it shows what was looked for, not everything the century said. Derived data, CC0.</p></div>`);
    view.append(wrap);
    const show = id => { const s = wrap.querySelector("#sel"); s.innerHTML = panel(id); bind(s);
      history.replaceState(null, "", id ? "#/atlas/" + id : "#/atlas"); };
    const bind = root => root.querySelectorAll("[data-n]").forEach(b => b.onclick = () => { NET && NET.select(b.dataset.n); show(b.dataset.n); });
    NET && NET.stop();
    NET = network(wrap.querySelector("#net"), { nodes: A.nodes.map(n => ({ ...n, name: short(n) })), edges: A.edges },
      { h: Math.min(620, Math.max(380, innerHeight * .62)), onSelect: show, color: n => "--fam-" + n.sec, labelCap: 34 });
    if (sel) NET.select(sel);
    wrap.querySelector("#reheat").onclick = () => NET.reheat();
    wrap.querySelector("#zin").onclick = () => NET.zoomBy(1.4);
    wrap.querySelector("#zout").onclick = () => NET.zoomBy(1 / 1.4);
    wrap.querySelector("#zreset").onclick = () => NET.resetView();
    bind(wrap);
  }).catch(e => { view.innerHTML = `<div class="panel"><p>${esc(e.message)}</p></div>`; });
}

/* ============================================================ BIBLIOGRAPHY */
function viewBibliography() {
  view.append(el(`<p class="fine">Loading…</p>`));
  (D.bib ? Promise.resolve(D.bib) : getJSON("data/bibliography.json")).then(B => {
    D.bib = B;
    view.innerHTML = "";
    const it = s => esc(s).replace(/\*([^*]+)\*/g, "<i>$1</i>");
    const wrap = el(`<div>
      <div class="viewhead"><span class="tag">Bibliography</span><h1>Everything in the apparatus</h1>
        <p class="lede">The editions behind the text, every work and every journal article in the margin, and the studies the notes name,
        in APA style. Each entry links to its source and to its place in the apparatus.</p></div>
      <div class="panel bibtools">
        <input type="search" id="bq" placeholder="Filter by author, title, journal, year…" aria-label="Filter the bibliography">
        <button class="btn" id="bbib" type="button">Download BibTeX</button>
        <button class="btn" id="bris" type="button">Download RIS</button>
        <span class="fine" id="bcount"></span>
      </div>
      <div id="blist"></div>
      <p class="fine">Built by <span class="mono">tools/build_bibliography.py</span> from the works list and the glosses. Access tiers: A full text here,
        B linked, C read in a copy and summarized, D recorded. Bibliographic data, CC0.</p></div>`);
    view.append(wrap);
    const list = wrap.querySelector("#blist");
    const draw = q => {
      const qq = q.toLowerCase().trim();
      const es = B.entries.filter(e => !qq || (e.apa + " " + e.note).toLowerCase().includes(qq));
      wrap.querySelector("#bcount").textContent = `${es.length} of ${B.entries.length}`;
      list.innerHTML = Object.entries(B.groups).map(([g, title]) => {
        const xs = es.filter(e => e.group === g);
        if (!xs.length) return "";
        return `<section class="panel"><h2>${esc(title)} <span class="fine">(${xs.length})</span></h2><ol class="biblist">${xs.map(e => `<li>
          <span class="ref">${it(e.apa)}</span>
          <span class="bmeta">${e.tier ? `<span class="tier t${e.tier}">${e.tier}</span>` : ""}${e.note ? `<span class="fine">${esc(e.note).slice(0, 160)}</span>` : ""}
          ${e.url ? `<a href="${esc(e.url)}" target="_blank" rel="noopener">source ↗</a>` : ""}
          ${e.here ? `<a href="${esc(e.here)}">in the apparatus →</a>` : ""}</span></li>`).join("")}</ol></section>`;
      }).join("");
    };
    const q = wrap.querySelector("#bq");
    q.oninput = () => draw(q.value);
    draw("");
    const save = (name, text, type) => { const a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([text], { type })); a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 2000); };
    const shown = () => B.entries.filter(e => !q.value.trim() || (e.apa + " " + e.note).toLowerCase().includes(q.value.toLowerCase().trim()));
    const surname = a => a.includes(",") ? a.split(",")[0] : a.split(/\s+/).filter(Boolean).pop();
    const key = (e, i) => (surname(e.bib.author && e.bib.author[0] || e.bib.title || "x") || "x")
      .normalize("NFD").replace(/[^A-Za-z]/g, "").toLowerCase() + (e.bib.year || "") + "_" + i;
    wrap.querySelector("#bbib").onclick = () => save("annotationes.bib", shown().map((e, i) => {
      const b = e.bib, f = { author: (b.author || []).join(" and "), title: b.title, journal: b.journal, volume: b.volume,
        pages: b.pages, year: b.year, publisher: b.publisher, address: b.address, series: b.series, note: b.note, url: e.url };
      return `@${b.type === "article" ? "article" : b.type === "periodical" ? "misc" : "book"}{${key(e, i)},\n` +
        Object.entries(f).filter(([, v]) => v).map(([k, v]) => `  ${k} = {${String(v).replace(/[{}]/g, "")}}`).join(",\n") + "\n}";
    }).join("\n\n"), "application/x-bibtex");
    wrap.querySelector("#bris").onclick = () => save("annotationes.ris", shown().map(e => {
      const b = e.bib, L = [["TY", b.type === "article" ? "JOUR" : b.type === "periodical" ? "JFULL" : "BOOK"]];
      (b.author || []).forEach(a => L.push(["AU", a]));
      L.push(["TI", b.title]); if (b.journal) L.push(["JO", b.journal]); if (b.volume) L.push(["VL", b.volume]);
      if (b.pages) { const [sp, ep] = b.pages.split(",")[0].split("--"); L.push(["SP", sp.trim()]); if (ep) L.push(["EP", ep.trim()]); }
      if (b.year) L.push(["PY", b.year]); if (b.publisher) L.push(["PB", b.publisher]); if (b.address) L.push(["CY", b.address]);
      if (b.note) L.push(["N1", b.note]); if (e.url) L.push(["UR", e.url]); L.push(["ER", ""]);
      return L.map(([k, v]) => `${k}  - ${v}`).join("\n");
    }).join("\n\n"), "application/x-research-info-systems");
  }).catch(e => { view.innerHTML = `<div class="panel"><p>${esc(e.message)}</p></div>`; });
}

/* ============================================================ METHOD */
/* ============================================================ PATHS */
async function paths() {
  if (!D.paths) D.paths = (await getJSON("data/paths.json")).paths;
  return D.paths;
}
function viewPaths(id) {
  view.append(el(`<p class="fine">Loading…</p>`));
  paths().then(P => {
    view.innerHTML = "";
    const p = id && P.find(x => x.id === id);
    if (!p) {
      view.append(el(`<div>
        <div class="viewhead"><span class="tag">Reading paths</span><h1>Paths through the margin</h1>
          <p class="lede">Each path follows one passage of the book through the century, station by station. A station
          is a gloss of the apparatus; the line above it says why it stands there.</p></div>
        <div class="pathlist">${P.map(x => `<a class="panel pathcard" href="#/paths/${esc(x.id)}">
          <h2>${esc(x.title)}</h2><p class="readable">${esc(x.question)}</p>
          <p class="fine">${x.stations.length} stations</p></a>`).join("")}</div>
        <p class="fine">Paths still to come, once their material is in: the <em>Anima Christi</em> in Przywara (1938) and in
        Jung's ETH lectures (1939); the Exercises and politics after 1945 and in Spain in the 1930s.</p></div>`));
      return;
    }
    const i = P.indexOf(p);
    const wrap = el(`<div>
      <div class="viewhead"><span class="tag"><a href="#/paths">Reading paths</a> · ${i + 1} of ${P.length}</span>
        <h1>${esc(p.title)}</h1><p class="lede">${esc(p.question)}</p></div>
      <div class="panel"><p class="readable">${esc(p.intro)}</p></div>
      ${p.plate && (D.plates || {})[p.plate] ? `<div style="max-width:30rem">${plateFig(p.plate)}</div>` : ""}
      <ol class="stations"></ol>
      <p class="fine">${i > 0 ? `← <a href="#/paths/${esc(P[i - 1].id)}">${esc(P[i - 1].title)}</a>` : ""}
        ${i < P.length - 1 ? ` &nbsp; <a href="#/paths/${esc(P[i + 1].id)}">${esc(P[i + 1].title)}</a> →` : ""}</p></div>`);
    const ol = wrap.querySelector(".stations");
    p.stations.forEach(s => {
      const g = D.glosses.find(x => x.id === s.gloss);
      if (!g) return;
      const li = el(`<li class="station"><p class="why">${esc(s.why)}
        ${g.spex ? `<a href="#/spex/${g.spex[0]}">Read ${esc(range(g.spex))} →</a>` : ""}</p></li>`);
      li.append(glossCard(g, { showRange: true }));
      ol.append(li);
    });
    view.append(wrap);
  }).catch(e => { view.innerHTML = `<div class="panel"><p>${esc(e.message)}</p></div>`; });
}

/* ============================================================ INTRODUCTION */
function viewIntro() {
  view.append(el(`<div>
    <div class="viewhead"><span class="tag">Introduction</span><h1>A book and its century</h1>
      <p class="lede">What the margin of this apparatus shows so far, and how to read it.</p></div>
    <div class="panel essay readable">
      <p>The <em>Spiritual Exercises</em> were not written to be read. They are directions for the one who gives a
      retreat: twenty annotations, a set of examinations, meditations and contemplations for four weeks, rules and
      notes, in a fixed order. The twentieth century read them all the same, more widely than any century before, and
      in more ways: as a manual, as a doctrine, as a set piece in a novel, as a psychological technique. Annotationes
      keeps the book at the centre of the screen and lets those readings collect in the margin, each where it touches
      the text.</p>
      <h2>A grid the century made</h2>
      <p>To place a reading on a paragraph one needs paragraphs. The numbers [1]–[370] that every modern commentary
      cites date from 1928. The three oldest commentaries here, Rickaby (1915, second edition 1923), Longridge (1919)
      and Feder (1922), were written without them, and two of the commentators rebuild the book as they go. Rickaby
      moves the rules into the weeks they belong to and the mysteries of the life of Christ into the days of the
      Second Week. Przywara's three volumes (1938–1940) follow the days of the retreat, so that the rules for eating,
      alms and scruples fall on the first day of the Third Week and the rules for thinking with the Church at the end
      of the Fourth. Mapping such works onto the grid is an editorial act, and every gloss says on what basis it was
      placed: a section read, a table of contents, an article title, a page, a match of the Spanish text.</p>
      <h2>Where the century looks</h2>
      <p>Counting glosses is a crude measure, and the running commentaries weigh heavily because they gloss
      everything. Set them aside, and the readings that pick out a passage gather on a few places: the Principle and
      Foundation [23], the First Week with its meditation on hell [65]–[71], the annotations, the Kingdom [91]–[100],
      the Contemplation to Attain Love [230]–[237] and the rules for discernment [313]–[336]. Most journal articles,
      in the <em>Zeitschrift für Aszese und Mystik</em> from 1926 and in <em>Geist und Leben</em> from 1947, address
      the book as a whole or its method rather than a passage. The Two Standards [136]–[148], outside the
      commentaries, is glossed for its sources, in two Spanish articles of 1915 on where Ignatius found it. The Kingdom
      [91]–[100] is the passage the 1930s articles of the <em>Zeitschrift für Aszese und Mystik</em> address most often, and
      the vocabulary of those years, leader and following, enters its reading (a <a href="#/paths/king">reading path</a>
      follows it). The thirteenth rule [365], the sentence of the book most
      quoted outside the Church, is glossed less than one would expect: the debates that made it notorious lie
      largely after 1978 or are not yet in the apparatus.</p>
      <h2>Outside the Church</h2>
      <p>Two readers from outside the commentaries run through the margin. Joyce's <em>Portrait of the Artist</em>
      (1916) puts a school retreat at its centre, and its two sermons on hell follow the fifth exercise through the
      five senses. Jung returns to the Exercises in some thirty places of his <em>Collected Works</em> between 1935
      and 1957, besides the ETH lectures of 1939–40. He quotes the book in Rickaby's second edition, so that his
      reading and Rickaby's notes can be laid side by side on the same paragraph. His stations are the Foundation,
      the colloquy, the senses in the meditation on hell and in the application of the senses, and a scene that is
      not in the book at all: the serpent-like vision of the <em>Autobiography</em>, first consoling, later known as
      evil. The apparatus places it on the rules for the enemy who comes as an angel of light and says that the
      placement is its own.</p>
      <h2>Languages and access</h2>
      <p>The margin is strongest so far in German (Feder's translation and notes, Przywara, the two journals) and in
      English (Rickaby, Longridge, Joyce, Jung, <em>Studies in the Spirituality of Jesuits</em>, <em>The Way</em>),
      with French from the <em>Revue d'ascétique et de mystique</em> and Latin from the <em>Acta Apostolicae
      Sedis</em>. Spanish comes so far from before 1931: eleven articles in <em>Razón y Fe</em> (1904–1919), where the
      sources of the book were fought over, Codina's study of its origins (1926), and Benjamín Marcos's lay apology of 1923, which claims Ignatius for
      Spanish philosophy and quotes the book in the form of a retreat manual; Italian from Torti's eight-day
      commentary (1909). The protected Spanish and Italian work after 1930 is not yet in. What can be shown depends on rights: works in the public domain
      are shown (tier A), freely available ones are linked (B), protected works are read in a copy and represented by
      anchors and summaries only (C), and the rest is recorded for reference (D).</p>
      <h2>How to use it</h2>
      <p>Open the <a href="#/spex/23">reader</a> on any paragraph and look to the margin; the strip beside the text shows
      where glosses gather under the current filters, and the decade filter shows attention moving through the book.
      The <a href="#/paths">reading paths</a> follow single passages through the century; the <a href="#/atlas">atlas</a>
      shows which concepts the readings join; the <a href="#/bibliography">bibliography</a> lists everything in the
      apparatus. The <a href="#/works">works
      list</a> gives each work's record, rights and coverage, and the <a href="#/method">method page</a> says how the
      apparatus was built and where it is uncertain.</p>
    </div></div>`));
}

function viewMethod() {
  const tierRows = Object.keys(TIERS).map(t => `<tr><td><span class="tier ${t}">${t}</span></td><td>${esc(TIERS[t])}</td><td>${{
    A: "The text is public domain in the United States (published before 1931) and is shown here: in full, or as the passages a gloss quotes.",
    B: "The text is free to read on its publisher's site. The apparatus records where it touches the book and links there; it copies nothing.",
    C: "The text is protected. The apparatus will ship only an anchor table (which page treats which paragraph), derived data without text, and the full-text functions open on a copy the reader owns. The first table, for Przywara's Deus semper maior vol. I, is in (read from its table of contents).",
    D: "Known and recorded, not obtainable or not yet cleared. Listed so that the gaps are visible.",
  }[t]}</td></tr>`).join("");
  view.append(el(`<div>
    <div class="viewhead"><span class="tag">Method</span><h1>Method, sources and limits</h1>
      <p class="lede">How the margin is made, what each mark means, and what is not there yet.</p></div>
    <div class="panel"><h2>The centre text</h2>
      <p class="readable">The Exercises are taken over from Ignatiana: the Spanish autograph and the Latin Vulgate of
      1548 from Monumenta Ignatiana (Madrid 1919), and Elder Mullan's English of 1914, all three in the US public
      domain, segmented onto the paragraph grid [1]–[370]. The German layer is Alfred Feder's translation from the
      autograph (Regensburg 1922), free in the United States and, Feder having died in 1927, in Germany as well. It was
      read by machine from a microfilm, cleaned and corrected against a dictionary (every change is logged), and put
      on the grid by an anchor table compiled by reading Feder beside the Spanish; a length check against the Spanish
      flags five paragraphs, all explained (mystery headings lost in the scan, short apparitions). Residual reading
      errors remain, and Feder's italics, which mark the words he supplied, are not reproduced.</p>
      <p class="readable">The grid itself dates from 1928. Works written before it (Rickaby 1915, Longridge 1919,
      Feder 1922) are mapped onto it editorially; their own divisions are kept as labels.</p></div>
    <div class="panel"><h2>Access tiers</h2><table class="plain"><tr><th></th><th>Tier</th><th>What it means here</th></tr>${tierRows}</table>
      <p class="fine" style="margin-top:.8rem">The rights standard is that of Ignatiana and the Woodstock Letters: US public
      domain, with the German and European position stated per work. Quotations are taken only from tier-A works; the
      build stops if a quote is attached to anything else.</p></div>
    <div class="panel"><h2>How a gloss is assigned</h2><table class="plain">
      ${Object.entries(BASIS).map(([k, v]) => `<tr><td class="mono">${k}</td><td>${esc(v)}</td></tr>`).join("")}</table>
      <p class="readable" style="margin-top:.8rem">The basis is shown on every card. A gloss assigned from a title or a
      table of contents says where a work speaks, not what it says; only <em>read</em> glosses carry a summary of
      content. Summaries are my wording, never the commentator's, unless the work is in the public domain and the
      card shows a quotation.</p>
      <p class="readable">The density strip counts placed glosses per paragraph under the current filters, on a
      square-root scale. Glosses on the book as a whole are kept out of it and listed separately. A long commentary
      cut into many blocks weighs more than a single article: the strip shows where glosses are, not how important
      they are.</p></div>
    <div class="panel"><h2>Stage 1: what is in, what is pending</h2>
      <ul class="readable">
        <li>In: the trilingual text; Longridge 1919 as commentary layer (131 blocks and notes, text on demand); Joyce
        1916; <em>Summorum Pontificum</em> 1922 and <em>Mens nostra</em> 1929 (key passages); Przywara's
        <em>Deus semper maior</em> by its table of contents; journal articles from the free archives of the
        <em>Zeitschrift für Aszese und Mystik</em> (1926–1944) and <em>Geist und Leben</em> (1947–1978), assigned from
        their titles.</li>
        <li>In since stage 1b: Feder 1922 as German layer of the centre text, paragraph-exact; Rickaby's notes
        (second edition, 1923) as a commentary layer, placed by matching his Spanish column to the autograph.</li>
        <li>Since then: Feder's endnotes (108 notes, pp. 164–185) as a German commentary layer, placed by the page
        that carries each call; a page anchor table for all three volumes of Przywara's <em>Deus semper maior</em>
        (148 anchors, read in the lending scans); selected articles of the <em>Revue d'ascétique et de mystique</em>
        vols. 1–4 and of <em>Studies in the Spirituality of Jesuits</em>, read and assigned; 28 passages of
        Jung's <em>Collected Works</em>, read and placed by paragraph (summaries only; Jung quotes the Exercises
        in Rickaby's second edition); Spanish and Italian before 1931: eleven articles of <em>Razón y Fe</em>
        (1904–1919, found by searching vols. 1–61), Codina's <em>Los orígenes de los Ejercicios</em> (1926) by its
        own subject index, Torti's Italian commentary (1909) by its section heads, and Benjamín Marcos, <em>San Ignacio
        de Loyola</em> (1923), read in full in Project Gutenberg; Rickaby's English translation as a second English
        text in the reader ("en · Rickaby"), cut onto the grid between the openings found in his Spanish column, with
        Mullan's English steering the cuts (machine-read, cuts can be off by a clause); twelve articles of the
        <em>Zeitschrift für Aszese und Mystik</em> and <em>Geist und Leben</em> read in full and summarized, among them
        six on the Christ-King meditation for the path on the King 1929–1942; Przywara's own index of the numbers
        of the Exercises (vol. III, pp. 438–440), transcribed by hand: 281 entries, of which the 130 that send a paragraph
        beyond the sections his tables of contents give it stand as glosses of their own.</li>
        <li>Pending: Spanish and Italian work after 1930 (Casanovas, Calveras, Iparraguirre,
        the review <em>Manresa</em>), still to be searched.</li>
      </ul></div>
    <div class="panel"><h2>How to cite</h2>
      <p class="readable">Fassbender, P. (2026). <i>Annotationes: The Spiritual Exercises in the Twentieth Century. A reception
      apparatus</i> (Version 1.0.0) [Data set]. Zenodo. <a href="https://doi.org/10.5281/zenodo.24447236" target="_blank" rel="noopener">https://doi.org/10.5281/zenodo.24447236</a></p>
      <p class="fine">Concept DOI, which always resolves to the latest version:
      <a href="https://doi.org/10.5281/zenodo.24447235" target="_blank" rel="noopener">10.5281/zenodo.24447235</a>.
      Cite the Exercises by paragraph number ([23]) and each work by its own pages.</p></div>
    <div class="panel"><h2>Licences and data</h2>
      <p class="readable">Code MIT; editorial texts (notes, summaries, introductions) CC BY 4.0; derived data (gloss
      index, coverage, anchor tables) CC0. The public-domain texts are public domain. No protected text is in the
      repository. The gloss index is built by <span class="mono">tools/build_glosses.py</span> from the files in
      <span class="mono">data/</span>.</p></div>
  </div>`));
}

/* ============================================================ LEGAL */
function viewImprint() {
  view.append(el(`<div>
    <div class="viewhead"><span class="tag">Legal notice</span><h1>Legal notice</h1>
      <p class="lede">Who operates this site, and how to reach them.</p></div>
    <div class="panel"><h2>Operator</h2>
      <p class="readable">Dr. Pantaleon Fassbender<br>16751 NE 5th Street<br>Williston, FL 32696<br>United States</p>
      <p class="readable">Email: <a href="mailto:pantaleonfassbender@gmail.com">pantaleonfassbender@gmail.com</a></p>
      <p class="readable">This site is a personal research project, operated and hosted in the United States by a
      private individual, and not on behalf of any institution, employer, publisher or religious order. It carries
      no advertising and no sponsorship. Responsible for the content: Dr. Pantaleon Fassbender, at the address above.
      How data are handled is set out in the <a href="#/privacy">privacy notice</a>.</p></div>
    <div class="panel"><h2>Rights in the texts</h2>
      <p class="readable">The site shows running text from public-domain editions only. For protected works it holds
      bibliographic records, references to paragraphs and pages, and editorial matter written for this site; all
      rights in those works rest with their authors, translators and publishers. If you hold rights in one of them and
      consider anything here to exceed what bibliographic reference and scholarly citation permit, write to the
      address above and it will be dealt with promptly.</p></div>
    <div class="panel"><h2>Liability for links</h2>
      <p class="readable">The site links to external archives and publishers. Their content is the responsibility of
      their operators. Links were checked when they were set; any link will be removed promptly on concrete evidence
      of a problem.</p></div>
    <div class="panel"><h2>No warranty</h2>
      <p class="readable">A research instrument offered free of charge and without warranty. Assignments can be wrong;
      the basis of each is shown on its card. Verify anything you intend to publish against the printed editions.</p></div>
  </div>`));
}

function viewPrivacy() {
  view.append(el(`<div>
    <div class="viewhead"><span class="tag">Privacy</span><h1>Privacy notice</h1>
      <p class="lede">What this site does with data, at the level of detail at which it is true.</p></div>
    <div class="panel"><h2>What the site is</h2>
      <p class="readable">A set of static files. No accounts, no forms, no cookies, no analytics, no advertising, and
      nothing loaded from third-party servers: opening a page contacts only the host in your address bar. Links to
      external archives are ordinary links; following one takes you to that site under its own terms.</p></div>
    <div class="panel"><h2>Server logs</h2>
      <p class="readable">The site is hosted by Netlify, whose infrastructure records the requests it serves
      (typically IP address, time, URL, status, user agent and referrer). This is the only server-side collection. It
      is used to deliver and secure the service; the operator does not analyse it. Where the GDPR applies, the legal
      basis is Art. 6(1)(f). Processing takes place in the United States.</p></div>
    <div class="panel"><h2>Stored on your device</h2>
      <p class="readable">The site keeps three preferences in your browser's localStorage: the colour theme, the
      language of the centre text and the margin filters. They never leave your device and can be removed by clearing
      site data for this domain. Nothing else is stored.</p></div>
    <div class="panel"><h2>Your rights</h2>
      <p class="readable">Readers in the European Economic Area have the rights of Articles 15–21 GDPR and may complain
      to a supervisory authority (Art. 77). Requests go to the address in the <a href="#/imprint">legal notice</a>;
      apart from the hosting logs, the site holds nothing about you. The site is addressed to adult readers and
      knowingly collects nothing from children.</p></div>
    <div class="panel"><h2>Changes</h2><p class="readable">Effective 21 November 2026.</p></div>
  </div>`));
}

/* ---------- theme ---------- */
document.getElementById("themeBtn").onclick = () => {
  const now = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", now);
  store("annTheme", now);
};

boot();
