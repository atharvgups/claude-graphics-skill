"""
Bar chart renderer — the workhorse editorial chart.

This is the chart type behind most "publication-grade" graphics (the a16z /
Jason Saltzman house style): a single confident series, direct value labels on
the bars, the faintest horizontal gridlines, no spines or clutter, and a strong
serif headline carrying the story. It deliberately strips the chrome a default
Plotly bar chart shows, because the polish *is* the restraint.

Design choices that matter:
  * **Direct labels.** Each bar is labeled with its value, so the reader never
    hunts across to a y-axis. The y-axis tick labels are therefore hidden — the
    numbers live on the bars where the eye already is.
  * **One color, by default.** A categorical bar chart reads cleanest in a
    single palette color. Use `highlight` to make one or a few bars pop (the
    classic "this is the bar that matters" move) — highlighted bars keep the
    accent color while the rest fade to a muted tint.
  * **Horizontal for rankings.** Long category names (companies, countries)
    belong on a horizontal bar chart; set `"orientation": "h"`.

Spec shape:

    {
      "chart_type": "bar",
      "title": "...", "subtitle": "...", "source": "...",
      "theme": "editorial",
      "value_format": ",.0f", "value_prefix": "$", "value_suffix": "",
      "orientation": "v",            # "v" (default) | "h"
      "highlight": ["2026"],         # optional: bar label(s) or index(es) to emphasize
      "bars": [
        { "label": "2021", "value": 12, "color": "#optional" },
        ...
      ]
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import (add_circle_legend, apply_footer, apply_titles,
                   cartesian_axes, format_value, register)
from theme import hex_to_rgba


def _resolve_highlight(spec, labels):
    """Return a set of bar indices to emphasize, accepting labels or indices."""
    raw = spec.get("highlight")
    if raw is None:
        return None
    if not isinstance(raw, list):
        raw = [raw]
    wanted = set()
    for item in raw:
        if isinstance(item, int) and 0 <= item < len(labels):
            wanted.add(item)
        elif item in labels:
            wanted.add(labels.index(item))
    return wanted or None


def _render_multi(spec: dict, theme: dict) -> go.Figure:
    """
    Grouped or stacked multi-series bars — including **diverging** stacks where
    positive contributions stack up and negative ones stack down from a zero
    baseline (the a16z "scaled by contribution" look). Multi-series charts use a
    bottom legend + a real value axis rather than per-segment labels (labeling
    every block would be noise).

    Editorial signatures applied here:
      * **stack_palette** — a broader 9-tone earthy palette so 6+ stacked
        segments stay distinct yet calm (falls back to the theme palette).
      * **Circle-dot legend** — Plotly draws square swatches for bars; the
        editorial look uses round dots, so the bars are kept out of the legend
        and one data-less scatter per series supplies a circular entry.
      * **Prominent zero baseline** — the line the stack diverges from, drawn
        under the bars so it reads through the cream segment gaps.
      * **Cream segment borders** — thin canvas-colored lines between blocks.
      * Optional **footer** strip (`footer`/`wordmark`) via apply_footer.

    Flags: `"stacked": true` to stack (else grouped), `"percent": true` for a
    100%-stacked composition, `"y_dtick"` to force gridline spacing.
    """
    x = spec.get("x") or []
    series = spec["series"]
    if not x:
        raise ValueError("Multi-series bar needs an 'x' (category) list")
    stacked = bool(spec.get("stacked", False))
    percent = bool(spec.get("percent", False))  # 100%-stacked composition

    # For a 100%-stacked bar, normalize each category's stack to sum to 100.
    plot_values = [list(s["values"]) for s in series]
    if percent:
        stacked = True
        totals = [sum(plot_values[k][j] for k in range(len(series)))
                  for j in range(len(x))]
        plot_values = [[(v / totals[j] * 100 if totals[j] else 0)
                        for j, v in enumerate(vals)] for vals in plot_values]

    pal = theme.get("stack_palette") or theme["palette"]
    suffix = spec.get("value_suffix", "")

    def _color(i, s):
        return s.get("color") or pal[i % len(pal)]

    fig = go.Figure()
    # Bars carry the data; a thin canvas-colored segment border gives the subtle
    # cream gaps between stacked blocks. Bars stay out of the legend (see below).
    for i, s in enumerate(series):
        if "values" not in s:
            raise ValueError(f"Series #{i} is missing required 'values'")
        name = s.get("name", f"Series {i + 1}")
        fig.add_trace(go.Bar(
            x=x, y=plot_values[i], name=name,
            marker=dict(color=_color(i, s),
                        line=dict(color=theme["paper_bg"], width=0.8)),
            showlegend=False,
            hovertemplate="%{x} · " + name + ": %{y:.1f}" + suffix
                          + "<extra></extra>",
        ))

    # Circle-dot legend (round swatches instead of squares). traceorder="normal"
    # because Plotly auto-reverses the legend for stacked bars and we want it in
    # series/reading order, matching the data and the editorial reference.
    names = [s.get("name", f"Series {i + 1}") for i, s in enumerate(series)]
    add_circle_legend(fig, names, [_color(i, s) for i, s in enumerate(series)],
                      theme)

    fig.update_layout(
        barmode="stack" if stacked else "group",
        bargap=spec.get("bargap", 0.3), bargroupgap=0.08,
        height=spec.get("height", 720), width=spec.get("width", 1080),
    )
    cartesian_axes(fig, theme, spec, x_grid=False, y_grid=True)
    if percent:
        fig.update_yaxes(ticksuffix="%", range=[0, 100])
    if spec.get("y_dtick"):
        fig.update_yaxes(dtick=spec["y_dtick"])

    # Prominent zero baseline — drawn under the bars so it shows in the gaps and
    # reads as the divider for diverging (+/-) stacks.
    fig.add_shape(type="line", xref="paper", yref="y", x0=0, x1=1, y0=0, y1=0,
                  line=dict(color=hex_to_rgba(theme["font_color"], 0.55),
                            width=1.6),
                  layer="below")

    has_footer = bool(spec.get("footer") or spec.get("wordmark"))
    fig.update_layout(margin=dict(t=128, l=72, r=44,
                                  b=300 if has_footer else 124))

    if has_footer:
        apply_titles(fig, {**spec, "source": ""}, theme)
        apply_footer(fig, spec, theme)
    else:
        apply_titles(fig, spec, theme)
    return fig


def _split_value(value, spec):
    """Return (number_part, unit_part) so the number can read as the hero and the
    unit as a quiet sidekick. e.g. 7.4 with suffix ' hrs' -> ('7.4', 'hrs')."""
    fmt = spec.get("value_format", ",.0f")
    prefix = spec.get("value_prefix", "")
    suffix = spec.get("value_suffix", "")
    neg = isinstance(value, (int, float)) and value < 0 and prefix
    try:
        body = format(abs(value) if neg else value, fmt)
    except (ValueError, TypeError):
        body = str(value)
    return f"{'-' if neg else ''}{prefix}{body}", suffix.strip()


def _render_horizontal(spec, theme, bars, labels, values):
    """
    The editorial ranking bar — the workhorse a16z-style graphic, dialed in.

    What separates this from a default horizontal bar export:
      * **No vertical gridlines.** A single hairline baseline at zero anchors the
        bars; everything else is whitespace. Gridlines slicing through bars are
        the #1 "exported from a tool" tell.
      * **Solid muted bars.** De-emphasized bars stay solid in a warm neutral
        (not a washed-out ghost tint), so they read as real data while the one
        highlighted bar carries the accent. Warm-neutral vs. cool-teal is the
        contrast that looks *designed*.
      * **The number is the hero.** Value labels render the figure bold and the
        unit smaller/lighter beside it — and the unit is shown on the top bar
        only, killing the "7.4 hrs / 5.1 hrs / 4.3 hrs…" repetition.
      * **Typographic hierarchy.** The highlighted bar's category label and value
        go bold-navy; the rest recede. One thing shouts.
      * **Rounded bar caps + a header rule** under the title block for the
        finished, print-laid-out feel.
      * **Optional editorial `note`** — a small italic callout that fills the
        dead corner and gives the chart a human voice.
    """
    accent = theme["palette"][0]
    neg_c = theme["palette"][4 % len(theme["palette"])]  # rust, for negatives
    bar_muted = theme.get("bar_muted") or hex_to_rgba(theme["font_color"], 0.30)
    title_c = theme["title_color"]
    sub_c = theme.get("subtitle_color", theme["font_color"])
    highlight = _resolve_highlight(spec, labels)
    # Diverging ranking: bars run right (positive, accent) / left (negative, rust)
    # from a central zero line — a16z's "Spirited Away" layout.
    diverging = bool(spec.get("diverging")) or any(v < 0 for v in values)
    n = len(labels)

    # Per-bar styling. When no highlight is set, every bar is "on" (full accent);
    # with highlight, chosen bars keep the accent and the rest go solid-muted.
    bar_colors, label_colors, value_texts, cat_texts = [], [], [], []
    for i, b in enumerate(bars):
        on = (highlight is None) or (i in highlight)
        if b.get("color"):
            bar_colors.append(b["color"])
        elif diverging and highlight is None:
            bar_colors.append(accent if values[i] >= 0 else neg_c)
        elif highlight is None:
            bar_colors.append(accent)
        else:
            bar_colors.append(accent if i in highlight else bar_muted)

        num, unit = _split_value(values[i], spec)
        # Show the unit only on the first (top) row — once is enough; repeating it
        # on every bar is clutter. The subtitle already carries the full unit.
        show_unit = unit and i == 0
        main = f"<b>{num}</b>"
        if show_unit:
            main += f"<span style='font-size:0.78em'> {unit}</span>"
        # Optional per-bar secondary figure beneath the headline value (a16z
        # "Spirited Away" dual label, e.g. a contribution "+6.63 pp").
        if b.get("sub") is not None:
            main += (f"<br><span style='font-size:0.72em;color:"
                     f"{hex_to_rgba(theme['font_color'], 0.6)}'>{b['sub']}</span>")
        value_texts.append(main)
        label_colors.append(title_c if on else hex_to_rgba(theme["font_color"], 0.55))

        lab = labels[i]
        if highlight is not None and on:
            cat_texts.append(f"<span style='color:{title_c}'><b>{lab}</b></span>")
        elif highlight is not None:
            cat_texts.append(f"<span style='color:{sub_c}'>{lab}</span>")
        else:
            cat_texts.append(f"<span style='color:{title_c}'>{lab}</span>")

    # Numeric y positions (top bar highest) — robust to duplicate labels and gives
    # exact control over spacing/order without categorical-axis surprises.
    ypos = [n - 1 - i for i in range(n)]
    if diverging:
        lo, hi = min(values + [0]), max(values + [0])
        span = (hi - lo) or 1
        axis_range = [lo - span * 0.16, hi + span * 0.16]
    else:
        hi = max(values + [0])
        axis_range = [0, hi * 1.16]  # headroom for outside value labels

    # Hover text: a per-bar `hover` string wins (e.g. show an exact, unrounded
    # figure on hover while the bar label stays clean); else the formatted value.
    def _hover(b, l, v):
        num, unit = _split_value(v, spec)
        return b.get("hover") or f"{l}: {num}{(' ' + unit) if unit else ''}"

    fig = go.Figure(go.Bar(
        y=ypos, x=values, orientation="h",
        marker=dict(color=bar_colors, cornerradius=5, line=dict(width=0)),
        text=value_texts, textposition="outside", cliponaxis=False,
        textfont=dict(family=theme["font_family"],
                      size=theme["label_size"] + 2, color=label_colors),
        customdata=[_hover(b, l, v) for b, l, v in zip(bars, labels, values)],
        hovertemplate="%{customdata}<extra></extra>",
        width=0.64,
    ))

    fig.update_yaxes(
        tickmode="array", tickvals=ypos, ticktext=cat_texts,
        showgrid=False, zeroline=False, showline=False, ticks="",
        range=[-0.6, n - 0.4],
        tickfont=dict(family=theme["font_family"], size=theme["label_size"] + 1),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, showline=False, ticks="",
                     showticklabels=False, range=axis_range)

    # Hairline zero baseline — the bars' anchor (replaces the gridlines); a touch
    # stronger for diverging charts, where it's the central +/- divider.
    fig.add_shape(type="line", xref="x", yref="y",
                  x0=0, x1=0, y0=-0.6, y1=n - 0.4,
                  line=dict(color=hex_to_rgba(title_c, 0.5 if diverging else 0.32),
                            width=1.6 if diverging else 1.4),
                  layer="below")

    maxlen = max((len(l) for l in labels), default=0)
    left = min(340, max(110, maxlen * 9 + 34))
    width = spec.get("width", 1040)
    right = 58
    fig.update_layout(
        height=spec.get("height", 600), width=width,
        bargap=0.42, showlegend=False,
        margin=dict(t=138, l=left, r=right, b=72),
    )

    # Full-bleed header rule under the title block — spans the entire graphic
    # width (label column + plot), aligned to the title's left edge. This is the
    # editorial "laid out on a page" cue that a plot-area-only rule misses.
    plot_w = max(width - left - right, 1)
    pad = 28  # canvas inset matching the title block
    fig.add_shape(type="line", xref="paper", yref="paper",
                  x0=(pad - left) / plot_w, x1=1 + (right - pad) / plot_w,
                  y0=1.0, y1=1.0,
                  line=dict(color=hex_to_rgba(title_c, 0.28), width=1))

    # Auto-place in the emptiest corner: descending ranking → space at the
    # bottom; ascending → at the top.
    descending = values[0] >= values[-1]
    note_default = dict(
        x=0.995, xanchor="right", align="right",
        y=0.12 if descending else 0.96,
        yanchor="bottom" if descending else "top",
    )
    _editorial_note(fig, spec, theme, note_default)
    apply_titles(fig, spec, theme, x_shift=-(left - 28))
    return fig


def _editorial_note(fig, spec, theme, default):
    """String → auto-placed note; dict → control {text,x,y,xanchor,yanchor,
    align,width,arrow}. `"note": false` or omit → suppressed."""
    note = spec.get("note")
    if not note:                       # missing, "", or explicit false
        return
    if isinstance(note, str):
        note = {"text": note}
    fig.add_annotation(
        text=f"<i>{note['text']}</i>", xref="paper", yref="paper",
        x=note.get("x", default["x"]), xanchor=note.get("xanchor", default["xanchor"]),
        y=note.get("y", default["y"]), yanchor=note.get("yanchor", default["yanchor"]),
        showarrow=bool(note.get("arrow", False)),
        align=note.get("align", default["align"]), width=note.get("width", 300),
        font=dict(family=theme["font_family"], size=13.5,
                  color=theme.get("subtitle_color", theme["font_color"])),
    )


@register("bar")
def render(spec: dict, theme: dict) -> go.Figure:
    # Multi-series data → grouped/stacked path; otherwise a single-series bar.
    if spec.get("series"):
        return _render_multi(spec, theme)

    bars = spec.get("bars") or []
    if not bars:
        raise ValueError("Bar spec needs a non-empty 'bars' list (or 'series')")
    for i, bar in enumerate(bars):
        if "value" not in bar:
            raise ValueError(f"Bar #{i} is missing required 'value': {bar!r}")

    labels = [b.get("label", f"#{i + 1}") for i, b in enumerate(bars)]
    values = [float(b["value"]) for b in bars]
    horizontal = spec.get("orientation", "v").lower().startswith("h")

    if horizontal:
        return _render_horizontal(spec, theme, bars, labels, values)

    # Color logic: explicit per-bar color wins; otherwise one accent color for
    # all bars, unless `highlight` is set — then chosen bars keep the accent and
    # the rest go solid-muted (warm neutral), matching the horizontal path so the
    # two orientations read as one family.
    accent = theme["palette"][0]
    neg_c = theme["palette"][4 % len(theme["palette"])]  # rust, for negatives
    muted = theme.get("bar_muted") or hex_to_rgba(theme["font_color"], 0.30)
    title_c = theme["title_color"]
    highlight = _resolve_highlight(spec, labels)
    # Diverging columns (some negative values): positive=accent, negative=rust,
    # with a zero baseline — matches the horizontal path.
    diverging = bool(spec.get("diverging")) or any(v < 0 for v in values)
    colors = []
    for i, bar in enumerate(bars):
        if bar.get("color"):
            colors.append(bar["color"])
        elif diverging and highlight is None:
            colors.append(accent if values[i] >= 0 else neg_c)
        elif highlight is None:
            colors.append(accent)
        else:
            colors.append(accent if i in highlight else muted)

    text = [format_value(v, spec) for v in values]
    grid = theme.get("grid_color", "rgba(0,0,0,0.08)")

    # Value axis range with headroom so outside labels never clip. Diverging
    # charts get extra room BELOW so negative labels clear the x-axis labels.
    lo, hi = min(values + [0]), max(values + [0])
    span = (hi - lo) or 1.0
    axis_range = ([lo - span * 0.16, hi + span * 0.16] if diverging
                  else [0, hi + span * 0.16])

    fig = go.Figure(go.Bar(
        x=labels, y=values, textposition="outside",
        marker=dict(color=colors, cornerradius=5, line=dict(width=0)),
        text=[f"<b>{t}</b>" for t in text],
        cliponaxis=False,
        hovertemplate="%{customdata}<extra></extra>",
        customdata=[f"{l}: {t}" for l, t in zip(labels, text)],
        width=0.7,
    ))
    fig.update_xaxes(showgrid=False, zeroline=False, showline=False,
                     ticks="", tickfont=dict(size=theme["label_size"]))
    fig.update_yaxes(showgrid=True, gridcolor=grid, zeroline=False,
                     showline=False, ticks="", showticklabels=False,
                     range=axis_range)
    if diverging:
        # Visible zero divider between positive and negative columns.
        fig.add_hline(y=0, line=dict(color=hex_to_rgba(title_c, 0.5), width=1.6),
                      layer="below")
    fig.update_layout(margin=dict(t=120, l=24, r=24, b=70))

    fig.update_traces(textfont=dict(family=theme["font_family"],
                                    size=theme["label_size"] + 1,
                                    color=theme["font_color"]))
    fig.update_layout(
        height=spec.get("height", 640),
        width=spec.get("width", 1000),
        bargap=0.35,
        showlegend=False,
    )
    descending = values[0] >= values[-1]
    _editorial_note(fig, spec, theme, dict(
        y=0.96, yanchor="top",
        x=0.995 if descending else 0.01,
        xanchor="right" if descending else "left",
        align="right" if descending else "left"))
    apply_titles(fig, spec, theme, x_shift=0)
    return fig
