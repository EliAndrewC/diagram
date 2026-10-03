# Feature Specification: Bamboo held out of a yard's or bed's sun

**Feature Branch**: `315-bamboo-in-the-sun` (no branch - committed on `main` in the clone)

**Created**: 2026-10-02

**Status**: Accepted (spec-fidelity, round 2)

**Input**: The GM, 2026-10-02 (verbatim in `request.md`): *"figure out whether it would need to be far away and then make
it be the distance away that it would have to be if that is appropriate. On the other hand, if you look it up and you find
that it deserves to be on the exempt list, then we can keep it on the exempt list."*

## Context (observed 2026-10-02)

Feature 310 holds every canopy tree out of a threshing yard's or garden bed's SUN GROUND: the plot widened east and west
and deepened south by a reach, from its north edge down. Each thing that casts a shadow keeps its own distance, worked out
from its height and where the late-autumn sun stands (`research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html`):
a neighbor's farmhouse, reckoned at a 20 ft ridge, keeps the south strip; a canopy tree, reckoned at the least height the
record gives a working windbreak's tree, keeps the canopy reach east, west and south. Bamboo was left out on the GM's
earlier "maybe bamboo", which the GM now says was not a ruling.

**What the research says (to be confirmed by the record's checks in the plan).** Bamboo is not low. A bamboo maker's
page (https://www.taketora.co.jp/c/special/bamboo, saved and grepped 2026-10-02) gives madake, the timber bamboo a farm
kept for its baskets and its building, culms of 10-20 m; hachiku 10-15 m; moso, the largest, 10-20 m. The record's bamboo
page already has madake reaching "roughly 20 m" in close thickets that shade out almost everything else, and its Tonami
passage lists a farm grove's bamboo stands as madake, moso, hachiku and yadake
(`research/questions/0075-bamboo-groves-chikurin.html`). Yadake is shorter, 2-5 m, and is classed as a bamboo grass (sasa),
not a bamboo (Kotobank, https://kotobank.jp/word/%E7%9F%A2%E7%AB%B9-648513; a regional plant survey,
https://mikawanoyasou.org/data/yadake.htm), so in the Tonami grove it stood beside three timber bamboos, not in their
place. The ministry's bamboo page (https://www.maff.go.jp/j/pr/aff/1301/spe1_02.html) refused the fetch (403) and is not
relied on. What the plan's reading must confirm: the timber bamboos' least height, and so whether a bamboo stand's reach
equals the canopy reach.

**Where bamboo stands on our maps** (one-shot count, observed 2026-10-02; method: the recorded stands' outlines and the
culm marks parsed from each SVG, each tested against every plot's sun ground at the canopy reach):

| bamboo | recorded today | on the five pool hamlets | in a plot's sun ground |
|---|---|---|---|
| a household's own stand, and a shared thicket | yes, as stands | 3 stands | none |
| culm marks in a farm grove's windward bands | no | part of 329 marks | none |
| culm marks among a windbreak's or belt's clumps | no | part of 329 marks | none |

So no pool map draws bamboo in a plot's sun today, but nothing holds it there: the marks are placed without the sun test
(feature 310 skipped it for them by name), and two of the three kinds are not recorded, so no check can see them.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - No bamboo shades a threshing yard or a garden bed (Priority: P1)

The GM opens any generated hamlet and every threshing yard and garden bed has open sky to its east, west and south, bamboo
included, at the distance bamboo's height gives.

**Why this priority**: it is the request: if bamboo shades, it keeps the distance its shade needs.

**Independent Test**: on every shipped hamlet and on a cohort of rolled seeds, count the bamboo - stands and culm marks -
in any plot's sun ground at bamboo's reach; the count is zero, and the count is read from a record of every bamboo mark.

**Acceptance Scenarios**:

1. **Given** a generated hamlet, **When** every bamboo stand and every bamboo culm mark is tested against every threshing
   yard and garden bed, **Then** none stands in the plot's sun ground at bamboo's reach.
2. **Given** a bamboo mark a placer would set in a plot's sun ground, **When** the placer seats it, **Then** it is refused
   there, as a canopy crown is.
3. **Given** the finished map's check, **When** it counts bamboo, **Then** it reads every drawn bamboo mark and stand
   from the manifest, and the count matches the marks drawn.

---

### User Story 2 - The record says why bamboo is held and how far (Priority: P1)

The record's sun page states that bamboo is held, cites the heights its distance comes from, and no longer calls bamboo an
exemption; the map's explanations of bamboo, the yard, the garden and the groves agree with it.

**Why this priority**: the GM asked to look it up; the answer and its sources belong in the record, beside the rule.

**Independent Test**: the sun page names bamboo among the things held, with its reach and the cited heights; no page or
modal still calls bamboo exempt from the sun rule.

**Acceptance Scenarios**:

1. **Given** the record's page on keeping yards and gardens in the sun, **When** a reader looks up bamboo, **Then** it is
   held, at a reach worked out from its least cited height, with each height footnoted to a page the reader can open.
2. **Given** every modal and record page that mentions bamboo and the sun, **When** each is read, **Then** none says
   bamboo is exempt.

---

### Edge Cases

- **Bamboo under a grove's crowns.** A culm mark drawn between the crowns of a farm's grove or a belt is held like the
  crowns beside it; where a band's crowns already keep out of the sun ground, its bamboo keeps out with them.
- **A stand that cannot be seated.** A household's stand whose every seat lies in a plot's sun is not drawn there; the
  farm keeps none, as a farm with no room keeps none today.
- **The coppiced mulberry and the tea hedge** stay outside the rule, as feature 310 ruled: they are not tall, and this
  feature changes nothing about them.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: No bamboo - a household's stand, a shared thicket, or a culm mark in a farm grove, a windbreak or a belt -
  MUST stand in a threshing yard's or garden bed's sun ground at bamboo's reach, on any scripted map.
- **FR-002**: Bamboo's reach MUST be worked out, by the same derivation the canopy reach uses (the late-autumn sun at the
  map's latitude), from the least cited height of the bamboo our stands and culm marks stand for - the timber bamboos
  (madake, hachiku, moso), the kinds the record puts in a farm's stands and grove - and stated beside the rule with the
  heights it comes from. A grove's bamboo, drawn without a kind, is held at the timber bamboos' reach.
- **FR-003**: Every bamboo placer MUST test a mark's or a stand's seat against the sun ground before drawing it, as every
  crown placer does.
- **FR-004**: Every drawn bamboo mark and stand MUST be recorded on the manifest, so the finished map's check reads them.
- **FR-005**: The finished map's check (the gate's and the cohort audit's) MUST count bamboo in a plot's sun ground beside
  the canopy crowns, from that record, and MUST find what it counts (non-vacuity).
- **FR-006**: The record's sun page, the bamboo page where it speaks of the sun, and every modal that calls bamboo exempt
  MUST be brought in step: bamboo held, its reach and its sources stated.

### Key Entities

- **Sun ground**: a plot widened east and west and deepened south by a reach, from its north edge down (feature 310).
- **Bamboo reach**: the distance a bamboo stand's late-autumn shadow carries east, west and south, from its least cited
  height.
- **Bamboo record**: every drawn bamboo mark and stand on the manifest, by place.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-004, FR-005): On the five pool hamlets and on the cohort the gate rolls, zero bamboo marks or stands
  stand in any plot's sun ground at bamboo's reach, counted from the record.
- **SC-002**: The count of bamboo marks the record holds equals the count drawn on each pool hamlet (FR-004).
- **SC-003** (FR-003, FR-005): A bamboo mark placed by hand in a plot's sun ground makes the check fail, and a placer handed
  a seat in the sun refuses it.
- **SC-004** (FR-002, FR-006): The sun page states bamboo's reach with each height it rests on footnoted and confirmed by the
  record's checks, and no page or modal calls bamboo exempt.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Bamboo is held to the sun rule, not exempt | historically accurate for the heights; the rule itself a guess, as feature 310's is | the GM asked to look it up and keep the exemption only if bamboo deserves it; the timber bamboos a farm kept stand at least as tall as the tree the canopy reach is reckoned from, in thickets that shade out almost everything else | the sun page; `tree_shade.py` |
| Bamboo's reach is worked out from the timber bamboos' least cited height, by the canopy reach's own derivation | guess (the least height, as for trees; taller stands would reach further) | the GM expected a different distance for different things; the derivation gives each thing its own distance from its own height, and what that height comes to is for the plan's reading to confirm | the sun page; the plan |
| A grove's bamboo, drawn without a kind, is held at the timber bamboos' reach, not yadake's | guess | the Tonami grove held madake, moso and hachiku beside yadake, a shorter bamboo grass; a patch drawn without a kind may hold any of them, and the tall ones decide its shade | the sun page; the bamboo drawing page |
| The coppiced mulberry and the tea hedge stay outside the rule | as feature 310 recorded | not tall; unchanged here | feature 310's spec |
| A bed slid south after the groves stand keeps its new sun ground clear of every standing crown, promised persimmon and bamboo mark | guess - the sun rule's, as feature 310's | the slide that clears a bed's morning shade moved its sun ground over a neighbor's persimmon (cohort seed 14, a regression feature 310 shipped); the rule holds wherever a bed ends up | `rolling/farmsteads.py` `beds_sun_clear` |
| On a grove farm the bed stands wholly south of the front wall, and a band in a turned bed's east reach is cut back to a pixel clear of it | guess - the layout's, as feature 310's | a bed taller than its yard rose past the east band's end, and a bed turned with its house rises past an unturned band (cohort seeds 15 and 906); the cut was 1.3 ft on cohort seed 906 at a rake of -8 degrees (one-shot, observed 2026-10-02; method: the farm's band end against its turned bed, probed on the roll) | `rolling/dispersed.py` `clear_east_of_beds` |
| The persimmon's paces stop at the dooryard - its crown's edge within about 30 ft of the house - and a farm with no seat there keeps none | historically accurate for the place (the dooryard: the fruit-tree page's `jataff-fuyu-kaki` and `toyoko-kaki` put a persimmon in the dooryard of every house; `research.md` R3); the 30 ft is the drawing page's own GUESS, as is its exact reach | paced on, a crowded farm's persimmon walked out past any dooryard onto a row's street (cohort seed 23, refused; observed 2026-10-02, method: the roll probed at the web's refusal, the trunk's box against the street's tread); on the grove-farm maps every persimmon but one stood 35 to 80 ft out (one-shot, observed 2026-10-02; method: each crown's edge measured from its house in the house's frame on the main pool) | `homestead_parts/fixture_seats.py` `PERSIMMON_DOORYARD_FT` |
| On a grove farm the persimmon may stand in its own grove behind the house, never a neighbor's, never on the flank | historically accurate for the place (the traditional igune held "a few fruit trees", Sendai's replanting plan, `research/questions/0075-bamboo-groves-chikurin.html`); the flank stays unrecorded, as the fruit-tree page says | a grove farm's front is its own plots' sun and its back the service strip before its windward band, so held off its grove it had no dooryard seat (one-shot, observed 2026-10-02; method: the regenerated pool's persimmons counted per house - with the grove seat Kashikawa keeps 16 of 20 and Mizuguchi 10 of 12, every one behind its house within the dooryard) | `fixture_seats.lay_fixtures` (`fruit`), `rolling/fit.py` `_fixtures_in_bands` |
| A household's own persimmon in a yard's or bed's sun - its own or a placed neighbor's - is dropped, decided where its homestead is laid; a template judges the tree at its seat's own rake | guess | the placer lays a chosen seat's homestead afresh (`_place_bundle`), so a tree dropped by the fit alone came back on the record in a yard's sun (cohort seed 1); and holding the template at every rake the house might take left no seat for it at all | `rolling/fit.py` `_settle_persimmon`, `rolling/bundle.py` `_bundle_geom` |
| A gateway walled in leaves along the exit strip's end, or from the first bearing turned off the downslope whose sweep is dry | guess - the track's own rule, kept | walked out clear of every steading, a gateway stopped in the corner of a farm's own grove with no way out wider than a track's gap (cohort seed 19); the connector's later fallbacks already started from the strip's end | `hamletgen/ways/track.py` `gateway_track` |
| A shared row well is not dug in the street's bend, and a row street is laid without the jogs its planned line takes from the field's edge | guess (the bend's 30 degrees over 40 ft either way) | a well in the inside of a step in the street held the street to two sharp turns 40 ft apart (observed 2026-10-02; method: the roll probed at the web's refusal, the street's drawn points), a kink on a tree lane no settle may cut, and the web was refused (cohort seed 903) | `homesteads/wells.py` `street_turns_at`, `ways/street.py` |

## Assumptions

- The legacy hand-drawn pool is untouched (frozen exhibits).
- A bamboo mark under a crown is drawn beneath it; holding it out of the sun ground changes no crown.
- Houses, plots and seats stay where the seating puts them; what gives way is bamboo, a persimmon (moved into its dooryard or its own grove, or dropped), a bed slid south only where its new sun ground is clear, and a grove band's end cut back out of a turned bed's east reach. Re-seating moves the pool's farms, as any change to what a homestead holds does.

## Review history

| round | reviewer | verdict | what it found |
|---|---|---|---|
| spec 1 | spec-fidelity | CHANGES REQUIRED | the height setting the reach left out yadake, a kind the record puts in the grove, and was stated as settled before the reading |
| spec 2 | spec-fidelity-verify | FAITHFUL | - |
| amendment 1 (the regressions 310 shipped; the persimmon) | spec-fidelity | FAITHFUL | two NOT-REVIEWABLE returns first, for unlabeled figures |
