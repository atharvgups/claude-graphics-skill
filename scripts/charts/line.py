"""
Line / area chart renderer — for trends over time or any ordered x.

Tuned to the a16z multi-line house style:
  * **Maximally-separated colors** (`line_palette`) so adjacent lines never read
    as the same hue, reinforced by a **dash-style cycle** (solid → dot → dash-dot
    …) — a16z distinguishes series by color *and* dash, which also survives B&W.
  * **Circle-dot legend** (not line swatches) for multi-series; a **single series
    gets NO legend** — the title/subtitle carry it (a16z never legends one line).
  * Optional **end-of-line value labels** (`end_values`) — the final number
    printed at each line's right end in its color (a16z chart 6).
  * Optional markers (`markers`) drawn with a paper-colored halo so dots sit
    cleanly on the line.
  * Area via `fill` (flat tint) or `stacked` (stacked area, dot legend + the
    broad stack palette).

Spec shape:

    {
      "chart_type": "line",
      "x": ["2019", "2020", "2021", ...],
      "series": [
        { "name": "Technology", "values": [12, 18, 25, ...], "color": "#opt",
          "dash": "solid|dot|dash|dashdot" },
        { "name": "Software",   "values": [ 8, 11, 19, ...] }
      ],
      "fill": false, "stacked": false, "markers": false,
      "dash_styles": true,            // cycle dash per series (auto when >1 line)
      "end_values": false,            // label each line's final value at its end
      "label_mode": "legend"          // "legend" | "end" (name labels at line end)
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import (add_circle_legend, apply_footer, apply_titles,
                   cartesian_axes, format_value, register)
from theme import hex_to_rgba

# Dash cycle: the lead series stays solid (emphasis), the rest take distinct
# patterns — matches how a16z separates overlapping lines.
_DASHES = ["solid", "dot", "dashdot", "dash", "longdash", "longdashdot"]


@register("line")
def render(spec: dict, theme: dict) -> go.Figure:
    x = spec.get("x") or []
    series = spec.get("series") or []
    if not x:
        raise ValueError("Line spec needs a non-empty 'x' list")
    if not series:
        raise ValueError("Line spec needs a non-empty 'series' list")

    fill = bool(spec.get("fill", False))
    stacked = bool(spec.get("stacked", False))
    markers = bool(spec.get("markers", False))
    mode = "lines+markers" if markers else "lines"
    label_mode = spec.get("label_mode", "legend")
    end_values = bool(spec.get("end_values", False))
    single = len(series) == 1

    # String x → categorical axis (even spacing; safe annotation refs by index).
    is_cat = any(isinstance(xi, str) for xi in x)
    line_pal = theme.get("line_palette") or theme["palette"]
    stack_pal = theme.get("stack_palette") or line_pal
    # Dash variation is on by default for multiple plain lines; off for areas
    # (the fill already separates them) and single series.
    use_dash = spec.get("dash_styles", len(series) > 1 and not (stacked or fill))

    fig = go.Figure()
    colors, names = [], []
    for i, s in enumerate(series):
        if "values" not in s:
            raise ValueError(f"Series #{i} is missing required 'values'")
        if s.get("color"):
            c = s["color"]
        elif stacked:
            c = stack_pal[i % len(stack_pal)]
        else:
            c = line_pal[i % len(line_pal)]
        colors.append(c)
        names.append(s.get("name", f"Series {i + 1}"))
        dash = s.get("dash") or (_DASHES[i % len(_DASHES)] if use_dash else "solid")
        trace = dict(
            x=x, y=s["values"], name=names[-1], mode=mode,
            line=dict(color=c, width=3, dash=dash),
            marker=dict(color=c, size=8,
                        line=dict(color=theme["paper_bg"], width=1.5)),
            hovertemplate="%{fullData.name}: %{y}<extra></extra>",
            showlegend=False,  # legend handled explicitly below
        )
        if stacked:
            trace["stackgroup"] = "one"
            trace["fillcolor"] = hex_to_rgba(c, 0.65)
            trace["line"]["dash"] = "solid"
        elif fill:
            trace["fill"] = "tozeroy"
            if single:
                # a16z single-area look: a vertical gradient fading the fill from
                # the line color down to transparent at the baseline.
                trace["fillgradient"] = dict(
                    type="vertical",
                    colorscale=[[0, hex_to_rgba(c, 0.0)],
                                [1, hex_to_rgba(c, 0.42)]])
            else:
                trace["fillcolor"] = hex_to_rgba(c, 0.16)
        fig.add_trace(go.Scatter(**trace))

    # End-of-line labels are pinned to the plot's right edge in PAPER x (with the
    # data y) — never x=x[-1], because referencing a categorical x value from an
    # annotation coerces the whole x-axis to numeric and collapses the data.
    def _end_label(y, text, color, size_bump=0, shift=10):
        fig.add_annotation(
            xref="paper", x=1.0, xshift=shift, yref="y", y=y,
            text=text, xanchor="left", showarrow=False,
            font=dict(family=theme["font_family"],
                      size=theme["label_size"] + size_bump, color=color),
        )

    right, bottom = 36, 118
    if label_mode == "end" and not single:
        # Direct NAME labels at the end of each line — no legend.
        for i, s in enumerate(series):
            _end_label(s["values"][-1], f"<b>{names[i]}</b>", colors[i], shift=12)
        right, bottom = 188, 84
    elif single:
        bottom = 96  # title carries it; no legend
    else:
        add_circle_legend(fig, names, colors, theme)
        bottom = 120

    # End-of-line VALUE labels (a16z chart 6): bold final number in series color.
    if end_values:
        for i, s in enumerate(series):
            _end_label(s["values"][-1],
                       f"<b>{format_value(s['values'][-1], spec)}</b>",
                       colors[i], size_bump=1)
        right = max(right, 104)

    # Per-point VALUE labels (a16z chart 8): bold value above each marker.
    # Reference points by category INDEX (x=j, xref="x") not the label string —
    # a string x on an unset xref defaults to paper and flies off-canvas.
    if spec.get("point_labels"):
        for i, s in enumerate(series):
            for j, yi in enumerate(s["values"]):
                fig.add_annotation(
                    x=(j if is_cat else x[j]), xref="x", yref="y", y=yi, yshift=15,
                    text=format_value(yi, spec), showarrow=False,
                    font=dict(family=theme["font_family"],
                              size=theme["label_size"], color=colors[i]))

    # Shaded period bands (recession/forecast shading): faint vertical regions
    # spanning an x-range, drawn beneath the lines.
    for band in spec.get("bands", []):
        bf, bt = band.get("from"), band.get("to")
        bx0 = x.index(bf) if (is_cat and bf in x) else bf
        bx1 = x.index(bt) if (is_cat and bt in x) else bt
        fig.add_vrect(x0=bx0, x1=bx1, layer="below", line_width=0,
                      fillcolor=hex_to_rgba(theme["title_color"], 0.06))
        if band.get("label"):
            fig.add_annotation(
                x=(bx0 + bx1) / 2, xref="x", y=1.0, yref="paper",
                yanchor="bottom", yshift=3, text=band["label"], showarrow=False,
                xanchor="center", font=dict(family=theme["font_family"],
                                            size=theme["label_size"] - 1,
                                            color=theme.get("subtitle_color",
                                                            theme["font_color"])))

    # Event markers (annotated time series): dotted vertical rules with a small
    # top label at given x positions — "what happened, and when".
    for ev in spec.get("events", []):
        ex = ev.get("x")
        xpos = x.index(ex) if (is_cat and ex in x) else ex
        fig.add_vline(x=xpos, layer="below",
                      line=dict(color=hex_to_rgba(theme["title_color"], 0.38),
                                width=1.2, dash="dot"))
        fig.add_annotation(
            x=xpos, xref="x", y=1.0, yref="paper", yanchor="bottom", yshift=3,
            text=ev.get("label", ""), showarrow=False, xanchor="center",
            font=dict(family=theme["font_family"], size=theme["label_size"] - 1,
                      color=theme.get("subtitle_color", theme["font_color"])))

    has_footer = bool(spec.get("footer") or spec.get("wordmark"))
    if has_footer:
        bottom = max(bottom, 226)

    cartesian_axes(fig, theme, spec, x_grid=False, y_grid=True)
    # Force a categorical x-axis when labels are strings: it keeps even spacing
    # and — critically — lets annotations safely reference x values without
    # coercing the axis to numeric (which silently collapses the data).
    if is_cat:
        fig.update_xaxes(type="category")
    fig.update_layout(
        margin=dict(t=120, l=62, r=right, b=bottom),
        height=spec.get("height", 620),
        width=spec.get("width", 1040),
        hovermode="x unified",
    )
    if has_footer:
        apply_titles(fig, {**spec, "source": ""}, theme)
        apply_footer(fig, spec, theme)
    else:
        apply_titles(fig, spec, theme)
    return fig
