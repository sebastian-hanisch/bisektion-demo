"""Konstanten: Regler-Grenzen, feste Annahmen, Experiment-Raster, Farben und Presets."""

KINDS = ("textbook", "random", "grid", "ring", "scalefree", "verbund", "geometric")
KIND_NAMES = {"textbook": "Lehrbeispiel (Hantel mit Anhängsel)", "random": "Zufallsnetz", "grid": "Gitter", "ring": "Ring mit Abkürzungen", "scalefree": "Skalenfreies Netz", "verbund": "Verbundnetz",
              "geometric": "Kartennetz"}
KIND_HELP = {
    "textbook": "Acht Standorte, von Hand zu rechnen: zwei Werke, ein Verbindungsstück und ein Standort am Rand.",
    "random": "Zufallsbaum plus zufällige Leitungen; der mittlere Grad ist einstellbar.",
    "grid": "Standorte auf einem Raster, Verbindungen zu den vier Nachbarn.",
    "ring": "Vier nächste Nachbarn auf einem Ring, ein Zehntel der Leitungen führt zu einem zufälligen Standort.",
    "scalefree": "Neue Standorte hängen sich bevorzugt an gut vernetzte an (je zwei Leitungen).",
    "verbund": "Drei Regionen mit dichten inneren Verbindungen und wenigen Leitungen dazwischen (einstellbar).",
    "geometric": "Zufällige Punkte in einem Quadrat, jeder mit seinen drei nächsten Nachbarn verbunden: ein Straßennetz im Kleinen.",
}
KIND_REGLER = {
    "textbook": "Das Lehrbeispiel ist fest: Größe, Grad, Leitungen und Zufalls-Seed des Netzes wirken hier nicht (Startanordnungen und Verfahren schon).",
    "random": "Wirksam: Standorte, mittlerer Grad, Zufalls-Seed.",
    "grid": "Wirksam: Standorte (gerundet auf ein Quadrat). Grad, Leitungen und Zufalls-Seed des Netzes wirken nicht.",
    "ring": "Wirksam: Standorte, Zufalls-Seed.",
    "scalefree": "Wirksam: Standorte, Zufalls-Seed.",
    "verbund": "Wirksam: Standorte, mittlerer Grad (in den Regionen), Leitungen zwischen den Regionen, Zufalls-Seed.",
    "geometric": "Wirksam: Standorte, Zufalls-Seed.",
}
METHODS = ("kl", "fm")
METHOD_NAMES = {"kl": "Kernighan–Lin (Paartausch)", "fm": "Fiduccia–Mattheyses (Einzelzug)"}

N_MIN, N_MAX, DEFAULT_N = 8, 120, 24
DEG_MIN, DEG_MAX, DEFAULT_DEG = 2.0, 10.0, 4.0
LINKS_MIN, LINKS_MAX, DEFAULT_LINKS = 1, 8, 2
SLACK_MIN, SLACK_MAX, DEFAULT_SLACK = 0, 6, 1
STARTS = (1, 3, 10, 30)
DEFAULT_STARTS = 10
SEED_MAX, DEFAULT_SEED = 999999, 7
DEFAULT_KIND, DEFAULT_METHOD = "textbook", "kl"
REGIONS = 3
RING_NEIGHBOURS, RING_REWIRE = 4, 0.1
SCALEFREE_M = 2
BRUTE_N = 20                             # größte Netzgröße für die Aufzählung aller Bisektionen (App, Test, Experimente)
MAX_PASSES = 50
START_SALT = 4242                        # Zufallsquelle der Startanordnungen: getrennt von der des Netzes

SWEEP_SEEDS = tuple(range(100000, 100012))   # feste Netze für alle Experimente: nie ein einzelner Zufalls-Seed als Befund
EX_N = 16                                # Quadratzahl: das Gitter hat dieselbe Größe wie die anderen Netztypen
EX_KINDS = (("random", 3.0), ("random", 5.0), ("grid", 0.0), ("ring", 0.0), ("scalefree", 0.0), ("verbund", 5.0), ("geometric", 0.0))
EX_STARTS = 10
EX_BIG_N = 81
EX_BIG_SEEDS = 4
EX_BIG_REFERENCE = 20                    # FM-Starts für die beste gefundene Bisektion im großen Netz
EX_SLACK_N = 36
EX_SLACK_SEEDS = 4
EX_SLACK_STARTS = 4

COLOR_SIDE_A = "#2F6B65"
COLOR_SIDE_B = "#4c78a8"
COLOR_CUT = "#d1495b"
COLOR_NODE = "#c9d1d3"
COLOR_EDGE = "rgba(150,150,150,0.45)"
COLOR_BAR = "#4c78a8"
COLOR_BAR2 = "#e8a33d"
COLOR_BAR3 = "#2F6B65"
COLOR_LOCK = "#8d6cab"

PRESETS = {
    "Lehrbeispiel (Hantel mit Anhängsel)": {"kind": "textbook", "n": DEFAULT_N, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "seed": DEFAULT_SEED, "method": "kl", "slack": DEFAULT_SLACK, "starts": DEFAULT_STARTS},
    "Ohne Balance kein Problem": {"kind": "random", "n": 18, "deg": 5.0, "links": DEFAULT_LINKS, "seed": 100001, "method": "kl", "slack": DEFAULT_SLACK, "starts": DEFAULT_STARTS},
    "Ein Start verfehlt das Optimum": {"kind": "random", "n": 18, "deg": 3.0, "links": DEFAULT_LINKS, "seed": 2, "method": "kl", "slack": DEFAULT_SLACK, "starts": DEFAULT_STARTS},
    "Fiduccia–Mattheyses verfehlt es ebenso": {"kind": "scalefree", "n": 18, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "seed": 3, "method": "fm", "slack": DEFAULT_SLACK, "starts": DEFAULT_STARTS},
    "Ohne Spielraum bleibt Fiduccia–Mattheyses stehen": {"kind": "grid", "n": 16, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "seed": 3, "method": "fm", "slack": 0, "starts": DEFAULT_STARTS},
    "Viele gleich gute Zweiteilungen": {"kind": "verbund", "n": 18, "deg": 5.0, "links": 1, "seed": 1, "method": "kl", "slack": DEFAULT_SLACK, "starts": DEFAULT_STARTS},
    "Großes Kartennetz": {"kind": "geometric", "n": 80, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "seed": 5, "method": "kl", "slack": DEFAULT_SLACK, "starts": 10},
}
PRESET_HELP = {
    "Lehrbeispiel (Hantel mit Anhängsel)": "Der kleinste Schnitt ist 1 (ein Standort allein oder das Verbindungsstück), die kleinste Zweiteilung 4 gegen 4 kostet 2 (von Hand zu prüfen).",
    "Ohne Balance kein Problem": "Der kleinste Schnitt trennt nur einen einzelnen Standort ab und kostet 1; die kleinste ausgewogene Zweiteilung kostet mehr als das Zehnfache.",
    "Ein Start verfehlt das Optimum": "Von einer zufälligen Anordnung aus bleibt Kernighan–Lin in einem Zustand stehen, der nicht optimal ist; das Beste aus zehn Starts findet das Optimum.",
    "Fiduccia–Mattheyses verfehlt es ebenso": "Auch der Einzelzug bleibt bei einem Start über dem Optimum; das Beste aus zehn Starts trifft es.",
    "Ohne Spielraum bleibt Fiduccia–Mattheyses stehen": "Bei gerader Standortzahl und Spielraum 0 ist jeder Einzelzug blockiert: Der Durchlauf bewegt nichts, die Startanordnung bleibt.",
    "Viele gleich gute Zweiteilungen": "Drei Regionen mit nur einer Leitung zwischen je zwei Regionen: Es gibt viele gleich gute ausgewogene Zweiteilungen, die Aufzählung zählt sie.",
    "Großes Kartennetz": "80 Standorte, keine Aufzählung mehr möglich: Die Hälften zeigen sich auf der Karte, die Läufe streuen.",
}
