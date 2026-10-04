# Implementation Plan: No ways placed before the homesteads

**Feature**: 320-no-ways-before-homesteads | **Spec**: spec.md | **Request**: request.md

## Summary

Remove the exit strip and the field's corridor from a nucleated hamlet's seating (FR-001); seat the houses with only
feature 318's lane's room between neighbors keeping a way possible; lay the track out once the houses stand, then each
household's way in the gaps, joined to the track out (FR-003); leave the field path to the web (FR-004). Every branch that
existed only for the strip is deleted.

## Performance bookends (constitution VI)

`make perf LABEL=320-start` on main (264a24ca5, the 318 landing, taken 2026-10-04) and `LABEL=320-end` at the last commit;
`make perf-report AGAINST=320-start`. FR-005: the two removals are measured together; an increase owes the records its
band asks, and were the reservations faster the measurement goes to the GM.

## Decisions

**D1 - Seating with nothing reserved (FR-001, FR-002).** `stages._seat_households` on the nucleated form: no `start_tree`
corridor, no `access_exit`, no `reserve_field_corridor`. The seating still asks `access.exit_bearing` whether the margin has a
lawful bearing out (a margin with none seats no one, as now) - a test of ground, nothing recorded or reserved. An empty
`AccessTree` (its half-width, no legs) stands for the seating's bookkeeping (a passage's walk barred, a tight seat's distance
to a way - none while seating). `SeatRegion`'s reachable ground (`_reached`, read by `opens`) is flooded from an ANCHOR: the
open ground past the seat band along that bearing (from the band's bound out to where the strip ended) - ground the region
keeps privately, never a corridor, never on the manifest. A household whose dooryard opens only onto ground the anchor's
flood does not reach (beyond water, walled in) is not open (FR-002; the over-count 318 measured from the window's edge,
cohort seed 13, is why the anchor is on the way-out side only).

**D2 - The track out first, then the households' ways (FR-003, FR-008).** Once the last house stands, inside
`stage_homesteads` and before any farmstead is drawn (the overlap registry refuses a lane on a drawn yard), the track out's
whole course is chosen ONCE by the track's own search (`track.choose_track_out`, lifted from `stage_track`: the cluster
gateway, `gateway_track` / `connector_track`, `connector_through`), its fabric the homesteads as seated (`seated_fabric`: each
household's house, yard, beds, well, sheds and fixtures from its seated geometry) and the wood seats. It is recorded
(`way_out_track`); its stretch within the gap raster's window is the tree the flood starts from and the ways join; the wood
seats are reserved after the parts are drawn. `stage_track` draws the recorded track and chooses nothing; a map with no
recorded track (the row and dispersed forms) chooses it there as before. No gate or first leg is decided apart from it.

**D3 - The field path laid by the web (FR-003, FR-004).** With no field's corridor, the web's own field path (`settle.
settle_field`, `corridors.field_runs`) is what reaches the field on a brook map - as it did before feature 287 W03 reserved it.
The cohort measures whether any map's field goes unreached (`law.field_unreached`); were one to, the fix is in the web's
search, never a reservation before the houses.

**D4 - The strip's branches deleted.** `access.start_tree` (its corridor), `stages.reserve_field_corridor`, and every branch
reading `access_exit`: `gateway.track_from_the_strip_end`, `cluster_edge`'s strip gateway and `gate_on_the_strip`'s strip walk,
`track.on_the_strip`, `track.folds_on_the_strip`, `track._connector_through`'s strip fallback, `web`'s keep-on-the-strip skip,
`joints`' strip exception, `tree.strip_run` / `_strip` / `_along` / `_at`, `reserve_the_seating`'s strip, and
`tools/placement_stages`' strip. Each fallback they guarded (the row and dispersed forms' path) becomes the only path.

**D6 - The marsh ends (FR-007).** A fourth, short component in the marsh outline's wave (`WAVE_SHORT_FT`, weighted as
`WAVE_WEIGHTS` gives it); observed 2026-10-04 (exact 2 ft `straightest_run` over three laid strips and a short-ended strip,
40 seeds each, scratchpad `marshvar2.py`): the longest straight stretch fell from 160 ft to 85 ft, under the bar
`test_no_stretch_of_a_shaped_outline_runs_straight_for_the_share_a_visible_edge_may_not_pass` holds.

**D5 - The record (FR-006).** Page 0081's drawing page already says houses first, ways after; the claims that cited the strip
or the field's corridor are rewritten with the code; the claims and record checks owed are run through feature 318's scoped
re-check (`make claims-triage`).

## Verification

`make quick` while iterating; the reference spec and the 10/20/40-household bookend seeds rolled to check every household
reached; `make cohort N=24` against main's 30/30; `make done`; the bookends. Occasions: village lane (placement and the order
of laying change) - glyph-check on Inashiro.

## Constitution Check

Research-driven (XII): page 0081 (houses first, ways worn after). No new figure. Fix-where-found (XIV) applies to what the
removal exposes.
