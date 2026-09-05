# Fields: the research behind the paddy, plot and crop rules

*The research behind the rules in [`../settlements/fields.md`](../settlements/fields.md). Findings, anchors and disclosed departures live here so the rule file stays operational; this file is where citations and deeper historical context get added as they accumulate.*

**Load this file when:** you are changing a field rule, a plot size, a crop ratio or a check threshold - or you want the historical basis before overriding one. Not needed to simply DRAW a field from the rules file.

Every entry: what the research found, the decision it drove, and any deliberate departure from literal reality. Anchors are stable - rules link to them by `#slug`.

---

## In-field features - flat flooded paddy hosts obstacles least

**Grounds:** `paddy_features_match_archetype`, `field_ponds_on_low_ground`

**Evidence:** corroborated, liberty

**Sources:** the per-archetype matrix rests on the 2026-07 pass (feng-shui grave siting, terrace outcrops) - not re-sourced on 2026-08-28; the grave-island liberty is the GM's (2026-07-20) - leftover

- *What the research found.* Flat, flooded valley-bottom paddy is the archetype that hosts non-rice obstacles LEAST - it is the most valuable, most intensively worked, and wet. Grave mounds and feng-shui knolls are MARGIN/slope features in the rice south (feng-shui wants a backing hill + downslope water view, so the dead go on the slope, not the wet center); rock outcrops are a TERRACE feature (bedrock the risers wrap around) and are absent on alluvial valley/polder and delta dike-pond; small OPEN-WATER ponds (a low pocket / header tameike / half-moon by a hall) are the one thing that genuinely belongs in the wet middle. The per-archetype matrix (research.md) is encoded in `_PADDY_POND_KINDS` / `_PADDY_ROCK_KINDS` / `_PADDY_GRAVE_KINDS` and enforced by `paddy_features_match_archetype`.

- *CALIBRATED LIBERTY (GM 2026-07-20, disclosed).* The in-field grave ISLAND (the "graves among the paddy" look) is a north-China-dry-plain / Japanese-corroborated signature, NOT the rice-south default (which is margin/slope). The GM approved "both", so it is drawn rarely (~30% on valley/terraces/ribbon) as a deliberate departure, recorded here and in research.md D1, not an oversight.

## Paddy plots - irregular patchwork, and why the grid is anachronistic

**Grounds:** `_paddy_plots`, the `plot` grain

**Evidence:** attested

**Sources:** `kochi-seiri-jawiki` (READ: the grid is Meiji consolidation), `nougyoudoboku-keihan` (READ: the standard bund), `aze-standard` (the earlier key). Azenuri timing and the 2-5 ft azemichi not re-read - leftover

Pre-modern paddies were fitted to the land and water by piecemeal reclamation and inheritance, so plots are odd-sized and odd-shaped with bunds meeting at **T-junctions**; the tidy rectangular grid is a **modern (Meiji/Showa) land-consolidation (*kochi seiri*) artifact** and reads as anachronistic.

What the research found: what separated real paddies was the *aze* (China: *tiangeng*) - a puddled-mud ridge roughly 1-2 ft wide and ~1 ft high, re-plastered each spring (*azenuri*) so each basin holds its shallow sheet of water (how deep, and the drained stages between, in 'How deep the water actually stands' below); the walking bunds (*azemichi*) ran ~2-5 ft.

### Bunds are SHARED, and the fabric is continuous

**Grounds:** `paddy_plot_seams_shared`; `waterfields/seams.py::close_seams`

**Evidence:** follows from the *aze*'s construction and maintenance, above

*What the research found.* The *aze* is the wall BETWEEN two basins, and it is built once. Three
things make a second, parallel ridge with a strip of ground between it and the first impossible in
practice. It doubles the *azenuri* - the spring re-plastering, the single largest maintenance job
the bund network carries - for no gain. It holds no water: neither basin's rim is improved by a
wall standing off in the middle of a strip. And the strip itself is idle land inside an irrigated
command area, which is the most valuable ground on the map - the same land hunger that keeps field
margins down to one scythe swath (`research/vegetation.md`) does not tolerate a few feet of bare
mud between two paddies. What real paddy fabric looks like is therefore ONE connected bund network
whose lines meet at **T-junctions**; a free-standing four-sided ring inside it is not a paddy at
all. The odd, piecemeal parcels that fabric produces are the honest look - and note that the
detached, individually-walled rectangle is exactly the *kochi seiri* read this section already
flags as anachronistic, arrived at from the other direction.

*The decision it drove (GM 2026-08-17, on Inashiro:* "a tiny little standalone rectangle of earthen
walls is just smack dab in the middle of where the field should be ... it should basically always
be the case that two adjacent rice paddies share a single earthen wall rather than two different
earthen walls"*).* Two halves. **Generation**: `waterfields/seams.py::close_seams` replaced the
wedge filler. It takes the bare ground exactly as the carve left it - the command area, minus
everything planted, minus the drawn channels and their banks - then PLANTS every pocket wide enough
to hold a basin (so the new basin's outline IS the surrounding bunds) and ABSORBS every pocket too
thin to plant into the neighbor it shares the most bund with (so the two walls become one). Its
postcondition is that no square foot inside the command area is bare. **Checking**:
`paddy_plot_seams_shared` fails a plot that runs a bund alongside a neighbor's across dry floor,
or that draws a whole ring inside a neighboring basin.

*Disclosed departures.* (1) A **shallow lap** is left alone, in both halves: a plot drawn over part
of its neighbor paints out the bund it covers, so the pair still reads as one shared wall. Only
near-containment is a fault. (2) The rule's upper bound is 24 real ft of gap - wider than that the
ground between two basins is bare FLOOR, which is `paddy_fan_gapless`'s rule, and stating it twice
at two tolerances is how checks start disagreeing. (3) A pocket **too thin to bund** is absorbed
rather than planted, matching the fan toe's existing thickness rule (`_TOE_MIN_THICKNESS`) - a
needle basin cannot be leveled or bunded at any sane cost.

### A bund runs on, or it turns for a reason - it does not step sideways and carry on

**Grounds:** `waterfields/banks.py::jog_steps`; `waterfields/seams.py::_seam_cuts`, `_unjog`; `tools/jogs.py`

**Evidence:** follows from the *aze*'s construction and maintenance, above; the *kochi seiri* framing at the head of this section

*What the research found.* Nothing new about the *aze* - this is the shared-bund finding read one
step further, and it is worth writing down separately because the two rules pull in opposite
directions and a reader who has only one of them will break the other. The section above says real
paddy fabric is odd-shaped and piecemeal, and the section head says STRAIGHT rectangular plots are
the modern land-consolidation artifact: **the organic waver is period-correct and must not be
cleaned up.** What that permits is a bund that BENDS, a basin that is a trapezoid, and a wall that
runs out at a T-junction. What it does not permit, and what nothing in the record produces, is a
wall that runs, hops a few feet SIDEWAYS, and carries on parallel to itself.

Three reasons, all of them the *aze*'s own economics. The bill for a bund is its LENGTH, since
*azenuri* is re-plastering along it every spring; a jog buys the extra run between two corners for
nothing. Corners are the part of a puddled ridge that slumps and so the part that is re-plastered
hardest, and a jog buys two of them. And the ground the jog trades is worth nothing to either
party: it sits at the same level, floods from the same offtake and is reachable from either basin,
so no farmer pays a wall's maintenance to move a boundary a few feet sideways along its own line.
Where a real parcel boundary DOES step there is a thing at the corner - a ditch, a path, a rock, an
inherited holding - and at the scale these maps are drawn we draw those things, so a step with
nothing at its corner is not a boundary at all.

*The decision it drove (GM 2026-08-18, on Inashiro:* "the earthen wall is kind of going in a
southward direction, and then instead of just continuing on and meeting at the four way
intersection between the north south earthen walls and the east west earthen walls, it just goes
sharply to the left before going down, thus making these extremely irregular shapes. This really,
really looks like a rendering error"*).* Measured, it was one: snapshotting `close_seams`'s input
and output gives **0 steps on the 543 carved rings and 26 on the 634 it hands back**, and every
frozen pre-`close_seams` fixture in `pool/regressions/` scores 0.

**THE MECHANISM, which is a pitch nothing else on the map uses.** A thin residual strip between two
carved rows is one connected scrap. `_plant` used to grid a pocket from the POCKET'S OWN bounding
box at `plot_across` - 48 ft on a hamlet - and that is a position at which NEITHER row breaks, so
every offcut it handed back landed mid-basin on both sides. `_absorb` then welded them alternately
into the row above and the row below, and the wall between the rows came out a staircase.

**Generation, in three parts, and the first is the one that matters** (counts are steps at the
rule's own thresholds across the four scripted hamlets, 26/37/20/24 before):

- `_seam_cuts` - **cut a pocket where the fabric already breaks.** A pocket's outline IS the
  surrounding basins' outline, so its corners are where the rows either side of it end; cutting
  there means an offcut lines up with the basin it will be welded into. The even spacing still
  governs and a neighbor's corner only wins within 0.35 of a cell of it, which is a MEASURED
  ceiling: at 0.40 the cut follows the neighbors far enough to move the fan's envelope, and
  Kashikawa's dry hem - tiled against that envelope - shifts onto a footbridge.
- `_absorb`'s **jog guard** - refuse a weld that adds a step to its host, ranked in the same ladder
  that already refuses a needle or a lump. Alone it takes 26/37/20/24 to 23/33/17/16: it can only
  CHOOSE a host, and the steps that survive it are the ones where the ground had only one home.
- `_unjog` - **repair what neither could avoid**, by trading the corner between the two basins that
  share the wall so the hop becomes a bend, or by flattening a whole tab so the wall runs on
  straight. Its refusals are the rules it would otherwise break, each measured breaking one; they
  are listed at the function.

Together: **0 / 1 / 5 / 1 steps**, and - the number that answers the report - **no plot ring on any
of the four carries more than one step**, against 6 / 9 / 4 / 7 rings that did. The staircase is
gone; what is left is single, small, isolated corners. `tools/jogs.py` reports them on demand and
[`future-work/farming-communities.md`](../future-work/farming-communities.md) carries the residue.

*Disclosed departures.* (1) The rule is DIRECTED - it compares headings over the full circle, not
modulo 180 degrees - because a plain thin rectangle is two parallel runs a short link apart, and
modulo 180 every narrow basin the fabric legitimately carries fires on its own end wall (78 hits
against 28 on Inashiro). (2) The hop must turn HARD at both ends, 55 degrees or more, or a gently
CURVING bund sampled into segments fires all along it - Kuwabata's long curved parcels reported 57
steps on 43 rings without that clause and 0 with it, Enokida 106 on 188. (3) A hop longer than the
link cap is not judged at all: past that the offset is a LIMB and the parcel is an L, which is
exactly the honest odd shape this file describes.

### A basin never tapers to a point - the fan toe truncates

*GM ruling 2026-08-17, closing the fan-toe SUNBURST that the backlog (now
[`future-work/closed.md`](../future-work/closed.md)) had carried as an open
question. The question was posed honestly - "a real cascade fan does narrow to its outfall, and the
honest question is whether this narrows too tidily" - and the GM's standard was simply realism.*

**The shape is authentic; the angles were not.** Two things had to be separated before anything
could be fixed, because a rule that got them backwards would have destroyed something real:

- **Radial convergence at the outfall is real** and is not a defect. An alluvial cascade fan
  genuinely narrows toward its collector, and the bunds of the basins on it converge with it. Any
  rule that flattened that would be making the map *less* faithful.
- **Narrowness is real too.** The strips at Shiroyone Senmaida and in the Philippine Cordilleras
  are genuinely a few feet wide and worked by hand. So the rule is deliberately **NOT** a minimum
  plot width - that would have been the obvious rule and it would have been wrong.
- **What no real basin does is taper to ZERO.** A paddy is a *level, bunded, puddled* unit holding
  standing water at an even depth. The arithmetic is the whole argument: at a 7.5 degree apex a
  plot is **5 ft wide 40 ft back from its point and 2.6 ft at 20 ft**, while an aze is ~1.5 ft of
  puddled mud (`AZE_FT`) on **each** side. The last yards are therefore two bunds with no floor
  between them - it cannot be leveled, cannot hold a depth, and cannot be transplanted. At 25
  degrees the same wedge is 17 ft wide 40 ft back, which is a workable bunded strip.

**What a real fan toe does instead** is what this file's shared-bund section already says a real
fan did with any awkward ground: the point is truncated into a headland along the collector, or the
odd corner is simply left unpaddied - *"the odd unplantable scrap was simply taken into the basin
beside it rather than walled off on its own."* The fix is therefore not new doctrine; it is the
existing doctrine applied to a case that was slipping through.

**Why it slipped through, which is the transferable part.** The toe pass already dropped
unbundable slivers, but its test was an **inradius proxy** (`2*Area/Perimeter`) - a THICKNESS. A
needle that is LONG passes a thickness test on the strength of its middle while its point is still
unworkable, and Inashiro's were 130-254 ft long. *A thickness test cannot see a taper.* The apex
angle is the measure that can, and `pointed_ring` was already in the codebase carrying a
pool-measured calibration (seam wedges 7-23 degrees, honest hem strips 45+), so the rule reuses
both ends of it rather than inventing a third number: **the placer refuses at 25 degrees, the gate
`paddy_plots_are_workable_basins` fires at 15** - placer stricter than gate, as everywhere else.

**Three places had to refuse a needle, and finding that took provenance data rather than
guessing.** Fixing only the carve took Inashiro 17 -> 8; also fixing `_plant` took it to 6; and
the survivors turned out (by instrumenting `close_seams` and classifying every needle by origin)
to be **entirely `carved_grown`** - good basins that *welding a scrap into them* had drawn out to a
point. The lesson is the cheap one: two wrong guesses cost a regeneration cycle each, and one
provenance probe answered it outright.

- `waterfields/comb.py::_comb_toe_and_hem` - drops needle apexes as well as thin slivers, and runs
  **after** `hem_to_bank` so it judges the ring that is actually recorded rather than one a later
  pass rewrites.
- `waterfields/seams.py::close_seams` - re-judges what `_plant` hands back and routes needles to
  the scrap path.
- `waterfields/seams.py::_absorb` - declines a weld that would needle the absorbing basin, in the
  same rejection ladder that already declines MultiPolygon, holed and bow-tie unions.

**The deliberate residue:** a strip that needles every basin it touches stays bare, and that is the
honest answer rather than a failure - the fan's base floor (`comb_base_fill`) draws under it, so it
reads as the toe's own ground. This is the same treatment the slivers dropped for thinness have
always had.

### Minimum basin SIZE - there is no absolute floor, and the real floor is a ratio

*GM question 2026-08-17, reading a scripted hamlet:* "most of the rice paddy fields are rectangular,
but then there are a few very small triangles. Is that realistic? It looks like it is just a
mistake, like, basically, a rendering artifact rather than something that is from our historical
research. Relatedly, should there be a minimum rice paddy size? I would expect that there would be."

**Grounds:** `_TOE_MIN_AREA` / `_GATE_MIN_AREA` in `waterfields/banks.py`;
`waterfields/comb.py::_comb_toe_and_hem`; `waterfields/seams.py`; the gate checks
`paddy_basins_are_worth_their_bund` and `comb_fans_record_their_design_cell`

**Evidence:** attested for the size range; the ratio is derived, from two independent arguments

**Sources:** `senmaida`, `bench-terrace-riser`

#### What the research found: no absolute minimum exists

Shiroyone Senmaida on the Noto peninsula works **1,004 basins on about 4 hectares**. The average
paddy is quoted at ~18-20 m2; many run about 1 m2, and the smallest is roughly **half a meter
square - two rice stalks**. The local anecdote is the clearest statement of the scale: a paddy once
reported missing turned up under a straw raincoat that had been laid on the ground. Obasute carries
over 2,000 small paddies; Longsheng's largest terrace is 0.62 mu (~0.10 acre) and most are far
smaller. So a floor stated in acres would condemn the most famous paddies in Japan, and our own
smallest scripted-hamlet basin - 240 sq ft, ~22 m2 - is *larger* than a typical Senmaida paddy.

**The absolute floor was therefore PRICED AND DECLINED.** It is the obvious rule and it is wrong,
in the same way and for the same reason that a minimum plot WIDTH was the obvious rule and wrong
when the fan-toe needles were fixed above.

#### Why those micro-basins are a TERRACE phenomenon, which is the whole finding

The discriminator is what the wall is for, and it is a physical difference, not a matter of degree.

- **On a terrace the wall already exists.** A bench terrace is a level platform cut into a slope and
  held by a **riser** - a near-vertical retaining face 0.8-1.5 m high, stone-faced where stone is to
  hand - and the riser is demanded by the SLOPE whether or not anyone subdivides. Water is held by a
  small 10-15 cm lip on top of it. The marginal cost of one more tiny bench is close to nothing, and
  the alternative to a 2 m2 bench is bare rock. Micro-paddies follow.
- **On a valley-floor cascade fan there is no riser.** The *aze* IS the whole structure, built only
  to hold water: puddled mud, re-plastered every spring (*azenuri*, the largest single maintenance
  job the bund network carries), standing on a strip of the most valuable land on the map. Its cost
  is charged entirely to the basin it creates, and the alternative to a scrap is never "no rice" -
  it is **making the basin next door bigger**, which costs no new wall at all.

That is this file's own shared-bund answer for an awkward scrap ("taken into the basin beside it
rather than walled off on its own") arrived at from the size direction. So the floor is real, it is
**contextual**, and it is a **ratio to the fan's own design cell** rather than an area.

#### Where the ratio sits - two independent derivations, and they agree

1. **Geometry.** A quarter of the design cell's AREA is half its linear size in both directions. A
   parcel below that is not a cell that came out small; it is a fragment of one.
2. **Cost.** With `AZE_FT` 1.5 and half charged to each side, the bund eats a share of the ground it
   encloses that climbs as the basin shrinks: 8.1% at a hamlet's 38.6 ft design cell, 16.2% at
   19.2 ft. A quarter of the cell is exactly the square at which that overhead has **doubled**. The
   doubling point barely moves with scale - 0.248 of the cell at 38.6 ft, 0.256 at the village's
   47 ft - so the number is not scale-tuned.

Both land on **0.25**, which is why it is not a compromise. The gate fires lower, at **0.20**, and
that pair is deliberately *not* the 0.6 ratio the apex rule uses (15 of 25) - see below.

#### Why the gate could not sit at 0.15, which is the transferable part

`_TOE_MIN_THICKNESS` already implies an area floor. It demands an inradius of `0.16 * plot_across`,
and a compact basin's inradius is half its side, so a square basin bottoms out near
`(0.32 * plot_across)^2` - about **0.16 of the cell**. Measured with the size floor patched off, the
smallest basin on any of the four scripted hamlets is 0.160 of its cell and nothing sits below it.
A gate at 0.15 was therefore a check that **could never fire**, and it was caught the only way that
works: by generating a manifest with the new rule switched off and watching the check pass on it.
The band the placer newly refuses is [0.16, 0.25), and the gate takes the middle of it.

The residue this leaves is also worth naming: the defect the GM saw lives in that narrow band, so it
is small parcels rather than absurd ones - 240-370 sq ft against a 1,488 sq ft cell. The rule is a
fabric correction, not a rescue.

#### The cost, measured before the number was chosen

Over the 2,829 basins of the four scripted hamlets, **1.63% sit under 0.25 of their cell** and 0.46%
under 0.20. Nothing is lost: each is dropped by the toe pass and then absorbed by `close_seams` into
the basin it shares the most bund with, so planted acreage, the field outline and the household
COUNT are all unchanged (Inashiro stays at 20.5 / 19.5 acres and 15 of 15 households).

**The ripple is NOT nothing, though, and the first draft of this section said it was.** A
`settlement-review` pass on Inashiro measured what the write-up had asserted away, and it was wrong:
the claim "farmhouse rings unchanged" was copied from the paddy-CELL calibration note above, where
it is true because that change subdivides the same envelope into more cells and draws the same
number of everything else. **This rule changes the NUMBER of drawn plots**, the patchwork draws from
the shared placement RNG, and so every downstream placement re-rolls. Measured against main's tip:

**And SAY WHICH METRIC.** The first version of this table did not, and was wrong by 2-4x as a result
(caught by the Sawada review). "Up to 78 px" was every new house's distance to the *nearest old*
house - which lets one old house partner several new ones, and so structurally under-reports. The
honest figure is a **one-to-one matching**: the smallest possible LARGEST displacement over all
pairings. On Sawada that is 286 px rather than 78, and one household leaves the mid-string for an
outlying pocket entirely.

Measured against main's tip, with the three review-found placement fixes in:

| map | basins | houses unmoved | min-max displacement | other |
|---|---|---|---|---|
| Inashiro | 640 -> 634 | 0 of 15 | **564 px** | gardens 18 -> 17, farm sheds 6 -> 3, view shifts |
| Kashikawa | 827 -> 814 | 20 of 20 | **0 px** | byte-identical, view included |
| Mizuguchi | 519 -> 511 | 7 of 12 | **250 px** | gardens 16 -> 17, farm sheds 2 -> 1 |
| Sawada | 843 -> 818 | 11 of 19 | **540 px** | gardens 20 -> 23, farm sheds 5 -> 6 |

Household counts (15/15, 20/20, 12/12, 19/19), acreage and the field outlines all hold - it is the
positions that rotate, by a map-specific amount, and Kashikawa proves the amount can be zero.

The lesson is general and belongs with the rule: **any change to a drawn COUNT re-rolls the shared
placement stream, so its ripple has to be measured rather than reasoned about** - and the reasoning
that feels safest ("the field outline is the same, so the rings that key off it are the same") is
exactly the one that fails, because the rings do not key off the outline through the RNG. It is also
how the cohort seed-41 well regression happened: a well moved, not a paddy. Three further defects
came out of the same rotation and were fixed under Principle XIV rather than ledgered - the byre
ranking, the windbreak's frame clip, and lane frontage; each map's notes carry its own.

One measurement trap is recorded because it cost a full calibration pass: the reference must be the
fan's **recorded** `cell`, not `paddy_grain(ftpx)`. `plot_texture` had already scaled the hamlets'
target down to 1,488 sq ft, so measuring against the un-textured 2,176 sq ft grain overstated every
ratio by about 1.5x. `build_comb` now records the cell it actually carved to, and
`comb_fans_record_their_design_cell` keeps that record from quietly disappearing.

#### The arrowhead: a chevron is pointed AND notched, and neither half alone can see one

*Follow-up to the size floor, 2026-08-18, from a `settlement-review` dart on Mizuguchi at
(1021-1084, 968-1012) that the area rule could not reach.*

**Grounds:** `_CHEVRON_MIN_APEX` / `is_chevron` in `waterfields/banks.py`; the refusals in
`comb.py::_comb_toe_and_hem` and `seams.py`

**The ledger asked for a tip-angle floor and the measurement said no.** The review called the ring an
arrowhead and quoted reflex corners of 311.9 / 273.1 deg, so a minimum tip angle of ~25-30 deg was
the obvious rule. Measured on the ring itself it is **not pointed enough** (min apex 38.3 deg raw,
39.0 deduped, against a placer that already refuses at 25), **not lobed enough** (solidity 0.878,
against the 0.85 the weld and tint guards use) and **not deeply notched** (deepest interior angle
227.4 deg, where 16 basins in the pool exceed 300). By every measure the project already owned it is
an ordinary irregular basin - which is what the fabric is supposed to be full of.

**What separates it is the conjunction.** A basin may taper honestly (the hem strips do). A basin may
be concave honestly (one wrapped round a neighbor is). One that does BOTH has a point at one end and
a bite out of its side, and that is an arrowhead. Over the 2,777 carved basins of the four scripted
hamlets: apex < 40 deg alone is 71 (2.6%), solidity < 0.90 alone is 49 (1.8%), **the conjunction is
13 (0.47%)** - small enough to read one by one, which is how the thresholds were chosen rather than
fitted. Both are round on purpose: 40 deg is "comes to a point", 0.90 is "has a real notch". Fitting
tightly to the motivating ring (39 / 0.88) would have caught 11 and been overfitting to one example.

**NO GATE CHECK ACCOMPANIES THIS RULE, and that is a decision rather than an omission.** The carve is
clean - a provenance probe measured **zero** chevrons entering `close_seams` on both affected maps -
but `close_seams`' absorb ladder deliberately accepts a chevron as its LAST resort, because the
alternative is leaving a scrap bare between two basins that each keep their own wall, which is the
doubled bund `paddy_plot_seams_shared` exists to prevent and a worse defect than an awkward shape.
So 5 of 2,774 survive pool-wide (13 -> 5, all from that tier). A gate would therefore either fail
the shipped pool or be tuned to pass it, and tuning a check to its own output is how a check stops
meaning anything. The placer rule stands on its own measurement; if the residue ever needs closing,
the lever is the absorb ladder's last tier, not a new threshold.

#### The other declined alternative: paddies are NOT restricted to four sides

The GM raised this himself and doubted it, correctly. A rule that every basin be a quadrilateral was
considered and **DECLINED outright**: it would re-impose exactly the tidy rectangular grid that this
file's own "irregular patchwork" section identifies as the *kochi seiri* land-consolidation artifact,
and it would contradict the attested look - the tanada mosaic of odd, piecemeal parcels meeting at
T-junctions. A triangular basin is legitimate; several survive on every map. What was wrong was never
the number of sides but the SIZE, with triangularity as its symptom, because a clipped corner of the
plot lattice at the fan's boundary is the shape a fragment naturally takes.

*Re-sourcing note (2026-08-28, feature 143):* the bund page read gives a standard trapezoid of 30 cm height and 30 cm TOP width on 1:1 slopes, i.e. about 1 ft high and ~3 ft at the base - the entry's "1-2 ft wide, ~1 ft high" reads as a top-to-base span and is consistent; cold regions run ~50 cm top / ~40 cm high. Nothing read supports a bund a meter high.

## How deep the water actually stands, and why a single number is the wrong shape

**Grounds:** the `paddy` class's `what` and `caveat`; the aze finding above; `check_village/segments_04a` (no wellhead in a paddy)

**Evidence:** researched, MODERN - every figure below is contemporary Japanese extension guidance; no pre-modern number was found

**Sources:** [`maff-suitou-mizu`](SOURCES.md#maff-suitou-mizu), [`zennoh-mizukanri`](SOURCES.md#zennoh-mizukanri)

- *What we said, and why it was wrong TWICE.* From feature 134 until 2026-08-29 the map told its
  reader that a paddy holds "four to six inches of water" (about 10-15 cm), citing
  `tabayashi-1986`. Both halves fail. The depth is wrong: the maintained figures are **2-3 cm**,
  about an inch - 活着後は水深2~3cmのやや浅水とし ("after rooting, a slightly shallow 2-3 cm"), and for
  the twenty days from heading, 2~3cm程度の湛水状態を保つことが重要です. And the SHAPE is wrong, which
  is the larger error: there is no season-long depth to state.
- *The season, as the sources give it.* 3-4 cm at transplanting, held slightly deep against cold and
  wind until the plant roots; 2-3 cm once rooted, deliberately shallow so the water warms and
  tillering starts early; then **中干し (nakaboshi), the mid-season drain** - the field is taken down
  to nothing and dried until 田面に小さなヒビが入り、軽く足跡がつく程度 ("small cracks appear in the
  field surface and a light footprint shows"); then intermittent wet-and-dry; standing water again
  at heading, 2-3 cm for twenty days; intermittent through ripening; and a final drain 5-7 days
  before harvest. **A paddy is not under water all season, and for part of midsummer it is dry
  enough to crack.**
- *Where the four-to-six-inch figure DOES appear, and why it misled.* 10 cm and 20 cm are real
  numbers in the record - but as a cold contingency, not a norm: MAFF gives them under
  気温が下がる恐れがある場合は ("when there is risk of falling temperature"), 10 cm at panicle
  formation and 20 cm at booting, to protect the young panicle. A figure read out of that context
  becomes a maintained depth that nobody maintains.
- *The citation that never supported it.* `tabayashi-1986` is a study of the distribution and
  development of irrigation systems, classified by water source. It says nothing about water depth.
  Our own `SOURCES.md` "Used for" line had always said so - tameike siting, one outlet, the canal
  taper, supply/drain separation - which is exactly what that field exists to make visible.
- *What we could NOT get, and what that costs.* No pre-modern depth figure, in Japanese or Chinese
  material. The searches returned Edo irrigation infrastructure and water-dispute histories and no
  number. So the figures above are **modern extension guidance applied backward**, and the class's
  caveat says so to the reader rather than presenting them as a historical finding. What is
  plausible about applying them backward - that the agronomy of a puddled basin has not changed, and
  that shallow warm water for tillering is a constraint of the plant rather than of the century - is
  reasoning, not evidence, and is not asserted.
- *The bund is NOT re-derived from this.* The aze runs roughly 1-2 ft wide and about a foot high
  (sourced separately, above). A foot of ridge over an inch of water is not a contradiction to fix:
  the ridge has to hold the 10-20 cm cold-protection state, keep freeboard in rain, and be walked.
  That is inference rather than a finding, which is why it lives here and in the feature's spec
  rather than as a sourced claim, and why nothing drawn changed - `AZE_FT` is a WIDTH.
- *Available if wanted, not built.* The staging is a real seasonal axis: a map showing nakaboshi
  would draw cracked mud where this one draws water. The map depicts one moment and which moment is
  a question nobody has asked yet, so this is recorded rather than made a knob (feature 160).

## Nitrogen - a flooded paddy makes its own

**Grounds:** the ~6% soy share; azemame as a food crop

**Evidence:** attested (the mechanism is textbook), researched (not re-read this pass)

**Sources:** searched 2026-08-28: the IntechOpen chapter (intechopen.com/chapters/69541) reads only a general "biological nitrogen fixation" clause; Springer 978-3-662-10385-2_22 paywalled; MDPI agriculture9020029 403. Azolla-cyanobacteria fixation and renge green manure want an open source (IRRI / FAO azolla pages) - leftover `azolla-enwiki` (READ, leftovers pass: Azolla on the flooded paddy releasing nitrogen; the cyanobacterial symbiont and renge - ja.wikipedia ゲンゲ - still to read)

- *Nitrogen - the paddy makes its OWN, so soy is food not fertiliser.* A flooded paddy is near self-sustaining for nitrogen: the standing water hosts N-fixing **cyanobacteria + *azolla*** and the **irrigation water carries in silt/nutrients** from upstream - which is why paddies crop continuously for centuries where dry-field monoculture exhausts the soil. Legumes entered as **winter green manure grown IN the drained paddy** (*renge* / Chinese milk vetch, plowed under before spring flooding) + applied night soil / ash / fish-and-oilseed cake - NOT soy on the margins washing in. So the ~6% soy is a **food crop** (dry fields, and characteristically on the paddy bunds - *aze-mame*, "ridge beans"), NOT the paddy's nitrogen supply.

## Why ruled rows waited for Meiji

**Grounds:** `_paddy_surface` (no ruled rows on a wet paddy)

**Evidence:** attested (the package), researched (the police enforcement - SUMMARY-ONLY)

**Sources:** `seijoue-kotobank`, `seijoue-seika`, `kubota-transplanting` (READ: seijoue rare before Meiji, promoted nationally in the 1890s-1900s with the 田打車 weeder, ropes and rulers). The police standing over the planting and the 1903 order: SUMMARY-ONLY (search syntheses of agri.hakase-jyuku.com "サーベル農政"; not read)

- *WHY rows waited for Meiji when row planting is ancient (GM 2026-07-23 - the idea was never the bottleneck, the economics were).* Dry-crop rows are FREE: the seed goes into a plowed furrow, and the furrow IS the row. Wet rice is TRANSPLANTED into a puddled flooded sheet with no furrows and no guide lines, so rows must be PURCHASED - marked ropes or a rolled gridding frame, plus every planter aligning to them - and the bill lands in the year's tightest labor window (the whole village transplants in days, on a shared water schedule). And for centuries the purchase bought nothing: rows pay when a tool travels BETWEEN them (the ancient dry-field hoe/cultivator), but nothing could travel between rows in a flooded paddy - weeding was by hand and foot either way. What changed in Meiji was the arrival of the between-rows tool for mud: the hand-pushed ROTARY PADDY WEEDER, which only works on plants ruled in both directions - so *seijoue* + marking frame + rotary weeder spread as ONE package, pushed by state extension hard enough that police sometimes stood over farmers to enforce straight lines ("saber farming"), itself evidence the private payoff was marginal before the full package. Traditional transplanting was NOT chaos though: clump spacing was roughly even (a practiced hand keeps density consistent - density drives yield), just never ruled - which is exactly what the sparse unruled shoot-mottle renders.

## Water-first v2 - pond, distribution and the three layout modes

**Grounds:** `waterfields.py`; `build_comb` / `build_terraces` / `build_ribbon`

**Evidence:** attested, corroborated

**Sources:** [`tabayashi-1986`](SOURCES.md#tabayashi-1986), [`kagawa-tameike`](SOURCES.md#kagawa-tameike), [`jsidre-minumadai`](SOURCES.md#jsidre-minumadai), [`japanese-wiki-corpus`](SOURCES.md#japanese-wiki-corpus), [`beitang-studies`](SOURCES.md#beitang-studies)

- **Pond**: a valley-head *tameike* behind an earthen dike, sitting ABOVE its fields ("located at a valley head and constructed by dividing off the valley mouth with an earthen dike... at elevations higher than the surface of the paddy fields they serve" - Tabayashi 1986, Geographical Review of Japan 60(1)). ONE outlet: an inclined intake (shahi) feeding a bottom conduit (sokohi) through the dam; the spillway is flood-safety, never distribution (Kagawa pref. tameike docs). Parent/child pond linkage (oyaike/koike, Kagawa; "melon-on-the-vine" in China) is attested flavor for larger systems.
   - **Distribution**: sluice -> head-race -> division point (bunsuiguchi) -> a branching TREE. "Main canals **gradually decrease in size as they are tapped by branch canals**" (Tabayashi) - hence the drawn taper. The smallest ditches "are often considered parts of the paddy fields they serve" - hence ditch-as-plot-boundary. SPARSE is correct: a village digs the minimum network; a ditch beside every paddy (yohaisui bunri) is a Meiji land-readjustment (1899/1905) anachronism.
   - **Layout modes** (terrain-driven; the GM wants all three eventually):
     - **COMB (the default)**: supply canals along the HIGH margins, delivery ditches perpendicular down-slope, one drain along the low line. Grounding: the Edo Kishu-school layout (Minuma-dai 1728 - the LAYOUT is sourced, the NAME is queued: a 2026-08-29 read found 紀州流 attested as Izawa Yasobei's river-channelization method rather than a field layout, so do not re-use the name elsewhere until it checks out, `SOURCES.md` re-sourcing queue: supply on the elevated margins, drainage channel on the lowest line, water reused downstream) AND codified Chinese canal doctrine (mains along contours/ridges on high ground, field channels perpendicular to contours). Chinese *beitang* pond systems - the direct tameike analogue - were THE dominant village-scale mode in rice China (8.3M ponds serving ~39% of irrigated area into the 1950s, ~71% in hilly regions); the GM chose the Chinese default deliberately (Rokugan demographics anchor to Song/Ming China).
     - **FAN (supported option, not default)**: gently-descending canals radiating from a valley-mouth apex - the Dujiangyan / Tedori-alluvial-fan geometry. Correct where the land fans out below the pond.
     - **JORI GRID (future option, recorded on GM request - NOT implemented)**: from the 7th century much of Japan's long-settled PLAINS carried an astronomically-oriented 109 m grid (jori-sei: 1-cho squares in 6x6-ri blocks, cut into ~12 x 109 m tan strips). A plains village in an ancient core province shows semi-regular GRIDDED paddies, not organic patchwork - Rokugan analog: ancient heartland provinces (e.g. Crane/Phoenix cores). The organic warp-thread patchwork is correct for terrain-following villages like Kikuta.

## Plot sizes, pond sizing and acreage from population

**Grounds:** the v2 carve targets

**Evidence:** interpolated

**Sources:** `kokudaka-jawiki` (READ: one koku a year; real stipends ~1.8), `gokogomin-kotobank` (READ: 40% then 50% - the "~45%" is an undisclosed midpoint, now disclosed). Not read: the 2,000-2,500 m3/ha tameike ratio (the Aomori 21nn_17ike.pdf is unreadable to the fetcher), the 1.3 koku/tan yield, the 0.02-0.25 acre plots and the Tedori straightening - leftover

- **Plots**: pre-modern 0.02-0.25 acre, irregular; v2 carves ~0.1-0.15 acre, ~9 scattered plots per household (fragmented holdings were normal). STRAIGHT rectangular channels/plots are post-1900 consolidation (the Tedori fan's ditches were only straightened in the early 1900s) - the organic waver is period-correct, do not "clean it up".

- **Pond sizing (the rule)**: sole-storage tameike run ~2,000-2,500 m3 of storage per irrigated ha (typical depth 2-4 m); a STREAM-FED pond refilling 1-2x a season is comfortable at ~1,200-1,500 m3/ha. Hoshigaoka: 31.8 ha of paddy -> ~1.5 ha pond surface (rx=145, ry=92 px at 1px=2ft) ~ 47,000 m3 at ~3 m ~ 1,470 m3/ha + feeder stream. The first draft's 0.84 ha pond (~790 m3/ha) was honestly undersized - keep pond area proportional to command area.

- **Acreage from population (the sizing rule)**: a person eats ~1 koku/yr; pre-modern yield ~1.3 koku/tan; coarse grain fills part of the diet while ~45% of rice goes to tax -> ~0.8-1.0 tan gross paddy per person -> 350 people ~ 280-350 tan = **69-86 acres** (+ dry margins later). WIP Kikuta lands ~79 acres / ~600 plots.

## Tract sizes - no settlement-class cap

**Grounds:** comb-fan sizing (`field_fall`) on every map tier; the pending town-paddy recalibration (GM 2026-08-02, decision open)

**Evidence:** researched

**Sources:** [`li-bozhong-jiangnan`](SOURCES.md#li-bozhong-jiangnan), [`skinner-marketing`](SOURCES.md#skinner-marketing), [`aric-land-history`](SOURCES.md#aric-land-history), [`mdpi-kunisaki`](SOURCES.md#mdpi-kunisaki), [`buck-survey`](SOURCES.md#buck-survey)

The PLOT question (one leveled cell, ~0.05 ac) is settled above; this entry is the layer above it - the TRACT: one contiguous field system (a comb fan, a terrace flight, a polder) and how much ground it commands. Asked by the GM 2026-08-02 after Hoshizora's west comb read as "extremely unusual": *what range of rice paddy sizes might we see in a mixed-use settlement - partially urban, partially pastoral grazing, partially food-growing farms?*

- *Per-household paddy (China first).* Mid-Qing Jiangnan farms averaged ~10 *mu* per farmer - Li Bozhong's "ten *mu* per farmer" - at the Ming-Qing *mu* of ~614 m2, so **~1.5 acres of intensively worked wet rice per farm household**; Buck's surveys corroborate that a holding was scattered over several parcels. Japan corroborates: the Edo average farm household held ~1 *cho* (~2.45 ac) TOTAL, paddy plus dry, putting its paddy share in the same ~1-1.5 ac. The working band: **~1-2.5 acres of paddy per farm household** - the same number the diet-side acreage-from-population rule above reaches independently (~0.8-1.0 *tan*/person x ~4.5-person households).

- *The communal-system floor.* A comb fan is communal waterworks - weir, head-race, canal fork, tapering deliveries, a drain collector. The smallest attested community systems are pond/tank-fed: small *tameike* systems run ~10 ha each (Kunisaki's Tsunai ward: 5 systems totaling 50 ha across 11 farmers), and traditional village tanks typically command tens of hectares, well under 200. Even a handful of cooperating households implies ~1.5 ac each, so **the floor for a system that justifies drawn head-race-and-collector infrastructure is roughly 3-8 ha (~8-20 ac) - exactly the hamlet tier**. Nobody builds a weir and a canal fork for 2 acres; ground that size is ONE household's holding, watered by a single ditch. The GM's framing is the right mental model: a hamlet IS a small paddy tract with farmhouses around it, and a hamlet-sized tract is the honest minimum for any fully-drawn fan, wherever it appears.

- *The town edge has NO tier of its own.* A market town / county seat is the CENTER of a farmed hinterland (Skinner: the standard marketing community is ~18 villages over ~300-500 km2), and cultivation historically pressed against the built edge - Chinese county seats with farmland to the walls and farmers walking out from town; Japanese post towns strung along highways through continuous paddy. Tract size is set by water, terrain, and mouths fed - never by settlement class. A mixed-use edge (urban core + hay/grazing + farms, the Hoshizora premise) legitimately carries anything from a hamlet-grade fan (~8-20 ac) where irrigable ground is short, through village-grade tracts (~50-90 ac), up to open farmland bounded only by the frame; the attested LOW end is terrain-limited (the upland Kiso post towns), and even there the limit is the terrain, not the town-ness. Small is legal where the map shows the terrain reason (hay country, forest, slope); tiny-with-full-waterworks is not attested anywhere.

- *What the pool draws today (audited 2026-08-02; shoelace area of each paddy `outline` x ftpx^2).* Hamlets 7.7-35.3 ac for 14-18 steadings (~0.5-2.2 ac/household - in-band). Villages 54.9-86.8 ac for 55-85 (~0.9-1.3 - in-band). Provincial cities 40.6-61.6 ac in 6-10 edge fans of 2.8-10.1 ac each, every fan visibly RUNNING OFF the frame - the truncation itself says "slice of a larger field", so the small on-frame acreage is honest. Towns are the outlier: Hoshizora 2.4 ac total against 45 depicted farmsteads, Ubame 4.0 against 35, Hirameki 8.2 against 73 - **0.05-0.11 ac per depicted farm household, 15-30x under the band; each town's whole drawn paddy is smaller than ONE real household's holding**. The cause is mechanical, not doctrinal: the town gens hand-cap `field_fall` at 145-320 px and hand-set `row_step=(52,72)` outside the `paddy_grain` lineage. The "town map shows a slice of the county's farmland" doctrine covers a fan that runs off-frame (hoshizora-ne, ubame-south do) but NOT an enclosed one - hoshizora-west is bounded by stream, road, monastery, and laborers' quarter on all four sides and therefore reads as a complete, absurdly small farm.

- *The decision (GM 2026-08-03).* The accidental town cap is dropped and the ladder is: **8 acres is the hard floor for any ENCLOSED fan** (one that does not run off the frame), reserved for mixed-use / terrain-limited maps that SHOW the reason there is no more irrigable ground (Hoshizora's relay hayfields + grazing + forest, `near_ring_density="thin"`); **~20 acres is the ordinary small end for a non-specialized town** - in practice drawn as a modest enclosed fan plus off-frame slices, since 20 enclosed acres at 1 ft/px is ~a third of a town canvas and a real town sits amid continuous farmland anyway; villages stay population-sized at ~50-90 ac; cities keep the off-frame slice convention. Off-frame slices stay exempt from the floor ON-MAP (the truncation says "more beyond"); the floor bites exactly where an enclosed fan reads as a complete system. An enclosed fan's own ring reads as ~1-2.5 ac/household for the steadings living off it; the rest of a town's depicted farmers read as working the off-frame fields, which is why `town_has_field_off_edge` matters on every town map. *Landed 2026-08-03:* the ring placer's road-severed filter + `farmsteads_reach_their_fields_unsevered` (hoshizora's lone south-of-road farmhouse is gone), and Tango's four offenders (fn1/fn2/fs1 as off-view slices, nw1 as the in-wall exemption). *Pending with the town recompositions* (the floor check itself waits in [`../pending-enclosed-fan-floor.md`](../pending-enclosed-fan-floor.md)): the three towns' fans, the town combs' `paddy_grain`/`grain=2` lineage move, and with it the bund-vs-drain stroke fix (the 1 ft/px bund and drain rendered at equal ~1.5 px weight because the town gens passed `grain=1` where the engine's docstring calls for `grain = 2/ftpx`).

## Where dry (hatake) crops go - the topographic catena

**Grounds:** the `dry_band` knob

**Evidence:** researched

**Sources:** `satoyama-enwiki` (READ: the mosaic and the foothill-to-flat border zone). The Takeuchi-school catena sentence ("large middle river terraces... large areas of crop fields and small areas of paddy") is SUMMARY-ONLY - the mekongwatch PDF is unreadable to the fetcher; find the paper itself - leftover

WHERE dry crops go: wet-rice villages sort by a topographic CATENA - irrigated paddy holds the flat valley bottom / plain; DRY fields (hatake) take the HIGHER, well-drained ground the water cannot command (river terraces, natural levees / micro-highs threading the plain, alluvial-fan edges, lower slopes, AND the slightly-raised ground the homesteads sit on); coppice woodland (satoyama) crowns the hills above. Sources: satoyama land-use literature ("wet-rice in the plains and valley bottoms... satoyama woodlands/grasslands for dry-field crops"; "large middle river terraces... large areas of crop fields and small areas of paddy"); Kanto-plain historical-GIS land-use studies. So dry fields are NOT one neat strip - historically they sit in SEVERAL positions, above all AROUND the houses ("each family has some paddy and some hatake", the household's dry plots near its home).

## The wettest plots are their own kind of ground - shitsuden, and why they read blue

**Grounds:** the `wet paddy` interactive class (feature 159); the FLOODED tint in `waterfields/carve.py`, `polder.py`, `hill.py`

**Evidence:** researched (the category and its penalties are READ; the siting is an inference, said so below)

**Sources:** [`kotobank-shitsuden`](SOURCES.md#kotobank-shitsuden), [`kotobank-kanden`](SOURCES.md#kotobank-kanden), [`kotobank-yatsuda`](SOURCES.md#kotobank-yatsuda), [`kotobank-fukada`](SOURCES.md#kotobank-fukada), [`fao-rice-water`](SOURCES.md#fao-rice-water)

- *A wet paddy is a NAMED category, not a wetter example of the same thing.* Pre-modern Japanese
  agriculture split paddy land in two. **湿田 (shitsuden)**, "wet paddy": 水はけが悪く、水稲を栽培
  していないときでも過湿な状態の水田。また、麦などの裏作のできない水田。 - *"a paddy with poor
  drainage that stays waterlogged even when rice is not being grown; also, a paddy on which a winter
  crop such as wheat cannot be grown"*. Against it **乾田 (kanden)**, "dry paddy": 水はけのぐあいが
  よく、水を入れないときには乾いて畑の状態になる田。 - *"a paddy with good drainage that, when water
  is not let in, dries out to a dryland-field state"*. The distinction is about the ground and its
  drainage, and it holds all year, which is why it is a KIND of plot rather than a moment in one
  plot's season.
- *It is worse ground, and the record is blunt about how.* 過湿、滞水のために農作業が困難で、また麦
  などの裏作ができない排水不良田 - work is hard and there is no winter crop; 地温が夏は乾田より低く
  酸素不足の状態で - the soil runs colder than a dry paddy in summer and short of oxygen; 倒伏や病害、
  生育遅延などで収量は不安定である - lodging, disease and delayed growth make the yield unreliable.
  Flatly: 湿田の生産性は概して低い - *"shitsuden productivity is generally low"*. So a household
  holding one is holding the plot nobody wanted, and that is the fact the map is worth showing.
- *The scale of the problem, from the other end.* From Meiji the state ran 湿田の乾田化 - the
  conversion of wet paddy to dry - as a national undertaking, and 全国の水田の2/3以上は乾田となった
  といわれる, *"it is said that more than two-thirds of the nation's paddies became kanden"*. A
  program that size is the measure of how much wet paddy there was to convert, which is the reason a
  pre-modern map should carry some.
- *The valley bottom is where it sits, and it has its own word.* **谷津田 / 谷地田 (yatsuda /
  yachida)** is the valley-bottom paddy - 台地が開析されてできた谷間の低地すなわち谷地に分布する水田
  ... 一般に湿地で古く開発された, *"distributed in the valley lowland formed by the dissection of a
  plateau ... generally wetland, developed long ago"*. **深田 (fukada)**, "deep paddy", is attested
  separately as どろの深い田。沼田 - *"a paddy with deep mud; a swamp paddy"* - the opposite of 浅田
  (asada, shallow paddy). It names a DEGREE of mud, not a position on a slope.
- *What is an INFERENCE, and is drawn anyway (constitution XII).* That the plots lying on the drain
  collector are therefore the wettest ground in the field is not a finding anybody wrote down. The
  attested part is the cascade: in traditional terraced paddy *"water flows from one plot to another
  and no distinction can be made between irrigation and drainage"*, and surface runoff *"can be
  re-used, i.e., recycled within the system"*. Gravity does the rest, and the engine has always sited
  the tint that way (`carve.py`: *"only the level whose BOTTOM edge lies on the collector floods -
  the wettest, lowest ground"*). It is a reasoned inference from an attested mechanism, and it is
  labeled one here rather than presented as a finding.
- *Two things we did NOT get, and do not assert.* No source read gives a maintained growing-season
  water depth of four to six inches as such - IRRI's 5-10 cm figure could only be reached in a search
  summary (the host refused the fetch) and FAO's fetched 5-20 cm is a bund-construction range, not a
  maintained depth. And nothing read says the water surface stays visible between the plants until
  the canopy closes, which is the sentence a reader might expect to justify drawing one plot bluer
  than another; the drawn difference rests on the ground being wetter, not on a sourced claim about
  what a camera would see. Queued in [`SOURCES.md`](SOURCES.md#re-sourcing-queue).
- *The drawing convention, stated where it will be read.* Which plots wear the tint is the picture,
  not the topography, and the two field engines differ: a COMB field tints a random 45% of the
  eligible rank (`carve.py`), so Inashiro shows 2 blue plots over 24 low ones, while a POLDER or
  TERRACE field tints every low plot (`polder.py`, `hill.py`), so Enokida shows 22 over 22 and Tanada
  40 over 40. On a comb map, therefore, blue is a SAMPLE of the wet ground and not the whole of it -
  the modal says so, because a reader who reads the tint as the set is being misled about the other
  22 plots.

## What a bund bean actually looks like - the soybean plant against the bead we draw (researched 2026-09-05, feature 183)

**Grounds:** `BEAN_GREEN` and the `r="1.4"` bead in `settlement/fields/comb.py`; the `bund beans` class note in `interactive/classes.py` (a map drawing convention, written in the GM's form)

**Evidence:** attested (the practice, the height, the leaf color), liberty (the bead's size and color)

**Sources:** `nabunken-azemame`, `wikipedia-soybean`, `cropfarming-soybeans`

*The question.* The GM's wording rule (feature 183) asks a convention's note to say what the feature
actually looks like beside how we draw it. The beads on the bunds are soybeans (azemame); the record
held the practice and the color decision but no figure for the plant itself.

*What the research found.* The practice, READ from the Nara National Research Institute for Cultural
Properties' Asuka pages: *"『畦豆（あぜまめ）』とも呼ばれる大豆です ... 田植え後に畦に種がまかれ、稲刈りと同時に収穫されます"* -
a soybean also called azemame, sown on the bund after transplanting and harvested with the rice; once
grown all over Japan, mostly gone with land consolidation and herbicide, still grown at Asuka; the
photo caption has them *"ずらっと育っている"* - growing in a row along the bund. The plant, READ: *"fully
mature soybean plants are generally between 50 and 125 cm (20 and 50 in) in height"* (Wikipedia,
Soybean, Description); *"The plant is erect and bushy, with branches coming off a central stem"* and
*"The leaflets are broad, pointed, and medium green"* (cropfarming.org - a trade site, the one page
read that states the leaf color; Wikipedia's Description says nothing about color). **Not found:** a
figure for one plant's spread on the bund - the Iowa State extension page on row spacing discusses
canopy-closure timing, not plant width - so the record does NOT say how wide a bund bean stands, and
no note may compare the bead's width to the plant's. SUMMARY-ONLY and not used: search snippets on
azemame roots firming the bund, miso from azemame in Noto, and nitrogen to the paddy (the last
contradicted by 'Nitrogen - a flooded paddy makes its own' above).

*The convention, stated for the reader.* We draw each plant as a round bead about 3 ft across
(`r="1.4"` px at one foot per pixel), in a single row on the bund, in a deep pine green (`#2F6B35`)
chosen so the beads read against the pale rice; real foliage is medium green, and the bead is drawn
darker than the plant. The plant is a knee-to-waist-high bush (50-125 cm); the bead says only where
it stands. `waterfields/palette.py` records why the color was chosen (GM 2026-08-15: the old olive
read as neither rice nor bund).

## Free lore hooks, and the sources

**Grounds:** /law, /calendar, village detail

**Evidence:** researched

**Sources:** [`tabayashi-1986`](SOURCES.md#tabayashi-1986), [`kagawa-tameike`](SOURCES.md#kagawa-tameike), [`jsidre-minumadai`](SOURCES.md#jsidre-minumadai), [`maff-water-history`](SOURCES.md#maff-water-history), [`nies-shiroyone`](SOURCES.md#nies-shiroyone), [`japanese-wiki-corpus`](SOURCES.md#japanese-wiki-corpus), [`beitang-studies`](SOURCES.md#beitang-studies)

- **Free lore hooks from the sources** (for /law, /calendar, village details): drought rotation in fixed village turns; water-heads (mizugashira) elected to run the flow; supply turns timed by BURNING INCENSE STICKS (senkomizu); upstream villages leveraging position in water disputes; a village trading pond-management duty for water rights.
   - Sources: Tabayashi 1986 (jstage grj1984b/60/1), Kagawa pref. tameike structure pages, JSIDRE on Minuma-dai, MAFF agricultural-water history PDF, Shiroyone terraced-paddies (NIES), jori-sei (Japanese Wiki Corpus + Tsukuba field-trace surveys), beitang studies (Nature Comms 2023; Jiang-Huai pond irrigation, PMC6695888), Chinese canal-layout doctrine (灌溉渠道 refs).
