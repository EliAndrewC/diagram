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
