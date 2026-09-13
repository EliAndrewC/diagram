# Feature 236 - catch mistakes early and cheaply

**Created**: 2026-09-12
**Status**: FAITHFUL (spec-fidelity round 5, 2026-09-12)
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

**FR-002** Anchors MUST match whitespace-insensitively. Four of the six anchor misses the prior session recorded were an anchor spanning a line wrap (`research.md` R7), so exact matching would leave the
commonest miss in place.

**FR-003** The root `CLAUDE.md` MUST name `_patch.py` beside its "Edit files with `Edit`" rule, which it
does not replace: `Edit` stays the default; this is for the sweep that genuinely must be scripted.

### B. Shell commands, before the round trip (items 2 and 3)

**FR-004** A `PreToolUse` hook MUST parse every Bash command with bash in the tool's own configuration -
`bash -O extglob -n` at minimum - and REFUSE one that fails to parse, printing the parser's message.
Plain `bash -n` is not enough: the tool runs a command through `eval` one line at a time, so an option
enabled on one line governs the next, and `bash -n` with defaults refuses `shopt -s extglob` followed by
`!(x)` while the tool runs it (`research.md` R6).

**FR-004a** A Bash command carrying an unescaped backtick span that bash would EXECUTE - inside a
double-quoted string, or in the body of an UNQUOTED heredoc (`<<EOF`) - MUST be REFUSED, naming `$(...)`
and single quotes as the fix. This is the case the GM named, in their words: *"putting backticks in a
place that they do not belong ... have a hook detect that and then reject it early"*. `bash -n` cannot see
it, because it is valid syntax that runs. Detection MUST walk shell quote state, so a backtick inside
single quotes or a QUOTED heredoc body (`<<'EOF'`), which does not execute, is not refused. Measured over the 60 most recent transcripts, NONE of the executing spans was a deliberate substitution - every one a markdown code span written into prose - and that zero holds under all four walkers tried, whose counts differ (`research.md` R8); so the refusal fires on no correct work in the record, and this project
writes deliberate substitution as `$(...)`. The detector SHOULD share its quote walk with `_hm_make.py
recipe_comment_hazards`.

**FR-005** A `git commit` MUST be REFUSED, naming the `-F -` heredoc form, when any `-m` message contains
a double quote or a newline, or when `-m` is given more than once. This is item 3's literal ban on `-m`
for multi-line messages. It is a refusal and not a rewrite because the misquoted `-m` class parses cleanly
into a WRONG message - an inner quote closes the string early - so a rewrite would faithfully preserve the
wrong message. (The instance on record was in fact refused by `bash -n`, but only because a later `(`
happened to fall outside the prematurely closed quote; `research.md` R2 row 3. The ban does not rely on
that accident.) The refusal names the quoted-delimiter form `git commit -F - <<'EOF'`, whose body is
literal - an unquoted `<<EOF` would execute any backtick in the message (FR-004a). A single `-m` with no quote and no newline is untouched.

**FR-006** A commit whose trailers carry a co-author key with an address other than
`noreply@anthropic.com` MUST be refused, naming the expected form. The key MUST match case-insensitively
(git trailer keys are, so `Co-authored-by:` is the same key), the ADDRESS is what is checked rather than
the display name (which carries the model and changes), and the check MUST read every route a trailer
can arrive by: `-m`, `-F -`, `-F <file>` and `--trailer`. A message carrying other trailers - such as
`Claude-Session:` - is unaffected.

### C. House style where the writes actually go (item 4)

**FR-007** A Bash command whose payload carries a British spelling or a forbidden dash MUST be
CORRECTED - `updatedInput` carrying the corrected command, with an `additionalContext` naming what
changed - EXCEPT where the command is itself a spelling fix, which is REPORTED at exit 0 and left
exactly as typed (the GM 2026-09-12, ruling on D2: *"we should warn when it is the sed shape, and for
other shapes just correct it"*). A fix is the sed shape the GM named - a segment whose command is
`sed`, however it is reached (`xargs sed`, `find -exec sed`) - and a command carrying BOTH spellings
of the same word, which is that shape written in another language (D9).

**FR-007b** The correction MUST leave untouched what a command only NAMES rather than writes, and the
classes are those measured on the real commands this hook had warned on (`research.md` R10): a
searcher's segment wherever it stands (a leading `!`, a `$(...)`, a pipeline), a regex alternation, a
character class or `$'...'` holding a dash, a string whose whole content is one word, and a path
token. This is FR-007a's rule reaching the shapes it missed, not a new exemption: what a command looks
for is not what it writes, and correcting it breaks the command instead of the text.

**FR-007c** A path outside the project carries no house-style duty: `/tmp`, already exempt, and the
session state directory `~/.claude/projects/`, whose auto-memory index format is Claude Code's own and
uses an em-dash (D10). The exemption MUST be decided by where the write LANDS, and the write targets
MUST be read by the walk the main-tree guard already uses (`_hm_tree.walk`) rather than by a second
one: variables assigned in the same command are expanded, heredoc BODIES are not scanned for
redirects, and `git commit` writes to the repository rather than to a file. A destination the walk
cannot resolve - a relative path with no cwd, a target behind a variable assigned elsewhere - is NEVER
outside. Where the command resolves NO write target at all, the fallback is every path it names; where
it resolves one, a path merely MENTIONED decides nothing, because reading the memory file while
writing a project file names one of each. A program heredoc that could write anywhere does not
disqualify a command whose resolvable targets are all outside (D11).

**FR-007a** "Outside a quoted span" means the house-style sense - a prose quotation (`「」`, curly or
straight quotes, `<q>`, `<blockquote>`) or a backtick span naming a token - and NOT shell quoting: under a
`<<'PY'` heredoc the whole payload is shell-quoted, which would make the exemption swallow the rule.
Search-command segments MUST be dropped as `_hookmatch.py` already drops them.

**FR-008** A check in `make quick` MUST scan the DELTA - lines added or changed against the merge base,
**and every untracked file** - and fail naming file and line. Untracked files are named because the
motivating failures were new files written through heredocs, which `git diff` against a base does not
show. It MUST read the house-style hook's own word table (`BRIT` in `scripts/house-style-hooks.sh`), so the hook, the check and the ledger agree on one list. It MUST match as the hook matches - word-bounded and case-insensitive. Not the whole tree: 192 pre-existing lines are ledgered in `research.md` R4.

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

**FR-009a** `.specify/templates/tasks-template.md` MUST carry an "American spellings, hyphens only"
checklist line, because the GM asked for it in advance as well as checked after: *"we can have that as a
checklist item in advance as well as having an automated check for it"*. FR-008 is the check; this is the
checklist.

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

**FR-010c** Check 2 MUST scan the WHOLE TREE (the GM 2026-09-12: *"You should do the tree wide scan
instead of leaving this half done"*) - every tracked file and every untracked file git would keep, by
suffix - because all five of feature 234's survivals were outside `specs/` (`research.md` R5): two
skill `CLAUDE.md` files, the root guard table, a script docstring and a research page. A VERBATIM
RECORD is not a claim and is not scanned: `scripts/fixtures/` and `dev/*-log/` (D5). The narrating
exemption applies wherever a Decisions recorded or Review history section stands. The scan MUST read a
file whatever its extension - a `Makefile` states rules and figures here - and skip only what is
binary: the always-binary extensions, the generated `.svg` renders, and any file whose first bytes
carry a NUL.

**FR-010d** The `WITHDRAWN:` marker MUST open a line, a list bullet aside. Unanchored, the sentence
that DESCRIBES the marker declares one, which cost little while the scan read one directory and would
ban a phrase tree-wide now.

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
**SC-002** (FR-004) The 238-command corpus of `research.md` R6 replayed through the hook is refused by
the PARSE rule on exactly the two commands that failed at run time and nothing else, and the
`shopt -s extglob` then `!(x)` case passes. (The `-m` ban refuses 23 of the same corpus - FR-005's
rule, and its own measurement rather than a cost: `research.md` R9.)
**SC-003** (FR-004a) `echo "use `make quick` first"` is refused naming `$(...)`; so is a backtick span in
an unquoted `<<EOF` body; the same text in single quotes, and in a quoted `<<'EOF'` body, is not.
**SC-004** (FR-005) A `-m` message containing a double quote is refused; one containing a newline is
refused; two `-m` flags are refused; each refusal names `git commit -F - <<'EOF'`; a single plain `-m`
is untouched.
**SC-005** (FR-006) A message carrying both `Co-Authored-By:` with the expected address and a
`Claude-Session:` line passes; a `co-authored-by:` key with another address is refused; another address
supplied through `--trailer` is refused; so is one in a file given to `-F`.
**SC-006** (FR-007, FR-007a, FR-007b, FR-007c) A heredoc writing `centre` is CORRECTED to `center` and
an `echo >>` with it likewise; `sed -i 's/centre/center/g'`, a Python replacement pair and any command
carrying both spellings are reported and left exactly as typed; a sweep's own word list, a regex
alternation, a path token, a negated search, a prose quotation, a backtick span and
`git grep -n "centre"` are untouched. A write to the auto-memory index under `~/.claude/projects/` is
untouched IN THE SHAPES THE RECORD USES - the path literal, the path behind a variable assigned in the
same command, a directory behind such a variable - and so is a `/tmp` heredoc whose body carries a
line beginning `>`, and so is each of those when a program heredoc stands in the same command (D11);
while a command that writes project content by a route the walk RESOLVES is corrected even when a
redirect goes outside: reading the memory file and writing a project file in one breath, and a commit
message beside a `> /tmp/gate.log`.
**SC-007** (FR-008, FR-008a, FR-008b, FR-008c) The phase fails on a British spelling in a changed line and
in an untracked file; does not fail on one inside a multi-line `<blockquote>` whose opening tag is not in
the delta; does not fail on a line merely moved; does not fail on the 192 ledgered lines; and runs on a
delta that changes no Python.
**SC-008** (FR-010, FR-010a, FR-010c, FR-010d, FR-011) Each of the four checks fails on a constructed
fixture; a withdrawn figure narrated in Decisions recorded does not fail check 2, while one standing in
a sibling spec, a `docs/*.md`, a `CLAUDE.md` and a script docstring each IS named; one inside
`scripts/fixtures/` or `dev/*-log/` is not; a `WITHDRAWN:` that does not open a line declares no
marker; a freshly claimed spec with no `tasks.md` passes; the lint runs at gate and push over the
touched `specs/` directories.
**SC-009** (FR-010b) This spec passes checks 1 and 3.
**SC-010** (FR-012, FR-013, FR-014) The agent file documents VERIFY mode, and a review task generated from
the template for any round after the first names the changed passages and asks for a full reading of
those alone.
**SC-011** (FR-003, FR-009) The root `CLAUDE.md` names `_patch.py` beside the `Edit` rule and records the
Edit-versus-Bash tension.
**SC-012** (spec-wide) Every check is proven to FIRE by removing its mechanism and watching a test go red.
**SC-013** (spec-wide) `make hooks-test`, `make quick`, `make done` and `make page-check` are green.
**SC-014** (FR-009a) The tasks template carries the "American spellings, hyphens only" checklist line.

## Decisions recorded

**D1 - a red-tree commit guard is DECLINED.** It was a SEVENTH candidate, offered alongside the six and
recommended for skipping, so the GM's "all 6" does not cover it. Mid-task commits on red are protected
here, so a guard would fire on correct work.

**D2 - the hook CORRECTS a Bash payload, and warns only where the command is itself the fix.** The
departure the first version flagged went back to the GM, who ruled (2026-09-12): *"I think that we
could exempt that sed shape and otherwise correct in the hook rather than warning. So, basically, we
should warn when it is the sed shape, and for other shapes just correct it."* So the hook corrects, and
the sed shape is reported and left as typed. What that ruling COSTS was measured before it was built
rather than assumed (`research.md` R10, FR-007b): a command is not an edit, and correcting a word the
command only NAMES breaks a command that was right - a search would look for the other spelling, a
sweep's word list would stop matching the violations it exists to find, a file name would stop naming
a file. Those classes are held out and the rest is corrected.

**D3 - `bash -n` refuses, parsing with the tool's options.** An earlier draft claimed that a command which
cannot parse cannot do correct work. That is false for plain `bash -n`, which refuses an extglob pattern
the tool runs; it holds for the parse FR-004 specifies. The replay of 238 real commands found no false
positive (`research.md` R6).

**D4 - `-m` with a quote or newline is refused, not rewritten.** Item 3 says "banning". A rewrite was
drafted twice and dropped both times: the misquoted class parses into the wrong message, so any rewrite
preserves the wrong message exactly. An earlier draft also claimed the motivating commit "parses
cleanly"; it was in fact caught by `bash -n` - by the accident of a later `(` (`research.md` R2 row 3) -
which is exactly why the ban stands on its own rather than on that parse.

**D5 - the withdrawn-figure check scans the WHOLE TREE.** An earlier draft dropped the check, and the
review of this spec ruled that a narrowing no one approved; the version that shipped kept it but
reached only `specs/`, and recorded that limit rather than solving it - with all five of feature 234's
survivals sitting outside `specs/` (`research.md` R5), which is to say the check could not have caught
the case that motivated it. The GM ruled on the recorded limit (2026-09-12): *"You should do the tree
wide scan instead of leaving this half done."* The scan reads every tracked and every kept untracked
text file; the ONE class held out is a VERBATIM RECORD - `scripts/fixtures/` and `dev/*-log/` - on the
same ground as D8: a corpus of commands that really ran and a log of runs that really happened are
history, not a claim still standing, and a scan that failed on them would ask a session to falsify the
record. The alternative priced and rejected: exempting nothing, which makes every frozen corpus a
blocker the moment a marker names a phrase it happens to carry.

**D6 - an executing backtick is REFUSED.** An earlier draft only warned, on the reason that a backtick in
double quotes is sometimes deliberate command substitution. That reason was never measured, and the
measurement contradicts it: across four walkers whose counts differ, zero executing spans were deliberate (`research.md` R8).
A warning at exit 0 lets the command run anyway - including `cd /diagram` and `git init --bare`, both in
the record - so it makes no single mistake cheaper, and the GM asked that it be rejected early.

**D7 - a moved line is not in the delta.** A file split forced by the 1,000-line gate moves lines without
authoring them; counting them would make every split a spelling sweep. A line whose content changed is in
the delta and owes the fix.

**D8 - `scripts/fixtures/` is exempt from the house-style rules, in the check AND in the hook.** Found
by running the check over this feature's own work (`research.md` R9): all 43 of its findings were
inside the frozen 238-command corpus, because several of those commands were house-style sweeps and
carry the words by necessity. A fixture is a VERBATIM RECORD of what ran; correcting one would falsify
it and break the measurement it reproduces, which is the same ground as the GM's ruling that a
quotation keeps its own characters. The alternative priced and rejected: encoding the words in the
corpus, which would make the replay no longer a replay. This is an addition to the exemption set
FR-008a inherits from the hook, made after the spec was accepted and recorded here for the GM.

**D9 - "the sed shape" is read as THE FIX, so a replacement pair in any language is warned too.** The
GM named `sed`. A Python sweep's `t.replace("the centre of", "the center of")`, an `_patch.py` anchor
and its replacement, and an `awk` substitution are the same command doing the same thing, and the
GM's own reason - a correction would replace a word with itself and the fix would do nothing - applies
to each without modification. The rule implemented is therefore: the sed shape, plus any command
carrying BOTH spellings of one word. Measured: of the 53 commands the shipped rule reports, 9 carry a
`sed` segment and 42 carry both spellings with no `sed` anywhere (`research.md` R10), so the literal
reading would hand those 42 to the corrector - about half of them replacement pairs whose fix would
silently become a no-op. The predicate knows the SHAPE, not the intent: the other half are quotations,
searches and prose naming both spellings, which are reported rather than corrected, and a real
violation among them still fails `make quick` in the delta. This is a widening of what the GM said,
decided after acceptance, and it went to `spec-fidelity` as an exception before it was kept
(LEGITIMATE, amendment round 1).

**D10 - the session state directory is outside the project, as `/tmp` already was.** The hook's
existing exemption says a file outside the project is not project content, and names `/tmp` because
that was the instance in front of it. `~/.claude/projects/<project>/memory/` is outside the project in
exactly the same sense, and its index line format - `- [Title](file.md) — hook` - is Claude Code's own
and carries an em-dash, so correcting a memory write rewrote the format of the file as it was written
(`research.md` R10 found it in the replay). Also decided after acceptance and put to the reviewer.
Its WIDTH is the part that needed fixing: judged by every path the command mentioned, the exemption
silenced the rule on a command that read the memory file and wrote a project file in one breath -
found by the amendment review, and now decided by the write targets (FR-007c).

**D11 - a program heredoc does not disqualify a command whose resolvable write targets are all outside
the project, and the cost of that is named.** `python3 - <<'PY'` can write anywhere, so an earlier
draft appended an unknowable destination for every such command and acted on it. Measured by replaying
that draft (the hook at `31ef2907^`) against the shipped one over the window: **21** commands whose
every resolvable target was outside the project are silent now and were not - 15 of them corrected and
6 reported - and **7** of the 21 write the auto-memory index, whose em-dash is Claude Code's own
format (`research.md` R10). **The two mistakes are not
equal.** A correction that should not have happened silently rewrites someone else's text, and this
project has paid for that twice - the reader agents whose verbatim page text was Americanized in
2026-09-06, and the memory format here. A correction that did NOT happen leaves a British spelling in
the tree, where `make quick` fails on it in the delta - which is the half of item 4 that enforces, and
the reason the hook half can afford to be cautious. So the exemption follows the resolvable targets.
What it costs, stated rather than implied: a project write inside a command whose only resolvable
targets are outside is not corrected by the hook. The alternative priced and rejected is the draft
that produced the 21.

## Out of scope

- The research record and the agents that read it; the GM ruled it valuable as it stands.
- The 192 pre-existing lines of British spelling, ledgered by area in `research.md` R4 under Principle XIII.
- Reducing review rounds by lowering the bar: this removes rounds by making their cheap findings
  impossible, never by asking the reviewer for less.

## Review history

**Amendment 2, round 5** (`spec-fidelity`, MODE 3 VERIFY): **CHANGES REQUIRED**, two items, both
one-line restatements of stale text, both applied - the superseded figure standing in a fourth place
(D11's closing sentence), and `git commit` listed among the writes that yield an unresolvable target
when the walk in fact resolves it to the repository, as FR-007c and the case table both say. The round
confirmed every figure in the changed passages against its own replay, reproducing D11's 21 and 7, the
27/8 upper bound and the 42 both-spellings to the command, and it re-confirmed that the counter's
fifth round is reached. **This is where the five-round cap applies and the matter goes to the GM.**
What it is NOT is the persistent misunderstanding the cap exists to end: the ruling is judged
LEGITIMATE, its measurement is independently reproduced, the enforcing half of item 4 is untouched,
and both remaining items were stale sentences rather than a disagreement about what was asked. The
work stays in the clone until the GM rules.

**Amendment 2, round 4** (`spec-fidelity`, MODE 3 VERIFY): **CHANGES REQUIRED**, three items, all
taken, none of them a change to what the hook DOES - a stale count, a figure that did not reproduce,
and a docstring describing a deleted rule. D11 was judged LEGITIMATE, on the test that matters: the
outside-the-project exemption pre-dates this feature, D11 only decides which side the unresolvable
case falls on, and the enforcing half of item 4 - the `make quick` delta phase - is untouched. The
figure that did not reproduce is the one carrying D11's whole justification, and it is the second
time this amendment has stated a number measured by the hook's own target list rather than plainly:
re-measured here by replaying the pre-D11 hook (`31ef2907^`) against the shipped one over the window,
**21** commands change (15 corrected, 6 reported, now silent) and **7** of them write the auto-memory
index. The reviewer's independent run and this session's agree to the command. D9 was restated from
the consolidated run (53 reported, 9 sed, 42 both spellings), and `_hm_house.write_targets`'s docstring
no longer explains the rule D11 replaced - a reader repairing the "bug" it described would have undone
D11.

**Amendment 2, round 3** (`spec-fidelity`, MODE 3 VERIFY): **CHANGES REQUIRED**, five items, all
taken, and the round confirmed round 2's split and verdict figures against its own replay. Three were
mine to have got wrong. (1) The guard could be switched off entirely: the ImportError stub still took
one argument while the call site passed two, so an unimportable `_hm_house` raised a TypeError - and
the wrapper turns a crash into silence - for EVERY command rather than for one exemption. The stub
takes the arguments the call site passes now, and a case drives the hook with `_hm_house` broken on
purpose. (2) R10's "none of them is wrong in either direction" was true only when judged by the hook's
own target list, which is the circularity R10's own closing sentence warns about: judged plainly, this
round measured 19 commands whose every resolvable target was outside the project being corrected, 4 of
them the auto-memory index. That is D11; round 4 re-measured those two figures as 21 and 7, which is
what R10 and D11 carry. (3) FR-007c had dropped the
mention-fallback clause while the hook still carried the fallback, which decides 10 commands in the
window - the clause is back, because the spec and the code must say the same thing. Also taken: SC-006
now says the memory shapes hold when a program heredoc stands in the same command, and round 1's dash
figure is marked as its own run.

**Amendment 2, round 2** (`spec-fidelity`, MODE 3 VERIFY): **CHANGES REQUIRED**, three items, all
taken; four of round 1's seven confirmed resolved against re-run measurements (the reviewer's own
replay reproduced R10's window, its dash count exactly, and the withdrawn 2.2 s), and the reviewer
found round 1's fix for the exemption had introduced a worse defect than the one it fixed. Reading
write targets out of the raw command text got four shapes of the record wrong at once, measured over
the whole window: 7 writes outside the project newly CORRECTED - including the auto-memory in this
project's own `M=<path>; cat >> $M` form, and a scratchpad heredoc whose body carries a line opening
`>` - and 4 project writes newly SILENCED, where a `write_text` into the pool or a commit message sat
beside a `> /tmp/....log` redirect. The fix is to stop deriving a second walk: `_hm_tree.walk` already
expands a command's own variable assignments, strips heredoc bodies and knows `git commit` writes to
the repository, and a destination it cannot resolve is never outside. Re-measured the way the reviewer
set it: 47 verdicts change against the pre-fix hook and none is wrong in either direction. The other
two items: SC-006 named the literal path where the record uses four shapes, and each is a case now;
and the split of the reported commands was restated from the shipped hook (9 with a sed segment, 48
both spellings alone, 2 the GM's `request.md`). One more defect fell out of the work rather than the
review: `_outside(None)` raised, and the wrapper turns a crash into SILENCE, so the guard was off for
every command whose target could not be resolved - the suite caught it, and the rule it violated was
one this amendment had already written down.

**Amendment 2, round 1** (`spec-fidelity`, MODE 3 VERIFY; the counter reset to zero for a
post-acceptance amendment): **CHANGES REQUIRED**, seven items, all taken, and both exceptions judged
**LEGITIMATE** - D9 because the GM's own stated reason applies unmodified to a replacement pair
written in any language, D10 because it instances an exemption the hook already carries. The
consequential items, each of which the reviewer MEASURED rather than inferred: (1) the replay's
prefilter had its dashes flattened to hyphens by this very hook as the script was written, so R10's
window counted commands carrying a spaced hyphen - re-run, and the figures restated from it; (2) the
dash half of the ruling had therefore never been priced, and now is (201 of 545 on this round's own
run; R10 carries the final figures); (3) R10's "2.2 s"
did not reproduce - re-measured, the walk rewrite buys nothing on real commands and the 2.2 s was
container contention, which R10 now says; (4) R10 and D9 called the warned class "fixes" when the
predicate only sees both spellings, and the hook's own message asserted the same thing to the session
- both restated, and the message now names the rule that fired; (5) D10's exemption was judged by
every path a command MENTIONS, which silenced the whole rule on a command that read the memory file
and wrote a project file in one breath - it reads the write targets now (FR-007c); (6) the tree-wide
scan was narrowed by an unstated suffix roster that dropped every `Makefile` - it reads any
non-binary file now, extensionless included; (7) two statements the amendment falsified were still
standing, in `check-house-style-delta.py` and in ticked task T11.

**Amendment round 1** (`spec-fidelity`, MODE 3 VERIFY - the mode this feature adds, used on itself):
the counter reset to zero for a post-acceptance amendment, D8 (`scripts/fixtures/` exempt from the
house-style rules) judged LEGITIMATE, and ONE contradiction the amendment introduced: R9's table
reports 23 corpus commands refused by the `-m` ban, which falsified SC-002's "and nothing else" read
of the whole hook. SC-002 now says which RULE that clause is about. The reviewer re-ran the
measurements rather than trusting them - 43 findings without the exemption, all 43 in the one corpus
file, 0 with it - and checked the seam the class carries: all three files under `scripts/fixtures/`
are verbatim command corpora replayed by suites, so the directory-wide form is the right width. Its
aside, taken: the hook half of D8 had no case of its own, so a widening or a loss of it would have
gone unnoticed.

**Round 5** (`spec-fidelity`, changed text + contradiction scan): **FAITHFUL**, with four small record
fixes taken before implementation. R4 carried a stale paragraph beside its replacement; R8 still said
"zero of 42" where the finding is zero under every walker; the committed walker hid a backtick behind an
apostrophe inside an unquoted heredoc body - the exact case FR-004a names - so the walker now reads such a
body separately and its selftest pins it, with a bare backtick; and R8's count now says when it was taken,
over a window that moves.

**Round 4** (`spec-fidelity`, changed text + contradiction scan): all seven round-3 items confirmed
resolved; two more, both the recurring class of a figure written without its method. (1) R4's count was
case-SENSITIVE while the hook matches case-insensitively, so "the hook, the check and the ledger agree on
one list" was false - the list was shared, the matched set was not - and its area table still held
figures from an older run. Recounted the way the hook matches: 192 lines in 83 files, the exact command
recorded, the table rebuilt from that one run. (2) R8's count depended on the walker: three walkers gave
18, 42 and about 100. The walker is now committed as the record with a selftest pinning its rules (it
counts 73), and FR-004a and D6 cite the finding that holds under every walker - zero deliberate - rather
than a count none reproduces. The review also confirmed FR-004a's refusal is at the bar: a command that
prints markdown with backticks through double quotes or an unquoted heredoc is not correct work, because
bash runs the spans and corrupts the text.

**Round 3** (`spec-fidelity`): CHANGES REQUIRED, seven items, all taken; the reviewer re-ran the
measurements rather than trusting them and three were wrong. R7 had five anchor misses where the
transcript holds six. R2 row 3 said `bash -n` cannot see the nested-quote commit, but that commit was one
of `bash -n`'s two refusals - caught only because a later `(` fell outside a quote that had already
closed. R5 still called the withdrawn-figure check DROPPED while D5 kept it. FR-004a warned on an
unmeasured reason, and the measurement found no deliberate substitution at all, so it refuses. Also taken:
backticks in unquoted heredoc bodies, the quoted `<<'EOF'` form, and the GM's checklist item as FR-009a.

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
