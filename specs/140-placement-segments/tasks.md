# Tasks: Placement Measures Against a Few Segments (feature 140)

- [x] T01 measure what placement tests against (feature 138's census: one 2,880-vertex dike band; the field envelope; crop plots bbox-gated) and how many chords the real outlines need at 3 / 6 / 10 px
- [x] T02 `simplify_ring`, `ring_offset` (mitered), `keepout_ring` (measured reach), `facing_chains` + `chain_violated` + `chain_distance` in `_geom/primitives.py`; `convex_hull` moved there; tests: containment on random smooth outlines and a drawn dike, the facing chains never looser than the outline on the house side, open and few
- [x] T03 the dike's keep-out = the crest's chords pushed out to the band's reach (`dikes[].keepout`, `keepout_chords`); `structures_clear_of_dike` measures it
- [x] T04 placement measures the field chains (`Settlement.field_face` from `stage_seat`; `_field_chains`, `_field_blocks_point/_rect`, `_field_within`; `_in_blocked`, `_wall_on_the_bund`, the near-field test); a simplified ring where no seat is planned
- [x] T05 `finish()` records `fields[].keepout_chains` / `keepout`; `houses_clear_of_paddies` measures the chains
- [x] T06 the tolerance chosen by measurement on the reference (3 px passes the gate; 4, 6, 8 break the lane web - research R3)
- [x] T07 the reference and the four live pool hamlets regenerated on the finished engine, gated, rendered; `settlement-review` on each (Sawada / Mizuguchi / Kashikawa ACCEPTABLE WITH NOTES, Inashiro NOT ACCEPTABLE on the notice board's drift - research R5/R6); verdicts and measured set-backs recorded in each map's notes
- [x] T08 `make done` green - 3,898 passed, 1 m 45 s cold on the merged engine (the board scorer weighted; two legacy fixtures widened for the 3 px push-out); research R4 holds the timings (polder `stage_homesteads` 9.2 -> 1.9 s; the reference clean at 8-9 chords); research R4 (timings: polder `stage_homesteads` ~9 -> ~2 s, the reference field tests, the two checks); the stop-work ritual
- [x] T09 feature 141 claimed (`specs/141-checks-and-corpus-audit/gm-request.md`, the GM's words verbatim; the spec waits on the session's feedback and the GM's go)
