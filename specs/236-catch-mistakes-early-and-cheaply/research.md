# Feature 236 - research and measurement

## R1 - where 201 minutes went (measured 2026-09-12, from this repository's own records)

The GM asked for a breakdown of a session that delivered features 233 and 234. Wall clock from the
session's own commit timestamps: **201 minutes over 43 commits**, 17:24 to 20:44 UTC. (The GM's estimate
was "thirty three minutes or more"; the real figure is six times that, which is itself why the question
was worth asking.)

Agent wall time, from the durations the completion notifications report:

| agent | runs | total min | mean min |
|---|---|---|---|
| **`spec-fidelity`** | **20** | **91** | 4.5 |
| `quote-check` | 2 | 17 | 8.6 |
| `source-reader` | 2 | 13 | 6.4 |
| `settlement-review` | 1 | 11 | 11.0 |
| `entry-drift` | 3 | 10 | 3.4 |
| `record-format` | 2 | 10 | 4.8 |
| `source-applicability` | 1 | 7 | 7.5 |
| **total** | **31** | **159** | |

159 agent-minutes inside a 201-minute session - overlapped with the session's own work rather than
serial, but the dominant cost by a wide margin.

**The gate was NOT the cost**, which is worth recording because it is where a reader would look first:
`make done` short-circuited or ran in ~70 s, `make page-check` ~10 s, `make hooks-test` skipped 19 of its
21 suites. Three days of work in features 213-221 took the gate off the critical path and it has stayed
off.

**`spec-fidelity` is 45% of everything.** Nine rounds on 233, eleven on 234. At least eight of the twenty
returned findings a mechanical check could have caught before the round was ever dispatched: a figure
stated with no method, a British spelling, a superseded paragraph still standing, a stale `tasks.md`, a
criterion demanding a number the spec never gave.

## R2 - the session's own rework, classified as system gaps rather than as carelessness

The GM's ruling on this is the feature's premise: *"anytime someone says, 'oops, that's embarrassing.
I'll just do better in the future', then a good engineer says, hold on. This might be a system designs
problem masquerading as a personal failing."* So each failure is classified by whether a cheap check
could have caught it.

| # | what happened | mechanically catchable? |
|---|---|---|
| 1 | Three patch scripts aborted on a cosmetic anchor and DISCARDED substantive edits alongside it (once silently losing seven good edits) | **YES** - the scripts accumulated substitutions in memory and wrote at the end, so any assert discarded everything. A helper that writes per edit makes the failure impossible |
| 2 | `sed -i 's/...GM's ruling.../'` - an apostrophe inside a single-quoted expression | **YES** - `bash -n` reports it as a syntax error in milliseconds, before the round trip |
| 3 | `git commit -m "...said \"the pond's own center\"..."` - inner double quotes ended the string, producing a cascade of bogus pathspecs | **PARTLY** - it is VALID bash doing the wrong thing, so `bash -n` cannot see it; banning `-m` for multi-line messages in favor of `-F -` kills the class |
| 4 | A placeholder address (`duplicate@anthropic.com`) landed in a `Co-Authored-By` trailer from a shell fallback branch that was never meant to run | **YES** - the expected attribution line is known and exact |
| 5 | Every British spelling introduced this session went unchecked | **YES, and the hole is already known** - see R3 |
| 6 | A commit landed on a red `page-check` | **YES but DECLINED** - mid-task commits on red are legitimate and sacred here, so a guard would fire on correct work, which is this project's stated bar for not building one |

## R3 - the guard hole this feature closes, already found once elsewhere

`scripts/house-style-hooks.sh` intercepts the `Edit` and `Write` tools and CORRECTS British spellings and
dashes in the text being written (feature 164). It never sees a file written by a shell command.

This session wrote almost every file through `python3 - <<'PY'` heredocs in Bash, so the corrector was
bypassed end to end: `centre` in a gate test, `licence` in a docstring, `neighbour's` and `travelling` in
spec prose, `centre` twice in registry write-ups that DERIVE onto a reader-facing citations page. Each was
caught later by a `spec-fidelity` round costing minutes, where the hook would have fixed it for free.

**This exact hole has been found and closed once before, for a different guard.** `make-only-hooks.sh`
refuses a guard file written from a shell command, and its message names the shape: *"Layer 3 only sees
the Edit and Write tools, so this route slips past it - the same ungated-sibling shape this feature exists
to close."* House style still has it open.

**And there is a live tension underneath it**, which this feature should state rather than leave for the
next session to rediscover: the root `CLAUDE.md` says to edit files with `Edit` rather than heredoc'd
Python, while this session ran under an instruction preferring Bash wherever Bash can do the job. Following
the second lost the first's guard.

## R4 - the tree is not clean, so a tree-wide style check cannot be the design (measured 2026-09-12)

The GM asked for the British-spelling check "in, for example, our quick tests". Measured before specifying
it: `git grep` over tracked files excluding `.clones/`, on the common British forms, returns **146 hits**.
They are spread across engine comments, docs, test names, `scripts/fixtures/`, a Makefile comment and four
research citations pages - and the citations hits are inside 「」 quotations, where the house-style rule
explicitly exempts them.

**So a tree-wide check would fail on the day it landed**, and the feature would silently owe a 100-plus
file correction sweep that the GM did not ask for. The check is therefore scoped to the DELTA - the lines
this push adds or changes - which is also the only scope that would have caught the failures that motivate
it, since every one of them was new text.

**The pre-existing set is LEDGERED, not fixed** (Principle XIII: a pre-existing failure stays ledgered and
is not fixed under someone else's feature). `research.md` is where it is listed by area; a sweep of it is
its own work and wants the GM.

Zero of the 146 are in `specs/*/request.md`, which is the one place Principle V forbids touching - checked,
because a check that corrected the GM's own words would be worse than no check.

## R5 - the `WITHDRAWN:` rule, priced and DROPPED from this feature

The failure it aimed at is real and documented: feature 234's withdrawn measurement survived in five
shipped places. But the rule as first specified fails in both directions, and the review of this spec
demonstrated both against feature 234 itself:

- **It would not have caught its own motivating case.** All five surviving places were OUTSIDE `specs/` -
  two skill `CLAUDE.md` files, the root guard table, a script docstring, a research HTML page. A rule
  confined to a feature's own spec directory does not reach any of them.
- **It fires on correct work.** Feature 234's `spec.md` legitimately narrates "22 ft" and "6.7 m" in at
  least six places outside the withdrawing line - in decision records and review history, which is exactly
  the behavior this project requires of a decision that was reversed.

A rule that would reach the real surface has to scan the whole tree, which is a broadening beyond the
`spec-lint` the GM approved. **Dropped from feature 236 and recorded here** with the measurement, so the
next session inherits the finding rather than the idea.
