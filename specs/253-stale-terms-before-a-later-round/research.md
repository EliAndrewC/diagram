# Research - 253 the old value is looked for before a later review round is spent on it

## R1 - what the search finds on the real case (observed 2026-09-19; method: `stale_candidates` over `git show` of the two commits)

Feature 251's directory at the dispatch of its first amendment review (`36d34718`) against what the previous
round saw (`a5d5051e`):

- searching every text file, `research.md` included: 18 candidates, 2 of them real. 15 of the 16 false ones were
  in `research.md`, whose results tables legitimately keep the tier that was TESTED (the sixteenth is FR-002's own
  note on the proposal, below) ("| record-format towns | sonnet / medium |").
- searching everything but `research.md` (and the other named exclusions - on this case that is `spec.md`,
  `plan.md`, the task lines and `checklists/requirements.md`): 3 candidates, all in `spec.md` - FR-007's "`source-reader`
  moves to Sonnet at high effort" (real; that round's item 1), FR-008's "(Opus, medium, the same tools)" (real;
  part of item 2), and FR-002's own note "the proposal had `record-format` on sonnet / medium" (not stale: it
  describes the proposal). Two of three is a list worth reading; that is why `research.md` is not searched.

## R2 - what it would and would not have caught, over ALL of 251's amendment-round findings

| round | finding | caught? |
|---|---|---|
| pass 1, round 1 | FR-007 still "moves to Sonnet" | CAUGHT |
| pass 1, round 1 | FR-008 "(Opus, medium, the same tools)" | CAUGHT |
| pass 1, round 1 | FR-008's heading, the Summary and US5 still "medium-effort twin" | NOT CAUGHT - those lines name `spec-fidelity`, not the changed row's `spec-fidelity-verify` |
| pass 1, round 1 | FR-011 "the run is repeated at the new tier" | NOT CAUGHT - a procedure made false, no value left behind |
| pass 1, round 1 | SC-004 "stepped back up and re-run" | NOT CAUGHT - same |
| pass 1, round 1 | FR-011's two-artifacts-and-a-clean shape against the trimmed batch | NOT CAUGHT - same |
| pass 1, round 1 | FR-011 / SC-005 "per-run mean" against R5's pairing | NOT CAUGHT - a disagreement between two documents |
| pass 1, round 2 | the history's "it cut none" against R5's own row | NOT CAUGHT - a false sentence, newly written |
| pass 1, round 2 | "111-line contract against 236" | NOT CAUGHT - a wrong figure, newly written |
| pass 2, round 1 | an ordered experiment not run | NOT CAUGHT - an omission |
| pass 2, round 1 | R5 "no further tier was tried" and its landing row | NOT CAUGHT - in `research.md`, which R1 shows cannot be searched usefully |
| pass 2, round 1 | the Haiku caveat with no requirement behind it | NOT CAUGHT - an omission |
| pass 2, round 1 | SC-004's closing clause false for `record-format` | NOT CAUGHT - a sentence made false |

**2 of 13, and no ROUND saved:** every one of those rounds carried at least one finding the search cannot see, so
each would still have returned CHANGES REQUIRED. The session's premise - "most later-round findings were text left
stale" - was true; its remedy reaches only the narrowest kind of stale text, a VALUE left beside its subject.
What the rounds mostly found were SENTENCES made false by a decision that moved, and omissions. This feature
ships the search because the GM asked for it and it is cheap and quiet (three candidates on the real case), and
it says plainly here that it is not where the 61% goes (later rounds' share of the review process's cost,
observed 2026-09-19; method: every recorded `spec-fidelity` run classed by its prompt's mode and weighted as feature 251's R1). Where that goes is turns (observed 2026-09-19; method: `measure/profile.py` over the recorded `spec-fidelity`
transcripts): a later round re-reads about
50 k tokens of fixed context on each of about 7 turns (`measure/profile.py`), whatever it was asked to look at.
