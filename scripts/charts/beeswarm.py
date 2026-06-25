"""
Beeswarm / strip renderer — every observation as a dot, packed to show a
distribution's shape without hiding the raw points (a box plot's honest cousin).

Packing is deterministic (value-binned, spread symmetrically within each bin) —
no RNG — so renders are reproducible. An optional median tick per group.

Spec shape:

    {
      "chart_type": "beeswarm",
      "groups": [ { "name": "SMB", "values": [...], "color": "#opt" }, ... ],
      "y_title": "Days to close", "show_median": true
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import apply_titles, cartesian_axes, register
from theme import color_for_index, hex_to_rgba


def _swarm_x(values, center, width, nbins=26):
    """Symmetric within-bin spread → the classic beeswarm silhouette."""
    if not values:
        return []
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1
    bins, xs = {}, [center] * len(values)
    for i in sorted(range(len(values)), key=lambda k: values[k]):
        b = int((values[i] - lo) / span * (nbins - 1))
        bins.setdefault(b, []).append(i)
    for idxs in bins.values():
        m = len(idxs)
        for k, i in enumerate(idxs):
            xs[i] = center + (k - (m - 1) / 2) * width
    return xs


@register("beeswarm")
def render(spec: dict, theme: dict) -> go.Figure:
    groups = spec.get("groups") or []
    if not groups:
        raise ValueError("Beeswarm needs a non-empty 'groups' list")
    show_median = spec.get("show_median", True)
    width = spec.get("dot_spacing", 0.035)

    fig = go.Figure()
    for i, g in enumerate(groups):
        vals = g.get("values") or []
        c = g.get("color") or color_for_index(theme, i)
        xs = _swarm_x(vals, i, width)
        fig.add_trace(go.Scatter(
            x=xs, y=vals, mode="markers", name=g.get("name", f"Group {i + 1}"),
            marker=dict(color=hex_to_rgba(c, 0.85), size=9,
                        line=dict(color=theme["paper_bg"], width=0.8)),
            hovertemplate="%{y}<extra>" + g.get("name", "") + "</extra>",
            showlegend=False,
        ))
        if show_median and vals:
            s = sorted(vals)
            n = len(s)
            med = s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2
            fig.add_shape(type="line", xref="x", yref="y",
                          x0=i - 0.32, x1=i + 0.32, y0=med, y1=med,
                          line=dict(color=theme["title_color"], width=2.5))

    cartesian_axes(fig, theme, spec, x_grid=False, y_grid=True)
    fig.update_xaxes(tickmode="array", tickvals=list(range(len(groups))),
                     ticktext=[g.get("name", "") for g in groups],
                     range=[-0.6, len(groups) - 0.4],
                     tickfont=dict(family=theme["font_family"],
                                   size=theme["label_size"] + 1,
                                   color=theme["title_color"]))
    axis_font = dict(family=theme["font_family"], size=theme["label_size"] + 1,
                     color=theme.get("subtitle_color", theme["font_color"]))
    fig.update_yaxes(title=dict(text=spec.get("y_title", ""), font=axis_font))
    fig.update_layout(
        margin=dict(t=120, l=72, r=40, b=80),
        height=spec.get("height", 640), width=spec.get("width", 1020),
    )
    apply_titles(fig, spec, theme)
    return fig
