"""Orakel-Tests (DEMO-PLAYBOOK §12): jede Kernroutine gegen einen anderen Rechenweg, feste Seeds, zusammen unter 10 Sekunden.

  Regalverfahren (Next, First, Best Fit)   gegen  eine bewusst naive Zweitumsetzung (Regale als Listen von Rechtecken, Belegung jedes Mal neu summiert).
  Optimum (CP-SAT, dev/opt.py)             gegen  eine Aufzählung aller ganzzahligen Positionen in sehr kleinen Behältern (Kantenlänge 5, höchstens 4 Rechtecke).
  Schranken                                gegen  das Optimum: Fläche und große Rechtecke nie darüber.
  Packungen                                gegen  den unabhängigen Prüfer.
  Eigenschaften: gemeinsames Skalieren, Eingabereihenfolge bei sortierten Schlüsseln ohne Gleichstand, Regalhöhen bei Höhensortierung.
"""

import random

import pytest

import rgv_algorithm as A


def instanzen(anzahl, n_lo, n_hi, cap_lo=10, cap_hi=40, seed0=0):
    for seed in range(seed0, seed0 + anzahl):
        rng = random.Random(seed)
        cap = rng.randint(cap_lo, cap_hi)
        n = rng.randint(n_lo, n_hi)
        yield cap, tuple((rng.randint(1, cap), rng.randint(1, cap)) for _ in range(n))


# --- Orakel für die Regeln ---------------------------------------------------------------------------------------------------------------------


def pack_naiv(rects, order, cap, regel):
    """Zweitumsetzung: jedes Regal ist ein Dict mit der Liste seiner Rechtecke; Höhe = Höhe des ersten Rechtecks, Belegung = Summe der Breiten, bei jeder Frage neu gerechnet."""
    behaelter = []                                   # je Behälter: Liste von Regalen {"y": ..., "teile": [...]}
    for i in order:
        w, h = rects[i]
        sicht = [(b, s) for b in range(len(behaelter)) for s in range(len(behaelter[b]))]
        if regel == 0 and sicht:
            sicht = [sicht[-1]]
        passend = []
        for b, s in sicht:
            teile = behaelter[b][s]["teile"]
            hoehe = rects[teile[0]][1]
            belegt = sum(rects[t][0] for t in teile)
            if h <= hoehe and belegt + w <= cap:
                passend.append((b, s, cap - belegt - w))
        if passend:
            if regel == 2:
                b, s, _ = min(passend, key=lambda t: (t[2], t[0], t[1]))
            else:
                b, s, _ = passend[0]
            behaelter[b][s]["teile"].append(i)
            continue
        ziele = [len(behaelter) - 1] if (regel == 0 and behaelter) else list(range(len(behaelter)))
        platziert = False
        for b in ziele:
            oben = sum(rects[sh["teile"][0]][1] for sh in behaelter[b])
            if oben + h <= cap:
                behaelter[b].append({"teile": [i]})
                platziert = True
                break
        if not platziert:
            behaelter.append([{"teile": [i]}])
    return [[t for sh in b for t in sh["teile"]] for b in behaelter]


@pytest.mark.parametrize("regel", [0, 1, 2])
def test_regeln_gegen_die_naive_zweitumsetzung(regel):
    for cap, rects in instanzen(40, 1, 25, cap_lo=10, cap_hi=100, seed0=300):
        for schluessel in (0, 1, 2, 3):
            order = A.reihenfolge(rects, schluessel)
            bins, platz = A.pack(rects, order, cap, regel)
            assert sorted(sorted(b) for b in bins) == sorted(sorted(b) for b in pack_naiv(rects, order, cap, regel)), (cap, rects, schluessel)
            assert A.packung_pruefen(rects, platz, cap)


# --- Orakel für das Optimum ----------------------------------------------------------------------------------------------------------------------


def optimum_aufzaehlung(rects, cap):
    """Kleinste Behälterzahl durch Aufzählung: Rechteck für Rechteck an jede ganzzahlige Position eines vorhandenen oder eines neuen Behälters (neu: alle Positionen)."""
    n = len(rects)
    if n == 0:
        return 0
    best = n

    def passt(belegt, x, y, w, h):
        return all(x + w <= bx or bx + bw <= x or y + h <= by or by + bh <= y for bx, by, bw, bh in belegt)

    def rec(i, behaelter):
        nonlocal best
        if len(behaelter) >= best:
            return
        if i == n:
            best = len(behaelter)
            return
        w, h = rects[i]
        for lst in behaelter:
            for x in range(cap - w + 1):
                for y in range(cap - h + 1):
                    if passt(lst, x, y, w, h):
                        lst.append((x, y, w, h))
                        rec(i + 1, behaelter)
                        lst.pop()
        if len(behaelter) + 1 < best:
            for x in range(cap - w + 1):
                for y in range(cap - h + 1):
                    behaelter.append([(x, y, w, h)])
                    rec(i + 1, behaelter)
                    behaelter.pop()

    rec(0, [])
    return best


def _kleine_instanzen():
    rng = random.Random(777)
    for _ in range(25):
        n = rng.randint(2, 4)
        yield tuple((rng.randint(2, 5), rng.randint(2, 5)) for _ in range(n))


def test_aufzaehlung_gegen_cpsat_bei_sehr_kleinen_behaeltern():
    pytest.importorskip("ortools")
    from dev.opt import optimum_cpsat

    for rects in _kleine_instanzen():
        ober = min(A.anzahl(rects, k, r, 5) for k in range(4) for r in range(3))
        fl, gr, s = A.schranken(rects, 5)
        soll = optimum_aufzaehlung(rects, 5)
        ist = ober if ober == s else optimum_cpsat(rects, 5, ober, 30.0)
        assert ist == soll, (rects, ist, soll)
        assert s <= soll <= ober, (rects, s, soll, ober)


def test_schranken_nie_ueber_dem_optimum_und_heuristiken_nie_darunter():
    for rects in _kleine_instanzen():
        fl, gr, s = A.schranken(rects, 5)
        opt = optimum_aufzaehlung(rects, 5)
        assert fl <= opt and gr <= opt
        for k in range(4):
            for r in range(3):
                assert A.anzahl(rects, k, r, 5) >= opt


# --- Eigenschaften -----------------------------------------------------------------------------------------------------------------------------


def test_gemeinsames_skalieren_aendert_die_behaelterzahl_nicht():
    for cap, rects in instanzen(30, 1, 15, cap_lo=10, cap_hi=40, seed0=1100):
        gross = tuple((3 * w, 3 * h) for w, h in rects)
        for k in range(4):
            for r in range(3):
                assert A.anzahl(gross, k, r, 3 * cap) == A.anzahl(rects, k, r, cap), (cap, rects, k, r)
        assert A.schranken(gross, 3 * cap)[1:] == A.schranken(rects, cap)[1:]


def test_eingabereihenfolge_aendert_die_sortierten_schluessel_ohne_gleichstand_nicht():
    rng = random.Random(1300)
    geprueft = 0
    for cap, rects in instanzen(60, 2, 15, cap_lo=60, cap_hi=300, seed0=1300):
        gemischt = list(rects)
        rng.shuffle(gemischt)
        for k in range(1, 4):
            if len(set(A.schluessel_wert(rects, k))) < len(rects):
                continue
            geprueft += 1
            for r in range(3):
                a = A.pack(rects, A.reihenfolge(rects, k), cap, r)[1]
                b = A.pack(tuple(gemischt), A.reihenfolge(tuple(gemischt), k), cap, r)[1]
                lage = lambda rs, pl: sorted((rs[i], bb, x, y) for i, bb, x, y in pl)    # noqa: E731
                assert lage(rects, a) == lage(tuple(gemischt), b), (cap, rects, k, r)
    assert geprueft >= 100            # der Test prüft wirklich etwas


def test_bei_hoehensortierung_nehmen_die_regalhoehen_im_behaelter_nach_oben_nicht_zu():
    for cap, rects in instanzen(40, 2, 25, cap_lo=20, cap_hi=100, seed0=1500):
        for r in range(3):
            bins, platz = A.pack(rects, A.reihenfolge(rects, 1), cap, r)
            for b in range(len(bins)):
                regale = {}
                for i, bb, x, y in platz:
                    if bb == b:
                        regale[y] = max(regale.get(y, 0), rects[i][1])
                hoehen = [regale[y] for y in sorted(regale)]
                assert hoehen == sorted(hoehen, reverse=True), (cap, rects, r, b)


def test_jedes_rechteck_ist_hoechstens_so_hoch_wie_sein_regal():
    for cap, rects in instanzen(40, 2, 25, cap_lo=20, cap_hi=100, seed0=1700):
        for k in range(4):
            for r in range(3):
                _, platz = A.pack(rects, A.reihenfolge(rects, k), cap, r)
                regal_hoehe = {}
                for i, b, x, y in sorted(platz, key=lambda p: (p[1], p[3], p[2])):
                    regal_hoehe.setdefault((b, y), rects[i][1])       # das erste Rechteck von links legt die Höhe fest
                assert all(rects[i][1] <= regal_hoehe[(b, y)] for i, b, x, y in platz), (cap, rects, k, r)
