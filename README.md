# claude-graphics-skill

A Claude Skill for generating **polished, presentation-ready data
visualizations** from structured data. Sankey diagrams are the flagship use
case; the engine is modular so flow charts, funnels, and network diagrams can be
added without rewiring anything.

The goal is the "viral LinkedIn data graphic" look — designed defaults
(typography, curated palettes, title/subtitle/source furniture) so output looks
finished without manual tweaking.

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

**Chart types** (set via `chart_type`) — **23 in all**: `bar`
(single/grouped/stacked/100%, v or h), `line` (line/area), `combo` (dual-axis
bar+line), `scatter`/bubble, `pie`/donut, `waterfall`, `dot` (lollipop/dumbbell),
`heatmap`, `treemap`, `sunburst`, `small_multiples`, `histogram`, `box`/violin,
`radar`, `slope`, `bump`, `candlestick`, `table`, `bignumber` (KPI), `gauge`,
`bullet`, `sankey`, `funnel`. Full field spec in
[`references/chart_types.md`](references/chart_types.md). Run
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
| `chart_type` | which renderer: `sankey`, `funnel`, or `bar` |
| `title` / `subtitle` / `source` | headline, one-line takeaway, attribution |
| `theme` | `midnight` \| `simula` \| `editorial` \| `brand` |
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
├── requirements.txt          # plotly (core) + kaleido (optional static export)
├── scripts/
│   ├── render.py             # CLI: load spec → dispatch by chart_type → write file
│   ├── theme.py              # palettes + themes + color helpers (the "designed" layer)
│   └── charts/
│       ├── __init__.py       # imports each chart module to register it
│       ├── base.py           # registry + shared title/axis/legend/value helpers
│       ├── bar.py            # bar: single, grouped, stacked (v/h)
│       ├── line.py           # line + area, multi-series
│       ├── combo.py          # dual-axis bar + line
│       ├── scatter.py        # scatter + bubble
│       ├── pie.py            # pie + donut
│       ├── waterfall.py      # bridges / walks
│       ├── dot.py            # lollipop + dumbbell (before/after)
│       ├── heatmap.py        # matrix / cohorts
│       ├── treemap.py        # nested parts-of-whole
│       ├── small_multiples.py# grid of mini charts (shared scale)
│       ├── sankey.py         # Sankey (auto crossing-minimizing layout + highlight)
│       └── funnel.py         # funnel
├── examples/                 # fabricated specs, ready to render (mostly editorial/a16z)
│   ├── ai_spend_bar.json         # Bar · vertical, single highlight
│   ├── tool_ranking_bar.json     # Bar · horizontal ranking
│   ├── venture_stacked_bar.json  # Bar · stacked multi-series
│   ├── valuation_line.json       # Line · multi-series
│   ├── inference_combo.json      # Combo · dual-axis bar + line
│   ├── spend_retention_scatter.json # Scatter · bubble
│   ├── revenue_mix_pie.json      # Pie · donut
│   ├── arr_waterfall.json        # Waterfall · ARR bridge
│   ├── adoption_dumbbell.json    # Dot · dumbbell (before/after)
│   ├── retention_heatmap.json    # Heatmap · cohorts
│   ├── spend_treemap.json        # Treemap · cloud spend
│   ├── regions_small_multiples.json # Small multiples · line grid
│   ├── budget_flow.json          # Sankey · editorial
│   ├── energy_flow.json          # Sankey · editorial (hub)
│   ├── user_funnel.json          # Sankey · editorial, highlight mode
│   ├── conversion_funnel.json    # Funnel · editorial
│   ├── simula_sankey.json        # Sankey · simula dark brand (crossing-free)
│   └── simula_funnel.json        # Funnel · simula dark brand
└── output/                   # generated graphics (gitignored)
```

**Extending:** add `scripts/charts/<type>.py` with a `@register("<type>")`
renderer returning a Plotly `Figure`, then import it in
`scripts/charts/__init__.py`. Themes and the title/source furniture apply for
free. `sankey.py` and `funnel.py` use entirely different Plotly traces but share
the same theming/furniture — copy `funnel.py` (the simpler of the two) as a
template for a new chart type.
