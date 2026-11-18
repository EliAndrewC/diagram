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
audit checks' verdicts the one measure kept exact. Recorded here as well as in `specs/449-rust-codebase/request.md` because the
reviewers and the round arbiter, who never read that file, kept reaching for the opposite. Applied: constitution XIII "A
differing output is not a regression" (v2.35.0), 449's FR-002, `docs/efficiency-tooling.md`, `docs/diff-run.md`, and the
`spec-fidelity`, `spec-fidelity-verify`, `round-arbiter` and `escalation-check` agent files.
