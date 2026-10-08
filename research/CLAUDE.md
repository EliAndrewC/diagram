# research/ - the historical record: the rules

This file auto-loads into every session that reads a research file, on every turn, so it carries the RULES and an
index. Why each is the rule - the GM's words, the incidents, the measurements - is in
[`docs/research-record-rules.md`](../docs/research-record-rules.md), under the same headings; read it before arguing with
a rule. The root `CLAUDE.md` "Research" section (archive first, bundles, the write cap, `make lines`/`append`, the
download list) applies here and is not repeated.

| when you | load |
|---|---|
| write or restyle a section | [`STYLE.md`](STYLE.md) - how an entry reads |
| need a source only the GM can fetch, process the GM's downloads, archive a cited URL, or the GM says "ingest"/"sync" | [`downloads.md`](downloads.md) |
| push a record change: which checks it owes, recording an answer, the code's `Research:` claims, a modal's section moving | [`record-checks.md`](record-checks.md) |

## Where things are (features 258, 303)

| what you want | where it is |
|---|---|
| a question's research | `research/questions/NNNN-<heading id>.html` - one flat directory, one STEM per question (feature 303) |
| how our maps draw it | `research/questions/NNNN-<heading id>.drawing.html`, the same stem |
| a page's footnotes | `<its file>.notes.html` beside it (`NNNN-<id>.notes.html`, `NNNN-<id>.drawing.notes.html`); originals in `.originals.html` |
| a question's tags | the marker on the line after its heading: `<!-- tags: subject=a,b; setting=countryside,town; level=detail -->` |
| the vocabulary | `research/tags.json` - every subject, setting and level |
| the sections, their order | `research/contents.json` - the table of contents; a section takes questions by a rule over their tags |
| a source's registry entry | `research/sources/010-works-cited/NNNN-<key>.html` |
| the page a reader opens | `research/site/q/<heading id>.html` (a question), `findings/<section>.html` and `drawing/<section>.html` (a section in each half), `tags/<facet>-<tag>.html`, `all.html` (the whole record) - BUILT by `make record`, never committed, never hand-edited |
| a pointer to a question | `research/questions/NNNN-<heading id>[.drawing].html` - the FILE, never a built page; a whole section is `research/contents.json#<section id>` (`scripts/check-research-pointers.py`) |
| a glossary term | `l7r/diagram/interactive/assets/glossary/NNNN-<term>.json`, one file per term (feature 259) |
| the download list | `research/to-download.md` (canonical; [`downloads.md`](downloads.md)) |

`NNNN` is the question's identity across the record, never its order: the order is the table of contents' (its section,
then its level, then its number). Find a question with a glob on its heading id (`ls research/questions/*-<anchor>*`) or
a grep over `research/questions/` - never `ls research/sources/` bare (2,127 entries), never open a built page to edit
it (the guard re-aims the Edit). A pointer of a retired form (`research/<page>/NNN-...`, or an old page name and its
three-digit number) is refused by the pointer check, naming the new one from `research/moved-303.json`.
`research/assets/glossary-variants.txt` maps a word to the term that owns it; grep it, never read it whole.

**Editing.** Edit the file, then `make record` (and `make glossary` for a term) at the repository root;
`make record CHECK=1` builds in memory and names every refusal (a link that lands nowhere, an id used twice, a note
nothing cites, a question with no tags or tags no section takes). **A new question**: `make reserve KIND=question
KEY=<heading id>` gives it the next number and a stub; write its heading and FILL ITS TAGS from `research/tags.json` -
subjects (the first is primary and decides its section), settings, one level (foundational, subtype, detail, counts and
measurements); its home is the first section of `contents.json` whose rule takes those tags. Its drawing page is the
same stem's `.drawing.html` and states no tags (it inherits them); a second drawing page of one question is a stem of its
own saying `<!-- about: NNNN-<slug> -->`. **Renaming or renumbering one** - a retitled heading, a new number - is `make
fragment-move FROM=<file> TO=<file>`, which moves every file of the stem and rewrites every pointer to it. **Regrouping
the record** is an edit to `contents.json` alone; no question file moves. **A footnote**: no number anywhere - `<sup
class="fn" data-note="<key>"></sup>` in the prose, `<li data-note="<key>">...</li>` in that page's `.notes.html`; repeats
of one work are `key`, `key-2`, ... A reference resolves in its own page's notes only.
**A link** inside the record is written from `questions/`: another question as `NNNN-<slug>[.drawing].html[#id]`, an id
on the same page as `#id`, the registry as `../SOURCES.html#<key>`.
**A term**: a new file with a free prefix; the prefix order decides which term wins a shared variant. The
assembled `assets/glossary.json` is written by `make glossary`, and the site's `glossary.js` by `make record`; neither
is hand-edited.

**Checking** (feature 250). `make check-bundle Q=<NNNN>` (a question's number - both its pages - or one page's file
name; `KEY=<k>` for a registry entry; `KIND=<class>` for `entry-drift`; `NOTES=<key,key>` to re-check only those)
copies what ONE check reads out of the repository into one `MANIFEST.md`; dispatch the check naming that MANIFEST and
nothing under `/diagram`. `make notes Q= KEYS=` prints a few notes and the paragraphs carrying them; `IN=<section or
tag>` runs a prepass over a whole section. A report's findings are applied in ONE turn - every turn re-reads the whole
context. Which checks a change owes: [`record-checks.md`](record-checks.md).

**Write sessions.** Over the cap (four questions, ten new registry keys) the runner names the split (`<g>a-write.md`,
`<g>b-write.md`); at the eleventh key, finish the question in hand, write the unreached items to `$L7R_CONTINUE` as a
brief of the same shape, commit and stop. Escapes, logged: `WRITE_CAP_OK='<reason>'`, `KEY_CAP_OK='<reason>'`.

**Every page read is on the sources-consulted ledger** (feature 288). `make source-pages OUT=<dir> URL=<u>
QUESTION=<NNNN>` prints each page's earlier reads BEFORE it fetches, and caches each page (`REFRESH=1` fetches a copy
under seven days old again). A page already `rejected` for the same question is not re-read without a reason. Record
every outcome with `make source-outcome URL=<u> OUTCOME=cited:<key>|rejected:<why>|nothing-found|unreadable
[QUESTION=<NNNN>]` (`make reserve KIND=registry KEY=<k> URL=<u>` marks its source `cited:<k>` itself); `make
sources-consulted URL=<u>` (or `KEY=<regex>`) looks a page up without fetching it. A URL cited any other way is archived
with `make archive URL=<u>` ([`downloads.md`](downloads.md)).

## A question has a size (feature 250 D14, GM 2026-09-26)

A question's PROSE stays under 20,000 bytes (`scripts/check-question-size.py`; `make quick` fails on one a
change touched; `make question-sizes` lists all). Its notes and originals are not counted: they are bounded where they
are read (`make check-bundle ... FOR=quote-check` splits them into bundles of at most 12,000 bytes, one agent each). One
over it is split along its topics: a finding stays with the decision it drove; each part is its own question with its
heading and notes; the joins POINT at each other, never restate each other's evidence. A split that would strip a finding
of what it needs is not made - it is raised instead.

## How a section reads (GM 2026-09-29, feature 292)

Every section follows [`STYLE.md`](STYLE.md): a TOPIC under a plain-English title, opening with a short account of what
the thing was and why, then short bullets each led by a bold question or statement; no `Sources:` roster; the GM's
inciting question nowhere. The **`record-style`** agent judges a restyled section against the guide, after `make
style-prepass`. How the maps DRAW a thing is its own page, the question's `.drawing.html`; `make record` writes the links
both ways (`record/xref.py`); its rule of the map may be a `<div class="spec">` holding a list.

## Who the record is for (GM 2026-09-05, feature 180)

The reader is a casual RPG enthusiast at the map, not the next session. They go map -> modal -> "See
references" (the QUESTIONS we asked) -> the answer on the research page -> the sources. So:

- **A heading is the question a reader would ask from the map**, the answer allowed in the same line. The
  bookkeeping (date, feature, task) is an HTML comment on the next line, never in the heading.
- **An anchor is stable**: a renamed heading owes its inbound links - the class entries' `Entry:` tags
  (`scripts/check-entry-headings.py` fails the gate on one that resolves to nothing). A section deliberately not
  written is `research/contents.json#<section> (no dedicated entry - recorded as silent)`.
- A class's explanation names the entries it was written from; that pointer is all that puts a question on a
  modal. The pointer is exactly the questions the modal's statements rest on (`dev/modals.md` M14), and
  `modal-research` checks it both ways and searches the record for a question that answers what the modal leaves open.

## Four labels (GM 2026-09-05, feature 183)

A finding and the modal written from it carry one of four labels: **accurate**, **deviation** (the setting
differs from the history it is based on), **convention** (a glyph drawn at another size or color so the map
reads), **guess**. A convention's modal note says so in the GM's form and ends with the real size or color, or
says it was searched for and not found. The word is the same in the entry, the rule, the code comment and the
map's notes.

## Every reference is a link (GM 2026-09-06, feature 190)

A key is never bare. A document we READ links to the first URL on its registry citation line; one we did not
read (`SUMMARY-ONLY`, `URL: none`, `unfetched` without `READ`) links to its registry entry. The key is the link
text. A work named in prose, or by its author's surname at first mention in a section, is linked the same way;
a read document with no entry gets one first (after searching the registry by URL, percent-decoded, and by the
whole entry), and nothing links to a URL nobody fetched. A new entry records the URL and its READ date. A `Pointers, not
read:` item with no entry, a page named only as silent or unreadable, and an unregistered summary-only or withdrawn item
stay plain; a REGISTERED name is linked whatever label surrounds it. `tests/interactive/test_sources.py` holds it.

## A reference QUOTES what it rests on (GM 2026-09-06, feature 194)

A footnote per assertion - several a sentence when it asserts several things, two on a sentence resting on two
sources - and every note quotes the passage it rests on, VERBATIM including the source's own spelling and dashes (the
house-style guard exempts quoted spans). A foreign passage is quoted in English translation, marked: `「English」
(translated; original: 「原文」)` - the translation follows house style, the original follows the note. English is presumed
and this project is presumed the translator (feature 292, GM 2026-09-29: *"we should presume the source is in English
unless ... stated otherwise ... we should presume that all translations are done by this project unless explicitly stated
otherwise, which allows us to simply say 'translated'"*): an English passage carries no marker, and only a translation by
someone else names them (`translated by <who>`), or one that says more than its language keeps its words; the original
is the checker's anchor, never a second quote. A note quoting several passages joins them with `; ` (a passage that
introduces others ends with `:` before them); the assembly shows them as a list, nested under the introducing one.
**The original is stored apart** (feature 292, GM 2026-09-29): write the note the natural way, original inline, and `make
record` moves each `original: 「...」` run into the question's `NNN-<id>.originals.html` beside its notes, leaving a
placeholder; the assembly puts it back, and the page shows it collapsed behind a click. No check but `translation-check`
reads an original (the quote-check meets one only where the script could not match it on the page). The same form holds
in body prose and in a `SOURCES.html` entry. A section carries no `<p><strong>Sources:</strong> ...</p>` roster
(`tests/interactive/test_no_sources_roster.py`); its sources are the keys its footnotes cite. Nothing is quoted from
memory.

## A citation links to a page where its quote can be READ - or it is not a citation (GM 2026-09-06, feature 195)

A note is one of THREE forms:

- **CITATION**: `<a href="https://..."><code>key</code></a> - 「passage」 (gloss)` - the link a public page on which
  the passage can be read: the paper's public PDF, not its abstract; the full-text view, not a library landing page;
  the original-language page, not an English rendering that is on no page. Never a paywall, a login wall or a
  search summary.
- **ABSENCE**: `no publicly readable source<!-- searched YYYY-MM-DD: what was tried -->` then what the search found,
  visible - a list of `<span class="pass">` items (`pass sub` nested) where it is several things (feature 292, GM
  2026-09-29: the search log is for a session, so it is a comment; the reader sees the one opening sentence
  `record/absence.py` keeps, which `make record` puts in place of the marker, and the findings). The old form, the
  search in visible parentheses, still reads and is converted by the sweep. An absence note supports only a stated silence
  or a GUESS of our own - never a claim of what a named page says that no one here could read (feature 292, GM
  2026-09-30); such a claim is read and quoted, or removed. No key, no URL; the
  assertion stands, honestly labeled; the registry entry stays, marked *Not cited*. It may carry `settled DATE`
  only after two independent passes on different dates, the second using a tool the first lacked, and it re-opens
  on anything that changes what can be read. Settling is never obligatory.
- **GROUNDS**: `no source is owed: <reason>` from a CLOSED list - `measured on our own maps`, `the record's own
  silence`, `follows from the definitions`, `physical necessity`, `a drawing convention`, `this project's
  decision`. NEVER for a claim about how a place was built, farmed, planted, governed or lived in, nor for a
  labeled GUESS about the physical world - those owe a citation or an absence note. A note may name more than one
  reason; using one of the four not yet exemplified on an existing note takes a written argument at that note's page. A
  note converted from an absence note keeps its search in an HTML comment.

The one exception, by the GM's ruling: the GM's own campaign notes are canon and keep their registry link; the registry
entry they open cites the notes on GitHub (feature 307, GM 2026-10-02): the file at
`https://github.com/EliAndrewC/l7r/blob/master/setting/<file>.md`, and each quoted section followed by its heading's URL,
its anchor by GitHub's rule (`sources.github_anchor`). The build makes every bare URL on a citation line a link that
opens in a new tab, so a citation line is written with its URL in plain text. A page the container cannot fetch is not
thereby unreadable: a source only the GM can fetch is read from the GM's archived copy and asked for with `make
download-add` ([`downloads.md`](downloads.md)).

`tests/interactive/test_footnotes.py` holds the mechanical half. The **`quote-check`** agent holds the rest -
per note VERBATIM / SUPPORTS, per section the assertions with no footnote - after `make quote-verbatim`, on
the units `make record-owed` names, its verdicts recorded with `make record-checked` and in the task (`quote-check
confirmed`).

## Written for the reader (GM 2026-09-07, feature 209)

1. **A term the reader would not know is a glossary tooltip** - one glossary for the map and the record, each
   definition written from the record's own text; nothing is wrapped by hand. A term nothing uses fails the gate.
2. **A note for a session is an HTML comment**: the `Grounds:` and `Evidence:` fields, a feature, a task, a spec,
   a test, a make target, an engine identifier, a fetch verdict. Visible: a source key's link, a decision and the
   alternatives it declined - told as the project's choice, never as a GM ruling (feature 292, GM 2026-09-29: the
   ruling, its date and words go in an HTML comment beside it) - the honest label on a claim (a GUESS; that a search
   found nothing - its date and terms are a comment).
3. **No history of the document in the document**: no "used to say", no correction dates, no "re-sourced by".
   A changed finding is REWRITTEN; git holds the old wording. An absence note's provenance ("the passage came from
   `key`") is an HTML comment inside its `<li>`.
4. **A question a reader would not think to ask says why it is here** (GM 2026-10-02, feature 311): an intro paragraph,
   `<p class="intro">`, first after the heading - what Rokugan or the map has, and that the research below shows what the
   historical record holds instead. It cites nothing and adds no claim the findings below do not carry. The rule and its
   form: `STYLE.md` section 2; the **`intro-check`** agent judges it.

`tests/interactive/test_record_format.py` holds the mechanical half; the **`record-format`** agent (after
`make record-prepass`) the rest - VOCABULARY, SESSION NOTE, HISTORY - on the questions whose visible words
`make record-owed` says changed. The registry is not under rules 2 and 3.

## A question's notes stand at its foot; every cited work says what it is (feature 301)

- A note is written in the notes file of the page that cites it (a note two pages cite is in both); the site's page for
  each question carries the notes it cites, numbered from 1, then the works they cite (the GM, 2026-10-01: *"start the
  footnotes counting at one every time ... include the footnotes and reference sources at the bottom of each individual
  page"*); the single page numbers once through the whole record.
- **A registry entry explains its work once**: after the citation line, `<p><em>What it is:</em> ...</p>` and
  `<p><em>Why it applies, and its limits:</em> ...</p>`, each one to three sentences, honest about date, place
  and method. A cited key without both fails the build; every list of works cited is derived from them.
- **A `Used for:` line names each section it serves as a LINK**, never a page file name: `(<a
  href="contents.json#religion-and-the-dead">Religion and the dead</a>)`, the section's id from `research/contents.json`
  and its title as the text. The build links it to the section's page, or to its place on the single page, and refuses
  an id that is not a section (GM 2026-10-02).
- **Every entry is TAGGED, and its limits are its own** (feature 305, GM 2026-10-02: labels whose tooltips carry *"the
  standardized explanation of the strengths and limitations inherent to the category of source, in addition to the
  specific explanation"*). The entry's last line is `<!-- tags: period=a[,b]; region=x[,y]; kind=k -->`, values from
  `research/source-tags.json`, the first of each facet primary; the GM's campaign notes carry none. PERIOD follows the
  evidence the record takes, not the publication (a modern study of Edo registers is `premodern`); the cut-offs by region
  are in the period explanations. `research/source-sections.json` groups every list of works by the primary tags, so
  regrouping is an edit there alone. The labels carry the category's standard limits, so "Why it applies, and its limits"
  states only what is SPECIFIC to the work - never "it is a tertiary article", "a tourism page citing no study", "a
  present-day count used as an anchor", said generically. `make reserve KIND=registry KEY=<k> URL=<u> TAGS="period=..;
  region=..; kind=.."` writes the marker; `make record CHECK=1` refuses an entry untagged, tagged with an unknown value,
  or whose tags no section takes. A vocabulary edit is followed by `make source-tags-contract`.
- **A source is judged before it is used**: the **`source-applicability`** agent on every write-up `make record-owed`
  names, and BEFORE a source's numbers, claims or details reach a map or a rule (a physical task's fifth box). A
  NOT-APPLICABLE source is recorded and listed for the GM, and the assertions resting on it keep their label until the
  GM rules.

## The record IS HTML (feature 194)

The record is hand-authored HTML: the questions under `research/questions/`, the registry's fragments under
`research/sources/`; a page's heading id is its anchor and its file's slug. `make record` builds the site from them
(`record/site.py`): each page's `<head>` links the site's copy of `assets/record.css`, `site.css`, `glossary.js`,
`nav.js`, `site.js` and `record.js`. These rule files stay Markdown. The page mechanics are in
[`../l7r/diagram/interactive/CLAUDE.md`](../l7r/diagram/interactive/CLAUDE.md).

## The record is the ONE home per topic (GM 2026-09-12, feature 229)

Per question a page holds the finding, the decision it drove (what was chosen and why, the alternatives declined - the
GM's ruling, its date and words in an HTML comment, feature 292), and - for a rule no generator yet encodes - the
**specification**, `<p class="spec"><strong>The rule the map follows:</strong> ...</p>`, in real feet at the tier's scale
(the pixel figure in a comment beside it), naming no engine identifier or check in its visible text, and - where it rests
on no finding - saying which it is: a convention, a calibration against the drawn exhibits, or a guess; it is retired once
a generator encodes the rule with its reasoning. A rule the engine encodes with its reasoning is not written twice; a
reason its code comment lacks goes on the page, and the comment points at the anchor. Nothing names a retired
`settlements/*.md` rule file (`tests/interactive/test_record.py`).
