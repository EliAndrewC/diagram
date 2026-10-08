# The Markdown audit (feature 329, FR-012)

Every `.md` file under `.claude/skills/diagram/` at `5e2ba4824`, 389 files. The 85 documentation files were judged one
by one by four readers (Opus, 2026-10-07, one per slice, brief in the session scratchpad: read each file, check what it
names against the code and the Makefile, apply the GM's documentation rules); the session took the final call. Paths
are post-move (the prefix dropped). Three kinds are judged as a class (FR-012), every member listed in the appendix.

## Final calls (where the session departs from a reader, or settles a choice)

- `wip/README.md`: the reader said DELETE (wholly stale). KEPT, and raised with the GM: a README is the GM's to write
  or remove (`readme-hooks.sh`; the GM: "you personally should literally never touch a readme file"), and an audit
  request is not the explicit delegation that guard's one escape asks for.
- Destinations for the files that leave the project root: `SKILL.md` -> `docs/usage.md`; `buildings.md` ->
  `docs/buildings.md` and `buildings/programs.md` -> `docs/buildings/programs.md` (Mode A usage, beside the usage
  document; the claims-index keys and `_claims.py` move with them); `migration-plan.md` -> `docs/migration-plan.md`;
  `timings.md` -> `dev/timings.md`; `dev/skill-boundary.md` -> `docs/package-boundary.md` (no longer about a skill);
  `dev/reviews.md` -> `docs/reviews.md`; `dev/switches.md` -> `docs/switches.md`. The root then holds no loose document
  but `CLAUDE.md`.
- `dev/` stays the engine-development folder and `docs/` the repository's process; the root `CLAUDE.md` says so.
- `l7r/diagram/CLAUDE.md`'s command map: dropped from the auto-loaded file; `docs/make-targets.html` is generated from
  the Makefile's `##` lines, so a row it lacks is added as a `##` line there.

## Class verdicts

- **The modal write-ups** (`l7r/diagram/interactive/assets/modals/{choice,hamlet,sheet}/*.md`, 274 files): KEEP in
  place. They are content the page build reads (feature 319), in a form `modal-form` and the gate hold; the move
  changes nothing in them.
- **The pool's per-map notes** (`pool/*/*/*.notes.md`, `legacy-hand-authored-pool/*/*/*.notes.md`): KEEP in place. Each
  is the record beside its map, written for the GM and read by the review agents and `pack_audit`.
- **The verbatim records** (none are Markdown under the skill directory except the logs' `CLAUDE.md` files, which
  were judged individually in slice 2).

## Slice 1 - the skill root, buildings, future-work, wip (21 files: KEEP 6, TRIM 4, TRIM+MOVE 3, SPLIT 1, DELETE 7)
| file | lines | verdict | reason |
|---|---|---|---|
| CLAUDE.md (skill index) | 18 | DELETE | Its 3-row "what to read" table goes into the root CLAUDE.md; "why this file is short" is history; "run as modules from this directory" is false after the move; it would collide at the root. |
| SKILL.md | 291 | SPLIT + TRIM -> docs/usage.md | Usage parts (two modes, workflow incl. water-flow-first and city knobs, scale ladder, labeling, short output/tree summary, setting-file list) -> docs/usage.md. Mode A-only parts (canvas, palette, patterns, orientation, title block, framing, label sizes, Edo/Sengoku framework) -> docs/buildings.md. China-first -> docs/research-doctrine.md + one root bullet. "The working rule behind the tooling" deleted (duplicates root + efficiency-tooling). Interactive-map paragraph -> one line. Render pipeline: env check -> docs/container.md, draw order -> dev/placement.md, env knobs dropped (duplicate dev/loop.md, stale). Tracking -> dev/pool.md (stale: legacy renders no longer committed). References: bare index; stale hamletgen/test_villages/pyproject bullets deleted. Step 5 trimmed to the pack_audit red-fixture rule. Broken ../relic, ../temple links and the /gm-assistant mount fixed. |
| buildings.md | 353 | TRIM + MOVE docs/buildings.md | Live Mode A procedure with Research: claims (claims-index keys + _claims.py BASE_PATHS + agents re-pointed). Fix "swept patch" (feature 280: open earth) and the modest-shrine torii-silhouette contradiction; "iterate until no findings" -> two rounds on the occasion; cut used-to-say narratives, keep don't-re-add kernels. |
| buildings/programs.md | 224 | KEEP + MOVE docs/buildings/programs.md | Generated tables + live prose; fix "swept patch"; re-point tools/building_programs.py and the Makefile target. |
| flophouse-research.md | 297 | DELETE | Settled 2026-07; decisions live on research 0185 and 0122; cites retired check_village checks. |
| future-work/CLAUDE.md | 90 | TRIM | Keep table + rules 1-5; cut the 3,453-line story, "why these groupings", the guesswork essay (one line). |
| future-work/cities.md | 89 | KEEP | Audited 2026-10-07; open. |
| future-work/closed.md | 145 | TRIM | Drop the 2026-08 heading-only lines and the 08-24 audit narrative. |
| future-work/compounds.md | 80 | KEEP | Open items. |
| future-work/cross-cutting.md | 104 | KEEP | Open. |
| future-work/farming-communities.md | 244 | KEEP | Open, re-measured 2026-10-07. |
| future-work/towns.md | 56 | KEEP | Open; receives the carried town items. |
| hamletgen.md | 594 | DELETE | "EXPERIMENT, not adopted" header contradicts adoption; describes retired check_village, the 695-manifest corpus; stage docs live in hamletgen/CLAUDE.md, polder status in migration-plan. Carry the "three lessons that outlived their bugs" to dev/lessons.md; re-point SKILL.md, dev/pool.md, comb.py, roll.py. |
| migration-plan.md | 351 | TRIM + MOVE docs/migration-plan.md | Open standing plan (test_docs_match_the_mechanism reads it). Stale: pool count, "189 checks", last-updated, ratchet history, "the old instruction here", regression corpus, retired timings command. |
| pending-enclosed-fan-floor.md | 63 | DELETE | Restore recipe targets removed gate()/pool/regressions/tests/check_village. Carry the rule (an enclosed fan under 8 real acres reads below hamlet grade) to future-work/towns.md; fix the pointer in research 0017's drawing page. |
| timings.md | 425 | MOVE dev/timings.md + TRIM header | Frozen ledger (blocks verbatim); cut the stale re-measure instructions; re-point its six readers. |
| town-checks-audit.md | 100 | DELETE | 2026-07-21 audit of the retired battery; carry the generator-parity gaps to future-work/towns.md. |
| town-deep-audit.md | 266 | DELETE | 2026-07-24 audit of frozen towns against a retired rule file; carry 6.1, 6.3, 7.2-7.5, 8.2, 8.4, 8.7, 8.8 to future-work/towns.md; fix the works-cited comment naming it. |
| wip/README.md | 44 | DELETE | Wholly stale (the GM dropped the hand pass 2026-10-07); one line to wip/shiro_daika/CLAUDE.md; fix the .gitignore comment pointing at it. |
| wip/shiro-daika.notes.md | 504 | KEEP | Exhibit notes, verbatim; one status line at the top. |
| wip/shiro_daika/CLAUDE.md | 48 | TRIM | Keep part order, the isort warning, the table; cut the carve-out, loop-fix and feature-021 stories. |

## Slice 2 - dev/ (19 files: KEEP 2, TRIM 10, SPLIT 3, MOVE+TRIM 3, DELETE 1)
| file | lines | verdict | reason |
|---|---|---|---|
| dev/RESUME-HERE.md | 74 | DELETE | 2026-08-24 handoff; "Still open: Nothing"; points at retired make explain; its ruling is in hamletgen/driver.py and placement.md. Carry the feature-128 lane lessons to dev/lessons.md. |
| dev/bypass-log/CLAUDE.md | 52 | TRIM | ~30 lines verbatim from run-log/CLAUDE.md; links nonexistent ../perf-log/README.md. Keep the outcome meanings; point to perf-log/CLAUDE.md for the directory rule. |
| dev/cache.md | 89 | TRIM | Accurate; gate maps now via tests/gate/_pool.py not tests/test_villages.py; drop the "split out ... verbatim" opener. |
| dev/decisions.md | 141 | SPLIT | The two "don't put a question to the GM" sections (repo-wide; partly repeat root CLAUDE.md and docs/research-doctrine.md 139ff) merge into docs/research-doctrine.md; the engine rules stay. |
| dev/diagnostics.md | 199 | TRIM | tools/site_justice.py and crop_map.py are gone; cut their usage, keep the lesson; why_placed/open_seat/make why-placed live. |
| dev/gate.md | 232 | TRIM | Cut "READ THIS FIRST IF YOU REMEMBER THE CHECK BATTERY", most of "Why it went", the retired make check-census line (keep its lesson). |
| dev/idle-log/CLAUDE.md | 11 | KEEP | Short, accurate; written by idle-tests-hooks. |
| dev/lessons.md | 468 | TRIM | Leftover "## 3." numbering, "see #1" dangling; shell/git lessons now enforced or in docs/efficiency-tooling.md (backticks in -m, setsid --fork, worktree .git) dropped; engine lessons stay. |
| dev/loop.md | 647 | SPLIT + TRIM | Stale: tests/test_regressions.py and its replay gone; direct python3 -m pytest / ruff (refused by hooks); timings.md frozen; make reference gone; broken half-sentence in the remote section. Keep probe vs survey, same-edit test updates, one pool-wide dry run. Remote-runs table -> docs/. Dated measurement sections -> delete (specs hold them). |
| dev/modals-particular.md | 43 | TRIM | P3 names three tabs; M4 now four (Depiction, GM 2026-10-04). Fix the line. |
| dev/modals.md | 180 | KEEP | Live contract read by _modal_bundle.py and the modal agents. |
| dev/perf-log/CLAUDE.md | 43 | TRIM | Becomes the one home of the "directory, not one file" rule (with the GM's 2026-08-24 quote); shorten the README story; its python3 -m perf_snapshot example -> make targets. |
| dev/performance.md | 1126 | SPLIT | Lines 1-330 lasting doctrine stay; ~800 lines of per-feature "what it bought" sections are landed history -> one "levers measured and withdrawn - don't re-try" list, the rest dropped to the specs. |
| dev/placement.md | 598 | TRIM | STAGES table matches driver.py (18 stages); the hand-authored phase model and capital-era findings concern frozen legacy maps -> cut. |
| dev/pool.md | 179 | TRIM | pool/regressions/ gone; regression replays, test_checks, re-gated, waivers stale; "superseded by the freeze" and "found SIX things" history; detached-worktree rule repeats root CLAUDE.md; listing out of date (country-shrines/, a round-trip magistracy). |
| dev/reviews.md | 184 | TRIM + MOVE docs/reviews.md | Repo-wide process; the pre-294 history section describes replaced machinery; backstory-review has no agent file. |
| dev/run-log/CLAUDE.md | 52 | TRIM | Directory text repeats bypass-log; nonexistent perf-log/README.md link; keep the field list and the GM quote. |
| dev/skill-boundary.md | 92 | MOVE docs/ + TRIM | Repo-level architecture; rewrite every "skill" framing as one package; re-check finding 1 (compound.py into settlements) - the segments/check_village evidence was retired by 166. |
| dev/switches.md | 74 | TRIM + MOVE docs/ | Remote switch is repo-wide CI; cut "why only one axis now"; keep unknown-key-ignored and idle_context/GREEN_TARGETS warnings. |
dev/ stays (engine development); docs/ = repo process; logs stay in dev/; root CLAUDE.md says which is which.

## Slice 3 - the engine's CLAUDE.md files (27 files: KEEP 5, TRIM 22 incl. 5 with SPLIT/MERGE/MOVE)
Load cost: l7r/diagram/CLAUDE.md is 33 KB and loads for every engine file (pool/ and tests/ import it).
| file | lines | verdict | reason |
|---|---|---|---|
| l7r/diagram/CLAUDE.md | 309 | TRIM + MOVE (to ~100 lines) | Command map -> docs/make-targets (generated; rows it lacks go in the Makefile ## lines) and dev/loop.md; dead "retired scope lock" row; root-CLAUDE.md duplicates (iterate once, worktree, XIV, XVI, reviews, knob ladder, claims) -> pointers; stale bare python3 -m commands, a broken sentence, tools/site_justice.py; index misses buildings/, dwellings.py, switches.py; drop the history comment and "used to carry 1,449 lines"; rewrite the skill framing. |
| l7r/diagram/ci/CLAUDE.md | 155 | TRIM + SPLIT | "soak suite is EMPTY" false; modules missing gate_plugin, imagecheck, rollcensus, rollverdict; measurement route / threat model / verified/ path -> new dev/ci.md. |
| l7r/diagram/hamletgen/CLAUDE.md | 115 | TRIM | water/ row names wrong files; stale homesteads.py and fixtures_min rows; missing clearance.py; cohort reproduction recipe stale (feature 214); "earlier version blamed" narrative; obsolete byte-identity verification; draw-order pointer -> dev/placement.md; MOVE-never-copy -> pointer to sitegen. |
| l7r/diagram/hamletgen/hinterland/CLAUDE.md | 16 | KEEP | Accurate; the repeated "Split from... LAYERS" boilerplate shrinks to one line. |
| l7r/diagram/hamletgen/homesteads/CLAUDE.md | 21 | TRIM | Missing 7 of 17 modules. |
| l7r/diagram/hamletgen/water/CLAUDE.md | 28 | KEEP | Matches; drop "bodies are verbatim". |
| l7r/diagram/hamletgen/ways/CLAUDE.md | 39 | TRIM | Missing gateway, keeper, street; knots row -> one line, mechanism to the docstring. |
| l7r/diagram/interactive/CLAUDE.md | 235 | TRIM + SPLIT | page.py/raster.py measurement paragraphs + the blue-plot two-tint table -> new dev/interactive-page.md; keep the GM-only notes ruling, don't-re-add-a-lead, no-browser-rolled-page, tagging; missing choices, conditions, extents, glossary_source, record/; classes.py is a package; page-check duplicated in the child. |
| l7r/diagram/interactive/classes/CLAUDE.md | 107 | TRIM + MERGE | "explanation IS the docstring" superseded by modal files (319) -> delete; "the conversion" -> one line; "when a section a modal was written from moves" -> dev/modals.md, rewritten for modal files and entry-gate. |
| l7r/diagram/pipeline/CLAUDE.md | 95 | TRIM | Rollcache history -> one line; python3 -m regen -> make map(s); THE TRAP pointer -> dev/cache.md; feature-161 narrative -> rule. |
| l7r/diagram/settlement/CLAUDE.md | 75 | TRIM | Package rows -> one-line pointers to children; missing farm_fixtures, see_through; draw-order -> dev/placement.md; retired make hamlet-floor; 94% ratchet history -> one line; becomes the one home of the Monkeypatching and Mixins/mypy notes. |
| l7r/diagram/settlement/_geom/CLAUDE.md | 121 | TRIM | Missing region, water_index; names retired check_village; rolling is a package; census story; Monkeypatching duplicate. |
| l7r/diagram/settlement/city/CLAUDE.md | 84 | TRIM | "The oracle" obsolete (frozen exhibits, byte identity dropped); stage-2 history -> one rule; missing crop, knobs; Mixins duplicate. |
| l7r/diagram/settlement/civic_grounds/CLAUDE.md | 185 | TRIM + MOVE | Drop the size-history narratives; stable-yard stages table and RNG rules -> stable_yard.py docstring (3-line pointer stays); missing edge_seat; Monkeypatching duplicate. |
| l7r/diagram/settlement/fields/CLAUDE.md | 87 | TRIM | Wrong test path; function-scale history; Monkeypatching duplicate. |
| l7r/diagram/settlement/homestead_parts/CLAUDE.md | 24 | TRIM | Missing belt_law, fixture_seats, tree_shade, wood_share; drop line counts. |
| l7r/diagram/settlement/land/CLAUDE.md | 84 | TRIM | Missing outline; feature-120 "did not move here" history; "two relocations priced and declined"; skill-CLAUDE.md pointer -> dev/decisions.md; Mixins duplicate. |
| l7r/diagram/settlement/rolling/CLAUDE.md | 109 | TRIM | Missing fit_index, gap_ways, lot, passage; partial import graph -> drop; center-vs-footprint pointer -> dev/placement.md; stale line count; Monkeypatching duplicate. |
| l7r/diagram/settlement/shrines_wells/CLAUDE.md | 114 | TRIM | Missing forest; retired check cited as live; open_seat pointer -> dev/diagnostics.md; stale narrative; Monkeypatching duplicate. |
| l7r/diagram/settlement/structures/CLAUDE.md | 96 | TRIM | Missing urban_fixtures; fixtures.py is a package. |
| l7r/diagram/settlement/structures/fixtures/CLAUDE.md | 15 | KEEP | Matches. |
| l7r/diagram/settlement/water_ways/CLAUDE.md | 18 | KEEP | Matches. |
| l7r/diagram/sitegen/CLAUDE.md | 47 | TRIM | "Why it is small" -> the rule; the one home of MOVE-never-copy. |
| l7r/diagram/tools/CLAUDE.md | 107 | TRIM | Lists absent tools (site_justice, timings, jogs, crop_map); misses 15 tools; "Known stale, recorded rather than fixed" -> fix and delete; python3 -m -> make targets. |
| l7r/diagram/tools/pack_audit/CLAUDE.md | 20 | TRIM | Missing __main__, labels, registry, shared, sun. |
| l7r/diagram/waterfields/CLAUDE.md | 40 | TRIM | Broken banks.py row (_absorb deleted by 302); missing twins.py; hill.py paragraph into the table; partial import DAG; retired make hamlet-floor. |
| l7r/diagram/waterfields/seams/CLAUDE.md | 13 | KEEP | Current. |

## Slice 4 - research/, tests/, pool/ (19 files: KEEP 11, TRIM 7, one also SPLIT)
| file | lines | verdict | reason |
|---|---|---|---|
| research/CLAUDE.md | 332 | TRIM + SPLIT | Auto-loaded on every research turn (~30 KB). Repeats the root CLAUDE.md Research section (archive-first, write cap, make lines/append, bundles, download-add); "a cheaper check is proved" repeats docs/research-record-rules.md; the feature-292 PILOT section is stale (signed off 2026-09-30) and with it the "where it still has one" Sources-roster clauses; the retired feature-211 citations-pages note is history. Split out: the download list workflow -> research/downloads.md; "Which check is owed" + claims -> research/record-checks.md (each "Load this file when:"). Keep the "Where things are" table, Editing, citation forms, four labels. |
| research/STYLE.md | 224 | TRIM | Current (record-style, style-prepass). Stale: "awaiting the GM's confirmation in the pilot" (accepted 2026-09-30), the "(inferred - the Nth pilot)" tags collapse to "inferred"; section 4 names the GM's TO-DOWNLOAD.md copy - wrong since feature 313 (research/to-download.md via make download-add). |
| research/to-download.md | 3891 | KEEP | The canonical download list; scripts/_downloads.py reads it and the push holds it append-only; old parts are list history. |
| tests/CLAUDE.md | 217 | TRIM | Says python3 -m pytest (refused by make-only-hooks -> make quick / make test-file); points to "the skill's ../CLAUDE.md"; names retired make check-census and hamlet-floor, nonexistent gate/test_scripted_fixtures.py and pool/regressions/; title "the diagram skill's test bed"; directory table misses labels/, gate/, tooling/ and tier dirs; interactive/ row is feature history. |
| tests/fixtures/hoshigaoka-off-map-red.notes.md | 8 | KEEP | Read by pack_audit (onmap.py:57, report.py:86) beside its red fixture. |
| tests/fixtures/shrine-synthetic.notes.md | 5 | KEEP | Read by tests/tools/test_shared.py:198 (the pack_audit declaration). |
| tests/full/interactive/page_browser/CLAUDE.md | 16 | TRIM | Index misses test_page_lit.py; the "Retired 2026-09-07" story -> one don't-re-add line (3.9 GiB at 8 workers). |
| tests/hamletgen/ways/CLAUDE.md | 34 | TRIM | Index covers 14 of 27 test files; add the 13 missing, drop per-file counts, preamble to one line. |
| tests/settlement/CLAUDE.md | 27 | TRIM | python3 -m pytest "from the skill dir" -> make test-file; wrong index pointer (-> l7r/diagram/settlement/CLAUDE.md); one-line rule for the feature-numbered files. |
| tests/settlement/structures/CLAUDE.md | 30 | KEEP | Table matches the directory exactly. |
| tests/soak/CLAUDE.md | 119 | TRIM | Makefile points here; "Why it is empty, honestly" no longer fits (test_village_determinism.py lives here); "why soak not sweep" -> one don't-rename line; retired-tests paragraph -> pointer. |
| tests/tooling/fixtures/brief_load/c1-write.md | - | KEEP | Fixture read by test_brief_load.py. |
| tests/tooling/fixtures/brief_load/g1-check-a.md | - | KEEP | Fixture read by test_brief_load.py. |
| tests/tooling/fixtures/brief_load/h1-check-a.md | - | KEEP | Fixture read by test_brief_load.py. |
| tests/tooling/fixtures/brief_load/owed-buildings-1.md | - | KEEP | Fixture read by test_brief_load.py. |
| tests/tooling/fixtures/brief_load/s-write.md | - | KEEP | Fixture read by test_brief_load.py. |
| tests/tooling/fixtures/brief_load/v2-write.md | - | KEEP | Fixture read by test_brief_load.py. |
| tests/tooling/fixtures/brief_load/x1-write.md | - | KEEP | Fixture read by test_brief_load.py. |
| pool/CLAUDE.md | 3 | KEEP | The @../l7r/diagram/CLAUDE.md import; its comment's "the skill's CLAUDE.md" rewritten by the sweep. |
Pointers to update on the research/CLAUDE.md split: root CLAUDE.md, docs/research-doctrine.md (3), docs/efficiency-tooling.md (1).

## Appendix - every member of the class verdicts

### Modal write-ups (KEEP)
- l7r/diagram/interactive/assets/modals/choice/bamboo--both.md
- l7r/diagram/interactive/assets/modals/choice/bamboo--homestead.md
- l7r/diagram/interactive/assets/modals/choice/bamboo--none.md
- l7r/diagram/interactive/assets/modals/choice/bamboo--thicket.md
- l7r/diagram/interactive/assets/modals/choice/bath_seat--main_door.md
- l7r/diagram/interactive/assets/modals/choice/bath_seat--stable_end.md
- l7r/diagram/interactive/assets/modals/choice/byre_form--courtyard.md
- l7r/diagram/interactive/assets/modals/choice/byre_form--detached_commons.md
- l7r/diagram/interactive/assets/modals/choice/byre_form--yard_shed.md
- l7r/diagram/interactive/assets/modals/choice/caravan_inn_form--hatago.md
- l7r/diagram/interactive/assets/modals/choice/caravan_inn_form--wagon.md
- l7r/diagram/interactive/assets/modals/choice/cluster_position--flank.md
- l7r/diagram/interactive/assets/modals/choice/cluster_position--high_margin.md
- l7r/diagram/interactive/assets/modals/choice/cluster_position--mid_margin.md
- l7r/diagram/interactive/assets/modals/choice/cluster_position--on_rise.md
- l7r/diagram/interactive/assets/modals/choice/cluster_position--valley_head.md
- l7r/diagram/interactive/assets/modals/choice/cluster_position--valley_mouth.md
- l7r/diagram/interactive/assets/modals/choice/cluster_shape--crescent.md
- l7r/diagram/interactive/assets/modals/choice/cluster_shape--elongated.md
- l7r/diagram/interactive/assets/modals/choice/cluster_shape--round.md
- l7r/diagram/interactive/assets/modals/choice/cluster_shape--split.md
- l7r/diagram/interactive/assets/modals/choice/copse_siting--against_the_belt.md
- l7r/diagram/interactive/assets/modals/choice/copse_siting--among_the_houses.md
- l7r/diagram/interactive/assets/modals/choice/dike_crop--fruit.md
- l7r/diagram/interactive/assets/modals/choice/dike_crop--mulberry.md
- l7r/diagram/interactive/assets/modals/choice/dike_crop--tea.md
- l7r/diagram/interactive/assets/modals/choice/family_form--one_roof.md
- l7r/diagram/interactive/assets/modals/choice/family_form--retirement_house.md
- l7r/diagram/interactive/assets/modals/choice/fan_middle--cleared.md
- l7r/diagram/interactive/assets/modals/choice/fan_middle--wild.md
- l7r/diagram/interactive/assets/modals/choice/farm_water--channel.md
- l7r/diagram/interactive/assets/modals/choice/farm_water--well.md
- l7r/diagram/interactive/assets/modals/choice/field_archetype--contour_terraces.md
- l7r/diagram/interactive/assets/modals/choice/field_archetype--mulberry_dike_fishpond.md
- l7r/diagram/interactive/assets/modals/choice/field_archetype--polder_grid.md
- l7r/diagram/interactive/assets/modals/choice/field_archetype--ribbon_valley.md
- l7r/diagram/interactive/assets/modals/choice/field_archetype--valley_paddy.md
- l7r/diagram/interactive/assets/modals/choice/footbridge_form--earthen.md
- l7r/diagram/interactive/assets/modals/choice/footbridge_form--log.md
- l7r/diagram/interactive/assets/modals/choice/footbridge_form--plank.md
- l7r/diagram/interactive/assets/modals/choice/fry_form--fry_village.md
- l7r/diagram/interactive/assets/modals/choice/fry_form--none.md
- l7r/diagram/interactive/assets/modals/choice/grain_drift.md
- l7r/diagram/interactive/assets/modals/choice/grave_form--corner.md
- l7r/diagram/interactive/assets/modals/choice/grave_form--island.md
- l7r/diagram/interactive/assets/modals/choice/grove_sides--2.md
- l7r/diagram/interactive/assets/modals/choice/grove_sides--3.md
- l7r/diagram/interactive/assets/modals/choice/grove_sides--4.md
- l7r/diagram/interactive/assets/modals/choice/hamlet_burial--village_ground.md
- l7r/diagram/interactive/assets/modals/choice/harvest_weather--changeable.md
- l7r/diagram/interactive/assets/modals/choice/harvest_weather--settled.md
- l7r/diagram/interactive/assets/modals/choice/intake--open.md
- l7r/diagram/interactive/assets/modals/choice/intake--weir.md
- l7r/diagram/interactive/assets/modals/choice/kosatsuba_seat--center.md
- l7r/diagram/interactive/assets/modals/choice/kosatsuba_seat--entrance.md
- l7r/diagram/interactive/assets/modals/choice/kosatsuba_seat--frontage.md
- l7r/diagram/interactive/assets/modals/choice/kosatsuba_siting--frontage.md
- l7r/diagram/interactive/assets/modals/choice/kosatsuba_siting--waterside.md
- l7r/diagram/interactive/assets/modals/choice/land_use_overlay--lotus.md
- l7r/diagram/interactive/assets/modals/choice/land_use_overlay--mulberry_fishpond.md
- l7r/diagram/interactive/assets/modals/choice/land_use_overlay--none.md
- l7r/diagram/interactive/assets/modals/choice/land_use_overlay--tea_fringe.md
- l7r/diagram/interactive/assets/modals/choice/lane_skeleton--T.md
- l7r/diagram/interactive/assets/modals/choice/lane_skeleton--Y.md
- l7r/diagram/interactive/assets/modals/choice/lane_skeleton--cross.md
- l7r/diagram/interactive/assets/modals/choice/lane_skeleton--none.md
- l7r/diagram/interactive/assets/modals/choice/lane_skeleton--spine.md
- l7r/diagram/interactive/assets/modals/choice/lane_skeleton--waterside.md
- l7r/diagram/interactive/assets/modals/choice/lane_web--alleys.md
- l7r/diagram/interactive/assets/modals/choice/lane_web--back_lane.md
- l7r/diagram/interactive/assets/modals/choice/leftover--pond.md
- l7r/diagram/interactive/assets/modals/choice/leftover--rice.md
- l7r/diagram/interactive/assets/modals/choice/manure_form--heap.md
- l7r/diagram/interactive/assets/modals/choice/manure_form--pit.md
- l7r/diagram/interactive/assets/modals/choice/paddy_rest--settled.md
- l7r/diagram/interactive/assets/modals/choice/paddy_rest--unsettled.md
- l7r/diagram/interactive/assets/modals/choice/plot_regularity--grid.md
- l7r/diagram/interactive/assets/modals/choice/plot_regularity--organic.md
- l7r/diagram/interactive/assets/modals/choice/plot_size--large_block.md
- l7r/diagram/interactive/assets/modals/choice/plot_size--medium.md
- l7r/diagram/interactive/assets/modals/choice/plot_size--small_irregular.md
- l7r/diagram/interactive/assets/modals/choice/plot_size--strip.md
- l7r/diagram/interactive/assets/modals/choice/pond_layout--grid.md
- l7r/diagram/interactive/assets/modals/choice/pond_layout--mosaic.md
- l7r/diagram/interactive/assets/modals/choice/row_line--edge.md
- l7r/diagram/interactive/assets/modals/choice/row_line--street.md
- l7r/diagram/interactive/assets/modals/choice/row_sides--both.md
- l7r/diagram/interactive/assets/modals/choice/row_sides--one.md
- l7r/diagram/interactive/assets/modals/choice/row_water--own.md
- l7r/diagram/interactive/assets/modals/choice/row_water--shared.md
- l7r/diagram/interactive/assets/modals/choice/settlement_form--dike_top.md
- l7r/diagram/interactive/assets/modals/choice/settlement_form--dispersed.md
- l7r/diagram/interactive/assets/modals/choice/settlement_form--linear.md
- l7r/diagram/interactive/assets/modals/choice/settlement_form--nucleated.md
- l7r/diagram/interactive/assets/modals/choice/settlement_form--water_town.md
- l7r/diagram/interactive/assets/modals/choice/water_sink--offmap.md
- l7r/diagram/interactive/assets/modals/choice/water_sink--pond.md
- l7r/diagram/interactive/assets/modals/choice/water_source_position--chain.md
- l7r/diagram/interactive/assets/modals/choice/water_source_position--corner_NE.md
- l7r/diagram/interactive/assets/modals/choice/water_source_position--corner_NW.md
- l7r/diagram/interactive/assets/modals/choice/water_source_position--corner_SE.md
- l7r/diagram/interactive/assets/modals/choice/water_source_position--corner_SW.md
- l7r/diagram/interactive/assets/modals/choice/water_source_position--corner_high.md
- l7r/diagram/interactive/assets/modals/choice/water_source_position--edge_E.md
- l7r/diagram/interactive/assets/modals/choice/water_source_position--edge_N.md
- l7r/diagram/interactive/assets/modals/choice/water_source_position--edge_S.md
- l7r/diagram/interactive/assets/modals/choice/water_source_position--edge_W.md
- l7r/diagram/interactive/assets/modals/choice/water_source_position--head_center.md
- l7r/diagram/interactive/assets/modals/choice/water_source_position--head_left.md
- l7r/diagram/interactive/assets/modals/choice/water_source_position--head_right.md
- l7r/diagram/interactive/assets/modals/choice/water_source_position--mid_margin.md
- l7r/diagram/interactive/assets/modals/choice/weir_form--crib.md
- l7r/diagram/interactive/assets/modals/choice/weir_form--fence.md
- l7r/diagram/interactive/assets/modals/choice/weir_form--frame.md
- l7r/diagram/interactive/assets/modals/choice/weir_form--gabion.md
- l7r/diagram/interactive/assets/modals/choice/windbreak_belt--conifer_led.md
- l7r/diagram/interactive/assets/modals/choice/windbreak_belt--mixed_broadleaf.md
- l7r/diagram/interactive/assets/modals/choice/winter_crop--barley.md
- l7r/diagram/interactive/assets/modals/choice/winter_crop--none.md
- l7r/diagram/interactive/assets/modals/hamlet/alder.md
- l7r/diagram/interactive/assets/modals/hamlet/barley.md
- l7r/diagram/interactive/assets/modals/hamlet/bath-room.md
- l7r/diagram/interactive/assets/modals/hamlet/buckwheat.md
- l7r/diagram/interactive/assets/modals/hamlet/bund-beans.md
- l7r/diagram/interactive/assets/modals/hamlet/bund.md
- l7r/diagram/interactive/assets/modals/hamlet/burial-ground.md
- l7r/diagram/interactive/assets/modals/hamlet/byre.md
- l7r/diagram/interactive/assets/modals/hamlet/copse.md
- l7r/diagram/interactive/assets/modals/hamlet/drainage-ditch.md
- l7r/diagram/interactive/assets/modals/hamlet/fallow.md
- l7r/diagram/interactive/assets/modals/hamlet/farm-channel.md
- l7r/diagram/interactive/assets/modals/hamlet/farm-holding.md
- l7r/diagram/interactive/assets/modals/hamlet/farmhouse.md
- l7r/diagram/interactive/assets/modals/hamlet/field-pond.md
- l7r/diagram/interactive/assets/modals/hamlet/field-rock.md
- l7r/diagram/interactive/assets/modals/hamlet/fish-pond.md
- l7r/diagram/interactive/assets/modals/hamlet/footbridge.md
- l7r/diagram/interactive/assets/modals/hamlet/fruit-dike.md
- l7r/diagram/interactive/assets/modals/hamlet/fry-pond.md
- l7r/diagram/interactive/assets/modals/hamlet/garden.md
- l7r/diagram/interactive/assets/modals/hamlet/grave-island.md
- l7r/diagram/interactive/assets/modals/hamlet/hen-coop.md
- l7r/diagram/interactive/assets/modals/hamlet/homestead-bamboo.md
- l7r/diagram/interactive/assets/modals/hamlet/homestead-grove.md
- l7r/diagram/interactive/assets/modals/hamlet/household-shrine.md
- l7r/diagram/interactive/assets/modals/hamlet/irrigation-ditch.md
- l7r/diagram/interactive/assets/modals/hamlet/manure-heap.md
- l7r/diagram/interactive/assets/modals/hamlet/manure-pit.md
- l7r/diagram/interactive/assets/modals/hamlet/marsh.md
- l7r/diagram/interactive/assets/modals/hamlet/millet.md
- l7r/diagram/interactive/assets/modals/hamlet/mulberry-dike.md
- l7r/diagram/interactive/assets/modals/hamlet/notice-board.md
- l7r/diagram/interactive/assets/modals/hamlet/paddy.md
- l7r/diagram/interactive/assets/modals/hamlet/perimeter-dike.md
- l7r/diagram/interactive/assets/modals/hamlet/persimmon.md
- l7r/diagram/interactive/assets/modals/hamlet/pig-sty.md
- l7r/diagram/interactive/assets/modals/hamlet/pond-canal.md
- l7r/diagram/interactive/assets/modals/hamlet/pond.md
- l7r/diagram/interactive/assets/modals/hamlet/privy.md
- l7r/diagram/interactive/assets/modals/hamlet/retirement-house.md
- l7r/diagram/interactive/assets/modals/hamlet/scrub-and-rough-grazing.md
- l7r/diagram/interactive/assets/modals/hamlet/shared-bamboo-grove.md
- l7r/diagram/interactive/assets/modals/hamlet/sluice-gate.md
- l7r/diagram/interactive/assets/modals/hamlet/soy.md
- l7r/diagram/interactive/assets/modals/hamlet/storage-shed.md
- l7r/diagram/interactive/assets/modals/hamlet/stream.md
- l7r/diagram/interactive/assets/modals/hamlet/tea-dike.md
- l7r/diagram/interactive/assets/modals/hamlet/threshing-yard.md
- l7r/diagram/interactive/assets/modals/hamlet/village-lane.md
- l7r/diagram/interactive/assets/modals/hamlet/weir.md
- l7r/diagram/interactive/assets/modals/hamlet/well.md
- l7r/diagram/interactive/assets/modals/hamlet/wet-paddy.md
- l7r/diagram/interactive/assets/modals/hamlet/windbreak.md
- l7r/diagram/interactive/assets/modals/hamlet/wood-shed.md
- l7r/diagram/interactive/assets/modals/hamlet/woodland-commons.md
- l7r/diagram/interactive/assets/modals/sheet/ancestral-alcove.md
- l7r/diagram/interactive/assets/modals/sheet/approach.md
- l7r/diagram/interactive/assets/modals/sheet/barracks.md
- l7r/diagram/interactive/assets/modals/sheet/basin.md
- l7r/diagram/interactive/assets/modals/sheet/bath.md
- l7r/diagram/interactive/assets/modals/sheet/bell-tower.md
- l7r/diagram/interactive/assets/modals/sheet/boatmen-s-altar.md
- l7r/diagram/interactive/assets/modals/sheet/border-court.md
- l7r/diagram/interactive/assets/modals/sheet/boundary-stones.md
- l7r/diagram/interactive/assets/modals/sheet/burial-ground.md
- l7r/diagram/interactive/assets/modals/sheet/cart-yard.md
- l7r/diagram/interactive/assets/modals/sheet/cell.md
- l7r/diagram/interactive/assets/modals/sheet/charcoal-bales.md
- l7r/diagram/interactive/assets/modals/sheet/charcoal-store.md
- l7r/diagram/interactive/assets/modals/sheet/cinnabar-workshop.md
- l7r/diagram/interactive/assets/modals/sheet/clerks--room.md
- l7r/diagram/interactive/assets/modals/sheet/clerks--seats.md
- l7r/diagram/interactive/assets/modals/sheet/compound-shrine.md
- l7r/diagram/interactive/assets/modals/sheet/compound-wall.md
- l7r/diagram/interactive/assets/modals/sheet/court-divider.md
- l7r/diagram/interactive/assets/modals/sheet/day-office.md
- l7r/diagram/interactive/assets/modals/sheet/dock.md
- l7r/diagram/interactive/assets/modals/sheet/door.md
- l7r/diagram/interactive/assets/modals/sheet/drying-stones-and-bowls.md
- l7r/diagram/interactive/assets/modals/sheet/engawa.md
- l7r/diagram/interactive/assets/modals/sheet/family-quarters.md
- l7r/diagram/interactive/assets/modals/sheet/fire-water-tubs.md
- l7r/diagram/interactive/assets/modals/sheet/footpath.md
- l7r/diagram/interactive/assets/modals/sheet/fox-border.md
- l7r/diagram/interactive/assets/modals/sheet/garden-pines.md
- l7r/diagram/interactive/assets/modals/sheet/garden-pond.md
- l7r/diagram/interactive/assets/modals/sheet/garden.md
- l7r/diagram/interactive/assets/modals/sheet/gatehouse.md
- l7r/diagram/interactive/assets/modals/sheet/genkan.md
- l7r/diagram/interactive/assets/modals/sheet/granary-stilts.md
- l7r/diagram/interactive/assets/modals/sheet/granary.md
- l7r/diagram/interactive/assets/modals/sheet/guardian-figures.md
- l7r/diagram/interactive/assets/modals/sheet/guest-quarters.md
- l7r/diagram/interactive/assets/modals/sheet/hall-and-dwelling.md
- l7r/diagram/interactive/assets/modals/sheet/hearing-court.md
- l7r/diagram/interactive/assets/modals/sheet/hearth.md
- l7r/diagram/interactive/assets/modals/sheet/inner-court.md
- l7r/diagram/interactive/assets/modals/sheet/inner-rooms.md
- l7r/diagram/interactive/assets/modals/sheet/karo-s-house.md
- l7r/diagram/interactive/assets/modals/sheet/kennel.md
- l7r/diagram/interactive/assets/modals/sheet/kitchen.md
- l7r/diagram/interactive/assets/modals/sheet/kneeling-positions.md
- l7r/diagram/interactive/assets/modals/sheet/lanterns.md
- l7r/diagram/interactive/assets/modals/sheet/latrine.md
- l7r/diagram/interactive/assets/modals/sheet/lord-s-quarters.md
- l7r/diagram/interactive/assets/modals/sheet/magistrate-s-dais.md
- l7r/diagram/interactive/assets/modals/sheet/main-gate.md
- l7r/diagram/interactive/assets/modals/sheet/nakamon.md
- l7r/diagram/interactive/assets/modals/sheet/notice-board.md
- l7r/diagram/interactive/assets/modals/sheet/office-hall.md
- l7r/diagram/interactive/assets/modals/sheet/official-study.md
- l7r/diagram/interactive/assets/modals/sheet/outer-court.md
- l7r/diagram/interactive/assets/modals/sheet/parley-mats.md
- l7r/diagram/interactive/assets/modals/sheet/parley-room.md
- l7r/diagram/interactive/assets/modals/sheet/practice-ground.md
- l7r/diagram/interactive/assets/modals/sheet/precinct-clearing.md
- l7r/diagram/interactive/assets/modals/sheet/rear-yard.md
- l7r/diagram/interactive/assets/modals/sheet/reception-room.md
- l7r/diagram/interactive/assets/modals/sheet/residence-corridor.md
- l7r/diagram/interactive/assets/modals/sheet/residence.md
- l7r/diagram/interactive/assets/modals/sheet/retainers--quarters.md
- l7r/diagram/interactive/assets/modals/sheet/revetment.md
- l7r/diagram/interactive/assets/modals/sheet/river-landing.md
- l7r/diagram/interactive/assets/modals/sheet/river-watch.md
- l7r/diagram/interactive/assets/modals/sheet/river.md
- l7r/diagram/interactive/assets/modals/sheet/road.md
- l7r/diagram/interactive/assets/modals/sheet/sacred-tree.md
- l7r/diagram/interactive/assets/modals/sheet/sanctuary.md
- l7r/diagram/interactive/assets/modals/sheet/servants--quarters.md
- l7r/diagram/interactive/assets/modals/sheet/shrine-altar.md
- l7r/diagram/interactive/assets/modals/sheet/shrine-grove.md
- l7r/diagram/interactive/assets/modals/sheet/shuttered-wing.md
- l7r/diagram/interactive/assets/modals/sheet/side-gate.md
- l7r/diagram/interactive/assets/modals/sheet/stables.md
- l7r/diagram/interactive/assets/modals/sheet/stage.md
- l7r/diagram/interactive/assets/modals/sheet/steelyard.md
- l7r/diagram/interactive/assets/modals/sheet/stone-lantern.md
- l7r/diagram/interactive/assets/modals/sheet/storehouse.md
- l7r/diagram/interactive/assets/modals/sheet/strength-stones.md
- l7r/diagram/interactive/assets/modals/sheet/striking-posts.md
- l7r/diagram/interactive/assets/modals/sheet/sumo-ring.md
- l7r/diagram/interactive/assets/modals/sheet/tally-office.md
- l7r/diagram/interactive/assets/modals/sheet/tax-archive.md
- l7r/diagram/interactive/assets/modals/sheet/tax-barge.md
- l7r/diagram/interactive/assets/modals/sheet/the-monk-s-rooms.md
- l7r/diagram/interactive/assets/modals/sheet/threshold-stones.md
- l7r/diagram/interactive/assets/modals/sheet/torii.md
- l7r/diagram/interactive/assets/modals/sheet/vegetable-garden.md
- l7r/diagram/interactive/assets/modals/sheet/weapon-rack.md
- l7r/diagram/interactive/assets/modals/sheet/weighing-floor.md
- l7r/diagram/interactive/assets/modals/sheet/well.md
- l7r/diagram/interactive/assets/modals/sheet/wood-kami-altar.md
- l7r/diagram/interactive/assets/modals/sheet/writing-pavilion.md
- l7r/diagram/interactive/assets/modals/sheet/writing-room.md

### Pool and legacy notes (KEEP)
- legacy-hand-authored-pool/hamlets/akagahara/akagahara.notes.md
- legacy-hand-authored-pool/hamlets/enokida/enokida.notes.md
- legacy-hand-authored-pool/hamlets/honda/honda.notes.md
- legacy-hand-authored-pool/hamlets/ikegami/ikegami.notes.md
- legacy-hand-authored-pool/hamlets/moritono/moritono.notes.md
- legacy-hand-authored-pool/hamlets/shimizu/shimizu.notes.md
- legacy-hand-authored-pool/hamlets/tanada/tanada.notes.md
- legacy-hand-authored-pool/hamlets/yatsuda/yatsuda.notes.md
- legacy-hand-authored-pool/provincial-cities/minami/minami.notes.md
- legacy-hand-authored-pool/provincial-cities/nagahara/nagahara.notes.md
- legacy-hand-authored-pool/provincial-cities/tango/tango.notes.md
- legacy-hand-authored-pool/towns/hirameki/hirameki.notes.md
- legacy-hand-authored-pool/towns/hoshizora/hoshizora.notes.md
- legacy-hand-authored-pool/towns/ubame/ubame.notes.md
- legacy-hand-authored-pool/villages/hikari-no-sato/hikari-no-sato.notes.md
- legacy-hand-authored-pool/villages/hoshigaoka/hoshigaoka.notes.md
- legacy-hand-authored-pool/villages/kikuta/kikuta.notes.md
- legacy-hand-authored-pool/villages/ueda/ueda.notes.md
- pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.notes.md
- pool/hamlets/inashiro/inashiro.notes.md
- pool/hamlets/kashikawa/kashikawa.notes.md
- pool/hamlets/kuwabata/kuwabata.notes.md
- pool/hamlets/mizuguchi/mizuguchi.notes.md
- pool/hamlets/sawada/sawada.notes.md
- pool/magistracies/county-magistracy-example/county-magistracy-example.notes.md
- pool/magistracies/hayakawa-magistracy/hayakawa-magistracy.notes.md
- pool/magistracies/ochiba-magistracy/ochiba-magistracy.notes.md
- pool/magistracies/ochiba-roundtrip-test/ochiba-roundtrip-test.notes.md
- pool/magistracies/ubame-magistracy/ubame-magistracy.notes.md
