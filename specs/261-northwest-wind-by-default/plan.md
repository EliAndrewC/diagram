# Implementation Plan: The wind is northwest unless a map declares otherwise

**Feature**: `261-northwest-wind-by-default` | **Date**: 2026-09-26 | **Spec**: [`spec.md`](spec.md) |
**Research**: [`research.md`](research.md) (R0-R8) | **Measurements**: [`measure.py`](measure.py)

## Summary

The scripted hamlet generator's wind becomes the regional northwest on every map that declares none; the
slope-derived wind (`windward_for`, `WIND_TURNS`) and the seat re-read in `stage_ways` are retired; the seat
search refuses a margin whose back is more than 45 degrees off the wind except as a recorded last fallback;
the manifest records the wind's source; the windbreak's pop-up says the belt's side and why; the record, the
docs and the notes say the new rule; and the five pool hamlets are re-rolled. The amendment of 2026-09-27 (the GM:
fix the placement algorithm rather than route around it) makes the brook crossable - ways cross it at fords decked
by a plank bridge, and the brook's strike-out, its re-roll and the far-bank refusal are retired - so Kashikawa and
Mizuguchi return to their original seeds 3 and 23; Sawada keeps 24, its seed 6 refused by the drain and the wet toe.
It also fixes what the settlement-reviews found on the re-rolled maps (D10-D14).

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
  (the Sendai *igune*, the monsoon); the entry is rewritten to state the rule and its footnote gloss corrected, and
  `quote-check` and `record-format` run on it. The amendment's two physical questions (T13, T15) each had a research
  pass: the ford spacing and a farmstead's one bank are guesses with absence notes (`research/water/270`,
  `research/homesteads/250`); the one source newly relied on, `mizu-no-bunka-60`, was already read, and
  `source-applicability` judged it for its new use (APPLICABLE-WITH-LIMITS, the limits written into its registry
  entry).
- **XIII. No known regressions**: **PASS with a measured baseline** - the 48-seed cohort was rolled on the
  unmodified engine in a detached worktree and on this one (R3, and the final engine in R5).
- **XIV. Fix defects where found**: the divided test that read a band's halves instead of the brook's banks (D7),
  and `make record` leaving a notes-only edit unwritable, were found in this work and fixed in it.
- **XVI. Build what was asked**: **PASS** - the wind is never renamed and no map declares one. Two exceptions were
  put to `spec-fidelity` in MODE 1 and both were REFUSED (R4): putting a wind-facing divided seat ahead of feature
  230's strike-out, engine-wide, under the engine as it was. The GM then ruled (2026-09-27) that an engine that
  cannot lay out a valid configuration is fixed rather than routed around: the brook became crossable (D9) and the
  strike-out was retired, so two of the three re-seeds were undone (D4). The off-wind last resort (D2) is recorded on the map and forbidden on the pool, and it is raised
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

### D3 - The fallback order: wind-facing, then off-wind; the brook is scored, never a tier

A clean wind-facing margin first, then an off-wind one (recorded as `seat_offwind`). The brook no longer makes a
tier: feature 230's strike-out - a margin the brook divides used only when every margin is divided - is retired by
the GM's ruling of 2026-09-27, because the engine could not draw the crossing the record attests (R4, R7). A margin
the brook crosses is scored down (`score -= 3.0` times the share of the band's sample points near the brook, at
`seat_cluster`) so an uncrossed one wins when the
two are otherwise level; what feature 230's strike-out protected against - a byre, a well or a garden across the
water from its house (R4) - is now a placement rule on the farmstead itself (D10), not a refusal of the seat. The
two exception checks of R4 refused a wind-first order under the OLD engine; with crossings drawn, the order they
refused is no longer an exception to anything.

### D4 - The seeds: Inashiro 4, Kuwabata 21, Kashikawa 3 and Mizuguchi 23 kept; Sawada 6 -> 24

The spec's Edge Case (amended 2026-09-27) measures each map at its current seed once crossings exist and returns it
to that seed unless a research-supported refusal is recorded. Measured (R7, and R5 for the belt): Kashikawa at seed 3 seats 20/20
wind-facing, the belt 285 crowns at 320 degrees; Mizuguchi at seed 23 seats 12/12 wind-facing astride its brook
(8 and 4), its weir back. Both keep their original seeds. Sawada's seed 6 was refused by the drain and the wet toe
- rules FR-010 keeps, supported by the record - so 24 stands (R2). Nothing in the spec's "When no seed works"
list is done. The reason is in each generator's docstring, and the pool test holds the belt's arc to 200 degrees
as well as its bearing.

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

### D7 - The divided test asked which half, not which bank - fixed, then retired with the strike-out

`seat_cluster`'s divided test recorded the LATERAL half of the band for every sample point near the brook, so a
brook running behind the band read as dividing it (R4). `brook_banks()` fixed it (constitution XIV); the amendment
then retired the divided test altogether (D3), and `brook_banks()` with it. `bank_of()` in
`homesteads/stages.py` stays as the one side test the engine keeps.

### D8 - The knob values the re-seeds dropped are declared back, and stay declared

Re-seeding changes every rolled knob on a map, and the pool lost its only exhibit of four knob values (R6). Two of
those maps are back on their original seeds, and the declarations stay: a declared value holds the exhibit whatever
a later engine change does to the roll. A knob
owes one map per value, so each is declared on the map that showed it before - the same mechanism as Sawada's
`intake="open"` - and `HamletSpec` gains `byre_form`, pinned onto the settlement engine's knob, because that one had
no spec field. No wind rule moves: the declarations are re-rolled and measured with the rest (R5).

### D9 - A way crosses the brook at a ford, and every crossing is decked

`brook_fords(brook, FORD_SPACING, FORD_BEND_DEG)` (ways/checks.py) marks a crossing place every 160 ft (`m:ford-spacing`) along the
brook where its course bends less than 20 degrees over the crossing, so a way can cross it square;
`gap_segments` opens the brook's no-route corridor `FORD_HALF` (30 ft) each side of each ford, so the router passes
there and nowhere else; `ford_crossing` routes the field spur through the nearest ford when its direct line would
cross the water; `stage_crossings`' `bridges()` decks every crossing, as it already did for any way over water. The
far-bank refusal (`far_bank`), the strike-out and the brook re-roll are deleted. Class: accurate for the form (a
hamlet astride its own small channel, `research/water/270`); the spacing and the bend limit are a guess with an
absence note there. Indexed: the fords are a short list per map (under 30), cut into the brook's corridor once.
A crossing is PRICED: the route lattice charges `BROOK_CROSSING_COST_FT` (150 ft, a guess recorded in water/270) for
entering the brook's band, and the string-pull may not take back a crossing the lattice paid to avoid - Kashikawa drew a
lane across the brook and back to reach a house on its own bank. And every crossing is SQUARED at `stage_crossings`
(`square_crossings`, more than 10 degrees off square), the record and the ink together, before `bridges()` lays the deck
along it - a string-pulled way passed the 60 ft ford gap 52 degrees off square. The band is kept once per roll as brook
sample points in a 20 px bucket grid (`set_crossing`), asked per free lattice cell.

### D10 - A farmstead stands whole on one bank (FR-013)

`Settlement._parts_fit` refuses a homestead configuration when the line from the house's center to any part's
(yard, garden bed, kura) crosses a stream (`_parts_across_stream`), and `farmstead_fixtures` refuses a fixture or
persimmon seat on the same test (`across_the_brook`). Measured before (R8): Inashiro 4 parts across, Mizuguchi 2.
Class: guess, recorded with its absence note (`research/homesteads/250`; the one unread on-topic paper is on the
GM's download list). Cost: one segment test per part against a course of about fifty points, per configuration
already being judged; no index is owed.

### D11 - The copse stands within reach of what it is named for (FR-014)

`village_grove` takes `near=(points, reach)`: the dooryard copse within 90 ft of a farmhouse (`m:copse-house-reach`)
(`COPSE_HOUSE_REACH_FT`), the against-the-belt copse within 60 ft of a belt crown (`COPSE_BELT_REACH_FT`); every
clump, the re-seat nudge's included, is asked of one `Seats` index. The review found Kashikawa's copse spread to 393 crowns a median 167 ft from any house (R8). Class: accurate for the form ("in the gaps between the houses",
vegetation/020); the reach is a calibration of that phrase, recorded at the constants.

### D12 - The entrance board stands where every departure passes (FR-015)

Where a hamlet's connector hands over to its lanes (`kosatsuba_handover`), that junction is the entrance anchor: every
household's way out passes it and no other point. `departure_routes` walks each dwelling's way out through the drawn
lanes to the handover and on along the connector, and both placers (`place_kosatsuba`, `stage_notice`'s re-seat) keep
first the seats the fewest of those routes miss (`routes_missed`, 20 ft), then those within `KOSATSUBA_HANDOVER_BAND_FT`
(20 ft) of the nearest to the handover; the connector itself is offered as a way to post on. The census states, for an
entrance board, how many households' ways out pass it, not how many farmhouses stand within 250 ft. The review measured
1-2 households per map leaving by a lane that never came near the board; now 0 on all four entrance maps. A connector that
meets no other way keeps the first-arrival walk. A defect in an existing rule (constitution XIV).

### D13 - A brook never doubles back (FR-017)

`unfold(course, BROOK_MAX_TURN_DEG)` in `water/brook.py` deletes a vertex that turns the course more than 100
degrees; Sawada's brook folded 123 degrees where its stations clamped at the frame. A drawing defect fixed; the
limit is a calibration (a stream's own meander turns well under it), recorded at the constant.

### D14 - The belt keeps its depth, and its pop-up names a direction, not two sides (FR-016)

The pool test measures the belt's depth along the wind in 40 ft bins across it and holds every bin that no way, no
brook and no page edge cuts to the record's 30 ft minimum (`research/vegetation/020`: shallower "reads as a row of
blobs"). The windbreak pop-up says the belt stands "toward the northwest" rather than "on the north and west",
because Kuwabata's belt is a west strip; the class text says "on the windward one or two sides".

### D15 - The field path reaches the field across the brook (FR-012)

Three defects kept a spur from the rice once crossings were honest: its origin was pushed past the furthest house onto
the brook's far bank (`_cluster_edge_toward` now stops short of a stream it would cross); it was scored against the whole
brook, so a crossing at a ford counted as a violation (scored against the brook gapped at the fords); and the stub trim
read its field end as a dead end (`trim_lane_stubs` now leaves the spur, like the connector, to the sweeps that record a
drop), while the dangling-ends sweep counted only the paddy, not the dry hem, as the field. Inashiro, Kashikawa and
Mizuguchi each get their one way to the rice.

### D16 - Three misuses of `seg_intersect` fixed (constitution XIV)

`seg_intersect` answers for the LINES and is documented "call only when they cross". `ford_crossing`, `path_violations`
(a pre-existing brook term and the twice-bridged count) and the first `square_crossings` used it as a crossing test, so
every non-parallel segment "crossed": every spur detoured to a ford, and every connector bearing scored a brook violation
per segment. Each now tests `segments_cross` first. The connector bearings the scorer chooses changed with it, and the
notes' district directions were re-read from the drawn tracks.

### D17 - What the reviews found beside the crossings

- The brook turns off the frame where the frame box would pin it (`brook_skirt`), after half its stations: Sawada ran
  457 ft level along the top margin (the GM's 2026-08-26 ruling); now 66 ft, held by a pool test that fires on the old
  manifest.
- A shape other than round is declared only past round's aspect ceiling: Inashiro's 1.97 was declared a crescent and
  reads as a round cloud; it is recorded unhonored.
- The scrub's settlement keep-out is the hull of the houses and the farmsteads' parts grown by 44 ft, not the bbox of the
  house centers (Sawada's rectangular clearing; Kuwabata's fringe privy in the scrub).
- A board's caption is seated on the page when any seat allows (Kashikawa's was clipped past the left edge).
- `generate` finishes every attempt into a stage beside the map and promotes only the kept one, so a concurrent reader
  never sees a rejected roll (the gate's census read Sawada's first attempt).

## Phases

1. Engine: D1, D2, D3 with their unit tests (plan, cluster, surface); the amendment's D9-D14 with theirs.
2. Measurement: R1-R6 (trial, seed searches, cohort both ways, the shipped maps, the knob values).
3. Pool: D4, the five re-rolls, the pool test, R4.
4. Page: D5 with its tests.
5. Record and docs: D6; `quote-check` and `record-format` on the entry; `entry-drift` on the windbreak class.
6. Acceptance: `make done`, `settlement-review` one agent per map, ledger rows; the 48-seed cohort against R3's baseline.

## Complexity Tracking

None.
