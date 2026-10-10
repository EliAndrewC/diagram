# Feature 377: No feature is filed without the GM's approval, and the tooling holds it

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-10
**Status**: Done 2026-10-10 - amendment 1 landed: spec FAITHFUL, plan CLEAR, every task ticked; suite 44/44

**Affects**: tooling, review process

**Approved**: the GM, 2026-10-10, "Can you make that tweak prior to working on the new feature 376?"

**Input**: `request.md` (the GM, 2026-10-10)

## Why

Sessions file spec-kit features on their own judgment. They see work to do, claim a number, write a `spec.md`
whose status is `Filed` and push it, and at most mention it somewhere in a long run of output. The GM finds out only
when `make speckit-todo` happens to show it. The repository's own guidelines invite this: CLAUDE.md says "Defer work by
filing a feature" (feature 330). Feature 376, filed this same day for 347's follow-up, is the case that prompted it:
the GM would rather have had 347 extended and reopened.

The GM's words (request.md): spec-kit features "should not be filed without my explicit approval", enforced by tooling
that makes a feature invalid "unless it has like the line that quotes my approval to file the feature, which is like
formatted in a specific way", so that it "can't be committed at all, like not even to a branch", and only "with new
features um, going forward".

## User Scenarios & Testing

### User Story 1 - A session cannot file a feature the GM did not approve (Priority: P1)

A session finds follow-up work and writes a `spec.md` for a new feature. When it tries to commit it, the commit is
refused. The refusal tells the session to ask the GM, and gives the exact approval line to add once the GM says yes.

**Why this priority**: it is the GM's request. Without it the guideline is a reminder, and reminders are what failed.

**Independent Test**: in a scratch repository, stage a new `specs/NNN-x/spec.md` with no approval line and run the
commit through the guard. It is refused. Add an approval line quoting words the transcript's GM messages do not
contain, and it is refused. Quote words the GM did write, and it passes.

**Acceptance Scenarios**:

1. **Given** a new feature's `spec.md` with no `**Approved**:` line, **When** a session runs `git commit` (or `git add`)
   that would stage it, **Then** the command is refused with the line's form and the instruction to ask the GM.
2. **Given** an approval line whose quoted words appear in no message the GM typed in this session, **When** the
   session commits, **Then** it is refused, and the message says the quote was not found among the GM's messages.
3. **Given** an approval line quoting the GM's own words from this session, **When** the session commits, **Then** it
   passes.
4. **Given** a feature numbered below 377, **When** any session edits and commits it, **Then** this guard does not
   apply.

### User Story 2 - The push holds the form even where the commit guard could not see (Priority: P2)

A commit made outside a Claude Code session (by a script, or by the GM on another machine) is not seen by the commit
guard. The push re-checks that every feature from 377 on carries an approval line of the right form.

**Independent Test**: a spec-lint run over a spec directory numbered 377 or above with no approval line reports one
finding. With the line it reports none.

**Acceptance Scenarios**:

1. **Given** a push that adds or changes the `spec.md` of a feature numbered 377 or above with no well-formed approval
   line, **When** `sync-with-main.sh` runs its push checks, **Then** the push is refused with the line's form.

### User Story 3 - The guidelines say ask first, and prefer reopening (Priority: P2)

A session reading the guidelines learns:
- never file a feature without asking;
- put the proposal in the final message, not only mid-stream;
- prefer extending and reopening the feature the work came from over filing a new one.

**Independent Test**: CLAUDE.md, `docs/spec-kit-and-reviews.md` and the claim's own output no longer tell a session to
"defer work by filing a feature", and do say the three things above.

### Edge Cases

- **Renumbering** (`make claim RENUMBER=`): a feature moved to a new number keeps its approval line. The guard sees
  that the file came from an existing `spec.md` (git's rename detection), and judges it as not new.
- **Reopening a closed feature** (amendment 1): a session may reopen a feature, do the work and close it again with no
  approval - the count of features with open work does not grow. What needs the GM's approval is a reopened feature
  that LANDS open (FR-011), for any feature number: an old feature left open adds to the count as a new one does.
- **A headless or subagent session**: its first message is a prompt another session wrote. The guard reads only the
  GM's own typed messages and answers. A sub-session filing a feature needs the approval quoted to it, and carries the
  same limitation as any forwarded quote (Assumptions).
- **The GM answers a question with a choice** (`AskUserQuestion`): the answer the GM picked is the GM's message for
  this purpose.
- **A one-word "yes"**: a quote must be at least three words, so a bare "yes" or "ok" from anywhere in the session
  cannot approve a feature. The session quotes the GM's fuller reply, or asks for one. An answer picked in a question
  is often short ("File it"), so there the quote may be the question together with the picked answer, as the answer
  record holds them (`"Shall I file feature 380 for X?"="File it"`); the three words count over the whole quote.
- **The approval is about a different feature**: the guard cannot judge meaning, only that the words are the GM's.
  `spec-fidelity` already reads `request.md` and the spec against the GM's words; its contract adds one check: the
  approval line's quote approves THIS feature.
- **Compaction**: the guard reads the whole transcript file. A message from before a compaction is still the GM's
  message.

## Requirements

### Functional Requirements

- **FR-001 - The approval line.** The `spec.md` of every feature numbered 377 or above carries at least one line of
  the form
  `**Approved**: the GM, YYYY-MM-DD, "<the GM's words, verbatim>"`.
  The quote is at least three words. It is the GM's words as the session received them, dictation slips included, or,
  for an answer the GM picked in a question, the question and the picked answer as the answer record holds them.
- **FR-002 - Refused at the commit.** A `git add` or `git commit` run by a session that would stage a NEW `spec.md` of
  a feature numbered 377 or above is refused unless that file carries an approval line whose quote appears in a
  message the GM typed in the session's own transcript, or in an answer the GM gave to a question there. NEW means
  absent from HEAD at that path and not a rename of an existing `spec.md`. Whitespace and curly-versus-straight quote
  marks are normalized; nothing else is.
- **FR-003** - withdrawn in round 1 (reopening is not gated; see What it does not cover).
- **FR-004 - The push backstop.** At the push, spec-lint reports any `spec.md` of a feature numbered 377 or above, in
  the push's delta, that has no approval line of FR-001's form.
- **FR-005 - The refusal carries the fix.** Each refusal states the line's exact form and that the session must ask
  the GM (the refusals of FR-011 and FR-012 name finishing and closing first). It names which check failed: no line, too short, or not found among the GM's messages. A test pins the
  text.
- **FR-006 - No escape for the session.** Neither the commit guard, the push backstop nor the push check of FR-011
  and FR-012 has an escape variable. The
  GM's approval is the only way through.
- **FR-007 - The guidelines.**
  - CLAUDE.md's development-workflow bullet that says "Defer work by filing a feature" says instead: never file a
    feature without the GM's approval; propose it in the turn's final message; prefer extending and reopening
    the feature the work came from.
  - `docs/spec-kit-and-reviews.md` records the rule with the GM's words.
  - `make claim` prints the approval line's form when it claims.
  - The guard table in CLAUDE.md gains the guard's row.
- **FR-008** - withdrawn in round 1 (376 gets no approval line; D1).
- **FR-009 - spec-fidelity checks the approval's subject.** Its contract adds: an approval line's quote must approve
  the feature it sits in; otherwise the verdict is NOT FAITHFUL.
- **FR-011 - A reopen that lands open needs approval** (amendment 1). When a session runs `scripts/sync-with-main.sh
  done` or `push`, every feature that was SETTLED at the delta's base and is OPEN at its head is refused, unless the delta
  adds an approval line to its `spec.md` whose quote the GM wrote in this session (as FR-002 reads the GM's messages).
  SETTLED means no session work is left: `make speckit-todo`'s `closed` (a status line opening `Done`, `Superseded by`
  or `Withdrawn`, or every task ticked) or its `done - GM review pending`, which speckit-todo lists among the open but
  which holds only the GM's own box. Anything else is open. A feature reopened and SETTLED again within the delta passes
  with no approval. Any feature number. The refusal names the approval-free route FIRST: finish the work and close
  the feature, then land it (the work stays committed in the clone and backed up meanwhile); the approval line is the
  way to land it open. A push of the reopened feature's `specs/` directory alone is held like any other.
- **FR-012 - Open work hidden under a closed status** (amendment 1). The same push check refuses a delta that adds an
  unticked task to a feature whose status line still opens `Done`, `Superseded by` or `Withdrawn` at HEAD: speckit-todo
  reads it as closed and the GM would never see the work. Its refusal leads, as FR-011's does, with doing the work and ticking the task
  before landing; the same approval line, added in the delta, lets it land open.
- **FR-010 - Tested.** The guard has a suite under `tests/hooks/` run by `make hooks-test`, covering every scenario
  above (no line, short quote, foreign quote, the GM's quote, an AskUserQuestion answer, a rename, a feature below
  377). The spec-lint check has a test, and a test proves each guard fires on the unguarded case.

## Success Criteria

- **SC-001** (FR-001, FR-002, FR-005, FR-006, FR-010): in the guard's suite, a new feature with no approval line, one with a quote of fewer than three words,
  and one with words the GM did not write are each refused at `git commit` and at `git add`. One quoting the GM's words
  passes.
- **SC-002** (FR-001, FR-002, FR-004): no feature numbered below 377 is refused or reported by either check; a run over today's `specs/` reports
  nothing.
- **SC-003** (FR-004, FR-010): the push refuses a delta that adds a 377-or-later spec without the line.
- **SC-004** (FR-007): CLAUDE.md no longer contains "Defer work by filing a feature".
- **SC-005** (FR-009): spec-fidelity's contract asks whether the approval line approves the feature it sits in.
- **SC-006** (FR-003, FR-008): the withdrawn requirements stay withdrawn - no commit-time gate on a reopen (FR-011
  judges what lands instead), and 376 carries no approval line.
- **SC-007** (FR-011, FR-012, FR-010): in the guard's suite, a push carrying a feature reopened and left open is refused; one
  reopened and settled again passes; one left open with the GM's quoted approval added passes; a feature open at the
  base and still open is not this check's; an unticked task added under a `Done` status is refused.

## What it does not cover

- **Features below 377**: never checked, as the GM asked. 376 was filed before the request and stays as it is.
- **Commits the guard cannot see**: one made outside a Claude Code session, and one a session makes inside a `make`
  target or a script (the guard reads the command line, as every commit guard here does). The push backstop checks the
  line's form on both, not the transcript.
- **A reopen pushed outside a session** (by hand, or the GM's own): FR-011 and FR-012 run as a session hook, so only
  a session's push is held; whether an added approval line is there could be read without the transcript, but who
  wrote it could not, and that push is not checked.
- **Whether the GM meant THIS feature**: the guard verifies only that the words are the GM's. `spec-fidelity` judges
  the subject (FR-009).

## Decisions Recorded

- **D1 - The boundary is 377**, the first feature filed after the request ("only be with new features um, going
  forward"). Round 1 ruled a boundary at 376, with an approval line written for it, not legitimate: the GM's reply
  accepted 376 after the fact and said they would have preferred 347 reopened, which is not an approval to file.
- **D2 - Commit-time, in the session's own hooks, not a git pre-commit hook.** Every other commit guard here
  (`conflict-marker-hooks.sh`) is a Claude Code hook. Only such a hook can read the session transcript, which is what
  makes the approval verifiable rather than typed. A git pre-commit hook would also need installing in every clone.
  What neither can see, a commit made outside a session, is what the push backstop is for.
- **D4 - Amendment 1 does not relax FR-002.** The amendment speaks of an old feature reopened; the original request
  objects to the filing itself ("why are you even putting it in a branch if I didn't say to make it?"). A new feature
  still needs the approval at its first commit, whether or not the session finishes it.
- **D3 - The constitution is not amended.** It does not say to defer work by filing a feature; that is CLAUDE.md's
  wording, from feature 330. Principle XIV's "deferred with the measurement and the sketch" is satisfied by a
  proposal to the GM.

## Assumptions

- A headless session's prompt is not the GM's message (its `promptSource` is `sdk`), so a quote forwarded into one does
  not approve a feature there; a sub-session does not file features.
- Claude Code passes a transcript path to PreToolUse hooks. The GM's typed prompts sit in it as `user` records with string
  content, and messages sent mid-turn as `queued_command` attachments, each marked with a human origin and separate
  from tool results and harness notices (measured by the plan review, 2026-10-10).

## Review history

- spec-fidelity, Mode 2, round 1 (2026-10-10): CHANGES REQUIRED. Applied:
  - FR-003 (gating a reopen) dropped, with its edge case and test. It was not asked, it gated the path the GM
    prefers, and it reached older features; it is asked of the GM instead.
  - The boundary moved from 376 to 377 and FR-008 dropped: the line on 376 would have presented an after-the-fact
    acceptance as an approval to file (D1).
  - 377's own approval line now quotes the GM's request to build it, not the rule.
  - Non-blocking, also applied: commits made inside a `make` target or script are named as unseen; a short picked
    answer may be quoted with its question.
- spec-fidelity-verify, Mode 3, round 2 (2026-10-10): **FAITHFUL**. Every round 1 item resolved. One non-blocking
  note, applied: FR-001 names the question-and-answer form of a quote, so it agrees with FR-002.
- Form fix after acceptance (2026-10-10), no behavior changed: each success criterion names the requirements it covers
  (spec-lint check 3), and SC-005 and SC-006 were added to cover FR-009 and the two withdrawn ids.
- Amendment 1 (2026-10-10, the GM's words in request.md): FR-011 added - a reopened feature that lands open needs the
  GM's approval; one reopened, worked and closed again does not. The reopen edge case and SC-006/SC-007 follow.
- spec-fidelity, Mode 2, amendment 1 round 1 (2026-10-10): CHANGES REQUIRED. Applied: FR-011 states its own settled
  rule (speckit-todo lists `done - GM review pending` as open; this check counts it settled, as no session work is
  left); the reopen refusal leads with finishing and closing; FR-006 covers the push check; FR-012 added for open
  tasks under a closed status; the does-not-cover line corrected; D4 records that FR-002 is unchanged.
- spec-fidelity-verify, amendment 1 round 2 (2026-10-10): CHANGES REQUIRED, two wordings. Applied: FR-011's operative
  sentence and its pass case use SETTLED; FR-012's refusal leads with doing the work, as FR-011's does (FR-005 widened).

