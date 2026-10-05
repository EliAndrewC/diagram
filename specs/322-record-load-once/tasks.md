# Tasks: the record loaded once (feature 322)

**Input**: plan.md (D1-D5)

## Occasions

- none: no map draws or places anything differently - a cache in the record's reader (spec, Decisions Recorded)

## Tasks

- [x] T01 the baseline: the 322-start bookend on unmodified code (plan, Performance bookends)
      research: rendering
      verify: DONE. 322-start bookend taken on unmodified code (dev/perf-log/20261005T025634Z-322-start-diagram-performance.json)
- [x] T02 the loaded record cached per directory and forgotten by clear_caches, with its claim; the load-count, two-directory, edit and byte-identity tests (D1, D2, D3, D5, FR-001 to FR-004, SC-001 to SC-004)
      research: rendering
      verify: DONE. sources._loaded per normalized dir, cleared by clear_caches, its claim; count/two-dir/edit tests pass and each went red on the unfixed code; SC-004 byte identity one-shot over every real page (research.md R2)
- [x] T03 the test helper reads through record_text; the four record tests timed (D4, FR-005, SC-001, SC-005)
      research: rendering
      verify: DONE. text_of returns record_text(rel); the four record tests 3.81/0.87/0.30/0.23 s vs the workaround's 3.8/1.0/0.3/0.2; tests/interactive 5,308 green in 16 s (research.md R2)
- [x] T04 make done; the 322-end bookend and the records its band owes; claims owed answered (FR-006, SC-005)
      research: rendering
      verify: DONE. make done green (158 s); 322-end bookend band 0 at 15/20/40 households, owes nothing; claims-owed none after impl-drift IN-STEP 3/3
