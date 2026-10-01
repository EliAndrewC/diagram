# Feature 280, group W1 (water: channel widths) - handoff from the write session, 2026-09-28

## Sections written

- SECTION=0068
- SECTION=0055
- SECTION=water/040
- SECTION=water/050
- SECTION=water/620

## Registry keys

- KEY=zhouli-suiren-wikisource
- KEY=hattori-site-yayoiken
- KEY=sena-site-shizuoka
- KEY=kotobank-minakuchi-matsuri
- KEY=kotobank-azebiki
- KEY=minumadai-jawiki
- KEY=akiba-1948-kangai
- KEY=kosaka-2014-tamagawa-bunsui
- KEY=suido-ishizue-yayoi-suiden
- KEY=kaogongji-wikisource (existing; its Used for gains the channel ladder)
- KEY=ishizue-jugo-yosui (existing; its Used for gains the 1537 width as a canal-tier figure)

## Outcomes

M28 MIXED - the ladder's built rungs all have a figure from before modern times: the field ditch in the Kaogongji's one-chi quan and a one-village Edo intake of 7 sun square (Tamagawa branches, Josuiki), the lateral in the Hattori site's 0.5-1 m drain and 1.4-2 m canal and a 14-village Edo intake of 3 shaku, the main canal between the Juugo canal's regulated 6 shaku 1 sun (1537) and the Minuma canal's 6 ken (1727); the two modern design documents stay only as corroboration (0068 table, the new water/620); the brook and town-river rows are natural watercourses with no premodern width found and stay estimates - nothing for the generator to stop drawing: the ladder, Stream and IrrigationDitch widths, moat.py and water.py stand as drawn - searched 2026-09-28: 村明細帳 川幅 間 用水 堰, 村明細帳 用水路 幅 尺 江戸時代 堀 間, 江戸時代 用水 小堀 幅 尺 田 水路 村 普請, 見沼代用水 幅 間 開削当時 (Japanese); 清代 宁夏 唐徕渠 渠口 阔 丈 支渠 陡口 毛渠 府志, 考工记 匠人 畎 遂 沟 洫 浍, 周礼 遂人 (Chinese); web search, Kotobank, ja.wikipedia, zh.wikisource, Suido no Ishizue, Gifu prefectural archives - GM ruling: the stroke convention and ordering (2026-07-21) is the GM's, not a ruling on the widths' sources; not knowingly modern.

M29 MIXED - the finite ladder whose last rung is a channel of its own width is classical (the Kaogongji's five channels, the Suiren's path on each), and the hand-off from that channel through an opening in the bund and on from plot to plot is attested (water openings in the Hattori site's bunds; Akiba dating "a proper arrangement of paddy plots and irrigation channels" to the 1910 law, flow-through irrigation before it); the modern-only parts, the terminal channel "sized to peak demand" and its bed set -5 to +10 cm against the paddy, were justifications, not drawn forms, and are removed from 0055 - no change to the maps: the delivery ditch keeps its blunt end at the lateral tier; the modern part (a ditch to every plot) is already water/610's finding - searched as M28, plus 田越し灌漑 近世 江戸時代 一般的, 田越灌漑 近世 用排兼用 耕地整理以前, 百姓伝記 水口 田 畔 用水 溝 (Japanese) - GM ruling: the question is the GM's (2026-08-17); keeping the floor was the record's decision, not knowingly on modern sources.

M30 MIXED - the head race's 6.0 ft (~1.8 m) matches the Hattori canal (1.4-2 m) and the 1537 Juugo width (~1.85 m); the canal and delivery strokes (4.5 down to 1.2 ft) sit between that and the finest rungs; the drain passes through the Hattori drain's 0.5-1 m (1.6-3.3 ft) on its way from 1.2 ft to a 5.5 ft outfall, and the outfall is wider than any premodern drain read, resting on the hydrology and on the measurement on Inashiro (water/050) - no stroke need change; the one width without a period figure is the drain outfall (DrainageDitch, 5.5 ft): if the GM wants it held to a read figure it would be about 3 ft, but the record already measured that raising or lowering it moves the cluster against the 60 ft bar, so this is the GM's call, not the orchestrator's - searched as M28 - GM ruling: true size (2026-08-17), with the measurement in hand; not knowingly on modern sources.

M31 MIXED - the continuous bund along the channel is attested (the Hattori canal "enclosed by large bunds", the Sena channel banks and large bunds reinforced together in the Late Yayoi-Kofun, the Suiren's path on each channel), as is the opening (the rite at a paddy's inlet in a poem of about 1134; the excavated intakes and outlets); the dividing bund of ~1.5 ft is attested (the Edo survey's one-shaku bund, Tokugawa Kinreiko 1726; Hattori small bunds 20-60 cm); the mizuguchi's 50 cm, sill and outlet levels are modern-only and moot, since the opening is not drawn; the bund along a canal, at the one site measured, is a LARGE bund, 80-150 cm - water/040 now carries a spec: a bund along the head race or a canal drawn about 3 ft, between plots or along a delivery ditch about 1.5 ft (the Bund kind; `fields.py`'s aze_w should cite kotobank-azebiki and hattori-site-yayoiken rather than aze-standard, which is now corroboration only) - searched 2026-09-28: 近世 水田跡 発掘 水路 幅 畦畔 幅 cm 江戸時代 遺跡, 畦際引 検地 畦 一尺 江戸, 地方凡例録 用水 堀 幅 井路 普請, 弥生 水田 水路 幅 畦畔 幅 登呂 大畦畔 小畦畔, 水口祭 苗代 水口 江戸時代 (Japanese); web search, Kotobank, ja.wikipedia, Suido no Ishizue, the Hattori and Sena site pages; no width found for an Edo bund along a canal - GM ruling: the non-render of the mizuguchi and the continuous bund were the record's decision on the GM's question of 2026-08-17; the 1.5 ft width was not ruled on by the GM.

## Left open, and why

- 0068 was treated as NOT held: `git log origin/main..HEAD` in the 269 clone lists it only for a merge-from-main commit, and `git diff origin/main HEAD` shows no change to it; 269's claim does not list 010 among its edits. None of 030, 040, 050 showed any 269 commit.
- The Hattori site's jawiki summary (小区画水田) is 269's key `shokukaku-suiden-jawiki`, not landed; it was read but not cited here, to avoid a colliding registry file. 269's 0014 (Inazato, 1869, bunds 2 shaku) postdates 1868 and was not used.
- Two repeats of `ishizue-jugo-yosui` on the water page are numbered -3 (010) and -4 (050) so that 0062's -1 and -2 did not need renumbering.
- The Tamagawa, Sena and Akiba PDFs were read from their own text layers, extracted with pdftotext and added to the check directory (/tmp/l7r-check/280-w1-pages); Akiba's scan interleaves two columns.
- Unfetchable in this session: chinawater.com.cn (the Qing Huinong canal's 13 zhang mouth, a candidate for a Chinese main-canal figure) and gushicimingju (a Suiren transcription; zh.wikisource used instead).
