# ochiba-roundtrip-test - design notes (round-trip TEST artifact)

**Program type**: magistrate's manor (county magistracy) - round-trip TEST artifact.

This is NOT a replacement for `ochiba-magistracy.svg`. It is the OUTPUT of feeding the
EXISTING hand-authored Ochiba's real program (envelope, court-spine, and building masses
measured off the finished map at 3 px = 1 ft) back through the perimeter-first compound generator
(feature 008; rebuilt in Rust from its derivation by feature 449 T152, `rust/mode_a/src/compound/`), to test whether
the generator composes Ochiba the way the GM hand-composed it.

Regenerate: `make map MAP=pool/magistracies/ochiba-roundtrip-test`. The program lives
in [`ochiba-roundtrip-test.compound.json`](ochiba-roundtrip-test.compound.json) (it was `ochiba_program()` in the gen until
feature 449 T152), its research claims with it.

Garden pavilions and point features (bath, wells, latrines, porch, privy, fire-tubs) are NOT
massed perimeter buildings - they are hand-placed in the final map regardless - so they are
omitted here; the placer only arranges the wall-ranging masses.

## What the test found (and drove)

The FIRST round-trip (before the placer fixes) placed 14 of 15 and dropped `residence (E)`,
exposing two real limits in the old placer: it could not rank the servants BEHIND the
residence (it only hugged walls), and its crude per-court corner reservation let a short
building block a whole corner it did not occupy. Those two findings drove the feature-008
placer rework:

1. **Second rank.** A building can be tagged `rank=2`; it sits offset inward past the rank-1
   row on its wall. Ochiba's servants (`rank=2`, N wall) now form the rear service strip
   BEHIND the residence, exactly as the hand-map ranks them.
2. **2-D collision + placement tiers.** The corner reservation is gone. Buildings are placed
   in tiers - N/S rows first (they own the corners), then E/W columns (which flow BELOW the
   N/S buildings), then the divider hall last (which flows CENTERED between the E/W columns) -
   each sliding along its wall past every obstacle via real rectangle overlap.

## Result: the placer now reproduces Ochiba

With both fixes it places all 15 with zero overflow, and the composition matches the
hand-authored map: the residence owns the N corners, the kitchen flows below the NW corner,
the servants rank behind the residence, the karo backs the divider, the Inari shrine +
cinnabar workshop hug the E wall, and in the outer court the office hall sits centered behind
the oshirasu with the tax-archive column on the W wall and the granary/barracks/cell column on
the E wall. Coverage 36%, perimeter-hugging 61%.

## Verdict

The live `ochiba-magistracy.svg` is UNCHANGED - this remains a scaffold/test artifact, because
the finished map carries particulars the placer does not (the two-block flying-geese massing,
the garden bath pavilion, altars/relics/annotations, wells, latrines, fire-tubs). But the
round-trip achieved its goal: the placer can now express a fully-composed residential court,
not just an administrative one. A NEW manor can start from a draft like this and be
hand-refined, and the residential-court composition will already be right.

2026-07-24 wall-ink clearance: regenerated after `compound.py` stopped seating wall-hugging
buildings on the wall CENTERLINE. The wall is drawn at true thickness centered on the
boundary, so half of it lies inside - every rank-1 building here had been standing 1.5 ft
inside the masonry, with its own outline swallowed by the wall stroke. The placer now leaves
the ink plus a foot and a half clear of its face (3 ft off a compound wall's centerline, 2.5 ft off the divider's; feature 374 wave 134, research 0092's "a foot or two"), and the inner-court
garden zone moved 36 -> 38 ft so the shifted N-wall row still clears it. Checked by
`tools/pack_audit.py` `structures_on_walls`; see docs/buildings.md "Walls and gates".

2026-11-18 (feature 449 T182): the program's residence is Ochiba's as her sheet draws it - one 90 x 50 ft block of rooms (it was
two room-less bars, 90 and 93 x 25 ft), the rear strip behind it and the kitchen as its ell - so the placer seats the house's two
privies (0101). Its rooms at the ordinary houses' sizes, in the palace order (the round arbiter's ask:449-T182-room-layout and
ask:449-T182-room-scope; the bands are the kinds' Guesses, applied to the generated plans): the reception 28 x 15 ft at the east
end of the garden row, the lord's quarters 25 x 15 ft behind it, the family quarters 20 x 18 ft at the row's west end, the guest
room 42 x 18 ft between; behind the garden row a 6 ft corridor, stepped 3 ft at the reception, drawn as a passage (a lighter floor, a dotted edge) and captioned;
the back row captioned bays of inner rooms in two ranks - three bays 14 ft deep along the north wall side (32.7, 32.3 and 25 ft long), two 12 ft deep behind the west two (32.7 and 32.3 ft) - the maids' room 14 x 12 ft at the west end of the second rank's west bay; the corridor pieces drawn as one passage, one dotted outline round them and one caption. A door-kind building's fire-water tub is seated
only within reach of one of its doors (compound_parts.py), so the karo's house, whose door faces the house 4 ft off, takes none (no
check asks one there).

2026-11-19 (feature 449 T187): the storehouses stand behind the house again, in its rear strip on the north wall as Ochiba's
sheet draws them (0091's drawing page: "The household's storehouses stand behind the house"): they were the north wall's second
rank, behind the house while it stood on the wall, and once T182 set the house off the wall that rank stood before it, the
storehouses' backs to the reception. The senior retainers' long-house is drawn as Ochiba's three dwellings of 17 ft, a door to
each on its south face, and the barracks as her two of 16.5 ft, the north one's door on its court face and the south one's on
its south end, where the garrison privy stands before the court face (0097, 0106: each dwelling with a door of its own); both
were drawn undivided behind one door, which `lodging_entrances` now refuses. The kitchen still joins the house's east end - the
placer cannot seat the house with the kitchen first (measured: the house then finds no seat), and no page places a kitchen's end -
and the guests' privy stands on the rear face behind the reception's span, as 0101's drawing page places it. The room bands are
a guide for a generated plan's rooms that no check holds.

2026-11-19 (feature 449 T152): drawn by the compound generator rebuilt in Rust from its derivation
(`specs/449-rust-codebase/derivations/T208-compound.md`), the program moved into the spec file. What the program needed, room first
(the GM, 2026-10-12), each a knob of the program, never a squeeze: the barracks' order 4 -> 7, so the north end of the east column is
the barracks' and the granary flows below it (with the granary seated first, pushed below the practice ground's band, the barracks'
33 ft found no room in the column); the kitchen's door at 0.75 of its court face, so the bath has its service side by the house; and the ground before the family
rooms, between the house and the divider west of the karo's house, named `inner court` (about 64 x 24 ft that the void rule of
0116's drawing page refuses unnamed), and the ground north of the garden between the kitchen and the shrine column named `service
yard` (106 x 48 ft, as Ochiba's own sheet names the kitchen's work ground), the central open ground the old sheet left unnamed. The hearing court's floor is white gravel, the floor knob's first form (0099's drawing page: white gravel or river cobbles, each plan taking one), as Ochiba's own sheet captions it. The gatehouse stands in the south-west corner, as before: the program's forecourt holds the ground
beside the gate (docs/buildings.md puts a gatehouse beside the gate - the forecourt zone, measured off Ochiba's sheet, is the program's).
The shrine's tree stands in the ground held past the shrine's south end as the shrine is seated, the cinnabar workshop below it. The
water depth, each well's gear and roof rolled by the docs' formula (`random.Random(zlib.crc32(b"<sheet>:<knob>"))`), the wells numbered
kitchen, garden, stables: water depth deep; well gear 1 pulley frame, well roof 1 roof; well gear 2 sweep, well roof 2 roof; well gear 3
sweep, well roof 3 open.

2026-11-22 (feature 449 T276): an armory room in the office hall's west end, its back row (14 x 20 ft, 0123's Pingyao; its size and the back row a GUESS),
the program's armory made required (knob 4: every seat keeps one); the hall, not a gate range, because the main gate here is a one-bay gate with a gatehouse beside it and no gate range, so knob 4 leaves the hall's bay and rolls no armory site; the hall's 120 ft unchanged, as the hand sheet carves its armory from the
clerks' room's end.
2026-11-22 (feature 449 T300; building-review 2026-11-22 O1, O2): the office hall drawn as Ochiba's is, not as one floor beside its armory - the back row's armory (now 14 x 16.7 ft, as the hand sheet's), day office and official study (53 x 16.7 ft each), the magistrate's dais 30 x 10 ft on the front band's south face and a clerk's seat each side (0113's drawing page; the room sizes the kinds' guesses); and the bare 70 x 16 ft strip behind the residence named a rear yard, as the hand sheet's rear yard takes the rest of its strip (a GUESS: no source names a rear yard). The hall's west door in its front band (feature 449 T299), as the hand sheet's, so the armory's arms leave by the hall's west end (a GUESS: no source states an armory's doors).
2026-11-22 (feature 449 T303): knob 4 now rolls the armory's site from the map's seed among the sites the sheet offers, so this one-bay gate's sheet rolls between the hall's bay and a store of its own - exactly `random.Random(zlib.crc32(b"ochiba-roundtrip-test:armory site")).choice(["office hall", "a store of its own"])` = office hall - and the armory stays in the hall (the T276 line's "rolls no armory site" is superseded); `armory_site` holds it.
