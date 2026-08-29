# Research: five things about highlighting

All four decisions here are RENDERING decisions - conventions of the page, with nothing physical
behind them. None of them changes what is on the map, only how the page lights it and what the modal
says. Recorded per constitution XII so that a later session reading the CSS knows these were chosen
rather than defaulted.

## R1 - the planted highlight tone (DEVIATION, recorded)

**Question.** A lit mulberry dike went one flat gold, bank and crowns together, and the GM could
"no longer see the greenery along them".

**Why it happened.** The crowns are tagged with the DIKE's own class - deliberately, since feature
150, because they are the dike's planting and hovering either should light both. The stylesheet then
paints one `--hl` over the whole class, and a shape that is only distinguishable by its color stops
being distinguishable.

**The decision.** A second highlight tone for the planting, `--hl-planted: #8FA31E` with stroke
`#5F6E12` - an olive-green that is unmistakably part of the same lit feature (same value, same
saturation family as the gold) while still reading as leaf. Two alternatives were priced and
declined:

- **Give the crowns their own class** (`mulberry crown`). Rejected: it splits one feature into two in
  the modal, the census and the hover, so hovering the bank would no longer light the crop growing on
  it - the opposite of what the GM asked for.
- **Leave the crowns unhighlighted** (tag them `"-"`). Rejected for the same reason and because
  `all_ink_is_ruled_on` would then stop covering them.

**What it costs.** One more token on the group element, and the rule that a `Planted` group's
highlight color is not the standard one - so a reader comparing two screenshots sees two colors
inside one lit feature. That is the intent; it is recorded here so it is not later "fixed".

**Sources:** none - this is a rendering convention, not a claim about the world. The thing being
made legible (a dike-pond bank carrying mulberry) is researched at
`research/dike-pond-agriculture.md`.

## R2 - the sluice's hit box (RENDERING)

The GM: the sluices are "really hard to click on". Measured: a pond sluice is drawn as a 2.4 px
stroke, against a field ditch's 3.5. `HIT_WIDEN` already solves exactly this for the ditch, with
`(6.0, 9.0, 4.5)` - six times the drawn width, floored at 9 px. Applied unchanged, which is what
"similar to what we are doing with the field ditches" asks for; at 2.4 px the factor gives 14.4 px,
so the floor does not bind and the box scales with the mark as the ditch's does.

## R3 - the sibling pairs (RENDERING)

Two confusable pairs on a dike-pond map, each now cross-linked in both directions:

- **field ditch / pond sluice** - both are thin blue water marks. One is the paddy fabric's plumbing;
  the other is a gate in a dike.
- **crop dike / perimeter dike** - both are called "dike" and both are banks of piled earth. One is a
  field boundary around one pond; the other is the embankment that keeps the river out of the whole
  settlement.

The crop dike is a rolled knob with four values, so the pair is written four times rather than once.
That is one step past the GM's literal words ("the two different dike modals" - the two on the map in
front of them); it is declared in the spec's Assumptions and was put to `spec-fidelity`, because a
sugarcane hamlet would otherwise ship a half-linked pair for no reason a reader could see.

## R4 - name and key are now separate (RENDERING)

`FeatureClass.name` is the modal's heading; `key` is what every drawn element carries and what
`all_ink_is_ruled_on` checks. They were equal for every class until the GM asked that the windbreak
modal "actually say 'Windbreak forest' instead of just 'windbreak'". Only the name moves - moving the
key would rewrite the ink of every windbreak on every map for a heading. The test that asserted
equality now asserts the name CONTAINS the key, which still catches a mismatched or mistyped row.

## R5 - the merge pass was changing the picture (DEFECT, fixed here)

Found while verifying FR-003 with feature 148's page-vs-SVG check: **Kuwabata's page sat 0.255% of
pixels from its own PNG, against the reference hamlet's 0.015%.** Crop of the woodland showed why -
every crown's outline drawn OVER its neighbors, so a dense stand read as a heap of glass rings.

**Mechanism.** One `<path>` paints all of its subpath FILLS and only then its stroke. Two same-styled
outlined circles merged into one path therefore swap what covers what wherever they overlap. Feature
148 guarded the translucent case and missed this one.

**Fix, and what each part measured** (Kuwabata / Inashiro page elements, from 10,052 / 7,508):

| change | elements | page vs SVG |
|---|---|---|
| an outlined shape may not merge with one it overlaps | 14,924 / 11,810 | 0.236% / 0.005% |
| ...one style keeps up to 8 open buckets instead of one *(reverted, see below)* | 14,765 / 11,707 | 0.238% / 0.005% |
| ...a circle's overlap is tested as a CIRCLE, not as its box | 14,411 / 11,653 | 0.239% / 0.005% |
| ...**a line is not an outlined shape** (it has no fill area) | 9,566 / 7,395 | 0.239% / 0.005% |
| ...a member clears everything skipped since the bucket OPENED | 9,726 / 7,511 | 0.236% / 0.005% |

The fourth row is the one that matters for cost: the scatters are one `<line>` per blade with no
`fill` attribute at all, and reading an absent fill as black made every blade outlined - 5,536
unmerged blades on Kuwabata's scrub where 1,200 paths had been. With that right, the ring artifact is
gone and the page carries FEWER elements than before the fix.

**The second row was implemented and then taken out again.** Keeping several buckets open per style
looked like the obvious way to pay for the guard - a refused element threw its bucket away - and on the
map that stresses it hardest it made no difference at all: 9,726 elements with a cap of 8 and 9,726 with
a cap of 1, once the line fix was in. It is recorded here, and named in the code, so the next reader does
not implement it a second time on the same reasoning.

The last row is a soundness hole of feature 148's own: a bucket cleared its skipped extents whenever
a member joined, which proves only that THAT member cleared them, while every later member is emitted
at the FIRST member's position too. Cumulative now; it costs 160 elements.

## R6 - the residual 0.236% is antialiasing, and it is ACCEPTED

**What it is.** Bisected to the smallest prefix that differs: a marsh reed tuft, three opaque blades
of one stroke color sharing a root. Painted as three `<line>`s, the overlapping ends composite three
times; painted as one path, the union is composited once. Same color, so the interiors match exactly
and only the ANTIALIASED edge pixels differ - which is why the whole residual sits in the 9-24/255
delta band, invisible at any zoom, and why the two crops of the same ground are indistinguishable by
eye. With merging disabled entirely the page matches its PNG on every single pixel (0.000%), so this
accounts for all of it.

**What was priced and declined.** Blocking a merge between overlapping same-styled STROKES would
close it. It also un-merges every scatter on the map - the tufts share a root by construction - which
is the whole 5,536-vs-1,200 cost above, paid on every map, to remove a difference no reader can see.
Declined.

**Accepted** (this session, 2026-08-29, reported to the GM): the page may differ from its PNG by
antialiasing at overlapping same-color strokes. Kuwabata 0.236%, Inashiro 0.005%, all of it under
delta 25/255. Recorded so a later session does not read it as a bug and pay the element cost to
"fix" it. If it ever needs revisiting, the lever is one condition in `_refused`.

## R7 - a widened box that loses to another class's box (DEFECT, found by review, fixed here)

`settlement-review` measured what the commit had claimed. FR-001 shipped, and the sluice still did not
win its own box: **42.4% of the widened area, median 40%, worst 10.3%, seven of 52 under 25%** - and
only 47.3% of the sluice's own drawn 2.4 px stroke. The evidence in the commit ("a point in the middle
of the widened copy resolves to `pond sluice`") was true of the midpoint and false of most of the box.

**Mechanism.** A hit copy rode inside its own class group, so document order decided every contest
between two invisible boxes. **49 of the 52 sluices are drawn ON a field ditch** (median centerline
separation 0.03 px - a sluice IS a gate in a watercourse, so this is correct engineering), the ditch's
group comes later, and its 14.4 px box therefore covered the sluice's box AND the sluice's own ink.

**Fix, and the design that was tried first.** `HIT_ON_TOP` lifts a class's boxes out of its group into
one layer above the ink. Lifting EVERY widened class was implemented first and measured wrong: above
the ink, the bund's 12 px box (eight times a 1.4 px mark) stops being buried and blankets the map -
**+5,112 sample points to the bund, -2,802 from the mulberry dike, -1,472 from the vegetable ground,
-914 from the paddy**, so hovering a dike would have answered "bund". An intermediate rule, "the
thinnest drawn mark wins", is the same mistake with arithmetic on top: the bund IS the thinnest, and it
took 59.5% of every sluice box. **Thinness is not smallness, and it is smallness that makes a target
hard.** So only a mark that cannot be hit any other way is lifted, and today that is the pond sluice
alone.

**Measured after** (125,173 sample points, `document.elementFromPoint`, each box scrolled into view):
sluice **88.3%** of its box's bounding RECTANGLE, median 91.7%, worst 72.2%, **none under 25%**.
`settlement-review` replayed it over the widened STROKE REGION instead - the part that is actually
hittable, a rectangle's corners being outside a diagonal line's stroke - and got **96.0%, median 95.8%,
worst 92.6%**. Both definitions reproduce the same 42.3-42.4% before the fix, so they agree about the
mechanism and differ only in what counts as inside the box; the rectangle figure is the pessimistic one
and is the number this feature is held to. Map-wide, every other class is unchanged to the sample except
the ground immediately around the sluices - field ditch -300 points, mulberry dike -128.

**AND THE LIFT BROKE ITS OWN RULE** (settlement-review round 2). "A box may beat empty ground; it may
not beat another feature's drawn ink" - it took **88.4% of one pig sty's own footprint and 42.8% of a
duck pen's**, because that sty's center lies 4.67 px from a lifted line whose half-width is 7.2, so the
box simply contained it. The GM's "really hard to click on" had been moved off the sluice and onto a
farm building. My own map-wide census could not see it: at a 7 px grid the sty is four sample points.
The layer is now clipped (`HIT_KEEP_CLEAR`) against every recorded structure footprint - 75 holes for
this map's 75 records, an even-odd path, since clipping is part of SVG hit-testing where masking is not.
Measured after: every sty and pen back to its main-branch share to the tenth of a point (74.3% for the
flagged one, against 11.6% before the clip), and the sluice keeps 88.3% - the clip costs it 0.3.

**Sources:** none - a page interaction convention, with nothing physical behind it.

## R8 - the GM's own defect was still standing on the perimeter dike (DEFECT, found by review)

R1 fixed the crop dike. `dikes.py` draws the polder embankment's two planted rows - willow on the water
face, mulberry on the inner - inside the same string as the earth mottle, tagged plain. Lit, that was
**36,843 px of drawn crown turned flat gold, and 0 px of `--hl-planted`**, under a modal that says the
bank is "planted with willow and mulberry to bind it". FR-005's new sibling link walks the reader
straight from the fixed dike to the unfixed one.

The planted rows are now their own string under the same clip, tagged `Planted("perimeter dike")`. The
split re-opens the clip group, so the raster is no longer bit-for-bit: **45,564 px of 12,181,000 differ,
44,860 of them by 1, 699 by 2 and five by 3**, every one within 36.6 px of the dike outline -
clip-edge antialiasing, no geometry moved. (An earlier version of this entry said 18,640 and a maximum
of 2; `settlement-review` re-rendered both SVGs with the pipeline's own resvg flags and got the figures
above. The wrong ones are left visible here rather than quietly corrected, because a measurement nobody
can reproduce is worse than one that is openly wrong.) **In Chromium the two pages render pixel-identical
unlit** - 0 differing pixels - so the antialiasing does not reach the interactive target at all. The
manifest changes only in `z` ordinals (one more drawn string shifts every later index by one), and the
two consumers of the shifted fields move together, so relative order holds.

Rejoining the two emitted strings reproduces the original byte for byte (124,431 chars), which is the
proof that this is a split and not an edit.
