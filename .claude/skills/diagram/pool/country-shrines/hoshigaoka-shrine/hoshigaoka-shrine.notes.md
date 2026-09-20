# Design notes: Hoshigaoka Country Shrine

**Subject**: the shrine of Hoshigaoka village district - the seat of the district's country monk - Otsuki, of the Order of Bishamon, whose record is the Obsidian Portal character of that name - who lives here, keeps the district's registers, and performs the villagers' rites. Hoshigaoka is the reference village of the water-first family (`legacy-hand-authored-pool/villages/hoshigaoka/`), whose district names the GM dictated on 2026-08-29; on its village map the shrine stands apart from the houses at the south-east water-mouth entrance on the grazing back-slope, and this sheet is that place at 3 px = 1 ft. The exemplar of the country-shrine program (feature 254), drawn to the village map (feature 257).

**Program type**: Country shrine (a village district's shrine) - see `buildings/programs.md`.

**Form**: one roof

**On map**: legacy-hand-authored-pool/villages/hoshigaoka/hoshigaoka.json - religious at (392, 1074) = hall

**The sheet matches the village map** (the GM, 2026-09-20: "we should make the diagram view match what is shown on the larger map of Hoshigaoka"). The hall's center is the map's shrine at map (392, 1074); 6 sheet px make one map px. The frame runs 100 ft either side of the axis, from 60 ft in front of the arch to 20 ft behind the well - 200 by 250 ft with the title band - and shows what the map shows there and nothing else: the hall, one arch, the well, and the swept clearing the map records around the shrine. The map's connector lane (nearest 148 ft from the arch, east of the axis), the water-mouth grove (its nearest tree 238 ft from the hall), the village graveyard (430 ft west), the crescent pond and the nearest byre all lie outside the frame. `matches_map` holds the sheet to this in both directions.

**Overridden by the map** - program items the research puts differently, drawn as the map has them because the map is the canon for the site:

- **The grove**: the program surrounds a shrine with its wood; the map draws no tree within the frame (a site item - absent here). The ground is the map's swept clearing.
- **The burial ground**: the program puts the district's dead beside the shrine; the map keeps the village graveyard 430 ft to the west (a site item - absent here).
- **The water point's place**: the research puts the purification basin beside the approach; the map sites the shrine's one well 108 ft behind the hall on the axis, and the sheet draws that well as the shrine's water and no basin (one water point, as the map has one).
- **The hall's footprint**: the map's block is 60 by 48 ft, long side east-west, so the one-roof building is drawn at that, inside the 2,100-3,600 sq ft band (2,880), rather than at the record's longer bar.
- **The arch's place**: 20 ft in front of the hall's face, where the map's one torii stands, at the fence's south side; the fence is drawn to it, so the precinct is short in front and long behind.

**Knob settings** (every knob, defaults included):

1. Hall-and-dwelling form: **one roof** (the default - the GM's form, 2026-09-19). The building is 60 by 48 ft (the map's footprint), its two uses END TO END along the ridge as at Kaie-ji: the kitchen's earthen floor at the west end (16 ft, with its own door on the north wall), the villagers' hall in the center, 28 ft wide, facing the approach with its raised step and its altar at the rear toward the sanctuary, and the monk's rooms at the east end (16 ft) with a 12 ft writing room for the district's registers in the front corner and the dwelling's own door on the east wall.
2. Bell tower: **absent** (the default).
3. Dedication: **Bishamon**, the Fortune of Strength - the GM's word for this district (2026-09-20: Hoshigaoka's village shrine is Otsuki's shrine of Bishamon, and Inari, the rice Fortune, stays the program's default). The dedication is named on the sanctuary and nothing else of it is drawn: at average wealth the sheet carries no guardian figures, and the research pass on what a Bishamon dedication puts in a rural precinct is recorded under knob 3 in `buildings/programs.md`.
4. Grove and burial-ground side: **by the map - neither** (see "Overridden by the map").
5. Wealth: **average** - thatch and plain timber, no lanterns, no guardian figures.

**Particulars**: the named monk. Otsuki registers the district's births and marriages, stamps its travel papers and teaches the village's sons and daughters their letters in the hall; his chief clerk Sadaji, the headman's second son, and two of the district's licensed ashigaru keep the records and the correspondence, so the writing room and its record chest are in daily use (his Obsidian Portal record). A relic, a second altar, a bell or a festival stage are still the GM's to add, and each goes in this file when it does.

**Deliberate choices and tolerated stretches**:

- The precinct is 100 by 162 ft, a GUESS bounded by what it must contain - and it must contain the well the map put 108 ft behind the hall, which is why the fence runs so far north: the ground between the sanctuary and the well is swept gravel, open because the map shows it open.
- The arch, the approach, the well and the fence carry no captions except the well's one word, which says what a lone curb 108 ft behind the hall is; each is declared by its `id` for the checks. The hall and the sanctuary carry the two labels the program finds them by; the captions that remain say what is instance-specific or not visible: the room uses, the dedication.
- The building is a uniform 60 by 48 ft block, the map's. The one attested one-roof example steps in depth between its two ends (Kaie-ji); the block is the map's and is kept.
- A plain break in the west fence beside the kitchen garden is the household's service way; firewood and the harvest of the tax-free plot do not pass under the arch.
- The sanctuary is 6 by 6 ft, true size, on a plinth; the arch spans 15 ft outer, 10.7 ft clear over the 10 ft approach. Both are drawn at their real size, not as markers.
- The kitchen garden and the privy stand at the dwelling ends, the privy at the back corner, the garden beside the west end - the household bed and the attached privy of the program.
- The map's generator promises a seven-arch avenue in its comment; the map's manifest records one torii and the render draws one, so the sheet draws one (spec 257 FR-009 - reported to the GM, not fixed here).

**Review log**:

- `size-audit` (2026-09-19, Opus, the previous drawing): five findings, four applied - the burial ground grown, the writing room cut to 12 ft, the north fence brought to the sanctuary, the arch's posts moved clear of the approach; the fifth, the well glyph out-measuring the sanctuary, answered by drawing the basin true. The burial ground and the basin have since left the sheet (the map).
- `building-review` (2026-09-19, Opus, the previous drawing): ten errors, all applied - the kitchen moved off the axis to the west end, the writing room a corner room, the kitchen door and the dwelling's door drawn, the privy attached, the scale bar moved, the tubs at the kitchen, the altar drawn, the service break in the fence, the dedication named.
- `size-audit` and `building-review` (2026-09-20, Opus, this drawing): pending - their rows follow when they return.
