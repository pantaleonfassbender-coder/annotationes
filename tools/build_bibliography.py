# -*- coding: utf-8 -*-
"""Build data/bibliography.json: one bibliography over the whole apparatus.

Groups:
  text      the editions behind the text at the centre (Autograph and Vulgate after the Monumenta,
            Mullan's English, Feder's German, Rickaby's English);
  works     every work in data/works.json except the journals, by author;
  articles  every journal article that stands in the margin (glosses of the journals), by author;
  journals  the journals themselves;
  cited     a few studies named in the notes and paths, with their data as the citing texts give them.

Each entry carries an APA-7-style reference (italics marked with *…*), the link to its source, the
access tier, the place in the apparatus, and the fields for a BibTeX or RIS export, which the page
builds on demand. Bibliographic data, CC0.

Usage: python -P tools/build_bibliography.py
"""
import json, os, re, unicodedata

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(REPO, 'data', *p)
load = lambda p: json.load(open(p, encoding='utf-8'))

JOURNALS = {'ram', 'zam', 'gul', 'studies', 'theway', 'ryf'}
PARTICLES = {'von', 'van', 'de', 'del', 'della', 'v.', 'du', 'der'}

def clean_author(a):
    a = re.sub(r'\s*\((?:ed|eds|trans)\.\)|\s*\(\d{4}[–-]\d{4}\)', '', a or '')
    a = re.sub(r',\s*(?:SJ|S\.J\.|SSJE)\b', '', a).strip()
    return a

SPECIAL = {'Raitz': 'Raitz von Frentz'}   # compound surnames the simple rule would split

def apa_name(a):
    """'Hans Urs von Balthasar' -> 'Balthasar, H. U. von'; 'C. G. Jung' -> 'Jung, C. G.';
    several authors joined by 'and' -> 'A, & B'; corporate authors and popes stay as they are."""
    a = clean_author(a)
    if ' and ' in a:
        names = [apa_name(x) for x in a.split(' and ')]
        return ', '.join(names[:-1]) + ', & ' + names[-1]
    if not a or ' ' not in a or a.startswith(('Jesuits', 'Die ', 'Arbeitskreis', 'Communauté')) \
            or re.search(r'\b[IVX]+$', a):
        return a
    for k, sur in SPECIAL.items():
        if k in a.split():
            given = a.split()[:a.split().index(k)]
            return sur + ', ' + ' '.join(g if g.endswith('.') else g[0] + '.' for g in given)
    parts = a.split()
    i = len(parts) - 1
    while i > 1 and parts[i - 1].lower() in PARTICLES:
        i -= 1
    sur, given = parts[-1], parts[:i]
    part = ' '.join(parts[i:-1])
    if part.lower() in PARTICLES or all(p.lower() in PARTICLES for p in part.split()):
        pass
    elif part:
        sur = part + ' ' + sur; part = ''
    ini = ' '.join(g[0] + '.' if not g.endswith('.') else g for g in given)
    return f'{sur}, {ini}' + (f' {part}' if part else '')

def sortkey(s):
    s = unicodedata.normalize('NFD', s)
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()

def ref_work(w):
    a = w.get('author') or ''
    role = ' (Ed.)' if '(ed.)' in a else ' (Trans.)' if '(trans.)' in a else ''
    who = apa_name(a) + role if a else ''
    yr = f"{w['year']}–{w['yearEnd']}" if w.get('yearEnd') and w['yearEnd'] != w['year'] else str(w['year'])
    imp = (w.get('imprint') or '').rstrip('.')
    head = f'{dot(who)} ({yr}). ' if who else ''
    title = f"*{w['title']}*" if who else f"*{w['title']}* ({yr})"
    return f'{head}{title}' + end(w['title']) + (f' {imp}.' if imp else '')

dot = lambda w: w if w.endswith('.') else w + '.'
end = lambda t: '' if re.search(r'[.?!]$', t.strip()) else '.'

LOC = re.compile(r'^(?P<j>.+?) (?P<v>[IVXL]+/\d+|\d+) \((?P<y>[^)]*)\)(?:, (?:vol\. \d+, )?pp?\. (?P<p>[\d–\-]+))?')

def main():
    works = load(D('works.json'))['works']
    glosses = load(D('glosses.json'))['glosses']
    ex = load(D('exercitia.json'))
    out = []

    # the text at the centre
    out += [
        {'group': 'text', 'sort': 'exercitia 1919', 'apa': '*Exercitia spiritualia S. Ignatii de Loyola et eorum directoria* (1919). Monumenta Historica Societatis Iesu, Monumenta Ignatiana, ser. II. Madrid. The Autograph and the Vulgate of 1548 as edited there.',
         'note': ex['quellen']['es'] + ' ' + ex['quellen']['la'], 'url': '', 'tier': 'A', 'here': '#/spex/1',
         'bib': {'type': 'book', 'title': 'Exercitia spiritualia S. Ignatii de Loyola et eorum directoria', 'year': '1919', 'address': 'Madrid', 'series': 'Monumenta Historica Societatis Iesu, Monumenta Ignatiana, ser. II'}},
        {'group': 'text', 'sort': 'ignatius mullan 1914', 'apa': 'Ignatius of Loyola. (1914). *The Spiritual Exercises of St. Ignatius of Loyola* (E. Mullan, Trans.). P. J. Kenedy.',
         'note': ex['quellen']['en'], 'url': '', 'tier': 'A', 'here': '#/spex/1',
         'bib': {'type': 'book', 'author': ['Ignatius of Loyola'], 'title': 'The Spiritual Exercises of St. Ignatius of Loyola', 'year': '1914', 'publisher': 'P. J. Kenedy', 'address': 'New York', 'note': 'Translated by Elder Mullan'}},
    ]
    byid = {w['id']: w for w in works}
    for wid, label in (('feder-1922', 'German text in the reader'), ('rickaby-1915', 'second English text in the reader')):
        w = byid[wid]
        out.append({'group': 'text', 'sort': 'ignatius ' + wid, 'apa': ref_work(w), 'note': label,
                    'url': w['sources'][0]['url'] if w.get('sources') else '', 'tier': w['tier'], 'here': '#/works/' + wid,
                    'bib': {'type': 'book', 'author': [clean_author(w['author'])], 'title': w['title'], 'year': str(w['year']), 'note': w.get('imprint', '')}})

    # works
    for w in works:
        if w['genre'] == 'journal':
            out.append({'group': 'journals', 'sort': sortkey(w['title']), 'apa': ref_work(w), 'note': w.get('status', ''),
                        'url': w['sources'][0]['url'] if w.get('sources') else '', 'tier': w['tier'], 'here': '#/works/' + w['id'],
                        'bib': {'type': 'periodical', 'title': w['title'], 'year': str(w['year']), 'note': w.get('imprint', '')}})
            continue
        a = clean_author(w.get('author'))
        out.append({'group': 'works', 'sort': sortkey(apa_name(w.get('author')) + ' ' + str(w['year'])), 'apa': ref_work(w),
                    'note': w.get('status', ''), 'url': w['sources'][0]['url'] if w.get('sources') else '',
                    'tier': w['tier'], 'here': '#/works/' + w['id'],
                    'bib': {'type': 'book', 'author': [a] if a else [], 'title': w['title'], 'year': str(w['year']), 'note': w.get('imprint', '')}})

    # journal articles in the margin, once each
    seen = {}
    for g in glosses:
        if g['work'] not in JOURNALS or not g.get('title'):
            continue
        key = (g.get('author'), g['title'])
        if key in seen:
            continue
        m = LOC.match(g['loc'])
        j, v, pp = (m.group('j'), m.group('v'), m.group('p')) if m else (byid[g['work']]['title'], '', None)
        au = clean_author(g.get('author'))
        who = apa_name(au) if au else ''
        apa = f"{dot(who)} ({g.get('year')}). {g['title']}{end(g['title'])} *{j}*" + (f", *{v}*" if v else '') + (f", {pp}" if pp else '') + '.'
        here = f"#/spex/{g['spex'][0]}" if g.get('spex') else '#/book'
        seen[key] = True
        out.append({'group': 'articles', 'sort': sortkey(f"{who} {g.get('year')}"), 'apa': apa,
                    'note': 'read' if g.get('basis') == 'read' else 'listed by title', 'url': g.get('url', ''),
                    'tier': byid[g['work']]['tier'], 'here': here,
                    'bib': {'type': 'article', 'author': [au] if au else [], 'title': g['title'], 'journal': j, 'volume': v,
                            'pages': (pp or '').replace('–', '--'), 'year': str(g.get('year'))}})

    # studies named in the notes and paths, as the citing texts give them
    cited = [
        ('Leturia, P.', 1928, 'El "Reino de Cristo" y los prólogos del Flos Sanctorum de Loyola', 'Manresa', '4', '334–349',
         'cited by Kellerwessel 1932 and Zeiger 1942 for the Flos Sanctorum as a source of the Kingdom'),
        ('Tournier, F.', 1910, 'Les "deux cités" dans la littérature chrétienne', 'Études', '123', '644–665',
         'the thesis Codina answers in Razón y Fe 1915 (cited by Zeiger 1942)'),
        ('Kreiten, W.', 1882, 'Zur Entstehung des Exerzitienbüchleins', 'Stimmen aus Maria-Laach', '23', '32–55, 154–171',
         'cited by Zeiger 1942'),
    ]
    for au, yr, ti, jo, vo, pp, note in cited:
        out.append({'group': 'cited', 'sort': sortkey(f'{au} {yr}'), 'apa': f'{au} ({yr}). {ti}. *{jo}*, *{vo}*, {pp}.',
                    'note': note, 'url': '', 'tier': '', 'here': '',
                    'bib': {'type': 'article', 'author': [au], 'title': ti, 'journal': jo, 'volume': vo, 'pages': pp.replace('–', '--'), 'year': str(yr)}})

    order = {'text': 0, 'works': 1, 'articles': 2, 'journals': 3, 'cited': 4}
    out.sort(key=lambda e: (order[e['group']], e['sort']))
    doc = {'_note': 'Bibliography of the apparatus (tools/build_bibliography.py). APA 7 style; *…* marks italics. CC0.',
           'groups': {'text': 'The text at the centre', 'works': 'Works in the apparatus',
                      'articles': 'Journal articles in the margin', 'journals': 'Journals',
                      'cited': 'Studies named in the notes'},
           'entries': out}
    json.dump(doc, open(D('bibliography.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    from collections import Counter
    print(len(out), 'entries', dict(Counter(e['group'] for e in out)))
    for e in out[:6] + [x for x in out if x['group'] == 'articles'][:4]:
        print(' ', e['apa'][:150])

if __name__ == '__main__':
    main()
