# -*- coding: utf-8 -*-
"""Build data/glosses.json, the index the reader works from.

Sources:
  data/longridge_exx.json          Longridge 1919 (taken over from Ignatiana):
                                   one gloss per commentary block and per
                                   Additional Note; the text stays in that
                                   file and is loaded when a card is opened.
  data/feder_notes.json            Feder 1922's endnotes (tools/feder_notes.py).
  data/src/glosses_curated.json    hand-written glosses (notes CC BY 4.0).
  data/src/jung_cw.json            Jung's Collected Works, passages read (tier C: summaries only).
  data/src/journals.json           Zeitschrift für Aszese und Mystik and
                                   Geist und Leben articles, assigned from
                                   their titles (built by tools/journals.py).

Every gloss gets: id, work, spex ([from, to] or None), loc, basis, note and,
where present, quote, url, author, title, year, ref (where the full text is).
The script checks ranges against the grid [1]-[370] and work ids against
data/works.json, and stops on any error.

Usage: python tools/build_glosses.py
"""
import json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(REPO, 'data', *p)

def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

works = {w['id']: w for w in load(D('works.json'))['works']}
out, errors = [], []

# Longridge 1919: commentary blocks and Additional Notes.
L = load(D('longridge_exx.json'))
for sec, blocks in L['sections'].items():
    for i, b in enumerate(blocks):
        out.append({
            'id': f'longridge-{sec}-{i}', 'work': 'longridge-1919',
            'spex': [b['von'], b['bis']], 'loc': b.get('label', ''),
            'basis': 'section', 'label': b.get('label', ''),
            'note': '', 'ref': {'file': 'longridge_exx.json', 'section': sec, 'index': i},
        })
for n in L['notes']:
    out.append({
        'id': f'longridge-note-{n["id"]}', 'work': 'longridge-1919',
        'spex': [n['von'], n['bis']], 'loc': f'Additional Note {n["id"]}',
        'basis': 'section', 'label': f'Additional Note {n["id"]}: {n["titel"]}',
        'note': '', 'ref': {'file': 'longridge_exx.json', 'note': n['id']},
    })

# Rickaby 1923: one gloss per run of paragraphs a set of his notes follows (a set that
# follows text from two places of his rearranged book gives two glosses, same text).
RK = load(D('rickaby_exx.json'))
for i, e in enumerate(RK['entries']):
    pg = f'pp. {e["pages"][0]}–{e["pages"][1]}' if e['pages'][0] != e['pages'][1] else f'p. {e["pages"][0]}'
    for k, (a, b) in enumerate(e['runs']):
        out.append({
            'id': f'rickaby-{i}-{k}', 'work': 'rickaby-1915', 'year': 1923,
            'spex': [a, b], 'loc': pg, 'basis': 'matched',
            'label': f'Notes on [{a}]–[{b}]' if a != b else f'Notes on [{a}]',
            'note': '', 'ref': {'file': 'rickaby_exx.json', 'index': i},
        })

# Feder 1922: his endnotes, placed by the page that carries the call (data/feder_notes.json,
# built by tools/feder_notes.py). The card shows the opening; the whole note loads on demand.
FN = load(D('feder_notes.json'))
for i, e in enumerate(FN['entries']):
    t = e['paras'][0]
    cut = t if len(t) <= 260 else t[:t.rfind(' ', 0, 240)] + ' …'
    g = {'id': f'feder-note-{i}', 'work': 'feder-1922', 'spex': e['spex'], 'loc': f'note on p. {e["page"]}',
         'basis': 'page', 'note': '', 'quote': cut}
    if cut != t:
        g['ref'] = {'file': 'feder_notes.json', 'index': i}
    out.append(g)

# Przywara: the page anchor table (volume and pages where each part of the Exercises is treated).
PZ = load(D('src', 'przywara_anchors.json'))
ROMAN = {1: 'I', 2: 'II', 3: 'III'}
for i, a in enumerate(PZ['anchors']):
    pp = f'pp. {a["pp"][0]}–{a["pp"][1]}' if a['pp'][0] != a['pp'][1] else f'p. {a["pp"][0]}'
    out.append({
        'id': f'przywara-a{i}', 'work': 'przywara-dsm', 'spex': a['spex'],
        'loc': f'vol. {ROMAN[a["vol"]]}, {pp}', 'basis': 'toc', 'note': a['what'],
        'anchor': {'vol': a['vol'], 'pp': a['pp']},
    })

# Przywara's own index of the numbers of the Exercises (vol. III, pp. 438-440, transcribed by hand,
# tools/przywara_register.py). An entry becomes a gloss only where it adds to the anchor table: where it
# sends a paragraph to pages outside the sections the tables of contents assign to it.
def _ref(r):
    if r['open']:
        return f'{r["from"]} ff.'
    if r['to'] == r['from']:
        return str(r['from'])
    if r['to'] == r['from'] + 1:
        return f'{r["from"]} f.'
    return f'{r["from"]}–{r["to"]}'

def _refs(rs):
    by = {}
    for r in rs:
        by.setdefault(r['vol'], []).append(_ref(r))
    return '; '.join(f'{ROMAN[v]} {", ".join(p)}' for v, p in sorted(by.items()))

_ov = lambda a, b, c, d: a <= d and c <= b
for e in load(D('src', 'przywara_register.json'))['entries']:
    s0, s1 = e['spex']
    anc = [a for a in PZ['anchors'] if a['spex'] and _ov(a['spex'][0], a['spex'][1], s0, s1)]
    covered = lambda r: any(a['vol'] == r['vol'] and _ov(a['pp'][0], a['pp'][1], r['from'], r['to']) for a in anc)
    if all(covered(r) for r in e['refs']):
        continue
    main = [r for r in e['refs'] if r['main']]
    rest = [r for r in e['refs'] if not r['main']]
    rng = f'[{s0}]' if s0 == s1 else f'[{s0}]–[{s1}]'
    note = f"Przywara's own index of the numbers of the Exercises sends {rng} to "
    note += (f'{_refs(main)} (in italics in the index)' + (f', and to {_refs(rest)}' if rest else '')) if main else _refs(rest)
    note += '' if note.endswith('.') else '.'
    first = (main or e['refs'])[0]
    out.append({
        'id': f'przywara-r{s0}' + (f'-{s1}' if s1 != s0 else ''), 'work': 'przywara-dsm', 'spex': [s0, s1],
        'loc': 'vol. III, pp. 438–440 (index of numbers)', 'basis': 'index', 'note': note,
        'anchor': {'vol': first['vol'], 'pp': [first['from'], first['to']]},
    })

out += load(D('src', 'glosses_curated.json'))['glosses']
out += load(D('src', 'es_it.json'))['glosses']   # Spanish and Italian, before 1931 (tools/es_it.py)
# Jung: each passage links to its volume in the operator's Collected Works apparatus, which
# has no paragraph address (its deepest route is #/volumes/{n}).
JUNG_SITE = 'https://analysis-works-jung.netlify.app/#/volumes/'
for g in load(D('src', 'jung_cw.json'))['glosses']:
    vol = re.match(r'CW (\w+)', g['loc']).group(1)
    out.append({**g, 'url': JUNG_SITE + vol, 'linkLabel': f'CW {vol} in the Collected Works apparatus'})
if os.path.exists(D('src', 'journals.json')):
    out += load(D('src', 'journals.json'))['glosses']

seen = set()
for g in out:
    if g['id'] in seen:
        errors.append(f'duplicate id {g["id"]}')
    seen.add(g['id'])
    if g['work'] not in works:
        errors.append(f'{g["id"]}: unknown work {g["work"]}')
    s = g.get('spex')
    if s is not None and not (1 <= s[0] <= s[1] <= 370):
        errors.append(f'{g["id"]}: bad range {s}')
    if g.get('quote') and works.get(g['work'], {}).get('tier') != 'A':
        errors.append(f'{g["id"]}: quote outside a public-domain work')

if errors:
    print('\n'.join(errors))
    sys.exit(1)

with open(D('glosses.json'), 'w', encoding='utf-8') as f:
    json.dump({'_note': 'Generated by tools/build_glosses.py; do not edit by hand.',
               'glosses': out}, f, ensure_ascii=False, separators=(',', ':'))
by = {}
for g in out:
    by[g['work']] = by.get(g['work'], 0) + 1
print(f'{len(out)} glosses -> data/glosses.json')
for k, v in sorted(by.items(), key=lambda x: -x[1]):
    print(f'  {v:4d}  {k}')
