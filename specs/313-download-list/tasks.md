# Tasks - feature 313, the canonical download list, the GM's marked copy, and the access tags

Every task is tooling over the download list and the record's own files. The seeds restate what entries already say,
read line by line; no new finding is made and nothing a map draws changes, so each is `research: rendering`.

## Occasions

- none: no map, sheet, glyph or placement changes

## Tasks

- [ ] T01 [US1] `scripts/_downloads.py` parse, render, marks and the import; `research/to-download.md` and
      `research/to-download.state.json` imported from the GM's file and 312's high-risk list; the round trip re-derives both
      sources byte for byte (FR-001 to FR-004, SC-001; plan D2, D3)
      research: rendering
      verify:
- [ ] T02 [US2] [US3] Ingest (three-way, KEEP=/DROP=, refusals, unknown ids) and sync (the baseline set, the uncommitted
      refusal); `make downloads-ingest`, `make downloads-sync`; tests red first in `tests/tooling/test_downloads.py` driving
      a temporary copy through sync, tick, GM edit, session edit and ingest (FR-005, FR-007, SC-002; plan D4, D5)
      research: rendering
      verify:
- [ ] T03 [US2] The inbox takes an entry id (`MATCH="<file>=#17"`, `=H3`) and ingest passes the saved-as matches; a case in
      `test_archive_ops.py` (FR-006; plan D7)
      research: rendering
      verify:
- [ ] T04 [US4] Add under the host-wide lock and `make download-add FILE=`; the push check `_downloads.py
      check` with its selftest in `sync-with-main.sh`; tests for two adds taking distinct numbers and each of the five
      refusals (FR-008, FR-010, SC-003; plan D6, D11)
      research: rendering
      verify:
- [ ] T05 [US4] The guard `scripts/download-copy-hooks.sh`, registered in `.claude/settings.json`; its companion
      `scripts/test-download-copy-hooks.sh`, proven red with the match deleted (FR-009, SC-004; plan D10)
      research: rendering
      verify:
- [ ] T06 [US5] `scripts/_access_tags.py` and `research/source-access.json` (the eight states); `make access-tags`; tests in
      `tests/tooling/test_access_tags.py` pinning one key per rule, each mark combination, several entries, a seeded
      paywalled key, and seeded-then-downloaded showing gm-full (FR-011, FR-012, SC-005; plan D9)
      research: rendering
      verify:
- [ ] T07 [US5] The seeds: every paywall mention in the list and the registry read, the confirmed ones recorded with `SET`;
      `research.md` lists the seeded and the passed over; the report's counts per state recorded there (FR-011, SC-005;
      plan D9a)
      research: rendering
      verify:
- [ ] T08 The doctrine: the TO-DOWNLOAD rule rewritten at `CLAUDE.md`, the research `CLAUDE.md`,
      `docs/research-doctrine.md`, `docs/research-record-rules.md` and `container-scripts/page-session-rules.md`; the
      GM's ingest and sync in the research `CLAUDE.md`; the guard's row in the root guard table and `docs/guards.md`
      (FR-013, SC-006; plan D12)
      research: rendering
      verify:
- [ ] T09 `make done` and `make hooks-test` green; `check-research-pointers.py` and `make record CHECK=1` over the new files;
      zero new failures against the baseline; pushed
      research: rendering
      verify:
