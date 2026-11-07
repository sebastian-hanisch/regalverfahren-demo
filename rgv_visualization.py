"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import rgv_constants as C

ABSTAND = 8     # Platz zwischen zwei Behältern in der Zeichnung


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_behaelter(rects, platz, cap):
    """Alle Behälter nebeneinander, jedes Rechteck an seiner Stelle; die Farbe zeigt das Regal (gleiche Höhe über dem Boden im selben Behälter), die Beschriftung die Teilenummer.

    Die Behälterrahmen sind rot gestrichelt. Das Achsenverhältnis ist 1 : 1, damit die Rechtecke maßstäblich sind."""
    bins = sorted({b for _, b, _, _ in platz})
    regale = {}                                       # (Behälter, y) -> laufende Nummer des Regals im Behälter
    for _, b, _, y in sorted(platz, key=lambda p: (p[1], p[3])):
        regale.setdefault((b, y), sum(1 for (bb, _) in regale if bb == b))
    fig = go.Figure()
    shapes = []
    xs, ys, texte, farben = [], [], [], []
    for b in bins:
        x0 = b * (cap + ABSTAND)
        shapes.append(dict(type="rect", x0=x0, y0=0, x1=x0 + cap, y1=cap, line=dict(color=C.COLOR_LINE, width=2, dash="dash"), fillcolor="rgba(0,0,0,0)"))
    for i, b, x, y in platz:
        w, h = rects[i]
        x0 = b * (cap + ABSTAND) + x
        farbe = C.REGAL_FARBEN[regale[(b, y)] % len(C.REGAL_FARBEN)]
        shapes.append(dict(type="rect", x0=x0, y0=y, x1=x0 + w, y1=y + h, line=dict(color="white", width=1.5), fillcolor=farbe, opacity=0.9))
        xs.append(x0 + w / 2)
        ys.append(y + h / 2)
        texte.append(f"Teil {i + 1}: {w} × {h}, Behälter {b + 1}, Regal {regale[(b, y)] + 1}")
        farben.append(farbe)
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="text", text=[str(t.split(":")[0].replace("Teil ", "")) for t in texte], textfont=dict(color="white", size=11),
                             hovertext=texte, hoverinfo="text", showlegend=False))
    fig.update_layout(shapes=shapes)
    breite = len(bins) * (cap + ABSTAND) - ABSTAND
    fig.update_xaxes(range=[-2, breite + 2], constrain="domain", showgrid=False, zeroline=False, tickmode="array", tickvals=[b * (cap + ABSTAND) + cap / 2 for b in bins], ticktext=[f"B{b + 1}" for b in bins])
    fig.update_yaxes(range=[-2, cap + 2], constrain="domain", showgrid=False, zeroline=False, scaleanchor="x", scaleratio=1, title_text="Höhe")
    return _base(fig, 340)


def build_messung(werte, titel):
    """Mittlere Behälter über der Vergleichsbasis: je Schlüssel drei Balken (die drei Regeln); werte = {Schlüssel: {Regel: Wert}}."""
    fig = go.Figure()
    schluessel = sorted(werte)
    namen = [C.SCHLUESSEL_KURZ[k] for k in schluessel]
    for r in sorted(werte[schluessel[0]]):
        zahlen = [werte[k][r] for k in schluessel]
        fig.add_trace(go.Bar(name=C.REGEL_NAME[r], x=namen, y=zahlen, marker_color=C.REGEL_FARBEN[r], text=[f"{w:.2f}" for w in zahlen], textposition="outside", cliponaxis=False,
                             hovertemplate="%{x}, " + C.REGEL_NAME[r] + ": %{y:.2f}<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text=titel)
    return _base(fig, 360)
