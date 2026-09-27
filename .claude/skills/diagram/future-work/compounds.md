# Future work: compounds (Mode A plans)

**Everything to do with a walled compound drawn as an interior plan** rather than a settlement in its
fields: magistracies today, and - as they are built - samurai city estates, governor's mansions,
samurai country estates, temple precincts drawn in their own right, and keeps.

**This file was empty until 2026-09-26**, and the 2026-08-24 note that said so predicted why: nobody had
looked at a compound recently. Feature 262 (the interactive magistracy pages) looked - it measured every
drawn kind against the whole research record (`specs/262-interactive-magistracy-pages/coverage.md`) and ran
`building-review` over the Ochiba page - and what it found is below.

## Research owed (recorded 2026-09-26; HELD by the GM)

The GM, 2026-09-26: *"I will hold off on research passes for now because we're currently working on the
research process for token efficiency, but make sure that is recorded as needing a research pass later ...
This includes places where our existing research contradicts itself."* So nothing here is to be researched
until the GM picks it up; each item is a research QUESTION with what the record holds today. The page makes
each visible to a reader: an unresearched kind has no "See references" link, a guess leads with "This is a
guess", and a part researched thinly is disclosed in the kind's caveat (`l7r/diagram/interactive/compound_kinds/`).

### Kinds shown as accurate with no research section behind them

Their "accurate" was carried from `buildings/types.json`'s program item (spec 262 FR-005 forbade
re-deciding it), so the page does not announce a liberty - but a reader finds no references.

- **gatehouse** - a monban-sho beside the opening, ~40 by 14 ft. No entry covers it.
- **bath** - a detached pavilion of 12-18 ft. The record's only bath is a farmstead bath shed.
- **guest quarters** - only the guest's door is researched ('Guest doors feed courts, not flanks'); the room
  and Hayakawa's detached guest house are not.

### Kinds labeled guess because the record is silent

- **clerks' room** - `types.json` already called it a guess; 'Clerks are few, local, and heimen' covers the
  clerks, not the room (Ochiba and Ubame draw it as a room of the office hall, Hayakawa as its own building).
- **karo's house** - a chief retainer's separate house in the residence court; the rule is `buildings.md`'s
  interior-audit prose, not a research entry.
- **kennel** (Ubame), **writing pavilion** (Ubame) - each made by the map's story; both have real counterparts.
- **salt wards** (Hayakawa) - morijio is named only in `buildings.md`; no canon line, no research entry.

### Parts of researched kinds that the research does not reach (disclosed in their caveats)

- river landing: the river watch and the boatmen's altar; parley room: supported only by analogy to
  'Drawing a clan border'; Ubame's cousin-to-cousin ancestral alcove (the entry covers father to son);
  road widths; the engawa; the shrine garden; the vegetable garden's north seat and size; why a border
  posting keeps a border court.

### Research sections resting on a source no reader can open

- 'Guest doors feed courts, not flanks' - the staged arrival (gate, court or garden, genkan) has no readable
  source; it rests on the GM's 2026-07 rule.
- the kitchen's 67-tsubo mid-rank house and the stable-stall figures - the record's own estimates.
- the branch office with two shrines - an excavation plan no one can open.

### Where the record contradicts the sheets, or itself

1. **The hearing court** - 'No interrogation room' quotes Takayama's shirasu as paved with stone and roofed;
   every sheet draws an open court of white sand, and the program item calls the sand court accurate.
2. **Carts** - the ways record ('What vehicle used a village lane') confines carts to city streets and has them
   barred from highways; the sheets draw cart gates, Ubame's cart yard and Hayakawa's bale-cart lane.
3. **The cell's size** - four figures: `types.json` (a remand cage ~10 by 12 ft), `buildings.md` (18 by 15 ft),
   'The Mode A scale is 3 px = 1 ft' (23 by 17 ft drawn), and the program band (8-26 ft).
4. **Wall thickness** - the religion-and-death entry on gates and walls draws compound walls at 1.5-2 ft;
   'A compound wall is a building, not a boundary line', the scale entry and `buildings.md` say 3 ft (the
   modal follows the last, on the GM's ruling in that entry).
5. **The main gate's width** - the sheets' 13.3 ft passage sits between that same entry's calibrations for a
   samurai residence gate (9-12 ft) and a yamen gatehouse (18-24 ft); which applies to a county magistracy?
6. **The charcoal store's fire gap** - 'Charcoal yards: a tallied depot' derives a 30 ft gap for charcoal
   stacks; Ubame's store is a sealed plaster kura ~16 ft across the cart yard. Does the gap apply to a kura?
7. **The notice board** - the bench's board kept separate from the town's kosatsuba is `programs.md`'s
   division, not the record's.

### Opened by the 2026-09-26 reception move on Ochiba (building-review)

- **Should a guest cross the viewing garden to reach the genkan?** The genkan now sits on the reception's
  garden face. 'Guest doors feed courts, not flanks' allows "court or garden", and 'The shady rear is the
  service strip' places the garden south of the formal rooms, but neither says the genkan opened onto that
  garden; Takayama Jinya's entrance faces the gate's approach and its reception looks onto a separate
  garden. Was the approach a forecourt fenced off from the viewing garden (a naka-kaki or shiorido), or a
  path through it? If both are attested, a knob.
- **The pond on the nakamon-to-genkan axis** - the ceremonial route detours round it with no drawn path; the
  fix is a drawn stepping-stone path or the genkan moved west within the reception bay (x ~528-568), once
  the question above is answered.
- **Did an ordinary posting's private rooms have a small garden of their own?** Ochiba's lord's and family
  rooms now look south onto the kitchen roof.
- **The order of the residence's rooms** - Ochiba now runs reception, then the lord's rooms, then the family's
  deepest (omote, naka-oku, oku), on the building-review's reading of Takayama Jinya; no research entry records
  the gradient. A rendering choice awaiting its research.

### Canon gaps (for the GM, not research)

- Ubame, Hayakawa, the Kurogi, Moriguchi and Nagahara are absent from the mounted `l7r.md`, though Ubame's
  notes cite it (and cite line 832 for the Ministry controlling shrines, where 832 has the Ministry of Rites
  deciding doctrine). Their particulars rest on each map's own notes.
- Ubame's notes call meeting on the border line "standard practice", unsourced.
- "Chigiri-no-Chou" (Ochiba, at the Myobu altar) appears in no mounted setting file; it is canon on Obsidian Portal,
  in Kitsune Tatsuya's GM-only notes (the Ledger of Broken Bowls; found 2026-09-27, feature 264).

### Opened by feature 264 - the parts of features as their own kinds (2026-09-27)

The GM asked for every feature drawn inside a feature to highlight and open on its own; each part got a kind written
from the existing record (`specs/264-nested-features-own-kinds/coverage.md` is the measurement). Splitting a part
out of an accurate parent can drop it to `guess`, because the parent's sections never covered it - these are now
visible where they were hidden inside the parent's write-up.

- **Guess, record silent** (each a research question): the **garden pond** of a shoin residence garden (form, size,
  whether a county post kept one); the **stone lantern** in a residence garden, and whether a receiving court kept one
  (Ubame's border court); **garden pines**; the **engawa** along a shoin residence's garden face (`shoinzukuri-jawiki`
  is the first page to read); the **residence corridor** (watari-roka) and the offset two-block massing itself;
  the **clerks' seats** - who sat beside the magistrate at an Edo hearing, and where; a **boatmen's altar** at a river
  landing; a **river watch** post (kawa-bansho) at a landing; storm shutters (amado), only if Ubame's **shuttered
  wing** is to be grounded beyond its story.
- **Accurate but thin** (disclosed in the caveats): the **hearth**'s form - the record names the kitchen's kamado
  range, while Ochiba and Ubame draw a sunken irori; the **granary stilts** - how a grain kura's floor was raised
  (posts or a stone base) and why away from a river, since the one reason the record gives is flood at a quay; the
  **striking posts** and **weapon rack** as objects (form, height, count); the **balance beam**'s form (beam or
  steelyard); a sourced statement of the **lord's quarters** beyond the private study; drawn **door** widths.
- **Contradictions and tensions**: the one genkan the record attests (Takayama) is on the OFFICE block, where all
  three sheets put their only genkan on the residence; the record makes stepped landings (gangi) the norm and a pier
  the exception for a shelving bank, where Hayakawa draws a pier and no steps with no note that its bank shelves;
  Hayakawa's one torii serves two shrines, a case the torii sections do not address; the hearing court's kneeling
  marks are drawn on open sand where Takayama's court was stone-paved and roofed (carried from 262).
- **Raised by the three building reviews (2026-09-27), each a research question**: a genkan approached across the
  formal garden, where the usual surviving form fronts a court facing the gate; the kneeling parties on mushiro
  straw mats over the gravel rather than on marked places; whether several kami share one hall's altar; the clerks'
  seats' size (drawn ~27 by 7 ft against a writing place of about one tatami); the garden pines' crowns (drawn 4-6
  ft, where mature garden pines run 15-30 ft); the torii's distance from a compound hall (the record's ~20 ft is a
  village shrine's; Ubame's stands ~5 ft off, and the wood-kami altar sits on the same axis just past it); an irori
  on a raised floor beside a doma with kamado, a common samurai kitchen form - if attested, the hearth becomes a
  knob; the tax barge's bales drawn ~4 ft across against a tawara of ~2.5 by 1.5 ft.
- **Drawing defects the reviews found outside this feature** (each a sheet edit for a later session): Hayakawa's
  reception bay, its engawa and its genkan face the kitchen's flank 11 ft away rather than the garden (B120, B230);
  Hayakawa's karo's door opens 0.3 ft short of the court divider, and its servants' door into the residence's north
  wall 2 ft away; Ochiba's and Ubame's kitchens draw no door of their own.
- **Canon, settled from Obsidian Portal (2026-09-27)**: the river-stone stroke practice, the lacquer bowls drying
  in the workshop (replacement Pact-Bowls, lacquered on site) and the Chigiri-no-Chou (the Ledger of Broken Bowls)
  are all in Kitsune Tatsuya's GM-only notes - not missing canon, as this file and 262's coverage had it. Whether
  a magistracy page may carry GM-only notes is the GM's call; until they rule, the stroke-practice line (262's,
  under the cinnabar workshop) is OFF Ochiba's page (removed 2026-09-27), and the other Ochiba notes that may rest
  on the same GM-only source (the fox-fire lantern's story, the Chigiri-no-Chou) are left as 262 shipped them.
- **Hamlet labels in the zoomed-out hit map (unmeasured)**: a small label's blended glyph edges can answer as the
  kind one palette step away, or as none. Fixed for magistracy pages only (`raster.id_map(crisp_text=)`); the hamlet
  pages were held unchanged by feature 264's FR-008. Measure a hamlet page's small captions before changing it.

### Settled on 2026-09-26, recorded so it is not reopened

- Ochiba's threshold stones are drawn ~3.3 by 4.7 ft ON PURPOSE (GM: Ochiba is where the threshold stones are
  made and painted); canon's field stones are two fists.
- Ochiba's reception room now faces the inner garden (it faced the kitchen roof, against 'The shady rear is the
  service strip'); the genkan moved with it.
