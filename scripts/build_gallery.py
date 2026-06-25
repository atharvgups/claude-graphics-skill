#!/usr/bin/env python3
"""
Build a contact-sheet gallery of every example spec — renders each to PNG and
assembles one scrollable HTML page grouped by chart type. Handy for eyeballing
the whole library at once (and as a visual regression check).

Usage:
    python build_gallery.py            # renders examples/ -> output/gallery.html
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import charts  # noqa: F401,E402  -> registers all chart types
from charts.base import get_renderer  # noqa: E402
from theme import get_theme  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX_DIR = os.path.join(ROOT, "examples")
OUT_DIR = os.path.join(ROOT, "output")
IMG_DIR = os.path.join(OUT_DIR, "gallery")


def main() -> int:
    os.makedirs(IMG_DIR, exist_ok=True)
    cards = []
    for fn in sorted(os.listdir(EX_DIR)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(EX_DIR, fn), encoding="utf-8") as fh:
            spec = json.load(fh)
        name = os.path.splitext(fn)[0]
        ctype = spec.get("chart_type", "?")
        title = spec.get("title", name)
        theme = get_theme(spec.get("theme"))
        fig = get_renderer(ctype)(spec, theme)
        png = os.path.join(IMG_DIR, f"{name}.png")
        try:
            fig.write_image(png, format="png", scale=1)
        except Exception as exc:  # pragma: no cover (needs kaleido+chrome)
            print(f"! {name}: PNG export failed ({exc})")
            continue
        cards.append((ctype, title, f"gallery/{name}.png"))
        print(f"✓ {name} ({ctype})")

    cards.sort(key=lambda c: (c[0], c[1]))
    items = "\n".join(
        f'''  <figure class="card">
    <img src="{src}" loading="lazy" alt="{title}">
    <figcaption><span class="type">{ctype}</span> {title}</figcaption>
  </figure>''' for ctype, title, src in cards
    )
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Graphics skill — gallery</title>
<style>
  body {{ margin:0; background:#ECE8DD; color:#1E2A44;
         font-family: Georgia, 'Times New Roman', serif; }}
  header {{ padding:40px 48px 8px; }}
  h1 {{ margin:0; font-size:34px; }}
  p.sub {{ margin:6px 0 0; color:#6E6A5F; font-size:16px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(440px,1fr));
           gap:28px; padding:28px 48px 64px; }}
  .card {{ margin:0; background:#fff; border-radius:10px; overflow:hidden;
           box-shadow:0 1px 3px rgba(30,42,68,.12); }}
  .card img {{ width:100%; display:block; }}
  figcaption {{ padding:12px 16px; font-size:14px; color:#3A3A36; }}
  .type {{ display:inline-block; background:#1E2A44; color:#fff; font-size:11px;
           font-family: -apple-system, Arial, sans-serif; letter-spacing:.04em;
           text-transform:uppercase; padding:2px 8px; border-radius:5px;
           margin-right:8px; }}
</style></head><body>
<header>
  <h1>Graphics skill — full gallery</h1>
  <p class="sub">{len(cards)} examples · {len(set(c[0] for c in cards))} chart types · one consistent a16z-grade aesthetic</p>
</header>
<div class="grid">
{items}
</div>
</body></html>"""
    out = os.path.join(OUT_DIR, "gallery.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"\n→ {out}  ({len(cards)} charts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
