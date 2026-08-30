# T08 - the FR-006 placer read, for every NEVER-FIRES candidate

The census produces a candidate; this read produces the ruling (feature 158, and the round-1 spec
review which cut the "soft-failing placer keeps its check" clause). Two outcomes only: **evidence that
the CURRENT placer is missed** reclassifies the check FIRING, or **no such evidence** and it is deleted.

**Nothing has been deleted.** T10-T13 are held pending the GM's ruling on the escalated spec.

Nine candidates, after the census's own defect was fixed (R7: two of the original eleven were an
artifact of indexed check names, not dead checks). Grouped by what the read found.

---

## A. PHANTOM - the name cannot be emitted at ANY scale (2)

These are not checks. They are entries in `tests/fixtures/gate_check_names.json` that the derived
registry (feature 109) produced by reading an f-string **without evaluating the branch guard around
it**. No manifest at any scale can make the gate emit them, so they cannot fail, cannot pass, and
cannot be made to fire.

| name | why it cannot be emitted |
|---|---|
| `village_has_no_headman` | `_seg_0243` reads `if scale == "village": pass; else: check(f"{scale}_has_no_headman", ...)`. The emitting branch requires `scale != "village"`, so the string `village_has_no_headman` can never be built. The `pass` is feature 141's retirement of `village_has_headman`, which left the name behind in the pin. |
| `capital_has_kosatsuba` | `_seg_0546`'s guard is `scale in ("town", "city", "village", "hamlet")` and the name is `f"{scale}_has_kosatsuba"`. `capital` is excluded by the guard, so that name is never built. |

**Measured, not reasoned** - the gate was run at all five scales and asked what it emitted:

    scale=hamlet   -> ['hamlet_has_no_headman']    ['hamlet_has_kosatsuba']
    scale=village  -> []                           ['village_has_kosatsuba']
    scale=town     -> ['town_has_no_headman']      ['town_has_kosatsuba']
    scale=city     -> ['city_has_no_headman']      ['city_has_kosatsuba']
    scale=capital  -> ['capital_has_no_headman']   []

**This corrects the round-3 spec review on one point, with evidence.** It argued `village_has_no_headman`
*"can be made to fire"* because `roll_village` is a live mixin serving that scale. The rule it argued from
is right and is what found this - **read the guard** - but the reading has to go one level further than
the scale: at village scale the segment takes the `pass` branch, so nothing is emitted at all. The review's
sibling example (`village_has_kosatsuba`, made to fire by a three-line hand-built manifest) is real and is
a different check, in a different segment, with no such branch.

**This is a DEFECT IN THE PIN, not only a census finding** (constitution XIV). Two names in the live
roster correspond to no reachable check, so every count this repository has published of "how many checks
there are" is two high. The fix belongs with the deletion (T10) and is held with it. The general form is
worth more than the two instances: **`registry_analysis` enumerates a dynamic check name across every
scale without evaluating the condition that guards it**, so any future `check(f"{scale}_...")` behind a
scale branch will mint phantom names the same way. Three segments build a name at runtime today
(`grep 'check(\s*f"' segments_*.py` is the whole population).

---

## B. TIER-DEAD - reachable, but only on a tier no generator can produce (3)

| name | read |
|---|---|
| `capital_has_no_headman` | `_seg_0243` has NO scale guard and emits on any non-village map. Reachable at capital scale, and only there. |
| `city_has_no_headman` | same segment, city scale. |
| `town_has_no_headman` | same segment, town scale. |

Feature 158 deleted the frozen town/city/capital exhibits on the GM's ruling - *"there is no reason to see
what would happen if we encountered a type of map, which is literally impossible to produce any longer"* -
and no scripted generator exists above the hamlet. So nothing can produce a manifest at these scales
today. Note what this is NOT: it is not the check being wrong, and it is not a placer guarantee. The
sibling `hamlet_has_no_headman` runs on every hamlet roll and passes.

The honest framing for the GM: deleting these three costs nothing today and costs a re-derivation when the
town tier converts to scripted generation. That is the same trade feature 158 already took, one tier down.

---

## C. KEEP - the read found a reason (4)

### `waivers_are_documented` and `waivers_are_live`

**These never fire BECAUSE the thing they guard is currently unused, and that is the argument for keeping
them, not against.** They are the two meta-checks that stop the waiver hatch rotting: a waiver must carry
60+ characters of actual reason, and must name a check that really failed on this map. Zero live maps
carry a waiver (R3), so neither has anything to judge.

`dev/gate.md` records that neither may itself be waived, *"or the hatch would swallow its own guard"*, and
that they exist so waivers *"rot loudly instead of accumulating into a map that is quietly exempt from
rules nobody remembers it was breaking"*. Deleting a guard on an escape hatch on the grounds that the
hatch is currently shut is the precise inversion of what the guard is for.

They are also not post-placement audits in the sense this feature is retiring: they check a DECLARATION a
person wrote, not a placer's output. Under the session's three-way reading they are engine-completeness
checks.

### `farmhouse_aspect_in_range`

Reachable and RUN on every scripted hamlet - `_seg_0285_099`, guarded to hamlet/village/town, needs >= 10
plain houses, which every live map has. It fails a farmhouse over 2.7:1 long-to-wide, on the grounding
that a minka lengthened by adding bays and never became a shed.

**The placer does not guarantee it; the margin is ~11%.** Measured on the live pool:

| map | plain houses | aspect min | aspect max | threshold |
|---|---|---|---|---|
| inashiro | 15 | 1.40 | **2.37** | 2.70 |
| kashikawa | 20 | 1.34 | 2.11 | 2.70 |
| kuwabata | 16 | 1.41 | **2.39** | 2.70 |
| mizuguchi | 12 | 1.44 | 1.99 | 2.70 |
| sawada | 19 | 1.36 | 2.31 | 2.70 |

And the mechanism explains the tightness: `consts.py` records that *"the nucleated path jitters a minka's
length to 1.35x"*, so a base near the top of the 1.3-2.5:1 norm plus a full-length jitter lands at the
threshold. This is a live guard on a real regression, not a re-measurement of a guarantee. KEEP.

### `waterward_strips_run_off_the_frame`

Added **2026-08-29** (feature 150 T55) after `settlement-review` found the defect it guards: the polder's
waterward reed strip was cut from "drawn to the canvas edge" to a `WATERWARD_DEPTH` band, and a band can
stop inside the frame, where the reader sees a straight line where wild water stops being wild. Its own
docstring names this engine's standing failure shape - *"a rule that cannot fire looks exactly like a rule
that passes"*.

It does not fire because the fix works: `WATERWARD_DEPTH = 280.0` against a tightest measured flank of 245
px of headroom. A check written last week to hold a specific regression, on a constant with a 35 px
margin, is the clearest possible KEEP. **What it owes is a scripted negative fixture** - it currently has
no artifact proving its teeth, which is the same gap `dev/gate.md` records for
`lanes_do_not_break_mid_run`.

---

## What the read did NOT find

**Not one of the nine is a bug in the placement algorithm.** The GM's framing anticipated two outcomes for
a firing check - a placer bug, or a fold into a trial-and-error placer - and the never-fires set produces
neither: two phantoms, three tier-dead, four live guards worth keeping. That is a finding about where the
value of this feature actually is, and it points at the 103 `FIRES-HAND-ONLY` rows rather than here.
