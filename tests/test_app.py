"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: lädt app.py mit den Standardeinstellungen, klickt jeden Button, stellt jede Auswahl
auf jeden ihrer Werte und das Zahlenfeld an seine Grenzen und prüft, dass kein Python-Fehler auftritt (insbesondere `StreamlitDuplicateElementId`
bei mehreren Diagrammen ohne key= und `StreamlitAPIException` bei Auswahlen mit ungültigem Wert)."""

import os

from streamlit.testing.v1 import AppTest

import rgv_constants as C

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_selectbox_value_does_not_raise():
    keys = [s.key for s in _fresh_app().selectbox]
    assert {"quelle_select", "n_select", "schluessel_select", "regel_select", "exp_verteilung", "exp_n"} <= set(keys)
    werte = {"quelle_select": list(C.QUELLEN), "n_select": list(range(len(C.N_WERTE))), "schluessel_select": list(C.SCHLUESSEL), "regel_select": list(C.REGELN),
             "exp_verteilung": list(range(len(C.VERTEILUNGEN))), "exp_n": list(range(len(C.MESS_N)))}
    for key in keys:
        for wert in werte[key]:
            at = _fresh_app()
            at.selectbox(key=key).set_value(wert).run(timeout=TIMEOUT)
            assert not at.exception, (key, wert, [str(e) for e in at.exception])


def test_seed_at_its_min_and_max_does_not_raise():
    for quelle in (0, 5):
        for wert in (0, C.SEED_MAX):
            at = _fresh_app()
            at.selectbox(key="quelle_select").set_value(quelle).run(timeout=TIMEOUT)
            at.number_input(key="seed_input").set_value(wert).run(timeout=TIMEOUT)
            assert not at.exception, (quelle, wert, [str(e) for e in at.exception])


def test_wuerfeln_wechselt_vom_beispiel_zu_einer_zufallsinstanz():
    at = _fresh_app()
    assert at.selectbox(key="quelle_select").value == 0
    at.button[[b.label for b in at.button].index("🎲 Neue Zufallsinstanz würfeln")].click().run(timeout=TIMEOUT)
    assert at.selectbox(key="quelle_select").value == 2 and not at.exception
    at.selectbox(key="quelle_select").set_value(5).run(timeout=TIMEOUT)
    seed_vorher = at.number_input(key="seed_input").value
    at.button[[b.label for b in at.button].index("🎲 Neue Zufallsinstanz würfeln")].click().run(timeout=TIMEOUT)
    assert at.selectbox(key="quelle_select").value == 5 and at.number_input(key="seed_input").value != seed_vorher


def test_standardansicht_zeigt_das_erwartete_verdikt():
    at = _fresh_app()
    infos = [i.value for i in at.info]
    assert any("In der Lieferreihenfolge mit Next Fit brauchen die Rechtecke **6** Behälter." in i and "Das Optimum ist **3**: 3 zu viel (die Schranke ist 3)." in i for i in infos)    # Beispiel 1, Lieferung, Next Fit
    assert any("um bis zu **2**; zwischen den vier Schlüsseln bei gleicher Regel um bis zu **2**. Beide wirken hier gleich stark." in i for i in infos)


def test_expander_stehen_unter_ihren_namen():
    labels = [e.label for e in _fresh_app().expander]
    assert "📐 Mathematische Formulierung" in labels and "⚠️ Annahmen, Grenzen und bekannte Probleme" in labels
