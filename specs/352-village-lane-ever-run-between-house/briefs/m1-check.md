<!-- page-load: kind=check -->
# Brief - feature 352, session 2: check and apply

You are a FRESH session for one part of one feature. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-research`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above
all.

**What moved.** Session 1 wrote 0036's answer (or its absence) to whether a village lane ran between a farmhouse and its
own grove, and a sentence on its drawing page; its handoff is `specs/352-village-lane-ever-run-between-house/briefs/m1-handoff.md`.

**Your question:** Q=0036

## The procedure (check, apply)

1. `make record-owed UNANSWERED=1` names every unit still owed - work from that list only. Dispatch one agent per owed
   unit, in the background, each from its own bundle and naming its own MANIFEST.md, in waves of at most 20:
   - quote-check: `make quote-verbatim Q=0036` then `make check-bundle Q=0036 FOR=quote-check`;
   - record-format: `make check-bundle Q=0036 FOR=record-format`;
   - source-reader and source-applicability on any new note or write-up the list names;
   - intro-check, and the modals' checks, where the list names them.
2. Run `make apply-edits FROM=<each output_file>`; apply by hand only what it refuses or lists as `EDIT: none`.
3. Answer each check from the bundle it read - `make record-checked CHECK=<check> BUNDLE=<its bundle> RESULT="..."`. Its
   own edits then owe the unit again: re-check ONCE what moved, from a fresh bundle, and answer that round from its bundle
   too. A unit is closed only by a round that read the words as they stand.
4. Run `make record && make citations` and the record tests once. Commit each fix with a message opening `352: `. A round
   cap or a tripwire goes to the round arbiter as its refusal says (`make arbiter-bundle BATCH=1` when several units are
   at the cap together). Do not push.
5. Append one line per check to `specs/352-village-lane-ever-run-between-house/briefs/m1-checks.md` with `make append`.
   Your last message is one paragraph, and it ends with what `make record-owed UNANSWERED=1` still lists.
