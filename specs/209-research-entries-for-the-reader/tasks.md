# Tasks - 209 research entries for the reader

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` (the record's form; nothing physical).

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code (up to five rounds)
      research: rendering
      verify: DONE. FAITHFUL at round 3 of 5: round 1 required SOURCES.html swept under rules 2 and 3 (only the machine-read markers kept, in comments, with the classifier reading comment text), FR-005 definite over all 16 pages, D1's count; round 2 one word (SC-002 counts all sixteen); round 3 FAITHFUL. The reviewer's aside: D5's fold-back (one agent instead of record-format beside quote-check) is the GM's call
- [x] T02 the glossary on the record (FR-001): `record_glossary_js()`, `tools/glossary_asset.py`, `make glossary`, `record.js` wrap + `record.css` `.gl`, the script tag on all 16 pages, ~75 record terms defined; the synthetic record hover in the browser module
      research: rendering
      verify: DONE. glossary.py record_glossary_js() + ~270 record terms (298 total, every one used by a modal or a page, no duplicate variant); tools/glossary_asset.py + make glossary (tests/tools/test_glossary_asset.py 2 passed); record.js wraps text nodes with a Unicode word boundary, definition in the footnote box; record.css .gl; the script tag on all 16 pages; browser test test_the_record_page_defines_its_terms_on_hover_in_the_footnote_box green (18 passed in the synthetic module)
- [x] T03 the fields are comments (FR-002, mechanical): 287 `Grounds:`/`Evidence:` fields across 15 pages, two merged paragraphs by hand
      research: rendering
      verify: DONE. 287 fields across 15 pages by scripts/fields_to_comments (scratchpad; recorded in research.md R2), two merged paragraphs by hand; test_the_fields_for_a_session_are_comments green on all 15
- [x] T04 the judgment sweep (FR-002, FR-003, FR-006): seven editors under the rulebook over the 15 pages; `record-format` over every page after; findings resolved
      research: rendering
      verify: DONE. Seven editors swept the 15 pages under the rulebook (specs/209 research.md R2); five record-format checks (Opus) then reported over all 16 pages - the tally is the 2026-09-07 row of docs/review-ledger.md - and five editors plus a script over SOURCES.html applied every item under apply-rules.md (no heading renamed; GM rulings, declined alternatives and dated absence labels kept). Two citation mismatches the editors surfaced became absence notes (hinterland fn-4, homesteads fn-87); the bamboo count corrected to the manifest (3 of 15); the glossary's bare `fang` variant removed (it would have defined the six yamen offices as a Tang ward). After: test_record_format 50, test_footnotes 48, test_record 18, test_sources 7, test_page 74 passed; every one of the 412 glossary terms used by a modal or a page
- [x] T05 the checks (FR-005): `.claude/agents/record-format.md`; `tests/interactive/test_record_format.py`; `tests/tools/test_glossary_asset.py`; the map's glossary-used test split
      research: rendering
      verify: DONE. .claude/agents/record-format.md (model: opus); tests/interactive/test_record_format.py 50 passed over all 16 pages (fields, glossary load, asset in sync, every term used, FORBIDDEN_VISIBLE shapes absent, the shapes fire on a planted sentence); tests/tools/test_glossary_asset.py; test_page.py's used-test split (74 passed); test_sources.py's classifier reads comment text (7 passed); test_record.py's Markdown-token scan excludes scripts/fixtures/ (pre-existing red on main, fixed under XIV)
- [x] T06 the guidelines (FR-004): `research/CLAUDE.md` "Written for the reader", `research/README.md`, `interactive/CLAUDE.md`, `tests/CLAUDE.md`, root `CLAUDE.md`
      research: rendering
      verify: DONE. research/CLAUDE.md 'Written for the reader' (the GM's words, the three rules, the two checks); research/README.md entry format (two fields as comments, the rewrite rule); interactive/CLAUDE.md glossary row; tests/CLAUDE.md interactive row; root CLAUDE.md one sentence in the WHAT THE RECORD IS FOR bullet; container-scripts/append-system-prompt.md lists quote-check and record-format
- [x] T07 `make page-check` green, `make done` green (FR-007, SC-004); SC-001 checked in a browser by hand; land GATED
      research: rendering
      verify: DONE. make page-check green (569 interactive tests + 18 browser tests, the record's synthetic page among them); make done green on the second run - 3,100 passed, coverage 100% (22,464 statements), 438 s - after the first run's one red (the new tool's operations-registry row); SC-001 checked in Chromium (sc-001-hover.png: the heading's yashikirin dotted, the definition in the box, no field, no correction note); landing GATED
