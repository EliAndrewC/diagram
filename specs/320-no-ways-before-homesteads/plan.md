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

**D2 - The track out first, then the households' ways (FR-003).** `lay_the_ways` moves from the end of `stage_homesteads` to
`stage_track`, after the connector is laid: the connector's legs (from its start, within the gap raster's window) become the
tree the flood starts from and the ways join (`AccessTree.add`). The seating's reservations split: the wood seats stay
reserved at the end of the homesteads stage; the corridors are reserved when the ways are laid (`reserve_the_seating`'s
corridor half, called from the gap pass's caller). `tree.hosts` reads "on the connector" where it read "on the strip".

**D3 - The field path laid by the web (FR-003, FR-004).** With no field's corridor, the web's own field path (`settle.
settle_field`, `corridors.field_runs`) is what reaches the field on a brook map - as it did before feature 287 W03 reserved it.
The cohort measures whether any map's field goes unreached (`law.field_unreached`); were one to, the fix is in the web's
search, never a reservation before the houses.

**D4 - The strip's branches deleted.** `access.start_tree` (its corridor), `stages.reserve_field_corridor`, and every branch
reading `access_exit`: `gateway.track_from_the_strip_end`, `cluster_edge`'s strip gateway and `gate_on_the_strip`'s strip walk,
`track.on_the_strip`, `track.folds_on_the_strip`, `track._connector_through`'s strip fallback, `web`'s keep-on-the-strip skip,
`joints`' strip exception, `tree.strip_run` / `_strip` / `_along` / `_at`, `reserve_the_seating`'s strip, and
`tools/placement_stages`' strip. Each fallback they guarded (the row and dispersed forms' path) becomes the only path.

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
