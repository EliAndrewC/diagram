# Feature 232 - every absence note gets a real research pass

**Status**: DRAFT (spec-fidelity round 1 applied; awaiting round 2)
**Request**: [`request.md`](request.md), the GM's words verbatim, 2026-09-12.

## What the GM asked for

Run down all of the absence notes. Do however much research is needed to find sources and citations for
them, in the normal way, under the normal rules. Where a source is probably readable by a person but not
by this session - a paywall, a 403, a PDF that will not open to a reader of text - list it for the GM,
who will fetch it and save it in the usual place.

**"Absence notes" is this feature's READING of a dictated phrase.** The GM wrote "Epson's notes"; the
argument for reading it as "absence notes" - that their message answers feature 229's closing report
paragraph for paragraph - is set out in [`request.md`](request.md), and everything below depends on it.

## What an absence note is, and why there are 162 of them

A footnote in this record either QUOTES a passage and links a page where the passage can be read, or it
is an ABSENCE note: no key, no link, and a plain statement of what was searched and when (constitution
XII; GM 2026-09-06, feature 195). The claim is still asserted - the maps draw it - but the sentence says
what stands behind it.

Feature 229 migrated the retired rule files into the record and held every migrated claim to that
contract for the first time. The rule files had named sources in prose, without quotation and usually
without a link, so 108 of its 176 new footnotes came out as absence notes. With the notes that predate
it, the record carries **162**, over **17** citations pages. The inventory is
[`inventory.json`](inventory.json), built from the pages themselves rather than by hand.

| | count |
|---|---|
| absence notes in the record | 162 |
| of those, naming a source whose fetch was BLOCKED (403, paywall, login, an unreadable PDF) | 31 |
| of those, recording a search that found no page to name | 131 |

## Requirements

**FR-001 Every one of the 162 is worked, and each ends in exactly one of four states**, recorded per note
in `research.md` R1. Not a sample, and not the blocked 31 only. The unit of work is the NOTE.

1. **CITED** - a readable page carrying a supporting passage was found. The note becomes an ordinary
   footnote: the key, its link, and the passage quoted verbatim, in English translation where the source
   is not in English, with the original following as the checker's anchor (feature 202).
2. **STILL ABSENT** - the pass found nothing readable. The note is REWRITTEN with today's date and what
   this pass actually searched, replacing the older search. **This state has a floor; see FR-002.**
3. **FOR THE GM** - a specific document is named, is probably readable by a person, and this session
   cannot open it. The note stays an absence note naming that document, and the document goes on the
   list in FR-005.
4. **CONTRADICTED** - a readable source says the opposite. See FR-004.

**FR-002 STILL ABSENT IS EARNED, NEVER DECLARED.** The GM's words are *"do however much research you need
to do"*, and a feature that may rewrite 131 notes to "searched today, found nothing" without reading
anything would satisfy every other requirement here while doing none of the work. So a note may reach
state 2 only when, and `research.md` R1 records for it:

- the **searches actually run**, as query text, not as a description of searching;
- the **candidate pointers those searches returned** - title, author and URL - or the explicit finding
  that they returned none;
- and that **every candidate judged plausible was attempted THROUGH `source-reader`**, with its verdict.
  A search summary is a pointer and never a source (constitution XII), so a candidate dismissed from a
  snippet without a fetch does not count as attempted.

Everything a pass READS goes through the normal procedure in this order, nothing skipped because the
feature is large: `source-reader` reads the page and returns the passage; the session writes the footnote
and the registry entry from the returned quotes; `source-applicability` judges the source and its two
write-ups BEFORE its numbers or claims reach a page; `quote-check` confirms the passage is on the page
and supports the assertion; `record-format` checks the changed entry reads for the reader.

**FR-003 The registry is carried forward at BOTH ends.** A new key gets its citation line with its URL,
its "What it is" write-up and its "Why it applies, and its limits" write-up. And the OLD key - the
registry already holds 68 entries of the feature-195 "Not cited ... no publicly readable page carries the
passage" form, each with a `Used for:` line - **stays as the record of the search and is brought up to
date**: its "Not cited" line says what this pass found, and its `Used for:` line stops claiming what a
new source now carries. A feature that landed a sourced footnote beside a registry still declaring the
same claim unsupported would have made the record contradict itself. `make citations` then derives the
works lists and the hover scripts.

**FR-004 A claim a source CONTRADICTS is corrected in the RECORD - findings, rule text and specification
alike - and the divergence from the maps is stated where a reader meets it.** Since feature 229 the
research pages hold the rule, and for a tier no generator draws yet they hold the specification too, so
"the record" here means every one of those, and correcting them is what a research pass is for.

What is NOT changed under this feature is what a generator DRAWS. That is an engine change: it moves
maps, and it owes its own spec-kit feature, a settlement review and a gate. So where a corrected finding
no longer matches what a map draws, the page **states the divergence in reader-facing text** - the record
must never assert a rule the maps do not follow, and a page that quietly misdescribes its own map is the
one failure constitution XII names. Each divergence is also a row in the closing report (FR-005).

**FR-005 Two artifacts for the GM, named here so they cannot be forgotten.**

- `for-the-gm.md`: every document this session judges a person could probably reach and it could not,
  with its title, author, date, identifier (DOI, ISBN, standard number), the URL tried, what blocked it,
  the assertion it would support, and how much it would change. Ordered by what it buys the record. The
  GM saves what they find in the usual place (`/host-l7r-repo/academic-sources/`) and this session reads
  from there.
- `closing-report.md`: what the pass changed, and every CONTRADICTED claim with what the source says,
  what the map currently does, and whether the divergence is now stated on the page.

**FR-006 Nothing is cited that was not read, and no absence note is quietly deleted.** A note leaves the
record only by becoming a footnote that cites a source and passes `quote-check` - including a note whose
claim was corrected, which leaves as a citation of the contradicting source.

**FR-007 The gate stays green and the record's own tests hold** - every link resolves, every cited key is
a link to the right target, every registry key carries both write-ups, the committed citations scripts
equal their derivation, and no page states a count that is stale.

## Success criteria

- **SC-001** All 162 notes are accounted for in `research.md` R1, one row each, with its final state.
- **SC-002** Zero notes are deleted without becoming a citation; the count of absence notes falls only by
  the number that became citations.
- **SC-003** Every new registry key has both write-ups and a `source-applicability` verdict, and every
  old key whose claim was sourced or corrected has its "Not cited" and `Used for:` lines brought forward.
- **SC-004** Every footnote this feature changed carries its own `quote-check` confirmation, recorded per
  footnote. A footnote without one does not land.
- **SC-005** Every STILL ABSENT row in R1 carries its queries, its candidate pointers and a
  `source-reader` verdict per plausible candidate (FR-002). A row without them is not done.
- **SC-006** `for-the-gm.md` exists and every entry names a specific document, not a topic.
- **SC-007** Every CONTRADICTED row in R1 appears in `closing-report.md` with what the source says and
  what the map currently does, and its divergence is stated on the page itself.
- **SC-008** `make done` green; `make page-check` green.

## Out of scope, deliberately

- **What a generator draws.** Correcting the record is in scope (FR-004); changing a map is an engine
  change owing its own feature, its own review and its own gate.
- **Mode A's operative document.** The GM ruled the same day that `buildings.md` stays; `buildings.html`'s
  two absence notes ARE in scope, because the GM said all of them, but the rule file is untouched.
- **Adding new claims.** This feature sources what the record already asserts; it does not extend it.
- **Guess-labeled claims that carry no absence footnote.** Feature 229's closing report named two numbers
  - 113 guess mentions and 108 absence notes - and the GM asked for the NOTES. A claim the record labels
  a guess in prose, with no footnote of its own (`homesteads.html`'s persimmon and firewood placement are
  the worked examples), is left alone. Decided here rather than at implementation time; it is a clean
  follow-on feature if the GM wants it.

## Decisions recorded

- **D1 The unit is the note, not the page.** A page-by-page sweep would let a page with two hard notes be
  declared done because its other twelve were easy. Each note carries its own verdict.
- **D2 The blocked 31 are not a separate phase.** They are worked in order with the rest, because a
  blocked source is often not the only one that would carry the passage, and the cheapest outcome is
  finding another page that is readable.
- **D3 A search that found nothing is REWRITTEN, not left.** An absence note's whole value is the date and
  what was tried; leaving a 2026-09-06 note untouched after this pass would misreport the feature's own work.
- **D4 Reading runs in background agents, never in the session's turn** (GM 2026-08-28). One hung fetch in
  a foreground batch blocks the whole turn.
- **D5 `inventory.json`'s `blocked` flag is descriptive, not a phase boundary.** It is a keyword split and
  two rows sit oddly in it (`cities/river-cities.html` fn-15, `vegetation.html` fn-90 read as searches
  that found nothing rather than fetches refused). Nothing depends on it: FR-001 works all 162 and D2
  refuses to phase them.
