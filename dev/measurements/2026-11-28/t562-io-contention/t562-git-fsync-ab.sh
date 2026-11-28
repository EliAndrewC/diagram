#!/usr/bin/env bash
# t562 lever: git's fsyncs in test-fixture repos. A fixture-like loop (init, add, commit, branch, update-ref, status) N times,
# with git's default fsync against core.fsync=none (set by GIT_CONFIG_COUNT env, as a test harness would), alternated ABAB so
# load drifts hit both. Reports wall seconds and the jbd2 'requested' (forced) transactions over each run.
# Usage: t562-git-fsync-ab.sh <scratch-dir> <out.tsv> [N] [rounds]
set -u
S=${1:?}; OUT=${2:?}; N=${3:-40}; R=${4:-3}
J=/proc/fs/jbd2/nvme0n1p3-8/info
req() { sed -n 's/.*(\([0-9]*\) requested).*/\1/p' $J; }
printf 'setting\tround\tseconds\tjbd2_requested\tload\n' > "$OUT"
loop() {
  local d=$1
  for i in $(seq "$N"); do
    git init -q "$d/r$i" && cd "$d/r$i" && echo "$i" > a && git add a && git -c user.name=x -c user.email=x@x commit -qm a \
      && git branch b && git update-ref refs/l7r/x HEAD && echo y >> a && git -c user.name=x -c user.email=x@x commit -qam b \
      && git status --short > /dev/null; cd "$d"
  done
}
for r in $(seq "$R"); do
  for setting in default fsync-none; do
    d=$S/git-$setting-$r; rm -rf "$d"; mkdir -p "$d"
    if [ $setting = fsync-none ]; then export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsync GIT_CONFIG_VALUE_0=none; else unset GIT_CONFIG_COUNT GIT_CONFIG_KEY_0 GIT_CONFIG_VALUE_0; fi
    l=$(cut -d' ' -f1 /proc/loadavg); q0=$(req); t0=$(date +%s.%N)
    ( loop "$d" )
    t1=$(date +%s.%N); q1=$(req)
    printf '%s\t%s\t%.2f\t%s\t%s\n' $setting $r "$(echo "$t1-$t0" | bc)" $((q1-q0)) "$l" >> "$OUT"
    rm -rf "$d"
  done
done
