# Tasks - feature 301, the record as a manual

Every task is tooling over the record: nothing a map draws or asserts changes, so each is `research: rendering`.

- [x] T01 Baseline: the regression baseline in a detached worktree; `make perf LABEL=301-start` (D1)
      research: rendering
      verify: DONE. DONE. make perf LABEL=301-start on the unmodified code (20.2 s total, median 4.5 s, worst 7.0 s); the regression baseline taken in a detached worktree at main's tip: make maps there stops at the same tripwire seed 33 refusal as the clone (research R10 - pre-existing, ledgered)
- [x] T02 [US3] The read layer: pages enumerated from fragment directories (`store.page_dirs`); the works block derived in memory; `sources.record_text` for every engine reader; the scripts that read built pages moved to it (D1)
      research: rendering
      verify: DONE. DONE. sources.record_text reads every page in memory (pages found by fragment directory); citations.fill_works derives the works block from strings; the scripts (_record_prepass, _quote_verbatim, _entry_owed, _open_questions, _check_bundle via prepass, check-entry-headings, footnote_census, gate-stamp browser key, the record-edit guard) read the new forms; make quick ALL=1 5248 passed with no built page on disk
- [x] T03 [US1] The link resolver: one id index over the record, every href resolved per form, an unresolved one a refusal; the record's own broken links found by it fixed (D2)
      research: rendering
      verify: DONE. DONE. record/site_links.py: one id index, every href resolved per form, an unresolved one a refusal naming the fragment; the real record built with 0 refusals; test_record_site.py SC-003 walks every link of both forms (0 broken) and a small record proves each refusal
- [x] T04 [US1] Notes per small page (numbered from 1, the foot with notes and the works cited) and once over the single page (D2)
      research: rendering
      verify: DONE. DONE. record/site_notes.py: a small page numbers from 1 with its notes and works at the foot; Numbering counts once through the single page with unique fnref ids; SC-002 holds on every small page and on all.html (1..N)
- [x] T05 [US1] The site: home, parent pages, small pages, registry pages, the single page with its table of contents, `nav.js` + `assets/site.js` + `assets/site.css`; `make record` writes it, `CHECK=1` builds to a temporary directory; `make citations` runs `make record`; the old page writers retired (D2)
      research: rendering
      verify: DONE. DONE. make record builds research/site/ (2,640 pages, ~4 s): home, part pages, small pages, registry pages, all.html with its contents, nav.js + assets/site.js + site.css; CHECK=1 builds in memory; make citations is a name for record; tools/citations_asset.py retired; 100% coverage of site, site_links, site_notes
- [x] T06 [US1] The site looked at in a browser (the browser harness): a small page, a parent page, a registry page and the single page, the navigation and the footnote hover (D2)
      research: rendering
      verify: DONE. DONE. Looked at in Chromium (Playwright, file://): a small page with its sidebar, foot notes and the footnote hover; a part page with its question list and leads; a registry entry page; the phone width; the single page, which keeps the glossary hover wrapped lazily (research R8: 3.2-3.5 s against 10.8 s eager)
- [x] T07 [US2] Map links to the small pages; the `Entry:` form names fragments, read by `sources.py`, `check-entry-headings.py`, `_entry_owed.py`, `entry-gate.sh`, `_check_bundle.py`; the 162 `Entry:` lines converted (D3)
      research: rendering
      verify: DONE. DONE. research_questions links SITE_PAGES + <page dir>/<heading id>.html; Entry: lines name fragments (162 converted by the sweep), read by sources.entry_fragments, check-entry-headings (selftest), _entry_owed (fragment diff, test), _open_questions
- [x] T08 [US2] Inashiro regenerated and its modal links opened (SC-004); then `make maps` over the pool (D3)
      research: rendering
      verify: DONE. DONE. Inashiro regenerated: its 91 modal links all open existing small pages of the built site; make maps SCOPE=all: kashikawa, kuwabata, mizuguchi, sawada regenerated, maps clean; 563 modal links over the pool's 7 pages, 0 missing (SC-004); tripwire seed 33 fails identically on main (research R10)
- [x] T09 [US3] Out of git: `.gitignore`, `git rm --cached` of every output; the push block's record check means "builds cleanly"; `gate-stamp.py`'s browser key; the record-edit guard re-aims a site page too (D4)
      research: rendering
      verify: DONE. DONE. .gitignore covers research/site, the old page paths, citations/ and assets/glossary.js; 113 outputs git rm'd; the push's record check means builds-cleanly; gate-stamp's browser key hashes fragments; the record-edit guard re-aims site pages (16 checks green)
- [x] T10 [US3] render-sync builds the record in main behind a stamp; the stamp's inputs are every tracked file under `research/` plus the Python modules the build actually imports (taken from `sys.modules` after a build, so `interactive/glossary.py` and `glossary_source.py` are in it - plan review item 3); the three cases of SC-005 as a test (D4)
      research: rendering
      verify: DONE. DONE. pipeline/record_build.py: render-sync rebuilds behind a stamp of the record's files, glossary.json and the engine modules the build imports (sys.modules); test_record_build.py holds SC-005's three cases; render_cache.main calls it where a record exists
- [x] T11 [US5] `sync-with-main.sh` refuses a clone with no commit in common with main, with its test in `make hooks-test` (D4, FR-019)
      research: rendering
      verify: DONE. DONE. sync-with-main.sh refuse_unrelated_history at sync-in and push; case 11 of test-sync-with-main.sh (50 checks green)
- [x] T12 [US4] The pointer sweep: `scripts/_pointer_sweep.py` run over the tracked files; the review list resolved by hand; the functional Python edited by hand - the files that name built outputs as paths rather than point at research: `interactive/sources.py`, `interactive/citations.py`, `interactive/record/*.py`, `tools/record_asset.py`, `tools/citations_asset.py`, `tools/glossary_asset.py`, `scripts/_quote_verbatim.py`, `scripts/_record_prepass.py`, `scripts/_entry_owed.py`, `scripts/_hm_record.py`, `scripts/gate-stamp.py`, `scripts/record-edit-hooks.sh`, and the tests under `tests/interactive/` and `tests/tools/` that open built pages (plan review item 4) (D5)
      research: rendering
      verify: DONE. DONE. scripts/_pointer_sweep.py rewrote ~470 files (live files by exact, anchor, prefix or verbatim match; 99 hand resolutions in pointer-review.md; landed specs' retired headings and stale fragments to their page directory); the functional Python and the tests edited by hand; check-research-pointers.py clean over the tree
- [x] T13 [US4] The pointer check at the gate and the push; `make fragment-move` with its test; the docs say a pointer names a fragment (D5)
      research: rendering
      verify: DONE. DONE. check-research-pointers.py at the gate (tests/tooling/test_research_pointers.py) and the push (selftest first); make fragment-move (scripts/_fragment_move.py, selftest: heading id, own-page and cross-page links, confusables, pointers); CLAUDE.md, research/CLAUDE.md, research-record-rules.md, research-doctrine.md, the constitution, interactive/pipeline/tests CLAUDE.md say a pointer names a fragment
- [x] T17 [US4] `spec-lint --delta` judges a pre-existing spec directory by the findings the push adds (base vs head, prefix-free multiset), its selftest covering a pointer-only edit (passes) and a new finding (fails); the sweep pushed through the review and plan gates' escapes with the reason logged (FR-027)
      research: rendering
      verify: DONE. DONE. spec-lint --delta judges a spec directory present at the merge base by what the push adds (at_base, introduced: prefix-free and inner-location-free multiset); selftest covers a pointer-only edit (passes), a new finding (fails), a new directory (whole); on this delta spec 233's 62 old findings introduce 0
- [x] T14 [US6] The user-level sudo hook, its self-test, `make hooks-test` running it, the guard rows; the GM's other containers checked for the mount (D6)
      research: rendering
      verify: DONE. DONE. ~/.claude/hooks/missing-program-hook.sh on PostToolUse and PostToolUseFailure in ~/.claude/settings.json; fired live in this session on an empty which; self-test 151/151 (both payloads, every form, every repetition, the host silent); make hooks-test runs it; guards.md and CLAUDE.md rows; all four running containers mount ~/.claude (research R9)
- [ ] T15 Land: `make perf LABEL=301-end` and the report; `make done` green; push; `/diagram` built by render-sync; `git gc --aggressive --prune=now` on `/diagram` with sizes (D7)
      research: rendering
      verify:
- [ ] T16 [US5] The scrub, in this order (plan review items 1 and 2): every live session told to push and pause FIRST; then the rewrite built from main's tip in a scratch mirror and verified; `docs/history-rewrite-301.md` committed INTO the rewritten history as its last commit; immediately before the GM's force push, main's tip checked equal to the tip the mirror was built from (rebuilt if not); after it, `/diagram` reset and repacked; every clone under `.clones/` checked for unpushed commits (live or stale) and those replayed or bundled before any clone is deleted or re-cloned (D7)
      research: rendering
      verify:
