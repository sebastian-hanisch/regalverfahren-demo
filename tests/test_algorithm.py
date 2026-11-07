"""Kern an der Mini-Instanz von Hand und an den Handbeispielen der App (DEMO-PLAYBOOK §1b).

Handrechnung Mini-Instanz (Behälter 10 mal 10; Rechtecke 0: (6, 4), 1: (5, 3), 2: (3, 2), 3: (4, 3), 4: (4, 3), 5: (4, 2); Fläche 77, Schranke 1):
  Next Fit, Lieferreihenfolge: 0 -> Regal 0 (Höhe 4, Breite 6); 1 -> 6 + 5 > 10, neues Regal 1 darüber (y = 4, Höhe 3); 2 -> letztes Regal, 5 + 3 = 8; 3 -> 8 + 4 > 10, neues Regal 2 (y = 7, Höhe 3,
      7 + 3 = 10 passt); 4 -> letztes Regal, 4 + 4 = 8; 5 -> 8 + 4 > 10, neues Regal wäre bei y = 10, 10 + 2 > 10, also neuer Behälter.         => [[0, 1, 2, 3, 4], [5]]
  First Fit, Lieferreihenfolge: 0 -> Regal 0; 1 -> Regal 1 (y = 4); 2 -> Regal 0 passt (6 + 3 = 9); 3 -> Regal 0 nicht (9 + 4), Regal 1 (5 + 4 = 9); 4 -> weder Regal 0 noch 1, neues Regal 2 (y = 7);
      5 -> Regal 0 nicht, Regal 1 nicht, Regal 2 (4 + 4 = 8).                                                                               => [[0, 1, 2, 3, 4, 5]]
  nach Höhe (Höhen 4, 3, 2, 3, 3, 2; Reihenfolge 0, 1, 3, 4, 2, 5): Next Fit 0 -> Regal 0; 1 -> Regal 1; 3 -> Regal 1 (5 + 4 = 9); 4 -> 9 + 4 > 10, Regal 2 (y = 7); 2 -> Regal 2 (4 + 3 = 7);
      5 -> 7 + 4 > 10, kein Platz oben, neuer Behälter.                                                                                    => [[0, 1, 3, 4, 2], [5]]
      First Fit: 0, 1, 3, 4 wie oben; 2 -> Regal 0 (6 + 3 = 9); 5 -> Regal 2 (4 + 4 = 8).                                                  => [[0, 1, 3, 4, 2, 5]]
"""

import pytest

import rgv_algorithm as A
import rgv_constants as C
import rgv_evaluation as ev
from rgv_scenario import beispiel


def _pack(inst, schluessel, regel):
    return A.pack(inst.rects, A.reihenfolge(inst.rects, schluessel), inst.cap, regel)


def test_next_fit_in_lieferreihenfolge_auf_der_mini_instanz(mini):
    bins, platz = _pack(mini, 0, 0)
    assert bins == [[0, 1, 2, 3, 4], [5]]
    assert sorted(platz) == [(0, 0, 0, 0), (1, 0, 0, 4), (2, 0, 5, 4), (3, 0, 0, 7), (4, 0, 4, 7), (5, 1, 0, 0)]


def test_first_fit_in_lieferreihenfolge_auf_der_mini_instanz(mini):
    bins, platz = _pack(mini, 0, 1)
    assert bins == [[0, 1, 2, 3, 4, 5]]
    assert sorted(platz) == [(0, 0, 0, 0), (1, 0, 0, 4), (2, 0, 6, 0), (3, 0, 5, 4), (4, 0, 0, 7), (5, 0, 4, 7)]


def test_sortieren_nach_hoehe_auf_der_mini_instanz(mini):
    assert A.reihenfolge(mini.rects, 1) == [0, 1, 3, 4, 2, 5]
    assert _pack(mini, 1, 0)[0] == [[0, 1, 3, 4, 2], [5]]
    assert _pack(mini, 1, 1)[0] == [[0, 1, 3, 4, 2, 5]]


def test_weitere_schluessel_auf_der_mini_instanz(mini):
    # Flächen 24, 15, 6, 12, 12, 8 -> 0, 1, 3, 4 (Gleichstand: Lieferreihenfolge), 5, 2
    assert A.reihenfolge(mini.rects, 2) == [0, 1, 3, 4, 5, 2]
    # Breiten 6, 5, 3, 4, 4, 4 -> 0, 1, 3, 4, 5 (Gleichstand: Lieferreihenfolge), 2
    assert A.reihenfolge(mini.rects, 3) == [0, 1, 3, 4, 5, 2]
    assert A.reihenfolge(mini.rects, 0) == [0, 1, 2, 3, 4, 5]


def test_best_fit_nimmt_das_passende_regal_mit_der_kleinsten_restbreite():
    # Regal 0 hat nach dem ersten Rechteck Breite 4 belegt (Höhe 5), Regal 1 (y = 5, Höhe 4) Breite 7. Das Rechteck (3, 3) passt auf beide: First Fit nimmt Regal 0 (4 + 3 = 7, Rest 3),
    # Best Fit Regal 1 (7 + 3 = 10, Rest 0).
    rects = ((4, 5), (7, 4), (3, 3))
    assert A.pack(rects, [0, 1, 2], 10, 1)[1] == [(0, 0, 0, 0), (1, 0, 0, 5), (2, 0, 4, 0)]
    assert A.pack(rects, [0, 1, 2], 10, 2)[1] == [(0, 0, 0, 0), (1, 0, 0, 5), (2, 0, 7, 5)]


def test_schranken_der_mini_instanz_und_eines_beispiels_mit_grossen_rechtecken(mini):
    assert A.schranken(mini.rects, mini.cap) == (1, 0, 1)
    # Fläche 3600 + 3850 + 900 = 8350 -> 1; (60, 60) und (55, 70) reichen in beiden Maßen über die Hälfte -> 2
    assert A.schranken(((60, 60), (55, 70), (30, 30)), 100) == (1, 2, 2)


# --- die Handbeispiele der App (Phase-0-Rechnung, von Hand nachgerechnet) -----------------------------------------------------------------


def test_beispiel_1_schranke_und_flaeche():
    inst = beispiel(0)
    assert A.schranken(inst.rects, inst.cap) == (3, 1, 3)
    assert sum(w * h for w, h in inst.rects) == 21_255      # 21255 / 10000 aufgerundet: 3; nur (52, 58) reicht in beiden Maßen über die Hälfte


def test_beispiel_1_lieferreihenfolge_next_fit_sechs_behaelter():
    """Von Hand: 0 -> B1; 1 (40,59) passt nicht oberhalb von 0 (43 + 59 > 100): B2; 2 -> B2 (40 + 41 = 81); 3 (20,58): 81 + 20 > 100, oben 59 + 58 > 100: B3; 4 -> B3 (20 + 47 = 67);
    5 (52,58): 67 + 52 > 100, oben 58 + 58 > 100: B4; 6 (56,21): 52 + 56 > 100, neues Regal bei y = 58 (58 + 21 = 79): B4; 7 (49,34): oben 79 + 34 > 100: B5; 8 (44,56): neues Regal bei y = 34
    (34 + 56 = 90): B5; 9 (34,50): 44 + 34 = 78; 10 (22,38): 78 + 22 = 100 passt (inklusive Grenze); 11 (39,35): 100 + 39 > 100, oben 90 + 35 > 100: B6."""
    inst = beispiel(0)
    bins, platz = _pack(inst, 0, 0)
    assert bins == [[0], [1, 2], [3, 4], [5, 6], [7, 8, 9, 10], [11]]
    assert A.packung_pruefen(inst.rects, platz, inst.cap)


def test_beispiel_1_nach_hoehe_first_fit_drei_behaelter():
    """Von Hand (Reihenfolge nach Höhe 59, 58, 58, 56, 50, 46, 45, 43, 38, 35, 34, 21 = Teile 1, 3, 5, 8, 9, 4, 2, 0, 10, 11, 7, 6): 1 -> B1 Regal 0 (Höhe 59); 3 -> daneben (40 + 20 = 60);
    5 (52,58) passt nicht (60 + 52), oben 59 + 58 > 100: B2; 8 (44,56) -> B2 (52 + 44 = 96); 9 (34,50) -> B1 Regal 0 (60 + 34 = 94); 4 (47,46): B1 und B2 voll, oben passt nicht: B3;
    2 (41,45) -> B3 (47 + 41 = 88); 0 (35,43): 88 + 35 > 100, neues Regal in B3 bei y = 46 (46 + 43 = 89); 10 (22,38) -> dieses Regal (35 + 22 = 57); 11 (39,35) -> 57 + 39 = 96; 7 (49,34): neues
    Regal in B1 bei y = 59 (59 + 34 = 93); 6 (56,21): B1 Regal 1 (49 + 56 > 100), B1 oben 93 + 21 > 100, B2 neues Regal bei y = 58 (58 + 21 = 79)."""
    inst = beispiel(0)
    assert A.reihenfolge(inst.rects, 1) == [1, 3, 5, 8, 9, 4, 2, 0, 10, 11, 7, 6]
    bins, platz = _pack(inst, 1, 1)
    assert bins == [[1, 3, 9, 7], [5, 8, 6], [4, 2, 0, 10, 11]]
    assert sorted(platz) == [(0, 2, 0, 46), (1, 0, 0, 0), (2, 2, 47, 0), (3, 0, 40, 0), (4, 2, 0, 0), (5, 1, 0, 0), (6, 1, 0, 58), (7, 0, 0, 59), (8, 1, 52, 0), (9, 0, 60, 0),
                             (10, 2, 35, 46), (11, 2, 57, 46)]
    assert A.packung_pruefen(inst.rects, platz, inst.cap)


def test_beispiele_zwoelf_kombinationen_der_phase_0():
    erwartet = {0: {(0, 0): 6, (0, 1): 5, (1, 0): 4, (1, 1): 3, (2, 0): 5, (2, 1): 4}, 1: {(0, 0): 4, (0, 1): 4, (1, 0): 4, (1, 1): 3, (2, 0): 5, (2, 1): 4}}
    for b, soll in erwartet.items():
        inst = beispiel(b)
        for (k, r), n in soll.items():
            assert A.anzahl(inst.rects, k, r, inst.cap) == n, (b, k, r)
    assert [A.schranke(beispiel(b).rects, C.CAP) for b in (0, 1)] == [3, 2] and C.BEISPIEL_OPTIMUM == {0: 3, 1: 3}


def test_alle_ergebnisse_der_beispiele_sind_zulaessige_packungen():
    for b in (0, 1):
        inst = beispiel(b)
        for k in C.SCHLUESSEL:
            for r in C.REGELN:
                bins, platz = _pack(inst, k, r)
                assert A.packung_pruefen(inst.rects, platz, inst.cap) and sorted(i for bb in bins for i in bb) == list(range(inst.n)), (b, k, r)


def test_packungspruefer_erkennt_fehler():
    rects = ((6, 4), (5, 3), (4, 2))
    ok = [(0, 0, 0, 0), (1, 0, 0, 4), (2, 0, 6, 0)]
    assert A.packung_pruefen(rects, ok, 10)
    assert not A.packung_pruefen(rects, [(0, 0, 0, 0), (1, 0, 5, 0), (2, 0, 6, 4)], 10)     # (0) und (1) überlappen
    assert not A.packung_pruefen(rects, [(0, 0, 5, 0), (1, 0, 0, 4), (2, 0, 6, 5)], 10)     # Rechteck 0 ragt über den Rand (5 + 6 > 10)
    assert A.packung_pruefen(rects, [(0, 0, 0, 0), (1, 0, 0, 4), (2, 0, 6, 8)], 10)         # 8 + 2 = 10: genau am oberen Rand, gültig (Grenze inklusive)
    assert not A.packung_pruefen(rects, [(0, 0, 0, 0), (1, 0, 0, 4), (2, 0, 6, 9)], 10)     # 9 + 2 = 11: ragt oben heraus
    assert not A.packung_pruefen(rects, ok[:2], 10)                                           # Rechteck 2 fehlt
    assert not A.packung_pruefen(rects, ok + [(2, 0, 0, 7)], 10)                              # Rechteck 2 doppelt
    assert A.packung_pruefen(rects, [(0, 0, 0, 0), (1, 1, 0, 0), (2, 1, 5, 0)], 10)         # zwei Behälter, kein Konflikt


@pytest.mark.parametrize("regel", [0, 1, 2])
def test_analyse_stimmt_mit_dem_kern_ueberein(regel):
    a = ev.analyse(ev.Settings(0, 0, 7, 1, regel))
    assert a.count == len(a.bins) == A.anzahl(a.inst.rects, 1, regel, a.inst.cap)
    assert a.liefer == A.anzahl(a.inst.rects, 0, regel, a.inst.cap) and a.opt == 3 and a.schranke == 3
