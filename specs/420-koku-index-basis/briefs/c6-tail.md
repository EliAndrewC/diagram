<!-- page-load: kind=check -->
# Brief - feature 420, session C6: the tail of C1, C2 and C3

You are a FRESH session for one part of one feature. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/diagram-money-marks`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.
The clone has just been merged with main (0298-0300 from the other queue are in it; leave them alone).

**What is left.** The check sessions C1-C3 each ended with a `STILL OWED:` line in
`specs/420-koku-index-basis/briefs/c1-checks.md`, `c2-checks.md` and `c3-checks.md`. Read those three lines first; this brief
settles them.

**Yours:** 0265, 0286, 0301, 0302 and the registry keys those checks named. Nothing else.

## Fixes first (commit each, messages opening `420: `)

1. **0265:** "one official's house" and "the official Li Ciming" rest on no quoted passage. Quote Wu's sentence naming his post
   if the source has one (read it on its page); otherwise write "one man's house" and "Li Ciming".
2. **0301:** the heading "Kyoto 1745-1754's grains, other beans and fish are Tokyo 1882-1886's" is loose for the beans (0.66
   against 0.67; the paper's own ratio 0.63): reword it to what the figures show. The fish-absence note's "the rice series"
   names no series the page introduces: name it (Iwahashi), or reword.
3. **0302, Hong Liangji's place in 1793:** C3's source-applicability found Hong away from Changzhou from 1790 (Beijing, then
   Guizhou from autumn 1792). Settle where his "now" prices describe: search Kotobank, the CBDB, Chinese Wikipedia and the essay
   itself (`make archive-find`, then the web) for where he was when he wrote 『意言·生計篇』 and what place the essay speaks of.
   Write what a source says; if none settles it, label the present prices with what the essay supports (his home district, as
   he reports it) and say the year and place of his observation are not stated. The table's suzhou-1750 cells and any
   `data-paid` follow.
4. **Glossary and links where C1 found them missing** (fix those that are quick, as a session would on its own pages): the
   glossary gaps C1 named (han, biaobu, laoyangpi, mianchou, guihai, wuchen, cash, yin) that the pages use and the glossary
   lacks (`research/assets/glossary-variants.txt`; one file per term, `make glossary`); Miyamoto 1963 and 『柳菴雑筆』 linked if a
   readable page exists, else left as named.
5. **Not yours to decide:** C3's question for the GM (the djvu text-layer links on 0302's Timkovski notes) - leave the notes
   as they are and do not change the first-URL rule. The Osaka 1832 letter-book's era (C1) and the kyoto-1790/1800 salt
   confidence text (gm-assistant's file) - leave them.

## Then the checks (check, apply)

1. `make record-owed` names every unit owed. A check's THIRD round on one subject (record-format 0286 and 0301, translation-check
   0301#kusano-1996-kinsei-shijo-keizai, per C2's line) goes to the round arbiter first: `make arbiter-bundle
   TRIGGER="round:<check>|q:<n>@3"`, dispatch `round-arbiter` on its MANIFEST, and follow its ruling. The rest: in the
   background, in one message, one agent per owed unit of yours, each from its own bundle (`make check-bundle Q=<n> FOR=<check>`;
   `make quote-verbatim Q=<n>` before quote-check; `make check-bundle KEY=<k> WHOLE=1` for source-reader; `make check-bundle
   KEY=<k>` for source-applicability on a changed write-up). Four or more of one check go as ONE `check-wave` workflow.
2. `make apply-edits FROM=<each output_file>`; apply by hand only what it refuses or lists as `EDIT: none`. Then `make record &&
   make citations` and the record tests once (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`),
   and answer each check with `make record-checked`. Commit each fix with a message opening `420: `. Do not push.
3. Append one line per check to `specs/420-koku-index-basis/briefs/c6-checks.md` with `make append`, then a last line `STILL OWED:`
   naming anything left (`make record-owed UNANSWERED=1` must show nothing of yours). Your last message is one paragraph.
