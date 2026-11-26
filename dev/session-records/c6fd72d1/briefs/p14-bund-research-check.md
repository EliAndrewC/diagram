# Brief - feature 449 (0014, 0284), session 2: check and apply

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

The previous session's handoff is `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p14-bund-research-write.md`. Your units are
the RECORD checks owed on what that handoff names: 0014 (its research page), 0284 (its drawing page), the NEW research question the handoff names, and the registry entry `ishiguro-azemame-tool` (and any split page or registry entry it lists). What it
wrote: on 0014's research page a MOVE - the section on why a hand-piled bund wavers (its opening paragraph and five blocks, word for word) to a new research-only question, a `<a class="moved">` pointer left where it stood - and then one new block in the bund-bean section (the Ishiguro village's beans, holes about a foot apart, two or three to a hole, one row down the bund); in the registry entry `ishiguro-azemame-tool` its `What it is:` place-name sourced or cut; on 0284's drawing page the block `comb-bund-bow` restated (no SOURCE gives how far a bund bowed; the record's own reading guesses a foot or two over a hundred feet) with its `data-guess`. An older owed unit on another question is another builder's: leave it and report it. Leave every `modal-*`
unit alone.

**Held on purpose.** (1) The moved blocks were moved UNCHANGED: a check's EDIT to their wording on the new page is applied only where the check finds a real fault (a broken link, a note that did not come with its sentence); a style rewording of text that stood checked on the old page is not this unit - report it `OPEN`. First confirm the move lost nothing: `git -C /diagram/.clones/diagram-backlog diff --stat -- research/questions` and compare the moved text on the new page with `git -C /diagram/.clones/diagram-backlog show HEAD:research/questions/0014-bunds-between-the-paddies-aze.html` (lines 26-33: from "Why a hand-piled bund wavers is written down nowhere we looked" to the block "Where a real boundary did step"); a lost or altered claim-bearing word is put back before any check runs. A new question owes its intro check: run it with the rest. (2) `comb-bund-bow`'s `data-guess` was rewritten BY THE WRITE BRIEF'S STATED EXCEPTION (no pop-up cites the slug): do not refuse it or put the old one back. (3) The registry entry's edit re-owes `source-applicability` on it: run it with the rest.

**The cascade the coordinator expects (not your work).** `hamlet/bund-beans` is the pop-up that says how far a plant spread is not recorded; `hamlet/bund` and `choice/plot_regularity--organic` state the moved section. Under `## Wording that pop-ups or claims may echo` list, old and new, any sentence a check changed on the beans' spacing, a bund's bow or wander, or the corners.

## What to do

1. Read the handoff: `make lines FILE=/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p14-bund-research-write.md KEY='^- |^B[1-9]|^## |^CHECKED|^OPEN|^FOUND'`.
2. `make record-owed`. For each record check it names on your units, run its mechanical prepass first
   (`make quote-verbatim Q=<stem> NOTES=<notes>` before quote-check; `make record-prepass Q=<stem>` before record-format;
   the others as the record's `CLAUDE.md` names them), then `make check-bundle` for it. Dispatch ALL the checks in ONE
   message, in the FOREGROUND, each prompt naming its bundle's MANIFEST; save each reply to a file under
   `/tmp/pb-checks/p14-bund-research/`. If a dispatch is refused as tied to another task, repeat it with `DECIDE_OK="<reason of two
   words or more>"` and say so in the handoff.
3. Apply each reply's EDITs with `make apply-edits FROM=<the saved reply>`; fix by hand what has no EDIT; record every check
   with `make record-checked CHECK=<check> BUNDLE=<bundle> RESULT=<result>`. Then `make record-owed` again and run what it
   re-owes: at most TWO rounds a check. A third round is the round arbiter's - do not run it, report the unit `OPEN`.
   A check's EDIT that would put back text an earlier round replaced, change an existing item tag's `data-guess`, or drop
   a labeled GUESS is not applied: report it `OPEN` with the reply's file, use no escape.
4. `make record CHECK=1`, `make record`, `make glossary`, `make question-sizes`,
   `make rust-test CRATE=rust/gate/crates/registry`, and `make record-owed` once more (nothing of yours owed, or said why).
5. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p14-bund-research-check.md`: one line per check run
   (`CHECKED <check> <unit> round <n>: <verdict counts>; EDITs applied <n>, refused <n>; re-owed yes|no`), every file you
   changed under `## Files`, each page's prose size, what is `OPEN` and why, and - for the coordinator's cascade
   comparison - under `## Wording that pop-ups or claims may echo`, every sentence a check changed that a pop-up or a
   `Research:` claim could be quoting (old words, new words). Your last message is one paragraph.
