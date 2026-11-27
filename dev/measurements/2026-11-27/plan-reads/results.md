# How many plan bytes do builders pull into context? 2026-11-26/27 builder transcripts

Task 451 T499. Asked: plan.md (824,251 bytes) and plan-done.md (3,131,453) are large; review bundles carry only changed blocks, but no
figure says what a builder's own Read and Bash calls returned. Method (`plan-reads.py`, read-only, `python3 -I plan-reads.py`; full
output in `results-full.txt`): every subagent transcript under `/home/agent/.claude/projects/-diagram*/` whose first prompt has a
line opening `BUILDER-BRIEF <feature> T<n>` and whose first timestamp is 2026-11-26 or 27 (114 builders, deduplicated by agent id;
this task's own builder left out). A call counts when it is a Read of a path named plan.md or plan-done.md (the returned text) or a
Bash whose command names either (its whole output - an UPPER bound where one command also ran something else, for example
`sed ...; cat other-file`; 19 "other bash" calls of 20,684 bytes and the few chained ones are the whole of that doubt). Bytes are
UTF-8 bytes of the tool result text; the denominator is the builder's total tool-result bytes (not its whole context: the system
prompt, brief and its own output are not in it). Tokens are an ESTIMATE at about 4 bytes a token.

## Per builder (the ten with most plan bytes; all 114 rows are in `results-full.txt`)

| task | start | plan bytes | tool-result bytes | share | calls |
|---|---|---|---|---|---|
| 451 T296,T297 | 11-27T06:21 | 116,795 | 199,688 | 58.5% | 17 |
| 451 T355 | 11-27T01:32 | 106,235 | 419,820 | 25.3% | 11 |
| 451 T308 | 11-27T02:05 | 87,458 | 367,848 | 23.8% | 20 |
| 451 T313 | 11-27T03:10 | 83,600 | 452,702 | 18.5% | 11 |
| 451 T365,T373,T420 | 11-27T05:12 | 78,206 | 233,760 | 33.5% | 12 |
| 451 T409,T406 | 11-27T04:20 | 77,585 | 337,105 | 23.0% | 7 |
| 451 T391 | 11-27T01:05 | 71,396 | 326,386 | 21.9% | 13 |
| 451 T311 | 11-27T05:45 | 69,444 | 224,170 | 31.0% | 11 |
| 451 T419,T404 | 11-27T03:51 | 67,451 | 241,350 | 27.9% | 30 |
| 451 T347 | 11-26T23:03 | 66,942 | 298,443 | 22.4% | 11 |

## Distribution and sum

plan bytes per builder: median 30,377, p90 63,808, max 116,795
share per builder: median 14.5%, p90 28.9%, max 58.5%
sum plan bytes 3,683,572 of 24,977,891 tool-result bytes (14.7%); builders reading any plan: 110
estimate only (about 4 bytes a token): 920,893 tokens total, 8,078 a builder mean

| shape | calls | bytes | share of plan bytes |
|---|---|---|---|
| grep | 563 | 1,830,901 | 49.7% |
| sed range | 114 | 1,206,194 | 32.7% |
| Read with offset/limit | 64 | 411,273 | 11.2% |
| cat/head/tail | 146 | 154,440 | 4.2% |
| awk | 7 | 60,080 | 1.6% |
| other bash | 19 | 20,684 | 0.6% |

largest single calls:
- 37,300 Read with offset/limit: /diagram/.clones/diagram-backlog-t271/specs/451-time-retro-and-efficiency/plan.md
- 37,300 Read with offset/limit: /diagram/.clones/diagram-backlog-t271/specs/451-time-retro-and-efficiency/plan.md
- 35,722 Read with offset/limit: /diagram/.clones/diagram-backlog-t270/specs/451-time-retro-and-efficiency/plan.md
- 29,540 grep: cd /diagram/.clones/diagram-backlog-b1 && grep -n "^### T307" -A60 specs/451-time-retro-and-efficiency/plan.md | head -120
- 29,540 grep: cd /diagram/.clones/diagram-backlog-b1 && grep -n "^### T307" -A60 specs/451-time-retro-and-efficiency/plan.md | head -120
- 28,418 sed range: cd /diagram/.clones/diagram-backlog-t270 && sed -n 3317,3404p specs/451-time-retro-and-efficiency/plan.md; sed -n 6925,6990p specs/451-time-retro-and-efficiency
- 28,390 sed range: cd /diagram/.clones/diagram-backlog-t271 && sed -n 3375,3470p specs/451-time-retro-and-efficiency/plan.md; echo ----; sed -n 5835,5900p specs/451-time-retro-and
- 28,207 sed range: cd /diagram/.clones/diagram-backlog-t270 && sed -n 14753,14800p specs/451-time-retro-and-efficiency/plan-done.md | cut -c1-2500 | tail -n +10; cat dev/measureme

## Reading

- No builder Read the whole file (the Read tool refuses them): 0 calls "Read whole file". Grep (563 calls, 49.7%) and sed ranges (114 calls,
  32.7%) carry 82% of the plan bytes; offset/limit Reads carry 11%. A grep is 3.3 KB a call, a sed range 10.6 KB, a Read 6.4 KB.
- Mean builder: 32 KB of plan (about 8,000 tokens, ESTIMATE) of 219 KB of tool results (about 55,000 tokens, ESTIMATE); 110 of 114 read
  some. Worst: T296,T297 at 116,795 bytes (58.5% of its tool results), about 29,000 tokens (ESTIMATE).
- Against the 300k-token context cap the mean is about 2.7% and the worst about 10% (ESTIMATE; the cap counts the whole context, which this
  denominator does not). A builder needs its OWN task's section (about 3 to 15 KB each) and its dependencies' lines, so a `make` target printing
  one task's section could save only the surplus, at most a third or so of 3.7 MB: about 2,500 tokens a builder (ESTIMATE). No lever filed.
