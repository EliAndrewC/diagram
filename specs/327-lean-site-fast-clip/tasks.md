# Tasks: a leaner site build and a faster clip (feature 327)

**Input**: plan.md (D1-D6)

## Occasions

- none: no map draws or places anything differently - pictures and pages byte-identical (spec, Decisions Recorded)

## Tasks

- [x] T01 SiteFiles: the build holds pages as UTF-8, the single page built as bytes, write writes their bytes; its tests (D1, D6, FR-001, FR-002)
      research: rendering
      verify: DONE. SiteFiles holds pages as UTF-8; shell_utf8 builds all.html as bytes; write writes the bytes; tests: round-trip, byte compare, write same bytes, shell_utf8 equals shell encoded; tests/interactive 5,318 green
- [x] T02 the clip parsed once: prepare_offmap / assemble_offmap, drop_offmap as the two, picture preparing its lines once; one cap on resvg processes; the reference-equality and cap tests (D2, D3, D5, FR-003, FR-004)
      research: rendering
      verify: DONE. prepare_offmap/assemble_offmap, drop_offmap as the two, prepare_doc once per picture, RESVG_SLOTS 4; tests: reference drop_offmap equal over the real-line fixture and edge cases at 90 boxes, tile_doc prepared equals text, cap counted (red uncapped at 9)
- [x] T03 the measurements: the site's result and peak, every file against main's site; the clip's CPU, the render's span and peak alternated, every pool picture against today's (SC-001, SC-002, SC-004)
      research: rendering
      verify: DONE. site: peak 236 -> 165 MB, held 148 -> 84 MB, 2,698 files identical to main; clip CPU 0.82-0.92 -> 0.11-0.12 s; render 5 rounds alternated: peak 374.6 -> 370.6 MB mean, span 3.55 -> 3.21 s, PNG and page identical; 5 tiled pool pictures identical (research.md R2, R3)
- [x] T04 make done; both bookends back to back in an arranged window and the records their band owes; claims owed answered (FR-005, SC-005)
      research: rendering
      verify: DONE. make done green (209 s); claims IN-STEP 26/26; 327 bookends back to back in an arranged window: band 3 at 20 households under falling load, control and perf-audit (consistent, justified), the GM signed off 2026-10-05 (research.md R4)
