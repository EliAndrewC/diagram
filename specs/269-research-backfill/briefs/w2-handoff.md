# 269 W2 handoff - water: thin sections (B24, B25)

Written 2026-09-27 by the W2 write session. Pages saved at `/tmp/l7r-check/269-w2-pages` (MANIFEST.txt, plus
`Con_Ref_83.txt` and `kaibori_booklet_2.txt`, pdftotext of the two PDFs beside them). One `source-reader` pass
covered 9 claims: 8 READ, 1 NOT-FOUND (C9, the negative search for a reed harvest at a tameike), 0 CONTRADICTED.

## Sections

- SECTION=water/090
- SECTION=water/100
- SECTION=water/160
- SECTION=water/280
- SECTION=water/340
- SECTION=fields/090

## New registry keys

- KEY=shonairyo-akusuiro-jawiki
- KEY=akusuiro-kotobank
- KEY=mazumder-2024-sediment-exclusion
- KEY=seitai-kobo-kaibori-2017

Glossary terms added: `kaibori` (13450), `bed load` (13460).

## Items

B24 SILENT - A second search (2026-09-27, in Japanese and English) again found no source putting a reed harvest on a tameike's margin. What the record now says a pond did yield is cited: its embankment and inside were mown regularly (`tameike-jawiki`), and kaibori put the dredged mud on the fields and the fish on the table (`seitai-kobo-kaibori-2017`). This went into a new question, water/340, split out of water/280 because 280 was over the 20,000-byte cap (20,625 bytes before this group touched it). 280 now points at 340. - No change to the generator: the margin's reed stays a standing fringe, and no reed-harvest feature (cut bed, racks, stacks) is drawn. 340 labels that as a guess in the negative sense.

B25 ACCURATE (with two labeled guesses kept) - The four thin sections now cite their real-world claims:
- water/090: a drain empties into a river or natural watercourse (`maff-drain-shape`, plus an Edo-period akusuiro in `shonairyo-akusuiro-jawiki`). A drain ending in a pond of its own is labeled a guess, with an absence note.
- water/100: a wet moat is fed from a river and held in stepped pools on sloping ground (`hori-jawiki`). The ring's two paths rest on a grounds note ("follows from the definitions"). The sediment claim now cites `mazumder-2024-sediment-exclusion`: an intake's position and angle govern how much bed load it takes, and the best angle in a straight channel is 120 degrees, though the text does not say which way that is measured. The claim that a square tap on a near-still moat sheds silt stays a labeled guess; its absence note gained the 2026-09-27 search.
- water/160: graves go on high, dry ground (`meiji-1884-bochi-saimoku`). On an alluvial plain, settlements stand on the levee and the back marsh is paddy (`shizen-teibo-kotobank`, `kohai-shicchi-jawiki`). A shrine hall kept off marsh now says it rests on the GM's ruling alone.
- fields/090: what akusui means (`akusuiro-kotobank`), and the Edo-period drain to a river (`shonairyo-akusuiro-jawiki`).

B25's effect on the generator is none: every rule these sections state stands as written. The one point for the generator is water/100's junction sweep. The sources support "the angle matters" but not "a square tap silts", so the sweep stays justified by legibility and the GM's catch, not by silt.

## Left open, and why

- The Mazumder paper defines its intake angle only in a figure that pdftotext cannot read. Whether its 120 degrees points downstream is not established. A check session that can see the PDF's Figure 1 could settle it and then promote or drop the water/100 guess.
- entry-drift is owed for the `Marsh` class (`interactive/classes/greenery.py`). Its `Entry:` names water/280, whose body changed: the reed-crop paragraph moved to 340. The Marsh modal says nothing of a reed harvest, so I expect IN-STEP, but the check has not been run.
- The size check still lists four questions over the cap that this group did not touch: water/070 and water/270 (W1's), homesteads/210 and vegetation/120. Each owner should split its own.
- Nothing here owes a correction to a section owned by 265, 267 or 268.
