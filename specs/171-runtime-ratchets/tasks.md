# Tasks: Runtime Ratchets (feature 171)

Written by the `Diagram tooling` session, which is implementing this; the spec, request and research
are the `diagram-testing` session's, handed off at the GM's direction with a FAITHFUL verdict at
round 5. Every task is `research: procedure` - this is about what the tooling measures of itself.

**The handoff's five warnings are treated as constraints, not advice** (they were each learned by a
review round finding them wrong): the GM's two numbers are HARD CEILINGS the mechanism sits under and
the `min()` is not to be removed; the baseline is PINNED, never rolling; the comparison differs by
target and regime; D1 and D2 are the spec author's decisions and are the GM's to overturn, not mine to
quietly change; and FR-007 is OPTIONAL because `quick` already times itself inline.

- [x] T01 baseline: `make hooks-test` and `make done` green before any change
      research: procedure
      verify: both green, so anything red afterwards is this feature's

- [x] T02 FR-003 / FR-005: the ratchet TABLE - one row per target, carrying the pinned baseline, the
      GM's hard ceiling where one exists, the comparison mode, and whether it is armed. A new target
      is a row, not a new mechanism (FR-005); the FULL/AWS row is present and OFF (FR-006)
      research: procedure
      verify: the table is data, and a test reads it rather than restating it

- [x] T03 FR-004: the derivation, `min(HARD_CEILING, max(baseline + 4, int(baseline * 1.3)))`, with a
      test that it REPRODUCES the GM's own numbers at the baselines they reasoned from - 11 s -> 15 s
      and 35 s -> 45 s - which is the whole argument for trusting it on a target they never named
      research: procedure
      verify: both worked examples asserted, plus that the `min()` binds (a drifting baseline cannot
      buy a ceiling above the GM's figure - the defect round 2 of their review caught)

- [x] T04 FR-001: `make quick` FAILS at 15 s or more, measured on THE RUN ITSELF
      research: procedure
      verify: driven at 14 s (passes) and 15 s (fails) with an injected duration, not by waiting

- [x] T05 FR-002: `make done` fails at its ceiling, with ONE RULE PER REGIME - while the pinned
      baseline is above 35 s, the median of the last 25 green same-scope runs against the derived
      ceiling; once the baseline is 35 s or less, THE RUN ITSELF against the GM's fixed 45 s
      research: procedure
      verify: both regimes driven from a seeded run log; and the case the handoff flagged - a single
      45 s run against a 35 s median must FAIL rather than pass

- [x] T06 FR-009: only runs that DID THE WORK are compared, and like with like - a short-circuited
      `already verified`, a failed run and a different scope are not evidence about duration
      research: procedure
      verify: a seeded log containing each of those, asserting they are excluded

- [x] T07 FR-008: a failure SAYS WHAT TO DO, in the house style, naming the target, the number, the
      ceiling and the baseline it came from
      research: procedure
      verify: the message asserted, as `QUICK_BUDGET`'s already is

- [x] T08 FR-010: moving a pinned baseline in EITHER direction leaves a written reason at the point of
      change
      research: procedure
      verify: a test that fails if a baseline row carries no reason

- [x] T09 FR-007 is OPTIONAL and is DECLINED for now, with the reason recorded: `quick` writes no
      run-log entry (measured n=0 against `done`'s 337) but times itself inline, so the GM's 15 s bar
      does not need it. Revisit if a target needs the median comparison
      research: procedure
      verify: the decision recorded in this file and in the spec's Decisions section

- [x] T10 D1 and D2 are the spec author's decisions, not the GM's - carry them forward unchanged and
      surface both to the GM at close-out rather than silently adopting or altering them
      research: procedure
      verify: the close-out report names the 155 s interim baseline (giving 201 s) and the median
      comparison as decisions awaiting the GM

- [x] T11 the whole guard suite and the gate, green together, then the push
      research: procedure
      verify: both exit 0 on a CLEAN run. The run before it went red on `make-only` and the cause
      was mine: I edited `_hookmatch.py` while the gate was reading it. Second self-inflicted false
      red this session (169 R14 was the first, running suites beside a running gate)

## What this session decided, and what remains the GM's

**Mine, recorded here rather than in the handoff's spec, which is the other session's document:**

- **FR-007 DECLINED** (T09). `make quick` writes no run-log entry - measured n=0 against `done`'s 337 -
  but it times itself inline, so the GM's 15 s bar does not need one. Revisit when a target needs the
  median comparison. The handoff author agreed when asked.
- **The gate's ratchet runs AFTER the run is logged.** This run belongs in the median it is judged
  against, and a gate that failed without recording what it did would hide the number the next session
  needs to diagnose it.
- **Two defects fixed on the way** (Principle XIV): `_gatecost.py` hardcoded the mirror as `/diagram`,
  so a checkout elsewhere read the wrong tree's log and no test could isolate itself - my own FR-009
  fixture had a seeded log and still got the live median mixed in, which is a test quietly measuring
  production. And the median ignored scope, which FR-009 forbids.

**THE GM'S, and neither is adopted silently** - both are the handoff author's decisions, carried
forward unchanged and surfaced at close-out:

- **D1**: the 155 s interim baseline for `done`, which yields the 201 s ceiling in force today. It is
  an interim number standing in for a 35 s baseline that does not exist yet.
- **D2**: comparing the MEDIAN rather than the run while that interim regime holds, because at 201 s a
  per-run bar would fire on 28% of normal runs.

One thing the handoff author and I both got wrong, and the measurement that settles it: we each
suspected `done`'s historical medians had been measuring a suite that skipped work, because `make
tooling` was collecting ZERO tests until this session fixed it. **They were not.** `make done` ran
2317 passed / 2 skipped / 1 xfailed BOTH before and after that fix - the `-m tooling` breakage was in
the CLI filter only, and `done` never selected by that path. The narrower true statement, which is
worth keeping: the standalone `make tooling` target measured nothing, so anything citing THAT target
as evidence was reading a dead instrument. It does not touch `done`'s medians, and the 35 s the GM
wants to return to is not called into question by it.

Recorded because the inference was plausible, was made independently by two sessions, and was wrong -
and because the counts that disprove it took one grep of two log files.
