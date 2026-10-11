# Feature 379: An arbiter's tooling fix is made, not lost

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-10
**Status**: In progress - amendment 1 (a tooling fix lands alone, mid-feature); the original FR-001 to FR-004 landed 2026-10-10

**Amendment 1 approved**: the GM, 2026-10-10, "yes please"

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

### Amendment 1 - a tooling fix lands alone, mid-feature (`request.md`, Amendment 1)

- **FR-005 Tooling lands on its own.** A session whose feature is in progress lands a commit's TOOLING - the proposal's
  `scripts/`, `tests/` and the agent instruction files (`.claude/agents/`, `.claude/skills/`, any `CLAUDE.md`), plus the
  wiring a `scripts/` fix needs to take effect, which is the session's reading of "tooling": the `Makefile` (its targets),
  `.claude/settings.json` (hook registration) and `docs/make-targets.html` (generated from the Makefile) - on main by itself,
  while the feature's other work stays in the clone until the feature closes as today. It lands on top of the latest main,
  through the checks a push of that change runs - and any test it lands is run there, so a test that needs work not yet
  landed is refused rather than breaking main - with no history rewritten and no local branch. A change to any other path
  is refused, naming it; so is one that does not apply cleanly onto main.
- **FR-006 The arbiter's fix is landed, not only made.** `make arbiter-fix-done` (FR-002) refuses until the fix's test is on
  main as it is in the clone, naming the landing command: a fix made but held in one clone leaves every other session on
  the misfire it mends.

## Success criteria

- **SC-001** (FR-001, FR-002, FR-003, FR-004) Replaying 2026-10-10's research-session ruling: the recorded `tooling_fix` is an
  open item; `make tick` refuses until it is done or declined, and so does the closing check at the push; a decline, and a
  fix made, are each on the GM's review.
- **SC-002** (FR-002, FR-004) Each refusal has a test that fails on today's code.
- **SC-003** (FR-005) In a fixture clone with a feature in progress holding both engine work and a guard fix: the tooling lands
  on main alone, main carries none of the engine work, the full push is still refused, and the clone's next merge of main is
  clean; a change naming a non-tooling path is refused, and so is one that does not apply cleanly onto main; and a landed
  test that fails without work still held in the clone is refused, with main unchanged.
- **SC-004** (FR-006) `make arbiter-fix-done` refuses while the fix's test is not on main, and passes once it is.

## Review history

- spec-fidelity, Mode 2, round 1 (2026-10-10): CHANGES REQUIRED. Applied:
  - FR-001: a `process-fault` ruling's fault is its `tooling_fix`, held like any other; the contract stops saying "file".
  - FR-002: the GM-review row carries the fix, and a fix made adds what was built and its test to the GM's review.
- spec-fidelity-verify, Mode 3, round 2 (2026-10-10): FAITHFUL - both round 1 items resolved.
- spec-fidelity-verify, amendment 1 round 1 (2026-10-10): CHANGES REQUIRED. Applied:
  - FR-005 takes all of `tests/` as the GM approved (a narrower list could hold an arbiter fix's test from ever landing),
    and every test it lands is run before the push; `docs/` dropped for `docs/make-targets.html` alone; `.claude/skills/`
    added; the Makefile and settings named as the session's reading of "tooling", with why.
  - SC-003 also covers a change that does not apply cleanly onto main.
- spec-fidelity-verify, amendment 1 round 2 (2026-10-10): CHANGES REQUIRED - FR-005's landed-test refusal had no success
  criterion. Applied: SC-003 adds a landed test failing without work held in the clone, refused with main unchanged.
- spec-fidelity-verify, amendment 1 round 3 (2026-10-10): FAITHFUL - round 2's item resolved.
