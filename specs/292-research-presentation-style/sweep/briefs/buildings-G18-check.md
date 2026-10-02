<!-- page-load: kind=check -->
# Brief - feature 292 (how a research section is presented), the sweep: buildings group G18, session 2: check and apply

You are a FRESH session for one part of feature 292. This brief is the whole of what you need; do not read the
feature's spec, plan or tasks. Work in this clone (`/diagram/.clones/diagram-reorg`); the research record's
`CLAUDE.md` applies to you.

**What the feature is for.** The research record is being reorganized into one section per TOPIC and rewritten under
the style guide `research/STYLE.md`, with how our maps draw each thing in a separate RENDERING section; the GM accepted
the process and its checks on 2026-09-30. Session 1 wrote the topics of this group and folded the old sections into
them. Its handoff is `specs/292-research-presentation-style/sweep/buildings-G18-handoff.md` - read it with
`make lines FILE=<handoff> KEY="SECTION=|RENDERING=|OLD=|MODALS=|BASE="` (in `.claude/skills/diagram`).

**Your topics:** "Hunting dogs and kennels (inugoya)"; "Martial training grounds and dojo"

## The procedure (check, apply)

1. **Claim:** `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram reorg (diagram-reorg) | 292 | sweep buildings G18 check in progress | 2026-09-30"`.
2. **Bundles**, in `.claude/skills/diagram`, one per check (each prints the MANIFEST to hand its agent):
   - the old sections, for the merge audit: for each path in `OLD=`, `git -C /diagram/.clones/diagram-reorg show
     <BASE>:.claude/skills/diagram/<path> > /tmp/l7r-old-buildings-G18/<file name>` (the fragment only);
   - `record-style` on each research section, WITH the merge audit: `make check-bundle Q=<NNNN>
     FOR=record-style EXTRA="<the saved old fragments>" OUT=/tmp/l7r-check/buildings-G18-<n>-rs`; and on each
     rendering section: `make check-bundle Q=<NNNN> FOR=record-style OUT=...`;
   - `quote-check` on each research and rendering section: `make check-bundle ... FOR=quote-check` - it may print
     several bundles (the notes in batches); each is its own agent;
   - `record-format` on each research and rendering section: `... FOR=record-format`;
   - `entry-drift` for each class in `MODALS=`: `make check-bundle Q=<NNNN> KIND=<class>
     FOR=entry-drift EXTRA="research/questions/<the drawing page>"`, and say in the dispatch that the
     modal is judged against both sections together;
   - `translation-check`, only if `make translation-owed Q=<NNNN>` lists pairs (and the same for the
     rendering section): `make check-bundle Q=<NNNN> FOR=translation-check`.
3. **Dispatch the checks in the background, at most THREE at a time** (the containers share a 9 GB memory cap):
   each agent is named for its check (`record-style`, `quote-check`, `record-format`, `entry-drift`,
   `translation-check`) and handed its MANIFEST and nothing under `/diagram`. Ask each for counts first, then only
   what to act on, as EDIT blocks. Start the next as one finishes.
4. **Apply**: each `quote-check` and `record-format` report with `make apply-edits FROM=<the output_file its dispatch
   printed>` (`SKIP=<n,n>` for a block you disagree with); then BY HAND, in ONE message of parallel `Edit` calls per
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
7. **Commit** only the files you changed (`git -C` with paths), message beginning `292 sweep buildings G18 check:`; do
   not push. **Report**: `make append FILE=/diagram/.clones/diagram-reorg/specs/292-research-presentation-style/sweep/buildings-checks.md
   LINE="- G18 <section id>: record-style F<n> N<n> LOST<n>; quote-check S<n> P<n> D<n>; record-format V<n> S<n> H<n>; entry-drift <class> <verdict> ...; translation <verdicts or none>; open: <anything left>"`
   - one line per section - and close the claim with `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md
   LINE="Diagram reorg (diagram-reorg) | 292 | sweep buildings G18 checked, committed in clone | 2026-09-30"`. Your last
   message is one paragraph.
