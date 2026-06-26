"""
Waterfall renderer — for bridges: how a starting value becomes an ending value
through a sequence of gains and losses (ARR walk, P&L bridge, headcount change).

Spec shape:

    {
      "chart_type": "waterfall",
      "steps": [
        { "label": "Starting ARR", "value": 100, "type": "absolute" },
        { "label": "New",          "value": 40 },                 // relative (default)
        { "label": "Expansion",    "value": 15 },
        { "label": "Churn",        "value": -12 },
        { "label": "Ending ARR",   "value": 143, "type": "total" }
      ]
    }

`type` is `relative` (a gain/loss, the default), `absolute` (a hard reset to a
value — usually the first bar), or `total` (a computed running sum — usually the
last). Gains, losses, and totals are colored distinctly so the bridge reads at
a glance.
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import apply_titles, cartesian_axes, format_value, register
from theme import color_for_index, hex_to_rgba


@register("waterfall")
def render(spec: dict, theme: dict) -> go.Figure:
    steps = spec.get("steps") or []
    if not steps:
        raise ValueError("Waterfall spec needs a non-empty 'steps' list")
    for i, s in enumerate(steps):
        if "value" not in s:
            raise ValueError(f"Step #{i} is missing required 'value'")

    labels = [s.get("label", f"#{i + 1}") for i, s in enumerate(steps)]
    values = [float(s["value"]) for s in steps]
    measure = [
        "total" if s.get("type") == "total"
        else "absolute" if s.get("type") in ("absolute", "start")
        else "relative"
        for s in steps
    ]
    text = [format_value(v, spec) for v in values]

    inc = color_for_index(theme, 0)   # gains
    dec = color_for_index(theme, 4)   # losses
    # Totals anchor the bridge, so they take the theme's anchor color (deep navy
    # in editorial) rather than another palette hue that competes with gains/
    # losses. Falls back to the 2nd palette entry on themes without an anchor.
    tot = theme.get("total_color") or color_for_index(theme, 1)   # totals / resets

    fig = go.Figure(go.Waterfall(
        x=labels, y=values, measure=measure,
        text=[f"<b>{t}</b>" for t in text], textposition="outside",
        textfont=dict(family=theme["font_family"], size=theme["label_size"],
                      color=theme["font_color"]),
        connector=dict(line=dict(color=hex_to_rgba(theme["font_color"], 0.25),
                                 width=1)),
        increasing=dict(marker=dict(color=inc)),
        decreasing=dict(marker=dict(color=dec)),
        totals=dict(marker=dict(color=tot)),
        hovertemplate="%{x}: %{text}<extra></extra>",
    ))
    cartesian_axes(fig, theme, spec, x_grid=False, y_grid=True, y_labels=False)
    fig.update_layout(
        margin=dict(t=120, l=24, r=24, b=70),
        height=spec.get("height", 640), width=spec.get("width", 1040),
        showlegend=False,
    )
    apply_titles(fig, spec, theme)
    return fig
