# Handoff - feature 269 group F2 (fields: ways and seasons), session 1: research and write

Written 2026-09-27. Nothing here was skipped for a claim: RESEARCH-CLAIMS.md showed no other session on B04-B06.

## Questions new or changed

- SECTION=fields/290
- SECTION=fields/300
- SECTION=fields/310
- SECTION=fields/180
- SECTION=homesteads/210

## New registry keys

- KEY=kotobank-nodo
- KEY=kotobank-keihan
- KEY=kotobank-nawate
- KEY=kotobank-nimosaku
- KEY=nimosaku-jawiki
- KEY=kigosai-warazuka
- KEY=hirogawa-genryu-noka
- KEY=zuozhuan-chenggong
- KEY=shijing-xinnanshan
- KEY=zgkpw-longzuo

Existing keys newly cited on the fields page: aze-jawiki (notes aze-jawiki-4..6), kotobank-aze-sekai-daihyakka
(-3), kotobank-kanden (-3), kotobank-warazuka (moved from homesteads/210 to fields/310). New glossary terms:
nimosaku (variants double cropping, double-cropped), nawate, Zuo Zhuan, Book of Songs (variant Shijing).

## Items

B04 ACCURATE - the way from the houses reaches the paddy's bank and goes on as the bund, which dictionaries and the
farm ministry's glossary call the path through the paddies (azemichi, nawate, attested by about 934); no page read
has a walkers' gap in a bund or a path that stops short of the field (absence note, searched 2026-09-27) - the field
spur should always end ON the paddy's outer bund, never in open ground short of it and never through a gap; on the
three pool maps whose spur clips to 0 ft (Kashikawa, Mizuguchi, Sawada) the hamlet's nearest lane should run on to
the bund rather than no way reaching the rice; Inashiro's spur that ended 17 ft short in scrub is the same defect. The
joining point (nearest point of the bund) is a GUESS; the spec paragraph on fields/290 states the rule.

B05 KNOB (the winter crop) and ACCURATE (the rick) - rice-and-barley double cropping (nimosaku) is attested from the
Heian period, widespread by Kamakura (1264 law), grown further in the Edo period in Kinki and San'yo, limited by wet
paddies, cold and short fertilizer (fields/300); the straw rick stood on the reaped paddy or its bunds, some round a
central pole, its straw kept into the next year for fodder, manure and fuel by one Meiji-to-1960 local account
(fields/310), how far into the year unread - nothing changes on today's summer maps (no rick, no winter crop); for the
deferred seasonal maps, roll per settlement whether dry paddies carry winter barley (wet paddies never can), and draw
ricks late autumn through winter on reaped paddies and bunds (on a barley-sown paddy the bund, a GUESS).
homesteads/210's rick paragraph is now a pointer to fields/310 (its "stand to spring is a GUESS" is replaced by the
finding).

B06 CONTRADICTION-RESOLVED - fields/180 said neighboring strips were plowed to their own orientations, an inference
from fragmented holdings; the one East Asian passage read (the Zuo Zhuan, 589 BCE, quoting the Book of Songs) puts the
row direction in the LAND, tract by tract, running "south and east", i.e. one of two ways a right angle apart, and
refuses a single direction for all - so the East Asian record is no longer silent, and it supports the furlong-like
block form, not the per-plot one - `waterfields/carve.py`'s maximize-separation furrow angle (widest gap, no two
neighbors within ~6 degrees) and the `dry_plot_furrows_vary` check that forbids near-parallel neighbors both encode
the wrong shape: the generator should group dry plots into tracts on one lie of land, share a direction inside a tract
(a few degrees' jitter), and change it between tracts by up to a right angle, the check re-scoped to compare tracts
(the sketch in future-work/farming-communities.md "THE ANSWER IS A KNOB" - roll `hem_block_len` - is the mechanism;
the per-plot leg of that knob now rests only on inference and is labeled a GUESS on the page). Tract size and in-tract
jitter are GUESSES. The furrow kind's modal (written from fields/180) is likely DRIFTED.

## Left open, and why

- The rick's duration beyond "into the next year" and whether a bund rick stood at midsummer: no page read says
  (absence note on fields/310). The one other page saying "until spring" is a hobbyist's 2022 post of what it found
  online, not cited.
- No premodern Japanese source on row direction was found (kotobank and jawiki 畝, Nogyo Zensho summaries); the
  modern gardening advice (north-south for sun, along the contour on slopes) is present-day and not cited. Nogyo Zensho
  itself is on the NDL digital collection (not text-searchable here); a later pass could read its dry-field chapter.
- No correction is owed to a section another feature owns. ways/020 (265's) says the field track "simply stops at the
  hem's edge" where dry plots block the way; fields/290 is about the paddy and does not contradict it, but 265 may
  want to point at fields/290 for the paddy case.
- `make test-file` on the four record tests: 255 passed, 2 failed, both on water.html notes 44 and 46 - the W1
  session's uncommitted water work (water 070/290 fragments and registry 10490-10630, glossary 10240/10250), present
  in the tree before this session started; `check-question-size.py` also flags water/070 and water/270 (W1's). None
  touched here. The derived shared files committed with F2 (SOURCES.html, glossary.json, glossary.js,
  glossary-variants.txt) necessarily carry W1's uncommitted edits too; W1's own
  fragments, water.html and citations/water.* stay uncommitted for that session to commit.
- homesteads/210 was already 20,060 bytes with its notes before this session; moving the rick's notes to fields/310
  brought it under the cap.
