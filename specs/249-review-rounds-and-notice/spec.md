# Feature 249 - review rounds read the diff, and the batching notice speaks on any single call

**Status:** specified; awaiting a FAITHFUL verdict (see Review history).

## Summary

Three tooling changes the GM approved on 2026-09-14 (`request.md`), each making automatic a thing that
was already written down and was not followed. A round of `spec-fidelity` after the first is REWRITTEN
by a hook into the bounded form the agent's contract already prescribes: the previous round's verdict
and the diff since it, prepended to the session's prompt, whatever the session wrote (`research.md`
R1). The batching guard's one-turn-early notice fires on any single-call turn at one below the bar,
not only on a bare read (R2). And MODE 3's third step names a bounded procedure. Nothing here is engine
code, so the delta takes the DIRECT route.

## Functional requirements

**FR-001 - the batching notice fires on ANY single-call turn at one below the bar.** In
`scripts/batching-hooks.sh`, the notice branch drops its shape test entirely - the call's shape AND
its `run_in_background` flag, which is the same judgment factored out as a boolean: it fires when the
call is the first of its turn and the window holds exactly one serial turn fewer than the bar, whether
the call is a bare read, a folded command or a backgrounded launch. The block keeps both tests
unchanged - a folded or backgrounded command is never the right thing to refuse. The notice's wording, its JSON form and its record
(`reminded`/`serial-recon-notice`) are unchanged.

**FR-002 - a `spec-fidelity` dispatch for a feature the tooling has already seen is REWRITTEN into
MODE 3.** A new guard, `scripts/review-round-hooks.sh pretool`, runs on every Agent dispatch. When the
subagent type is `spec-fidelity`, the dispatch is a SPEC review (MODE 2 or MODE 3 - see FR-003 for how
the other two modes are told apart), the prompt names a feature directory (`specs/NNN-slug`) that exists
in this session's clone, and the guard holds a snapshot of that directory from an earlier dispatch, it
returns `updatedInput` with the prompt PREPENDED by a preamble carrying: the round number, counted
within the current pass - a pass begins at the first dispatch the tooling sees and again after a
recovered previous verdict of FAITHFUL, so an amendment's first round is stated as round 1 of a new
pass, never as round six, which is what the GM's 2026-09-12 ruling on the cap requires; the previous
round's verdict verbatim, recovered from the session's subagent transcripts (R3), or - when none is
found - the spec's own Review history entry for that round, marked as the session's summary rather
than the reviewer's words; a unified diff of the feature directory against the snapshot; and the
instruction that this is MODE 3 - read the preamble and what a grep for the ids and terms it names turns
up, and answer any whole-spec question the session's prompt asks from the diff and a grep, never from a
re-read. It then replaces the snapshot with the directory as dispatched, so the next round diffs against
this one, and records `rewrote`/`mode-3-preamble`. The session's own prompt follows the preamble
unchanged. The clone is the one `clone-sync-hooks.sh resolve` names for the session, else the git top
level of the payload's working directory.

**FR-003 - the first dispatch takes the snapshot silently, and a spec with history but no snapshot is
told.** With no snapshot, the guard copies the feature directory into its state and returns nothing
(`permitted`/`first-round`) - unless the spec's Review history already records a round, in which case it
also returns one line of `additionalContext` saying this is a round after the first and that the changed
passages must be supplied by hand this once, because the tooling has no earlier snapshot to diff against
(`reminded`/`history-without-snapshot`). A dispatch naming no feature directory, or one the clone does
not hold, passes untouched (`permitted`/`no-feature`). **A MODE 1 or MODE 4 dispatch passes untouched
and neither takes nor refreshes the snapshot** (`permitted`/`other-mode`): a plan review must read the
WHOLE plan and find its decisions itself (feature 243), and an exception check precedes the spec's
initial reading, which MODE 3's own opening says is a full one. The discriminator is the prompt's text:
a prompt that names `MODE 4`, `plan review` or `plan.md` is a plan review; one that names `MODE 1` or
`exception` is an exception check; every other `spec-fidelity` dispatch is a spec review. The state is
`<clone>/.git/review-round/<NNN-slug>/`, beside the pair guard's `review-snapshot/`: never committed,
never shared between sessions (R4).

**FR-004 - a deliberate full re-read is an escape with a reason.** `REVIEW_ROUND_OK="<reason>"` in the
prompt passes the dispatch through untouched and refreshes the snapshot, recorded `escaped`/
`review-round-ok`. As for `ESCALATION_OK`, a prompt is prose with no command grammar, so the token is
matched as a substring of the prompt; a token with no reason is refused with the standard reason
message, `blocked`/`REVIEW_ROUND_OK-no-reason`.

**FR-005 - the agent's contract names the bounded procedure and the ruling.** In
`.claude/agents/spec-fidelity.md` MODE 3, step 3 is restated: grep the feature directory for the ids
and terms the changed passages name (an FR, an SC, a decision, a task id, a figure, a phrase the change
altered) and read the hits in full; a passage no hit names is not read. The mode's opening records the
GM's 2026-09-14 ruling in their words - a round after the first, including one confirming a verbatim
application of the previous round's edits, reviews the paragraphs that changed - and says that the
tooling now supplies the preamble, so a reviewer that receives none knows the dispatch was the first.

**FR-006 - the tests.** `scripts/test-review-round-hooks.sh` drives the new guard on a fixture clone:
a non-`spec-fidelity` dispatch passes untouched; a first dispatch is silent and leaves a snapshot; a
second dispatch after an edit returns valid JSON whose `updatedInput.prompt` opens with the preamble,
carries the diff, names the round and ends with the session's prompt verbatim, and is recorded
`rewrote`; the previous verdict is recovered from a fixture subagent transcript, and the Review history
fallback is used when none matches; a spec with history and no snapshot gets the context line; a
prompt naming no feature passes; a MODE 4 dispatch and a MODE 1 dispatch naming the feature pass
untouched and leave the snapshot as it was; the escape passes with a reason and is refused without one;
the snapshot advances so a third dispatch diffs against the second; a recovered FAITHFUL verdict starts
the round count again at one. `scripts/test-batching-hooks.sh` gains the cases that a FOLDED single call
and a BACKGROUNDED single call at one below the bar each receive the notice. The firing-log census
(`tests/tooling/test_guard_firing_log.py`) gains rows for the new guard's recorded branches and
classifies `REVIEW_ROUND_OK` beside `ESCALATION_OK`. `make hooks-test` is green.

**FR-007 - the record.** The hook's header states the defect and the GM's ruling; the root `CLAUDE.md`
enforcement table gains a row for the new guard and amends the batching row; `docs/efficiency-tooling.md`
gains the row; `.claude/settings.json` wires the guard on the Agent matcher beside `escalation-hooks.sh`.

**FR-008 - nothing here is engine code.** The delta is `scripts/`, `.claude/`, `tests/tooling/`, docs
and this feature's directory; the route is DIRECT with the guard-script stamp from a green
`make hooks-test`.

## Success criteria

- **SC-001** (FR-001) - in the batching suite, two serial turns followed by a folded single call produce
  the notice, so do two followed by a backgrounded single call, and the block still passes a folded
  command at the bar.
- **SC-002** (FR-002) - on this feature's own second review round, if one is needed, the reviewer's
  report says it read the preamble's diff and the grep hits and names no file read end to end; failing
  that, the suite's second-dispatch case proves the rewrite.
- **SC-003** (FR-003) - the suite's first-dispatch, history-without-snapshot, no-feature, MODE 4 and
  MODE 1 cases pass, and the state directory is under the clone's `.git/`.
- **SC-004** (FR-004) - the suite's escape cases pass; the escape census classifies the token.
- **SC-005** (FR-005) - MODE 3 step 3 names the grep procedure; the ruling is quoted; the contract says
  the preamble is the tooling's.
- **SC-006** (FR-006) - `make hooks-test` green, the census rows present, `make quick` green.
- **SC-007** (FR-007) - the header, both table rows and the settings entry exist.
- **SC-008** (FR-008) - the delta touches no `l7r/**/*.py`; the push routes DIRECT.

## Decisions recorded

**D1 - a rewrite, not a context line.** The session's own proposal was a context line. The GM's
ruling is that instructions are not reliably followed and tooling is; a context line is an instruction
the session may not carry into its prompt, while a rewritten prompt reaches the reviewer whatever the
session wrote. So the preamble is prepended by the hook and placed FIRST, before the session's text.

**D2 - the diff base is a snapshot at dispatch, not a commit** (R4).

**D3 - the previous verdict is read from the subagent transcript, with the Review history as the
fallback** (R3). The reviewer's own words are what the next round confirms against; the contract says to
judge an item against the request, not against the session's summary of it, and the fallback is marked
as a summary so the reviewer knows which it holds.

**D4 - no branch of the new guard blocks, except the reason floor.** Every outcome is a rewrite, a
context line or silence, because each is free; the one refusal is the standard one for an escape with
no reason, which every guard carries.

**D5 - the block's shape test stays.** The notice is free; the block costs a round trip, and the hook's
own record says most early blocks landed on already-substantive calls before the shape test existed.
Only the notice changes.

**D7 - the notice drops the background exclusion with the shape test, on the GM's words.** The
session's own draft kept "not backgrounded" on the notice. The reviewer pointed out that the hook itself
treats backgrounding as part of the one shape judgment, and the GM approved "fire on any single call".
A notice on a backgrounded launch costs nothing and can only arrive earlier, so the exclusion is gone
from the notice and kept on the block.

**D8 - the other two modes are told apart by the prompt's text, not by a new field.** The Agent tool
carries no mode; the session's prompt names it (the contract's own headings are `MODE 1` to `MODE 4`,
and a plan review names `plan.md`). A word test on the prompt is the only discriminator a hook has, and
it defaults to the spec review, which is the common dispatch and the one whose cost was measured.

**D6 - the reviewer is not asked to ignore the session's prompt, only to answer it from the diff.**
A session may still ask a whole-spec question; the preamble says how to answer it without a re-read.
Removing the session's text would lose the request quotation and the round's context that only the
session has.

## Review history

- **Round 1 (2026-09-14), `spec-fidelity`: CHANGES REQUIRED**, four items, all applied: the rewrite
  discriminated MODE 2/3 from MODE 1/4 by the prompt's text, with the two modes passing untouched and
  their suite cases named (1, FR-002, FR-003, FR-006, SC-003, D8); FR-001 drops the background exclusion
  with the shape test, as the GM's words say (2, D7, SC-001); the round number counts within a pass that
  restarts at a recovered FAITHFUL, per the GM's 2026-09-12 cap ruling (3, FR-002); R1's sum corrected,
  the agents' durations and the session's waits stated as the two different quantities they are (4). The departure from a context line to a
  rewrite was ruled FAITHFUL, a strengthening within the GM's own reason.
