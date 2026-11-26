---
kind: adopted
title: the builders' fixed report format
for: a builder's report is written in fixed fields (scripts/container/builder-report-format.md) so that it carries what the coordinating session goes on to use and not what it never reads, the report being re-read on every later turn of the session
measured: 2026-11-26
measurement: 38 builder reports of 2026-11-25/26, median 4,415 characters; never used afterwards: the modified-path list (0 of 32), a passing check's own line (0 of 26), "how to test" (0 of 5); fourteen re-expressed in the format came to 55% (the eight longest), 69% (four typical) and 98% (two short) of their length with no used item lost; the saving about 0.74% of the session's input tokens raw, a tenth of that weighted for cached reads
command: python3 dev/measurements/2026-11-26/report-format/m14r-reports.py (and m14r-parts.py, m14r-windows.py, m14r-check.py beside it; they read the coordinating session's transcript, so the 2026-11-26 tables are kept in m14r-results.md)
falsifier: a report in the format from which the session lacked something it needed
threshold: one such loss in the next twenty reports reopens the capped fields (BUILT's eight bullets, the second table as a path); the caps are GUESS knobs
cost: the format file read once by each builder at its stop point (about 600 tokens)
last-audited: 2026-11-26
cadence-days: 14
---

Adopted on the GM's pre-approval for the talk's item 14 (`docs/process-decisions.md`, "The builders' report has a fixed
format"). No guard enforces it. The measurement's caveats: the re-expressions were written knowing what was used; the 24
reports not re-expressed are estimated; a brief that needs a second table whole must say so.
