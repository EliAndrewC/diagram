# Tasks - 211 citations pages

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Every task is `research: rendering` (the record's form) or
`research: procedure` (how sessions work) - nothing physical is decided in this feature.

- [ ] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code (up to five rounds)
      research: procedure
- [ ] T02 the reading code (FR-002, FR-003, FR-006): `citation_lines`/`not_read`/`link_target` lifted from `test_sources.py` into `interactive/sources.py`; `registry_entries()`; new `interactive/citations.py` (a citations page's notes, the derived script, the works section, the works region rewrite); `tests/interactive/test_citations.py`
      research: rendering
- [ ] T03 the tool and target: `tools/citations_asset.py`, `make citations` (`CHECK=1`), the `_invocation.py` row, `tests/tools/test_citations_asset.py`
      research: rendering
- [ ] T04 the split, once, by script (FR-001, FR-002): 15 citations pages written, 795 notes moved verbatim, every reference re-pointed, the link section and the script tag in every research page; `record.js` resolves a note from `window.RECORD_CITATIONS`; the script recorded in `research.md`
      research: rendering
- [ ] T05 the record tests follow the notes (FR-006): `test_footnotes.py`, `test_sources.py`, `test_record.py`, `test_record_format.py`; `gate-stamp.py`'s browser key covers `research/citations/**`; the browser synthetic record page hovers a note that is only in the derived script
      research: rendering
- [ ] T06 the write-ups drafted (FR-003, FR-004): 20 batches of 16 keys, one Opus drafter each under the rulebook (`research.md` R2); drafts collected, house style held
      research: rendering
- [ ] T07 the `source-applicability` agent (FR-005): `.claude/agents/source-applicability.md` (Opus); run over every batch's drafts by agents other than the drafters; verdicts recorded in `research.md` R3; MISSING limits written in; NOT-APPLICABLE sources listed for the GM (D5)
      research: procedure
- [ ] T08 the write-ups landed in `SOURCES.html` (all 319 cited keys), `make citations` (the works sections derived), `record-format` over the registry and the citations pages, findings resolved
      research: rendering
- [ ] T09 the procedure (FR-007): `research/CLAUDE.md`, `research/README.md`, root `CLAUDE.md`, the constitution (XII, MINOR), `tasks-template.md`, `append-system-prompt.md`, `interactive/CLAUDE.md`, `tests/CLAUDE.md`, `tools/CLAUDE.md`, `quote-check.md`, `record-format.md`; the fifth research box in `test_task_research_boxes.py` from feature 211; `docs/review-ledger.md` rows
      research: procedure
- [ ] T10 `make page-check` green, `make done` green (FR-008, SC-005); SC-001 and SC-002 checked in a browser from disk; land GATED
      research: rendering
