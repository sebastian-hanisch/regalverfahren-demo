"""Setzt die README zusammen: Tabellen und Text der Annahmen kommen aus denselben Funktionen wie in der App (nur zum Schreiben der README, nicht Teil der Laufzeit).

    python dev/readme_bauen.py [ANZAHL_TESTS]
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import rgv_constants as C  # noqa: E402
import rgv_evaluation as ev  # noqa: E402


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def tabellen():
    """(Tabelle A, Tabelle B, Tabelle C): A = Behälter über der Vergleichsbasis je Zelle und Kombination, B = Anteil Optimum getroffen, C = Optimum gegen Schranke."""
    kopf = " | ".join(f"{C.SCHLUESSEL_KURZ[k]} {C.REGEL_KURZ[r]}" for k in range(4) for r in range(3))
    ta = ["| Verteilung | n | Basis | " + kopf + " |", "|---|---|---|" + "---|" * 12]
    for v in range(len(C.VERTEILUNGEN)):
        for ni, n in enumerate(C.MESS_N):
            z = ev.zeile(v, ni)
            b, m = ev.referenz(z)
            ta.append(f"| {C.VERTEILUNG_KURZ[v]} | {n} | {'Optimum' if b == 'dem Optimum' else 'Schranke'} | " + " | ".join(de(m[k][r]) for k in range(4) for r in range(3)) + " |")
    tb = ["| Verteilung | n | Höhe First | Höhe Next | Fläche First | Lieferung First | Treffer Lieferung Next |", "|---|---|---|---|---|---|---|"]
    for v in range(len(C.VERTEILUNGEN)):
        for ni, n in enumerate(C.MESS_N):
            if n in C.EXAKT_N:
                z = ev.zeile(v, ni)
                t = z["anteil_opt"]
                tb.append(f"| {C.VERTEILUNG_KURZ[v]} | {n} | {t[1][1]:.0f} % | {t[1][0]:.0f} % | {t[2][1]:.0f} % | {t[0][1]:.0f} % | {t[0][0]:.0f} % |")
    tc = ["| Verteilung | n | Optimum minus Schranke (Mittel) | Optimum über der Schranke | nicht entschieden |", "|---|---|---|---|---|"]
    for r in ev.optimum_zeilen():
        tc.append(f"| {C.VERTEILUNG_KURZ[r['verteilung']]} | {r['n']} | {de(r['opt_minus_schranke'])} | {r['ueber']} von {r['entschieden']} | {r['offen']} |")
    return "\n".join(ta), "\n".join(tb), "\n".join(tc)


if __name__ == "__main__":
    vorlage = (ROOT / "dev" / "readme_vorlage.md").read_text(encoding="utf-8")
    ta, tb, tc = tabellen()
    anzahl = sys.argv[1] if len(sys.argv) > 1 else "TESTZAHL"
    text = (vorlage.replace("{{TABELLE_A}}", ta).replace("{{TABELLE_B}}", tb).replace("{{TABELLE_C}}", tc)
            .replace("{{ANNAHMEN}}", C.ASSUMPTIONS_MARKDOWN).replace("{{CPSAT_ZEITLIMIT}}", f"{C.CPSAT_ZEITLIMIT:.0f}").replace("{{TESTS}}", anzahl))
    (ROOT / "README.md").write_text(text, encoding="utf-8")
    print("README.md geschrieben")
