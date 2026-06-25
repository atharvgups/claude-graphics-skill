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
| bar — diverging vertical | index_yoy_diverging | done | 5 | 2nd pass: rust negatives, zero line, labels clear x-axis |
| bar — diverging horizontal | category_growth_diverging | done | 5 | teal-right/rust-left from central zero |
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
| marimekko / mosaic | done (5) | cloud_market_marimekko; width=size, stacks=share, auto-contrast labels |
| 2×2 quadrant scatter | done (5) | positioning_quadrant; dotted dividers + corner labels, gridless |
| choropleth map | done (5) | datacenter_choropleth; US-states/world, sequential scale, cream borders |
| population pyramid | done (5) | workforce_pyramid; mirrored bars, center divider, side headers |
| connected/path scatter | done (5) | inflation_path_scatter; spline threads points in time order |
| stream graph | done (5) | compute_stream; centered baseline, spline bands |
| ridgeline | done (5) | latency_ridgeline; self-contained Gaussian KDE, overlapping ridges |

**Phase 2 COMPLETE — all 11 a16z signature types added, each scores 5.**
| beeswarm / strip | done (5) | deal_cycle_beeswarm; deterministic bin-packing, median ticks |
| pictograph / isotype | done (5) | ai_adoption_pictograph; 10x10 waffle, largest-remainder counts |
| annotated time series | done (5) | dau_annotated_line; events:[] dotted markers + top labels |

## Shared-helper backlog (cascades to many types)
- Line/area: marker support, dash-style cycle, gradient area fill, per-point value
  labels, end-of-line VALUE labels, single-series legend suppression.
- Stacked bar: per-x outline highlight; two-line x-axis labels.

## STATUS: Phase 1 + Phase 2 COMPLETE
30 registered chart types, all scoring 5; 45 examples; gallery renders clean;
docs (SKILL/README/chart_types) in sync; ~/Downloads/graphics.skill rebuilt
(115KB, no junk). Local commits only on `a16z-charts-expansion` — never pushed.
Second pass done: vertical-diverging fix; verified grouped bars, long-label
auto-margin, and dark-theme (simula) robustness of all new furniture (dot legend,
footer + crosshatch, zero line, diverging). Added grouped + long-label + vertical-
diverging examples. 47 examples total.

## Log
- a59a7fa baseline import (all current work).
- 3d23d83 a16z calibration notes + PROGRESS.
- line: line_palette (separated hues), dash-style cycle, circle-dot legend,
  single-series legend suppression, end-of-line VALUE labels, halo markers.
  Fixed: end-label at x=x[-1] collapsed categorical x-axis → pin to paper x=1.0.
