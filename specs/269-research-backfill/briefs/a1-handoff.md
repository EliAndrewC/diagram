# Handoff - feature 269, group A1 (archetypes: dike-pond), session 1: research and write

Written 2026-09-27. No item of A1 was claimed by another session. Canon (`make canon`: mulberry, silkworm, pig,
duck, fish pond, sugar cane) says nothing beyond silk and mulberry in general, so all three items are history.

## Questions new or changed

- SECTION=archetypes/200
- SECTION=archetypes/210
- SECTION=archetypes/220
- SECTION=archetypes/230
- SECTION=archetypes/140
- SECTION=archetypes/170
- SECTION=archetypes/171
- SECTION=archetypes/172
- SECTION=archetypes/173

(140, 170 and 171 changed only by a pointer sentence or a bullet; 172 dropped the unreadable Miles 2003 note and the
nursery-share sentence, which moved to 200; 173's closing claim was corrected.)

## New registry keys

- KEY=guangdong-xinyu-22
- KEY=guangdong-xinyu-20
- KEY=guangdong-xinyu-25
- KEY=guangdong-xinyu-27
- KEY=nongzheng-quanshu-41
- KEY=pwsannong-gudai-zaisang
- KEY=pwsannong-zhusanjiao-nongyeshi
- KEY=kotobank-souen
- KEY=kotobank-negari

## Items

- B32 (fry ponds) KNOB - Qu Dajun (late 17th c.) says fry ponds existed only in Jiujiang, where seven-tenths of the pond water raised fry; everywhere else ponds raised grown fish on fry bought from Jiujiang, whose West River fry landings were granted to it in the Hongzhi reign; a modern manual's 25-30% is for a farm that stocks itself - `FryPond` / `hamletgen` fry share: the one-smallest-parcel-in-ten share matches neither attested form; the knob is an ordinary grow-out hamlet (no fry ponds) or a fry village (about 70% of pond water nursery); turbid fry water against clear grow-out water could be shown in pond color. GM's call (the fry pond was the GM's choice); the `FryPond` Note should drop "the century the trade rose in is not [read]" (now read: Hongzhi, 1488-1505) and the manual share as the basis.
- B32 (pig sty) ACCURATE + SILENT - pigs were the dike-pond district's stock (pwsannong history, mid-Ming on), fed in the Qing loop on pond-surface feed with their dung going to the mulberry; a late-Ming instruction (Xu Guangqi, 1639) pens livestock (sheep) on a fish-pond bank so the dung feeds the fish; no page gives the share of households - `PigSty` stays; its sources can add `pwsannong-zhusanjiao-nongyeshi` and `nongzheng-quanshu-41`, and `STY_SHARE` (0.25-0.50) stays a labeled guess.
- B32 (duck pen) CONTRADICTION-RESOLVED - the premodern delta's ducks were herded in the coastal rice fields (Qu Dajun, chapter 20) and duck-raising was the sand-field district's trade, not the dike-pond district's; no page puts a premodern duck pen at a fish pond; archetypes 171 called the pond-corner duck pen an attested form, and it now points to 210 - `DuckPen` on a premodern dike-pond hamlet is a modern form; the GM chose it, so whether it stays, is relabeled as a later form, or moves to the paddy hamlets' fields is the GM's call; `PEN_SHARE` stays a guess either way.
- B33 ACCURATE (density) + SILENT (crown width) - old spacing ran along a continuum set by training height: about 300 mid-trunk trees a mu (one per ~24 sq ft) in the late-Qing Yangtze delta, 8,000-10,000 root-cut bushes a mu (~1 sq ft) in the undated Pearl delta figure, 800-1,000 (root-cut, 11-13 sq ft) and 400-600 (mid-cut, 18-27 sq ft) per 10a in 20th-century Japan; no page gives crown width - nothing to change unless the GM rules: the drawn one bush per ~23 sq ft sits at the one dated premodern figure and inside Japan's mid-cut range; it is calibrated liberty, and the density ruling stays the GM's (fc:10).
- B34 CONTRADICTION-RESOLVED - archetypes 173 said no non-mulberry dike is attested before the mulberry dike gave way; the fruit dike is older: Qu Dajun lists pond dikes planted with lychee most, tea and mulberry next, then mandarin and orange, longan too, and a modern history dates fruit-dike ponds to the mid-Ming, before the mulberry dike; the cane dike is named for the Ming-Qing only in an undated modern list; banana and cane were field crops rotated in Zengcheng; no premodern banana or vegetable dike - `FruitDike`'s Note ("by the gazetteer's account it is a modern one; the fruit is named only in bulk") is now wrong: it is the oldest dike planting read, its fruit is lychee above all, with longan and citrus; `BananaDike` has no premodern attestation; `SugarcaneDike` rests on one undated secondary listing; a tea dike is attested and not drawn. Which crops a premodern hamlet may roll is the GM's open decision (fc:25).

## Owed and left open

- The modals that name archetypes 171, 172 and 173 as `Entry:` (PigSty, DuckPen, FryPond, SugarcaneDike, BananaDike, FruitDike) will be named by `_entry_owed.py`; the rewrites above are for the orchestrator.
- Nothing A1 found owes a correction to 265, 267 or 268.
- Archetypes 180 (sty against the sluice) needed no change: nothing read speaks to the sluice.
- Crown width of a mulberry bush: two searches, nothing. Zhong Gongfu's 1980 paper (Acta Geographica Sinica) and Ruddle & Zhong 1988 remain the likely sources; the progressingeography.com PDF of a paper on the delta's mulberry-dike fishponds would not decode in the container.
- `make test-file` over the four record tests: 255 passed, 2 failed, both on `water.html` (an absence note with a link, a grounds note with a non-list reason) - another session's uncommitted W1 check-c work in this clone, not A1's. `check-question-size.py` flags homesteads 210, vegetation 120, water 070 and water 270; no archetypes question is over the cap.
