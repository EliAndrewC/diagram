# Feature 227 - the homestead's envelope first, and the placement page generated from the code

**Status**: IN PROGRESS 2026-09-12. `spec-fidelity` round 1 CHANGES REQUIRED (three items), round 2 FAITHFUL; amended during implementation (the per-configuration fallback, D8, SC-1's measure) - re-reviewed from a fresh count per the GM's 2026-09-12 ruling: amendment round 1 CHANGES REQUIRED (the bound), round 2 FAITHFUL.
**Request**: [`request.md`](request.md). **Research**: [`research.md`](research.md) - R1 where a placer call's
positions come from today, R2 the after. **Predecessors**: 226 (the site boundary and the seats proposed from
it - the ground is asked once; this feature is the placer's search), 134/207 (the placement-stages page and its
notes as data), 162 (`make docs` - the Makefile explanation derived from the Makefile's own lines).

## Summary

Two things the GM asked for on the feature-226 numbers. First, the placer: a call today judges 26 to 60
positions and 100 to 220 rectangles for one seat because it tests the HOUSE's box before the placer and the
WHOLE homestead inside it, walking a spiral of offsets and two 2 px slides with the full battery at each. The GM's
model is the right one: draw the rectangle the homestead will occupy, know there is space for it, and only then
decide what goes where inside it. Second, the placement walk-through page: generated from the code's own
documentation - the stage docstrings, the steps each stage declares, the roster - so it is always current, at the
granularity of the algorithm rather than one card per stage, re-plated automatically, and accepted by the GM as
the feature's last task after rounds of feedback in the clone.

## Functional requirements

- **FR-001 The envelope first.** A placer call for a nucleated homestead tests ONE rectangle before anything
  else: the homestead's ENVELOPE - the bounding box of the largest configuration the roll can take at that seat
  (the house at its rolled size, the threshing yard south of it, a garden on either side, a kura north when the
  household has one) - against the site boundary at the nine points the boundary asks (`_site_blocks_rect`) and
  against the placed boxes. Only when the envelope fits are the parts laid out INSIDE it - the garden side by the
  sun rules (fewest shaded beds, then the preference order), the beds, the kura - and the rules that read the parts
  asked ONCE at that spot: the eave gap to the nearest house, the wall rule against the paddy, the sun corridors.
  Where the union of every configuration is REFUSED - tight ground, the pockets between a dike mosaic's ponds -
  each configuration's own box (the garden on the left OR the right) is tested in turn - one rectangle each, plus
  the single re-test after FR-002's computed move - so a seat is at most nine rectangles (the union, then at most
  one box and one move per configuration) and never a walk. No spiral of offsets, no 2 px slide: a seat no configuration's
  box fits is refused and the proposer offers the next seat. Every homestead so seated still has its garden, and the bed split still varies (the GM: *"as long as
  they are there and there's some variety"*): R2 reports, per pool hamlet, the share of homesteads with a garden and
  the distribution of the bed splits (one bed, two flanking, stacked, side by side), and the feature reduces
  neither. The dispersed form (the town's and the village's bundle with its grove) keeps its path as it is.
- **FR-002 The seat is where the house will stand, computed once.** The front row's standoff from a site chain is
  the wall rule's distance (`HOUSE_PADDY_GAP_FT` + 1) plus the tilt allowance plus the reach of the homestead's CORE -
  the house, the yard south of it, the kura north - toward that chord along its normal (a paddy the yard faces gets
  the yard's depth; the garden's side is chosen later, so it is not counted), so the slide toward the paddy has
  nothing to do; and where the outline lies beyond the chord (a dike's bank, a pond's fringe) the seat is pushed ONCE
  along the normal by the outline's measured reach past the homestead's near edge plus a footpath's room (a seat two
  pixels off a dike's bank left no way a lane could pass, and the web stranded it) - the same computed move, against
  the ground (Kuwabata's dike heads seated nobody without it and the cluster drifted 112 px off its polder); the row and the lattice stand at the bundle pitch, so the slide along
  the neighbors has nothing to do. A configuration's box that overlaps exactly one placed box is moved ONCE by the
  measured overlap, away from that neighbor (the GM: *"measuring the distance to the neighbor and then moving
  however much the correct amount is"*) and tested once more - at most one computed move per configuration, four
  per seat; any other refusal offers the next seat. The ranks
  BEHIND the front row are proposed behind the standing houses - each round offers the seat one envelope's depth
  further from the field behind every house of the rank before it, in a brick pattern (the odd ranks behind the
  midpoints between neighbors), and only when a round seats nothing behind does the cluster grow ALONG the field
  (the seats a pitch beyond each end of the rank, and the brick's outer half-seats; the rescue rounds offer these
  first, before their cloud - cohort seed 25 seated 19 of 20 without them) - because a placer that takes the seat it is given needs seats that fit by
  construction, which a random cloud deduped to a lattice does not give it (D8). The front row's share of the
  quota follows the rolled cluster shape (D8). The rescue rounds keep the old cloud over a wider band, seeded a
  third of a pitch apart; the fifteen-ring spiral they ran goes with the spiral.
- **FR-003 Counted.** `meta.seat_search` keeps its counts; `positions` becomes the number of envelope tests, and a
  new `parts` counts the part layouts tried. R2 reports both per pool map beside R1's.
- **FR-004 The page is generated from the code.** `tools/placement_stages.py` writes the walk-through from the
  code's own documentation, never from a notes file: each stage's DOCSTRING is its explanation (the first
  paragraph its purpose, the rest the algorithm and its order), and EVERY stage in `STAGES` declares its STEPS -
  the functions that are its algorithm, in the order it calls them; a stage that genuinely is one algorithm
  declares that one function - in a `Steps:` section of that docstring, one dotted name per line; the generator
  imports each step and renders its docstring under the stage, so the homesteads stage shows the site boundary,
  the front row from the chains, the lattice, the envelope pre-test, the placer laying the parts inside the
  envelope, and the rescue rounds, each in its own words, and every other stage shows its own algorithm the same
  way. A stage without a docstring, a stage with no `Steps:` section, a step without a docstring, or a `Steps:`
  name that does not resolve FAILS `tests/tools/test_placement_stages.py` at the gate (`stage_web` has no
  docstring today; it gets one). `placement_stages_notes.json` is retired and its prose moved
  into the stage docstrings it described. Plates stay one per stage that lays ink, none per step; the homesteads
  stage's plate also draws the site boundary it was seated against (the chords, the outline rings, the corridors)
  over the map, since that boundary is the thing the GM asked about and no plate shows it. The page carries a
  short lede saying how it is generated and from what.
- **FR-005 Re-plated automatically.** The page is regenerated by the same landing procedure that regenerates
  the pool's renders (`render-sync`, feature 187's fingerprint): when the engine content changed, main's copy is
  re-plated; a docstring edit re-plates it too (a docstring is content the page shows, so the fingerprint for the
  page hashes the stage modules' text, not their docstring-stripped AST). `make placement-stages` remains the
  by-hand route. The page stays generated, never committed.
- **FR-006 The GM accepts the page.** The feature's last task is the GM's acceptance of the page in the clone,
  after rounds of their suggestions; the feature lands only then.

## Success criteria

- SC-1 Rectangles tested per placer call at most nine (the union, then at most one box and one computed move's
  re-test per configuration) and no walk of positions - against 26-60 positions per call today (R1); rectangles judged per house under 80 on every pool
  hamlet (113-387 under feature 226); candidates per house no more than feature 226's on every map but the dike
  mosaic, where the pockets refuse most seats (R2 reports all three).
- SC-2 Every pool map seats its declared households on the first roll; the 48-map cohort passes with
  `households_seated` and `farmhouses_reach_a_way`; every homestead has its garden and the bed splits vary
  (R2's per-map distribution, no fewer split forms than before); the settlement-review judges the re-packed
  layouts.
- SC-3 Every stage on the page declares its steps and every step's prose came from its docstring; the gate fails
  otherwise; the page is regenerated by the landing.
- SC-4 The GM's acceptance (T07).

## Decisions Recorded

- **D1 No spiral, no slide, by measurement.** R1: 70-85% of a call's positions are the spiral, mostly on calls
  that fail outright because the house fit where the homestead did not; the rest the two 2 px slides. The slide
  had no recorded reason (commit ed0e884e, "more map WIP"): it stepped because the stop is whichever of eight
  rules fires first, and stepping avoided computing the clearance to each. With the seat at its standoff and the
  pitch, neither has work; there are two computed moves and no walk (FR-002) - the neighbor overlap inside the
  placer, and the one push against the outline at proposal time where the buildable line lies beyond the crop's chord,
  cleared by a footpath's room - each measured and applied once.
- **D2 The envelope is built from the house the roll WILL take.** A first cut of 226's pre-test used the largest
  house and refused seats the placer could take with a smaller one; here the size is rolled before the seat is
  tested, not after, so the box tested is the box the homestead will occupy - the union of its configurations
  first, then (FR-001) each configuration's own - and the parts never need ground their box did not clear.
- **D3 Steps are declared in the docstring, not by a decorator.** The GM named "the documentation, the
  docstrings, the stages" as the source; a `Steps:` list in the stage's own docstring is readable in the file
  by a person and by the generator alike, and a name that stops resolving fails the gate.
- **D4 Plates per stage, none per step; the boundary drawn on the homesteads plate.** The GM: *"I don't know
  whether it makes sense for there to even be images at every stage."* A step is prose; a stage that lays ink
  keeps its plate; the one new picture is the boundary, because it is what this line of work is about and no
  plate shows it. How many plates the page carries - more, or fewer than one per ink-laying stage - is the GM's
  call at acceptance; this version keeps today's one-per-ink-stage set plus the boundary overlay.
- **D5 Re-plated at landing, like the pool.** The page costs a roll of Inashiro eighteen times with plates, so
  it is not regenerated on every edit; it is regenerated where the pool's renders are, by the fingerprint.
- **D6 Maps move; the packing is accepted.** The GM: *"I'm fine with the clusters packing looser. And I don't
  really have any particular preference about two bed garden proportions. as long as they are there and there's
  some variety."* No target for either; the review judges the invariants.
- **D7 The dispersed bundle keeps its path.** Only the nucleated placer is rewritten; the grove-carrying form is
  used by no pool hamlet today and is not measured here.
- **D8 The seats behind the front row come from the standing houses, and the row's share from the shape.** With
  no spiral to slide a seed into a fit, the random cloud deduped to a pitch lattice seated Kuwabata 14 of 16 and
  strung Inashiro along the paddy at a drawn aspect of 5.1 on a rolled crescent (the row filled every seat it was
  offered and "one rank's worth of the band" was the whole quota). So each round proposes, behind every standing
  house, the seat one envelope's depth further from the field - plus a 4 px gap and, where the ranks climb north
  away from the field, the sun corridor a yard owes to its south (cohort seed 8: at the bare depth every clear seat
  failed the parts' rules) - in a brick pattern; the seats a pitch beyond each end of the rank and the brick's outer
  half-seats are offered only in a round that seated nothing behind, so the cluster grows along the field only when
  its back is refused (offered every round they strung Inashiro's crescent to 5.0 and Mizuguchi's round to 4.9, the
  half-seats alone to 4.5), and the rescue rounds offer those along-the-field seats first, before their cloud; and the front row
  takes about sqrt(N x A) houses for a quota N and a rolled aspect band whose two ends sum to A - measured: the
  ranks stand an envelope's depth apart on an arc and the drawn aspect is read on the houses' own axis, so seven in
  Inashiro's row drew 1.66, ten drew 1.84 (crescent 1.9-4.2), six in Kuwabata's 1.71 (round 1.0-2.0). The knob
  binds within its band on the mosaic and just under it on the crescent and the elongated map; how far a rolled
  shape must bind is the GM's call at acceptance, the numbers being in R2.

- **D9 What the review's second pass changed, and what it did not.** Four of its findings were mechanical and are
  fixed: the notice board's frame test admitted a board up to 30 px OUTSIDE the view (Sawada's shipped 21 px above the
  sheet, undrawn) and now insets by the board's own footprint; the stage's re-seat loop ranked an anchored board by its
  distance to the anchor alone, where `place_kosatsuba` narrows to the anchor BAND and then takes the traffic - it
  reads that rule from the same constant now; the garden's side had gone to 0 of 82 west, because a box the ground has
  already cleared for every configuration leaves the fixed preference order deciding every time, so the doctrine's tier
  (the sunny south strip before the walls) is kept and the hand within it is positional; and the ranks were measured a
  step behind whoever stood in front, which compounds - each rank's DEPTH is now the row's own plus k steps, measured
  once from the seat. Two were measured and left: the cluster reads as "fragmented" only on a CENTER-to-center link,
  and this engine's own rule is that a gap verdict reads footprints - homestead to homestead the pool's median gap is
  4 to 31 px, so the fabric is continuous and the houses are apart by exactly the yards and gardens between them; and
  the board at an `entrance` seat reaches fewer households than the busiest stretch of the same lane BECAUSE that is
  what an entrance seat is, a declared knob with its own research (and the verification pass measured the board at or
  above the best seat its own anchor band offers on all four anchored maps). Two are the GM's at acceptance (T07):
  Kuwabata's cluster standing off its dike behind the bank, and the windbreak that cluster displaced.
- **D10 One bar for a lane's end, found by a re-packed cluster (Principle XIV).** `_trim_to_service` pulled a run's
  ends back to the last point within 40 ft of a way or 90 ft of a HOUSE, while the gate asks 60 ft of a way, a house
  or the field - so an end that fell in the 60-90 band was trimmed to a position the gate then failed, and the trim's
  own docstring still quoted the older pair. The drift had been there since the check was tightened and only bit when
  this feature's re-pack put two of Inashiro's skeleton arms at 81-97 ft. `WAY_END_REACH_FT` is the one constant now
  and the gate test imports it. It is passed by the caller that draws a way BEFORE anything serves the houses - the
  cluster's skeleton - and NOT by the late pass, which runs after `_serve_stragglers`: trimming to 60 ft there takes
  back the tail that was an outlying steading's only way, and cohort seed 39 stranded a farmhouse the moment both
  were tightened together. The web's own lanes trim to the bar at DRAW time (`_lay_web_lane`), which is before the
  stragglers and so carries no such risk - and that is where the dangling ends actually were: they carry the role of
  the pass before them, which is what made them read as skeleton arms.
- **D11 DEFERRED with its measurement: a straggler path that does not reach the way it was drawn to.** Two remain in
  the pool - Kashikawa at 63 px from anything and Kuwabata at 68, against the 60 px bar; main ships one of the same
  kind (Sawada, 68). The mechanism: `_serve_stragglers` routes from the house to a target ON the network and then
  clips the tread, so a clip that cuts the far end leaves a path that connects nothing - and because the stub is
  itself a lane, `farmhouses_reach_a_way` then passes on the house it was drawn for, which is the same "a web that
  does not join up is not a web" defect `_lay_web_lane`'s join rule exists for, at the straggler. The sketch: refuse
  to draw a straggler whose drawn tread ends further than `WAY_END_REACH_FT` from the network, and let the house go
  genuinely unserved so the driver's re-roll can move it. It is deferred rather than done because refusing those
  paths turns a cosmetic stub into a re-roll trigger, which wants its own cohort measurement; the gate does not see
  it because this rule is judged on the reference roll alone.

## Review history

- Round 1 (2026-09-12): CHANGES REQUIRED on three items - the GM's condition on the gardens ("as long as they are
  there and there's some variety") was quoted in D6 and carried by no requirement; the `Steps:` declaration was
  optional for every stage but homesteads while the GM asked for the algorithms at EACH stage; D4 resolved the
  GM's image doubt in one direction. Applied: FR-001/SC-2 carry the gardens and the split variety as a measured
  criterion; FR-004/SC-3 make the declaration mandatory on every stage; D4 puts both directions in the GM's hands.
  The dispersed-form boundary (D7) and the boundary overlay (D4) examined and passed.
- Round 2 (2026-09-12): FAITHFUL. Asides kept: D2's "never refuses what the parts could use" is looser than FR-001's
  both-sides envelope (narrowed at landing to the house-size point it is about); the notes' prose moves from data back
  into docstrings, which the gate key strips and FR-005's page fingerprint hashes.
- Amendment round 1 (2026-09-12, fresh count per the GM's ruling): the per-configuration fallback and D8 FAITHFUL;
  CHANGES REQUIRED on the bound - nine rectangles per seat (the union, then a box and a computed move's re-test per
  configuration), the move per configuration. Applied.
- Amendment round 2 (2026-09-12): FAITHFUL. Asides kept for the landing: FR-002/D8's "one envelope's depth" is that depth
  plus a 4 px gap and, where the ranks climb north, the yard's sun corridor; the count of configurations (four) is
  named in one place.
- Amended after the settlement-review's first pass (2026-09-12): FR-002 gained the ground push, the core's reach and
  the ends as the fallback (the review: Kuwabata's cluster 112 px off its polder with `front = 0`, its belt gone with
  it; measured on the way: the union's garden stood every front house a garden's width off a paddy beside it, and the
  ends offered in every round strung Inashiro to 5.0 and Mizuguchi to 4.9, the half-seats alone to 4.5). Re-reviewed from a
  fresh count: round 1 CHANGES REQUIRED on D1 and D8 still stating the replaced behavior (applied, with the rescue's
  along-the-field seats and the push's footpath room).
- Amendment round 2 after the review (2026-09-12): FAITHFUL - the footpath's room is part of the one move's amount, the
  rescue's ordering an ordering inside a path the spec already had. Asides kept: FR-002 names the room in prose where
  the code names `WEB_FABRIC_GAP * 2 + 6`; the proposer's push asks the boundary outside `meta.seat_search` (R2 says so).
