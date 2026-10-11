<!-- page-load: kind=check -->
# Brief - features 336, 337, 338 and 343, group M1, session 3: what M1's checks left owed

You are a FRESH session for one part of four features. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-research`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above
all. Commit each change with a message opening with the number of the feature whose text it changes (0104's surface and
gravel: 343; Takayama: 336; the middle gate: 338; 0099: 337).

**Where M1 stopped** (`specs/343-receiving-court-swept/briefs/m1-checks.md`, its last lines). Do these, in this order:

1. **quote-check 0104, `takayama-jinya-city` (338).** Quote the 現存遺構 heading as a passage of its own, and name the
   日本遺産構成文化財 subheading the listed middle gate stands under.
2. **quote-check 0099, `oshirasu-jawiki-3` (337).** "Edo's South Town Magistracy" is in the page's PREVIOUS paragraph, not
   in the passage quoted: add that passage (its original stored apart, as the note's form requires) or reword the claim
   to what the quoted passage says.
3. **The stone lantern (343; a ruling by the main session).** The Ubame border court is drawn with a stone lantern that
   no drawing page names. On 0104's DRAWING page, in the bullet "The ground before the entrance is drawn as an open
   court, and a garden in its place is a guess", add that the stone lantern set in the border court is part of the same
   guess: no page read places a lantern in a court before a guest's entrance (Morse's garden-book plates show lanterns
   in gardens, not in a receiving court). No new source; cite the notes the bullet already carries.
4. **The round arbiter ACCEPTED source-reader on 0104** (`round:source-reader|q:0104@5`): no further source-reader on
   0104. It left two `translation-check`s owed: `kazusa-bugyosho`'s passage #4 (whether 談話として reads as "as his
   recorded account") and the kabuki-mon gloss inside `orange-hatchobori-yoriki`'s translated quote. 0099's
   `roofed-court-size-absence` goes by 0099's own count: run source-reader on it only if `make record-owed` owes it.
5. **The fourteen pop-ups M1's triage sent on.** `modal-research` and `modal-depiction`, each from
   `make modal-bundle`, on: hearing-court, magistrate-s-dais, clerks--seats, kneeling-positions, office-hall, door,
   garden, genkan, guest-quarters, main-gate, nakamon, side-gate, residence, outer-court (all `sheet/`). One agent per
   unit, in the background, in one message. `make record-owed` names their exact bundles.

## The procedure (check, apply)

1. Items 1-3 by hand (the fragments, never a built page), then `make record-owed`: dispatch every owed check from its own
   bundle (quote-check after `make quote-verbatim`, record-format, translation-check, translation-check as item 4, the
   modal checks as item 5), in the background, in one message.
2. `make apply-edits FROM=<each output_file>`; apply by hand only what it refuses or lists as `EDIT: none`. A pop-up
   finding that would change what a pop-up says about the drawing is applied; one that asks for new research is filed as
   a line in the checks file, not researched. Then `make record && make citations` and the record tests once, and
   answer each check with `make record-checked`.
3. Re-check once only what moved. Do not push.
4. Append one line per check to `specs/343-receiving-court-swept/briefs/m1-checks.md` with `make append`. Your last
   message is one paragraph.
