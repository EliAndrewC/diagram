# Tasks - feature 262, interactive magistracy pages

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D10). Measurement: [`coverage.md`](coverage.md).
American spellings, hyphens only.

**No task here is `research: physical`.** The GM's instruction is to tie into the research that already
exists; no research text is edited, no finding is made, and every classification is carried from an existing
finding (FR-005). No map draws anything new: every sheet's PNG is measured pixel-identical.

## Phase 0 - the baselines

- [ ] T01 The regression baseline: `make done` on unmodified HEAD in a detached worktree; every later failure
      checked against it before it is called new
      research: rendering
      measure: the run's own output
- [ ] T02 The picture and audit baselines: each of the five sheets rendered to PNG and run through
      `make pack-audit` before the first edit; the original red fixtures' audit outputs likewise
      research: rendering
      measure: the saved PNGs and audit texts

## Phase 1 - the reader and the page (FR-001, FR-002, FR-011; D1-D3)

- [ ] T03 `interactive/sheet.py`: tagged SVG -> the page's two lists, nearest tag wins, ancestors re-opened,
      `defs` ruled out, the census, `element_kinds`, `write_sheet_page`; tests on plain strings
      research: rendering
- [ ] T04 The page takes a registry (`explanations`, `unregistered_classes`, `render_page`, `write_html`),
      defaulting to the hamlet vocabulary so no hamlet caller or byte changes
      research: rendering

## Phase 2 - Ochiba, the reference sheet (FR-004, FR-005, SC-002, SC-003; D4-D6)

- [ ] T05 Ochiba tagged; its precinct split into one rect per court; PNG and audit measured identical
      research: rendering
      measure: `make picture-diff` and the audit diff against T02
- [ ] T06 The Mode A registry written from `coverage.md`: grounds, office, household, particulars - every
      label carried from an existing finding, every entry naming its sections or declaring none
      research: rendering
- [ ] T07 The fold (FR-003a; D9): the magistracies items name their kind and state no class, why or label;
      the audit finds them by tag and prints the kind's class and why; `programs.md` re-rendered; every
      sheet's audit measured identical
      research: rendering
      measure: the audit diff against T02
- [ ] T08 Ochiba's gen writes its page; the GM's two examples asserted on the page's data (the threshold
      stones lead with the deviation, the hearing court announces nothing and lists its questions)
      research: rendering

## Phase 3 - the pool (FR-001, FR-006-FR-010, SC-001, SC-004, SC-006; D7, D8, D10)

- [ ] T09 Hayakawa and Ubame tagged, their precincts split; PNG and audit measured identical
      research: rendering
      measure: `make picture-diff` and the audit diff against T02
- [ ] T10 The placer writes kinds (`BuildingSpec.feature`, `emit_svg`), refusing a building without one; both
      drafts regenerated, PNG and audit measured identical; their gens write their pages
      research: rendering
      measure: `make picture-diff` and the audit diff against T02
- [ ] T11 The red fixtures re-derived as the tagged sheet plus their own defect (D10): no untagged ink, each
      fixture's audit output unchanged, every registry fixture test still firing
      research: rendering
      measure: the audit diff against T02's fixture outputs
- [ ] T12 The per-map facts (FR-010): each hand-drawn sheet's notes carry a "Map notes / Features" block keyed
      by kind, and each page shows it
      research: rendering
- [ ] T13 The pool sweep: every sheet carries a known kind on every element; the registry is closed over the
      five maps; each entry complete, in its label's form, resolving or declaring silence
      research: rendering

## Phase 4 - closing

- [ ] T14 The glossary covers every term the new write-ups use; the record's derived glossary asset rebuilt
      research: rendering
- [ ] T15 The docs: `interactive/CLAUDE.md` (the Mode A sheet and its registry), `buildings.md` / `SKILL.md`
      (tag what you draw), the programs table; the Hoshigaoka country shrine named as follow-up
      research: rendering
- [ ] T16 `building-review` of the Ochiba page at acceptance, in the background, one map; a ledger row;
      its findings through `escalation-check` before the GM sees them
      research: rendering
- [ ] T17 `make done` green, every failure checked against T01
      research: rendering
      measure: the gate's own output
- [ ] T18 The closing report to the GM lists both sets (User Story 4): the kinds labeled `guess` because no
      finding classifies them, and the kinds no research section covers
      research: rendering
