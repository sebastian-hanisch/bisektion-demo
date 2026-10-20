"""Jede Zahl im README (Abschnitt „Befunde“) wird hier über dieselben Experimentfunktionen wie in der App nachgerechnet (DEMO-PLAYBOOK §4).

Zähler und Mittel über feste Netze (je Netztyp zwölf Netze mit 16 Standorten, feste Zufalls-Seeds), nie ein einzelner Zufalls-Seed. Aufwand in Paarbewertungen (Kernighan–Lin) und Zügen
(Fiduccia–Mattheyses), nicht in Sekunden. Die Zahlen der Vormessung im Einzelplan stammen aus Wegwerfskripten mit anderen Netzen; maßgeblich sind diese hier."""

import pytest

import bis_constants as C
import bis_evaluation as ev

from conftest import cached


def test_every_method_agrees_with_the_enumeration_on_every_small_network():
    rows = cached("exactness_rows")
    assert len(rows) == 7 and sum(r["nets"] for r in rows) == 84 and sum(r["checks"] for r in rows) == 8568 and sum(r["wrong"] for r in rows) == 0
    assert all(r["n"] == 16 and r["starts"] == 10 and r["checks"] == 1224 for r in rows)                  # je Netz 2 + 2 Verfahren · 10 Läufe · 5 Prüfungen


def test_balanced_halving_costs_a_multiple_of_the_minimum_cut():
    rows = cached("balance_rows")
    assert [r["label"] for r in rows] == ["Zufallsnetz, Grad 3", "Zufallsnetz, Grad 5", "Gitter", "Ring mit Abkürzungen", "Skalenfreies Netz", "Verbundnetz, Grad 5", "Kartennetz"]
    means = [r["sum_ratio"] / r["nets"] for r in rows]
    assert [round(m, 2) for m in means] == [5.0, 7.21, 2.0, 2.11, 4.08, 3.5, 2.07]
    assert (min(r["min_ratio"] for r in rows), max(r["max_ratio"] for r in rows)) == (1.0, 14.0)
    assert [r["trivial"] for r in rows] == [12, 12, 12, 12, 12, 0, 5] and sum(r["trivial"] for r in rows) == 65
    assert [r["sum_mincut"] for r in rows] == [12, 25, 24, 35, 24, 24, 25] and [r["sum_bisection"] for r in rows] == [60, 150, 48, 73, 98, 84, 45]
    assert [r["sum_opt"] for r in rows] == [32, 32, 24, 15, 71, 60, 19]                                    # Zahl der kleinsten Zweiteilungen, über je zwölf Netze


def test_one_start_often_misses_the_optimum_and_the_best_of_ten_never_does():
    rows = cached("starts_rows")
    assert [r["one"]["kl"] for r in rows] == [8, 10, 8, 11, 10, 7, 11] and sum(r["one"]["kl"] for r in rows) == 65
    assert [r["one"]["fm"] for r in rows] == [8, 7, 9, 10, 10, 7, 10] and sum(r["one"]["fm"] for r in rows) == 61
    assert all(r["best"] == {"kl": 12, "fm": 12} and r["nets"] == 12 for r in rows) and sum(r["nets"] for r in rows) == 84
    assert 84 - 65 == 19 and 84 - 61 == 23
    assert 65 / 84 == pytest.approx(0.774, abs=0.001) and 61 / 84 == pytest.approx(0.726, abs=0.001)


def test_in_the_large_network_a_single_start_stays_above_the_best_found():
    rows = cached("big_rows")
    assert all(r["n"] == 81 and r["reference"] == 20 and r["nets"] == 4 for r in rows)
    assert [r["gap_kl"] for r in rows] == [14.0, 6.0, 0.0, 6.0, 6.0, 7.0, 12.0] and sum(r["gap_kl"] for r in rows) == 51 and round(51 / 28, 1) == 1.8
    assert [r["gap_fm"] for r in rows] == [8.0, 8.0, 0.0, 1.0, 12.0, 6.0, 7.0] and sum(r["gap_fm"] for r in rows) == 42 and round(42 / 28, 1) == 1.5
    assert sum(r["evals_kl"] for r in rows) / 28 == 82820 and round(sum(r["moves_fm"] for r in rows) / 28) == 312
    assert [r["sum_ref"] for r in rows] == [57.0, 158.0, 40.0, 38.0, 120.0, 70.0, 13.0]


def test_some_spielraum_is_necessary_and_more_makes_fiduccia_mattheyses_worse():
    rows = cached("slack_rows")
    assert [r["slack"] for r in rows] == [0, 1, 2, 3, 4] and all(r["runs"] == 112 and r["n"] == 36 and r["sum_start"] == 4102 for r in rows)
    assert [r["sum_final"] for r in rows] == [4102, 1259, 1347, 1619, 1809] and [r["stuck"] for r in rows] == [112, 0, 0, 0, 0]
    assert [round(r["sum_final"] / r["runs"], 1) for r in rows] == [36.6, 11.2, 12.0, 14.5, 16.2]


def test_the_preset_descriptions_hold():
    def a(name):
        return ev.analyse(ev.Settings(**C.PRESETS[name]))
    lehr = a("Lehrbeispiel (Hantel mit Anhängsel)")
    assert (lehr.mincut, lehr.optimum, lehr.exact.count, lehr.exact.total) == (1, 2, 1, 35)
    ohne = a("Ohne Balance kein Problem")
    assert ohne.mincut == 1 and ohne.mincut_trivial and ohne.optimum == 14 and ohne.optimum > 10 * ohne.mincut
    ein = a("Ein Start verfehlt das Optimum")
    assert ein.first_cut("kl") > ein.optimum == ein.best_cut("kl") == 5
    fmp = a("Fiduccia–Mattheyses verfehlt es ebenso")
    assert fmp.first_cut("fm") > fmp.optimum == fmp.best_cut("fm") == 8
    spiel = a("Ohne Spielraum bleibt Fiduccia–Mattheyses stehen")
    assert spiel.settings.slack == 0 and all(r.passes[0].stuck and r.cut == r.start_cut for r in spiel.runs["fm"]) and spiel.best_cut("fm") > spiel.optimum
    viele = a("Viele gleich gute Zweiteilungen")
    assert viele.exact.count == 18 and viele.exact.total == 24310 and not viele.mincut_trivial
    gross = a("Großes Kartennetz")
    assert gross.n == 80 and gross.exact is None and gross.reference == 3 and gross.best_cut("kl") == 4 and len({r.cut for r in gross.runs["kl"]}) > 3
