# Research: Faster landings

## R1 - Did today's `cover-changed` miss the coverage reds? (FR-003a)

- **Finding** (`m:coverage-reds-replay`): of today's 6 coverage reds, the 5 that name lines name 8 spans (20 lines), and every one is EXISTING
  lines that lost their coverage - a test or caller deleted with its pass, or code moved behind a new branch - none added. The
  sixth was the gate not counting new tests marked `tooling`, which `cover-changed`'s run counted.
- **Which modules** (same key, re-run by `bash specs/430-faster-landings/replay-reds.sh`): THREE of the five name lines in a module
  their delta changed (31f739f5d, d92ff2c90, 39ea51383); TWO name a module their delta did not touch - 7f209090b `law.py:933`
  (its delta changed the modules that called it) and 449e7df7b `checks.py:141` (its delta deleted the field spur that reached it).
- **So**: `cover-changed` asks only the lines a change ADDS, by design (its docstring), so it could see none of the five; and it
  runs a different selection from the floor's. FR-003's check asks EVERY line of each changed module (the GM's "on the changed
  modules") with the tests the gate's floor counts for it: it catches three of the five line-naming reds and the sixth. The two
  whose lost line sits in an unchanged module stay the gate's to catch - the narrowing FR-009 asks stated, at a price of 2 of
  today's 6 reds (one gate each, 4-5 minutes - observed 2026-10-26, method: `dev/run-log`, the GM's figure in `request.md` item 3).

## R2 - What holds a claims triage back until the plan review returns? (FR-007)

- **Finding** (read 2026-10-26, method: the guards' agent lists and the guard log): nothing does. The decide-first test runs for
  the agents in `scripts/hooks/check-bundle-hooks.sh` `CHECKS` and `scripts/hooks/pair-hooks.sh` `REVIEW_AGENTS`; `claims-triage`
  is in neither (`impl-drift` is in `CHECKS`). `make guard-log` holds no decide-first refusal of a `claims-triage` dispatch, only
  three `step-back-due` refusals (2026-10-19 twice, 2026-10-21).
- **So**: the triage ran after the plan review because the session's own order put it there - the claims round was begun at the
  landing. FR-007 is met by the guards as they stand; what is missing is the prompt to start it: `make decide` and `make
  plan-delta` name the owed triage, so it is dispatched beside the review (D7), and a guard test pins that decide-first lets it
  through while impl-drift still waits.

## R3 - The non-module files of today's test-tree full runs (FR-002)

- **Finding** (`m:full-plan-reasons`): 4 the top-level `tests/conftest.py`, 2 `tests/hooks/test-cohort-gate.sh` (a guard suite
  `make hooks-test` runs, no pytest test), 1 `tests/hamletgen/ways/CLAUDE.md`, 1 `tests/tooling/ci/conftest.py`.
- **And** the fixture data under `tests/` is read across directories (observed 2026-10-26, method: `find tests/fixtures -type f`
  and a grep of `tests/**/test_*.py` for `fixtures/`): `tests/fixtures/` (56 files) holds no test module of its own, so "the tests of that directory" alone would select nothing for a change there.
- **So**: a data file selects its own directory's tests AND every test module that names it (its file name or its directory
  under `tests/`), a superset of FR-002's directory - the narrowing FR-009 forbids otherwise (D2).
