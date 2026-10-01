# Handoff - feature 280, group C5 (session 1: research and write), 2026-09-29

## Sections

- SECTION=cities/fabric/030
- SECTION=0174
- SECTION=cities/hinterland/600
- SECTION=0151

## New registry keys

- KEY=kemingbaike-pingyao-gucheng
- KEY=sohu-moat-history
- KEY=zhengding-chengqiang-zhwiki
- KEY=han-changan-zhwiki
- KEY=visitbeijing-caiyuan

## Items

M128 MIXED - the record now says the unbuilt ground inside a wall is premodern (Sui-Tang Chang'an's plowed south, Jinan's lake at a fifth of its original walled area, a third of Beijing waste ground in 1895), that every share read is a capital's or a provincial capital's, and that the map keeps a county seat's open reserve to no more than a fifth; 25-30% is given by no page read - `citybudget.py` should drop the 25-30% "norm" from its docstring and comment (lines ~19, ~145) and keep the 20% cap as the ceiling, calibrated to Jinan's fifth; the future city generator must not exceed 20% - searched 2026-09-28 and 2026-09-29: English and Chinese web searches (明清 城内 空地 农田 菜地 县城 比例, 城中多隙地, 城内多旷地), Chang (1977), The Paper's essay on fields in cities, a Lu Xiqi and Ma Jian article, a Jiangxi Republican-era land-use study (search summary only); a Qing county-town study (iqh.ruc.edu.cn) unfetchable. GM ruling: none on the reserve share; the 25-30% was the record's own guess (specs/009), not the GM's.

M129 PREMODERN-ATTESTED - new question hinterland/600 dates farmland inside a Chinese city wall to the Sui-Tang (Chang'an), the Ming (Beijing's Shichahai paddies; the Jiajing outer wall enclosing vegetable land), 1853 Nanjing and 1910 Jining, and the night-soil trade to Japan in 1525, 1585 and 1789-90 (Edo); hinterland/050 points at it - no change to the kinds or maps: the legacy provincial city's in-wall farming quarter and its vegetable tracts stay. The Chinese night-soil record read is still only King (1909); no earlier Chinese account was sought (it was not needed for the outcome). GM ruling: the in-wall farmland is the GM's density canon for the provincial tier (freed ground goes to farmland), ruled knowingly; the farmer ring stays a labeled deviation.

M130 MIXED - defenses/100 now gives the period figures first: the Song compendium (1044) fixes no width (it follows the ground, dug to the water, about thirty paces out), the Ming Wubei Zhi sets a floor of 3.5 zhang wide (about 35 ft) and 1.5-2 zhang deep (15-21 ft), Pingyao's moat in 1370 was one zhang (about 10 ft), the Han capital's excavated moat is 8 m or 45 m depending on the encyclopedia, and Zhengding's ten zhang (about 100 ft) is undated; the 55-100 ft great-city band is present-day measurement only, and the broad water moat (Xiangyang, Guide) has no dated width - kinds/maps: the city moat code's 66 ft (`settlement/city/moat.py:46`) rests on no period figure; the spec now says a provincial seat's moat should be drawn at about 35-36 ft (the treatise's floor) and a county seat's about 10 ft; minami, nagahara and tango redraw their moats at ~36 ft if the orchestrator applies it (and check `castle_civic.py:98`, whose ~80 ft castle moat is justified as "wider than the city's own ~66 ft"); the broad water moat is not drawn (no generator draws it today) - searched 2026-09-29: Chinese and English web searches (县志 城池 池广 深 丈 护城河; 明代 县城 护城河 宽度 地方志; 城河阔必三丈五尺; 濠深广各一丈; 襄阳 护城河 志 濠 阔; 归德府城 城湖 形成), the Wujing zongyao chapter on Wikisource, zh.wikipedia on the moat, walled cities, city walls and the walls of Xi'an, Datong, Xingcheng, Jingzhou, Shouxian, Nanjing, Wuxi, Zhengding, Pingyao, Xiangyang and Han Chang'an; ctext refused automated reading of the Wubei Zhi. GM ruling: none on the moat width; the 66 ft was a calibration, not a ruling.

## Open

- The Wubei Zhi rule is read on a popular article's quotation (sohu-moat-history), not on the treatise; ctext refuses automated reads. A GM-fetched copy of the Wubei Zhi's 城 chapter would firm it.
- TO-DOWNLOAD entries 299 (Wuxi Daily: Wuxi's Yuan-Ming moat, reportedly 7 zhang wide) and 300 (Ming Yunnan walled seats from the Dian zhi) might give the period figure for a prefectural seat's moat that the band lacks; if one does, the provincial-seat width may rise above the treatise's floor.
- The 050 section stays at 19,640 bytes with its notes; any further addition there must go in 600 or a split.
