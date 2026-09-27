# Future work: compounds (Mode A plans)

**Everything to do with a walled compound drawn as an interior plan** rather than a settlement in its
fields: magistracies today, and - as they are built - samurai city estates, governor's mansions,
samurai country estates, temple precincts drawn in their own right, and keeps.

**This file was empty until 2026-09-26**, and the 2026-08-24 note that said so predicted why: nobody had
looked at a compound recently. Feature 262 (the interactive magistracy pages) looked - it measured every
drawn kind against the whole research record (`specs/262-interactive-magistracy-pages/coverage.md`) and ran
`building-review` over the Ochiba page - and what it found is below.

## Research owed (rewritten by feature 267, 2026-09-27)

Feature 267 took up everything this section held when the GM released it (*"take on whatever future work research
we've been putting off"*, 2026-09-27): 53 questions, each answered ACCURATE, KNOB, SILENT or CONTRADICTION-RESOLVED
(`specs/267-compound-research-owed/outcomes.md`), the kinds rewritten from the answers and the three sheets redrawn
(`forms.md` there holds which form each sheet takes). What is left is below - each a research QUESTION with what the
record holds today, or a silence the maps fill with a labeled guess. The page shows each to its reader: a guess leads
with "This is a guess", and a thin part is disclosed in its kind's caveat (`l7r/diagram/interactive/compound_kinds/`).

### Questions the research opened (each needs a pass)

- **Did Takayama's guest route from the office genkan to the residence run indoors?** Research buildings 370 places
  the genkan on the office and says the visitors' route runs through the office to the residence; Ochiba draws it as
  the office's rear door, the middle gate and the garden path to the reception's veranda stone. Whether that way ran
  under roof (a corridor, the office's own rooms) is not recorded; a Takayama Jin'ya plan with its watari-rōka would
  answer it.

- **How big was a roofed hearing court?** The court is roofed on every sheet now (research buildings 450), but at
  the old open court's size - larger than the office hall it fronts. No measured roofed court was found (Takayama's
  two courts are described, not measured). The size each sheet draws is a guess, disclosed; if a court turns out to
  be a room-scale bay, the sheets shrink it.
- **Was the knee-high striking bundle an adult drill in the period?** Research buildings 560 attests the adult bundle
  only as present-day practice; its one writer holds the older form a children's exercise of one to a few branches.
  Ubame draws the bundle as the knob's second form, labeled a guess in its notes.
- **Where did the Koseki form's middle gate stand relative to the offices?** The roji approach (Hayakawa, Ubame)
  runs a guest of rank behind the office hall to the divider gate; if the middle gate opened off the forecourt, the
  divider gate's place becomes a per-sheet form.
- **What stood between the office's genkan and its working rooms at Takayama** (a genkan-no-ma, a shikidai)? Ochiba's
  genkan opens into the office hall's end room.
- **Were stepped landings (gangi) cut back into the bank or built out into the water?** Hayakawa's steps project a
  few feet past the revetment face.
- **How often was a grave drawn in the fields, by field kind?** The rate (about three maps in ten) is a degree chosen
  for the maps; the record argues "common where the custom held" and gives no number (research fields 220).
- **Where were a house's ancestral tablets kept** - a butsudan in the butsuma beside the zashiki, which the kind calls
  the ancestral alcove? The placing at the formal end stands (research buildings 270); the word may not.

### Silences the maps fill with a labeled guess

Searched and not found (the dated absence notes are in the record): a household kennel's form and seat (590); a study
standing apart at an official's compound, and its size (600); two sides meeting in a room across their border -
history kept each party on its own ground (610; Ubame's parley room is the setting's own); the road's width before a
compound's gate (ways 070); a gap between a charcoal kura and its neighbors (urban-features 210); a household keeping
an unused wing shuttered by day (350); tablets of predecessors in office rather than in the house's line (280); a torii's
distance from its hall (religion-and-death 230); a bench's notice board at the office's own gate before Meiji (470);
the size of the clerks' place in the hall, of the cell within the span read, of a bath, a stable stall and a kitchen.

### Sources to read when a pass comes back

Closer sources named but not read (each check report's "Open" line, gathered in `outcomes.md`): Ueno 1985 (Rekihaku
bulletin vol. 6) on tablet veneration; the NILIM page on samurai-house ranks; the holding archive of the 1841 Edo
magistracy plan; Takehashi yohitsu for the Nakano dog figures; Ji Cheng's Yuanye (1631) on a study's garden siting;
the Fuchu Joge pamphlet's drawing labels, which sit only in its PDF's images and want a rendering reader.

### Canon gaps (for the GM, not research)

- Ubame, Hayakawa, the Kurogi, Moriguchi and Nagahara are absent from the mounted `l7r.md`, though Ubame's
  notes cite it (and cite line 832 for the Ministry controlling shrines, where 832 has the Ministry of Rites
  deciding doctrine). Their particulars rest on each map's own notes.
- Whether a magistracy page may carry GM-only Obsidian Portal notes is the GM's call; until they rule, the
  stroke-practice line is off Ochiba's page, and the Ochiba notes that may rest on the same GM-only source (the
  fox-fire lantern's story, the Chigiri-no-Chou) are left as feature 262 shipped them.

### Drawing and tooling questions left open

- **The program example's captions and `seat_label` disagree on 9** (feature 267, 2026-09-27: striking posts, residence, well, gatehouse, practice ground, both clerks, straw mats' seat and leader). `compound.py` seats through the one placer but with its own view: a caption's subject is one chosen shape (the rear alley, one seat, one mat) where `seat_label` takes every drawn shape of the kind; it counts invisible stand-ins for tubs and stones and blocks the roofed court only after the court's own captions; and it measures every caption at the standard's character width where `seat_label` measures bold, capitals and spacing (feature 267's rules). The reasons are read from the code, not measured. The fix is one view: `compound.py` builds its obstacle index with `seat_label.classify` over the sheet it is drawing, or `seat_label` gains the composer's subjects; measure first which disagreements each removes.
- Door glyphs drawn as slabs outside their walls where the rendering rule says flush (every sheet's informal doors -
  a convention question).
- The torii drawn as an elevation silhouette on Mode A sheets while `buildings.md` (feature 268) says a Mode A arch
  is drawn in plan; the "Modest shrine" bullet still says silhouette. Settle the rule, then redraw.
- Hamlet labels in the zoomed-out hit map (unmeasured): a small label's blended glyph edges can answer as the kind one
  palette step away. Fixed for magistracy pages only (`raster.id_map(crisp_text=)`); measure a hamlet page first.
- The glossary tooltip matcher has no proper-name exclusion: "Shinden Togashi" picks up the shinden (new fields)
  tooltip (religion-and-death 220's check).

### Settled on 2026-09-26, recorded so it is not reopened

- Ochiba's threshold stones are drawn ~3.3 by 4.7 ft ON PURPOSE (GM: Ochiba is where the threshold stones are
  made and painted); canon's field stones are two fists.
- Ochiba's reception room now faces the inner garden (it faced the kitchen roof, against 'The shady rear is the
  service strip'); the genkan moved with it.
