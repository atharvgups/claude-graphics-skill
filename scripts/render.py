#!/usr/bin/env python3
"""
CLI entry point for the graphics skill.

Reads a JSON spec, dispatches to the renderer for its `chart_type`, applies the
chosen theme, and writes an artifact-renderable file. HTML output is fully
interactive (hover, drag) and self-contained; SVG/PNG are static exports for
slides or LinkedIn (PNG/SVG need the optional `kaleido` package).

Usage:
    python render.py SPEC.json [-o OUT] [-f html|svg|png] [-t THEME] [--png-scale N]

Examples:
    python render.py examples/budget_flow.json
    python render.py examples/user_funnel.json -t editorial -f svg
    python render.py spec.json -o output/my_chart.html
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# Make sibling modules importable whether run as `python render.py` or `-m`.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import charts  # noqa: F401,E402  -> registers all chart types on import
from charts.base import get_renderer  # noqa: E402
from theme import get_theme  # noqa: E402


def load_spec(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def default_output(spec_path: str, fmt: str) -> str:
    base = os.path.splitext(os.path.basename(spec_path))[0]
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, f"{base}.{fmt}")


def write_output(fig, out_path: str, fmt: str, png_scale: int) -> None:
    if fmt == "html":
        # include_plotlyjs=True -> standalone file that renders offline as an
        # artifact, no network needed.
        fig.write_html(out_path, include_plotlyjs=True, full_html=True)
        return
    # SVG / PNG go through kaleido.
    try:
        fig.write_image(out_path, format=fmt, scale=png_scale)
    except Exception as exc:  # pragma: no cover - depends on optional dep
        raise SystemExit(
            f"Static export to .{fmt} failed: {exc}\n"
            "Static formats need the 'kaleido' package: pip install kaleido\n"
            "Or export HTML instead (-f html), which has no extra dependency."
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a data-graphic spec.")
    parser.add_argument("spec", help="Path to the JSON spec file")
    parser.add_argument("-o", "--out", help="Output path (extension sets format if -f omitted)")
    parser.add_argument(
        "-f",
        "--format",
        choices=["html", "svg", "png"],
        help="Output format (default: html, or inferred from --out extension)",
    )
    parser.add_argument("-t", "--theme", help="Override the spec's theme (midnight|editorial|brand)")
    parser.add_argument("--png-scale", type=int, default=2, help="Scale factor for PNG export (default 2 = retina)")
    args = parser.parse_args(argv)

    spec = load_spec(args.spec)

    # Format precedence: -f flag > --out extension > html default.
    fmt = args.format
    if not fmt and args.out:
        fmt = os.path.splitext(args.out)[1].lstrip(".").lower() or None
    fmt = fmt or "html"
    if fmt not in ("html", "svg", "png"):
        raise SystemExit(f"Unsupported format '{fmt}'. Use html, svg, or png.")

    theme = get_theme(args.theme or spec.get("theme"))
    renderer = get_renderer(spec.get("chart_type", "sankey"))
    fig = renderer(spec, theme)

    out_path = args.out or default_output(args.spec, fmt)
    write_output(fig, out_path, fmt, args.png_scale)
    print(f"✓ Wrote {fmt.upper()} -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
