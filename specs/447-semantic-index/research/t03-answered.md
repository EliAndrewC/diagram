# T03 "have we already answered this?" (amendment 2, the GM 2026-10-30)

Run 2026-10-30. 20 record pages drawn at random (`random.seed(447)` over the 549 numbered pages; 19 page numbers, 0198 drawn
twice). A sonnet agent read each page and wrote the question a GM would ask in his own words, told not to reuse the title's words
(`answered-questions.json`); a second sonnet agent, shown only the questions and never the record, gave up to three term sets for a
text search (`answered-terms.json`). `python3 specs/447-semantic-index/answered.py answered-questions.json answered-terms.json
answered-out.json` asked each question of the index (its rank among the record's pages in the first 200 passages) and ran the term
sets in order over `research/questions/*.html`, every term required (found when any file of the page's number is a hit).

```
index rank 1: 15/19, in first 3: 17/19, worst 6; text found on try 1: 14/19, by try 3: 19/19; pages in the finding search: median 16, range 1-88; index seconds 0.98-1.45
```

| page | index rank | text: found on try | pages that search returned |
|---|---|---|---|
| 0009 | 1 | 1 | 16 |
| 0018 | 1 | 1 | 16 |
| 0043 | 3 | 1 | 28 |
| 0048 | 1 | 1 | 88 |
| 0065 | 1 | 2 | 2 |
| 0068 | 6 | 1 | 27 |
| 0086 | 1 | 1 | 5 |
| 0100 | 1 | 1 | 55 |
| 0124 | 1 | 3 | 71 |
| 0134 | 1 | 1 | 29 |
| 0153 | 1 | 1 | 15 |
| 0181 | 4 | 2 | 18 |
| 0198 | 1 | 1 | 1 |
| 0207 | 2 | 1 | 5 |
| 0215 | 1 | 1 | 16 |
| 0216 | 1 | 1 | 13 |
| 0236 | 1 | 1 | 23 |
| 0281 | 1 | 2 | 2 |
| 0306 | 1 | 2 | 11 |

The caveat: the questions were written by an agent that had read the pages, so some of their vocabulary may be the pages' own,
which helps both searches alike; the term-picking agent never saw the pages.
