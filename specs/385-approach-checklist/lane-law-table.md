# The lane law, rule by rule (feature 385 T01, plan D1)

Every rule `law.LAW` names, and the per-lane rules `last_resort.lanes_breaking` asks, classed by what it describes. Read from
each predicate's `Research:` claim (2026-10-17, `l7r/diagram/hamletgen/ways/law.py`, `law_water.py`, `tails.py`, `checks.py`) and
the two lane drawing pages.

**Classes.** **R**: the research record (the question file named). **G**: a GM ruling. **O**: ours - a convention, a guess or
unresearched. A rule is often R in its principle and O in its numbers: 0081's drawing page says of every turn and distance limit,
*"chosen at the scale of a dozen paces, not measured"*.

**The principles the walking rules rest on** (0081, the findings page): *"A worn path usually takes the shortest or easiest way"*;
walkers prefer *"the fewest turns or the least change of angle"* (the London study); a lane never doubles back. The GM, 2026-10-17:
a path takes the natural route round what stands in its way, does not double back for nothing, and two paths running side by side
become one; lanes follow the houses (also 2026-10-02, and 0246).

**Verdicts.** *kept*: describes how people walk, or a fact of the map, everywhere it applies. *obstruction-aware*: describes open
ground only - a turn or meeting the mapped ground forces becomes lawful (plan D2). *merged*: two treads nearly along each other
over open ground become one path (plan D4).

## Bends and ends

| rule (`LAW` name) | predicate | what it describes | class | numbers | verdict |
|---|---|---|---|---|---|
| `bends` | `lanes_that_kink` (`clearance.kink_spans`) | a path takes one easy arc, not a zig and an immediate zag, and never doubles back | R 0081 (fewest turns, never doubling back); numbers O | 140 deg hairpin; two 50 deg turns within 40 ft | obstruction-aware: a zigzag or hairpin whose chord the ground blocks is walked round what stands there |
| `hooks` | `hooked_ends` (`hooked`) | an end does not curl back on itself in its last pace | R 0081 (no doubling back); numbers O | 12 ft leg, 90 deg | obstruction-aware: a hook round a corner that blocks the straight end is the walk to the door round it |
| `husks` | `husks` | a lane record that draws nothing | O (data hygiene, not a walker's behavior) | under 2 points or 1 ft | kept (no shape on the map; nothing to walk) |

## Where lanes meet

| rule | predicate | what it describes | class | numbers | verdict |
|---|---|---|---|---|---|
| `folded_joints` | `folded_joint_pairs` | two lanes met end to end are one path to the walker, so no hairpin at the joint | R 0081 ("Two lanes that meet end to end are read as one"); numbers O | 140 deg | obstruction-aware, as `bends` |
| `connector_hairpins` | `connector_hairpin_ends` | no hairpin where a lane meets the track out's start | R 0081; numbers O | a returning leg under 40 ft; 1.5 ft of the start | obstruction-aware, as `bends` |
| `needle_joins` | `needle_ends` | a lane meets another as a T, never a needle | R 0081 (the T); numbers O (`NEEDLE_DEG` and `NEEDLE_FT`: CONVENTION) | under 20 deg; a leg over 20 ft | obstruction-aware where the sliver between leg and tread holds mapped ground; **merged** where it is open grass (G 2026-10-17) |
| `shallow_crossings` (new) | `shallow_crossing_at` | two ways crossing at a needle's angle are one path wandering over the other | G 2026-10-17; the angle O (`NEEDLE_DEG`) | under 20 deg | **merged**: cut at the crossing, the end re-aimed as a T (plan D4; seed 10 under the wave 155 patch) |
| `doubled_tails` | `doubled_tails` (`tails.tail_doubled`) | a way drawn twice: an end running on beside another way | O (UNRESEARCHED: "no page we read covers a way drawn twice"); the merge is G 2026-10-17 | within 15 deg | kept, and is the merge's own cut (plan D4) |
| `needle_loops` | `needle_loops` | two ways laid round a sliver of ground too narrow to be anything | O; the merge is G 2026-10-17 | a face under `NEEDLE_LOOP_FT` mean width | kept (the settle opens or welds it); a sliver this narrow holds no house, so nothing forces it |
| `joins_short` | `near_misses` | ends that nearly meet are joined at one point | R 0081 ("Lane ends that nearly meet are joined"); numbers O | within 25 ft | kept |
| (the gate's `lane_knots`) | `knots.knots`, `knots.lane_knots` | three lanes do not arrive a few feet apart: ends that nearly meet are one junction | R 0081; numbers O | within 25 ft | obstruction-aware (plan D4b): two ends with fabric between them are two paths either side of a fence, not a knot |
| `width_steps` | `width_steps` | one way keeps one width | R 0081 | none | kept |
| `networks` | `lane_networks` | the lanes are one network | R 0246 | joined at 4 ft | kept |
| `fragments` | `short_fragments` | a scrap of lane that serves nothing | O (UNRESEARCHED: debris) | under 30 ft | kept (no walker wears a path to nothing) |

## Reach

| rule | predicate | what it describes | class | numbers | verdict |
|---|---|---|---|---|---|
| `dangling_ends` | `dangling_ends` | an end reaches something a reader can see | R 0246 (pulled back to the last house); numbers GUESS | 60 ft of a house, 12 ft of its built ground | kept |
| `doorstep_ends` | `doorstep_ends` | no fan of stubs at one door | O (UNRESEARCHED) | more than two free ends within 80 ft | kept (a fan of stubs is what the merge also prevents) |
| `field_unreached` | `field_unreached` | a way reaches the field on a brook map | R 0014 | none | kept |
| `unreached_houses` | `checks.unreached_houses` | every farmhouse reached (but those reached across a neighbor) | R 0246 | none | kept |
| `unreached_targets` | `unreached_targets` | a path runs to the graves | O (UNRESEARCHED) | 14 ft of the burial ground | kept |

## Fabric

| rule | predicate | what it describes | class | numbers | verdict |
|---|---|---|---|---|---|
| `over_fixtures` | `lanes_over_fixtures` | no tread through a building or fixture | R 0246 ("Nothing is built on a lane") | none | kept - this is the ground the obstruction test reads |
| `breaks_mid_run` | `breaks_mid_run` | no tread across another household's yard or bed | R 0246 | none | kept - likewise |

## Water

| rule | predicate | what it describes | class | numbers | verdict |
|---|---|---|---|---|---|
| `over_and_back` | `over_and_back` | a way does not cross the brook and back | R 0035 | none | kept |
| `off_ford` | `off_ford_crossings` | a lane crosses the brook at a ford | R (the ford pages); numbers O | `FORD_HALF` 30 ft | kept |
| `oblique_brook`, `oblique_channel` | `oblique_crossings` | a crossing is square to the water | R; numbers O | `FORD_SQUARE_TOL_DEG` | kept |
| `unbridged` | `unbridged_crossings` | every crossing decked | R 0087 | none | kept |
| `undeckable`, `short_decks` | `undeckable_crossings`, `short_decks` | a deck spans its water where one can stand | R 0087 | deck spans | kept |
| `planks` | `plank_faults` | planks on the supply ditches | R 0084 | none | kept |
| `way_outs` | `way_outs_crossing` | the ways out do not cross | R 0035 | none | kept |

## What changes

Six rules become obstruction-aware (`bends`, `hooks`, `folded_joints`, `connector_hairpins`, `needle_joins`, and the knot rule), and the needle over
open grass is merged by the settle's re-aim (`reaimed`), extended to a household's way's foot and to a shallow crossing (plan D4). Every other rule describes how people walk or a fact of the map, everywhere it
applies, and is kept. No rule is retired. No number changes value (plan D5).

## The ground that forces a turn (plan D2)

The settle's two obstacle families (`clearance.py`, the clear-stretch scan) and the fabric rules' ground, as one set: crop, marsh
and the wet toe (`obstacles`); houses, yards, gardens and groves (`tight`); fixtures (`fixture_quads`) and solid boxes
(`solid_boxes`). No kind the settle routes round is left out, so no shape the settle bends round something is refused for its
angle.
