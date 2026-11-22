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

json.dump({'_note': "Spanish and Italian reception before 1931 (tier A): Razón y Fe 1904-1919 (articles found by searching vols. 1-61 for the Exercises; authors from signatures and indexes; pages from the scans' running heads); Codina 1926 by its own subject index; Torti 1909 by its section heads. Links go to the first page in the Internet Archive scan. Notes CC BY 4.0.",
           'glosses': G}, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(G))
