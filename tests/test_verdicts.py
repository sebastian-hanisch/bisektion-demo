"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Seeds; so prüft der Test Grenzen und jede genannte Zahl direkt."""

import dataclasses

import bis_constants as C
import bis_evaluation as ev


def test_formats():
    assert ev._i(1234567) == "1.234.567" and ev._i(7) == "7"
    assert ev._dec(3.0) == "3" and ev._dec(1234.5) == "1.234,5" and ev._dec(0.75) == "0,8" and ev._dec(2.25, 2) == "2,25"
    assert ev._pct(0.256) == "26" and ev._pct(0.256, 1) == "25,6"
    assert ev._unit("kl") == "Paarbewertungen" and ev._unit("fm") == "Züge"
    assert ev._starts(1) == "1 Start" and ev._starts(10) == "10 Starts" and ev._starts(1000) == "1.000 Starts"


def test_verdict_exact_counts_and_warns_on_any_deviation():
    rows = [{"nets": 3, "checks": 30, "wrong": 0, "n": 8, "starts": 4}, {"nets": 2, "checks": 2000, "wrong": 0, "n": 8, "starts": 4}]
    kind, text = ev.verdict_exact(rows)
    assert kind == "info" and text.startswith("Auf 5 Netzen mit 8 Standorten (2 Netztypen) bestehen 2.030 Prüfungen:") and "je 4 Läufe" in text and text.endswith("Abweichungen: 0.")
    rows[1]["wrong"] = 1
    rows[0]["wrong"] = 2
    assert ev.verdict_exact(rows) == ("warning", "Auf 5 Netzen weichen 3 von 2.030 Prüfungen von der Aufzählung ab.")


def test_verdict_balance_names_the_cheapest_and_the_dearest_net_type():
    rows = [{"label": "A", "nets": 2, "sum_ratio": 6.0, "min_ratio": 2.0, "max_ratio": 4.0, "trivial": 2, "n": 8},
            {"label": "B", "nets": 2, "sum_ratio": 9.0, "min_ratio": 3.0, "max_ratio": 6.5, "trivial": 0, "n": 8}]
    kind, text = ev.verdict_balance(rows)
    assert kind == "info"
    assert text == ("Auf 4 Netzen (2 Netztypen, 8 Standorte) kostet die kleinste ausgewogene Zweiteilung im Mittel je Netztyp das 3-Fache (A) bis 4,5-Fache (B) des kleinsten Schnitts ohne Balance; "
                    "im einzelnen Netz das 2- bis 6,5-Fache. In 2 von 4 Netzen ist ein kleinster Schnitt ein einzelner Standort.")
    rows.reverse()
    assert "das 3-Fache (A) bis 4,5-Fache (B)" in ev.verdict_balance(rows)[1]                    # unabhängig von der Reihenfolge


def test_verdict_starts_counts_hits_names_the_worst_type_and_warns_on_a_miss():
    rows = [{"label": "A", "nets": 4, "one": {"kl": 3, "fm": 1}, "best": {"kl": 4, "fm": 4}, "starts": 3, "n": 8},
            {"label": "B", "nets": 4, "one": {"kl": 2, "fm": 4}, "best": {"kl": 4, "fm": 3}, "starts": 3, "n": 8}]
    kind, text = ev.verdict_starts(rows)
    assert kind == "warning"
    assert text == ("Mit einem Start treffen Kernighan–Lin in 5 und Fiduccia–Mattheyses in 5 von 8 Netzen das Optimum; mit dem Besten aus 3 Starts 8 bzw. 7. "
                    "Am häufigsten verfehlt ein Start das Optimum im Netztyp A (3 von 4 Netzen bei Fiduccia–Mattheyses). In 1 Fall blieb auch das Beste aus 3 Starts über dem Optimum.")
    rows[1]["best"]["kl"] = 3
    assert ev.verdict_starts(rows)[1].endswith("In 2 Fällen blieb auch das Beste aus 3 Starts über dem Optimum.")
    rows[1]["best"] = {"kl": 4, "fm": 4}
    kind, text = ev.verdict_starts(rows)
    assert kind == "info" and "Fall" not in text and text.endswith("bei Fiduccia–Mattheyses).")


def test_verdict_starts_names_kernighan_lin_when_it_misses_more():
    rows = [{"label": "A", "nets": 4, "one": {"kl": 1, "fm": 3}, "best": {"kl": 4, "fm": 4}, "starts": 3, "n": 8}]
    assert "im Netztyp A (3 von 4 Netzen bei Kernighan–Lin)" in ev.verdict_starts(rows)[1]


def test_verdict_big_gives_the_means_per_net_and_the_units():
    rows = [{"nets": 2, "gap_kl": 3.0, "gap_fm": 5.0, "evals_kl": 2000.0, "moves_fm": 100.0, "n": 20, "reference": 5},
            {"nets": 2, "gap_kl": 3.0, "gap_fm": 3.0, "evals_kl": 1000.0, "moves_fm": 60.0, "n": 20, "reference": 5}]
    kind, text = ev.verdict_big(rows)
    assert kind == "info"
    assert text == ("Bei 20 Standorten liegt ein Start im Mittel um 1,5 (Kernighan–Lin) bzw. 2 (Fiduccia–Mattheyses) Leitungen über der besten gefundenen Zweiteilung (aus 5 Starts "
                    "von Fiduccia–Mattheyses und einem von Kernighan–Lin; 4 Netze). Ein Start von Kernighan–Lin braucht im Mittel 750 Paarbewertungen, einer von Fiduccia–Mattheyses 40 Züge; die Einheiten sind verschieden.")


def test_verdict_slack_lists_every_slack_and_names_the_best():
    rows = [{"slack": 0, "runs": 4, "sum_start": 40, "sum_final": 40, "stuck": 4, "n": 10}, {"slack": 1, "runs": 4, "sum_start": 40, "sum_final": 20, "stuck": 0, "n": 10},
            {"slack": 2, "runs": 4, "sum_start": 40, "sum_final": 26, "stuck": 0, "n": 10}]
    kind, text = ev.verdict_slack(rows)
    assert kind == "info"
    assert text == ("Bei 10 Standorten mit Fiduccia–Mattheyses endet ein Lauf im Mittel bei 10 (Spielraum 0), 5 (Spielraum 1), 6,5 (Spielraum 2); der Start liegt im Mittel bei 10. "
                    "Ohne Spielraum war in 4 von 4 Läufen jeder Zug blockiert. Im Mittel über alle Läufe ist der Spielraum 1 am besten.")
    no_zero = ev.verdict_slack(rows[1:])[1]
    assert "Ohne Spielraum" not in no_zero and no_zero.endswith("Im Mittel über alle Läufe ist der Spielraum 1 am besten.")
    rows[2]["sum_final"] = 12                                                                  # mittlerer Endwert 3: Spielraum 2 ist jetzt am besten
    assert ev.verdict_slack(rows)[1].endswith("Im Mittel über alle Läufe ist der Spielraum 2 am besten.")


def test_verdict_question_for_the_textbook_network_by_hand():
    a = ev.analyse(ev.Settings())
    kind, text = ev.verdict_question(a)
    assert kind == "info"
    assert text == ("**Bei 8 Standorten kostet der kleinste Schnitt ohne Balance 1 (ein einzelner Standort), die kleinste ausgewogene Zweiteilung 2.** Ausgewogen halbieren kostet also das 2-Fache. "
                    "Kernighan–Lin (Paartausch): Der erste Start (8 Leitungen zwischen den Hälften) endet bei 2, dem Optimum; das Beste aus 10 Starts ist 2, das Optimum. Es gibt 1 optimale Zweiteilung unter 35.")


def test_verdict_question_branches():
    first = ev.analyse(ev.Settings(**C.PRESETS["Ein Start verfehlt das Optimum"]))
    text = ev.verdict_question(first)[1]
    assert "endet bei 7, 2 über dem Optimum; das Beste aus 10 Starts ist 5, das Optimum." in text and "Es gibt 2 optimale Zweiteilungen unter 24.310." in text
    assert ev.verdict_question(dataclasses.replace(first, settings=dataclasses.replace(first.settings, starts=1)))[1].count("das Beste aus 1 Start ist") == 1
    big = ev.analyse(ev.Settings(**C.PRESETS["Großes Kartennetz"]))
    text = ev.verdict_question(big)[1]
    assert "die kleinste ausgewogene Zweiteilung 3 (beste gefundene, ohne Aufzählung).**" in text and "ein einzelner Standort" not in text and "Optimum" not in text and "optimale" not in text
    many = ev.analyse(ev.Settings(**C.PRESETS["Viele gleich gute Zweiteilungen"]))
    assert "Es gibt 18 optimale Zweiteilungen unter 24.310." in ev.verdict_question(many)[1] and "das 5-Fache" in ev.verdict_question(many)[1]
