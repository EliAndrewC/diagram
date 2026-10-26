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

<!-- plan-archive: T07 to T07 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
