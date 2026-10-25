I ruled all 124 numbers. Only one world question was left unresearched: how thickly the scrub pines stand (`commons` 557, the 6000). I searched it and found nothing (SILENT). Everything else is settled by the record, by the units' own claims or by earlier passes (T29 P7, T38 N2 and N9). Nothing was edited, and I fetched no web page, so the sources-consulted ledger has no new rows.

## Sources that bear on these numbers

**Record pages** (`/diagram/.clones/diagram-backlog/research/questions/`):
- **0027-polder-dikes…drawing.html**
  - 「The willow row stands about three quarters of the way out from the field side, toward the water, and the mulberry row about a quarter of the way, on the field side. So the distance between the rows follows the width of the bank, and the maps draw to no figure for it.」 This covers 0.74 and 0.26, and means the page gives no figure for a tree's wobble in its row.
  - 「…is drawn thicker in some stretches and pinched in others, and mottled with patches of earth of different ages, as repairs are.」 This is the rule `dike_band`'s three sines carry out; the amplitudes are ours.
- **0078-grass-hills…drawing.html**: 「open hill ground of coarse grass, low brush and a few scraggly pines」; 「open grass, or grass with thin low pine」; 「Drawn open and sparse」. The page gives the rule but no density.
  - Its quoted biodic source (archived PDF, Edo period): 「その形態は、草原であるものや、樹高３～４ｍまでの松を中心とした疎林であるものなど、多様であった」 (translation: "its form varied, some grassland, some sparse woodland chiefly of pine up to 3-4 m tall").
  - It also says 「The grass and the brush are one small block of tufts and dots repeated across the ground … the way a map's legend shows a kind of ground」. This, with tiles.py's own claim 「cover tiles - CONVENTION」, is why every tile number is CONVENTION.
- **0073-scrub…drawing.html**: 「The scraggly pines and the woodland trees stand back from the margin by as far as their drawn crowns spread, so nothing leans over a crop.」 The 14 bs reach comes from this.
- **0074-reed-beds…drawing.html**: 「Where a stream or a ditch crosses the marsh, or a drain runs along a paddy's foot, the reeds are drawn right to the water's edge.」 and 「That reeds stand at the water is the record's own finding for a reservoir's shore.」 This covers the 1.5 at the pond rim.
- **0137-domain-capitals…drawing.html**: 「the streets … roads 30 ft , the ring road 20 ft … the Tokaido's 5 ken (~30 ft)」.
- **0081-village-lanes.drawing.html**: 「a footpath is drawn 3 ft wide, the cluster's spine and its spur to the fields 5 ft, and the track out to the wider world 6 ft.」
- **0151-city-moats…drawing.html**: 「A Japanese town that encloses itself draws a moat about 33 ft wide.」; 「A Ming treatise sets every city moat a smallest width of about 35 ft」; 「A provincial seat's moat is drawn 66 ft across」. None of these is 22.
- **Earlier passes**:
  - `/diagram/.clones/diagram-backlog/specs/417-all-seeds-pass/evidence/t29/pass-P7-other.md`: pine height and reach SEARCHED-SILENT; "spacing along the crest" ruled NOT-ABOUT-THE-WORLD.
  - `/diagram/.clones/diagram-backlog/specs/417-all-seeds-pass/evidence/t38/pass-N9-homestead-parts.md`: 「No production code sets `road_width`, `moat_width` or `ring_road_width`」, so it ruled those fallbacks NONE.

**This pass's search: how thickly scrub pines stood on a grass hill (`commons` 6000)**
- **SILENT.** Nothing found gives a count or spacing of pines on an Edo grass hill or a Qing denuded hill.
- Archive terms: 草山, 柴山, 疎林, アカマツ 疎, 松 まばら, pine density, scattered pine, grass hill. The only bearing hit is the biodic PDF above, which gives a height (3-4 m) but no density. The other 疎林 hits are about a shrine precinct (Sano), the Musashino moor and a modern terrain-visibility test.
- Web queries, none of which named a page worth reading, so none was fetched:
  - 江戸時代 草山 松 疎林 本数 反当たり 柴山 景観. Results: [biodic](https://www.biodic.go.jp/cbd/2006/pdf/1102_2_12.pdf), [Kyoto pref.](https://www.pref.kyoto.jp/kankyo_red/2026/static/04_ecosystem/02_human-environment/02_article.html), [chikyu repo](https://chikyu.repo.nii.ac.jp/record/2030/files/Jizoku2005_Redacted_13.pdf). The search summary mentions an 1811 Amagi 御林 survey with tree counts per 字 (subdivision of a village), but no per-area figure.
  - 明治 初期 林相 赤松 疎林 一町歩 何本 柴山 草山 調査. Results: [Kyoto pref. 03](https://www.pref.kyoto.jp/kankyo_red/2026/static/04_ecosystem/02_human-environment/03_article.html), [Shiga pref.](https://www.pref.shiga.lg.jp/file/attachment/5109009.pdf).
  - 清代 南方 荒山 童山 疏林 马尾松 稀疏 村落 后山 樵采 植被 景观. Results were modern ecology only, e.g. [plant-ecology 1986](https://www.plant-ecology.com/CN/Y1986/V10/I4/294).

## Flags
- **`cover.py:395` overclaims.** It reads 「scrub pines - 0078.drawing: … one throw to 6,000 sq ft」, but 0078 gives only "a few scraggly pines". The 6,000 is ours, and is now SEARCHED-SILENT.
- **`wet.py::trim_off_marsh` cites 0057.drawing for 「a way's ends walked back off the reeds」.** No sentence in 0057's drawing, notes or findings says this; the rule rests on the GM's 2026-08-12 ruling in the docstring. I ruled the 6 a tolerance on the reeds' feathered drawn edge (`MARSH_FEATHER_BS` 46), not a world distance.
- **`cover.py:810` fallback 40×30 never fires.** Houses, gardens, yards and groves all carry `w`/`h`. It also disagrees with 0029's 46×28.
- **`registry.py:130` fallbacks** never fire in production (N9), but the legacy hand-authored pool carries these keys, so an old map missing one would reach them.
  - Road 30 and ring road 20 match 0137; lane 6 matches 0081.
  - The moat's 22 matches nothing in 0151 (33, 35, 66).
  - The same fallbacks disagree across files: road 26 in `captions.py` and `ground.py`; ring road 8 in `_knobs.py`; moat 26 in `_knobs.py:630`.
- **`dike_top_houses` "spacing along the crest" is claimed as GUESS, but T29 P7 ruled it NOT-ABOUT-THE-WORLD.** The two should be reconciled.

## One row per number

| file::unit | line | value | ruling | what the number does |
|---|---|---|---|---|
| cover.py::farmstead_keepouts | 71 | 45 | NOT-ABOUT-THE-WORLD | angle step growing each point by the margin (octagon) |
| cover.py::_commons_keep | 329 | 14 | SEARCHED-SILENT (T29 P7, pine height; the stand-back rule is CITED 0073.drawing) | crop keep-out prefilter reach, the tallest pine's tip |
| cover.py::commons | 557 | 6000 | SEARCHED-SILENT (this pass; rule CITED 0078.drawing "a few scraggly pines"; docstring overclaims) | one pine throw per 6,000 sq ft |
| cover.py::commons | 570 | 1.1 | CONVENTION | pine trunk stroke width |
| cover.py::commons | 573 | 0.25 | CONVENTION | pine glyph branch spacing up the trunk |
| cover.py::commons | 573 | 0.45 | CONVENTION | pine glyph first branch height |
| cover.py::commons | 573 | 3.6 | CONVENTION | pine glyph branch length |
| cover.py::_stock_woodland | 686 | 6 | NOT-ABOUT-THE-WORLD | throw cap, six times the crown target |
| cover.py::hinterland | 810 | 30 | NONE (fallback never fires; see flags) | fallback footprint height |
| cover.py::hinterland | 810 | 40 | NONE (fallback never fires; see flags) | fallback footprint width |
| cover.py::hinterland | 815 | 120 | CONVENTION | scrub band bleed past the canvas edge |
| dikes.py::dike_band | 93 | 34 | NOT-ABOUT-THE-WORLD | densifying step along the dike's inner face |
| dikes.py::dike_band | 112 | 0.16 | CITED 0027.drawing (rule; the amplitude NOT-ABOUT-THE-WORLD) | fine width-wave amplitude |
| dikes.py::dike_band | 112 | 0.22 | CITED 0027.drawing (rule; amplitude ours) | middle width-wave amplitude |
| dikes.py::dike_band | 112 | 0.26 | CITED 0027.drawing (rule; amplitude ours) | broad width-wave amplitude |
| dikes.py::dike_band | 112 | 5 | CITED 0027.drawing (rule; harmonic ours) | fine wave's harmonic |
| dikes.py::perimeter_dike | 253 | 29 | NONE | seed salt (0x1D) |
| dikes.py::perimeter_dike | 255 | 0.7 | CONVENTION (claimed "earth mottle - CONVENTION") | mottle throw count per px of bbox |
| dikes.py::perimeter_dike | 260 | 13 | CONVENTION | mottle ellipse max rx |
| dikes.py::perimeter_dike | 260 | 9 | CONVENTION | mottle ellipse max ry |
| dikes.py::perimeter_dike | 289 | 0.74 | CITED 0027.drawing ("about three quarters of the way out … toward the water") | willow row's place across the band |
| dikes.py::perimeter_dike | 291 | 1.4 | CONVENTION (wobble under a crown radius; 0027 "draw[s] to no figure") | willow wander off its row line |
| dikes.py::perimeter_dike | 294 | 0.26 | CITED 0027.drawing ("about a quarter of the way, on the field side") | mulberry row's place across the band |
| dikes.py::perimeter_dike | 296 | 1.2 | CONVENTION (as 291) | mulberry wander off its row line |
| dikes.py::perimeter_dike | 335 | 1000 | CONVENTION | label siting score: prefer the north side |
| dikes.py::perimeter_dike | 335 | 200 | CONVENTION | label siting penalty on the village's side |
| dikes.py::dike_gates | 366 | 1e9 | NONE | sentinel distance |
| dikes.py::dike_top_houses | 441 | 3358 | NONE | seed salt (0xD1E) |
| dikes.py::dike_top_houses | 445 | 0.18 | GUESS (unit's claim "spacing along the crest", T36 P7; T29 P7 ruled NOT-ABOUT-THE-WORLD) | house seat jitter along the crest |
| dikes.py::dike_top_houses | 456 | 0.28 | CONVENTION | platform mottle spread (height) |
| dikes.py::dike_top_houses | 456 | 0.32 | CONVENTION | platform mottle spread (width) |
| dikes.py::dike_top_houses | 458 | 5 | CONVENTION | platform mottle ry max / rx min |
| dikes.py::dike_top_houses | 458 | 8 | CONVENTION | platform mottle rx max |
| outline.py::natural_outline | 70 | 5 | NOT-ABOUT-THE-WORLD | smallest rounding radius the search tries |
| outline.py::natural_outline | 71 | 8 | NOT-ABOUT-THE-WORLD | buffer curve resolution |
| outline.py::natural_outline | 79 | 12 | NOT-ABOUT-THE-WORLD | fewest wave sample points |
| tiles.py::grass_tile | 90 | 1.5 | CONVENTION (tiles claim; 0078 "the way a map's legend shows") | brush dot min radius |
| tiles.py::grass_tile | 90 | 2.4 | CONVENTION | brush dot max radius |
| tiles.py::grass_tile | 91 | 0.45 | CONVENTION | blade lean |
| tiles.py::grass_tile | 91 | 2.4 | CONVENTION | blade min length |
| tiles.py::grass_tile | 91 | 4.2 | CONVENTION | blade max length |
| tiles.py::grass_tile | 105 | 4.2 | CONVENTION | blade reach for wrapping at the tile edge |
| tiles.py::reed_tile | 168 | 0.6 | CONVENTION | tint min radius share |
| tiles.py::reed_tile | 168 | 15 | CONVENTION | tint min radius cap |
| tiles.py::reed_tile | 173 | 1.2 | CONVENTION | glint min ry |
| tiles.py::reed_tile | 173 | 2.6 | CONVENTION | glint min rx |
| tiles.py::reed_tile | 173 | 4.6 | CONVENTION | glint max rx |
| tiles.py::reed_tile | 174 | 0.2 | CONVENTION | reed lean |
| tiles.py::reed_tile | 174 | 7 | CONVENTION | reed max length |
| tiles.py::reed_tile | 182 | 7 | CONVENTION | reed wrap reach |
| tiles.py::bamboo_tile | 217 | 0.6 | CONVENTION | culm mark x jitter |
| tiles.py::bamboo_tile | 218 | 0.6 | CONVENTION | culm mark y jitter |
| tiles.py::bamboo_tile | 220 | 11 | CONVENTION | bamboo mark wrap reach |
| tiles.py::reed_overlay_tile | 276 | 0.2 | CONVENTION | reed lean |
| tiles.py::reed_overlay_tile | 276 | 5 | CONVENTION | reed min length |
| tiles.py::reed_overlay_tile | 276 | 8 | CONVENTION | reed max length |
| tiles.py::reed_overlay_tile | 278 | 4.5 | CONVENTION | glint max ry |
| tiles.py::reed_overlay_tile | 278 | 6 | CONVENTION | glint min rx |
| tiles.py::reed_overlay_tile | 278 | 8 | CONVENTION | glint count |
| tiles.py::grass_overlay_tile | 295 | 0.45 | CONVENTION | blade lean |
| tiles.py::grass_overlay_tile | 295 | 2.8 | CONVENTION | blade min length |
| tiles.py::grass_overlay_tile | 295 | 4.6 | CONVENTION | blade max length |
| tiles.py::grass_overlay_tile | 297 | 1.8 | CONVENTION | dot min radius |
| tiles.py::grass_overlay_tile | 297 | 2.6 | CONVENTION | dot max radius |
| tiles.py::fringe_tile | 323 | 0.45 | CONVENTION | grass lean |
| tiles.py::fringe_tile | 323 | 2.4 | CONVENTION | grass min length |
| tiles.py::fringe_tile | 323 | 4.2 | CONVENTION | grass max length |
| tiles.py::fringe_tile | 324 | 0.2 | CONVENTION | reed lean |
| tiles.py::fringe_tile | 324 | 7 | CONVENTION | reed max length |
| tiles.py::fringe_tile | 326 | 18 | CONVENTION | tint max radius |
| tiles.py::reed_bank_tile | 352 | 0.2 | CONVENTION | reed lean |
| tiles.py::reed_bank_tile | 352 | 4.5 | CONVENTION | reed min length |
| tiles.py::reed_bank_tile | 352 | 7.5 | CONVENTION | reed max length |
| tiles.py::cover_rings | 387 | 0.25 | NONE | simplify tolerance |
| wet.py::pond_fringe_ring | 72 | 16 | NOT-ABOUT-THE-WORLD | ring vertex count |
| wet.py::_ellipse | 102 | 64 | NOT-ABOUT-THE-WORLD | pond polygon vertex count |
| wet.py::pond_cut | 219 | 25 | NONE | slack when matching the pond's own box |
| wet.py::ellipse_ring | 303 | 32 | NOT-ABOUT-THE-WORLD | ring vertex count |
| wet.py::marsh | 420 | 40 | NONE | prefilter reach for crests near the box |
| wet.py::marsh | 451 | 5 | NONE | keep-out grid slot id |
| wet.py::marsh | 452 | 6 | NONE | keep-out grid slot id |
| wet.py::marsh | 465 | 1.5 | CITED 0074.drawing ("reeds are drawn right to the water's edge"; 1.5 the drawn slack) | bare rim the reeds keep off the pond |
| wet.py::trim_off_marsh | 486 | 6 | NOT-ABOUT-THE-WORLD (tolerance on the feathered drawn edge; 0057 citation unsupported, see flags) | way end counts as soaked within 6 px |
| wet.py::trim_off_marsh | 515 | 30 | NOT-ABOUT-THE-WORLD | shortest leg before dropping it |
| wet.py::trim_off_marsh | 523 | 24 | NOT-ABOUT-THE-WORLD | walk-back step |
| wet.py::toe_band | 560 | 120 | CONVENTION | bleed past the canvas edge |
| wet.py::toe_band | 593 | 24 | NOT-ABOUT-THE-WORLD | cross-slope station step floor |
| wet.py::toe_band | 624 | 0.2 | NOT-ABOUT-THE-WORLD (flare GUESS already claimed) | flank sample station |
| wet.py::toe_band | 624 | 0.4 | NOT-ABOUT-THE-WORLD | flank sample station |
| wet.py::toe_band | 624 | 0.6 | NOT-ABOUT-THE-WORLD | flank sample station |
| wet.py::toe_band | 624 | 0.8 | NOT-ABOUT-THE-WORLD | flank sample station |
| wet.py::surface_water_dist | 660 | 1e9 | NONE | sentinel distance |
| hand_sheet.py::_path_points | 177 | 6 | NONE | SVG C-command argument count |
| hand_sheet.py::_path_points | 177 | 7 | NONE | SVG A-command argument count |
| hand_sheet.py::_text_shape | 304 | 12 | CONVENTION | default font size |
| hand_sheet.py::leader_to_ink | 450 | 1.5 | CONVENTION | leader already touching ink, left alone |
| hand_sheet.py::_luma | 626 | 16 | NONE | hex base |
| hand_sheet.py::_luma | 627 | 0.114 | NONE | Rec.601 luma weight (blue) |
| hand_sheet.py::_luma | 627 | 0.299 | NONE | Rec.601 luma weight (red) |
| hand_sheet.py::_luma | 627 | 0.587 | NONE | Rec.601 luma weight (green) |
| svg.py::leader_svg | 43 | 0.08 | CONVENTION | leader stroke as a share of font size |
| svg.py::leader_svg | 43 | 0.6 | CONVENTION | thinnest leader stroke |
| matrix.py::matrix_violations | 39 | 4000 | CONVENTION | default sheet width |
| matrix.py::matrix_violations | 40 | 4000 | CONVENTION | default sheet height |
| matrix.py::matrix_violations | 46 | 120 | NONE | spatial index cell |
| registry.py::element_extents | 97 | 2.5 | CONVENTION | ward fence line's drawn width |
| registry.py::element_extents | 125 | 8 | NONE (fallback never fires; every well carries r) | well radius fallback |
| registry.py::element_extents | 126 | 12 | NOT-ABOUT-THE-WORLD | well polygon vertex count |
| registry.py::element_extents | 126 | 6 | NOT-ABOUT-THE-WORLD | π/6 angle step |
| registry.py::element_extents | 128 | 16 | NOT-ABOUT-THE-WORLD | pond polygon vertex count |
| registry.py::element_extents | 128 | 8 | NOT-ABOUT-THE-WORLD | π/8 angle step |
| registry.py::element_extents | 130 | 20 | NONE (production never reaches it; = 0137.drawing ring road 20 ft) | ring road width fallback |
| registry.py::element_extents | 130 | 22 | NONE (production never reaches it; matches no 0151 width, see flags) | moat width fallback |
| registry.py::element_extents | 130 | 30 | NONE (production never reaches it; = 0137.drawing roads 30 ft) | road width fallback |
| registry.py::element_extents | 130 | 6 | NONE (production never reaches it; = 0081.drawing track 6 ft) | lane width fallback |
| registry.py::__init__ | 231 | 4000 | CONVENTION | default sheet size |
| reserved.py::seat_radius | 79 | 8 | NONE (fallback never fires; every well carries r) | well radius fallback |
| reserved.py::conflicts | 162 | 6 | NONE (fallback never fires; every lane carries w; = 0081 track) | lane width fallback |
| reserved.py::seat_walls | 213 | 12 | NOT-ABOUT-THE-WORLD | keep-out polygon sides |
| taxonomy.py::_mx_same | 775 | 1.5 | NONE | same-point tolerance |
| geom.py::crosses_poly | 84 | 8 | NOT-ABOUT-THE-WORLD | sampling step |
| geom.py::crosses_poly | 84 | 900 | NOT-ABOUT-THE-WORLD | sample cap |
| well_gear.py::gear_svg | 91 | 3.5 | CONVENTION | pulley frame's left post offset |
| well_gear.py::gear_svg | 93 | 1.5 | CONVENTION | left post dot offset |
| well_gear.py::gear_svg | 94 | 1.5 | CONVENTION | right post dot offset |
| well_gear.py::gear_svg | 95 | 1.5 | CONVENTION | crossbar end offset |

**Leads not followed**
- The 1811 Amagi 御林改め (forest survey) records tree counts per subdivision (named in the first search's summary, page not read). It is a closed forest, not a grass hill, but it may be the nearest period stand count.