# Research - 247 two beads per bund

## R1. Where a single bead comes from, and how many there are

**The mechanism.** `waterfields/carve.py` `_bund_beans` picks, for each plot that rolls beans, one or two
edges of its ring and lays a bead every `spacing` along each (the constant in `_bund_beans`' signature, read 2026-09-14), leaving the corners empty: an edge
of length L carries `int(L / spacing) - 1` beads, so an edge between two and three spacings long carries
exactly ONE and a shorter one none. A second route to a single bead is the drops: a bead buried by a
later-painted plot, or under a ditch's, a channel's or a pond's water, is removed one bead at a time
(`_bund_beans` for the plot and ditch cases, `settlement/fields/comb.py` `_comb_drop_drowned_beads` for
the pond and the recorded ditches), so a run of two or three can be left with one.

**The count** (observed 2026-09-14; method: a scratch script over the shipped hamlet manifests, each bead
assigned to the nearest edge of the nearest recorded plot ring and the beads grouped by edge; a group is
a run). The share of runs holding one bead:

| map | beads | runs | runs of one bead |
|---|---|---|---|
| Inashiro | 656 | 250 | 50 |
| Kashikawa | 815 | 299 | 56 |
| Mizuguchi | 425 | 163 | 37 |
| Sawada | 739 | 298 | 62 |

Kuwabata records no bead-bearing field. About one run in five is a single bead on every map, which is
the thing the GM saw.

## R2. The rule chosen, and the two ways it could have been met

A beaded segment must show at least two beads. Two forms would satisfy that:

- **Lay two on every chosen edge**, however short - place them at thirds of a short edge. On a filler
  sliver a few pixels long the two beads would touch or overlap, which reads as one blob; and the
  spacing would then vary by edge, where today it is one constant.
- **Let only an edge long enough for two beads at the spacing be a candidate**, and drop a run whole
  when the drops leave it below two. The spacing stays one constant; a short edge simply carries no
  beans, and the plot's beans go on a longer edge instead.

The second is taken (spec D1). It is a rendering convention with nothing physical behind it (the GM's
own words in `request.md`), so there is no research pass to run and no source to read; the record's
convention paragraph and the modal's note say the new thing (FR-004), and neither states a finding.

## R3. The random stream is not touched

The candidate filter is applied AFTER `R.shuffle(order)` and the `R.randint(1, 2)` that follow it draw
exactly as before, so every draw `_bund_beans` makes is the same draw on the same call; the drops run
after all draws, as they already did. What moves on a map is the beads and nothing else (GM 2026-09-08:
a map may move for a draw change anyway; here it does not need to).
