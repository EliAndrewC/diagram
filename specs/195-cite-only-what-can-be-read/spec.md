# Feature 195 - cite only what can be read

**Request**: [`request.md`](request.md), the GM's words verbatim (2026-09-06). **Status**: IMPLEMENTED 2026-09-06 (tasks.md); spec-fidelity round 1 returned three changes (census by derivation over all footnotes, no label exception, carve-out by key + reported), applied; round 2 FAITHFUL (three asides applied: 780 footnotes, CITATION footnote in US1, A1 covers `budgets.md` too).

## Summary

A citation in this repository has two halves that must BOTH hold, or the source is not cited at all: a quoted passage
that actually backs the assertion, and a link to a page on the public internet where that passage can be read. The
GM: *"even if a given source is 'known' to support a point we are making, if we are not able to simultaneously quote a
relevant passage with a quote which actually backs up our assertion and then link to a page on the public internet
where that quote can be read, then we should NOT be claiming that the source supports us."* Three things follow:

1. **The guideline** says so, everywhere the citation rule is stated (constitution XII, root `CLAUDE.md`,
   `research/CLAUDE.md`), and it SUPERSEDES the 2026-08-27 clause that let a claim taken from a summary of an
   unread source be *"still asserted and cited, labeled SUMMARY-ONLY"*. A summary is not a page where the quote can
   be read. A SUMMARY-ONLY registry entry remains a record of what was searched; it is never a citation.
2. **The subagent checks** enforce it: `quote-check` tests READABILITY as well as accuracy and support - the footnote's
   own link must be a public page on which the fetch finds the quoted passage - and returns a verdict that says the
   footnote cannot stand when it is not; `source-reader`'s `SUMMARY-ONLY` verdict means "not citable", not "cite
   with a label".
3. **The existing record is brought under the rule**: every footnote that today links to something other than a public
   page carrying its quote is worked - re-pointed to a public page where the passage can be read and verified there,
   or removed and replaced by an honest note that no readable source was found - so the record makes no claim of
   support it cannot show.

## User Scenarios & Testing

### User Story 1 - a reader clicks a footnote and can read the quote (P1)

A player hovers a footnote on a research page, reads the quoted passage, clicks the key, and lands on a public page
where that passage is. Never on a registry entry that says the page could not be fetched, a paywalled abstract, a
library landing page with no text, or a page in another language that does not contain the quoted words.

**Acceptance**: for every CITATION footnote in `research/**/*.html`, the link target is an `http(s)` URL (not
`SOURCES.html#...`), and an agent fetching that URL finds the quoted passage on it. The one carve-out is A1 below.

### User Story 2 - a session adding a citation cannot cite what it cannot show (P1)

A future session finds a source it "knows" supports a point but can only reach a summary, an abstract or a snippet.
The guideline tells it not to cite; if it does, `quote-check` returns the footnote as not citable and the entry does
not land with it. The assertion may still stand, marked as resting on nothing readable.

**Acceptance**: the rule is stated in the three guideline files and both agent definitions; a `research: physical`
task's `quote-check confirmed` box means readability was checked too.

### User Story 3 - the record is honest about what it lost (P2)

Where a citation is removed, the reader is not silently left with a bare assertion that reads like a finding. The
footnote marker stays and its footnote becomes an ABSENCE NOTE: no key, no link, the words "no publicly readable
source" and what was searched and when. Constitution XII: an unlabeled guess is the one failure.

### Edge Cases

- A quote that is on a PDF the publisher serves publicly (a J-STAGE `_pdf` link, a PMC article) IS readable; the link
  points at the PDF or article page on which the passage appears, not at an abstract page that does not carry it.
- A book on archive.org: the `details/` landing page carries no text; the full-text view (`stream/.../_djvu.txt` or
  the page reader) does, if the passage is found there - then the footnote links to that.
- A page in Japanese or Chinese quoted in English translation: the footnote quotes the ORIGINAL passage (the existing
  form: 「original」 with an English gloss), and the link is the page carrying that original. An English sentence that
  is on no page is not a quote.
- The GM's own notes (`l7r.md`, `URL: none`) - see A1.
- A source read once by a session but whose page has since gone away: not readable now, so not citable now; the
  footnote becomes an absence note that says the URL no longer resolves.
- Two footnotes quoting the same unreadable source in one section: both go; the key leaves the section's Sources
  roster when no footnote in the section quotes it (the roster rule from feature 194 already requires that).

## Requirements

### Functional Requirements

- **FR-001 (the rule)**: constitution Principle XII gains **CITE ONLY WHAT CAN BE READ** (v2.19.0, the GM's words
  verbatim): a citation carries a passage that backs the assertion AND a link to a public page where that passage
  can be read, or the source is not cited. The sentence in QUOTE WHAT YOU CITE reading *"a source that could not be
  read quotes the summary it was recorded from and says so"* is struck; the 2026-08-27 READ WHAT YOU CITE clause's
  "asserted and cited, labeled SUMMARY-ONLY" is struck and replaced by: the claim may be asserted, labeled as resting
  on no readable source, and never cited. Root `CLAUDE.md` (the research-driven-rule bullet) and
  `research/CLAUDE.md` ("A reference QUOTES..." and "Every reference is a link") say the same.
- **FR-002 (footnote forms)**: a footnote is one of exactly two forms. CITATION: `<a href="https://...">
  <code>key</code></a> - 「passage」 (gloss)`, the link an `http(s)` URL on which the passage can be read. ABSENCE:
  no key and no link - `no publicly readable source (searched YYYY-MM-DD: what was searched)`. A footnote linking
  to `SOURCES.html#` is neither, with ONE carve-out named by KEY: the GM's own campaign notes - `l7r-median-domain`
  and any key whose registry entry cites `l7r.md` or `budgets.md`, the GM's own notes (A1). No other unreadable entry is carved out: not a `URL: none`
  print-only book, not a page that has gone away, not a paywalled full text, not a SUMMARY-ONLY entry - each of those
  becomes an absence note. `tests/interactive/test_footnotes.py` enforces the two forms and the by-key carve-out;
  `tests/interactive/test_sources.py`'s classifier no longer sends a footnote to the registry for an unread source -
  a key whose entry is SUMMARY-ONLY or unfetched may not appear in a footnote at all.
- **FR-003 (quote-check)**: `.claude/agents/quote-check.md` adds a READABILITY verdict per footnote - `READABLE`
  (the footnote's own link is a public page and the fetch found the passage there) or `NOT-READABLE` (paywall,
  login, abstract-only, landing page, the passage not on that page, the host refusing) - and states that a
  NOT-READABLE footnote cannot land as a citation: re-point it to a page where the passage can be read, or make it
  an absence note. Its SUMMARY-ONLY handling ("checked against a fresh search") is removed.
- **FR-004 (source-reader)**: `.claude/agents/source-reader.md` keeps the `SUMMARY-ONLY` verdict as a REPORT and
  states what the session does with it under this rule: record the search in the registry entry, cite nothing, and
  give the assertion an absence note (or find a readable page).
- **FR-005 (the sweep - census)**: the SEARCH SPACE is every footnote in `research/**/*.html` (780 on 2026-09-06). A
  footnote is a CANDIDATE unless a recorded verdict says its quoted passage was SEEN on the page its own link targets:
  the feature-194 `quote-check` reports (per footnote, VERBATIM or DIFFERS means the checker fetched the linked page
  and found the passage there) and the 2026-09-06 re-fetch (SAME or RESTORED). A footnote with no such verdict - the
  registry-linked, the `archive.org/details/` landing pages, the J-STAGE abstract pages, the NOT-ON-PAGE re-fetches,
  and, above all, every footnote the 194 checkers recorded as UNFETCHABLE and left standing with the registry's
  passage (the T06 residue: springer, sciencedirect, mdpi, wiley, tandfonline, jstor, doi.org resolving to any of
  them, baidu, zhihu) - is a candidate and is fetched by a reader. The four link shapes are examples of how a
  candidate looks, never the definition. The census script prints the count and its derivation before the sweep and
  again after it, when every footnote must carry a SEEN verdict, be an absence note, or be an A1 key.
- **FR-006 (the sweep - work)**: each candidate is worked by a reader agent: find a public page where the passage can
  be read (the source's own PDF link, an open-access copy, the archive.org full text, the publisher's article page),
  fetch it once, confirm the passage character for character. RE-POINT when found - the footnote's link becomes that
  URL and the registry entry gains it. REMOVE when not - the footnote becomes an absence note naming what was
  searched; the key leaves the section's roster if nothing else quotes it there; the registry entry stays, marked
  "not cited (no publicly readable text)". Nothing is decided from memory; a passage the agent could not see on a
  public page is not readable.
- **FR-007 (labels)**: an assertion whose only citation was removed is labeled as resting on no readable source, in
  the absence note itself; where the assertion feeds a map class explanation (`interactive/classes/`) whose label
  was `accurate` on the strength of that source alone, the label is reviewed and the case listed in the tasks file
  for the GM. The label is the GM's to change: every affected label is LISTED under this feature and none is changed.
- **FR-008 (reporting)**: the answer to the GM lists, per file, footnotes re-pointed and footnotes removed, the
  sources that were dropped from the record entirely (no footnote left anywhere), every assertion now carrying
  an absence note, every map class label listed under FR-007, AND the A1 carve-out itself - the four footnotes
  quoting the GM's notes that keep a registry link - so the exception reaches the GM as an exception (XVI).

### Key Entities

- **Footnote**: `<li id="fn-n">` in `<section class="footnotes">`; CITATION or ABSENCE form (FR-002).
- **Registry entry**: `<h3 id="key">` in `research/SOURCES.html`; may be labeled SUMMARY-ONLY (a search record, never
  a citation) or "not cited (no publicly readable text)".
- **Absence note**: the footnote text for an assertion with no readable source.

## Success Criteria

### Measurable Outcomes

- **SC-001**: every footnote in `research/**/*.html` is one of: a CITATION with a recorded SEEN verdict on the page its
  link targets; an ABSENCE note; an A1 key. Zero footnotes lack all three - the census script's second run says so
  over the whole search space, and the FR-002 tests hold the form and the registry rule at the gate.
- **SC-002**: every candidate from the census (FR-005) has a recorded verdict from a reader: RE-POINTED with the
  URL, or REMOVED with what was searched. No candidate is resolved by the session's own memory of the source.
- **SC-003**: the rule appears, in the GM's words, in the constitution (v2.19.0), root `CLAUDE.md`,
  `research/CLAUDE.md`, `quote-check.md` and `source-reader.md`.
- **SC-004**: the record and interactive tests are green; a `make done` on the merged tree is green if any engine
  file changes (none is expected - the classifier lives in the test).

## Decisions Recorded

- **D1 - a summary is not a page.** The 2026-08-27 SUMMARY-ONLY clause is superseded, not amended: a citation of a
  summary claims support that no reader can check. The registry keeps the entries as the record of what was
  searched. (GM 2026-09-06, this request.)
- **D2 - the absence note is a footnote, not a bracket in the prose.** The reader meets the record through the
  footnote marker; a marker that opens to "no publicly readable source, searched X" is the honest form and keeps the
  prose readable. It carries no key, so the roster and link tests can tell it from a citation mechanically.
- **D3 - re-point before remove.** A passage that IS on a public page reachable from the source's own site (a PDF
  link beside an abstract, the full-text view behind a landing page) is readable; removing it would lose a true
  citation. The agent must look there first, once, and only then declare nothing readable.
- **D4 - the readability test is a FETCH by an agent, the form test is static.** A test cannot fetch the internet at
  the gate; `quote-check` does the fetch before the entry lands, and the static tests hold the form so a footnote
  that skipped the agent is still visibly wrong.

## Assumptions

- **A1 - the GM's own notes are canon, not a source claimed to support a historical point.** Four footnotes quote
  `l7r.md` (`l7r-median-domain`, `URL: none`). The request is about *"online sources"* and *"claiming that the source
  supports us"*; the GM's notes DEFINE the setting rather than evidence it, and they are quoted in full in the
  footnote. They keep their registry link. If the GM rules otherwise, they become absence notes in one pass.
- **A2** - a public PDF is a public page. A page that requires a login, a purchase, or an institutional network is not.
- **A3** - an English rendering of a Japanese or Chinese page is not a quote; the original passage is, with a gloss
  (the record's existing form).
- **A4** - the sweep is run by Sonnet reader agents in waves (one fetch per host per agent), as the feature-194
  backfill was; the session applies their verdicts by script and never by recall.
