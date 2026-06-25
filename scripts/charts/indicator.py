"""
Indicator renderers — the dashboard/KPI family, all built on go.Indicator:

  * `bignumber` — one or more big-number callouts, each with an optional delta
    vs a reference (the "headline metric" tiles atop a report).
  * `gauge`     — a single value on a dial, with an optional target threshold.
  * `bullet`    — actual-vs-target bars, the compact KPI-tracking layout.

Shared: `value_prefix` / `value_suffix` format the numbers; deltas color green
(up) / rust (down) on theme.
"""

from __future__ import annotations

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .base import apply_titles, register
from theme import color_for_index


def _delta(theme, reference, relative=False):
    return dict(reference=reference, relative=relative,
                increasing=dict(color=color_for_index(theme, 0)),
                decreasing=dict(color=color_for_index(theme, 4)),
                font=dict(family=theme["font_family"]))


@register("bignumber")
def render_bignumber(spec: dict, theme: dict) -> go.Figure:
    metrics = spec.get("metrics")
    if not metrics:
        if "value" not in spec:
            raise ValueError("bignumber needs 'metrics' or a 'value'")
        metrics = [{"label": spec.get("label", ""), "value": spec["value"],
                    "reference": spec.get("reference")}]
    n = len(metrics)
    fig = make_subplots(rows=1, cols=n,
                        specs=[[{"type": "indicator"} for _ in range(n)]])
    for i, m in enumerate(metrics):
        ref = m.get("reference")
        fig.add_trace(go.Indicator(
            mode="number+delta" if ref is not None else "number",
            value=m["value"],
            number=dict(prefix=spec.get("value_prefix", ""),
                        suffix=spec.get("value_suffix", ""),
                        font=dict(family=theme["font_family"],
                                  color=theme["title_color"], size=56)),
            delta=_delta(theme, ref, spec.get("relative_delta", False)) if ref is not None else None,
            title=dict(text=m.get("label", ""),
                       font=dict(family=theme["font_family"],
                                 color=theme["subtitle_color"],
                                 size=theme["label_size"] + 3)),
        ), row=1, col=i + 1)
    fig.update_layout(margin=dict(t=140, l=30, r=30, b=62),
                      height=spec.get("height", 340),
                      width=spec.get("width", 280 * n + 60))
    apply_titles(fig, spec, theme)
    return fig


@register("gauge")
def render_gauge(spec: dict, theme: dict) -> go.Figure:
    if "value" not in spec:
        raise ValueError("gauge needs a 'value'")
    value = spec["value"]
    target = spec.get("target")
    rng = spec.get("range") or [0, (value or 1) * 1.5]
    accent = color_for_index(theme, 0)
    grid = theme.get("grid_color", "rgba(0,0,0,0.1)")
    tick = dict(family=theme["font_family"], size=theme["label_size"],
                color=theme.get("subtitle_color", theme["font_color"]))
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta" if target is not None else "gauge+number",
        value=value,
        number=dict(prefix=spec.get("value_prefix", ""),
                    suffix=spec.get("value_suffix", ""),
                    font=dict(family=theme["font_family"],
                              color=theme["title_color"], size=46)),
        delta=_delta(theme, target) if target is not None else None,
        gauge=dict(axis=dict(range=rng, tickfont=tick, tickcolor=grid),
                   bar=dict(color=accent), bgcolor=theme["plot_bg"],
                   borderwidth=0,
                   threshold=dict(line=dict(color=color_for_index(theme, 4), width=4),
                                  value=target) if target is not None else None),
    ))
    fig.update_layout(margin=dict(t=130, l=50, r=50, b=62),
                      height=spec.get("height", 520),
                      width=spec.get("width", 760))
    apply_titles(fig, spec, theme, x_shift=-26)
    return fig


@register("bullet")
def render_bullet(spec: dict, theme: dict) -> go.Figure:
    items = spec.get("items") or []
    if not items:
        raise ValueError("bullet needs a non-empty 'items' list")
    n = len(items)
    accent = color_for_index(theme, 0)
    fig = make_subplots(rows=n, cols=1, vertical_spacing=0.5 / max(n, 1),
                        specs=[[{"type": "indicator"}] for _ in range(n)])
    for i, it in enumerate(items):
        target = it.get("target")
        mx = it.get("max", max(it["value"], target or 0) * 1.3 or 1)
        fig.add_trace(go.Indicator(
            mode="number+gauge+delta" if target is not None else "number+gauge",
            value=it["value"],
            delta=_delta(theme, target) if target is not None else None,
            number=dict(prefix=spec.get("value_prefix", ""),
                        suffix=spec.get("value_suffix", ""),
                        font=dict(family=theme["font_family"])),
            gauge=dict(shape="bullet", axis=dict(range=[0, mx]),
                       bar=dict(color=accent), bgcolor=theme["plot_bg"],
                       borderwidth=0,
                       threshold=dict(line=dict(color=color_for_index(theme, 4), width=3),
                                      value=target) if target is not None else None),
            title=dict(text=it.get("label", ""),
                       font=dict(family=theme["font_family"],
                                 color=theme["font_color"],
                                 size=theme["label_size"])),
        ), row=i + 1, col=1)
    fig.update_layout(margin=dict(t=130, l=140, r=50, b=70),
                      height=spec.get("height", 90 * n + 150),
                      width=spec.get("width", 1000))
    apply_titles(fig, spec, theme, x_shift=-116)
    return fig
