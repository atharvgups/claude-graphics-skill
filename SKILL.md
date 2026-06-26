---
name: graphics
description: >-
  Turn data into polished, presentation-ready charts in a consistent editorial
  (a16z / Jason Saltzman) house style. Use for ANY chart, graph, or data graphic
  — bar (incl. grouped/stacked/diverging), line, area, combo, scatter/bubble,
  quadrant, pie/donut, waterfall, dot/lollipop, heatmap, treemap, sunburst,
  marimekko, histogram, box/violin, beeswarm, ridgeline, radar, slope, bump,
  stream, candlestick, table, KPI/big-number, gauge, bullet, choropleth map,
  population pyramid, pictograph, sankey, and funnel. Trigger whenever the user
  wants to make/build/visualize/plot/chart data, turn numbers into a
  graphic/infographic, make something look good for a deck/LinkedIn/report, names
  a specific chart type, or pastes a table/CSV. Produces interactive,
  self-contained HTML (plus optional SVG/PNG) that looks finished by default.
---

# Graphics — Presentation-Ready Data Visualizations

This skill turns structured data into **designed** graphics — the kind that look
at home in a board deck or a viral LinkedIn post, not a default chart export. It
covers **30 chart types** behind one JSON spec, all rendered in a consistent
editorial (a16z / Jason Saltzman) house style so a whole set of charts reads as
if one studio made them. The engine is modular, so new chart types drop in
without touching the pipeline.

## When to use this

Reach for this skill whenever the user wants a *finished visual* from data:

- **Any chart or graph** — "make/build/create a chart", "visualize/plot this",
  "chart these numbers", or naming a specific type (bar, line, scatter, …).
- **"Make this data into a graphic"** — they have numbers (or a pasted table/CSV)
  and want something shareable and polished.
- **Flows & funnels** — a Sankey for quantities *moving between* things
  (sources → uses, stages → outcomes); a funnel for conversion drop-off.

Default to the `editorial` theme and let the data shape pick the chart type (the
data → type guide is below).

## How it works

> **Always render through this engine. Never hand-write Plotly/matplotlib code or
> a `<script>` chart.** The entire point of the skill is the consistent editorial
> look, which lives in `scripts/`. Writing your own chart bypasses it and you get
> a generic export. The only correct workflow is: write a JSON spec → run
> `scripts/render.py`. If unsure the engine works, run the self-check first —
> `python scripts/render.py --selfcheck` — which confirms the renderer is live
> (and tells you the one-time setup command if deps are missing). Do that setup;
> do not fall back to ad-hoc charting.

A graphic is described by a small **JSON spec**. You render it with one command:

```bash
python scripts/render.py SPEC.json [-o OUT] [-f html|svg|png] [-t THEME]
```

- **HTML** (default) is interactive (hover, drag) and fully self-contained — it
  renders as an artifact with no network access. Prefer it.
- **SVG / PNG** are static exports for slides/print/LinkedIn (need `kaleido`).
- **Chart types** (`chart_type` field) — one spec format, **30 chart types**:
  `bar` (single/grouped/stacked/100%/**diverging**, v or h), `line` (multi-series,
  line/area, **annotated** via `events`), `combo` (dual-axis bar + multi-line),
  `scatter`/bubble (+ **trendline**, **2×2 quadrant**, **connected/path**),
  `pie`/donut, `waterfall`, `dot` (lollipop/dumbbell), `heatmap`, `treemap`,
  `sunburst`, `small_multiples`, `histogram`, `box`/violin, `radar`, `slope`,
  `bump`, `candlestick`, `table`, `bignumber` (KPI), `gauge`, `bullet`, `sankey`,
  `funnel`, `marimekko` (mosaic), `pyramid` (population), `choropleth` (map),
  `pictograph` (waffle), `beeswarm`, `stream` (ThemeRiver), `ridgeline`. Full
  field spec for each in `references/chart_types.md`; the guide below maps data → type.
- **Themes**: `editorial` (**the default** — the a16z / Jason Saltzman press
  style: warm paper canvas, deep-navy serif headline, tight earthy palette; this
  is the consistent house aesthetic and what you should use unless asked
  otherwise), `simula` (dark, on-brand for Simula content — cyan→indigo→violet
  on slate), `midnight` (dark, high-impact, generic LinkedIn), `brand` (light,
  modern indigo). Override with `-t` or the spec's `"theme"` field. Every theme
  styles every chart type identically, so output stays consistent across charts.

When making content **for Simula**, default to the `simula` theme — its dark
canvas is built to stop the scroll in a LinkedIn feed and its palette is pulled
straight from the Simula logo.

### Setup (first run only)

The engine needs Plotly. If imports fail, install into a local venv so you don't
touch system Python:

```bash
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
# then run with ./.venv/bin/python scripts/render.py ...
```

`kaleido` (in requirements.txt) is only needed for SVG/PNG; HTML works without it.

## The spec format

Every spec shares the same "header" fields (title/subtitle/source/theme/value
formatting); the data fields differ per chart type.

**Shared header (all chart types):**

```jsonc
{
  "chart_type": "sankey",          // "sankey" | "funnel" | "bar"
  "title": "Where the Series A Went",
  "subtitle": "$14M raised → deployed across 18 months",  // one-line takeaway
  "source": "Source: Simula internal data",               // attribution / credibility
  "theme": "editorial",            // editorial (default) | simula | midnight | brand
  "value_format": ",.1f",          // Python format spec for numbers
  "value_prefix": "$",             // wraps the number, e.g. "$"
  "value_suffix": "M",             // e.g. "M", "%", " TWh", " users"
  "height": 680, "width": 1150     // optional canvas size
}
```

The **data fields differ per chart type**. The table below is the cheat sheet;
**`references/chart_types.md` has the full field spec for every type**, and every
`examples/*.json` file is a complete, copy-pasteable spec — often the fastest
path is to copy the matching example and edit its data.

| chart_type | key data fields | notes |
|---|---|---|
| `bar` | `bars[]` **or** `x`+`series[]` | `orientation` v/h, `highlight`, `note` callout, `stacked` (mixed signs → diverging), `percent`, `footer`/`wordmark` strip |
| `line` | `x`, `series[]` | `fill`/`stacked` = area, `label_mode: "end"` |
| `combo` | `x`, `bar{}`, `line{}` | dual y-axes; per-side `axis_title`/`prefix`/`suffix` |
| `scatter` | `points[]` or `series[]` | `size` → bubble, `show_labels`, `x_title`/`y_title` |
| `pie` | `slices[]` | `donut: true` for a ring |
| `waterfall` | `steps[]` | step `type`: relative / absolute / total |
| `dot` | `items[]` | `value` → lollipop; `start`+`end` → dumbbell |
| `heatmap` | `x`, `y`, `z[][]` | `show_values`, optional `colorscale` |
| `treemap` | `items[]` (`label`,`value`,`parent?`) | nest via `parent` |
| `sunburst` | `items[]` (like treemap) | radial hierarchy |
| `small_multiples` | `panels[]`, `x` | `panel_type` line/bar, `columns`, shared scale |
| `histogram` | `values[]` | `bins`, `x_title`/`y_title` |
| `box` | `groups[]` | `violin: true` for violins |
| `radar` | `axes[]`, `series[]` | 3–8 axes, 1–3 series |
| `slope` | `items[]` (`start`,`end`) | `left_label`/`right_label` |
| `bump` | `x`, `series[]` | ranks computed automatically |
| `candlestick` | `data[]` (OHLC) | financial price action |
| `table` | `columns[]`, `rows[][]` | styled data table |
| `bignumber` | `metrics[]` | KPI callouts, delta vs `reference` |
| `gauge` | `value` (+`target`,`range`) | single value on a dial |
| `bullet` | `items[]` (`value`,`target`) | actual-vs-target bars |
| `sankey` | `nodes[]`, `links[]` | `highlight` for a story path; auto crossing-min |
| `funnel` | `stages[]` | conversion stages |

**Rules that keep output clean:**

- Colors are auto-assigned from the theme palette — **omit per-item `color`**
  unless the user wants specific brand colors.
- For Sankeys, links reference node `id`s; a typo'd id is a clear error. The
  `highlight` field mutes everything but the named path (the "one story" look).
- Keep `subtitle` to a single insight — that's what makes a graphic *say*
  something rather than just show data.

**Write a callout by default.** When the data has a clear story — a runaway
leader, a surprising gap, a trend — add a one-line `note` stating the takeaway in
plain language (e.g. "Foundation models took a third of every dollar."). This
editorial annotation is the strongest "a human made this" signal. Suppress with
`"note": false` when there's no single punchline.

## The bar: functional AND beautiful

The whole reason this skill exists is that a *correct* chart and a *good* chart
are not the same thing. The graphics this produces are meant to stop the scroll
in a LinkedIn feed and hold up on a board slide — so a render that is accurate
but ugly, cramped, or confusing is a **failure**, not a draft. Treat visual
quality as a hard requirement on par with the data being right.

Concretely, a finished graphic should clear every one of these:

- **Reads in 3 seconds.** The main story is obvious at a glance. The title states
  *what*, the subtitle states the *takeaway* (not a restatement of the title).
- **Nothing is cramped or overlapping.** Labels don't collide with each other or
  sit illegibly on top of busy flows. There's generous whitespace. If it feels
  tight, make the canvas bigger (`height`/`width`) rather than shrinking text.
- **Flows/stages read as distinct shapes**, not a muddy tangle. For Sankeys this
  is mostly about *node ordering* — see below.
- **Color is purposeful and restrained.** Distinct hues, but from the theme
  palette; no clashing or near-duplicate colors. Don't hand-pick colors unless
  the user wants specific brand colors.
- **It looks designed, not exported.** Bold, legible labels; a real headline;
  an attribution/source line. The default themes do this for you — lean on them.

### The quality bar: the a16z / Jason Saltzman house style

The target is the data graphics Jason Saltzman publishes for a16z
([a16z.news/t/charts](https://www.a16z.news/t/charts)) — the gold standard for
"a person sees this and assumes a studio spent hours on it." What makes them
work, and what the `editorial` theme is built to reproduce:

- **Warm paper background**, never stark white — it reads as print, not export.
- **A serif headline in deep navy**, doing the editorial heavy lifting, with a
  quieter one-line subtitle beneath it.
- **A muted, earthy palette** — desaturated teal, ochre, rust, navy, sage.
  Saturated/neon colors are the tell of an amateur chart; restraint is the look.
- **Almost no chrome** — the faintest horizontal gridlines, no borders, no
  boxes, no redundant axes. Whitespace does the framing.
- **Direct labeling** — values sit on the bars/flows and series are labeled in
  place; legends are avoided. One clear emphasis (a single highlighted bar, one
  bold annotation) rather than everything shouting.
- **A small, italic-feeling source line** bottom-left for credibility.

For newsletter/blog/report graphics, default to `editorial` and aim squarely at
this bar. For LinkedIn (especially Simula), `simula`/`midnight` apply the same
discipline on a dark, scroll-stopping canvas.

### Sankey clarity: crossings are handled for you (mostly)

The #1 thing that makes a Sankey "confusing" is flows crossing into a spaghetti
tangle. The renderer fights this automatically: it lays nodes out in
left-to-right columns and orders each column with a **volume-weighted barycenter
sweep**, so the biggest flows run straight across and connected nodes line up.
You do **not** need to hand-order the `nodes` array — tree- and hub-shaped data
come out crossing-free on their own.

Two things to know:

- **Some data can't be made crossing-free.** If many sources each split to the
  same several targets (a near-complete bipartite block), crossings are
  mathematically unavoidable — no ordering removes them. When a render still
  looks busy, the fix is usually the *data*: group small flows into an "Other"
  node, or drop minor links, rather than fighting the layout. (This is the
  single most-recommended tip in Sankey design guides.)
- **Escape hatches** for when you want manual control:
  - `"auto_layout": false` in the spec falls back to Plotly's default ordering.
  - Give any node explicit `"x"` and `"y"` (both 0–1, x=column position,
    y=vertical) to hand-place nodes; this disables auto-layout entirely so your
    positions are never overridden.

## Workflow for producing a graphic

1. **Pick the chart type** by the question the data answers:
   - *Compare / rank categories* → `bar` (horizontal for long labels), or `dot`
     for a lighter ranking.
   - *Composition over time / groups per period* → `bar` + `series` (stacked or
     grouped). *Positive **and** negative contributions per period* → stacked
     `bar` with mixed-sign values (diverging stack — the a16z "scaled by
     contribution" look); add a `footer`/`wordmark` strip for the full press style.
   - *Trend over time* → `line` (use `fill`/`stacked` for area).
   - *Two different scales / "volume vs. rate"* → `combo` (dual-axis bar+line).
   - *Relationship between two variables* (± a 3rd as size) → `scatter`/bubble.
   - *Before vs. after / two points per item* → `dot` (dumbbell).
   - *A start value bridged to an end value by ± steps* → `waterfall`.
   - *A matrix / cohort grid / intensity over two dimensions* → `heatmap`.
   - *Parts of a whole*: few slices → `pie`/donut; many → `treemap`/`sunburst`.
   - *The same chart across many slices* → `small_multiples`.
   - *Distribution of one variable* → `histogram`; *spread across groups* → `box`.
   - *Multi-dimension comparison of a few entities* → `radar`.
   - *Two-period change, line-style* → `slope`; *rank changes over time* → `bump`.
   - *Headline KPI numbers* → `bignumber`; *one value vs a goal* → `gauge`;
     *several actuals vs targets* → `bullet`.
   - *Price/OHLC over time* → `candlestick`. *The data itself is the story* → `table`.
   - *Flow / splitting between things* → `sankey`. *Conversion stages* → `funnel`.
   - *+/− contributions ranked* → diverging `bar` (`orientation:"h"`, mixed signs).
   - *Two dims: category size × its mix* → `marimekko`. *Cohort split by group* → `pyramid`.
   - *Values across a map* → `choropleth`. *Share as "X of 100"* → `pictograph`.
   - *Every observation in a distribution* → `beeswarm`; *many distributions* → `ridgeline`.
   - *Composition flowing over time* → `stream`. *Positioning in 2 dims* → `scatter` + `quadrants`.
   - *A path through 2 dims over time* → `scatter` + `connect`. *Events on a trend* → `line` + `events`.

   When two types fit, prefer the simpler/harder-to-misread one (bar over pie,
   bar over sankey, dot over bar for sparse rankings).
2. **Get the data into spec shape.** From whatever the user gives you (a table,
   a paragraph, a CSV), derive `nodes`/`links`, `stages`, or `bars`. For a
   Sankey, prefer tree/hub-shaped data (it renders crossing-free); if the data
   is a messy many-to-many, reshape it (see above) rather than shipping a
   tangle. Write JSON to a file.
3. **Choose a theme.** Default to `editorial` (the a16z house look) — it's the
   consistent aesthetic and the right call for almost everything. Switch to
   `simula` only for explicit Simula/LinkedIn brand content, `midnight` for
   other dark LinkedIn posts, `brand` for light product decks.
4. **Write a sharp title + subtitle.** The subtitle should state the takeaway.
5. **Render a PNG and LOOK AT IT.** This step is not optional. Run with `-f png`
   and actually open/read the image. You cannot judge a graphic from its spec —
   you have to see it. Check it against every bullet in "The bar" above:
   overlapping labels? crossing flows? cramped? weak title? muddy color?
6. **Fix what you see and re-render.** Bump `height`/`width` for breathing room,
   reorder nodes to undo crossings, tighten the title, adjust the theme. Loop
   step 5–6 until the image genuinely looks good — typically 1–3 passes. Do not
   show the user the first render just because it succeeded.
7. **Then present** the polished result (HTML for interactivity, PNG/SVG for the
   feed/slides) and iterate on their feedback.

**`examples/` has 30 complete, copy-pasteable specs — at least one per chart
type** (filenames are descriptive, e.g. `venture_stacked_bar.json`,
`adoption_dumbbell.json`, `kpi_bignumber.json`, `regions_small_multiples.json`,
`spend_sunburst.json`, `price_candlestick.json`). When building a new graphic,
the fastest path is usually to copy the example for that chart type and swap in
the data. To eyeball the whole library at once, run
`python scripts/build_gallery.py` → opens `output/gallery.html`.

Every editorial example shares the identical a16z aesthetic — that consistency
across all 30 chart types is the point.

## Extending to new chart types

The engine is a registry: each chart type is one module in `scripts/charts/`
that defines `render(spec, theme) -> plotly.Figure` and decorates it with
`@register("name")`. `sankey.py`, `funnel.py`, and `bar.py` are the reference
implementations — they share themes and the title/subtitle/source furniture
(`apply_titles`) but use completely different Plotly traces, which is the proof
the engine generalizes. `bar.py` is the simplest; copy it as a template. To add,
say, a network diagram:

1. Create `scripts/charts/network.py` with a `@register("network")` renderer
   that returns a Plotly `Figure`, pulling colors/fonts from the `theme` dict
   and calling `apply_titles(fig, spec, theme)` for the headline furniture.
2. Add `from . import network` to `scripts/charts/__init__.py`.

That's it — `chart_type: "network"` now works, every theme applies for free, and
the CLI needs no changes. Use `scripts/charts/funnel.py` as the template (it's
the simplest of the two).
