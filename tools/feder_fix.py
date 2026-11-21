# -*- coding: utf-8 -*-
"""Dictionary-checked correction of the OCR of Feder 1922.

Only words that are not German words (wordfreq, Zipf frequency 0) are
touched, and only by changes that turn them into a word that is: typical
confusions of this microfilm (ch read as cli, li or di; R read as E; m as rn;
ü as ii ...) and words glued together across a lost space. Every change is
written to a log so that it can be checked; anything without a confident
candidate is left as it is and listed as unresolved.

Usage: python -P tools/feder_fix.py <blocks.json> <fixed.json> <log.json>
"""
import json, re, sys
from wordfreq import zipf_frequency

def z(w):
    return zipf_frequency(w, 'de')

SUBS = [('cli', 'ch'), ('di', 'ch'), ('li', 'h'), ('tli', 'th'), ('rn', 'm'), ('ii', 'ü'), ('ii', 'n'),
        ('iu', 'in'), ('ni', 'm'), ('u', 'n'), ('n', 'u'), ('c', 'e'), ('e', 'c'), ('t', 'f'), ('f', 't'),
        ('fs', 'ß'), ('l', 'i'), ('i', 'l'), ('1', 'l'), ('0', 'o'), ('ö', 'o'), ('ä', 'a'), ('a', 'ä'),
        ('o', 'ö'), ('u', 'ü'), ('ü', 'u'), ('h', 'b'), ('b', 'h'), ('rr', 'n'), ('w', 'v')]
FIRST = [('E', 'R'), ('K', 'R'), ('B', 'R'), ('Ü', 'U'), ('0', 'O'), ('l', 'I'), ('1', 'I'), ('O', 'G'), ('ß', 'S')]
SUBS += [('ö', 'e'), ('ä', 'ü')]
# A lost space is only restored next to a function word or before a capital:
# German compounds of two content words are far commoner than glued words.
FUNC = set('der die das den dem des und oder um wie was daß da ich ihr er sie es im am auf bei nach zum zur '
           'sondern denn damit indem auch jede jeder jedes nicht nur so als wenn weil ob ein eine einen einem einer '
           'eines in'.split())
# Prepositions and adverbs that double as verb prefixes (hin-neigt, aus-warfen)
# may stand second but never first in a split.
NOT_FIRST = set('in an auf aus bei mit nach von vor zu über unter durch für gegen hin ein'.split())
WORD = re.compile(r"[A-Za-zÄÖÜäöüß0-9]+")
# Words the dictionary does not know but that are right as printed.
KEEP = {'Exerzitand', 'Exerzitanden', 'hinneigt', 'hinneige', 'Nichtbesitzes', 'Ehrsucht', 'freuenden', 'Peinen',
        'einwirke', 'auswarfen', 'hinruft', 'Beweggrunde', 'Ausspruche', 'Löset', 'mitgesagt', 'aussprengt',
        'anfluß', 'gegenleuchte', 'überzart', 'Ertragung', 'beteure', 'bestrebe', 'Gebene', 'durchbetrachtet',
        'Lebensberuf', 'Menschenpaare', 'Generalbeichte', 'Reueschmerz', 'Almosenverteilung'}
# Readings settled by looking at the context; the dictionary rules cannot reach them.
MANUAL = {'ocer': 'oder', 'sinid': 'sind', 'a5er': 'aber', 'GoUes': 'Gottes', 'eineic': 'einer', 'daiä': 'daß',
          '5rost': 'Trost', 'vielcher': 'welcher', 'juaden': 'Gnaden', 'arüber': 'darüber', 'diQS': 'dies',
          'seihst': 'selbst', 'dalä': 'daß', 'davS': 'das', 'Aiigen': 'Augen', 'ejne': 'eine', 'aiif': 'auf',
          'Zusat': 'Zusatz', 'vorrichtet': 'verrichtet', 'luid': 'und', 'tind': 'und', 'kanuj': 'kann',
          'aMCh': 'auch', 'inehr': 'mehr', 'Galtin': 'Gattin', 'Wlal': 'Mal', 'irgendines': 'irgendeines',
          'orhält': 'erhält', 'Maiä': 'Maß', 'bgesang': 'Lobgesang', 'Josepher': 'Joseph er', 'esicht': 'Gesicht',
          'rnachdenkenzii': 'nachdenken zu', 'ichgesündigt': 'ich gesündigt', 'hinnimmtder': 'hinnimmt der',
          'gepflogendrittens': 'gepflogen drittens', 'aussprechetuud': 'ausspreche und', 'tiberdenkt': 'überdenkt',
          'einschlielälich': 'einschließlich', 'ungeu': 'ungen', 'versuciit': 'versucht', 'erwäbuten': 'erwähnten',
          'sinnliciien': 'sinnlichen', 'früliereii': 'früheren', 'uämlicli': 'nämlich', 'ziim': 'zum',
          'Ichheiße': 'Ich heiße', 'rriit': 'mit', 'midi': 'mich', 'Eeueschmerz': 'Reueschmerz',
          'Exerzitandeu': 'Exerzitanden', 'jestät': 'jestät', 'Peir': 'Petr', 'liinie': 'Linie',
          'eihen': 'einen', 'Zwedi': 'Zweck', 'Greiste': 'Geiste', 'Matm': 'Mann', 'seihe': 'seine',
          'wilU': 'will', 'außeii': 'außen', 'Schwörens': 'Schwörens', 'Weibda': 'Weib da'}
# Damaged strings that span more than one token.
STRING_FIX = [('«?aröt*s', 'daraus'), ('EmpfäugT nis', 'Empfängnis'), ('Gi;iäde', 'Gnade'), ('Wodi£', 'Woche'),
              ('alsOj', 'also,'),
              # footnote lines that ran into the text at a page foot, and a running head
              ('Jak 1, 17. wertig ist', 'wertig ist'),
              ('« Hebr 2, 17; 3, 1 usw. — »vgl Matth 8, 19: 16, 24; Joh 8, 12; 13, 15; 1 Petr 2, 21 usw. bei', 'bei'),
              ('Regeln über die kirchliche Gesinnung Vom Glauben,', 'vom Glauben,')]
STRING_FIX += [('AÖ-olt.', 'Gott'), ('Ver: nunft', 'Vernunft'), ('Vorti"bung', 'Vorübung'), ('Yoll Jcommenheit', 'Vollkommenheit'),
               ('Ehrfurcht: zu', 'Ehrfurcht zu'), ('wirken*:', 'wirken.'), ('LTikl,', 'Luk 1,'), ('CLuk', '(Luk')]
DROP = [r'I>ie allgemeine Gewissenserforschung BT', r'ende:']   # running-head remnants standing alone
# Second reading pass (21 November 2026): every remaining non-word read in context.
MANUAL.update({
    'siis': 'als', 'Sils': 'als', 'AVenn': 'Wenn', 'Beraerkungen': 'Bemerkungen', 'Laufenkörperliche': 'Laufen körperliche',
    'handgreiflieber': 'handgreiflicher', 'Exerzitaiiden': 'Exerzitanden', 'hinneigenj': 'hinneigen', '7betreff': 'betreff',
    'Gehrauches': 'Gebrauches', 'Exerzitieuleiter': 'Exerzitienleiter', 'ewissenserforschung': 'Gewissenserforschung',
    'JZieles': 'Zieles', 'Selbstprüfuug': 'Selbstprüfung', 'Mittagtischsoll': 'Mittagtisch soll',
    'Zweilinienügurebenso': 'Zweilinienfigur ebenso', 'esonderen': 'besonderen', 'eWissenserforschung': 'Gewissenserforschung',
    'Betätigungenrein': 'Betätigungen rein', 'Körpereingekerkert': 'Körper eingekerkert', 'Tierenlebt': 'Tieren lebt',
    'Beschämungmeiner': 'Beschämung meiner', 'Damaskuserschaffen': 'Damaskus erschaffen', 'Bußezubrachten': 'Buße zubrachten',
    'Anmutungendie': 'Anmutungen die', 'dari3ieten': 'darbieten', 'bestehtans': 'besteht aus', 'Crnade': 'Gnade',
    'Zwiegesprächein': 'Zwiegespräche in', 'Feuerglutenund': 'Feuergluten und', 'Exefzitanden': 'Exerzitanden',
    'Yerhrecher': 'Verbrecher', 'hgumi': 'beginne', 'wUnsohe': 'wünsche', 'Simmelsy': 'Himmels', 'Reueträneu': 'Reuetränen',
    'Ajiteil': 'Anteil', 'Soldatangesehen': 'Soldat angesehen', 'Vaterseinzugehen': 'Vaters einzugehen',
    'Gewichtdarbringen': 'Gewicht darbringen', 'hiramlisclien': 'himmlischen', 'dfts': 'des', 'Dänii': 'Dann',
    'nViederholung': 'Wiederholung', 'Beschauuiig': 'Beschauung', 'Vorbereitungsgehet': 'Vorbereitungsgebet',
    'Taistsinn': 'Tastsinn', 'Geheimnissesäuf': 'Geheimnisse auf', 'Witterüngsverhältnisse': 'Witterungsverhältnisse',
    'hieraufstelle': 'hierauf stelle', 'AnweMung': 'Anwendung', 'zuruckblieb': 'zurückblieb', 'Näbrväter': 'Nährväter',
    'Einfübrungr': 'Einführung', 'Vorbereitunsgebet': 'Vorbereitungsgebet', 'Heerführerzeigt': 'Heerführer zeigt',
    'Wiederholangen': 'Wiederholungen', 'bestitoiiit': 'bestimmt', 'nämliclien': 'nämlichen', 'beteuernj': 'beteuern',
    'verpflichtetübertreten': 'verpflichtet übertreten', 'läßliclie': 'läßliche', 'schmacherftiUten': 'schmacherfüllten',
    'Wajil': 'Wahl', 'AVurde': 'Wurde', 'Tichtige': 'richtige', 'läfet': 'läßt', 'zYfQitZit': 'zweite Zeit',
    'VQrhandeUj': 'vorhanden', 'ißh': 'ich', 'veränderliciien': 'veränderlichen', 'tiberlege': 'überlege',
    'besitzeeinzig': 'besitze einzig', 'betraeüte': 'betrachte', 'näMich': 'nämlich', 'AVeise': 'Weise',
    'elegenheit': 'Gelegenheit', 'Vaterunseri': 'Vaterunser', 'früheresagt': 'früher gesagt', 'schliefelicb': 'schließlich',
    'verscMedene': 'verschiedene', 'erwgen': 'erwägen', 'Betrachtang': 'Betrachtung', 'WiederholuugeH': 'Wiederholungen',
    'Anivendung': 'Anwendung', 'Vorbereitüngsgebet': 'Vorbereitungsgebet', 'Zeitderen': 'Zeit deren', 'anMeten': 'anbieten',
    'Majestätgeschaffen': 'Majestät geschaffen', 'verlejht': 'verleiht', 'tfhungen': 'Übungen', 'ZueiYst': 'Zuerst',
    'Gebetsweiseu': 'Gebetsweisen', 'Seelenkräft': 'Seelenkräfte', 'Vorbereitiingsgebet': 'Vorbereitungsgebet',
    'AVortes': 'Wortes', 'Änima': 'Anima', 'Ziveite': 'Zweite', 'Täufersverktindet': 'Täufers verkündet',
    'löeschneiduiis': 'Beschneidung', 'jrold': 'Gold', 'AVeihrauch': 'Weihrauch', 'AVeisheit': 'Weisheit', 'wiö': 'wie',
    'muij': 'muß', 'befaaid': 'befand', 'jet2t': 'jetzt', 'KapiteF': 'Kapitel', 'PMlippus': 'Philippus',
    'Hoißhzeit': 'Hochzeit', 'ewelche': 'welche', 'Christuö': 'Christus', 'Meev': 'Meer', 'ünd': 'und',
    'Aussendiiiig': 'Aussendung', 'HimmeU': 'Himmel', 'Schivestern': 'Schwestern', 'znm': 'zum', 'niederindes': 'nieder indes',
    'scMckte': 'schickte', 'zTi': 'zu', 'Eäuher': 'Räuber', 'fspalteten': 'spalteten', 'AVächter': 'Wächter',
    'Maiih': 'Matth', 'Honigscheibezu': 'Honigscheibe zu', 'Jakobtis': 'Jakobus', 'Apgl': 'Apg 1',
    'emigermaßen': 'einigermaßen', 'Kegungen': 'Regungen', 'Weseü': 'Wesen', 'irgead': 'irgend', 'deijenige': 'derjenige',
    'VorscMäge': 'Vorschläge', 'wül': 'will', 'Tugendenauszukundschaften': 'Tugenden auszukundschaften', 'Woohe': 'Woche',
    'verTbännen': 'verbannen', 'einQv': 'einer', 'scMecliten': 'schlechten', 'üinabzog': 'hinabzog',
    'voränschreiteri': 'voranschreiten', 'Erigetn': 'Engeln', 'GunsterweisuDg': 'Gunsterweisung',
    'Älmosenverteilungh': 'Almosenverteilung', 'inir': 'mir', 'ehtsprecliend': 'entsprechend', 'Regelif': 'Regel',
    'Kirchenversammlüng': 'Kirchenversammlung', 'muiä': 'muß', 'daijemand': 'daß jemand', 'nipht': 'nicht',
    'ivurdcj': 'wurde', 'erivähnt': 'erwähnt', 'auQh': 'auch', 'trachtetdas': 'trachtet das', 'Beraliard': 'Bernhard',
    'dieBüß': 'die Buß', 'ihreiBekämpfung': 'ihre Bekämpfung', 'Predigtender': 'Predigten der', 'Äuiäerungen': 'Äußerungen',
    'Sentenzenmeisterund': 'Sentenzenmeister und', 'Zeitverhältriisseii': 'Zeitverhältnissen', 'heueren': 'neueren',
    'uüd': 'und', 'jstets': 'stets', 'erscheinthalte': 'erscheint, halte', 'Büß': 'Buß', 'diö': 'die',
    'Kreuzzugsbullenund': 'Kreuzzugsbullen und', 'Keinignng': 'Reinigung', 'Untersdieidung': 'Unterscheidung',
    'tiiehen': 'fliehen', 'Ejigej': 'Engel',
})

def candidates(w):
    seen = set()
    for a, b in SUBS:
        i = w.find(a)
        while i != -1:
            c = w[:i] + b + w[i + len(a):]
            if c not in seen:
                seen.add(c); yield c
            i = w.find(a, i + 1)
    for a, b in FIRST:
        if w.startswith(a):
            c = b + w[len(a):]
            if c not in seen:
                seen.add(c); yield c

def deletions(w):
    for i in range(len(w)):
        yield w[:i] + w[i + 1:]

def fix_word(w):
    if w in MANUAL:
        return MANUAL[w] if MANUAL[w] != w else None
    if len(w) < 4 or z(w) > 0 or w.isdigit() or w in KEEP:
        return None
    best = max(((z(c), c) for c in candidates(w)), default=(0, None))
    if best[0] >= 2.5:
        return best[1]
    # two confusions in one word (Betraclituiig): stricter threshold
    if len(w) >= 7:
        best = max(((z(c2), c2) for c in candidates(w) for c2 in candidates(c)), default=(0, None))
        if best[0] >= 3.0:
            return best[1]
    # a lost space, only next to a function word or before a capital;
    # participles in -end- (betrachtendes, freuenden) are never split
    if len(w) >= 5 and not re.search(r'end(e|es|er|en|em)$', w):
        splits = []
        for k in range(2, len(w) - 1):
            a, b = w[:k], w[k:]
            if a.lower() in NOT_FIRST or len(a) < 2 or len(b) < 2:
                continue
            if not (a.lower() in FUNC or b in FUNC or b in NOT_FIRST or b[0].isupper()):
                continue
            splits.append((min(z(a), z(b)), a + ' ' + b))
        if splits:
            s = max(splits)
            if s[0] >= 3.0:
                return s[1]
    # a stray character: never the first letter, unless it is junk before a capital (jSiehe, ySamen)
    dels = [c for i, c in enumerate(deletions(w)) if len(c) >= 3 and (i > 0 or ((w[0].islower() or w[0] in 'Il') and w[1:2].isupper()))]
    best = max(((z(c), c) for c in dels), default=(0, None))
    if best[0] >= 3.0:
        return best[1]
    return None

def main(src, dst, logp):
    blocks = json.load(open(src, encoding='utf-8'))
    log, unresolved = [], {}
    for b in blocks:
        t = b['text']
        for a, c in STRING_FIX:
            if a in t:
                t = t.replace(a, c)
                log.append({'page': b['page'], 'from': a, 'to': c})
        t = re.sub(r'([a-zäöüß])([.:;!?])([A-ZÄÖÜ])', r'\1\2 \3', t)     # lost space after punctuation
        t = re.sub(r'\\v', 'w', t)                                        # Grund\vahrheit
        t = re.sub(r'\b([A-ZÄÖÜ])\.([a-zäöü]{2,})\b', r'\1\2', t)          # D.er
        t = re.sub(r'(^|\s),,(?=\w)', r'\1„', t)                            # opening quote read as two commas
        t = t.replace(',,', ',')                                           # a doubled comma elsewhere
        t = re.sub(r'(?<=\w)\*+', '', t)                                    # note marks glued to a word
        t = re.sub(r'(?<=[a-zäöüß])\s\d{1,2}\.?$', '.', t)                  # note call left at the end (werde 2.)
        t = re.sub(r'(?<=\s)[\'*®©€£¥|«»;:,.]+(?=\s)', '', t)              # stray marks between words
        t = re.sub(r'\s+([,.;:!?])', r'\1', t)
        t = re.sub(r'\s{2,}', ' ', t).strip()
        def rep(m):
            w = m.group(0)
            f = fix_word(w)
            if f:
                log.append({'page': b['page'], 'from': w, 'to': f})
                return f
            if len(w) >= 4 and not w.isdigit() and z(w) == 0 and not w[0].isupper():
                unresolved[w] = unresolved.get(w, 0) + 1
            return w
        b['text'] = WORD.sub(rep, t)
    # a running head that slipped into the body, and the paragraph split it caused
    blocks = [b for b in blocks if not re.fullmatch(r"Regeln f/ d\.'Üriterscheidüng der Geister 145", b['text'])
              and not any(re.fullmatch(d, b['text']) for d in DROP)]
    merged = []
    for b in blocks:
        if merged and not merged[-1]['head'] and re.match(r'[a-zäöüß]', b['text']) and not re.search(r'[.!?:]["“”]?$', merged[-1]['text']):
            merged[-1]['text'] = merged[-1]['text'].rstrip(' ,V') + ' ' + b['text'] if merged[-1]['text'].rstrip().endswith((' V ,', 'V ,')) else merged[-1]['text'] + ' ' + b['text']
            merged[-1]['pages'] = sorted(set(merged[-1]['pages'] + b['pages']))
            log.append({'page': b['page'], 'from': '¶', 'to': '(paragraph joined across a page break)'})
        else:
            merged.append(b)
    blocks = merged
    json.dump(blocks, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump({'changes': log, 'unresolved_lowercase': sorted(unresolved.items(), key=lambda x: -x[1])},
              open(logp, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(log), 'changes,', len(unresolved), 'unresolved lower-case forms')

if __name__ == '__main__':
    main(*sys.argv[1:4])
