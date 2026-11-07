"""Kennzahlen, Verdikt-Logik und das Messraster (vorberechnet in rgv_precomputed.json, erzeugt von generate_precomputed.py)."""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import rgv_algorithm as A
import rgv_constants as C
from rgv_scenario import Instance, mess_seed, quelle_instanz, zufallsinstanz

PRECOMPUTED = Path(__file__).resolve().parent / "rgv_precomputed.json"
SCHLUESSEL_LISTE = tuple(sorted(C.SCHLUESSEL))
REGEL_LISTE = tuple(sorted(C.REGELN))


@dataclass(frozen=True)
class Settings:
    quelle: int = 0
    n_index: int = 0
    seed: int = C.DEFAULT_SEED
    schluessel: int = 0
    regel: int = 0


@dataclass(frozen=True)
class Analysis:
    inst: Instance
    order: tuple          # Teilenummern in der Reihenfolge, in der gepackt wird
    bins: tuple           # Behälter als Tupel von Teilenummern
    platz: tuple          # Platzierungen (Teil, Behälter, x, y)
    count: int
    liefer: int           # Behälterzahl in Lieferreihenfolge mit derselben Regel
    schranke: int
    opt: object           # Optimum (int) bei den Handbeispielen, sonst None
    tabelle: tuple        # tabelle[schluessel][regel] = Behälterzahl, 4 x 3
    settings: Settings


def tabelle(inst: Instance) -> tuple:
    """Behälterzahl für jede Kombination aus Schlüssel (Zeile) und Regel (Spalte)."""
    return tuple(tuple(A.anzahl(inst.rects, k, r, inst.cap) for r in REGEL_LISTE) for k in SCHLUESSEL_LISTE)


def analyse(s: Settings) -> Analysis:
    inst = quelle_instanz(s.quelle, C.N_WERTE[s.n_index], s.seed)
    order = A.reihenfolge(inst.rects, s.schluessel)
    bins, platz = A.pack(inst.rects, order, inst.cap, s.regel)
    assert A.packung_pruefen(inst.rects, platz, inst.cap)
    tab = tabelle(inst)
    return Analysis(inst, tuple(order), tuple(tuple(b) for b in bins), tuple(platz), len(bins), tab[0][s.regel], A.schranke(inst.rects, inst.cap),
                    C.BEISPIEL_OPTIMUM.get(s.quelle), tab, s)


# ------------------------------------------------------------------------------------------------------------------------------------------
# Verdikte (reine Funktionen: (Art, Text))


def verdict_aktuell(a: Analysis) -> tuple[str, str]:
    """Verdikt zur gewählten Kombination: Behälterzahl gegen die Lieferreihenfolge (gleiche Regel) und gegen das Optimum, wo es bekannt ist."""
    s = a.settings
    schluessel = C.SCHLUESSEL_MIT[s.schluessel]
    regel = C.REGEL_NAME[s.regel]
    if a.opt is None:
        opt_teil = f" Das Optimum ist für diese Instanz nicht berechnet; die Schranke ist {a.schranke}."
    elif a.count == a.opt:
        opt_teil = f" Das ist das Optimum (die Schranke allein ergäbe {a.schranke})."
    else:
        opt_teil = f" Das Optimum ist **{a.opt}**: {a.count - a.opt} zu viel (die Schranke ist {a.schranke})."
    if s.schluessel == 0:
        return "info", f"In der Lieferreihenfolge mit {regel} brauchen die Rechtecke **{a.count}** Behälter." + opt_teil
    kopf = f"Nach {schluessel} sortiert und mit {regel} gesetzt brauchen die Rechtecke **{a.count}** Behälter, in Lieferreihenfolge {a.liefer}."
    if a.count > a.liefer:
        return "warning", kopf + f" Sortieren schadet hier um {a.count - a.liefer}." + opt_teil
    if a.count < a.liefer:
        return "success", kopf + f" Sortieren spart hier {a.liefer - a.count}." + opt_teil
    return "info", kopf + " Sortieren ändert hier nichts." + opt_teil


def spannen(t: tuple) -> tuple[int, int]:
    """(regel, schluessel) der 4 x 3 Tabelle: größter Unterschied zwischen den Regeln innerhalb einer Zeile; größter Unterschied zwischen den Schlüsseln innerhalb einer Spalte."""
    regel = max(max(z) - min(z) for z in t)
    schluessel = max(max(t[k][r] for k in range(len(t))) - min(t[k][r] for k in range(len(t))) for r in range(len(t[0])))
    return regel, schluessel


def verdict_tabelle(a: Analysis) -> tuple[str, str]:
    """Kernfrage: Was verändert die Behälterzahl mehr, die Regel oder der Schlüssel? Gezählt über die ganze 4 x 3 Tabelle dieser Instanz."""
    regel, schluessel = spannen(a.tabelle)
    teil = (f"Zwischen den drei Regeln unterscheidet sich die Behälterzahl bei gleichem Schlüssel um bis zu **{regel}**; "
            f"zwischen den vier Schlüsseln bei gleicher Regel um bis zu **{schluessel}**.")
    if regel > schluessel:
        return "success", teil + " Hier zählt die Regel mehr als der Schlüssel."
    if regel == schluessel:
        return "info", teil + " Beide wirken hier gleich stark."
    return "warning", teil + " Hier zählt der Schlüssel mehr als die Regel."


# ------------------------------------------------------------------------------------------------------------------------------------------
# Messraster


def optima(verteilung: int, n_index: int, rechner) -> list:
    """Optimum jeder Instanz einer Zelle mit dem Rechner `rechner(rects, cap, obergrenze)` (-1 = nicht entschieden)."""
    n = C.MESS_N[n_index]
    out = []
    for j in range(C.INSTANZEN):
        inst = zufallsinstanz(verteilung, n, mess_seed(verteilung, n_index, j))
        ober = min(A.anzahl(inst.rects, k, r, inst.cap) for k in SCHLUESSEL_LISTE for r in REGEL_LISTE)
        out.append(rechner(inst.rects, inst.cap, ober))
    return out


def messzelle(verteilung: int, n_index: int, opt: list | None = None) -> dict:
    """Rechnet eine Zelle des Messrasters frisch: Summen (ganze Zahlen, damit der Vergleich exakt ist) über INSTANZEN feste Instanzen.

    ueber_schranke[k][r] = Summe über alle Instanzen von (Behälter mit Schlüssel k und Regel r minus Schranke). first_besser[k] und first_schlechter[k]: Zahl der Instanzen, in denen First Fit
    mit Schlüssel k weniger bzw. mehr Behälter braucht als Next Fit. gross_ueber_flaeche: Zahl der Instanzen, in denen die Schranke „große Rechtecke“ über der Flächenschranke liegt.
    Mit `opt` (Optimum je Instanz, -1 = nicht entschieden) zusätzlich, nur über die entschiedenen Instanzen: ueber_opt[k][r], trifft_opt[k][r] (Zahl der Instanzen mit Behälter gleich Optimum),
    opt_minus_schranke (Summe), opt_ueber_schranke (Zahl der Instanzen mit Optimum über der Schranke) und entschieden."""
    n = C.MESS_N[n_index]
    ks = [str(k) for k in SCHLUESSEL_LISTE]
    rs = [str(r) for r in REGEL_LISTE]
    out = {"ueber_schranke": {k: dict.fromkeys(rs, 0) for k in ks}, "first_besser": dict.fromkeys(ks, 0), "first_schlechter": dict.fromkeys(ks, 0), "gross_ueber_flaeche": 0}
    if opt is not None:
        out.update({"entschieden": 0, "ueber_opt": {k: dict.fromkeys(rs, 0) for k in ks}, "trifft_opt": {k: dict.fromkeys(rs, 0) for k in ks}, "opt_minus_schranke": 0, "opt_ueber_schranke": 0})
    for j in range(C.INSTANZEN):
        inst = zufallsinstanz(verteilung, n, mess_seed(verteilung, n_index, j))
        flaeche, gross, s = A.schranken(inst.rects, inst.cap)
        t = tabelle(inst)
        out["gross_ueber_flaeche"] += gross > flaeche
        for k in SCHLUESSEL_LISTE:
            for r in REGEL_LISTE:
                out["ueber_schranke"][str(k)][str(r)] += t[k][r] - s
            out["first_besser"][str(k)] += t[k][1] < t[k][0]
            out["first_schlechter"][str(k)] += t[k][1] > t[k][0]
        if opt is not None and opt[j] >= 0:
            out["entschieden"] += 1
            out["opt_minus_schranke"] += opt[j] - s
            out["opt_ueber_schranke"] += opt[j] > s
            for k in SCHLUESSEL_LISTE:
                for r in REGEL_LISTE:
                    out["ueber_opt"][str(k)][str(r)] += t[k][r] - opt[j]
                    out["trifft_opt"][str(k)][str(r)] += t[k][r] == opt[j]
    return out


@lru_cache(maxsize=1)
def vorberechnet() -> dict:
    return json.loads(PRECOMPUTED.read_text(encoding="utf-8"))


def zelle_schluessel(verteilung: int, n_index: int) -> str:
    return f"{C.VERTEILUNGEN[verteilung][0]}|{C.MESS_N[n_index]}"


def zeile(verteilung: int, n_index: int, daten: dict | None = None) -> dict:
    """Mittelwerte und Anteile einer Zelle aus den vorberechneten Summen."""
    daten = daten or vorberechnet()
    z = daten["zellen"][zelle_schluessel(verteilung, n_index)]
    k = daten["instanzen"]
    ks = SCHLUESSEL_LISTE
    exakt = "entschieden" in z
    e = z.get("entschieden", 0)

    def tab(summen, nenner):
        return {s: {r: summen[str(s)][str(r)] / nenner for r in REGEL_LISTE} for s in ks}

    return {
        "verteilung": verteilung,
        "name": C.VERTEILUNG_LANG[verteilung],
        "n": C.MESS_N[n_index],
        "instanzen": k,
        "exakt": exakt,
        "entschieden": e,
        "offen": (k - e) if exakt else 0,
        "mittel_schranke": tab(z["ueber_schranke"], k),
        "mittel_opt": tab(z["ueber_opt"], e) if exakt and e else None,
        "anteil_opt": {s: {r: 100.0 * z["trifft_opt"][str(s)][str(r)] / e for r in REGEL_LISTE} for s in ks} if exakt and e else None,
        "opt_minus_schranke": z["opt_minus_schranke"] / e if exakt and e else None,
        "opt_ueber_schranke": z.get("opt_ueber_schranke", 0),
        "first_besser": {s: z["first_besser"][str(s)] for s in ks},
        "first_schlechter": {s: z["first_schlechter"][str(s)] for s in ks},
        "gross_ueber_flaeche": z["gross_ueber_flaeche"],
    }


def referenz(z: dict) -> tuple[str, dict]:
    """(Name der Vergleichsbasis, Mittel je Schlüssel und Regel): das Optimum, wo es für mindestens eine Instanz der Zelle bekannt ist, sonst die Schranke."""
    if z["exakt"] and z["entschieden"]:
        return "dem Optimum", z["mittel_opt"]
    return "der Schranke", z["mittel_schranke"]


def kombi_name(k: int, r: int) -> str:
    return f"{C.SCHLUESSEL_KURZ[k]} mit {C.REGEL_NAME[r]}"


def verdict_messung(z: dict) -> tuple[str, str]:
    """Verdikt zur gewählten Zelle: beste Kombination, Wirkung der Regel bei Höhensortierung und Wirkung des Schlüssels Fläche; auf zwei Stellen gerundet verglichen."""
    basis, m = referenz(z)
    g = {k: {r: round(m[k][r], 2) for r in REGEL_LISTE} for k in SCHLUESSEL_LISTE}
    beste = min(g[k][r] for k in SCHLUESSEL_LISTE for r in REGEL_LISTE)
    namen = [kombi_name(k, r) for k in SCHLUESSEL_LISTE for r in REGEL_LISTE if g[k][r] == beste]
    n_inst = z["entschieden"] if basis == "dem Optimum" else z["instanzen"]
    kopf = f"Für {C.VERTEILUNG_LANG[z['verteilung']]} mit n = {z['n']} liegt die beste Kombination, {' und '.join(namen)}, im Mittel {beste:.2f} Behälter über {basis} ({n_inst} Instanzen)."
    regel = f" Mit der Höhe als Schlüssel braucht Next Fit {g[1][0]:.2f}, First Fit {g[1][1]:.2f}; nach der Fläche statt nach der Höhe sortiert braucht First Fit {g[2][1]:.2f}."
    fuss = ""
    if basis == "dem Optimum" and z["offen"]:
        fuss += f" {z['offen']} von {z['instanzen']} Instanzen sind nicht entschieden und fehlen im Mittel."
    if basis == "der Schranke":
        fuss += " Bei dieser Rechteckzahl fehlt das Optimum und die Schranke ist locker: Lesen Sie nur die Unterschiede zwischen den Kombinationen, nicht den Abstand."
    if g[2][0] > g[0][0]:
        return "warning", kopf + regel + f" Next Fit nach der Fläche ({g[2][0]:.2f}) ist **schlechter als Next Fit ohne Sortieren** ({g[0][0]:.2f})." + fuss
    return "info", kopf + regel + fuss


def spannweiten(z: dict) -> tuple[float, float]:
    """(Regel, Schlüssel) in Behältern über der Vergleichsbasis, auf zwei Stellen gerundet: größter Unterschied zwischen den drei Regeln bei gleichem Schlüssel; größter Unterschied
    zwischen den vier Schlüsseln bei gleicher Regel."""
    _, m = referenz(z)
    g = {k: {r: round(m[k][r], 2) for r in REGEL_LISTE} for k in SCHLUESSEL_LISTE}
    regel = max(max(g[k].values()) - min(g[k].values()) for k in SCHLUESSEL_LISTE)
    schluessel = max(max(g[k][r] for k in SCHLUESSEL_LISTE) - min(g[k][r] for k in SCHLUESSEL_LISTE) for r in REGEL_LISTE)
    return regel, schluessel


def verdict_regeln(z: dict) -> tuple[str, str]:
    """Verdikt zu Experiment 1b: Spannweite zwischen den Regeln gegen Spannweite zwischen den Schlüsseln, auf zwei Stellen gerundet."""
    regel, schluessel = spannweiten(z)
    teil = (f"Für {C.VERTEILUNG_LANG[z['verteilung']]} mit n = {z['n']} unterscheiden sich die drei Regeln bei gleichem Schlüssel um bis zu **{regel:.2f}** Behälter, "
            f"die vier Schlüssel bei gleicher Regel um bis zu **{schluessel:.2f}**.")
    if regel > schluessel:
        return "success", teil + " Die Regel entscheidet hier mehr als der Schlüssel."
    if regel == schluessel:
        return "info", teil + " Beide wirken hier gleich stark."
    return "warning", teil + " Hier wirkt der Schlüssel stärker als die Regel."


def optimum_zeilen(daten: dict | None = None) -> list:
    """Experiment 2: für alle Zellen mit Optimum (n = 12 und 20, vier Verteilungen): Anteil der Instanzen, in denen First Fit mit Schlüssel Höhe das Optimum trifft, Abstand und Optimum
    gegen Schranke."""
    zeilen = []
    for v in range(len(C.VERTEILUNGEN)):
        for ni, n in enumerate(C.MESS_N):
            if n in C.EXAKT_N:
                z = zeile(v, ni, daten)
                zeilen.append({"verteilung": v, "n": n, "entschieden": z["entschieden"], "offen": z["offen"], "instanzen": z["instanzen"],
                               "treffer": None if z["anteil_opt"] is None else z["anteil_opt"][1][1],
                               "abstand": None if z["mittel_opt"] is None else z["mittel_opt"][1][1],
                               "opt_minus_schranke": z["opt_minus_schranke"], "ueber": z["opt_ueber_schranke"]})
    return zeilen


def verdict_optimum(zeilen: list) -> tuple[str, str]:
    """Verdikt zu Experiment 2: die Zeile mit dem größten mittleren Abstand zwischen Optimum und Schranke (auf zwei Stellen gerundet) und die mit dem kleinsten Anteil Treffer."""
    gueltig = [z for z in zeilen if z["opt_minus_schranke"] is not None and z["treffer"] is not None]
    if not gueltig:
        return "info", "Es gibt keine Zelle mit bekanntem Optimum."
    locker = max(gueltig, key=lambda z: (round(z["opt_minus_schranke"], 2), -z["n"]))
    schwach = min(gueltig, key=lambda z: (round(z["treffer"]), z["n"]))
    return "info", (f"Am lockersten ist die Schranke bei {C.VERTEILUNG_DAT[locker['verteilung']]} mit n = {locker['n']}: Das Optimum liegt im Mittel um **{locker['opt_minus_schranke']:.2f}** über ihr "
                    f"und in {locker['ueber']} von {locker['entschieden']} entschiedenen Instanzen darüber. First Fit mit der Höhe trifft das Optimum am seltensten bei {C.VERTEILUNG_DAT[schwach['verteilung']]} "
                    f"mit n = {schwach['n']}: in {schwach['treffer']:.0f} % der {schwach['entschieden']} entschiedenen Instanzen.")
