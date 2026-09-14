# Feature 247 - two beads per bund

**Status**: FAITHFUL (`spec-fidelity`, round 2 of 5, 2026-09-14); FR-005 then widened to every shipped hamlet on the round-2 aside, awaiting its verify round.
**Request**: [`request.md`](request.md) - the GM's words verbatim.
**Research**: [`research.md`](research.md) - where a single bead comes from, the count on the shipped maps, the forms the rule could take.
**Predecessors**: the bead line (GM 2026-08-15, water-honest beads), 230 (the ditches recorded before the field), 245 (lit beads at low zoom).

## Summary

The GM: on any segment of earthen bund that carries bund beans, at least two bead glyphs; some segments
show only one. This is a change to the glyph rendering convention only - the beans are too small to be
visible at map scale, the beads are how we represent them - and it changes nothing about what the map
depicts, nothing in the research, and no source. Today a bead run is laid along one or two edges of a
plot at one fixed spacing with the corners left empty, so an edge between two and three spacings long
yields exactly one bead; and the drops (a bead buried by a later plot, or under ditch, channel or pond
water) remove beads one at a time, so a run can be left with one bead, or with a painted-over gap in
its middle that leaves one bead on each side (research R1). The rule: a segment - a contiguous line of
beads on one bund - shows two beads or none. A short edge that carried one bead carries two at its
thirds; a run that any drop leaves with a single bead, on either side of the gap the drop opened, loses
that bead. The random stream is untouched (R3); the manifest's shape is unchanged and the gate judges
the rule from what it already records.

## Functional requirements

- **FR-001 Every beaded bund segment carries at least two beads.** A segment is a CONTIGUOUS run of
  drawn beads on one bund line: the beads laid along one edge of one plot ring, split wherever a drop
  removed a bead between two survivors. Every segment drawn and recorded holds two or more beads. This
  holds after every drop the engine applies - the plot-burial and ditch-net drops in `_bund_beans`, and
  the pond and recorded-ditch drops at the draw site: a part left with a single bead is dropped, not
  left as one glyph.
- **FR-002 A short edge carries two beads at its thirds.** An edge between two and three bead spacings
  long, which today yields one bead at its middle, yields two beads at its thirds. An edge under two
  spacings yields none, exactly as today; an edge of three spacings or more is laid at the spacing with
  the corners empty, exactly as today. Which edges a plot beads, how many, and the share of plots that
  roll beans (the `bean_frac` knob) are unchanged - no bund gains beans and none loses them for being
  short.
- **FR-003 The random stream is unchanged.** Every draw `_bund_beans` makes is the same draw as before
  on the same call: the bead count per edge and the drop rule are computed after the shuffle and the
  edge-count draw, and the drops run after all draws, as today. Nothing on a map moves but the beads.
- **FR-004 The record says the convention, and states no finding.** The research page's paragraph that
  states the bead convention for the reader (`research/fields.html`, "What a bund bean actually looks
  like") and the bund-beans modal's Note say that a beaded segment is drawn with at least two beads and
  why (one bead does not read as a run). Neither adds a finding, a source or a citation, and the
  research section's findings are untouched; the modal's prose is rewritten in the same delta, so no
  entry-drift pair is left open.
- **FR-005 The manifest is unchanged in shape, and the gate holds the rule from it.** The field record
  keeps its `bund_beans` list and its `plot_rings` exactly as today and gains no field. A gate test over
  every shipped hamlet manifest, each read through the gate's own pool reader (so a cold cache rolls a
  map once, for the sweep and this test alike, and a warm one rolls nothing), derives the segments
  from those two records - two beads in one segment when they lie within one and a half spacings of each
  other and both sit on one recorded ring edge, the method of R1 - and asserts every segment holds two
  or more. Unit tests cover: the thirds rule on a short edge and the unchanged laying on a long one; the
  drop rule under a plot burial and under the ditch net, including a middle drop that splits a run; the
  drop rule at the draw site under pond water; and that the random state after `_bund_beans` is the
  same as before the change on the same input.
- **FR-006 The point of change says why.** `_bund_beans` and the draw-site drop carry the rule and the
  GM's reason at the point of change, with the forms priced (R2) and the stream argument (R3).

## Success criteria

- **SC-001** (FR-001, FR-005): the gate test passes on every shipped hamlet manifest, and the R1 script
  counts zero single-bead runs on each of them after regeneration.
- **SC-002** (FR-002, FR-003): the unit tests pass, including the one that compares the random state
  after the call with the previous code's on the same input.
- **SC-003** (FR-004): the research paragraph and the modal Note say the new thing; `make page-check`
  reports no open entry-drift pair; `make glossary CHECK=1` and `make citations CHECK=1` report nothing
  stale.
- **SC-004** (FR-006): the comments exist at both points of change.
- **SC-005** (spec-wide): `make map` on the reference hamlet then `make maps` over the pool, both green;
  `make verify` green with the settlement-review dispatched beside it, since every bead-bearing hamlet
  manifest moves; lands GATED.

## Decisions recorded

- **D1 - a short edge carries two beads at its thirds; the other two forms are declined.** Three forms
  meet the request (R2). Taken: an edge of two to three spacings, which carries one bead today, carries
  two at its thirds, so every bund that shows beans today still does and the spacing is bent only on
  those edges (the two beads on the shortest such edge stand about two thirds of a spacing apart, clear
  of each other). Declined: laying nothing on a short edge - one constant spacing, but a visible loss of
  beaned bunds the GM did not ask for; and passing over a short edge for a longer one of the same plot -
  beans on bunds that carry none today, which was not asked for either. This is a choice between
  renderings of a convention, not between two supportable readings of a record, so it is not a knob.
- **D2 - the segment is the contiguous run, not the edge** (round 1, finding 1). A dropped middle bead
  leaves one bead on each side of a painted-over stretch - two segments of one glyph each, which the GM
  would still see. So the drop rule splits a run at the gap and judges each part; the gate test derives
  the same unit.
- **D3 - no new manifest field** (round 1, finding 3). The field record already carries the plot rings
  in draw order beside the bead list, and the segments derive from the two; a run structure inside the
  engine's net (never recorded) carries the grouping from `_bund_beans` to the draw-site drop, where the
  same split-and-judge runs and the list is flattened for the draw and the record.
- **D4 - a drop that leaves a single bead removes it rather than re-laying the run.** Nothing can be
  added where the drop was - that ground is painted over or under water - so the single bead goes. This
  is the one place the change removes beads that show today (R1's runs of one, and the runs of two that
  a drop had already thinned), and it is what the request asks.
- **D5 - no research pass.** The GM states the change is a rendering convention with no bearing on the
  reality depicted or on the research; the tasks are `research: rendering`.

## Out of scope

- The bead's color, size, opacity, the spacing on an edge of three spacings or more, or the share of
  plots that roll beans.
- Two adjacent plots each laying a run on the bund they share (existing behavior; adds beads, never
  leaves one).
- The terrace, ribbon and polder engines, which lay no beads.

## Review history

- **Round 1 (2026-09-14, MODE 2): NOT FAITHFUL, three changes, all taken.** (1) A run defined as an
  edge could keep two beads either side of a dropped middle one - two single glyphs; the unit is now the
  contiguous run (FR-001, D2). (2) Re-choosing a longer edge for a plot whose short edge was drawn put
  beans on bunds that carry none; dropped, and the short-edge form changed with it so that no bund loses
  its beans either (FR-002, D1). (3) A new manifest field was unpriced against deriving the runs from the
  rings already recorded; no field is added and the gate derives (FR-005, D3). R1 re-counted by the
  contiguous-run method after the reviewer showed the nearest-edge count split runs on shared bunds.
- **Round 2 (2026-09-14, MODE 3): FAITHFUL.** All three items resolved; the thirds form judged inside
  the request (the floor is met by adding a glyph, and nothing the GM sees is removed but the
  singletons). One aside taken after the verdict: the gate test runs over every shipped hamlet manifest
  rather than the reference alone, since a manifest read through the pool reader costs no roll (FR-005,
  SC-001). The other aside - a glance at the shortest beaded edge on the reference map - is T05's.
