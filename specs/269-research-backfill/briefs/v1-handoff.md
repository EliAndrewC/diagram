# Handoff - feature 269, group V1 (vegetation: woods), session 1: research and write

Written 2026-09-27. No item was claimed by another session. The saved pages are in `/tmp/l7r-check/269-v1-pages`
(`pNN.txt` is text pulled from the PDF of the same number); one `source-reader` read every claim (16 READ,
2 NOT-FOUND: nothing read puts a boundary on a ridge, stream or path, and nothing gives a crown width).

## Sections

- SECTION=vegetation/210
- SECTION=vegetation/220
- SECTION=vegetation/230
- SECTION=vegetation/140
- SECTION=vegetation/060
- SECTION=vegetation/070

## New registry keys

- KEY=miura-2019-yashikiyama
- KEY=takehara-2004-yashikirin
- KEY=kotobank-yashikirin-heibonsha
- KEY=kotobank-murazakai
- KEY=yaotsu-sanron
- KEY=narumi-2002-sanron-ezu
- KEY=kanagawa-museum-saikyo-ezu
- KEY=migita-chiba-konara-canopy
- KEY=hasegawa-2018-toyama-konara
- KEY=rinya-satoyama-junkan
- KEY=niigata-konara-coppice
- KEY=katakura-1989-konara-coppice
- KEY=iriaichi-jawiki

## Items

B26 ACCURATE - the trees among a village's houses were each homestead's own wood (yashikirin) on its lot, and the one period measurement read (a 1684 Mito-domain register quoted by Miura 2019) gives three households' woods of 5 se 21 bu, 1 tan and 2 tan 6 se, about 6,100 to 27,800 sq ft, with form and size said to vary; no page gives a size or clump count for a copse shared by the whole village (absence note) - the copse's floor should be set per homestead, not by the gaps left over: each homestead that keeps a wood gets a rolled 6,000-28,000 sq ft of trees counting its windward grove and its copse share together (calibrated liberty, not a knob), so Inashiro's single 30 x 30 ft clump and Mizuguchi's three clumps over 335 ft draw far less than one household's wood; farming-communities.md candidate fix (1) now has its number, and (2) (do not record an undrawn copse) still stands on its own.

B27 CONTRADICTION-RESOLVED (siting) and SILENT (the boundary features) - the village is houses, then fields, then hill land (kotobank-murazakai), the satoyama is the nearest, lowest slopes around the settlement (satoyama-jawiki), and the fuel wood stood on the outer edge beyond the fields (Miura 2019 quoting a 1910 account), while low grass and riverbank land was the other, grass commons (iriaichi-jawiki); hill-land boundaries were vague for the terrain and, when ruled, were drawn lines that bent, marked with rocks and sealed at their ends and bends; that they followed ridge, stream and path is on no page read and is now labeled a GUESS with an absence note - Kashikawa's two parcels (505 and 887 ft downslope, one 75 ft from the reed marsh) contradict the record: a woodland parcel should be seated beyond the fields and on ground higher than the fields it adjoins (the scorer's upslope term must bind, not be outbid by nearness), low wet ground left to grass and reeds; the square-parcel item (A) is unaffected - the irregular outline stays ACCURATE, the ridge/stream/path bounding a GUESS. vegetation/140's heading text changed (its anchor kept).

B28 CONTRADICTION-RESOLVED (stocking) and SILENT (crown size) - a worked fuel wood was thin, low, many-stemmed trees cut every 15-30 years, a cut konara stump sending up ~33 shoots (~14 after three years), holding ~100 m3/ha at 20 years against 265 uncut; the one stems-per-hectare figure read for konara of about coppice age is 1,700/ha at 29 years (one per ~63 sq ft, ~8 ft centers), two to three times the unread 500-800 band, which vegetation/060 now labels a GUESS; no page gives a crown width for any coppice tree - the woodland commons should be stocked at ~1,700 crowns/ha on ~8 ft centers with crowns ~8-9 ft across (the width a GUESS sized so neighbors meet), which is farming-communities.md item F's "stocked like parkland" answered with a number; the belt and other woods keep 060's figures (CANOPY_R_FT and CANOPY_SPACING_FT for them stay guesses), so the one-constant finding in vegetation/070 would split if the commons takes its own crown.

## Left open, and owed elsewhere

- vegetation/020 (the three groves) describes the dooryard copse as spread through the open gaps among the houses; vegetation/210 finds it is the homesteads' own woods. 020 should point to 210 and drop "throughout the gaps" as the sizing rule. Not in a range this group owns, so not edited.
- vegetation/154 (did every farmstead keep bamboo; group V2's B29): the 1910 account quoted in 210's notes puts a bamboo wood among the woods round the farmhouses on the Musashino upland (`miura-2019-yashikiyama`, note `miura-2019-yashikiyama-2`) - usable evidence for V2.
- The engine repeats "bounded by ridge, stream and path" in `hamletgen/hinterland.py`'s comment; it is now a labeled guess in the record, and the comment should say so when the generator is next touched.
- `scripts/check-question-size.py` reports homesteads/210 (the farmstead fixtures, group H1's) at 20,060 bytes, over the cap; not touched here.
- Crown width stays SILENT after two dated searches (2026-09-14, 2026-09-27); a third pass with a different tool (the MDPI Castanopsis paper and the Kobe ScienceDirect paper, which refuse an automated fetch) is the only lead. They are not added to TO-DOWNLOAD.md because the konara figures now cover the woodland commons; add them if the belt's crowns are researched.
