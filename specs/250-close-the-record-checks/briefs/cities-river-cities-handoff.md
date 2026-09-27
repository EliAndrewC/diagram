# Handoff - feature 250, page `cities/river-cities`, session 1 (locate, read, write)

## Changed questions

- SECTION=010 (most-provincial-cities-sit-on-a-river)
- SECTION=020 (which-way-does-an-offtake-leave-a-river-and-why)
- SECTION=030 (does-a-citys-canal-open-its-own-mouth-on-the-river)
- SECTION=040 (the-wharfs-working-face-piers-quays-and-stepped-landings)

## New registry keys (each needs source-applicability)

- KEY=chongqing-chengqiang-zhwiki (zh.wikipedia 重庆城墙)
- KEY=cementconcrete-headworks (cementconcrete.org, headworks layout; unsigned, no references)
- KEY=ahmed-soliman-2022 (SCIREA J. Civil Eng. 7(1) 2022, lateral-intake flume study; PDF only)
- KEY=kiba-jawiki (ja.wikipedia 木場)

Existing key newly cited on this page: fengshui-enwiki (010; already quoted on religion-and-death 150).

## FR-002 items and their forms

1. 010, "tapping the river upstream and returning downstream so the current flushes it" - ABSENCE, already carried by `most-provincial-cities-sit-on-a-river-2` (dated 2026-09-14); its search extended with a 2026-09-27 pass (ja 堀 Niigata passage, zh 护城河/城池/重庆城墙: no intake-and-return). No source found.
2. 010 spec 1, "the river IS the stronger defense on that flank" - rewritten to "on that flank the river IS the moat" with a CITATION (`chongqing-chengqiang-zhwiki`: 「依江为壕」 and the gazetteer's 「环江为池」), plus a GROUNDS note `most-provincial-cities-sit-on-a-river-4` (a drawing convention) on "drawn heavier ... the dug moat included". The comparative "stronger" was dropped: no page read compares a river's defensive worth with a dug moat's (search in the note's HTML comment).
3. 010 spec 1, "the dead cross the river ..." - GROUNDS `most-provincial-cities-sit-on-a-river-5` (this project's decision), and the set-back now links to religion-and-death "How far from water does a burial ground lie?".
4. 010 spec 2, "never on a paddy body or on its ditches" - CITATION `fengshui-enwiki` (graves far from water and on unvaluable farmland, southern China), plus the same link to religion-and-death 180.
5. 020, the two "cautions" on no readable page - both now CITATIONS: `ahmed-soliman-2022` (right-angle intakes draw a large sediment share; least at the paper's 164°, read by this page as ~16° off the flow - the conversion is flagged in the note as this page's reading of the paper's Fig. 2; the Bulle/Schoklitsch "no optimum" review line) and `cementconcrete-headworks` (regulator 「90o to 120o with the axis of weir」). "often-quoted" was dropped from the prose. The sentence was rewritten to say what the flume found.
6. 030, "the single navigation entrance" - reworded to "on these maps ..." with a GROUNDS note `does-a-citys-canal-open-its-own-mouth-on-the-river` (this project's decision).
7. 040, the matou stepped landing - already carries its own CITATION `matou-zhwiki` directly after the clause (the note says the faced bank is not on that page); nothing changed.
8. 040, "a port that also handles timber and stone wants at least one [pier]" - the source-reader found ja 木場 cuts against the timber half (timber floated, worked and stored in the water). Rewritten: stone keeps the claim, labeled "in this page's guess", with ABSENCE note `the-wharfs-working-face-piers-quays-and-stepped-landings-2` (searched 2026-09-27: ja 桟橋, en Pier); timber now "wants none", with a CITATION `kiba-jawiki`.

## FR-006

None owed on this page.

## Open, for session 2

- The ahmed-soliman-2022 note's degree conversion (164° -> about 16 degrees off the flow) is a reading of the paper's figure; the source-reader confirmed Fig. 2 draws alpha from the upstream main channel. Quote-check should confirm the prose's "about 16 degrees" is fairly labeled.
- cementconcrete-headworks is weak (unsigned, undated, typos); source-applicability should judge whether it can carry the weir-axis claim. aboutcivil.org (Haseeb Jamal, 2017) gives only 90° to the weir and is not registered.
- 020's prose now names a flume study; record-format may want glossary tooltips for "flume" and "headworks" / "weir".
- None of the four questions is over the 20,000-byte cap after the edits (scripts/check-question-size.py silent).
- The saved pages are in /tmp/l7r-check/cities-river-cities-pages (PDFs: 10 idc, 12 IGNOU GM copy, 13 aceesjr, 14 scirea = ahmed-soliman-2022).

## From session 2a (010, 030; 2026-09-27)

- For whoever checks 020: source-applicability on `ahmed-soliman-2022` found that the paper tested only 110 to 170 degrees, so "right-angle intakes draw a large sediment share" comes from the paper's framing of earlier work, not from its own runs. SCIREA was also on Beall's list. The registry write-up now says both. 020's prose should rely on the direction of the effect, not on the 164 degree figure, and should not present the right-angle line as the flume's result.
- Open, not fixed: the glossary tooltip matcher (`research/assets/record.js`, and `interactive/assets/page.js` for the modals) matches case-insensitively, so the capitalized proper names "Han" (50 occurrences across the record: Han River, Han dynasty) and "Fen" (9: Fen River) show the tooltips for `han` (a daimyo's domain) and `fen` (a land unit). This is a defect across the whole record, not just this page. A fix needs a per-term case flag carried through `glossary_for` in `page.py` and both matchers. That is engine code, which would put this research queue on the gated route, so it was left to a feature of its own.
