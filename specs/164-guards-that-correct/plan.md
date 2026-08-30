# Implementation Plan: Guards That Correct Instead of Refusing

**Feature**: 164-guards-that-correct | **Spec**: [`spec.md`](spec.md) | **Created**: 2026-08-30

## The mechanism, already proved

Feature 162 established and this feature re-verified, against the installed harness rather than a
document:

| capability | shape | verified |
|---|---|---|
| rewrite the command | `hookSpecificOutput.updatedInput` at exit 0 | the rewritten command ran; no round trip |
| speak to the model | `hookSpecificOutput.additionalContext` at exit 0 | quoted back verbatim |
| rewrite an EDIT | the same, with `new_string` replaced | the file on disk carried the correction |
| context on a READ | the same, on the Read tool | quoted back verbatim |
| see how a command will run | `run_in_background` is in the Bash payload | `{"command", "description", "run_in_background"}` |

## Constitution Check

| principle | how this plan satisfies it |
|---|---|
| VI | every change is a guard or its companion; `make hooks-test` is the proof, and it is a gate phase |
| X | new logic lives in `_hookmatch.py` (unit-testable, no shell) and the guards' own suites cover each branch |
| XII | done: `research.md` prices every conversion from 280 recorded firings |
| XIII | baseline: `make hooks-test` green on the unmodified clone before the first edit |
| XIV | three defects found while auditing are fixed here: `make-only`'s bare-pytest message gives a false reason and omits the one-file target; `measure-hooks` counts a mention as a run; `house-style` cannot tell a word being USED from a word being NAMED |
| XVI | `spec.md` went to `spec-fidelity` before this plan existed, and its round-1 findings are applied |
| XVIII | no assertion is retired without deleting its vectors; every new behavior gets vectors proved to fire |

## Phase 1 - the shared decisions move into `_hookmatch.py`

Two pure functions, tested with plain strings, no shell:

- `as_make_target(cmd)` - a bare pytest of ONE test file becomes `make test-file FILE=<path>`, or
  `None` when the shape is not exactly rebuildable (a `-k` filter, a coverage or plugin flag, a
  second path, a directory, a pipeline). Preserves a leading `cd ... &&` and this project's
  `( cd <abs> && ... )` convention verbatim. Drafted and exercised against fifteen shapes already.
- `bracket_pattern(cmd)` - a `pgrep -f <literal>` / `pkill -f <literal>` becomes the bracket form.

Both live beside `combine()` from 162, for the same reason: a decision a guard makes about a command
belongs where it can be tested without bash quoting in the way.

`no-poll` and `measure` additionally start asking `_hookmatch.py` whether their shape is INVOKED
rather than merely mentioned, exactly as `gate-hooks` has since 2026-08-29.

## Phase 2 - the four rewrites

| guard | today | after |
|---|---|---|
| `make-only` | refuses a bare pytest, naming the gate targets and giving coverage as the reason | rewrites one-file runs to `make test-file`; every other shape keeps the refusal, with the TRUE reason and the one-file target named |
| `no-poll` | refuses a literal `pgrep -f` | rewrites it to the bracket form it already recommends |
| `pair` | refuses `make done` when a review is owed | rewrites it to `make verify`, with the line telling the session to dispatch the review in the same turn |
| `house-style` | refuses an edit containing an em-dash or a British spelling | corrects the payload, EXCEPT on any file recording the GM's own words, where it still refuses |

`house-style`'s correction table holds only substitutions with no judgment in them. The British verb
form of "practice" is excluded - which of the two spellings is right there depends on the sentence -
and stays a refusal.

**A word inside a backtick code span is a MENTION, not a use.** This plan's first draft was refused
by that guard for NAMING the excluded word as an example, which is the third mention-not-invocation
false positive this session (after `no-poll` on the spec text and `measure-hooks` on prose). The
guard's exemption list covers the files that must quote the RULE, but not a spec or plan discussing
it - and a backtick span is exactly how this repository's prose marks a token it is talking about.

The GM-writing exemption is extended to `specs/*/request.md` BEFORE any correction is computed.

## Phase 3 - the two teach-first conversions

- `guard-file` returns its `GUARD_EDIT_OK` line as `additionalContext` on a READ of a guard file.
  The refusal stays as the backstop.
- `batching` attaches its playbook one turn below the threshold. The window, the backoff and the
  block are untouched.

## Phase 4 - recording, and the suites

Every conversion calls `guard_log` (feature 162) with `rewrote` / `reminded` / `blocked`, and every
suite isolates `GUARD_LOG_DIR` for the whole file and asserts it never dropped that isolation
(feature 162 T16). Each new assertion is proved to FIRE by removing the code it guards.

## Order

1. baseline `make hooks-test` on the unmodified clone
2. Phase 1, with its unit tests
3. Phase 2 guard by guard, each with its companion suite green before the next
4. Phase 3
5. `make hooks-test`, then `make done`, then the push

## What this plan deliberately does NOT do

- Permit a backgrounded `sleep` loop (`research.md` R5) - it changes what the guard forbids.
- Retune `discard`, whose 5-of-5 escape rate is a question for the GM.
- Convert any Makefile refusal: R6 enumerates all ten and finds one convertible, and that one
  (`review-gate` refusing the number claim) is R4's question for the GM rather than a change here.
