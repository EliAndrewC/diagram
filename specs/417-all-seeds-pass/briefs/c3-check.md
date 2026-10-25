<!-- page-load: kind=check -->
# Brief - feature 417, session C3: check and apply

You are a FRESH session for one part of one feature. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-backlog-pages`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What moved.** Session S3 recorded sources on record pages, in commits opening `417: `. Its handoff is
`specs/417-all-seeds-pass/briefs/handoff.md` (its `## Session S3` section), which names the questions and keys.

**Not yours:** any unit outside the questions and registry keys that handoff section names.

## The procedure (check, apply)

1. `make record-owed` names every unit the delta owes. In the background, in one message, dispatch one agent per owed unit of
   yours, each from its own bundle and naming its own MANIFEST.md (at most three of one check at once):
   - quote-check: `make check-bundle Q=<n> FOR=quote-check`, after `make quote-verbatim Q=<n>`;
   - source-reader: on each new note, `make check-bundle KEY=<k> WHOLE=1`;
   - source-applicability: on each new registry write-up, `make check-bundle KEY=<k>`;
   - record-format and intro-check where owed; translation-check on each pair `make translation-owed` names.
2. Run `make apply-edits FROM=<each output_file>`. Apply by hand only what it refuses or lists as `EDIT: none`. Then run `make
   record && make citations` and the record tests once, and answer each check with `make record-checked`. Commit each fix with
   a message opening `417: `.
3. Re-check once only what moved. A check's third round on one subject goes to the round arbiter first (`make arbiter-bundle
   TRIGGER="round:<check>|q:<n>@3"`). Do not push.
4. Append one line per check to `specs/417-all-seeds-pass/briefs/c3-checks.md` with `make append`, then a last line `STILL OWED:`
   naming anything left. Your last message is one paragraph.
