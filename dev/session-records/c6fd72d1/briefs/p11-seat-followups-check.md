# Brief - feature 449 (0057, 0031, 0081), session 2: check and apply

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

The previous session's handoff is `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p11-seat-followups-write.md`. Your units are
the RECORD checks owed on what that handoff names: 0057, 0031 and 0081 (each its drawing page) and the NEW drawing-only question the handoff names (and any split page or registry entry it lists). What it
wrote: on 0057's drawing page a DEVIATION item `toe-on-tapering-flank` (the wet ground the point-by-point edge lays up a flank that tapers inward downhill); on 0031's drawing page a MOVE - the section on a scattered farm's reach of its rice (two blocks and the rule paragraph, word for word) to a new drawing-only question, a `<a class="moved">` pointer left where it stood - and then one GUESS item, `seat-astride-brook-windward-corner`; on 0081's drawing page one GUESS item, `way-out-from-band-ends`. An older owed unit on another question is another builder's: leave it and report it. Leave every `modal-*`
unit alone.

**Held on purpose.** (1) The moved blocks were moved UNCHANGED: a check's EDIT to their wording on the new page is applied only where the check finds a real fault (a broken link, a note that did not come with its sentence); a style rewording of text that stood checked on the old page is not this unit - report it `OPEN`. First confirm the move lost nothing: `git -C /diagram/.clones/diagram-backlog diff --stat -- research/questions` and compare the moved text on the new page with `git -C /diagram/.clones/diagram-backlog show HEAD:research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html` (the lines from "A scattered farm fronts its own fields" down to the paragraph "The rule the map follows: a scattered settlement needs roughly twice the room per farm"); a lost or altered claim-bearing word is put back before any check runs. A new question owes its intro check: run it with the rest. (2) The three new items record what the map draws since feature 449 T426, labeled on purpose: a check may correct a label's note or wording, never delete an item or rename its slug (the engine's claims will cite them). (3) On 0057 the item is labeled DEVIATION and says what the map DRAWS on a tapering flank; whether the code should instead cut the wet ground off at the field's lower corners is the coordinator's open question, not a check's: an EDIT that turns the block into a rule that the wet ground SHOULD climb the flank, or that removes the block as a defect, is not applied - report it `OPEN` with the reply's file. (4) On 0031 the block "Where does a village's cluster sit?" and its two tags were not edited: apply no EDIT that changes either tag.

**The cascade the coordinator expects (not your work).** `seat.rs` `BAND_EXITS#the way out from the band's ends` and `open_at_an_end#a seat astride the brook leaves by its open bank` say the pages are silent and will be restated to cite the new item ids; `choice/cluster_position--high_margin` and `hamlet/marsh` are the pop-ups that state the seat's rule and the marsh's upper edge. So under `## Wording that pop-ups or claims may echo` list, with old and new words, any sentence a check changed about the wet flank, the seat astride the brook, a fall square across the wind, or the point a way out is asked from.

## What to do

1. Read the handoff: `make lines FILE=/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p11-seat-followups-write.md KEY='^- |^N[1-9]|^## |^CHECKED|^OPEN|^FOUND'`.
2. `make record-owed`. For each record check it names on your units, run its mechanical prepass first
   (`make quote-verbatim Q=<stem> NOTES=<notes>` before quote-check; `make record-prepass Q=<stem>` before record-format;
   the others as the record's `CLAUDE.md` names them), then `make check-bundle` for it. Dispatch ALL the checks in ONE
   message, in the FOREGROUND, each prompt naming its bundle's MANIFEST; save each reply to a file under
   `/tmp/pb-checks/p11-seat-followups/`. If a dispatch is refused as tied to another task, repeat it with `DECIDE_OK="<reason of two
   words or more>"` and say so in the handoff.
3. Apply each reply's EDITs with `make apply-edits FROM=<the saved reply>`; fix by hand what has no EDIT; record every check
   with `make record-checked CHECK=<check> BUNDLE=<bundle> RESULT=<result>`. Then `make record-owed` again and run what it
   re-owes: at most TWO rounds a check. A third round is the round arbiter's - do not run it, report the unit `OPEN`.
   A check's EDIT that would put back text an earlier round replaced, change an existing item tag's `data-guess`, or drop
   a labeled GUESS is not applied: report it `OPEN` with the reply's file, use no escape.
4. `make record CHECK=1`, `make record`, `make glossary`, `make question-sizes`,
   `make rust-test CRATE=rust/gate/crates/registry`, and `make record-owed` once more (nothing of yours owed, or said why).
5. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p11-seat-followups-check.md`: one line per check run
   (`CHECKED <check> <unit> round <n>: <verdict counts>; EDITs applied <n>, refused <n>; re-owed yes|no`), every file you
   changed under `## Files`, each page's prose size, what is `OPEN` and why, and - for the coordinator's cascade
   comparison - under `## Wording that pop-ups or claims may echo`, every sentence a check changed that a pop-up or a
   `Research:` claim could be quoting (old words, new words). Your last message is one paragraph.
