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
and appear in no more than N fragments:

| in <= N fragments | candidates | of the 12 terms feature 259's runs proposed |
|---:|---:|---:|
| 1 | 21 | 4 |
| **2** | **34** | **9** |
| 3 | 41 | 9 |
| 5 | 53 | 9 |
| 10 | 75 | 9 |
| 20 | 101 | 9 |

**What it decides.** FR-002's cutoff of 2. The catch plateaus immediately at 9 of 12 while the list
keeps growing - 20 costs 67 more words for nothing - so the cheapest cutoff that catches what this
filter can catch is the right one.

A coverage count that compared strings exactly would say 7 of 12. It is 9: the record writes
`stringers` and `wingwalls`, and the candidate list carries the prose's own form, which is the form the
reader meets and the form the model is handed.

## R3 - What the filter cannot reach, named rather than discovered later

**Finding.** Of the twelve terms those three runs proposed, three are not raised at the cutoff:

| term | why not |
|---|---|
| `carried deck` | MULTI-WORD - the filter is word-level and cannot see a phrase |
| `spread footing` | the same |
| `embankment` | common in the record: **23 fragments**, though the glossary does not define it |

**What it decides.** FR-007 and FR-008. The list is a FLOOR under the model's noticing and not a
replacement for it: three of twelve are reachable no other way, so the contract asks the model to rule
on the list AND to add what it sees, and says plainly what the list cannot reach - otherwise an empty
list reads as an empty question.

## R4 - What it costs, and R5 - what the check then does

Taken by T02 and T09 respectively, and recorded here when they are.
