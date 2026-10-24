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
