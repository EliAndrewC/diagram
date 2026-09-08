# Feature 218 - efficient overlap checks

**Status**: IMPLEMENTED 2026-09-08 (windbreak 7.27 s -> 0.50 s; hinterland 8.09 s -> 1.27 s, the shortfall against the one-second target reported in R3 with its reason; every pool map byte-identical; bookends -50.5%; `make done` green at 100%, 215 s on a FULL cold run - R4) - `spec-fidelity` FAITHFUL at round 2 of 5 (the reviewer's two asides recorded: FR-003's SVG is a hair beyond the manifest the GM's "Yes" named, and strictly stronger; a stage landing between the 50% floor and the one-second target is reported as a shortfall and the GM decides whether it earns a second pass). Round 1 required three changes, applied: the constitution clause is stated in the GM's terms (a prospective obligation on how a feature performs its checks) and no longer declares a fix-on-sight duty D5 would then decline (FR-005); the leave-it bar in the hinterland census is a NUMBER (FR-002, D5), and the commons scatter's disposition is reported either way; SC-002's target is the GM's own - a fraction of a second - with 50% only the reportable floor.
**Request**: [`request.md`](request.md). **Research**: [`research.md`](research.md) - the profiles before
and after, the census of per-candidate scans in the two stages, the timings the GM asked for.
**Predecessors**: 145 (the `RingIndex` and `boxed_rings`, which gave the ground-cover scatters their
indexes - the marsh scatter was left with one path still linear), 129 (the performance bookends),
216 (the gate at 3 rolls of 3 - the GM's own note on why `make done` may not get much faster).

## Summary

The GM asked whether the windbreak really needs seven seconds and whether that is an overlap check run
per tree against everything on the map. It is: `village_grove` tests every candidate clump position
against every edge of every crop polygon and every watercourse segment, linearly, in pure Python, and
the marsh scatter in the hinterland stage rebuilds its whole watercourse segment list for most of its
points. Both are the shape this engine's performance doctrine already names (`dev/performance.md`,
"a per-candidate scan of geometry that does not change during the scan"), and both stand beside code
that already does it right. This feature makes the two stages do what the GM proposed - build the
outline of the blocked ground ONCE, then place each tree with a cheap test - with byte-identical maps
as the proof that nothing moved; it records the timings the GM asked for; and it writes the practice
into the guidelines and the constitution, so a larger map is laid out this way from the start. The
field stage is NOT in scope (the GM: *"limit ourselves to only the forests for now"*, then *"both the
windbreak and the hinterland"*); its cost is a different shape and is recorded in the research for a
later feature. No new subagent check (the GM: *"I do not believe that it is appropriate at this time"*);
the future review is recorded as a declined-for-now option.

## Functional requirements

- **FR-001 The windbreak's blocked ground is built once.** In `village_grove`
  (`settlement/homestead_parts/stands.py`), every test a candidate clump makes against geometry that
  does not change during the fill - the crop polygons and dry plots (inside, or within the crop margin
  of an edge), the dike outlines, the watercourses, the lanes and roads, the grove's own outline, and
  the occupancy circles (houses, yards, wells, shrines, ponds, the other grove's clumps) - is answered
  from an index built ONCE before the grid is walked (`boxed_rings` + `boxed_grid` for rings,
  `boxed_segs` + `boxed_grid` for polylines, `RingIndex` for the outline, a `PointGrid` of circles for
  the occupancy list), and never by walking the whole registry per candidate. The re-seat search
  (`_reseat`) asks the same indexes. The exact tests still DECIDE: every verdict is identical to the
  linear scan's, so every recorded clump is where it was.
- **FR-002 The hinterland's scatters ask a pre-built index for every static keep-out.** The marsh
  scatter's watercourse test (`settlement/land/wet.py` `_sparse` -> `_on_watercourse`) reads a
  pre-boxed grid for EVERY mark type - one grid per distinct pad, built once per marsh - so
  `_watercourse_segs` (and the taper split inside it) is never rebuilt per point. The rest of the
  hinterland stage (the commons scatter, the open-ground parcels, `_on_watercourse`'s other callers)
  is CENSUSED for the same shape, against a stated bar: each per-candidate scan of static geometry
  whose cumulative time on the seed-4 cProfile of its stage (`make perf-profile SEED=4 STAGE=hinterland`)
  is 0.10 s or more is converted the same way; one below 0.10 s is listed in research R2 with its
  measured share and left, because a conversion that buys nothing is churn. The commons scrub scatter
  - the GM's *"grass strokes and scrub pines and such"* - is reported in R2 either way: converted, or
  listed with its measured share and the reason. Verdicts identical, as FR-001.
- **FR-003 Byte-identical maps are the PROOF, no longer the requirement.** As specified and reviewed,
  every live pool map was to regenerate byte-identical (manifest, SVG) with the two stages converted -
  `dev/performance.md`'s own rule for this shape: an index that only prunes is output-preserving by
  construction, so any drift is a soundness bug. Mid-implementation the GM relaxed it (request.md, the
  two closing messages): *"It is absolutely not required that the changes that we are making here
  result in bite identical output ... as long as they still follow our general rules, and the maps end
  up looking more or less the same"*, and further speed *"at the cost of having the maps look a little
  bit different"* is acceptable *"so long as nothing ends up overlapping, which isn't supposed to
  overlap"*. Every conversion this feature ships is an exact index and DID regenerate byte-identical
  (research R3), so the stronger proof is reported and no map review is owed; a later, map-changing
  lever (D6) starts from the GM's relaxation rather than from this clause.
- **FR-004 The timings the GM asked for are recorded.** (a) The stage profile of the reference hamlet
  (seed 4) before and after, per stage, and the from-scratch wall clock of one roll with every output
  (SVG, PNG, HTML) - research R1 and R3. (b) The feature's performance bookends (`make perf
  LABEL=218-start` on unmodified code, `218-end` before the push; the per-seed and total change).
  (c) The time of a green `make done` after the change, beside the last recorded one before it, with
  the GM's own caveat that the gate rolls 3 maps and may not move much - research R4. (d) A
  windbreak or hinterland stage that does not get materially faster is a finding to report, not a
  reason to widen the scope.
- **FR-005 The practice becomes doctrine.** The constitution's Principle X (Python Discipline) gains a
  clause, in the GM's words where they are quotable, as a PROSPECTIVE obligation on how a feature
  performs its checks: every feature that involves overlapping or overlap checking within a map or
  diagram - any test of a candidate against features already on the map - performs the efficient
  version of that check, so that tens of seconds are not spent on what a fraction of a second can do:
  the geometry that does not change during the scan is built into an index ONCE (a bounding-box
  prefilter, a grid, a ring index, an outline of the blocked ground) and each candidate asks the
  index, and *"We do not have literally every item on the map checking for overlap with literally
  every other item"* - a rule that matters more as the maps get larger. The clause governs new code
  and code a profile shows costing time (this feature's two cases are its exemplars); it does not
  declare a retroactive fix-everything duty, which is why D5 can stand beside it. A MINOR amendment
  (2.24.0). The root `CLAUDE.md` (the verification
  bullets), the skill's `CLAUDE.md` (the existing "INDEX it - do not coarsen it" line gains the
  build-once form and this feature's measurement) and `dev/performance.md` (a third shape: the index
  that exists and is not used) carry the rule and its date. The `plan-template.md` Constitution Check
  gains the question, so a plan that adds an overlap check answers how it is indexed before tasks are
  generated. The `.claude/agents/` tree gains NOTHING; the possible future subagent review of
  overlap-checking code is recorded in Decisions Recorded as declined for now, with the GM's words.
- **FR-006 Tests, under the floor.** Any helper lifted out of the two closures to build or query an
  index is a module-level function tested with plain lists and tuples (feature 146's doctrine); the
  conversions are covered at 100% by the gate's existing rolls plus those unit tests; a test proves the
  index verdicts equal the linear scan's on a synthetic layout that exercises every keep-out class
  (crop edge inside the pad, watercourse within reach, a clump on the outline's rim, an occupancy
  circle).

## Success criteria

- **SC-001** Every live pool map regenerates byte-identical after the change (`make maps` over the
  tier, `git status` clean on `pool/`).
- **SC-002** On the reference hamlet's seed 4 stage profile, `stage_windbreak` and `stage_hinterland`
  each take UNDER ONE SECOND - the GM's own target (*"a fraction of a second rather than the many
  seconds that we are spending now"*). A fall of more than half is only the reportable FLOOR: a stage
  that lands between the floor and the target is reported to the GM as a shortfall against their
  words (FR-004 d), never recorded as a pass. The numbers are recorded, whatever they are.
- **SC-003** `make done` green at 100% on both floors; the bookends recorded; the gate's time recorded
  beside its predecessor.
- **SC-004** The constitution carries the clause at 2.24.0; the three guidance files and the plan
  template carry the rule.

## Decisions Recorded

- **D1 - index, do not redesign.** The GM's proposal - draw the outline first, then only keep trees
  off one another - is what the code already does in structure: the grove's footprint is an oversized
  outline that the keep-outs carve, and the trees never test against each other (a dense belt overlaps
  its clumps on purpose). What was wrong was the carving: per candidate, against every edge. Building
  the carved outline once as indexes over the same keep-outs is the GM's proposal made literal, keeps
  every ruling the placer encodes (the sun corridors, the re-seat around a local obstacle, the belt
  gap fill), and is provably output-preserving. A shapely union of the blocked ground would also work
  and was not chosen: it changes the geometry at polygon-boolean precision, so byte-identity could not
  be the oracle, and the engine's index family already exists for exactly this use.
- **D2 - the field stays out.** The GM excluded it and the profile agrees: `stage_field`'s time is in
  closing the comb's seams (about 540,000 small shapely calls), an algorithmic cost with no redundant
  scan to remove. Recorded in research R2 as the next candidate, with its profile.
- **D3 - a constitution clause, not only a CLAUDE.md line.** The GM: *"our project guidelines and
  perhaps even our spec kit constitution is upgraded"*. A rule about how engine code is written belongs
  in Principle X beside the file-size and closure clauses, and a new obligation is MINOR by the
  versioning policy.
- **D4 - no subagent now; the future one recorded.** The GM ruled it out for this feature and named
  the shape of a later one: *"any code which involves overlaps or overlap checking gets reviewed by a
  subagent"*. Recorded here so a later feature starts from the GM's words rather than from a session's
  guess; nothing under `.claude/agents/` changes.
- **D6 - the map-changing levers are recorded, not taken.** With byte-identity relaxed (FR-003), the
  hinterland's remaining time is the commons scatter's own work per glyph in Python - a random draw
  per throw, the outline test, one cell read, the feather distance, then the tuft's three blades and
  their SVG text - not any per-candidate scan (research R2: three quarters of the throws are ACCEPTED
  and drawn, so there is little waste left to remove). The levers that would cut it further all change
  what a map draws: fewer marks per acre (a density the research set), or a vectorized scatter (every
  throw tested at once through numpy/shapely, the SVG assembled in bulk). Both are recorded in R2 with
  their estimated gain as the next feature's starting point; neither is taken here, because each
  changes every hamlet's ground cover and so owes a settlement-review pass over the pool that this
  feature's exact conversions do not, and the spec the GM approved bounds this feature to the
  efficient CHECK. The GM decides whether the shortfall against the one-second target (SC-002) earns
  that pass.
- **D5 - a scan under the bar is listed, not converted; the bar is 0.10 s.** The census (FR-002) will
  find linear scans in code the profile barely reaches (the woodland placer tests every crop polygon
  per tree and its whole stage runs in 0.01 s). Converting one below 0.10 s of profiled cumulative
  time is churn with a nonzero regression risk and no gain a reader could measure; the doctrine
  (FR-005) governs NEW code and code a profile shows costing time, and says so. Each is listed with
  its measured share so the next reader knows it was seen and can convert it the day it grows.
