# Feature 429: four rules that lived only in session memories, made into tooling

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-26

**Status**: Done (amendment 1 landed 2026-10-26)

**Affects**: tooling

**Approved**: the GM, 2026-10-26, "Sounds great. I approve all of that. So please do it end to end. Thanks."

**Amendment 1** (the GM, 2026-10-26, in `request.md`): offers are not questions - *"saying that you made a decision but
then offering to reverse it ... without that actually being a question that is floated for me, that is all perfectly fine"*
- but *"that offer should only be made if it crosses a certain threshold of significance"*. FR-006, SC-006.

**Input**: `request.md` (the GM's request and the four guards the audit proposed, verbatim).

## Why

The GM retired project memories on 2026-10-26: *"it empirically does not work to simply tell you to remember them ...
That is why our tooling must enforce the correct behavior every time."* The audit of the 128 memories found four rules
that a memory held and no tool enforced, each with an incident behind it:

1. **An engine edit while a review runs.** Feature 261 (2026-09-27) edited engine code while map reviews were still
   running, twice; every still-running review then recorded NOT-REVIEWABLE, because its verdict is keyed to the engine
   it reviewed, costing a whole extra round. Feature 317 repeated it with a docstring edit. The memory said a guard
   was "proposed, not built".
2. **A question to the GM that no filter read.** `escalation-hooks.sh` arms only when a `settlement-review`,
   `building-review` or `size-audit` is dispatched. On 2026-10-25 a feature 417 report asked the GM whether a finding
   applied and which of two placements to take, with no review behind it; nothing fired, and the GM answered *"that is
   the kind of question that our processes are supposed to answer"*.
3. **An edit in gm-assistant's main tree.** On 2026-10-20 a session left setting-note edits uncommitted in
   `/host-l7r-repo/gm-assistant`, which refused every gm-assistant push until that session cleaned up (diagram#10).
   `repo-safety-hooks.sh` refuses git WRITES under `/host-l7r-repo`; an Edit or Write there passes.
4. **"Did this wave move a map?" answered from a scratch copy.** Feature 328 wave 68 (2026-10-09) copied the manifests
   after a gate test had already regenerated them and recorded four hamlets unchanged while Sawada's board had moved
   76 degrees. The right comparison is against HEAD, and nothing prints it.

## User Scenarios & Testing

### US1 - an engine edit waits for the reviews it would invalidate (P1)

A session dispatches review agents and, before they return, edits an engine file. The edit is refused, naming the
reviews still running and saying to draft the fix outside the clone until they return. Once every review has
returned, the same edit passes.

**Acceptance**: with a live review agent of a map-review type in this session, an Edit of `l7r/.../x.py` or a pool gen
or manifest in the clone is refused; a docstring-only edit is refused too; an edit of a doc, a test or a script passes;
after the agent finishes, the edit passes.

### US2 - a question for the GM is filtered before the turn ends (P1)

A session ends a turn with a question or decision for the GM and has not run `escalation-check` on it this turn.
The turn end is refused once, telling it to run the filter on its draft; a turn whose final message asks the GM
nothing passes untouched.

**Acceptance**: the stop check flags a final message that asks the GM to choose or decide, passes one that only
reports, passes when an `escalation-check` was dispatched since the GM's last message, and blocks at most once per
final message.

### US3 - gm-assistant's main tree is not edited from here (P2)

An Edit, Write or a shell write to a file in `/host-l7r-repo/gm-assistant` is refused with the two compliant routes:
a gm-assistant clone, or the wording handed over on an issue. A file inside a gm-assistant clone
(`/host-l7r-repo/gm-assistant/.clones/<name>/...`) and every other path under `/host-l7r-repo` are untouched by this guard.

### US4 - a reroll says whether it moved the map, against HEAD (P2)

`make map` ends by saying whether the map's manifest differs from HEAD; `make maps-moved` lists every pool manifest
that differs from HEAD, the comparison a wave records.

## Requirements

- **FR-001**: An Edit, Write or NotebookEdit of an ENGINE path (the one list, `l7r/diagram/ci/delta.py` `is_engine()`)
  inside the session's clone is refused while an agent of a map-review type (`pair-hooks.sh`'s `REVIEW_AGENTS_RE`)
  launched by this session has not finished. The refusal names the running reviews and the compliant route (draft
  outside the clone; edit once they return; or stop them with TaskStop). Every map-review agent this session launched
  that has not FINISHED counts as live, stalled or not; the refusal names a stalled one with the stall hook's route
  (TaskStop, then `agent-stall-hooks.sh ack`), after which the edit passes.
- **FR-002**: At the turn's end, a final message that asks the GM a question or puts a decision to him, with no
  `escalation-check` dispatched since his last message, is refused ONCE (per message) with the instruction to run the
  filter on the draft. The detector is narrow and measured against past final messages before it ships: its hit rate,
  a sample of its hits, and its RECALL - how many of an independently labeled sample of past final messages that put a
  question or decision to the GM it catches, the 2026-10-25 feature 417 message among them - recorded in `research.md`.
- **FR-003**: An Edit, Write or NotebookEdit whose file is in `/host-l7r-repo/gm-assistant` outside its `.clones/`, and a
  Bash command whose write target (a redirection, `tee`, `sed -i`, the destination of `cp`/`mv`) is there, are refused
  with the clone and issue routes. A Bash refusal takes an escape with a reason, for the GM's explicit say-so.
- **FR-004**: `make map` ends with one line saying whether its manifest differs from HEAD; `make maps-moved` lists every
  pool manifest that differs from HEAD (or says none does).
- **FR-005**: Each guard has its test companion run by `make hooks-test`, proving it fires on the unfixed shape and
  passes the correct one; each records its firings (`guard_log`) and has its row in `docs/guards.md`; the dev-loop and
  tooling docs that stated these as rules to remember point at the tooling instead.

- **FR-006** (amendment 1): The detector tells an ASK (a question, a choice, or a decision or go-ahead the GM must give
  before the work goes on) from an OFFER (a decision already made or work already done, with an offer to reverse or extend
  it). An offer is not a question and is never a GM review item. Because an offer is due only when it clears a threshold of
  significance - a decision that might otherwise have been floated as a question - a final message carrying offers owes the
  same once-per-message `escalation-check` pass, whose contract judges each offer KEEP (significant) or CUT (a routine
  decision), so that a message offering to reverse every decision is cut back. The detector is re-measured against labels
  that tell the two apart.

## Success Criteria

- **SC-001** (FR-001): The 2026-09-27 shape (an engine edit with a review live) is refused in a test, and the edit passes once
  the review has finished; a stalled review still refuses until it is stopped and acked.
- **SC-002** (FR-002): The 2026-10-25 shape (a final message putting two choices to the GM, no filter run) is refused once in a
  test; a report-only message and a message after a filter dispatch pass.
- **SC-003**: An Edit in gm-assistant's main tree is refused and one in its clone passes, in a test (FR-003).
- **SC-004**: `make maps-moved` on a clone with one changed manifest names exactly that one (FR-004).
- **SC-006** (FR-006): On three-way labeled samples (ASKS / OFFER / NONE), recorded in `research.md` R3, the detector
  separates asks from offers, and a test shows an offer-only message refused once with the significance instruction and an
  ask refused with the question instruction.
- **SC-005** (FR-005): `make hooks-test` green with the three guard suites (engine-freeze, gm-tree, escalation section 9), `tests/tooling/test_maps_moved.py` green in the gate's tooling tree, and each guard's row in `docs/guards.md`.

## Review history

- spec-fidelity round 1 (2026-10-26): CHANGES REQUIRED - (1) FR-001's stall carve-out (a review agent unmoved for the stall
  bound not counted live) ruled NOT LEGITIMATE against "no engine edits while a review is running": a slow review looks the
  same, TaskStop already gives the route, and the pairing guard counts pending agents "stalled or not"; count them live and
  name the stalled ones with the TaskStop route; (2) FR-002's measurement records only the detector's hits; add how many
  past final messages that put a question or decision to the GM it catches, the 2026-10-25 feature 417 message among them.
  FR-003's Bash escape (the GM's explicit say-so) ruled LEGITIMATE. Both changes made: FR-001 counts every unfinished
  review live, SC-001 adds the stalled case; FR-002 adds the recall measurement.
- spec-fidelity round 2 (2026-10-26): FAITHFUL - (1) RESOLVED: FR-001 counts every unfinished map-review agent live,
  stalled or not, with TaskStop then ack as the route, and SC-001 tests the stalled case; "not finished" is stricter than
  round 1's suggested `pending` (which reads a review mid tool call as finished, R2) and accepted; (2) RESOLVED: R1
  records recall against two independently labeled samples (holdout 9 of 11 before fitting, 0 false alarms in 89; the
  feature 417 message caught), re-run by quote-matching since the uncommitted corpus has grown (8 of 8, 10 of 11, 0 false
  alarms reproduced). For the plan review: D167's two-day age bound is not in FR-001 or R2; T06 has no FR.
  Applied after: the labels are keyed by the sha1 of each message (reproduced on a 1,435-message corpus, 8 of 8 and 10 of
  11, 0 false alarms); the age bound was struck by the plan review; spec-lint's FR/SC pairing fixed on SC-001 and SC-002 (wording
  only); SC-005 reconciled with the plan review's note (T04 is a report, its test in the tooling tree).
- spec-fidelity-verify round 1 of amendment 1 (2026-10-26): FAITHFUL - FR-006 matches amendment 1: an offer is not a
  question and never a GM review item; the once-per-message escalation-check pass enforces only the GM's significance
  threshold ("except insofar as ... threshold of significance"), with KEEP for a decision that might otherwise have been
  floated as a question and CUT for routine ones. R3 re-run on 1,449 messages: asks 18 of 19, offer 1 of 1, 0 false
  alarms in 161; R1's 8 of 8 and 10 of 11 reproduce. Carry-overs resolved (sha1 keys, R1 label committed, age bound
  struck). Non-blocking: R1's "as shipped" row still names "if you want ... I", which R3 moved to OFFER; SC-005's change
  was more than wording. Both applied.
