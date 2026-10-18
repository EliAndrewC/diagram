# Handoff - feature 385 T10, round 2, session 1 (write)

Commit eb5c8c265. Claims on 0018 and 0027 taken and released.

## Changed headings

- SECTION=0018/how-our-maps-draw-dike-ponds-sangji-yutang
- SECTION=0027/how-our-maps-draw-a-polders-dike-and-its-trees

In 0018's drawing page: the splits bullet names all five, labeled, with the 1:1 (fao-ac241e) and the gazetteer office's
three-to-seven (gd-gazetteer-sangji) and the caveat on order; the inset bullet has Kuwabata at three to seven (the 0.56-0.80
parcel range, measured at seven to three, was dropped, not re-measured); the bank-width bullet carries the finding below.
In 0027's drawing page: the "23 ft crop dikes" sentence of the band bullet is restated from 0018.

## Pop-ups edited (Guesses only)

- `choice/field_archetype--mulberry_dike_fishpond.md` (the six-in-ten and the 23 ft Guesses)
- `choice/land_use_overlay--mulberry_fishpond.md` (six in ten)
- `hamlet/fish-pond.md` (six in ten)
- `hamlet/fruit-dike.md` (23 ft; not named by the arbiter, but the brief's grep finds it)
- `hamlet/mulberry-dike.md` ("three splits" in its first Guess; the brief's grep misses it)

The brief's grep pattern `six in ten` misses the actual text `six parts in ten`; a check should grep `six parts in ten\|23 ft\|three splits`.
Left stale, outside this brief's "Guesses only": `hamlet/mulberry-dike.md`'s Depiction ("each settlement's ponds are drawn at
one of the three") and `field_archetype`'s Depiction ("kept broader than the pond banks"), which is false at the drier splits.

## The bank-width finding

By the manual 0018 cites (fao-ac264e-ch10), a bank that seats a pig sty is one of its 5-10 m (~16-33 ft) dikes, so Kuwabata's
drawn 42 ft bank (three to seven) is wider than the manual's sty dike and the delta account's 6-10 m, under only one village's
undated former 20 m, and the 15 ft bank of the seven-to-three split is a little under the manual's 5 m for a sty-bearing dike;
both are written as findings for the engine to follow (one inset per village, sty or no sty), and 0027 now says the polder's
band (14-40 ft) no longer reads as the greater bank at the drier splits.
