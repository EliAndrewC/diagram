<!-- page-load: kind=check -->
# Brief - feature 291 (how many sides a homestead grove takes), group R2, session 2a: check and apply

You are a FRESH session for one part of feature 291. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files
apply to you, the research record's `CLAUDE.md` above all.

**What the feature is for.** The GM reversed their 2026-08-29 hook ruling for the farmstead's own grove on 2026-09-29
(its sides are now rolled: two, three or four); the village's shelter belt stays on one or two windward sides. Session 1
recorded that in the village belt's entries. Its handoff is `specs/291-homestead-grove-sides/briefs/r2-handoff.md` -
read only your own lines (`make lines FILE=<handoff> KEY="SECTION=vegetation"`).

**Your questions:** Q=0072, PAGE=vegetation SECTION=620
**Your registry keys:** none

## The procedure (check, apply)

1. **Check, all in one message, in the background.** For each question: `make check-bundle Q=<NNNN> FOR=quote-check` for `quote-check`, and `... FOR=record-format` for `record-format` (in
   `.claude/skills/diagram`), each agent naming its own MANIFEST.md and nothing else.
2. **Apply each report with ONE command**: `make apply-edits FROM=<the output_file its dispatch printed>`, `SKIP=<n,n>`
   for a block you disagree with. Then do BY HAND only what it lists as REFUSED, what you skipped, and the `EDIT: none`
   findings - all in ONE message of parallel `Edit` calls. Then `make record && make citations` and the four record tests
   (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`) ONCE.
3. **Re-check ONCE, only what moved.** A PARTIAL left after it is labeled honestly and left.
4. **Commit** only the files you changed (`git -C` with paths), message beginning `291 R2 check:`; do not push.
5. **Report.** Append to `specs/291-homestead-grove-sides/briefs/r2-checks.md` (with `make append`) one line per
   question: its verdicts and anything left open. Your last message is one paragraph.
