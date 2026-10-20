"""Gemeinsame Fixtures: die Mini-Netze, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b).

Teure Experimente laufen einmal je Testlauf (`lru_cache`) und werden von Claims-, Verdikt- und Mutationstests gemeinsam genutzt."""

import sys
from functools import lru_cache
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def adj_of(n, pairs):
    nb = [set() for _ in range(n)]
    for u, v in pairs:
        nb[u].add(v)
        nb[v].add(u)
    return tuple(frozenset(s) for s in nb)


# Von Hand gerechnete Mini-Netze: Name -> (n, Leitungen, kleinste Bisektion, Zahl der kleinsten, Zahl aller Bisektionen, kleinster Schnitt ohne Balance)
MINI = {
    "zwei_dreiecke": (6, [(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)], 1, 1, 10, 1),
    "kreis6": (6, [(v, (v + 1) % 6) for v in range(6)], 2, 3, 10, 2),               # Halbierungen des Rings: zwei Leitungen, drei Möglichkeiten mit dem Standort 0
    "pfad4": (4, [(0, 1), (1, 2), (2, 3)], 1, 1, 3, 1),
    "vollstaendig4": (4, [(a, b) for a in range(4) for b in range(a + 1, 4)], 4, 3, 3, 3),
    "stern5": (5, [(0, v) for v in range(1, 5)], 2, 6, 10, 1),                    # Mitte in der größeren Hälfte (3): zwei Blätter in der anderen, Schnitt 2; sechs Möglichkeiten
    "hantel": (8, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (4, 5), (4, 6), (5, 6), (3, 4), (0, 7)], 2, 1, 35, 1),
}


class FixedRandom:
    """Liefert immer fast 1: Fisher–Yates lässt die Reihenfolge unverändert, die Startanordnung ist die Nummernfolge (erste Hälfte in Hälfte 0)."""

    def random(self):
        return 0.999999


@pytest.fixture
def mini():
    return MINI


@lru_cache(maxsize=None)
def cached(name):
    """Einmal je Testlauf berechnete Experimente (Name der Funktion in bis_experiments)."""
    import bis_experiments as ex
    return getattr(ex, name)()
