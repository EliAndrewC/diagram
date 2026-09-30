<!-- page-load: kind=check -->
# Brief - feature 291 (how many sides a homestead grove takes), group R13, session 2: check and apply

You are a FRESH session for one part of feature 291. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all.

**What moved.** Session 1 corrected three sentences the settlement-reviews found saying more than the record supports (homesteads/155's summary on the fan's foot, the fields-section water paragraph on a dispersed farm's own water, and the spelling resson). Its handoff is
`specs/291-homestead-grove-sides/briefs/r13-handoff.md`.

**Your questions:** the questions the handoff names (homesteads 155, the homesteads fields-section question it edited, towns 390)
**Your registry keys:** any the handoff names as new

## The procedure (check, apply)

1. In the background, in one message, for each question: `make check-bundle PAGE=<page> SECTION=<q> FOR=quote-check` for
   `quote-check` and `... FOR=record-format` for `record-format` (in `.claude/skills/diagram`), each naming its own
   MANIFEST.md; and `source-applicability` (`make check-bundle KEY=<k>`) on any registry key the handoff names as new.
2. `make apply-edits FROM=<each output_file>`; by hand only what it refuses or lists as `EDIT: none`, in one message.
   Then `make record && make citations` and the four record tests once.
3. Re-check once only what moved. Commit only your files (message beginning `291 R13 check:`); do not push.
4. Append one line to `specs/291-homestead-grove-sides/briefs/r13-checks.md` (with `make append`). Your last message is
   one paragraph.
