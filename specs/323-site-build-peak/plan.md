# Implementation Plan: The site build's peak

**Feature**: 323-site-build-peak | **Spec**: spec.md | **Request**: request.md

## Summary

`site_pages.shell` takes the single page's body as its list of pieces, makes each piece's links in place and joins once;
`Build._single` hands it that list. Every other page is built as before.

## Performance bookends (constitution VI)

`make perf LABEL=323-start` taken retroactively in a detached worktree at cc4ba1e18 (the pre-feature commit; the prototype was
already in the clone's working tree - the gate's documented retroactive form) and `LABEL=323-end` at the last commit;
`make perf-report AGAINST=323-start`. Map generation does not build the site, so no band is expected.

## Decisions

**D1 - The page's frame split from its body (FR-002).** A function `frame(title, here, open_keys, *, lazy_glossary)` returns the
text before and after the page's content - everything `shell` writes, up to `<main>\n` and from `\n</main>` on. `shell` with a
string body is `head + linkify(body) + tail`, the same bytes as today's f-string.

**D2 - The single page assembled a piece at a time (FR-001).** `shell` given a LIST makes each piece's links in place
(`body[i] = linkify(body[i])`, so the old piece is freed as its linkified one replaces it) and returns `"".join([head, *body,
tail])`. `_single` puts its heading and its table of contents at the front of its `out` list and passes that list. The list is the
caller's and is consumed: documented in `shell`'s docstring.

**D3 - Why per piece is the same as the whole (FR-002).** `linkify` splits its input at markup (`_MARKUP_PART`: a comment, an `<a>`
element whole, a script, a style, a tag) and links URLs only in the text between. Each of `_single`'s pieces is a whole fragment
(a question page, a section opening or close, a note list, a registry entry), so no link, comment, script or style spans two
pieces, and splitting the whole or each piece finds the same text. Proven on the real record by the file-for-file comparison
(SC-002), and on a constructed case by a unit test.

**D4 - What stays (FR-003).** `build` still returns the path-to-text dictionary; the other `shell` callers pass a string as now.

**D5 - Research claims.** `frame` carries `Research: page frame - NONE: process plumbing`; `shell` and `_single`, whose code
changes, are owed `impl-drift` only if `make claims-owed` says so.

## Tests

- `tests/interactive/test_record_site.py`: `shell` given a list of pieces (a bare URL, a URL inside a link, a comment holding a URL)
  equals `shell` given their join; the list form linkifies each piece; the fixture record's single page carries its entries' URLs
  as links.
- SC-001 and SC-002 as a one-shot over the real record, recorded in research.md (as feature 322 did for its full comparison: a
  permanent test would build the whole site again in the gate).

## Verification

`make test-file FILE=tests/interactive`; `make done`; the bookends.

## Constitution Check

No map draws or states anything differently, and no page of the record changes (no Decisions Recorded entries). Not a research
question. 100% coverage for the new and changed lines from the tests above. Fix-where-found (XIV) applies to what the change
exposes.
