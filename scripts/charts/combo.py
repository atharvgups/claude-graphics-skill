"""
Combo (dual-axis bar + line) renderer — a16z's signature "two stories" chart.

Bars on the left axis, a line on the right axis, sharing an x. Perfect for
"volume vs. rate" pairs (e.g. tokens sold as bars + price as a line). Each side
gets its own axis title and optional prefix/suffix so the two scales read clearly.

Spec shape:

    {
      "chart_type": "combo",
      "x": ["Nov '24", "Dec '24", ...],
      "bar":  { "name": "Tokens (B)", "values": [...], "axis_title": "Tokens (B)",
                "suffix": "K" },
      "line": { "name": "Price ($/1M)", "values": [...], "axis_title": "Price ($/1M)",
                "prefix": "$" }
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import (add_circle_legend, apply_footer, apply_titles, register)
from theme import color_for_index


@register("combo")
def render(spec: dict, theme: dict) -> go.Figure:
    x = spec.get("x") or []
    bar = spec.get("bar") or {}
    line = spec.get("line") or {}
    if not x or "values" not in bar or "values" not in line:
        raise ValueError("Combo spec needs 'x', 'bar.values', and 'line.values'")

    bar_color = bar.get("color") or color_for_index(theme, 0)
    line_color = line.get("color") or color_for_index(theme, 3)
    grid = theme.get("grid_color", "rgba(0,0,0,0.08)")
    tick = dict(family=theme["font_family"], size=theme["label_size"],
                color=theme.get("subtitle_color", theme["font_color"]))
    axis_font = dict(family=theme["font_family"], size=theme["label_size"],
                     color=theme.get("subtitle_color", theme["font_color"]))

    fig = go.Figure()
    # Real traces stay out of the legend; circle dots stand in for both the bar
    # and the line so the legend matches the editorial dot style.
    fig.add_trace(go.Bar(
        x=x, y=bar["values"], name=bar.get("name", "Bar"),
        marker=dict(color=bar_color, line=dict(width=0)), width=0.62, yaxis="y",
        showlegend=False, hovertemplate="%{x}: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=line["values"], name=line.get("name", "Line"),
        mode="lines+markers", line=dict(color=line_color, width=3),
        marker=dict(color=line_color, size=7), yaxis="y2",
        showlegend=False, hovertemplate="%{x}: %{y}<extra></extra>",
    ))

    has_footer = bool(spec.get("footer") or spec.get("wordmark"))
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showline=False, ticks="",
                   tickfont=tick),
        yaxis=dict(showgrid=True, gridcolor=grid, zeroline=False, showline=False,
                   ticks="", tickfont=tick,
                   tickprefix=bar.get("prefix", ""), ticksuffix=bar.get("suffix", ""),
                   title=dict(text=bar.get("axis_title", ""), font=axis_font)),
        yaxis2=dict(overlaying="y", side="right", showgrid=False, zeroline=False,
                    showline=False, ticks="", tickfont=tick,
                    tickprefix=line.get("prefix", ""), ticksuffix=line.get("suffix", ""),
                    title=dict(text=line.get("axis_title", ""), font=axis_font)),
        margin=dict(t=120, l=72, r=78, b=226 if has_footer else 118),
        height=spec.get("height", 640),
        width=spec.get("width", 1080),
    )
    add_circle_legend(fig, [bar.get("name", "Bar"), line.get("name", "Line")],
                      [bar_color, line_color], theme)
    if has_footer:
        apply_titles(fig, {**spec, "source": ""}, theme)
        apply_footer(fig, spec, theme)
    else:
        apply_titles(fig, spec, theme)
    return fig
