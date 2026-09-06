# Feature 191 - references that QUOTE their sources, checked, and the research record as HTML

**Status**: FAITHFUL (`spec-fidelity`, round 5 of 5, 2026-09-06) - cleared for implementation (constitution XVI). Round 4 returned FR-013 a third
time - the absolute literal inside the record, over-sweeping of same-basename files outside it, a wrong hand
count - and offered one formulation, a resolution rule with a three-part test; FR-013 is now that rule verbatim
in substance, with no census in the spec. Round 3 returned one item, fixed: FR-013's
search space excluded the record's own RELATIVE links (90, invisible to a literal grep) and its test was a
literal-absence check - now the relative forms are in the space and the test is a resolution check over every link
in every page. Round 2 returned two items, both fixed:
FR-001 stated the citation form in Markdown, which FR-009 deletes (now the HTML form, with T01 after T04); FR-013
omitted the 78 engine-code pointers and ~208 doc pointers (now a stated search space, every literal updated, a
test that none remains). Round 1 returned NOT FAITHFUL on five
items and REFUSED the exception this spec had put to it (generate the HTML from Markdown that stays): the GM's
*"the markdown on GitHub will no longer exist as it has been replaced with HTML"* is the post-condition, stated by
the GM and used as the premise for the local links, and hand-authored HTML delivers every capability asked for.
So the record CONVERTS (Part 3 rewritten); the file surface is 15 record files plus the registry, not "18";
`quote-check confirmed` is ADDED beside `source-reader confirmed`, not swapped for it; the class entries and
`_ENTRY_FILE` move to `.html` with an existence test; a footnote may carry more than one passage.
**Request**: [`request.md`](request.md) - the GM's words verbatim (2026-09-06, three parts)
**Predecessors**: 143 (read what you cite; `SOURCES.md` keys with URLs), 180 (the modal's references are the
research QUESTIONS, linked to GitHub), 190 (every reference is a link)

## Summary

Today a research section ends in a `**Sources:**` line of keys, and the registry entry says what a source was
used for - sometimes with a quote, mostly not. The GM wants the QUOTE to be the citation: *"in our references
section, we quote the passage or passages from the reference which support the assertion that we are making.
There is no point in including a reference if it is not being quoted"* - one footnote per assertion, *"even if this
means multiple footnote links per paragraph or even multiple per sentence"*, a subagent that checks the quote is
verbatim AND supports the assertion AND that every relevant assertion carries a footnote, the whole existing record
backfilled, and the record rendered as HTML with hover footnotes (the ACOUP form), the maps linking to it locally.

## Part 1 - the rule, and the check (FR-001 to FR-005)

- **FR-001 The form of a citation is a FOOTNOTE that quotes - in the record's own format, HTML (FR-009).** An
  assertion in a research page is followed by a footnote reference, `<sup class="fn"><a id="fnref-n" href="#fn-n">n</a></sup>`
  (numbered per page), and the footnote in the page's foot, `<section class="footnotes"><ol><li id="fn-n">`,
  carries: the registry key as a link (feature 190's rule decides the target), the QUOTED PASSAGE - or PASSAGES,
  when more than one is needed to support the assertion (the GM: *"the passage or passages"*) - verbatim in the
  source's language (a gloss in English after each when the passage is not English), one clause on what it
  supports when that is not plain, and a return link `<a class="fnback" href="#fnref-n">`. A sentence that makes
  two assertions from two sources carries two footnotes. Example, in a page:
  `Chickens roosted in a coop in Han China<sup class="fn"><a id="fnref-7" href="#fn-7">7</a></sup>, and in Japan
  the chicken was a timekeeper, not a coop bird<sup class="fn"><a id="fnref-8" href="#fn-8">8</a></sup>.` with
  `<li id="fn-7"><a href="https://zh.wikisource.org/..."><code>qimin-yaoshu-yangji</code></a> - 「雞棲，宜據地為籠，
  籠內著棧」 (the coop is a cage set on the ground with perches inside) <a class="fnback" href="#fnref-7">back</a></li>`.
  The `<p><strong>Sources:</strong> ...</p>` roster stays as the section's key list - the modal reads it - and
  every key on it MUST be quoted by at least one footnote in that section (*"no point in including a reference
  if it is not being quoted"*); a key with nothing to quote leaves the roster. The exemplar (T01) is authored in
  HTML AFTER the conversion (T04), and the doctrine text (T03) states this HTML form - the rule going forward is a
  rule about the pages.
- **FR-002 A source that could not be read quotes what WAS seen.** A SUMMARY-ONLY entry's footnote quotes the
  search summary it was recorded from, labeled `SUMMARY-ONLY` in the footnote, so the reader sees exactly what the
  claim rests on; a `URL: none` source (the GM's own notes) quotes the note. Nothing is quoted from memory.
- **FR-003 The subagent check.** A new agent, `quote-check` (`.claude/agents/quote-check.md`, Sonnet like
  `source-reader` - verification, not judgment), takes a research file or section and returns, per footnote:
  VERBATIM / DIFFERS (with the page's actual text) / NOT-ON-PAGE for the quote; SUPPORTS / PARTIAL / DOES-NOT-SUPPORT
  for the assertion the footnote is attached to; and, per section, the assertions it finds WITHOUT a footnote (the
  GM: *"every relevant assertion has a footnote link"*). One fetch per host; background; stall-watched like the
  reader. The doctrine: every new or changed research entry is checked by it before its feature lands, and the
  result is recorded in the feature's tasks: a `research: physical` task gains a FOURTH box, `quote-check confirmed`,
  beside `source-reader confirmed` - the GM's words are *"both ... and also ... and"*, an addition on top of the
  check they say is already in place, so nothing is retired (`tests/test_task_research_boxes.py` learns the
  fourth box).
- **FR-004 The mechanical half is a TEST.** `tests/interactive/test_footnotes.py`: every footnote reference resolves
  to a definition and every definition is referenced; every definition carries a registry key and at least one quotation
  (quotation marks or 「」, at least 12 characters; several passages from the same source may follow one another); every key on a section's Sources
  roster is quoted by a footnote in that section; footnote numbers are unique per file. The judgment half
  (verbatim, supports, complete) is FR-003's agent - a test cannot read a page.
- **FR-005 The rule is written where the record is written**: `research/CLAUDE.md` (the form, the check, the
  test), `research/README.md`'s template is the GM's to update (reported), root `CLAUDE.md`'s research bullet, and
  the constitution's Principle XII gains the clause (v2.17.0): a source is cited by QUOTING the passage that
  supports the assertion, and the quote is checked.

## Part 2 - the backfill (FR-006 to FR-008)

- **FR-006 Every existing section is backfilled.** For each of the 183 sections in the 15 RECORD files - the 9 top-level and 6 `cities/` files that carry findings;
  `SOURCES.md` is the registry, `README.md` and `CLAUDE.md` are instruction files with no assertion to footnote
  (feature 190 FR-004 states the same surface): each assertion
  that rests on a source gets a footnote quoting that source; the quotes come from the page (the `source-reader` /
  `quote-check` agents fetch it), never from memory; a registry entry that already carries the verbatim passage
  (many do - `READ: 「...」`) supplies it directly and the agent confirms it. Scale, measured: 15 files, 183 sections,
  365 registry entries, 459 keyed citation sites, 202 prose-named ones (feature 190).
- **FR-007 The backfill runs as a batch of background agents, one per RECORD file (15)**, each writing footnotes for its file
  and reporting what it could not quote; then `quote-check` runs over every file and its findings are fixed
  (DIFFERS -> the page's text; DOES-NOT-SUPPORT -> a better passage or the assertion re-labeled; a missing
  footnote -> added). The residue - sources that no longer resolve, pages that refuse the fetch - is recorded per
  footnote as FR-002 says, and listed in T-tasks with what was tried.
- **FR-008 What the backfill does NOT change:** no finding's meaning; no label; no rule file. It adds footnotes and
  moves quotes; where a source turns out not to support the assertion it was cited for, that is a CONTRADICTED
  finding and is reported to the GM in the answer, the text left as it is unless the fix is a plain error of
  fact (feature 190's precedent: the year 1697).

## Part 3 - the record CONVERTS to HTML (FR-009 to FR-014)

- **FR-009 The record files convert in place, and the Markdown is deleted.** The 15 record files and the registry
  become tracked, hand-authored HTML at the same paths with the `.html` extension - `research/water.html`,
  `research/cities/fabric.html`, `research/SOURCES.html` - and `research/water.md` etc. are removed in the same
  commit (`git mv` plus the conversion, so history follows the file). From then on a research edit is an HTML
  edit. `research/CLAUDE.md` and `research/README.md` are NOT converted: they are instruction files, not
  reference sections, and the README is the GM's (constitution XVII) - its link table now names files that moved,
  which is reported to the GM. The one-time conversion is scripted (python-markdown as a throwaway tool in the
  scratchpad, never a dependency of the engine), and its output is checked before commit: every heading, table,
  list, link, quote and SOURCE block of the Markdown present in the page, and the page readable and editable as
  text - one block element per line group, the source's line wraps kept inside paragraphs so diffs stay small.
- **FR-010 Section ids keep exactly the strings `github_anchor` computes today**, so every pointer that landed on
  GitHub lands on the page: `<h2 id="...">`; the function stays as THE id rule for the record, renamed in its
  docstring from "GitHub's anchor" to "the record's anchor (GitHub's rule, kept when the record converted)".
  Registry entries are `<h3 id="<key>"><code>key</code></h3>`, so feature 190's `SOURCES.md#key` links become
  `SOURCES.html#key` and still resolve.
- **FR-011 Footnotes, and the hover.** In a page: `<sup class="fn"><a id="fnref-n" href="#fn-n">n</a></sup>` after
  the assertion; at the foot `<section class="footnotes"><ol><li id="fn-n">` with the key link, the quoted
  passage(s), the gloss and a return link `<a class="fnback" href="#fnref-n">`. One shared stylesheet and one
  shared script, `research/assets/record.css` and `research/assets/record.js`, referenced relatively from every
  page (`cities/` pages with `../`), so a `file://` page is self-contained and a fix to the hover is one edit:
  moving the mouse over a reference shows the footnote beside it (ACOUP's form), clicking jumps to it, Escape
  and moving away dismiss it, the box stays inside the viewport. A page's `<head>` carries the charset, the
  title (the file's H1) and the two links; nothing else is required of an author.
- **FR-012 The maps link locally, and the code reads HTML.** `sources.py` parses the pages: headings and their
  ids, the `Sources:` rosters (`<p><strong>Sources:</strong> ...`) and the `<code>key</code>` tokens in them, the
  section bodies; `_ENTRY_FILE` and every class's `entry` string name `research/<file>.html`;
  `research_questions()` returns a path RELATIVE to the map's own page - `../../../research/homesteads.html#anchor`
  from `pool/<tier>/<name>/<name>.html` (every map and every legacy exhibit sits three levels under the skill
  root) - and the references modal opens it in a new tab as before. `RESEARCH_URL` (GitHub) is retired. A test
  proves every class entry's file and every anchor a pool map emits exist on disk (feature 180 FR-012a's silent
  miss, held for the new surface).
- **FR-013 Everything that names the record moves to the HTML surface - by a RESOLUTION RULE, not a list of
  shapes.** The space: every `.md` token in every tracked file outside `specs/` and outside the GM's
  `research/README.md`, links and prose alike, that RESOLVES - against the containing file's own directory, or
  as a skill-root or repository-root path - to one of the 16 converted files. A token that resolves anywhere
  else (`../settlements/water.md`, `../buildings.md` - the skill's `buildings.md`, not the record's -
  `budgets.md`, `l7r.md`) is OUT and must be byte-identical after the sweep. The sweep is scripted on that rule,
  and its count is recorded in T05 (no hand census in this spec: rounds 2, 3 and 4 each found a hand-listed
  shape short by one - the absolute literal, the record's relative links, the absolute literal INSIDE the
  record and the prose tokens of `research/CLAUDE.md`). The test, three halves: (a) every link target in every
  converted page resolves to a file that exists on disk, and where it names an id that id exists in that page;
  (b) NO `.md` token anywhere outside `specs/` and `research/README.md` resolves to a converted file - prose,
  inline code, `research/CLAUDE.md` and the record's own pages included; (c) every `.md` link target in every
  converted page and in `research/CLAUDE.md` still exists on disk - what fails if the sweep touches a
  `settlements/` or `buildings.md` pointer. Also moving: the house-style and SOURCE-block guards (they act on
  edited text; the `.html` paths are checked to be in their scope), feature 190's link test (every
  `<code>key</code>` in a page inside an `<a>` with the right target), the Sources-roster tests, the browser
  test (opens one research page and hovers one footnote), and 100% coverage as everything else.
- **FR-014 Documentation**: `interactive/CLAUDE.md` (the page chain ends at a local page), `research/CLAUDE.md`
  (the record is HTML; the footnote form; the hover assets), `dev/` where render-sync was described as the
  pages' source (nothing generates them now).

## Decisions Recorded

- **D1 - footnotes, not inline quotes.** The GM named footnotes and the ACOUP hover; a quote inline after every
  assertion would double the record's length on the page and bury the argument.
- **D2 - the record converts; generation was REFUSED.** Round 1 ruled the generate-from-Markdown proposal an
  illegitimate exception: the GM stated the post-condition (*"the markdown on GitHub will no longer exist"*) and
  built the local links on it, and hand-authored HTML loses no capability asked for. Recorded so the question is
  not reopened. Cost accepted with it: GitHub shows a committed `.html` as source, so the public GitHub view of
  the record stops being browsable prose - the reading path feature 180 built; the maps link locally instead.
  Reported to the GM in the answer.
- **D3 - the Sources roster stays and is bound to the footnotes.** The modal reads keys per section from it; the
  footnotes are where the quotes live; FR-004 binds the two (every roster key quoted). Declined: deriving the
  roster from the footnotes (the modal's parser and 190's test both read the roster; two consumers would change
  for nothing the reader sees).
- **D4 - numbering per FILE** (`fn-1` ...): a footnote is one id in one page, and a new one takes the next number.
- **D5 - the backfill is per file, in parallel, and checked by a second agent.** The writer agent and the checker
  are different runs so the check is independent (constitution I's author-is-not-reviewer rule).
