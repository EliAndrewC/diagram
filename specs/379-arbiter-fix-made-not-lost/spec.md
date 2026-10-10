# Feature 379: An arbiter's tooling fix is made, not lost

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-10
**Status**: In progress

**Affects**: review process, tooling

**Approved**: the GM, 2026-10-10, "I agree with your recommendations around the arbiter tooling fixes as well, by the way. So yeah, please go ahead and implement that as well."

**Input**: `request.md` (the GM, 2026-10-10)

## Why

On 2026-10-10 the "Diagram research" session ran two `make done` gates in one clone at once. Both went red together, the
red-gate tripwire fired twice, and the round arbiter (feature 375) ruled twice - recommending, in its ruling's prose, "the gate
should refuse to start while another make done is running in the same clone. File that as a tooling row". Nothing filed it; the
recommendation lived only in `arbiter.jsonl`'s `what` text, and the GM heard of it only because an hourly check read the
ruling. The longer a session runs, the likelier such a recommendation is lost - and an arbiter's tooling fix is exactly the
high-value kind: it sees a loop from outside, when a tooling gap is visible.

## Requirements

- **FR-001 The fix is a field.** The round arbiter states a recommended tooling fix as its own field of the ruling
  (`tooling_fix`: one sentence, or absent), never only in its prose; its contract says so, and when to give one. A
  `process-fault` ruling always carries its fault as a `tooling_fix`. The contract no longer tells anyone to "file" a tooling
  row under any ruling: the fix goes in `tooling_fix` (spec review round 1: "File that as a tooling row" is how the first was lost).
- **FR-002 Made soon, held by the tooling.** `make arbiter-ruled` records a `tooling_fix` as an OPEN item of the active
  feature. `make tick` refuses while the feature has an open item, naming it: the fix is made, with its test, in the feature
  the session is working on, and the item is closed with `make arbiter-fix-done ID= NOTE="<what was built, its test>"`. An
  open item is made or declined, never filed. The GM sees every one: the ruling's GM-review row carries its `tooling_fix`,
  and `make arbiter-fix-done` adds what was built and its test to that review, as a decline does its reason ("that is the
  kind of thing that I would want to know about").
- **FR-003 An overhaul goes to the GM, never inline, never a silent feature.** A fix too large to make inline - one that
  overhauls a process rather than mending a tool - is declined with `make arbiter-fix-declined ID= REASON="<why it is an
  overhaul>"`, which writes a row of the GM's review (`make gm-review`, feature 375 FR-012). Nothing is filed as a feature
  without the GM's say-so, and the session never stops to ask: the decline is the GM's to review after landing.
- **FR-004 The closing check holds it too.** A feature does not close (feature 375's closing check) with an open item.

## Success criteria

- **SC-001** (FR-001, FR-002, FR-003, FR-004) Replaying 2026-10-10's research-session ruling: the recorded `tooling_fix` is an
  open item; `make tick` refuses until it is done or declined, and so does the closing check at the push; a decline, and a
  fix made, are each on the GM's review.
- **SC-002** (FR-002, FR-004) Each refusal has a test that fails on today's code.

## Review history

- spec-fidelity, Mode 2, round 1 (2026-10-10): CHANGES REQUIRED. Applied:
  - FR-001: a `process-fault` ruling's fault is its `tooling_fix`, held like any other; the contract stops saying "file".
  - FR-002: the GM-review row carries the fix, and a fix made adds what was built and its test to the GM's review.
- spec-fidelity-verify, Mode 3, round 2 (2026-10-10): FAITHFUL - both round 1 items resolved.
