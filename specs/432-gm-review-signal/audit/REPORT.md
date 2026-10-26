# GM-review audit, 2026-10-26: all 465 open rows judged

Judged by nine agents on one rubric (RUBRIC.md beside this file); every row's verdict is in judged.json.

| category | rows | YES | MAYBE |
|---|---|---|---|
| tooling-fix-process | 159 | 0 | 0 |
| round-cap-accept | 156 | 0 | 0 |
| round-cap-continue | 37 | 0 | 0 |
| step-back-routine | 37 | 0 | 2 |
| red-gate-fix | 23 | 0 | 0 |
| route-change | 15 | 0 | 0 |
| accepted-limitation | 11 | 2 | 2 |
| scope-or-ruling-touch | 10 | 8 | 2 |
| process-fault | 9 | 1 | 3 |
| research-reading | 4 | 0 | 1 |
| map-or-output-change | 1 | 0 | 0 |
| review-waiver | 1 | 0 | 0 |
| deferred-finding | 1 | 0 | 0 |
| content-style-question | 1 | 0 | 1 |

## YES

- **390#1** (hour:390-money-foundation-research@1): Hourly step-back, otherwise routine. Its for_gm says research found three canon figures unattested or ambiguous: budgets.md's ~1.5 koku a person a year, its ~187 kg paddy koku, and l7r.md's '40 gallons'. Whether the canon changes is for the GM.
  - why: Test 1: only the GM can change his own canon notes (budgets.md, l7r.md), and the research says three of his figures may be wrong.
- **391#3** (hour:390-money-foundation-research@2): 390's hour 2 converged and the round-counter bug got a tooling fix. Its for_gm: l7r.md caps rent at a sixth of a plot's productive capacity in one section and a sixth of its total value in another. Also, two setting claims dropped out of the 0248 intro.
  - why: Test 1: the GM's own canon (l7r.md) contradicts itself on the rent cap, and only he can say which reading is right. The dropped intro claims are a smaller research-reading cost (test 2).
- **397#10** (hour:397-campaign-costs-arrows-paper-rents-plays@1): The hour clock now skips idle gaps (built). Not built: adding translation-check to the Workflow tool's pre-authorized wave jobs, because that list is the GM's own pre-authorization in append-system-prompt.md.
  - why: Test 1: widening a permission only the GM grants. A small, yes/no decision, but genuinely his.
- **374#60** (ask:b7-residence-route): Three GM hand-drawn magistracy sheets draw a ~145-tsubo residence where research 0091 says 49-67; redraw all three, or keep the size as a recorded deviation? Held for the GM.
  - why: Test 1 (and 2): what to build. The choice is a wholesale redraw of the GM's own signature sheets versus keeping a known research deviation; the arbiter itself ruled it the GM's question.
- **385#21** (ask:t03-claims-at-landing): T03 lands under CLAIMS_OK with three findings on unchanged code carried to T12. The arbiter explicitly put to the GM how much checking a change owes: the claims gate refuses drift on unchanged code.
  - why: Test 1: a new standing rule of the project (when the claims gate may refuse a landing), which the arbiter itself said is the GM's to decide. The GM did answer it: spec 385 Amendment 3, 2026-10-17, 'lock in option three'. The row is now stale.
- **385#40** (ask:t06-single-file-short): Single file fits only some dispersed seeds. 14 of 20 keep HEAD's ranked seating, which 0031 says not to squeeze. The arbiter ordered a new feature filed (farmsteads carved within the paddy) as the research answer.
  - why: Test 1 and test 2. It decides what to BUILD: a new feature, which needs the GM's approval, and none is filed in specs/. It also accepts a known gap: most dispersed hamlets keep a seating the research page forbids.
- **374#81** (hour:374-match-the-research-continued@2): Hour-2 step-back ruled continue, but flagged for the GM that about 85 pop-up record checks ran on about six bamboo and shelter pop-ups in one batch (each wording edit re-owed the sibling checks, about 98 of 216 minutes spent waiting), and that the cascade tripwire never fired.
  - why: Test 4: check depth is out of proportion to the change, and the cascade guard meant to catch that did not fire. The tooling fix in this row only touched step-back timing, not the cascade, so this is a systemic cost the GM might want to fund a fix for. Whether a later cascade fix (e.g. feature 398's cascade@1) covers sibling re-owing is not stated in the row.
- **385#11** (ask:t03-d17-route): Ruled to land T03's four seed fixes and move the general side-by-side lane merge, which the GM's amendment-1 reply put in T03's scope, to a later task, because the merge regressed six seeds; seed 57 also worsened from 1 to 4 knots.
  - why: Test 1: it narrows scope the GM set in his own words ('the four seeds plus the general side-by-side merge'), and the arbiter itself says the GM must be told plainly so he is not again told 'done, but still failing'. Test 2 as well: Inashiro F1-F3 stays NEEDS-WORK on a pool map.
- **385#12** (hour:385-approach-checklist@6): Hour-6 step-back confirmed route (a) with a condition (bisect seed 57's extra knots before landing). Its for_gm says the GM's 'two paths side by side become one' does not land in T03 and Inashiro F1-F3 stays NEEDS-WORK until a later measured task.
  - why: Test 1 and test 2: a GM-requested behavior is deferred out of the task he scoped, and a visible defect on the Inashiro pool map stands meanwhile. This is the one item in this stretch he would want to know about.
- **385#106** (hour:385-approach-checklist@38): Hour 38 step-back: 385 is closing; for_gm asks the GM to decide, as one batch, whether to retire or re-measure the 22 of 45 tooling fixes that fix-yield reads as 'saves nothing'.
  - why: Tests 1 and 2: this answers a report the GM himself ordered (T119, his change 3), and retiring guards in bulk would weaken checks project-wide. The arbiter cannot rule it one row at a time. A weaker case for NO: the arbiter could have ordered a re-measurement itself and brought him only the result.
- **388#0** (hour:388-retire-roll-village@1): Hour 1 of 388: a rollback after the gate found frozen exhibits calling roll_village helpers; for_gm says four helpers were kept despite the GM's 'just delete it now', and which frozen exhibits must stay runnable is his call.
  - why: Test 1: it narrows a direct instruction from the GM ('just delete it now') and asks something only he can decide: whether the frozen legacy exhibits (Hikari-no-sato, Ueda, Hoshigaoka) must stay runnable.

## MAYBE

- **391#6** (hour:391-comparative-money-sources@3): Routine hour 3 of 391. Its for_gm: the session rewrote the CLAUDE.md rule 'a feature is filed only with the GM's approval' so features the GM asked for need no approval round, and asks the GM to confirm the wording.
  - why: Test 1: a session rewrote a standing rule built on the GM's words. The current CLAUDE.md quotes his 2026-10-18 words verbatim beside the new rule, so the rewrite looks faithful. It is YES only if the wording goes beyond what he said.
- **395#0** (hour:395-shrine-building-costs@1): Routine hour 1 of 395. Its for_gm: a 434 MB download (ruiju-kinsei-fuzokushi-ge) cannot go into the GitHub source archive without Git LFS or splitting the PDF.
  - why: Test 1 holds only if LFS (paid storage) is being weighed. Splitting is free and reversible, and the GM's 2026-10-25 rule ('take the algorithmically easier route and say which') points to it.
- **422#1** (ask:set-down-422): Feature 422, research-only, is set down despite set-down refusing at 87% of the 90% weekly cap. Five engine claims findings that claims-carry pushed into it move to the claims backlog. The arbiter flags 'for the GM' that a claims carry into a feature with no code change is a pattern to watch.
  - why: Test 4, and possibly test 1: the arbiter itself names a systemic fault (claims-carry dumping unrelated engine findings into a feature that changed no code) with no tooling fix. It also overrode a refusal tied to the GM's usage-cap rule. The row does not say whether the pattern recurs or whether overriding the cap-linked refusal is within the arbiter's remit.
- **400#2** (hour:400-campaign-costs-fruit-salt-hemp-wages@2): Hour-2 step-back on 400 found a clean check cycle and no route change, but its for_gm field carries two open questions: does a cell in a public .xls count as a readable page, and how to archive a 433 MB PDF (split it or use Git LFS).
  - why: Test 1, possibly: the .xls question sets a standing citation rule and Git LFS may cost money. The row does not say whether research-doctrine already settles .xls readability, or whether splitting the PDF (free and within the session's reach) was ruled out.
- **405#0** (hour:405-engine-findings-from-385@1): Hour-1 step-back on 405: a 5-minute fix was buried in about 20 minutes of reviews. The for_gm field asks whether the GM wants the Lands open line review at all for one-edit landings.
  - why: Test 4, possibly: a recurring process cost (landing takes about four times as long as the fix) that tooling has not fixed. The row does not say whether this is a one-off or a cost every 405 landing pays, nor whether the arbiter could simply drop the review itself.
- **412#0** (ask:412-record-round5): Round 5 is made the last round of 412's record checks. The why also flags that round 4 put a derived Chinese Repository rate of about 0.75 tael a dollar on the 0289 page, which the session's s4 log had marked 'the GM's call'.
  - why: Test 3, possibly: a money figure on a shipped page was chosen when the session had reserved that choice for the GM. But plan-done.md says both 0.75 and 0.71 tael a dollar are stated and the choice is left to the GM, so the page may show both, and under the knob rule (several attested values become a knob) it may not need him at all. The row does not say whether the money tool uses one value.
- **417#4** (ask:417-T29-drifted): 17 DRIFTED claims were allowed to land as the record's mark of known drift: the code departs from research (DOORSTEP_FT 80 vs 60, GABLE_MARGIN_FT 6 vs 3, and others) and each departure is filed as a fixing task. The arbiter also proposed narrowing the claims gate so it admits such relabels.
  - why: Test 2, possibly: the proposed tooling fix would permanently narrow the claims gate's refusal of introduced DRIFTED claims, a check weakened, though the change follows the GM's 2026-10-25 words that labels must say truthfully where code has drifted. The row does not say whether the narrowing was built, nor how it stops a landing that creates new drift from slipping through.
- **374#5** (round:modal-depiction|modal:sheet/nakamon@3): Accept on the nakamon pop-up: modal-depiction rule M11 re-adds a Guesses bullet that modal-form/modal-research delete; the arbiter closed the unit with the bullet removed and 'filed the conflict'.
  - why: Test 4 (faintly 3): two check contracts that conflict would loop on every pop-up of this shape, and stopping the loop settled what ships (a GUESS bullet dropped). Missing: whether the filed conflict was ever resolved in the agent contracts or tooling. If it was, this is NO.
- **385#0** (hour:385-approach-checklist@2): Hour-2 step-back ruled continue, but flagged for the GM that adding two bullets to 0081's drawing page put 217 claims into triage plus 58 impl-drift checks, because claims are invalidated by whole page, not by cited passage.
  - why: Test 4 if still unfixed: check work multiplies out of proportion to a small page edit, the same class as 374#81. The row's tooling fix was cohort tracebacks; 385#4 later fixed only the relabel-only case. Missing: whether claim invalidation is now scoped to the cited passage.
- **385#75** (hour:385-approach-checklist@22): Hour 22 step-back: work converged; for_gm asks whether a pop-up whose sources conflict should tell one reading or lay out the disagreement, and notes about 70 dispatches spent on sibling cards.
  - why: Test 1, possibly: how pop-ups handle conflicting sources would be a standing content rule that affects every card, and a grep of docs/ and research/CLAUDE.md found no rule on it. It is NO if the modal-form agent file or the style guide already settles it. The dispatch-cost note is process and does not belong to the GM.
- **335#2** (ask:f335-garden-modal-depiction): garden modal-depiction accepted after the check's EDITs were applied verbatim. The arbiter also called one leftover finding 'the GM's to decide': the generated county example draws the garden as plain stipple, not the pond or dry garden that research 0103 makes a knob.
  - why: Tests 2/3: the map is known to contradict research 0103, and the arbiter explicitly handed it to the GM. I read specs/335-*/found.jsonl, where line 11 has it as an open renderer row ('outside 335 sheets'). The row does not say whether any feature schedules it. Under the 2026-10-25 rule it is backlog work the record already settles, not a decision for the GM.
