# Feature 253 - the old value is looked for before a later review round is spent on it

**Status:** draft 2026-09-19 - round 1 CHANGES REQUIRED applied (see Review history).

## Summary

The GM approved (`request.md`) a tooling change that costs no model tokens: before a later `spec-fidelity`
round is dispatched after a value in the feature changed, the feature directory is searched for the OLD
value, so the session fixes what it left stale instead of paying a review round to be told. This feature
builds the search, puts it where a later round is dispatched, and proves it on the stale passages feature
251 actually shipped to its reviewer. No engine code: the delta routes DIRECT.

## Functional requirements

**FR-001 - the search.** `scripts/_stale_terms.py` compares two states of a feature directory - the one the
previous review round saw and the present one - and reports STALE CANDIDATES. For every line the change
REPLACED (paired old and new line), the SUBJECTS are the backticked terms the old and the new line share, and
the OLD VALUES are the words and numbers the old line had and the new line does not. A candidate is any
OTHER line of the present feature directory that names a subject AND still carries an old value. A changed
line with no backticked subject yields nothing: without an anchor the search cannot tell a stale passage
from an unrelated use of a common word. Matching is case-insensitive (the table said `sonnet`, the stale
sentence said "Sonnet"). It searches EVERY text file of the feature directory - `spec.md`, `plan.md`, the TASK
lines of `tasks.md`, and whatever else a feature holds (`data-model.md`, `contracts/`, `quickstart.md`, a
ledger), so a file kind nobody anticipated is searched by default - EXCEPT what is named here, each with why it
legitimately keeps an old value: the
`Review history` section (it records what used to be); a task's `verify:` note (a dated record); `request.md`
and `gm-request.md` (the GM's words); `research.md` (a results table keeps the value that was TESTED - measured on the real case,
`research.md` R1: with it included 16 of 18 candidates were false); `measurements.json` and `plan-review.json`
(recorded figures and a recorded verdict, re-derived or re-issued, never hand-edited); `measure/` (a harness's
code). It decides nothing and edits nothing; a candidate is a line for the session to look at.

**FR-002 - run where a later round is dispatched.** The review-round guard (`scripts/_hm_review_round.py`,
`review-round-hooks.sh`), on the branch where it rewrites a later round, first runs the search between its
snapshot (what the previous round saw) and the feature directory. With no candidate the dispatch proceeds
exactly as today. With candidates the dispatch is REFUSED once, before any snapshot or round state moves,
with a message listing each candidate as `file:line`, the subject, the old value and the line it changed
on - and the two ways on: fix the lines and dispatch again, or dispatch again with
`STALE_TERMS_OK="<reason>"` in the prompt when the candidates are not stale (a reason is required, as for
every escape, and the firing is recorded). A refusal is the right shape here by the project's guard
doctrine: whether a candidate is stale is a decision only the session can supply, and the refusal costs one
turn where the review round it MAY prevent costs a subagent run and usually a second one (`research.md` R2
measures how often that is: on feature 251's thirteen findings, never a whole round).

**FR-003 - also a make target.** `make stale-terms F=<feature>` runs the same search by hand against the
guard's snapshot (or `AGAINST=<git ref>` when there is none) and prints the candidates, so a session can
look before it dispatches.

**FR-004 - proven on the real case, tested, recorded.** The test module reconstructs feature 251's
directory as it stood at the dispatch of its first amendment review (commit `36d34718`) against the state
its previous round saw (commit `a5d5051e`), and asserts the search names FR-007's "`source-reader` moves
to Sonnet" line - a finding that round spent itself on - and names nothing in `request.md`, the Review
history or a `verify:` note. `research.md` records, for ALL the stale-text findings of 251's amendment rounds,
which the search would have caught and which it cannot (SC-002 states the count honestly). The guard suite
gains cases for the refusal, the escape with and without a reason, and the no-candidate pass. The root
`CLAUDE.md` guard row, `docs/guards.md`, `docs/spec-kit-and-reviews.md` and the make-targets page say what
is now true.

## Success criteria

- **SC-001** (FR-001, FR-004) On feature 251's real before-and-after, the search reports the FR-007 line and
  reports no line from `request.md`, the Review history or a `verify:` note.
- **SC-002** (FR-004) `research.md` lists each stale-text finding of 251's amendment rounds with CAUGHT or
  NOT CAUGHT and why; the feature claims no more than that count.
- **SC-003** (FR-002, FR-003) In the guard suite a later round with a stale candidate is refused with the
  candidate's `file:line`; the same dispatch with `STALE_TERMS_OK="<reason>"` is rewritten and routed as
  today; a bare token is refused; a later round with no candidate is untouched by this feature.
- **SC-004** (FR-004) `make hooks-test` and `make quick` are green.

## Assumptions

- The guard's snapshot is the state the previous round saw (feature 249); a feature with no snapshot gets no
  search from the guard, as it gets no rewrite.
- The search is a heuristic with a stated reach: it finds a value left behind beside a named subject, not a
  sentence made false in other words ("stepped back up and re-run"). Those still cost a round.

## Review history

- **Round 1 (2026-09-19) - CHANGES REQUIRED, two items, both applied.** The refusal in FR-002 was ruled WITHIN the
  request (the suggestion's load-bearing word is "first": an advisory note rides along with a dispatch that is
  already going, and the round is spent anyway). (1) `tasks.md` was excluded whole where only its dated `verify:`
  notes keep an old value legitimately: task lines are now searched. (2) "`.md` files only" was an exclusion with
  no reason: every unsearched thing is now named with its reason, `research.md` on a measurement.
- **Round 2 (2026-09-19) - CHANGES REQUIRED, one item, applied.** Both round-1 items verified. The fix for item 2 had
  turned an exclusion list into a WHITELIST of three files, silently dropping operative text other features hold
  (`data-model.md`, `contracts/`, `quickstart.md`, ledgers) and `gm-request.md`: the default is flipped back - every
  text file is searched except what is named. FR-002's "prevents" softened to "may prevent", beside R2's count.
