<!-- page-load: kind=check -->
# Brief - feature 431, session C1: check and apply

You are a FRESH session for one part of one feature. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-money-research`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What moved.** Session S1 wrote two new money questions - the farm household's unpaid work, and how long it took to make cloth - with pointers from 0209 and 0306, with new registry entries, in commits opening `431: `. Its handoff is `specs/431-household-work-never-paid/briefs/handoff.md` (its `## Session S1` section), which names the questions and keys.

**Not yours:** any unit outside S1's two new questions, the pointer bullets in 0209 and 0306 and the registry keys that handoff section names (another part of this feature, or
another feature, may be owed in this clone; leave it alone).

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
4. Append one line per check to `specs/431-household-work-never-paid/briefs/c1-checks.md` with `make append`, then a last
   line `STILL OWED:` naming anything left. Your last message is one paragraph.
