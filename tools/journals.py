# -*- coding: utf-8 -*-
"""Crawl the free chronological archives of the Zeitschrift für Aszese und
Mystik (1926-1944) and Geist und Leben (1947-1978) and assign articles on the
Exercises to paragraphs of the 1928 grid from their titles alone.

Only bibliographic data are taken (rubric, author and title string, pages,
URL of the article page); no article text is fetched. The article pages are
stable; the PDF links on them carry a token that expires after a day, so the
apparatus links to the article page.

  python tools/journals.py crawl    fetch the issue lists -> tools/cache/journals_raw.json
  python tools/journals.py assign   raw list -> data/src/journals.json

The title rules below are deliberately narrow. An article the rules do not
recognise as being about the Exercises is left out rather than guessed; one
recognised as about the Exercises but not about a particular part goes to
"the book as a whole".
"""
import json, os, re, sys, time, html
import urllib.request
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', 'cache')
RAW = os.path.join(CACHE, 'journals_raw.json')
OUT = os.path.join(REPO, 'data', 'src', 'journals.json')
BASE = 'https://www.geist-und-leben.de/archiv/'
ROOTS = {'zam': BASE + 'archiv-zam/', 'gul': BASE + 'archiv-gul/'}
GUL_LAST_YEAR = 1978

def fetch(url):
    for k in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (research crawler; bibliographic data only)'})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception:
            time.sleep(2 + 3 * k)
    return ''

def children(page, base):
    out = []
    for h in re.findall(r'href="([^"]+)"', page):
        h = html.unescape(h).split('?')[0]
        if h.startswith(base) and h != base and len(h[len(base):].strip('/').split('/')) == 1 and h not in out:
            out.append(h)
    return out

def articles(page, issue):
    """Article entries of an issue page: the breadcrumb-style label text of each link."""
    out, seen = [], set()
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', page, re.S):
        h = html.unescape(m.group(1)).split('?')[0]
        t = re.sub(r'<[^>]+>', ' ', m.group(2))
        t = re.sub(r'\s+', ' ', html.unescape(t)).strip()
        if not h.startswith(issue) or h == issue or h in seen or not t or t.lower() == 'pdf' or t == 'Anzeigen':
            continue
        seen.add(h)
        out.append({'url': h, 'label': t})
    return out

def crawl():
    os.makedirs(CACHE, exist_ok=True)
    raw = []
    with ThreadPoolExecutor(6) as ex:
        for j, root in ROOTS.items():
            vols = children(fetch(root), root)
            if j == 'gul':
                vols = [v for v in vols if (m := re.search(r'gul-\d+-(\d{4})', v)) and int(m.group(1)) <= GUL_LAST_YEAR]
            issues = []
            for v, page in zip(vols, ex.map(fetch, vols)):
                issues += [(v, i) for i in children(page, v)]
            for (v, i), page in zip(issues, ex.map(fetch, [i for _, i in issues])):
                for a in articles(page, i):
                    raw.append({'journal': j, 'vol': v.rstrip('/').rsplit('/', 1)[1],
                                'issue': i.rstrip('/').rsplit('/', 1)[1], **a})
            print(j, len(vols), 'volumes', len(issues), 'issues', sum(r['journal'] == j for r in raw), 'entries', flush=True)
    with open(RAW, 'w', encoding='utf-8') as f:
        json.dump(raw, f, ensure_ascii=False, indent=0)

# ---------------------------------------------------------------- assignment
ON_EXX = re.compile(r'Exerziti|Exercit|geistlichen Übungen|ignatian|Ignatius|Loyola|Unterscheidung der Geister', re.I)
RULES = [  # (pattern, [from, to]); first match wins
    (r'Unterscheidung der Geister|Regeln zur Unterscheidung', [313, 336]),
    (r'Prinzip und Fundament|Fundament', [23, 23]),
    (r'Indifferen', [23, 23]),
    (r'zwei Banner|zwei Fahnen|Bannern|Fahnen', [136, 148]),
    (r'drei Menschenklassen|Menschenpaare|drei Paare', [149, 157]),
    (r'Demut', [165, 168]),
    (r'\bWahl\b|Wahlzeit|Lebenswahl|Election', [169, 189]),
    (r'Ruf des Königs|Reich Christi|Königsbetrachtung|Christ-?[Kk]önigs-?[Bb]etrachtung', [91, 100]),
    (r'Contemplatio ad amorem|Liebe zu erlangen|Erlangung der Liebe|Betrachtung über die Liebe', [230, 237]),
    (r'Vorbereitungsgebet', [46, 46]),
    (r'Vorbemerkungen', [1, 20]),
    (r'Anwendung der Sinne', [121, 126]),
    (r'Gewissenserforschung|Examen', [24, 43]),
    (r'Fühlen mit der Kirche|kirchlichen Sinn|sentire cum ecclesia|Regeln.{0,20}Kirche', [352, 370]),
    (r'erste[nr]? Woche', [24, 90]),
    (r'zweite[nr]? Woche', [91, 189]),
    (r'dritte[nr]? Woche', [190, 217]),
    (r'vierte[nr]? Woche', [218, 237]),
    (r'Exerzitienleiter|Exerzitiengeber|Exerzitienmeister|Annotation', [1, 20]),
]
SKIP = re.compile(r'^(Besprechungen|Buchbesprechungen|Literaturnachweis|Literaturbericht|Bücher|Neue Bücher|Inhalt|Register)', re.I)
# Ignatian items about the life, the Diary, the Constitutions or the cult rather
# than the book and its practice. The reception of the Exercises in the wider
# sense (Ignatian prayer, asceticism, mysticism) stays in.
NOT_BOOK = re.compile(r'Tagebuch|Storta|Ordenssatzungen|Briefwechsel|Biographie|Fürsten|Volksfrömmigkeit|'
                      r'innere[nr]? Entwicklung|persönlich|Ignatiusfest|Ein Wort des hl|Canisius|^Ignatius von Loyola$', re.I)
KEEP_IGN = re.compile(r'Mystik|Frömmigkeit|Spiritualität|Gebet|Betracht|Aszese|aszetisch|Gleichmut|Heiligkeit|'
                      r'Kirche|Christologie|Gnadenführung|Grundhaltung|Gottesliebe|Wort als Frage|Unruhe', re.I)
EXX_PROPER = re.compile(r'Exerziti|Exercit|geistlichen Übungen|Unterscheidung der Geister|Fundament|Königs-?[Bb]etrachtung', re.I)
PARTICLES = {'von', 'v.', 'de', 'van', 'zu', 'vom', 'der'}
NAMES = ['Franz Joseph Schierse']   # names the rule below would cut wrongly

def parse(label):
    rubric, _, rest = label.partition(' | ')
    if not rest:
        rubric, rest = '', label
    m = re.search(r'\s*\[(\d+\*?\s*[−–-]\s*\d+\*?|\d+\*?)\]', rest)
    pages = re.sub(r'\s', '', m.group(1)).replace('−', '–').replace('-', '–') if m else ''
    head = rest[:m.start()] if m else rest
    return rubric.strip(), head.strip(), pages

def split_author(head):
    """The archive gives 'Author Title' as one string. Names are taken as the
    leading run of capitalised words, initials and particles, at most two
    plain words unless a particle or initial precedes."""
    if head.startswith('['):
        a, _, t = head[1:].partition(']')
        return a.strip(), t.strip()
    if head.startswith('Die deutschen Bischöfe '):
        return 'Die deutschen Bischöfe', head[len('Die deutschen Bischöfe '):]
    for full in NAMES:
        if head.startswith(full + ' '):
            return full, head[len(full) + 1:]
    toks, author, surname, plain = head.split(' '), [], False, 0
    for t in toks:
        initial = bool(re.fullmatch(r'(?:[A-ZÄÖÜ][a-zäöü]{0,4}\.)+(?:[A-Z]\.)*', t))
        particle = t in PARTICLES
        cap = bool(re.match(r'[A-ZÄÖÜÉ][\w\-éèàäöü]*$', t))
        prev = author[-1] if author else ''
        if surname and not particle and prev not in PARTICLES:
            break                      # the surname has been read; only a particle (and its name) may follow
        if particle or (initial and not surname):
            author.append(t)
            continue
        if cap:
            author.append(t)
            plain += 1
            if prev in PARTICLES or prev.endswith('.') or plain == 2:
                surname = True
            continue
        break
    if len(author) < 2 or author[-1] in PARTICLES:
        return '', head
    return ' '.join(author), ' '.join(toks[len(author):])

def assign():
    raw = json.load(open(RAW, encoding='utf-8'))
    out = []
    for r in raw:
        rubric, head, pages = parse(r['label'])
        if SKIP.match(head) or SKIP.match(rubric) or not ON_EXX.search(head) or NOT_BOOK.search(head):
            continue
        author, title = split_author(head)
        if not EXX_PROPER.search(title) and not KEEP_IGN.search(title):
            continue
        spex = None
        for pat, rng in RULES:
            if re.search(pat, title, re.I):
                spex = rng
                break
        vm = re.search(r'(zam|gul)-(\d+)-(\d{4})', r['vol'])
        vol, year = int(vm.group(2)), int(vm.group(3))
        name = 'Zeitschrift für Aszese und Mystik' if r['journal'] == 'zam' else 'Geist und Leben'
        slug = re.sub(r'[^a-z0-9]+', '-', r['url'].rstrip('/').rsplit('/', 1)[1].lower())[:60]
        out.append({
            'id': f"{r['journal']}-{year}-{slug}".rstrip('-'),
            'work': r['journal'], 'spex': spex, 'basis': 'title',
            'author': author, 'title': title, 'year': year,
            'loc': f"{name} {vol} ({year}){', pp. ' + pages if pages else ''}" + (f' · {rubric}' if rubric else ''),
            'url': r['url'], 'note': '',
        })
    seen, uniq = set(), []
    for g in out:
        if g['id'] in seen:
            continue
        seen.add(g['id'])
        uniq.append(g)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'_note': 'Generated by tools/journals.py assign: bibliographic data only, assigned from titles.',
                   'glosses': uniq}, f, ensure_ascii=False, indent=1)
    placed = sum(1 for g in uniq if g['spex'])
    print(f'{len(uniq)} articles on the Exercises, {placed} placed on paragraphs -> data/src/journals.json')

if __name__ == '__main__':
    {'crawl': crawl, 'assign': assign}[sys.argv[1]]()
