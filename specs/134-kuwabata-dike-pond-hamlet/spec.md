# Feature Specification: Kuwabata, the Dike-Pond Hamlet, Scripted and Audited

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=134-kuwabata-dike-pond-hamlet`)

**Created**: 2026-08-27

**Status**: Draft - awaiting the `spec-fidelity` review (constitution XVI)

**Input**: [`gm-request.md`](gm-request.md), verbatim and unedited. That file is the authority for
this specification.

## The feature, in one sentence

Kuwabata - the mulberry-dike fish-pond hamlet, today a hand-authored script - becomes a map the
scripted hamlet generator produces from a short declaration, carrying every feature the accepted
reference hamlet (Inashiro, feature 133) carries; the finished map is then audited against the
historical record for features a dike-pond hamlet would have that a paddy hamlet would not, and
that gap list is PRESENTED to the GM - nothing new is drawn until the GM chooses - and the feature
closes only on the GM's acceptance.

## Why this exists (the GM's words)

- *"Now that we have gotten our reference hamlet of Inashiro to the point where I am happy with it
  and have formally accepted it as being a solid baseline. I would like to move on to generating
  other types of hamlets in a scripted manner. the next type of hamlet that I would like to make
  sure we are able to script in this way is Kuwabata."*
- *"when I look at Kuwabata I do not See many of the features which we have incorporated into our
  reference hamlet. For example, I do not see bamboo groves, and the sheds look like the old style
  sheds rather than the new style sheds."*
- *"I could imagine there being map features which would exist in Kuwabata but not in Inashiro,
  which is why I believe that this would be a useful exercise as one of the first things that we
  do."*
- *"I don't think that you should move forward with adding new map features without talking to me
  first."*
- *"part of the SpendKit feature is going to be my own acceptance."*

## What is true today (established before this spec was written)

- Kuwabata IS a pool map with a generator script (`pool/hamlets/kuwabata.gen.py`), but that script
  is HAND-AUTHORED: it pins coordinates and calls the drawing engine directly. It is not produced by
  the scripted hamlet generator (`hamletgen`) the way Inashiro is, so it received none of the
  reference-hamlet work: no bamboo stands, no farmstead fixtures (privy, woodpile, manure heap, bath
  shed, coop, household shrine, persimmon), the old shed forms, no lane web, no toe band. The GM's
  guess was right.
- The migration plan lists the `mulberry_dike_fishpond` archetype as NOT STARTED, depending on the
  `polder_grid` archetype (FITTED, not promoted: 29/32 in its last sweep, one known blocker) and on
  the land-use overlay step, which the engine already implements (`apply_land_use`) but the
  generator does not yet drive.
- The hand-authored Kuwabata records several archetype-specific compositions the generator has no
  equivalent for: the wholesale conversion of the polder to ponds (`eligible="all"`, ~90%), the
  mosaic pond layout, the waterward reed fringe declared on the wet flanks, the windward gap that
  lets an L-shaped windbreak fit against an east-dike village, and footbridge caps that put the
  crossings on the settlement side of the ring canal.
- The scope switch is LOCKED to the reference settlement (thrown 2026-08-27 by the feature 133
  session for an unrelated cohort hang). Under the lock a SINGLE named map may still be rolled
  (`make map GEN=...`), which is all this feature needs to iterate on Kuwabata; the multi-map
  sweeps stay deferred to whichever session unlocks.

## The shape of the feature

Three phases, in the order the GM gave them, and a hard stop between the second and the third:

1. **Research first** (constitution XII): before the generator learns the archetype, the record on
   how a dike-pond hamlet was actually composed is read - where the houses stood relative to the
   dikes and the ponds, how the ponds were fed and drained, what the household economy put on the
   ground. Much of this is already in `research/archetypes.md` from features 005/010; the pass
   confirms what is there, fills what is missing, and cites what it reads.
2. **The conversion**: the generator produces Kuwabata from a declaration of the same shape as
   Inashiro's; the map passes the gate; every reference-hamlet feature appears on it where the
   archetype allows it.
3. **The audit**: the finished map is compared against the record for the features a dike-pond
   hamlet would carry that a paddy hamlet would not. The output is a LIST with prevalence and a
   reading of each item, presented to the GM. **No new category of map feature is added in this
   feature without the GM choosing it** - the GM's words: *"I don't want you adding new categories
   of things to these maps without running them by me first."*

Then the session STOPS and presents. The acceptance task is the GM's alone; the feature stays in
the clone until it is ticked (feature 133's mechanism: a feature in progress lands nothing except
its own number claim). Whatever the GM chooses from the audit list becomes tasks the GM names, in
this feature or a later one - that choice is theirs.

## User Scenarios & Testing

### User Story 1 - Kuwabata from a declaration (Priority: P1)

The GM opens Kuwabata's pool entry and finds a short declaration - a name, a seed, a household
count, the land's fall, the archetype - instead of two hundred lines of pinned geometry. The map it
produces is recognizably Kuwabata: a diked polder converted almost wholly to fish ponds rimmed with
mulberry, a header reservoir at the high corner, a village on the dry dike, and every reference
hamlet feature standing among the houses.

**Why this priority**: it is the thing the GM asked for first and everything else stands on it.

**Independent Test**: regenerate the map from its declaration alone; the gate passes; the map's
manifest declares the dike-pond archetype; a side-by-side with Inashiro's manifest shows every
feature family Inashiro carries (bamboo, fixtures, the new sheds, the lane web, the toe band, the
notice board, the windbreak, wells, byres) present on Kuwabata, or a recorded archetype reason for
each absence.

**Acceptance Scenarios**:

1. **Given** the declaration names the dike-pond archetype, **When** the map is generated, **Then**
   almost every polder cell is a pond with a mulberry-planted bank, water enters at the high corner
   and leaves at the low corner through sluices in the perimeter dike, and the village stands on the
   dry side of the dike.
2. **Given** the generated map, **When** its feature families are compared with Inashiro's, **Then**
   each reference-hamlet family is present, or its absence is recorded against the archetype with
   the research that justifies it (for example: no toe band where there is no sloping field).
3. **Given** the declaration is changed in only its seed, **When** the map is regenerated, **Then**
   a different but equally valid dike-pond hamlet results - the conversion is a generator, not a
   re-encoding of one drawing.
4. **Given** the generated map, **When** the gate runs on it, **Then** it passes with no waiver
   that the hand-authored map did not already carry, and every regression fixture that protected
   the hand-authored Kuwabata still fires.

---

### User Story 2 - Nothing the reference hamlet taught is lost (Priority: P1)

The GM looks at the new Kuwabata expecting the sheds, the bamboo, the privies and woodpiles they
saw accepted on Inashiro, and finds them - drawn by the same rules, at the same sizes, with the
same per-hamlet share bands, because the same stages drew them.

**Why this priority**: the GM named this as the motivating gap (*"I do not see bamboo groves, and
the sheds look like the old style sheds"*).

**Independent Test**: the feature-family census above; and Inashiro's own manifest is byte-identical
before and after this feature - the reference hamlet does not move.

**Acceptance Scenarios**:

1. **Given** the reference hamlet accepted under feature 133, **When** this feature's changes are
   in, **Then** Inashiro regenerates to exactly the accepted manifest.
2. **Given** a reference-hamlet feature that cannot honestly stand on a dike-pond hamlet, **When**
   the generator omits it, **Then** the omission is recorded (the research, the rule, the pointer)
   and visible in the spec's Decisions Recorded table.

---

### User Story 3 - The audit: what a dike-pond hamlet still lacks (Priority: P1)

The GM receives a list, with the prevalence the record gives for each item and a reading of each,
of features that would stand on a dike-pond hamlet but not on a paddy one - the silk side of the
household economy, the fish side, the water side - and chooses which, if any, to add. The session
adds none of them on its own.

**Why this priority**: the GM asked for it explicitly and set the stopping rule around it.

**Independent Test**: the list exists in this feature's directory, every item carries a source read
through the source-reader, and the map contains no feature category that was not on Inashiro or the
hand-authored Kuwabata at the start of the feature.

**Acceptance Scenarios**:

1. **Given** the research pass, **When** it finds a feature the record attests on a noticeable share
   of dike-pond households or hamlets, **Then** the item is listed with its prevalence, its source,
   and whether it is drawable at true scale.
2. **Given** the list, **When** the session finishes the phase, **Then** it presents the list to the
   GM and stops; no item is implemented.
3. **Given** a candidate the record does NOT support, **Then** it appears in a "not owed" list with
   the reason, so the question is not reopened.

---

### User Story 4 - The GM accepts (Priority: P1)

The GM looks at the generated Kuwabata and the audit, and either names further tasks or accepts.
The feature closes only on the GM's word, recorded verbatim.

**Independent Test**: the acceptance task is unticked until the GM's words are recorded in it; the
push refuses to land the feature's engine work while it is open.

---

### Edge Cases

- The polder archetype the dike-pond one stands on has one known blocker (the title landing on the
  windbreak belt when framing is tight). If Kuwabata's seed hits it, the blocker is fixed in this
  feature (constitution XIV), not worked around by choosing another seed.
- The scope lock refuses multi-map sweeps. Any cohort evidence the conversion would normally owe
  (the polder archetype's promotion bar is a green cohort) is recorded as OWED at unlock, with the
  command, not run around the lock.
- Kuwabata's household count (16) is inside the hamlet band; if the fitted polder cannot reach the
  acreage the count demands at the calibrated cell size, the fit reports it rather than stretching
  the cell.
- Where the record supports two forms for a dike-pond composition (a uniform chessboard versus a
  mosaic; willow versus mulberry on the water face), the generator rolls between them per seed
  (constitution XII, the knob rule), and Kuwabata's declaration pins the form the hand-authored map
  showed the GM.

## Requirements

### Functional Requirements

- **FR-001**: The scripted hamlet generator MUST produce a dike-pond hamlet from a declaration whose
  required fields are only facts a person knows (name, seed, households, the land's fall, the
  archetype), with every position derived.
- **FR-002**: The generated Kuwabata MUST carry every feature family the accepted reference hamlet
  carries, or record per family the archetype reason it is absent.
- **FR-003**: Kuwabata's pool entry MUST be replaced by the declaration; the hand-authored script is
  retired from the pool (kept in history), and the migration plan's status table is updated.
- **FR-004**: The reference hamlet's accepted output MUST be unchanged by this feature.
- **FR-005**: The generated map MUST pass the gate, and every existing regression fixture named for
  Kuwabata MUST still fire.
- **FR-006**: A research pass MUST precede the generator work and the audit, cite what it reads,
  and route every claim through the source-reader (constitution XII, v2.11.0).
- **FR-007**: The audit MUST deliver a list of candidate features with prevalence, source and a
  drawability reading, plus a not-owed list with reasons, and the session MUST stop and present it
  without implementing any item.
- **FR-008**: No new CATEGORY of map feature MAY be added in this feature unless the GM chooses it
  in their own words, recorded in the task that adds it.
- **FR-009**: The feature MUST close only on the GM's acceptance, recorded verbatim in its final
  task; that task is never ticked by a session.
- **FR-010**: Every task is classified `research: rendering | physical | procedure`; physical tasks
  carry the three research boxes (constitution v2.12.0).
- **FR-011**: Any sweep the scope lock refuses is recorded as owed at unlock, never run around the
  lock.

### Key Entities

- **The declaration**: name, seed, households, fall, archetype, plus pinnable knobs - what a pool
  entry states.
- **The dike-pond archetype**: a polder converted (almost) wholly to ponds with mulberry banks; the
  rare end state, distinct from the scattered overlay a paddy polder may carry.
- **The feature-family census**: the per-family comparison between Inashiro and Kuwabata that
  User Story 2 tests.
- **The audit list**: candidate features with prevalence, source, drawability, and the not-owed
  list.

## Success Criteria

- **SC-001**: Kuwabata's pool entry is under 30 lines of declaration and regenerates a gate-passing
  map from it alone.
- **SC-002**: 100% of Inashiro's feature families are present on Kuwabata or recorded as
  archetype-absent with a research pointer; zero unexplained absences.
- **SC-003**: Inashiro's manifest is identical before and after.
- **SC-004**: The audit list is delivered with a source per item, and the GM is presented with it
  before any of its items exists on a map.
- **SC-005**: The feature lands on main only after the acceptance task carries the GM's words.

## Decisions Recorded (constitution XII - the reader who will click on it)

Filled as the work lands; each row is a rendering decision this feature makes, with its class.

| Decision | Class (accurate / deviation / guess) | Why | Recorded at |
|---|---|---|---|
| (to be filled during implementation) | | | |

## Assumptions

- "Scripted" means produced by the `hamletgen` generator from a declaration, as Inashiro is - not
  merely "has a `.gen.py`", which Kuwabata already does.
- The archetype builds on the existing polder stage; the polder archetype's own promotion into the
  rolled set is NOT required by this feature (that bar is a cohort the lock defers), only that
  Kuwabata's seed generates and passes.
- "Every feature we built into our reference hamlet" means the feature families Inashiro's accepted
  manifest records, judged per family against the archetype - the GM's examples were bamboo and the
  shed forms.
- The audit's "noticeable percentage" threshold follows feature 133 T52's reading: an item is listed
  when the record gives it a prevalence worth a GM decision, and anything the record supports only
  weakly is listed as not-owed with the reason rather than silently dropped.
- The GM's acceptance may come with further named tasks first; those are appended to this feature's
  task list the way feature 133 did it, each timed.

## Review history (constitution XVI)

- (pending) round 1 `spec-fidelity`.
