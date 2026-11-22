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
  toc: "assigned from the table of contents",
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
    method: viewMethod, imprint: viewImprint, privacy: viewPrivacy }[r];
  if (!fn) { viewHome(); return; }
  const res = fn();
  if (typeof res === "function") res();
  if (r !== "spex") window.scrollTo(0, 0);
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
        <p><a href="#/book">Glosses on the book as a whole</a> · <a href="#/works">All works</a></p>
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
        <li><strong>The century read the book unevenly.</strong> Reception gathers on a few paragraphs: the Foundation,
        the Two Standards, the Three Classes, the Contemplation to Attain Love, the rules for discernment and the rules
        for thinking with the Church.</li>
        <li><strong>The citation grid is itself a twentieth-century artefact.</strong> The numbers [1]–[370] that every
        modern commentary cites date from 1928. Longridge (1919) and Feder (1922) wrote before them; their sections are
        mapped onto the grid here by hand.</li>
        <li><strong>The book crossed out of the Church.</strong> A novelist (Joyce, 1916), a psychologist (Jung,
        1939–40) and a critic (Barthes, 1971) read it beside the theologians, and the margin keeps them on the same
        paragraph.</li>
      </ol>
    </div>
    <h2 style="margin-top:1.6rem">Plates</h2>
    <div class="plates">${["spex", "rickaby-1915", "joyce-1916", "longridge-1919", "pius11-1922", "pius11-1929"].map(plateFig).join("")}</div>
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
          ${["es", "la", "en", "de", "all"].map(l => `<button type="button" data-l="${l}" ${l === "de" ? 'title="German: Feder 1922"' : ""}>${l === "all" ? "all" : l}</button>`).join("")}
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
  const one = l => {
    if (l === "de") return de();
    const t = p[l] || "", L = p["label_" + l];
    const norm = s => s.toLowerCase().replace(/[^a-záéíóúñ0-9]/g, "");
    const lab = L && !norm(t).startsWith(norm(L)) ? `<span class="plabel">${esc(L)}</span>` : "";
    return lab + esc(t);
  };
  if (exLang === "all") return ["es", "la", "en", "de"].map(l => `<span class="lang">${l}</span>${one(l)}`).join("");
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
    ${g.url ? `<p class="note"><a href="${esc(g.url)}" target="_blank" rel="noopener">Read on the publisher's site ↗</a></p>` : ""}
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
const moreLabel = g => g.work === "rickaby-1915" ? "Show Rickaby's notes" : "Show Longridge's text";
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

/* ============================================================ METHOD */
function viewMethod() {
  const tierRows = Object.keys(TIERS).map(t => `<tr><td><span class="tier ${t}">${t}</span></td><td>${esc(TIERS[t])}</td><td>${{
    A: "The text is public domain in the United States (published before 1931) and is shown here: in full, or as the passages a gloss quotes.",
    B: "The text is free to read on its publisher's site. The apparatus records where it touches the book and links there; it copies nothing.",
    C: "The text is protected. The apparatus will ship only an anchor table (which page treats which paragraph), derived data without text, and the full-text functions open on a copy the reader owns. Stage 1 has no anchor tables yet.",
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
        <li>Pending: Rickaby's translation; Feder's endnotes as a commentary layer; the articles of
        the <em>Revue d'ascétique et de mystique</em> vols. 1–4; <em>Studies in the Spirituality of Jesuits</em>; page
        anchor tables for the tier-C works, Przywara first; the Jung passages, which have been located but not yet
        read.</li>
      </ul></div>
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
