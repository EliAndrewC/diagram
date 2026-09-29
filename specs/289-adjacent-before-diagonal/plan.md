# Plan - feature 289, adjacent before diagonal

Spec: [`spec.md`](spec.md) (FAITHFUL, round 1). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Decisions

- **D1 - the order** (FR-001). `labels/standard.py` `POSITIONS` becomes: above (0, -1), below (0, +1), left (-1, 0),
  right (+1, 0), then upper right, upper left, lower right, lower left, above slightly right, below slightly left - the
  four adjacent positions the GM named, then today's others in today's order. `_point_cands` already places a centered
  entry (sx 0) squarely above or below its subject. The comment beside `POSITIONS` says it is the GM's deliberate
  deviation from the QGIS / Krygier-Wood order it quotes, and that its match is a Mapbox documentation example's order - not
  Zoraster's (the spec review).
- **D2 - the fallback's sides** (FR-002). `_extended_cands` walks above, below, left, right (today above, below,
  right, left); its slides along each side are unchanged.
- **D3 - the record** (FR-003). The research entry "Where does a caption sit" (`research/presentation/040-*.html`),
  in its "Which side" paragraph: the maps' order and that its first step is a deliberate deviation by the GM's ruling
  (a grounds note, this project's decision); the textbooks' order and why it starts at the corners (its existing
  citations); that no source treats a small drawn object on a plan as its own case (an absence note, with what was
  searched); and the other published orders, cited - a German reference dictionary, the place to the right of a point as ideal
  (`spektrum-schriftplatzierung`, translated from the German); Zoraster's oil-well schemes, above ranked high, and the
  2024 user study - readers prefer directly above, its order top, bottom, right, then corners
  (`bobak-cmolik-cadik-2024`, the arXiv full text); a Mapbox documentation example ordering top, bottom, left, right
  (`mapbox-variable-label-placement`). Imhof's own text is paywalled and is cited only through these. Three new
  registry entries; `make record`. Checked by `quote-check`, `record-format` and `source-applicability` from their
  bundles. T02 stays `research: rendering`: it records a drawing convention and its sources, not how a place was
  built; its citations still go through the three checks.
- **D4 - the maps** (FR-004). The four hand sheets are regenerated (`make map`); the scripted hamlets are regenerated
  to count the captions that move, and take it on every render after. Unit tests that name a position first are
  updated with the order.
- **D5 - verification** (SC-001 to SC-003). A unit test blocks the positions in turn (SC-001); a count over the four
  sheets of notice-board labels at a corner while an adjacent seat at the same ring is free (SC-002, recorded in
  `measurements.json`); `make done`.

## Constitution Check

- XVI: the order is the GM's as stated; everything else unchanged (FR-002).
- XII: the deviation is labeled and recorded where the order is defined, in the record and in the spec.
