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
- `buildings.md::Outer court (administrative / public)#stables` (DRIFTED, E2): 28-32 ft for 2-4 one-ken stalls (12-24 ft) is longer than a small stable "three bays long"; the horse count is a GUESS the claim presents as research
- `buildings.md::Outer court (administrative / public)#tax archive drawn with white-plaster fill, heavy stroke and dark door mark` (UNCLAIMED, E0): tax archive drawn with white-plaster fill, heavy stroke and dark door mark
- `buildings.md::Sacred features#a fence round the sanctuary alone as a wealth knob (0223 §171-172 finds such fences before 1868 only where the shogunate or a lord built them)` (UNCLAIMED, E0): a fence round the sanctuary alone as a wealth knob (0223 §171-172 finds such fences before 1868 only where the shogunate or a lord built them)
- `buildings.md::Sacred features#grove inside a compound wall` (MISLABELED, E0): 0218's drawing page does answer what stands with a compound shrine: a single tree (the seat of the god is "an old tree or a stone"). The claim should cite 0218 rather than say UNRESEARCHED, and against it a stippled grove rectangle would drift
- `buildings.md::Sacred features#sanctuary` (DRIFTED, E2): ~6 ft square at the back on the axis matches the record, but the page attests two forms: 1 and 3 ken are the commonest widths, and a covering building (oiya) was sometimes built over the sanctuary. The procedure fixes the one-bay, uncovered form; roll the forms or record the choice
- `buildings.md::Sacred features#the whole sacred complex held to at most ~2/3 of the residence` (UNCLAIMED, E0): the whole sacred complex held to at most ~2/3 of the residence
- `buildings.md::Scale#well location marker` (DRIFTED, E2): the page's marker is ~19 ft across (r 9.36 ft), scales with the map, and is calibrated hamlet-to-city at 0.35-0.85 of a dwelling; it marks a ~4 ft curb, not "~3-4 ft". A 22 px (~7 ft) marker at 3 px/ft fits neither the size nor the band; record the plan's marker on the page or redraw
- `buildings/programs.md::Country shrine (a village district's shrine)#a well as the purification stop beside the approach ("the well or basin"; the required item is `well`)` (UNCLAIMED, E0): a well as the purification stop beside the approach ("the well or basin"; the required item is `well`)
- `buildings/programs.md::Country shrine (a village district's shrine)#approach width about 10 ft` (UNCLAIMED, E0): approach width about 10 ft
- `buildings/programs.md::Country shrine (a village district's shrine)#bell tower band 6-16 by 6-16 ft` (UNCLAIMED, E0): bell tower band 6-16 by 6-16 ft
- `buildings/programs.md::Country shrine (a village district's shrine)#building size anchors` (DRIFTED, E2): the table's hall band "18-38 by 18-38 ft" runs past the attested "about 21 to 35 ft" and the claim's own 20-35; and the 46x28 dwelling is not a 0221 finding ("the farmhouse size is a guess"), so that part should be GUESS 0221 drawing
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
- `l7r/diagram/hamletgen/homesteads/capacity.py::free_seats#the exhaustive seat order` (CANNOT-TELL, E4): 0029 drawing §78 sets a seat order for a growing clustered settlement (nearest the cluster, then nearer the fields), while this code sorts by distance from the seat with ties broken by coordinates; I need to know whether the grown (clustered) path calls free_seats: if it does, the label should cite §78 and the tie-break is DRIFTED
- `l7r/diagram/hamletgen/homesteads/farm_water.py::farm_channel#how far a channel's source is sought: 20 ft steps, 60 ft spread, widened fourfold` (UNCLAIMED, E0): how far a channel's source is sought: 20 ft steps, 60 ft spread, widened fourfold
- `l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#a footpath's room off the outline` (MISLABELED, E0): `WEB_FABRIC_GAP * 2.0 + 6.0` (20 ft) is the lane's room 0246 records as a convention ("7 ft at each garden fence and a 4 ft tread ... 20 ft in all"); the label should cite 0246 drawing as CONVENTION, and the code's 6 ft of tread does not match the page's 4 ft tread plus 2 ft parting
- `l7r/diagram/hamletgen/homesteads/stages.py::_seat_households#a yard's sun between ranks` (DRIFTED, E2): the code adds `max(0.0, -oy) * SUN_CORRIDOR_FT`, so only ranks climbing north get the corridor; a rank laid south of the front rank stands just south of that rank's yards, which the 39 ft rule ("no neighbor's farmhouse ... within 39 ft to the south of a yard") forbids equally; ranks should be spaced by the corridor whether they run north or south
- `l7r/diagram/hamletgen/homesteads/wells.py::place_wells#grove farms take their own water and are left out of the communal wells` (UNCLAIMED, E0): grove farms take their own water and are left out of the communal wells
- `l7r/diagram/hamletgen/homesteads/wells.py::place_wells#no well seated over a household's reserved wood-floor seats` (UNCLAIMED, E0): no well seated over a household's reserved wood-floor seats
- `l7r/diagram/hamletgen/ways/serve.py::_lay_web_lane#no way drawn twice` (MISLABELED, E0): refusing a lane that runs beside another (over 60% of the run, or over 100 ft unbroken) decides where lanes exist on the ground, not how they are shown; the label should be GUESS or UNRESEARCHED
- `l7r/diagram/hamletgen/ways/serve.py::_lay_web_lane#not along a shelter belt` (NEEDS-RESEARCH, E4): the page backs the rule ("a belt is kept whole, and a lane must still get through it") but records no 60 ft figure for a lane inside a belt; the 60 ft should be labeled GUESS or be recorded on the drawing page
- `l7r/diagram/hamletgen/ways/serve.py::shadowed_by#no way drawn twice` (MISLABELED, E0): refusing a way that runs within 30 ft of another for more than 100 ft is a rule about where lanes run, not a drawing convention; should be GUESS or UNRESEARCHED
- `l7r/diagram/hamletgen/ways/street.py::row_reach#street run past its end farms` (CANNOT-TELL, E4): the 0033 drawing page says "The street runs on off the map as the road into it", which may answer or contradict a half-frame overrun; I need to see which end of the street the overrun is applied to
- `l7r/diagram/hamletgen/ways/web.py::_lay_skeleton#clear of crop, wet and water` (MISLABELED, E0): the 0081 and 0246 drawing pages answer the rule of keeping off crop and wet ground ("never crosses row crops", "keeps off wet ground"), so the claim should cite them with the 20 ft as a GUESS or CONVENTION; note §59 also lets a lane "touch a plot's boundary"
- `l7r/diagram/hamletgen/ways/web.py::stage_web#a web lane's span` (MISLABELED, E0): 0246 says a back lane "runs only along the houses it serves" (served = within 100 ft, §10), so the rule is answered; the claim should cite 0246 and reconcile the 1.5 x WEB_REACH_FT (150 ft) span with the 100 ft service reach
- `l7r/diagram/hamletgen/ways/web.py::stage_web#door path reach` (MISLABELED, E0): the 12 ft steading arrival is recorded on the 0246 drawing page as part of its GUESS ("within 12 ft of the steading's built ground"), so the claim should name that page (GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html); the 40 ft is not recorded there
- `l7r/diagram/hamletgen/ways/web.py::stage_web#web lanes off the hard ground` (MISLABELED, E0): 0246 ("a stretch that would cross the field, a crop, wet ground ... is cut out") and 0081 drawing answer the rule, so the claim should cite them with the 8 ft margin as a GUESS or CONVENTION
- `l7r/diagram/hamletgen/cluster.py::seat_cluster#band on the canvas` (CANNOT-TELL, E4): code keeps seat_c at least lat*0.5 from the frame; the band samples at t=±0.9*lat, which suggests lat is the half-length, so this would be a quarter of the length, not "half the band's length"; need band_extent's meaning of lat
- `l7r/diagram/hamletgen/cluster.py::seat_cluster#brook across the band` (DRIFTED, E2): 0035 makes the uncrossed site a tie-breaker ("otherwise equally good") and builds on both banks where the best wind-facing site is crossed; score -= 3.0*crossed outweighs the whole wind term (1.0) and the upslope term (0.8), so a crossed best site always loses; the penalty should only break near-ties
