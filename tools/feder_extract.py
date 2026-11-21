# -*- coding: utf-8 -*-
"""Rebuild the running text of Feder's translation (Regensburg 1922) from the
Internet Archive's ABBYY FineReader output for the University of Chicago
microfilm MN5044ucmf_5 (one book page per frame).

What it does, per frame: orders the lines, takes the page number from the
running head and drops the head, drops footnotes (smaller type in the lower
part of the page) and signature marks, rebuilds paragraphs from ABBYY's
paragraph breaks and first-line indents, carries a paragraph across the page
break when the new page does not open with an indent, removes note-call
marks, and joins hyphenated line breaks.

What it does not do: correct OCR errors (tools/feder_fix.py does a
dictionary-checked pass), or restore Feder's italics, which mark words the
translator supplied: ABBYY's italic flags on this microfilm are unreliable.

Usage: python tools/feder_extract.py <MN5044ucmf_5_abbyy.gz> <out.json>
The ABBYY file is a download from archive.org/details/MN5044ucmf_5; the
output is the public-domain text, written where you point it.
"""
import gzip, json, re, sys
import xml.etree.ElementTree as ET
from collections import Counter

NS = '{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}'
FIRST, LAST = 18, 163          # pages of the Exercises in the 1922 edition

def frames(path):
    for ev, el in ET.iterparse(gzip.open(path), events=('end',)):
        if el.tag != NS + 'page':
            continue
        lines = []
        for bi, block in enumerate(el.iter(NS + 'block')):
            for pi, par in enumerate(block.iter(NS + 'par')):
                for line in par.iter(NS + 'line'):
                    txt, fs = [], Counter()
                    for f in line.iter(NS + 'formatting'):
                        s = ''.join(c.text or '' for c in f.iter(NS + 'charParams'))
                        txt.append(s)
                        fs[float((f.get('fs') or '0').rstrip('.'))] += len(s)
                    t = re.sub(r'\s+', ' ', ''.join(txt)).strip()
                    if t:
                        lines.append({'par': (bi, pi), 'l': int(line.get('l')), 'r': int(line.get('r')),
                                      't': int(line.get('t')), 'b': int(line.get('b')),
                                      'fs': fs.most_common(1)[0][0], 'text': t})
        el.clear()
        yield sorted(lines, key=lambda x: x['t'])

HEAD_NUM = re.compile(r'^\W{0,3}(\d{1,3})\b|\b(\d{1,3})\W{0,3}$')
FOOT = re.compile(r'^\W{0,5}(?:[a-z*"\'^]|<!|\d)?\W{0,3}\s*vgl\b|^\W{0,3}\*|^[\'\-^]{1,3}\s*Wir setzen|In Kursivlettern|^\W{0,3}[a-z]\W{0,2}\s*(?:Gal|Matth|Luk|Joh|Mark|Ps|Gen|Apg|Rom|Kor)\b')

def clean_calls(s):
    s = re.sub(r"\s*['’]?\^\s*\d{0,2}o?", '', s)          # ^, '^, ^o, ^12: note calls
    s = re.sub(r'(?<=[a-zäöüß.,;:])\d{1,2}(?=[\s.,;:]|$)', '', s)   # digit glued to a word end
    s = s.replace('■', '').replace('•', '')
    return re.sub(r'\s{2,}', ' ', s).strip()

def main(src, out):
    pages, last_no = [], 0
    for lines in frames(src):
        if not lines:
            continue
        body_fs = Counter(round(x['fs']) for x in lines).most_common(1)[0][0]
        top, bottom = lines[0]['t'], max(x['b'] for x in lines)
        no = None
        head = lines[0]
        m = HEAD_NUM.search(head['text'])
        if len(head['text']) < 62 and m and (head['fs'] <= body_fs or re.search(r'[A-Za-zä]{4}', head['text'])):
            no = int(m.group(1) or m.group(2))
            lines = lines[1:]
        if no is None or not (last_no < no <= last_no + 3):
            no = last_no + 1 if last_no else no or 0
        last_no = no
        body, infoot = [], False
        for x in lines:
            low = x['t'] > top + 0.55 * (bottom - top)
            if low and FOOT.search(x['text']):
                infoot = True                               # Feder's footnotes: scripture references, editorial notes
            if infoot or (low and x['fs'] <= body_fs - 2):
                continue                                    # footnote
            if re.fullmatch(r'[\W\d*]{1,6}', x['text']) or (low and re.fullmatch(r'\W*\d{1,2}\s?\*\W*', x['text'])):
                continue                                    # signature mark, stray characters
            body.append(x)
        pages.append({'page': no, 'lines': body})

    pages = [p for p in pages if FIRST <= p['page'] <= LAST]
    blocks = []
    for p in pages:
        if not p['lines']:
            continue
        lmin = min(x['l'] for x in p['lines'])
        rmax = max(x['r'] for x in p['lines'])
        prev = None
        for i, x in enumerate(p['lines']):
            indent = x['l'] - lmin > 45
            centered = x['l'] - lmin > 140 and rmax - x['r'] > 140
            newpar = prev is None and (indent or centered) or (prev is not None and x['par'] != prev['par'] and (indent or centered))
            if prev is None and not newpar and blocks:
                blocks[-1]['lines'].append(x['text'])        # continuation across the page break
                blocks[-1]['pages'].append(p['page'])
            elif newpar or prev is None:
                blocks.append({'page': p['page'], 'pages': [p['page']], 'head': centered, 'lines': [x['text']]})
            else:
                blocks[-1]['lines'].append(x['text'])
            prev = x
    out_blocks = []
    for b in blocks:
        s = ''
        for ln in b['lines']:
            ln = ln.strip()
            if s.endswith('-') and ln[:1].islower():
                s = s[:-1] + ln
            elif s:
                s += ' ' + ln
            else:
                s = ln
        out_blocks.append({'page': b['page'], 'pages': sorted(set(b['pages'])), 'head': b['head'], 'text': clean_calls(s)})
    json.dump(out_blocks, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(out_blocks), 'blocks, pages', out_blocks[0]['page'], '-', out_blocks[-1]['page'])

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
