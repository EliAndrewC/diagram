# Feature 208 - the raster is a render

**Status**: FAITHFUL (`spec-fidelity`, round 1 of 5) - cleared for implementation (constitution XVI). The review flagged one implementation hazard, taken up in FR-001: the generation cache must not file a skip-render page as a pool output.
**Request**: [`request.md`](request.md) - the GM's words verbatim.
**Research**: [`research.md`](research.md) - the audit: what a page write costs, who pays it, who reads it.
**Predecessors**: feature 200 (the page's raster picture and id map); 134 (the page beside every map);
203 (the WebP encode at method 0).

## Summary

The GM: *"we're doing a whole lot of rasterizing that is completely pointless and not actually needed for
the tests. Right? please do an audit, and then Make the change to write the picture in a subprocess. And,
also, to not write it at all for test rolls where it is not needed."* The audit (R1) found the page's
raster made on every roll, test rolls included - about 30 times per gate, 7.3 s and a 450 MB spike each,
for pages nothing reads. This feature makes the raster a render, like the PNG: made only when the roll
renders. When it is made, the picture's decode and encode run in a child process, so the worker never holds
them. If a worker still rests far above the roll's own level afterward, the freed memory is trimmed.

## Functional requirements

- **FR-001 The raster is a render.** The page's picture and id map are made only under the condition the
  PNG is made today: `finish(render=True)` with `DIAGRAM_SKIP_RENDER` unset. `render_page` gains
  `with_raster: bool = True` (named so because `raster` is the module it calls); `write_html` passes it
  through; `finish` passes `render and not DIAGRAM_SKIP_RENDER`. The generation cache treats a
  skip-render page as it treats a skip-render PNG: not filed as the key's output and evicted from the
  entry, so a later cache hit never restores a vector-only page into the pool (the review's hazard).
  **And the placement plates** (`tools/placement_stages.py`, found by the gate's own sampler at 1.6 GB in
  one process): each of the eighteen stage plates finished a copy with `render=True`, making a full page
  raster nothing reads; the plate is the PNG, so the page is written vector-only and the PNG rendered by
  the same call `finish` made - the plates' pixels are unchanged.
  A roll that does not render writes a complete vector-only page (`"r": 0`, no image element) - the same
  page a host without resvg gets today - so a test that reads a rolled page still finds one. The shipped
  pool pages (`make map`, regen, render-sync) render and keep their raster.
- **FR-002 The picture in a subprocess.** `raster.picture` keeps its signature and output. The PIL decode
  and the lossless WebP encode (method 0, quality 100) run in a child Python that imports only PIL, fed the
  PNG on stdin and returning the WebP on stdout; the parent holds only the PNG and WebP bytes. A child that
  fails raises with its stderr. Same pixels: the existing lossless tests hold unchanged.
- **FR-003 `malloc_trim` if the floor stays.** After FR-002, measure a worker's resting RSS after a
  rendered page write against the roll's own level (121 MB in R1). If the floor stays well above it, call
  `malloc_trim(0)` through ctypes after the page write; if the subprocess alone brings it down, do not.
  Either way the measurement and the decision are recorded (research R5, spec D3).
- **FR-004 Tests.** `finish(render=False)` on a small settlement writes a page with `"r": 0` and no
  `<image id="raster">`; `finish(render=True)` writes one with the raster; `DIAGRAM_SKIP_RENDER=1` yields
  `"r": 0` even with `render=True`; `render_page(..., with_raster=False)` makes neither picture nor id map (a
  monkeypatched `raster.picture` is never called); `picture()`'s child produces byte-identical WebP to an
  in-process PIL encode of the same PNG; a failing child raises and names the failure. Whatever FR-003
  decides is tested: the trim call is made after a rendered page write, or it does not exist.
- **FR-005 Measured before and after.** The per-roll cost of a test roll (R1: 7.3 s, a 450 MB spike) and
  the gate's peak and test-phase time (the 2026-09-07 profile: 5,955 MiB, 355 s) against the same
  measurements after the change, in research R5.
- **FR-006 The record.** The why at each point of change (`finish.py`, `page.py`, `raster.py`), the
  `raster.py` row of `interactive/CLAUDE.md`, and the memory findings in `dev/performance.md`.

## Success criteria

- **SC-001** A test roll (`generate(out_base=None)`, the roll cache, the pool sweep under
  `DIAGRAM_SKIP_RENDER`) makes no picture and no id map: the raster functions are not called.
- **SC-002** `make map GEN=pool/hamlets/kuwabata/kuwabata.gen.py` writes a page whose raster payload is
  byte-identical to the one main's page carries today for the same roll.
- **SC-003** `make done` green; the gate's peak memory and test-phase time recorded against the profile.

## Decisions Recorded

- **D1 - a vector-only page for a test roll, not no page.** The string pass is about 1.5 s of a 36 s test and
  tests read the `.html` beside a manifest; the page without its raster is a form every page already has
  (no resvg on the host). Removing the page would have changed what a test roll leaves on disk for a
  saving nobody asked for.
- **D2 - a PIL child, not `cwebp`.** libwebp-tools is not installed and a PIL child adds no dependency;
  the output is the same library's. Revisit if a faster encoder is ever wanted.
- **D3 - `malloc_trim` decided by measurement** (FR-003), as the GM conditioned it.
- **D4 - the id map stays in-process.** It is resvg's own PNG, no PIL, 0.3 s.
