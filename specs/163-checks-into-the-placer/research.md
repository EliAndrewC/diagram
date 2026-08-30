# Research: what the check battery actually costs, and what already fires

Measured 2026-08-30 in `.clones/diagram-testing` at `c33315db`, before any change. These are the baseline
numbers the wrap-up reports and the floor the User Story 1 census has to beat. (An earlier draft said they
were what FR-011 and SC-005 measure against; both were removed at spec review as unrequested, and the
constitution's own perf bookends - not a requirement of this feature - are what guard a regression.)

## R1 - the per-map cost is small; the SURFACE is the cost

The GM's framing is that running the checks *"every time a map is generated instead of having it happen
when a thing is placed"* is the waste. Measured, the per-generation half of that is minor:

| what | measured |
|---|---|
| `make gate-manifest M=pool/hamlets/inashiro/inashiro.json` (full battery, one finished map) | **1.3 s** |

So retiring the battery buys ~1.3 s per map roll, against hamlet rolls that run tens of seconds. That is
real but it is not the argument. The argument is the surface the battery carries:

| surface | lines / count |
|---|---|
| `check_village/` source | **14,483 lines** (385 registry segments, 152 live check names) |
| its tests (`tests/check_village/`, `tests/gate/`) | **7,464 lines** - 23% of the whole 32,813-line test tree |
| frozen negative fixtures (`pool/regressions/`) | **105 manifests, 11 MB** |
| the placement engine the battery audits (`settlement/`, `hamletgen/`, `waterfields/`) | 38,153 lines |

**~22,000 lines of audit code plus 11 MB of frozen maps, against a 38,000-line generator.** That ratio
is the honest statement of the GM's point, and it is the number to carry into the User Story 2
discussion - not the 1.3 s.

**Sources:** none - this is a measurement of this repository, not a research finding. `wc -l` over the
trees named above; the gate timing is a single `make gate-manifest` run on an otherwise idle container.

## R2 - the floor for the never-fires census

A cheap static pre-count, to give User Story 1 a number to beat and to prove the census is not returning
an empty set (FR-005). This is NOT the census: it greps rather than executes, which FR-002 forbids as the
method, and it therefore both over- and under-counts. It is a sanity floor only.

| firing source | live checks with evidence |
|---|---|
| a frozen negative fixture in `pool/regressions/` naming it in `_regression.fires` | 76 of 152 |
| a name appearing in any file under `tests/` | 140 of 152 |
| a waiver declared on a live pool map | **0 of 152** |
| union of frozen + scripted negative fixtures | ~95 of 152 |

- **9 checks have no frozen fixture, no test naming them, and no waiver at all**:
  `capital_has_kosatsuba`, `capital_has_no_headman`, `city_has_no_headman`, `farmhouse_aspect_in_range`,
  `stream_end_anchored`, `stream_source_anchored`, `town_has_no_headman`, `village_has_no_headman`,
  `ways_clear_of_castle_moat`. Six of the nine are legacy-tier checks with no scripted executor at all
  (feature 158 deleted the frozen town/city exhibits that were their only possible subjects).
- **~57 checks have no NEGATIVE fixture of any kind** - nothing in the tree is known to make them fail.
  The gap between 9 and 57 is the difference between "no test names it" and "no test makes it FAIL",
  and closing that gap by execution rather than by grep is precisely FR-002.

So the census's candidate set is expected to land between **9 and 57**, and a census returning zero or
returning all 152 is a broken census, not a finding.

**Sources:** none - a measurement of this repository.

## R3 - no live map is exempting itself

Zero waivers are declared on the five live scripted hamlets. Every waiver in the repository belongs to a
frozen hand-authored exhibit. So on the live pool the battery is fully green with nothing suppressed,
which is what makes the GM's *"our automated checks are not catching anything in this exact moment"*
literally true today - and what makes "never fires" so weak a test on its own, since a battery that
catches nothing is what both a correct generator and a neutered battery produce.

**Sources:** none - a measurement of this repository.

## R4 - the constitution XIII regression baseline

Taken 2026-08-30 on UNMODIFIED code in a detached worktree (`git worktree add --detach /tmp/base163 HEAD`),
never a stash, per Principle XIII:

    /tmp/base163/.claude/skills/diagram $ make done
    2753 passed, 2 skipped in 144.51s
    gate green (reference settlement + non-map tests)

Zero pre-existing failures, so there is no ledger to carry and every failure after this point is this
feature's. The worktree carried no gitignored-artifact failures this time - the trap recorded on
2026-08-24 (2 such failures from missing pool PNGs) did not recur, because the tests that read renders
are in `tests/full/`, which `make done` deselects.

**Sources:** none - a measurement of this repository.

## R5 - the first firing census, before the suite sweep

`make firing-census` over the 5 live maps and the 105 frozen fixtures, 797 verdicts observed:

| verdict | count | meaning |
|---|---|---|
| `FIRES` | 40 | the current implementation makes it fail (all 40 from scripted-era fixtures; **zero live maps fail anything**) |
| `FIRES-HAND-ONLY` | 53 | only a hand-era frozen manifest makes it fail |
| `NEVER-FIRES` | 59 | nothing in the pool or the corpus makes it fail |

**This is NOT yet the answer, and the instrument says so** - the ledger's own header prints `NO suite
journal`. The proof that it matters is in the tree already: `gardens_clear_of_channels` reads NEVER-FIRES
here, and `tests/check_village/test_segments_04_homesteads.py` makes it fail from a hand-built manifest on
every run. That is exactly the FR-002 gap between "no artifact makes it fail" and "nothing makes it fail",
and closing it is T04's whole job. Read this table as the floor: 59 is the largest the NEVER-FIRES set can
be, and the suite sweep can only shrink it.

The static pre-count in R2 guessed the candidate set at 9-57 and the measured floor is 59 before the
sweep, which is inside the spirit of that band and above its top - the difference is that R2 counted a
NAME appearing in a test as evidence, and this counts a check actually being made to FAIL.

**Sources:** none - a measurement of this repository.

## R6 - the census with the suite sweep folded in: the answer to the GM's first task

`make firing-census-suite` - the 5 live maps, the 105 frozen fixtures, and the whole pytest suite run
with the gate's verdict journal on (2,767 passed, 162.8 s; 7 xdist workers each wrote a journal).
**1,029 verdicts observed.**

| verdict | before the sweep | after | meaning |
|---|---|---|---|
| `FIRES` | 40 | **40** | the CURRENT implementation makes it fail - every one from a scripted-era fixture |
| `FIRES-HAND-ONLY` | 53 | **101** | only a hand-era artifact or a hand-BUILT test manifest makes it fail |
| `NEVER-FIRES` | 59 | **11** | nothing in the repository makes it fail |

**The sweep moved 48 checks out of NEVER-FIRES, and that is the measurement that justifies FR-002.** A
census built on globbing `pool/` would have reported 59 dead checks; 48 of them are made to fail by a
test's inline hand-built manifest that no artifact glob can see. Had the census been built the cheap
way, this feature would have deleted 48 working checks.

The eleven with no firing evidence anywhere:

    capital_has_kosatsuba      capital_has_no_headman     city_has_no_headman
    farmhouse_aspect_in_range  stream_end_anchored        stream_source_anchored
    town_has_no_headman        village_has_no_headman     waivers_are_documented
    waivers_are_live           waterward_strips_run_off_the_frame

**Every one is a CANDIDATE, not a verdict** (FR-006, feature 158), and two of the eleven show why the
placer read is not a formality:

- **`waivers_are_documented` and `waivers_are_live`** are the two meta-checks that keep the waiver hatch
  from rotting - a waiver must carry 60+ characters of real reason, and must name a check that actually
  failed. They never fire because **no live map carries a waiver** (R3). Deleting them would remove the
  only guard on the escape hatch every other rule can be excused through, and it would do so precisely
  BECAUSE the hatch is currently unused. They are also the checks `dev/gate.md` records as deliberately
  un-waivable, *"or the hatch would swallow its own guard"*.
- **`village_has_no_headman`** is the case the round-3 spec review predicted before the census ran: it
  comes back NEVER-FIRES, and `roll_village` is a live mixin that still serves that scale, whose sibling
  `village_has_kosatsuba` is made to fire by a three-line hand-built manifest in the tree today.

And the two names the review used to break the "legacy tier" grouping both land where it said they would:
`ways_clear_of_castle_moat` is `FIRES-HAND-ONLY` (a test makes it fail - it has no scale guard at all),
not a tier casualty, and `gardens_clear_of_channels` moved from NEVER-FIRES to `FIRES-HAND-ONLY` on the
sweep, exactly as predicted when the gap was found.

**Sources:** none - a measurement of this repository.

## R7 - a defect in the census itself, found by doing the placer read

The FR-006 read (T08) starts by reading each candidate's segment body, and the first two it opened
invalidated two of the census's own rows. **Three checks build their name at RUNTIME and two of them
append an INDEX:**

    check(f"stream_source_anchored[{idx}]", ...)
    check(f"stream_end_anchored[{idx}]", ...)
    check(f"{scale}_has_no_headman", ...)

So what `check()` emits is `stream_source_anchored[0]`, and what `gate_check_names.json` pins is
`stream_source_anchored`. The census compared the two literally, found no match, and reported both stream
anchors as NEVER-FIRES - **while the gate fires them on every map that has a stream.** They were two of the
eleven names this feature was about to hand to a deletion task.

Fixed in `tools/firing_census.py` with `base_name()`, applied on both read paths (the artifact gate and the
suite journal), with a guard that goes red if a fourth dynamically-named check appears in a shape it
cannot normalize. Corrected counts:

| verdict | before the fix | after |
|---|---|---|
| `FIRES` | 40 | 40 |
| `FIRES-HAND-ONLY` | 101 | **103** |
| `NEVER-FIRES` | 11 | **9** |

**The lesson is the one this repository keeps re-learning, in a new costume.** `dev/gate.md`'s "MEASURE
WHAT THE RULE MEASURES" table collects nine defects that were each *"a correct measurement of a DIFFERENT
QUANTITY than the rule it was serving"*. This is the tenth: the census correctly measured "which PINNED
names appear in the verdict stream" when the rule it served was "which CHECKS fire". And it was caught the
way every one of those nine was caught - by comparing against a case with a known answer, not by reading
the code more carefully.

It is also the argument for FR-006 in one instance: the census's verdict was a candidate, the read was the
ruling, and the read overturned two of eleven.

**Sources:** none - a measurement of this repository.

## R8 - what the nine never-fires candidates turned out to be

Full read in [`placer-reads.md`](placer-reads.md). The summary, because it changes where this feature's
value lies:

| group | n | what it is |
|---|---|---|
| **PHANTOM** | 2 | `village_has_no_headman`, `capital_has_kosatsuba` - names the derived registry minted from an f-string without evaluating the branch guard around it. Unreachable at every scale, proven by running the gate at all five. Not checks; pin entries. |
| **TIER-DEAD** | 3 | `capital_has_no_headman`, `city_has_no_headman`, `town_has_no_headman` - reachable, but only on tiers feature 158 left without a single producible artifact. |
| **KEEP** | 4 | `waivers_are_documented` + `waivers_are_live` (they guard the escape hatch, and never fire precisely because it is currently shut); `farmhouse_aspect_in_range` (live on every roll, drawn max 2.39 against a 2.70 threshold - an 11% margin, not a guarantee); `waterward_strips_run_off_the_frame` (written last week for a settlement-review finding, holding a 280 px constant with 35 px of headroom). |

**Not one of the nine is a bug in the placement algorithm.** The GM's request anticipated two outcomes for
a check the audit catches - a placer bug, or a fold into a trial-and-error placer - and the never-fires set
produces neither. Whatever this feature is worth, it is not here: it is in the **103 `FIRES-HAND-ONLY`**
rows, where the question is whether a check proven only by a hand-BUILT test manifest counts as firing
"with our current implementation". That is the GM's call and it is the big lever.

**The PHANTOM group is also a defect in its own right** (constitution XIV): two names in the live roster
correspond to no reachable check, so every published count of "how many checks there are" is two high, and
`registry_analysis` will mint more the same way for any future `check(f"{scale}_...")` behind a scale
branch. The fix belongs with T10 and is held with it.

**Sources:** none - a measurement of this repository.

## R9 - the retirement, and the derivation defect it exposed (T09-T11)

The GM's ruling of 2026-08-30 (*"go"*, accepting the recommendation in `gm-request.md`) set the criterion:
`FIRES-HAND-ONLY` is NOT a deletion criterion. Only the genuinely dead go. **Five names, 152 -> 147.**

**T09, orphaned citations: none.** Grepped `research/`, `settlements/`, `buildings/`, `SKILL.md` and
`dev/` for all five names - zero hits, so no historical finding loses its only operative statement.

**T10/T11, what was actually removed, and how.** Not five deletions - two code changes:

- **`_seg_0243`** was rewritten from `if scale == "village": pass; else: check(f"{scale}_has_no_headman", ...)`
  to `if scale == "hamlet": check("hamlet_has_no_headman", ...)`. That retires four names at once - the
  phantom `village_has_no_headman` and the three tier-dead ones - and replaces a tier-keyed name with a
  CONSTANT, so this segment can never mint a name again. It also gains a `scales` guard it did not have
  (feature 145's benefit: the segment is no longer entered at four of five scales).
- **`registry_analysis._bases_of`** now expands `f"{scale}_..."` over the segment's OWN admitted scales
  instead of all five (`_DERIVATION_VERSION` 2 -> 3). That retires `capital_has_kosatsuba`.

**The second one is a defect in the derived registry, not a cleanup** (constitution XIV). The analyzer
already computed each segment's admitted scales - feature 145 added exactly that - and the tier-keyed name
expansion never consulted it. So a segment guarded `scale in ("town", "city", "village", "hamlet")` minted
`capital_has_kosatsuba`, a name no manifest at any scale can make the gate emit. **The two facts were
computed independently, in the same function, and never compared.** Any future `check(f"{scale}_...")`
behind a scale guard would have minted more the same way.

Worth stating plainly because it is the same shape twice in one feature: the census's own indexed-name bug
(R7) and this one are both **two correct computations that were never put beside each other.** Neither was
a wrong calculation.

Cost of the phantoms, before they were found: two names sat in the live pin, so every published count of
"how many checks there are" was high by two, and the firing census handed both to a deletion task as
though they were dead checks rather than names of nothing.

**Guards.** `tests/check_village/test_registry_derive.py` holds the frozen legacy oracle; two rows (0243,
0546) were hand-edited, `checks` only, with the reason in its docstring - the established procedure, and
the fourth such edit since feature 109. The census's own guard proves no dynamically-named check
normalizes to a name the pin does not carry.

**After the retirement:** 147 checks, 40 `FIRES`, 103 `FIRES-HAND-ONLY`, and **4 `NEVER-FIRES` - every one
of them a documented KEEP** (`farmhouse_aspect_in_range`, `waivers_are_documented`, `waivers_are_live`,
`waterward_strips_run_off_the_frame`). There is nothing dead left in the battery.

**Sources:** none - a measurement of this repository.
