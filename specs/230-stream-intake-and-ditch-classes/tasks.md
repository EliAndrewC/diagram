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
      verify:
- [ ] T06 FR-006 the seat rule and its shortfall re-roll - the research pass on whether a hamlet stood on ONE bank of its stream or on both with a crossing, the label that follows from it, and the declined alternative recorded
      research: physical
      - [x] research pass - specs/230 research R6: the record answers by SCALE (one bank of a river, through the middle of the settlement's own channel), so the rule is this project's own guess and is labeled one
      - [x] source-reader confirmed - one Opus reader, 14 sources, verdicts per sub-question including the CONTRADICTED trio on Harie and the NOT-FOUND on what crosses a settlement's channel
      - [ ] recorded and cited - R6 carries the finding and the quotes; the reader-facing section on research/water.html and the registry entries for its new keys are NOT written
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
      verify: the rule is labeled a GUESS at all three places it lives (spec D9, cluster.py at the point of change, future-work as the knob candidate the crossing machinery blocks). The public record page is the part still owed.

