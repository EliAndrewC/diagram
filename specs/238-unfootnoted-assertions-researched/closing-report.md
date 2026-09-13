# Feature 238 - closing report

## What the GM asked

> please start that other research pass for all of those assertions about the world that do not carry a
> footnote, but that seem like things that should require a citation.

and then, once the size of it was known:

> So why don't we close out all of the low hanging fruit, which is to say the things that we think we can
> get done with just a few passes and not another really deep and extensive round of searching and such.
> and then we can close out this feature and open a successor for the rest.

## What shipped

**The inventory, which is the thing the successor could not do without.** Four independent `quote-check`
readers over all nineteen research pages named **695 sentences** that assert something about how a place
was built, farmed, governed or lived in and carry no footnote. Feature 232 had estimated "roughly 180
across the thirteen pages" - **low by about a factor of four**, and not carelessly: that number came from
six agents noticing these in passing while doing a different job, and a count made in passing counts what
was noticed. R6 gives every one of the 695 a disposition; R7 says which of them this feature closed, so
the successor filters a list rather than re-reading the record.

**Every item that needed no new reading, on every page.** 142 bare inline `(unsourced)`-class markers
moved into absence notes at their own assertions; the roster-hidden claims on `urban-features` and
`buildings`; the six sections that disowned a figure while carrying no footnote at all; two whole pages
closed on the reading alone; the caravan inn.

**Twelve defects, of which two changed what an entry argues.** These are the class where the record
stated something WRONG rather than merely unsupported, and they are worth more per hour than the gaps.

## The numbers

| | |
|---|---:|
| sentences the readers named | 695 |
| sections read | 282 |
| pages read | 19 |
| inline markers converted to notes | 142 |
| notes written by hand beside them | 23 |
| defects corrected | 12 |
| new registry keys, all judged | 3 |
| pages closed outright | 2 |
| items left to the successor | the `CITE` remainder, ~600 |

## The two findings that changed an argument

**The Wagner workforce figures said the opposite of what the record built on them.** The entry read "200
charcoal producers alongside 200 furnace-tenders and 300 miners" and concluded the fuel workforce was as
large as the furnace workforce. The source says "more than 200 furnace tenders, 300 miners, and 200
'water-carriers' and charcoal producers" - one figure covering two trades, against a furnace figure
explicitly "more than". The comparison does not survive, and it was leaned on in three places. Worse, the
record used that staffing as its picture of ONE concentrated complex while the same paragraph of the
source rejects exactly that reading.

**The two-site arrangement the maps draw is attested Chinese practice, not a Japanese override.** The
entry's "THE DISCLOSED DIVERGENCE" had the Chinese arrangement as one site and ours as a Japanese
departure. Both arrangements are in the same work: the single site is the seventeenth-century treatise's,
and Guangdong's large-scale sector is the other - ironworks in the forested mountains, pig iron shipped
downriver to be converted and cast at an industrial town. The heading is now "WHY THE TWO SITES ARE NOT A
DEPARTURE".

## What the checks caught that the session got wrong

Three of the twelve defects were this session's own, and each was caught by the check that exists for it.

- **`source-applicability` caught an inference written flat as a fact** - that a hatago "took travelers on
  foot and by palanquin" - in a limits paragraph, in the first citation this feature registered, in a
  feature whose entire subject is inferences written flat. It was load-bearing: the disqualifying
  conclusion was drawn from it.
- **`quote-check` refused a GROUNDS note** on the burakumin quarter. The sentence asserted what a walled
  city did and why, which feature 235 bars a grounds note from carrying, and the session had written a
  warning about that very risk into the note's own comment before making the mistake.
- **A quotation of a damaged text layer, fixed halfway.** The degree signs in a scanned page's quote were
  apostrophes from a broken extraction; the session corrected them and then DEFENDED a second artifact of
  the same kind in the same sentence. Two readers disagreed about the glyph; looking at the page image
  settled it, and both artifacts are now corrected in both notes that quote the passage.

**And two reader findings did not survive checking**, which is the other half of the same lesson: an agent
reported our quotation as differing from a paper when the PDF confirms our wording (the agent dropped a
word), and another returned CONTRADICTED on a claim that was in this session's prompt rather than on the
page. **An agent's finding is a lead, not a verdict.**

## What `spec-fidelity` refused, and why it matters

The amendment's first draft cut the scope **by page** where the GM cut it **by cheapness**. The
roster-disclosure class is cheap on every page - the search is already done and dated - and a page
boundary swept all of it to the successor along with the expensive items sitting beside it. The review
named the cause exactly: the session drew the line at its own unit of work. FR-012 now cuts by item, and
the recut is why 142 markers and six disowning sections were worked instead of two empty pages.

## What is left open, honestly

- **About 600 `CITE` items**, each needing its own reading. This is feature 242, and R7 is its work list.
  Most of them have **never been searched** - they are not failed hunts, and the successor should not
  read them as such.
- **Fifty-one redundant roster disclosures.** The label now sits at the assertion; the roster line still
  carries it too. Cosmetic, fifty-one edits, no change of meaning in any - deferred by VOLUME and named
  here because FR-012 requires that rather than a silent page rule.
- **Two items the record cannot settle without the GM**: whether the caravan inn's story count should
  become a knob now that a two-story Japanese highway inn is attested (the adjudication refused the knob
  for this glyph, and the GM may still want it), and the Xuxiebian site name, which a second full search
  of both Wagner works confirms is in neither.
- **`presentation.html` and `settlements.html` are done and will not reappear** in the successor.

## The entry-drift discharge

The conversions moved 27 modal pairs. Every one is a label-only change: a marker left the prose and a note
arrived at the assertion, and **no finding moved in any of them**. None touches the sections where a
finding DID move - the Wagner iron work, the Daoism source swap, the inn - because no modal is written
from those. That is the case feature 234 provides one recorded sweep reason for, and it is taken.
