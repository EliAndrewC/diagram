# Tasks: feature 145 - the hamlet coverage floor, and the sixteen-second roll

Every task is `research: rendering` (nothing physical is decided here).

- [x] T01 gm-request.md verbatim; spec; spec-fidelity round 1 (4 changes) and round 2 (FAITHFUL) - `research: rendering`
- [x] T02 perf bookend `144-start` before any engine change (128.2 s total; seeds 4/25/39/47 = 17.6 / 51.0 / 19.9 / 39.7 s) - `research: rendering`
- [x] T03 `RingIndex` (`_geom/indexes.py`) + exactness test; `commons` and `marsh` scatters use it - `research: rendering`
- [x] T04 `fit_field`: `_predict_k` power-law step, bracket kept; unit test of every branch - `research: rendering`
- [x] T05 `boxed_hit`'s crop-margin `edge_dist` over whole paddy rings - index it the same way; re-profile hinterland - `research: rendering`
- [x] T06 the remaining hinterland cost after T05: profile, hoist or index what is per-candidate and static - `research: rendering`
- [x] T07 the field carve's own per-candidate loops: measured (seed 47: close_seams 56% of a carve, `_quad_in_supply` 19%); the win taken was fewer CARVES (the saturation probe, 39 -> 8) - the carve's internals are left with the measurement recorded in research R1/R2 - `research: rendering`
- [x] T08 the other slow stages on the cohort's worst seeds (25: 51 s, 47: 40 s): profile the top stage of each and apply the same shape - `research: rendering`
- [x] T10 the hamlet floor: derive the module set from the roll cache records, refuse without them; a phase of `test-full` after the two existing reports; the settlement ratchet stays - `research: rendering`
- [x] T11 guard test: the floor fires on a module in the set, stays quiet on one outside - `research: rendering`
- [x] T13 the GM's ruling on the other-tier residue: MOVE it (2026-08-28) - eight moves, the scale-derived segment skip, imports are not execution; path 99 -> 89 modules - `research: rendering`
- [x] T12 the floor measured, the other-tier code MOVED on the GM's ruling, and the hamlet residue described (research R3b/R3c/R3e): the path is 89 modules at **97.68%**, 373 lines - `research: rendering`
- [x] T09 the four placer defects the moved maps exposed (research R2b): connector wet-band offset, belt crown keep-out, unjog knee, footpath standing place/junction off water - `research: rendering`
- [x] T20 `make durations` before/after: the settlement-geometry tests over the quick cutoff, each made faster or carrying a written reason - `research: rendering`
- [x] T21 `make test-full` GREEN on every test (2,300+); all three coverage floors now report together; the hamlet floor is red at 97.68% with its residue classified for the GM; the global floor's tooling misses are pre-existing (R3d) - `research: rendering`
- [x] T22 perf bookend `144-end`, `make perf-report AGAINST=144-start`; research.md R1-R4 (the billions, the two fixes, the floor's definition, the numbers) - `research: rendering`
- [x] T23 settlement-review of the reference (maps moved); findings fixed - `research: rendering`
- [x] T24 doctrine: `dev/performance.md` (the index shape, again), `tests/CLAUDE.md` / settlement CLAUDE.md coverage paragraph (the derived floor) - `research: rendering`
- [x] T14 MOVED to feature 146 in full (the GM 2026-08-28: *"go ahead and make a single feature for all three of them"*), the floor's red state included as tasks of that feature
- [x] T99 **the GM accepts**, 2026-08-28, verbatim: *"Sounds great. I accept. So please merge your work back into the main checkout. Then open a separate feature for the residue in three named classes. Instead of having the biggest one as its own feature, go ahead and make a single feature for all three of them. After your existing work is merged into the main checkout, then please begin that feature and take it to completion and then merge it in as well without needing any acceptance from me. I think I'm still a little bit unclear on whether the floor being red on that three hundred and seventy three line residue. is captured by this new feature. or not. If it is not, then please include that as separate tasks within the same feature so that by the time your next round of work makes its way back into main, then the floor will no longer be red. Please proceed with that. Thank you."* Accepted state: the cohort 126.7 -> 49.2 s, the hamlet floor 89 modules at 97.68%, `make done` green (2,293 tests, 53.8 s). The residue is feature 146, whose closing task is a GREEN floor.

Numbering: this feature was claimed as 144 on 2026-08-28 and renumbered to 145 the same day when a peer
session's `specs/144-road-width-thirty` landed on main first (the clone could not push its claim while it
carried uncommitted engine work). The perf bookend taken BEFORE any engine change keeps its recorded
label `144-start` - an append-only record is not renamed; `make perf-report AGAINST=144-start` is the
comparison, and the closing bookend is `145-end`.
