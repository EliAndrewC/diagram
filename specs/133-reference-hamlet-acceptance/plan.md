# Implementation Plan: The Reference Hamlet Is Accepted by the GM

**Branch**: none (`SPECIFY_FEATURE=133-reference-hamlet-acceptance`) | **Date**: 2026-08-25 | **Spec**: [spec.md](spec.md)

## Summary

A skeleton: the tooling the GM asked for at the very beginning (the would-have-dispatched trail,
the motivation written into the doctrine), then one task at a time from the GM, each timed, then
acceptance. The map work is whatever the GM points at; it is not planned here.

## Technical Context

**Language/Version**: Python 3.14, GNU make | **Storage**: `dev/run-log/` entries (`where:
would-have-dispatched`) | **Testing**: `tests/ci/` (ci/ is exempt from the gate - `make quick` is
its check, FR-025 of 132) | **Single-artifact target**: `pool/hamlets/inashiro.gen.py` (seed 4,
~26 s `make reference`, ~60 s `make map`) - the ONLY map this feature rolls, by the lock |
**Performance bookends**: NOT TAKEN - scope locked (132 FR-010); owed at unlock, recorded here.

## Constitution Check

- I, II, III: N/A. V: PASS (nothing of the GM's is edited except by quoting).
- VI: PASS - every task verified on Inashiro alone; `make done` (reference scope) before any
  landing; map tasks stay in the clone until acceptance.
- XIII: the baseline for each map task is the reference map's gate result before the change;
  pool regressions are out of view under the lock by the GM's decision (132).
- XIV: defects met in a task are fixed in it and counted in its time (spec edge case).
- XVI: this skeleton is reviewed before Phase 0 is built; each GM task is verbatim, so a batch
  of FRs is re-reviewed only when a task changes the spec's requirements.

## Design

### The task clock (FR-002, FR-003)

Each GM task is a `tasks.md` entry in this shape, written BEFORE work starts:

```
- [ ] T05 <the GM's words, verbatim>
      given 2026-08-26T14:02Z | done - | elapsed - | runs: -
```

and completed to:

```
- [x] T05 <the GM's words, verbatim>
      given 2026-08-26T14:02Z | done 2026-08-26T14:19Z | elapsed 17 min | runs: reference x2 (26 s, 27 s), map x1 (61 s), done x1 (already verified 1 s)
      note: <only if out of proportion - which of the GM's three causes, and what follows>
```

The `runs:` list is read from `dev/run-log/` entries in the window (`make audit` prints them),
never from memory.

### The would-have-dispatched trail (FR-004, FR-005)

`runlog.write_would_have(skill, target, scope, minutes, reason)` writes a run-log entry with
`where: would-have-dispatched`, `cost_usd` at the estimate, excluded from `remote_entries()` (so
month-to-date is untouched) and listed by a new `would_have_report(skill)` block in
`remote_spend_report`. Written from `ci/__main__.py` wherever remote-off refuses or the merge is
LOCAL-GATED with a decision that would otherwise have been DISPATCH (computed by calling `decide`
once more with `remote_off=None`), and from the Makefile's `REMOTE_OK` refusals (`ci-check`,
`ci-image`) through `switches check remote` - which gains the write. Tests in `tests/ci/`.

### The doctrine (FR-007)

- Constitution: a new clause in the Development Workflow section, "Iteration wall-clock is the
  cost", with the GM's words; version bump to 2.3.0.
- Root `CLAUDE.md`: the "Iteration-loop efficiency" heading gains the GM's framing as the project
  goal it serves; the diagram skill's `CLAUDE.md` and `SKILL.md` each gain one paragraph.

### What is NOT built here

FR-006's DIRECT-route gap: recorded as a question; no change without the GM.
