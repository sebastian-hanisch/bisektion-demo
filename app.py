"""Ausgewogen halbieren: Kernighan–Lin und Fiduccia–Mattheyses - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Fünftes Stück der Reihe „Schnitte und Zusammenhang“: Wie teilt man ein Netz in zwei gleich große Hälften mit wenig Schnitt? Kernighan–Lin (Paartausch) gegen Fiduccia–Mattheyses (Einzelzug mit Spielraum der Balance),
Mehrfachstarts, die Aufzählung als Optimum und der kleinste Schnitt ohne Balance als Kontrast.

Lauffähig mit: streamlit run app.py
"""

import pandas as pd
import streamlit as st

import bis_algorithm as A
import bis_constants as C
import bis_evaluation as ev
import bis_experiments as ex
from bis_layout import dunkles_design, kopf_css
from bis_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from bis_visualization import (
    build_balance,
    build_best_so_far,
    build_big,
    build_exact,
    build_fm_curve,
    build_kl_curve,
    build_methods,
    build_partition_map,
    build_slack,
    build_starts,
    build_starts_hit,
    fm_state,
    kl_state,
)

st.set_page_config(page_title="Ausgewogen halbieren: Kernighan–Lin und Fiduccia–Mattheyses – Sebastian Hanisch", layout="wide")

_i, _dec = ev._i, ev._dec


def _show(verdict):
    kind, text = verdict
    {"success": st.success, "info": st.info, "warning": st.warning}[kind](text)


@st.cache_data(show_spinner=False, max_entries=8)
def _analysis(settings):
    return ev.analyse(settings)


@st.cache_data(show_spinner=False)
def _exactness():
    return ex.exactness_rows()


@st.cache_data(show_spinner=False)
def _balance():
    return ex.balance_rows()


@st.cache_data(show_spinner=False)
def _starts():
    return ex.starts_rows()


@st.cache_data(show_spinner=False)
def _big():
    return ex.big_rows()


@st.cache_data(show_spinner=False)
def _slack():
    return ex.slack_rows()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in bis_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("⚖️ Ausgewogen halbieren: Kernighan–Lin und Fiduccia–Mattheyses")
st.markdown(
    """
**Wie teilt man ein Netz in zwei gleich große Hälften mit möglichst wenig Leitungen dazwischen?** Das ist eine **Bisektion**. Der kleinste Schnitt ohne Balance (Stück 2 der Reihe) hilft hier nicht: Er trennt auf den Modellnetzen meist nur einen einzelnen
Standort ab (nicht beim Verbundnetz, beim Kartennetz nur teils). Wer **ausgewogen** teilen will, rechnet eine andere Aufgabe, und sie ist schwer. Die Demo zeigt zwei Verbesserungsverfahren, die von einer Zufallsanordnung ausgehen: **Kernighan–Lin** tauscht **Paare** aus beiden Hälften
(der beste Präfix einer Gewinnfolge wird ausgeführt), **Fiduccia–Mattheyses** verschiebt **einzelne** Standorte und darf dabei die Hälften kurz verschieden groß werden lassen (**Spielraum**).

Auffällig: Beide Verfahren bleiben von **einer** Zufallsanordnung aus oft über dem Optimum stehen; **mehrere Starts** helfen. Und der Spielraum der Balance ist keine Nebensache: **Ohne Spielraum ist bei gerader Standortzahl jeder Zug blockiert.**

Das ist das fünfte Stück der Reihe **Schnitte und Zusammenhang**; der kleinste Schnitt ohne Balance steht in **globaler-schnitt-demo**. Kernighan–Lin als Werkzeug (rekursive Halbierung) taucht in **order-batching-demo** auf.
Weiter unten: die Experimente **🔬**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So halbiert man ein Netz ausgewogen", expanded=True):
    st.markdown(
        """
1. **Bisektion:** Die Standorte werden in zwei Hälften der Größe ⌈n/2⌉ und ⌊n/2⌋ geteilt; der **Schnitt** ist die Zahl der Leitungen zwischen den Hälften. Gesucht ist die kleinste.
2. **Gewinn:** Für einen Standort v ist D(v) die Zahl seiner Leitungen **nach außen** minus die nach **innen**: Rückt v in die andere Hälfte, sinkt der Schnitt um D(v).
3. **Kernighan–Lin, ein Durchlauf:** Man wählt das Paar (a, b) aus beiden Hälften mit dem größten Tauschgewinn D(a) + D(b) − 2 · [a, b verbunden], **sperrt** beide und wiederholt das, bis alle gesperrt sind. Vom Anfang der Gewinnfolge wird der **beste Präfix** ausgeführt, wenn seine Summe positiv ist; dann der nächste Durchlauf.
4. **Fiduccia–Mattheyses, ein Durchlauf:** Man verschiebt immer den freien Standort mit dem größten Gewinn (und sperrt ihn), auch wenn der Schnitt dabei wächst, und darf die Hälften verschieden groß werden lassen (**Spielraum** s). Ausgeführt wird der beste Präfix unter den Zuständen, in denen die Hälften wieder ausgewogen sind.
5. **Mehrere Starts:** Beide Verfahren enden in einem **lokalen** Optimum; man startet von mehreren zufälligen Anordnungen und nimmt das Beste.

| Begriff | Bedeutung |
|---|---|
| **Bisektion** | Zweiteilung der Standorte in zwei Hälften der Größe ⌈n/2⌉ und ⌊n/2⌋ |
| **Schnitt** | Zahl der Leitungen zwischen den Hälften |
| **Gewinn D(v)** | Leitungen nach außen minus nach innen: so viel sinkt der Schnitt, wenn v die Hälfte wechselt |
| **Beste Präfix** | der Anfang der Zug- oder Tauschfolge mit dem kleinsten Schnitt (nur wieder ausgewogene Zustände) |
| **Spielraum** | wie weit die Hälften während eines Durchlaufs von der gleichen Größe abweichen dürfen (Fiduccia–Mattheyses) |
| **Paarbewertung / Zug** | Zähleinheit bei Kernighan–Lin (jedes angesehene Paar) / bei Fiduccia–Mattheyses (jeder ausgeführte Einzelzug) |
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Netz**")
    kind = st.selectbox("Art des Netzes", list(C.KINDS), format_func=C.KIND_NAMES.get, key="kind_select", help=C.KIND_HELP.get(st.session_state.get("kind_select", C.DEFAULT_KIND), ""))
    n = st.slider("Standorte n", *bounds("n_slider"), key="n_slider", help=f"Wie viele Standorte das Netz hat (das Gitter rundet auf ein Quadrat). Die Aufzählung des Optimums läuft bis {C.BRUTE_N} Standorte.")
    deg = st.slider("Mittlerer Grad", *bounds("deg_slider"), key="deg_slider", step=0.5, help="Leitungen je Standort im Mittel; wirkt beim Zufallsnetz und innerhalb der Regionen des Verbundnetzes.")
    links = st.slider("Leitungen zwischen je zwei Regionen", *bounds("links_slider"), key="links_slider", help="Wirkt nur beim Verbundnetz.")
    seed = st.number_input("Zufalls-Seed des Netzes", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neues Netz erzeugen", width="stretch", on_click=randomize_seed)
    st.caption(C.KIND_REGLER[kind])
    st.markdown("**Verfahren**")
    method = st.selectbox("Verfahren", list(C.METHODS), format_func=C.METHOD_NAMES.get, key="method_select", help="Welches Verfahren im Ablauf gezeigt und in den Kennzahlen genannt wird; beide laufen auf denselben Startanordnungen.")
    slack = st.slider("Spielraum der Balance (Fiduccia–Mattheyses)", *bounds("slack_slider"), key="slack_slider", help="Wie weit die Hälften während eines Durchlaufs von der gleichen Größe abweichen dürfen. Bei 0 ist bei gerader Standortzahl jeder Zug blockiert.")
    starts = st.selectbox("Zahl der Zufallsstarts", list(C.STARTS), key="starts_select", help="Von wie vielen zufälligen Anordnungen aus jedes Verfahren startet.")

sync_query_params({"kind_select": kind, "n_slider": int(n), "deg_slider": float(deg), "links_slider": int(links), "seed_input": int(seed), "method_select": method, "slack_slider": int(slack), "starts_select": int(starts)})

settings = ev.Settings(kind, int(n), float(deg), int(links), int(seed), method, int(slack), int(starts))
with st.spinner("Rechne die Starts beider Verfahren..."):
    a = _analysis(settings)
problems = ev.validate(a)
for p in problems:
    st.error(f"Prüfung fehlgeschlagen: {p}")
signature = f"{settings.kind}_{settings.n}_{settings.deg}_{settings.links}_{settings.seed}_{settings.method}_{settings.slack}_{settings.starts}"
inst = a.inst
names = [inst.name(v) for v in range(a.n)]
mname = C.METHOD_NAMES[method]

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
st.caption(f"{C.KIND_NAMES[kind]} mit {_i(a.n)} Standorten und {_i(a.m)} Leitungen. Standorte sind ab 1 nummeriert (das Lehrbeispiel hat Buchstaben). Ein Start ist eine zufällige Anordnung in zwei Hälften.")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Kleinster Schnitt ohne Balance", _i(a.mincut), delta="ein einzelner Standort" if a.mincut_trivial else "echte Teilung", delta_color="off")
m2.metric("Kleinste ausgewogene Zweiteilung", _i(a.reference), delta=f"{_dec(a.reference / a.mincut)}-fach" if a.mincut else None, delta_color="off")
m3.metric(f"{mname.split(' ')[0]}: erster Start", _i(a.first_cut()), delta=f"{a.first_cut() - a.reference:+d} gegen {'Optimum' if a.exact else 'beste Lösung'}" if a.first_cut() != a.reference else "trifft das Optimum" if a.exact else "beste bekannte", delta_color="inverse" if a.first_cut() != a.reference else "off")
m4.metric(f"Bestes aus {_i(a.settings.starts)} Starts", _i(a.best_cut()), delta=f"{_i(a.work)} {ev._unit(method)}", delta_color="off")

tab_run, tab_starts, tab_cut = st.tabs(["🔀 Ein Durchlauf", "🎯 Mehrfachstarts", "⚖️ Kleinster Schnitt und Balance"])

# --- Tab 1: Ein Durchlauf ------------------------------------------------------------------------------------------------------------------

with tab_run:
    c1, c2, c3 = st.columns(3)
    start_no = c1.number_input("Start Nr.", 1, a.settings.starts, 1, step=1, key=f"start_{signature}", help="Welche der Zufallsanordnungen als Ablauf gezeigt wird.")
    run = a.chosen()[int(start_no) - 1]
    if len(run.passes) > 1:
        pass_no = c2.slider("Durchlauf", 1, len(run.passes), 1, key=f"pass_{signature}_{int(start_no)}", help="Welcher Durchlauf des Verfahrens gezeigt wird; der letzte bringt keinen Gewinn mehr.")
    else:
        pass_no = 1
        c2.markdown("**Durchlauf 1** (der einzige: er bringt keinen Gewinn)")
    p = run.passes[pass_no - 1]
    cur = list(run.start)
    for q in run.passes[: pass_no - 1]:
        cur = kl_state(cur, q.swaps, q.best) if method == "kl" else fm_state(cur, q.moves, q.best)
    total = len(p.swaps) if method == "kl" else len(p.moves)
    if total:
        step = c3.slider("Schritt", 0, total, min(total, p.best or 1), key=f"step_{signature}_{int(start_no)}_{pass_no}", help="Wie viele Tausche oder Züge dieses Durchlaufs schon ausgeführt sind (vorbelegt: der beste Präfix).")
    else:
        step = 0
        c3.markdown("**Schritt 0** (kein Tausch, kein Zug möglich)")
    step = min(step, total)
    if method == "kl":
        state = kl_state(cur, p.swaps, step)
        locked = {v for pair in p.swaps[:step] for v in pair[:2]}
        highlight = set(p.swaps[step - 1][:2]) if step else set()
    else:
        state = fm_state(cur, p.moves, step)
        locked = {m[0] for m in p.moves[:step]}
        highlight = {p.moves[step - 1][0]} if step else set()
    q1, q2, q3 = st.columns(3)
    q1.metric("Schnitt vor dem Durchlauf", _i(p.cut_before))
    q2.metric("Schnitt in diesem Schritt", _i(A.cut_size(inst.adj, state)), delta=f"{A.cut_size(inst.adj, state) - p.cut_before:+d} gegen den Anfang", delta_color="inverse")
    q3.metric("Schnitt nach dem Durchlauf", _i(p.cut_after), delta=f"Gewinn {_i(p.gain)}" if p.gain else "kein Gewinn", delta_color="off")
    if method == "kl":
        txt = (f"**Durchlauf {pass_no}:** {_i(len(p.swaps))} Paare in der Reihenfolge der Wahl; der beste Präfix hat {_i(p.best)} Paare und den Gewinn {_i(p.gain)}" if p.best
               else f"**Durchlauf {pass_no}:** Kein Präfix der {_i(len(p.swaps))} Paare hat einen positiven Gewinn, der Durchlauf ändert nichts und das Verfahren endet.")
    elif p.stuck:
        txt = f"**Durchlauf {pass_no}:** Jeder Zug wäre unausgewogen: Bei Spielraum {_i(a.settings.slack)} und {_i(a.n)} Standorten ist **kein einziger Zug erlaubt**, die Anordnung bleibt wie sie ist."
    else:
        txt = (f"**Durchlauf {pass_no}:** {_i(len(p.moves))} Züge; der beste ausgewogene Präfix hat {_i(p.best)} Züge und den Gewinn {_i(p.gain)}" if p.best
               else f"**Durchlauf {pass_no}:** Kein wieder ausgewogener Zustand unterbietet den Anfang, der Durchlauf ändert nichts und das Verfahren endet.")
    st.markdown(txt + ".")
    st.plotly_chart(build_partition_map(inst, state, locked, highlight), width="stretch", key="chart_partition")
    st.caption("Grün und blau sind die beiden Hälften, gestrichelt rot die Leitungen dazwischen (der Schnitt). Gesperrte Standorte haben einen violetten Rand, die zuletzt bewegten sind rote Rauten.")
    if total:
        st.plotly_chart(build_kl_curve(p) if method == "kl" else build_fm_curve(p, a.n), width="stretch", key="chart_curve")
        if method == "kl":
            st.caption("Summe der Gewinne nach jedem getauschten Paar; der beste Präfix (rote Raute) wird ausgeführt, wenn seine Summe positiv ist.")
            st.dataframe(pd.DataFrame([{"Paar": i + 1, "Tausch": f"{names[x]} ↔ {names[y]}", "Gewinn": g, "Summe": s} for i, ((x, y, g), s) in enumerate(zip(p.swaps, p.cumulative))][:80]), hide_index=True, width="stretch")
        else:
            st.caption("Schnitt nach jedem Zug; grüne Punkte sind wieder ausgewogene Zustände, nur unter ihnen wird der beste Präfix gewählt (rote Raute).")
            st.dataframe(pd.DataFrame([{"Zug": i + 1, "Standort": names[v], "Gewinn": g, "Schnitt danach": c, "Größe Hälfte 1": s} for i, (v, g, c, s) in enumerate(p.moves)][:80]), hide_index=True, width="stretch")

# --- Tab 2: Mehrfachstarts -----------------------------------------------------------------------------------------------------------------

with tab_starts:
    st.markdown(f"**{mname}:** Ergebnis je Start")
    st.plotly_chart(build_starts(a.chosen(), a.optimum), width="stretch", key="chart_starts")
    st.caption("Balken: Schnitt am Ende; grau dahinter: Schnitt der Startanordnung. Grün: der Start trifft das Optimum (nur bei Aufzählung).")
    h1, h2 = st.columns(2)
    h1.markdown("**Bestes bisher nach r Starts:**")
    h1.plotly_chart(build_best_so_far(a.chosen(), a.optimum), width="stretch", key="chart_best")
    h2.markdown("**Beide Verfahren, dieselben Startanordnungen:**")
    h2.plotly_chart(build_methods(a), width="stretch", key="chart_methods")
    best = a.best_run()
    st.markdown("**Das Beste aller Starts:**")
    st.plotly_chart(build_partition_map(inst, list(best.side)), width="stretch", key="chart_best_map")
    st.caption(f"{mname}, Schnitt {_i(best.cut)}; Hälfte 1: {{{', '.join(names[v] for v in range(a.n) if best.side[v] == 0)}}}.")

# --- Tab 3: Kleinster Schnitt und Balance --------------------------------------------------------------------------------------------------

with tab_cut:
    w1, w2 = st.columns(2)
    w1.markdown(f"**Kleinster Schnitt ohne Balance: {_i(a.mincut)}**")
    side_mc = [0 if v in set(a.mincut_side) else 1 for v in range(a.n)]
    w1.plotly_chart(build_partition_map(inst, side_mc), width="stretch", key="chart_mincut")
    w1.caption(f"Eine Seite hat {_i(len(a.mincut_side))} von {_i(a.n)} Standorten: " + ("ein einzelner Standort." if a.mincut_trivial else "eine echte Teilung, aber nicht ausgewogen."))
    ref_side = list(a.exact.side) if a.exact else list(a.best_run().side)
    w2.markdown(f"**Kleinste ausgewogene Zweiteilung: {_i(a.reference)}**" + ("" if a.exact else " (beste gefundene)"))
    w2.plotly_chart(build_partition_map(inst, ref_side), width="stretch", key="chart_refmap")
    w2.caption(("Aufzählung aller Bisektionen: " + (f"{_i(a.exact.count)} {'optimale Zweiteilung' if a.exact.count == 1 else 'optimale Zweiteilungen'} unter {_i(a.exact.total)}." if a.exact else "")) if a.exact
               else f"Bei mehr als {C.BRUTE_N} Standorten zählt die Demo nicht mehr alle Bisektionen auf; gezeigt ist das Beste aller Starts beider Verfahren.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie teilt man ausgewogen, und wie weit ist ein Start vom Optimum?")
_show(ev.verdict_question(a))

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

with st.spinner("Rechne die Experimente (einmalig, einige Sekunden)..."):
    rows_x, rows_b, rows_s, rows_big, rows_slack = _exactness(), _balance(), _starts(), _big(), _slack()

st.subheader("🔬 Experiment 1: Stimmen die Verfahren mit der Aufzählung aller Bisektionen überein?")
st.caption(f"{len(rows_x)} Netztypen mit je {len(C.SWEEP_SEEDS)} festen Netzen mit {C.EX_N} Standorten; je {C.EX_STARTS} Starts beider Verfahren gegen die Aufzählung aller Bisektionen.")
st.plotly_chart(build_exact(rows_x), width="stretch", key="chart_exact")
_show(ev.verdict_exact(rows_x))

st.subheader("🔬 Experiment 2: Wie viel teurer ist die ausgewogene Zweiteilung als der kleinste Schnitt?")
st.caption(f"Kleinste Bisektion geteilt durch den kleinsten Schnitt ohne Balance ({C.EX_N} Standorte, je Netztyp {len(C.SWEEP_SEEDS)} Netze; Mittel, kleinstes und größtes Netz).")
st.plotly_chart(build_balance(rows_b), width="stretch", key="chart_balance")
_show(ev.verdict_balance(rows_b))

st.subheader("🔬 Experiment 3: Wie oft trifft ein Start das Optimum, wie oft das Beste aus zehn?")
st.caption(f"Anteil der Netze, in denen das Optimum getroffen wird ({C.EX_N} Standorte, je Netztyp {len(C.SWEEP_SEEDS)} Netze): ein Start gegen das Beste aus {C.EX_STARTS} Starts, beide Verfahren auf denselben Startanordnungen.")
st.plotly_chart(build_starts_hit(rows_s), width="stretch", key="chart_starts_hit")
_show(ev.verdict_starts(rows_s))

st.subheader("🔬 Experiment 4: Wie weit liegt ein Start im großen Netz von der besten Lösung?")
st.caption(f"Bei {C.EX_BIG_N} Standorten (keine Aufzählung): Abstand eines Starts zur besten gefundenen Zweiteilung ({C.EX_BIG_REFERENCE} Starts von Fiduccia–Mattheyses und ein Start von Kernighan–Lin), {C.EX_BIG_SEEDS} Netze je Typ.")
st.plotly_chart(build_big(rows_big), width="stretch", key="chart_big")
_show(ev.verdict_big(rows_big))

st.subheader("🔬 Experiment 5: Was bringt der Spielraum der Balance?")
st.caption(f"Fiduccia–Mattheyses bei {C.EX_SLACK_N} Standorten mit Spielraum 0 bis 4 ({len(C.EX_KINDS)} Netztypen, {C.EX_SLACK_SEEDS} Netze je Typ, {C.EX_SLACK_STARTS} Starts): mittlerer Schnitt am Ende gegen den am Anfang.")
st.plotly_chart(build_slack(rows_slack), width="stretch", key="chart_slack")
_show(ev.verdict_slack(rows_slack))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Gleiche Hälften** | Die Demo teilt nach der Zahl der Standorte; Standorte mit Gewicht (Lasten, Größen) oder mehr als zwei Teile brauchen andere Bedingungen. | - |
| **Lokale Verbesserung** | Beide Verfahren bleiben in einem lokalen Optimum stehen und sehen nur die Umgebung der Anordnung; ob ein Start das Optimum trifft, hängt vom Netz und vom Start ab (Experiment 3). | - |
| **Gleiche Leitungen** | Alle Leitungen zählen gleich; mit Kosten wäre der Schnitt eine gewichtete Summe. | globaler-schnitt-demo |
| **Zusammenhang der Hälften** | Keines der Verfahren garantiert, dass jede Hälfte zusammenhängt; für Bezirke ist das eine zusätzliche Bedingung. | - |
| **Kein Anspruch auf beste Verfahren** | Die Demo baut die lehrbaren Grundverfahren, keine Bibliothek für große Netze; wer Millionen Standorte teilt, nutzt andere Verfahren. | - |
| **Synthetische Netze, bis 120 Standorte** | Reale Netze haben andere Strukturen; Aufwand in Paarbewertungen und Zügen gezählt (verschiedene Einheiten), nicht in Sekunden. Die Aufzählung läuft bis 20 Standorte. | - |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben** ein ungerichteter Graph $G = (V, E)$ mit $n = |V|$ Standorten. Eine **Bisektion** ist eine Menge $S \subseteq V$ mit $|S| = \lceil n/2 \rceil$; ihr Schnitt ist

$$c(S) = \bigl|\{\{u,v\} \in E : u \in S,\ v \notin S\}\bigr|.$$

**Minimale Bisektion** (NP-schwer): $\min_S c(S)$ über alle Bisektionen; der kleinste Schnitt ohne Balance ist dagegen $\min_{\emptyset \ne S \subsetneq V} c(S) \le \delta(G)$, höchstens der Mindestgrad.

**Gewinn.** Für $v \in V$ sei $E(v)$ die Zahl seiner Leitungen zur anderen Hälfte und $I(v)$ die zur eigenen; dann ist $D(v) = E(v) - I(v)$ die Abnahme des Schnitts, wenn $v$ allein die Hälfte wechselt.

**Kernighan–Lin.** Tauscht man $a \in S$ und $b \notin S$, ändert sich der Schnitt um

$$g(a, b) = D(a) + D(b) - 2\,[\{a,b\} \in E].$$

Nach dem Tausch von $(a, b)$ gelten für die übrigen freien Standorte $x$ in der Hälfte von $a$ und $y$ in der von $b$

$$D'(x) = D(x) + 2[\{x,a\} \in E] - 2[\{x,b\} \in E], \qquad D'(y) = D(y) + 2[\{y,b\} \in E] - 2[\{y,a\} \in E].$$

Mit den Gewinnen $g_1, \dots, g_k$ der gewählten Paare wird der Präfix $j^* = \arg\max_j \sum_{i \le j} g_i$ ausgeführt, wenn die Summe positiv ist.

**Fiduccia–Mattheyses.** Jeder Zug verschiebt den freien Standort $v$ mit größtem $D(v)$, sofern die Größe $|S|$ danach in $[\lfloor n/2 \rfloor - s,\ \lceil n/2 \rceil + s]$ bleibt; danach ändern sich $D(u)$ der Nachbarn $u$ um $\pm 2$. Ausgeführt wird der beste Präfix unter den Zuständen mit $|S| \in \{\lfloor n/2 \rfloor, \lceil n/2 \rceil\}$. Bei geradem $n$ und $s = 0$ ist jeder Zug blockiert.

**Literatur.** B. W. Kernighan, S. Lin: *An efficient heuristic procedure for partitioning graphs*, The Bell System Technical Journal 49 (2), 1970, S. 291–307. C. M. Fiduccia, R. M. Mattheyses: *A linear-time heuristic for improving network partitions*, 19th Design Automation Conference, 1982, S. 175–181. Die Demo rechnet beide in der einfachsten Form (ohne Gewinn-Fächer von Fiduccia–Mattheyses; jede Wahl durchsucht alle freien Standorte), behauptet keine Zahlen der Originale und keine Laufzeit.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
