# Tasks: Kuwabata, the Dike-Pond Hamlet, Scripted and Audited (150)

Checked off only when verified on Kuwabata (and Inashiro unchanged). T99 is the GM's alone.

## Phase 0 - the skeleton

- [x] T01 `spec-fidelity` review of spec.md against gm-request.md: round 1 three changes (FR-008 widened, the knob edge case split, FR-007 carries the FR-002 omissions), round 2 FAITHFUL - recorded in spec.md
      research: procedure
- [x] T02 the number claim pushed to main at 827bd8d6 (specs/ alone, route DIRECT; the feature otherwise stays in the clone until T99)
      research: procedure

## Phase 1 - research before the generator (constitution XII)

- [x] T10 the conversion's own research: where a dike-pond hamlet's houses stand, how the block is fed and drained, grid vs mosaic, the 6:4 ratio - the record already answers (research/archetypes.md 'Polder siting', 'A dike-pond is fed and drained through sluice gates', 'Grid vs mosaic', 'The 6:4 water-to-dike ratio'); this task confirms the pointers and lists what the generator will read from them
      given 2026-08-27T23:40Z | done 2026-08-28 (with T11) | runs: none (reads)
      research: physical
      - [x] research pass (the record's four entries, pointers above)  - [x] source-reader confirmed (the 2026-08-28 run: sluice, ratio, dredging, pond size all READ)  - [x] recorded and cited (research/archetypes.md, the four `Sources:` lines)
- [x] T11 source the four dike-pond entries the conversion rests on whose `Sources:` line reads "not recorded" (v2.10.0): find and read the sources, register them in SOURCES.md, mark SUMMARY-ONLY where the page could not be read
      note: sourced - ratio (`gd-gazetteer-sangji` READ, `fao-ac241e` READ), sluice (`fao-x6708e` READ), pond size/dike width (`isis-dykepond` READ carrying `ruddle-zhong-1988` SUMMARY-ONLY: 403 on every host), grid-vs-mosaic (`mdpi-3860` SUMMARY-ONLY, 403). The coppice density was not re-found: on the re-sourcing queue. The first research agent hung 8+ h and never returned; the pass was redone in-session (parallel fetches) and verified by `source-reader` (2 min)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited

## Phase 2 - the conversion

- [x] T20 the archetype in the spec and the plan: `mulberry_dike_fishpond` in FIELD_ARCHETYPES (not ROLLED), cardinal falls, the per-archetype polder table (cell, parcel mix, gap, mosaic), `pond_layout` as a rolled knob with Kuwabata pinned to mosaic; tests in tests/hamletgen/test_plan.py
      given 2026-08-27T23:05Z | done 2026-08-27T23:40Z (with T21-T24; one sitting) | runs: quick x4, map x4, hamlet x3, family-census x2, gate-manifest x4
      note: the record already answered every number (`build_polder` TRUE-SCALE SIZING, research/archetypes.md 'Grid vs mosaic', 'The 6:4 water-to-dike ratio'); `POLDER_FABRIC`, `POND_LAYOUTS`, `DIKEPOND_CONVERSION` carry the why. The source-reader box is owed with T11: those entries' `Sources:` lines read 'not recorded'
      research: physical (the numbers are the record's: build_polder TRUE-SCALE SIZING, research 'Grid vs mosaic')
      - [x] research pass (the record: pointers above)  - [x] source-reader confirmed (T11's run)  - [x] recorded and cited (T11)
- [x] T21 the stage: `stage_polder` parameterized by the table; the dike-pond path applies the wholesale overlay, declares `field_archetype` / `pond_layout` / `waterward`, draws the waterward reed fringe; every `== "polder_grid"` in the generator becomes `is_polder(plan)`; footbridge caps on the dike-pond ring
      note: three defects met and fixed here (XIV): the windbreak drew over the header reservoir (`village_grove` had no pond keep-out); `_touch_junctions` closed a 30 ft lane onto its own start (a 28 ft loop, `lanes_bend_like_paths`); the fringe first went in the hinterland and was drawn over an already-routed connector (`roads_clear_of_marsh`) - now its own stage after the seat. The seams check stands aside for dike-pond fabric (two rings a dike apart ARE the system). Crossing caps: village on a toe flank -> that toe 3, far toe 0; at the head or foot -> both toes 2 (a capped-to-zero toe was a long ditch with no plank)
      research: physical (research 'Polder siting', 'Polder ring canal' crossings)
      - [x] research pass (the record: research/archetypes.md 'Polder siting', settlements.md 'Polder ring canal')  - [x] source-reader confirmed (T11's run; 'Polder siting' carries shen-kuo / fei-xiaotong)  - [x] recorded and cited (T11)
- [x] T22 Kuwabata's pool entry is a declaration (`HamletSpec(name="Kuwabata", seed=..., households=16, down_deg=90, field_archetype="mulberry_dike_fishpond", pond_layout="mosaic")`); the hand-authored script retired (git history keeps it); renders un-tracked (`git rm` svg/png, drop the `.gitignore` `!` lines - dev/pool.md); kuwabata.notes.md rewritten for the scripted map; migration-plan.md status table updated
      note: `kuwabata.gen.py` is 4 lines of declaration + docstring; svg/png untracked, the two `!` lines dropped from .gitignore; notes.md rewritten; migration-plan.md FITTED
      research: rendering
- [x] T23 the map generates and the gate passes: `make map GEN=pool/hamlets/kuwabata.gen.py`; the three `pool/regressions/*kuwabata*` fixtures still fire; any blocker met (the polder title/belt one included) fixed here (XIV)
      note: gate OK on the first roll after the fixes above; the three `pool/regressions/*kuwabata*` fixtures are frozen manifests the gate replays (unchanged)
      research: rendering
- [x] T24 the feature-family census: `tools/family_census.py` + `make family-census`; Inashiro vs Kuwabata; every absence classified in spec.md Decisions Recorded with its research pointer; Inashiro's manifest byte-identical before/after (`make reference` + diff)
      note: the family census: 37 families/kinds in both; Inashiro-only `dry_plots`, `field_ditches:branch`, `field_ponds` (all archetype-absent, spec Decisions Recorded); Kuwabata-only the dike-pond families. `git diff` on inashiro.json: empty
      research: rendering
- [x] T25 knob maps owed: one map per `pond_layout` value (grid, mosaic) rolled one at a time with `make map GEN=` under the lock; `make done` (locked) green; the deferred sweeps (polder cohort, tripwire, perf bookends) recorded here as OWED at unlock with their commands
      note: mosaic = the pool map; grid = the hamlet target with `--name Kuwabata --seed 21 --households 16 --down-deg 90 --archetype mulberry_dike_fishpond --pond-layout grid --out wip/kuwabata-grid` (gate OK; wip renders are gitignored). OWED AT UNLOCK: the cohort with polders in the mix (the polder archetypes' promotion bar), the tripwire, the perf bookends (feature 129), the 33 deferred map-rolling tests (the unlocked gate)
      research: procedure

## Phase 3 - the audit (present, do not implement)

- [x] T30 the dike-pond research pass: what stands on a silk-and-fish hamlet that a paddy hamlet lacks, and which paddy features a no-rice hamlet should lack (search-pass agent, then `source-reader` on every claim)
      given 2026-08-27T23:09Z | done 2026-08-28 | elapsed: 8+ h of it a hung search agent (never returned; the pass redone in-session in ~25 min, 4 parallel fetch/search turns) | runs: source-reader x1 (Sonnet, 11 fetches, 2 min)
      note: Fei 1939 READ in full locally (the one primary silk-village ethnography); Ruddle & Zhong SUMMARY-ONLY throughout (403 everywhere); pond huts NOT SUPPORTED after two searches
      research: physical
      - [x] research pass  - [x] source-reader confirmed (every non-Fei claim READ verbatim; the Fei quotes READ by the session from the full text - the reader's fetch truncates the book, recorded in SOURCES.md)  - [x] recorded and cited (research/archetypes.md 'What stands on a dike-pond hamlet...'; SOURCES.md 11 keys)
- [x] T31 the record: research/archetypes.md gains the findings with `Sources:` lines; SOURCES.md the keys; `specs/139-.../audit.md` the gap list (prevalence, source, drawability), the not-owed list, and the should-be-absent list
      note: `specs/150-kuwabata-dike-pond-hamlet/audit.md` - six candidates (A1 creek + boats + landing the strongest), one should-be-absent (B1 the threshing yard on a no-rice hamlet), six not-owed, the three archetype absences (D), the holding figure (E)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited
- [x] T32 present to the GM and STOP: the generated map's path, the census, the audit list; `settlement-review` of Kuwabata launched in the background at this hand-back (dev/reviews.md: at acceptance, never per task); no item of the audit implemented (FR-007, FR-008)
      note: settlement-review FULL (2026-08-28, docs/review-ledger.md): needs-work -> four errors fixed here (XIV): `polder_crossing_caps` now puts the planks on the collector the village abuts (head -> feeder 3, foot -> drain 3, toes 1 each; the first cut satisfied `long_ditches_have_a_footbridge` with every plank 350-1,100 ft from the houses); `_title_obstacles` gains wells and the notice board (the placard sat on the east well); the board's seat search probes the caption at its TILT (a -32 degree caption reached a yard the level box cleared). Its "no sluice-gate glyph at the dike cuts" is a NEW glyph -> audit.md A7 for the GM; "leftover cells as stubble not rice" -> audit.md B2. `scatter_audit` is archetype-blind on dike-pond fabric (bank crowns read as crowns-in-crop): OWED, a tool fix. Main's interactive feature (its own 134) landed meanwhile: every dike-pond ink is now ruled on - four classes added to the registry, its test and its spec table (fish pond, mulberry dike, pond sluice, perimeter dike), each written FROM the research with sources
      research: procedure
- [x] T33 **the hung-agent guard** - the GM (2026-08-28): *"can you add something to catch hung agents next time?"* - built here as `scripts/agent-watch-hooks.sh` (Stop hook refuses once per pending agent and hands over the watchdog; `watchdog` exits on finish/stall so the session is re-invoked; prompt hook flags stale agents) + `test-agent-watch-hooks.sh` (18 cases) + settings.json. **RETIRED at the merge on 2026-08-29**: feature 143 answered the same ask in another session and landed on main first, so `scripts/agent-stall-hooks.sh` is the guard and this one was dropped - the reasoning, and what carried over (`pending`), in docs/iteration-loop.md
      research: procedure
- [x] T34 renumbered 134 -> 139: a peer session landed `134-interactive-html-map` on main after this feature's number claim (827bd8d6) without renumbering; every reference in this feature's files moved to 139 (138 is a peer's unpushed claim)
      research: procedure

- [x] T35 **a green locked gate on the FINAL tree** - was OWED; green 2026-08-28 (make-done-8, 3,928 passed; the browser tests passed on a quieter box). The last two `make done` runs (2026-08-28) went red only on tests/interactive/test_page_browser.py (main's feature-134 page): run 1 `load took 6596 ms` against a 5 s budget, run 2 `Page.evaluate: Target crashed` twice - the headless Chromium renderer killed under 22 xdist workers on a box with 4.6 GB free (other sessions running). Both tests pass alone in this clone (9 passed, 60 s) and the CI tooling test that also flaked in run 1 passes alone here and on unmodified main. Not a regression of this delta (nothing here touches the page); it is the environment. Re-run `make done` when the box is quiet; if the crash recurs on a quiet box, the fix belongs with the browser fixture (a relaunch on "Target crashed", or a memory-aware worker count for that file). The green run that DID cover this feature's engine content is the third run (make-done-3, 3,768 tests, before main's browser tests were merged in)
      research: procedure

## Phase 4 - the GM

- [x] T40 **A1 DECLINED - the creek and boats are not drawn; the documentation stops implying Kuwabata has one (the connector lane is its market link, to the market or to the water that carries it)** - the GM (2026-08-28), on audit.md: *"With regards to the creek along the landward flank, I understand that the real world place that this is based on had one, but would it necessarily be the case that any settlement of this sort would have one. I wouldn't think so. As such, I don't think that we should push to include it, and I think we can update the documentation for the specific settlement to not imply that it will have one. In particular, because there is a lane leading away from the settlement, then we can presume that that is either connected to the market itself or that is what leads to the stream or river that is the water market or is connected to the water market. I do like all of the other options, though. In particular, thrashing yards on a no-rice hamlet seem bad and should be eliminated. That seems like the most egregious thing on the map, which is wrong. But I think I do like literally every other option there Even if one or more of them is a tunable knob, which would not necessarily be enabled on this specific map. I would therefore like for you to proceed with all of the items you listed from your audit. Thanks."*
      given 2026-08-28T12:56Z | done 2026-08-28 (T40-T48 in one sitting, ~3.5 h; the yards took most of it - two web experiments were reverted after they moved the reference hamlet) | runs: quick x14, map x18, hamlet x6, gate-manifest x8
      research: rendering

- [x] T41 **B1 - no threshing yards on a no-rice hamlet: the dike-pond archetype's farmsteads carry no threshing yard** - same instruction (T40)
      given 2026-08-28T12:56Z | done 2026-08-28 (T40-T48 in one sitting, ~3.5 h; the yards took most of it - two web experiments were reverted after they moved the reference hamlet) | runs: quick x14, map x18, hamlet x6, gate-manifest x8
      research: physical
      - [x] research pass (the T30 pass; research/archetypes.md audit section)  - [x] source-reader confirmed (the T30 run)  - [x] recorded and cited (the class entries name their sources; settlements/archetypes.md carries the rules)

- [x] T42 **A2 - the manure fixture rolls `heap | pit` per hamlet; the pit is a half-buried earthenware jar behind the house (and along the road), a new glyph and class** - same instruction (T40)
      given 2026-08-28T12:56Z | done 2026-08-28 (T40-T48 in one sitting, ~3.5 h; the yards took most of it - two web experiments were reverted after they moved the reference hamlet) | runs: quick x14, map x18, hamlet x6, gate-manifest x8
      research: physical
      - [x] research pass (the T30 pass; research/archetypes.md audit section)  - [x] source-reader confirmed (the T30 run)  - [x] recorded and cited (the class entries name their sources; settlements/archetypes.md carries the rules)

- [x] T43 **A5 - fry ponds: a few of the block's smallest parcels are designated fry nursery ponds in the manifest, with a class of their own for the interactive map** - same instruction (T40)
      given 2026-08-28T12:56Z | done 2026-08-28 (T40-T48 in one sitting, ~3.5 h; the yards took most of it - two web experiments were reverted after they moved the reference hamlet) | runs: quick x14, map x18, hamlet x6, gate-manifest x8
      research: physical
      - [x] research pass (the T30 pass; research/archetypes.md audit section)  - [x] source-reader confirmed (the T30 run)  - [x] recorded and cited (the class entries name their sources; settlements/archetypes.md carries the rules)

- [x] T44 **A7 - a sluice-gate glyph at the two perimeter dike cuts (boards across the gap), a new glyph and class** - same instruction (T40)
      given 2026-08-28T12:56Z | done 2026-08-28 (T40-T48 in one sitting, ~3.5 h; the yards took most of it - two web experiments were reverted after they moved the reference hamlet) | runs: quick x14, map x18, hamlet x6, gate-manifest x8
      research: physical
      - [x] research pass (the T30 pass; research/archetypes.md audit section)  - [x] source-reader confirmed (the T30 run)  - [x] recorded and cited (the class entries name their sources; settlements/archetypes.md carries the rules)

- [x] T45 **A3 - a pig sty on a pond dike (or over the water) beside the village, a new fixture kind, position and class; a per-hamlet share** - same instruction (T40)
      given 2026-08-28T12:56Z | done 2026-08-28 (T40-T48 in one sitting, ~3.5 h; the yards took most of it - two web experiments were reverted after they moved the reference hamlet) | runs: quick x14, map x18, hamlet x6, gate-manifest x8
      research: physical
      - [x] research pass (the T30 pass; research/archetypes.md audit section)  - [x] source-reader confirmed (the T30 run)  - [x] recorded and cited (the class entries name their sources; settlements/archetypes.md carries the rules)

- [x] T46 **A4 - a duck pen at a pond corner: a fenced dry run on the dike and a wet run in the water, a new fixture and class; a per-hamlet share** - same instruction (T40)
      given 2026-08-28T12:56Z | done 2026-08-28 (T40-T48 in one sitting, ~3.5 h; the yards took most of it - two web experiments were reverted after they moved the reference hamlet) | runs: quick x14, map x18, hamlet x6, gate-manifest x8
      research: physical
      - [x] research pass (the T30 pass; research/archetypes.md audit section)  - [x] source-reader confirmed (the T30 run)  - [x] recorded and cited (the class entries name their sources; settlements/archetypes.md carries the rules)

- [x] T47 **A6 - the dike crop as a rolled knob `mulberry | sugarcane | banana | fruit` (a hamlet TYPE, not a mix); Kuwabata pinned to mulberry; three new plant glyphs and classes** - same instruction (T40)
      given 2026-08-28T12:56Z | done 2026-08-28 (T40-T48 in one sitting, ~3.5 h; the yards took most of it - two web experiments were reverted after they moved the reference hamlet) | runs: quick x14, map x18, hamlet x6, gate-manifest x8
      research: physical
      - [x] research pass (the T30 pass; research/archetypes.md audit section)  - [x] source-reader confirmed (the T30 run)  - [x] recorded and cited (the class entries name their sources; settlements/archetypes.md carries the rules)

- [x] T48 **B2 - the leftover cells as a rolled knob `rice | vegetables | pond` (residual paddy, vegetable ground, or full conversion); Kuwabata's value rolled** - same instruction (T40)
      given 2026-08-28T12:56Z | done 2026-08-28 (T40-T48 in one sitting, ~3.5 h; the yards took most of it - two web experiments were reverted after they moved the reference hamlet) | runs: quick x14, map x18, hamlet x6, gate-manifest x8
      research: physical
      - [x] research pass (the T30 pass; research/archetypes.md audit section)  - [x] source-reader confirmed (the T30 run)  - [x] recorded and cited (the class entries name their sources; settlements/archetypes.md carries the rules)

- [x] T49 knob maps for every new knob value (one map per value, `make hamlet ... --out wip/...`), `make done`, `settlement-review` at the hand-back; a green gate on the final tree (folds T35)
      note: wip/kuwabata-{grid,manure-heap,cane,banana,fruit,leftover-rice,leftover-pond} all OK; the locked gate green on the final tree (3,928 tests; make-done-8); DELTA settlement-review 2026-08-28 needs-work -> fixed (docs/review-ledger.md); T35's browser-test reds did not recur on the quieter box
      research: procedure
- [x] T50 **no farmhouse or garden on marshland** - the GM (2026-08-28), reviewing the map: *"I see multiple farmhouses on that map that appear to overlap with marshland. Is that realistic? looks like a mistake to me. one of the gardens also appears to be on marshland. at least partially, which also looks like a mistake. I think we need to update our placement algorithms to make that impossible. The irrigated channel which feeds into the water for everything stops short of actually being connected to the feeder pond. This is clearly a mistake, and we should update our placement algorithm to make this work. Similarly, there is a spot close to the top left of the rectangular boundary of irrigated channels which run along the edge of the ponds which does not plate connect. It stops just short of connecting. This is clearly a mistake and should be corrected in our placement algorithm. This last issue is just a Glyph rendering convention, but I think it is an important one because of how awkward it looks. When two village lane segments intersect, they are currently doing so very awkwardly. I can see the manner in which They come together such that it looks like one of them is literally just rendered on top of the other at the place where they intersect. This is not how actual roads or even dirt paths come together. It should look as if they are all essentially one contiguous structure even if under the hood they are implemented as if they are separate lanes. Therefore, we need better rendering of the places where these things intersect with one another. [...] The same thing also applies incidentally to any place where our water sources meet. So when a stream meets a irrigated channel or where an irrigated channel or a ditch meets a pond, where right now it clearly looks like one is rendered on top of the other where they intersect, which again is not what we want because water just flows. [...] This is not specific to this map and is a fix which I expect to apply to all maps when you make it. One particular place where I think our rendering conventions need to accommodate this is that we appear to have a convention in which a dark blue line is drawn around the edge of a pond, but then that means that when a stream or channel intersects with it, then it is running into a solid blue line, which makes it look like there is some sort of obstruction present. [...] where two bodies of water come together, such as an irrigated channel and a pond, then at the point where they intersect, the dark blue outline should not be present at the place of their intersection, thus ensuring that there is a continuous flow of water."*
      given 2026-08-28T16:28Z | done 2026-08-28T22:40Z | elapsed ~6 h (one session, the web re-solve cost most of it) | runs: make map x20, make maps x3, make done x1
      research: physical
      - [x] research pass (the record already answers it: a reed fringe is wet ground, not building ground - `hamletgen/cluster.py` seat rules HARD 1/2 and `settlements/water.md` "DWELLINGS keep OFF the wet low TOE", research/water.md `toe_band`; the GM's own instruction settles the rest)  - [x] source-reader confirmed (no new source: an existing rule extended to the fringe polygon)  - [x] recorded and cited (`settlement/land/wet.py` `marsh`, `settlement/houses.py` `_hard_ground`, `hamletgen/cluster.py` `seat_cluster` wet_foul, `pool/hamlets/kuwabata.notes.md`)
      outcome: the marsh polygon registers as hard ground (`wet_polys`) so no house/garden/yard footprint passes `_hard_clear` on it, AND the cluster seat scores wet ground so the cluster stands clear of the reeds rather than losing two houses to far seats; declined levers recorded in kuwabata.notes.md; Inashiro byte-identical (z-index fields aside)
- [x] T51 **the inlet channel reaches the feeder pond** - same instruction (T50)
      given 2026-08-28T16:28Z | done 2026-08-28T22:40Z | elapsed ~6 h (one session, the web re-solve cost most of it) | runs: make map x20, make maps x3, make done x1
      research: rendering
- [x] T52 **the ring canal's top-left corner connects** - same instruction (T50)
      given 2026-08-28T16:28Z | done 2026-08-28T22:40Z | elapsed ~6 h (one session, the web re-solve cost most of it) | runs: make map x20, make maps x3, make done x1
      research: rendering
- [x] T53 **junctions render as one continuous structure - lanes meeting lanes, water meeting water, a channel entering a pond through its outline - on every map** - same instruction (T50)
      given 2026-08-28T16:28Z | done 2026-08-28T22:40Z | elapsed ~6 h (one session, the web re-solve cost most of it) | runs: make map x20, make maps x3, make done x1
      research: rendering
- [x] T54 **no marsh ink on the earthen mounds** - the GM (2026-08-28), reviewing the map after T50-T53: *"Okay. That looks a lot better. However, I am now seeing another issue, which is that it looks like the marshland overlaps with the earthen mounds, which surround all of the ponds. like the hazy blue that denotes the marsh is clearly overlaid on top of the greenery of the earthen mounds. In some cases, it seems to even extend past them. this seems like a relatively straightforward change to the placement rules will fix it."*
      given 2026-08-28T23:05Z | done 2026-08-29T00:35Z | elapsed ~1.5 h | runs: 6 map rolls, 1 tier sweep, 5 quick runs, 1 gate
      research: physical
      - [x] research pass (the record already answers it: `research/archetypes.md` "a wei-tian / dike-pond dike was dredged pond-mud heaped and packed (the dig-and-pile cycle), trapezoidal in section, PLANTED with mulberry/willow" and "a bare bank of heaped dredge-mud is a liability ... so planting the dike was the standard remedy"; `settlements/archetypes.md` "Polder waterward fringe": the un-reclaimed fluctuating wild lies OUTSIDE the dike. Reeds root in shallow standing water; a maintained, cropped embankment is not that ground, so wet ground abuts a mound and never crosses it)
      - [x] source-reader confirmed (no new source read: an existing, already-read finding applied to a new rule)
      - [x] recorded and cited (`settlement/land/wet.py` `marsh` keep-out, `hamletgen/water.py` `dike_face` + `stage_waterward`, `settlements/water.md`, `pool/hamlets/kuwabata.notes.md`, the spec's Decisions Recorded)
      outcome: no reed blade, glint or wet-tint circle of any marsh role touches a perimeter dike band or a fish pond's mulberry bank on any map (structural check on Kuwabata's own ink: 0 of 11,299 tint circles, 0 of 98,928 blades, 0 of 3,260 glints), and the waterward strip's inner edge FOLLOWS the dike's outer face, so nothing extends past a mound either; Inashiro byte-identical

- [x] T55 **a vegetable ground may not overlap the channels beside it** - the GM (2026-08-29), reviewing the map after T54: *"Looks great!  The only issue I see now is that one of the vegetable grounds overlaps with the irrigated channels which run between the vegetable grounds and the ponds.  So the placement rules should be updated to fix this."*
      given 2026-08-29T01:20Z | done 2026-08-29T03:10Z | elapsed ~1.9 h | runs: 12 map rolls, 6 quick runs, 1 baseline worktree, 1 gate
      research: rendering
      outcome: a channel that CROSSES a parcel now cuts it (the strip beyond the ditch was never that
      holding's ground) and the remaining outline is projected onto the band's edge, so it follows the
      channel's own curve and keeps its wander everywhere else. Measured on Kuwabata: 335 channel-stroke
      samples inside a parcel -> 0, with the leftover vegetable ground the GM saw the worst of them.
      Priced and declined, both measured: PUSHING every outline point off the band (the parcel swallowed
      the ditch whole - 45 samples became 133) and CLIPPING by half-planes along the run (cleared the
      water but straightened the wandered edges, failing `polder_parcels_are_organic`, and cost 3.4% of
      the block's acreage).

- [x] T99 **the GM accepts the scripted Kuwabata** - tickable only on the GM's explicit word, recorded here verbatim. Never ticked by a session.
      given 2026-08-27 | done 2026-08-29T06:40Z | the GM's word, verbatim: *"Please do the small follow-up
      now as well as the second open item about writing the one shared helper. Thanks. after you have done
      those things. then you can mark feature one three nine as accepted and merge it all back into main.
      Thanks."* (2026-08-29, after the T50-T55 rounds and four settlement-review passes.)
      research: procedure

## The 2026-08-29 settlement-review: three fixed here, three DEFERRED with their measurements

- [x] D0 the three deferrals below recorded with their measurement, mechanism and sketch (Principle XIV)

The delta review of the re-rolled Kuwabata (after the merge onto main) returned `needs-work` with six
errors. Three are fixed in this feature (see the commits); three are DEFERRED under Principle XIV's
one exception, and a deferral here is a deliverable rather than a shrug - each carries the
measurement that establishes the defect, the mechanism, and an implementation sketch.

The three below are **not done**. They are recorded here so the next session inherits the
measurement instead of re-deriving it, and they are written as prose rather than open task boxes on
purpose: this feature IS finished, and an open box in a landed spec would (correctly) refuse every
future push under `sync-with-main.sh`'s in-progress rule. Each is owed its own feature.

**Fixed here.** Error 6 (the marsh hit polygon over the mulberry banks - the record half of the GM's
own T54 complaint); error 3 (the reed fringe reading as a bare blue plate); error 2 (the crossing
knot and its 3.1 ft nub, closed by `drop_end_nubs` - and the 22 ft overrun went with it: the
connector now leaves the crossing cleanly and lane 5's run past it measures 87 ft, which is a route
rather than a hook).

**D1.A 10 ft woodpile severs the back lane, and no test can see it** - MEASURED on Kuwabata:
      `lanes[1]` head (2354.4, 585.6) and `lanes[2]` tail (2358.6, 610.2) point at each other across
      **25.0 ft** of bare ground, both drawn as rounded caps; the only thing between them is a
      woodpile, 10 x 3.5 ft, at (2351.3, 600.5), **5.6 ft** off the line. Everything else is 21 ft or
      further. MECHANISM, traced: `_touch_junctions` reaches it (25 ft is inside `_LANE_JOIN_FT` =
      30), `_clear_touch` refuses the straight link, and BOTH router attempts return `[]` - the
      standard one (`pad_mult=2.0, cell=10.0`) and the tighter fallback added here
      (`pad_mult=1.0, cell=5.0`). The router is not wrong: `_plan_gap` = `WEB_FABRIC_GAP` + 0.71 x
      cell = **10.6 ft**, so a way may not pass within ~10.6 ft of the woodpile, and the corridor
      offers 5.6. Every endpoint-reach check passes because each piece reaches the network at its
      OTHER end, so `lanes_form_one_network`, `lanes_reach_something` and the rest are all green over
      a severed back lane. SKETCH: this is a STAGE-ORDERING fix, which is why it is deferred - the
      fixture is placed before the web and cannot know a lane will want that ground. Either the
      homestead's small fixtures are seated after the web with the lane corridors as a keep-out (the
      reviewer's "a woodpile is the cheapest thing on a homestead to move"), or a fixture yields when
      a link within the join reach is blocked by it alone. Do NOT fix it by narrowing
      `WEB_FABRIC_GAP`; that number is load-bearing and its three reverted widenings are recorded at
      `_clear_touch`. *(research: rendering)*

**D2.The windbreak belt shelters 3 of 16 houses; half its own canopy is never drawn** - MEASURED:
      `village_groves[0]`'s belt polygon is 554 x 509 ft, the drawn canopy is 38 clumps in a
      186 x 147 ft corner, and a further **24 clumps sit in `clumps_offpage`** and are never drawn.
      Across-wind the cluster spans 437 ft and the drawn belt 218 ft - **50%** of the frontage it
      exists to shelter; **13 of 16 houses have no clump within 150 ft**, the gate's own embrace
      radius. MECHANISM: the band is offset into the wind from the house **centroid** and sized across
      the wind, but `meta.cluster_shape_unhonored = "round"` with `cluster_aspect_drawn = 2.44` - the
      seat wanted a round cluster and got a 486 x 212 ft east-west ribbon, so the band lands ON the
      ribbon's north-east half (where the per-crown filter deletes every crown) and its south-west
      quarter lands on the reservoir. `village_windbreak_embraces_cluster` passes because it asks only
      that a substantial belt be within 150 px of A farmhouse, which the western remnant satisfies.
      SKETCH: derive the belt's extent from the drawn cluster's windward HULL rather than an offset
      from its centroid, so an elongated cluster gets an elongated belt; and when clumps are refused,
      refuse the BAND POSITION rather than the canopy. Deferred because it redesigns the belt placer
      and moves the windbreak on every hamlet in the pool. *(research: physical - a windbreak's extent
      relative to what it shelters is a fact about how these were planted)*
      The physical question it opens - a windbreak's extent relative to what it shelters - owes the
      research pass, a `source-reader` confirmation and a citation when it is taken up.

**D3 (SINCE RESOLVED ITSELF ON THIS MAP - do not implement the sketch against today's Kuwabata).**
The re-check review of 2026-08-29 found the re-rolled caption wrapped to two lines at rot -43.1, and
its rotated quad now laps nothing: the 78.1 sq ft overlap into the garden at (2427, 620) is gone.
The mechanism below is unchanged and will recur, so whoever takes this up needs a map that still
shows it. **A caption is seated with no regard for anything but lanes** - MEASURED: `labels[0]`
      ("notice board") rotates to corners (2428.6, 613.5), (2465.9, 576.2), (2471.8, 582.1),
      (2434.5, 619.4); the first lies INSIDE the garden of the house at (2384.7, 590.1), and the box
      laps that garden by 12.3 x 13.0 ft and the persimmon at (2425, 593) by 5.1 x 18.0 ft.
      MECHANISM: `pick_caption_seat` filters on `hug` and on `_box_clearance`, and `_box_clearance`
      measures **only the drawn ways**. The comment at the satisfice rule already names the symptom -
      "a copse clump through the text" - and chose lane clearance as the bar anyway. Nothing else owns
      it either: the check that would have caught it was retired in main's battery rebuild, and the
      seven surviving label checks are about ways, alignment, the frame and label-vs-label. So by the
      GM's own rule (2026-08-29) this belongs to the PLACER, not to a new check - no single placement
      rule is responsible for it today, which is exactly the case a scorer must take on. SKETCH: add a
      fabric term to the legality filter - a seat is legal when its ROTATED quad (the `_hug` closure
      already computes one; `_box_clearance` does not) laps no `_LABEL_GROUP` member it does not name -
      keeping the satisfice-then-nearest tie-break. Deferred because it moves a caption on every map
      in the pool and each one then owes a review. *(research: rendering)*

## The pool sweep of 2026-08-29: what it fixed, and what it found that this feature did not cause

Four `settlement-review` passes ran over the maps the merge re-rolled (Inashiro, Kashikawa,
Mizuguchi, Sawada), because `lanes`, `farm_fixtures`, `drawn_channels`, `streams` and
`bamboo_stands` all moved on all four under an unchanged `.gen.py`. Fixed in this feature:

- [x] P1 **A regression this feature caused.** Putting every watercourse in ONE block (T53) left every
      sheen above every bed, so a sheen's ROUND CAP printed inside whatever its course ran into - a
      pale blob on the head-race at Mizuguchi's intake, the join the hamlet is named for. Measured
      across the pool before fixing: a stream sheen lies under a later-drawn bed for **0.1 to 4.3 ft
      per map** - cap-sized at joins, never a long run - which is why the CAP is the fix and the block
      order is not. Sheens are butt-capped now. *(research: rendering)*
- [x] P2 **The reed fringe was thinnest exactly where the record says reeds are thickest.** The pad
      holding reeds off the water was the mark's isotropic reach (7 ft), so tufts stood 7.66 ft off
      the waterline and the density profile out from Mizuguchi's rim ran 12.0 / 27.4 / 33.0 / 24.4 per
      1,000 sq ft. But a reed tuft's blades are drawn near-VERTICAL - ~7 ft up, at most ~1.4 ft
      sideways. The pad is split: lateral reach for the tuft's own point, and the blade TOP tested
      separately, so a tuft south of the pond still keeps its height back while one beside it stands
      at the rim. After: nearest base **7.66 -> 1.52 ft**, rim band **12.0 -> 21.2**, profile
      21.2 / 29.3 / 35.9 / 21.8 / 22.5, and **0 blades in the water**. Grounded in the research pass
      recorded at research/water.md, not in a preference. *(research: physical - already researched,
      confirmed and cited in this feature)*
- [x] P3 **The title placard was translucent** at `fill-opacity="0.94"` and the ground cover ghosted
      through it - 6,900 of 79,772 interior pixels on Kashikawa, 8.65%, with grass, brush dots and two
      whole pine glyphs legible at native resolution. Identical defect and identical fix to that map's
      own field grave eight days earlier. Opaque now. *(research: rendering)*
- [x] P4 **The scalebar's recorded box was the placard's foot, not its ink** - over-claiming 26 px,
      41% of its own height, and reaching 12 px BELOW the placard containing it. Nothing keeps out of
      that box, so the over-claim bought nothing and cost the interactive map, which highlights it.
      Derived from the drawn extents now. *(research: rendering)*

**Found by the sweep, NOT caused by this feature, and left alone** - each is byte-identical to main's
tip, so fixing it here would put an unreviewed change into a merge that is already large. Recorded so
the next session inherits the measurement:

- **Kashikawa lane 0 ends in bare ground reaching nothing**: its north end (2401.4, 2453.7) stands
  206.1 ft from any other lane and 246.5 ft from the nearest farmhouse corner, blunt-capped in open
  grazing, the outer half of a 229.8 ft run serving nothing. `lanes_reach_something` is green on it,
  which is the gap a reviewer exists to close.
- **Mizuguchi's through-route necks 6 ft -> 3 ft -> 6 ft for 11 ft** at (933-944, 1778-1780): lane4
  and lane3 never meet, and the only ink joining two 6 ft lanes is 11.1 ft of a 3 ft back lane, capped
  at both ends. Measured tread depth 9.5 / 3.2 / 7.6 ft across the waist. Feature 124's rule ("a
  healing link inherits the width of the way it joins") did not apply because here the WIDE lane joins
  the THIN one.
- **Mizuguchi's "copse" is two trees** - `village_groves[1]`, 205.4 x 58.5 ft, r=11, 2 clumps 175 ft
  apart, both inside the windbreak's own canopy. A feature that draws degenerate should be placed
  properly or dropped, the way woodland parcels under the legibility floor already are.
- **Kashikawa's homestead fixture ring is stamped, not composed**: 13 of 20 farmhouses carry the row
  at dy -18 to -21 ft, privies at bearing 31-41 deg at 10 of 13, and at 3 of 4 manure homesteads the
  pit sits 9.5 ft directly above the privy with x agreeing to 0.7 ft. The arrangement is right; the
  VARIANCE is zero. This is calibrated liberty (a degree, not a knob) and the degree is currently nil.
- **Kashikawa's notes carry an accepted limitation that is not on the map** - a board caption clipping
  "the byre's roof by 15.4 x 4.8 ft" at (2003, 2838), where no byre stands within 167 ft in this
  manifest or main's. A future session will quote it as a live cost.
- **A knob candidate, not a defect**: where a kosatsuba stands. Mizuguchi's is at the western wellhead
  (7 of 12 houses within 250 ft) rather than the busiest frontage (11 of 12). Both are attested - the
  takafuda stood at crossroads and bridgeheads, and at the village well - so by constitution XII this
  is two supportable answers and therefore a per-settlement knob, which the siter cannot express today.

## The pool sweep, round 2: what the four reviews found after the first four fixes

- [x] P5 **A record that still contradicted its ink on the REFERENCE hamlet.** The keep-out refactor made
      `wet_polys` no-build, so every over-claim in a marsh outline became a placement rule and an
      interactive answer. On Inashiro, **46.7% of the pond-fringe polygon lay inside the pond** and the toe
      polygon covered **88,418 sq ft of the drawn rice fan**, with a field pond inside it - ink clean, record
      wrong. The clip now subtracts the pond from a fringe and the fields from a toe or waterside, as well as
      the diked block. Two bugs surfaced doing it and both are recorded at the point of change: a field
      outline that self-intersects makes `buffer(0)` return a MultiPolygon (`_filled`), and subtracting the
      pond turns a fringe into an ANNULUS, which `best.exterior` silently threw away - handing the disc
      straight back. The record carries one ring, so the hole is spliced in on a zero-width **keyhole** seam,
      oriented so the signed area subtracts. Measured after: fringe ring **30,860 sq ft against 30,819
      expected** (outer minus pond), pond centre outside the ring, toe **0.00%** in the fields. *(rendering)*
- [x] P6 **The nub pass was calibrated below the defect it was written for.** It shipped at a 5 ft floor -
      taken from the ONE case that prompted it, 3.1 ft - and Sawada then showed two nubs that cleared it: an
      8.25 ft boot turning -87 degrees off a 117 ft run, and a 5.74 ft first segment turning 88 degrees. The
      floor is 9 ft now, about a lane-width-and-a-half at hamlet tier, and the blast radius was MEASURED
      before it was changed: over the whole pool, 5 -> 9 ft drops 3 more end vertices, **all three on Sawada,
      no other map touched**; 12 ft catches nothing 9 does not. *(rendering)*
- [x] P7 **A bead where two watercourses butt end-to-end** - Sawada's brook mouth and head intake, and
      Kashikawa's head join. `_clip_to_moat` and `_clip_to_river` have pulled their endpoints back by the
      stroke's CAP RADIUS since they were written, because a round cap bulges half a stroke-width past its
      endpoint; `_clip_to_stream` never took the argument, and the caller passed it to the other two and not
      to it. A one-argument asymmetry, not a new mechanism. *(rendering)*
- [x] P8 **The reviewer's own doc carried a retired rule.** `.claude/agents/settlement-review.md` still
      stated the 45-degree steep-caption clamp that the GM retired on 2026-08-27 (feature 133 T38), so the
      reviewer reported Inashiro's 84.8-degree and Sawada's 80.9-degree captions as defects while the engine
      was following the ruling exactly. Corrected, with a note not to re-raise them. *(rendering)*

**Found and NOT fixed - recorded with the measurement so the next session inherits it.** Each moves
placement or ink on maps across the pool, and none was caused by this feature:

- **Every privy and manure pit on Sawada stands UPWIND of its own house** - 11 of 12 NE and 1 E against
  `windward: NE`. Mechanism, measured pool-wide: `_PRIVY_SEATS` in `hamletgen/homesteads.py` is expressed in
  the HOUSE's local frame (back 0.60 / gate 0.25 / naya 0.15) and houses draw at rot 0-4 degrees, so "back"
  is north on every map. Inashiro 0/11 upwind, Kuwabata 0/9, Mizuguchi 0/4, Kashikawa 3/14, **Sawada 12/12**
  - the other four are downwind by luck, and Sawada drew the one windward value that exposes it. Nothing in
  the seat table consults `plan.windward`. The three seats are each attested, so the fix is not a new seat:
  when two seats are otherwise equal, prefer the one not within 90 degrees of `windward`.
- **Every flooded-plot predicate tests SHARPNESS and none tests SIZE.** Sawada's surviving flooded plot is
  6,706 sq ft - **4.9x the median basin and the largest of 776** - on the one map whose brief is that it has
  no pond, so the object the eye lands on in the field is a 170 ft blue sheet. Its position is sanctioned
  doctrine and the 2026-08-28 nearest-corner fix works; the gap is that a basin `close_seams` absorbed up to
  five design cells keeps the tint it was given as one. Add an AREA clause, tested on the FINAL ring.
- **A caption can be seated across a lane from its own glyph** (Inashiro: the board at x 1094.5-1100.5, lane
  1 at 1103.5-1110.6, the caption at 1109.3-1122.5 - the full lane width between them, and a shrine 22 ft
  away on the caption's own side). This is the half D3 does not cover: a way-side term in the seat filter.
  The map's notes also assert this defect "did not recur", and it is on the shipped sheet.
- **The windbreak trim got WORSE, not better** (Sawada): the deferral of 2026-08-28 recorded 57 px of bare
  strip and 37 in-frame undrawn clumps "improving"; it is now **85 px and 38**, with **5 of 19 houses beyond
  the drawn belt's end** and a 510 ft belt against a 714 ft cluster. The deferral's premise no longer holds.
- **The copse draws inside the windbreak** (Sawada: 13 of 17 copse clumps touching a windbreak clump; and
  degenerate elsewhere - Mizuguchi's copse is 2 clumps in a 205 ft record, Inashiro's 2 in a 313 ft one).
  The project's own doctrine says they are different plantings for different reasons, so this contradicts a
  recorded claim. A knob candidate: a copse embedded in the belt vs one threading the houses.
- **The persimmon's four fruit dots are a rigid mirrored 2x2** at exactly (+/-3.5, +/-3.5), r 1.3, identical
  on every tree and every map - the doctrine's own strongest face-read trigger, and the anti-twin problem in
  miniature. Jitter them off the position hash.
- **Seated fixture counts fall well short of their declared shares**: Inashiro declares manure .531 per
  household and seats 2 of 15 (p about 0.002 under a binomial); Kashikawa and Mizuguchi show the same gap.
  Either the placer refuses at a rate nothing records, or the shares do not mean what the record reads.
- **`make jogs` exits RED on Sawada** - 3 sideways steps in 776 rings, the largest 12.5 ft - and nobody is
  reading a diagnostic the project maintains for exactly this.
- **Notes drift on three maps**: Kashikawa's accepted-limitation entry names a byre that stands nowhere
  within 167 ft; Inashiro's notes give stale clump, stand and fixture counts; Mizuguchi's records a board at
  "the traffic optimum" it no longer occupies.

