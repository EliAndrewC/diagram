# Future work: compounds (Mode A plans)

**Everything to do with a walled compound drawn as an interior plan** rather than a settlement in its
fields: magistracies today, and - as they are built - samurai city estates, governor's mansions,
samurai country estates, temple precincts drawn in their own right, and keeps.

A drift between a Mode A procedure (`buildings.md`, `buildings/programs.md`) and the research record is NOT tracked
here: `make claims-report` lists every one (the `buildings.md::` and `programs.md::` rows). A guess or silence the
record already labels is listed by `make open-questions`. An entry here is sheet-level or research work neither carries.

## OPEN 2026-09-28: the magistracies' rear strips, and what feature 283's reviews left open

Feature 283 moved the three magistracies' kitchen gardens out of their shady rear strips for their sun (the GM, "Move
them all"). Filling the strips they left took four `building-review` rounds a sheet; the session carried what the
fourth round still found here rather than into a fifth (spec 283, Decisions Recorded, with its cost). Each is a finding
to work, the research ones first:

- **Ubame's rear yard** (open ground since the GM's 2026-09-28 ruling to draw what the sources most safely support):
  stepping stones or a way to the two storehouse doors, a service way to the reception's privy (its cesspit has no approach that avoids a garden),
  and settle the 19 x 31 ft strip east of the reception; end the garden at the storehouses' south faces.
- **Hayakawa**: the family's way out of the inner garden (whether a wicket stood there is an absence note on
  research/questions/0104, so the sheet draws a labeled guess or none); the working well at the middle gate's mouth beside
  the guests' first stone (research: was a draw-well ever on the roji's line?); the 33 x 12 ft rear pocket, kept for
  caption seats the one placer no longer needs - judge it as dead space.
- **Ubame**: the servants' quarters' four bays under one door are the common-room form, accurate as drawn PROVIDED the
  bay divisions read as sliding partitions (research buildings 910, feature 293). Owed: look at the sheet's divisions and
  redraw them as sliding partitions if they read as walls.
- **Tools**: pack-audit's aligned-gap finder pairs two buildings across a third
  (Ochiba's "28.7 ft" nagaya-to-storehouse gap; `tools/pack_audit/checks.py` `aligned_gaps`, unchanged since 2026-08-31).

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
  answer it. A lead is already in the record: 0104.drawing.notes quotes shirobito-1717-takayama, "The route goes round
  the rooms of the goyakusho ... and continues on to the residence" - read it first.

- **How big was a roofed hearing court?** The court is roofed on every sheet now (research buildings 450), but at
  the old open court's size - larger than the office hall it fronts. No measured roofed court was found (Takayama's
  two courts are described, not measured). The size each sheet draws is a guess, disclosed in the modal; research 0099
  carries no absence note for it, so `make open-questions` cannot list it - add one or answer it.
- **Where did the Koseki form's middle gate stand relative to the offices?** The roji approach (Hayakawa, Ubame)
  runs a guest of rank behind the office hall to the divider gate; if the middle gate opened off the forecourt, the
  divider gate's place becomes a per-sheet form.
- **Hayakawa's stepped landing (sheet check)**: the record now says the steps are cut into the revetment (0176); check
  whether the sheet's steps still project past the revetment face, and redraw them if they do.

### Sources to read when a pass comes back

Closer sources named but not read (each check report's "Open" line, gathered in `outcomes.md`): Ueno 1985 (Rekihaku
bulletin vol. 6) on tablet veneration; the NILIM page on samurai-house ranks; the holding archive of the 1841 Edo
magistracy plan; Takehashi yohitsu for the Nakano dog figures; Ji Cheng's Yuanye (1631) on a study's garden siting;
the Fuchu Joge pamphlet's drawing labels, which sit only in its PDF's images and want a rendering reader.

### Drawing and tooling questions left open

- **The program example's captions and the hand-sheet placer (`labels.hand_sheet`, `seat_label` until feature 286) disagreed on 9** (feature 267, 2026-09-27: striking posts, residence, well, gatehouse, practice ground, both clerks, straw mats' seat and leader). `compound.py` seats through the one placer but with its own view: a caption's subject is one chosen shape (the rear alley, one seat, one mat) where the hand-sheet placer takes what the caption declares; it counts invisible stand-ins for tubs and stones and blocks the roofed court only after the court's own captions; and it measures every caption at the standard's character width where the hand-sheet placer measures bold, capitals and spacing (feature 267's rules). The reasons are read from the code, not measured. The fix is one view: `compound.py` builds its obstacle index with `hand_sheet.classify` over the sheet it is drawing, or `hand_sheet` gains the composer's subjects; measure first which disagreements each removes.
- Door glyphs drawn as slabs outside their walls where the rendering rule says flush (every sheet's informal doors -
  a convention question).
- The torii drawn as an elevation silhouette on Mode A sheets while `buildings.md` (feature 268) says a Mode A arch
  is drawn in plan; the "Modest shrine" bullet still says silhouette. Settle the rule, then redraw.

## Is the receiving court "swept"? (found by feature 280, 2026-09-29)

The practice ground's "swept earth" was reworded to open earth in feature 280 (M66 found the swept precinct recorded only
in modern custom). The receiving court's modal (`l7r/diagram/interactive/assets/modals/sheet/border-court.md`) still reads
"The plan draws the border court as a swept garden"; research 0224's drawing page finds swept ground at shrines and graves
recorded only in modern custom. Owed: a research pass on whether a receiving court's surface is attested swept or raked
before modern times, and the modal reworded if not.
