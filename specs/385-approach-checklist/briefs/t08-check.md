<!-- page-load: kind=check -->
# Brief - feature 385 T08, session 2: check and apply

You are a FRESH session for one part of one feature. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-backlog`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above
all.

**What moved.** Session 1 brought 0061's drawing page in step with the maps: a hamlet's tail pond's bank is rolled bare or
planted sparsely with mulberry and cudrania, the pitch, crown and alternation labeled GUESS and the two greens CONVENTION; its
handoff is `specs/385-approach-checklist/briefs/t08-handoff.md`.

**Your question:** Q=0061

## The procedure (check, apply)

1. `make record-owed UNANSWERED=1` names every unit still owed - work from that list only. Dispatch one agent per owed
   unit, in the background, each from its own bundle and naming its own MANIFEST.md, in waves of at most 20:
   - quote-check: `make quote-verbatim Q=0061` then `make check-bundle Q=0061 FOR=quote-check`;
   - record-format: `make check-bundle Q=0061 FOR=record-format`;
   - source-reader, source-applicability and translation-check on any new note, write-up or translation the list names;
   - intro-check, and the modals' checks, where the list names them.
2. Run `make apply-edits FROM=<each output_file>`; apply by hand only what it refuses or lists as `EDIT: none`.
3. Answer each check from the bundle it read - `make record-checked CHECK=<check> BUNDLE=<its bundle> RESULT="..."`. Its
   own edits then owe the unit again: re-check ONCE what moved, from a fresh bundle, and answer that round from its bundle
   too. A unit is closed only by a round that read the words as they stand.
4. Run `make record && make citations` and the record tests once. Commit each fix with a message opening `385: `. A round
   cap or a tripwire goes to the round arbiter as its refusal says (`make arbiter-bundle BATCH=1` when several units are
   at the cap together). Do not push.
5. Append one line per check to `specs/385-approach-checklist/briefs/t08-checks.md` with `make append`.
   Your last message is one paragraph, and it ends with what `make record-owed UNANSWERED=1` still lists.
