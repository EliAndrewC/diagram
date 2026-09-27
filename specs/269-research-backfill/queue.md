# The queue (plan D2)

`queue.txt` is the whole queue, in the inventory's "Queue order": for each group its write brief, then its checks
step, then a sync from main. `wait265.sh` holds the edit-existing groups until feature 265 has landed. Launch from
`.claude/skills/diagram` with `make page-session BRIEF="$(cat <clone>/specs/269-research-backfill/queue.txt)"`. To
relaunch after a dead runner, drop from `queue.txt`'s copy the groups the newest `.git/page-sessions/run-*.log` shows
finished (a group whose write session started but did not end is resumed with `claude --resume <sid>` first).
