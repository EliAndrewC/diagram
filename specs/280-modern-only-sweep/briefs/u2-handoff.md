# Handoff - feature 280, group U2 (urban-features: brewery, pawnshop, smithy), session 1

- SECTION=urban-features/030
- SECTION=0201
- SECTION=0205
- SECTION=urban-features/440
- SECTION=urban-features/710
- KEY=itami-okada-sakagura
- KEY=qinxiang-dangpu-sina
- KEY=yaowan-dangpu-chinatax
- KEY=sakai-inoue-kajiyashiki
- KEY=sakai-tcb-teppo-kajiyashiki
- KEY=boso-no-mura-isumiya

## Outcomes

M99 MIXED - the brewery's evidence moved from Trade works (030, which was over the 20,000-byte cap) to a new question, urban-features/710 "How big was a brewery's vat hall before modern times?": the Edo-period halls measured run about 50-62 ft long (Tochigi, late Edo, about 60 x 30 ft; Itami, about 1715, a two-story hall 15.7 x 14.8 m, about 52 x 49 ft; Kanazawa's store 62 x 23 ft in 510), while the 96-103 ft hall is Meiji and no Edo hall that long was found - `s.brewery` (minami, nagahara, tango) should draw its vat hall about 50-62 ft long and about 23-49 ft across, not 96 ft; the 030 spec now says so - searched 2026-09-28 in Japanese on the web and the national cultural-heritage database: "酒蔵 江戸時代 桁行 梁間 重要文化財 仕込蔵 建築年代 18世紀", "旧岡田家住宅 酒蔵 桁行 梁間 延宝", "灘 酒蔵 江戸時代 建築 桁行 間 大蔵 規模 文化遺産オンライン 江戸後期 酒造" (registered halls of 16 ken or more found were Meiji or later: Hatsuzakura, Kunimanzai 1908, Takagaki 1926 at 10 ken). GM ruling: the brewery compound is ruled in (GM 2026-07-24, "I'd like all of them", knowingly); the 96 ft size was never a GM ruling.

M100 PREMODERN-ATTESTED - 340 now cites a mid-Qing pawnshop at Qinxiang (Wuxi), a two-story building about 18 x 20 m (59 x 66 ft) on the middle of a market town's old street with an 8 m street gable and 5 m fire walls, and the Qing Baofengcui pawnshop at Yaowan, fronting the main street, four courts deep, its pledge store in the front court (the town's two pawnshops are in the county gazetteer for the early Qing) - `s.pawnshop`'s Chinese form (minami, nagahara, tango) stands; it may be drawn up to about 59 x 66 ft; nothing to stop. The Macau trade history's multi-story goods building (貨樓) was read but is undated and is not cited. GM ruling: the pawnshop is ruled in (GM 2026-07-24 list, knowingly); the two-form knob is the record's, not a GM ruling.

M101 MODERN-ONLY undated-custom - 430 now says the Boso no Mura smithy (21 x 18 ft, gabled, tiled, work floor inside) was built from a museum's survey of a working smithy of modern times that it does not date, with a Meiji fitting, and the fitting order is from smithies of today; no village smithy plan from before 1868 was found, so under the GM's 2026-09-28 rule the 21 x 18 ft plan is held back (a village smithy draws as one of the village's ordinary houses, its size a guess) unless the GM admits undated records of custom; the village smith himself stays premodern-attested (Ehime, Yashio) - the future village generator should not take 21 x 18 ft or the tiled gable as history; no map draws it today - searched 2026-09-28 in Japanese: "鍛冶屋 江戸時代 作業場 間取り 土間 間口 民家 文化財 野鍛冶", "近世 鍛冶工房跡 発掘調査 江戸時代 村 鍛冶遺構 建物跡 規模", "江戸時代 村 鍛冶屋 家屋 間口 奥行 村明細帳 鍛冶 小屋 規模", "職人尽絵 鍛冶 ふいご 仕事場", "鍛冶屋 江戸後期 建築 移築 民家 指定文化財 鍛冶場 土間", "和漢三才図会 OR 人倫訓蒙図彙 鍛冶 挿絵 仕事場 鞴", and in English "Edo period village blacksmith workshop floor plan", on the web and the national cultural-heritage database (the Iwamuro "Kokajiya" house of 1830-68 is a townhouse whose record says nothing of a forge). GM ruling: none on the smithy's form; the GM's rule of 2026-09-28 governs.

M102 MIXED - 440 now cites the Sakai gunsmith Inoue's house (on its site by 1689), an early-Edo block 3.5 ken (about 21 ft) wide with a through earth floor, whose street room was the finishing room and whose forge on show is rebuilt from a Meiji drawing: the 21 ft frontage of a town smith's house is premodern, while the 18 ft depth (from the modern village model) and a hearth in the street room are not - the town smithy (unscripted) should be about 21 ft wide and as deep as the shop-houses beside it (depth a guess), not 18 ft; the 440 spec now says so - searched 2026-09-28 in Japanese: "鍛冶町 城下町 間口 屋敷 江戸時代 鍛冶屋 軒 間口 間", "堺 鉄炮鍛冶屋敷 井上関右衛門家住宅 間口 奥行 建築年代 江戸時代 作業場", "鍛冶屋 江戸時代 絵 店先 土間 ふいご 町の鍛冶屋 仕事場 通りに面". GM ruling: none on the town smithy's size; the county town's master smith is canon (budgets.md).

## Left open

- 0207's spec still says "larger halls are in Trade works"; they are now in 710 (030 points there). 510 was outside this group's write list; a one-line pointer fix is owed.
- The Qinxiang source is a blog repeating a Wuxi Daily article (wxrb.com/doc/2022/04/17/162476.shtml) and the Jiangsu gazetteer office's copy (jssdfz.jiangsu.gov.cn/n97/20220420/i18067.html); neither original would load in the container (SSL errors). The check session may try them.
- Moving the brewery evidence from 030 to 710 changes the section `s.brewery`'s modal was written from; entry-drift owes a pass.
- Pre-existing and not this group's: towns.html [^99] fails test_footnotes (from T2); urban-features/082 is over the size cap (U1).
