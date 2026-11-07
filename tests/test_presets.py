"""Presets: Vollständigkeit, gültige Werte, erstes Preset = Standardeinstellungen, jedes Preset liefert die versprochene Aussage."""

import rgv_algorithm as A
import rgv_constants as C
import rgv_evaluation as ev
import rgv_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_widget_bounds():
    for name, preset in C.PRESETS.items():
        for key, state_key in P.PRESET_KEYS.items():
            spec = P.SETTING_SPECS[state_key]
            assert spec.lo <= preset[key] <= spec.hi, (name, key)


def test_first_preset_equals_the_default_settings():
    assert ev.Settings(**next(iter(C.PRESETS.values()))) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_defaults_of_the_widgets_equal_the_default_settings():
    s = ev.Settings()
    assert [P.SETTING_SPECS[k].default for k in ("quelle_select", "n_select", "seed_input", "schluessel_select", "regel_select")] == [s.quelle, s.n_index, s.seed, s.schluessel, s.regel]


def test_presets_behaupten_nur_was_stimmt():
    """Die Hilfetexte der Presets nennen Behälterzahlen und Vergleiche; sie müssen mit der Rechnung übereinstimmen."""
    eins = ev.analyse(ev.Settings(**C.PRESETS["Beispiel 1, Lieferung, nur das letzte Regal"]))
    assert eins.count == 6 and "Das sind sechs Behälter." in C.PRESET_HELP["Beispiel 1, Lieferung, nur das letzte Regal"]
    zwei = ev.analyse(ev.Settings(**C.PRESETS["Beispiel 1, nach Höhe, erstes passendes Regal"]))
    assert zwei.count == 3 == zwei.opt and "Das sind drei Behälter, so viele wie das Optimum." in C.PRESET_HELP["Beispiel 1, nach Höhe, erstes passendes Regal"]
    drei = ev.analyse(ev.Settings(**C.PRESETS["Beispiel 2, nach Fläche, erstes passendes Regal"]))
    hoehe = ev.analyse(ev.Settings(**{**C.PRESETS["Beispiel 2, nach Fläche, erstes passendes Regal"], "schluessel": 1}))
    assert drei.count == 4 and hoehe.count == 3 and "Hier ist die Höhe die bessere Wahl." in C.PRESET_HELP["Beispiel 2, nach Fläche, erstes passendes Regal"]
    vier = C.PRESETS["Mittlere Rechtecke, nach Höhe, nur das letzte Regal"]
    a = ev.analyse(ev.Settings(**vier))
    first = A.anzahl(a.inst.rects, 1, 1, a.inst.cap)
    assert a.inst.n == 20 and a.count > first and "20 mittleren Rechtecken" in C.PRESET_HELP["Mittlere Rechtecke, nach Höhe, nur das letzte Regal"]
    assert all(A.packung_pruefen(x.inst.rects, x.platz, x.inst.cap) for x in (eins, zwei, drei, a))
