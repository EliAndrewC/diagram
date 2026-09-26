# Implementation Plan: The wind is northwest unless a map declares otherwise

**Feature**: `261-northwest-wind-by-default` | **Date**: 2026-09-26 | **Spec**: [`spec.md`](spec.md) |
**Research**: [`research.md`](research.md) (R1-R4) | **Measurements**: [`measure.py`](measure.py)

## Summary

The scripted hamlet generator's wind becomes the regional northwest on every map that declares none; the
slope-derived wind (`windward_for`, `WIND_TURNS`) and the seat re-read in `stage_ways` are retired; the seat
search refuses a margin whose back is more than 45 degrees off the wind except as a recorded last fallback;
the manifest records the wind's source; the windbreak's pop-up says the belt's side and why; the record, the
docs and the notes say the new rule; and the five pool hamlets are re-rolled - two of them re-seeded, as the
spec's Edge Cases allow, because R1 measured them failing at their old seeds.

## Technical Context

Python 3, the `hamletgen` package (`plan.py`, `consts.py`, `cluster.py`, `ways/track.py`, `water/skeleton.py`),
the interactive page (`interactive/place.py`, `page.py`, `classes/greenery.py`, `assets/siblings.json`), one
research fragment and its notes, `hamletgen.md`, three CLAUDE.md index lines, five pool generators' manifests and
notes. No new dependency. The seat filter is one dot product per margin already being scored: no index is owed
(it adds no overlap check).

## Performance bookends

The seat filter costs one dot product per candidate margin. The pool maps change geometry (a different seat
and, for two, a different seed), so their stage times move for that reason and not for new work; `make done`'s
own perf ratchet judges it, and any band it reports is explained against R4's re-rolls.

## Constitution Check

- **I. Independent review**: **PASS** - `spec-fidelity` accepted the spec in two rounds; this plan is reviewed by
  the same agent before a task is ticked; `settlement-review` runs on the re-rolled maps at acceptance.
- **VI. Verify before reporting done**: **PASS** - every task names its verification; R4 is measured on the
  shipped manifests by `measure.py`.
- **X. Python discipline**: **PASS** - ruff, pyrefly, 100% coverage; the new branches (the off-wind fallback, the
  divided off-wind margin, the pop-up sentence's three cases) each have a test.
- **XII. Historical grounding**: **PASS** - the northwest default is already cited in `research/vegetation/030`
  (the Sendai *igune*, the monsoon); no new source is used, so no source-reader or applicability run is owed; the
  entry is rewritten to state the rule and its footnote gloss corrected, and `quote-check` and `record-format`
  run on it.
- **XIII. No known regressions**: **PASS with a measured baseline** - the 48-seed cohort was rolled on the
  unmodified engine in a detached worktree and on this one (R3).
- **XIV. Fix defects where found**: the divided-margin fallback that let an off-wind divided margin win before
  the off-wind fallback was found in this work and fixed in it (D3).
- **XVI. Build what was asked**: **PASS** - the wind is never renamed and no map declares one. Two exceptions were
  put to `spec-fidelity` in MODE 1 and both were REFUSED (R4): putting a wind-facing divided seat ahead of feature
  230's strike-out, engine-wide. What stands instead is the spec's own path - re-seeding - for the three maps that
  needed it. The off-wind last resort (D2) is recorded on the map and forbidden on the pool, and it is raised
  with the GM in the hand-off.

## The design

### D1 - The default is a constant, the declaration the only override

`plan_site` sets `windward = spec.windward or DEFAULT_WINDWARD` (`"NW"`); `windward_for` and `WIND_TURNS` are
deleted, with the reasoning for the retirement kept at `DEFAULT_WINDWARD` in `consts.py`. `HamletSpec.windward`
already existed and is unchanged: it is the declaration. The manifest records `wind_source` =
`declared` | `regional`.

### D2 - The seat bends to the wind: a 45-degree bar, and a recorded fallback

`seat_cluster` computes each margin's facing (outward normal . wind). A margin under `WIND_BACK_MIN_DOT` (cos 45
deg) is not a candidate; it is kept in an `offwind` list used only when no wind-facing margin, clean or
divided, exists. The seat reports `offwind`; `stage_ways` writes `meta.seat_offwind` where it used to rename the
wind. 45 degrees is half the compass-quarter spacing, so the back faces the windward quarter itself - the
spec-fidelity round judged it calibration, not a loophole. The bar is a map convention and says so at the
constant. The pool may not carry `seat_offwind` (the pool test).

### D3 - The fallback order: wind-facing clean, off-wind clean, divided (wind-facing first)

Feature 230's rule stands: a margin the brook divides is used only when EVERY margin is divided. So the order is
a clean wind-facing margin, then a clean off-wind one (recorded as `seat_offwind`), then the best divided margin
with a wind-facing one first. Putting a wind-facing divided margin ahead of a clean off-wind one was measured and
put to the exception check twice, and refused (R4): over the 48 cohort specs that order took 12 divided seats, and
in 3 of them a byre, a well, a garden or farm fixtures stood across the brook from their houses - feature 230's
own failure - where this order produced none. What this order costs instead is off-wind seats outside the pool
(22 of the 48, 10 with belts under 50 clumps, 4 with none; R4), which is why a pool map that falls back is
re-seeded (D4) and why the fallback is raised with the GM.

### D4 - Re-seeding, and only re-seeding, for the three maps that failed at their seeds

R1 measured Sawada (falls northwest) falling back off the wind at seed 6, and Mizuguchi seating 8 of 12 at seed
23; R4 measured Kashikawa falling back off the wind at seed 3 with a belt of no trees. The seed searches (R2, R4)
kept each map's declared fall, sink and knobs: Sawada 24 (the only one of thirty with a clean wind-facing seat),
Mizuguchi 27 (12/12, undivided, 349 clumps at 325 degrees), Kashikawa 8 (one of five clean seeds; 14 drew more trees
but wrapped the belt 333 degrees round the houses, which the record rules out). Inashiro keeps its reference seed 4
once the divided test is fixed (D7). Nothing in the spec's "When no seed works" list is done: no bar loosened, no
wind declared, no rename, no declared knob changed, no belt in the crop. The reason is in each generator's
docstring, and the pool test holds the belt's arc to 200 degrees as well as its bearing.

### D5 - The pop-up: the notes win, the default names the side and its reason

`place.windbreak_default(meta)` mirrors `lane_default`: on a map that records `wind_source`, it says which sides
the belt stands on and whether the wind is the region's or the place's declared one; a manifest without it (the
frozen hand-authored pool) gets nothing and the class text stands alone. The class `What` loses "high side"
(false where the northwest is downhill) and gains the north-and-west rule; its `Entry` names
`vegetation/030`, the section the rule is written from; `siblings.json` says the same.

### D6 - The record and the docs

`research/vegetation/030`'s paragraph that claimed "northwest by default" while describing the slope rule is
rewritten to the rule as built, with the GM's 2026-09-26 words; the arc figures are re-measured on the re-rolled
maps (`measure.py`); the `kisetsufu-jawiki` note's gloss stops calling the slope reading "this page's
derivation". `hamletgen.md`, the hamletgen and sitegen indexes, and the five notes files' "Known open" wind lines
are updated.

### D7 - The divided test asks which bank, not which half (constitution XIV)

`seat_cluster`'s divided test recorded the LATERAL half of the band for every sample point within twice the band's
depth of the brook, so a brook running behind the band parallel to the margin read as dividing it (R4: Kashikawa
and Inashiro "divided" with every house on one bank). `brook_banks()`, lifted to module level and unit-tested,
takes the side of the nearest brook segment for each band point instead. Found in this work; fixed in it.

### D8 - The knob values the re-seeds dropped are declared back

Re-seeding changes every rolled knob on a map, and the pool lost its only exhibit of four knob values (R6). A knob
owes one map per value, so each is declared on the map that showed it before - the same mechanism as Sawada's
`intake="open"` - and `HamletSpec` gains `byre_form`, pinned onto the settlement engine's knob, because that one had
no spec field. No wind rule moves: the declarations are re-rolled and measured with the rest (R5).

## Phases

1. Engine: D1, D2, D3 with their unit tests (plan, cluster, surface).
2. Measurement: R1-R3 (trial, seed search, cohort both ways).
3. Pool: D4, the five re-rolls, the pool test, R4.
4. Page: D5 with its tests.
5. Record and docs: D6; `quote-check` and `record-format` on the entry; `entry-drift` on the windbreak class.
6. Acceptance: `make done`, `settlement-review` one agent per map, ledger rows.

## Complexity Tracking

None.
