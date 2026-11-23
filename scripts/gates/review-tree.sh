#!/usr/bin/env bash
# TOOL_RECORD: each run's record is .git/review-trees/<commit>.json (its gate's pid, state and exit) beside its log, and make verify's run is in the event log (451 T164)
# review-tree.sh <feature> "<T1 [T2 ...]>" [extra paths...] - A MAP REVIEW'S PAIRED GATE JUDGED ON A SNAPSHOT OF THE BUNDLE'S OWN WORK
# (feature 451 T164). `make verify T=<task(s)>` runs this: the gate (`make done`) and the review snapshot build in the clone's review
# tree, a worktree at a commit of the bundle's own files on HEAD, as land-alone's landing worktree does; the snapshot's units are judged
# by that gate's record (`rust/gate/crates/reviews/src/reviews/prereq/tree.rs`), never the clone's green stamp.
#
# WHY (observed 2026-11-22): with three builders in one clone the 449 T312 bundle's verify gate went red or "tree moved" four times on
# other builders' half-done edits, seven of its ten finished verdicts were rewritten NOT-REVIEWABLE because a page session and a
# test-file edit wrote into the clone while the reviews ran, and earlier the T289 bundle's reviews waited hours on a Mode A binary another
# bundle's edit had staled, which also dropped its new-element units. The gate judged the shared working tree; this judges a commit.
#
# THE COMMIT: a temporary one of the bundle's files alone, never on a branch, HEAD and the clone's index untouched (commit-on-CLEAR,
# 451 T152, is not built). Its files: HEAD's tree with each file a line filed under one of the tasks names (land-alone's own `split`,
# read from its script so the attribution has one copy) taken from the clone's working tree, and any extra path named (`FILES=`). A file
# no task's line names - a make target's write, a generator's - stays out, listed: the review tree redraws the maps itself.
#
# Steps, each refusing with what to do: (1) one review tree setup at a time (a lock), and none while the tree's last gate runs or its
# units wait for their verdicts (escape REVIEW_TREE_OK="<why>"); (2) the bundle's files; (3) the temporary commit; (4) the worktree
# <clone>-review, added or reset to it (it is the tool's: nobody's work lives there; its own cargo target directory, built once, kept);
# (5) the clone's kept check results seeded where newer (`cp -u`; never its generation cache, which a tree's own engine build ids miss); (6) every live map the cache does not serve
# drawn there (`reviews owed --undrawn`, so no unit hides behind a stale engine), the engine key read, the owed units read and
# snapshotted into the clone's `.git/review-snapshot/` with their `tree.json`; (7) the gate started detached in the review tree, its
# record `.git/review-trees/<commit>.json` (`running`, then `green` or `red`), its log what `.git/verify-gate.log` links to.
# Exit 0 started, 2 refused.
set -u
F=${1:?usage: review-tree.sh <feature> "<tasks>" [paths]}
T=${2:?usage: review-tree.sh <feature> "<tasks>" [paths]}
shift 2
EXTRA=("$@")
ROOT=$(git rev-parse --show-toplevel) || exit 2
COMMON=$(git -C "$ROOT" rev-parse --path-format=absolute --git-common-dir) || exit 2
WT=${REVIEW_TREE:-$(dirname "$ROOT")/$(basename "$ROOT")-review}
MAKE=${REVIEW_TREE_MAKE:-make}
GATE=${REVIEW_TREE_GATE:-$ROOT/scripts/gates/l7r-gate.sh}
RECS=$COMMON/review-trees
say() { printf 'review-tree: %s\n' "$*"; }
die() { printf 'review-tree: refused - %s\n' "$*" >&2; exit 2; }
t0=${EPOCHREALTIME/,/.}
lap() { local t=${EPOCHREALTIME/,/.}; awk -v a="$t0" -v b="$t" 'BEGIN { printf "%.1f", b - a }'; t0=$t; }
mkdir -p "$RECS" || exit 2

# A gate record, written whole (`rec <file> key=value ...`, a value read as JSON where it parses).
rec() {
  python3 -I - "$@" <<'PY'
import json, os, sys
path, pairs = sys.argv[1], sys.argv[2:]
d = {}
if os.path.exists(path):
    try:
        d = json.load(open(path))
    except ValueError:
        d = {}
for p in pairs:
    k, _, v = p.partition('=')
    try:
        d[k] = json.loads(v)
    except ValueError:
        d[k] = v
tmp = path + '.tmp'
json.dump(d, open(tmp, 'w'))
os.replace(tmp, path)
PY
}

# (1) one setup at a time, and the last tree left alone while its gate runs or its units wait for their verdicts
exec 9>"$COMMON/review-tree.lock"
flock -n 9 || die "another review tree is being set up ($COMMON/review-tree.lock) - run make verify again once it has started"
if [ -f "$RECS/current" ]; then
  busy=$(python3 -I - "$RECS/$(cat "$RECS/current").json" "$ROOT/.git/review-verdicts" "$GATE" "$ROOT" <<'PY'
import json, os, subprocess, sys
try:
    d = json.load(open(sys.argv[1]))
except (OSError, ValueError):
    sys.exit(0)
pid = d.get('pid') or 0
if d.get('state') == 'running' and pid and os.path.exists(f'/proc/{pid}'):
    print(f"its gate for {d.get('tasks')} is still running (pid {pid}) - wait for it: make verify-wait, run_in_background")
    sys.exit(0)
def carried(u):
    # 451 T176: a PASS or NEEDS-WORK at another key still answers while its sheet's drawing and notes hash as the review read them
    # (the gate's `reviews prereq answered`, which the checkpoint and the push's review gate read alike)
    ask = [sys.argv[3], 'reviews', 'prereq', 'answered', '--clone', sys.argv[4], '--unit', u, '--key', d.get('key') or '']
    return subprocess.run(ask, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
waiting = []
for u in (d.get('units') or []) if d.get('state') == 'green' else []:
    try:
        v = json.load(open(os.path.join(sys.argv[2], u + '.json')))
    except (OSError, ValueError):
        v = {}
    if v.get('engine_key') != d.get('key') and not (v and carried(u)):
        waiting.append(u)
if waiting:
    print(f"{d.get('tasks')}'s units have no verdict at its key yet: {' '.join(waiting)} - dispatch them, or wait for them")
PY
)
  if [ -n "$busy" ]; then
    if [ -n "${REVIEW_TREE_OK:-}" ]; then
      [ "$(printf '%s' "$REVIEW_TREE_OK" | wc -w)" -ge 2 ] || die "REVIEW_TREE_OK needs a reason of two words or more"
      say "REVIEW_TREE_OK ($REVIEW_TREE_OK): resetting the review tree though $busy"
      "$GATE" log bypass review-tree "$REVIEW_TREE_OK" >/dev/null 2>&1 || true
    else
      die "the review tree $WT is in use: $busy. A reset under it would move what its reviewers read; REVIEW_TREE_OK=\"<why>\" resets it anyway"
    fi
  fi
fi

# (2) the bundle's own files: land-alone's attribution, read from its script (one copy of the rule)
lib=$(sed -n "/^read -r -d '' PYLIB <<'PY'\$/,/^PY\$/p" "$ROOT/scripts/land-alone.sh" | sed '1d;$d')
[ -n "$lib" ] || die "scripts/land-alone.sh holds no PYLIB to read the attribution from"
split=$(python3 -I -c "$lib" split "$ROOT" "${L7R_EVENTS_DIR:-$COMMON/l7r-events}" "$F" "$T") || die "the event log could not be read (above)"
own=$(printf '%s\n' "$split" | sed -n 's/^own\t//p')
for p in "${EXTRA[@]}"; do own=$(printf '%s\n%s' "$own" "${p#./}"); done
own=$(printf '%s\n' "$own" | sed '/^$/d' | sort -u)
left=$(printf '%s\n' "$split" | sed -n 's/^\(unnamed\|other\)\t//p' | wc -l)
say "$T's own files: $(printf '%s\n' "$own" | sed '/^$/d' | wc -l) (the clone's $left other uncommitted files left out: another task's, or no task's - a make target's or a generator's write, which FILES=\"<paths>\" adds)"

# (3) the temporary commit: HEAD's tree with the bundle's files as the clone holds them
head=$(git -C "$ROOT" rev-parse HEAD) || exit 2
idx=$(mktemp "${TMPDIR:-/tmp}/review-tree-index.XXXXXX") || exit 2
trap 'rm -f "$idx"' EXIT
export GIT_INDEX_FILE=$idx
git -C "$ROOT" read-tree "$head" || die "HEAD's tree could not be read"
while IFS= read -r f; do
  [ -n "$f" ] || continue
  if [ -e "$ROOT/$f" ] || [ -L "$ROOT/$f" ]; then
    git -C "$ROOT" update-index --add -- "$f" || die "$f could not be taken into the review commit"
  else
    git -C "$ROOT" update-index --force-remove -- "$f" || die "$f's removal could not be taken"
  fi
done <<<"$own"
tree=$(git -C "$ROOT" write-tree) || die "the review commit's tree could not be written"
unset GIT_INDEX_FILE
commit=$(git -C "$ROOT" commit-tree "$tree" -p "$head" -m "review tree: $F $T (451 T164, never landed)") || die "the review commit could not be written"
say "commit ${commit:0:10}: $T's files on HEAD ${head:0:10} ($(lap) s)"

# (4) the review tree at that commit
if [ -e "$WT/.git" ]; then
  git -C "$WT" reset -q --hard && git -C "$WT" clean -fdq -e .gencache && git -C "$WT" checkout -q --detach "$commit" \
    || die "the review tree $WT could not be moved to $commit (above)"
else
  git -C "$ROOT" worktree add -q --detach "$WT" "$commit" || die "the review tree $WT could not be added (above)"
fi
say "worktree $WT at ${commit:0:10} ($(lap) s)"

# (5) the clone's kept results, where newer: each is keyed by its inputs' contents, so the clone's runs on the same files serve here
gd=$(git -C "$WT" rev-parse --absolute-git-dir) || exit 2
for d in rust-checks hooks-test; do
  [ -d "$COMMON/$d" ] && mkdir -p "$gd/$d" && cp -a -u "$COMMON/$d/." "$gd/$d/"
done
# NOT the clone's generation cache (measured 2026-11-22): an entry is keyed by its engine binary's build id, and each tree's binary embeds its
# own source path (`strings tool/hamlet` names diagram-backlog-review/rust/phases/...), so the clone's 6.2 GB never served a map here; it cost
# 19.2 s a run and its disk. The review tree's own .gencache, kept across resets (`clean -e .gencache`), serves it: the second run drew 1 map
# of the first's 7, the third none. Don't seed it.
say "kept results seeded ($(lap) s)"

# (6) every map drawn, the key, the owed units and their snapshot - all in the review tree
cd "$WT" || exit 2
# the review tree's own launcher: its tools are built from the snapshot's sources, never a builder's half-done edit in the clone
GATE=${REVIEW_TREE_GATE:-$WT/scripts/gates/l7r-gate.sh}
# the bundle's own started task, carried in (451 T166): the clone's one mark is any builder's last `make task-start` or `make set-down`,
# and read here it named another feature's task, or none, under 449 T328's two runs (measured 2026-11-23); a gate built before reads
# the mark as before
undeclared=$(L7R_VERIFY_STARTED="$F $T" "$GATE" reviews owed --root "$WT" --check-declared)
[ -z "$undeclared" ] || printf '\n\033[1mOCCASIONS NOT DECLARED\033[0m: %s\n' "$undeclared"
for at in $("$GATE" reviews owed --root "$WT" --undrawn | cut -f2); do
  say "drawing $at (the generation cache does not serve it as it stands)"
  $MAKE --no-print-directory map MAP="$at" >/dev/null || die "make map MAP=$at failed in the review tree - run it there by hand (cd $WT), then make verify again"
done
say "maps current ($(lap) s)"
key=$("$GATE" delta key worktree) || die "the review tree's engine key could not be read"
printf 'engine key %s (the review tree)\n' "${key:0:12}"
maps=$("$GATE" reviews owed --root "$WT" | tr '\n' ' ' | sed 's/ $//')
why=$("$GATE" reviews owed --root "$WT" --why)
case $why in *"HIDES until"* | *"HIDDEN until"*)
  printf '\n\033[1mUNITS HIDDEN\033[0m: %s\n' "$why"
  die "a map in the review tree is still not current, so the units it owes are unknown (above) - nothing snapshotted" ;;
esac
units=$(printf '%s' "$maps" | python3 -I -c 'import json,sys; print(json.dumps(sys.stdin.read().split()))')
if [ -z "$maps" ]; then
  printf '\n\033[1mNO REVIEW CHECK OWED\033[0m: %s (feature 294: a check is owed on its occasion, never because a manifest moved). The gate runs alone; the GM looks at the map.\n' "$why"
else
  mirror=""; case "$ROOT" in */.clones/*) mirror="${ROOT%%/.clones/*}";; esac
  # a frozen exhibit no engine draws, its render missing (449 T289's rule, kept from the recipe this replaced)
  # shellcheck disable=SC2086 # the units are slugs, one a word
  for gen in $("$GATE" reviews snapshot --root "$WT" --stale-renders $maps); do
    case $gen in sheet:*) svg=${gen#sheet:}
      die "$svg has no generator and no render - make sheet-render SHEET=$svg OUT=${svg%.svg}.png in the clone, then make verify again with FILES=${svg%.svg}.png" ;;
    esac
    $MAKE --no-print-directory map MAP="$gen" >/dev/null || die "make map MAP=$gen failed in the review tree (cd $WT)"
  done
  # shellcheck disable=SC2086 # the units are slugs, one a word
  snap=$("$GATE" reviews snapshot --root "$WT" --state "$ROOT" --commit "$commit" --key "$key" ${mirror:+--mirror "$mirror"} $maps) \
    || die "the snapshot could not be taken (above)"
  n=$(printf '%s\n' $maps | wc -l)
  printf 'owed: %s\n%s\n' "$why" "$snap"
  # A VERDICT THAT STANDS IS NO ROUND (451 T199): a unit whose last PASS or NEEDS-WORK is carried to its sheet as just snapshotted, its
  # open findings only nitpick, outside or confirmation, owes no dispatch - 4 of 2026-11-23's 60 later building-review rounds were such
  # (`reviews/prereq/stands.rs`); its prompt stays, should the builder judge otherwise.
  # shellcheck disable=SC2086 # the units are slugs, one a word
  for u in $("$GATE" reviews prereq standing --clone "$ROOT" --maps "$maps" 2>/dev/null); do
    printf 'answered: %s - its last verdict stands on this sheet (carried, open findings only nitpick/outside): dispatch none (451 T199)\n' "$u"
    n=$((n - 1))
  done
  # A NITPICK FIXED ON THE SHEET OWES A ROUND OF ITS EDIT ALONE (451 T199): the builder names the fixed nitpicks; the tool refuses an
  # error or questionable one, and writes the change-scoped prompt (`reviews/prereq/scoped.rs`)
  printf 'a unit whose sheet edit fixed ONLY nitpicks of its last verdict: `make review-fixed UNIT=<unit> FINDING="<ids>"`, then dispatch the change-scoped prompt it writes in place of that unit'"'"'s full round (451 T199)\n'
  printf '\n\033[1mWHEN THE GATE IS GREEN, dispatch %s review agent(s), ONE PER UNIT\033[0m - each Agent call is the unit'"'"'s check (its slug begins with it) and takes the contents of its prompt file named above (.git/review-snapshot/<unit>/dispatch.md). Each unit is judged by the review tree'"'"'s gate at %s, not the clone'"'"'s: another builder'"'"'s edit to the clone neither blocks nor voids it (451 T164).\n' "$n" "${commit:0:10}"
fi

# (7) the gate, detached in the review tree; its record and its log
log=$RECS/$commit.log
gate=$RECS/$commit.json
rm -f "$gate"
rec "$gate" commit="$commit" key="$key" tasks="$T" feature="$F" units="$units" tree="$WT" log="$log" state=running
printf '%s\n' "$commit" > "$RECS/current"
ln -sfn "$log" "$ROOT/.git/verify-gate.log"
printf '\nstarting the gate in the review tree, detached, in a log of its own (.git/verify-gate.log links to it): WAIT WITH `make verify-wait`, run_in_background - its exit is the notification.\n\n'
(
  trap '' HUP
  # the runner names itself: the parent writing `$!` after it could overwrite a gate already ended
  rec "$gate" pid="$BASHPID"
  PAIR_OK="started by make verify in the review tree - the review is dispatched in the same turn" $MAKE --no-print-directory done
  rc=$?
  state=red; [ "$rc" = 0 ] && state=green
  rec "$gate" state="$state" exit="$rc"
  printf 'review-tree: the gate at %s exited %s: %s\n' "${commit:0:10}" "$rc" "$state"
) > "$log" 2>&1 9>&- &
exit 0
