# Review ledger - is each review subagent pulling its weight?

One row per review pass (GM 2026-08-26: *"Do we keep a record of when the settlement review finds
things and when it doesn't?"* - until this file, only the per-map `.notes.md` catch-rate lines did,
which nobody could total). A pass that finds nothing is not a wasted pass - it is the verification
the constitution requires (Principle I) - but a run of passes that never catch anything the author
missed is the signal to sharpen the agent (procedure: root `CLAUDE.md` "Improving a review
subagent"; the agents live in `.claude/agents/`, and each is edited only with a motivating case).

| date | agent | subject | wall | verdict | caught (author had missed) | outcome |
|---|---|---|---|---|---|---|
| 2026-08-26 | settlement-review | Inashiro T11 footplanks | 2.9 min | pass | 3 record-the-why items (seat mechanism, taper measurement, planked/unplanked twin) | recorded |
| 2026-08-26 | settlement-review | Inashiro T12 round 1 (hard marsh keep-out) | 2.1 min | needs-work | REAL: ruled line + 40 ft bare strip on the toe's straight edge (second-order effect of the fix; the author's crops had not shown it) | fixed (soft keep-out) |
| 2026-08-26 | settlement-review | Inashiro T12 round 2 (soft keep-out, all families) | 2.4 min | pass | 1 nitpick (ramp asymmetry) | NOT CAUGHT: the GM then saw pines still standing in the bog along the 46 px seam - the reviewer measured the ramp and passed the form the GM rejected. Lesson for the agent: judge "does X overlap Y" from the GM's stated objection at fit zoom, not from the mechanism's own profile |
| 2026-08-26 | settlement-review | Inashiro T12 round 3 (woody hard, grass soft) | 5.0 min | pass | nothing new (2 nitpicks: notes entry pending, audit blind to wet ground wider than its polygon); judged at fit zoom first + a manifest-free pixel check; states round 2 was its own miss | recorded |
