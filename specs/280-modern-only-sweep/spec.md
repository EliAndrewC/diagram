# Feature Specification: The modern-only sweep

**Feature Branch**: `280-modern-only-sweep` (no branch - `main`, per CLAUDE.md)

**Created**: 2026-09-28

**Status**: FAITHFUL at round 2; phase 1 (audit and research queue) and phase 2 (elimination, 2026-09-29) done

**Input**: the GM's request, verbatim in [`request.md`](request.md): *"We should eliminate anything which is only
modern"*, and *"I do also want a sweep of what we have to find anything else that is modern only"*, run *"as its own
feature separately and in parallel"*.

## What is owed

The maps show a premodern setting. Anything a map draws, any form a knob rolls, and any research claim a map rests on
that is attested ONLY in modern sources is to be found and eliminated. Feature 269 already handles the cases the GM
named (the duck pen; the cane, banana and vegetable dikes; the tea dike added; the general rule written into
`docs/research-doctrine.md`). This feature is the sweep for everything else.

The work runs in phases. **Phase 1** (this session): the audit, the inventory of candidates, the research queue and the
plan. **Phase 2**: the research sessions, one per group, each candidate searched for a premodern attestation FIRST.
**Phase 3**: the eliminations in the engine, the kinds and the maps, after the research, and for any module feature 269
holds, after 269 lands.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Nothing on a map is only modern (Priority: P1)

The GM opens a hamlet, a town or a magistracy and clicks each feature. None of them is a thing attested only in the
modern period. A feature whose only attestation is modern has gone from the maps, and from the forms a knob can roll.

**Independent Test**: every inventory candidate has an outcome line in `outcomes.md`; every MODERN-ONLY outcome has a
matching elimination (the kind retired, the knob option removed, the generator no longer drawing it, the motivating
map regenerated), or, only where the GM ruled it in knowing it was modern-only, a GM ruling after `escalation-check`.

**Acceptance Scenarios**:

1. **Given** a candidate the research finds attested before modernity, **When** the feature lands, **Then** it stays,
   and its section cites the premodern attestation.
2. **Given** a candidate the research finds attested only in the modern period, **When** the feature lands, **Then**
   no scripted map draws it, no knob rolls it, and its section records the search that found nothing earlier, dated.
3. **Given** a candidate with some forms attested before modernity and some only after (MIXED), **When** the feature
   lands, **Then** the attested forms stay (a knob among them where there are two or more) and the modern-only forms go.
   A degree along a continuum (a density, a count, a size) is calibrated to the premodern figure, as the GM ruled for
   mulberry spacing on 2026-09-28.

### User Story 2 - Nothing is eliminated on a guess (Priority: P1)

Before any candidate is called modern-only, a research pass searches for a premodern attestation of it, reads what it
finds through `source-reader`, and records the outcome by the record's rules.

**Independent Test**: every MODERN-ONLY outcome names the search (terms, languages, where searched) and its date.

### User Story 3 - The GM hears what reverses a ruling (Priority: P2)

Where the GM ruled a feature in without knowing it was modern (as the duck pen was: *"I didn't know that this was a
modern thing when I asked to have it added, so we should get rid of it"*), it is eliminated like any other, and the GM
is told which ruling the finding reverses. Only where the record shows the GM ruled a form in KNOWING it was
modern-only - two GM rulings in conflict - does it go to the GM through `escalation-check` before it is removed.

## Edge Cases

- **A modern source describing older practice.** The test is when the practice is attested, not when the source was
  written. A modern historian, a museum, an archaeological report or a folklore volume that places a form before
  modernity is a premodern attestation. A modern record that gives no date is not (D1).
- **Frozen legacy maps.** The 18 hand-authored maps under `legacy-hand-authored-pool/` are never regenerated or edited
  (the GM, 2026-08-16), and on 2026-09-28 the GM declined to update hand-drawn maps for a finding (the headman's gate).
  A modern-only form on a legacy map is recorded against that map in `migration-plan.md` as owed at its scripted
  conversion, and the list goes to the GM. It is not dropped.
- **Sections other features hold.** Feature 269's sections (until it lands), 272's, and 279's religion-and-death
  124-129 are not edited here. A finding owed to one is written in the handoff and sent to its owner.
- **Modules feature 269 is editing** (its `briefs/engine/groups.md`): no phase-3 change touches one until 269 lands.
- **A modern-only form with no premodern replacement in the same place** (a fixture that fills a yard): the map shows
  what the premodern record puts there, or nothing. The generator is not left with a gap it cannot place around.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The audit MUST cover every research page (fields, homesteads, water, vegetation, archetypes,
  religion-and-death, settlements, towns, buildings, ways, urban-features, presentation, and every `cities/*` page),
  every interactive kind and knob form, the pool maps' kinds, the legacy maps' kinds, and the magistracy compound kinds.
  It MUST find four kinds of candidate: (a) a section whose only sources are modern (20th century on) for something a
  map draws; (b) a section whose own text calls a drawn form modern, today's, postwar, or Meiji or later; (c) a kind or
  knob form whose `Entry:` section is (a) or (b); (d) a map feature with no record entry where modern practice is the
  likely source.
- **FR-002**: `inventory.md` MUST list one row per candidate: its section, the drawn form, why it looks modern-only,
  and the maps it touches. Candidates already handled by 269, or held by 272 or 279, are listed as excluded with the owner.
- **FR-003**: Every candidate MUST be researched, a search for a premodern attestation first, and end in one of three
  outcomes: MODERN-ONLY (the search that found no premodern attestation, dated), PREMODERN-ATTESTED (cited), or MIXED
  (which forms are attested, cited, and which are not, with the search).
- **FR-004**: The research MUST follow the record's procedure: page sessions from briefs of at most four questions,
  checks on bundles, `make reserve` for prefixes, `make lines` / `make append` for coordination files, and the claims
  in `/diagram/.clones/RESEARCH-CLAIMS.md`.
- **FR-005**: A MODERN-ONLY form MUST be eliminated from every scripted map and every knob: the generator no longer
  draws or rolls it, its kind is retired, and each motivating map is regenerated and reviewed. A MIXED candidate loses
  only its modern-only forms.
- **FR-006**: A MODERN-ONLY form the GM ruled in MUST be eliminated under FR-005 like any other; the finding and the
  ruling it reverses are reported to the GM. The one exception is a form the record shows the GM ruled in KNOWING it
  was modern-only: that conflict of two rulings goes to the GM through `escalation-check` before removal.
- **FR-007**: A modern-only form on a frozen legacy map MUST be recorded in `migration-plan.md` against that map, owed
  at its conversion, and listed for the GM.
- **FR-008**: The record MUST state each outcome in the section that makes the claim: the premodern attestation cited,
  or the modern-only finding with the search and the decision that the maps do not draw it.
- **FR-009**: Each kind whose section changed MUST follow it (`Entry:`, label, prose), checked by `entry-drift`.
- **FR-010**: No section or module another feature holds (Edge Cases) MAY be edited by this feature.

### Key Entities

- **Candidate**: a drawn form, knob form or claim that looks modern-only, with its section and maps (M01...).
- **Group**: a research session's worth of candidates (at most four questions), on one page, with a free prefix range.
- **Outcome**: MODERN-ONLY / PREMODERN-ATTESTED / MIXED, per candidate, in `outcomes.md`.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002): `inventory.md` has a row for every candidate the audit found on every page and kind
  source named in FR-001, and a line per page or source that yielded none.
- **SC-002** (FR-003, FR-008): every candidate has an outcome line in `outcomes.md` naming its section, and each
  MODERN-ONLY line names its search and date.
- **SC-003** (FR-005): no MODERN-ONLY form is drawn by a regenerated pool map or offered by a knob, and each changed
  map has a `settlement-review` or `building-review` row in `docs/review-ledger.md`.
- **SC-004** (FR-006, FR-007): every reversed GM ruling, every knowingly-ruled modern-only form and every legacy-map
  list reaches the GM after an `escalation-check` verdict.
- **SC-005** (FR-009): every changed kind has an `entry-drift` verdict of IN-STEP.
- **SC-007** (FR-004): every write brief assigns at most four questions by `scripts/_brief_load.py`, and every new or
  changed section has quote-check and record-format verdicts (and each new key a source-applicability verdict) in its
  group's checks file.
- **SC-006** (FR-010): `git diff` over the feature touches no held section, and no 269 module before 269 lands.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

- **D1 - where "modern" begins, and the undated record** (guess, the session's; flagged to the GM). A form is attested
  premodern when a readable source places it in Japan before the Meiji Restoration (1868), or in China before the end
  of the Qing (1912), whatever the source's own date. A 20th-century record of remembered custom that gives no date
  (a folklore volume's "in the old days") does NOT place the form before modernity - it could mean the Meiji era - so a
  form attested only so is MODERN-ONLY with the tag `undated-custom`, which lets the set be re-sorted if the GM rules
  such records premodern. This follows the GM's own handling on 2026-09-28: cane was dropped for being on one undated
  modern list only, and the undated root-cut mulberry density was set aside for the dated late-Qing figure.
- **D2 - the frozen legacy maps are not edited** (the GM's standing ruling, 2026-08-16, and 2026-09-28 on the headman's
  gate). Their modern-only forms are owed at conversion (FR-007).
- **Per candidate**: every item's outcome, section and drawn form is a row of `outcomes.md`. One line per elimination
  (phase 2, 2026-09-29), labeled by what the map now draws. Each figure is the research record's finding for the
  section its row in outcomes.md names (the feature keeps no research.md of its own), or a map figure
  observed 2026-09-29 (method: read from the regenerated manifest):
- **M09 - Bund cross-section** (historically accurate): the Bund modal: a few inches high, today's standard a foot; Sources kotobank-azebiki, hattori-site-yayoiken
- **M10 - Water depth** (historically accurate): the Paddy modal: the drained stages are premodern (Qimin yaoshu, Chen Fu), the depths modern
- **M12 - Pond sized by command area** (guess): the m3/ha rule gone from 0017; the scripted tameike is sized from Ikegami by households, noted as held below Chen Fu's measure (a guess)
- **M16 - Work-yard median** (guess): YARD_MEDIAN_TSUBO 18 -> 25 (the IRRI spreading depth retired; undated-custom calibration)
- **M18 - Farm-shed size** (historically accurate): the storehouse annex drawn about 1.67 times as long as deep, inside the Edo sheds' 18-27 ft; the Meiji-Taisho barns not drawn
- **M20 - Outbuildings, the storehouse share and the heap rate** (guess): the storehouse annex on ~1 farm in 8 (KURA_SHARE 0.125, headman always); the heap's 40-70% stays a guess
- **M21 - The firewood stack** (historically accurate): the woodpile is a wood shed only, 35-45% of farmsteads, larger houses first, 24 x 12 ft; the eaves stack and (found in passing, undated-custom) the kizuma removed
- **M22 - The bath shed** (historically accurate): the bath is a room joined to the house, 20-30%, main door / stable end / a headman's floored rooms, 6 x 6-12 ft; the shed and corridor removed
- **M23 - The detached privy** (guess): the privy rolled from the Kakimochi table's sixteen sizes (it was a 6 x 6 ft guess)
- **M26 - House bearings** (historically accurate): the quarter-turned tenth removed (QUARTER_TURN_SHARE); houses turn with their lane
- **M32 - The separated net** (historically accurate): the DrainageDitch modal: the separated net is the Minuma layout, not modern consolidation
- **M34 - The wet toe along the collector** (historically accurate): the modern MAFF grounding of the reed edge removed (water/600, the Marsh modal); the engine reads the fan's toe, never the drain - no geometry change; reported to the GM (ruled in 2026-08-26 unknowingly)
- **M36 - The stake-and-reed weir** (historically accurate): the weir fence woven with brushwood, not reed (the Weir modal, brook.py)
- **M39 - Too wet to build on** (historically accurate): the well keep-out re-grounded as this project's decision (0058, 660); the two modern well manuals marked Not cited
- **M49 - The take-yabu** (historically accurate): the take-yabu thicket seated at the settlement's edge behind its back row, not the field margin
- **M54 - The polder parcel** (historically accurate): the rice polder's cell 110 -> 190 ft (three mu, the 1897 fish-scale register); no pool map rolls it
- **M55 - Dike planting rows** (historically accurate): the dikes.py comment re-pointed at Pan Jixun; no geometry
- **M56 - The pond grid** (historically accurate): POND_LAYOUTS mosaic only; reversal of the GM's knob of 2026-08-18 reported
- **M57 - Dike-pond sluices** (historically accurate): the per-pond sluice removed (PondSluice retired, the sty keep-clear and its gate test with it); reversal of the GM's 2026-07-22 request reported
- **M58 - The 6:4 ratio** (historically accurate): the water inset 11 -> 23 ft: 0.62 water per parcel on Kuwabata (was 0.80)
- **M59 - Fry ponds on the smallest parcels** (historically accurate): the fry pond no longer a 1-3 mu parcel form by share (see M60)
- **M60 - One parcel in ten a fry pond** (historically accurate): FRY_FORMS knob: none, or a fry village (the smallest ponds up to 7/10 of the water); the one-in-ten removed
- **M61 - The sty at the water** (historically accurate): the PigSty modal: on the pond bank as the 1639 pen; no flush-into-the-pond claim
- **M62 - The pig shed on the dike** (historically accurate): the 5-10 m shed-dike width not a rule the maps follow (PigSty modal)
- **M65 - The sanctuary fence** (historically accurate): the sanctuary fence dropped from the wealth knob (programs.md); no kind drew it
- **M66 - The swept collar** (historically accurate): no swept collar at arches or graves (the clearings' collars 30 -> 0); the precinct's ground kept, not called swept (key precinct clearing); undated-custom (shrine half)
- **M68 - One ground per village** (historically accurate): no hamlet burial ground of its own (hamlet_burial village_ground only); undated-custom
- **M69 - The crematory's set-back** (guess): the 390 ft crematory set-back relabeled a guess (190); no scripted map draws it
- **M70 - Cremation-ground size and fire bed** (historically accurate): the cremation ground open-air on most seats (ROOFED_SHARE 0.25), no pyre platform or hut
- **M71 - Six stone jizo** (historically accurate): the six jizo only at a burial ground's entrance; the village cremation ground on its own draws none
- **M75 - Set-back from water** (historically accurate): the scaled water set-backs gone: the village cremation ground keeps a bank margin only; the hamlet's own ground (which carried them) retired by M68
- **M77 - Burial distance** (historically accurate): no set distance drawn; the village cremation's 650 ft is a search reach, relabeled; downstream kept as a drawing tie-break only (attested today only)
- **M81 - The fence as a gift** (historically accurate): as M65
- **M97 - Well capacity** (historically accurate): the Well modal: the Beijing figure, not the Sphere standard
- **M104 - The charcoal cooling ground** (historically accurate): the charcoal yard's cooling apron removed from the engine; the CharcoalStore and cart-yard modals drop the cooling and 30 ft gap
- **M105 - Bale sizes** (historically accurate): the bale notes (TaxBarge, CharcoalBales modals)
- **M111 - The kitchen door** (historically accurate): the Door modal says nothing of who used the kitchen door
- **M112 - The 67-tsubo house** (historically accurate): the Residence and Kitchen modals measure against the 49-tsubo house of 1794, not the 67-tsubo Meiji plan (the sheets were already at 49)
- **M114 - The notice board at the gate** (guess): the notice board: notices at the office gate accurate (Chinese county office), the freestanding board a guess
- **M115 - The striking bundle** (historically accurate): Ubame's striking bundle replaced by upright posts; the knob's bundle value gone; undated-custom
- **M119 - Bunk rooms** (historically accurate): no bunk rooms (Barracks modal, buildings.md, Hayakawa's sheet comment); the size band's recalibration to the staff rowhouse recorded (future-work/compounds)
- **M124 - Private landings** (historically accurate): the Dock modal: a private back-gate landing is modern only; Hayakawa's steps across the street stand; legacy maps' back-gate landings owed at conversion
- **M125 - The boatmen's water-god shrine** (historically accurate): the boatmen's altar is the boats' guardian's shrine (Hayakawa sheet, modal); undated-custom
- **The woodpile's kizuma** (found in passing; historically accurate): the stacked-wall form removed - undated modern
  pages only (undated-custom); the woodpile is drawn as a lean-to shed.
- **The dike-pond water inset** (guess, calibration): 23 ft, six parts water in ten on Kuwabata (0.62 measured); the
  6:4 ratio is the record's, the inset that reaches it is calibrated on the map.

## Review history

- Round 1 (spec-fidelity, 2026-09-28): CHANGES REQUIRED, two findings; D2 / FR-007 judged legitimate. (1) D1 counted an
  undated modern record of custom as premodern - an exception to its own rule and to the GM's handling of cane and
  mulberry; it is now MODERN-ONLY tagged `undated-custom`. (2) FR-006 held GM-ruled forms back, where the GM's own
  example (the duck pen) is one to eliminate; such forms are now eliminated and the reversal reported, with only a form
  ruled in knowingly going to the GM first (User Stories 1 and 3, SC-004). The legacy count, 18, was confirmed by
  counting the directories.
- Round 2 (spec-fidelity, 2026-09-28): FAITHFUL. Both fixes confirmed against the diff; the knowingly-ruled exception
  checked as an exception and held (it only asks the GM before removal, and never keeps the form); the 18 legacy maps
  recounted. No new findings.
