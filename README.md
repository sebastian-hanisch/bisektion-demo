# Ausgewogen halbieren: Kernighan–Lin und Fiduccia–Mattheyses – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-bisektion-demo.streamlit.app/)**

Fünftes Stück der Reihe **Schnitte und Zusammenhang** (Arbeitstitel der Linie `schnitte-zusammenhang`) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“, Bereich Graphentheorie. Vehikel: ein **Verbindungsnetz zwischen Standorten** (Depots, Umschlagpunkte, Werke), synthetisch und mit festem Zufalls-Seed, alle Leitungen gleich. Die Demo fragt: **Wie teilt man das Netz in zwei gleich große Hälften, zwischen denen möglichst wenige Leitungen liegen, und warum muss man „gleich groß“ verlangen?** Zwei klassische Verbesserungsverfahren starten von einer zufälligen Anordnung: **Kernighan–Lin** tauscht Paare aus beiden Hälften, **Fiduccia–Mattheyses** verschiebt einzelne Standorte und lässt die Hälften dabei kurz ungleich groß werden (Spielraum).

Nachbarn: den kleinsten Schnitt ohne Balance zeigt `globaler-schnitt-demo`, den Zusammenhang über disjunkte Wege `menger-demo`; Kernighan–Lin als eines von drei Verfahren in der Auftragsbündelung `order-batching-demo`; Knotentrennmengen in planaren Graphen `planar-separator-demo`.

## Warum dieses Problem

Der kleinste Schnitt eines Netzes trennt auf den Modellnetzen meist nur **einen einzelnen Standort** ab und sagt wenig über eine sinnvolle Teilung. Wer ein Netz in zwei Gebiete, zwei Rechenknoten oder zwei Schichten teilen will, braucht eine Bedingung an die Größe der Hälften, und mit ihr wird das Problem schwer (die minimale Bisektion ist NP-schwer). Die Demo zeigt, **was die Balance kostet** (das Mehrfache des kleinsten Schnitts), **wie die beiden Verfahren Schritt für Schritt vorgehen** (Gewinnfolge, gesperrte Standorte, bester Präfix), **dass ein Start oft nicht das Optimum trifft, mehrere Starts es aber auf allen gemessenen Netzen treffen**, und dass **mehr Spielraum die Ergebnisse von Fiduccia–Mattheyses verschlechtert**, kein Spielraum aber jeden Zug blockiert.

## Befunde und Korrekturen gegenüber dem Plan

- **Hook ist die Balance, nicht der Verfahrensvergleich:** Der Plan sah vorab, dass zehn Starts das Optimum fast immer treffen; das bestätigt sich (84 von 84 Netzen, siehe Tabelle). Die Aussage der Demo ist deshalb nicht „welches Verfahren ist besser“ (die Zahlen unterscheiden sich kaum und wechseln mit dem Netztyp), sondern die Kosten der Balance und die Abhängigkeit vom Start.
- **Die Vormessungszahlen gelten nicht:** „76 von 96 (Kernighan–Lin) und 75 von 96 (Fiduccia–Mattheyses) mit einem Start“, „Bisektion 2- bis 6-fach so teuer“ stammen aus Wegwerfskripten mit anderen Netzen und Größen (17 und 18 Standorte, Delaunay-Karte). Die Demo misst neu (Tabelle unten): **65 bzw. 61 von 84** Netzen mit einem Start, die Bisektion **1- bis 14-fach** so teuer wie der kleinste Schnitt.
- **Kartennetz statt Delaunay:** Das Straßennetz im Kleinen entsteht aus zufälligen Punkten, jeder mit seinen drei nächsten Nachbarn verbunden (zusammenhängend gemacht), nicht aus einer Delaunay-Triangulierung.
- **Spielraum 1 als Voreinstellung:** In der Vormessung blockierte bei strikter Gleichheit jeder Zug von Fiduccia–Mattheyses. Die Demo zeigt das als eigenes Preset („Ohne Spielraum bleibt Fiduccia–Mattheyses stehen“) und rechnet sonst mit Spielraum 1 (Experiment 5 zeigt, dass mehr Spielraum schlechter ist).
- **Mehrstufig und Hypergraph nicht hier:** Das mehrstufige Verfahren (METIS-Stil) ist Stück 6 der Linie; hier nur die beiden Verbesserungsverfahren.

## Modell

Ein einfaches, **zusammenhängendes** Netz mit n Standorten (Zufallsnetz: Zufallsbaum plus Leitungen bis zum mittleren Grad; Gitter, Ring mit Abkürzungen, skalenfreies Netz nach bevorzugter Anbindung, Verbundnetz mit drei Regionen und einstellbar vielen Leitungen dazwischen, Kartennetz) und das handgebaute **Lehrbeispiel Hantel mit Anhängsel**: Werk 1 (A, B, C, D) und Werk 2 (E, F, G) sind je ein vollständiges Netz, dazu die Leitung D–E und der Standort H nur an A. Von Hand: der kleinste Schnitt ohne Balance ist **1** (H allein oder die Leitung D–E), die kleinste **Bisektion** (4 gegen 4) ist **2** ({A, B, C, D} gegen {E, F, G, H}: D–E und A–H). Das Gitter hat Quadratzahl viele Standorte (n wird gerundet). Der Zufall kommt nur aus `random.Random(seed)` mit `random()` (plattformstabil); die Startanordnungen haben eine eigene Zufallsquelle, getrennt von der des Netzes. Details und Formeln: Expander „📐 Mathematische Formulierung“ in der App.

## Methodik

- **Kernighan–Lin:** Ein Durchlauf wählt wiederholt das Paar (a, b) aus beiden Hälften mit dem größten Tauschgewinn D(a) + D(b) − 2 · [a, b verbunden], sperrt beide und aktualisiert die Gewinne der übrigen. Vom Anfang der Gewinnfolge wird der **beste Präfix** ausgeführt, wenn seine Summe positiv ist; Durchläufe wiederholen sich, bis keiner mehr gewinnt. Aufwand in **Paarbewertungen** (jedes angesehene Paar).
- **Fiduccia–Mattheyses:** Ein Durchlauf verschiebt wiederholt den freien Standort mit dem größten Gewinn (bei Gleichstand der kleinste), sperrt ihn und darf die Hälften verschieden groß werden lassen (Spielraum s). Ausgeführt wird der beste Präfix unter den wieder ausgewogenen Zuständen. Aufwand in **Zügen**. Ohne Spielraum (s = 0) ist bei gerader Standortzahl jeder Zug blockiert.
- **Mehrere Starts:** unabhängige zufällige Anordnungen in zwei Hälften; beide Verfahren laufen von **denselben** Startanordnungen.
- **Aufzählung:** alle Zweiteilungen in Hälften der Größe ⌊n/2⌋ und ⌈n/2⌉ (bis 20 Standorte): kleinster Schnitt, Zahl der kleinsten, Zahl aller. Der **kleinste Schnitt ohne Balance** kommt aus Stoer–Wagner (siehe `globaler-schnitt-demo`).
- **Unabhängige Prüfer:** Die App prüft jedes Ergebnis vor der Anzeige (jede Zweiteilung ausgewogen, der gemeldete Schnitt gleich der Nachzählung, nie über dem Start, die Gewinne der Durchläufe gleich den Unterschieden der Schnitte, bei höchstens 20 Standorten nie unter dem Optimum der Aufzählung).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py`; Zähler über feste Netze (je Netztyp zwölf Netze mit 16 Standorten, feste Zufalls-Seeds), nie ein einzelner Zufalls-Seed. Netztypen: Zufallsnetz mit mittlerem Grad 3 und 5, Gitter, Ring mit Abkürzungen, skalenfreies Netz, Verbundnetz (mittlerer Grad 5, eine Leitung zwischen je zwei Regionen), Kartennetz. Aufwand in Paarbewertungen (Kernighan–Lin) und Zügen (Fiduccia–Mattheyses), nicht in Sekunden.

| Frage | Befund |
|---|---|
| Stimmen die Verfahren mit der Aufzählung aller Bisektionen überein? | Auf **84** Netzen (sieben Netztypen, je zwölf) bestehen **8.568** Prüfungen: Die Aufzählung liefert eine ausgewogene Zweiteilung, und jeder der je 10 Läufe beider Verfahren endet ausgewogen, mit nachgezähltem Schnitt, nie über dem Start und nie unter dem Optimum; die Gewinne der Durchläufe sind gleich den Unterschieden der Schnitte. Abweichungen: **0**. |
| Wie viel teurer ist die ausgewogene Zweiteilung als der kleinste Schnitt? | Mittel je Netztyp das **2,0-Fache** (Gitter), **2,1** (Ring, Kartennetz), **3,5** (Verbundnetz), **4,1** (skalenfrei), **5,0** (Zufallsnetz Grad 3), **7,2** (Zufallsnetz Grad 5); im einzelnen Netz das **1,0-** (Kartennetz) bis **14-Fache** (Zufallsnetz Grad 5). |
| Wie oft trennt der kleinste Schnitt nur einen Standort ab? | In **65 von 84** Netzen: in **12 von 12** bei Zufallsnetz (Grad 3 und 5), Gitter, Ring und skalenfreiem Netz, in **5 von 12** beim Kartennetz und in **0 von 12** im Verbundnetz. |
| Wie viele kleinste Zweiteilungen gibt es? | Summe über je zwölf Netze: **32** (Zufallsnetz Grad 3 und 5), **24** (Gitter), **15** (Ring), **71** (skalenfrei), **60** (Verbundnetz), **19** (Kartennetz). |
| Wie oft trifft ein Start das Optimum? | Mit **einem** Start trifft Kernighan–Lin in **65 von 84** Netzen (77 %), Fiduccia–Mattheyses in **61 von 84** (73 %) das Optimum; je Netztyp Kernighan–Lin zwischen 7 und 11 von 12, Fiduccia–Mattheyses zwischen 7 und 10 von 12. Mit dem **Besten aus 10 Starts** treffen beide in **84 von 84** Netzen das Optimum. |
| Wie weit liegt ein Start im großen Netz von der besten gefundenen Lösung? | Bei **81** Standorten (keine Aufzählung; Referenz: das Beste aus 20 Starts von Fiduccia–Mattheyses und einem von Kernighan–Lin; vier Netze je Typ, 28 insgesamt) liegt ein Start im Mittel **1,8** (Kernighan–Lin) bzw. **1,5** (Fiduccia–Mattheyses) Leitungen darüber; im Gitter bei beiden **0**. Ein Start von Kernighan–Lin braucht im Mittel **82.820** Paarbewertungen, einer von Fiduccia–Mattheyses **312** Züge: verschiedene Einheiten, verglichen wird nicht. |
| Was bringt der Spielraum der Balance? | Fiduccia–Mattheyses bei **36** Standorten (sieben Netztypen, vier Netze je Typ, vier Starts, 112 Läufe je Spielraum): mittlerer Schnitt am Ende **36,6** (Spielraum 0; gleich dem Start, **in 112 von 112 Läufen war jeder Zug blockiert**), **11,2** (1), **12,0** (2), **14,5** (3), **16,2** (4). Spielraum 1 ist am besten. |
| Das Lehrbeispiel von Hand? | Hantel mit Anhängsel, 8 Standorte, 11 Leitungen: kleinster Schnitt **1**, kleinste Bisektion **2**, genau **eine** von **35** Bisektionen; beide Verfahren treffen sie mit jedem der 10 Starts. |
| Sind die Preset-Beschreibungen belegt? | Ja, jedes Preset in `tests/test_claims.py` (z. B. „Ohne Balance kein Problem“: kleinster Schnitt 1, kleinste Bisektion 14 bei 18 Standorten; „Viele gleich gute Zweiteilungen“: 18 von 24.310). |
| Ist die Rechnung korrekt? | Kleinste Bisektion, Zahl der kleinsten und Zahl aller gleich einer **unabhängigen Aufzählung** (`itertools.combinations`) auf 24 festen Netzen; kleinster Schnitt gleich `networkx.edge_connectivity` auf 36 Netzen und gleich dem kleinsten Schnitt über alle Teilmengen auf kleinen Zufallsnetzen; jeder Durchlauf von Kernighan–Lin und Fiduccia–Mattheyses Zug für Zug nachgespielt (Gewinn gleich Unterschied der Nachzählung, Hälften im Spielraum, jeder Standort einmal bewegt); die Bisektion von `networkx.kernighan_lin_bisection` ausgewogen und nie unter dem Optimum (`tests/test_oracle_bisektion.py`). |

## Ehrliche Grenzen

- **Die Verfahren sind lokal.** Beide bleiben in einem lokalen Optimum stehen; ein einzelner Start verfehlt das Optimum in 19 von 84 Netzen (Kernighan–Lin) bzw. 23 von 84 (Fiduccia–Mattheyses). Dass das Beste aus zehn Starts auf **allen 84** Netzen traf, gilt für Netze mit 16 Standorten, nicht für große.
- **Verfahrensvergleich nicht belastbar:** Kernighan–Lin und Fiduccia–Mattheyses liegen auf diesen Netzen nahe beieinander und wechseln die Reihenfolge je Netztyp; die Demo behauptet keinen Sieger. Im großen Netz sind vier Netze je Typ eine kleine Stichprobe.
- **Die Referenz im großen Netz ist nur die beste gefundene** Lösung; ob sie optimal ist, wissen wir nicht (keine Aufzählung über 20 Standorte).
- **Einfache Formen:** Kernighan–Lin mit Paarsuche über alle Paare (ohne Beschleunigung), Fiduccia–Mattheyses ohne Gewinn-Fächer (lineare Laufzeit der Originalarbeit). Mehrstufige Verfahren (METIS) und Hypergraphen sind nicht Teil dieses Stücks.
- **Gleiche Leitungen, gleich große Hälften:** Keine Gewichte, keine Lasten, nur zwei Teile; die Hälften müssen nicht zusammenhängen.
- **Der Spielraum 1 ist auf diesen Netzen gemessen am besten**; die Messung zeigt nicht, dass das für jedes Netz gilt.
- **Aufwand gezählt, nicht gemessen.** Paarbewertungen und Züge sind verschiedene Einheiten; ein Vergleich in Sekunden fehlt bewusst.
- **Größe:** bis 120 Standorte, die Aufzählung bis 20.

## Tests

Das Verzeichnis `tests/` enthält zurzeit 109 Tests (Laufzeit etwa 40 Sekunden auf dem Entwicklungsrechner):

- **Kern** (`test_algorithm.py`): jede Einheit an von Hand gerechneten Mini-Netzen (zwei Dreiecke, Kreis, Pfad, vollständiges Netz, Stern, Hantel): Gewinne, Kernighan–Lin Paar für Paar (Gewinnfolge, bester Präfix, Paarbewertungen), Fiduccia–Mattheyses Zug für Zug mit und ohne Spielraum, Aufzählung, kleinster Schnitt.
- **Szenarien** (`test_scenario.py`): einfach, zusammenhängend, deterministisch für jeden Netztyp; Größen (Gitter, skalenfreies Netz, Regionen, Lehrbeispiel).
- **Orakel** (`test_oracle_bisektion.py`): unabhängige Aufzählung, `networkx.edge_connectivity`, Schnitt über alle Teilmengen, Durchläufe nachgespielt, `networkx.kernighan_lin_bisection`.
- **Randfälle** (`test_edge_cases.py`): zwei und vier Standorte, Netz ohne Leitungen, Durchlaufgrenze, ungerade Standortzahl, jede Art von Prüffehler an verfälschten Analysen, Reglergrenzen.
- **Zweige, Verdikte, Befunde** (`test_branches.py`, `test_verdicts.py`, `test_claims.py`): jedes Preset löst seine Beschreibung ein und jede Abbildung rendert; jedes Verdikt an handgesetzten Zeilen; jede Zahl dieses README.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler am Minimum und Maximum), Layout (Schnellstart oben, aktives Preset hervorgehoben), Footer, Laufzeit-Importe.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: ein Durchlauf (Schritt für Schritt), Mehrfachstarts, kleinster Schnitt und Balance, fünf Experimente |
| `requirements-dev.txt` | Laufzeit plus pytest und networkx (Gegenproben) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `bis_algorithm.py` | Kern: Gewinne, Kernighan–Lin, Fiduccia–Mattheyses, Mehrfachstarts, Aufzählung, kleinster Schnitt |
| `bis_constants.py` | Regler-Grenzen, Netztypen, Raster der Experimente, Farben, Presets |
| `bis_evaluation.py` | Analyse, Prüfung vor der Anzeige, Verdikte |
| `bis_experiments.py` | Experimente über feste Netze |
| `bis_layout.py` | Fester Kopf (Stylesheet) |
| `bis_presets.py` | Permalink, Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `bis_scenario.py` | Netze: Lehrbeispiel, Zufallsnetz, Gitter, Ring, skalenfreies Netz, Verbundnetz, Kartennetz |
| `bis_visualization.py` | Plotly-Abbildungen (Karten mit Hälften und Schnitt, Gewinnfolgen, Starts, Experimente; Achsen gesperrt) |
| `tests/` | Mini-Netze, Orakel, Randfälle, Zweige, Verdikte, Befunde, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Mehrstufige Verfahren (METIS-Stil), Hypergraphen, gewichtete Standorte, mehr als zwei Teile:** nur als Einordnung; das mehrstufige Verfahren ist ein eigenes Stück der Linie.
- **Spektrale Verfahren:** eigenes Stück der Linie (spektrale Schnitte).
- **Echte Netze oder Dateiimport:** die Netze sind synthetisch.
- **Messung der Laufzeit:** gezählt werden Paarbewertungen und Züge.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und pandas.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
