# Feature Specification: gate and review friction

**Feature Branch**: `442-gate-and-review-friction` (no branch; work on `main` in the clone)

**Created**: 2026-10-27

**Status**: Draft

**Affects**: tooling

**Approved**: the GM, 2026-10-27, "Thoise improvement sound worth doing in any case, so why don't you knock those out"

**Input**: `request.md` (the GM's words, verbatim, and the four improvements of trial 441's report).

## Why

Trial 441's report measured four losses in features 440 and 441: a landing refused at its end because the merge's
feature-complete check read the spec's verdict differently from the review gate (about 10 min; the second time - feature 387
found the same drift); a `sync-in` that waited about 3 min behind the landing's own render-sync; three of 440's ten review
findings were success criteria left unrevised when their requirement was rewritten; and a measurement-only trial's review
re-ran every profile to re-derive figures its research files already recorded (about 3 min).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One reading of a spec's verdict (Priority: P1)

1. **Given** a spec, **Then** the review gate and the merge's feature-complete check ask ONE function whether it carries its
   fidelity verdict - a FAITHFUL line naming its review, or a round arbiter's ruling standing for it (a round cap's or an asked
   one) - and agree on every case.

### User Story 2 - A sync that does not queue behind a render (Priority: P1)

1. **Given** `scripts/sync-with-main.sh sync-in` run by hand while a render-sync holds the mirror lock and the mirror is
   already at GitHub main's tip (as it is right after a landing's push), **Then** it takes no lock, refreshes nothing and merges
   the clone; **Given** main has moved, **Then** it waits at most the bounded time the prompt hook waits and leaves the render to
   the background runner.

### User Story 3 - A criterion left behind is caught before a round (Priority: P2)

1. **Given** a change that rewrites a requirement's text, **Then** the leftovers search a later review round runs names each
   success criterion that cites that requirement and was not itself touched by the change, as a candidate to look at.

### User Story 4 - A measurement trial's review checks, not re-runs (Priority: P2)

1. **Given** a trial brief Done that landed no engine code - its Status says it was set down or stopped at the measurement -
   **When** `make trial-review F=<n>` runs, **Then** it writes a bundle - the brief, the request, its research files with each
   command's output recorded in them - and prints the one-review dispatch, which asks the reviewer to check each figure against
   the output recorded beside it and to re-run a command only where no output is recorded for it or the output disagrees.
2. **Given** any other trial (one whose spike lands), **Then** `trial-review` prints the ordinary full-review dispatch.

## Requirements *(mandatory)*

- **FR-001**: One function (`scripts/hooks/lib/hm_arbiter.py`, `spec_verdict`) decides whether a spec carries its verdict; the
  review gate (`scripts/gates/review-gate.sh`) and `l7r/diagram/ci/features.py` both call it; the merge check's bare
  "FAITHFUL" substring test and its own ruling reader are retired; a test runs the same cases through both callers. These two
  are every gate that reads a spec's verdict to refuse a push or a landing - found by `grep -rn "FAITHFUL\|spec_ruled\|spec-ruled\|spec_accepted" scripts l7r Makefile`
  outside the tests (2026-10-27). `hm_review_round.accepted` reads acceptance too, but to NUMBER a review's rounds, not to gate
  one; it stays out of FR-001 (no landing waits on it).
- **FR-002**: `sync-in`, after fetching, takes no mirror lock and refreshes nothing when the mirror's HEAD already equals the
  GitHub main it fetched; otherwise, run by hand as by the prompt hook, it waits for the lock at most `SYNC_LOCK_WAIT` and hands
  render-sync to the background runner. (A foreground render by hand stays `scripts/sync-with-main.sh render-sync`.)
- **FR-003**: The stale-terms search (`scripts/reviews/stale_terms.py`) names, for each requirement whose text the change
  rewrote, every success criterion citing it that the change left untouched, as a candidate; the round's dispatch shows it as
  the search shows its others, with the same `STALE_TERMS_OK` escape. It is built there, not in spec-lint as the report's row
  put it, because only the round's snapshot holds "the same edit" (spec-lint reads one tree), and the stale-terms search refuses
  the dispatch before a round is counted, on every round after the first - the moment the check is for.
- **FR-004**: A trial records each measurement's command output in its research file (a fenced block beside the figure; the
  trial template asks for it). `make trial-review F=<n>`, for a Done trial whose Status says it was set down or stopped at the
  measurement, writes the review bundle (the brief, the request, the research files) and prints the dispatch (spec-fidelity,
  MODE 2) with the check-not-re-run instruction - a figure with no recorded output is re-run; for any other trial it prints the
  ordinary full-review dispatch. `docs/spec-kit-and-reviews.md`'s trial form names it.
- **FR-005**: `docs/guards.md` names the changed checks; nothing added refuses on a time (feature 435 FR-006).

## Success Criteria *(mandatory)*

- **SC-001** (FR-001): a test gives the verdict cases - FAITHFUL on a review line, "NOT FAITHFUL", a mention in prose, a round
  cap's accept, an asked accept, a `continue` - to the review gate's call and the merge check, and they agree on each.
- **SC-002** (FR-002): the sync-with-main hook tests pass a `sync-in` that, with the lock held and the mirror at the tip,
  returns at once without taking the lock; and one that, with main moved, returns within the bounded wait.
- **SC-003** (FR-003): a stale-terms test names an untouched criterion of a rewritten requirement, and not one the same change
  touched.
- **SC-004** (FR-004): a test of `trial-review` finds the brief, the research files with their recorded outputs and the
  instruction in a stopped trial's bundle and prompt, and the full-review dispatch for a trial whose spike landed.
- **SC-005** (FR-005): the docs name the changes; nothing added refuses on a time.

## Review history

- 2026-10-27, round 1 (spec-fidelity, MODE 2): CHANGES REQUIRED - sync-in skips the lock when the mirror is at the tip, the
  foreground flag cut; the outputs recorded by the trial, the check-not-re-run only for a trial that landed no code; the move to
  stale-terms stated; FR-001's search and `hm_review_round.accepted` ruled out.

## Assumptions

- The four are the report's rows, in its order.
