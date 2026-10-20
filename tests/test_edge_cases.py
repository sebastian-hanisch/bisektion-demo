"""Randfälle der Kernroutinen: kleinste Netze, genau zwei Standorte je Hälfte, Gleichstände, Grenzen inklusive (DEMO-PLAYBOOK §12)."""

import random

import pytest

import bis_algorithm as A
import bis_constants as C
import bis_evaluation as ev
import bis_scenario as S

from conftest import FixedRandom, adj_of


def test_two_locations_form_the_smallest_bisection():
    adj = adj_of(2, [(0, 1)])
    ex = A.exact_bisection(adj)
    assert (ex.value, ex.count, ex.total, ex.side) == (1, 1, 1, (0, 1))
    assert A.min_cut(adj) == (1, (0,)) or A.min_cut(adj)[0] == 1
    run = A.kl(adj, [0, 1])
    assert run.cut == 1 and run.side == (0, 1) and run.passes[-1].gain == 0
    assert A.fm(adj, [0, 1], 1).cut == 1


def test_four_locations_with_two_per_half():
    adj = adj_of(4, [(0, 1), (2, 3)])                                                       # nicht zusammenhängend: kleinster Schnitt 0, Bisektion 0
    ex = A.exact_bisection(adj)
    assert (ex.value, ex.count, ex.total) == (0, 1, 3) and A.min_cut(adj)[0] == 0
    side, p = A.kl_pass(adj, [0, 1, 0, 1])
    assert p.cut_before == 2 and p.cut_after == 0 and A.cut_size(adj, side) == 0


def test_a_network_without_links_has_no_gain_and_does_not_loop():
    adj = adj_of(6, [])
    for method in C.METHODS:
        run = A.run_method(method, adj, A.random_bisection(6, FixedRandom()), 1)
        assert run.cut == 0 and run.start_cut == 0 and len(run.passes) == 1 and run.passes[0].gain == 0


def test_balanced_sizes_at_the_smallest_networks():
    assert A.balanced_sizes(2) == {1} and A.balanced_sizes(3) == {1, 2} and A.balanced_sizes(1) == {0, 1}


def test_a_run_stops_at_the_pass_limit():
    adj = adj_of(6, [(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])
    run = A.kl(adj, [0, 0, 1, 0, 1, 1], max_passes=1)
    assert len(run.passes) == 1 and run.cut == 1 and run.passes[0].gain == 4                 # der Lauf hört nach dem ersten Durchlauf auf, auch wenn er gewonnen hat
    run = A.fm(adj, [0, 0, 1, 0, 1, 1], 1, max_passes=1)
    assert len(run.passes) == 1 and run.cut == 1


def test_exact_bisection_odd_n_counts_every_partition_once():
    adj = adj_of(3, [(0, 1), (1, 2)])
    ex = A.exact_bisection(adj)
    assert (ex.value, ex.count, ex.total) == (1, 2, 3)                                       # Pfad 0-1-2: {0} | {1,2} und {0,1} | {2}
    assert A.is_balanced(ex.side) and ex.side == (0, 0, 1)                                    # bei ungerader Zahl ist die Hälfte 0 die größere (Dokumentation der Funktion)


def test_is_trivial_boundaries():
    assert A.is_trivial(5, {2}) and A.is_trivial(5, {0, 1, 2, 3}) and not A.is_trivial(5, {0, 1}) and not A.is_trivial(5, {0, 1, 2}) and not A.is_trivial(4, {0, 1})


def test_random_bisection_of_two_and_three_locations():
    assert A.random_bisection(2, FixedRandom()) == [0, 1] and A.random_bisection(3, FixedRandom()) == [0, 0, 1]


def test_validate_reports_every_kind_of_problem_on_tampered_analyses():
    import dataclasses
    a = ev.analyse(ev.Settings())
    assert ev.validate(a) == []
    kl = a.runs["kl"]
    bad_cut = dataclasses.replace(kl[0], cut=kl[0].cut + 1)
    assert any("Nachzählung" in p for p in ev.validate(dataclasses.replace(a, runs={**a.runs, "kl": (bad_cut,) + kl[1:]})))
    unbalanced = dataclasses.replace(kl[0], side=(0,) * 8)
    assert any("nicht ausgewogen" in p for p in ev.validate(dataclasses.replace(a, runs={**a.runs, "kl": (unbalanced,) + kl[1:]})))
    below = dataclasses.replace(a.exact, value=a.exact.value + 1)
    assert any("unter dem Optimum" in p for p in ev.validate(dataclasses.replace(a, exact=below)))
    wrong_exact = dataclasses.replace(a.exact, value=a.exact.value + 5)
    assert any("Aufzählung" in p for p in ev.validate(dataclasses.replace(a, exact=wrong_exact)))
    assert any("ohne Balance" in p for p in ev.validate(dataclasses.replace(a, mincut=99)))
    p0 = dataclasses.replace(kl[0].passes[0], gain=kl[0].passes[0].gain + 1)
    gains = dataclasses.replace(kl[0], passes=(p0,) + kl[0].passes[1:])
    assert any("Gewinne" in p for p in ev.validate(dataclasses.replace(a, runs={**a.runs, "kl": (gains,) + kl[1:]})))
    worse = dataclasses.replace(kl[0], start_cut=kl[0].cut - 1) if kl[0].cut > 0 else None
    assert worse is not None
    assert any("größer als der Start" in p or "Nachzählung" in p for p in ev.validate(dataclasses.replace(a, runs={**a.runs, "kl": (worse,) + kl[1:]})))


def test_the_analysis_is_deterministic_and_does_not_depend_on_the_method_setting():
    a1 = ev.analyse(ev.Settings(kind="random", n=14, seed=5))
    a2 = ev.analyse(ev.Settings(kind="random", n=14, seed=5))
    assert a1.runs == a2.runs and a1.exact == a2.exact
    b = ev.analyse(ev.Settings(kind="random", n=14, seed=5, method="fm"))
    assert b.runs == a1.runs and b.chosen() is b.runs["fm"]                                  # beide Verfahren laufen immer, gleiche Startanordnungen
    assert [r.start for r in a1.runs["kl"]] == [r.start for r in a1.runs["fm"]]


def test_size_boundaries_of_the_regler_range():
    for n in (C.N_MIN, C.N_MAX):
        inst = S.make_instance("random", n, C.DEG_MIN, C.LINKS_MIN, 1)
        assert inst.n == n and len(S._components(inst.adj)) == 1
    a = ev.analyse(ev.Settings(kind="random", n=C.BRUTE_N, seed=3))
    assert a.exact is not None
    assert ev.analyse(ev.Settings(kind="random", n=C.BRUTE_N + 1, seed=3)).exact is None


def test_unknown_method_raises():
    with pytest.raises(ValueError):
        A.run_method("annealing", adj_of(4, [(0, 1)]), [0, 0, 1, 1], 1)
    assert random.Random(1)
