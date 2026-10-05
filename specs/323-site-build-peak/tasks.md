# Tasks: the site build's peak (feature 323)

**Input**: plan.md (D1-D5)

## Occasions

- none: no map draws or places anything differently, and no page of the record changes - how one page is assembled (spec, Decisions Recorded)

## Tasks

- [x] T01 the baseline: the 323-start bookend at the pre-feature commit (plan, Performance bookends)
      research: rendering
      verify: DONE. 323-start bookend taken retroactively at cc4ba1e18 in a detached worktree (dev/perf-log/20261005T033114Z-323-start-base323.json)
- [x] T02 the frame split from the body; the single page assembled a piece at a time; the claim; the shell and fixture tests (D1-D5, FR-001 to FR-003)
      research: rendering
      verify: DONE. frame() and a list-consuming shell; _single passes its pieces; tests: pieces equal the whole, a registry URL linked on the fixture single page; tests/interactive 5,310 green
- [x] T03 the peak and the file-for-file comparison on the real record, recorded (SC-001, SC-002)
      research: rendering
      verify: DONE. final code: build peak 312 -> 236 MB, result 148 MB, 2,698 files byte-identical to main's site at cc4ba1e18 (research.md R3)
- [x] T04 make done; the 323-end bookend and the records its band owes; claims owed answered (FR-004, SC-003)
      research: rendering
      verify: DONE. make done green (200 s); 323-end re-taken alone: band 0 at 10/20/40 hh, band 1 on seed 25 at 15 hh (+2.5%, field), explained with control perf-control-seed25-15-field and confirmed consistent by perf-audit; no claim owed (research.md R4)
