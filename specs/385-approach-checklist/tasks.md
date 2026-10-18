# Tasks - feature 385, the approach checklist

One task at a time (FR-006): each is ticked only once its retro row is in `retro.md` and any change it names is made. T01 changes
what the hamlet maps draw (their lanes); its decisions are the GM's ruling and 0081's research read, so it is `research: rendering`.

## Occasions

- placement-changed: well on inashiro - T05: the pocket well off its farmstead, a shared well of the rolled siting (374 wave 155)
- placement-changed: well on kuwabata - T05: as Inashiro
- placement-changed: well on sawada - T05: as Inashiro
- placement-changed: village lane - T01: a turn or meeting the ground forces is lawful, and a lane end running nearly along another way over open ground is merged onto it (plan D2, D4)

## Tasks

- [x] T01 The lane law describes how people walk (plan T01, D1-D7): the rule table; `forced_turn` asked by the angle rules; a refusal names its rules; side by side merged; measured on the cohort, seed 10 patched and the pool; the drawing pages; its retro row
      research: rendering
      verify: DONE. lane law: rule table (lane-law-table.md); forced turns and meetings lawful (ways/forced.py, test_forced.py red on the old law); refusals name their rules (D3); side by side merged at needles and shallow crossings, a household's foot re-aimed (D4); the knot rule reads the ground (D4b); cohort 50/54 as HEAD, seed 10 under the w155 patch passes; 0081 drawing page; every record, pop-up and claim check answered; glyph-check NEEDS-WORK accepted, F1-F3 carried to T03; retro row in retro.md
- [x] T02 The tooling (plan T02; FR-003 to FR-005, and amendment 1, FR-008 to FR-011): the Approach block required by `make tick`, the triggers' fresh answer, the per-task split; re-checks against what the last check read, one check where several are spent, no write while a gate runs, the check cost measured; its retro row [lands-open]
      research: rendering
      verify: DONE. all seven items landed on main (D8-D14), each with a test red without it; hooks-test and the tooling tests green; per-task and per-check tables printed by make feature-report F=385; part B after hour 5 CLEAR; retro row in retro.md
- [x] T03 FIRST the blind Approach (amendment 2, FR-012): a fresh agent writes T03's part A from the task, the checklist, the code and the record alone; then the four cohort seeds failing at HEAD (17, 21, 40, 45), as T01 leaves them, and the side-by-side shape T01 leaves (the glyph-check of 2026-10-17, F1-F3 on Inashiro: a stub and a lane run side by side, joined by a rung) - the merge decided as one general test, not a fourth detector; its retro row [lands-open]
      research: rendering
      verify: DONE. seeds 17, 21, 40, 45 pass; nothing newly fails against HEAD; pool clean (Kashikawa lane 9 straightened); D17's merge, seeds 49, 55 and 57's residue carried to T12 by the round arbiter; claims and record checks answered; gate green; retro row in retro.md
- [x] T04 T48: the web carries a re-deal of the seats (384's User Story 2, SC-004); its retro row [lands-open]
      research: rendering
      verify: DONE. see retro.md's T04 row; plan CLEAR (T04 round 2)
- [x] T05 T47: the wave 155 pocket-well patch re-landed, no waiver; its retro row [lands-open]
      research: rendering
      verify: DONE. pool clean on T05's tree; make done green (199 s); glyph-checks PASS on inashiro, kuwabata, sawada; make cohort-landing 54/54; claims gate clear but the front row and the standoff, carried into T06 by ask:t05-old-drifts-at-landing
- [x] T06 A ranking row (chosen at its start, a kind not yet tried); its retro row [lands-open]
      research: rendering
      verify: DONE. cohort-landing 54/54 (fresh block 6/48); gate green (221 s); a scattered hamlet single file round its paddy and dry plots where the line holds every farm (4 of 18 dispersed seeds), as before otherwise (decided on a copy, no farm taken back); claims settled over four impl-drift rounds; the gap filed (found-wave157), farmsteads within the paddy proposed to the GM
- [ ] T07 A ranking row; its retro row [lands-open]
      research: rendering
- [ ] T08 A ranking row; its retro row [lands-open]
      research: rendering
- [ ] T09 A ranking row; its retro row [lands-open]
      research: rendering
- [ ] T10 A ranking row; its retro row [lands-open]
      research: rendering
- [ ] T31 Amendment 7, FR-020: a ranking row (chosen at its start, a kind not yet tried where one is left); its retro row [lands-open]
      research: rendering
- [ ] T32 Amendment 7, FR-020: a ranking row (chosen at its start, a kind not yet tried where one is left); its retro row [lands-open]
      research: rendering
- [ ] T33 Amendment 7, FR-020: a ranking row (chosen at its start, a kind not yet tried where one is left); its retro row [lands-open]
      research: rendering
- [ ] T34 Amendment 7, FR-020: a ranking row (chosen at its start, a kind not yet tried where one is left); its retro row [lands-open]
      research: rendering
- [ ] T35 Amendment 7, FR-020: a ranking row (chosen at its start, a kind not yet tried where one is left); its retro row [lands-open]
      research: rendering
- [ ] T36 Amendment 7, FR-020: a ranking row (chosen at its start, a kind not yet tried where one is left); its retro row [lands-open]
      research: rendering
- [ ] T37 Amendment 7, FR-020: a ranking row (chosen at its start, a kind not yet tried where one is left); its retro row [lands-open]
      research: rendering
- [ ] T38 Amendment 7, FR-020: a ranking row (chosen at its start, a kind not yet tried where one is left); its retro row [lands-open]
      research: rendering
- [ ] T39 Amendment 7, FR-020: a ranking row (chosen at its start, a kind not yet tried where one is left); its retro row [lands-open]
      research: rendering
- [ ] T40 Amendment 7, FR-020: a ranking row (chosen at its start, a kind not yet tried where one is left); its retro row [lands-open]
      research: rendering
- [ ] T12 Carried from T03 by the round arbiter (hour:385-approach-checklist@6, ask:t03-d17-route, ask:t03-seed57-residue): D17's side-by-side merge (saved; F1-F3 merged and seed 49 fixed, six seeds regressed - 7, 24, 37, 51, 52, 57 - because the later settle passes are blind to the junctions it makes), seed 49, seed 55 (lane_knots 1, as at HEAD), seed 57 (lanes 1/13, ends 21.6 ft apart, settle_knots' gather refused by needle_loops; 2 knots against HEAD's 1) and Inashiro F1-F3's glyph-check NEEDS-WORK; done when seed 57 PASSES. Its Approach first asks whether the merge needs a fixed reach at all (REACH 20 then 25 ft is ours), whether the refusals behind seed 49 (a field and farmhouses unreached) rest on research, and whether needle_loops' and needle_joins' rules are research or ours; only then the design that makes the later passes aware of the merge's junctions. Also carried at T03's landing (ask:t03-claims-at-landing): settle.py::theirs DRIFTED - take a lane's own household from fabric.owned_gardens instead of the 80 ft radius, measured on the cohort; Lawful.fault's doubled tail at 15 degrees against 0081's 20 - which number the research fixes, first; clearance.py::_clear_link re-checked once its bundle carries link_survives; its retro row [lands-open]
      research: rendering
- [x] T13 Amendment 3 (FR-013, the GM's option 3): the claims gate carries a finding a page edit surfaced on unchanged code instead of refusing it - `make claims-carry F=<n>` files it as an open task the open-task refusal honors; T03's three findings filed by it; its retro row
      research: rendering
      verify: DONE. claims gate carries a page edit's finding on unchanged code (D26-D28); make claims-carry files it into the active feature only; tests red without each rule (test_claims_index, test_lands_open, test-claims-gate.sh); SC-007 replayed on T03's landing: theirs and _clear_link carried, the doubled tail still introduced (T03 changed that code); retro row in retro.md
- [x] T14 Amendment 4 (FR-014 to FR-016): the report tells the session's calls from its subagents' and prints each task's phases and its decision-log skeleton; the checklist's one goal a task; T03 replayed; its retro row
      research: rendering
      verify: DONE. report tells session from subagent calls (transcripts exact, window estimate per run), foreground runs as waiting, idle apart, per-task phases and decision-log skeleton; checklist A9 one goal, C8 to the skeleton; T03 replayed (202 of 549 calls subagents'); tests in test_event_log.py red without each; arbiter fix on ask:t14-plan-round4 done; retro row
- [x] T15 A cohort rolled over an uncommitted engine diff says so (found by T04, plan D36): `cohort_known --stamp`, its readers skip it [lands-open]
      research: rendering
      verify: DONE. see retro.md's T15 row; plan CLEAR (T04 round 2)
- [x] T16 A plan review's third round on one task waits for the round arbiter (the arbiter's fix on hour:385-approach-checklist@9, plan D37) [lands-open]
      research: rendering
      verify: DONE. see retro.md's T16 row; plan CLEAR (T04 round 2)
- [x] T17 Amendment 5, FR-017: the push checks the make-targets page is current [lands-open]
      research: rendering
      verify: DONE. see retro.md's amendment 5 rows; plan accepted by the round arbiter on round:spec-fidelity|plan:385-approach-checklist#T17@3
- [x] T18 Amendment 5, FR-018: `make arbiter-fix-done LAND=` lands the fix and settles it in one command [lands-open]
      research: rendering
      verify: DONE. see retro.md's amendment 5 rows; plan accepted by the round arbiter on round:spec-fidelity|plan:385-approach-checklist#T17@3
- [x] T19 Amendment 5, FR-019: the ledger refusal names `make ledger-owed WRITE=`, which writes each row from the reply [lands-open]
      research: rendering
      verify: DONE. see retro.md's amendment 5 rows; plan accepted by the round arbiter on round:spec-fidelity|plan:385-approach-checklist#T17@3
- [x] T20 The hour decided once per message, and the step-back lists the hour guard's refusals (the arbiter's fix on hour:385-approach-checklist@10, plan D42) [lands-open]
      research: rendering
      verify: DONE. landed on main; tests/tooling/test_checkpoint.py green (the hour decided once per message; the step-back lists refused events)
- [x] T21 A batch reply's own EDITs settle its units; `make record-owed` names `make apply-edits FROM=<reply>` (the arbiter's fix on ask:t05-lane-popup-round3, plan D43) [lands-open]
      research: rendering
      verify: DONE. landed on main; tests/tooling/test_apply_edits.py 18 green; the arbiter's fix on ask:t05-lane-popup-round3 settled
- [x] T22 A refused dispatch is sent again or recorded dropped before a turn ends, and the decide-first refusal names its check (the arbiter's fix on hour:385-approach-checklist@11, plan D44) [lands-open]
      research: rendering
      verify: DONE. landed on main; tests/hooks/test-pair-hooks.sh 97 green, red without the stop layer; the arbiter's fix on hour@11 settled
- [x] T23 The claims gate takes a MISLABELED answered by its prescribed relabel as answered, as `claims-owed` already does (found by T05, plan D45) [lands-open]
      research: rendering
      verify: DONE. landed on main; tests/tooling/test_claims_scoping.py green, red without the gate's skip; T05's three relabels no longer refused
- [x] T24 `make land-tooling` merges main in itself when the clone is behind, so a landing never fails on a stale base (found three times on 2026-10-18, plan D46) [lands-open]
      research: rendering
      verify: DONE. landed on main; tests/hooks/test-land-tooling.sh 33 green (3c a stale base lands, 3 a conflict refuses with the merge aborted)
- [x] T25 A claims bundle inlines the callees a unit reads from other modules and the constants they read, one level on (the arbiter's fix on ask:t05-old-drifts-at-landing, plan D47) [lands-open]
      research: rendering
      verify: DONE. landed on main; tests/tooling/test_claims_index.py green; the standoff's first bundle carries every name its rounds asked for (154 KB); the arbiter's fix on ask:t05-old-drifts-at-landing settled
- [x] T26 `make verify` renders each owed map whose render is missing or older than its generator or manifest before it writes the review prompts (the arbiter's fix on hour:385-approach-checklist@12, plan D48) [lands-open]
      research: rendering
      verify: DONE. landed on main; tests/tooling/test_review_owed.py 66 green; the arbiter's fix on hour@12 settled
- [x] T27 The heading an owed Approach or part B asks for passes the tick: stamps compared to the minute the heading carries (found ticking T05 and T22, plan D49) [lands-open]
      research: rendering
      verify: DONE. landed on main; tests/tooling/test_approach_gate.py green; T05 and T22 tick with the headings owe printed
- [x] T28 An arbiter's ask bundle carries the research claims on every number its question or evidence names (the arbiter's fix on ask:t06-scattered-single-file, plan D50) [lands-open]
      research: rendering
      verify: DONE. landed on main; tests/tooling/test_arbiter_fixes_352.py green, red without claims_section; the ruled ask's own words give 1.3 acres its claim and 273 ft no claim; the arbiter's fix on ask:t06-scattered-single-file settled
- [x] T29 Each plan review's bundle has its own path, keyed by its tasks and its blocks' digest (the arbiter's fix on hour:385-approach-checklist@13, plan D53) [lands-open]
      research: rendering
      verify: DONE. landed on main; tests/tooling/test_plan_blocks.py green, red without the keyed path; two plan-delta runs write two bundles; the arbiter's fix on hour@13 settled
- [x] T30 Nothing is merged into a clone while a make runs in it, on the tool-call path too (the arbiter's fix on red-gate@2026-10-18T12:36:36Z, plan D54) [lands-open]
      research: rendering
      verify: DONE. landed on main; the tooling suite runs no land-tooling (1,924 tests, HEAD unchanged); the gate lock holds the merge on both clone-sync paths and in land-tooling, each test red without it
- [ ] T41 A check dispatch a later hook refused is counted as no round (the arbiter's fix on round:source-reader|q:0081@3, plan D56) [lands-open]
      research: rendering
- [ ] T11 The close: the checklist to `docs/`, the refusals extended to every feature (FR-001), the final report (SC-001, SC-002); and D30's wording, filed by the round arbiter's ruling on ask:t14-plan-round4 (T14's plan round 4, rows 1-3 - the code already does each, `test_a_transcript_named_call_is_its_run_s_anywhere_and_a_mixed_overlap_is_the_missing_run_s_estimate`): the outside-every-window clause carries its own condition (no `by`, no transcript names it), the overlap clause says "still an estimate", and a call inside both a found and a missing run's window is the missing run's estimate [lands-open]
      research: rendering
- [ ] GM review (make gm-reviewed F=385) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
