# Rust claims to restate after the page sessions (one builder, one landing at the end)

## From P2's cascade (2026-11-24; detail: cascade/p2-cascade.md)
1. rust/phases/src/field/channels.rs::SUPPLY_W#supply canals (DRIFTED): "4.0 -> 1.5 down the brook's flank"; drop the note "(the page's "far edge" is the brook's flank here)"; cite 0068 drawing, the table row "supply canal down the brook's flank".
2. rust/phases/src/field/channels.rs::division#the fork (DRIFTED): "a supply canal along the upper edge and one down the brook's flank"; drop "the page's far-edge canal". Same row.
3. rust/phases/src/field/brook.rs::brook#the tap's stride (DRIFTED): no longer "silent": GUESS on 0059's drawing page, item brook-line-below-intake (about 70 ft below a shoulder intake).
4. rust/phases/src/driver.rs::BROOK_TAP_RUN#the brook's course (MISLABELED): GUESS on 0059's drawing page, item brook-line-below-intake; the slew, skirt, wander and station constants that say "as BROOK_TAP_RUN's" need their own account.
5. rust/phases/src/field/brook.rs::brook#outside the crop (CANNOT-TELL, held by T218, unrecorded): make it agree with the stride ("never in for the tap's stride; out at once where the skirt's line passes it"); it could cite 0059's item.
6. Stale comment in brook.rs: "ran 110-160 ft straight against 0054's ten widths" predates the 70 ft hold.
PAGE follow-up (for a later brief): 0059's new sentence looks untrue for a STRAIGHT-sited shoulder intake (the intake stands 14-22 ft outside the corner, inside the 34 ft skirt line, so the brook steps out at once; holds for a bend-sited intake) - arithmetic from constants, not measured on a map. Pop-ups hamlet/stream and choice/intake_place--shoulder do not state the 70 ft guess (451 T226).

## From P1's cascade and T420 (already restated by T420's builder; listed for completeness): none owed.

## Page follow-ups from P3 (2026-11-24; for a later brief)
- registry entry ishiguro-azemame-tool: its `What it is:` names the village's place (Takayanagi, Kashiwazaki, Niigata) from the check's own web search; the cited page names only 石黒 and the Niigata page is not on the sources-consulted ledger: source it or drop the place.
- 0284's comb-bund-bow block (and the older polder block) says no page read gives how far a bund bowed and links 0014's research page, which says "a straight hundred-foot bund bows by a foot or two", unfootnoted (0014 has 12 bytes of room).

## From P3's cascade (2026-11-24/25; detail and verdict texts: cascade/p3-cascade.md)
CODE FIRST (449 T429): staged.rs::rice_pond / polder_stage#a rice polder's pocket pond gives no pond when no remaining host is low.
1. lattice.rs::BOW#the bund's bow (DRIFTED): cite 0284 drawing `comb-bund-bow` for the 15% GUESS.
2. lattice.rs::Lines.new#the bund's bow (DRIFTED): same item, for the per-row bow.
3. beans.rs::BEAD_STEP_FT#the beads' spacing (MISLABELED, held unrecorded): CONVENTION, `bean-spacing-8-ft`; drop "silent".
4. beans.rs::BUND_SHARE#which bunds (DRIFTED): GUESS, `beans-three-bunds-in-eight`.
5. beans.rs::bean_runs#a run's most and its spacing (DRIFTED, held): four at most a GUESS (`bean-run-at-most-four`); spacing a CONVENTION.
6. beans.rs::bean_runs#how many (DRIFTED, held): GUESS, `beans-three-bunds-in-eight`.
7. beans.rs::settle#a drowned bead alone (DRIFTED, held): GUESS, `drowned-bead-dropped`.
8-10. beans.rs::bean_runs#no bead in the water, beans.rs::settle#no bead in the water, driver.rs::settled#no bead in the water (MISLABELED): GUESS, `drowned-bead-dropped`, not a finding.
11. staged.rs::rice_pond#a four-sided host (DRIFTED, held): GUESS, 0008 drawing `pond-host-four-sided`.
12. staged.rs::rice_pond#never a resting plot (DRIFTED): GUESS, `pond-never-resting-plot`.
13-14. driver.rs::draw_field#the pocket pond's ring, driver/polder.rs::draw_polder#the pocket pond's ring (DRIFTED, held): GUESS, `pond-bank-and-margin-width`; drop "no page sizes the margin"; word as drawn (the bank line centered at r + 2.5).
PAGE follow-ups: 0008's `pond-bank-and-margin-width` says the wet ground is 2.5 ft wide; the bank stroke overlaps the fill so about 1 ft shows (found.jsonl); the Ishiguro 30 cm finding belongs on 0014's RESEARCH page (then hamlet/bund-beans' About may carry it); hamlet/field-pond's Guesses tab states none of the three pond guesses.

## From P3b's cascade (2026-11-25; cascade/p3b-cascade.md)
20. rust/phases/src/field/lattice.rs::cuts_counted#a half-row between counts (line 88, DRIFTED): GUESS on 0005's drawing page, item `half-row-between-counts` (the count nearest the band's middle, the same count on both halves of a row, the drain at its middle, each basin's length rolled from the row's own stream).
POP-UP (a LINKS fix, re-owes nothing): hamlet/paddy's `Drawing:` line gains research/questions/0346-how-our-maps-draw-the-rice-inside-a-paddy.drawing.html (the rice shoots' drawing rules moved there by P3b's split).

## From P4's cascade (2026-11-25; cascade/p4-cascade.md)
21. field/dry.rs::refused#off the water (held): cite `dry-plot-off-water`, drop "silent".
22. hem.rs::CLEAR_FT#off the water: cite `dry-plot-off-water`, drop "silent".
23. driver/check.rs::check#no dry plot on the water: cite `dry-plot-off-water` beside the dry-side block (the check also covers the brook and the drain's run).
24. field/build.rs::hem_bounds#the toe's band whatever the grain asks: cite `barley-hamlet-toe-band`; the one band is the page's GUESS.
25. field/states.rs::states#a resting plot from the green (held): cite `resting-plot-one-state`, drop "silent".
26. field/dike.rs::CROWN_FT#the crowns (held): the values are radii (draw_polder draws a circle of radius r); willow 7-11 ft across, mulberry 4.4-7.2 against the page's 7; cite `willow-crown-size` and 0018's mulberry crown.
27. field/dike.rs::GAP_HALF_FT#the gap (held): cite `rows-gap-at-channel`, call 5.5 ft a radius. ON PAPER the largest crown at 15 ft reaches 9.5 ft and can overlap a sluice post (outer face 10 ft from the middle line) by up to 0.5 ft: measure with 449 T427.
PAGE follow-up: 0011's "from the canal's start" means the toe end in the code's frame, the opposite of where the water enters; reword both the page and the claim to "laid from the toe end of the canal, up along it, until the need is met".

## From P10's cascade (2026-11-25; cascade/p10-cascade.md)
FOR T427'S BUILDER (the code changes): field/polder.rs::ditches#the ring canal on a dike-pond block (cite 0019 drawing `ring-canal-width-dike-pond`, every trunk at least the creek width, drop "no width of its own"); field/polder.rs::ditches#the widths (the ladder's trunk widths for a rice polder only; cite `ring-canal-width-dike-pond` for the dike-pond form). Check RING_FT (the ring 6 to 12 ft in) still fits an 8 ft ring canal.
WORDING ONLY:
28. field/polder.rs::ditches#a creek's mouth on the ring canal: cite 0019 drawing `creek-mouth-on-ring-canal`, drop "silent"; keep the half-width stop and the measured ends.
29. field/polder/creeks.rs::EASE_STEPS#the easing's steps: cite 0019 drawing `pinched-mosaic-eased`; drop "no rule for a block it pinches".
30. creeks.rs::eased#room for the creeks: add `pinched-mosaic-eased` as the easing's GUESS; keep the 0018 citation for 6 to 8 ft.
31. creeks.rs::creek_width#one width a block: cite 0018 drawing `one-creek-width-a-block`; drop the silent-page argument.
32. polder.rs::ditches#the creeks' width: add `one-creek-width-a-block` (unjudged read).
33. polder.rs::row_ditches#the row ditch's width: add `one-creek-width-a-block` (unjudged read).
POP-UPS (no check sent them on): hamlet/pond-canal's Guesses tab states neither the creek width nor the ring canal's bound, and keeps "not every dike-pond hamlet need have had water a boat could travel"; hamlet/fish-pond's flat "lay in a mosaic"; hamlet/sluice-gate's "upstream head ... downstream tail" as fact (all three already on 449 T425's line).

## From P11's cascade (2026-11-25; cascade/p11-cascade.md)
34. seat.rs::open_at_an_end#a seat astride the brook leaves by its open bank: cite 0081 `way-out-from-band-ends` (GUESS), 0031 `seat-astride-brook-windward-corner`, 0057 `toe-on-tapering-flank`, 0035 for both banks; drop "the record does not say where a cluster's way out starts".
35. seat.rs::BAND_EXITS#the way out from the band's ends: cite 0081 `way-out-from-band-ends`; drop "silent".
36. driver/toe.rs::toe_band#toe band edge: add the tapering-flank DEVIATION, 0057 `toe-on-tapering-flank` (and see 449 T432, which may change the code).
37. seat.rs::seat#a walled-in head gives way: a GUESS citing 0081 `way-out-from-band-ends`.
38. seat/exit.rs::Exit.has_exit#dry way out of the seat: drop "a walled-in head is refused"; a site walled in at its middle is passed over (`way-out-from-band-ends`).
plus the 3 claims-label lines P11's cascade names, and its two optional citations (cascade/p11-cascade.md).
POP-UPS (451 T226, T234): choice/cluster_position--high_margin does not state the corner astride the brook; hamlet/marsh does not state the wet ground carried up a tapering flank (the more visible omission); choice/settlement_form--dispersed states the moved rule but its Drawing: line names 0031, not 0349.

## From P12's cascade (2026-11-25; cascade/p12-cascade.md)
FOR T432: toe.rs::toe_band#toe band edge (state what T432 draws); toe.rs::toe_band#toe band width (driver.rs:422 passes only f.fan.ring, the paddy fan: fix the code or say "the paddy fan's"); margins.rs::ranked#not on the wet toe ("below the fields" wrong while the flank is drawn; cite 0057 drawing with 0058); seat.rs::open_at_an_end and margins.rs::SQUARE_EPS rest on the wet windward flank: re-measure after T432; hamlet/marsh's new sentence describes the flank: re-check if the flank goes.
WORDING: dry.rs::PINCH_SHARE#the pinch and pinched#the pinch cite 0006 `dry-plot-taper-at-bend`; dry.rs::hem#a column's climb ends cites it with 0011; dry.rs::hem#the last band from the canal's start: the GUESS on 0011 drawing, "from the toe end of the canal, up along it"; seat.rs::open_at_an_end cites 0031 and 0081 drawing; margins.rs::SQUARE_EPS relabeled GUESS on 0031 drawing.
POP-UPS: barley, buckwheat, soy share millet's sentence but did not get its taper EDIT; `dry-plot-taper-at-bend` reaches no Guesses tab.
