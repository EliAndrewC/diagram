# Closed - the ledger

One line each. The full narrative is in git history and, where it matters, at the point of change in
the code. **Nothing here is waiting on anyone.**

It exists so a later session can distinguish "settled" from "forgotten" without reading a diff. That
is not hypothetical: the 2026-08-24 audit found two questions that had drifted back to reading as
OPEN - one for five days, one for seven - and both were about to be put to the GM a second time.

**When you close an item, move it here in the same commit that closes it.**

- DONE 2026-08-19: `cluster_shape` was the same defect as 2e, one tier worse - it WAS rolled and read by nothing
- DONE 2026-08-19: the woodland scan vetted a SQUARE while the gate measured a ROTATED BBOX
- DONE 2026-08-19: the streams were invisible to every way-vs-water test
- DONE: azemame record hygiene - water-buried beads (2026-08-15, same day)
- DONE 2026-08-16: pocket ponds carry ink-on-water of their own (settlement-review, 2026-08-15)
- DONE 2026-08-16 (the known-opens session, same day): four ledger items closed
- DONE 2026-08-17: cohort seed 2's four drainage failures - ONE defect, and the ledger's sketch was right
- DECIDED 2026-08-17: `plot_rings` STAYS a paint-order stack - documented, with a lap ceiling
- DONE 2026-08-17: the fan-toe SUNBURST - RULED and fixed
- DONE 2026-08-17: the paddy size floor, and the well fix it had to wait behind
- RESOLVED 2026-08-18 (was BLOCKING): cohort seed 5's drain, and the well tie-break's cost
- DONE 2026-08-17: `_outside_cloud` now tests the CROP's box, not a box of house centers
- DONE 2026-08-17: cohort seeds 9 and 11 - and the "genuine conflict" was two bugs
- RULED 2026-08-17: the fan-toe SUNBURST (was: "needs a GM ruling before anyone re-cuts it")
- DONE (feature 118): `rolling.py::roll_village` - and the measurement worth keeping
- DONE 2026-08-17 (same day): two farmhouses could MERGE - now ruled and gated
- RULED 2026-08-17 (same day): Kashikawa's hamlet-of-one
- How both of the above were closed (2026-08-17)
- MOSTLY DONE 2026-08-18: three found by the 2026-08-17 review round (see the status on each)
- 1. RETRACTED - the flooded tint census does NOT reproduce; keep only the test sketch
- 2. DONE 2026-08-18 - a lane dead-ends 90 ft past its own junction (Sawada)
- 3. RESOLVED BY MEASUREMENT 2026-08-18 - the "adaptive" garden side IS adapting
- 4. DONE 2026-08-18 - `scatter_audit` reported `crown=0` on a map recording 2,665 crowns
- 5. DONE 2026-08-18 - the shared byres end-loaded onto one flank of the cluster
- 6. DONE 2026-08-18 - the kura flag is stable against regeneration but NOT against re-packing
- Corrections to items 1 and 3 above (2026-08-17, same day)
- ONE DONE, ONE OPEN: two more from the Sawada re-review (2026-08-17)
- 7. DONE 2026-08-18 - the title placard printed over a woodland commons parcel
- THE THREE QUESTIONS - ALL RESOLVED (2026-08-18)
- A. RESOLVED BY RESEARCH - a byre belongs beside a wellhead. Nothing to change.
- B. RULED BY THE GM - KEEP THE KNOB, and make the drawing match it.
- C. RESOLVED BY RESEARCH - the back rank IS served, and the FORM of the service is a knob.
- D. DONE / HANDED OVER 2026-08-18 - the two lane-topology defects
- MOSTLY DONE 2026-08-19: paddy bunds that step sideways - the staircase is gone, 7 corners remain
- CORRECTED - cohort seed 10's belt hole is a SUN CORRIDOR, not a polygon pinch
- DONE 2026-08-19: the gen-time budgets had drifted from protection into a coin toss
- DONE 2026-08-19: coverage that depends on whether the GEN CACHE was warm
- DONE 2026-09-27 (feature 261): one bank or both - ways cross the brook at a ford with a plank bridge, so a hamlet stands astride its own channel as the record attests at that size (research/water.html, 'Does a hamlet stand on one bank of its stream, or around it?'); not a knob, because the one-bank form belongs to a river and no hamlet map draws one
- RULED 2026-09-28 (the GM): no GM-only Obsidian Portal notes on a page, not now and not ever - the GM moves a note somewhere visible to show it; Ubame's post stays within one lineage (Moriguchi is its domain's only dynasty province)
- DONE 2026-09-28 (269 E4, B06): the dry-hem furrow variety cliff - the record (research/fields.html, 'Why do neighboring dry plots run their furrows different ways?') sets the row direction TRACT BY TRACT, not per plot, so the hem runs in tracts sharing one direction with a few degrees per plot and a turn of at least ~20 deg at each seam (`waterfields/furrows.py`), and `dry_plot_furrows_vary` judges tracts over every shipped hamlet; the per-plot maximize-separation rule and its blind radius are gone
- DECIDED 2026-09-28 (the GM, 269 B33): the dike-pond mulberry keeps the premodern spacing - the drawn ~23 sq ft a bush is the late-Qing mid-trunk figure (research/archetypes 220); the modern root-cut density is not used
- DECIDED 2026-09-28 (the GM, 269 B34; done in 269 E9): a hamlet's dikes roll mulberry, fruit or tea; cane, banana and vegetable dikes are retired as modern-only (research/archetypes 230)
- DONE 2026-09-28 (269 B16): the byre on the inner commons or the outer fringe - neither; the record puts the beast with its household (research/homesteads 300), drawn as the inner stable or a yard shed; what is left of the commons form is its own open entry
- DONE 2026-09-28 (269 B16): the byre at the settlement edge - no page read sites a byre there (research/homesteads 300); closed with the entry above
- DONE 2026-09-28 (269 B17): how far past its last steading a way may run - an end serves a house at its dooryard or beside it within the gate's 60 ft, never past it (research/ways; `trim_lane_stubs`); Sawada's and Kashikawa's run-outs moved
- DONE 2026-09-28 (269 B27): Kashikawa's woodland downslope - the woodland is seated beyond the fields and above the field it adjoins, never downslope of every house (research/vegetation 140; `hinterland/parcels.py` `woodland_tier`)
- DONE 2026-09-28 (269 B28): woodland stocked like parkland - the commons coppice is stocked one crown per 64 sq ft at 8-9 ft (research/vegetation 230; `COMMONS_SPACING_FT`, `CrownIndex`)
- DONE 2026-09-28 (269 B30): the belt and the copse share one crown vocabulary - the belt rolls conifer-led rows or mixed broadleaf (research/vegetation 270; `windbreak_belt`)
- DONE 2026-09-28 (269 B04): where a field path ends, and the three pool maps with no spur - every way reaches the field ON its bund (research/fields 290); Inashiro and Mizuguchi join by a spur, Kashikawa and Sawada by a lane run on, Kuwabata by a branch to the polder dike (`meta.field_path`)
- DONE 2026-09-28 (269 B29): the grove's bamboo never drawn - 8% of the windbreak mix is bamboo, inked as culm marks where no crown covers it (research/vegetation 260; `GROVE_BAMBOO_SHARE`)
- DONE 2026-09-28 (269 fc:2261): the declared fixture prevalence not drawn - each declared share is seated as its count, a house with no room passing its fixture on (`meta.farm_fixtures_target`)
