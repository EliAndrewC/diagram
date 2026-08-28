# Feature Specification: Kuwabata, the Dike-Pond Hamlet, Scripted and Audited

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=139-kuwabata-dike-pond-hamlet`)

**Created**: 2026-08-27

**Status**: APPROVED by `spec-fidelity` - round 2 verdict **FAITHFUL** (2026-08-27), after round 1 returned three changes. Implementation may begin.

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
   in the spec's Decisions Recorded table AND carried into the findings presented to the GM
   (FR-007), who rules on it at acceptance.

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
- Where the record supports two forms for a dike-pond composition, the two cases are judged
  separately. A form composed only of things already on these maps (a uniform chessboard versus a
  mosaic of the same ponds) is a knob rolled per seed (constitution XII), with Kuwabata's
  declaration pinning the form the hand-authored map showed the GM. A form whose alternative
  introduces a thing NOT already drawn on Inashiro or the hand-authored Kuwabata (willow on the
  water face, for one) is NOT implemented in this feature: it goes on the audit list for the GM to
  choose, because the GM said *"at least not in this specific case"*.

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
  drawability reading, plus a not-owed list with reasons, AND every reference-hamlet feature family
  omitted from Kuwabata under FR-002, each with its archetype reason and research pointer - so the
  GM decides at acceptance whether each omission is right; the session MUST stop and present the
  whole of it without implementing any item.
- **FR-008**: No map feature that does not already stand on the hand-authored Kuwabata or on
  Inashiro's accepted manifest MAY be added in this feature - in the conversion phase any more than
  in the audit phase - unless the GM chooses it in their own words, recorded in the task that adds
  it. The GM gave this twice: *"I don't think that you should move forward with adding new map
  features without talking to me first"* and *"I don't want you adding new categories of things
  to these maps without running them by me first, at least not in this specific case."*
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
| The dike-pond is BUILT as the polder carried to the wholesale `mulberry_fishpond` overlay (`eligible="all"`) | accurate | the wall-to-wall landscape is the rare end state of the scattered overlay, ~300 years of 挖塘培基 plot by plot; Shunde 4.6% (1581) to rice under a tenth (c. 1900) | `research/archetypes.md` "The three overlay values"; `hamletgen/consts.py` `POLDER_ARCHETYPES`; `water.py` `stage_polder` |
| Pond module 160 ft, merge-heavy parcels (mostly 160x320 ft ~0.48 ha), 22 ft mulberry dikes | accurate, with the record's CAVEAT | traditional ponds 0.4-0.6 ha oblongs, dikes 6-10 m (Ruddle & Zhong / FAO); the sizes are 20th-century surveys of the traditional landscape, not Ming/Qing documents | `waterfields/polder.py` TRUE-SCALE SIZING; `consts.py` `POLDER_FABRIC`; T11 sources |
| `pond_layout` grid \| mosaic rolled per seed; Kuwabata pinned to mosaic | accurate (two attested forms -> a knob) | the wei-tian was a surveyed grid, the Pearl-delta dike-pond an accreted mosaic; both carried dike-ponds | `research/archetypes.md` "Grid vs mosaic"; `consts.py` `POND_LAYOUTS` |
| 90% of the block converted; leftovers repainted as standing rice | calibrated liberty (a DEGREE along the attested continuum) | the end state is "(almost) every cell"; the exact share is not a measured number | `consts.py` `DIKEPOND_CONVERSION` |
| The village at the block's HEAD (north), derived by `seat_cluster` (back to the NW wind, upslope) | guess between attested options | the record attests the village on whichever dry ground the margin polder abuts (shore-side) or on the dike / interior in deep water; it does not say which flank of a head-fed block; the hand-authored map's east flank was a hand decision | `research/archetypes.md` "Polder siting"; `kuwabata.notes.md`; the T30 audit revisits it |
| Waterward reed fringe on the cross flanks the village does not occupy and on the foot; never the head | accurate (siting) / the strip geometry is a drawing convention | outside the dike is the fluctuating water it was reclaimed from except on the landward shore; the reservoir already stands at the head | `research/archetypes.md` "Polder siting"; `water.py` `waterward_flanks`, `stage_waterward` |
| Ring-canal planks cluster on the settlement-side toe (3), one per lateral, none on the feeder/drain; both toes 2 when the village is at the head | accurate (research 2026-07-22) for the toe case; the head case is a reasoned extension | people cross where they live and walk the bunds; an uncrossed toe is a long ditch with no plank | `settlements.md` "Polder ring canal"; `water.py` `polder_crossing_caps` |
| The seams rule stands aside on a dike-pond field | accurate | two ponds a dike apart ARE the 桑基魚塘 fabric; the strip between the rings is the planted dike | `check_village/segments_08d` `paddy_plot_seams_shared` |
| The windbreak keeps off the pond (tameike or header reservoir) | rendering rule (a defect fix) | 15 clumps stood in open water on the first roll | `settlement/homestead_parts.py` `village_grove` |
| Absent by archetype: `dry_plots` (a comb's dry hem), `field_ditches:branch` (comb deliveries), `field_ponds` (no obstacle tiles - open water is the fabric) | accurate | a polder is a solid diked block with laterals; research D4 forbids in-field features on the dike-pond | `research/fields.md`; `settlement/fields/features.py` `_paddy_features`; `make family-census` |
| Ring-canal planks: head-seated village -> the feeder carries 3, each toe 1; foot-seated -> the drain 3 | accurate (the researched rule applied to the collector the village abuts) | the first cut satisfied the check with every plank 350-1,100 ft from the houses | `water.py` `polder_crossing_caps`; docs/review-ledger.md 2026-08-28 |
| The title placard clears wells and the notice board; the board caption is probed at its tilt | rendering rules (defect fixes from the review) | a placard on a well hides a traffic-sited fixture; a tilted caption reaches ground its level box does not | `settlement/finish.py` `_title_obstacles`; `structures/fixtures.py` `kosatsuba` |
| The dike-pond ink's classes for the interactive map: fish pond, mulberry dike, pond sluice, perimeter dike | each labeled in its entry (accurate, with the sizes' 20th-century caveat) | main's `all_ink_is_ruled_on` met its first dike-pond | `interactive/classes.py`; `specs/134-interactive-html-map/spec.md` FR-007 table |
| No threshing floor on the dike-pond archetype; the forecourt stays recorded as `kind: forecourt` | accurate (the GM's ruling on a read fact: rice is what a threshing floor is for) | dropping the reservation re-packed the web and the belt (measured), so the ground stays reserved and only the ink goes | `settlement/rolling/bundle.py`, `homestead_parts.py` `_attach_yard`; `segments_04b` `harvest_yards_present` |
| `manure_form` heap \| pit, rolled | accurate (two attested forms) | Sugiura 1973 heaps; Fei 1939 half-buried earthenware pits | `consts.py` `MANURE_FORMS`; `farm_fixtures.py` |
| Fry ponds: the smallest 10% of parcels (1-3), a record and class | guess (the trade is read, the share is not) | Miles 2003; the Sangyuanwei proverb | `landuse.py` `apply_land_use`; class `fry pond` |
| A sluice gate at every perimeter-dike cut, snapped to the recorded water | accurate (form) / the seat is the cut | FAO x6708e; the polder's 窦 | `land/dikes.py` `dike_gates`; `frame.py` `stage_crossings` |
| Pig sties on the dikes (25-50% of households) and duck pens (10-30%) on the nearest ponds | guess (practice read, premodern share not) | FAO ac264e; Ruddle & Zhong via isis | `hamletgen/pondstock.py`; `farm_fixtures.py` `PondStockMixin` |
| `dike_crop` mulberry (x3) \| sugarcane \| banana \| fruit, one type per hamlet; Kuwabata pinned mulberry | accurate (the types) / the weighting is a degree | the gazetteer office's succession of types; the 1980s survey's cane 18% vs mulberry 12% | `consts.py` `DIKE_CROPS`; `landuse.py` `_mulberry_rows` |
| `leftover` rice \| vegetables \| pond, rolled | accurate (the three states) / the even roll is a degree | Fei's vegetables under the mulberry; the gazetteers' no-rice district | `consts.py` `LEFTOVER_FORMS`; `landuse.py` `_landuse_repaint_leftovers` |
| A creek, boats and a landing NOT drawn | the GM's ruling (2026-08-28) | a dike-pond hamlet need not sit on navigable water; the lane is the link | `kuwabata.gen.py`, `kuwabata.notes.md`, audit A1 |
| Acreage per household is the paddy figure (`GROSS_ACRES_PER_HOUSEHOLD` 1.3 ac) | guess - carried over unexamined | whether a silk-and-fish household held the same ground is a T30 audit question | `hamletgen/consts.py`; `kuwabata.notes.md` "Known open" |
| A reed marsh is HARD ground: no farmhouse, garden or yard footprint on it; the cluster seat scores wet ground like the dry-plot foul and refuses a seat centered in it (T50) | accurate | reed fringe is wet ground, not building ground - the seat rules already excluded the toe and the tameike's low ground; the fringe polygon simply had never been registered where a placer reads; GM 2026-08-28: "update our placement algorithms to make that impossible" | `settlement/land/wet.py` `marsh`, `settlement/houses.py` `_hard_ground`, `hamletgen/cluster.py` `seat_cluster` wet_foul, `pool/hamlets/kuwabata.notes.md` |
| The polder's inlet stub reaches the reservoir's rim (2 ft inside it) and the hairline record inserts the ring head at its place along the source -> mouth chord (T51) | deviation (legibility of a real junction) | the stub ended a fixed 52 ft past the ring corner while the reservoir walked uphill to clear the crop - a 30 ft dry gap no real feeder has; the hairline's mouth is pulled clear of the envelope's corner in up to three rounds | `hamletgen/water.py` `stage_polder`, `settlement/fields/comb.py` `_comb_source_channel` |
| Every toe collector of the ring canal ends ON the nearer trunk after the corner rounding (T52) | accurate | the ring is a closed loop; the rounding swept each corner inside the lattice node the toes were laid to (a 9 ft gap at the NW corner) | `waterfields/polder.py` `_onto_poly`, `build_polder` |
| Village lanes draw through the ground block (shoulders below every tread); every watercourse composites in ONE water block (rims, then beds with the pond's fill last, then sheens) - on every map (T53) | deviation (rendering convention) | the GM: junctions must read as "one contiguous structure" and "water just flows"; the pond's rim "should not be present at the place of their intersection" | `settlement/water_ways.py` `_lane_ink_at`, `settlement/finish.py` (the water block), `settlements/water.md`, `dev/placement.md` |
| The title pocket is reserved ONCE, shrinks to 210 x 120 before giving up, and on a sheet with no blank box is reserved OUTSIDE the content (the crop takes it in; `crop_hugs_content` counts the placard) | deviation (sheet furniture) | fallout of T50's re-seated cluster: nothing on the sheet was blank enough and the placard fell back onto the windbreak; the frame's margin is capped, so the reservation is content | `hamletgen/hinterland.py` `title_pocket`, `hamletgen/frame.py` `stage_frame`, `settlement/core.py` `crop_to_content(extra=)`, `check_village/segments_01a` |
| A final-pass junction that would hairpin at a door spur joins from the vertex before the spur; every other junction is laid exactly as before | deviation (rendering) | nothing smooths a post-smoothing link; only a join today's gate already fails is changed, so Inashiro and the tripwire seeds are untouched (five wider toucher levers were priced and declined - kuwabata.notes.md) | `hamletgen/ways.py` `_touch_junctions` `final`, `_zigzags` |

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

- Round 1 (2026-08-27): three changes. (1) FR-008 bound only a new "category"; the GM's broader
  sentence had no FR - FR-008 now bars any feature not already on Inashiro or the hand-authored
  Kuwabata, in the conversion phase too. (2) The knob edge case bundled pond layout (things already
  drawn) with willow-vs-mulberry (a plant not on the maps) - split; the second goes to the audit
  list. (3) FR-007's list ran one way only; it now carries every reference-hamlet family omitted
  under FR-002, so the GM sees the omissions the way they saw the missing bamboo.
- Round 2 (2026-08-27): **FAITHFUL**. Two asides recorded: US1 AS3's seed-variation roll is one named map per invocation under the lock (owed at unlock if it cannot be rolled that way); SC-001's 30 lines is the spec's number, not the GM's.
