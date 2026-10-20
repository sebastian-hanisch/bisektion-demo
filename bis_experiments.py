"""Experimente über feste Netze (nie ein einzelner Zufalls-Seed als Befund). Jede Funktion gibt eine Liste von Zeilen (dict) zurück; Verdikte und Abbildungen lesen nur diese Zeilen.

1. `exactness_rows`: stimmen beide Verfahren (Ausgewogenheit, Schnitt, Gewinne, nie unter dem Optimum) mit der Aufzählung aller Bisektionen überein?
2. `balance_rows`: wie viel teurer ist die ausgewogene Zweiteilung als der kleinste Schnitt ohne Balance?
3. `starts_rows`: wie oft trifft ein Start, wie oft das Beste aus zehn Starts das Optimum?
4. `big_rows`: im großen Netz: Abstand zur besten gefundenen Bisektion und Aufwand je Verfahren bei einem Start.
5. `slack_rows`: Fiduccia–Mattheyses mit wachsendem Spielraum der Balance."""

import random

import bis_algorithm as A
import bis_constants as C
import bis_scenario as S


def kind_label(kind, deg):
    name = C.KIND_NAMES[kind]
    return f"{name}, Grad {deg:g}".replace(".", ",") if kind in ("random", "verbund") else name


def _net(kind, deg, n, seed):
    return S.make_instance(kind, n, deg, 1, seed)


def _rng(seed, extra=0):
    return random.Random(seed * 53 + C.START_SALT + extra)


def _pass_gains_ok(run, adj):
    """Der Gewinn jedes Durchlaufs ist gleich dem Unterschied der nachgezählten Schnitte; die Durchläufe schließen aneinander an."""
    cut = run.start_cut
    for p in run.passes:
        if p.cut_before != cut or p.cut_before - p.cut_after != p.gain:
            return False
        cut = p.cut_after
    return cut == run.cut


def exactness_rows():
    rows = []
    for kind, deg in C.EX_KINDS:
        checks = wrong = 0
        for seed in C.SWEEP_SEEDS:
            inst = _net(kind, deg, C.EX_N, seed)
            adj = inst.adj
            ex = A.exact_bisection(adj)
            mc, _ = A.min_cut(adj)
            res = [ex.total > 0 and ex.value >= mc, A.cut_size(adj, ex.side) == ex.value and A.is_balanced(ex.side)]
            for method in C.METHODS:
                for run in A.multistart(method, adj, C.EX_STARTS, C.DEFAULT_SLACK, _rng(seed)):
                    res += [A.is_balanced(run.side), run.cut == A.cut_size(adj, run.side), run.cut >= ex.value, run.cut <= run.start_cut, _pass_gains_ok(run, adj)]
            checks += len(res)
            wrong += res.count(False)
        rows.append({"kind": kind, "deg": deg, "label": kind_label(kind, deg), "nets": len(C.SWEEP_SEEDS), "checks": checks, "wrong": wrong, "n": C.EX_N, "starts": C.EX_STARTS})
    return rows


def balance_rows():
    rows = []
    for kind, deg in C.EX_KINDS:
        row = {"kind": kind, "deg": deg, "label": kind_label(kind, deg), "nets": 0, "sum_ratio": 0.0, "min_ratio": None, "max_ratio": None, "trivial": 0, "sum_opt": 0, "sum_mincut": 0, "sum_bisection": 0, "n": C.EX_N}
        for seed in C.SWEEP_SEEDS:
            inst = _net(kind, deg, C.EX_N, seed)
            ex = A.exact_bisection(inst.adj)
            mc, side = A.min_cut(inst.adj)
            ratio = ex.value / mc
            row["nets"] += 1
            row["sum_ratio"] += ratio
            row["min_ratio"] = ratio if row["min_ratio"] is None else min(row["min_ratio"], ratio)
            row["max_ratio"] = ratio if row["max_ratio"] is None else max(row["max_ratio"], ratio)
            row["trivial"] += A.is_trivial(inst.n, set(side))
            row["sum_opt"] += ex.count
            row["sum_mincut"] += mc
            row["sum_bisection"] += ex.value
        rows.append(row)
    return rows


def starts_rows():
    rows = []
    for kind, deg in C.EX_KINDS:
        row = {"kind": kind, "deg": deg, "label": kind_label(kind, deg), "nets": 0, "one": {"kl": 0, "fm": 0}, "best": {"kl": 0, "fm": 0}, "starts": C.EX_STARTS, "n": C.EX_N}
        for seed in C.SWEEP_SEEDS:
            inst = _net(kind, deg, C.EX_N, seed)
            ex = A.exact_bisection(inst.adj)
            row["nets"] += 1
            for method in C.METHODS:
                runs = A.multistart(method, inst.adj, C.EX_STARTS, C.DEFAULT_SLACK, _rng(seed))
                row["one"][method] += runs[0].cut == ex.value
                row["best"][method] += min(r.cut for r in runs) == ex.value
        rows.append(row)
    return rows


def big_rows():
    rows = []
    for kind, deg in C.EX_KINDS:
        row = {"kind": kind, "deg": deg, "label": kind_label(kind, deg), "nets": 0, "gap_kl": 0.0, "gap_fm": 0.0, "evals_kl": 0.0, "moves_fm": 0.0, "sum_ref": 0.0, "n": C.EX_BIG_N, "reference": C.EX_BIG_REFERENCE}
        for seed in C.SWEEP_SEEDS[:C.EX_BIG_SEEDS]:
            inst = _net(kind, deg, C.EX_BIG_N, seed)
            adj = inst.adj
            fm_runs = A.multistart("fm", adj, C.EX_BIG_REFERENCE, C.DEFAULT_SLACK, _rng(seed))
            kl_one = A.multistart("kl", adj, 1, C.DEFAULT_SLACK, _rng(seed))[0]
            ref = min(min(r.cut for r in fm_runs), kl_one.cut)
            row["nets"] += 1
            row["gap_kl"] += kl_one.cut - ref
            row["gap_fm"] += fm_runs[0].cut - ref
            row["evals_kl"] += kl_one.work
            row["moves_fm"] += fm_runs[0].work
            row["sum_ref"] += ref
        rows.append(row)
    return rows


def slack_rows():
    rows = []
    for slack in range(0, 5):
        row = {"slack": slack, "runs": 0, "sum_start": 0, "sum_final": 0, "stuck": 0, "n": C.EX_SLACK_N}
        for kind, deg in C.EX_KINDS:
            for seed in C.SWEEP_SEEDS[:C.EX_SLACK_SEEDS]:
                inst = _net(kind, deg, C.EX_SLACK_N, seed)
                for run in A.multistart("fm", inst.adj, C.EX_SLACK_STARTS, slack, _rng(seed)):
                    row["runs"] += 1
                    row["sum_start"] += run.start_cut
                    row["sum_final"] += run.cut
                    row["stuck"] += run.passes[0].stuck
        rows.append(row)
    return rows
