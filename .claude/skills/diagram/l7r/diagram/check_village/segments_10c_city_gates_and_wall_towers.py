"""Gate segments (city gates and wall towers; keys 0563_078-0563_125) - bodies verbatim, registry order preserved."""


# a lane heading at a NEIGHBORHOOD wall (a ward fence) should reach it and end at a KIDO GATE - the
# commoners' lanes pull in to the gates they pass through to work in the samurai quarter. Stopping a
# sliver short, or meeting the fence with no gate, both read as a mistake. (Stopping short of the
# MAIN city wall is fine - that is the city's own edge, not a neighborhood boundary.)


# THE KIDO SQUARES TO WHAT IT BARS (GM 2026-07-26, refining the 2026-07-24 fence rule).
# A kido is a gate across a WAY: it is shut at night to stop traffic, so the roofed bar
# stands SQUARE ACROSS THE LANE that runs through it, and the fence meets the gate at
# whatever angle the fence happens to run. The two readings agree wherever a lane crosses
# its fence squarely - which is most crossings, and why the fence rule held up for two
# days - and diverge exactly where a lane meets the fence obliquely: Tango's SW ring-road
# gate, drawn on its ~44deg fence jog while the ring road passed at ~172deg, sat 38 degrees
# off square to the road it was supposedly barring and read as a glyph dropped on the
# roadbed. Only a gate with NO lane through it falls back to the fence tangent (still never
# an axis-aligned stamp on a slanted run - Nagahara's SW kido, Tango's S jog, both frozen
# in pool/regressions/). lane_through_gate/kido_bar_deg are the SAME functions s.ward
# places with, so placer and checker cannot drift. s.kido records the drawn angle as 'rot'
# (legacy manifests fall back to the horizontal flag: True -> 90, False -> 0); it must match
# within ~7 degrees mod 180.


# ... and the guard house + inspection station sit AT THE GATE THROAT - hard by the opening,
# flanking the road as it enters - not walked back along the wall. Historically decisive (see
# settlements.md 'Historical grounding'): an inspection/tax barrier only works where traffic
# is forced single-file, and the gate passage is that one chokepoint in the whole wall; set
# the station back along the wall and arrivals disperse into the streets before ever reaching
# it. So each must sit within ~70px of its gate vertex (the built placement lands ~35-45px in).
# The looser city_inspection_station_at_each_gate / city_gate_has_guardhouse radii (160/180)
# deliberately have SLACK for the barbican, and would wave through the old far placement that
# walked the pair 80/144px along the wall - THIS check is what gives that rule teeth.


# the gate's own (smaller) TOWER must sit AT its gate - the CLOSEST tower to the opening, not
# marooned out along the curtain with a mural bastion seated nearer (GM 2026-07-22: the S gate's
# tower had walked to arc 118 to dodge a ward-gate kido, reading as a random small tower
# mid-wall while a mamian sat at the gate). A gate tower is a gate_structs "tower"; every other
# wall_tower is a mamian. When one flank of the gate is blocked the tower takes the OTHER flank
# at the opening (city_wall does this), so it should never be out-distanced by a mural.


# a fortified city is TOWERED for enfilading fire along the wall face: guard towers spaced
# at regular intervals around the whole rampart (a bowshot apart), not only at the gates -
# so no long bare arc of wall sits uncovered. Spacing is judged by the widest angular gap
# between consecutive towers around the wall centroid.


# guard towers sit SQUARE to the wall (rotated to its tangent) rather than all axis-aligned -
# a tower on a slanted stretch slants with it. Each tower's recorded rotation must match the
# angle of the nearest wall edge (mod 90, since a square reads the same every 90 degrees).


# the GATE FURNITURE - the guard house + inspection station that sit along the ring road just
# inside each gate - is likewise SQUARE TO THE WALL: rotated to the wall's LOCAL tangent at its
# own position (NOT the gate vertex's - the wall has already curved away by then), so the ring
# road runs lengthwise through it. Each is a rectangle (its long axis runs ALONG the wall), so
# its rotation must match the nearest wall edge angle mod 180 (a 180 deg flip is the same, a 90
# deg turn would stand it the wrong way across the road). Tolerance is TIGHTER than the towers'
# (6 vs 15 deg): the furniture rotation is set from the exact local edge angle, not the towers'
# chord-through-neighbors approximation, so a correctly-placed piece matches near-exactly - and
# the gates sit on shallow wall stretches (~8 deg), which a 15 deg window would wave through.


# ... and the guard house + inspection station are SEPARATE buildings: walked along a
# tightly-curving wall the two arcs can converge, and an inspection annex drawn through
# its guard house reads as a collision (GM, 2026-07)


# WALL FURNITURE STAYS OUT OF THE MOAT: a guard tower straddles the wall and may PROJECT a
# stride past its outer face (the horse-face bastion), but its footing must stand on the
# BERM, never in the water - a tight moat gap leaves a narrow berm, so a tower centered on
# the wall line pokes its outer face into the bed. Same for the gate towers and the guard
# house / inspection station. (Bridges are exempt - they span the moat by design.)


# THE WARD GATES STAND CLEAR OF THE WALL TOWERS: a kido hangs on the ward fence where a
# lane or the ring road crosses it, and the fence ends abut the rampart - so the LAST
# kido can land against a mural tower's footprint (its guard box read as "a small square
# building" inside the tower - GM, 2026-07). Both are overlap-EXEMPT classes (each sits
# on its own wall), so no generic pass catches the pair. The kido cannot move (it gates
# a fixed crossing), so the TOWER yields - city_wall(tower_skip=[...]) relocates it to
# the neighboring wall vertex.


# a GATE TOWER (a gate's guard tower, or a mural tower) must not OVERLAP the gate's
# INSPECTION STATION or GUARD HOUSE (GM, 2026-07). The gate complex packs tight (guardhouse
# + inspection + tower + gateposts at each gate) and inspection stations are overlap-EXEMPT
# against the gate furniture, which had let a tower footprint STACK on the inspection post -
# each is a distinct building and they must sit CLEAR of one another, abutting not stacked.
