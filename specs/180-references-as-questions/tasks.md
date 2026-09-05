# Tasks - feature 180

Spec: [`spec.md`](spec.md) (FAITHFUL, spec-fidelity round 3). Request: [`request.md`](request.md).

Every task here is `research: rendering` - a map-page convention with nothing physical behind it. No
research entry is read for a rule, none is edited (spec FR-018).

## The record, read as questions

- [ ] T01 FR-004/FR-005/FR-006: `sources.py` - `RESEARCH_URL`, `github_anchor()`, `question_text()`, `research_questions()`
      research: rendering
      verify: unit tests on live headings (a `?`, a ` - `, a parenthetical, CJK, a repeated heading's `-1`);
      `research_questions` on the farmhouse entry returns its three sections in the entry's order
- [ ] T02 FR-011/FR-012: `page.explanations()` and `place.place_card()` emit `questions`, drop `refs`/`entry`/`sources`; `citations()` removed
      research: rendering
      verify: `test_page.py` JSON-shape assertions updated; every class whose entry quotes a heading resolves to >= 1 question; grep shows no consumer of `citations`
- [ ] T02a FR-012a: `_ENTRY_FILE` accepts one directory level (the Principle XIV fix the review noticed)
      research: rendering
      verify: a test entry naming `research/cities/<file>.md` resolves to its section; the 51 live entries are unaffected

## The page

- [ ] T03 FR-001/FR-002: the explanation footer loses `#x-entry`; the references link keys on `questions`
      research: rendering
      verify: `render_page` output carries no `x-entry`; `page.js` sets nothing on it
- [ ] T04 FR-003/FR-007/FR-008/FR-009/FR-010: `openRefs()` lists question links (new tab), the intro sentence, the button text "Return to <Name> writeup"
      research: rendering
      verify: the browser test opens the bund's references, sees >= 1 link to `RESEARCH_URL`, the button text, and no `Record:` anywhere in the explanation
- [ ] T05 FR-015: regenerate the reference hamlet's page and look at it
      research: rendering
      verify: `make map GEN=pool/hamlets/inashiro/inashiro.gen.py`; the farmhouse modal shows no Record line; its references list the three homestead questions with working anchors

## The documentation

- [ ] T06 FR-016: `research/README.md` - who the record is for and how it is organized for them
      research: rendering
      verify: the section names the audience, the question-shaped heading rule, the four-step chain, why sources are one click out, and that new questions are the GM's to name
- [ ] T07 FR-016: `interactive/CLAUDE.md` (the modal as it now is; the `sources.py` row) and the root `CLAUDE.md` pointer
      research: rendering
      verify: read back; both describe what ships, not what shipped in 134

## Closing

- [ ] T08 FR-014: tests for everything above, at the 100% floor
      research: rendering
      verify: `make test-file FILE=tests/interactive/test_page.py`, `test_sources.py`, then the browser test at the gate
- [ ] T09 `make done` green, the pairing recorded, and the answer to the GM
      research: rendering
      verify: green gate; `PAIR_OK` with the reason (this feature rolls no new map; the page's TEXT changed, and the GM reads that page themselves)
