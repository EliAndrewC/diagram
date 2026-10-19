<!-- page-load: kind=check -->
# Brief - feature 395, session 2: check and apply

You are a FRESH session for one part of one feature. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/money`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What moved.** Session 1 wrote four new money questions on what a small forest shrine cost (the sanctuary, the roof,
torii and stonework, rites and furnishings), and their registry entries, in commits opening `395: `. Its handoff is
`specs/395-shrine-building-costs/briefs/s1-handoff.md`, which names the questions and keys.

## The procedure (check, apply)

1. `make record-owed` names every unit the delta owes. In the background, in one message, dispatch one agent per owed
   unit, each from its own bundle and naming its own MANIFEST.md. Four or more of one check go as ONE `check-wave`
   workflow.
   - quote-check: `make check-bundle Q=<n> FOR=quote-check`, after `make quote-verbatim Q=<n>`;
   - source-reader: on each new note, `make check-bundle Q=<n> FOR=source-reader`;
   - source-applicability: on each new registry write-up, `make check-bundle KEY=<k> FOR=source-applicability`;
   - record-format and intro-check where owed;
   - translation-check: on each pair `make translation-owed` names.
2. Run `make apply-edits FROM=<each output_file>`. In one message, apply by hand only what it refuses or lists as `EDIT:
   none`. Then run `make record && make citations` and the record tests once, and answer each check with `make
   record-checked`. Commit each fix with a message opening `395: `.
3. Re-check once only what moved. A check's third round on one subject goes to the round arbiter first (`make
   arbiter-bundle`). Do not push.
4. Append one line per check to `specs/395-shrine-building-costs/briefs/s1-checks.md` with `make append`, then a last
   line `STILL OWED:` naming anything left. Your last message is one paragraph.
