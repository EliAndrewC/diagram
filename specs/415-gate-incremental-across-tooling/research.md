# Research - feature 415

## R1 - feature 405 T26's landing, by phase (observed 2026-10-24)

Method: the landing's log (`make land F=405 T=T26`, its fourth attempt), its commit and run-record times, and `make
durations FULL=1` on the same tree. The landing took 8.8 minutes, 14:18:21 to 14:27:10 UTC:

| step | time |
|---|---|
| the first pass of quick refusals (`cover-changed` 48 s of it) | ~1 min |
| the gate's preflight (`make quick`, 754 unit tests) | 34 s |
| static, format, typecheck and the reference step | ~30 s |
| the gate's test phase: 10,376 tests, coverage on, rolls real | 280 s |
| the landing cohort past the gate's end | 1.4 min |
| the ticks and the push | ~0.5 min |

The gate ran in FULL mode: "gate: FULL - the tooling changed (Makefile, pyproject, lockfiles, scripts/)". Asked of the
gate's planner offline on its baseline, T26's two engine files (`hamletgen/ways/tree.py`,
`settlement/homestead_parts/fixture_seats.py`) reached 143 of 11,890 baseline tests in 21 test modules. The same tree
without coverage and with rolls served from cache ran in 157 s and 180 s (two `make durations` runs). Of October's green
gate runs in `dev/run-log/2026-10/`, 286 were full (median 194 s) and 49 incremental (median 42 s).
