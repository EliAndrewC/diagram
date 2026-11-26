# Brief - feature 452 T003 (0097), session 2: check and apply

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

The previous session's handoff is `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p7-rowhouse-write.md`. Your units are
the RECORD checks owed on what that handoff names: 0097 (both pages and their notes) (and any split page or registry entry it lists). What it
wrote: on the question page the finding "How big was a staff rowhouse?" restated - what the 80 and 145 ft rest on, rows past 145 ft recorded twice (Matsusaka quoted; Sakai by this project's count off a scaled redrawing), no measured row under about 60 ft at an office - with up to six new registry entries; on the drawing page the barracks' 145 ft ceiling relabeled as this project's limit and the 48 ft row labeled a GUESS. An older owed unit on another question is another builder's: leave it and report it. Leave every `modal-*`
unit alone.

**Held on purpose.** Two figures are THIS PROJECT'S measurements off an author's scaled redrawing (Sakai's doshin rows, about 270 to 290 ft from a count of dwellings; Sakai's two-dwelling block, about 70 by 45 ft) and are labeled so: a quote-check finding that the source does not state them is answered by the label and the arithmetic in the comment, not by deleting them - if the check will not have it, report `OPEN`. The pop-up `sheet/retainers--quarters` ("80 to 145 ft") is the coordinator's.

## What to do

1. Read the handoff: `make lines FILE=/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p7-rowhouse-write.md KEY='^- |^R[1-9]|^## |^CHECKED|^OPEN|^FOUND'`.
2. `make record-owed`. For each record check it names on your units, run its mechanical prepass first
   (`make quote-verbatim Q=<stem> NOTES=<notes>` before quote-check; `make record-prepass Q=<stem>` before record-format;
   the others as the record's `CLAUDE.md` names them), then `make check-bundle` for it. Dispatch ALL the checks in ONE
   message, in the FOREGROUND, each prompt naming its bundle's MANIFEST; save each reply to a file under
   `/tmp/pb-checks/p7-rowhouse/`. If a dispatch is refused as tied to another task, repeat it with `DECIDE_OK="<reason of two
   words or more>"` and say so in the handoff.
3. Apply each reply's EDITs with `make apply-edits FROM=<the saved reply>`; fix by hand what has no EDIT; record every check
   with `make record-checked CHECK=<check> BUNDLE=<bundle> RESULT=<result>`. Then `make record-owed` again and run what it
   re-owes: at most TWO rounds a check. A third round is the round arbiter's - do not run it, report the unit `OPEN`.
   A check's EDIT that would put back text an earlier round replaced, change an existing item tag's `data-guess`, or drop
   a labeled GUESS is not applied: report it `OPEN` with the reply's file, use no escape.
4. `make record CHECK=1`, `make record`, `make glossary`, `make question-sizes`,
   `make rust-test CRATE=rust/gate/crates/registry`, and `make record-owed` once more (nothing of yours owed, or said why).
5. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p7-rowhouse-check.md`: one line per check run
   (`CHECKED <check> <unit> round <n>: <verdict counts>; EDITs applied <n>, refused <n>; re-owed yes|no`), every file you
   changed under `## Files`, each page's prose size, what is `OPEN` and why, and - for the coordinator's cascade
   comparison - under `## Wording that pop-ups or claims may echo`, every sentence a check changed that a pop-up or a
   `Research:` claim could be quoting (old words, new words). Your last message is one paragraph.
