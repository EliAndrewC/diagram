# Tasks - 230 the stream's intake, and the two ditch classes

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md).

- [x] T01 spec-fidelity review FAITHFUL; research R1
      research: rendering
      verify: DONE. spec-fidelity rounds 1-4 CHANGES REQUIRED (Kuwabata's off-frame drain; SC-2's sweep; FR-004 (d); the pond feeder's record-less stroke; FR-004 recut to the finished research and FR-002's three sinks), round 5 FAITHFUL 2026-09-12; research R1 from the code and Inashiro's manifest
- [x] T02 FR-003 the research pass: where does a natural stream become an irrigation ditch, and what is a drain's outfall run; the record, the registry, the rule line, the pointers
      research: physical
      - [x] research pass - R2a (Japan-first) and R2b (China-first), the synthesis R2c
      - [x] source-reader confirmed - both readers reported per claim; their verbatim passages are R2a/R2b
      - [x] recorded and cited - research/water.html, the two sections named in R2c, with their footnotes on research/citations/water.html and 16 registry entries in SOURCES.html
      - [x] quote-check confirmed - 40 footnotes, 18 links, all READABLE and SUPPORTS; two DIFFERS fixed (an unmarked elision in the Wang Zhen original, and a compound the page reads as 用排再利用, re-read off the PDF's own text layer), and the section's five bare absence claims given absence notes in feature 195's form
      - [x] source-applicability confirmed - all 16 new keys judged; six write-ups' limits corrected (commit dafec40f)
      verify: DONE. two Opus readers (Japan-first, China-first), one attempt per host, R2a/R2b verbatim; the finding R2c; 16 registry entries with both write-ups; two new sections of research/water.html with footnotes 70-108 on the citations page; settlements/water.md rewritten (the brook is tapped and runs on; the drain's continuation is a drainage ditch in every sink); glossary +14 terms; pointers at hamletgen/water.py, hamletgen/sink.py and waterfields/comb.py
- [x] T03 FR-001/FR-002 the two classes decided from the role at every emit site, the off-frame drain run as the pond run's kind, the vocabulary table, the sibling texts, the hit boxes, the tests; Inashiro's page
      research: rendering
      verify: DONE. irrigation ditch / drainage ditch decided from the record's role at every emit site (ditch_style, channel_class, the record-less pond feeder fixed as supply); the drain's continuation drawn and recorded alike in every sink (drain_run); FR-007 table, siblings, HIT rows, SINCE_189 snapshot table; Inashiro's page hovers the collector and the supply net apart; tests/interactive 675 green
- [x] T04 FR-004 the head per R2 - the intake and the head race derived from the finding (or the labeled guess), with its unit tests; Inashiro
      research: physical
      - [x] research pass - the same T02 pass answers it: R2c, and the two sections of research/water.html it produced
      - [x] source-reader confirmed - the head works, their order and the stream continuing below them are R2a/R2b quotes
      - [x] recorded and cited - the intake, the two forms, the bank, the angle and the head race's length are all in the water record; the length is a labeled guess and the knob's even roll is labeled one too
      - [x] quote-check confirmed - the same pass as T02, over both sections
      - [x] source-applicability confirmed - the same 16 keys
      verify: DONE. the brook is tapped at an intake and runs on past the fan down a rolled flank (brook_skirt); the head race leaves the bank at the record's offtake angle over a rolled lead; the intake's form is a knob (weir x4, open pinned on Sawada) with the oblique stone-crib bar drawn on a weir hamlet; the drain joins the passing brook where one falls within reach, else the pond or the frame - all three sinks exercised by the pool. Five settlement-review passes drove the geometry (ledger rows): sharpest turn 49.3/104.5/48.6/51.9 deg, median 4.1-15.4, no brook vertex in cultivated ground on any map, one connected piece in the view on every map, the offtake angle exactly the record's 35 deg
- [ ] T05 FR-005 the pool, the cohort if the routing changed, `make verify` + settlement-review, the records (R3, the notes entries, the perf bookends), spec IMPLEMENTED, land
      research: rendering
      verify: the pool regenerated and all five maps seat every household with no roll failure; eight settlement-review passes (ledger rows); the cohort restored to 48/48 against the pre-feature baseline; the perf bookends taken alternately with a detached worktree and the band-3 explanation recorded. OPEN: the perf-audit subagent's confirmation, and the GM's sign-off on the band-3 increase, which is theirs to give.
- [ ] T06 FR-006 the seat rule and its shortfall re-roll - the research pass on whether a hamlet stood on ONE bank of its stream or on both with a crossing, the label that follows from it, and the declined alternative recorded
      research: physical
      - [x] research pass - specs/230 research R6: the record answers by SCALE (one bank of a river, through the middle of the settlement's own channel), so the rule is this project's own guess and is labeled one
      - [x] source-reader confirmed - one Opus reader, 14 sources, verdicts per sub-question including the CONTRADICTED trio on Harie and the NOT-FOUND on what crosses a settlement's channel
      - [x] recorded and cited - research/water.html, "Does a hamlet stand on one bank of its stream, or around it?", with ten registry entries and footnotes 120-131
      - [x] quote-check confirmed - 11 footnotes, all READABLE; two DIFFERS corrected (the journal's full-width comma, the Chinese page's double quotes), a gloss naming a party the page does not carry removed, the kundoku mislabeled as classical Chinese fixed, the emphasis this project had added inside quotations taken out, and three PARTIAL assertions brought back to what the quotes grant
      - [x] source-applicability confirmed - all ten keys APPLICABLE-WITH-LIMITS; three wrong 'What it is' write-ups (two bylines, a lawsuit's dates) and seven missing limits corrected, including a scale claim that rested on a modern household count (commit b2c345fc)
      verify: the rule is labeled a GUESS at all three places it lives (spec D9, cluster.py at the point of change, future-work as the knob candidate the crossing machinery blocks). The public record page is the part still owed.
- [ ] T07 settlement-review pass 10's findings, each fixed and verified on a regenerated pool (the reviews read the snapshot taken before the lane-ink, sawtooth-nudge and drain-hue fixes)
      research: rendering
      - [x] Inashiro E1: the connector undrawn - five passes deleted a lane record and left its ink slot; `drop_lanes` + a behavioral and a static test; all five maps draw every lane exactly once
      - [x] Inashiro E2: the brook's +/-29 degree sawtooth - `_off_the_axes` kicked alternate legs a flat 11 px; now tilts just past the detector (median turn ~12 -> ~5.7)
      - [x] Inashiro E3 / Kashikawa E5 / Sawada N2 / Mizuguchi N2: the two ditch inks indistinguishable - DRAIN_HUE #7C9EB0 -> #5E7A76; the z-order audit reads the constants
      - [x] the FRAME-BOX sawtooth (Kashikawa E3, Mizuguchi's 68.7 at v26, Sawada's 46 degree notch): margin 44 + the frame reserving the brook beside the field; two levers refused on measurement (commit a7ca530d)
      - [ ] the tap corner, remaining 51-53 degrees (Sawada E1, Mizuguchi E3): over 200 ft the fork opens to 81-86 degrees
      - [x] the guaranteed flooded plot is a wedge (Mizuguchi E1, Kashikawa E4, Sawada E2): a sixth tint clause (fill of the minimum rectangle >= 0.80; pool median 0.93) and the promotion ranked on-the-collector, then fill, then size; plots on the collector count as low. Every map's blue plot: 0.79-1.19x median, aspect 1.08-2.0, fill 0.85-1.00, 2.5-10.7 px from the drain
      - [x] paddy rings below 15 degrees on Kashikawa (E2) - none on any of the five regenerated maps by the gate's own `pointed_ring` at 15 degrees; the gate tests read only Inashiro and Kuwabata, so a cheap all-manifest check is still owed (below)
      - [ ] a gate test that reads every shipped pool manifest for sub-15 degree rings, not only the two the gate rolls
      - [ ] FOUND, pre-existing on main: 20-49 pairs of paddy rings overlap per brook map (up to 482 sq px) - decide defect or layering, then fix or record
      - [x] the weir drawn backwards on Kashikawa (E1): set a pixel below the mouth, slanting up from the intake bank (found from the race's bearing); intake-bank end 5.5-7.0 px below the mouth on both weir maps
      - [x] Mizuguchi E2: the drain doubles back to its pond in a 111.6 degree hairpin - `pond_run` leads a run to a pond more than 100 degrees off the collector's heading round a cubic; sharpest bend 37 degrees; a pond straight downslope keeps the ordinary run (a 60 degree cut bent Inashiro's too and broke its lane web)
      - [x] Kuwabata E1: the polder's laterals carry both feed and drain sluices and are classed irrigation ditch - not an open question: research/archetypes.html already records the canals as 'the conveyance-and-drainage network the ponds exchange water with'. A `pond canal` class on the dike-pond archetype (327 strokes on Kuwabata); a rice polder's laterals stay irrigation ditches, the ring drain a drainage ditch
      - [x] the Pond modal contradicts itself (Mizuguchi E5, Kuwabata E2): rewritten to name both parts a pond plays, the reservoir above (read) and the sink at the foot (the map's declared sink, disclosed as a caveat - `pond` leaves the no-caveat list on purpose)
      - [ ] notes: Kashikawa E6 (stale census, "the fork at the top is a brook and a ditch parting", the subject line), Mizuguchi E4 (no-sluice-glyph line, tameike/reservoir wording, census), Sawada E3 + N3 (census, the 75 ft)
      - [ ] Inashiro Q1 windbreak tail up the east edge; N1 flooded-plot lip; N3 an undrawn channels[0] record; N4 a 4.8 ft field chain; Kuwabata N1-N4 lane web (a doubled road, a sliver wedge, a tight loop); Kuwabata E3 supply tapers reversed (also on main); Kashikawa N2 dangling bund stubs
      - [ ] open research questions, recorded rather than guessed: the confluence reading as an offtake (Kashikawa Q1); a path to a house's back door (Sawada Q1, Mizuguchi Q2); a drainage pond with no outflow beside a brook (Mizuguchi Q1)

