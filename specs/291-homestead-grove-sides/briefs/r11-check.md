<!-- page-load: kind=check -->
# Brief - feature 291 (how many sides a homestead grove takes), group R11, session 2: check and apply

You are a FRESH session for one part of feature 291. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all.

**What moved.** Session 1 brought vegetation/154's map-facing lines in line with the engine (the side weights, Inashiro's as-built count, the bamboo patch in a farm's grove). Its handoff is
`specs/291-homestead-grove-sides/briefs/r11-handoff.md`.

**Your questions:** PAGE=vegetation SECTION=154
**Your registry keys:** none

## The procedure (check, apply)

1. In the background, in one message, for each question: `make check-bundle PAGE=vegetation SECTION=154 FOR=quote-check` for
   `quote-check` and `... FOR=record-format` for `record-format` (in `.claude/skills/diagram`), each naming its own
   MANIFEST.md; and `source-applicability` (`make check-bundle KEY=<k>`) on any registry key the handoff names as new.
2. `make apply-edits FROM=<each output_file>`; by hand only what it refuses or lists as `EDIT: none`, in one message.
   Then `make record && make citations` and the four record tests once.
3. Re-check once only what moved. Commit only your files (message beginning `291 R11 check:`); do not push.
4. Append one line to `specs/291-homestead-grove-sides/briefs/r11-checks.md` (with `make append`). Your last message is
   one paragraph.
