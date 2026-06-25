"""
Pictograph / waffle (isotype) renderer — a grid of squares where each cell is a
unit of the whole, filled proportionally by category. Reads as "X out of 100",
which lands a share story harder than a pie.

Spec shape:

    {
      "chart_type": "pictograph",
      "items": [ { "label": "Enterprise", "value": 52 }, ... ],
      "total": 100,          // optional; default = sum of values
      "columns": 10, "rows": 10, "value_suffix": "%"
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import add_circle_legend, apply_titles, format_value, register


@register("pictograph")
def render(spec: dict, theme: dict) -> go.Figure:
    items = spec.get("items") or []
    if not items:
        raise ValueError("Pictograph needs a non-empty 'items' list")
    total = spec.get("total") or sum(it["value"] for it in items)
    cols = spec.get("columns", 10)
    rows = spec.get("rows", 10)
    cells = cols * rows

    # Largest-remainder rounding so the cell counts sum to EXACTLY `cells`.
    raw = [it["value"] / total * cells for it in items]
    counts = [int(r) for r in raw]
    order = sorted(range(len(items)), key=lambda i: raw[i] - counts[i],
                   reverse=True)
    for k in range(cells - sum(counts)):
        counts[order[k % len(items)]] += 1

    pal = theme.get("stack_palette") or theme["palette"]
    seq = []
    for i, c in enumerate(counts):
        seq += [pal[i % len(pal)]] * c
    seq = seq[:cells]

    xs, ys, cs = [], [], []
    for idx in range(cells):
        xs.append(idx // rows)   # fill column by column...
        ys.append(idx % rows)    # ...bottom to top
        cs.append(seq[idx])

    fig = go.Figure(go.Scatter(
        x=xs, y=ys, mode="markers",
        marker=dict(symbol="square", size=spec.get("marker_size", 26), color=cs,
                    line=dict(color=theme["paper_bg"], width=2)),
        hoverinfo="skip", showlegend=False,
    ))
    fig.update_xaxes(visible=False, range=[-0.6, cols - 0.4])
    fig.update_yaxes(visible=False, range=[-0.6, rows - 0.4],
                     scaleanchor="x", scaleratio=1)

    names = [f"{it.get('label', '')} · {format_value(it['value'], spec)}"
             for it in items]
    add_circle_legend(fig, names,
                      [pal[i % len(pal)] for i in range(len(items))], theme)
    fig.update_layout(
        margin=dict(t=130, l=40, r=40, b=120),
        height=spec.get("height", 660), width=spec.get("width", 760),
        plot_bgcolor=theme["plot_bg"],
    )
    apply_titles(fig, spec, theme)
    return fig
