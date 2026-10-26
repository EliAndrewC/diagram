# Working notes: what a session working this feature must know first

**Load this file when:** you start working the feature (planning or any task).

## Before the first change

- **Wait for the engine refactors in flight.** On 2026-10-26 the GM held this feature because another session was making
  the tests more efficient and removing guess-and-check from placement ("I don't want to be making multiple different
  fundamental engine refactors at the same time", `request.md` 2). Check with the GM that it has landed.
- **Re-run the survey first** (`make perf-fanout`, built as this feature's first task: `tooling-perf-fanout.md`). Line
  numbers and counts in `research/` are from commit dd3793e29. Chains will have moved, and some may already be gone after
  the refactors. Re-scope against the new output, not against this record.
- **Read open feature 373** (`specs/373-field-tie-distance-per-tie/`, hamlet + performance) before planning: it is a related
  open performance item and may fold into this one.
- **Take the start bookend:** `make perf LABEL=427-start SCALING=1`.

## Rules the work is held to (the project's, restated only as pointers)

- **Engine changes are spec-kit work on the gated route** (root `CLAUDE.md`). `make land` runs `make done` and
  `make cohort-landing`, and no seed may regress (constitution XIII).
- **Maps may change for speed but never against the research** (GM 2026-09-30 and 2026-10-18, `l7r/diagram/CLAUDE.md`
  "Performance"). Many of the functions named here carry `Research:` claims; a claim on moved or rewritten code is re-owed
  (`make claims-owed`). Before changing what `CanopyArea` counts (C5) or the wells' ranking (R1), read the claims on them.
- **The function cap** (100 statements, `check-function-cap.py`) and the **1,000-line file bar** (split into a package)
  hold for new code.
- **Measure the time by an A/B against HEAD**, not by cProfile's seconds, and verify each refactor by the chain's call count
  falling in `make perf-fanout`. A refactor that changes a map is judged by the cohort and the rules, not byte identity.
- **Mind the host memory cap** when fanning out profiles or cohorts. The containers share 10 GB; five parallel profiles fit
  on 2026-10-26 with the other containers at about 4 GB.

## Lessons from the exercise

- **Predict a saving per seed, never from medians** (`research/estimate-exercise.md`, the wells correction).
- **Read the code before naming a cause.** The estimate agents called `CanopyArea` an index and `_seats_near` a scan;
  neither was.
- **No single function is slow.** A profile sorted by time will keep showing 0.3-0.8 s items. Sort by calls and walk up to
  the multiplying loop; that is what the survey does.
