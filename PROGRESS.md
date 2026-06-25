# PROGRESS — a16z charts expansion

Branch: `a16z-charts-expansion` (dedicated LOCAL repo, no remote, never pushed).
Method: render → **Read the PNG** → critique vs `references/a16z_observations.md`
→ fix shared helpers → re-read → regress (build_gallery) → commit. One type/commit.

Scores are honest a16z-fidelity (1–5). "done" = the PNG truly looks studio-made.

## Phase 1 — existing types
| type | example | status | score | note |
|---|---|---|---|---|
| bar — horizontal | tool_ranking_bar | done | 5 | reference standard (callout, full-bleed rule, num-hero) |
| bar — vertical | ai_spend_bar | done | 5 | callout + rule + rounded caps |
| bar — diverging stacked | manufacturing_construction | done | 5 | matches a16z reference chart 4 |
| bar — grouped/100% | venture_stacked_bar, channel_mix_percent_bar | done | 5 | verified: full stacks, dot legend, % axis |
| line — multi | valuation_line | done | 5 | line_palette + dash cycle + circle legend + end-value labels |
| line — single | machinery_line | done | 5 | no legend, halo markers, end-value label (fixed cat-axis collapse bug) |
| area | rtd_share_area | done | 5 | gradient fill + halo markers + per-point value labels; cat-axis hardened |
| combo | inference_combo, industrial_imports_combo | done | 5 | multi-line on RHS + distinct marker shapes; rounded bars; dot legend |
| scatter/bubble | spend_retention_scatter | done | 5 | halo markers, navy labels, optional trendline + highlight |
| pie/donut | revenue_mix_pie | done | 5 | verified: direct outside labels, no legend, clean |
| waterfall | arr_waterfall | done | 5 | fixed negative fmt (-$9M); teal gains/rust losses/navy totals |
| dot (lollipop/dumbbell) | adoption_dumbbell | done | 5 | verified: gray→teal connectors, end labels, legend |
| heatmap | retention_heatmap | done | 5 | triangular cohort grid: null cells render blank |
| treemap | spend_treemap | done | 5 | verified: value-sized cells, direct labels, palette |
| sunburst | spend_sunburst | done | 5 | verified: nested hierarchy, labeled segments |
| small_multiples | regions_small_multiples | done | 5 | verified: shared-scale 2x3 grid, clean |
| histogram | deal_size_histogram | done | 5 | verified: clean distribution, axis titles |
| box/violin | latency_box | done | 5 | verified: median+mean, distinct colors, clean |
| radar | product_radar | done | 5 | verified: two filled polygons, dot legend |
| slope | margin_slope | done | 5 | verified: risers teal / fallers rust, dual labels |
| bump | model_bump | done | 5 | verified: smooth rank ribbons, right-edge labels |
| candlestick | price_candlestick | done | 5 | verified: teal/rust OHLC candles, wicks, $ axis |
| table | startups_table | done | 5 | verified: navy header, zebra rows |
| bignumber | kpi_bignumber | done | 5 | verified: big navy numbers, green deltas |
| gauge | nps_gauge | done | 5 | fixed: faint accent track so full arc reads |
| bullet | quota_bullet | done | 5 | verified: teal bars, rust targets, big-number deltas |
| sankey | budget/energy/user_funnel, simula | done | 5 | verified: crossing-free hub flow, labeled nodes |
| funnel | conversion_funnel, simula_funnel | done | 5 | verified: proportional stages, %+value labels |

**Phase 1 COMPLETE — every existing type scores 5.**

## Phase 2 — a16z signature types to ADD
| type | status | note |
|---|---|---|
| diverging horizontal bar | done (5) | category_growth_diverging; teal-right/rust-left from central zero, callout |
| marimekko / mosaic | todo | variable-width stacked bars |
| 2×2 quadrant scatter | done (5) | positioning_quadrant; dotted dividers + corner labels, gridless |
| choropleth map | todo | US/world |
| population pyramid | todo | diverging horizontal by cohort |
| connected/path scatter | done (5) | inflation_path_scatter; spline threads points in time order |
| stream graph | todo | wiggle-stacked area |
| ridgeline | todo | stacked density ridges |
| beeswarm / strip | todo | distribution dots |
| pictograph / isotype | todo | icon arrays |
| annotated time series | todo | event markers on a line |

## Shared-helper backlog (cascades to many types)
- Line/area: marker support, dash-style cycle, gradient area fill, per-point value
  labels, end-of-line VALUE labels, single-series legend suppression.
- Stacked bar: per-x outline highlight; two-line x-axis labels.

## Log
- a59a7fa baseline import (all current work).
- 3d23d83 a16z calibration notes + PROGRESS.
- line: line_palette (separated hues), dash-style cycle, circle-dot legend,
  single-series legend suppression, end-of-line VALUE labels, halo markers.
  Fixed: end-label at x=x[-1] collapsed categorical x-axis → pin to paper x=1.0.
