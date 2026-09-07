# Research - 208 The raster is a render

RENDERING/TOOLING research, nothing physical. Measured in the container on 2026-09-07 with a per-test RSS
plugin (a sampling thread at 20 ms), a cgroup sampler, tracemalloc on one file, and a per-stage wrapper.

## R1. The audit: what a page write costs, and who pays it

One rolling test (`tests/gate/test_paddy_fabric.py`, one worker, no coverage, roll cache bypassed), the
worker's RSS in MiB:

| step | before -> peak -> after | time |
|---|---|---|
| import the engine, collect | 111 | |
| the 18 placement stages of the hamlet roll | 70 -> 121 | 24 s |
| the page's vector part (`drop_offmap` x1,160, `merge_primitives` x591, wrap, hit regions) | 121 -> 146 | ~1.5 s |
| `raster.picture`: resvg at 3 px per map px, PIL decode, libwebp lossless encode | 146 -> **598** -> 173 | 7.3 s |
| `raster.id_map`: resvg at 1 px per map px, no PIL | 173 | 0.3 s |
| resting afterward | 250 (the allocator keeping freed C memory) | |

In isolation on Kuwabata's SVG: the PNG is 6.4 MB, PIL's decode to RGBA costs 70 MB (3210 x 5784 = 18.6 Mpx),
and the lossless WebP encode peaks a further 240 MB; afterward the process keeps 131 MB. Tracemalloc agrees:
at an 870 MB RSS peak only 93 MB was Python objects - the rest is C memory inside PIL and libwebp.

Under the gate (8 workers, coverage on): 21 tests peaked above 400 MB, 13 above 600, one above 800; three
workers in their raster step at the same moment put Python at 3.26 GiB and the container at 5,955 MiB
(baseline 2,768: three Claude processes and 1.6 GiB of file cache). Two gates at once reached the 8 GiB cap
(3,455 reclaim events, no kill).

**Who pays.** `Settlement.finish()` writes the SVG, then ALWAYS `write_html()`, and `render_page()` makes the
picture and the id map whenever the SVG has a viewBox. The `render` flag and `DIAGRAM_SKIP_RENDER` spare only
the PNG. So every roll a test makes pays the raster:

| caller | render | writes the raster today |
|---|---|---|
| `hamletgen/driver.py` `generate(out_base=None)` - the scratch finish into a temp dir, deleted at once | False | yes |
| `pipeline/rollcache.py` (the gate's cached rolls, `obtain` / `_produce_and_store`) | False | yes |
| `pipeline/gencache.py` `gate_obtain` (the pool sweep, in a coverage subprocess, `DIAGRAM_SKIP_RENDER=1`) | env | yes |
| `tools/cohort_audit.py`, `tools/mapcheck.py` | False | yes |
| `make map` / `regen` / render-sync (the shipped pool pages) | True | yes - and must |
| `tools/placement_stages.py` (the placement plates, eighteen per run, re-plated by the gate) | True | yes - and nothing reads the eighteen stage pages; the walk-through links the PNG plates. Found by the gate's sampler at 1.6 GB in one process (R5) |

**Who reads a rolled page's raster.** Nobody, since the rolled-page browser tests were retired earlier
today: `tests/interactive/test_raster.py` drives `picture()` and `id_map()` on a tiny hand-written SVG, and
`tests/interactive/test_page.py` drives `render_page` on synthetic strings. No test opens a rolled map's
page. About 30 raster writes per gate (21 in workers, the pool sweep's 10 in subprocesses), each 7.3 s and
450 MB, for pages nothing reads: roughly 3.5 CPU-minutes and every one of the memory spikes.

## R2. The change, and why a vector-only page rather than no page

The raster becomes a RENDER: made on the same condition as the PNG (`render=True` and `DIAGRAM_SKIP_RENDER`
unset). A test roll still writes its page - the string pass is about 1.5 s and some tests read the `.html`
beside a manifest (`tests/settlement/`, `tests/pipeline/test_render_cache.py`) - but the page carries
`"r": 0`: complete, openable, vector only, the form every page has on a host without resvg today. The shipped
pool pages are unchanged: `make map`, regen and render-sync render, and they keep the raster.

## R3. The picture in a subprocess

`raster.picture` keeps its signature and its output. The PIL decode and the WebP encode move into a child
Python that imports only PIL (`sys.executable -c`, the PNG on stdin, the WebP on stdout); the parent holds
the 6 MB PNG and the 3 MB WebP and nothing else. The child's 400 MB lives and dies with it, and glibc has
nothing to retain in the worker. Measured after the change (R5). `cwebp` (libwebp-tools) would do the same
without Python but is not installed; a PIL child adds no dependency. The id map stays in-process: it is
resvg's PNG straight through, 0.3 s, no PIL.

## R4. `malloc_trim` - only if the floor stays

The GM's condition: *"If writing in a subprocess is not enough to free the one hundred and thirty megabytes
of memory, then, yes, please also do the malloc_trim."* The resting floor after a page write is 250 MB; the
roll itself ends at 121. If, with the picture in a child, a worker still rests well above the roll's own
level, `ctypes.CDLL("libc.so.6").malloc_trim(0)` after the page write returns the freed arenas. Decided by
measurement, recorded in R5.

## R5. Measured after the change

**One test roll** (`tests/gate/test_paddy_fabric.py`, one worker, no coverage, cache bypassed, the same
instrument as R1):

| | before | after |
|---|---|---|
| picture / id map / resvg calls in the roll | 1 / 1 / 2 | 0 / 0 / 0 |
| `finish()` | 121 -> 598 -> 178 MB, 9.2 s | 121 -> 153 -> 146 MB, 1.6 s |
| the test's peak RSS | 598 MB | 153 MB |
| the file's 8 tests | 34.6 s | 27.3 s |

**A rendered page** (`make map GEN=pool/hamlets/kuwabata/kuwabata.gen.py`, the container sampled at 0.5 s):
the parent process sat at 118-125 MB before, during and after the picture; the child rose to 447 MB and
exited; resvg (its own process, as before) used 115-146 MB for the picture and 421 MB for the 2,600-wide PNG.
The parent's resting level after the page write, 125 MB, is the roll's own level (121 in R1) - the floor
the GM named (130 MB retained) is gone with the child, so `malloc_trim` is NOT added (FR-003, D3). The
page's raster payload is byte-identical to main's page for the same roll: picture sha 51b3c0e5c6e7bb9e,
id map sha 84dacedcbb6bd32d, before and after (SC-002).

**The gate** (`make done` with the same per-test plugin and cgroup sampler as the 2026-09-07 profile;
the container held 3.3 GiB idle at the start, against 2.8 before, most of it file cache):

| | the profile (before) | the landing gate (after) |
|---|---|---|
| test phase | 355 s (3,046 tests) | 315 s (3,050 tests) |
| container peak | 5,955 MiB | 5,568 MiB (with 0.5 GiB more cache at the start) |
| Python at the peak | 3,261 MiB | 2,047 MiB |
| worker peak in a test (highest / typical) | 808 / 630-750 MiB | 341 / 240-253 MiB |
| tests peaking above 400 / 600 / 800 MiB | 21 / 13 / 1 | 0 / 0 / 0 |
| a worker's resting level after its rolls | 245-266 MiB | 200-246 MiB |
| the placement-stages re-plate (one process) | 1,632 MiB | 210 MiB |

The one remaining outlier is the cohort test (`test_a_rolled_cohort_passes_the_whole_gate`, 341 MB over
252 s): it holds a whole cohort of rolls at once. What a worker now carries is the engine, the coverage
tracer and its rolled manifests - the shape the GM asked about is gone.
