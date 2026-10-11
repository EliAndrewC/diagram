<!-- page-load: kind=check -->
# Brief - feature 343, session 4: the checks still owed, check and apply

You are a FRESH session for one part of one feature. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-research`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above
all.

**What moved since the last answers.** Session 3 (M1b) applied its checks' edits to 0104 and to the compound sheet's
pop-ups AFTER it recorded their answers, so no check has read the words as they stand; and the main session then added
"or left as bare earth" to 0104's sentence on the ground before an entrance and to its absence note
`entrance-ground-surface-absence` (the search comment now names the Morse searches for bare, hard, trodden and beaten earth).
Session 3's record is `specs/343-receiving-court-swept/briefs/m1-checks.md`.

**Your questions:** Q=0104 (and Q=0099 only if `make record-owed UNANSWERED=1` names it)
**Your pop-ups:** the `sheet/` ones `make record-owed UNANSWERED=1` names - border-court, clerks--seats, door, garden,
garden-pond, genkan, guest-quarters, kneeling-positions, magistrate-s-dais, main-gate, nakamon, office-hall, outer-court,
residence, side-gate.
**Your registry keys:** none expected.

## The procedure (check, apply)

1. `make record-owed UNANSWERED=1` names every unit still owed - work from that list only. Dispatch one agent per owed
   unit, in the background, each from its own bundle and naming its own MANIFEST.md, in waves of at most 20 per message
   (21 at once is refused):
   - quote-check: `make quote-verbatim Q=0104` then `make check-bundle Q=0104 FOR=quote-check`;
   - record-format: `make check-bundle Q=0104 FOR=record-format`;
   - source-reader: `make check-bundle Q=0104 FOR=source-reader` on `entrance-ground-surface-absence`;
   - each pop-up: `make modal-bundle KIND="sheet/<name>" FOR=modal-research`, `... FOR=modal-form` and
     `... FOR=modal-depiction` for the checks the list names for it.
2. Run `make apply-edits FROM=<each output_file>`; apply by hand only what it refuses or lists as `EDIT: none`.
3. Answer each check from the bundle it read - `make record-checked CHECK=<check> BUNDLE=<its bundle> RESULT="..."`. Its own edits then owe the unit again: re-check ONCE what moved, from a fresh bundle, and answer that round from its bundle too. A unit is closed only by a round that read the words as they stand. Session 3 applied edits after its last round on several units, and each such unit was owed again.
4. Run `make record && make citations` and the record tests once. Commit each fix with a message opening `343: `. A round
   cap or a tripwire goes to the round arbiter as its refusal says. Do not push.
5. Append one line per check to `specs/343-receiving-court-swept/briefs/m1-checks.md` with `make append`, opening
   `(M1c)`. Your last message is one paragraph, and it ends with what `make record-owed UNANSWERED=1` still lists.
