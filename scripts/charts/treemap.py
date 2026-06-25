"""
Treemap renderer — nested rectangles sized by value. Good for parts-of-a-whole
with many categories (where a pie would break down), and for one level of
hierarchy via `parent`.

Spec shape:

    {
      "chart_type": "treemap",
      "items": [
        { "label": "Cloud",   "value": 120 },
        { "label": "EC2",     "value": 60, "parent": "Cloud" },   // optional nesting
        { "label": "S3",      "value": 35, "parent": "Cloud" },
        { "label": "Data",    "value": 80 }
      ]
    }

Omit `parent` (or set "") for a flat, single-level treemap.
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import apply_titles, format_value, register
from theme import color_for_index


@register("treemap")
def render(spec: dict, theme: dict) -> go.Figure:
    items = spec.get("items") or []
    if not items:
        raise ValueError("Treemap spec needs a non-empty 'items' list")
    for i, it in enumerate(items):
        if "label" not in it or "value" not in it:
            raise ValueError(f"Item #{i} needs both 'label' and 'value'")

    labels = [it["label"] for it in items]
    parents = [it.get("parent", "") for it in items]
    values = [float(it["value"]) for it in items]
    # Color only top-level tiles distinctly; children inherit visually via Plotly.
    colors = [it.get("color") or color_for_index(theme, i)
              for i, it in enumerate(items)]

    fig = go.Figure(go.Treemap(
        labels=labels, parents=parents, values=values,
        branchvalues="remainder",
        marker=dict(colors=colors, line=dict(color=theme["paper_bg"], width=2)),
        tiling=dict(pad=2),
        pathbar=dict(visible=False),
        texttemplate="<b>%{label}</b><br>%{value}",
        textfont=dict(family=theme["font_family"], size=theme["label_size"] + 1,
                      color="#FFFFFF"),
        hovertemplate="%{label}: %{value}<extra></extra>",
    ))
    fig.update_layout(
        margin=dict(t=120, l=24, r=24, b=60),
        height=spec.get("height", 640), width=spec.get("width", 1040),
    )
    apply_titles(fig, spec, theme)
    return fig
