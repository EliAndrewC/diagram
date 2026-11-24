<!-- page-load: kind=check -->
# Brief - feature 453, session C1: check and apply

You are a FRESH session for one feature's record checks. This brief is the whole of what you need. Work in this clone (`/diagram/.clones/diagram-research`); the research record's `CLAUDE.md` applies to you above all.

**What moved.** Session S1 wrote the empty-bale question in commits opening `453: `. Its handoff is `specs/453-empty-charcoal-bales/briefs/handoff.md` (its `## Session S1` section, read with `make lines`), which names the questions and keys.

**Not yours:** any unit outside that handoff section (another feature may be owed in this clone; leave it alone).

## The procedure (check, apply)

1. `make record-owed` names every unit the delta owes. In ONE message, in the FOREGROUND, dispatch one agent per owed unit of yours, each from its own bundle and naming its own MANIFEST.md. Four or more of one check go as ONE `check-wave` workflow.
   - quote-check: `make check-bundle Q=<n> FOR=quote-check`, after `make quote-verbatim Q=<n>` (page images with `IMAGES=` for scans);
   - source-reader: on each new note, `make check-bundle KEY=<k> WHOLE=1`;
   - source-applicability: on each new registry write-up, `make check-bundle KEY=<k>`;
   - record-format and intro-check where owed; translation-check on each pair `make translation-owed` names.
2. Run `make apply-edits FROM=<each output_file>`. In one message, apply by hand only what it refuses or lists as `EDIT: none`. Then `make record CHECK=1`, `make record`, `make glossary` and `make question-sizes` once, and answer each check with `make record-checked`. Commit each fix with a message opening `453: `.
3. Re-check once only what moved. A check's third round on one subject goes to the round arbiter first, on that round's own trigger (`make arbiter-bundle TRIGGER="round:<check>|q:<n>@3"`). Do not push.
4. Append one line per check to `specs/453-empty-charcoal-bales/briefs/c1-checks.md` with `make append`, then a last line `STILL OWED:` naming anything left. Your last message is one paragraph.
