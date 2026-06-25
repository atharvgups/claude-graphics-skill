"""
Box-plot (or violin) renderer — compare distributions across groups.

Set `"violin": true` to draw violins instead of boxes (same spec). Each group
shows its spread, median, and outliers — the honest way to show "it varies",
not just an average.

Spec shape:

    {
      "chart_type": "box",
      "violin": false,
      "groups": [
        { "name": "Starter",    "values": [10, 12, 9, 15, 11, ...] },
        { "name": "Enterprise", "values": [40, 55, 48, 62, 51, ...] }
      ]
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import apply_titles, cartesian_axes, register
from theme import color_for_index, hex_to_rgba


@register("box")
def render(spec: dict, theme: dict) -> go.Figure:
    groups = spec.get("groups") or []
    if not groups:
        raise ValueError("Box spec needs a non-empty 'groups' list")

    violin = bool(spec.get("violin", False))
    fig = go.Figure()
    for i, g in enumerate(groups):
        if "values" not in g:
            raise ValueError(f"Group #{i} is missing required 'values'")
        c = g.get("color") or color_for_index(theme, i)
        common = dict(y=g["values"], name=g.get("name", f"#{i + 1}"),
                      line=dict(color=c), fillcolor=hex_to_rgba(c, 0.35),
                      marker=dict(color=c))
        if violin:
            fig.add_trace(go.Violin(box_visible=True, meanline_visible=True,
                                    points=False, **common))
        else:
            fig.add_trace(go.Box(boxmean=spec.get("show_mean", True),
                                 boxpoints=False, **common))

    cartesian_axes(fig, theme, spec, x_grid=False, y_grid=True)
    fig.update_layout(
        margin=dict(t=120, l=66, r=30, b=64),
        height=spec.get("height", 620), width=spec.get("width", 1000),
        showlegend=False,
    )
    apply_titles(fig, spec, theme)
    return fig
