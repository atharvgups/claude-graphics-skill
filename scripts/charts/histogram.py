"""
Histogram renderer — the distribution of a single numeric variable.

Spec shape:

    {
      "chart_type": "histogram",
      "values": [12, 14, 9, 22, ...],
      "bins": 20,                       // optional bin count
      "x_title": "Deal size ($K)", "y_title": "Count"
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import apply_titles, cartesian_axes, register
from theme import color_for_index


@register("histogram")
def render(spec: dict, theme: dict) -> go.Figure:
    values = spec.get("values") or []
    if not values:
        raise ValueError("Histogram spec needs a non-empty 'values' list")

    fig = go.Figure(go.Histogram(
        x=values, nbinsx=spec.get("bins"),
        marker=dict(color=color_for_index(theme, 0),
                    line=dict(color=theme["paper_bg"], width=1)),
        hovertemplate="%{x}: %{y}<extra></extra>",
    ))
    cartesian_axes(fig, theme, spec, x_grid=False, y_grid=True)
    axis_font = dict(family=theme["font_family"], size=theme["label_size"],
                     color=theme.get("subtitle_color", theme["font_color"]))
    fig.update_xaxes(title=dict(text=spec.get("x_title", ""), font=axis_font))
    fig.update_yaxes(title=dict(text=spec.get("y_title", "Count"), font=axis_font))
    fig.update_layout(
        margin=dict(t=120, l=66, r=30, b=64), bargap=0.04,
        height=spec.get("height", 620), width=spec.get("width", 1040),
        showlegend=False,
    )
    apply_titles(fig, spec, theme)
    return fig
