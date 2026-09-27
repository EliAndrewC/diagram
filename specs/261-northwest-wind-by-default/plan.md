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
Mizuguchi each get their one way to the field.

### D16 - Three misuses of `seg_intersect` fixed (constitution XIV)

`seg_intersect` answers for the LINES and is documented "call only when they cross". `ford_crossing`, `path_violations`
(a pre-existing brook term and the twice-bridged count) and the first `square_crossings` used it as a crossing test, so
every non-parallel segment "crossed": every spur detoured to a ford, and every connector bearing scored a brook violation
per segment. Each now tests `segments_cross` first. The connector bearings the scorer chooses changed with it, and the
notes' district directions were re-read from the drawn tracks.

### D17 - What the reviews found beside the crossings

Measured before and after in research R9.

- The brook turns off the frame where the frame box would pin it (`brook_skirt`), after half its stations: Sawada ran
  457 ft level along the top margin (`m:sawada-brook-ruled`; the GM's 2026-08-26 ruling); now 66 ft, held by a pool test that fires on the old
  manifest.
- A shape other than round is declared only past round's aspect ceiling: Inashiro's 1.97 was declared a crescent and
  reads as a round cloud; it is recorded unhonored.
- The scrub's settlement keep-out is the hull of the houses and the farmsteads' parts grown by 44 ft, not the bbox of the
  house centers (Sawada's rectangular clearing; Kuwabata's fringe privy in the scrub).
- A board's caption is seated on the page when any seat allows (Kashikawa's was clipped past the left edge).
- `generate` finishes every attempt into a stage beside the map and promotes only the kept one, so a concurrent reader
  never sees a rejected roll (the gate's census read Sawada's first attempt).
- No solid part of a farmstead - the house included - stands on a stream (`_rect_on_stream` in `_parts_fit`), and the entrance
  board prefers a seat in the open among those every departure passes (Mizuguchi: a house wall on the brook's course, a
  board inside a crown).
- A connector that runs through, both ends off the sheet, hands over where a lane's end meets it (`kosatsuba_handover`).
- The web's dangling-ends sweep runs once more after `straighten_joints`: an end that reached the lane it was then joined
  to was left reaching only its own lane (Mizuguchi).

### D18 - The ways and the caption, as the next reviews drew them

Measured before and after in research R10.

- A lane that runs back along another for 30 ft or more within 14 ft is cut where the doubling starts (`along_tail`,
  `_sweep_doubled_tails`, before the last dangling-ends sweep); a lane record left with fewer than two points is dropped.
  Kuwabata's join lane ran 122 ft back along its connector; three maps carried empty straggler records.
- An orphan join is routed with the brook as an obstacle and refuses a link that crosses it an even number of times,
  keeping one only as a last resort (Mizuguchi's web crossed and crossed straight back).
- The board is sited where its caption fits, as THE ONE PLACER (feature 266, merged from main) answers it: the siter and
  the frame stage's re-seat hand each candidate board to `place` at the angle the board will be drawn at, and a caption
  fits when the placer seats it at the preferred ring with nothing under it and no leader (`board_caption_level`); one
  clear of every crown ranks first, and the manifest records the level the chosen seat had
  (`kosatsuba_caption_level`). Before the merge this feature built the same question against the old caption search
  (`caption_room`, a drawn-quad lane test, a pull that keeps the board nearest, an upright fallback removed for the GM's
  2026-08-27 ruling that the caption stands at the board's angle); feature 266 replaced that search, and those pieces
  went with it. What they fixed stands as pool tests: no caption on a roof or a lane, at its board's angle, nearest its
  board, and clear of the canopy unless the record says no seat offered it.
- Of two tails doubled into one junction the narrower is cut, never the wider, and a tail that crossed the way before it
  came alongside ends at that crossing: the cut drew Sawada a hook and necked its 6 ft route out to a 3 ft path.
- A household whose way out crosses the brook and back is served again by the straggler pass to a way on its own bank
  that reaches the connector dry-shod (`_link_home_bank`, before the passes that read the finished joints). Mizuguchi's
  pocket between the brook and the head-race reached its own bank's lane over two planks.
- A lane record whose points are all one point is dropped with the husks.
- A free end's short stub past a kink is taken off (`trim_free_stub`): on Kuwabata's fourth roll, after the merge with
  main, the ring lane threaded a threshing yard and a garden to a door and ended 19 ft past a jog - two turns of 84 and
  72 degrees inside 40 ft, which the cohort's lane-rules test refuses; straightening the joints again, the router's
  `_unjog` and keeping channel crossings unsquared were each tried and none reached it (the jog was the web's own).
- A lane crossing any drawn channel is squared like a brook crossing (Mizuguchi's head-race plank lay 44 degrees off;
  research ways/030: a plank "crosses its ditch square").
- A roll that raises removes its own stage, and `.roll-*/` is ignored: two interrupted rolls left staging directories in
  Kuwabata's pool folder and a commit took them in.
- A caption whose halo would notch a tree crown is refused where a clear one exists: the siter ranks a board whose aligned
  caption clears the canopy above one that merely fits, and the placer's shaded test reads the drawn quad and halo
  (`quad_on_canopy`), not a disc round the caption's center (Kuwabata's caption stood in the windbreak).
- No third woodland parcel stands in a ruled row with two others: an in-row seat is stepped sideways where the ground
  allows and refused where it does not - the count is a target the scan meets only where there is ground (Inashiro keeps
  two). A preference that fell back to the row was tried first and kept the chain.
- No copse clump is based in the marsh (research/vegetation.html: woody cover "stands on the dry ground above it"). The
  keep-out is the copse's alone: applied to every grove it took Sawada's windward belt from 179 crowns to 104, and 20-34
  of the 68 refused crowns stood on ground drawn dry - the toe marsh's recorded outline runs under the settlement's
  cleared ground there. Recorded in `future-work/farming-communities.md` with the measurement and a sketch.
- A copse clump is near a house only on the house's own bank (`BankNear`): Kashikawa's copse had three clumps across the
  brook from every farmhouse, within the 90 ft reach only as the crow flies.
- A diagonal wind wraps the belt round two sides, so its seating window opens on both axes the wind has a share of (on a
  northwest wind's tie only the x axis opened, and Inashiro's north arm stood 28 ft deep behind its northernmost house);
  each arm of the belt has its own inner face (`windbreak_faces`), and the frame holds every belt clump within 100 ft of
  a farmhouse on the page - that house's shelter - since the face is the belt's TYPICAL front.
- A seat whose windbreak band would fall off the canvas scores down (`belt_off_canvas`), as the brook and the dry hem do.
- A belt stands beyond a lane that runs along its band (`past_the_lanes`), unless that would put it in the marsh: Kuwabata's
  ring lane ran lengthwise down the belt's middle and halved its drawn depth (median 67 ft against main's 104).
- A wind-facing seat whose belt band falls more than a fifth off the canvas (`BELT_ROOM_MAX_OFF`, three of the band's
  fifteen sample points) is only a fallback, below every wind-facing seat with room and above the off-wind ones: scored
  alone, Mizuguchi's seat 34-47 ft from the west edge still won, because every other wind-facing margin had the brook
  across its band. Its houses now stand north of the brook with the belt west of them on open ground.
- A front-row seat is pushed across a brook that runs between it and its field (`water_push`, beside `_ground_push`'s
  outline push), and a seat the water moved tries a quarter pitch either way along the row when it collides: with the
  houses seated against the wind down Inashiro's brook flank, every front seat lay in the water's corridor, the cloud
  seated the rest, and the rolled crescent drew 1.62:1 against main's 4.07. Sampling the whole row at three quarters of
  a pitch honored it and moved Kuwabata, which has no brook, enough to split its lane web in two (one join's route ran
  50 ft past an unjoined crossing); the extra tries go only where the water moved the seat. Cutting that overrun back,
  splitting lanes at loose crossings and a last orphan join were each tried first and each moved other maps' lanes.
- A household re-served on its own bank (`_link_home_bank`) loses the lane over the brook it no longer needs, where every
  house that lane serves is served by the rest (`excursion_lanes`): Kashikawa's new way stood 39 ft from the door, as
  did the old lane over the plank, and the walker took the old one.
- The notice board may stand within 26 ft of the top edge, as of the bottom (`_fits(top=)`): Mizuguchi's connector
  handed over to its lanes at y 82, inside the 88 ft a house keeps for the title band, and the board went 202 ft away
  where two households' ways out missed it. The title is placed at finish, clear of what is drawn.
- The scrub keeps off each farmstead's own grown outline and the ground between two within 140 ft
  (`farmstead_keepouts`), not the whole cluster's hull: Kuwabata's copse keeps within 90 ft of a house while the hull
  reached further, and a 240 x 270 ft wedge inside it came out bare with a straight edge.
- The brook's walk swings across its whole band at every station (`BROOK_WANDER_STEP` 4 -> 10, the band unchanged at
  10 ft, so the frame and the skirt it is sized to are untouched), and an exit leg still on the page bends at its middle
  (`exit_bend`): Sawada's middle reach ran 872 ft within 3.1 ft of a line, 70% of its course on the page.
- A household's own dry plot is laid against its homestead (`stage_homestead_fields`, after the ways): the levee model -
  the old settlement and its dry fields on the same raised ground, the paddy behind (research/fields.html, the catena;
  `shizen-teibo-jawiki`, `kohai-shicchi-jawiki`) - beside the canal hem, which stays as the second position. The toe
  band and the cover's cultivated extent leave these plots out, so neither moves after the seat and the router were
  handed it (a homestead plot moved Sawada's toe marsh over its handover). The plot's size is a GUESS.
- A woodland parcel prefers a seat not across the field from the cluster (a preference, like the cross-slope one).
  Inashiro has none: its woods must stand 80% inside the predicted frame, which begins 100 ft west of the houses, and
  every seat on the houses' side at every size falls between their keep-out and the field's set-back.
- The segment leaving the brook's tap run is nudged off a screen axis like every other (`_off_the_axes(hold=1)`, where
  the tap run and that segment were both exempt), and the approach's legs are too: Sawada's leaving segment drew exactly
  vertical below its tap, Inashiro's approach a leg 1.2 degrees off vertical (on main as well).
- A lane's elbow inside the brook's half-width is dropped before its crossing is squared (`square_crossings`): Kashikawa's
  lane bent 3 ft inside the water, its crossing segment was too short to square, and its plank lay 44 degrees off.
- The scatter frame's prediction takes in the title pocket's band below the content when every seat above it is off the
  canvas (`TITLE_POCKET_RISE`), and the confluence the frame reserves: cohort seed 45's pocket went below, past the
  prediction.
- A review acceptance carries the round it answered and counts only there, and a NOT-REVIEWABLE verdict keeps the verdict
  it was written over (`scripts/_review_prereq.py`): four reviews found this round's findings cleared by earlier rounds'
  acceptances of other findings with the same number, and a NOT-REVIEWABLE record had wiped them.
- The entrance is the last point where a way joins the approach, walked in from the map's edge (`outermost_join`), and a
  household's way out runs from its door to the connector's outer end (`departure_routes`): routed to the handover first
  and then out, a lane that met Inashiro's track 190 ft below it was walked up and back, and every route passed a board
  at the handover by construction. The board's candidate ways are those within reach of the handover by segment, not
  vertex, since the handover now lies mid-leg.
- A bamboo stand keeps off the water at its half-width and 3 ft (Mizuguchi's thicket stood on the brook), and a lane that
  runs on past the connector to a loose end is cut where it met it (`cut_past_connector`; Mizuguchi's leg ran 52 ft on
  and off the sheet), never where the tail is some house's only way.
- The connector cut leaves a lane whose other end already stands on the connector, and a kept fragment does not vouch for
  the houses its own cut would strand: it had cut an Inashiro farmstead's only lane from its house end, leaving a 4 ft
  stub the entrance was then sited on. A lane end is judged against every way but the one its own far end stands on
  (`_trim_to_service`): a Mizuguchi lane left the connector, ran 61 ft past its house and counted as arriving at the
  connector it had left.
- A belt crown seated in a toe marsh is drawn as alder (the `alder` mix and class): the record's woody stage at a reed
  edge is alder or willow, never pine (research/vegetation.html, the marsh margin). Sawada's windward belt stands on
  its toe's reed edge (70 of 201 clumps in the marsh); holding the belt off the reeds took the windward belt away and
  failed its depth test, and a belt that stops at the marsh does the same. The carr along the rest of the toe - the
  second form the record names for it - is not built.

### D19 - The board on the approach, grain by archetype, and the plot's corner (round 6fefdcdf)

- An `entrance` board at a handover stands on the approach itself where a seat there passes every departure: among the
  seats every way out passes, the connector's win, in the siter and the frame stage's re-seat alike. A board is squared
  to the way it stands on, and Inashiro's outermost join is a one-farmstead web straggler whose verge won, so the board
  stood 87.7 degrees off the track every household walks (research/urban-features.html: broadside to the one way out).
- The homestead field is a grain plot, so an archetype that buys its grain in lays none (`GRAIN_BOUGHT_IN`: the
  mulberry dike-fishpond, which 「abandoned rice to plant mulberry」 - research/archetypes.html; Kuwabata's GM-confirmed
  economy). Kuwabata had drawn six barley, millet and buckwheat plots.
- A farmstead fixture is refused a seat whose line to its house crosses a lane (`across_a_lane`, the brook's line test):
  a shrine stands in a corner of the house plot and a coop in the yard (research/homesteads.html), and Mizuguchi drew a
  coop, a woodpile and its one shrine beyond the lane behind their house. The rule's cost was measured, not assumed:
  against the commit before it, seven more fixtures went unseated on four maps (Inashiro a heap; Kashikawa two coops and
  a bath; Sawada a second heap; Mizuguchi a coop and a woodpile - observed 2026-09-27: `meta.farm_fixtures_unseated` in each pool manifest at commit 6b6031073, against 6f75efe4a's one Sawada heap) and two maps lost their only shrine (observed 2026-09-27 on a roll with the lane rule and without the shrine pass, not committed: Kashikawa and Mizuguchi). The placement was
  fixed rather than the rule relaxed:
  - a fixture every recorded seat of which is refused is offered the ring round its own house's other walls
    (`yard_ring`: the back wall at three points, each flank at three heights, the front corners), at the same outward
    rungs the recorded seats get, before it counts as a miss. The recorded seats keep their order and win wherever they
    fit; the ring is a GUESS, labeled at the point of change (the record places each fixture at a wall, not at which
    one when that one is taken).
  - a shrine with no seat passes to the next house with room, and the miss is recorded only if none takes it. The
    record gives the shrine's COUNT (3-8% of homesteads, never exceeding the share, research/homesteads.html) and not
    its household; the engine chooses the household by a positional roll, and the pass re-rolls that choice to a house
    with room, keeping the count.
  - the ring is not refused by a homestead BUNDLE box: `_try_place_bundle` reserves a rectangle round each whole
    steading and registers its parts - house, yard, gardens - one by one besides, so the bundle is a packing
    reservation, not ground. Tested as a solid, a bundle offset by its gardens refused its own house's open flank and a
    neighbor's refused ground nothing stood on; Mizuguchi's farmstead at (1277, 257) seated no coop and no stack
    (spec-fidelity of round 6fefdcdf, probed seat by seat). The skip is the ring's only: taken for every seat, the
    fixtures took the flanks first and the persimmons after them lost their ground (observed 2026-09-27 on a trial roll with the skip on every seat, not committed: the manifests' `persimmons` counted, Inashiro 6 where it drew 12).
  - the persimmon, which alone recorded no miss, tries its six bearings a step (10 ft) further out and records one
    when none takes it. The pool had been dropping persimmons silently: with the step, Sawada draws 17 where it drew
    14, Mizuguchi 11 where 8, Kuwabata 13 where 12, with no miss on any map (observed 2026-09-27: `persimmons` counted with
    `git show <rev>:<map>.json` at 818ac79b0 and at b915f256a).
  Measured after all of it (`m:pool-r15-unseated`): no fixture of any kind unseated on any of the five maps, where the
  commit before the lane rule left Sawada one heap short.


### D20 - The belt keeps its depth across itself, and the brook turns on curves (round 97c20bc9)

- The belt's far face is the fringe grown by a DISC of the belt's depth (`far_face`, `BELT_DEPTH_FT` 110): a neighbor `d`
  across the wind counts by `depth * sqrt(1 - (d / depth)^2)` of its lead. The far face used to be the near face moved
  along the wind, which is the belt's depth only where the fringe lies square to it; where the fringe runs along the wind
  the band thinned to a sliver, and Kashikawa's westernmost steading's garden and sun lane emptied it - a hole in the
  windward face (settlement-review, round 97c20bc9; research/vegetation.html: a belt "reads as a wall of trees only at"
  80-120 ft of depth, and a windbreak with a hole funnels the wind). The band is now at least 84 ft across itself on
  every pool map where no page edge cuts it (`m:belt-r16-depth`). A square window (a neighbor's whole lead) was tried
  first and thickened belts for bumps of a few tens of feet (observed 2026-09-27 on a roll not committed: Sawada 559
  clumps, Inashiro 364, Kuwabata 232, Mizuguchi 304, against the disc's 539, 312, 191 and 252); the disc leaves a square
  or gently bumped fringe unchanged. Every belt grew, most where its fringe turns (observed 2026-09-27, the census
  blocks at commits 881679390 and 02aa89eae): Inashiro 241 to 312 clumps, Kashikawa 277 to 504, Kuwabata 125 to 191,
  Mizuguchi 237 to 252, Sawada 201 to 539.
- A brook turns on a curve: its corners are filleted at `BROOK_BEND_WIDTHS` (2.5) of its drawn width, the ratio the
  ditches are drawn at (research/water.html "Why does every ditch turn on a curve?"), and the tap the head race leaves
  from is held (`round_the_brooks`, `Settlement.round_stream`). Sawada drew corners of 27-47 degrees
  (`m:brook-r16-turn`). It is done LATE, at the start of the crossings stage, rounding the drawn course and its record in
  place. Rounding it where the brook is first drawn was tried and reverted (observed 2026-09-27 on rolls not committed):
  every way routed against the brook's corners moved, Mizuguchi's re-rolled web left its field path's head off the lanes
  and a way out crossing the brook twice, and the next re-roll would find another; the ways were right, and it is the
  drawing that was wrong. The planks are squared and decked against the rounded course.
- The pool test that keeps the brook off the screen axes judges runs of a wander stride (`BROOK_WANDER_STEP`, 10 ft) or
  more: a curve that turns through an axis has a short chord or two on it, and the GM's objection is to a course running
  along one.


### D21 - The copse at the belt's lee face, and the board's well distance where it is drawn (round 31ef113b)

- The against-the-belt copse anchors on the belt's LEE FACE (`lee_face`: in each 40 ft band across the wind, the crowns
  within a crown's 30 ft depth of the most leeward), so it stands in the belt's shelter on the houses' side, "tucked
  against the back grove" (`COPSE_SITINGS`). Anchored on every belt crown, and once D20 gave the belt its depth where it
  turns, 31 of Mizuguchi's 75 copse crowns stood beyond the belt's windward face (settlement-review, round 31ef113b); none
  does now (`m:mizuguchi-r17-copse`, 0 crowns). The band and depth are a map drawing convention, calibrated to a crown.
- `meta.kosatsuba_well_ft` is recorded for the board as drawn: the frame stage's re-seat records it too
  (`record_board_well`). Sawada's said 353.5 ft of a board 173.3 ft from its nearest well, the first seat's figure; every
  pool map's recorded figure is now its drawn one (`m:sawada-r17-well`, 173.3 ft).
- The drawn belt is measured as one piece in crowns, not in its outline (`m:kashikawa-r16-belt-pieces`, 1 piece): the
  depth record reads the polygon, and the review's hole was between crowns inside an unbroken outline.

## Phases

1. Engine: D1, D2, D3 with their unit tests (plan, cluster, surface); the amendment's D9-D17 with theirs.
2. Measurement: R1-R6 (trial, seed searches, cohort both ways, the shipped maps, the knob values).
3. Pool: D4, the five re-rolls, the pool test, R4.
4. Page: D5 with its tests.
5. Record and docs: D6; `quote-check` and `record-format` on the entry; `entry-drift` on the windbreak class.
6. Acceptance: `make done`, `settlement-review` one agent per map, ledger rows; the 48-seed cohort against R3's baseline.

## Complexity Tracking

None.
