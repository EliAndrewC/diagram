# Feature 379: An arbiter's tooling fix is made, not lost

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-10
**Status**: In progress

**Owed at**: now

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
  (`tooling_fix`: one sentence, or absent), never only in its prose; its contract says so, and when to give one.
- **FR-002 Made soon, held by the tooling.** `make arbiter-ruled` records a `tooling_fix` as an OPEN item of the active
  feature. `make tick` refuses while the feature has an open item, naming it: the fix is made, with its test, in the feature
  the session is working on, and the item is closed with `make arbiter-fix-done ID= NOTE="<what was built, its test>"`.
- **FR-003 An overhaul goes to the GM, never inline, never a silent feature.** A fix too large to make inline - one that
  overhauls a process rather than mending a tool - is declined with `make arbiter-fix-declined ID= REASON="<why it is an
  overhaul>"`, which writes a row of the GM's review (`make gm-review`, feature 375 FR-012). Nothing is filed as a feature
  without the GM's say-so, and the session never stops to ask: the decline is the GM's to review after landing.
- **FR-004 The closing check holds it too.** A feature does not close (feature 375's closing check) with an open item.

## Success criteria

- **SC-001** (FR-001, FR-002, FR-003, FR-004) Replaying 2026-10-10's research-session ruling: the recorded `tooling_fix` is an
  open item; `make tick` refuses until it is done or declined; a decline is a GM-review row.
- **SC-002** (FR-002, FR-004) Each refusal has a test that fails on today's code.
