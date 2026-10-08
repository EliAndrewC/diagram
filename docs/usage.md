# Diagrams: usage

Top-down SVG plans of Rokugani locations - magistrate manors, village layouts, temple plans, military compounds, battle terrain and the like - rendered to PNG and to an interactive HTML page. This is the usage document; the repository's index is the root [`CLAUDE.md`](../CLAUDE.md). The Mode A vocabulary and sheet conventions live in [`docs/buildings.md`](buildings.md), with its compound programs in [`building-programs.md`](building-programs.md); the Mode B record - each topic's finding, the decision it drove and, for a tier no generator draws yet, the specification a map follows - is the research under [`research/`](../research/), with [`research/contents.json#tiers`](../research/contents.json#tiers) as the tier index. Read the index, then pull only the topics the subject calls for. What specifically goes in a given diagram is decided in conversation with the GM, not codified here.

The first worked example is [`pool/magistracies/ochiba-magistracy/ochiba-magistracy.svg`](../pool/magistracies/ochiba-magistracy/ochiba-magistracy.svg) (County Magistrate Kitsune Tatsuya's two-courtyard manor), the canonical Mode A template: copy it as the starting point for a new compound plan rather than rebuilding from scratch.

**Why the record is kept** (GM 2026-08-26): every map also becomes an interactive page where a reader clicks a feature to learn what it is, why it stands there, and whether that is historically accurate, a deliberate deviation, a map drawing convention or a guess - so every decision carries one of those four labels (constitution XII).

## Core principle: roughly to scale

Every diagram carries a **declared scale** - the GM's scale ladder (2026-07, extended to Mode A):

| Tier | Scale | Why |
|------|-------|-----|
| Compound plan (Mode A) | **3 px = 1 ft** | interior plans need room-level legibility; a county magistracy's ~250×200 ft is authored on a 1200×900 working canvas, then the viewBox is cropped tight to the content (see "Framing" in [`docs/buildings.md`](buildings.md)) |
| Hamlet, town | **1 px = 1 ft** | towns crop to their core and skip most surrounding farmland, so they earn the zoom |
| Village | **1 px = 2 ft** | must show ~60-90 acres of working farmland around ~50-70 homesteads |
| Provincial city | **1 px = 3 ft** | the budget-derived walled seat spans ~0.55 mi; 3 makes the wall a plausible ~1.5-1.7 mi circuit, at the top of the 2-5 li Chinese county-seat band |

The round numbers are deliberate (a human should be able to read distances off the map). Mode A compound plans declare their scale with a **scale bar drawn on the sheet** (the "Scale" section of [`docs/buildings.md`](buildings.md)). Mode B declares via `s.meta(ftpx=N)`: the building grain follows automatically (`bscale = 1/ftpx` - the urban glyph library is calibrated at town scale, with the 44x29px farmhouse ~ the 46x28 ft *minka* anchor; this is what keeps a "merchant house" the same real ~57 ft on every map). Real-feet constants convert through `s.px(ft)`; linear features through `s.lw(ft)`, which applies the **4px linework floor**: standard cartographic practice - a 5 ft roji at 3 ft/px would be an invisible 1.7px, so thin linework draws at the minimum visible width, true-width-or-floored, never inflated past the floor. Villages declare `ftpx=2` for the record but keep `bscale = 1.0` (their placement constants were hand-pre-scaled to 2 ft/px before ftpx existed). Checks read `meta.ftpx` wherever a threshold means real feet (`on_a_street`'s 85 ft, the city theater's 185 ft).

Within the declared scale, **everything is to scale** (GM ruling 2026-07-21): every feature with a real footprint - buildings, halls, torii, yards, fields, mounds, gates - draws at its TRUE size, and "it would be small at this scale" is a reason to ask the GM, never to silently inflate. The ONE sanctioned divergence is the **STROKE CONVENTION**, which covers two things and only these two:

- **Linework floors** - thin LINEAR features (ditches, wall lines, lane edges) draw true-width-or-floored at the minimum visible width (`s.lw()`, the hairline band), never fattened past the floor. A 1 ft ditch at 3 ft/px is 0.33 px - the floor rescues it from invisibility; honesty anchors on the wide features, which draw true.
- **Location markers** - a feature whose real size is sub-glyph at map scale (the well: a real curb is ~3-4 ft) is denoted by a legible MARKER at its to-scale LOCATION; the marker's own pixels are not claimed to be to scale. Wells are the canonical case (their marker scales with the map grain, ~half a dwelling, so it reads consistently at every tier). The **kosatsuba** (the settlement notice board) is the second: a true 12x5 ft frame is legible at 1 ft/px but degenerates to a 4x1.7 px sliver at city grain, so its glyph floors at 11 px on the long axis with the aspect preserved (GM 2026-07-24 - the marker NEVER shrinks a board, so the tiers where true size reads keep drawing true size). A marker records the true footprint in the manifest and its DRAWN box separately (`vw`/`vh`, mirroring the wells' `vr`), so audits read real feet while the overlap checks clear the pixels actually on the map.

The stroke convention is a visibility mechanism, **not a size license**: it never applies to anything with a drawable footprint. The framing (GM 2026-07-22): the SVG shapes and lines are the **strokes of the brush** - the *rendering conventions* by which a real feature is communicated to a human reader, the same way a paper map's line weights and symbols are conventions, not claims that the ink is life-sized. So the stroke convention documents HOW we draw (min-visible linework, a marker for a sub-glyph feature), and it lets us emphasize realism *because* the footprints themselves are never fudged. A feature with a real footprint draws that footprint TRUE; where its real shape is knowable (a projecting mamian bastion, not a convenient square), we draw the true shape. Relative sizes and distances stay proportional to reality - a thing twice as large (or twice as far) in the world reads roughly twice as large (or far) on the map. Hold proportions honest:

- A cemetery serving a thousand inhabitants should clearly **dwarf** one serving a hundred; a provincial city's wall should dwarf a village shrine; a manor should outsize a peasant house by about the ratio it really is.
- When you **size or place a new element**, ask "how big / how far is this relative to its neighbors in reality?" and match that proportion - don't just pick numbers that fit the gap.
- This is why glyphs scale with the settlement grain (`s.bscale`), why a wellhead/grave/manor is sized against the dwellings around it, and why distances (set-backs, approaches, spacing) are tuned to read at the right *relative* magnitude.
- "Not literally 1px = 1 *shaku*" settles ties and rounds awkward numbers; it never excuses a feature that reads two or three times too big or too small for what it represents. When a check or a reviewer says something "looks too small/large/close," that is a real scale error to fix, not a quirk of a non-literal map.
- The *relative-size* facts that anchor specific glyphs (e.g. a threshing yard is ~1-3% of the paddy it serves) and every other research-grounded rule are recorded **on the research page that carries the rule** under [`research/`](../research/) (Mode A grounding on [`research/contents.json#compounds`](../research/contents.json#compounds)).

Geography questions resolve **China first, then Japan**: the rule and its worked examples are in [`docs/research-doctrine.md`](research-doctrine.md).

## Two modes

Two kinds of diagram share the labeling rules, the kanji triangle and the self-review below, but differ in subject and method:

- **Mode A - Compound and building plans** (manor, magistracy, temple, keep, battlefield). Interior plan view: walls, courts, rooms, building footprints. Hand-authored SVG, copied from the canonical template and edited. The vocabulary, sheet conventions (canvas, palette, patterns, orientation, title block, framing, label sizes), period defaults and checklist live in [`docs/buildings.md`](buildings.md) - read it before starting a Mode A diagram; it indexes [`docs/building-programs.md`](building-programs.md) (per-building-type programs) and [`research/contents.json#compounds`](../research/contents.json#compounds) (the research behind the conventions).
- **Mode B - Settlement maps** (hamlet, village, town, provincial city - walled or unwalled). Landscape plan: a settlement in its fields, with realistic house density, irregular paddies, irrigation, and a shrine. The hamlet tier is generated by [`hamletgen/`](../l7r/diagram/hamletgen/CLAUDE.md) and held by the gate's tests of the placer; every other tier is a hand-authored exhibit until its generator exists, and its specification waits on the research pages. Canonical scripted example: [`pool/hamlets/inashiro/`](../pool/hamlets/inashiro/); hand-authored: [`legacy-hand-authored-pool/villages/kikuta/`](../legacy-hand-authored-pool/villages/kikuta/). Read [`research/contents.json#tiers`](../research/contents.json#tiers) for the tiers, then the topic pages the subject calls for (water and fields nearly always; towns, cities and urban features by tier). The standing conversion plan is [`docs/migration-plan.md`](migration-plan.md).

## Workflow

1. **Pre-design conversation.** Talk to the GM about what's present. Ask about scale (manor vs. village vs. temple vs. battlefield), notable features (workshops, shrines, garrisons), the residing NPC(s), the surrounding context (walled? what's outside?). Pull sizing and role context from the setting files listed under "References".

   **Settle the WATER FLOW before drawing anything - at EVERY tier, not just cities** (GM rule 2026-07-24). Before a single feature is placed, decide the map's **drainage bearing** (`meta(water_flow=<deg>)`, 0 = east / 90 = south) and, separately, the land's fall (`meta(down_deg=...)`). These are not the same fact and must not be derived from each other: a valley floor runs across the fall of the sides it lies between, and a dug contour channel is built almost parallel to the contours. Flow direction is a property of the LANDSCAPE, so reason from the regional terrain first - a mountain range running northwest to southeast throws settlements off both flanks, draining northeast on one side and southwest on the other, so establish which side of which range this place sits on. Everything downstream of that decision depends on it: which end of the settlement takes the tanneries and the burakumin quarter, which way the dyer may rinse, where the drains discharge, and which way a moat flushes. Watercourse polylines are authored UPSTREAM-FIRST. **Aim for verisimilitude, not uniformity**: do NOT make every watercourse on a map run the same way - local topography varies and most of these works are artificial (a ditch dug ALONG a slope is how you intercept downhill flow). The one hard rule is that water never gains elevation; the anti-pattern to avoid is the classic fantasy-map river running parallel to a mountain range along its base. When a course runs across the fall, be able to say why and record it. These maps carry no contour lines by design, so the declared data is the ONLY place the terrain exists. See [`research/contents.json#water`](../research/contents.json#water).

   **When generating a new PROVINCIAL CITY, ask these city-defining knobs up front** (they set the whole layout, so settle them before pitching):
   - **Does an Imperial road run through it?** (`meta(imperial_road=...)` + an N-S road through the gates; it gets a commercial ribbon). A city off the Imperial network has ordinary roads, none labeled "Imperial."
   - **Is there a river / water?** (a trunk `s.river(...)`, a fed `s.moat(...)`, canals + a `s.water_gate(...)`, a dock/wharf) - or is it a dry inland seat?
   - **What is the wall's DEFENSE TIER?** (`meta(wall_defense="siege"|"garrison"|"peaceful")`) - how hard was it fortified, which sets guard-tower density. **`siege`** = a border/besieged city, `>= 2` towers within aimed-lethal bowshot (197 ft), a dense bastion ring; **`garrison`** (default) = a garrisoned interior city, `>= 2` within full war-bow reach (328 ft); **`peaceful`** = long at peace, the sparser Xi'an crossfire (`>= 1` within 197 ft). Drive it off the city's history and location. See [`research/questions/0148-towers-along-the-city-wall-mamian.html`](../research/questions/0148-towers-along-the-city-wall-mamian.html). (Tango and Nagahara are both `siege`.)

2. **Pitch and confirm.** Offer the GM 3-5 distinct ideas to react to before settling on a layout. Flag any deliberate L5R divergences from historical Japan (e.g., Inari shrine as a hall rather than a standalone, on-grounds barracks rather than off-site retainer housing).

3. **Draw it.** Top-down plan view, north at the top of the viewBox, the main gate of any walled compound facing south (bottom). A Mode A sheet follows the conventions and vocabulary in [`docs/buildings.md`](buildings.md); a Mode B map is a `.gen.py` against the settlement library.

4. **Render** (below).

5. **Self-review.** Read the rendered PNG yourself. Does every named feature appear? Are labels legible? Is the layout coherent? Iterate before showing the GM.

   **Every found defect becomes a TEST** (GM rule, 2026-07-21): write it FIRST, see it fire RED on the unfixed artifact, apply the fix, see it GREEN. For a scripted Mode B map that test is a unit test of the placer that made the defect, or a seed test in `tests/gate/` where no single placement owns the property. **Mode A is drawn by hand, so it keeps its automated checks** (GM 2026-08-30: *"for nonscripted diagrams such as the magistracy diagrams, there still are automated checks and those serve a valuable purpose because those maps are generated by hand rather than by a scripted process"*): a defect decidable from the SVG's geometry becomes a check in [`tools/pack_audit/`](../l7r/diagram/tools/pack_audit/CLAUDE.md), red-tested against a frozen copy of the bad map in `tests/fixtures/<subject>-...-red.svg`. Only a defect that needs JUDGMENT rather than geometry goes to the `building-review` agent instead.

6. **Report to GM.** Describe what changed, what's deliberately absent, where the diagram diverges from history (Edo vs. Sengoku vs. L5R), and offer a historical-accuracy review pass.

## Labeling rule: English-default

Use **English** for commonplace nouns: `latrine`, `bath`, `granary`, `entry porch`, `cell`, `hearing court`, `kitchen`, `stables`, `well`.

Reserve **Japanese** for terms that function as names:

- **Roles / titles** that are L5R-specific: `karo`, `daimyo`, `yoriki`, `daikan`, `ashigaru`.
- **Theological / cosmological proper terms**: `Ta-no-Kami`, `Myobu`, Fortune names (`Inari`, `Bishamon`, etc.).
- **Named relics**: `Akami-fude`, `Chigiri-no-Chou`, etc. - coined per gm-assistant's relic skill.
- **Named places, clans, families, lineages**: as canonical.

When kanji appears in a label, it must pass the **kanji ↔ romaji ↔ meaning triangle** per Constitution Principle XI. Cross-reference: gm-assistant's [relic skill](https://github.com/EliAndrewC/gm-assistant/tree/main/.claude/skills/relic) for the triangle worksheet pattern.

Three further labeling rules (GM, 2026-07):

- **Label Imperial roads; leave other roads unlabeled.** An Imperial road is a named institution - part of the maintained Imperial highway network - and flagging it tells the reader something real about the settlement (traffic, waystations, who maintains it). An ordinary road needs no label: the drawing already shows where it runs and which edge it leaves by, so a label like "north road" restates what the map makes obvious (same defect as labeling a gate "gate"). Validated instance: Nagahara's through-road was labeled "north road" - removed; Tango's and Hoshizora's "Imperial Road" labels stay.
- **Annotations explain the unusual, not the universal.** A feature label states the function (`clerks' duty room`); italic sub-notes are reserved for what is particular to THIS subject (`staging store - tax grain barges down to Nagahara`). A note that would be equally true on any instance of the feature ("3-4 town clerks by day") is clutter - facts like that live in these docs, not on the sheet. This applies to ALL prose on the sheet, legend/notes boxes included: a box line stating a program fact ("~15 samurai per county town") is the same defect relocated.
- **Terms mean what they say.** A label that quietly asserts a quantity, rate, or relationship must match the setting's actual arrangements: "tithe" implies a tenth, and Rokugan's land tax is 1/3, so it is *tax grain* and a *tax archive* - never "tithe".

## Rendering

The renderer is **resvg** (its setup and why there is no fallback: [`docs/container.md`](container.md)).

- **Mode B** renders itself: `s.finish()` writes the SVG, the PNG at 2600 px and `<map>.html` - the interactive page (feature 134), where hovering a feature lights every feature of its kind and clicking it opens what it is, why it stands there and its sources ([`l7r/diagram/interactive/`](../l7r/diagram/interactive/CLAUDE.md)). Regenerate a map with `make map GEN=pool/<tier>/<map>/<map>.gen.py`; never call `resvg` by hand for one.
- **Mode A**: each sheet's gen renders its picture and page with the captions placed by the one placer; `make sheet-render SHEET=<svg> OUT=<png>` renders one to look at. 2400 px wide or more keeps the smallest labels (latrines, well annotations) legible.
- Draw order (what paints over what): [`dev/placement.md`](../dev/placement.md), DRAW ORDER.
- After rendering, **read the PNG back yourself with the Read tool** to verify legibility and correctness before declaring done. Per Constitution Principle I the author is not a reliable reviewer of their own visual output - but at minimum, look at it once before reporting it as ready.

## Output convention

Finished diagrams live in **two trees**, each `<tree>/<tier>/<map>/` - one folder per map, holding that map's whole bundle (feature 161):

- **`pool/`** - what is LIVE: regenerated and re-gated on every run.
  - `pool/hamlets/<map>/` - **Mode B** scripted settlement maps (`villages/`, `towns/`, `provincial-cities/`, `capitals/` appear here as those tiers convert)
  - `pool/magistracies/<map>/`, `pool/country-shrines/<map>/` - **Mode A** hand-authored plans, one folder per building type. Hand-authored BY DESIGN - a compound is small enough that scripting it buys nothing
- **`legacy-hand-authored-pool/<tier>/<map>/`** - the FROZEN hand-authored Mode B exhibits (GM 2026-08-16): never regenerated, never re-gated. A map leaves this tree only by being CONVERTED to scripted generation, when its folder moves into `pool/`
- scratch output (a trial render, `hamletgen --out`) goes to the session's scratchpad, never into the repository; the top-level `wip/` was retired on 2026-10-08

`pool/index.html` (`make pool-index`) covers both trees on one page. Each map is a set of files sharing the map's name, inside its own folder (e.g. `pool/hamlets/inashiro/inashiro.*`):

- `<subject>.svg` - the drawing. **Mode A: this IS the source** (hand-authored, tracked). **Mode B: this is DERIVED** from the `.gen.py` + `.json`.
- `<subject>.png`, `<subject>.html` - the raster and the interactive page (always derived, never tracked - feature 178)
- `<subject>.notes.md` - design notes: intent, knob settings, deliberate choices, review log; the second source for the `building-review` / `settlement-review` checks. **Every pool subject carries one**: intent that lives only in gen comments means a future session cannot tell a deliberate oddity from a regression
- `<subject>.gen.py` - the generator (Mode B), or the sheet's render script (Mode A)
- `<subject>.json` - the Mode B manifest: the record every rule, tool and interactive page reads

What git tracks and why: [`dev/pool.md`](../dev/pool.md) and the comments in `.gitignore`.

Subject names: lowercase-kebab-case, descriptive (e.g., `ochiba-magistracy`, `wasp-keep-hachinaga`, `kitsune-mori-pilgrimage-trail`).

## References

- [`pool/magistracies/ochiba-magistracy/`](../pool/magistracies/ochiba-magistracy/) - canonical Mode A worked example and template
- [`pool/magistracies/hayakawa-magistracy/`](../pool/magistracies/hayakawa-magistracy/) - Mode A example B: the generic magistrate's-manor program instantiated fresh
- [`research/contents.json#tiers`](../research/contents.json#tiers) - the Mode B tier index, beside the topic pages (water, fields, homesteads, ways, vegetation, religion-and-death, presentation, towns, cities, urban features, archetypes)
- [`building-programs.md`](building-programs.md) - the Mode A compound programs, split out of `docs/buildings.md`
- [`research/`](../research/) - the research behind every rule; `make record` builds the site a reader opens
- [`settlement/`](../l7r/diagram/settlement/CLAUDE.md) - the shared Mode B library (the `Settlement` class as a mixin-composed package)
- [`hamletgen/`](../l7r/diagram/hamletgen/CLAUDE.md) - the scripted hamlet generator, the method the project is migrating to ([`docs/migration-plan.md`](migration-plan.md))
- [`tools/pack_audit/`](../l7r/diagram/tools/pack_audit/CLAUDE.md) - Mode A automated audit of a compound SVG; run it before presenting a compound plan
- [`overlap/`](../l7r/diagram/overlap/) - the overlap taxonomy: which features may lie on which, and why
- [`tests/gate/`](../tests/gate/) - the finished-map tests no placer unit test can replace
- Legacy Mode B exhibits, one per form (read each one's `.gen.py` docstring and `.notes.md`):
  - [`villages/kikuta/`](../legacy-hand-authored-pool/villages/kikuta/) - pond-fed single comb-field, LINEAR ribbon village
  - [`villages/hikari-no-sato/`](../legacy-hand-authored-pool/villages/hikari-no-sato/) - the water-first SPLIT (multi-block) village
  - [`hamlets/moritono/`](../legacy-hand-authored-pool/hamlets/moritono/) - a hamlet beside a forest, water flowing E->W
  - [`hamlets/akagahara/`](../legacy-hand-authored-pool/hamlets/akagahara/) - a DISPERSED hamlet on red-clay ground
  - [`towns/hoshizora/`](../legacy-hand-authored-pool/towns/hoshizora/) - an unwalled county-seat town on an Imperial road
  - [`towns/hirameki/`](../legacy-hand-authored-pool/towns/hirameki/) - a walled town, every legal water topology
  - [`towns/ubame/`](../legacy-hand-authored-pool/towns/ubame/) - an unwalled BORDER town with no Imperial road; smoke downwind, filth downstream
  - [`provincial-cities/tango/`](../legacy-hand-authored-pool/provincial-cities/tango/) - a walled provincial city sized budget-first ([`research/contents.json#city-sizing`](../research/contents.json#city-sizing))
  - [`provincial-cities/minami/`](../legacy-hand-authored-pool/provincial-cities/minami/) - a `peaceful` wall tier and a program that does not fit an ordinary city's budget
- The GM's setting notes (gm-assistant, mounted read-only at `/host-l7r-repo/gm-assistant`; on GitHub: <https://github.com/EliAndrewC/gm-assistant/tree/main/setting>):
  - `/host-l7r-repo/gm-assistant/setting/village-headsmen.md` - village structure, strip-allocation/usufruct, headman role (Mode B grounding)
  - `/host-l7r-repo/gm-assistant/setting/median-domain.md` - sizing data (samurai per town, etc.)
  - `/host-l7r-repo/gm-assistant/setting/government.md` - role hierarchies (ministries, magistrates, etc.)
  - `/host-l7r-repo/gm-assistant/setting/hierarchies.md` - administrative structure (province / county / village)
  - `/host-l7r-repo/gm-assistant/setting/demographics.md` - populations
  - `/host-l7r-repo/gm-assistant/setting/castes.md` - caste assignments
- gm-assistant's [temple skill](https://github.com/EliAndrewC/gm-assistant/tree/main/.claude/skills/temple) - temple organization (for diagrams of religious sites)
- gm-assistant's [relic skill](https://github.com/EliAndrewC/gm-assistant/tree/main/.claude/skills/relic) - Japanese authenticity triangle; relic conventions
- [`.specify/memory/constitution.md`](../.specify/memory/constitution.md) - Principle I (visual verification before declaring done), Principle XI (Japanese authenticity)
