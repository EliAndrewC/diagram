# Feature 328 wave 1: findings the claims gate counts as introduced

Load this file when: the push of feature 328's wave 1 is refused by `claims-gate.sh`, or a later wave picks up these rows.

Wave 1 corrected claim lines only (tier E0). Re-checking the units it touched made `impl-drift` read decisions nobody
had checked before - new claim lines, and units whose reason strings or claims changed - and it found these mismatches.
None is a change wave 1 made to what the code does: each is the implementation as it stood, now measured. The gate
calls them introduced (the base index held the unit IN-STEP or had no row). Each is a row of `ranking.json` with
`found: wave 1 re-check` (from `audit/found-wave1.jsonl`), tiered by its implementation work, so a later wave fixes it
in easiest-first order. They land with CLAIMS_OK naming this file, as feature 318's did.

- `buildings/programs.md::Magistrate's manor (county magistracy)#manor kitchen garden by the sun` (DRIFTED, E3): every
  residence keeps a garden, its site and size rolled knobs (0109 drawing); the procedure makes it optional.
- `buildings/programs.md::...#posting wealth knob` (DRIFTED, E1): the poor end's look is a GUESS on 0091's drawing page;
  the procedure calls it historically genuine.
- `buildings/programs.md::...#rear service strip` (DRIFTED, E3): where servants lodge is a two-form knob (gate range,
  rear hut; 0091); the procedure fixes the rear.
- `buildings/programs.md::...#staff housing knob` (DRIFTED, E2): option (c), retainers in town, is attested only at an
  urban magistracy (0114); restrict it to urban tiers.
- `l7r/diagram/overlap/taxonomy.py::_OVERLAP_EXEMPT#mill beside its stream` (DRIFTED, E1): the wheel sits in a mill
  race led off the stream (0064), not in the drain or stream.
- `l7r/diagram/overlap/taxonomy.py::_OVERLAP_EXEMPT#yard, garden and fixtures against the house` (DRIFTED, E2): the wood
  shed stands about 6 ft off a wall (0043), not against the house.
- `l7r/diagram/settlement/city/canals.py::CanalsMixin.farmland_ring#sluice standoff` (CANNOT-TELL, E1): the sluice is
  30 px from the tap point, perhaps about 57 ft beyond the rim where 0146 says about 90 ft; measure and set it.

The other findings the wave's re-checks surfaced in the same units were findings already (the gate lists them as
pre-existing), or were fixed within the wave (three rounds of claim corrections), or are recorded in `ranking.json` as
moved rows (`audit/overrides.json`: the rank step, the merchant kura size, the universal shrine) or found rows.

## Wave 2 (2026-10-07)

Wave 2 changed fifteen values and procedure sentences, and its re-checks read every claim of the sections and units those
touched - 271 claims, then 102 more after two corrections. The gate counts the findings below as introduced: each is the
implementation as it stood, measured for the first time (a procedure section's every claim is re-judged when one of its
sentences changes, and a unit's when a constant it reads moves). None is a change wave 2 made to what a map draws. Each is
a found row in `ranking.json` (`audit/found-wave2b.jsonl`), tiered provisionally by its verdict (a claim fix E0, a drift
E2, a question for the record E4) until the wave that takes it re-tiers it.

- `buildings.md::Fire-water tubs#a tub never on a well glyph; moved to another eaves corner` (UNCLAIMED, E0): a tub never on a well glyph; moved to another eaves corner
- `buildings.md::Fire-water tubs#tub against its wall` (MISLABELED, E0): the page does answer that tubs stand at the building ("kept at the wooden buildings, at the entrance"), so cite 0100 drawing §3 for that; only the gutter feed and the ~3.5 ft limit are UNRESEARCHED
- `buildings.md::Fire-water tubs#tub clear of the footprint` (MISLABELED, E0): the procedure gives this as the GM's rule of 2026-07-25/26, so it should be CANON naming that ruling; also "~2 ft clear" disagrees with "2.2 px", which is ~0.7 ft at 3 px = 1 ft
- `buildings.md::Outer court (administrative / public)#cell` (DRIFTED, E2): the 12 x 10 ft size is in step (small end of 6-18 mats, size not recorded), but the procedure's "1-2 occupants" contradicts the measured cells "each shared by several prisoners"
- `buildings.md::Outer court (administrative / public)#cell kept well under the barracks` (UNCLAIMED, E0): cell kept well under the barracks
- `buildings.md::Outer court (administrative / public)#granary kept under a residence block` (UNCLAIMED, E0): granary kept under a residence block
- `buildings.md::Outer court (administrative / public)#practice ground area` (MISLABELED, E0): the drawing page records 90-135 sq ft per samurai as a guess, so this should be GUESS 0165 drawing
- `buildings.md::Outer court (administrative / public)#practice ground placement` (MISLABELED, E0): answered by "draws a practice ground beside its guards' quarters", so cite 0165 drawing
- `buildings.md::Outer court (administrative / public)#practice ground shared with cart staging or muster` (UNCLAIMED, E0): practice ground shared with cart staging or muster
- `buildings.md::Outer court (administrative / public)#practice ground weapon rack` (MISLABELED, E0): the drawing page records the ~8 x 2 ft rack as a guess, so this should be GUESS 0165 drawing
- `buildings.md::Outer court (administrative / public)#stable below barracks` (MISLABELED, E0): the findings page calls the stable-below-barracks order a GUESS ("none says where a stable ranked"), so this should be GUESS 0116 drawing
- `buildings.md::Outer court (administrative / public)#stables` (DRIFTED, E3, tiered by its work at T25a): the stable becomes 0108's small warrior stable: three bays long of one-ken stalls, with the kusa-no-ma passage before the stalls and the tozamurai room, the procedure's ~84-96 px re-derived, the three magistracy sheets' stables redrawn, and the 2-4 horse count labeled GUESS
- `buildings.md::Outer court (administrative / public)#tax archive drawn with white-plaster fill, heavy stroke and dark door mark` (UNCLAIMED, E0): tax archive drawn with white-plaster fill, heavy stroke and dark door mark
- `buildings.md::Sacred features#a fence round the sanctuary alone as a wealth knob (0223 §171-172 finds such fences before 1868 only where the shogunate or a lord built them)` (UNCLAIMED, E0): a fence round the sanctuary alone as a wealth knob (0223 §171-172 finds such fences before 1868 only where the shogunate or a lord built them)
- `buildings.md::Sacred features#grove inside a compound wall` (MISLABELED, E3, tiered by its work at T25a): draw the compound shrine beside a single tree (0218 drawing), not a stippled grove rectangle, and redraw the three magistracy sheets
- `buildings.md::Sacred features#sanctuary` (DRIFTED, E3, tiered by its work at T25a): the sanctuary's width becomes a rolled knob, 1 ken (~6 ft) or 3 ken (~18 ft) per 0222, the covering house left undrawn as 0222 records, with the procedure, type band and shrine sheets following
- `buildings.md::Sacred features#the whole sacred complex held to at most ~2/3 of the residence` (UNCLAIMED, E0): the whole sacred complex held to at most ~2/3 of the residence
- `buildings.md::Scale#well location marker` (DRIFTED, E3, tiered by its work at T25a): draw Mode A wells at 0196's curb, about 4 ft square (12 px at 3 px/ft) on its about 4 ft-wider apron, true size, in place of the 22 px marker, and redraw every pool sheet's wells
- `buildings/programs.md::Country shrine (a village district's shrine)#a well as the purification stop beside the approach ("the well or basin"; the required item is `well`)` (UNCLAIMED, E0): a well as the purification stop beside the approach ("the well or basin"; the required item is `well`)
- `buildings/programs.md::Country shrine (a village district's shrine)#approach width about 10 ft` (UNCLAIMED, E0): approach width about 10 ft
- `buildings/programs.md::Country shrine (a village district's shrine)#bell tower band 6-16 by 6-16 ft` (UNCLAIMED, E0): bell tower band 6-16 by 6-16 ft
- `buildings/programs.md::Country shrine (a village district's shrine)#building size anchors` (DRIFTED, E2, tiered by its work at T25a): widen the country shrine's size bands to the record: a sanctuary of 1 or 3 ken (Hie's 2-bay about 12 x 6 ft) and worship halls from about 18 ft (Hie about 18 x 12, Rokusha 9 tsubo), in the band, its table and the sheet sizing rule
- `buildings/programs.md::Country shrine (a village district's shrine)#dwelling privy` (MISLABELED, E0): 0222's drawing page records the privy at the dwelling as "a GUESS ... no page we read names them at a village shrine"; should be GUESS research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html
- `buildings/programs.md::Country shrine (a village district's shrine)#kitchen garden by the sun` (MISLABELED, E0): 0109's drawing page records the keeper's plot "place and its size are a GUESS", and the six-hour rule rests on a GUESS reading; should be GUESS citing the two drawing pages
- `buildings/programs.md::Country shrine (a village district's shrine)#sacred tree drawn as the biggest crown in the precinct` (UNCLAIMED, E0): sacred tree drawn as the biggest crown in the precinct
- `buildings/programs.md::Magistrate's manor (county magistracy)#a detached guest house at a rich posting (0091's drawing page records it as a GUESS)` (UNCLAIMED, E0): a detached guest house at a rich posting (0091's drawing page records it as a GUESS)
- `buildings/programs.md::Magistrate's manor (county magistracy)#formal visitors and the privacy baffle` (MISLABELED, E0): 0104 answers this: "the genkan is drawn on the office. The way to the residence runs on through the office"; it should cite 0104's drawing page, and "go no deeper" is the project's reading beyond that
- `buildings/programs.md::Magistrate's manor (county magistracy)#granary weight knob` (DRIFTED, E2): the program puts a granary row inside a remote county's compound; 0098 calls the terminal row a GUESS from a whole-province office ("is this project's GUESS") and gives no count, and its drawing page gives a county office "a single storehouse", with the row at the river landing for a county on navigable water and an isolated county leaning to the office's single store
- `buildings/programs.md::Magistrate's manor (county magistracy)#upland granary strongbox role` (MISLABELED, E0): 0098 bears on this: "The tax on dry fields was often paid in cash", with the money share delivered to the office; it should cite 0098, and note the tension with the deviation that the dry-field share arrives in kind
- `buildings/programs.md::Magistrate's manor (county magistracy)#wells by use` (MISLABELED, E0): 0091 places wells "at the front, at the side or indoors", not by a kitchen; the kitchen well is 0105's drawing-page reading ("that the one well also filled the bath is our reading"), so the label should be GUESS on 0105's drawing page
- `l7r/diagram/hamletgen/cluster.py::seat_cluster#belt room on the canvas` (CANNOT-TELL, E4): 0072 says a belt that runs off the frame is sound, and one exhibit has about 28% of its outline off the page (747 ft outline, 537 ft framed). Whether BELT_ROOM_MAX_OFF 0.2 would refuse that depends on what belt_off_canvas measures, which the bundle does not show
- `l7r/diagram/hamletgen/cluster.py::seat_cluster#not in the reed fringe` (MISLABELED, E0): the account "0058 has no fringe rule" is false: 0058 says "A pond's reed fringe does not count as marsh ... this project does not extend the rule to it". The claim should say the GM ruling of 2026-08-28 overrides 0058 §99 (or be a DEVIATION once 0058 records that ruling)
- `l7r/diagram/hamletgen/cluster.py::seat_cluster#the seat center set dep + 12 ft out from the field margin` (UNCLAIMED, E0): the seat center set dep + 12 ft out from the field margin
- `l7r/diagram/hamletgen/hinterland/parcels.py::open_ground_patches#a ring with room for fewer than 5 crowns is refused as a wood` (UNCLAIMED, E0): a ring with room for fewer than 5 crowns is refused as a wood
- `l7r/diagram/hamletgen/hinterland/parcels.py::open_ground_patches#commons legibility floor: a ring under 120 ft is dropped rather than drawn smaller (fewer, never smaller)` (UNCLAIMED, E0): commons legibility floor: a ring under 120 ft is dropped rather than drawn smaller (fewer, never smaller)
- `l7r/diagram/hamletgen/hinterland/parcels.py::open_ground_patches#line follows its bounds` (CANNOT-TELL, E4): the bundle does not give LOT_BOUND_REACH's value, so I cannot check it against the page's "Within about 45 ft"; the edge following its bounds matches the page's rule, which the page itself calls a GUESS
- `l7r/diagram/hamletgen/homesteads/capacity.py::free_seats#the exhaustive seat order` (CANNOT-TELL, E2, tiered by its work at T25a): break the tie among seats about as near the seat by nearer the fields (0029 drawing), not by coordinates: free_seats' sort key becomes (distance band, distance to the field outline)
- `l7r/diagram/hamletgen/homesteads/farm_water.py::farm_channel#how far a channel's source is sought: 20 ft steps, 60 ft spread, widened fourfold` (UNCLAIMED, E0): how far a channel's source is sought: 20 ft steps, 60 ft spread, widened fourfold
- `l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#a footpath's room off the outline` (MISLABELED, E0): `WEB_FABRIC_GAP * 2.0 + 6.0` (20 ft) is the lane's room 0246 records as a convention ("7 ft at each garden fence and a 4 ft tread ... 20 ft in all"); the label should cite 0246 drawing as CONVENTION, and the code's 6 ft of tread does not match the page's 4 ft tread plus 2 ft parting
- `l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#a yard's sun between ranks` (DRIFTED, E2, tiered by its work at T25a): _rank_step adds s.px(SUN_CORRIDOR_FT) whichever way the ranks run, abs(oy) in place of max(0, -oy), so no rank stands within 39 ft south of another rank's yards (0038 drawing)
- `l7r/diagram/hamletgen/homesteads/wells.py::place_wells#grove farms take their own water and are left out of the communal wells` (UNCLAIMED, E0): grove farms take their own water and are left out of the communal wells
- `l7r/diagram/hamletgen/homesteads/wells.py::place_wells#no well seated over a household's reserved wood-floor seats` (UNCLAIMED, E0): no well seated over a household's reserved wood-floor seats
- `l7r/diagram/hamletgen/ways/serve.py::_lay_web_lane#no way drawn twice` (MISLABELED, E0): refusing a lane that runs beside another (over 60% of the run, or over 100 ft unbroken) decides where lanes exist on the ground, not how they are shown; the label should be GUESS or UNRESEARCHED
- `l7r/diagram/hamletgen/ways/serve.py::_lay_web_lane#not along a shelter belt` (NEEDS-RESEARCH, E0, tiered by its work at T25a): split the claim: a lane kept through a shelter belt cited to 0072 drawing, and the 60 ft a lane may run inside one claimed UNRESEARCHED
- `l7r/diagram/hamletgen/ways/serve.py::shadowed_by#no way drawn twice` (MISLABELED, E0): refusing a way that runs within 30 ft of another for more than 100 ft is a rule about where lanes run, not a drawing convention; should be GUESS or UNRESEARCHED
- `l7r/diagram/hamletgen/ways/street.py::row_reach#street run past its end farms` (CANNOT-TELL, E0, tiered by its work at T25a): reword the claim: half a frame past the end farms at both ends of the span, UNRESEARCHED, the run off the map being street_run_out's road (0033 drawing)
- `l7r/diagram/hamletgen/ways/web.py::_lay_skeleton#clear of crop, wet and water` (MISLABELED, E0): the 0081 and 0246 drawing pages answer the rule of keeping off crop and wet ground ("never crosses row crops", "keeps off wet ground"), so the claim should cite them with the 20 ft as a GUESS or CONVENTION; note §59 also lets a lane "touch a plot's boundary"
- `l7r/diagram/hamletgen/ways/web.py::stage_web#a web lane's span` (MISLABELED, E0): 0246 says a back lane "runs only along the houses it serves" (served = within 100 ft, §10), so the rule is answered; the claim should cite 0246 and reconcile the 1.5 x WEB_REACH_FT (150 ft) span with the 100 ft service reach
- `l7r/diagram/hamletgen/ways/web.py::stage_web#door path reach` (MISLABELED, E0): the 12 ft steading arrival is recorded on the 0246 drawing page as part of its GUESS ("within 12 ft of the steading's built ground"), so the claim should name that page (GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html); the 40 ft is not recorded there
- `l7r/diagram/hamletgen/ways/web.py::stage_web#web lanes off the hard ground` (MISLABELED, E0): 0246 ("a stretch that would cross the field, a crop, wet ground ... is cut out") and 0081 drawing answer the rule, so the claim should cite them with the 8 ft margin as a GUESS or CONVENTION
- `l7r/diagram/hamletgen/cluster.py::seat_cluster#band on the canvas` (CANNOT-TELL, E4): code keeps seat_c at least lat*0.5 from the frame; the band samples at t=±0.9*lat, which suggests lat is the half-length, so this would be a quarter of the length, not "half the band's length"; need band_extent's meaning of lat
- `l7r/diagram/hamletgen/cluster.py::seat_cluster#brook across the band` (DRIFTED, E2): 0035 makes the uncrossed site a tie-breaker ("otherwise equally good") and builds on both banks where the best wind-facing site is crossed; score -= 3.0*crossed outweighs the whole wind term (1.0) and the upslope term (0.8), so a crossed best site always loses; the penalty should only break near-ties

## Wave 4 (2026-10-07)

Wave 4 brought the lane law to 0081 and 0246: the 7 ft margin off a garden fence on lanes, tracks and bridges, the
25 ft join reach everywhere, lane ends within 25 ft gathered at one point (at seating and in a settle step), every lane
at its rank's width, and the four rows ranked ahead of it. Its re-checks closed 34 ranked rows and found 8 more already
in step; the five whose keys moved are recorded in `audit/waves.json`. The gate counts the findings below as introduced:
each is a found row in `ranking.json` (`audit/found-wave4.jsonl`), the work a later wave takes, or a value held where
the research-correct value made a map refuse (spec Edge Case: held at the old value, waiting on the found row that
lets it move).

- `l7r/diagram/hamletgen/ways/web.py::stage_web#a footpath reaches every farmhouse 7 ft off a plot` (DRIFTED, E3): footpaths thread to every farmhouse while keeping 0246's 7 ft off a garden fence: at 7 ft Kashikawa's settled web left two farmhouses off the network (WebRefused at (3024, 3004) and (3265, 2589)) - re-route or re-seat so the gap holds
- `l7r/diagram/hamletgen/ways/checks.py::lanes_share_tread#one network at 25 ft` (DRIFTED, E2): two lanes count as one network only where their treads meet (0081), the 25 ft join reach applying to ends that are then joined at one point - not any vertex within 25 ft of another run
- `l7r/diagram/hamletgen/ways/street.py::join_to#joining leg's berth` (MISLABELED, E1): the joining leg's berth at 0246's 7 ft off a garden fence (it reads FOOTPATH_FABRIC_GAP, held at 4 ft); the claim cites 0246
- `l7r/diagram/settlement/rolling/gap_ways.py::_way_for#knotted fallback: a foot is left within 25 ft beside a junction when no gathered or knot-f` (UNCLAIMED, E0): claim it: knotted fallback: a foot is left within 25 ft beside a junction when no gathered or knot-free join is admitted, contrary to 0081 §21 "three lanes never arrive a few feet apart in a knot"; the page does not record this as a DEVIATION
- `l7r/diagram/hamletgen/ways/smooth.py::_smooth_web#a hairpin arm under 40 ft is kept when its tip is the lane's only contact with another way` (UNCLAIMED, E0): claim it: a hairpin arm under 40 ft is kept when its tip is the lane's only contact with another way; this exception is not in 0081 §19
- `l7r/diagram/hamletgen/ways/smooth.py::_smooth_web#the knot's node is placed on a through lane's tread (4 ft touch), else at the ends' centro` (UNCLAIMED, E0): claim it: the knot's node is placed on a through lane's tread (4 ft touch), else at the ends' centroid
- `l7r/diagram/hamletgen/ways/smooth.py::_smooth_web#the string-pull chord's lane keep-out is max(4 ft, w/2 + 2 ft), with a default width of 5 ` (UNCLAIMED, E0): claim it: the string-pull chord's lane keep-out is max(4 ft, w/2 + 2 ft), with a default width of 5 ft
- `l7r/diagram/settlement/rolling/gap_ways.py::knot_free_foot#a foot slides along the tree at most 2 x the knot reach (50 ft)` (UNCLAIMED, E0): claim it: a foot slides along the tree at most 2 x the knot reach (50 ft)
- `l7r/diagram/hamletgen/ways/knots.py::settle_knots#a lane with no width is judged at 3 ft in the lawfulness check` (UNCLAIMED, E0): claim it: a lane with no width is judged at 3 ft in the lawfulness check
- `l7r/diagram/hamletgen/ways/knots.py::settle_knots#a knot no lawful gather reaches` (DRIFTED, E3): gather the knots left on Inashiro (lanes 9/11 at 19.1 ft; lane 3 24.1 ft from the track head) and Sawada (lanes 9/12, 21.9 ft) at one point (0081): every single-point gather today runs a way along another, through a yard, or off the network - re-lay the earlier household's way at seating so a lawful gather exists; then drop the map from test_pool_261's _KNOTS_WAITING
- `l7r/diagram/hamletgen/ways/joints.py::RANK_WIDTHS#the spine at 5 ft` (DRIFTED, E2): give the cluster's spine 0081's 5 ft rank (the table has footpath, field spur and track out only): the route joining the track out to the field spur is one through-route (0081) and should take the spine's width, not run as 3 ft household ways
- `l7r/diagram/hamletgen/ways/law.py::fronting_ends#an end discharged by a house` (DRIFTED, E2): count a lane end as reaching a farmhouse within 60 ft of the house or 12 ft of its steading's built ground (0246.drawing), not within 80 ft of the house's center (DOORSTEP_FT); fronting_ends and lane_ends_front_different_houses both read it
- `l7r/diagram/hamletgen/ways/smooth.py::_smooth_web#a hairpin arm kept as the only contact` (DRIFTED, E2): 0081 cuts a returning leg under 40 ft with one recorded exception (the folded field spur); the smoother also keeps an arm whose tip is the lane's only contact. Join the lane elsewhere so the arm can be cut, or, where the record supports keeping it, record the exception on 0081's drawing page (a record edit)

## Wave 5 (2026-10-07)

Wave 5 took the next run of E1: a row village's street run on off the map at both ends (0033), captions leaderless out to
twice the usual gap (0242), the funerary caption group, the tier glossary, the execution ground and boundary stone, the
honmaru at about 2 ha, the martial hall's long hall, the ministries by tier, the town and city walls' figures in feet,
the plank 4 ft, the sluice 90 ft past the moat's rim, the moat's river ends square and the water gate's 60 ft opening.
Two rows moved: the mill (a mill race is a new element, E3) and the moat's width (0146 and 0151 disagree, E4). The gate
counts the findings below as introduced: each is the implementation as it stood, read for the first time because a unit
or section around it changed. Each is a found row in `ranking.json` (`audit/found-wave5.jsonl`), tiered provisionally by
its verdict (a claim fix E0, a drift E2, a question for the record E4) until the wave that takes it re-tiers it.

- `l7r/diagram/hamletgen/ways/track.py::_thread_the_fabric#the track's route walled by the field, crop, toe band and wet ground, and kept off drawn water` (UNCLAIMED, E0): claim it: the track's route walled by the field, crop, toe band and wet ground, and kept off drawn water
- `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.castle#ground reserved` (MISLABELED, E0): the max(36 x bscale, 26) px margin outside the moat is a physical rule for how close buildings stand to the castle works, not plumbing; it should be UNRESEARCHED
- `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.castle#inner moat` (MISLABELED, E0): the findings answer the inner moat's width: Hiroshima's "inner moat 30 to 104 m" (~98-341 ft), while the code draws mw*0.5 = 40 ft, below that range; the width should cite 0139.html §51 and be widened, and only the 0.42 x gap offset stays UNRESEARCHED
- `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.ministry#office apron` (DRIFTED, E2, tiered by its work at T25a): reserve the office's 42 ft edge clearance (0163 drawing) in real feet in place of max(30 x bscale, 26) px, re-deriving the 26 px floor kept for the office-abut clearance against the center-tested urban packs
- `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.wall#buildings kept off the rampart` (MISLABELED, E0): the cited 0125 drawing page answers this: "a clear strip about 46 ft wide" (the code uses 46 px, not px(46)); 0147 answers the gate buildings' clearance, "about 36 ft clear around each" (the code uses 32 px); both should cite those blocks
- `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.wall#guard station and tower` (MISLABELED, E0): 0147 answers both: a town gate has "a 13 ft passage under a tower about 40 by 24 ft" and a "small guard room ... about 12 by 18 ft just inside it", but the code draws a 40 x 40 px tower beside the gate and a 96 x 46 px station; the claim should cite 0147, and the code is off from it
- `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.castle#each bailey's gate turned 90 degrees from its parent's (the dogleg route)` (UNCLAIMED, E0): claim it: each bailey's gate turned 90 degrees from its parent's (the dogleg route)
- `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.martial_hall#the layout: hall across the north, lane on the south band, sensei's house between, azuchi 10 ft deep, shooting line 6 ft` (UNCLAIMED, E0): claim it: the layout: hall across the north, lane on the south band, sensei's house between, azuchi 10 ft deep, shooting line 6 ft from the lane's end
- `l7r/diagram/settlement/castle_civic.py::honmaru_fracs#the honmaru held to at most 0.34 of a small enceinte's half-sides` (UNCLAIMED, E0): claim it: the honmaru held to at most 0.34 of a small enceinte's half-sides
- `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#longer plank at a junction` (MISLABELED, E0): 0084 answers this: it lists "the joins of ditches" among things that rule a seat out, and holds the span at "about 8 ft" because a longer board "would read as a jetty"; the code instead widens the deck over the junction. Should cite 0084, and against it this is a drift
- `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#off dry crops, gardens and groves` (MISLABELED, E0): 0084 answers it ("Houses, crops, other crossings ... can rule out every wide spot"); should cite 0084, not UNRESEARCHED
- `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#short abutment` (CANNOT-TELL, E1, tiered by its work at T25a): PLANK_ABUTMENT becomes a real-feet figure converted at each use (self.px), sized so a deck over a 2.5 ft ditch spans about 8 ft (0084 drawing), in place of 6 px at every grain
- `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#supply ditches only` (NEEDS-RESEARCH, E0, tiered by its work at T25a): split the claim: no plank over the collector or drain cited to 0084 drawing (the foot drains and diagonal edge drains), and the feeder's exclusion from SUPPLY_ROLES claimed UNRESEARCHED
- `l7r/diagram/settlement/city/walls.py::WallsMixin._gate_caption#ground reserved round the gate works` (DRIFTED, E1, tiered by its work at T25a): the guard house and inspection hall's reserved margin becomes self.px(36) (about 36 ft clear around each) in place of the fixed 12 px
- `l7r/diagram/settlement/city/walls.py::WallsMixin._seat_mural_towers#exempt stretches` (DRIFTED, E1, tiered by its work at T25a): the coverage sweep's exempt stretches become self.px(390) of a gate and self.px(165) of its guard buildings in place of the fixed 130 and 55 px
- `l7r/diagram/settlement/city/walls.py::WallsMixin._seat_mural_towers#reach counted from the parapet` (DRIFTED, E1, tiered by its work at T25a): a tower's reach is counted from its parapet at self.px(36) out from its center (0148 drawing) in place of the fixed `+ 12.0` px, and the stale half-footprint comment goes
- `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#assumed water widths when a record has none (DEFAULT_W: streams 9.0, channels 2.5, ditches 4.2)` (UNCLAIMED, E0): claim it: assumed water widths when a record has none (DEFAULT_W: streams 9.0, channels 2.5, ditches 4.2)
- `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#a seat nearer a drain or collector than its own ditch refused (plank_on_supply)` (UNCLAIMED, E0): claim it: a seat nearer a drain or collector than its own ditch refused (plank_on_supply)
- `l7r/diagram/settlement/city/walls.py::WallsMixin._gate_flanking_buildings#fallback road width px(26) for the verge setback` (UNCLAIMED, E0): claim it: fallback road width px(26) for the verge setback
- `l7r/diagram/settlement/city/walls.py::WallsMixin._gate_flanking_buildings#guard buildings turned square to the local wall tangent` (UNCLAIMED, E0): claim it: guard buildings turned square to the local wall tangent
- `l7r/diagram/settlement/city/walls.py::WallsMixin._seat_mural_towers#mural tower nudged outward onto the berm, px(40)` (UNCLAIMED, E0): claim it: mural tower nudged outward onto the berm, px(40)
- `l7r/diagram/settlement/city/walls.py::WallsMixin._seat_mural_towers#a slid tower kept at least 45 px from a gate` (UNCLAIMED, E0): claim it: a slid tower kept at least 45 px from a gate
- `l7r/diagram/settlement/city/moat.py::MoatMixin.water_gate#arch on two piers with a grille` (DRIFTED, E2, tiered by its work at T25a): draw a grille at both the outer and the inner face of the wall and the stone-lined channel between them (0179 drawing) in place of one set of bars
- `l7r/diagram/settlement/city/canals.py::CanalsMixin.farmland_ring#non-moat (river) taps are never swept; the head race leaves on the outward bearing, unaligned with the current` (UNCLAIMED, E0): claim it: non-moat (river) taps are never swept; the head race leaves on the outward bearing, unaligned with the current
- `l7r/diagram/settlement/city/canals.py::CanalsMixin.farmland_ring#sluice set radially outward from the city center (or the caller's bearing)` (UNCLAIMED, E0): claim it: sluice set radially outward from the city center (or the caller's bearing)
- `l7r/diagram/settlement/civic_grounds/justice.py::JusticeGroundsMixin.boundary_marker#one stone drawn, where 0217 draws a group of one to three at an entrance` (UNCLAIMED, E0): claim it: one stone drawn, where 0217 draws a group of one to three at an entrance
- `l7r/diagram/settlement/civic_grounds/justice.py::JusticeGroundsMixin.execution_ground#two post sockets about 3 ft square, and their spacing` (UNCLAIMED, E0): claim it: two post sockets about 3 ft square, and their spacing
- `l7r/diagram/hamletgen/ways/track.py::_thread_the_fabric#the track's route walled` (MISLABELED, E0): 0246 walls only a back lane's stretches (§63); the track's walls are in 0081 ("never crosses row crops", "stops at the flooded paddy", "keeps off wet ground"), and keeping off drawn water belongs to 0035's crossing rule; repoint to 0081 (and 0035 for the water)
- `l7r/diagram/hamletgen/ways/track.py::stage_track#row road` (MISLABELED, E0): 0033 backs the run off the map, but it is silent on the ford; the crossing (ford_crossing) rests on 0035, so add 0035 for "over a ford"
- `l7r/diagram/hamletgen/ways/track.py::stage_track#spur clip margin` (MISLABELED, E0): 0081 answers this: a lane "may touch a plot's boundary", and the path joins the bund; a 12 ft margin off the dry plots is a DEVIATION from §9, not UNRESEARCHED (only the toe-band margin is unanswered)
- `l7r/diagram/labels/standard.py::REACH_EM#how far the ringed search runs` (MISLABELED, E0): how far a caption is displaced before its leader is how it is shown (0242 calls the gap "our calibration"); the label should be CONVENTION, not UNRESEARCHED
- `l7r/diagram/overlap/taxonomy.py::_LABEL_GROUP#an arch is never covered` (MISLABELED, E0): this is the GM's ruling (2026-07-27, "never be covered by the 'temple of X' label"), and it overrides 0243's "its own building or compound"; the label should be CANON naming that ruling
- `l7r/diagram/hamletgen/ways/law.py::near_misses#a household way's door end is never counted as a join that stops short` (UNCLAIMED, E0): claim it: a household way's door end is never counted as a join that stops short
- `l7r/diagram/hamletgen/ways/track.py::stage_track#spur tip set back 17 ft (SPUR_SETBACK) off the field outline's vertex` (UNCLAIMED, E0): claim it: spur tip set back 17 ft (SPUR_SETBACK) off the field outline's vertex
- `l7r/diagram/hamletgen/ways/track.py::stage_track#connector and spur keep a 40 ft no-build clearance (LANE_CLEARANCE)` (UNCLAIMED, E0): claim it: connector and spur keep a 40 ft no-build clearance (LANE_CLEARANCE)
- `l7r/diagram/settlement/city/moat.py::MoatMixin.water_gate#pier depth through the wall, 30 ft` (UNCLAIMED, E0): claim it: the piers 30 ft deep through the wall, UNRESEARCHED (0147 gives a water gate's opening and pier width, not its depth)
- `l7r/diagram/settlement/city/moat.py::MoatMixin.water_gate#one opening whatever the canal` (UNCLAIMED, E0): claim it: one 60 ft opening whatever the canal; 0179 makes the passage as wide as its canal and gives a river a row of arched openings - claim against 0179 (a drift to rank if the canal is narrower or a river)
- `l7r/diagram/settlement/structures/fixtures/_helpers.py::kosatsuba_anchor#board placements` (DRIFTED, E3, tiered by its work at T25a): add the bridge end (0190: a village board stands at a bridge end) to the rolled board placements, as a `kosatsuba_seat` option with its own anchor
- `l7r/diagram/settlement/structures/fixtures/_helpers.py::kosatsuba_handover#a through track's handover` (NEEDS-RESEARCH, E0, tiered by its work at T25a): claim the through track's handover UNRESEARCHED: where both ends are off the sheet, the lane end joining it nearest the houses' middle (0190 says only entrance)
- `l7r/diagram/hamletgen/ways/track.py::stage_track#valley and polder connector width CONNECTOR_WIDTH 6 ft` (UNCLAIMED, E0): claim it: valley and polder connector width CONNECTOR_WIDTH 6 ft
- `l7r/diagram/settlement/structures/fixtures/_helpers.py::kosatsuba_anchor#the approach counts as reaching the houses within KOSATSUBA_ENTRANCE_REACH_FT 100 ft of a dwelling` (UNCLAIMED, E0): claim it: the approach counts as reaching the houses within KOSATSUBA_ENTRANCE_REACH_FT 100 ft of a dwelling
- `l7r/diagram/interactive/place.py::KINDS#a hamlet's dead burned and buried at the main village's` (UNCLAIMED, E0): claim it: a hamlet has no cremation ground; its dead are burned and buried at the main village's, which holds the district's grounds - cite the burial question (0236)

T25a (amendment 6) tiered the rows above that the re-checks had tiered by their verdict alone by the work each takes;
each bullet now carries its tier and fix line as `ranking.json` holds them.


## Wave 6 (2026-10-07)

Wave 6 wrote or relabeled the claims of every open E0 row (claim lines only), in two rounds of re-checks, and lifted the
lane law's water rules out of `law.py` at the 1,000-line bar (`law_water.py`, units unchanged). Where a claim now cites the
page that answers it, the code stands stated against that page; each such departure, and what the re-checks found beside
the claims, is a found row in `ranking.json` (`audit/found-wave6.jsonl`), tiered provisionally by its verdict (a drift E1,
a claim fix E0, a question for the record E4):

- `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.castle#inner moat width` (DRIFTED, E2, tiered by its work at T25a): draw the inner moat at least 98 ft wide (0139: Hiroshima's inner moat 30 to 104 m) in place of `mw * 0.5`, and move its ring (`ir = gap * 0.42`) out far enough that the broader water clears the honmaru wall
- `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.wall#ground round the gate structures` (DRIFTED, E1, tiered by its work at T25a): the gate structures' reserved margin becomes self.px(36) (about 36 ft clear around each) in place of the fixed `bm = 32` px
- `l7r/diagram/settlement/city/canals.py::CanalsMixin.farmland_ring#a river tap unswept` (DRIFTED, E2, tiered by its work at T25a): sweep a river tap downstream as a moat tap is swept (`moat_swept_tap`, read along the river's source-to-mouth order), leaving at 0054's drawn 35 degrees off the downstream heading, not on the outward bearing
- `l7r/diagram/settlement/city/moat.py::MoatMixin.water_gate#one opening` (DRIFTED, E3, tiered by its work at T25a): size the water gate's opening to its canal's width (0179 drawing) in place of the fixed 60 ft, with the wall's gap following it, and draw a river crossing the wall as a row of arched openings
- `l7r/diagram/settlement/city/walls.py::WallsMixin._gate_flanking_buildings#fallback road width` (DRIFTED, E1, tiered by its work at T25a): the fallback road width becomes self.px(30) (0147 drawing: the gate's 30 ft is the trunk road's width) in place of px(26), and the claim names `road_width`, not a ring road
- `l7r/diagram/settlement/city/walls.py::WallsMixin._seat_mural_towers#a slid tower off a gate` (DRIFTED, E1, tiered by its work at T25a): hold a slid mural tower to self.px(390) from every gate (0148 drawing: no tower within 390 ft of a gate) in place of the fixed 45 px
- `l7r/diagram/settlement/city/walls.py::WallsMixin._seat_mural_towers#tower onto the berm` (CANNOT-TELL, E3, tiered by its work at T25a): seat each mural tower so its 40 ft platform stands out past the wall face (0148 drawing: 12 m, about 39 ft, out) in place of nudging it inward to a 6 px outer projection, with the moat's berm made wide enough to keep it dry
- `l7r/diagram/hamletgen/ways/track.py::stage_track#lane clearance` (DRIFTED, E1, tiered by its work at T25a): LANE_CLEARANCE becomes 7 ft (0246 drawing: a lane's middle keeps 7 ft clear of a garden fence and nothing is built on its tread) in place of the 40 ft corridor, and the claim cites 0246.drawing for it
- `l7r/diagram/settlement/civic_grounds/justice.py::JusticeGroundsMixin.boundary_marker#how many stones` (DRIFTED, E2, tiered by its work at T25a): roll each entrance's stone count from 1 to 3 from the map's seed (0217 drawing: a map draws a group rather than a single stone) and draw and record that many stones as a group
- `l7r/diagram/settlement/structures/fixtures/_helpers.py::kosatsuba_anchor#reaching the houses` (DRIFTED, E1, tiered by its work at T25a): KOSATSUBA_ENTRANCE_REACH_FT becomes 60 ft, cited as GUESS to 0246 drawing (a way reaches a farmhouse within 60 ft of it), in place of 100 ft
- `l7r/diagram/hamletgen/ways/law_water.py::oblique_at#square ditch crossing` (NEEDS-RESEARCH, E0, tiered by its work at T25a): claim the channel crossing UNRESEARCHED: squared within FORD_SQUARE_TOL_DEG, 10 degrees (0084 squares only the standalone footplank; 0087 solves a carried deck at its way's angle and gives no tolerance), the brook keeping its 0035 citation
- `l7r/diagram/settlement/castle_civic.py::CastleCivicMixin.martial_hall#practice gear` (MISLABELED, E1, tiered by its work at T25a): drop the practice gear from the state hall's compound (the `_keiko_gear` call) so it is drawn as its wall and three features, the rest implied, and cite research/questions/0165-martial-training-grounds-and-dojo.drawing.html for it
- `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#assumed ditch width` (DRIFTED, E1, tiered by its work at T25a): the field ditch's assumed width becomes self.px(2.5) (0084 drawing: 2.5 ft at the head, tapering toward 1.2 ft) in place of 4.2 px, in both `DEFAULT_W["field_ditches"]` and `d.get("w", 4.2)`
- `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#assumed stream and channel widths` (MISLABELED, E1, tiered by its work at T25a): the brook's assumed width becomes self.px(7) (0035 drawing: a brook 7 ft wide) in place of the 9 px `DEFAULT_W["streams"]`, cited to 0035, and the channel's 2.5 px default is claimed UNRESEARCHED
- `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#off dry crops and gardens` (DRIFTED, E2, tiered by its work at T25a): keep the narrow seats as a fallback: offer the seats whose water earns a board first, and when houses, crops, other crossings or joins rule out every one, lay the crossing at the widest seat remaining (0084 drawing) rather than none
- `l7r/diagram/hamletgen/ways/law_water.py::off_ford_at#how far from a crossing place a brook crossing may stand, FORD_HALF 30 ft` (UNCLAIMED, E0, tiered by its work at T25a): claim off_ford_at's reach: how far from a crossing place a brook crossing may stand - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: FORD_HALF, half the 60 ft crossing place, 30 ft
- `l7r/diagram/hamletgen/ways/law_water.py::short_decks#assumed water widths where none is recorded: 3 ft for a ditch or channel, 6 ft for a stream` (UNCLAIMED, E0): claim it: assumed water widths where none is recorded, 3 ft for a ditch or channel, 6 ft for a stream

T25a (amendment 6) tiered the rows above that the re-checks had tiered by their verdict alone by the work each takes;
each bullet now carries its tier and fix line as `ranking.json` holds them.

## Wave 7 (2026-10-07)

Wave 7 took the open E0 claims and E1 rows 183-234, after T25a tiered the provisional rows by their work: the plank's
abutment and assumed widths in feet, the samurai caption's estates, the castle wall's and city gate's figures in feet, the
civic grounds' sizes, counts and reaches, the boundary stone at its true size, the city note claimed CANON (the GM's
feature-156 request). The connector's clearance was held at 40 ft: 0246's 7 ft is measured to a fence, and the corridor is a
center test, so the edge-based test is its own E2 row. The rows the re-checks left open carry their new fix lines in
`ranking.json` (`audit/overrides.json`). The gate counts the findings below as introduced: each is a found row
(`audit/found-wave7.jsonl`), tiered provisionally by its verdict until a read by its work (as T25a) before an E1 wave takes it.

- `l7r/diagram/settlement/civic_grounds/civic.py::CivicWorksMixin.merchant_storehouses#a kura behind the shop` (DRIFTED, E1): the page puts storehouses "at the back of the lot", thick along the block backs; the code tucks the kura 2 px into the shop's own back wall (off = h/2 + kh/2 - 2), not at the lot's rear
- `l7r/diagram/settlement/civic_grounds/civic.py::CivicWorksMixin.terrace#cell frontage` (DRIFTED, E1): 18 x 24 ft gives a 432 sq ft cell, Shibata's lowest-retainer unit, but the drawing page sets the setting's Rank 1-4 terrace at "a drawn unit of about 990 square feet", above Shibata's 430; the cell should grow, or the claim should be a DEVIATION the drawing page records
- `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cemetery#keep-clear margin` (MISLABELED, E0): the record does speak: "no cleared band is drawn around it. Other features are placed without regard to the plot's cleared ground", and no set distance from houses is drawn; the claim should cite 0224/0235, and against them the 8 px block band drifts
- `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cremation_ground#keep-clear margin` (MISLABELED, E0): the page answers keep-clear: "keeps 120 ft clear of houses and wells", and "No fire clearance is drawn around a pyre"; the claim should cite 0238, and the 8 px band (about 24 ft) matches neither
- `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cremation_ground#six jizo at a burial ground's entrance` (DRIFTED, E1): the pages put the six jizo "at the entrance of a village's burial ground", shared with a cremation ground beside it; the code seats them on the cremation ground's own north rim (cy - cry - jh), whatever side the burial ground is on
- `l7r/diagram/settlement/civic_grounds/stable_yard.py::StableYardMixin._yard_watering#trough count` (DRIFTED, E1): the page says "a plain stables yard draws two troughs, and a caravan ground three"; the code keys on r >= 76 px, but animal_ground's default r is px(127.5), about 42 px at 3 ft/px, the same as a stables yard, so a default caravan ground draws 2; key the count on the yard's kind
- `l7r/diagram/settlement/civic_grounds/civic.py::CivicWorksMixin.precinct_interior#parish plot seated at the precinct's rear, east of the axis (x+44, 14 px in from the rear edge)` (UNCLAIMED, E0): claim it: parish plot seated at the precinct's rear, east of the axis (x+44, 14 px in from the rear edge)
- `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cemetery#no six jizo drawn at a burial ground's entrance unless a cremation ground stands beside it` (UNCLAIMED, E0): claim it: no six jizo drawn at a burial ground's entrance unless a cremation ground stands beside it
- `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cremation_ground#cleared ground's depth 0.7 of its width` (UNCLAIMED, E0): claim it: cleared ground's depth 0.7 of its width
- `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cremation_ground#fire bed always a stone-framed trench (never an open pyre)` (UNCLAIMED, E0): claim it: fire bed always a stone-framed trench (never an open pyre)
- `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cremation_ground#snow-country walled hut over the bed never drawn` (UNCLAIMED, E0): claim it: snow-country walled hut over the bed never drawn
- `l7r/diagram/settlement/city/bridges.py::BridgesMixin.channel_footbridges#obliqueness ceiling` (MISLABELED, E0): the ceiling allows a deck up to 3x the nominal span, and 0084 drawing answers how long a deck runs ("spans about 8 ft", joins rule a seat out); the claim should cite it, and against it the ceiling is part of the junction drift
- `l7r/diagram/hamletgen/consts.py::LANE_CLEARANCE#fronting lane's corridor` (DRIFTED, E1): the 7 ft is §16's figure, but §16 measures from the garden fence to the lane's middle, and the constant's own comment says `_near_corridor` tests a candidate's CENTER; I need the corridor test in Settlement.lane to tell whether 7 ft is measured to a fence or footprint, or to a center. The 40 ft derivation in the comment is stale
- `l7r/diagram/hamletgen/ways/bund.py::a_way_onto_the_bund#water between is crossed` (NEEDS-RESEARCH, E4): 0084 says a way over water takes one planked deck, but nothing in it caps the way at one watercourse (`for over in (0, 1)`); the cap should be claimed UNRESEARCHED
- `l7r/diagram/hamletgen/ways/bund.py::carry_on#stepped spur's corridor` (DRIFTED, E1): passes LANE_CLEARANCE, 7 ft, as §16 gives
- `l7r/diagram/hamletgen/ways/law_water.py::off_ford_at#how far off a crossing place` (NEEDS-RESEARCH, E4): 0035 sets crossing places about every 160 ft but gives no 60 ft width for one, so the 30 ft FORD_HALF reach is unresearched
- `l7r/diagram/hamletgen/ways/law_water.py::short_decks#assumed water widths` (MISLABELED, E0): the bundle gives these widths: delivery ditches 2.5 ft at the head tapering to 1.2 ft (0084), and the brook 7 ft (0035). The 3 ft and 6 ft defaults should cite those pages, and they differ from them
- `l7r/diagram/hamletgen/ways/web.py::_lay_skeleton#skeleton margin off the hard ground` (MISLABELED, E0): 0081 answers this for the crops: a lane "may touch a plot's boundary". The 20 ft off the crops should be a DEVIATION recorded on 0081; only the marsh and ditch part stays UNRESEARCHED
- `l7r/diagram/interactive/place.py::KINDS#a city's figure takes in its samurai country estates` (MISLABELED, E0): 0001 answers this, and the other way: a provincial city's "about 3,000 ... counts only those living within the walls". Either 0001 records the GM's feature-156 ruling, or the claim cites 0001 and the text in place.json follows it. I could not see place.json's wording
- `l7r/diagram/hamletgen/ways/bund.py::a_way_onto_the_bund#a lane end within 6 ft of the paddy (BUND_REACH_FT) counts as on the bund` (UNCLAIMED, E0): claim it: a lane end within 6 ft of the paddy (BUND_REACH_FT) counts as on the bund
- `l7r/diagram/hamletgen/ways/bund.py::a_way_onto_the_bund#branched field path 5 ft wide (BRANCH_WIDTH)` (UNCLAIMED, E0): claim it: branched field path 5 ft wide (BRANCH_WIDTH)
- `l7r/diagram/hamletgen/ways/bund.py::carry_on#stepped field path 5 ft wide (BRANCH_WIDTH)` (UNCLAIMED, E0): claim it: stepped field path 5 ft wide (BRANCH_WIDTH)
- `l7r/diagram/hamletgen/ways/serve.py::_lay_web_lane#a run within 25 ft of the network counts as arrived (_LANE_JOIN_FT)` (UNCLAIMED, E0): claim it: a run within 25 ft of the network counts as arrived (_LANE_JOIN_FT)
- `l7r/diagram/hamletgen/ways/serve.py::_lay_web_lane#link kept 8 ft off hard ground, 7 ft off walls` (UNCLAIMED, E0): claim it: link kept 8 ft off hard ground, 7 ft off walls
- `l7r/diagram/hamletgen/ways/street.py::row_reach#a farm frame taken as 100 ft where none is recorded (0033 gives 220-260 ft)` (UNCLAIMED, E0): claim it: a farm frame taken as 100 ft where none is recorded (0033 gives 220-260 ft)
- `l7r/diagram/hamletgen/ways/web.py::_lay_skeleton#skeleton arm's no-build corridor LANE_CLEARANCE, 7 ft` (UNCLAIMED, E0): claim it: skeleton arm's no-build corridor LANE_CLEARANCE, 7 ft
- `l7r/diagram/hamletgen/ways/bund.py::a_way_onto_the_bund#a lane end within 6 ft (BUND_REACH_FT) of the paddy counts as joined to the bund` (UNCLAIMED, E0): claim it: a lane end within 6 ft (BUND_REACH_FT) of the paddy counts as joined to the bund
- `l7r/diagram/hamletgen/ways/bund.py::a_way_onto_the_bund#the branched field path 5 ft wide (BRANCH_WIDTH) with the LANE_CLEARANCE corridor` (UNCLAIMED, E0): claim it: the branched field path 5 ft wide (BRANCH_WIDTH) with the LANE_CLEARANCE corridor
- `l7r/diagram/hamletgen/ways/bund.py::carry_on#the stepped field path drawn 5 ft wide (BRANCH_WIDTH)` (UNCLAIMED, E0): claim it: the stepped field path drawn 5 ft wide (BRANCH_WIDTH)
- `l7r/diagram/hamletgen/ways/web.py::_lay_skeleton#each skeleton arm registers the 40 ft LANE_CLEARANCE no-build corridor` (UNCLAIMED, E0): claim it: each skeleton arm registers the 40 ft LANE_CLEARANCE no-build corridor

## Wave 8 (2026-10-07)

Wave 8 wrote the open E0 claims (each claim that states a drift naming the found row that fixes it, D8) and took E1 rows
187-247: the deck's assumed widths, a row farm's frame (0033), the temple and gate caption words, the city wall's four exempt
stretches, the terrace unit, the cemetery's and cremation ground's margins and first row. The gate counts the findings below
as introduced: each is a found row (`audit/found-wave8.jsonl`), the drift a claim now states or what the re-checks found
beside the changed claims, tiered provisionally by its verdict until a read by its work.

- `l7r/diagram/hamletgen/ways/street.py::row_reach#a farm frame where none is recorded` (DRIFTED, E1): take a farm frame where none is recorded at 0033's 220-260 ft (a row village's holding) in place of the BUNDLE_PITCH fallback
- `l7r/diagram/hamletgen/ways/law_water.py::oblique_at#a channel crossing at its way's angle` (NEEDS-RESEARCH, E4): 0087 solves a carried deck at its way's angle while the crossing rows of checks.py square every crossing over water: reconcile the two pages on a lane over a channel before dropping or keeping the 10 degree squaring
- `l7r/diagram/settlement/civic_grounds/funerary.py::cremation_ground#the fire bed's two forms` (DRIFTED, E3): roll the fire bed between 0238's two attested forms, a stack of firewood in open country away from the houses and a stone-framed trench beside a burial ground, as a knob per ground
- `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cremation_ground#the snow-country hut` (DRIFTED, E3): draw 0238's snow-country form, a walled hut of four to six tatami over the bed, where the map is snow country, beside the open bed and the four-post roof
- `l7r/diagram/hamletgen/ways/bund.py::a_way_onto_the_bund#field path width` (MISLABELED, E0): the 5 ft spur width matches, but the claim also cites 0081 for the `LANE_CLEARANCE` 40 ft corridor, and 0081 gives no clearance figure; the corridor belongs to 0246 §85 (7 ft from fence to lane middle) as its own claim, which carries the same mismatch as the skeleton corridor
- `l7r/diagram/hamletgen/ways/bund.py::a_way_onto_the_bund#on the bund` (DRIFTED, E1): `paddy.dist(q) <= BUND_REACH_FT` returns "joined" with the end left where it is, so a path can stop up to 6 ft short of the bund in open ground; §21 says the path "never ends in open ground short of the bund". The end should be carried on until it touches the bund, and no page gives the 6 ft
- `l7r/diagram/hamletgen/ways/serve.py::_lay_web_lane#arrived at the network` (DRIFTED, E1): a run passing within 25 ft is counted as arrived without its tread reaching the network: the mid-run branch draws with no snap, and the end branch leaves the gap when `_clear_link` fails. §65 joins ends "at a single point" and §84 joins lanes "where their treads meet"; 25 ft should be the reach that triggers a join, not a gap that stays open
- `l7r/diagram/hamletgen/ways/serve.py::_lay_web_lane#link off hard ground and walls` (MISLABELED, E0): the 7 ft off walls (`WEB_FABRIC_GAP`) is 0246's figure, a lane's middle 7 ft clear of a garden fence, so it should cite 0246; only the 8 ft off hard ground stays UNRESEARCHED (0081 §53 lets a lane touch a plot's boundary)
- `l7r/diagram/hamletgen/ways/web.py::_lay_skeleton#skeleton arm's corridor` (DRIFTED, E1): `s.lane(piece, width=5, clearance=LANE_CLEARANCE)` registers a 40 ft center corridor, while 0246 sets the lane's room at 18 ft, "7 ft at each garden fence"; the claim itself says the edge-based corridor row still has to fix it. It should be 7 ft from fence to middle, or a recorded DEVIATION
- `l7r/diagram/hamletgen/ways/serve.py::_lay_web_lane#a healing link kept if its ends lie within 12 ft of the run and of the network (`_reach < 12.0`, `_net_reach < 12.0`), a` (UNCLAIMED, E0): claim it: a healing link kept if its ends lie within 12 ft of the run and of the network (`_reach < 12.0`, `_net_reach < 12.0`), a gap left unjoined
- `l7r/diagram/settlement/civic_grounds/civic.py::CivicWorksMixin.precinct_interior#parish plot's seat` (MISLABELED, E0): 0227 places "the graveyard outside the cloister at the back", which answers the rear seat; cite 0227 for the rear and keep only the east-of-axis offset (x+44) as GUESS
- `l7r/diagram/settlement/civic_grounds/civic.py::CivicWorksMixin.terrace#frontage and depth` (MISLABELED, E0): 0140 gives the row-house cell's shape, "about 18 ft of frontage" on a 24 ft depth (frontage under depth, single-file), but 33 x 30 makes cells wider than deep; cite 0140 §137 and keep that proportion scaled to 990 sq ft (about 27 x 36 ft); the docstring's "~21 ft deep" is stale
- `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cemetery#six jizo at its entrance` (DRIFTED, E1): cemetery draws no jizo at all, but the page has "Six small stone jizo stand in a row at the entrance of a village's burial ground"; the claim itself admits it; draw them at the burial ground's entrance here
- `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cremation_ground#fire bed's form` (DRIFTED, E1): the claim records two attested forms (a firewood stack and a stone-framed trench), yet the code always draws the framed trench and no drawing page records that as a deviation; roll per seed. The cited drawing page names neither form, so the claim should also cite 0238.html
- `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cremation_ground#no walled hut` (DRIFTED, E1): the page attests "in snow country, set in a walled hut of about four to six tatami", but the code rolls only open or roofed and never draws the hut; add it as a form, keyed to snow country
- `l7r/diagram/labels/obstacles.py::GROUP_WORDS#a shrine caption may cover the temples (0243 §11)` (UNCLAIMED, E0): claim it: a shrine caption may cover the temples (0243 §11)
- `l7r/diagram/labels/obstacles.py::GROUP_WORDS#a guard or inspection caption may cover the gate's posts (0243 §9)` (UNCLAIMED, E0): claim it: a guard or inspection caption may cover the gate's posts (0243 §9)
- `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cemetery#stupa height 13 px and its seats (rear corners of a ruled plot, interior of an organic one)` (UNCLAIMED, E0): claim it: stupa height 13 px and its seats (rear corners of a ruled plot, interior of an organic one)
- `l7r/diagram/settlement/civic_grounds/funerary.py::FuneraryGroundsMixin.cremation_ground#jizo true size px(2.0) x px(2.7) ft against 0235 §102's "about 2 ft tall", and their 1.4-width pitch` (UNCLAIMED, E0): claim it: jizo true size px(2.0) x px(2.7) ft against 0235 §102's "about 2 ft tall", and their 1.4-width pitch

## Wave 9 (2026-10-07)

Wave 9 wrote the five open in-scope E0 claims and took in-scope E1 rows 265-297 (the scope of amendment 8): the kura's
west annex held to the shed band, the comb's and pond's feeder and outfall widths, the privy, yard-privy and wood-shed steps
off their walls, the privy's 48 ft sun reach, the lesser broadleaf floor and the windbreak's conifer share, the belt's 80 ft
depth and 30 ft gap in feet, the 50 ft morning-sun reach east of a bed (the dispersed layout's own reach as well), the
garden cap, the dike gate's 20 ft span and the 39 ft house shade. Three rows were re-tiered by their work: the commons fill
to E2 (a glyph change) and the two surface-water rows to E4 (0196 against the recorded 2026-08-18 ruling). The re-checks of
the changed units found the rows below (`audit/found-wave9.jsonl`), tiered provisionally by verdict until a read by their work.

- `l7r/diagram/hamletgen/ways/bund.py::a_way_onto_the_bund#field path's corridor` (DRIFTED, E3): the claim states the drift: the corridor is 0246's 7 ft to a fence held as a 40 ft center corridor; fixed by the edge-based corridor row (consts.py::LANE_CLEARANCE)
- `l7r/diagram/settlement/farm_fixtures.py::KURA_PARTS#free-standing storage shed` (DRIFTED, E3): draw 0052's free-standing storage shed (18-27 ft, roof rolled) on about one farm in three, or record the omission as a DEVIATION through the exception path
- `l7r/diagram/settlement/farm_fixtures.py::KURA_PARTS#north annex` (MISLABELED, E0): cite 0040's drawing page for the back-wall placement; 0052 gives the band
- `l7r/diagram/settlement/fields/comb.py::CombMixin._comb_draw_ditches#drain outfall` (CANNOT-TELL, E0): re-check with outfall_run in the bundle (0067: the turn out of the collector held to 55 degrees or less)
- `l7r/diagram/settlement/fields/comb.py::CombMixin._comb_draw_ditches#outfall corridor` (DRIFTED, E2): on a hamlet or village map use the below-the-drain rule; the 33 ft corridor from a channel's centerline is the town and city rule, and in feet (px(33))
- `l7r/diagram/settlement/fields/comb.py::CombMixin._comb_draw_source#feeder brook` (DRIFTED, E2): the feeder brook runs on past the intake (0196: never a brook taken whole by its ditch)
- `l7r/diagram/settlement/fields/comb.py::CombMixin._comb_draw_source#feeder brook width` (DRIFTED, E1): feeder brook width=7 px -> self.px(7.0), stored in feet (0068)
- `l7r/diagram/settlement/fields/comb.py::CombMixin._comb_draw_source#planted pond bank` (MISLABELED, E0): the page records every bank drawn bare as the project's choice: DEVIATION 0061, through the exception path
- `l7r/diagram/settlement/land/dikes.py::DikeMixin.dike_gates#gate glyph at the polder cut` (CANNOT-TELL, E0): re-check with sluice_gate and its callers' span_ft in the bundle (0179: a 16-24 ft span)
- `l7r/diagram/settlement/homestead_parts/fixture_seats.py::_seats#privy seats` (DRIFTED, E2): seat the barn-side privy against a barn's outer wall (0047), not the house's own +x end, or record the house-end seat on the page
- `l7r/diagram/settlement/homestead_parts/fixture_seats.py::shed_off_a_wall#wood shed a ken off a wall` (DRIFTED, E1): admit a shed only a ken (6 ft) off its wall, not g + a ken + a STEP_FT (about 14 ft)
- `l7r/diagram/settlement/homestead_parts/fixture_seats.py::_wood_shed#wood shed seats` (CANNOT-TELL, E0): re-check with wall_places and against_a_wall in the bundle: never the front yard (0051)
- `l7r/diagram/settlement/homestead_parts/fixture_seats.py::_seats#manure heap fallback spots` (UNCLAIMED, E0): the manure heap's fallback spots (beside the privy at 1.1 and 1.9 widths, 10 ft further out) and its no-privy seats at 0.3 hw / 0.3 hh
- `l7r/diagram/settlement/homestead_parts/fixture_seats.py::_wood_shed#wood shed fallback seats` (UNCLAIMED, E0): the wood shed's fallback seats paced a further STEP_FT (8 ft) out beyond the ken seats
- `l7r/diagram/settlement/homestead_parts/groves.py::GrovesMixin._draw_grove#crown over no roof or wellhead` (MISLABELED, E0): add 0072's drawing page for the wellhead (a wellhead in a belt removes the clumps round it)
- `l7r/diagram/settlement/homestead_parts/groves.py::GrovesMixin._draw_grove#crown size` (DRIFTED, E1): hold every crown to 0080's 0.75-1.4 of the mean radius, one size for hill woods and windbreak cedars alike (no conifer x1.15)
- `l7r/diagram/settlement/homestead_parts/groves.py::GrovesMixin._draw_grove#crowns per clump ceiling` (MISLABELED, E0): the cap of 28 overrides 0080's density on large clumps: a DEVIATION through the exception path, or drop the cap
- `l7r/diagram/settlement/homestead_parts/groves.py::GrovesMixin._draw_grove#crowns per clump floor` (MISLABELED, E0): the floor of 5 over-stocks small clumps against 0080's density: a DEVIATION through the exception path, or drop the floor
- `l7r/diagram/settlement/homestead_parts/groves.py::GrovesMixin._draw_grove#bamboo patch forced` (UNCLAIMED, E0): a grove item inside the farm's bamboo patch (bamboo_box) forced to bamboo, in any mix and even when bamboo=False
- `l7r/diagram/settlement/homestead_parts/stands.py::StandsMixin.village_grove#clump off buildings, wells and shrines` (MISLABELED, E0): narrow the label to buildings (0071 §15); give the wellhead keep-out (vr + 1.05 clump + 1) its own UNRESEARCHED claim
- `l7r/diagram/settlement/homestead_parts/stands.py::StandsMixin.village_grove#off the plots' sun` (DRIFTED, E2): keep every crown 50 ft east, west and south of a yard or bed (0038), threshing yards included, not the 39 ft house-shade corridor south
- `l7r/diagram/settlement/homestead_parts/stands.py::StandsMixin.village_grove#belt off the deep marsh` (NEEDS-RESEARCH, E0): mark the cut at the reed margin (MARSH_FEATHER_BS) UNRESEARCHED: the page gives no limit on how far in
- `l7r/diagram/settlement/homestead_parts/stands.py::StandsMixin.village_grove#wellhead canopy keep-out` (UNCLAIMED, E0): wellhead canopy keep-out, vr + 1.05 clump + 1
- `l7r/diagram/settlement/homestead_parts/stands.py::StandsMixin.village_grove#copse off the whole marsh` (UNCLAIMED, E0): copse kept off the whole marsh, not only the deep marsh
- `l7r/diagram/settlement/homestead_parts/stands.py::StandsMixin.village_grove#copse mix` (UNCLAIMED, E0): copse drawn in the fruit-and-broadleaf mix, no bamboo or conifer
- `l7r/diagram/settlement/homestead_parts/stands.py::StandsMixin.village_grove#clump inside the page window` (UNCLAIMED, E0): a clump kept only when some of its crown falls inside the page window
- `l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_geom#grove cleared east of turned beds` (UNCLAIMED, E0): a dispersed farm's grove cleared 50 ft east of its turned beds
- `l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_layout#south band off an unkept yard` (UNCLAIMED, E0): south band on a map that does not keep the sun stands YARD_SUN_STRIP 22 off the yard, unscaled
- `l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_layout#byre beside the house` (NEEDS-RESEARCH, E0): mark the flank away from the garden UNRESEARCHED: no page places the byre on a flank
- `l7r/diagram/settlement/rolling/bundle.py::BundleGeomMixin._bundle_layout#storehouse on the north wall` (MISLABELED, E0): the drawing page calls the north-wall annex a convention the record contradicts: DEVIATION 0040, through the exception path
- `l7r/diagram/settlement/farm_fixtures.py::kura_rect#annex held in its band` (DRIFTED, E0): name the recorded exception in the claim: on a house under about 22 ft deep the 1.8 to one wins and the annex runs under 18 ft (the docstring's own measured choice), or keep the 18 ft floor
- `l7r/diagram/settlement/farm_fixtures.py::kura_rect#annex seat` (UNCLAIMED, E0): annex seat: against the north or west wall, and where along that wall (`KURA_PARTS` offsets); 0040's drawing page covers it
- `l7r/diagram/settlement/fields/comb.py::CombMixin._comb_draw_hem#default watercourse widths` (UNCLAIMED, E0): default watercourse widths when a record carries none (stream 9, channel 2.5, canal 14)
- `l7r/diagram/settlement/fields/comb.py::CombMixin._comb_draw_hem#nothing on a dry plot` (UNCLAIMED, E0): nothing built or planted on a dry plot (plots registered in `block_polys` and `dry_polys`)

The gate held one value (FR-004): `l7r/diagram/settlement/homestead_parts/grove_rules.py::gardens_east_shaded#a neighbor's band` (DRIFTED, E3): keep a neighbor farm's grove band 50 ft east of a bed (0038): at 50 ft a row village's next farm's deep west band stands 38 ft east of the bed (Mizuguchi, three farms), so the row frames or the band's reach re-seat; NEIGHBOR_REACH_FT holds the check at 22 ft until then. And it found a Z across a joint on Kuwabata that no
joint pass could mend (the settle draws a tree lane as judged): the seating's judge now refuses a corridor the knot pass would
gather into one (`tree.gathered_zigzag`), and the router lays another.
- `l7r/diagram/hamletgen/ways/tree.py::admits#way out crosses each brook once` (NEEDS-RESEARCH, E0): label the one-crossing limit UNRESEARCHED (0035 prices a crossing at about 150 ft of walk and spaces crossings, but sets no one-per-brook limit), or derive it in the claim's account
- `l7r/diagram/settlement/homestead_parts/grove_rules.py::gardens_east_shaded#east reach below the bed` (DRIFTED, E2): test the band against the page's clear ground from the bed's north edge down to 50 ft below its south edge (0038 §77), not the bed's own height, so a band southeast of the bed is caught
- `l7r/diagram/hamletgen/ways/tree.py::admits#track out's width as judged` (UNCLAIMED, E0): the track out's stub judged at 6 ft (0081's track)
- `l7r/diagram/settlement/homestead_parts/wood_share.py::WoodShares.__init__#afternoon lane as the copse plants` (MISLABELED, E0): cite 0038 (every crown 50 ft west or southwest of a yard or bed) for the copse's west reservation, not NONE
- `l7r/diagram/settlement/homestead_parts/wood_share.py::WoodShares.__init__#sun strip default` (MISLABELED, E2): the copse seats' south strip at 0038's 50 ft, not the 22 ft default labeled GUESS; with the copse's sun ground below (feature 317 measured seats reserved in the west lane left unplanted)
- `l7r/diagram/settlement/homestead_parts/wood_share.py::copse_keepouts#plots' sun strips` (DRIFTED, E2): reserve the copse's seats 50 ft east, west and south of every yard and bed (0038), yards' east included, as the planting holds them
- `l7r/diagram/settlement/homestead_parts/wood_share.py::WoodShares.__init__#copse clump size` (UNCLAIMED, E0): the drawn size of a copse clump (`COPSE_CLUMP_BS` 22 bs)
- `l7r/diagram/settlement/homestead_parts/wood_share.py::WoodShares.__init__#copse seat pitch` (UNCLAIMED, E0): the spacing between copse seats (`SEAT_PITCH_BS` 11*sqrt(2) bs)

### Wave 9: an open regression held for the GM (Kuwabata's zigzag across a joint)

Wave 9's values move Kuwabata's homesteads: either half of the wave alone (the homestead layout rows, or the grove and field
rows) produces it, so no single value can be held. On the new layout, house (4051.7, 1727)'s access lane rounds its
neighbor's forecourt corner and its foot stands 5 ft from that neighbor's door end; the knot pass gathers the foot onto the
door end (0081: ends within 25 ft are one point), and the two lanes walk as a Z (turns of 110 and 86 degrees within 31 ft) -
`test_no_zigzag_straddles_a_joint[kuwabata]`. Measured, rule by rule:

- the joint pass's T and its moved-back joint: the T's foot is the joint itself (the foot stands behind the door lane's first
  leg), and moving the joint drops the door end (`keeps_the_web`); a T on the next leg is a needle join the web refuses; and
  every joint pass is undone by the settle, which draws a tree lane as judged (`settle_tree`)
- the shortcut that drops the overshoot crosses the neighbor's forecourt (the overlap matrix)
- refusing such a way at the seating's judge mends Kuwabata (the household re-seated) but leaves the reference at seed 47
  without its field way (`WebRefused`: two households' ways refused, the field way hosted on them)
- a preference instead (the judge REPORTS the gathered zigzag, onto a fixed door end or a junction only, and the gap pass
  takes such a way only where no other exit is admitted): seed 47 rolls, but Kuwabata's household has no other exit, so its Z
  stands - and the bookends read band 3 (20 households +6.9%, seed 39 +21.8%: every exit tried for a household whose first
  way zigzags). WITHDRAWN: it mended nothing on the pool at that price

The remaining exits (constitution XIII): a re-seat rule for a household whose only ways zigzag that keeps the field way's host
(hours of work, sketch: in the gap pass, when only held ways remain, release the household's seat to the seating's re-seat
queue before the field way is laid), or a GM waiver. Wave 9 stays unpushed in the clone until the GM rules.
