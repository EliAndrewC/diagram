# Feature 236 - catch mistakes early and cheaply

**Created**: 2026-09-12
**Status**: Draft
**Input**: the GM's request, verbatim, in `request.md`, with the six items as the session put them

## Summary

A session that delivered features 233 and 234 ran 201 minutes, and 91 of them went to 20 `spec-fidelity`
rounds, at least eight of which returned findings a mechanical check could have caught for nothing
(`research.md` R1). The same session lost further time to its own rework and called that an
embarrassment needing no tooling. The GM declined that reading:

> Mistakes are inevitable, and good systems catch mistakes early and cheaply. And if a system is set up
> such that mistakes are very expensive, particularly mistakes which it is easy to make and which are made
> frequently, then the system design is poor. ... anytime someone says, "oops, that's embarrassing. I'll
> just do better in the future", then a good engineer says, hold on. This might be a system designs
> problem masquerading as a personal failing.

Classified that way (`research.md` R2), five of six failures are mechanically catchable, and one of them
is a guard hole already closed once for a different guard (R3). The GM approved six changes as one
feature; `request.md` records them as they were put. This feature delivers those six.

**The research record is explicitly out of scope** - the GM: *"I agree that the research record was
valuable, and I don't see anything there that I want to change either."*

## Functional requirements

### A. The edit helper (item 1)

**FR-001** A shared `scripts/_patch.py` MUST apply a list of (anchor, replacement) edits to a file so that
each edit is its own write: an anchor matching zero or more than one time is REPORTED and SKIPPED, and
every other edit in the batch still lands. It MUST print one line per edit saying which.

**FR-002** Anchors MUST match whitespace-insensitively. Three of the five anchor misses the prior session
recorded were an anchor spanning a line wrap (`research.md` R7), so exact matching would leave the
commonest miss in place.

**FR-003** The root `CLAUDE.md` MUST name `_patch.py` beside its "Edit files with `Edit`" rule, which it
does not replace: `Edit` stays the default; this is for the sweep that genuinely must be scripted.

### B. Shell commands, before the round trip (items 2 and 3)

**FR-004** A `PreToolUse` hook MUST parse every Bash command with bash in the tool's own configuration -
`bash -O extglob -n` at minimum - and REFUSE one that fails to parse, printing the parser's message.
Plain `bash -n` is not enough: the tool runs a command through `eval` one line at a time, so an option
enabled on one line governs the next, and `bash -n` with defaults refuses `shopt -s extglob` followed by
`!(x)` while the tool runs it (`research.md` R6).

**FR-004a** A Bash command carrying an unescaped backtick inside a double-quoted string MUST raise
`additionalContext`, at exit 0, naming that it EXECUTES and suggesting `$(...)` or single quotes. This is
the case the GM named - *"putting backticks in a place that they do not belong"* - and `bash -n` cannot
see it, because it is valid syntax that runs (`research.md` R8). It MUST NOT refuse: `"today is
`date`"` is deliberate substitution, so a refusal would fire on correct work. The detector SHOULD reuse
`_hm_make.py recipe_comment_hazards`, which already finds this hazard in Makefiles.

**FR-005** A `git commit` MUST be REFUSED, naming the `-F -` heredoc form, when any `-m` message contains
a double quote or a newline, or when `-m` is given more than once. This is item 3's literal ban on `-m`
for multi-line messages. It is a refusal and not a rewrite because the motivating failure parses cleanly
into a WRONG message - the inner quote closed the string - and a rewrite would faithfully preserve the
wrong message (`research.md` R2 row 3). A single `-m` with no quote and no newline is untouched.

**FR-006** A commit whose trailers carry a co-author key with an address other than
`noreply@anthropic.com` MUST be refused, naming the expected form. The key MUST match case-insensitively
(git trailer keys are, so `Co-authored-by:` is the same key), the ADDRESS is what is checked rather than
the display name (which carries the model and changes), and the check MUST read every route a trailer
can arrive by: `-m`, `-F -`, `-F <file>` and `--trailer`. A message carrying other trailers - such as
`Claude-Session:` - is unaffected.

### C. House style where the writes actually go (item 4)

**FR-007** A Bash command whose payload carries a British spelling or a forbidden dash MUST raise
`additionalContext` naming the words, at exit 0. It MUST NOT rewrite the command (D2).

**FR-007a** "Outside a quoted span" means the house-style sense - a prose quotation (`「」`, curly or
straight quotes, `<q>`, `<blockquote>`) or a backtick span naming a token - and NOT shell quoting: under a
`<<'PY'` heredoc the whole payload is shell-quoted, which would make the exemption swallow the rule.
Search-command segments MUST be dropped as `_hookmatch.py` already drops them.

**FR-008** A check in `make quick` MUST scan the DELTA - lines added or changed against the merge base,
**and every untracked file** - and fail naming file and line. Untracked files are named because the
motivating failures were new files written through heredocs, which `git diff` against a base does not
show. Not the whole tree: 146 pre-existing hits are ledgered in `research.md` R4.

**FR-008a** Exemptions MUST be judged from the whole FILE, not the changed line: a line inside a multi-line
`<blockquote>`, a 「」 quotation or a `SOURCE` block carries no opening marker of its own. It MUST carry
the full exemption set of the hook it mirrors - the GM's writing, `SOURCE` blocks, verbatim
`specs/*/request.md`, backtick spans, prose quotations, and the files that must quote the rule - and
exclude `.clones/`.

**FR-008b** A line MOVED within the delta - present among its removed lines and its added lines alike -
MUST NOT be flagged. A file split forced by the 1,000-line gate moves content without authoring it, and
must not become a spelling sweep of every moved line (D7).

**FR-008c** It MUST be a `make quick` PHASE rather than a pytest test: `make quick` is testmon-selected,
and a scan whose own code never changes would sit unexecuted through the edits it exists to catch.

**FR-009** The root `CLAUDE.md` MUST record the tension beneath FR-007: it says edit with `Edit`, while a
session run under an instruction preferring Bash loses that guard.

### D. `spec-lint` (item 5)

**FR-010** `scripts/spec-lint.py` MUST check a `specs/NNN-*/` directory and fail naming file and line, on
the four checks item 5 names:

  1. **A measured figure with no research pointer.** A paragraph in the Summary, Functional
     requirements, Success criteria or Decisions recorded that states a number with a unit of measure -
     `ft`, `m`, `km`, `ha`, `mu`, `sq ft`, `%`, `ms`, `s`, `min`, `minute`, `h`, `MB`, `MiB`, `GiB`, `px` -
     MUST also carry a pointer to a research section (`R<k>` or `research.md`). Counts with no unit
     ("20 rounds", "FR-001") are not figures. The Review history and Out of scope sections are exempt.
  2. **A withdrawn figure still standing.** A `research.md` may mark superseded text `WITHDRAWN: <text>`,
     where `<text>` is at least twelve characters and contains a letter, so a bare number cannot be
     banned. That text may not appear in the spec outside its Decisions recorded and Review history
     sections, which exist to narrate a reversal.
  3. **An orphaned requirement.** An id is `FR-` or `SC-` followed by three digits and an optional
     lower-case letter, so `FR-007a` is its own id distinct from `FR-007`. Every FR id MUST be named by at
     least one success criterion - a decision or task does not count. Every SC MUST name at least one FR
     id, or declare itself `(spec-wide)` for a criterion that genuinely covers the whole feature.
  4. **A stale task list.** Every FR or SC id a `tasks.md` cites MUST exist in the spec.

**FR-010a** Checks 1, 3 and 4 apply ONLY to a spec with a `tasks.md`. A freshly claimed spec has none, and
the root `CLAUDE.md` protects two pushes that carry exactly that - the number claim and the mid-feature
milestone push.

**FR-010b** This spec MUST itself pass checks 1 and 3. A rule its author's own document fails is either
wrong or the document is.

**FR-010c** Check 2 reaches only `specs/`. Feature 234's withdrawn measurement survived in five places
outside it (`research.md` R5); that limit is recorded in D5 rather than solved here.

**FR-011** `spec-lint` MUST run in the gate and at push beside `check-file-scale.py`, over every `specs/`
directory the delta touches, with a `--selftest` first as its siblings have.

### E. The re-review, narrowed (item 6)

**FR-012** The `spec-fidelity` agent file MUST document a VERIFY mode: given the items a round claims to
have applied, confirm each, read every added or changed passage in full, and scan the rest only for
contradictions those changes introduce.

**FR-013** `.specify/templates/tasks-template.md` MUST carry the review-task shape, because the GM ruled
doctrine alone will not hold it: *"it would not be enough to simply mention in our spec hit constitution
that you should not do that. We would need the checklists in the tasks to be very explicit about the fact
that that is how this works."* A review task names the round, the items, the changed passages and the
mode.

**FR-014** The FIRST review of a spec is a full reading. EVERY later round - including after an amendment
- reads all added or changed text in full plus a contradiction scan of the rest, and never re-reads
unchanged text in full. This is the GM's rule as given - *"only rereviewing the new stuff"* - and it
carries no further exception, because each exception drafted before this one re-admitted the whole-spec
re-read the GM said should not happen.

## Success criteria

**SC-001** (FR-001, FR-002) Over three edits whose second anchor misses, the first and third land, the
second is reported, and the file carries both; an anchor spanning a line wrap matches.
**SC-002** (FR-004) The 238-command corpus of `research.md` R6 replayed through the hook refuses exactly
the two commands that failed at run time and nothing else, and the `shopt -s extglob` then `!(x)` case
passes.
**SC-003** (FR-004a) `echo "use `make quick` first"` warns naming the execution; the same text in single
quotes does not.
**SC-004** (FR-005) A `-m` message containing a double quote is refused; one containing a newline is
refused; two `-m` flags are refused; a single plain `-m` is untouched.
**SC-005** (FR-006) A message carrying both `Co-Authored-By:` with the expected address and a
`Claude-Session:` line passes; a `co-authored-by:` key with another address is refused; another address
supplied through `--trailer` is refused; so is one in a file given to `-F`.
**SC-006** (FR-007, FR-007a) A heredoc writing `centre` warns naming it; the word inside a prose quotation
or a backtick span does not; `git grep -n "centre"` does not.
**SC-007** (FR-008, FR-008a, FR-008b, FR-008c) The phase fails on a British spelling in a changed line and
in an untracked file; does not fail on one inside a multi-line `<blockquote>` whose opening tag is not in
the delta; does not fail on a line merely moved; does not fail on the 146 ledgered hits; and runs on a
delta that changes no Python.
**SC-008** (FR-010, FR-010a, FR-010c, FR-011) Each of the four checks fails on a constructed fixture; a
withdrawn figure narrated in Decisions recorded does not fail check 2, and one standing in a file outside
`specs/` is not reached by it; a freshly claimed spec with no `tasks.md`
passes; the lint runs at gate and push over the touched `specs/` directories.
**SC-009** (FR-010b) This spec passes checks 1 and 3.
**SC-010** (FR-012, FR-013, FR-014) The agent file documents VERIFY mode, and a review task generated from
the template for any round after the first names the changed passages and asks for a full reading of
those alone.
**SC-011** (FR-003, FR-009) The root `CLAUDE.md` names `_patch.py` beside the `Edit` rule and records the
Edit-versus-Bash tension.
**SC-012** (spec-wide) Every check is proven to FIRE by removing its mechanism and watching a test go red.
**SC-013** (spec-wide) `make hooks-test`, `make quick`, `make done` and `make page-check` are green.

## Decisions recorded

**D1 - a red-tree commit guard is DECLINED.** It was a SEVENTH candidate, offered alongside the six and
recommended for skipping, so the GM's "all 6" does not cover it. Mid-task commits on red are protected
here, so a guard would fire on correct work.

**D2 - the house-style hook WARNS where item 4 said it would correct - a departure, flagged for the GM.**
The session told the GM the hook *corrects*. It does not, for a concrete reason rather than a general
cost: a Bash payload is often itself a spelling fix - `sed -i 's/centre/center/g'` - and correcting the
payload would turn that fix into a no-op. The enforcement item 4 asked for is kept in full by the
`make quick` phase, which fails; only the hook's half teaches instead of correcting. Raised with the GM
once the work runs, not decided silently.

**D3 - `bash -n` refuses, parsing with the tool's options.** An earlier draft claimed that a command which
cannot parse cannot do correct work. That is false for plain `bash -n`, which refuses an extglob pattern
the tool runs; it holds for the parse FR-004 specifies. The replay of 238 real commands found no false
positive (`research.md` R6).

**D4 - `-m` with a quote or newline is refused, not rewritten.** Item 3 says "banning". A rewrite was
drafted twice and dropped both times: the failure it targets parses into the wrong message, so any
rewrite preserves the wrong message exactly.

**D5 - the withdrawn-figure check is kept, scoped to `specs/`, with its limit recorded.** An earlier draft
dropped it, and the review of this spec ruled that a narrowing no one approved: item 5 names the check,
and the spec directory has real cases - R1 counts "a superseded paragraph still standing" among the
findings. What it cannot reach is text outside `specs/`, where feature 234's five survivals were
(`research.md` R5). Reaching that means a tree-wide scan, a different mechanism than the `spec-lint`
approved.

**D6 - a backtick inside double quotes WARNS rather than refusing.** It is the case the GM named and
`bash -n` misses (`research.md` R8), but it is sometimes deliberate command substitution, so a refusal
would fire on correct work.

**D7 - a moved line is not in the delta.** A file split forced by the 1,000-line gate moves lines without
authoring them; counting them would make every split a spelling sweep. A line whose content changed is in
the delta and owes the fix.

## Out of scope

- The research record and the agents that read it; the GM ruled it valuable as it stands.
- The 146 pre-existing British spellings, ledgered by area in `research.md` R4 under Principle XIII.
- Reducing review rounds by lowering the bar: this removes rounds by making their cheap findings
  impossible, never by asking the reviewer for less.

## Review history

**Round 2** (`spec-fidelity`, full reading): CHANGES REQUIRED, fifteen items, all taken, and four
measurements added to `research.md` rather than more assertion. The consequential ones: plain `bash -n`
fires on correct work (extglob enabled on one line and used on the next), so FR-004 parses with the
tool's options, measured in R6 against 238 real commands; FR-014 as drafted re-admitted the whole-spec
re-read the GM said should not happen, and is now the GM's rule with no exception; D5 dropped an approved
check on reasoning the review rejected under Principle XVI, so the check is back, scoped and with its
limit recorded; FR-010 carried a rule never among item 5's four and lacked one that was, and its orphan
rule failed this very spec; FR-006 was silently evadable by a case-variant key or a `--trailer`; FR-008
missed untracked files, which is where the motivating failures were, and judged exemptions per line; the
ledger the spec claimed did not exist; and FR-002's reason had no measurement (R7 now gives one). Added on
the session's own finding: FR-004a, the backtick case the GM named, which `bash -n` cannot see (R8).


**Round 1** (`spec-fidelity`, 2026-09-12): CHANGES REQUIRED, twelve items, all taken. The consequential
ones: the six the GM approved existed only in a transcript and are now in `request.md`; FR-008 would have
failed on landing against 146 measured pre-existing hits, so it is scoped to the DELTA and the rest is
ledgered; the `WITHDRAWN:` rule would not have caught its own motivating case and fired on correct work, so
it is dropped with its measurement (D5); FR-010's orphan rule would have refused THIS spec and the
number-claim push the root `CLAUDE.md` protects, so it applies only past the claim stage and this spec now
passes it; D4's "exactly derivable" was false for its own case, so FR-005 refuses where it cannot rebuild;
FR-006 pinned a literal that changes and now matches by shape; FR-014 graded its own trigger and now uses
the reset doctrine's; SC-007's self-absolving hedge is replaced by a named ledger; and "outside a quoted
span" was undefined in a way that would have let shell quoting swallow the rule.
