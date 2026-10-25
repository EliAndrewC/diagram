I ran one search pass over the 64 claim keys in `pass-P2a-hamlet-water.txt`. Only two web sources speak to a claim. A 2013 survey of 153 surviving oblique weirs supports the 30° weir skew. The 1957 Leopold and Wolman river paper contradicts the brook's straight-run allowance (the `RULED_*` constants). The record already held three more relevant passages (meander geometry, Japanese reservoir-pond types, and the Rites of Zhou ditch count) that the engine doesn't yet use. Most of the remaining keys are drawing tolerances that no source could address.

**Ledger gap:** `make source-pages` refused both PDFs ("no text layer can be read here"). The ledger records both attempts, but no copy was saved. I downloaded them with curl and extracted the text with pdftotext, in `/tmp/l7r-pass/leopold-raw/` and `/tmp/l7r-pass/jila461-raw/`. Whoever cites them needs to archive them. I recorded no outcomes, because both pages bear on the question and you record the citation.

## Sources

**1. Murakami Shuichi, "Research on possibilities of landscape at intake points of oblique weirs…", journal of the Japanese Institute of Landscape Architecture** – https://jila-zouen.org/wpdata/wp-content/uploads/2014/04/461.pdf
- **Date of evidence:** 153 oblique weirs still standing, surveyed 2008–2012. The paper treats the oblique weir as the form from before modern times, now disappearing. It measures surviving river weirs, so some may have been rebuilt, and none is a brook weir.
- 「もともと堰の多くは河道に対して直角ではなく斜めの方向に横断する「斜め堰」であったという」 – "originally most weirs were 'oblique weirs', crossing the channel not at a right angle but slantwise" (translation). The PDF's two-column text breaks this sentence apart; I joined the pieces.
- 「斜度は 5 度から 78 度まで分布し，河道に対して直角に近い例から，平行に近い例まで認められる。30 度未満が 85 例と過半数を占め，相対的に斜度の小さい例の方が多い。全事例の平均値は 30 度である。」 – "The skew ranges from 5 to 78 degrees, from cases nearly perpendicular to the channel to cases nearly parallel. 85 cases, a majority, are under 30 degrees, so the smaller skews are the more common. The mean over all cases is 30 degrees." (translation)
- The paper also finds that the regional and plain-versus-mountain means are all close to 30°, with no clear trend.
- Skew here is the angle between the weir line and the perpendicular to the channel. That is the same quantity the engine's `WEIR_SKEW_DEG` measures (`brook.py:684`, an offset of tan 30° from the bank normal).

**2. Leopold & Wolman, "River channel patterns: braided, meandering and straight", USGS Professional Paper 282-B (1957)** – https://pubs.usgs.gov/pp/0282b/report.pdf
- **Date of evidence:** modern field observation. It describes how natural channels form, not a human practice, so the pre-1868/1912 cutoff doesn't apply to it.
- From the OCR text, with its errors kept: 「I n our experience truly straight channels ara so rare among natural rivers as to bt> almost nonexistent. Extremdy short segments or reaches of the channel may be straight, but it can be stated as a generalization thaf, reaches which are straight for distances exceeding ten timss the channel width are rare.」
- It gives one counter-instance: 「For 500 feet this rhannel is straight」 (Valley Creek, Pa.). Even there, "the thalweg wanders back and forth".

**3. Archived English Wikipedia "Meander"** (`.specify/source-archive/72/72b4983d5f42/…/text.txt`; record key meander-enwiki, already cited on page 0054)
- **Date of evidence:** modern geomorphology.
- 「In general the meander length is 10–14 times, with an average 11 times, the fullbank channel width and 3 to 5 times… the radius of curvature at the apex. This radius is 2–3 times the channel width.」
- 「In contrast to sine waves, the loops of a meandering stream are more nearly circular.」
- 「Streams or rivers with a single channel and sinuosities of 1.5 or more are defined as meandering」

**4. Archived Japanese Wikipedia "ため池"** (`24/249382059f96/…/text.txt`)
- **Date of evidence:** a modern description. It dates only the Sayama pond system (17th century).
- 「複数の池が棚状に連なるものを重ね池、または親子池ともよばれている」 – "ponds strung one below another like shelves are called kasane-ike, or parent-and-child ponds" (translation)
- 皿池 are fed 「川や谷池、もしくは他の皿池から用水路を経て引かれてきた水」 – "by water led through irrigation canals from rivers, valley ponds or other sara-ike" (translation)
- The only case of field drainage reused in a lower pond is Sri Lanka: 「上流の余水や排水を下流の池に送って反復利用する」 – "sending upstream surplus and drainage water to the pond below for repeated use" (translation)

**5. The Rites of Zhou, Suiren section** (already in the record, `0055…notes`, zhouli-suiren-wikisource; pre-Han, an ideal scheme)
- 「凡治野：夫間有遂，遂上有徑；十夫有溝，溝上有畛；百夫有洫…」 – "between each fu (one man's allotment) a sui ditch; for ten fu a gou; for a hundred fu a xu" (translation)

## Reading

**ATTESTED** for the weir skew. Surviving oblique weirs average exactly 30° off the perpendicular, with a majority under 30°, which matches `WEIR_SKEW_DEG`. The only caveat is scale: these are river weirs, and none is a brook weir.

**NOT ATTESTED** for the brook's allowed straight runs.
- **The contradiction:** Leopold & Wolman find natural reaches straight for more than ten channel widths "rare". At the record's 7 ft brook (0059.drawing) that is about 70 ft.
- **Where the engine is looser:**
  - The share rule only applies once 300 ft of brook is in view (`RULED_MIN_LEN_FT`), so a shorter brook in view can be straight from end to end.
  - Above that length, up to 0.4 of the brook may be one straight run (`RULED_SHARE`), which is hundreds of feet.
- **The counter-instance:** a single 500 ft straight reach is recorded (Valley Creek), but as the exception.

**ATTESTED ONLY FOR the per-vertex case** on fold-back.
- The per-vertex cap is safe: a bend of radius 2–3 widths (14–21 ft at 7 ft), cut into the engine's 10 ft steps, turns about 30–40° per vertex, so the 100° cap never bites.
- The docstring's reason, "a natural brook does not double back", is contradicted for meandering water: its loops are "more nearly circular", so the heading does reverse over a loop. It holds only for a low-sinuosity brook, and the claim that a steep fan-head brook is low-sinuosity is my own inference, not a source's.

**Tension, not a clean contradiction, on `OFFTAKE_LADDER`.**
- **The record's note:** 0053.notes:30 says the pages read don't count ditches.
- **But the record already holds a classical count:** the Rites of Zhou gives a ditch per allotment and a gou per ten allotments. At 99 households that ideal would give about ten gou, against the engine's 4 offtakes.
- **Why it isn't decisive:** the record itself (0055/0068) reads the Rites as an ideal scheme, and a fu is a land allotment, not a hamlet household.

**SILENT** for everything else, even after this pass. My searches:
- **Archive terms:** meander, sinuosity, 蛇行, 曲流, 斜め堰, 抽水植物, ヨシ帯, 挺水植物, 池塘, 小川, 分水口.
- **Web queries:**
  - 斜め堰 角度 江戸時代, and 山田堰 斜め堰 河道に対して 度, for the weir skew. This search surfaced the Murakami paper, the one source the table cites for the skew.
  - The Leopold "ten channel widths" query, which surfaced paper 2.
  - 陂塘 退水 回归水 塘堰 承接, 落ち水 ため池 反復利用, and ため池 ヨシ 群落 幅 水深, for drain-fed ponds and the reed fringe. These found nothing beyond modern lake reed-planting depths and cascade overflow, with no premodern drain-fed pond and no fringe width.

## One row per claim key

| Key | Status |
|---|---|
| consts_water::BROOK_MAX_TURN_DEG | ANSWERED, ATTESTED ONLY FOR the per-vertex cap (Meander archive: radius 2–3 widths). **Flag:** "never doubles back" is contradicted at loop scale for meandering water |
| consts_water::BROOK_SKIRT (34 ft) | RECORD-SILENT-BEFORE: 0059.drawing ("leaving the stream its margin", no figure); 0073.drawing ("natural streams take no margin"). Not searched on the web |
| consts_water::BROOK_WANDER (10 ft) | SEARCHED-SILENT for amplitude. Scale only: wavelength about 11 widths (about 77 ft), radius 2–3 widths |
| consts_water::BROOK_WANDER_STEP (10 ft) | NOT-ABOUT-THE-WORLD (the walk's step size). Scale as in the row above |
| consts_water::OFFTAKE_LADDER | RECORD-SILENT-BEFORE: 0053.notes:30. **Tension:** the Rites of Zhou count (an ideal scheme) is held at 0055.notes:29/47 but not applied |
| consts_water::POND_SETBACK_LIMIT (300 ft) | RECORD-SILENT-BEFORE: 0060.notes:43 and 0053.drawing.notes:21 (no drain-fed pond described). SEARCHED-SILENT (this pass) |
| consts_water::SINKS (2/3 pond) | RECORD-SILENT-BEFORE: 0060.drawing GUESS. SEARCHED-SILENT (this pass); cascades held for Japan only, field-drain reuse for Sri Lanka only |
| sink::BROOK_JOIN_DESCENT | NOT-ABOUT-THE-WORLD (0060.drawing calls the drain-to-brook join "the map's rule rather than the record's") |
| sink::BROOK_JOIN_LEAD | NOT-ABOUT-THE-WORLD |
| sink::SINK_FRINGE (44 ft) | RECORD-SILENT-BEFORE: 0061.drawing (fringe present, no width; plants sorted by depth in mineta-2007). SEARCHED-SILENT (this pass) |
| sink::_through_the_crop | NOT-ABOUT-THE-WORLD |
| sink::brook_join (join reach 420 ft) | RECORD-SILENT-BEFORE: 0060.drawing ("where the passing brook comes near", map's rule, no figure) |
| sink::brook_join (nearest fallen point, off the crop) | NOT-ABOUT-THE-WORLD (routing rule; downhill-only already in 0060.drawing) |
| sink::hull_route (12 ft) | NOT-ABOUT-THE-WORLD |
| sink::lay_sink (no building, 10 ft) | Not searched by the record or this pass (a world question: houses' distance from a pond). Lead |
| sink::lay_sink (reed fringe width) | As SINK_FRINGE: RECORD-SILENT-BEFORE, SEARCHED-SILENT |
| sink::pond_seat (set-back limit) | As POND_SETBACK_LIMIT |
| sink::pond_seat (sways 0.9/1.8) | NOT-ABOUT-THE-WORLD |
| sink::pond_setback (margins) | NOT-ABOUT-THE-WORLD |
| sink::route_refusals | NOT-ABOUT-THE-WORLD (routing rule) |
| brook::approach_legs (approach bow) | NOT-ABOUT-THE-WORLD |
| brook::approach_legs (approach wobble) | NOT-ABOUT-THE-WORLD |
| brook::approach_legs (intake reach) | NOT-ABOUT-THE-WORLD |
| brook::around_the_field (clearance) | As BROOK_SKIRT |
| brook::bend_at | NOT-ABOUT-THE-WORLD |
| brook::bend_runs | NOT-ABOUT-THE-WORLD (implements the straight-run rule; see RULED_*) |
| brook::brook_skirt (corners cut) | NOT-ABOUT-THE-WORLD |
| brook::brook_skirt (crop clearance) | As BROOK_SKIRT |
| brook::brook_skirt (head crop yields) | NOT-ABOUT-THE-WORLD |
| brook::brook_skirt (meander, 16 stations) | NOT-ABOUT-THE-WORLD |
| brook::brook_skirt (tap run, 70 px) | RECORD-SILENT-BEFORE: 0059.notes:53 (no intake-to-first-division distance) |
| brook::brook_violations (no fold-back) | As BROOK_MAX_TURN_DEG |
| brook::brook_violations (no ruled run) | ANSWERED, Leopold & Wolman: straight runs over 10 widths are rare. The rule's direction is right; its bound is too loose (see RULED_*) |
| brook::chord_offsets | NOT-ABOUT-THE-WORLD |
| brook::clear_of_field (step) | NOT-ABOUT-THE-WORLD |
| brook::draw_intake (weir skew 30°) | ANSWERED, Murakami: mean 30°, range 5–78°, majority under 30° |
| brook::feed_brook (approach bearing) | NOT-ABOUT-THE-WORLD |
| brook::round_the_field (approach bow) | NOT-ABOUT-THE-WORLD |
| brook_course::EXIT_BEND_FRAC | NOT-ABOUT-THE-WORLD |
| brook_course::EXIT_BEND_MAX_FT | NOT-ABOUT-THE-WORLD |
| brook_course::_v_within | NOT-ABOUT-THE-WORLD |
| brook_course::_wander (meander) | As BROOK_WANDER: SEARCHED-SILENT for amplitude |
| brook_course::exit_bend | NOT-ABOUT-THE-WORLD |
| brook_course::exit_legs (exit leg bend) | NOT-ABOUT-THE-WORLD |
| brook_course::exit_legs (exit span) | NOT-ABOUT-THE-WORLD |
| brook_course::exit_legs (turn onto the fall) | NOT-ABOUT-THE-WORLD |
| brook_course::unfold (no fold-back) | As BROOK_MAX_TURN_DEG |
| brook_rules::RULED_MIN_LEN_FT (300 ft) | ANSWERED, **CONTRADICTED** by Leopold & Wolman: about 10 widths (about 70 ft) |
| brook_rules::RULED_SHARE (0.4) | ANSWERED, **CONTRADICTED** by Leopold & Wolman (allows runs far past 10 widths) |
| brook_rules::RULED_TOL_FT (3.1 ft) | SEARCHED-SILENT (the paper defines straightness by sinuosity, with no tolerance) |
| brook_rules::ruled_share_ok | As RULED_SHARE, **CONTRADICTED** |
| brook_rules::straightest_chord | ANSWERED, Leopold & Wolman (supports holding a natural brook off long straight runs) |
| brook_rules::straightest_run | ANSWERED, Leopold & Wolman (as above) |
| comb::stage_field (30 px ditch corridors) | RECORD-SILENT-BEFORE for village ditches. ATTESTED ONLY FOR a great aqueduct: Tamagawa notice of 1739, tree rows protected 3 ken (about 18 ft) each side (0055.notes:49). 0022.drawing gives an 8 ft ditch corridor inside a polder |
| fit::HEAD_OFFSETS | RECORD-SILENT-BEFORE: 0059.drawing.notes:51 |
| fit::_fit_at_aspect (fan proportions) | NOT-ABOUT-THE-WORLD (taken from the project's authored Ikegami map, not a source) |
| fit::head_sluice (head set-back 0.36) | NOT-ABOUT-THE-WORLD |
| fit::head_sluice (intake offset) | As HEAD_OFFSETS |
| polder::_nearest_pair (block aspect band) | NOT-ABOUT-THE-WORLD (Enokida, an authored map) |
| polder::dike_face | RECORD-SILENT-BEFORE: 0073.drawing ("reeds ran up to the dike is a GUESS") |
| polder::fit_polder (block aspect) | NOT-ABOUT-THE-WORLD (Enokida, an authored map) |
| polder::polder_crossing_caps | RECORD-SILENT-BEFORE: 0035.drawing (crossing spacing a GUESS). Not searched |
| polder::stage_polder (ditch corridors) | As comb::stage_field |
| polder::stage_polder (reservoir size) | RECORD-SILENT-BEFORE (per the claim's own text: 0061, 0017, 0019, 0020) |

**Contradicted figures:** `RULED_MIN_LEN_FT`, `RULED_SHARE` and `ruled_share_ok` (Leopold & Wolman), and the "never doubles back" rationale for meandering water (Meander archive).

## Leads not followed
- Murakami's Table 3 gives weir length and river width per case. It may give a skew trend by river width that would show what applies at brook scale.
- Leopold & Wolman figure 41 (Valley Creek): its channel width wasn't extracted, so the 500 ft straight reach can't yet be counted in widths.
- How far houses stood from a pond or brook (`lay_sink`, `BROOK_SKIRT`): neither the record nor this pass searched it.
- The Sri Lanka drainage-reuse ponds are cited to the ja.wiki ため池 article's note 17. A China/Japan counterpart might be under 塘 串联 or 連珠式 in Chinese pond-irrigation histories.
- A Japanese 蛇行 or 河道 survey of small streams could give how sinuous a fan-head brook is, to settle the fold-back rationale for steep water.

Sources:
- [Murakami, oblique weir intakes (JILA 461.pdf)](https://jila-zouen.org/wpdata/wp-content/uploads/2014/04/461.pdf)
- [Leopold & Wolman 1957, USGS PP 282-B](https://pubs.usgs.gov/pp/0282b/report.pdf)
- [USGS publication page, PP 282-B](https://pubs.usgs.gov/publication/pp282B)