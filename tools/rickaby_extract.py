# -*- coding: utf-8 -*-
"""Rickaby, The Spiritual Exercises of St. Ignatius Loyola: Spanish and English,
with a Continuous Commentary (2nd ed., London: Burns Oates & Washbourne, 1923),
from the Google Books PDF of the Stanford copy (id F7kHAQAAIAAJ), text layer as
delivered by Google.

The book prints the Spanish autograph and Rickaby's English in two columns
(the sides alternate between versos and rectos) and his commentary across the
full width between them. This script

1. classifies every line as left column, right column or full width (a short
   line that has no partner in the other column at its height belongs to the
   full-width commentary), drops running heads and page numbers;
2. turns each page into an ordered run of text regions (Spanish + English)
   and commentary regions, and tells the Spanish column from the English one
   by their function words;
3. finds where each canonical paragraph [1]-[370] begins in Rickaby's Spanish,
   by matching the opening of the autograph as edited in Ignatiana
   (data/exercitia.json) against his column, in order;
4. gives every commentary run the range of paragraphs whose text precedes it.

Usage: python -P tools/rickaby_extract.py <rickaby.pdf> <data/exercitia.json> <out.json>
"""
import json, re, sys, unicodedata
from difflib import SequenceMatcher
import pymupdf

ES = set('que de la el en y los las del se por con para su sus como más es lo al ó á nuestro señor ánima '
         'quando ansí exercicios hazer tiene ser una uno otra otro'.split())
EN = set('the of and to in that is be his he it as with for which by this our from or not who are will'.split())

def lines_of(page):
    out = []
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            t = ''.join(s['text'] for s in l['spans']).strip()
            if t:
                x0, y0, x1, y1 = l['bbox']
                out.append({'x0': x0, 'x1': x1, 'y': (y0 + y1) / 2, 'y0': y0, 't': t})
    return out

def classify(page):
    W = page.rect.width
    mid = W / 2
    L = lines_of(page)
    if not L:
        return []
    top = min(l['y0'] for l in L)
    L = [l for l in L if l['y0'] > top + 12 or not re.search(r'\d|[A-Z]{4,}', l['t'])]   # running head
    # the gutter: the x in the middle band that the fewest lines cross (the scans are not centred)
    xs = range(int(W * 0.38), int(W * 0.66))
    g = min(xs, key=lambda x: (sum(1 for l in L if l['x0'] < x - 2 and l['x1'] > x + 2), abs(x - mid)))
    for l in L:
        if l['x1'] <= g + 3:
            l['k'] = 'L'
        elif l['x0'] >= g - 3:
            l['k'] = 'R'
        else:
            l['k'] = 'F'
    for l in L:
        if l['k'] in 'LR':
            other = 'R' if l['k'] == 'L' else 'L'
            partner = any(m['k'] == other and abs(m['y'] - l['y']) < 7 for m in L)
            near_f = any(m['k'] == 'F' and abs(m['y'] - l['y']) < 16 for m in L)
            if not partner and near_f:
                l['k'] = 'F'
    # rows: words the text layer splits into separate lines at the same height
    L.sort(key=lambda l: l['y'])
    row, rows = [], []
    for l in L:
        if row and abs(l['y'] - row[-1]['y']) > 3.5:
            rows.append(row); row = []
        row.append(l)
    if row:
        rows.append(row)
    out = []
    for r_i, r in enumerate(rows):
        for l in sorted(r, key=lambda l: l['x0']):
            l['row'] = r_i
            out.append(l)
    return out

def lang(text):
    w = re.findall(r'[a-záéíóúñ]+', text.lower())
    es = sum(x in ES for x in w); en = sum(x in EN for x in w)
    return 'es' if es > en else 'en'

def join(lines):
    s = ''
    for t in lines:
        if s.endswith('-') and t[:1].islower():
            s = s[:-1] + t
        else:
            s = (s + ' ' + t) if s else t
    s = re.sub(r'\s+([,.;:!?])', r'\1', s)
    return re.sub(r'\s{2,}', ' ', s).strip()

def paragraphs(buf):
    """Commentary text with paragraph breaks ('\\n\\n') where a row starts indented after a
    sentence end, or with NOTES."""
    rows = {}
    for l in buf:
        rows.setdefault(l['row'], []).append(l)
    rows = [sorted(r, key=lambda l: l['x0']) for _, r in sorted(rows.items())]
    left = min(r[0]['x0'] for r in rows)
    parts, cur = [], []
    for r in rows:
        t = ' '.join(l['t'] for l in r)
        indented = r[0]['x0'] - left > 7
        if cur and (re.match(r'NOTES\b', t) or (indented and re.search(r'[.!?:"”\')]\s*$', cur[-1]))):
            parts.append(join(cur)); cur = []
        cur.append(t)
    if cur:
        parts.append(join(cur))
    return '\n\n'.join(p for p in parts if p)

def regions(doc, first, last):
    """Ordered list of ('T', {'es','en'}, page) and ('C', text, page)."""
    out = []
    for i in range(first, last + 1):
        L = classify(doc[i])
        cur, buf = None, []
        def flush():
            if not buf:
                return
            if cur == 'F':
                out.append(['C', paragraphs(buf), i])
            else:
                cols = {}
                for side in 'LR':
                    txt = join([l['t'] for l in sorted([l for l in buf if l['k'] == side], key=lambda l: (l['row'], l['x0']))])
                    if txt:
                        cols[lang(txt)] = (cols.get(lang(txt), '') + ' ' + txt).strip()
                # a real text region has a Spanish and an English column of some length; anything
                # else (side-notes beside the commentary, a stray short line) belongs to the commentary
                if len(cols.get('es', '')) > 60 and len(cols.get('en', '')) > 60:
                    out.append(['T', cols, i])
                else:
                    out.append(['C', join([l['t'] for l in sorted(buf, key=lambda l: (l['row'], l['x0']))]), i])
        for l in L:
            k = 'F' if l['k'] == 'F' else 'T'
            if k != cur:
                flush(); cur, buf = k, []
            buf.append(l)
        flush()
    # merge neighbours of the same kind (across page breaks)
    merged = []
    for r in out:
        if merged and merged[-1][0] == r[0]:
            if r[0] == 'C':
                merged[-1][1] += ('\n\n' if re.match(r'NOTES\b', r[1]) else ' ') + r[1]
            else:
                for k, v in r[1].items():
                    merged[-1][1][k] = (merged[-1][1].get(k, '') + ' ' + v).strip()
            merged[-1].append(r[2])
        else:
            merged.append(r[:])
    return merged

def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.replace('v', 'u').replace('y', 'i').replace('z', 'c').replace('ç', 'c').replace('h', '')
    return re.sub(r'[^a-z0-9]', '', s)

def main(pdf, exp, out, first=17, last=258):
    doc = pymupdf.open(pdf)
    R = regions(doc, first, last)
    E = json.load(open(exp, encoding='utf-8'))
    units = [u for s in E['sections'] for u in s['units']]
    # Spanish words with the region each belongs to; match by word pairs
    words, owner = [], []
    for ri, r in enumerate(R):
        if r[0] == 'T' and r[1].get('es'):
            for w in r[1]['es'].split():
                nw = norm(w)
                if nw:
                    words.append(nw); owner.append(ri)
    pairs = {}
    for i in range(len(words) - 1):
        pairs.setdefault(words[i] + ' ' + words[i + 1], []).append(i)
    def region_at(pos):
        return owner[min(pos, len(owner) - 1)]
    starts, pos, misses = {}, 0, []
    for u in units:
        key = [norm(w) for w in u['es'].split()][:14]
        key = [w for w in key if w]
        kp = [key[i] + ' ' + key[i + 1] for i in range(len(key) - 1)]
        votes = {}
        for k, p in enumerate(kp):
            for i in pairs.get(p, []):
                votes[i - k] = votes.get(i - k, 0) + 1   # candidate start = position minus offset in key
        cands = sorted(((v, s) for s, v in votes.items() if v >= max(2, len(kp) // 3)), reverse=True)
        after = [c for c in cands if pos <= c[1] <= pos + 3000]
        pick = max(after, key=lambda c: (c[0], -c[1])) if after else (cands[0] if cands else None)
        if pick:
            starts[u['n']] = pick[1]
            if pick[1] >= pos:
                pos = pick[1] + 1
        else:
            misses.append(u['n'])
    # every text region gets the paragraphs that begin in it, plus the one running into it
    # A stray hit far from its neighbours in Rickaby's order is a false match: drop it.
    seq = sorted((p, n) for n, p in starts.items())
    for k, (p, n) in enumerate(seq):
        nb = [m for _, m in seq[max(0, k - 3):k] + seq[k + 1:k + 4]]
        if nb and min(abs(n - m) for m in nb) > 12:
            starts.pop(n); misses.append(n)
    # Rickaby reorders the book (Presupposition first, the Examens after the Additions, the rules for
    # the First Week after the First Week), so ranges are taken from positions in his own order:
    # a text region holds the paragraphs that begin in it and the one whose text runs into it.
    by_pos = sorted((p, n) for n, p in starts.items())
    first_word = {}
    for i, ri in enumerate(owner):
        first_word.setdefault(ri, i)
    blocks, cur_range = [], [1, 1]
    for ri, r in enumerate(R):
        if r[0] == 'T' and ri in first_word:
            lo = first_word[ri]
            hi = max(i for i, o in enumerate(owner) if o == ri)
            inside = [n for p, n in by_pos if lo <= p <= hi]
            before = [n for p, n in by_pos if p < lo]
            first_in = min([p for p, _ in by_pos if lo <= p <= hi], default=hi + 1)
            # a region continues the previous paragraph only if its text runs on for a while
            # before the first opening (a heading such as SEGUNDA SEMANA does not count)
            running = before[-1] if before and first_in - lo > 15 else None
            ns = sorted(set(inside + ([running] if running else [])))
            runs = []
            for n in ns:
                if runs and n - runs[-1][1] <= 2:
                    runs[-1][1] = n
                else:
                    runs.append([n, n])
            blocks.append({'kind': 'text', 'runs': runs, 'pages': sorted(set(r[2:])),
                           'units': ns, 'en': r[1].get('en', ''), 'es': r[1].get('es', '')})
        elif r[0] == 'C':
            prev = next((b for b in reversed(blocks) if b['kind'] == 'text'), None)
            blocks.append({'kind': 'comm', 'runs': prev['runs'] if prev else [], 'pages': sorted(set(r[2:])), 'text': r[1]})
    json.dump({'starts': starts, 'misses': misses, 'blocks': blocks}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(R), 'regions;', len(starts), 'paragraph openings found;', len(misses), 'not found:', misses[:60])



def publish(raw, out):
    """Turn the raw regions into data/rickaby_exx.json: Rickaby's notes, one entry per
    commentary run, with the paragraph ranges of the text they follow."""
    R = json.load(open(raw, encoding='utf-8'))
    ESW = re.compile(r'\b(que|del|nuestro|Señor|ánima|para|los|las|como|quando|ansí|despues)\b')
    entries = []
    for b in R['blocks']:
        if b['kind'] != 'comm' or not b['runs']:
            continue
        paras = []
        for p in b['text'].split('\n\n'):
            p = re.sub(r'^NOTES\.\s*', '', p.strip())                        # the heading of each set of notes
            p = re.sub(r'^(66|99)\s+', '“', p)                               # an opening quote read as 66 or 99
            p = re.sub(r'([a-z])- ([a-z])', r'\1\2', p)                      # line-end hyphens kept by the text layer
            w = re.findall(r'[a-záéíóúñ]+', p.lower())
            es, en = sum(x in ES for x in w), sum(x in EN for x in w)
            if (es >= 3 and es >= 0.25 * en) or len(p) < 30:              # column text that slipped in, stray tails
                continue
            paras.append(p)
        if not paras or sum(len(p) for p in paras) < 120:
            continue
        pages = [p - 16 for p in b['pages']]                               # printed page = PDF page - 16
        entries.append({'runs': b['runs'], 'pages': [pages[0], pages[-1]], 'paras': paras})
    doc = {
        'titel': 'Rickaby 1923: notes',
        'quelle': 'Joseph Rickaby, S.J., The Spiritual Exercises of St. Ignatius Loyola: Spanish and English, with a '
                  'Continuous Commentary. Second edition. London: Burns Oates & Washbourne, 1923 (first edition 1915). '
                  'Google Books F7kHAQAAIAAJ (Stanford copy), text layer as delivered by Google.',
        'hinweis': 'Machine-read text, not corrected by hand. Rickaby prints the Spanish autograph and his translation in '
                   'two columns and his notes across the page; only the notes are given here. He rearranges the book '
                   '(the Presupposition first, the Examens after the Additions, each set of rules after its Week, the '
                   'Mysteries inside the days of the Second Week); each note is placed on the paragraphs whose text it '
                   'follows, found by matching his Spanish to the autograph. Page numbers are those of the 1923 edition.',
        'entries': entries,
    }
    json.dump(doc, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(entries), 'note runs ->', out)


if __name__ == '__main__':
    if sys.argv[1] == 'publish':
        publish(sys.argv[2], sys.argv[3])
    else:
        main(*sys.argv[1:4])
