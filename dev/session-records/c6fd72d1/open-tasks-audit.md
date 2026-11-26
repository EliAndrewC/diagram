# Open-tasks audit: what was filed Friday 2026-11-20 to Monday 2026-11-23, and why (features 449 and 451)

Read-only. Clone diagram-backlog at 52c982ddb0 (2026-11-24 09:15 -0500). Filing date = the first commit that added the task's
line to tasks.md / tasks-done.md, in the commit's own clock (-0500, the GM's local time). Every label below (kind, mechanism,
verdict) is mine, assigned from the task line's words: 449's 181 rows read at 250 to 900 characters each, 451's 215 rows at
about 320. Counts are **measured** from git plus those labels unless marked (estimated) or (inferred).

## Summary

1. **Opened against closed, Fri-Mon (measured).** 449: 176 filed, 162 closed (160 by work, 2 withdrawn) = 1.09 opened per closed.
   451: 205 filed (22 its own plan), 164 closed (157 by work, 7 withdrawn) = 1.25. No day reached two for one; the worst was
   449's Sunday, 116 against 92 (1.26). The loop was real, nearer one-for-one than two-for-one.
2. **449 by verdict (my labels, n=176).** SHOULD HAVE BEEN OPENED 72 (41%); REAL BUT SURFACED BY CHURN 48 (27%), true findings
   that appeared only because a check was re-run or aimed at old material; PROCESS-MADE 56 (32%).
3. **Bugs in ported code are a small part.** 23 rows name engine code or a newly ported stage's drawing. Hamlet engine
   (rust/phases) 9, all true: the polder stage's 5 found by its first review on Friday, 4 seat and belt faults found by churn.
   Mode A code 14: 4 found on the change, 8 by churn, 1 hypothetical (T301), 1 ruled a choice of form (T398). The other 99 true
   rows: Mode A sheets 34, record and pop-ups 25, research questions 21, tooling 13, port leftovers 6.
4. **Sunday's flood (inferred from the lines' references and the ledger).** T249's tool fix re-checked 63 old claim units and
   re-found the manor's known drifts (T265); fixing them redrew the magistracy sheets, and each redraw's review found layout
   faults the last fix made (T274 -> T288 -> T309 -> T320 -> T329 -> T353). About 47 of the 72 SHOULD rows sit under that root
   or T197's (estimated by mechanism, not traced row by row): needed once the sheets changed, which churn caused.
5. **451, the tooling's own loop (n=205).** 171 true: 22 plan, 20 the GM's requests, 55 tool faults met while working, 29 faults
   in tools built inside the window, 18 measured time sinks, 15 load flakes, 12 shell-reader over-refusals. 34 process-made: 22
   shell-reader shapes found by probe or plan review with no live case, 7 duplicates, 5 bookkeeping. 41 still open.
6. **Still in place.** (a) Outside-the-change filing: 52 of 449's 176 rows (30 true, 22 process-made), the largest mechanism;
   rule unchanged (impl-drift.md 121-124, 131-134; quote-check.md 192; building-review.md 88). (b) Redraw review: 29, kept by
   design; T176, T199, T214 cut only the nitpick and other-sheet cases. (c) Later rounds and leftovers: 20; T188-T190 cut most,
   yet the cascade test owed a third round and filed a NO-EDIT wording row (T410). (d) Restatements filed as tasks: 30, although
   XIV v2.36.0 (11-19) and the claims switch at report (10-28) were both in force: each line says "lands before T158" under
   the GM's 11-18 "fix all known bugs in each step". (e) Tooling fix-of-fix: 0.6 a rule task. (f) Stale copies after a change: 8.
7. **Closed, by replay only.** The cascade from a cited page moving (T185, T186, T191, T194, T196, T209-T213, T215): three real
   landings replayed, 147 and 22 forced claims down to 0; no fresh live change yet. Labels (T187, T192): 994 tags. Trims (T184).
8. **Tuesday (one bundle, so weak).** Git does not show "about 10 new 449 rows from 7": T405-T409 were filed Monday 11:29-11:37
   (03cc1514d1, 6dd0ad5a7c), before the rules. The cascade test closed 7 rows (2 withdrawn as not needed) and filed 5 in 449
   (T410-T414, commit 7fc9f06512) and 7 in 451 (T208-T214): 0.7 per closed row in 449, 1.7 with tooling. Of the 5: 3 outside
   findings on old material (T411, T413, T414), 1 old fault on a claim the triage sent (T412), 1 round-2 wording (T410); none a
   fault in what the 7 changed. After the six fixes: 451 closed 8, opened 3 (T215, T216 the GM's; T217 a fix-of-fix); 449 opened 0.
   That morning's claims round listed its one MISLABELED in claims-report and put its one outside finding in found.jsonl: the
   same finding in another queue, not a lower rate. 449's found.jsonl holds 68 open rows dated in the window (not matched to tasks).
9. **"Not two for one"?** For a record or pop-up change: supported, weakly (0.7; one bundle; every new row from (a) or (c)).
   For a sheet redraw: untested since the rules. For porting a hamlet stage, the next real work: the only data is Friday's
   polder stage, 10 rows from one stage, 5 of them true drawing faults no rule should remove.
10. **Uncertain.** One reader's labels (451 from 320 characters a line); item 4's tracing; replay-only proof; 56 rows entered in
    one commit Sunday 08:15 (up to 6 of 451's are Saturday's); whether an open found.jsonl row must become a task (no gate found).
11. **Biggest remaining source:** outside-the-change findings on old material, filed against the feature being landed: 0.32 per
    closed task in the window (52/162), 0.43 to 0.57 in the cascade test. 30 of the 52 were true, which is why the loop feels
    necessary. Undecided: whether such a row blocks the landing feature or queues elsewhere, as the 17 moved to 452 did.

## Mechanisms, feature 449 (Fri-Mon, n=176; counts measured from my labels)

| mechanism | code | rows | should / churn-real / process | still in place? | closed by, and the evidence |
|---|---|---|---|---|---|
| a check's finding "outside the change" on old material | OUT | 52 | 0 / 30 / 22 | partly open | Rule unchanged: impl-drift.md 121-124, 131-134; quote-check.md 192; building-review.md 88. Fewer old units are read since T186/T191/T176/T199, so fewer such findings arise (inferred). Cascade test: 3 of its 5 new rows. 2026-11-24 08:21: one went to found.jsonl, not a task (n=1). |
| review of a sheet a follow-up redrew, finding on that redraw | REDRAW | 29 | 27 / 0 / 2 | in place (kept) | A redrawn sheet is reviewed, by design. T176 (other sheets not re-owed), T199 and T214 (a nitpick fix carries the verdict; T214 proven by replay only). Untested live: nothing was redrawn after the rules. |
| a later round of the same check, or a check session's leftovers | ROUND | 20 | 1 / 4 / 15 | partly open | T188 (wording never re-owes), T189 (later round scoped), T190 (settled stays). Cascade test: T188 held, but 0334 owed a third round (arbiter accepted) and round 2 filed T410 with NO EDIT. |
| a check run on a follow-up's own record or code edit | CASC | 15 | 1 / 7 / 7 | mostly closed | T185, T186, T191, T194, T196, T209, T212, T213. Replay of landings 085f4598c3, cce80ca436, 7fc9f06512 (plan-done T209-T212). No fresh live change yet. |
| a tooling failure met while working | TOOL | 12 | 12 / 0 / 0 | in place | 12 in 449, 55 in 451; each is a fault in a guard, gate or check. |
| a research pass answered; its result put into the record or a sheet | PASS2REC | 10 | 9 / 1 / 0 | in place (kept) | Research doctrine; rate follows the questions asked (21 Q rows in the window). |
| a doc, note or drawing page left stale by our own change | STALE | 8 | 8 / 0 / 0 | in place | Needed work, filed apart from the change that caused it. T198 holds generated files current; hand-written copies are not covered. |
| old material re-checked because a tool or fingerprint moved | RECHECK | 7 | 0 / 6 / 1 | open for tool changes | T204, T211 (anchors), T210, T215 (regenerated rows): replay 147 and 22 forced to 0. Nothing stops a future fingerprint change (as T249) re-owing every unit. |
| first review of a newly ported stage | FIRST | 5 | 5 / 0 / 0 | in place (wanted) | The polder stage, Friday: 5 drawing faults. The GM 2026-11-24: real defects are fixed before new code. |
| work-budget bookkeeping | BUDGET | 4 | 0 / 0 / 4 | in place (kept) | Features 443/444. |
| port leftovers | PORT | 4 | 4 / 0 / 0 | n/a | Planned scope. |
| duplicate, folded or withdrawn | DUP | 3 | 0 / 0 / 3 | in place | Filed, then folded by a plan review or a second filing. |
| the GM's request | GM | 2 | 2 / 0 / 0 | n/a |  |
| the builder's own measurement | OWN | 2 | 2 / 0 / 0 | in place (wanted) | T384, T395: caption leaders through buildings. |
| a size trim | TRIM | 1 | 0 / 0 / 1 | closed | T184. Cascade test: 0097 over the cap was split to 0334, no trim; the new page owed 3 new-page checks. |
| a test failing good work under load | FLAKE | 1 | 1 / 0 / 0 | in place | 15 in 451, 1 in 449; three builders plus closing checks at load 15 to 130. |
| a deferred clause of another task | SPLIT | 1 | 0 / 0 / 1 | in place |  |

## Mechanisms, feature 451 (Fri-Mon, n=205)

| mechanism | code | rows | should / churn-real / process | still in place? | closed by, and the evidence |
|---|---|---|---|---|---|
| a tooling failure met while working | TOOL | 55 | 55 / 0 / 0 | in place | 12 in 449, 55 in 451; each is a fault in a guard, gate or check. |
| shell-command reader of the tree guards: each fix shows more shapes | SHELL | 34 | 12 / 0 / 22 | open, unworked | 16 of the 34 still open (T49, T51, T125-T134, T137, T138, T140, T144, T145); no rule stops a plan review listing new shapes. |
| a fault or leftover in a tool built inside the window (fix-of-fix) | NEWTOOL | 34 | 29 / 0 / 5 | in place | 16 rule tasks (T184-T193, T195-T200) -> 10 fix rows (T194, T201, T204, T209-T215), 0.6 per rule task. T217 on Tuesday. |
| the feature's own plan | PLAN | 22 | 22 / 0 / 0 | n/a | 451 T01-T22, one commit Friday 00:24. |
| the GM's request | GM | 20 | 20 / 0 / 0 | n/a |  |
| a measured time sink | MEAS | 18 | 18 / 0 / 0 | in place (wanted) | The GM's efficiency request. |
| a test failing good work under load | FLAKE | 15 | 15 / 0 / 0 | in place | 15 in 451, 1 in 449; three builders plus closing checks at load 15 to 130. |
| duplicate, folded or withdrawn | DUP | 7 | 0 / 0 / 7 | in place | Filed, then folded by a plan review or a second filing. |

## Per day (measured; git commit date, -0500)

| day | 449 filed (S / C / P) | 449 closed (work / withdrawn / moved) | 451 filed (S / P) | 451 closed (work / withdrawn) |
|---|---|---|---|---|
| Fri 11-20 | 10 (8 / 0 / 2) | 7 (7 / 0 / 0) | 58 (49 / 9) | 45 (43 / 2) |
| Sat 11-21 | 1 (1 / 0 / 0) | 0 (0 / 0 / 0) | 74 (58 / 16) | 61 (61 / 0) |
| Sun 11-22 | 116 (45 / 35 / 36) | 92 (91 / 1 / 0) | 35 (27 / 8) | 19 (17 / 2) |
| Mon 11-23 | 49 (18 / 13 / 18) | 63 (62 / 1 / 0) | 38 (37 / 1) | 39 (36 / 3) |
| Tue 11-24 (to 09:15) | 5 (0 / 2 / 3) | 24 (5 / 2 / 17) | 10 (10 / 0) | 8 (8 / 0) |

Closes count every box ticked that day, whenever its row was filed. Tuesday's 17 "moved" are the rows now open in 452.
Reconciling with followup-sources.md: it counted 115 lines carrying "lands before T158" (T254-T404); git has 165 rows filed
on the 22nd and 23rd, the other 50 being T245-T253, the rows that say "lands before T244" or nothing, and T405-T409.

## Estimates for the mechanisms still in place (new rows per landed change)

| mechanism | window rate (measured from labels) | cascade test (measured, n=1) | estimate going on |
|---|---|---|---|
| outside the change | 52 per 162 closed = 0.32 | 3 of 7 (4 with T412) = 0.43 to 0.57 | 0.2 to 0.5 a record or sheet change (estimated); unknown for an engine stage |
| later rounds, leftovers | 20 per 162 = 0.12 | 1 of 7 = 0.14 | about 0.1 (estimated) |
| redraw review | 29 rows, all on the five magistracy sheets | 0 (no redraw) | 0 unless a Mode A sheet is redrawn; then about 1 a redraw (estimated from T274-T356's chain, not counted per landing) |
| restatement filed as a task | 30 per 162 = 0.19 | 2 of 7 (T411, T414) | falls to near 0 only if claims-report takes them all, as it did once on 2026-11-24 |
| tooling fix-of-fix | 34 per 164 closed in 451 = 0.21 | 7 of 7 (T208-T214, six fixed the same day) | 0.6 a new rule (16 rule tasks T184-T193 and T195-T200 drew 10 fix rows: T194, T201, T204, T209-T215), near 0 with no new rules |

Sum for a record or pop-up change with no redraw: about 0.3 to 0.8 new 449 rows per closed row (estimated), below one, and
none of them from the change itself in the one bundle measured.

## Three things the brief asked that the tables do not show

- **The claims switch at report (feature 445, 2026-10-28).** It was in force all window, yet 30 restatement rows were filed as
  tasks, each "lands before T158", the lines citing the GM's 2026-11-18 "fix all known bugs in each step before porting the
  next" (T265, T287, T350 quote it). On 2026-11-24 08:21 one MISLABELED claim was listed by claims-report with no task
  (commit 851cb7b662); seven hours earlier the cascade test had filed a MISLABELED claim as T411. One listing is not yet a rule
  seen working.
- **found.jsonl is a second queue.** 449's holds 76 rows dated in the window: 68 open, 3 filed, 5 settled (measured, read from
  the file). Many of the 68 were also filed as tasks without their row being closed (T368-T370 name the file), so the number
  with no task lies between 0 and 68 and was not matched. The cascade test's commit added none.
- **The gap audit's items.** Items 3, 5-7 and 9-12 became T195-T200; items 1 and 2 look to be T193's and T201's subject (inferred from their lines). Items 4 (a
  split made as T184's refusal teaches is not seen as a move) and 8 (an edit to data-guess text is never reviewed) are named by
  no 451 task line (grep); their state in the code was not checked.

## Rubric (how each label was assigned)

- **Kind.** Dc engine code; Ds a drawn sheet or map; Dr the record says something false or contradicts itself; R a claim, doc
  or note that does not match while the drawing is fine; Q a research question; W wording, format, vocabulary; T tooling;
  PW planned work or the GM's request.
- **Verdict.** S (should have been opened): a wrong outcome found on the change being landed, port or planned work, a tool
  fault that blocked or misled work, or the work an answered research pass owed. C (real but surfaced by churn): kind Dc, Ds, Dr
  or Q, and the line says outside the change, a PASS sheet, "same on main", a re-check after a tool moved, or a check on a
  follow-up's own record edit. P (process-made): kind W however found; kind R, except where the drawing itself changed and
  its description was left behind (the 8 STALE rows) or a research pass's answer is being written in (PASS2REC's T330, T334,
  T361, T372), which are S; a nitpick; a hypothetical no map shows; budget bookkeeping; a duplicate; a shell-reader row with
  no live case. A builder's own measurement of ported code is S even where main shows the same (T395), since no re-run check
  surfaced it.
- **451.** Every row is tooling, so S means a real fault or measured waste and P means churn; the split between a live
  over-refusal (S) and a probe-found shape (P) among the 34 shell-reader rows is inferred from the line's first words.
- **Dates crossing the window's edge.** 449 T234 was found 2026-11-19 and filed Friday 01:09. 449 T411-T413 were found late on the
  23rd and filed Tuesday 00:59 with the cascade test. 451's lines date by another clock (T55: committed Fri 23:04, "measured
  2026-11-21"). No row is undated; none is unclassified, but these 449 verdicts are the least sure: T240, T257, T301, T317,
  T319, T341, T344, T374, T398, T412.

## Appendix: every row (id | filed | closed as | kind | mechanism | verdict | what)


### 449, Friday to Monday (176 rows)

449 T234 | 11-20 01:09 | done | Ds | FIRST | S | sluice drawn 8 ft square against 0179 (ported polder)
449 T235 | 11-20 01:09 | done | T | BUDGET | P | derivation prices work the Rust never does
449 T236 | 11-20 01:46 | done | Ds | FIRST | S | reed strip over the sluice cuts (ported polder)
449 T237 | 11-20 01:46 | done | T | TOOL | S | reviews owed has no rust/ drawing path (port gap)
449 T238 | 11-20 02:57 | done | T | TOOL | S | Rust placement change owes no review (port gap)
449 T239 | 11-20 04:33 | done | Ds | FIRST | S | settlement ground drawn over the dike (ported polder)
449 T240 | 11-20 04:33 | done | Ds | FIRST | S | two polder drawing points impl-drift could not confirm
449 T241 | 11-20 05:10 | done | T | TOOL | S | claims bundle leaves out a cited page
449 T242 | 11-20 06:43 | done | T | TOOL | S | plan-verdict writes unstyled words, next quick red
449 T243 | 11-20 22:23 | done | T | BUDGET | P | no budget change path for a pool-sheet stage (deferral re-filed by 451 T36)
449 T244 | 11-21 11:38 | done | PW | GM | S | stop before the parked hamlet stages
449 T245 | 11-22 08:15 | withdrawn | T | DUP | P | folded into 451 T142
449 T246 | 11-22 02:14 | done | T | DUP | P | mirror row of 451 T142
449 T247 | 11-22 08:15 | done | PW | PORT | S | last tracked Python deleted
449 T248 | 11-22 08:15 | done | PW | PORT | S | .py under specs/ against SC-005
449 T249 | 11-22 08:15 | done | T | TOOL | S | claim fingerprint misses account-cited pages (its fix re-checked 63 units)
449 T250 | 11-22 08:15 | done | T | BUDGET | P | bank bands priced by no derivation
449 T251 | 11-22 08:15 | done | PW | PORT | S | constitution's Python-era passages
449 T252 | 11-22 08:15 | done | PW | GM | S | constitution VI's one command
449 T253 | 11-22 08:15 | done | T | BUDGET | P | budget-change cannot set a 10-household figure
449 T254 | 11-22 08:15 | done | R | CASC | P | pop-up sizes rest only on a drawing page (modal-research on T197)
449 T255 | 11-22 08:15 | done | W | ROUND | P | 0004 opening wording, left by a closed check
449 T256 | 11-22 08:15 | done | Dr | CASC | C | farmhouse pop-up keeps a phrase T197 found unsupported
449 T257 | 11-22 08:15 | done | Dr | CASC | C | 0030 note fails quote-verbatim
449 T258 | 11-22 08:15 | done | T | TOOL | S | decide guard ties record checks to another builder's task
449 T259 | 11-22 08:15 | done | T | TOOL | S | work-budget-bundle reads a stale run file silently
449 T260 | 11-22 08:15 | done | Dr | RECHECK | C | 0091 and 0115 contradict on the servants' side
449 T261 | 11-22 08:15 | done | Dr | RECHECK | C | 0031 says every hamlet backs the wind, Sawada does not
449 T262 | 11-22 08:15 | done | R | CASC | P | pop-up statement rests on no Entry page
449 T263 | 11-22 08:15 | done | Ds | FIRST | S | polder feeder stops 8.5 ft short of the ring canal
449 T264 | 11-22 08:15 | done | R | RECHECK | P | bare GUESS label (claims-label lint)
449 T265 | 11-22 08:15 | done | Dc | RECHECK | C | two known manor drifts (417 T33's), re-found by the T249 re-check
449 T266 | 11-22 08:15 | done | Dr | OUT | C | 0222 notes still say what corrected findings do not
449 T267 | 11-22 08:15 | done | R | CASC | P | 'hearth' against 'kamado' in notes and an SVG comment
449 T268 | 11-22 08:15 | done | T | TOOL | S | set-down reads a foreground agent as a launch
449 T269 | 11-22 08:15 | done | T | TOOL | S | found-close cannot settle a no-defect row
449 T270 | 11-22 08:15 | done | R | CASC | P | pop-up Guesses tab lacks a page's new GUESS (label)
449 T271 | 11-22 08:15 | done | Dc | OUT | C | town place card drops farmhouses against 0004
449 T272 | 11-22 08:15 | done | R | CASC | P | pop-up Guesses tab lacks 0222's plinth GUESS (label)
449 T273 | 11-22 08:15 | done | PW | PORT | S | browser crate's test Chromium is Python (SC-005)
449 T274 | 11-22 08:15 | done | Ds | REDRAW | S | county granary re-sited (review of T265's redraw)
449 T275 | 11-22 08:15 | done | Q | REDRAW | S | armory size questionables (size-audit, new kind)
449 T276 | 11-22 08:15 | done | Ds | REDRAW | S | armory drawn on the four sheets without one
449 T277 | 11-22 08:15 | done | Dc | CASC | C | off-wind seat's belt ground on the wrong side (Sawada)
449 T278 | 11-22 08:15 | done | R | OUT | P | 0116 drawing page against the manor procedure's granary seat
449 T279 | 11-22 08:15 | done | R | OUT | P | docs give 113 x 28 ft where the page gives 113 x 38
449 T280 | 11-22 08:15 | done | Ds | REDRAW | P | nitpick: 7.5 ft lane by the karo's door
449 T281 | 11-22 08:15 | done | R | OUT | P | docs bullet 'behind the offices' against the seat it gives
449 T282 | 11-22 08:15 | done | R | CASC | P | pop-ups' Rokugan rules rest only on drawing pages
449 T283 | 11-22 08:15 | done | W | OUT | P | quote-check punctuation and heading findings
449 T284 | 11-22 08:15 | done | Q | CASC | C | five pop-ups' open form and research findings (modal-form M5)
449 T285 | 11-22 08:15 | done | R | OUT | P | hill exception missing for a sheet on no map (no such sheet exists)
449 T286 | 11-22 08:15 | done | W | OUT | P | 0222 record findings from rounds 2 to 11
449 T287 | 11-22 08:15 | done | Dc | RECHECK | C | country shrine dwelling's two known drifts
449 T288 | 11-22 08:49 | done | Ds | REDRAW | S | karo's door onto open court again (made by T274's fix)
449 T289 | 11-22 08:49 | done | Q | REDRAW | S | where a seat with a barracks kept its arms
449 T290 | 11-22 08:49 | done | Dc | REDRAW | S | armory size band admits 6.7x the anchor
449 T291 | 11-22 08:49 | done | Ds | OUT | C | no formal entrance facing the gate (N2 outside)
449 T292 | 11-22 11:10 | done | Dc | CASC | C | polder seat's belt takes no side (Kuwabata)
449 T293 | 11-22 11:10 | done | Dc | OUT | C | oblique wind's belt room laps past the field edge
449 T294 | 11-22 11:10 | done | Dc | OUT | C | band-end belt lies outside the kept ground
449 T295 | 11-22 11:10 | done | R | ROUND | P | armory gate-range seat recorded on 0093 (arbiter route b)
449 T296 | 11-22 11:10 | done | Q | OUT | C | main-gate pop-up's two M5 gaps
449 T297 | 11-22 11:10 | done | Ds | RECHECK | C | Ochiba's bare ground, an October finding still open
449 T298 | 11-22 11:10 | done | R | STALE | S | notes still say 'no armory' after T276 drew one
449 T299 | 11-22 11:10 | done | Ds | REDRAW | S | the armory's way out of the office hall
449 T300 | 11-22 11:10 | done | Ds | OUT | C | rows the building-reviews filed outside their change
449 T301 | 11-22 11:12 | done | Dc | OUT | P | windbreak_default's unchecked quarter (no map pairs them)
449 T302 | 11-22 17:57 | done | R | STALE | S | docs' two knob copies lack T285's hill exception
449 T303 | 11-22 17:57 | done | Q | PASS2REC | S | knob 4's third form from T289's research pass
449 T304 | 11-22 17:57 | done | R | OUT | P | arch count for a sheet on no map (no such sheet exists)
449 T305 | 11-22 17:57 | done | W | OUT | P | record findings outside T282/T283's page changes
449 T306 | 11-22 17:57 | done | Dr | ROUND | C | Ubame notes give a reason no GM note carries
449 T307 | 11-22 17:57 | done | Dr | CASC | C | byre pop-ups describe a wing the engine never draws
449 T308 | 11-22 17:57 | done | Q | OUT | C | the gatekeepers' place as a knob of its own
449 T309 | 11-22 17:57 | done | Ds | ROUND | S | county barracks out-sizes its residence against 0116's rank
449 T310 | 11-22 17:57 | done | Dr | OUT | C | 0113's unqualified absence against 0104's new measure
449 T311 | 11-22 17:57 | done | W | ROUND | P | 'arrow lane' undefined (record-format, three rounds)
449 T312 | 11-22 17:57 | done | Ds | REDRAW | S | dais drawn over the hall's only forecourt door
449 T313 | 11-22 17:57 | done | Ds | REDRAW | S | official study 2.8x its anchor (size-audit)
449 T314 | 11-22 17:57 | done | Ds | REDRAW | S | county rear ground contradicts its own source
449 T315 | 11-22 17:57 | done | Ds | REDRAW | S | day office 1.8x its anchor (size-audit)
449 T316 | 11-22 17:57 | done | Ds | REDRAW | S | dais 1.7x its anchor (size-audit)
449 T317 | 11-22 17:57 | done | Dc | OUT | C | place card contradicts itself on a declared NW wind
449 T318 | 11-22 17:57 | done | W | ROUND | P | stale session comment in 0220's notes
449 T319 | 11-22 17:57 | done | R | OUT | C | 0123's 'faced south, by regulation' rests on an unchecked note
449 T320 | 11-22 17:57 | done | Ds | REDRAW | S | county after T309: E2 and stale notes
449 T321 | 11-22 17:57 | done | R | OUT | P | storehouse bands overlap the barracks' (no sheet wrong)
449 T322 | 11-22 17:57 | done | W | ROUND | P | record vocabulary left by page checks
449 T323 | 11-22 17:57 | done | Dr | OUT | C | two absence notes may describe pages not read
449 T324 | 11-22 17:57 | done | W | ROUND | P | two unread leads put on the download list
449 T325 | 11-22 17:57 | done | R | ROUND | P | two pop-ups' leftovers (size per sheet)
449 T326 | 11-22 18:10 | done | Ds | OUT | C | round trip's three outside rows
449 T327 | 11-22 18:32 | done | Q | OUT | C | road banding drawn with no page recording it
449 T328 | 11-22 20:14 | done | Ds | PASS2REC | S | road bands removed after T327's research pass
449 T329 | 11-22 20:14 | done | Ds | REDRAW | S | county recomposition (genkan off the gate's line)
449 T330 | 11-22 20:14 | done | R | PASS2REC | S | page session putting the T312 passes into the record
449 T331 | 11-22 20:14 | done | Ds | OUT | C | garrison privy 0.5 ft off the granary (same on main)
449 T332 | 11-22 20:14 | done | Ds | ROUND | P | Ochiba's two leftover nitpick rows
449 T333 | 11-22 20:14 | done | W | OUT | P | record follow-ups: unfetchable source, notes
449 T334 | 11-22 20:49 | done | R | PASS2REC | S | pop-ups given the T330 answers
449 T335 | 11-22 20:49 | done | Ds | REDRAW | S | round trip's office hall after T312/T326
449 T336 | 11-22 20:49 | done | Ds | REDRAW | S | writing and binding rooms oversized (size-audit)
449 T337 | 11-22 20:49 | done | Q | REDRAW | S | what stands behind the dais after the reorder
449 T338 | 11-22 20:49 | done | R | STALE | S | captions, comments and notes after the reorder
449 T339 | 11-22 20:49 | done | Ds | OUT | C | two outside rows (Ubame household door onto the alley)
449 T340 | 11-22 20:49 | done | R | OUT | P | side gate's band recorded (PASS on content)
449 T341 | 11-22 23:27 | done | Ds | OUT | C | cart gates wider than the side gate band T340 recorded
449 T342 | 11-22 23:27 | done | R | STALE | S | 0088 drawing page still describes the bands T328 removed
449 T343 | 11-22 23:27 | done | R | OUT | P | 0116 drawing page against docs on an attached privy
449 T344 | 11-22 23:27 | done | Dr | OUT | C | 0101 makes one instance the general rule (and notes)
449 T345 | 11-22 23:27 | done | T | TOOL | S | page cache holds a bot-check page
449 T346 | 11-22 23:27 | done | Q | CASC | C | docs' inner-court postern rule has no source
449 T347 | 11-22 23:27 | done | R | ROUND | P | claims DRIFTED with fix: claim (T330 bundle)
449 T348 | 11-22 23:27 | done | Q | ROUND | C | inner court's ground and wall unrecorded (modal-form)
449 T349 | 11-22 23:27 | done | R | OUT | P | no page records the side gate's drawn posts as a convention
449 T350 | 11-22 23:27 | done | Dc | RECHECK | C | manor's two other known drifts, found again
449 T351 | 11-22 23:27 | done | W | REDRAW | P | nitpick: notes do not say who works the writing rooms
449 T352 | 11-22 23:27 | done | R | STALE | S | magistracy notes not brought to the T328-T340 drawing
449 T353 | 11-22 23:27 | done | Ds | REDRAW | S | gatehouse left 40 ft from the gate T329 moved
449 T354 | 11-22 23:27 | done | Ds | REDRAW | S | round trip's hearing court after T335
449 T355 | 11-22 23:27 | done | Ds | REDRAW | S | unnamed band after T332 moved the archive
449 T356 | 11-22 23:27 | done | Ds | REDRAW | S | county after T329's gate move (cell by the gate)
449 T357 | 11-22 23:27 | done | Ds | REDRAW | S | darker square where two paths overlap
449 T358 | 11-22 23:27 | done | Q | OUT | C | did a jin'ya hall keep a corridor (reviews' O rows)
449 T359 | 11-22 23:27 | done | Ds | OUT | C | cinnabar workshop drawn with the shrine's mark (same on main)
449 T360 | 11-22 23:27 | done | R | STALE | S | 0106 drawing page gives the long-house T329 redrew
449 T361 | 11-23 00:56 | done | R | PASS2REC | S | three record-page follow-ups from research passes
449 T362 | 11-23 00:56 | done | W | OUT | P | title in a quoted passage with no glossary term
449 T363 | 11-23 00:56 | done | R | ROUND | P | landing leftovers: DRIFTED fix: claim, UNCLAIMED rows
449 T364 | 11-23 00:56 | done | Ds | REDRAW | S | county granary exceeds its residence block
449 T365 | 11-23 00:56 | done | R | ROUND | P | two procedure claims left by impl-drift
449 T366 | 11-23 00:56 | done | Dc | ROUND | C | refusal message names a seat 0123 rejects
449 T367 | 11-23 00:56 | done | Dc | OUT | C | armory always in the west bay where 0123 finds the side varied
449 T368 | 11-23 00:56 | done | R | OUT | P | dais optional in the program table (every sheet has one)
449 T369 | 11-23 00:56 | done | R | OUT | P | 0218 drawing page gives the shrine a tree as a finding (label)
449 T370 | 11-23 00:56 | done | R | OUT | P | 0190 drawing page does not record the second board
449 T371 | 11-23 04:23 | done | R | ROUND | P | 0104 drawing page's porch against Ochiba's hand sheet
449 T372 | 11-23 04:23 | done | R | PASS2REC | S | junior officials' lodging and cell seat into the record
449 T373 | 11-23 04:23 | done | R | STALE | S | three drawing pages state what the sheets no longer draw
449 T374 | 11-23 04:23 | moved | Dr | PASS2REC | C | docs cite a cart gate from an OCR misreading
449 T375 | 11-23 04:23 | done | Ds | PASS2REC | S | household's way redrawn off the working rooms
449 T376 | 11-23 04:23 | done | Q | OUT | C | two pop-ups leave a look question open (modal-form)
449 T377 | 11-23 04:23 | done | T | TOOL | S | redrawn.rs owes every compound map's whole legend
449 T378 | 11-23 04:23 | withdrawn | R | CASC | P | shrine-tree claim DRIFTED after T369 (label)
449 T379 | 11-23 04:23 | withdrawn | W | DUP | P | withdrawn: fixed in the T358 bundle
449 T380 | 11-23 04:23 | moved | W | OUT | P | PASS sheets' notes and comments (nitpicks, outside)
449 T381 | 11-23 04:23 | done | Q | OUT | C | official study's seat (a PASS sheet's finding)
449 T382 | 11-23 04:23 | done | Q | OUT | C | did a magistracy keep a waiting shed
449 T383 | 11-23 04:23 | done | T | TOOL | S | pack-audit reads a practice ground as unbuilt
449 T384 | 11-23 04:23 | done | Dc | OWN | S | caption placer's leaders cross buildings (county)
449 T385 | 11-23 04:23 | done | W | TRIM | P | two questions 65 and 44 bytes over the size cap
449 T386 | 11-23 04:23 | moved | Q | REDRAW | S | how menservants lodged (re-review Q1)
449 T387 | 11-23 04:23 | moved | Q | REDRAW | S | was a hearing court screened (re-review Q2)
449 T388 | 11-23 04:23 | done | Ds | OUT | C | stables' only door into the grooms' room
449 T389 | 11-23 04:23 | moved | Q | REDRAW | S | how long a junior officials' rowhouse ran (glyph-check)
449 T390 | 11-23 04:23 | moved | R | OUT | P | two out-of-change docs rows restated
449 T391 | 11-23 04:23 | done | T | FLAKE | S | diffrun's timeout test fails under load
449 T392 | 11-23 07:49 | done | Ds | PASS2REC | S | official study re-seated per T381's pass
449 T393 | 11-23 07:49 | moved | R | SPLIT | P | county notes re-cited (T372's deferred clause)
449 T394 | 11-23 07:49 | done | Q | ROUND | C | what a staff rowhouse was built of (modal-form M5)
449 T395 | 11-23 09:19 | done | Dc | OWN | S | Ochiba's latrine leader through the stables (same on main)
449 T396 | 11-23 07:49 | moved | R | ROUND | P | three claims restated to moved pages
449 T397 | 11-23 09:19 | done | Dc | OUT | C | door_lane takes only the first end door
449 T398 | 11-23 09:19 | done | Dc | OUT | P | gatehouse seat (arbiter: a choice of form, not a defect)
449 T399 | 11-23 07:49 | withdrawn | W | OUT | P | note join mark (cascade test: not needed)
449 T400 | 11-23 07:49 | done | R | ROUND | P | 'deliberate simplification' claims (no map or check effect)
449 T401 | 11-23 09:19 | done | Ds | OUT | C | stables' ridge across the shorter side
449 T402 | 11-23 09:19 | done | Dc | CASC | S | leader to a dashed line ends on bare paper
449 T403 | 11-23 09:19 | done | Q | REDRAW | S | the stables' gable door (after T388's fix)
449 T404 | 11-23 09:19 | moved | Q | OUT | C | the stalls' rear doors
449 T405 | 11-23 11:29 | moved | Q | PASS2REC | S | 0108 takes JAANUS's depth (T401's search pass)
449 T406 | 11-23 11:29 | moved | R | STALE | S | 0093 drawing page states the knob T398 drew
449 T407 | 11-23 11:29 | done | W | ROUND | P | notes nitpicks (cascade test: one of three needed)
449 T408 | 11-23 11:29 | moved | Ds | OUT | C | Ubame's garden bed 1.3 ft off the veranda
449 T409 | 11-23 11:37 | done | Dr | OUT | C | official-study About states a guess as history

### 449, Tuesday 2026-11-24 (the comparison group) (5 rows)

449 T410 | 11-24 00:59 | moved | W | ROUND | P | term with no gloss on 0334 (round 2, NO EDIT)
449 T411 | 11-24 00:59 | moved | R | OUT | P | grave markers claim MISLABELED
449 T412 | 11-24 00:59 | moved | Dc | CASC | C | modest shrine always a wooden hall (two attested forms)
449 T413 | 11-24 00:59 | moved | Ds | OUT | C | burial ground drawn without 0235's stones
449 T414 | 11-24 00:59 | moved | R | OUT | P | 0097 drawing page against docs on the row's length

### 451, Friday to Monday (205 rows)

451 T01 | 11-20 00:24 | done | PW | PLAN | S | `spec-fidelity` PLAN REVIEW of plan.md, recorded with `make plan-verdi
451 T02 | 11-20 00:24 | done | PW | PLAN | S | One make detector: `shared::make::invoked` (the targets in command ord
451 T03 | 11-20 00:24 | done | PW | PLAN | S | The category table and the line's task: the shared `bucket_of` table (
451 T04 | 11-20 00:24 | done | PW | PLAN | S | A background run's end: `bg` on a backgrounded Bash call's PostToolUse
451 T05 | 11-20 00:24 | done | PW | PLAN | S | The Rust checks' phase lines: `build`, `test`, `cover-build` (per fami
451 T06 | 11-20 00:24 | done | PW | PLAN | S | The landing's phase lines: `cheap`, `gate`, `cohort`, `claims`, `push`
451 T07 | 11-20 00:24 | done | PW | PLAN | S | An agent's cost and task: `task` on the Agent dispatch line from its d
451 T08 | 11-20 00:24 | done | PW | PLAN | S | `make where-time`'s columns - tests, compile, gate, land, review, mode
451 T09 | 11-20 00:24 | done | PW | PLAN | S | `make where-time`'s background-run column: a launch paired with its en
451 T10 | 11-20 00:24 | done | PW | PLAN | S | `make where-time`'s critical path apart from the summed agent-minutes,
451 T11 | 11-20 00:24 | done | PW | PLAN | S | `make feature-report` reads the same columns through `where_time/colum
451 T12 | 11-20 00:24 | done | PW | PLAN | S | The context cap: a new guard `context_cap_hooks` refusing a builder's 
451 T13 | 11-20 00:24 | done | PW | PLAN | S | A builder resumed: `context_cap_hooks` refuses a SendMessage to a buil
451 T14 | 11-20 00:24 | done | PW | PLAN | S | The third `make static`: a new guard `static_runs_hooks` refusing a ta
451 T15 | 11-20 00:24 | done | PW | PLAN | S | A run the harness cannot track: `no_poll_hooks` refuses a make or carg
451 T16 | 11-20 00:24 | done | PW | PLAN | S | A main-session wait slower than its check: `no_poll_hooks` refuses, on
451 T17 | 11-20 00:24 | done | PW | PLAN | S | The deferral's form: `make decide` refuses a found-and-left deferral w
451 T18 | 11-20 00:24 | done | PW | PLAN | S | `make land T="T1,T2"` read as `T="T1 T2"`, in `rust/gate/crates/land/s
451 T19 | 11-20 00:24 | done | PW | PLAN | S | `make task-add` runs each of `make quick`'s checks to its own end over
451 T20 | 11-20 00:24 | done | PW | PLAN | S | The shard form - `tests/hooks/test-<name>.<k>.sh`, each shard a job un
451 T21 | 11-20 00:24 | done | PW | PLAN | S | The three slowest suites split into shards where it speeds the run (me
451 T22 | 11-20 00:24 | open | PW | PLAN | S | (waits: a full day after T02-T21 land) The close: on the first full da
451 T23 | 11-20 01:46 | done | T | TOOL | S | Two builders' cargo runs in one clone corrupt each other's coverage (f
451 T24 | 11-20 01:46 | done | T | TOOL | S | A gate test reads the real environment (found by T02, 2026-11-20): rus
451 T25 | 11-20 02:12 | done | T | TOOL | S | make decide's figure lint stops at its first finding (found writing T2
451 T26 | 11-20 02:57 | done | T | TOOL | S | The event log files a line under the clone's .specify/feature.json, no
451 T27 | 11-20 05:10 | withdrawn | T | DUP | P | Withdrawn: folded into T25 (T25's plan review, 2026-11-20, BLOCKED its
451 T28 | 11-20 07:59 | done | PW | GM | S | Performance work goes first (FR-013, the GM 2026-11-20): a [perf] tag 
451 T29 | 11-20 09:23 | done | T | TOOL | S | make set-down leaves the feature's started-task mark (found landing T0
451 T30 | 11-20 09:23 | withdrawn | T | DUP | P | Withdrawn: folded into T15 (T15's plan review, 2026-11-20, ruled leavi
451 T31 | 11-20 09:23 | done | T | SHELL | S | main-tree refuses a read as a write (found by T15's corpus replay, 202
451 T32 | 11-20 10:19 | done | T | TOOL | S | Guard tests read the real environment (found by T14, 2026-11-20): with
451 T33 | 11-20 10:19 | done | T | SHELL | P | guard_file_hooks refuses sed -i on a guard source but lets a Python he
451 T34 | 11-20 10:19 | done | T | MEAS | S | No make target formats one file (found by T14, 2026-11-20): make forma
451 T35 | 11-20 10:53 | done | T | FLAKE | S | Two timing tests fail under load (found by T12, 2026-11-20): rustc's a
451 T36 | 11-20 10:53 | done | T | NEWTOOL | P | The archived deferrals T17's replay found (2026-11-20): 449 T156, T200
451 T37 | 11-20 11:38 | done | T | TOOL | S | The plan-review bundle cuts a decision at its list (found by T19's pla
451 T38 | 11-20 12:39 | done | T | TOOL | S | Gate crates' tests read the real environment through the guard (found 
451 T39 | 11-20 12:39 | done | T | TOOL | S | A FRESH=1 test run may replay another run's result (found by T32, 2026
451 T40 | 11-20 14:04 | done | T | MEAS | S | entry-gate's case-4 chain sets hooks-test's full-run wall (found by T2
451 T41 | 11-20 14:37 | done | T | TOOL | S | A neighbor's uncompiling guard edit blocks every gate command (found b
451 T42 | 11-20 15:44 | done | T | SHELL | P | main-tree and gm-tree judge no Python program run from stdin (found by
451 T43 | 11-20 15:44 | done | T | MEAS | S | Every owed-units computation re-reads every record page at the merge b
451 T44 | 11-20 17:34 | done | T | NEWTOOL | S | py_c reads every subprocess call as a writer (found by T42, 2026-11-20
451 T45 | 11-20 17:34 | done | T | FLAKE | S | house_style_hooks' verdict varies under load (found by T42's replay, 2
451 T46 | 11-20 17:34 | done | T | TOOL | S | The plan-review bundle gives a reviewer the wrong decision (found by T
451 T47 | 11-20 18:32 | done | T | FLAKE | S | The pages crate's coverage misses runner/watch.rs line 271 in one make
451 T48 | 11-20 18:32 | done | T | TOOL | S | The bundle reads ids inside a clause naming another feature as the rev
451 T49 | 11-20 21:25 | open | T | SHELL | P | (waits: T110 lands) gate_write_hooks lets through a write into the tre
451 T50 | 11-20 21:25 | done | T | SHELL | P | shared::tree's git_write reads 12 writing git subcommands as reads (fo
451 T51 | 11-20 21:25 | open | T | SHELL | P | (waits: T138 lands) A program run from a script file (python3 $S/x.py)
451 T52 | 11-20 22:23 | open | T | NEWTOOL | P | (waits: T51 lands) The make-call readers that skip shared::make (the 4
451 T53 | 11-20 22:23 | done | T | NEWTOOL | S | Three T26 leftovers (found by 451 T36): make events-refile DRY=1 still
451 T54 | 11-20 22:23 | done | T | TOOL | S | The stale-terms guard refuses a review on a common word (found 2026-11
451 T55 | 11-20 23:04 | done | T | MEAS | S | A builder's closing checks run one after another and block its writing
451 T56 | 11-20 23:04 | done | T | NEWTOOL | S | make events-refile leaves 23 lines in 385's log (found by T53, 2026-11
451 T57 | 11-20 23:04 | done | T | MEAS | S | A crate's tests run twice, once plain in make rust-test and again in i
451 T58 | 11-20 23:04 | done | T | MEAS | S | rust/guard is the root of 27 gate crates, so any guard edit rebuilds t
451 T59 | 11-21 00:31 | done | T | NEWTOOL | S | The guard's SubagentStop tok field is short (found by T10, 2026-11-21:
451 T60 | 11-21 00:31 | done | T | NEWTOOL | S | The context cap names a builder's handoff under the call's working dir
451 T61 | 11-21 00:31 | done | T | TOOL | S | The wait's proof-of-life check ends a live wait as gone (found by T55'
451 T62 | 11-21 01:38 | done | T | TOOL | S | The clone-claim backstop refuses the first Edit or Write of a clean cl
451 T63 | 11-21 01:38 | done | T | SHELL | S | The make-only guard refuses a read-only Python heredoc over the event 
451 T64 | 11-21 01:38 | done | T | NEWTOOL | S | T55's order notice counts a code edit already landed (found 2026-11-21
451 T65 | 11-21 02:23 | done | T | TOOL | S | The set-down guard counts a resumed agent as finished (found 2026-11-2
451 T66 | 11-21 02:23 | done | T | NEWTOOL | S | Nothing pins T58's rebuild count (found by T58, 2026-11-21: a hook edi
451 T67 | 11-21 02:23 | done | T | SHELL | S | The README guard refuses a cp of a hook's source to /tmp (found by T58
451 T68 | 11-21 03:32 | done | T | NEWTOOL | S | The context cap read an advisor-carrying row's usage as the builder's 
451 T69 | 11-21 04:21 | done | T | NEWTOOL | S | The event log's tok leaves out the advisor's own tokens (found by T68,
451 T70 | 11-21 04:21 | done | T | FLAKE | S | rust/browser's real-Chromium test fails good work under load (found by
451 T71 | 11-21 04:21 | done | T | NEWTOOL | S | A wait on a file an agent appends from its own separate Bash calls sti
451 T72 | 11-21 05:07 | done | T | NEWTOOL | S | Two make closing-checks runs in one clone share .git/closing-checks/ a
451 T73 | 11-21 05:07 | done | T | NEWTOOL | S | The stale-terms check reads a subject re-wrapped onto the next line as
451 T74 | 11-21 06:51 | done | T | TOOL | S | The event log files a call under its working directory's tree, so a ca
451 T75 | 11-21 06:51 | done | T | SHELL | P | The README guard refuses a README path held as the text of a one-line 
451 T76 | 11-21 07:30 | done | T | NEWTOOL | S | The mirror's .git/l7r-events/_unassigned.jsonl holds 13 lines the refi
451 T77 | 11-21 07:30 | done | T | TOOL | S | The plan hold refuses an edit that starts exactly where a held section
451 T78 | 11-21 08:14 | done | T | TOOL | S | The plan hold refuses a shell write that shares only template text wit
451 T79 | 11-21 08:14 | done | T | SHELL | P | shared::tree's walk splits a `\`-continued line and a `${VAR}`'s brace
451 T80 | 11-21 11:26 | done | T | TOOL | S | The plan hold's write-back restores nothing for a task whose headings 
451 T81 | 11-21 11:26 | done | T | FLAKE | S | house_style_hooks' million-step timing test fails good work under load
451 T82 | 11-21 11:26 | done | T | TOOL | S | The plan bundle's requirement reader reads only '- **FR-NNN**' and mis
451 T83 | 11-21 11:26 | done | T | SHELL | P | shared::tree's walk blanks a quoted word that holds a space or a shell
451 T84 | 11-21 11:26 | done | T | MEAS | S | A builder stops short of ready-to-land and hands its last steps back (
451 T85 | 11-21 11:26 | done | T | MEAS | S | The Stop hook's run-still-going refusal fires on runs a still-running 
451 T86 | 11-21 11:26 | done | T | MEAS | S | A builder's closing checks go red on another builder's half-done files
451 T87 | 11-21 11:26 | done | T | SHELL | S | make-only refuses a guard file's name written in a scratch tree as a g
451 T88 | 11-21 11:26 | done | T | MEAS | S | Builders run three at once only 26% of the time because tasks are disp
451 T89 | 11-21 11:26 | done | T | SHELL | S | py_c judges a `python3 -c` program that writes a place it computes fro
451 T90 | 11-21 11:26 | done | T | SHELL | S | (waits: T118 lands) gate-write reads a target's command from its segme
451 T91 | 11-21 11:26 | done | T | SHELL | S | T79's bind rule refuses two kinds of scratch write HEAD allowed (found
451 T92 | 11-21 11:26 | done | T | TOOL | S | An arbiter's accept on one task's plan round records CLEAR for every c
451 T93 | 11-21 12:16 | done | T | NEWTOOL | S | The event log's Bash lines carry no write paths, so T86's closing chec
451 T94 | 11-21 12:16 | done | T | TOOL | S | The land crate's tests read the session's PLAN_REVIEW_OK and write the
451 T95 | 11-21 12:16 | done | T | NEWTOOL | S | make closing-checks' BLOCKED tag misses a coverage red (found by T86's
451 T96 | 11-21 13:32 | done | T | NEWTOOL | S | A Bash call's Python program run from a heredoc or -c names no file in
451 T97 | 11-21 13:32 | done | T | MEAS | S | shared::tree's walk compiles its patterns on first use in every hook p
451 T98 | 11-21 13:32 | done | T | MEAS | S | (waits: a full day after T88 lands) Builder occupancy after T88 is unm
451 T99 | 11-21 13:32 | done | T | FLAKE | S | test-idle-tests-hooks.sh's wall-clock case fails good work under load 
451 T100 | 11-21 13:32 | withdrawn | T | DUP | P | Withdrawn: fixed by T171 (253f81afa7) for its finished-run half, and i
451 T101 | 11-21 14:37 | done | T | TOOL | S | make land refuses a ready task while the clone's one active-task mark 
451 T102 | 11-21 15:16 | done | T | NEWTOOL | S | Rolling dispatch names a task that waits on a measured day (found 2026
451 T103 | 11-21 15:54 | done | T | MEAS | S | shared::shape's strip_heredocs and strip_quotes build their patterns o
451 T104 | 11-21 14:58 | open | T | FLAKE | S | Two more of test-idle-tests-hooks.sh's cases can fail good work (found
451 T105 | 11-21 20:51 | done | T | TOOL | S | land-alone's take-back gives up on a file both sides changed the same 
451 T106 | 11-21 16:40 | done | T | NEWTOOL | S | A builder's event-log lines keep the task its brief named after the co
451 T107 | 11-22 08:15 | open | T | FLAKE | S | The bundle crate's rare-paths depiction test fails good work under loa
451 T108 | 11-21 15:54 | done | T | NEWTOOL | S | The quoted-string pattern that hung a guard also stands at shared::wai
451 T109 | 11-22 08:15 | open | T | NEWTOOL | P | T92's wording left after its CLEAR (found by T92's builder, 2026-11-21
451 T110 | 11-21 20:13 | done | T | SHELL | S | (waits: T96 lands) The Python program reader (shared::tree::program, T
451 T111 | 11-21 17:03 | done | T | FLAKE | S | The stall-watchdog suite's case 4 fails good work under load (found 20
451 T112 | 11-21 16:30 | done | T | SHELL | S | The quoted-string pattern T103 and T108 gave shape's scan still stands
451 T113 | 11-21 16:30 | done | T | SHELL | S | The quoted-string pattern T103 and T108 gave shape's scan still stands
451 T114 | 11-21 17:51 | done | T | TOOL | S | A rustfmt rewrap after a green cover makes lines no test reaches, foun
451 T115 | 11-21 17:03 | done | T | FLAKE | S | Fixed sleeps in four hook suites wait 0.3-1.0 s for an event the next 
451 T116 | 11-22 08:15 | open | T | TOOL | S | (waits: T87 lands) make guard-edit for a file outside any repository w
451 T117 | 11-22 08:15 | open | T | TOOL | S | discard_hooks lets git worktree remove --force through on a worktree h
451 T118 | 11-21 21:02 | done | T | SHELL | S | (waits: T110 lands) shared::tree::program reads two Python shapes as w
451 T119 | 11-22 08:15 | withdrawn | T | DUP | P | Withdrawn: folded into T116 (the same stray permit, filed twice on 202
451 T120 | 11-21 18:39 | open | T | TOOL | S | The plan hold's refusal judges a task section whose own headings stand
451 T121 | 11-21 20:13 | open | T | TOOL | S | A crate-wide make format reformats other builders' uncommitted files (
451 T122 | 11-21 20:13 | open | T | NEWTOOL | S | closing-checks' set-apart note names no file-scale red of another task
451 T123 | 11-21 20:13 | done | T | TOOL | S | A plan hold reaches a tree it was not taken in, and checks_hooks' test
451 T125 | 11-21 20:13 | open | T | SHELL | P | (waits: T110 lands) shared::tree::program names no write onto a root t
451 T126 | 11-21 21:00 | open | T | SHELL | P | guard-file's Read reminder tells a scratch copy of a guard file it is 
451 T127 | 11-21 21:00 | open | T | SHELL | P | shared::tree's env_from reads an assignment's value from the command's
451 T128 | 11-21 21:00 | open | T | SHELL | P | make-only's by-name clear overrules the text patterns over the whole c
451 T129 | 11-21 22:29 | done | T | SHELL | S | (waits: T83 lands) shared::tree's ASSIGN pattern keeps its `(?<!\$)\{`
451 T130 | 11-21 21:00 | open | T | SHELL | P | the shell walk does not read CDPATH, so a cd it moves is placed where 
451 T131 | 11-21 21:00 | open | T | SHELL | P | make-only's Python patterns read a program's string literals as its co
451 T132 | 11-21 21:00 | open | T | SHELL | P | shared::tree's quote scan pairs quotes flat, so one quoted body whose 
451 T133 | 11-21 21:00 | open | T | SHELL | P | shared::tree's held double-quoted body hides a `$(...)` that holds a q
451 T134 | 11-21 21:00 | open | T | SHELL | P | shared::tree's walk reads the `<` and `>` of a `[[ ... ]]` test and of
451 T135 | 11-22 08:15 | open | T | TOOL | S | The round-3 tripwire never counts a task's plan rounds: T87's section 
451 T136 | 11-22 08:15 | open | T | TOOL | S | land-alone commits a landing's sections without the filed lines of the
451 T137 | 11-21 22:49 | open | T | SHELL | P | shared::tree judges a Python program run from stdin that writes throug
451 T138 | 11-21 22:59 | open | T | SHELL | P | (waits: T118 lands) t79's stdin probe stays refused by gate-write on t
451 T139 | 11-21 22:59 | open | T | FLAKE | S | test-no-poll-hooks.sh's 'two waiters on one quiet file and no run: sti
451 T140 | 11-21 22:49 | open | T | SHELL | P | (waits: T91 lands) shared::tree's walk holds a quoted word without its
451 T141 | 11-22 08:15 | done | PW | GM | S | A bundle of small tasks shares one builder, one replay, one plan secti
451 T142 | 11-22 01:29 | done | T | TOOL | S | The gate tool's build can fail to link on stale incremental state, and
451 T143 | 11-22 00:02 | open | T | TOOL | S | Other crates' tests read a session escape or write the live guard log,
451 T144 | 11-22 00:42 | open | T | SHELL | P | The tree guards read a default dropped for an assigned name: measured 
451 T145 | 11-22 00:42 | open | T | SHELL | P | (waits: T91 lands) T91 straight-line rule over-refuses a reassignment 
451 T146 | 11-22 01:29 | open | T | TOOL | S | The guard launcher's and make rust-test's incremental builds can link 
451 T147 | 11-22 08:15 | done | T | TOOL | S | A landing refuses on another feature's open plan-review passes, which 
451 T148 | 11-22 08:15 | open | T | TOOL | S | One builder's edit that does not compile stops every other builder's g
451 T149 | 11-22 08:15 | open | T | TOOL | S | A builder's staged change is swept into another task's commit (observe
451 T150 | 11-22 08:15 | open | T | TOOL | S | A landing refuses a file in its delta that another started task also e
451 T151 | 11-22 08:15 | done | T | TOOL | S | make ledger-owed traces no Workflow agent to the session that ran it, 
451 T152 | 11-22 08:15 | open | T | MEAS | S | A task's CLEAR plan verdict commits its files to the clone at once, so
451 T153 | 11-22 10:04 | done | PW | GM | S | Every phase writes its Phase line, so the time report has no gap (the 
451 T154 | 11-22 10:04 | done | T | MEAS | S | A TRIAL: the gate compiles each crate three times and runs its tests t
451 T155 | 11-22 10:04 | done | T | MEAS | S | A TRIAL: a landing recompiles what the clone already built (measured 2
451 T156 | 11-22 10:04 | done | T | TOOL | S | The Stop hook's free-slot count misses running work (observed 2026-11-
451 T157 | 11-22 10:32 | done | T | TOOL | S | A landing is refused on other open tasks' record-check passes (observe
451 T158 | 11-22 14:36 | done | PW | GM | S | The disk fills with build caches and nothing refuses before it does (m
451 T159 | 11-22 20:15 | open | T | TOOL | S | A fresh tree's gate is red on rust/mode_a (found 2026-11-22 by 451 T15
451 T160 | 11-22 20:15 | done | T | FLAKE | S | pool's maps::tests::the_launcher_runs_the_gate_script fails 'Text file
451 T161 | 11-22 20:15 | done | T | TOOL | S | An edit is booked to the clone's mark, not to the builder that made it
451 T162 | 11-22 20:35 | withdrawn | T | DUP | P | Withdrawn: folded into T160 (fixed in its bundle - reviews' prereq/tes
451 T163 | 11-22 20:35 | open | T | NEWTOOL | P | the 449 log's edit lines written before 451 T161 by a builder whose de
451 T164 | 11-22 20:35 | done | T | TOOL | S | A map review's paired gate is judged on a snapshot of committed work, 
451 T165 | 11-22 22:15 | withdrawn | T | DUP | P | Withdrawn: done by T175 (d82ee10048) (measured 2026-11-23, plan.md's T
451 T166 | 11-22 22:25 | done | T | NEWTOOL | S | make verify T= (451 T164's review tree) prints 'OCCASIONS NOT DECLARED
451 T167 | 11-22 22:53 | done | T | TOOL | S | A page session's edits and check passes are booked to the clone's mark
451 T168 | 11-22 23:24 | done | T | NEWTOOL | P | Page-session lines the pre-T167 hook booked to the clone's mark (449 T
451 T169 | 11-23 00:05 | done | T | MEAS | S | The hook command echoed on every hook message is about 190 characters 
451 T170 | 11-23 00:05 | done | PW | GM | S | Every guard message is held to a word budget, mechanically (the GM 202
451 T171 | 11-23 00:05 | done | T | MEAS | S | The same Stop message fires again and again where nothing changed (mea
451 T172 | 11-23 01:01 | done | T | FLAKE | S | tests/hooks/test-l7r-guard.sh's case 'locked: no wait on another call'
451 T173 | 11-23 02:01 | open | T | FLAKE | S | tests/hooks/test-finished-run-hooks.sh section 6's five refusal cases 
451 T174 | 11-23 05:11 | done | T | NEWTOOL | S | Every guard's messages reach the budget check: the suites of repo-safe
451 T175 | 11-23 05:11 | done | T | TOOL | S | engine-freeze-hooks refuses every engine edit in any tree the session 
451 T176 | 11-23 05:11 | done | T | TOOL | S | a building-review's verdict is held at an engine key that covers every
451 T177 | 11-23 05:11 | done | T | NEWTOOL | S | Review the 255 guard wordings 451 T170 baselined unreviewed (dev/guard
451 T178 | 11-23 05:11 | open | T | TOOL | S | tests/hooks/test-review-tree.sh runs in no gate (found by T176, 2026-1
451 T179 | 11-23 05:11 | done | T | TOOL | S | the round arbiter's ask accepted a malformed trigger (plan:specs/449-r
451 T180 | 11-23 05:11 | done | T | TOOL | S | make land's land-alone step committed another started task's plan sect
451 T181 | 11-23 07:20 | open | T | TOOL | S | reviews prereq gate_state (rust/gate/crates/reviews/src/reviews/prereq
451 T182 | 11-23 08:10 | done | T | NEWTOOL | S | a round-arbiter tooling fix built in Rust inside the very task being l
451 T183 | 11-23 12:42 | done | PW | GM | S | Stop hooks never block to keep the session busy (the GM 2026-11-23, re
451 T184 | 11-23 14:22 | done | PW | GM | S | A size edit never changes a claim (the GM 2026-11-23, request.md 'the 
451 T185 | 11-23 14:22 | done | PW | GM | S | A split is a move (the GM 2026-11-23, request.md 'the convergence talk
451 T186 | 11-23 14:22 | done | PW | GM | S | Only a claim-changing edit re-owes a pop-up's or claim's check (the GM
451 T187 | 11-23 14:22 | done | PW | GM | S | Labels are data (the GM 2026-11-23, request.md 'the convergence talk')
451 T188 | 11-23 14:22 | done | PW | GM | S | Only factual findings cascade (the GM 2026-11-23, request.md 'the conv
451 T189 | 11-23 14:22 | done | PW | GM | S | A later review round is scoped to the change (the GM 2026-11-23, reque
451 T190 | 11-23 14:22 | done | PW | GM | S | Settled choices stay settled (the GM 2026-11-23, request.md 'the conve
451 T191 | 11-23 15:27 | done | T | NEWTOOL | S | The claims triage gets T186's filter (the GM 2026-11-23, the convergen
451 T192 | 11-23 15:42 | done | T | NEWTOOL | S | Labels are data, the rest of the record (filed by T187, measured 2026-
451 T193 | 11-23 17:03 | done | PW | GM | S | A builder waiting on a background watch that never fires is seen and w
451 T194 | 11-23 17:03 | done | T | NEWTOOL | S | T185's and T186's split defects, found by T184's split, the cascade ru
451 T195 | 11-23 17:09 | done | PW | GM | S | Triage and EDIT replies fail closed (the GM 2026-11-23: 'check whether
451 T196 | 11-23 17:09 | done | PW | GM | S | Claims and scoped rounds follow T185's pointers (the GM 2026-11-23: 'c
451 T197 | 11-23 17:09 | done | PW | GM | S | Review answers carry the build they were judged by (the GM 2026-11-23:
451 T198 | 11-23 17:09 | done | PW | GM | S | Derived files are checked before make done (the GM 2026-11-23: 'check 
451 T199 | 11-23 17:09 | done | PW | GM | S | T188 reaches building-review (the GM 2026-11-23: 'check whether there 
451 T200 | 11-23 17:09 | done | PW | GM | S | Low-cost gaps from the audit (the GM 2026-11-23: 'check whether there 
451 T201 | 11-23 17:39 | done | T | NEWTOOL | S | The idle check names a builder whose live work outlasts its wait (451 
451 T202 | 11-23 17:47 | done | T | TOOL | S | After a landing the clone takes main's tick commit back (observed 2026
451 T203 | 11-23 18:35 | withdrawn | T | DUP | P | Withdrawn: built in T199 (T198's bundle's MODE 4 round 2, 2026-11-23, 
451 T204 | 11-23 18:35 | done | T | NEWTOOL | S | Naming an item on a classed claim owes no impl-drift (observed 2026-11
451 T206 | 11-23 18:35 | open | T | TOOL | S | The coverage build's link can fail on stale l7r_shared incremental uni
451 T207 | 11-23 19:39 | done | T | FLAKE | S | rust/guard's make_only_hooks::tests::an_escape_is_recorded_with_its_re

### 451, Tuesday 2026-11-24 (the comparison group) (10 rows)

451 T208 | 11-24 00:59 | open | T | TOOL | S | The page-session runner reads a weekly usage limit as a 15-minute rese
451 T209 | 11-24 00:59 | done | T | NEWTOOL | S | modal-triage clears a pure addition that contradicts a pop-up's own st
451 T210 | 11-24 00:59 | done | T | NEWTOOL | S | 147 claims forced to full impl-drift after make building-programs rege
451 T211 | 11-24 00:59 | done | T | NEWTOOL | S | 22 claims forced because gather_code (rust/gate/crates/claims/src/clai
451 T212 | 11-24 00:59 | done | T | NEWTOOL | S | 8 false sends from the three ABSENCE phrases ('the one case', 'only on
451 T213 | 11-24 00:59 | done | T | NEWTOOL | S | relabeled_only (rust/gate/crates/claims/src/claims/index.rs, line 447)
451 T214 | 11-24 00:59 | done | T | NEWTOOL | S | make review-fixed refuses a sheet with no earlier verdict to carry (ru
451 T215 | 11-24 08:32 | done | T | NEWTOOL | S | a procedure section's kept words live in the repository beside dev/cla
451 T216 | 11-24 08:45 | done | PW | GM | S | an ad-hoc agent that judges or builds runs on the session's model (the
451 T217 | 11-24 09:15 | open | T | NEWTOOL | S | agent-model-hooks accepts the SESSION_MODEL line on a built-in type th
