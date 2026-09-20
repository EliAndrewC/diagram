# Research: where a research page's bytes actually go

Every figure in `spec.md` points at a finding here. All four were taken on 2026-09-20 at `9d11c6e2`
("256: the plan's last authority phrase corrected"), before any of this feature's work, and each
re-runs as one command:

    python3 specs/258-split-the-record-into-per-entry-files/measure.py R1

`R1` and `R4` read the record and re-run anywhere. `R2` and `R3` read `~/.claude/projects/`, this
machine's transcript store, which is not in the repository: they re-run only while those transcripts
survive, and their tables are reported here for that reason. Their absolute totals grow as this
session is itself recorded; the shares are what the spec rests on.

**Every figure below is BYTES, not characters.** The record quotes Chinese and Japanese, where a
character is three bytes: counting characters understates the registry alone by 21,893.

## R1 - What the record's files weigh, and what one entry weighs

**Question.** Is a page big enough for the split to matter, and how small is one entry?

**Finding.** The ten heaviest files, of 19 that are over 100,000 bytes:

| file | bytes |
|---|---:|
| `research/SOURCES.html` | 1,150,367 |
| `research/citations/cities/capitals.html` | 376,566 |
| `research/citations/urban-features.html` | 294,925 |
| `research/citations/religion-and-death.html` | 266,322 |
| `research/citations/water.html` | 257,601 |
| `research/citations/homesteads.html` | 212,221 |
| `research/cities/capitals.html` | 180,046 |
| `research/citations/fields.html` | 163,877 |
| `research/water.html` | 163,008 |
| `research/urban-features.html` | 161,945 |

Against that, ONE entry is small:

- **a registry entry**: 920 of them, median 1,174 bytes, largest 3,791;
- **a question**: 19 to 39 a page (2 to 39 counting the two smallest pages), a page's average
  between 2,664 (`buildings.html`) and 9,290 (`cities/sizing.html`), largest single question 37,583
  (`fields.html`). `water.html`'s 28 questions average 5,777, the figure `spec.md` US1 quotes;
- **a note**: 3 to 231 a page, a page's average between 437 and 774 bytes.

**What it decides.** The ratio is three orders of magnitude at the registry (1,150,367 against a
median entry of 1,174) and roughly thirty to one on a page. SC-001's 40,000-byte bar for the largest
hand-edited file clears the largest question (37,583) with little to spare - deliberately: a question
that big is one its author should split, and the bar says so.

## R2 - What the SESSION's own editing costs today

**Question.** The GM's premise was that editing a hundreds-of-kilobytes file costs tokens because it
has to be ingested. Does the transcript record bear that out?

**Finding.** Over 284 transcripts: 195,845,246 bytes of tool results in all, of which 1,097,220 -
**0.56%** - were reads of files under `research/`. Of the 91 reads of record files, **82 (90%) asked
for a window** rather than a whole file. Over the whole history there were 95 `Edit`/`Write` calls on
record files, 87,004 bytes of payload between them.

**What it decides.** The premise is true of the file and false of the session: a big file does not
force a big read, because a grep and a windowed read already avoid it. This is why the spec's Summary
puts the saving on the agents, why no success criterion claims a saving in the session's own editing,
and why the split has to pay for itself somewhere else - which R3 is.

## R3 - What a CHECKING AGENT reads

**Question.** When an agent checks one entry, how much of its context is the page it was pointed at?

**Finding.** Share of everything that entered the agent's context that was one research page, over
the 17 recorded agent runs (features 251, 255 and 256, each in its own worktree) that read one:

| recorded agent run | all bytes | the page | share |
|---|---:|---:|---:|
| `source-applicability` (255-sa-shanghai-control) | 239,992 | 236,044 | 98% |
| `quote-check` (255-qc-capitals) | 101,782 | 91,926 | 90% |
| `record-format` (seeded-format-clean) | 104,890 | 93,076 | 88% |
| `entry-drift` (seeded-entry-drift-noticeboard) | 71,255 | 58,689 | 82% |
| `source-applicability` (255-sa-shanghai-2) | 11,231 | 9,060 | 80% |
| `quote-check` (seeded-quote-242-urban) | 174,449 | 126,657 | 72% |
| `entry-drift` (seeded-entry-drift-well) | 56,791 | 40,907 | 72% |
| `entry-drift` (seeded-entry-drift-marsh) | 37,646 | 26,763 | 71% |
| `quote-check` (255-qc-urban) | 100,873 | 68,648 | 68% |
| `entry-drift` (seeded-entry-drift-farmhouse) | 38,805 | 25,827 | 66% |
| `record-format` (seeded-x-format-towns-opus-medium) | 234,147 | 110,504 | 47% |

Six further runs sit between 23% and 36%; the **median of all 17 is 68%**. Feature 251's census
(`specs/251-*/research.md`) measured input at 75-90% of an agent's cost, so the share above is very
nearly the share of the bill.

**What it decides.** This is the feature's justification, SC-002's baseline, and the reason FR-024
puts the rule in the agent CONTRACTS rather than anywhere else: an agent that still reads the whole
page collects nothing from the split, and since feature 256 the defined agents launch with
`omitClaudeMd: true`, so no `CLAUDE.md` reaches them.

**The limit of this finding, stated.** These are runs kept from three features' seeded-fault
experiments, not a sample designed for this question. They are consistent - every run that read a page
spent most of its context on it - but they are not a controlled measurement, which is exactly why
FR-026 requires a re-run against a recorded case before the feature lands, rather than resting on this
table.

## R4 - The footnote numbers are already out of order

**Question.** Is the renumbering the GM approved a real fix or a tidy-up?

**Finding.** Of the 19 pages, **16 carry their footnote references out of document order**. The three
that do not are the pages with 0, 3 and 19 references - small enough that nothing has ever been
inserted into them. `archetypes.html`'s first paragraph alone cites notes 3, 2 and 1, in that order.

Two pages carry a **duplicated reference id**: `archetypes.html` (`fnref-83`) and
`religion-and-death.html` (`fnref-176`, `fnref-177`, `fnref-180` and `fnref-184`). A duplicated `id`
is invalid HTML, and the note's single back link can only return to one of the two.

**What it decides.** FR-019 (allocate at assembly, in document order) and FR-021 (a document-unique id
per reference, the back link to the first). The duplicated ids are a defect found while working here
and fixed in the same work, under constitution XIV, rather than left for someone else.

## What was NOT measured, and why

- **The cost of the assembly itself.** A few hundred kilobytes of string joining over about 1,400
  files, run when the record changes. It is not on the map-drawing path and not on the gate's hot
  path. If it turns out to cost a measurable share of `make done`, that is a measurement the
  implementation owes, not a design question.
- **Whether a smaller read makes a check WORSE.** This cannot be measured from the record; it needs a
  re-run on a case with known findings, which is FR-026 and is owed before the feature lands. Feature
  255 established the rule: cutting what a check reads can lose findings, and a seeded run is how that
  is caught.
