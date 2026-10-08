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
- none (wave 34): the two-width joint pass changes no pool map; the reservoir seat tried and reverted
- none (wave 33): the path's own beds and sheds made obstacles; the five pool hamlets unchanged
- none (wave 32): claims only, no executed code changed
- none (wave 31): the network join tightened changes no pool map; the bund trial reverted
- none (wave 30): the reservoir share tried and reverted; a claim relabeled, no executed code changed
- none (wave 29): claims only, no executed code changed
- none (wave 28): the polder edge and the knot form tried and reverted; a claim and a comment changed, no executed code
- none (wave 27): the brook and flank rules change no pool map
- none (wave 26): the drain's corridor dropped on a hamlet; the five pool hamlets unchanged
- none (wave 25): claims and one code comment, no executed code changed
- none (wave 24): the rank step reaches no pool map; Kuwabata's two sties move 3.8 and 1.7 ft along their own bank (measured 2026-10-08, kuwabata.json 397c005fb vs HEAD)
- none (wave 23): claims only, no executed code changed
- placement-changed: farm holding on kashikawa - wave 22: the far-row holding three LOTS deep (0033 drawing: three times the frame's
  width), not three frame depths; Kashikawa's holdings run deeper (47 dry plots to 67), its houses unmoved.
- none (wave 21): two claims written - no code a map executes changed.
- placement-changed: woodland commons on kashikawa - wave 20: a wood only where the walk from the houses runs THROUGH the field and
  beyond it, on every tier (0077 drawing: beyond the fields AND higher than them; the woodland glyph check found the slope tier
  admitting the houses' own side) - Kashikawa draws one wood where three stood; Inashiro's and Mizuguchi's woods now fit nowhere
  on the sheet and are recorded beyond it (`woodland_offsheet`, N and W), the woodland commons gone from their legends. The
  woodland unit's two rounds are spent (waves 19 and 20, the second NEEDS-WORK); its F1 is verified by measurement
  (`measurements.json` mizuguchi-glyph-woodland-F1-side) - a third round asks the GM's waiver.
- placement-changed: woodland commons on inashiro - wave 19: the coppice wood taken beyond the fields from the houses first (0077
  drawing), where feature 261 preferred the houses' side; Inashiro's woods re-placed (three where two stood).
- placement-changed: woodland commons on kashikawa - wave 19: the same; Kashikawa's woods move across its field.
- none (wave 18): the thicket's 70% passes dropped moved nothing drawn - measured: Kashikawa's and Mizuguchi's thickets were seated
  at full size and their manifests are unchanged; the other rows are claims.
- placement-changed: shared bamboo grove on kashikawa - wave 17: every thicket pass holds the stand just beyond the back row
  (0075 drawing; its near edge within `THICKET_ROW_DEPTH_FT` of the row's back edge): Kashikawa's thicket moves from 88 ft
  behind its row to against it; Mizuguchi's, the other pool thicket, stands where it stood.
- none (wave 16): the two retired knob forms moved nothing drawn - measured on the regenerated maps against the base: Mizuguchi,
  which declared the belt-side copse, is linear and draws no copse, and Kashikawa's and Sawada's notice boards stand where they
  stood (the drawing-water bid did not decide their seats); only each map's recorded knob changed.
- none (wave 5, the other rows): each fix moves one value inside a rule that already places or sizes the element (a
  size, a width, a count, a reach, a caption's leader); no element is new to a map and no glyph is redrawn.

- none (wave 6): claim lines only (tier E0) - nothing a map draws or where it is placed moves.
- none (wave 7): on the scripted pool maps each fix moves one value inside a rule that already places or sizes the element
  (a clearance, a size, a count, a reach); the water gate's opening and the boundary stones' group change a glyph's form, but
  only the legacy hand-authored cities draw them (`water_gate(`, `boundary_marker(`), and feature 294 exempts legacy maps.
- none (wave 8): on the scripted pool maps, claim lines and values inside rules that already place or size the element (a
  width, a margin, a stretch); the cemetery, cremation ground, terrace and city wall are drawn only on exempt legacy maps.
- none (amendment 8 and wave 9): the scope is a ranking column and a deferred list; wave 9's fixes move values inside rules
  that already place or size the element (a step off a wall, a reach, a crown floor, a share, a depth, a width, a size)); the
  dike gate's span sizes a glyph no pool map's manifest records (`dike_gates`), and the commons fill, a glyph change, moved to E2.
- glyph-redrawn: notice board on inashiro - wave 10 sizes the kosatsuba to the page's 16 x 6 ft (from 12 x 5) and turns it
  30 degrees to its way (from 45); its other rows move values inside rules that already place or size their elements.
- none (wave 11): claim lines and three values inside rules that already place or size their elements (the hem's fallback
  watercourse widths, the stub's bund reach in pixels, the polder's default gaps in feet); no glyph redrawn, no element new.
- none (wave 12): claim lines and two values in feet inside rules that already place their elements (the brook's bank margin, the
  polder toe's run); no glyph redrawn, no element new.
- none (wave 13): claim lines and the Mode A procedures' text; no sheet redrawn (the redraw rows are E3), the country shrine's
  widened bands still hold Hoshigaoka as drawn.
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
  - `buildings/programs.md::Magistrate's manor (county magistracy)#granary weight knob` - taken with the granary forms row it is tied to (impl-drift on the split claim: the office draws one storehouse, any row stands at the town's river landing - 0098's drawing page): the knob is where the rice waits, the office draws one storehouse either way; no sheet draws a row at the office
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

- [x] T25a the found rows tiered provisionally by verdict read and tiered by the work they take, by a fresh reader, before
      the wave chooses its rows (FR-002, FR-003, SC-003)
      research: rendering
      verify: DONE. DONE. 34 rows tiered by their work by a fresh Opus reader (audit/t25a-out.jsonl, each reason measured in the code), applied in audit/overrides.json: 18 moved (E0 6, E1 12, E2 9, E3 7); the follow-up record carries the new tiers
- [x] T25 the bookend pair, back to back: `make perf LABEL=328-start` in a detached worktree at main's engine, then
      `LABEL=328-end` in the clone (constitution VI)
      research: rendering
      verify: DONE. DONE. 328-start in a detached worktree at origin/main and 328-end in the clone, back to back: band 0 (total -2.4%, 40 hh -0.9%), nothing owed
- [x] T26 the open E0 claims; then the E1 rows, each with the unit tests it moves; proven on the reference hamlet (Inashiro,
      its PNG looked at) and then across the pool and the cohort's bookend seeds; a town or city value no pool map draws is
      proven by its unit test; each row fixed toward the page it cites, DEVIATION written only after `spec-fidelity` rules it
      LEGITIMATE on the exception path (a GM ruling is CANON naming it); a value that makes a map refuse is held and the row
      takes the tier of the work it needs (FR-004, FR-005, spec Edge Cases)
      research: rendering
      verify: DONE. DONE. The seven E0 claims; the E1 rows: plank abutment 5.5 ft and widths in feet, the samurai caption's estates, the castle wall's gate ground 36 ft, the city gate's road 30 ft, ground 36 ft, towers 390/165 ft and reach 36 ft, the civic grounds (granary one 45 x 25 ft store, ten merchant homes, kura 17 ft square, precinct 310 x 235 ft, terrace 8 units 24 ft deep, markers 9 ft, fire bed 6 x 3 ft, stalls a ken, yards 255 ft, wells within 40 ft), the boundary stone at 4 ft (its floor removed), the martial hall's practice gear removed; the lane clearance held at 40 ft (a center corridor) and re-tiered E2. Inashiro rolled; the pool and the cohort through the gate; city values by their unit tests
- [x] T27 every touched unit re-checked by `impl-drift`; each wave-7 row IN-STEP or re-tiered with its measured reason (FR-005, SC-002)
      research: rendering
      verify: DONE. DONE. impl-drift on every touched unit (bundles A-E of wave 7; make claims-owed: no claim is owed); 21 rows IN-STEP, 4 claimed under their unit's label, 9 re-tiered with the re-check's further finding (overrides.json); 30 findings ranked as found rows
- [x] T28 the close: the band's records, `make done` green, the wave column, landed (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. DONE. make done green (185 s); band 0 nothing owed; the wave column written

## Phase 9 - wave 8 (the open E0 claims, then the next run of E1: rows 187-247) - amendment 7, 2026-10-07

T29a first: the 14 found rows wave 7's re-checks tiered by verdict alone are tiered by their work by a fresh reader
(`audit/t29a-out.jsonl`, applied in `audit/overrides.json`; 11 moved), as T25a did. Then the 18 open E0 rows (SC-003),
each a claim written or relabeled (cite the page that answers it, CANON for a GM ruling, GUESS or UNRESEARCHED where the page
is silent; DEVIATION only after the exception path rules it LEGITIMATE). Then the next contiguous run of E1 (FR-006), rows
187-247 in ranking order, ending with the civic grounds' last row (the next open E1 row is 253): the deck's assumed water
widths, a row street's farm frame (row 192, found by this amendment's first round), the temple and gate caption words, the city wall's exempt stretches, the terrace unit, the cemetery's and cremation
ground's margins and the cemetery's first row. Every `after` these rows carry is a row inside the wave or closed.

  - `l7r/diagram/hamletgen/ways/bund.py::a_way_onto_the_bund#a lane end within 6 ft (BUND_REACH_FT) of the paddy counts as joined to the bund` - claim it: a lane end within 6 ft (BUND_REACH_FT) of the paddy counts as joined to the bund
  - `l7r/diagram/hamletgen/ways/bund.py::a_way_onto_the_bund#a lane end within 6 ft of the paddy (BUND_REACH_FT) counts as on the bund` - claim it: a lane end within 6 ft of the paddy (BUND_REACH_FT) counts as on the bund
  - `l7r/diagram/hamletgen/ways/bund.py::a_way_onto_the_bund#branched field path 5 ft wide (BRANCH_WIDTH)` - claim it: branched field path 5 ft wide (BRANCH_WIDTH)
  - `l7r/diagram/hamletgen/ways/bund.py::a_way_onto_the_bund#the branched field path 5 ft wide (BRANCH_WIDTH) with the LANE_CLEARANCE corridor` - claim it: the branched field path 5 ft wide (BRANCH_WIDTH) with the LANE_CLEARANCE corridor
  - `l7r/diagram/hamletgen/ways/bund.py::carry_on#stepped field path 5 ft wide (BRANCH_WIDTH)` - claim it: stepped field path 5 ft wide (BRANCH_WIDTH)
  - `l7r/diagram/hamletgen/ways/bund.py::carry_on#the stepped field path drawn 5 ft wide (BRANCH_WIDTH)` - claim it: the stepped field path drawn 5 ft wide (BRANCH_WIDTH)
  - `l7r/diagram/hamletgen/ways/law_water.py::oblique_at#square ditch crossing` - cite 0087 (a carried deck crosses at an angle, solved for it) against the code's 10 degree squaring of a channel crossing; the question is the found row law_water.py::oblique_at#a channel crossing at its way's angle (E4)
  - `l7r/diagram/hamletgen/ways/serve.py::_lay_web_lane#a run within 25 ft of the network counts as arrived (_LANE_JOIN_FT)` - claim it: a run within 25 ft of the network counts as arrived (_LANE_JOIN_FT)
  - `l7r/diagram/hamletgen/ways/serve.py::_lay_web_lane#link kept 8 ft off hard ground, 7 ft off walls` - claim it: link kept 8 ft off hard ground, 7 ft off walls
  - `l7r/diagram/hamletgen/ways/street.py::row_reach#a farm frame taken as 100 ft where none is recorded (0033 gives 220-260 ft)` - claim the frame fallback against 0033 (a row village's holding 220-260 ft): BUNDLE_PITCH where none is recorded; the difference is fixed by the found row street.py::row_reach#a farm frame where none is recorded (E1)
  - `l7r/diagram/hamletgen/ways/web.py::_lay_skeleton#each skeleton arm registers the 40 ft LANE_CLEARANCE no-build corridor` - claim it: each skeleton arm registers the 40 ft LANE_CLEARANCE no-build corridor
  - `l7r/diagram/hamletgen/ways/web.py::_lay_skeleton#skeleton arm's no-build corridor LANE_CLEARANCE, 7 ft` - claim the skeleton arm's no-build corridor as `LANE_CLEARANCE`, 40 ft as a center corridor, against 0246's 7 ft to a fence; the difference is fixed by the edge-based corridor row (consts.py::LANE_CLEARANCE, E3)
  - `l7r/diagram/settlement/civic_grounds/civic.py::CivicWorksMixin.precinct_interior#parish plot seated at the precinct's rear, east of the axis (x+44, 14 px in from the rear edge)` - claim it: parish plot seated at the precinct's rear, east of the axis (x+44, 14 px in from the rear edge)
  - `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cemetery#no six jizo drawn at a burial ground's entrance unless a cremation ground stands beside it` - claim it: no six jizo drawn at a burial ground's entrance unless a cremation ground stands beside it
  - `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cremation_ground#cleared ground's depth 0.7 of its width` - claim it: cleared ground's depth 0.7 of its width
  - `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cremation_ground#fire bed always a stone-framed trench (never an open pyre)` - cite 0238 (the fire bed a stack of firewood or a stone-framed trench) against the code's trench alone; the second form is the found row funerary.py::cremation_ground#the fire bed's two forms (E3)
  - `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cremation_ground#snow-country walled hut over the bed never drawn` - claim it: snow-country walled hut over the bed never drawn
  - `l7r/diagram/settlement/structures/fixtures/_helpers.py::kosatsuba_handover#a through track's handover` - cite 0190 (a board at the village's center or its entrance, and at crossroads where people pass) for the junction nearest the houses' middle

  - `l7r/diagram/hamletgen/ways/law_water.py::short_decks#assumed water widths` - Set the fallback widths in short_decks to the record's: a field ditch 2.5 ft (its head, 0084) in place of 3.0, and a stream 7 ft (0035) in place of 6.0, citing those pages; the channel's 3 ft stays claimed UNRESEARCHED.
  - `l7r/diagram/hamletgen/ways/street.py::row_reach#a farm frame where none is recorded` - take a farm frame where none is recorded at 0033's 220-260 ft (a row village's holding) in place of the BUNDLE_PITCH fallback
  - `l7r/diagram/overlap/taxonomy.py::_LABEL_GROUP#a caption covers its own group` - the funerary group and the samurai caption's estates are in step (wave 7); left: give the temple group the word 'shrine' and the gate group 'guard' and 'inspection' (0243: a temple's or shrine's name covers the temples; a guard-house or inspection caption the gate's guard-houses and inspection posts)
  - `l7r/diagram/settlement/city/walls.py::WallsMixin._seat_mural_towers#exempt stretches` - the coverage sweep exempts all four of 0148's stretches: add 135 ft of a water gate and 186 ft of a ward gate to the 390 ft of a gate and 165 ft of its guard buildings
  - `l7r/diagram/settlement/civic_grounds/civic.py::CivicWorksMixin.terrace#cell frontage` - Grow the terrace's default cell to the drawing page's Rank 1-4 unit of about 990 sq ft (0140 drawing) from 18 x 24 ft (432 sq ft), the frontage/depth split labeled GUESS.
  - `l7r/diagram/settlement/civic_grounds/civic.py::CivicWorksMixin.terrace#range depth` - size the drawn terrace unit to the drawing page's about 990 sq ft (Rank 1-4) in place of Shibata's 18 x 24 ft (432 sq ft) cell
  - `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cemetery#keep-clear margin` - Set the cemetery's block band bm from 8 px to 0, so it blocks only the plot's own ground (0224: no cleared band is drawn, other features placed without regard to it; 0235: no set distance from houses), and cite 0224/0235.
  - `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cemetery#rows of low markers` - start the first row a marker's height inside a ruled plot's edge (or test each marker's top against the plot as against the blob) so every marker stands wholly inside the ground
  - `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cremation_ground#keep-clear margin` - Set the cremation ground's block band m from 8 px to 0 (0238: no fire clearance is drawn around a pyre), with the 120 ft from houses and wells cited to 0238 where edge_seat holds it (roll.py clear_px=self.px(120)).

- [x] T29a the found rows tiered provisionally by verdict read and tiered by the work they take, by a fresh reader, before
      the wave chooses its rows (FR-002, FR-003, SC-003)
      research: rendering
      verify: DONE. DONE. 14 rows tiered by their work by a fresh Opus reader (audit/t29a-out.jsonl, each reason measured in the code), applied in audit/overrides.json: 11 moved
- [x] T30 the bookend pair, back to back: `make perf LABEL=328-start` in a detached worktree at main's engine, then
      `LABEL=328-end` in the clone (constitution VI)
      research: rendering
      verify: DONE. DONE. 328-start in a detached worktree at origin/main, 328-end in the clone, back to back (a first pair that overlapped a detached run was discarded): band 1 (40 hh +1.3%); explanation UNVERIFIED, perf-audit CONSISTENT by alternating counterfactual runs (the two changed functions called 0 times on the perf seeds)
- [x] T31 the open E0 claims; then the E1 rows, each fixed toward the page it cites (DEVIATION only through the exception
      path), with the unit tests it moves; proven on the reference hamlet and the pool through the gate, a town or city value
      by its unit test; a value that makes a map refuse is held and the row takes the tier of the work it needs (FR-004,
      FR-005, spec Edge Cases)
      research: rendering
      verify: DONE. DONE. The 18 E0 claims (each stating a drift names its found row, D8); the E1 rows: short_decks' widths 2.5/7 ft, ROW_FRAME_FT 240 ft (0033), the temple and gate caption words, the city wall's four exempt stretches, the terrace unit 33 x 30 ft (990 sq ft), the cemetery's and cremation ground's margins 0, the cemetery's first row inside its edge; the pool through the gate, city values by their unit tests
- [x] T32 every touched unit re-checked by `impl-drift`; each wave-8 row IN-STEP or re-tiered with its measured reason (FR-005, SC-002)
      research: rendering
      verify: DONE. DONE. impl-drift on every touched unit (bundles A-C of wave 8; make claims-owed: no claim is owed); 25 rows closed (6 IN-STEP, 19 claimed under their unit's label), 2 more on their re-checks; findings ranked as found rows (found-wave8.jsonl)
- [x] T33 the close: the band's records, `make done` green, the wave column, landed (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. DONE. make done green (202 s); band 1 explained and confirmed; the wave column written

## Phase 10 - the scope (amendment 8, the GM 2026-10-07), then wave 9 (the open in-scope E0 claims, then in-scope E1 rows 265-297)

The feature now fixes the code the kept maps execute (FR-010): every ranked row takes a scope from the kept maps' own
execution records and the `hamletgen/` rule (`audit/scope.py` -> `audit/scope.json`, a column of `ranking.md`), every claimed
unit outside it is listed in `dev/claims-deferred.json`, and `make claims-report` shows their findings DEFERRED
(`scripts/_claims.py`, tested). T34a: the 5 found rows wave 8 tiered by verdict alone are tiered by their work by a fresh
reader (`audit/t34a-out.jsonl`, 3 moved). Then the 5 open in-scope E0 rows (SC-003), each a claim written or relabeled
(DEVIATION only after the exception path rules it LEGITIMATE), and the next contiguous run of in-scope E1 rows (FR-006), rows
265-297 in ranking order (the next open in-scope E1 row is 303). Every `after` these rows carry is a row inside the wave or
closed.

  - `l7r/diagram/hamletgen/ways/bund.py::a_way_onto_the_bund#field path width` - Split the claim: keep 0081 for the 5 ft `BRANCH_WIDTH` spur, and claim the `LANE_CLEARANCE` corridor separately against 0246 (a lane's middle 7 ft clear of a garden fence), naming the 40 ft center-corridor drift as fixed by the edge-based corridor row (consts.py::LANE_CLEARANCE, E3).
  - `l7r/diagram/hamletgen/ways/serve.py::_lay_web_lane#a healing link kept if its ends lie within 12 ft of the run and of the network (`_reach < 12.0`, `_net_reach < 12.0`), a` - claim it: a healing link kept if its ends lie within 12 ft of the run and of the network (`_reach < 12.0`, `_net_reach < 12.0`), a gap left unjoined
  - `l7r/diagram/hamletgen/ways/serve.py::_lay_web_lane#link off hard ground and walls` - Split the claim: the 7 ft off walls (`tight_margin=WEB_FABRIC_GAP` in the link's `clear_runs`) cites 0246's 7 ft from a garden fence to a lane's middle, and the 8 ft off hard ground (`WEB_HARD_GAP`) stays UNRESEARCHED.
  - `l7r/diagram/labels/obstacles.py::GROUP_WORDS#a guard or inspection caption may cover the gate's posts (0243 §9)` - claim it: a guard or inspection caption may cover the gate's posts (0243 §9)
  - `l7r/diagram/labels/obstacles.py::GROUP_WORDS#a shrine caption may cover the temples (0243 §11)` - claim it: a shrine caption may cover the temples (0243 §11)

  - `l7r/diagram/settlement/farm_fixtures.py::KURA_PARTS#west annex` - W annex 0.32 x 0.56 (15 x 16 ft) -> 18-27 ft long, 10-12 ft deep, 1.5-1.8 to one
  - `l7r/diagram/settlement/farm_fixtures.py::kura_rect#west annex size` - hold the west annex to 0040 drawing's band: 18-27 ft long, 1.5-1.8 times as long as deep, as the north annex is
  - `l7r/diagram/settlement/fields/comb.py::CombMixin._comb_draw_ditches#outfall recorded width` - record the outfall's width as the inked _dw, not 2.5
  - `l7r/diagram/settlement/fields/comb.py::CombMixin._comb_draw_hem#bank beside the source brook` - measure the bank margin from the 7 px brook actually drawn (7/2 + 3) and label the 3 px a GUESS
  - `l7r/diagram/settlement/fields/comb.py::CombMixin._comb_draw_source#pond feeder width` - pond feeder from width=6 to ~3 ft (twice the 1.5 ft floor), converted per map
  - `l7r/diagram/settlement/fields/comb.py::CombMixin._comb_source_channel#feed recorded width` - record the feed width as 6.0, the head race it traces
  - `l7r/diagram/settlement/fields/features.py::FieldFeaturesMixin.pond#pond feeder width` - pond feeder stroke from fixed 5 px to ~3 ft converted per map
  - `l7r/diagram/settlement/homestead_parts/belt_law.py::MIN_BELT_DEPTH_FT#least belt depth` - MIN_BELT_DEPTH_FT 30 -> 80 ft (0071 drawing: never thinner than 80 ft)
  - `l7r/diagram/settlement/homestead_parts/fixture_seats.py::PRIVY_FRONT_STEP_FT#front privy off the front wall` - front privy edge 8 ft off the front wall: drop the WALL_GAP_FT from the seat (or PRIVY_FRONT_STEP_FT 4.5)
  - `l7r/diagram/settlement/homestead_parts/fixture_seats.py::PRIVY_YARD_STEP_FT#yard outhouse off the back wall` - yard privy edge a ken (6 ft) off the back wall: drop the gap (or PRIVY_YARD_STEP_FT 2.5)
  - `l7r/diagram/settlement/homestead_parts/fixture_seats.py::WOODSHED_STEP_FT#wood shed off its wall` - wood shed edge 6 ft off its wall: drop the gap from the seat (or WOODSHED_STEP_FT 2.5)
  - `l7r/diagram/settlement/homestead_parts/fixture_seats.py::privy_sun_reach_ft#sun-side reach by size` - cap a sunny-side privy center at 48 ft from its house; drop the size allowance in privy_sun_reach_ft
  - `l7r/diagram/settlement/homestead_parts/groves.py::GrovesMixin._draw_grove#lesser broadleaf crown size` - LESSER_BROADLEAF_S floor 0.6 -> 0.75 of the mean radius (0080 drawing: 0.75-1.4), cite 0080
  - `l7r/diagram/settlement/homestead_parts/groves.py::GrovesMixin._draw_grove#windbreak conifer share` - windbreak conifer share c_th = b_th + 0.48 (0072/Takehara: 48% cedar, the dominant tree)
  - `l7r/diagram/settlement/homestead_parts/stands.py::StandsMixin.village_grove#belt deep and whole` - village_grove gap test compares px(_BELT_GAP_FT), 30 ft at every grain
  - `l7r/diagram/settlement/homestead_parts/stands.py::StandsMixin.village_grove#clumps off the gardens' east` - the east lane 50 ft in feet (0038: no crown within 50 ft east, west or south of a yard or bed), yards included, not 24 px past a garden
  - `l7r/diagram/settlement/homestead_parts/grove_rules.py::EAST_REACH_PX#garden's morning sun` - EAST_REACH_PX 22 bscale -> 0038's 50 ft east reach via px() (after: l7r/diagram/settlement/homestead_parts/wood_share.py::EAST_LANE_PX#bed's morning lane)
  - `l7r/diagram/settlement/homestead_parts/wood_share.py::EAST_LANE_PX#bed's morning lane` - EAST_LANE_PX 24 px -> 0038's 50 ft via px() (after: l7r/diagram/settlement/homestead_parts/grove_rules.py::EAST_REACH_PX#garden's morning sun)
  - `l7r/diagram/settlement/homestead_parts/grove_rules.py::gardens_east_shaded#garden's morning sun` - same constant: gardens_east_shaded reads the 50 ft reach (0038) via px() (after: l7r/diagram/settlement/homestead_parts/grove_rules.py::EAST_REACH_PX#garden's morning sun)
  - `l7r/diagram/settlement/land/cover.py::GroundCoverMixin.commons#scrub ground color` - drop the straw-gold solid fill under the commons tufts (0078: no solid fill, no outline)
  - `l7r/diagram/settlement/land/dikes.py::DikeMixin.dike_gates#gate glyph at the polder cut` - draw the dike gate at a 16-24 ft sluice span, passing the span to the glyph frame
  - `l7r/diagram/settlement/land/wet.py::water_lines#watered by surface water` - water_lines includes irrigation channels and ponds per 0196 drawing (drop the 'never an irrigation ditch' exclusion)
  - `l7r/diagram/settlement/land/wet.py::surface_water_dist#watered by surface water` - count irrigation channels as surface water in surface_water_dist (via water_lines) (after: l7r/diagram/settlement/land/wet.py::water_lines#watered by surface water)
  - `l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_layout#garden size` - nucleated garden cap 48 x 34 ft -> a cap whose area stays <= 1,507 sq ft (e.g. 44 x 34 ft), per 0039
  - `l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_layout#headman keeps an ordinary yard and garden` - headman's garden held to an ordinary farm's: the same lowered cap (<= 1,507 sq ft, near the 592 sq ft typical) applies to a big house (after: l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_layout#garden size)
  - `l7r/diagram/settlement/rolling/fit.py::BundleFitMixin._garden_shaded#garden shaded by a house to its south` - _garden_shaded reach gh + 4 px -> px(39) south of the bed (0038's 39 ft house-shade corridor)

- [x] T34 the scope applied: `audit/scope.py` and `audit/scope.json`, the ranking's scope column (`audit/merge.py`),
      `dev/claims-deferred.json` over every claimed unit, and `make claims-report` showing a deferred unit's findings DEFERRED
      (`scripts/_claims.py`, its test); the Mode A sheets' records taken (`make map`) so the scope sees them (FR-010)
      research: rendering
      verify: DONE. DONE. audit/scope.py (the kept maps' own execution records, all of hamletgen/, knobs resolved by name or by typing rule, constructed classes, measured per-claim exceptions) -> audit/scope.json and the ranking's scope column; dev/claims-deferred.json over every claimed unit (897 units, 14 claims); make claims-report shows their findings DEFERRED (158), the push's claims gate skips them (scripts/_claims.py, tested); the Mode A records taken with make map
- [x] T34a the in-scope found rows tiered provisionally by verdict read and tiered by the work they take, by a fresh reader
      (FR-002, FR-003, SC-003)
      research: rendering
      verify: DONE. DONE. 5 rows tiered by their work by a fresh Opus reader (audit/t34a-out.jsonl): 3 moved
- [x] T35 the bookend pair, back to back: `make perf LABEL=328-start` in a detached worktree at main's engine, then
      `LABEL=328-end` in the clone, nothing else running (constitution VI)
      research: rendering
      verify: DONE. the pair taken back to back (dev/perf-log 328-start at main, 328-end in the clone): band 3 - total +8.9%, seed 25 +15.0% (notice +0.7 s), 20 hh seed 39 +21.8%; explained (the board's seat search on layouts the wave moved: 3 routes and 7,932 seat fits against 2, a found row to index it), perf-audit dispatched; the GM's sign-off owed (band 3). A first pair with the zigzag preference read band 3 too, and the preference was withdrawn
- [x] T36 the open in-scope E0 claims; then the E1 rows, each fixed toward the page it cites (DEVIATION only through the
      exception path), with the unit tests it moves; proven on the reference hamlet (Inashiro, its PNG looked at) and the pool
      through the gate; a value that makes a map refuse is held and the row takes the tier of the work it needs (FR-004,
      FR-005, spec Edge Cases)
      research: rendering
      verify: DONE. the 5 E0 claims and E1 rows 265-297 fixed toward their pages; held by row where the gate or a measured roll needed it (FR-004): the yard privy's step (Kuwabata's zigzag across a joint, bisected by row) and the wood shed's step (three scaling rolls' web refusals, bisected by row), each E3 after its found row; three rows re-tiered (the commons fill E2, the surface water E4); the front step's label reopened as an E0 relabel (GUESS 0047); the entrance board's widened pass pruned to its reach (lossless, tested); Inashiro looked at; the pool through a green make done
- [x] T37 every touched unit re-checked by `impl-drift`; each wave-9 row IN-STEP or re-tiered with its measured reason (FR-005, SC-002)
      research: rendering
      verify: DONE. impl-drift on every touched unit (bundles A-I, scratchpad/w9, each recorded with make claims-checked); every finding a found row tiered by its work (T38a, T38b) or a held row's own stated drift (D8)
- [ ] T38 the close: the band's records, `make done` green, the wave column, landed (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify:


## Phase 11 - wave 10 (amendment 9): the open in-scope E0 claims, then in-scope E1 rows 290-354

Wave 9's re-checks found its found rows (`audit/found-wave9.jsonl`), every one tiered by its work by a fresh reader (T38a,
`audit/t38a-out.jsonl`; T38b, `audit/t38b-out.jsonl` and `audit/t38c-out.jsonl`); the NEEDS-RESEARCH rows are E4, the research
first (spec Edge Cases). With them, the last 20 in-scope E1 rows in ranking order, rows 290-354 (FR-006). The four DEVIATION relabels (the planted pond bank, the crowns-per-clump floor and ceiling, the north-wall storehouse) went
through the exception path and were ruled NOT LEGITIMATE: the floor and the ceiling are dropped (E1), the bank's two forms
and the free-standing storehouse are E3, and the two annex claims move with the storehouse. Every `after` these rows carry is a row inside the wave or closed. The next open in-scope row is E2, row 355. WAVE 10
BEGINS ONCE WAVE 9 IS PUSHED (FR-006) - or as the exception check rules (plan, Wave 10).

  - `l7r/diagram/hamletgen/ways/tree.py::admits#track out's width as judged` - add to admits' Research block (tree.py:193-198): "track out's width as judged - research/questions/0081-village-lanes.drawing.html: the track out's stub (`_root`) judged at 6 ft, the track out as drawn", pointing at tree.py:205
  - `l7r/diagram/settlement/fields/comb.py::CombMixin._comb_draw_hem#default watercourse widths` - add to _comb_draw_hem's Research block (comb.py:373-378): 'fallback watercourse widths - UNRESEARCHED: stream 9, channel 2.5, canal 14 px where a record carries no w' (the same label wellground.py:30 gives the same tuple)
  - `l7r/diagram/settlement/fields/comb.py::CombMixin._comb_draw_hem#nothing on a dry plot` - add to _comb_draw_hem's Research block: 'nothing built or planted on a dry plot - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: each drawn hem plot registered in block_polys (no building) and dry_polys (no grove clump, fringe or scatter)', pointing at comb.py:444-445
  - `l7r/diagram/settlement/homestead_parts/fixture_seats.py::PRIVY_FRONT_STEP_FT#front privy off the front wall` - relabel GUESS research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: 8 ft (the page records the 8 ft as its own guess); the code's 8 ft edge stands
  - `l7r/diagram/settlement/homestead_parts/fixture_seats.py::_seats#manure heap fallback spots` - fixture_seats.py:478: add a claim for the manure heap's fallback spots (beside the privy at 1.1 and 1.9 widths, 10 ft further out, lines 503-512) and its no-privy seats at 0.3 hw / 0.3 hh (line 501), UNRESEARCHED
  - `l7r/diagram/settlement/homestead_parts/fixture_seats.py::_wood_shed#wood shed fallback seats` - fixture_seats.py:383: add a claim for the fallback seats paced a further STEP_FT (8 ft) out (outward(seats, px(STEP_FT), 1), line 386), UNRESEARCHED
  - `l7r/diagram/settlement/homestead_parts/groves.py::GrovesMixin._draw_grove#bamboo patch forced` - groves.py:~720: add a claim for in_box(..., bamboo_box) at :788 forcing an item to bamboo in any mix and even when bamboo=False, citing research/questions/0075-bamboo-groves-chikurin.drawing.html (the farm's patch) or UNRESEARCHED
  - `l7r/diagram/settlement/homestead_parts/groves.py::GrovesMixin._draw_grove#crown over no roof or wellhead` - groves.py:727: add research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html for the wellhead (a wellhead in a belt removes the clumps round it) beside 0071
  - `l7r/diagram/settlement/homestead_parts/stands.py::StandsMixin.village_grove#clump inside the page window` - stands.py:~252: add a claim, CONVENTION, that a clump is kept only when part of its crown falls inside the page window
  - `l7r/diagram/settlement/homestead_parts/stands.py::StandsMixin.village_grove#clump off buildings, wells and shrines` - stands.py:250: narrow the claim to buildings (0071 section 15) and add a separate UNRESEARCHED claim for the wellhead keep-out vr + 1.05 clump + 1 (line ~91)
  - `l7r/diagram/settlement/homestead_parts/stands.py::StandsMixin.village_grove#copse mix` - stands.py:~252: add a claim that the copse is drawn in the dooryard mix (fruit and broadleaf, no bamboo or conifer), citing research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html as groves.py:722 does
  - `l7r/diagram/settlement/homestead_parts/stands.py::StandsMixin.village_grove#copse off the whole marsh` - stands.py:~252: add a claim that the copse is kept off the whole marsh, not only the deep marsh, citing research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html (woody cover on the dry ground above it)
  - `l7r/diagram/settlement/homestead_parts/stands.py::StandsMixin.village_grove#wellhead canopy keep-out` - stands.py:~252: add a claim for the wellhead keep-out vr + clump * 1.05 + 1.0 (line ~91), UNRESEARCHED or citing 0071/0072 for the wellhead
  - `l7r/diagram/settlement/homestead_parts/wood_share.py::WoodShares.__init__#afternoon lane as the copse plants` - relabel wood_share.py:249-250 from NONE to 'research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: the map's west_sun_lane, 50 ft (WEST_SUN_FT) west and southwest of each yard and bed on the scripted hamlets, as the copse plants it (stands.py _west_sun_ft); none where a map declares none'
  - `l7r/diagram/settlement/homestead_parts/wood_share.py::WoodShares.__init__#copse clump size` - add to WoodShares.__init__'s Research block (wood_share.py:246-251): 'copse clump size - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: COPSE_CLUMP_BS, 22 bscale units', the constant's own claim at line 57
  - `l7r/diagram/settlement/homestead_parts/wood_share.py::WoodShares.__init__#copse seat pitch` - add 'copse seat pitch - CONVENTION: SEAT_PITCH_BS, the clump radius times the square root of two, so the reserved crowns cover every point of a cell' to WoodShares.__init__'s Research block (and a Research line under SEAT_PITCH_BS at wood_share.py:61)
  - `l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_geom#grove cleared east of turned beds` - bundle.py:148 _bundle_geom docstring: add a claim for clear_east_of_beds (a dispersed farm's grove cleared 50 ft east of its turned beds), citing research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html
  - `l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_layout#south band off an unkept yard` - bundle.py:277: add a claim for the non-sun-keeping case (yard_sun=YARD_SUN_STRIP, 22, unscaled, line 382), UNRESEARCHED
  - `l7r/diagram/settlement/structures/fixtures/siting.py::FixtureSitingMixin._board_for#anchored board band` - add to _board_for's Research block (siting.py:417-423): 'anchored board band - UNRESEARCHED: within KOSATSUBA_ANCHOR_BAND_FT, 60 ft, of the nearest seat to the anchor, the board's 60 ft siting distance reused (research/questions/0190-notice-boards-kosatsuba.drawing.html calls the 60 ft this project's own figure)', pointing at siting.py:440
  - `l7r/diagram/settlement/structures/fixtures/siting.py::FixtureSitingMixin._board_for#handover band` - add to _board_for's Research block: 'handover band - UNRESEARCHED: an entrance board within KOSATSUBA_HANDOVER_BAND_FT, 20 ft, of the nearest seat to the handover, where every departure passes', pointing at siting.py:448-449 (the constant's claim at _helpers.py:92)

  - `l7r/diagram/settlement/fields/comb.py::CombMixin._comb_draw_source#feeder brook width` - comb.py:651: width=7 -> width=self.px(7.0) (0059/0068: a brook about 7 ft wide), and drop "in px rather than feet" from the claim at comb.py:630
  - `l7r/diagram/settlement/homestead_parts/groves.py::GrovesMixin._draw_grove#crowns per clump ceiling` - drop the cap: a clump's crown count is 0080's density alone (round(area / GROVE_CROWN_AREA)); GROVE_CLUMP_CROWNS kept only where band_clumps cuts a band into clumps, claimed for that
  - `l7r/diagram/settlement/homestead_parts/groves.py::GrovesMixin._draw_grove#crowns per clump floor` - drop the floor: the count is 0080's density, rounded (no max(5, ...))
  - `l7r/diagram/settlement/homestead_parts/wood_share.py::copse_keepouts#south strip in feet` - scale the south strip's `sun_depth` (feet) by `ppf` as the east and west lanes are (copse_keepouts, wood_share.py:114)
  - `l7r/diagram/settlement/structures/fixtures/_helpers.py::kosatsuba_anchor#reaching the houses` - KOSATSUBA_ENTRANCE_REACH_FT becomes 60 ft, cited as GUESS to 0246 drawing (a way reaches a farmhouse within 60 ft of it), in place of 100 ft
  - `l7r/diagram/settlement/structures/fixtures/board_seat.py::FACING_DEG#board faces its way` - FACING_DEG from 45.0 to 30.0
  - `l7r/diagram/settlement/structures/fixtures/boards.py::BoardsMixin.board_record#board size` - board_record from px(12) x px(5) to px(16) x px(6)
  - `l7r/diagram/settlement/structures/fixtures/boards.py::BoardsMixin.kosatsuba#board size` - kosatsuba board 16 x 6 ft via board_record
  - `l7r/diagram/settlement/structures/fixtures/siting.py::FixtureSitingMixin._board_routes#lane fallback width` - lane fallback tread from 8 px to the recorded lane width in feet (0081's 3/5/6 ft via px), citing 0081
  - `l7r/diagram/settlement/structures/fixtures/siting.py::FixtureSitingMixin._route_seats#least offset off the tread` - least offset to 6 ft (px(6)) from the road edge, citing 0190
  - `l7r/diagram/settlement/structures/fixtures/siting.py::FixtureSitingMixin.place_kosatsuba#probe size` - probe the 7 x 3 ft face the page names instead of 12 x 5 ft floored at 11 px
  - `l7r/diagram/settlement/water_ways/lanes.py::LanesMixin.trim_lane_stubs#meeting another way` - trim_lane_stubs way_reach 40 -> 60 ft (px-scaled), per 0246
  - `l7r/diagram/settlement/water_ways/water.py::WaterBodiesMixin.stream#stream width` - stream width 9 raw px -> px(7) (0068's village brook)
  - `l7r/diagram/waterfields/carve.py::_dry_fields#off the water and the frame` - drop a cell that falls inside any supply canal's bank (local half-width + CANAL_BERM_FT), not only within 0.5 px of the painted edge
  - `l7r/diagram/waterfields/comb.py::_comb_drain#wandering line` - scale the drain wander by the map's scale: jitter +/-6 ft and sample spacing 120-170 ft converted to px (x grain/2)
  - `l7r/diagram/waterfields/hem.py::_comb_dry_and_beans#fork triangle planted dry` - fire the fork-triangle band only on a coarse grain: `grain < 1.0` (city), not `grain != 1.0`
  - `l7r/diagram/waterfields/polder.py::build_polder#acreage reckoned` - reckon acreage at the map's scale: area * ftpx**2 / 43560 (both sites), not *4
  - `l7r/diagram/waterfields/polder.py::build_polder#module size` - default module cell 150 -> 190 ft (converted at ftpx)
  - `l7r/diagram/waterfields/polder.py::unpoint_parcels#no parcel tapers to a point` - cut polder apexes under 25 deg (0005), not NEEDLE_DEG 15
  - `l7r/diagram/waterfields/ring_rules.py::MAX_STEPS#sideways steps` - MAX_STEPS 1 -> 0: no ring keeps a sideways step

- [x] T38a wave 9's found rows tiered by the work they take, by a fresh reader (FR-002, FR-003, SC-003)
      research: rendering
      verify: DONE. 29 rows tiered by their work by a fresh Opus reader (audit/t38a-out.jsonl): 4 moved (the drain outfall and the wood shed's front seat to E2, the crown size to E2, the feeder brook to E3); T38b, the 18 found after: 14 then 4 (audit/t38b-out.jsonl, audit/t38c-out.jsonl), 3 moved (the bed's east reach below it to E3, the copse's sun strip to E1, the board's traffic floor to E3)
- [x] T39 the open in-scope E0 claims, each written or relabeled (a DEVIATION only after the exception path rules it
      LEGITIMATE); then the E1 rows, each fixed toward the page it cites, with the unit tests it moves; proven on the reference
      hamlet (Inashiro, its PNG looked at) and the pool through the gate; a value that makes a map refuse is held and the row
      takes the tier of the work it needs (FR-004, FR-005, spec Edge Cases)
      research: rendering
      verify: DONE. the 20 open in-scope E0 claims written and the 20 E1 rows fixed toward their pages (the notice board 16 x 6 ft, a 7 x 3 ft probe, 30 degrees, 6 ft off the road, entrance at 60 ft; 3 ft lane fallback; stubs to 60 ft; a 7 ft brook and feeder; clump crowns at 0080's density, no floor or cap; the fork triangle on a city's grain; the drain's wander in feet; no sideways ring step; the polder's acreage, module and 25 degree apex; the copse's south strip in feet); the four DEVIATION relabels ruled NOT LEGITIMATE and re-tiered; the canal's berm held (Inashiro's toe marsh, bisected), E3; Sawada's strict knot xfail restored (one knot where main has one); Inashiro looked at; the pool through a green make done; the notice board's glyph-check PASS
- [x] T40 every touched unit re-checked by `impl-drift`; each wave-10 row IN-STEP or re-tiered with its measured reason (FR-005, SC-002)
      research: rendering
      verify: DONE. impl-drift on every touched unit (bundles A-E, scratchpad/w10, each recorded with make claims-checked); the wave's own stale claim texts corrected and re-checked; every other finding a found row (audit/found-wave10.jsonl)
- [ ] T41 the bookend pair, back to back, and the close: the band's records, `make done` green, the wave column, landed (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify:


## Phase 12 - wave 11 (amendment 10): the last open in-scope E0 and E1 rows

Wave 10's re-checks found its found rows (`audit/found-wave10.jsonl`), each tiered by its work by a fresh reader (T42a,
`audit/t42a-out.jsonl`: 5 moved - the board's marker floor and the feeder brook against the head race to E4, the pond feeder's
record, the wood shed's fallback pace and the board's reach in feet to E2). The open in-scope E0 and E1 rows are these 11 -
every one left in the ranking (FR-006): 8 claims, then 3 values. After them every open in-scope row is E2 or above (the next,
row 365). Wave 11 starts on the unpushed waves 9 and 10 under amendment 9's second exception (plan, Wave 10: the GM's band-3
sign-off the only thing between them and main).

  - `l7r/diagram/settlement/homestead_parts/groves.py::GrovesMixin._draw_grove#mixed broadleaf belt` - add a claim to groves.py::_draw_grove: 'mixed broadleaf belt - 0072: rounded broadleaf crowns in the woods' size mix, no conifer'
  - `l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_layout#dispersed well pocket` - add a claim to bundle.py::_bundle_layout: 'dispersed well pocket - UNRESEARCHED: the wellhead plus a 3 ft margin, 2 * _well_vr() + px(6.0)' (bundle.py:390), as _lay_well_pocket's (:412)
  - `l7r/diagram/waterfields/carve.py::_dry_fields#end plot split` - add a claim to waterfields/carve.py::_dry_fields: 'end plot split - NONE: an end cell stretched past 1.35 plot widths by the snap to the canal's length is halved, coarse grains only (carve.py:119)'
  - `l7r/diagram/waterfields/comb.py::_comb_drain#straight last leg` - add a claim to waterfields/comb.py::_comb_drain: 'straight last leg - UNRESEARCHED: no jittered sample within DRAIN_MIN_LEG (84 px) of the outfall' (comb.py:619)
  - `l7r/diagram/waterfields/polder.py::_apex#polder plumbing` - relabel the claim on waterfields/polder.py::_apex: cite 0005 (no basin tapers to a point sharper than 25 degrees), POLDER_APEX_DEG = 25.0 at polder.py:839, the sharpest convex corner taken first
  - `l7r/diagram/waterfields/polder.py::build_polder#interior bund node jitter` - add a claim to build_polder: 'hand-piled outlines - 0014: each parcel softened by organic (fillet 0.05 of the module, bow 0.02)' (polder.py:41), the node jitter itself already claimed in _polder_lattice
  - `l7r/diagram/waterfields/polder.py::build_polder#low rows wet` - re-check: _polder_parcels flags low = r >= rows - 2 (polder.py:364) and tints every low plot FLOODED (:371), merges never straddle the band (:380); 0007 says a polder tints every low plot (22 of 22 on Enokida) - reword the claim at polder.py:98 and :334 to 'every low plot, the two lowest rows as the drawing's low band'
  - `l7r/diagram/waterfields/polder.py::build_polder#module line bow` - add a claim to build_polder: 'module line bow - 0014: each row and column line bowed up to line_wander 0.10 of the module, off the boundary lines' (polder.py:40, applied in _polder_lattice)

  - `l7r/diagram/settlement/fields/comb.py::CombMixin._comb_draw_hem#fallback watercourse widths` - settlement/fields/comb.py:395: replace the fallback widths (streams 9.0, channels 2.5, canals 14.0 px) with 0068's in feet at scale (self.px(7.0), self.px(4.5), self.px(6.0)) and relabel the claim at :378 to cite 0068
  - `l7r/diagram/settlement/water_ways/lanes.py::LanesMixin.trim_lane_stubs#arrival at the bund` - settlement/water_ways/lanes.py:335: compare edge_dist against self.px(BUND_REACH_FT) instead of the bare BUND_REACH_FT, and relabel the claim at :263 as GUESS 0014 (the page gives no 6 ft)
  - `l7r/diagram/waterfields/polder.py::build_polder#gaps` - waterfields/polder.py:36: express the default gap (1.5, 4.0) px in feet scaled by ftpx (a 3 ft bund and an 8 ft corridor at any scale, i.e. 1.5/ftpx and 4.0/ftpx)

- [x] T42a wave 10's found rows tiered by the work they take, by a fresh reader (FR-002, FR-003, SC-003)
      research: rendering
      verify: DONE. 19 rows tiered by their work by a fresh Opus reader (audit/t42a-out.jsonl): 5 moved
- [x] T43 the claims written and the values fixed toward their pages, with the unit tests they move; proven on Inashiro and the
      pool through the gate; a value that makes a map refuse is held as its found row (FR-004, FR-005)
      research: rendering
      verify: DONE. the 8 claims written and the 3 values fixed toward their pages (the hem's fallback widths in feet, 0068 and 0059; the stub's bund reach in pixels; the polder's default gaps in feet); no pool map moved (the census unchanged); the pool through a green make done
- [x] T44 every touched unit re-checked by `impl-drift` (FR-005, SC-002)
      research: rendering
      verify: DONE. impl-drift on every touched unit (w11bA, w11bB recorded); the wave's own mislabels corrected; every other finding a found row (audit/found-wave11.jsonl)
- [x] T45 the bookend pair, wave 11's own (opening at wave 10's closing commit), and the close: the band's records, `make done`
      green, the wave column (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. wave 11's own pair (328-start at 6be618a9e, 328-end at the clone): band 0, owes nothing; make done green; the wave column written; before any push the main-to-HEAD landing pair is retaken as the newest pair (plan, Wave 11)


## Phase 13 - wave 12 (amendment 11): wave 11's found E0 and E1 rows

Wave 11's re-checks found 12 rows (`audit/found-wave11.jsonl`), each tiered by its work by a fresh reader (T46a,
`audit/t46a-out.jsonl`: none moved). The open in-scope E0 and E1 rows are these 10 - 8 claims, then 2 values in feet; after
them every open in-scope row is E2 or above (the next, row 375). Wave 12 starts on the unpushed waves 9-11 under the wave-11
exception's condition (6): conditions (1)-(5) still held when wave 11 closed (6760d9bbf, its backup pushed, its own pair band 0).

  - `l7r/diagram/settlement/fields/comb.py::CombMixin._comb_draw_hem#coarse-grain top-up` - settlement/fields/comb.py _comb_draw_hem docstring (after line 376), add: 'coarse-grain top-up - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: the reserve plots `_coarse_grain_top_up` returns are drawn after the refused plots, by the same refusal rule'
  - `l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_layout#grove pad` - settlement/rolling/bundle.py _bundle_layout docstring, add: 'frame padded for a lane - GUESS research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: half `LANE_ROOM_FT` (16 ft) on every side, so neighbors' groves stand 32 ft apart'
  - `l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_layout#service strip` - settlement/rolling/bundle.py _bundle_layout docstring, add: 'service strip - GUESS research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the windward stand `SERVICE_STRIP_FT` (24 ft) off the back and windward end walls, sized to seat a wood shed'
  - `l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_layout#thin band width` - settlement/rolling/bundle.py _bundle_layout docstring, add: 'thin band - GUESS research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: a grove side away from the wind one tree deep, `THIN_BAND_FT` 17 ft (two 0080 mean crown radii)'
  - `l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_layout#way in through the grove` - settlement/rolling/bundle.py _bundle_layout docstring, add: 'way in through a ring - GUESS research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: one `WAY_IN_FT` (36 ft) break at the front band's middle, sized so a lane can be routed through'
  - `l7r/diagram/waterfields/comb.py::_comb_drain#collector above the frame` - waterfields/comb.py _comb_drain docstring (after line 579), add: 'collector above the frame - UNRESEARCHED: the fitted collector lifted to stand 40 px (unscaled) above the frame's bottom edge (line 610)'
  - `l7r/diagram/waterfields/polder.py::build_polder#hand-piled outlines` - re-check: _polder_parcels (polder.py line 373) passes fillet=0.05 * cell to palette.organic_parcel, which draws each corner's two legs independently from fillet * triangular(0.12, 2.2, 0.7) (palette.py line 176) and roughens the arc by the corner's own reach - corner by corner from all but square to a broad sweep, as 0014 says; claim stands: 'hand-piled outlines - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: each parcel softened by `organic` (a fillet of 0.05 of the module, each corner's legs drawn 0.12-2.2x of it, a bow of 0.02)'
  - `l7r/diagram/waterfields/polder.py::build_polder#lattice unbent by default` - waterfields/polder.py build_polder docstring (after line 99), add: 'lattice unbent by default - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: a rice polder keeps its surveyed grid (`mosaic` 0, `edge_wander` 0); the dike-pond block passes its own mosaic'

  - `l7r/diagram/settlement/fields/comb.py::CombMixin._comb_draw_hem#bank margin in feet` - settlement/fields/comb.py line 407: replace the source brook's margin `7.0 / 2 + 3.0` with `self.px(7.0) / 2 + self.px(3.0)` (the drawn 7 ft brook's half-width plus a 3 ft bund at the map's scale), and reword the claim line 376 to 'a bund's width, 3 ft, past the drawn 7 ft brook's bank, at the map's scale'
  - `l7r/diagram/waterfields/polder.py::build_polder#toe ends run on 3 ft` - waterfields/polder.py line 144: `along_trunk(_on, _best, ..., 3.0)` becomes `along_trunk(_on, _best, ..., 3.0 / ftpx)` (ftpx is already a build_polder parameter); claim line 101 adds 'at the map's scale'

- [x] T46a wave 11's found rows tiered by the work they take, by a fresh reader (FR-002, FR-003, SC-003)
      research: rendering
      verify: DONE. 12 rows tiered by their work by a fresh Opus reader (audit/t46a-out.jsonl): none moved
- [x] T47 the claims written and the values fixed toward their pages; the pool through the gate (FR-004, FR-005)
      research: rendering
      verify: DONE. the 8 claims written and the 2 values in feet (the brook's bank margin, the polder toe's run); no pool map moved (the census unchanged); make done green
- [x] T48 every touched unit re-checked by `impl-drift`, and the close: wave 12's own bookend pair, `make done` green, the wave
      column (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. impl-drift on every touched unit (w12bA 24 IN-STEP, w12bB the corrected lattice claim IN-STEP), two byre values filed as found rows; wave 12's own pair (328-start at 6760d9bbf): band 0, owes nothing; the wave column written


## Phase 14 - wave 13 (amendment 12): the byre claims, then the procedure-only Mode A rows

The open in-scope rows after wave 12 are wave 12's two found byre claims (E0), then the E2 run, which opens with the Mode A
procedure rows. An exception check (2026-10-07) ruled there is nothing to ask the GM - the Mode A sheets are in scope by the
GM's own words - and that FR-003's own definition applies: a row whose fix redraws a hand-drawn sheet is E3. A fresh reader
sorted the 18 Mode A E2 rows by measuring the sheets (`audit/modea-sort-out.jsonl`): 6 redraw a sheet (the tubs at the entrance,
the barracks, the clerks at the dais, the well curbs, the country shrine's tubs, the granary's caption) and are E3; these 12
change only the procedure and record each sheet's roll in its notes. Amendment 12 round 1: the knobs whose pages say "rolled from the map's seed" were rolled (`random.Random(zlib.crc32(b"<sheet>:<knob>"))`): Hayakawa's shared arch lands on the form drawn; the second kami's rolls for Hayakawa's river kami and Ubame's wood kami land on ONE HALL where each is drawn in a shrine of its own, so that row is E3 (a redrawn sheet) and left this wave. With the two claims, wave 13 is these 13 rows. The next
open in-scope row is E2, row 393, the first kept-code rule (`hamletgen/cluster.py`).

  - `l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_layout#byre footprint` - the byre's footprint `BYRE_FT` 16.12 x 10.92 ft
  - `l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_layout#byre off the house` - the byre set `YARD_SHED_GAP_FT[0]`, 6 ft, off the house

  - `buildings.md::Outer court (administrative / public)#granary kept under a residence block` - the under-the-residence ceiling tied to the granary-weight knob: a terminal store may be the largest building (0098 drawing)
  - `buildings.md::Sacred features#burial ground beside the precinct` - burial ground placed by a knob, in the shrine's yard or apart from it, rolled/following the map; DEVIATION label dropped
  - `buildings.md::Sacred features#compound shrine arch` - compound shrine's arch optional (may have none) and shared-or-own a knob rolled per map, in procedure and notes
  - `buildings.md::Sacred features#grove` - grove covers the sides of the hall knob 8 gives (behind, sides, both, all round), not the whole precinct; 'swept' clearing dropped
  - `buildings.md::Walls and gates#threshold wards` - threshold wards bullet dropped from Walls and gates (no pair at any official's gate before present-day custom); no sheet still draws them
  - `buildings.md::Scale#salt ward marker` - salt ward marker claim and the Scale paragraph's salt-ward marker text dropped; Hayakawa's wards already off the sheet
  - `buildings/programs.md::Country shrine (a village district's shrine)#building size anchors` - widen the country shrine's size bands to the record: a sanctuary of 1 or 3 ken (Hie's 2-bay about 12 x 6 ft) and worship halls from about 18 ft (Hie about 18 x 12, Rokusha 9 tsubo), in the band, its table and the sheet sizing rule
  - `buildings/programs.md::Country shrine (a village district's shrine)#burial ground beside the precinct` - country shrine's burial ground rolls in the yard or apart on a knob, DEVIATION label dropped
  - `buildings/programs.md::Magistrate's manor (county magistracy)#formal visitors and the privacy baffle` - where office and residence share a compound the genkan is drawn on the office (0104 drawing), not on the residence's reception block
  - `buildings/programs.md::Magistrate's manor (county magistracy)#sand hearing court` - 'sand hearing court' -> roofed hearing court with a floor knob (white gravel or river cobbles), each plan taking one
  - `buildings/programs.md::Magistrate's manor (county magistracy)#tier knob` - capital tier's staff housing made a knob: outside (Edo yoriki) or inside (a domain's Edo estate)

- [x] T49 the claims written; the procedures changed toward their pages, each sheet's roll recorded in its notes, no sheet redrawn;
      the country shrine's bands widened in `types.json` and its table regenerated (FR-004, FR-005, FR-009)
      research: rendering
      verify: DONE. the two byre claims written; 11 procedure-only Mode A rows changed toward their pages (the granary ceiling, the burial ground knob in buildings.md and programs.md, the shrine arch knob with Hayakawa's seeded roll, the grove's sides, the threshold wards and the salt-ward marker dropped, the country shrine's bands widened in types.json and its table, the office's genkan, the hearing court's floor knob, the capital tier's housing knob), each sheet's form in its notes; no sheet redrawn; the second kami's seeded rolls land off two sheets' drawn forms, so that row is E3
- [x] T50 every touched claim re-checked by `impl-drift`, and the close: wave 13's own bookend pair, `make done` green, the wave
      column (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. impl-drift on every touched claim (w13 bundles A-E, 189 claims recorded; the wave's rows IN-STEP; 13 new findings filed); make done green; wave 13's own pair (328-start at c45460dd1) band 1, explained, perf-audit consistent; the wave column written

## Phase 15 - wave 14 (amendment 13): wave 13's found claims

Wave 13's re-checks of the procedure files found 13 rows (`audit/found-wave13.jsonl`), each tiered by its work by a fresh reader
(T51a, `audit/t51a-out.jsonl`): 3 moved - the tax-free fields E4 -> E0 (nothing drawn waits on research; the label alone), the
true-size paragraph and the wall-abutment rule E2 -> E3 (Ubame's bales drawn 6x3 ft, and structures 0.5 ft off a wall on Ubame,
Ochiba and the generated examples, would be redrawn). The open in-scope E0 rows are these 8 claims; after them every open
in-scope row is E1 (deferred only) or E2 and above, the next E2 row 393 (`hamletgen/cluster.py`).

  - `buildings.md::Checklist for a new diagram#practice ground sizing` - UNRESEARCHED -> GUESS 0165 drawing (its page: "The figure is a GUESS")
  - `buildings.md::Walls and gates#divider wall` - UNRESEARCHED -> 0092 drawing (the lighter plastered wall of a foot or more)
  - `buildings.md::Walls and gates#threshold stones` - UNRESEARCHED -> CANON, the GM's rulings of 2026-07-25 and 2026-09-26
  - `buildings/programs.md::Country shrine (a village district's shrine)#bell tower knob` - 0222 -> GUESS 0222 drawing (absent by default)
  - `buildings/programs.md::Country shrine (a village district's shrine)#grove and burial side knob` - CANON (the GM, 2026-09-20) for following the map; the off-map burial roll its own claim on 0226 drawing
  - `buildings/programs.md::Country shrine (a village district's shrine)#innermost arch one pitch off the hall` - CONVENTION -> GUESS 0220 drawing
  - `buildings/programs.md::Country shrine (a village district's shrine)#tax-free fields off the sheet` - 0221 -> 0221 drawing ("Nothing about the shrine's land or its income is drawn"); the fields themselves their own claim on 0221
  - `buildings/programs.md::Magistrate's manor (county magistracy)#inner-court postern` - GUESS 0101 drawing -> GUESS alone, saying what 0101's drawing page searched (no night-soil gate at a samurai house; the page records no such door)

- [x] T51a wave 13's found rows tiered by the work they take, by a fresh reader (FR-002, FR-003, SC-003)
      research: rendering
      verify: DONE. 13 rows tiered by their work by a fresh Opus reader (audit/t51a-out.jsonl): 3 moved (tax-free fields E4 -> E0 with its basis; true size and structures abut walls E2 -> E3)
- [x] T51 the 8 claims corrected - label, citation or wording only; no procedure text, sheet or code changes (FR-003 E0, FR-004)
      research: rendering
      verify: DONE. the 8 claims corrected by label, citation or wording only; impl-drift's re-check moved two (the tax-free fields onto 0221's drawing page, the postern a GUESS stating what 0101's page searched); no procedure text, sheet or engine line changed
- [x] T52 every touched claim re-checked by `impl-drift`, and the close: wave 14's own bookend pair, `make done` green, the wave
      column (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. impl-drift on every touched claim (w14 bundles A-B, 12 recorded, all IN-STEP at the last round); make done green (already verified, no engine change); wave 14's own pair (328-start at 2e0268412) band 1, explained, perf-audit consistent; the wave column written; the scope script now keeps the page path (73 units)

## Phase 16 - wave 15 (amendment 14): the reopened rows, the Mode A paragraphs and the drain at the seat

Wave 13's re-check found four rows of closed waves out of step again; the filer had skipped any key already ranked, and now
reopens it (`audit/found-wave13.jsonl`, `reopened`). A fresh reader tiered the four by their work (T53a, `audit/t53a-out.jsonl`):
the granary forms E0 (a claim split), the farmers' stage, the manor kitchen garden and the upland granary's strongbox role E2 -
no sheet redrawn. The open in-scope run is then the one E0 row and the E2 rows in ranking order, the Mode A paragraphs first and
then `hamletgen/cluster.py`'s drain rules; wave 15 is these 9 rows.

  - `buildings.md::Outer court (administrative / public)#granary forms` - split: the forms on 0098; the size a GUESS on 0098's drawing page, the terminal row at the office the question page's GUESS; the kura form's unshown vents a drawing convention
  - `buildings.md::Checklist for a new diagram#size hierarchy` - the checklist's ranks from 0116's drawing page (office hall, residence, rowhouse; the grain storehouse by the rice held); the cell's rank its own GUESS claim
  - `buildings/programs.md::Country shrine (a village district's shrine)#farmers' stage knob` - absent by default, claimed as 0222's drawing page's GUESS (the page: "absent by default ... unless they are turned on"); a roll was tried and withdrawn against that page
  - `buildings/programs.md::Country shrine (a village district's shrine)#no subsidiary buildings` - the drawing page's choice, with what the record shows: subsidiary shrines sometimes in a precinct, Rokusha's office in a register of 1872 or after
  - `buildings/programs.md::Country shrine (a village district's shrine)#sumo ring knob` - the same claim as the stage's: absent by default, 0222 drawing page's GUESS
  - `buildings/programs.md::Magistrate's manor (county magistracy)#manor kitchen garden by the sun` - the site knob among four and the size knob of 0109's drawing page, in the procedure (each sheet's notes already declare both)
  - `buildings/programs.md::Magistrate's manor (county magistracy)#upland granary strongbox role` - the strongbox clause and its claim dropped
  - `l7r/diagram/hamletgen/cluster.py::below_drain#wet side of the drain` - judged within the drain's span across the slope (0058 drawing): ground past either end is a dry flank
  - `l7r/diagram/hamletgen/cluster.py::seat_cluster#never below the drain` - the seat's drain refusal removed: 0058 keeps the ground below a drain from dispersed farmsteads only, not a nucleated cluster; the per-farm rule, which no seat ever enforced, filed E3 (`audit/found-wave15.jsonl`)

- [x] T53a the four reopened rows tiered by the work they take, by a fresh reader (FR-002, FR-003, SC-003)
      research: rendering
      verify: DONE. 4 rows tiered by their work by a fresh Opus reader (audit/t53a-out.jsonl): granary forms E0, the rest E2; no sheet redrawn
- [x] T53 the Mode A rows changed toward their pages: the claims, the procedure paragraphs and the regenerated table (FR-004, FR-005, FR-009)
      research: rendering
      verify: DONE. the Mode A rows changed toward their pages: granary claims split (forms, size GUESS, the vents a convention, one storehouse at the office with the row at the landing - the granary-weight row taken with it), the size hierarchy from 0116's drawing page, subsidiary buildings with what the record shows, the stage and sumo defaults claimed as 0222's GUESS (a roll tried and withdrawn against that page), the manor kitchen garden's two knobs, the strongbox clause dropped; the programs table regenerated
- [x] T54 `below_drain`'s span and the seat without the drain rule, with their tests; the pool hamlets regenerated (FR-004, FR-005)
      research: rendering
      verify: DONE. below_drain judged within the drain's span across the slope (test: past either end, a diagonal drain, a drain straight down the slope); the seat's drain rule removed with its tests rewritten; no pool hamlet's manifest changed (the rule never fired on one); the per-farm rule filed E3
- [x] T55 every touched claim re-checked by `impl-drift`, the modals' owed record checks, and the close: wave 15's own bookend pair,
      `make done` green, the wave column (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. impl-drift on every touched claim (w15 bundles, every wave row IN-STEP at the last round; findings filed and closed rows reopened); make done green; wave 15's own pair (328-start at 68ee171f4) band 1, explained, perf-audit consistent (its own alternating runs); the wave column written

## Phase 17 - wave 16 (amendment 15): the copse among the houses, the board on the frontage

Wave 15's re-checks found 7 rows; one was stale (the two-building dwelling size, IN-STEP on the second round) and dropped; a
fresh reader tiered the other 6 by their work (T56a, `audit/t56a-out.jsonl`): donated stonework E0, the privacy baffle E2, the
walled enclosure E3 (two gatehouses redrawn), and three E4 - two whose only remedy is a research page edited (the exception
path) and the checkpoint's staffing (research first). The open in-scope run is then the E0 row and the E2 rows in ranking order;
wave 16 takes the E0, the privacy-baffle paragraph, the copse rows (`COPSE_SITINGS` with `COPSE_BELT_REACH_FT` and
`stage_windbreak`'s two copse rows, one retirement) and the notice board's siting. The next open row is `WEB_HARD_GAP` (407).

  - `buildings/programs.md::Country shrine (a village district's shrine)#donated stonework` - split: the gifts on 0222; none at average a GUESS on its drawing page
  - `buildings/programs.md::Magistrate's manor (county magistracy)#formal visitors and the privacy baffle` - the visitors' way runs on through the office (0104 drawing); "go no deeper" dropped
  - `l7r/diagram/hamletgen/consts.py::COPSE_SITINGS#village copse siting` - among the houses only (0071 drawing); the against-the-belt form retired with `against_the_belt`, `copse_seat`, `lee_face`, its choice value and modal; Mizuguchi's declaration of it dropped
  - `l7r/diagram/hamletgen/consts.py::COPSE_BELT_REACH_FT#copse against the belt` - retired with the form
  - `l7r/diagram/hamletgen/hinterland/stages.py::stage_windbreak#against-the-belt copse clump` - retired with the form
  - `l7r/diagram/hamletgen/hinterland/stages.py::stage_windbreak#copse among the homes` - the copse only among the houses
  - `buildings/programs.md::Magistrate's manor (county magistracy)#granary weight knob` - reopened by this wave's re-check (wave 15 had written that an isolated county's storehouse may be the compound's largest building, against 0098's drawing page's single 43-50 x 25-27 ft granary): the clause dropped, the rank left to `buildings.md`'s own GUESS claim
  - `l7r/diagram/hamletgen/consts.py::KOSATSUBA_SITINGS#notice board siting` - the busiest frontage only (0190 drawing); the drawing-water bid, its choice value and modal retired

- [x] T56a wave 15's found rows tiered by the work they take, by a fresh reader (FR-002, FR-003, SC-003)
      research: rendering
      verify: DONE. 6 rows tiered by their work by a fresh Opus reader (audit/t56a-out.jsonl): 1 E0, 1 E2, 1 E3, 3 E4; the stale seventh dropped
- [x] T57 the two Mode A rows; the copse and board sitings retired in the engine, their tests, choices and modals; Mizuguchi, Kashikawa and Sawada regenerated (FR-004, FR-005)
      research: rendering
      verify: DONE. the donated stonework split; the privacy baffle to 0104; the copse against the belt and the board at the drawing-water place retired (no page behind either), with their code, tests, choice values and modals; the granary-weight clause the re-check reopened dropped; Mizuguchi, Kashikawa and Sawada regenerated - measured, nothing drawn moved (meta only)
- [x] T58 every touched claim re-checked by `impl-drift`, the occasions' glyph checks, and the close: wave 16's own bookend pair, `make done` green, the wave column (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. impl-drift on every touched claim (every wave row IN-STEP at the last round); occasions none, measured; make done green; wave 16's own pair (328-start at 799a0bf4b) band 1, caused by the retired copse form on seeds 39 and 47 at 40 hh (+0.2 s windbreak, timed by perf-audit), total -4.3%, perf-audit consistent; the wave column written

## Phase 18 - wave 17 (amendment 16): wave 16's claims and the thicket's reach

Wave 16's re-checks found 4 rows: one stale (the staff housing knob, IN-STEP on the later round), dropped with its closing wave
restored; the other 3 are UNCLAIMED decisions, E0 by their verdict - each needs only its claim. Then the E2 run: `WEB_HARD_GAP`
(410) is measured to be a change across five modules (the hard ground is one list read with one gap by `ways/serve.py`,
`ways/route.py`, `ways/clearance.py`, `ways/web.py` and `homesteads/boundary.py`) and is E3 by FR-003; the next is the thicket's
fallback (411). The next open row is the belt in the marsh (412).

  - `l7r/diagram/hamletgen/hinterland/stages.py::stage_windbreak#no copse drawn where there is no belt and no reserved seats` - its claim written (UNRESEARCHED)
  - `l7r/diagram/hamletgen/plan.py::plan_site#a farmstead grove takes 2, 3 or 4 sides the spec refusal` - its claim written (0036 drawing: two, three or four sides)
  - `l7r/diagram/settlement/structures/fixtures/siting.py::FixtureSitingMixin._route_seats#farthest seat 60 ft from the road kosatsubawayreachft 0190 2` - its claim written (GUESS 0190 drawing: the project's own figure)
  - `l7r/diagram/hamletgen/hinterland/bamboo.py::bamboo_seats#thicket fallback: THICKET_REACH_FT 220 ft, then anywhere on the page behind the back row (0075 says "just beyond the back row")` - every pass held to 0075's "just beyond the back row" (the near edge within `THICKET_ROW_DEPTH_FT`, 30 ft, of the row's back edge), the fallback walking the row's whole length; no thicket only where none fits there

- [x] T59 the three claims; the thicket's fallback held to the band just beyond the back row, with its two tests; Kashikawa and Mizuguchi regenerated (FR-004, FR-005)
      research: rendering
      verify: DONE. the three claims written; every thicket pass held just beyond the back row (its back edge, THICKET_ROW_DEPTH_FT 30 ft UNRESEARCHED), the fallback along the row's whole length, with two tests; WEB_HARD_GAP measured E3 (five modules); Kashikawa's thicket re-placed against its row, Mizuguchi's unchanged
- [x] T60 every touched claim re-checked by `impl-drift`, the occasion's review (glyph-check on Kashikawa's thicket, one map), and the close: wave 17's own bookend pair, `make done` green, the wave
      column (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. impl-drift on every touched claim (five rounds; every wave row IN-STEP at the last); the glyph checks PASS (Kashikawa's thicket; Inashiro's notice board, re-owed); make done green; wave 17's own pair (328-start at b49a6c221) band 1, variance by perf-audit's timings, consistent; the wave column written

## Phase 19 - wave 18 (amendment 17): the thicket's claims and its one size

Wave 17's re-checks found 5 rows, each tiered by its work by a fresh reader (T61a, `audit/t61a-out.jsonl`): 4 E0, 1 E2. Two of
the E0 rows (the keep-out pads' account and the pads it left out) were already fixed in wave 17 (074a12773, IN-STEP at its last
round) and carry wave 17's mark. Wave 18 takes the other two E0 claims and the E2 run's head, the shrunk stand; the next open
row is the belt in the marsh (416).

  - `l7r/diagram/hamletgen/hinterland/bamboo.py::bamboo_seats#thicket size bamboothicketft 84 x 58 ft 0075 20 guess` - the size's claim labeled GUESS on 0075's drawing page, which marks its 84 by 58 ft a GUESS
  - `l7r/diagram/hamletgen/hinterland/bamboo.py::bamboo_seats#watercourse margin of half-width  3 ft no page gives the fig` - the margin its own UNRESEARCHED claim; "within 3 ft of a watercourse" out of the 0075 claim
  - `l7r/diagram/hamletgen/hinterland/bamboo.py::bamboo_seats#off crop and water` - settled by the watercourse margin's fix, by the route this E4 row itself offers (the 3 ft claimed UNRESEARCHED) - spec-fidelity's aside, amendment 17 round 1
  - `l7r/diagram/hamletgen/hinterland/bamboo.py::bamboo_seats#shrunk stand` - the 70% passes dropped: the thicket at the page's size (GUESS on 0075), none where it fits nowhere (UNRESEARCHED)

- [x] T61a wave 17's found rows tiered by the work they take, by a fresh reader (FR-002, FR-003, SC-003)
      research: rendering
      verify: DONE. 5 rows tiered by their work by a fresh Opus reader (audit/t61a-out.jsonl): 4 E0 (two already fixed in wave 17), 1 E2
- [x] T61 the two claims; the 70% passes dropped; Kashikawa and Mizuguchi regenerated (FR-004, FR-005)
      research: rendering
      verify: DONE. the thicket size GUESS on 0075 (and drawn at full size only), the watercourse margin UNRESEARCHED, the 70% passes dropped (none where the full stand fits nowhere, UNRESEARCHED); row 807 settled by the same fix; both pool thickets unchanged
- [x] T62 every touched claim re-checked by `impl-drift`, and the close: wave 18's own bookend pair, `make done` green, the wave
      column (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. impl-drift on every touched claim (two rounds; all IN-STEP); make done green; wave 18's own pair (328-start at 8c3b5cdef) band 1, variance (perf-audit: identical call counts), consistent; the wave column written

## Phase 20 - wave 19 (amendment 18): the belt into the marsh, the wood beyond the fields

Wave 18's re-checks filed no new row. The open in-scope run is the E2 rows in ranking order: the belt in the marsh (416) and the
wood's side of the field (417). The next open row is the seat order's tie (421).

  - `l7r/diagram/hamletgen/hinterland/belt.py::past_the_lanes#no belt in the marsh` - the belt keeps its depth past a back lane into the marsh, its trees there drawn as alder (0074 drawing); the wet guard and its marsh test retired
  - `l7r/diagram/hamletgen/hinterland/parcels.py::open_ground_patches#near side of the field preferred` - seats across the field from the houses taken first (0077 drawing: the nearest slope beyond the fields), inverting feature 261's preference

- [x] T63 the belt's wet guard retired; the wood's preference inverted; the five pool hamlets regenerated (Inashiro's and Kashikawa's woods move) (FR-004, FR-005)
      research: rendering
      verify: DONE. the belt's wet guard retired (its marsh trees alder, 0074); the wood beyond the fields first (0077), inverting feature 261; the five hamlets regenerated - Inashiro's and Kashikawa's woods move, no belt moved; the brook fixture laid within reach of the first parcel
- [x] T64 every touched claim re-checked by `impl-drift`, the occasions' reviews (glyph-check on Inashiro's and Kashikawa's woodland commons), and the close: wave 19's own bookend pair, `make done` green, the wave column (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. impl-drift on every touched claim (27 IN-STEP); the glyph checks PASS (Inashiro's woodland commons, F1 filed as a found row; Kashikawa's thicket re-owed); the notice board's third round capped (passed twice, unmoved - the GM's waiver asked at the end); make done green; wave 19's own pair band 1, the parcel scan's growth timed by perf-audit (consistent); the wave column written

## Phase 21 - wave 20 (amendment 19): a real crossing, the seat's tie, each house's bath wall

Wave 19's glyph check filed one row - the wood's walk clipping a field's corner - tiered E2 by a fresh reader (T65a,
`audit/t65a-out.jsonl`: one predicate, used once). With it the open in-scope run takes the seat order's tie (422) and the bath
room's wall (423, 424); the next open row is the fixture count's cap (425).

  - `l7r/diagram/hamletgen/hinterland/parcels.py::open_ground_patches#beyond the fields by a real crossing` - only seats the walk from the houses reaches THROUGH the field (`crossed_through`, `REAL_CROSSING_SHARE` 0.5 UNRESEARCHED), on every tier, the seats higher than the fields ranked first where the ground slopes (0077 drawing: beyond the fields and higher than them); none on the houses' side
  - `l7r/diagram/hamletgen/homesteads/capacity.py::free_seats#the exhaustive seat order` - of seats about as near (one grid pitch), the one nearer the field first (0029 drawing)
  - `l7r/diagram/hamletgen/homesteads/fixtures.py::BATH_SEATS#bath room wall` - the wall rolled per house, not once per hamlet
  - `l7r/diagram/hamletgen/homesteads/fixtures.py::fixture_forms#bath room wall` - beyond the stable wing at 0.8 (0044: 17 of 21 and 12 of 15 registered baths); the roll reaches the map only where the main-door seat is free - on the pool hamlets the threshing yard covers it, so every bath draws beyond the stable (a found row, E3: the seat geometry)

- [x] T65a wave 19's found row tiered by the work it takes, by a fresh reader (FR-002, FR-003, SC-003)
      research: rendering
      verify: DONE. 1 row tiered E2 by a fresh Opus reader (audit/t65a-out.jsonl): one predicate, used once
- [x] T65 the real crossing on the level, the seat's tie, each house's bath wall rolled at the registers' share (drawn: see the found row), with their tests; the five hamlets regenerated (FR-004, FR-005)
      research: rendering
      verify: DONE. the walk through the field asked of every wood on every tier (0077: beyond the fields and higher than them), no wood on the houses' side; the seat order's tie toward the field (0029); each house's bath wall rolled at 0.8 (0044; the main-door seat that never draws filed E3); both new asks vectorized (band 3 -> 1); Kashikawa one wood, Inashiro and Mizuguchi recorded off the sheet
- [x] T66 every touched claim re-checked by `impl-drift`, the occasion's review (glyph-check on Mizuguchi's woodland commons: NEEDS-WORK, fixed and measured), and the close: wave 20's own bookend pair, `make done` green, the wave column (FR-005, FR-006, SC-002, SC-003)
      research: rendering
      verify: DONE. impl-drift on every touched claim (five rounds, all IN-STEP at the last); the woodland glyph check NEEDS-WORK fixed and verified by measurement (its two rounds spent); amendment 19 FAITHFUL (round 5); make done green; wave 20's own pair band 1 (total -10.8%), explained from perf-audit's timings and confirmed; the wave column written

## Phase 22 - wave 21 (amendment 20): the woods' two framing claims

Wave 20's re-checks filed three rows: the main-door bath (E3, its review's) and two UNCLAIMED framing decisions in
`open_ground_patches`, tiered E0 by a fresh reader (T67a, `audit/t67a-out.jsonl`). Wave 21 takes the two claims; the next open
row is the fixture count's cap (425).

  - `l7r/diagram/hamletgen/hinterland/parcels.py::open_ground_patches#scan seat window 08 of the square's box inside the predicted` - its CONVENTION claim written
  - `l7r/diagram/hamletgen/hinterland/parcels.py::open_ground_patches#woods kept out of the title pocket titlepocket keep rectangl` - its CONVENTION claim written

- [x] T67a wave 20's found rows tiered by the work they take, by a fresh reader (FR-002, FR-003, SC-003)
      research: rendering
      verify: DONE. 2 rows tiered E0 by a fresh Opus reader (audit/t67a-out.jsonl)
- [x] T67 the two claims written (FR-004)
      research: rendering
      verify: DONE. the two CONVENTION claims written in open_ground_patches (the scan's seat window, the title pocket kept clear); no executed code changed
- [x] T68 the claims re-checked by `impl-drift`, and the close: wave 21's own bookend pair, `make done` green, the wave column (FR-005, FR-006)
      research: rendering
      verify: DONE. impl-drift on both claims IN-STEP; amendment 20 FAITHFUL; make done green (already verified); wave 21's own pair band 1, variance on identical code (perf-audit consistent); the wave column written

## Phase 23 - wave 22 (amendment 21): the far-row holding's depth

Row 427 (the shrine cap) is held for the GM (exception check LEGITIMATE, recorded in its flag). Row 428 (the persimmon under the
farm's own grove) is measured a change across modules - the grove draws its conifers in `settlement/homestead_parts/groves.py`
before the persimmon is seated - and is E3 by FR-003. Wave 22 takes row 429; the next open row is the ranks' yard sun (430).

  - `l7r/diagram/hamletgen/homesteads/rows.py::seat_rows#far-row dry-field share` - the holding three lots (frame widths) deep on a street laid first, one on the dry edge (0033 drawing), the streets spaced by it

- [x] T69 the holding sized by lots; the five hamlets regenerated (Kashikawa's holdings deeper) (FR-004, FR-005)
      research: rendering
      verify: DONE. the holding one lot wide and three lots deep (0033), the streets spaced by it; Kashikawa's holdings 240 x 720 ft lot against lot, the other four hamlets unchanged
- [x] T70 the claims re-checked by `impl-drift`, the occasion's review (glyph-check on Kashikawa's farm holding), and the close: wave 22's own bookend pair, `make done` green, the wave column (FR-005, FR-006)
      research: rendering
      verify: DONE. impl-drift IN-STEP on the row; amendment 21 FAITHFUL; glyph-check farm holding PASS twice (F1 width fixed and measured); 0033's acreage and ten modals brought to the page (record checks answered); make done green; wave 22's own pair band 1, noise on nucleated rolls (perf-audit consistent, control recorded); the wave column

## Phase 24 - wave 23 (amendment 22): wave 22's found rows, claimed

Wave 22's seven found rows tiered E0 by a fresh reader (six stand; see below) (T71a, `audit/t71a-out.jsonl`); two pairs are duplicates. The well row is
withdrawn as a drift: 0196's "about 19 ft across" is the curb `well()` draws at a 9.36 ft radius; the 24.75 ft is the roof square,
which the page does not size. The street-facing claim stays E3 as tiered.
The line's share and slack (`seat_rows#farms to a street`, NEEDS-RESEARCH) is E4, not E0 (amendment 22 round 1): its claim's
first half, on the page, stays; the UNRESEARCHED line is removed until its research pass.

  - `l7r/diagram/hamletgen/homesteads/rows.py::seat_rows#farms one frame apart, never more than 240 ft` (and its duplicate, row spacing)
  - `l7r/diagram/hamletgen/homesteads/rows.py::seat_rows#the next street past the last one's holdings` (and its duplicate)
  - `l7r/diagram/hamletgen/homesteads/rows.py::seat_rows#holding set behind its frame` - UNRESEARCHED
  - `l7r/diagram/settlement/shrines_wells/wells.py::WellsMixin._well_vr#wellhead marker larger than life` - the curb the page's; the roof UNRESEARCHED

- [x] T71a wave 22's found rows tiered by the work they take, by a fresh reader (FR-002, FR-003, SC-003)
      research: rendering
- [x] T71 the claims written in `seat_rows` and `_well_vr` (FR-003 E0, FR-004)
      research: rendering
      verify: DONE. claims written in seat_rows (the row's step, the next street past the holdings, the holding's margin UNRESEARCHED, further streets parallel) and _well_vr (the curb the page's 19 ft, the roof UNRESEARCHED); the line's share and slack back to E4 (round 1)
- [x] T72 the claims re-checked by `impl-drift`; the close: wave 23's own bookend pair, `make done` green, the wave column (FR-005, FR-006)
      research: rendering
      verify: DONE. impl-drift: 9 + 5 triaged claims IN-STEP; amendment 22 FAITHFUL (round 3), plan CLEAR; make done green; wave 23's own pair band 1, identical bytecode (perf-audit consistent); the wave column

## Phase 25 - wave 24 (amendment 23): the yard's sun between ranks, the bank's nearest seat

The next open in-scope rows in ranked order (row 434, the shrine cap, held for the GM): wave 23's one found row (tiered first),
the rank step's sun, the step between ranks, and the sty's bank seat. Row 437: impl-drift found the step about 111 ft
north-south against 0038's 92 ft rows (envelope + lane room + sun added); the lane now runs inside the yard's sun, the gap the
larger of the two (plan review, amendment 23: fixed here, not left open).

  - `l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#a yard's sun between ranks` - `SUN_CORRIDOR_FT` by the step's north-south share whichever way the ranks run (0038 drawing)
  - `l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#the step between ranks` - an envelope and the larger of the lane's room and the 39 ft sun, so north-south ranks stand 0038's 92 ft apart
  - `l7r/diagram/hamletgen/pondstock.py::_bank_seats#edge midpoints first` - every bank seat ranked together nearest the houses (0025 drawing); the UNRESEARCHED clause retired
  - `l7r/diagram/hamletgen/homesteads/rows.py::draw_holdings#a holding plot that touches a lane or stream` - E0 (T73a): claimed, as `cell on a lane or stream left undrawn` - GUESS (impl-drift: leaving a cell unplanted is a decision about the place, not its drawing)

- [x] T73a wave 23's found row tiered by the work it takes, by a fresh reader (FR-002, FR-003, SC-003)
      research: rendering
- [x] T73 the rank step both ways, the bank's seats in one ranking, the found row as tiered; the five hamlets regenerated (FR-004, FR-005)
      research: rendering
      verify: DONE. the rank step owes the yard's sun either way and lays its lane inside it, so north-south ranks stand 0038's 92 ft apart; every bank seat in one ranking (0025), Kuwabata's sties 3.8 and 1.7 ft along their bank; the holding's dropped cell claimed GUESS
- [x] T74 the claims re-checked by `impl-drift`; the close: wave 24's own bookend pair, `make done` green, the wave column (FR-005, FR-006)
      research: rendering
      verify: DONE. impl-drift IN-STEP on the wave's claims; amendment 23 FAITHFUL, plan CLEAR; make done green; wave 24's own pair band 1, noise on nucleated rolls (perf-audit consistent, control recorded); the wave column

## Phase 26 - wave 25 (amendment 24): wave 24's found rows

Wave 24's nine found rows tiered by a fresh reader (T75a, `audit/t75a-out.jsonl`): eight E0, one E3 (a scattered hamlet's rank
rounds against 0031's single file - with the redeclared maps it is several places). Of the E0 rows, the dropped holding cell
closed in wave 24, and the lane's room and the rank jitter stand as claimed (the reader read both against 0246 and the code).

  - `l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#seats kept apart` - rewritten NONE, a candidate dedupe
  - `l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#the seating's reach` - rewritten to where the bound applies
  - `l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#a lane's room between ranks` - stands; the comment that called it a lane reworded
  - `l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#rank depth jitter` - stands
  - `l7r/diagram/hamletgen/pondstock.py::_bank_seats#sty seat pulled in by half the bank` - claimed on 0025's drawing page
  - `l7r/diagram/hamletgen/homesteads/rows.py::draw_holdings#holding strip cut into plots` - claimed on 0033's drawing page
  - `l7r/diagram/hamletgen/homesteads/rows.py::draw_holdings#crop cells kept back from lanes` - claimed GUESS

- [x] T75a wave 24's found rows tiered by the work they take, by a fresh reader (FR-002, FR-003, SC-003)
      research: rendering
- [x] T75 the claims written (FR-003 E0, FR-004)
      research: rendering
      verify: DONE. the seating's reach and the seats kept apart restated, the sty's bank inset (0025), the holding's plots (0033) and its lane margins (GUESS) claimed; the lane's room and the rank jitter stand; the rank comment reworded
- [x] T76 the claims re-checked by `impl-drift`; the close: wave 25's own bookend pair, `make done` green, the wave column (FR-005, FR-006)
      research: rendering
      verify: DONE. impl-drift IN-STEP on all five (the sty inset re-asked with the inset's value and units); amendment 24 FAITHFUL, plan CLEAR; make done green; wave 25's own pair band 0; the wave column

## Phase 27 - wave 26 (amendment 25): no town's corridor along a hamlet's drain

The next open in-scope row (row 434, the shrine cap, held for the GM). 0058's drawing page sets the 33 ft no-build strip along a
channel for town and city maps, which draw no marsh below their fields; on a hamlet the drain's rule is the marsh and the wet
ground below it. A nucleated cluster is exempt from the below-drain rule (0058); the rule for a dispersed hamlet's
farmsteads is not yet asked (`cluster.below_drain` has no engine caller since wave 15) and is open as row 669 (E3). The brook rows after it (bend, downhill,
dip allowance) are the next wave.

  - `l7r/diagram/hamletgen/sink.py::drain_run#no-build corridor` - the corridor no longer registered on a hamlet's drain

- [x] T77 the hamlet's drain registers no corridor; the five hamlets regenerated (FR-004, FR-005)
      research: rendering
      verify: DONE. the hamlet's drain registers no 33 ft corridor (0058: the town and city maps' rule); the five hamlets unchanged; the below-drain rule's dispersed case left open as row 669
- [x] T78 the claims re-checked by `impl-drift`; the close: wave 26's own bookend pair, `make done` green, the wave column (FR-005, FR-006)
      research: rendering
      verify: DONE. impl-drift IN-STEP on the three drain claims; amendment 25 FAITHFUL (round 2), plan CLEAR; make done green; wave 26's own pair band 0; the wave column

## Phase 28 - wave 27 (amendment 26): the brook never climbs; both flanks as the page judges them

The next open in-scope rows: the brook trio (448-450) and row 451. A first trial of the brook rows also broke out of the bend
loop and turned the bend, and failed 6 of 28 brook tests; the session re-tiered them E3 on it, and amendment 26 round 1
showed the literal fix alone passes all 28 - the re-tier is withdrawn and the three are done here.

  - `l7r/diagram/hamletgen/water/brook.py::bend_runs#bend across the fall` - a run across the fall takes no dip down it (cap 0), so no next leg climbs
  - `l7r/diagram/hamletgen/water/brook.py::brook_violations#runs downhill` - the downhill check strict (0054: strictly under 90)
  - `l7r/diagram/hamletgen/water/brook_rules.py::BEND_DIP_FT#bend dip allowance` - retired
  - `l7r/diagram/hamletgen/water/fit.py::flanks_commanded#both flanks commanded` - a flank of 150 ft or less not judged; a judged flank owed 80 ft or 30%, the lesser (0053 drawing)

- [x] T79 the brook never climbs below its tap (no dip, the strict check, the allowance retired); the flank rule as 0053 states it, its tests to the page (FR-004, FR-005)
      research: rendering
      verify: DONE. the brook below its tap never climbs - no dip down the fall, the strict check, BEND_DIP_FT retired (0054); flanks_commanded as 0053 states it; test_brook 28 and test_fit_flanks 7 passed; the five hamlets regenerated unchanged
- [x] T80 the claims re-checked by `impl-drift`; the close: wave 27's own bookend pair, `make done` green, the wave column (FR-005, FR-006)
      research: rendering
      verify: DONE. impl-drift IN-STEP (1 + 11); amendment 26 FAITHFUL (round 2), plan CLEAR; make done green; wave 27's own pair band 1, host load on unchanged maps (perf-audit consistent, each over-5% seed diagnosed by counterfactual); the wave column

## Phase 29 - wave 28 (amendment 27): the polder's outer face with the water

The next open in-scope row, 452. Its suggested fix (no edge wander, from 0019's "fixed outer edge") was tried: Kuwabata's
perimeter dike came out a straight-sided rectangle (each side within 5-12 ft of a line, main's 55-58), and its glyph check found
it NEEDS-WORK (F1, wrong form) - 0027's drawing page curves the dike's outer face with the water's edge and rules a rectangular
polder modern, under the GM's 2026-09-28 ruling to "eliminate anything which is only modern". 0019 and 0022 mean the interior
drift leaves the edge alone, not that it is straight. The change is reverted; the code already matches 0027, and only its claim
was wrong (it cited 0019 for a 0.86 box-fill walk-down no page states, and a comment called the block a surveyed rectangle): E0,
the claim restated. The trial's knot form is reverted with it and its gap filed as a found row.

  - `l7r/diagram/hamletgen/water/polder.py::_polder_candidate#surveyed block` - restated: the outer face with the water (0027); the 0.86 walk-down a CONVENTION

- [x] T81 the polder's outer edge tried (Kuwabata re-rolled), judged by its glyph check, reverted; the claim restated against 0027 (FR-003, FR-004, FR-005)
      research: rendering
      verify: DONE. no edge wander tried: Kuwabata's dike a straight-sided rectangle, glyph check NEEDS-WORK (F1, 0027 and the GM's no-modern ruling); reverted with the knot form it needed (gap filed); the code matches 0027, its claim restated, the walk-down labeled GUESS, a comment corrected
- [x] T82 the close: the claim re-checked by `impl-drift`; no executed code changed since wave 27's close; `make done` green; the wave column (FR-005, FR-006)
      research: rendering
      verify: DONE. impl-drift IN-STEP on the restated claims; amendment 27 FAITHFUL (round 5), plan CLEAR; no executed code changed since wave 27's close; make done green; the wave column

## Phase 30 - wave 29 (amendment 28): wave 28's found rows

Wave 28's six found rows tiered by a fresh reader (T83a, `audit/t83a-out.jsonl`): five E0 (one a duplicate, one closed in wave 28),
one E2 (the knot gap in `next_gather`, left for its place in the run).

  - `l7r/diagram/hamletgen/water/polder.py::_polder_candidate#block centered` - CONVENTION, a framing; turned to the fall, not at any bearing
  - `l7r/diagram/hamletgen/water/polder.py::_polder_candidate#block's rows run along the fall` (and its duplicate) - claimed on 0019's drawing page
  - `l7r/diagram/hamletgen/water/polder.py::_polder_candidate#cleanparcelsfalse` - claimed on 0055's drawing page: the drawn block is cleaned, the flag defers it for speed

- [x] T83a wave 28's found rows tiered by the work they take, by a fresh reader (FR-002, FR-003, SC-003)
      research: rendering
- [x] T83 the claims written (FR-003 E0, FR-004)
      research: rendering
      verify: DONE. the polder block's framing (CONVENTION), its turn to the fall (0019) and its deferred parcel cleanup (0055) claimed
- [x] T84 the claims re-checked by `impl-drift`; the close: `make done` green, the wave column (FR-005, FR-006)
      research: rendering
      verify: DONE. impl-drift IN-STEP on all three; amendment 28 FAITHFUL, plan CLEAR; make done green; no executed code changed; the wave column

## Phase 31 - wave 30 (amendment 29): the polder's reservoir - tried, reverted, research first

The next open in-scope E2 row (row 434 held for the GM). Its suggested fix sized the polder's header reservoir by the paddy it
waters, two or three tenths of it (0061, the Song-dynasty manual), in place of a fixed 82 x 54 ft ellipse. Tried: Kuwabata's
reservoir came to about 4.25 acres against its 21.2-acre block (which is all fish ponds, no paddy). impl-drift then found the
share inapplicable: 0061 gives it only for a field on high ground whose pond is its fields' only water, and a polder is low
ground diked out of standing water, its reservoir the wild water the inlet sluice draws from - no page sizes it. Reverted; the
fixed ellipse is claimed UNRESEARCHED with what was searched, and the row is E4, research first.

  - `l7r/diagram/hamletgen/water/polder.py::stage_polder#reservoir size` - claimed UNRESEARCHED; the row re-tiered E4

- [x] T85 the reservoir share tried (Kuwabata re-rolled) and reverted; the fixed size claimed UNRESEARCHED; row 458 E4 (FR-003, FR-004)
      research: rendering
      verify: DONE. the share tried (Kuwabata's reservoir 4.25 acres) and reverted - 0061's share is a high-ground pond's, not a polder's wild-water source; the fixed size claimed UNRESEARCHED; row 458 E4, open
- [x] T86 the claim re-checked by `impl-drift`; no executed code changed since wave 29's close; `make done` green (FR-005, FR-006)
      research: rendering
      verify: DONE. impl-drift IN-STEP on the relabeled claim; amendment 29 FAITHFUL (round 3), plan CLEAR; make done green; no executed code or map differs from wave 29's close

## Phase 32 - wave 31 (amendment 30): one network only where treads meet

The next open in-scope E2 rows. Row 459 (`a_way_onto_the_bund#on the bund`) tried literally - an end within `BUND_REACH_FT`
of the paddy with no water between carried on to the bund - and measured: Mizuguchi's field spur, laid after the pass, then
started 22 ft off the street's end (measured 2026-10-08, the pool test's knot report) and `test_no_lane_ends_knot_short_of_a_join[mizuguchi]` failed; keeping a junction end in
place did not cure it. The fix spans the bund pass and the spur's laying: E3 by FR-003, the trial reverted. Then row 460.

  - `l7r/diagram/hamletgen/ways/checks.py::lanes_share_tread#one network at 25 ft` - two lanes one network only where their treads meet (within the ink tolerance); ends within 25 ft are the knot pass's to join at one point (0081)

- [x] T87 row 459 tried, measured and re-tiered E3; the network join to the treads' meeting, its test to the page (FR-003, FR-004, FR-005)
      research: rendering
      verify: DONE. row 459 tried, measured (Mizuguchi's spur 22 ft off the street, the knot test failed) and re-tiered E3, reproduced by the review; two lanes one network only where their treads meet (0246; 0081's 25 ft is the knot pass's), its test to the page; the five hamlets unchanged
- [x] T88 the claims re-checked by `impl-drift`; the close: wave 31's own bookend pair, `make done` green, the wave column (FR-005, FR-006)
      research: rendering
      verify: DONE. impl-drift IN-STEP (the claim relabeled to 0246); amendment 30 FAITHFUL, plan CLEAR; make done green; wave 31's own pair band 0 on a retake (the first band 3 under another session's load, every stage grown); the wave column

## Phase 33 - wave 32 (amendment 31): wave 30's found rows

Wave 30's five found rows tiered by a fresh reader (T89a, `audit/t89a-out.jsonl`): two E0 - the code already matches a
drawing page - one E0 withdrawn to E3 by impl-drift (the pond layout), and two E2 (the reservoir's first seat and the inlet stub run outside the dike, against 0019's "no channel runs
outside the dike"; one change in `polder.py`, left for its place in the run).

  - `l7r/diagram/hamletgen/water/polder.py::stage_polder#dike-pond conversion` - cited to 0020's drawing page (the leftover roll, 1.0 or 0.9)
  - `l7r/diagram/hamletgen/water/polder.py::stage_polder#dike-pond mosaic bend strength` - claimed on 0019's drawing page; impl-drift found it DRIFTED (the chessboard layout is attested and never rolled): re-tiered E3, open
  - `l7r/diagram/hamletgen/water/polder.py::stage_polder#polder fabric per archetype` - claimed on 0022's drawing page

- [x] T89a wave 30's found rows tiered by the work they take, by a fresh reader (FR-002, FR-003, SC-003)
      research: rendering
- [x] T89 the claims written (FR-003 E0, FR-004)
      research: rendering
      verify: DONE. the dike-pond conversion (0020 drawing) and the polder fabric (0022 drawing) claimed; the pond layout's claim found DRIFTED, re-tiered E3, open
- [x] T90 the claims re-checked by `impl-drift`; the close: `make done` green, the wave column (FR-005, FR-006)
      research: rendering
      verify: DONE. impl-drift IN-STEP on two, DRIFTED on the pond layout (E3); amendment 31 rounds recorded, plan CLEAR; make done green; no executed code changed; the wave column

## Phase 34 - wave 33 (amendment 32): a path goes round its own beds and sheds

The next open in-scope E2 row (row 434 held for the GM; the polder rows re-tiered in wave 32 sit later in the run). 0246's
drawing page: a way leaves round its own beds and fixtures. `_homestead_polys` exempted a farm's own garden and sheds from its
own path's fabric along with its dooryard; now only the dooryard (and the grove band, which the path leaves through) is its own.

  - `l7r/diagram/hamletgen/ways/fabric.py::_homestead_polys#a path leaves its own yard` - the owner's beds, sheds, byres and retirement house obstacles to its own path

- [x] T91 the path's own beds and sheds obstacles; the five hamlets regenerated (unchanged); the owner test (FR-004, FR-005)
      research: rendering
      verify: DONE. the path's own beds, sheds, byres and retirement house obstacles to it, only its dooryard and grove band its own (0246); the five hamlets unchanged; the owner test
- [x] T92 the claims re-checked by `impl-drift`; the close: wave 33's own bookend pair, `make done` green, the wave column (FR-005, FR-006)
      research: rendering
      verify: DONE. impl-drift IN-STEP on all four; amendment 32 FAITHFUL, plan CLEAR; make done green after the 329 merge; wave 33's own pair band 1 on a quiet host (two band-3 pairs under another session's load diagnosed by an interleaved control, perf-audit consistent); the wave column

## Phase 35 - wave 34 (amendment 33): a jog across ways of two widths pulled straight

The next open in-scope E2 rows. The polder's reservoir seat and inlet stub (one change, 0019's "no channel runs outside the
dike") tried literally - the walk from the inlet until the rim clears the dike's outer face: the inlet outside the dike fell
from 63.8 to 14.7 ft (`m:wave34-kuwabata-inlet-outside-dike`), but Kuwabata re-rolled with lanes 7 and 13 zigzagging across
their joint (a 39 ft turn-back, past the joints pass's 12 ft hook rule) and the pool test refused it: E3 (the seat and the
joints pass), reverted. Row 464 (the track's inner end joined however far) and row 465 (the spine's 5 ft rank) are re-tiered
E3 with their evidence in `audit/overrides.json` (amendment 33 round 1): `_pull_back_to_service` is handed no hard ground,
walls or water, so a routed join changes its caller in `web.py` and calls `route._route`; the code names no spine
(`rank_width` ranks by connector, spur and role). Row 466 is taken.

  - `l7r/diagram/hamletgen/ways/joints.py::_one_joint#ways of two kinds stay two` - a joint of two kinds string-pulled like any other (0081), then split back into its two records (`split_at`, `_split_committed`), each keeping its width

- [ ] T93 the reservoir seat tried, measured and re-tiered E3; rows 464 and 465 re-tiered E3 with their evidence; the two-width joint pulled straight and split back, its tests (FR-003, FR-004, FR-005)
      research: rendering
- [ ] T94 the claims re-checked by `impl-drift`; the close: wave 34's own bookend pair, `make done` green, the wave column (FR-005, FR-006)
      research: rendering
