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
Second pass (robustness + fidelity, all committed):
- vertical-diverging bars: rust negatives, zero divider, labels clear the x-axis
- dual-label diverging bar: per-bar `sub` = a16z chart 7 contribution pp
- footer universal across single-series bars (alignment-aware apply_footer)
- long titles/subtitles now wrap to a 2nd line instead of overflowing
- verified: grouped bars, long category labels, lollipop dot, dark-theme (simula)
- README fully synced (architecture tree → all 29 modules + 50 examples)
- new examples: index_yoy_diverging, category_growth_diverging (dual-label),
  round_sizes_grouped, eng_time_bar, context_window_lollipop, simula_models_bar
50 examples total; gallery renders all 50 clean; package rebuilt (120K).

## Headline alignment fix (Isaac feedback — "title slightly indented")
Root cause: on cartesian charts the title/legend/footer anchored to the PLOT
edge (l=40..110px) while the y-axis labels extended further left, so the headline
looked indented. Added `edge_align()` (base.py) and applied across bar (multi),
line, combo, scatter, heatmap, histogram, box, candlestick, bump, slope,
small_multiples, pie (needed automargin=False), radar. All headlines now sit at
the ~28px canvas edge (verified by pixel measurement, title_x≈30). Charts already
at the edge: treemap, sunburst, table, sankey, funnel, dot, waterfall, indicators.

## Colorblind safety (CVD audit — `scripts/qa_colorblind.py`)
Simulated protanopia/deuteranopia/tritanopia (Machado 2009, severity 1.0) on
every theme's `palette`/`stack_palette`/`line_palette`, measuring CIE Lab ΔE.
Gate = ADJACENT pairs (the ones that touch in a stack / are drawn in order) must
clear ΔE 12 under all three CVD types; non-adjacent pairs are warn-only (spatial
separation + direct labels disambiguate).
- editorial.stack_palette (the requested target): PASS — adjacent min ΔE ≥ 19.6
  under all CVD. No collisions → no change, as the brief anticipated.
- editorial.palette / line_palette: PASS (adjacent min ≥ 12.4 / 17.1).
- The sweep CAUGHT a real adjacent fail in simula.palette: teal #14B8A6 and
  magenta #EC4899 collapsed to ΔE 6 under deuteranopia when adjacent. Fixed by a
  same-color-set tail reorder (magenta → index 7); adjacent min now ~16. Lead
  brand gradient untouched, so ≤4-series charts are byte-identical.
- midnight/brand: no adjacent fails (only non-adjacent warnings). Left as-is.
- Follow-up: measured NORMAL-vision near-duplicates too. midnight is clean
  (closest pair ΔE 31). simula's only close pair (indigo|violet ΔE 14) is the
  intentional logo gradient — left as-is. brand had a real near-duplicate:
  #6366F1 (idx 8) sat ΔE ~14-18 from both the indigo (#0) and violet (#5) even
  to normal vision, so 6+-series charts wasted a slot on a look-alike. Swapped
  it for a true blue #3B82F6 (fills the one hue gap, equally vivid); closest
  normal pair is now ΔE 17.9 and the CVD gate still passes.

## Critique pass (render → Read PNG → fix)
Re-read PNGs of the reference standard + representative types. tool_ranking_bar,
manufacturing_construction (diverging stack), inference_combo all hold at 5.
Caught one latent defect on multi-line: end-of-line value/name labels were placed
at the exact data-y with no separation, so series finishing at close values
(valuation_line: 38% vs 30%) stacked and nearly overlapped. Fixed with a shared
`_deconflict()` greedy vertical nudge in line.py — cascades to every multi-line
chart. Verified by re-Read: labels now clearly separated.

## Log
- a59a7fa baseline import (all current work).
- 3d23d83 a16z calibration notes + PROGRESS.
- line: line_palette (separated hues), dash-style cycle, circle-dot legend,
  single-series legend suppression, end-of-line VALUE labels, halo markers.
  Fixed: end-label at x=x[-1] collapsed categorical x-axis → pin to paper x=1.0.
