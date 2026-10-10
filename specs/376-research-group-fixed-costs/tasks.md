# Tasks - feature 376, the claims sign-up sheet through tooling, and the archive before the web

Every task is tooling: nothing a map draws changes and no physical decision is made, so each is `research: rendering`.

## Occasions

- none: no map, sheet, glyph or placement changes

## Tasks

- [x] T01 The claims tool (plan D1, FR-001): `scripts/pages/research_claims.py` + `make research-claim` / `research-claims`; lock, owner, live rule (a done-like word anywhere after the owner), the sweep, old-line runs matched through moved-303.json, release with a reason
      research: rendering
      verify: DONE. research_claims.py + make research-claim/research-claims: lock, owner = clone name, live = owner's latest line with no done-like word, sweep writes release lines for closed features, old-line runs via moved-303.json, release by name with WHY; test_research_claims.py 8/8 incl. SC-001 on a 1,138-line sheet (at most five lines, overlap refused naming only the holder, release frees)
- [x] T02 The sheet's guard (plan D2, FR-002): `scripts/hooks/claims-file-hooks.sh`, registered on Read/Edit/Write and Bash
      research: rendering
      verify: DONE. claims-file-hooks.sh, no escape, matches invocations (a grep FOR the name is a mention); registered on Bash|Read|Edit|Write|NotebookEdit; test-claims-file-hooks.sh 24/24; make hooks-test green
- [x] T03 The text (plan D3, FR-003, FR-004): page-session-rules.md, CLAUDE.md's large-file rule and guard row, docs/guards.md
      research: rendering
      verify: DONE. page-session-rules.md names make research-claim/research-claims (make lines/append kept for handoffs and checks reports); CLAUDE.md states the GM's large-file rule and both guard rows; docs/guards.md records both guards
- [x] T04 The archive behind an unreadable page (plan D4, FR-006): quote_verbatim asks a PDF; CachedPages reads the archived text after the live page fails; archived passages count only when VERBATIM
      research: rendering
      verify: DONE. quote_verbatim asks a PDF (live flag); CachedPages reads the archive's text.txt after the live page fails, uncached; archived passages count only when VERBATIM, READABLE only where the link answered; 8 new tests red at HEAD in a worktree, green now (71 in the two files)
- [x] T07 The archive before an agent's own fetch (plan D6, FR-006): archive-first-hooks.sh + hm_archive_first.py, registered on WebFetch
      research: rendering
      verify: DONE. archive-first-hooks.sh + hm_archive_first.py on WebFetch: an actor's first fetch of a held page refused with its text path and capture date, the same actor's second passes; test-archive-first-hooks.sh 8/8
- [x] T05 Validation (plan D5, SC-004): make quote-verbatim before and after on real questions citing PDFs; recorded in research.md R2
      research: rendering
      verify: DONE. quote-verbatim on 0059 0235 0009 0080 0033 at HEAD (worktree) and with D4: 41 passages to VERBATIM, 11 notes to READABLE, none lost; 4 NOT-CHECKED -> UNFETCHABLE are one maff.go.jp PDF now asked and refused 403 (R2)
- [x] T06 Close: the tooling tests and make hooks-test green; feature report; landed
      research: rendering
      verify: DONE. tooling tests 171 passed, make hooks-test green; the sweep run once on the real sheet: 334 claims of closed features released in 9 lines (258 questions live -> 0); report written; landed by the push carrying this tick
