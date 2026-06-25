"""
Theme + palette definitions for the graphics skill.

The whole point of this skill is that raw Plotly/Matplotlib output looks generic.
A theme bundles the handful of choices that actually make a chart read as
"designed" rather than "exported": background, typography, a curated and
*distinct* color palette, flow opacity, and spacing. Chart renderers pull these
values instead of hard-coding them, so a single `--theme` flag restyles every
chart type the same way.

Add a new look by adding one entry to THEMES. Keep palettes curated and high
contrast against the background — auto-generated rainbows are the #1 reason
data graphics look amateurish.
"""

from __future__ import annotations

# --- Curated, deliberately-distinct palettes -------------------------------
# Each color is chosen to be separable from its neighbors even for viewers with
# common color-vision deficiencies, and to stay legible against the theme bg.

PALETTES = {
    # Bright, saturated accents that pop on a dark canvas.
    "neon": [
        "#5B8FF9", "#61DDAA", "#F6BD16", "#F08BB4",
        "#7262FD", "#78D3F8", "#FF9D4D", "#9661BC",
        "#52C41A", "#FF6B6B",
    ],
    # Muted, earthy "press" tones tuned to the a16z / Jason Saltzman house
    # style: desaturated teal, slate, sage, ochre, rust. Deliberately TIGHT and
    # harmonious (analogous earth tones, one teal lead) rather than a wide
    # rainbow — restraint is what makes an editorial chart read as "designed by
    # a studio". The teal leads because it's the natural accent/highlight color.
    "editorial": [
        "#3E7C73", "#466089", "#7C9A6B", "#C98A3C",
        "#A8553A", "#5E8F86", "#8A7B57", "#6E6A8C",
    ],
    # Confident tech-brand palette: indigo-led, clean, modern.
    "brand": [
        "#4338CA", "#0EA5E9", "#10B981", "#F59E0B",
        "#EC4899", "#8B5CF6", "#14B8A6", "#EF4444",
        "#6366F1", "#84CC16",
    ],
    # Simula brand palette, derived from the logo's cyan→blue→indigo gradient
    # plus the accent colors used across simula.ad. Indigo leads (the primary
    # brand color), followed by the bright logo cyan and violet, then a spread
    # of distinct supporting hues that stay vivid on a dark canvas.
    "simula": [
        "#4F46E5", "#22D3EE", "#7C3AED", "#3B82F6",
        "#14B8A6", "#EC4899", "#F97316", "#22C55E",
        "#A5B4FC", "#FBBF24",
    ],
}

# --- Themes ----------------------------------------------------------------
# A theme = one palette + the canvas/type/spacing decisions that surround it.

THEMES = {
    # Dark, high-impact. This is the "viral LinkedIn graphic" default — bold
    # flows on near-black read well in a feed and screenshot cleanly.
    "midnight": {
        "paper_bg": "#0B1020",
        "plot_bg": "#0B1020",
        "font_family": "Inter, 'Helvetica Neue', Arial, sans-serif",
        "font_color": "#E6EAF2",
        "title_color": "#FFFFFF",
        "subtitle_color": "#9BA8C2",
        "source_color": "#5C6784",
        "palette": PALETTES["neon"],
        "link_opacity": 0.55,
        "node_pad": 30,
        "node_thickness": 26,
        "node_line_color": "#0B1020",
        "node_line_width": 0.5,
        "title_size": 30,
        "subtitle_size": 16,
        "label_size": 14,
        "grid_color": "rgba(255,255,255,0.07)",
        "muted_color": "#39435A",
        "bar_muted": "#2C3650",
        "bar_track": "rgba(255,255,255,0.04)",
    },
    # Editorial "press" theme modeled on the a16z / Jason Saltzman chart style:
    # warm paper canvas, deep-navy serif headline, earthy muted palette, the
    # faintest horizontal gridlines. Reach for this for newsletter/blog/print
    # graphics and anything that should read as a polished publication chart.
    "editorial": {
        "paper_bg": "#ECE8DD",
        "plot_bg": "#ECE8DD",
        "font_family": "Georgia, 'Times New Roman', serif",
        "font_color": "#3A3A36",
        "title_color": "#1E2A44",
        "subtitle_color": "#6E6A5F",
        "source_color": "#A29D8E",
        "palette": PALETTES["editorial"],
        # Broader 9-tone palette for multi-category stacks (the tight 8-tone
        # `palette` is analogous-by-design and muddies when 6+ segments stack).
        # Sampled directly from the a16z / Jason Saltzman stacked-bar house style:
        # teal, forest, slate-periwinkle, steel-blue, navy, moss, dusty-rose,
        # sage, warm-gray — distinct but all desaturated so the stack stays calm.
        "stack_palette": [
            "#3B7A86", "#2E3826", "#7C89A6", "#A7C0D0", "#1F2A48",
            "#7D9A50", "#C77E92", "#AEC994", "#6F6E64",
        ],
        "link_opacity": 0.42,
        "node_pad": 30,
        "node_thickness": 24,
        "node_line_color": "#ECE8DD",
        "node_line_width": 0.5,
        "title_size": 31,
        "subtitle_size": 16,
        "label_size": 14,
        "grid_color": "rgba(30,42,68,0.10)",
        "muted_color": "#C4BEAE",
        # Solid warm-taupe fill for de-emphasized bars. A real editorial chart
        # keeps the "other" bars as confident, readable data in a quiet neutral
        # — the warm/cool contrast against the teal highlight is the whole move.
        # (The old ghost-gray rgba tint read as "unfilled placeholder".)
        "bar_muted": "#CBC2AD",
        "bar_track": "rgba(30,42,68,0.05)",
    },
    # Simula's on-brand theme. Dark slate canvas (matching the dark sections of
    # simula.ad: slate-900 #0F172A) so graphics stop the scroll in a LinkedIn
    # feed, with the brand's cyan→indigo→violet palette as accents. This is the
    # theme to reach for when making content *for Simula*. (For a light on-brand
    # variant, copy this entry, swap the bg to #FFFFFF and the text colors dark.)
    "simula": {
        "paper_bg": "#0F172A",
        "plot_bg": "#0F172A",
        "font_family": "'Plus Jakarta Sans', 'Inter', 'Helvetica Neue', Arial, sans-serif",
        "font_color": "#E2E8F0",
        "title_color": "#FFFFFF",
        "subtitle_color": "#94A3B8",
        "source_color": "#64748B",
        "palette": PALETTES["simula"],
        "link_opacity": 0.58,
        "node_pad": 32,
        "node_thickness": 26,
        "node_line_color": "#0F172A",
        "node_line_width": 0.5,
        "title_size": 30,
        "subtitle_size": 16,
        "label_size": 15,
        "grid_color": "rgba(148,163,184,0.13)",
        "muted_color": "#334155",
        "bar_muted": "#2A3750",
        "bar_track": "rgba(148,163,184,0.06)",
    },
    # Light, crisp, indigo-led. A safe modern default for product/brand work.
    "brand": {
        "paper_bg": "#FFFFFF",
        "plot_bg": "#FFFFFF",
        "font_family": "Inter, 'Helvetica Neue', Arial, sans-serif",
        "font_color": "#1F2937",
        "title_color": "#111827",
        "subtitle_color": "#6B7280",
        "source_color": "#9CA3AF",
        "palette": PALETTES["brand"],
        "link_opacity": 0.46,
        "node_pad": 30,
        "node_thickness": 24,
        "node_line_color": "#FFFFFF",
        "node_line_width": 0.5,
        "title_size": 30,
        "subtitle_size": 16,
        "label_size": 14,
        "grid_color": "rgba(17,24,39,0.08)",
        "muted_color": "#CBD0D8",
        "bar_muted": "#D8DCE3",
        "bar_track": "rgba(17,24,39,0.04)",
    },
}

# Editorial is the house default: the a16z-style cream/navy/earthy look is the
# consistent aesthetic across every chart type. Dark themes (simula, midnight)
# are opt-in for LinkedIn/brand contexts.
DEFAULT_THEME = "editorial"


def get_theme(name: str | None) -> dict:
    """Return a theme dict, falling back to the default with a clear error."""
    if not name:
        return THEMES[DEFAULT_THEME]
    if name not in THEMES:
        raise ValueError(
            f"Unknown theme '{name}'. Available: {', '.join(sorted(THEMES))}"
        )
    return THEMES[name]


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert '#rrggbb' to an 'rgba(r,g,b,a)' string for translucent flows."""
    h = hex_color.lstrip("#")
    if len(h) == 3:  # support shorthand like #abc
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def color_for_index(theme: dict, index: int) -> str:
    """Pick a palette color, cycling if there are more nodes than colors."""
    palette = theme["palette"]
    return palette[index % len(palette)]
