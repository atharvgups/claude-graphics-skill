"""
Slopegraph — two time points, one line per item. Shows who rose and who fell
between two periods far more cleanly than a grouped bar. Lines that go up are
colored with the accent; lines that fall are muted/rust, so the movers pop.

Spec shape:

    {
      "chart_type": "slope",
      "left_label": "2024", "right_label": "2026",
      "items": [
        { "label": "Engineering", "start": 34, "end": 78 },
        { "label": "Finance",     "start": 28, "end": 19 }
      ]
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import apply_titles, format_value, register
from theme import color_for_index, hex_to_rgba


@register("slope")
def render(spec: dict, theme: dict) -> go.Figure:
    items = spec.get("items") or []
    if not items:
        raise ValueError("Slope spec needs a non-empty 'items' list")
    for i, it in enumerate(items):
        if "start" not in it or "end" not in it:
            raise ValueError(f"Item #{i} needs both 'start' and 'end'")

    up = color_for_index(theme, 0)
    down = color_for_index(theme, 4)
    label_font = dict(family=theme["font_family"], size=theme["label_size"],
                      color=theme["font_color"])

    fig = go.Figure()
    for it in items:
        c = up if it["end"] >= it["start"] else down
        fig.add_trace(go.Scatter(
            x=[0, 1], y=[it["start"], it["end"]], mode="lines+markers",
            line=dict(color=c, width=2.5), marker=dict(color=c, size=9),
            hoverinfo="skip", showlegend=False,
        ))
        name = it.get("label", "")
        fig.add_annotation(x=0, y=it["start"], xanchor="right", xshift=-10,
                           text=f"{name}  <b>{format_value(it['start'], spec)}</b>",
                           showarrow=False, font=label_font)
        fig.add_annotation(x=1, y=it["end"], xanchor="left", xshift=10,
                           text=f"<b>{format_value(it['end'], spec)}</b>  {name}",
                           showarrow=False, font=label_font)

    head_font = dict(family=theme["font_family"], size=theme["label_size"] + 2,
                     color=theme["title_color"])
    fig.add_annotation(x=0, y=1.06, xref="x", yref="paper", text=f"<b>{spec.get('left_label', 'Before')}</b>",
                       showarrow=False, font=head_font, xanchor="center")
    fig.add_annotation(x=1, y=1.06, xref="x", yref="paper", text=f"<b>{spec.get('right_label', 'After')}</b>",
                       showarrow=False, font=head_font, xanchor="center")

    fig.update_xaxes(visible=False, range=[-0.35, 1.35])
    fig.update_yaxes(visible=False)
    fig.update_layout(
        margin=dict(t=130, l=40, r=40, b=60),
        height=spec.get("height", 660), width=spec.get("width", 900),
        plot_bgcolor=theme["plot_bg"],
    )
    apply_titles(fig, spec, theme, x_shift=-(40 - 28))  # headline to canvas edge
    return fig
