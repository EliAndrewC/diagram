# Implementation Plan: What a Guard Block Costs, and What It Saves

**Feature**: 161-guard-block-economics | **Spec**: [`spec.md`](spec.md) | **Created**: 2026-08-30

## The mechanism this feature turns on, PROVED before it was planned

A `PreToolUse` hook in Claude Code 2.1.251 can do two things this project's twelve guards have never
used. Both were verified empirically against the installed harness (a throwaway settings file, a
throwaway hook and a `claude -p` run in the scratchpad), not read off documentation:

| capability | shape | verified result |
|---|---|---|
| **rewrite the command** | `{"hookSpecificOutput":{"hookEventName":"PreToolUse","updatedInput":{"command":"..."}}}`, exit 0 | the REWRITTEN command ran; the session never saw a refusal and spent no round trip |
| **speak to the model without blocking** | `{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"..."}}`, exit 0 | the model received the text verbatim alongside an allowed tool call |

Every guard in this repository is built out of exit code 2, which is the one mechanism that costs a
round trip. The GM's request is, in effect, a request to use the other two: **combine instead of
rejecting** (`updatedInput`) and **teach before failing** (`additionalContext`).

Neither field needs `permissionDecision`, so a hook can correct a command without granting it any
permission it did not already have, and the other eleven guards still run.

## Constitution Check

| principle | how this plan satisfies it |
|---|---|
| VI (verification before done) | every change is to a guard or the Makefile; each has a companion test script that `make hooks-test` runs as a gate phase, and the gate is the proof |
| X (100% coverage on pure logic) | the new logic lives in shell guards and `_hookmatch.py`; `scripts/test-*-hooks.sh` covers each branch, and each new assertion is proved to FIRE by removing the code and watching it go red |
| XII (research before a ruling) | done: `research.md` prices every decision from the run log and a transcript replay; nothing here is a guess |
| XIII (no known regressions) | baseline in a detached worktree before the first edit; `make hooks-test` and `make done` before the push |
| XVIII (a guard needs a companion test) | no assertion is retired without deleting its vectors; no behavior is added without new ones |
| XVI (no unrequested exception) | `spec.md` went to `spec-fidelity` before this plan existed |

## Phase 1 - the expensive-measurement guard (FR-001, FR-002)

`scripts/measure-hooks.sh`:

1. `BUDGET` default 2 -> 1, and the block message stops saying "the third". The message keeps naming
   `make cov-file`, `make quick` and `make test-file`, which is the part that gives the blocked
   session somewhere to go.
2. NEW: when an expensive measurement is ALLOWED and it is the first of a streak, the hook returns
   `additionalContext` carrying the batching reminder - what the run is about to cost (derived, see
   Phase 3), what the cheap loop is, and that the next one in this streak will be refused. Emitted
   once per streak: the state file already distinguishes the first from the rest.
3. The hook must therefore print JSON on stdout and still exit 0. Its existing block path (exit 2 +
   stderr) is untouched.

## Phase 2 - combine, do not reject (FR-003)

`scripts/gate-hooks.sh` loses the quick+done refusal and gains a rewrite:

- **Recognize** the shapes that are unambiguous: one command whose top-level segments (split on
  `&&`, `;`, `||`) contain a make invocation whose goals include `quick` AND another (or the same)
  invocation whose goals include `done`. `_hookmatch.py` already decides "which make targets does
  this command actually INVOKE" with command-position anchoring, quoted strings and heredocs blanked
  - the rewrite reuses that decision so a mention can never be rewritten.
- **Rewrite** by dropping the `quick` goal: `make quick done` -> `make done`; `make quick && make
  done` -> `make done`; a segment that becomes an empty make invocation is removed with its
  separator. Everything else in the command (a `cd`, a `git commit` after the gate, environment
  assignments) is preserved verbatim.
- **Refuse to be clever**: if the command does not match that shape exactly - a pipe, a redirect, a
  subshell around the pair, a `make quick` with arguments the rewrite would have to interpret
  (`ALL=1`, `FILE=`) - the hook allows it UNCHANGED. It never blocks and never guesses. The
  fallback costs one warm `quick` (4.1 s); a wrong rewrite costs a session its command.
- **Say what it did**: `additionalContext` names the rewrite in one line, so the session's next turn
  reads correct output rather than wondering where `quick` went.
- The `-k`-subset block in the same file is untouched.

## Phase 3 - the numbers stop being hardcoded (FR-005)

A new `scripts/_gatecost.py`: given a make target, print the median seconds of its recent recorded
runs from `dev/run-log/` (green runs only, most recent N, both the clone's log and main's), or print
nothing when the log cannot answer. The guards call it when they compose a message, and the Makefile
uses it for the `help` line and the `bypass-audit` prompt.

Known stale strings to replace, all found while planning: `gate-hooks.sh` ("~70 s with scope
locked", "~30 s of the same tests"); `make-only-hooks.sh` ("quick ~33 s", "reference ~26 s", "done
~75 s locked / ~4.5 min unlocked"); the `help` target ("done ~5.5min"); the `bypass-audit` prompt
("~5.5 min"). A test asserts no guard message contains a hardcoded second- or minute-count for a
make target.

## Phase 4 - a guard firing is recorded (FR-006)

`scripts/_guardlog.sh`, sourced by the guards: `guard_log <guard> <event> <detail>` appends ONE file
to `~/.claude/guard-log/` (`<utc>-<pid>.json`: guard, event `blocked|escaped|rewrote|reminded`,
session, cwd, the first 200 characters of the command).

**Why host-wide and not `dev/guard-log/` in the clone**: a hook fires for commands that name no
clone at all, so it cannot reliably decide which working tree an entry belongs to, and writing into
main's tree is forbidden. The cost, recorded rather than hidden: the log is not versioned and a
container rebuild loses it. The declined alternative was a per-clone directory, which would have
needed the hook to guess a tree.

`make audit` gains a per-guard census: firings, escapes, escape rate, oldest and newest entry.

## Order, and what each step is verified with

1. baseline in a detached worktree (`git worktree add --detach /tmp/base161 HEAD`)
2. Phase 4 (the firing log) first, so every later phase can record itself - `scripts/test-guardlog.sh`
3. Phase 3 (derived numbers), `scripts/test-gatecost.sh` + the no-hardcoded-number assertion
4. Phase 1 (the measurement guard), `scripts/test-measure-hooks.sh` extended
5. Phase 2 (combine, do not reject), `scripts/test-gate-hooks.sh` extended, vectors for the retired block deleted
6. `make hooks-test`, then `make done`, then the push

Each guard change is proved to FIRE by deleting the code and watching its test go red, per the
project's rule for adding a guard.

## What this plan deliberately does NOT do

Reorder `make done`'s phases so the 1.8 s of static checks run ahead of the 29 s reference roll.
It is measured, it is cheap, and `spec-fidelity` ruled it unrequested in round 2 - the GM's request
is about what a guard does when it fires. It is written up as `research.md` R7 and goes to the GM as
its own question.
