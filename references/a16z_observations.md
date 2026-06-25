# a16z / Jason Saltzman chart house style — calibration notes

Observed from 8 real "Charts of the Week" graphics (a16z.news), June 2026.
These are the ground truth the skill must match. Re-read before judging a render.

## The invariant house system (every chart)
- **Canvas:** warm paper cream, ~`#ECE8DD` (never white). Square-ish aspect (≈1:1).
- **Headline:** deep-navy serif, bold, left-aligned, often 2 lines. `#1E2A44`.
- **Subtitle:** one muted gray-brown serif line stating the *takeaway/units*, not
  restating the title. `#6E6A5F`-ish.
- **Chrome:** only the faintest horizontal gridlines. No axis spines, no tick
  marks, no boxes. X-axis labels float (no line). Y labels small, muted.
- **Legend:** when needed, a **circle-dot** legend below the plot, left-aligned,
  wrapping — never squares. Single-series charts have **NO legend** (title carries).
- **Source line:** small, muted, bottom-left (e.g. "Source: Census").
- **Footer strip:** thin full-width rule, **"More charts: a16z.news/subscribe"**
  (bold italic) bottom-left, **A16Z wordmark** bottom-right, faint diagonal
  **crosshatch** texture behind it.
- **Palette:** muted earthy — teal, navy, slate, sage/olive, ochre, rust, dusty
  rose, gray. One accent carries the story; the rest are quiet. Never neon/rainbow.
- **Labeling:** numbers are the hero, direct on the marks; units small/quiet.

## Per-type observations (and our gaps)

### Combo (bar + lines), dual axis — chart 1
- Sage-green bars (LHS) + **two** lines (RHS): navy with **diamond** markers,
  ochre with **circle** markers. Distinct marker SHAPES per line.
- Circle-dot legend, 3 items. → GAP: our combo does bar + **one** line only, no
  markers. Need multi-line + marker shapes.

### Multi-line — chart 2 ("Investment Has Favored IP")
- 3 lines, each a different color AND **line style**: ochre solid, green solid,
  navy **dotted**. Dash style distinguishes series, not only color.
- No markers here; thick lines (~3px). → GAP: we don't vary dash style.

### Line with end-labels + legend — chart 6 ("RTD Cocktails")
- 3 dashed/dotted lines; the **final value** is labeled at each line's right end
  in the line color (131.3 / 103.8 / 91.4), AND a circle-dot legend names them.
- → GAP: our `label_mode:"end"` labels the NAME; a16z labels the end VALUE and
  still shows a legend for names.

### Single line — chart 5 ("Machinery Construction")
- One teal line, ~3px, gently smoothed, no markers. **No legend.** Y dtick 1.5.
- → GAP: single-series line should auto-suppress the legend.

### Area, single series, gradient — chart 8 ("Cocktails-in-a-Can")
- One blue line + **vertical gradient fill** (line color → transparent downward),
  **circle markers** at each point, and a **bold value label above every point**
  (8.8% … 31.2%). No legend.
- → GAP: our area fill is flat alpha; need gradient, point markers, point labels.

### Diverging stacked bar (vertical) — charts 3 & 4
- Positive up / negative down from a zero line; muted multi-palette; circle-dot
  legend. ✓ We match this well (manufacturing_construction).
- Chart 3 extra: the **latest x-category (Q4'25) is outlined** (ochre stroke around
  the whole stacked bar) to spotlight it. → GAP: no per-x outline highlight.
- X labels are **two-line** (Q1 over '16). → minor GAP.

### Diverging HORIZONTAL bar — chart 7 ("Spirited Away")
- Bars diverge L/R from a vertical zero line: positives green to the right,
  negatives dusty-rose to the left. Category labels right-aligned on the left.
- **Two labels per bar:** the headline % (bold) and a smaller contribution "+6.63
  pp" beneath (muted). Dark inset core encodes the contribution; light extension
  the full value. No legend.
- → BIG GAP: we have no diverging horizontal bar at all. High priority (Phase 2).

## Priority gaps distilled
1. **Line/area overhaul** (cascades to line, area, combo): markers (circle default),
   per-series dash styles, gradient area fill, per-point value labels, end-of-line
   VALUE labels, single-series → no legend.
2. **Diverging horizontal bar** — new capability.
3. **Combo**: support multiple lines + distinct marker shapes.
4. **Stacked bar**: optional outline-highlight of one x-category; two-line x labels.
