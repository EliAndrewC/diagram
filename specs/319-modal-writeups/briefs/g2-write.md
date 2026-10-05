# Brief - feature 319, G2: two defects found by G1. Session 1: write

You are a FRESH session for one part of feature 319. This brief is the whole of what you need; do not read the feature's spec or
plan. Work in this clone (`/diagram/.clones/diagram-html`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all.

## Your items (two questions; no new registry key expected - `ihns-bunongshu` exists)

- **0015** (`research/questions/0015-flower-growing-and-the-chrysanthemum-kiku.html` and its notes). Its absence note
  `flower-growing-and-the-chrysanthemum-kiku-2` says the text of Zhang Lüxiang's *Bu nongshu* "was not found on any readable
  page", and its group "How old is Tongxiang's chrysanthemum growing?" concludes "Tongxiang's is a modern case". The book is now
  read in full (feature 319 G1): http://agri-history.ihns.ac.cn/books/bns.htm, registry key `ihns-bunongshu`, archived at
  `/diagram/.specify/source-archive/29/29913b34ce12/20261004T222822Z/text.txt`. Its passage on 甘菊 (sweet chrysanthemum), found by
  a grep - read the whole passage yourself:
  「…每地棱头种一二枝，取其花可以减茶叶之半。茶性苦寒，与甘菊同泡，有相济之用，若种之成亩，其利视种豆自倍，吾里不种棉花，亦有以此为业者，但费采摘工夫，及适市贸易，耳目混乱耳。」
  (on the pass's reading, to be your own: one or two plants at the head of each field ridge; its flowers can halve the tea
  leaves; brewed with tea; grown by the mu, its profit is double that of beans; in my district, which does not grow cotton, some
  make it their trade, though it costs picking labor and the bustle of selling at market). The book is dated 1658 by its editor
  (see how 0039 cites `ihns-bunongshu`). Correct the group and its conclusion to what the book says, with its limits (one author,
  partly prescriptive; 甘菊 is the tea chrysanthemum - say how the record identifies it, or that the book does not say which
  flower), and the absence note to what is still not found. Any other sentence in 0015 or in a page that cites its conclusion
  (grep `research/questions/` for "modern case" and for 0015's heading id) that the correction makes false is yours too.
- **0029** (`research/questions/0029-farmhouses-minka.html`) is 20,007 bytes of prose, over the 20,000 cap
  (`python3 scripts/check-question-size.py` from the clone root): tighten its own wording by a few words without dropping a
  finding or a footnote.

Do NOT edit any drawing page or any modal file.

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="0015"` and `KEY="0029"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | G2 in progress (0015 Bu nongshu chrysanthemum, 0029 size) | 2026-10-04"`.
2. `make source-pages`, then the source-reader agent from a bundle on every passage you will quote.
3. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/319-modal-writeups/briefs/g2-handoff.md` (one `- SECTION=<NNNN>/<id>` line per question touched and a sentence
   each), commit only your files (message beginning `319 G2:`), do not push. Your last message is one paragraph.
