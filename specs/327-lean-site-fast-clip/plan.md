# Implementation Plan: A leaner site build and a faster clip

**Feature**: 327-lean-site-fast-clip | **Spec**: spec.md | **Request**: request.md

## Summary

The site build fills a `SiteFiles` mapping that holds each page as UTF-8 bytes and gives text on read. The off-map clip is split
into a one-time parse of a line (`prepare_offmap`) and a cheap per-box assembly (`assemble_offmap`); `drop_offmap` is the two in a
row, and a picture prepares its classed lines once and assembles them per tile.

## Performance bookends (constitution VI)

Both taken back to back at the end, in a window arranged with the container's other session by message (features 324 and 326's
lesson): `make perf LABEL=327-start` in a detached worktree at the pre-feature commit (06fea4766), then `make perf-gate` in the clone.
The snapshot times only the roll's stages, which neither change touches.

## Decisions

**D1 - `SiteFiles` (FR-001, FR-002).** A `collections.abc.MutableMapping[str, str]` in `record/site.py` whose store is a dict of
UTF-8 bytes: `__setitem__` encodes, `__getitem__` decodes, `__iter__`/`__len__`/`__delitem__` as a dict's. `__eq__` compares the
stores when both sides are `SiteFiles` (two builds compared without decoding), else falls back to the mapping comparison. `raw(path)`
gives the bytes. `Build` fills one (`self.files: SiteFiles`), so each page is encoded as it is built and its text freed; `build`
returns it. `write` writes each page's bytes in binary mode when it is given a `SiteFiles` - the same bytes the text mode wrote,
since the text is written as UTF-8 with no newline translation on Linux - and text as before otherwise.

**D2 - The clip, parsed once (FR-003).** `prepare_offmap(s)` returns the line as a list of parts: fixed text, a shape element with its
box, or a merged path (its opening, its subpaths each with a box, its closing). `assemble_offmap(parts, vb)` keeps a shape whose box
meets the viewBox plus `OFFMAP_MARGIN`, keeps a path's subpaths that do and drops the path whole when none does - exactly
`drop_offmap`'s rules, which become `assemble_offmap(prepare_offmap(s), vb)`. A line with a `transform` prepares to one fixed part.
The paths are matched before the shapes, as `drop_offmap` substituted them, and the two never overlap (a shape element cannot sit
inside a path's tag).

**D3 - A picture's lines prepared once (FR-003, FR-004).** `picture` prepares the classed lines once (`prepare_doc`: a classed line as its
parts, any other line as its text) and each tile's `tile_doc` assembles from them; the tile's viewBox set as now. The prepared form
holds the line's text in pieces plus a box per droppable element - measured against the render's peak (SC-004).

**D5 - One cap on resvg processes (FR-004).** Measured (research.md R3): with the clip parsed once the tiles no longer stagger,
start together and overlap the PNG and the id map, and the render's peak rose. A module-level `RESVG_SLOTS =
threading.BoundedSemaphore(4)` in `raster` is held around every resvg launch in the process - `resvg_png` (the tiles, the id map)
and `finish.render_png` (the PNG) - so at most four run at once; only the scheduling changes. Four, not three: both measured the
same, and four keeps the tiles and one whole-map render together.

**D6 - The single page built as bytes (FR-001, SC-001).** Measured (research.md R2): holding the pages as UTF-8 alone raised the
build's peak, because the single page was joined as 42 MB of text and then encoded. `site_pages.shell_utf8` links and encodes the
single page's pieces one at a time and joins the bytes; `SiteFiles.set_raw` takes them. `shell` keeps its text form for every
other page.

**D4 - Research claims.** New units inherit their modules' claims; `make claims-owed` decides what is owed.

## Tests

- `tests/interactive/test_raster.py`: `assemble_offmap(prepare_offmap(line), box)` equals a REFERENCE copy of the old
  `drop_offmap` (kept in the test) for every line of a real page fixture and many boxes, including transform lines, paths outside
  the grammar, shapes in both attribute orders and lines whose every part drops; `tile_doc` from prepared lines equals it from text.
- `tests/interactive/test_raster.py`: never more than four resvg processes at once, the picture the same bytes.
- `tests/interactive/test_record_site.py`: `shell_utf8` of a page's pieces equals `shell` of their join, encoded; `SiteFiles` round-trips text, compares equal and unequal without decoding, iterates and
  measures like a dict; `write` writes the same bytes from a `SiteFiles` as from a dict.
- SC-001, SC-002 and SC-004 measured once, recorded in research.md.

## Verification

`make test-file FILE=tests/interactive`; the measurements; `make done`; the bookends.

## Constitution Check

No map draws or states anything differently; pictures and pages byte-identical (no Decisions Recorded entries). Not a research
question. 100% coverage for the new units from the tests above.
