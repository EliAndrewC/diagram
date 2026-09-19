# Where this feature comes from

Features 251 to 253 (2026-09-19) measured what the subagent checks cost and tried to cut it. Every MODEL
downgrade of a judgment check missed recorded findings; effort moved little; and a free pass over the
transcripts (`specs/251-tiered-subagent-checks/research.md` R9) showed why: a check's cost is roughly its
TURNS times (a fixed context of 47-67 k tokens plus everything it has read so far). The session reported a
list of tooling candidates that follow from that, and one unrelated test defect.

## The GM's words (2026-09-19)

> there is a "Diagram tests" session which you should talk to to hand off a bug report about the unrelated defect you described.  When you've done that, make a new feature for all of the findings which you believe are worth investigating and/or pursuing.

(The bug report - `make quick`'s intermittent "different tests were collected" - was handed to the "Diagram
tests" session before this feature was claimed. It is not part of this feature.)

## The findings the session had reported, which the GM's "the findings" refers to

| agent | what the transcripts show | the candidate |
|---|---|---|
| `settlement-review` | 43 turns and 39 shell calls a run; a 48 k-character contract re-read every turn; the most expensive check per run | one script call that returns every standard measurement, and the contract trimmed of its worked examples |
| `source-applicability` | reads the whole sources registry about 10 times a run to find a few entries | a script that extracts entries by key and hands them over |
| `record-format`, `quote-check` | read whole research pages even when the check is scoped | the scope flags already built (`SECTION=`, `NOTES=`) emit the in-scope text, so the agent never opens the page |
| `spec-fidelity` later rounds | 7 turns at 50 k fixed context each | a contract line telling the agent to send independent reads and greps together |
| `source-reader` | works from the fetch tool's extracts, never the page; reading whole pages found the passage every cheaper tier missed, at 2-8 times the cost | a script that saves the named pages' text, the reader grepping it and reading only around the hits |

And, from the same report: every check starts at 47-67 k tokens before it reads anything, where a bare agent
in an empty project starts at about 2 k and one inside this repository at 12-15 k - what fills the rest was
not established.

Ruled out in that report, and not part of this feature: `perf-audit` (10 runs in all), `building-review` and
`size-audit` (no recorded runs to measure), and any cheaper MODEL for a first reading or for
`settlement-review`.
