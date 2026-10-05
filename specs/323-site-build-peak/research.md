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

## R3 - The final code (after T02)

Observed 2026-10-04, method: the same tracemalloc one-shot over `site.build(RESEARCH_DIR)` with `frame` and the list-taking
`shell`, every file compared with main's `research/site/` (built at cc4ba1e18, the same record): traced peak 236 MB (312 MB
before, R1), the result 148 MB as before, all 2,698 files byte-identical. SC-001 (at least 50 MB lower) and SC-002 hold.

## R4 - The bookends (observed 2026-10-04, method: `make perf-gate` and `make perf-profile`)

The first two 323-end bookends were taken while a full `make done` ran beside them in the same container (a failed gate's
command went on to the perf gate while the session re-ran the gate) and read band 3 at 40 households (+40.6%, +19.4%); they
measured that load, not the code, and are not committed. The 323-end re-taken alone (load ~3) reads band 0 at every household
count (-6.2 / -4.7 / -3.9%) and band 1 on one seed: seed 25 at 15 households +2.5%, field +0.1 s. Its control
(`measurements.json` `perf-control-seed25-15-field`): the field stage alternated on the base and the clone, three runs each,
the same 2,193,040 primitive calls, 1.501 s against 1.522 s medians - the same code, inside the run-to-run spread.
