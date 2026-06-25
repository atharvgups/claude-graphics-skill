"""
Scatter / bubble chart renderer — for relationships between two variables.

  * Plain x/y points, or grouped into colored `series`.
  * Optional `size` per point turns it into a bubble chart (area-scaled so big
    values don't visually dominate).
  * Optional per-point `label` (set `show_labels`) for callout-style charts.

Spec shape:

    {
      "chart_type": "scatter",
      "x_title": "Spend ($K)", "y_title": "Retention (%)",
      "show_labels": true,
      "points": [ { "x": 12, "y": 48, "label": "Acme", "size": 30 }, ... ]
      // OR grouped:
      // "series": [ { "name": "SMB", "points": [ {"x":..,"y":..}, ... ] }, ... ]
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import apply_titles, cartesian_axes, register, style_legend
from theme import color_for_index


def _sizes(points):
    """Area-scaled marker sizes from optional per-point `size`, else a constant."""
    raw = [p.get("size") for p in points]
    if not any(s is not None for s in raw):
        return 14
    biggest = max((abs(s) for s in raw if s is not None), default=1) or 1
    return [(abs(s) / biggest) ** 0.5 * 46 + 9 if s is not None else 12 for s in raw]


def render_points(fig, points, name, color, theme, show_labels):
    fig.add_trace(go.Scatter(
        x=[p["x"] for p in points],
        y=[p["y"] for p in points],
        mode="markers+text" if show_labels else "markers",
        name=name,
        text=[p.get("label", "") for p in points] if show_labels else None,
        textposition="top center",
        textfont=dict(family=theme["font_family"], size=theme["label_size"],
                      color=theme["font_color"]),
        marker=dict(color=color, size=_sizes(points), line=dict(width=0),
                    opacity=0.82),
        hovertemplate="(%{x}, %{y})<extra></extra>",
    ))


@register("scatter")
def render(spec: dict, theme: dict) -> go.Figure:
    series = spec.get("series")
    points = spec.get("points")
    show_labels = bool(spec.get("show_labels", False))
    fig = go.Figure()

    if series:
        for i, s in enumerate(series):
            render_points(fig, s.get("points", []), s.get("name", f"Series {i + 1}"),
                          s.get("color") or color_for_index(theme, i), theme, show_labels)
        style_legend(fig, theme)
        bottom = 118
    elif points:
        render_points(fig, points, "", color_for_index(theme, 0), theme, show_labels)
        fig.update_layout(showlegend=False)
        bottom = 70
    else:
        raise ValueError("Scatter spec needs 'points' or 'series'")

    cartesian_axes(fig, theme, spec, x_grid=True, y_grid=True)
    axis_font = dict(family=theme["font_family"], size=theme["label_size"] + 1,
                     color=theme.get("subtitle_color", theme["font_color"]))
    fig.update_xaxes(title=dict(text=spec.get("x_title", ""), font=axis_font))
    fig.update_yaxes(title=dict(text=spec.get("y_title", ""), font=axis_font))
    fig.update_layout(
        margin=dict(t=120, l=72, r=40, b=bottom),
        height=spec.get("height", 640),
        width=spec.get("width", 1000),
    )
    apply_titles(fig, spec, theme)
    return fig
