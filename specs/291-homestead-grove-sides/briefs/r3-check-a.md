<!-- page-load: kind=check -->
# Brief - feature 291 (how many sides a homestead grove takes), group R3, session 2a: check and apply

You are a FRESH session for one part of feature 291. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all.

**What moved.** Session 1 rewrote one sentence of `homesteads/010` - the drawn depth of the windward stand (1.57 house
depths, about 44 ft at a 28 ft-deep farmhouse, a GUESS) - so it agrees with what the maps draw. Its handoff is
`specs/291-homestead-grove-sides/briefs/r3-handoff.md`.

**Your questions:** PAGE=homesteads SECTION=010
**Your registry keys:** none

## The procedure (check, apply)

1. In the background, in one message: `make check-bundle PAGE=homesteads SECTION=010 FOR=quote-check` for `quote-check`
   and `... FOR=record-format` for `record-format` (in `.claude/skills/diagram`), each naming its own MANIFEST.md.
2. `make apply-edits FROM=<each output_file>`; by hand only what it refuses or lists as `EDIT: none`, in one message.
   Then `make record && make citations` and the four record tests once.
3. Re-check once only what moved. Commit only your files (message beginning `291 R3 check:`); do not push.
4. Append one line to `specs/291-homestead-grove-sides/briefs/r3-checks.md` (with `make append`). Your last message is
   one paragraph.
