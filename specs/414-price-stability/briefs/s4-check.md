<!-- page-load: kind=check -->
# Brief - feature 414, session 4: check and apply

You are a FRESH session for one part of one feature. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-money-pages`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What moved.** Sessions 1-3 wrote five new money questions (A-E), and
their new registry entries, in commits opening `414: `. Its handoff is `specs/414-price-stability/briefs/handoff.md`,
which names the questions and keys.

**Not yours:** feature 412's units (0250, 0265, 0273, 0279, 0286-0289 and their registry keys) are owed in this clone too,
because 412 is not yet on main; another session checks them. Check only the units of the questions and keys feature 414's
handoff names, and leave every 412 unit alone.

## The procedure (check, apply)

1. `make record-owed` names every unit the delta owes. In the background, in one message, dispatch one agent per owed
   unit, each from its own bundle and naming its own MANIFEST.md. Four or more of one check go as ONE `check-wave`
   workflow.
   - quote-check: `make check-bundle Q=<n> FOR=quote-check`, after `make quote-verbatim Q=<n>` (row dumps for spreadsheet
     cells; page images with `IMAGES=` for scans);
   - source-reader: on each new note, `make check-bundle KEY=<k> WHOLE=1`;
   - source-applicability: on each new registry write-up, `make check-bundle KEY=<k>`;
   - record-format and intro-check where owed;
   - translation-check: on each pair `make translation-owed` names.
2. Run `make apply-edits FROM=<each output_file>`. In one message, apply by hand only what it refuses or lists as `EDIT:
   none`. Then run `make record && make citations` and the record tests once, and answer each check with `make
   record-checked`. Commit each fix with a message opening `414: `.
3. Re-check once only what moved. A check's third round on one subject goes to the round arbiter first, on that round's own
   trigger (`make arbiter-bundle TRIGGER="round:<check>|q:<n>@3"`). Do not push.
4. Append one line per check to `specs/414-price-stability/briefs/s4-checks.md` with `make append`, then a last
   line `STILL OWED:` naming anything left. Your last message is one paragraph.
