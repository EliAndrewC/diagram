# Feature 301 - the record as a manual

**Feature Branch**: none (main, in the clone `diagram-reorg`)
**Created**: 2026-10-01
**Status**: Draft
**Request**: [`request.md`](request.md) - the GM's words verbatim: the research assembled into *"a single page version ...
with a linkable table of contents at the very top"* and *"a page structure where anything that would be a top-level table
of contents entry ... will be its own separate parent section and then maybe each of our subsections are themselves
individual pages within the larger section, which are linked on the left"*; map links *"to the smaller pages"*; the
assembled files out of source control but *"on the main checkout"*, regenerated on landing like the map renders; pointers
to *"the source which is fed into and used to generate that HTML page"*; the history scrubbed and repacked; and a hook that
reminds a session of its sudo access whenever any check finds a program missing.
**Predecessors**: 258 (the record written per entry and assembled), 211 (citations pages), 292 (the rendering collection
and its cross-links), and the render-sync model of 2026-07-22 (`scripts/sync-with-main.sh`).

## Summary

The research record is already written as one fragment per question and assembled by `make record` into 37 pages plus the
sources registry and a citations page beside each. This feature changes only what the assembly writes, and where it lives:

1. **Two forms of one manual.** A multi-page site with a navigation tree on the left: each current page (fields, homesteads,
   each rendering and cities page, the sources registry) is a parent section, and each question and each registry entry is
   its own small page. Beside it, one single page holding the whole record - research, rendering, citations and sources -
   under a linked table of contents. The left navigation links the single page.
2. **Footnotes.** A small page numbers its notes from 1 and carries its own notes and the sources they cite at its foot. The
   single page numbers once, through the whole record.
3. **Map links** go to the small per-question pages.
4. **Out of git, onto main.** Every assembled output is gitignored and dropped from the index; render-sync builds it in the
   main checkout when, and only when, something it is built from changed.
5. **Pointers name the source.** The rule that a rendering decision points at its research stays; the pointer names the
   fragment, every pointer is checked to resolve, and a rename carries its pointers with it.
6. **History.** After the feature lands, the assembled-page versions committed since feature 258 are removed from the
   history (the session builds and verifies it; the GM force-pushes), and the main checkout is repacked.
7. **A sudo reminder.** Whenever a command fails for a missing program, or any check for a program comes up empty, the
   session is reminded it has passwordless sudo in this container to install it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read the record as a manual (Priority: P1)

The GM opens the research and finds a left-hand tree of sections and questions, reads one question per page with its notes
at the foot, and can open the whole record as one page to read straight through or search.

**Why this priority**: it is the request.

**Independent Test**: build the record; open a small page, the single page, and follow the tree.

**Acceptance Scenarios**:

1. **Given** the built record, **When** the GM opens any small page, **Then** the left navigation lists every parent
   section, the current section's questions, and a link to the single page, and the current page is marked.
2. **Given** a small page with footnotes, **When** the GM reads it, **Then** its notes are numbered from 1, the hover over a
   reference shows the note as it does today, and the foot of the page lists exactly the notes and the sources that page
   cites - no others.
3. **Given** the single page, **When** the GM opens it, **Then** a table of contents at the top links every parent section
   and every question, the research, rendering, citations and sources are all on it, and its notes are numbered once from 1
   through the whole page.
4. **Given** a link inside the record to another question (a cross-link, a rendering/research `xref`, a typed link), **When**
   the GM follows it on a small page, **Then** it reaches that question's small page; on the single page, its anchor on the
   single page.

### User Story 2 - A map links to the question (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a rendered interactive map, **When** the GM opens a modal and clicks a research question, **Then** the
   question's small page opens - never the single page, never a whole section.

### User Story 3 - The assembled record is built on main, not committed (Priority: P1)

**Acceptance Scenarios**:

1. **Given** the feature landed, **When** `git ls-files` is run on main, **Then** no assembled page, citations page,
   derived script or single page is tracked; the fragments, the hand-written assets and the build code are.
2. **Given** a landing that changed a fragment, **When** render-sync runs on the main checkout, **Then** the record there is
   rebuilt and current; **Given** a landing that changed nothing the record is built from, **Then** render-sync skips the
   build.
3. **Given** a fresh clone, **When** a session runs `make record`, **Then** the whole record is built there.

### User Story 4 - Pointers reach the canonical research (Priority: P1)

**Acceptance Scenarios**:

1. **Given** the code, docs, specs, skill files and modal `Entry:` lines, **When** they cite research, **Then** they name a
   fragment path under `research/`, and the gate fails naming every pointer that does not resolve to a fragment.
2. **Given** a fragment renamed or moved by the record's tooling, **When** the change is made, **Then** every pointer to it is
   rewritten in the same change.
3. **Given** an old pointer `research/<page>.html "Heading"` that matches no fragment exactly, **When** the sweep runs,
   **Then** it is listed for review and not guessed.

### User Story 5 - A lean history (Priority: P2)

**Acceptance Scenarios**:

1. **Given** the feature landed, **When** the session builds the rewritten history, **Then** every assembled-page version
   committed from feature 258 (commit `0fef1e6f3`) onward is gone, the pre-258 versions of those paths (the hand-written
   source of that time) are kept, every commit's tree is otherwise identical to the original's, and the tip's tree is
   byte-identical.
2. **Given** the verified history, **When** the GM force-pushes it, **Then** the main checkout is reset to it and repacked,
   every session clone is replaced, and the other live session's unpushed work is carried onto the new history.
3. **Given** a clone that still holds the old history, **When** it syncs, **Then** the sync refuses rather than merging the
   two histories.

### User Story 6 - A missing program reminds the session of sudo (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a Bash command whose output says a program is not found (`command not found`, an executable's `No such file or
   directory`), **When** it finishes, **Then** the session receives a short note that it has passwordless sudo here and the
   likely package to install.
2. **Given** an existence check that comes up empty - `which`, `command -v`, `type`, `hash`, `whereis`, `dpkg -s`,
   `dpkg -l`, `apt list --installed`, `apt-cache policy`, `pip show`, `pip list | grep`, `python -c "import x"`,
   `test -x`/`[ -x ]` on a program path, `ls` of a binary path, `<program> --version` - **When** it finishes, **Then** the same
   note is added.
3. **Given** a check that FINDS the program, or an unrelated failure, **When** it finishes, **Then** no note is added.
4. **Given** a Claude Code session on the GM's host (not in a container), in any project, **When** a program is missing,
   **Then** no note is added; **Given** a session in any container, in any project, **Then** the note is added.

### Edge Cases

- A question cites no source: its small page has no notes block.
- A note cites a source several times on one small page: the source is listed once at the foot.
- A heading id must be unique across the whole record (it is the single page's anchor and the small page's name); on
  2026-10-01 the 473 questions' ids collide nowhere, and the build refuses a collision.
- A pointer in a spec of a LANDED feature is history: the sweep rewrites it all the same so the resolve check covers every
  file, and the request files the GM wrote are left alone (SOURCE text, quoted).
- The single page is large (about 11 MB summed across the assembled pages, observed 2026-10-01 by `du` on `research/`); it is built but never committed, and the small pages are
  what the maps link.
- The scrub runs only after the feature's landing; a clone created between the landing and the force push is replaced with
  the rest.
- The sudo note fires at most once per distinct program per session, so a loop of misses does not flood the context.

## Requirements *(mandatory)*

### Functional Requirements

**The two forms**

- **FR-001**: `make record` MUST build, from the fragments alone, a multi-page site: one parent page per current page
  (each research page, each `rendering/` and `cities/` page, the sources registry) and one small page per question and per
  registry entry.
- **FR-002**: Every small and parent page MUST carry a left navigation listing every parent section, expanding the current
  section's questions, marking the current page, and linking the single page.
- **FR-003**: `make record` MUST build the single page: the whole record - every research and rendering question, every
  citation, the sources registry - under a table of contents at its top that links every parent section and question.
- **FR-004**: A small page MUST number its footnotes from 1 and end with its notes and the list of sources its notes cite,
  only those; the footnote hover MUST work as it does today.
- **FR-005**: The single page MUST number its footnotes once through the whole record.
- **FR-006**: Every link the assembly writes or copies between questions (the rendering/research cross-links, typed links,
  the "not to be confused with" lists, glossary and source links) MUST resolve in each form: to the small page in the site,
  to the anchor on the single page. A link that resolves nowhere MUST fail the build.
- **FR-007**: The build MUST refuse a heading id used twice across the record.

**The maps**

- **FR-008**: A map modal's research link MUST open the question's small page.

**Out of git, onto main**

- **FR-009**: Every assembled output - the pages, the citations pages and their scripts, the registry page, the derived
  glossary script, the site and the single page - MUST be gitignored and removed from the index.
- **FR-010**: render-sync MUST build the record in the main checkout when anything it is built from changed since the
  last build there, and skip it otherwise, on the map renders' model.
- **FR-011**: Every gate check that compared a derived record file with its committed copy MUST become a check that the
  record builds cleanly from the fragments.

**Pointers**

- **FR-012**: Every pointer to the research in code, docs, specs, skill files, agent files and modal `Entry:` lines MUST
  name a fragment path; the modal machinery MUST read the new form.
- **FR-013**: The existing `research/<page>.html "Heading"` pointers MUST be swept to fragment paths; a pointer matching no
  fragment exactly MUST be listed for review, never guessed.
- **FR-014**: The gate MUST fail on any fragment pointer that does not resolve, naming it.
- **FR-015**: The record's tooling that renames or moves a fragment MUST rewrite every pointer to it in the same change.
- **FR-016**: `CLAUDE.md`, the research `CLAUDE.md`, the constitution's wording if it names the page form, and the
  research doctrine MUST say a pointer names the fragment.

**History**

- **FR-017**: After the feature lands, the session MUST build a rewritten history with every assembled-output version
  committed from `0fef1e6f3` onward removed and the pre-258 versions kept, and verify it: each commit's tree equals the
  original's less the removed paths; the tip's tree is byte-identical; before and after sizes measured.
- **FR-018**: The session MUST coordinate with every live session before the GM's force push - each pushes or hands over
  its unpushed commits - and after it reset and repack the main checkout, replace every clone, and replay any unpushed
  commits onto the new history.
- **FR-019**: `scripts/sync-with-main.sh` MUST refuse to sync a clone whose history shares no commit with main's, naming
  the re-clone command.
- **FR-020**: An old-to-new commit map for the rewritten range MUST be recorded under `docs/`.
- **FR-021**: The session MUST run `git gc --aggressive --prune=now` on the main checkout under the sync lock.

**The sudo reminder**

- **FR-022**: A PostToolUse hook on Bash MUST add a short note - passwordless sudo is available here, and the package that
  likely provides the program - whenever a command's output says a program was not found, or any program-existence check
  (the forms in User Story 6) comes up empty.
- **FR-023**: The hook MUST stay silent when the program is found or the failure is unrelated, and note a program at most
  once per session.
- **FR-024**: The hook MUST be USER-LEVEL, in every project the GM runs (GM, 2026-10-01: *"I do want this hook to apply to
  all of my projects. In many different directories, in many different containers"*): its script under `~/.claude/hooks/`
  and its registration in `~/.claude/settings.json` - the host's own `~/.claude`, which every container mounts - not in
  this repository's settings.
- **FR-025**: The hook MUST fire only inside a container (GM: *"all containers have sudo access"*, and host sessions do
  not): it detects a container (podman's `/run/.containerenv`, docker's `/.dockerenv`, a container cgroup or `container`
  environment variable) and is silent on the host.
- **FR-026**: The hook MUST have a self-test beside it under `~/.claude/hooks/` (every listed form fires in a container;
  a found program, an unrelated failure, and any miss on the host stay silent), run by this repository's `make hooks-test`
  when present, and a row in `docs/guards.md` and the `CLAUDE.md` guard table marking it user-level.

### Key Entities

- **Fragment**: one question, one registry entry, or a page's front/tail; the canonical record and the target of every pointer.
- **Parent section**: one current page's fragments in order; a page of the site and a table-of-contents entry of the single page.
- **Small page**: one question or registry entry with its own notes and sources at its foot.
- **Single page**: the whole record under one table of contents, one footnote count.
- **Pointer**: a fragment path named outside the record.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001-FR-003): after `make record`, one small page exists per question and per registry entry, one parent
  page per current page, and one single page; a test walks the navigation from every page.
- **SC-002** (FR-004, FR-005): a test finds every small page's notes numbered 1..n with the foot listing exactly the cited
  notes and sources, and the single page's notes numbered 1..N across the record.
- **SC-003** (FR-006, FR-007): a link check over both forms finds zero unresolved links; a seeded duplicate id fails the build.
- **SC-004** (FR-008): every modal research link in the pool's rendered maps resolves to an existing small page.
- **SC-005** (FR-009-FR-011): `git ls-files` lists no assembled output; render-sync rebuilds after a fragment change and
  skips after an engine-only change (measured); the gate passes.
- **SC-006** (FR-012-FR-016): zero pointers to an assembled page remain outside the record and quoted GM text; the resolve
  check fails on a seeded bad pointer; a rename test rewrites its pointer; the review list from the sweep is empty or
  resolved.
- **SC-007** (FR-017-FR-021): the rewritten history verifies tree-for-tree; `.git` on the main checkout measured before and
  after (observed 2026-10-01; method: `du -sh` on the main checkout's `.git` and on a scratch mirror after
  `git gc --aggressive` with and without a full scrub: 236, 102 and 85 MB - so expected about 85-90 MB after); every clone's root commit matches main's; a seeded unrelated-history clone is refused.
- **SC-008** (FR-022-FR-026): the hook's self-test fires on every listed form in a container and stays silent on found
  programs, unrelated failures and every miss with the container markers absent; the hook is registered in
  `~/.claude/settings.json`, not in this repository's.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

This feature draws nothing and states nothing new on a map; it changes where a modal's research link points (FR-008). No
rendering decision is made.

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Small pages number notes from 1; the single page numbers once | map drawing convention (presentation) | GM accepted, 2026-10-01 | this spec; the record's assembly |
| Modal links open the small page | map drawing convention (presentation) | GM, 2026-10-01 second message | this spec; `interactive/sources.py` |

## Assumptions

- The registry's entries become small pages too (the fragment is the unit, and a footnote's source link needs a page to land on).
- Today's look and the footnote hover carry over; the left navigation is plain HTML and CSS, no framework.
- The rendering/research cross-link pairs (feature 292) stay as they are, resolved per form.
- The GM's force push is the only push this feature cannot make itself; everything before and after it is the session's.
- Diagram review is the one other live session on 2026-10-01; the coordination covers whatever sessions are live at the time.
- `git-filter-repo` is installed with sudo for the rewrite.
