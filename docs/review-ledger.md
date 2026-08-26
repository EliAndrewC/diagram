# Review ledger - is each review subagent pulling its weight?

**The SESSION writes this, never the reviewer** (GM 2026-08-26: *"the reviewer itself should not be
what logs its findings because you might disagree with the reviewer. And the log entry should
indicate both what the findings were and whether they were actually acted upon"*). One row per
FINDING (errors, questionable items, nitpicks, and "caught nothing" as its own row), with the
session's disposition. Add the rows in the same commit that acts on the review. A pass that finds
nothing is still the verification the constitution requires; a run of passes that never catch what
the author missed - or that pass what the GM then rejects - is the signal to sharpen the agent
(root `CLAUDE.md` "Improving a review subagent").

Columns: **found** = what the reviewer reported; **author had missed?** = would the session have
shipped it; **acted on** = fixed / recorded-only / declined (with why) / MISSED-BY-REVIEWER (the GM
or a later pass found what this one should have).

| date | agent | subject (wall) | verdict | found | author had missed? | acted on |
|---|---|---|---|---|---|---|
| 2026-08-26 | settlement-review | Inashiro T11 footplanks (2.9 min) | pass | branch planks seat at the TAIL of the qualifying run, not the head | yes (mechanism unexplained) | recorded-only: position judged better than the head; mechanism written at the point of change |
| 2026-08-26 | settlement-review | Inashiro T11 footplanks | pass | one seat reads 1.95 ft against a >= 2.0 rule | yes | recorded-only: the reviewer measured linearly; `taper_w` (square-root) is authoritative and puts it >= 2.0 |
| 2026-08-26 | settlement-review | Inashiro T11 footplanks | pass | planked/unplanked twin ditches 12 ft apart | no (known pair geometry) | recorded-only |
| 2026-08-26 | settlement-review | Inashiro T12 round 1, hard marsh keep-out (2.1 min) | needs-work | ruled line + ~40 ft bare strip on the toe's straight west edge | YES - the author's crops had not shown it | fixed (round 2: soft keep-out) |
| 2026-08-26 | settlement-review | Inashiro T12 round 2, soft keep-out for all families (2.4 min) | pass | ramp asymmetry west vs north (~25 vs 46 px) | yes | recorded-only |
| 2026-08-26 | settlement-review | Inashiro T12 round 2 | pass | **MISSED-BY-REVIEWER**: pines and brush standing in the reeds along the 1,600 px north seam - the GM saw it on first look | (the author missed it too) | fixed (round 3: woody hard-excluded); became an agent rule, TDD-run against this render: the fit-zoom-first wording did NOT fire (still pass); the manifest-free PIXEL-COUNT wording fired (needs-work, 1,260 bases) and is the validated example |
| 2026-08-26 | settlement-review | Inashiro T12 round 3, woody hard / grass soft (5.0 min) | pass | caught nothing new; 2 nitpicks (notes entry pending; audit blind to wet ground wider than its polygon) | - | notes entry written; audit nitpick recorded-only (not the case on any current map) |
| 2026-08-26 | settlement-review (TDD, general-purpose adopting the definition) | Inashiro T12 round-2 render, rule attempt 1 "fit zoom first" (1.9 min) | pass | nothing (the rule did not fire) | - | rule rejected - no teeth; recorded in the agent's validated examples |
| 2026-08-26 | settlement-review (TDD, same) | Inashiro T12 round-2 render, rule attempt 2 "pixel count" (3.8 min) | needs-work | 1,260 scrub bases on marsh ink inside the frame; plus QUESTIONABLE: whether a reed margin historically carries woody scrub (research would settle it; band width a knob if both) | yes (round 3 had already fixed the ink; the research question is open) | rule kept as validated; the research question recorded-only in `research/vegetation.md` as the GUESS it already is |
