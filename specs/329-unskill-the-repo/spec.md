# Feature Specification: Unskill the repository

**Feature Branch**: none (main, `SPECIFY_FEATURE=329-unskill-the-repo`)

**Created**: 2026-10-07

**Status**: Draft

**Input**: the GM's request, verbatim in [`request.md`](request.md): stop keeping the diagram project as a Claude
Code skill under `.claude/skills/diagram/` and refactor it out, "taking the feature from start to finish".

## Summary

The repository was born as one skill of gm-assistant and was split out with the skill directory intact. Nothing
uses it as a skill any more: gm-assistant has no `diagram` skill, nobody invokes `/diagram`, and the nested
`CLAUDE.md` files load by directory wherever that directory is. What remains is the cost: every pointer in the
project carries the `.claude/skills/diagram/` prefix, the project has two Makefiles and two config roots, and the
real project lives inside a tool-configuration directory. This feature moves the project to the repository root
and retires the skill.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The project lives at the root (Priority: P1)

The GM, or a session, opens the repository and finds the engine, the pool, the research record, the building
vocabulary and the tests at the top level, runs every `make` target from the root, and follows every pointer in a
live document, script, hook or agent file to a file that exists.

**Why this priority**: it is the request.

**Independent Test**: after the move, the whole gate (`make done`) is green from the repository root, the hook
suite (`make hooks-test`) is green, and a scan of every live file finds no pointer to the old location.

**Acceptance Scenarios**:

1. **Given** a fresh clone of main after the feature lands, **When** a session runs `make done` at the clone root,
   **Then** the gate runs every phase it ran before the move and is green.
2. **Given** the same clone, **When** any live file (outside the feature history in `specs/` and the verbatim
   records) is searched for the old prefix, **Then** nothing is found.
3. **Given** the same clone, **When** Claude Code lists its skills, **Then** `diagram` is not among them.

---

### User Story 2 - Nothing already working is lost (Priority: P1)

Every guard, gate, record check, review agent, CodeBuild definition, render-sync and research tool does what it
did before, against the new paths.

**Why this priority**: constitution XIII - no known regressions. A move that leaves one guard silently matching
nothing is a regression nobody sees.

**Independent Test**: the hook suite, the gate and the push-time checks are green; every guard that matches on a
path is shown, by a test, to fire on the new path.

**Acceptance Scenarios**:

1. **Given** a guard that refused or rewrote a command naming a file under the old location, **When** the same
   command names that file at its new location, **Then** the guard behaves exactly as before.
2. **Given** the gate's warm caches in a clone before the move, **When** that clone syncs in the move, **Then** the
   caches are carried to the new location (or deliberately invalidated, with the reason recorded), and nothing is
   left behind at the old location.

---

### User Story 3 - The other clones survive the landing (Priority: P2)

A session in another clone, mid-feature, syncs in and carries on.

**Why this priority**: many clones exist and some hold unpushed work; a move that strands them costs more than
it saves.

**Independent Test**: a scratch clone with an unpushed commit that edits a moved file and adds a new file under
the old location syncs in cleanly; its edits land on the moved files and its new file lands at the new location.

**Acceptance Scenarios**:

1. **Given** a clone with a commit editing a file at its old path, **When** it syncs in, **Then** the edit is
   applied to the file at its new path with no conflict.
2. **Given** a clone that later tries to land a file or pointer naming the old location, **When** it pushes,
   **Then** the push is refused with the new path in the message.

---

### Edge Cases

- A name that collides at the root: the root already has `CLAUDE.md`, `Makefile` and `.gitignore`, and so does the
  skill directory. Each is merged, never overwritten.
- Gitignored artifacts (renders, the generation cache, the built record site, test caches) do not move with
  `git mv`; a clone or the mirror that syncs in keeps them at the old location unless something carries them.
- Records keyed on a path (cache keys, gate stamps, perf and run records, the testmon database, the review ledger,
  recorded command corpora used as hook fixtures) may silently stop matching.
- The feature history in `specs/` names the old paths about a thousand times; it is history and is not rewritten.
- gm-assistant has one document naming the old path; this repository does not edit gm-assistant.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Everything under `.claude/skills/diagram/` MUST move to the repository root at the same relative
  path, by `git mv` so history follows, except the names FR-002 and FR-003 settle. The directory
  `.claude/skills/diagram/` MUST NOT exist afterward.
- **FR-002**: The three colliding files MUST be merged: one `Makefile` at the root holding every target (the root
  forwarder retires), one `.gitignore` at the root holding both sets of rules with their paths corrected, and one
  root `CLAUDE.md` that absorbs the skill directory's index without growing what a research session loads.
- **FR-003**: `SKILL.md` MUST stop being a skill: its content becomes a usage document under `docs/`, with its
  frontmatter dropped and its links corrected, and the root `CLAUDE.md` names it.
- **FR-004**: Every live pointer to the old location MUST be rewritten to the new one: scripts, hooks and their
  tests, agent files, the Makefile, buildspecs, the CI Dockerfile, container scripts, docs, the moved files
  themselves (code, comments, docs, research comments), and the `.claude/settings.json` hook commands. Live means
  everything except the feature history (`specs/`) and verbatim records (`dev/*-log/`, review-ledger rows written
  before this feature, recorded command corpora); the plan names each verbatim record and how its tests stay
  meaningful.
- **FR-005**: The feature history MUST be left as written, and one note MUST tell a reader of an old spec how to
  read an old path (drop the prefix).
- **FR-006**: Every guard, gate, push check and record tool that matches on a path MUST behave on the new path as
  it did on the old one, each shown by a test.
- **FR-007**: A check MUST refuse a live file that names the old location, at the gate and at the push, with the
  new path in its message.
- **FR-008**: Syncing in the move MUST carry each clone's and the mirror's gitignored artifacts from the old
  location to the new one (or invalidate a cache that cannot be carried, recorded with why) and leave no
  `.claude/skills/diagram/` directory behind.
- **FR-009**: A clone with unpushed commits against the old paths MUST be able to sync in the move, shown by a test
  on a scratch clone.
- **FR-010**: The gate (`make done`) and the hook suite (`make hooks-test`) MUST be green from the repository root
  after the move, with no phase lost and no test dropped.
- **FR-011**: The project's own documents that explain the skill (the root `CLAUDE.md` opening,
  `dev/skill-boundary.md`, the usage document) MUST say the project is no longer a skill and why, once.

### Key Entities

- **Live file**: any tracked file outside `specs/` and the verbatim records FR-004 names.
- **Verbatim record**: a file that quotes what happened at a time and must not be rewritten to say otherwise.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero live files name the old location, counted by the FR-007 check (FR-001, FR-004, FR-007).
- **SC-002**: The gate and the hook suite are green from the root, with the same test count or more than the
  baseline taken before the move (FR-002, FR-006, FR-010).
- **SC-003**: Claude Code's skill list in a session started in a clone after the move does not include `diagram`,
  and `docs/` holds the usage document the root `CLAUDE.md` names (FR-003, FR-011).
- **SC-004**: After sync-in, a clone holding warm caches has no `.claude/skills/diagram/` directory and its first
  gate is no slower than a warm gate on the baseline, within the gate's own ratchet tolerance (FR-008).
- **SC-005**: The scratch-clone sync test passes, and an old spec's path resolves by the FR-005 note
  (FR-005, FR-009).

## Decisions Recorded

This feature draws and states nothing on a map; it is tooling. Its layout decisions are recorded in `plan.md`.

## Assumptions

- The move lands as one commit between features: feature 328's session is told by the push-time refusal and the
  sync-in carry, not by hand.
- The loose documents at the skill root (`buildings.md`, `hamletgen.md`, `migration-plan.md` and the rest) move to
  the root at the same relative path; tidying them into `docs/` is a separate decision, not taken here, so the
  move stays a prefix strip that a reviewer can check mechanically.
- The CodeBuild remote is off; its definitions are updated and checked locally, not dispatched, unless the plan
  finds a cheap way to prove them.
- gm-assistant's one pointer (`docs/iteration-loop.md`) is reported to the GM, not edited.
