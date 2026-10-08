# Feature 330 - the audit: every feature settled, every future-work entry accounted for

## A. The gm-assistant check (T02, FR-005, SC-005)

**Searched** (2026-10-08): every `specs/*/` directory's `spec.md`, `request.md` and `gm-request.md`, for
gm-assistant's own subjects - `webapp`, `Obsidian Portal`, `Discord`, `backstor`, `chargen`, `character sheet`,
`cherrypy`, `playwright screenshot`, the relic and temple skills, the `frontend-review` and `backstory-review`
agents - flagging any directory with three or more hits.

**Found**: four, each read:

| feature | hits | what it is about |
|---|---|---|
| `119-l7r-diagram-namespace` | 27 | the diagram's `l7r.diagram` namespace, which shares its parent package with the webapp's `l7r.app` - diagram work |
| `127-gated-make-commands` | 3 | the diagram's make-only guards; the webapp is named as what the guards leave alone - diagram work |
| `130-codebuild-merge-gate` | 5 | the diagram's CodeBuild merge gate; gm-assistant's resources it reused - diagram work |
| `131-split-diagram-repo` | 19 | splitting the diagram out of gm-assistant into this repository - diagram work |

**Result**: no feature belongs to gm-assistant; none deleted. The split (feature 131) carried over only the features
that concern the diagram, as the root `CLAUDE.md` says ("features 001-131 that concern the diagram live here").


## B. Every future-work entry accounted for (T04, FR-006, SC-003)

**Closing check first** (2026-10-08, an independent read of every entry against the current code, the git log and
the later specs): **37 FILE, 0 DONE, 0 DISPOSED**. No entry's named code, check or doc had changed: for example
`settlement/city/civic.py` still holds `governor_mansion`, the `GraveIsland` class and its glossary file stand,
`_knobs.py` still rolls the detached commons byre at 0.1, `tools/notes_census.py` still does not count `farm_sheds`,
`docs/buildings.md` still says the sheets draw the torii as an elevation silhouette. The seasonal maps the GM deferred
(feature 133 T60) are deferred, not disposed of; the funerary grounds' old number 275 was withdrawn, the work was not.

**Filed**: 37 features - one per entry, and one per named piece of `compounds.md`'s "Research owed" (its four
questions and three drawing items; its opening and its "Sources to read" paragraph travel with each piece as context).
Each spec carries the entry verbatim under "The entry, as filed" and names the file and heading it came from. The
mapping, which T05 reads to re-aim the pointers, is [`filed.json`](filed.json); the script is
[`file_entries.py`](file_entries.py).

| feature | from | entry |
|---|---|---|
| `331-fold-settlement-city-civic-py-into` | `cities.md` | Fold settlement/city/civic.py into castle_civic.py (feature 113, 2026-08-16) |
| `332-town-city-capital-tiers-hand-seated` | `cities.md` | The town, city and capital tiers' hand-seated captions go through the one placer when thei... |
| `333-scripted-city-generator-must-draw-differently` | `cities.md` | OWED AT CONVERSION (269's research, 2026-09-28): what the scripted city generator must dra... |
| `334-frozen-cities-modern-only-forms` | `cities.md` | OWED AT CONVERSION: the frozen cities' modern-only forms (feature 280, the modern-only swe... |
| `335-magistracies-rear-strips-feature283-reviews-left` | `compounds.md` | OPEN 2026-09-28: the magistracies' rear strips, and what feature 283's reviews left open |
| `336-takayama-guest-route-office-genkan-residence` | `compounds.md` | Research owed (rewritten by feature 267, 2026-09-27) (piece 1) |
| `337-big-was-roofed-hearing-court` | `compounds.md` | Research owed (rewritten by feature 267, 2026-09-27) (piece 2) |
| `338-koseki-form-middle-gate-stand-relative` | `compounds.md` | Research owed (rewritten by feature 267, 2026-09-27) (piece 3) |
| `339-hayakawa-stepped-landing` | `compounds.md` | Research owed (rewritten by feature 267, 2026-09-27) (piece 4) |
| `340-program-example-captions-hand-sheet-placer` | `compounds.md` | Research owed (rewritten by feature 267, 2026-09-27) (piece 5) |
| `341-door-glyphs-drawn-as-slabs-outside` | `compounds.md` | Research owed (rewritten by feature 267, 2026-09-27) (piece 6) |
| `342-torii-drawn-as-elevation-silhouette-mode` | `compounds.md` | Research owed (rewritten by feature 267, 2026-09-27) (piece 7) |
| `343-receiving-court-swept` | `compounds.md` | Is the receiving court "swept"? (found by feature 280, 2026-09-29) |
| `344-fabric-first-generation-research-direction` | `cross-cutting.md` | 2. Fabric-first generation (the GM's ordering question, 2026-08-10) - RESEARCH DIRECTION |
| `345-push-time-roll-review-agent` | `cross-cutting.md` | The push-time `roll-review` agent (deferred by feature 217, 2026-09-08) |
| `346-lighting-watercourse-paints-over-things-cross` | `cross-cutting.md` | Lighting a watercourse paints over the things that CROSS it (measured 2026-09-12, feature ... |
| `347-measure-feature274-write-cap-line-reads` | `cross-cutting.md` | MEASURE feature 274's write cap and line reads on the groups that run after it landed (owe... |
| `348-hamlet-labels-zoomed-out-hit-map` | `cross-cutting.md` | Hamlet labels in the zoomed-out hit map (found by feature 267, 2026-09-27; unmeasured) |
| `349-rename-grave-island-class-field-grave` | `farming-communities.md` | Rename the `grave island` class to `field grave` (settlement-review, Kashikawa 2026-09-28) |
| `350-village-funerary-grounds-headman-gate` | `farming-communities.md` | OPEN 2026-09-28, OWED AT CONVERSION: a village's funerary grounds (was feature 275, withdr... |
| `351-village-generator-draws-no-shrine-grove` | `farming-communities.md` | OPEN 2026-09-27, OWED AT CONVERSION: the village generator draws no shrine grove, sacred t... |
| `352-village-lane-ever-run-between-house` | `farming-communities.md` | RESEARCH OWED (feature 287's woods review, 2026-09-29): did a village lane ever run betwee... |
| `353-shared-byre-commons-rolled-map-ten` | `farming-communities.md` | OPEN 2026-09-28 (269 B16): the shared byre on the commons is still rolled, one map in ten,... |
| `354-seasonal-maps-straw-rick-hasa-frames` | `farming-communities.md` | DEFERRED 2026-08-27 (GM, feature 133 T60): seasonal maps - the straw rick, the hasa frames... |
| `355-reader-takes-river-tap-width-hue` | `farming-communities.md` | What a reader takes for the river at the tap: the width and the hue (feature 230 pass 12, ... |
| `356-ways-meet-material-changes` | `farming-communities.md` | Two ways that meet where the material changes (feature 230 pass 12, 2026-09-13) |
| `357-owed-conversion-knob-candidates` | `farming-communities.md` | OWED AT CONVERSION and knob candidates (feature 280, the modern-only sweep, 2026-09-29) |
| `358-found-feature280-settlement-reviews-measured-fixed` | `farming-communities.md` | Found by feature 280's settlement-reviews (2026-09-29), measured and not yet fixed |
| `359-found-feature291-settlement-reviews-measured-left` | `farming-communities.md` | Found by feature 291's settlement-reviews (2026-09-30), measured and left |
| `360-tree-run-crossing-water-more-than` | `farming-communities.md` | OPEN 2026-09-30 (feature 287): a tree run crossing water more than ~18 deg off square is r... |
| `361-notes-census-count-storehouse-annexes` | `farming-communities.md` | OPEN 2026-09-30 (feature 293, settlement-review of Kuwabata, round 2): the notes census do... |
| `362-connector-may-leave-through-belt-windward` | `farming-communities.md` | OPEN 2026-09-30 (feature 293 on 291): the connector may leave through the belt's windward ... |
| `363-kiln-glyph-defects` | `towns.md` | OWED AT CONVERSION: two `s.kiln` glyph defects (settlement-review on Ubame, 2026-08-17) |
| `364-frozen-towns-modern-only-forms` | `towns.md` | OWED AT CONVERSION: the frozen towns' modern-only forms (feature 280, the modern-only swee... |
| `365-enclosed-fan-tract-floor` | `towns.md` | OWED AT CONVERSION: the enclosed-fan tract floor (GM decision 2026-08-03) |
| `366-generator-parity-gaps` | `towns.md` | OWED AT CONVERSION: generator-parity gaps (town-checks audit, 2026-07-21; re-checked 2026-... |
| `367-town-deep-audit-open-items` | `towns.md` | OWED AT CONVERSION: the town deep audit's open items (2026-07-24, against the frozen Hoshi... |


## C. Every existing open feature settled (T03, FR-004, SC-002)

The 27 features open before this feature (`make speckit-todo` on 2026-10-08: 10 filed, 2 planned, 15 in progress),
each read with its open tasks, the commits naming it and the later specs naming it, by three independent passes. The
status line each now carries holds its evidence; [`settle.py`](settle.py) wrote them.

**Done** (19) - the work landed; what was left unticked was bookkeeping (stop-work, the final gate, a report) or tasks
a later feature or a recorded ruling disposed of:

| feature | evidence |
|---|---|
| 007 packing-audit hardening | e6450f5f2 (2026-07-13) landed T001-T012 with the task list; `pack_audit/grids.py` `top_vacant_rects`, `region_density` |
| 008 Mode A composition | 6da94c18f; `compound.py` `place`, `pack_audit` `perimeter_hugging_pct`, `docs/buildings.md` "Composition" |
| 010 land-use overlay grounding | ff0b34d5b with the spec; `settlement/fields/landuse.py` (the topographic filter, the economic fraction), `_knobs.py` the overlay values |
| 012 in-field paddy features | 6f4c9333c; `settlement/fields/features.py` "feature 012"; `overlap/taxonomy.py` the field ponds, rocks and graves |
| 015 punishment grounds | f78e4e533; T038 (stop-work) the only open task |
| 016 Minami | 614696beb (T14-T16: the eight-precinct doctrine and the temple knobs, now in the record's questions 0234, 0237, 0181), 6a0ce606c (the map); a frozen exhibit since |
| 017 overlap matrix | 81deedca4 "all eleven matrix defects cleared - ... Clears Ubame's crop plot in the stream" (T008); `_MATRIX_OUTSTANDING` empty |
| 112 fields package | 745a067ae, 9f0287e51, 0463c9d7a; T031-T033 bookkeeping |
| 114 structures package | 92656dfca; T035 the final gate and stop-work |
| 115 civic-grounds package | 2389749ea, 4885c99d5; T004 moot (wip/ retired), the rest bookkeeping or gates of landed commits |
| 118 rolling package | 7ad4e23c5, 0bcf81548; T033, T041 the gate and stop-work |
| 119 l7r namespace | 0280ec9c0, 948682a5a, 2e2d609b6, 7df1b1878; T032 stop-work |
| 125 lanes do not break | a44013da0, e42cd4210, d305556aa; the spec has no tasks - a write-up of what shipped |
| 126 derived lanes and form | 9fcb6b0d2, 7b448f78a; FR-003 superseded by 128 (`specs/128-all-lanes-derived/spec.md:11`); the forms switched back on by 291; US3 decided as no code change (its research.md); the gate fixtures withdrawn with the battery (166) |
| 130 CodeBuild merge gate | b3bb3782d and before; T063 (the first FULL run) withdrawn by the GM's remote-off ruling (`dev/switches.json`, 2026-09-05) |
| 131 split repository | 5c38ebc4a, 0773b970a, c8002dd79; T027 (the report) bookkeeping |
| 139 remaining test failures | its spec: "a test the efficiency session retires as no longer valid leaves the inventory by that retirement"; e20ca2623 deleted the battery its checks were in; `tools/mapcheck.py` TRIPWIRE_EXPECTED empty |
| 155 main's red floor | 84e75096b closed the red lines; the coverage decision taken by the GM in feature 174 ("the time has come to begin once again enforcing one hundred percent code coverage") |
| 175 warm the remote build | 3c7e52f28, c09942435 "MEASURED - the cache pays, 189s -> 158s"; its owed measurement taken by 177 (D5 there) |

**Withdrawn** (3) - by a recorded GM ruling:

| feature | ruling |
|---|---|
| 019 capital skeleton and castle | the GM, 2026-10-07: Shiro Daika's hand pass dropped (`docs/migration-plan.md`); the engine half landed (8eb15b41a); its checks went with the battery (e20ca2623), its byte-identity task with the 2026-08-16 freeze |
| 021 capital housing | the same ruling; its whole scope was the hand map's fabric (spec: "graduate the map from wip/ to pool/capitals/"); US1 landed (d5a99e619) |
| 275 village burial ground | the GM, 2026-09-28, recorded in its request.md ("I think you can get rid of it entirely"); a `spec.md` now carries the status, and the work is filed as feature 350 |

**Left open** (4), and listed for the GM where the GM is the one who can settle it:

- **111 hamletgen package** - in progress. The split landed (4917173f2, 818b7ea82); US2, decomposing the long stage
  functions, was HELD for the GM as "a taste call about readability, not a rule violation" (its research.md R12) and
  never ruled on. Measured now: `stage_ways` no longer exists (128 split it), `stage_sink` is 52 lines; `place_wells`
  (293 lines, 77 statements), `open_ground_patches` (481, 124) and five others remain long, all under the
  constitution's bar of a few hundred statements. **For the GM**: decompose them, or withdraw US2.
- **121 placer drawn footprint** - in progress. All three user stories landed (7a4ca9ec3, ef68b24c7, 44974634a);
  T007 went with the fixtures (166), T018 is deferred to the town tier by its research.md, T022 and T029 measured a
  placer 306 and 308 replaced. **Genuinely left**: T017, a test pinning the two allowed grove abutments.
- **312 uncited-source catalog** - filed on main, but **its work was done and never landed**: it sits in the clone
  `/diagram/.clones/diagram-uncited` - 79 commits main lacks, ending at 6e291a37f (2026-10-03), its tasks.md 23 of 23
  ticked, two uncommitted test edits, and no `backup/` branch on GitHub, so that clone is its only copy. It predates
  feature 329's move and touches 2,479 files, so landing it is a merge across the move, then the gate and the record
  gates. **For the GM**: land that clone's work, or decide 312's fate.
- **325 the GM's rulings from 319** - filed, open by design: a tracking list the GM works through; R1 (which season
  a hamlet's dry-field crops show) awaits a ruling.

**After**: `make speckit-todo` reads 39 filed (the 37 filed from future-work, 312, 325), 0 planned, 3 in progress
(111, 121, this feature), 242 closed.


## D. Before and after, and the spot check (T07, SC-002, SC-003)

`future-work/` is deleted (its five entry files and its index); `scripts/gates/check-old-layout.py` passes with no
live mention of it left.

**`make speckit-todo`, before** (2026-10-08, ahead of this feature's settling and filing): `open: 9 filed, 2 planned, 16 in progress; closed: 220`

**After**: `open: 39 filed, 0 planned, 3 in progress; closed: 242`

The difference: 37 features filed from the backlog (331-367), 22 of the old open features closed with their evidence
(section C), 4 left open (111, 121, 312, 325), and this feature itself in progress.

**Spot check** (SC-002): ten open and ten closed features drawn at random (seed 330), each read against its own
files - none misclassified. The open ten are filed (no tasks) or part-ticked; the closed ten have every task ticked
or a `Done` status carrying its evidence. Some closed features still say `Draft` or `Implemented` on their status
line: their ticked tasks decide, as plan D1 says.

```
filed        365-enclosed-fan-tract-floor                 0/0  **Status**: Filed - from future-work/towns.md, "OWED AT CONVERSION: the enclosed-fan tract floor (GM deci
in progress  330-open-work-as-features                    6/8  **Status**: Accepted - spec-fidelity FAITHFUL, round 2 (2026-10-08)
filed        325-gm-rulings-from-319                      0/0  (no spec)
filed        351-village-generator-draws-no-shrine-grove  0/0  **Status**: Filed - from future-work/farming-communities.md, "OPEN 2026-09-27, OWED AT CONVERSION: the vi
filed        361-notes-census-count-storehouse-annexes    0/0  **Status**: Filed - from future-work/farming-communities.md, "OPEN 2026-09-30 (feature 293, settlement-re
in progress  121-placer-drawn-footprint                   23/33  **Status**: Draft
filed        347-measure-feature274-write-cap-line-reads  0/0  **Status**: Filed - from future-work/cross-cutting.md, "MEASURE feature 274's write cap and line reads on
filed        358-found-feature280-settlement-reviews-meas 0/0  **Status**: Filed - from future-work/farming-communities.md, "Found by feature 280's settlement-reviews (
filed        363-kiln-glyph-defects                       0/0  **Status**: Filed - from future-work/towns.md, "OWED AT CONVERSION: two `s.kiln` glyph defects (settlemen
filed        341-door-glyphs-drawn-as-slabs-outside       0/0  **Status**: Filed - from future-work/compounds.md, "Research owed (rewritten by feature 267, 2026-09-27)"
closed       116-shrines-wells-package                    33/33  **Status**: Implemented 2026-08-16. Final per-file line counts: `wells.py` 294, `shrines.py` 251,
closed       118-rolling-package                          39/41  **Status**: Done (2026-08-17): 7ad4e23c5 and 0bcf81548; only the gate and stop-work were left unticked (f
closed       027-init-star-imports                        9/9  **Status**: Implemented (2026-08-16)
closed       329-unskill-the-repo                         9/9  **Status**: Accepted - spec-fidelity FAITHFUL, round 2 (2026-10-07)
closed       292-research-presentation-style              42/42  (none)
closed       195-cite-only-what-can-be-read               7/7  (none)
closed       149-coverage-floor-flakiness                 9/9  **Status**: APPROVED - `spec-fidelity` round 2 returned FAITHFUL. (This line read APPROVED once before th
closed       225-fold-cull-and-clip                       5/5  **Status**: IMPLEMENTED 2026-09-11 (the picture's tiles 0.7-1.3 s -> 0.5-0.7; Inashiro's clips 30 -> 1 an
closed       304-homesteads-at-scale                      20/20  **Status**: Draft
closed       214-pack-the-roster                          7/7  **Status**: IMPLEMENTED 2026-09-08 - `spec-fidelity` round 1 required three changes, all applied (FR-007 
```
