# Cascade P12 (449 T432's and T428's pages, T425): 0057 research + drawing, 0006 drawing, 0011 drawing

Clone /diagram/.clones/diagram-backlog at b75ade5b7e (P12's page commit, unpushed). Coordinator: c6fd72d1. Replies saved under
/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/p12/. Nothing staged, committed or pushed; no rust/ file edited.

**STATUS: `make quick` is RED** on question-size: P12's own 0006 drawing SIZE EDIT (19,539 -> 21,792 bytes against its 20,000 limit,
the qualifiers `not` and `without` dropped). Not caused by this cascade; see (c).

## Counts per stage

| stage | in | tool cleared | to an agent | outcome |
|---|---|---|---|---|
| (1) record-format 0057 third round | 1 | - | round-arbiter | ACCEPT, not run |
| claims-triage | 55 | 55 (FR-005 a) | 0 | - |
| claims-owed -> impl-drift | 11 | - | 1 bundle | IN-STEP 7, DRIFTED 3, CANNOT-TELL 1; 3 HELD by 451 T218 |
| 451 T218 re-bundle (`PAGES=` the 7 named) | 3 | - | 1 bundle | DRIFTED 2, CANNOT-TELL 1 - all recorded |
| directed impl-drift (`REASON=` + `PAGES=` 0057 x2, 0006 drawing) | 7 | - | 1 bundle | IN-STEP 2, DRIFTED 4, MISLABELED 1; all 7 recorded (3 had their § pointers on uncited pages dropped) |
| modal-triage | 30 | 22 (incl. every 0057 research-page gaps/references unit) | 8 | 7 TOUCHES, 1 untouched (`hamlet/marsh`) |
| modal-depiction | 7 owed + 1 directed (`hamlet/marsh`) | - | 8 | 6 clean; 2 EDITs (millet TRUTH, marsh COVERAGE), applied 2, refused 0 |

Paid dispatches: 1 arbiter, 3 impl-drift, 1 modal-triage, 8 modal-depiction = 13.

### Arbiter
- This clone's counter named the unit `round:record-format|q:0057@2` (the check session counted it the third; the arbiter says the
  bundle lists all four dispatches, the counter two - "not a mismatch"). Ruling ACCEPT: "the page now reads 'to prevent cold-water
  damage', from quote-check's EDIT, and that is the maff-shosuiro-sheet note's own quoted words ... another round would only re-read
  common words it has already passed." Noted, not filed: Latin binomials in cao-2019; "slope wetlands" undefined on the drawing page;
  the glossary's `kohai` maybe matching `kohai-shicchi`/`kohai-teichi` (check the tooltip matcher).
- It was refused until it also ruled `round:quote-check|q:0031@4` (owed from an earlier session, in the batch): ACCEPT ("each round's
  one finding was settled by the next"). Both recorded in specs/449-rust-codebase/arbiter.jsonl.

### Claims verdicts (not IN-STEP), quoted
- `field/dry.rs::PINCH_SHARE#the pinch` DRIFTED (T218 round): "the cited page is not silent: §27 already records this figure as a
  GUESS ... `PINCH_SHARE = 0.5` matches it; fix: claim; effect: none".
- `field/dry.rs::pinched#the pinch` DRIFTED (T218): "§27 records the rule as a GUESS ... code and page agree; restate the claim to
  cite §27; fix: claim; effect: none".
- `field/dry.rs::hem#the last band from the canal's start` CANNOT-TELL (T218): "§36 records the order as a GUESS ('laid from the toe
  end of the canal, up along it') ... I would need to know which end of the canal `line[0]` is". Resolved here, not re-dispatched:
  build.rs:330 hands the hem "the far flank's drawn course from the foot up", so `line[0]` is the toe end -> fix: claim.
- `driver/toe.rs::toe_band#toe band width` CANNOT-TELL: "the page now takes the band's width from 'the fan's plots and the dry fields
  round them' ... `toe_band` measures only the `rings` it is handed ... If they hold only the paddy fans, the hem's strips on the far
  flank can reach past the marsh's end".
- `seat/margins.rs::ranked#not on the wet toe` DRIFTED (directed; recorded, was IN-STEP 2026-11-24): "the claim says the marsh lies 'below the
  fields', and the toe band also climbs the side of the fields that narrows downhill ... cite 0057 drawing §200, §202 alongside 0058".
- `seat.rs::open_at_an_end#a seat astride the brook leaves by its open bank` DRIFTED (directed; recorded; ALREADY DRIFTED since 2026-11-24, wrong page): "this GUESS names 0035 as
  the page that records it, but 0035 records no such guess. The guess is recorded by 0031 §21 ... and 0081 §116 ... `BAND_EXITS`
  ±0.6 matches §116 ... fix: claim".
- `seat/margins.rs::SQUARE_EPS#the square end in` MISLABELED (directed; recorded, was IN-STEP): "a bare GUESS, but ... 0031 §20 admits a fall
  'across' the wind, and §21 seats such a hamlet at 'the windward corner at the head of its fields' ... label should be `GUESS
  question 0031 (abbreviated in the session record)`".
- `field/dry.rs::hem#a column's climb ends` DRIFTED (directed; recorded): "0006's drawing page now says it: 'Where a strip's lower or
  upper edge would run under half a plot's length, that strip is not drawn' ... fix: claim (cite 0006 drawing §158 ...; 0011 §166 for
  the climb); effect: none".
- `driver/check.rs::check#no dry plot on the water` DRIFTED, **fix: code** (directed; recorded): "`dry_on_water` tests only a plot's
  corners ... A ditch, the brook or the drain's run that crosses a plot, or ends inside it, without reaching a corner passes the
  check. 0006 §161 drops a plot that 'would have the end of one inside it'... effect: tool". Not fixed (no rust/ edits).
- `toe_band#toe band edge`: **IN-STEP**, "this is the page's smoothed edge that climbs a narrowing side [§102, §104]". This OVERWROTE the index's open DRIFTED fix: claim of 2026-11-24 ("on a side where the fields narrow downhill that same edge carries the wet ground up the whole side, which 0057 now records as a deliberate [deviation]"). The claim's words did not change, so that restatement is still owed in substance and goes on the T432 list.
- `check#no dry plot on the water` was ALREADY DRIFTED fix: claim (2026-11-24: §27 speaks only of the plot's own canal; the brook and drain covered elsewhere). This round moved it to fix: code (a corner-only test). No task in specs/ names it.

### Pop-up EDITs, quoted (applied by `make apply-edits`)
- `hamlet/millet` TRUTH: "each squared to the canal behind a bare bank." -> "each squared to the canal behind a bare bank, so that
  where the canal bends the plots beside it taper."
- `hamlet/marsh` COVERAGE (directed): after "straight run does not read as an edge." adds "Where the fields narrow inward downhill,
  the marsh climbs that side of them its whole length, its edge set just below the lowest field at each point across the slope -
  simpler to draw than cutting it off at the fields' lower corners, and unlike the real ground, where a fan's springs came out along its
  foot and its sides were among the land cleared early; a valley side that did run wet, against a hill foot, was still farmed as cold,
  wet paddy, not left to reed."
- Clean: `cluster_position--on_rise`, `--valley_mouth` ("off any drawn marsh" covers the keep-off), `farm-holding` (the Shinbori block
  is about the hem, not the holding), `barley`, `buckwheat`, `soy` (the taper is a GUESS; "rectangular" is the page's own opening).

## PREDICTED vs ACTUAL

| predicted | actual |
|---|---|
| `hamlet/marsh` may come back GAPS | NOT TESTED: GAPS is modal-research's verdict, and its unit was tool-cleared at modal-triage (the depiction unit was triaged untouched). A directed modal-depiction found COVERAGE 1 and an EDIT adding the flank. Its new sentence carries research statements (springs at the foot, sides cleared early, a hill-foot side farmed as cold paddy) that no modal-research has read. A directed modal-research on marsh would test both; it was not run. |
| `cluster_position--valley_mouth`, `--on_rise` re-check | Triage TOUCHED both (B: valley-floor block); both clean. |
| `toe_band#toe band edge`, `PAD#toe band edge` IN-STEP; T432 owes them again | Both owed, both IN-STEP. |
| (coordinator's brief) `toe_band#toe band edge` should read as a DEVIATION with no ground | NOT so: impl-drift reads the DEVIATION block `toe-on-tapering-flank` as still recorded (label kept) and the code matches it. impl-drift does not judge whether a deviation's grounds hold; the applicability ruling (DOES-NOT-APPLY) lives only in the handoff, so the claim stays IN-STEP until T432. |
| `toe_band#toe band width`, `PAD#toe band width`, `flaring flanks` should clear | PAD width IN-STEP; flaring flanks IN-STEP (directed); `toe_band#toe band width` came back CANNOT-TELL (the "dry fields round them" width). Not predicted. |
| fan_middle--wild/cleared should clear | Tool-cleared. |
| `Canal.frame` / `hem#square to the canal` DRIFTED fix: claim likely | Both IN-STEP ("tapering at a bend" already in hem's wording). |
| `check#no dry plot on the water` re-check | Not owed (its rested block stood); the directed check found a CODE defect (corners only), not a wording issue. |
| barley/buckwheat/millet ("small rectangular plots") IN-STEP, GAPS possible at the bend | Triage touched all four plus soy; only millet got an EDIT; barley/buckwheat/soy, with the same sentence, judged clean. |
| `farm-holding` if it states the frame | Touched; clean. |
| DIRECTED: `PINCH_SHARE`, `pinched` (say "silent") | Both owed anyway and DRIFTED fix: claim, after a 451 T218 hold. |
| DIRECTED: `hem#a column's climb ends` | DRIFTED fix: claim. |
| `hem#the last band from the canal's start` DRIFTED (silent since P4) | DRIFTED, T218 hold, then CANNOT-TELL; resolved fix: claim (build.rs:330). |
| `build#the climb's order` IN-STEP | IN-STEP. |
| DIRECTED: `ranked`, `open_at_an_end`, `stage_seat`, `SQUARE_EPS` | `stage_seat` IN-STEP; `ranked` DRIFTED and `SQUARE_EPS` MISLABELED (both new, both were IN-STEP); `open_at_an_end` DRIFTED (already open). All recorded; only the § pointers on uncited pages were dropped. |
| All 10 of 0011's pop-ups clear | Tool-cleared. |

## Judgment

(a) **Over-cascade: small.** 55 claims and 22 pop-ups were cleared without an agent. The modal-triage TOUCHES on the four crop pop-ups and
farm-holding cost five depiction passes; four of them found nothing. The T218 hold cost one extra impl-drift on three claims. Its extra
pages (0018, 0053, 0242, 0246) were irrelevant again (the known misfire shape), but the re-judge did read the cited page more closely. The
record-format third round went to the arbiter and was accepted without a run.

(b) **Under-cascade: three gaps, the same shapes as before.**
- `hamlet/marsh`: its Entry units were tool-cleared and its Drawing unit was triaged untouched. The flank omission P11 reported was
  caught only by a directed check (the tenth time a page's DEVIATION or GUESS has not reached its pop-up, 451 T226).
- FR-005 a cleared `ranked` and `SQUARE_EPS` (they cite 0058 / no page). The directed check found them DRIFTED / MISLABELED, the stale-silent and
  other-page pattern again. Their verdicts are recorded; claims-checked dropped only the § pointers on pages they do not cite.
- `toe_band#toe band edge`: this round's IN-STEP overwrote an open DRIFTED fix: claim with the claim's words unchanged. A fresh
  judge reading the recorded DEVIATION sees no drift, so the index lost a finding. Carried below.
- Sibling inconsistency: one sentence ("each squared to the canal behind a bare bank") in four crop pop-ups got one EDIT (millet) and
  three passes. Millet now mentions the taper and barley, buckwheat and soy do not. Reported, not added: no check's EDIT.
- The new GUESS `dry-plot-taper-at-bend` reaches no Guesses tab (millet, barley and buckwheat noted it for modal-form/modal-research;
  451 T226). Reported, not added.

(c) **Rules that fired.**
- FR-005 a: 55 claims cleared. Modal triage tool clearance: 22. The agent: 7 TOUCHES, 1 untouched.
- 451 T218: held 3 lines (PINCH_SHARE, pinched, hem#the last band), one re-bundle with `PAGES=`, all 3 recorded.
- claims-checked's "rests on a page it does not cite": dropped the § pointers of 3 directed verdicts (the verdicts were recorded).
- claims-checked format refusal: 2 directed lines written "Fix:" capitalized, re-recorded once corrected.
- Round arbiter: 1 ACCEPT on the EDIT-only third-round shape (the fifth today), plus 1 forced ACCEPT (0031 quote-check @4) the batch rule
  pulled in.
- Escapes used: `WAVE_OK` x3 (the agent-prefix wave guard refused the 4th to 6th hand-launched `modal-depiction`; this subagent has no
  Workflow tool); `SIZE_EDIT_OK` x1 (a measurement run of `make quick` only, not a landing; quick re-run plain afterwards and left RED).
- Decide-first guard: not refused (449 T425 in each description, `DECIDE_OK` in each prompt).
- `make quick`: RED on question-size. 0006's drawing page is a SIZE EDIT (19,539 -> 21,792 bytes against its 20,000 limit) that drops
  the qualifiers `not` and `without` from the Edo-period block. That comes from P12's own commit, not this cascade. The rewrite is a correction:
  the new block still calls the frame "a reconstruction" and "this project's own". So P12's landing owes `SIZE_EDIT_OK="<the Edo block
  restated as a correction>"` or a split. With that escape, quick is clean. "A correction, not a fit" is my reading, for the lander to
  decide. The escaped run does not show that 21,792 bytes against a 20,000 limit is acceptable (`make done` may refuse the size).

## The rust claims to restate (none restated here)

**Settled by 449 T432's code change (the wet flank):**
- `driver/toe.rs::toe_band#toe band edge`: index IN-STEP now, but the 2026-11-24 DRIFTED fix: claim it overwrote still stands in substance.
  The claim should say the edge carries the wet ground up a narrowing side as the DEVIATION `toe-on-tapering-flank`, or whatever T432
  draws instead. T432 rewrites it.
- `driver/toe.rs::toe_band#toe band width`: CANNOT-TELL, answered here. driver.rs:422 calls `toe_band(&[g.ring], ...)` with
  `ring: &f.fan.ring` (driver.rs:398), the paddy fan alone; the hem is laid after the seat. So the band's width does not take in the dry
  fields, as 0057 drawing ("the fan's plots and the dry fields round them") says. That is a code question (the hem's far-flank strips may
  reach past the marsh's end) for T432's rewrite of `toe_band`; otherwise the claim must say "the paddy fan's".
- `seat/margins.rs::ranked#not on the wet toe`: "below the fields" vs a toe up the narrowing side. If T432 drops the flank, the old
  wording is right again with 0057 drawing cited; if it keeps it, cite 0057 drawing (the keep-off block) alongside 0058.
- The 0057 halves of `seat.rs::open_at_an_end` ("its windward flank on the wet toe", the 4-of-35,000 measure) and `SQUARE_EPS` (seed
  901280's wet windward flank): they re-measure after T432.
- `hamlet/marsh`'s new Depiction sentence describes the flank as drawn. T432 must re-owe it if the flank goes.

**Wording only (code already matches):**
- `field/dry.rs::PINCH_SHARE#the pinch`: "GUESS research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html:
  `dry-plot-taper-at-bend` - under half a plot's length a strip is not drawn" (no longer "silent").
- `field/dry.rs::pinched#the pinch`: the same citation of `dry-plot-taper-at-bend`.
- `field/dry.rs::hem#a column's climb ends`: cite 0006 drawing `dry-plot-taper-at-bend` for the pinch at half a plot's length, with
  0011 drawing for the climb.
- `field/dry.rs::hem#the last band from the canal's start`: "GUESS question 0011 (abbreviated in the session record) (the clearing starts from
  the plots nearest the toe): from the toe end of the canal, up along it, until the need is met".
- `seat.rs::open_at_an_end`: the GUESS cites 0035 wrongly. Cite 0031 drawing (its track leaves by the open bank) and 0081 drawing (six-tenths
  to each end, `BAND_EXITS`).
- `seat/margins.rs::SQUARE_EPS#the square end in`: relabel from a bare GUESS to `GUESS research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html`
  (a fall across the wind admitted, the windward corner at the head).

**Code defect, neither T432 nor wording:** `driver/check.rs::check#no dry plot on the water` (an existing DRIFTED row, its fix moved from
  claim to code this round; no task in specs/ names it). `dry_on_water` tests corners only, so a
watercourse crossing a plot, or ending inside it, passes (0006 drawing: a plot "would have the end of one inside it" is dropped). It
needs a task: test each plot edge against each water segment, and a water end inside the plot.

## Files changed (uncommitted, in the clone)
- l7r/diagram/interactive/assets/modals/hamlet/millet.md, l7r/diagram/interactive/assets/modals/hamlet/marsh.md (the two EDITs)
- dev/claims-index.json, dev/claims-pages.json (claims-checked)
- specs/449-rust-codebase/arbiter.jsonl (the two rulings)
- dev/review-ledger.md (ledger-owed WRITE: 11 rows; a re-run lists none owed)
- plus the tools' own record/state files under .git/
