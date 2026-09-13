# Feature 240 - a review round is not spent on an unverified fix

**Status**: DRAFT (awaiting `spec-fidelity`)
**Request**: [`request.md`](request.md), the GM's words verbatim. **Research**: [`research.md`](research.md).
**Peer**: feature 239 (`Diagram (Kuwabata)`) holds the same contract for `spec-fidelity` and spec figures;
the split was agreed between the two sessions and is recorded in `request.md`. This feature touches
neither file 239 touches, and builds on 239's `measurements.json` rather than a parallel format.

## Summary

A `settlement-review` round costs 11 to 25 minutes of wall time. Feature 230 spent fourteen of them, and
its last three rounds were largely spent finding defects the previous round's fix had introduced
(`research.md` R1). The GM's ruling is that this cannot be fixed with instructions - *"procedures which
rely on someone, whether it's a human or an LLM, remembering to do something are flawed"* - so the
tooling must either stop the dispatch or make the review exit in seconds.

Both failures that motivated it are one shape: **a fix reasoned from a model and dispatched without being
measured against the artifact**. The canopy keep-out measured grove clump bases with one nominal radius
where the claim was about drawn crowns that reach a median 16.3 ft further; the perf explanation
attributed a stage's growth to the map because the code was absent from a cumulative-time profile, which
an A/B refuted in one measurement. Neither is catchable by a rule about EFFORT - the work was done - so
every requirement here is about the RECORD a claim rests on: what was measured, with what command, over
what source, and on what machine state.

Three layers, cheapest first. A script decides what is decidable (does the record exist, does its command
run, is the map current); the reviewer decides what is judgment (can that source support this claim) and
exits before reading anything; and the perf command refuses an attribution with no counterfactual.

## Functional requirements

### A. The dispatch is refused before it costs anything (FR-001 to FR-003)

**FR-001 A `settlement-review` dispatch MUST be refused when a map it names is not current with the
engine.** `scripts/pair-hooks.sh`'s `pretool` branch already intercepts an Agent dispatch of
`settlement-review`; it MUST additionally ask, per map named in the prompt, whether the pool artifact the
reviewer will read matches what the current engine would produce - the generation cache already decides
exactly this when `regen` prints CACHED against REGENERATED, so the check is a key comparison and rolls
nothing. A map whose key has moved, or whose snapshot is missing the `.json`, `.svg`, `.png` or `.html`
the reviewer needs, is named in the refusal with the command that fixes it (`make map GEN=...`).

*Why this one first*: a reviewer reading a map that no longer exists produces a report in which nothing
looks wrong, which is worse than an unverified number. Feature 230's pass 12 ran that way - the roll cache
evicted the renders mid-gate and three of five agents rasterized the SVG themselves to work around it.

**FR-002 A measured figure in the dispatch prompt MUST be backed by a recorded measurement.** The hook
scans the prompt with the same figure detector `scripts/spec-lint.py` uses (a number with a unit) and
requires each to resolve to an entry in the run's measurements file. A figure that resolves to nothing is
NAMED in the refusal, with the command that would record it - the author almost always has the
measurement and simply did not record it, so the refusal must cost seconds rather than a re-measurement
(feature 239's own review rounds, relayed by that session).

**FR-003 The refusal MUST be escapable with a stated reason, and the escape MUST be recorded.** The escape
is `REVIEW_PREREQ_OK="<why>"`, subject to the project's existing escape rules - an invocation rather than a
mention, a reason of at least two words and eight characters, logged to `dev/bypass-log/`. A review of a
map deliberately left in a bad state (a negative fixture, a reproduction) is the case it exists for.

### B. The reviewer exits before it reads anything (FR-004 to FR-006)

**FR-004 `.claude/agents/settlement-review.md` MUST carry a FIRST STAGE that can return NOT-REVIEWABLE.**
Before reading the map, the agent reads the measurements file the dispatch names and returns
NOT-REVIEWABLE - naming what is missing and nothing else - when a figure in the dispatch has no record, or
when a record's `source` cannot support the claim it is offered for. A NOT-REVIEWABLE return is not a
review: it does not appear in the review ledger as a pass, and the session records the missing
measurements and re-dispatches.

**FR-005 The judgment FR-004 makes is about the SOURCE, and the canopy case is its worked example.** A
measurement record carries `quantity` (what was measured, in words) and `source` (the fields or the
artifact bytes it read). A claim about what a reader SEES - a clearance, an overlap, a legibility - rests
on a source that carries the drawn thing: `tree_crowns` and the SVG's own ink can support "the plank
stands clear of the canopy"; a grove's `clumps` with its nominal `r` cannot, because the drawn crowns are
jittered off those bases and reach further. The agent is told to make that judgment and to exit when the
answer is no; it is NOT asked to re-derive the number, which is what its rounds are for.

**FR-006 The reviewer MUST keep the right to measure independently.** Nothing here removes the instinct
that has been this project's best defect-finder: the pass-13 agents re-derived the canopy clearance from
scratch and that is how the proxy was caught. What the contract removes is the reviewer having to rebuild
a harness to check arithmetic it was handed.

### C. The record a claim rests on (FR-007 to FR-009)

**FR-007 Measurements are recorded in feature 239's format, extended by two fields.** The existing shape
is `value`, `unit`, `command`, `taken`, and optional `note`, `varies`, `load`. This feature adds
`quantity` and `source` (FR-005) and, where a claim is about one map, `subject`. The file lives beside the
feature that measures (`specs/NNN-slug/measurements.json`), written by a harness under `measure/` and
refreshed by one command. If 239 lands first, this feature adopts whatever that format then is; if this
one lands first, that session has said it will match.

**FR-008 A recorded command MUST run from the repository.** A command that reads a corpus under `/tmp`
re-runs nowhere and is not a record; the refresh command MUST be runnable on a clean checkout of the
repository, and the harness MUST fail rather than record a figure it cannot re-derive that way (feature
239's own review round found this in its first `measurements.json`).

**FR-009 A TIMING record MUST carry the machine state it was taken on, and MUST refuse a noisy one.** The
container runs several sessions at once: the same command on the same tree measured 145 ms and 303 ms an
hour apart, the second while another session rolled a map. A timing harness records the one-minute load
average and refuses to record above a quiet threshold, which this feature measures rather than guesses
(`research.md`). Corruption that looks like a result is the failure mode being removed.

### D. An attribution owes a counterfactual (FR-010)

**FR-010 `make perf-explain` MUST refuse a causal attribution that has no control measurement.** Where the
explanation names a cause - "the growth is X" - the command requires a recorded measurement of the same
subject with X removed or disabled, in the measurements file, or the explanation must state in its own
words that the attribution is unverified. This is exactly the step that settled feature 230's dispute: the
author reasoned from a profile in which the true cause did not appear, and the `perf-audit` agent forced
the rule to return True and measured 4.70 s against 2.56 s against a 1.34 s baseline. A free predicate in
the wrong place is invisible to a cumulative-time profile and still doubles a stage, so "it is not in the
profile" is not evidence, and the command should not accept it as one.

## Success criteria

- **SC-001** (FR-001) A `settlement-review` dispatch naming a map whose generation key has moved is
  refused, in under two seconds, naming that map and `make map GEN=...`; the same dispatch is permitted
  once the map is regenerated. Proven on a real pool map, both ways.
- **SC-002** (FR-002, FR-003) A dispatch prompt carrying a figure with no record is refused and the
  refusal NAMES that figure; with `REVIEW_PREREQ_OK="<reason>"` it is permitted and the reason lands in
  `dev/bypass-log/`; a bare token with no reason is refused.
- **SC-003** (FR-004, FR-005) Given feature 230's own pass-13 dispatch - "the plank stands 6.6 ft clear of
  the nearest crown" backed by a record whose `source` is the grove's clump bases - the agent contract
  returns NOT-REVIEWABLE naming that figure and its source, and given the same claim backed by a record
  whose source is `tree_crowns` it proceeds. The worked example is carried in the agent file.
- **SC-004** (FR-007, FR-008) Every entry this feature's own `measurements.json` carries re-derives by
  running its recorded command from a clean checkout, proven by a test that runs them.
- **SC-005** (FR-009) A timing harness refuses to record above the measured quiet threshold and records
  the load average with every figure it does write.
- **SC-006** (FR-010) `make perf-explain` refuses an attribution with no control measurement, and accepts
  the same explanation once the control is recorded or the attribution is labeled unverified. Feature
  230's own first explanation is the negative fixture.
- **SC-007** (spec-wide) `make done` green; the two guards this feature adds have suites that are proven
  to FIRE by deleting the guard and watching a test go red, per the project's own rule for a new guard.

## Decisions recorded

- **D1 The script decides shape, the agent decides adequacy.** "Does a record exist for this figure" is
  decidable and belongs in the hook; "can this source support this claim" is judgment and belongs in the
  agent's first stage. Splitting them the other way would either put prose classification into a shell
  guard or spend 20 minutes to learn a file was missing.
- **D2 Two layers rather than one, deliberately.** The hook cannot see a dispatch that reaches the agent
  by another route, and the agent cannot save the seconds the hook saves. Each is the other's backstop.
- **D3 This feature does not touch `spec-fidelity`, `scripts/spec-lint.py`, the tasks template, or the
  house-style guard** - all four are feature 239's, by agreement between the sessions.
- **D4 The figure detector is SHARED with `spec-lint.py`, not copied.** A second detector would drift
  from the first, and this repository has the stale-literal lesson recorded already.
