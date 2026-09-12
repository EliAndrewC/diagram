# Feature 230 - the stream's intake, and the two ditch classes

**Status**: DRAFT 2026-09-12 - `spec-fidelity` review pending.
**Request**: [`request.md`](request.md). **Research**: [`research.md`](research.md) - R1 the state of the record
before the pass, R2 the pass itself (what was searched, what was found, the verdicts), R3 the maps before and
after. **Predecessors**: 134 (the class vocabulary), 159 (a class decided at one emit site from the fill about to
be drawn - the precedent for FR-001's rule), 143/194/195/211 (the research record's form), the water-width
ladder and the fork (research/water.html, "Drawn width is RANK" and "The head-race forks").

## Summary

Three things the GM asked for on the reference hamlet, all at the head and the foot of the comb field:

1. **The one `field ditch` class becomes two.** The ditches that FEED the paddies (the intake, the head race,
   the supply canals, the delivery ditches) and the ditches that DRAIN them (the collector along the low line
   and its run onward to the pond, a stream or the frame's edge) are both dug channels, but the reader's question
   is different at each end and so is the record behind each; today one class and one explanation cover both, and
   the explanation is written entirely about supply. The engine already carries the distinction on every record
   (`role`), and already paints the drain a different blue.
2. **The drain's continuation is one kind of thing whichever way the water goes.** Today the run from the
   collector's outfall into the pond is classed a field ditch (Inashiro, Mizuguchi) and the same run off the frame
   is drawn and classed as a STREAM (Sawada, Kashikawa). That is the inconsistency the GM asked to have fixed.
3. **The point where the brook becomes the ditch is researched and then derived, not a constant.** Today the
   brook is a fixed 420 px run ending at the intake, and the head race is a hardcoded 90 px straight continuation
   down the fall to the fork - no weir, no gate, no bend, no research entry behind the 90. A research pass answers
   where and how a natural stream became an irrigation canal in the setting's two reference traditions, and the
   engine then draws what the record says: a decisive finding is implemented; two attested forms become a knob
   rolled per settlement; a silent record leaves a labeled guess and a question for the GM (constitution XII).

## Functional requirements

- **FR-001 Two classes replace `field ditch`, decided at the emit site from the record's own role.** The
  vocabulary (`interactive/classes/water_and_ways.py`, the FR-007 table in `specs/134-interactive-html-map/spec.md`
  that the registry tests read) loses `field ditch` and gains:
  - **`irrigation ditch`** - the dug channels that carry water TO the paddies: every `field_ditches` record whose
    `role` is not `drain` (a comb's head race, supply canals and delivery ditches; a polder's feeder ring and
    laterals), and every `channels` record whose destination is a field (the source-to-field feed from a stream,
    a pond or a moat, and a field-to-field cascade connector).
  - **`drainage ditch`** - the dug channels that carry water AWAY: every `field_ditches` record whose `role` is
    `drain` (a comb's collector; a polder's drain and toe collectors), and every `channels` record that leaves a
    drain (`frm.kind == "drain"`): the outfall run into the pond, to a stream confluence, to a moat, or off the frame
    (FR-002).
  The class is decided where the stroke is emitted, from the SAME field that decides its color today (the `role`
  of the record, or the `frm` anchor of a channel), so class and color cannot disagree - the rule feature 159 set
  for the blue plot. Every emit site that writes `field ditch` today is converted (the plan enumerates them:
  `water_ways/water.py` `channel`, `field_channel`, the pond-clipped re-emits in `water_ways/clipping.py`, the
  pond's feeder stroke in `fields/features.py`), and no `field ditch` key survives anywhere the page or its tests
  read: the engine, `page.py`'s hit-widening and priority rows (both new keys get rows - the GM's "very thin and
  hard to move my mouse over" ruling applies to both), `assets/siblings.json`, the pool maps' `.notes.md`
  feature blocks, the test fixtures and the FR-007 table. Each class gets its own explanation, written from the
  record and carrying its label: the irrigation ditch's from the supply entries the old class already named; the
  drainage ditch's from the record's drain entries (the drain's tail wider than the head race; supply and drain
  kept separate; where the runoff goes) and from whatever FR-003 adds about the foot of the field. The sibling
  texts that named `field ditch` (against the stream, the pond, the pond sluice and the perimeter dike) are
  rewritten for the class each pair now concerns, and a new pair distinguishes the two ditches from each other.
- **FR-002 The drain's continuation carries ONE class whichever way the water goes.** The run from the
  collector's outfall onward - into the tameike (`hamletgen/sink.py`, drawn by `field_channel` and recorded as a
  `channels` record from the drain), or off the frame (the same module, drawn today by `stream` at 8 px and
  recorded in `streams`) - is the same kind of thing on the page in both cases. It is a **drainage ditch**: the
  collector's own dug continuation, drawn at the collector's width, recorded as a `channels` record leaving the
  drain, not a `streams` record - UNLESS FR-003's pass finds that a village drain's outfall run was a natural
  watercourse rather than a dug one, in which case both runs follow that finding together. Whichever way, the two
  sinks agree, and the `stream` class's explanation stops claiming the brook "carries the drain away".
- **FR-003 The research pass: where does a natural stream become an irrigation ditch?** A `research: physical`
  task with the five boxes (research pass; source-reader confirmed; recorded and cited; quote-check confirmed;
  source-applicability confirmed), run FIRST, before any change to the head's geometry. The questions, Japan
  and China both:
  1. What structure marks the point where a stream's water enters a canal - the weir, the intake gate, the head
     works - and what did a small-stream village weir look like before modern times?
  2. Does the stream CONTINUE below the diversion with its surplus, or was a small brook ever taken wholly into a
     village's ditch so that no stream continues?
  3. How far does the main canal run from the intake before its first division, and is there a settling reach or
     sand trap near the intake?
  4. At what angle does the intake canal leave the stream?
  5. The supply/drainage vocabulary and practice: were the two kept separate, and where did a village's drain
     discharge - a river, a pond, another field, the next village's intake? (This is the foot's half of the
     question, and what FR-002 waits on.)
  The reading is dispatched to background readers (one attempt per host, verbatim passages, translations
  marked); every new source gets a registry entry with both write-ups and is judged by `source-applicability`
  BEFORE its numbers or forms reach the engine; the finding is written as a new section of `research/water.html`
  headed as the question a reader would ask from the map, every assertion footnoted on
  `research/citations/water.html` (`make citations`), `quote-check` and `record-format` run over it, the rule
  line in `settlements/water.md` that today says the brook "BECOMES the irrigation channel - it hands off to
  the comb and stops" rewritten to say what the record says, and a pointer at each point of change
  (`waterfields/comb.py` `_comb_skeleton`, `hamletgen/water.py` `feed_brook`, `hamletgen/sink.py`).
- **FR-004 The stream-to-ditch point is DERIVED from the finding, on the ladder the constitution sets.** Whatever
  FR-003 finds replaces the 90 px head race and the "stream ends at the intake" convention in the scripted hamlet
  generator, the one live tier with a brook at its head (Inashiro, Mizuguchi, Sawada, Kashikawa; Kuwabata's
  polder is pond-fed and keeps its head, and the frozen legacy exhibits are never regenerated). The outcomes,
  each fully specified now so the finding chooses rather than the session:
  - **(a) The record is decisive for a weir with the stream continuing.** The brook runs on past the intake -
    routed clear of the crop as it is today, down a flank of the fan, to wherever the record says a village
    brook went (off the frame, or into the drain's own outfall) - and the intake is DRAWN: a weir across the
    brook with the head race leaving its pool on one bank, at the attested angle, running the attested distance
    (or a distance derived from the fan, with per-map variance) to the fork. The weir is a new class with its own
    entry, drawn at true size or as a labeled map drawing convention if true size is sub-perceptual.
  - **(b) The record is decisive for whole capture of a small brook.** The brook still ends at the intake, but
    the point is MARKED by the weir or head-gate glyph, and the head race's length and line follow the finding -
    for instance the brook arriving at an angle so the straight dug reach reads as dug against the brook's line.
  - **(c) The record attests BOTH forms.** They become a knob, rolled from the map's seed per settlement, and a
    knob owes one map per value on the sheet (the pool shows both if its seeds roll both).
  - **(d) The record is silent or contradictory.** The GM is asked, with what was searched and found; the 90 px
    head race stays, labeled GUESS in the research entry, the rule file and the class's `Note:`.
  In every outcome the two constants - the 90 px head race and the 420 px brook run - are either derived or are
  recorded as guesses with the record's reason, at the point of change; the page's `stream` and `irrigation
  ditch` explanations say what the map now shows; and the brook is never drawn through a paddy (the standing
  placer rule).
- **FR-005 Reference hamlet first, then the pool; the standing gate.** Every step is two steps (constitution VI):
  Inashiro, then the five pool maps, their pages regenerated. The changed placers get unit tests; the page's
  registry tests cover the two classes; `make done` is green at 100% coverage; `settlement-review` reads the pool
  maps whose head moved (scope stated per map); the perf bookends are taken; and if the brook's routing changes
  (outcome a or c), a 48-seed cohort proves no seed draws a stream through its crop or strands its brook.

## Success criteria

- **SC-1** On Inashiro's page, hovering the collector lights the drain and its outfall run and nothing of the
  supply net; hovering the head race lights the supply net and nothing of the drain. The two modals' texts are
  different: the irrigation ditch's says nothing about where the water goes, the drainage ditch's nothing about
  feeding the paddies.
- **SC-2** `field ditch` occurs nowhere the page or its tests read - engine, assets, fixtures, notes, the FR-007
  table - only in git history and the specs' own records.
- **SC-3** Sawada's and Kashikawa's off-frame drain runs and Inashiro's and Mizuguchi's pond runs carry the same
  class and the same record kind.
- **SC-4** The head race and the intake on every comb pool map follow a recorded, footnoted finding - or a GUESS
  the record labels and the GM has been told about - and the physical task's five boxes are ticked with their
  verdicts.
- **SC-5** `make done` green; `settlement-review` PASS on every pool map it reads; no regression against the
  detached-worktree baseline; the perf band explained and confirmed if one is reached.

## Decisions recorded

- **D1 The names are the reader's words.** `irrigation ditch` and `drainage ditch`: the GM's own second word
  ("a drainage ditch"), and the pair a casual reader knows without a tooltip. The record's own pair (the
  Japanese supply and drainage canals) is quoted in the entry, not used as the key.
- **D2 The class is decided from the role at the emit site**, never by a second list - the wet-paddy precedent
  (feature 159): the color and the class read one field.
- **D3 The outfall run is a drainage ditch in both sinks** (FR-002), the collector's dug continuation, unless the
  pass finds otherwise; the finding, when it lands, is written here.
- **D4 The ladder outcome** - (a), (b), (c) or (d) of FR-004 - is written here when the pass lands, with the
  passages that chose it.
- **D5 Scope is the live scripted hamlets.** The polder's head is a pond; the city fans are frozen exhibits or
  moat-fed; neither has a brook meeting a head race. Both take the class split (their strokes carry roles) and
  nothing else.

## Out of scope

- The drain's ROUTE (where the outfall sits, the pond's set-back) - only its class and record kind change.
- The legacy hand-authored pool, which is frozen and never regenerated.
- The page's speed, and any change to the hit-box mechanics beyond the two new rows.

## Review history

- Round 1: pending.
