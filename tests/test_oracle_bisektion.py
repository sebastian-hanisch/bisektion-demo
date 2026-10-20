"""Orakel-Test bisektion-demo: kleinste Bisektion, kleinster Schnitt ohne Balance und die Durchläufe beider Verfahren gegen unabhängige Rechenwege (DEMO-PLAYBOOK §12).

Unabhängig: die Aufzählung aller Zweiteilungen mit `itertools.combinations` (eigene Schnittzählung aus der Kantenliste), `networkx.edge_connectivity` und `networkx.minimum_cut` für den Schnitt ohne Balance.
Die Durchläufe von Kernighan–Lin und Fiduccia–Mattheyses werden Zug für Zug nachgespielt: jeder gemeldete Gewinn wird an einer eigenen Nachzählung des Schnitts geprüft. Feste Netze (Seeds)."""

import itertools
import random

import pytest

import bis_algorithm as A
import bis_scenario as S

nx = pytest.importorskip("networkx")

from conftest import MINI  # noqa: E402


def _nets(count=36, base=700):
    kinds = ("random", "grid", "ring", "scalefree", "verbund", "geometric")
    for k in range(count):
        yield S.make_instance(kinds[k % len(kinds)], 8 + (k * 3) % 11, (3.0, 4.5, 6.0)[k % 3], 1 + k % 3, base + k)


def _count(pairs, side0):
    return sum((u in side0) != (v in side0) for u, v in pairs)


def _brute(n, pairs):
    """(kleinster Schnitt einer ausgewogenen Zweiteilung, Zahl der kleinsten, Zahl aller): alle Teilmengen der Größe ⌊n/2⌋ und ⌈n/2⌉; jede Zweiteilung kommt zweimal vor (Teilmenge und Rest)."""
    sizes = {n // 2, n - n // 2}
    values = []
    for k in sizes:
        for sub in itertools.combinations(range(n), k):
            values.append(_count(pairs, set(sub)))
    best = min(values)
    return best, values.count(best) // 2, len(values) // 2


def _graph(inst):
    g = nx.Graph()
    g.add_nodes_from(range(inst.n))
    g.add_edges_from(inst.pairs)
    return g


def test_the_oracle_itself_on_the_hand_computed_mini_networks():
    for name, (n, pairs, value, count, total, _mc) in MINI.items():
        assert _brute(n, pairs) == (value, count, total), name


def test_exact_bisection_equals_the_independent_enumeration():
    for inst in _nets(24):
        value, count, total = _brute(inst.n, inst.pairs)
        ex = A.exact_bisection(inst.adj)
        assert (ex.value, ex.count, ex.total) == (value, count, total), (inst.kind, inst.n)
        assert _count(inst.pairs, {v for v in range(inst.n) if ex.side[v] == 0}) == value


def test_min_cut_equals_networkx_edge_connectivity_and_the_side_is_a_real_cut():
    for inst in _nets():
        value, side = A.min_cut(inst.adj)
        g = _graph(inst)
        assert value == nx.edge_connectivity(g), (inst.kind, inst.n)
        assert 0 < len(side) < inst.n and _count(inst.pairs, set(side)) == value


def test_min_cut_value_equals_the_smallest_cut_over_all_subsets_on_tiny_networks():
    rng = random.Random(5)
    for _ in range(30):
        n = rng.randint(3, 8)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n) if rng.random() < 0.5]
        if not pairs or len(S._components(S._adj_from_pairs(n, pairs))) != 1:
            continue
        smallest = min(_count(pairs, set(sub)) for k in range(1, n) for sub in itertools.combinations(range(n), k))
        assert A.min_cut(S._adj_from_pairs(n, pairs))[0] == smallest


def test_no_run_beats_the_optimum_and_every_run_is_balanced_and_recounted():
    for inst in _nets(18, 900):
        value, _c, _t = _brute(inst.n, inst.pairs)
        for method in ("kl", "fm"):
            for run in A.multistart(method, inst.adj, 6, 1, random.Random(inst.n)):
                side0 = {v for v in range(inst.n) if run.side[v] == 0}
                assert A.is_balanced(run.side) and _count(inst.pairs, side0) == run.cut >= value
                assert run.cut <= run.start_cut == _count(inst.pairs, {v for v in range(inst.n) if run.start[v] == 0})


def test_kl_passes_replayed_swap_by_swap_against_an_own_recount():
    for inst in _nets(18, 1000):
        side = A.random_bisection(inst.n, random.Random(inst.n + 3))
        new, p = A.kl_pass(inst.adj, side)
        cur = list(side)
        cut = _count(inst.pairs, {v for v in range(inst.n) if cur[v] == 0})
        seen = set()
        total = 0
        for i, (a, b, g) in enumerate(p.swaps):
            assert cur[a] == 0 and cur[b] == 1 and a not in seen and b not in seen
            seen |= {a, b}
            cur[a], cur[b] = 1, 0
            now = _count(inst.pairs, {v for v in range(inst.n) if cur[v] == 0})
            assert cut - now == g, (inst.kind, i)
            cut = now
            total += g
            assert p.cumulative[i] == total
            if i + 1 == p.best:
                assert list(new) == cur
        if not p.best:
            assert list(new) == list(side)
        assert p.cut_after == _count(inst.pairs, {v for v in range(inst.n) if new[v] == 0})


def test_fm_passes_replayed_move_by_move_against_an_own_recount():
    for inst in _nets(18, 1100):
        for slack in (0, 1, 2):
            side = A.random_bisection(inst.n, random.Random(inst.n + 7))
            new, p = A.fm_pass(inst.adj, side, slack)
            cur = list(side)
            cut = _count(inst.pairs, {v for v in range(inst.n) if cur[v] == 0})
            moved = set()
            lo, hi = inst.n // 2 - slack, inst.n - inst.n // 2 + slack
            for i, (v, g, cut_after, size0) in enumerate(p.moves):
                assert v not in moved
                moved.add(v)
                cur[v] ^= 1
                now = _count(inst.pairs, {u for u in range(inst.n) if cur[u] == 0})
                assert cut - now == g and now == cut_after and size0 == cur.count(0) and lo <= size0 <= hi
                cut = now
                if i + 1 == p.best:
                    assert list(new) == cur
            if not p.best:
                assert list(new) == list(side)
            assert p.cut_after == _count(inst.pairs, {u for u in range(inst.n) if new[u] == 0}) <= p.cut_before


def test_networkx_kernighan_lin_gives_the_same_kind_of_answer():
    """Gegenprobe „gleiche Aussage, nicht gleiches Ergebnis“: die Bisektion von networkx ist ausgewogen und nie kleiner als das Optimum; unser Bestes aus zehn Starts trifft das Optimum."""
    for inst in _nets(14, 1300):
        value, _c, _t = _brute(inst.n, inst.pairs)
        a, b = nx.algorithms.community.kernighan_lin_bisection(_graph(inst), seed=1)
        assert abs(len(a) - len(b)) <= 1 and _count(inst.pairs, set(a)) >= value
        assert min(r.cut for r in A.multistart("kl", inst.adj, 10, 1, random.Random(inst.n))) == value
