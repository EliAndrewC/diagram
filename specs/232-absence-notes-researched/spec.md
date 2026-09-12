# Feature 232 - every absence note gets a real research pass

**Status**: DRAFT (awaiting `spec-fidelity`)
**Request**: [`request.md`](request.md), the GM's words verbatim, 2026-09-12.

## What the GM asked for

Run down all of the absence notes. Do however much research is needed to find sources and citations for
them, in the normal way, under the normal rules. Where a source is probably readable by a person but not
by this session - a paywall, a 403, a PDF that will not open to a reader of text - list it for the GM,
who will fetch it and save it in the usual place.

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

**FR-001 Every one of the 162 is worked.** Not a sample and not the blocked 31 only. The unit of work is
the NOTE, and each ends in exactly one of four states, recorded per note in `research.md` R1:

1. **CITED** - a readable page carrying a supporting passage was found. The note becomes an ordinary
   footnote: the key, its link, and the passage quoted verbatim, in English translation where the source
   is not in English, with the original following as the checker's anchor (feature 202).
2. **STILL ABSENT** - the pass found nothing readable. The note is REWRITTEN with today's date and what
   this pass actually searched, replacing the older search.
3. **FOR THE GM** - a specific document is named, is probably readable by a person, and this session
   cannot open it. The note stays an absence note naming that document, and the document goes on the
   list in FR-005.
4. **CONTRADICTED** - a readable source says the opposite. See FR-004.

**FR-002 Every new source goes through the full normal procedure**, in this order, with nothing skipped
because the feature is large: `source-reader` reads the page and returns the passage; the session writes
the footnote and the registry entry from the returned quotes; `source-applicability` judges the source
and its two write-ups BEFORE its numbers or claims reach a page; `quote-check` confirms the passage is on
the page and supports the assertion; `record-format` checks the changed entry reads for the reader. A
source that cannot be read is not cited, whatever it is known to say.

**FR-003 A registry entry is written for every new key** - the citation line with its URL, the "What it
is" write-up and the "Why it applies, and its limits" write-up - and `make citations` derives the works
lists and hover scripts.

**FR-004 A CONTRADICTED claim is corrected in the RECORD and reported to the GM; the MAPS are not
changed under this feature.** Correcting a sentence the sources contradict is what the research pass is
for and is in scope. Changing what a generator draws is not what was asked for, may move maps, and owes
its own feature; each is listed in the closing report with what the source says and what the map does.

**FR-005 The list for the GM.** `for-the-gm.md`: every document this session judges a person could
probably reach and it could not, with its title, author, date, identifier (DOI, ISBN, handle), the URL
tried, what blocked it, the assertion it would support, and how much it would change. Ordered by what it
buys the record, not alphabetically. The GM saves what they find in the usual place
(`/host-l7r-repo/academic-sources/`) and this session reads from there.

**FR-006 Nothing is cited that was not read**, and no absence note is quietly deleted. A note may only
leave the record by becoming a citation that passes `quote-check`.

**FR-007 The gate stays green and the record's own tests hold** - every link resolves, every cited key is
a link to the right target, every registry key carries both write-ups, the committed citations scripts
equal their derivation, and no page states a count that is stale.

## Success criteria

- **SC-001** All 162 notes are accounted for in `research.md` R1, one row each, with its final state.
- **SC-002** Zero notes are deleted without becoming a citation; the count of absence notes falls only by
  the number that became citations.
- **SC-003** Every new registry key has both write-ups and a `source-applicability` verdict.
- **SC-004** `quote-check` returns no unresolved finding on any page this feature changed.
- **SC-005** `for-the-gm.md` exists and every entry on it names a specific document, not a topic.
- **SC-006** `make done` green; `make page-check` green.

## Out of scope, deliberately

- Changing any map, any generator, any drawn rule or any specification (FR-004).
- Mode A's operative document. The GM ruled the same day that `buildings.md` stays; its research page's
  two absence notes are IN scope, because the GM said all of them, but the rule file is untouched.
- Adding new claims. This feature sources what the record already asserts; it does not extend it.

## Decisions recorded

- **D1 The unit is the note, not the page.** A page-by-page sweep would let a page with two hard notes be
  declared done because its other twelve were easy. Each note carries its own verdict.
- **D2 The blocked 31 are not a separate phase.** They are worked in order with the rest, because a
  blocked source is often not the only one that would carry the passage, and the cheapest outcome is
  finding another page that is readable.
- **D3 A search that found nothing is REWRITTEN, not left.** An absence note's whole value is the date
  and what was tried; leaving a 2026-09-06 note untouched after a 2026-09-12 pass would misreport this
  feature's own work.
- **D4 Reading runs in background agents, never in the session's turn** (GM 2026-08-28). One hung fetch
  in a foreground batch blocks the whole turn.
