# The GM's standing rulings that no spec records

**Load this file when:** you are about to cite one of the GM's rulings and cannot find his words in a
`specs/*/request.md`, an `**Approved**:` line or a spec, or `escalation-check` asks where a ruling came from.

These were held only in session memories until 2026-10-26, when the GM retired project memories (*"anything that would
go into a memory probably either needs to be a tooling fix or it needs to live in the documentation"*). Each entry is his
words, verbatim, with the place the rule is now applied. A new standing ruling goes into the doc or guard that applies
it, not here; this file holds only what had no other home.

## To scale means true size (2026-07-21)

On the Kuwabata polder rework, rejecting parcels drawn larger than the researched ~1 mu for legibility: *"I do not want
that. We're trying to be perfectly to scale, remember?"* A to-scale map draws a researched size at its TRUE size; a
feature that seems illegibly small is raised with the GM, never silently inflated. Applied: constitution XII, the
labeled-decision rule (an inflated size is an unlabeled deviation). A doc that calls something "oversized" or "a
legibility floor" predates this ruling: check its date before believing it.

## Following the research needs no permission (2026-09-12)

After a session asked whether it might move water on a map: *"I'm not sure why you would even have to ask me that
because when not otherwise stated, when we don't have a firm decision to the contrary, then it is always okay to make
changes to comport with our actual research ... you should assume that when your research shows that a map should be
tweaked in order to comport to how these places actually looked, then you can just do that."* And: *"if you find more
bugs along the way, then you should just go ahead and fix them."* Applied: root `CLAUDE.md` "Research",
`escalation-check` tests 4 and 5.

## Away means finish alone (2026-10-04)

Leaving feature 320 to land unattended: *"you should NOT stop to ask me questions. If you need to run more than the
normal number of review rounds on anything, you should consider those additional rounds to be pre-approved ... if you
run into any bugs or deficiencies, you should not ask me how to proceed and should instead treat each one as something
you should fix ... work through all problems on your own and not stop or ask for guidance until the feature is complete
and the work has landed on main."* Applied: root `CLAUDE.md` "Run the chain end to end, unattended"; a review past its
cap goes to the round arbiter (feature 379); `make set-down` refuses while the week's usage is under the soft cap.

## Make the tests cheap, never hide their cost (2026-09-07)

On the incremental gate (feature 207): *"I am not interested in doing full baseline runs in the background at this time
because I want to first get things back to a point where the tests themselves are so efficient that we don't need to
worry about such things. After our project has expanded and the tests become inescapably lengthy, then perhaps we will
turn the idle tests back on."* A slow gate is answered by cheaper tests (selection, caching, roll speed), not by an idle
run nobody watches; do not propose re-arming idle tests until the GM raises it. Applied: `rust/guard/src/guards/idle_tests_hooks.rs`
(disarmed), `docs/iteration-loop.md`.

## Everything works, not bitwise identical (2026-11-18)

Told a round-arbiter ruling had held a port's diagnostics (feature 449 T150) to PIL's exact pixels on image formats nobody
passes: *"And whyyyyy did the arbitur rule that things must match exactly when I keep saying they don't have to so long as
everything works?!?!"*; and on the amendment: *"gotcha, thanks - yeah we should definitely amend our project guidelines and
speckit constitution and whatever else we need to update to clarify this and remove any references to things needing to be
bitwise identical or anything like that as an exactness standard"*. Earlier the same: *"the resulting maps do NOT need to be
bitwise identical!  I feel like I've said this dozens of times"* (2026-11-17) and *"it's always okay for maps to change, so long
as the changes don't violate our research findings"* (2026-10-18). For every port and every change: an output may differ from
what it replaces so long as everything works - its tests pass, it does its job for its callers, its research claims hold; the
drawn outputs must pass their checks and hold their research claims, and a ported check must still do its job (T181, below). Recorded here as well as in `specs/449-rust-codebase/request.md` because the
reviewers and the round arbiter, who never read that file, kept reaching for the opposite. Applied: constitution XIII "A
differing output is not a regression" (v2.35.0, reworded 2.35.1), 449's FR-002, `docs/efficiency-tooling.md`, `docs/diff-run.md`, and the
`spec-fidelity`, `spec-fidelity-verify`, `round-arbiter` and `escalation-check` agent files.

The same day, on T180's own wording ("the audit checks' verdicts the one measure kept exact"): *"When you say "the audit checks pass/fail must match exactly", then surely you mean "the audit checks must pass" right?!"*. Yes: nothing is
kept exact. Two things are owed, neither an exactness standard: a drawn output - a map, a sheet, a page - must pass its checks and
hold its research claims, and nothing about its bytes, pixels or positions must match what it replaces; and a check that is ported
must still do its job - its red fixtures still fail and the sheets it passed still pass, which is how a port of a check is shown to
work - while a check fixed or improved on purpose (constitution XIV; FR-002's exception for a check that refuses correct work) changes
as fixed. Applied by feature 449 T181: constitution 2.35.1 and the same files as above.

And on fixing as the port goes: *"gotcha; yeah we want to use this port to fix broken things as we find them, so it needs to be okay to have checks pass as we make those fixes; in general we should fix all known bugs in each step before moving on to porting the next step"*. So a check's verdicts change as a bug is fixed - a sheet a buggy check refused now passing, or an engine bug fixed changing a map - and that is expected, never a regression; a ported check is shown to work by catching what it is meant to catch; and each step's known defects (found by the port, its claims rounds or its reviews) are fixed before the next step's port begins, in every copy that still lives (the Rust and any kept Python).

## A defect is a wrong outcome, not a difference (2026-11-19)

After a chain of sub-pixel "defects" was fixed in code across feature 449's T188-T194 - impl-drift judging code against a
CONVENTION's own wording, plan reviews blocking for differences left, every edge case filed as found and left - and told of the
session's rule that a drift which moves no caption and contradicts no research finding is fixed by restating the claim: *"Yes that tolerance rule seems good.  And not only that: what changes can we make to our project guidelines to make this kind of thing more obvious?  Like, I feel like I keep having to come back and say, over and over again, "don't spent a lot of time 'fixing' things which are not actually wrong like things which are different than you expected but still work perfectly well and are in line with our research and produce maps which look fine"."* And on T196's plan: *"sounds good, we'll give that a try and see what happens - hopefully we can arrange things so that they are noticed and caught before I come back and have to point them out next time - that is not the only measure of success but it is an important one.  thanks!"* A defect is a wrong outcome - a map that reads wrong, a research finding contradicted, a check that passes bad work or refuses good work, a tool that crashes, hangs or answers wrongly - never a difference from what was expected, from the Python or from a convention's wording; "fix all known bugs" (2026-11-18, above) means defects. Applied by feature 449 T196: constitution XIV (v2.36.0), the root and `research/` CLAUDE.md files, `docs/approach-checklist.md` item 12 and the task section `make task-add` writes, the plan template's XIV entry, `impl-drift` (its `fix: claim` or `fix: code`, refused without one by `make claims-checked`), `spec-fidelity`, `spec-fidelity-verify`, `round-arbiter` and `escalation-check`, `docs/reviews.md`, `docs/research-doctrine.md` and `docs/spec-kit-and-reviews.md`.
