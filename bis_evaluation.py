"""Kennzahlen, Prüfung der Ergebnisse und Verdikte. Verdikte sind reine Funktionen (Art, Text): Zahlen kommen aus den Zeilen, nie aus dem Text.

Standorte sind in der Anzeige ab 1 nummeriert (`inst.name`), im Kern ab 0 (das Lehrbeispiel hat Buchstaben)."""

import random
from dataclasses import dataclass, field

import bis_algorithm as A
import bis_constants as C
import bis_scenario as S


@dataclass(frozen=True)
class Settings:
    kind: str = C.DEFAULT_KIND
    n: int = C.DEFAULT_N
    deg: float = C.DEFAULT_DEG
    links: int = C.DEFAULT_LINKS
    seed: int = C.DEFAULT_SEED
    method: str = C.DEFAULT_METHOD
    slack: int = C.DEFAULT_SLACK
    starts: int = C.DEFAULT_STARTS


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    inst: S.Instance = field(compare=False, repr=False)
    exact: A.Exact | None = field(compare=False, repr=False)        # nur bei höchstens BRUTE_N Standorten
    mincut: int = field(compare=False)
    mincut_side: tuple = field(compare=False, repr=False)
    runs: dict = field(compare=False, repr=False)                   # {"kl": Läufe, "fm": Läufe}, gleiche Startanordnungen

    @property
    def n(self):
        return self.inst.n

    @property
    def m(self):
        return self.inst.m

    def chosen(self):
        return self.runs[self.settings.method]

    def best_run(self, method=None):
        runs = self.runs[method or self.settings.method]
        return min(runs, key=lambda r: (r.cut, runs.index(r)))

    def best_cut(self, method=None):
        return self.best_run(method).cut

    def first_cut(self, method=None):
        return self.runs[method or self.settings.method][0].cut

    @property
    def optimum(self):
        return self.exact.value if self.exact else None

    @property
    def reference(self):
        """Kleinster bekannter Schnitt einer Bisektion: das Optimum, sonst das Beste aller Läufe beider Verfahren."""
        return self.optimum if self.exact else min(r.cut for runs in self.runs.values() for r in runs)

    @property
    def mincut_trivial(self):
        return A.is_trivial(self.n, set(self.mincut_side))

    @property
    def work(self):
        return sum(r.work for r in self.chosen())


def analyse(settings: Settings) -> Analysis:
    inst = S.make_instance(settings.kind, settings.n, settings.deg, settings.links, settings.seed)
    adj = inst.adj
    exact = A.exact_bisection(adj) if inst.n <= C.BRUTE_N else None
    mc, side = A.min_cut(adj)
    runs = {m: A.multistart(m, adj, settings.starts, settings.slack, random.Random(settings.seed * 53 + C.START_SALT)) for m in C.METHODS}
    return Analysis(settings, inst, exact, mc, side, runs)


def validate(a: Analysis) -> list:
    """Unabhängige Prüfung vor der Anzeige: gibt die Liste der Probleme zurück (leer = alles in Ordnung)."""
    problems = []
    adj = a.inst.adj
    if a.exact is not None:
        if not A.is_balanced(a.exact.side) or A.cut_size(adj, a.exact.side) != a.exact.value:
            problems.append("Die Aufzählung liefert keine ausgewogene Zweiteilung mit dem gemeldeten Schnitt")
    if a.mincut > a.reference:
        problems.append("Der kleinste Schnitt ohne Balance ist größer als eine ausgewogene Zweiteilung")
    for method, runs in a.runs.items():
        name = C.METHOD_NAMES[method]
        for run in runs:
            if not A.is_balanced(run.side):
                problems.append(f"{name}: eine Zweiteilung ist nicht ausgewogen")
                break
            if run.cut != A.cut_size(adj, run.side) or run.start_cut != A.cut_size(adj, run.start):
                problems.append(f"{name}: der gemeldete Schnitt stimmt nicht mit der Nachzählung überein")
                break
            if run.cut > run.start_cut:
                problems.append(f"{name}: der Schnitt ist größer als der Start")
                break
            cut = run.start_cut
            ok = True
            for p in run.passes:
                ok = ok and p.cut_before == cut and p.cut_before - p.cut_after == p.gain
                cut = p.cut_after
            if not ok or cut != run.cut:
                problems.append(f"{name}: die Gewinne der Durchläufe stimmen nicht mit den Schnitten überein")
                break
            if a.exact is not None and run.cut < a.exact.value:
                problems.append(f"{name}: ein Lauf liegt unter dem Optimum der Aufzählung")
                break
    return problems


# --- Formate ---------------------------------------------------------------------------------------------------------------------------------------


def _i(x) -> str:
    """Ganze Zahl mit Punkt als Tausendertrenner."""
    return f"{x:,.0f}".replace(",", ".")


def _dec(x, digits=1) -> str:
    """Zahl mit Komma; ganze Werte ohne Nachkommastelle."""
    x = float(x)
    if x == int(x):
        return _i(x)
    return f"{x:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(share, digits=0) -> str:
    return _dec(round(100.0 * share, digits), digits) if digits else _i(round(100.0 * share))


def _starts(n) -> str:
    return "1 Start" if n == 1 else f"{_i(n)} Starts"


def _unit(method) -> str:
    return "Paarbewertungen" if method == "kl" else "Züge"


# --- Verdikte -------------------------------------------------------------------------------------------------------------------------------------


def verdict_question(a: Analysis):
    """Kernfrage: kleinster Schnitt ohne Balance, kleinste Bisektion und was das gewählte Verfahren findet."""
    s = a.settings
    name = C.METHOD_NAMES[s.method]
    head = (f"**Bei {_i(a.n)} Standorten kostet der kleinste Schnitt ohne Balance {_i(a.mincut)}"
            f"{' (ein einzelner Standort)' if a.mincut_trivial else ''}, die kleinste ausgewogene Zweiteilung {_i(a.reference)}"
            f"{'' if a.exact else ' (beste gefundene, ohne Aufzählung)'}.**")
    ratio = f" Ausgewogen halbieren kostet also das {_dec(a.reference / a.mincut)}-Fache." if a.mincut else ""
    first, best = a.first_cut(), a.best_cut()
    start = a.chosen()[0].start_cut
    found = (f" {name}: Der erste Start ({_i(start)} Leitungen zwischen den Hälften) endet bei {_i(first)}"
             f"{'' if not a.exact else (', dem Optimum' if first == a.optimum else f', {_i(first - a.optimum)} über dem Optimum')}; "
             f"das Beste aus {_starts(s.starts)} ist {_i(best)}{'' if not a.exact else (', das Optimum' if best == a.optimum else f', {_i(best - a.optimum)} über dem Optimum')}.")
    if a.exact:
        found += f" Es gibt {_i(a.exact.count)} {'optimale Zweiteilung' if a.exact.count == 1 else 'optimale Zweiteilungen'} unter {_i(a.exact.total)}."
    return "info", head + ratio + found


def verdict_exact(rows):
    nets, checks, wrong = (sum(r[k] for r in rows) for k in ("nets", "checks", "wrong"))
    n, starts = rows[0]["n"], rows[0]["starts"]
    if wrong:
        return "warning", f"Auf {_i(nets)} Netzen weichen {_i(wrong)} von {_i(checks)} Prüfungen von der Aufzählung ab."
    return "info", (f"Auf {_i(nets)} Netzen mit {_i(n)} Standorten ({len(rows)} Netztypen) bestehen {_i(checks)} Prüfungen: Die Aufzählung liefert eine ausgewogene Zweiteilung, und jeder der je {_i(starts)} Läufe "
                    f"beider Verfahren endet ausgewogen, mit nachgezähltem Schnitt, nie über dem Start und nie unter dem Optimum, und die Gewinne der Durchläufe sind gleich den Unterschieden der Schnitte. Abweichungen: 0.")


def verdict_balance(rows):
    nets = sum(r["nets"] for r in rows)
    mean = lambda r: r["sum_ratio"] / r["nets"]   # noqa: E731
    lo, hi = min(rows, key=mean), max(rows, key=mean)
    low, high = min(r["min_ratio"] for r in rows), max(r["max_ratio"] for r in rows)
    triv = sum(r["trivial"] for r in rows)
    text = (f"Auf {_i(nets)} Netzen ({len(rows)} Netztypen, {_i(rows[0]['n'])} Standorte) kostet die kleinste ausgewogene Zweiteilung im Mittel je Netztyp das {_dec(mean(lo))}-Fache ({lo['label']}) bis "
            f"{_dec(mean(hi))}-Fache ({hi['label']}) des kleinsten Schnitts ohne Balance; im einzelnen Netz das {_dec(low)}- bis {_dec(high)}-Fache. Der kleinste Schnitt trennt in {_i(triv)} von {_i(nets)} Netzen "
            f"nur einen einzelnen Standort ab.")
    return "info", text


def verdict_starts(rows):
    nets = sum(r["nets"] for r in rows)
    one = {m: sum(r["one"][m] for r in rows) for m in C.METHODS}
    best = {m: sum(r["best"][m] for r in rows) for m in C.METHODS}
    starts = rows[0]["starts"]
    text = (f"Mit einem Start treffen Kernighan–Lin in {_i(one['kl'])} und Fiduccia–Mattheyses in {_i(one['fm'])} von {_i(nets)} Netzen das Optimum; mit dem Besten aus {_i(starts)} Starts "
            f"{_i(best['kl'])} bzw. {_i(best['fm'])}.")
    worst = min(rows, key=lambda r: min(r["one"].values()))
    text += f" Am häufigsten verfehlt ein Start das Optimum im Netztyp {worst['label']} ({_i(worst['nets'] - min(worst['one'].values()))} von {_i(worst['nets'])} Netzen bei {C.METHOD_NAMES['kl' if worst['one']['kl'] < worst['one']['fm'] else 'fm'].split(' ')[0]})."
    bad = nets * 2 - best["kl"] - best["fm"]
    return ("warning" if bad else "info"), text if not bad else text + f" In {_i(bad)} {'Fall' if bad == 1 else 'Fällen'} blieb auch das Beste aus {_starts(starts)} über dem Optimum."


def verdict_big(rows):
    n, ref = rows[0]["n"], rows[0]["reference"]
    nets = sum(r["nets"] for r in rows)
    gap_kl = sum(r["gap_kl"] for r in rows) / nets
    gap_fm = sum(r["gap_fm"] for r in rows) / nets
    evals = sum(r["evals_kl"] for r in rows) / nets
    moves = sum(r["moves_fm"] for r in rows) / nets
    text = (f"Bei {_i(n)} Standorten liegt ein Start im Mittel um {_dec(gap_kl)} (Kernighan–Lin) bzw. {_dec(gap_fm)} (Fiduccia–Mattheyses) Leitungen über der besten gefundenen Zweiteilung (aus {_i(ref)} Starts "
            f"von Fiduccia–Mattheyses und einem von Kernighan–Lin; {_i(nets)} Netze). Ein Start von Kernighan–Lin braucht im Mittel {_i(evals)} Paarbewertungen, einer von Fiduccia–Mattheyses {_i(moves)} Züge; "
            f"die Einheiten sind verschieden.")
    return "info", text


def verdict_slack(rows):
    by = {r["slack"]: r for r in rows}
    mean = lambda r: r["sum_final"] / r["runs"]   # noqa: E731
    best = min(rows, key=mean)
    zero = by.get(0)
    text = (f"Bei {_i(rows[0]['n'])} Standorten mit Fiduccia–Mattheyses endet ein Lauf im Mittel bei " + ", ".join(f"{_dec(mean(r))} (Spielraum {_i(r['slack'])})" for r in rows)
            + f"; der Start liegt im Mittel bei {_dec(rows[0]['sum_start'] / rows[0]['runs'])}.")
    if zero:
        text += f" Ohne Spielraum war in {_i(zero['stuck'])} von {_i(zero['runs'])} Läufen jeder Zug blockiert."
    text += f" Am besten ist der Spielraum {_i(best['slack'])}."
    return "info", text
