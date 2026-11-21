# -*- coding: utf-8 -*-
"""Put Feder's translation (Regensburg 1922) on the grid [1]-[370].

Feder translated from the Spanish autograph and kept its divisions, but his
book predates the 1928 numbering. The editorial anchor table
tools/feder_anchors.json gives, for every canonical paragraph, the words with
which it begins in Feder's text, or the printed paragraph it has to be split
from; it was compiled by reading the two texts side by side. This script
applies it and writes data/feder.json.

Usage: python -P tools/feder_align.py <fixed.json> <tools/feder_anchors.json> <data/feder.json>
"""
import json, re, sys
from difflib import SequenceMatcher

def norm(s):
    return re.sub(r'[^0-9a-zäöüß]', '', s.lower())

def starts(text, anchor):
    """Tolerant: the OCR clean-up may change punctuation and spacing after the table was made."""
    a = norm(anchor)[:24]
    t = norm(text[:80])[:len(a)]
    return t == a or SequenceMatcher(None, a, t).ratio() >= 0.7

def find_at(text, at):
    pat = r'[^0-9A-Za-zÄÖÜäöüß]*'.join(re.escape(c) for c in at if c.isalnum())
    m = re.search(pat, text)
    return m.start() if m else -1

def main(src, anchors, out):
    B = [b for b in json.load(open(src, encoding='utf-8')) if b['page'] >= 19]
    A = json.load(open(anchors, encoding='utf-8'))

    # 1. splits
    for n, sp in sorted(A['split'].items(), key=lambda x: int(x[0])):
        i = next(i for i, b in enumerate(B) if starts(b['text'], sp['block']) and find_at(b['text'], sp['at']) > 0)
        k = find_at(B[i]['text'], sp['at'])
        assert k > 0, (n, sp)
        head, tail = B[i]['text'][:k].rstrip(" ,;:'\"«»f"), B[i]['text'][k:]
        B[i:i + 1] = [dict(B[i], text=head), dict(B[i], text=tail, split_for=int(n))]

    # 2. where each canonical paragraph begins
    begin, pos = {}, 0
    for n in range(1, 371):
        key = str(n)
        if key in A['start']:
            # exact opening (14 letters) within the next blocks first; else the closest opening there
            a = norm(A['start'][key])
            window = range(pos, min(len(B), pos + 25))
            i = next((i for i in window if norm(B[i]['text'][:80]).startswith(a[:14])), None)
            if i is None:
                best = max(((SequenceMatcher(None, a[:24], norm(B[i]['text'][:80])[:24]).ratio(), i) for i in window),
                           default=(0, None))
                i = best[1] if best[0] >= 0.6 else None
        elif key in A['split']:
            i = next((i for i in range(pos, len(B)) if B[i].get('split_for') == n), None)
        else:
            continue
        assert i is not None, f'[{n}] not found after block {pos}'
        begin[n] = i
        pos = i + 1

    # 3. cut
    order = sorted(begin)
    units = []
    for n in range(1, 371):
        if n not in begin:
            units.append({'n': n, 'de': '', 'pages': [], 'missing': A['empty'].get(str(n), '')})
            continue
        j = order.index(n)
        lo = 0 if j == 0 else begin[n]                  # the heading before [1] belongs to [1]
        hi = begin[order[j + 1]] if j + 1 < len(order) else len(B)
        blocks = B[lo:hi]
        units.append({'n': n, 'de': ' '.join(b['text'] for b in blocks).strip(),
                      'pages': sorted({p for b in blocks for p in b['pages']})})
    doc = {
        'titel': 'Ignatius von Loyola, Geistliche Übungen, übertragen von Alfred Feder SJ (Regensburg 1922)',
        'quelle': 'Ignatius von Loyola, Geistliche Übungen. Nach dem spanischen Urtext übertragen, eingeleitet und mit '
                  'Anmerkungen versehen von Alfred Feder S. J. Zweite, verbesserte und erweiterte Auflage. Regensburg: '
                  'Verlagsanstalt vorm. G. J. Manz, 1922. Text from the University of Chicago microfilm, Internet Archive '
                  'MN5044ucmf_5 (ABBYY OCR), cleaned by tools/feder_extract.py and tools/feder_fix.py.',
        'vorlage_status': 'Public domain in the United States (published 1922) and in Germany (the translator died in 1927).',
        'hinweis': 'Machine-read from a microfilm and corrected by dictionary; residual reading errors remain. Feder printed '
                   'words he supplied in italics; the italics are not reproduced. His footnotes (mostly scripture '
                   'references) and his endnotes are left out. Page numbers are those of the 1922 edition.',
        'units': units,
    }
    json.dump(doc, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(sum(1 for u in units if u['de']), 'of 370 paragraphs filled ->', out)
    # keep the table in step with the cleaned text, so later corrections do not drift from it
    for n, i in begin.items():
        if str(n) in A['start']:
            A['start'][str(n)] = B[i]['text'][:32]
    json.dump(A, open(anchors, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main(*sys.argv[1:4])
