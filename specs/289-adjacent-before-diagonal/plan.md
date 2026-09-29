# Plan - feature 289, adjacent before diagonal

Spec: [`spec.md`](spec.md) (FAITHFUL, round 1). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Decisions

- **D1 - the order** (FR-001). `labels/standard.py` `POSITIONS` becomes: above (0, -1), below (0, +1), left (-1, 0),
  right (+1, 0), then upper right, upper left, lower right, lower left, above slightly right, below slightly left - the
  four adjacent positions the GM named, then today's others in today's order. `_point_cands` already places a centered
  entry (sx 0) squarely above or below its subject. The comment beside `POSITIONS` says it is the GM's deliberate
  deviation from the QGIS / Krygier-Wood order it quotes, and that its match is Mapbox's documented default - not
  Zoraster's (the spec review).
- **D2 - the fallback's sides** (FR-002). `_extended_cands` walks above, below, left, right (today above, below,
  right, left); its slides along each side are unchanged.
- **D3 - the record** (FR-003). The research entry "Where does a caption sit" (`research/presentation/040-*.html`)
  says, in its "Which side" paragraph, that the maps depart from the standard's order by the GM's ruling, what the
  order is, and why; its Evidence comment names the deviation. No new source is cited: the deviation is the GM's
  ruling, and the readers' findings stand in this feature's `research.md`. `make record` reassembles the page.
- **D4 - the maps** (FR-004). The four hand sheets are regenerated (`make map`); the scripted hamlets are regenerated
  to count the captions that move, and take it on every render after. Unit tests that name a position first are
  updated with the order.
- **D5 - verification** (SC-001 to SC-003). A unit test blocks the positions in turn (SC-001); a count over the four
  sheets of notice-board labels at a corner while an adjacent seat at the same ring is free (SC-002, recorded in
  `measurements.json`); `make done`.

## Constitution Check

- XVI: the order is the GM's as stated; everything else unchanged (FR-002).
- XII: the deviation is labeled and recorded where the order is defined, in the record and in the spec.
