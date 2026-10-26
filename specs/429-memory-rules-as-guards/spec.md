# Feature 429: four rules that lived only in session memories, made into tooling

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-26

**Status**: Draft

**Affects**: tooling

**Approved**: the GM, 2026-10-26, "Sounds great. I approve all of that. So please do it end to end. Thanks."

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
  outside the clone; edit once they return; or stop them with TaskStop). An agent whose transcript has not moved for
  the stall bound is not counted live (`agent-stall-hooks.sh` reports it).
- **FR-002**: At the turn's end, a final message that asks the GM a question or puts a decision to him, with no
  `escalation-check` dispatched since his last message, is refused ONCE (per message) with the instruction to run the
  filter on the draft. The detector is narrow and measured against past final messages before it ships (its hit rate
  and a sample of its hits recorded in `research.md`).
- **FR-003**: An Edit, Write or NotebookEdit whose file is in `/host-l7r-repo/gm-assistant` outside its `.clones/`, and a
  Bash command whose write target (a redirection, `tee`, `sed -i`, the destination of `cp`/`mv`) is there, are refused
  with the clone and issue routes. A Bash refusal takes an escape with a reason, for the GM's explicit say-so.
- **FR-004**: `make map` ends with one line saying whether its manifest differs from HEAD; `make maps-moved` lists every
  pool manifest that differs from HEAD (or says none does).
- **FR-005**: Each guard has its test companion run by `make hooks-test`, proving it fires on the unfixed shape and
  passes the correct one; each records its firings (`guard_log`) and has its row in `docs/guards.md`; the dev-loop and
  tooling docs that stated these as rules to remember point at the tooling instead.

## Success Criteria

- **SC-001**: The 2026-09-27 shape (an engine edit with a review live) is refused in a test, and the edit passes once
  the review has finished (FR-001).
- **SC-002**: The 2026-10-25 shape (a final message putting two choices to the GM, no filter run) is refused once in a
  test; a report-only message and a message after a filter dispatch pass (FR-002).
- **SC-003**: An Edit in gm-assistant's main tree is refused and one in its clone passes, in a test (FR-003).
- **SC-004**: `make maps-moved` on a clone with one changed manifest names exactly that one (FR-004).
- **SC-005** (spec-wide): `make hooks-test` green with the four companions.
