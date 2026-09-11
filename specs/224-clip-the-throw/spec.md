# Feature 224 - clip the throw, the glossary scan, and the drop's last pass

**Status**: IN PROGRESS 2026-09-11. `spec-fidelity` round 1 FAITHFUL (D1 a faithful application of the 2026-09-08 ruling; FR-002 the necessary form of item 1).
**Request**: [`request.md`](request.md). **Research**: [`research.md`](research.md) - R1 the before (from
specs/223 R2 and this feature's own measurements), R2 the after. **Predecessors**: 223 (the off-frame blades
culled at finish; the phase table these three items come from), 218 (the scatter's `KeepoutGrid`), 200
(`drop_offmap`), 182/209 (the glossary).

## Summary

The three items the 223 report left, as listed. The scatter still throws every point over the whole parcel and
pays the keep-out test and the blade draws for the ~90% of them the frame will clip; the page's glossary scan
runs 729 word-boundary regex searches over the whole explanations text; `drop_offmap` still walks every
classed string. This feature clips the throw to a frame the scatter can predict, prefilters the glossary scan
with a substring test, and gives the drop's shape parser a direct path - and measures each.

## Functional requirements

- **FR-001 The scatter's throw is clipped to a predicted frame.** `settlement/land/cover.py` `commons` (the
  grass tufts, brush dots and pines of a grazing or scrub parcel) and `settlement/land/wet.py` `marsh` (the wet
  tint, reeds and glints) throw uniformly over the parcel's bounding box and test each point against the
  keep-out grid before drawing it; on a hamlet the parcel runs to the canvas edge while the frame is a third
  of the sheet, so about 90% of the throws pay the test and the draws for ink that is culled at finish (223).
  Each throw is now tested FIRST against a frame the stage predicts, and a point outside it costs nothing
  more than its two coordinate draws. The prediction (`hamletgen/hinterland/frame.py`, `scatter_frame`) is
  the bounding box of the crop's own frame-setting boxes at that moment (`Settlement._crop_boxes`, the same
  reader `crop_to_content` uses) together with every polygon reserved but not yet drawn that the crop will
  later take in (the title pocket when it is outside the content, the bamboo seats, the woodland patches,
  the belt), grown by the crop's margin and a safety pad (D2), recorded in the manifest as
  `meta.scatter_frame`. The throw COUNT is unchanged (the parcel's area over the density constant), so the
  density inside the frame is the density it was; the realized texture inside the frame re-rolls, because the
  draws an off-frame point used to consume are no longer made - permitted by the GM's 2026-09-08 ruling that a
  map may look a little different for speed when the rules hold, and each scatter already rolls in its own
  RNG scope so nothing outside the scatter moves. A settlement with no prediction (every hand-authored tier,
  and the woodland parcels, whose crowns are recorded features) throws as before.
- **FR-002 The prediction is verified, never trusted.** At `finish()`, the view is compared with
  `meta.scatter_frame`; a view that reaches past it on any side is recorded as `meta.scatter_frame_breach`
  (the overhang per side) - a breach means a strip inside the frame may have been thrown nothing, which is a
  visible defect. A gate test over every pool manifest asserts no breach, and R2 records the largest overhang
  the pool and a 48-map cohort actually reach against the pad, which is how the pad is justified (D2).
- **FR-003 The glossary scan is prefiltered.** `interactive/page.py` `glossary_for` runs
  `re.search(r"\b" + variant + r"\b")` for every variant of every glossary term over the whole explanations text
  - 729 searches on Inashiro, 0.28 s of the 0.33 s step. A variant that is not a substring of the text cannot
  match with boundaries either, so a plain `in` test (C speed) runs first and the regex only on the few that
  pass; the same terms come out for the same text.
- **FR-004 `drop_offmap`'s shape parser takes a direct path.** `raster.drop_offmap` `fix_shape` parses every
  element's attributes into a dict by a general regex before judging it. The writer emits each shape with a
  fixed attribute order, so a per-tag regex that captures the coordinates directly is tried first, the general
  parse kept as the fallback for any other order; verdicts identical.
- **FR-005 Measured before and after, per hamlet**, as 223's R2 measured (the phase marks): the scatter's stage
  time, `flush_blade_groups`, `drop_offmap`, the explanations step, the SVG size and the regen total.
- **FR-006 Verification.** `make done` green; the pool regenerated; a settlement-review of the five maps, since
  the scatter's texture re-rolls (D1) - the same rules, a different throw.

## Success criteria

- SC-1 `stage_hinterland` under 1.0 s on Inashiro, Kashikawa, Kuwabata and Mizuguchi and under 1.4 on Sawada
  (1.3 / 1.8 / 1.4 / 1.1 / 1.8 after 223); no breach on any pool map or cohort seed.
- SC-2 The explanations step under 0.1 s on every hamlet (0.30-0.38 after 223), the glossary the same terms.
- SC-3 `drop_offmap` under 0.1 s on every hamlet (0.15-0.22 after 223).
- SC-4 Regeneration per pool hamlet down by at least 1 s on every map (8.4-14.3 after 223).

## Decisions Recorded

- **D1 The in-frame texture re-rolls; nothing else moves.** A stream-preserving form was priced: to keep the
  in-frame draws identical, an off-frame point would still have to consume the draws it consumed - and which
  draws those are depends on the keep-out test's answer, the expensive thing. So the texture inside the frame
  is a different throw of the same density under the same keep-outs; the houses, fields, lanes, water, crowns
  and every recorded feature are untouched because each scatter rolls inside its own `rng_scope`. The GM's
  ruling (2026-09-08) covers exactly this; the settlement-review judges the result.
- **D2 The safety pad is 120 px, measured.** The crop is the frame-setting boxes plus `CROP_MARGIN` (48 px),
  and `crop_hugs_content` forbids more than 56 px of view past the content; the prediction already holds every
  reserved polygon the crop can later take in. What it cannot hold is a hard feature placed after the
  hinterland that lands outside everything known - a notice board on a lane's verge past the last house, a
  crossing - which the 120 px band covers with the margin; the pool's and the cohort's largest realized
  overhangs are in R2 and the pad is revisited if either approaches it. A breach is recorded, not hidden
  (FR-002).
- **D3 The throw count is not rescaled to the clipped box.** Throwing the parcel's own count and discarding the
  outside points keeps the in-frame density exactly what the density constant states; scaling the count to the
  clipped area would have to re-derive the constant's meaning from a box the parcel does not have.

## Review history

- Round 1 (2026-09-11): FAITHFUL - the three FRs are the three items in order; D1 rests on the GM's general 2026-09-08 ruling with its conditions met; FR-002 is how "the rules held" is known rather than asserted; the aside: item 3's cost may also sit in the per-string scans around `fix_shape`, SC-3 bounds it either way.
