"""Kern der Demo (nur Standardbibliothek): ausgewogen halbieren.

Ein Netz hat n Standorte und ungewichtete Leitungen `adj[v]` (Nachbarmengen). Eine **Bisektion** teilt die Standorte in zwei Hälften der Größe ⌈n/2⌉ und ⌊n/2⌋; ihr **Schnitt** ist die Zahl der Leitungen zwischen den Hälften.
`side[v]` ist 0 oder 1.

* `kl`: Kernighan–Lin. Ein Durchlauf tauscht Paare (a aus der einen, b aus der anderen Hälfte) mit dem größten Gewinn D(a) + D(b) - 2 w(a, b), sperrt sie und wiederholt das, bis alle gesperrt sind; der beste Präfix der
  Gewinnfolge wird ausgeführt, wenn sein Gewinn positiv ist. D(v) = Leitungen nach außen - Leitungen nach innen.
* `fm`: Fiduccia–Mattheyses. Ein Durchlauf verschiebt **einzelne** Standorte (größter Gewinn zuerst, jeder nur einmal) und darf dabei die Hälften verschieden groß werden lassen (**Spielraum**); ausgeführt wird der beste Präfix
  unter den Zuständen, die wieder ausgewogen sind. Ohne Spielraum ist bei gerader Standortzahl jeder Zug blockiert.
* `exact_bisection`: Aufzählung aller Bisektionen (kleine Netze) als Optimum und Prüfer.
* `min_cut`: der kleinste Schnitt **ohne** Balance (Stoer–Wagner) als Kontrast.

Aufwand wird gezählt, nie in Sekunden: bei Kernighan–Lin in **Paarbewertungen** (jedes angesehene Paar), bei Fiduccia–Mattheyses in **Zügen** (jeder ausgeführte Einzelzug, auch die verworfenen)."""

from dataclasses import dataclass
from itertools import combinations

import bis_constants as C


# --- Hilfen --------------------------------------------------------------------------------------------------------------------------------------


def cut_size(adj, side):
    """Zahl der Leitungen zwischen den Hälften."""
    return sum(1 for u in range(len(adj)) for v in adj[u] if u < v and side[u] != side[v])


def balanced_sizes(n):
    """Erlaubte Größen der Hälfte 0 bei einer Bisektion: ⌊n/2⌋ und ⌈n/2⌉."""
    return {n // 2, n - n // 2}


def is_balanced(side):
    return sum(1 for s in side if s == 0) in balanced_sizes(len(side))


def random_bisection(n, rng):
    """Zufällige Bisektion: Fisher–Yates mit `random()`, die ersten ⌈n/2⌉ Standorte in Hälfte 0."""
    order = list(range(n))
    for i in range(n - 1, 0, -1):
        j = min(i, int(rng.random() * (i + 1)))
        order[i], order[j] = order[j], order[i]
    side = [1] * n
    for v in order[: n - n // 2]:
        side[v] = 0
    return side


def degrees_to_sides(adj, side):
    """D(v) = Leitungen nach außen minus Leitungen nach innen (Gewinn beim Verschieben eines einzelnen Standorts)."""
    return [sum(1 for u in adj[v] if side[u] != side[v]) - sum(1 for u in adj[v] if side[u] == side[v]) for v in range(len(adj))]


# --- Kernighan–Lin -------------------------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class KLPass:
    swaps: tuple            # ((a, b, Gewinn), ...) in der Reihenfolge der Wahl
    cumulative: tuple       # Summe der Gewinne nach jedem Paar
    best: int               # Länge des besten Präfix (0: kein positiver Gewinn)
    gain: int               # Gewinn des besten Präfix (0, wenn nichts ausgeführt wird)
    evals: int              # Paarbewertungen in diesem Durchlauf
    cut_before: int
    cut_after: int


def kl_pass(adj, side):
    """Ein Durchlauf von Kernighan–Lin auf einer Kopie; gibt (neue Hälften, Durchlauf) zurück."""
    n = len(adj)
    side = list(side)
    d = degrees_to_sides(adj, side)
    free = {0: [v for v in range(n) if side[v] == 0], 1: [v for v in range(n) if side[v] == 1]}
    swaps, cumulative, evals, total = [], [], 0, 0
    for _ in range(min(len(free[0]), len(free[1]))):
        best = None
        for a in free[0]:
            for b in free[1]:
                g = d[a] + d[b] - (2 if b in adj[a] else 0)
                if best is None or g > best[0]:
                    best = (g, a, b)
        evals += len(free[0]) * len(free[1])
        g, a, b = best
        swaps.append((a, b, g))
        total += g
        cumulative.append(total)
        free[0].remove(a)
        free[1].remove(b)
        for x in free[0]:
            d[x] += 2 * (1 if x in adj[a] else 0) - 2 * (1 if x in adj[b] else 0)
        for y in free[1]:
            d[y] += 2 * (1 if y in adj[b] else 0) - 2 * (1 if y in adj[a] else 0)
    before = cut_size(adj, side)
    best_k = max(range(len(cumulative)), key=lambda i: (cumulative[i], -i)) + 1 if cumulative else 0
    gain = cumulative[best_k - 1] if best_k and cumulative[best_k - 1] > 0 else 0
    if not gain:
        best_k = 0
    new = list(side)
    for a, b, _g in swaps[:best_k]:
        new[a], new[b] = 1, 0
    return new, KLPass(tuple(swaps), tuple(cumulative), best_k, gain, evals, before, cut_size(adj, new))


@dataclass(frozen=True)
class Run:
    side: tuple
    cut: int
    start_cut: int
    passes: tuple           # KLPass bzw. FMPass je Durchlauf (der letzte ohne Gewinn)
    work: int               # Paarbewertungen (KL) bzw. Züge (FM)
    start: tuple            # die Startanordnung


def kl(adj, side, max_passes=C.MAX_PASSES):
    """Kernighan–Lin bis kein Durchlauf mehr gewinnt."""
    start = tuple(side)
    cur, passes, work = list(side), [], 0
    for _ in range(max_passes):
        cur, p = kl_pass(adj, cur)
        passes.append(p)
        work += p.evals
        if p.gain <= 0:
            break
    return Run(tuple(cur), cut_size(adj, cur), cut_size(adj, start), tuple(passes), work, start)


# --- Fiduccia–Mattheyses -------------------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class FMPass:
    moves: tuple            # ((Standort, Gewinn, Schnitt danach, Größe der Hälfte 0 danach), ...) in der Reihenfolge der Züge
    best: int               # Länge des besten Präfix unter den wieder ausgewogenen Zuständen (0: nichts ausgeführt)
    gain: int
    stuck: bool             # kein einziger Zug war erlaubt
    cut_before: int
    cut_after: int


def fm_pass(adj, side, slack):
    """Ein Durchlauf von Fiduccia–Mattheyses auf einer Kopie; die Größe der Hälfte 0 darf zwischen ⌊n/2⌋ - slack und ⌈n/2⌉ + slack liegen."""
    n = len(adj)
    side = list(side)
    lo, hi = n // 2 - slack, n - n // 2 + slack
    size0 = sum(1 for s in side if s == 0)
    gain = degrees_to_sides(adj, side)
    cut = cut_size(adj, side)
    start_cut = cut
    locked = [False] * n
    moves = []
    for _ in range(n):
        cand = [v for v in range(n) if not locked[v] and lo <= size0 + (-1 if side[v] == 0 else 1) <= hi]
        if not cand:
            break
        v = max(cand, key=lambda x: (gain[x], -x))
        g = gain[v]
        cut -= g
        size0 += -1 if side[v] == 0 else 1
        side[v] ^= 1
        locked[v] = True
        for u in adj[v]:
            if not locked[u]:
                gain[u] += -2 if side[u] == side[v] else 2
        gain[v] = -g
        moves.append((v, g, cut, size0))
    ok = [i for i, (_v, _g, _c, s) in enumerate(moves) if s in balanced_sizes(n)]
    best_i = min(ok, key=lambda i: (moves[i][2], i)) if ok else None
    best = best_i + 1 if best_i is not None and moves[best_i][2] < start_cut else 0
    new = list(side)
    for v, _g, _c, _s in reversed(moves[best:]):                         # Züge nach dem besten Präfix zurücknehmen
        new[v] ^= 1
    return new, FMPass(tuple(moves), best, start_cut - moves[best - 1][2] if best else 0, not moves, start_cut, cut_size(adj, new))


def fm(adj, side, slack, max_passes=C.MAX_PASSES):
    """Fiduccia–Mattheyses bis kein Durchlauf mehr gewinnt."""
    start = tuple(side)
    cur, passes, work = list(side), [], 0
    for _ in range(max_passes):
        cur, p = fm_pass(adj, cur, slack)
        passes.append(p)
        work += len(p.moves)
        if p.gain <= 0:
            break
    return Run(tuple(cur), cut_size(adj, cur), cut_size(adj, start), tuple(passes), work, start)


def run_method(method, adj, side, slack):
    if method == "kl":
        return kl(adj, side)
    if method == "fm":
        return fm(adj, side, slack)
    raise ValueError(f"unbekanntes Verfahren {method}")


def multistart(method, adj, starts, slack, rng):
    """`starts` unabhängige Zufallsstarts; gibt die Läufe in der Reihenfolge der Starts zurück."""
    return tuple(run_method(method, adj, random_bisection(len(adj), rng), slack) for _ in range(starts))


# --- Optimum und Kontrast ------------------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Exact:
    value: int
    count: int              # Zahl der Bisektionen mit dem kleinsten Schnitt (jede Zweiteilung einmal)
    side: tuple             # eine davon
    total: int              # Zahl aller Bisektionen


def exact_bisection(adj):
    """Alle Bisektionen (n <= 20): kleinster Schnitt, Zahl der kleinsten und Zahl aller. Bei geradem n enthält die Hälfte 0 den Standort 0, bei ungeradem n ist die Hälfte 0 die größere."""
    n = len(adj)
    full = (1 << n) - 1
    mask = [sum(1 << u for u in adj[v]) for v in range(n)]
    size = n - n // 2
    best, count, best_set, total = None, 0, None, 0
    pool = range(1, n) if n % 2 == 0 and size == n // 2 else range(n)
    k = size - 1 if n % 2 == 0 else size
    for combo in combinations(pool, k):
        s = 0
        members = ((0,) + combo) if n % 2 == 0 else combo
        for v in members:
            s |= 1 << v
        out = ~s & full
        cut = sum((mask[v] & out).bit_count() for v in members)
        total += 1
        if best is None or cut < best:
            best, count, best_set = cut, 1, members
        elif cut == best:
            count += 1
    side = tuple(0 if v in set(best_set) else 1 for v in range(n))
    return Exact(best, count, side, total)


def min_cut(adj):
    """Kleinster Schnitt ohne Balance (Stoer–Wagner, ungewichtet): (Wert, eine Seite)."""
    n = len(adj)
    if n < 2:
        return 0, ()
    w = [[1 if v in adj[u] else 0 for v in range(n)] for u in range(n)]
    members = {v: [v] for v in range(n)}
    active = list(range(n))
    best = None
    while len(active) > 1:
        key = {v: 0 for v in active}
        rest = list(active)
        order, bind = [], []
        while rest:
            pick = min(rest, key=lambda v: (-key[v], v))
            order.append(pick)
            bind.append(key[pick])
            rest.remove(pick)
            for v in rest:
                key[v] += w[pick][v]
        last, before = order[-1], order[-2]
        if best is None or bind[-1] < best[0]:
            best = (bind[-1], tuple(sorted(members[last])))
        for x in active:
            if x != last and x != before:
                w[before][x] += w[last][x]
                w[x][before] = w[before][x]
        members[before].extend(members[last])
        active.remove(last)
    return best


def is_trivial(n, side_set):
    return len(side_set) == 1 or len(side_set) == n - 1
