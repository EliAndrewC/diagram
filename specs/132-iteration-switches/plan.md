# Implementation Plan: The Iteration Switches

**Branch**: none (`SPECIFY_FEATURE=132-iteration-switches`) | **Date**: 2026-08-25 | **Spec**: [spec.md](spec.md)

## Summary

One tracked JSON setting (`dev/switches.json`) with two axes, read by a new pure module
`l7r/diagram/switches.py`, written only by four make targets that commit. The ci dispatcher gains
a sixth (first-printed) condition `remote-enabled` and a LOCAL-GATED verdict path; the sweep
targets gain a first recipe line that asks the switch; `mapcheck` and `cohort_audit` ask it in
Python too. `sync-with-main.sh` learns a third route name. Every refusal has a test that fires.

## Technical Context

**Language/Version**: Python 3.14 (pinned), GNU make, bash
**Primary Dependencies**: none new
**Storage**: `.claude/skills/diagram/dev/switches.json` (tracked)
**Testing**: pytest (100% on `switches.py` and the ci package), `make hooks-test` for the shell guard
**Single-artifact target**: N/A - no generator code changes; the reference settlement is not re-rolled by this feature except as part of `make done`
**Performance bookends**: N/A - `l7r/diagram/hamletgen`, `check_village` and the pipeline are untouched; `make perf` measures the generator, which this feature does not change. (Recorded here so the absence is a decision, not an omission.)

## Constitution Check

- I, II: N/A - no UI in this repository.
- III (pool data): N/A - no generated content.
- V (GM's writing): PASS - nothing touched.
- VI (verification): PASS - reference-scope `make done` before push; the gated route pushes on the local-done rule.
- X (quality): PASS - ruff/mypy strict/pytest, 100% on the new module and the ci package.
- XII (research before ruling): N/A - tooling, not history.
- XIII (no regressions): PASS - baseline is a green `make done` on main's tip (commit 4f51d39a's run-log entry).
- XIV (fix what you find): the `resvg`-missing render-sync failure was an environment gap, fixed by `setup-dev-env.sh`, not a code defect.
- XVI (spec reviewed by someone else): `spec-fidelity` round 1 launched before this plan; implementation waits for FAITHFUL.
- XVIII (guards ship with tests): PASS by construction - tasks T12-T15.

## Design

### The setting (FR-001..005)

```json
{
  "remote": {"state": "off", "why": "...", "who": "Eli Courtwright", "utc": "2026-08-25T18:00:00Z"},
  "scope":  {"state": "reference", "why": "...", "who": "...", "utc": "..."}
}
```

`switches.read(skill_dir) -> Switches`: absent -> defaults; unparseable or wrong shape -> `Switches`
with both axes CLOSED and `error` set (FR-004). `remote.state in {"on","off"}`,
`scope.state in {"unlocked","reference"}` - anything else is malformed.

`python3 -m l7r.diagram.switches` (registered in `_invocation.OPERATIONS` as `switches`, cheap):

- `show` - both axes (FR-005; `make switches`)
- `set remote off|on --why W` / `set scope reference|unlocked --why W` - writes the file with
  who/utc; the make target commits it (FR-002). Refuses an empty `--why`.
- `check remote WHAT` / `check scope WHAT` - exit 0 if allowed, else prints the refusal (reason,
  date, the release target, the local route for WHAT) and exits 1 (FR-006, FR-010).

### Makefile

- `ci-off REASON=` / `ci-on REASON=` / `scope-lock REASON=` / `scope-unlock REASON=` / `switches`.
- `SWEEP_OK = @python3 -m l7r.diagram.switches check scope $@` as the FIRST recipe line of
  `cohort`, `tripwire`, `test-full`; conditional on `FULL` in `done`, `ci-check`, `ci-merge`;
  conditional on `TARGET` in `ci-check`; on `SCOPE=all` in `maps`.
- `REMOTE_OK = @python3 -m l7r.diagram.switches check remote $@` first in `ci-check`, `ci-image`.
  `ci-merge` does NOT get it - the dispatcher handles remote-off itself because it must still
  produce the LOCAL-GATED verdict for the ritual (FR-008).

### The dispatcher (FR-006..009)

- `decision.decide(..., remote_off: str | None)`: first condition `remote-enabled`. Verdict:
  any other failing condition -> `REFUSE(that)`; else verified satisfies -> `SKIP-VERIFIED`; else
  remote off -> `REFUSE(remote-enabled)`; else `DISPATCH`. So LOCAL-GATED is "the existing local
  verified rule, with dispatch as the fallback removed".
- `__main__`: read switches before constructing `Boto3Client`. With remote off: `status` runs with
  no client (already supported); `check`/`image` refuse (name `make done` / `make ci-on`);
  `merge` runs `status_text` with no client, writes `.git/ci-verdict`, returns 0 only on
  SKIP-VERIFIED. `ci-status --route` prints `GATED-LOCAL` when the route is GATED and remote is off.
- `dispatch.status_text` passes the switch through. No AWS call can occur: the client is None.

### The ritual (FR-008, FR-009)

`sync-with-main.sh`: accept `GATED-LOCAL` from `ci-status ROUTE=1`; print
`route GATED (local - remote off)`; take the GATED branch (ci-merge -> verdict -> push on
SKIP-VERIFIED). `FULL=1` with remote off is refused by ci-merge. Companion:
`scripts/test-sync-with-main.sh` gains the third route via the `CI_ROUTE`/`CI_MERGE` seams.

### The rule: ONE map per invocation, reference only (FR-010, FR-012, FR-013)

Round 1 of the fidelity review turned the enumeration into a rule, so the Python layer covers every
multi-map entry point, not a list of targets:

- `pipeline.regen.main`: under the lock, more than one gen -> refuse (a glob expands in the shell
  before make sees it, so the module is where a globbed `GEN` is caught).
- `tools.cache_audit.main`: refuse under the lock (its default rolls a subset repeatedly).
- `tools.make_regressions.main`: refuse under the lock (rebuilds the corpus from many seeds).
- Makefile: `SWEEP_OK` also first in `cache-audit` and `regressions`; `map` passes through to the
  module's own check (the list is only known there).
- `tools.perf_snapshot --record` refuses under the lock (round 2: several seeds is a sweep);
  `SWEEP_OK` first in `perf` and `perf-gate`. A feature landing under the lock records "bookends
  not taken - scope locked" in its plan; they are owed at unlock.
- Left runnable, recorded in `dev/switches.md` with the alternatives priced (FR-018): the FR-012
  set - `map` with one gen, `hamlet` with one spec, `perf-profile` (one seed, one stage),
  `placement-stages` (the reference map's stages), and every no-map target.

### The test seams (the reviewer's aside, Principle XIV)

`sync-with-main.sh` honors `CI_ROUTE`, `CI_MERGE` and `CI_PERF_REVIEW` only when
`$ROOT/$SKILL_DIR/Makefile` is ABSENT - the fixture case its test builds (`.claude/skills/x`). On a
real clone they are ignored, so `CI_ROUTE=DIRECT` can no longer skip the gated route. The
companion test gains a case proving a real-shaped tree ignores the seam.

### mapcheck / cohort_audit (FR-011, FR-013)

- `mapcheck`: `--scope all` under lock -> refuse; `auto` under lock -> reference only, no
  tripwire, no widening; prints "scope locked (reason) - reference map only".
- `cohort_audit.main`: refuse first thing, before the reference check.

### Guard-file hook (FR-016)

Add `*/.claude/skills/diagram/dev/switches.json` to `scripts/guard-file-hooks.sh`'s pattern and a
case to its test.

### Records (FR-017, FR-018)

`dev/switches.md` (what, why, the two axes, the fail-closed rule, the decision on single-map
targets and the priced alternatives), the ci `CLAUDE.md` sixth condition, CLAUDE.md's enforcement
table row, `dev/loop.md` ladder note, comments at each Makefile line.

### The amendment: `make done` short-circuits (FR-019..FR-023)

`delta.is_gate` (a rule over everything the gate reads or runs) and `gate_key_worktree`; the
`VerificationState` gains `gate_key`; `state.already_verified(root)` is the decision; `ci
verified-done` exposes it; the `done` recipe is ONE shell block whose first step exits 0 on
`already verified` (re-stamp, run-log `already-verified`, `green-local done`). Never for FULL; no
flag in either direction. Containment (the key holds every file gate-stamp hashes) is what makes
the re-stamp honest, and a test proves it against gate-stamp's own lists.

## Test design

- `tests/test_switches.py`: read defaults / absent / malformed (fail closed) / write round-trip /
  who-utc-commit / every `check` outcome and message / CLI exit codes / empty why refused.
- `tests/ci/test_decision.py`: `remote-enabled` row; verdict table with remote off x {verified
  local, unverified, other failing condition}.
- `tests/ci/test_main.py`: remote off -> check/image refuse with rc 1, `FakeClient` never
  constructed (monkeypatched constructor raises); merge remote off -> SKIP-VERIFIED path writes
  ci-verdict; `--route` prints GATED-LOCAL.
- `tests/tools/test_mapcheck.py` / `test_cohort_audit.py`: lock refusals and no-widening.
- Makefile-level: `tests/test_switches.py::test_make_targets_refuse_under_lock` runs real `make`
  in a fixture skill dir (Makefile copied, `l7r` symlinked) with the lock thrown: `cohort`,
  `tripwire`, `test-full`, `done FULL=1`, `ci-check FULL=1`, `ci-image` (remote off) all exit 1
  with the refusal text and never reach `reference`.
- `scripts/test-sync-with-main.sh`: GATED-LOCAL route.
- `scripts/test-guard-file-hooks.sh`: switches.json is a guard file.

## Complexity Tracking

None. No new dependency, no new subsystem; one 200-line module and recipe lines.
