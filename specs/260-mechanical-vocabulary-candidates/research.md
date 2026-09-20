# Research: what a mechanical candidate list can and cannot do

Every figure in `spec.md` points at a finding here, and each re-runs as one command:

    python3 specs/260-mechanical-vocabulary-candidates/measure.py R1

All three read the repository and re-run anywhere. Taken 2026-09-20 at `26f8bb4f` (feature 259's
landing), on the entry feature 259's three `record-format` runs all checked: `ways`, the question "How
far past the bank does a bridge land?".

## R1 - The shape the GM was offered does not work

**Question.** The session told the GM: *"the prepass emits every word in the entry with no line in
`glossary-variants.txt`"*. Is that a list?

**Finding.** No. The entry has **324 distinct words** and **314 of them** have no line in the index -
`about`, `and`, `are`, `angle`, `approach`. Ordinary English is not in a glossary, so "not in the
glossary" is nearly every word.

**What it decides.** The purpose the GM chose stands; the mechanism they were offered is replaced, and
the spec says so in its Summary rather than narrowing the promise quietly.

## R2 - Rarity within the record's own corpus

**Question.** What filter separates a word a reader may not know from ordinary English, without
shipping a word list to maintain?

**Finding.** How rare the word is in the record itself. The corpus is the record's **1,479 question
fragments**, 19,140 distinct words. Candidates are the entry's words that are not in the variant index
and appear in no more than N fragments.

**Counted the way the question demands.** Feature 259's three runs proposed eleven terms between them.
Eight are the CORE every run proposed - which never varied, and so is not what this feature is for.
Three are the TAIL that differed from run to run: `nrcs`, `out-to-out`, `embankment`. One more,
`obliquity`, every run DISMISSED as defined inline; the list raising it is neither a catch nor a miss.

| in <= N fragments | candidates | core caught | TAIL caught |
|---:|---:|---:|---:|
| 1 | 21 | 3 of 8 | 1 of 3 |
| **2** | **34** | **6 of 8** | **2 of 3** |
| 3 | 41 | 6 of 8 | 2 of 3 |
| 5 | 53 | 6 of 8 | 2 of 3 |
| 10 | 75 | 6 of 8 | 2 of 3 |
| 20 | 101 | 6 of 8 | 2 of 3 |

**What it decides.** FR-002's cutoff of 2. Everything plateaus at once while the list keeps growing -
20 costs 67 more words for nothing - so the cheapest cutoff that catches what this filter can catch is
the right one.

**And what the first draft of this record got wrong**, which the spec review of 2026-09-20 measured: it
reported "9 of 12", counting `obliquity` as a term to catch and folding the tail into a core that never
varied. The number that decides whether this feature does its job is 2 of 3 - the terms whose presence
actually moved between runs - and it is smaller and less flattering than the headline it replaces.

A coverage count comparing strings exactly would say less again: the record writes `stringers` and
`wingwalls`, and the list carries the prose's own form, which is what the reader meets and what the
model is handed.

## R3 - What the filter cannot reach, named rather than discovered later

**Finding.** Of the eleven terms those three runs proposed, three are not raised at the cutoff:

| term | why not |
|---|---|
| `carried deck` | MULTI-WORD - the filter is word-level and cannot see a phrase |
| `spread footing` | the same |
| `embankment` | common in the record: **23 fragments**, though the glossary does not define it |

**What it decides.** FR-007 and FR-008. The list is a FLOOR under the model's noticing and not a
replacement for it: three of the eleven proposed terms are reachable no other way, so the contract asks
the model to rule on the list AND to add what it sees, and says plainly what the list cannot reach -
otherwise an empty list reads as an empty question.

**And what FR-004 does not do.** No registry source key appears among the 34, and none appears anywhere
in the record's 321 candidate lists - but not because FR-004 excludes them. `ritter-timber-bridges` is
in 3 fragments and is kept off by the rarity cutoff; `nrcs-ts14q-abutments` never survives the word
regex, which splits it at the digits into `nrcs-ts` and `q-abutments`, both also over the cutoff. The
spec review of 2026-09-20 measured this and struck the first draft's premise that a key is "rare by
construction", which is false. FR-004 is kept as a FLOOR - a key rare enough to survive the cutoff
would otherwise be raised - and the spec says it removes nothing today rather than claiming a saving.

## R4 - What it costs

**Finding** (observed 2026-09-20; method: the pass run over every entry of the record in one process,
wall clock on a shared container):

| | |
|---|---|
| the corpus walk - 1,479 fragments | 0.31 |
| the candidate pass over all 321 entries | **0.79** |
| one invocation, as a session runs it (`make record-prepass PAGE=ways SECTION=010`) | 0.45 |
| FR-010's bar | 5 |

(seconds, wall clock on a shared container)

**Before and after, the number a session actually experiences** (observed 2026-09-20; method: the same
command three times in each of two trees on a quiet machine - a detached worktree at `26f8bb4f`, the
commit before this feature, and the clone with the pass in it):

| | |
|---|---|
| `make record-prepass PAGE=ways SECTION=010` BEFORE | 0.11, 0.11, 0.10 |
| the same command AFTER | 0.48, 0.47, 0.48 |
| FR-010's bar | 5 |

The pass costs about **0.37 s an invocation**, nearly all of it the corpus walk, and lands at a tenth of
the bar. There is no before counterpart to the 0.79 s in-process sweep, because before this feature
there was no pass to sweep; the per-invocation pair is the comparison FR-010 is about, since the bar
exists so that a session runs this before every dispatch rather than skipping it.

**And one thing it cost before it was measured** (observed 2026-09-20, same method). The first version
walked the record for every section's notes, and read the corpus once per page: the whole-record sweep
took **7.52 seconds**, over the bar. Both are the shape this engine's performance doc names as the only slow shape it has ever found -
a per-candidate scan of ground that does not change during the scan. The notes are indexed once and the
four derived inputs are memoized within a run, which is the whole of the fix.

**What the sweep also establishes**: 321 sections, 5,592 candidates, median 13 a section, largest 115
(`archetypes`, the dike-pond hamlet question), smallest 0 - and **no registry key raised anywhere**
(SC-003).

## R5 - What the check then does

**Question.** Given the list, does `record-format` rule on it - and does the floor cost it the noticing
it was doing before?

**Method** (observed 2026-09-20). One `record-format` dispatch on the same entry all three of feature
259's runs checked, handed the prepass output verbatim and asked for the three things FR-007 and FR-008
name: a verdict on every candidate, anything beyond the list, and the two visible-text classes the
contract already asked for.

**Finding.**

| | |
|---|---|
| candidates ruled on | **34 of 34**, in the list's order, one line each |
| PROPOSE | 11 |
| DEFINED INLINE | 3 (`decking`, `embedment`, `obliquity`) |
| ORDINARY | 20 |
| terms reported BEYOND the list | 6 |

SC-004 is met, and met item by item: every candidate carries its verdict, and the plainly ordinary ones
are one short line each rather than an argument.

**The part that decides whether the floor is safe.** Three of the six terms it added beyond the list are
exactly the three R3 named as unreachable - `carried deck` and `spread footing` (phrases the word-level
filter cannot see) and `embankment` (23 fragments, so not rare). It also added `bearing seat`, which it
called the entry's hinge, `landing` and `USDA`. The floor did not replace the noticing; the run found
more beyond the list than any of feature 259's three runs proposed in total.

**Against feature 259's three runs**, which is the comparison this feature was created by: those runs
agreed on eight terms and differed in a tail of three, and no pair of them met "the same findings". This
run's relationship to the list is not a tail at all - it is 34 verdicts against 34 names. What still
varies is what a run finds BEYOND the list, and the contract says in as many words that a report is not
judged incomplete for containing it.

**What it decides.** SC-004, and the substitution FR-011 puts to the GM: the bar is checkable, and what
it certifies is the floor, not the whole of the check.
