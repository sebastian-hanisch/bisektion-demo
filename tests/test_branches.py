"""Zweige der Hauptansicht (Nullspalte-Lehre): Jeder Weg, den die App zeigt, kommt in mindestens einem Preset oder einem festen Netz vor.

Ein Preset, das seine Beschreibung nicht einlöst, fällt hier auf. Die Abbildungen werden für jeden Zweig einmal gebaut (kein Fehler, nichtleere Daten)."""

import bis_constants as C
import bis_evaluation as ev
import bis_visualization as V


def _all():
    return {name: ev.analyse(ev.Settings(**p)) for name, p in C.PRESETS.items()}


def test_every_preset_validates_clean():
    for name, a in _all().items():
        assert ev.validate(a) == [], name


def test_every_branch_of_the_question_is_reached():
    analyses = _all().values()
    assert any(a.exact is None for a in analyses) and any(a.exact is not None for a in analyses)
    assert any(a.mincut_trivial for a in analyses) and any(not a.mincut_trivial for a in analyses)
    assert any(a.first_cut() > a.optimum for a in analyses if a.exact) and any(a.first_cut() == a.optimum for a in analyses if a.exact)
    assert any(a.exact.count > 1 for a in analyses if a.exact) and any(a.exact.count == 1 for a in analyses if a.exact)
    assert any(a.settings.method == "kl" for a in analyses) and any(a.settings.method == "fm" for a in analyses)
    assert any(any(r.passes[0].stuck for r in a.runs["fm"]) for a in analyses)


def test_every_kind_is_used_by_a_preset_or_is_a_known_extra():
    kinds = {p["kind"] for p in C.PRESETS.values()}
    assert kinds >= {"textbook", "random", "grid", "scalefree", "verbund", "geometric"}


def test_the_figures_build_for_every_preset():
    for name, a in _all().items():
        run = a.best_run()
        for method in C.METHODS:
            assert V.build_starts(a.runs[method], a.optimum).data, (name, method)
            assert V.build_best_so_far(a.runs[method], a.optimum).data, (name, method)
        assert V.build_methods(a).data and V.build_partition_map(a.inst, run.side).data, name
        first = run.passes[0]
        if run.start is not None and a.settings.method == "kl" and first.swaps:
            assert V.build_kl_curve(first).data and V.kl_state(run.start, first.swaps, len(first.swaps))
        if a.settings.method == "fm" and first.moves:
            assert V.build_fm_curve(first, a.n).data and V.fm_state(run.start, first.moves, len(first.moves))


def test_the_experiment_figures_build_from_the_cached_rows():
    from conftest import cached
    for fig, rows in ((V.build_exact, "exactness_rows"), (V.build_balance, "balance_rows"), (V.build_starts_hit, "starts_rows"), (V.build_big, "big_rows"), (V.build_slack, "slack_rows")):
        assert fig(cached(rows)).data
