"""Gate segments (bridges and gate roads; keys 0334-0359) - bodies verbatim, registry order preserved."""


# THREE OF THIS FILE'S BRIDGE RULES WERE RETIRED (feature 158, 2026-08-29, GM: *"if our placement
# algorithm guarantees that a thing is correct, then I do not believe that there is value in running
# an automated check afterwards to ensure that that exact same thing is correct"*).
# `bridges_align_with_their_way` re-derived the way x water crossings from the SAME shared source
# `settlement.bridges()` places from - `city/bridges.py` says so in its own docstring - and then
# asked whether the deck it had just been handed sat on the crossing it had just been computed for:
# the same measure of the same fact. Its whole evidence was two decks a person placed BY HAND on
# Minami and Nagahara in July 2026, on maps no generator can produce; every deck `s.bridges()` has
# ever solved landed 0.0-1.0 px and 0.0-1.0 deg off its crossing. `bridges_seat_on_water` and
# `bridges_clear_of_houses` went with it - the first fired once, on Shiro Daika's hand-authored
# towpath plank, the second never fired anywhere at all. Their whole derivation subgraph
# (0334-0338, 0341-0344 here) went too, including the ways x waters double loop, which the gate had
# been running on every map to feed a single retired verdict.
#
# `bridges_span_their_water` was a candidate on the same measurement and was KEPT, deliberately: the
# recorded history in `hamletgen/ways.py` shows it catching the SCRIPTED placer four separate times
# on oblique crossings (a 7 px stream at 17 degrees, and three more), so its placer does not
# guarantee it - it is exactly the case Principle XIV's "the placer only does its best" describes.


# A WATERCOURSE PIERCES A RAMPART ONLY AT A WATER GATE (GM 2026-08-09). Nagahara's cargo
# canal anchored its east end to a moat vertex BY INDEX; a past ring re-derivation moved the
# vertex, the approach leg slid 40px off the shuimen gap, and the canal shipped running
# UNDER the wall - placement and the wall's gap had no shared source and nothing compared
# the crossing to the gate. The doctrine was already prose (inwall_drain_outfall: "never
# draw a ditch running through the city wall"); this makes it a check for every DRAWN
# canal/channel/stream against a closed rampart. Buried conduits (drawn=False) pierce
# nothing; the moat is the ring outside and never crosses.


# ---- feature 021: the capital housing layer -------------------------------------------
# FABRIC DECLARES ITS DISTRICTS (T003): once dwellings stand, the capital records which
# named district each pack filled - the districts are the rank-gradient check's ground
# truth and the reader's map of intent. The bare 020 state (no fabric) stays legal, so
# this is a declaration-existence rule on the HOUSED capital only ("a check that never
# RUNS looks exactly like a check that passes").


# RANK GRADES WITH DISTANCE FROM THE CASTLE (T004; research 021 item 1): the jokamachi
# law - senior walled yashiki nearest the castle, detached houses next, retainer
# terraces at the band edge. Footprint family: CLASSIFICATION (members assigned by
# center to the band district containing them) + an ordering on band MEAN distances;
# 12px slack absorbs band-boundary geometry. Bands without members are skipped, so a
# mid-build map stays legal.


# THE WALL SETTLES FIRST (GM process rule, 2026-08-10): fine iteration on a capital is
# forbidden until the interior's OPEN share is inside the band, because every fine
# adjustment is downstream of the wall and a wall re-derivation invalidates them all.
# Measured the day the rule was made: 41% of the walled interior stood as claimed-open
# commons after two wall sizings, and hours of junction/well/kido tuning had been spent
# against a rampart that was about to move. Claimed-open ground (commons of any role)
# inside the wall must stay under ~15% of the interior - beyond that, the wall is
# oversized for its fabric: RE-DERIVE RX/RY (citybudget) before touching anything else.


# SOVEREIGN PRECINCT INTERIORS (T017, research item 7): once a precinct reservation is
# DECLARED (M['precincts'], the 021 engine path), its head-house program must actually be
# drawn - >= 5 halls, every one fully inside the reserved rect (a dormitory overhanging the
# reservation is a pack-collision waiting to happen; the reserve is the contract).


# TERAMACHI BACKSTRIP stays LEAN (T019, research item 9, capitals only): the rim temples
# are part of the defensive belt, and the strip BEHIND each (between temple and rampart)
# is the temples' own back ground + the patrol strip - never packed housing. Monk houses
# are the temples' own and may stand there.


# THE FABRIC HITS THE BUDGET'S BAND TARGETS (T006): the 018 budget is the housing
# authority, so each band's drawn count lands on its dwelling_target - yashiki compounds
# and detached samurai houses by record count, terraces by their UNIT count (one roof,
# `units` households), packed rows by dwelling-kind buildings in the machi-family
# districts. Tolerance max(2, 5%) absorbs seat jitter without permitting a quietly-short
# band (the Minami sign-off lesson, applied at band granularity).


# A TERRACE IS A RANGE (T005): the record models ONE roof over several household cells;
# a single-cell "terrace" is a detached house miscoded, and would double-count against
# the band targets. Runs wherever the record appears.


# A JOSUI-IDO SITS ON THE BURIED MAIN (research 021 item 4): from the settling basin at
# the gate the mokuhi trunk mains run under the WAYS and the laterals under the roji -
# Edo branched its pipes under the tenement alleys to the josui-ido courts - so a
# cistern-well stands within the band (900 real ft of the terminus; the DISCLOSED
# calibrated liberty - Edo's mains ran kilometers, a young domain system serves its two
# gate-quarter blocks) and within 30px of some way. A dug draw-well (no kind) is untouched.


# THE KIDO MESH BARS THE MACHI MOUTHS (research 021 item 6): every street mouth into an
# in-wall machi district carries its night-barred kido. The mouths come from settlement.
# machi_mouths - the SAME source the placer reads - so placement and validation cannot
# disagree (the bridge_carried_ways doctrine).
# ...and the mesh is a KNOB, not a law (GM 2026-08-10): interior ward gates may be right
# for one city and wrong for the next, so meta(ward_gates=False) turns the whole doctrine
# off for a map that does not use them. It is an explicit declaration, never an absence -
# a map that simply forgot its kido still fails.


# EVERY GATE'S ROAD JOINS THE RING ROAD (GM 2026-08-09, the capital's side gates: both
# trunk-road polylines STARTED at the gate point on the wall, so the road reached the gate
# from outside while inside the gate opened onto 90 ft of bare ground 30px short of the
# ring - a door to nowhere, and invisible because no check watched gate-to-ring
# connectivity. A walled city's gate traffic distributes along the ring, so SOME way (the
# Imperial road, a trunk road, or a street) must pass the gate AND meet the ring - by a
# vertex near it or by crossing it outright.
