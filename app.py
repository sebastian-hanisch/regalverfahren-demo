"""Packen: von Zeilen zu Regalen, NFDH gegen FFDH - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 7 der Reihe „Packen: Reihenfolge und Platzierungsregel“. Rechtecke ohne Überlappung in Behälter: Regale als einfachster Dekodierer. Zählt die Regel (nur das letzte Regal
oder das erste passende) oder der Sortierschlüssel (Höhe oder Fläche) mehr? Das Messraster (vorberechnet in rgv_precomputed.json) zeigt die Antwort an je 100 Zufallsinstanzen.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import rgv_constants as C
from rgv_evaluation import (
    REGEL_LISTE,
    SCHLUESSEL_LISTE,
    Settings,
    analyse,
    optimum_zeilen,
    referenz,
    verdict_aktuell,
    verdict_messung,
    verdict_optimum,
    verdict_regeln,
    verdict_tabelle,
    zeile,
)
from rgv_layout import dunkles_design, kopf_css
from rgv_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from rgv_visualization import build_behaelter, build_messung

st.set_page_config(page_title="Packen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in rgv_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧩 Von Zeilen zu Regalen: NFDH gegen FFDH")
st.markdown(
    """
Rechtecke sollen ohne Überlappung in möglichst wenige Behälter. Der einfachste Weg ist ein **Regal**: eine waagerechte Zeile, deren Höhe das erste Rechteck darin festlegt. Zwei Fragen bleiben: **In welches Regal kommt das nächste Rechteck**, und **in welcher Reihenfolge nimmt man die Rechtecke**? Die Demo zeigt an zwölf Rechtecken und an einem Messraster aus je 100 Zufallsinstanzen, wie viel an der Regel hängt und wie viel am Sortierschlüssel, und wie weit ein Regalplan vom Optimum entfernt ist.

Weiter unten: der Abschnitt **🔬 Experimente**, **🚧 Wo die Annahmen enden**, der Expander **⚠️ Annahmen, Grenzen und bekannte Probleme** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert Packen mit Regalen", expanded=True):
    st.markdown(
        """
1. **Schlüssel wählen:** Die Rechtecke werden in der Lieferreihenfolge genommen oder absteigend nach Höhe, Fläche oder Breite sortiert.
2. **Regel anwenden, Rechteck für Rechteck:** Ein Rechteck passt auf ein Regal, wenn es nicht höher ist als das Regal und in der Breite noch Platz hat. *Next Fit* (NFDH) prüft nur das zuletzt geöffnete Regal, *First Fit* (FFDH) das erste Regal, auf das es passt, *Best Fit* (BFDH) unter den passenden das mit der kleinsten Restbreite danach. Passt es auf kein Regal, wird oberhalb ein neues geöffnet, und wenn dort die Höhe nicht reicht, ein neuer Behälter.
3. **Wo die Wirkung sitzt:** Das Kästchen *Kernfrage* unten zählt, was die Behälterzahl mehr verändert, die Regel oder der Schlüssel.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Rechtecke**")
    quelle = st.selectbox("Instanz", list(C.QUELLEN), format_func=C.QUELLEN.get, key="quelle_select",
                          help="Die beiden Beispiele haben je zwölf feste Rechtecke. Die anderen vier sind Zufallsinstanzen mit verschiedener Verteilung der Maße.")
    n_index = st.selectbox("Zahl der Rechtecke (nur Zufallsinstanzen)", list(range(len(C.N_WERTE))), format_func=lambda i: str(C.N_WERTE[i]), key="n_select",
                           help="Gilt nur für Zufallsinstanzen.")
    seed = st.number_input("Startzahl der Zufallsinstanz", *bounds("seed_input"), key="seed_input", step=1,
                           help="Wirkt nur bei den Zufallsinstanzen.")
    st.button("🎲 Neue Zufallsinstanz würfeln", width="stretch", on_click=randomize_seed)
    st.markdown("**Packen**")
    schluessel = st.selectbox("Sortierschlüssel", list(C.SCHLUESSEL), format_func=C.SCHLUESSEL.get, key="schluessel_select",
                              help="Wonach die Rechtecke sortiert werden, absteigend. „Lieferreihenfolge“ sortiert nicht.")
    regel = st.selectbox("Regel: in welches Regal?", list(C.REGELN), format_func=C.REGELN.get, key="regel_select",
                         help="Wohin das nächste Rechteck kommt.")

sync_query_params({"quelle_select": int(quelle), "n_select": int(n_index), "seed_input": int(seed), "schluessel_select": int(schluessel), "regel_select": int(regel)})

settings = Settings(int(quelle), int(n_index), int(seed), int(schluessel), int(regel))
a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3 = st.columns(3)
# Delta immer als „mein Wert minus Referenz“; die Farbe regelt delta_color="inverse" (Vorzeichen-Falle, DEMO-PLAYBOOK §2).
if a.opt is not None:
    m1.metric("Behälter (gewählte Kombination)", a.count, delta=a.count - a.opt, delta_color="inverse", help="Delta: gewählte Behälterzahl minus Optimum.")
    m2.metric("Optimum (exakt, über alle Packungen)", a.opt, delta="Referenz", delta_color="off")
else:
    m1.metric("Behälter (gewählte Kombination)", a.count)
    m2.metric("Optimum", "nicht berechnet", delta="nur für die Beispiele", delta_color="off")
m3.metric("Untere Schranke", a.schranke, delta="Fläche oder große Rechtecke", delta_color="off")
flaeche = sum(w * h for w, h in a.inst.rects)
st.caption(f"{a.inst.n} Rechtecke, Gesamtfläche {flaeche} von {a.inst.cap * a.inst.cap} je Behälter. In Lieferreihenfolge brauchen sie mit der gewählten Regel {a.liefer} Behälter.")
st.markdown("**So liegen die Rechtecke:** jeder gestrichelte Rahmen ist ein Behälter, die Farbe zeigt das Regal, die Zahl die Nummer des Rechtecks in der Lieferreihenfolge.")
st.plotly_chart(build_behaelter(a.inst.rects, a.platz, a.inst.cap), width="stretch", key="main_chart")
st.caption("Die Rechtecke sind maßstäblich. Ein Regal ist so hoch wie sein erstes Rechteck; jedes weitere darin ist höchstens so hoch.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Was verändert die Behälterzahl mehr, die Regel oder der Sortierschlüssel?")
kind, text = verdict_aktuell(a)
getattr(st, kind)(text)

zeilen = ["| Schlüssel \\ Regel | " + " | ".join(C.REGEL_KURZ[r] for r in REGEL_LISTE) + " |", "|---|" + "---|" * len(REGEL_LISTE)]
for k in SCHLUESSEL_LISTE:
    zellen = []
    for r in REGEL_LISTE:
        wert = str(a.tabelle[k][r])
        zellen.append(f"**{wert}**" if (k, r) == (settings.schluessel, settings.regel) else wert)
    zeilen.append(f"| {C.SCHLUESSEL_KURZ[k]} | " + " | ".join(zellen) + " |")
st.markdown("Behälterzahl für alle 12 Kombinationen (die gewählte ist fett):\n\n" + "\n".join(zeilen))
kind, text = verdict_tabelle(a)
getattr(st, kind)(text)

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experimente: Gilt das für viele Instanzen?")
st.caption(
    f"Gemessen an je {C.INSTANZEN} festen Zufallsinstanzen pro Zelle, Behälter {C.CAP} mal {C.CAP}, ganzzahlige Maße der Rechtecke ohne Drehung. "
    "Die Zahlen sind vorberechnet (`generate_precomputed.py`)."
)
e1, e2 = st.columns(2)
verteilung = e1.selectbox("Verteilung der Rechtecke", list(range(len(C.VERTEILUNGEN))), index=0, format_func=lambda i: C.VERTEILUNGEN[i][1], key="exp_verteilung")
ni = e2.selectbox("Zahl der Rechtecke n", list(range(len(C.MESS_N))), index=3, format_func=lambda i: str(C.MESS_N[i]), key="exp_n")
z = zeile(int(verteilung), int(ni))

st.markdown("### Experiment 1: Regel gegen Schlüssel")
basis, mittel = referenz(z)
st.plotly_chart(build_messung(mittel, f"Behälter über {basis} (Mittel)"), width="stretch", key="exp_chart")
tab = ["| Schlüssel | " + " | ".join(C.REGEL_KURZ[r] for r in REGEL_LISTE) + " |", "|---|" + "---|" * len(REGEL_LISTE)]
for k in SCHLUESSEL_LISTE:
    tab.append(f"| {C.SCHLUESSEL_KURZ[k]} | " + " | ".join(f"{mittel[k][r]:.2f}" for r in REGEL_LISTE) + " |")
st.markdown("\n".join(tab))
st.caption(
    f"Mittlere Behälter über {basis}: Mittel über die Instanzen der Zelle" + (" (nur die entschiedenen)" if z["exakt"] else "") + ". Next, First und Best sind die drei Regeln. "
    f"First Fit braucht weniger Behälter als Next Fit bei Höhe in {z['first_besser'][1]} von {z['instanzen']} Instanzen und mehr in {z['first_schlechter'][1]}."
)
kind, text = verdict_messung(z)
getattr(st, kind)(text)
kind, text = verdict_regeln(z)
getattr(st, kind)(text)

st.markdown("### Experiment 2: Wie nah am Optimum?")
oz = optimum_zeilen()
tab2 = ["| Rechtecke | Treffer | Abstand | Lücke |", "|---|---|---|---|"]
for r in oz:
    treffer = "-" if r["treffer"] is None else f"{r['treffer']:.0f} %"
    abstand = "-" if r["abstand"] is None else f"{r['abstand']:.2f}"
    ohne = "-" if r["opt_minus_schranke"] is None else f"{r['opt_minus_schranke']:.2f}"
    offen = f", {r['offen']} offen" if r["offen"] else ""
    tab2.append(f"| {C.VERTEILUNG_KURZ[r['verteilung']]} {r['n']}{offen} | {treffer} | {abstand} | {ohne} |")
st.markdown("\n".join(tab2))
st.caption(
    "Treffer: Anteil der entschiedenen Instanzen, in denen First Fit mit dem Schlüssel Höhe genau das Optimum braucht. Abstand: mittlere Behälter über dem Optimum für diese Kombination. "
    "Lücke: Optimum minus Schranke, Mittel über die entschiedenen Instanzen. „offen“ hinter dem Namen: Zahl der nicht entschiedenen Instanzen. Das Optimum gilt über alle Packungen, nicht nur Regalpläne. "
    "Bei 20 Rechtecken entscheidet CP-SAT mit " + f"{C.CPSAT_ZEITLIMIT:.0f}" + " Sekunden Zeitlimit; die nicht entschiedenen Instanzen fehlen im Mittel, und die Zahl hängt von der Rechenzeit ab."
)
kind, text = verdict_optimum(oz)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist |
|---|---|
| **Keine Drehung** | Dürfen die Rechtecke gedreht werden, ändert sich die Aufgabe, und der Schlüssel „Höhe“ ist nicht mehr eindeutig. Die Demo misst das nicht. |
| **Nur Regalpläne** | Ohne Regale (freie Platzierung, etwa Skyline oder MaxRects) ist mehr möglich; das Optimum der Demo gilt über alle Packungen und liegt deshalb oft unter dem besten Regalplan. |
| **Die Maße sind zufällig verteilt** | Nur vier Verteilungen mit festen Bereichen sind gemessen. Andere Verteilungen können anders ausfallen. |
| **Die Schranke ist scharf** | In 2D ist sie locker: Das Optimum liegt schon bei zwölf mittleren Rechtecken oft darüber (Experiment 2); bei 40 und 80 Rechtecken fehlt das Optimum ganz. |
| **Alle Rechtecke sind vor dem Packen bekannt** | Wer jedes Rechteck sofort einsortieren muss, kann nicht sortieren. Das ist Online-Packen. Mehr dazu: [Online](https://sebastianhanisch.net/konzepte-online-algorithmen.html). |
"""
)

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(C.ASSUMPTIONS_MARKDOWN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** *Gegeben:* Rechtecke mit ganzzahliger Breite und Höhe und Behälter der Größe $C \times C$. *Gesucht:* eine überlappungsfreie Platzierung aller Rechtecke in möglichst wenigen Behältern, ohne Drehung.

| Symbol | Bedeutung |
|---|---|
| $n$ | Zahl der Rechtecke |
| $w_i$, $h_i$ | Breite und Höhe von Rechteck $i$, $1 \le w_i, h_i \le C$ |
| $C$ | Seitenlänge eines Behälters |
| $\mathrm{OPT}$ | kleinste mögliche Zahl von Behältern über alle Platzierungen |
| $L$ | untere Schranke für $\mathrm{OPT}$ |

**Schlüssel und Regel.** Ein Schlüssel ordnet jedem Rechteck eine Zahl $s_i$ zu: $h_i$, $w_i h_i$ oder $w_i$; die Rechtecke werden nach fallendem $s_i$ genommen, Gleichstände in der Lieferreihenfolge. Ein *Regal* ist eine Zeile der Höhe $h$ des ersten Rechtecks darin; Rechtecke kommen von links nach rechts darauf, solange ihre Höhe höchstens $h$ ist und die belegte Breite plus $w_i$ höchstens $C$ ergibt. *Next Fit* prüft nur das zuletzt geöffnete Regal, *First Fit* das erste passende in der Reihenfolge der Behälter und Regale, *Best Fit* unter den passenden das mit der kleinsten Restbreite danach. Passt das Rechteck auf kein Regal, öffnet es ein neues Regal direkt über dem letzten: bei Next Fit im letzten Behälter, bei First und Best Fit im ersten Behälter mit genug Resthöhe; sonst einen neuen Behälter. Sortiert nach der Höhe heißen die Verfahren NFDH, FFDH und BFDH.

**Schranken.** $L_{\mathrm{Fl}} = \left\lceil \tfrac{1}{C^2} \sum_i w_i h_i \right\rceil \le \mathrm{OPT}$. Rechtecke mit $w_i > C/2$ und $h_i > C/2$ („große“) überlappen paarweise in jedem Behälter: Jedes liegt mit $x \le C - w_i < C/2$ und $x + w_i > C/2$ über der Stelle $x = C/2$ und ebenso in der Höhe, enthält also den Mittelpunkt des Behälters. Daher braucht jedes große Rechteck einen eigenen Behälter, $L_{\mathrm{gr}} = |\{ i : w_i > C/2, h_i > C/2 \}| \le \mathrm{OPT}$, und $L = \max(L_{\mathrm{Fl}}, L_{\mathrm{gr}})$.

**Exaktes Optimum** (Generator, nicht die App). Ein Zuordnungsmodell mit Bedingungen „keine Überlappung“ für jeden Behälter (CP-SAT, `NoOverlap2D`), minimiert die Zahl benutzter Behälter; das Optimum gilt über alle Packungen, nicht nur Regalpläne. Bei den beiden Beispielen steht es als Konstante und wird in den Tests nachgerechnet.

**Literatur** (Zusammenfassungen aus Suchtreffern, Originale nicht gelesen). Coffman, Garey, Johnson und Tarjan (SIAM Journal on Computing 9, 1980) analysieren Regalverfahren (NFDH, FFDH und weitere) für das Streifenpacken, bei dem die Höhe eines Streifens unendlicher Höhe minimiert wird; das ist nicht dasselbe wie die Behälter dieser Demo. Die Demo übernimmt daraus keine Zahl und keine Gütegarantie.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
