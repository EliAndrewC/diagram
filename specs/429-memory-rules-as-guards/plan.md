# Implementation Plan: four rules that lived only in session memories, made into tooling (feature 429)

**Spec**: `spec.md` | **Request**: `request.md`

## Summary

Three guards and one printed comparison, each where the rule's moment is: an engine edit (PreToolUse on Edit, Write,
NotebookEdit), the turn's end (Stop, in `escalation-hooks.sh`), a write into gm-assistant's tree (PreToolUse on Edit,
Write, NotebookEdit and Bash), and the end of `make map`.

## Measured before planning (2026-10-26)

- **Live agents** (`research.md` R2): `meta.json` gains `"finished": true` on this harness, but most meta files on this
  machine predate the key, so a finished agent is also read from its transcript (last record an assistant `end_turn`).
  `agent-stall-hooks.sh pending` is not the test: a review mid tool call ends on an assistant `tool_use` record.
- **The question detector** (`research.md` R1, `measure/`): measured on past final messages against two independently
  labeled samples; the holdout's recall before fitting and its false alarms are the figures the guard rests on.
- **gm-assistant's tree**: `/host-l7r-repo/gm-assistant` is gm-assistant's main working tree; its clones live under
  `/host-l7r-repo/gm-assistant/.clones/`. `repo-safety-hooks.sh` refuses only git writes under `/host-l7r-repo` and
  says edits there "stay legal, the intake workflow needs them" - the intake writes `/host-l7r-repo/academic-sources/`,
  not gm-assistant, so the new guard is scoped to gm-assistant alone.
- **Pool manifests**: `git ls-files pool | grep json$` - 5 tracked manifests, one per hamlet.

## Constitution Check

Tooling only (no engine path): `scripts/hooks/`, `tests/hooks/`, the Makefile, `.claude/settings.json`, docs. Lands by
the DIRECT route; no map moves. XVIII: every guard has its test companion.

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T05 to T05 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T06 to T06 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->

## T07 - amendment 1: offers are not questions, but owe a significance test (FR-006, SC-006)

### T07 Approach (checklist part A)

1. **The goal, in the world.** The GM sees an offer only when the decision it hands back mattered, and never as a question.
2. **The constraints.** FR-006; FR-002's question branch unchanged.
3. **Where each comes from.** G: amendment 1 in `request.md`; O: `research.md` R3.
4. **Do they describe the world here?** Yes: R3, three-way labels.
5. **The order.** the detector's split, the refusal text, escalation-check's offer section, the suite, R3.
6. **The exits.** an offer-only message refused once with the significance instruction; an ask wins on a mixed message.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `tests/hooks/test-escalation-hooks.sh` section 10 green; R3's counts.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T07 Decisions

**D172 - one detector, two kinds of line; one filter, two instructions.** `hm_gm_question.classify` returns ask lines and
offer-only lines (an ask on the same line wins); `judge` prints `ask` or `offer` with the first line. An offer still owes
the once-per-message `escalation-check`, because the GM's threshold of significance is a judgment the filter makes
(its offer section: KEEP a decision that might otherwise have been floated as a question, CUT a routine one, cut a message
offering back most of its decisions down to the one or two that clear the bar). No count cap: a pattern cannot weigh
significance.
