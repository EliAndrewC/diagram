I didn't run a web search on this file. None of its 67 numbers is a question about the world that the record hasn't already ruled on. Every row is either a fixed rule (NONE, CONVENTION, NOT-ABOUT-THE-WORLD) or traced to a research page. Nothing was fetched, so nothing went on the sources ledger.

## Sources (all from the record; no web pages read)

- **`0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html`** (the channel-widths drawing page). Its width table has "head race (the whole fan, above the fork) 6.0 small main canal" and "delivery ditch 2.5 -> 1.2 lateral dwindling to field ditch". The 6.0 rests on the excavated Hattori central canal, "1.4-2 m (~5-7 ft)", and the 1537 Jugo canal rules, "just over six shaku" (Yayoi period and 1537).
- **`0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.html`** (the findings page): "This record's widths for a village brook and a town river, about 2 m (~7 ft) and 20 m (~66 ft), are GUESSES. Brooks and rivers are natural watercourses, not things anyone built, and no record from before modern times that we read gives either a width."
- **`0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.drawing.html`** (for the 3 ft that sits beside the 9 on line 250): "about 3 ft along the head race or a canal - a large bund, inside the 80-150 cm (~2.6-4.9 ft) of the large bunds along the canal at the Hattori site. The 3 ft is a calibration against that one excavated site". The page sets it beside a canal; the code uses it beside a brook.

**Why no search ran.** Only two values looked like questions about the world, and neither is one:
- **`feed_brook` 420** is the shortest distance to the brook's source, which `approach_legs` always places off the canvas (`max(run, to_edge + 60)`). It is an anchor point for the drawing, and no source could say where an off-sheet anchor sits.
- **`stage_waterward` 30 / 20** carry each reed strip a little past the dike's bounding box so the strips on two sides meet at a corner. Page 0019's drawing page already covers the reed fringe on the water-facing sides; how far a strip runs past the corner is a joining of the drawing.

A brook width also needed no search: page 0068 records it as already searched, with no source found.

## Table

| file::unit | line | value | ruling | what the number does |
|---|---|---|---|---|
| brook.py::brook_skirt | 170 | 40 | NOT-ABOUT-THE-WORLD | how far the crop check looks either side of a station, beyond the stride |
| brook.py::brook_skirt | 251 | 12 | NOT-ABOUT-THE-WORLD | the narrower look-around for a cut corner point |
| brook.py::brook_skirt | 251 | 1e9 | NONE | sentinel floor (-1e9, no baseline) |
| brook.py::axes_off | 331 | 0.3 | NOT-ABOUT-THE-WORLD | cutoff: can the flank direction tilt this segment, or is it across the fall |
| brook.py::bend_at | 358 | 8 | NOT-ABOUT-THE-WORLD | match distance: a segment this near the run counts as part of it |
| brook.py::bend_runs | 391 | 0.3 | NOT-ABOUT-THE-WORLD | cutoff: can the flank direction leave a level run |
| brook.py::bend_runs | 401 | 0.3 | NOT-ABOUT-THE-WORLD | cutoff: does a straight run lie across the fall |
| brook.py::level_offsets | 413 | 0.3 | NOT-ABOUT-THE-WORLD | floor on a divisor (stops division by near-zero) |
| brook.py::chord_offsets | 426 | 0.3 | NOT-ABOUT-THE-WORLD | floor on a divisor (stops division by near-zero) |
| brook.py::feed_brook | 517 | 420 | NOT-ABOUT-THE-WORLD | shortest distance to the approach's start point, which is always off the canvas |
| brook.py::feed_brook | 553 | 7 | NOT-ABOUT-THE-WORLD | bearing search: 7 steps either side (10° each, to ±70°); only a code note calls it a guess, no page |
| brook.py::feed_brook | 553 | 8 | NOT-ABOUT-THE-WORLD | upper end of the same bearing range |
| brook.py::feed_brook | 567 | 7 | NOT-ABOUT-THE-WORLD | the same bearing search, round-the-field pass |
| brook.py::feed_brook | 567 | 8 | NOT-ABOUT-THE-WORLD | the same, upper end |
| brook.py::draw_intake | 693 | 6 | CITED 0068.drawing | fallback head-race width, 6.0 ft ("head race ... 6.0") |
| brook.py::draw_intake | 694 | 0.2 | NONE | stops division by a tiny sine |
| brook.py::open_race_mouth | 759 | 7 | GUESS 0068.html | fallback brook width ("about 2 m (~7 ft) ... are GUESSES") |
| brook.py::open_race_mouth | 759 | 8 | NOT-ABOUT-THE-WORLD | match distance: a race starting this near the bank is the one at the tap |
| brook.py::open_race_mouth | 762 | 0.05 | NONE | tiny tolerance: race not already at the tap |
| brook.py::open_race_mouth | 765 | 2.5 | CITED 0068.drawing | fallback width for the colour fade at the race mouth ("delivery ditch 2.5"); see lead 4 |
| brook.py::weir_glyph | 833 | 0.9 | CONVENTION | weir stake dots: start of their spread along the bar |
| brook.py::weir_glyph | 833 | 1.8 | CONVENTION | weir stake dots: length of their spread |
| brook.py::weir_glyph | 839 | 0.2 | CONVENTION | crib weir: inner tick position |
| brook.py::weir_glyph | 839 | 0.62 | CONVENTION | crib weir: outer tick position |
| brook.py::weir_glyph | 839 | 0.7 | CONVENTION | crib weir: tick stroke width |
| brook.py::weir_glyph | 841 | 0.45 | CONVENTION | frame weir: log line offset |
| brook.py::weir_glyph | 841 | 0.8 | CONVENTION | frame weir: log stroke width |
| brook.py::weir_glyph | 841 | 0.95 | CONVENTION | frame weir: log line extent |
| brook.py::weir_glyph | 842 | 0.7 | CONVENTION | frame weir: stake dot radius |
| brook.py::weir_glyph | 842 | 5 | CONVENTION | frame weir: stake dot count |
| brook.py::weir_glyph | 844 | 0.6 | CONVENTION | basket weir: seam stroke width |
| brook.py::weir_glyph | 845 | 0.12 | CONVENTION | basket weir: weave slant |
| brook.py::weir_glyph | 845 | 0.25 | CONVENTION | basket weir: inner weave position |
| brook.py::weir_glyph | 845 | 0.4 | CONVENTION | basket weir: weave stroke width |
| brook.py::weir_glyph | 845 | 0.75 | CONVENTION | basket weir: outer weave position |
| brook.py::weir_glyph | 847 | 0.55 | CONVENTION | fence weir: stake dot radius |
| brook.py::weir_glyph | 847 | 6 | CONVENTION | fence weir: stake dot count |
| brook.py::weir_glyph | 849 | 1.2 | CONVENTION | upstream lip: width as a share of half the bar's thickness |
| brook.py::weir_glyph | 849 | 1.6 | CONVENTION | upstream lip: widest allowed |
| brook_course.py::exit_legs | 55 | 1e9 | NONE | sentinel (no edge on this axis) |
| brook_course.py::exit_legs | 66 | 0.15 | NOT-ABOUT-THE-WORLD | cutoff: the course's heading still runs downhill |
| brook_course.py::round_the_brooks | 300 | 7 | GUESS 0068.html | fallback brook width (same guess as line 759) |
| brook_rules.py::monotone_down | 206 | 0.01 | NOT-ABOUT-THE-WORLD | rounding slack in the "runs downhill" test |
| brook_rules.py::reserved_box | 250 | 9 | GUESS 0068.html | brook width in the keep-off band; doesn't match: the page and `comb.py` use 7 (lead 1) |
| fit.py::fit_field | 45 | 0.06 | NOT-ABOUT-THE-WORLD | the fit's own stopping tolerance, inside the band page 0017 sets |
| fit.py::fit_field | 45 | 9 | NOT-ABOUT-THE-WORLD | number of fitting rounds |
| fit.py::_fit_at_aspect | 195 | 0.35 | NOT-ABOUT-THE-WORLD | lower end of the size-multiplier search range |
| fit.py::_fit_at_aspect | 195 | 2.2 | NOT-ABOUT-THE-WORLD | upper end of the size-multiplier search range |
| fit.py::_fit_at_aspect | 231 | 0.001 | NONE | tiny clamp just inside the range |
| fit.py::_fit_at_aspect | 280 | 0.03 | NOT-ABOUT-THE-WORLD | stop when the range is narrower than about one plot row |
| fit.py::_fit_at_aspect | 288 | 0.001 | NONE | tiny clamp for the probe at the range's top |
| fit.py::_predict_k | 315 | 0.2 | NOT-ABOUT-THE-WORLD | lowest believable exponent in the size prediction |
| fit.py::_predict_k | 315 | 6 | NOT-ABOUT-THE-WORLD | highest believable exponent in the size prediction |
| fit.py::tail_dangles | 378 | 5 | NOT-ABOUT-THE-WORLD | match distance: two canal ends this close count as one |
| polder.py::reservoir_clear_of_crop | 42 | 96 | NOT-ABOUT-THE-WORLD | how many points sample the reservoir's ellipse |
| polder.py::walk_pond_uphill | 57 | 12 | NOT-ABOUT-THE-WORLD | step size of the uphill walk that seats the reservoir |
| polder.py::dike_gaps_at_channels | 99 | 64 | NONE | lookup-grid cell size; the output is identical with or without it (the full-scan test checks this) |
| polder.py::inlet_to_rim | 132 | 30 | NOT-ABOUT-THE-WORLD | number of halving steps to find the rim |
| polder.py::stage_polder | 295 | 109 | NONE | seed mask (0x6D) |
| polder.py::fit_polder | 334 | 0.06 | NOT-ABOUT-THE-WORLD | the fit's own tolerance, inside the 12% band page 0017 sets |
| polder.py::fit_polder | 334 | 9 | NOT-ABOUT-THE-WORLD | number of fitting rounds |
| polder.py::fit_polder | 370 | 6 | NOT-ABOUT-THE-WORLD | fewest rows in the grid search |
| polder.py::fit_polder | 370 | 44 | NOT-ABOUT-THE-WORLD | most rows in the grid search |
| polder.py::_nearest_pair | 423 | 6 | NOT-ABOUT-THE-WORLD | rows search, lower end |
| polder.py::_nearest_pair | 423 | 45 | NOT-ABOUT-THE-WORLD | rows search, upper end (exclusive) |
| polder.py::_polder_candidate | 462 | 0.4 | NOT-ABOUT-THE-WORLD | edge-wobble step, eased until the block fills its box |
| polder.py::_polder_candidate | 462 | 0.3 | NOT-ABOUT-THE-WORLD | the same, next step |
| polder.py::_polder_candidate | 462 | 0.2 | NOT-ABOUT-THE-WORLD | the same, next step |
| polder.py::_polder_candidate | 462 | 0.12 | NOT-ABOUT-THE-WORLD | the same, last step |
| polder.py::dike_face | 531 | 32 | NOT-ABOUT-THE-WORLD | how many bins sample the dike's outer face |
| polder.py::stage_waterward | 634 | 30 | CONVENTION | reed strip runs on past the dike's low-side end, so strips meet at the corner |
| polder.py::stage_waterward | 634 | 20 | CONVENTION | the same past the high-side end |
| polder.py::stage_waterward | 635 | 30 | CONVENTION | the same, across the other axis |
| polder.py::stage_waterward | 635 | 20 | CONVENTION | the same, across the other axis |
| polder.py::stage_waterward | 652 | 20 | CONVENTION | strip's outer edge carried past the canvas edge |
| polder.py::stage_waterward | 653 | 20 | CONVENTION | the same |
| polder.py::stage_waterward | 654 | 20 | CONVENTION | the same |
| polder.py::stage_waterward | 655 | 20 | CONVENTION | the same |

## Leads (not followed)

1. **The 9 on line 250 is out of step with the code it claims to copy.** `reserved_box` builds its keep-off band as `9.0 / 2 + 3.0`. Its docstring says it drops plots by the same test `_comb_draw_hem` uses, but `comb.py` (around line 383) uses `self.px(7.0) / 2 + self.px(3.0)`. So the box treats as wet a ring of plots that the drawn hem keeps. The 9 is older than the 2026 move of the project (commit 5be123073), so its origin is in the history before that.
2. **The channel-widths drawing page contradicts the 7 ft brook.** It says "the brook arrives narrower than the head race it feeds" and asks "Why might a head race run wider than the brook that feeds it?" With the race at 6.0 ft, a 7 ft brook is wider. Either the prose or the guess needs adjusting. Also, `BROOK_DRAWN_W`'s docstring cites the drawing page, but the GUESS sentence about the brook's width is only on the findings page.
3. **The 30 vs 20 overrun in `stage_waterward` is uneven and nothing explains it.** I ruled it CONVENTION. But the strip is recorded as marsh where nothing may be built, so the extra 30 ft at a corner does add wet ground on the map.
4. **The 2.5 on line 765 is a delivery-ditch width used as the head race's fallback.** The head race's own width is 6.0, so if the fallback ever fires it uses the wrong width.