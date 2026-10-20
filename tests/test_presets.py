"""Presets: Vollständigkeit, gültige Werte, erstes Preset = Standardeinstellungen; Permalink-Grenzen."""

import bis_constants as C
import bis_evaluation as ev
import bis_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds_and_choices():
    for name, preset in C.PRESETS.items():
        assert preset["kind"] in C.KINDS and preset["method"] in C.METHODS and preset["starts"] in C.STARTS, name
        assert C.N_MIN <= preset["n"] <= C.N_MAX and C.DEG_MIN <= preset["deg"] <= C.DEG_MAX and C.LINKS_MIN <= preset["links"] <= C.LINKS_MAX, name
        assert C.SLACK_MIN <= preset["slack"] <= C.SLACK_MAX and 0 <= preset["seed"] <= C.SEED_MAX, name


def test_the_first_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[next(iter(C.PRESETS))]) == ev.Settings()


def test_setting_specs_cover_every_preset_key_and_every_choice_field_is_listed():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    assert {spec.url_param for spec in P.SETTING_SPECS.values()} == {"kind", "n", "deg", "links", "seed", "method", "slack", "starts"}
    assert set(P.CHOICES) == {"kind_select", "method_select", "starts_select"} and P.CHOICES["starts_select"] == C.STARTS and P.CHOICES["method_select"] == C.METHODS


def test_every_kind_has_a_name_a_help_text_and_a_regler_note_and_every_method_a_name():
    assert set(C.KIND_NAMES) == set(C.KIND_HELP) == set(C.KIND_REGLER) == set(C.KINDS) and set(C.METHOD_NAMES) == set(C.METHODS)


def test_the_experiment_grid_uses_only_known_kinds_and_sizes_inside_the_regler_range():
    assert all(kind in C.KINDS and kind != "textbook" for kind, _deg in C.EX_KINDS)
    for n in (C.EX_N, C.EX_BIG_N, C.EX_SLACK_N):
        assert C.N_MIN <= n <= C.N_MAX and int(n ** 0.5) ** 2 == n                      # Quadratzahl: das Gitter hat dieselbe Größe wie die anderen Netztypen
    assert C.EX_N <= C.BRUTE_N < C.EX_BIG_N and C.EX_BIG_SEEDS <= len(C.SWEEP_SEEDS) and C.EX_SLACK_SEEDS <= len(C.SWEEP_SEEDS) and C.EX_STARTS in C.STARTS
    assert C.DEFAULT_STARTS in C.STARTS


def test_the_presets_that_use_the_enumeration_stay_within_its_limit():
    for name, preset in C.PRESETS.items():
        n = ev.analyse(ev.Settings(**preset)).n
        assert (n <= C.BRUTE_N) == (name != "Großes Kartennetz"), name
