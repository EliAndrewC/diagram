<!-- page-load: kind=check -->
# Brief - feature 368, session 3: the checks still owed, check and apply

You are a FRESH session for one part of one feature. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-research`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above
all.

**What is still owed.** Session 2 (M2) named it at its end (`specs/368-record-0047-loose-ends/briefs/m2-checks.md`, its
STILL OWED line): quote-check, record-format and source-reader on 0047's absence note `how-our-maps-place-privies-benjo-4`
and the 48 ft bullet in their final "no measured distance" wording - a new unit by the round arbiter's ruling, so a first
reading, not a round 4; modal-depiction on buckwheat, soy and privy; and a modal triage of the four manure pop-ups
(manure_form--heap, manure_form--pit, manure-heap, manure-pit), whose drawing page 0047 moved again. The round arbiter's
rulings are in `specs/368-record-0047-loose-ends/arbiter.jsonl`; read them before dispatching.

**Your questions:** Q=0047 (and Q=0006 only if `make record-owed UNANSWERED=1` names it)
**Your registry keys:** none expected.

## The procedure (check, apply)

1. `make record-owed UNANSWERED=1` names every unit still owed - work from that list only. Dispatch one agent per owed
   unit, in the background, each from its own bundle and naming its own MANIFEST.md:
   - quote-check: `make quote-verbatim Q=0047` then `make check-bundle Q=0047 FOR=quote-check`;
   - record-format: `make check-bundle Q=0047 FOR=record-format`;
   - source-reader: `make check-bundle Q=0047 FOR=source-reader` on `how-our-maps-place-privies-benjo-4`;
   - the manure pop-ups: `make modal-triage`, then `make modal-triaged`; each pop-up it names, and buckwheat, soy and privy:
     `make modal-bundle KIND="hamlet/<name>" FOR=modal-depiction` (`choice/<name>` for the manure_form ones).
2. Run `make apply-edits FROM=<each output_file>`; apply by hand only what it refuses or lists as `EDIT: none`.
3. Answer each check from the bundle it read - `make record-checked CHECK=<check> BUNDLE=<its bundle> RESULT="..."`. Its own edits then owe the unit again: re-check ONCE what moved, from a fresh bundle, and answer that round from its bundle too. A unit is closed only by a round that read the words as they stand. Session 2's last edits had no round after them, which is why these units are owed.
4. Run `make record && make citations` and the record tests once. Commit each fix with a message opening `368: `. A round
   cap or a tripwire goes to the round arbiter as its refusal says. Do not push.
5. Append one line per check to `specs/368-record-0047-loose-ends/briefs/m2-checks.md` with `make append`, opening
   `(M2b)`. Your last message is one paragraph, and it ends with what `make record-owed UNANSWERED=1` still lists.
