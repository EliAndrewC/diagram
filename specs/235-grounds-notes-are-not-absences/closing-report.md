# Feature 235 - closing report

## What the GM asked

*"what can we do in the future to not label things like decisions that we have made as 'absent'? because
that is very confusing. Like, something being 'absent' implies that there is a action that we need to
take. So, I mean, the number of things in that category should eventually be zero. But if we're counting
things that are not actually problems in a category that is meant to denote problems, then we're just
gonna keep getting confused. Right?"*

## What shipped

**A third footnote form.** A note may now read `no source is owed: <reason>`, where the reason is one of
six on a closed list. It means there is nothing to find, so the note is not a work item and does not
count in the backlog. The absence note is unchanged except for FR-004's addition.

**A settled state on the absence note**, so the category is one a claim can LEAVE. The GM's "should
eventually be zero" could not happen under the old rule: a claim the record is genuinely silent about
kept an open absence note for ever, and the backlog had a permanent floor of work nobody could do. An
absence searched to exhaustion by two dated passes, each naming its tools and the second naming one the
first lacked, carries `settled DATE` and leaves the count. It ships with **no instance**, deliberately:
feature 232's second pass found readable sources for 90 of 162 notes a first pass had called hopeless, so
against that base rate settling is never obligatory and a note left open costs nothing but an honest
number.

**Four checker surfaces taught the form BEFORE any note was written** - the constitution's Principle XII
(amended, v2.26.0, with the GM's words as the ruling), `research/CLAUDE.md`, the footnote test's
classifier AND its consumer, and the `quote-check` agent. Writing a grounds note first would have turned
the gate red and looked like the feature failing rather than the checkers not knowing the vocabulary.

**A census, because nothing counted footnotes at all.** `make footnote-census` prints cited / grounds /
ABSENT / settled per page and in total, sharing the engine's own classifier so the gate and the tool
cannot disagree. Its ABSENT column is the backlog and the only number anybody has to act on.

## The numbers

| | cited | grounds | ABSENT | settled |
|---|---|---|---|---|
| before | 969 | 0 | 84 | 0 |
| after | 969 | 1 | 83 | 0 |

## What the record turned out to contain, which is the honest headline

A triage proposed **eighteen** notes for reclassification. Reading the pages gave five. A `spec-fidelity`
round that went to the files rather than trusting that reading gave **one**. So:

- **one** note converts (`cities/sizing.html` fn-2, `measured on our own maps`),
- **three** were argued at their own pages and all three REFUSED, each argument left at the note,
- **fourteen** were confirmed as open absences, each carrying a comment naming which clause of FR-003
  keeps it there so the next reader does not re-open it.

The labeling defect the GM identified is real and worth a mechanism. Today's record contains almost none
of it - which is itself the answer to "how many of these are actually problems". What the feature buys is
the future: the next session that meets a sentence with nothing to find has a word for it.

**And the way the triage went wrong is the same failure the whole body of work exists to fix.** It was
built from an extraction that took the sentence nearest each footnote marker and classified from those
extracts without opening the pages. An extraction over HTML is evidence about the extractor.

## Two sentences moved out of the reader's text

`cities/river-cities.html` carried *"Do not 'fix' it."* and `cities/defenses.html` *"which is why it is
really a rule about what may NOT stand there rather than a rule about a road"* - the record explaining
its own rule to a session. Both are HTML comments now, the reader-facing half of the defenses sentence
stays, and **both footnotes stay too**, as open absence notes: they annotate the neighboring sentences,
which are unsourced claims about the world. An earlier draft of the spec would have deleted them, which
is the GM's complaint inverted.

## OFFERED, not applied: three corrections to `research/README.md`

A README is the GM's to write (constitution XVII), and the authorization given on 2026-09-12 was for one
specific correction already put to them, not a standing one. So these are offered:

1. **The binary.** The README says a new entry *"cites, or it says what was searched and not found"* -
   the same two-way choice this feature just replaced. The sentence could read: *"A new entry never says
   `not recorded`: it cites, it says what was searched and not found, or - where there is nothing to find
   because the sentence is not a claim about the world - it says no source is owed and names the reason."*
2. **A rule feature 195 superseded.** The same paragraph says a page that could not be read has its claim
   labeled `SUMMARY-ONLY`. Since 2026-09-06 a claim taken from a source that could not be read is not
   cited at all, and the label is retired.
3. **A pointer to a file that no longer exists.** The same paragraph names `SOURCES.md`'s queue. The
   registry is `SOURCES.html`, and that queue is gone. (No test catches this one: the retired-Markdown
   sweep exempts the README by name.)

## What this feature deliberately did NOT do

- **Settle any note.** The mechanism ships with no instance; settling one needs two dated passes and the
  judgment belongs to that note's own research.
- **Use any of the three barred reasons.** `this project's decision`, `a drawing convention` and
  `physical necessity` have no verified instance in the record and may not be used to reclassify an
  existing note. They exist for the future, which is what the GM asked about.
- **Touch the four evidence classes.** Accurate / deviation / convention / guess are unchanged; this is
  about the FOOTNOTE's kind.
