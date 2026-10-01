# Tasks - feature 303, the record organized by tags

Every task is tooling over the record: nothing a map draws or asserts changes, so each is `research: rendering`.

- [ ] T01 Baseline: `make done` on unmodified main in a detached worktree (`/tmp/base303`); `make record` timed before any edit (constitution XIII, plan Performance)
      research: rendering
- [ ] T02 [US1] [US2] The data: `research/tags.json` (the vocabulary, FR-005) and `research/contents.json` (FR-009, FR-013); the tag table from the tagging pass reviewed, the torn calls ruled (FR-008, FR-008a; plan D5, D11)
      research: rendering
- [ ] T03 [US5] `record/questions.py` and `record/contents.py`: stems and markers read, tags validated, homing and order computed; each refusal of FR-007 and FR-010 a failing test first (FR-001, FR-002, FR-006, FR-007, FR-010, FR-011; plan D1, D2, D5)
      research: rendering
- [ ] T04 The migration script on a fixture record: numbers, moves, link rewriting through the old index, the 19 notes copies, markers, openings into section descriptions, confusables, `moved-303.json`, `tags.md`, `migration.md`; its test proves body text unchanged but for links and markers (SC-003; plan D1-D4, D7, D11)
      research: rendering
- [ ] T05 The migration run on the real record; `tags.md` and `migration.md` written; SC-003's count, id set and normalized-body comparison pass (FR-001, FR-003, FR-008, FR-016)
      research: rendering
- [ ] T06 [US1] [US2] [US3] The engine on the new layout: `store.py`, `site_links.py`, `xref.py`, `confusables.py`, `site.py` + `site_pages.py` (halves, sections, tag pages, question pages, single page, nav), `sources.py` (Entry resolution, `SITE_PAGES` + `q/`), `citations.py`, `tools/footnote_census.py`, `pipeline/record_build.py`; feature 258's one-time migrations deleted (FR-004, FR-012, FR-013, FR-014, FR-015, FR-020; plan D6, D7, D10)
      research: rendering
- [ ] T07 [US1] The site looked at in a browser: home, a section page in each half, a question page with its tags and notes, a tag page, the single page (SC-001, SC-005, SC-010)
      research: rendering
- [ ] T08 [US4] The pointer sweep over the repository and the pointer check on the new forms, refusing every old form with its new pointer named (FR-017, FR-018; SC-007; plan D8)
      research: rendering
- [ ] T09 [US4] [US5] Tools, make targets and hooks on the new layout (`Q=`, `IN=`, `make reserve KIND=question`, `make fragment-move` of a stem, briefs), each with its test; `make hooks-test` green (FR-019; SC-008; plan D9)
      research: rendering
- [ ] T10 Docs and agent contracts describe the new layout, tags and contents (FR-021)
      research: rendering
- [ ] T11 [US4] The pool's interactive pages regenerated (`make maps`) and every research link in them resolved against the built site (FR-020; SC-009)
      research: rendering
- [ ] T12 Verify and land: SC-002 and SC-006 as tests; `make record CHECK=1`; `make done` compared with T01's baseline; peers' unpushed research work checked (plan D12); the migration script deleted; pushed (SC-011)
      research: rendering
