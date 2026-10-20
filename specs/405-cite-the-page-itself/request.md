# Feature 405 - the request

## The GM's words, verbatim (2026-10-19, answering the money session's open items)

```
Yes, a cell in a public spreadsheet counts as a readable page. And yes, Morisata and Gamble Notes may link straight to their page.
```

(Dictation: "Morisata" is Morisada, the author of 守貞謾稿 / 類聚近世風俗志.)

## What it answers

- Feature 400's checks asked whether a cell of a public .xls download counts as a readable page: 0275's and 0260's
  Bochum (Zhili 物料價值則例) rows are quoted from the chapter spreadsheets, but the notes link the database's landing
  page, where no row can be read.
- Features 402 and 403 asked whether a Morisada note may link to its NDL koma page, and a Gamble note to its page image:
  `tests/interactive/test_sources.py` forces every note's link to the registry entry's FIRST URL (the volume, the
  book's landing page), so quote-check reports the passage as not on the linked page.
