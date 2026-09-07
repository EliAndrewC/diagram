# Feature 211 - citations pages

**Status**: Draft - awaiting `spec-fidelity` (constitution XVI).
**Request**: [`request.md`](request.md) - the GM's words verbatim.
**Predecessors**: feature 194 (a citation is a footnote that quotes; the record is hand-authored HTML with the
ACOUP hover); 195 (cite only what can be read; the absence note); 190 (every key is a link, the target decided by the
registry's citation line); 209 (the record is written for its reader; one glossary, derived to the record as a
committed asset that a test holds in sync - the DRY-by-derivation pattern this feature reuses); the registry
`research/SOURCES.html` (constitution v2.10.0/v2.13.0: every key, what it was used for, where it can be read).

## Summary

The footnotes are 35 to 65 percent of every research page's bytes (`research/homesteads.html`: 157.5 KB, of which
58.9 KB is its 88 footnotes; `cities/capitals.html`: 190.9 KB, 64.9 KB) and the GM expects them to grow - longer
quotations, explanatory text around them. This feature (1) moves every page's footnotes into a CITATIONS PAGE,
`research/citations/<name>.html` beside `research/<name>.html`, without duplicating their content - the research
page's hover still shows the footnote's text, loaded from the citations page's content rather than re-typed; (2) puts
at the top of each citations page a list of the works its footnotes cite - for each, what it is (name, authors, one to
three sentences on what the work is) and why we consider it a good and valid source for what we look up in it, with
its honest limitations - written ONCE per work in a shared store, never once per page; (3) adds a subagent check that
judges whether a source is applicable to a premodern East Asian setting, runs it over every source the record cites
as their write-ups are added, and makes it a step of the procedure BEFORE a new source's numbers, claims or details
are integrated into the maps.

The pages in scope are the fifteen research pages (`research/*.html` less `SOURCES.html`, and `research/cities/*.html`;
795 footnotes citing 319 distinct registry keys as of 2026-09-07), the registry `SOURCES.html`, the record's assets,
the tooling and tests that read the record, and the procedure documents.

## Functional requirements

- **FR-001 A citations page beside every research page.** For every research page `research/<name>.html` there is
  `research/citations/<name>.html` (`research/citations/cities/<name>.html` for a `cities/` page), hand-authored HTML
  like the rest of the record (feature 194's ruling: the record IS HTML, edited as a page), loading the same
  stylesheet, glossary and script. Its body is: a heading naming the page it serves and a link back to it; the WORKS
  section of FR-003; then the page's footnotes, `<section class="footnotes"><ol><li id="fn-n">...</li>` - every
  `<li>` moved verbatim from the research page (its key link, its quoted passage, its gloss, its comments; an
  absence note unchanged), keeping its number and its id, its back link re-pointed at the research page
  (`../<name>.html#fnref-n`). A footnote may hold several paragraphs: the `<li>` form admits `<p>` children, so a
  quotation can be lengthened or explanatory text added around it without changing the form.
- **FR-002 The research page keeps its references and its hover, and loses the notes' bytes.** In every research
  page each `<sup class="fn">` reference now links to its note on the citations page
  (`href="citations/<name>.html#fn-n"`; `../citations/cities/<name>.html#fn-n` from `cities/`); the
  `<section class="footnotes">` is replaced by a short section linking to the citations page. Hovering a reference
  shows the SAME note as before - the footnote's content, key link and quote - which the page reads from a DERIVED
  asset, `research/citations/<name>.js` (`citations/cities/<name>.js`), written from the citations page by a make
  target (`make citations`) and committed; a test proves each committed asset equals its derivation, so the note's
  text exists in exactly ONE hand-authored place and the asset can never disagree with it. Why an asset and not a
  fetch: the pages are opened from disk (`file://`), where a browser refuses a script's fetch of a sibling file and
  a same-origin read of an iframe; a `<script src>` is the one thing that loads (D1 prices the alternatives). No
  content is typed twice, which is the GM's DRY requirement: *"we should be careful to avoid duplicating content"*.
- **FR-003 The works cited, at the top of each citations page.** Before its footnotes, each citations page lists
  every work its footnotes cite, in order of first citation, and for each: the work's name, its authors and where
  it can be read (the registry's citation line, the key linked as feature 190 links it); **what it is** - one to
  three sentences on what the work is; and **why it applies, and its limits** - one to three sentences on why we
  consider it a good and valid source for what we use it to look up, INCLUDING its honest limitations in the GM's
  sense: the era (a 1900 survey is modern, its land largely pre-industrial, its techniques partly not - say so),
  the place (a Korean source stands in for a Chinese or Japanese one we could not find, and says so), the kind
  (an encyclopedia article, a tourist board's page, a modern measurement, a statute). These two write-ups are
  written ONCE per work, in the registry entry for its key (`SOURCES.html`, two new paragraphs after the citation
  line: `<p><em>What it is:</em> ...</p>` and `<p><em>Why it applies, and its limits:</em> ...</p>`), and the works
  section of every citations page is DERIVED from the registry by the same make target, between markers that say
  so, for the keys that page's footnotes cite; a test proves each page's works section equals its derivation and
  that every cited key's entry carries both write-ups. So a work cited by `homesteads.html` and `fields.html` has
  ONE write-up, in one file, shown on both citations pages - *"we do not want to have multiple different write ups
  of a single paper"*. A key with no write-up is a gate failure, so a new source cannot be cited without one.
- **FR-004 The write-ups are written for the reader, and every one is checked.** Every cited key (319 today, the
  GM's own campaign notes among them, as canon) gets both write-ups in this feature, from the registry entry and
  the work itself, in the reader-facing form of feature 209 (a term the reader would not know is a glossary
  tooltip; nothing addressed to a session outside a comment; no history of the document). Each write-up is then
  checked by the agent of FR-005 - *"We can run this subagent check on each of our sources as we add them"* - and its
  findings resolved before the feature lands: a limit the check names that the write-up omits is added; a source the
  check finds NOT applicable is recorded as such in its write-up and in this feature's `research.md`, with the
  entries that rest on it, for the GM (the assertions stand, honestly labeled; re-sourcing a rule is a research
  pass of its own).
- **FR-005 The source-applicability check.** A new check agent, `.claude/agents/source-applicability.md` (Opus,
  like every check agent - GM 2026-09-07), given one or more sources - a registry key with its entry and write-ups,
  or a NEW source not yet registered: its citation, its URL and the claim or number it is about to support - reads
  the work (one attempt per host, as `quote-check` does) and reports, per source: WHAT it is (kind, authors, date,
  place, method - and whether the write-up describes it accurately); its ERA and PLACE against the setting's basis
  (imperial China and pre-Meiji Japan; Korea and the wider region as analogs); a verdict - APPLICABLE,
  APPLICABLE-WITH-LIMITS (each limit named: a modern technique, a post-industrial number, a different region, a
  tertiary source, a figure from a different scale of place), or NOT-APPLICABLE (why: twenty-first-century
  forestry yields, a mechanized farm, a source about something else) - and whether the write-up's stated limits are
  HONEST, MISSING one (which), or OVERSTATED. Judgment about the source, never about the map or the rule; it never
  edits. It is run (a) whenever a source's write-up is added or changed - this feature's backfill and every new key
  from here - and (b) BEFORE a session integrates a new source's numbers, claims or details into a map or a rule:
  a `research: physical` task carries a FIFTH box, `source-applicability confirmed`, beside the four (constitution
  XII, `tests/test_task_research_boxes.py`: binds on tasks from feature 211 on, older task files are history),
  so the check is a shape the gate refuses to skip, not a memory - *"that subagent check should also be run when we
  first begin to make use of the source prior to integrating its numbers or claims or details into our maps."*
- **FR-006 The checks that read the record follow the notes.** Every test and agent that reads footnotes reads
  them from the citations page: `tests/interactive/test_footnotes.py` (every reference on a research page resolves
  to a note on its citations page and every note is referenced; every note's form; every roster key quoted in its
  section; the translation-note rule over the citations pages), `test_sources.py` (a key in a citations page is a
  link to the right target; the works section's key links too), `test_record.py` (every link in a citations page
  resolves - the file, the id), `test_record_format.py` (a citations page is a record page: it loads the glossary,
  its visible text carries no session note and no history, its terms count as used). The `quote-check` agent takes
  the citations page as where the notes are; `record-format` takes a citations page as a page in scope. The
  `browser` gate key (`scripts/gate-stamp.py`) covers `research/citations/**` as it covers `research/*.html`. The
  code that decides where a key links (`link_target`, `not_read`, `citation_lines` in `test_sources.py`) moves
  into `interactive/sources.py`, because the make target needs it and a tool under `l7r/` does not import from
  `tests/`; the test imports it from there - still one body.
- **FR-007 The procedure.** `research/CLAUDE.md` gains a section carrying the GM's words: where the notes live and
  how a new footnote is added (the `<li>` on the citations page, the reference on the research page,
  `make citations`); what a registry entry carries from here (the two write-ups, checked); and the
  source-applicability step at both moments. `research/README.md`'s entry format and "Citing" say the same in
  the format's terms; root `CLAUDE.md`'s research bullet and its task-checkbox bullet name the agent and the fifth
  box; the constitution's Principle XII gains the step (a new obligation - a MINOR bump); the
  `.specify/templates/tasks-template.md` box list gains the box; `container-scripts/append-system-prompt.md`
  authorizes the new agent beside `quote-check` and `record-format`; `interactive/CLAUDE.md`'s `sources.py` row and
  `tests/CLAUDE.md`'s interactive row describe the new reading.
- **FR-008 Verification.** `make page-check` green (the assets and the interactive tests); `make done` green (the
  `sources.py` change, the new tool and the new tests route the delta GATED); every research page opened in a
  browser from disk shows a footnote's note on hover exactly as before, and its citations page shows the works
  and the notes; the house style holds over every edited page, quoted spans left as their sources wrote them.

## Success criteria

- **SC-001** `research/homesteads.html` is at most 100 KB, and every research page has lost at least the bytes of
  its footnote section; `research/citations/homesteads.html` exists, opens from disk, and lists its works before
  its 88 notes.
- **SC-002** Hovering footnote 1 on `research/homesteads.html` opened from disk shows the Kashima survey's quote,
  as before the split; clicking it lands on `citations/homesteads.html#fn-1`, whose back link returns.
- **SC-003** Every one of the 319 cited keys has both write-ups in `SOURCES.html`; the `source-applicability`
  agent's verdict on each is recorded in this feature's `research.md`, and no MISSING limit is left unwritten.
- **SC-004** `grep -c 'wang-ochiai-2022'` finds ONE `What it is:` paragraph for it in the whole repository - in
  the registry - while both `citations/homesteads.html` and `citations/fields.html` show it (derived); a change to
  the registry paragraph followed by `make citations` changes both pages.
- **SC-005** `make page-check` and `make done` green; the derivation is exercised by the tests that compare it.

## Decisions Recorded

- **D1 - the citations page is the hand-authored store; the research page loads a derived script.** The GM
  offered JSON, YAML, Markdown or "another HTML file, which has its own IDs that can be parsed and extracted", and
  asked for multi-paragraph, well-formatted text. HTML is that format, it is what the record already is (feature
  194: generation of the record was refused by its review; the page is edited by hand), and every check the
  record has - the footnote tests, the house-style guard's exemption for quoted spans, `quote-check`,
  `record-format`, the glossary wrap - already reads it. Priced and declined: a YAML or JSON store with BOTH pages
  derived from it (JSON has no multi-line strings, the GM's own objection; YAML block scalars holding HTML add a
  format every check must learn, and the page a reader opens would be generated, which 194's review refused);
  Markdown (deleted by 194, and `test_record.py` fails any pointer to it); a runtime fetch of the citations page
  (refused by browsers on `file://`); a hidden iframe (same); keeping the notes in the research page hidden (does
  not shorten the page, which is the request). The derived `citations/<name>.js` is the glossary pattern of feature
  209: committed, pinned by a test, never edited - the DRY principle is kept by derivation, exactly as
  `research/assets/glossary.js` keeps it.
- **D2 - the write-ups live in the registry, one per key.** The registry is already the single store keyed by
  source, read by the tests and the map, and the GM asked that a work cited from two pages be *"drawing from a
  single data source"*. Two fields per entry, in the entry's own form (a labeled paragraph, like `Used for:`), so
  the registry's parser and the reader's page both find them. The works section of a citations page is derived
  from those fields between markers, not rendered by script, so a reader without JavaScript sees it, the
  record-format test reads it as visible text, and the glossary wraps it. Priced and declined: one file per work
  under `research/sources/` (319 files, and every link in the record re-pointed); a script-rendered works list from
  a derived `sources.js` (invisible to the visible-text tests and to a reader with scripts off). The cost accepted:
  `SOURCES.html` grows by roughly two short paragraphs per cited key - about 200 KB on 206 KB. Splitting the
  registry is a separate question and the GM's; it is stated here, not decided.
- **D3 - the write-ups are drafted by agents and checked by different agents.** 319 works is a backfill no
  session can write in its own context; the drafting is fanned out to Opus agents given the registry entries
  verbatim and told to read the work when the entry does not say what it is; the applicability check is a
  DIFFERENT agent over the same keys (author is not reviewer, constitution I). The fan-out is the GM's own request
  here (*"run this subagent check on each of our sources"*, *"work the entire feature from start to finish"*).
- **D4 - the check has two moments, and the second is a checkbox.** The GM asked for the check when a source is
  added and *"when we first begin to make use of the source prior to integrating its numbers"*; the project's answer
  to "remember to do X" is a shape a test refuses (constitution v2.12.0: the research boxes), so the second moment
  is the fifth box on a physical task. The agent's name says what it decides: `source-applicability`.
- **D5 - a NOT-APPLICABLE verdict on an existing source is recorded, not silently acted on.** The GM: *"hopefully,
  this will not result in any issues being uncovered."* If it does, the honest state of the record is the write-up
  saying so and the assertions that rest on the source labeled as resting on a source of limited applicability;
  replacing the source is a research pass under the physical-task procedure, listed for the GM in this feature's
  `research.md` (constitution XIV's carve-out for work that is a pass of its own, with the measurement stated).
- **D6 - numbering stays per page.** Notes keep the numbers they have (`fn-1`... per research page), so no
  reference changes its text and no anchor a reader may have bookmarked moves; a citations page's ids are its
  research page's.
- **D7 - the works are ordered by first citation.** The reader arrives from a footnote; the list follows the
  page's own order rather than the alphabet of keys a reader never sees. The key stays the link text (feature 190).
