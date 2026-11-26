# Brief - feature 449 (0057, 0006, 0011), session 2: check and apply

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

The previous session's handoff is `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p12-fan-dryplot-write.md`. Your units are
the RECORD checks owed on what that handoff names: 0057 (its research page and its drawing page), 0006 and 0011 (each its drawing page), and every NEW registry entry the handoff lists (and any split page or registry entry it lists). What it
wrote: on 0057's research page new blocks on where a fan's wet ground lies (its toe and front margin; nothing on its sides, which two sources class as early-cleared farmland; a wet side attested only for a valley floor against a hill foot, farmed as cold wet paddy) and the word "perimeter" for a wetland study's "edge"; on 0057's drawing page the same word, and the DEVIATION block `toe-on-tapering-flank` with its grounds and its `data-guess` restated; on 0006's drawing page the canal-squared block's grounds restated as a RECONSTRUCTION with its two limits (strips squared to a road beside a drinking-water canal; at Nobidome along the canal; none where the canal irrigated), a bend clause, and one new GUESS item `dry-plot-taper-at-bend`; on 0011's drawing page one phrase ("from the toe end of the canal, up along it"). Up to nine new registry keys. An older owed unit on another question is another builder's: leave it and report it. Leave every `modal-*`
unit alone.

**Held on purpose.** (1) `toe-on-tapering-flank`'s `data-guess` was rewritten BY THIS BRIEF'S STATED EXCEPTION (no pop-up cites the slug): do not refuse it or put the old one back; any other change to an existing tag's `data-item`, `data-label` or `data-guess` is refused as the template says. The block stays a DEVIATION that says what the map DRAWS: an EDIT that turns it into a rule that the wet ground SHOULD climb, or removes it as a defect, is not applied - report it `OPEN` with the reply's file (449 T432's code change follows this pair). (2) `dry-plot-taper-at-bend` is a GUESS recording what the code draws since 449 T423: a check may correct its note or wording, never delete it or rename its slug. (3) The Musashino frame stays a RECONSTRUCTION; an EDIT that relabels it accurate, or drops either limit, is refused.

**Two rulings the coordinator needs, each a named line in your handoff.** (a) `T432-APPLICABILITY <APPLIES|DOES-NOT-APPLY|CANNOT-TELL> - <the check's words>`: when you dispatch `source-applicability` on the new entries (the RIHN guide, the farm ministry's catch-channel sheet), add to its prompt, verbatim: "Also rule whether this valley-wall finding APPLIES to the drawn case: a hamlet's fields on a fan in a valley, one side of the fields narrowing downhill toward the head's corner along the brook; is that side a valley floor against a hill foot, where the sources attest a wet side, or a fan's side, where they do not? Read, for the drawn ground: research/questions/0057-marshes-and-wetlands-shitchi.drawing.html (the blocks 'The marsh is as wide as the fields above it' - 'the wet ground follows the fan, not the valley' - and 'Where the fields narrow inward downhill') and /diagram/.clones/diagram-backlog/.git/l7r-handoffs/T426-b1.md (its 'Causes (measured)' section: the seeds whose windward flank, along the brook, narrows downhill)." If no new entry makes `source-applicability` owed, run it once on the RIHN entry with that question and say so. (b) `T428 <CLOSES|CODE> - <why>`: CLOSES if every check leaves `dry-plot-taper-at-bend` saying what `rust/phases/src/field/dry.rs` draws (read it at HEAD, read only); CODE, with the check's words, if a check finds the drawn taper contradicts a finding.

**The cascade the coordinator expects (not your work).** Under `## Wording that pop-ups or claims may echo` list, old and new, any sentence a check changed on a fan's wet toe or its sides, the wet side, "perimeter", a plot square to its canal, the bend, or the last band's end.

## What to do

1. Read the handoff: `make lines FILE=/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p12-fan-dryplot-write.md KEY='^- |^F[1-9]|^## |^CHECKED|^OPEN|^FOUND'`.
2. `make record-owed`. For each record check it names on your units, run its mechanical prepass first
   (`make quote-verbatim Q=<stem> NOTES=<notes>` before quote-check; `make record-prepass Q=<stem>` before record-format;
   the others as the record's `CLAUDE.md` names them), then `make check-bundle` for it. Dispatch ALL the checks in ONE
   message, in the FOREGROUND, each prompt naming its bundle's MANIFEST; save each reply to a file under
   `/tmp/pb-checks/p12-fan-dryplot/`. If a dispatch is refused as tied to another task, repeat it with `DECIDE_OK="<reason of two
   words or more>"` and say so in the handoff.
3. Apply each reply's EDITs with `make apply-edits FROM=<the saved reply>`; fix by hand what has no EDIT; record every check
   with `make record-checked CHECK=<check> BUNDLE=<bundle> RESULT=<result>`. Then `make record-owed` again and run what it
   re-owes: at most TWO rounds a check. A third round is the round arbiter's - do not run it, report the unit `OPEN`.
   A check's EDIT that would put back text an earlier round replaced, change an existing item tag's `data-guess`, or drop
   a labeled GUESS is not applied: report it `OPEN` with the reply's file, use no escape.
4. `make record CHECK=1`, `make record`, `make glossary`, `make question-sizes`,
   `make rust-test CRATE=rust/gate/crates/registry`, and `make record-owed` once more (nothing of yours owed, or said why).
5. **Hand off.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/p12-fan-dryplot-check.md`: one line per check run
   (`CHECKED <check> <unit> round <n>: <verdict counts>; EDITs applied <n>, refused <n>; re-owed yes|no`), every file you
   changed under `## Files`, each page's prose size, what is `OPEN` and why, and - for the coordinator's cascade
   comparison - under `## Wording that pop-ups or claims may echo`, every sentence a check changed that a pop-up or a
   `Research:` claim could be quoting (old words, new words). Your last message is one paragraph.
