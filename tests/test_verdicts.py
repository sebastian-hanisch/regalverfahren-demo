"""Verdikte (reine Funktionen in rgv_evaluation.py) an von Hand gesetzten Werten: jede Schwelle und jede Zahl im Text steht hier (DEMO-PLAYBOOK §12).

Die Analysen und Zellen werden von Hand gebaut, nicht aus Seeds gerechnet."""

import pytest

import rgv_constants as C
import rgv_evaluation as ev
from rgv_scenario import Instance


def _analyse(schluessel, regel, count, liefer, schranke, opt, tabelle=None):
    tab = tabelle or tuple(tuple(5 for _ in range(3)) for _ in range(4))
    return ev.Analysis(Instance(((5, 5),), 10), (0,), ((0,),), ((0, 0, 0, 0),), count, liefer, schranke, opt, tab, ev.Settings(0, 0, 7, schluessel, regel))


# --- verdict_aktuell -----------------------------------------------------------------------------------------------------------------------


def test_aktuell_schadet_ist_eine_warnung_mit_dem_unterschied_und_dem_optimum():
    kind, text = ev.verdict_aktuell(_analyse(2, 0, 5, 4, 3, 3))
    assert kind == "warning"
    assert "Nach der Fläche sortiert und mit Next Fit gesetzt brauchen die Rechtecke **5** Behälter, in Lieferreihenfolge 4." in text
    assert "Sortieren schadet hier um 1." in text and "Das Optimum ist **3**: 2 zu viel (die Schranke ist 3)." in text


def test_aktuell_spart_ist_ein_erfolg_und_nennt_das_optimum():
    kind, text = ev.verdict_aktuell(_analyse(1, 1, 3, 5, 3, 3))
    assert kind == "success"
    assert "Nach der Höhe sortiert und mit First Fit gesetzt brauchen die Rechtecke **3** Behälter, in Lieferreihenfolge 5." in text
    assert "Sortieren spart hier 2." in text and "Das ist das Optimum (die Schranke allein ergäbe 3)." in text


def test_aktuell_gleich_ist_info():
    kind, text = ev.verdict_aktuell(_analyse(3, 2, 4, 4, 2, 3))
    assert kind == "info" and "Nach der Breite sortiert und mit Best Fit gesetzt" in text and "Sortieren ändert hier nichts." in text
    assert "Sortieren schadet" not in text and "Sortieren spart" not in text and "Das Optimum ist **3**: 1 zu viel (die Schranke ist 2)." in text


def test_aktuell_ohne_optimum_nennt_die_schranke():
    kind, text = ev.verdict_aktuell(_analyse(1, 0, 9, 11, 6, None))
    assert kind == "success" and "Sortieren spart hier 2." in text
    assert "Das Optimum ist für diese Instanz nicht berechnet; die Schranke ist 6." in text


def test_aktuell_lieferreihenfolge_ist_info_ohne_vergleich():
    kind, text = ev.verdict_aktuell(_analyse(0, 1, 4, 4, 4, 4))
    assert kind == "info" and "In der Lieferreihenfolge mit First Fit brauchen die Rechtecke **4** Behälter." in text and "Sortieren schadet" not in text


@pytest.mark.parametrize("schluessel,wort", [(1, "der Höhe"), (2, "der Fläche"), (3, "der Breite")])
def test_aktuell_nennt_den_schluessel(schluessel, wort):
    assert f"Nach {wort} sortiert" in ev.verdict_aktuell(_analyse(schluessel, 0, 5, 4, 4, 4))[1]


# --- spannen und verdict_tabelle -----------------------------------------------------------------------------------------------------------


def _tab(zeilen):
    return tuple(tuple(z) for z in zeilen)


def test_spannen_regel_und_schluessel():
    t = _tab([(6, 5, 5), (4, 3, 3), (5, 4, 4), (6, 5, 5)])
    assert ev.spannen(t) == (1, 2)       # Regeln: jede Zeile hat Spanne 1; Schlüssel: Spalte 0 (6 gegen 4) -> 2, Spalte 1 (5 gegen 3) -> 2, Spalte 2 ebenso -> 2


def test_verdict_tabelle_regel_staerker_ist_erfolg():
    t = _tab([(9, 3, 3), (9, 3, 3), (9, 3, 3), (9, 3, 3)])
    assert ev.spannen(t) == (6, 0)
    kind, text = ev.verdict_tabelle(_analyse(1, 0, 9, 9, 3, 3, t))
    assert kind == "success" and "bis zu **6**" in text and "bis zu **0**" in text and "Hier zählt die Regel mehr als der Schlüssel." in text


def test_verdict_tabelle_gleich_stark_ist_info():
    t = _tab([(4, 4, 4), (4, 4, 4), (5, 5, 5), (4, 4, 4)])           # Regeln 0, Schlüssel 1
    assert ev.spannen(t) == (0, 1)
    t = _tab([(4, 5, 4), (4, 4, 4), (4, 4, 4), (4, 4, 4)])           # Regeln 1, Schlüssel 1
    assert ev.spannen(t) == (1, 1)
    kind, text = ev.verdict_tabelle(_analyse(1, 0, 4, 4, 4, 4, t))
    assert kind == "info" and "Beide wirken hier gleich stark." in text


def test_verdict_tabelle_schluessel_staerker_ist_warnung():
    t = _tab([(3, 3, 3), (8, 8, 8), (3, 3, 3), (3, 3, 3)])
    assert ev.spannen(t) == (0, 5)
    kind, text = ev.verdict_tabelle(_analyse(1, 0, 8, 8, 3, 3, t))
    assert kind == "warning" and "bis zu **0**" in text and "bis zu **5**" in text and "Hier zählt der Schlüssel mehr als die Regel." in text


# --- verdict_messung, referenz -------------------------------------------------------------------------------------------------------------


def _zelle(tab, verteilung=0, n=20, exakt=True, entschieden=100, instanzen=100):
    """tab: {Schlüssel: {Regel: Wert}} sowohl als Mittel über dem Optimum als auch über der Schranke."""
    return {"verteilung": verteilung, "name": C.VERTEILUNG_LANG[verteilung], "n": n, "instanzen": instanzen, "exakt": exakt, "entschieden": entschieden if exakt else 0,
            "offen": (instanzen - entschieden) if exakt else 0, "mittel_schranke": tab, "mittel_opt": tab if exakt and entschieden else None, "anteil_opt": None,
            "opt_minus_schranke": None, "opt_ueber_schranke": 0, "first_besser": dict.fromkeys(tab, 0), "first_schlechter": dict.fromkeys(tab, 0), "gross_ueber_flaeche": 0}


TAB_FLAECHE_SCHADET = {0: {0: 3.92, 1: 2.07, 2: 2.16}, 1: {0: 2.12, 1: 0.70, 2: 0.69}, 2: {0: 4.10, 1: 1.26, 2: 1.29}, 3: {0: 3.77, 1: 1.95, 2: 2.01}}
TAB_FLAECHE_OK = {0: {0: 6.68, 1: 2.36, 2: 2.84}, 1: {0: 1.81, 1: 0.46, 2: 0.44}, 2: {0: 6.31, 1: 1.54, 2: 1.61}, 3: {0: 6.48, 1: 2.21, 2: 2.43}}


def test_referenz_nimmt_das_optimum_wenn_bekannt_sonst_die_schranke():
    basis, m = ev.referenz(_zelle(TAB_FLAECHE_OK))
    assert basis == "dem Optimum" and m == TAB_FLAECHE_OK
    basis, m = ev.referenz(_zelle(TAB_FLAECHE_OK, n=40, exakt=False))
    assert basis == "der Schranke" and m == TAB_FLAECHE_OK
    basis, m = ev.referenz(_zelle(TAB_FLAECHE_OK, entschieden=0))
    assert basis == "der Schranke"


def test_messung_flaeche_schadet_bei_next_ist_warnung_mit_den_zahlen():
    kind, text = ev.verdict_messung(_zelle(TAB_FLAECHE_SCHADET))
    assert kind == "warning"
    assert "Für mittlere Rechtecke mit n = 20 liegt die beste Kombination, Höhe mit Best Fit, im Mittel 0.69 Behälter über dem Optimum (100 Instanzen)." in text
    assert "Mit der Höhe als Schlüssel braucht Next Fit 2.12, First Fit 0.70; nach der Fläche statt nach der Höhe sortiert braucht First Fit 1.26." in text
    assert "Next Fit nach der Fläche (4.10) ist **schlechter als Next Fit ohne Sortieren** (3.92)." in text


def test_messung_ohne_flaechenschaden_ist_info():
    kind, text = ev.verdict_messung(_zelle(TAB_FLAECHE_OK, verteilung=2, n=12))
    assert kind == "info" and "Für kleine Rechtecke mit n = 12" in text and "Höhe mit Best Fit" in text and "schlechter als Next Fit" not in text


def test_messung_nennt_mehrere_beste_kombinationen():
    tab = {k: {r: 1.0 for r in range(3)} for k in range(4)}
    text = ev.verdict_messung(_zelle(tab))[1]
    assert "Lieferung mit Next Fit und Lieferung mit First Fit und Lieferung mit Best Fit und Höhe mit Next Fit" in text and "im Mittel 1.00 Behälter" in text


def test_messung_vergleicht_die_auf_zwei_stellen_gerundeten_werte():
    tab = {k: dict(v) for k, v in TAB_FLAECHE_SCHADET.items()}
    tab[2][0] = 3.9204                  # angezeigt 3.92, gleich Next Fit ohne Sortieren: nicht schlechter
    kind, text = ev.verdict_messung(_zelle(tab))
    assert kind == "info" and "schlechter als Next Fit" not in text


def test_messung_nennt_nicht_entschiedene_instanzen():
    kind, text = ev.verdict_messung(_zelle(TAB_FLAECHE_OK, entschieden=96))
    assert "4 von 100 Instanzen sind nicht entschieden und fehlen im Mittel." in text and "(96 Instanzen)" in text


def test_messung_warnt_ohne_optimum_vor_der_lockeren_schranke():
    text = ev.verdict_messung(_zelle(TAB_FLAECHE_OK, n=80, exakt=False))[1]
    assert "über der Schranke (100 Instanzen)" in text and "Lesen Sie nur die Unterschiede zwischen den Kombinationen, nicht den Abstand." in text
    text = ev.verdict_messung(_zelle(TAB_FLAECHE_OK, n=12))[1]
    assert "nicht den Abstand" not in text


# --- verdict_regeln ------------------------------------------------------------------------------------------------------------------------


def test_regeln_regel_staerker_ist_erfolg():
    tab = {k: {0: 9.0, 1: 2.0, 2: 2.0} for k in range(4)}            # Regelspanne 7,00, Schlüsselspanne 0,00
    kind, text = ev.verdict_regeln(_zelle(tab))
    assert kind == "success" and "bis zu **7.00** Behälter" in text and "bis zu **0.00**" in text and "Die Regel entscheidet hier mehr als der Schlüssel." in text


def test_regeln_gleich_ist_info():
    tab = {k: {r: 1.0 for r in range(3)} for k in range(4)}
    kind, text = ev.verdict_regeln(_zelle(tab))
    assert kind == "info" and "bis zu **0.00** Behälter" in text and "Beide wirken hier gleich stark." in text


def test_regeln_schluessel_staerker_ist_warnung():
    tab = {k: {r: 1.0 for r in range(3)} for k in range(4)}
    tab[2] = {0: 3.0, 1: 3.0, 2: 3.5}                                 # Regelspanne 0,50 (Zeile 2), Schlüsselspanne 2,50 (Spalte 2)
    kind, text = ev.verdict_regeln(_zelle(tab))
    assert kind == "warning" and "bis zu **0.50** Behälter" in text and "bis zu **2.50**" in text and "Hier wirkt der Schlüssel stärker als die Regel." in text
    assert "mittlere Rechtecke mit n = 20" in text


# --- Experiment 2 ---------------------------------------------------------------------------------------------------------------------------


def _zeilen():
    return [{"verteilung": 0, "n": 12, "entschieden": 100, "offen": 0, "instanzen": 100, "treffer": 80.0, "abstand": 0.2, "opt_minus_schranke": 0.47, "ueber": 40},
            {"verteilung": 1, "n": 20, "entschieden": 97, "offen": 3, "instanzen": 100, "treffer": 55.0, "abstand": 0.5, "opt_minus_schranke": 0.62, "ueber": 60},
            {"verteilung": 2, "n": 12, "entschieden": 100, "offen": 0, "instanzen": 100, "treffer": 70.0, "abstand": 0.3, "opt_minus_schranke": 0.03, "ueber": 3}]


def test_optimum_verdikt_nennt_die_lockerste_zeile_und_die_schwaechste():
    kind, text = ev.verdict_optimum(_zeilen())
    assert kind == "info"
    assert ("Am lockersten ist die Schranke bei breit gestreuten Rechtecken mit n = 20: Das Optimum liegt im Mittel um **0.62** über ihr und in 60 von 97 entschiedenen Instanzen darüber. "
            "First Fit mit der Höhe trifft das Optimum am seltensten bei breit gestreuten Rechtecken mit n = 20: in 55 % der 97 entschiedenen Instanzen.") in text


def test_optimum_verdikt_ohne_optimum():
    z = [{"verteilung": 0, "n": 20, "entschieden": 0, "offen": 100, "instanzen": 100, "treffer": None, "abstand": None, "opt_minus_schranke": None, "ueber": 0}]
    assert ev.verdict_optimum(z) == ("info", "Es gibt keine Zelle mit bekanntem Optimum.")
