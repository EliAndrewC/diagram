# Feature 239 - measurable guards, and figures that are derived

**Created**: 2026-09-13
**Status**: DRAFT (awaiting `spec-fidelity`)
**Input**: the GM's request, verbatim, in `request.md`

## Summary

Feature 236's second amendment - a hook change of 309 added lines and 18 removed (`m:amendment-guard-lines-added`) - took 208 minutes, and a census of
the session's own transcript says where (`research.md` R1): 78.9 min replaying a command window, 78.0
min idle behind five review rounds, 29.3 min of model latency, 15.0 min of tests. The GM asked whether
more tooling would fix that. The record says yes for three of the four blocks, and names the reason
in each case:

- **A guard's decision cannot be called.** 275 of `house-style-hooks.sh`'s 367 lines are a Python
  program inside a shell string, so measuring it costs a process per command - 231 ms against 6.2 ms
  in process, 129 s against 3.5 s over one window (`research.md` R3).
- **Nothing freezes the window.** Nine passes each rebuilt the same list from 1,034 transcripts, and
  two of them ran against a prefilter this very hook had corrupted (`research.md` R4).
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
conversion is its own change with its own before/after diff. A sweep of fifteen guards in one feature
would be fifteen chances to change a verdict silently.

### B. Measuring a guard is cheap (FR-004 to FR-007)

**FR-004** A frozen corpus of real commands MUST live in `scripts/fixtures/`, built from the recent
transcripts by a committed command and named with the date it was taken. Its prefilter MUST write its
dashes by codepoint, because the literal ones were corrected to hyphens by the hook as the script was
saved, which inflated one window by an order of magnitude (`research.md` R4).

**FR-005** `make hookbench GUARD=<name>` MUST replay that corpus through the guard's decision IN
PROCESS and print the verdict counts. Over the measured window this is 3.5 s where the spawning form
is 129 s (`research.md` R3).

**FR-006** `make hookbench GUARD=<name> AGAINST=<git-ref>` MUST print the VERDICT DIFF against that
ref - every command whose verdict changed, in both directions, with its targets. This is the check
feature 236's exemption owed and did not have: two drafts of it passed their own cases while changing
11 real verdicts for the worse.

**FR-007** The bench MUST refuse a guard whose decision it cannot import, naming FR-001, rather than
silently falling back to spawning - a fallback would make the 37x cost invisible again.

### C. A measured figure is derived, not typed (FR-008 to FR-011)

**FR-008** A feature's measured figures MUST live in `specs/NNN-*/measurements.json`, written by the
harness rather than by hand. Each entry is named by a KEY - lower-case kebab, unique in the file -
and carries the value, its unit, the command that produced it, the date it was taken, and optionally a
note. A prose figure points at an entry by writing `m:<key>` in its own paragraph, the way a research
pointer is written today.

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

**FR-010** A ONE-SHOT observation MUST stay legal, labeled with the date it was observed and the
method, and check 5 MUST accept it. The class is NARROW: something no command can produce - a
container state, a wall-clock span with no transcript behind it. It is NOT a count over a moving
window: the frozen corpus of FR-004 makes that re-runnable, so it owes a key, and every disputed
figure in the motivating incident was exactly that (`research.md` R2). Too tight and the rule fires on
correct work, which teaches sessions to bypass it; too wide and it permits what the GM asked to stop.

**FR-011** `make figures` MUST re-run every recorded command in a feature's `measurements.json` and
report any value that moved, in the manner of `make notes-census`.

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
**SC-006** (FR-008, FR-009, FR-009a, FR-009b) A figure with no key fails `spec-lint`; a figure in
`research.md` and one in a Review history entry are both reached, and a Review history figure labeled
as that round's own run passes; `1,034` matches a recorded 1034 and `164` a recorded 164.2; a key absent from
`measurements.json` fails; a recorded value that does not appear in its paragraph fails; the correct
form passes - and this spec's own figures pass, as feature 236's FR-010b required of its author.
**SC-007** (FR-010) A one-shot observation with its date and method passes; the same sentence without
the label fails.
**SC-008** (FR-011) `make figures` reports a value that moved and is silent when none did.
**SC-009** (FR-012, FR-013, FR-014) The agent file carries the NOT-REVIEWABLE contract and the license
to measure independently; the tasks template's review task names the measurements file; a review
dispatched against a spec whose figures carry no keys returns NOT-REVIEWABLE naming them.
**SC-010** (spec-wide) Every mechanism is proven to FIRE by breaking it and watching a test go red.
**SC-011** (spec-wide) `make hooks-test`, `make quick` and `make done` are green.

## Decisions recorded

**D1 - one guard converts, not sixteen.** The census (`research.md` R4) makes a sweep tempting and the
sweep is exactly the wrong shape: each conversion owes a verdict diff over the window, and sixteen in
one feature is sixteen chances to move a verdict unnoticed. House-style converts because it is the
largest (273 lines), the one that cost the measurement time, and the one whose quoted-string form has
now broken twice on an apostrophe.

**D2 - a one-shot observation stays legal, labeled - and the class is narrower than the first draft
of this decision said.** The GM asked whether a reviewer should refuse figures given directly. Some
figures genuinely cannot be re-run - a container state, a span with nothing recording it - and a rule
with no room for those fires on correct work. But the first draft justified the class with "the
session ran 208 minutes", and that example is FALSE: this feature ships the command that reproduces
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

**D5 - the corpus is frozen with a date and refreshed deliberately.** A rolling window makes two runs
disagree for reasons that have nothing to do with the code, which is what made feature 236's figures
drift between rounds. Refreshing is a command a session runs on purpose, and the file name says when.

## Out of scope

- Converting the other fifteen inline-Python guards (D1); they are candidates with line counts.
- The model-latency block of R1 (29.3 min): it is turn structure, which the batching guard already
  governs, and no mechanism here would move it.
- The review rounds themselves. This feature makes their cheap findings impossible; it does not ask
  the reviewer for less.
