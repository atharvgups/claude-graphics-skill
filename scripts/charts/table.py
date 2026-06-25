"""
Styled table renderer — when the data IS the story (leaderboards, comparisons,
metric grids). Navy header, zebra rows, themed type. Not every dataset wants a
chart; a clean table often beats a bad one.

Spec shape:

    {
      "chart_type": "table",
      "columns": ["Company", "ARR ($M)", "Growth", "NRR"],
      "rows": [
        ["Acme",  "42", "+120%", "131%"],
        ["Globex","31", "+88%",  "119%"]
      ]
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import apply_titles, register
from theme import color_for_index, hex_to_rgba


@register("table")
def render(spec: dict, theme: dict) -> go.Figure:
    columns = spec.get("columns") or []
    rows = spec.get("rows") or []
    if not columns or not rows:
        raise ValueError("Table spec needs 'columns' and 'rows'")

    # Transpose rows -> per-column value lists for go.Table.
    cols_data = [[row[c] if c < len(row) else "" for row in rows]
                 for c in range(len(columns))]
    zebra = hex_to_rgba(color_for_index(theme, 0), 0.10)
    base = theme["paper_bg"]
    fill = [[base if r % 2 == 0 else zebra for r in range(len(rows))]] * len(columns)

    fig = go.Figure(go.Table(
        columnwidth=spec.get("column_widths"),
        header=dict(
            values=[f"<b>{c}</b>" for c in columns],
            fill_color=theme["title_color"], align="left", height=38,
            font=dict(color="#FFFFFF", family=theme["font_family"],
                      size=theme["label_size"] + 1),
            line=dict(width=0)),
        cells=dict(
            values=cols_data, fill_color=fill, align="left", height=33,
            font=dict(color=theme["font_color"], family=theme["font_family"],
                      size=theme["label_size"]),
            line=dict(width=0)),
    ))
    n = len(rows)
    fig.update_layout(
        margin=dict(t=120, l=24, r=24, b=58),
        height=spec.get("height", 160 + 36 * n), width=spec.get("width", 1000),
    )
    apply_titles(fig, spec, theme)
    return fig
