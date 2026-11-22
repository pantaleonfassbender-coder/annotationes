# -*- coding: utf-8 -*-
"""Build data/atlas.json, the concept atlas of the apparatus, after the atlas of the Woodstock
Letters edition (tools/build_atlas.py there).

Woodstock has one language and a full text, so its terms are chosen by keyness. The margin here
is in six languages and mostly made of short glosses, so the terms are a fixed lexicon of the
concepts of the Exercises and their reception (CONCEPTS below), each with its spellings in English,
German, Spanish, Italian, French and Latin. The lexicon is editorial; it says what was looked for.

Units. Every gloss is a unit (title, note and quote), except where the apparatus holds the work's
own text: there each paragraph of the text is a unit (Longridge 1919, Rickaby's notes, Feder's
endnotes). Przywara's index entries carry no words and are left out.

Edges. Two concepts are joined when they occur in the same unit more often than chance allows
(positive pointwise mutual information over units, at least MIN_CO shared units); each concept keeps
its strongest PER_TERM links.

Every concept carries its spread over the parts of the book (the sections of data/exercitia.json)
and over decades, the paragraphs and glosses where it is most frequent, and its centre of gravity:
the family of works (commentaries; journals and papal documents; history and philosophy; psychology
and literature) in which its share of units, smoothed by SMOOTH, is highest. The commentaries held in
full give most of the units, so the families are compared by share, not by count. Derived data, CC0.

Usage: python -P tools/build_atlas.py
"""
import json, math, os, re, unicodedata
from collections import Counter, defaultdict
from itertools import combinations

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(REPO, 'data', *p)
MIN_CO = 3
MIN_F = 4         # units a concept must occur in to enter the atlas
PER_TERM = 8
SMOOTH = 20       # added to each family's unit count when the centre of gravity is computed

FAMILY = {'commentary': 'commentary', 'translation': 'commentary', 'journal': 'journal',
          'history': 'history', 'philosophy': 'history', 'psychology': 'psychology',
          'literature': 'psychology', 'magisterium': 'journal'}
FAMILIES = ['commentary', 'journal', 'history', 'psychology']

# id: (label, [patterns on lower-cased text with accents removed])
CONCEPTS = {
 'foundation': ('Principle and Foundation', [r'\bfoundation', r'fundament', r'principio y fundamento', r'principium et fundamentum']),
 'end-of-man': ('end of man', [r'end of man', r'man (?:is|was) created', r'creatus est', r'fin del hombre', r'ziel des menschen', r'endziel', r'last end']),
 'indifference': ('indifference', [r'indifferen', r'indiferen', r'gleichmut', r'adiaphor']),
 'glory': ('glory of God', [r'\bglory', r'\bgloria', r'herrlichkeit', r'ehre gottes', r'\bdoxa', r'maiorem']),
 'magis': ('the more (magis)', [r'\bmagis\b', r'\bthe more\b', r'je mehr']),
 'sin': ('sin', [r'\bsins?\b', r'pecado', r'peccat', r'\bsunde', r'\bsunden']),
 'hell': ('hell', [r'\bhell\b', r'infierno', r'inferno', r'\bholle', r'damn']),
 'death-judgment': ('death and judgment', [r'\bdeath\b', r'\bmuerte', r'\btod\b', r'judgment', r'judgement', r'juicio', r'gericht']),
 'senses': ('the five senses', [r'\bsenses\b', r'sentidos', r'\bsinne', r'application of the senses', r'aplicacion de (?:los )?sentidos', r'\bsmell', r'\btaste']),
 'imagination': ('imagination and composition of place', [r'imagina', r'composition of (?:the )?place', r'composicion de lugar', r'compositio loci', r'phantasie', r'einbildung', r'vorstellung des ortes']),
 'active-imagination': ('active imagination', [r'active imagination', r'aktive imagination']),
 'colloquy': ('colloquy', [r'colloqu', r'coloquio', r'zwiegesprach', r'zwiesprache']),
 'examen': ('examen', [r'\bexamen', r'examination of conscience', r'gewissenserforschung', r'\berforschung']),
 'meditation': ('meditation', [r'meditat', r'meditacion', r'betrachtung']),
 'contemplation': ('contemplation', [r'contemplat', r'contemplacion', r'beschauung']),
 'methods-of-prayer': ('methods of prayer', [r'methods? of prayer', r'modos? de orar', r'gebetsweise', r'manner of praying']),
 'consolation': ('consolation', [r'consol', r'\btrost', r'getrost']),
 'desolation': ('desolation', [r'desola', r'trostlos']),
 'discernment': ('discernment of spirits', [r'discern', r'discrecion', r'discretio', r'unterscheidung', r'spirits\b', r'(?:good|evil|bad) spirit']),
 'angel-of-light': ('the enemy as angel of light', [r'angel of light', r'angel de luz', r'engel des lichts', r'serpent', r'schlange']),
 'enemy': ('enemy and Lucifer', [r'\benemy', r'enemigo', r'\bfeind', r'lucifer', r'\bdevil', r'demon', r'teufel', r'\bsatan']),
 'election': ('election', [r'\belection', r'eleccion', r'elezione', r'\belectio', r'\bwahl', r'lebenswahl', r'standeswahl']),
 'state-of-life': ('state of life and vocation', [r'state of life', r'states of life', r'estado de vida', r'lebensstand', r'vocation', r'vocacion', r'berufung']),
 'disordered': ('disordered attachment', [r'inordinate', r'disordered', r'desordenad', r'ungeordnet', r'attachment', r'afeccion']),
 'kingdom': ('Kingdom of Christ', [r'kingdom', r'\breino', r'\bregno', r'reich christi', r'reiche christi', r'regnum', r'konigsbetrachtung', r'christkonig']),
 'king': ('the King', [r'\bking\b', r'\bkings\b', r'\brey\b', r'\bkonig\b', r'\bkonigs\b', r'\brex\b']),
 'standards': ('Two Standards', [r'two standards', r'dos banderas', r'banderas', r'zwei (?:banner|fahnen)', r'\bstandard\b', r'duobus vexillis']),
 'three-classes': ('Three Classes', [r'three classes', r'three pairs', r'binarios', r'menschenklassen', r'menschenpaare']),
 'humility': ('humility', [r'humilit', r'humildad', r'umilta', r'\bdemut']),
 'poverty': ('poverty', [r'poverty', r'pobreza', r'poverta', r'\barmut', r'paupertas']),
 'obedience': ('obedience', [r'obedien', r'gehorsam', r'obbedien']),
 'love': ('love', [r'\blove\b', r'\bamor\b', r'\bamore\b', r'\bliebe\b', r'caritas', r'charity']),
 'following': ('following Christ', [r'imitation', r'imitatio', r'nachfolge', r'follow(?:ing)? (?:of )?christ', r'seguir a cristo', r'sequela']),
 'cross': ('cross and passion', [r'\bcross\b', r'\bcruz\b', r'\bcroce', r'\bkreuz', r'\bpassion', r'\bpasion', r'crucif']),
 'resurrection': ('resurrection', [r'resurrect', r'resurreccion', r'auferstehung', r'risen']),
 'mary': ('Our Lady', [r'our lady', r'virgin', r'virgen', r'madonna', r'muttergottes', r'mutter gottes', r'\bmaria\b', r'\bmary\b']),
 'incarnation': ('incarnation and nativity', [r'incarnat', r'encarnacion', r'menschwerdung', r'nativity', r'nacimiento', r'geburt christi']),
 'church': ('the Church', [r'\bchurch', r'iglesia', r'chiesa', r'\bkirche', r'ecclesia']),
 'hierarchy': ('hierarchy and authority', [r'hierarch', r'jerarqu', r'authority', r'autoridad', r'autoritat']),
 'catholic-action': ('Catholic Action', [r'catholic action', r'katholische aktion', r'accion catolica', r'actio catholica']),
 'social': ('workers and the social question', [r'worker', r'obrero', r'arbeiter', r'social question', r'problema social', r'soziale frage', r'working']),
 'leader': ('leader and following (Fuhrer, Gefolgschaft)', [r'fuhrer', r'gefolgschaft', r'gefolgsmann', r'\bleader']),
 'knight': ('knight and soldier', [r'knight', r'caballer', r'\britter', r'soldier', r'soldado', r'soldat', r'militar', r'military', r'crusade', r'kreuzzug']),
 'heroism': ('the heroic', [r'\bhero', r'heroi', r'heldisch', r'\bheld']),
 'freedom': ('freedom', [r'freedom', r'liberty', r'libertad', r'liberta', r'freiheit']),
 'will-of-god': ('the will of God', [r'will of god', r'voluntad de dios', r'willen? gottes', r'divine will', r'gottes willen']),
 'perfection': ('perfection', [r'perfection', r'perfeccion', r'vollkommen']),
 'mysticism': ('mysticism', [r'mystic', r'mistic', r'mystik']),
 'asceticism': ('asceticism', [r'ascetic', r'ascetica', r'ascetique', r'aszese', r'aszetik', r'ascese']),
 'method': ('method', [r'\bmethod', r'\bmetodo', r'\bmethode', r'methodus']),
 'retreat': ('the retreat as institution', [r'\bretreats?\b', r'retiro', r'casas? de ejercicios', r'exerzitienhaus', r'exerzitienbewegung', r'ritiro', r'retraite']),
 'director': ('the one who gives the Exercises', [r'director', r'\bgiver\b', r'who gives', r'exerzitienmeister', r'exerzitiengeber', r'el que da']),
 'manresa': ('Manresa', [r'manresa']),
 'sources': ('sources and origins of the book', [r'\bsources?\b', r'fuentes?\b', r'\bquellen?\b', r'origins?\b', r'origenes', r'entstehung', r'borrow', r'antecedent']),
 'cisneros': ('Cisneros and the Ejercitatorio', [r'cisneros', r'ejercitatorio', r'montserrat']),
 'ludolph': ('Ludolph and the Flos Sanctorum', [r'ludol', r'vita christi', r'flos sanctorum', r'legenda aurea']),
 'devotio-moderna': ('Devotio moderna', [r'devotio moderna', r'common life', r'mauburn', r'mombaer', r'kempis', r'imitation of christ']),
 'fathers': ('the Fathers', [r'church fathers', r'fathers of the church', r'kirchenvater', r'patristi', r'augustin', r'\bbasil']),
 'scholastic': ('Aquinas and scholastic philosophy', [r'aquinas', r'thomas', r'scholast', r'escolast', r'thomist']),
 'scripture': ('Scripture and the Gospels', [r'scripture', r'escritura', r'heilige schrift', r'\bgospel', r'evangeli', r'\bpaul\b', r'paulus', r'pauline']),
 'liturgy': ('liturgy', [r'liturg']),
 'autograph': ('the text and its editions', [r'autograph', r'autografo', r'vulgat', r'monumenta', r'critical edition', r'translation']),
 'unconscious': ('the unconscious and the self', [r'unconscious', r'unbewusst', r'inconsciente', r'\bthe self\b', r'\bego\b', r'psycholog', r'psicolog']),
 'grace': ('grace', [r'\bgrace', r'\bgracia', r'\bgrazia', r'\bgnade', r'\bgratia']),
 'holy-spirit': ('the Holy Spirit', [r'holy spirit', r'holy ghost', r'espiritu santo', r'heiligen? geist', r'spiritu sancto', r'spirito santo']),
 'scruples': ('scruples', [r'scrupl', r'escrupul', r'skrupel']),
 'alms': ('alms', [r'\balms', r'limosna', r'almosen', r'elemosin']),
 'tears': ('tears and compunction', [r'\btears\b', r'lagrimas', r'tranen', r'compunction', r'contrition', r'reue']),
 'world': ('the world', [r'\bworld\b', r'\bmundo\b', r'\bwelt\b', r'\bmondo\b', r'weltfreud', r'weltflucht']),
 'communal': ('discernment in common', [r'communal', r'in common', r'gemeinschaft', r'community', r'group']),
}
COMPILED = {k: re.compile('|'.join(p)) for k, (_, p) in CONCEPTS.items()}

def fold(s):
    s = unicodedata.normalize('NFD', s.lower().replace('ß', 'ss'))
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')

def load(p):
    return json.load(open(p, encoding='utf-8'))

def main():
    works = {w['id']: w for w in load(D('works.json'))['works']}
    glosses = load(D('glosses.json'))['glosses']
    ex = load(D('exercitia.json'))
    sections = [(s['id'], s['von'], s['bis'], s['titel_en']) for s in ex['sections']]
    units = []      # (text, work, year, spex, gloss id or None)
    full = {'longridge-1919', 'rickaby-1915'}
    for g in glosses:
        if g['work'] in full or g['id'].startswith('feder-note-') or g['id'].startswith('przywara-r'):
            continue
        t = ' '.join(str(g.get(k) or '') for k in ('title', 'note', 'quote'))
        w = works[g['work']]
        units.append((t, g['work'], g.get('year') or w.get('year'), g.get('spex'), g['id']))
    for sec in load(D('longridge_exx.json'))['sections'].values():
        for blk in sec:
            for p in blk['paras']:
                units.append((p['s'], 'longridge-1919', 1919, [blk['von'], blk['bis']], None))
    for e in load(D('rickaby_exx.json'))['entries']:
        r = e['runs'][0] if e['runs'] else None
        for p in e['paras']:
            units.append((p, 'rickaby-1915', 1923, r, None))
    for e in load(D('feder_notes.json'))['entries']:
        for p in e['paras']:
            units.append((p, 'feder-1922', 1922, e.get('spex'), None))

    occ = []         # per unit: set of concepts
    for t, *_ in units:
        ft = fold(t)
        occ.append({k for k, rx in COMPILED.items() if rx.search(ft)})
    N = len(units)
    f = Counter(k for s in occ for k in s)
    fam_units = Counter(FAMILY[works[u[1]]['genre']] for u in units)
    co = Counter()
    for s in occ:
        for a, b in combinations(sorted(s), 2):
            co[(a, b)] += 1
    edges = []
    for (a, b), n in co.items():
        if n < MIN_CO or f[a] < MIN_F or f[b] < MIN_F:
            continue
        pmi = math.log2(n * N / (f[a] * f[b]))
        if pmi > 0:
            edges.append({'s': a, 't': b, 'f': n, 'pmi': round(pmi, 2)})
    # keep each concept's strongest links
    keep = set()
    by = defaultdict(list)
    for i, e in enumerate(edges):
        by[e['s']].append(i); by[e['t']].append(i)
    for k, ix in by.items():
        ix.sort(key=lambda i: -edges[i]['pmi'] * math.log(1 + edges[i]['f']))
        keep.update(ix[:PER_TERM])
    edges = [edges[i] for i in sorted(keep)]

    decades = list(range(1900, 1980, 10))
    nodes = []
    for k, (label, _) in CONCEPTS.items():
        if f[k] < MIN_F:
            continue
        idx = [i for i, s in enumerate(occ) if k in s]
        fam = Counter(FAMILY[works[units[i][1]]['genre']] for i in idx)
        # share of each family's units, smoothed so that a family with few units (the popes)
        # does not win on a single gloss
        share = {x: fam[x] / (fam_units[x] + SMOOTH) for x in FAMILIES}
        centre = max(share, key=share.get)
        sdist = [0] * len(sections)
        para = Counter()
        for i in idx:
            sp = units[i][3]
            if not sp:
                continue
            for n in range(sp[0], min(sp[1], sp[0] + 25) + 1):
                para[n] += 1 / (sp[1] - sp[0] + 1)
            for j, (_, a, b, _) in enumerate(sections):
                if sp[0] <= b and a <= sp[1]:
                    sdist[j] += 1
        ddist = [0] * len(decades)
        for i in idx:
            y = units[i][2]
            if isinstance(y, int) and 1900 <= y < 1980:
                ddist[(y - 1900) // 10] += 1
        gl = [units[i][4] for i in idx if units[i][4]]
        nodes.append({'id': k, 'label': label, 'f': f[k], 'sec': centre,
                      'fam': [fam[x] for x in FAMILIES], 'sdist': sdist, 'ddist': ddist,
                      'paras': [n for n, _ in para.most_common(10)],
                      'glosses': gl[:400]})
    doc = {'_note': 'Concept atlas of the apparatus (tools/build_atlas.py): co-occurrence of a fixed lexicon of '
                    'concepts in glosses and in the commentary paragraphs held in full. Derived data, CC0.',
           'units': N, 'families': FAMILIES, 'famUnits': [fam_units[x] for x in FAMILIES],
           'sections': [{'id': s[0], 'von': s[1], 'bis': s[2], 'title': s[3]} for s in sections],
           'decades': decades, 'nodes': nodes, 'edges': edges,
           'lexicon': {k: {'label': l, 'patterns': p} for k, (l, p) in CONCEPTS.items()}}
    json.dump(doc, open(D('atlas.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(N, 'units;', len(nodes), 'concepts;', len(edges), 'links ->', D('atlas.json'))
    for x in sorted(nodes, key=lambda n: -n['f'])[:12]:
        print(' ', x['id'], x['f'], x['sec'])
    print('rare:', [(x['id'], x['f']) for x in sorted(nodes, key=lambda n: n['f'])[:10]])

if __name__ == '__main__':
    main()
