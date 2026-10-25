I ruled all 128 numbers in `t38_N6-waterfields.txt`. Only one was an open question about the world: how often a dry plot keeps its neighbour's crop (`carve.py:282`, 0.45). My search on it found nothing, so it is **SILENT**. Everything else was settled by the record or decides nothing about the place. I read no web page, so nothing went on the sources ledger.

## Sources from the record

Research pages are in `/diagram/research/questions/`.

- **0005 drawing page** (`0005-rice-paddies-and-their-plots-suiden.drawing.html`):
  - "No basin tapers to a point sharper than 25 degrees … The maps refuse a point sharper than 25 degrees."
  - "the usual basin is about 48 ft across its canal and 26 to 36 ft along it". 26 to 36 ft is 31 ft give or take 16%, which is the code's 0.16.
  - "the maps set no least width for a basin; that would have been the obvious rule, and a wrong one."
- **0054 drawing page**: "A bend's radius is capped at 35% of the straight run on either side."
- **0068 drawing page**: "a delivery ditch's head is capped at 0.8 of its canal's local width where it leaves it".
- **0006 drawing page**:
  - "Its rows run either along the contour or down to its outfall, the two a right angle apart".
  - On crops it says two opposite things: "each plot is its own field, often of another crop than its neighbor" and "a plot often keeping its neighbor's crop". It gives no source for either.
- **0007 drawing page**: "A comb field gives each plot of its lowest row, the ones whose foot lies on the drain, a 45% chance of the tint". It also says: "Which plots wear the tint is a drawing convention, not a survey."
- **0022 drawing page**:
  - "a walking bund about 3 ft wide, or a field ditch with its banks, about 8 ft. Both widths are this project's setting". The code insets each parcel by 1.5 ft on each side, which gives the page's 3 ft.
  - "About three mu (~half an acre) on average … a figure the drawing is set to" and "most split into two or three oblong strips and a few merge along the fall".
  - Worked out on a 5.5 mu module (my arithmetic), `parcel_mix` (0.52 two strips, 0.16 three, 0.12 merged, 0.20 whole) gives 1.78 parcels a module, a mean of 3.1 mu. That matches the page's target.
- **0019 drawing page**:
  - "The canals are drawn in long, nearly straight reaches that waver gently … The line is a drawing convention."
  - "How strongly the lattice bends is a calibrated liberty. It was set on the Kuwabata map".
- **0284 drawing page**:
  - "A corner's rounding is drawn from a wide spread, from all but square to a broad sweep … a GUESS. The arc itself is roughened".
  - "up to about a tenth of the grid's spacing … How far a line bows is this project's setting … no page we read says how far a bund's run bowed".
- **0053 findings page** (as quoted in `_comb_threads`'s claims): "the delivery ditches leave their supply canal at right angles". Canal B's 58° is recorded there as "a departure the code keeps until feature 417 T34".
- **T29 pass P2b table** (`/diagram/.clones/diagram-backlog/specs/417-all-seeds-pass/evidence/t29/pass-P2b-fields.md`), rows marked not about the world: 40 (cut-back within its run), 56 (sub-ditches), 62 (thread wander), 63 (dug canal course), 69 and 73 (basin size and rows where the sector narrows). Row 45 (neighbor keeps the crop) reads "never searched".

## Search pass: does a dry plot keep its neighbour's crop?

**SILENT.**
- **Archive:** I ran `make archive-find` on 作付, 輪作, 畑作, 隣の畑, 同じ作物, 間作, hatake, crop rotation, neighbouring field, neighboring plot, 轮作, 旱地, 相邻 and 插花. I read the hits for 同じ作物 (ja.wikipedia 畑), neighbouring field (IDE paper) and 隣の畑 (MAFF Tarama). None speaks to it: the first is slash-and-burn fallow years, the second is irrigation passing between paddies, the third is island wells.
- **Web:** I ran four queries: 明清 江南 旱地 作物 地块 相邻 种植 布局 插花; 江戸時代 畑 作付 村 隣接 同じ作物 まとまり; 近世 畑 輪作 麦 大豆 粟 一筆ごと 作物 異なる 村絵図; and an English query on Tokugawa upland plots and same-crop blocks. The results carried only background: Li Bozhong on Jiangnan, Huizhou shack people, Musashino upland villages, and 村絵図 as a type of record.

**A mismatch to correct:** the unit's own claim says "GUESS: searched, the record silent (T36 P2b)". P2b row 45 says it was never searched. As of this pass it has been searched, and nothing was found. The code also keeps the neighbour's crop about two times in three (the claim's own reckoning), against 0006's "often of another crop than its neighbor".

## Table

NAW = NOT-ABOUT-THE-WORLD.

| file::unit | line | value | ruling | what the number does |
|---|---|---|---|---|
| banks.py::drain_bank_clearance | 93 | 1e9 | NONE | sentinel starting distance |
| banks.py::_nearest_segment | 143 | 1e9 | NONE | sentinel |
| banks.py::__init__ | 195 | 64 | NONE | spatial-index cell |
| banks.py::off_with_the_fall | 338 | 1e9 | NONE | sentinel |
| banks.py::hem_on_paddy | 669 | 0.85 | NAW | shrinks the quad before the overlap test, so a plot just touching the paddy is kept |
| banks.py::round_channel_joints | 676 | 6 | NAW | samples along a rounded bend |
| banks.py::swept_bend | 732 | 0.35 | CITED 0054.drawing | bend radius capped at 35% of the run ("capped at 35% of the straight run") |
| banks.py::swept_bend | 732 | 0.9 | NAW (P2b row 40) | a hairpin's tangent point kept within 90% of its run |
| banks.py::jog_vertices | 884 | 5 | NAW | too few vertices for a run, a hop and the run resuming |
| banks.py::pointed_ring | 913 | 25 | CITED 0005.drawing | sharpest angle allowed at a basin's point ("sharper than 25 degrees") |
| carve.py::_dry_fields | 72 | 1.1 | CITED 0006.drawing | default spread is "not steep", so tracts take both row directions; the value only has to be at least 0.3 |
| carve.py::_dry_fields | 222 | 1e9 | NONE | sentinel fallback |
| carve.py::_dry_fields | 282 | 0.45 | GUESS 0006.drawing; SILENT this pass | chance a plot re-rolls its crop instead of keeping its neighbour's |
| comb.py::carve_comb | 91 | 45 | NONE | default fall direction; the only caller (`fit.py`) passes `plan.down_deg` |
| comb.py::carve_comb | 102 | 1.1 | CITED 0006.drawing | same default spread as carve.py:72 (no caller overrides it) |
| comb.py::finish_comb | 260 | 73733 | NONE | seed salt (0x12005) |
| comb.py::finish_comb | 267 | 43560 | NONE | square feet in an acre |
| comb.py::_mk_thread | 338 | 110 | NAW (P2b row 62) | how far down the fall a ditch's takeoff heading relaxes |
| comb.py::_mk_thread | 342 | 1.2 | NAW | heading clamp that keeps tan() finite |
| comb.py::_mk_thread | 344 | 0.2 | NONE | floor on cos (divide guard) |
| comb.py::_comb_skeleton | 388 | 0.045 | NAW (P2b row 63) | canal A's heading wobble per segment |
| comb.py::_comb_skeleton | 392 | 0.05 | NONE | wobble of a polyline that is thrown away (only its random draw is kept) |
| comb.py::_comb_skeleton | 392 | 120 | NONE | segment length of the same thrown-away polyline |
| comb.py::_comb_skeleton | 392 | 58 | CONTRADICTED 0053.html (kept departure) | canal B's heading off the fall; the polyline here is thrown away, but `bc` reuses the 58 |
| comb.py::_comb_threads | 422 | 170 | NAW (P2b row 62) | canal B thread's relax distance |
| comb.py::_comb_threads | 462 | 0.24 | NAW (P2b row 56) | sub-ditch takeoff, low end of its share of the run |
| comb.py::_comb_threads | 462 | 0.38 | NAW (P2b row 56) | the same, high end |
| comb.py::_comb_threads | 474 | 40 | NAW | fallback if canal B has no offtake (its claim guarantees one) |
| comb.py::_comb_march | 494 | 300 | NAW | march overrun past the frame |
| comb.py::_comb_march | 518 | 60 | NAW | off-frame margin that stops the march |
| comb.py::_comb_brook | 614 | 14 | NAW | is the outfall inside the frame |
| comb.py::_comb_brook | 622 | 40 | NONE | step cap on a course that is not drawn |
| comb.py::_comb_brook | 627 | 22 | NONE | cross-slope jitter of the undrawn course |
| comb.py::_comb_brook | 627 | 40 | NONE | the same |
| comb.py::_comb_brook | 627 | 88 | NONE | step length; the first heading is direction only |
| comb.py::_comb_brook | 628 | 105 | NONE | downhill step of the undrawn course |
| comb.py::_comb_brook | 628 | 72 | NONE | the same |
| comb.py::_comb_brook | 628 | 88 | NONE | step length, as line 627 |
| comb.py::_comb_brook | 631 | 12 | NONE | edge stop of the undrawn course |
| comb.py::_comb_canal_pieces | 697 | 6 | NAW | samples per canal piece |
| comb.py::_comb_canal_pieces | 697 | 7 | NAW | the same (range end) |
| frame.py::__init__ | 258 | 110 | NAW (P2b row 62) | thread relax distance |
| frame.py::_f_at_u | 305 | 20 | NAW | range tolerance |
| furrows.py::settle_tract_seams | 157 | 0.025 | NAW | rotation search step |
| furrows.py::settle_tract_seams | 157 | 64 | NAW | rotation search count |
| hem.py::_comb_dry_and_beans | 103 | 43560 | NONE | square feet in an acre |
| hem.py::middle_reserve | 192 | 32 | NONE | seed bits |
| palette.py::paddy_grain | 35 | 0.16 | CITED 0005.drawing | row step ±16% (26 to 36 ft, so 31 ft ±16%) |
| palette.py::paddy_grain | 48 | 43560 | NONE | square feet in an acre |
| palette.py::organic_parcel | 131 | 5 | NAW | most arc samples |
| palette.py::organic_parcel | 154 | 0.42 | NAW | keeps a corner cut inside its edge (validity guard) |
| palette.py::organic_parcel | 176 | 0.12 | GUESS 0284.drawing | smallest corner fillet ("all but square") |
| palette.py::organic_parcel | 176 | 0.7 | GUESS 0284.drawing | most likely fillet |
| palette.py::organic_parcel | 176 | 2.2 | GUESS 0284.drawing | largest fillet ("a broad sweep") |
| palette.py::organic_parcel | 186 | 0.18 | GUESS 0284.drawing | roughening of the arc (page gives no amount) |
| palette.py::organic_parcel | 192 | 0.8 | NAW | sample density of the arc |
| palette.py::organic_parcel | 205 | 0.1 | NAW | a run's wander capped at a tenth of its own length (spike guard) |
| partition.py::__init__ | 141 | 20 | NAW | overrun past the region |
| partition.py::thread_lines | 175 | 40 | NAW | overrun of the extension |
| partition.py::grid_lines | 201 | 6 | NAW | width-sampling start offset; cancelled at line 213 |
| partition.py::grid_lines | 203 | 12 | NAW | width samples |
| partition.py::grid_lines | 203 | 13 | NAW | the same (range end) |
| partition.py::grid_lines | 209 | 6.28 | NONE | phase range (about 2π) |
| partition.py::grid_lines | 210 | 6.28 | NONE | phase range (about 2π) |
| partition.py::grid_lines | 213 | 6 | NAW | first row back at the root |
| partition.py::grid_lines | 223 | 70 | GUESS 0284.drawing | wavelength of the column-line wobble |
| partition.py::grid_lines | 225 | 47 | GUESS 0284.drawing | wavelength of the row drift |
| partition.py::grid_lines | 251 | 40 | NAW | line overrun |
| partition.py::outer_lines | 267 | 40 | NAW | line overrun |
| partition.py::_column_kept | 315 | 1.5 | NAW (as P2b rows 69/73; 0005 sets no least width) | thin columns once there are 1.5× too many |
| polder.py::build_polder | 73 | 0.52 | CITED 0022.drawing | share of modules split in two (the mix gives about 3.1 mu a parcel) |
| polder.py::build_polder | 73 | 0.16 | CITED 0022.drawing | share split in three |
| polder.py::build_polder | 73 | 0.12 | CITED 0022.drawing | share merged along the fall |
| polder.py::build_polder | 78 | 0.1 | GUESS 0284.drawing | module line bows up to a tenth of a module ("this project's setting") |
| polder.py::build_polder | 147 | 1.5 | GUESS 0022.drawing | half of the 3 ft walking-bund gap ("this project's setting") |
| polder.py::_polder_lattice | 252 | 24301 | NONE | seed salt (0x5EED) |
| polder.py::_polder_lattice | 253 | 0.9 | GUESS 0019.drawing | edge-wander amplitude (a drawing convention) |
| polder.py::_polder_lattice | 254 | 0.05 | GUESS 0019.drawing | block tilt |
| polder.py::_polder_lattice | 260 | 0.4 | GUESS 0019.drawing | cross-warp harmonic weight |
| polder.py::_polder_lattice | 260 | 0.6 | GUESS 0019.drawing | cross-warp harmonic weight |
| polder.py::_polder_lattice | 260 | 0.8 | GUESS 0019.drawing | cross-warp frequency |
| polder.py::_polder_lattice | 260 | 1.7 | GUESS 0019.drawing | cross-warp frequency |
| polder.py::_polder_lattice | 264 | 0.4 | GUESS 0019.drawing | fall-warp harmonic weight |
| polder.py::_polder_lattice | 264 | 0.6 | GUESS 0019.drawing | fall-warp harmonic weight |
| polder.py::_polder_lattice | 264 | 0.7 | GUESS 0019.drawing | fall-warp frequency |
| polder.py::_polder_lattice | 264 | 1.6 | GUESS 0019.drawing | fall-warp frequency |
| polder.py::_polder_lattice | 300 | 12377 | NONE | seed salt (0x3059) |
| polder.py::_polder_lattice | 309 | 0.6 | GUESS 0019.drawing | mosaic harmonic weight ("calibrated liberty") |
| polder.py::_polder_lattice | 309 | 1.3 | GUESS 0019.drawing | mosaic frequency |
| polder.py::_polder_lattice | 309 | 2.1 | GUESS 0019.drawing | mosaic frequency |
| polder.py::_polder_lattice | 310 | 0.6 | GUESS 0019.drawing | mosaic harmonic weight |
| polder.py::_polder_lattice | 310 | 1.1 | GUESS 0019.drawing | mosaic frequency |
| polder.py::_polder_lattice | 310 | 1.9 | GUESS 0019.drawing | mosaic frequency |
| polder.py::_polder_lattice | 327 | 4606 | NONE | seed salt (0x11FE) |
| polder.py::_polder_lattice | 329 | 0.35 | GUESS 0284.drawing | least bow of a row line |
| polder.py::_polder_lattice | 329 | 0.9 | GUESS 0284.drawing | row-bow frequency, low end |
| polder.py::_polder_lattice | 329 | 2.3 | GUESS 0284.drawing | row-bow frequency, high end |
| polder.py::_polder_lattice | 330 | 0.35 | GUESS 0284.drawing | least bow of a column line |
| polder.py::_polder_lattice | 330 | 0.9 | GUESS 0284.drawing | column-bow frequency, low end |
| polder.py::_polder_lattice | 330 | 2.3 | GUESS 0284.drawing | column-bow frequency, high end |
| polder.py::_polder_parcels | 401 | 47710 | NONE | seed salt (0x0BA5E) |
| polder.py::_polder_envelope | 455 | 12 | NAW | samples per side |
| polder.py::_polder_envelope | 456 | 12 | NAW | the same |
| polder.py::_polder_ring | 493 | 2.2 | GUESS 0019.drawing | ring-canal waver frequency ("waver gently … a drawing convention") |
| polder.py::_polder_ring | 518 | 6 | NAW | samples per side |
| polder.py::_polder_ring | 518 | 7 | NAW | the same (range end) |
| polder.py::_polder_ring | 519 | 1.7 | NONE | phase step between sides |
| polder.py::_polder_ring | 521 | 6 | NAW | corner-arc samples |
| polder.py::_polder_ring | 521 | 7 | NAW | the same (range end) |
| polder.py::_polder_channels | 611 | 0.8 | CITED 0068.drawing | ring toes capped at 0.8 of the feeder (the page's delivery rule) |
| polder.py::_polder_channels | 647 | 0.8 | CITED 0068.drawing | a lateral's head capped at 0.8 of its canal |
| polder.py::_thin | 767 | 0.4 | NONE | simplify tolerance |
| polder.py::_polder_close | 853 | 0.75 | NAW | test for trimming a trailing stub leg |
| polder.py::_polder_close | 857 | 5 | NAW | fallback drain width if no drain exists (every polder draws one) |
| polder.py::clean_polder_parcels | 871 | 43560 | NONE | square feet in an acre |
| ring_rules.py::fan_context | 452 | 0.05 | NONE | duplicate-point tolerance |
| seams/close.py::blunt_points | 147 | 0.45 | NAW | cut kept within 45% of each leg (validity guard) |
| seams/close.py::_weld_within_rules | 182 | 0.4 | NONE | buffer tolerance |
| seams/close.py::_weld_within_rules | 183 | 0.02 | NONE | buffer tolerance |
| seams/close.py::_weld_within_rules | 193 | 0.05 | NONE | simplify tolerance |
| seams/pockets.py::_outside_command | 171 | 6 | NAW | sampling step |
| seams/pockets.py::_outside_command | 171 | 64 | NAW | least sample count |
| settle.py::shared_length | 139 | 0.2 | NONE | buffer tolerance |
| settle.py::neighbors | 231 | 0.2 | NONE | buffer tolerance |
| settle.py::neighbors | 232 | 0.2 | NONE | buffer tolerance |
| tint.py::mark_low | 91 | 0.25 | CITED 0007.drawing | quarter-plot reach, the code's test of "whose foot lies on the drain" |
| tint.py::fronts | 105 | 0.25 | CITED 0007.drawing | the same test of fronting the drain |
| tint.py::judge_tint | 162 | 0.25 | CITED 0007.drawing | the same, for the tint floor |

## Leads not followed
- 山口徹『近世畑作村落の研究』(2000), on early modern upland-field villages: may show how crops were laid out plot by plot.
- Li Bozhong, *Agricultural Development in Jiangnan, 1620-1850*: dry-land crop arrangement.
- 検地帳 or 作付 records that list a crop for each plot (Japan), and 魚鱗圖冊 fish-scale registers (China): could give a real adjacency share.

Sources:
- [kotobank 畑作](https://kotobank.jp/word/%E7%95%91%E4%BD%9C-601740) (search result only, not read)
- [Agricultural Development in Jiangnan, 1620-1850](https://shss.hkust.edu.hk/node/216) (search result only, not read)
- [Cultivating Commons, OSU](https://history.osu.edu/publications/cultivating-commons-joint-ownership-arable-land-early-modern-japan) (search result only, not read)
- [Geographical Review of Japan 24(7)](https://www.jstage.jst.go.jp/article/grj1925/24/7/24_7_231/_article/-char/en) (search result only, not read)