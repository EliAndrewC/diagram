# Tasks - feature 303, the record organized by tags

Every task is tooling over the record: nothing a map draws or asserts changes, so each is `research: rendering`.

- [x] T01 Baseline: `make done` on unmodified main in a detached worktree (`/tmp/base303`); `make record` timed before any edit (constitution XIII, plan Performance)
      research: rendering
      verify: DONE. Baseline make done on unmodified main (8ef670632) in a detached worktree /tmp/base303: gate green; make record before any edit 2.5 s, 2,640 pages (2026-10-01, wall clock)
- [x] T02 [US1] [US2] The data: `research/tags.json` (the vocabulary, FR-005) and `research/contents.json` (FR-009, FR-013); the tag table from the tagging pass reviewed, the torn calls ruled (FR-008, FR-008a; plan D5, D11)
      research: rendering
      verify: DONE. research/tags.json (30 subjects, 3 settings, 4 levels) and research/contents.json (FR-013's sections); 240 research questions tagged by four Opus readers in batches of 60, the torn calls ruled; tags.md generated from the markers, 243 rows; FR-008a: 3 conventions (the Presentation questions)
- [x] T03 [US5] `record/questions.py` and `record/contents.py`: stems and markers read, tags validated, homing and order computed; each refusal of FR-007 and FR-010 a failing test first (FR-001, FR-002, FR-006, FR-007, FR-010, FR-011; plan D1, D2, D5)
      research: rendering
      verify: DONE. record/questions.py and record/contents.py: stems, markers, tags, homing (first match), order (level then number), select(); every FR-007/FR-010 refusal a test in tests/interactive/test_record_questions.py (fed the bad case, named by file)
- [x] T04 The migration script on a fixture record: numbers, moves, link rewriting through the old index, the 19 notes copies, markers, openings into section descriptions, confusables, `moved-303.json`, `tags.md`, `migration.md`; its test proves body text unchanged but for links and markers (SC-003; plan D1-D4, D7, D11)
      research: rendering
      verify: DONE. scripts/_record_flatten.py (one-time; deleted after its run): numbers, moves, links resolved by the old site_links index, 19 notes copied, markers, openings, confusables, moved-303.json; dry runs on the real record named 4 whole-part links, repointed first (research R10)
- [x] T05 The migration run on the real record; `tags.md` and `migration.md` written; SC-003's count, id set and normalized-body comparison pass (FR-001, FR-003, FR-008, FR-016)
      research: rendering
      verify: DONE. Migration run: 1,404 files to research/questions/, 243 stems; SC-003 checked against HEAD - same file count, same ids (474 headings), every body identical but for links and markers except the two R10 link-text fixes; tags.md and R9 written
- [x] T06 [US1] [US2] [US3] The engine on the new layout: `store.py`, `site_links.py`, `xref.py`, `confusables.py`, `site.py` + `site_pages.py` (halves, sections, tag pages, question pages, single page, nav), `sources.py` (Entry resolution, `SITE_PAGES` + `q/`), `citations.py`, `tools/footnote_census.py`, `pipeline/record_build.py`; feature 258's one-time migrations deleted (FR-004, FR-012, FR-013, FR-014, FR-015, FR-020; plan D6, D7, D10)
      research: rendering
      verify: DONE. Engine on the new layout: store, site_links, xref, confusables, site + site_pages (halves, nested sections, tag pages, q/ pages, all.html, nav), sources (Entry, SITE_PAGES + q/), citations, footnote_census, record_build; citations_side, split's SPLIT path and stage-3 migrations deleted; make record 2.0 s, 2,687 pages; 100% coverage held by make done
- [x] T07 [US1] The site looked at in a browser: home, a section page in each half, a question page with its tags and notes, a tag page, the single page (SC-001, SC-005, SC-010)
      research: rendering
      verify: DONE. Site looked at in Chromium (Playwright): home, a question page with tags, notes and confusables, a section page in each half, a tag page; sidebar nesting indented; SC-001/SC-005/SC-010 hold as tests in test_record_site.py
- [x] T08 [US4] The pointer sweep over the repository and the pointer check on the new forms, refusing every old form with its new pointer named (FR-017, FR-018; SC-007; plan D8)
      research: rendering
      verify: DONE. Pointer sweep (four passes, each from what the check found) and check-research-pointers.py on the new forms: refuses retired paths, page dirs, built pages, .md pages, old page+number, PAGE=/SECTION=, glued section ids, naming the replacement from moved-303.json; clean over the repository
- [x] T09 [US4] [US5] Tools, make targets and hooks on the new layout (`Q=`, `IN=`, `make reserve KIND=question`, `make fragment-move` of a stem, briefs), each with its test; `make hooks-test` green (FR-019; SC-008; plan D9)
      research: rendering
      verify: DONE. Tools on Q=/IN=: check-bundle, quote-verbatim, record-prepass, style-prepass, translation-owed, notes, brief load, entry-owed, open-questions, question-size, fragment-move (a stem), make reserve KIND=question, new-file and record-edit hooks; tests/tooling 1,094 passed; hook suites green
- [x] T10 Docs and agent contracts describe the new layout, tags and contents (FR-021)
      research: rendering
      verify: DONE. Docs and agent contracts: root and research CLAUDE.md, STYLE.md, page-session rules, interactive and tests CLAUDE.md, research-record-rules (+ the 303 section), doctrine, guards, efficiency-tooling, constitution pointer, seven agent files; README correction offered (readme-correction-offered.md)
- [x] T11 [US4] The pool's interactive pages regenerated (`make maps`) and every research link in them resolved against the built site (FR-020; SC-009)
      research: rendering
      verify: DONE. make maps SCOPE=all: maps clean; every modal research link (545, every class and compound kind) resolves to a built page of the site (SC-009)
- [x] T12 Verify and land: SC-002 and SC-006 as tests; `make record CHECK=1`; `make done` compared with T01's baseline; peers' unpushed research work checked (plan D12); the migration script deleted; pushed (SC-011)
      research: rendering
      verify: DONE. make done green on the merged tree (with feature 302): 130 s; make record CHECK=1 clean; pointer and entry checks clean; no peer clone holds unpushed research work; one-time scripts deleted
