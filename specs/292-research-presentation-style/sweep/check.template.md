<!-- page-load: kind=check -->
# Brief - feature 292 (how a research section is presented), the sweep: {page} group {group}, session 2: check and apply

You are a FRESH session for one part of feature 292. This brief is the whole of what you need; do not read the
feature's spec, plan or tasks. Work in this clone (`{clone}`); the research record's
`CLAUDE.md` applies to you.

**What the feature is for.** The research record is being reorganized into one section per TOPIC and rewritten under
the style guide `research/STYLE.md`, with how our maps draw each thing in a separate RENDERING section; the GM accepted
the process and its checks on 2026-09-30. Session 1 wrote the topics of this group and folded the old sections into
them. Its handoff is `specs/292-research-presentation-style/sweep/{page}-{group}-handoff.md` - read it with
`make lines FILE=<handoff> KEY="SECTION=|RENDERING=|OLD=|MODALS=|BASE="` (in `.claude/skills/diagram`).

**Your topics:** {topic_titles}

> **READ THIS FIRST - you are a headless session.** Every check agent you dispatch runs in the FOREGROUND: `Agent`
> calls WITHOUT `run_in_background`, two in one message, and your turn waits for them. A background agent's result
> never reaches a headless session: if you dispatch in the background, or end a turn saying you are "waiting", the
> session hangs for good and is killed. There is nothing to wait for between turns - keep working until the report
> is appended.

## The procedure (check, apply)

1. **Claim:** `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram reorg ({clonename}) | 292 | sweep {page} {group} check in progress | {date}"`.
2. **Bundles**, in `.claude/skills/diagram`, one per check (each prints the MANIFEST to hand its agent):
   - the old sections, for the merge audit: for each path in `OLD=`, `git -C {clone} show
     <BASE>:.claude/skills/diagram/<path> > /tmp/l7r-old-{page}-{group}/<file name>` (the fragment only);
   - `record-style` on each research section, WITH the merge audit: `make check-bundle PAGE={page} SECTION=<id>
     FOR=record-style EXTRA="<the saved old fragments>" OUT=/tmp/l7r-check/{page}-{group}-<n>-rs`; and on each
     rendering section: `make check-bundle PAGE=rendering/{page} SECTION=<rid> FOR=record-style OUT=...`;
   - `quote-check` on each research and rendering section: `make check-bundle ... FOR=quote-check` - it may print
     several bundles (the notes in batches); each is its own agent;
   - `record-format` on each research and rendering section: `... FOR=record-format`;
   - `entry-drift` for each class in `MODALS=`: `make check-bundle PAGE={page} SECTION=<id> KIND=<class>
     FOR=entry-drift EXTRA="research/questions/{page}/<the rendering fragment>"`, and say in the dispatch that the
     modal is judged against both sections together;
   - `translation-check`, only if `make translation-owed PAGE={page} SECTION=<id>` lists pairs (and the same for the
     rendering section): `make check-bundle PAGE={page} SECTION=<id> FOR=translation-check`.
3. **Dispatch the checks in the FOREGROUND, TWO per message** - two `Agent` calls in one message, neither with
   `run_in_background`, so they run side by side and your turn waits for both. NEVER end a turn, and never dispatch
   in the background, to wait for a check: this is a headless session, and a background agent's result never reaches
   one that has ended its turn - the first sweep check sessions stalled that way for over an hour. Two at a time
   because the containers share a 9 GB memory cap and another queue runs beside yours. Each agent is named for its
   check (`record-style`, `quote-check`, `record-format`, `entry-drift`, `translation-check`) and handed its MANIFEST
   and nothing under `/diagram`; ask each for counts first, then only what to act on, as EDIT blocks. As each pair
   returns, save each report's text with `Write` to `/tmp/l7r-check/{page}-{group}-<n>-<check>.reply.md`.
4. **Apply**: each `quote-check` and `record-format` report with `make apply-edits FROM=<its saved .reply.md>` (`SKIP=<n,n>` for a block you disagree with); then BY HAND, in ONE message of parallel `Edit` calls per
   section, everything else: every `record-style` FAIL (its rule 5a lines are the lead lines to use), every item its
   merge audit calls LOST (restore it where it belongs, or keep it in an HTML comment if a style rule cut it), each
   `EDIT: none` finding, each `entry-drift` DRIFTED (rewrite the modal sentence from the sections; the class docstring
   is the modal), each `translation-check` LOOSE or WRONG. A NOTE is applied when it is right. A finding you judge
   wrong is left, with one line in your report saying why.
5. **Rebuild and test once**: `make glossary` if a term changed, `make record && make citations`, `make style-prepass`
   on each section (its FAIL lists empty), `make test-file FILE=tests/interactive`, `python3 scripts/check-question-size.py`
   from the clone root.
6. **Re-check once, only what moved much**: a `quote-check` on notes you changed (`make check-bundle ... NOTES=<key,key>
   FOR=quote-check`). A PARTIAL left after it is labeled honestly and left.
6a. **A large PDF is read, not skipped.** When a check reports a page unfetchable because the web fetch refuses
   files over 10 MB, download it (`curl -sL -o <file> <url>`), extract it (`pdftotext <file> -`) and grep the quoted
   passages yourself. A page is unreadable only when neither works; it never goes on the GM's download list for its
   size alone.
7. **Commit** only the files you changed (`git -C` with paths), message beginning `292 sweep {page} {group} check:`; do
   not push. **Report**: `make append FILE={clone}/specs/292-research-presentation-style/sweep/{page}-checks.md
   LINE="- {group} <section id>: record-style F<n> N<n> LOST<n>; quote-check S<n> P<n> D<n>; record-format V<n> S<n> H<n>; entry-drift <class> <verdict> ...; translation <verdicts or none>; open: <anything left>"`
   - one line per section - and close the claim with `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md
   LINE="Diagram reorg ({clonename}) | 292 | sweep {page} {group} checked, committed in clone | {date}"`. Your last
   message is one paragraph.
