I ruled all 84 numbers in `t38_N2-hinterland.txt`. Only one world question had no earlier search, the shape of a coppice lot, and I found nothing on it, so it is SEARCHED-SILENT. Most of the hinterland's world questions were already searched by pass P5 (`/diagram/.clones/diagram-backlog/specs/417-all-seeds-pass/evidence/t29/pass-P5-hinterland.md`). I reused those rulings rather than search them again. Nothing was edited.

## Sources that bear on these numbers

**Record pages** (`/diagram/research/questions/`):
- **0071.drawing** (groves; Hong Kong measurements are modern measurements of old groves):
  - 「The back grove is drawn 80 to 120 ft deep. … A convention: no source gives a grove's depth.」
  - 「no clump of the back grove … stands within 50 ft east, west or south of a yard or kitchen bed; where the wind puts the back grove west of the houses, its inner edge moves out to keep that distance.」
- **0068** (channel widths): 「This record's widths for a village brook and a town river, about 2 m (~7 ft) and 20 m (~66 ft), are GUESSES. … no record from before modern times that we read gives either a width.」
- **0080.drawing** (crowns): 「One crown size serves the hill woods and the windbreak's cedars alike … No page we read gives a crown width for a cedar windbreak.」 and 「so every crown size is a GUESS.」
- **0077.drawing** (coppice): 「So each patch is drawn as an outline whose edge wanders smoothly … The wandering edge itself is a map drawing convention.」 The page gives the rule but no numbers. The `_parcel_outline` docstring credits it with "radius 0.80-1.00 on two low harmonics", which overstates what the page says.
- **0077.notes**: 「none describes a coppice lot laid out as a surveyed rectangle.」
- **0075.drawing / .notes** (bamboo): the thicket's size and seat are GUESS. No passage gives the thicket's clearance from yards, sheds or wells. P5 searched this and found only that bamboo was attested right against houses, plus the 農政全書 (1639) note that its roots damage paving.
- **0038** (Qimin Yaoshu, 6th c., as P5 quotes it): a tree's shade reaches east, west and north as far as the tree is tall, about 33 ft at the record's 10 m windbreak.

**This pass's search: coppice lot aspect and bearing (`open_ground_patches` 1.2, and the ±20° bearing jitter on the same unit)**
- **SEARCHED-SILENT.** Nothing found says whether a village's coppice lots were long or square, or how they lay to the slope.
- Archive terms: 割山, 山割, 短冊, 雑木林 区画, 薪炭林, 入会林, coppice lot, woodlot. The only hit worth reading was the archived ja.wikipedia 入会地 article, which says nothing about lot shape.
- Web queries:
  - 割山 江戸時代 入会山 分割 短冊状 尾根 麓 区画
  - 割山 割地 山林 江戸 各戸に分割 形状 帯状 斜面
  - English "wariyama … strips slope ridge to foot"
  - 清代 分山 山场 分界 契约 柴山 地块 形状 自山脚至山顶
- Page read: the Tohoku repository paper on Ueda Kami-Shiojiri's 割山, which cites an 1860 (万延元年) agreement. It reports 226 household lots and kunugi (sawtooth oak) planting, but nothing on lot shape or how lots lay to the slope. I recorded it as nothing-found; `make source-pages` could not read it, so I read the PDF through pdftotext.

## Flags (stale or duplicated numbers)
- **`past_the_lanes` default `depth=146`**: this is 36 + an old 110 ft depth. Its only engine caller passes `BELT_NEAR_FT + BELT_DEPTH_FT`, which is 136. The default is used only by `tests/hamletgen/test_hinterland.py:597`.
- **`frame.py:58` fallback `w` 6**: every stream record is written with `w` (`settlement/water_ways/water.py`: `self.px(7.0)`, 0068's 7 ft), so the 6 never fires. It also disagrees with that 7 ft.
- **`stages.py:367` `14.0 * s.bscale`**: this is half of `village_grove`'s 28-unit windbreak clump (`settlement/homestead_parts/stands.py`, "GUESS … T36 pass P1"), typed in again instead of read from there.
- **`belt.py:320` `+ 12.0`**: per its comment this comes from the plot geometry: half-house 23 + gap 3 + bed 22, minus the 36 ft face. The claim belongs with those constants.
- **`belt_polygon` ladder**: the steps are not about the world. P5's departure stands, and T33 already carries it: the real refusal is 20 px from the crop, inside one tree-height of shade (0038).

## One row per number

| file::unit | line | value | ruling | what the number does |
|---|---|---|---|---|
| bamboo.py::bamboo_seats | 217 | 8 | SEARCHED-SILENT (P5 "keep-out pads") | thicket kept 8 ft off a threshing yard |
| bamboo.py::bamboo_seats | 218 | 8 | SEARCHED-SILENT (P5) | thicket kept 8 ft off a garden |
| bamboo.py::bamboo_seats | 219 | 8 | SEARCHED-SILENT (P5) | thicket kept 8 ft off a farm shed |
| bamboo.py::bamboo_seats | 220 | 8 | SEARCHED-SILENT (P5) | thicket kept 8 ft off a byre |
| bamboo.py::bamboo_seats | 231 | 14 | SEARCHED-SILENT (P5) | thicket kept 14 ft off a well |
| bamboo.py::bamboo_seats | 237 | 1e9 | NONE | unbounded box for sun keep-outs |
| belt.py::fringe_profile | 48 | 40 | NOT-ABOUT-THE-WORLD | column's search window across the wind (rule CITED 0072.drawing) |
| belt.py::past_the_lanes | 92 | 146 | CITED 0071.drawing (80-120 ft convention); stale default, see flags | default near face + depth |
| belt.py::round_the_houses | 194 | 15 | NOT-ABOUT-THE-WORLD | arc sampling step, degrees |
| belt.py::round_the_houses | 194 | 7 | NOT-ABOUT-THE-WORLD | arc sample count bound |
| belt.py::belt_polygon | 274 | 24 | NOT-ABOUT-THE-WORLD | most profile columns |
| belt.py::belt_polygon | 274 | 7 | NOT-ABOUT-THE-WORLD | fewest profile columns |
| belt.py::belt_polygon | 276 | 4.29497e+09 | NONE | seed mask |
| belt.py::belt_polygon | 276 | 7919 | NONE | seed multiplier |
| belt.py::belt_polygon | 320 | 12 | CITED 0071.drawing (rule: inner edge moves out for the sun); value derived, see flags | extra west-sun offset of the near face |
| belt.py::belt_polygon | 329 | 11 | NOT-ABOUT-THE-WORLD | lane samples per segment |
| belt.py::belt_polygon | 371 | 0.88 | NOT-ABOUT-THE-WORLD (P5 flag stands) | belt-shortening step off the crop |
| belt.py::belt_polygon | 371 | 0.74 | NOT-ABOUT-THE-WORLD (P5 flag) | belt-shortening step off the crop |
| belt.py::belt_polygon | 371 | 44 | NOT-ABOUT-THE-WORLD (P5 flag) | push-back step off the crop |
| belt.py::belt_polygon | 385 | 40 | NOT-ABOUT-THE-WORLD | same window as line 48, in belt reach |
| belt.py::belt_polygon | 386 | 6 | CONVENTION | belt vertices clamped inside the canvas |
| frame.py::brook_beside_the_field | 58 | 6 | GUESS 0068 (page guesses 7 ft; fallback departs and never fires) | brook width if a record lacks w |
| frame.py::pocket_clear_of_features | 274 | 8 | CONVENTION | default glyph radius (box width) |
| frame.py::pocket_clear_of_features | 275 | 8 | CONVENTION | default glyph radius (box height) |
| frame.py::pocket_clear_of_features | 277 | 19 | CONVENTION | torii glyph box half-width |
| frame.py::pocket_clear_of_features | 277 | 18 | CONVENTION | torii glyph box below the point |
| frame.py::clear_pocket_spot | 288 | 22 | CONVENTION | title scan inset (top) |
| frame.py::clear_pocket_spot | 289 | 22 | CONVENTION | title scan inset (bottom) |
| frame.py::clear_pocket_spot | 290 | 22 | CONVENTION | title scan inset (left) |
| frame.py::clear_pocket_spot | 291 | 22 | CONVENTION | title scan inset (right) |
| frame.py::clear_pocket_spot | 294 | 24 | NOT-ABOUT-THE-WORLD | title scan x step |
| frame.py::clear_pocket_spot | 295 | 24 | NOT-ABOUT-THE-WORLD | title scan y step |
| frame.py::title_pocket | 299 | 300 | CONVENTION | title pocket width |
| frame.py::title_pocket | 299 | 190 | CONVENTION | title pocket height |
| frame.py::title_pocket | 324 | 15 | CONVENTION | placard margin, width |
| frame.py::title_pocket | 324 | 14 | CONVENTION | placard margin, height |
| frame.py::title_pocket | 325 | 30 | CONVENTION | content box pad on the sheet |
| frame.py::title_pocket | 350 | 15 | CONVENTION | smaller pocket margin, width |
| frame.py::title_pocket | 350 | 14 | CONVENTION | smaller pocket margin, height |
| frame.py::title_pocket | 365 | 12 | CONVENTION | placard + 6 px each side |
| frame.py::title_pocket | 370 | 8 | CONVENTION | outside pocket offset from content |
| frame.py::title_pocket | 371 | 16 | CONVENTION | outward label shift |
| frame.py::title_pocket | 371 | 32 | CONVENTION | outward label shift |
| frame.py::title_pocket | 371 | 48 | CONVENTION | outward label shift |
| parcels.py::fit_square_parcel | 132 | 0.8 | NOT-ABOUT-THE-WORLD | shrink-ladder rung |
| parcels.py::fit_square_parcel | 132 | 0.7 | NOT-ABOUT-THE-WORLD | shrink-ladder rung |
| parcels.py::parcel_wet_share | 160 | 5 | NOT-ABOUT-THE-WORLD | sample grid columns |
| parcels.py::parcel_wet_share | 161 | 5 | NOT-ABOUT-THE-WORLD | sample grid rows |
| parcels.py::parcel_wet_share | 162 | 5 | NOT-ABOUT-THE-WORLD | grid x division |
| parcels.py::parcel_wet_share | 163 | 5 | NOT-ABOUT-THE-WORLD | grid y division |
| parcels.py::parcel_wet_share | 166 | 25 | NOT-ABOUT-THE-WORLD | sample count |
| parcels.py::off_the_row | 203 | 1.05 | NOT-ABOUT-THE-WORLD | sideways step off a row |
| parcels.py::off_the_row | 203 | 1.5 | NOT-ABOUT-THE-WORLD | sideways step off a row |
| parcels.py::_beyond_the_fields | 303 | 1e9 | NONE | tier-ranking sentinel |
| parcels.py::open_ground_patches | 406 | 0.2 | NOT-ABOUT-THE-WORLD (P5 "per-parcel size bands") | per-map ladder spread 0.9-1.1 |
| parcels.py::open_ground_patches | 406 | 76 | NONE | jitter salt |
| parcels.py::open_ground_patches | 452 | 0.415 | NOT-ABOUT-THE-WORLD | √2−1 diagonal slack, geometry |
| parcels.py::open_ground_patches | 475 | 16 | NOT-ABOUT-THE-WORLD | scan window inset from content box |
| parcels.py::open_ground_patches | 476 | 16 | NOT-ABOUT-THE-WORLD | scan window inset from content box |
| parcels.py::open_ground_patches | 583 | 71 | NONE | jitter salt |
| parcels.py::open_ground_patches | 584 | 72 | NONE | jitter salt |
| parcels.py::open_ground_patches | 596 | 73 | NONE | jitter salt |
| parcels.py::open_ground_patches | 597 | 0.36 | NOT-ABOUT-THE-WORLD (P5) | size-band spread 0.82-1.18 |
| parcels.py::open_ground_patches | 683 | 78 | NONE | jitter salt (bearing) |
| parcels.py::open_ground_patches | 690 | 1.2 | SEARCHED-SILENT (0077.notes; this pass) | lot elongation up to 2.2:1 |
| parcels.py::open_ground_patches | 690 | 77 | NONE | jitter salt |
| parcels.py::open_ground_patches | 692 | 0.72 | NOT-ABOUT-THE-WORLD | aspect-ladder step |
| parcels.py::open_ground_patches | 692 | 0.45 | NOT-ABOUT-THE-WORLD | aspect-ladder step |
| parcels.py::open_ground_patches | 751 | 1.35 | NOT-ABOUT-THE-WORLD (P5 "parcels kept apart") | exclusion radius 1.15-2.5× size |
| parcels.py::open_ground_patches | 751 | 74 | NONE | jitter salt |
| parcels.py::_parcel_outline | 755 | 12 | NOT-ABOUT-THE-WORLD | outline vertex count |
| parcels.py::_parcel_outline | 780 | 79 | NONE | jitter salt |
| parcels.py::_parcel_outline | 780 | 80 | NONE | jitter salt |
| parcels.py::_parcel_outline | 783 | 0.35 | CITED 0077.drawing (convention; number not on page) | vertex angle wander |
| parcels.py::_parcel_outline | 783 | 81 | NONE | jitter salt |
| parcels.py::_parcel_outline | 785 | 0.2 | CITED 0077.drawing (convention; docstring overstates) | edge radius wander range |
| parcels.py::_parcel_outline | 785 | 0.25 | CITED 0077.drawing (convention) | harmonic amplitude |
| parcels.py::_parcel_outline | 785 | 0.8 | CITED 0077.drawing (convention) | minimum edge radius share |
| parcels.py::follow_the_bounds | 897 | 19 | NOT-ABOUT-THE-WORLD | coarse search start |
| parcels.py::follow_the_bounds | 897 | 20 | NOT-ABOUT-THE-WORLD | coarse search divisions |
| parcels.py::follow_the_bounds | 901 | 0.05 | NOT-ABOUT-THE-WORLD | bisection bracket |
| parcels.py::follow_the_bounds | 902 | 20 | NOT-ABOUT-THE-WORLD | bisection iterations |
| parcels.py::open_ground_region | 935 | 40 | NOT-ABOUT-THE-WORLD | raster region pad |
| parcels.py::open_ground_region | 942 | 40 | NOT-ABOUT-THE-WORLD (set-backs CITED 0038) | "south of the crop" tolerance |
| parcels.py::_crop_refuses | 983 | 40 | NOT-ABOUT-THE-WORLD (set-backs CITED 0038) | same tolerance |
| stages.py::plant_the_belt | 351 | 30 | CONVENTION | frame opened past belt (x) |
| stages.py::plant_the_belt | 353 | 30 | CONVENTION | frame opened past belt (y) |
| stages.py::plant_the_belt | 367 | 14 | GUESS 0080.drawing (copy of stands.py clump/2) | belt clump radius for page prediction |
| stages.py::stage_windbreak | 444 | 210 | NONE | jitter salt |

## Leads not followed
- 越後 and 芸州北部 割山 studies, and Meiji cadastral maps (地籍図) of divided commons: these might show how the lots lay to the slope.
- Huizhou mountain-share contracts (山场 四至 契约 分股) for how Ming-Qing fuel hills were divided.
- P5's leads remain open (川西林盘, the u-ryukyu Tarama PDF that needs OCR, 農業全書 on bamboo).

Sources:
- [Tohoku repository, 割山 paper (nothing found)](https://tohoku.repo.nii.ac.jp/record/137233/files/0387-3056-2021-78-1-1.pdf)
- [Azumino 入会絵図 PDF (search result only)](https://www.city.azumino.nagano.jp/uploaded/attachment/58810.pdf)
- [kotobank 割地制度 (search result only)](https://kotobank.jp/word/%E5%89%B2%E5%9C%B0%E5%88%B6%E5%BA%A6-880122)
- [Warichi, Wikipedia (search result only)](https://en.wikipedia.org/wiki/Warichi)
- [HKUST Journal 21.2 (search result only)](https://schina-publication.hkust.edu.hk/sites/default/files/pubs/Jour-21.2.B03.pdf)