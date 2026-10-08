# Feature Specification: Open work as features

**Feature Branch**: none (main, `SPECIFY_FEATURE=330-open-work-as-features`)

**Created**: 2026-10-08

**Status**: Draft

**Input**: the GM's request, verbatim in [`request.md`](request.md): know which spec-kit features were filed and
never worked, and which were started and never finished; delete any that belong to gm-assistant; turn everything in
`future-work/` into an unimplemented spec-kit feature and retire the directory; and add a make target - the GM named
`make speckit-todo` - that lists the features not yet implemented and the partially implemented ones.

## Summary

Deferred work lives in two places today: `future-work/` (five files of entries by map type) and the spec-kit
features under `specs/`, some of which were filed and never worked or started and never finished. Nothing answers
"what is still open?" in one place, and a feature's real state is often not what its files say: of the 246 feature
directories, 27 have open or no tasks while several of those say "Implemented" on their status line. This feature
makes `specs/` the one home of open work, makes every feature's state readable by a command, and settles the state
of every existing feature once.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask the tooling what is open (Priority: P1)

The GM, or a session, runs `make speckit-todo` and sees every feature that is not finished: the ones filed and never
started, the ones planned but not begun, and the ones partly done, each with its number, its title and how far it
got. Finished and closed features are left out, so the list is the work.

**Why this priority**: it is what makes the rest worth doing - once the open work lives in `specs/`, this command is
how anyone finds it.

**Independent Test**: on a fixture `specs/` tree holding one feature in each state, the command lists exactly the
open ones under the right heading and none of the closed ones.

**Acceptance Scenarios**:

1. **Given** a feature with only a `spec.md`, **When** `make speckit-todo` runs, **Then** it is listed as filed,
   not started.
2. **Given** a feature whose tasks are partly ticked, **When** it runs, **Then** it is listed as in progress with
   its ticked and total counts.
3. **Given** a feature whose tasks are all ticked, or whose status says it was finished, superseded or withdrawn,
   **When** it runs, **Then** it is not listed.

---

### User Story 2 - Every existing feature has a true state (Priority: P1)

Every one of the 246 existing feature directories reads as what it really is. A feature that was implemented but
left with unticked tasks says it is done; one that a later feature replaced says which; one the GM dropped says it
was withdrawn; one still wanted stays open with its remaining work visible. Any feature that belongs to gm-assistant
rather than this repository is deleted.

**Why this priority**: without it, User Story 1's list is wrong on day one - it would list as open work that was
finished, superseded or dropped months ago.

**Independent Test**: after the audit, every feature `make speckit-todo` lists is one a reader of its spec would
agree is open, and every feature it omits is finished, superseded or withdrawn by its own files' say-so.

**Acceptance Scenarios**:

1. **Given** a feature marked "Implemented" with unticked tasks, **When** the audit settles it, **Then** its status
   says it is done (or its truly-outstanding tasks stay open and it is listed as in progress).
2. **Given** a feature the GM dropped (for example the capital's hand pass, dropped 2026-10-07), **When** the audit
   settles it, **Then** its status says withdrawn and names the ruling.
3. **Given** the whole `specs/` tree, **When** the audit is done, **Then** no feature is about gm-assistant's
   webapp or other content outside this repository.

---

### User Story 3 - future-work/ becomes features (Priority: P2)

Every open entry in `future-work/` becomes its own unimplemented feature under `specs/`, carrying the entry's text,
and `future-work/` is removed. An entry that turns out to be already done - or that a recorded GM ruling or a later
feature disposed of - is closed instead, with the evidence, rather than filed. Every pointer to a `future-work/` entry - code comments, notes, docs - names the feature
it became.

**Why this priority**: it is the GM's stated end state; it depends on User Story 1 so the filed features are
findable.

**Independent Test**: after the conversion, `future-work/` does not exist, the number of features filed plus the
number of entries closed equals the number of entries there were, and no live file points into `future-work/`.

**Acceptance Scenarios**:

1. **Given** an open entry in `future-work/towns.md`, **When** it is converted, **Then** a new feature exists whose
   spec carries the entry's text and says it was filed from `future-work/`, and `make speckit-todo` lists it as
   filed.
2. **Given** a code comment citing a `future-work/` entry by title, **When** the conversion lands, **Then** the
   comment names the feature instead.
3. **Given** the conversion has landed, **When** a session wants to defer new work, **Then** the project's rules
   tell it to file a feature (claim a number, write its spec) - there is no `future-work/` to add to.

### Edge Cases

- A feature directory with no `spec.md` (a claim abandoned before a spec was written): listed as filed, flagged as
  having no spec, never silently skipped.
- Two features with the same number (`196-fengshui-grove-sizes` and `196-warm-and-cold-ratchets` already exist):
  both listed, by directory name.
- A `tasks.md` whose checkboxes use a form the counter does not read: the feature is listed rather than hidden, so a
  parsing miss shows up as open work, not as finished work.
- A status line that says "Implemented" but tasks that are open: the tasks decide until the audit settles it; the
  command does not trust free text it cannot parse.
- A `future-work/` entry that is several pieces of work: it becomes one feature per piece where the entry itself
  names separate pieces (FR-006); otherwise one feature.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `make speckit-todo` MUST list every feature under `specs/` that is not closed, grouped by state -
  filed (no tasks yet), planned (tasks, none ticked), in progress (some ticked) - with its number, title and, where
  it has tasks, ticked and total counts. It MUST end with the count in each state.
- **FR-002**: A feature MUST count as closed when every task in its `tasks.md` is ticked, or when its spec's
  `**Status**:` line begins with one of a fixed, documented set of closing words (finished, superseded by a named
  feature, withdrawn). The set MUST be stated once, where the command and its tests both read it.
- **FR-003**: The command MUST read only `specs/`, change nothing, need no network, and finish in under 2 seconds
  over the current tree.
- **FR-004**: Every existing feature MUST be settled once: each feature that is open by FR-002 is either left open
  because its work is still wanted, or closed by editing its status line to say why (done, superseded by which
  feature, or withdrawn by which ruling). The settlement of each MUST be recorded in this feature's audit, with the
  evidence (the commits or later feature that did the work, or the ruling).
- **FR-005**: Any feature whose subject is gm-assistant's and not this repository's MUST be deleted, and the audit
  MUST say what was checked and what was found.
- **FR-006**: Every entry in `future-work/` MUST become one new feature - or one per piece where the entry itself
  names separate pieces (as `compounds.md`'s "Research owed" does) - with its own claimed number and a `spec.md`
  carrying the entry's text verbatim and naming the file and heading it came from, status filed. An entry found
  already done MUST be closed instead and listed in the audit with its evidence (the commits or the feature that did
  the work); an entry may also be closed where a recorded GM ruling, or a later feature that replaced it, is cited.
  Every other entry is filed - including an OWED AT CONVERSION entry whose task `future-work/` calls dead.
- **FR-007**: `future-work/` MUST be removed, and every live pointer to it or to one of its entries MUST be re-aimed
  at the feature the entry became, or dropped where the entry was closed.
- **FR-008**: The project's rules (the root `CLAUDE.md`, and every doc that told a session to add to `future-work/`)
  MUST say instead that deferred work is filed as a feature, and how.
- **FR-009**: The command MUST be listed in the generated make-target reference and covered by tests: one fixture
  feature per state, the closing words, a feature with no `spec.md`, and a feature whose checkboxes it cannot read.

### Key Entities

- **Feature**: a directory under `specs/` named `NNN-slug`; its state is derived from its own files.
- **Feature state**: filed, planned, in progress (open) or closed; closed carries its reason.
- **Open entry**: a `future-work/` item that names work not yet done.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: One command answers "what is open?" across the whole repository, in under 2 seconds.
- **SC-002**: After the audit, every feature the command lists is open by its own spec's account; a spot check of
  ten listed and ten unlisted features finds none misclassified.
- **SC-003**: `future-work/` no longer exists; every entry is accounted for - filed as a feature (one per named
  piece), or closed as done or by a cited ruling or later feature - with none dropped.
- **SC-004**: No live file points into `future-work/`.
- **SC-005**: No feature in `specs/` is about gm-assistant's own content.

## Assumptions

- A feature whose remaining unticked tasks were done (the commits or a later feature show it) is closed as done. It
  is closed as withdrawn-in-part only where a recorded ruling or a later feature dropped or replaced those tasks,
  cited in the audit; otherwise it stays open and is listed for the GM.
- Where a feature's fate needs the GM's judgment - the record holds no ruling and the work could still be wanted -
  it stays open and is listed for the GM, rather than closed on a guess.
- Feature numbers for the new features come from `make claim`, one per entry, so concurrent sessions cannot collide.
- Converting an entry carries its text as written; rewording it into a full spec is the work of whoever picks the
  feature up.
- This feature draws and states nothing on a map, so it records no rendering decisions.
