# Plan - 230 the stream's intake, and the two ditch classes

Spec: [`spec.md`](spec.md). Research: [`research.md`](research.md). DRAFT until the spec is FAITHFUL; the FR-004
half is filled in when the pass (research R2) lands.

## Constitution check

- **XII (research before a physical decision)**: FR-003 runs first; nothing at the head moves until R2 is
  written, its sources judged (`source-applicability`) and its entry checked (`quote-check`, `record-format`).
  Two attested forms become a knob (FR-004 c). A silent record is a labeled guess and a question for the GM (d).
- **VI (reference then pool; review before a map ships)**: FR-005. The gate is `make verify` (gate + the
  settlement-review dispatched in the same turn) over the pool, once, at the end; `make quick` while iterating.
- **X (100% coverage; files under 1,000 lines; an overlap check in its efficient form)**: the new class code is
  docstrings and one-line role reads; the brook's routing, if it changes, reuses `feed_brook`'s crop test
  against the envelope (a handful of segments per candidate, no scan).
- **XIV (fix defects where found)**: the review's out-of-delta findings are fixed in this work.
- **XVI (do the literal thing)**: the spec is reviewed by `spec-fidelity` against `request.md` before T02 starts.

## The class split (FR-001, FR-002) - engine and page

1. **The vocabulary.** `interactive/classes/water_and_ways.py`: `FieldDitch` becomes `IrrigationDitch`
   (`key = "irrigation ditch"`) and a new `DrainageDitch` (`key = "drainage ditch"`) after it, each with its own
   `What:`/`Why:`/`Note:`/`Caveat:` from the record. The irrigation ditch keeps the supply entries ('The comb net is
   drawn at TRUE SIZE', 'Where the drawn net STOPS', 'The head-race forks', 'Water-first v2') plus the new intake
   section from R2; the drainage ditch names 'The drain's tail is WIDER than the head-race', the supply/drain
   separation and 'No toe marsh at town/city scale', plus R2's foot-of-the-field finding. `Stream`'s `What:` stops
   saying the brook carries the drain away (FR-002).
2. **The FR-007 table** in `specs/134-interactive-html-map/spec.md`: the `field ditch` row becomes two rows; the
   `stream`, `pond`, `pond sluice` and `perimeter dike` rows' sibling columns name the right ditch. The registry
   test reads this table (`test_every_spec_class_is_registered_and_nothing_else`).
3. **The snapshot** `tests/fixtures/classes_before_189.json` is NOT edited (spec SC-2; it is the record of the
   registry before feature 189). Its test gains `SINCE_189 = {"field ditch": ("irrigation ditch", "drainage
   ditch")}` - the keys retired since the snapshot and their successors - and reads: every snapshot key is in
   `CLASSES` or retired; every `CLASSES` key is in the snapshot or a successor; the data-field equality holds for
   every surviving key; the count is 51 - retired + added.
4. **Sibling texts** (`assets/siblings.json`): rewrite the three pairs that name `field ditch` (with `pond
   sluice`, `stream`, `pond`) for the class each concerns - the sluice pairs with the irrigation ditch (a pond's
   supply); the stream and the pond pair with BOTH ditches; add the irrigation/drainage pair. `test_classes.py`'s
   confusable-pairs list and its bare-caveat set follow.
5. **Hit boxes** (`page.py`): `HIT_WIDEN` and `HIT_PRIORITY` rows for both keys, the sluice's "similar to the field
   ditches" equality kept against the irrigation ditch; `test_page.py`'s examples renamed.
6. **The emit sites** - the class from the role, at the stroke:
   - `water_ways/clipping.py` `field_channel(pts, col, w0, w1, late, cls="irrigation ditch")` gains a `cls`
     parameter with the irrigation default, passed through to both `_water` calls;
   - `fields/comb.py` line 368 passes `cls="drainage ditch" if c["role"] == "drain" else "irrigation ditch"` -
     the SAME conditional that picks the color, written once as a small helper (`ditch_class(role)` beside the
     color pick, so the two cannot diverge);
   - `hamletgen/sink.py` line 310 (the outfall run to the pond) passes `cls="drainage ditch"`;
   - `water_ways/water.py` `channel()` classes by its anchors: `frm.kind == "drain"` -> drainage, else irrigation
     (a city's moat-fed feed, a cascade connector, a drain culvert to a moat or stream);
   - `fields/features.py` line 34 (a pond's feeder stroke) -> irrigation; `city/canals.py` line 180 -> irrigation.
7. **FR-002, the off-frame run** (`hamletgen/sink.py` 238/246 - Sawada, Kashikawa and Kuwabata): drawn by `field_channel` at the collector's tail
   width (`chan_px(DRAIN_FT[1], GRAIN)`, as the pond run is) with `cls="drainage ditch"`, recorded in
   `M["channels"]` `frm: drain -> to: offmap` (the pond run's record shape), the corridor reserved as the pond run
   reserves its own (`field_channel` registers none). What reads the old `streams` record: `ways/track.py`'s
   watercourse list (reads `channels` and `drawn_channels` too - covered), `plan.sink_brook` (kept, it is a
   polyline), `tests/gate/test_water_flow.py` (the `offmap` kind branch - read before editing), and
   `tests/hamletgen/test_sink.py`. `stream_runs_off_edge`-style rules that lived in the retired battery are unit
   tests now; each one that asserted "the drain brook is a stream" is rewritten to assert the channel reaches the
   frame. **If R2 finds the outfall run was a natural watercourse**, this step inverts: the POND run becomes a
   `stream` record too, and the class is `stream` for both - D3 records which.
8. **Notes and prose**: `pool/hamlets/*/*.notes.md` mentions (prose only - no `### Features` key uses the class);
   `settlements/water.md` wherever it names the class; `interactive/CLAUDE.md`'s class list; `dev/placement.md`
   if it names the key.
9. **Verification of this half**: `make quick`; `make page-check` (registry tests, the synthetic browser page,
   which builds one element per class from `CLASSES`); `make map GEN=pool/hamlets/inashiro/inashiro.gen.py` and
   open the page: hover the collector (SC-1); then the pool.

## The research pass (FR-003) - the procedure

- Two background readers (Japan-first, China-first), one attempt per host, dispatched 2026-09-12; the stall
  watcher armed (`agent-stall-hooks.sh watch`).
- From their quotes: R2 in `research.md` (what was searched, each verdict, the passages); every new work a
  registry entry in `research/SOURCES.html` with its citation line and both write-ups; `source-applicability`
  over the new keys BEFORE any number reaches the engine; the new section of `research/water.html` (heading as
  the reader's question; `<!-- researched 2026-09-12, feature 230 T02 -->`; Grounds and Evidence as comments;
  the `Sources:` roster; a footnote per assertion on `research/citations/water.html`; `make citations`); the
  glossary for any new term (`weir`, `head race`, `bunsuiguchi`, `collector` already exist); `quote-check` and
  `record-format` in the same turn over the new section and the drain entries the drainage class cites; the
  rule line in `settlements/water.md`; the pointers at the three points of change.
- The five boxes on T02, ticked on verification with the verdicts written in.

## The head (FR-004) - filled in when R2 lands

The outcome (a/b/c/d) and its design go here: what replaces `_comb_skeleton`'s 90 px and `feed_brook`'s 420 px,
how the brook is routed if it continues, the weir glyph's class and size, the knob's name and values if there
are two forms, and the unit tests of each. Until then, nothing at the head moves.

## Tasks

`tasks.md` - T01 the spec review; T02 the research pass (physical, five boxes); T03 the class split and FR-002
on Inashiro; T04 the head per R2 on Inashiro; T05 the pool, the cohort if the routing changed, the review, the
records, the landing.
