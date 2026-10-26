# Research - feature 415

## R1 - feature 405 T26's landing, by phase

Observed 2026-10-24; method: the landing's log (`make land F=405 T=T26`, its fourth attempt) and its commit and run-record
times. The landing took 8.8 minutes, 14:18:21 to 14:27:10 UTC:
- the first pass of quick refusals: ~1 min, `cover-changed` 48 s of it;
- the gate's preflight (`make quick`, 754 unit tests): 34 s;
- static, format, typecheck and the reference step: ~30 s;
- the gate's test phase, 10,376 tests with coverage on and rolls real: 280 s;
- the landing cohort past the gate's end: 1.4 min;
- the ticks and the push: ~0.5 min.

Observed 2026-10-24; method: the landing's log, and the gate's planner (`incremental.contexts_touching`, `over_the_fraction`)
asked offline on the clone's baseline. The gate ran in FULL mode: "gate: FULL - the tooling changed (Makefile, pyproject,
lockfiles, scripts/)". T26's two engine files (`hamletgen/ways/tree.py`, `settlement/homestead_parts/fixture_seats.py`)
reached 143 of 11,890 baseline tests in 21 test modules.

Observed 2026-10-24; method: two `make durations FULL=1` runs on the same tree, and a count of `dev/run-log/2026-10/`. The
tree without coverage and with rolls served from cache ran in 157 s and 180 s. Of October's green gate runs, 286 were full
(median 194 s) and 49 incremental (median 42 s).

## R2 - what a gate run costs here (T04, FR-007)

Observed 2026-10-24; method: `make done` in the clone (`diagram-backlog`), one full and three incremental runs, each
incremental one a real gate over a real engine change - one executed statement added inside a function body of
`hamletgen/ways/tree.py`, then `settlement/core.py`, then `settlement/_geom/primitives.py` and `overlap/registry.py`, each
reverted after - plus `scripts/measure/gate_costs.py` (new) as a `scripts/` change in all three; the records' T01 fields read
by `make gate-costs`:
- full: 10,281 tests selected; the test phase (pytest) 197 s, the floors 10 s, the gate 223 s; load 5.68 at the start;
- incremental, 1 engine file and the `scripts/` readers: 1,492 selected; pytest 70 s, floors 10 s, the gate 93 s; load 5.05;
- incremental, 2 engine files: 1,965 selected; pytest 108 s, floors 11 s, the gate 132 s; load 7.65;
- incremental, 4 engine files: 2,657 selected; pytest 102 s, floors 9 s, the gate 125 s; load 4.9.

Observed 2026-10-24; method: `make gate-costs`, least squares over those four runs' pytest seconds on their selected counts.
The test phase costs about 67 s fixed plus 12.7 ms per selected test. The 1,965-test run, at the highest load, ran slower than
the 2,657-test one: a run's seconds move with the box's load as much as with its selection, so the per-test figure is rough.
Outside the test phase a gate pays about 25 s (preflight 11-18 s, static, format, typecheck and the reference step about 4-9
s). At the old cutoff, 60% of a 11,954-test baseline, an incremental test phase would cost about 67 + 0.6 x 11,954 x 12.7
ms = 158 s against the full run's 197 s; at 80%, about 188 s - so above about 80% running what is reached saves next to nothing.

Observed 2026-10-24; method: the same records, in order. The selection grows between full runs, as the baseline (the last
full run) predicts: 1,492, then 1,965, then 2,657 as the session's own probe edits accumulated (1, then 2, then 4 engine
files - staged, not observed across landings) - so each later landing would pay for every earlier change until a full run
resets it. That growth, not drift, is what the refresh (T05) must bound. These runs stand in for landings, the GM's approved
departure (request.md amendment 1); a landing runs the fixed cohort and the coverage check beside its gate, so its numbers
may shift under that load.

## R3 - a real engine landing after a tooling change, end to end (T06, SC-006)

Observed 2026-10-26 from the records of 2026-10-25; method: the landing's own log (`make land F=417 T=T04`, the session's
`landT04.log`, its start the call at 04:20:05Z and its end the file's last write at 04:25:12Z), the gate's run record
(`dev/run-log/2026-10/20261025T042434374185-1969079.json`) and main's commits. It is D9's landing: the first after T05 whose
own change did not move `gate_config` and which had `scripts/` changes since its baseline - its record reads
`plan_mode: incremental`, "1 engine file(s) and 9 test module(s) changed, 8 scripts/ file(s) (222 module(s) that read
scripts/)", the engine file `l7r/diagram/tools/cohort_audit.py`. It was the landing's third call; the two before it were
refused by the cheap checks (British spellings) in under a minute each, as T26's fourth attempt was the one R1 timed.

Observed 2026-10-25, method: the landing's log and run record, as above. The landing took **5.1 minutes** against R1's 8.8,
04:20:05 to 04:25:12 UTC:
- the cheap refusals and the gate's preflight (`make quick`): ~45 s, preflight 21 s of it;
- the gate's test phase, 2,023 tests selected and 1,330 tooling tests reused: pytest 151 s, the hook suites 51 s, the floors 12 s
  (the gate 224 s in all, against T26's 280 s test phase alone);
- the landing cohort ran beside the gate and was done when it was;
- the claims round, the push and the tick: ~37 s; the fresh block of 48 rolled after the push, off the landing's path.

Observed 2026-10-26, method: `make gate-costs` and each run record's `plan_reason`, 2026-10-25 to 2026-10-26 15:03Z: 39 of 45 gate runs still planned full. Their reasons: 11 a pool
manifest (`inashiro.json`), 7 a `CLAUDE.md` under `tests/`, 6 an import-time line, 5 the top-level or ci `conftest.py`, 5 a
hook suite under `tests/hooks/`, 3 no baseline, 2 the gate's configuration. Feature 430 T01-T02 (landed 2026-10-26 14:51Z)
answers the manifests, the docs and the deeper test-tree files, the hook suites among them (T08); the top-level `conftest.py`
and an import-time line still plan full by design. No landing has yet run under 430's planner without itself moving the gate's
configuration, so how often the gate now stays incremental is the next landings' to show (`make gate-costs`).
