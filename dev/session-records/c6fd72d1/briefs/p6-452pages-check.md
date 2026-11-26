# Brief - feature 452 T016 and T012 (0093, 0101, 0220), session 2: check and apply

<!-- page-load: kind=check -->

You are a FRESH headless page session. This brief is the whole of what you need. Work only in this clone,
`/diagram/.clones/diagram-backlog`, from its root (`cd` into it in every command; `git -C` for every git call).
`scripts/container/page-session-rules.md` is in your system prompt; the research record's `CLAUDE.md` loads when you touch
`research/`.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; touch only
the files your units need and list them in the handoff. Never run `scripts/sync-with-main.sh`, never push, and never push
the archive by hand. Do not edit any `Research:` claim, `dev/claims-index.json`, `pool/`, `docs/`, `rust/`, the `Makefile`
or any pop-up (`l7r/diagram/interactive/assets/modals/`). Do not run `make claims-*` or `make modal-*` (the orchestrating
session runs the claims' and the pop-ups' checks, and compares that cascade with the write brief's prediction). A citation
quotes its passage verbatim from the page you read; read the archived copy first (`make archive-find`).

## Your units

The previous session's handoff is `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p6-452pages-write.md`. Your units are
the RECORD checks owed on what that handoff names: 0093, 0101 and 0220 (each its drawing page) and the registry entry `jawiki-yashikigami` (and any split page or registry entry it lists). What it
wrote: on 0093's drawing page the gatekeepers' block restated to a knob (a gatehouse of its own beside the gate or behind it) and a GUESS item `gatehouse-behind-setback`; on 0101's drawing page the 5 ft square privy narrowed to a samurai house's, taken from the smallest farm privy counted; on 0220's drawing page one sentence (an office's shrine follows the household-shrine page by analogy) and on the registry entry `jawiki-yashikigami` two limits and a `Used for:` line, applied from a saved source-applicability reply. An older owed unit on another question is another builder's: leave it and report it. Leave every `modal-*`
unit alone.

**The source-applicability check is re-owed on `jawiki-yashikigami`** because its entry changed: run it as `make record-owed` names it. It is the SAME check whose reply the write session applied (saved at `/home/agent/.claude/jobs/c6fd72d1/tmp/briefs/reply-452-t012-source-applicability-0220.md`): this run counts as its round 2 on that entry, so if it returns anything but a clean verdict, apply its EDITs once and report the unit `OPEN` rather than run a third round.

## What to do

1. Read the handoff: `make lines FILE=/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p6-452pages-write.md KEY='^- |^G[1-9]|^## |^CHECKED|^OPEN|^FOUND'`.
2. `make record-owed`. For each record check it names on your units, run its mechanical prepass first
   (`make quote-verbatim Q=<stem> NOTES=<notes>` before quote-check; `make record-prepass Q=<stem>` before record-format;
   the others as the record's `CLAUDE.md` names them), then `make check-bundle` for it. Dispatch ALL the checks in ONE
   message, in the FOREGROUND, each prompt naming its bundle's MANIFEST; save each reply to a file under
   `/tmp/pb-checks/p6-452pages/`. If a dispatch is refused as tied to another task, repeat it with `DECIDE_OK="<reason of two
   words or more>"` and say so in the handoff.
3. Apply each reply's EDITs with `make apply-edits FROM=<the saved reply>`; fix by hand what has no EDIT; record every check
   with `make record-checked CHECK=<check> BUNDLE=<bundle> RESULT=<result>`. Then `make record-owed` again and run what it
   re-owes: at most TWO rounds a check. A third round is the round arbiter's - do not run it, report the unit `OPEN`.
   A check's EDIT that would put back text an earlier round replaced, change an existing item tag's `data-guess`, or drop
   a labeled GUESS is not applied: report it `OPEN` with the reply's file, use no escape.
4. `make record CHECK=1`, `make record`, `make glossary`, `make question-sizes`,
   `make rust-test CRATE=rust/gate/crates/registry`, and `make record-owed` once more (nothing of yours owed, or said why).
5. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p6-452pages-check.md`: one line per check run
   (`CHECKED <check> <unit> round <n>: <verdict counts>; EDITs applied <n>, refused <n>; re-owed yes|no`), every file you
   changed under `## Files`, each page's prose size, what is `OPEN` and why, and - for the coordinator's cascade
   comparison - under `## Wording that pop-ups or claims may echo`, every sentence a check changed that a pop-up or a
   `Research:` claim could be quoting (old words, new words). Your last message is one paragraph.
