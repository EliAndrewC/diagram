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
| 3 | `git commit -m "...said \"the pond's own center\"..."` - inner double quotes ended the string, producing a cascade of bogus pathspecs | **PARTLY, and only by accident** - the misquoted `-m` class parses cleanly unless a LATER character happens to break it. This instance was refused by `bash -n` (R6) only because the `(` in a later trailer's `(1M context)` fell outside the prematurely closed quote. Remove that `(` and it parses. Banning `-m` for quote- or newline-carrying messages kills the class rather than relying on the accident |
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

The GM asked for the British-spelling check "in, for example, our quick tests". Measured before specifying it, matching EXACTLY the way the house-style hook matches: the 44 words of
`BRIT` in `scripts/house-style-hooks.sh`, each word-bounded and CASE-INSENSITIVE - the hook tests
`re.search(rf"\b{w}\b", visible, re.I)`, so `CENTRE` and `NEIGHBOUR` in an engine comment are hits. The
command, flags included:

```
git grep -nIiE '\b(<the 44 words of BRIT, longest first, joined by |>)\b' -- . ':!.clones' ':!specs/236-*'
```

It returns **192 lines in 83 files**. (Earlier drafts said 146 from an ad-hoc list nobody recorded, then
161 from a case-SENSITIVE run - neither matched what the hook matches, so "the hook, the check and the
ledger agree on one list" was false while the list was shared and the matched set was not.)

**So a tree-wide check would fail on the day it landed**, and the feature would silently owe a sweep of
83 files that the GM did not ask for. The check is therefore scoped to the DELTA - the lines this push adds
or changes - which is also the only scope that would have caught the failures that motivate it, since
every one of them was new text.

**The pre-existing set is LEDGERED, not fixed** (Principle XIII: a pre-existing failure stays ledgered and
is not fixed under someone else's feature). By area, from `git grep -lIiE` - the same pattern and the same
exclusions - so this table and the count above come from one run:

| area | files |
|---|---|
| `.claude/skills/diagram/tests` | 25 |
| `specs` | 24 |
| `.claude/skills/diagram/l7r` | 7 |
| `.claude/skills/diagram/research` (hits inside 「」 quotations - exempt) | 7 |
| `scripts` | 5 |
| `.claude/skills/diagram/legacy-hand-authored-pool` | 3 |
| `.claude` | 2 |
| `.claude/skills/diagram/dev` | 2 |
| `.claude/skills/diagram/future-work` | 2 |
| `.claude/skills/diagram/pool` | 2 |
| `.specify` | 2 |
| `CLAUDE.md` | 1 |
| `docs` | 1 |
| **total** | **83** |

Zero of them are in `specs/*/request.md` under the same case-insensitive match, which is the one place
Principle V forbids touching - checked, because a check that corrected the GM's own words would be worse
than no check.

A sweep of them is its own work and wants the GM.

Zero of the 161 are in `specs/*/request.md` (re-checked against the hook's table), which is the one place Principle V forbids touching - checked,
because a check that corrected the GM's own words would be worse than no check.

## R5 - the withdrawn-figure check, and why it cannot reach outside `specs/`

The failure it aimed at is real and documented: feature 234's withdrawn measurement survived in five
shipped places. But the rule as first specified fails in both directions, and the review of this spec
demonstrated both against feature 234 itself:

- **It would not have caught its own motivating case.** All five surviving places were OUTSIDE `specs/` -
  two skill `CLAUDE.md` files, the root guard table, a script docstring, a research HTML page. A rule
  confined to a feature's own spec directory does not reach any of them.
- **It fires on correct work.** Feature 234's `spec.md` legitimately narrates "22 ft" and "6.7 m" in at
  least six places outside the withdrawing line - in decision records and review history, which is exactly
  the behavior this project requires of a decision that was reversed.

**So the check is KEPT, redesigned, and bounded** (spec D5, FR-010 check 2). The two faults are fixes to the first design, not reasons to deliver nothing: narration is exempted by SECTION (Decisions recorded and Review history exist to narrate a reversal), and the marked text must be at least twelve characters and contain a letter, so a bare number cannot be banned. What it still cannot reach is text outside `specs/` - where all five of feature 234's survivals were. Reaching that is a tree-wide scan, a different mechanism from the `spec-lint` approved, and that limit is recorded rather than solved.


## R6 - `bash -n` replayed over every command this project actually ran (measured 2026-09-12)

The prior session's transcript holds **238 Bash commands** that the tool executed. Each was replayed
through `bash -n` and, where it was refused, checked against the tool result it had actually produced:

| | count |
|---|---|
| commands replayed | 238 |
| refused by `bash -n` | **2** |
| of those, ALSO failed with a syntax error at run time | **2** |
| false positives | **0** |

So on the real corpus the check refuses exactly the commands that failed, and nothing that worked. Both
refusals would have saved the round trip their failure cost.

**The corpus does not contain every correct shape, and the review of this spec found one it lacks.** The
Bash tool runs bash 5.3 through `eval`, one line at a time, so `shopt -s extglob` on one line enables
`!(x)` on the next; `bash -n` parses the whole text first with extglob off and refuses it:

| | result |
|---|---|
| `bash -n` over `shopt -s extglob` then `ls !(x)` | **REFUSE** (a false positive) |
| `bash -O extglob -n` over the same text | pass |

So the check must parse with the options the tool's shell can enable, not with bash's defaults. A zero on
the replay is necessary and not sufficient; the replay corpus is the regression test and the extglob case
is added to it by hand.

## R7 - how anchor misses actually happen (measured 2026-09-12)

The prior session recorded **6** patch anchor misses. Read against the fix each one needed:

| anchor | what was wrong | fixed by |
|---|---|---|
| "sections and keys the new text was written from..." | spanned a line wrap | whitespace-insensitive matching |
| "Any distance function this feature ships MUST return 0" | spanned a line wrap | whitespace-insensitive matching |
| "the declined widening, without the draft" | the sentence was split across lines | splitting the edit at the wrap |
| "three worst sties stand 0.13, 0.03 and 0.08..." | the text had already been changed | a new anchor |
| "D6's open door (doctrine-unenforced..." | the text was never there | dropping the edit |
| "(see the Review history, round 4 of `settlement-review`..." | spanned a line wrap ("round 4 / of `settlement-review`") | whitespace-insensitive matching |

**Four of six were line wraps.** That is the measurement behind whitespace-insensitive anchors, and it is
also why the mid-session fix was the regex matcher every later patch used.

## R8 - backticks that PARSE and RUN (measured 2026-09-12)

The GM asked specifically about *"putting backticks in a place that they do not belong"* and *"some kind
of issue with commands that you are running involving backticks, which is knowable through static
analysis to be something that we don't want to do"*. `bash -n` cannot see the dangerous form, because it
is valid syntax:

| command | `bash -n` | at run time |
|---|---|---|
| `echo "use `make quick` first"` | **pass** | **runs `make quick`** |

Backticks inside double quotes are command substitution. The usual way they arrive in a session's command
is as a markdown code span written into prose - a commit message, an echo, a heredoc'd note - which is
exactly how this project's Makefile recipe-comment guard came to exist, after a comment executed
`make test-full` from inside `make test-full` and recursed 914 levels. That guard (`_hm_make.py
recipe_comment_hazards`) covers Makefiles only.

**Measured, and the part of the measurement that holds settles refuse-versus-warn.** Across the 60 most recent transcripts,
Bash commands were walked with a shell quote-state walker. **The COUNT depends on the walker, so it is not
the finding.** Round 3's walker counted 18 executing spans, this spec's first counted 42 (double-quoted
contexts only), round 4's rough walker about 100, and the walker now COMMITTED beside this file as the
record - `measure_backticks.py`, whose `selftest()` pins every rule it applies (single and ANSI-C quotes do
not execute; a heredoc delimiter quoted any of three ways makes its body literal; an escaped backtick opens
nothing; bare and double-quoted contexts both execute) - counts **73 over 16,748 commands**. Run it with
`python3 specs/236-catch-mistakes-early-and-cheaply/measure_backticks.py`.

**What holds under all four walkers is that NONE is a deliberate command substitution.** Every span the
committed walker lists is a markdown code span or an identifier written into prose - `## Map notes`,
`close_seams`, `<name>.notes.md`, `[a-z0-9-]+` - and several would have done real damage had they run:
`cd /diagram` enters main's tree, `git init --bare`, `find`. Not one is a `date`-style substitution.

So an earlier draft's reason for only warning - that `"today is `date`"` is sometimes deliberate - is
contradicted by the data: zero of 42. And this project writes deliberate substitution as `$(...)`. The
check REFUSES, naming `$(...)` and single quotes as the fix, which is the GM's own word: *"reject it
early"*. A backtick in an UNQUOTED heredoc body (`<<EOF`) executes the same way and is caught the same way.
