# Von Zeilen zu Regalen: NFDH gegen FFDH – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-regalverfahren-demo.streamlit.app/)**

Stück 7 der Konzepte-Reihe **„Packen: Reihenfolge und Platzierungsregel“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (ein Verfahren mit wachsendem Beispiel: eine Packung entsteht aus einer Reihenfolge der Teile und einer Regel, wohin das nächste kommt). Die Demo geht von Zahlen (Stücke 1 bis 4 und 14) zu **Rechtecken, die nicht überlappen dürfen**, und nimmt den einfachsten Dekodierer dafür: **Regale**. Sie fragt, wie viel an der Regel hängt (in welches Regal kommt das nächste Rechteck) und wie viel am Sortierschlüssel, und wie weit ein Regalplan vom Optimum entfernt ist. Die Fall-Demos zu Zuschnitt und Paletten zeigen die Anwendung samt Kostenmodell; diese Demo erklärt den Mechanismus davor.

## Warum dieses Problem

Bei einer Größe sortiert man „das größte zuerst“ und die Regel, wohin ein Teil kommt, ändert fast nichts. Bei Rechtecken in Regalen ist das anders: Die Regel zählt stark, und der Schlüssel „größte Fläche zuerst“ ist nicht der richtige, die Höhe ist es. Die Demo zeigt an zwölf Rechtecken, dass derselbe Satz Rechtecke je nach Reihenfolge und Regel 6 oder 3 Behälter braucht, und misst dasselbe an je 100 Zufallsinstanzen in 16 Zellen.

## Modell

Rechtecke mit ganzzahliger Breite und Höhe, ohne Drehung, in Behältern der Größe 100 mal 100, alle vorab bekannt. Ein **Regal** ist eine waagerechte Zeile; ihre Höhe ist die Höhe des ersten Rechtecks darin; ein Rechteck passt darauf, wenn es nicht höher ist und die belegte Breite plus seine Breite höchstens 100 ergibt. **Regeln:** *Next Fit* (nur das zuletzt geöffnete Regal, NFDH), *First Fit* (das erste passende Regal, FFDH), *Best Fit* (unter den passenden das mit der kleinsten Restbreite danach, BFDH); passt es auf kein Regal, kommt ein neues darüber, sonst ein neuer Behälter. **Schlüssel** (absteigend, Gleichstand: Lieferreihenfolge): Lieferreihenfolge, Höhe, Fläche, Breite. **Schranken:** die Fläche aller Rechtecke durch die Behälterfläche, aufgerundet, und die Zahl der Rechtecke, die in beiden Maßen über die Hälfte reichen (jedes braucht einen eigenen Behälter); das Größere von beiden. **Optimum** über alle Packungen (nicht nur Regalpläne) mit CP-SAT im Generator. **Vier Verteilungen:** *mittel* (Breite und Höhe 20 bis 60), *breit* (5 bis 70), *klein* (10 bis 40), *hoch schmal* (Breite 5 bis 30, Höhe 30 bis 80). Formeln im Expander 📐 der App.

## Methodik

- **Kern** (`rgv_algorithm.py`): `schluessel_wert`, `reihenfolge`, `pack` (drei Regeln, liefert Behälter und Platzierungen), `schranken`, `packung_pruefen` (unabhängiger Prüfer: jedes Rechteck genau einmal, im Behälter, keine Überlappung).
- **Handbeispiele:** zwei feste Mengen von je zwölf Rechtecken. Die App zeichnet die Behälter maßstäblich (Farbe = Regal) und zeigt alle 12 Kombinationen aus Schlüssel und Regel.
- **Messraster:** vier Verteilungen × vier Rechteckzahlen (12, 20, 40, 80) × **100 feste Instanzen** je Zelle. Maßstab ist bei 12 und 20 Rechtecken das Optimum (CP-SAT, 60 Sekunden Zeitlimit je Instanz, nicht entschiedene Instanzen fehlen im Mittel), bei 40 und 80 die Schranke. Die Summen stehen als ganze Zahlen in `rgv_precomputed.json` (erzeugt von `generate_precomputed.py`).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an den Instanzen dieser Demo (feste Seeds), nachgerechnet in `tests/test_claims.py`, `tests/test_algorithm.py` und `tests/test_oracle_regalverfahren.py`. Tabellenwerte sind Mittel über die Instanzen einer Zelle von (Behälter minus Vergleichsbasis).

| Frage | Befund |
|---|---|
| Beispiel 1 (zwölf Rechtecke, Schranke 3, Optimum 3) | Next / First Fit: in Lieferreihenfolge **6 / 5** Behälter, nach der Höhe **4 / 3**, nach der Fläche **5 / 4** (`tests/test_algorithm.py`) |
| Beispiel 2 (zwölf andere Rechtecke, Schranke 2, Optimum 3) | Next / First Fit: in Lieferreihenfolge **4 / 4**, nach der Höhe **4 / 3**, nach der Fläche **5 / 4**; die Schranke liegt unter dem Optimum |
| Ist First Fit besser als Next Fit? | Mit dem Schlüssel Höhe in allen 16 Zellen: in **1600** Instanzen nie schlechter. Mit den anderen drei Schlüsseln gibt es **7** Ausnahmen in 4800 Instanzen (Messung, kein Beweis) |
| Welcher Schlüssel ist am besten? | **Höhe** in allen **16** Zellen und bei jeder der drei Regeln (auf zwei Stellen gerundet verglichen) |
| Hilft „größte Fläche zuerst“? | Mit First Fit ja, aber weniger als die Höhe. Mit Next Fit ist Sortieren nach der Fläche in **6 von 16** Zellen schlechter als gar nicht zu sortieren (mittlere Rechtecke bei n = 20 und 80, breit gestreute bei allen vier Zahlen) |
| Zählt die Regel oder der Schlüssel mehr? | Beides: In **8** Zellen ist der Unterschied zwischen den Regeln (bei gleichem Schlüssel) größer als der zwischen den Schlüsseln (bei gleicher Regel), in den anderen **8** umgekehrt. Die Regeln unterscheiden sich um **0,38** bis **14,28** Behälter, die Schlüssel um **0,77** bis **11,37** |
| Best Fit gegen First Fit | Mit dem Schlüssel Höhe unterscheiden sie sich in jeder Zelle um höchstens **0,30** Behälter |
| Wie nah am Optimum? | First Fit nach Höhe trifft das Optimum bei 12 Rechtecken in 67 bis 80 % der entschiedenen Instanzen, bei 20 Rechtecken in 49 bis 96 % |
| Wie scharf ist die Schranke? | Das Optimum liegt bei 12 Rechtecken im Mittel 0,02 bis 0,37 über ihr (bei mittleren Rechtecken in 33 von 100 Instanzen darüber), bei 20 Rechtecken 0,00 bis 0,42; bei 40 und 80 fehlt das Optimum |
| Wie oft liegt die zweite Schranke („große Rechtecke“) über der Fläche? | In höchstens **5** von 100 Instanzen je Zelle, zusammen in **10** von 1600 |
| Wie viele Instanzen sind nicht entschieden? | **3** von 400 bei 12 und **39** von 400 bei 20 Rechtecken (**27** bei mittleren, 1 bei breit gestreuten, 0 bei kleinen und 11 bei hohen schmalen); die Zahl hängt von der Rechenzeit ab |

**Behälter über der Vergleichsbasis** (Mittel; Basis: Optimum bei 12 und 20 Rechtecken, nur über die entschiedenen Instanzen, sonst die Schranke; je Schlüssel die Regeln Next / First / Best; Maßstab bei 40 und 80 Rechtecken ist locker, dort zählt nur der Vergleich der Kombinationen):

| Verteilung | n | Basis | Lieferung Next | Lieferung First | Lieferung Best | Höhe Next | Höhe First | Höhe Best | Fläche Next | Fläche First | Fläche Best | Breite Next | Breite First | Breite Best |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mittel | 12 | Optimum | 1,98 | 1,18 | 1,23 | 0,88 | 0,31 | 0,30 | 1,80 | 0,64 | 0,64 | 1,89 | 1,05 | 1,05 |
| mittel | 20 | Optimum | 3,53 | 1,78 | 1,89 | 2,15 | 0,51 | 0,45 | 3,70 | 1,18 | 1,16 | 3,66 | 1,81 | 1,88 |
| mittel | 40 | Schranke | 7,94 | 3,53 | 3,81 | 4,48 | 1,23 | 1,18 | 7,93 | 2,30 | 2,31 | 7,96 | 3,49 | 3,63 |
| mittel | 80 | Schranke | 15,47 | 6,04 | 6,44 | 9,49 | 1,95 | 1,93 | 16,44 | 3,64 | 3,71 | 16,05 | 5,90 | 6,32 |
| breit | 12 | Optimum | 2,09 | 1,16 | 1,17 | 0,89 | 0,28 | 0,25 | 2,16 | 0,92 | 0,93 | 2,05 | 1,33 | 1,36 |
| breit | 20 | Optimum | 3,48 | 1,75 | 1,88 | 1,74 | 0,47 | 0,43 | 3,78 | 1,22 | 1,21 | 3,55 | 1,82 | 1,94 |
| breit | 40 | Schranke | 8,47 | 3,79 | 4,10 | 4,42 | 1,19 | 1,11 | 9,09 | 2,66 | 2,73 | 8,09 | 3,73 | 3,93 |
| breit | 80 | Schranke | 17,86 | 6,71 | 7,32 | 9,51 | 1,78 | 1,48 | 18,47 | 4,19 | 4,29 | 16,45 | 5,86 | 6,61 |
| klein | 12 | Optimum | 1,14 | 0,90 | 0,92 | 0,47 | 0,33 | 0,33 | 1,04 | 0,82 | 0,83 | 1,24 | 0,86 | 0,91 |
| klein | 20 | Optimum | 1,40 | 0,64 | 0,73 | 0,22 | 0,04 | 0,04 | 1,19 | 0,31 | 0,34 | 1,27 | 0,71 | 0,77 |
| klein | 40 | Schranke | 3,30 | 1,52 | 1,66 | 0,95 | 0,24 | 0,23 | 3,15 | 1,01 | 1,09 | 3,27 | 1,50 | 1,58 |
| klein | 80 | Schranke | 6,65 | 2,42 | 2,81 | 1,93 | 0,54 | 0,54 | 6,39 | 1,54 | 1,63 | 6,68 | 2,39 | 2,55 |
| hoch schmal | 12 | Optimum | 2,23 | 1,38 | 1,44 | 0,23 | 0,20 | 0,20 | 1,92 | 1,21 | 1,22 | 2,19 | 1,65 | 1,69 |
| hoch schmal | 20 | Optimum | 3,79 | 1,94 | 2,13 | 0,64 | 0,40 | 0,39 | 3,26 | 1,51 | 1,61 | 3,58 | 2,04 | 2,21 |
| hoch schmal | 40 | Schranke | 7,83 | 3,68 | 4,04 | 2,29 | 1,25 | 1,23 | 7,70 | 3,57 | 3,61 | 8,02 | 3,94 | 4,24 |
| hoch schmal | 80 | Schranke | 15,79 | 6,06 | 6,87 | 4,42 | 1,77 | 1,73 | 14,71 | 5,56 | 5,84 | 15,50 | 6,25 | 6,98 |

**Optimum getroffen** (Anteil der entschiedenen Instanzen, in denen die Kombination genau das Optimum braucht):

| Verteilung | n | Höhe First | Höhe Next | Fläche First | Lieferung First | Treffer Lieferung Next |
|---|---|---|---|---|---|---|
| mittel | 12 | 69 % | 20 % | 43 % | 8 % | 0 % |
| mittel | 20 | 49 % | 0 % | 12 % | 1 % | 0 % |
| breit | 12 | 72 % | 21 % | 29 % | 12 % | 3 % |
| breit | 20 | 53 % | 2 % | 14 % | 3 % | 0 % |
| klein | 12 | 67 % | 53 % | 18 % | 12 % | 2 % |
| klein | 20 | 96 % | 78 % | 69 % | 38 % | 0 % |
| hoch schmal | 12 | 80 % | 77 % | 9 % | 12 % | 3 % |
| hoch schmal | 20 | 60 % | 38 % | 4 % | 2 % | 0 % |

**Optimum gegen Schranke** (Mittel über die entschiedenen Instanzen; bei mittleren Rechtecken und 20 Rechtecken sind nur 73 von 100 Instanzen entschieden, und zwar die leichteren, der Mittelwert ist dort nach unten verzerrt):

| Verteilung | n | Optimum minus Schranke (Mittel) | Optimum über der Schranke | nicht entschieden |
|---|---|---|---|---|
| mittel | 12 | 0,33 | 33 von 100 | 0 |
| mittel | 20 | 0,14 | 10 von 73 | 27 |
| breit | 12 | 0,37 | 37 von 100 | 0 |
| breit | 20 | 0,42 | 40 von 99 | 1 |
| klein | 12 | 0,02 | 2 von 99 | 1 |
| klein | 20 | 0,00 | 0 von 100 | 0 |
| hoch schmal | 12 | 0,13 | 13 von 98 | 2 |
| hoch schmal | 20 | 0,37 | 33 von 89 | 11 |

## Ehrliche Grenzen

- Alle Aussagen gelten für Rechtecke ohne Drehung, vier Verteilungen mit festen Bereichen, vier Rechteckzahlen und eine Behältergröße. Andere Verteilungen, Drehung und Praxisdaten sind nicht gemessen.
- Das Optimum gilt über **alle** Packungen, nicht nur über Regalpläne; ein Teil des Abstands „Regalplan minus Optimum“ liegt am Regal als Dekodierer. Freie Platzierung ohne Regale (Skyline, MaxRects) ist nicht Gegenstand dieses Stücks.
- Das Optimum bei 20 Rechtecken kommt aus CP-SAT mit Zeitlimit; die nicht entschiedenen Instanzen sind die schweren und fehlen im Mittel. Bei mittleren Rechtecken sind 27 von 100 offen, der Mittelwert dort ist deshalb nach unten verzerrt, und die Zahl hängt von der Rechenzeit ab.
- Bei 40 und 80 Rechtecken fehlt das Optimum; die Schranke ist in 2D locker (schon bei 12 mittleren Rechtecken liegt das Optimum in 33 von 100 Instanzen darüber), also ist dort nur der Vergleich der Kombinationen belastbar, nicht der Abstand zur Schranke.
- Die Literaturhinweise (Coffman u. a. 1980 zu Regalverfahren beim Streifenpacken) stammen aus Suchtreffern, das Original wurde nicht gelesen; es wird keine Zahl und keine Gütegarantie daraus übernommen, und das Streifenproblem ist nicht dasselbe wie die Behälter dieser Demo.
- Das Raster sagt nichts über Rechtecke, die einzeln nacheinander ohne Kenntnis der späteren eintreffen (Online-Packen, Konzepte-Reihe Online-Algorithmen).

### Annahmen, Grenzen und bekannte Probleme (Text wie in der App)

**Annahmen.** Rechtecke mit ganzzahliger Breite und Höhe, ohne Drehung; Behälter 100 mal 100; alle Rechtecke sind vor dem Packen bekannt; Regale sind waagerechte Zeilen, deren Höhe das erste Rechteck darin festlegt.

**Grenzen.** Das Messraster deckt vier Verteilungen der Rechteckmaße und vier Rechteckzahlen ab, jeweils mit 100 Instanzen je Zelle. Praxisdaten, Drehung und freie Platzierung ohne Regale (Skyline, MaxRects) kommen nicht vor. Das exakte Optimum (über alle Packungen, nicht nur Regalpläne) gibt es bei 12 und 20 Rechtecken, bei 20 mit Zeitlimit; bei 40 und 80 Rechtecken fehlt es.

**Bekannte Probleme und Unsicherheiten.** Bei 40 und 80 Rechtecken ist der Maßstab die Schranke, die in 2D locker ist: Ein Teil des Abstands ist Schranke, nicht schlechtes Packen. Die Zahl der bei 20 Rechtecken nicht entschiedenen Instanzen hängt von der Rechenzeit ab. Die Mittelwerte des Rasters gelten für diese festen Instanzen; mit anderen Startzahlen ändern sie sich etwas, und eine einzelne Zelle ist kein Gesetz. Die Literaturhinweise im Mathematik-Expander stammen aus Suchtreffern (nur Zusammenfassungen), die Originale wurden nicht gelesen. Die App wurde im Browser bedient (Presets, Würfel-Button und Ausklapper auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät.

## Verifikation

- **Kern:** Next, First und Best Fit mit den Schlüsseln Lieferung und Höhe an einer von Hand gerechneten Mini-Instanz (sechs Rechtecke, Behälter 10 mal 10, mit den Platzierungen); Best Fit an einem Handbeispiel mit eindeutiger Wahl; beide Handbeispiele der App, Beispiel 1 mit den Behältern und Platzierungen der Packungen Next/Lieferung und First/Höhe; unabhängiger Packungsprüfer; Randfälle (leere Eingabe, ein Rechteck, Rechteck gleich Behälter, Grenzen inklusive, zu hohes Rechteck, kein Platz oben, ungültige Eingaben).
- **Orakel** (`tests/test_oracle_regalverfahren.py`): die drei Regeln gegen eine bewusst naive Zweitumsetzung (40 Instanzen, vier Schlüssel); das Optimum aus CP-SAT gegen eine vollständige Aufzählung aller ganzzahligen Positionen in sehr kleinen Behältern (25 Instanzen mit höchstens 4 Rechtecken); die Schranken nie über dem Optimum und alle Heuristiken nie darunter; Eigenschaften: gemeinsames Skalieren, Eingabereihenfolge bei sortierten Schlüsseln, bei Höhensortierung nehmen die Regalhöhen im Behälter nach oben nicht zu, jedes Rechteck ist höchstens so hoch wie sein Regal.
- **Messraster:** jede der 16 Zellen wird frisch gerechnet und exakt mit `rgv_precomputed.json` verglichen, bei 20 Rechtecken eine Stichprobe mit CP-SAT; jede Zahl dieser README als Textsuche (`tests/test_claims.py`).
- **Verdikte:** alle Zweige und Schwellen an von Hand gesetzten Werten (`tests/test_verdicts.py`).
- **Presets und Layout:** vollständig, Werte innerhalb der Reglergrenzen, erstes Preset gleich Standardeinstellung, jeder Hilfetext stimmt mit der Rechnung überein; Schnellstart oben in der Seitenleiste, fester Kopf, genau das passende Preset hervorgehoben (`tests/test_layout.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jede Auswahl in jedem Wert, Startzahl an den Grenzen) und Footer-Test.
- **Tests gesamt:** 137.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `dev/opt.py` | exaktes Optimum mit CP-SAT (nur Generator und Tests) |
| `dev/readme_bauen.py`, `dev/readme_vorlage.md` | setzen die README aus der Vorlage, den Tabellen der Messzellen und dem Text der Annahmen zusammen |
| `generate_precomputed.py` | erzeugt `rgv_precomputed.json` (Messraster); `--check` vergleicht, `--retry-u` rechnet nicht entschiedene Instanzen neu, `--keep-opt` behält die Optima |
| `requirements-dev.txt` | Laufzeit plus pytest und ortools |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `rgv_algorithm.py` | Kern: Schlüssel, Regalverfahren, Schranken, Packungsprüfer |
| `rgv_constants.py` | Beispiele, Reglerwerte, Messraster, Farben, Presets, Text der Annahmen |
| `rgv_evaluation.py` | Analyse, Verdikte, Messzellen |
| `rgv_layout.py` | Fester Kopf (Stylesheet) |
| `rgv_precomputed.json` | vorberechnete Summen und Optima des Messrasters |
| `rgv_presets.py` | Permalink (Begrenzen), Presets (Schnellstart, aktives Preset hervorgehoben), Würfel-Button |
| `rgv_scenario.py` | Instanzen: Handbeispiele und Zufallsinstanzen mit festen Seeds |
| `rgv_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Mini-Instanz und Handrechnung, Orakel, Randfälle, Verdikte, Presets, Layout, Messraster und Zahlen der README, AppTest-Rauchtest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Drehung der Rechtecke und freie Platzierung (Skyline, MaxRects):** nicht Gegenstand dieses Stücks.
- **Optimum bei mehr als 20 Rechtecken:** CP-SAT lässt schon bei 20 mittleren Rechtecken viele Instanzen offen.
- **Gütegarantien und Zahlen aus der Literatur:** Die Originale wurden nicht gelesen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit und Plotly.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
