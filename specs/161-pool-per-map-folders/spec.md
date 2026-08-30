# Feature Specification: One folder per map, and the frozen hand-authored pool moved out of `pool/`

**Feature Branch**: none - this project does not use feature branches (CLAUDE.md, GM 2026-07-27). `SPECIFY_FEATURE=161-pool-per-map-folders`.

**Created**: 2026-08-30

**Status**: Draft

**Input**: The GM's request, verbatim:

> I would like to move settlements in our pool into their own individual folders, e.g. currently I see this:
>
> ```
> eli@mujina:~/l7r/diagram$ ls ./.claude/skills/diagram/pool/hamlets/
> akagahara.gen.py    honda.gen.py      inashiro.gen.py     kashikawa.png      mizuguchi.json      sawada.html       tanada.gen.py
> akagahara.json      honda.json        inashiro.html       kashikawa.svg      mizuguchi.notes.md  sawada.json       tanada.json
> akagahara.notes.md  honda.notes.md    inashiro.json       kuwabata.gen.py    mizuguchi.png       sawada.notes.md   tanada.notes.md
> akagahara.png       honda.png         inashiro.notes.md   kuwabata.html      mizuguchi.svg       sawada.png        tanada.png
> akagahara.svg       honda.svg         inashiro.png        kuwabata.json      moritono.gen.py     sawada.svg        tanada.svg
> enokida.gen.py      ikegami.gen.py    inashiro.svg        kuwabata.notes.md  moritono.json       shimizu.gen.py    yatsuda.gen.py
> enokida.json        ikegami.json      kashikawa.gen.py    kuwabata.png       moritono.notes.md   shimizu.json      yatsuda.json
> enokida.notes.md    ikegami.notes.md  kashikawa.html      kuwabata.svg       moritono.png        shimizu.notes.md  yatsuda.notes.md
> enokida.png         ikegami.png       kashikawa.json      mizuguchi.gen.py   moritono.svg        shimizu.png       yatsuda.png
> enokida.svg         ikegami.svg       kashikawa.notes.md  mizuguchi.html     sawada.gen.py       shimizu.svg       yatsuda.svg
> ```
>
> and I would like `akagahara/` and `enokida/` and `honda/` etc to each be their own individual folders with their relevant files inside.
>
> Also, many of those hamlets are hand-authored rather than scripted, so I think we should move every settlement which is hand-authored out of the `pool/` directory and into a `legacy-hand-authored-pool/` directory. Diagrams which have no plans to become hand-authored (currently this is only the `magistracies/` folder, but I expect other buildings will continue to always be hand-authored because they are sufficiently small as to not require a scripted process to make them able to generated in a short time) should stay in the existing `pool/` directory but should also move into subfolders.
>
> The `pool/index.html` should be updated, along with anything in the codebase which references or relies on the old directory structure.

---

## User Scenarios & Testing *(mandatory)*

The user here is the GM, who browses the pool as **files on disk** and as **`pool/index.html`**, and
the sessions that work on the pool through `make`.

### User Story 1 - One map, one folder (Priority: P1)

The GM lists a tier folder and sees one entry per settlement, not five files per settlement
interleaved alphabetically with every other settlement's five. Opening a settlement's folder shows
that map's whole bundle - generator, manifest, notes, and the three renders - together.

**Why this priority**: This is the request's first sentence and its motivating example. The listing
the GM pasted is 65 files in one flat directory, in which the five files belonging to one map are
scattered across five columns; the fix is what makes the pool legible at all.

**Independent Test**: `ls` any tier folder in the live pool or the legacy tree and count directory
entries: one per map, each a directory. `ls` one such directory and see exactly that map's files.
Nothing about the second story needs to be true for this to deliver its value.

**Acceptance Scenarios**:

1. **Given** the reorganized tree, **When** the GM lists `pool/hamlets/`, **Then** they see five
   directories (`inashiro/`, `kashikawa/`, `kuwabata/`, `mizuguchi/`, `sawada/`) and no loose files.
2. **Given** the reorganized tree, **When** the GM lists `pool/hamlets/inashiro/`, **Then** they see
   `inashiro.gen.py`, `inashiro.json`, `inashiro.notes.md`, and (once rendered) `inashiro.svg`,
   `inashiro.png`, `inashiro.html` - and nothing belonging to another map.
3. **Given** the reorganized tree, **When** the GM lists `pool/magistracies/`, **Then** they see one
   directory per Mode A compound plan, each holding that plan's `.gen.py`, `.notes.md`, `.svg` and
   `.png`.

---

### User Story 2 - The frozen hand-authored maps leave the live pool (Priority: P1)

The maps whose authoring method is deprecated no longer sit beside the maps that are actively
generated. `pool/` holds only what is live - the scripted settlements and the Mode A compound plans
that are hand-authored *by design* - and the 18 frozen exhibits move to a sibling
`legacy-hand-authored-pool/` tree that names what they are.

**Why this priority**: This is the request's second paragraph, and it is the half that carries
meaning rather than tidiness: the freeze (GM 2026-08-16) already made these maps museum pieces that
are never regenerated and never re-gated, but nothing in the directory layout said so. A session or
a GM looking at `pool/hamlets/` today cannot tell `akagahara` (frozen exhibit) from `inashiro`
(live, rolled every gate) without opening a file.

**Independent Test**: List `pool/` and `legacy-hand-authored-pool/` and check the membership against
`poolmaps.classify()`: everything under `pool/` classifies `scripted` or `compound`, everything
under `legacy-hand-authored-pool/` classifies `legacy`, and neither set is empty.

**Acceptance Scenarios**:

1. **Given** the reorganized tree, **When** a session lists the live pool's settlement tiers,
   **Then** `pool/villages/`, `pool/towns/` and `pool/provincial-cities/` no longer exist (every
   map they held was frozen) and `pool/hamlets/` holds only the five scripted maps.
2. **Given** the reorganized tree, **When** the GM opens `legacy-hand-authored-pool/`, **Then** they
   find `hamlets/`, `villages/`, `towns/` and `provincial-cities/`, each holding one folder per
   frozen map.
3. **Given** a frozen map's folder, **When** anything inspects its committed `.svg` and `.png`,
   **Then** the bytes are identical to what was committed before the move, and git records the
   change as a rename rather than a delete plus an add.

---

### User Story 3 - Every tool and document follows the tree (Priority: P1)

Nothing in the repository still assumes the old two-level shape. The pool index covers both trees,
the gate rolls and gates the same five scripted maps it did before, the diagnostic tools take the
new paths, and no document tells a reader to open a path that no longer exists.

**Why this priority**: Same priority as the moves themselves because a move that leaves the tooling
behind is not a delivered change - it is a broken repository. The GM named this explicitly ("along
with anything in the codebase which references or relies on the old directory structure").

**Independent Test**: `make done` is green, and a repository-wide search for the old two-level pool
paths returns only deliberate historical references (a `.notes.md` recording what a path used to be,
a spec describing the old layout).

**Acceptance Scenarios**:

1. **Given** the reorganized tree, **When** `make done` runs, **Then** it is green - including the
   `tests/test_villages.py` sweep, which discovers and gates exactly the same five scripted maps.
2. **Given** the reorganized tree, **When** the pool index is rebuilt, **Then** it lists every map
   in both trees with a working thumbnail, notes link and (where present) interactive link.
3. **Given** the reorganized tree, **When** a session runs any documented `make` recipe with its
   default argument (`make map`, `make gate-manifest`, `make sun-audit`, `make family-census`,
   `make notes-census`), **Then** the recipe resolves a path that exists.

---

### Edge Cases

- **A map with no renders yet.** A scripted map's `.svg`/`.png`/`.html` are gitignored and absent in
  a fresh clone. The per-map folder must still exist (its `.gen.py`, `.json` and `.notes.md` are
  tracked), and the index must keep saying "render not synced" rather than omitting the row.
- **A tier folder that empties completely.** `villages/`, `towns/` and `provincial-cities/` hold
  only frozen maps, so the live pool loses those folders entirely. The index must not show an empty
  section, and the tooling must not assume a fixed set of live tiers.
- **A tier that exists in both trees.** `hamlets/` exists live *and* legacy. Any code keyed on a
  tier name alone would now be ambiguous; the classification must stay keyed on the map, not the
  tier.
- **The one-map-per-invocation scope lock.** `regen.py` refuses more than one gen under the scope
  lock, catching the whole-pool glob. That glob gains a level; the refusal must still fire.
- **`pool/regressions/`.** 107 negative-fixture `.json` plus one `.notes.md` and one `.svg`. These
  are not settlements and have no per-map bundle; they stay flat, and the index keeps skipping them.
- **A name that is a map in one tree and a fixture elsewhere.** `ubame` is both a frozen TOWN and a
  live MAGISTRACY (`ubame-magistracy`). The two must land in different trees without collision.

## Requirements *(mandatory)*

### Functional Requirements

**The layout**

- **FR-001**: Every map in the pool MUST live in its own directory, named for the map's stem, inside
  its tier directory. No map file may sit loose in a tier directory.
- **FR-002**: The files inside a map's directory MUST keep the map's stem as their basename -
  `inashiro/inashiro.gen.py`, not `inashiro/gen.py`. (GM decision, asked and answered 2026-08-30.)
- **FR-003**: A map's directory MUST hold every artifact belonging to that map and nothing else:
  the generator, the manifest, the notes, and the SVG/PNG/HTML renders where they exist.
- **FR-004**: Maps that `poolmaps.classify()` calls `legacy` MUST move out of `pool/` into a sibling
  `legacy-hand-authored-pool/` directory, keeping their tier directory and gaining a per-map
  directory inside it.
- **FR-005**: Maps that classify `scripted` or `compound` MUST stay under `pool/`, gaining a per-map
  directory.
- **FR-006**: `pool/regressions/` MUST keep its present flat shape. Its contents are negative
  fixtures, not maps, and have no per-map bundle to fold.
- **FR-007**: The move MUST be a pure relocation. Every relocated file's bytes MUST be unchanged,
  except a `.gen.py` whose own path arithmetic must deepen (FR-010) and a document whose text names
  a path (FR-016). No map may be re-rolled, and no manifest or render may be rewritten, as part of
  this feature.
- **FR-008**: The 18 frozen maps' committed `.svg` and `.png` exhibits MUST remain in git across the
  move, recorded as renames.
- **FR-009**: The freeze itself MUST be unchanged: legacy gens are still never re-run, `regen.py`
  still prints `FROZEN` for them, and `--frozen-ok` is still the only override.

**The code**

- **FR-010**: Every `.gen.py` MUST resolve the skill root and its own output base correctly from its
  new depth. A generator run from its new location MUST write its artifacts beside itself.
- **FR-011**: `poolmaps.classify()` MUST return the same answer for every map it does today when
  handed the map's new, one-level-deeper path.
- **FR-012**: Every consumer that discovers maps by walking the pool MUST find exactly the maps it
  found before - no more (a fixture mistaken for a map) and no fewer (a map hidden by the extra
  level). This covers the render cache's regeneration sweep, the gate's map sweep, the cache audit,
  the timings census, the notes census, the check census and the map-check tool.
- **FR-013**: Consumers that walk maps MUST cover BOTH trees where their job concerns both, and the
  live tree ONLY where their job is the live pool. Specifically: the render cache, the pool index
  and the notes census concern both trees; the gate's regeneration sweep and the cache audit concern
  the live pool only, because a frozen map is never regenerated.
- **FR-014**: `regen.py`'s one-map-per-invocation scope-lock refusal MUST still fire on a
  whole-pool glob at the new depth.
- **FR-015**: The repository's ignore rules MUST keep ignoring derived renders for live maps, keep
  tracking the frozen exhibits' renders, and keep tracking every Mode A `.svg` as source. The rules
  SHOULD be expressed so that adding a map or a tier does not require adding ignore lines - the
  present per-tier, per-file form is what made 36 hand-written un-ignore lines necessary.

**The index**

- **FR-016**: `pool/index.html` MUST remain ONE page covering BOTH trees: the live pool's sections
  first, then the frozen legacy sections. (GM decision, asked and answered 2026-08-30.)
- **FR-017**: The index MUST make plain which tree a section belongs to, so the GM can tell a live
  map from a frozen exhibit without reading the Method column.
- **FR-018**: Every link and image the index emits MUST resolve from a plain `file://` open of the
  page in whatever tree it sits in, including links that cross out of `pool/` into
  `legacy-hand-authored-pool/`.
- **FR-019**: The index MUST keep the properties it has today: derived (no timestamps, byte-identical
  on an unchanged pool), columns derived from the manifests rather than curated, an unknown map
  folder still getting a section rather than vanishing, and a settlement-tier map with no manifest
  reported in red rather than guessed at.

**The documentation**

- **FR-020**: Every path in the repository's prose that names a pool file or folder MUST name a path
  that exists after the move, or be explicitly marked as historical.
- **FR-021**: `migration-plan.md` MUST record the new layout, since it is the standing plan a session
  reads before touching the pool and it describes the freeze that this split makes visible.
- **FR-022**: The reasoning behind the split MUST be recorded where a future session will meet it -
  what the two trees mean, what decides which tree a map goes in, and what a session must do when a
  map is converted from hand-authored to scripted (it moves trees).

### Key Entities

- **Live pool (`pool/`)**: the maps that are regenerated and gated. Two kinds: `scripted` Mode B
  settlements produced by a generator, and `compound` Mode A plans that are hand-authored by design
  because they are small enough that scripting buys nothing.
- **Legacy pool (`legacy-hand-authored-pool/`)**: the 18 frozen hand-authored Mode B maps. Permanent
  exhibits: never regenerated, never re-gated, renders committed write-once. A map leaves this tree
  only by being converted to scripted generation, at which point it moves to `pool/`.
- **Map bundle**: one settlement's or plan's files, sharing a stem - `.gen.py` (source), `.json`
  (manifest, Mode B only), `.notes.md` (the record), `.svg`/`.png`/`.html` (renders).
- **Tier**: `hamlets`, `villages`, `towns`, `provincial-cities`, `capitals`, `magistracies`. A tier
  name may now appear in both trees.
- **Regression corpus (`pool/regressions/`)**: negative fixtures proving checks have teeth. Not maps.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Listing any tier directory in either tree shows one entry per map and zero loose files.
- **SC-002**: The GM can see, from the directory path alone, whether a map is live or a frozen
  exhibit - no file needs opening.
- **SC-003**: Every map that was in the pool before the move is present after it, exactly once:
  23 Mode B settlements and 5 Mode A plans, 5 + 5 live and 18 legacy.
- **SC-004**: Every relocated file's content is byte-identical to before the move, apart from the
  generators' own path arithmetic and documents that name a path. Verified by comparing content
  hashes across the move, not by eye.
- **SC-005**: `make done` is green, at the same scope and with the same test count as before the
  move (modulo tests added by this feature), and the map sweep gates the same five scripted maps.
- **SC-006**: The rebuilt index shows all 28 maps, with every thumbnail, notes link and interactive
  link resolving from a `file://` open.
- **SC-007**: A repository-wide search for the old two-level pool paths returns only deliberately
  historical references.
- **SC-008**: Adding a new map to either tree requires no new ignore rule.

## Decisions Recorded

This feature draws nothing and states nothing on any map. No glyph, size, placement rule, distance
or density changes; no manifest is rewritten; every render is byte-identical to the one committed
before the move (FR-007). The table is therefore empty by construction rather than by omission - the
section is kept, rather than deleted, so the spec review can see that the question was asked and
answered rather than skipped.

Every task in this feature is `research: rendering`: the work is a directory restructuring and its
tooling, and no question about how a place was built, farmed, planted or lived in arises anywhere in
it.

## Assumptions

- **The classification is settled and is not this feature's to revisit.** `poolmaps.classify()` is
  the single source of truth for which tree a map belongs in, and its `LEGACY_FROZEN_GENS` and
  `COMPOUND_GENS` are closed lists. This feature moves files according to that answer; it does not
  reclassify any map.
- **The GM's phrase "no plans to become hand-authored" means "no plans to become SCRIPTED".** The
  sentence's own example (magistracies) and its stated reason (small enough that a scripted process
  buys nothing) make the intent unambiguous, and `migration-plan.md` section 1 already rules Mode A
  out of the migration's scope. Mode A plans stay in `pool/`.
- **`legacy-hand-authored-pool/` is a sibling of `pool/`**, inside the skill directory - the plain
  reading of "out of the `pool/` directory and into a `legacy-hand-authored-pool/` directory".
- **`wip/` is out of scope.** The capital-tier draft (`shiro-daika`) and the cohort HTML already sit
  outside `pool/`, and the capital tier is unfinished. Nothing about it changes here.
- **The renders' bytes are what matters, not their mtimes.** Moving a file does not change its
  content; some tooling keys on mtime (the index's staleness check) and may legitimately rebuild
  once after the move.
- **The environment defect found during recon is fixed under this feature.** The two Python
  lockfiles pinned conflicting numpy versions (`requirements.txt` 2.5.1 via shapely,
  `requirements-dev.txt` 2.5.2 via types-shapely), and `setup-dev-env.sh` installs both in one pip
  command - so a fresh container could not be provisioned at all. Fixed where found, per Principle
  XIV, with the dev lockfile constrained to the runtime lock so the drift cannot recur.
