# Feature 256 - defined subagents launch without the root `CLAUDE.md` and the memory index

**Status:** FAITHFUL at round 3 (2026-09-20, see Review history); planned, not yet implemented.

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
moved, or does not bear on that check. The memory index is not swept entry by entry - by the GM's words the memories
are the main session's, and no check's contract refers to the index (feature 255, R5) - but anything a check turns
out to have needed from it is written into that contract like any other rule (*"If there's something that a subagent
should know, it should be in the subagent specification"*). The field may also keep a NESTED `CLAUDE.md`
(`.claude/skills/diagram/CLAUDE.md`, `research/CLAUDE.md`) from loading when a check reads under those trees; the
same reading is made of those two files for the checks that work there.

**FR-002 - the field is set in all twelve agent files.** `omitClaudeMd: true` is added to the frontmatter of
`building-review`, `entry-drift`, `escalation-check`, `perf-audit`, `quote-check`, `record-format`,
`settlement-review`, `size-audit`, `source-applicability`, `source-reader`, `spec-fidelity` and
`spec-fidelity-verify`. Nothing is changed for an ad-hoc agent or for the main session.

**FR-003 - it is proven on recorded findings, in the setting where the field acts.** The field is ignored when an
agent runs as a session's main agent, which is how feature 251's headless harness runs a check; so each seeded run
here is a headless session in the case's worktree whose only job is to dispatch the agent under test ONCE with the
recorded prompt, verbatim, and return its reply - the agent then runs as a subagent, as it does in real use. Cases,
each run twice in that same setting, with the field and without it (the control): the two later review rounds of
feature 255's R3 on `spec-fidelity-verify`, and the one-section `record-format` case of feature 255's R2 (six
recorded findings, the contract as it stands on main). The field stands when, on every case, the run with the
field misses nothing its control caught. Six runs; the batch's size and rough weight are stated before it is
launched, and `research.md` holds one row per run with the subagent's own turns and weight.

**FR-004 - what a failed proof does.** The field is set on all twelve per FR-002 in every case. If a run with the
field misses what its control caught, the missed finding is read against everything the field removes - the root
`CLAUDE.md`, the memory index and the nested `CLAUDE.md` files: when something there accounts for it, that is
written into the contract (FR-001) and the pair is run once more. When nothing accounts for it, or the second pair
misses again, `research.md` records the runs and the missed finding and the result is raised with the GM once the
feature works; the field remains set unless the GM rules otherwise.

**FR-005 - the three agents with no recorded runs.** `perf-audit`, `building-review` and `size-audit` have no
recorded run to replay. For them FR-001's reading is done with the same care and the field is set without a seeded
run, as the GM agreed (`request.md`); `research.md` names those three, and says that the seven agents which DO have
recorded runs were also not re-run, per D1 - ten of the twelve end the feature with no seeded run of their own.

**FR-006 - the record.** The measured first-turn input of one real defined agent, dispatched from this repository
before and after the field, is recorded in `research.md`. Root `CLAUDE.md`'s review-subagents bullet and
`docs/efficiency-tooling.md` say that a defined agent launches without the root `CLAUDE.md` and the memory index and
that what it needs is written in its contract; `docs/review-ledger.md` is not touched (no review pass of a shipping
map is made).

## Success criteria

- **SC-001** (FR-001) `research.md` holds, per agent, the rules considered and the disposition of each.
- **SC-002** (FR-002) All twelve agent files carry the field.
- **SC-003** (FR-003, FR-004) `research.md` holds one row per seeded run, and each tested agent ends on a clean proof, or
  with its runs and the missed finding recorded and raised with the GM, the field set either way.
- **SC-004** (FR-005) The three agents with no recorded run to replay are named, and `research.md` says that the seven
  with recorded runs were also not re-run, per D1.
- **SC-005** (FR-006) The before-and-after first-turn input of a real defined agent is recorded; `make hooks-test`
  and `make quick` are green; nothing under `l7r/` or `pool/` changed.

## Assumptions

- The harness honors `omitClaudeMd` for a project agent file as it did for the inline probe agent of feature 255's
  R7; FR-006's measurement is also the check of this.
- A change to an agent file takes effect for THIS session's dispatches only after it lands and the mirror
  fast-forwards (feature 251, R4), which is why the proof runs through headless sessions in worktrees.

## Decisions Recorded

- **D1 - the proof is sized small, by the GM's standing instruction** (2026-09-19, *"redoing old work is only useful
  insofar as it does give us sensible measurements"*): three cases on the two cheapest tested agents, each with a
  control, as the proposal the GM answered "go" to said. The other seven agents that do have recorded runs are
  covered by FR-001's reading and by the same field behaving the same way, not by a seeded run each.

## Review history

- **Round 1 (2026-09-20) - CHANGES REQUIRED, four items, all applied.** (1) FR-004's failure branch left the field
  unset for an agent whose proof failed, which writes an exception into the GM's unconditional ruling: the field is
  now set on all twelve in every case, and a persisting miss is recorded and raised with the GM. (2) "Nothing is
  moved from the memory index" was broader than the GM's words: what a check turns out to have needed from the index
  goes into its contract, and a missed finding is read against everything the field removes. (3) A guard in the tier
  test requiring the field of every future agent file was unrequested: cut, with the half of SC-002 that leaned on
  it. (4) SC-004 read as though nine agents were proven: it now says ten of twelve get no seeded run. The reviewer's
  aside - the field may also drop the nested `CLAUDE.md` files - is taken into FR-001 and FR-004.
- **Round 2 (2026-09-20) - all four items RESOLVED; CHANGES REQUIRED on one new item, applied.** The renumbering
  left `measure/dispatch_seeded.sh` citing FR-004 for the dispatch setting, which is FR-003 now: corrected.
- **Round 3 (2026-09-20) - FAITHFUL.** The orphaned id verified corrected; every id `plan.md` and `tasks.md` cite
  exists and means what it is cited for; nothing new introduced.
