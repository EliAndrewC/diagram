# Tasks: The Reference Hamlet Is Accepted by the GM (133)

Checked off only when verified on Inashiro. Every task from T10 on is the GM's, verbatim, one at a
time, and carries its clock (plan.md "The task clock"). The skeleton phase (T01-T04) is NOT
measured - the GM's instruction.

## Phase 0 - the skeleton (not measured)

- [ ] T01 `spec-fidelity` review of this skeleton; verdict recorded in spec.md
- [ ] T02 the would-have-dispatched trail (FR-004): `runlog.write_would_have` + report block; written from `ci/__main__.py` (remote-off refusals, LOCAL-GATED merges that would have DISPATCHED) and from `switches check remote`; `make ci-status`/`make audit` show it; tests in `tests/ci/` and `tests/test_switches.py`; `make quick` green
- [ ] T03 the doctrine (FR-007): constitution clause (v2.3.0), root CLAUDE.md, skill CLAUDE.md, SKILL.md
- [ ] T04 skeleton pushed to main (the spec-number claim; DIRECT - nothing in it is engine content) so a fresh session's clone carries it; `.specify/feature.json` points at 133 in this clone

## Phase 1 - the GM's tasks, one at a time (measured)

_(appended as the GM names them; each entry: the GM's words verbatim, then `given | done | elapsed | runs:` and a `note:` only if the time was out of proportion)_

## Phase 9 - acceptance

- [ ] T90 the would-have-dispatched audit (FR-005): every entry in the period, and for each whether it should have run; each "no" names a tooling change
- [ ] T99 **the GM accepts the current state of Inashiro** - tickable only on the GM's explicit word, recorded here verbatim
