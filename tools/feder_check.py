# -*- coding: utf-8 -*-
"""Check data/feder.json against the Spanish autograph, paragraph by paragraph.

For every canonical paragraph the length of Feder's German is set against the
length of the Spanish, scaled by the ratio over the whole book. A paragraph
far outside the band is a candidate for a wrong cut; the report shows its
opening and closing words next to the English, so it can be checked by eye.
Run after every change to tools/feder_anchors.json.

Usage: python -P tools/feder_check.py [lo] [hi]     (band, default 0.55 2.0)
"""
import json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lo, hi = (float(sys.argv[1]), float(sys.argv[2])) if len(sys.argv) > 2 else (0.55, 2.0)
F = json.load(open(os.path.join(REPO, 'data', 'feder.json'), encoding='utf-8'))
E = json.load(open(os.path.join(REPO, 'data', 'exercitia.json'), encoding='utf-8'))
es = {u['n']: u for s in E['sections'] for u in s['units']}
R = sum(len(u['de']) for u in F['units']) / sum(len(es[u['n']]['es']) for u in F['units'] if u['de'])
bad = 0
for u in F['units']:
    n = u['n']
    if not u['de']:
        print(f'[{n}] EMPTY  {u.get("missing", "")}')
        bad += 1
        continue
    r = len(u['de']) / (R * max(30, len(es[n]['es'])))
    if not lo <= r <= hi:
        bad += 1
        print(f'[{n}] ratio {r:.2f}  pp. {u["pages"]}\n   de: {u["de"][:90]} … {u["de"][-60:]}\n   en: {es[n]["en"][:90]} … {es[n]["en"][-60:]}')
print(f'R = {R:.2f}; {bad} of 370 flagged (band {lo}-{hi})')
