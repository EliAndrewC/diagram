# Plan - 209 research entries for the reader

**Spec**: [`spec.md`](spec.md). **Request**: [`request.md`](request.md). **Research**: [`research.md`](research.md).

## Constitution Check

- I (independent review): `spec-fidelity` before implementation; `record-format` (new, Opus) over every swept page; `quote-check` not re-run because no quoted passage changes (spec FR-006) - the footnote tests still hold every footnote's form.
- VI (verification): `make page-check` (the record's assets are interactive assets; one synthetic record page in the existing browser module, never a real page - GM 2026-09-07), `make done` (the delta routes GATED: `glossary.py`, a new tool, new tests).
- X clause 5 (100% coverage): `record_glossary_js()` and `tools/glossary_asset.py` are covered by `tests/tools/test_glossary_asset.py` and `tests/interactive/test_record_format.py`.
- XII (the record): every entry keeps its finding, its footnotes, its labels and its decisions; only the form changes. Nothing physical is researched - every task is `research: rendering`.
- XVI (do the literal thing): the four changes, the guidelines, the sweep, the extended checks - and the one boundary (SOURCES.html, D6) stated to the GM rather than decided silently.

## Approach

1. **The glossary reaches the record as a derived asset** (D1). `glossary.py` gains `record_glossary_js()`; `tools/glossary_asset.py` writes or checks `research/assets/glossary.js`; `make glossary`. `record.js` walks the page's text nodes (skipping code/pre/script/style) and wraps matches in the map's `.gl` span; the definition shows in the footnote box (`#fntip`), placed by the same code. Every record page loads `glossary.js` before `record.js` (both deferred, document order). The glossary grows by ~75 record terms, each defined from the record's text.
2. **The fields become comments by script** (287 fields across 15 pages, two merged paragraphs by hand), then the judgment sweep: one editing agent per page group under a written rulebook (`specs/209/research.md` R2), the `record-format` agent over every page after, findings resolved by the session.
3. **The tests**: `tests/interactive/test_record_format.py` (the mechanical half), `tests/tools/test_glossary_asset.py`, the browser hover test, and the map's glossary-used test split so a record-only term is legal.
4. **The guidelines**: `research/CLAUDE.md` "Written for the reader", `research/README.md` entry format, the glossary row of `interactive/CLAUDE.md`, the `tests/CLAUDE.md` row, one sentence in root `CLAUDE.md`.

## Files

- `l7r/diagram/interactive/glossary.py`, `l7r/diagram/tools/glossary_asset.py`, `Makefile` (`glossary`)
- `research/assets/record.js`, `research/assets/record.css`, `research/assets/glossary.js` (derived), every `research/*.html` and `research/cities/*.html`
- `.claude/agents/record-format.md`
- `tests/interactive/test_record_format.py`, `tests/tools/test_glossary_asset.py`, `tests/interactive/test_page.py`, `tests/full/interactive/page_browser/{conftest,test_synthetic}.py`
- `research/CLAUDE.md`, `research/README.md`, `l7r/diagram/interactive/CLAUDE.md`, `tests/CLAUDE.md`, `CLAUDE.md`
