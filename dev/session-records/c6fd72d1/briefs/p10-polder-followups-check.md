# Brief - feature 449 (0018, 0019), session 2: check and apply

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

The previous session's handoff is `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p10-polder-followups-write.md`. Your units are
the RECORD checks owed on what that handoff names: 0018 (its drawing page, and the one note `wuhurec-wanchun-5` of its research notes) and 0019 (its drawing page) (and any split page or registry entry it lists). What it
wrote: on 0019's drawing page three GUESS items - `ring-canal-width-dike-pond` (the ring canal of a dike-pond block drawn no narrower than the block's creeks), `creek-mouth-on-ring-canal`, `pinched-mosaic-eased` (or this last on 0018's drawing page, if the handoff says 0019 had no room); on 0018's drawing page the GUESS item `one-creek-width-a-block` and the least-pond block restated to its two cases, its tag's `data-guess` rewritten with it; in 0018's research notes ONE word of the note `wuhurec-wanchun-5`, "fiscal commissioner" made "transport commissioner". An older owed unit on another question is another builder's: leave it and report it. Leave every `modal-*`
unit alone.

**Held on purpose.** (1) The ring canal's width is written as a BOUND (no narrower than the creeks), a GUESS, because the code that draws it is feature 449 T427, not yet built: a check may correct how it is cited or noted, never turn the bound into a figure, delete the item or rename a slug (the engine's claims will cite `ring-canal-width-dike-pond`, `creek-mouth-on-ring-canal`, `pinched-mosaic-eased`, `one-creek-width-a-block`). The figure "about 6 to 8 ft" and the slug `creek-width-between-ponds` stand as the last pair left them. (2) The tag `least-pond` had its `data-guess` rewritten ON PURPOSE by the write session (the block now states two cases; no pop-up cites the tag): that is not the tag change step 3 refuses, and a check's EDIT that restores the one-case wording is not applied - report it `OPEN`. (3) On 0018's drawing page the block "The bank is drawn as planted ground" is a placeholder of feature 449 T422: apply no EDIT to it.

**The one phrase that looped last time - read this before step 2.** On 2026-11-24 the same word change (0018's note `wuhurec-wanchun-5`: "fiscal commissioner" to "transport commissioner", to agree with 0019's two notes and the glossary term; the original is 转运使) was made by hand AFTER the last pair's checks had run two rounds, and re-owed three units a third round each: `quote-check:0018#wuhurec-wanchun-5`, `record-format:0018`, `translation-check:0018#wuhurec-wanchun-5`. This time the write session made it, so those three units are EXPECTED in your first `make record-owed` and are this pair's ROUND 1: run each ONCE, in the same message as the rest. To keep it from looping: (a) if `make record-owed`, a dispatch guard or `make record-checked` calls any of them a third round or names the round arbiter (the counter may still hold the last pair's rounds), do NOT run it, use no escape and do NOT put the word back - report the unit `OPEN` with the refusal's line verbatim; the coordinator takes it to the arbiter, whose ruling of 2026-11-24 named this follow-up (`/home/agent/.claude/jobs/c6fd72d1/tmp/cascade/p1-cascade.md`, stage 1). (b) A check's EDIT that would render 转运使 any other way than "transport commissioner", on 0018 or on 0019, is not applied: `OPEN`, with the reply's file. (c) Apply EVERY reply's EDITs before the second `make record-owed`, so no check's one-phrase EDIT lands after another's round; and if round 2 leaves a unit owed only because another check's EDIT reworded a phrase (a synonym, a glossary term), that unit's next round is its third: do not run it, report it `OPEN` - the arbiter accepted exactly such units last time. 0019's two notes already agree and are not yours to change.

**The cascade the coordinator expects (not your work; it is why your handoff's last section matters).** After this pair the coordinator runs the claims' and the pop-ups' checks and expects: `rust/phases/src/field/polder.rs` `ditches#the ring canal on a dike-pond block` DRIFTED fix: code until T427 lands (it says the ring canal keeps 1.5 to 5.5 ft, narrower than a creek); `hamlet/pond-canal` to come to carry the width guess on its Guesses tab and to lose "not every dike-pond hamlet need have had water a boat could travel"; `hamlet/fish-pond`'s flat "lay in a mosaic among winding rivers" and `hamlet/sluice-gate`'s "the intake stood at the ring's upstream head and the outlet at its downstream tail" stated as fact to be found only by a directed check. So under `## Wording that pop-ups or claims may echo` list, with old and new words, any sentence a check changed about the ring canal's width, the creeks' width or mouth, the mosaic's bend, the least pond, or boats on the creeks.

## What to do

1. Read the handoff: `make lines FILE=/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p10-polder-followups-write.md KEY='^- |^K[1-9]|^## |^CHECKED|^OPEN|^FOUND'`.
2. `make record-owed`. For each record check it names on your units, run its mechanical prepass first
   (`make quote-verbatim Q=<stem> NOTES=<notes>` before quote-check; `make record-prepass Q=<stem>` before record-format;
   the others as the record's `CLAUDE.md` names them), then `make check-bundle` for it. Dispatch ALL the checks in ONE
   message, in the FOREGROUND, each prompt naming its bundle's MANIFEST; save each reply to a file under
   `/tmp/pb-checks/p10-polder-followups/`. If a dispatch is refused as tied to another task, repeat it with `DECIDE_OK="<reason of two
   words or more>"` and say so in the handoff.
3. Apply each reply's EDITs with `make apply-edits FROM=<the saved reply>`; fix by hand what has no EDIT; record every check
   with `make record-checked CHECK=<check> BUNDLE=<bundle> RESULT=<result>`. Then `make record-owed` again and run what it
   re-owes: at most TWO rounds a check. A third round is the round arbiter's - do not run it, report the unit `OPEN`.
   A check's EDIT that would put back text an earlier round replaced, change an existing item tag's `data-guess`, or drop
   a labeled GUESS is not applied: report it `OPEN` with the reply's file, use no escape.
4. `make record CHECK=1`, `make record`, `make glossary`, `make question-sizes`,
   `make rust-test CRATE=rust/gate/crates/registry`, and `make record-owed` once more (nothing of yours owed, or said why).
5. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p10-polder-followups-check.md`: one line per check run
   (`CHECKED <check> <unit> round <n>: <verdict counts>; EDITs applied <n>, refused <n>; re-owed yes|no`), every file you
   changed under `## Files`, each page's prose size, what is `OPEN` and why, and - for the coordinator's cascade
   comparison - under `## Wording that pop-ups or claims may echo`, every sentence a check changed that a pop-up or a
   `Research:` claim could be quoting (old words, new words). Your last message is one paragraph.
