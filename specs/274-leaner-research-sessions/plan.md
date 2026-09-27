# Implementation Plan: Leaner research sessions

**Feature**: `274-leaner-research-sessions` | **Date**: 2026-09-27 | **Spec**: [spec.md](spec.md)

## Summary

Three changes to the research process, from research.md R1:
- a cap on write sessions: at most four questions assigned, counted by the runner, and at most ten new registry keys,
  counted by `make reserve`, with the rest continued in a new session;
- coordination files read and written by line;
- a slim rules file in place of the root CLAUDE.md for headless page sessions.

Then land, and tell the research sessions.

## Decisions

- **D1 - One counting helper, `scripts/_brief_load.py`** (FR-001). `load(text, record) -> (kind, questions, detail)`.
  - An exempt kind is read from `<!-- page-load: kind=check|assertions|split|handover -->`.
  - Otherwise the helper reads only the assignment lists: the `## Your items` section (up to the next `## `), and the
    `**Your questions:**` and `**Your pairs**` lines or blocks.
  - In an item line it counts each section named: `<page>/NNN` (the last segment of a page name is accepted as an
    alias), and a backticked `NNN` under the page named last, or else under the item list's most-named page.
  - A range `NNN-MMM` is expanded against the page's actual `NNN-*.html` fragments. Code references such as
    `file.py:195-304` are ignored.
  - An item line naming no section counts one question per distinct item id, and at least one. The check-brief form
    `PAGE=<p> SECTION=<NNN>` counts one each.
  - The page names are derived from the record's directories, not listed by hand.
  - It was prototyped on the real briefs: 269's V2 counts 9, C1 6 and X1 10; 272's S counts 8; 271's `g1-check-a` and
    269's `h1-check-a` count 2 each. It errs toward over-counting, which is the safe side for a cap.
- **D2 - The runner enforces it** (FR-001).
  - `plan()` checks every brief listed at launch and refuses before anything detaches: exit 2, with a message naming
    the count, the sections, the split and `WRITE_CAP_OK`.
  - `work()` checks each brief a `then:` step prints. A refused one writes `STOPPED <brief>: <reason>` to the run log
    and ends the queue.
  - `WRITE_CAP_OK='<reason>'` (two words or more) lets a brief through. The escape writes a guard-log entry in
    `~/.claude/guard-log/`'s format (`guard page-session`, `event escaped`, `rule write-cap`), so `make audit` counts it.
- **D3 - Continuation** (FR-001, the key half).
  - Each session runs with `L7R_PAGE_SESSION=<sid>` and `L7R_CONTINUE=<its log dir>/continue.md`.
  - When a session ends and that file exists, the runner queues it next, counted like any brief, and logs
    `continued <sid> -> <new sid>`.
  - The continuation lands between the write session and the group's `then:` checks step, so the checks see both
    sessions' handoff lines. A continuation brief appends to the same handoff.
- **D4 - The key cap in `make reserve`** (FR-001).
  - `reserve-prefix.py` records `session` (`L7R_PAGE_SESSION`) on every ledger row.
  - The cap covers WRITE sessions only (plan review round 1: FR-001 caps "a write session", and a check session is
    not capped). The runner exports `L7R_KEY_CAP=10` only to a session whose brief declares no exempt kind, and to that
    brief's continuations; a check, assertions, split or handover session never sees it.
  - With `L7R_KEY_CAP` and a session set, a registry reservation past the tenth for that session is refused with the
    continuation instruction: finish the question in hand, write the unreached items to `$L7R_CONTINUE` as a brief of the same shape
    (same header, `## Your items`, the same handoff path), commit, and stop.
  - `KEY_CAP_OK='<reason>'` passes it; the Makefile passes it through, and it is guard-logged.
  - Glossary terms are not capped.
- **D5 - `make lines` and `make append`** (FR-002), in `scripts/_coord.py`.
  - `lines FILE= KEY=<regex>` prints the matching lines, numbered, at most 80, then `(<n> of <total> lines shown)`, and
    `(<m> more matched - narrow KEY)` when the 80 cut matches off, so a cut never passes for the whole answer.
  - `append FILE= LINE=` appends one line, creating the file if needed, and prints only `appended to <file>`. It reads
    `LINE` from the environment (make exports command-line variables to recipes), so quotes in it survive.
- **D6 - The slim rules file** (FR-003): `container-scripts/page-session-rules.md`, from the draft this feature was given.
  - The runner's `floor_flags` appends it after the standing authorizations, in ONE `--append-system-prompt` (moved
    there from `page-session.sh`, so the flag the test reads is the flag a session is started with).
  - `floor_flags` adds the clone's own root `CLAUDE.md` to `claudeMdExcludes`; the mirror's was already there. The
    research record's CLAUDE.md still auto-loads.
  - A drift test maps every bullet of the root CLAUDE.md's `### House style` and `### Research` sections to a phrase in
    the slim file, or to a stated "not for page sessions" entry. It fails on a bullet count it does not know.
- **D7 - `brief.py` declares its kinds** (FR-001): `assertions` on its page briefs (`COMMON`/`WRITE`), `check` on its
  2a/2b and owed-modal briefs, and `split` on its split briefs. Tested.
- **D8 - Docs** (FR-001, FR-002): the research CLAUDE.md's page-session paragraph, `docs/research-record-rules.md`'s
  "Two sessions per page" and the root CLAUDE.md's research bullet state both limits (four questions, ten registry keys),
  the continuation, the `<!-- page-load: kind=... -->` line with its four exempt kinds (`check`, `assertions`, `split`,
  `handover`), and the read-by-line rule, with research.md R1's figures (plan review round 1).
- **D9 - The probe** (FR-004): one trivial headless session under the old flags and one under the new, each answering
  one line. Their first-turn input tokens are recorded as research.md R2. That is two sessions of one turn each; the
  cost is stated before launch (about 50 K tokens).
- **D10 - The owed measurement** (FR-004): `.claude/skills/diagram/future-work/cross-cutting.md` gets the post-landing
  measurement, with `measure/`'s scripts and R1's baseline: median 1.02 M a thing, peak 246 K, write sessions a median
  of 74 turns.
- **D11 - Telling the sessions** (FR-005): done by the session "Diagram supplemental" after the landing is on main. It
  sends one message to each research session, says what changed and what their generators may now hit, and records it
  in the peer log.

## Constitution check

- XIII: the runner, reserve and the Makefile targets are tested; `make done` runs before the push.
- Guards: the refusal names the compliant split and the escape, and the escape is logged with its reason.
- XVI: every requirement is built as specified; the review rounds are in the spec.

## Review history

- Round 1 (spec-fidelity, 2026-09-27): BLOCKED, two findings. (1) D4 capped keys in every page session; the cap is
  now exported only to a session whose brief declares no exempt kind, and to its continuations. (2) D8 left out the
  `page-load` line; it now names it with its four kinds. Also taken from the asides: `make lines` says when its
  80-line cut dropped matches. D6's append moved into the runner so the tested flags are the launched ones.
