# Call counts replace the timing band

**Load this file when:** you work User Story 5, the change to how performance is watched.

## The GM's decision (`request.md` 4)

- **Timings stay recorded but stop driving anything.** `make perf` keeps the wall and CPU seconds and the machine's state.
  No rule says which timing increase is permitted; there is no band, no flag and no record owed on a timing.
- **Call counts are recorded beside the timings and are what is watched.** Per stage and per seed, they are deterministic:
  the same code and seed give the same count on any processor under any load.
- **A call-count increase over the line owes the round arbiter's acceptance.** It is not a gate the session cannot pass,
  but it is not landed silently either. The arbiter accepts it, or rules to keep optimizing, without the GM, and raises it
  to the GM only when it judges the increase too large. The GM: "this is the kind of thing that I would expect the arbiter
  to be able to handle without me."

## Why counts work where timings did not

The project spent features 129, 178, 179 and 375 tuning timing bands against noise:

- a per-environment band-1 line;
- identical code on the same CodeBuild box crossing band 1 on five of six comparisons (constitution v2.16.0's amendment
  note);
- load and processor moving bookends taken back to back (memory: "bookends drift with load").

A call count has none of that noise. It changes only when the code or the seed changes, so any change is real and points
at the chain that moved (`tooling-perf-fanout.md`).

## How to count cheaply

`make perf-profile` uses cProfile, which costs about +225% (`dev/performance.md`, measured on seed 4: 27.4 s -> 89.0 s); that is too much for every bookend. Options to measure, cheapest
first:

1. **`sys.monitoring` (PEP 669) CALL / PY_START events with a per-code-object counter.** These are the hooks
   `pipeline/gencache.py` already uses for dependency capture. Check that the tool IDs do not collide; gencache claims one.
2. **`sys.setprofile` with a counter only:** cheaper than cProfile, but heavier than `sys.monitoring`.
3. **cProfile on one seed only,** with timings taken unprofiled on the others.

Measure each option's overhead on the reference hamlet before choosing, and record the choice and its overhead beside the
code.

Count Python-level calls per stage. C code inside shapely and numpy is not counted. That is the point: it is cheap work, and
the count tracks interpreter work.

## What the flag compares, and its line

- **Compared:** a stage's count at each seed and size against the same seed and size on HEAD before the change (the
  `-start` bookend, or main).
- **Line:** a GUESS knob for the first version, named in `make tunables`. The suggested starting value is an increase over
  5% in any stage on any seed, or over 2% in the total. Tune it on the first few landings and record why beside it.
- **Expected movement:** a count moves when an interpreter or library version changes (Python 3.14 -> 3.15, a shapely
  release). Record those versions in the snapshot, and refuse to compare snapshots taken on different versions rather than
  flag them. A count also moves legitimately when a feature adds rules. That is exactly what the arbiter's acceptance is for:
  necessary, commensurate, no way around it (the band-3 standard of feature 129, now applied to calls).

## Flow at landing

1. `make perf LABEL=<NNN>-start` / `-end` record counts with the timings.
2. At the push (`sync-with-main.sh`, where `make perf-review` runs today), a count increase over the line with no ruling
   refuses the push. It names `make arbiter-ask` with the subject pre-filled: the stages, the seeds and the top growing
   chains from `make perf-fanout`.
3. The `round-arbiter` rules:
   - `accept`: the increase is the cost of a rule the feature adds, and is commensurate;
   - `continue`: optimize first;
   - `process-fault`.

   An accepted ruling clears that pair. The arbiter's agent file gains the call-count case and the guidance on when an
   increase is "too much" and goes to the GM.
4. A decrease is printed and never needs anything.

## What changes where (from a grep on 2026-10-26; re-grep before editing)

| place | today | change |
|---|---|---|
| `.specify/memory/constitution.md` Principle VI | the bands as a flag (v2.30.0) | timings recorded only; call counts flagged, the arbiter accepts. A MINOR amendment |
| `l7r/diagram/tools/perf_bands.py` | the three timing bands | retired, or turned into the call-count line |
| `l7r/diagram/tools/perf_review.py` (`--check`), `make perf-review`, `make perf-gate` | print the band-1 timing flag | compare counts; refuse an unruled increase; timings printed for information only |
| `l7r/diagram/tools/perf_snapshot.py`, `make perf` | seconds per stage | plus calls per stage per seed, and interpreter and library versions |
| `scripts/sync-with-main.sh` (around line 395) | runs `make perf-review` and prints the flag | the call-count check and its refusal text, naming the arbiter command |
| `.claude/agents/round-arbiter.md` | band-3 timing case | the call-count case and its escalation guidance |
| `.claude/agents/perf-audit.md` | adjudicates timing bands | retire, or repoint at a call-count investigation |
| `l7r/diagram/CLAUDE.md` ("Performance is recorded and flagged"), `dev/performance.md` ("The three bands"), `docs/guards.md` (perf rows) | the timing flag | the new rule, with the GM's words |
| `tests/tools/test_perf_bands.py`, `test_perf_review.py`, `test_perf_snapshot.py` | pin the bands | pin the call-count line, the refusal and the version guard |
| project memory `feedback_perf_signoff_by_session.md` | "perf is a flag, never a gate" | updated when this lands |

Each guard change follows the project's guard rules (`docs/guards.md`):

- a test companion in `make hooks-test`;
- the refusal names the compliant command;
- prove it fires by deleting it and watching a test go red.
