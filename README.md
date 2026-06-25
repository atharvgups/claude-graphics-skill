# claude-graphics-skill

A Claude Skill for generating **polished, presentation-ready data
visualizations** from structured data — **30 chart types**, each tuned to the
a16z / Jason Saltzman editorial house style. The engine is a registry: every
chart type is one module, so new types drop in without rewiring anything.

The goal is the "a person assumes a studio spent hours on this" look — designed
defaults (serif headlines on warm paper, curated earthy palettes, one-accent
emphasis, number-as-hero labels, header rule + footer wordmark, editorial
callouts) so output looks finished without manual tweaking. A dark `simula`
theme applies the same discipline for scroll-stopping LinkedIn graphics.

## Quick start

```bash
# 1. Install dependencies (one-time, isolated venv recommended)
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt

# 2. Render an example to interactive HTML
./.venv/bin/python scripts/render.py examples/budget_flow.json

# 3. Open the result
open output/budget_flow.html
```

Static export (needs `kaleido`, included in requirements):

```bash
./.venv/bin/python scripts/render.py examples/energy_flow.json -f png   # for slides/LinkedIn
./.venv/bin/python scripts/render.py examples/energy_flow.json -f svg   # vector
```

## CLI

```
python scripts/render.py SPEC.json [options]

  -o, --out PATH        Output path (extension infers format if -f omitted)
  -f, --format FMT      html (default) | svg | png
  -t, --theme NAME      midnight (default) | simula | editorial | brand
  --png-scale N         PNG resolution multiplier (default 2 = retina)
```

**Chart types** (set via `chart_type`) — **30 in all**: `bar`
(single/grouped/stacked/100%/diverging, v or h), `line` (line/area/annotated),
`combo` (dual-axis bar + multi-line), `scatter`/bubble (+ trendline, 2×2 quadrant,
connected path), `pie`/donut, `waterfall`, `dot` (lollipop/dumbbell), `heatmap`,
`treemap`, `sunburst`, `small_multiples`, `histogram`, `box`/violin, `radar`,
`slope`, `bump`, `candlestick`, `table`, `bignumber` (KPI), `gauge`, `bullet`,
`sankey`, `funnel`, `marimekko` (mosaic), `pyramid` (population), `choropleth`
(map), `pictograph` (waffle), `beeswarm`, `stream` (ThemeRiver), `ridgeline`.
Full field spec in [`references/chart_types.md`](references/chart_types.md). Run
`python scripts/build_gallery.py` to render a contact sheet of every example.

**Themes:** `midnight` (dark, high-impact — default), `simula` (dark, on-brand
for Simula — palette pulled from the logo's cyan→indigo→violet gradient),
`editorial` (the a16z / Jason Saltzman press look — warm paper, navy serif,
earthy palette), `brand` (light, modern indigo).

## Inputs

A graphic is a small JSON **spec**. Full schema and rules are in
[`SKILL.md`](SKILL.md#the-spec-format); the short version:

| Field | What it is |
|---|---|
| `chart_type` | which renderer — one of 30 (see the list above / `references/chart_types.md`) |
| `title` / `subtitle` / `source` | headline, one-line takeaway, attribution |
| `theme` | `editorial` (default) \| `simula` \| `midnight` \| `brand` |
| `footer` / `wordmark` | optional brand strip: CTA line + wordmark + rule + crosshatch |
| `value_format` / `value_prefix` / `value_suffix` | number formatting |
| `nodes` / `links` | Sankey data: `[{ "id", "label", "color?" }]` + `[{ "source", "target", "value", "color?" }]` |
| `stages` | Funnel data: `[{ "label", "value", "color?" }]` top-to-bottom |
| `bars` (+ `orientation`, `highlight`) | Bar data: `[{ "label", "value", "color?" }]`; `orientation` `"v"`/`"h"`, `highlight` label(s)/index(es) |

### Example invocations (what a user might say to Claude)

- *"Take this budget table and make a Sankey showing where the money goes — dark
  theme, for a LinkedIn post."*
- *"We had 10k signups, 6.2k activated, 2.6k converted to paid. Diagram the
  funnel."*
- *"Visualize national energy flow from sources to end use, editorial style."*
- *"Make an a16z-style bar chart of AI's share of software spend by year,
  highlight 2026."*

## Architecture

```
claude-graphics-skill/
├── SKILL.md                  # Skill definition (frontmatter + instructions)
├── README.md                 # This file
├── PROGRESS.md               # per-type quality tracker (a16z-fidelity scores)
├── requirements.txt          # plotly (core) + kaleido (optional static export)
├── references/
│   ├── chart_types.md        # full field spec for every chart_type
│   └── a16z_observations.md  # house-style calibration notes (real charts studied)
├── scripts/
│   ├── render.py             # CLI: load spec → dispatch by chart_type → write file
│   ├── build_gallery.py      # render every example → output/gallery.html contact sheet
│   ├── theme.py              # palettes + themes + color helpers (the "designed" layer)
│   └── charts/
│       ├── __init__.py       # imports each chart module to register it
│       ├── base.py           # registry + shared title/axis/legend/footer/value helpers
│       ├── bar.py            # bar: single/grouped/stacked/100%/diverging (v/h), dual-label
│       ├── line.py           # line + area (gradient, markers, dash, end-labels, events)
│       ├── combo.py          # dual-axis bar + multi-line (marker shapes)
│       ├── scatter.py        # scatter/bubble + trendline + 2×2 quadrant + connected path
│       ├── pie.py            # pie + donut
│       ├── waterfall.py      # bridges / walks
│       ├── dot.py            # lollipop + dumbbell (before/after)
│       ├── heatmap.py        # matrix / cohorts (triangular)
│       ├── treemap.py        # nested parts-of-whole
│       ├── hierarchy.py      # sunburst (radial hierarchy)
│       ├── small_multiples.py# grid of mini charts (shared scale)
│       ├── histogram.py      # distribution of one variable
│       ├── box.py            # box / violin by group
│       ├── radar.py          # multi-dimension comparison
│       ├── slope.py          # two-period slopegraph
│       ├── bump.py           # rank-over-time
│       ├── candlestick.py    # OHLC price action
│       ├── table.py          # styled data table
│       ├── indicator.py      # bignumber (KPI) + gauge + bullet
│       ├── marimekko.py      # variable-width 100%-stacked columns (mosaic)
│       ├── pyramid.py        # population pyramid (mirrored cohorts)
│       ├── choropleth.py     # shaded map (US states / world)
│       ├── pictograph.py     # waffle / isotype ("X out of 100")
│       ├── beeswarm.py       # distribution dots by group
│       ├── stream.py         # stream graph (centered ThemeRiver)
│       ├── ridgeline.py      # overlapping density ridges (joyplot)
│       ├── sankey.py         # Sankey (auto crossing-minimizing layout + highlight)
│       └── funnel.py         # funnel
├── examples/                 # 50 ready-to-render specs, ≥1 per chart type
│                             #   (mostly editorial/a16z; a few simula dark-brand)
└── output/                   # generated graphics + gallery.html (gitignored)
```

Run `python scripts/build_gallery.py` to see all 50 examples at once. Each
`examples/*.json` filename is descriptive (e.g. `category_growth_diverging.json`,
`cloud_market_marimekko.json`, `latency_ridgeline.json`).

**Extending:** add `scripts/charts/<type>.py` with a `@register("<type>")`
renderer returning a Plotly `Figure`, then import it in
`scripts/charts/__init__.py`. Themes and the title/source furniture apply for
free. `sankey.py` and `funnel.py` use entirely different Plotly traces but share
the same theming/furniture — copy `funnel.py` (the simpler of the two) as a
template for a new chart type.
