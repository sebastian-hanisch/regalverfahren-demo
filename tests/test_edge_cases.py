"""Randfälle: leere Eingabe, ein Rechteck, Rechteck gleich Behälter, genau passende Regale, Gleichstände, ungültige Eingaben."""

import pytest

import rgv_algorithm as A
import rgv_constants as C
from rgv_scenario import Instance, mess_seed, zufallsinstanz


@pytest.mark.parametrize("regel", [0, 1, 2])
def test_leere_eingabe_ergibt_keine_behaelter(regel):
    assert A.pack((), [], 10, regel) == ([], [])
    assert A.schranken((), 10) == (0, 0, 0)


@pytest.mark.parametrize("regel", [0, 1, 2])
def test_ein_rechteck_und_rechteck_gleich_behaelter(regel):
    assert A.pack(((7, 3),), [0], 10, regel) == ([[0]], [(0, 0, 0, 0)])
    bins, platz = A.pack(((10, 10), (1, 1)), [0, 1], 10, regel)
    assert bins == [[0], [1]] and platz == [(0, 0, 0, 0), (1, 1, 0, 0)]


@pytest.mark.parametrize("regel", [0, 1, 2])
def test_grenzen_sind_inklusive(regel):
    # Breite: 5 + 5 = 10 passt auf ein Regal; Höhe: 5 + 5 = 10 passt in einen Behälter
    bins, platz = A.pack(((5, 5), (5, 5), (5, 5), (5, 5)), [0, 1, 2, 3], 10, regel)
    assert bins == [[0, 1, 2, 3]] and sorted(platz) == [(0, 0, 0, 0), (1, 0, 5, 0), (2, 0, 0, 5), (3, 0, 5, 5)]


@pytest.mark.parametrize("regel", [0, 1, 2])
def test_ein_zu_hohes_rechteck_oeffnet_ein_neues_regal_obwohl_breite_frei_ist(regel):
    # Regal 0 hat Höhe 3 und noch 6 Breite frei; das Rechteck (4, 4) ist höher als das Regal und kommt auf ein neues Regal darüber
    bins, platz = A.pack(((4, 3), (4, 4)), [0, 1], 10, regel)
    assert bins == [[0, 1]] and platz == [(0, 0, 0, 0), (1, 0, 0, 3)]


@pytest.mark.parametrize("regel", [0, 1, 2])
def test_kein_platz_oben_oeffnet_einen_neuen_behaelter(regel):
    # zwei Regale der Höhe 6 und 5 passen nicht übereinander (11 > 10)
    bins, _ = A.pack(((10, 6), (10, 5)), [0, 1], 10, regel)
    assert bins == [[0], [1]]


def test_next_fit_geht_nie_zurueck_und_first_fit_schon():
    # Regal 0 (Höhe 5) hat Breite 5 belegt, Regal 1 (Höhe 3) Breite 9. Das Rechteck (3, 2) passt auf Regal 0 (5 + 3 = 8), nicht auf Regal 1 (9 + 3 = 12).
    # Next Fit schaut nur auf Regal 1 und öffnet Regal 2 (y = 8); First Fit nimmt Regal 0.
    rects = ((5, 5), (9, 3), (3, 2))
    assert A.pack(rects, [0, 1, 2], 10, 0)[1] == [(0, 0, 0, 0), (1, 0, 0, 5), (2, 0, 0, 8)]
    assert A.pack(rects, [0, 1, 2], 10, 1)[1] == [(0, 0, 0, 0), (1, 0, 0, 5), (2, 0, 5, 0)]


def test_gleichstand_beim_sortieren_haelt_die_lieferreihenfolge():
    assert A.reihenfolge(((3, 4), (5, 4), (2, 4)), 1) == [0, 1, 2]
    assert A.reihenfolge(((3, 4), (5, 4), (2, 4)), 3) == [1, 0, 2]
    assert A.reihenfolge(((2, 6), (3, 4), (4, 3)), 2) == [0, 1, 2]       # Flächen 12 und 12 und 12: Lieferreihenfolge


def test_schranke_nimmt_das_groessere_von_flaeche_und_grossen_rechtecken():
    assert A.schranken(((51, 51), (51, 51), (51, 51)), 100) == (1, 3, 3)       # Fläche 7803 -> 1, drei große
    assert A.schranken(((50, 50), (50, 50), (50, 50), (50, 50)), 100) == (1, 0, 1)   # genau die Hälfte ist nicht „über die Hälfte“: Fläche 10000 -> 1, keine großen
    assert A.schranken(((100, 100), (1, 1)), 100) == (2, 1, 2)


def test_ungueltige_eingaben_werfen():
    with pytest.raises(ValueError):
        A.pack(((11, 1),), [0], 10, 0)         # Breite größer als der Behälter
    with pytest.raises(ValueError):
        A.pack(((1, 11),), [0], 10, 0)         # Höhe größer als der Behälter
    with pytest.raises(ValueError):
        A.pack(((0, 1),), [0], 10, 0)          # Maß null
    with pytest.raises(ValueError):
        A.pack(((3, 4), (2, 2)), [0, 0], 10, 0)    # keine Permutation
    with pytest.raises(ValueError):
        A.pack(((3, 4), (2, 2)), [0], 10, 0)       # unvollständige Reihenfolge
    with pytest.raises(ValueError):
        A.pack(((3, 4),), [0], 10, 7)              # unbekannte Regel
    with pytest.raises(ValueError):
        A.reihenfolge(((3, 4),), 9)                # unbekannter Schlüssel
    with pytest.raises(ValueError):
        Instance(((3, 4),), 0)
    with pytest.raises(ValueError):
        Instance(((3, 11),), 10)


def test_zufallsinstanz_ist_deterministisch_und_haelt_die_bereiche():
    for v, (_, _, (wl, wh), (hl, hh)) in enumerate(C.VERTEILUNGEN):
        inst = zufallsinstanz(v, 50, 123)
        assert inst == zufallsinstanz(v, 50, 123) and inst != zufallsinstanz(v, 50, 124)
        assert all(wl <= w <= wh and hl <= h <= hh for w, h in inst.rects)
    assert mess_seed(0, 0, 0) == 1_001_000 and mess_seed(3, 3, 99) == 4_004_099
