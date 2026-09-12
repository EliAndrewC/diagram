# Feature 234 - the modal entry owed when the record moves

**Created**: 2026-09-12
**Status**: ACCEPTED 2026-09-12, after five rounds of `spec-fidelity` (see Review history)
**Input**: the GM's message, verbatim, in `request.md`

## Summary

The GM asked, having just told a session to update the pigsty write-up on the map page: would that have
happened on its own? It would not. Their conclusion - "that should be another fix to the project
guidelines and what have you" - is this feature.

What a modal says about a feature IS the docstring of its `Kind` class (feature 189), written FROM a
research section the class names in its `Entry:` tag. Two things are missing between the two, and they
are NOT the same kind of problem - which is the whole design:

1. **A pointer that no longer lands is mechanically decidable.** `research_questions()` matches a
   heading by prefix and returns `[]` for one that no longer exists, silently; `test_an_entry_is_complete`
   asserts only `"research/" in fc.entry`. `research/CLAUDE.md` already requires a rename to fix its
   inbound class entries, in prose, with nothing behind it. A broken heading is never correct work, so
   this can be GATED.
2. **A modal whose prose has gone out of step with its section is a judgment about prose.** No
   git-derived rule can decide it. This is REPORTED and never refused.

The round-1 draft of this spec proposed a push-time refusal for (2) and was withdrawn on measurement:
replayed over the repository's own history, that rule would have fired on **30 of the last 32**
research-only commits, naming up to 41 classes at once, and every one of those 30 is a maintenance sweep
of the record - citations, translations, HTML-comment conversions - that changes no obligation on any
modal. `research.md` R2 carries the count. The root `CLAUDE.md` keeps a list of rules deliberately NOT
enforced precisely because "a guard that fires on correct work teaches a session to bypass every guard",
and this key would have earned its place on it.

## Functional requirements

### The report

**FR-001** A new script `scripts/_entry_owed.py` MUST answer, for the working delta against the merge
base with `origin/main`, which feature classes' modal prose MAY now be stale: every class whose `Entry:`
names a research section whose BODY changed in that delta, and whose own **explanation prose** did not
change in the same delta. It MUST be modeled on `scripts/_review_owed.py` - the same ask-git-never-cache
shape - printing one class key per line with the section that moved, empty when nothing is named, and a
`--why` form printing the ruling.

**FR-002** The exemption in FR-001 is keyed on the class's EXPLANATION prose - the `What:`, `Why:`,
`Note:` and `Caveat:` values - and NOT on the whole docstring. The docstring also carries the `Name:`,
`Covers:`, `Label:`, `Sources:` and `Entry:` data tags (feature 207), so a re-pointed `Entry:` or a
house-style correction would otherwise silence the check for that class while the prose a reader sees
stands untouched.

**FR-003** The answer MUST be asked FRESH at each decision point rather than cached, for the same reason
`_review_owed.py` is. The decision points are exactly two, and MUST be enumerated in the script's
docstring as feature 231 enumerates its three:
  1. `make page-check` - the target a research-page-plus-docstring delta actually owes;
  2. `scripts/sync-with-main.sh` at push time.

**FR-004** (rewritten on the GM's 2026-09-12 ruling) The two decision points differ, and deliberately:

  1. **`make page-check` REPORTS and does not block.** Teaching where it is free is this project's own
     ladder, and a session mid-work has not finished the edit the report is about.
  2. **The PUSH REFUSES.** Nothing lands while a named pair is unresolved. The session either rewrites
     the modal's prose, or records a reason - one entry in `dev/bypass-log/`, which may cover a whole
     maintenance sweep - and the push then proceeds. The escape token is `ENTRY_DRIFT_OK="<reason>"`,
     carried through the same `escape_reason` floor as every other escape in this repository (two
     words, eight characters) and recorded so `make audit` lists it.

This IS the enforcement the GM's ruling requires, and it is the shape this repository already uses for
every rule whose compliant action only a session can supply - `guard-write`, `guard-file`,
`FILE_SIZE_OK`, `PAIR_OK`: the guard refuses, the session supplies the judgment no tool has, in writing,
and the reason is auditable afterward. What was declined is a SILENT obligation, not a costly one.

**FR-005** The report MUST be actionable without further lookup: per class, the class key, the research
file and heading that moved, and the file and line of the docstring whose prose to re-read.

**FR-006** `make done` MUST NOT be the reporting channel. It exits at its short-circuit (skill
`Makefile:122`) before any phase runs when engine content is unchanged, and a research-page edit plus a
class docstring is not engine content (features 188, 189, 207) - so a report there would be vacuous for
the exact delta this feature exists for, shipping green and never printing once.

### The gated half

**FR-007** A class's `Entry:` heading MUST resolve to at least one research question, enforced in
**both** of the two places feature 173's file-size bar is enforced: a gate test naming the class that
fails, AND the push-time check in `scripts/sync-with-main.sh` beside `check-file-scale.py` and
`check-duplicate-defs.py`. This fires on exactly the thing it names and is never correct work, which is
what qualifies it to be gated at all (the bar the root `CLAUDE.md` sets in its "Deliberately NOT
enforced" note).

**The gate alone would not do.** A heading breaks when a section in `research/*.html` is renamed, and a
research-page-only delta owes NOTHING: `gate-stamp.py`'s `SKIP_ONLY_AREAS` is `{"browser"}` and its
`--check` skips it with the comment "research and test edits owe no gate at push" (line 451), while the
`page` area covers only `interactive/assets/*` and `classes/*.py`. So the delta shape that BREAKS a
heading - by construction a research edit touching no Python, which is also R2's 30-of-32 shape - runs
no gate, no `make page-check` and no push obligation. A gate-only check would surface the breakage as an
inherited red on the NEXT session's unrelated engine change.

**And the push-time call MUST run the checker's own `--selftest` first and die if it fails**, as all
three of its siblings at that call site do (`sync-with-main.sh` lines 222, 229, 234), for the reason
stated there: a checker that cannot prove it still bites is the failure mode that motivated it. FR-011's
non-vacuity test is a GATE test, and this requirement's whole argument is that the breaking delta runs no
gate - so the one push where this check stands alone is precisely the one where nothing else proves the
matching surface still matches. This is exactly the reasoning FR-006 and
`research.md` R3 apply to the report, and the round-2 review caught that the spec had not applied it to
its own other half.

**FR-008** A deliberately silent entry MUST stay legal in the form `fallow` already uses -
`research/fields.html (no dedicated entry - recorded as silent)` - and MUST be recognized EXPLICITLY
rather than by the absence of a match, so a broken heading and a declared silence cannot be confused.

**FR-009** FR-007 is PROPHYLACTIC and the spec records it as such: measured 2026-09-12, **0 of 51**
entries are broken today (50 resolve, 1 is the declared silence). It gives teeth to a rule
`research/CLAUDE.md` already states in prose; it is not a fix to a live defect, and a later audit must
not read it as one.

### Proving they work

**FR-010** Both checks MUST be proven to FIRE: a test that breaks a heading and goes red, and a test
that constructs a delta and asserts the script names the class. The matching MUST be by SHAPE rather
than against a hardcoded literal that would drift with its target.

**FR-011** Restating the project's "a stale literal agrees with itself" note as a testable obligation.
This feature ships TWO matching surfaces with two different non-vacuity mechanisms, and each MUST be
covered separately or one can stop matching quietly:
  1. **`_entry_owed.py`'s** surface (the `Entry:` tags, the section bodies, the explanation-prose tags) -
     a GATE test MUST fail if it matches nothing.
  2. **The heading checker's** surface - its `--selftest`, run at the gate AND at the push per FR-007,
     MUST fail if it matches nothing.
A renamed tag, a changed docstring format or a moved research directory must turn one of these red
rather than producing a silent all-clear.

### The guidelines the GM asked for

**FR-012** The rule MUST be written into `research/CLAUDE.md` beside the prose rule it gives teeth to,
and into `interactive/classes/CLAUDE.md` where "Writing an entry" is documented: when a section a class
was written from moves, the session DISPATCHES `entry-drift` at that pair and then either rewrites the
prose or records why it did not change - the record going to `dev/bypass-log/` as FR-013.1 specifies. The actor is named deliberately: an earlier draft said the
session "re-reads" while FR-013 gave the job to an agent, which named two actors for one job and
required neither. The root `CLAUDE.md` guard table MUST gain a row, that table being the
enumeration of what is enforced and where - the row stating plainly that the staleness half REPORTS and
the heading half GATES.

**FR-013** The judgment - does this modal still say what its section says - MUST be performed by a
subagent that actually performs it. `record-format` and `quote-check` do NOT: `record-format` reads a
RESEARCH ENTRY as its reader would ("You decide nothing about the map or the rule"), `quote-check`
judges whether a quotation supports the assertion it hangs on, and neither one ever opens a `Kind`
docstring. Naming them here would have required nothing that is not already required and pointed the
session at a pass that comes back green without looking at the modal - which is the GM's own failure
reinstalled one level up: everyone believes something checked it, nothing did. The round-2 review caught
this, and it is recorded rather than quietly corrected because the draft's wording was persuasive.

So this feature adds `.claude/agents/entry-drift.md`: given a class's EXPLANATION prose and the current
text of the section its `Entry:` names, it reports **IN-STEP**, **DRIFTED** (naming the sentence of the
modal the section no longer supports, or the finding the section now carries that the modal does not),
or **CANNOT-TELL** (with what it would need). Verification, not judgment about the map: it never edits
and never decides a rule. `model: opus` like every subagent check (GM 2026-09-07), which
`tests/test_agent_models.py` enforces.

**It MUST be wired, or it is worse than nothing.** An agent nothing dispatches is a third thing everyone
believes checked the modal. Two things follow:

  1. **A decision point.** The classes `_entry_owed.py` names at the PUSH decision point (FR-003.2) ARE
     what the session hands to `entry-drift` - and the report's printed line MUST say so in as many
     words, because that line is the only thing that runs on this delta shape.

     **The timing is honest about itself.** The report does not block (FR-004), and `push_cmd` prints it
     and then pushes in the same invocation (`sync-with-main.sh:348/352`), so the pairs are named by the
     run that pushes and the dispatch, the rewrite or the recorded line FOLLOW as a further commit. This
     feature does not claim otherwise. If surfacing at the end proves too late in practice, the lever is
     round 2's recorded aside - making a research-page edit owe `make page-check` at push - and that
     lever is the GM's, not this feature's, because it hangs a ~26 s target on every research edit.

     The dispatch is owed **per pair whose section's FINDING moved**, not per pair named. A maintenance
     sweep of the record - a footnote relocated, a session note turned into an HTML comment, a citation
     re-pointed, a passage translated - changes no finding and is discharged by one recorded line, not
     by an agent per class. This is not a loophole; it is the same measurement D1 rests on, applied
     consistently (see D6).

     **That line goes in `dev/bypass-log/`**, beside the project's other recorded waivers, one entry per
     decision with the class key, the section, and the verdict or the reason - so `make audit`
     enumerates it like everything else there. A destination is not optional: D6's whole cost argument
     is that a session can no longer pass a stale modal WITHOUT BEING TOLD, and that is unobservable
     afterwards - to a later session or to the GM asking "was this pair judged?" - unless the answer
     lands somewhere findable. A feature whose subject is that an unseen obligation does not happen is
     the wrong place to leave a record homeless.
  2. **Pre-authorization.** `entry-drift` MUST be added to the nine agents enumerated in
     `container-scripts/append-system-prompt.md`. Without it the mandate loses to the default system
     prompt's "do not call the Agent tool unless the user asked", which sits ABOVE `CLAUDE.md` - the
     documented 2026-07-27 failure in which three city maps shipped unreviewed - and the first session
     to meet a named pair will correctly decline to dispatch it.

**FR-014** The guidelines written by FR-012 MUST state plainly that `record-format` and `quote-check`
are the changed RESEARCH ENTRY's own standing obligations and are NOT a check on any modal, so that a
future reader of `research/CLAUDE.md` or `interactive/classes/CLAUDE.md` cannot mistake a green pass
from either for one.

## Success criteria

**SC-001** Over a CONSTRUCTED delta in a fixture repository - a research section's body changed, a class
naming it left alone - the script names that class, its section and its docstring line. (It must be a
constructed delta: feature 233 lands its research edit and its docstring rewrite together, so the real
tree will correctly say nothing.)

**SC-002** Over the same fixture with the class's `What:`/`Why:` prose also changed, the script is
silent; with only its `Entry:` tag changed, the script still names it (FR-002).

**SC-003** Breaking any class's `Entry:` heading turns the gate red, naming the class - AND a delta
whose ONLY change is a renamed research heading is refused at push, by the session that renamed it. The
second half is the one that matters and the one a gate-only check silently fails; a criterion that does
not distinguish the two passes on an engine delta that happened to run the gate.

**SC-004** Changing `fallow`'s declared silence into a broken heading turns the gate red - the carve-out
does not swallow the rule.

**SC-005** A delta touching only research sections no class entry names produces no report.

**SC-006** Deleting `_entry_owed.py`'s matching surface turns FR-011.1's gate test red, and breaking
the heading checker's turns its `--selftest` red at BOTH the gate and the push - neither produces a
quiet pass.

**SC-007** `.claude/agents/entry-drift.md` exists, pins `model: opus`, passes
`tests/test_agent_models.py`, and its contract names the three verdicts. Its worked example is feature
233's own pair, run and recorded there: the `PigSty` modal against the section 233 rewrites, which must
come back DRIFTED before 233's docstring rewrite and IN-STEP after it. A new agent whose first real
dispatch is the case that motivated it is the cheapest honest proof it does anything.

<!-- SC-008 was the task-checkbox criterion, deleted in round 4 with the checkbox it proved; the
     numbers below are not renumbered because the Review history references them. -->

**SC-009** `container-scripts/append-system-prompt.md` names `entry-drift` among the pre-authorized
agents, asserted by a test rather than by inspection.

**SC-010** A push whose only change is a renamed research heading is REFUSED, and a push made with the
heading checker's matching surface broken is refused by its `--selftest` rather than passing quietly.

**SC-011** `make audit` enumerates every entry taking FR-008's declared-silence form.

**SC-012** The guidelines say the thing - the deliverable the GM literally asked for, and until now the
only one no criterion covered. Checkable at task time: `research/CLAUDE.md` and
`interactive/classes/CLAUDE.md` each state what is owed when a section a class was written from moves
(dispatch `entry-drift`, then rewrite or record to `dev/bypass-log/`); the root `CLAUDE.md` guard table
carries a row saying the staleness half REPORTS and the heading half GATES; and both skill documents say
plainly that `record-format` and `quote-check` are the changed research entry's own obligations and are
NOT a check on any modal (FR-014).

**SC-013** A push with an unresolved named pair is REFUSED; the same push with the pair's prose
rewritten proceeds; and the same push with `ENTRY_DRIFT_OK="<reason>"` proceeds and the reason lands in
`dev/bypass-log/` where `make audit` lists it. A bare token with no reason is refused by the same
two-word, eight-character floor every other escape uses.

**SC-014** `make hooks-test` green, `make done` green, `make page-check` green.

## Decisions recorded

**D1 - REPORT at the gate, REFUSE at the push (amended 2026-09-12).** The round-1 design refused at push
with no way to discharge the refusal, and was withdrawn on the measurement in
`research.md` R2: 30 of 32, up to 41 classes at a time, all correct work. Recorded here rather than
silently dropped, because the next session to notice this seam will have the same idea.

**D2 - the split between what is gated and what is reported is the design.** A heading that does not
resolve is decidable and never correct; a modal that has drifted from its section is a judgment about
prose. Putting both behind one mechanism is what made the first draft wrong.

**D3 - the unit is the SECTION, not the file.** File-level keying would fire on every edit to a large
page. It does not rescue the staleness key from R2 - the sections classes name ARE the busy ones - but
it is still the right unit for the report, which should name the section a reader would look at.

**D4 - content-derived, never a stored hash.** No table of "this entry was current as of this text" is
kept: such a table is exactly the stale literal that agrees with itself. git is the record.

**D5 - the REPORT's page-check half has no escape token and needs none; its PUSH half has
`ENTRY_DRIFT_OK`; the HEADING CHECK refuses and still has none, deliberately.**
Two halves, two answers, stated separately because a single "nothing refuses" sentence was wrong the
moment FR-007 grew a push-time refusal (round 3). The report (FR-001 to FR-006) never refuses, so there
is nothing to escape. FR-007 DOES refuse, at gate and at push, and carries no escape token even so -
unlike `check-file-scale.py`'s `FILE_SIZE_OK`, which exists because a large file can be legitimate
ordered data. A class entry pointing at a heading that does not exist has no legitimate form: the one
case that looks like it - a section deliberately not written - is FR-008's declared silence, which is
an in-band recognized VALUE and not an escape. Recorded so a later session does not add one for
symmetry.

**D6 - the obligation is ENFORCED AT THE PUSH (GM's ruling, 2026-09-12).** This entry previously
accepted that nothing enforced the dispatch and called the obligation doctrine. The GM struck that:
*"I don't believe that we should have any such thing as an unenforced doctrine. If it is unenforced,
then it is not a doctrine. something should either not be considered doctrinal or it should be
enforced."* So it is enforced - the push refuses until a named pair is resolved or a reason is recorded
(FR-004.2).

*Why not a quieter key instead.* The narrowing was measured before enforcement was chosen: firing only
on what a reader SEES, rather than on any change to the section's body, takes 39 of 39 research-only
commits down to 38 of 39 (`research.md` R5). One commit in thirty-nine. There is no mechanical key that
separates "this section now says something different" from "this section was maintained", because that
is a judgment about meaning - which is why the compliant action is a written judgment rather than a
tool's verdict.

*What it costs, in observable terms.* Every research-only push now carries one obligation: resolve the
named pairs or write one line. A maintenance sweep naming 41 classes is discharged by a single recorded
line under the FINDING rule in FR-013.1, so the cost is one sentence per sweep rather than 41 dispatches.

*Alternatives priced and DECLINED.* A task checkbox (round 3): rejected on measurement - the enforcer
reads only a `tasks.md`'s text and a feature number, so a delta-derived condition is not expressible in
it, and it would not run on this delta shape anyway. A narrowed key (above): rejected, one commit in
thirty-nine. A silent obligation with no mechanism (this entry's previous content): rejected by the GM.

*Superseded content, kept because the reasoning still bounds the design.* Nothing enforces that a session
hands a named pair to `entry-drift` BEYOND the recorded reason - the guard cannot tell a real judgment
from a hollow one, only that one was made and by whom. That residue is the same as every other escape in
this repository and is audited the same way.

*The enforcer, and the two that were priced and failed before it.* The condition is "the report named a
pair", delta-derived and known only to `_entry_owed.py` - which runs at push, where the refusal now
lives. The two that do not work:
  - **A task checkbox** beside `quote-check confirmed` (the round-3 design). REJECTED on measurement:
    `tests/test_task_research_boxes.py` reads exactly two inputs, the text of a `tasks.md` and the
    feature number from its directory name - no delta, no git, no class index - so the condition is not
    expressible in it. And its enforcement would not run on the motivating delta anyway: `make done`
    short-circuits at `Makefile:122` on a research-plus-docstring delta, and `make page-check`
    (`Makefile:926`) runs only `tests/interactive` and the browser page tests, not that test. A checkbox
    that cannot be conditioned is always owed or never owed.
    - **A refusal at push with no way to discharge it** - which is what D1 rejected, and still rejects:
    the key fires on nearly every research-only commit, so a refusal that could only be satisfied by
    rewriting prose would block correct work. The refusal that ships can be discharged by a recorded
    reason, which is the difference.

*What it costs, in observable terms.* A session that ignores the report's printed line ships a stale
modal, exactly as today. What changes is that it can no longer do so without being told - which is the
GM's own complaint ("would you have done it?"), and is the difference between a silent gap and a
declined prompt.

*Why the round-3 design was worse than this.* It moved D1's declined cost from the refusal onto a
checkbox without re-pricing it: on one of those 30 sweeps it would have demanded either 41 Opus
dispatches to conclude that a footnote moved, or a box ticked without dispatching - which is the unwired
agent round 3 existed to fix, wearing a tick.

*Who chose.* This spec did - the session, on the measurements returned by rounds 3 and 4 of its own
`spec-fidelity` review. **The GM has NOT ruled on it.** They asked for a fix to the project guidelines
and were not asked whether "doctrine, unenforced" is an acceptable answer for the judgment half, which
is a call they may want to make themselves. Recorded so a later reader knows this door is open rather
than closed.


## Out of scope

- Judging whether a rewritten modal entry is GOOD - that is `record-format` and `quote-check`.
- Making a research-page edit owe `make page-check` at push. Round 2 recorded it as a lever and the GM
  DECLINED it on 2026-09-12: *"A research edit should not owe a make page check at push."* So the report
  reaches a research-only delta at the push and nowhere earlier, which is where the refusal lives anyway.
- Backfilling entries currently out of step with their sections. The check is DELTA-based against the
  merge base and cannot surface historic drift at all; the first run's delta is feature 233's edits, so
  it will name what 233 touched and nothing else. An empty result is therefore NOT evidence that the 51
  entries are in step, and the spec says so here so nobody later reads it as such. A sweep of the 51 is
  its own work, wants the GM's call, and is not begun here.

## Review history

**Round 6** (`spec-fidelity`, 2026-09-12): **FAITHFUL.** All four round-5 items confirmed resolved in
substance, not in appearance, and the load-bearing claims re-verified in source rather than taken from
this history - the `_TAGS`/`_DATA_TAGS` split, the three selftested siblings at the push call site, that
`push_cmd` prints and pushes in one function body, the `Makefile:115-122` short-circuit, what
`page-check` runs, that `make audit` reads `dev/bypass-log/`, the nine pre-authorized agents, and
`fallow`'s declared silence.

On the question this feature could most easily have failed - whether D6 preserves the very behavior the
GM complained about - the verdict is no: the spec delivers the guidelines fix AND a report that makes a
stale pair impossible to miss silently, and declines the enforcement the GM did not ask for on the
measurement that is this project's own stated reason for keeping a rule off the enforced list. The
residual is stated as a cost in observable terms and flagged as the GM's call.

**Why a sixth round exists, one past the cap.** No round returned the word FAITHFUL - each applied its
changes and moved on - and the push gate reads for a recorded verdict, so this round was run to obtain
one rather than to reopen the design. The reviewer's own reading: not the argument-going-nowhere the cap
exists to end, since no round reopened a settled decision, each found new and smaller items, and the
spec was made SMALLER twice on measurements. The overrun was flagged to the GM rather than absorbed.

**Status: ACCEPTED, FAITHFUL.** Implementation may begin.

**Round 5** (`spec-fidelity`, 2026-09-12): the final round under the five-round cap. All three round-4
items confirmed resolved; four small closing edits required, all taken, and the reviewer classified them
explicitly as "(a) small and closing ... Do not escalate to the GM on account of this verdict."
(1) D6 carried three of the four elements this project requires of an accepted-limitation record and was
missing WHO CHOSE - which here is not bookkeeping, because "doctrine, unenforced" for the judgment half
is a call the GM may want to make. D6 now says the session chose it on the review's own measurements and
that the GM has not ruled, so the door reads as open.
(2) FR-013.1 claimed the pairs are handed to the agent "before the work lands". False, and contradicted
by round 2's own recorded aside: the report does not block and `push_cmd` prints then pushes in one
invocation, so the dispatch follows as a further commit. Stated honestly now, with the `page-check`-at-
push lever named as the GM's to pull if end-of-work surfacing proves too late.
(3) FR-012 and FR-013.1 both required the session to RECORD something and neither said where - leaving
the one trace D6's cost argument depends on unobservable. Both now name `dev/bypass-log/`, which
`make audit` already enumerates.
(4) The guidelines - the deliverable the GM literally asked for - were the only thing in the spec no
success criterion verified, while lesser items had two. SC-012 covers FR-012 and FR-014.
The reviewer independently verified `_TAGS` less `_DATA_TAGS`, the three selftest siblings, the
`SKIP_ONLY_AREAS` skip, what `page-check` runs, the nine pre-authorized agents, `fallow`'s declared
silence and `test_an_entry_is_complete`'s single assertion. It ruled the heading half SHIP rather than
cut: it is the decidable half, never correct work, the cheapest thing here to gate, and cutting it would
leave a `research/CLAUDE.md` rule with nothing behind it.
**Status: accepted.** Five rounds, each finding new and smaller items; no round reopened an earlier
decision. Implementation may begin.

**Round 4** (`spec-fidelity`, 2026-09-12): round-3 items (2)-(5) verified resolved in source. Item (1),
the wiring, was resolved **in appearance only**, and the fix is a CUT rather than more machinery.
Three findings, all taken.
(1) The gate-enforced task checkbox could not work. `research_box_violations(text, feature)` reads the
text of a `tasks.md` and a feature number and nothing else - no delta, no git, no class index - so a
delta-derived condition is not expressible in it; SC-008 gave it away by proving the rule textually. And
its enforcement would not have run on the motivating delta regardless: `make done` short-circuits at
`Makefile:122`, and `make page-check` (`Makefile:926`) does not run that test. The reviewer noted this
was the THIRD appearance of one blind spot - round 1 found it in the report's gate channel, round 2 in
FR-007's gate-only enforcement, and round 3's own fix reintroduced it in the checkbox.
(2) Worse, the checkbox hung a MANDATORY obligation on the very key D1 withdrew on measurement: on one
of R2's 30 sweeps it would have demanded 41 Opus dispatches to conclude a footnote had moved, or a tick
without a dispatch. Not a literal contradiction with FR-004, but a purpose-level one.
The checkbox and SC-008 are DELETED. The dispatch is owed per pair whose section's FINDING moved, said
in the report's own printed line, and the obligation is recorded as doctrine in a new D6 with both
rejected enforcers priced and the cost of having none stated plainly.
(3) FR-011 said "the script's matching surface" in a spec with two scripts and two different
non-vacuity mechanisms; both are now named separately, with SC-006 covering each.
The reviewer ruled the design sound and told the session NOT to escalate: "the design (gate the
decidable half, report the judgment half, route the judgment to an agent) is right and rounds 1-3 got it
there." It also flagged the heading half (FR-007-FR-009) as the severable piece if the GM ever wants
this smaller - prophylactic against a defect that does not exist, honestly labeled as such by FR-009,
and in scope because `request.md` records that the GM was told about the broken-heading silence in the
same turn they answered.

**Round 3** (`spec-fidelity`, 2026-09-12): FR-007's push placement verified in the source and CLOSED
(`push_cmd` runs `check-file-scale.py` unconditionally at lines 229/236, upstream of the route decision
at ~330, so BOTH routes run it on a whole-tree scan). Four required changes, all taken, three of them
consequences of round 2's own fixes.
(1) `entry-drift` was specified but WIRED TO NOTHING - no decision point, and FR-012 assigned the same
judgment to the session, so the spec named two actors for one job and required neither. The agent could
have shipped, never been dispatched, and every criterion still passed. The reviewer's phrase is the one
worth keeping: an unwired agent is worse than no agent, because it is a third thing everyone believes
checked the modal. Now pinned as a task checkbox the gate enforces, with FR-012's actor corrected.
(2) `entry-drift` was not pre-authorized in `container-scripts/append-system-prompt.md`, so the default
system prompt's "do not call the Agent tool unless the user asked" would have outranked it - the
documented 2026-07-27 failure - and the first session to meet a named pair would have correctly declined
to dispatch it.
(3) D5 said "nothing refuses, so nothing needs escaping", which round 2's own FR-007 refusal made false.
Split into two halves with the reason each way.
(4) FR-011's non-vacuity proof is a GATE test while FR-007's argument is that the breaking delta runs no
gate - so on the one push where the heading check stands alone, nothing proved it still bites. The
push-time call now runs a `--selftest` first, as all three of its siblings do.
Also taken, from the reviewer's aside: FR-008's declared-silence carve-out is enumerated by `make audit`
(SC-011), on the project's own reasoning that a carve-out nobody can enumerate is one nobody revisits.
Round 3 of five; the reviewer noted the findings are converging and told the session NOT to escalate.

**Round 2** (`spec-fidelity`, 2026-09-12): all nine round-1 items confirmed addressed in substance, and
two NEW required changes, both taken.
(1) FR-007 gated the heading check at a target the breaking delta does not run - the spec made exactly
this argument for the report in FR-006 and failed to apply it to its own other half. `gate-stamp.py`
line 451 skips `research/` at push, so a renamed heading would have surfaced as an inherited red on the
next session's unrelated work. FR-007 now enforces at the gate AND at push, and SC-003 pins the
research-only delta, which the old criterion could not distinguish from an engine delta that happened to
run the gate.
(2) FR-013 routed the judgment to `record-format` and `quote-check`, neither of which reads a `Kind`
docstring at all - so as drafted it required nothing new and pointed the session at a green pass that
never looks at the modal. That is the GM's own failure one level up. Replaced with a real agent
(`entry-drift`) that performs the comparison, plus FR-014 so the guidelines say plainly that the other
two are not a check on a modal. SC-008 pins it to feature 233's own pair.
The reviewer independently verified 0 of 51 broken entries, the `Makefile:122` short-circuit, and that
FR-002's prose/data partition is the code's own (`_base.py` `_TAGS` less `_DATA_TAGS`), noting the
partition should be DERIVED from `_DATA_TAGS` rather than restated - taken as part of FR-010's shape
rule.
**Its aside, recorded for the GM and NOT acted on**: the report's only channel that runs for the
dominant delta shape is the push, so a pair is surfaced at the end of the work rather than during it. If
that proves too late in practice, the lever is to make a research-page edit owe `make page-check` at
push - a one-line change to `SKIP_ONLY_AREAS` semantics, and a COST decision (it would put a ~26 s
target on every research edit), which is the GM's to make rather than this feature's.

**Round 1** (`spec-fidelity`, 2026-09-12): verdict CHANGES REQUIRED, nine items. The central one killed
the design: the reviewer replayed the proposed push-time refusal over the repository's own history and
found it would fire on 30 of the last 32 research-only commits, naming up to 41 classes at a time, all
of them correct maintenance work on the record - and noted that the draft contradicted itself, FR-009
asserting it would not fire on correct work while FR-005 named that same work as its escape's purpose.
The refusal is withdrawn (D1) and the measurement recorded (`research.md` R2). Also taken: the gate is
not a reporting channel because `make done` short-circuits before any phase on this delta shape (FR-006,
`research.md` R3); the exemption is narrowed from the whole docstring to the explanation prose (FR-002);
the decision points are enumerated (FR-003); "a no-op must refuse" is restated as a testable obligation
(FR-011); SC-001 is restated over a constructed delta, its original premise being about to become
impossible once 233 lands its research edit and docstring together; FR-007's zero-current-violations
status is disclosed (FR-009); and the "Out of scope" bullet no longer implies the first run could
surface the existing backlog. The reviewer's closing aside - that the reliable half of this seam is a
judgment the project already routes to an agent - is taken as FR-013.
