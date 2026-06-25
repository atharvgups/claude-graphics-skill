"""
Bump chart — rank position over time (who's #1 each period). Computes ranks from
raw values automatically (highest value = rank 1) and draws one smooth line per
entity, labeled at the right end. Great for "the leaderboard changed" stories.

Spec shape:

    {
      "chart_type": "bump",
      "x": ["2022", "2023", "2024", "2025"],
      "series": [
        { "name": "Model A", "values": [10, 14, 22, 40] },
        { "name": "Model B", "values": [12, 13, 18, 25] }
      ]
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import apply_titles, register
from theme import color_for_index


@register("bump")
def render(spec: dict, theme: dict) -> go.Figure:
    x = spec.get("x") or []
    series = spec.get("series") or []
    if not x or not series:
        raise ValueError("Bump spec needs 'x' and 'series'")
    m = len(x)
    # Rank within each period: highest value -> rank 1.
    ranks = [[0] * m for _ in series]
    for j in range(m):
        order = sorted(range(len(series)),
                       key=lambda i: series[i]["values"][j], reverse=True)
        for r, i in enumerate(order):
            ranks[i][j] = r + 1

    fig = go.Figure()
    for i, s in enumerate(series):
        c = s.get("color") or color_for_index(theme, i)
        fig.add_trace(go.Scatter(
            x=x, y=ranks[i], mode="lines+markers",
            line=dict(color=c, width=4, shape="spline"),
            marker=dict(color=c, size=13),
            hovertemplate=s.get("name", "") + " · #%{y}<extra></extra>",
            showlegend=False,
        ))
        fig.add_annotation(x=x[-1], y=ranks[i][-1], xanchor="left", xshift=14,
                           text=f"<b>{s.get('name', '')}</b>", showarrow=False,
                           font=dict(family=theme["font_family"],
                                     size=theme["label_size"], color=c))

    tick = dict(family=theme["font_family"], size=theme["label_size"],
                color=theme.get("subtitle_color", theme["font_color"]))
    fig.update_xaxes(showgrid=False, zeroline=False, showline=False, ticks="",
                     tickfont=tick)
    fig.update_yaxes(autorange="reversed", tickmode="array",
                     tickvals=list(range(1, len(series) + 1)),
                     showgrid=False, zeroline=False, showline=False, ticks="",
                     tickprefix="#", tickfont=tick)
    fig.update_layout(
        margin=dict(t=120, l=50, r=160, b=60),
        height=spec.get("height", 600), width=spec.get("width", 1040),
        plot_bgcolor=theme["plot_bg"],
    )
    apply_titles(fig, spec, theme)
    return fig
