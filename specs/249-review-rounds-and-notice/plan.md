# Plan - 249 review rounds read the diff, and the notice speaks on any single call

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **XVIII**: every guard ships with its companion; the new guard has `test-review-round-hooks.sh`,
  the batching change a new case in its suite, and `make hooks-test` runs both as a gate phase.
- **VI**: `make hooks-test` and `make quick` green before the push.
- **X**: no engine code; the new hook is one file well under the bar.
- **XVI**: spec-fidelity before code; this plan reviewed (MODE 4) before any tick.
- **Route**: `scripts/`, `.claude/`, `tests/tooling/`, docs only -> DIRECT, with the guard-script stamp.
- **Guard files**: `batching-hooks.sh`, its suite and the new hook are guard files - every edit carries
  `GUARD_EDIT_OK` with the reason.

## Design

- **P1 `batching-hooks.sh`**: the notice condition loses `&& is_recon_call`; the block condition keeps it.
  Suite case 2c: two serial turns, then a Bash payload whose command contains `;` - the notice is present
  and the call is allowed.
- **P2 `review-round-hooks.sh pretool`** (bash + one python block, the `escalation-hooks.sh` shape):
  parse the payload (tool, subagent type, prompt, transcript path, session id, cwd); exit 0 unless
  `spec-fidelity`; feature dir = first `specs/NNN-slug` in the prompt; clone = `clone-sync-hooks.sh
  resolve` on the payload, else `git rev-parse --show-toplevel` from the payload's cwd; state =
  `<clone>/.git/review-round/<dir>/` holding `snapshot/` and `round`. Escape first: `REVIEW_ROUND_OK`
  substring in the prompt -> reason via `_hm_escape.py escape-reason` on the prompt text; no reason ->
  the standard refusal; with one -> refresh the snapshot, log `escaped`, exit 0. No snapshot -> copy the
  directory (text files), round=1, log `permitted/first-round`; if `spec.md`'s Review history has a
  round entry, also emit the context line and log `reminded/history-without-snapshot`. Snapshot present
  -> `diff -ru snapshot dir`, previous verdict from `${transcript_path%.jsonl}/subagents/agent-*.jsonl`
  (newest whose first record's content names the dir and whose last record's text carries FAITHFUL or
  CHANGES REQUIRED), else the last Review history bullet marked as a summary; emit `updatedInput` with
  the preamble prepended to the prompt and every other tool_input field unchanged, plus one line of
  `additionalContext` naming the round; refresh the snapshot; round+1; log `rewrote/mode-3-preamble`.
- **P3 the preamble**: a fixed heading naming the mode, the round and the feature; the rule in one
  sentence with the GM's date; the previous verdict under its own heading (or the marked fallback);
  the diff under its own; "The session's prompt follows" and then the prompt.
- **P4 the suite**: a fixture repo with `specs/301-fixture/spec.md`, a fake subagents dir with one
  transcript whose first line names the dir and whose last carries `CHANGES REQUIRED`, payloads built
  with `transcript_path` pointing at the fixture; the cases FR-006 lists; the guard log isolated as
  every recording suite does.
- **P5 the census**: rows `("review-round", spec-fidelity dispatch naming no feature, "permitted",
  "no-feature")` and the escape cases; `REVIEW_ROUND_OK` classified `command` with the agent-prompt
  exclusion wording of `ESCALATION_OK`.
- **P6 the contract**: MODE 3 opening and step 3 restated per FR-005.
- **P7 the record**: hook header, `CLAUDE.md` rows, `docs/efficiency-tooling.md` row, settings entry.
