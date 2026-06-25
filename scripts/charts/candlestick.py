"""
Candlestick (OHLC) renderer — price action over time. Up days use the accent,
down days the rust tone.

Spec shape:

    {
      "chart_type": "candlestick",
      "value_prefix": "$",
      "data": [
        { "date": "2026-01-02", "open": 100, "high": 108, "low": 98, "close": 106 },
        ...
      ]
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import apply_titles, cartesian_axes, register
from theme import color_for_index


@register("candlestick")
def render(spec: dict, theme: dict) -> go.Figure:
    data = spec.get("data") or []
    if not data:
        raise ValueError("Candlestick spec needs a non-empty 'data' list")
    for i, d in enumerate(data):
        for k in ("open", "high", "low", "close"):
            if k not in d:
                raise ValueError(f"Data point #{i} is missing '{k}'")

    inc = color_for_index(theme, 0)
    dec = color_for_index(theme, 4)
    fig = go.Figure(go.Candlestick(
        x=[d.get("date", i) for i, d in enumerate(data)],
        open=[d["open"] for d in data], high=[d["high"] for d in data],
        low=[d["low"] for d in data], close=[d["close"] for d in data],
        increasing=dict(line=dict(color=inc), fillcolor=inc),
        decreasing=dict(line=dict(color=dec), fillcolor=dec),
    ))
    cartesian_axes(fig, theme, spec, x_grid=False, y_grid=True)
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        margin=dict(t=120, l=66, r=30, b=60),
        height=spec.get("height", 620), width=spec.get("width", 1080),
        showlegend=False,
    )
    apply_titles(fig, spec, theme, x_shift=-(66 - 28))  # headline to canvas edge
    return fig
