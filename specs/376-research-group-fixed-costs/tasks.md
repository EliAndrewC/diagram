# Tasks - feature 376, the claims sign-up sheet through tooling, and the archive before the web

Every task is tooling: nothing a map draws changes and no physical decision is made, so each is `research: rendering`.

## Occasions

- none: no map, sheet, glyph or placement changes

## Tasks

- [ ] T01 The claims tool (plan D1, FR-001): `scripts/pages/research_claims.py` + `make research-claim` / `research-claims`; lock, owner, live rule (a done-like word anywhere after the owner), the sweep, old-line runs matched through moved-303.json, release with a reason
      research: rendering
      verify: tests/tooling/test_research_claims.py - SC-001 (a sheet the real one's size: at most five lines; overlap refused naming only the holder; a release frees it), the lock, an old free-text line matched
- [ ] T02 The sheet's guard (plan D2, FR-002): `scripts/hooks/claims-file-hooks.sh`, registered on Read/Edit/Write and Bash
      research: rendering
      verify: tests/hooks/test-claims-file-hooks.sh - every hand route refused naming the FR-001 command (SC-002); the FR-001 commands pass; make hooks-test green
- [ ] T03 The text (plan D3, FR-003, FR-004): page-session-rules.md, CLAUDE.md's large-file rule and guard row, docs/guards.md
      research: rendering
      verify: SC-002's rules line; SC-003's CLAUDE.md line
- [ ] T04 The archive behind an unreadable page (plan D4, FR-006): quote_verbatim asks a PDF; CachedPages reads the archived text after the live page fails; archived passages count only when VERBATIM
      research: rendering
      verify: tests in test_quote_verbatim.py and test_sources.py fail on the gap (a PDF NOT-CHECKED with its text archived) and pass after
- [ ] T07 The archive before an agent's own fetch (plan D6, FR-006): archive-first-hooks.sh + hm_archive_first.py, registered on WebFetch
      research: rendering
      verify: tests/hooks/test-archive-first-hooks.sh - first fetch of a held page refused with its text; the same actor's second passes; another actor, an unheld page, a WebSearch
- [ ] T05 Validation (plan D5, SC-004): make quote-verbatim before and after on real questions citing PDFs; recorded in research.md R2
      research: rendering
      verify: every changed verdict is NOT-CHECKED -> VERBATIM
- [ ] T06 Close: the tooling tests and make hooks-test green; feature report; landed
      research: rendering
      verify: the push accepted
