<!-- page-load: kind=split -->
# Brief - feature 269, finishing: split the questions over the size cap, part 3

You are a FRESH session in `/diagram/.clones/diagram-supplemental`; the research record's CLAUDE.md applies. Read
coordination files only with `make lines` / `make append`. Take registry and glossary prefixes with `make reserve`.

Split each of these along its topics, so that a question plus its notes stays under 20,000 bytes
(`python3 scripts/check-question-size.py`). A finding stays with its footnotes. The new question takes a free prefix
between its neighbors, and every pointer to a moved paragraph is repointed:
- `0061` (20,802 bytes after the 261 merge: the reeded shore and the mown embankment are its two topics).

After the split, quote-check the new and changed questions from bundles (`make check-bundle ... FOR=quote-check`, the agents in the background in one message) and apply the reports with `make apply-edits`.

Then `make record && make citations`, the four record tests, and the size check. Write
`specs/269-research-backfill/briefs/sp3-handoff.md` with one `- SECTION=<page>/<NNN>` line per question you created or
changed. Commit with the message `269 SP3: <what was split>`. Do not push. Your last message is one sentence.
