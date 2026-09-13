# Feature 240 - plan

## Architecture, settled before the first edit

**One importable decision module, called by the hook.** The decisions FR-003 to FR-006 make live in
`scripts/_review_prereq.py`, a stdlib module with a CLI, and `scripts/pair-hooks.sh` calls it. This is
feature 239's own lesson (its R3): a guard whose decision is a program inside a shell string cannot be
called, timed or unit-tested without spawning the whole hook. The module is tested directly by
`tests/tooling/test_review_prereq.py`; the hook's wiring is tested by `scripts/test-pair-hooks.sh`.

**The records, and where they live.** All are clone-local and gitignored, like the pairing state beside
them under `<clone>/.git/`:
- `review-verdicts/<map>.json` - the verdict record the agent writes as its last act (FR-001): `map`,
  `engine_key`, `verdict`, `findings` [{`id`, `severity`, `what`}], `written`.
- `review-dispositions/<map>.json` - `accepted` dispositions (FR-003), written only by
  `make review-accept MAP= FINDING= REASON=`, which also writes the bypass-log entry `make audit` lists.
- measurement records are feature 239's `measurements.json` under the feature that measures, extended by
  `quantity`, `source`, `subject`, `verifies` (FR-009); the module scans `specs/*/measurements.json`.

**Map currency without a side effect (FR-005).** `pipeline/gencache.load()` copies cached outputs into
place on a hit, so it must not be the check. `gencache` gains `is_current(gen) -> bool`, the key
comparison alone, and `load()` calls it so there is one body; the module asks it per pool gen.

**The pair closes on a verdict (FR-002).** `pair-hooks.sh`'s Agent branch stops writing `review_key` at
dispatch; `review_recorded()` becomes true when a PASS or NEEDS-WORK verdict record for the current key
exists for every owed map. Between dispatch and verdict, the existing `review_pending()` (a subagent this
session launched that has not finished) keeps the stop branch quiet, so a running review is unaffected.

**Order inside the Agent branch**: escape (`REVIEW_PREREQ_OK`, then the existing `PAIR_OK`), then the
prerequisite module (FR-003 findings, FR-004 fix-review gate, FR-005 currency, FR-006 figures), then the
existing no-gate refusal. A refusal names what is missing and the command that fixes it.

**review-gate.sh (FR-002)** gains one refusal: a changed map whose most recent verdict record is
NOT-REVIEWABLE. Its notes-file rule and `REVIEW_GATE_OK` are untouched.

**The agent files (FR-007, FR-008, FR-010)** get a FIRST STAGE section above everything else, and
`settlement-review.md` a closing VERDICT RECORD section with the shape.

**Perf (FR-010)**: `perf_review.py explain` gains `--control KEY` / `--unverified REASON`, one of which is
required; `--control` must name a record in a `measurements.json`; `--unverified` is logged. The Makefile's
`perf-explain` passes `CONTROL=` / `UNVERIFIED=`.

## Constitution check

- XIII no regressions: every guard suite and the gate green before the push.
- X clause 5: the new module and `gencache.is_current` owe 100% coverage; the module is under `scripts/`,
  which the coverage floor does not measure, so its behavior is proven by its own pytest file instead.
- XVIII guards have suites proven to FIRE: each new refusal is deleted once and a test watched to go red.
- A guard file edit carries `GUARD_EDIT_OK` with a reason at each change.
