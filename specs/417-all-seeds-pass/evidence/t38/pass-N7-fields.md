I ruled all 112 numbers. Three of them conflict with the record: the dry-row angle, the ripe-plot share, and a research claim that cites a figure its page doesn't give. About a third of the numbers are in code that nothing runs.

**Code that nothing runs.** I searched the whole clone for callers:
- `water_field` has none; only docstrings and the feature-112 split script name it. `_rows`, `_taxfree_plots`, `_wf_feed` and `_wf_main_drain` are reached only through it.
- `apply_land_use` is called once, at `hamletgen/water/polder.py:272`. That call always passes `mulberry_fishpond`, `eligible="all"` and `fraction=1.0` or `0.9`.
  - So the `land_use_overlay` knob is never read.
  - The lotus branch, `_landuse_tea_fringe` and the clustered branch of `_pick_overlay_plots` never run, and the 0.55 default is never used.
- In `_comb_source_channel`, `din` (built from 70, 12 and 14) and the 20 px bow only feed the first `_ch_poly`. Both branches overwrite that afterwards (feature 294 B1), so the four numbers reach neither ink nor record.

## Sources that bear

**Record pages** (all under /diagram/research/questions/):
- **0284 drawing:**
  - 「A junction's pile of earth is drawn four to six feet across, a GUESS… never thinner than the map's line so it never vanishes」
  - 「Each basin corner meeting at a crossing gets its own fillet of earth… and roughly a quarter are left bare」
- **0068 drawing:** 「The drawn drain passes through that width on its way from a 1.2 ft head to a 5.5 ft outfall」
- **0009 drawing:** 「on some maps about one rice plot in sixteen is drawn still flooded and one in twenty gold, ripening early」
  - Its own comment says paddy.py rolls the ripe shades "about 5%". The code rolls `ro > 0.975`, which is 2.5%: a mismatch.
- **0005 drawing:**
  - 「The scatter is a sample of the planting, not each plant」
  - Its evidence tag reads: convention (the shoot mottle as a sample) … guess (… nine plots a household)
- **0006 drawing:** 「Every dry plot is drawn with furrows, and which way they run is set tract by tract」
  - It gives no dry-grain/soy share. The "62"/"620" hits on the page are feature numbers, so `water_field`'s claim citing 0006 for "62% dry grain" is a mis-cite.
- **0026 drawing:** its Grounds comment reads 「tea two clipped rows at t 0.32 and 0.70, runs of 7.5 ft broken by 5 ft」, and its evidence tag lists 「guess (… the tea hedge's width and runs …)」.
- **0013 drawing:** evidence tag 「guess (… that they favor the far end of the water's run)」
- **0020 drawing:**
  - 「Converted plots are set in patches rather than scattered evenly - a GUESS」
  - 「A share well short of everything is what the history shows」 (no 0.55 is given)
- **0014 drawing:** 「a dividing bund… about 1.5 ft wide, between the one and two shaku the old records give… a walking bund… 2 to 5 ft, a GUESS」

**Grave-marker search (the one search pass).** It covers the stone heights and widths at lines 498, 537 and 539.

1. **明史 卷60 禮十四** (archived copy `29/29b7523ed213`, zh.wikisource 明史/卷60). The rules date from 1370-1372; the history was compiled in 1739.
   - 「其制自洪武三年定。五品以上用碑，龜趺螭首。六品以下用碣，方趺圓首。」 (translation) "The rule was fixed in Hongwu 3 (1370): officials of the fifth rank and above have a stele with a tortoise base and dragon head; the sixth rank and below have a *jie*, with a square base and round head."
   - 「碑身遞殺五寸，至五尺五寸止。其廣遞殺二寸，至二尺二寸止。」 (translation) "The stele body shrinks by 5 cun a grade and stops at 5 chi 5 cun; its breadth shrinks by 2 cun and stops at 2 chi 2 cun." A Ming chi is about 32 cm, so that is about 5.8 ft tall and 2.3 ft wide.
   - For commoners (1372): 「志石二片，如官之儀。塋地圍十八步。」 (translation) "Two epitaph stones, as in the officials' rite. Grave ground 18 bu round." These epitaph stones are buried tablets; no standing stele is prescribed.
2. **kotobank 墓** (世界大百科事典, 西脇常記; archived copy `be/be5bc402dadf`). The evidence describes the Tang.
   - 「七品以上は飾りのない石碑高さ4尺とされた」 (translation) "Officials of the seventh rank and above were allowed a plain stone stele 4 chi high" (about 3.9 ft).

**Reading: ATTESTED ONLY FOR ranked officials.** The codes cap officials' steles: the lowest Ming body is about 5.8 ft by 2.3 ft, and Tang rank seven is 4 chi. The 1372 commoner rule names only buried epitaph stones. So the island's 8 ft stone stands taller than the lowest official's stele, on a commoner's grave the code gave no standing stone at all. That is not an explicit ban, so I don't call it CONTRADICTED.

For Japan the search is **SILENT**:
- The archived Tanigawa 2018 Waseda page (`99/99945fd75590`) says only that markers grew larger from the Kyōhō era (1716-1735) on, with no figures.
- Queries run: 近世墓標 農村 高さ cm; 近世墓標 総高 角柱形 舟形; 江戸時代 農民 墓石 高さ 尺 触書.
- The Rekihaku PDF (kenkyuhokoku_111_10) is a scanned JBIG2 file with no text layer; I recorded it as unreadable on the ledger.

**Other searches this pass, all SILENT:**
- **Mulberry rows' place across the bank:** 桑基鱼塘 基面 种桑 行距 returned nothing on spacing or setback.
- **Dry grain against soy share:** 江戸 村 畑 作付 大豆 麦 粟 割合 村明細帳 found that village registers record whether crops were grown, not their shares.
- **Lotus bloom size:** I read the Flora of China text at naturelib.net (flowers 10-23 cm, leaves 25-90 cm). The blooms are a symbol on a path nothing runs, so I recorded the page as `rejected:`. The Flora of China PDF itself is recorded as unreadable.

## One row per number

In the last column, (uncalled) marks numbers in code nothing runs, as listed at the top. "P2b" means the T29/T36 pass at `/diagram/.clones/diagram-backlog/specs/417-all-seeds-pass/evidence/t29/pass-P2b-fields.md`.

| file::unit | line | value | ruling | what the number does |
|---|---|---|---|---|
| comb.py::bund_junctions | 220 | 0.75 | NONE | node-merge tolerance |
| comb.py::bund_junctions | 231 | 16 | NONE | hex base of the seed hash |
| comb.py::bund_junctions | 232 | 1.1 | CITED 0284 drawing (rule: "never thinner than the map's line") | pile floored just above the drawn bund width |
| comb.py::bund_junctions | 240 | 0.25 | CITED 0284 drawing ("roughly a quarter are left bare") | share of crossing corners left unpiled |
| comb.py::bund_junctions | 251 | 0.25 | NONE | Bézier sample point |
| comb.py::bund_junctions | 251 | 0.75 | NONE | Bézier sample point |
| comb.py::_comb_draw_ditches | 676 | 5.5 | CITED 0068 drawing ("1.2 ft head to a 5.5 ft outfall") | fallback outfall width |
| comb.py::_comb_record_field | 725 | 30 | NONE | manifest band for recording plots near the drain |
| comb.py::_comb_record_ditches | 797 | 0.05 | NONE | duplicate-point tolerance |
| comb.py::_comb_source_channel | 822 | 70 | NONE (overwritten, reaches no ink or record) | step from the fork into the crop |
| comb.py::_comb_source_channel | 842 | 12 | NONE (overwritten) | clearance test for the pulled end |
| comb.py::_comb_source_channel | 862 | 14 | NONE (overwritten) | pull off the edge |
| comb.py::_comb_source_channel | 892 | 20 | NONE (overwritten) | bow off the chord |
| features.py::grave_form | 37 | 4.29497e9 | NONE | 32-bit seed mask |
| features.py::turning_corners | 40 | 45 | NOT-ABOUT-THE-WORLD | turn that counts as a real corner |
| features.py::carve_around_grave | 125 | 0.2 | NONE | cut tolerance |
| features.py::_mound_meets_pond | 191 | 16 | NONE | ring sampling |
| features.py::_mound_meets_pond | 191 | 32 | NONE | ring sampling |
| features.py::pond | 236 | 12 | CONVENTION (the "pond glyph" claim) | inner sheen inset |
| features.py::_paddy_features | 285 | 39633 | NONE | substream salt 0x9AD1 |
| features.py::_paddy_features | 285 | 4.29497e9 | NONE | seed mask |
| features.py::_plot_pond | 392 | 1.5 | CONVENTION | half-length of a reed mark |
| features.py::_plot_pond | 393 | 8 | CONVENTION | count of reed marks |
| features.py::_pond_fit | 424 | 12 | NONE | rim sampling |
| features.py::_pond_fit | 424 | 24 | NONE | rim sampling |
| features.py::_plot_rock | 455 | 5 | SEARCHED-SILENT P2b (outcrop size) | boulder scatter, y |
| features.py::_plot_rock | 455 | 7 | SEARCHED-SILENT P2b (outcrop size) | boulder scatter, x |
| features.py::_plot_rock | 458 | 0.1 | CONVENTION | lit-crown highlight path |
| features.py::_plot_rock | 458 | 0.2 | CONVENTION | lit-crown highlight path |
| features.py::_plot_rock | 458 | 0.4 | CONVENTION | lit-crown highlight path |
| features.py::_plot_corner_grave | 487 | 6.5 | GUESS (unit's claim; P2b searched silent, the Ming 18 bu ceiling) | corner mound's half-length, the carve disc |
| features.py::_plot_corner_grave | 498 | 1.6 | NOT-ABOUT-THE-WORLD (as P2b's stone offset) | second stone's offset across |
| features.py::_plot_corner_grave | 498 | 2.2 | NOT-ABOUT-THE-WORLD | first stone's offset / second's base step |
| features.py::_plot_corner_grave | 498 | 3.5 | ATTESTED ONLY FOR officials (明史 卷60); SILENT for a commoner (this pass) | second stone's height |
| features.py::_plot_corner_grave | 498 | 6.5 | ATTESTED ONLY FOR officials (明史 卷60); SILENT for a commoner | first stone's height |
| features.py::_plot_grave_island | 521 | 6 | GUESS (unit's claim "at least 18 x 12"; P2b) | least mound half-height |
| features.py::_plot_grave_island | 521 | 9 | GUESS (unit's claim; P2b) | least mound half-width |
| features.py::_plot_grave_island | 537 | 5 | ATTESTED ONLY FOR officials (明史 卷60); SILENT for a commoner | second stone's height |
| features.py::_plot_grave_island | 537 | 6.5 | as above | third stone's height |
| features.py::_plot_grave_island | 537 | 8 | as above; taller than the lowest Ming official's stele body (5.5 chi, about 5.8 ft) | first stone's height |
| features.py::_plot_grave_island | 539 | 1.3 | ATTESTED ONLY FOR officials (stele 2.2 chi wide at the least); SILENT for a commoner | stone half-width (2.6 wide) |
| features.py::_rounded_pond | 559 | 0.4 | NONE | scale floor |
| features.py::_rounded_pond | 565 | 0.45 | NONE | fillet cap as a share of the edge |
| features.py::_rounded_pond | 579 | 0.25 | NONE | quadratic midpoint sample |
| landuse.py::mulberry_row_ts | 86 | 0.08 | SEARCHED-SILENT (this pass) | rows held off the water and bank edges |
| landuse.py::mulberry_row_ts | 86 | 0.84 | SEARCHED-SILENT (this pass) | span of the band the rows fill |
| landuse.py::apply_land_use | 156 | 0.55 | default never used; 0020 drawing gives the rule ("a share well short of everything") but no 0.55 | converted share of eligible plots |
| landuse.py::_landuse_tea_fringe | 358 | 6 | UNRESEARCHED (uncalled); the rows it starts are CONTRADICTED by Fortune 1843 (P2b) | first tea row's set-in from the plot edge |
| landuse.py::_landuse_repaint_leftovers | 379 | 13 | NONE | seed multiplier |
| landuse.py::_landuse_repaint_leftovers | 379 | 7 | NONE | seed multiplier |
| landuse.py::_landuse_repaint_leftovers | 391 | 12 | GUESS P2b ("corners eased") | leftover waterline fillet reach |
| landuse.py::_landuse_repaint_leftovers | 391 | 2.5 | GUESS 0014 drawing (wider than a 1-2 shaku dividing bund, inside the guessed 2-5 ft walking bund) | water set in from the bund |
| landuse.py::_landuse_repaint_leftovers | 395 | 4.5 | CONVENTION, 0005 drawing (mottle as a sample; names pitch=4.5) | shoot pitch, flooded leftover |
| landuse.py::_landuse_repaint_leftovers | 399 | 4.5 | CONVENTION, 0005 drawing | shoot pitch, dry leftover |
| landuse.py::_landuse_draw_plot | 445 | 2.5 | NONE | cover grown to erase the base stroke |
| landuse.py::_landuse_draw_plot | 469 | 0.7 | NONE | dig-back scale floor |
| landuse.py::_landuse_draw_plot | 471 | 8 | GUESS P2b ("corners eased") | bank corner fillet reach |
| landuse.py::_landuse_draw_plot | 472 | 16 | GUESS P2b ("corners eased") | water corner fillet reach |
| landuse.py::_landuse_draw_plot | 501 | 14 | CONVENTION (uncalled lotus path) | bloom scatter |
| landuse.py::_landuse_draw_plot | 501 | 2.5 | CONVENTION (uncalled; real flowers 10-23 cm per Flora of China, so not true scale) | least bloom radius |
| landuse.py::_mulberry_rows | 532 | 0.4 | NONE | scale floor |
| landuse.py::_mulberry_rows | 548 | 20 | NONE | channel-index bbox pad |
| landuse.py::_mulberry_rows | 549 | 20 | NONE | channel-index bbox pad |
| landuse.py::_mulberry_rows | 553 | 1e9 | NONE | sentinel |
| landuse.py::_mulberry_rows | 563 | 6 | CONVENTION (the "bank mottle" claim) | mottle ry max |
| landuse.py::_mulberry_rows | 563 | 8 | CONVENTION | mottle rx max |
| landuse.py::_mulberry_rows | 573 | 1.3 | NOT-ABOUT-THE-WORLD | mulberry crown jitter |
| landuse.py::_mulberry_rows | 583 | 0.32 | GUESS 0026 drawing | inner tea hedge's place across the band |
| landuse.py::_mulberry_rows | 583 | 0.7 | GUESS 0026 drawing | outer tea hedge's place across the band |
| landuse.py::_mulberry_rows | 584 | 2.5 | GUESS 0026 drawing (7.5 ft runs, 5 ft gaps) | tea hedge walk step |
| landuse.py::_pick_overlay_plots | 624 | 9 | GUESS 0005 / 0020 drawing (uncalled clustered path) | one seed plot per nine converted |
| outfall.py::outfall_run | 37 | 520 | NONE | reach that carries the run off the sheet |
| outfall.py::outfall_run | 37 | 70 | NOT-ABOUT-THE-WORLD | straight lead before the curve |
| paddy.py::rest_plots | 134 | 0.05 | GUESS 0013 drawing (far-end weighting a guess) | least weight at the near end |
| paddy.py::_taxfree_plots | 155 | 40 | NOT-ABOUT-THE-WORLD (uncalled) | sort bin for spreading |
| paddy.py::_paddy_surface | 163 | 22 | CONVENTION, 0005 drawing | shoot-dot cap |
| paddy.py::_paddy_surface | 189 | 80 | CONVENTION, 0005 drawing | px² per shoot dot |
| paddy.py::_paddy_surface | 198 | 0.1 | CONVENTION, 0005 drawing | grid dropout |
| paddy.py::_rows | 218 | 0.6 | CONTRADICTED 0006 drawing (rows set tract by tract) (uncalled) | random row angle per plot, ±34° |
| paddy.py::_rows | 225 | 0.85 | CONVENTION (uncalled) | row opacity |
| paddy.py::rest_basin | 267 | 13 | NONE | seed multiplier |
| paddy.py::rest_basin | 267 | 7 | NONE | seed multiplier |
| paddy.py::rest_basin | 270 | 900 | CONVENTION | tufts per px² (decoration) |
| paddy.py::water_field | 279 | 52 | GUESS (unit's claim; P2b) (uncalled) | outline wobble |
| paddy.py::water_field | 325 | 13 | NONE | seed multiplier |
| paddy.py::water_field | 325 | 7 | NONE | seed multiplier |
| paddy.py::water_field | 333 | 0.55 | NOT-ABOUT-THE-WORLD (uncalled) | last-column threshold |
| paddy.py::water_field | 336 | 6.28 | NONE | 2π |
| paddy.py::water_field | 341 | 1.7 | NONE | phase decorrelation |
| paddy.py::water_field | 355 | 0.6 | NOT-ABOUT-THE-WORLD (uncalled) | last-row threshold |
| paddy.py::water_field | 367 | 0.08 | SEARCHED-SILENT P2b (田越し 何枚) (uncalled); 0006 is silent on margins | edge-dryness jitter |
| paddy.py::water_field | 367 | 0.6 | SEARCHED-SILENT P2b (uncalled) | how near the edge a plot goes dry |
| paddy.py::water_field | 368 | 0.62 | SEARCHED-SILENT (this pass) (uncalled); the claim mis-cites 0006 | dry grain vs soy share |
| paddy.py::water_field | 376 | 0.3 | CITED 0009 drawing (one in sixteen still flooded overall) (uncalled) | flooded share near the ditches |
| paddy.py::water_field | 378 | 0.975 | CITED 0009 drawing, MISMATCH: page says one in twenty, code rolls 1 in 40 (uncalled) | ripe share |
| paddy.py::water_field | 412 | 14 | NOT-ABOUT-THE-WORLD (uncalled) | lateral sampling step |
| paddy.py::_wf_feed | 439 | 14 | GUESS P2b ("feed and outfall's seat") (uncalled) | fallback interior clearance |
| paddy.py::_wf_main_drain | 472 | 11 | NOT-ABOUT-THE-WORLD (uncalled) | sampling step |
| paddy.py::_wf_main_drain | 476 | 6 | NOT-ABOUT-THE-WORLD (uncalled) | boundary scan step |
| paddy.py::_wf_main_drain | 477 | 1.4 | GUESS P2b ("canals set in from the edges", twice the 0.7 inset) (uncalled) | depth a field needs to carry a main and a drain |

## Leads not followed
- The 木津惣墓 marker survey (about 3,300 Edo markers) and prefectural excavation reports' 墓標計測表: measured heights of commoners' markers.
- 明會典 / 大清會典 on commoners' surface markers; the stele table (表2) in kotobank's 墓 article, which is an image.
- Fortune 1843: whether tea rows ran to a plot's edge (only matters if the tea fringe is wired up).
- 『広東新語』 / 順徳 gazetteers: where mulberry stood across a dike.
- If tea fringe and lotus stay uncalled, the parent could rule them dead and retire them rather than research them.

Sources:
- [明史/卷60 (zh.wikisource)](https://zh.wikisource.org/wiki/明史/卷60)
- [kotobank 墓](https://kotobank.jp/word/%E5%A2%93-599723)
- [Waseda Weekly, Tanigawa 2018](https://www.waseda.jp/inst/weekly/academics/2018/06/29/40014/)
- [naturelib.net, Nelumbo nucifera (Flora of China text)](https://naturelib.net/plantae/nelumbo-nucifera/)
- [Flora of China Nelumbonaceae PDF (unreadable)](https://www.iplant.cn/foc/pdf/Nelumbonaceae.pdf)
- [Rekihaku kenkyuhokoku 111-10 (unreadable)](https://rekihaku.repo.nii.ac.jp/record/1221/files/kenkyuhokoku_111_10.pdf)
- [Search lead: hirosaki repo, 近世墓石](https://hirosaki.repo.nii.ac.jp/record/6083/files/JinbunShakaikagakuRonso9_1.pdf)
- [Search lead: 宮本, 村明細帳](https://hosei.ecats-library.jp/da/repository/00001960/73-4miyamoto.pdf)
- [Search lead: 基塘农业 (douban)](https://douban.com/note/854307225)