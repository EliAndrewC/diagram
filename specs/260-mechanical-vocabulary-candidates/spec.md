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
fragments, and not in the variant index, is a candidate - **34 of them** on that entry.

**What that catches, counted the way the question demands.** Feature 259's three runs proposed eleven
terms between them: eight that every run proposed - the stable core, which never varied and is not the
problem - and three that varied from run to run, which is the whole of the variance this feature
exists to remove. The list catches **2 of those 3** (`nrcs`, `out-to-out`; `embankment` is in 23
fragments and is not rare), and 6 of the 8 core. A first draft of this spec reported "9 of 12", which
counted a term every run DISMISSED as a term to catch and buried the tail inside a core that was never
at issue (R2, R3).

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
- **A citation key** (`ritter-timber-bridges`, `nrcs-ts14q-abutments`) is not a word a reader is asked
  to know, and none appears on any list - but not because FR-004 excludes it. What keeps keys off today
  is the rarity cutoff (`ritter-timber-bridges` is in 3 fragments) and the word regex (which splits
  `nrcs-ts14q-abutments` at its digits into two shards, both over the cutoff). The registry-key and
  `<code>` exclusions are a floor against a key rare enough to survive that, and remove nothing on the
  measured entry (R3).
- **An entry whose every rare word is already defined** produces an empty list, which is a result and
  not a failure.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The sections prepass MUST report, per section, the words of that section's visible text
  that have no line in the derived variant index and that appear in no more than a stated number of the
  record's question fragments.
- **FR-002**: The cutoff MUST be 2 fragments, and the number MUST be stated where it is applied, with
  its measurement, counted the way SC-002 counts: at 2 the list is 34 words and catches **2 of the 3
  terms whose presence varied between feature 259's runs**, and 6 of the 8 core terms every run proposed
  anyway; raising it to 20 adds 67 words and catches no more of either (R2).
- **FR-003**: Each candidate MUST carry the count of fragments it appears in, so a reader of the list
  can see why it is there.
- **FR-004**: A registry source key MUST NOT be a candidate, and text inside a `<code>` span MUST NOT
  be scanned at all - those carry keys and identifiers, not words a reader is asked to know. **Measured,
  this removes nothing on the entry the feature was built against**: the shards a key breaks into
  (`nrcs-ts`, `q-abutments`) are already over the rarity cutoff, and `ritter-timber-bridges` is in 3
  fragments. It is a floor against a key rare enough to survive the cutoff, not a filter that fires
  today, and it is written down as that rather than as a saving it does not make.
- **FR-005**: The text searched MUST be what a READER meets: HTML comments and tags are not words.
- **FR-006**: The frequency corpus MUST be the record's own question fragments, derived at run time. No
  word list is shipped, and nothing about it is maintained by hand.
- **FR-007**: `record-format`'s contract MUST tell it to rule on every candidate it is given, to say
  which verdict each got, and to add anything it notices that the list did not raise.
- **FR-008**: The contract MUST state what the list cannot reach - a multi-word term, and a word the
  record uses often - so that the model does not read an empty list as an empty question.
- **FR-009**: The acceptance bar for a scoping change MUST be restated in
  `.claude/skills/diagram/research/CLAUDE.md`, the operative doc a session reads before it dispatches a
  record check: every candidate ruled on, rather than the same findings. Features 258 and 259 carry the
  old bar in their specs; those are history and are not edited.
- **FR-010**: The prepass MUST stay cheap enough to run before every dispatch. The bar is five
  seconds over the whole record, which R4 measures against; it is a bar and not an observation,
  chosen because a session runs this before a dispatch and anything slower gets skipped.

- **FR-009a**: The statements of the old bar that this feature does NOT change MUST be named, and named
  for what they actually govern, because a criterion that claims a reach it does not have is the defect
  this feature was created by. Three survive in the operative docs, and they are **not one kind**:
  - **Two are about a different decision** - whether a check may run on a CHEAPER MODEL, not whether it
    may read less: `CLAUDE.md`'s "a downgrade stands only after a seeded-fault run on known findings",
    and the same rule at length in `docs/spec-kit-and-reviews.md` (`tests/test_agent_models.py`'s header
    restates it a third time, in a test rather than an operative doc). They rest on the same assumption
    this feature disproved and are left deliberately: a tier downgrade is the GM's own doctrine, and
    changing it is not this feature's to do. It is raised with them instead (FR-011).
  - **One is about SCOPING** - the same decision FR-009 restates the bar for: `docs/efficiency-tooling.md`'s
    feature-255 row, whose candidates each "cut what a check READS" and were "kept only if it hit every
    recorded finding for less". Its FINDING is history and stands - those candidates did lose recorded
    findings. Its CRITERION is the one this feature replaces, so leaving it unqualified would put two
    bars on one decision. The row keeps its measurement and gains a pointer to the new bar. The spec
    review of 2026-09-20 found this, having caught the first draft of this requirement calling all
    three a tier rule.
- **FR-011**: The mechanism this feature substituted for the one the GM approved MUST be put to them
  once the implementation works, naming what changed and what it costs - that "every candidate ruled
  on" now certifies only the words a word-level rarity filter can reach, so a check that misses every
  multi-word term and every record-common one clears it in both conditions. Constitution XVI's route
  for a departure that proves necessary is to carry on and raise it; the raising is a requirement here
  so that it cannot be the thing that gets dropped at the end.

### Key Entities

- **Candidate**: one word of an entry, with its fragment count - a word the glossary does not define and
  the record rarely uses. What the model is asked to rule on.
- **The corpus**: the record's question fragments, which is what "rarely" is measured against.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: (FR-001, FR-002, FR-003, FR-005) On the entry feature 259 measured three times, the
  prepass reports 34 candidates where it reports 0 today, each with its fragment count.
- **SC-002**: (FR-002, FR-006) Of the THREE terms whose presence varied between feature 259's runs -
  the variance this feature exists to remove - the list raises 2, and the one it does not is named with
  the reason (R3). Of the eight the runs never disagreed about it raises 6. Both numbers are stated;
  the first is the one that decides whether this worked.
- **SC-003**: (FR-004) No registry source key appears in a candidate list over the whole record - which
  is true today with or without FR-004, and is recorded as such (R3).
- **SC-004**: (FR-007, FR-008) A `record-format` run given the list rules on every candidate, and its
  report says so item by item.
- **SC-005**: (FR-009, FR-009a) `research/CLAUDE.md` states the new bar; the two TIER-downgrade
  statements of the old one are named in this spec as knowingly left, with the reason; and the one
  SCOPING statement that survives - `docs/efficiency-tooling.md`'s feature-255 row - points at the new
  bar instead of standing as a second one.
- **SC-006**: (FR-010) The prepass stays cheap enough to run before every dispatch: its wall time
  over the whole record is recorded in R4 and stays under the bar FR-010 states.
- **SC-007**: (FR-009a, FR-011) The GM is told what was substituted and what the approved bar now
  certifies, and the three unchanged statements of the old bar are named.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

This feature draws nothing, states nothing on a map, and changes no research text. It changes what a
script prints and what a check is asked to do.

## Assumptions

- The GM chose the PURPOSE - move the noticing into the script so the model rules on a fixed list. The
  mechanism is the measurement's to decide, and the mechanism they were offered (every undefined word)
  is not the one that works.
- The model's own noticing is not replaced, only given a floor. Three of the eleven terms those runs
  proposed are reachable no other way, which is why FR-007 asks for both.
- Features 258 and 259 keep their specs as written, including 259's SC-002 recorded as unmet. A spec is
  a record of what was decided when; this feature is what changed the decision.
