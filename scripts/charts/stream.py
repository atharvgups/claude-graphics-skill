"""
Stream graph (ThemeRiver) renderer — a stacked area flowed around a centered
baseline instead of zero, so the whole composition reads as an organic "river"
of bands over time. Good for showing how a mix shifts when totals also change.

Spec shape:

    {
      "chart_type": "stream",
      "x": ["2019", "2020", ...],
      "series": [ { "name": "Training", "values": [...], "color": "#opt" }, ... ]
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import (add_circle_legend, apply_footer, apply_titles, edge_align,
                   register)
from theme import hex_to_rgba


@register("stream")
def render(spec: dict, theme: dict) -> go.Figure:
    x = spec.get("x") or []
    series = spec.get("series") or []
    if not x or not series:
        raise ValueError("Stream needs 'x' and 'series'")
    m, nseries = len(x), len(series)
    vals = [s["values"] for s in series]

    # Centered ("silhouette") baseline: at each x the whole stack is centered on
    # zero, which produces the symmetric streamgraph flow.
    lower = [[0.0] * m for _ in range(nseries)]
    upper = [[0.0] * m for _ in range(nseries)]
    for j in range(m):
        total = sum(vals[i][j] for i in range(nseries))
        cum = -total / 2
        for i in range(nseries):
            lower[i][j] = cum
            cum += vals[i][j]
            upper[i][j] = cum

    pal = theme.get("stack_palette") or theme["palette"]
    fig = go.Figure()
    for i, s in enumerate(series):
        c = s.get("color") or pal[i % len(pal)]
        xx = list(x) + list(x)[::-1]
        yy = upper[i] + lower[i][::-1]
        fig.add_trace(go.Scatter(
            x=xx, y=yy, fill="toself", mode="lines",
            line=dict(color=theme["paper_bg"], width=1, shape="spline"),
            fillcolor=hex_to_rgba(c, 0.92), name=s.get("name", f"Series {i + 1}"),
            hoverinfo="skip", showlegend=False,
        ))

    add_circle_legend(
        fig, [s.get("name", f"Series {i + 1}") for i, s in enumerate(series)],
        [s.get("color") or pal[i % len(pal)] for i, s in enumerate(series)], theme)

    is_cat = any(isinstance(xi, str) for xi in x)
    tick = dict(family=theme["font_family"], size=theme["label_size"],
                color=theme.get("subtitle_color", theme["font_color"]))
    fig.update_xaxes(showgrid=False, zeroline=False, showline=False, ticks="",
                     tickfont=tick)
    if is_cat:
        fig.update_xaxes(type="category")
    fig.update_yaxes(visible=False)  # streamgraph y is relative, not a scale

    has_footer = bool(spec.get("footer") or spec.get("wordmark"))
    fig.update_layout(
        height=spec.get("height", 620), width=spec.get("width", 1060),
        margin=dict(t=120, l=40, r=40, b=300 if has_footer else 120),
        plot_bgcolor=theme["plot_bg"],
    )
    al = edge_align(spec.get("width", 1060), 40, 40, 28)
    fig.update_layout(legend=dict(x=al["legend_x"]))
    if has_footer:
        apply_titles(fig, {**spec, "source": ""}, theme, x_shift=al["x_shift"])
        apply_footer(fig, spec, theme, x_shift=al["x_shift"],
                     rule_x=al["rule_x"], wordmark_xshift=al["wordmark_xshift"])
    else:
        apply_titles(fig, spec, theme, x_shift=al["x_shift"])
    return fig
