# Feature 157 - research

Nothing here is a HISTORICAL question. Every decision this feature makes is a map convention
(constitution XII's "deviation" class), so the research pass this project owes a *physical* question
is not owed here - see the note in `spec.md`'s "Decisions Recorded". What follows is the
MEASUREMENT pass, which is owed: the GM reported a symptom, and the rule of this repository is that
the next step is a measurement, never a speculative edit.

## R1 - what actually happened to Kuwabata's notice-board caption

Measured against `pool/hamlets/kuwabata.json` at commit `7aee251f`.

- board: `x=2394.2, y=559.1, rot=151.9`, drawn `12.0 x 5.0` px (hamlet grain, 1 px = 1 ft)
- caption tilt: `linear_tilt(151.9) = -28.1` - the board's own angle, correct
- caption record: box `x 2404.1..2456.9, y 547.3..555.7`, so its center is `(2430.5, 551.5)` and its
  anchor `(2430.5, 553.7)`

Decomposed in the CAPTION'S OWN FRAME (the axis the text runs along, and the axis across it):

| quantity | value |
|---|---|
| displacement ALONG the baseline (lateral) | **35.6 px** |
| displacement ACROSS it (standoff) | 10.4 px |
| the caption's own half-run | 26.4 px |
| the board's half-extent along that baseline | 6.5 px |

So the board is **past the end of its own label**: the caption's run spans -26.4..+26.4 about its
center and the board sits at 35.6. That is exactly what the GM described - *"correctly aligned ...
the correct distance ... but ... off to the right a bit"*. The alignment and the standoff are right;
the lateral is wrong.

## R2 - which seat the placer chose, and why

`Settlement.kosatsuba` builds 30 candidate seats for a TILTED board
(`fixtures.py`, the `elif _t:` branch):

```
for above in (False, True) for gap in (11, 16, 21, 28, 36) for lateral in (0.0, +38.88, -38.88)
```

and hands them to `pick_caption_seat`, which keeps the seats inside the hug cap, then those clearing
the lane target, then those that are not `blocked`, and takes the NEAREST of what survives.

Enumerated on Kuwabata (`hug` = quad gap to the board, `clear` = the lane/well clearance the gate
measures, `blocked` = the structural/way-side term):

| seat | dist | hug | clear | blocked |
|---|---|---|---|---|
| gap 11, lateral 0 (the historical default) | 13.5 | 3.5 | **1.88** (< the 3.0 target) | lap:houses |
| gap 16, lateral 0 | 18.5 | 8.5 | 6.88 | lap:houses (**true**: the quad really does clip a house) |
| gap 11, lateral +38.88 | 41.2 | 8.6 | 15.23 | - |

Only three of the thirty seats cleared everything, and all three are lateral `+38.88`. The nearest of
them won, was then pulled half its air toward the board (`pull_caption_toward`, feature 133 T40), and
that is the shipped seat.

**So nothing went wrong at the level the GM suspected.** The board was placed last, the caption was
seated immediately after it against the finished map, and the search did what it was told. The
search itself is what is wrong, in three separate ways:

### R2a - THE LATERAL LADDER IS DERIVED FROM THE CAPTION, NOT FROM THE SUBJECT

`lateral = _chw + hw + 6` - the caption's half-width plus the board's. For "notice board" at 8 pt
that is **38.88 px of slide along a 12 px board**. Sliding a caption along its subject is a real and
documented convention (`_best_label_spot`'s `slides`, and the along-feature rule for a river's name),
but there the slides are `span * 0.25` and `span * 0.4` - fractions of the SUBJECT. A slide of 39 px
along a 12 px plank is not "along the subject"; it is "away from it", and it is the whole defect.

### R2b - THE PERPENDICULAR LADDER STEPS OVER THE GOOD GROUND

Gaps `(11, 16, 21, 28, 36)`. At lateral 0 the board's south side is legal at gap **14** and at no
other sampled value: 11 fails the lane target by 1.1 ft, 16 and beyond genuinely clip a house.
A dense re-scan (gap 8..40 by 2, lateral -44..44 by 2, both sides, applying every rule the placer and
the gate apply) finds **97 legal seats**, the most centered of which is:

```
lateral 0.0, gap 14, below:  seat (2402.0, 573.7)   lane clearance 4.88 ft   structure gap 1.43 px   hug 9.0 px
```

which is directly below the board, and is the seat the GM is asking for. The ladder walked straight
over it. This is the same failure the LEVEL branch of this function already fixed once, and recorded
as *"DENSE ANNULUS, NOT FOUR RAYS ... four rays cannot serve two constraints at once"* - the fix was
never carried across to the tilted branch.

### R2c - THE STRUCTURAL PROBE MEASURES A BOX IT DOES NOT DRAW

`_blocked` builds the caption's TRUE rotated quad and then immediately collapses it to that quad's
axis-aligned bounding box. At -28.1 degrees a `53.8 x 10` px caption becomes a `52 x 34` px box - it
more than triples the caption's thickness. Measured consequence on the very seat under discussion:
`gap 11, lateral 0` is reported `lap:houses`, and its true quad clears the nearest structure by
**4.43 px**.

This is the defect this file's own neighbors warn about twice, in these words: *"an AABB standoff to
a diagonal subject is the caption's own length, not its thickness"*, and *"the placer and its check
must read one source; that is the oldest rule in this engine's CLAUDE.md and I broke it in code
written to enforce it"*. Fixed here under Principle XIV (a defect found in the course of the work is
fixed in that work).

## R3 - is there a general rule the gate can hold?

Measured across every caption in the pool that records a referent (16 of them), decomposed the same
way. Writing `lat` for the displacement along the caption's baseline, `capHalf` for the caption's
half-run and `subjHalf` for the subject's half-extent along that same baseline:

| map | caption | lat | capHalf | subjHalf |
|---|---|---|---|---|
| inashiro | notice board | 2.2 | 26.4 | 3.0 |
| kashikawa | notice board | -1.5 | 26.4 | 6.1 |
| **kuwabata** | **notice board** | **-35.6** | 26.4 | 6.5 |
| mizuguchi | notice board | -0.6 | 26.4 | 6.5 |
| sawada | notice board | 1.6 | 26.4 | 5.9 |
| minami | theater stage | 0.0 | 39.3 | 35.0 |
| nagahara | theater stage | 25.3 | 39.4 | 31.7 |
| tango | theater stage | 66.3 | 39.4 | 22.0 |
| tango | gate market (x2) | 57.5 | 30.2 | 22.3 |
| tango | Imperial Road | -76.2 | 42.9 | 4.3 |
| hirameki | theater stage | 96.9 | 39.4 | 52.5 |
| hoshizora | theater stage | 104.3 | 39.4 | 60.0 |
| hoshizora | Imperial Road | -42.9 | 42.9 | 17.6 |
| ubame | theater stage | -86.3 | 39.3 | 42.0 |
| ubame | caravan inn | 13.8 | 27.2 | 46.6 |

**TWO CANDIDATE RULES WERE PRICED, and the weaker one was rejected for having no teeth.**

- *Overlap*: `|lat| <= capHalf + subjHalf + air`. It is the natural general statement ("the caption
  and its subject must lie alongside each other"), and it **does not catch Kuwabata**: 35.6 against a
  bound of 32.9 + air. The five town/city `theater stage` and `gate market` captions sit at exactly
  `air = 5.0` past the bound, because `_best_label_spot`'s END directions seat a caption off the end
  of its subject at `LABEL_MIN_AIR`. A rule that passes the map the GM complained about is not a
  rule.
- *Centered on the subject*: `|lat| <= subjHalf + LABEL_MIN_AIR` - a caption may slide along its
  subject as far as the subject goes, plus the standoff air, and no further. Kuwabata: 35.6 against
  11.5, **FAIL**. Every other notice board in the pool passes with 6-10 px to spare.

**The centered rule is the one that states what the GM asked for, so it is the one implemented - and
it is scoped to the notice-board caption family, deliberately.** Applied to every family it would
also fail 8 town and city captions (`theater stage` x5, `gate market` x2, `Imperial Road` x2, per the
table), which are seated by a different placer (`_best_label_spot`) whose end-seats and long-subject
slides are documented, deliberate, and correct for a subject tens of times the caption's length.
Bringing them under the rule means reflowing the town and city tiers - a different feature, with its
own pool sweep and its own review. Recorded here so the next reader knows the exclusion is a priced
decision and not an oversight, and knows the exact number to beat.

## R4 - what a label PHASE changes, and what it must not

The hamlet pipeline already places the notice board LAST (feature 154, GM 2026-08-29), and the
caption is seated inline inside `kosatsuba`. So on a hamlet, moving the caption into a phase that
runs immediately afterward changes **nothing about what the seat search can see** - which is the
property that makes this refactor safe to land with the seat fix in the same feature: any caption
that moves, moved because of the seat rules, not because of the phase.

The tiers where it does change something are the hand-authored village, town and city scripts, which
call `s.kosatsuba(...)` in the middle of the script and go on placing features afterward. There the
caption will now be seated against the finished map. That is the GM's stated reason for wanting the
phase at all - *"how we place labels will always depend on what else is on the map"* - so it is the
intended effect, and those maps get a pool sweep and an independent review before anything lands.

**Sources:** none. No claim in this document is about the historical world; every number in it was
measured on this repository's own artifacts at commit `7aee251f` by the scripts recorded in the
task list. (Constitution XII asks for sources behind research FINDINGS; a measurement of our own
output is sourced by being reproducible, and the reproduction is the point.)

## R5 - what the fixed placer actually produces, and where the check's bound came from

Measured on the five scripted hamlets after the fix (`make maps`, whole tier, clean). `lat` is the
displacement ALONG the caption's own baseline - the axis the GM's complaint is about - and `bound` is
the rule's limit, the subject's own half-extent along that baseline plus `LABEL_MIN_AIR`:

| map | lat, before | lat, after | subjHalf | bound | headroom |
|---|---|---|---|---|---|
| inashiro | 2.22 | **2.22** | 3.0 | 8.0 | 3.6x |
| kashikawa | -1.53 | **-1.53** | 6.1 | 11.1 | 7.3x |
| **kuwabata** | **-35.6** | **-1.02** | 6.5 | 11.5 | 11.3x |
| mizuguchi | -0.63 | **-0.63** | 6.5 | 11.5 | 18x |
| sawada | 1.55 | **1.55** | 5.9 | 10.9 | 7.0x |

Only Kuwabata's caption moved materially; inashiro and mizuguchi were already seated centrally and
their manifests are byte-unchanged. Kuwabata fails the bound by a factor of **3.1** before the fix and
passes with 11x of headroom after it.

**THE BOUND IS REUSED, NOT INVENTED, AND NOT FITTED.** `LABEL_MIN_AIR` (5.0 px) is the engine's own
constant for the clear air that makes a caption read as "beside, but not touching". The rule it states
is one sentence - *a caption may slide along its subject as far as the subject itself extends, plus the
air it keeps across it* - and it is deliberately NOT tuned to the motivating map: fitting a general
rule to the single case that was easiest to measure is this repository's recurring defect, named as
such by a settlement-review three days ago (`sawada.notes.md`, the 4.5 ft remnant constant against an
11.4 ft remnant, *"the third instance on this one map's notes"*).

**The alternative that was priced and rejected** is in R3: the natural "the caption and its subject must
OVERLAP along the baseline" does not catch the map the GM complained about, because the caption is four
times the length of the plank it names.

## R6 - the legacy pool is FROZEN, which reverses one of the spec review's prescriptions

The round-1 spec review asked for two WORKAROUND hand seats to be removed so the corrected placer would
seat them - Minami's `place_punishment_spot(label_xy=(1270, 1454))` and Nagahara's
`kosatsuba(1492, 1341, rot=0, label_xy=(1530, 1329))`. Both were removed. Both removals were then
REVERTED, and the reason is a GM ruling the reviewer had no way to know about.

Minami and Nagahara are two of the 19 hand-authored maps the GM froze on 2026-08-16 (`dev/pool.md`,
`migration-plan.md` section 2): *"never regenerated, never re-gated ... The fix for a frozen map that
violates a post-freeze rule is CONVERSION, not retrofit - do not 'fix' a frozen map, and do not treat
its rule violations as bugs."* `make maps` confirms it in the artifact - the tier sweep rolls five
scripted hamlets and no legacy map at all - and `regen.py` prints `FROZEN` and skips.

So the edit changes nothing any reader will ever see, while desynchronizing an exhibit's source from
the manifest it shipped with. **Accepted**: Nagahara's city map keeps a notice-board caption 38.0 px
along its own baseline from its board. **What it costs**: one frozen exhibit displays the defect this
feature fixes. **The alternative priced**: converting Nagahara to scripted generation, which is a
feature of its own and would land the corrected caption for free. **Who chose**: the GM, on 2026-08-16.

The same ruling settles the eight referent-less board records the review flagged (`enokida`, `honda`,
`yatsuda`, `tanada`, `hirameki`, `minami`, `nagahara`, `tango`): every one is a frozen exhibit, so the
new check is scoped to `meta.generated_by` maps - which is not a dodge but the scoping every sibling
caption check already uses.

## R7 - the 48-seed cohort, measured three ways

Constitution XIII: a regression is measured, not remembered. The baseline was taken on unmodified
HEAD in a detached worktree; the two post-change runs differ only in whether the new check existed.

| run | passed | `labels_within_image` | `captions_clear_the_ways_they_stand_on` | `caption_stands_beside_its_referent` |
|---|---|---|---|---|
| BASELINE (unmodified HEAD, worktree) | **28/48** | 1 | 1 | - |
| the seat fix, before the check existed | **29/48** | **0** | 1 | - |
| the seat fix, with the check | **24/48** | 0 | 1 | 6 |

**The seat fix is a net GAIN and breaks nothing**: 28 -> 29, with one `labels_within_image` failure
fixed, `captions_clear_the_ways_they_stand_on` unmoved, and no check newly firing. Every other
residue line is identical seed for seed (10 `lanes_form_one_network`, 3 `farmhouses_reach_a_way`,
2 `features_do_not_overlap`, 2 `lanes_reach_something`, 2 `paddy_bunds_do_not_stagger`, 1 each
`village_windbreak_is_continuous`, `wells_clear_of_trees`, `lanes_bend_like_paths`) - all
pre-existing, none of them this feature's.

**The whole 29 -> 24 drop is the NEW RULE reporting maps that were already like that.** Six of 48
seeds seat a board caption further along its baseline than the board extends; one of the six was
already failing something else, which is why the pass count falls by five rather than six.

**A note on the baseline's own two caption failures**, because they are the reason the seat fix
counts as a gain rather than a wash: the pre-change engine shipped one caption outside the frame and
one on a lane tread across 48 seeds. The first is fixed by the denser ladder finding a seat the
coarse one stepped over. The second is unchanged - a different rule, on a seed where no seat clears.
