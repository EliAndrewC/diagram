# Tasks - feature 262, interactive magistracy pages

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D10). Measurement: [`coverage.md`](coverage.md).
American spellings, hyphens only.

**No task here is `research: physical`.** The GM's instruction is to tie into the research that already
exists; no research text is edited, no finding is made, and every classification is carried from an existing
finding (FR-005). No map draws anything new: every sheet's PNG is measured pixel-identical.

## Phase 0 - the baselines

- [x] T01 The regression baseline: `make done` on unmodified HEAD in a detached worktree; every later failure
      checked against it before it is called new
      research: rendering
      measure: the run's own output
      verify: DONE. DONE. make done on unmodified 0c7a19c5 in a detached worktree: 4195 passed, 1 failed (the raster-wash browser test) and hooks-test failed (batching, finished-run suites reading this live session). Neither fails in the clone: the feature's gate is green with the browser package run, so both were worktree/session artifacts, not regressions.
- [x] T02 The picture and audit baselines: each of the five sheets rendered to PNG and run through
      `make pack-audit` before the first edit; the original red fixtures' audit outputs likewise
      research: rendering
      measure: the saved PNGs and audit texts
      verify: DONE. DONE. Five sheets rendered at 2400 px and run through make pack-audit before the first edit; 19 red fixtures' audit outputs saved (scratchpad/base, fxaudit).

## Phase 1 - the reader and the page (FR-001, FR-002, FR-011; D1-D3)

- [x] T03 `interactive/sheet.py`: tagged SVG -> the page's two lists, nearest tag wins, ancestors re-opened,
      `defs` ruled out, the census, `element_kinds`, `write_sheet_page`; tests on plain strings
      research: rendering
      verify: DONE. DONE. interactive/sheet.py: 14 tests on plain strings (nearest tag wins, ancestors re-opened, defs ruled out, ids once, census, element_kinds, write_sheet_page).
- [x] T04 The page takes a registry (`explanations`, `unregistered_classes`, `render_page`, `write_html`),
      defaulting to the hamlet vocabulary so no hamlet caller or byte changes
      research: rendering
      verify: DONE. DONE. registry threaded through explanations, unregistered_classes, render_page, write_html with the hamlet CLASSES default; the hamlet interactive tests pass unchanged.

## Phase 2 - Ochiba, the reference sheet (FR-004, FR-005, SC-002, SC-003; D4-D6)

- [x] T05 Ochiba tagged; its precinct split into one rect per court; PNG and audit measured identical
      research: rendering
      measure: `make picture-diff` and the audit diff against T02
      verify: DONE. DONE. Ochiba: 58 tags, precinct split into two abutting court rects; make picture-diff 0 of 5157600 px, pack-audit output identical.
- [x] T06 The Mode A registry written from `coverage.md`: grounds, office, household, particulars - every
      label carried from an existing finding, every entry naming its sections or declaring none
      research: rendering
      verify: DONE. DONE. 52 kinds in compound_kinds (grounds 14, office 11, household 15, particulars 12), written from coverage.md; every entry resolves or declares silence (test_compound_kinds).
- [x] T07 The fold (FR-003a; D9): the magistracies items name their kind and state no class, why or label;
      the audit finds them by tag and prints the kind's class and why; `programs.md` re-rendered; every
      sheet's audit measured identical
      research: rendering
      measure: the audit diff against T02
      verify: DONE. DONE. 21 magistracies items name their kind with no class, why or label; classification() reads the registry; programs.md re-rendered; audit identical on all five sheets and 19 fixtures.
- [x] T08 Ochiba's gen writes its page; SC-002's four clauses asserted on the page's data: the threshold
      stones lead with the deviation, the hearing court announces nothing and lists its questions, the outer
      and inner courts each carry their own ground, and the stones' modal carries Ochiba's own note (FR-010)
      research: rendering
      verify: DONE. DONE. Ochiba gen writes its page; test_the_gm_s_two_examples_hold_on_the_ochiba_page asserts the four SC-002 clauses; clicked in Chromium: stones lead with the deviation plus the map note, hearing court 3 questions.

## Phase 3 - the pool (FR-001, FR-006-FR-010, SC-001, SC-004, SC-006; D7, D8, D10)

- [x] T09 Hayakawa and Ubame tagged, their precincts split; PNG and audit measured identical
      research: rendering
      measure: `make picture-diff` and the audit diff against T02
      verify: DONE. DONE. Hayakawa and Ubame tagged, precincts split (inner under outer); picture-diff 0 px on both, audits identical.
- [x] T10 The placer writes kinds (`BuildingSpec.feature`, `emit_svg`), refusing a building without one; both
      drafts regenerated, PNG and audit measured identical; their gens write their pages
      research: rendering
      measure: `make picture-diff` and the audit diff against T02
      verify: DONE. DONE. BuildingSpec.feature, emit_svg writes data-kind and refuses a building without one; both drafts regenerated, picture-diff 0 px, audits identical; gens write pages.
- [x] T11 The red fixtures re-derived as the tagged sheet plus their own defect (D10): no untagged ink, each
      fixture's audit output unchanged, every registry fixture test still firing
      research: rendering
      measure: the audit diff against T02's fixture outputs
      verify: DONE. DONE. 19 fixtures re-derived by git merge-file plus tag carry-over; no untagged ink; audit outputs unchanged; ochiba-no-cell re-cut to drop the whole cell group; test_registry green.
- [x] T12 The per-map facts (FR-010): each hand-drawn sheet's notes carry a "Map notes / Features" block keyed
      by kind, and each page shows it
      research: rendering
      verify: DONE. DONE. Map notes / Features blocks on the three notes files (Ochiba 9 keys, Hayakawa 8, Ubame 15); read_map_notes parses each; the stones' note shows on the page.
- [x] T13 The pool sweep: every sheet carries a known kind on every element; the registry is closed over the
      five maps; each entry complete, in its label's form, resolving or declaring silence
      research: rendering
      verify: DONE. DONE. test_compound_kinds: every sheet 0 unclassed and 0 unregistered, registry closed over the five, 52 entries complete and in their label's form.

## Phase 4 - closing

- [x] T14 The glossary covers every term the new write-ups use; the record's derived glossary asset rebuilt
      research: rendering
      verify: DONE. DONE. nakamon and morijio added; karo widened to the house elder it names; make glossary wrote 722 terms; the record-format glossary test covers both registries.
- [x] T15 The docs: `interactive/CLAUDE.md` (the Mode A sheet and its registry), `buildings.md` / `SKILL.md`
      (tag what you draw), the programs table; the Hoshigaoka country shrine named as follow-up
      research: rendering
      verify: DONE. DONE. interactive/CLAUDE.md section, buildings.md checklist item and program note, programs.md rendered; the Hoshigaoka shrine named as follow-up in the closing report.
- [x] T16 `building-review` of the Ochiba page at acceptance, in the background, one map; a ledger row;
      its findings through `escalation-check` before the GM sees them
      research: rendering
      verify: DONE. DONE. building-review of the Ochiba page returned needs-work; every prose, caveat and notes finding applied (compound_kinds, notes block, a Mode A caveat lead); ledger row added; findings for the GM filtered by escalation-check (3 keep, 2 rewrite, 4 cut).
- [x] T17 `make done` green, every failure checked against T01
      research: rendering
      measure: the gate's own output
      verify: DONE. DONE. make done green on the merged tree in 123 s, the browser package run.
- [x] T18 The closing report to the GM lists both sets (User Story 4): the kinds labeled `guess` because no
      finding classifies them, and the kinds no research section covers
      research: rendering
      verify: DONE. DONE. The closing report lists the kinds labeled guess (clerks' room, karo's house, kennel, writing pavilion, salt wards) and the kinds no research section covers, per the escalation-check filter.
