# Feature 242 - cite the unfootnoted assertions

**Status:** DRAFT - not reviewed. Feature 238 claimed this number and wrote this outline so the work list
would not be lost; the spec itself is the next session's to finish and put to `spec-fidelity`.

## Summary

Feature 238 read all nineteen research pages with four independent `quote-check` agents, found **695
sentences** that assert something about how a place was built, farmed, governed or lived in and carry no
footnote, classified every one of them, and worked every item that needed no new reading. This feature is
the remainder: **about 600 `CITE` items, each needing its own `source-reader` pass** before a footnote can
be written.

## What this feature does NOT have to do

**It does not re-read the record.** That is the whole reason 238 finished the inventory rather than
leaving it half-built. Its inputs are:

- `specs/238-unfootnoted-assertions-researched/research.md` R3 (the four shapes), R6 (the classification),
  R6a (where the counts come from) and **R7 (the closed list - what 238 worked, so this feature owns the
  reader-report items R7 does not name)**;
- the four verbatim agent reports under `specs/238-unfootnoted-assertions-researched/reader-reports/`,
  which are the authority on the identity of each item.

## What it must not repeat

Feature 238's closing report records three mistakes its own checks caught, and each is a trap this
feature will walk into again if nobody says so:

- **An inference written flat as a fact**, inside a limits paragraph, in a feature whose subject is
  inferences written flat. `source-applicability` caught it.
- **A GROUNDS note carrying a claim about how a place was built or governed.** Feature 235 bars it;
  `quote-check` refused one anyway. A grounds note is for a decision, a convention, a definition or a
  physical necessity, and for nothing else.
- **A quotation of a damaged text layer.** A scanned page's broken extraction is not what a reader sees.
  Where a quote comes from a PDF, look at the page image before trusting the characters.

And two agent findings that did NOT survive checking: **an agent's finding is a lead, not a verdict.**

## The shape of the work, as 238 measured it

- Most of the ~600 have **never been searched**. They are not failed hunts, and an absence note on one
  should not imply a hunt that never happened.
- The order is not the item count. It is value: a claim the record states WRONGLY costs a reader more
  than one it states without support.
- The GM's downloads live in `/host-l7r-repo/academic-sources/`, and
  **`TO-DOWNLOAD.md` Part 4 is where this feature appends what it cannot read** - at the END, never in
  the middle, each with a clickable link. 238 closed with nothing to add there; this one will fill it.

## Also inherited

**Fifty-one redundant roster disclosures** (238 R7): sections whose `Sources:` line still carries a
disclosure the assertion's own note now carries. Cosmetic, no change of meaning, deferred by volume.

**Two items only the GM can settle**, carried forward from 238's closing report: whether the caravan
inn's story count should become a knob now that a two-story Japanese highway inn is attested, and the
Xuxiebian site name, which a second full search of both Wagner works confirms is in neither.
