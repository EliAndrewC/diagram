# Tasks - feature 298, tiled ground cover

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (A-F). Order: the tiles; the zones and the finish's cover block; bamboo;
the page; the consumers, tests and record; the measurement; land.

## Setup

- [ ] T01 The base: `/tmp/base298` at the commit before this feature's code, the five pool hamlets timed (`stagemin.sh`, best of three) and their files sized
      research: rendering

## The tiles (A)

- [ ] T02 [US1] [US2] `settlement/land/tiles.py`: `cover_pattern(kind, bs)` for grass, reed and bamboo - seamless, at the scatter's density - with tests (A)
      research: rendering

## The zones and the cover block (B)

- [ ] T03 [US1] `KeepoutGrid.shape()` - the union of the filed keep-outs as one geometry - with a test against `taken_many` (B)
      research: rendering
- [ ] T04 [US1] The commons records its cover (ring, bare ground) in place of `grass_scatter`'s throw; the pines unchanged (B)
      research: rendering
- [ ] T05 [US1] The marsh records its cover in place of `_throw`; the re-throw (`offer_rethrow`, `throw_again`, `throw_to_the_view`'s registry) retires (B)
      research: rendering
- [ ] T06 [US1] `flush_covers()`: the cover block spliced right after the land, the shapes clipped to the view; `_cull_cover_in` adds to the bare ground; `_blade_groups` / `flush_blade_groups` / `_blade_starts` retire (B)
      research: rendering

## Bamboo (C)

- [ ] T07 [US2] `bamboo_stand` draws its ring with the bamboo tile; `marks` the grid's seat count (C)
      research: rendering

## The page (D)

- [ ] T08 [US1] The scrub's hit region from its recorded cover; `HIT_FROM_MARKS`, `marks_region` and the premerged blade path retire; the census clean (D)
      research: rendering

## Consumers, tests, record (E)

- [ ] T09 The scatter audit's blade/dot/reed families, `placement_stages`' watermark list, the blade/reed tests rewritten against the covers (E)
      research: rendering
- [ ] T10 The record: the research entries and the modals that describe the glyphs; `entry-drift` on each pair owed; `dev/performance.md` (E)
      research: rendering

## Measure and land (F)

- [ ] T11 [US3] The five pool hamlets regenerated; the base and the clone timed back to back and sized; `measurements.md` (F)
      research: rendering
- [ ] T12 The gate green; the GM's look (Kashikawa, Inashiro) and the settlement-review decision recorded; land
      research: rendering
