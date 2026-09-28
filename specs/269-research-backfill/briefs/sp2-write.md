<!-- page-load: kind=split -->
# Brief - feature 269, finishing: split the questions over the size cap, part 2

You are a FRESH session in `/diagram/.clones/diagram-supplemental`; the research record's CLAUDE.md applies. Read
coordination files only with `make lines` / `make append`. Take registry and glossary prefixes with `make reserve`.

Split each of these along its topics, so that a question plus its notes stays under 20,000 bytes
(`python3 scripts/check-question-size.py`). A finding stays with its footnotes. The new question takes a free prefix
between its neighbors, and every pointer to a moved paragraph is repointed:
- `vegetation/120`;
- `water/070`;
- `water/270`.

Then `make record && make citations`, the four record tests, and the size check. Write
`specs/269-research-backfill/briefs/sp2-handoff.md` with one `- SECTION=<page>/<NNN>` line per question you created or
changed. Commit with the message `269 SP2: <what was split>`. Do not push. Your last message is one sentence.
