"""Jede Zahl der README und der App-Texte, nachgerechnet (DEMO-PLAYBOOK §4 und §11a).

* Das vorberechnete Raster (rgv_precomputed.json): jede der 16 Zellen frisch gerechnet; die Optima bei 12 und 20 Rechtecken aus der Datei (bei 12 wird eine Stichprobe, bei 20 eine
  kleine Stichprobe schnell lösbarer Instanzen mit CP-SAT nachgerechnet).
* Die Befunde der README werden aus denselben Auswertungsfunktionen wie in der App berechnet und als Text in der README gesucht.
* Der Text des Expanders „Annahmen, Grenzen und bekannte Probleme“ steht wörtlich in der README.
Dezimalzahlen stehen in der README mit Komma, in der App mit Punkt."""

import itertools
from pathlib import Path

import pytest

import rgv_algorithm as A
import rgv_constants as C
import rgv_evaluation as ev
from rgv_scenario import beispiel, mess_seed, zufallsinstanz

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
ZELLEN = list(itertools.product(range(len(C.VERTEILUNGEN)), range(len(C.MESS_N))))


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def alle():
    return {(v, ni): ev.zeile(v, ni) for v, ni in ZELLEN}


def test_raster_hat_alle_zellen_und_die_parameter():
    daten = ev.vorberechnet()
    assert daten["instanzen"] == C.INSTANZEN == 100 and daten["cap"] == C.CAP == 100 and daten["cpsat_zeitlimit"] == C.CPSAT_ZEITLIMIT == 60.0
    assert set(daten["zellen"]) == {ev.zelle_schluessel(v, ni) for v, ni in ZELLEN} and len(ZELLEN) == 16
    for (v, ni), n in ((k, C.MESS_N[k[1]]) for k in ZELLEN):
        z = daten["zellen"][ev.zelle_schluessel(v, ni)]
        assert ("opt" in z) == (n in C.EXAKT_N)
        if "opt" in z:
            assert len(z["opt"]) == 100


@pytest.mark.parametrize("v,ni", ZELLEN)
def test_jede_zelle_stimmt_mit_frischer_rechnung(v, ni):
    gespeichert = ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)]
    if C.MESS_N[ni] in C.EXAKT_N:
        frisch = ev.messzelle(v, ni, gespeichert["opt"])
        frisch["opt"] = gespeichert["opt"]
    else:
        frisch = ev.messzelle(v, ni)
    assert frisch == gespeichert


def test_gespeicherte_optima_liegen_zwischen_schranke_und_bester_heuristik():
    """Für jede entschiedene Instanz bei 12 und 20 Rechtecken: Schranke <= Optimum <= beste Heuristik (die Packung mit dieser Zahl existiert)."""
    for v, ni in ZELLEN:
        if C.MESS_N[ni] not in C.EXAKT_N:
            continue
        opt = ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)]["opt"]
        for j, o in enumerate(opt):
            if o < 0:
                continue
            inst = zufallsinstanz(v, C.MESS_N[ni], mess_seed(v, ni, j))
            ober = min(A.anzahl(inst.rects, k, r, inst.cap) for k in range(4) for r in range(3))
            assert A.schranke(inst.rects, inst.cap) <= o <= ober, (v, ni, j)


STICHPROBE_12 = {0: (9, 11), 1: (6, 7), 2: (7, 9), 3: (17, 27)}       # je zwei Instanzen, die CP-SAT in Bruchteilen von Sekunden entscheidet (bei kleinen Rechtecken ohne Optimum über der Schranke)


@pytest.mark.parametrize("v", range(len(C.VERTEILUNGEN)))
def test_stichprobe_der_optima_bei_12_rechtecken_stimmt_mit_cpsat_ueberein(v):
    pytest.importorskip("ortools")
    from dev.opt import optimum_cpsat

    ni = C.MESS_N.index(12)
    opt = ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)]["opt"]
    for j in STICHPROBE_12[v]:
        inst = zufallsinstanz(v, 12, mess_seed(v, ni, j))
        ober = min(A.anzahl(inst.rects, k, r, inst.cap) for k in range(4) for r in range(3))
        ist = ober if ober == A.schranke(inst.rects, inst.cap) else optimum_cpsat(inst.rects, inst.cap, ober, 60.0)
        assert ist == opt[j] >= 0, (v, j)


STICHPROBE_20 = {0: (28, 34), 1: (5, 6), 2: (0, 1), 3: (2, 6)}      # je zwei Instanzen, die CP-SAT schnell entscheidet (außer bei kleinen Rechtecken mit Optimum über der Schranke)


@pytest.mark.parametrize("v", range(len(C.VERTEILUNGEN)))
def test_stichprobe_der_optima_bei_20_rechtecken_stimmt_mit_cpsat_ueberein(v):
    pytest.importorskip("ortools")
    from dev.opt import optimum_cpsat

    ni = C.MESS_N.index(20)
    opt = ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)]["opt"]
    for j in STICHPROBE_20[v]:
        inst = zufallsinstanz(v, 20, mess_seed(v, ni, j))
        ober = min(A.anzahl(inst.rects, k, r, inst.cap) for k in range(4) for r in range(3))
        untergrenze = A.schranke(inst.rects, inst.cap)
        ist = ober if ober == untergrenze else optimum_cpsat(inst.rects, inst.cap, ober, 60.0)
        assert ist == opt[j] >= untergrenze, (v, j)
        if v != 2:
            assert opt[j] > untergrenze, (v, j)


# --- Tabellen der README -------------------------------------------------------------------------------------------------------------------


def test_readme_tabellen_geben_jede_zeile_wieder():
    from dev.readme_bauen import tabellen

    for tabelle in tabellen():
        for zeile in tabelle.split("\n"):
            assert zeile in README, zeile


# --- Befunde der README --------------------------------------------------------------------------------------------------------------------


def test_beispiele_in_der_readme():
    for b, (sch, opt, text) in {0: (3, 3, "Beispiel 1 (zwölf Rechtecke, Schranke 3, Optimum 3)"), 1: (2, 3, "Beispiel 2 (zwölf andere Rechtecke, Schranke 2, Optimum 3)")}.items():
        assert A.schranke(beispiel(b).rects, C.CAP) == sch and C.BEISPIEL_OPTIMUM[b] == opt and text in README
    z = {b: {(k, r): A.anzahl(beispiel(b).rects, k, r, C.CAP) for k in (0, 1, 2) for r in (0, 1)} for b in (0, 1)}
    assert [z[0][(k, r)] for k in (0, 1, 2) for r in (0, 1)] == [6, 5, 4, 3, 5, 4] and [z[1][(k, r)] for k in (0, 1, 2) for r in (0, 1)] == [4, 4, 4, 3, 5, 4]
    assert "in Lieferreihenfolge **6 / 5** Behälter, nach der Höhe **4 / 3**, nach der Fläche **5 / 4**" in README
    assert "in Lieferreihenfolge **4 / 4**, nach der Höhe **4 / 3**, nach der Fläche **5 / 4**" in README


def test_first_fit_ist_mit_hoehensortierung_nie_schlechter_als_next_fit():
    zellen = alle()
    assert sum(z["first_schlechter"][1] for z in zellen.values()) == 0 and len(zellen) * C.INSTANZEN == 1600
    ausnahmen = sum(z["first_schlechter"][k] for z in zellen.values() for k in (0, 2, 3))
    assert ausnahmen == 7 and len(zellen) * C.INSTANZEN * 3 == 4800
    assert "in **1600** Instanzen nie schlechter" in README and "gibt es **7** Ausnahmen in 4800 Instanzen" in README


def test_hoehe_ist_in_allen_zellen_der_beste_schluessel():
    for (v, ni), z in alle().items():
        _, m = ev.referenz(z)
        g = {k: {r: round(m[k][r], 2) for r in range(3)} for k in range(4)}
        assert all(g[1][r] <= g[k][r] for k in (0, 2, 3) for r in range(3)), (v, ni)
    assert "**Höhe** in allen **16** Zellen und bei jeder der drei Regeln" in README


def test_flaeche_schadet_bei_next_fit_in_sechs_zellen():
    schlechter = []
    for (v, ni), z in alle().items():
        _, m = ev.referenz(z)
        if round(m[2][0], 2) > round(m[0][0], 2):
            schlechter.append((v, C.MESS_N[ni]))
    assert schlechter == [(0, 20), (0, 80), (1, 12), (1, 20), (1, 40), (1, 80)]
    assert "in **6 von 16** Zellen schlechter als gar nicht zu sortieren (mittlere Rechtecke bei n = 20 und 80, breit gestreute bei allen vier Zahlen)" in README


def test_regel_gegen_schluessel_in_16_zellen():
    spannen = {k: ev.spannweiten(z) for k, z in alle().items()}
    assert len(spannen) == 16 and sum(r > s for r, s in spannen.values()) == 8 and sum(s > r for r, s in spannen.values()) == 8
    assert de(min(r for r, _ in spannen.values())) == "0,38" and de(max(r for r, _ in spannen.values())) == "14,28"
    assert de(min(s for _, s in spannen.values())) == "0,77" and de(max(s for _, s in spannen.values())) == "11,37"
    assert "In **8** Zellen ist der Unterschied zwischen den Regeln (bei gleichem Schlüssel) größer als der zwischen den Schlüsseln (bei gleicher Regel), in den anderen **8** umgekehrt" in README
    assert "Die Regeln unterscheiden sich um **0,38** bis **14,28** Behälter, die Schlüssel um **0,77** bis **11,37**" in README


def test_best_fit_und_first_fit_mit_hoehe_liegen_nahe_beieinander():
    abstand = 0
    for z in alle().values():
        _, m = ev.referenz(z)
        abstand = max(abstand, abs(round(m[1][1], 2) - round(m[1][2], 2)))
    assert de(abstand) == "0,30" and "um höchstens **0,30** Behälter" in README


def test_optimum_getroffen_und_schranke_gegen_optimum():
    t = {(v, ni): ev.zeile(v, ni) for v, ni in ZELLEN if C.MESS_N[ni] in C.EXAKT_N}
    assert [round(t[(v, 0)]["anteil_opt"][1][1]) for v in range(4)] == [69, 72, 67, 80]
    assert [round(t[(v, 1)]["anteil_opt"][1][1]) for v in range(4)] == [49, 53, 96, 60]
    assert "bei 12 Rechtecken in 67 bis 80 % der entschiedenen Instanzen, bei 20 Rechtecken in 49 bis 96 %" in README
    assert [de(t[(v, 0)]["opt_minus_schranke"]) for v in range(4)] == ["0,33", "0,37", "0,02", "0,13"]
    assert [de(t[(v, 1)]["opt_minus_schranke"]) for v in range(4)] == ["0,14", "0,42", "0,00", "0,37"] and t[(0, 0)]["opt_ueber_schranke"] == 33
    assert "bei 12 Rechtecken im Mittel 0,02 bis 0,37 über ihr (bei mittleren Rechtecken in 33 von 100 Instanzen darüber), bei 20 Rechtecken 0,00 bis 0,42" in README
    assert "schon bei 12 mittleren Rechtecken liegt das Optimum in 33 von 100 Instanzen darüber" in README


def test_experiment_2_zeigt_first_fit_mit_hoehe():
    """Die Tabelle von Experiment 2 nimmt die Kombination Höhe mit First Fit (nicht Höhe mit Next Fit): Treffer und Abstand stimmen mit den Zellen überein und unterscheiden sich von Next Fit."""
    zeilen = ev.optimum_zeilen()
    assert len(zeilen) == 8 and [(r["verteilung"], r["n"]) for r in zeilen] == [(v, n) for v in range(4) for n in (12, 20)]
    for r in zeilen:
        z = ev.zeile(r["verteilung"], C.MESS_N.index(r["n"]))
        assert r["treffer"] == z["anteil_opt"][1][1] and r["treffer"] != z["anteil_opt"][1][0]
        assert r["abstand"] == z["mittel_opt"][1][1] and r["abstand"] != z["mittel_opt"][1][0]
        assert r["opt_minus_schranke"] == z["opt_minus_schranke"] and r["ueber"] == z["opt_ueber_schranke"] and r["offen"] == z["offen"]


def test_zweite_schranke_liegt_selten_ueber_der_flaeche():
    zellen = alle()
    assert max(z["gross_ueber_flaeche"] for z in zellen.values()) == 5 and sum(z["gross_ueber_flaeche"] for z in zellen.values()) == 10
    assert "In höchstens **5** von 100 Instanzen je Zelle, zusammen in **10** von 1600" in README


def test_nicht_entschiedene_instanzen():
    offen12 = [ev.zeile(v, 0)["offen"] for v in range(4)]
    offen20 = [ev.zeile(v, 1)["offen"] for v in range(4)]
    assert offen12 == [0, 0, 1, 2] and offen20 == [27, 1, 0, 11] and sum(offen12) == 3 and sum(offen20) == 39
    assert ev.zeile(0, 1)["entschieden"] == 73
    assert "**3** von 400 bei 12 und **39** von 400 bei 20 Rechtecken (**27** bei mittleren, 1 bei breit gestreuten, 0 bei kleinen und 11 bei hohen schmalen)" in README
    assert "nur 73 von 100 Instanzen entschieden" in README and "Bei mittleren Rechtecken sind 27 von 100 offen" in README


# --- Beispiele und Texte --------------------------------------------------------------------------------------------------------------------


def test_annahmen_text_der_app_steht_woertlich_in_der_readme():
    assert C.ASSUMPTIONS_MARKDOWN in README


def test_zahlen_im_annahmen_text_sind_die_der_konstanten():
    t = C.ASSUMPTIONS_MARKDOWN
    assert f"Behälter {C.CAP} mal {C.CAP}" in t and f"{C.INSTANZEN} Instanzen" in t and "bei 12 und 20 Rechtecken" in t and "bei 40 und 80 Rechtecken" in t
    assert C.MESS_N == (12, 20, 40, 80) and C.EXAKT_N == (12, 20)


def test_readme_nennt_die_verteilungen_wie_der_code():
    assert "*mittel* (Breite und Höhe 20 bis 60), *breit* (5 bis 70), *klein* (10 bis 40), *hoch schmal* (Breite 5 bis 30, Höhe 30 bis 80)" in README
    assert [(vt[2], vt[3]) for vt in C.VERTEILUNGEN] == [((20, 60), (20, 60)), ((5, 70), (5, 70)), ((10, 40), (10, 40)), ((5, 30), (30, 80))]
    assert f"{C.CPSAT_ZEITLIMIT:.0f} Sekunden Zeitlimit je Instanz" in README
    assert "vier Verteilungen × vier Rechteckzahlen (12, 20, 40, 80) × **100 feste Instanzen**" in README
