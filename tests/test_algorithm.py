"""Kern: jede Einheit an von Hand gerechneten Mini-Netzen (DEMO-PLAYBOOK §1b)."""

import random

import pytest

import bis_algorithm as A

from conftest import MINI, FixedRandom, adj_of


def _adj(name):
    n, pairs, *_ = MINI[name]
    return adj_of(n, pairs)


def test_cut_size_balanced_sizes_and_is_balanced_by_hand():
    adj = _adj("zwei_dreiecke")
    assert A.cut_size(adj, [0, 0, 0, 1, 1, 1]) == 1 and A.cut_size(adj, [0, 0, 1, 0, 1, 1]) == 5 and A.cut_size(adj, [0] * 6) == 0
    assert A.balanced_sizes(6) == {3} and A.balanced_sizes(5) == {2, 3} and A.balanced_sizes(7) == {3, 4}
    assert A.is_balanced([0, 1, 0, 1]) and A.is_balanced([0, 0, 1, 1, 1]) and not A.is_balanced([0, 0, 0, 1]) and not A.is_balanced([0, 0, 0, 0, 0, 1])


def test_random_bisection_with_a_fixed_source_is_the_number_order_and_always_balanced():
    assert A.random_bisection(6, FixedRandom()) == [0, 0, 0, 1, 1, 1] and A.random_bisection(5, FixedRandom()) == [0, 0, 0, 1, 1]
    rng = random.Random(4)
    for n in (4, 7, 18, 33):
        assert A.is_balanced(A.random_bisection(n, rng))
    assert A.random_bisection(12, random.Random(1)) == A.random_bisection(12, random.Random(1)) != A.random_bisection(12, random.Random(2))


def test_gains_d_by_hand():
    adj = _adj("zwei_dreiecke")
    assert A.degrees_to_sides(adj, [0, 0, 1, 0, 1, 1]) == [0, 0, 3, 3, 0, 0]                  # Standort 2 und 3 haben nur Leitungen nach außen


def test_kl_pass_by_hand():
    adj = _adj("zwei_dreiecke")
    side, p = A.kl_pass(adj, [0, 0, 1, 0, 1, 1])
    assert p.swaps == ((3, 2, 4), (0, 4, -4), (1, 5, 0)) and p.cumulative == (4, 0, 0) and p.best == 1 and p.gain == 4
    assert (p.evals, p.cut_before, p.cut_after) == (14, 5, 1) and side == [0, 0, 0, 1, 1, 1]       # 3 mal 3 + 2 mal 2 + 1 Paar bewertet


def test_kl_pass_without_gain_changes_nothing():
    adj = _adj("zwei_dreiecke")
    side, p = A.kl_pass(adj, [0, 0, 0, 1, 1, 1])
    assert side == [0, 0, 0, 1, 1, 1] and p.best == 0 and p.gain == 0 and p.cut_before == p.cut_after == 1 and p.cumulative[0] < 0


def test_kl_runs_until_no_gain_and_counts_work():
    adj = _adj("zwei_dreiecke")
    run = A.kl(adj, [0, 0, 1, 0, 1, 1])
    assert run.side == (0, 0, 0, 1, 1, 1) and run.cut == 1 and run.start_cut == 5 and len(run.passes) == 2 and run.work == 28 and run.start == (0, 0, 1, 0, 1, 1)
    assert [p.gain for p in run.passes] == [4, 0]


def test_fm_pass_by_hand_with_slack_one():
    adj = _adj("zwei_dreiecke")
    side, p = A.fm_pass(adj, [0, 0, 1, 0, 1, 1], 1)
    assert p.moves == ((2, 3, 2, 4), (3, 1, 1, 3), (0, -2, 3, 2), (4, -2, 5, 3), (1, 0, 5, 2), (5, 0, 5, 3))
    assert p.best == 2 and p.gain == 4 and not p.stuck and (p.cut_before, p.cut_after) == (5, 1) and side == [0, 0, 0, 1, 1, 1]


def test_fm_without_slack_is_stuck_on_even_and_moves_on_odd_networks():
    adj = _adj("zwei_dreiecke")
    side, p = A.fm_pass(adj, [0, 0, 1, 0, 1, 1], 0)
    assert p.stuck and p.moves == () and p.best == 0 and p.gain == 0 and side == [0, 0, 1, 0, 1, 1]
    star = _adj("stern5")
    _s, q = A.fm_pass(star, A.random_bisection(5, FixedRandom()), 0)
    assert not q.stuck and len(q.moves) >= 1                                                 # bei ungerader Standortzahl ist der Wechsel zwischen ⌊n/2⌋ und ⌈n/2⌉ erlaubt


def test_fm_run_and_work_by_hand():
    adj = _adj("zwei_dreiecke")
    run = A.fm(adj, [0, 0, 1, 0, 1, 1], 1)
    assert run.cut == 1 and run.side == (0, 0, 0, 1, 1, 1) and run.passes[0].gain == 4 and run.passes[-1].gain == 0 and run.work == 6 * len(run.passes)


def test_run_method_dispatch_and_multistart_uses_the_given_source():
    adj = _adj("zwei_dreiecke")
    s = [0, 0, 1, 0, 1, 1]
    assert A.run_method("kl", adj, s, 1) == A.kl(adj, s) and A.run_method("fm", adj, s, 1) == A.fm(adj, s, 1)
    with pytest.raises(ValueError):
        A.run_method("tabu", adj, s, 1)
    runs = A.multistart("kl", adj, 4, 1, random.Random(3))
    assert len(runs) == 4 and runs == A.multistart("kl", adj, 4, 1, random.Random(3)) and all(A.is_balanced(r.side) for r in runs)


def test_exact_bisection_of_every_mini_network():
    for name, (n, pairs, value, count, total, _mc) in MINI.items():
        ex = A.exact_bisection(adj_of(n, pairs))
        assert (ex.value, ex.count, ex.total) == (value, count, total), name
        assert A.is_balanced(ex.side) and A.cut_size(adj_of(n, pairs), ex.side) == value, name


def test_exact_bisection_sides_by_hand():
    assert A.exact_bisection(_adj("zwei_dreiecke")).side == (0, 0, 0, 1, 1, 1)
    assert A.exact_bisection(_adj("hantel")).side == (0, 0, 0, 0, 1, 1, 1, 1)                 # {A, B, C, D} gegen {E, F, G, H}: D-E und A-H
    assert A.exact_bisection(_adj("pfad4")).side == (0, 0, 1, 1)


def test_min_cut_without_balance_of_every_mini_network():
    for name, (n, pairs, _v, _c, _t, mc) in MINI.items():
        value, side = A.min_cut(adj_of(n, pairs))
        assert value == mc, name
        assert A.cut_size(adj_of(n, pairs), [0 if v in set(side) else 1 for v in range(n)]) == value, name


def test_min_cut_is_a_single_location_in_the_hantel_and_trivial_flag():
    value, side = A.min_cut(_adj("hantel"))
    assert (value, side) == (1, (7,)) and A.is_trivial(8, set(side))                       # Phase 1 endet am Standort H: seine eine Leitung ist der kleinste Schnitt
    assert A.is_trivial(8, {3}) and A.is_trivial(8, set(range(7))) and not A.is_trivial(8, {0, 1})
    assert A.min_cut(adj_of(1, [])) == (0, ())


def test_balance_costs_more_than_the_minimum_cut_on_the_hantel_and_the_star():
    for name in ("hantel", "stern5"):
        n, pairs, value, _c, _t, mc = MINI[name]
        assert value > mc
