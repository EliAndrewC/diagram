# Tasks: Kuwabata, the Dike-Pond Hamlet, Scripted and Audited (134)

Checked off only when verified on Kuwabata (and Inashiro unchanged). T99 is the GM's alone.

## Phase 0 - the skeleton

- [x] T01 `spec-fidelity` review of spec.md against gm-request.md: round 1 three changes (FR-008 widened, the knob edge case split, FR-007 carries the FR-002 omissions), round 2 FAITHFUL - recorded in spec.md
      research: procedure
- [ ] T02 the number claim pushed to main (specs/ alone; the feature otherwise stays in the clone until T99)
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
      research: physical (the numbers are the record's: build_polder TRUE-SCALE SIZING, research 'Grid vs mosaic')
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T21 the stage: `stage_polder` parameterized by the table; the dike-pond path applies the wholesale overlay, declares `field_archetype` / `pond_layout` / `waterward`, draws the waterward reed fringe; every `== "polder_grid"` in the generator becomes `is_polder(plan)`; footbridge caps on the dike-pond ring
      research: physical (research 'Polder siting', 'Polder ring canal' crossings)
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited
- [ ] T22 Kuwabata's pool entry is a declaration (`HamletSpec(name="Kuwabata", seed=..., households=16, down_deg=90, field_archetype="mulberry_dike_fishpond", pond_layout="mosaic")`); the hand-authored script retired (git history keeps it); renders un-tracked (`git rm` svg/png, drop the `.gitignore` `!` lines - dev/pool.md); kuwabata.notes.md rewritten for the scripted map; migration-plan.md status table updated
      research: rendering
- [ ] T23 the map generates and the gate passes: `make map GEN=pool/hamlets/kuwabata.gen.py`; the three `pool/regressions/*kuwabata*` fixtures still fire; any blocker met (the polder title/belt one included) fixed here (XIV)
      research: rendering
- [ ] T24 the feature-family census: `tools/family_census.py` + `make family-census`; Inashiro vs Kuwabata; every absence classified in spec.md Decisions Recorded with its research pointer; Inashiro's manifest byte-identical before/after (`make reference` + diff)
      research: rendering
- [ ] T25 knob maps owed: one map per `pond_layout` value (grid, mosaic) rolled one at a time with `make map GEN=` under the lock; `make done` (locked) green; the deferred sweeps (polder cohort, tripwire, perf bookends) recorded here as OWED at unlock with their commands
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
