<!-- page-load: kind=check -->
# Brief - feature 431, session C3: check and apply

You are a FRESH session for one part of one feature. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-money-research`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What moved.** Session S3 added cross-pointers among 0311, 0004, 0183 and 431's new questions 0312, 0313, 0315, 0316 and 0317, and cut one clause from a quotation in 0313's notes, in commits opening `431: `. Its handoff is `specs/431-household-work-never-paid/briefs/handoff.md` (its `## Session S3` section).

**Not yours:** any unit outside the sections S3's handoff names (another feature may be owed in this clone; leave it alone).

## The procedure (check, apply)

1. `make record-owed` names every unit the delta owes. In the background, in one message, dispatch one agent per owed
   unit of yours, each from its own bundle and naming its own MANIFEST.md. Four or more of one check go as ONE `check-wave`
   workflow.
   - quote-check: `make check-bundle Q=<n> FOR=quote-check`, after `make quote-verbatim Q=<n>` (page images with `IMAGES=`
     for scans);
   - source-reader: on each new note, `make check-bundle KEY=<k> WHOLE=1`;
   - source-applicability: on each new registry write-up, `make check-bundle KEY=<k>`;
   - record-format and intro-check where owed; translation-check on each pair `make translation-owed` names.
2. Run `make apply-edits FROM=<each output_file>`. In one message, apply by hand only what it refuses or lists as `EDIT:
   none`. Then run `make record && make citations` and the record tests once, and answer each check with `make
   record-checked`. Commit each fix with a message opening `431: `.
3. Re-check once only what moved. A check's third round on one subject goes to the round arbiter first, on that round's own
   trigger (`make arbiter-bundle TRIGGER="round:<check>|q:<n>@3"`). Do not push.
4. Append one line per check to `specs/431-household-work-never-paid/briefs/c3-checks.md` with `make append`, then a last
   line `STILL OWED:` naming anything left. Your last message is one paragraph.
