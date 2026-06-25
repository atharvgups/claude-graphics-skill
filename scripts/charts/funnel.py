"""
Funnel chart renderer (second chart type — proves the engine generalizes).

A funnel is the natural companion to a Sankey for conversion storytelling: a
single sequence of stages that shrinks from top to bottom, with each bar showing
its absolute value and its share of the starting cohort. It uses a completely
different Plotly trace (`go.Funnel`) and a cartesian layout rather than Sankey's
node/link model — which is the point: it demonstrates that adding a chart type
needs nothing but a new module + a `@register` call. Themes and the
title/subtitle/source furniture come for free.

Spec shape:

    {
      "chart_type": "funnel",
      "title": "...", "subtitle": "...", "source": "...",
      "theme": "simula",
      "value_format": ",.0f", "value_prefix": "", "value_suffix": " users",
      "stages": [
        { "label": "Site visitors", "value": 50000, "color": "#optional" },
        { "label": "Signups",       "value": 12000 },
        ...
      ]
    }

Stages render top-to-bottom in the order given. Each bar's label shows the
formatted value and its percentage of the first (top) stage, so the drop-off
story is readable at a glance without hover.
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import apply_titles, format_value, register
from theme import color_for_index, hex_to_rgba


@register("funnel")
def render(spec: dict, theme: dict) -> go.Figure:
    stages = spec.get("stages") or []
    if not stages:
        raise ValueError("Funnel spec needs a non-empty 'stages' list")

    labels, values, colors = [], [], []
    for i, stage in enumerate(stages):
        if "value" not in stage:
            raise ValueError(f"Stage #{i} is missing required 'value': {stage!r}")
        labels.append(stage.get("label", f"Stage {i + 1}"))
        values.append(float(stage["value"]))
        colors.append(stage.get("color") or color_for_index(theme, i))

    # Build our own bar text so the themed value format (prefix/suffix) applies
    # and we can pair the absolute value with its share of the top of funnel —
    # Plotly's built-in textinfo can't honor custom value formatting.
    top = values[0] if values[0] else 1.0
    # Bold the value, keep the share lighter — same hierarchy as a Sankey label.
    bar_text = [
        f"<b>{format_value(v, spec)}</b>   {v / top * 100:.0f}%" for v in values
    ]

    fig = go.Figure(
        go.Funnel(
            y=labels,
            x=values,
            text=bar_text,
            textinfo="text",
            # "auto" keeps labels inside the wide top bars but pushes them
            # outside the narrow bottom bars (steep funnels can shrink to a
            # sliver), so every stage's value stays legible.
            textposition="auto",
            textfont=dict(
                family=theme["font_family"],
                size=theme["label_size"] + 1,
                color=theme["font_color"],
            ),
            # Crisp 2px edge in the canvas color separates stacked stages
            # cleanly without the heavy outlined look.
            marker=dict(
                color=colors,
                line=dict(color=theme["paper_bg"], width=2),
            ),
            # The default dotted connector reads as cheap/janky. A faint *filled*
            # connector instead joins the stages into one continuous funnel
            # silhouette — the classic infographic look — with no visible line.
            connector=dict(
                fillcolor=hex_to_rgba(theme["source_color"], 0.18),
                line=dict(width=0),
            ),
            hovertemplate="%{y}: %{text}<extra></extra>",
        )
    )

    # Hide the x axis entirely; keep y category labels (the stage names) but
    # strip grid/baseline so the bars sit on a clean canvas.
    fig.update_xaxes(visible=False)
    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        showline=False,
        # Size the left margin to the labels ourselves (rather than letting
        # automargin do it) so we know exactly how wide it is and can pull the
        # title block back to the canvas edge by the same amount — keeping the
        # title aligned the same way it is on charts with no left axis.
        automargin=False,
        tickfont=dict(
            family=theme["font_family"],
            size=theme["label_size"],
            color=theme["font_color"],
        ),
    )
    longest = max((len(l) for l in labels), default=0)
    left_margin = min(320, max(120, int(longest * theme["label_size"] * 0.62) + 24))
    fig.update_layout(
        margin=dict(t=120, l=left_margin, r=24, b=70),
        height=spec.get("height", 620),
        width=spec.get("width", 1000),
        funnelmode="stack",
    )
    # Plot area starts at left_margin; shift the title block back to ~24px in.
    apply_titles(fig, spec, theme, x_shift=-(left_margin - 24))
    return fig
