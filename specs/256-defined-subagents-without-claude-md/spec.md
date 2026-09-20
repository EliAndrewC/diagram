# Feature 256 - defined subagents launch without the root `CLAUDE.md` and the memory index

**Status:** drafted 2026-09-20; awaiting its first review.

## Summary

The GM ruled (`request.md`) that a subagent this repository DEFINES should not be handed the root `CLAUDE.md` or the
session's memory index: what such an agent needs to know belongs in its own specification. An ad-hoc agent a
session dispatches keeps both. The harness has the switch - `omitClaudeMd: true` in an agent file's frontmatter,
measured in feature 255's R7 to remove both files from a subagent's first turn. This feature first moves into each
contract whatever that check was relying on the root `CLAUDE.md` to tell it, then sets the field in all twelve agent
files, and proves on recorded findings that the checks still find what they found. No engine code: the delta routes
DIRECT.

## Functional requirements

**FR-001 - what each check relied on is found and moved into its contract.** For each of the twelve files under
`.claude/agents/`, the root `CLAUDE.md` is read rule by rule against the contract, and a rule the check's JOB depends
on that the contract does not already state is added to the contract, in the contract's own voice and no longer than
the check needs. `research.md` records, per agent, each rule considered and whether it was already stated, was
moved, or does not bear on that check. Nothing is moved from the memory index: by the GM's words the memories are
the main session's.

**FR-002 - the field is set in all twelve agent files.** `omitClaudeMd: true` is added to the frontmatter of
`building-review`, `entry-drift`, `escalation-check`, `perf-audit`, `quote-check`, `record-format`,
`settlement-review`, `size-audit`, `source-applicability`, `source-reader`, `spec-fidelity` and
`spec-fidelity-verify`. Nothing is changed for an ad-hoc agent or for the main session.

**FR-003 - a guard keeps it so.** `.claude/skills/diagram/tests/test_agent_models.py`, which already reads every
agent file's frontmatter for its pinned tier, also requires `omitClaudeMd: true` of every file under
`.claude/agents/`, so an agent added later is defined without the two files unless someone decides otherwise in the
test. Its tier table is untouched.

**FR-004 - it is proven on recorded findings, in the setting where the field acts.** The field is ignored when an
agent runs as a session's main agent, which is how feature 251's headless harness runs a check; so each seeded run
here is a headless session in the case's worktree whose only job is to dispatch the agent under test ONCE with the
recorded prompt, verbatim, and return its reply - the agent then runs as a subagent, as it does in real use. Cases,
each run twice in that same setting, with the field and without it (the control): the two later review rounds of
feature 255's R3 on `spec-fidelity-verify`, and the one-section `record-format` case of feature 255's R2 (six
recorded findings, the contract as it stands on main). The field stands when, on every case, the run with the
field misses nothing its control caught. Six runs; the batch's size and rough weight are stated before it is
launched, and `research.md` holds one row per run with the subagent's own turns and weight.

**FR-005 - what a failed proof does.** If a run with the field misses what its control caught, the missed finding is
read against the root `CLAUDE.md`: when a rule there accounts for it, that rule is moved into the contract (FR-001)
and the pair is run once more; when none does, or the second pair misses again, the field is NOT set for that agent,
`research.md` says so with the runs, and the result goes to the GM. The other agents are not held back by it.

**FR-006 - the three agents with no recorded runs.** `perf-audit`, `building-review` and `size-audit` have no
recorded run to replay. For them FR-001's reading is done with the same care and the field is set without a seeded
run, as the GM agreed (`request.md`); `research.md` says which three were not proven and why.

**FR-007 - the record.** The measured first-turn input of one real defined agent, dispatched from this repository
before and after the field, is recorded in `research.md`. Root `CLAUDE.md`'s review-subagents bullet and
`docs/efficiency-tooling.md` say that a defined agent launches without the root `CLAUDE.md` and the memory index and
that what it needs is written in its contract; `docs/review-ledger.md` is not touched (no review pass of a shipping
map is made).

## Success criteria

- **SC-001** (FR-001) `research.md` holds, per agent, the rules considered and the disposition of each.
- **SC-002** (FR-002, FR-003) All twelve agent files carry the field, and the tier test fails on an agent file
  without it (proven by removing it from one file and watching the test go red).
- **SC-003** (FR-004, FR-005) `research.md` holds one row per seeded run, and each tested agent ends with the field
  set on a clean proof or not set with its runs.
- **SC-004** (FR-006) The three unproven agents are named as such.
- **SC-005** (FR-007) The before-and-after first-turn input of a real defined agent is recorded; `make hooks-test`
  and `make quick` are green; nothing under `l7r/` or `pool/` changed.

## Assumptions

- The harness honors `omitClaudeMd` for a project agent file as it did for the inline probe agent of feature 255's
  R7; FR-007's measurement is also the check of this.
- A change to an agent file takes effect for THIS session's dispatches only after it lands and the mirror
  fast-forwards (feature 251, R4), which is why the proof runs through headless sessions in worktrees.

## Decisions Recorded

- **D1 - the proof is sized small, by the GM's standing instruction** (2026-09-19, *"redoing old work is only useful
  insofar as it does give us sensible measurements"*): three cases on the two cheapest tested agents, each with a
  control, as the proposal the GM answered "go" to said. The other seven agents that do have recorded runs are
  covered by FR-001's reading and by the same field behaving the same way, not by a seeded run each.
