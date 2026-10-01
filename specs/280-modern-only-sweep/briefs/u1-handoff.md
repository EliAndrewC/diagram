# Handoff - feature 280, group U1 (urban-features: wells and troughs), session 1

- SECTION=urban-features/082
- SECTION=0196
- SECTION=urban-features/270
- SECTION=urban-features/700
- KEY=qimin-yaoshu-yangma
- KEY=kotobank-umabune
- KEY=basuiso-jawiki
- KEY=qq-2024-beijing-wells
- KEY=kotobank-kurumaido
- KEY=shi-zhang-lulu
- KEY=zhou-2026-gugong-wells
- KEY=yamaguchi-ouchi-ido
- KEY=fukuoka-museum-ido

(Existing keys newly cited: wangzhen-nongshu-18, tiangong-shuili, both at urban-features/700.)

## Items

M96 MIXED - urban-features/082 now says a stable yard's trough is premodern (the Japanese horse trough, a fodder tub, in a dictionary of about 934; the Qimin Yaoshu's many troughs in a stallion yard and a campaign horse's trough set in the open), and so is rationed watering at set times (the Qimin Yaoshu's three waterings a day), but the free-standing two-sided watering trough the cluster was modeled on is modern-only (London's Victorian troughs; the first in Japan was London's gift to Tokyo, set up 1906), no premodern trough beside a well was found, and the drinking figures are modern with no premodern figure beside them; the capacity now counts one side of each trough (~7 head, a plain yard ~14, a caravan ground ~20) and no longer leans on the London throughput - for `stable_troughs_beside_well` / `civic_grounds/stable_yard.py` and the gate stable yards of minami, nagahara, tango: at map scale nothing visible changes (the glyph is the same); the generator's comments, any modal text and the capacity reasoning should stop describing a two-sided London-type trough and describe the plain one-sided yard trough; the 14 ft length stays, labeled a guess; the placement beside the well stays (a GM ruling) but is labeled that the trough held water there is a guess - searched 2026-09-28: Japanese (馬槽, 飼葉桶, 馬水槽, 宿場 馬 水飲み 水槽, 馬に水 桶 宿場, 江戸 厩 水飼), Chinese (石马槽 驿站 饮马槽, 饮马槽 石槽 井台 古井, 古代 客栈 马槽 石槽 饮马, 齐民要术 养马 饮), English (Qing inn courtyard stone trough), over Kotobank, ja.wikipedia, Gushiwen (Qimin Yaoshu), museum pages, Beijing Evening News, NetEase. GM ruling: the GM ruled the trough count and the placement beside the well, and the dig-your-own-well rule, in knowingly (2026-07-23, recorded in the section); no record shows the GM ruled on the two-sided London form itself, so that was not knowingly ruled in.

M97 MIXED - 0196 now rests "capacity never binds" on late-Qing Beijing (1,228 wells for an official ~800,000, at least 652 persons to a well, a modern writer's division of two Qing counts) and labels the Sphere ~400 per open well a present-day relief standard the rule does not rest on - for the Well kind: the Well modal (`interactive/classes/water_and_ways.py:322`, and its Sources line 332) should replace "Sphere: one open well serves about 400 inhabitants" with the Beijing figure (a well served several hundred; late-Qing Beijing at least ~650) and add `qq-2024-beijing-wells` to its Sources; the generator's well counts do not change (they are the disclosed liberty and the capacity is used only in the negative), so the six legacy towns and cities and the scripted hamlets are untouched - searched 2026-09-28: Chinese (京师坊巷志稿 水井, 北京 水井 清代 户 人口 水窝子), Japanese (江戸 長屋 井戸 何軒 共同), over Beijing Daily, Tencent News, Qianggen, eonet, geolab. The Beijing figure is a capital's (many wells bitter, water carried by sellers), so it bounds capacity from above and says nothing of a village's well count. GM ruling: the per-tier well bands are a disclosed liberty the GM accepted; the Sphere figure was never ruled on by the GM.

M98 MIXED - urban-features/270 (split for size into 270 and new 700) now says the sweep, the pulley frame and the roofed well are premodern (Wang Zhen 1313: sweep for shallow water, windlass on a frame over the well for shallow and deep; Tiangong Kaiwu 1637; a pulley on a well frame in a Western Han mural; the pulley well in Kyoto by 1753; a pavilion over every Ming-Qing palace well, one with a pulley on a beam), that the 118 cm curb is a modern book's undated measurement, that no premodern curb survives excavation, and that the ~4 ft curb is calibrated to a Muromachi shaft about 1 m across; the ~1900 Owari well is labeled Meiji - for the Well kind and the maps: nothing to stop drawing; the pulley frame (two posts and a beam) is no longer a guess at the form, only at its proportions; the one-in-three roof stays a labeled guess (no premodern count of roofs over ordinary wells found); the depth-weighted gear knob now has a premodern rule behind it (Wang Zhen) - searched 2026-09-28: Japanese (車井戸 滑車 室町 江戸, 跳ね釣瓶 絵巻 一遍聖絵, 江戸 井戸 発掘 方形 井戸枠, 井戸屋形 名所図会, 守貞謾稿 井戸 車井戸, はね釣瓶 洛中洛外図), Chinese (天工开物 桔槔 辘轳, 井亭 明清), over Kotobank, ja.wikipedia, Fukuoka City Museum, Yamaguchi City, kinsei-izen, NDL CRD, the CAS agri-history site, Palace Museum, Beijing Daily, Wikisource (Wang Zhen, Tiangong). GM ruling: the wellhead's marker size is a GM ruling (2026-07-21); the gears, the curb and the roof were not individually ruled by the GM.

## Left open

- The roof's frequency over ordinary wells: no premodern count found; a folklore or village survey is where it would be. The kinsei-izen list of old wells was read but not cited: its roofs are mostly later additions and its dates are traditions.
- The Nihon Kokugo Daijiten's 1685 illustration of a pulley well (Saikaku shokoku banashi) is named on kotobank but not visible in its text; it would push the Japanese pulley well to 1685.
- The Ehon Edo fuzoku orai's Edo well-cleaning passage (a pulley at the back-alley communal wells) was read on eonet but its book's date (believed 1905, a Meiji recollection) is summary-only, so it was not cited.
- No held section: 269's claim does not include urban-features and its clone's diff there against origin/main is empty (only merge commits touch it).
