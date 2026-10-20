"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import bis_algorithm as A
import bis_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _lines(inst, pairs):
    xs, ys = [], []
    for u, v in pairs:
        xs += [float(inst.xy[u, 0]), float(inst.xy[v, 0]), None]
        ys += [float(inst.xy[u, 1]), float(inst.xy[v, 1]), None]
    return xs, ys


def _nodes(inst, nodes, color, size, symbol="circle", name=None, show_text=False, line_color="white", line_width=1):
    nodes = list(nodes)
    return go.Scatter(
        x=[float(inst.xy[v, 0]) for v in nodes], y=[float(inst.xy[v, 1]) for v in nodes], mode="markers+text" if show_text else "markers",
        marker=dict(size=size, color=color, symbol=symbol, line=dict(color=line_color, width=line_width)), text=[inst.name(v) for v in nodes] if show_text else None,
        textfont=dict(size=10, color="#ffffff"), textposition="middle center", hovertext=[f"Standort {inst.name(v)}" for v in nodes], hoverinfo="text", name=name, showlegend=name is not None)


def _map_layout(fig, inst, height=470):
    xs, ys = inst.xy[:, 0], inst.xy[:, 1]
    pad = 0.25 * max(float(xs.max() - xs.min()), float(ys.max() - ys.min()), 1.0)
    fig.update_xaxes(visible=False, range=[float(xs.min()) - pad, float(xs.max()) + pad])
    fig.update_yaxes(visible=False, range=[float(ys.min()) - pad, float(ys.max()) + pad], scaleanchor="x", scaleratio=1)
    return _base(fig, height)


def build_partition_map(inst, side, locked=(), highlight=()):
    """Karte mit den beiden Hälften (grün und blau), den Leitungen dazwischen (rot, gestrichelt), den schon gesperrten Standorten (violetter Rand) und den zuletzt bewegten (rote Raute)."""
    fig = go.Figure()
    cross = [(u, v) for u, v in inst.pairs if side[u] != side[v]]
    rest = [(u, v) for u, v in inst.pairs if side[u] == side[v]]
    xs, ys = _lines(inst, rest)
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_EDGE, width=1.2), hoverinfo="skip", showlegend=False))
    xs, ys = _lines(inst, cross)
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_CUT, width=2.6, dash="dot"), hoverinfo="skip", name=f"Schnitt ({len(cross)})"))
    show_text = inst.n <= 60
    size = 22 if show_text else 11
    locked, highlight = set(locked), set(highlight)
    for half, color, name in ((0, C.COLOR_SIDE_A, "Hälfte 1"), (1, C.COLOR_SIDE_B, "Hälfte 2")):
        plain = [v for v in range(inst.n) if side[v] == half and v not in locked and v not in highlight]
        held = [v for v in range(inst.n) if side[v] == half and v in locked and v not in highlight]
        moved = [v for v in range(inst.n) if side[v] == half and v in highlight]
        fig.add_trace(_nodes(inst, plain, color, size, name=name, show_text=show_text))
        if held:
            fig.add_trace(_nodes(inst, held, color, size, show_text=show_text, line_color=C.COLOR_LOCK, line_width=3))
        if moved:
            fig.add_trace(_nodes(inst, moved, color, size + 6, "diamond", show_text=show_text, line_color=C.COLOR_CUT, line_width=3))
    return _map_layout(fig, inst)


def kl_state(start, swaps, k):
    """Hälften nach den ersten k Paaren eines Kernighan–Lin-Durchlaufs."""
    side = list(start)
    for a, b, _g in swaps[:k]:
        side[a], side[b] = 1, 0
    return side


def fm_state(start, moves, k):
    """Hälften nach den ersten k Zügen eines Fiduccia–Mattheyses-Durchlaufs."""
    side = list(start)
    for v, _g, _c, _s in moves[:k]:
        side[v] ^= 1
    return side


def build_kl_curve(p):
    """Kernighan–Lin: Summe der Gewinne nach jedem Paar; der beste Präfix ist rot."""
    xs = list(range(1, len(p.cumulative) + 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0] + xs, y=[0] + list(p.cumulative), mode="lines+markers", line=dict(color=C.COLOR_BAR, width=3), name="Summe der Gewinne", hovertemplate="%{x} Paare: %{y}<extra></extra>"))
    if p.best:
        fig.add_trace(go.Scatter(x=[p.best], y=[p.cumulative[p.best - 1]], mode="markers", marker=dict(color=C.COLOR_CUT, size=14, symbol="diamond"), name="bester Präfix"))
    fig.add_hline(y=0, line=dict(color="#8a9a9c", dash="dot"))
    fig.update_xaxes(title_text="Zahl der getauschten Paare", dtick=1 if len(xs) <= 20 else None)
    fig.update_yaxes(title_text="Gewinn (weniger Leitungen im Schnitt)")
    return _base(fig, 300)


def build_fm_curve(p, n):
    """Fiduccia–Mattheyses: Schnitt nach jedem Zug; wieder ausgewogene Zustände sind größer, der beste Präfix ist rot."""
    xs = list(range(0, len(p.moves) + 1))
    cuts = [p.cut_before] + [c for _v, _g, c, _s in p.moves]
    bal = [True] + [s in A.balanced_sizes(n) for _v, _g, _c, s in p.moves]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=cuts, mode="lines", line=dict(color=C.COLOR_BAR, width=3), name="Schnitt", hovertemplate="%{x} Züge: %{y}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[x for x, b in zip(xs, bal) if b], y=[c for c, b in zip(cuts, bal) if b], mode="markers", marker=dict(color=C.COLOR_BAR3, size=9), name="ausgewogen"))
    if p.best:
        fig.add_trace(go.Scatter(x=[p.best], y=[cuts[p.best]], mode="markers", marker=dict(color=C.COLOR_CUT, size=14, symbol="diamond"), name="bester Präfix"))
    fig.update_xaxes(title_text="Zahl der Züge")
    fig.update_yaxes(title_text="Schnitt nach dem Zug")
    return _base(fig, 300)


def build_starts(runs, optimum):
    """Ergebnis je Start (Balken) mit dem Optimum (rote Linie, falls bekannt)."""
    xs = [str(i + 1) for i in range(len(runs))]
    colors = [C.COLOR_BAR3 if optimum is not None and r.cut == optimum else C.COLOR_BAR for r in runs]
    fig = go.Figure(go.Bar(x=xs, y=[r.cut for r in runs], marker_color=colors, text=[str(r.cut) for r in runs], textposition="outside", cliponaxis=False, showlegend=False,
                           hovertemplate="Start %{x}: Schnitt %{y}<extra></extra>"))
    fig.add_trace(go.Bar(x=xs, y=[r.start_cut for r in runs], marker_color="rgba(150,150,150,0.35)", name="Schnitt der Startanordnung", hovertemplate="Start %{x}: Anfang %{y}<extra></extra>"))
    if optimum is not None:
        fig.add_hline(y=optimum, line=dict(color=C.COLOR_CUT, dash="dash"), annotation_text=f"Optimum {optimum}", annotation_position="top left")
    fig.update_layout(barmode="overlay")
    fig.update_xaxes(title_text="Start Nr.", type="category")
    fig.update_yaxes(title_text="Schnitt am Ende (Balken) und am Anfang (grau)")
    return _base(fig, 340)


def build_best_so_far(runs, optimum):
    """Bester Schnitt nach r Starts."""
    best, curve = None, []
    for r in runs:
        best = r.cut if best is None else min(best, r.cut)
        curve.append(best)
    fig = go.Figure(go.Scatter(x=list(range(1, len(curve) + 1)), y=curve, mode="lines+markers", line=dict(color=C.COLOR_BAR3, width=3, shape="hv"), showlegend=False,
                               hovertemplate="%{x} Starts: %{y}<extra></extra>"))
    if optimum is not None:
        fig.add_hline(y=optimum, line=dict(color=C.COLOR_CUT, dash="dash"), annotation_text=f"Optimum {optimum}", annotation_position="top right")
    fig.update_xaxes(title_text="Zahl der Starts", dtick=1 if len(curve) <= 12 else None)
    fig.update_yaxes(title_text="bester Schnitt bisher")
    return _base(fig, 300)


def build_methods(a):
    """Beide Verfahren mit denselben Startanordnungen: Schnitt je Start nebeneinander."""
    xs = [str(i + 1) for i in range(a.settings.starts)]
    fig = go.Figure()
    for method, color in (("kl", C.COLOR_BAR), ("fm", C.COLOR_BAR2)):
        fig.add_trace(go.Bar(x=xs, y=[r.cut for r in a.runs[method]], name=C.METHOD_NAMES[method], marker_color=color, hovertemplate="Start %{x}: %{y}<extra></extra>"))
    if a.optimum is not None:
        fig.add_hline(y=a.optimum, line=dict(color=C.COLOR_CUT, dash="dash"), annotation_text=f"Optimum {a.optimum}", annotation_position="top left")
    fig.update_layout(barmode="group")
    fig.update_xaxes(title_text="Start Nr.", type="category")
    fig.update_yaxes(title_text="Schnitt am Ende")
    return _base(fig, 320)


# --- Experimente ---------------------------------------------------------------------------------------------------------------------------------


def build_exact(rows):
    ys = [round(100 * (r["checks"] - r["wrong"]) / r["checks"]) if r["checks"] else 0 for r in rows]
    fig = go.Figure(go.Bar(x=[r["label"] for r in rows], y=ys, marker_color=C.COLOR_BAR, text=[f"{y} %" for y in ys], textposition="outside", cliponaxis=False, showlegend=False))
    fig.update_yaxes(title_text="Prüfungen ohne Abweichung (%)", range=[0, 118])
    return _base(fig)


def build_balance(rows):
    labels = [r["label"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=[round(r["sum_ratio"] / r["nets"], 2) for r in rows], name="Mittel", marker_color=C.COLOR_BAR3, hovertemplate="%{x}: %{y}-fach<extra></extra>"))
    fig.add_trace(go.Scatter(x=labels, y=[r["max_ratio"] for r in rows], mode="markers", marker=dict(color=C.COLOR_CUT, size=11, symbol="diamond"), name="größtes Netz", hovertemplate="%{x}: %{y}-fach<extra></extra>"))
    fig.add_trace(go.Scatter(x=labels, y=[r["min_ratio"] for r in rows], mode="markers", marker=dict(color=C.COLOR_BAR2, size=11, symbol="circle"), name="kleinstes Netz", hovertemplate="%{x}: %{y}-fach<extra></extra>"))
    fig.update_yaxes(title_text="kleinste Bisektion / kleinster Schnitt", rangemode="tozero")
    return _base(fig)


def build_starts_hit(rows):
    labels = [r["label"] for r in rows]
    fig = go.Figure()
    for method, color in (("kl", C.COLOR_BAR), ("fm", C.COLOR_BAR2)):
        fig.add_trace(go.Bar(x=labels, y=[round(100 * r["one"][method] / r["nets"]) for r in rows], name=f"{C.METHOD_NAMES[method].split(' ')[0]}, ein Start", marker_color=color, hovertemplate="%{x}: %{y} %<extra></extra>"))
    for method, color in (("kl", "rgba(76,120,168,0.45)"), ("fm", "rgba(232,163,61,0.45)")):
        fig.add_trace(go.Bar(x=labels, y=[round(100 * r["best"][method] / r["nets"]) for r in rows], name=f"{C.METHOD_NAMES[method].split(' ')[0]}, bestes aus {rows[0]['starts']}", marker_color=color,
                             hovertemplate="%{x}: %{y} %<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Netze, in denen das Optimum getroffen wird (%)", range=[0, 105])
    return _base(fig, 380)


def build_big(rows):
    labels = [r["label"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=[round(r["gap_kl"] / r["nets"], 2) for r in rows], name="Kernighan–Lin, ein Start", marker_color=C.COLOR_BAR, hovertemplate="%{x}: %{y}<extra></extra>"))
    fig.add_trace(go.Bar(x=labels, y=[round(r["gap_fm"] / r["nets"], 2) for r in rows], name="Fiduccia–Mattheyses, ein Start", marker_color=C.COLOR_BAR2, hovertemplate="%{x}: %{y}<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Leitungen über der besten gefundenen Zweiteilung (Mittel)")
    return _base(fig)


def build_slack(rows):
    xs = [r["slack"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=[r["sum_final"] / r["runs"] for r in rows], mode="lines+markers", name="Schnitt am Ende", line=dict(color=C.COLOR_BAR3, width=3), hovertemplate="Spielraum %{x}: %{y:.1f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=xs, y=[r["sum_start"] / r["runs"] for r in rows], mode="lines", name="Schnitt am Anfang", line=dict(color="#8a9a9c", width=2, dash="dash")))
    fig.update_xaxes(title_text="Spielraum der Balance (Standorte)", dtick=1)
    fig.update_yaxes(title_text="Schnitt (Mittel über die Läufe)", rangemode="tozero")
    return _base(fig)
