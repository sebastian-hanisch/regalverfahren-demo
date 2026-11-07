"""Erzeugt rgv_precomputed.json: das Messraster (vier Verteilungen der Rechteckmaße × Rechteckzahlen 12, 20, 40, 80 × 100 feste Instanzen).

    python generate_precomputed.py            # rechnet alles neu (bei 12 und 20 Rechtecken das Optimum mit CP-SAT und Zeitlimit; etwa 30 bis 60 Minuten)
    python generate_precomputed.py --retry-u  # rechnet nur die nicht entschiedenen Instanzen (Optimum -1) mit dem Zeitlimit der Konstanten noch einmal
    python generate_precomputed.py --keep-opt # behält die gespeicherten Optima und rechnet nur die Behälterzahlen neu (nach einer Änderung an Schlüsseln oder Regeln)
    python generate_precomputed.py --check    # rechnet das Schnelle nach (alle Zellen mit den gespeicherten Optima) und vergleicht mit der Datei

Das Optimum kommt aus `dev/opt.py` (CP-SAT, `NoOverlap2D`) mit Zeitlimit C.CPSAT_ZEITLIMIT; die Zahl der nicht entschiedenen Instanzen hängt von der Rechenzeit ab, die Datei hält
den Stand dieses Laufs fest (Optimum -1 = nicht entschieden). Ist die beste gefundene Packung so groß wie die Schranke, ist das Optimum die Schranke."""

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import rgv_algorithm as A
import rgv_constants as C
import rgv_evaluation as ev
from rgv_scenario import mess_seed, zufallsinstanz


def _cpsat(args):
    """Ein Optimum: (verteilung, n_index, j) -> Optimum oder -1."""
    from dev.opt import optimum_cpsat

    v, ni, j = args
    inst = zufallsinstanz(v, C.MESS_N[ni], mess_seed(v, ni, j))
    ober = min(A.anzahl(inst.rects, k, r, inst.cap) for k in ev.SCHLUESSEL_LISTE for r in ev.REGEL_LISTE)
    if ober == A.schranke(inst.rects, inst.cap):
        return ober
    return optimum_cpsat(inst.rects, inst.cap, ober, C.CPSAT_ZEITLIMIT)


def optima(v: int, ni: int, pool, alt: list | None = None, behalten: bool = False) -> list:
    """Optimum je Instanz der Zelle (-1 = nicht entschieden). Mit `alt` werden nur die Instanzen mit -1 neu gerechnet; mit `behalten` gar keine."""
    if behalten:
        return list(alt)
    offene = [j for j in range(C.INSTANZEN) if alt is None or alt[j] < 0]
    neu = dict(zip(offene, pool.map(_cpsat, [(v, ni, j) for j in offene])))
    return [neu.get(j, alt[j] if alt else -1) for j in range(C.INSTANZEN)]


def erzeugen(retry_u: bool = False, behalten: bool = False) -> dict:
    alt = ev.vorberechnet() if (retry_u or behalten) else None
    daten = {"instanzen": C.INSTANZEN, "cap": C.CAP, "cpsat_zeitlimit": C.CPSAT_ZEITLIMIT, "zellen": {}}
    arbeiter = max(1, min(3, (os.cpu_count() or 2) // 4))
    with ProcessPoolExecutor(arbeiter) as pool:
        for v in range(len(C.VERTEILUNGEN)):
            for ni, n in enumerate(C.MESS_N):
                t = time.perf_counter()
                schl = ev.zelle_schluessel(v, ni)
                if n in C.EXAKT_N:
                    opt = optima(v, ni, pool, alt["zellen"][schl]["opt"] if alt else None, behalten)
                    zelle = ev.messzelle(v, ni, opt)
                    zelle["opt"] = opt
                    info = f"entschieden {zelle['entschieden']} von {C.INSTANZEN}"
                else:
                    zelle = ev.messzelle(v, ni)
                    info = ""
                daten["zellen"][schl] = zelle
                print(f"{schl}: {time.perf_counter() - t:.0f} s  {info}", flush=True)
                if not behalten:
                    ev.PRECOMPUTED.with_suffix(".teil.json").write_text(json.dumps(daten, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return daten


def pruefen() -> int:
    gespeichert = ev.vorberechnet()
    schlecht = 0
    for v in range(len(C.VERTEILUNGEN)):
        for ni, n in enumerate(C.MESS_N):
            schl = ev.zelle_schluessel(v, ni)
            z = gespeichert["zellen"][schl]
            if n in C.EXAKT_N:
                frisch = ev.messzelle(v, ni, z["opt"])
                frisch["opt"] = z["opt"]
            else:
                frisch = ev.messzelle(v, ni)
            if frisch != z:
                schlecht += 1
                print("ABWEICHUNG", schl)
    print("gleich" if not schlecht else f"{schlecht} Abweichungen")
    return 1 if schlecht else 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(pruefen())
    daten = erzeugen("--retry-u" in sys.argv, "--keep-opt" in sys.argv)
    ev.PRECOMPUTED.write_text(json.dumps(daten, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    teil = ev.PRECOMPUTED.with_suffix(".teil.json")
    if teil.exists():
        teil.unlink()
    print("geschrieben:", ev.PRECOMPUTED.name)
