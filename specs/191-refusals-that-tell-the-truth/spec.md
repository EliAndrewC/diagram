# 191 - Refusals that tell the truth

**Status**: draft
**Request**: [request.md](request.md) (the GM's words, verbatim)

## Why

Retiring `make reference` as a public rung (2026-09-06) left two PRINTED messages in engine
Python naming a target that no longer resolves. A refusal that sends a session to a command that
fails is the exact defect class that `tests/test_operations_registry.py` caught earlier the same
day with `citybudget`, and it is worse here: `_invocation.guard()` is the make-only guard, so its
message is the FIRST thing a session reads after being refused.

Reading the two sites found more rot than the report described. The make-only ladder in
`_invocation.py` is stale in **three** ways, not one:

| line | what it says | why it is wrong |
|---|---|---|
| `make reference    ~26 s` | names the retired rung | the target does not exist; `make reference` errors |
| `make quick        ~33 s` | states a duration | feature 162: a guard message may not say how long a command takes - it goes stale and was measured doing so |
| `make done ~75 s locked / ~4.5 min unlocked` | states durations AND cites the SCOPE LOCK | the scope lock was retired entirely by feature 185; "locked/unlocked" describes a mechanism that no longer exists |

**And the guard that was supposed to prevent the duration half does not look at this file.**
`tests/tooling/test_guard_message_durations.py` scans `SCRIPTS = REPO / "scripts"`. The make-only
guard has two halves - `scripts/make-only-hooks.sh` and `l7r/diagram/_invocation.py` - and only the
shell half is covered. That is why the Python half carries the forbidden text and a retired
feature's vocabulary while its sibling is clean. This is the same shape as the bug that started the
day: a rule censused over the surface where it was first written rather than over every place the
mechanism lives.

## Requirements

- **FR-001** `_invocation.guard()`'s ladder names only targets that resolve. `make reference` is
  removed from it.
- **FR-002** That ladder states no durations. The rule is feature 162's and already binds every
  shell guard; nothing about this message makes it an exception.
- **FR-003** That ladder contains no scope-lock vocabulary ("locked", "unlocked"), the mechanism
  having been retired by feature 185.
- **FR-004** `hamlet_floor.check()`'s empty-path message names a live target as the producer of the
  first roll record.
- **FR-005** `test_guard_message_durations.py` covers the Python guard messages as well as
  `scripts/`, so FR-002 cannot rot again in the place it just rotted. The set of covered files is
  DERIVED, not a hand-written roster (constitution X clause 14): the natural derivation is the
  modules `_invocation.OPERATIONS` and the guard surface already declare, not a list somebody
  maintains.
- **FR-006** Every target named in any message this feature touches is asserted to exist as a make
  target. The existing `test_operations_registry.py` proves this for the OPERATIONS registry; the
  same property is owed by prose that names a command.

## Out of scope, stated so it is not read in

- The gate slowdown. It is the other half of the GM's message and is an investigation, not a code
  change; it does not belong in a feature about message text.
- `specs/189`. The GM explicitly assigned it elsewhere: *"I will have the other session handle
  that."*
- Rewording the refusals beyond what FR-001..FR-004 require. The messages are well-written; three
  facts in them are stale.

## Decisions Recorded

- **D1 - the GM's docstring suggestion is DECLINED, on mechanism.** Recorded in full in
  [request.md](request.md). Both messages are runtime output; a docstring is not printed. Class:
  not a research question - a fact about the code.
- **D2 - the duration guard is WIDENED rather than the message exempted.** The alternative was to
  leave `_invocation.py` outside the guard and simply fix the text, which costs nothing today and
  re-rots the moment somebody edits it. Declined for that reason.
- **D3 - `make maps` is the replacement pointer, not `make _reference`.** `_reference` exists and
  works, but it was made internal ON PURPOSE hours earlier; a refusal that teaches sessions to type
  the internal name would undo that decision through the back door. `make maps` is public and does
  roll the reference alone after a failure.

## Success Criteria

- **SC-001** `grep -n "make reference" l7r/diagram/` returns nothing outside a comment that
  explains the retirement.
- **SC-002** Every command named in `_invocation.guard()`'s output resolves as a make target.
- **SC-003** `test_guard_message_durations.py` FAILS if a duration is planted in
  `_invocation.py`'s message - proven by planting one and watching it go red, per the add-a-guard
  rule.
- **SC-004** `make done` green, 100% coverage held.

## Review history

(to be filled by the `spec-fidelity` subagent before implementation - constitution XVI)
