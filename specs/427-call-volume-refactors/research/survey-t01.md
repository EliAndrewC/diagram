# The survey, re-run as a command (T01, FR-002)

**Load this file when:** you scope an engine task of this feature against the survey (FR-002).

- **Command**: `make perf-fanout LABEL=427-T01` (seed 39, 20 and 40 households, every stage, HOT 50,000, JOBS 3), run
  2026-10-26 on the engine at commit 917e46132; the report is `dev/perf-log/20261026T164639Z-fanout-427-T01.txt`.
- **Against the hand survey** (`fanout-2026-10-26.txt`, commit dd3793e29): all stages 24,140,034 calls at 20 households and
  62,648,969 at 40, where the hand survey had 24,140,555 and 62,798,345 - the engine barely moved between them.
- **The stages by calls at 40** (observed 2026-10-26, method: the command above): lane_wells 22.6M (growth exponent 2.24, the
  cubic term R1 names), web 11.1M, homesteads 10.7M, hinterland 6.0M, field 4.5M, windbreak 3.9M, appurtenances 1.9M, notice 1.0M;
  every other stage under 0.3M.
- **So** the order the GM approved (`request.md` 5) holds as the survey reads it: the wells (US3) carry the largest share and
  the only super-quadratic growth; the lane web (US4's lane family) is second and waits for feature 417's lane conversions.
