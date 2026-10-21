<!-- page-load: kind=check -->
# Brief - feature 408, session 3: check and apply

You are a FRESH session for one part of one feature. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/money`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What moved.** Sessions 1-2 revised five money questions (0257, 0258, 0260, 0268, 0271), and their new registry
entries, in commits opening `408: `. Its handoff is `specs/408-shrine-small-lines/briefs/handoff.md`, which names the
questions and keys.

## The procedure (check, apply)

1. `make record-owed` names every unit the delta owes. In the background, in one message, dispatch one agent per owed
   unit, each from its own bundle and naming its own MANIFEST.md. Four or more of one check go as ONE `check-wave`
   workflow.
   - quote-check: `make check-bundle Q=<n> FOR=quote-check`, after `make quote-verbatim Q=<n>` (page images with `IMAGES=`
     for the scans and scrambled PDFs; row dumps for the .xls cells);
   - source-reader: on each new note, `make check-bundle KEY=<k> WHOLE=1`;
   - source-applicability: on each new registry write-up, `make check-bundle KEY=<k>`;
   - record-format and intro-check where owed;
   - translation-check: on each pair `make translation-owed` names.
2. Run `make apply-edits FROM=<each output_file>`. In one message, apply by hand only what it refuses or lists as `EDIT:
   none`. Then run `make record && make citations` and the record tests once, and answer each check with `make
   record-checked`. Commit each fix with a message opening `408: `.
3. Re-check once only what moved. A check's third round on one subject goes to the round arbiter first (`make
   arbiter-bundle`). Do not push.
4. Append one line per check to `specs/408-shrine-small-lines/briefs/s3-checks.md` with `make append`, then a last
   line `STILL OWED:` naming anything left. Your last message is one paragraph.
