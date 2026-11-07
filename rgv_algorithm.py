"""Kern der Demo (nur Standardbibliothek): Sortierschlüssel, Regalverfahren, Schranken und der unabhängige Prüfer.

Ein Behälter ist `cap` mal `cap`. Ein Regal ist eine waagerechte Zeile; ihre Höhe ist die Höhe des ersten Rechtecks darin. Ein Rechteck passt auf ein Regal, wenn es nicht höher ist
als das Regal und die belegte Breite plus seine Breite höchstens `cap` ergibt. Packungen sind Listen von Behältern (je Behälter die Teilenummern, Index in der Lieferreihenfolge)
und Platzierungen (Teil, Behälter, x, y) mit der linken unteren Ecke."""


def schluessel_wert(rects, schluessel: int):
    """Sortierzahlen der Rechtecke (größer = früher); `None` bei der Lieferreihenfolge. 1 Höhe, 2 Fläche, 3 Breite."""
    if schluessel == 0:
        return None
    if schluessel == 1:
        return [h for _, h in rects]
    if schluessel == 2:
        return [w * h for w, h in rects]
    if schluessel == 3:
        return [w for w, _ in rects]
    raise ValueError(f"Schlüssel {schluessel!r} unbekannt")


def reihenfolge(rects, schluessel: int) -> list:
    """Teilenummern in der Reihenfolge, in der gepackt wird: absteigend nach der Sortierzahl; Gleichstände bleiben in der Lieferreihenfolge."""
    z = schluessel_wert(rects, schluessel)
    if z is None:
        return list(range(len(rects)))
    return sorted(range(len(rects)), key=lambda i: (-z[i], i))


def pack(rects, order, cap: int, regel: int):
    """Rechtecke in der Reihenfolge `order` auf Regale setzen. Regel 0 (Next): nur das letzte Regal des letzten Behälters; 1 (First): das erste passende Regal in der Reihenfolge der Behälter
    und Regale; 2 (Best): unter den passenden Regalen das mit der kleinsten Restbreite nach dem Einsetzen (Gleichstand: das frühere). Passt es auf kein Regal, wird ein neues Regal geöffnet:
    bei Next oberhalb des letzten Regals im letzten Behälter, bei First und Best im ersten Behälter mit genug Resthöhe; sonst ein neuer Behälter.
    Gibt (bins, platz) zurück: bins[b] = Teilenummern des Behälters, platz = Liste (Teil, Behälter, x, y)."""
    if regel not in (0, 1, 2):
        raise ValueError(f"Regel {regel!r} unbekannt")
    if sorted(order) != list(range(len(rects))):
        raise ValueError("die Reihenfolge muss jedes Rechteck genau einmal enthalten")
    for t in rects:
        if len(t) != 2 or any(x <= 0 or x > cap for x in t):
            raise ValueError(f"Rechteck {t!r} ungültig (zwei Maße, je 1 bis {cap})")
    regale = []                        # je Behälter: Liste von Regalen [y, hoehe, belegte_breite]
    bins = []
    platz = []
    for i in order:
        w, h = rects[i]
        if regel == 0:
            kandidaten = [(len(regale) - 1, len(regale[-1]) - 1)] if regale else []
        else:
            kandidaten = [(b, s) for b in range(len(regale)) for s in range(len(regale[b]))]
        wahl, beste = None, None
        for b, s in kandidaten:
            sh = regale[b][s]
            if h <= sh[1] and sh[2] + w <= cap:
                if regel != 2:
                    wahl = (b, s)
                    break
                rest = cap - sh[2] - w
                if beste is None or rest < beste:
                    beste, wahl = rest, (b, s)
        if wahl is not None:
            b, s = wahl
            sh = regale[b][s]
            platz.append((i, b, sh[2], sh[0]))
            bins[b].append(i)
            sh[2] += w
            continue
        orte = [len(regale) - 1] if (regel == 0 and regale) else list(range(len(regale)))
        gesetzt = False
        for b in orte:
            oben = regale[b][-1][0] + regale[b][-1][1]
            if oben + h <= cap:
                regale[b].append([oben, h, w])
                bins[b].append(i)
                platz.append((i, b, 0, oben))
                gesetzt = True
                break
        if not gesetzt:
            regale.append([[0, h, w]])
            bins.append([i])
            platz.append((i, len(regale) - 1, 0, 0))
    return bins, platz


def anzahl(rects, schluessel: int, regel: int, cap: int) -> int:
    return len(pack(rects, reihenfolge(rects, schluessel), cap, regel)[0])


def packung_pruefen(rects, platz, cap: int) -> bool:
    """Unabhängiger Prüfer: jedes Rechteck genau einmal, ganz im Behälter, keine zwei Rechtecke eines Behälters überlappen."""
    if sorted(p[0] for p in platz) != list(range(len(rects))):
        return False
    je = {}
    for i, b, x, y in platz:
        w, h = rects[i]
        if x < 0 or y < 0 or x + w > cap or y + h > cap:
            return False
        je.setdefault(b, []).append((x, y, x + w, y + h))
    for lst in je.values():
        for a in range(len(lst)):
            for c in range(a + 1, len(lst)):
                p, q = lst[a], lst[c]
                if p[0] < q[2] and q[0] < p[2] and p[1] < q[3] and q[1] < p[3]:
                    return False
    return True


def schranken(rects, cap: int):
    """(Flächenschranke, Zahl der großen Rechtecke, Schranke): die Fläche aller Rechtecke durch die Behälterfläche aufgerundet; die Zahl der Rechtecke, die in beiden Maßen
    über die Hälfte reichen (zwei solche überlappen in jedem Behälter über dem Mittelpunkt, jedes braucht also einen eigenen Behälter); das Größere von beiden."""
    flaeche = -(-sum(w * h for w, h in rects) // (cap * cap))
    gross = sum(1 for w, h in rects if 2 * w > cap and 2 * h > cap)
    return flaeche, gross, max(flaeche, gross)


def schranke(rects, cap: int) -> int:
    return schranken(rects, cap)[2]
