# Tasks - feature 319, modal write-ups a reader can take in

Phases follow the GM's order (spec FR-010): guidelines and checks, the farmhouse pilot, the garden pilot, a further pilot if
the garden's first rewrite needs changes, then - on the GM's go-ahead - the title card's choices and the rollout. The GM's
verdict on each pilot round is recorded under its task (SC-005). Nothing but the spec claim lands on main until the rollout is
done (FR-012).

## Occasions

- none: no map, sheet, glyph or placement changes - the page is a second serialization of the same drawing (feature 134
  FR-010); the modal checks are this feature's subject, owed by its own command (plan D6)

## Phase 1 - guidelines, the form, the tabs, the checks

- [x] T01 [US1] [US5] The two guideline documents, `dev/modals.md` (standardized) and `dev/modals-particular.md` (particular),
  numbered rules with their provenance; indexed from `interactive/classes/CLAUDE.md`; `research/CLAUDE.md`'s "New questions
  reach a modal only when the GM asks for them" brought in line with M14 (FR-001, FR-002, FR-003; plan D3)
      research: rendering
      verify: DONE. DONE. dev/modals.md (M1-M20) and dev/modals-particular.md (P1-P8), numbered with provenance; indexed from classes/CLAUDE.md; research/CLAUDE.md's references line brought in line with M14
- [x] T02 [US2] The About form in `classes/_base.py` (`About:` paragraphs, `Guesses:` bullets, `Form:`, no `Label:`; the old
  form still parses) and the page data (`about`, `guesses`); `tests/interactive/test_about_form.py` red then green; the
  registry snapshot test exempts an About-form class's label (FR-005; plan D1)
      research: rendering
      verify: DONE. DONE. About:/Guesses:/Form: parsed beside the old form (_base.py), about/guesses on the page data; test_about_form.py 9 cases; snapshot and completeness tests take the About form; 743 interactive tests green
- [x] T03 [US2] [US3] The tabbed modal - About / Guesses / References in one dialog, hidden when empty, opening on About; the
  references dialog retired; `page.js`, `page.css`, `page.py`; the browser test and `test_page.py` rewritten for tabs;
  `interactive/CLAUDE.md`'s presumption-of-accuracy and references sections rewritten; `make page-check` green (FR-005,
  FR-006, FR-007; plan D2)
      research: rendering
      verify: DONE. DONE. one dialog, tabs About/Guesses/References hidden when empty, opening on About; references dialog retired; browser test and test_page rewritten; interactive/CLAUDE.md sections updated; make page-check green 5346 passed
- [x] T04 [US3] `scripts/_modal_bundle.py` and `make modal-bundle KIND= FOR=` / `make modal-prepass KIND=`: the rendered tabs,
  the guidelines copy, the prepass (word counts, barred phrases, bullets, Entry resolution) and the candidates - the UNION of
  any shared subject tag with the Entry pages and the kind's name or glossary variants, ranked, never cut, the whole question
  record copied for grep; a fixture test that 0004 is a farmhouse candidate (FR-008; plan D5)
      research: rendering
      verify: DONE. DONE. scripts/_modal_bundle.py + make modal-bundle / modal-prepass: rendered tabs, guidelines copy, prepass, Entry pages, UNION candidates ranked never cut, record/ for grep; test_modal_checks.py proves 0004 a farmhouse candidate
- [x] T05 [US3] `.claude/agents/modal-form.md` and `.claude/agents/modal-research.md` (Opus, medium, `omitClaudeMd`), their
  rows in `tests/test_agent_models.py`; `modal-research` reports accuracy, references and gaps as three verdicts (FR-008; plan
  D4)
      research: rendering
      verify: DONE. DONE. .claude/agents/modal-form.md and modal-research.md (opus/medium, omitClaudeMd), tier rows; modal-research reports ACCURACY/REFERENCES/GAPS; check-bundle-hooks knows both
- [x] T06 [US3] Owed and enforced: `scripts/_modal_owed.py` owes `modal-form:<key>`, `modal-accuracy:<key>`,
  `modal-references:<key>`, `modal-gaps:<key>` for an About-form class whose About, Guesses or Entry changed, and the three
  research units (not a `modal-research:<key>` - the plan review's note) when a page its Entry names changed, replacing
  entry-drift for About-form classes only; folded into `_record_owed.py`, `make record-checked`, `entry-gate.sh`; tests on
  fixture trees; the refusal message names the command (FR-008; plan D6)
      research: rendering
      verify: DONE. DONE. scripts/_modal_owed.py owes modal-form + modal-accuracy/-references/-gaps; folded into _record_owed (record-owed, record-checked, entry-gate), entry-drift dropped for About-form keys; 54 tooling tests green
- [x] T07 [US3] The checks proved on the OLD text (plan D7): the current farmhouse and garden converted mechanically into
  bundles; `modal-form` reports the farmhouse's missing materials and occupancy and the garden's guess-led opening;
  `modal-research` reports 0004 as a farmhouse gap. A check that passes the old text is fixed first. Ledger rows with cost
      research: rendering
      verify: DONE. DONE. research.md R1: all four proof runs fired - modal-form flagged the farmhouse's missing materials/occupancy and the garden's guess lead; modal-research found 0004 (farmhouse G1) and the garden's accurate-not-guess (A1); bundle cut 380->140 KB

## Phase 2 - the farmhouse pilot

- [x] T08 [US1] The research pass for the farmhouse's unanswered standard questions - its walls; whether it closed up (storm
  shutters, board doors) - archive first, then the web; recorded and cited on the question pages they belong to (0029 for the
  walls, 0102 or 0117 for the openings) through a write and a check page session (plan D8)
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed
      verify: DONE. DONE. research pass (sonnet, archive first; research.md R2); written by the F1 page sessions: new question 0244 Farmhouse walls, 0117 the big door barred at night and the veranda's storm shutters; checked in nine rounds (f1-checks.md) - quote-check, record-format, source-reader, source-applicability, translation-check, intro-check, entry-drift (Door); make record-owed UNANSWERED=1: nothing owed
- [x] T09 [US1] The farmhouse rewritten in the About form from the guidelines: purpose (one household; work on the earth floor;
  the inner stable), look (thatch on a hipped or gabled roof, the earth floor and the raised rooms, the walls, the big sliding
  door and its wicket), how many (household of about five, low and high), size; guesses as bullets; `Entry:` exactly what it
  rests on; both checks green in at most two rounds; Inashiro's page regenerated in the clone (plan D9)
      research: rendering
      verify: DONE. DONE. Farmhouse in the About form: purpose, look, how many, size; no guesses; Entry 0029 0028 0004 0048 0244 0107 0117 0029.drawing; modal-form rounds 1-6 (clean), modal-research rounds 1-5 (clean bar one declined clause); all four units answered; page-check green; Inashiro regenerated in the clone
- [x] T10 [US6] THE GM'S VERDICT on the farmhouse - each change made in the guidelines first, then the modal, re-checked;
  repeated until the GM is satisfied (FR-010)
      research: rendering
      verify: DONE. GM 2026-10-03/04: accepted the farmhouse write-up; changes asked (Depiction tab, its name, roof left to the claims backlog) made in the guidelines first

- [x] T18 [US6] One file per modal (plan D12): every `Kind`'s text moved to `interactive/assets/modals/<hamlet|sheet>/<slug>.md`
  by script, the registry field-for-field unchanged (test); `Kind.feature()` reads the file; the render fingerprint takes every
  file under `interactive/assets/`; `_modal_owed`, `_modal_bundle`, `_entry_owed`, `_bundle_owed`, `_check_bundle`,
  `_apply_edits` read the files; docs; `make page-check` and the tooling tests green
      research: rendering
      verify: DONE. DONE. 155 modals moved to interactive/assets/modals/<hamlet|sheet>/<slug>.md, both registries field-for-field identical (snapshot compare); Kind.feature reads the file; render fingerprint takes every file under interactive/assets (test); _modal_owed/_modal_bundle/_entry_owed/_bundle_owed/_check_bundle/_apply_edits read the files, units keyed hamlet/<slug> or sheet/<slug>; plan review CLEAR; page-check 5349, quick green; 0029 trimmed under the size cap and its record checks answered (quote-check 3 rounds, record-format 3)

- [x] T19 [US3b] The Depiction tab (plan D13): `Depiction:` and `Drawing:` in the modal file (a drawing page under `Entry:`
  refused); the fourth tab on the page, hidden when empty, in the shared grid cell; the guidelines' Depiction section and M13
  amended; tests red then green; `make page-check` green
      research: rendering
      verify: DONE. Depiction: and Drawing: parsed; .drawing.html under Entry: refused; the tab rendered and stacked with the others; make test-file green 10,989 passed
- [x] T20 [US3b] `modal-depiction`: the agent file and its tier row; the bundle (`FOR=modal-depiction`: drawing pages, the
  claims-index rows citing them, the glyph crop); the owed unit; `modal-research` reading research questions only; proved on the
  farmhouse's current text (it must flag the missing tab and the drawing pages on References)
      research: rendering
      verify: DONE. modal-depiction agent + tier row; bundle with LISTED and CANDIDATE pages (sibling and old-form base legs), claims, glyph crop; plan review round 4 CLEAR
- [x] T21 [US3b] The farmhouse's Depiction tab written; all four modal checks green; Inashiro regenerated; THE GM'S VERDICT
      research: rendering
      verify: DONE. GM 2026-10-04: 'That looks good' on the farmhouse with its Depiction tab; four checks answered; Inashiro regenerated

## Phase 3 - the garden pilot (and a further pilot only if needed)

- [ ] T11 [US2] The garden rewritten from the (amended) guidelines - M6 settled on it - with its research pass where a
  standard question is open; both checks; the page regenerated
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
      verify:
- [ ] T12 [US6] THE GM'S VERDICT on the garden's FIRST rewrite. Accepted with no changes and the GM's go-ahead: the rollout
  starts. Otherwise: changes to the guidelines, then the garden; a further feature is piloted as T11/T12 (FR-010, SC-005)
      research: rendering
      verify:

## Phase 4 - the title card's choices (after the go-ahead)

- [ ] T13 [US4] D10 settled into `plan.md` and re-reviewed: `interactive/assets/choices.json` over EVERY per-settlement
  choice - a test reads the POPULATED `KNOBS` registry (23 knobs, seven registered from other modules - the plan review's
  note), not `_knobs.py`'s lines, and every `### Features` source key; the choice-value modals in a new registry in the About
  form; the title card lists the choices, each value opening its modal; the hamlets' `### Features` facts moved; a test that
  no hamlet feature modal differs between two pool maps (FR-004, FR-009, SC-004)
      research: rendering
      verify:

## Phase 5 - the rollout (after the go-ahead)

- [ ] T14 [US6] Every hamlet class rewritten in the About form, by writer agents on disjoint modules, each class checked from
  its own bundles; research passes where a standard question is open (FR-011)
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
      verify:
- [ ] T15 [US4] Every choice value's modal written and checked (FR-011)
      research: rendering
      verify:
- [ ] T16 [US5] The sheets: every compound kind classed standard or `Form: particular` (plan D11); the general kinds rewritten
  under `modals.md`, the particulars and every sheet's `### Features` entries under `modals-particular.md`, the canon answer in
  the `modal-research` bundle; checked (FR-003, FR-011)
      research: rendering
      verify:
- [ ] T17 The old form retired: the What/Why/Note/Caveat parser, the label lead, the caveat machinery and their tests; the
  docs; `make page-check` and `make done` green; the pool pages regenerated; the push (FR-012, SC-006)
      research: rendering
      verify:
