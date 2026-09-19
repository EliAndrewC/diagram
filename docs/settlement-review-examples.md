# Settlement review - the validated examples

Moved out of `.claude/agents/settlement-review.md` by feature 255 (2026-09-19), verbatim: the agent opens this file
when a finding of one of these kinds is in doubt, instead of carrying it in its context on every turn of every review.


*(Populated by the Subagent-check TDD procedure in `docs/spec-kit-and-reviews.md`: a rule is added
here in GENERAL form, run against the unfixed artifact, and only once it FIRES is the specific
instance recorded below. An example here means the rule demonstrably has teeth.)*

**Pixel-count rule for "X inside Y", 2026-08-26 - Inashiro (reference hamlet), feature 133 T12. RED
then GREEN, in two attempts.** The GM's complaint: scrub "growing out of the marshland in exactly the
same pattern" as outside it. Round 2 of the fix let every scrub family thin into the marsh over the
reeds' 46 px feather; the round-2 review measured the depth profile, found it the designed
complement of the reed ramp, and PASSED - and the GM, reloading the PNG, said *"it looks like it is
still overlapping!"* (pines and brush standing in the reeds along 1,600 px of the north seam). The
first rule tried - "answer the GM's question at fit zoom before measuring" - was run against that
same round-2 render and STILL PASSED it: the reviewer's downscaled view of a 2,600 px sheet does not
show what the GM sees at full size, so a vision-only rule has no teeth here. The rule that fired is
the manifest-free pixel count above: run against the round-2 render it returned needs-work on
**1,260 scrub bases on marsh-tinted ground inside the frame (2,584 on marsh ink), all within the
46 px band, at near-outside density for the first 20 px** - the audit's 0 violations overruled
because the audit encoded the author's own allowance. Round 3 (woody families hard-excluded, grass
alone grading in) passes the same count at 0 woody bases on bog-colored pixels.

**Traffic-siting rule, 2026-07-27 - Ubame (unwalled town), added in general form and run against the
unfixed map. RED then GREEN.** The GM's report was "the notice board in Ubame does not look
well-placed; I'd expect it to be in a higher-traffic area", with the observation that no mathematical
rule can say what counts as foot traffic - so the rule was written as a judgment check here rather
than as a gate check.

- **TRAFFIC SITING - the board at the quiet end (CAUGHT, error #1 of the run).** The kosatsuba stood
  at (1622,522): across the bridge, on the far bank of the valley stream from the entire town, ~120
  ft past the east end of the shop rows and ~400 ft from the magistracy's own gate. **8** structures
  within 250 ft, exactly **1** within 150, against **23** at the high street's busiest stretch. The
  agent named the mechanism as well as the fact: the gen walked four candidate rects taking the
  first that FIT, the first three failed, and it fell through to the eastern APPROACH - and the
  `assert` could not catch it because it only tested that SOME seat was found. Note what stayed
  green throughout: `kosatsuba_by_the_road` passes anywhere on a road, including the stretch past
  the last house, so the automated check is silent on the only thing the feature is for.
- **Why the map had drifted there, which is the transferable part.** The board's glyph is 11 px and
  fits almost anywhere; its CAPTION does not, and the busiest frontage is exactly where there is
  least room for one. A siter hunting ground big enough to hold both walks away from the traffic by
  construction. Fixed at the root: `place_kosatsuba` now scores the caption as part of the seat, so
  a seat whose caption fits outranks one whose caption does not, and among those the busiest wins.
  Ubame's board went from 8 structures within 250 ft to 16, on the frontage, gate green. **Expect
  this shape again** - any feature whose label is much larger than its glyph will drift toward empty
  ground, and the emptiness is the defect.

**Founding run, 2026-07-26 - Ubame (unwalled town), run against a map with two defects deliberately
re-planted and the full gate GREEN throughout.** Both planted defects were caught, and four more
were found that nobody had planted. Verified against the manifest afterward: three of the four held,
one did not.

- **GLYPH LEGIBILITY - the face (planted, CAUGHT).** A new refining-forge glyph read as a face: two
  saturated red hearth blocks mirrored about the vertical axis, a centered anvil below and between
  them, two roof posts standing up like ears. The agent named the trigger set exactly and correctly
  said to fix it in the engine glyph rather than on the one map, since every future iron town
  inherits it. *This is why the mirror rule is stated as a rule and not an example* - the same
  failure previously retired the tethered-oxen glyphs.
- **FORM - belt vs blob (planted, CAUGHT).** A communal windbreak drawn as a 295 x 325 ft round wood
  (aspect 0.86) in the middle of the built-up town, canopy lapping a flophouse roof. It passes
  `village_windbreak_embraces_cluster`, which tests *adjacency*, not shape. The agent also caught
  that the notes recorded this as already fixed while the gen still authored a near-circular polygon
  - a notes-vs-drawing inconsistency, which is its own finding.
- **CROSS-ARTIFACT - the road through the compound (unplanted, CONFIRMED).** The trunk road's north
  edge ran **18 px inside** the magistracy's south wall, 80 ft from the compound's own gate.
  `manors` is an `_OVERLAP_TARGET` - a thing others avoid - and never an `_OVERLAP_STRUCT`, so
  nothing in the gate ever tested a compound's own wall against a roadbed. Now the automated check
  `manor_walls_clear_of_ways`.
- **JURISDICTION - building on the neighbor's soil (unplanted, CONFIRMED).** Three farmstead kitchen
  gardens and two grazing commons reached up to **43 px past the drawn clan border**, while the
  map's own notes promised the cover was "kept west of the border." Now the automated check
  `structures_stay_on_their_side_of_a_border` (tested on the CENTER, so a compound standing its wall
  on the line stays legal).
- **ANNOTATION - a caption pierced by its own feature (unplanted, CONFIRMED).** Both monasteries'
  innermost torii was drawn through its own hall's caption box, reading as a smudge on the text.
- **A finding I wrongly dismissed, and the real lesson (corrected 2026-07-26 by round 2).** The
  founding run reported scrub drawn on the theater stage roof. I "verified" it against the manifest,
  found nothing, and recorded it as NOT REPRODUCED. **The agent was right and I was wrong.** Round 2
  found the ink and named its exact coordinates - three `#94A063` scrub circles inside the stage
  footprint - and the reason my check missed it is doubly instructive:
  - I queried `theater_stages`; the manifest key is **`theater_stage`**, singular. The lookup
    returned an empty list, the loop body never ran, my script printed nothing, and I read that
    silence as a zero. **A verification that never runs looks exactly like a verification that
    passes** - the same trap the checks themselves are written to avoid, committed while checking
    somebody else's work.
  - Even with the right key it would have failed, because **hinterland scrub is not recorded in the
    manifest at all**. No manifest audit can see it, which is precisely why an agent that reads
    PIXELS is not redundant with the gate.

  So the rule is NOT "distrust the reviewer." It is: **when a finding is about INK, verify it in the
  SVG, not the manifest** - confirm the key exists and the query returned rows before believing a
  negative result. A reviewer looking at pixels can see things the manifest structurally cannot
  record.

**The lesson the founding run teaches about scope**: every one of the six findings was invisible to
~300 green geometric checks, and none of them was a near-miss on a threshold. They were a glyph that
depicted the wrong thing, a shape the metric could not see, two features nobody had thought to
compare, and a caption collision. That is the residue, and it is what this agent is for.
