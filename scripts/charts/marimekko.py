"""
Marimekko / mosaic renderer — variable-width 100%-stacked columns.

Encodes TWO dimensions at once: each column's **width** is its category size
(e.g. market size, headcount), and the stacked segments are that category's
**composition**. An a16z favorite for "big market, and here's the mix" stories.

Spec shape:

    {
      "chart_type": "marimekko",
      "categories": [ { "name": "Cloud", "total": 420 }, ... ],   // width = total
      "segments":   [ { "name": "AWS", "values": [..per category..] }, ... ],
      "value_suffix": "%"
    }

If a category omits `total`, its width is the sum of its segment values.
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import (add_circle_legend, apply_footer, apply_titles, edge_align,
                   register)
from theme import hex_to_rgba


def _ideal_text(hex_color, theme):
    """White on dark segments, navy on light ones — keeps in-cell labels legible."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#FFFFFF" if lum < 0.6 else theme["title_color"]


@register("marimekko")
def render(spec: dict, theme: dict) -> go.Figure:
    cats = spec.get("categories") or []
    segments = spec.get("segments") or []
    if not cats or not segments:
        raise ValueError("Marimekko needs 'categories' and 'segments'")
    ncat = len(cats)

    def col_sum(j):
        return sum(s["values"][j] for s in segments) or 1

    totals = [cats[j].get("total", col_sum(j)) for j in range(ncat)]
    grand = sum(totals) or 1
    widths = [t / grand * 100 for t in totals]
    centers, cum = [], 0.0
    for w in widths:
        centers.append(cum + w / 2)
        cum += w

    pal = theme.get("stack_palette") or theme["palette"]
    fig = go.Figure()
    for i, s in enumerate(segments):
        c = s.get("color") or pal[i % len(pal)]
        ys, texts = [], []
        for j in range(ncat):
            pct = s["values"][j] / col_sum(j) * 100
            ys.append(pct)
            texts.append(f"{pct:.0f}%" if pct >= 8 else "")  # hide tiny cells
        fig.add_trace(go.Bar(
            x=centers, y=ys, width=widths,
            name=s.get("name", f"Series {i + 1}"),
            marker=dict(color=c, line=dict(color=theme["paper_bg"], width=1.2)),
            text=texts, textposition="inside", insidetextanchor="middle",
            textfont=dict(family=theme["font_family"], size=theme["label_size"],
                          color=_ideal_text(c, theme)),
            showlegend=False,
            hovertemplate="%{text}<extra>" + s.get("name", "") + "</extra>",
        ))

    add_circle_legend(
        fig, [s.get("name", f"Series {i + 1}") for i, s in enumerate(segments)],
        [s.get("color") or pal[i % len(pal)] for i, s in enumerate(segments)],
        theme)

    # Category labels on top: name over its width-share.
    ticktext = [f"<b>{cats[j].get('name', '')}</b><br>"
                f"<span style='font-size:0.82em'>{widths[j]:.0f}%</span>"
                for j in range(ncat)]
    has_footer = bool(spec.get("footer") or spec.get("wordmark"))
    fig.update_layout(
        barmode="stack", bargap=0,
        height=spec.get("height", 680), width=spec.get("width", 1080),
        margin=dict(t=150, l=40, r=40, b=300 if has_footer else 124),
    )
    fig.update_xaxes(range=[0, 100], tickmode="array", tickvals=centers,
                     ticktext=ticktext, showgrid=False, zeroline=False,
                     showline=False, ticks="", side="top",
                     tickfont=dict(family=theme["font_family"],
                                   size=theme["label_size"],
                                   color=theme["title_color"]))
    fig.update_yaxes(range=[0, 100], showgrid=False, zeroline=False,
                     showline=False, ticks="", showticklabels=False)

    al = edge_align(spec.get("width", 1080), 40, 40, 28)
    fig.update_layout(legend=dict(x=al["legend_x"]))
    if has_footer:
        apply_titles(fig, {**spec, "source": ""}, theme, x_shift=al["x_shift"])
        apply_footer(fig, spec, theme, x_shift=al["x_shift"],
                     rule_x=al["rule_x"], wordmark_xshift=al["wordmark_xshift"])
    else:
        apply_titles(fig, spec, theme, x_shift=al["x_shift"])
    return fig
