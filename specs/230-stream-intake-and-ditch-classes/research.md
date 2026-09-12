# Feature 230 - research

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md).

## R1 The state of the record before the pass (2026-09-12)

What the engine draws at the head of a comb field today, read from the code and from Inashiro's manifest:

| piece | where | what it is |
|---|---|---|
| the intake point | `hamletgen/water.py` `head_sluice` | 36% of the canvas up the fall from the center, plus a rolled lateral offset (`HEAD_OFFSETS`) |
| the brook | `hamletgen/water.py` `feed_brook` | a fixed 420 px run ending AT the intake, one 26 px bow, bearing swung off the fall only to clear the crop; recorded as a `streams` record with no `to` |
| the head race | `waterfields/comb.py` `_comb_skeleton` | a hardcoded 90 px straight continuation down the fall from the intake to the fork (the bunsuiguchi); `role: main` |
| the drawn join | Inashiro's PNG | the 7 px stream meets the ~5 px head race at a rounded cap, 90 ft above the fork, on one straight line - no weir, gate or bend |

Neither constant carries a comment or a research entry. `settlements/water.md` line 12 (the Ikegami rule) says the brook
"reaches the sluice, and there BECOMES the irrigation channel - it hands off to the comb and stops", a rule that came
from the GM's catch of two overlapping water lines on the first Ikegami draft, not from research. `research/water.html`
"Drawn width is RANK" mentions "ponding above the weir" in passing as the physical reading of the width step, and
`research/fields.html` "The communal-system floor" lists "weir, head-race, canal fork" as the communal works, with no
footnote on the weir. No section of the record asks where a stream becomes a ditch.

At the foot: the collector (`role: drain`) ends at its outfall; with `water_sink="pond"` the run to the tameike is drawn
by `field_channel` at the drain's width and recorded as a `channels` record `frm: drain -> to: pond` (class `field
ditch`); with `water_sink="offmap"` the run is drawn by `stream` at 8 px and recorded in `streams` `frm: drain -> to:
offmap` (class `stream`). Inashiro and Mizuguchi drain to a pond; Sawada and Kashikawa off the frame; Kuwabata is a
pond-fed polder.

The class: one `FieldDitch` class covers `field_ditches` and `channels` alike, its explanation written about supply
(the comb layout, the taper, sparseness). Every `field_ditches` record carries `role` (`main`, `branch`, `drain`; a
polder adds `lateral`, and `seg` names its ring segments), and the drain is painted `#7C9EB0` against the supply net's
`#6C9CBE` at the one emit loop in `fields/comb.py`.

## R2 The pass

Pending - the readers were dispatched 2026-09-12 (Japan-first and China-first, one attempt per host).

## R3 The maps before and after

Pending.
