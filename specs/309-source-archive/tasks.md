# Tasks - feature 309, source archive

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Measurement: [`measurement/`](measurement/).

## Occasions

- none: the feature draws nothing on a map - no element new to a map, no glyph, no placement rule; the record's source pages
  gain one line of links.

## Phase 1 - the engine half (US2, US3; FR-001, FR-007, FR-010)

- [x] T01 [US2] `record/archive.py`: the cited-URL census (registry entries with their comments, footnote links without),
      the URL id, the manifest reader, the refusals with their command, the archived-copy line; red-green tests in
      `tests/interactive/test_record_archive.py`
      research: rendering
      verify: DONE. record/archive.py; 13 tests in test_record_archive.py pass (census, ids, refusals, pending week, entry line, site build)
- [x] T02 [US3] `site.py`: the archived-copy line under each source's citation line; the refusals gathered with the build's
      research: rendering
      verify: DONE. site.py entry_html + run; test_a_source_page_shows_its_archived_copy_and_the_build_refuses_a_missing_one passes

## Phase 2 - the tooling half (US1, US2; FR-002 - FR-006, FR-008, FR-009, FR-011, FR-012)

- [x] T10 [US1] `scripts/_archive.py`: fetch and render, the dead/refused orders (plan D2, D10), the Wayback fallback, parts
      past 95 MB, the one working copy under the host lock, the push by environment, the manifest rows, the GM copies from
      `gm-copies.json`, the lanes, the report; tests in `tests/tooling/test_archive.py` (fixtures, a stand-in browser, a
      bare remote on disk)
      research: rendering
      verify: DONE. _archive.py; 33 tests in test_archive.py pass (dead/refused orders, wayback, parts, lanes, bare-remote push, pending-upload settle, report)
- [x] T11 [US2] `make reserve KIND=registry ... URL=` archives the new entry's URL (`reserve-prefix.py:archive_at_cite`);
      `make archive`, `make archive-sources`; the mirror's `.gitignore`; `check-research-pointers.py` knows `research/archive/`
      research: rendering
      verify: DONE. archive_at_cite + its test; make archive / archive-sources; .gitignore; check-research-pointers.py clean
- [x] T12 [US1] FR-012: the GM's `academic-sources/` matched to keys, `research/archive/gm-copies.json` (42 entries, 33
      matched over 30 keys, 7 copy no cited source - plan.md)
      research: rendering
      verify: DONE. gm-copies.json committed: 40 matched entries + 2 GM lists, 33 matched over 30 keys, 7 unmatched listed

## Phase 3 - the backfill (US1; SC-001, SC-002, SC-005)

- [x] T20 [US1] One URL end to end (`make archive URL=` on visit-toyama-sankyoson): captured, pushed, its row written
      research: rendering
      verify: DONE. make archive URL=visit-toyama sankyoson: archived, pushed to diagram-research (page.mhtml 5.2 MB, served.html, text.txt, capture.json), row 6852fcd492a9.json
- [ ] T21 [US1] The backfill (`make archive-sources WORKERS=4`) over every cited URL; the coverage report recorded in
      `measurement/coverage.txt` (SC-001); every unreachable URL with its reason
      research: rendering
- [ ] T22 [US1] SC-002: 20 archived copies drawn at random (5+ Wikipedia, 5+ PDFs, 5+ small sites) from a fresh clone of the
      archive repository - each opens (MHTML parses, PDF has pages) and holds its entry's quoted passage where it quotes one;
      recorded in `measurement/sc002.txt`
      research: rendering
- [ ] T23 [US1] SC-005: the backfill run again on the complete archive fetches nothing
      research: rendering

## Phase 4 - close

- [x] T30 The docs: `research/CLAUDE.md` (the operative rule) and `docs/research-doctrine.md` (the GM's words)
      research: rendering
      verify: DONE. research/CLAUDE.md paragraph + docs/research-doctrine.md section written
- [ ] T31 `make record CHECK=1` builds cleanly with the manifest complete (SC-004 proven by its test); `make done` green
      research: rendering
