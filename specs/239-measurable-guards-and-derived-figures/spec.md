# Feature 239 - measurable guards, and figures that are derived

**Created**: 2026-09-13
**Status**: DRAFT (awaiting `spec-fidelity`)
**Input**: the GM's request, verbatim, in `request.md`

## Summary

Feature 236's second amendment - a hook change of about 40 lines - took 208 minutes, and a census of
the session's own transcript says where (`research.md` R1): 78.9 min replaying a command window, 78.0
min idle behind five review rounds, 29.3 min of model latency, 15.0 min of tests. The GM asked whether
more tooling would fix that. The record says yes for three of the four blocks, and names the reason
in each case:

- **A guard's decision cannot be called.** 273 of `house-style-hooks.sh`'s 366 lines are a Python
  program inside a shell string, so measuring it costs a process per command - 164 ms against 3.7 ms
  in process, 92 s against 2.1 s over one window (`research.md` R3).
- **Nothing freezes the window.** Nine passes each rebuilt the same list from 1,034 transcripts, and
  two of them ran against a prefilter this very hook had corrupted (`research.md` R4).
- **Half the review findings were arithmetic.** Ten of twenty were a figure stale, unreproducible, or
  measured one way and stated another; rounds 4 and 5 found nothing else (`research.md` R2). The
  reviewer rebuilt its own harness in four of five rounds to check them (`research.md` R5).

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

**FR-003** ONLY the house-style guard moves under this feature. The census found inline Python in 16
files (`research.md` R4); the rest are recorded as candidates with their line counts, and each later
conversion is its own change with its own before/after diff. A sweep of sixteen guards in one feature
would be sixteen chances to change a verdict silently.

### B. Measuring a guard is cheap (FR-004 to FR-007)

**FR-004** A frozen corpus of real commands MUST live in `scripts/fixtures/`, built from the recent
transcripts by a committed command and named with the date it was taken. Its prefilter MUST write its
dashes by codepoint, because the literal ones were corrected to hyphens by the hook as the script was
saved, which inflated one window by an order of magnitude (`research.md` R4).

**FR-005** `make hookbench GUARD=<name>` MUST replay that corpus through the guard's decision IN
PROCESS and print the verdict counts. Over the measured window this is 2.1 s where the spawning form
is 92 s (`research.md` R3).

**FR-006** `make hookbench GUARD=<name> AGAINST=<git-ref>` MUST print the VERDICT DIFF against that
ref - every command whose verdict changed, in both directions, with its targets. This is the check
feature 236's exemption owed and did not have: two drafts of it passed their own cases while changing
11 real verdicts for the worse.

**FR-007** The bench MUST refuse a guard whose decision it cannot import, naming FR-001, rather than
silently falling back to spawning - a fallback would make the 44x cost invisible again.

### C. A measured figure is derived, not typed (FR-008 to FR-011)

**FR-008** A feature's measured figures MUST live in `specs/NNN-*/measurements.json`, written by the
harness rather than by hand. Each entry carries: the value, the command that produced it, the date it
was taken, and optionally a note.

**FR-009** A figure with a UNIT in the operative sections - the sections `spec-lint` check 1 already
names - MUST carry a pointer to its key, and `spec-lint` MUST fail when the key is missing, when the
key is not in `measurements.json`, or when the recorded value does not appear in the paragraph. This
is check 1's existing definition of a figure, extended from "has a pointer to prose" to "has a pointer
to a number a command produced".

**FR-010** A ONE-SHOT observation MUST stay legal and MUST be labeled: something that cannot be re-run
- a wall-clock span already past, a container state, a count taken over a window that has moved - is
written with the date it was observed and the method, and check 5 accepts it. Without this the rule
fires on correct work, which is how a guard teaches sessions to bypass it.

**FR-011** `make figures` MUST re-run every recorded command in a feature's `measurements.json` and
report any value that moved, in the manner of `make notes-census`.

### D. A reviewer does not adjudicate a figure it cannot re-run (FR-012 to FR-014)

**FR-012** `.claude/agents/spec-fidelity.md` MUST carry the contract the GM proposed: where a round's
changed passages state measured figures, the reviewer verifies them by RE-RUNNING the recorded command
from `measurements.json`; and where a figure has neither a key nor a one-shot label, the round returns
**NOT-REVIEWABLE**, naming those figures, before reading anything else.

**FR-013** The refusal MUST NOT stop the reviewer measuring independently when it wants to. The four
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
**SC-002** (FR-003) The other 15 files are listed with their line counts in the spec's decisions, and
none of them is edited by this feature.
**SC-003** (FR-004, FR-005) The corpus is committed with its build command and a date in its name; a
bench run over it completes in seconds rather than minutes, and the figure is recorded in
`measurements.json` rather than asserted here.
**SC-004** (FR-006) The bench, run against the commit before feature 236's exemption change,
reproduces that change's verdict diff - the same commands, in the same directions.
**SC-005** (FR-007) A guard with no importable decision is refused by name.
**SC-006** (FR-008, FR-009) A figure with no key fails `spec-lint`; a key absent from
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

**D2 - a one-shot observation stays legal, labeled.** The GM asked whether the reviewer should refuse
figures given directly. Taken literally that refuses "the session ran 208 minutes", which no command
can re-run. So the rule is: re-runnable figures carry a key; a figure that cannot be re-run carries its
date and method. Both are checkable; neither fires on correct work.

**D3 - the reviewer refuses rather than re-derives, and the GM's doubt is answered with the record.**
The GM offered this as spitballing. The record supports it: ten of twenty findings were arithmetic
(`research.md` R2), and in four of five rounds the reviewer rebuilt a harness to check numbers
(`research.md` R5). The risk of the rule is that a reviewer stops thinking about whether a figure is
TRUE because it can see it was recorded; FR-013 answers that by keeping independent measurement
explicitly welcome. The cost of NOT having it is measured: rounds 4 and 5 of feature 236's amendment
found nothing but stale arithmetic.

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
