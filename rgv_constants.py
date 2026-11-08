"""Konstanten: Regler-Grenzen, feste Beispiele, Messraster, Farben und Presets."""

CAP = 100                 # Behälter 100 x 100 (Breite und Höhe)

# --- Beispiele (Rechtecke als (Breite, Höhe) in Lieferreihenfolge) -----------------------------------------------------------------------
# Beispiel 1: Schranke 3, Optimum 3 (CP-SAT, in den Tests nachgerechnet); Lieferung Next 6, First 5; Höhe Next 4, First 3; Fläche Next 5, First 4 (Phase 0, von Hand nachgerechnet).
# Beispiel 2: Schranke 2, Optimum 3; Lieferung Next 4, First 4; Höhe Next 4, First 3; Fläche Next 5, First 4.
BEISPIELE = {
    0: ((35, 43), (40, 59), (41, 45), (20, 58), (47, 46), (52, 58), (56, 21), (49, 34), (44, 56), (34, 50), (22, 38), (39, 35)),
    1: ((24, 58), (33, 44), (45, 37), (27, 29), (32, 35), (28, 57), (59, 53), (30, 26), (49, 50), (23, 43), (24, 54), (38, 47)),
}
BEISPIEL_OPTIMUM = {0: 3, 1: 3}

# Quellen der Instanz: 0 und 1 = Handbeispiele, 2 bis 5 = Zufallsinstanzen mit der jeweiligen Verteilung
QUELLEN = {0: "Beispiel 1 (zwölf Rechtecke)", 1: "Beispiel 2 (zwölf andere Rechtecke)", 2: "zufällig, mittlere Rechtecke", 3: "zufällig, breit gestreute Rechtecke",
           4: "zufällig, kleine Rechtecke", 5: "zufällig, hohe schmale Rechtecke"}
ZUFALL_QUELLEN = (2, 3, 4, 5)
N_WERTE = (12, 20, 40)                    # Zahl der Rechtecke der Zufallsinstanzen in der App

# Verteilungen: (Schlüssel, Name, Bereich der Breite, Bereich der Höhe)
VERTEILUNGEN = (
    ("mittel", "mittlere Rechtecke (20 bis 60)", (20, 60), (20, 60)),
    ("breit", "breit gestreute Rechtecke (5 bis 70)", (5, 70), (5, 70)),
    ("klein", "kleine Rechtecke (10 bis 40)", (10, 40), (10, 40)),
    ("hochschmal", "hohe schmale Rechtecke (Breite 5 bis 30, Höhe 30 bis 80)", (5, 30), (30, 80)),
)
VERTEILUNG_KURZ = ("mittel", "breit", "klein", "hoch schmal")
VERTEILUNG_LANG = ("mittlere Rechtecke", "breit gestreute Rechtecke", "kleine Rechtecke", "hohe schmale Rechtecke")
VERTEILUNG_DAT = ("mittleren Rechtecken", "breit gestreuten Rechtecken", "kleinen Rechtecken", "hohen schmalen Rechtecken")   # nach „bei“

SCHLUESSEL = {0: "Lieferreihenfolge (nicht sortiert)", 1: "nach Höhe (höchstes zuerst)", 2: "nach Fläche (größte zuerst)", 3: "nach Breite (breiteste zuerst)"}
SCHLUESSEL_KURZ = {0: "Lieferung", 1: "Höhe", 2: "Fläche", 3: "Breite"}
SCHLUESSEL_MIT = {0: "der Lieferreihenfolge", 1: "der Höhe", 2: "der Fläche", 3: "der Breite"}

REGELN = {0: "nur das letzte Regal (Next Fit, NFDH)", 1: "erstes passendes Regal (First Fit, FFDH)", 2: "passendstes Regal (Best Fit, BFDH)"}
REGEL_KURZ = {0: "Next", 1: "First", 2: "Best"}
REGEL_NAME = {0: "Next Fit", 1: "First Fit", 2: "Best Fit"}
REGEL_CODES = {0: "next", 1: "first", 2: "best"}

SEED_MAX, DEFAULT_SEED = 999999, 7

# --- Messraster ---------------------------------------------------------------------------------------------------------------------------
INSTANZEN = 100                           # Instanzen je Zelle; der Wert steht neben jeder Zahl
MESS_N = (12, 20, 40, 80)
EXAKT_N = (12, 20)                        # in diesen Zellen gibt es das Optimum (CP-SAT mit Zeitlimit, ggf. nicht entschieden)
CPSAT_ZEITLIMIT = 60.0                    # Sekunden je Instanz (Generator); nicht entschiedene Instanzen stehen in einer eigenen Spalte

COLOR_LINE = "#c0392b"
COLOR_BARS = "#4c78a8"
REGAL_FARBEN = ("#4c78a8", "#f58518", "#54a24b", "#b279a2", "#e45756", "#72b7b2", "#9d755d", "#bab0ac", "#eeca3b", "#ff9da6")
REGEL_FARBEN = {0: "#c0392b", 1: "#2F6B65", 2: "#4c78a8"}

PRESETS = {
    "Beispiel 1, Lieferung, nur das letzte Regal": {"quelle": 0, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": 0, "regel": 0},
    "Beispiel 1, nach Höhe, erstes passendes Regal": {"quelle": 0, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": 1, "regel": 1},
    "Beispiel 2, nach Fläche, erstes passendes Regal": {"quelle": 1, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": 2, "regel": 1},
    "Mittlere Rechtecke, nach Höhe, nur das letzte Regal": {"quelle": 2, "n_index": 1, "seed": DEFAULT_SEED, "schluessel": 1, "regel": 0},
}
PRESET_HELP = {
    "Beispiel 1, Lieferung, nur das letzte Regal": "Zwölf Rechtecke in der Reihenfolge, in der sie ankommen; jedes kommt in das zuletzt geöffnete Regal oder, wenn es dort nicht passt, in ein neues. Das sind sechs Behälter.",
    "Beispiel 1, nach Höhe, erstes passendes Regal": "Dieselben zwölf Rechtecke, nach der Höhe sortiert und in das erste Regal gesetzt, in dem sie passen. Das sind drei Behälter, so viele wie das Optimum.",
    "Beispiel 2, nach Fläche, erstes passendes Regal": "Ein zweites Beispiel, nach der Fläche sortiert (wie „das größte zuerst“ bei einer Größe). Hier ist die Höhe die bessere Wahl.",
    "Mittlere Rechtecke, nach Höhe, nur das letzte Regal": "Eine Zufallsinstanz mit 20 mittleren Rechtecken: Auch sortiert nach der Höhe braucht „nur das letzte Regal“ hier einen Behälter mehr als „erstes passendes Regal“ (im Mittel dieser Zelle 1,6).",
}

# Text des Expanders „Annahmen, Grenzen und bekannte Probleme“; derselbe Wortlaut steht in der README (tests/test_claims.py vergleicht beide).
ASSUMPTIONS_MARKDOWN = f"""**Annahmen.** Rechtecke mit ganzzahliger Breite und Höhe, ohne Drehung; Behälter {CAP} mal {CAP}; alle Rechtecke sind vor dem Packen bekannt; Regale sind waagerechte Zeilen, deren Höhe das erste Rechteck darin festlegt.

**Grenzen.** Das Messraster deckt vier Verteilungen der Rechteckmaße und vier Rechteckzahlen ab, jeweils mit {INSTANZEN} Instanzen je Zelle. Praxisdaten, Drehung und freie Platzierung ohne Regale (Skyline, MaxRects) kommen nicht vor. Das exakte Optimum (über alle Packungen, nicht nur Regalpläne) gibt es bei 12 und 20 Rechtecken, bei 20 mit Zeitlimit; bei 40 und 80 Rechtecken fehlt es.

**Bekannte Probleme und Unsicherheiten.** Bei 40 und 80 Rechtecken ist der Maßstab die Schranke, die in 2D locker ist: Ein Teil des Abstands ist Schranke, nicht schlechtes Packen. Die Zahl der bei 20 Rechtecken nicht entschiedenen Instanzen hängt von der Rechenzeit ab. Die Mittelwerte des Rasters gelten für diese festen Instanzen; mit anderen Startzahlen ändern sie sich etwas, und eine einzelne Zelle ist kein Gesetz. Die Literaturhinweise im Mathematik-Expander stammen aus Suchtreffern (nur Zusammenfassungen), die Originale wurden nicht gelesen. Die App wurde im Browser bedient (Presets, Würfel-Button und Ausklapper auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät."""
