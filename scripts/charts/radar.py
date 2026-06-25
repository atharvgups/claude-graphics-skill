"""
Radar (spider) chart — compare a few entities across several shared dimensions.
Best with 3–8 axes and 1–3 series; more than that turns to mush.

Spec shape:

    {
      "chart_type": "radar",
      "axes": ["Speed", "Quality", "Cost", "Support", "Ease"],
      "series": [
        { "name": "Us",         "values": [8, 9, 6, 7, 8] },
        { "name": "Competitor", "values": [6, 7, 8, 5, 6] }
      ]
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import apply_titles, register, style_legend
from theme import color_for_index, hex_to_rgba


@register("radar")
def render(spec: dict, theme: dict) -> go.Figure:
    axes = spec.get("axes") or []
    series = spec.get("series") or []
    if not axes or not series:
        raise ValueError("Radar spec needs 'axes' and 'series'")

    fig = go.Figure()
    for i, s in enumerate(series):
        if "values" not in s:
            raise ValueError(f"Series #{i} is missing required 'values'")
        c = s.get("color") or color_for_index(theme, i)
        # Close the loop by repeating the first point.
        fig.add_trace(go.Scatterpolar(
            r=list(s["values"]) + [s["values"][0]],
            theta=list(axes) + [axes[0]],
            name=s.get("name", f"Series {i + 1}"),
            fill="toself", fillcolor=hex_to_rgba(c, 0.18),
            line=dict(color=c, width=2.5),
        ))

    grid = theme.get("grid_color", "rgba(0,0,0,0.08)")
    tick = dict(family=theme["font_family"], size=theme["label_size"],
                color=theme.get("subtitle_color", theme["font_color"]))
    fig.update_layout(
        polar=dict(
            bgcolor=theme["plot_bg"],
            radialaxis=dict(gridcolor=grid, linecolor=grid, tickfont=tick,
                            angle=90, tickangle=90),
            angularaxis=dict(gridcolor=grid, linecolor=grid,
                             tickfont=dict(family=theme["font_family"],
                                           size=theme["label_size"],
                                           color=theme["font_color"])),
        ),
        margin=dict(t=120, l=70, r=70, b=110),
        height=spec.get("height", 660), width=spec.get("width", 860),
    )
    style_legend(fig, theme)
    apply_titles(fig, spec, theme)
    return fig
