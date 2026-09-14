# Research - 247 two beads per bund

## R1. Where a single bead comes from, and how many there are

**The mechanism.** `waterfields/carve.py` `_bund_beans` picks, for each plot that rolls beans, one or two
edges of its ring and lays a bead every `spacing` along each (the constant in `_bund_beans`' signature,
read 2026-09-14), leaving the corners empty: an edge of length L carries `int(L / spacing) - 1` beads, so
an edge between two and three spacings long carries exactly ONE and a shorter one none. A second route
to a single bead is the drops: a bead buried by a later-painted plot, or under a ditch's, a channel's or
a pond's water, is removed one bead at a time (`_bund_beans` for the plot and ditch cases,
`settlement/fields/comb.py` `_comb_drop_drowned_beads` for the pond and the recorded ditches), so a run
can be left with one bead - and a dropped MIDDLE bead leaves two beads at the ends of an edge with a
painted-over stretch between them, which the eye reads as two segments of one glyph each.

**The count** (observed 2026-09-14; method: a scratch script over the shipped hamlet manifests, in
which two recorded beads belong to one run when they lie within one and a half bead spacings of each
other and both sit within three quarters of a pixel of one recorded plot-ring edge - so a run on a
shared bund is one run whichever plot's ring it is measured against, two runs meeting at a corner are
two, and a dropped bead's gap splits a run). The runs of one bead, with the runs of two beside them
because the drop-whole rule of spec D4 will turn some of those into none:

| map | beads | runs | runs of one bead | runs of two |
|---|---|---|---|---|
| Inashiro | 656 | 240 | 37 | 90 |
| Kashikawa | 815 | 283 | 35 | 112 |
| Mizuguchi | 425 | 151 | 25 | 48 |
| Sawada | 739 | 270 | 35 | 107 |

Kuwabata records no bead-bearing field. About one run in seven is a single bead on every map, which is
the thing the GM saw. (A first count that assigned each bead to its single NEAREST edge gave higher
figures - fifty on Inashiro - because a run on a bund two rings share was split between the two rings'
coincident edges; the spec-fidelity reviewer reproduced that count and the method above replaces it.)

## R2. The rule chosen, and the forms it could have taken

A beaded segment must show at least two beads, where a segment is what the eye sees: a contiguous line
of beads on one bund. Three forms were priced:

- **A short edge carries two beads at its thirds.** An edge between two and three spacings long, which
  today carries one bead at its middle, carries two at its thirds; an edge under two spacings carries
  none, as today; an edge of three or more is laid at the spacing, as today. Every bund that shows beans
  today still shows beans; the two beads on the shortest such edge stand about two thirds of a spacing
  apart, well clear of each other at the bead's drawn radius.
- **A short edge carries no beans.** Only an edge with room for two beads at the spacing is laid at all.
  One constant spacing everywhere, but every bund whose chosen edge is short loses the beans it shows
  today - a visible drop in how many bunds carry beans, which the GM did not ask for.
- **A short edge is passed over and a longer edge of the same plot chosen instead.** Keeps the bead count
  up, but puts beans on bunds that carry none today, which the GM did not ask for either.

The first is taken (spec D1). For the drops, the rule is the same in every form: a run that a drop
leaves with a single bead - or splits into parts of which one is a single bead - loses that bead, because
nothing can be added where the drop was (the ground there is painted over or under water).

This is a rendering convention with nothing physical behind it (the GM's own words in `request.md`), so
there is no research pass to run and no source to read; the record's convention paragraph and the
modal's note say the new thing (FR-004), and neither states a finding.

## R3. The random stream is not touched

The bead count per edge and the drop rule are computed after `R.shuffle(order)` and the `R.randint(1, 2)`
that follow it, which draw exactly as before, so every draw `_bund_beans` makes is the same draw on the
same call; the drops run after all draws, as they already did. What moves on a map is the beads and
nothing else (GM 2026-09-08: a map may move for a draw change anyway; here it does not need to).
