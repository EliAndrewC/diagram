# Feature 230 - the stream's intake, and the two ditch classes

**Status**: ACCEPTED 2026-09-12 - `spec-fidelity` rounds 1-4 CHANGES REQUIRED (each applied, see Review history), round 5 FAITHFUL. Implementation in progress.
**Request**: [`request.md`](request.md). **Research**: [`research.md`](research.md) - R1 the state of the record
before the pass, R2 the pass itself (what was searched, what was found, the verdicts), R3 the maps before and
after. **Predecessors**: 134 (the class vocabulary), 159 (a class decided at one emit site from the fill about to
be drawn - the precedent for FR-001's rule), 143/194/195/211 (the research record's form), the water-width
ladder and the fork (research/water.html, "Drawn width is RANK" and "The head-race forks").

## Summary

Three things the GM asked for on the reference hamlet, all at the head and the foot of the comb field - and one
consequence of the third that reaches past the field: once the brook runs on down the fan's flank instead of
ending at the intake, the settlement is seated clear of it (FR-006).

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
   down the fall to the fork - no weir, no gate, no bend, no research entry behind the 90. The research pass
   (FR-003, run first; research.md R2) found that a natural stream becomes a ditch at an INTAKE on one of its banks
   and that the stream runs on below it, in both reference traditions; that the intake took two attested forms, a
   bare bank intake and a built weir; and that the record holds no distance from the intake to the first division.
   FR-004 is the design that follows: the brook continues past the fan, the intake form is a per-settlement knob,
   and the head race's length is derived from the geometry.

## Functional requirements

- **FR-001 Two classes replace `field ditch`, decided at the emit site from the record's own role.** The
  vocabulary (`interactive/classes/water_and_ways.py`, the FR-007 table in `specs/134-interactive-html-map/spec.md`
  that the registry tests read) loses `field ditch` and gains:
  ONE rule, total and exclusive, so no stroke the engine can emit is left without a class: a `field_ditches`
  record is a **drainage ditch** when its `role` is `drain` and an **irrigation ditch** otherwise; a `channels`
  record is a **drainage ditch** when its `frm.kind` is `drain` and an **irrigation ditch** otherwise; and a
  ditch stroke emitted with NO water record at all - today only the pond's feeder curve in `fields/features.py`,
  drawn with an empty record and a fixed hue - is an **irrigation ditch**, the feed into a reservoir being
  supply. What that makes each class, as illustration and not as the test:
  - **`irrigation ditch`** - the dug channels that carry water TO the paddies: a comb's head race, supply canals
    and delivery ditches; a polder's feeder ring and laterals; the source-to-field feed from a stream, a pond or a
    moat; a stream-fed tap to a ditch; a field-to-field cascade connector that leaves a FIELD (`frm.kind` is
    `field`).
  - **`drainage ditch`** - the dug channels that carry water AWAY: a comb's collector; a polder's drain and toe
    collectors; the outfall run into the pond, to a stream confluence, to a moat, or off the frame (FR-002); and a
    cascade connector that leaves a DRAIN to feed a lower field (`frm.kind` is `drain`, `to.kind` is `field` - a
    town's fan reusing its upper fan's runoff), which is the drain's water going on and so is classed with the
    drain, whatever it feeds.
  The class is decided where the stroke is emitted, and wherever a stroke's color is chosen from a record
  (the `role` of a ditch record in the comb's emit loop, the `frm` anchor of a channel) the class reads the SAME
  field, so class and color cannot disagree there - the rule feature 159 set for the blue plot; the record-less
  feeder curve has a fixed hue and takes the fixed class above. Every emit site that writes `field ditch` today is converted (the plan enumerates them:
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
- **FR-002 The drain's continuation carries ONE class whichever way the water goes, and it may reach the passing
  brook.** The run from the collector's outfall onward is a **drainage ditch** in every sink: the collector's own dug
  continuation, drawn at the collector's tail width by the ditch stroke, recorded as a `channels` record leaving the
  drain (`frm.kind` is `drain`), never a `streams` record. Three sinks, and the record kind names each in `to`:
  - **into the tameike** (`to.kind` is `pond`; Inashiro, Mizuguchi today) - as drawn now;
  - **into the passing brook** (`to.kind` is `stream`) - NEW, the form the research found (a district's drainage
    returned to the river to be taken up below, research R2c point 6): when FR-004's continuing brook passes within
    reach of the outfall (the condition is the same bearing-and-distance search the off-frame run makes today, with
    the brook's bank as a candidate end that wins over the frame when a clear route to it exists), the drain runs to
    the brook's bank and joins it at a confluence, the ditch stroke's stream clip making the mouth; the ditch is a
    drainage ditch to the junction and the brook below the junction stays a `stream`;
  - **off the frame** (`to.kind` is `offmap`; Sawada, Kashikawa and Kuwabata today, drawn by `stream` at 8 px and
    recorded in `streams`) - kept for a drain the brook does not pass, now drawn and recorded as the other two are.
  So the two sinks that disagreed today agree, the third is the researched one, and the `stream` class's explanation
  stops claiming the brook "carries the drain away". The outfall itself and the pond's set-back do not move; what
  changes about the route is only that a run which reached the frame may now end at the brook instead.
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
  The entry answers the GM's own candidate reading in so many words - that the stream should "still be called
  a stream right up until the point where it branched into two" - saying whether the record supports it,
  refutes it, or is silent, since that is what the GM was looking at when they asked.
  The reading is dispatched to background readers (one attempt per host, verbatim passages, translations
  marked); every new source gets a registry entry with both write-ups and is judged by `source-applicability`
  BEFORE its numbers or forms reach the engine; the finding is written as a new section of `research/water.html`
  headed as the question a reader would ask from the map, every assertion footnoted on
  `research/citations/water.html` (`make citations`), `quote-check` and `record-format` run over it, the rule
  line in `settlements/water.md` that today says the brook "BECOMES the irrigation channel - it hands off to
  the comb and stops" rewritten to say what the record says, and a pointer at each point of change
  (`waterfields/comb.py` `_comb_skeleton`, `hamletgen/water.py` `feed_brook`, `hamletgen/sink.py`).
- **FR-004 The stream-to-ditch point, as the research found it: the brook runs on, the intake is a knob, the
  head race is derived.** In the scripted hamlet generator, the one live tier with a brook at its head (Inashiro,
  Mizuguchi, Sawada, Kashikawa; Kuwabata's polder is pond-fed and keeps its head; the frozen legacy exhibits are never
  regenerated), the head of every comb field is drawn thus:
  - **The brook CONTINUES past the intake.** It comes down off the high ground, passes the head of the fan on one
    side - the side its rolled approach puts it on - and runs on down that flank of the field, routed clear of every
    plot (the paddies and the dry hem alike) and of the pond, to leave the frame; it receives the drain where FR-002
    says. It is one `streams` record from off the map to off the map, never drawn through a paddy (the standing
    placer rule), and the two constants that made the old picture - the 420 px run and the 90 px head race - are
    gone from the code.
  - **The intake form is a KNOB with exactly two values**, rolled from the map's seed per settlement with an even
    chance (the record attests both and gives no proportion; the even roll is labeled a GUESS in the entry, the rule
    file and the weir's `Note:`):
    - **`weir`** - a bar of stone-packed timber crib across the brook at the intake mouth, running diagonally
      upstream from the mouth as the old oblique weirs did, drawn as a full closure of the brook (a map drawing
      convention, recorded: half-river closures were the common old form and are unreadable at a 7 ft brook) and
      5 ft thick (a GUESS, recorded: no source read gives a village weir's thickness). It is a new class, `weir`,
      with its own explanation, entry, label and hit-box row, a row of the FR-007 table, and a `weir` record in the
      manifest.
    - **`open`** - the bare bank intake: nothing is built across the brook, because the record says that in old
      times often nothing was. What marks the point is the offtake junction itself: the brook runs on straight and
      the head race leaves its bank at an acute angle pointing downstream, so the page shows a visible fork of
      stream and ditch where today it shows one line changing width. The intake is recorded in the manifest with its
      form so the page and the tests can read which was rolled.
  - **The head race is DERIVED.** It leaves the brook's bank at the intake at an acute angle pointing downstream
    (the record's offtake rule, 30-45 degrees) and runs to the division point at the fan's head; its length is
    whatever that geometry gives - the intake's lead upslope of the fork and its lateral offset from it, both rolled
    per map within a stated band - never a constant; the record's silence on the distance is labeled in the entry
    and at the point of change.
  - **One map per knob value is on the sheet**: the pool's four comb hamlets show both an `open` and a `weir`
    intake (a knob owes one map per value; if the pool's seeds roll one value only, one hamlet's roll is salted so
    that both are shown, and the salt is recorded).
  - The page's `stream`, `irrigation ditch` and `weir` explanations say what the map now shows.
- **FR-005 Reference hamlet first, then the pool; the standing gate.** Every step is two steps (constitution VI):
  Inashiro, then the five pool maps, their pages regenerated. The changed placers get unit tests; the page's
  registry tests cover the two classes; `make done` is green at 100% coverage; `settlement-review` reads the pool
  maps whose head moved (scope stated per map); the perf bookends are taken; the pool shows one map per intake
  value (FR-004); and because the brook's routing changes on every comb map, a 48-seed cohort proves no seed draws a
  stream through its crop, strands its brook, or loses households to the brook's corridor (the cohort audit's
  shortfall report).

- **FR-006 The brook's new course changes where the cluster may be seated, and that may not cost the map a
  household.** Because FR-004's brook runs on down a flank of the field instead of ending at the intake, a field
  margin can have a stream through it. `seat_cluster` therefore scores a margin down in proportion to how near
  the brook runs to the band, and STRIKES OUT a margin the brook DIVIDES, the scored form deciding only when
  every margin is divided - so a hamlet the brook crosses whatever it does is still seated. On the reference
  hamlet this moves the whole cluster - the fifteen houses, both wells, the three byres, the lane web, the
  notice board, the windbreak and the copse - to the other margin, while the field, its ditches and the tameike
  stay where they are. The rule may not cost a household: where a roll seats fewer households than its spec
  declares AND the brook steered its seat - by either half of the rule, the strike-out or the proximity penalty
  - the map is rolled again with the brook ignored at the seat, and that roll is kept only if it seats MORE.
  Which way each map came down is recorded on it (`meta.seat_divided`).

## Success criteria

- **SC-1** On Inashiro's page, hovering the collector lights the drain and its outfall run and nothing of the
  supply net; hovering the head race lights the supply net and nothing of the drain. The two modals' texts are
  different: the irrigation ditch's says nothing about where the water goes, the drainage ditch's nothing about
  feeding the paddies.
- **SC-2** The class KEY `field ditch` survives on no live surface the page or its registry tests read: the
  engine's emit sites and class registry, `page.py`'s hit rows, `assets/siblings.json`, the pool `.notes.md`
  feature blocks, the FR-007 table. Two things are deliberately NOT touched: the phrase's ordinary prose use (the
  width-ladder comments, "~70x a field ditch"), and `tests/fixtures/classes_before_189.json`, which is the record
  of what the registry WAS before feature 189 and is not edited; its equality test carries the proof forward
  through a small table of the keys retired and added since the snapshot (`field ditch` -> `irrigation ditch`,
  `drainage ditch`), so the 51-class proof still holds for every key the snapshot has and the count moves with
  the table rather than by hand.
- **SC-3** Sawada's, Kashikawa's and Kuwabata's off-frame drain runs and Inashiro's and Mizuguchi's pond runs
  carry the same class and the same record kind.
- **SC-4** The head race and the intake on every comb pool map follow a recorded, footnoted finding - or a GUESS
  the record labels and the GM has been told about - and the physical task's five boxes are ticked with their
  verdicts.
- **SC-6** Across the 48-seed cohort every seed seats every household its spec declares - the pre-feature
  baseline of 48 of 48 restored, not approached - and no pool map or cohort seed leaves a homestead across the
  brook from the lanes, wells and board that serve it. Inashiro's notes record that the cluster moved, and why.
- **SC-5** `make done` green; `settlement-review` PASS on every pool map it reads; no regression against the
  detached-worktree baseline; the perf band explained and confirmed if one is reached.

## Decisions recorded

- **D1 The names are the reader's words.** `irrigation ditch` and `drainage ditch`: the GM's own second word
  ("a drainage ditch"), and the pair a casual reader knows without a tooltip. The record's own pair (the
  Japanese supply and drainage canals) is quoted in the entry, not used as the key.
- **D2 The class is decided from the role at the emit site**, never by a second list - the wet-paddy precedent
  (feature 159): where a color is chosen from a record, the class reads the same field - a ditch record's `role`
  (`drain` or not), a channel record's `frm.kind` (`drain` or not) - and the one record-less stroke (the pond's
  feeder curve) is an irrigation ditch by the rule's third clause; the rule is total, so a channel shape the pool
  does not draw today (a stream-fed tap to a ditch, a drain-fed cascade) is classed by the same tests and never
  falls through.
- **D3 The outfall run is a drainage ditch in both sinks** (FR-002), the collector's dug continuation. The pass
  settled it (research R2c point 6): before postwar field consolidation a paddy's drainage went field to field or
  back into a combined channel and returned to the river to be taken up by the district below, so a village drain
  is a dug channel that reaches a watercourse - never a brook of its own. Where the continuing brook passes the
  outfall the drain joins it (a confluence); where it does not, the drain runs on as a ditch to the frame or the
  pond.
- **D4 The research outcome, and the ladder it was read on** (research R2c; the ladder - decisive, two forms,
  silent - was the spec's original FR-004 and is history now that FR-004 states the delivered design). The stream CONTINUES past the intake -
  decisive in both traditions: half-river closures the common old form, the araizeki letting water over its crest
  at all times, the 1615 Ishi-ibi returning its surplus to the main river, FAO's intake taking the upper part of the
  flow and disposing of the lower part down the river, Dujiangyan and Lingqu dividing the river in stated
  proportions. The GM's "stream until it forks" reading is refuted in its letter (what forks is the dug canal, at a
  division works below the intake; the fork is never on the stream) and confirmed in its spirit (the stream stays
  a stream, all the way past the field). The intake FORM is a knob between two attested forms: the bare bank intake
  ("in old times ... in many cases no intake weir was built at all") and the weir (timber frames packed with stone,
  gabions, brushwood; oblique, running diagonally upstream from the intake mouth; Wang Zhen's timber palisade on
  the brook above the fields) - an even roll, the proportion a GUESS because the record gives none. Declined:
  whole capture of the brook (admitted by ICID's "part or all" and MAFF's drought passage, shown done nowhere -
  not a form the record shows, so not a knob value); the half-river closure as the drawn weir form (attested,
  but at a 7 ft brook a half-bar is unreadable - the full oblique closure of Tatai is drawn, a map drawing
  convention recorded in the entry). The head race's length is DERIVED from where the brook passes the fan's head
  and where the fork stands; the record gives no distance ("short distances", Tabayashi), and the entry says so.
- **D5 Scope is the live scripted hamlets.** FR-004 (the head) reaches the four comb hamlets whose brook meets
  a head race; Kuwabata's polder head is a pond and is out of FR-004's scope ONLY - it takes the class split
  (FR-001) and the drain-continuation fix (FR-002) like every other pool map, since its drain leaves the frame
  through the same code. The city fans are frozen exhibits or moat-fed and take the class split alone, on the
  next regeneration if ever.

- **D6 What the first review sent back, and what each answer was** (`settlement-review`, needs-work, seven errors; the ledger row carries the finding). The brook's course now reads EVERY cultivated ring - the paddy envelope, the dry hem plots and the supply canals - because the hem is laid outside the envelope and clearing the envelope alone put 1,456 ft of Sawada's brook between plough furrows; the profile is per RING rather than per vertex, since a plot's outermost corner can lie far downslope of the ground its body covers. The offset WANDERS on a seeded reflecting walk (`BROOK_WANDER`, `_wander`) instead of being held at the floor: held, it draws the ruled line the GM rejected on Inashiro by name in August and runs parallel to whatever canal hems that margin, which is the Ikegami two-water-lines catch in a new place. `_off_the_axes` is the backstop for the coincidence a diagonal fall can still produce, nudging away from the crop and never across the heading. The brook runs on down the FALL for its first stride below the tap (`BROOK_TAP_RUN`) so that the offtake angle the record states is the angle the reader sees - measured 64 and 46 degrees before it, because the rule is an angle off the brook's own heading and the code took it off the land's fall. The confluence must leave a trunk below it (`BROOK_JOIN_TRUNK`) after Sawada's landed 4.5 ft inside the frame. And a straggler footpath is routed against the STREAMS (`stream_segs`, the deck-needing subset that helper was split out for) after one crossed the new brook at 1.9 degrees with no deck; the empty list at that call site was right about ditches and became wrong the day the brook stopped ending at the intake.
- **D7 The angle at which the drain MEETS the brook is emergent, and labeled so.** The record's canal-junction rule governs an offtake LEAVING its parent (30 to 45 degrees, pointing downstream); the pass did not ask what angle water ARRIVING at a watercourse was cut to, and the reviewer's reading - that a made outfall may have been turned downstream while a natural tributary was not, which would make it a knob - is a research question this feature does not answer. The confluence's angle is whatever the geometry gives, and the record says so rather than implying a rule.

- **D8 Two questions the review raised and this feature does not answer**, both recorded rather than
  quietly settled. (1) Whether a made drain's mouth was turned downstream like a canal offtake, which would
  make the mouth angle a knob (D7). (2) Whether a 5.5 ft collector should carry watercourse ink or ditch ink
  where it meets a brook: at the confluence the two arms differ by about twenty units of color and a reader
  cannot tell which is the stream. That is a map-convention question and the palette is shared by every map,
  so it is the GM's to rule rather than this delta's to change.

- **D9 A hamlet does not straddle its own brook - and that rule may not cost it a household.** The brook runs
  past the fan now, so a field margin can have a stream down the middle of it; the fourth and fifth review
  passes measured what a cluster seated there looks like (a homestead, its byre, two threshing yards and their
  gardens on the far bank, every lane and both wells on the near one, no deck anywhere on 2,000 ft of water).
  So `seat_cluster` scores a margin down when the brook runs near the band and strikes it out when the brook
  divides the band. The 48-seed cohort then measured the other side of it against the pre-feature baseline -
  48/48 became 46/48 - because the ground the brook rules out is ground the houses had. Both outcomes are
  defects, so neither rule is absolute: a roll that comes up short and was steered by the brook is rolled again
  with the brook ignored at the seat, and kept only if it seats MORE. Which way a map came down is recorded on
  it (`meta.seat_divided`). Measurements and the per-seed mechanism: research R5.
- **D10 A rejected re-roll is no longer the manifest the report carries.** Found while diagnosing D9's
  shortfall and older than this feature: `generate`'s re-roll loop relied on the kept attempt rolling last,
  which holds only when an `out_base` lets it re-emit the keeper - and a cohort passes none, so the report's
  manifest could be a roll the loop had just rejected, while its verdict lines were the kept roll's. The
  cohort audit reads the seated count off that manifest. The keeper is snapshotted and restored instead
  (constitution XIV: a defect found in the course of other work is fixed in that work).

## Out of scope

- The drain's outfall and the pond's set-back: neither moves. The drain's continuation changes in class, record
  kind and drawn width, and in one way in its route - a run that reached the frame may end at the passing brook
  instead (FR-002); nothing else about where the drain runs changes.
- The settlement's seat is NOT out of scope: FR-006 moves it, and only for the brook. Nothing else about where
  the settlement stands changes - the band's size, its shape knob, the wind and slope scoring and every other
  hard rule are as they were.
- The legacy hand-authored pool, which is frozen and never regenerated.
- The page's speed, and any change to the hit-box mechanics beyond the two new rows.

## Review history

- Round 1 (2026-09-12): CHANGES REQUIRED, three items, each applied - (1) D5 exempted Kuwabata from FR-002 though
  its off-frame drain run is written by the same code (FR-002, SC-3, D5 now name it); (2) SC-2 swept in the
  phrase's prose uses and the frozen pre-189 snapshot (rewritten to the class KEY on live surfaces, the snapshot
  untouched and its proof carried by a retired/added table); (3) FR-004 (d) ended the feature with a labeled
  guess against "and then making that change as well" (the GM's ruling is implemented under this feature; the
  guess is interim). The reviewer's aside - answer the GM's "stream until it forks" reading explicitly - added
  to FR-003.
- Round 2 (2026-09-12): CHANGES REQUIRED, two items, each applied - (1) FR-001's channel rule was neither total
  nor exclusive (a drain-fed cascade matched both bullets, a stream-fed tap to a ditch matched neither) and D2
  stated a different rule; now one rule - `role` is `drain` / `frm.kind` is `drain` -> drainage, else
  irrigation - with the destination lists as illustration and the cascade named; (2) the Out-of-scope route
  bullet said "only its class and record kind change", contradicting FR-002's drawn width; rewritten.
- Round 3 (2026-09-12): CHANGES REQUIRED, one item, applied - the pond's feeder curve in `fields/features.py` is
  emitted with an empty record, so FR-001's two-clause rule could not reach it and "the same field that decides
  its color" was untrue there; a third clause (a record-less ditch stroke is an irrigation ditch) added to FR-001
  and D2, and the color sentence qualified. D3 and D4 filled from the finished research pass in the same edit.
- Round 4 (2026-09-12): CHANGES REQUIRED, two items, each applied - (1) FR-004 still read as the pre-research
  ladder while D4 recorded the finding, so the delivered design was unspecified (a weir on every map by (a), a knob by
  D4); FR-004 rewritten as the one design - the brook continues, the intake knob with two values and what each
  draws at the point, the head race derived, one map per value; the ladder kept as history in D4; (2) FR-002, D3 and
  Out of scope disagreed about the confluence; FR-002 now names three sinks (pond, the passing brook, the frame),
  the condition, the record and the class below the junction, the inert UNLESS removed, and Out of scope says the
  one way the route changes. FR-005's cohort made unconditional and given the one-map-per-value duty.
- Round 5 (2026-09-12): FAITHFUL. The reviewer's aside - once every comb map's brook runs down its flank, the off-frame drain sink may be reached only by Kuwabata's polder; confirm at the pool sweep which comb map, if any, still exercises it, or record that none does - is carried to T05.
- Amendment round 1 (2026-09-12, the counter reset to zero on the post-acceptance decisions D6-D10, per the GM's
  ruling of the same day): CHANGES REQUIRED, five items. D9 and D10 were judged INSIDE the request - a brook that
  runs from off-map to off-map is the geometry accepted FR-004 creates, so seating the cluster clear of it is what
  paying for that costs rather than a widening, and D10 is Principle XIV applied to a defect found while
  diagnosing D9. What was wrong was that the delivered behavior lived only in a decision paragraph: (1) no
  requirement stated the seat rule - now FR-006; (2) no success criterion measured it - now SC-6; (3) D9 asserted a
  physical proposition ("a hamlet does not straddle its own brook") with no Principle XII label and no declined
  alternative, and the task carrying it was classified `rendering` so it owed no research boxes - a research pass
  is running and the label follows it, in D9, in Inashiro's notes and at the point of change alike; (4) the rule
  moved into its own `research: physical` task, T06, with the five boxes; (5) the Summary and Out of scope
  described a smaller feature than the one built - both corrected. The reviewer's aside is recorded as a question
  for a later feature: the record may show villages on both banks with a crossing, which under the knob doctrine
  would make one bank versus two a KNOB rather than a rule.

