#!/usr/bin/env python3
"""
Colorblind-safety QA for the theme palettes.

Stacked bars, areas, and multi-line charts lean on color to separate series, so
the palettes have to survive the common color-vision deficiencies — not just look
good to trichromats. This script simulates protanopia, deuteranopia, and
tritanopia (Machado et al. 2009, severity 1.0) on each theme's `palette`,
`stack_palette`, and `line_palette`, then measures distinguishability in CIE Lab.

Two questions, two thresholds:

  * ADJACENT pairs (segments that physically touch in a stack / lines drawn in
    order) must stay clearly distinct — this is the real failure mode, gated at
    ΔE >= ADJ_MIN. A failure here exits non-zero.
  * ANY pair (legend-matching across non-touching segments) is reported when it
    dips below PAIR_WARN, but only warned — spatial separation + the house
    direct-labeling style disambiguate these.

Usage:
    python qa_colorblind.py            # check all theme palettes, exit 1 on fail
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from theme import THEMES  # noqa: E402

# CIE76 ΔE bands (rough): <8 risky, 8-15 subtle, >15 clearly distinct.
ADJ_MIN = 12.0   # adjacent segments must clear this under every vision type
PAIR_WARN = 11.0  # report any non-adjacent pair below this (informational)

# Machado et al. 2009 severity-1.0 matrices — operate on LINEAR RGB.
CVD = {
    "normal": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    "protanopia": [[0.152286, 1.052583, -0.204868],
                   [0.114503, 0.786281, 0.099216],
                   [-0.003882, -0.048116, 1.051998]],
    "deuteranopia": [[0.367322, 0.860646, -0.227968],
                     [0.280085, 0.672501, 0.047413],
                     [-0.011820, 0.042940, 0.968881]],
    "tritanopia": [[1.255528, -0.076749, -0.178779],
                   [-0.078411, 0.930809, 0.147602],
                   [0.004733, 0.691367, 0.303900]],
}


def _hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _srgb2lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _rgb2xyz(r, g, b):
    return (0.4124 * r + 0.3576 * g + 0.1805 * b,
            0.2126 * r + 0.7152 * g + 0.0722 * b,
            0.0193 * r + 0.1192 * g + 0.9505 * b)


def _f(t):
    d = 6 / 29
    return t ** (1 / 3) if t > d ** 3 else t / (3 * d * d) + 4 / 29


def _xyz2lab(x, y, z):
    xn, yn, zn = 0.95047, 1.0, 1.08883
    fx, fy, fz = _f(x / xn), _f(y / yn), _f(z / zn)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def _simulate(hex_color, mat):
    """Hex color seen under a CVD matrix, returned as CIE Lab."""
    r, g, b = (_srgb2lin(c) for c in _hex2rgb(hex_color))
    o = [sum(mat[i][j] * v for j, v in enumerate((r, g, b))) for i in range(3)]
    return _xyz2lab(*_rgb2xyz(*o))


def _de76(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def check_palette(label, colors):
    """Return True if adjacent distinguishability holds under every vision type."""
    print(f"\n# {label}  ({len(colors)} tones)")
    ok = True
    for vision, mat in CVD.items():
        labs = [_simulate(c, mat) for c in colors]
        adj = [(i, i + 1, _de76(labs[i], labs[i + 1]))
               for i in range(len(labs) - 1)]
        worst_adj = min(adj, key=lambda t: t[2]) if adj else (0, 0, 999)
        flag = "" if worst_adj[2] >= ADJ_MIN else "  ** ADJACENT FAIL **"
        if worst_adj[2] < ADJ_MIN:
            ok = False
        print(f"  {vision:13s} adjacent min ΔE = {worst_adj[2]:5.1f}"
              f"  (#{worst_adj[0]}|#{worst_adj[1]}){flag}")
        if vision != "normal":
            low = sorted(((i, j, _de76(labs[i], labs[j]))
                          for i in range(len(labs))
                          for j in range(i + 1, len(labs))
                          if _de76(labs[i], labs[j]) < PAIR_WARN),
                         key=lambda t: t[2])
            for i, j, d in low:
                print(f"                  · any-pair #{i}|#{j} ΔE={d:.1f}"
                      " (non-adjacent — warn only)")
    return ok


def main() -> int:
    all_ok = True
    for tname, theme in THEMES.items():
        for key in ("palette", "stack_palette", "line_palette"):
            colors = theme.get(key)
            if colors:
                all_ok &= check_palette(f"{tname}.{key}", colors)
    print("\n" + ("PASS — all adjacent pairs clear ΔE %.0f under every vision type"
                  % ADJ_MIN if all_ok
                  else "FAIL — an adjacent pair is too close under a CVD type"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
