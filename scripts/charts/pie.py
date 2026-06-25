"""
Pie / donut renderer — for parts of a whole (use sparingly; bars usually win).

Spec shape:

    {
      "chart_type": "pie",
      "donut": true,                 // false = full pie
      "slices": [
        { "label": "Enterprise", "value": 52, "color": "#opt" },
        { "label": "Mid-market", "value": 31 },
        { "label": "SMB",        "value": 17 }
      ]
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import apply_titles, register
from theme import color_for_index


@register("pie")
def render(spec: dict, theme: dict) -> go.Figure:
    slices = spec.get("slices") or []
    if not slices:
        raise ValueError("Pie spec needs a non-empty 'slices' list")
    for i, s in enumerate(slices):
        if "value" not in s:
            raise ValueError(f"Slice #{i} is missing required 'value'")

    labels = [s.get("label", f"#{i + 1}") for i, s in enumerate(slices)]
    values = [float(s["value"]) for s in slices]
    colors = [s.get("color") or color_for_index(theme, i) for i, s in enumerate(slices)]

    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        marker=dict(colors=colors, line=dict(color=theme["paper_bg"], width=2)),
        hole=0.55 if spec.get("donut", False) else 0,
        sort=False, direction="clockwise",
        # automargin off: keep the paper origin fixed so the headline stays at the
        # canvas edge (outside labels otherwise auto-expand the margin and shove
        # the title inward). Plotly shrinks the pie to fit the labels instead.
        automargin=False,
        textposition="outside",
        texttemplate="<b>%{label}</b>  %{percent}",
        textfont=dict(family=theme["font_family"], size=theme["label_size"],
                      color=theme["font_color"]),
        hovertemplate="%{label}: %{value}<extra></extra>",
    ))
    fig.update_layout(
        showlegend=False,
        margin=dict(t=120, l=40, r=40, b=70),
        height=spec.get("height", 640),
        width=spec.get("width", 900),
    )
    apply_titles(fig, spec, theme, x_shift=-(40 - 28))  # headline to canvas edge
    return fig
