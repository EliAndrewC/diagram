# Tasks - 208 The raster is a render

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` (tooling; nothing physical).

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code
      research: rendering
      verify: DONE. FAITHFUL at round 1 of 5; D1 (a vector-only page for test rolls) judged the literal request - 'it' is the picture, not the page; the review flagged gencache filing .html as a cached output under DIAGRAM_SKIP_RENDER, handled in T02
- [x] T02 the raster is a render: `render_page(raster=)`, `write_html(raster=)`, `finish` passes the PNG's
      condition (FR-001); the why at each point
      research: rendering
      verify: DONE. DONE. render_page(with_raster=True) - named so because raster is the module - via raster_wanted(); write_html passes it; finish computes rendering = render and not DIAGRAM_SKIP_RENDER once and uses it for both the page's raster and the PNG; gencache treats a skip-render .html as it treats the PNG (not filed, evicted; load deletes a standing one the entry lacks) - the spec review's hazard; the why at each point
- [x] T03 the picture's decode and encode in a PIL child (FR-002)
      research: rendering
      verify: DONE. DONE. raster.webp_lossless(png): a child python -c importing only PIL, the PNG on stdin, the WebP on stdout, a failing child raises RuntimeError with rc and stderr; picture() keeps its signature; the encode comment (203's method 0) moved with it
- [x] T04 measure the resting floor after a rendered page write; `malloc_trim` only if it stays (FR-003, D3);
      research R5
      research: rendering
      verify: DONE. DONE. Measured on make map of Kuwabata with the container sampled at 0.5 s: the parent sat at 118-125 MB before, during and after the picture (the roll's own level is 121); the child rose to 447 MB and exited; resvg 115-146 MB for the picture, 421 MB for the PNG. The 130 MB floor is gone with the child, so no malloc_trim (D3); research R5 records it and test_finish asserts no trim call exists
- [x] T05 tests (FR-004); SC-001 shown with the stage instrument on a test roll
      research: rendering
      verify: DONE. DONE. four tests: the child's bytes equal an in-process encode and a dying child raises (test_raster); with_raster=False never calls the encoder and is the r:0 form, raster_wanted's three cases (test_page); finish render=False / render=True / DIAGRAM_SKIP_RENDER=1 (test_finish); a skip-render page is not filed and a stale one evicted, load deletes the standing one (test_gencache); 16+75+22+20 passed. SC-001 shown with the stage instrument on test_paddy_fabric with the cache bypassed: picture calls 0, id_map calls 0, resvg calls 0; the test's peak 598 -> 153 MiB, finish 9.2 s -> 1.6 s
- [x] T06 SC-002: Kuwabata's page through `make map`, raster payload byte-identical to main's
      research: rendering
      verify: DONE. DONE. make map GEN=pool/hamlets/kuwabata/kuwabata.gen.py REGENERATED in 44 s; the page's picture (sha 51b3c0e5c6e7bb9e, 4,264,703 chars of data URI) and id map (84dacedcbb6bd32d) identical to main's page and to the clone's page before the change
- [ ] T07 the record (FR-006); `make done` green with the gate's peak and time recorded (FR-005, SC-003);
      land GATED
      research: rendering
