# Chart type reference — full spec for every chart_type

Read this when you need the exact fields for a chart type. Every spec also has a
matching file in `examples/` that is a complete, copy-pasteable starting point —
often faster to copy an example and edit it than to build from scratch.

## Shared header (all chart types)

```jsonc
{
  "chart_type": "bar",             // see the 23 types below
  "title": "Where the Series A Went",
  "subtitle": "$14M raised → deployed across 18 months",  // the takeaway, not a restatement
  "source": "Source: Simula internal data",               // attribution / credibility
  "theme": "editorial",            // editorial (default) | simula | midnight | brand
  "value_format": ",.1f",          // Python format spec for numbers
  "value_prefix": "$",             // wraps the number, e.g. "$"
  "value_suffix": "M",             // e.g. "M", "%", " TWh", " users"
  "height": 680, "width": 1150     // optional canvas size
}
```

Colors are auto-assigned from the theme's harmonious palette — **omit per-item
`color` unless** the user wants specific brand colors. Keep `subtitle` to one
insight.

---

## bar — single / grouped / stacked (vertical or horizontal)

Single series via `bars`; `orientation` `"v"` (default) or `"h"`; `highlight`
emphasizes bars (label(s) or index(es)), muting the rest. Direct value labels.

```jsonc
{ "chart_type": "bar", "orientation": "v", "highlight": ["2026"],
  "bars": [ { "label": "2021", "value": 4 }, { "label": "2026", "value": 48 } ] }
```

`note` adds a one-line **italic editorial callout** — the strongest "a human
made this" cue. Pass a string and it auto-places in the emptiest corner
(descending ranking → bottom, ascending → top; horizontal → right, vertical →
follows the trend), or a dict `{ "text", "x", "y", "xanchor", "yanchor", "align",
"width" }` for manual control. Use `<br>` for line breaks. **Write one by
default** when the data has a clear takeaway; set `"note": false` to suppress it.

```jsonc
{ "chart_type": "bar", "orientation": "h", "highlight": ["Foundation models"],
  "note": "Foundation models took a third of every dollar.",
  "bars": [ { "label": "Foundation models", "value": 1.4 } ] }
```

Grouped/stacked via `x` + `series`; `"stacked": true` to stack, `"percent": true`
for a 100%-stacked composition (auto % axis). Multi-series uses a circle-dot
legend + value axis (no per-segment labels), the broader 9-tone `stack_palette`,
cream segment borders, and a prominent zero baseline — all automatic.

```jsonc
{ "chart_type": "bar", "stacked": true, "x": ["Q1", "Q2"],
  "series": [ { "name": "Early", "values": [34, 38] }, { "name": "Late", "values": [40, 55] } ] }
```

**Diverging stacks** ("scaled by contribution" — the a16z signature): include
**negative** values and they stack *down* from zero while positives stack *up*,
diverging from the zero line. No extra flag — just `"stacked": true` with mixed
signs. Tuning fields: `y_dtick` (force gridline spacing, e.g. `10` for 10% steps)
and `bargap` (bar width; lower = wider, ~`0.22` for a dense year-by-year stack).

The **editorial footer strip** (the a16z bottom band) is opt-in on any
multi-series **bar**, stacked-area **line**, or **combo**: `footer` draws a
brand/CTA line bottom-left (e.g. `"More charts: simula.ad"`) and `wordmark` a
brand mark bottom-right (e.g. `"SIMULA"`), separated from the chart by a
full-width rule and a faint diagonal **crosshatch** paper-weave (disable with
`"footer_texture": false`). When either is set, the source line drops below the
legend automatically. The round-dot legend and broader `stack_palette` apply to
those same multi-series types. See `examples/manufacturing_construction.json` for
the full diverging-stacked + footer reference.

```jsonc
{ "chart_type": "bar", "stacked": true, "value_suffix": "%", "y_dtick": 10,
  "bargap": 0.22, "footer": "More charts: simula.ad", "wordmark": "SIMULA",
  "x": ["2013", "2014", "2015"],
  "series": [ { "name": "Chemical", "values": [15, 18, 30] },
              { "name": "Primary Metal", "values": [0.5, 0.5, 3] },
              { "name": "Transportation Equipment", "values": [2, 4, -10] } ] }
```

## line — line or area, multi-series

`x` + `series`. Lines get **maximally-separated colors** (`line_palette`) plus an
auto **dash-style cycle** (solid → dot → dash-dot …) so series never blur — set a
per-series `"dash"` or `"dash_styles": false` to override. `markers` → halo'd
dots; `fill` → area tint (a **vertical gradient** for a single series);
`point_labels: true` prints the value above every point (a16z area style);
`stacked` → stacked area (dot legend). A **single
series draws no legend** (the title carries it). `end_values: true` prints each
line's final value at its right end in the series color (a16z signature);
`label_mode: "end"` instead labels the series NAME at the end (no legend).

```jsonc
{ "chart_type": "line", "end_values": true, "x": ["2022", "2023", "2024"],
  "series": [ { "name": "Software", "values": [55, 35, 70] },
              { "name": "Internet", "values": [40, 28, 48], "dash": "dot" } ] }
```

## combo — dual-axis bar + line

A `bar` and a `line` over shared `x`; each side can set `axis_title`, `prefix`,
`suffix`. For "volume vs. rate" stories.

```jsonc
{ "chart_type": "combo", "x": ["Jan", "Feb"],
  "bar":  { "name": "Tokens (B)", "axis_title": "Tokens (B)", "values": [5, 16] },
  "line": { "name": "Price", "axis_title": "Price ($/1M)", "prefix": "$", "values": [1.6, 0.95] } }
```

## scatter — incl. bubble

`points` (or grouped `series` of points). `size` per point → bubble; `show_labels`
annotates points; `x_title`/`y_title` label axes.

```jsonc
{ "chart_type": "scatter", "show_labels": true, "x_title": "ACV ($K)", "y_title": "Retention (%)",
  "points": [ { "x": 55, "y": 117, "label": "Business", "size": 260 } ] }
```

## pie — pie or donut

`slices`; `"donut": true` for a ring. Use sparingly (bars/treemap usually win).

```jsonc
{ "chart_type": "pie", "donut": true,
  "slices": [ { "label": "Enterprise", "value": 52 }, { "label": "SMB", "value": 12 } ] }
```

## waterfall — bridges / walks

`steps`; each `type` is `relative` (default gain/loss), `absolute` (a hard value,
usually first), or `total` (running sum, usually last). Gains/losses/totals
colored distinctly.

```jsonc
{ "chart_type": "waterfall",
  "steps": [ { "label": "Start", "value": 100, "type": "absolute" },
             { "label": "New", "value": 42 }, { "label": "Churn", "value": -18 },
             { "label": "End", "value": 124, "type": "total" } ] }
```

## dot — lollipop or dumbbell (before/after)

Auto-detected: items with `value` → lollipop (with optional `highlight`); items
with `start` + `end` → dumbbell (set `start_name`/`end_name` for the legend).

```jsonc
{ "chart_type": "dot", "start_name": "2024", "end_name": "2026",
  "items": [ { "label": "Engineering", "start": 34, "end": 78 } ] }
```

## heatmap — matrix / cohorts

`x` (cols), `y` (rows, top→bottom), `z` (rows × cols). `show_values` prints each
cell. Sequential scale from canvas color → accent (override with `colorscale`).

```jsonc
{ "chart_type": "heatmap", "show_values": true, "x": ["M0", "M1"], "y": ["Jan", "Feb"],
  "z": [ [100, 64], [100, 67] ] }
```

## treemap — nested parts-of-a-whole

`items` with `label` + `value`; add `parent` to nest. Good when a pie has too
many slices.

```jsonc
{ "chart_type": "treemap",
  "items": [ { "label": "Compute", "value": 420 }, { "label": "Storage", "value": 180 } ] }
```

## sunburst — radial hierarchy

Same `items`/`parent` shape as treemap; rings instead of rectangles. Container
parents can use `value: 0` (children determine size).

```jsonc
{ "chart_type": "sunburst",
  "items": [ { "label": "Cloud", "value": 0 },
             { "label": "EC2", "value": 60, "parent": "Cloud" } ] }
```

## small_multiples — a grid of mini charts

One `panel` per slice on a shared scale (the honest way to compare many). Set
`panel_type` (`line`/`bar`), `columns`, `fill`, and a shared `x`.

```jsonc
{ "chart_type": "small_multiples", "panel_type": "line", "columns": 3, "fill": true,
  "x": ["Q1", "Q2", "Q3"],
  "panels": [ { "title": "Enterprise", "values": [12, 18, 25] },
              { "title": "SMB", "values": [5, 6, 6] } ] }
```

## histogram — distribution of one variable

`values` (raw numbers); optional `bins`, `x_title`, `y_title`.

```jsonc
{ "chart_type": "histogram", "bins": 24, "x_title": "Deal size ($K)",
  "values": [8, 12, 15, 9, 22, 31, ...] }
```

## box — box plot (or violin) by group

`groups`, each `{ name, values }`. `"violin": true` for violins; `show_mean`
toggles the mean line.

```jsonc
{ "chart_type": "box",
  "groups": [ { "name": "Free", "values": [180, 220, 250, ...] },
              { "name": "Pro", "values": [90, 110, 130, ...] } ] }
```

## radar — multi-dimension comparison

`axes` (3–8 dimensions) + `series`, each `{ name, values }` aligned to `axes`.

```jsonc
{ "chart_type": "radar", "axes": ["Speed", "Quality", "Cost"],
  "series": [ { "name": "Us", "values": [9, 8, 7] }, { "name": "Them", "values": [6, 9, 5] } ] }
```

## slope — slopegraph (two periods)

`items` with `start` + `end`; `left_label`/`right_label` head the columns. Risers
are accent-colored, fallers rust.

```jsonc
{ "chart_type": "slope", "left_label": "2024", "right_label": "2026",
  "items": [ { "label": "Platform", "start": 62, "end": 78 } ] }
```

## bump — rank over time

`x` + `series` of raw `values`; ranks are computed per period (highest = #1) and
drawn as smooth lines labeled at the right.

```jsonc
{ "chart_type": "bump", "x": ["Jan", "Mar", "May"],
  "series": [ { "name": "Model A", "values": [10, 14, 22] } ] }
```

## candlestick — OHLC price action

`data` of `{ date, open, high, low, close }`. Up days accent, down days rust.

```jsonc
{ "chart_type": "candlestick", "value_prefix": "$",
  "data": [ { "date": "Wk 1", "open": 100, "high": 108, "low": 97, "close": 106 } ] }
```

## table — styled data table

`columns` + `rows` (row = list of cell strings). Navy header, zebra rows. When
the data *is* the story.

```jsonc
{ "chart_type": "table", "columns": ["Company", "ARR"],
  "rows": [ ["Simula", "42"], ["Globex", "28"] ] }
```

## bignumber — KPI callouts

`metrics`, each `{ label, value, reference? }` (delta vs reference auto-computed,
green up / rust down). One or many side by side.

```jsonc
{ "chart_type": "bignumber",
  "metrics": [ { "label": "ARR ($M)", "value": 42, "reference": 31 } ] }
```

## gauge — single value on a dial

`value`, optional `target` (threshold + delta) and `range`.

```jsonc
{ "chart_type": "gauge", "value": 62, "target": 50, "range": [0, 100] }
```

## bullet — actual vs target

`items`, each `{ label, value, target?, max? }`. Compact KPI-tracking bars.

```jsonc
{ "chart_type": "bullet", "value_prefix": "$", "value_suffix": "K",
  "items": [ { "label": "Enterprise", "value": 920, "target": 800, "max": 1100 } ] }
```

## sankey — flows between nodes

`nodes` (referenced by `id`; `label` shown) + `links` (`source`/`target` are
node ids, `value` sets width). `show_values_in_labels` appends throughput;
`highlight` (node ids/labels on a path) mutes everything else for a one-story
look. Layout auto-minimizes crossings — prefer tree/hub-shaped data.

```jsonc
{ "chart_type": "sankey", "highlight": ["raise", "rnd"],
  "nodes": [ { "id": "raise", "label": "Series A" }, { "id": "rnd", "label": "R&D" } ],
  "links": [ { "source": "raise", "target": "rnd", "value": 7.0 } ] }
```

A typo'd link id is a clear error, not a silent misdraw. For genuinely
many-to-many data, group small flows into an "Other" node rather than shipping a
tangle.

## funnel — conversion stages

`stages` top-to-bottom; each bar shows value + share of the top stage.

```jsonc
{ "chart_type": "funnel",
  "stages": [ { "label": "Impressions", "value": 1200000 }, { "label": "Engaged", "value": 384000 } ] }
```
