"""
Sunburst renderer — the radial sibling of treemap for hierarchical
parts-of-a-whole. Same data shape as treemap (`items` with `label`, `value`,
optional `parent`); pick whichever framing reads best (treemap = rectangles,
sunburst = rings).

Spec shape:

    {
      "chart_type": "sunburst",
      "items": [
        { "label": "Cloud", "value": 0 },
        { "label": "Compute", "value": 60, "parent": "Cloud" },
        { "label": "Storage", "value": 35, "parent": "Cloud" }
      ]
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import apply_titles, register
from theme import color_for_index


def _common(spec, theme):
    items = spec.get("items") or []
    if not items:
        raise ValueError("Hierarchy spec needs a non-empty 'items' list")
    for i, it in enumerate(items):
        if "label" not in it:
            raise ValueError(f"Item #{i} is missing 'label'")
    labels = [it["label"] for it in items]
    parents = [it.get("parent", "") for it in items]
    values = [float(it.get("value", 0)) for it in items]
    colors = [it.get("color") or color_for_index(theme, i) for i, it in enumerate(items)]
    return labels, parents, values, colors


def _finish(fig, spec, theme):
    fig.update_layout(
        margin=dict(t=120, l=24, r=24, b=62),
        height=spec.get("height", 660), width=spec.get("width", 920),
    )
    apply_titles(fig, spec, theme)
    return fig


@register("sunburst")
def render_sunburst(spec: dict, theme: dict) -> go.Figure:
    labels, parents, values, colors = _common(spec, theme)
    fig = go.Figure(go.Sunburst(
        labels=labels, parents=parents, values=values,
        branchvalues="remainder",
        marker=dict(colors=colors, line=dict(color=theme["paper_bg"], width=2)),
        texttemplate="<b>%{label}</b>",
        insidetextfont=dict(color="#FFFFFF", family=theme["font_family"]),
        hovertemplate="%{label}: %{value}<extra></extra>",
    ))
    return _finish(fig, spec, theme)
