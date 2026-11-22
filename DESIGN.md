# Annotationes — the Spiritual Exercises in the twentieth century

**A research apparatus on the modern reception of the *Exercitia spiritualia*, in the orbit of Ignatiana** ·
Design document, draft 1 (21 November 2026) · working title

Ignatiana (ignatian-research.netlify.app) ends in 1773. Annotationes picks up one book of its corpus,
the *Spiritual Exercises*, and follows what the twentieth century made of it: in commentary and
translation, in retreat practice and papal teaching, in psychology, philosophy and literature, in
German, French, Spanish, English and Italian. The text of Ignatius stays at the centre of the screen;
the century gathers around it in the margin, paragraph by paragraph, the way a gloss gathers around a
medieval text.

The name comes from the twenty *Anotaciones* [1]–[20] with which the book opens: notes on how the
Exercises are to be given and received. The apparatus is a set of annotations on that book, made by a
century.

---

## 1. Premise

Three claims the apparatus is built to make visible rather than assert:

1. **The century read the book unevenly.** Reception clusters on a handful of paragraphs: the Principle
   and Foundation [23], the Two Standards [136]–[147], the Three Classes [149]–[157], the Contemplation
   to Attain Love [230]–[237], the Rules for Discernment [313]–[336], and the Rules for Thinking with the
   Church [352]–[370], above all the thirteenth rule [365]. The density bar (§3) shows where, and when.
2. **The citation grid is itself a twentieth-century artefact.** The paragraph numbers [1]–[370] that
   every modern commentary cites date only from 1928. The reception of the century runs on an
   apparatus the century made.
3. **The book crossed out of the Church.** Psychology (Jung, 1939–40), structuralism (Barthes, 1971),
   historiography (Certeau) and literature (Joyce, 1916) read it alongside the theologians. The
   apparatus keeps them in one margin, so that they can be compared on the same paragraph.

## 2. Scope

- **Time:** 1900 to 1978 as the working frame. 1922 (Ignatius declared patron of all retreats) and
  1928 (the paragraph grid) open it; 1978 (Fleming's *Contemporary Reading*) closes it, after the 31st
  and 32nd General Congregations (1965–66, 1974–75). Extending to 2000 is possible and left open (§11).
- **Languages:** German, French, Spanish and English from the start; Italian as a second step. Interface
  in English like Ignatiana, entry metadata in the original language.
- **Kinds of reception (genre filter):** commentary · translation · retreat conferences · magisterium ·
  psychology · philosophy and theory · literature · history of the Exercises · journals.

## 3. Interface: text in the centre, the century in the margin

### 3.1 The reader (`#/spex/{n}`)

- **Centre column:** the *Exercises* from Ignatiana's `data/exercitia.json`: Spanish autograph,
  Vulgate of 1548, English of Mullan 1914, paragraph-exact [1]–[370], language toggle as in Ignatiana
  (es / la / en / de / all). German layer: Feder 1922, public domain in the US and Germany (§5); it
  predates the 1928 grid, so it has to be segmented onto [1]–[370] editorially, as Longridge was.
- **Margin:** the glosses on the current paragraph or range, as cards: author, year, language, work,
  locator, a one-line editorial summary (my wording, never the commentator's text unless tier A), and
  an access badge (A–D, §5).
- **Filters:** language · decade · genre · access tier · author. Filters persist (`localStorage`).
- **Density bar:** a vertical strip beside the text, one cell per paragraph, shaded by the number of
  glosses under the current filters. Clicking a cell jumps there. Switching the decade filter animates
  how attention moves through the book across the century.
- **Deep links:** every paragraph and every gloss has an address (`#/spex/23`, `#/gloss/{id}`), so
  that the introduction, reading paths and other sites can link into it. Ignatiana's `SpEx [n]`
  citations link here for the reception view.

### 3.2 Other views

- **Commentators** (`#/authors`): one page per author with all glosses, ordered by paragraph, and the
  list of works with access tier.
- **Works** (`#/works/{id}`): bibliographic record, access, the paragraph coverage as a strip.
- **Reception curve** (`#/curve`): glosses per paragraph group and decade, small multiples.
- **Network** (`#/network`): who answers whom (see §6).
- **Translation atlas** (`#/atlas`): see §6.
- **Reading paths**, **introduction**, **method**, **imprint**, as in Ignatiana.

## 4. Data model

One file per concern, as in Ignatiana. Draft schemas:

```jsonc
// data/works.json
{ "id": "przywara-dsm",
  "author": "Erich Przywara", "authorId": "przywara",
  "title": "Deus semper maior. Theologie der Exerzitien",
  "year": 1938, "yearEnd": 1940, "lang": "de",
  "publisher": "Herder", "place": "Freiburg im Breisgau", "volumes": 3,
  "genre": "commentary",
  "tier": "C",                         // A full text · B free link · C own copy · D reference only
  "rights": "DE until 2042 (author d. 1972); US until 2033–35",
  "copies": [ { "where": "Internet Archive (lending)", "id": "deussempermaiort0001eric", "vol": 1 },
              { "where": "KU Leuven Limo (sign-in)", "id": "alma9916871850101488" } ] }

// data/glosses.json
{ "id": "przywara-dsm-023a",
  "work": "przywara-dsm",
  "spex": [23, 23],                    // paragraph range covered
  "loc": { "vol": 1, "pageFrom": 0, "pageTo": 0 },   // page in the reference copy
  "note": "Editorial one-line summary in English, my wording.",
  "url": null,                         // tier B: direct link to the article or page
  "text": null }                       // tier A only: the passage itself

// data/anchors/{work}.json   (tier C, the Jung-site method)
{ "work": "przywara-dsm", "edition": "Herder 1938–40", "pageCount": [0, 0, 0],
  "anchors": [ [23, 1, 0] ] }          // [paragraph, volume, page]
```

The anchor tables for tier C are derived data (which page discusses which paragraph). They carry no
text and are released under CC0, as in the Jung site and Ignatiana.

## 5. Corpus and access tiers

Rights standard as in Ignatiana and the Woodstock Letters: **US public domain** (published before 1931
as of 2026; build guard `PD_CUTOFF = year − 96`), with the German and EU position stated per work on
the method page. Items marked *(verify)* have not been checked yet.

### Tier A: full text (public domain)

| Work | Year | Language | Source | Status |
|---|---|---|---|---|
Checked 21 November 2026; the status column says what was confirmed and what is still open.

| Work | Year | Language | Source | Status |
|---|---|---|---|---|
| Rickaby, *The Spiritual Exercises … Spanish and English, with a Continuous Commentary* | 1915 (2nd ed. 1923) | en | Google Books F7kHAQAAIAAJ (2nd ed. 1923, PDF downloaded by hand: captcha); HathiTrust `uiug.30112000597846` (1923) sits behind a Cloudflare check | **in (stage 1b): notes as commentary layer** |
| Longridge, *The Spiritual Exercises … translated … with commentary and the Directorium* | 1919 | en | IA `spiritualexercis00igna_4`; already segmented in Ignatiana (`longridge_exx.json`) | reuse |
| Pius XI, apostolic constitution *Summorum Pontificum*, 25 July 1922: "S. Ignatius de Loyola caelestis Exercitiorum spiritualium patronus" | 1922 | la | AAS 14 (1922), issue 12 of 25 July 1922: IA `sim_acta-apostolicae-sedis_1922-07-25_14_12`, not restricted, OCR available; Latin also on vatican.va | confirmed |
| Pius XI, encyclical *Mens nostra*, 20 December 1929 | 1929 | la | AAS 21 (1929), issue 16 of 31 December 1929: IA `sim_acta-apostolicae-sedis_1929-12-31_21_16`, not restricted, OCR available; vatican.va has la/en/es/it (check whether the modern translations are protected; the Latin is not) | confirmed |
| Joyce, *A Portrait of the Artist as a Young Man*, ch. III (the retreat sermons) | 1916 | en | public domain worldwide | literary reception |
| Feder, *Ignatius von Loyola, Geistliche Übungen. Nach dem spanischen Urtext übertragen, eingeleitet und mit Anmerkungen versehen*, 2nd ed., Regensburg: Manz 1922 (first ed. a few months earlier, for the 400th anniversary 1522/23) | 1922 | de | IA `MN5044ucmf_5` (University of Chicago microfilm, not restricted; OCR poor, needs re-OCR from the PDF). Feder 1872–1927 (VIAF), so the text is public domain in Germany too. The Herder edition of 1939 (IA `ignatiusvonloyol0000alfr`) is lending only | **confirmed: German layer** |
| Przywara, *Majestas Divina. Ignatianische Frömmigkeit* | 1925 | de | title and date confirmed (Schaber, *Geist und Leben* 2003); English by Corbishley in *The Life of the Spirit* 1944–45 (protected); no free scan found | US-PD, DE protected until 2042; scan open |
| Watrigant (ed.), *Collection de la Bibliothèque des Exercices de saint Ignace* | 1906–1930s | fr | series confirmed (Tournai from 1906, later Enghien; e.g. nos. 52–53 of 1914); IA `labibliothequede0000pjhw` is a single item of 1892, not the series; no full run found online | scan open |
| Bremond and the "ascétique ou mystique" controversy | 1920s | fr | not confirmed which texts; Bremond d. 1933, public domain in France | open |
| *Revue d'ascétique et de mystique* (de Guibert, Toulouse, from 1920) | 1920– | fr | IA `revuedasctique01toul` (vols. 1–2) and `revuedasctique03toul` (vols. 3–4), University of Toronto scans, not restricted | confirmed for vols. 1–4; later volumes up to 1930 open |
| *Manresa* (Madrid, from 1925) | 1925– | es | journal confirmed; no digitisation found | open |
| *Zeitschrift für Aszese und Mystik* (Würzburg, 1925/26–1944; continued as *Geist und Leben*) | 1926– | de | free chronological archive at geist-und-leben.de/archiv/archiv-zam/ (19 volumes, article pages open without login); linked as tier B, the 1926–30 volumes would qualify for tier A | **confirmed (stage 1: 39 articles linked)** |

### Tier B: freely available, linked only

The apparatus maps the article to paragraphs and links out; it hosts no text.

- *Geist und Leben* (from 1947): the **chronological** archive at geist-und-leben.de/archiv/archiv-gul/
  is free (article pages open without login; the PDF links on them carry a token that expires after a
  day, so the apparatus links the article page). The systematic archive needs a subscription. The old
  host old.geist-und-leben.de fails its certificate check and is not linked. Stage 1: 37 articles
  1947–1978 linked, plus Faber 1993 on Przywara.
- *The Way* and *The Way Supplement*: **selected** back articles are free as PDFs under
  `theway.org.uk/back/{file}.pdf` (e.g. `s103Endean.pdf` = Supplement 103, confirmed); the directory
  is not listable and full issues are for subscribers. The link layer therefore needs one verified URL
  per article.
- *Studies in the Spirituality of Jesuits* (from 1969): open access, complete archive at Jesuit Sources
  Digital (jesuitsourcesdigital.bc.edu), no account needed. Confirmed.

### Tier C: own copy (the Jung-site method)

Only the anchor table ships. Full-text functions (concordance, KWIC) open locally once the reader loads
a copy; the page count is checked against the reference edition, with a warning on mismatch.

- Przywara, *Deus semper maior* (1938–40): IA lending scans of all three volumes
  (`deussempermaiort0001eric`, `…0000eric` = vol. II by date, `…0003eric`); KU Leuven PDF (three
  files, sign-in only). **First tier-C work.**
- Hugo Rahner, *Ignatius von Loyola und das geschichtliche Werden seiner Frömmigkeit* (1947).
- Karl Rahner, "Die Logik der existentiellen Erkenntnis bei Ignatius von Loyola" (1956);
  *Betrachtungen zum ignatianischen Exerzitienbuch* (1965).
- Hans Urs von Balthasar, translation of the Exercises (Luzern 1946; later Johannes Verlag,
  Einsiedeln, Sigillum 1, 4th ed. 1962) and related writings. Its marginal numbers were cited in
  German scholarship of the 1950s and 60s.
- Gaston Fessard, *La dialectique des Exercices spirituels de saint Ignace de Loyola* (1956, 1966).
- Roland Barthes, *Sade, Fourier, Loyola* (1971).
- Michel de Certeau, "L'espace du désir ou le 'fondement' des Exercices spirituels" (*Christus*, 1973).
- C. G. Jung, *Jung on Ignatius of Loyola's Spiritual Exercises: Lectures Delivered at ETH Zurich,
  Volume 7: 1939–1940*, ed. Martin Liebscher (Princeton, 2023).
- Ignacio Iparraguirre, *Historia de los Ejercicios de San Ignacio* (1946–73): history of the
  practice, useful as a frame for the Spanish line.
- Louis J. Puhl, English translation (1951); William A. M. Peters (1967); David L. Fleming,
  *A Contemporary Reading* (1978).

### Tier D: reference only

Everything not obtainable: bibliographic record plus paragraph range, so that the density bar still
counts it. Gerard Manley Hopkins's notes on the Exercises (written 1880–81, first published 1959) need
a rights check before anything beyond tier D (UK rule for works first published posthumously).

## 6. Tools (as in Ignatiana and the Woodstock Letters, without the AI dialogue)

- **Concordance with KWIC** over tier A, and over tier C once copies are opened; canonical citation on
  every line (`SpEx [23]`, `Przywara DSM I, 112`).
- **Full-text search** with Pagefind, built at deploy (Woodstock pattern).
- **Translation atlas** (new): how key words are rendered across translations 1914–1978:
  *indiferentes* [23], *afecciones desordenadas* [1], *consolación* / *desolación* [316]–[317],
  *sentir* [2], [352], *composición viendo el lugar* [47]. Single words only, so protected translations
  can be included under the quotation right.
- **Reception curve** per paragraph group and decade (§3.2).
- **Citation network:** who answers whom. Candidate edges to verify: Przywara → Balthasar; Hugo
  Rahner ↔ Jung (Eranos); Fessard → Certeau → Barthes; Karl Rahner on the logic of election.
- **Concept atlas** after the Jung-site model, over tier A plus opened copies.
- **Reading paths**, each station with a reason and a guiding question. Drafts:
  1. The Foundation [23] in the twentieth century.
  2. The thirteenth rule [365] as a scandal and its readers.
  3. Discernment between theology and psychology (Jung, the Rahners, Meissner later).
  4. Exercises and politics, 1930–1975 (Spain in the 1930s, *Mens nostra*, Arrupe, GC 32).
  5. Two commentaries on the *Anima Christi*, 1938–39: Przywara and Jung.
  Built (22 November 2026, `data/paths.json`, `#/paths`): the Foundation; hell through the five senses;
  the colloquy; discernment between theology and psychology; the thirteenth rule; the retreat as an
  institution 1916–1929. Paths 4 and 5 of the drafts wait for their material. The introduction essay
  (`#/intro`) reports what the margin shows so far, including where it contradicts claim 1 of §1: outside
  the running commentaries the Two Standards, the Three Classes and the thirteenth rule are thinly glossed.
- **Plates from the start** (public domain): title pages of the Vulgate 1548, Rickaby 1915, Longridge
  1919, Joyce 1916; AAS pages of 1922 and 1929; retreat houses before 1931 (verify images).
- **Data download** as one archive with manifest, as in Ignatiana.

## 7. The Jung line

Two layers, both linked rather than reproduced:

1. **Collected Works.** A scan of the operator's copy of the Complete Digital Edition finds Ignatius,
   Loyola, *Exercitia* or "Spiritual Exercises" in roughly 40 places across twelve volumes, index pages
   excluded. Main stations, mapped through the Jung site's anchor table:
   - CW 8 §395: the vision of the serpent with many eyes
   - CW 9i §232–238: "Concerning Rebirth", the *Exercitia*
   - CW 11: several places between §779 and §958
   - CW 13 §293
   - CW 18 §1536–1549
   Done (22 November 2026): the scan was rerun and the passages read; 28 glosses in
   `data/src/jung_cw.json`, paragraph numbers read from the page, summaries only. Passages where
   "spiritual exercises" is generic are left out. Findings: Jung quotes the Exercises in Rickaby's
   second edition (1923) throughout (CW 9ii, 13, 14); the stations cluster on the Foundation [23],
   the colloquy [53–54], the hell meditation and the senses [65–71, 121–126, 247–248], and, by way
   of the serpent vision of the Autobiography, on discernment. The deep link into the Jung site
   waits for the address of the operator's own deploy.
2. **ETH lectures 1939–40** (Liebscher 2023), tier C. Like Przywara's first volume, they take up the
   *Anima Christi*; whether Jung knew Przywara's work is to be checked in Liebscher's apparatus.

## 8. Relation to the sister sites

- **Ignatiana:** source of the centre text (`exercitia.json`) and of Longridge. Two-way links: from
  `SpEx [n]` in Ignatiana to `#/spex/n` here, and back.
- **Jung site (collected-works):** deep links by `CW n §m`. Do not link `collected-works.netlify.app`,
  which belongs to someone else; use the address of the user's own deploy.
- **Woodstock Letters:** retreat practice in the American province up to 1930 (tier A, already
  searchable there); glosses can point into it.

## 9. Licences (planned)

Code MIT; editorial texts (summaries, introduction, paths) CC BY 4.0; derived data (anchor tables,
gloss index) CC0; public-domain texts as such. No copyrighted text in the repository.

## 10. Phases

1. **Frame:** reader with centre text from Ignatiana, gloss model, density bar, filters, tier-B link
   layer (Geist und Leben, The Way, Studies), tier-A texts Rickaby, Longridge, Feder (German layer),
   *Summorum Pontificum* 1922, *Mens nostra* 1929, Joyce, RAM vols. 1–4. Plates.
2. **First own-copy work:** anchor table for Przywara, *Deus semper maior* I–III; then Karl Rahner
   1965 and Fessard.
3. **Jung module:** Collected Works stations and ETH lectures.
4. Translation atlas, network, reading paths, introduction essay.

## 11. Open questions

- End date 1978 or 2000?
- German translation layer: done (stage 1b, 21 November 2026), Feder 1922, paragraph-exact. Open: the
  residual reading errors of the microfilm OCR (a better scan of the 1921/22 editions would help) and
  Feder's italics (translator's additions). His endnotes are in (108 notes, `tools/feder_notes.py`),
  placed page-exact by the page of the call, since the calls were not kept in the text; a paragraph-exact
  placement would need the call marks read from the page images.
- Should the 1928 numbering be told as its own story (who introduced it, in which edition)? It would
  make claim 2 of §1 checkable.
- Name: *Annotationes* is a working title.
