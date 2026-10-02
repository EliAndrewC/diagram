# The research doctrine, as the GM ruled it

*Project reference, split out of [`../CLAUDE.md`](../CLAUDE.md) so it is loaded on demand rather
than in every session's context. CLAUDE.md keeps the six rules in one line each; this file is the
full record with the GM's words. The operative form of the citation rules - the footnote shape, the
notes and the works cited, the download list - is
[`.claude/skills/diagram/research/CLAUDE.md`](../.claude/skills/diagram/research/CLAUDE.md), which
auto-loads when a session edits the record; the principles are constitution XII.*

**Load this file when:** a research task raises a question the one-liners do not settle - what
counts as a readable source, when a guess may be recorded, how a two-form finding becomes a knob.

---

- **Record the "why" of every research-driven rule (REQUIRED).** When historical (or setting)
  research leads us to a concrete generation rule, automated check, or magic number - "every
  farmhouse had a work yard," "~30% of farms had a storehouse," "threshing was per-household, not
  communal" - we capture the *reasoning* alongside the *rule*. Encoding the finding into a check or
  generator is necessary but not sufficient: a bare `count >= 0.3 * n` teaches a future reader
  nothing about why 0.3. So write the finding down where the rule lives - a research section, or a
  comment next to the check - covering what the research found, the decision it drove, and any
  deliberate departures from literal reality (features drawn larger than true scale for legibility
  while keeping *relative* sizes roughly honest). This protects against having to redo the research
  when memory fades or the context window rolls over, and applies to any generator, not just
  `/diagram`.
- **And the sources.** Every research finding names its sources, registered by key in
  `research/sources/` with what each was used for and the URL where it can be read (`URL: none -
  <why>` when there is none), because the interactive map owes its reader the source behind each
  claim. Primary and scholarly work first, then serious references (and an encyclopedia article's
  own references over the article); never an AI-generated encyclopedia such as Grokipedia -
  machine-rewritten, no editorial community, no provenance a reader can follow; a web-search summary
  is a pointer to sources, never a source.
- **Read what you cite.** A source is cited only after the page or paper itself has been fetched
  and read - a search summary or another page's paraphrase can state the opposite of what the source
  found. A claim taken from a summary of a source that could not be read is NOT cited (GM
  2026-09-06: *"If we are linking to online sources whose content which is quotable from public
  sources does not support our claims then we should not cite it. For example, even if a given
  source is "known" to support a point we are making, if we are not able to simultaneously quote a
  relevant passage with a quote which actually backs up our assertion and then link to a page on the
  public internet where that quote can be read, then we should NOT be claiming that the source
  supports us."*) - the claim may still be asserted, its footnote an ABSENCE note (no key, no link,
  what was searched and when), the registry entry kept as the record of the search. Dispatch the
  reading to the `source-reader` agent, in the background: give it each claim verbatim with its
  pointer and it returns READ with a quote, SUMMARY-ONLY, CONTRADICTED or NOT-FOUND; the session then
  writes the entry from the quotes.
- **Quote what you cite** (GM 2026-09-06: *"we quote the passage or passages from the reference
  which support the assertion that we are making. There is no point in including a reference if it is
  not being quoted"*). A citation is a FOOTNOTE at the assertion carrying the key, its link and the
  quoted passage(s) verbatim, one per assertion, several in a sentence that makes several; the
  quote is confirmed to be on the page by a SCRIPT (`make quote-verbatim`, feature 251: a model reads
  tokens, not characters, and blurs exactly the hyphen-for-a-dash the record must keep), and the
  `quote-check` agent, handed its report, confirms the quote supports the assertion and that every
  relevant assertion has one, before the entry lands. A foreign-language passage is quoted in
  English translation, marked as one (GM 2026-09-07: *"for foreign language things we want to quote
  the English translation rather than the original text but we also want to note that it is a
  translation"* - the note names the language and the translator, the original follows the note as
  the checker's anchor). The one exception is the GM's own campaign notes, canon rather than
  evidence (GM 2026-09-07: *"it is correct to make L7R setting notes an exception to the citation
  rule, so that should indeed be a documented exception"*).
- **The record is HTML**, hand-authored as one stem per question (`research/questions/NNNN-<heading id>.html`, how
  our maps draw it as its `.drawing.html`, each page's notes beside it; feature 303), tagged and grouped by
  `research/tags.json` and `research/contents.json`, and BUILT by `make record` into the site a reader opens (feature 301, GM 2026-10-01):
  `research/site/`, a page per question with its notes numbered from 1 and the works it cites at its foot, and
  the whole record on one page - never committed, built on main by render-sync. The maps link each question's
  small page, and every pointer to the research names its fragment (`scripts/check-research-pointers.py`).
  Every cited work's registry entry says what it is and why it applies with its honest limits - two
  write-ups, written once and derived into the works list at the foot of every page that
  cites the work. Every work carries TAGS - the period of its evidence, its region, its kind - from
  `research/source-tags.json`, and the build groups the works by them (`research/source-sections.json`) and shows each tag
  as a label whose tooltip is the category's standard strengths and limits, so a write-up states only the limits
  specific to its work (feature 305, GM 2026-10-02: *"it would be much better and more efficient to have a tagging system
  where the makefile target which assembles these pages automatically applies the correct labels"*) - and a source is judged by the `source-applicability` agent when its write-ups
  land and BEFORE a session integrates its numbers into a map (GM 2026-09-07: *"whatever subagent
  check we create in order to justify whether a source is applicable to be used in the creation of
  our diagrams, that subagent check should also be run when we first begin to make use of the source
  prior to integrating its numbers or claims or details into our maps."*).
- **A source only the GM can fetch goes on the download list, in THEIR format, appended at the
  end** (GM 2026-09-14: *"each source has a link to what you think the URL is and a link to the
  Google search as a backup where the Google search should uniquely identify the resource ... saved
  in markdown in this format since that is much easier for me to find things"*):
  the canonical list `research/to-download.md` through `make download-add` (feature 313; the GM's
  `academic-sources/TO-DOWNLOAD.md` is their marked copy, synced from it), one markdown entry per work with the guessed
  direct link AND the uniquely identifying Google-search link, what rests on it and what blocked it,
  never handed over only in a chat message; the full shape is in the research directory's
  `CLAUDE.md`, "A source the GM is to fetch by hand".
- **WHAT THE RECORD IS FOR - the reader who will click on it** (GM 2026-08-26, constitution XII).
  Every map has an interactive HTML rendering: a player hovers a feature, sees it highlighted,
  clicks it and learns what it is, why it is there, and whether that is **historically accurate**, a
  **deliberate deviation** (the SETTING differing from the history it is based on - Legend of the
  Five Rings canon; showing a feature type on the sheet - the near samurai estate; a priced
  trade-off), a **map drawing convention** (a glyph drawn at a different scale or color than the
  feature would have, so the map reads to a human eye - the oversized well, the dark bund beads; GM
  2026-09-05: *"we should distinguish in our descriptions between 'deviations' ... and 'map drawing
  conventions'"*), or a **guess** made because the record has no firm number. On a city map,
  highlight every tannery and learn that a tannery stands by water because hides are soaked. So every
  rendering decision - glyph, size, placement rule, distance, density - is recorded in one of those
  four classes, in `research/` (the finding), the operative doc (the rule) and at the point of change
  (the pointer), and listed in the feature's spec under "Decisions Recorded". An unlabeled guess is
  the one failure: the reader must never be told a guess is a finding.
- **The reader reaches the record by QUESTION** (GM 2026-09-05): the audience is *"casual RPG
  enthusiasts who might be interested to learn a little more about why these settlements are the way
  that they are"*, so a modal's "See references" lists the research headings the feature was written
  from - the questions we asked - each linking to its section on the public GitHub rendering of
  `research/`, where the sources are; the third-party works themselves are one click further out,
  never in the reader's face. A research heading is therefore written as the question a reader would
  ask from the map, and its anchor is stable.
- **The entry itself is written for that reader** (GM 2026-09-07): a term they would not know is a
  glossary tooltip exactly as on the map (one glossary, `interactive/glossary.py`, derived into the
  site's `glossary.js` by `make record`); anything addressed to a session - `Grounds:`,
  `Evidence:`, a feature number, a task id, an engine identifier, a fetch verdict - is an HTML
  comment; and nothing in the entry says what it used to say or when it was corrected (*"we can look
  it up in our version control history"*). The `record-format` agent checks all three on every
  question whose visible words changed (`make record-owed`, feature 311) beside `quote-check`; `tests/interactive/test_record_format.py` holds the mechanical
  shapes. The sensibility in full: the research directory's `CLAUDE.md`, "Who the record is for".
- **Record a decision to ACCEPT a limitation, and the alternatives that were declined (REQUIRED)**
  (GM 2026-08-17: *"we should always document this kind of decision... that way if we look it up
  later, we'll know it was a deliberate decision"*). The rule above covers a decision that produced a
  rule; this covers the other kind - where we looked at something imperfect and deliberately chose
  to leave it. Undocumented, those are indistinguishable from bugs, and the next session "fixes"
  them. So write down **what was accepted, what it costs in observable terms, which alternatives were
  priced, and who chose** - the rejected options matter as much as the chosen one, because they are
  what stops the question being reopened from scratch. Worked example:
  [`research/contents.json#water`](../.claude/skills/diagram/research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html)
  "How our maps draw channel widths" - the GM asked why a channel did not visibly narrow, the
  honest answer was that at true scale it cannot, two legibility multipliers were priced against
  keeping true size, and the ruling plus both declined numbers are recorded where the next reader
  will meet the map.
- **RESEARCH BEFORE YOU ASK FOR A RULING (REQUIRED)** (GM 2026-08-18, constitution XII). A question
  about how a place was actually built, farmed or lived in is a RESEARCH question. Run the search
  pass FIRST; the GM is asked only when the record turns out silent or contradictory, and the ask
  must say what was searched, what was found, and why it does not settle the matter. This binds the
  review loop hardest, because that is where these surface: a reviewer writing *"this wants a
  one-line ruling"* has identified a QUESTION, not delegated it.
- **A GUESS IS THE LAST RESORT - RUN THE RESEARCH PASS FIRST, ALWAYS (REQUIRED)** (GM 2026-08-26).
  Not only before asking the GM: before making ANY decision about how a place was built, farmed,
  planted or lived in whose answer you do not know - from the GM, a reviewer, a test or your own
  doubt, however small. The "guess" label is for a record that was searched and found silent. *"That
  is the kind of project that this is."*
- **MULTIPLE SUPPORTABLE ANSWERS BECOME A KNOB, NOT A CHOICE (REQUIRED)** (GM 2026-08-18). Where the
  research shows a thing was genuinely done more than one way, do NOT pick the reading you prefer:
  make it a **tunable knob with per-settlement variance**, rolled from the map's own seed like every
  other knob. The reason is a project goal rather than a historical one - these maps exist for
  players who must tell one settlement from another at a glance, so *"we want settlements which are
  within historical norms while being as different from one another as is justifiable by our
  historical research"*. Every place the record permits two forms is a place two maps can honestly
  differ, and picking one throws that away permanently. The ladder: research it; if decisive,
  implement what it says; if it supports two forms, add the knob; only if it is silent does the GM
  rule. (The "calibrated liberty" clause covers a DEGREE along a continuum - how large, how dense,
  how often - never a choice between distinct FORMS.)
- **A FORM ATTESTED ONLY IN MODERN SOURCES IS ELIMINATED FROM THE PREMODERN MAPS (REQUIRED)** (GM
  2026-09-28: *"We should eliminate anything which is only modern"*; and of the dike crops, *"We should
  avoid anything that appears only on modern lists"*). A form earns a place on a map, or a value in a
  knob, only when a premodern source attests it; one read only in a modern manual, survey or listing is
  not drawn, however well documented its modern practice. The rule applies to what the GM once asked for
  as well: the duck pen at a fish pond was drawn because the GM chose it and retired when the record found
  it modern (269 B32), and the cane, banana and vegetable dikes left the dike-crop knob while the attested
  tea dike joined it (269 B34). The same reasoning holds a modern COUNT off the premodern maps: the GM kept
  hamlets without a shrine of their own because the modern counts reflect *"a wealthier and even
  post-industrial society"* (269 B35). Where animals lived in the premodern place - ducks herded in the
  fields rather than penned at the ponds - the write-up of that place says so.

## The record is written per entry, and the pages are assembled (feature 258, GM 2026-09-20)

The GM asked whether the record's HTML pages should be split into per-entry files that a script
assembles back into the same documents, because editing a file of hundreds of kilobytes costs tokens.
The measurement said yes and moved the reason: reads of `research/` by the SESSION are 0.56% of all tool
output and 90% of them already ask for a window, but one research page was **23% to 98% of everything
that entered a checking agent's context** - a median of 68% over seventeen recorded runs - to check one
entry (`specs/258-split-the-record-into-per-entry-files/research.md` R2, R3).

So a question is `research/questions/NNNN-<heading id>.html` (feature 303), its footnotes are the `.notes.html` beside it,
a source is `research/sources/NNNN-<key>.html`, and `make record` writes the pages a reader opens. The
operative rules - how to find an entry without reading a page, how to add a question or a footnote, what
to hand a check - are in `.claude/skills/diagram/research/CLAUDE.md`.

Three things worth knowing beyond the mechanics:

- **Footnote numbers are allocated at assembly, in document order, and are typed nowhere.** Before this,
  16 of 19 pages carried their references out of order, because a note added mid-page either renumbers
  everything after it by hand or is appended out of order. Two defects fell out of allocating rather
  than typing: 4 references carried no `id` at all, and 2 pages carried a duplicated one.
- **Byte-identity is what made the split checkable, and it is not enough by itself.** Splitting and
  rejoining is lossless wherever you cut, so a splitter that cut through an HTML comment would assemble
  back byte for byte while writing fragments that correspond to nothing - which is exactly the trap
  `SOURCES.html` carries, an 8,042-byte comment holding two whole `<h2>` groups no reader sees. The
  tests assert the section count and the heading ids as well as the bytes.
- **The rule that a check reads the fragment lives in the agent CONTRACTS**, because a defined agent
  launches without this repository's `CLAUDE.md` files (feature 256). It is the whole saving; an agent
  that still opens the page collects nothing from the split.

## Every cited source is archived, privately (feature 309, GM 2026-10-02)

The GM asked for *"backup copies of all of the content we are referencing"*, against *"websites going offline, failing
to be maintained"* and *"changing URLs in a website redesign"*: every web page and every PDF the record cites, *"even
things which seem at low risk of going away, like wikipedia pages"*, a web page *"whole ... with images and css and such
and not just the html content"*. A citation is a verbatim quote from a page the reader can open; a page that dies or is
edited under its quote leaves the footnote uncheckable, so the record keeps its own copy of every cited page.

The copies live in the private repository `EliAndrewC/diagram-research`, private on purpose: *"If someone's copyrighted
work goes offline then having a private copy allows me to contact the author and ask whether they are okay with me
hosting a copy publicly, but for now I just want an archive."* Nothing from it is linked or copied anywhere public. The
host keeps one working copy of it, pushed straight to GitHub - no clone of it per session (the GM). The GM's own
downloaded files in `academic-sources/` that copy a cited source are archived beside its captures. The mechanism, the
fallback order for a dead or a refused page and the measurements: `specs/309-source-archive/`; the operative rule:
`.claude/skills/diagram/research/CLAUDE.md`.

**Amendment (the GM, 2026-10-02).** The download directory is a queue: *"once something has been added to the diagram
research repository and then pushed, then we can delete it from the academic sources directory. And in that way, looking
at that directory is just a good way to know whether there is something that we have not processed yet."* Sources read
and not cited are archived too - *"When we check a paper for one fact, it may not have what we need for the question that
we are asking, but then we may end up wanting to check the paper later for a different fact"* - every page a session
reads, the earlier reads included (the GM's choice). Then, the same day, the GM held that backfill and moved the
uncited pages to their own feature (312): a page not worth keeping is recorded with why and never stored, and a page kept
gets a write-up like any cited source; until it lands, a page is archived when it is cited. And the research pass looks in the archive first: *"our research
procedure should include a step where we first check to see if we already have something, rather than going out and
trying to find it on the internet"* - `make archive-inbox`, then `make archive-find`, before any search.


## What enforces each citation rule (feature 312, FR-005)

The GM, 2026-10-02: *"we should definitely make sure that our citation rules are enforced by tooling and not just
remembering to do the correct thing."* Every citation rule the five rules files state (ROOT = the project `CLAUDE.md`,
RC = `.claude/skills/diagram/research/CLAUDE.md`, RR = `docs/research-record-rules.md`, RD = this file, PS =
`container-scripts/page-session-rules.md`) is listed with the tool that holds it: a script that refuses, a build refusal, a
hook, a test, or - for a rule that needs judgment - a check agent the record gate owes on the words the rule governs
(`scripts/_record_units.py` owes it; `scripts/entry-gate.sh` refuses the push until it is answered). Rows that are not
citation rules (rendering, process, coordination) are kept and marked out of scope, so the inventory can be read whole.
`tests/test_citation_rule_inventory.py` holds every file this table names to existing. A NEW citation rule is added here
with its tool in the same change.

| # | rule | stated in | enforced by | mechanical |
|---|---|---|---|---|
| 1 | Every citation is a footnote at the assertion (one per assertion, several per sentence that asserts several), written `<sup class="fn" data-note="key">` with a matching `<li data-note>` in the page's notes file; no hand-typed numbers. | ROOT (Research, "A citation is a footnote"); RC:68-76 (Editing), RC:~165 ("A reference QUOTES"); RR:227; RD:46-49 | `l7r/diagram/interactive/record/notes.py` (NoteError: "a reference names `k`, which no note on this page defines"; note nothing references; key defined twice; not lower-case kebab); `record/site_notes.py:67`; `tests/interactive/test_footnotes.py::test_every_footnote_resolves_and_every_definition_quotes_a_registered_source`. Gap: "one footnote per assertion" (an assertion with no note) is only the quote-check agent's "assertions with no footnote" reading, owed via `scripts/_record_units.py` ("a block with no mark ... -> quote-check unfootnoted reading"). | yes for resolve/orphan/duplicate; no for "one per assertion" |
| 2 | Every footnote quotes the passage it rests on, verbatim, including the source's own spelling and dashes; nothing is quoted from memory. | ROOT; RC (A reference QUOTES, ~l.165-185); RR:227; RD:46-53; PS:31-33 | `scripts/_quote_verbatim.py` (`make quote-verbatim`, character-for-character against the saved page; bundled by `scripts/_check_bundle.py:262`); `tests/interactive/test_footnotes.py` (a citation note must carry a quotation of 12+ chars: "no quotation"); `quote-check` agent owed by `scripts/_record_units.py` (a note new/changed -> quote-check) and answered at push by `scripts/entry-gate.sh` (needs `make record-checked`). The house-style hook exempts quoted spans (`scripts/_hm_house.py`). | yes (verbatim on the page); no (does it support) -> see row 5 |
| 3 | A foreign-language passage is quoted in English translation, marked `(translated; original: 「...」)`; English is presumed and this project the translator, so only another translator is named; the original follows the note as the checker's anchor, never as a second quote. | RC (A reference QUOTES); RR:227; RD:53-57; ROOT ("English translation marked as one"); PS:31-32 | `tests/interactive/test_footnotes.py::test_a_foreign_language_quote_is_a_marked_translation`, `::test_no_note_says_the_source_s_own_english_or_by_this_project`; `record/originals.py` (a bad original refused by name, `test_record_site.py::test_a_notes_file_with_a_bad_original_is_refused_by_name`); `translation-check` agent owed by `scripts/_translation_owed.py` / `_record_owed.py`. | yes (shape); no (faithfulness - agent) |
| 4 | A note quoting several passages joins them with `; ` (a lead-in passage ends with `:`) and an original is stored apart in `.originals.html` by the build. | RC (A reference QUOTES) | `record/originals.py` stores the original apart; the joining form is `quote-check`'s `JOINED-WRONG` (`.claude/agents/quote-check.md`, feature 312), owed on every changed note by `scripts/_record_units.py` | yes (partly NONE: the `; `/`:` joining) |
| 5 | The quoted passage must actually support the assertion it is attached to (verbatim is not enough). | RR:227; RC (A reference QUOTES, quote-check paragraph); RD:49-52 | `.claude/agents/quote-check.md` (SUPPORTS / PARTIAL / DOES-NOT-SUPPORT), owed by `scripts/_record_units.py` and held by `scripts/entry-gate.sh` (unanswered unit refuses the push). | no |
| 6 | Cite a source only after the page itself has been fetched and read; a claim taken from a summary of an unread source is not cited, and a web-search summary is a pointer, never a source. | RD:33-45 and RD:26-32; ROOT ("A source that cannot be read is not cited"); RC (A citation links..., GM 2026-09-06); PS:31-32 | `source-reader` agent (`.claude/agents/source-reader.md`: READ / NOT-FOUND / CONTRADICTED), owed on every new/changed note (`scripts/_record_units.py`: note changed -> source-reader) and answered at `scripts/entry-gate.sh`; `scripts/_source_pages.py` saves the page before the reader runs. Nothing proves the session actually fetched the page it cites. | no |
| 7 | Dispatch reading to `source-reader` in the background, handing it the full page saved by `make source-pages` (not a fetch extract). | ROOT; RR:198 (every reference is a link); RD:42-45 | `scripts/check-bundle-hooks.sh` (a record check dispatched at the repo instead of a bundle is refused); `scripts/_check_bundle.py` (`check-bundle: REFUSED` for a check nothing owes). | yes |
| 8 | A citation's link must be a public http(s) page on which the passage can be read (the public PDF, not the abstract; the full-text view, not a landing page); never a paywall, login wall or search summary. | RC (A citation links to a page ..., CITATION); RR:251; ROOT | `l7r/diagram/interactive/citations.py::footnote_form` (a citation whose key links to a non-http target is a defect "which is not a page on the public internet where the quote can be read"; canon keys exempt); `tests/interactive/test_footnotes.py`. Whether the page really shows the passage is `quote-check` READABLE (`.claude/agents/quote-check.md`). | yes (link shape); no (paywall / page really readable) |
| 9 | A page the container cannot fetch is not thereby unreadable: if the GM can open it, it is public; the GM downloads it, the session reads the archived copy, the footnote links the PUBLIC page and says the copy was read, quote-check runs against the copy; a paywalled text with a public abstract is cited for the abstract's words only. | RC (A citation links ..., last paragraph); RR:251 (A page the container cannot fetch...); ROOT | `scripts/_archive_ops.py` / `make archive-inbox` / `make archive-find` (gm-copies/); `make access-tags` (`scripts/_access_tags.py`). The "link public page, say the copy was read" form is not mechanically checked. | no |
| 10 | When a page cannot be read, the claim may still stand with an ABSENCE note: `no publicly readable source<!-- searched YYYY-MM-DD: what was tried -->` plus what the search found; no key, no URL. | RC (ABSENCE); RR:251; RD:39-45; ROOT; PS:23-24 | `citations.py::ABSENCE` + `footnote_form` ("an absence note carries no key and no link"); `record/absence.py`; `tests/interactive/test_footnotes.py::test_the_sourceless_footnote_forms_keep_their_shape`. | yes |
| 11 | An absence note supports only a stated silence or a GUESS of our own - never a claim of what a named page says that no one here could read. | RC (ABSENCE, feature 292, GM 2026-09-30) | `quote-check`'s `CLAIM-FROM-UNREAD` (`.claude/agents/quote-check.md`, feature 312), owed on every changed note by `scripts/_record_units.py` | no |
| 12 | An absence note may carry `settled DATE` only after two independent passes on different dates, the second using a tool the first lacked; it re-opens on anything that changes what can be read. | RC (ABSENCE); RR:251 | `tests/interactive/test_footnotes.py::sourceless_shape_faults` (settled needs two different `searched` dates; only an absence note can be settled); "second used a tool the first lacked" is left to `record-format` (per the test comment); `scripts/_open_questions.py` derives the open list. | yes (two dates); no (tool differs) |
| 13 | A GROUNDS note (`no source is owed: <reason>`) takes a reason from a CLOSED list of six; carries no key, link or quotation. | RC (GROUNDS); RR:251 | `citations.py::GROUNDS_REASONS`, `grounds_reasons`, `footnote_form` ("names a reason that is not one of the six"); `tests/interactive/test_footnotes.py` (`sourceless_shape_faults`). | yes |
| 14 | A GROUNDS note is NEVER used for a claim about how a place was built, farmed, planted, governed or lived in, nor for a labeled GUESS about the physical world - those owe a citation or an absence note. | RC (GROUNDS); RR:251 | `quote-check`'s `GROUNDS-MISUSED` (`.claude/agents/quote-check.md`, feature 312), owed on every changed note by `scripts/_record_units.py` | no |
| 15 | Using one of the four not-yet-exemplified grounds reasons on an existing note takes a written argument at that note's page; a note converted from an absence note keeps its search in an HTML comment. | RC (GROUNDS); RR:251 | `quote-check`'s `GROUNDS-UNARGUED` (`.claude/agents/quote-check.md`, feature 312), owed on every changed note by `scripts/_record_units.py` | no (written-argument part); the HTML-comment part is partly yes but unchecked |
| 16 | Only the GM's own campaign notes are exempt from the citation rule (canon, not evidence); they keep their registry link, and that entry cites the notes on GitHub (`https://github.com/EliAndrewC/l7r/blob/master/setting/<file>.md`, each quoted section followed by its heading URL by GitHub's anchor rule). Nothing else is carved out (`URL: none`, gone pages, SUMMARY-ONLY). | RC (the one exception ...); RR:251; RD:57-59; ROOT ("GM's own campaign notes ... need no citation") | `citations.py::footnote_form` (canon keys allowed to link `SOURCES.html#`); `l7r/diagram/interactive/sources.py::canon_keys`; `tests/interactive/test_citations.py::test_every_canon_entry_links_its_notes_on_github_and_none_says_url_none`; `record/source_tags.py` (exactly one canon section). | yes |
| 17 | Every reference to a work is a link: a key is never bare; a document READ links to the first URL on its registry citation line; one not read (SUMMARY-ONLY, `URL: none`, unfetched) links to its registry entry; the key is the link text; a work named in prose or by surname is linked at first mention in a section. | RC (Every reference is a link); RR:198 | `tests/interactive/test_sources.py` (every cited key a link to the right target); a work named in prose or by surname: `quote-check`'s `UNLINKED-NAME` (`.claude/agents/quote-check.md`, feature 312) | yes (keys); NONE for prose/surname mentions |
| 18 | Every cited key is a registry entry (`research/sources/010-works-cited/NNNN-<key>.html`); the registry has one entry per key; a read document with no entry gets one first, after searching the registry by URL (percent-decoded) and by the whole entry; nothing links to a URL nobody fetched. | RC (Every reference ..., Where things are); RR:198; RD:26-29; PS:63-66 | `tests/interactive/test_footnotes.py` ("no registry key link"); `tests/interactive/test_sources.py::test_the_registry_has_one_entry_per_key`; `scripts/reserve-prefix.py` (`make reserve KIND=registry`, flock-allocated, duplicate-key refusal); `scripts/new-file-hooks.sh` (a new registry file without a reserved prefix is refused). "search the registry by URL first" is process only. | yes (existence/uniqueness); no (search-first) |
| 19 | A registry entry records the URL where the work can be read (`URL: none - <why>` when none) and the READ date. | RD:26-28; RC (Every reference is a link, "A new entry records the URL and its READ date") | `tests/interactive/test_page.py` (an entry with neither a URL nor `URL: none - <why>` fails) | yes -> NONE found for URL/READ-date presence |
| 20 | Source quality order: primary and scholarly work first, then serious references (an encyclopedia article's own references over the article). | RD:28-30 | `source-applicability` (`.claude/agents/source-applicability.md`: it judges the kind of work and names a closer public source it knows of), owed on every changed write-up by `scripts/_record_units.py` | no |
| 21 | Never cite an AI-generated encyclopedia (Grokipedia); other banned citations are listed by URL pattern with the GM's approval. | RD:29-31; (feature 312 FR-004 in `record/blocked.py`) | `l7r/diagram/interactive/record/blocked.py` (`BlockedListError`, `refusal()`, `refusals()` wired into `record/site.py:237`; data `research/blocked-domains.json`, `research/banned-citations.json`); `tests/interactive/test_record_blocked.py::test_the_real_list_blocks_grokipedia_with_the_gms_approval`, `::test_the_build_refuses_a_blocked_or_banned_citation_in_an_entry_or_a_footnote`; `scripts/blocked-fetch-hooks.sh` (fetch routes). | yes |
| 22 | A form attested only in modern sources is eliminated from the premodern maps (a form earns a place, or a knob value, only when a premodern source attests it). | RD:150-160 | out of FR-005's scope - a rendering rule (what a map draws), not a citation rule | no |
| 23 | Every cited work's registry entry carries two write-ups after its citation line: `<p><em>What it is:</em>` and `<p><em>Why it applies, and its limits:</em>`, each one to three sentences, honest about date, place and method. | RC (A question's notes stand at its foot; every cited work says what it is); RR:390 | `record/site.py:250` (build refusal: "whose registry entry has no write-up (`What it is:` and `Why it applies, and its limits:`)"); `l7r/diagram/interactive/citations.py::works_html` (missing list); `tests/interactive/test_citations.py::test_every_cited_work_has_both_write_ups`. Honesty and the 1-3 sentence length: NONE mechanical (judged by `source-applicability`). | yes (present); no (honest / length) |
| 24 | A work cited from several pages has one write-up (explained once; no duplicated write-ups); the works list at each page's foot is derived. | RC (same section); RR:390 | `tests/interactive/test_citations.py::test_a_work_cited_from_two_pages_has_one_write_up`; derived by `citations.py::works_html` / `record/site_notes.py`. | yes |
| 25 | A write-up's "limits" paragraph states only what is specific to the work (the category's standard limits are carried by its labels) - never generic lines like "it is a tertiary article". | RC (Every entry is TAGGED); PS:65-66 | `source-applicability`'s RESTATES verdict (`.claude/agents/source-applicability.md`, step 4), owed on every changed write-up | no |
| 26 | Every registry entry is tagged `<!-- tags: period=a[,b]; region=x[,y]; kind=k -->` from `research/source-tags.json` (first value primary; period follows the evidence, not the publication); the GM's campaign notes carry none; the build refuses an untagged entry, an unknown value, or tags no section takes. | RC (Every entry is TAGGED); RD:66-72; PS:63-66; RC "A vocabulary edit is followed by `make source-tags-contract`" | `l7r/diagram/interactive/record/source_tags.py` (`SourceTagError`: "no period in its tags", "not a period value", "two tags markers", etc.; catalog errors gathered in `record/site.py`); `scripts/reserve-prefix.py` (`TAGS=` validated against `source-tags.json`); `tests/interactive/test_source_tags.py`. "period follows the evidence" is judgment. | yes (presence/validity); no (correct period) |
| 27 | A `Used for:` line in a registry entry names each section it serves as a LINK `(<a href="contents.json#id">Title</a>)`, never a page file name; the build refuses an id that is not a section. | RC (A question's notes ...); RR:390 | `record/site_links.py` (resolves `contents.json#<id>`; unknown id refused); `tests/interactive/test_record_site.py::test_a_used_for_line_links_its_section_on_both_forms_and_an_unknown_one_is_refused`. | yes |
| 28 | A source is judged (APPLICABLE / WITH-LIMITS / NOT-APPLICABLE to a premodern East Asian setting, write-up limits HONEST/MISSING/OVERSTATED) when its write-ups land and BEFORE its numbers/claims/details reach a map or a rule; a NOT-APPLICABLE source is recorded and listed for the GM and its assertions keep their label until the GM rules. | RC (A source is judged before it is used); RR:390; RD:72-76; ROOT; PS:71-72 | `.claude/agents/source-applicability.md`; owed by `scripts/_record_units.py` ("a source write-up's visible words changed -> source-applicability", incl. `sources/040-uncited-works`) and held at push by `scripts/entry-gate.sh`; `tests/test_task_research_boxes.py` (physical task's fifth box `source-applicability confirmed`, from feature 211). The "before it reaches a map" half is only the task box. | yes (owed on write-up change, task box); no (the judgment; map-use timing) |
| 29 | A `research: physical` task carries boxes `research pass`, `source-reader confirmed`, `recorded and cited`, `quote-check confirmed`, `source-applicability confirmed`, all ticked before the task is. | ROOT (Development workflow, not the Research section but cites it); RR:390-438 | out of FR-005's scope - a task-box rule (`tests/test_task_research_boxes.py` holds it) | yes |
| 30 | A source only the GM can fetch goes at the END of the download list in the GM's format: one entry per work headed `### NEW. <the work>`, a link to where the session believes it lives, `- Fallback:` Google-search link that uniquely finds it, `- **Rests on it:**` naming the `research/questions/` files, `- Blocked by:` - BOTH links, always; never handed over only in a chat message. | ROOT; RC (A citation links ..., download paragraph); RR:251 ("A source the GM is to fetch by hand"); RD:77-85; PS:32-33 | `scripts/_downloads.py` (`make download-add FILE=`: "checked for its parts (plan D6); refuses naming what is missing", numbered under a host lock, appended at the end; `check` at push refuses an entry lost, moved, inserted - plan D11); `scripts/sync-with-main.sh` runs it at push. The "chat message only" prohibition and "Google query uniquely identifies" are not checkable. | yes (shape/placement); no (unique query; not chat-only) |
| 31 | Never write the GM's copy `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md`; sessions append only to `research/to-download.md`; "ingest" and "sync" are the GM's words and run `make downloads-ingest` / `make downloads-sync`. | RC (The GM's two words); RR:251; ROOT; PS:32-33 | `scripts/download-copy-hooks.sh` (refuses a write to the copy; escape `DOWNLOAD_COPY_OK`); `scripts/_downloads.py` (sync refuses while the copy holds un-ingested marks). | yes |
| 32 | Every cited page (every URL in a registry entry, its comments' too, and every URL a footnote links) is archived in the PRIVATE repo `EliAndrewC/diagram-research`, with a row in `research/archive/<id[:2]>/<id>.json`. | RC (Every cited page is archived); RD:191-205; ROOT | `l7r/diagram/interactive/record/archive.py::refusals` (build refusal "a cited URL with no covering row", naming `make archive URL=<u>`; wired in `record/site.py:236`; a pending upload covered one week then refused); `tests/interactive/test_record_archive.py`. `make reserve ... URL=` and `make source-outcome OUTCOME=cited:` archive their URLs (`scripts/_archive_ops.py`). | yes |
| 33 | Never link or copy the archive anywhere public (much of it is copyrighted); the repo stays private. | RC (Every cited page is archived); RD:199-205; ROOT | the archive repository is PRIVATE on GitHub (access control); its copies are linked only from the record's archived-copy lines the GM asked for (`l7r/diagram/interactive/record/archive.py`) | yes (a grep for the archive repo's URL/paths in public output could check it) |
| 34 | Look in the archive before the web: start each research pass with `make archive-inbox` (the GM's downloads archived then removed; a NEW download is WAITING until `MATCH='<file>=<key>'` or `NONE='<file>'`), then `make archive-find URL= | KEY= | `scripts/_archive_ops.py` (the commands); the order is held by `scripts/blocked-fetch-hooks.sh`, which tells a WebFetch of an archived page to use `make archive-find` (feature 312), and `make archive-find` prints the earlier attempts first | ROOT; RC (Look in the archive before the web); RD:207-216; PS:34-38 |
| 35 | Every page read is on the sources-consulted ledger and the attempts log: `make source-pages ... QUESTION=<NNNN> SOUGHT="..."` prints each URL's earlier reads, attempts and filter verdict before it fetches; a page already judged for the same question is not re-read without a reason; every page's outcome is recorded with `make source-outcome`. | RC (Every page read is on the ledger); PS:44-47; ROOT | `scripts/_source_pages.py` (prints earlier reads and attempts first; refuses without `SOUGHT=`; refuses a re-read of a page already judged for the same question without `REREAD=` - feature 312); `scripts/_attempts.py`; `scripts/_sources.py` (`make source-outcome`) | yes |
| 36 | Several attested forms are a KNOB rolled per settlement from the seed, never a choice (a degree along a continuum is calibrated liberty). | ROOT; RD:139-149; PS:25-26 | out of FR-005's scope - a design rule for the generator | no |
| 37 | Every rendering decision is recorded in one of four classes - accurate, deviation, convention, guess - in `research/` (the finding), the operative doc, the point of change (pointer) and the feature's spec "Decisions Recorded"; an unlabeled guess is the one failure; a convention's modal note ends with the real size or color. | ROOT; RC (Four labels); RR:182; RD:86-99; PS:27-28 | out of FR-005's scope - a rule for labeling rendering decisions | no |
| 38 | A research-driven rule or magic number records its why beside the rule; a decision to ACCEPT a limitation records what it costs, the alternatives priced, and who chose. | ROOT; RD:15-25, RD:115-127; PS:29-30 | out of FR-005's scope - a rule for recording the why of a rule | no |
| 39 | Run the search pass before deciding, before asking the GM, and before writing "guess"; ask the GM only when the record is silent or contradictory and say what was searched and found; a record silent after a search gets an absence note. | ROOT; RD:128-138; PS:23-24 | out of FR-005's scope - a process rule for when to ask the GM | no |
| 40 | Setting canon is read only through `make canon TERMS="a\|b\|c"` (every term in one call). | ROOT (guards table); PS:18-19 | `scripts/canon-read-hooks.sh` (refuses a direct read or grep of `setting/`, and a second `make canon` within three calls unless it folds the earlier terms); `scripts/_hm_canon.py` | yes |
| 41 | The record is HTML under `research/`: one stem per question (`questions/NNNN-<heading id>.html`, `.drawing.html`, `.notes.html`, `.originals.html`), sources under `sources/NNNN-<key>.html`; never edit a built page; footnote numbers are allocated at build. | ROOT; RC (Where things are, Editing); RD:60-65; RR:439-520; PS:39-41 | `scripts/record-edit-hooks.sh` (an Edit aimed at a built page is re-aimed at the fragment or refused; Write refused); `l7r/diagram/interactive/record/site.py` (build refusals: duplicate ids, orphan notes, links that land nowhere); `tests/interactive/test_record_site.py`, `test_record_store.py`. | yes |
| 42 | A pointer to the research (code comment, doc, spec, `Entry:`) names the FILE (`research/questions/NNNN-<id>[.drawing].html`, or `research/contents.json#<section>`), never a built page or a retired form. | ROOT; RC (Where things are); RR:520 | `scripts/check-research-pointers.py` ("pointers to the research that do not resolve, or are of a retired form"), run at the gate and at push; `make fragment-move` rewrites pointers; `scripts/check-entry-headings.py` (Entry: heading resolves; fails the gate). | yes |
| 43 | Every question carries TAGS (subjects - first is primary - settings, one level) from `research/tags.json`; its home is the first `contents.json` section that takes them; the build refuses a question with no tags or tags no section takes. | ROOT; RC (Editing, A new question); RR:587 | `l7r/diagram/interactive/record/contents.py` (`ContentsError`: "no subject in its tags", "N levels - a question has exactly one", "no such tag in tags.json"); `scripts/reserve-prefix.py` (stub with an unfilled marker the build refuses); `tests/interactive/test_record_questions.py`. | yes |
| 44 | A heading is the question a reader would ask from the map; an anchor is stable (a renamed heading owes its inbound `Entry:` links). | RC (Who the record is for); RR:127; RD:100-106 | `scripts/check-entry-headings.py` (gate fails on an `Entry:` resolving to nothing); `make fragment-move`. "Heading phrased as a question" is judged by `intro-check`/`record-style`. | yes (anchors); no (phrasing) |
| 45 | The record is written for a casual reader: a term they would not know is a glossary tooltip; session notes (`Grounds:`, `Evidence:`, a feature/task/spec/make target/engine identifier, fetch verdicts) are HTML comments; no history of the document ("used to say", correction dates). | RC (Written for the reader, items 1-3); RR:333; RD:107-114; ROOT; PS:39-40 | `tests/interactive/test_record_format.py::test_the_fields_for_a_session_are_comments`, `::test_no_session_note_or_document_history_is_visible`, `::test_every_glossary_term_is_used_by_a_modal_or_a_record_page`; `record-format` agent owed by `scripts/_record_units.py` (VOCABULARY, SESSION NOTE, HISTORY; prepass `scripts/_record_prepass.py` candidates must each be ruled on). | yes (the listed shapes); no (vocabulary/history judgment) |
| 46 | A question a reader would not think to ask opens with `<p class="intro">`, cites nothing and adds no claim the findings do not carry. | RC (Written for the reader, item 4); `STYLE.md` section 2 | `tests/interactive/test_record_format.py::test_every_intro_paragraph_has_its_shape`; `intro-check` agent owed by `scripts/_record_units.py` (heading or intro changed). | yes (shape); no (needed / honest) |
| 47 | A question's prose stays under 20,000 bytes (notes and originals not counted). | RC (A question has a size) | `scripts/check-question-size.py` (`make quick` fails on one a change touched; `make question-sizes`). | yes |
| 48 | A section a modal was written from moving owes an `entry-drift` check and a rewrite of what it calls DRIFTED. | RC (When a section a modal was written FROM moves); RR:489 | `scripts/_entry_owed.py` + `scripts/entry-gate.sh` (push refuses unanswered pairs; escape `ENTRY_DRIFT_OK`); `.claude/agents/entry-drift.md`. | yes (owed/answered); no (IN-STEP verdict) |
| 49 | Reading and checking are dispatched to defined agents in the background, each run against a `make check-bundle` bundle (never a path under `/diagram`), after the mechanical prepass whose output goes in the prompt; the agent's reply is counts first. | ROOT; RC (Checking); PS:42-43, PS:71-72 | `scripts/check-bundle-hooks.sh` (refuses a record-check dispatch into the repo, names the `make check-bundle` command); `scripts/_check_bundle.py` (builds MANIFEST, includes `quote-verbatim.txt`, prepass rows). | yes |
| 50 | A check runs only where the words it reads changed (`make record-owed` names every unit); `make check-bundle` refuses a bundle for a check nothing owes; each returned check is recorded with `make record-checked`, or the push refuses the unit. | RC (Which check is owed, and when it is answered); PS:73-76; ROOT (guards table) | `scripts/_record_owed.py` / `scripts/_record_units.py` (owed set), `scripts/_bundle_owed.py` + `scripts/_check_bundle.py` ("check-bundle: REFUSED"), `scripts/check-bundle-hooks.sh`, `scripts/entry-gate.sh` (`--unanswered`; escapes `CHECK_NOT_OWED_OK`, `NOT_OWED_OK`, `RECORD_CHECKS_OK`). | yes |
| 51 | A cheaper check is proved by every candidate the prepass raised being ruled on (not "same findings"); a tier downgrade is proved by seeded runs on known findings, three a leg. | RC (A cheaper check is proved); RR:9 | `tests/test_agent_models.py` (pinned tiers, `omitClaudeMd`); the "three a leg" evidence itself is not checked. | no |
| 52 | A write session takes at most four questions and at most ten new registry keys; larger briefs must declare `<!-- page-load: kind=... -->`; the eleventh key sends the rest to a continuation brief. | RC (A write session takes ...); PS:50-54; ROOT | `scripts/_brief_load.py::refusal` ("WRITE_CAP_OK" escape) via `scripts/_page_session_runner.py`; `scripts/reserve-prefix.py` key-cap (escape `KEY_CAP_OK`). | yes |
| 53 | Coordination files (claims file, handoff, checks report) are read by line (`make lines`) and written with `make append`, never whole. | RC (A write session takes ...); PS:48-49; ROOT | out of FR-005's scope - a coordination-file rule for page sessions | yes (a hook could match reads of those paths) |
| 54 | New glossary files and registry entries take their prefix from `make reserve KIND=glossary\|registry\|uncited KEY=<k>` (host-wide lock). | ROOT (guards table); PS:63-64; RC (Editing, A term) | `scripts/new-file-hooks.sh` (refuses an unreserved new file, names `make reserve`); `scripts/reserve-prefix.py` | yes |
| 55 | An ad-hoc agent always names a `model` (`sonnet` to read, fetch, translate, extract; `opus` for anything that judges); defined agents carry `omitClaudeMd`. | ROOT; PS:77-78 | `scripts/agent-model-hooks.sh` (refuses a model-less ad-hoc dispatch); `tests/test_agent_models.py`. | yes |
| 56 | An uncited page worth keeping gets a write-up like a cited source and its entry lives in the uncited works (`040-uncited-works`); a page not worth keeping is recorded with why and never stored; a footnote may not cite an uncited entry (it is moved to the works cited first with `make cite-uncited`). | RD:207-216 (amendment); RC (archive paragraph "which uncited pages to keep is feature 312's") | `record/site.py:251` (build refusal naming `make cite-uncited KEY=`); `tests/interactive/test_record_uncited.py`; `scripts/_uncited.py` + `.claude/agents/source-filter.md`; `scripts/_record_units.py` `SOURCE_DIRS` (write-ups of uncited works are owed `source-applicability`). | yes |
| 57 | Source roster: a section's `<p><strong>Sources:</strong>` roster, where it still exists, has every key quoted by a footnote in that section; a section restyled under STYLE.md has none. | RC (A reference QUOTES; STYLE.md section); RR:227; ROOT (notes at its foot) | `tests/interactive/test_footnotes.py::test_every_key_on_a_sources_roster_is_quoted_by_a_footnote_in_its_section`; `tests/interactive/test_no_sources_roster.py::test_no_section_keeps_a_sources_roster` (the second now forbids rosters altogether, which makes the first vacuous - RC and RR still describe rosters as a live form: stale wording). | yes |
| 58 | The notes appear at each question's foot, numbered from 1 on that page, with the works they cite; the single page numbers once through the whole record; a note two pages cite is in both notes files. | RC (A question's notes stand at its foot); RR:390, RR:520 | `tests/interactive/test_record_site.py::test_a_small_page_numbers_its_notes_from_one_and_its_foot_lists_what_it_cites`, `::test_the_single_page_numbers_once_through_the_whole_record`; `record/site_notes.py`. | yes |
| 59 | The build makes every bare URL on a citation line a link opening in a new tab, so a citation line is written with its URL in plain text; no page of the built site shows a bare URL. | RC (A citation links ..., canon paragraph) | `l7r/diagram/interactive/sources.py::linkify`; `tests/interactive/test_citations.py::test_a_bare_url_becomes_a_link_opening_a_new_tab...`; `tests/interactive/test_record_site.py::test_no_page_of_the_built_site_shows_a_bare_url`. | yes |
| 60 | House style stops at a quotation: a quoted passage keeps its source's own dashes and spellings (and the GM's own writing). | ROOT (House style); PS:10-12; RC (A reference QUOTES) | `scripts/house-style-hooks.sh` + `scripts/_hm_house.py` (exempts 「」, quotes, GM blocks), `scripts/check-house-style-delta.py`. | yes |
| 61 | A research page is worked in two fresh sessions (write, then check-and-apply from briefs via `make page-session`); a report's findings are applied in one turn. | ROOT; RC (Checking) | out of FR-005's scope - a session-procedure rule | no |
| 62 | Never push or commit against `/host-l7r-repo`; research session work stays in its clone. | ROOT (intro) ; PS:58-61 | `scripts/repo-safety-hooks.sh` (git writes to `/host-l7r-repo` refused; escape `HOST_GIT_OK`). | yes |
