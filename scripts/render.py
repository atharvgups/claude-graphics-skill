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

# Heavy imports (plotly, etc.) are wrapped so `--selfcheck` can report a missing
# dependency with a friendly fix instead of crashing on an import traceback —
# that absent-deps case is exactly when a caller most needs the diagnosis.
try:
    import charts  # noqa: F401  -> registers all chart types on import
    from charts.base import get_renderer
    from theme import get_theme
    _IMPORT_ERROR = None
except Exception as _exc:  # pragma: no cover - depends on env
    _IMPORT_ERROR = _exc


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


def selfcheck() -> int:
    """Prove the engine is live before relying on it: registry populated, theme
    loads, and a real chart renders to HTML in-memory. Exits 0 only if rendering
    actually works — so a caller can gate on it instead of hand-rolling a chart.
    """
    if _IMPORT_ERROR is not None:
        print(f"✗ graphics engine NOT live: {_IMPORT_ERROR}")
        print("  Fix: from the skill dir run "
              "`python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt`,"
              " then call render.py with ./.venv/bin/python.")
        return 1

    from charts.base import _REGISTRY  # noqa: PLC0415

    try:
        n = len(_REGISTRY)
        if n == 0:
            raise RuntimeError("no chart types registered")
        theme = get_theme("editorial")
        spec = {"chart_type": "bar", "orientation": "h", "title": "selfcheck",
                "bars": [{"label": "A", "value": 3}, {"label": "B", "value": 7}]}
        fig = get_renderer("bar")(spec, theme)
        html = fig.to_html(include_plotlyjs=False, full_html=False)
        if "<div" not in html:
            raise RuntimeError("renderer produced no HTML")
    except Exception as exc:  # surface the real failure, don't mask it
        print(f"✗ graphics engine NOT live: {exc}")
        print("  Fix: from the skill dir run "
              "`python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt`,"
              " then call render.py with ./.venv/bin/python.")
        return 1

    try:
        import kaleido  # noqa: F401,PLC0415
        png = "available"
    except Exception:
        png = "MISSING (HTML still works; `pip install kaleido` for PNG/SVG)"

    print("✓ graphics engine is LIVE — render via scripts/render.py, do NOT "
          "hand-write chart code.")
    print(f"  chart types registered: {n}")
    print(f"  HTML export: working   ·   PNG/SVG (kaleido): {png}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a data-graphic spec.")
    parser.add_argument(
        "--selfcheck",
        action="store_true",
        help="Verify the engine is live (registry + a real render) and exit. "
             "Run this FIRST if unsure the skill works; if it passes, always "
             "render through this script rather than writing chart code.",
    )
    parser.add_argument("spec", nargs="?", help="Path to the JSON spec file")
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

    if args.selfcheck:
        return selfcheck()
    if not args.spec:
        parser.error("the following arguments are required: spec "
                     "(or pass --selfcheck)")
    if _IMPORT_ERROR is not None:
        raise SystemExit(
            f"graphics engine can't load ({_IMPORT_ERROR}). Run "
            "`python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt`"
            " first, then render with ./.venv/bin/python. (Run --selfcheck to verify.)"
        )

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
