# Plan - feature 282, what is in a threshing yard, and where

Spec: [`spec.md`](spec.md) (FAITHFUL, round 3). Request: [`request.md`](request.md).

## What the research found (homesteads 025 and 505; FR-001, FR-002)

- **The yard at harvest** (025): threshing was done in the yard, on mats; the grain was then dried on mats spread to
  fill the yard (Kitamoto; the Kinki, Shikoku and Kyushu records confirm mat drying but not how much of the yard it
  took); 40-60 mats ordinarily, 100-150 on a large farm; a mat is 3 x 6 ft; husking was indoors. Silent on how the
  mats were laid and on anything else standing in the yard.
- **The rack by the house** (505): racks gathered near the house are named for the changeable-weather San'in coast,
  for threshing within the homestead (one sentence, Nishimura and Makino 1959). The drying method followed the natural
  and social setting over whole regions - deep snow, rainy harvests, wet paddies, and teaching or custom working across
  a prefecture - not a village's choice: no source shows neighboring villages in one climate differing. Silent on which
  side of the house the rack stood. That settled weather keeps racks off the house is our reading (racks were mostly
  built on the fields, entry 500).

## Decisions

- **D1 - the knob is an environment input, never a free roll** (FR-005). `HamletSpec.harvest_weather`, one of
  `settled` | `changeable` (`HARVEST_WEATHERS`), default `settled` (`DEFAULT_HARVEST_WEATHER`) - the regional
  default, declared otherwise on the spec, exactly as `windward` is (feature 261). It is NOT rolled: FR-002 found the
  environment decided, so FR-005 forbids a free roll; not rolling also leaves every other seed draw where it was. The
  plan carries it (`SitePlan.harvest_weather`), the skeleton sets `s._house_racks` and records `meta.harvest_weather`.
  The settlement engine's other maps (villages, towns) read `getattr(self, "_house_racks", False)`: no rack unless a
  generator declares one. Entry 500's drying-method knob is the same choice (FR-005's last clause): 500 now points at
  505 and says the method follows the weather, and no second knob exists. The default is this project's decision
  (the gathered racks are one region's form), labeled so on 505.
- **D2 - the exhibit**. Sawada declares `harvest_weather="changeable"` so the pool shows the rack; the pool's hamlets are
  independent exhibits (Sawada already declares a wind for the same reason). Only Sawada's yards gain racks; the four
  others keep none. Class: this project's decision.
- **D3 - the mats** (FR-004). `_draw_threshing_yard` drops the fixed 14 x 9 ft center mat, the swept-rim line and the
  south rack. The yard's local frame is tiled in cells of 6 x 3 ft (`MAT_FT`, tobunken-mushiro: 3 x 6 shaku), long side
  along the yard's width, inset 1 ft, laid in rows with a 2 ft gap around each (45% of a full cover; the gap closes a step at a time - 1.5, 1, 0.5, then 0 ft - where a small or clipped yard would fall under a third, and is thinned back evenly where the edge-to-edge step overshoots two thirds; a checkered half was tried first and read as pavers), each only if its four
  corners lie inside the yard's quad; the count lands in the band [ceil(full/3), floor(2 full/3)], `full` = the
  yard's area / 18 sq ft - the floor by closing the gap, the ceiling by the even thinning. The
  pure layout is a module-level function `mat_cells(w, h, poly_local, ftpx, keep_out)` so it is tested with plain
  inputs. Rows and the gapped thinning: the rows a GUESS, the thinning a CONVENTION (the GM's words), recorded on 025.
- **D4 - the rack** (FR-006). When `_house_racks`: a module-level `rack_segment(w, h, rot, ftpx, side_pref)` returns the
  rack's centerline in the local frame, or None. Candidates run along the yard's two side edges (the local x = +/-
  edges, inset 2 ft), from the edge facing the house (local north, inset 2 ft) toward the far edge, clipped so that
  (a) they stay in the half nearest the house (local y <= 0) and (b) every corner of the rack's footprint (2.5 ft wide,
  a CONVENTION so it reads) lies in the yard's MAP-north half after the house's rake is applied - the clip is solved
  in map coordinates, so it holds for any rotation, the quarter turns of feature 269 included. The preferred side comes
  from `_hjit` at the yard's center; the other side is tried if the preferred one clips below 4 ft. The half nearest the
  house is our guess and yields before the knob does (plan review round 1): where neither side's near half leaves 4 ft,
  the whole side edge is tried, still held off the map-south half - under any rotation part of one side edge lies
  map-north of the center, so every yard on a changeable-weather map takes a rack (a Sawada test asserts every yard
  has one). Drawn as today's rack glyph (rails + posts every ~6 ft + hung straw),
  turned with the yard. The mats skip cells under the rack's footprint. The manifest's yard record gains `mats` (the
  drawn count) and, when present, `rack` (the footprint's four corners in map coordinates).
- **D5 - the modal** (FR-007). The `threshing yard` class docstring rewritten from 025 and 505: What (a floor of mats
  at harvest, a rack by the house where the harvest weather is changeable), Why, Note/Caveat with the labels (mats
  accurate, the count drawn a CONVENTION in the GM's form with the real 40-60 and 3 x 6 ft, the rows a GUESS, the rack
  knob and its side a GUESS), `Label`, `Entry:` naming 020, 025, 030 and 505.
- **D6 - maps and reviews** (FR-008). Regenerate the five pool hamlets (the glyph changes on all; Sawada also gains
  racks; the layout of no map moves, as nothing placed changes size); `settlement-review` on Sawada (the map whose
  look changes most), gate and review paired as the pair guard requires; `make done`.
- **D7 - the 269 merge**. Feature 269 (diagram-supplemental, unlanded) edits `_attach_yard` (quarter turns). 282 edits
  only `_draw_threshing_yard`, the new helpers and the manifest dict; the rack is solved in map coordinates so it is
  right under a quarter turn. 282 lands after telling 269's session; if 269 lands first, merge main and re-run the
  yard tests.

## Constitution check

- XII (research): every rule labeled - accurate (mats over the yard, the rack by the house in changeable weather),
  convention (the drawn count, the rack's drawn width), guess (the rows, the rack's side and length), this project's
  decision (the settled default, the exhibit).
- XIII (no regressions): baseline in a detached worktree before the gate.
- XVI (the literal thing): mats "over the yard", racks "only in settlements rolled for tall racks" - set by the
  weather as FR-005 requires - and never on the south side.
- Indexing: no new overlap check against placed features (the glyph is drawn inside a reserved rect).
