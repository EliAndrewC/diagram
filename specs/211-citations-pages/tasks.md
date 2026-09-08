# Tasks - 211 citations pages

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Every task is `research: rendering` (the record's form) or
`research: procedure` (how sessions work) - nothing physical is decided in this feature.

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code (up to five rounds)
      research: procedure
      verify: DONE. FAITHFUL at round 2 of 5: round 1's one item was SC-004 (it asked for one paragraph in the whole repository while FR-003 derives copies into the pages); restated as one HAND-AUTHORED paragraph plus derived copies between markers. Round 2 FAITHFUL; both rounds' aside for the GM: the registry doubles (D2)
- [x] T02 the reading code (FR-002, FR-003, FR-006): `citation_lines`/`not_read`/`link_target` lifted from `test_sources.py` into `interactive/sources.py`; `registry_entries()`; new `interactive/citations.py` (a citations page's notes, the derived script, the works section, the works region rewrite); `tests/interactive/test_citations.py`
      research: rendering
      verify: DONE. DONE. interactive/citations.py (notes, cited_keys, note_for_script, script_js, works_html, with_works, derive) + sources.py (citation_lines/not_read/link_target moved from test_sources.py - one body; registry_entries()); tests/interactive/test_citations.py 13 cases green on the split record (the derivation cases; the works cases red until T08 lands the write-ups)
- [x] T03 the tool and target: `tools/citations_asset.py`, `make citations` (`CHECK=1`), the `_invocation.py` row, `tests/tools/test_citations_asset.py`
      research: rendering
      verify: DONE. DONE. tools/citations_asset.py, make citations (CHECK=1), the _invocation.py row (cheap), make docs regenerated; tests/tools/test_citations_asset.py 2 passed
- [x] T04 the split, once, by script (FR-001, FR-002): 15 citations pages written, 795 notes moved verbatim, every reference re-pointed, the link section and the script tag in every research page; `record.js` resolves a note from `window.RECORD_CITATIONS`; the script recorded in `research.md`
      research: rendering
      verify: DONE. DONE. specs/211/split.py run once from HEAD (a first run sliced at stale offsets and was restored from git and re-run - recorded in the script): 15 citations pages, 795 notes moved verbatim, 6 notes that reference another note kept in-page, every reference re-pointed, the link section + script tag in every research page; homesteads.html 157,538 -> 101,119 bytes; record.js reads a note from window.RECORD_CITATIONS and wraps the glossary over it; make citations wrote the 15 scripts
- [x] T05 the record tests follow the notes (FR-006): `test_footnotes.py`, `test_sources.py`, `test_record.py`, `test_record_format.py`; `gate-stamp.py`'s browser key covers `research/citations/**`; the browser synthetic record page hovers a note that is only in the derived script
      research: rendering
      verify: DONE. DONE. test_footnotes.py (refs point at the page's own citations page, notes read from it, a note's reference to a note counts, the absence classifier ignores the back link), test_sources.py (scans the 30 pages, imports the classifier from sources.py; 1,000+ links checked), test_record.py (33 passed over 31 pages), test_record_format.py (80 passed; citations pages are record pages, not finding files); gate-stamp.py browser key + research/citations/*.js; the synthetic record page hovers a note only in the derived table (18 browser tests passed)
- [x] T06 the write-ups drafted (FR-003, FR-004): 20 batches of 16 keys, one Opus drafter each under the rulebook (`research.md` R2); drafts collected, house style held
      research: rendering
      verify: DONE. DONE. 20 Opus drafters, one per batch of 16 keys, under specs/211/writeup-rules.md; 319 write-ups, every key with both paragraphs, no dashes; drafts kept in the session scratchpad and landed by specs/211/land_writeups.py
- [x] T07 the `source-applicability` agent (FR-005): `.claude/agents/source-applicability.md` (Opus); run over every batch's drafts by agents other than the drafters; verdicts recorded in `research.md` R3; MISSING limits written in; NOT-APPLICABLE sources listed for the GM (D5)
      research: procedure
      verify: DONE. DONE. .claude/agents/source-applicability.md (Opus, WebFetch/WebSearch/Read); 20 batches checked by Opus agents other than the drafters (dispatched as general-purpose agents told to follow the file - a new agent type is not routed mid-session); 17 reports before the rate limit, 3 after; verdicts in research.md R3; 0 NOT-APPLICABLE sources, 16 partial not-applicable uses, ~160 write-ups revised, 40+ Used-for lines cut to their pages, 15 research sentences relabeled (R4); the GM's list in R5
- [ ] T08 the write-ups landed in `SOURCES.html` (all 319 cited keys), `make citations` (the works sections derived), `record-format` over the registry and the citations pages, findings resolved
      research: rendering
- [ ] T09 the procedure (FR-007): `research/CLAUDE.md`, `research/README.md`, root `CLAUDE.md`, the constitution (XII, MINOR), `tasks-template.md`, `append-system-prompt.md`, `interactive/CLAUDE.md`, `tests/CLAUDE.md`, `tools/CLAUDE.md`, `quote-check.md`, `record-format.md`; the fifth research box in `test_task_research_boxes.py` from feature 211; `docs/review-ledger.md` rows
      research: procedure
- [ ] T10 `make page-check` green, `make done` green (FR-008, SC-005); SC-001 and SC-002 checked in a browser from disk; land GATED
      research: rendering
