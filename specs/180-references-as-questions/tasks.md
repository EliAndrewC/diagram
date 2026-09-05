# Tasks - feature 180

Spec: [`spec.md`](spec.md) (FAITHFUL, spec-fidelity round 3). Request: [`request.md`](request.md).

Every task here is `research: rendering` - a map-page convention with nothing physical behind it. No
research entry is read for a rule, none is edited (spec FR-018).

## The record, read as questions

- [x] T01 FR-004/FR-005/FR-006: `sources.py` - `RESEARCH_URL`, `github_anchor()`, `question_text()`, `research_questions()`
      research: rendering
      verify: DONE. `RESEARCH_URL`, `github_anchor` (GitHub's rule, counted over every heading level and outside code fences), `question_text`, `research_questions` (entry order, deduplicated). Seven anchors read off the LIVE GitHub rendering on 2026-09-05 are pinned; the farmhouse entry resolves to its three homestead sections in the entry's order
- [x] T02 FR-011/FR-012: `page.explanations()` and `place.place_card()` emit `questions`, drop `refs`/`entry`/`sources`; `citations()` removed
      research: rendering
      verify: DONE. `explanations()` and `place_card()` emit `questions` and drop `refs`/`entry`/`sources`; the `fc.sources` fallback is gone (its one beneficiary, `fallow`, was already hidden); `citations()` deleted with its single test assertion. `FeatureClass.sources` stays in the registry and `test_classes` still asserts it
- [x] T02a FR-012a: `_ENTRY_FILE` accepts one directory level (the Principle XIV fix the review noticed)
      research: rendering
      verify: DONE. `_ENTRY_FILE` takes one directory level; `test_sources.py` proves `research/cities/fabric.md - 'Urban commoners built in continuous street walls'` resolves to its URL and its sources. The 51 live entries name only top-level files, so no page changed
## The page

- [x] T03 FR-001/FR-002: the explanation footer loses `#x-entry`; the references link keys on `questions`
      research: rendering
      verify: DONE. The footer is `See references (N)` + Close; `x-entry` appears nowhere in markup or script (a test splits the page and checks both halves separately, because the script's own comment names the old footer to say it is gone)
- [x] T04 FR-003/FR-007/FR-008/FR-009/FR-010: `openRefs()` lists question links (new tab), the intro sentence, the button text "Return to <Name> writeup"
      research: rendering
      verify: DONE. `openRefs()` builds one `a.q` per question (`target=_blank`, `rel=noopener`), `page.REFERENCES_LEAD` above the list, the button `Return to <Name> writeup`; the browser test asserts the links point at `RESEARCH_URL`, the count on the link equals the number of links, the button text for the bund, and no `Record:` in the explanation
- [x] T05 FR-015: regenerate the reference hamlet's page and look at it
      research: rendering
      verify: DONE. `make map GEN=pool/hamlets/inashiro/inashiro.gen.py` REGENERATED (18.1 s); read back from the page JSON: farmhouse -> the three homestead questions in entry order with anchors of the form `homesteads.md#how-close-does-a-farmhouse-stand-to-the-paddy-...`; paddy 4, village lane 2, place 1; `x-entry` absent, `r-intro` present
## The documentation

- [x] T06 FR-016: `research/README.md` - who the record is for and how it is organized for them
      research: rendering
      verify: DONE - in `research/CLAUDE.md`, NOT `README.md`: the README guard (constitution XVII) refused the edit with no escape hatch, and its own alternative - the directory's auto-loading CLAUDE.md - reaches the author of a new entry, which a README does not. Spec FR-016 and D9 amended to say so; spec-fidelity round 4 asked to grade the amendment and the file's content
- [x] T07 FR-016: `interactive/CLAUDE.md` (the modal as it now is; the `sources.py` row) and the root `CLAUDE.md` pointer
      research: rendering
      verify: DONE. `interactive/CLAUDE.md`: the intro, the `sources.py` row, "one click away" corrected, and a new section with the on-page / where-from table and the anchor rule; root `CLAUDE.md` "WHAT THE RECORD IS FOR" gains the by-question pointer to `research/CLAUDE.md`
## Closing

- [ ] T08 FR-014: tests for everything above, at the 100% floor
      research: rendering
      verify: `make test-file FILE=tests/interactive/test_page.py`, `test_sources.py`, then the browser test at the gate
- [ ] T09 `make done` green, the pairing recorded, and the answer to the GM
      research: rendering
      verify: green gate; `PAIR_OK` with the reason (this feature rolls no new map; the page's TEXT changed, and the GM reads that page themselves)
