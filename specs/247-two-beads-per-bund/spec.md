# Feature 247 - two beads per bund

**Status**: DRAFT - awaiting the spec-fidelity review.
**Request**: [`request.md`](request.md) - the GM's words verbatim.
**Research**: [`research.md`](research.md) - where a single bead comes from, the count on the shipped maps, the two forms the rule could take.
**Predecessors**: the bead line (GM 2026-08-15, water-honest beads), 230 (the ditches recorded before the field), 245 (lit beads at low zoom).

## Summary

The GM: on any segment of earthen bund that carries bund beans, at least two bead glyphs; some segments
show only one. This is a change to the glyph rendering convention only - the beans are too small to be
visible at map scale, the beads are how we represent them - and it changes nothing about what the map
depicts, nothing in the research, and no source. Today a bead run is laid along one or two edges of a
plot at one fixed spacing, an edge between two and three spacings long yields exactly one bead, and the
drops (a bead buried by a later plot, or under ditch, channel or pond water) remove beads one at a time,
so a run of two can be left with one (research R1). The rule: a run is laid only on an edge long enough
for two beads at the spacing, and a run that any drop leaves below two beads is dropped whole. The
random stream is untouched (R3); the manifest records the runs so the gate can hold the rule.

## Functional requirements

- **FR-001 Every beaded bund segment carries at least two beads.** A bead run - the beads laid along one
  edge of one plot ring - that is drawn and recorded holds two or more beads. This holds after every drop
  the engine applies: the plot-burial and ditch-net drops in `_bund_beans`, and the pond and recorded-ditch
  drops at the draw site. A run reduced below two by any of them is dropped whole, not left as one bead.
- **FR-002 Only an edge long enough for two beads is a candidate.** An edge yields beads only when its
  length at the bead spacing leaves room for two beads with the corners empty, as the line is laid today.
  A plot's one or two beaded edges are chosen from its candidate edges, so a plot with a short edge
  among longer ones is not left beanless because a short edge was drawn. The bead spacing is unchanged.
  The share of plots that roll beans (the `bean_frac` knob) is unchanged.
- **FR-003 The random stream is unchanged.** Every draw `_bund_beans` makes is the same draw as before
  on the same call: the candidate filter runs after the shuffle and the edge count draw, and the drops run
  after all draws, as today. Nothing on a map moves but the beads.
- **FR-004 The record says the convention, and states no finding.** The research page's paragraph that
  states the bead convention for the reader (`research/fields.html`, "What a bund bean actually looks
  like") and the bund-beans modal's Note say that a beaded segment is drawn with at least two beads and
  why (one bead does not read as a run). Neither adds a finding, a source or a citation, and the
  research section's findings are untouched; the modal's prose is rewritten in the same delta, so no
  entry-drift pair is left open.
- **FR-005 The manifest records the runs, and the gate holds the rule.** The field record keeps its flat
  `bund_beans` list unchanged in shape, and beside it records the run structure as the length of each
  run in list order (the flat list being the runs concatenated). A gate test over every shipped manifest
  asserts that every recorded run holds at least two beads and that the run lengths sum to the bead
  count. Unit tests cover: the short-edge candidate rule, the drop-whole rule under a plot burial and
  under the ditch net, and the drop-whole rule at the draw site under pond water.
- **FR-006 The point of change says why.** `_bund_beans` and the draw-site drop carry the rule and the
  GM's reason at the point of change, with the two forms priced (R2) and the stream argument (R3).

## Success criteria

- **SC-001** (FR-001, FR-005): the gate test passes over every shipped manifest - no recorded run holds
  fewer than two beads, and the lengths sum to the bead count - and the same script that counted the
  single-bead runs in R1 counts none on the regenerated maps.
- **SC-002** (FR-002, FR-003): the unit tests pass; on a seeded roll of the same plots, the set of
  edges chosen and the number of edges chosen per plot are those the previous code chose whenever the
  chosen edges are all candidates, and the random state after the call is the same as before the change.
- **SC-003** (FR-004): the research paragraph and the modal Note say the new thing; `make page-check`
  reports no open entry-drift pair; `make glossary` and `make citations` report nothing stale.
- **SC-004** (FR-006): the comments exist at both points of change.
- **SC-005** (spec-wide): `make map` on the reference hamlet then `make maps` over the pool, both green;
  `make verify` green with the settlement-review dispatched beside it, since every hamlet manifest moves;
  lands GATED.

## Decisions recorded

- **D1 - a short edge carries no beans rather than two crowded beads.** Two forms meet the request (R2):
  place two beads on every chosen edge however short, or let only an edge with room for two at the
  spacing be a candidate and drop a run whole when it falls below two. The second is taken: the spacing
  stays one constant, two beads on a sliver would touch and read as one blob, and the plot's beans go on
  a longer edge instead. This is a choice between two renderings of a convention, not between two
  supportable readings of a record, so it is not a knob.
- **D2 - the candidate filter runs after the shuffle, not before.** Filtering the edge list before
  `R.shuffle` would change how many random numbers the shuffle draws and ripple every later draw; after
  it, every draw is unchanged (R3, FR-003). A moved map was allowed (GM 2026-09-08) but is not needed.
- **D3 - the run structure is recorded as lengths, not as a second list of points.** The flat bead list
  stays exactly as every consumer reads it (the gate's water-honesty test, the page's hit regions); a
  list of run lengths beside it carries the grouping at a few bytes per run, where a list of lists of
  points would double the bead record.
- **D4 - a run is dropped whole at the draw site too.** The pond and recorded-ditch drops live in
  `settlement/fields/comb.py`, after `_bund_beans` returned; they operate on the runs and re-flatten, so
  the rule holds on the finished map and the manifest, not only on the function's own output.
- **D5 - no research pass.** The GM states the change is a rendering convention with no bearing on the
  reality depicted or on the research; the tasks are `research: rendering`.

## Out of scope

- The bead's color, size, opacity, the spacing, or the share of plots that roll beans.
- Two adjacent plots each laying a run on the bund they share (existing behavior; adds beads, never
  leaves one).
- The terrace, ribbon and polder engines, which lay no beads.

## Review history

- (none yet)
