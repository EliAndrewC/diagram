# Compound programs

*Part of the Mode A compound/building docs - the scale, vocabulary, composition rules and checklist live in [`../buildings.md`](../buildings.md).*

**Load this file when:** you are drawing a compound whose TYPE has a documented program - today the county magistrate's manor and the country shrine. A building type with no program yet is drawn from the vocabulary and the composition rules, and gets its program here before its exemplar lands (`buildings.md`, "Adding a building type").

---

## Compound programs

Per-building-type specs: the required program every instance shares, the knobs that make instances differ, and staffing/sizing anchors. The research reasoning behind each program lives on [`research/buildings.html`](../research/buildings.html) (the magistracy) and [`research/religion-and-death.html`](../research/religion-and-death.html) (the country shrine). (Planned next entries: samurai country estate, governor's compound, castle keep.)

**A type is declared once.** Each program's REQUIRED ITEMS - the label a check finds each by, the size band it is held to, the class of that band and the finding it rests on - are the declaration in [`l7r/diagram/buildings/types.json`](../l7r/diagram/buildings/types.json), and the table under each heading below is RENDERED from it by `make building-programs` (`CHECK=1` fails the gate when it is stale). Edit the declaration, never the table. The prose around a table - the composition rules, the knobs, the anchors, the staffing - is hand-written here and is what the reviewers read beside the table; the checks read the declaration (`tools/pack_audit/registry.py`, the sweep in `tests/test_mode_a_sheets.py`).

### Magistrate's manor (county magistracy)

The seat of a County Magistrate (Rank 5): a walled compound in the county town combining court, tax office, granary, garrison, and the magistrate's household. [`pool/magistracies/ochiba-magistracy/ochiba-magistracy.svg`](../pool/magistracies/ochiba-magistracy/ochiba-magistracy.svg) is the worked example - it is this generic program plus Ochiba's particulars (the hall-scale two-altar Inari shrine, the Akami-fude and Fox-Fire Lantern relics, the cinnabar workshop colonnade, the Pact-Bowl threshold stone). A new magistracy should read as the same institution while sharing none of those particulars. [`pool/magistracies/hayakawa-magistracy/hayakawa-magistracy.svg`](../pool/magistracies/hayakawa-magistracy/hayakawa-magistracy.svg) is the validation instance: the same program with every knob set differently (rich river-landing county, staff-housing option (c), guest-wing annex, two modest shrines, cell by the gatehouse).

**Composition rules** (every county magistracy; the items themselves are the table below):

- **Walled enclosure** with a formal main gate + gatehouse and at least one lesser side/rear door. One lesser door must serve the INNER court directly (a kitchen/service postern for deliveries and night-soil), so household traffic never crosses the hearing court; a busy OUTER court (stables, cell, granary) warrants a small service gate of its own too, so muck, night-soil, and prisoner transfers skip the formal gate. After placing buildings, walk the cart route from the gates to the granary and stables in your head - a route every diagram must actually have (a round-2 review caught a gatehouse-and-hearing-court squeeze that cut the granary off from the main gate). Walls mark jurisdiction more than they defend: most impressive on the public approach, plainer at the rear.
- **Guest doors feed courts, not flanks.** Every entrance intended for GUESTS opens into something suitable for receiving them - a court, a garden, a graveled forecourt - never directly into (or against the flank of) a building. Service doors deliberately do the opposite: the kitchen postern opens straight into work space. When adding any door, ask who comes through it and what they step into.
- **Two-court zoning**: public/administrative outer court at the gate; private inner court behind (residence, garden, shrine). The internal divider wall has its own gate - a household door (~24 px / 8 ft, a real nakamon, visibly narrower than the ceremonial main gate), customarily on the main axis directly BEHIND the office hall, which is deliberate: the hall itself is the privacy baffle. Formal visitors are received in the hall and go no deeper; the divider gate serves household traffic (the state/home hinge), and heavy service uses the kitchen postern, so the narrow alley behind the hall is a feature, not a defect. Checked: `two_court_zoning`.
- **The office hall is the compound's working heart**: rear day rooms (day office for tax and case business, plus the magistrate's official study), with the dais band on the south face - dais and flanking clerk positions overlooking the **sand hearing court** with kneeling positions. The residence's "private study" is for the household side of life; official business happens here. The clerks' duty room is a workroom for 3-4 heimen clerks who live in the county town and commute - a room of the hall on the drawn sheets, never clerk housing.
- **The residence** has rank-graded quarters, one formal genkan on the reception block; the family block and any detached dwelling (karo's house, guest house) reach the court by an informal door - no sealed boxes. **A rear service strip** behind it (the shady north side): the servants' nagaya plus utility (a kura, a kitchen garden, the attached family privy), OR a narrow service alley - never a wide empty band (see Latrines and the rear service strip).
- **The shrine is universal equipment**, Inari by default. Scale and dedication are the per-manor particular; Ochiba's full two-altar hall is the exception, justified by its priest-magistrate, not the norm - and even it stays subordinate in footprint to the residence (the hall-shrine ceiling, the `shrine` band below).
- **Wells** are distributed by use (kitchen, garden, stables); **latrines** roughly one per functional zone, the residence privy attached to the house, the rest against service walls near a gate; **fire-water tubs** (~8-12) at the fire-prone wooden buildings, weighted to the kitchen (2), none at the plaster kura (Fire discipline).
- **The notice board** just outside the main gate is the BENCH'S board (verdicts, edicts, bounties - the court's output, read by those who come to it); the settlement's own kosatsuba is a DIFFERENT board on the town map, posting the state's standing law at the busiest public point (`research/urban-features.html`, the notice-board entry; GM 2026-07-24). Both existed at once. Checked: `notice_board_adrift`.
- **The practice ground** stands in the outer court beside the watch's lodging - swept patch + weapon rack + striking posts, sized to the resident platoon. The compound trains daily; only a city keeps a dojo (see grounding).
- **The compound is mostly open** - building coverage in the jin'ya band, buildings ringing the courts with the court-spine (forecourt, oshirasu, garden) held open in the center, loose slack consolidated rather than the envelope shrunk (the packing grounding). Checked: `coverage_band`, `perimeter_hugging`.

**Required program**, rendered from the declaration:

<!-- types.json:magistracies -->
| item | found by the label | band (feet; either orientation) | class | why |
|---|---|---|---|---|
| `office_hall` | `/official study|^office hall$/` | 80-150 by 20-45 ft | guess | the vocabulary's ~360 by 84 px working block; no measured jin'ya office wing behind it |
| `hearing_court` | `/^HEARING COURT$|^oshirasu$/` | presence | accurate | the oshirasu before the dais - buildings.md, 'Hearing court' |
| `clerks` | `/^clerks'/` | presence | guess | the program's ~28 by 18 ft workroom for 3-4 clerks - a ROOM of the office hall on the drawn sheets, with no footprint of its own to measure, so held to presence |
| `tax_archive` | `/^tax archive$/` | 20-48 by 10-36 ft | accurate | a sealed kura of ~32-36 ft; buildings.md, 'Tax archive' |
| `granary` | `/^granary$/` | 30-60 by 14-36 ft | accurate | a staging kura ~43-50 by 25-27 ft, size-audited 2026-07 |
| `cell` | `/^cell$/` | 8-26 by 8-26 ft | accurate | a remand cage ~10 by 12 ft, true size since the glyph doctrine's retirement |
| `barracks` | `/^barracks$/` | 20-70 by 10-40 ft | guess | the vocabulary's ~80-160 px range; occupancy follows the staff-housing knob |
| `stables` | `/^stables$/` | 16-44 by 10-30 ft | accurate | a few-horse umaya, drawn smaller than the barracks - size-audited 2026-07 |
| `residence` | `/^residence/` | presence | accurate | the lord's wing, 180-200 ft long, audited and validated; a zone label |
| `kitchen` | `/^kitchen(?! garden)/` | 20-52 by 16-46 ft | accurate | an institutional daidokoro ~40 by 33 ft, smaller than a residence block - size-audited 2026-07 |
| `bath` | `/^bath$/` | 8-22 by 8-22 ft | accurate | a detached pavilion of 12-18 ft - size-audited 2026-07 |
| `inner_garden` | `/^inner garden$|^garden$/` | presence | accurate | the inner court's garden; a zone |
| `servants` | `/^servants/` | 20-90 by 8-30 ft | guess | a nagaya for ~10 servants (Ubame's runs 85 ft); no measured example behind the band |
| `shrine` | `/shrine/` | 40-1150 sq ft | accurate | a modest shrine, with the hall-shrine ceiling of ~36 by 30 ft subordinate to the residence |
| `well` | `/^well$/` | presence | convention | the curb glyph marks the well's location without claiming its pixels |
| `latrine` | `/^latrine$/` | presence | accurate | one privy per functional zone, ~3-4 |
| `fire_water` | `/^fire-water tubs$/` | presence | accurate | gutter-fed tensuioke at the wooden buildings |
| `notice_board` | `/^notice board$/` | presence | accurate | the bench's board outside the main gate |
| `practice_ground` | `/^practice ground$/` | presence | accurate | courtyard keiko; a dojo is a city institution |
| `gatehouse` | `/^gatehouse$/` | 20-56 by 6-24 ft | accurate | a monban-sho beside the opening, ~40 by 14 ft |
| `guest` | `/^guest/` | presence | accurate | a guest room in the residence or a detached guest house |

The bands are the Mode A vocabulary's sizes (buildings.md, 'Building vocabulary'), each re-derived by the size-audit in 2026-07 where it says so; a band written from the program's prose alone is labeled a guess. A zone label (RESIDENCE, HEARING COURT, inner garden) names ground or a suite rather than one structure, so it is held to presence only.
<!-- /types.json:magistracies -->

**Staffing and sizing anchors** (the Harima worked example in [budgets.md](https://github.com/EliAndrewC/l7r/blob/main/setting/budgets.md) plus `/host-l7r-repo/gm-assistant/setting/demographics.md`): ~15 working samurai - the county's "full platoon" of magistrate, senior retainers, and junior bushi, with only a handful of non-working dependents; a standing ashigaru contingent; ~3-4 heimen clerks commuting from town; and ~10 servants (cooks, grooms, cleaners) living on-grounds. The magistrate's discretionary income is ~1,000 koku/yr, and the compound handles a ~6,400 koku/yr county tax flow, most of it passed up to the governor.

**Knobs** (the axes that make two magistracies read differently):

1. **Tier.** The county magistracy is the baseline. The capital-stationed Imperial / Clan / Family magistrates get larger urban compounds with yoriki duty rooms and most staff living out in the city (the urban pattern from the grounding). The tiny end is a road checkpoint post: 2-3 samurai, one office room, a cell, a barrier gate.
2. **Posting wealth.** County magistracies are tax-farmed and exam-competed for their revenue. A rich posting shows fine timber, a guest house, generous ceremony space; a poor one shows historically-genuine deferred maintenance - patched walls, a drafty hall.
3. **Granary weight.** A staging node (grain flows through toward water transport) keeps one modest kura; a terminal store (remote county, costly transport) keeps a granary row. Read the county's Mode B geography to pick. An upland county's granary also shifts CONTENTS: more in-kind goods (soybeans, barley, local products) and a partial strongbox role, since less of its tax is rice (see grounding).
4. **Garrison emphasis.** Bandit country adds ashigaru, an armory, a watchtower; a quiet county keeps a token watch.
5. **Staff housing.** (a) Everyone in the barracks and residence wing - the default, per the mostly-unmarried working platoon; (b) plus a few attached family rowhouses inside the walls for married sergeants and corporals; (c) senior retainers keep their own houses in town and the compound holds only the duty watch - suits a wealthy or long-settled magistracy, and shows on the town's Mode B map as samurai houses near the manor.
6. **Tenure character.** A freshly-appointed exam magistrate keeps a standardized office; strong office continuity (a long line of magistrates, or inherited rites and relics like Ochiba's) accretes manor character - an ancestral alcove, mature gardens, accumulated oddities.
7. **Resident particulars.** The "Ochiba slot": shrine dedication (Bishamon for a garrison county, Daikoku for a market county), a relic, a workshop, a dojo (a personal distinction of the resident, never a default program building - see the dojo grounding bullet). Designed per-manor in conversation with the GM.
8. **Justice-front furniture.** How public-facing the bench is: a petition window separate from the trial court, a grievance drum or bell at the gate, the prominence of the notice board. Vary by clan culture.

### Country shrine (a village district's shrine)

The seat of a village district's **country monk** - the one tax-free religious figure of the district (an Adept-rank monk of the Ministry of Rites' order, per the campaign notes), who keeps the district's birth, death, marriage and travel records, performs the villagers' rites, and lives at the shrine. [`pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.svg`](../pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.svg) is the worked example, named for Hoshigaoka's district; its particulars beyond the program are open for the GM. The research behind every rule here is on [`research/religion-and-death.html`](../research/religion-and-death.html): "Does the country monk live at the shrine?" and "How big is a country shrine, and what stands in its precinct?".

**The monk lives here, and that is the historically accurate form** (GM 2026-09-19; the research pass of feature 254). Before 1868 a Japanese village's sacred site was ordinarily a shrine with a small temple attached where the shrine-monk lived and performed the villagers' rites in Buddhist form; the parish temple's priest lived in its kuri; a Qing village temple engaged a monk to reside and keep it. The two forms history also had - a pure Shinto village shrine with no resident, tended by the parishioners' rota, and the unstaffed rural temple with a commuting priest - are forms this setting does not draw. On the sheet, "lives here" means UNDER THE HALL'S ROOF by default (knob 1), not merely within the fence.

**Composition rules** (every country shrine; the items themselves are the table below):

- **A precinct bounded by a fence or hedge, never a wall** - a `<g id="fence">` of fence strokes around the ground marked `id="precinct"`, on swept gravel (`keidai-gravel`). A wall is a compound's; a shrine's boundary is the tamagaki and the grove. Checked: `fence_not_wall`.
- **The approach runs from the arch to the hall**, and the sanctuary stands BEHIND the hall on the same axis: arch, then hall, then sanctuary, each marked by id (`approach`, `arch`, `hall`, `sanctuary`). The arch stands where the way enters the precinct - it straddles the approach at the fence line, the one built thing a way runs under. Checked: `sanctuary_on_axis`, `arch_on_approach`.
- **The hall is the precinct's largest building** and, under one roof (the default), it is also the monk's home: the villagers' end toward the arch, the dwelling end behind with its kitchen garden and privy. Under the two-building form the dwelling is a farmhouse-class house beside the hall.
- **The well or basin stands beside the approach**, never on it and never under the arch - the purification stop on the way in. Checked: `well_clear_of_arch`.
- **The grove surrounds the precinct**; the hall, the arch and the approach sit in a cleared opening, not under the canopy. **The burial ground lies beside the precinct**, outside the fence, in the shrine's yard - the village rule on the village maps.
- **No office building**: a small shrine kept none, and its business was done in the monk's own rooms - the district's registers live in a writing room or record chest in the dwelling. **No bell as a requirement** (knob 2). **The tax-free fields lie off the sheet**; the sheet shows the kitchen garden and the yard.
- **Fire-water** at the wooden buildings, as at the magistracy: a tub at the hall's corners, one at the dwelling end.

**Required program**, rendered from the declaration:

<!-- types.json:country-shrines -->
| item | found by the label | band (feet; either orientation) | class | why |
|---|---|---|---|---|
| `sanctuary` | `/^sanctuary/` | 4-10 by 4-10 ft | accurate | a one-bay honden; a village example of 1789 measures 1.98 by 1.82 m |
| `hall` | `/^hall|shrine hall|hall and dwelling/` | 18-38 by 18-38 ft (under `one roof`: 2100-3600 sq ft) | accurate | a village hall of 20-35 ft on a side from measured rural examples (a 1778 Kannon hall 6.54 m square; a 1790 haiden 9.78 by 10.62 m), with a Nara temple hondō of 5 by 5 ken as the upper bound, not a village example; under one roof with the dwelling, the Kaie-ji band of 200-330 sq m - one attested example, a city Zen temple's, called rare by its own listing |
| `dwelling` | `/dwelling|monk's house|kuri/` | 34-60 by 18-38 ft (under `one roof`: absent) | guess | form accurate - a kuri resembling the farmhouse of its region; size the map's own farmhouse of 46 by 28 ft, no small kuri measured; absent as a separate building under one roof |
| `arch` | `/^arch$|torii/` | presence | accurate | the area within the torii is the sacred precinct; an arch fronts every shrine a way runs up to |
| `approach` | `/^approach$/` | presence | accurate | the sandō from the arch to the hall |
| `well` | `/^well$|basin/` | presence | accurate | the temizuya beside the approach, never under the arch |
| `fence` | `/^fence$|^hedge$/` | presence | accurate | a tamagaki or hedge bounds a shrine; a wall is a compound's |
| `grove` | `/grove/` | presence | accurate | the chinju no mori the precinct stands in |
| `burial_ground` | `/burial|graves/` | presence | accurate | the village burial ground in the shrine's yard - the record's village rule |
| `kitchen_garden` | `/^kitchen garden$|^vegetable garden$/` | presence | accurate | the household bed at the dwelling |
| `privy` | `/^privy$|^latrine$/` | presence | accurate | attached to the dwelling |
| `fire_water` | `/^fire-water/` | presence | accurate | tensuioke at the wooden buildings, as at the magistracy |
| `bell_tower` | `/bell/` | 6-16 by 6-16 ft - optional, a knob | guess | the minimal temple as 'a main hall and a bell tower' rests on one undated commercial page in the present tense; a village hall may have neither - the bell knob, its presence rule a guess for that reason |

The country monk lives at the shrine: the hall is the villagers' rite-place and the monk's home in one building by default (the GM's words of 2026-09-19; attested at Kaie-ji and called rare there), or two buildings in the ordinary parish temple's form. The bands are the measured village halls, honden and kuri of the research pass (specs/254-country-shrine/research.md R3); the precinct itself is a guess bounded by what it must contain.
<!-- /types.json:country-shrines -->

**Knobs:**

1. **Hall-and-dwelling form**: `one roof` (the default - the hall is the monk's home and the villagers' rite-place in one building, attested at Kaie-ji and called rare there) or `two buildings` (the ordinary parish temple's hall and kuri). The default is set against the sources' "rare" on the GM's own words of 2026-09-19 - "the shrine is both their home and the place where the villagers come ... if there is any choice in the matter, then I want to make that the case". Written in the notes file as `**Form**: one roof` or `**Form**: two buildings`; the program check reads it.
2. **Bell tower**: absent (default) or present - the minimal temple was "a main hall and a bell tower", and a village hall may have neither.
3. **Dedication and its furniture**: the Fortune the shrine serves and what that puts on the sheet - the instance particular, designed with the GM. The exemplar takes the rice Fortune, the ordinary rural dedication, pending the GM's word.
4. **Grove and burial-ground side**: which side of the precinct each takes, by the site (read the village map: the water-mouth grove is where the shrine already stands).
5. **Wealth**: a poor district's thatch and plain timber against a rich one's tile and lanterns.

**Size anchors** (research R3; the bands in the table): the sanctuary about 6 ft square (a one-bay honden, 1.98 by 1.82 m measured; accurate); the one-roof building 200 to 330 sq m (Kaie-ji, 25.2 m long by 8 to 13 m deep; accurate as a band from one attested example), its hall end 20 to 35 ft on a side (a 1778 village hall 6.54 m square; a 1790 haiden 9.78 by 10.62 m; a hondō 5 by 5 ken) and its dwelling end the farmhouse's 46 by 28 ft (form accurate - a kuri "resembling the farmhouse of its region"; size a guess, no small kuri measured); the precinct a GUESS bounded by its contents (no Japanese precinct area could be read; the one compound figure is Chinese, 2.5 mu). The hierarchy: the hall-and-dwelling building out-foots every other building on the sheet, and the sanctuary is the smallest.

**Staffing and income** (the campaign notes): one country monk, with a few acolytes who help farm the tax-free plot on a part-time basis, on loan from larger families in the village; the monk's income is the plot's produce plus gifts and fees for the rites performed for the villagers - which is the parish temple's own economy, the danka's fuse and the temple's exempt land.
