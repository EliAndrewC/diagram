<!-- page-load: kind=check -->
# Brief - feature 291 (how many sides a homestead grove takes), group R6, session 2a: check and apply

You are a FRESH session for one part of feature 291. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all.

**What moved.** Session 1 wrote a new homesteads question, "How was a row village laid out?" (what line a row
followed, one side or both, frontage and spacing, where the fields lay, how long, the homestead grove in a row), and a
pointer to it in the LINEAR section of "Does a hamlet have to be nucleated at all?". Its handoff, with the section ids and new keys, is
`specs/291-homestead-grove-sides/briefs/r6-handoff.md` - read it first for the ids.

**Your questions:** the sections the handoff names (IN=homesteads)
**Your registry keys:** the new keys the handoff names

## The procedure (check, apply)

1. In the background, in one message, for each question: `make check-bundle Q=<NNNN> FOR=quote-check`
   for `quote-check` and `... FOR=record-format` for `record-format`; and for each new key `make check-bundle KEY=<k>
   FOR=source-applicability` for `source-applicability` (in `.claude/skills/diagram`), each naming its own MANIFEST.md.
2. `make apply-edits FROM=<each output_file>`; by hand only what it refuses or lists as `EDIT: none`, in one message.
   Then `make record && make citations` and the four record tests once.
3. Re-check once only what moved. Commit only your files (message beginning `291 R6 check:`); do not push.
4. Append one line per question and key to `specs/291-homestead-grove-sides/briefs/r6-checks.md` (with `make append`).
   Your last message is one paragraph.
