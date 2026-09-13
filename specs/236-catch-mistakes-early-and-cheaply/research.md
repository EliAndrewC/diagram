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
nothing; bare and double-quoted contexts both execute; every span in an UNQUOTED heredoc body executes,
and an apostrophe there is literal text rather than a quote) - counted **73 over 16,748 commands** on
2026-09-12. The window is the 60 most RECENT transcripts, so the count moves as sessions run: the same
day it read 74 over 16,767 after the unquoted-body fix. Its one disclosed over-count is a backtick inside a
`#` comment, which does not run but cannot be a deliberate substitution either. Run it with
`python3 specs/236-catch-mistakes-early-and-cheaply/measure_backticks.py`.

**What holds under all four walkers is that NONE is a deliberate command substitution.** Every span the
committed walker lists is a markdown code span or an identifier written into prose - `## Map notes`,
`close_seams`, `<name>.notes.md`, `[a-z0-9-]+` - and several would have done real damage had they run:
`cd /diagram` enters main's tree, `git init --bare`, `find`. Not one is a `date`-style substitution.

So an earlier draft's reason for only warning - that `"today is `date`"` is sometimes deliberate - is
contradicted by the data: zero under every walker. And this project writes deliberate substitution as `$(...)`. The
check REFUSES, naming `$(...)` and single quotes as the fix, which is the GM's own word: *"reject it
early"*. A backtick in an UNQUOTED heredoc body (`<<EOF`) executes the same way and is caught the same way.

## R9 - what the implementation itself measured (2026-09-12)

Three numbers came out of building the six checks rather than out of the record, and each is
reproducible by a command this feature ships.

**The frozen corpus, replayed through the hook** (`scripts/fixtures/bash-parse-corpus-2026-09.json`,
re-run by `scripts/test-shell-check-hooks.sh` on every gate, so these are the suite's own assertions
rather than a note):

| rule | of the 238 commands |
|---|---|
| refused by the PARSE | 2 - both of which had also failed at run time |
| parse false positives | 0 |
| refused by the `-m` ban | **23** |
| refused by the backtick rule | 0 |
| refused by the co-author rule | 0 |

The 23 are the finding worth keeping: nearly a tenth of one session's commands carried a `-m` message
with a newline or a nested quote in it, which is item 3's whole subject and had never been counted.
The backtick rule's zero on this corpus is consistent with R8 - the 74 executing spans are spread over
16,767 commands and 60 transcripts, so a 238-command window is expected to hold none.

**Every mechanism proved to fire.** Each of the thirteen was broken in place, its own suite run, and
the tree restored: per-edit writes, whitespace-insensitive anchors, the parse's own options, the
executing backtick, the `-m` ban, the co-author address, whole-file exemptions, moved lines, untracked
files, and each of `spec-lint`'s four checks. 13 of 13 went red.

**A backtick after an unquoted `#` does not run, and the guard does not refuse it.** The measurement
walker of R8 counts such a span (its one disclosed over-count); the GUARD walks comments and skips
them, because refusing `ls  # see \`make quick\`` would be a guard firing on correct work. The finding
R8 rests on is unaffected: a comment cannot hold a deliberate substitution either.

**The delta check found a class of file that must keep its British spellings.** Its first run over
this feature's own work named 43 hits, every one of them inside the frozen command corpus - several of
those 238 commands were house-style sweeps, so they carry the words by necessity. A fixture is a
verbatim record: correcting one would falsify it and break the measurement it reproduces. So
`scripts/fixtures/` is exempt in the check AND in the hook (spec D8).

## R10 - what correcting a Bash payload would rewrite (measured 2026-09-13)

The GM ruled that the hook should correct a Bash payload and warn only on the sed shape (`request.md`,
2026-09-13). A command is not an edit, so the ruling was priced before it was built:
`measure_bash_corrections.py` replays every unique Bash command in the last fourteen days of
transcripts - the session's own and its subagents' - through this hook. The script is committed and
re-runnable; `scripts/_hm_house.py` carries the rules it produced, each with a case in
`scripts/test_hooks_cases.py`.

**The prefilter writes its dashes by codepoint, and that is a finding rather than a detail.** Written
literally, they were corrected to hyphens by this very hook as the file was saved, which made the
prefilter match any command containing a spaced hyphen - an order of magnitude more commands, none of
which it could act on. The word table is read out of the hook for the same reason.

**The window** (as of 2026-09-13T02:16; it is a trailing fourteen days, so it sheds as well as grows
and a re-run will not reproduce these to the command). 552 unique commands carried a British spelling
or a forbidden dash: 352 a spelling, 200 a dash alone.

| the hook's verdict | commands |
|---|---|
| corrected | 181 |
| reported, left as typed | 53 |
| silent - every hit is a word the command only NAMES, or the write lands outside the project | 318 |

**What is reported rather than corrected, and what the rule actually knows.** Of the 53: **9** carry a
`sed` segment - the shape the GM named - **42** carry both spellings of one word with no `sed`
anywhere, and 2 are writes of the GM's own verbatim `request.md`, reported by a rule older than this
amendment. The 42 are the same thing written in Python, in an `_patch.py` anchor pair, in a table of
pairs.

It is worth being exact about what the predicate can and cannot see: **it recognizes the SHAPE of a
replacement pair, not the intent.** An independent replay in the amendment review found about half of
the both-carrying commands to be replacement pairs; the rest are quotations of source text, searches,
and prose that names both spellings - including, occasionally, a real violation, which is then
reported rather than corrected and still fails `make quick` if it reaches the delta. The hook's
message says which rule fired rather than asserting the command is a fix. Two other disclosed costs:
`sed` used to READ (`sed -n '104p' CLAUDE.md`) is reported, because the rule is the command the GM
named rather than a judgment about what that command does; and a narrower predicate - both spellings
within one statement - would keep every measured replacement pair, but it would miss a Python sweep
whose `old` and `new` are separate multi-line strings, so the wider one is kept.

**Three classes the first draft would have broken, each found by reading the replay rather than by
reasoning about it.**

- **A sweep's own word list.** A set of quoted spellings in a Python heredoc is the tool that FINDS
  violations; correcting it leaves a list of American spellings that matches nothing. A string whose
  whole content is one word is now a mention, exactly as a backtick span is in prose.
- **A search the segment-dropper did not recognize.** `! grep -qiE '<words>'` (the negation stands
  where the command should be), a searcher inside `$(...)`, a regex alternation in any language, and
  a dash inside a character class or a `$'...'` string. FR-007a's rule reaching the shapes it missed.
- **The session state directory.** Writes to `~/.claude/projects/<project>/memory/` were being
  corrected, and that index's own line format carries an em-dash. Outside the project, as `/tmp`
  already was (spec D10) - and judged by the command's WRITE TARGETS: judged by every path a command
  mentions, the exemption silenced the rule on a command that read the memory file and wrote a project
  file in one breath, and the first fix for that silenced nothing but corrected the memory write
  itself, because a heredoc writing the index names relative files in its own body.

**What the hook costs, measured over the same 552 commands**: median **0.067 s**, p95 0.266 s, almost
all of it Python startup. The range walk inside it was rewritten from a scan quadratic in held ranges
to a linear one, and the honest figure for that rewrite is: **nothing measurable on real commands**
(0.33 s against 0.31 s over the 60 longest commands the hook acts on) and 0.085 s against 0.035 s on
a synthetic command built to be dense in held ranges. The rewrite is kept because it is the better
algorithm and its selftest pins it, NOT as a measured saving; the 2.2 s per command that prompted it
was replay throughput while the container was running several test suites at once, which is a
measurement of the container rather than of the walk.

**The exemption is measured against the whole window, never against its own cases.** Two drafts of it
were wrong and both passed their tests. Reading write targets out of the raw command text changed 11
verdicts for the worse - 7 writes outside the project newly corrected (the `M=<path>; cat >> $M` shape,
and a heredoc body carrying a line that opens with `>`) and 4 project writes newly silenced (a
`write_text` into the pool, two commit messages, each beside a `> /tmp/....log`). Appending an
unknowable destination for every program heredoc then acted on **21** commands whose every resolvable
target was outside - 15 corrected and 6 reported - **7** of them the auto-memory index, which is the
harm D10 exists to prevent (measured by replaying that draft, the hook at `31ef2907^`, against the
shipped one over this window; the first figure came from a round that judged by the hook's own target
list and did not reproduce). With the targets read by `_hm_tree.walk` and D11's
ruling in place, the same replay against the pre-exemption hook changes **52** verdicts and none is
wrong in either direction: **0** outside-the-project writes newly acted on, **0** project writes newly
silenced. What D11 leaves is an upper bound rather than a defect: **27** commands in the window are
exempt while carrying a program heredoc that could in principle write anywhere, **8** of them writing
the auto-memory (where the exemption is certainly right). That replay is the check to re-run if this
exemption is ever touched again - a case file agreeing with the check that wrote it is this
repository's own recorded failure mode.
