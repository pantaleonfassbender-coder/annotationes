# -*- coding: utf-8 -*-
"""Build assets/plates/ and data/plates.json: one public-domain plate per
work where a suitable page exists, fetched page by page over the Internet
Archive's IIIF service (no full scans are downloaded or carried). A faithful
reproduction of a public-domain two-dimensional page adds nothing
licensable; every plate names its source, scan and leaf.

The 1548 title page is taken over from Ignatiana (same source, same leaf).

Usage: python tools/build_plates.py          (needs the network and Pillow)
"""
import io, json, os, urllib.request
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, 'assets', 'plates')
os.makedirs(OUT, exist_ok=True)

def ia(item, leaf, w=1400):
    return f"https://iiif.archive.org/iiif/{item}${leaf}/full/{w},/0/default.jpg"

PLATES = [
 {'id': 'longridge-1919', 'url': ia('spiritualexercis00igna_4', 7),
  'caption': "Title page of Longridge's translation and commentary, London 1919: an Anglican "
             "religious of the Cowley Fathers, with the society's seal.",
  'credit': "W. H. Longridge, The Spiritual Exercises of Saint Ignatius of Loyola (London: Robert Scott, 1919). "
            "Internet Archive spiritualexercis00igna_4, leaf 7. Public domain."},
 {'id': 'joyce-1916', 'url': ia('aportraitartist00joycgoog', 8, 800),  # Google scan: the service times out above its native width
  'caption': "Title page of the Huebsch edition of A Portrait of the Artist as a Young Man, in the fifth printing "
             "of 1922 from which the page references here are taken.",
  'credit': "James Joyce, A Portrait of the Artist as a Young Man (New York: B. W. Huebsch, 1916; 5th printing 1922). "
            "Internet Archive aportraitartist00joycgoog, leaf 8. Public domain."},
 {'id': 'pius11-1922', 'url': ia('sim_acta-apostolicae-sedis_1922-07-25_14_12', 5),
  'caption': "Summorum Pontificum as printed in the Acta Apostolicae Sedis: Ignatius declared heavenly patron "
             "of the Spiritual Exercises, 25 July 1922.",
  'credit': "Acta Apostolicae Sedis 14 (1922), p. 420. Internet Archive sim_acta-apostolicae-sedis_1922-07-25_14_12, "
            "leaf 5. Public domain."},
 {'id': 'pius11-1929', 'url': ia('sim_acta-apostolicae-sedis_1929-12-31_21_16', 10, 1100),
  'caption': "The first page of the encyclical Mens nostra on the Spiritual Exercises, 20 December 1929.",
  'credit': "Acta Apostolicae Sedis 21 (1929), p. 689. Internet Archive sim_acta-apostolicae-sedis_1929-12-31_21_16, "
            "leaf 10. Public domain."},
]
SPEX = {'id': 'spex',
        'caption': "The editio princeps: Exercitia spiritualia, Rome 1548, the Vulgate's title page with the IHS "
                   "device, the year Paul III approved the book.",
        'credit': "Exercitia spiritualia (Rome: Antonio Blado, 1548). Internet Archive bub_gb_eyZ68wmgWoIC, leaf 8. "
                  "Public domain. Taken over from Ignatiana."}

def fetch(url, tries=5):
    import time
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (plate builder)'})
            with urllib.request.urlopen(req, timeout=120) as r:
                return Image.open(io.BytesIO(r.read())).convert('RGB')
        except Exception as e:      # the IIIF service answers 504 while it renders a cold page
            if k == tries - 1:
                raise
            print('  retry', url.split('/iiif/')[1].split('/')[0], e)
            time.sleep(10 * (k + 1))

# Plates made by hand stay in the registry: rickaby-1915 is page 10 of the Google Books PDF
# (F7kHAQAAIAAJ), rendered at 220 dpi with PyMuPDF; Google Books serves that PDF only after a
# captcha, so it cannot be fetched here.
try:
    reg = json.load(open(os.path.join(REPO, 'data', 'plates.json'), encoding='utf-8'))
except FileNotFoundError:
    reg = {}
reg[SPEX['id']] = {'caption': SPEX['caption'], 'credit': SPEX['credit']}
for p in PLATES:
    im = fetch(p['url'])
    im.save(os.path.join(OUT, p['id'] + '.jpg'), quality=82, optimize=True, progressive=True)
    t = im.copy(); t.thumbnail((360, 360))
    t.save(os.path.join(OUT, p['id'] + '_t.jpg'), quality=80, optimize=True)
    reg[p['id']] = {'caption': p['caption'], 'credit': p['credit']}
    print('ok', p['id'], im.size)
with open(os.path.join(REPO, 'data', 'plates.json'), 'w', encoding='utf-8') as f:
    json.dump(reg, f, ensure_ascii=False, indent=1)
print(len(reg), 'plates -> data/plates.json')
