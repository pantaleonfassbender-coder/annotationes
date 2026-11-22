# -*- coding: utf-8 -*-
"""Przywara's own index of the numbers of the Exercises (Deus semper maior III, pp. 438-440).

Reads the hand transcription data/src/przywara_register.txt and writes data/src/przywara_register.json:
one entry per line of the index, with the paragraphs it names and its references by volume and page;
pages set in italics in the index (marked *…* in the transcription) are kept as 'main'.

'f.' is read as the page and the next, 'ff.' as the page and the two after it (Przywara gives no end),
'bis' joins two pages into a range. The index uses the 1928 numbering, so the entries go onto the grid
as they stand.

Usage: python -P tools/przywara_register.py data/src/przywara_register.txt data/src/przywara_register.json
"""
import json, re, sys

ROMAN = {'I': 1, 'II': 2, 'III': 3}

def parse_refs(s):
    refs = []
    for part in s.split(';'):
        part = part.strip().rstrip('.')
        m = re.match(r'(III|II|I)\s+(.*)$', part)
        if not m:
            raise ValueError('no volume in: ' + part)
        vol, rest = ROMAN[m.group(1)], m.group(2)
        rest = re.sub(r'\s+bis\s+', ' bis ', rest)
        toks = rest.split()
        i = 0
        while i < len(toks):
            t = toks[i]
            main = t.startswith('*')
            t = t.strip('*')
            if t in ('f.', 'ff.', 'f', 'ff'):
                refs[-1]['to'] = refs[-1]['from'] + (1 if t.rstrip('.') == 'f' else 2)
                refs[-1]['open'] = t.rstrip('.') == 'ff'
                i += 1; continue
            if t == 'bis':
                nxt = toks[i + 1].strip('*')
                refs[-1]['to'] = int(nxt); refs[-1]['main'] = refs[-1]['main'] or toks[i + 1].startswith('*')
                i += 2; continue
            a, _, b = t.partition('-')
            refs.append({'vol': vol, 'from': int(a), 'to': int(b) if b else int(a), 'main': main, 'open': False})
            i += 1
    return refs

def main(src, out):
    entries = []
    for line in open(src, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        key, _, refs = line.partition(':')
        a, _, b = key.partition('-')
        entries.append({'spex': [int(a), int(b or a)], 'printed': refs.strip(), 'refs': parse_refs(refs)})
    for e in entries:
        for r in e['refs']:
            assert r['to'] >= r['from'], e
    doc = {'_note': "Erich Przywara, Deus semper maior III (Freiburg: Herder, 1940), pp. 438-440, 'Nummern des "
                    "Exerzitientextes': transcribed by hand from the borrowed Internet Archive scan "
                    "(deussempermaiort0003eric) on 22 November 2026, as no usable OCR exists. A register of page "
                    "numbers (CC0). 'main' marks pages the index sets in italics. 'f.' is read as two pages, "
                    "'ff.' as three with 'open' set, since the index gives no end.",
           'entries': entries}
    json.dump(doc, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    cov = {n for e in entries for n in range(e['spex'][0], e['spex'][1] + 1)}
    print(len(entries), 'entries;', len(cov), 'paragraphs named; not named:', [n for n in range(1, 371) if n not in cov])

if __name__ == '__main__':
    main(*sys.argv[1:3])
