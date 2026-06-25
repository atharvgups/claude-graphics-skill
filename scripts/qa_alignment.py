#!/usr/bin/env python3
"""
QA gate: every chart's headline must sit at the canvas edge, not indented to the
plot area. Renders each example to PNG, measures the leftmost ink of the title
row, and flags any chart whose title is indented (or missing).

This guards the exact regression Isaac caught — a renderer change that anchors the
title/legend/footer to the plot edge (past the y-axis labels) instead of the
canvas edge. Run it after touching apply_titles / edge_align / any renderer.

Usage:
    python scripts/qa_alignment.py            # render + measure all examples
    python scripts/qa_alignment.py --max 42   # custom indent threshold (px)

Exit code 1 if any chart's title_x exceeds the threshold (so it can gate CI).
Needs Pillow (in requirements.txt) and kaleido+Chrome for the PNG export.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import charts  # noqa: F401,E402  -> registers all chart types
from charts.base import get_renderer  # noqa: E402
from theme import get_theme  # noqa: E402

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print("QA needs Pillow: ./.venv/bin/pip install Pillow")
    raise SystemExit(2)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX_DIR = os.path.join(ROOT, "examples")
OUT_DIR = os.path.join(ROOT, "output", "_qa")


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _title_x(png, y0=18, y1=80, x_scan=560, dark=150):
    """Leftmost dark (text) pixel in the title row band, or None if blank."""
    im = Image.open(png).convert("RGB")
    px = im.load()
    w = im.size[0]
    best = None
    for y in range(y0, y1):
        for x in range(0, min(x_scan, w)):
            if _lum(px[x, y]) < dark:
                best = x if best is None else min(best, x)
                break
    return best


def main(argv) -> int:
    max_x = 42
    if "--max" in argv:
        max_x = int(argv[argv.index("--max") + 1])
    os.makedirs(OUT_DIR, exist_ok=True)

    rows, flagged = [], []
    for fn in sorted(os.listdir(EX_DIR)):
        if not fn.endswith(".json"):
            continue
        name = fn[:-5]
        with open(os.path.join(EX_DIR, fn), encoding="utf-8") as fh:
            spec = json.load(fh)
        fig = get_renderer(spec.get("chart_type"))(spec, get_theme(spec.get("theme")))
        png = os.path.join(OUT_DIR, f"{name}.png")
        try:
            fig.write_image(png, format="png", scale=1)
        except Exception as exc:  # pragma: no cover (needs kaleido+chrome)
            print(f"! {name}: render failed ({exc})")
            flagged.append((name, "render-failed"))
            continue
        tx = _title_x(png)
        rows.append((name, tx))
        if tx is None or tx > max_x:
            flagged.append((name, tx))

    aligned = sum(1 for _, t in rows if t is not None and t <= max_x)
    print(f"alignment QA: {aligned}/{len(rows)} titles at the canvas edge "
          f"(<= {max_x}px)")
    if flagged:
        print("FAIL — indented or missing titles:")
        for name, tx in flagged:
            print(f"  {name}: title_x={tx}")
        return 1
    print("PASS — every chart's headline is at the canvas edge.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
