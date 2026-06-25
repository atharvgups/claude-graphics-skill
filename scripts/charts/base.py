"""
Chart registry + shared helpers.

Every chart type registers itself here with `@register("name")`. The CLI looks
up the renderer by `chart_type` and calls it with (spec, theme), getting back a
Plotly Figure. Adding a new graphic — funnel, network, treemap — means writing
one module that defines a renderer and decorates it. Nothing else in the
pipeline needs to change; that's what keeps the skill extensible.
"""

from __future__ import annotations

from typing import Callable, Dict

import plotly.graph_objects as go

from theme import hex_to_rgba

# chart_type -> renderer(spec: dict, theme: dict) -> plotly.graph_objects.Figure
_REGISTRY: Dict[str, Callable] = {}


def register(chart_type: str):
    """Decorator: register a renderer under a chart_type name."""

    def decorator(fn: Callable) -> Callable:
        _REGISTRY[chart_type] = fn
        return fn

    return decorator


def get_renderer(chart_type: str) -> Callable:
    if chart_type not in _REGISTRY:
        raise ValueError(
            f"No renderer for chart_type '{chart_type}'. "
            f"Available: {', '.join(available_charts()) or '(none loaded)'}"
        )
    return _REGISTRY[chart_type]


def available_charts() -> list[str]:
    return sorted(_REGISTRY)


def format_value(value: float, spec: dict) -> str:
    """
    Format a number for labels using the spec's display preferences.

    `value_format` is a standard Python format spec (e.g. ',.0f' for
    thousands-separated integers, ',.1f' for one decimal). `value_prefix` /
    `value_suffix` wrap it ('$' / '%' / ' GWh'). Sensible defaults mean the
    caller usually supplies nothing and still gets clean output.
    """
    fmt = spec.get("value_format", ",.0f")
    prefix = spec.get("value_prefix", "")
    suffix = spec.get("value_suffix", "")
    # Negative values with a prefix read correctly as "-$9M", not "$-9M": pull the
    # sign out in front of the prefix (no-op when there's no prefix).
    neg = isinstance(value, (int, float)) and value < 0 and prefix
    try:
        body = format(abs(value) if neg else value, fmt)
    except (ValueError, TypeError):
        body = str(value)
    return f"{'-' if neg else ''}{prefix}{body}{suffix}"


def apply_titles(fig, spec: dict, theme: dict, x_shift: float = 0) -> None:
    """
    Add the title / subtitle / source furniture that turns a bare chart into a
    finished graphic. These three lines do most of the "editorial" lift: a bold
    headline, a one-line takeaway, and an attribution that signals credibility.

    Layout reserves headroom at the top (title + subtitle) and a thin footer
    (source) so they never collide with the plot. Renderers should set their
    own top/bottom margins to match; see the SANKEY layout for the reference.

    `x_shift` nudges the whole text block horizontally in pixels. Annotations
    are anchored to the *plot* area (xref="paper"), so charts with a wide left
    margin (e.g. a funnel's stage labels) would otherwise indent the title.
    Such charts use a fixed left margin and pass a negative x_shift to pull the
    title block back to the canvas edge, keeping alignment consistent with
    charts that have no left axis (like the Sankey).
    """
    title = spec.get("title", "")
    subtitle = spec.get("subtitle", "")
    source = spec.get("source", "")

    # Position everything as paper-referenced annotations with pixel offsets.
    # Plotly's layout.title doesn't support pixel nudging (yshift), and we want
    # all three text elements left-aligned to the same edge with predictable
    # spacing regardless of chart type — annotations give us that control.
    annotations = list(fig.layout.annotations or [])

    if title:
        annotations.append(
            dict(
                text=f"<b>{title}</b>",
                x=0, xref="paper", xanchor="left",
                y=1.0, yref="paper", yanchor="bottom",
                xshift=x_shift,
                yshift=64 if subtitle else 40,
                showarrow=False,
                font=dict(
                    family=theme["font_family"],
                    size=theme["title_size"],
                    color=theme["title_color"],
                ),
            )
        )

    if subtitle:
        annotations.append(
            dict(
                text=subtitle,
                x=0, xref="paper", xanchor="left",
                y=1.0, yref="paper", yanchor="bottom",
                xshift=x_shift,
                yshift=36,
                showarrow=False,
                font=dict(
                    family=theme["font_family"],
                    size=theme["subtitle_size"],
                    color=theme["subtitle_color"],
                ),
            )
        )

    if source:
        annotations.append(
            dict(
                text=source,
                x=0, xref="paper", xanchor="left",
                y=0, yref="paper", yanchor="top",
                xshift=x_shift,
                yshift=-34,
                showarrow=False,
                font=dict(
                    family=theme["font_family"],
                    size=12,
                    color=theme["source_color"],
                ),
            )
        )

    fig.update_layout(
        annotations=annotations,
        paper_bgcolor=theme["paper_bg"],
        plot_bgcolor=theme["plot_bg"],
        font=dict(family=theme["font_family"], color=theme["font_color"]),
    )


def cartesian_axes(fig, theme, spec=None, *, x_grid=False, y_grid=True,
                   x_labels=True, y_labels=True, value_axis="y"):
    """
    Apply the shared minimal-chrome cartesian styling: faint gridlines on one
    axis only, no spines, no tick marks, themed tick fonts. This is the editorial
    restraint that every line/scatter/combo/bar chart shares so they read as one
    family. `value_axis` (x or y) gets the spec's value prefix/suffix on its
    ticks (e.g. "$", "%").
    """
    grid = theme.get("grid_color", "rgba(0,0,0,0.08)")
    tick = dict(family=theme["font_family"], size=theme["label_size"],
                color=theme.get("subtitle_color", theme["font_color"]))
    fig.update_xaxes(showgrid=x_grid, gridcolor=grid, zeroline=False,
                     showline=False, ticks="", tickfont=tick,
                     showticklabels=x_labels)
    fig.update_yaxes(showgrid=y_grid, gridcolor=grid, zeroline=False,
                     showline=False, ticks="", tickfont=tick,
                     showticklabels=y_labels)
    if spec:
        pref, suf = spec.get("value_prefix", ""), spec.get("value_suffix", "")
        if value_axis == "y":
            fig.update_yaxes(tickprefix=pref, ticksuffix=suf)
        else:
            fig.update_xaxes(tickprefix=pref, ticksuffix=suf)


def style_legend(fig, theme):
    """
    Bottom-left horizontal legend, themed and chrome-free — a16z-style. Sits low
    in the bottom margin (below the source line, which apply_titles places just
    under the plot). Charts that call this should use a ~118px bottom margin so
    the legend has room.
    """
    fig.update_layout(legend=dict(
        orientation="h", yanchor="top", y=-0.16, x=0, xanchor="left",
        font=dict(family=theme["font_family"], size=theme["label_size"],
                  color=theme["font_color"]),
        bgcolor="rgba(0,0,0,0)", title_text="",
    ))


def add_circle_legend(fig, names, colors, theme, *, traceorder="normal"):
    """
    Swap the default legend swatch (a square for bars, a line for lines) for the
    editorial **round dot** — the a16z legend style. Adds one data-less scatter
    per entry purely for the swatch; the caller must set `showlegend=False` on
    the real traces so only these dots appear. Then styles the legend (low,
    left, chrome-free) the same way for every chart type that uses it.
    """
    for name, c in zip(names, colors):
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(symbol="circle", size=11, color=c),
            name=name, showlegend=True, hoverinfo="skip",
        ))
    style_legend(fig, theme)
    fig.update_layout(legend=dict(
        y=-0.11, traceorder=traceorder, itemsizing="constant", tracegroupgap=8,
        font=dict(family=theme["font_family"], size=15,
                  color=theme["font_color"])))


def _footer_texture(fig, theme, rule_y, x0=0.0, x1=1.0, *, run=0.045,
                    spacing=0.013, band=0.13):
    """
    Faint diagonal **crosshatch** behind the footer band — the subtle paper-weave
    on a16z charts. Drawn as ONE multi-segment `path` shape (cheap: a single
    object regardless of line count) in paper coordinates, clipped to the content
    width [0, 1], sitting just below the footer rule.
    """
    top = rule_y - 0.004          # just under the rule
    bot = rule_y - band           # down toward the canvas edge

    def _clip(xb, y_a, y_b):
        # Segment (xb, y_a) -> (xb+run, y_b); keep only the part with x in [x0,x1].
        lo = max(0.0, (x0 - xb) / run)
        hi = min(1.0, (x1 - xb) / run)
        if lo >= hi:
            return None
        return (xb + run * lo, y_a + (y_b - y_a) * lo,
                xb + run * hi, y_a + (y_b - y_a) * hi)

    segs = []
    xb = x0 - run
    while xb <= x1:
        for s in (_clip(xb, bot, top), _clip(xb, top, bot)):  # "/" and "\"
            if s:
                segs.append("M {:.4f} {:.4f} L {:.4f} {:.4f}".format(*s))
        xb += spacing
    if segs:
        fig.add_shape(
            type="path", xref="paper", yref="paper", path=" ".join(segs),
            line=dict(color=hex_to_rgba(theme["title_color"], 0.10), width=0.6),
            layer="below",
        )


def apply_footer(fig, spec, theme, source_y=-0.30, rule_y=-0.38, x_shift=0,
                 rule_x=(0.0, 1.0), wordmark_xshift=0):
    """
    The editorial footer strip — the bottom band on a16z / Jason Saltzman charts:
    a small source line, a full-width hairline rule, a brand/CTA line bottom-left,
    and a wordmark bottom-right. All opt-in:

      * `source`  — attribution (drawn here, lower than the default, so it clears
                    a multi-row legend).
      * `footer`  — a brand/CTA line, e.g. "More charts: simula.ad" (bottom-left).
      * `wordmark`— a small brand mark, e.g. "SIMULA" (bottom-right).

    `x_shift` nudges the left-aligned text to the canvas edge (charts with a wide
    left margin pass a negative shift, like apply_titles); `rule_x` is the paper
    x-range of the full-bleed rule + texture; `wordmark_xshift` right-aligns the
    wordmark to the canvas edge. Positions are paper-referenced with negative y;
    the caller must reserve enough bottom margin.
    """
    title_c = theme["title_color"]
    fam = theme["font_family"]
    src = spec.get("source")
    footer = spec.get("footer")
    wordmark = spec.get("wordmark")

    if src:
        fig.add_annotation(
            text=src, xref="paper", yref="paper", xshift=x_shift,
            x=0, xanchor="left", y=source_y, yanchor="top", showarrow=False,
            font=dict(family=fam, size=12.5, color=theme["source_color"]),
        )

    if not (footer or wordmark):
        return

    if spec.get("footer_texture", True):
        _footer_texture(fig, theme, rule_y, rule_x[0], rule_x[1])

    fig.add_shape(
        type="line", xref="paper", yref="paper",
        x0=rule_x[0], x1=rule_x[1], y0=rule_y, y1=rule_y,
        line=dict(color=hex_to_rgba(title_c, 0.22), width=1),
    )
    if footer:
        fig.add_annotation(
            text=f"<b><i>{footer}</i></b>", xref="paper", yref="paper",
            x=0, xanchor="left", xshift=x_shift, y=rule_y - 0.025,
            yanchor="top", showarrow=False,
            font=dict(family=fam, size=15.5, color=theme["subtitle_color"]),
        )
    if wordmark:
        fig.add_annotation(
            text=f"<b>{wordmark}</b>", xref="paper", yref="paper",
            x=1, xanchor="right", xshift=wordmark_xshift, y=rule_y - 0.02,
            yanchor="top", showarrow=False,
            font=dict(family=fam, size=19, color=hex_to_rgba(title_c, 0.85)),
        )
