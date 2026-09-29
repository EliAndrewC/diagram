# Handoff - feature 280, group V3 (vegetation: kept-cut margins and bamboo), session 1: research and write

- SECTION=vegetation/090
- SECTION=vegetation/110
- SECTION=vegetation/150
- SECTION=vegetation/152
- SECTION=vegetation/630
- SECTION=vegetation/640
- KEY=nagaokakyo-take-nishiyama
- KEY=nagaokakyo-take-takenoko
- KEY=nagaokakyo-muraezu-1801
- KEY=ogura-kyoto-ezu-shokusei
- KEY=goto-meiji40-chizukigo

No section was held (vegetation 090's 269 line is landed: `git log origin/main..HEAD` in diagram-supplemental printed nothing for vegetation/).
Existing keys newly cited here: kotobank-karishiki (vegetation/630, three new notes from the Yamakawa and Heibonsha entries on the same page), kotobank-azebiki (vegetation/630), qimin-yaoshu-zhongzhu (vegetation/640, its bamboo chapter), hiroshima-keihan-manual (vegetation/630).

## Items

M47 MIXED - the new question vegetation/630 finds the grass of a field's bund cut for green manure (karishiki) from antiquity through early modern farming, with paddies needing wide grass-cutting ground around them (kotobank-karishiki, Yamakawa and Heibonsha entries), and one old width, the shogunate survey's 1726 reckoning of a one-shaku bund plus a one-shaku strip beside it, about 2 ft of ground no crop stood on (kotobank-azebiki); how often a bund was cut is known only from modern surveys (3.4 a year, 2007-08, brush cutters), and 090 now points there and calls the 6 ft a choice wider than the one old figure - for ScrubAndRoughGrazing / `homestead_parts/keepouts.py` (all scripted hamlets): nothing need stop; the kept-cut margin is historical; the premodern figure to calibrate to is about 2 ft (bund plus strip, from the crop to the bund's far side), beyond which the grass-cutting ground is attested but unmeasured, so 6 ft is a guess within it (the GM may keep it or narrow it toward 2 ft) - searched 2026-09-29, Japanese: 畦草 刈り 江戸時代 農書 肥料 秣 畦畔; 畔の草 刈る 農書; 会津農書 畦 草; 百姓伝記 畔 草 刈; 陰伐/日陰伐 田畑 山際 (field-shade cutting); Chinese: 清代 田埂 割草 農書 田塍; web search and kotobank, adeac, J-STAGE listings. GM ruling: the 6 ft is the record's own figure, not a GM ruling; the GM did not rule the cutting frequency.

M48 MIXED - vegetation/110 now says the levee pages it rested on describe today's mowing, while before modern times a channel's bank was the bund of the paddy beside it (the record's own finding at water/040) and bund grass was cut for green manure (at vegetation/630), with no old record speaking of a channel bank itself or of the width cut - for ScrubAndRoughGrazing / `keepouts.py` (all scripted hamlets): nothing need stop where the channel runs along a paddy bund; the 6 ft is the crop margin's choice reused (same calibration as M47, about 2 ft of bund and strip); a bank margin along a channel with no paddy bund beside it has no attestation, old or new - searched 2026-09-29, Japanese: 江戸時代 用水路 土手 草刈り 村 普請; 江浚 OR 藻刈 用水 江戸時代; web search. GM ruling: yes - the GM ruled the bank margin in (110, "What prompted it": berm strips read as scrub crowding the channels), knowingly as a visual fix, NOT knowing it rested on modern mowing.

M49 PREMODERN-ATTESTED - the new question vegetation/640 finds a bamboo thicket round the settlement before modern times: an early-Edo Rakugai-zu screen paints settlements ringed by bamboo groves (nagaokakyo-take-nishiyama), the district's villages paid a bamboo tax and managed bamboo groves through the Edo period (nagaokakyo-take-takenoko), bamboo groves beside shrines and temples were not rare around 1658-1661 (ogura-kyoto-ezu-shokusei), and the sixth-century Qimin yaoshu wants bamboo on high level ground near hills and says it dies in a wet low field (qimin-yaoshu-zhongzhu); 150 points there; no record, old or new, holds the thicket in common or seats it at a paddy's margin (absence note) - for SharedBambooGrove (`greenery.py:42`; HomesteadBamboo shares the entry) on kashikawa and mizuguchi and the legacy maps: keep drawing the thicket, but seat it at the settlement's edge on dry ground rather than "at the field margin's shady end" (that seat, and the word "shared", are guesses); the kind's Note ("the page placing the thicket at the plain's edge describes the present day") is now stale and should cite 640 - the evidence is all from the Kyoto region, a bamboo specialist, plus one Chinese manual. GM ruling: yes - the GM ruled the bamboo knob in on 2026-08-27 (152, "make that change in the manner that you had previously proposed"), knowingly as to the form, not knowing its placement rested on a present-day page.

M50 MODERN-ONLY - vegetation/152 now says a separate bamboo-grove map symbol is found only on modern maps (on the Land Survey Department's maps of about 1910, goto-meiji40-chizukigo; no page dates its introduction or traces it before 1868), while maps and pictures before modern times drew the growth itself (a village map of 1801 draws a thicket round a lord's house, nagaokakyo-muraezu-1801; the early-Edo screen paints bamboo round settlements) and their pictorial maps more often than not had no legend (ogura-kyoto-ezu-shokusei) - for SharedBambooGrove and HomesteadBamboo on the scripted hamlets with bamboo: the stand's place and extent stay (historical); the mark is a drawing convention borrowed from a modern legend, and whether it stays is for the GM - there is no old symbol to put in its place, only a picture of the growth, so the least change is to describe the mark as this project's convention rather than as the GSI's - searched 2026-09-29, Japanese: 地図記号 竹林 由来 明治 制定 年 図式; 村絵図 竹藪 描かれ 江戸時代 凡例 竹林; 村絵図 竹藪 絵画的 表現 論文; the GSI's own symbol page refused the fetch; ja.wikipedia's list of map symbols gives the symbol no date. GM ruling: yes - the GM ruled the stand glyph in on 2026-08-27, knowingly (the proposal named the GSI legend as its model).

## Left open

- The GSI's own page on the bamboo-grove symbol (https://www.gsi.go.jp/KIDS/map-sign-tizukigou-2022-tikurin.htm) refused the fetch (an SSL renegotiation error); it may give the symbol's history. The ripro.co.jp "地図記号の変遷" PDFs (https://www.ripro.co.jp/yamaoka/archive/ac-otona/sym-hensen1.pdf) were not read and may date the symbol's first appearance (Meiji era either way, so M50's outcome would not change).
- The 1801 village map's thicket is not said to be bamboo; 152 says so.
- The Rakugai-zu screen itself (Kobe City Museum) was not seen, only the Nagaokakyo leaflet's description of it.
- The Tokugawa Kinreiko order's middle clauses (the "one shaku five sun each" reckoning with adjoining land) are translated tentatively, as in fields/630.
- 090's text keeps its guess that the bund was cut "as often as today"; 630 labels that a guess too.
