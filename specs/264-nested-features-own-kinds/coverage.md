# Research coverage of the nested kinds (measured 2026-09-27)

A measurement, not a decision. For every proposed NEW kind - a part drawn inside a feature on the three
hand-drawn magistracy sheets (Ochiba, Hayakawa, Ubame) - this lists the research sections that actually
say something about that kind of thing, what each one establishes, the matching `types.json` item, a
proposed label, the `Entry:` line to use, and what is owed. The rule is feature 262's
(`specs/262-interactive-magistracy-pages/coverage.md`):

- a section grounds it -> **accurate**
- the setting's canon or the map's story makes it, and it differs from history or has no historical
  counterpart -> **deviation**
- drawn larger or recolored for legibility where the record says so -> **convention**
- otherwise the `types.json` class if there is one, else **guess** (record silent).

An existing classification is carried, never re-decided: where 262 or a parent kind's docstring already
classified the part from a research section, that section covers it here. A parent kind that merely LISTS
the part in its `Covers:` line, with no section about the part behind it, does not count as coverage;
the row says so. Where the facts split one kind across two labels, the row gives the main label and names
the part that takes the other.

**How it was measured.** All 23 `research/buildings/` fragments were read in full. The other 266
question fragments (archetypes, cities/*, fields, homesteads, presentation, religion-and-death,
settlements, towns, urban-features, vegetation, water, ways) were searched for each kind's keywords -
hearth/irori/kamado, pond, lantern/toro, pine, genkan/porch, engawa/veranda, corridor/roka/watari,
door/katteguchi, zashiki/reception room/shoin/study, private/family/innermost rooms, shutter/amado,
altar/kamidana, torii, day office/goyoba/official study, clerk, kneel/tatami, stilt/raised floor/takayuka,
tategi/striking post/makiwara/weapon rack, revetment/ishigaki/quay, dock/jetty/pier/landing stage,
takasebune/barge, boatmen/funadama, watch post/bansho, balance/steelyard/scale, bale/tawara, lacquer/bowl
- and every hit that could plausibly speak to a kind was read; a section is listed only where its text
is about that kind of thing. `*.notes.html`, `_front`/`_tail`/`_citations-*` files, `research/sources/`
and the assembled pages were not used, and HTML comments inside a fragment (session notes) were not
counted as the record. Also read: the four `compound_kinds/*.py` registries (the parent kinds'
docstrings), `l7r/diagram/buildings/types.json` (every item), the three `*.notes.md`, the sheets'
SVG comments (`pool/magistracies/*/*.svg`), and a grep of `/host-l7r-repo/setting/l7r.md` for the
setting-made parts (canon, needs no citation).

`types.json` note: its `magistracies` tier now names only whole kinds (office hall, hearing court,
clerks' room, granary, residence, kitchen, garden, compound shrine, practice ground and so on) and has
NO item for any nested part; the one item that matches a proposed kind is the `country-shrines` tier's
`arch`. Rows below say "parent only" where the part's building or zone has an item and the part does not.

## Section key

Paths are relative to `.claude/skills/diagram/research/`. The heading is the fragment's own.

| id | fragment | heading |
|---|---|---|
| B010 | `buildings/010-administrative-culture-is-japan-first-for-compound-interiors.html` | Administrative culture is JAPAN-first for compound interiors |
| B020 | `buildings/020-office-in-front-residence-behind---the-two-court-split-is-universal.html` | Office in front, residence behind - the two-court split is universal |
| B030 | `buildings/030-every-administrative-compound-keeps-a-shrine.html` | Every administrative compound keeps a shrine |
| B050 | `buildings/050-clerks-are-few-local-and-heimen.html` | Clerks are few, local, and heimen |
| B080 | `buildings/080-the-granary-is-a-staging-node-not-the-terminal-store.html` | The granary is a staging node, not the terminal store |
| B090 | `buildings/090-the-courtroom-is-a-room-of-the-office-hall-not-a-freestanding-stage.html` | The courtroom is a room of the office hall, not a freestanding stage |
| B100 | `buildings/100-no-interrogation-room.html` | No interrogation room |
| B110 | `buildings/110-poverty-texture-is-historically-genuine.html` | Poverty texture is historically genuine |
| B120 | `buildings/120-guest-doors-feed-courts-not-flanks.html` | Guest doors feed courts, not flanks |
| B170 | `buildings/170-fire-water-is-distributed-to-the-halls-not-the-kura.html` | Fire-water is distributed to the halls, not the kura |
| B200 | `buildings/200-rendering--layout-is-checked-automatically-because-it-is-geometry-not-judgment.html` | Rendering / layout is checked automatically, because it is geometry not judgment |
| B210 | `buildings/210-a-dojo-is-a-city-institution-county-training-is-courtyard-keiko.html` | A dojo is a city institution; county training is courtyard keiko |
| B230 | `buildings/230-the-shady-rear-is-the-service-strip.html` | The shady rear is the service strip |
| U150 | `urban-features/150-charcoal-yards-a-tallied-depot-a-cooling-ground-and-a-weighing-floor.html` | Charcoal yards: a tallied depot, a cooling ground, and a weighing floor |
| U170 | `urban-features/170-drawing-a-clan-border.html` | Drawing a clan border |
| R080 | `religion-and-death/080-torii-are-votive-donations---the-count-records-patronage.html` | Torii are VOTIVE DONATIONS - the count records patronage |
| R090 | `religion-and-death/090-torii-spacing---two-regimes-and-nothing-in-between.html` | Torii spacing - two regimes and nothing in between |
| R120 | `religion-and-death/120-how-big-is-a-country-shrine-and-what-stands-in-its-precinct.html` | How big is a country shrine, and what stands in its precinct? Larger than a farmhouse, because it contains one |
| H210 | `homesteads/210-the-farmsteads-fixtures---privy-woodpile-manure-heap-bath-coop-household-shrine-persimmon.html` | The farmstead's fixtures - privy, woodpile, manure heap, bath, coop, household shrine, persimmon |
| W040 | `ways/040-where-does-a-villages-freight-go-onto-the-water---but-not-onto-a-canal.html` | Where does a village's freight go? Onto the water - but not onto a canal |
| CG080 | `cities/government/080-servant-housing-in-the-samurai-ward---servants-are-drawn-as-walls-not-as-houses.html` | Servant housing in the samurai ward - servants are drawn as WALLS, not as houses |
| CF140 | `cities/fabric/140-how-did-a-dense-wooden-city-watch-for-fire.html` | How did a dense wooden city watch for fire? |
| CR040 | `cities/river-cities/040-the-wharfs-working-face-piers-quays-and-stepped-landings.html` | The wharf's working face: piers, quays and stepped landings |
| CC280 | `cities/capitals/280-the-sluices-lifting-frame-the-quay-side-kura-and-the-boat-length-jetty.html` | The sluice's lifting frame, the quay-side kura, and the boat-length jetty |

Read and NOT listed (a keyword hit whose text is about something else): the half-moon / fengshui ponds
of `homesteads/180` and R130 (village geomantic ponds, not a garden pond); CF140's "trace of a single
water-supply pond" at Takayama (a fire-water pond, not ornamental); the pine hits in `vegetation/*` and
`homesteads/040` (windbreaks and hillside scrub); the lantern hits in `water/040`, `water/250` (the Toro
site); `homesteads/060`, `homesteads/140` (a farmhouse's hearth warming a magariya stable);
`cities/defenses/050` (guard and inspection posts at a city gate or the Hakone barrier - not a river post)
and CF140's neighborhood watch house (a fire watch); `cities/capitals/320` (boatmen's HOUSEHOLDS at a
wharf, not an altar); `urban-features/020`'s kneeling stone (the punishment ground, not the hearing
court); CG070 (it covers the practice ground, not its gear).

## Household

| kind | covering sections - what each establishes | types.json | proposed label | Entry: | owed |
|---|---|---|---|---|---|
| hearth | B170 - the kitchen's open kamado, "live flame all day", is the compound's top ignition source, which is why the kitchen gets two tubs. (The kitchen kind's docstring already states the kamado range from this section.) | parent only (`kitchen`) | **accurate** (the kitchen's fire). Split: Hayakawa draws a 10 by 4.3 ft kamado range, which B170 covers; Ochiba and Ubame draw a ~4.7 ft irori (notes, point-glyph lines), a form no section names | `research/buildings.html - 'Fire-water is distributed to the halls, not the kura'` | Research pass on the hearth FORM of an elite daidokoro (kamado range vs sunken irori), or redraw Ochiba's and Ubame's as a kamado. The Hayakawa notes' "a shoin kitchen combined fire + well + drain in one room" is a review finding with no section behind it |
| garden pond | NONE. The garden kind lists "ponds" in its What/Covers, but its sections (B230, B120) say nothing of a pond | parent only (`inner_garden`) | **guess** (record silent) | `research/buildings.html (no dedicated entry - recorded as silent)` | Research pass: the pond of a buke-yashiki / shoin garden (form, size, whether a county post's residence garden kept one). Ochiba's notes record "pond on axis (deliberate)" as an overruled review item - a design choice, not a finding |
| stone lantern | NONE (the only lantern hits are the Toro archaeological site). The garden kind lists "stone lanterns" with no section behind them. Not to be confused with the fox-fire lantern (its own kind, deviation) | parent only (`inner_garden`) | **guess** (record silent) | `research/buildings.html (no dedicated entry - recorded as silent)` | Research pass: the ishidoro in a residence garden; Ubame's is in the BORDER court, so the pass should say whether a receiving court kept one |
| garden pines | NONE (every pine hit is a windbreak or hillside stand) | parent only (`inner_garden`) | **guess** (record silent) | `research/buildings.html (no dedicated entry - recorded as silent)` | Research pass on garden pines in a residence garden. The sheet's comment ("old pines") and the rich-posting knob ("mature garden - laid down by generations of magistrates") are the map's story |
| genkan | B120 - arrival of rank was staged: gate, then court or garden, then "the formal stepped entrance (genkan)"; a visitor never steps from the street into a room. B090 - Takayama's 1816 office block lists the genkan with the examination room, office and great hall as one range (takayama-jinya-jawiki) | parent only (`residence`) | **accurate** (the genkan as the formal entrance). The staged arrival leading to it is the record's own reading and the GM's rule (B120 cites only kotobank-katteguchi and the GM), as the residence kind's caveat already says | `research/buildings.html - 'Guest doors feed courts, not flanks', 'The courtroom is a room of the office hall, not a freestanding stage'` | Nothing for the form. Tension to record: the one genkan B090 attests is the OFFICE block's, while all three sheets draw their only genkan on the residence's reception bay and none on the office hall |
| engawa | No section is about it. Passing mentions only: B110 - an administrator complained of snow on his verandas (the section marks it unsourced); R120 - a village haiden "with a veranda on three sides" and a temple kuri whose head priest's room has "a three-shaku corridor on its south and west sides" (religious buildings, not a residence) | parent only (`residence`) | **guess** (record silent). 262 recorded the same ("the engawa has no section"), and the residence kind's caveat says the veranda "has no entry of its own in the record" | `research/buildings.html (no dedicated entry - recorded as silent)` | Research pass: the engawa along a shoin residence's garden face. `shoinzukuri-jawiki` is already in the registry (B230 cites it) and is the first page to read |
| residence corridor | NONE. The two-block gankō massing "joined by a corridor" is a GM ruling (2026-07) in the Hayakawa notes, with no section; the residence kind's What states it without a section | parent only (`residence`) | **guess** (record silent) | `research/buildings.html (no dedicated entry - recorded as silent)` | Research pass: the watari-roka joining the blocks of an offset (flying-geese) shoin residence, and the massing itself |
| door | B120 - service circulation is "the deliberate inverse" of a guest's arrival; its source is kotobank-katteguchi, the kitchen door. CF140 - a plastered kura's "outer doors faced in earth and plaster" (the archive and charcoal-store doors). CG080 - a servants' range's doors face inward, into the compound. B200 - a door glyph sits flush to the wall it opens through (a rendering rule, "nothing physical behind it") | none | **accurate** (katteguchi, kura doors, range doors). Split: the parley-room doors ride on the parley room (**deviation**); the writing-pavilion door rides on a **guess** kind; the glyph's seat on the wall is B200's rendering rule; "every lodging block gets a drawn way in" is a building-review rule (notes), not a section | `research/buildings.html - 'Guest doors feed courts, not flanks', 'Rendering / layout is checked automatically, because it is geometry not judgment'; research/cities/fabric.html - 'How did a dense wooden city watch for fire?'; research/cities/government.html - 'Servant housing in the samurai ward'` | Nothing for the door as a thing. The drawn door WIDTHS have no section |
| lord's quarters | B090 - "the residence's private study is the wrong side of the state/home hinge for official business" (a premise of its argument, not a source's words). CG080 - Aizu's Saigo Tanomo residence sorts its 38 rooms into reception, retainers' office, family and maids'/servants' groups under one roof (no separate lord's group) | parent only (`residence`) | **accurate** (thin: the private study, B090). The occupant naming ("Tatsuya's quarters") is the GM's schematic convention (2026-07; notes, residence kind), not in the record | `research/buildings.html - 'The courtroom is a room of the office hall, not a freestanding stage'; research/cities/government.html - 'Servant housing in the samurai ward'` | Research pass if a sourced statement of the lord's own suite / shoin study is wanted; the Hayakawa notes' "the underlying zones (lord's rooms, inner family rooms, the shoin study) are historically real" rests on no section |
| family quarters | CG080 - the Aizu residence's family group under the one roof; in the Chinese form the rear row at the boundary of the innermost court goes to the owner's daughters, "so the inner rows house family rather than servants". B020 - the household lives inside the working compound, behind the office | parent only (`residence`) | **accurate**. Occupant naming is the GM's schematic convention, as above | `research/cities/government.html - 'Servant housing in the samurai ward'; research/buildings.html - 'Office in front, residence behind'` | Nothing; "deepest in the house" is supported only by the Chinese innermost-row case |
| reception room (zashiki) | B230 - the prized formal garden sat on the sunny south side "facing the reception rooms" (shoinzukuri-jawiki). CG080 - reception is one of the Aizu residence's room groups | parent only (`residence`) | **accurate** | `research/buildings.html - 'The shady rear is the service strip'; research/cities/government.html - 'Servant housing in the samurai ward'` | Nothing. The Hayakawa notes' "a residence keeps a formal reception room even with a separate office hall, per Takayama's yakutaku" is not in any section |
| shuttered wing (ubame) | NONE (no section on amado or on closed rooms) | parent only (`residence`) | **guess** (record silent). Story-made (Ubame notes knob 7: the estranged wife's rooms); closed shutters have a historical counterpart, so it is not a deviation - the same reasoning 262 applied to the kennel and the writing pavilion | `research/buildings.html (no dedicated entry - recorded as silent)` | Nothing owed for the story; a pass on amado only if the shutter form itself is to be grounded |
| inner rooms (added after the building review, 2026-09-27) | CG080 - a residence groups its rooms by use under one roof; the Chinese case puts the family in the innermost rows. The bay was first tagged `ancestral alcove`; the reviews found that called a ~30 by 25 ft bay (Ubame) and a ~41 by 25 ft zone (Hayakawa) an alcove, undoing a size-audit ruling that "an alcove is a bay, not a wing" | parent only (`residence`) | **accurate**, with the family quarters' caveat (innermost rests on the Chinese case) | `research/cities/government.html - 'Servant housing in the samurai ward'` | Nothing beyond the family quarters' row |
| nakamon (added after the building review) | B020 - the internal wall and its gate between the courts; carried whole from 262's `court divider and nakamon` row, which this feature split | parent only (`court_divider`) | **accurate**, with the carried caveat (its seat on the axis is the program's; its 8 ft width is the project's) | `research/buildings.html - 'Office in front, residence behind - the two-court split is universal'` | Tension the reviews found: the old write-up said formal visitors "go no deeper" than the office hall, while the genkan and the notes route the household's guests of rank through this door; the write-up now says official business stops at the hall and the household's guests pass. A pass on how a buke residence's guest reached its omote-genkan past a naka-mon would settle it |
| shrine altar (RULED after the building review: `deviation`; Ubame's torii glyph is the shrine's map sign, fabric of the compound shrine, not an altar) | B030 - a compound shrine is standard equipment, Inari by default, and "Ochiba's two-altar hall is the deliberate exception, justified by its priest-magistrate" (the compound shrine kind covers "their altars and inner glyphs" from it) | parent only (`shrine`) | Split, carried from 262's compound-shrine row: Ubame's Inari altar **accurate** (B030's default); Ochiba's Ta-no-Kami and Myobu altars **deviation** (B030 names the two-altar hall the deliberate exception); Hayakawa's flame (Fire Dragon) and wave (river kami) glyphs **deviation** in dedication (canon: the Elemental Dragons and elemental kami, l7r.md 3561-3563); its Ebisu corner altar is the map's story, Ebisu being canon's "fortune of honest work" (l7r.md 2175; Crab: Bishamon + Ebisu, 2184). The glyphs' dais-sized marker size is a convention stated in Ochiba's notes only, not in the record | `research/buildings.html - 'Every administrative compound keeps a shrine'` | Nothing on the dedications (canon). l7r.md has no hit for Ta-no-Kami or Myobu; Inari is "the Fortune of rice and foxes" (l7r.md 3665) |
| torii | R080 - one torii is the overwhelming mode for a true shrine, none only below the shrine tier. R090 - a village shrine's arch sits ~20 ft off its hall. R120 - "the arch marks the sacred ground"; the rule puts an arch over the approach where it crosses the fence. (H210's torii before a household shrine is a GM drawing convention for a farmstead hokora, not this case.) | `country-shrines` `arch` (accurate) "the area within the torii is the sacred precinct; an arch fronts every shrine a way runs up to" - a different tier; the magistracy tier has parent only (`shrine`) | **accurate** | `research/religion-and-death.html - 'Torii are VOTIVE DONATIONS', 'Torii spacing', 'How big is a country shrine, and what stands in its precinct?'` | Hayakawa's ONE arch shared by TWO shrines is not addressed by any section (R080/R090 count arches per shrine); recorded in the notes as a design choice |

## Office

| kind | covering sections - what each establishes | types.json | proposed label | Entry: | owed |
|---|---|---|---|---|---|
| day office | B090 - at Takayama the office wing holds the reception rooms, the day office (goyoba) and the official study, so the dais band is the front of a deeper hall with the day office behind it. B100 - questioning happens "in the day office or the hearing court like any other business" | parent only (`office_hall`) | **accurate** | `research/buildings.html - 'The courtroom is a room of the office hall, not a freestanding stage', 'No interrogation room'` | Nothing |
| official study | B090 - the official study is part of Takayama's office wing, behind the dais; the residence's private study is the wrong side of the state/home line for official business | parent only (`office_hall`) | **accurate** | `research/buildings.html - 'The courtroom is a room of the office hall, not a freestanding stage'` | Nothing |
| clerks' seats | NONE on seats at the dais. B050 covers the clerks themselves (3-4 local heimen who commute). The dais kind's What mentions "a clerk's place to either side" with no section behind it; the clerks' room kind is a guess | parent only (`office_hall`; `clerks` is the room) | **guess** (record silent) | `research/buildings.html (no dedicated entry - recorded as silent)` | Research pass: who sat beside the magistrate at an Edo hearing (clerks or recording officials at the shirasu) and where |
| kneeling positions | B010 - "raised hall over kneeling litigants" is shared by both traditions. B090 - the shirasu is one paired feature with the examination room of the office block. (The hearing court kind covers "its kneeling marks" from these.) | parent only (`hearing_court`) | **accurate**. The 3 by 3 ft half-tatami size is the notes' (true size per the 2026-07-21 ruling), with no section | `research/buildings.html - 'Administrative culture is JAPAN-first for compound interiors', 'The courtroom is a room of the office hall, not a freestanding stage'` | Carried contradiction: B100 quotes Takayama's shirasu as "paved with guri stone and ... roofed"; the sheets draw the marks on open sand |
| granary stilts | CC280 - at the Kuramae rice stores "the flood answer is the kura's own raised floor and the stone revetment, not distance". Nothing else: B080, B150, CF140 and T110 say nothing of the granary's floor (a mention in B200 is inside an HTML comment) | parent only (`granary` (accurate) "a staging kura ~43-50 by 25-27 ft") | **accurate** (thin: a kura's raised floor, CC280). Its form as corner posts is not described anywhere, and CC280's reason (river flood at a quay) fits only Hayakawa - Ochiba and Ubame are not on water | `research/cities/capitals.html - "The sluice's lifting frame"` | Research pass: how a grain kura's floor was raised (posts vs a stone plinth) and why off the river (damp, vermin) |

## Grounds

| kind | covering sections - what each establishes | types.json | proposed label | Entry: | owed |
|---|---|---|---|---|---|
| striking posts (tategi) | B210 - "Marking the GROUND and its GEAR rather than labeling a building is the honest form of the finding - rural practice left equipment, not architecture." (The practice ground kind covers "its weapon rack and striking posts" from this.) | parent only (`practice_ground`) | **accurate** (the gear as what marks practice). That the gear is tategi posts is not in the section; the posts are drawn as r2 location markers, a marker convention stated in the notes only, and the tategi/makiwara terminology is a size-audit ruling (notes) | `research/buildings.html - 'A dojo is a city institution; county training is courtyard keiko'` | Research pass if the tategi itself is to be sourced (form, height, count) |
| weapon rack | B210, as above | parent only (`practice_ground`) | **accurate** (the gear). The rack's form and its 8 by 2 ft (Ubame notes) are not in the section | `research/buildings.html - 'A dojo is a city institution; county training is courtyard keiko'` | As above, if the rack itself is to be sourced |

## Particulars

| kind | covering sections - what each establishes | types.json | proposed label | Entry: | owed |
|---|---|---|---|---|---|
| revetment (hayakawa) | CR040 - the dominant river-port form is the revetted quay face, the bank "faced with stone or timber cribbing", because a river's level moves by many feet through the year. CC280 - the stone revetment is the flood answer at the Kuramae stores | none | **accurate** | `research/cities/river-cities.html - "The wharf's working face"; research/cities/capitals.html - "The sluice's lifting frame"` | Nothing |
| dock (hayakawa) | CR040 - a pier or jetty springs from the faced bank for REACH where the bank shelves too gently for a loaded hull. CC280 - a jetty is a landing stage about a boat-length. W040 - a settlement on navigable natural water gets a boat landing or jetty as its main freight link (GM canon) | none | **accurate** | `research/cities/river-cities.html - "The wharf's working face"; research/cities/capitals.html - "The sluice's lifting frame"; research/ways.html - "Where does a village's freight go?"` | Tension: CR040 makes stepped landings (gangi) in the faced bank the NORM and the pier the exception for a shelving bank; Hayakawa draws a pier from its revetment and no stepped landing (its SVG comments name none), and no note records the bank as shelving |
| tax barge (hayakawa) | B080 - tax rice moved on HIRED commoner boats under the office's seals; the magistracy owned no hulls. CR040 - a takasebune ran from about 30 ft to 73 ft | none | **accurate** (the ~47 by 7 ft drawn barge is inside CR040's band) | `research/buildings.html - 'The granary is a staging node, not the terminal store'; research/cities/river-cities.html - "The wharf's working face"` | Nothing |
| boatmen's altar (hayakawa) | NONE. The river landing kind's caveat: "the river watch and the boatmen's altar are this map's own story, with no entry in the record" | none | **guess** (record silent); story-made (Hayakawa notes, 2026-07 accuracy review), with a plausible historical counterpart | `research/buildings.html (no dedicated entry - recorded as silent)` | Research pass: a boatmen's shrine or altar at a river landing (e.g. funadama / a landing's small shrine) |
| river watch (hayakawa) | NONE on a river post. (U140 records gate tariffs as canon, which is why the notes say the watch looks for gate-runners; it does not describe a watch.) | none | **guess** (record silent); story-made (Hayakawa notes: the watch looks for boats slipping past Nagahara's tariff gates) | `research/buildings.html (no dedicated entry - recorded as silent)` | Research pass: a river guard post (kawa-bansho) at a landing |
| balance beam (ubame) | U150 - the charcoal bale had no standard weight, so charcoal "must be weighed at the point of sale - that is the weighing floor". (The weighing floor kind covers "its balance beam and bales" from this.) | none | **accurate** (the weighing). The instrument's form - a beam balance rather than a steelyard - is not in the section | `research/urban-features.html - 'Charcoal yards: a tallied depot, a cooling ground, and a weighing floor'` | Research pass only if the instrument's form is to be sourced |
| charcoal bales (ubame) | U150 - the charcoal hyo / tawara bale, of no standard weight | none | **accurate** | `research/urban-features.html - 'Charcoal yards: a tallied depot, a cooling ground, and a weighing floor'` | Nothing (l7r.md 7181, white charcoal, is about the charcoal, not the bales) |
| parley mats (ubame) | U170 - names the parley room "with the line across its floor and kneeling mats on each side" as the architectural counterpart of the drawn line, by analogy; no historical evidence for the room | none | **deviation**, carried from the parley room (262) | `research/urban-features.html - 'Drawing a clan border'` | Nothing; the 3 by 3 ft size is the notes' |
| drying stones and bowls (ochiba) | NONE historical. Canon: threshold stones are "river-stones the size of two fists, painted with cinnabar fox-tracks", and the buried Pact-Bowls are "small lacquer bowls" (l7r.md 7165) | none | **deviation**, carried from the cinnabar workshop (262: canon-made, no historical counterpart) | `research/buildings.html (no dedicated entry - recorded as silent)` | Two gaps in the notes, not the record: the map note says the setting's record has a new magistrate practice strokes on river-stones at the colonnade - l7r.md has no such passage (grep: strokes, first season, colonnade); and it says neither the record nor the notes explain the two lacquer-black bowls, while canon's Pact-Bowls ARE small lacquer bowls (7165) - no note ties them together |

## Summary

**Kinds with no covering section (research owed):** garden pond, stone lantern, garden pines, engawa
(passing mentions only: B110 unsourced, R120 on religious buildings), residence corridor, clerks' seats,
boatmen's altar, river watch; and, resting on canon or the map's story rather than the record, the
shuttered wing (story, guess) and the drying stones and bowls (canon, deviation). Covered only thinly or
in part, with a narrower pass owed: the hearth's irori form (Ochiba, Ubame), the granary stilts' form and
their off-river reason, the lord's quarters (B090's premise only), the tategi and the weapon rack as
objects, and the balance beam's form.

**Contradictions and tensions found:**

1. Hearth: B170 names the kitchen's fire as the kamado, and Hayakawa draws a kamado range, but Ochiba
   and Ubame draw a ~4.7 ft irori; no section addresses an irori in a daidokoro.
2. Kneeling positions (carried from 262): B100 quotes Takayama's shirasu as paved with guri stone and
   roofed; the sheets draw the marks on open sand.
3. Genkan: the only genkan the record attests (B090, Takayama 1816) belongs to the OFFICE block; all
   three sheets draw their one genkan on the residence and none on the office hall.
4. Dock: CR040 makes the stepped landing (gangi) the norm and the pier the exception, for reach on a
   shelving bank; Hayakawa draws a pier and no stepped landing, and nothing records its bank as shelving.
5. Granary stilts: CC280's raised kura floor is a flood measure at a quay, which fits Hayakawa only; the
   inland granaries' raised floors have no reason in the record.
6. Torii: R080 and R090 count arches per shrine; Hayakawa's single arch serving two shrines is not
   addressed by any section.
7. Drying bowls (the notes against canon): Ochiba's map note calls the lacquer-black bowls unexplained by
   the setting's record, yet l7r.md 7165 describes the Pact-Bowls as small lacquer bowls; and the same note
   attributes the river-stone practice to the setting's record, which l7r.md does not contain.
8. Parent `Covers:` lines that claim parts no section covers: the garden kind (accurate) covers lanterns
   and ponds, the residence kind (accurate) covers the veranda strips and the corridor, the dais kind
   (accurate) describes a clerk's place to either side, and the river landing kind (accurate) covers the
   river watch and the boatmen's altar (it says so in its own caveat). Splitting these parts out changes
   their label from the parent's **accurate** to **guess**.
