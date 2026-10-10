# Feature Specification: The program example's captions and the hand-sheet placer (`labels.hand_sheet`, `seat_label` until feature 286) disagreed on 9

**Status**: Filed - from future-work/compounds.md, "Research owed (rewritten by feature 267, 2026-09-27)", piece 5, 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Owed at**: now

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

- **The program example's captions and the hand-sheet placer (`labels.hand_sheet`, `seat_label` until feature 286) disagreed on 9** (feature 267, 2026-09-27: striking posts, residence, well, gatehouse, practice ground, both clerks, straw mats' seat and leader). `compound.py` seats through the one placer but with its own view: a caption's subject is one chosen shape (the rear alley, one seat, one mat) where the hand-sheet placer takes what the caption declares; it counts invisible stand-ins for tubs and stones and blocks the roofed court only after the court's own captions; and it measures every caption at the standard's character width where the hand-sheet placer measures bold, capitals and spacing (feature 267's rules). The reasons are read from the code, not measured. The fix is one view: `compound.py` builds its obstacle index with `hand_sheet.classify` over the sheet it is drawing, or `hand_sheet` gains the composer's subjects; measure first which disagreements each removes.

### The context the entry gave every piece (Drawing and tooling questions left open)

Feature 267 took up everything this section held when the GM released it (*"take on whatever future work research
we've been putting off"*, 2026-09-27): 53 questions, each answered ACCURATE, KNOB, SILENT or CONTRADICTION-RESOLVED
(`specs/267-compound-research-owed/outcomes.md`), the kinds rewritten from the answers and the three sheets redrawn
(`forms.md` there holds which form each sheet takes). What is left is below - each a research QUESTION with what the
record holds today, or a silence the maps fill with a labeled guess. The page shows each to its reader: a guess leads
with "This is a guess", and a thin part is disclosed in its kind's caveat (`l7r/diagram/interactive/compound_kinds/`).

### Sources to read when a pass comes back

Closer sources named but not read (each check report's "Open" line, gathered in `outcomes.md`): Ueno 1985 (Rekihaku
bulletin vol. 6) on tablet veneration; the NILIM page on samurai-house ranks; the holding archive of the 1841 Edo
magistracy plan; Takehashi yohitsu for the Nakano dog figures; Ji Cheng's Yuanye (1631) on a study's garden siting;
the Fuchu Joge pamphlet's drawing labels, which sit only in its PDF's images and want a rendering reader.
