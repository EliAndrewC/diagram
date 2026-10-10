<!-- page-load: kind=check -->
# Brief - features 336, 337, 338 and 343, group M1, session 2: check and apply

You are a FRESH session for one part of four features. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-research`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above
all.

**What moved.** Session 1 wrote these record edits, each in its own commit:
- on `research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.html` (and its notes and drawing page):
  - 343: the absence note on the court's surface;
  - 336: the Takayama route sources;
  - 338: the Koseki house's middle gate and its absence note, and the divider gate labeled a guess on the drawing page;
- on `research/questions/0099-the-hearing-court-shirasu.html`, 337: the roofed court's size (an absence note, or a size
  if the archive held one).

Its handoff is `specs/343-receiving-court-swept/briefs/m1-handoff.md`.

**Your questions:** Q=0104, Q=0099
**Your registry keys:** the ones the handoff names.

## The procedure (check, apply)

1. `make record-owed` names every unit the delta owes. In the background, in one message, dispatch one agent per owed unit,
   each from its own bundle and each naming its own MANIFEST.md:
   - quote-check: `make check-bundle Q=<n> FOR=quote-check`;
   - record-format: `... FOR=record-format`;
   - source-applicability: `make check-bundle KEY=<key> FOR=source-applicability` for each key;
   - entry-drift: `make check-bundle Q=<n> FOR=entry-drift KIND=<class>` for each modal it is owed for.
2. Run `make apply-edits FROM=<each output_file>`. In one message, apply by hand only what it refuses or lists as
   `EDIT: none`. Then run `make record && make citations` and the record tests once, and answer each check with
   `make record-checked`. Commit each fix with a message opening with the number of the feature whose text it fixes.
3. Re-check once only what moved. Do not push.
4. Append one line per check to `specs/343-receiving-court-swept/briefs/m1-checks.md` with `make append`. Your last
   message is one paragraph.
