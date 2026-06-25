"""
Ridgeline (joyplot) renderer — one smoothed density per group, stacked with
overlap so you can compare many distributions at a glance (how a distribution
shifts across groups/time).

Densities use a self-contained Gaussian KDE (no scipy). Lower ridges are drawn
last so they overlap the ones behind, the classic ridgeline look.

Spec shape:

    {
      "chart_type": "ridgeline",
      "groups": [ { "name": "2024", "values": [...], "color": "#opt" }, ... ],
      "x_title": "Latency (ms)", "overlap": 1.6
    }
"""

from __future__ import annotations

import math

import plotly.graph_objects as go

from .base import apply_titles, register
from theme import hex_to_rgba


def _kde(values, grid, bw):
    norm = 1.0 / (len(values) * bw * math.sqrt(2 * math.pi))
    out = []
    for gx in grid:
        out.append(norm * sum(math.exp(-0.5 * ((gx - v) / bw) ** 2)
                              for v in values))
    return out


@register("ridgeline")
def render(spec: dict, theme: dict) -> go.Figure:
    groups = spec.get("groups") or []
    if not groups:
        raise ValueError("Ridgeline needs a non-empty 'groups' list")
    ng = len(groups)
    allv = [v for g in groups for v in g.get("values", [])]
    lo, hi = min(allv), max(allv)
    span = (hi - lo) or 1
    npts = 128
    grid = [lo - span * 0.06 + span * 1.12 * k / (npts - 1) for k in range(npts)]
    bw = span / 16
    overlap = spec.get("overlap", 1.6)

    pal = theme.get("stack_palette") or theme["palette"]
    dens = [_kde(g["values"], grid, bw) for g in groups]
    gmax = max((max(d) for d in dens), default=1) or 1
    scale = overlap / gmax

    fig = go.Figure()
    bases = []
    # Group 0 sits at the top; draw top→bottom so lower ridges overlap.
    for i, g in enumerate(groups):
        base = ng - 1 - i
        bases.append(base)
        c = g.get("color") or pal[i % len(pal)]
        ys = [base + d * scale for d in dens[i]]
        fig.add_trace(go.Scatter(
            x=grid + grid[::-1], y=ys + [base] * npts,
            fill="toself", mode="lines",
            line=dict(color=theme["paper_bg"], width=1.2, shape="spline"),
            fillcolor=hex_to_rgba(c, 0.85), name=g.get("name", f"Group {i + 1}"),
            hoverinfo="skip", showlegend=False,
        ))

    tick = dict(family=theme["font_family"], size=theme["label_size"],
                color=theme.get("subtitle_color", theme["font_color"]))
    fig.update_yaxes(tickmode="array", tickvals=bases,
                     ticktext=[g.get("name", "") for g in groups],
                     showgrid=False, zeroline=False, showline=False, ticks="",
                     range=[-0.4, ng - 1 + overlap + 0.3],
                     tickfont=dict(family=theme["font_family"],
                                   size=theme["label_size"] + 1,
                                   color=theme["title_color"]))
    fig.update_xaxes(showgrid=False, zeroline=False, showline=False, ticks="",
                     tickfont=tick,
                     tickprefix=spec.get("value_prefix", ""),
                     ticksuffix=spec.get("value_suffix", ""))
    axis_font = dict(family=theme["font_family"], size=theme["label_size"] + 1,
                     color=theme.get("subtitle_color", theme["font_color"]))
    fig.update_xaxes(title=dict(text=spec.get("x_title", ""), font=axis_font))
    fig.update_layout(
        height=spec.get("height", 660), width=spec.get("width", 1020),
        margin=dict(t=120, l=110, r=40, b=80), plot_bgcolor=theme["plot_bg"],
    )
    apply_titles(fig, spec, theme)
    return fig
