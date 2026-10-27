# Tasks - feature 436, perf-ab quick first

## Occasions

- none: tooling only - no map feature, glyph or placement rule

## Tasks

- [x] T01 `make perf-ab`'s three forms decided by the count compared (quick the default: seed 25 at 40 households, 6 runs; subset; FULL=1), the versions alternated A B / B A, wall and CPU time each with best and spread, the quick runs recorded by engine key and every non-quick run refused without one (PERF_AB_QUICK_OK with a reason), the A/A floor (AA=1) printed beside a quick result, and the checklist and guard table updated (D1-D8; FR-001 to FR-008)
      research: rendering
      verify: DONE. landed: make perf-ab: quick (one seed at one size, the default) first and enforced, subset, FULL=1; alternated A B / B A; wall and CPU best and spread; the A/A floor; quick 2.05 min against the sweep's 8.2
