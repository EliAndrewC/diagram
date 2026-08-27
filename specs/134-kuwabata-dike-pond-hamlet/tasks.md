# Tasks: Kuwabata, the Dike-Pond Hamlet, Scripted and Audited (134)

Checked off only when verified on Kuwabata (and Inashiro unchanged). T99 is the GM's alone.

## Phase 0 - the skeleton

- [x] T01 `spec-fidelity` review of spec.md against gm-request.md: round 1 three changes (FR-008 widened, the knob edge case split, FR-007 carries the FR-002 omissions), round 2 FAITHFUL - recorded in spec.md
      research: procedure
- [x] T02 the number claim pushed to main at 827bd8d6 (specs/ alone, route DIRECT; the feature otherwise stays in the clone until T99)
      research: procedure

## Phase 1 - research before the generator (constitution XII)

- [ ] T10 the conversion's own research: where a dike-pond hamlet's houses stand, how the block is fed and drained, grid vs mosaic, the 6:4 ratio - the record already answers (research/archetypes.md 'Polder siting', 'A dike-pond is fed and drained through sluice gates', 'Grid vs mosaic', 'The 6:4 water-to-dike ratio'); this task confirms the pointers and lists what the generator will read from them
      given 2026-08-27T23:40Z | done - | elapsed - | runs: -
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T11 source the four dike-pond entries the conversion rests on whose `Sources:` line reads "not recorded" (v2.10.0): find and read the sources, register them in SOURCES.md, mark SUMMARY-ONLY where the page could not be read
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited

## Phase 2 - the conversion

- [ ] T20 the archetype in the spec and the plan: `mulberry_dike_fishpond` in FIELD_ARCHETYPES (not ROLLED), cardinal falls, the per-archetype polder table (cell, parcel mix, gap, mosaic), `pond_layout` as a rolled knob with Kuwabata pinned to mosaic; tests in tests/hamletgen/test_plan.py
      given 2026-08-27T23:05Z | done 2026-08-27T23:40Z (with T21-T24; one sitting) | runs: quick x4, map x4, hamlet x3, family-census x2, gate-manifest x4
      OPEN ONLY FOR T11: the code and the map are done; the box stays open until the source-reader confirms the entries (constitution v2.12.0 refuses a ticked physical task with an open box)
      note: the record already answered every number (`build_polder` TRUE-SCALE SIZING, research/archetypes.md 'Grid vs mosaic', 'The 6:4 water-to-dike ratio'); `POLDER_FABRIC`, `POND_LAYOUTS`, `DIKEPOND_CONVERSION` carry the why. The source-reader box is owed with T11: those entries' `Sources:` lines read 'not recorded'
      research: physical (the numbers are the record's: build_polder TRUE-SCALE SIZING, research 'Grid vs mosaic')
      - [x] research pass (the record: pointers above)  - [ ] source-reader confirmed (T11)  - [ ] recorded and cited (T11)
- [ ] T21 the stage: `stage_polder` parameterized by the table; the dike-pond path applies the wholesale overlay, declares `field_archetype` / `pond_layout` / `waterward`, draws the waterward reed fringe; every `== "polder_grid"` in the generator becomes `is_polder(plan)`; footbridge caps on the dike-pond ring
      OPEN ONLY FOR T11, as T20
      note: three defects met and fixed here (XIV): the windbreak drew over the header reservoir (`village_grove` had no pond keep-out); `_touch_junctions` closed a 30 ft lane onto its own start (a 28 ft loop, `lanes_bend_like_paths`); the fringe first went in the hinterland and was drawn over an already-routed connector (`roads_clear_of_marsh`) - now its own stage after the seat. The seams check stands aside for dike-pond fabric (two rings a dike apart ARE the system). Crossing caps: village on a toe flank -> that toe 3, far toe 0; at the head or foot -> both toes 2 (a capped-to-zero toe was a long ditch with no plank)
      research: physical (research 'Polder siting', 'Polder ring canal' crossings)
      - [x] research pass (the record: research/archetypes.md 'Polder siting', settlements.md 'Polder ring canal')  - [ ] source-reader confirmed (T11)  - [ ] recorded and cited (T11)
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

- [ ] T30 the dike-pond research pass: what stands on a silk-and-fish hamlet that a paddy hamlet lacks, and which paddy features a no-rice hamlet should lack (search-pass agent, then `source-reader` on every claim)
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T31 the record: research/archetypes.md gains the findings with `Sources:` lines; SOURCES.md the keys; `specs/134-.../audit.md` the gap list (prevalence, source, drawability), the not-owed list, and the should-be-absent list
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T32 present to the GM and STOP: the generated map's path, the census, the audit list; `settlement-review` of Kuwabata launched in the background at this hand-back (dev/reviews.md: at acceptance, never per task); no item of the audit implemented (FR-007, FR-008)
      research: procedure

## Phase 4 - the GM

- [ ] T40 (open slot) tasks the GM names from the audit or the map, each in their words, timed, classified
- [ ] T99 **the GM accepts the scripted Kuwabata** - tickable only on the GM's explicit word, recorded here verbatim. Never ticked by a session.
