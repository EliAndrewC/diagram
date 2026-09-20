# Feature Specification: The prepass names the words; the model rules on them

**Feature**: `260-mechanical-vocabulary-candidates` | **Created**: 2026-09-20 | **Status**: Draft
**Input**: the GM's choice of 2026-09-20, verbatim in [`request.md`](request.md), of option C from the
four the session put to them when feature 259 landed with SC-002 unmet.

## Summary

`record-format` does two jobs at once: it NOTICES which words a reader might not know, and it JUDGES
them. The first is why its output wanders - three runs on one entry agree on eight terms and differ in
the tail, in both conditions (`specs/259-*/research.md` R5) - and it is why "it reports the same
findings" is a bar no pair of runs can clear, including two runs of the same thing.

The project's own rule is that what is mechanical runs FIRST, as a script, and its output goes in the
agent's prompt. `make record-prepass` is that script. On the entry all three runs checked it reports
**0 candidates**, because it does not look for unfamiliar words at all.

This feature makes it look. The prepass names the candidate words; the model rules on the list it is
given and adds anything it notices beyond it; and the acceptance bar for a scoped check becomes
something checkable - **every candidate the prepass raised is ruled on** - in place of a bar that
assumed a determinism the check does not have.

**The shape the GM was offered does not work, and the spec says so rather than narrowing it quietly.**
"Every word in the entry with no line in the variant index" raises **314 of the entry's 324 distinct
words** (R1), because ordinary English is not in a glossary. What works needs no shipped word list:
rarity within the record's own corpus. A word in **2 or fewer** of the record's 1,479 question
fragments, and not in the variant index, is a candidate - **34 of them** on that entry, catching 9 of
the 12 terms feature 259's three runs proposed (R2).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The check rules on a list instead of noticing an open one (Priority: P1)

A session runs `make record-prepass PAGE=ways SECTION=010` and gets, beside the section's text, the
words in it that the glossary does not define and the record rarely uses. It hands that list to
`record-format`, whose contract tells it to rule on each one and to add anything else it sees.

**Why this priority**: it is the whole feature, and the reason the GM chose this option over three
cheaper ones.

**Acceptance Scenarios**:

1. **Given** an entry, **When** the prepass runs over it, **Then** it prints a candidate list of tens of
   words, not hundreds, each with the number of fragments it appears in.
2. **Given** that list, **When** `record-format` reports, **Then** every candidate appears in its report
   with a verdict - proposed, dismissed as ordinary, or dismissed as defined inline.
3. **Given** a term the list did not raise, **When** the model notices it anyway, **Then** it reports it,
   and the report is not judged incomplete for containing it.

---

### User Story 2 - A scoping change can be judged (Priority: P1)

A future feature makes a check read less. Its evidence is no longer "the same findings", which no two
runs produce; it is that every candidate the prepass raised was ruled on in both conditions.

**Why this priority**: features 258 and 259 both wrote the unmeetable bar into their specs, and 259
landed with it recorded as failed. This is what replaces it.

**Acceptance Scenarios**:

1. **Given** two runs of one check on one entry, **When** their reports are compared, **Then** the
   comparison is per candidate and does not require the two tails to match.

---

### Edge Cases

- **A word the record uses often but the glossary does not define** is not raised - `embankment` appears
  in 23 fragments (R3). The model's own noticing is what covers this, which is why the contract says to
  add what it sees.
- **A multi-word term** is not raised: `carried deck` and `spread footing` are phrases, and the filter
  is word-level (R3). Same cover.
- **A word in the prose only as a plural** IS raised, in the prose's own form - `stringers`, `wingwalls`
  - which is the form the reader meets.
- **A citation key** (`ritter-timber-bridges`, `nrcs-ts14q-abutments`) is rare by construction and is
  not a word a reader is asked to know; it is excluded by being a key in the registry.
- **An entry whose every rare word is already defined** produces an empty list, which is a result and
  not a failure.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The sections prepass MUST report, per section, the words of that section's visible text
  that have no line in the derived variant index and that appear in no more than a stated number of the
  record's question fragments.
- **FR-002**: The cutoff MUST be 2 fragments, and the number MUST be stated where it is applied, with
  its measurement: at 2 the list is 34 words and catches 9 of the 12 known terms; raising it to 20 adds
  67 words and catches no more (R2).
- **FR-003**: Each candidate MUST carry the count of fragments it appears in, so a reader of the list
  can see why it is there.
- **FR-004**: A registry source key MUST NOT be a candidate.
- **FR-005**: The text searched MUST be what a READER meets: HTML comments and tags are not words.
- **FR-006**: The frequency corpus MUST be the record's own question fragments, derived at run time. No
  word list is shipped, and nothing about it is maintained by hand.
- **FR-007**: `record-format`'s contract MUST tell it to rule on every candidate it is given, to say
  which verdict each got, and to add anything it notices that the list did not raise.
- **FR-008**: The contract MUST state what the list cannot reach - a multi-word term, and a word the
  record uses often - so that the model does not read an empty list as an empty question.
- **FR-009**: The acceptance bar for a scoping change MUST be restated in the record's operative doc:
  every candidate ruled on, rather than the same findings. Features 258 and 259 carry the old bar in
  their specs; those are history and are not edited, but the doc a session reads MUST carry the new one.
- **FR-010**: The prepass MUST stay cheap enough to run before every dispatch. The bar is five
  seconds over the whole record, which R4 measures against; it is a bar and not an observation,
  chosen because a session runs this before a dispatch and anything slower gets skipped.

### Key Entities

- **Candidate**: one word of an entry, with its fragment count - a word the glossary does not define and
  the record rarely uses. What the model is asked to rule on.
- **The corpus**: the record's question fragments, which is what "rarely" is measured against.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: (FR-001, FR-002, FR-003, FR-005) On the entry feature 259 measured three times, the
  prepass reports 34 candidates where it reports 0 today, each with its fragment count.
- **SC-002**: (FR-002, FR-006) The list catches 9 of the 12 terms those three runs proposed, and the
  three it does not are named in the record with the reason (R3).
- **SC-003**: (FR-004) No registry source key appears in a candidate list.
- **SC-004**: (FR-007, FR-008) A `record-format` run given the list rules on every candidate, and its
  report says so item by item.
- **SC-005**: (FR-009) The operative doc states the new bar, and a session reading it is not sent to the
  criterion features 258 and 259 could not meet.
- **SC-006**: (FR-010) The prepass stays cheap enough to run before every dispatch: its wall time
  over the whole record is recorded in R4 and stays under the bar FR-010 states.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

This feature draws nothing, states nothing on a map, and changes no research text. It changes what a
script prints and what a check is asked to do.

## Assumptions

- The GM chose the PURPOSE - move the noticing into the script so the model rules on a fixed list. The
  mechanism is the measurement's to decide, and the mechanism they were offered (every undefined word)
  is not the one that works.
- The model's own noticing is not replaced, only given a floor. Three of the twelve known terms are
  reachable no other way, which is why FR-007 asks for both.
- Features 258 and 259 keep their specs as written, including 259's SC-002 recorded as unmet. A spec is
  a record of what was decided when; this feature is what changed the decision.
