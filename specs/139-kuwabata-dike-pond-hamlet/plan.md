# Implementation Plan: Kuwabata, the Dike-Pond Hamlet, Scripted and Audited

**Branch**: none (`SPECIFY_FEATURE=139-kuwabata-dike-pond-hamlet`) | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Teach `hamletgen` the `mulberry_dike_fishpond` archetype as what the engine already says it is - the
polder stage carried to the wholesale-conversion overlay - so Kuwabata's pool entry becomes a
declaration; census its feature families against Inashiro's; then run the dike-pond research pass
and hand the GM a gap list. Stop there. Nothing new is drawn without the GM's word.

## Technical Context

**Language/Version**: Python 3.14, GNU make | **Single-artifact target**: `pool/hamlets/kuwabata.gen.py`
(`make map GEN=pool/hamlets/kuwabata.gen.py` - one named map, legal under the scope lock) |
**Reference guard**: Inashiro's manifest byte-identical before/after (`make reference`, diff the json)
| **Gate**: `make done` (locked, ~75 s; the map-rolling tests are deferred to unlock and recorded as
owed) | **Performance bookends**: NOT TAKEN under the lock (132 FR-010) - owed at unlock, recorded
in tasks.md | **Switch state at start**: remote off, scope locked (thrown 2026-08-27 by the 133
session; its reason says "no other session runs make done until the GM says so" - this session
treats the GM's instruction to proceed with engine work in THIS session as that say-so for the
LOCKED, local-only `make done`, and records it here rather than silently; a locked done runs no
sweep and dispatches nothing).

## Constitution Check

- I, II: N/A. V: PASS (the GM's words are quoted only).
- VI: PASS - iterate on Kuwabata alone; `make done` once at the end; the reference hamlet's
  identity is the regression guard; the pool sweep is owed at unlock and said so.
- X: 100% coverage on `hamletgen/`; new branches get tests in `tests/hamletgen/`.
- XII: the conversion rests on findings already in `research/archetypes.md` (siting, sluices,
  grid-vs-mosaic, 6:4) - their `Sources:` lines read "not recorded", so T11 sources them through the
  source-reader before the generator work ships; the audit (T30-T32) is a new pass with its own
  reader run. Two attested forms -> a knob: `pond_layout` grid|mosaic already exists engine-side and
  becomes a rolled hamletgen knob, Kuwabata pinned to mosaic (what the GM saw).
- XIII: baseline = the hand-authored Kuwabata's gate result and the three regression fixtures
  named for it; Inashiro byte-identity.
- XIV: the polder archetype's one known blocker (title on the belt) is fixed here if Kuwabata's
  seed hits it; any defect met on the way is fixed in the task that met it.
- XVI: spec-fidelity round 1 before T20; the GM's "no new categories without me" is FR-008 and is
  the hard stop between phases 2 and 3.

## Design

### The archetype (T20-T22)

`FIELD_ARCHETYPES` gains `mulberry_dike_fishpond`; `plan_site` treats it as a polder (cardinal
falls). `stage_field` routes both polder archetypes through `stage_polder`, which takes its cell
size, parcel mix, gaps and mosaic from an archetype table in `consts.py` (rice polder 110 ft cell,
(0.52, 0.16, 0.12); dike-pond 160 ft cell, merge-heavy (0.10, 0.0, 0.60), 11 ft gaps - the
`build_polder` TRUE-SCALE SIZING note). After the polder draws, the dike-pond path applies
`apply_land_use(net, "mulberry_fishpond", rng, fraction=0.9, eligible="all")`, sets
`meta.field_archetype`, `meta.pond_layout`, the waterward reed fringe + `meta.waterward` (the
hand-authored map's composition; research 'Polder siting'), and the dike-pond footbridge caps.
Every `== "polder_grid"` test in the generator becomes `is_polder(plan)`.

### The census (T24)

A read-only tool (`tools/family_census.py`, `make family-census A= B=`) lists the manifest keys /
fixture kinds present on A and absent on B, so "every reference-hamlet feature" is a measured
table, not an impression. Absences are classified in the spec's Decisions Recorded table.

### The audit (T30-T32)

One search-pass agent (running), then `source-reader` on every claim, then
`specs/139-.../audit.md`: candidates with prevalence, source, drawability; a not-owed list; the
paddy features that should be ABSENT on a no-rice hamlet. Presented to the GM. No implementation.

### The task clock

Same shape as feature 133 (`given | done | elapsed | runs`, `research:` line, the three boxes on
physical tasks).
