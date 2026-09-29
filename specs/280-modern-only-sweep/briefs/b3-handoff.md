# Feature 280, group B3 handoff (session 1: research and write, 2026-09-29)

- SECTION=buildings/780
- SECTION=buildings/800
- SECTION=buildings/900
- KEY=tuancheng-yanwuting-zhwiki
- KEY=dachedian-zhwiki
- KEY=michie-siberian-overland
- KEY=kotobank-chugen
- KEY=sakai-hanshiro-bakumatsu
- KEY=mitamura-nagaya-tcpip
- KEY=meijimura-hohei6-heisha

Changed write-ups (Used for only): edo-hantei-jawiki, chongming-yanwuchang. No section was held (no 269 commits on buildings 780/800; 900 is new).

M117 MIXED - buildings/780 now says Chongming's drill ground and its three-bay hall are premodern (Wanli gazetteer, 1586; hall raised and named 1662; repaired 1799 and 1846) but the nine-bay 29 x 11.5 m hall pulled down about 2000 has no date of build, and the only other pre-1912 drill hall found (the imperial Jianrui camp's, 1748) is five bays, given in bays only - the Chinese state institution (Mode B city tier) should draw a drill hall of three bays, about 32 ft wide on the last hall's bay of about 3.2 m, depth a guess, instead of about 95 by 38 ft; ground, platform and south gate unchanged - searched: 崇明 演武厅 重建 with the Qing reign names; 县 演武厅 清代 文物保护单位 面阔 进深 米; 现存 清代 县城 演武厅 面阔三间/五间; zh.wikipedia 团城演武厅; beijing.gov.cn Tuancheng pages (wwj.beijing.gov.cn unfetchable); Chinese, web, 2026-09-29. GM ruling: none on the drill hall's size; the 95 x 38 ft figure was the record's own reading (feature 271), not a GM ruling.

M118 PREMODERN-ATTESTED - buildings/800 now says the carters' yard inn is Ming by name (mule-and-horse great inns for carters), was seen in 1863 on the Nankou road (a courtyard full of gear and horses, mules and donkeys, travelers in a common dormitory; animals tied in a Beijing inn's courtyard), and the Northeast cart inn is dated from the end of the Qing; the large stable as a building and hay in the corners rest only on the NetEase account, which covers the late Qing and the Republic together - the kinds and maps named need no change (the Chinese roll of the inn knob keeps the fenced yard, lodging and stable); if the orchestrator wants the stable proved separately from the Republic, the fallback is animals tied in the open yard (the 1863 form). GM ruling: none; the Chinese inn knob is the record's (feature 271).

M119 MIXED - new buildings/900 ("How were the rooms of a compound's barracks divided?") says a warrior's rowhouse was divided into dwellings (a unit of nine shaku by two ken, an earth-floored entry and a raised plank floor), with a few unmarried men sharing a unit (three retainers in Wakayama's Edo duty rowhouse, 1860) and the lowest servants (chugen) in large common rooms; no page read puts a bed, bunk or sleeping shelf in a premodern rowhouse, and the earliest barracks with beds found is the Meiji army's of 1873 - the Barracks kind (office.py What: "divided into bunk rooms"; buildings.md:57 "internal bunk divisions") should stop saying and drawing bunk rooms or bunk divisions and say a rowhouse divided into dwellings (or one large common room for servants), and its size band (20-70 x 10-40 ft, a guess) should follow buildings/750's staff rowhouse (12-24 ft deep, 80-145 ft long, bays 12-18 ft); magistracy sheets that label bunks lose the label - searched: 勤番長屋 部屋 相部屋; 勤番長屋 間取り 畳; 中間部屋 大部屋; 足軽長屋 一部屋 何人; 酒井伴四郎 長屋; 蚕棚 二段寝台 兵舎 明治; Kotobank 中間, ja.wikipedia 江戸藩邸 and 酒井伴四郎, JAANUS nagaya and tomobeya, Meiji-mura; Japanese and English, web, 2026-09-29. GM ruling: none; feature 262 wrote the kind and its size band is labeled a guess, and "bunk" was never ruled on.

Left open:
- The kind's Entry for Barracks names 'Staff housing spans a real spectrum' and the size-hierarchy section, not buildings/750 or the new 900; the orchestrator may want to point it at 900 when it rewrites the kind (modals only reach a new question when the GM asks).
- make test-file: test_footnotes fails on towns.html [^99] (a grounds note naming "arithmetic on the counts cited"), a page this group did not touch; buildings.html passes.
- The Kurume domain's Edo duty-rowhouse scroll (Tokyo Museum Collection, works/6235818) returned 403 and was not read; it might show a duty rowhouse's rooms, but nothing here rests on it.
