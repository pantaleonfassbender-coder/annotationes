# -*- coding: utf-8 -*-
"""Rickaby's English translation (2nd ed., 1923) on the paragraph grid [1]-[370].

Input: tools/cache/rickaby_raw.json, written by rickaby_extract.py. Its text blocks hold Rickaby's
English column for a run of paragraphs, and the positions where each paragraph opens in his Spanish
column (matched against the autograph). The English column has no paragraph numbers, so each block's
English is cut into paragraphs here:

1. the English is split into clauses (after . ; : ? ! followed by a space);
2. the paragraphs of the block are put in Rickaby's own order (by where they open in his Spanish);
   paragraphs whose opening was not found are slotted in after their predecessor;
3. a dynamic programme cuts the clause sequence into that many consecutive pieces so that each piece
   shares as many content words as possible with Mullan's English of the same paragraph
   (data/exercitia.json). Mullan only steers the cuts; no word of his is used.

A paragraph that Rickaby's order splits over two blocks gets both pieces. Machine-read text, not
corrected by hand.

Usage: python -P tools/rickaby_text.py tools/cache/rickaby_raw.json data/exercitia.json data/rickaby_text.json
"""
import json, re, sys
from collections import Counter

STOP = set('''a an the and or but of to in on at by for with from as is are was were be been being it its this that
these those he she him his her they them their we us our you your i me my who whom which what when where while
so than then there here not no nor all any each every some such shall will would should may might can could must
do does did have has had into upon unto also more most very own same other others one two three first second third
let made make himself themselves itself whether if because though although after before about against between
through during without within under over again further once only both few out up down off'''.split())

def words(s):
    return [w for w in re.findall(r"[a-z]+", s.lower()) if w not in STOP and len(w) > 2]

ABBR = r'(?:Matt|Mark|Luke|John|Cor|Acts|Rom|Gal|Eph|Phil|Col|Heb|Pet|Thess|Tim|Apoc|Gen|Exod|Ps|Is|vv|ver|vers|v|cf|ch|St|Cap|ibid)'
ORD = r'(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth)'

def clauses(text):
    """Split after sentence and clause ends (a closing quote may follow the stop) and before an
    ordinal opening such as 'The third', where Rickaby's paragraphs begin."""
    t = re.sub(r'''([.;:?!]['’”"]?)\s+''', r'\1\n', text.strip())
    # no cut after a Scripture reference's abbreviations ('Luke i. 38', 'Matt. xxvi. 26', 'vv. 46')
    t = re.sub(r'(?<![A-Za-z])((?:[ivxlc]+|' + ABBR + r')\.)\n', r'\1 ', t)
    t = re.sub(r'\s+(?=(?:The|THE|A|An)\s+' + ORD + r'\b)', '\n', t)
    return [p.strip() for p in t.split('\n') if p.strip()]


def cut(cl, targets, df=None):
    """Cut the clause list into len(targets) consecutive pieces (pieces may be empty) maximising the
    content words each piece shares with its target, weighted by how few of the block's targets
    contain the word."""
    n, k = len(cl), len(targets)
    W = [words(c) for c in cl]
    V = [set(words(t)) for t in targets]
    df = df or Counter(w for v in V for w in v)
    # prefix[t][j]: weighted hits of clauses 0..j-1 against target t
    prefix = []
    for t in range(k):
        acc, row = 0.0, [0.0]
        for ws in W:
            acc += sum(1.0 / df[w] for w in ws if w in V[t])
            row.append(acc)
        prefix.append(row)
    NEG = -1e18
    best = [[NEG] * (n + 1) for _ in range(k + 1)]
    back = [[0] * (n + 1) for _ in range(k + 1)]
    best[0][0] = 0.0
    for t in range(1, k + 1):
        P = prefix[t - 1]
        for j in range(n + 1):
            for i in range(j + 1):
                if best[t - 1][i] == NEG:
                    continue
                v = best[t - 1][i] + P[j] - P[i]
                if v > best[t][j]:
                    best[t][j], back[t][j] = v, i
    cuts, j = [], n
    for t in range(k, 0, -1):
        i = back[t][j]
        cuts.append((i, j)); j = i
    cuts.reverse()
    return [' '.join(cl[i:j]) for i, j in cuts], best[k][n]

def clean(order, misses):
    """Drop paragraph openings that rickaby_extract.py matched in the wrong place. Rickaby moves the
    Mysteries [261]-[312] into the days of the Second Week, so those may stand alone; the first
    paragraph of a block may be one running on from the block before. Otherwise a short run of
    paragraphs far in number from the rest of its block, or a paragraph out of order with the rest,
    is a false match; it is slotted in again beside its neighbour."""
    fixed = lambda n: n >= 261 and n <= 312
    keep = list(order)
    # short runs (at most three) that stand eight or more numbers away from the rest
    rest = [n for n in keep[1:] if not fixed(n)]
    runs, cur = [], []
    for n in sorted(rest):
        if cur and n - cur[-1] > 3:
            runs.append(cur); cur = []
        cur.append(n)
    if cur:
        runs.append(cur)
    if len(runs) > 1:
        for r in runs:
            others = [n for n in rest if n not in r]
            if len(r) <= 3 and min(min(abs(a - b) for b in others) for a in r) >= 8:
                keep = [n for n in keep if n not in r]
    # longest increasing run in Rickaby's order among the others
    body = [n for n in keep[1:] if not fixed(n)]
    if body:
        best = [1] * len(body); prev = [-1] * len(body)
        for i in range(len(body)):
            for j in range(i):
                if body[j] < body[i] and best[j] + 1 > best[i]:
                    best[i], prev[i] = best[j] + 1, j
        i = max(range(len(body)), key=lambda k: best[k]); lis = set()
        while i >= 0:
            lis.add(body[i]); i = prev[i]
        keep = [n for k, n in enumerate(keep) if k == 0 or fixed(n) or n in lis]
    return keep

def main(raw, exp, out):
    R = json.load(open(raw, encoding='utf-8'))
    E = json.load(open(exp, encoding='utf-8'))
    mullan = {u['n']: u['en'] for s in E['sections'] for u in s['units']}
    starts = {int(k): v for k, v in R['starts'].items()}
    misses = set(R['misses'])
    pieces = {}
    blocks = [b for b in R['blocks'] if b['kind'] == 'text' and b['en'].strip()]
    # openings matched at the very same place in Rickaby's Spanish (a run of 'Of the mysteries…'
    # headings, say) cannot all be right: none of them is trusted, they are slotted in below
    pos_n = Counter(starts.values())
    shared = {n for n, p in starts.items() if pos_n[p] > 1}
    orders = [clean(sorted([n for n in b['units'] if n not in shared], key=lambda n: starts.get(n, -1)), misses) for b in blocks]
    CL = [clauses(b['en'].strip()) for b in blocks]
    BW = [set(words(b['en'])) for b in blocks]
    placed = set(n for o in orders for n in o)
    for m in sorted(set(range(1, 371)) - placed):
        # an unplaced paragraph goes into the block of a neighbour, at the place where the cut
        # fits Mullan best
        # fits Mullan best: candidates are the blocks of its neighbours and the two blocks that
        # share most of its rarer words (Rickaby moves Mysteries far from their numbers)
        mw = set(words(mullan[m]))
        rare = {w for w in mw if sum(w in bw for bw in BW) <= 4}
        top = sorted(range(len(blocks)), key=lambda k: -len(rare & BW[k]))[:2]
        cands = sorted({k for k, o in enumerate(orders) if m + 1 in o or m - 1 in o} | set(top))
        best_gain, choice = None, None
        for k in cands:
            o = orders[k]
            dfk = Counter(w for x in o + [m] for w in set(words(mullan[x])))
            base = cut(CL[k], [mullan[x] for x in o], dfk)[1] if o else 0.0
            for i in range(len(o) + 1):
                g = cut(CL[k], [mullan[x] for x in o[:i] + [m] + o[i:]], dfk)[1] - base
                if best_gain is None or g > best_gain:
                    best_gain, choice = g, (k, i)
        if choice:
            orders[choice[0]].insert(choice[1], m); placed.add(m)
            print("slotted", m, "into pp.", blocks[choice[0]]["pages"][0] - 16, "at", choice[1], "gain", round(best_gain, 1))
    for b, order, cl in zip(blocks, orders, CL):
        en = b['en'].strip()
        if len(order) == 1:
            segs = [en]
        else:
            segs = cut(cl, [mullan[n] for n in order])[0]
        for n, s in zip(order, segs):
            if s.strip():
                pieces.setdefault(n, []).append({'en': s.strip(), 'pages': [b['pages'][0] - 16, b['pages'][-1] - 16]})
    units = []
    for n in range(1, 371):
        if n in pieces:
            ps = pieces[n]
            pg = [min(p['pages'][0] for p in ps), max(p['pages'][1] for p in ps)]
            units.append({'n': n, 'en': ' … '.join(p['en'] for p in ps), 'pages': pg})
    doc = {
        'titel': 'Rickaby 1923: translation',
        'quelle': 'Joseph Rickaby, S.J., The Spiritual Exercises of St. Ignatius Loyola: Spanish and English, with a '
                  'Continuous Commentary. Second edition. London: Burns Oates & Washbourne, 1923 (first edition 1915). '
                  'Google Books F7kHAQAAIAAJ (Stanford copy), text layer as delivered by Google. US public domain; '
                  'Rickaby died in 1932.',
        'hinweis': "Machine-read text, not corrected by hand. Rickaby's English column carries no paragraph numbers: "
                   'it was cut onto the grid by matching his Spanish column to the autograph and dividing the English '
                   'between those openings by its word overlap with Mullan 1914 (tools/rickaby_text.py). Cuts can be off '
                   'by a clause, and where Rickaby divides a paragraph of the book (the days of the Third Week in [208], for '
                   'example), a part may stand with a neighbouring paragraph. Page ranges are those of the run of text the paragraph stands in, 1923 edition; where '
                   'Rickaby moves a paragraph, it appears in his order, not the book\'s.',
        'units': units,
    }
    json.dump(doc, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(units), 'paragraphs ->', out)

if __name__ == '__main__':
    main(*sys.argv[1:4])
