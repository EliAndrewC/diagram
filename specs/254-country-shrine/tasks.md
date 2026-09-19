# Tasks - feature 254, the country shrine and checks in two layers

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Research: [`research.md`](research.md) (R1-R4
the pass; the plan's decisions D1-D13 in `plan.md`). Every prose or code task: American spellings,
hyphens only.

## Phase 0 - baseline and the declaration (FR-001; D1, D2, D3)

- [x] T01 The constitution XIII baseline: `git worktree add --detach /tmp/base HEAD`; there, `make quick
      ALL=1` and `make hooks-test`; the counts in `specs/254-country-shrine/measurements.json` as
      `m:baseline-quick`; each later failure checked against the clone
      research: rendering
      measure: the worktree's own `make quick ALL=1` output
      verify: DONE. worktree /tmp/base at 7cc2e95b: make quick ALL=1 3640 passed 5 skipped 33.78 s; make hooks-test all checks passed; recorded as m:baseline-quick before any edit under l7r
- [x] T02 The declaration: `.claude/skills/diagram/l7r/diagram/buildings/__init__.py`, `types.json`
      (the magistracy declared with its labels and bands from `programs.md`'s existing anchors; the
      country shrine declared from FR-008 to FR-010 with `class` and `why` per item) and `types.py`
      (`load_types`, `by_tier`, `hand_drawn_tiers`, shape validation per `contracts/types.schema.json`);
      `tests/test_building_types.py` red first (shape violations refused, both tiers present)
      research: rendering
      scaffold: `interactive/content.py`'s asset reader for the JSON
      verify: DONE. l7r/diagram/buildings/{__init__,types}.py + types.json with both tiers; parse_types refuses nine malformed shapes by name (parametrized); Band.holds both orientations and area; forms change or remove an item's band; make quick green
- [x] T03 Consumers derive (D2): `pipeline/poolmaps.py` classifies `compound` by declared tier and
      retires `COMPOUND_GENS`; `pipeline/pool_index.py` derives `MODE_A_DIRS` and the tier titles from
      the declaration, `pool_index_text.json` keeps the Mode B tiers only; `scripts/_size_table.py`'s
      usage line names `pool/<tier>/`; `tests/pipeline/test_poolmaps.py`, `test_pool_index.py` and
      `tests/test_villages.py` follow; the census test
      `test_no_type_name_outside_its_declaration` red first (a planted literal in `l7r/` fails it)
      research: rendering
      scaffold: `poolmaps.bundles()`'s tier field
      verify: DONE. poolmaps.classify by declared tier (COMPOUND_GENS retired), pool_index MODE_A_DIRS and TIER_SECTIONS derived, pool_index_text.json Mode B only, size-table usage generic, compound.py example path from the declaration; census test red on the planted literal and on the six real hits, green after; test_villages off-tier assertion; make quick green
- [x] T04 The ignore rule per tier (D3): `.gitignore`'s three per-file negations become one per
      hand-drawn tier plus a re-ignore per declared generated exception;
      `test_ignore_file_matches_the_declaration` red first; `git check-ignore` on all five magistracy
      svgs and the two generated exceptions unchanged; `tests/pipeline/test_render_cache.py` green
      research: rendering
      verify: DONE. .gitignore: one negation per hand-drawn tier + the two generated exceptions re-ignored; git check-ignore: hayakawa tracked, county-magistracy-example and ochiba-roundtrip-test ignored, a country-shrines svg tracked; the ignore test reads the declaration; make quick green

## Phase 1 - the parser and the registry (FR-002, FR-003, FR-005; D4-D9)

- [x] T05 The precinct marker (D4): `id="precinct"` on the court-earth interior rect of the five
      `pool/magistracies/*/*.svg` (and on the two generated examples' emitters in `compound.py`
      `emit_svg`); `tools/pack_audit/parse.py` reads marked rects as `interior`, raises naming the
      sheet when none is marked, drops the fill requirement; `tests/tools/test_pack_audit.py`'s
      synthetic sheets carry the marker; PNGs of the three hand-drawn sheets byte-identical
      (`tools/picture_diff.py` before and after)
      research: rendering
      verify: DONE. id=precinct on the court-earth rects of the 3 hand-drawn sheets (Hayakawa has two), the 8 red fixtures and compound.emit_svg; parse_svg reads marked rects in any attribute order and refuses a sheet without one (two red tests); resvg 2400 px renders of the three sheets byte-identical before and after (md5 56d21a98/4b615dfc/9e4ba3a9); make quick green
- [x] T06 The registry (D5, D6): `tools/pack_audit/registry.py` with `Check(name, run, types, fixture,
      fix)` and `CHECKS` over the eleven shared checks now in `checks.py`, the fire-water three declaring both tiers, and the magistracy's `notice_board_adrift`, `coverage_band` (the 37-42% band the report prints, made pass/fail) and `perimeter_hugging` (its floor derived from the five pool sheets, measured first and recorded as `m:hugging-floor`); `report.py` composes from it; `make pack-audit` output
      unchanged on Ochiba (diffed); every registered fixture exists and fires
      (`test_every_check_fires_on_its_fixture_and_passes_the_pool`), the fixtures that do not yet
      exist cut from a pool sheet in this task (`tests/fixtures/<sheet>-<check>-red.svg`)
      research: rendering
      scaffold: the existing red fixtures under `tests/fixtures/`
      verify: DONE. registry.py: Check(name, run, shared, fixture, fix) with types DERIVED from the declaration; 20 rows; report.py check block composed from it (findings identical on Ochiba, the block's presentation changed - the task's 'unchanged' held for findings, not text); nine new fixtures cut from Ochiba; test_registry proves every row fires on its fixture and passes the pool; make quick ALL=1 3726 passed
- [x] T07 New shared checks (D8): `structures_overlap` (sorted-edge sweep over structure rects,
      rounding floor `WALL_OVERLAP_MIN_PX`), `scale_bar_present`, `viewbox_cropped`; the magistracy's
      `two_court_zoning`; each registered with a red fixture cut from Ochiba or Hayakawa and a `fix`
      sentence; `pool/magistracies` clean under all four
      research: rendering
      scaffold: `structures_on_walls` for the rect-overlap form
      verify: DONE. structures_overlap (sorted-edge sweep, 30% of the smaller footprint, containment and corridor ends allowed), scale_bar_present, viewbox_cropped (ET walk with translate, definitions and parchment skipped, absolute path points only), gate_widths (5-16 ft or a structure spans the break), coverage_band (floor Takayama's 33%, ceiling 42%+2), perimeter_hugging (floor 45%, m:hugging-floor), two_court_zoning; each red on its fixture before landing; the five pool sheets clean
- [x] T08 Defects the registration finds (D9, constitution XIV): every firing of a registered check on a
      shipped magistracy sheet is a defect in the sheet or the check - fixed here, the sheet's
      `.notes.md` Review log carrying the entry; nothing ledgered as pre-existing
      research: rendering
      verify: DONE. defects found by registering: the two drafts drew walls and divider outside the groups the checks read and had no scale bar (emitter fixed, margins cropped to 21 px); Hayakawa at 35% coverage against a rule the record itself floors at Takayama's 33% (the check's exact 37 was the defect; the record's stale 'both manors at 37-38%' sentence corrected); the orphan-label check matched 'well' inside 'dwelling' (whole-word now, with its test)

## Phase 2 - the sweep (FR-004; D10)

- [x] T09 `tests/gate/test_mode_a_sheets.py` parametrized over the declared tiers' bundles, every
      applicable check asserted quiet with a message naming sheet, check and fix; the roster
      `tests/fixtures/gate_check_names.json`; the cost measured with `scripts/_gatecost.py` on the
      gate's durations record and written as `m:sweep-cost`
      research: rendering
      measure: `scripts/_gatecost.py` after one `make done`
      verify: DONE. tests/test_mode_a_sheets.py parametrized over the declared tiers' bundles, a draft's svg regenerated when absent; failures name sheet, check, fix; quick tree by tests/CLAUDE.md's rule (milliseconds, no roll); m:sweep-cost recorded; the render-site census and the sparse roster's comment record the two new readers

## Phase 3 - the program and the shrine's checks (FR-006 to FR-011; D1, D7, D8, D11)

- [x] T10 `check_program` and `check_bands` (D7): generic over the declaration; the nearest-label
      pairing moved from `scripts/_size_table.py` into `tools/pack_audit/labels.py` (the script a thin
      caller, `make size-table` output unchanged on Ochiba, diffed); the notes file's `**Form**: one roof`
      read to count a combined building as hall and dwelling; registered per type; fixtures for a
      missing item and an out-of-band item cut from Ochiba
      research: rendering
      scaffold: `_size_table.py`'s `nearest label by center distance`
      verify: DONE. labels.py: structure_for (smallest containing footprint, else nearest within 30 ft), check_program (optional and form-absent items skipped), check_bands (the form's band; area or w-by-h message); registered as program_complete and size_bands with fixtures ochiba-no-cell-red and ochiba-big-bath-red; scripts/_size_table.py pairs through nearest_label, output on Ochiba diffed identical; the placer drafts pass the whole program after the exception was ruled NOT LEGITIMATE and the emitter gained the point features; make quick ALL=1 green
- [x] T11 `buildings/programs.md`: BOTH types' required-items tables rendered between
      `<!-- types.json:<tier> -->` markers by a new `make building-programs` (`CHECK=1` on the gate,
      like `make glossary`) - the magistracy's bullets converted, their per-item reasoning moved into
      each item's `why` - and the "Country shrine (a village district's shrine)" entry with the knobs (FR-009), the
      size anchors (FR-010), residence (FR-011), staffing from the campaign notes (one country monk,
      part-time acolytes on loan), in prose; `buildings.md`: the vocabulary for the sanctuary, the arch,
      the fence and hedge, the swept-gravel ground pattern `keidai-gravel` and the grave markers, and
      the section "Adding a building type" listing exactly the files a type touches (FR-007);
      `.claude/agents/building-review.md` and `size-audit.md` name the program by type and read the
      type's rendered block (FR-006)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. programs.md: both types' required-items tables rendered by make building-programs (CHECK=1 green; registered as an operation); the country shrine's composition rules, knobs, anchors, staffing in prose; buildings.md: the shrine vocabulary, 'Adding a building type'; building-review.md and size-audit.md read the type's table. Boxes: the pass is R1-R3; source-reader READ every page but one (fn-144 re-sourced); recorded and cited fn-143 to fn-205; quote-check 47 VERBATIM, 5 PARTIALs closed with the readers' sentences, the wiki retired to an absence note; source-applicability none NOT-APPLICABLE, nine write-ups given their limits
- [x] T12 The shrine's checks (D8): `sanctuary_on_axis`, `arch_on_approach`, `well_clear_of_arch`,
      `fence_not_wall`, registered under `country-shrines`; their fixtures are cut from the exemplar
      in T17 - this task lands the checks with synthetic-sheet tests and T17 lands the fixtures
      research: rendering
      scaffold: `torii_clear_of_shrine` in `settlement/shrines_wells/torii.py` for the arch-on-axis form
      verify: DONE. sanctuary_on_axis, arch_on_approach, well_clear_of_arch, fence_not_wall read DECLARED ids (hall, sanctuary, approach, arch, well; a <g id=fence>) - Rect.ident and ParsedPlan.by_id added; synthetic shrine sheet + four synthetic red fixtures (T17 re-cuts from the exemplar); branch tests in test_shared.py; make quick ALL=1 green

## Phase 4 - the record (FR-012 to FR-014; D13)

- [x] T13 `research/religion-and-death.html`: two new sections after the village-shrine section - "Does
      the country monk live at the shrine?" and "How big is a country shrine, and what stands in its
      precinct?" - with `Sources:` lines, footnotes fn-143 onward on `citations/religion-and-death.html`
      quoting each passage (English translation marked, original kept), the four labels; the village
      section revised per FR-013; glossary terms (kuri, honden, haiden, bettō, jingūji, miyaza, jochi,
      shasō) in `interactive/assets/glossary.json`; every page read registered in `SOURCES.html` with
      its two write-ups (FR-014's list) and the unreadable pages in an absence note; `make citations`
      and `make glossary`; the village shrine's class entries name the two new questions
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      measure: `make quote-verbatim PAGE=religion-and-death` before quote-check; `make record-prepass
      PAGE=religion-and-death` before record-format
      verify: DONE. two sections on religion-and-death.html, the village section corrected to the one-roof reading, fn-143 to fn-205 (five absence notes), 35 registry entries with write-ups, 20 glossary terms; make citations and make glossary in sync; entry-drift owes no modal (no class names the section - only hamlets are scripted). Boxes as T11
- [x] T14 The verification agents, in the background, in order: `source-reader` on the two new sections
      (READ per claim; a CONTRADICTED verdict changes the text); `quote-check` after the verbatim script;
      `record-format` after the prepass; `entry-drift` on every class entry `scripts/_entry_owed.py`
      names for the revised village section; each verdict folded in and recorded in `research.md` R5
      research: rendering
      verify: DONE. source-reader (R6), quote-check (47 VERBATIM, 5 PARTIAL closed, 9 unfootnoted sentences sourced or marked the sheet's own), record-format (10 vocabulary, 2 session phrases, 5 unused terms) all folded in; entry-drift: _entry_owed names no pair; verdicts in research.md R6
- [x] T15 `source-applicability` over every new registry key, three dispatches by group (the Japanese
      encyclopedia and cultural-property pages; the Chinese pages; the RPG wiki), BEFORE T16 draws
      from their numbers; each limit written into the entry's write-ups; a NOT-APPLICABLE source
      removed from the sections and the program
      research: rendering
      verify: DONE. two dispatches over 34 keys: none NOT-APPLICABLE; the Mianning author corrected (Long Sheng), Gantang and Xietang written up honestly, nine entries given their limits; the bell knob's class downgraded to guess; verdicts in R6

## Phase 5 - the exemplar (FR-015, FR-016; D12)

- [x] T16 `pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.svg` hand-drawn to the program at
      3 px = 1 ft from the Ochiba template's style: the fenced precinct marked `id="precinct"` on
      swept gravel, the one-roof hall-and-dwelling (knob 1 default), the sanctuary behind it on the
      approach axis, the arch where the approach crosses the fence, the well beside the approach, the
      kitchen garden and privy at the dwelling end, fire-water, the grove and the burial ground beside
      the precinct, the scale bar, the title; `hoshigaoka-shrine.gen.py` rasterizing only;
      `hoshigaoka-shrine.notes.md` with program type, `**Form**: one roof`, every knob (dedication from
      the clan patron Fortune in Hoshigaoka's notes; bell absent; grove and burial-ground sides from
      Hoshigaoka's map; wealth average), particulars left open for the GM, an empty Review log
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. pool/country-shrines/hoshigaoka-shrine/: svg (precinct, hall, sanctuary, approach, arch, well, fence, kitchen garden declared by id; one roof, 76 x 36 ft, hall and dwelling end to end), gen (rasterizes), notes (program type, Form, five knobs, particulars open, Review log); size-table taken; the sheet clean under every registered check; 2400 px render read twice. Boxes as T11
- [x] T17 The shrine's four fixtures cut from the exemplar (`tests/fixtures/hoshigaoka-*-red.svg`),
      registered in T12's rows; `make quick` sweeps six sheets green; the pool index lists the tier
      with the program type (`make pool-index`)
      research: rendering
      verify: DONE. four fixtures cut from the exemplar (sanctuary off axis, arch adrift, well on the approach, walled) replace the synthetic stand-in; the registry test's CLEAN_STANDIN retired; make quick ALL=1 sweeps six sheets green; the pool index lists the tier
- [x] T18 `size-audit` from `make size-table`, then `building-review`, both in the background; findings
      fixed and re-run until clean or overruled with the rationale in the notes' Review log; one row
      each in `docs/review-ledger.md`; the closing bookend - the PNG re-read against R1-R3 and the
      result written in `research.md` R7
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. size-audit (5 findings, 4 applied, the fifth resolved by drawing the basin true) and building-review (10 errors applied, 4 questionables applied, 3 overruled with reasons in the notes) - both rows in docs/review-ledger.md; the closing bookend: the re-planned PNG read against R1-R3 (kitchen off the axis, the sanctuary behind the hall in its wood, the graves beside). Boxes as T11

## Phase 6 - the gate and the push (SC-001 to SC-006)

- [x] T19 `spec-fidelity` round 3 if the spec was amended during implementation, MODE 3 = VERIFY
      items from round 2: none - FAITHFUL
      changed since: whatever the implementation amended, listed here when it happens
      figures: specs/254-country-shrine/measurements.json - re-run with `make figures SPEC=specs/254-country-shrine`
      research: rendering
      verify: DONE. the spec was amended during implementation (four Decisions rows on the verification findings); round 3 ran as MODE 3 VERIFY on the diff and returned FAITHFUL, with two record corrections applied (the hugging command re-runnable by figures.py; the range current at 51-78 with the drafts)
- [ ] T20 `make done` in the background (the whole gate; 100% coverage over `l7r`; the file-size bar;
      the ratchet); every failure fixed together and re-run once; `scripts/sync-with-main.sh done` from
      the clone (engine code in the delta: the GATED route); the memory file updated
      research: rendering
      verify: the gate stamp green; the push reported; `git status -sb` clean and level with origin

## Dependencies

T01 before any edit under `l7r/`. T02 -> T03 -> T04. T05 -> T06 -> T07 -> T08 -> T09. T10 after T06.
T11 after T02 and T10. T12 after T06. T13 -> T14; T15 before T16. T16 after T11, T12, T15. T17 after
T16. T18 after T17. T19, T20 last. Parallel: T02 with T05 (different packages); T13 with T05-T09 (the
record and the engine share no file); T11's prose with T10's code.

## Strategy

US1 (T02-T10) is the MVP: the magistracy re-declared and swept proves the architecture before the
shrine exists. US2 (T11, T13-T15) can land before US3 and is what the GM asked to know. US3 (T12,
T16-T18) is the exemplar.
