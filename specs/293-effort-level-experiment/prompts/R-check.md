<!-- page-load: kind=check -->
# Brief - feature 293, task R: the servants' quarters, session 2: check and apply

You are a FRESH session. This brief is the whole of what you need; do not read the feature's spec or plan to orient. Work in
the clone you were started in (`git rev-parse --show-toplevel`); the project's CLAUDE.md files apply to you, the research
record's `CLAUDE.md` above all. No one will answer a question during this session: where you would ask the GM, record the
question and the default you took in the report, and carry on.

**Ad-hoc agents.** Dispatch any ad-hoc work that checks or judges (a verdict, a review, a comparison) that no defined agent
covers to the `adhoc-judge` agent. Dispatch ad-hoc reading, fetching, translating or extracting as you normally would.

Session 1 researched the Ubame servants' quarters question (one dormitory behind sliding partitions, or a door a household?)
and committed; its handoff is `specs/293-effort-level-experiment/prompts/R-handoff.md`. You check and apply ALL of it: every
`SECTION=` and `KEY=` line the handoff names. **Read narrowly**: `make lines FILE=<handoff> KEY="SECTION=|KEY="` for your
list; `make notes PAGE=buildings SECTION=<NNN> KEYS=<key,key>` for a few notes.

## The procedure (check, apply)

1. **Check, all in one message, in the background.** For each question: `make check-bundle PAGE=buildings SECTION=<NNN>
   FOR=quote-check` for `quote-check`, and `... FOR=record-format` for `record-format`, each agent naming its own MANIFEST.md
   and nothing else. For each key: `make check-bundle KEY=<key>` and `source-applicability`. An ABSENCE note that says what was
   searched is checked as one: its search is stated, dated and specific.
2. **Apply each report with ONE command**: `make apply-edits FROM=<the output_file its dispatch printed>` (in
   `.claude/skills/diagram`), `SKIP=<n,n>` for a block you disagree with. Then do BY HAND only what it lists as REFUSED, what
   you skipped, and the `EDIT: none` findings - all in ONE message of parallel `Edit` calls. A source `source-applicability`
   rules NOT-APPLICABLE: the assertions resting on it are relabeled (absence or guess), and the outcome changes if they carried it.
   Then `make glossary` if a term was added, `make record && make citations` and the four record tests ONCE.
3. **Re-check ONCE, only what moved** (`make check-bundle ... NOTES=<key,key> FOR=quote-check`, one `quote-check`). A PARTIAL
   left after it is labeled honestly in the note and left.
4. **If the modal of a map feature names a changed section as its `Entry:`**, run `scripts/_entry_owed.py` and `entry-drift` on
   what it names, and fix what drifted.
5. **Commit** with a message beginning `293 R check:`; do not push. Then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md
   LINE="Effort experiment | 293 | task R checked, committed in clone | <date>"`.
6. **Report.** Write `specs/293-effort-level-experiment/prompts/R-checks.md`: one line per question and key with its verdicts
   (quote-check, record-format, source-applicability), any outcome the checks changed, and anything left open. Commit it. Your
   last message is one paragraph.
