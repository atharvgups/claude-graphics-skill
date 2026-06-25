"""
Combo (dual-axis bar + line) renderer — a16z's signature "two stories" chart.

Bars on the left axis, one or more lines on the right axis, sharing an x. Perfect
for "volume vs. rate" pairs (tokens sold as bars + price as a line). a16z combos
(chart 1) put **multiple** lines on the right axis and distinguish them by
**marker shape** (circle, diamond, square …) as well as color.

Spec shape:

    {
      "chart_type": "combo",
      "x": ["Nov '24", "Dec '24", ...],
      "bar":  { "name": "Tokens (B)", "values": [...], "axis_title": "Tokens (B)",
                "suffix": "K" },
      "lines": [                          # or "line": {...} for a single line
        { "name": "Price ($/1M)", "values": [...], "axis_title": "Price ($/1M)",
          "prefix": "$" },
        { "name": "Imports CAGR", "values": [...], "dash": "dot" }
      ]
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import (add_circle_legend, apply_footer, apply_titles, edge_align,
                   register)
from theme import color_for_index

# Distinct marker shapes per line — a16z separates overlapping lines by shape.
_SHAPES = ["circle", "diamond", "square", "triangle-up", "x"]


@register("combo")
def render(spec: dict, theme: dict) -> go.Figure:
    x = spec.get("x") or []
    bar = spec.get("bar") or {}
    lines = spec.get("lines")
    if not lines:
        single = spec.get("line")
        lines = [single] if single else []
    if not x or "values" not in bar or not lines:
        raise ValueError("Combo spec needs 'x', 'bar.values', and 'line(s).values'")

    bar_color = bar.get("color") or color_for_index(theme, 0)
    line_pal = theme.get("line_palette") or theme["palette"]
    grid = theme.get("grid_color", "rgba(0,0,0,0.08)")
    tick = dict(family=theme["font_family"], size=theme["label_size"],
                color=theme.get("subtitle_color", theme["font_color"]))
    axis_font = dict(family=theme["font_family"], size=theme["label_size"],
                     color=theme.get("subtitle_color", theme["font_color"]))

    fig = go.Figure()
    # Real traces stay out of the legend; circle dots stand in below.
    fig.add_trace(go.Bar(
        x=x, y=bar["values"], name=bar.get("name", "Bar"),
        marker=dict(color=bar_color, cornerradius=4, line=dict(width=0)),
        width=0.62, yaxis="y", showlegend=False,
        hovertemplate="%{x}: %{y}<extra></extra>",
    ))

    line_colors = []
    for k, ln in enumerate(lines):
        if "values" not in ln:
            raise ValueError(f"Combo line #{k} is missing 'values'")
        # Lines avoid the bar's lead color: start at the 2nd palette entry.
        c = ln.get("color") or line_pal[(k + 1) % len(line_pal)]
        line_colors.append(c)
        fig.add_trace(go.Scatter(
            x=x, y=ln["values"], name=ln.get("name", f"Line {k + 1}"),
            mode="lines+markers", yaxis="y2",
            line=dict(color=c, width=3, dash=ln.get("dash", "solid")),
            marker=dict(color=c, size=8, symbol=_SHAPES[k % len(_SHAPES)],
                        line=dict(color=theme["paper_bg"], width=1.5)),
            showlegend=False, hovertemplate="%{x}: %{y}<extra></extra>",
        ))

    # Right axis formatting follows the first line (shared RHS scale).
    r0 = lines[0]
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
                    tickprefix=r0.get("prefix", ""), ticksuffix=r0.get("suffix", ""),
                    title=dict(text=r0.get("axis_title", ""), font=axis_font)),
        margin=dict(t=120, l=72, r=78, b=226 if has_footer else 120),
        height=spec.get("height", 640),
        width=spec.get("width", 1080),
    )
    add_circle_legend(fig, [bar.get("name", "Bar")] + [ln.get("name", f"Line {k+1}")
                            for k, ln in enumerate(lines)],
                      [bar_color] + line_colors, theme)
    # Align headline/legend/footer to the canvas edge (not the plot edge).
    al = edge_align(spec.get("width", 1080), 72, 78, 28)
    fig.update_layout(legend=dict(x=al["legend_x"]))
    if has_footer:
        apply_titles(fig, {**spec, "source": ""}, theme, x_shift=al["x_shift"])
        apply_footer(fig, spec, theme, x_shift=al["x_shift"],
                     rule_x=al["rule_x"], wordmark_xshift=al["wordmark_xshift"])
    else:
        apply_titles(fig, spec, theme, x_shift=al["x_shift"])
    return fig
