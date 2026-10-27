# Tasks - feature 438, the trial form and perf-share

## Occasions

- none: tooling only - no map feature, glyph or placement rule

## Tasks

- [x] T01 `make perf-share`: a module's share of each stage's time and its callers, read from the kept raw profiles (`PROFILES=`, else the newest of the seed, size and stage, else profiled then); `make perf-profile` names its raw profile with the household count (D1, D2; FR-001, FR-002, FR-007)
      research: rendering
      verify: DONE. landed in batch T01+T02: make perf-share (a module's share of each stage, from the kept profiles; 437's reading in under a second); make trial and the review gate's trial clause
- [x] T02 The trial form: `make trial SLUG=` writes a trial brief (`**Form**: trial`) from its template; the review gate passes a verdict-less trial not Done whose push leaves the engine unchanged on net; the docs (D3-D5; FR-003, FR-004, FR-006, FR-007)
      research: rendering
      verify: DONE. landed in batch T01+T02: make perf-share (a module's share of each stage, from the kept profiles; 437's reading in under a second); make trial and the review gate's trial clause
