# Feature 239 - measurable guards, and figures that are derived

**Created**: 2026-09-13
**Status**: ACCEPTED by the GM at the five-round cap (2026-09-13), round 5's items applied
**Input**: the GM's request, verbatim, in `request.md`

## Summary

Feature 236's second amendment - a hook change of 309 added lines and 18 removed (`m:amendment-guard-lines-added`) - took 208 minutes, and a census of
the session's own transcript says where (`research.md` R1): 78.9 min replaying a command window
(`m:amendment-replay-minutes`), 78.0 min idle behind five review rounds (`m:amendment-idle-minutes`),
29.3 min of model latency (`m:amendment-latency-minutes`), 15.0 min of tests
(`m:amendment-test-minutes`). The GM asked whether
more tooling would fix that. The record says yes for three of the four blocks, and names the reason
in each case:

- **A guard's decision cannot be called.** 275 of `house-style-hooks.sh`'s 367 lines are a Python
  program inside a shell string (`m:house-style-program-lines`, `m:house-style-file-lines`), so
  measuring it costs a process per command - 144 ms against 7.0 ms in process
  (`m:decision-spawned-ms`, `m:decision-in-process-ms`), 80 s against 3.9 s over the frozen window
  (`m:window-spawned-s`, `m:window-in-process-s`; `research.md` R3).
- **Nothing freezes the window.** Nine passes each rebuilt the same list of 560 commands
  (`m:frozen-window-commands`), and two ran against a prefilter this very hook had corrupted
  (`research.md` R4).
- **Half the review findings were arithmetic.** Ten of twenty were a figure stale, unreproducible, or
  measured one way and stated another, and the last two rounds found three figures and two stale
  sentences between them (`research.md` R2). The reviewer wrote its own harness in four of the five
  rounds to check figures it had been handed (`research.md` R5).

The GM added a fourth item as a question: should a reviewer refuse to adjudicate figures handed to it
directly, and demand the measurements with the command that produced them? **The record answers yes**,
with one narrowing - a figure that genuinely cannot be re-run stays legal and is labeled (D2).

## Functional requirements

### A. A guard's decision is a function (FR-001 to FR-003)

**FR-001** The house-style decision MUST move out of the shell string into an importable module
exposing one entry point that takes the hook payload and returns the verdict - silent, corrected (with
the new payload), reported (with the message), or blocked (with the refusal). `house-style-hooks.sh`
MUST become a thin wrapper: read stdin, call it, print, log, exit. The word table and the replacement
pairs MUST live in the module, and `scripts/check-house-style-delta.py` MUST import them rather than
regexing them out of the shell file as it does today.

**FR-002** The move MUST change no verdict. Its proof is two-sided: the guard's own 43 cases pass
unchanged, and every command in the frozen window (FR-004) gets the same verdict before and after,
with the diff printed and empty.

**FR-003** ONLY the house-style guard moves under this feature. The census found inline Python in 15
guard scripts, 25 counting the test scripts, and its table of line counts is `research.md` R4 - the
candidate list, written by a command rather than by hand; each later
conversion is its own change with its own before/after diff. A sweep of all fifteen in one feature
would be fifteen chances to change a verdict silently.

### B. Measuring a guard is cheap (FR-004 to FR-007)

**FR-004** A frozen corpus of real commands MUST live in `scripts/fixtures/`, built from the recent
transcripts by a committed command and named with the date it was taken. It ships with this feature:
560 commands (`m:frozen-window-commands`), 2.7 MB of text (D6). Its prefilter MUST write its
dashes by codepoint, because the literal ones were corrected to hyphens by the hook as the script was
saved, which inflated one window by an order of magnitude (`research.md` R4).

**FR-005** `make hookbench GUARD=<name>` MUST replay that corpus through the guard's decision IN
PROCESS and print the verdict counts. Over the frozen window this is 3.9 s where the spawning form is
80 s (`m:window-in-process-s`, `m:window-spawned-s`; `research.md` R3).

**FR-006** `make hookbench GUARD=<name> AGAINST=<git-ref>` MUST print the VERDICT DIFF against that
ref - every command whose verdict changed, in both directions, with its targets. This is the check
feature 236's exemption owed and did not have: two drafts of it passed their own cases while changing
11 real verdicts for the worse.

**FR-007** The bench MUST refuse a guard whose decision it cannot import, naming FR-001, rather than
silently falling back to spawning - a fallback would make the 21x cost invisible again
(`m:decision-spawn-ratio`).

### C. A measured figure is derived, not typed (FR-008 to FR-011)

**FR-008** A feature's measured figures MUST live in `specs/NNN-*/measurements.json`, written by the
harness rather than by hand. Each entry is named by a KEY - lower-case kebab, unique in the file -
and carries the value, its unit, the command that produced it, the date it was taken, and optionally a
note - and optionally `quantity`, what was measured in words, including the sample it was taken over.
A prose figure points at an entry by writing `m:<key>` in its own paragraph, the way a research
pointer is written today. (`quantity` comes from feature 240, which found its own canopy failure was a
right number for the wrong quantity; two of this feature's measurements failed the same way - a ratio
taken over a biased sample, and an entry saying "over all 560 commands" that had sampled three.)

**FR-009** `spec-lint` gains a fifth CHECK - a new check rather than an extension of check 1, because
these checks are numbered and tested one at a time. A figure with a unit MUST carry an `m:<key>`
pointer in its paragraph, and check 5 MUST fail when the pointer is missing, when the key is absent
from `measurements.json`, or when the recorded value does not appear in the paragraph.

**FR-009a** "Appears in the paragraph" MUST be decided NUMERICALLY, never by string containment: the
paragraph must hold a number token which, with thousands separators stripped, equals the recorded
value - or equals it rounded to the decimal places that token itself shows, so a paragraph may write
`164` for a recorded 164.2 and `1,034` for a recorded 1034.

**FR-009b** Check 5 MUST reach where the stale figures actually stood: the operative sections check 1
names, AND `research.md`, AND the Review history. Seven of the ten in the record stood in `research.md`
or a Review history entry (`research.md` R2), neither of which check 1 reads. A figure in a Review
history entry MAY carry a round label instead of a key - `on round N's own run` - because that section
exists to record what a round measured at the time; a bare figure there fails.

**FR-009c** A figure being NAMED rather than ASSERTED MUST NOT be asked for a key: check 5 MUST skip a
figure inside a BACKTICK SPAN, exactly as the house-style corrector does. `research.md` R2 quotes one
of the findings it classifies as "a `2.2 s` that was never measured", and that span is the whole of
what the motivating case needs - R2's other figures carry no unit and were never figures under D4.
An author-declared exemption - a section saying in prose that it narrates - MUST NOT be added: it has
no decidable marker and any section could opt out of the check by writing a sentence. Where a whole
section genuinely narrates, it is exempted BY HEADING, the way `spec-lint` already exempts Decisions
recorded and Review history from check 1.

**FR-010** A ONE-SHOT observation MUST stay legal, labeled with the date it was observed and the
method, and check 5 MUST accept it. The class is NARROW: something no command can produce - a
container state, a wall-clock span with no transcript behind it. It is NOT a count over a moving
window: the frozen corpus of FR-004 makes that re-runnable, so it owes a key, and every disputed
figure in the motivating incident was exactly that (`research.md` R2). Too tight and the rule fires on
correct work, which teaches sessions to bypass it; too wide and it permits what the GM asked to stop.

**FR-011** `make figures` MUST re-run every recorded command in a feature's `measurements.json` and
report any value that moved, in the manner of `make notes-census`.

**FR-011a** A TIMING does not repeat exactly, so an entry MAY carry `varies` - and the band MUST be a
number on the entry, not a judgment at check time: `varies: <fraction>`, defaulting to 0.10 when it is
written as `true`. `make figures` MUST accept a re-measured value within that fraction of the recorded
one and report anything outside it. The band belongs to `make figures` ALONE: check 5 re-measures
nothing, and a prose figure keeps FR-009a's rule - equal to the recorded value, or equal to it rounded
to the decimals the prose shows - so a band can never let prose say one number for a recorded other. Without a band a clean tree could never be silent
(`m:timing-run-to-run-drift-pct`, `research.md` R3: 3.4%, inside the default, recorded under the FR-011c override at load
1.47 to 2.52); without a NUMBER, a session sets the band at check time and the
check becomes unfalsifiable for every timing.

**FR-011b** WHICH entries may carry it is decided by the UNIT, not by the author: an entry whose unit
is a duration (`ms`, `s`, `min`, `h`), a percentage derived from durations, or a ratio (`x`) MAY carry
`varies`; an entry whose unit counts things (`commands`, `files`, `lines`) MUST NOT, and `spec-lint`
MUST refuse one that does. A count repeats exactly or the thing counted changed: 560 commands is 560.

**FR-011c** A harness that records a TIMING MUST record the machine's one-minute load average on the
entry, and MUST REFUSE to record while that load is above a stated quiet threshold unless explicitly
overridden - in which case the load stands on the entry for a reader to judge. The threshold itself
is a GUESS and is owed: the harness uses a one-minute load average of 2.0, chosen rather than measured,
and this FR is its single home - feature 240 defers to it rather than keeping a second. **The rule is a
PRECAUTION, not a finding, and the record says so.** No measurement in this feature shows contention
moving a timing: the doubling first offered as evidence came from the same three-command sampling bug
FR-011e names, and a review reproduced it on a quiet machine. The container is shared, so the rule is
kept; if evidence is wanted, it is owed as a keyed measurement, not an anecdote.

**FR-011d** `make figures` REPORTS a moved timing; only a moved COUNT fails. A timing is a property of the
machine as well as the code, so a gate that failed on one would fail on correct work, which is how a
guard teaches sessions to bypass it. The band of FR-011a is what separates "moved" from "the same
figure again", not a pass/fail line for the push.

**FR-011e** A harness MUST record the SAMPLE it measured in the entry's `quantity`, and a harness's
argument parsing MUST NOT let one option's value be read as another's. Both are the same failure
observed in this feature's own record: `--repeat 3` was parsed as a sample size of three, the entry
was written as if it covered the whole window, and two successive explanations of the resulting
numbers - path growth, then contention - were wrong before a review found the sample in the note.

### D. A reviewer does not adjudicate a figure it cannot re-run (FR-012 to FR-014)

**FR-012** `.claude/agents/spec-fidelity.md` MUST carry the contract the GM proposed: where a round's
changed passages state measured figures, the reviewer verifies them by RE-RUNNING the recorded command
from `measurements.json`; and where a figure has neither a key nor a one-shot label, the round returns
**NOT-REVIEWABLE**, naming those figures, before reading anything else. A NOT-REVIEWABLE return does
NOT consume one of the five rounds the cap counts - nothing was reviewed - and the session records the
figures and re-dispatches.

**FR-013** The refusal MUST NOT stop the reviewer measuring independently when it wants to. The ten
stale figures in the record were caught by a reviewer that re-derived them from scratch
(`research.md` R5), and that instinct is the reason the rounds were worth their time. What the
contract removes is the reviewer having to REBUILD a harness to check arithmetic; what it keeps is the
reviewer distrusting the number.

**FR-014** The review-task shape in `.specify/templates/tasks-template.md` MUST name the measurements
file and the refresh command in the dispatch, so the reviewer is given the route rather than asked for
it.

## Success criteria

**SC-001** (FR-001, FR-002) The house-style decision is importable and called by the wrapper; the 43
cases pass unchanged; `make hookbench GUARD=house-style AGAINST=<the commit before the move>` prints
zero changed verdicts.
**SC-002** (FR-003) `research.md` R4 carries the census table, written by `measure/guard_census.py`
with its counting convention stated in the harness, and no guard but house-style is edited here.
**SC-003** (FR-004, FR-005) The corpus is committed with its build command and a date in its name; a
bench run over it completes in seconds rather than minutes, and the figure is recorded in
`measurements.json` rather than asserted here.
**SC-004** (FR-006) The bench, run against the commit before feature 236's exemption change,
reproduces that change's verdict diff - the same commands, in the same directions.
**SC-005** (FR-007) A guard with no importable decision is refused by name.
**SC-006** (FR-008, FR-009, FR-009a, FR-009b, FR-009c) A figure with no key fails `spec-lint`; a
figure in `research.md` and one in a Review history entry are both reached, and a Review history
figure labeled as that round's own run passes; a figure inside a BACKTICK SPAN does not fail while the
same figure outside one does, and no prose declaration exempts a section; `144` matches the recorded
`m:decision-spawned-ms` and `7` matches a recorded 7.0; a key absent from
`measurements.json` fails; a recorded value that does not appear in its paragraph fails; the correct
form passes - and this spec's own figures pass, as feature 236's FR-010b required of its author.
**SC-007** (FR-010) A one-shot observation with its date and method passes; the same sentence without
the label fails.
**SC-008** (FR-011, FR-011a, FR-011b, FR-011c, FR-011d, FR-011e) `make figures` is silent on a tree where every
timing was re-measured within its band, REPORTS a timing outside it, and FAILS on a count that moved;
`spec-lint` refuses a `varies` on an entry whose unit counts things; and a harness asked to record a
timing while the load average is above its quiet threshold refuses, names the load, and records only
when overridden - with the load on the entry; every timing entry names its sample in `quantity`; and
`--repeat 3` never sets the sample size.
**SC-009** (FR-012, FR-013, FR-014) The agent file carries the NOT-REVIEWABLE contract and the license
to measure independently; the tasks template's review task names the measurements file; a review
dispatched against a spec whose figures carry no keys returns NOT-REVIEWABLE naming them.
**SC-010** (spec-wide) Every mechanism is proven to FIRE by breaking it and watching a test go red.
**SC-011** (spec-wide) `make hooks-test`, `make quick` and `make done` are green.

## Decisions recorded

**D1 - one guard converts, not fifteen.** The census (`research.md` R4) makes a sweep tempting and the
sweep is exactly the wrong shape: each conversion owes a verdict diff over the window, and fifteen in one feature is fifteen chances to move a verdict unnoticed. House-style converts because it is the largest (275 lines, `m:house-style-program-lines`), the one
that cost the measurement time, and the one whose quoted-string form has
now broken twice on an apostrophe.

**D2 - a one-shot observation stays legal, labeled - and the class is narrower than the first draft
of this decision said.** The GM asked whether a reviewer should refuse figures given directly. Some
figures genuinely cannot be re-run - a container state, a span with nothing recording it - and a rule
with no room for those fires on correct work. But the first draft justified the class with "the
session ran 208 minutes" (`research.md` R1, `m:amendment-wall-minutes`), and that example is FALSE: this feature ships the command that reproduces
it, which the review demonstrated by running it. The draft also admitted "a count over a window that
has moved", which would have covered every disputed figure in the motivating incident - the thing the
GM asked to stop. So the class is: no command can produce it. A count over a moving window is made
re-runnable by the frozen corpus (FR-004) and owes a key like any other.

**D3 - the reviewer refuses rather than re-derives, and the GM's doubt is answered with the record.**
The GM offered this as spitballing. The record supports it: ten of twenty findings were arithmetic
(`research.md` R2), and in four of five rounds the reviewer rebuilt a harness to check numbers
(`research.md` R5). The risk of the rule is that a reviewer stops thinking about whether a figure is
TRUE because it can see it was recorded; FR-013 answers that by keeping independent measurement
explicitly welcome. The cost of NOT having it is measured: between them, rounds 4 and 5 of
feature 236's amendment found three stale figures and two stale sentences, and no defect at all.

**D4 - check 5 keys on the definition check 1 already uses.** A figure is a number with a unit in the
operative sections. Widening it to every number would fire on ids and counts, which is the false
positive `spec-lint` was designed around in the first place.

**D7 - a review's CHANGES REQUIRED items are findings, and keying the contract on them is considered
and deferred to feature 240's format.** Feature 240's review found that a rule keyed on figures IN A
PROMPT is passed by leaving the numbers out. FR-012 has the same weakness in a weaker form: check 5 is
keyed on figures in the document, where omitting a figure removes the claim itself, but a reviewer
contract triggered by figures can still be dodged by writing fewer. The stronger trigger is the
finding - every item a round required has a record verifying it was applied. It is not built here,
because 240 is building a structured findings file for map reviews and a second format would split
the mechanism; and it is not added on the last round of this spec's initial review, where it would
land as an untested mechanism at the cap. When 240's format has been exercised, a spec round adopts
it. (Provenance: feature 240, 2026-09-13.)

**D6 - the corpus is committed whole: 2.7 MB of command text, 3.0 MB as the JSON on disk.** The window is 560 commands and the ten largest are
38-79 KB heredocs (`research.md` R4). Capping a command at 10,000 characters would keep 88% of them for 1.04 MB, and it
was rejected: the largest commands are exactly the ones that exercise the range walk, and a bench that
quietly drops them measures the easy half. The repository's `.git` is already 101 MB, so the price is
paid in a place that can afford it. (These figures are from `measure/freeze_window.py` and
`m:frozen-window-commands`.)

**D5 - the corpus is frozen with a date and refreshed deliberately.** A rolling window makes two runs
disagree for reasons that have nothing to do with the code, which is what made feature 236's figures
drift between rounds. Refreshing is a command a session runs on purpose, and the file name says when.

## Out of scope

- Converting the other FOURTEEN inline-Python guards (D1) - the census counts fifteen including
  house-style, which converts here; they are candidates with line counts in `research.md` R4.
- The model-latency block of R1 (29.3 min): it is turn structure, which the batching guard already
  governs, and no mechanism here would move it.
- The review rounds themselves. This feature makes their cheap findings impossible; it does not ask
  the reviewer for less.

## Review history

**ACCEPTED by the GM** (2026-09-13), at the five-round cap with round 5's three items applied: *"I
accept the spec as it stands, so please proceed."* The contract shape of section D - NOT-REVIEWABLE
returned before anything is read, not consuming a round - stands as written.


**Round 5** (`spec-fidelity`, MODE 3 VERIFY): CHANGES REQUIRED, three items, all applied, and the fifth
round of the initial acceptance, so the spec goes to the GM rather than to a sixth. Round 4's figures
were confirmed against a re-run. The consequential item was a FOURTH wrong attribution of one
measurement: FR-011c rested on a spawned timing said to have doubled under contention, and the
reviewer re-ran the three-command sample on a quiet machine and got the same figure - it was the
sampling bug all along. FR-011c keeps its rule as a stated PRECAUTION with no evidence behind it,
FR-011d gives its reason without a figure, and the history and both harness docstrings stop asserting
the contradicted cause. Also applied: a drift called "quiet" was recorded under the override at load
1.47 to 2.52, and now says so; and FR-011e had absorbed FR-011d's closing sentence and miscounted its
own list. The reviewer's closing judgment, for the GM: every item in rounds 4 and 5 is a figure or a
sentence failing the rule this spec writes, none concerns what the GM asked for, and item 1 was found
only because the reviewer re-ran the harness - which is section D's argument, made on this spec.


**Round 4** (`spec-fidelity`, MODE 3 VERIFY): CHANGES REQUIRED, four items, all taken, and FR-011c and
FR-011d judged IN SCOPE - recording the load is part of "how they were generated", and the severity of
a moved figure is FR-011 finally saying what it means. The round's main finding was the one this
feature exists to end, standing in its own record: the drift runs had overwritten the headline entries,
so the Summary, FR-005, FR-007, SC-006 and R3 all stated figures their own cited keys denied. Chasing
that found the cause, and it was not the one I had written down: the harness read the `3` in
`--repeat 3` as its sample size and timed the three longest heredocs, which the entries' own notes
said. That is now FR-011e, and the harness records its sample in `quantity`. The run was repeated under the FR-011c override at load 1.47 to 2.52, and the figures
reconciled to it (`m:decision-spawned-ms`, `m:timing-run-to-run-drift-pct`);
its drift falls inside the default band, so FR-011a stands. Also taken: the band belongs to `make
figures` alone, never to check 5, which keeps FR-009a's exact rule; FR-011c's evidence is labeled as
the one-shot observation it is; and the load is recorded at both ends of a run, after a quiet start
and a contended finish refused a clean measurement.


**Round 2** (`spec-fidelity`, MODE 3 VERIFY): CHANGES REQUIRED, six items, all taken, and every one of
them this spec failing to keep the rule it is writing. The two that mattered: R1's figures were
reproducible and unkeyed while `time_census.py` could not record at all, so under this spec's own
FR-010 they owed keys - the census takes `--record` now and R1 points at five; and `decision_cost.py`
extrapolated from a TYPED constant (`window = 558`) over a corpus under `/tmp` that no committed
command built, so its recorded figures could not be reproduced on a clean tree at all. FR-004's frozen
corpus was therefore built early, and the harness reads it and derives the window size from it. That
re-measurement moved the headline - on round 2's own run - to 145 ms against 7.0 ms and **21x**, where
the earlier sample said 231 / 6.2 and 37x - and the reason is worth keeping, so R3 now records it: the ratio depends on the
command mix, and the first sample was biased toward the short commands the guard acts on. Also taken:
D1 still quoted the retired 273; SC-006 claimed this spec's own figures pass when only one paragraph
carried a pointer; check 5 as specified would have fired on `research.md` R2, which NAMES figures it is
classifying (FR-009c); and `make figures` had no tolerance for a timing, which cannot repeat exactly
(FR-011a).

**Round 1** (`spec-fidelity`, full reading): CHANGES REQUIRED, ten items, all taken, eight of them
figures - in a spec whose subject is figures that restate themselves. The answer was to build the
harnesses rather than retype the numbers: `measure/` carries four now, and every figure they produce
is a key in `measurements.json`. What they corrected: 15 guard scripts with inline Python rather than
16, house-style at 275 of 367 rather than 273 of 366, and the change this feature is about at 309
lines added rather than "about 40" - understated sevenfold, in the direction that made the argument
stronger. The sharpest item was on the GM's own idea: D2 justified keeping one-shot observations legal
with "the session ran 208 minutes, which no command can re-run", which is false - this feature ships
that command - and it admitted "a count over a window that has moved", which would have covered every
disputed figure in the motivating incident. D2's class is now what no command can produce.

**Round 3** (`spec-fidelity`, MODE 3 VERIFY): CHANGES REQUIRED, four items, all taken, and two of them
were the spec disagreeing with its own research table - D1's body and the Out of scope line still
counted sixteen and fifteen where the census says fifteen including house-style, so fourteen remain.
The other two were holes a session could drive through: FR-011a required a tolerance band without
saying what it is or where it lives, so any later session could mark any entry `varies` and make check
5 unfalsifiable for every timing (the band is a number on the entry now, with a default, and FR-011b
decides by UNIT which entries may carry one); and FR-009c bundled the decidable backtick-span rule
with an author-declared "this section narrates" exemption that has no marker and that any section
could claim - the second is deleted, and a whole section that genuinely narrates is exempted by
HEADING, the way `spec-lint` already exempts Decisions recorded from check 1. The round also priced
the corpus decision to the digit (88% under a 10,000-character cap for 1.04 MB) and confirmed that
building the corpus at spec stage is measurement data rather than implementation.

**What round 3 set off, which is now FR-011c to FR-011e.** Answering its tolerance item meant
measuring the run-to-run drift, and the runs came back far off. I attributed that three times
before the record showed the cause: first to the program growing `sys.path`, written into a docstring
as fact; then to another session rolling a map at the time; and finally, correctly, to the harness
reading the `3` in `--repeat 3` as its sample size and timing the three longest heredocs in the window.
Round 4 found "over 3 frozen commands" in the entries' own notes, and round 5 reproduced the figure the
second explanation had blamed on contention, on a quiet machine. So the rules are three: a timing
records the load and refuses above a threshold, kept as a precaution with no measured evidence behind
it (FR-011c), `make figures` reports a moved timing while only a moved count fails (FR-011d), and an
entry records the sample it measured while no option's value can be read as another's (FR-011e).
