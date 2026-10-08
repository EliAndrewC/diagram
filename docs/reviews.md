# Invoking a review agent

**Load this file when:** You are about to launch a review check - `glyph-check`, `settlement-review`, `fix-check`, `building-review`, `size-audit` - or a feature asks which one is owed.

The repository's review process; the short always-on version is in the root [`CLAUDE.md`](../CLAUDE.md).

## WHICH review is owed: its OCCASION (feature 294, GM 2026-10-01)

A review check is owed only on the occasion its answer can change - never because an engine change moved a manifest. The GM:
*"as the number of settlements that we have in our pool grows ... This will become quickly untenable"*, and of the glyph
review, *"something that would be run only when a new element is added to the map and then not run it other times"* - *"a
category of thing"*. `scripts/_review_owed.py` is the one answer, asked by `make verify`, the pair guard and `review-gate.sh`:

| check | owed when | looks at |
|---|---|---|
| `glyph-check` | an element new to a map or sheet, whatever its mark (detected from `ink_classes` / `data-kind`); a glyph redrawn or an element re-placed by substantially different rules (declared: `glyph-redrawn:`, `placement-changed:` - the GM's tannery) | that element, on one map where it stands |
| `settlement-review` | a map new to the pool (detected); a new settlement form or tier (declared: `new-form:`, `new-tier:`) | the whole map: does it read as a distinct place, its declared economy, a new tier's fabric |
| `fix-check` | a feature closing a defect the GM reported by eye (declared: `gm-fix: <map> - <the complaint>`) | the GM's complaint, at fit zoom first |
| `building-review` | a sheet new to the pool (detected); a layout revised or a new program (declared: `layout-revised:`, `new-program:`) | the sheet's layout, program and coherence |
| `size-audit` | a sized kind new to a sheet (detected); a new program (declared) | that kind's real size, then a band the registry holds |

**A hand-drawn map awaiting conversion owes nothing.** The GM, 2026-10-01: *"All hand-drawn maps should be excempted from
settlement reviews because they will be converted to being scripted later. Hand-drawn diagrams of magistracies and country
shrines and later things which will never be scripted (by design) should still get setlement review."* A Mode B map in
`legacy-hand-authored-pool/` is skipped by every occasion (`_review_owed.exempt`); a Mode A sheet keeps its review wherever it
lives.

**The declaration.** Every feature that touches drawing or placement code carries an `## Occasions` section in its `tasks.md`,
one `- <occasion>: <argument>` line each, or `- none: <why>` - whether a change is substantial is the feature's call to
DECLARE; a delta that touches drawing or placement code with no section is refused at push (`review-gate.sh`). A TWEAK -
a change done directly, with no spec-kit feature - declares in its commit message instead, one `Occasion: <occasion>: <argument>`
line (GM 2026-10-01, the household shrine's torii); and a landed feature's section is not read again once every task is ticked. The research
behind the table is `specs/294-settlement-review-rethink/research.md` R1: every check of the three contracts sorted by what it
needs and when its answer changes, and what a placer or a test now holds instead.

**The shape, enforced** (the pair guard): one owed UNIT per agent (`<check>:<subject>`), each dispatched from the prompt file
`make verify` writes (`.git/review-snapshot/<unit>/dispatch.md`, with its `UNIT:` line); dispatched once the gate is GREEN for the
content (a review beside a running gate is refused - a gate going red mid-review cost ~36 NOT-REVIEWABLE runs, research R0); at
most two rounds per unit per feature (one review and one fix-verification; a third needs `REVIEW_ROUNDS_OK="<the GM's words>"`);
the stop hook holds the turn while an owed unit has no dispatch, run or record. An engine change that moves things under rules
already judged owes nothing and gets no report - the GM looks at the map.

**The ledger measures it.** Every pass is a row of the ledger's measured table - the check, each finding's class, whether the
author had missed it, and the run's cost from `make review-cost AGENT=<id>`; `make review-census` totals them per check, so a
check that never finds anything is a number.

## Invoking a review agent: launch it EARLY, in the background, and never wait on it

Launch an owed check the moment its gate is green - BEFORE your own visual pass, the docs and the commit: everything you do
while it runs is free (measured 2026-08-08: one `settlement-review` was 22% of a task's wall clock, with the session idle for
almost all of it). The GM (2026-08-26): *"iterating in a way that allows me to look at something more quickly will probably
be more productive than having a built in independent reviewer, which runs multiple times on every pass."* So:

- **A review runs in the BACKGROUND, after the map is handed back** - or in parallel with a LONG gate (`make done FULL=1`, a
  CodeBuild run), never alongside `make quick` (launching a multi-minute review "in parallel" with it just serializes). A
  finding becomes a follow-up task; it never holds the result.
- **Never busy-wait on one.** Same rule as the gate: act on the completion notification.
- **Every FINDING is a row in [`docs/review-ledger.md`](review-ledger.md), written by the SESSION, never by the reviewer**
  (the GM: you may disagree with the reviewer, and the log must say both what was found and whether it was acted on - fixed /
  recorded-only / declined with why / MISSED-BY-REVIEWER), in the same commit that acts on the review.

## WHAT GOES TO THE GM, AND WHAT DOES NOT (GM 2026-09-12)

The reviewers work. What failed on feature 227 was the step AFTER them: three of its findings went to
the GM as judgment calls, and all three came back as corrections. The GM's own diagnosis is the rule:
*"I'm trying to figure out why you keep escalating things to me that when I look at them don't seem
like problems because it might be that I simply do not understand why they are problems. And, thus,
I'm concerned that I will be ignoring something bad."* That last sentence is the real cost - an
escalation that is not a problem teaches the GM to doubt their own reading of the ones that are.

**The rule this broke already existed, in two places.** The agent's own output contract says
QUESTIONABLE means *"it needs a RESEARCH PASS - never 'a GM ruling'"*, and constitution XII says a
reviewer writing "this wants a one-line ruling" has identified a QUESTION, not delegated one. A
QUESTIONABLE item is the session's to settle. Forwarding one is skipping the work.

So before any finding reaches the GM, it passes three tests, in order:

1. **Which norm does it violate, named and located?** A constant, a check, a research heading, a
   ruling in the notes. No norm means no finding: the thing in front of you is how the map is, not
   something wrong with it. Two of 227's three failed here - a board measured against a scoring
   radius no rule uses as a bar, and a house-to-field distance against a maximum that does not exist.
2. **Did you run the research pass, and is the record genuinely silent?** Not "could the GM rule on
   this" - *has the record been asked*. One of 227's three had already been answered by a measurement
   taken an hour earlier on an older layout, and re-running it on the shipped map closed it.
3. **Does the GM's answer change what ships?** A number trending toward a bar it has not reached is a
   line in the map's notes, not a question. "Worth knowing" is not an escalation.

What IS the GM's: a genuine fork where the record supports two forms and the choice is taste or
canon; a cost they alone can price; and the acceptance of a finished thing. Put those up plainly, say
what you recommend, and say what you measured to get there.

**Record the misses in the ledger** (`docs/review-ledger.md`), which gained a column for exactly this,
so the escalation rate is a total rather than a feeling.

## A finding OUTSIDE the delta is still yours to fix

Constitution **Principle XIV** (GM 2026-08-17). An independent reviewer pointed at a DELTA reliably
turns up defects that have nothing to do with it - that is the reviewer working, not the reviewer
overreaching - and the answer is to FIX them in the work at hand, not to ledger them for a pass that
never comes. The only exception is a fix that would be an architectural change (a stage reordering, a
new subsystem, a placement engine rewritten); defer that WITH its measurement, its mechanism and an
implementation sketch, which is a deliverable rather than a shrug.

Do not reach for Principle XIII's "pre-existing failures stay ledgered" here. That clause is about
what BLOCKS a push, not about what you owe a defect you have seen.

Worked example, the paddy size floor (2026-08-17). Three `settlement-review` findings arrived that
had nothing to do with basin size: lane frontage regressed past the 94 ft threshold `homesteads.py`
records as its own diagnosed defect, the three shared byres collapsed onto three farmsteads
(median nearest-byre 373 ft), and a windbreak was clipped with 23 clumps drawn wholly off-canvas.
All three were fixed in that feature - 106/59/65/77 ft lane medians, byre median 107 ft, zero
off-canvas clumps - and the *first* attempt at the lane fix (a relaxation ladder) is recorded at the
point of change as having measurably done nothing, because a fix that fails is worth as much to the
next reader as the one that works.

## A `PAIR_OK` waiver is honored by the stop hook

A gate run with `PAIR_OK="<reason>"` records `waived_key` against that exact engine key, and `scripts/pair-hooks.sh stop`
honors it - per content, so an engine edit after a waived gate is guarded again. Do not drop that record: without it the
guard told a session to do the thing it had just done, which teaches that the documented remedy does not work
(`scripts/test-pair-hooks.sh` holds it). A one-off PAIRING HALF-OPEN report while a review is genuinely in flight was seen
once and not reproduced (likely a race against a transcript still being written); the hook fires once per engine key.

## `impl-drift` is owed by the claims index, not by an occasion (feature 316)

`impl-drift` judges the engine's and the Mode A procedures' research claims against the questions they cite. It is not a map
review: it is owed when `make claims-owed` names a claim (new, its code changed, or its question's findings moved), and the push
(`scripts/claims-gate.sh`) holds it. One bundle per file or per batch (`make claims-bundle MODULE=<file>`), the reply recorded
with `make claims-checked BUNDLE=<dir> REPLY=<file>`, a row of the ledger's measured table per pass as for any check.
