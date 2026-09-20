# Research: where a research page's bytes actually go

Every figure in `spec.md` points at a finding here. All five were taken on 2026-09-20 at `9d11c6e2`
("256: the plan's last authority phrase corrected"), before any of this feature's work, and each
re-runs as one command:

    python3 specs/258-split-the-record-into-per-entry-files/measure.py R1

`R1`, `R4` and `R5` read the record and re-run anywhere. `R2` and `R3` read `~/.claude/projects/`, this
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
- **a question**: 2 to 39 a page, a page's average between 2,664 (`buildings.html`) and 9,279
  (`cities/sizing.html`), largest single question 37,583 (`fields.html`). `water.html`'s 28 questions
  average 5,777, the figure `spec.md` US1 quotes;
- **a note**: 3 to 231 a page, a page's average between 437 and 840 bytes.

Two further figures decide whether SC-001's 40,000-byte bar can be met, because they are the largest
fragments the split will create that are not questions: the registry's **front matter, 8,712 bytes**,
and the largest notes file any one question would get, **28,118 bytes** (`cities/government.html`,
"Servant housing in the samurai ward", 35 notes). Both clear the bar. They were added to `measure.py R1`
on the spec review's aside of 2026-09-20.

**And the registry is not shaped the way it looks.** 8,042 of those 8,712 front-matter bytes are a
single HTML COMMENT, and inside it are two whole `<h2>` groups - the citing rules and the re-sourcing
queue - which no reader of the page sees. The registry has **three visible sections**: the works roster
(its own heading and intro are 213 bytes, then 920 entries), the attested instances (1,746) and the
setting canon (317). A naive cut on `<h2` finds five, splits the comment in half, and invents two
sections. (The two headings in the whole record that do not begin their line are both inside that same
comment, so the second half of FR-008a's rule - a heading is found wherever it stands on its line -
guards a case the record does not carry today. It is stated anyway, so that the cut is never anchored to
the line start.) Hence FR-008a, and the cut rule in `contracts/fragment-format.md`: a heading inside a
comment is not a section. This was found by checking the splitter's assumptions against the record before writing
it, which is the whole reason the byte-identity requirement is worth what it costs.

**What it decides.** The ratio is three orders of magnitude at the registry (1,150,367 against a
median entry of 1,174) and roughly thirty to one on a page. SC-001's 40,000-byte bar for the largest
hand-edited file clears the largest question (37,583) with little to spare - deliberately: a question
that big is one its author should split, and the bar says so.

## R2 - What the SESSION's own editing costs today

**Question.** The GM's premise was that editing a hundreds-of-kilobytes file costs tokens because it
has to be ingested. Does the transcript record bear that out?

**Finding.** Over 284 transcripts: 195,845,246 bytes of tool results in all, of which 1,097,220 -
**0.56%** - were reads of files under `research/`. Of the 91 reads of record files, **82 (90%) asked
for a window** rather than a whole file. Over the whole history there were 96 `Edit`/`Write` calls on
record files, 92,986 bytes of payload between them - a line `measure.py R2` prints, added on the spec
review's finding of 2026-09-20 that the figure had no route back to a run. (Observed 2026-09-20; method: `measure.py R2`, over
`~/.claude/projects/*/*.jsonl` on this machine. The store grows as sessions are recorded - the totals
moved by 161,473 bytes between two runs an hour apart - so the totals are a one-shot observation and the
share is the finding.)

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
| *(observed 2026-09-20; method: `measure.py R3`, over the kept worktree transcripts of features 251, 255 and 256)* | | | |

Six further runs sit between 23% and 36%; the **median of all 17 is 68%** (observed 2026-09-20, same
method and the same 17 runs as the table above). Feature 251's census
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

## R5 - What a note key can be derived from, and what else the allocation fixes

**Question.** Stage 3 names notes instead of numbering them, and the splitter has to derive 1,850 keys
without a human choosing them. Is there anything in a note to derive a key FROM, and is it unique?

**Finding.** Over the whole record: **1,860 references** and **1,850 notes**.

- **1,524 of the 1,850 notes lead with their source key** - `<a href="..."><code>fei-1939</code></a> - which is
  the natural key. The other **326 lead with no key** (an absence note, a note that reasons from several
  works, a note that quotes the GM), and take a key from their question's slug and their ordinal.
- **A source key is repeated within one page 635 times**, so the key alone is not unique: the rule is
  `fei-1939`, then `fei-1939-2`, `fei-1939-3`, in the order the notes appear.
- **4 references carry no `id` at all** (`archetypes.html`, `vegetation.html`), so nothing can link back
  to them. This is a second latent defect beside R4's duplicated ids, and both disappear when every
  reference's id is allocated rather than typed.

**What it decides.** The splitter's key rule (D4 in the plan), and FR-021's statement that a reference's
id is document-unique - which, measured here, fixes 4 missing ids and 2 duplicated ones rather than only
serving the twice-referenced note.

## R6 - The regression baseline (constitution XIII)

**Command.** `git worktree add --detach /tmp/base258 origin/main`, then `make done` there.

**Finding**, at `9d11c6e2`, 2026-09-20: **gate green. 4,113 passed, 4 skipped, 4 warnings in 51.40 s**,
scope FULL, 10 workers, all three coverage floors enforced. Recorded as `m:baseline-done`.

Two attempts were needed, and the first is instructive rather than embarrassing. It was taken at the
clone's own HEAD, which by then carried this feature's spec - and it failed, on `spec-lint --delta` over
that spec: 41 findings, nearly all of them check 3 ("FR-NNN is named by no success criterion"), because
this spec wrote each criterion's FR list at the END of a multi-line bullet and the check reads the ids
from the marker's own LINE. The clone's own invocation had not been showing them. So the baseline caught
a real defect in this feature's paperwork before any reviewer spent a round on it, which is what a
baseline at the right commit is for; the baseline itself was then re-taken at `origin/main`, where the
tree is genuinely unmodified.

## R7 - What the assembly costs the gate

**Before**, the same run as R6: the test phase is 51.40 s over 4,113 tests (observed 2026-09-20;
method: the `make done` of R6, in the detached worktree at `origin/main` - a wall-clock timing on a
shared container, so it is a one-shot observation and the comparison below is like for like).

**The check itself**: `make record CHECK=1` over the whole record - 20 pages, 1,251 fragments - runs in
**0.11 s** (measured by the plan review, 2026-09-20, on a shared container at load 0.75; recorded as
`m:record-check-cost`). The plan's bar was under 2 s, so the fallback it named - checking only the pages
whose fragments the delta touched - is not needed and is not built.

**After** is taken at T27, against this.

## R8 - The re-run FR-026 asks for: does a scoped check still find what the whole-page check found?

**Question.** Feature 255's ruling is that cutting what a check reads can lose findings. So: run
`record-format` over ONE question's fragments, against its own recorded whole-page run on the same
entry, and compare both what it read and what it found.

**The recorded run** (`seeded-format-clean`, feature 255): `record-format` over the whole of
`research/ways.html` - 93,076 bytes under `research/`, 88% of everything that entered its context
(observed 2026-09-20; method: `measure.py R3` over that run's kept transcript). On the question "How far
past the bank does a bridge land?" it reported VOCABULARY on **girder** and on **footing**.

**The scoped run** (2026-09-20, this feature): the same agent, handed
`research/ways/010-how-far-past-the-bank-does-a-bridge-land.html` and its `.notes.html`.

| | recorded, whole page | scoped |
|---|---:|---:|
| the entry's own bytes | 27,234 (the page) | **7,170** (the question, 3,680, and its notes, 3,490) |
| the shared glossary asset | 55,550 | 55,550 |
| all bytes under `research/` | 93,076 | 62,720 |
| VOCABULARY reported for this question | 2 | **12** (10 tooltips proposed, 2 dismissed as defined inline) |

**What it decides, and it is not all good news.** (Observed 2026-09-20; method: the dispatch's own
transcript, counted as `measure.py R3` counts one - every tool result whose file lies under
`research/` - against the recorded run of feature 255.)

- **Nothing was lost.** Every finding the recorded run made on this question the scoped run makes too
  (`girder`), and it makes ten more - `carried deck`, `footplank`, `stringer`, `spread footing`,
  `superstructure`, `backwall`, `wingwall`, `out-to-out`, `NRCS`, and a SESSION NOTE the whole-page run
  did not raise. `footing` is the one the recorded run raised and this one did not, for a reason that is
  not the scoping: the glossary has since gained `strip footing`. A check that reads less and finds
  less has not been improved; this one reads less and finds more.
- **The entry's bytes fall by 74%, not by 90%, and `ways.html` is why** (observed 2026-09-20; method:
  the two runs' own byte counts in the table above, and `measure.py R1`'s page sizes).** It is the SMALLEST page in the
  record - 27,234 bytes, five questions - deliberately chosen as the reference artifact because it is
  the smallest complete case. The same scoping on the median page (`water.html`, 163,008 bytes, 28
  questions) is a 96% fall, and on `cities/capitals.html` (180,046, 39 questions) 97%.
- **The glossary asset is read by both runs and cannot be scoped away.** `research/assets/glossary.js`
  is 55,550 bytes and VOCABULARY is judged against it - that is the check's contract, not a mistake. It
  is 88% of what the scoped run read under `research/`, which is why the table above separates it. SC-002
  said "nothing else under `research/`" and had to be corrected to say what it meant; see the spec's
  Review history.

## What was NOT measured, and why

- **The cost of the assembly itself.** A few hundred kilobytes of string joining over about 1,400
  files, run when the record changes. It is not on the map-drawing path and not on the gate's hot
  path. If it turns out to cost a measurable share of `make done`, that is a measurement the
  implementation owes, not a design question.
- **Whether a smaller read makes a check WORSE.** This cannot be measured from the record; it needs a
  re-run on a case with known findings, which is FR-026 and is owed before the feature lands. Feature
  255 established the rule: cutting what a check reads can lose findings, and a seeded run is how that
  is caught.
