# Tasks - feature 311, the record's checks owed by what an edit touches, and the question that says why it is asked

Every task is tooling over the record, or an intro that states only what the setting has and the class its question's
research already reaches: nothing a map draws changes and no new finding is made, so each is `research: rendering`.

## Occasions

- none: no map, sheet, glyph or placement changes; the record's checks are this feature's subject, owed by its own command

## Tasks

- [ ] T01 [US2] `scripts/_record_units.py` (words, blocks, notes, fingerprints, the FR-004 decision over plain dicts) and `scripts/_record_owed.py` (the base read once, the units, `--unanswered`, `--between`); `make record-owed`; tests red first in `tests/tooling/test_record_owed.py`, one per FR-004 row and Edge Case (FR-003, FR-004; plan D1, D2, D5)
      research: rendering
- [ ] T02 [US2] `_entry_owed.moved_anchors` on the normalized body - an intro, a comment, a tag marker owe no modal (FR-004 last row; plan D8); cases in `test_entry_owed.py`
      research: rendering
- [ ] T03 [US3] The answer record: `make record-checked` (BUNDLE= or Q=/NOTES=/KEY=/KIND=), records under the git dir keyed to fingerprints; `entry-gate.sh` as the record gate with `RECORD_CHECKS_OK` beside `ENTRY_DRIFT_OK`; `test-entry-gate.sh` unanswered, stale, answered, escape, silent (FR-006, FR-007, SC-004; plan D6, D7)
      research: rendering
- [ ] T04 [US2] `_check_bundle.py`: the not-owed refusal and `NOT_OWED_OK`, the owed-notes default, `owed-checks:` and `unit:` lines in the MANIFEST, `FOR=intro-check` with `QS=` batches; `check-bundle-hooks.sh` refusing a dispatch the MANIFEST does not owe (`CHECK_NOT_OWED_OK`), `intro-check` added; their tests (FR-005; plan D4, D9)
      research: rendering
- [ ] T05 [US1] The intro form `<p class="intro">`: `research/STYLE.md`, the research `CLAUDE.md`, `test_record_format.py`'s shape test; the built page checked to show it after the confusables block (FR-002; plan D3)
      research: rendering
- [ ] T06 [US1] `.claude/agents/intro-check.md`, its tier in `test_agent_models.py`, `_ledger_lint.py`; seeded runs three a leg on the three known questions (FR-001, SC-005; plan D4)
      research: rendering
- [ ] T07 [US1] The parley-room intro on `research/questions/0094-rooms-for-a-parley-across-a-border.html`, from the GM's draft; its owed units answered (FR-009, SC-001)
      research: rendering
- [ ] T08 [US1] The backfill: `intro-check` over every question in batches; `backfill.md`; every NEEDS-INTRO and INTRO-FIX written or fixed from the drawing page and `make canon`; each written intro's owed units answered, two rounds at most (FR-008, SC-003; plan D10)
      research: rendering
- [ ] T09 [US2] The doctrine follows the command: research `CLAUDE.md`, `docs/research-doctrine.md`, `container-scripts/page-session-rules.md`, the root `CLAUDE.md` guard table, `docs/guards.md`, the five check contracts (descriptions and bodies) (FR-010; plan D11)
      research: rendering
- [ ] T10 [US2] SC-002: `--between` over the last 30 record-only commits on main, tabulated in `research.md` beside what the doctrine's wording owed
      research: rendering
- [ ] T11 `make done` green, `make hooks-test`, `make record CHECK=1`; zero new failures against the baseline; pushed
      research: rendering
