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
- [ ] T12 first measurement of the floor at FULL (research R3b, `floor-first.txt`): 932 lines; ~700 are other-tier code inside hamlet-path modules - LISTED FOR THE GM with three options (R3b, recommendation: move them out); ~150 hamlet lines remain untested after the branch tests and the eight-seed cohort (hamletgen/ways.py 37, homesteads 12, small geometry) - OPEN, the GM's call on how far this feature carries them - `research: rendering`
- [x] T09 the four placer defects the moved maps exposed (research R2b): connector wet-band offset, belt crown keep-out, unjog knee, footpath standing place/junction off water - `research: rendering`
- [x] T20 `make durations` before/after: the settlement-geometry tests over the quick cutoff, each made faster or carrying a written reason - `research: rendering`
- [ ] T21 unlocked `make done` GREEN (2,281 tests, 2026-08-28); `make test-full`: every test green (2,294), the hamlet floor RED by design until T12's decision; the global floor's `ci/`/`switches`/tools misses are pre-existing (baseline FULL at 514e6cc0, research R2c) - `research: rendering`
- [x] T22 perf bookend `144-end`, `make perf-report AGAINST=144-start`; research.md R1-R4 (the billions, the two fixes, the floor's definition, the numbers) - `research: rendering`
- [x] T23 settlement-review of the reference (maps moved); findings fixed - `research: rendering`
- [x] T24 doctrine: `dev/performance.md` (the index shape, again), `tests/CLAUDE.md` / settlement CLAUDE.md coverage paragraph (the derived floor) - `research: rendering`
- [ ] T99 the GM accepts - verbatim, after the explanation of what changed and what remains (the 8 s / 40% targets: met or reported) - `research: rendering`

Numbering: this feature was claimed as 144 on 2026-08-28 and renumbered to 145 the same day when a peer
session's `specs/144-road-width-thirty` landed on main first (the clone could not push its claim while it
carried uncommitted engine work). The perf bookend taken BEFORE any engine change keeps its recorded
label `144-start` - an append-only record is not renamed; `make perf-report AGAINST=144-start` is the
comparison, and the closing bookend is `145-end`.
