# Tasks: feature 144 - the hamlet coverage floor, and the sixteen-second roll

Every task is `research: rendering` (nothing physical is decided here).

- [x] T01 gm-request.md verbatim; spec; spec-fidelity round 1 (4 changes) and round 2 (FAITHFUL) - `research: rendering`
- [x] T02 perf bookend `144-start` before any engine change (128.2 s total; seeds 4/25/39/47 = 17.6 / 51.0 / 19.9 / 39.7 s) - `research: rendering`
- [x] T03 `RingIndex` (`_geom/indexes.py`) + exactness test; `commons` and `marsh` scatters use it - `research: rendering`
- [x] T04 `fit_field`: `_predict_k` power-law step, bracket kept; unit test of every branch - `research: rendering`
- [ ] T05 `boxed_hit`'s crop-margin `edge_dist` over whole paddy rings - index it the same way; re-profile hinterland - `research: rendering`
- [ ] T06 the remaining hinterland cost after T05: profile, hoist or index what is per-candidate and static - `research: rendering`
- [ ] T07 the field carve's own per-candidate loops (`_quad_in_supply`'s 3 px edge walk, `close_seams`' shapely calls): measure, then index or hoist what pays - `research: rendering`
- [ ] T08 the other slow stages on the cohort's worst seeds (25: 51 s, 47: 40 s): profile the top stage of each and apply the same shape - `research: rendering`
- [ ] T10 the hamlet floor: derive the module set from the roll cache records, refuse without them; a phase of `test-full` after the two existing reports; the settlement ratchet stays - `research: rendering`
- [ ] T11 guard test: the floor fires on a module in the set, stays quiet on one outside - `research: rendering`
- [ ] T12 first measurement of the floor at FULL; every hamlet-path module under 100% brought up BY TESTS; any code only a non-hamlet tier reaches listed for the GM - `research: rendering`
- [ ] T20 `make durations` before/after: the settlement-geometry tests over the quick cutoff, each made faster or carrying a written reason - `research: rendering`
- [ ] T21 unlocked `make done` green; `make done FULL=1` green with the floor; corpus fires as before - `research: rendering`
- [ ] T22 perf bookend `144-end`, `make perf-report AGAINST=144-start`; research.md R1-R4 (the billions, the two fixes, the floor's definition, the numbers) - `research: rendering`
- [ ] T23 settlement-review of the reference (maps moved); findings fixed - `research: rendering`
- [ ] T24 doctrine: `dev/performance.md` (the index shape, again), `tests/CLAUDE.md` / settlement CLAUDE.md coverage paragraph (the derived floor) - `research: rendering`
- [ ] T99 the GM accepts - verbatim, after the explanation of what changed and what remains (the 8 s / 40% targets: met or reported) - `research: rendering`
