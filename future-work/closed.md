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
- DONE 2026-09-27 (feature 261): one bank or both - ways cross the brook at a ford with a plank bridge, so a hamlet stands astride its own channel as the record attests at that size (research/questions/0035-villages-beside-their-stream-one-bank-or-both.html); not a knob, because the one-bank form belongs to a river and no hamlet map draws one
- RULED 2026-09-28 (the GM): no GM-only Obsidian Portal notes on a page, not now and not ever - the GM moves a note somewhere visible to show it; Ubame's post stays within one lineage (Moriguchi is its domain's only dynasty province)
- DONE 2026-09-28 (269 E4, B06): the dry-hem furrow variety cliff - the record (research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html) sets the row direction TRACT BY TRACT, not per plot, so the hem runs in tracts sharing one direction with a few degrees per plot and a turn of at least ~20 deg at each seam (`waterfields/furrows.py`), and `dry_plot_furrows_vary` judges tracts over every shipped hamlet; the per-plot maximize-separation rule and its blind radius are gone
- DECIDED 2026-09-28 (the GM, 269 B33): the dike-pond mulberry keeps the premodern spacing - the drawn ~23 sq ft a bush is the late-Qing mid-trunk figure (research/questions/0026-mulberry-and-other-crops-on-pond-dikes-sangji-guoji.html); the modern root-cut density is not used
- DECIDED 2026-09-28 (the GM, 269 B34; done in 269 E9): a hamlet's dikes roll mulberry, fruit or tea; cane, banana and vegetable dikes are retired as modern-only (research/contents.json#field-archetypes 230)
- DONE 2026-09-28 (269 B16): the byre on the inner commons or the outer fringe - neither; the record puts the beast with its household (research/contents.json#homesteads 300), drawn as the inner stable or a yard shed; what is left of the commons form is its own open entry
- DONE 2026-09-28 (269 B16): the byre at the settlement edge - no page read sites a byre there (research/contents.json#homesteads 300); closed with the entry above
- DONE 2026-09-28 (269 B17): how far past its last steading a way may run - an end serves a house at its dooryard or beside it within the gate's 60 ft, never past it (research/contents.json#ways; `trim_lane_stubs`); Sawada's and Kashikawa's run-outs moved
- DONE 2026-09-28 (269 B27): Kashikawa's woodland downslope - the woodland is seated beyond the fields and above the field it adjoins, never downslope of every house (research/contents.json#vegetation 140; `hinterland/parcels.py` `woodland_tier`)
- DONE 2026-09-28 (269 B28): woodland stocked like parkland - the commons coppice is stocked one crown per 64 sq ft at 8-9 ft (research/contents.json#vegetation 230; `COMMONS_SPACING_FT`, `CrownIndex`)
- DONE 2026-09-28 (269 B30): the belt and the copse share one crown vocabulary - the belt rolls conifer-led rows or mixed broadleaf (research/contents.json#vegetation 270; `windbreak_belt`)
- DONE 2026-09-28 (269 B04): where a field path ends, and the three pool maps with no spur - every way reaches the field ON its bund (research/contents.json#fields 290); Inashiro and Mizuguchi join by a spur, Kashikawa and Sawada by a lane run on, Kuwabata by a branch to the polder dike (`meta.field_path`)
- DONE 2026-09-28 (269 B29): the grove's bamboo never drawn - 8% of the windbreak mix is bamboo, inked as culm marks where no crown covers it (research/contents.json#vegetation 260; `GROVE_BAMBOO_SHARE`)
- DONE 2026-09-28 (269 fc:2261): the declared fixture prevalence not drawn - each declared share is seated as its count, a house with no room passing its fixture on (`meta.farm_fixtures_target`)
- DONE 2026-09-30 (293 task R): one dormitory or a door a household, for a compound's servants' rowhouse - both forms attested, a knob per compound (research/contents.json#compounds 910); Ubame's one door is the common-room form, accurate as drawn if its bay divisions read as sliding partitions (the sheet check stays open in compounds.md)

### Closed by the 2026-10-07 audit (the GM: "remove anything which should no longer be tracked as future work")

Each line is an entry that was still listed as open, with what closed it. DONE = the work landed; OBSOLETE = the code,
check or map it was about is gone or frozen; REDUNDANT = tracked where it belongs (`make claims-report`, or the record's
own guess and absence notes that `make open-questions` reads); HISTORY = never open work.

Farming communities:
- OBSOLETE: no way reaches a hamlet's burial ground - a hamlet draws none since 280 M68 (its dead lie in the village's ground); the path is now part of the village entry in `farming-communities.md`
- DONE (273, 272): the village generator draws no cremation ground - `_roll_cremation`, the ragged off-center glyph; the wayside stones folded into the village entry
- DONE (287 woods W25): the homesteads' woods fell short of their rolled area on every map; the lane-between-house-and-grove question kept as its own research entry
- DONE (287 water W36): a wild fan middle leaves a hamlet almost no dry field (269 B07) - `winter_crop` knob, `waterfields/hem.py` `dry_reserve`
- DONE (287): the rest of the 269 landing's settlement-review findings - a lane end behind a house counts as its dooryard (W57), a rolled form the sheet never draws (H33/H34), eaves woodpiles off the wall (H35), belt bamboo reads as grass (302), coppice lots read as stamped discs (W26), the burial ground beside the title placard (W58), a needle join (W21), a house at the edge of the lanes' reach (H16), the field path's canal deck runs onto the paddy (W13), a lane and the connector doubling back (W22)
- DONE (280): grow-out hamlet or fry village (269 B32) - `FRY_FORMS`, `FRY_VILLAGE_SHARE`
- REDUNDANT: the toe marsh rolls no alder-willow carr (269 K3) - claims report, `land/wet.py::marsh#marsh edge form`
- DONE (292, 319): record text that still describes the engine before 269 (K1-K5)
- DONE (287 homes H37): the web stops exactly one clearance short of the lane it should join
- DONE (287 ways W25): the field SPUR can be forced onto a house on tight clusters
- OBSOLETE: feature 126 cost ~50% of generation speed, undiagnosed - the derivation was rebuilt since, and a slower target fails the gate
- DONE (287 wave 6): 2b. the packer must RESERVE ways - the `access_refused` fallback deleted; 2b-i. the skeleton must follow the margin (`_margin_frame`); 2c. the way-repair passes want ONE design (the fragment residue, H40)
- DONE (319 H8, 280): 2e. `plot_regularity` is recorded as though rolled and is a literal - the record rules a hamlet's plots never in even rows
- HISTORY: 2f. the shallow-crossing veto must be STREAM-scoped (the measurements kept at `ways/checks.py` `stream_segs`)
- DONE (146, 287 M1/W13): the oblique-deck growth loop fails SILENTLY - `seat_deck` skews toward square, an unseated crossing raises
- DONE: review residue from the supply-bank hem re-roll (the sluice-gate glyph, 269 E5 `draw_intake`), the canal-B fork re-roll (all five DONE 2026-08-16) and the shared-bund re-roll (a tip-angle companion to the area floor: `DART_MIN_APEX` recorded, the arrowhead rule enforced, 287 T02/T13)
- DONE: cohort seed 62's northern lobe - the frame in the well score (`homesteads/wells.py` `_extent_added`), `crop_extent_added` (287 H12)
- OBSOLETE (302 retired the carve and the seam pass): the kept/dropped read along hemmed ditch banks; the flooded tint discriminates on truncation depth; cohort seeds 9 and 11, the carve after all; paddy bunds still step sideways - isolated steps and why each is refused (`_unjog`, `_seam_cuts`, `tools/jogs.py` gone)
- DONE (ca56fbc0b): the 2026-08-18 round - A. every woodland commons an axis-aligned square; C. `surface_water_dist` reads `channels` (RULED: an irrigation ditch is not domestic water); E. belt continuity ungated; G. two glyph-vocabulary collisions
- OBSOLETE: byres buried in canopy - no longer reproduces (at most 10 crowns within 40 ft of a byre, against ~45)
- REDUNDANT: the grazing commons are a tiling - claims report, `stage_hinterland#grass ground form`, `commons#grass ground forms`; the density that is actually available, and it is not the pitch - research 0038
- DONE (287 H44): seed 31's threshing yard laps a paddy
- DONE (230): the FLOODED paddy tint has collapsed to zero pool-wide - a map exhibits the class it declares
- DONE (287 H45): the kura roll under-delivers 2.2x - a count, `lot.larger_first`; the storehouse share is a positional roll; the storehouse against the farmhouse is rolled per house by position, not by size (293)
- DONE (150 T53, 287 H42): every lane junction draws a cap bead, and one back lane halves its width mid-run
- DECIDED (287 T13): the paddy area floor cannot see WIDTH - no basin width floor, the record contradicts one (`BASIN_MIN_WIDTH_FT` recorded, not enforced)
- DONE (287 labels L2/L5/L10): the notice-board caption's halo notches the lane it stands on; gate 0617's five caption notches; the 2D seat search; the caption clearance on a CURVED tread; attempts 8-13 (HISTORY)
- HISTORY: the copse that collapsed to one tree
- REDUNDANT: the south well stands in the commons - claims report, `place_wells#wells among the houses`
- DONE (137, 166): the tier under the T99 engine - `TRIPWIRE_EXPECTED` empty since 2026-08-31
- DONE (267 G8): is the in-field grave island attested? (0236); DONE (287 W28): carve the paddy around an in-field grave island
- OBSOLETE (166): two checks that pass VACUOUSLY; seed 45's windbreak pin needs the full cohort (287 removed `GATE_COHORT_EXPECTED`)
- REDUNDANT: the notice board's two knobs answer one question - claims report, `KOSATSUBA_SITINGS`, `kosatsuba_seat`
- DONE (287 woods W21): eight tree trunks stand in a tread on Moritono (frozen) / a tree stands in a path on the reference hamlet (the straggler pass dropped) - `stands.trunk_on_tread`
- DONE (287 W18): the windbreak's far limb, where a cluster sits in two groups - no longer reproduces (`trim_to_the_wind`)
- DONE: the drain that reaches its pond round a hook (230 pass 12); a garden may be seated on an in-field ditch (287, W53 guaranteed); the toe marsh's recorded outline is not the drawn marsh (287, W08 guaranteed); five finished-map rules no placer guarantees (287)
- DONE (287 water W09): the weir's root lands on the head race's mouth
- OBSOLETE (287): the straggler router pays a fresh search per rejected target
- REDUNDANT: where the dry hem stands once the houses move off it - the finding is on research 0006; the `hem_siting` knob belongs to a levee archetype the engine does not have
- REDUNDANT (the record's guesses): M43, the water-mouth grove's area (0071); Kuwabata's block holds less water than its parcels (0018); Kuwabata's fry village keeps sties on grow-out ponds only (0025)
- REDUNDANT (claims report): the free-standing storage shed is drawn on no scripted map (`KURA_PARTS#free-standing storage shed`); the record classes the storehouse annex two ways (`KURA_PARTS` north/west annex)
- DONE: two skeleton lanes on Kashikawa detour through open grazing - no lane on any pool map fails the entry's own test
- REDUNDANT: a shared byre's pocket can end up out of every household's borrowing reach - every shed is within `_BORROW_REACH` today; folded into the 269 B16 entry

Cross-cutting:
- DONE (283): FLAKY: the raster-mode wash test - green in every `make done` since 2026-09-28
- DONE (273): the review-prereq guard matches a finding's measurement by bare id
- DONE (42bbccaf8): 2g. the render cache serves a PNG made from a DIFFERENT SVG
- REDUNDANT: three members that are in `settlement/structures/` only because of where feature 025 cut, and feature 115's leftovers (civic_grounds/) - the moves are named at the point of change (`structures/CLAUDE.md`, `civic_grounds/CLAUDE.md`)
- OBSOLETE (166): the gate's 15 over-150-line segment functions; 8. `TWIN_AXES` believes a declared knob over the drawn shape (`declare_cluster_shape` derives the shape from the drawn aspect)
- HISTORY: the would-have-dispatched trail was empty for the whole period
- DONE (174): the hamlet coverage floor's last 128 lines; 2h. `make done FULL=1` HAS NEVER BEEN GREEN (a plain `make done` runs the full suite with the floors); re-pin `done`'s ratchet baseline (174, 192, 196)
- DONE (166, 266): the caption-over-a-building rule was cut, and its apparatus - the registry is consumed by the one placer (`overlap/taxonomy.py` `_LABEL_GROUP`, `structures/captions.py` `label_obstacles`); the stale mentions swept 2026-10-07
- DONE (172): `hooks-test` runs its suites SERIALLY
- DONE (1d8d0fc53): three magistracy SVGs have no generator
- OBSOLETE (263): a single fallback wakeup for a LOST harness notification - `wakeup-hooks.sh` refuses one outside a live /loop
- DONE (295, fa30940d5): a headless session stalls on the no-poll guard

Cities and towns:
- OBSOLETE: 1. parametric feature bundles (gate wards, rim bands) - a task for a next hand-authored map, which will not exist
- OBSOLETE (166, 266, 286): restore `labels_clear_of_other_buildings` - the one placer does what the check guarded, and the GM rules out a check on an automated process
- DECIDED 2026-10-07 (the GM): the capital goes straight to a scripted generator; Shiro Daika's hand pass is dropped. So 4. wall size settles first (a hand-authoring process rule), 5. interior fullness deferred on Shiro Daika and its addendum, and `wip/shiro-daika.gen.py`'s unbounded cost are closed; their design inputs moved to `cross-cutting.md` "Fabric-first generation"
- REDUNDANT (the record's drawing pages): the moat's width (0151), the gate range's guard room (0147), the ward blocks (0162), lower mansions at the outer town (0173); where a Chinese-model town seats its magistrate (0123); the T plan and the crank at a town's ends (0121, 0136)

Compounds:
- DONE (4f5c8f949): the rear strip is a knob, not yet declared - both forms in `docs/buildings/programs.md`; the servants' half is in the claims report
- REDUNDANT (the record's absence notes): every sheet's bed (0109); the shrine keeper's plot (0109); the silences the maps fill with a labeled guess; the garden wicket (0104)
- DONE (294): `building-review`'s contract names a wall-ink line the audit no longer prints
- DONE (280 M115): was the knee-high striking bundle an adult drill? - not drawn
- DONE (the record): what stood between Takayama's genkan and its working rooms (0104: a genkan-no-ma); were gangi cut back into the bank (0176: cut into the revetment); how often a grave in the fields (0236, calibrated liberty); where the ancestral tablets were kept (0239, the butsuma)
- DONE (280 R1): the glossary tooltip matcher picks up "shinden" in "Shinden Togashi" - the name has its own entry
- REDUNDANT (claims report): the barracks size band after the bunk rooms - `docs/buildings.md::Outer court#barracks`
- DECIDED 2026-10-07 (the GM): canon gaps (Ubame, Hayakawa, the Kurogi, Moriguchi, Nagahara absent from `l7r.md`) are not tracked here; each sheet's notes carry the particulars
- SETTLED 2026-09-26 (the GM): Ochiba's threshold stones are drawn ~3.3 by 4.7 ft ON PURPOSE - Ochiba is where the threshold stones are made and painted; canon's field stones are two fists. Ochiba's reception room faces the inner garden (its notes)
