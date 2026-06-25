"""
Heatmap renderer — a matrix of values as a color grid (cohorts, day-by-hour
activity, correlation, category-by-period intensity).

Spec shape:

    {
      "chart_type": "heatmap",
      "x": ["Mon", "Tue", ...],          // column labels
      "y": ["Week 1", "Week 2", ...],    // row labels (top to bottom)
      "z": [[4, 8, 2, ...], ...],        // rows aligned to y, cols aligned to x
      "show_values": true,               // print each cell's value
      "colorscale": [[0, "#..."], [1, "#..."]]   // optional override
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import apply_titles, format_value, register
from theme import color_for_index


@register("heatmap")
def render(spec: dict, theme: dict) -> go.Figure:
    x = spec.get("x") or []
    y = spec.get("y") or []
    z = spec.get("z") or []
    if not z or not x or not y:
        raise ValueError("Heatmap spec needs 'x', 'y', and 'z'")

    # Sequential scale from the canvas color up to the accent — cohesive and
    # on-theme. Rows are reversed so the first y label sits at the top.
    scale = spec.get("colorscale") or [[0, theme["paper_bg"]],
                                        [1, color_for_index(theme, 0)]]
    show_values = spec.get("show_values", True)

    # Keep data in given order; autorange="reversed" (below) puts the first y
    # row at the top, so the first cohort/row reads top-down as written.
    heat = dict(
        x=x, y=y, z=z,
        colorscale=scale, xgap=3, ygap=3,
        # `null` cells (e.g. a cohort's future months) render as blank gaps — a
        # proper triangular cohort grid, not misleading 0s.
        hoverongaps=False,
        hovertemplate="%{y} · %{x}: %{z}<extra></extra>",
        colorbar=dict(outlinewidth=0, tickfont=dict(
            family=theme["font_family"], size=theme["label_size"],
            color=theme.get("subtitle_color", theme["font_color"]))),
    )
    if show_values:
        heat["text"] = [["" if v is None else format_value(v, spec)
                         for v in row] for row in z]
        heat["texttemplate"] = "%{text}"
        heat["textfont"] = dict(family=theme["font_family"],
                                size=theme["label_size"])

    fig = go.Figure(go.Heatmap(**heat))
    tick = dict(family=theme["font_family"], size=theme["label_size"],
                color=theme.get("subtitle_color", theme["font_color"]))
    fig.update_xaxes(showgrid=False, zeroline=False, showline=False, ticks="",
                     side="top", tickfont=tick)
    fig.update_yaxes(showgrid=False, zeroline=False, showline=False, ticks="",
                     tickfont=tick, autorange="reversed")
    fig.update_layout(
        margin=dict(t=140, l=110, r=40, b=60),
        height=spec.get("height", 620), width=spec.get("width", 1040),
    )
    apply_titles(fig, spec, theme)
    return fig
