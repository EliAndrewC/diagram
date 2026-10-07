# Tasks: the implementation brought to the research, easiest first (feature 328)

**Input**: plan.md (Phase 1, Phase 2, D1-D4). Only the CURRENT wave's rows are task boxes (spec FR-006); the rest of the
ranking is data in `ranking.json` / `ranking.md`, and the next wave is appended here as an amendment once this one lands.

## Occasions

- none: wave 1 changes `Research:` claim lines only (tier E0) - nothing a map draws or where it is placed moves.
- placement-changed: village lane - wave 4 brings the lane law to 0081 and 0246 (7 ft clear of a fence, ends joined
  within 25 ft, tails and hooks cut at 40 and 12 ft): the lanes are re-placed by substantially different rules.
- none (wave 2): each fix moves one value inside a rule that already places the element (a weight, a pitch, a share, a
  count's cap, an extent); no element is new to a map, no glyph is redrawn, and no element is re-placed by different rules.
- none (wave 5): each fix moves one value inside a rule that already places the element (a reach or a corridor in feet, a
  seat weight, a size band, a crown floor, a share, a cap); no element is new to a map, no glyph is redrawn, and no element
  is re-placed by different rules.

## Phase 1 - the audit

- [x] T01 the findings snapshot: `findings.json` = every finding of `make claims-report` at `a52ff1bcd` (565) (FR-001)
      research: rendering
      verify: DONE. findings.json: 565 findings (DRIFTED 439, MISLABELED 50, UNCLAIMED 36, NEEDS-RESEARCH 20, CANNOT-TELL 20) from dev/claims-index.json at a52ff1bcd
- [x] T02 the nine ranking batches, one Opus agent each, read-only, from `ranking-brief.md`; every finding tiered E0-E4 with its fix, files and dependencies (FR-002, FR-003)
      research: rendering
      verify: DONE. nine Opus batches (47-76 rows) returned 565 rows, each once (merge.py checked missing/extra = 0); 26 flagged deviation-tempting
- [x] T03 the merge: `ranking.json` in tier order (by module within a tier, dependencies after what they wait on), `ranking.md` generated; E0 rows outside the bounded E0 re-tiered; `tests/test_328_ranking.py` green (FR-001, SC-001)
      research: rendering
      verify: DONE. ranking.json 565 rows: E0 60, E1 162, E2 169, E3 136, E4 38; 30 flagged deviation-tempting. The 30 E0 rows tiered on the unbounded wording re-checked bounded (audit/e0review-out.jsonl): 23 stay E0 with a quoted e0_basis, 7 re-tiered; the shops-face-the-street row moved to E3 (its basis was a recorded DEVIATION, FR-004). Reproducible: python3 audit/merge.py audit . ; tests/test_328_ranking.py 2 passed
- [x] T04 the second reader: 30 rows sampled across tiers re-tiered blind by a fresh Opus reader; a batch disagreeing by more than one tier on more than 5 rows is re-run (plan D4)
      research: rendering
      verify: DONE. 30 rows (6 per tier, seed 328) re-tiered blind: 25/30 exact; 4 off by more than one tier (batches 8, 8, 5, 9) - no batch over 5, so none re-run (plan D4); for the 2 where the second reader ranked higher, the higher taken (audit/overrides.json)

## Phase 2 - wave 1 (tier E0: the claim alone)

- [x] T05 every E0 row's claim corrected to what the implementation already matches, module by module; `make claims-owed` lists them; each re-checked by `impl-drift` from `make claims-bundle` and recorded with `make claims-checked`; every one IN-STEP (FR-004, FR-005, SC-002)
      research: rendering
      verify: DONE. 56 of 57 E0 rows closed IN-STEP by impl-drift (audit/waves.json, from the claims index); 3 rows moved down when the re-check found a code mismatch (the rank step, the merchant kura, the universal shrine sheet - audit/overrides.json); three rounds of claim corrections (113 + 46 + 12 + 1 claims re-checked, bundles 1-8); 15 found rows added (audit/found-wave1.jsonl). Findings 565 -> 523.
- [x] T06 the wave's close: `make claims-report` shows the E0 rows gone and no new finding; `make done` green; `ranking.json` rows marked wave 1; landed (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. make claims-report: 5,934 claims, findings 565 -> 518 (DRIFTED 437, MISLABELED 28, UNCLAIMED 20, NEEDS-RESEARCH 20, CANNOT-TELL 13 at the close; owed 0); no finding introduced beyond the 7 named in claims-followup.md (ranked as found rows); make done green (174 s); ranking.json wave column set from the index

## Phase 3 - wave 2 (tier E1: one value) - amendment 1, 2026-10-07

Wave 2 takes the first sixteen E1 rows of `ranking.json`, less the row pitch and the brook's weight (see below), (the eight procedure fixes that change only the procedure's
own text, and eight single values of the hamlet generator outside its lane code). The E1 row
`hamletgen/consts.py::FOOTPATH_FABRIC_GAP` waits for wave 4 (the lane law): it is the same constant as the lane-law rows, and its
`after` names `ways/bund.py::RunOnBlocks.clear#off the steadings` (spec SC-003). No row of this wave redraws a sheet.

The row pitch (`hamletgen/consts.py::BUNDLE_PITCH`, 100 -> 0038's 92 ft) left the wave on measurement (2026-10-07): at
92 ft Kuwabata's lanes 3 and 8 zigzag across a joint that the engine's joint pass cannot repair (the T's foot falls on
the joint from both sides; both links that would drop the 36 ft jog skirt a steading and are refused). Held at 100 with
the regression gone, it now waits (`after`) for the found row that re-routes such a joint (E3).

The brook's weight (`hamletgen/cluster.py::seat_cluster#brook penalty weight`, 3.0 -> 0035's tiebreak) left the wave on
measurement (2026-10-07, the closing bookend): at 0.05 the 10-household seed 4 seated astride its brook and the settled
web left ten farmhouses off the network (`WebRefused`); restoring 3.0 alone, of the wave's values, rolls it. Held at 3.0
(`cluster.py` as on main), it waits for the found row that lets the web reach a cluster its brook crosses (E3). The rows:

  - `buildings.md::Fire-water tubs#tub glyph` - procedure's tub glyph r5 -> r~3.8 (2.5 ft across); sheets already draw r3.8
  - `buildings.md::Outer court (administrative / public)#archery bank` - archery lane drawn per 0164's yaba ~250 x 8 ft with the azuchi at its end, not ~90 ft (no sheet draws one)
  - `buildings.md::Sacred features#grove crown size` - grove crowns 13-24 ft (0080.drawing's 0.75-1.4 x 17 ft), cited to 0080's drawing page as a guess
  - `buildings.md::Scale#main gate passage width` - Scale section's main-gate passage made the two forms (yakuimon ~6-8.5 ft, nagaya-mon ~12 ft), dropping '~10-13 ft, ~40 px'; sheets already comply
  - `buildings/programs.md::Country shrine (a village district's shrine)#basin beside the approach` - procedure basin sentence: drop 'from Nikko in 1636'; the one pre-1868 pavilion found is Yakyu Inari's (1836), a village's plain basin attested (Nagao 1828)
  - `buildings/programs.md::Country shrine (a village district's shrine)#farmers' stage knob` - procedure knob 6: replace 'none in thirteen' with the record's 1,777 stages nationwide (lost stages and noh/puppet stages included); absent by default stands
  - `buildings/programs.md::Country shrine (a village district's shrine)#precinct size` - procedure precinct sentence: replace the stale 'one Edo set ... 60-240 tsubo' with Saga's Edo returns (lower part of 150-650) and Kami-Nerima 1821 (~10 to ~3,350 tsubo), plus 'a register can also overstate'
  - `buildings/programs.md::Magistrate's manor (county magistracy)#posting wealth knob` - the procedure calls the poor end's look a GUESS (0091 drawing: no page describes how a short-funded office looked); only the shortfall is attested
  - `l7r/diagram/hamletgen/hinterland/parcels.py::WET_SHARE_CAP#woods mostly on dry ground` - WET_SHARE_CAP 0.5 -> ~0 (0077: low ground by a river or marsh is left to grass, not wood)
  - `l7r/diagram/hamletgen/hinterland/parcels.py::open_ground_patches#mostly dry` - same constant: woodland parcels on dry ground only, WET_SHARE_CAP -> ~0
  - `l7r/diagram/hamletgen/homesteads/farm_water.py::farm_channel#where the channel ends` - cap the channel's end at one step (~6 ft) off the threshing yard, not up to 3.5 steps (21 ft)
  - `l7r/diagram/hamletgen/homesteads/fixtures.py::_PRIVY_SEATS#four privy seats` - privy seat weights to stable 35, yard 30, front 20, barn 15
  - `l7r/diagram/hamletgen/homesteads/wells.py::_WELL_DRAWN_R#wellhead drawn extent` - take the drawn extent from the glyph's vr (12.376 ft roof half-size, `_well_vr`) and fix the docstring's 16 px
  - `l7r/diagram/hamletgen/homesteads/wells.py::well_target#how many wells` - cap a hamlet's well count at two (min(2, round(households/6)))
- [x] T07 the bookend and the baseline before the first edit: `make perf LABEL=328-w2-start` on the clone while its engine content is main's (0cb60fb5e, nothing edited); that unmodified tree's green gate is the baseline each regression is judged against (plan Phase 2, constitution VI, XIII)
      research: rendering
      verify: DONE. 328-w2-start taken on the clone at main's engine content (0cb60fb5e, nothing edited): total 16.6s, median 3.9s, worst 5.1s (dev/perf-log 20261007T050851Z); the baseline tree's gate green at wave 1's landing
- [x] T08 the eight procedure rows: each sentence or figure in `buildings.md` / `buildings/programs.md` brought to its page; a row whose fix turns out to need a sheet redrawn moves to E3 and says so (FR-003, FR-004, FR-009)
      research: rendering
      verify: DONE. the eight procedure rows brought to their pages (tub r3.8, archery lane 250 x 8 ft, grove crowns 13-24 ft, the gate's two forms, the basin, the stage count, the Edo precincts, the poor posting a GUESS); none needed a sheet; each re-checked IN-STEP (wave 2 bundles 1-4)
- [x] T09 the eight generator values, each with the unit tests it moves, proven first on the reference hamlet (Inashiro) and then across the pool (FR-004, FR-005)
      research: rendering
      verify: DONE. six generator values landed (wet share 0, the channel one step, the privy seats in the page's order, the wellhead's extent from its glyph, at most two wells, WEB_REACH_FT decoupled at 0246's 100 ft); two rows held back on measurement and now wait for found E3 rows: the row pitch (at 92 a Kuwabata joint Z'd) and the brook's weight (at 0.05 the 10-household seed 4 refused); Inashiro looked at; the pool regenerated by the gate
- [x] T10 every unit the wave touched re-checked by `impl-drift` (`make claims-owed` -> bundles -> `make claims-checked`); each wave-2 row IN-STEP; anything the re-check finds ranked as a found row (FR-005, SC-002)
      research: rendering
      verify: DONE. every touched unit re-checked: 271 + 102 + 60 + 16 claims over bundles 1-11; all 14 wave-2 rows IN-STEP (audit/waves.json); what the re-checks found is ranked (audit/found-wave2*.jsonl) and listed in claims-followup.md
- [x] T11 the close: `make perf LABEL=328-w2-end` and the band's records; `make done` green; `ranking.json` wave column; `make claims-report` falls by the wave's rows with nothing introduced beyond a follow-up note; landed (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. 328-start -> 328-end band 1 (total -1.2%; 20-household seed 4 +0.7 s and 10-household seed 25 +0.2 s, both from the privy seats in 0047's order, measured by perf-audit's control and confirmed consistent); make done green (172 s); 14 wave-2 rows IN-STEP in ranking.json's wave column; the findings the re-checks exposed are found rows, listed in claims-followup.md

## Phase 4 - wave 3 (tier E0: the claim alone, the found rows) - amendment 2, 2026-10-07

Thirty-nine E0 rows stand open: 38 found rows the re-checks of waves 1 and 2 ranked (tiered provisionally by verdict: a
MISLABELED claim or an UNCLAIMED decision), and wave 1's one unclosed E0 row (`taxonomy.py::_OVERLAP_EXEMPT#annexes abut
their house`, T05's "56 of 57"). Tier order (SC-003) takes them before the rest of E1. Each is re-tiered on reading: a row
whose fix is more than the claim line moves to the tier it takes and says so (FR-003's bounded E0). Occasions: none - claim
lines only. The rows:

  - `buildings.md::Fire-water tubs#a tub never on a well glyph; moved to another eaves corner`
  - `buildings.md::Fire-water tubs#tub against its wall`
  - `buildings.md::Fire-water tubs#tub clear of the footprint`
  - `buildings.md::Outer court (administrative / public)#cell kept well under the barracks`
  - `buildings.md::Outer court (administrative / public)#granary kept under a residence block`
  - `buildings.md::Outer court (administrative / public)#practice ground area`
  - `buildings.md::Outer court (administrative / public)#practice ground placement`
  - `buildings.md::Outer court (administrative / public)#practice ground shared with cart staging or muster`
  - `buildings.md::Outer court (administrative / public)#practice ground weapon rack`
  - `buildings.md::Outer court (administrative / public)#stable below barracks`
  - `buildings.md::Outer court (administrative / public)#tax archive drawn with white-plaster fill, heavy stroke and dark door mark`
  - `buildings.md::Sacred features#a fence round the sanctuary alone as a wealth knob (0223 §171-172 finds such fences before 1868 only where the shogunate or a lord built them)`
  - `buildings.md::Sacred features#grove inside a compound wall`
  - `buildings.md::Sacred features#the whole sacred complex held to at most ~2/3 of the residence`
  - `buildings/programs.md::Country shrine (a village district's shrine)#a well as the purification stop beside the approach ("the well or basin"; the required item is `well`)`
  - `buildings/programs.md::Country shrine (a village district's shrine)#approach width about 10 ft`
  - `buildings/programs.md::Country shrine (a village district's shrine)#bell tower band 6-16 by 6-16 ft`
  - `buildings/programs.md::Country shrine (a village district's shrine)#dwelling privy`
  - `buildings/programs.md::Country shrine (a village district's shrine)#kitchen garden by the sun`
  - `buildings/programs.md::Country shrine (a village district's shrine)#sacred tree drawn as the biggest crown in the precinct`
  - `buildings/programs.md::Magistrate's manor (county magistracy)#a detached guest house at a rich posting (0091's drawing page records it as a GUESS)`
  - `buildings/programs.md::Magistrate's manor (county magistracy)#formal visitors and the privacy baffle`
  - `buildings/programs.md::Magistrate's manor (county magistracy)#upland granary strongbox role`
  - `buildings/programs.md::Magistrate's manor (county magistracy)#wells by use`
  - `l7r/diagram/hamletgen/cluster.py::seat_cluster#not in the reed fringe`
  - `l7r/diagram/hamletgen/cluster.py::seat_cluster#the seat center set dep + 12 ft out from the field margin`
  - `l7r/diagram/hamletgen/hinterland/parcels.py::open_ground_patches#a ring with room for fewer than 5 crowns is refused as a wood`
  - `l7r/diagram/hamletgen/hinterland/parcels.py::open_ground_patches#commons legibility floor: a ring under 120 ft is dropped rather than drawn smaller (fewer, never smaller)`
  - `l7r/diagram/hamletgen/homesteads/farm_water.py::farm_channel#how far a channel's source is sought: 20 ft steps, 60 ft spread, widened fourfold`
  - `l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#a footpath's room off the outline`
  - `l7r/diagram/hamletgen/homesteads/wells.py::place_wells#grove farms take their own water and are left out of the communal wells`
  - `l7r/diagram/hamletgen/homesteads/wells.py::place_wells#no well seated over a household's reserved wood-floor seats`
  - `l7r/diagram/hamletgen/ways/serve.py::_lay_web_lane#no way drawn twice`
  - `l7r/diagram/hamletgen/ways/serve.py::shadowed_by#no way drawn twice`
  - `l7r/diagram/hamletgen/ways/web.py::_lay_skeleton#clear of crop, wet and water`
  - `l7r/diagram/hamletgen/ways/web.py::stage_web#a web lane's span`
  - `l7r/diagram/hamletgen/ways/web.py::stage_web#door path reach`
  - `l7r/diagram/hamletgen/ways/web.py::stage_web#web lanes off the hard ground`
  - `l7r/diagram/overlap/taxonomy.py::_OVERLAP_EXEMPT#annexes abut their house`
- [x] T12a the 13 open found rows tiered provisionally above E0 (six E2, one E3, six E4, by verdict) read and tiered by the work they take (FR-002, FR-003), before any E1 wave chooses its rows - a row easier than its provisional tier moves down, and an E0 or E1 row it becomes joins this wave or the next E1 wave in order (SC-003)
      research: rendering
      verify: DONE. the 13 provisional rows tiered by their work by a fresh Opus reader (audit/t12a-out.jsonl): E0 1, E1 3, E2 3, E3 4, E4 2; the E0 row (line follows its bounds) taken into this wave and closed
- [x] T12 every row read and either its claim corrected (cite the page that already says what the code does, relabel, or claim the undecided decision) or re-tiered with the reason; each corrected claim re-checked by `impl-drift` and IN-STEP (FR-003, FR-004, FR-005)
      research: rendering
      verify: DONE. 39 rows read: 33 closed IN-STEP (24 corrected claims, 9 renamed or split and their parts re-checked), 6 re-tiered on reading with the reason (audit/overrides.json, found-wave3.jsonl); five re-check rounds (bundles 1-5)
- [x] T13 the close: `make done` green; the wave column set from the index; landed (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. make done green; the wave column set from the index (audit/waves.json); the claims gate lists nothing introduced; findings 553 -> 525

## Phase 5 - wave 4 (three E0 claims, four E1 rows ahead of the lane law, then the lane law's E1 rows of `hamletgen/ways/`) - amendment 3, 2026-10-07

The three open E0 rows (undecided decisions in the lane code and the seating) come first (SC-003); then four E1 rows
outside the lane code that rank ahead of it (T12a's re-tiered rows and one wave-3 found row, none waiting on another):

  - `buildings.md::Outer court (administrative / public)#cell` - procedure's Cell bullet: '1-2 occupants' becomes 'shared by several prisoners' (0096's measured cells); the 12 x 10 ft footprint stands
  - `buildings/programs.md::Country shrine (a village district's shrine)#building size anchors` - the hall-and-dwelling band_ft 18-38 becomes ~21-35 ft (0222's attested halls) in types.json and the programs.md table; the 46x28 dwelling's claim relabeled GUESS 0221 drawing
  - `l7r/diagram/hamletgen/cluster.py::seat_cluster#band on the canvas` - lat from band_extent is the band's HALF-length (dep/lat are the ellipse's semi-axes), so the frame test uses lat (half the band's length) not lat*0.5, with plan.seat_room's lat*0.5 term matched
  - `buildings/programs.md::Country shrine (a village district's shrine)#a well as the purification stop beside the approach ("the well or basin"; the required item is `well`)` - the program's required purification item becomes the stone basin beside the approach (0222), not a well; the claim cites 0222

and then the 37 E1 rows of the lane law: 33 held together since amendment 1 (plan D6's 32 in `ways/` and
`FOOTPATH_FABRIC_GAP`) and 4 the re-checks found since (the row street, a web lane's span, the door path, the orphan stub). One rule set:
0246's lane middle 7 ft clear of a garden fence, 0081's ends joined within 25 ft, a tail under 40 ft past a crossing cut, a
hook of 12 ft turning 90 degrees or more cut, a lane end serving a house within 60 ft. A row whose map fails the gate in a
way that takes more work than its tier takes that tier and waits on a found row (Edge Cases). The rows:

  - `l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#front-row standoff from the field set by the homestead core's reach (house, yard, shed, well pocket; garden excluded)` - claim the front-row standoff by the homestead core's reach
  - `l7r/diagram/hamletgen/ways/web.py::_lay_skeleton#skeleton arm clipped WEB_FABRIC_GAP (7 ft) off the steadings and trimmed back to the last point serving a house` - claim the skeleton arm's 7 ft fabric clip and its trim (0246)
  - `l7r/diagram/hamletgen/ways/web.py::stage_web#web lanes routed round the households' reserved wood seats as fabric` - claim the wood seats as fabric the web routes round
  - `l7r/diagram/hamletgen/ways/bund.py::RunOnBlocks.clear#off the steadings` - FOOTPATH_FABRIC_GAP 4 -> 7 ft (lane middle at least 7 ft off a garden fence, 0246)
  - `l7r/diagram/hamletgen/consts.py::FOOTPATH_FABRIC_GAP#footpath off a plot` - FOOTPATH_FABRIC_GAP 4.0 -> 7.0 (0246: a lane's middle at least 7 ft from a garden fence, footpath included)
  - `l7r/diagram/hamletgen/ways/clearance.py::clear_runs#threads between steadings` - clear_runs default tight_margin 6.0 -> 7.0 (WEB_FABRIC_GAP)
  - `l7r/diagram/hamletgen/ways/corridors.py::FIELD_ROUTE_GAP_FT#field way off the steadings` - FIELD_ROUTE_GAP_FT 5.5 -> 7 ft centerline off gardens
  - `l7r/diagram/hamletgen/ways/fabric.py::_draw_web#web lane's no-build corridor` - WEB_CLEARANCE 28 -> 18 ft, the lane's room between homesteads (0246)
  - `l7r/diagram/hamletgen/ways/fabric.py::_hits_a_steading#no house on a tread` - drop the 2 ft pad: a house corner is tested against half the tread only (0246 no corner on the tread)
  - `l7r/diagram/hamletgen/ways/fabric.py::house_hit#no house on a tread` - house_hit window half the tread, no 2 ft pad
  - `l7r/diagram/hamletgen/ways/joints.py::_MEET_FT#ends that nearly meet` - _MEET_FT 11.5 -> 25 ft (0081 ends within 25 ft joined)
  - `l7r/diagram/hamletgen/ways/joints.py::meet_end_to_end#ends that nearly meet are joined` - meet_end_to_end joins ends within 25 ft
  - `l7r/diagram/hamletgen/ways/law.py::JOIN_REACH_FT#a join that stops short` - _LANE_JOIN_FT (JOIN_REACH_FT) 30 -> 25 ft (0081)
  - `l7r/diagram/hamletgen/ways/checks.py::lanes_share_tread#one network at 40 ft` - treads count as joined only within the 25 ft join reach (0081), not 40 ft
  - `l7r/diagram/hamletgen/ways/law.py::connector_hairpin_ends#no hairpin at the track` - connector_hairpin_ends returning-leg figure 25 -> 40 ft (0081 section 1342)
  - `l7r/diagram/hamletgen/ways/law.py::fouls_fabric#foul margin` - _TOUCH_GAP 4 -> 7 ft off another's yard or garden (0246 lane middle 7 ft off a fence)
  - `l7r/diagram/hamletgen/ways/clearance.py::may_write#no nearer the fabric` - may_write bar max(_TOUCH_GAP, w/2+2) -> 7 ft off garden/yard fabric
  - `l7r/diagram/hamletgen/ways/clearance.py::_clear_touch#junction link margin` - _clear_touch margin off yards and gardens 4 -> 7 ft (_TOUCH_GAP, 0246)
  - `l7r/diagram/hamletgen/ways/law.py::near_misses#ends that nearly meet are joined` - near_misses uses the 25 ft join reach
  - `l7r/diagram/hamletgen/ways/law.py::span_walkable#a walkable span` - span_walkable keeps yards and gardens 7 ft off the line
  - `l7r/diagram/hamletgen/ways/settle.py::fouled_segment#off another household's yard or garden` - fouled_segment fouls a tread within 7 ft of another's yard or garden
  - `l7r/diagram/hamletgen/ways/smooth.py::_END_HOUSE_FT#lane end reaches a house` - _END_HOUSE_FT 90 -> 60
  - `l7r/diagram/hamletgen/ways/geom.py::_trim_to_service#an outlying house keeps its way` - _trim_to_service keeps an end serving a keep house only within 60 ft (or 12 ft of built ground), not WEB_REACH_FT 100
  - `l7r/diagram/hamletgen/ways/smooth.py::_END_WAY_FT#lane end reaches a way` - _END_WAY_FT 40 -> 60
  - `l7r/diagram/hamletgen/ways/smooth.py::_LONG_ARM_FT#hairpin arm cut length` - _LONG_ARM_FT 90 -> 40
  - `l7r/diagram/hamletgen/ways/sweeps.py::_FREE_STUB_FT#free-end stub past a kink` - free-end stub cut aligned to 0081: last leg 12 ft or less turning 90 deg or more (_FREE_STUB_FT 20 -> 12, kink 50 -> 90)
  - `l7r/diagram/hamletgen/ways/sweeps.py::_PAST_CONNECTOR_FT#overrun past the connector` - _PAST_CONNECTOR_FT 80 -> 40 (0081 tail under 40 ft past a crossing)
  - `l7r/diagram/hamletgen/ways/sweeps.py::_ROUTE_JOIN_FT#wide ends joined` - _ROUTE_JOIN_FT 30 -> 25
  - `l7r/diagram/hamletgen/ways/sweeps.py::_bridge_collinear_breaks#a short gap closed at any bearing` - any-bearing bridge band uses the 25 ft join reach
  - `l7r/diagram/hamletgen/ways/sweeps.py::_bridge_collinear_breaks#bridge clearance fallback` - bridge clearance fallback 4 -> 7 ft line off fabric (no lower fallback)
  - `l7r/diagram/hamletgen/ways/sweeps.py::cut_past_connector#overrun past the connector cut` - cut_past_connector cuts tails under 40 ft
  - `l7r/diagram/hamletgen/ways/sweeps.py::trim_free_stub#only a free-end stub of 20 ft or less (_FREE_STUB_FT) is cut` - claim the stub cut citing 0081 a lane's end loses its hook once aligned
  - `l7r/diagram/hamletgen/ways/touch.py::_touch_junctions#join reach` - _touch_junctions reach 25 ft on every pass (30 and final 48 -> 25)
  - `l7r/diagram/hamletgen/ways/track.py::_thread_the_fabric#gap off the steadings` - TRACK_FABRIC_GAP 16 -> 7 ft (0246 lane middle 7 ft off a fence)
  - `l7r/diagram/hamletgen/ways/geom.py::push_clear_of_fabric#gateway clearance` - TRACK_FABRIC_GAP 16 -> 7 ft in push_clear_of_fabric (0081/0246 lane-to-fence clearance)
  - `l7r/diagram/hamletgen/ways/web.py::stage_web#a row street trimmed to end at its outermost door-path joint or last farm door` - the row street runs on off the map as the road into it (0033 drawing), not trimmed at its last farm's path - with the lane law
  - `l7r/diagram/hamletgen/ways/web.py::stage_web#a web lane's span` - a back lane's span held to the houses it serves, within WEB_REACH_FT (100 ft, 0246), not 1.5 x WEB_REACH_FT (150 ft); the claim cites 0246
  - `l7r/diagram/hamletgen/ways/web.py::stage_web#back lane tie spacing` - stage_web passes 1.5 x BUNDLE_PITCH to web_cuts so ties stand about 300 ft apart
  - `l7r/diagram/hamletgen/ways/web.py::stage_web#door path distance` - DOOR_REACH_FT 40 ft brought to 0246 drawing's GUESS for a way reaching a farmhouse (within 60 ft of the house, or 12 ft of its built ground), the claim citing it
  - `l7r/diagram/hamletgen/ways/web.py::stage_web#orphan stub joined` - an orphan stub joined only within 0081's 25 ft join reach, not _STUB_REACH_FT 48 ft (with the lane law, wave 4)
- [x] T14 the bookend before the first edit: `make perf LABEL=328-start` re-taken on the clone at main's engine (the wave's own pair) (constitution VI)
      research: rendering
      verify: DONE. 328-start taken on the clone at main's engine after waves 2-3 landed, before any wave-4 edit: total 16.4s, median 4.0s, worst 4.9s, no seed refused
- [x] T15 the three E0 claims; then the four E1 rows ahead of the lane law (the cell, the building size anchors, the band on the canvas, the purification basin); then the lane law's values, each with the unit tests it moves; proven on the reference hamlet (Inashiro, its PNG looked at) and then across the pool and the cohort's bookend seeds (FR-004, FR-005)
      research: rendering
      verify: DONE. DONE. The three E0 claims and the four E1 rows (cell, building size anchors, band on the canvas, purification basin); the lane law: WEB_FABRIC_GAP 7 ft as the foul margin (may_write, _clear_touch, the bridge), TRACK_FABRIC_GAP and FIELD_ROUTE_GAP_FT 7, every join reach 25 ft, _SHORT_LEG_FT and _PAST_CONNECTOR_FT 40, the free stub 12 ft at 90 deg, WEB_CLEARANCE 18, DOOR_REACH_FT 60, lane ends within 25 ft gathered (gap_ways.gathered_foot at seating, knots.settle_knots in the settle), each lane at its rank's width; FOOTPATH_FABRIC_GAP held at 4 ft (at 7 ft Kashikawa refuses; the found row waits). Inashiro's PNG looked at; the pool and the cohort's bookend seeds roll; make done green (10,787 passed; knots strict-xfail on Inashiro and Sawada, the E3 found row)
- [x] T16 every touched unit re-checked by `impl-drift`; each wave-4 row IN-STEP or re-tiered with its measured reason (FR-005, SC-002)
      research: rendering
      verify: DONE. DONE. Every touched unit re-checked by impl-drift (bundles 1-16 of wave 4; make claims-owed: no claim is owed). 34 wave-4 rows IN-STEP, 8 more found in step on re-reading, 5 renamed or retired (audit/waves.json); held or drifted rows re-tiered as found rows with their measured reasons (audit/found-wave4.jsonl, claims-followup.md Wave 4)
- [x] T17 the occasion's review (glyph-check on the village lane, one map) on a green gate; the close: `make perf LABEL=328-end` and the band's records, `make done` green, the wave column, landed (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. DONE. glyph-check on the village lane (Inashiro): round 3 PASS; the later speed-up left every pool map byte-identical, so the round stands (PAIR_OK logged). Back-to-back bookends 328-start (worktree at origin/main) / 328-end: band 2 (40 hh +8.3%, seed 4 +14.4%); explanation with CONTROL=wave4-perf-control-no-gather (the gather 1.1-1.8 s per 40 hh map), perf-audit confirmed and audited JUSTIFIED; make done green; the wave column written

## Phase 6 - wave 5 (two E0 claims, then the E1 rows of the homestead and its fixtures) - amendment 4, 2026-10-07

The two open E0 rows (wave 4's re-checks: an aim test and a track route left unclaimed) come first (SC-003); then the
E1 rows of the next modules in ranking order, the homestead and what stands in it - its fixtures' seats, its groves and
belt, its bundle's garden, its kura and its wells (`settlement/homestead_parts/`, `settlement/rolling/bundle.py` and
`fit.py`, `settlement/farm_fixtures.py`, `settlement/shrines_wells/wells.py`). Every `after` these rows carry is a row
inside the wave, done first. The row-street row of `hamletgen/ways/web.py` stays for the next wave: 0033 has the street
run on off the map and 0246 pulls a way back to the last door it serves, so it is read before it is tiered.

  - `l7r/diagram/hamletgen/ways/law.py::near_misses#ends that nearly meet are joined` - the 25 ft is in step; claim the AIM_DEG 60 deg test that decides which ends count as UNRESEARCHED
  - `l7r/diagram/hamletgen/ways/track.py::_thread_the_fabric#the track's route walled by the field, crop, toe band and wet ground, and kept off drawn water` - claim it: the track's route walled by the field, crop, toe band and wet ground, and kept off drawn water

  - `l7r/diagram/settlement/farm_fixtures.py::KURA_PARTS#west annex` - W annex 0.32 x 0.56 (15 x 16 ft) -> 18-27 ft long, 10-12 ft deep, 1.5-1.8 to one
  - `l7r/diagram/settlement/farm_fixtures.py::kura_rect#west annex size` - hold the west annex to 0040 drawing's band: 18-27 ft long, 1.5-1.8 times as long as deep, as the north annex is
  - `l7r/diagram/settlement/homestead_parts/belt_law.py::MIN_BELT_DEPTH_FT#least belt depth` - MIN_BELT_DEPTH_FT 30 -> 80 ft (0071 drawing: never thinner than 80 ft)
  - `l7r/diagram/settlement/homestead_parts/fixture_seats.py::FixtureForms#privy seat weights` - privy seat weights to stable 35 / yard 30 / front 20 / barn 15 as 0047 drawing lists them
  - `l7r/diagram/settlement/homestead_parts/fixture_seats.py::PRIVY_FRONT_STEP_FT#front privy off the front wall` - front privy edge 8 ft off the front wall: drop the WALL_GAP_FT from the seat (or PRIVY_FRONT_STEP_FT 4.5)
  - `l7r/diagram/settlement/homestead_parts/fixture_seats.py::PRIVY_YARD_STEP_FT#yard outhouse off the back wall` - yard privy edge a ken (6 ft) off the back wall: drop the gap (or PRIVY_YARD_STEP_FT 2.5)
  - `l7r/diagram/settlement/homestead_parts/fixture_seats.py::WOODSHED_STEP_FT#wood shed off its wall` - wood shed edge 6 ft off its wall: drop the gap from the seat (or WOODSHED_STEP_FT 2.5)
  - `l7r/diagram/settlement/homestead_parts/fixture_seats.py::privy_sun_reach_ft#sun-side reach by size` - cap a sunny-side privy center at 48 ft from its house; drop the size allowance in privy_sun_reach_ft
  - `l7r/diagram/settlement/homestead_parts/groves.py::GrovesMixin._draw_grove#lesser broadleaf crown size` - LESSER_BROADLEAF_S floor 0.6 -> 0.75 of the mean radius (0080 drawing: 0.75-1.4), cite 0080
  - `l7r/diagram/settlement/homestead_parts/groves.py::GrovesMixin._draw_grove#windbreak conifer share` - windbreak conifer share c_th = b_th + 0.48 (0072/Takehara: 48% cedar, the dominant tree)
  - `l7r/diagram/settlement/homestead_parts/groves.py::GrovesMixin._grove_fits#off a yard's south strip` - grove box kept out of the 39 ft south corridor (0037/0038) via px(), not a fixed 22 px strip
  - `l7r/diagram/settlement/homestead_parts/stands.py::StandsMixin.village_grove#belt deep and whole` - village_grove gap test compares px(_BELT_GAP_FT), 30 ft at every grain
  - `l7r/diagram/settlement/homestead_parts/stands.py::StandsMixin.village_grove#clumps off the gardens' east` - the east lane 50 ft in feet (0038: no crown within 50 ft east, west or south of a yard or bed), yards included, not 24 px past a garden
  - `l7r/diagram/settlement/homestead_parts/grove_rules.py::EAST_REACH_PX#garden's morning sun` - EAST_REACH_PX 22 bscale -> 0038's 50 ft east reach via px() (after: l7r/diagram/settlement/homestead_parts/wood_share.py::EAST_LANE_PX#bed's morning lane)
  - `l7r/diagram/settlement/homestead_parts/wood_share.py::EAST_LANE_PX#bed's morning lane` - EAST_LANE_PX 24 px -> 0038's 50 ft via px() (after: l7r/diagram/settlement/homestead_parts/grove_rules.py::EAST_REACH_PX#garden's morning sun)
  - `l7r/diagram/settlement/homestead_parts/groves.py::GrovesMixin._shades_a_garden#garden's morning sun` - _shades_a_garden reach 22 x bscale -> 0038's 50 ft east via px() (after: l7r/diagram/settlement/homestead_parts/grove_rules.py::EAST_REACH_PX#garden's morning sun)
  - `l7r/diagram/settlement/homestead_parts/grove_rules.py::gardens_east_shaded#garden's morning sun` - same constant: gardens_east_shaded reads the 50 ft reach (0038) via px() (after: l7r/diagram/settlement/homestead_parts/grove_rules.py::EAST_REACH_PX#garden's morning sun)
  - `l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_layout#garden size` - nucleated garden cap 48 x 34 ft -> a cap whose area stays <= 1,507 sq ft (e.g. 44 x 34 ft), per 0039
  - `l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_layout#headman keeps an ordinary yard and garden` - headman's garden held to an ordinary farm's: the same lowered cap (<= 1,507 sq ft, near the 592 sq ft typical) applies to a big house (after: l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_layout#garden size)
  - `l7r/diagram/settlement/rolling/fit.py::BundleFitMixin._garden_shaded#garden shaded by a house to its south` - _garden_shaded reach gh + 4 px -> px(39) south of the bed (0038's 39 ft house-shade corridor)
  - `l7r/diagram/settlement/shrines_wells/wells.py::WellsMixin._farm_wells#every farmhouse within reach of a well` - farm well reach_ft 500 -> 760 ft (hamlet/village; 870 ft for a city's commoners)
  - `l7r/diagram/settlement/shrines_wells/wells.py::WellsMixin._farm_wells#seated in a steading's dooryard` - dooryard rings held to 95 ft from the dwelling via px(), not 150 px from the house center
  - `l7r/diagram/settlement/shrines_wells/wells.py::WellsMixin._farm_wells#fallback on field-rim ground off the crop` - fallback grid scans within 95 ft of the dwelling (0196), via px(), not 156 px (after: l7r/diagram/settlement/shrines_wells/wells.py::WellsMixin._farm_wells#seated in a steading's dooryard)

- [ ] T18 the bookend before the first edit: `make perf LABEL=328-start` in a detached worktree at main's engine, taken back
      to back with the end bookend (constitution VI; the wave-4 lesson: a pair taken apart reads the host's load)
      research: rendering
      verify:
- [ ] T19 the two E0 claims; then the E1 rows, each with the unit tests it moves; proven on the reference hamlet (Inashiro,
      its PNG looked at) and then across the pool and the cohort's bookend seeds; a value that makes a map refuse is held at
      its old value and the row takes the tier of the work it needs, as a found row (FR-004, FR-005, spec Edge Cases)
      research: rendering
      verify:
- [ ] T20 every touched unit re-checked by `impl-drift`; each wave-5 row IN-STEP or re-tiered with its measured reason (FR-005, SC-002)
      research: rendering
      verify:
- [ ] T21 the close: `make perf LABEL=328-end` and the band's records, `make done` green, the wave column, landed (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify:
