# Future work: cross-cutting

**Things that are not about one kind of map**: the gate, the caches and the render pipeline, engine
module organization, and generation doctrine that applies at every tier.

The test for this file is simple - if fixing it would change maps of more than one type, or would
change no map at all (tooling, structure, checks), it belongs here.

## 2. Fabric-first generation (the GM's ordering question, 2026-08-10) - RESEARCH DIRECTION
Today's order is shell-first: wall/roads/water, then fabric fitted inside, with the wall
PRE-SIZED from a budget density constant. The constant was wrong once (Tango's 690 vs the
capital's as-built 1,367) and the failure mode was structural: fabric could not fit, overflow
silently went extramural. A fabric-first order - grow streets/quarters/temples roughly
radially, THEN wrap wall/moat/ring around the built hull - makes wall-sizing correct BY
CONSTRUCTION. Known hard parts (the GM named them): gate-anchored programs (guard houses,
inspection stations, caravan clusters) need the gates, so it becomes two-pass - grow fabric,
choose gates on the hull, then place gate programs and re-arrange locally; ring/moat must
wrap an irregular hull rather than an ellipse. This is a full feature with its own spec, not
a mid-feature pivot. Candidate: the city tier's conversion (the GM, 2026-10-07: the capital goes straight to
a scripted generator; Shiro Daika's hand pass is dropped).

Design inputs measured on Shiro Daika's hand-authored first pass (2026-08-10), the motivating example:
- **Wall-to-fabric fullness is the headline requirement** (GM 2026-08-10). After three wall derivations the
  interior slack check passed (claimed-open + unclaimed <= ~15% of the interior), yet the map still read empty: 41% of
  the walled interior had been claimed-open commons at the first derivation, and hours of fine adjustment were tuned
  against a wall about to be wrong. A grown fabric with the wall wrapped round it has the right slack by construction;
  a wall must never be adjusted after the fine work.
- **Realized machi density is bounded by the SERVICE fabric, not the packer**: streets, kido reserves, well courts and
  roji took ~8% of the packed ground at the settled wall. Budget service ground per district (wells per ~20
  households, roji per 95 px reach) BEFORE deriving the wall, or the same gap reappears.
- **Place service features and packs in one deterministic order per district**, so a local edit stays local: the
  hand pass's endgame was cross-coupled reflows, every well, claim or alley edit re-rolling neighboring packs (three
  "dead cores" moved five times).

## The push-time `roll-review` agent (deferred by feature 217, 2026-09-08)

**What it would be**: an independent Opus check on the perf-audit pattern (feature 129) that the push demands ONLY
when the delta adds a `Roll` or `Duplicate` row to `tests/rolls.py`. It is given the constitution VI clause, the diff,
and the census verdict's printout (the lines the new roll alone reaches) and answers one question: could these lines
be reached without a roll - by packing the assertion onto a roll already made, or as unit tests of the placer? Its
record is written only by the agent (`AS=roll-review`, honor-based like `perf-audit`; the bypass log records), and
`sync-with-main.sh` refuses the push without it.

**Why it is third in line** (the GM, 2026-09-08: *"I don't want to run a subagent check every single time we run our
unit tests"*): the rule and the two cheap layers act at zero token cost - the verdict fails a roll with no unique line,
the guard puts the doctrine in front of the session when it opens the roster, and the audit pointer makes the
justification an artifact. A row that passes the verdict has already proved it reaches lines nothing else does; what
the agent would add is an independent opinion on whether those lines could be unit tests, which is judgment the
session is told to exercise and the GM reads in the diff.

**When to build it**: if a village-tier feature lands rows that the GM, reading the diff, judges should have been unit
tests - that is the measurement that says the judgment layer is not holding.

## Lighting a watercourse paints over the things that CROSS it (measured 2026-09-12, feature 230)

MEASURED by the feature's fifth settlement-review pass with `make page-lit` on Inashiro's page:
lighting the irrigation ditch repaints 35.8% of the footbridge's ink and 29.5% of the weir's;
lighting the stream repaints 57.7% of the weir's. On the sheet the deck and the stone crib are drawn
OVER the water they cross, which is how a reader knows they are a crossing at all; on the page,
hovering the water puts the water back on top of them.

MECHANISM: below the raster scale the page is one image of the whole picture with every leaf outside
the lit class hidden, and the lit class redrawn as vector ABOVE the image (features 200, 201, 203).
The image carries the map's true draw order. The redraw carries none of it, so a lit stroke lands over
everything the image drew after it. It is not new with this feature - any footbridge over a stream has
behaved this way since raster mode shipped - but the weir is a new thing standing in the water, and it
is the worst case measured so far.

PRICED AND DECLINED ONCE ALREADY, which is why this is a note and not a fix: feature 201 met the same
problem for FILLED shapes (a lit paddy hiding its own bunds and beans), priced exact stacking at 223 ms
per hover and a mask at 300-1,100 ms, and shipped the 0.45 wash instead (`specs/201` research.md R2,
R3). The wash does nothing for a STROKE, which is opaque by design so a ditch reads as a ditch.

SKETCH, the same shape feature 228 took for the crop dike one level down - carry the ORDER, not the
geometry. At page-write time record per class which LATER leaves overlap it (`page.py`'s merge
machinery already computes exactly that overlap to decide its buckets), and in raster mode draw those
few leaves above the lit group in their own order. It is bounded by the overlap, so it is a handful of
elements per hover rather than feature 201's whole-class restacking - which is the reason to think the
223 ms figure does not transfer, and the first thing to measure if anyone picks this up. The
alternative, splitting the water stroke geometrically where a fixture crosses it, is cheaper on the
page and is REFUSED: it would change the SVG and the PNG, which spec 134 FR-010 forbids.

## MEASURE feature 274's write cap and line reads on the groups that run after it landed (owed by 274 FR-004)

Feature 274 capped a research WRITE session at four questions and ten new registry keys (the runner and
`make reserve`), and moved coordination files to `make lines` / `make append`. Neither can be measured before
groups run under it, so the measurement is owed here. **Method**: `specs/274-leaner-research-sessions/measure/`
- `collect.py` (edit its `CLONES` list to the clones that ran, and keep only sessions whose first record is after the
landing commit's time - it has no cut-off of its own) writes `sessions.json` from the transcripts listed in each
clone's `.git/page-sessions/index.txt`, folded per message id as 250's `tokens.py` folds them; `analyze.py` prints the per-group table in
the shape of `groups-table.txt`; `decomp.py` splits the main context into floor, reads and tool results. Take every
complete group started after the landing. **The figures to beat** (274's research R1, 282 sessions in 65 groups
before it): per thing checked a median of 1.02 M (IQR 0.86-1.20); the largest context of any turn 246 K; write
sessions a median of 74 turns (mean turn 147 K, peak 237 K); about 60 M carried by whole reads of coordination
files. **Expected**: write sessions under ~40 turns, the peak back inside 250's 102-171 K band, per-thing cost
10-20% lower, and coordination reads near zero - and `grep continued .git/page-sessions/run-*.log` says how often the
key cap split a session. A continuation brief sits at `.git/page-sessions/<sid>/continue.md`, which `collect.py`'s `specs/NNN-` match does not read: attribute it to its parent's group through the run log's `continued <sid> -> <sid>` line. Close this entry with the table and the verdict in 274's research.md as R3.

## Hamlet labels in the zoomed-out hit map (found by feature 267, 2026-09-27; unmeasured)

A small label's blended glyph edges can answer the hit map as the kind one palette step away. It is fixed for magistracy
pages only (`interactive/raster.py` `id_map(crisp_text=)`, used on a Mode A sheet's page; the hamlet pages are held
unchanged). Sketch: measure a hamlet page's hit map at the smallest label size first; if it misreads, pass `crisp_text`
there too and re-measure the page's size and build time.
