I ruled all the numbers in the file. Only one is a question about the world that the record had not already ruled on: how far a dug drain bows off its straight line (the 0.08 at `sink.py` lines 476 and 631). The search pass on it came back **SILENT**. I edited nothing. I read one web page and recorded its outcome on the ledger with `make source-outcome`.

## Sources

**From the record**
- **`research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html`**:
  - "head race (the whole fan, above the fork) 6.0 small main canal". This is the 6.0 fallback at `washing.py` line 80. The page rests the 6.0 on the excavated Hattori canal and on the 1537 Jugo canal rules.
  - "A field ditch at the floor, about 1.5 ft on a hamlet map". This is the 1.5 fallback at line 81.
  - "drain 1.2 -> 5.5". This is the drain's drawn width, `DRAIN_FT`.
- **`0068-…ladder-of-channel-widths.html`**: it calls the brook's width of "about 2 m (~7 ft)" a GUESS. `Settlement.stream` writes `w = px(7.0)` with that claim. The 9.0 fallbacks below are therefore 2 ft off the record. They also never fire, because every stream record carries a `w`.
- **`0031-clustered-and-scattered-villages-shuson-sanson.drawing.html`**: "The channel is drawn 2.5 ft wide, as a delivery ditch is where it leaves its canal. That is a map drawing convention". This covers the 2.5 at `washing.py` lines 83 and 189 (`FARM_CHANNEL_W_FT`).
- **`0001-the-five-sizes-of-settlement-….drawing.html`**: "A hamlet draws 10 to 20 households". The `.html` page adds: "A hamlet is 10 to 20 households, 50 to 100 inhabitants. That is the setting's figure." This covers the cohort's span of 11 (10 to 20 households).
- **`0065-washing-places-at-the-waters-edge.html`**: "A washing place is drawn as a small pale footing with its steps marked across it. This is a map drawing convention". This covers the step lines (`/6`).
- **`0054-…how-channels-bend-and-join.drawing.html`** and **`0060-field-drains-akusuiro.drawing.html`**, read in full for the bow:
  - 0054 covers only the radius at a channel's turn: "About 2.5 channel widths in radius: … taken for a dug ditch as a GUESS".
  - 0060's "one such drain is a single straight leg about 400 ft long" describes one of the project's own city maps. It is not period evidence.
  - Neither page covers a bow along a straight run.

**From the search pass on the bow**
- **Archived: `https://www.jstage.jst.go.jp/article/grj1984b/60/1/60_1_41/_pdf`** (Geographical Review of Japan B 60(1), "Irrigation Systems in Japan", p. 45, on the Tedori fan; Edo-period works, rebuilt in the early 1900s): "Most secondary canals and ditches on the fan were rebuilt and rearranged as straight channels during an arable land reorganization project in the early 1900s." It is in English, so no translation is needed. It implies that before 1900 these canals were not laid straight, but it gives no form or offset. It is about supply canals, not a drain into a pond.
- **Read and rejected: `https://www.maff.go.jp/kyusyu/seibibu/history/06.html`** (the Saga plain creeks): "現在、かんがい排水事業や圃場整備事業によりクリークの統廃合が進められており、上の写真のように直線化された効率的な水路に変貌している。" (translation): "Now the creeks are being merged and consolidated by irrigation-and-drainage and field-consolidation projects, and are turning into efficient straightened channels as in the photo above." These are tidal-plain channels "数m～35m" (several m to 35 m) wide, so the page does not bear on a short dug drain.

## Reading

**SILENT** on whether a short dug drain, from a field's outfall to its pond or to the passing brook, bowed off its straight line, and by how much (the code bows it up to 10 ft, 0.08 of the run). The archive search covered 悪水路, akusui, 排水沟, 排水路, 溜池, 蛇行, 曲がり and meander. The web queries were "耕地整理以前 水路 曲がりくねった 田んぼ 江戸時代 排水路" and "古代 农田 排水沟 弯曲 顺地势 沟渠 走向 明清". The Tedori paper says only that early-1900s reorganization made the fan's canals straight. The Saga page concerns tidal creeks metres wide. 0054 covers turns, not a run's line. The code's own claim calls the bow a CONVENTION, but under your definition it is a shape in the world, so a "GUESS: searched, the record silent" claim would fit it better.

## Table

| file::unit | line | value | ruling | what the number does |
|---|---|---|---|---|
| clearance.py::__init__ | 187 | 16 | NONE | floor on the spatial-index cell |
| cluster.py::back_fouled | 61 | 7 | NOT-ABOUT-THE-WORLD | sample count along the back (claim: T29 pass E) |
| cluster.py::belt_off_canvas | 106 | 0.45 | NOT-ABOUT-THE-WORLD | lateral sample position across the belt |
| cluster.py::belt_off_canvas | 106 | 0.9 | NOT-ABOUT-THE-WORLD | outer lateral sample position |
| cluster.py::seat_has_dry_exit | 128 | 16 | NOT-ABOUT-THE-WORLD | pond disc drawn as a 16-gon |
| cluster.py::seat_has_dry_exit | 128 | 8 | NONE | pi/8 step of the same 16-gon |
| cluster.py::straight_exit | 153 | 1.5 | NOT-ABOUT-THE-WORLD | wall margin in cells, so the quick test is sufficient for the flood fill |
| cluster.py::straight_exit | 153 | 1.75 | NOT-ABOUT-THE-WORLD | water-line margin in cells, same reason |
| cluster.py::seat_cluster | 247 | 0.6 | NOT-ABOUT-THE-WORLD | lateral sample, band on open ground |
| cluster.py::seat_cluster | 247 | 34 | NOT-ABOUT-THE-WORLD | middle sample depth past the band |
| cluster.py::seat_cluster | 257 | 0.3 | NOT-ABOUT-THE-WORLD (seat_cluster claim, T29 pass B: "no source could speak to it") | seat refused past 0.30 of its back under crop |
| cluster.py::seat_cluster | 288 | 0.6 | NOT-ABOUT-THE-WORLD | lateral sample, reed-fringe share |
| cluster.py::seat_cluster | 288 | 34 | NOT-ABOUT-THE-WORLD | middle sample depth, reed-fringe share |
| cluster.py::seat_cluster | 324 | 0.45 | NOT-ABOUT-THE-WORLD | lateral sample, brook on the band |
| cluster.py::seat_cluster | 324 | 0.9 | NOT-ABOUT-THE-WORLD | outer lateral sample, brook on the band |
| cluster.py::seat_cluster | 324 | 34 | NOT-ABOUT-THE-WORLD | middle sample depth, brook on the band |
| cluster.py::_fork_spur | 485 | 8 | NOT-ABOUT-THE-WORLD | cap on passes (stops the loop) |
| cluster.py::_fork_spur | 493 | 14 | NOT-ABOUT-THE-WORLD | match tolerance: a hit this near the spur's end is not a fork |
| driver.py::_run_stages | 321 | 0.05 | NONE | profile print threshold, in seconds |
| driver.py::cohort_specs | 426 | 11 | CITED 0001-the-five-sizes-of-settlement-….drawing.html ("A hamlet draws 10 to 20 households") | cohort household span, 10 to 20 |
| driver.py::cohort_specs | 426 | 7 | NONE | seed multiplier stepping through the span |
| frame.py::band_to_edge | 192 | 20 | NOT-ABOUT-THE-WORLD | overshoot past the view's edge (as pass-N1 ruled `stage_waterward`) |
| plan.py::canvas_for | 380 | 0.4 | NOT-ABOUT-THE-WORLD | the generator's measured fan fill; working canvas, cropped away |
| plan.py::canvas_for | 381 | 50 | NOT-ABOUT-THE-WORLD | canvas rounded to 50 |
| plan.py::band_extent | 397 | 1100 | NOT-ABOUT-THE-WORLD (band_extent claim, T36 pass P7: "no source could speak to it") | cap on the band's half-length |
| plan.py::plan_site | 512 | 50 | NOT-ABOUT-THE-WORLD | canvas rounded to 50 |
| pondbank.py::bank_seats | 71 | 61 | NONE | `_hjit` salt |
| pondbank.py::bank_seats | 72 | 67 | NONE | `_hjit` salt |
| pondbank.py::seat_free | 101 | 9 | GUESS 0068-…ladder-of-channel-widths.html (the page guesses ~7 ft; 9 is off it, and the fallback never fires) | fallback stream width when a record has no `w` |
| pondstock.py::_bank_seats | 76 | 0.125, 0.25, 0.375, 0.625, 0.75, 0.875 (one row each, same ruling) | NOT-ABOUT-THE-WORLD | candidate seats at each eighth of a bank edge (0025 gives the rule, not the fractions) |
| pondstock.py::reserve_sty_seat | 142 | 16 | NOT-ABOUT-THE-WORLD | reserved disc drawn as a 16-gon |
| sink.py::drain_record | 130 | 2.5 | NOT-ABOUT-THE-WORLD (per the docstring: the topology record is held at a hairline on purpose; the drawn width is `DRAIN_FT` 1.2 to 5.5, CITED 0068.drawing) | width written in the drain's connectivity record |
| sink.py::pond_clear_of_crop | 158 | 12 | NONE | pi/12 rim step |
| sink.py::pond_clear_of_crop | 158 | 24 | NOT-ABOUT-THE-WORLD | rim sample count |
| sink.py::pond_setback | 164 | 14 | NOT-ABOUT-THE-WORLD | step of the walk downslope |
| sink.py::pond_setback | 164 | 900 | NOT-ABOUT-THE-WORLD | walk's ceiling; the real limit, `POND_SETBACK_LIMIT` 300, is SEARCHED-SILENT (T36 pass P2a) |
| sink.py::pond_setback | 177 | 24 | NOT-ABOUT-THE-WORLD | rim sample count |
| sink.py::hull_route | 294 | 100000 | NONE | ray length sentinel |
| sink.py::hull_route | 314 | 260 | NOT-ABOUT-THE-WORLD | off-canvas leg length ("its length is free") |
| sink.py::hull_route | 316 | 40 | NOT-ABOUT-THE-WORLD | cap on lengthening tries |
| sink.py::hull_route | 320 | 400 | NOT-ABOUT-THE-WORLD | lengthening step off the canvas |
| sink.py::_through_the_crop | 362 | 20 | NOT-ABOUT-THE-WORLD | samples along the run |
| sink.py::_through_the_crop | 362 | 21 | NOT-ABOUT-THE-WORLD | range bound for the same samples |
| sink.py::pond_run | 476 | 0.08 | SEARCHED-SILENT (this pass; the code's claim says CONVENTION) | drain's bow off the chord, 0.08 of the run, at most 10 ft |
| sink.py::pond_run | 497 | 0.45 | NOT-ABOUT-THE-WORLD | cubic's handle length, measured to keep bends at or under 36 degrees |
| sink.py::pond_run | 505 | 12 | NOT-ABOUT-THE-WORLD | curve sampled at twelfths |
| sink.py::pond_run | 505 | 13 | NOT-ABOUT-THE-WORLD | range bound for the same samples |
| sink.py::lay_sink | 631 | 0.08 | SEARCHED-SILENT (this pass; the code's claim says CONVENTION) | drain-to-brook bow, as at line 476 |
| sink.py::lay_sink | 671 | 12, 24, 40, 60 (one row each, same ruling) | NOT-ABOUT-THE-WORLD | how far back up the drain the start may move to sit inside the field |
| sink.py::lay_sink | 693 | 12, 24, 38, 54 (one row each, same ruling) | NOT-ABOUT-THE-WORLD | bearing swings tried (claim: route search is NONE) |
| sink.py::lay_sink | 694 | 70, 110, 160 (one row each, same ruling) | NOT-ABOUT-THE-WORLD | junction distances, first sweep |
| sink.py::lay_sink | 695 | 300, 400 (one row each, same ruling) | NOT-ABOUT-THE-WORLD | junction distances, wider sweep |
| sink.py::lay_sink | 703 | 1e9 | NONE | sentinel |
| sink.py::lay_sink | 704 | 1e9 | NONE | sentinel |
| sink.py::lay_sink | 706 | 120 | NOT-ABOUT-THE-WORLD | floor on the run to the edge |
| sink.py::lay_sink | 706 | 260 | NOT-ABOUT-THE-WORLD | run carried off the canvas |
| sink.py::lay_sink | 799 | 20 | NOT-ABOUT-THE-WORLD | pond clamped 20 inside the working canvas |
| washing.py::passing_courses | 79 | 9 | GUESS 0068-…ladder-of-channel-widths.html (the page guesses ~7 ft; 9 is off it, and the fallback never fires) | fallback stream half-width base |
| washing.py::passing_courses | 80 | 6 | CITED 0068.drawing ("head race … 6.0") | fallback channel width |
| washing.py::passing_courses | 81 | 1.5 | CITED 0068.drawing ("A field ditch at the floor, about 1.5 ft") | fallback field-ditch width |
| washing.py::passing_courses | 83 | 2.5 | CITED 0031.drawing ("drawn 2.5 ft wide, as a delivery ditch is") | fallback farm-channel width |
| washing.py::each_house_places | 189 | 2.5 | CITED 0031.drawing (same words) | fallback farm-channel width at the step |
| washing.py::draw_washing_place | 211 | 6 | CONVENTION (0065: "steps marked across it … a map drawing convention") | step lines at plus and minus one sixth of the footing |

## Leads not followed
- The same out-of-record 9 ft stream fallback appears at `l7r/diagram/settlement/water_ways/clipping.py:174` and `l7r/diagram/settlement/homestead_parts/wood_share.py:164`. Neither is in this file.
- `washing.py:80` reads a drain's `channels` record `w` (the hairline 2.5 from `drain_record`) as its real half-width. A washing place on the drain is therefore seated 1.25 ft from the centerline, while the drain is drawn up to 5.5 ft wide.
- The Mie University paper `https://mie-u.repo.nii.ac.jp/record/6033/files/AN100738460330008.pdf` (field re-plotting before the Meiji era, the 畝町倒し / サイメ) may describe the line of ditches before reorganization. I did not read it.

Sources:
- [MAFF Kyushu, 佐賀平野のクリーク](https://www.maff.go.jp/kyusyu/seibibu/history/06.html)
- [Geographical Review of Japan B 60(1), Irrigation Systems in Japan (archived)](https://www.jstage.jst.go.jp/article/grj1984b/60/1/60_1_41/_pdf)
- [Mie University paper (lead, not read)](https://mie-u.repo.nii.ac.jp/record/6033/files/AN100738460330008.pdf)