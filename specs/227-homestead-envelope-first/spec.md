# Feature 227 - the homestead's envelope first, and the placement page generated from the code

**Status**: IN PROGRESS 2026-09-12. AMENDED 2026-09-12 for the GM's fourth message - the tooling fix for the waiter that outlived its run (FR-009), the deferred lane-end defect fixed rather than deferred (FR-008, D11, D10 and D4 rewritten), a plate after every step that laid ink (FR-007), and the renders the acceptance depends on (FR-006). `spec-fidelity` round 1 CHANGES REQUIRED (three items), round 2 FAITHFUL; amended during implementation (the per-configuration fallback, D8, SC-1's measure) - re-reviewed from a fresh count per the GM's 2026-09-12 ruling: amendment round 1 CHANGES REQUIRED (the bound), round 2 FAITHFUL.
**Request**: [`request.md`](request.md). **Research**: [`research.md`](research.md) - R1 where a placer call's
positions come from today, R2 the after. **Predecessors**: 226 (the site boundary and the seats proposed from
it - the ground is asked once; this feature is the placer's search), 134/207 (the placement-stages page and its
notes as data), 162 (`make docs` - the Makefile explanation derived from the Makefile's own lines).

## Summary

FIVE things, over four of the GM's messages. The first two came from the feature-226 numbers; the last three from
their message of 2026-09-12 after they read the page and went looking for the maps - a tooling fix so that a wait on
a detached run cannot outlive the run (FR-009), the lane-end defect this feature had deferred, fixed test-first
(FR-008), and a plate after every step that put something on the map (FR-007). The first two: First, the placer: a call today judges 26 to 60
positions and 100 to 220 rectangles for one seat because it tests the HOUSE's box before the placer and the
WHOLE homestead inside it, walking a spiral of offsets and two 2 px slides with the full battery at each (R1; the slides themselves have no recorded reason - `research.md` R1, commit ed0e884e). The GM's
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
  into the stage docstrings it described. The homesteads
  stage's plate also draws the site boundary it was seated against (the chords, the outline rings, the corridors)
  over the map, since that boundary is the thing the GM asked about and no plate shows it. The page carries a
  short lede saying how it is generated and from what.
- **FR-007 A plate after every STEP that put something on the map** (the GM on the page, 2026-09-12: *"how much work
  would it be to show a new image for literally every stage at which it would be possible to render an image that has
  actual content? ... The very first image that we see has a stream, an irrigated ditch, dry cropfields, earthen bunds,
  field ponds, wet paddies, and a drainage ditch. That's an awful lot. And the algorithm walks us through the step by
  step seven part algorithm. So To what extent could we show what the map looks like after each of those parts?"*).
  Each step a stage declares gets its own plate, under its own prose, showing the map as it stood when that step
  finished and nothing later - so the field stage is seven pictures rather than one, and the homesteads stage shows
  the row appearing before the ranks. A step that drew nothing gets no plate and the page says in words that it
  measured or decided rather than drew: the GM named that case themselves (*"sometimes like the entire 'The bearing
  and the fall' phase There are literally no map visible features or changes"*). A step is watched by WRAPPING it for
  the duration of its stage - there is no moment between two of a stage's internal calls that the walk can reach from
  outside - and the plate is made after the stage from a copy wound back to where that step's ink ended; the wrap is
  undone on the way out, so no map is ever rolled through a patched engine. The two places the rewind is an
  approximation (a record rewritten in place later in the same stage, a deferred ground-cover group flushed at finish)
  are recorded at the code, and neither can show a feature from a LATER stage.
- **FR-008 The lane end rule reads what a walker arrives at, and the placer and the check read ONE body**
  (the GM, 2026-09-12: *"before you fix that, I would like you to fix the defect rather than deferring it. Presumably
  in a test driven development sort of way where we will know that it is fixed and that we will be unlikely to regress
  in the future"* - D11, deferred earlier in this feature and now fixed). `lanes_reach_something` asks that every
  internal lane end come within `WAY_END_REACH_FT` of another way, a farmhouse or the field, and it measures a
  farmhouse by its CENTER - so a straggler footpath clipped at the garden fence of the one steading it was drawn for
  read as a tread ending in grass. The rule gains a fourth clause at its own much tighter distance
  (`STEADING_ARRIVAL_FT`, derived from the clip's own margin and step): an end standing that near a steading's built
  ground - its house, byre, shed, threshing yard or garden - has ARRIVED there. Ground cover is not a destination: the
  grazing commons and the homestead groves are what the ground is, and an end that stops in them is the thing the rule
  exists to catch. The three 60 ft clauses are untouched, so the only ends this admits are ends at a dooryard. The
  clause lives in ONE body (`end_serves`) that the placer's trim and the gate's check both call. TWO callers that kept
  the loose default - 40 ft to a way, 90 ft to a house CENTER - ask the gate's bar now: the straggler pass's own trim,
  which is where the two shipped ends were accepted, and the LATE web tidy-up pass, which runs after the stragglers.
  The late pass takes the bar WITH A STATED EXCEPTION, because tightening it alone stranded a farmhouse (cohort seed
  39): a point that still comes within `WEB_REACH_FT` of a house no other way reaches counts as serving however far it
  is from anything else, measured to that house's center, which is what `farmhouses_reach_a_way` measures. The reason
  is an ordering of harms rather than a convenience - a dangling end is a blemish on the drawing, an unreached
  farmhouse breaks the map's own rule - and the set of such houses is computed per lane at that point, not assumed.
  The check gets a reader on EVERY shipped hamlet, off the committed manifests, not on the reference roll alone.
- **FR-009 A wait on a detached run checks that the run is still alive, and the tooling makes it so**
  (the GM, 2026-09-12: *"hooks which reject a command are a last resort, and it is far better to take a hook that does
  the wrong thing and then automatically convert it to a different command, which is the correct version of the
  command. For example, if you are waiting on output to appear somewhere, but not checking to see whether the process
  that is supposed to generate that output is still alive, then when possible, the hook should add the second proof of
  life check to what is being waited for"*, and *"simply telling you to set a watch properly next time is bad
  engineering practice because that's just another version of making you remember to do something"*). `no-poll-hooks.sh`
  ADDS the proof-of-life clause to a permitted file-watching wait that has none, naming the file the loop itself
  watches and asking the kernel - not a process pattern, which is the self-match trap the same guard exists for -
  whether anything still holds that file open and when it was last written; and a wait that ALREADY carries such a
  clause stops being refused as a busy-wait, which it was, measured on the shape the fix produces. The boundary the GM
  closed in feature 165 does not move: a liveness clause can only end a loop sooner, a condition must still read a
  real file, and a loop on a process or a network call is refused exactly as before.
- **FR-010 ...and the two guards the same conversation earned, because a rule in prose did not hold.** Both are
  `scripts/` changes, so they route DIRECT and owe no feature of their own; they are recorded here because this
  feature's own failures are what produced them.
  - **A review's findings do not reach the GM unfiltered.** Three of this feature's findings went up as judgment
    calls and came back as corrections: two rested on no project norm at all, one had been answered by a
    measurement nobody re-ran. The rule against that already existed in TWO places - the review agent's own
    output contract and constitution XII - and was disregarded anyway, which is the GM's whole point
    (*"If we already had a rule in two places and it was still disregarded, then it sounds like we need another
    process change ... you do a final subagent check on that writeup"*). So a `settlement-review`,
    `building-review` or `size-audit` dispatch ARMS a requirement and an `escalation-check` dispatch DISARMS it,
    and the turn may not close in between. The agent verifies each cited norm IN THE REPO, which is the part a
    session cannot do honestly about its own draft.
  - **A run still going must not be abandoned.** The mirror of the finished-run rule, and it happened while that
    rule was being relied on: a detached gate failed 58 s after a turn ended on "the gate is running" and sat
    unread for 52 minutes. The finished-run rule fires at the next PROMPT, which is the moment the damage is
    already done. The Stop hook now refuses a turn that would close over a live `make` in this session's clone,
    detected by CWD out of `/proc` rather than by a process pattern, once per run, with no token escape because a
    Stop payload carries no command to put one in.
- **FR-005 Re-plated automatically.** The page is regenerated by the same landing procedure that regenerates
  the pool's renders (`render-sync`, feature 187's fingerprint): when the engine content changed, main's copy is
  re-plated; a docstring edit re-plates it too (a docstring is content the page shows, so the fingerprint for the
  page hashes the stage modules' text, not their docstring-stripped AST). `make placement-stages` remains the
  by-hand route. The page stays generated, never committed.
- **FR-006 The GM accepts the page, with the maps in front of them.** The feature's last task is the GM's acceptance
  of the page in the clone, after rounds of their suggestions; the feature lands only then. The acceptance is offered
  only with the COMPLETE set of renders present: every map in the clone's pool carries its `.png` and its `.html`,
  checked rather than assumed. The GM asked for that in the same breath as the page (*"I don't seem to be able to see
  actual PNG and HTML versions of many of the maps ... I would be able to judge the things that you are asking me to
  judge If I was able to see more of the maps ... I'd like to look at it before giving my signoff"*), and the renders
  are gitignored artifacts that a killed or skipped run simply leaves missing - which is how two of them came to be
  absent when the GM went to look.

## Success criteria

- **SC-001** (FR-001, FR-002, FR-003) Rectangles tested per placer call at most nine (the union, then at most one box and one computed move's
  re-test per configuration) and no walk of positions - against 26-60 positions per call today (R1); rectangles judged per house under 80 on every pool
  hamlet (113-387 under feature 226); candidates per house no more than feature 226's on every map but the dike
  mosaic, where the pockets refuse most seats (R2 reports all three).
- **SC-002** (FR-001, FR-002) Every pool map seats its declared households on the first roll; the 48-map cohort passes with
  `households_seated` and `farmhouses_reach_a_way`; every homestead has its garden and the bed splits vary
  (R2's per-map distribution, no fewer split forms than before); the settlement-review judges the re-packed
  layouts.
- **SC-003** (FR-004) Every stage on the page declares its steps and every step's prose came from its docstring; the gate fails
  otherwise; the page is regenerated by the landing.
- **SC-005** (FR-005, FR-007) Every step that laid ink on the reference roll has its own plate on the page, in the stage's own order, and
  a step that laid none has none; the landing's re-plate cost and the page's size are measured and recorded (R5). The
  size is RECORDED, never a bar: a plate the GM asked for is not dropped to make the directory smaller.
- **SC-006** (FR-008) No lane end on any shipped hamlet reaches nothing, judged by the placer's own predicate over every committed
  manifest (the two that did - Kashikawa and Kuwabata - pass because the treads arrive at a garden, not because the
  bar moved); the arrival distance is tighter than the reach bar, proved by a test; the 48-seed cohort still passes.
- **SC-007** (FR-009, FR-010) The guard adds the liveness clause to every permitted file wait that lacks one, permits the shape that has
  one, and still refuses a process or network wait - each proved by a case in `scripts/test-no-poll-hooks.sh`.
- **SC-004** (FR-006) The GM's acceptance (T07), offered with every pool map's `.png` and `.html` present in the clone, listed.

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
- **D4 RESOLVED: a plate after every step that laid ink.** This decision first read *"plates per stage, none per
  step"*, on the GM's own doubt (*"I don't know whether it makes sense for there to even be images at every
  stage"*) and with the question left to them at acceptance. They answered it in the other direction on
  2026-09-12, having seen the page: *"how much work would it be to show a new image for literally every stage at
  which it would be possible to render an image that has actual content? ... I would really like to see that."* So
  FR-007 supersedes the per-stage-only form, a step that laid ink gets its own plate, and a step that laid none is
  explained in words - which is the other half of what they said (*"sometimes like the entire 'The bearing and the
  fall' phase There are literally no map visible features"*). The boundary overlay on the homesteads plate stays.
- **D5 Re-plated at landing, like the pool.** The page costs a roll of Inashiro and a plate for every stage and
  every step that drew - 37 of them, measured in R5 - so it is not regenerated on every edit; it is regenerated
  where the pool's renders are, by the fingerprint.
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
  and the gate test imports it. Every caller passes it now, and the CARVE-OUT THIS DECISION FIRST RECORDED IS
  REPLACED: it read that the late pass, which runs after `_serve_stragglers`, would NOT take the bar, because trimming
  to 60 ft there takes back the tail that was an outlying steading's only way and cohort seed 39 stranded a farmhouse
  the moment both were tightened together. The late pass takes the bar, and the stranding case is named instead of
  traded away - `keep`, the houses no other way comes within `WEB_REACH_FT` of, which a point may still serve at any
  distance (FR-008). The web's own lanes trim to the bar at DRAW time (`_lay_web_lane`), before the stragglers. The
  two ends that shipped were not skeleton arms at all, as this decision first supposed from their recorded role: they
  carry the role of the pass before them, and D11 has what they actually were.
- **D12 The plate's copy is taken inside the worker, which is what makes sixty plates affordable.** The walk held one
  deep copy of the part-built settlement per plate until it ended - the shape that took this process to 1.6 GB
  (feature 208) and that the OOM killer ended on 2026-09-12 (R4), and it would have been sixty copies rather than
  fourteen. The copy and the rewind happen in the plate worker now, so the peak is the pool's width; measured, 37
  plates cost less wall clock than 14 did (R5). It is recorded here because it is both the enabler of FR-007 and half
  the answer to the GM's *"Killed by what?"*.
- **D11 FIXED, and the mechanism was not what the deferral said it was.** The deferral recorded two straggler ends
  (Kashikawa 63 px from anything, Kuwabata 68, against the 60 px bar; main ships Sawada at 68) and named the mechanism
  as a clip cutting the far end off the network. Measured when the GM asked for the fix: it is the HOUSE end, and it
  is not in open ground at all. Kashikawa's stands 7.8 px from the garden of the one steading its path was drawn for,
  17 from a byre and 32 from the farmhouse's wall; Kuwabata's 6.9 px from a garden and 47 from a wall - the treads
  stop at the dooryard, which is where the clip leaves them (`clear_runs` cuts at the fabric margin, and the
  steading's own yard is in the obstacle set by design: *"the lane ends AT the yard, and the yard is private ground
  the household crosses on foot"*). What was wrong was the MEASUREMENT: a 46x28 ft farmhouse carries 27 ft of itself
  between its center and its front corner, so both the check and the trim overstated every distance by most of the
  slack the rule has. FR-008 is the fix. The first cut - read the footprint at the 60 ft bar - was tried and REJECTED
  the same afternoon by measurement: it passed the two stragglers and also let three of Inashiro's skeleton arms keep
  ends 56-60 ft from the nearest wall, which is a tread stopping in open ground, so arrival became its own clause at
  its own distance. The re-roll moved the maps, which the GM permits for a rule that holds (2026-09-08), and it
  LENGTHENED one Inashiro arm that now stops 8 px from a byre - a tread worn to the byre door, which the center
  reading had been trimming off.

## Review history

- **The amendment of 2026-09-12** (the GM's fourth message), reviewed from a fresh count per their ruling that the
  cap resets on a mid-implementation change: round 1 CHANGES REQUIRED - D4 still stated the per-stage-only plate
  decision the GM had just replaced, FR-008 claimed every caller asked the gate's bar when the late pass carries the
  `keep` exception and D10 still denied that pass took the bar at all, the renders had no requirement because the
  sweep had already produced them (*"a statement about today's disk, not a specification"*), and the Summary and
  Status described a feature half this size; two asides (SC-005's size must never become a reason to drop a plate the
  GM asked for, and the worker-side copy deserved a decision line - D12). All six applied. Round 2 FAITHFUL, with
  two asides taken here too: D5's plate count refreshed, and this entry.

- Round 1 (2026-09-12): CHANGES REQUIRED on three items - the GM's condition on the gardens ("as long as they are
  there and there's some variety") was quoted in D6 and carried by no requirement; the `Steps:` declaration was
  optional for every stage but homesteads while the GM asked for the algorithms at EACH stage; D4 resolved the
  GM's image doubt in one direction. Applied: FR-001/SC-002 carry the gardens and the split variety as a measured
  criterion; FR-004/SC-003 make the declaration mandatory on every stage; D4 puts both directions in the GM's hands.
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
