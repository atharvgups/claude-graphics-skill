"""
Small-multiples renderer — a grid of mini charts that share scale and styling so
the eye compares shapes across many categories at once (one panel per segment,
cohort, region, model, ...). This is the a16z "same chart, many slices" layout.

Spec shape:

    {
      "chart_type": "small_multiples",
      "panel_type": "line",          // "line" (default) | "bar"
      "columns": 3,                  // grid width (default: min(3, n))
      "shared_y": true,              // common y scale for honest comparison
      "fill": false,                 // area fill for line panels
      "x": ["2022", "2023", "2024"], // shared x (or give per-panel "x")
      "panels": [
        { "title": "Enterprise", "values": [12, 18, 25] },
        { "title": "Mid-market", "values": [ 8, 11, 14] },
        { "title": "SMB",        "values": [ 5,  6,  6] }
      ]
    }
"""

from __future__ import annotations

import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .base import apply_titles, register
from theme import color_for_index, hex_to_rgba


@register("small_multiples")
def render(spec: dict, theme: dict) -> go.Figure:
    panels = spec.get("panels") or []
    if not panels:
        raise ValueError("small_multiples spec needs a non-empty 'panels' list")
    for i, p in enumerate(panels):
        if "values" not in p:
            raise ValueError(f"Panel #{i} is missing required 'values'")

    n = len(panels)
    cols = int(spec.get("columns") or min(3, n))
    cols = max(1, cols)
    rows = math.ceil(n / cols)
    panel_type = spec.get("panel_type", "line")
    shared_y = bool(spec.get("shared_y", True))
    fill = bool(spec.get("fill", False))
    accent = color_for_index(theme, 0)
    shared_x = spec.get("x")

    titles = [p.get("title", "") for p in panels] + [""] * (rows * cols - n)
    fig = make_subplots(
        rows=rows, cols=cols, subplot_titles=titles,
        shared_yaxes=shared_y, shared_xaxes=False,
        horizontal_spacing=min(0.08, 0.9 / cols),
        vertical_spacing=min(0.16, 0.9 / rows),
    )

    for i, p in enumerate(panels):
        r, c = i // cols + 1, i % cols + 1
        x = p.get("x") or shared_x or list(range(len(p["values"])))
        color = p.get("color") or accent
        if panel_type == "bar":
            fig.add_trace(go.Bar(
                x=x, y=p["values"], marker=dict(color=color, line=dict(width=0)),
                hovertemplate="%{x}: %{y}<extra></extra>"), row=r, col=c)
        else:
            fig.add_trace(go.Scatter(
                x=x, y=p["values"], mode="lines", line=dict(color=color, width=2.5),
                fill="tozeroy" if fill else None,
                fillcolor=hex_to_rgba(color, 0.16) if fill else None,
                hovertemplate="%{x}: %{y}<extra></extra>"), row=r, col=c)

    # Minimal shared styling across every panel's axes.
    grid = theme.get("grid_color", "rgba(0,0,0,0.08)")
    tick = dict(family=theme["font_family"], size=theme["label_size"] - 2,
                color=theme.get("subtitle_color", theme["font_color"]))
    fig.update_xaxes(showgrid=False, zeroline=False, showline=False, ticks="",
                     tickfont=tick)
    fig.update_yaxes(showgrid=True, gridcolor=grid, zeroline=False, showline=False,
                     ticks="", tickfont=tick,
                     tickprefix=spec.get("value_prefix", ""),
                     ticksuffix=spec.get("value_suffix", ""))

    # Force ONE shared y range across every panel. make_subplots' shared_yaxes
    # only links axes within a row, which would let different rows use different
    # scales — the cardinal sin of small multiples (it hides real differences).
    if shared_y:
        allv = [v for p in panels for v in p["values"]]
        gmin, gmax = min(allv), max(allv)
        if fill or panel_type == "bar":
            yr = [min(0, gmin), gmax * 1.08]
        else:
            span = (gmax - gmin) or 1
            yr = [gmin - span * 0.12, gmax + span * 0.12]
        fig.update_yaxes(range=yr)

    # Style the panel titles (make_subplots adds them as annotations).
    for ann in fig.layout.annotations:
        ann.font = dict(family=theme["font_family"], size=theme["label_size"],
                        color=theme["title_color"])
        ann.xanchor = "left"
        ann.x = ann.x - 0.0  # keep position; just left-align text

    fig.update_layout(
        showlegend=False,
        margin=dict(t=140, l=56, r=30, b=60),
        height=spec.get("height", 240 * rows + 140),
        width=spec.get("width", 1080),
        bargap=0.3,
    )
    apply_titles(fig, spec, theme, x_shift=-(56 - 28))  # headline to canvas edge
    return fig
