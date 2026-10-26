# Feature 433: the magistracy residences brought to the research

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-26

**Status**: Planned (spec FAITHFUL, round 3, 2026-10-26); 433#0 answered 2026-10-26: Hayakawa is the sheet corrected

**Affects**: magistracy, research record

**Approved**: the GM, 2026-10-26, "However, the third magistracy should be corrected And whatever other changes need to be made should be made in order to make the whole thing correspond to our research, and we should correct our general procedures when creating new magistracy diagrams in order to correspond to our research."

**Input**: `request.md` (the question, his answer, the sheets' recorded wealth).

## Why

The three hand-drawn magistracy sheets draw the magistrate's house far larger than the record's houses of a samurai of that
rank, 49-67 tsubo (research 0091, 0118): about 141 tsubo at Ochiba, 152 at Ubame and 145 at Hayakawa (`research.md` R1);
`docs/buildings.md` keeps the large wings as a GUESS. The GM ruled that two sheets, Ochiba and Ubame, keep the large house as
recorded deviations, their magistrates being significantly wealthier than normal; that the third, Hayakawa, is corrected,
with whatever else it takes to make the whole sheet correspond to the research; and that the procedure for new magistracy
sheets follows the research.

## Requirements

- **FR-001**: the Hayakawa sheet draws a house within the research's 49-67 tsubo, and whatever on the Hayakawa sheet does not
  correspond to the research is brought to it - building coverage against 0116's band (`research.md` R2) among it, and the
  sheet's own texts that size or label the house (its notes, lines 59 and 75, and its SVG, line 281) - every review its
  changes owe run on their occasion.
- **FR-002**: the Ochiba and Ubame sheets record the large house as a DEVIATION with the GM's reason (a significantly
  wealthier magistrate), replacing the GUESS label, in every hit of `grep -rniE "residence wing|wing length|tsubo"
  docs/buildings.md pool/magistracies` (2026-10-26) that labels or sizes the magistrate's house on those two sheets or in
  `docs/buildings.md`: among them `docs/buildings.md` lines 17 and 23 (whose Ochiba wing length no longer matches the sheet,
  `research.md` R1), and Ochiba's notes (line 65) and Ubame's (line 109), whose "keeps to the 49-tsubo residence" R1's
  measurement contradicts.
- **FR-003**: the procedure for a NEW magistracy sheet sizes the house by the research, a larger house only as a recorded
  deviation with its reason, and keeps the sheet within 0116's coverage band (how, the plan's); found by `grep -rniE
  "ochiba|template|residence" docs/usage.md docs/buildings.md docs/building-programs.md l7r/diagram/compound_example.py
  l7r/diagram/compound_model.py` (2026-10-26): `docs/usage.md` lines 5, 41 and 119 (which make Ochiba the sheet new Mode A
  sheets are copied from), `docs/buildings.md`'s compound program, and `docs/building-programs.md`;
  `l7r/diagram/compound_example.py` already draws a 49-tsubo house. The Ochiba sheet is no longer the model for the house's
  size.
- **FR-004**: the sheets are the GM's naming; 433#0 asks him whether he meant them, since the sheets' notes record Ochiba
  "ordinary - solid but not lavish; no guest house", Ubame "rich posting, broke incumbent", and Hayakawa "RICH" ("one of the
  richest postings in the province"). An answer that reverses his naming amends FR-001 and FR-002; the redraw waits on it.
  ANSWERED (the GM, 2026-10-26): "Yes, Hayakawa is the one that should be corrected." FR-001 and FR-002 stand as written;
  Hayakawa's RICH knob stays, and the house is sized within the range for it (`plan.md` D1).

## Success Criteria

- **SC-001** (FR-001, FR-004): the Hayakawa house - the sheet FR-004 names corrected - measures within 49-67 tsubo, its coverage within 0116's band (R2), and every element
  of the sheet the research speaks to corresponds to it, each review its occasion owes passed.
- **SC-002** (FR-002, FR-003): no `Research:` claim or doc calls the magistracy house a GUESS; the two deviations name the GM's
  reason; the new-sheet procedure names the research's range and the coverage band, and no doc makes Ochiba the model for a
  new sheet's house.

## Review history

- spec-fidelity round 1 (2026-10-26): CHANGES REQUIRED - (1) FR-004 leaves the corrected sheet unnamed, so FR-001 and
  FR-002 have nothing to act on, though the GM named the sheets: "specifically for Ochiba and Ubame" kept, "the third"
  (Hayakawa) corrected. The spec carries his naming. 433#0 stays kept, and an answer that reverses it amends FR-001/002.
  The redraw may wait on 433#0. FR-004 and 433#0 also state Ubame's knob in full, "rich posting, broke incumbent", since
  his reason is the MAGISTRATE's wealth. (2) FR-001's "whatever else on the sheet the change makes inconsistent" narrows
  "whatever other changes need to be made ... to make the whole thing correspond to our research", which has no causal
  condition. It must read: whatever on the corrected sheet does not correspond to the research is brought to it. SC-001
  covers that clause, not only the house and the coverage. (3) FR-002 lists no search space for the claims it replaces.
  The list names the command that built it and reaches: docs/buildings.md:17 and :23 (the prose, whose "Ochiba ~200 ft"
  wing no longer matches a sheet that draws a 90 x 50 ft block - observed 2026-10-26, method: reading docs/buildings.md:23
  against the SVG's rects); hayakawa notes :59 and :75 and svg :281; and ubame
  notes :109, whose "keeps to the 49-tsubo residence" a measurement contradicts. (4) FR-003 lists no search space, and
  "the compound program" is ambiguous (docs/building-programs.md, or l7r/diagram/compound_example.py, which already uses
  49 tsubo). docs/usage.md:5, :41 and :119 also make Ochiba the template new Mode A sheets are copied from, and FR-003
  must reach them. A procedure that yields a sheet under 0116's coverage band does not correspond to the research (the
  question put to the GM raised this), so FR-003 keeps the band; how is the plan's. (5) Figures: spec-lint finds
  '42%' unpointed at lines 25 and 38. spec-lint accepts only `R<k>`, `research.md` or `research/<name>.md` (the 0116
  page is an .html under research/questions/), so the fix is an `m:<key>` or a `research.md` entry that the paragraph
  cites. The Why's "180-200 ft wings, about 145 tsubo" for all three sheets is unmeasured. A one-shot on this round's
  own run (2026-10-26) supports the premise: Ochiba ~141 tsubo, Ubame ~152, Hayakawa ~145. Method: at 3 px = 1 ft and
  35.58 sq ft a tsubo, sum each house's outer block rects (Ochiba 270x150 px; Ubame 270x76 and 306x76 plus the 10x16
  corridor; Hayakawa 288x76 and 242x76 plus the 10x34 corridor), the kitchen's outer rect (72x54 on all three) and
  the bath rect. Excluded: zone sub-rects, engawa strips, privies, and Hayakawa's 90x30 kitchen rect at (400,160.5),
  which is not the house's. Record these as measurements.
- spec-fidelity round 2 (2026-10-26, VERIFY): CHANGES REQUIRED - items (1), (2), (4) and (5) RESOLVED: FR-001/FR-002 name
  Hayakawa corrected and Ochiba and Ubame kept, FR-004 and 433#0 quote Ubame's "rich posting, broke incumbent" in full;
  FR-001 drops the causal condition and SC-001 covers every element the research speaks to; FR-003 names its grep, reaches
  docs/usage.md:5, :41 and :119 (read, they make Ochiba the template), docs/buildings.md's "Compound programs" and
  docs/building-programs.md, and keeps 0116's band; spec-lint passes and R1/R2 carry their date and method. Item (3) PARTLY
  RESOLVED, and the remainder is round 1's own misdirection: (1) FR-002 puts Hayakawa's notes :59, :75 and SVG :281 under
  "the Ochiba and Ubame sheets record the large house as a DEVIATION ... in every place found by", which tells the
  implementer to write a deviation into the sheet the GM said "should be corrected". Those three passages belong to FR-001
  (they go false when the house is redrawn and are brought to the research then); FR-002's reach is the Ochiba and Ubame
  sheets and docs/buildings.md only. Moving SVG :281 also fixes a false claim: FR-002's grep does not hit it (re-run this
  round). And the grep also hits pool/magistracies/county-magistracy-example and ochiba-roundtrip-test, which do not draw
  the large house, so "every place found by" needs its filter: every hit that labels or sizes the magistrate's house on
  a kept sheet or in docs/buildings.md. (Ochiba notes :65 carries the same "keeps to the 49-tsubo residence" as Ubame
  :109; the grep reaches it, so no change, but the implementer should know.) Read in full: the round's diff, request.md,
  gm-review.jsonl, spec.md :1-14, docs/buildings.md :15-30, hayakawa notes :57-60 and :74-76, hayakawa SVG :281, ubame
  notes :107-110, docs/usage.md :5, :41, :119; the FR-002 and FR-003 greps re-run.
- spec-fidelity round 3 (2026-10-26, VERIFY): FAITHFUL - round 2's one item RESOLVED: Hayakawa's notes :59, :75 and SVG
  :281 now sit under FR-001 as the sheet's own texts brought to the research (each re-read: :59 and :75 size the house at
  about 145 tsubo, :281 its former 180 ft bar), so nothing tells the implementer to write a deviation into the sheet the GM
  said "should be corrected"; FR-002 reaches only the Ochiba and Ubame sheets and docs/buildings.md, through the grep hits
  "that labels or sizes the magistrate's house" there, which drops county-magistracy-example and ochiba-roundtrip-test;
  the false claim that the grep finds SVG :281 is gone; Ochiba notes :65 is named beside Ubame :109 (both re-read, both
  "keeps to the 49-tsubo residence"). No contradiction introduced: SC-001 (every element of the sheet the research speaks
  to) covers the moved passages, and SC-002 and FR-004 still name FR-001/FR-002 consistently. Implementer's note, not a
  finding: docs/buildings.md :23 names Hayakawa's ~180 ft beside Ochiba's ~200 ft, so when FR-002 rewrites it as the
  deviation the Hayakawa figure goes to the redrawn house. Read in full: the round's diff, request.md, spec.md :20-54,
  docs/buildings.md :15-24, :204, :212, hayakawa notes :59, :75 and SVG :281, ochiba notes :65 and :116, ubame notes :109,
  the three sheets' SVG grep hits; FR-002's grep re-run.
