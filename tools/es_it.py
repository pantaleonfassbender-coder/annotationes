# -*- coding: utf-8 -*-
"""Spanish and Italian reception before 1931: writes data/src/es_it.json.

Hand-curated from the Internet Archive scans (Razón y Fe vols. 1-61, Codina 1926, Torti 1909):
articles found by text search, authors from signatures and indexes, scan pages from the hOCR page
index; links use the printed page label, which the viewer resolves (Razón y Fe: the scan position n,
with the item id doubled in the path because the item has two viewable files).

Usage: python -P tools/es_it.py data/src/es_it.json
"""
import json, sys
G = []

def rf(id_, vol, n, year, author, title, pages, spex, basis, note):
    G.append({'id': id_, 'work': 'ryf', 'spex': spex, 'basis': basis, 'author': author, 'title': title, 'year': year,
              'loc': f'Razón y Fe {vol} ({year}), {pages}',
              'url': f'https://archive.org/details/raznyfe{vol:02d}madruoft/raznyfe{vol:02d}madruoft/page/n{n}', 'note': note})

rf('ryf-1904-codina', 9, 431, 1904, 'Matías Codina', 'Una solución del problema social', 'pp. 426–442', None, 'read',
   "Closed retreats for workers as an answer to the social question, on the Belgian model of the retreat house at Fayt-lez-Manage in the mining district: the Exercises as Catholic social action.")
rf('ryf-1908-noguer', 21, 200, 1908, 'Narciso Noguer', 'Casas de Ejercicios para obreros en España', 'pp. 197–200', None, 'read',
   "A survey of the retreat houses for workers in Spain, ending on Loyola and Manresa as the places of the Exercises.")
rf('ryf-1909-martinez', 24, 282, 1909, 'Juan Antonio Martínez', 'La Biblioteca de los Ejercicios de San Ignacio de Loyola', 'pp. 277–288', None, 'read',
   "On Henri Watrigant's library of the Exercises at Enghien, the house of studies of the French Jesuits in Belgian exile: the Exercises as an object of historical scholarship.")
rf('ryf-1914-ataques', 39, 285, 1914, 'unsigned', 'Nuevos ataques a los «Ejercicios espirituales» de San Ignacio', 'pp. 280–297', None, 'read',
   "The Spanish echo of the Festugière controversy: Dom Maur Festugière's liturgical critique of Ignatian meditation, answered with the help of the Carmelite Fr María José del Sagrado Corazón and of Peeters; the method defended as freedom of spirit, not much knowing but feeling and tasting [2].")
rf('ryf-1914-bover', 39, 440, 1914, 'José M. Bover', 'El Reino de Dios y el Reino de Cristo, o el Evangelio y los Ejercicios de San Ignacio', 'pp. 433–442', [91, 100], 'read',
   "The Kingdom of God of the Gospels set beside the call of the King: the Kingdom of Christ as 'cipher and key' of the Exercises, which are a practice of the Gospel as the Gospel is the Kingdom of God.")
rf('ryf-1915-codina-a', 41, 479, 1915, 'Arturo Codina', '¿La meditación de «Dos Banderas» es de San Ignacio o de un anónimo?', 'pp. 474–487', [136, 148], 'read',
   "Taking up Van Ortroy's article in the Analecta Bollandiana (1913) and the thesis that Ignatius took the Two Standards from the pseudo-Bernardine parable De conflictu vitiorum et virtutum read at Loyola. The author is named from his own reference in the sequel.")
rf('ryf-1915-codina-b', 43, 207, 1915, 'Arturo Codina', '¿En Manresa o en París?', 'pp. 202–219 and 340–348', [136, 148], 'read',
   "Sequel: Tournier's thesis (Études, 1910) that the Two Standards depends on Werner of St Blasien's De duobus dominis and on Augustine, and the question whether the meditation was made at Manresa or in Paris; the second part reads its fruit with Meschler and Suárez as perfection in any state, not a call to apostolic life.")
rf('ryf-1916-astrain', 44, 40, 1916, 'Antonio Astrain', 'San Ignacio de Loyola y la Liturgia', 'pp. 35–46, 173–186, 291–305', None, 'read',
   "The historian of the Spanish Jesuits answers Dom Festugière's La Liturgie catholique (1913) in three articles: Ignatius' own practice of the liturgy, the charge of individualism, and the 'spirit and method' of the Exercises.")
rf('ryf-1917-codina', 48, 291, 1917, 'Arturo Codina', 'Los «Ejercicios» de San Ignacio y el «Ejercitatorio» de Cisneros', 'vol. 48, pp. 286–299 and 426–439; vol. 49, pp. 16–29', None, 'read',
   "Against Dom Besse and Dom Pierdet of Silos (Revista Eclesiástica, 1916–17), who derived the Exercises from García de Cisneros' Ejercitatorio (Montserrat, 1500): the claimed parallels are weighed one by one; that Ignatius read the Ejercitatorio is granted as probable, a dependence of the book is not proven.")
rf('ryf-1917-codina-47', 49, 21, 1917, 'Arturo Codina', 'Los «Ejercicios» de San Ignacio y el «Ejercitatorio» de Cisneros (conclusion)', 'pp. 16–29', [47, 47], 'read',
   "The composition of place and the examen after prayer are struck from the list of borrowings: they are not in the Ejercitatorio but in Cisneros' separate Directorio de las horas canónicas.")
rf('ryf-1918-manresa', 51, 282, 1918, 'F. de Manresa', 'Suárez, asceta: Suárez y el libro de los «Ejercicios»', 'pp. 277–290 and 454–459', None, 'read',
   "Suárez's defence of the Exercises in De religione Societatis Iesu, book IX, presented as the theology of a rough stone from the quarry of Manresa: an instrument of perfection, universal and safe.")
rf('ryf-1919-bover', 54, 350, 1919, 'José M. Bover', 'El «Principio y Fundamento» de los «Ejercicios» a la luz de las Epístolas de San Pablo', 'pp. 343–355', [23, 23], 'read',
   "The Foundation read through Paul: the source from which all the Exercises flow and on which they rest, and the paradox that, giving and bearing everything, it does not of itself finish anything.")

CU = 'https://archive.org/details/losorigenesdelos0000part/page/'
def cod(i, spex, pp, first, what):
    G.append({'id': f'codina-1926-{i}', 'work': 'codina-1926', 'spex': spex, 'basis': 'index', 'loc': pp,
              'url': CU + str(first), 'note': what})
cod(1, [1, 20], 'pp. 45, 101, 224', 45, "The annotations: later than Manresa; their origin and the corrections in the autograph; compared with Ludolph's Vita Christi.")
cod(2, [23, 23], 'pp. 45–46, 146, 158–159, 184', 45, "The Foundation dated to Manresa; its antecedents in Ludolph's Vita Christi and in the Imitation of Christ.")
cod(3, [24, 31], 'pp. 46–47, 65', 46, "The particular examen: whether it dates from Manresa; examens in Mauburnus; it did not always stand at the head of the book.")
cod(4, [32, 43], 'p. 47', 47, "How the general examen is made.")
cod(5, [65, 71], 'pp. 105–106, 159, 270–271', 105, "The meditation on hell founded on Scripture; the tenderness of its petition; its text compared with Cisneros'.")
cod(6, [73, 90], 'pp. 49, 115–116', 49, "The additions: their origin and meaning.")
cod(7, [91, 100], 'pp. 9, 14, 100, 193–195, 212–214', 193, "The Kingdom dated to Manresa; an autograph correction; the text of its second part; Anselm on the kingdom of Christ among its antecedents.")
cod(8, [136, 148], 'pp. 14, 196–199, 227–229', 196, "The Two Standards as part of the method of election; exposition; the example of Christ; the text compared with Ludolph.")
cod(9, [149, 157], 'pp. 3, 102–104', 102, "The Three Classes: their end, their link with Annotation 16, their origin.")
cod(10, [165, 168], 'pp. 3, 161, 203', 203, "The three kinds of humility: the third, and the foundation of all three.")
cod(11, [169, 189], 'pp. 3, 14, 50, 118–119', 50, "The election: its place in the book, its date (Manresa), its last preparation.")
cod(12, [210, 217], 'pp. 51–52, 222, 236–237', 51, "The rules for eating: their origin, with Brettle's view of it.")
cod(13, [230, 237], 'pp. 52–53', 52, "The Contemplation to Attain Love: origin.")
cod(14, [238, 260], 'p. 53', 53, "The three methods of prayer: origin.")
cod(15, [313, 336], 'pp. 50, 56, 161–163, 280', 50, "The rules for discernment: origin; the remedies for desolation.")
cod(16, [337, 344], 'pp. 56–57, 241', 56, "The rules for alms: origin and their link with Manresa.")
cod(17, [352, 370], 'pp. 58, 101, 204–207', 204, "The rules for thinking with the Church: origin, an autograph correction, the Church as mother.")
G.append({'id': 'codina-1926-cisneros', 'work': 'codina-1926', 'spex': None, 'basis': 'index', 'loc': 'Appendix III, pp. 261–281',
          'url': CU + '261',
          'note': "Cisneros' own summary of his Ejercitatorio and its chapter list, then Dom Besse's parallels examined (pp. 265–281): the question of the author's articles in Razón y Fe (1917) taken up again."})

TU = 'https://archive.org/details/esercizispiritua0000pcar/page/'
def tor(i, spex, n, what):
    G.append({'id': f'torti-1909-{i}', 'work': 'torti-1909', 'spex': spex, 'basis': 'toc', 'loc': f'p. {n}', 'url': TU + str(n), 'note': what})
tor('ann', [1, 20], 25, "Fascicle 3: the annotations, translated, as introduction.")
tor('fund', [23, 23], 33, "Day 1, exercises I–III: three considerations on the Foundation, the third on indifference before every election.")
tor('sins', [45, 54], 59, "Day 2, exercise IV: the threefold sin.")
tor('own', [55, 61], 71, "Exercise V: one's own sins, followed by an added meditation on venial sins.")
tor('hell', [65, 71], 87, "Exercise VII: hell. Day 3 adds death, the particular judgment and 'perfect conversion', for which the book leaves room in [71].")
tor('king', [91, 100], 133, "Exercises XI–XII: the Kingdom of Jesus Christ and its repetition, on the evening of day 3.")
tor('inc', [101, 117], 153, "Day 4: contemplation I joins the Incarnation and the Nativity, as Torti says he joins exercises the book keeps apart; then the Presentation, the flight into Egypt and the hidden life.")
tor('senses', [121, 126], 177, "Exercise XVI: application of the senses to the mysteries of the day.")
tor('stand', [136, 148], 185, "Day 5, exercises XVII–XVIII: the Two Standards and its repetition.")
tor('classes', [149, 157], 201, "Exercise XIX: the three classes of men.")
tor('humility', [165, 168], 209, "Exercise XX: the three degrees of humility, 'the sum of Christian perfection'.")
tor('third', [190, 209], 297, "Day 7: four contemplations of the Passion, ending in a summary of the whole Passion.")
tor('fourth', [218, 229], 337, "Day 8: the Resurrection and the apparition to Our Lady, the appearances, the Ascension.")
tor('love', [230, 237], 385, "Exercise XXXII: 'divine love stirs in us a love without measure', the Contemplation to Attain Love.")
tor('disc', [313, 336], 409, "Fascicle 43, § 1: rules for discernment, with a 'historical counterpart' (pp. 414–423): the conversion of the poet Adolphe Retté (1906), told as a living instance of the rules.")
tor('scruples', [345, 351], 423, "§ 2: scruples and 'two kindred serpentine persuasions'.")
tor('election', [169, 189], 426, "§ 3: on making a sound election, opening with a Latin text.")
tor('church', [352, 370], 440, "Translation of the rules for alms and for 'thinking sincerely with the Catholic Church'.")

# Benjamín Marcos, San Ignacio de Loyola (Madrid 1923), Project Gutenberg 63359. Read in full; pages from the
# page anchors of the Gutenberg HTML edition, which the links target.
MU = 'https://www.gutenberg.org/files/63359/63359-h/63359-h.htm#page_'
def mar(i, spex, pp, first, note, quote=None, basis='read'):
    g = {'id': f'marcos-1923-{i}', 'work': 'marcos-1923', 'spex': spex, 'basis': basis, 'loc': pp,
         'url': MU + str(first), 'linkLabel': 'Read in Project Gutenberg', 'note': note}
    if quote: g['quote'] = quote
    G.append(g)
mar('philosopher', None, 'pp. 145–280', 166,
    "The book belongs to a series on 'the great Spanish philosophers', after a first volume on Francisco Valles, and its thesis is that the Exercises hold the true philosophy against the materialism of the age: Ignatius is a philosopher because the book treats God as creator, the world in the creatures and man in his end. Its third chapter ends with Menéndez Pelayo's praise of Ignatius as the most living embodiment of the Spanish spirit.",
    "bien puede incluírsele entre las obras de los más esclarecidos, de los más grandes filósofos españoles")
mar('nexus', None, 'pp. 36–42', 36,
    "The book read as any well-written book: preface (the annotations), body (the four weeks), appendices (the methods of prayer, the mysteries, the rules). Its doctrine, Marcos says, is as old as the Church; what Ignatius did was to select it and give it a fixed plan.",
    "Lo que hizo San Ignacio fué seleccionar, escoger, adoptar estas doctrinas y acoplarlas para dar unidad, cohesión y viabilidad a la forma en que habían de hacerse los ejercicios")
mar('inner', None, 'pp. 66–76', 66,
    "The 'inner sources': the illumination by the Cardoner, quoted from the Autobiography, and the witnesses who call the book the work of divine instruction. On the tradition that the Virgin dictated it at Manresa he reports, citing the Monumenta, that it is held probable but not certain, and prints an engraving of the scene (p. 73).",
    "San Ignacio escribió los Ejercicios en Manresa, teniendo cierta ilustración sobrenatural")
mar('vita', [261, 312], 'pp. 77–98', 83,
    "The outer sources named as the Vita Christi, the Imitation, the Flos Sanctorum and the Bible. Montesino's Spanish Vita Christi is then printed in two columns beside the texts of the mysteries, from the Annunciation to the appearances after the Resurrection, and the proof is waived at once: the agreement is that of two books following the Gospels.",
    "nadie, al tratar de la vida y misterios de N. S. Jesucristo, puede alterar, en gran manera, el texto de los cuatro Evangelistas")
mar('cisneros', None, 'pp. 98–104', 98,
    "Cisneros' Ejercitatorio: the Montserrat witnesses for it, the Benedictine claim from Cayetano (1641) to Besse and Albers. His answer is that the Foundation, the particular examen, the Kingdom, the Three Classes and the rules for the election are not in the Ejercitatorio, which is a book for masters, not for exercitants. He ends by saying that Ignatius had read hardly a book and could not borrow from books he had not seen.",
    "mal podía tomar pasajes, ideas, pensamientos, sentencias, etc., de libros que no vió, como se le quiere atribuír")
mar('humility', [165, 168], 'p. 103', 103,
    "In the middle of the Benedictine dossier, a sentence derives the three kinds of humility from the twelve degrees of humility in the Rule of St Benedict, without a source.",
    "reduciendo a tres los doce que constituyen, según el Patriarca de los monjes de Occidente, toda la escala de la perfección")
mar('foundation', [23, 23], 'pp. 166–168, 218, 222–223', 166,
    "The Foundation as Ignatius' philosophy of God, world and man, and as the refutation of every school that puts man's end in pleasure. The words Marcos quotes under 'Principle and Foundation, point 1' ('Dios sacó todas las cosas de la nada…') are not in Ignatius' text: he is quoting a retreat book divided into points.",
    "él estudia a Dios como criador, al mundo, cuando habla de las criaturas, y al hombre, cuando analiza su fin")
mar('indifference', [23, 23], 'pp. 248–249', 248,
    "Indifference explained with a passage from Roothaan: created things are of themselves adiaphora, neither good nor bad, but not where God's law commands or forbids.",
    "Todas las cosas criadas de suyo son indiferentes, puesto que todas pueden igualmente o desayudar o ayudar a la consecución del fin del hombre.")
mar('powers', [45, 54], 'pp. 183–186, 238–239', 183,
    "The meditation on the three sins as a chain of comparison, judgment and conclusion, and the exercise of memory, understanding and will as proof of the unity and substance of the soul against those who reduce it to a series of phenomena; the scholastic axiom that nothing is in the intellect that was not first in the senses is ascribed to the method.",
    "nihil est in intellectu quod prius non fuerit in sensu")
mar('hell', [65, 71], 'pp. 223–225', 223,
    "Against the Cyrenaics, the lament of the damned soul, with the Ergo erravimus of Wisdom 5, quoted as Ignatius' words. The footnotes cite meditations called 'Hell of the soul', 'Death', 'Particular judgment' and 'Universal judgment': the retreat-manual form of the First Week, not the book. Placed on the hell exercise (editorial).",
    "Me he condenado por cosas que nunca satisficieron la sed de mi alma")
mar('kingdom', [91, 100], 'pp. 196–197', 196,
    "The call of the eternal King quoted at length in an expanded wording ('second part, point two' of a manual meditation), several times the length of the call in [95].",
    "Hijos míos: seguidme todos en esta empresa y conquista del Reino de los Cielos")
mar('standards', [136, 148], 'p. 264', 264,
    "The two standards as a providential division of mankind: those who follow Christ go to his Kingdom; those who leave him enlist under Lucifer, and still serve the ends of Providence without knowing it.",
    "los que se apartan de sus celestiales enseñanzas, es que se alistan en la “bandera de Lucifer, mortal enemigo de nuestra naturaleza humana”")
mar('bibliography', None, 'pp. 107–143', 107, "Lists of biographers of Ignatius, editions of the Exercises in Spanish and Latin, commentators and other writers on him, by the book's table of contents.", basis='toc')

json.dump({'_note': "Spanish and Italian reception before 1931 (tier A): Razón y Fe 1904-1919 (articles found by searching vols. 1-61 for the Exercises; authors from signatures and indexes; pages from the scans' running heads); Codina 1926 by its own subject index; Torti 1909 by its section heads; Marcos 1923 read in full in Project Gutenberg. Links go to the first page in the Internet Archive scan or the Gutenberg page anchor. Notes CC BY 4.0.",
           'glosses': G}, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(G))
