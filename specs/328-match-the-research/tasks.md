# Tasks: the implementation brought to the research, easiest first (feature 328)

**Input**: plan.md (Phase 1, Phase 2, D1-D4). Only the CURRENT wave's rows are task boxes (spec FR-006); the rest of the
ranking is data in `ranking.json` / `ranking.md`, and the next wave is appended here as an amendment once this one lands.

## Occasions

- none: wave 1 changes `Research:` claim lines only (tier E0) - nothing a map draws or where it is placed moves.
- (wave 4, landed and reviewed) placement-changed village lane - wave 4 brought the lane law to 0081 and 0246 (7 ft clear of a fence, ends joined
  within 25 ft, tails and hooks cut at 40 and 12 ft): the lanes are re-placed by substantially different rules.
- none (wave 2): each fix moves one value inside a rule that already places the element (a weight, a pitch, a share, a
  count's cap, an extent); no element is new to a map, no glyph is redrawn, and no element is re-placed by different rules.
- (wave 5, landed and reviewed) placement-changed village lane on kashikawa - wave 5: 0033's row street runs on off the map as the road into it at both ends, where
  the web cut it back to its last joint (`trim_streets`); Kashikawa's and Mizuguchi's far ends now run off the sheet as a
  second way out (every way is inked `village lane`).
- none (wave 5, the other rows): each fix moves one value inside a rule that already places or sizes the element (a
  size, a width, a count, a reach, a caption's leader); no element is new to a map and no glyph is redrawn.

- none (wave 6): claim lines only (tier E0) - nothing a map draws or where it is placed moves.
- none (wave 7): on the scripted pool maps each fix moves one value inside a rule that already places or sizes the element
  (a clearance, a size, a count, a reach); the water gate's opening and the boundary stones' group change a glyph's form, but
  only the legacy hand-authored cities draw them (`water_gate(`, `boundary_marker(`), and feature 294 exempts legacy maps.
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

## Phase 6 - wave 5 (two E0 claims, then the next run of E1: the row street and rows 148-173) - amendment 4, 2026-10-07

The two open E0 rows (wave 4's re-checks: an aim test and a track route left unclaimed) come first (SC-003); then the
next contiguous run of the ranking's E1 rows (FR-006): row 143, the row street - 0033, the page for a row village's
street, has it run on off the map as the road into it, so the street is no longer cut back to its last joint (0246's
pull-back is a clustered settlement's lane rule, plan D7) - and rows 148-173, in ranking order: the tier glossary, the
caption leader and its reach, the overlap matrix and taxonomy, the knobbed sizes, the castle and the city's walls,
bridges, canals, moat and governor's gate. Every `after` these rows carry is a row inside the wave or closed.

  - `l7r/diagram/hamletgen/ways/law.py::near_misses#ends that nearly meet are joined` - the 25 ft is in step; claim the AIM_DEG 60 deg test that decides which ends count as UNRESEARCHED
  - `l7r/diagram/hamletgen/ways/track.py::_thread_the_fabric#the track's route walled by the field, crop, toe band and wet ground, and kept off drawn water` - claim it: the track's route walled by the field, crop, toe band and wet ground, and kept off drawn water

  - `l7r/diagram/hamletgen/ways/web.py::stage_web#a row street trimmed to end at its outermost door-path joint or last farm door` - the row street runs on off the map as the road into it (0033 drawing), not trimmed at its last farm's path - with the lane law
  - `l7r/diagram/interactive/place.py::KINDS#what each tier is` - the 0001 figures match (1,296, 216, 40%); drop 'unless the hamlet keeps a burial ground of its own' from the hamlet text (and the village's 'hamlets without their own') per 0236
  - `l7r/diagram/labels/placer.py::leader_of#when a leader is drawn` - leader_of returns None while the caption is within twice the usual gap (rings 0 and 1, 1.0 em); a leader only past it
  - `l7r/diagram/labels/standard.py::REACH_EM#how far a caption may move` - leaderless reach capped at twice the usual gap (1 em); REACH_EM's 8 em kept only as the leadered search's outer bound, claimed UNRESEARCHED (after: l7r/diagram/labels/placer.py::leader_of#when a leader is drawn)
  - `l7r/diagram/overlap/matrix.py::DOJO_RANGE_FT#archery lane` - archery lane to 250 x 8 ft per 0164 (not 90 ft)
  - `l7r/diagram/overlap/taxonomy.py::_LABEL_GROUP#a caption covers its own group` - give graveyard, cremation, mausoleum and ossuary one shared funerary label group
  - `l7r/diagram/overlap/taxonomy.py::_OVERLAP_EXEMPT#mill beside its stream` - the mill seated in a short mill race led off the stream below the intake (0064), and the exemption says so
  - `l7r/diagram/settlement/_knobs.py::BOUNDARY_MARKER_FT#boundary stone size` - BOUNDARY_MARKER_FT 3.0 -> 4.0 per 0217 drawing
  - `l7r/diagram/settlement/_knobs.py::execution_ground_ft#execution ground size` - execution_ground_ft: a capital returns about 200 x 65 ft (0191: 150-250 x 50-80), provincial city keeps 100 x 60
  - `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.castle#bailey and masugata sizes` - cite 0139 drawing and size the honmaru to about 2 ha (frac ~0.04 of a 50 ha enceinte, not 0.34); masugata stays UNRESEARCHED
  - `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.martial_hall#hall program sizes` - martial hall 60 x 36 -> about 124 x 35 ft one long building; label the lane and 130 x 100 compound UNRESEARCHED
  - `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.ministry#ministry compound size` - ministry default 224 x 148 -> within 0167: provincial 110x80-140x95 ft, capital about 160 x 110 ft
  - `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.wall#gate opening` - gate opening 36 px -> px(13) (0147 drawing: 13 ft passage); cite 0147
  - `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.wall#rampart stroke` - rampart stroke fixed 10 px -> px(10..12) so it holds 10-12 ft at any grain
  - `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#plank width` - plank width in feet: px(4) (about 4 ft)
  - `l7r/diagram/settlement/city/canals.py::CanalsMixin.farmland_ring#sluice standoff` - measure the sluice's standoff from the moat's rim (not the tap point / centerline) and set it to about 90 ft (0146 drawing)
  - `l7r/diagram/settlement/city/civic.py::CityCivicMixin.governor_mansion#gate direction` - governor's compound gate to the south
  - `l7r/diagram/settlement/city/moat.py::MoatMixin.moat#junction tilts` - river_inlet_tilt and river_outlet_tilt to 0 (right angle)
  - `l7r/diagram/settlement/city/moat.py::MoatMixin.moat#moat width` - moat width px(35) (35 ft), not px(66)
  - `l7r/diagram/settlement/city/moat.py::MoatMixin.water_gate#glyph size` - water gate sized in feet via px(): 60 ft with ~12 ft piers, not a fixed 36 x 22 px
  - `l7r/diagram/settlement/city/walls.py::WallsMixin._gate_caption#ground reserved round the gate tower` - gate-tower apron to ~36 ft (px(36)), not 30 px (~90 ft)
  - `l7r/diagram/settlement/city/walls.py::WallsMixin._gate_flanking_buildings#set on the patrol road` - set the flanking buildings 105-135 ft inside the opening (ring_inset default 34 px gives ~102 ft); fix the ~20-100 ft comment
  - `l7r/diagram/settlement/city/walls.py::WallsMixin._seat_mural_towers#no tower in a gate or water-gate opening` - bar towers within 390 ft (px(390)) of a gate and 135 ft of a water gate
  - `l7r/diagram/settlement/city/walls.py::WallsMixin._seat_mural_towers#slide off a ward gate or gate works` - bar towers within 186 ft of a kido and 165 ft of guard buildings (px), not 32/40 px (after: l7r/diagram/settlement/city/walls.py::WallsMixin._seat_mural_towers#no tower in a gate or water-gate opening)
  - `l7r/diagram/settlement/city/walls.py::WallsMixin._tower#no-build margin` - no-build margin px(36) in feet; 12*max(bscale,0.5) gives ~18 ft at the city's bscale 1/3
  - `l7r/diagram/settlement/city/walls.py::WallsMixin._tower#tower footprint` - tower footprint 65 x 40 ft (along_ft 65, ~1.7:1)
  - `l7r/diagram/settlement/city/walls.py::WallsMixin._tower#tower building on the spur` - floor the tower building on the spur at 30 ft: max(30, min(34, 0.55*along)) (after: l7r/diagram/settlement/city/walls.py::WallsMixin._tower#tower footprint)

- [x] T18 the bookend before the first edit: `make perf LABEL=328-start` in a detached worktree at main's engine, taken back
      to back with the end bookend (constitution VI; the wave-4 lesson: a pair taken apart reads the host's load)
      research: rendering
      verify: DONE. DONE. 328-start taken in a detached worktree at origin/main (491b7bf7f, main's engine before any wave-5 edit), back to back with the end bookend on a quiet host (a first pair that overlapped the gate was discarded): total 16.9 s
- [x] T19 the two E0 claims; then the E1 rows, each with the unit tests it moves; proven on the reference hamlet (Inashiro,
      its PNG looked at; Kashikawa and Mizuguchi for the row street) and then across the pool and the cohort's bookend
      seeds; a town or city value no pool map draws is proven by its unit test; a value that makes a map refuse is held at
      its old value and the row takes the tier of the work it needs, as a found row (FR-004, FR-005, spec Edge Cases)
      research: rendering
      verify: DONE. DONE. The two E0 claims; the row street runs on off the map at both ends (0033; the far run flagged run_on so the board keeps the road's entrance); captions leaderless to twice the gap (0242); the funerary caption group; the tier text; the execution ground by tier and the 4 ft stone; the honmaru at 2 ha; the martial hall's 124 x 35 ft hall; ministries by tier; the town wall's 13 ft gate and 11 ft rampart; the plank 4 ft; the sluice 90 ft past the rim; the moat's river ends square; the water gate 60 ft clear between 12 ft piers; the governor's gate south; the city wall's figures in feet; the mill re-tiered E3 (a mill race is new), the moat width E4 (0146 and 0151 disagree), the dead archery constant removed. Proven on Inashiro, Kashikawa and Mizuguchi (PNGs looked at), then the pool and the cohort through the gate; city values by their unit tests
- [x] T20 every touched unit re-checked by `impl-drift`; each wave-5 row IN-STEP or re-tiered with its measured reason (FR-005, SC-002)
      research: rendering
      verify: DONE. DONE. impl-drift on every touched unit (bundles A-G of wave 5; make claims-owed: no claim is owed); 21 wave-5 rows IN-STEP, 6 closed by rename or removal, 5 re-tiered with their reasons (overrides.json), the re-checks' 37 further findings ranked as found rows (found-wave5.jsonl, claims-followup.md Wave 5)
- [x] T21 the occasion's review (glyph-check on Kashikawa's ways, one map) on a green gate; the close: `make perf LABEL=328-end` and the band's records, `make done` green, the wave column, landed (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. DONE. glyph-check on Kashikawa's ways PASS (the occasion now names its map, _review_owed.py); the later run_on flag left the lanes identical and restored main's board seat. Bookends back to back: band 0 (total -1.2%, 40 hh -5.8%), nothing owed; make done green; make page-check green; the wave column written

## Phase 7 - wave 6 (tier E0: the claim alone - the open rows) - amendment 5, 2026-10-07

Every open E0 row in ranking order (SC-003): the decisions wave 5's re-checks found unclaimed or mislabeled. Claim lines
only. Where a claim written or relabeled names a page that the code then departs from, the claim says what the code does against that page,
and the departure is a found row tiered by the work it takes (spec Edge Cases), not a code change in this wave.

  - `l7r/diagram/hamletgen/ways/law.py::near_misses#a household way's door end is never counted as a join that stops short` - claim it: a household way's door end is never counted as a join that stops short
  - `l7r/diagram/hamletgen/ways/track.py::_thread_the_fabric#the track's route walled` - 0246 walls only a back lane's stretches (§63); the track's walls are in 0081 ("never crosses row crops", "stops at the flooded paddy", "keeps off wet ground"), and keeping off drawn water belongs to 0035's crossing rule; repoint to 0081 (and 0035 for the water)
  - `l7r/diagram/hamletgen/ways/track.py::stage_track#connector and spur keep a 40 ft no-build clearance (LANE_CLEARANCE)` - claim it: connector and spur keep a 40 ft no-build clearance (LANE_CLEARANCE)
  - `l7r/diagram/hamletgen/ways/track.py::stage_track#spur clip margin` - 0081 answers where the spur stops at the dry plots (a lane "may touch a plot's boundary"); the claim cites 0081 against the code's 12 ft clip off the dry plots, which becomes a found row ranked toward 0081's rule; only the toe-band margin stays UNRESEARCHED
  - `l7r/diagram/hamletgen/ways/track.py::stage_track#spur tip set back 17 ft (SPUR_SETBACK) off the field outline's vertex` - claim it: spur tip set back 17 ft (SPUR_SETBACK) off the field outline's vertex
  - `l7r/diagram/hamletgen/ways/track.py::stage_track#valley and polder connector width CONNECTOR_WIDTH 6 ft` - claim it: valley and polder connector width CONNECTOR_WIDTH 6 ft
  - `l7r/diagram/interactive/place.py::KINDS#a hamlet's dead burned and buried at the main village's` - claim it: a hamlet has no cremation ground; its dead are burned and buried at the main village's, which holds the district's grounds - cite the burial question (0236)
  - `l7r/diagram/labels/standard.py::REACH_EM#how far the ringed search runs` - how far a caption is displaced before its leader is how it is shown (0242 calls the gap "our calibration"); the label should be CONVENTION, not UNRESEARCHED
  - `l7r/diagram/overlap/taxonomy.py::_LABEL_GROUP#an arch is never covered` - this is the GM's ruling (2026-07-27, "never be covered by the 'temple of X' label"), and it overrides 0243's "its own building or compound"; the label should be CANON naming that ruling
  - `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.castle#each bailey's gate turned 90 degrees from its parent's (the dogleg route)` - claim it: each bailey's gate turned 90 degrees from its parent's (the dogleg route)
  - `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.castle#ground reserved` - the max(36 x bscale, 26) px margin outside the moat is a physical rule for how close buildings stand to the castle works, not plumbing; it should be UNRESEARCHED
  - `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.castle#inner moat` - the findings answer the inner moat's width: Hiroshima's "inner moat 30 to 104 m" (~98-341 ft), while the code draws mw*0.5 = 40 ft, below that range; the width should cite 0139.html §51 and be widened, and only the 0.42 x gap offset stays UNRESEARCHED
  - `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.martial_hall#the layout: hall across the north, lane on the south band, sensei's house between, azuchi 10 ft deep, shooting line 6 ft` - claim it: the layout: hall across the north, lane on the south band, sensei's house between, azuchi 10 ft deep, shooting line 6 ft from the lane's end
  - `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.wall#buildings kept off the rampart` - the cited 0125 drawing page answers this: "a clear strip about 46 ft wide" (the code uses 46 px, not px(46)); 0147 answers the gate buildings' clearance, "about 36 ft clear around each" (the code uses 32 px); both should cite those blocks
  - `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.wall#gate opening` - the 13 ft passage is in step (0147); claim the 14 x 48 px gateposts UNRESEARCHED
  - `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.wall#guard station and tower` - 0147 answers both: a town gate has "a 13 ft passage under a tower about 40 by 24 ft" and a "small guard room ... about 12 by 18 ft just inside it", but the code draws a 40 x 40 px tower beside the gate and a 96 x 46 px station; the claim should cite 0147, and the code is off from it
  - `l7r/diagram/settlement/castle_civic.py::honmaru_fracs#the honmaru held to at most 0.34 of a small enceinte's half-sides` - claim it: the honmaru held to at most 0.34 of a small enceinte's half-sides
  - `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#a seat nearer a drain or collector than its own ditch refused (plank_on_supply)` - claim it: a seat nearer a drain or collector than its own ditch refused (plank_on_supply)
  - `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#assumed water widths when a record has none (DEFAULT_W: streams 9.0, channels 2.5, ditches 4.2)` - claim it: assumed water widths when a record has none (DEFAULT_W: streams 9.0, channels 2.5, ditches 4.2)
  - `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#longer plank at a junction` - 0084 answers this: it lists "the joins of ditches" among things that rule a seat out, and holds the span at "about 8 ft" because a longer board "would read as a jetty"; the code instead widens the deck over the junction. Should cite 0084, and against it this is a drift
  - `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#off dry crops, gardens and groves` - 0084 answers it ("Houses, crops, other crossings ... can rule out every wide spot"); should cite 0084, not UNRESEARCHED
  - `l7r/diagram/settlement/city/canals.py::CanalsMixin.farmland_ring#non-moat (river) taps are never swept; the head race leaves on the outward bearing, unaligned with the current` - claim it: non-moat (river) taps are never swept; the head race leaves on the outward bearing, unaligned with the current
  - `l7r/diagram/settlement/city/canals.py::CanalsMixin.farmland_ring#sluice set radially outward from the city center (or the caller's bearing)` - claim it: sluice set radially outward from the city center (or the caller's bearing)
  - `l7r/diagram/settlement/city/moat.py::MoatMixin.water_gate#one opening whatever the canal` - claim it: one 60 ft opening whatever the canal; 0179 makes the passage as wide as its canal and gives a river a row of arched openings - claim against 0179 (a drift to rank if the canal is narrower or a river)
  - `l7r/diagram/settlement/city/moat.py::MoatMixin.water_gate#pier depth through the wall, 30 ft` - claim it: the piers 30 ft deep through the wall, UNRESEARCHED (0147 gives a water gate's opening and pier width, not its depth)
  - `l7r/diagram/settlement/city/walls.py::WallsMixin._gate_flanking_buildings#fallback road width px(26) for the verge setback` - claim it: fallback road width px(26) for the verge setback
  - `l7r/diagram/settlement/city/walls.py::WallsMixin._gate_flanking_buildings#guard buildings turned square to the local wall tangent` - claim it: guard buildings turned square to the local wall tangent
  - `l7r/diagram/settlement/city/walls.py::WallsMixin._seat_mural_towers#a slid tower kept at least 45 px from a gate` - claim it: a slid tower kept at least 45 px from a gate
  - `l7r/diagram/settlement/city/walls.py::WallsMixin._seat_mural_towers#mural tower nudged outward onto the berm, px(40)` - claim it: mural tower nudged outward onto the berm, px(40)
  - `l7r/diagram/settlement/civic_grounds/justice.py::JusticeGroundsMixin.boundary_marker#one stone drawn, where 0217 draws a group of one to three at an entrance` - claim it: one stone drawn, where 0217 draws a group of one to three at an entrance
  - `l7r/diagram/settlement/civic_grounds/justice.py::JusticeGroundsMixin.execution_ground#two post sockets about 3 ft square, and their spacing` - claim it: two post sockets about 3 ft square, and their spacing
  - `l7r/diagram/settlement/structures/fixtures/_helpers.py::kosatsuba_anchor#the approach counts as reaching the houses within KOSATSUBA_ENTRANCE_REACH_FT 100 ft of a dwelling` - claim it: the approach counts as reaching the houses within KOSATSUBA_ENTRANCE_REACH_FT 100 ft of a dwelling

- [x] T22 every row's claim written or relabeled (cite the page that answers it, CANON for a GM ruling, GUESS or
      UNRESEARCHED where the page is silent; DEVIATION only after the exception path rules it LEGITIMATE); a departure a
      claim written or relabeled exposes - the code against the page it names - ranked as a found row (FR-003, FR-004)
      research: rendering
      verify: DONE. DONE. Every open E0 row's claim written or relabeled in two rounds: pages that answer cited, CANON for the GM's arch ruling, GUESS or UNRESEARCHED where silent, no DEVIATION; each departure a claim now states is a found row (found-wave6.jsonl). law.py's water rules lifted to law_water.py at the 1,000-line bar
- [x] T23 every touched unit re-checked by `impl-drift`; each wave-6 row IN-STEP or re-tiered with its measured reason (FR-005, SC-002)
      research: rendering
      verify: DONE. DONE. impl-drift on every touched unit (bundles A-D of wave 6; make claims-owed: no claim is owed); 32 rows closed (5 IN-STEP, 23 claimed under their unit's label, 4 claims stating a drift now ranked); 17 further findings ranked as found rows
- [x] T24 the close: `make done` green, the wave column, landed (no bookend: claim lines move no engine behavior) (FR-005, FR-006)
      research: rendering
      verify: DONE. DONE. make done green (193 s, every pool map, seeds 41-44); no bookend owed (claim lines and a unit move only); the wave column written

## Phase 8 - wave 7 (the open E0 claims, then the next run of E1: rows 183-234) - amendment 6, 2026-10-07

T25a first: the 34 found rows the re-checks of waves 4-6 tiered by their verdict alone are tiered by the work they take, by a
fresh reader (`audit/t25a-out.jsonl`, applied in `audit/overrides.json`), as T12a did before wave 3 - so the run below is
chosen on tiers set by the work. Then the 7 open E0 rows (SC-003); then the next contiguous run of E1 (FR-006), rows
183-234 in ranking order, ending with the civic grounds' last row (the next open E1 row is 235): the connector's
clearance, the tier text's city note, the samurai caption's estates, the martial hall's practice gear, the town wall's gate
ground, the plank's ditch, brook and abutment widths, the city gate's ground, road and towers in feet, and the civic
grounds' sizes, counts and reaches. Every `after` these rows carry is a row inside the wave or closed.

  - `l7r/diagram/hamletgen/ways/law_water.py::oblique_at#square ditch crossing` - claim the channel crossing UNRESEARCHED: squared within FORD_SQUARE_TOL_DEG, 10 degrees (0084 squares only the standalone footplank; 0087 solves a carried deck at its way's angle and gives no tolerance), the brook keeping its 0035 citation
  - `l7r/diagram/hamletgen/ways/law_water.py::off_ford_at#how far from a crossing place a brook crossing may stand, FORD_HALF 30 ft` - claim off_ford_at's reach: how far from a crossing place a brook crossing may stand - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: FORD_HALF, half the 60 ft crossing place, 30 ft
  - `l7r/diagram/hamletgen/ways/law_water.py::short_decks#assumed water widths where none is recorded: 3 ft for a ditch or channel, 6 ft for a stream` - claim it: assumed water widths where none is recorded, 3 ft for a ditch or channel, 6 ft for a stream
  - `l7r/diagram/hamletgen/ways/serve.py::_lay_web_lane#not along a shelter belt` - split the claim: a lane kept through a shelter belt cited to 0072 drawing, and the 60 ft a lane may run inside one claimed UNRESEARCHED
  - `l7r/diagram/hamletgen/ways/street.py::row_reach#street run past its end farms` - reword the claim: half a frame past the end farms at both ends of the span, UNRESEARCHED, the run off the map being street_run_out's road (0033 drawing)
  - `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#supply ditches only` - split the claim: no plank over the collector or drain cited to 0084 drawing (the foot drains and diagonal edge drains), and the feeder's exclusion from SUPPLY_ROLES claimed UNRESEARCHED
  - `l7r/diagram/settlement/structures/fixtures/_helpers.py::kosatsuba_handover#a through track's handover` - claim the through track's handover UNRESEARCHED: where both ends are off the sheet, the lane end joining it nearest the houses' middle (0190 says only entrance)

  - `l7r/diagram/hamletgen/ways/track.py::stage_track#lane clearance` - LANE_CLEARANCE becomes 7 ft (0246 drawing: a lane's middle keeps 7 ft clear of a garden fence and nothing is built on its tread) in place of the 40 ft corridor, and the claim cites 0246.drawing for it
  - `l7r/diagram/interactive/place.py::KINDS#what each tier is` - the city's population_note says 'by convention' it takes in the samurai country estates, where 0001 counts only those within the walls: align the note with 0001; if the convention proves a GM ruling, the claim is CANON naming that ruling
  - `l7r/diagram/overlap/taxonomy.py::_LABEL_GROUP#a caption covers its own group` - the funerary group is in step (wave 5); what is left: `manors` maps to 'estate', so a samurai caption may not cover the manors 0243 lets it cover ("A samurai caption, the samurai houses and estates") - give the samurai caption the estates
  - `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.martial_hall#practice gear` - drop the practice gear from the state hall's compound (the `_keiko_gear` call) so it is drawn as its wall and three features, the rest implied, and cite research/questions/0165-martial-training-grounds-and-dojo.drawing.html for it
  - `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.wall#ground round the gate structures` - the gate structures' reserved margin becomes self.px(36) (about 36 ft clear around each) in place of the fixed `bm = 32` px
  - `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#assumed ditch width` - the field ditch's assumed width becomes self.px(2.5) (0084 drawing: 2.5 ft at the head, tapering toward 1.2 ft) in place of 4.2 px, in both `DEFAULT_W["field_ditches"]` and `d.get("w", 4.2)`
  - `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#assumed stream and channel widths` - the brook's assumed width becomes self.px(7) (0035 drawing: a brook 7 ft wide) in place of the 9 px `DEFAULT_W["streams"]`, cited to 0035, and the channel's 2.5 px default is claimed UNRESEARCHED
  - `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#short abutment` - PLANK_ABUTMENT becomes a real-feet figure converted at each use (self.px), sized so a deck over a 2.5 ft ditch spans about 8 ft (0084 drawing), in place of 6 px at every grain
  - `l7r/diagram/settlement/city/walls.py::WallsMixin._gate_caption#ground reserved round the gate works` - the guard house and inspection hall's reserved margin becomes self.px(36) (about 36 ft clear around each) in place of the fixed 12 px
  - `l7r/diagram/settlement/city/walls.py::WallsMixin._gate_flanking_buildings#fallback road width` - the fallback road width becomes self.px(30) (0147 drawing: the gate's 30 ft is the trunk road's width) in place of px(26), and the claim names `road_width`, not a ring road
  - `l7r/diagram/settlement/city/walls.py::WallsMixin._seat_mural_towers#a slid tower off a gate` - hold a slid mural tower to self.px(390) from every gate (0148 drawing: no tower within 390 ft of a gate) in place of the fixed 45 px
  - `l7r/diagram/settlement/city/walls.py::WallsMixin._seat_mural_towers#exempt stretches` - the coverage sweep's exempt stretches become self.px(390) of a gate and self.px(165) of its guard buildings in place of the fixed 130 and 55 px
  - `l7r/diagram/settlement/city/walls.py::WallsMixin._seat_mural_towers#reach counted from the parapet` - a tower's reach is counted from its parapet at self.px(36) out from its center (0148 drawing) in place of the fixed `+ 12.0` px, and the stale half-footprint comment goes
  - `l7r/diagram/settlement/civic_grounds/civic.py::CivicWorksMixin.granary#store size and count` - default store w x h from fixed 58 x 34 px to px(45) x px(25) ft (one office store) or px-converted stores in the 440-740 sq ft band at a landing
  - `l7r/diagram/settlement/civic_grounds/civic.py::CivicWorksMixin.merchant_residences#how many` - default merchant_residences count from 4 to the page's dozen or so rich merchant families (less the 1-3 walled), ~10
  - `l7r/diagram/settlement/civic_grounds/civic.py::CivicWorksMixin.merchant_storehouses#kura size` - draw each merchant kura square, 14-20 ft (0152/0150 drawing: 'Each storehouse is 14 to 20 ft square')
  - `l7r/diagram/settlement/civic_grounds/civic.py::CivicWorksMixin.precinct_interior#precinct size` - default precinct from 130 x 100 px (~117,000 sq ft) to px-converted ~73,000 sq ft (e.g. 310 x 235 ft)
  - `l7r/diagram/settlement/civic_grounds/civic.py::CivicWorksMixin.terrace#cell count` - terrace default units from 6 to 8
  - `l7r/diagram/settlement/civic_grounds/civic.py::CivicWorksMixin.terrace#range depth` - range depth_ft from 21.0 to 24.0 (Shibata's 7.3 m)
  - `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cemetery#rows of low markers` - cemetery marker spacing from fixed 9 px to px(9) (about 9 ft)
  - `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cremation_ground#fire bed` - fire bed from px(12) x px(8) to about one coffin length and a little wider (~px(6) x px(3)), inside the 11 ft roof
  - `l7r/diagram/settlement/civic_grounds/justice.py::JusticeGroundsMixin.boundary_marker#stone size` - BOUNDARY_MARKER_FT from 3.0 to 4.0 and drop the 7 px drawn floor so the stone draws about 4 ft
  - `l7r/diagram/settlement/civic_grounds/lodging.py::LodgingMixin.stables#stall divisions` - stall step from 16 ft to one ken (~6 ft): max(6 * sf, floor)
  - `l7r/diagram/settlement/civic_grounds/stable_yard.py::StableYardMixin._stable_yard#yard radius` - yard radius default from 72 px to px(127.5) (255 ft across), converted per map
  - `l7r/diagram/settlement/civic_grounds/lodging.py::LodgingMixin.stables#working yard at a city's gate stables` - r is the scatter disk radius: the stables yard default r to the page's ~255 ft across (px(127.5)) (after: l7r/diagram/settlement/civic_grounds/stable_yard.py::StableYardMixin._stable_yard#yard radius)
  - `l7r/diagram/settlement/civic_grounds/lodging.py::LodgingMixin.animal_ground#caravan ground` - caravan ground default r to reach the 3-trough line (or key trough count on the ground's kind, caravan = 3) (after: l7r/diagram/settlement/civic_grounds/stable_yard.py::StableYardMixin._stable_yard#yard radius)
  - `l7r/diagram/settlement/civic_grounds/stable_yard.py::StableYardMixin._yard_watering#troughs clustered at the nearest well` - well reach from r + 40 px to a well within 40 ft (px(40)) of the yard's edge

- [ ] T25a the found rows tiered provisionally by verdict read and tiered by the work they take, by a fresh reader, before
      the wave chooses its rows (FR-002, FR-003, SC-003)
      research: rendering
      verify:
- [ ] T25 the bookend pair, back to back: `make perf LABEL=328-start` in a detached worktree at main's engine, then
      `LABEL=328-end` in the clone (constitution VI)
      research: rendering
      verify:
- [ ] T26 the open E0 claims; then the E1 rows, each with the unit tests it moves; proven on the reference hamlet (Inashiro,
      its PNG looked at) and then across the pool and the cohort's bookend seeds; a town or city value no pool map draws is
      proven by its unit test; each row fixed toward the page it cites, DEVIATION written only after `spec-fidelity` rules it
      LEGITIMATE on the exception path (a GM ruling is CANON naming it); a value that makes a map refuse is held and the row
      takes the tier of the work it needs (FR-004, FR-005, spec Edge Cases)
      research: rendering
      verify:
- [ ] T27 every touched unit re-checked by `impl-drift`; each wave-7 row IN-STEP or re-tiered with its measured reason (FR-005, SC-002)
      research: rendering
      verify:
- [ ] T28 the close: the band's records, `make done` green, the wave column, landed (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify:
