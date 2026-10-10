# Implementation Plan: no feature is filed without the GM's approval (feature 377)

**Spec**: `spec.md` | **Request**: `request.md` | **Model**: `conflict-marker-hooks.sh` (feature 241): a commit-time guard
on what a `git add` / `git commit` would stage, with its decider in `scripts/hooks/lib/`.

## Summary

One guard and one gate check, both reading one definition of the approval line:
- **The guard.** `scripts/hooks/feature-approval-hooks.sh` refuses at `git add` and `git commit` (FR-002, FR-005,
  FR-006), with its decider in `scripts/hooks/lib/hm_approval.py`.
- **The push backstop.** spec-lint gains a check on the line's form (FR-004).
- **The text.** The guidelines, `make claim`'s output and spec-fidelity's contract (FR-007, FR-009).

Everything is tooling, so every task is `research: rendering`. No engine file changes, so the landing is DIRECT,
stamped by `make hooks-test` and the tooling tests.

## Technical Context

- **Code.** Bash guards under `scripts/hooks/`, a stdlib Python decider under `scripts/hooks/lib/`, and spec-lint
  under `scripts/gates/`.
- **Tests.** A suite `tests/hooks/test-feature-approval-hooks.sh`, run by `make hooks-test`, which drives the REAL
  hook with a REAL payload, over a REAL git tree and a fixture transcript. spec-lint's case goes in
  `tests/tooling/test_spec_lint.py`.
- **A hard limit of this session.** The guards run from the mirror (`/diagram/scripts/hooks/`), so the new guard
  fires in no session until it lands. Its proof is the suite. After landing, the first claim of a new feature shows
  it live.

## Performance bookends

N/A: no generator change. The guard runs on every Bash call, so its cost is kept to the cheap bail-out D6 describes.

## Constitution Check

- **I-V**: N/A - no UI, no pool content, no SOURCE blocks.
- **VI (performance)**: N/A for maps. The per-call cost is a `case` on the command string, plus python only for a
  git add/commit (D6).
- **X (coverage)**: the scripts are tested to the project's habit: every branch the guard takes has a suite case.
- **XII (research)**: N/A - no physical decision.
- **XIII (no known regressions)**: `make hooks-test` and the tooling tests are green before and after.
- **XVI (the literal thing)**: every FR is built as written. The mechanisms chosen are the decisions below.

## Decisions

**D1 - One definition of the line.** `hm_approval.py` holds the form as one regex:
`^\*\*Approved\*\*: the GM, (\d{4}-\d{2}-\d{2}), "(.+)"\s*$` on a line of its own, in `spec.md`. It also holds the
first number the rule covers, `FIRST = 377`, and the three-word minimum. spec-lint imports it, adding
`scripts/hooks/lib` to `sys.path` as the scripts' own convention says, so the commit check and the push check cannot
drift apart.

**D2 - What counts as the GM's message.** The guard reads the transcript path from the hook payload's
`transcript_path` and takes two kinds of record:
- **A typed prompt.** A `user` record with string content, not `isMeta`, whose `origin.kind` is `human` or whose
  `promptSource` is `typed`. A record with neither field (an older Claude Code) counts only when its `entrypoint` is
  not an SDK one. Measured on this session's own transcript (2026-10-10): the GM's four prompts carry
  `origin.kind=human` and `promptSource=typed`; the session-name reminder is `isMeta`; and a headless page session's
  first prompt is `promptSource=sdk`, `entrypoint=sdk-cli`.
- **A message the GM sent mid-turn.** A `queued_command` attachment whose `origin.kind` is `human`, read from its
  `prompt`. The plan review measured 73 such messages in the last 40 transcripts, 41 of them reaching no `user`
  record, one of them "Yes, please go ahead and file this as a feature". Task notifications, peer relays and
  auto-continuations carry other origins and do not count.
- **The GM's answer to a question.** The `tool_result` of an `AskUserQuestion` call (matched by `tool_use_id`), when it
  is an answer: the record's `toolUseResult.answers`, or the "Your questions have been answered" preamble. A declined
  question is the harness's note, not the GM's words. The text holds the question and the picked answer, so a quote of
  the two together (`"<question>"="<answer>"`) matches it.

Text is normalized before the match: runs of whitespace become one space, and curly quotes and apostrophes become
straight ones. The quote must be a substring of one such message, at least three words long.

**D3 - What the command would stage** is `hm_conflict.staged_by(cmd, cwd)`, the conflict guard's own parser, reused
whole. Of those paths the guard keeps `specs/<NNN>-<slug>/spec.md`.

**D4 - NEW.**
- **NEW**: the path is absent from HEAD, is not the target of a staged rename (`git diff --cached -M --name-status`),
  and is not a renumber: a `specs/*-<same slug>/spec.md` in HEAD that has LEFT, gone from the working tree or with its
  deletion staged. A same-slug spec beside one still in place is a copy, and new (plan review, round 1).
- **The file to be committed** is the working-tree file, which is what `add` and `commit -a` take. A plain `commit`
  takes the index copy (`git show :<path>`).

**D5 - Refusals.** Exit 2, with the check that failed (no line / too short / not among the GM's messages), the exact
line to add, and "ask the GM in this session; the guard reads the GM's own messages". The refusal is logged through
`guard_log`. There is no escape token (FR-006). The suite pins the refusal's text (FR-005).

**D6 - Cost.** The same bail-out as the conflict guard: a `case` that needs `git` and `add` or `commit` in the
command, then `specs/` in what would be staged, before any transcript is read. A Bash call that is not a git
add/commit pays one `case`.

**D7 - The push backstop**, as spec-lint check 6 (`check_approval`): for a spec directory numbered `FIRST` or above,
the `spec.md` must hold a line of D1's form whose quote has at least three words. It runs on every touched spec,
like check 2, with or without a `tasks.md`. A landed spec is judged on what the push introduces, as spec-lint
already does.

**D8 - The text.**
- **CLAUDE.md.** The development-workflow bullet is rewritten: ask the GM before filing a feature; propose in the
  final message; prefer reopening the source feature. The guard table gains a row.
- **`docs/spec-kit-and-reviews.md`** gets a section with the GM's words. **`docs/guards.md`** gets the guard's record.
- **`make claim`** prints the line's form after a claim.
- **`.claude/agents/spec-fidelity.md`**, Mode 2, gains the subject check (FR-009).
- **Registration.** `.claude/settings.json` registers the hook beside `conflict-marker-hooks.sh`. It is a guard file,
  so the edit carries `GUARD_EDIT_OK`.

## Project Structure

```text
scripts/hooks/feature-approval-hooks.sh        new - the guard
scripts/hooks/lib/hm_approval.py               new - the decider and the one definition of the line
scripts/gates/spec-lint.py                     check 6
scripts/claim-feature.py                       prints the line's form
tests/hooks/test-feature-approval-hooks.sh     new - the suite
tests/tooling/test_spec_lint.py                check 6's cases
.claude/settings.json                          the registration
.claude/agents/spec-fidelity.md                the subject check
CLAUDE.md, docs/spec-kit-and-reviews.md, docs/guards.md
```
