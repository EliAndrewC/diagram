<!-- page-load: kind=check -->
# Brief - feature 291 (how many sides a homestead grove takes), group R7, session 2a: check and apply

You are a FRESH session for one part of feature 291. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all.

**What moved.** Session 1 wrote into the map sections of the homesteads questions on the row village what the maps
draw (the line and sides knobs, the spacing, the street, further streets, the far row's holding, the row's water), and
where the map draws a dispersed farm's own well - each value in its class. Its handoff is
`specs/291-homestead-grove-sides/briefs/r7-handoff.md`.

**Your questions:** Q=0033; PAGE=homesteads SECTION=156; PAGE=homesteads SECTION=200
**Your registry keys:** none

## The procedure (check, apply)

1. In the background, in one message, for each question: `make check-bundle Q=<NNNN> FOR=quote-check`
   for `quote-check` and `... FOR=record-format` for `record-format` (in `.claude/skills/diagram`), each naming its own
   MANIFEST.md.
2. `make apply-edits FROM=<each output_file>`; by hand only what it refuses or lists as `EDIT: none`, in one message.
   Then `make record && make citations` and the four record tests once.
3. Re-check once only what moved. Commit only your files (message beginning `291 R7 check:`); do not push.
4. Append one line per question to `specs/291-homestead-grove-sides/briefs/r7-checks.md` (with `make append`). Your
   last message is one paragraph.
