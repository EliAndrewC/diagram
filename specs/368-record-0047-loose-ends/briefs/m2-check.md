<!-- page-load: kind=check -->
# Brief - feature 368, session 2: check and apply

You are a FRESH session for one part of one feature. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-research`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above
all.

**What moved.** Session 1 wrote these record edits, in commits opening `368: `:
- on `research/questions/0047-farm-privies-and-their-night-soil-benjo.*`: today's privy figures and their method on the
  drawing page, the August table kept whole and dated; `wang-ochiai-2022-5`'s spelling made one; `wang-ochiai-2022-2`'s
  "Type V1" glossed or cut;
- on `research/questions/0006-dry-fields-and-their-crops-hatake.*`: a clause pointing to 0033's holdings, and what the
  dry plot's stroke stands for on the drawing page.

Its handoff is `specs/368-record-0047-loose-ends/briefs/m2-handoff.md`.

**Your questions:** Q=0047, Q=0006
**Your registry keys:** none expected; the ones the handoff names.

## The procedure (check, apply)

1. `make record-owed` names every unit the delta owes. In the background, in one message, dispatch one agent per owed unit,
   each from its own bundle and each naming its own MANIFEST.md:
   - quote-check: `make check-bundle Q=<n> FOR=quote-check` (after `make quote-verbatim Q=<n>`);
   - record-format: `... FOR=record-format`;
   - entry-drift: `make check-bundle Q=<n> FOR=entry-drift KIND=<class>` for each modal it is owed for;
   - modal-depiction: `make modal-bundle FOR=modal-depiction ...` for each modal it is owed for.
2. Run `make apply-edits FROM=<each output_file>`. In one message, apply by hand only what it refuses or lists as
   `EDIT: none`. Then run `make record && make citations` and the record tests once, and answer each check with
   `make record-checked`. Commit each fix with a message opening `368: `.
3. Re-check once only what moved. Do not push.
4. Append one line per check to `specs/368-record-0047-loose-ends/briefs/m2-checks.md` with `make append`. Your last
   message is one paragraph.
