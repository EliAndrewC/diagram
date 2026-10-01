# Tasks - feature 298, tiled ground cover

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (A-F). Order: the tiles; the zones and the finish's cover block; bamboo;
the page; the consumers, tests and record; the measurement; land.

## Setup

- [x] T01 The base: `/tmp/base298` at the commit before this feature's code, the five pool hamlets timed (`stagemin.sh`, best of three) and their files sized
      research: rendering
      verify: DONE. DONE. /tmp/base298 at 258626e2f; five pool hamlets timed and sized (research R1, R2)

## The tiles (A)

- [x] T02 [US1] [US2] `settlement/land/tiles.py`: `cover_pattern(kind, bs)` for grass, reed and bamboo - seamless, at the scatter's density - with tests (A)
      research: rendering
      verify: DONE. DONE. settlement/land/tiles.py grass/reed/bamboo tiles, seamless (_wrapped), at the scatter densities; tests/settlement/test_tiles_298.py

## The zones and the cover block (B)

- [x] T03 [US1] `KeepoutGrid.shape()` - the union of the filed keep-outs as one geometry - with a test against `taken_many` (B)
      research: rendering
      verify: DONE. DONE. KeepoutGrid.shape (the grown union _trees_for builds); test against hit_many; taken_many retired with its last callers
- [x] T04 [US1] The commons records its cover (ring, bare ground) in place of `grass_scatter`'s throw; the pines unchanged (B)
      research: rendering
      verify: DONE. DONE. commons records a grass Cover (keep shape + marshes + woods less their fringe + crescents + pond); grass_scatter removed; pines unchanged
- [x] T05 [US1] The marsh records its cover in place of `_throw`; the re-throw (`offer_rethrow`, `throw_again`, `throw_to_the_view`'s registry) retires (B)
      research: rendering
      verify: DONE. DONE. marsh records a reed Cover (keep shape at the tuft pads); _throw, offer_rethrow, throw_again, throw_to_the_view, scatter_strips, feather_keeps, _band_half_width removed
- [x] T06 [US1] `flush_covers()`: the cover block spliced right after the land, the shapes clipped to the view; `_cull_cover_in` adds to the bare ground; `_blade_groups` / `flush_blade_groups` / `_blade_starts` retire (B)
      research: rendering
      verify: DONE. DONE. _header reserves defs/scrub/pasture/marsh slots right above the land; flush_covers draws each zone clipped to the view; _cull_cover_in adds to the bare ground; blade buckets retired

## Bamboo (C)

- [x] T07 [US2] `bamboo_stand` draws its ring with the bamboo tile; `marks` the grid's seat count (C)
      research: rendering
      verify: DONE. DONE. bamboo_stand draws its ring with the bamboo tile at its own slot; marks = grid seats in the ring

## The page (D)

- [x] T08 [US1] The scrub's hit region from its recorded cover; `HIT_FROM_MARKS`, `marks_region` and the premerged blade path retire; the census clean (D)
      research: rendering
      verify: DONE. DONE. scrub hit region = recorded cover (evenodd path); HIT_FROM_MARKS, marks_region, merge_lines, premerged, blade_starts retired; browser test updated

## Consumers, tests, record (E)

- [x] T09 The scatter audit's blade/dot/reed families, `placement_stages`' watermark list, the blade/reed tests rewritten against the covers (E)
      research: rendering
      verify: DONE. DONE. scatter_audit pine/crown only; placement_stages watermark _covers; tests rewritten (_covered, _ground_points); gate test tests/gate/test_covers_298.py
- [x] T10 The record: the research entries and the modals that describe the glyphs; `entry-drift` on each pair owed; `dev/performance.md` (E)
      research: rendering
      verify: DONE. DONE. research vegetation 050/125/152 (125 heading renamed, link updated), record-format x3 applied; greenery.py modal prose; entry_owed none; dev/performance.md, land/CLAUDE.md

## Measure and land (F)

- [x] T11 [US3] The five pool hamlets regenerated; the base and the clone timed back to back and sized; `measurements.md` (F)
      research: rendering
      verify: DONE. DONE. research R2: regen 0.2-0.7 s faster, hinterland 0.83->0.66 s (Inashiro), SVG <=1/4 on four maps, page 13-30% smaller, PNG 4-22% larger
- [x] T12 The gate green; the GM's look (Kashikawa, Inashiro) and the settlement-review decision recorded; land
      research: rendering
      verify: DONE. DONE. make done green (98 s); Kashikawa and Inashiro looked at; settlement-review not owed (rendering-only, hook); land
