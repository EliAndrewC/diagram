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

## Stop before homesteads, and talk first (2026-11-21)

Once everything else is ported (feature 449) and the next step would be resuming the parked hamlet stages (`homesteads` first,
`rust/parked/`), the session does not proceed: it stops, and the GM and the session talk before any of that work starts. The GM,
2026-11-21: *"When you get to the point where you have ported everything else and then we're ready to go back to homesteads, then
don't actually proceed. Why don't you go ahead and stop, and then we can talk more after everything else is done before you get
started on that."* Enforced by 449's task filed the same day (a parked stage resumed only with the GM's words; the session's stop
there accepted).

## A provincial city's 3,000 include the samurai country estates around it (2026-11-24)

Canon. Two of the GM's own texts disagreed: feature 156's request (a city's ~3,000 "includes samurai country estates, only some of
which are depicted on the map, but does not include farmers") against the campaign notes (`l7r.md`: taxed isolated farms "including
samurai country estates, get tallied under the nearest village district") and `budgets.md` (the ~560 samurai on country estates
"tallied into the surrounding village districts"). Asked which holds, the GM, 2026-11-24: *"Yes, the provincial cities 3,000 include
the samurai country estates around it."* So the city place card's claim (`rust/mode_a/src/place.rs`, CANON, feature 156) stands as
written; research page 0001's "counts only those living within the walls" is the sentence restated (its drawing page already counts
"the samurai estates outside a city's wall" as city households). `l7r.md` and `budgets.md` are the GM's notes and are not edited
from here; their two sentences now differ from this ruling until he changes them.

## NOT a ruling: dry plots as rectangles against the canal (2026-11-24)

Page 0006's drawing page carried the comment "the GM's ruling, 2026-07: dry plots are rectangles laid out against the canal". The GM, 2026-11-24: *"I never made a ruling that dry plots are rectangles laid out against the canal. That was never at any point something that I said was true about these maps. That is what a session told me the research showed. But if that is not what the research shows, then we shouldn't do it."* The rule is the record's own (a reconstruction on that page), to be held to what the research shows; no session cites it as his. A comment in the record that names a ruling of the GM's is checked against his recorded words (a `request.md`, this file) before anything is built on it.

## Four statements about the setting are the GM's canon (2026-11-24)

The research record attributed these to the GM with no recorded words (the audit of 2026-11-24; question 452#0). Asked of each "is it your canon?", the GM, 2026-11-24: *"Yes all 4 of those are my canon."* The four, as put to him:

1. Shrine approaches have 1, 3 or 7 arches because those numbers carry power, seven most of all, and a few named great sites have long donated rows (research page 0220; his 2026-09-29 words already held arches at ordinary shrines).
2. Only a merchant family the daimyo has granted the right may have a walled, gated compound; wealth cannot buy one (0155).
3. The setting is more attentive to its peasantry than its historical models, which is why a city gets a generous count (0185).
4. Hirameki stood unwalled and was walled in haste during the Lion/Crane war, which excuses its shortfall in housing (0002).

Each is CANON, and a comment or claim that names it cites this entry.

## Ryusei's provincial lineages are recent (2026-11-26)

Canon. The GM's notes (`gm-assistant/setting/lineages.md`, "in Ryusei lands, all of the lineages are \"cosmopolitan
lineages\" and there are no \"provincial lineages\"") and research page 0138's worked example (one of Ryusei's six
chancellor lineages a provincial one) seemed to disagree. The GM, 2026-11-26: *"the Ryusei domain had no provincial lineages
until their recent involvement in the Lion/Unicorn war, at which point they expanded and acquired some provincial lineages,
hence the apparent contradiction"*. So both hold: the notes describe Ryusei before the war, and a present-day Ryusei capital
may seat a provincial lineage's chancellor. Applied on 0138's drawing page, which says the notes count the worked example's lineages as all cosmopolitan and
that the domain has since gained provincial lineages of its own in that war (it does not say which, or whether one holds a
Chancellery seat: his words do not).

## Burakumin neighborhoods stand inside a city's walls, at the edge (2026-11-26)

Canon. The GM, 2026-11-26: *"burakumin neighborhoods are indeed inside city walls, at the edge as our research says - I don't
remember any of our research indicating that they were always entirely outside the city walls. If I am wrong about that, and
they were historically outside the walls instead of inside the walls, then I completely support moving them there, but I
didn't think that was a deviation."* So the setting's placement is inside the wall at the edge; whether that DEPARTS from the
history is the record's question (research page 0156 labeled it a deliberate deviation): a search pass settles whether the
historical quarters stood inside or outside the walls, and the page's label follows it - and, by his words, if the history
puts them outside, the maps move them there.

## The aqueduct's banks drawn 2 px wider for legibility are fine (2026-11-26)

Research page 0141 draws the capital's aqueduct with its water at true size and its bank outline about 2 px wider each side
than life, a labeled drawing convention of 2026-08-09 that no record showed was ever raised with the GM, as "To scale means
true size" above requires. Asked, the GM, 2026-11-26: *"If the aqueduct is being made 2px larger to make it more legible on
the map then that's fine. Otherwise I'd want it shown to scale."* It is for legibility - the page's own reason is that the
true banks of so narrow a channel would vanish on the page - so the convention stands, now with his words. The bound is his:
an enlargement that is not for legibility is drawn to scale.

## 2.8% of a capital's row-house households live outside its wall (2026-11-26)

Canon. Research page 0181's drawing page put about 2.8% of a capital's row-house commoner households outside the wall - 60 of
2,160, some 300 inhabitants, the wharf hamlet only (the brokers, boatmen and porters who must live at the water they work)
and the towpath shore - a session's choice of 2026-08-10 among three answers (57%, the overflow of a wall sized too small,
never a decision; 30%, the share of the Chinese commercial cities, which would put about 1,800 inhabitants outside; and
this), labeled setting canon with none of his words recorded. The reasons given him: the capital the maps draw, Shiro Daika,
is a castle seat built for siege on the Crab clan's border, whose wall exists to keep its population inside, and it fits
Japan's enclosed castle towns. The GM, 2026-11-26: *"yes I accept the 2.8% figure as canon for the reasons explained"*. The
capital's samurai on country estates along the approaches (about 47 households, 15% of its samurai) are a separate line and
are not part of this figure.
