"""
Line / area chart renderer — for trends over time or any ordered x.

Handles the most common time-series shapes in one place:
  * one or many series (each its own palette color),
  * optional area fill (`fill`) and stacked area (`stacked`),
  * optional markers,
  * labeling either as a bottom legend (default, robust for many series) or as
    direct end-of-line labels (`label_mode: "end"`) — the cleaner a16z look when
    there are only a few series.

Spec shape:

    {
      "chart_type": "line",
      "x": ["2019", "2020", "2021", ...],
      "series": [
        { "name": "Technology", "values": [12, 18, 25, ...], "color": "#opt" },
        { "name": "Software",   "values": [ 8, 11, 19, ...] }
      ],
      "fill": false, "stacked": false, "markers": false,
      "label_mode": "legend"        // "legend" | "end"
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import (add_circle_legend, apply_footer, apply_titles,
                   cartesian_axes, register, style_legend)
from theme import color_for_index, hex_to_rgba


@register("line")
def render(spec: dict, theme: dict) -> go.Figure:
    x = spec.get("x") or []
    series = spec.get("series") or []
    if not x:
        raise ValueError("Line spec needs a non-empty 'x' list")
    if not series:
        raise ValueError("Line spec needs a non-empty 'series' list")

    fill = bool(spec.get("fill", False))
    stacked = bool(spec.get("stacked", False))
    mode = "lines+markers" if spec.get("markers", False) else "lines"
    label_mode = spec.get("label_mode", "legend")
    # Stacked areas read as categorical composition, so they use the broader
    # 9-tone stack palette + a circle-dot legend (like the stacked bar). Plain
    # lines keep their per-line palette color and native line swatch.
    pal_stack = theme.get("stack_palette") or theme["palette"]
    dot_legend = stacked and label_mode != "end"

    fig = go.Figure()
    colors, names = [], []
    for i, s in enumerate(series):
        if "values" not in s:
            raise ValueError(f"Series #{i} is missing required 'values'")
        if s.get("color"):
            c = s["color"]
        elif stacked:
            c = pal_stack[i % len(pal_stack)]
        else:
            c = color_for_index(theme, i)
        colors.append(c)
        names.append(s.get("name", f"Series {i + 1}"))
        trace = dict(
            x=x, y=s["values"], name=names[-1],
            mode=mode, line=dict(color=c, width=3),
            marker=dict(color=c, size=7),
            hovertemplate="%{fullData.name}: %{y}<extra></extra>",
            # Hide real traces from the legend when we draw circle dots instead.
            showlegend=(label_mode == "legend" and not dot_legend),
        )
        if stacked:
            trace["stackgroup"] = "one"
            trace["fillcolor"] = hex_to_rgba(c, 0.65)
        elif fill:
            trace["fill"] = "tozeroy"
            trace["fillcolor"] = hex_to_rgba(c, 0.18)
        fig.add_trace(go.Scatter(**trace))

    if label_mode == "end":
        # Direct labels at the end of each line — no legend, the editorial look.
        for i, s in enumerate(series):
            fig.add_annotation(
                x=x[-1], y=s["values"][-1], text=f"<b>{s.get('name', '')}</b>",
                xanchor="left", xshift=10, showarrow=False,
                font=dict(family=theme["font_family"],
                          size=theme["label_size"], color=colors[i]),
            )
        fig.update_layout(showlegend=False)
        right, bottom = 170, 70
    elif dot_legend:
        add_circle_legend(fig, names, colors, theme)
        right, bottom = 36, 124
    else:
        style_legend(fig, theme)
        right, bottom = 36, 118

    has_footer = bool(spec.get("footer") or spec.get("wordmark"))
    if has_footer:
        bottom = max(bottom, 226)

    cartesian_axes(fig, theme, spec, x_grid=False, y_grid=True)
    fig.update_layout(
        margin=dict(t=120, l=62, r=right, b=bottom),
        height=spec.get("height", 620),
        width=spec.get("width", 1040),
        hovermode="x unified",
    )
    if has_footer:
        apply_titles(fig, {**spec, "source": ""}, theme)
        apply_footer(fig, spec, theme)
    else:
        apply_titles(fig, spec, theme)
    return fig
