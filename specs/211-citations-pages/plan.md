# Plan - 211 citations pages

**Spec**: [`spec.md`](spec.md). **Request**: [`request.md`](request.md). **Research**: [`research.md`](research.md).

## Constitution Check

- I (independent review): `spec-fidelity` before implementation; `source-applicability` (new, Opus) over every
  cited source's write-ups, by agents other than the ones that drafted them; `record-format` over the citations
  pages and the registry after the backfill; `quote-check` NOT re-run over the record, because no quoted passage
  changes - every `<li>` moves verbatim and the mechanical footnote tests hold every note's form on its new page.
- VI (verification): `make page-check` (the record's assets and the interactive tests; the synthetic record page
  in the browser module gains the derived-script hover, never a real page - GM 2026-09-07); `make done` (the delta
  routes GATED: `sources.py`, a new tool, new tests, `test_task_research_boxes.py`).
- X clause 5 (100% coverage): `interactive/citations.py` and `tools/citations_asset.py` are covered by
  `tests/tools/test_citations_asset.py` and `tests/interactive/test_citations.py`; the classifier moved from
  `test_sources.py` into `sources.py` keeps its tests.
- XII (the record): every footnote keeps its key, its quote and its label; the record gains, per source, what it is
  and why it applies with its limits; a source found NOT applicable is recorded (spec D5), never hidden. The
  fifth research box is the procedure the GM asked for. Every task here is `research: rendering` (the record's form)
  or `research: procedure` - nothing physical is decided.
- XIV (defects where found): anything the backfill's agents surface about a citation - a wrong key, a footnote
  form the tests miss - is fixed in this feature and recorded in `research.md`.
- XVI (do the literal thing): the directory the GM named, the works list at the top, one write-up per work, the
  check at both moments; the one thing decided rather than asked - HTML as the store - is D1 with its alternatives.

## Approach

1. **The reading code** (`interactive/sources.py` + a new `interactive/citations.py`): `citation_lines`,
   `not_read`, `link_target` move from `test_sources.py` into `sources.py` (one body; the test imports them);
   `registry_entries()` reads each registry entry into its parts (citation line, what-it-is, why-it-applies,
   used-for); `citations.py` reads a citations page's `<li id="fn-n">` notes, derives the page's script
   (`window.RECORD_CITATIONS = {...}`, the back link stripped) and its works section (the cited keys in first-citation
   order, each with its citation line as text, its key link by `link_target`, and its two write-ups), and can
   rewrite the works region between its markers.
2. **The tool and target**: `tools/citations_asset.py` (`make citations`, `CHECK=1`) writes every page's script and
   works region, or reports which are stale; registered in `_invocation.py` as cheap.
3. **The split, by script, once**: for each research page, cut the `<section class="footnotes">`, write the
   citations page (head, heading, back link, works markers, the notes with back links re-pointed), re-point every
   `<sup class="fn">` reference, put the link section in the research page's place, add the script tag. Then
   `make citations`. The script is recorded in `research.md`; it is run once and not kept.
4. **The hover**: `record.js` resolves a reference's note from the page OR from `window.RECORD_CITATIONS`; the
   selector takes `href` ending in `#fn-n` wherever it points. `record.css` unchanged but for the link section.
5. **The write-ups**: 20 batches of 16 keys; one drafting agent per batch under the rulebook
   (`specs/211/research.md` R2), then one `source-applicability` agent per batch; the session applies the checks'
   findings to the drafts and lands them in `SOURCES.html`; `make citations`; `record-format` over the registry and
   the citations pages.
6. **The agent**: `.claude/agents/source-applicability.md`, Opus, `WebFetch, WebSearch, Read`.
7. **The tests**: `test_footnotes.py` reads notes from the citations page; `test_sources.py` scans citations pages
   and imports the classifier from `sources.py`; `test_record.py` and `test_record_format.py` include the
   citations pages; `test_citations.py` (the reader, the derivation, the equality of every committed script and
   works region, every cited key has both write-ups); `test_task_research_boxes.py` gains the fifth box from 211;
   the browser synthetic record page loads a derived script and hovers a note that is not in the page.
8. **The procedure**: `research/CLAUDE.md`, `research/README.md`, root `CLAUDE.md`, the constitution (XII, MINOR),
   `.specify/templates/tasks-template.md`, `container-scripts/append-system-prompt.md`, `interactive/CLAUDE.md`,
   `tests/CLAUDE.md`, `tools/CLAUDE.md`, `quote-check.md`, `record-format.md`, `gate-stamp.py`'s browser key.

## Files

- `l7r/diagram/interactive/sources.py`, `l7r/diagram/interactive/citations.py` (new), `l7r/diagram/tools/citations_asset.py`
  (new), `l7r/diagram/_invocation.py`, `Makefile` (`citations`)
- `research/assets/record.js`, `research/assets/record.css`; every `research/*.html`, `research/cities/*.html`;
  `research/citations/**` (new: 15 pages + 15 derived scripts); `research/SOURCES.html`
- `.claude/agents/source-applicability.md` (new), `quote-check.md`, `record-format.md`
- `tests/interactive/test_footnotes.py`, `test_sources.py`, `test_record.py`, `test_record_format.py`,
  `test_citations.py` (new), `tests/tools/test_citations_asset.py` (new), `tests/test_task_research_boxes.py`,
  `tests/full/interactive/page_browser/{conftest,test_synthetic}.py`
- `scripts/gate-stamp.py`; the procedure documents listed under 8.
