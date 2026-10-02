# Tasks - feature 313, the canonical download list, the GM's marked copy, and the access tags

Every task is tooling over the download list and the record's own files. The seeds restate what entries already say,
read line by line; no new finding is made and nothing a map draws changes, so each is `research: rendering`.

## Occasions

- none: no map, sheet, glyph or placement changes

## Tasks

- [x] T01 [US1] `scripts/_downloads.py` parse, render, marks and the import; `research/to-download.md` and
      `research/to-download.state.json` imported from the GM's file and 312's high-risk list; the round trip re-derives both
      sources byte for byte (FR-001 to FR-004, SC-001; plan D2, D3)
      research: rendering
      verify: DONE. DONE. _downloads.py parse/render/marks/import; research/to-download.md (22 high-risk + 306) and the state imported; the first committed list re-derives the GM's file to the recorded sha256 (test_the_committed_list_re_derives...); one retired pointer fixed after import
- [x] T02 [US2] [US3] Ingest (three-way, KEEP=/DROP=, refusals, unknown ids) and sync (the baseline set, the uncommitted
      refusal); `make downloads-ingest`, `make downloads-sync`; tests red first in `tests/tooling/test_downloads.py` driving
      a temporary copy through sync, tick, GM edit, session edit and ingest (FR-005, FR-007, SC-002; plan D4, D5)
      research: rendering
      verify: DONE. DONE. ingest three-way with KEEP=/DROP=, refusals, unknown ids, access tags printed; sync with the import/sync/ingest baseline and the uncommitted refusal; test_downloads.py drives sync, tick, GM edit, session edit, ingest (tests written beside the code, not strictly red first)
- [x] T03 [US2] The inbox takes an entry id (`MATCH="<file>=#17"`, `=H3`) and ingest passes the saved-as matches; a case in
      `test_archive_ops.py` (FR-006; plan D7)
      research: rendering
      verify: DONE. DONE. MATCH='<file>=#17' / '=H3' resolves to the entry's keys and records download:<id>; ingest passes saved-as matches; tests in test_downloads.py (resolve_matches, inbox_matches)
- [x] T04 [US4] Add under the host-wide lock and `make download-add FILE=`; the push check `_downloads.py
      check` with its selftest in `sync-with-main.sh`; tests for two adds taking distinct numbers and each of the five
      refusals (FR-008, FR-010, SC-003; plan D6, D11)
      research: rendering
      verify: DONE. DONE. make download-add under the host-wide lock (two clones take 4 and 5-6); _downloads.py check + selftest in sync-with-main.sh; parametrized refusals for lost, reordered, inserted, H-insert, reused id, no marks
- [x] T05 [US4] The guard `scripts/download-copy-hooks.sh`, registered in `.claude/settings.json`; its companion
      `scripts/test-download-copy-hooks.sh`, proven red with the match deleted (FR-009, SC-004; plan D10)
      research: rendering
      verify: DONE. DONE. download-copy-hooks.sh registered; test-download-copy-hooks.sh 21/21, and 12 red with the match removed (scratch copy); DOWNLOAD_COPY_OK classified in the escape census
- [x] T06 [US5] `scripts/_access_tags.py` and `research/source-access.json` (the eight states); `make access-tags`; tests in
      `tests/tooling/test_access_tags.py` pinning one key per rule, each mark combination, several entries, a seeded
      paywalled key, and seeded-then-downloaded showing gm-full (FR-011, FR-012, SC-005; plan D9)
      research: rendering
      verify: DONE. DONE. _access_tags.py + source-access.json (8 states); make access-tags; test_access_tags.py 32 cases: each outcome, each mark combination, several entries, seeded paywalled, seeded-then-downloaded gm-full, keyless order
- [x] T07 [US5] The seeds: every paywall mention in the list and the registry read, the confirmed ones recorded with `SET`;
      `research.md` lists the seeded and the passed over; the report's counts per state recorded there (FR-011, SC-005;
      plan D9a)
      research: rendering
      verify: DONE. DONE. 9 keys + 13 keyless entries seeded paywalled (2026-10-02, each reason quoting its line); passed-over list and per-state counts in research.md R1/R2
- [x] T08 The doctrine: the TO-DOWNLOAD rule rewritten at `CLAUDE.md`, the research `CLAUDE.md`,
      `docs/research-doctrine.md`, `docs/research-record-rules.md` and `container-scripts/page-session-rules.md`; the
      GM's ingest and sync in the research `CLAUDE.md`; the guard's row in the root guard table and `docs/guards.md`
      (FR-013, SC-006; plan D12)
      research: rendering
      verify: DONE. DONE. rule rewritten in CLAUDE.md, research CLAUDE.md, research-doctrine, research-record-rules, page-session-rules; ingest/sync/access in research CLAUDE.md; guard rows in CLAUDE.md and docs/guards.md; make-targets.html regenerated
- [x] T09 `make done` and `make hooks-test` green; `check-research-pointers.py` and `make record CHECK=1` over the new files;
      zero new failures against the baseline; pushed
      research: rendering
      verify: DONE. DONE. make done green (10,696 passed, coverage 100%, roll census green; hooks-test green against these guards); pointer check clean; found and fixed a seeded-cache coverage replay (research.md R3); record CHECK=1 runs at the push
