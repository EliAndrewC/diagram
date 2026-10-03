# Feature Specification: The implementation cross-referenced with the research, claim by claim

**Feature Branch**: `316-research-referencing` (no branch - committed on `main` in the clone)

**Created**: 2026-10-02

**Status**: Accepted - `spec-fidelity` FAITHFUL, round 3 (2026-10-02)

**Input**: The GM, 2026-10-02 (verbatim in `request.md`): *"I'm less concerned with bringing our current implementation in
line with our research than I am with having some kind of system that cross references our implementation with the research
findings"*; *"the code that generates a hamlet must have citations for anything that should be research derived"*; *"our
tooling should be able to evaluate whether or not an annotated thing has been edited since the last time a subagent check ran
on it"*; *"I do want that as part of this feature"* (the hamlet walk-through linking its research at every step); and, on the
session's recommendations, close feature 296 as superseded with its two findings as the first drifted rows, the push rule as
proposed, and per-claim granularity.

## Context (observed 2026-10-02)

The hamlet generator (the `hamletgen` package) holds 901 functions and methods, 25 classes and 365 module-level constants
(an `ast` count over its 62 files). The code that runs when a hamlet is generated is wider: the engine modules `hamletgen`
imports, directly or through others, are 241 modules in all (62 of them `hamletgen`, 112 under `settlement/`, 31
`interactive/`, 19 `waterfields/`, the rest `labels/`, `overlap/`, `sitegen/` and five single modules), 74,331 lines - counted
2026-10-02 by walking every `import` in the syntax tree from the `hamletgen` package outward. Decisions the GM named live
outside `hamletgen`: how much dry field a hamlet gets (`settlement/fields/grain.py`), where the dry hem is laid
(`settlement/fields/comb.py`), a grove's sides (`settlement/homestead_parts/grove_sides.py`), yard sizes
(`settlement/homestead_parts/yards.py`). Its research pointers are COMMENTS: 141 distinct questions named across 118 engine files,
about 85 GUESS labels, 27 "map drawing convention" labels and one "deliberate deviation" in `hamletgen` alone. The gate checks
that a pointer names a question that exists (`check-research-pointers.py`); nothing records what a pointer claims, whether any
check ever compared the code beside it with the question, or whether either side has changed since.

The Mode A procedures the GM named - the magistrate's manor and the country shrine - are written in
`.claude/skills/diagram/buildings/programs.md` (one section each) and drawn with the vocabulary of
`.claude/skills/diagram/buildings.md`. They carry no claim markers at all.

Feature 296 (filed, not started) was one mismatch found by luck: the row farm's orientation and the far row's dry-field share,
each against `research/questions/0033-row-villages-resson.html` (296 cites the pre-303 numbers homesteads/158 and /159). The
hamlet walk-through (`dev/placement-stages/hamlet-placement.html`, built from stage and step docstrings by feature 227) links to
no research.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Every research-derivable decision says what backs it (Priority: P1)

A reader of the hamlet generator, or of the two Mode A procedures, finds beside each decision a CLAIM: a short label for what is
decided (the far row's dry-field share, a field's size, a grove's side) and what backs it - a research question by its file, or
an explicit class (a guess, a map drawing convention, a deliberate deviation from a named question, or no physical decision at
all). A unit of code or a procedure section with no claim fails the gate.

**Why this priority**: the GM: *"the code that generates a hamlet must have citations for anything that should be research
derived"*; *"every single one of those things should get a research annotation"*.

**Independent Test**: delete the claims from one function in scope and run the gate: it fails naming that function; restore
them and it passes.

**Acceptance Scenarios**:

1. **Given** a function that decides the far row's dry-field share, **When** a reader opens it, **Then** its documentation names
   that claim and the question that backs it, in a form a tool can read without running the engine.
2. **Given** a function that only does geometry, **When** it is read, **Then** it carries an explicit "no physical decision"
   claim, its own or its module's.
3. **Given** a function or constant in scope with no claim, own or inherited, **When** the gate runs, **Then** it fails naming it
   and the form a claim takes.
4. **Given** a claim naming a question file that does not exist, or a malformed claim, **When** the gate runs, **Then** it fails.
5. **Given** a section of the magistracy or country-shrine procedure, **When** it is read, **Then** it carries its claims in the
   same grammar, and one without any fails the gate.

---

### User Story 2 - An up-to-date index of what the checks found (Priority: P1)

One committed index records, per claim, the verdict of the last check that compared the implementation with the research it
names, and fingerprints of both sides as that check read them. A report prints the index: what is in step, what is known to
have drifted, what needs research, what is mislabeled, and what is owed a check.

**Why this priority**: the GM: *"having an index of which things our sub-agent checks have shown to be valid and which ones are
known to not be valid ... there would always be an up-to-date index"*.

**Independent Test**: run the report on the landed feature: every claim in scope has a row, and the counts by verdict sum to the
number of claims.

**Acceptance Scenarios**:

1. **Given** the feature landed, **When** the report runs, **Then** every claim in scope has a verdict, and none is owed.
2. **Given** feature 296's two findings, **When** the report runs, **Then** both appear as drifted rows naming the code and the
   question.
3. **Given** a claim whose code changed since its verdict (its executable code, its claim line, or a constant it reads), **When**
   the report runs, **Then** it is listed as owed.
4. **Given** a claim whose cited question's findings changed since its verdict, **When** the report runs, **Then** it is owed.
5. **Given** a change only to comments, formatting or the prose of a docstring other than the claim lines, **When** the report
   runs, **Then** nothing is owed.

---

### User Story 3 - A changed implementation is re-checked, and only it (Priority: P1)

When code or a procedure section in scope changes, or a question a claim cites changes its findings, the tooling names exactly
the claims owed a check and builds the bundle the check reads; a new defined check judges each claim and returns a verdict
recorded in the index.

**Why this priority**: the GM: *"when the implementation changes then our tooling knows which specific functions need to be fed
to subagents to kind of redo the checks to see whether the new implementation is still in line with the research findings or
whether there need to be new research findings or whether something now must be marked as a guess or unresearched"*.

**Independent Test**: edit the executable code of one claimed function; the owed command names that function's claims and no
other; build its bundle, dispatch the check, record the verdict; the claim is no longer owed.

**Acceptance Scenarios**:

1. **Given** one function edited, **When** the owed command runs, **Then** it names every claim of that function and nothing else
   (constants it reads that did not change are not named; their own claims are units of their own).
2. **Given** a constant's value changed, **When** the owed command runs, **Then** the constant's claims and every claim of a
   function in scope that reads it are named.
3. **Given** a claim owed, **When** its check returns, **Then** one command records the verdict and the fingerprints the check
   read.
4. **Given** the check finds a decision the code makes that no claim covers, **When** it reports, **Then** it names it, and it is
   recorded as needing a claim.

---

### User Story 4 - The push holds it (Priority: P1)

A push whose delta owes a claim check that has not been answered is refused, naming each claim and the command that builds its
bundle. A finding the delta introduced - drifted, in need of research, mislabeled, unclaimed or undecided - is refused too. A
finding that was already there before the delta is not refused: it is printed as a warning.

**Why this priority**: the GM accepted the session's rule: an owed row blocks; a drifted row the change introduces blocks; a
pre-existing drifted row is a warning, as feature 296 was treated.

**Independent Test**: a test pushes (dry) a delta with an owed claim and sees the refusal; records a verdict and sees it pass; a
delta whose recorded verdict turns a previously in-step claim drifted is refused; one that leaves an already-drifted claim
drifted passes with the warning.

**Acceptance Scenarios**:

1. **Given** an owed claim with no current verdict, **When** the push runs, **Then** it is refused, naming the claim.
7. **Given** a unit judged for the first time with a finding, on code and research the delta did not change, **When** the push
   runs, **Then** it passes and prints the finding as pre-existing.
2. **Given** a verdict recorded before the claim's code or research changed again, **When** the push runs, **Then** it is refused
   as stale.
3. **Given** a claim in step at the merge base and drifted at the head, **When** the push runs, **Then** it is refused.
4. **Given** a claim drifted at the merge base and still drifted at the head, **When** the push runs, **Then** it passes and prints
   the claim as a known drift.
5. **Given** a stated reason, **When** the push runs, **Then** it passes and the reason is recorded where the bypass log is.
6. **Given** a delta touching nothing in scope and no question a claim cites, **When** the push runs, **Then** the gate is silent.

---

### User Story 5 - The walk-through proves it (Priority: P2)

The hamlet walk-through page shows, under each stage and each step, the claims that stage or step makes, each linked to the
research question it names on the built record, with its verdict; a guess, a convention or a deviation is shown as one.

**Why this priority**: the GM: *"if we are able to link to individual research pages in every step where we talk about what the
step is doing and then we say oh yeah and here is the research that demonstrates that this is the correct thing then that is a
great proof of implementation"*.

**Independent Test**: build the page; every stage and every step shows its claims; every pointer is a link that opens a page of
the built record; a step whose claims are all "no physical decision" says so.

**Acceptance Scenarios**:

1. **Given** the built page, **When** a reader opens a stage, **Then** each of its steps lists its claims with links and verdicts.
2. **Given** a claim marked drifted in the index, **When** the page is built, **Then** the step shows it as drifted.
3. **Given** a step with no claim, **When** the page is built, **Then** the build fails (the coverage gate already prevents it).

---

### User Story 6 - The audit, done once (Priority: P1)

Every claim in scope is written and then checked once, so the index starts complete: the hamlet generator and the two Mode A
procedures. What the audit finds is recorded, not fixed: a drifted claim stays drifted in the index (the warning class), and
only the claims themselves are corrected (a missing claim written, a mislabeled class corrected, an unresearched decision labeled
unresearched).

**Why this priority**: the GM: *"it seems worth doing an audit of our implementation of our scripted hamlet generation and our
procedures for the manually generated maps"*; and *"what I am saying is not even about fixing anything it's just about doing an
audit and then having an index"*.

**Independent Test**: after the audit, the report shows no owed claim, no claim with no verdict, and every drifted, needs-research
and mislabeled finding the audit made, with the claim it concerns.

**Acceptance Scenarios**:

1. **Given** the audit done, **When** the report runs, **Then** every claim has a verdict.
2. **Given** a decision the audit found unlabeled and the record silent on, **When** it is recorded, **Then** its claim says
   UNRESEARCHED (a guess is a decision a search pass came back empty on; none is run under this feature), and the report lists
   it, so the open research is visible.
3. **Given** a drifted finding, **When** the feature lands, **Then** the code is unchanged and the index carries it as drifted.

---

### Edge Cases

- **A function renamed or moved** between modules: its claims are keyed by module and qualified name, so a rename is a new unit
  and owes a check (the code may have changed with it); the old rows are dropped.
- **A claim line edited** (its label, pointer or class): the claim's fingerprint changes, so it is owed.
- **A question renamed or renumbered** (`make fragment-move`): pointers in claims are rewritten with it, as every pointer is, and
  the question's findings did not change, so nothing is owed.
- **A question's intro or comments changed only** (feature 311's intro): its findings did not change, so nothing is owed.
- **A claim citing a question's drawing page**: the drawing page's findings are fingerprinted too.
- **A bare GUESS, an UNRESEARCHED, CONVENTION, CANON or "no physical decision" claim** cites no question; it is owed only when
  its code changes. A GUESS naming its drawing page is owed when that page's findings change too.
- **A DEVIATION claim** names the question it deviates from, and is fingerprinted with it.
- **A module-wide claim** (a module whose units all make no physical decision, say): each unit in the module without its own
  claim inherits it, and each such unit is its own row - an edit to one function owes that function's inherited claim only.
- **A function nested inside another**: part of its enclosing function's code; not a unit of its own.
- **A procedure section** of the magistracy or country-shrine procedure, or of the building vocabulary they draw on: a unit is a
  section, fingerprinted by its text with comments removed and its claim markers kept.
- **A change in a function another unit calls**: not followed into the caller's fingerprint (the stated limit); the callee's own
  claims are units of their own and are owed.
- **The audit's own dispatches** are the declared occasion of this feature; the owed command treats every claim as owed until its
  first verdict.
- **A verdict recorded in another clone** travels with the commit, since the index is committed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A CLAIM is one line in a `Research:` section of a docstring - a module's, a class's, a function's or a method's - or
  of a string literal placed directly after a module-level constant's assignment. Its grammar is `<label> - <backing>`, with an
  optional `: <what the code does>`; the backing is one or more research question files (`research/questions/NNNN-<id>.html`
  or its `.drawing.html`), or `GUESS` (a decision the record was searched for and is silent on, optionally naming the drawing page that records
  the guess), `UNRESEARCHED` (a decision no research pass has yet looked for), `CONVENTION`, `DEVIATION <question file>`,
  `CANON` (a decision the GM made - the setting's canon or the GM's ruling), or `NONE` (no physical decision). The form is
  read from the source text, without importing the engine.
- **FR-002**: SCOPE in code is every function, method, class and module-level constant (an upper-case name) of the hamlet
  generator package and of every engine module it imports, directly or indirectly - the import graph, computed from the source
  each time coverage is checked, so a module newly imported into hamlet generation comes into scope with it. Each carries at least one claim of its own or inherits its module's `Research:` claims. A unit with
  neither, a malformed claim, or a pointer to a question file that does not exist fails the gate, naming the unit and the claim
  form.
- **FR-003**: SCOPE in the procedures is every section of the magistrate's-manor and country-shrine procedures and of the Mode A
  building vocabulary document. Each carries at least one claim, in the same grammar, as a marked HTML comment; a section with
  none fails the gate.
- **FR-004**: A UNIT of the index is one claim of one function, method, class, constant or procedure section (own or inherited).
  Its fingerprint is (a) the code: the unit's syntax tree with docstrings removed (so comments and formatting do not count),
  plus the claim line itself, plus the values of the module-level constants of in-scope modules the unit names; for
  a procedure section, its text with HTML comments other than claim markers removed and whitespace normalized; and (b) the
  research: the findings of each question the claim cites (its words less its intro, as feature 311 reads them).
- **FR-005**: The INDEX is one committed file: per unit, its verdict, both fingerprints as the check read them, the date, and a
  one-line note of what the check found. Its verdicts are IN-STEP, DRIFTED, NEEDS-RESEARCH (the code decides something the
  record does not cover and the claim does not label a guess or unresearched), MISLABELED (the claim's class or pointer is wrong
  - a guess the record answers, a pointer to a question that does not bear on it, NONE on code that decides something
  physical), UNCLAIMED (the check found a physical decision in the unit that no claim covers; the note names it) and
  CANNOT-TELL (the check could not decide; UNRESOLVED, never a pass). Every verdict but IN-STEP is a FINDING.
- **FR-006**: One command names every OWED unit: a unit with no row, or whose current fingerprints differ from its row's; one per
  line, with the reason (new, code changed, research changed) and the command that builds its bundle.
- **FR-007**: One command builds a check BUNDLE outside the repository for a set of owed units: each unit's source (the function
  or section), its claim lines, the constants it names, and the cited questions' pages; a bundle for a unit not owed is refused
  unless given a stated reason.
- **FR-008**: A new defined check judges each unit in its bundle and returns a verdict per unit, plus each decision it found in
  the code that no claim covers. It is pinned to a tier (a judging check: Opus) like every defined check and launches without the
  project's auto-loaded files.
- **FR-009**: One command records a returned verdict into the index with the fingerprints the bundle recorded, so a verdict is
  stale once either side changes again. An UNCLAIMED finding is recorded as a row of its own on the unit (its label is the
  decision the check named); it stays a finding until a claim covering the decision is written and checked, when the row is
  dropped.
- **FR-010**: The push, on both routes, refuses a delta with an owed unit unanswered or stale, or with an INTRODUCED finding: a
  unit whose verdict is a finding at the head where the merge base's index held that unit IN-STEP, or held no row for it AND the
  delta created or changed the unit's code (its fingerprint less the claim line) or the findings of a question it cites. A unit
  that held a finding at the merge base and holds one at the head is PRE-EXISTING whether or not its code or research changed;
  so is a first finding on code and research the delta did not touch (the audit's own findings, feature 296's two rows, a unit
  merely renamed, whose code is unchanged under its new key). A pre-existing finding is printed as a warning, never refused.
  One stated reason discharges the refusal and is written to the bypass log.
- **FR-011**: One command prints the index as a REPORT: counts by verdict, then every unit not IN-STEP with its location, its
  claim and its note.
- **FR-012**: The hamlet walk-through shows, under each stage and step, its claims (own or inherited), each pointer a link to that
  question's page in the built record, each with its verdict from the index, and each class shown as the class it is.
- **FR-013**: Every unit in scope is claimed and checked once (the audit); the index is complete at landing. Findings are
  recorded, not fixed in the code: the claims are corrected (written, relabeled, an unresearched decision labeled UNRESEARCHED), and a
  DRIFTED finding stays in the index.
- **FR-014**: Feature 296 is closed as superseded by this feature, and its two findings - the row farm turned to its street (a
  second attested form the map does not draw) and the far row's dry-field share (attested over a range the map does not roll) -
  are rows of the index with verdict DRIFTED, each on the claim of the code that decides it.
- **FR-015**: The doctrine says how claims are written and when the check runs (the engine dev loop, the research rules, the
  project's guard table, the new check's own contract), and the gate's and the push's failure messages carry the compliant
  command.

### Key Entities

- **Claim**: a label, its backing (questions or a class) and an optional account of what the code does.
- **Unit**: one claim of one function, method, class, constant or procedure section.
- **Index row**: a unit, its verdict, the code and research fingerprints its check read, the date and a note.
- **Owed unit**: a unit with no row or with a stale row, and why.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-002, FR-003): Every function, method, class and constant in the hamlet generator package and the engine
  modules it imports, and every section
  of the three procedure documents carries a claim, own or inherited, and the gate fails on a fixture that removes one.
- **SC-002** (FR-004, FR-006): On prepared deltas, the owed command names exactly: one function's claims for an edit to its code;
  nothing for a comment, formatting or prose edit; a constant's claims and its readers' claims for a change to its value; every
  claim citing a question for a change to that question's findings; nothing for that question's intro alone.
- **SC-003** (FR-005, FR-007, FR-008, FR-009, FR-011, FR-013): At landing the report shows every unit with a verdict and none owed,
  and lists every non-IN-STEP unit.
- **SC-004** (FR-010): Dry pushes in tests: an owed unit refuses; a recorded verdict passes; an IN-STEP-to-DRIFTED unit refuses; a
  DRIFTED-to-DRIFTED unit passes with the warning, also when its code changed and it was re-checked DRIFTED; a first verdict DRIFTED on untouched code passes with the warning, and on
  changed code refuses; a reason passes and is logged.
- **SC-005** (FR-008): The new check, seeded with known units - one in step, one drifted (feature 296's dry-field share), one
  mislabeled (a guess the record answers), one unclaimed decision - returns the known verdict on each, three runs a leg.
- **SC-006** (FR-012): Every stage and every step of the built walk-through shows its claims, and every question pointer on it is a
  link that resolves to a page of the built record.
- **SC-007** (FR-014): Feature 296's spec says it is superseded by this feature, and the index holds its two findings as DRIFTED.
- **SC-008** (FR-015): The engine dev loop, the research rules and the guard table each say how a claim is written and when the
  check is owed, naming the commands.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Claims live in docstrings, one per line | this project's decision, on the GM's preference | the GM: *"Docstrings would be preferable to comments since docstrings are introspectable"*; one per line is the per-claim granularity the GM accepted | this spec; the engine dev loop |
| A constant's claim is a string literal after its assignment | this project's decision | a constant has no docstring; a literal after it is read from the syntax tree as one, and stays next to the value | this spec |
| A module's `Research:` claims are inherited by its units that carry none | this project's decision | a geometry module's every helper would otherwise carry the same "no physical decision" line; inheritance keeps the coverage enforceable without that repetition, and each inherited claim is still its own unit | this spec |
| Calls into other functions are not followed by the fingerprint | this project's decision, stated as the limit | following callees would owe nearly every claim on any edit; per-claim units and constants' own claims carry what is decided where | this spec; the owed command's docstring |
| Drift found by the audit is recorded, not fixed in the code | the GM's direction | the GM: *"what I am saying is not even about fixing anything it's just about doing an audit and then having an index"*; the push rule accepted makes pre-existing drift a warning | this spec |
| An unresearched decision is claimed UNRESEARCHED, not GUESS | this project's decision, from the GM's words and the research doctrine | the GM: *"whether something now must be marked as a guess or unresearched"*; the doctrine reserves "guess" for a decision a search pass came back empty on, and the audit runs no search pass | this spec; the engine dev loop |
| A CANON class, and a GUESS that may name the drawing page recording it (amendment, 2026-10-03) | this project's decision, from the record's own rule | the audit found claims resting on the GM's rulings and campaign notes labeled GUESS or UNRESEARCHED for want of a class; the research doctrine makes the GM's notes *"canon, not evidence"*, needing no citation, so a claim on them is neither a guess nor unresearched. And a figure a drawing page records as a guess had no way to name that page | this spec; `tools/claims.py`; the `impl-drift` contract |
| The index is committed, not kept per clone | this project's decision | the GM asked for *"an up-to-date index"*; a verdict must travel with the code it judged, unlike feature 311's answer records | this spec |
| The code scope is the hamlet generator package and every engine module it imports, measured from the import graph; towns, villages and cities as such are out, and so are the hand-drawn maps | the GM's direction | the GM: *"the code that generates a hamlet must have citations for anything that should be research derived"* - a shared module that runs in a hamlet's generation is that code (the dry-field size and placement of the GM's own example live in `settlement/fields/`); *"we're not talking about towns and villages and cities because those will eventually be scripted"*; the hand maps are not procedures, and generator work does not edit them (GM 2026-09-28) | this spec |
| The procedure scope adds the Mode A building vocabulary (`buildings.md`) to the two program sections | this project's decision, within the GM's words | the GM: *"our procedures for the manually generated maps ... magistracy buildings and country shrines"*; both programs are drawn with that vocabulary (walls, gates, wells, latrines, sacred features), so its rules are part of their procedure | this spec |
| The research fingerprint is the question's findings - its words less its intro and its comments - not its whole text | this project's decision, narrowing the proposal's "a hash of the cited question's text" | an intro (feature 311) cites nothing and says only why the question is asked, and a comment or a re-wrap changes nothing a reader is told; hashing the whole text would owe every claim on a maintenance sweep, the waste feature 311 removed | this spec; the owed command's docstring |
| A NEEDS-RESEARCH, MISLABELED, UNCLAIMED or CANNOT-TELL finding the delta introduces blocks the push, as a DRIFTED one does; pre-existing ones warn | this project's decision, extending the accepted rule, which named drifted rows | each is the implementation out of step with what the record backs, the GM's citation requirement; a CANNOT-TELL is a check that did not answer, so treating it as a pass would let the index claim what no check confirmed | this spec |
| UNCLAIMED and CANNOT-TELL are verdicts of their own | this project's decision | the proposal had the check flag an unclaimed decision; recording it as a row keeps it in the index until a claim is written; CANNOT-TELL keeps an undecided check visible rather than silently clearing the owed state | this spec |

## Assumptions

- The map modals keep their own check (`entry-drift` on a class's `Entry:`); this feature does not add claims to them.
- The tooling is written for any package or document; extending the scope beyond the hamlet generator is a later feature.
- The audit is dispatched in batches (one check per stage or module group) rather than one per unit, as the bundle allows.
- Claims are written by this session (or agents it dispatches). No research pass is run under this feature: a decision the record
  does not cover is claimed UNRESEARCHED, never GUESS, because the research doctrine reserves "guess" for a decision a search
  pass came back empty on (CLAUDE.md, Research). The report lists the UNRESEARCHED claims as the open research.

## Review history

- **Round 1** (`spec-fidelity`, 2026-10-02): CHANGES REQUIRED - six items: the code scope cut to `hamletgen` where the GM said
  the code that generates a hamlet (the dry-field size and placement live in `settlement/fields/`); FR-010's "or held no row"
  refusing the audit's and 296's pre-existing findings at this feature's own landing; NEEDS-RESEARCH and MISLABELED blocking
  unrecorded and silent when pre-existing; CANNOT-TELL unproposed and clearing the owed state; no requirement recording an
  unclaimed decision; two departures unrecorded (the research fingerprint, `buildings.md`). All six applied: FR-002 scopes the
  import graph (measured in Context); FR-010 defines INTRODUCED and PRE-EXISTING, with a seventh scenario; every non-IN-STEP
  verdict is a FINDING, refused when introduced and warned when pre-existing; CANNOT-TELL is unresolved; UNCLAIMED is a verdict
  recorded per FR-009; four Decisions Recorded rows added and the scope row rewritten.
- **Round 2** (`spec-fidelity`, 2026-10-02): all six round-1 items RESOLVED; one new: FR-010's "or the delta changed its code"
  refused a unit already drifted at the base once its code or research was touched, against the accepted rule and US4
  scenario 4. Applied: the code-or-research clause applies only where the base held no row; a finding at both ends is
  pre-existing whatever changed; SC-004 adds the re-checked-DRIFTED case.
- **Round 3** (`spec-fidelity-verify`, 2026-10-02): **FAITHFUL** - the round-2 item resolved, no new departure.
- **Amendment after acceptance** (2026-10-03, the audit's second round): FR-001 gains `CANON` and a GUESS that may name its
  drawing page; one Decisions Recorded row. The counter resets for this amendment.
