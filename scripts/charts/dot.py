"""
Dot-plot renderer — lollipop or dumbbell. A cleaner alternative to bars for
rankings, and the go-to for before/after comparisons.

Two modes, auto-detected from the data:
  * **Lollipop** — items with a single `value`: a thin stem from zero to a dot.
  * **Dumbbell** — items with `start` and `end`: two dots joined by a bar, ideal
    for "moved from X to Y" (e.g. 2020 vs 2026).

Spec shape:

    {
      "chart_type": "dot",
      "highlight": ["Writing code"],            // optional emphasis (lollipop)
      "items": [
        { "label": "Writing code", "value": 7.4 },          // lollipop
        // ...or dumbbell:
        { "label": "Sales", "start": 20, "end": 45 }
      ]
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import apply_titles, cartesian_axes, format_value, register
from theme import color_for_index, hex_to_rgba


@register("dot")
def render(spec: dict, theme: dict) -> go.Figure:
    items = spec.get("items") or []
    if not items:
        raise ValueError("Dot spec needs a non-empty 'items' list")

    dumbbell = all(("start" in it and "end" in it) for it in items)
    if not dumbbell and not all("value" in it for it in items):
        raise ValueError("Dot items need either 'value' (lollipop) or "
                         "'start'+'end' (dumbbell)")

    labels = [it.get("label", f"#{i + 1}") for i, it in enumerate(items)]
    n = len(items)
    # Numeric y positions, reversed so the first item sits at the top.
    ypos = list(range(n - 1, -1, -1))

    accent = color_for_index(theme, 0)
    start_c = hex_to_rgba(theme["font_color"], 0.35)
    stem = hex_to_rgba(theme["font_color"], 0.30)

    fig = go.Figure()
    label_font = dict(family=theme["font_family"], size=theme["label_size"],
                      color=theme["font_color"])

    if dumbbell:
        end_c = color_for_index(theme, 0)
        for it, y in zip(items, ypos):
            fig.add_shape(type="line", x0=it["start"], x1=it["end"], y0=y, y1=y,
                          line=dict(color=hex_to_rgba(theme["font_color"], 0.45),
                                    width=4), layer="below")
        starts = [float(it["start"]) for it in items]
        ends = [float(it["end"]) for it in items]
        fig.add_trace(go.Scatter(
            x=starts, y=ypos, mode="markers", name=spec.get("start_name", "Start"),
            marker=dict(color=start_c, size=15, line=dict(width=0)),
            hovertemplate="%{x}<extra></extra>"))
        fig.add_trace(go.Scatter(
            x=ends, y=ypos, mode="markers", name=spec.get("end_name", "End"),
            marker=dict(color=end_c, size=15, line=dict(width=0)),
            hovertemplate="%{x}<extra></extra>"))
        for v, y in zip(ends, ypos):
            fig.add_annotation(x=v, y=y, text=f"<b>{format_value(v, spec)}</b>",
                               xanchor="left", xshift=12, showarrow=False,
                               font=label_font)
        fig.update_layout(showlegend=False)
    else:
        values = [float(it["value"]) for it in items]
        # Optional highlight: chosen items accent, others muted.
        hl = spec.get("highlight")
        hl = hl if isinstance(hl, list) else ([hl] if hl is not None else None)
        hlset = set(hl) if hl else None
        colors = [
            accent if (hlset is None or labels[i] in hlset or i in (hl or []))
            else theme.get("muted_color", "#BBB")
            for i in range(n)
        ]
        for v, y, c in zip(values, ypos, colors):
            fig.add_shape(type="line", x0=0, x1=v, y0=y, y1=y,
                          line=dict(color=stem, width=2), layer="below")
        fig.add_trace(go.Scatter(
            x=values, y=ypos, mode="markers",
            marker=dict(color=colors, size=18, line=dict(width=0)),
            hovertemplate="%{x}<extra></extra>"))
        for v, y in zip(values, ypos):
            fig.add_annotation(x=v, y=y, text=f"<b>{format_value(v, spec)}</b>",
                               xanchor="left", xshift=14, showarrow=False,
                               font=label_font)
        fig.update_layout(showlegend=False)

    cartesian_axes(fig, theme, spec, x_grid=True, y_grid=False, value_axis="x")
    fig.update_yaxes(tickmode="array", tickvals=ypos, ticktext=labels,
                     showgrid=False, tickfont=label_font,
                     range=[-0.7, n - 0.3])
    # Headroom on the right for the value labels.
    xmax = max((it.get("end", it.get("value", 0)) for it in items), default=1)
    xmin = min((it.get("start", 0) for it in items), default=0) if dumbbell else 0
    pad = (xmax - xmin) * 0.12 or 1
    fig.update_xaxes(range=[xmin - (pad if dumbbell else 0), xmax + pad])
    left = min(320, max(90, max((len(l) for l in labels), default=0) * 9 + 24))
    fig.update_layout(margin=dict(t=120, l=left, r=40, b=70),
                      height=spec.get("height", 600),
                      width=spec.get("width", 1000))
    apply_titles(fig, spec, theme, x_shift=-(left - 24))
    if dumbbell:
        from .base import style_legend
        style_legend(fig, theme)
        fig.update_layout(showlegend=True, margin=dict(t=120, l=left, r=40, b=118))
    return fig
