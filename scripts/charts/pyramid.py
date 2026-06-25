"""
Population pyramid renderer — two horizontal bar series mirrored around a center
axis (classic age/sex pyramid, or any left-vs-right split by cohort).

Spec shape:

    {
      "chart_type": "pyramid",
      "groups": ["0-9", "10-19", ...],          // cohorts, bottom -> top
      "left":  { "name": "Male",   "values": [...], "color": "#opt" },
      "right": { "name": "Female", "values": [...], "color": "#opt" }
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import (add_circle_legend, apply_footer, apply_titles, format_value,
                   register)
from theme import hex_to_rgba


@register("pyramid")
def render(spec: dict, theme: dict) -> go.Figure:
    groups = spec.get("groups") or []
    left = spec.get("left") or {}
    right = spec.get("right") or {}
    if not groups or "values" not in left or "values" not in right:
        raise ValueError("Pyramid needs 'groups', 'left.values', 'right.values'")

    n = len(groups)
    ypos = list(range(n))
    lc = left.get("color") or theme["palette"][1]
    rc = right.get("color") or theme["palette"][0]
    lvals, rvals = left["values"], right["values"]
    mx = max(max(lvals), max(rvals)) or 1

    def _bar(vals, signed, name, color):
        return go.Bar(
            y=ypos, x=[signed * v for v in vals], orientation="h", name=name,
            marker=dict(color=color, line=dict(color=theme["paper_bg"], width=1),
                        cornerradius=3),
            width=0.82, showlegend=False,
            text=[f"<b>{format_value(v, spec)}</b>" for v in vals],
            textposition="outside", cliponaxis=False,
            textfont=dict(family=theme["font_family"], size=theme["label_size"],
                          color=theme.get("subtitle_color", theme["font_color"])),
            customdata=vals, hovertemplate="%{customdata}<extra>" + name + "</extra>",
        )

    fig = go.Figure([_bar(lvals, -1, left.get("name", "Left"), lc),
                     _bar(rvals, 1, right.get("name", "Right"), rc)])

    # Symmetric x-axis with ABSOLUTE-magnitude tick labels (both sides positive).
    step = mx / 2
    tickvals = [-mx, -step, 0, step, mx]
    ticktext = [format_value(abs(v), spec) for v in tickvals]
    fig.update_xaxes(range=[-mx * 1.18, mx * 1.18], tickvals=tickvals,
                     ticktext=ticktext, showgrid=False, zeroline=False,
                     showline=False, ticks="",
                     tickfont=dict(family=theme["font_family"],
                                   size=theme["label_size"],
                                   color=theme.get("subtitle_color",
                                                   theme["font_color"])))
    fig.update_yaxes(tickmode="array", tickvals=ypos, ticktext=groups,
                     showgrid=False, zeroline=False, showline=False, ticks="",
                     tickfont=dict(family=theme["font_family"],
                                   size=theme["label_size"],
                                   color=theme["title_color"]))

    # Center divider + the two side names as headers above each half.
    fig.add_shape(type="line", xref="x", yref="paper", x0=0, x1=0, y0=0, y1=1,
                  line=dict(color=hex_to_rgba(theme["title_color"], 0.4),
                            width=1.4), layer="below")
    for sign, item, color in ((-1, left, lc), (1, right, rc)):
        fig.add_annotation(
            x=sign * mx * 0.55, y=1.0, xref="x", yref="paper", yshift=8,
            yanchor="bottom", text=f"<b>{item.get('name', '')}</b>",
            showarrow=False, font=dict(family=theme["font_family"],
                                       size=theme["label_size"] + 2, color=color))

    has_footer = bool(spec.get("footer") or spec.get("wordmark"))
    fig.update_layout(
        barmode="overlay", bargap=0.18,
        height=spec.get("height", 660), width=spec.get("width", 1020),
        margin=dict(t=140, l=86, r=40, b=300 if has_footer else 96),
    )
    if has_footer:
        apply_titles(fig, {**spec, "source": ""}, theme)
        apply_footer(fig, spec, theme)
    else:
        apply_titles(fig, spec, theme)
    return fig
