# Tasks - feature 449, a Rust codebase (phase 1: the guards)

Ticked tasks are archived in `tasks-done.md` (feature 449 T142): `make tick` moves each ticked task there with its lines; this file holds the open ones.

Phases 2-4 are planned to the task in their own plan amendments (plan.md, Summary). Every task here is tooling: a map convention with
nothing behind it in physical reality, so each is `research: rendering`.

## Occasions

- none: T252 - make maps adds read-only judges (the Mode A pool sweep's judge moved out of test-only code, a hamlet spec check) and the command over them; no map's drawing, placement, glyph or research page changes.
- none: phase 1 moves the guards that run on Claude Code's tool calls; no map feature, glyph, placement rule or research page changes.
- glyph-redrawn: sluice gate on kuwabata - T234: the polder's sluice redrawn from an 8 ft square on its point to the frame across its channel 0179's drawing page draws (board, two posts, crossbeam, windlass drum, 20 ft post to post); set aside at rust-only (444 FR-023)
- placement-changed: marsh on kuwabata - T236: the waterside reed strip laid from the dike's outer face itself and stopped at the banks of the feeder and the outfall where they cross the dike at the sluices, no longer over the dike's corners or across the channel mouths; set aside at rust-only (444 FR-023)
- none: T239 - the seat on a polder handed a ring off the dike's outer face, so Kuwabata's settlement's ground moves 52 ft north off the north dike and the head canal (y 2340 to 2288); that dashed ground and its label are the driver's placeholder mark (`-`, no registry element, outside the review lookup's legend), so no element is re-placed or redrawn and no glyph or placement unit is owed; the ink census is unchanged
- layout-revised: county-magistracy-example - T265: the granary moved from the office court to the inner court's north wall behind the offices, with a side gate of its own in the north wall; an armory bay at the office hall's west end, the hall 14 ft longer; the tax archive west of the hall and the hearing court recentered under the dais
- layout-revised: county-magistracy-example - T274: the granary out of the household's inner court (T265's seat and north cart gate withdrawn) to the head of the office court's east column, refused in the inner court by the generator; the barracks back below it in the south-east corner; the office hall centered in its free ground and the hearing court re-cut under the dais

## Tasks

### Setup (plan work breakdown 1)

### Foundational (plan work breakdown 2-4; blocks every guard)

### User Story 1 - every tool call answers at once (plan work breakdown 5, 7)

Each guard task, in the order below (the measured cost first, research R2, then the settings' order): the guard's decider in `rust/guard/src/guards/<guard>.rs` with its unit tests; its suite `tests/hooks/test-<guard>.sh` run with `HOOK` pointed at `l7r-guard --only <guard>` until every case passes (a case whose verdict changes is a constitution XIV fix, named in the commit - FR-002), the suite's own inline Python replaced in the same task (plan work breakdown 7); then, in ONE commit, the decider registered, `scripts/hooks/<guard>.sh` deleted and its `.claude/settings.json` entry removed (FR-003), landed with `make land-tooling`.

### User Story 1 - the suites' tooling and the close (plan work breakdown 6-8)

### User Story 2 - the gate is Rust (phase 2, opened 2026-11-08 by a plan amendment)

### Phase 3 (moved by the round arbiter's ruling `ask:449-hm-checks-route`, 2026-11-08; ported in one cut with their Python callers, FR-001)

## Dependencies

T001 -> T002 -> T003 -> T004 -> T005 -> the guard tasks (each depends on T002-T005, not on another guard) -> T050, T051 -> T052. A guard task whose decider needs a shared fact the library lacks extends T003's library in the same task.

## Parallel opportunities

The 44 guard tasks are independent of one another once T005 has landed: each touches its own decider, suite and settings entry. They land one at a time (each its own `make land-tooling`), since the settings file is shared.

## Implementation strategy

MVP: T001-T005 and the first guard, `pair-hooks` (T006): the dispatcher in every session with the slowest guard moved, its suite green, the call timed. Then the guards in order, each landed as it passes, so the session speeds up guard by guard.
- [ ] T158 Phase 4 S13, the deletion close (ask:449-phase4-slices) Q10: tools/claims.py and claims_context, claims_counters, claims_scope, claims_stale, tunables, gates/codeid.py, dead_closure, bundle_door, tools/__init__, l7r/diagram/__init__ deleted (2,443 lines), the claims re-keyed by claims carry, ruff, pyproject's list and the requirements files gone; the phase-4 close; and the Python left with no importer or reader after T222 (found 2026-11-19): l7r/diagram/interactive/, work_counts.py and knobs.json (no reader found), the shapely and scipy dependencies, scripts/gates/codeid.py's split_ids, l7r/diagram/CLAUDE.md's row for a switches.py that does not exist, and the make-only guard's pattern for the deleted hamletgen/__main__.py - each deleted after a measured check that nothing reads it; and `l7r-gate cohort fresh-seed`, whose one outside caller was the deleted make probe (T230, 2026-11-19), deleted if nothing else calls it
      research: rendering
- [ ] T252 Constitution VI's one self-scoping command, make maps (1.12.0, 1.12.1), on the GM's answer (found by T228, 2026-11-22; escalation-check KEEP): its tool went with the Python engine and today's are two commands, make map MAP= and the pool sweep make rust-test CRATE=rust/mode_a, which the clause forbids - the GM ruled 2026-11-22 (request.md, "okay good, please proceed on that basis then"): build the one self-scoping command over the Rust sweeps, a tier table with a named reference map per tier (Mode A and hamlets now, each larger tier its row as it lands), the clause kept and the new command's name put in as upkeep, no version
      research: rendering
- [ ] T259 make work-budget-bundle reads a stage's last run file silently, however old (found by 449 T253's builder, 2026-11-22: the waterward.polder MODE AUDIT's first round read UNCOUNTED because the bundle took a run file from 2026-11-20, a plain make work-budget writing none; re-run with WRITE=1 it read OVER at 4,677) - measured first how the bundle picks its run file and how often a bundle read one older than the tree it judges, then the bundle refuses a run file whose code key is not the tree's, naming make work-budget WRITE=1, red first on that shape
      research: rendering
- [ ] T260 0091 and 0115 put a household's servants on opposite sides of the house (found by 449 T249's claims re-check, bundle t249-01, 2026-11-22; found.jsonl row 139): research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.html block 127 guesses 'any servants' range stood in the shady rear, with the storehouses' (the Miwa house's chugen hut outside the back door), while 0115's findings and drawing page and docs/buildings.md put menservants and gatekeeper in a street-edge range and never draw a servants' rowhouse behind the house; a reader of 0091 expects a rear servants' range no sheet draws; a page session reconciles 0091's guess with 0115 (or records why they differ) and re-runs the record checks; no code changes
      research: rendering
- [ ] T275 The armory pop-up and sheet held to size-audit 2026-11-22's two questionables: Kaibara's store of arms as one or two eight-mat rooms (Q2: the Tamba page does not say how many of the three it took, where 0097 reads one), and the armory drawn in the hall's back row against Pingyao's full-depth end bay (Q1); a research pass on 0093 and 0097 first; lands before 449 T158
      research: rendering
- [ ] T276 An armory drawn on the four magistracy sheets that have none (hayakawa-magistracy, ochiba-magistracy, ubame-magistracy, ochiba-roundtrip-test; measured 2026-11-22 by a grep of their svg for data-kind armory), then the magistracies program's armory item made required in types.json (impl-drift 2026-11-22: knob 4 says every seat keeps one, the program holds it optional); lands before 449 T158
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
- [ ] T277 an off-the-wind seat keeps its belt's ground behind its back, not on its windward side (found by 449 T261, 2026-11-22): where a declared fall runs into the wind (Sawada, down_deg 225 into its northwest wind), rust/phases/src/seat.rs::seat takes the high margin with the cluster's back to the hill (Frame.offwind), and rust/phases/src/driver.rs::settlement_ground reaches the settlement's ground along Frame.out toward the belt, so the dry hem keeps off a belt strip on the hill side; research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html says every belt stands on the windward side (north and west) and the settlement is laid out with its back to it; a reader of Sawada's map would see the belt's kept ground uphill to the southeast, away from the wind; the belt's ground (and the belt stage when it is unparked) takes the windward side on an offwind frame, or 0072's drawing page records the offwind case, decided by the record; driver.rs's 'the seat's back to the wind' claim (line 411) restated with it
      research: rendering
- [ ] T278 0116's drawing page puts Ochiba's granary in the south-east corner of its office court (§231), against the manor procedure's granary at the head of an office-court flank column beside the office hall (found by impl-drift on 449 T274's claims, bundle t274b, 2026-11-22, outside that change): restate the page or move the sheet's granary, whichever the record supports
      research: rendering
- [ ] T279 docs/buildings.md's office hall claim gives Hayakawa's hall as 113 x 28 ft where 0090's drawing page (§15) gives 113 x 38 ft (found by impl-drift on 449 T274's claims, bundle t274b, 2026-11-22, outside that change): restate the claim to the page's size, or the page if the 28 is right
      research: rendering
- [ ] T280 The county magistracy example's karo's door and the next long-house bay open onto a 7.5 ft lane against the tax archive's blank west wall, 4.2 ft at the fire-tub (building-review N1 on 449 T274's sheet, 2026-11-22: T274 moved the archive 13.5 ft west; nothing sets a retainer bay's frontage, a nitpick): give the bays open court or record the lane
      research: rendering
- [ ] T281 docs/buildings.md's Outer court Granary bullet says the granary 'stands behind the offices', but the seat it then gives (north face on the divider, beside the office hall's end) is level with the hall, and behind the hall is the household's court the bullet refuses (impl-drift OUTSIDE THE CHANGE on 449 T274's re-check, bundle t274e, 2026-11-22): restate the clause as 'on the office side'
      research: rendering
- [ ] T282 Two shrine pop-ups' Rokugan rules rest only on drawing pages (modal-research M8/M13 on 449 T254's bundle, 2026-11-22): sheet/approach.md's one, three or seven arches and sheet/sanctuary.md's Fortune as the deity are the GM's canon stated only on 0220's and 0222's drawing pages, so no Entry page carries them; each canon sentence quoted in a comment and stated on 0220's and 0222's findings text as 0229's acolytes were (449 T262), and modal-research re-run on both pop-ups; lands before T244
      research: rendering
- [ ] T283 0028's and 0229's quote-check findings outside 449 T254's change (2026-11-22): on 0028, sugiura-1973-fuzoku-7's original likely ends in the paper's full-width period, not the ideographic one, and its 'snowy district' heading rests on Sabusawa's snow figures where the paper's own sentence (p. 146) should be quoted; matsumoto-dosojin-2 reads 花見 as Hanami where the place is Kemi; ido-jawiki (both notes files), sugiura-1973-fuzoku-4 and nakasendoway-dosojin join passages without '; '; on 0229, the opening's 'with a small house for its monk' generalizes onga-choshi-jiin-4's one temple (PARTIAL) and the drawing item 'The village's shrine is its parish temple.' lacks its period; a page session restates each to its source and quote-check re-runs; lands before T244
      research: rendering
- [ ] T284 Five pop-ups' open form and research findings (449 T254's modal rounds, 2026-11-22): hamlet/byre.md's look paragraph says nothing of the stable's walls or whether its front closed (modal-form M5; a research pass, then an answer or 'not recorded'); hamlet/well.md's guess 'about one well in three has a roof' sits beside a count of one well house to five farms with no reckoning between them (M11); choice/byre_form--yard_shed.md leaves 0108's Kinki farm stable of about 3 m square unreconciled with 0048's silence on a smallholder's byre size, and 0128's dug stable floor unasked (GAPS); sheet/wood-kami-altar.md's About does not say why Ubame's Inari shrine keeps a wood kami's altar or whose hand keeps it (canon: the GM's notes, else 'not recorded'); sheet/shrine-altar.md's emblem marks are a convention no drawing page records; each fixed and its modal checks run; lands before T244
      research: rendering
- [ ] T285 A hill shrine's burial ground can fall in its yard (impl-drift on 449 T254's shrine claims, 2026-11-22, DRIFTED outside the change): docs/building-programs.md's claim 'a hill shrine's village keeps its burial ground apart' and its burial_ground row follow 0236 ('a village whose shrine stands on a hill always takes a ground apart'), but the composition rule and knob 4 roll yard or apart with equal weights for every sheet on no map, with no hill exception, so a hill-shrine sheet on no map can draw graves in the shrine's yard; the hill exception put into the composition rule and the knob, the claim re-checked IN-STEP; lands before T244; its plan finds every live copy from what reads knob 4, not from one search pattern (449 T254 MODE 4, 2026-11-22)
      research: rendering
- [ ] T286 0222's two record findings outside 449 T254's change (quote-check and record-format, rounds 2 to 11, 2026-11-22): the drawing page's wealth-knob bullet says 'They are gifts a parish gave its shrine as it grew richer' and 'The strength stones stand beside the approach' with no footnote or link (the findings page's 'Most of what else stood in a precinct was given to it, piece by piece' may be what they rest on), and the nara-byakugoji-hondo-2 note's 'formal tile roof, single-piece S-curved tiles' (hongawarabuki, sangawara) has no glossary term; each linked or footnoted and the terms glossed in a page session, its checks run; lands before T244
      research: rendering
- [ ] T287 The country shrine dwelling's two known drifts, landed before the next port (found by 449 T254's claims round, 2026-11-22; the GM 2026-11-18: fix all known bugs in each step before porting the next): docs/building-programs.md's dwelling entry tags a plain earth-floored vestibule genkan, where the Edo genkan is an entrance with a shikidai (0104), so the monk's plain vestibule reads as a formal guests' entrance, and its kitchen is drawn all earth floor, where the kamado stood on the doma 'as a rule' and a kitchen of earth throughout is not attested (0107), so the kitchen reads as having no floored part; both are 417 T33's items (the genkan tag, the all-earth kitchen) - this box lands them, through 417 T33's own work or here, re-checks the two claims, and lands before T244
      research: rendering
- [ ] T288 The county magistracy example's karo's door opens onto open court again (building-review 2026-11-22 E1, engine key 6d0cb7befee0): T274's recentred hall pushed the tax archive to 34.5-52.5 ft, 7.5 ft off the senior retainers' long-house face at 27 ft, so the karo's door and his neighbor's face its blank west wall down a dead-end lane (pack-audit 7.5 ft H at svg(113,358)); where the archive goes is the builder's call; lands before 449 T244
      research: rendering
- [ ] T289 Where a guarded seat with a standing barracks and no gate range kept its arms (building-review 2026-11-22 Q2): the record's one hall armory, Pingyao's, served a seat with no standing barracks, and Kaibara's gun store stood in its gate range across from the guardroom (0093); a research pass first, then docs/building-programs.md's knob 4 restated or the county example's armory re-seated; lands before 449 T244
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
- [ ] T290 The armory's size band held to its two forms (size-audit 2026-11-22 S3, S4): types.json's band (w 12-24, h 12-40, no area) admits 24 x 40 ft, about 6.7x the Kaibara room; record the audit's form bands (gate range w 11-13, h 11-25, 120-320 sq ft; hall end bay w 11-18, h 11-41, 120-740 sq ft) through RequiredItem.forms, and docs/building-programs.md's 'about 12 ft square' restated as 12 x 12 to 12 x 24 ft; lands before 449 T244
      research: rendering
- [ ] T291 The county magistracy example's office hall has no formal entrance facing the gate, as Takayama's has (building-review 2026-11-22 N2, outside the change): judged against the record, then drawn or recorded as a deviation; lands before 449 T244
      research: rendering
- [ ] GM review (make gm-reviewed F=449) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
