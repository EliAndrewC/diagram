# Feature Specification: The glossary is written one word per file

**Feature**: `259-glossary-per-term` | **Created**: 2026-09-20 | **Status**: Draft
**Input**: the GM's two messages of 2026-09-20, verbatim in [`request.md`](request.md), on reading
feature 258's claim that the shared glossary asset "cannot be scoped away".

## Summary

Feature 258 split the research record into per-entry files so that a checking agent reads the entry it
checks. It left one file whole, and said so in its own report: `research/assets/glossary.js`, 144,524
bytes, which `record-format` reads on every run because VOCABULARY is judged against it. On the case 258
measured, the glossary was 55,550 of the 62,720 bytes that scoped check read under `research/`
(`specs/258-*/research.md` R8).

The GM asked why that file could not be split the same way. The measurement says it can, and that the
session's claim was wrong by 114,727 bytes:

| | bytes |
|---|---:|
| the glossary a check reads today | 144,524 |
| the 720 term NAMES alone | 5,808 |
| names + their variants | 20,981 |
| the definitions | 114,727 |

Testing "is this word already defined?" needs every term's NAME. It never needs a definition. So the
source splits one word per file, the directory listing answers the membership question without opening
anything, and a definition is read only when a check actually wants one - about 154 bytes.

What a reader opens does not change: `glossary.json` and the `glossary.js` derived from it stay exactly
as they are, byte for byte.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A check asks whether a word is defined without reading the glossary (Priority: P1)

`record-format` is dispatched over one question. To report VOCABULARY it must know which words the
glossary already defines. Today it reads 144,524 bytes to find out. After this it lists a directory.

**Why this priority**: it is the whole feature, and it is the last big read feature 258 left standing.

**Independent Test**: dispatch the same check over the same entry and compare the bytes it reads under
the glossary, and the findings it reports.

**Acceptance Scenarios**:

1. **Given** the glossary split one word per file, **When** a check needs the term list, **Then** a
   directory listing of 13,730 bytes answers it and no definition is read.
2. **Given** a word that is not a term but a VARIANT of one - `towpaths`, which the term `towpath`
   owns (verified in the index, not assumed) - **When** the check tests it, **Then** the derived variant index names the owning term in one
   lookup, without opening a term file. A grep would not do: measured, `windlass` matches three term
   files, because a definition may mention a word another term owns (FR-008).
3. **Given** a check that wants a definition - to judge whether it covers the sense, or to match the
   house style of a draft - **When** it reads one, **Then** it reads that term's file and no other.

---

### User Story 2 - A session edits one definition (Priority: P2)

A session correcting one definition opens a file of about 154 bytes, edits it, and runs the assembly.

**Why this priority**: it is the same benefit the record got, and it is what makes the per-term file the
real source rather than a second copy.

**Acceptance Scenarios**:

1. **Given** the split, **When** a session edits a definition, **Then** `make glossary` rebuilds
   `glossary.json` and `glossary.js`, and the gate and the push refuse a stale one.
2. **Given** an edit aimed at the assembled `glossary.json`, **When** exactly one term file holds the
   text, **Then** the edit is re-aimed at it, as feature 258's guard does for a record page.

---

### User Story 3 - What a reader sees does not change (Priority: P1)

Every tooltip on every map modal and every research page says exactly what it said before.

**Why this priority**: the glossary is read by a player hovering a word. This is an authoring change and
must be invisible.

**Acceptance Scenarios**:

1. **Given** the split has landed, **When** `glossary.json` and `glossary.js` are compared with the files
   they replace, **Then** they are byte-identical.

---

### Edge Cases

- **A term whose name cannot be a filename.** One term is `dS/m`; a slash cannot be in a filename. Eight
  more carry macrons (`Hyōjōsho`, `bettō`, `jingūji` and five others), which a filename carries perfectly
  well (R3).
- **Term ORDER is load-bearing**, which is not obvious: 7 variants are claimed by two terms each, and the
  page's matcher lets the LAST one win (`record.js` builds `defs[variant] = def` in file order, then
  sorts the variants by length). Re-ordering the terms would silently change which definition a reader
  sees for those 7 words. The split preserves the order (R2). An eighth case is a term listing one
  variant twice in its own array (`bettō`), which order does not affect.
- **A word that is a variant of no term** is what VOCABULARY exists to report; the directory answers
  "not defined" by not having it.
- **Two term files claiming one term name** cannot happen: the filename is the term.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The glossary's hand-edited source MUST become one file per term, in a directory.
- **FR-002**: A term file's name MUST carry the term itself, so that a directory listing IS the term
  list and a glob finds a term without opening anything. A character a filename cannot carry is
  percent-encoded, and the file records the term exactly (one term needs this today: `dS/m`).
- **FR-003**: The term files MUST carry an ordering prefix, gapped as feature 258's are, because term
  order decides which definition wins for a variant two terms claim - 7 of them today (R2).
- **FR-004**: `glossary.json` MUST become an assembled file, and `glossary.js` MUST continue to be
  derived from it unchanged. The assembly of the term files, BEFORE any content correction, MUST be
  byte-identical to the `glossary.json` it replaces - that is what proves the split changed nothing.
  FR-011's correction lands as a second diff, after it, carrying its own before-and-after listing.
- **FR-005**: One command MUST assemble it, and a check mode MUST report a stale committed file.
- **FR-006**: The gate and both push routes MUST refuse a `glossary.json` that differs from what its term
  files assemble, for the reason feature 258 established: a record-only change takes the DIRECT route,
  where the gate never runs.
- **FR-007**: An Edit aimed at the assembled `glossary.json` MUST be re-aimed at the one term file
  holding its text, or refused where none or several do - the guard feature 258 built, extended to this
  file rather than duplicated.
- **FR-008**: A DERIVED index of every variant and the term that owns it MUST be written beside the
  term files and checked like any other derived asset. This is point 3 of the answer the GM approved,
  and it is load-bearing rather than a convenience: a plain grep over the term files answers with
  CANDIDATES, not the claimant - measured, `windlass` matches three term files and `water mouth`
  three, because a definition may mention a word another term owns.
- **FR-008a**: The contracts of the checks that judge VOCABULARY MUST tell the agent to read that index
  - or list the directory, for the narrower question of whether a word is itself a term - and to open a
  term file only when it wants that term's definition. This is the only place the instruction can reach
  them (feature 256).
- **FR-009**: The record's own operative doc MUST state where a term lives and how to find one.
- **FR-010**: The saving MUST be demonstrated on a recorded case before the feature lands: the same
  check over the same entry, reporting the bytes read under the glossary and whether the findings are
  the same. A check that reads less but finds less has not been improved (feature 255).
- **FR-011**: No variant may be claimed by two terms, and no term may list one variant twice, once this
  lands - or the order FR-003 preserves stays load-bearing in a place nobody is looking. The resolving
  rule is the checkable one: the term whose own NAME is the variant keeps it, comparing names and
  variants with case, spaces and hyphens folded - without that folding the rule does not decide `water
  mouth`, claimed by `shuikou` and the term `water-mouth`, which is named with a hyphen (R2). Five of
  the seven resolve with no change to what a reader sees; two change it, and both are corrections.
  **This is a content correction, not part of the split**: FR-003 delivers the whole of what the GM
  asked for without touching a definition, and the split's own verification (FR-004) stands independent
  of this. It proceeds under constitution XIV - a defect found in the work at hand - and is raised with
  the GM once the implementation works.

### Key Entities

- **Term file**: one hand-authored file holding one glossary term - its name, its variants, its
  definition. The unit a session edits and a check reads.
- **The assembled glossary**: `glossary.json`, derived from the term files, committed, and read by the
  engine and the tests exactly as it is today.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: (FR-001, FR-002, FR-003) The largest hand-edited glossary file falls from 137,059 bytes to
  about 154 (the median term), and the term list a check needs is a directory listing of 13,730 bytes
  rather than a 144,524-byte read (R1).
- **SC-002**: (FR-008, FR-008a, FR-010) On the recorded case of FR-010, the check reads the variant
  index or the directory listing, and no definition it does not name, in place of the whole glossary -
  and it reports the same findings. What that costs is what FR-010's run reports; R1 declines to predict
  it, and so does this criterion. **NOT MET as written, and not reworded**: three runs of the check on
  one entry agree on eight terms and differ in the tail, in both conditions (R5). The criterion
  assumes a determinism `record-format` does not have; what to replace it with is a decision about
  what that check is, which is the GM's and not this feature's.
- **SC-003**: (FR-004) At the SPLIT's landing, `glossary.json` and `glossary.js` are byte-identical to
  the files they replace: the diff is empty. FR-011's resolution lands after it and on its own, so
  that its diff is exactly the variants it removes and nothing else - the same sequencing feature
  258 used for its renumbering.
- **SC-004**: (FR-005, FR-006) A stale committed `glossary.json` cannot reach main: it fails the gate and
  both push routes refuse it.
- **SC-005**: (FR-007, FR-009) An edit aimed at the assembled file never silently lands, and the
  operative doc states where a term lives.
- **SC-006**: (FR-011) No variant is claimed by two terms and no term lists one twice; a test fails if
  either happens again. The 8 changes this makes are listed in the commit that makes them, separately
  from the split.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

This feature draws nothing on a map. It changes nothing a reader sees, which SC-003 proves by diff -
with one exception, declared here: two tooltips out of 720 terms, each of which is showing another
term's definition today because of an order nobody chose.

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Where two terms claim one variant, the term whose NAME is that variant keeps it | map drawing convention (the modal's own presentation) | today the LAST term in file order wins and nobody decided that; 7 variants are in that state, and two of them show the wrong definition because of it - hovering `chaoguan` shows `lijin`, hovering `qiandao` shows `towpath` (R2) | this spec FR-011, R2, and the resolving test |

## Assumptions

- The GM's "each word in the glossary could be the name of the file" is taken as the form of the
  filename, with the ordering prefix feature 258 established in front of it - their own framing was
  "the same thing with the glossary that we are doing with other files", and the record's files carry
  that prefix. The prefix is what keeps the assembled file byte-identical.
- `glossary.js` stays a single derived file: a page opened from `file://` cannot fetch a sibling, which
  is why it is a script at all.
- The split is of the SOURCE under `interactive/assets/`. The glossary is shared by the map's modals and
  the record, and it keeps one home.

## Review history

- Round 1 (2026-09-20, `spec-fidelity`, Opus): CHANGES REQUIRED, seven items, all applied. The round
  re-ran every figure and they all reproduced; two of its findings were things it measured that this
  spec had asserted. (1) **FR-004 and SC-003 contradicted FR-011**: byte-identity cannot hold while a
  content correction moves the same bytes. Byte-identity is now the criterion for the SPLIT, and the
  correction lands as a second diff - which is how it was in fact landed, two commits. (2) **FR-011's
  rule did not decide `water mouth`**, claimed by `shuikou` and the term spelled `water-mouth`: the
  rule now states the folding of case, spaces and hyphens it silently depended on, and the
  implementation hit exactly that case. (3) R2's count was restated against the stated rule. (4) **The
  derived variant index the GM's own approved answer named had been dropped in favor of a grep** - and
  the round measured why that fails: `windlass` matches three term files, because a definition may
  mention a word another term owns. The index is back, as FR-008. (5) US1-AC2's `girders`/`girder`
  example is in the glossary 0 times; it now names a pair that exists. (6) SC-002 pinned a figure R1
  explicitly declines to predict; it states the criterion and leaves the figure to FR-010's run.
  (7) FR-011 and SC-006 are marked as what they are - a content correction not entailed by the split,
  proceeding under constitution XIV, raised with the GM rather than folded in silently.
- Round 2 (2026-09-20, `spec-fidelity`, Opus): CHANGES REQUIRED, six items, all applied. It checked the
  round-1 replacements against the artifacts and found one wrong - `well sweep` is owned by `jiegao`,
  not by `well-sweep` - which is the same class of miss it had raised as its own item 5. R4 compared
  against the wrong run's test phase; `measure.py R2` printed 8 where the record says 7, counting a
  term's own duplicate as a clash between terms; the module and its test still described the abolished
  state in the present tense; and the contract and the operative doc still taught `girders`/`girder`,
  which is in the glossary 0 times. Its sixth item was the substantive one: SC-002 was not satisfied
  and was not to be reworded, and one sample of a stochastic check could settle it neither way.
- Round 3 (2026-09-20, `spec-fidelity`, Opus): CHANGES REQUIRED, five items, all applied. A second
  scoped run was made for round 2's item 6, and R5 now records three runs: eight terms proposed by
  every one, a tail that varies in both directions, and SC-002 met by none of them. The round accepted
  that leaving the criterion unmet and escalated is right rather than rewording it - *"rewording a
  success criterion after measuring against it, so that the delivered result clears it, is editing the
  yardstick"* - and narrowed R5's own inference, which had claimed the variation IS the model's where
  the data only refutes the claim that the tail differences are scoping losses. It also observed that
  this was the third round in which a corrected example was corrected only where the review pointed:
  the `girder` token was swept this time, and the two places it remains each say why it is there.
- Round 4 (2026-09-20, `spec-fidelity`, Opus): **FAITHFUL.** All five of round 3's items confirmed, with
  the two timings traced back to the runs that produced them rather than read. One correction to this
  session's own account: the `girder` token survives in THREE places in the engine tree, not two - the
  synthetic fixture and two `file_name` assertions, which assert a string format on a synthetic input
  and claim nothing about the real glossary. The round's closing aside, for the GM: SC-002's real
  successor is a determinism question about `record-format` itself - a stable core plus a declared
  tail - and R5 is the evidence to hand them when they decide it.

