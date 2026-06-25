"""
Scatter / bubble chart renderer — for relationships between two variables.

  * Plain x/y points, or grouped into colored `series`.
  * Optional `size` per point turns it into a bubble chart (area-scaled so big
    values don't visually dominate).
  * Optional per-point `label` (set `show_labels`) for callout-style charts.
  * `highlight` (point label(s)) accents the story point(s), muting the rest.
  * `trendline: true` draws a dashed least-squares fit line (a16z shows the
    correlation rather than leaving the reader to infer it).

Spec shape:

    {
      "chart_type": "scatter",
      "x_title": "Spend ($K)", "y_title": "Retention (%)",
      "show_labels": true, "trendline": true, "highlight": ["Enterprise"],
      "points": [ { "x": 12, "y": 48, "label": "Acme", "size": 30 }, ... ]
      // OR grouped:
      // "series": [ { "name": "SMB", "points": [ {"x":..,"y":..}, ... ] }, ... ]
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import apply_titles, cartesian_axes, register, style_legend
from theme import color_for_index, hex_to_rgba


def _sizes(points):
    """Area-scaled marker sizes from optional per-point `size`, else a constant."""
    raw = [p.get("size") for p in points]
    if not any(s is not None for s in raw):
        return 15
    biggest = max((abs(s) for s in raw if s is not None), default=1) or 1
    return [(abs(s) / biggest) ** 0.5 * 46 + 10 if s is not None else 13
            for s in raw]


def _trend(points):
    """Least-squares line endpoints across the x-range, or None if degenerate."""
    xs = [p["x"] for p in points]
    ys = [p["y"] for p in points]
    n = len(xs)
    if n < 2:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    var = sum((v - mx) ** 2 for v in xs)
    if var == 0:
        return None
    slope = sum((vx - mx) * (vy - my) for vx, vy in zip(xs, ys)) / var
    b = my - slope * mx
    lo, hi = min(xs), max(xs)
    return (lo, slope * lo + b, hi, slope * hi + b)


def render_points(fig, points, name, colors, theme, show_labels, label_colors=None):
    # Markers carry a paper-colored halo so overlapping bubbles stay crisp.
    fig.add_trace(go.Scatter(
        x=[p["x"] for p in points],
        y=[p["y"] for p in points],
        mode="markers+text" if show_labels else "markers",
        name=name,
        text=[p.get("label", "") for p in points] if show_labels else None,
        textposition="top center",
        textfont=dict(family=theme["font_family"], size=theme["label_size"] + 1,
                      color=label_colors or theme["title_color"]),
        marker=dict(color=colors, size=_sizes(points),
                    line=dict(color=theme["paper_bg"], width=1.5), opacity=0.9),
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
            render_points(fig, s.get("points", []),
                          s.get("name", f"Series {i + 1}"),
                          s.get("color") or color_for_index(theme, i),
                          theme, show_labels)
        style_legend(fig, theme)
        bottom = 118
    elif points:
        accent = color_for_index(theme, 0)
        hl = spec.get("highlight")
        if hl is not None:
            hl = hl if isinstance(hl, list) else [hl]
            muted = hex_to_rgba(theme["font_color"], 0.34)
            colors = [accent if p.get("label") in hl else muted for p in points]
            label_colors = [theme["title_color"] if p.get("label") in hl
                            else theme.get("source_color") for p in points]
        else:
            colors, label_colors = accent, theme["title_color"]

        # Trendline first so it sits beneath the points.
        if spec.get("trendline"):
            t = _trend(points)
            if t:
                fig.add_trace(go.Scatter(
                    x=[t[0], t[2]], y=[t[1], t[3]], mode="lines",
                    line=dict(color=hex_to_rgba(accent, 0.5), width=2, dash="dash"),
                    hoverinfo="skip", showlegend=False))

        render_points(fig, points, "", colors, theme, show_labels, label_colors)
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
