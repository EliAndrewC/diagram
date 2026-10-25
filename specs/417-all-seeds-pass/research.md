# Feature 417 - research

## R1 - what a fresh block costs, and what it finds (measured 2026-10-24)

Method: `make cohort N=100 SEED=3000001 FRESH=0 JOBS=12` at main `b3f6738c2` (no engine diff), under `/usr/bin/time -v`;
seeds 3000001-3000100 were never rolled before. Host: 22 CPUs, load 1.3 at the start, 15 GB with the containers' 10 GB cap.

| block | wall | per seed | peak RSS of the make | failed |
|---|---|---|---|---|
| 100 fresh + 6 pinned | 4 min 41 s | 2.8 s | 136 MB (the workers are children) | 9 of 100 (9%) |

The nine: `lane_knots` (3000015, 3000054, 3000066), `WebRefused` (3000047, 3000053), `BrookRefused` (3000019),
`SiteRefused` (3000069), `groves_crossed_by_lanes` + `lane_knots` (3000078), `row_rules` (3000086). The same causes, in the
same order, as the spec's tally over 2,544 seeds (14%); the lower rate is within one block's spread (the logged 48-seed blocks
ran 6-21%).

**What it decides (D1).** A block of 500 is about 23 minutes at 12 workers; zero failures in 500 bounds the true rate under
0.6% at 95% (the rule of three, 3/500). A block of 1,000 is about 47 minutes and bounds it under 0.3%. 500 is SC-001's N;
1,000 is the closing measure.

## R2 - the inventory (FR-002)

Written by T02: every repair pass, every rule asked only of a finished map, every rule coded twice, and every finished-map
check the generator runs mid-map, with where it is and which point of the rule it breaks. Seeded from the session's survey of
2026-10-24 (to be completed, not trusted):

- the lane web's settle: `hamletgen/ways/settle/stage.py:52` `STEPS` - sixteen repair functions looped to a fixpoint, then
  `last_resort` (drops ordinary lanes) and `WebRefused`;
- the passes that repair a laid web: `ways/sweeps.py`, `tails.py`, `joints.py`, `touch.py`, `smooth.py`, `squaring.py`,
  `weld.py`, `knots.py` (each named in `ways/CLAUDE.md` as a pass after the web is laid);
- rules asked only of the finished map: `homesteads/row_rules.py` (`row_rules`, `water_rules`, `bamboo_mismatch`),
  `settlement/homestead_parts/grove_rules.py` (`groves_crossed_by_lanes` and four more), `cohort_audit`'s
  `farmstead_across_brook`;
- about fifteen more functions named like repairs in `homesteads/`, `homestead_parts/`, `waterfields/`, `labels/`, unread.
