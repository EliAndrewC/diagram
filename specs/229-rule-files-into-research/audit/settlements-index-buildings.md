# Audit: `settlements.md` (44.1 KB, the Mode B index), `SKILL.md`, `buildings.md` + `buildings/programs.md` against `research/buildings.html`

Independent Opus reader, 2026-09-12.

**Headline**: `l7r/diagram/check_village/` holds only `__pycache__`; `tests/check_village/`, `tests/test_regressions.py`, `pool/regressions/`, `tools/make_regressions.py` are gone; `solid_structs()` no longer exists; `test_every_solid_struct_is_gated_off_every_hazard` 0 hits. What survived feature 166 is the taxonomy DATA (`_OVERLAP_STRUCTS`, `_LABEL_GROUP`, `OVERLAP_CLASS`, `_MATRIX_*`) plus `matrix_violations()`, asserted in `tests/gate/test_no_feature_overlaps.py`.

## settlements.md

| Section (lines) | Class | Justification | Canonical home |
|---|---|---|---|
| Preamble 1-8 | A | links `l7r/diagram/check_village/` (dead) | `SKILL.md` "Two modes"; `settlement/CLAUDE.md` |
| Load only what the map needs 9-29 | B | live routing table (13 files) | doc-only by nature |
| Where a named section went 30-52 | B | 92 engine comments cite `settlements.md`, many by section name (`citybudget.py:85`, `overlap/taxonomy.py:91,95`, `civic_grounds/justice.py:25,82,166`, `_knobs.py:478,530`, `hamletgen/consts.py:453`) | live redirect surface |
| Architecture 53-67 | A | worked examples are frozen legacy maps | `settlement/CLAUDE.md`, `migration-plan.md:38-42` |
| `meta()` knobs 68-91 | B/F | 22 knobs, 9 read by nothing | per-knob below |
| Workflow spec -> validator -> persona 92-99 | F | step 3 runs the deleted module; step 2 copies a frozen gen | `SKILL.md` step 5, `hamletgen.md` |
| Scale and density 100-158 | B + D | population model, tier numbers, three GM rulings | below |
| The validator 159-201 | A + F | matrix paragraphs restate live code; check lists and four-leg suite describe deleted things | `overlap/taxonomy.py:305-320`, `matrix.py:27` |
| WAIVE the rule in writing 202-229 | D + F | rulings live; mechanism (`meta(waivers=)`, `waivers_are_live`) dead; pointer to skill CLAUDE.md "a map may override a rule in writing" is a dead link | |
| Historical grounding 230-238 | A | one entry, "the older inline form" | `research/buildings.html` scale entry |

Shares: A ~27%, B ~23%, C ~2%, D ~13%, E ~2%, F ~29% outright (~33% with dead knob rows and the waiver mechanism). F block measured 11,693 bytes + ~1,800 dead knob rows + ~700 waiver mechanism.

### D items
1. **A VILLAGE IS ITS DISTRICT** (GM 2026-08-29): "there is no reason to ever say what village district a village belongs to"; a village page states its county; a hamlet says its district; the shared name is a deliberate departure the maps do NOT flag (l7r.md "Place Names"). Partly in `interactive/place.py`.
2. **What a page STATES about size, per tier** (GM 2026-08-29): hamlet/village exact farmhouse count + ~5x; town/city exact non-farm dwelling count and no farmhouse count ("deliberately not all rendered"); the 1,200 IS THE TOWN'S OWN (settlement-review round 8; county reading would double-count ~172,000). Encoded as `Kind.default_population`; reasoning only here.
3. **The Hirameki waiver** (GM 2026-07-27): walled in haste in the Lion/Crane war; intramural chrysanthemum field; no burakumin quarter; waives the housing check on that ground.
4. **Reach for a waiver only when the PREMISE conflicts**: Minami priced honestly by the budget instead (a bigger wall).
5. **Lock the rules in against ORDINARY settlements first**: Tango and Hirameki both atypical and drawn early; the most portable paragraph in the file.
6. **The scale ladder** (GM 2026-07): hamlet/town 1 ft/px, village 2, city 3; town fields had run 4-8x under real area; constants in real feet; linework floors at 4 px true-or-floored. Duplicated on `research/buildings.html`; the 4 px floor and ftpx thresholds only here.

### B items - encoded
`windward` default NW (`groves.py:33`); `grove_prevalence=1.0` (`:47`); `inwall_groves=False` (`farmsteads.py:227`); `households` (`place.py:191`, `driver.py:354`, `wells.py:20`); `ftpx`/`bscale` (`core.py:404-417`; `roll.py:253`); hamlet band 10-20 (`consts.py:456` `HOUSEHOLD_BAND`, cited back to "Scale and density" at :453); population = dwellings x 5, `DWELLING_KINDS` ten kinds match (`dwellings.py:20-35`, `HOUSEHOLD = 5`); overlap classes and permission sets (`taxonomy.py:315+`, `matrix.py:27`).

### B items - NOT FOUND
`target_houses=N` ±15% (0 hits anywhere); `torii_expected`, `shrine_on_hill`, `fallow_implies_abandoned`, `monastery_fortunes`, `gate_market`, `population_tol` (frozen gens only); `clan=` setting two monastery dedications + "ASK the GM" (only `_knobs.py:216` reads clan for a water town); `theater_stage`, `fire_tower`, `granary`, `flophouses`, `walled` (manifest keys/docstrings only); the two-deep ring recipe (~55 gap, ~56 px spacing, single ring saturates ~40); the ~50 houses / 200-500 people / 40-100 households village band; town/city `top_up()` recipe (14 px ministry stand-clear, ~85 px stables standoff); "villages and hamlets are peasant-only".

### Disagreements
1. **0.7 houses per household is contradicted**: L104 says the gate requires ~0.7 per household; `hamletgen/homesteads/stages.py:32` says 0.85-1.05x; 16 of 17 manifests at ratio 1.00, Hikari no Sato 0.94; `interactive/place.py:198` demotes it to a permission and mis-describes Hikari. The GM's "~70 households ... at least 50 houses" was a FLOOR the doc turned into a ratio.
2. `_MATRIX_OUTSTANDING` described as populated; `taxonomy.py:629-640` is empty ("ALL ELEVEN are now fixed", 2026-07-26).
3. "Gated off all fifteen keep-clear hazards" (L161) has no mechanism; `dev/placement.md:317-408` carries the same stale claim.
4. `population_consistent_with_housing`, `town_farmers_plurality`, `no_groves_inside_walls`, `walled_town_has_gate_market`, `walled_town_has_fire_tower`, `city_has_fire_towers` 0 hits.

### What the engine's docs hold better
Draw order and keep-clear contract -> `dev/placement.md` (L8, L317); overlap classes -> `overlap/taxonomy.py:305-320`; knobs -> `hamletgen/plan.py:51-111` `HamletSpec` (19 fields; `settlements.md` never mentions it) and `_knobs.py`; the coverage floor and test shape -> root `CLAUDE.md`, `SKILL.md` step 5; tier page statements -> `interactive/place.py:185-205`.

### Verdict
Two documents in one: a live index (load table; the section-name forwarding table with 92 citers) + ~13% decision record nowhere else + ~30% stale validator prose that is actively harmful. If the rule files go, the index becomes: (a) nothing (no files to route to), (b) a tier status table (in `migration-plan.md` today), (c) a decisions home for D1-D6.

## SKILL.md
Fresher than settlements.md: step 5 already says no check battery; References already point hamlet work at `hamletgen.md`. One stale sentence at L79: "Built by a parametric generator with an automated validator gate" with a legacy village as its example - the reason a session lands in settlements.md expecting a validator. The References entry for `overlap/` is the model framing.

## buildings.md + programs.md vs research/buildings.html

| Section | Class | Note |
|---|---|---|
| Research pointer L3 | A | |
| Scale L7-11 | E + D | 3 px = 1 ft; the retired ~2x glyph doctrine; laundering tales; the retirement ruling NOT on the page |
| Design notes and review gate L13-31 | C | `building-review`, `size-audit` |
| Building vocabulary L33-115 | E | every named `pack_audit` check present |
| Composition L116-127 | E | `compound.py` |
| Programs pointer L128-130 | A | |
| Checklist L132-162 | C | |
| Historical grounding L164-166 | A | a pure pointer - the clean split settlements.md never finished |
| programs.md | E | staffing anchors (~15 samurai, 3-4 clerks, ~10 servants, ~1,000 koku, ~6,400 koku) sourced to budgets.md/demographics.md, nowhere else |

Shares: E ~72%, C ~20%, D ~5%, A ~3%, F ~1%. **Not meaningfully duplicated**: numbers agree everywhere checked (37-42% coverage band, 90-135 sqft per drilling samurai, 8-12 tubs, remand, 3 px = 1 ft).

### D items missing from research/buildings.html
1. **~2x point-glyph doctrine RETIRED** (GM 2026-07-21): true size for everything, point glyphs included; two limits (a stroke floor is linear; buildings are not glyphs); two sanctioned markers (wells; salt wards - "do NOT call r2.5 true size").
2. **Threshold stones OUTSIDE the passage** (GM 2026-07-25): a stone above ground is something a cart rolls over; Ochiba's pair inside a 13.3 ft gate, second round of the same defect.
3. **Fire-water tub OUTSIDE its building, no overlap** (GM 2026-07-25, tightened 2026-07-26): downspout and bucket line; `fire_water_adrift` vs `tubs_in_buildings`; fixtures `tests/fixtures/ubame-tubs-inside-red.svg`, `ubame-tub-straddle-red.svg`; "a center test has a blind band exactly the width of the glyph's radius".
4. **Structures ABUT a wall, never stand in it** (GM 2026-07-24): ~2 ft off a compound wall, ~1.5 ft off a divider; the privy color missing from the check's fill list until 2026-07-25; "when two checks look similar, ask whether their defaults point the same way".
Near-miss: the opening's INK width (`stroke-linecap="square"` inks half a stroke past each endpoint; every opening drew 3 ft narrow; Ubame's goods gate wider than its main gate) - a convention with no entry.

### Stale in the Mode A pair
`tools/pack_audit.py` is a package `l7r/diagram/tools/pack_audit/` - named as a file in eight places (checks live: `fire_water_adrift` `checks.py:63`, `tubs_in_buildings` `:90`, `passage_blockers` `:292`, `structures_on_walls` `:449`); `buildings.md` L134 sends Mode B work to the deleted validator; `programs.md` L11 points at a "Historical grounding section below" that does not exist.

### Verdict
`buildings.md` and `research/buildings.html` should both stay; the split is the worked example. The five conventions above belong on the page as convention entries; the eight paths and two pointers need fixing.
