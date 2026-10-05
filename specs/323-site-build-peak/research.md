# Research: the record site's build peak (feature 323)

## R1 - Where the build's memory goes (observed 2026-10-04, method: tracemalloc over `site.build(RESEARCH_DIR)` in a one-shot test)

Before (observed 2026-10-04, method: tracemalloc): traced peak 312 MB, 148 MB still held when the build returns (RSS 48 -> 351 MB). The result is 2,698 files, 72.6 M
characters, 135 MB of Python strings: every page carries non-Latin-1 text (Japanese), so 69.1 M characters are stored at two
bytes each (132 MB). 134 MB of the traced memory was allocated at `site_pages.shell`'s return.

Observed 2026-10-04, method: tracemalloc and reading the code - the transient 164 MB above the result is the single page, `all.html` (22.0 M characters, 42 MB): `_single` holds its pieces,
joins them, `shell` passes the join to `linkify`, which splits it into a list of parts and joins its output, and the f-string
copies that into the page - four to five copies of 42 MB at once.

## R2 - The prototype (observed 2026-10-04, method: the same one-shot, every file compared with main's `research/site/` at cc4ba1e18)

Observed 2026-10-04, method: tracemalloc and a file-for-file comparison - `shell` taking the single page's pieces as a list, linkifying each in place and joining once: traced peak 312 -> 236 MB, the
result unchanged at 148 MB, all 2,698 files byte-identical to main's built site. What remains above the result is the pieces
and the joined page (two copies of 42 MB); the dictionary of strings the build returns needs the page whole, so streaming it
is out of reach without changing what `build` returns.

What is NOT in reach as a straightforward change (observed 2026-10-04, method: string sizes of the built site): the 148 MB result. Storing pages as UTF-8 bytes would make it ~75-80 MB but
changes the type every caller and test reads.
