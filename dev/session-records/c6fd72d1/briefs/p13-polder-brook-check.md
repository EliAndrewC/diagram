# Brief - feature 449 (0018, 0008, 0059), session 2: check and apply

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

The previous session's handoff is `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p13-polder-brook-write.md`. Your units are
the RECORD checks owed on what that handoff names: 0018, 0008 and 0059 (each its drawing page) (and any split page or registry entry it lists). What it
wrote: on 0018's drawing page one new GUESS item, `feeder-and-run-ring-width` (on a dike-pond block the feeder and the outfall's run beyond the dike drawn at the ring canal's width, with its own ABSENCE note); on 0008's drawing page the block `pond-bank-and-margin-width` restated as drawn (the bank line about 2.5 ft out from the water, under a foot of wet ground showing); on 0059's drawing page the block `brook-line-below-intake` scoped to the intake's siting (from a bend it holds the intake's line; from a straight reach it first steps out to its keep-clear line). An older owed unit on another question is another builder's: leave it and report it. Leave every `modal-*`
unit alone.

**Held on purpose.** (1) The `data-guess` of `pond-bank-and-margin-width` and of `brook-line-below-intake` were rewritten BY THIS BRIEF'S STATED EXCEPTIONS (no pop-up cites either slug): do not refuse them or put the old ones back; any other change to an existing tag is refused as the template says. (2) `feeder-and-run-ring-width` states what 449 T431's code will draw (the code follows this pair): a check that finds the map today draws a 3 ft feeder and a 5.5 ft run is right, and that is not a fault of the page - an EDIT that writes today's widths back into the block is not applied; report it `OPEN` with the reply's file. A check may correct the item's note or wording, never delete it or rename its slug. (3) W2 and W3 restate what the code draws; an EDIT that puts back "the wet ground inside it about 2.5 ft wide" or "holds the intake's line" for every shoulder intake is not applied.

**The cascade the coordinator expects (not your work).** Under `## Wording that pop-ups or claims may echo` list, old and new, any sentence a check changed on a feeder's or an outfall run's width, a pocket pond's bank or wet margin, or how far the brook keeps an intake's line.

## What to do

1. Read the handoff: `make lines FILE=/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p13-polder-brook-write.md KEY='^- |^W[1-9]|^## |^CHECKED|^OPEN|^FOUND'`.
2. `make record-owed`. For each record check it names on your units, run its mechanical prepass first
   (`make quote-verbatim Q=<stem> NOTES=<notes>` before quote-check; `make record-prepass Q=<stem>` before record-format;
   the others as the record's `CLAUDE.md` names them), then `make check-bundle` for it. Dispatch ALL the checks in ONE
   message, in the FOREGROUND, each prompt naming its bundle's MANIFEST; save each reply to a file under
   `/tmp/pb-checks/p13-polder-brook/`. If a dispatch is refused as tied to another task, repeat it with `DECIDE_OK="<reason of two
   words or more>"` and say so in the handoff.
3. Apply each reply's EDITs with `make apply-edits FROM=<the saved reply>`; fix by hand what has no EDIT; record every check
   with `make record-checked CHECK=<check> BUNDLE=<bundle> RESULT=<result>`. Then `make record-owed` again and run what it
   re-owes: at most TWO rounds a check. A third round is the round arbiter's - do not run it, report the unit `OPEN`.
   A check's EDIT that would put back text an earlier round replaced, change an existing item tag's `data-guess`, or drop
   a labeled GUESS is not applied: report it `OPEN` with the reply's file, use no escape.
4. `make record CHECK=1`, `make record`, `make glossary`, `make question-sizes`,
   `make rust-test CRATE=rust/gate/crates/registry`, and `make record-owed` once more (nothing of yours owed, or said why).
5. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p13-polder-brook-check.md`: one line per check run
   (`CHECKED <check> <unit> round <n>: <verdict counts>; EDITs applied <n>, refused <n>; re-owed yes|no`), every file you
   changed under `## Files`, each page's prose size, what is `OPEN` and why, and - for the coordinator's cascade
   comparison - under `## Wording that pop-ups or claims may echo`, every sentence a check changed that a pop-up or a
   `Research:` claim could be quoting (old words, new words). Your last message is one paragraph.
