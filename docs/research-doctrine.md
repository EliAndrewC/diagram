# The research doctrine, as the GM ruled it

*Project reference, split out of [`../CLAUDE.md`](../CLAUDE.md) so it is loaded on demand rather
than in every session's context. CLAUDE.md keeps the six rules in one line each; this file is the
full record with the GM's words. The operative form of the citation rules - the footnote shape, the
citations pages, the download list - is
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
  `research/SOURCES.html` with what each was used for and the URL where it can be read (`URL: none -
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
  `quote-check` agent confirms the quote is on the page, supports the assertion, and that every
  relevant assertion has one, before the entry lands. A foreign-language passage is quoted in
  English translation, marked as one (GM 2026-09-07: *"for foreign language things we want to quote
  the English translation rather than the original text but we also want to note that it is a
  translation"* - the note names the language and the translator, the original follows the note as
  the checker's anchor). The one exception is the GM's own campaign notes, canon rather than
  evidence (GM 2026-09-07: *"it is correct to make L7R setting notes an exception to the citation
  rule, so that should indeed be a documented exception"*).
- **The record is HTML** (`research/*.html`, hand-authored), the footnotes on a CITATIONS PAGE
  beside each research page (`research/citations/<name>.html`, the research page's hover reading a
  derived `citations/<name>.js` that `make citations` writes), and the maps link to it locally.
  Every cited work's registry entry says what it is and why it applies with its honest limits - two
  write-ups, written once and derived into the works list at the top of every citations page that
  cites the work - and a source is judged by the `source-applicability` agent when its write-ups
  land and BEFORE a session integrates its numbers into a map (GM 2026-09-07: *"whatever subagent
  check we create in order to justify whether a source is applicable to be used in the creation of
  our diagrams, that subagent check should also be run when we first begin to make use of the source
  prior to integrating its numbers or claims or details into our maps."*).
- **A source only the GM can fetch goes on THEIR download list, in THEIR format, appended at the
  end** (GM 2026-09-14: *"each source has a link to what you think the URL is and a link to the
  Google search as a backup where the Google search should uniquely identify the resource ... saved
  in markdown in this format since that is much easier for me to find things"*):
  `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md`, one markdown entry per work with the guessed
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
  glossary tooltip exactly as on the map (one glossary, `interactive/glossary.py`, derived to
  `research/assets/glossary.js` by `make glossary`); anything addressed to a session - `Grounds:`,
  `Evidence:`, a feature number, a task id, an engine identifier, a fetch verdict - is an HTML
  comment; and nothing in the entry says what it used to say or when it was corrected (*"we can look
  it up in our version control history"*). The `record-format` agent checks all three on every
  changed entry beside `quote-check`; `tests/interactive/test_record_format.py` holds the mechanical
  shapes. The sensibility in full: the research directory's `CLAUDE.md`, "Who the record is for".
- **Record a decision to ACCEPT a limitation, and the alternatives that were declined (REQUIRED)**
  (GM 2026-08-17: *"we should always document this kind of decision... that way if we look it up
  later, we'll know it was a deliberate decision"*). The rule above covers a decision that produced a
  rule; this covers the other kind - where we looked at something imperfect and deliberately chose
  to leave it. Undocumented, those are indistinguishable from bugs, and the next session "fixes"
  them. So write down **what was accepted, what it costs in observable terms, which alternatives were
  priced, and who chose** - the rejected options matter as much as the chosen one, because they are
  what stops the question being reopened from scratch. Worked example:
  [`research/water.html`](../.claude/skills/diagram/research/water.html#what-drawing-at-true-size-left-open)
  "What drawing at true size left open" - the GM asked why a channel did not visibly narrow, the
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
