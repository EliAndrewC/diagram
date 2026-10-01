# Tasks - feature 301, the record as a manual

Every task is tooling over the record: nothing a map draws or asserts changes, so each is `research: rendering`.

- [ ] T01 Baseline: the regression baseline in a detached worktree; `make perf LABEL=301-start` (D1)
      research: rendering
      verify:
- [ ] T02 [US3] The read layer: pages enumerated from fragment directories (`store.page_dirs`); the works block derived in memory; `sources.record_text` for every engine reader; the scripts that read built pages moved to it (D1)
      research: rendering
      verify:
- [ ] T03 [US1] The link resolver: one id index over the record, every href resolved per form, an unresolved one a refusal; the record's own broken links found by it fixed (D2)
      research: rendering
      verify:
- [ ] T04 [US1] Notes per small page (numbered from 1, the foot with notes and the works cited) and once over the single page (D2)
      research: rendering
      verify:
- [ ] T05 [US1] The site: home, parent pages, small pages, registry pages, the single page with its table of contents, `nav.js` + `assets/site.js` + `assets/site.css`; `make record` writes it, `CHECK=1` builds to a temporary directory; `make citations` runs `make record`; the old page writers retired (D2)
      research: rendering
      verify:
- [ ] T06 [US1] The site looked at in a browser (the browser harness): a small page, a parent page, a registry page and the single page, the navigation and the footnote hover (D2)
      research: rendering
      verify:
- [ ] T07 [US2] Map links to the small pages; the `Entry:` form names fragments, read by `sources.py`, `check-entry-headings.py`, `_entry_owed.py`, `entry-gate.sh`, `_check_bundle.py`; the 162 `Entry:` lines converted (D3)
      research: rendering
      verify:
- [ ] T08 [US2] Inashiro regenerated and its modal links opened (SC-004); then `make maps` over the pool (D3)
      research: rendering
      verify:
- [ ] T09 [US3] Out of git: `.gitignore`, `git rm --cached` of every output; the push block's record check means "builds cleanly"; `gate-stamp.py`'s browser key; the record-edit guard re-aims a site page too (D4)
      research: rendering
      verify:
- [ ] T10 [US3] render-sync builds the record in main behind a stamp; the stamp's inputs are every tracked file under `research/` plus the Python modules the build actually imports (taken from `sys.modules` after a build, so `interactive/glossary.py` and `glossary_source.py` are in it - plan review item 3); the three cases of SC-005 as a test (D4)
      research: rendering
      verify:
- [ ] T11 [US5] `sync-with-main.sh` refuses a clone with no commit in common with main, with its test in `make hooks-test` (D4, FR-019)
      research: rendering
      verify:
- [ ] T12 [US4] The pointer sweep: `scripts/_pointer_sweep.py` run over the tracked files; the review list resolved by hand; the functional Python edited by hand - the files that name built outputs as paths rather than point at research: `interactive/sources.py`, `interactive/citations.py`, `interactive/record/*.py`, `tools/record_asset.py`, `tools/citations_asset.py`, `tools/glossary_asset.py`, `scripts/_quote_verbatim.py`, `scripts/_record_prepass.py`, `scripts/_entry_owed.py`, `scripts/_hm_record.py`, `scripts/gate-stamp.py`, `scripts/record-edit-hooks.sh`, and the tests under `tests/interactive/` and `tests/tools/` that open built pages (plan review item 4) (D5)
      research: rendering
      verify:
- [ ] T13 [US4] The pointer check at the gate and the push; `make fragment-move` with its test; the docs say a pointer names a fragment (D5)
      research: rendering
      verify:
- [ ] T17 [US4] `spec-lint --delta` judges a pre-existing spec directory by the findings the push adds (base vs head, prefix-free multiset), its selftest covering a pointer-only edit (passes) and a new finding (fails); the sweep pushed through the review and plan gates' escapes with the reason logged (FR-027)
      research: rendering
      verify:
- [ ] T14 [US6] The user-level sudo hook, its self-test, `make hooks-test` running it, the guard rows; the GM's other containers checked for the mount (D6)
      research: rendering
      verify:
- [ ] T15 Land: `make perf LABEL=301-end` and the report; `make done` green; push; `/diagram` built by render-sync; `git gc --aggressive --prune=now` on `/diagram` with sizes (D7)
      research: rendering
      verify:
- [ ] T16 [US5] The scrub, in this order (plan review items 1 and 2): every live session told to push and pause FIRST; then the rewrite built from main's tip in a scratch mirror and verified; `docs/history-rewrite-301.md` committed INTO the rewritten history as its last commit; immediately before the GM's force push, main's tip checked equal to the tip the mirror was built from (rebuilt if not); after it, `/diagram` reset and repacked; every clone under `.clones/` checked for unpushed commits (live or stale) and those replayed or bundled before any clone is deleted or re-cloned (D7)
      research: rendering
      verify:
