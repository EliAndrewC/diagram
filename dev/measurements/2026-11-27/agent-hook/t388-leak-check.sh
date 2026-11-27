#!/bin/bash
# t388: after the runs, nothing of the sandbox's reached the real state: no t388-* session or toolu_t388 id in the real event logs,
# the real checks state, check passes, prompt store, claim map or guard log; and the real targets' binaries were not rebuilt.
R=/diagram/.clones/diagram-backlog/.git
for f in "$R"/l7r-events/451-time-retro-and-efficiency.jsonl "$R"/l7r-events/_unassigned.jsonl "$R"/checks-open.json "$R"/check-passes.jsonl; do
  printf '%s\t%s\n' "$(grep -c 'toolu_t388\|t388-sess' "$f")" "$f"
done
printf '%s\t%s\n' "$(grep -rl 'toolu_t388\|(run [0-9]*)$' "$R"/l7r-agent-prompts 2>/dev/null | wc -l)" "prompt-store files naming a t388 run"
printf '%s\t%s\n' "$(ls /diagram/.clones/.session-clones | grep -c '^t388')" "claim-map entries t388-*"
printf '%s\t%s\n' "$(grep -rl 't388-sess\|toolu_t388' ~/.claude/guard-log 2>/dev/null | wc -l)" "guard-log entries naming t388"
stat -c '%y %n' ~/.cache/l7r-cargo-target/diagram/l7r-guard.good ~/.cache/l7r-cargo-target/diagram/tool/l7r-gate
