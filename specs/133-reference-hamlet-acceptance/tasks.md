# Tasks: The Reference Hamlet Is Accepted by the GM (133)

Checked off only when verified on Inashiro. Every task from T10 on is the GM's, verbatim, one at a
time, and carries its clock (plan.md "The task clock"). The skeleton phase (T01-T04) is NOT
measured - the GM's instruction.

## Phase 0 - the skeleton (not measured)

- [x] T01 `spec-fidelity` review of this skeleton: round 1 one change (no route promise), round 2 FAITHFUL - recorded in spec.md
- [x] T02 the would-have-dispatched trail (FR-004): `runlog.write_would_have` + `would_have_report` (inside `remote_spend_report`, so `make ci-status` and `make audit` show it); written from `ci/__main__.py` (remote-off refusals of check/image, LOCAL-GATED merges whose verdict is `REFUSE(remote-enabled)` = would have DISPATCHED) and from the Makefile's `REMOTE_OK` via `ci remote-ok`; entirely in `ci/` + Makefile so the skeleton's delta stays DIRECT; tests in `tests/ci/test_runlog.py` + `test_main.py`; `make quick` green
- [x] T03 the doctrine (FR-007): constitution v2.3.0 "Iteration wall-clock is the cost" (the GM's words), root CLAUDE.md iteration heading, skill CLAUDE.md "The goal all of this serves", SKILL.md "The working rule behind the tooling"
- [ ] T04 skeleton pushed to main (the spec-number claim; DIRECT - nothing in it is engine content) so a fresh session's clone carries it; `.specify/feature.json` points at 133 in this clone

## Phase 1 - the GM's tasks, one at a time (measured)

_(appended as the GM names them; each entry: the GM's words verbatim, then `given | done | elapsed | runs:` and a `note:` only if the time was out of proportion)_

## Phase 9 - acceptance

- [ ] T90 the would-have-dispatched audit (FR-005): every entry in the period, and for each whether it should have run; each "no" names a tooling change
- [ ] T99 **the GM accepts the current state of Inashiro** - tickable only on the GM's explicit word, recorded here verbatim
