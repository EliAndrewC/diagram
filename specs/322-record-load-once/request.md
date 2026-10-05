# The GM's request (2026-10-04), verbatim

> Eh, go ahead and fix it now, we might as well, even if it requires a full feature.

"It" - the session's explanation the GM was answering, verbatim:

> **The bug.** `record_text()` in `l7r/diagram/interactive/sources.py` returns one research page's text. Each page is cached,
> but the first time it reads a question page it calls `store.load()`, which reads and parses the entire research record (~480
> files, ~90 ms) just to render that one page. So any caller that reads N pages loads the whole record N times.
>
> **What I fixed.** The tests were the big victims: four tests read all 475 pages, about 42 s each. I added `text_of()` to
> `tests/_record_pages.py`, which loads the record once per test process and renders pages from it. That fixed the tests, but
> `record_text()` itself still has the bug.
