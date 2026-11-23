#!/usr/bin/env bash
# Tests for scripts/gates/review-tree.sh (`make verify T=<task(s)>`, feature 451 T164): the paired gate and the review snapshot built in
# a worktree at a temporary commit of the bundle's own files on HEAD - another builder's uncommitted file stays out, the clone's HEAD and
# index are untouched - the gate's record running, then green or red at the review tree's key, and the tree left alone while its gate
# runs or its units wait for their verdicts (REVIEW_TREE_OK="<why>" resets it), and a unit still hidden behind a map not current
# refused rather than dropped.
# Run: tests/hooks/test-review-tree.sh   (exit 0 = all green)
#
# The gate tools and make are stubs (REVIEW_TREE_GATE, REVIEW_TREE_MAKE): `reviews owed` answers from the fixture's files, `make done`
# waits for a release file where the fixture holds one and exits as it says; land-alone's attribution is the real one, read from the
# real scripts/land-alone.sh the fixture clone carries.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$HERE/../.."
PASS=0; FAIL=0
T=$(mktemp -d); trap 'rm -rf "$T"; git -C "$T/clone" worktree prune 2>/dev/null' EXIT
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }
unset REVIEW_TREE_OK

S=$T/stub; mkdir -p "$S"
cat > "$S/gate" <<'EOF'
#!/usr/bin/env bash
# the stub l7r-gate.sh: owed from $STUB/owed, $STUB/why, $STUB/undrawn; the key from $STUB/key; the snapshot a line a unit
d=$STUB
case "$1 $2" in
  "reviews owed")
    case "${5:-}${4:-}" in
      --check-declared*) exit 0 ;;
      --undrawn*) cat "$d/undrawn" 2>/dev/null; exit 0 ;;
      --why*) cat "$d/why" 2>/dev/null || echo "why"; exit 0 ;;
    esac
    cat "$d/owed" 2>/dev/null; exit 0 ;;
  "reviews snapshot")
    case " $* " in *" --stale-renders "*) exit 0 ;; esac
    echo "$*" > "$d/snapshot-args"; echo "snapshot taken"; exit 0 ;;
  "delta key") cat "$d/key"; exit 0 ;;
  "log bypass") echo "$*" >> "$d/bypasses"; exit 0 ;;
esac
echo "stub gate: unexpected $*" >&2; exit 9
EOF
cat > "$S/make" <<'EOF'
#!/usr/bin/env bash
# the stub make: `make --no-print-directory <target> [MAP=...]`
d=$STUB
case $2 in
  map) echo "${3#MAP=}" >> "$d/drawn"; exit 0 ;;
  done)
    pwd > "$d/done-in"
    if [ -e "$d/done.hold" ]; then for _ in $(seq 1 400); do [ -e "$d/release" ] && break; sleep 0.05; done; fi
    exit "$(cat "$d/done.rc" 2>/dev/null || echo 0)" ;;
esac
exit 9
EOF
chmod +x "$S/gate" "$S/make"

C=$T/clone; WT=$T/clone-review; EV=$T/events
mkdir -p "$C/scripts/gates" "$EV"
git -C "$C" init -q && git -C "$C" config user.email t@t && git -C "$C" config user.name T
cp "$REPO/scripts/land-alone.sh" "$C/scripts/land-alone.sh"
cp "$REPO/scripts/gates/review-tree.sh" "$C/scripts/gates/review-tree.sh"
printf 'a0\n' > "$C/a.txt"; printf 'b0\n' > "$C/b.txt"; printf 'gone\n' > "$C/c.txt"
git -C "$C" add -A && git -C "$C" commit -qm base
HEAD0=$(git -C "$C" rev-parse HEAD)
sleep 1  # an edit line older than its file's last commit claims nothing: the lines below are after it
now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
# the bundle T1 edited a.txt and removed c.txt; another builder's T2 edited b.txt, still half done
printf 'a1 the bundle\n' > "$C/a.txt"; printf 'b1 half done\n' > "$C/b.txt"; rm "$C/c.txt"
{
  printf '{"t":"%s","ev":"PostToolUse","cat":"edit","task":"T1","path":"%s/a.txt"}\n' "$now" "$C"
  printf '{"t":"%s","ev":"PostToolUse","task":"T1","writes":["%s/c.txt"]}\n' "$now" "$C"
  printf '{"t":"%s","ev":"PostToolUse","cat":"edit","task":"T2","path":"%s/b.txt"}\n' "$now" "$C"
} > "$EV/900-x.jsonl"
STUB=$S; export STUB
echo K1 > "$S/key"
run() { ( cd "$C" && L7R_EVENTS_DIR=$EV REVIEW_TREE=$WT REVIEW_TREE_GATE=$S/gate REVIEW_TREE_MAKE=$S/make \
  bash scripts/gates/review-tree.sh 900-x "T1" "$@" ) > "$T/out" 2>&1; echo $?; }
gate_rec() { python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get(sys.argv[2]))' "$C/.git/review-trees/$1.json" "$2"; }
wait_state() { for _ in $(seq 1 200); do [ "$(gate_rec "$1" state)" != running ] && return; sleep 0.05; done; }

echo "1. the review commit holds the bundle's files alone, the clone untouched"
printf 'building-review--c\n' > "$S/owed"
rc=$(run)
commit=$(cat "$C/.git/review-trees/current" 2>/dev/null)
[ "$rc" = 0 ] && [ -n "$commit" ] && ok "started (commit ${commit:0:10})" || { no "did not start" "$(cat "$T/out")"; }
[ "$(git -C "$C" show "$commit:a.txt" 2>/dev/null)" = "a1 the bundle" ] && ok "the bundle's edit is in it" || no "the bundle's edit is missing"
[ "$(git -C "$C" show "$commit:b.txt" 2>/dev/null)" = "b0" ] && ok "another builder's half-done file is not" || no "another builder's file leaked in"
git -C "$C" cat-file -e "$commit:c.txt" 2>/dev/null && no "the bundle's removal was not taken" || ok "the bundle's removal is taken"
[ "$(git -C "$C" rev-parse "$commit^")" = "$HEAD0" ] && ok "its parent is HEAD" || no "its parent is not HEAD"
[ "$(git -C "$C" rev-parse HEAD)" = "$HEAD0" ] && [ -z "$(git -C "$C" diff --cached --name-only)" ] \
  && [ "$(cat "$C/b.txt")" = "b1 half done" ] && ok "the clone's HEAD, index and files untouched" || no "the clone was moved"
[ "$(git -C "$WT" rev-parse HEAD)" = "$commit" ] && [ "$(cat "$WT/a.txt")" = "a1 the bundle" ] && ok "the review tree is at it" || no "the review tree is elsewhere"
grep -q -- "--state $C --commit $commit --key K1" "$S/snapshot-args" 2>/dev/null && grep -q "building-review--c" "$S/snapshot-args" \
  && ok "the snapshot is read in the review tree and kept in the clone" || no "the snapshot's arguments" "$(cat "$S/snapshot-args" 2>/dev/null)"
grep -q "other uncommitted files left out" "$T/out" && ok "what it left out is said" || no "no word of what it left out"

echo "2. the gate's record: running, then green at the review tree's key; the log is verify-wait's"
wait_state "$commit"
[ "$(gate_rec "$commit" state)" = green ] && [ "$(gate_rec "$commit" key)" = K1 ] && ok "green at K1" || no "the record" "$(cat "$C/.git/review-trees/$commit.json")"
[ "$(cat "$S/done-in")" = "$(cd "$WT" && pwd -P)" ] || [ "$(cat "$S/done-in")" = "$WT" ] && ok "the gate ran in the review tree" || no "the gate ran in $(cat "$S/done-in")"
[ "$(readlink "$C/.git/verify-gate.log")" = "$C/.git/review-trees/$commit.log" ] && grep -q "exited 0: green" "$C/.git/review-trees/$commit.log" \
  && ok "verify-gate.log links to its log" || no "the log link"
[ "$(gate_rec "$commit" units)" = "['building-review--c']" ] && ok "its units are recorded" || no "its units" "$(gate_rec "$commit" units)"

echo "3. the tree is left alone while its units wait for their verdicts, and while its gate runs"
rc=$(run)
[ "$rc" = 2 ] && grep -q "units have no verdict at its key yet: building-review--c" "$T/out" && ok "a reset under waiting units is refused" || no "not refused" "$(cat "$T/out")"
mkdir -p "$C/.git/review-verdicts"; printf '{"engine_key": "K1"}' > "$C/.git/review-verdicts/building-review--c.json"
: > "$S/done.hold"; echo K2 > "$S/key"
rc=$(run)
second=$(cat "$C/.git/review-trees/current")
[ "$rc" = 0 ] && [ "$second" != "$commit" ] || [ "$rc" = 0 ] && ok "a verdict at its key frees it" || no "not freed" "$(cat "$T/out")"
for _ in $(seq 1 100); do [ "$(gate_rec "$second" pid)" != None ] && break; sleep 0.05; done
rc=$(run)
[ "$rc" = 2 ] && grep -q "is still running (pid" "$T/out" && ok "a reset under a running gate is refused" || no "not refused while running" "$(cat "$T/out")"
rc=$(REVIEW_TREE_OK="one" run)
[ "$rc" = 2 ] && grep -q "two words or more" "$T/out" && ok "a one-word REVIEW_TREE_OK is refused" || no "a bare reason passed" "$(cat "$T/out")"
touch "$S/release"; wait_state "$second"; rm -f "$S/done.hold" "$S/release"

echo "4. a red gate is recorded red; REVIEW_TREE_OK resets a tree in use"
echo 1 > "$S/done.rc"
rc=$(REVIEW_TREE_OK="the GM asked for this map first" run)
third=$(cat "$C/.git/review-trees/current")
wait_state "$third"
[ "$rc" = 0 ] && grep -q "REVIEW_TREE_OK" "$T/out" && grep -q "the GM asked" "$S/bypasses" && ok "the escape resets it, recorded" || no "the escape" "$(cat "$T/out")"
[ "$(gate_rec "$third" state)" = red ] && ok "a red gate reads red" || no "a red gate read $(gate_rec "$third" state)"
rm -f "$S/done.rc"

echo "5. every map the cache does not serve is drawn first; a unit still hidden is refused, nothing snapshotted"
printf 'map\tpool/compounds/c\n' > "$S/undrawn"; : > "$S/owed"; rm -f "$S/drawn" "$S/snapshot-args"
rc=$(REVIEW_TREE_OK="the red gate's units are moot" run)
grep -qx "pool/compounds/c" "$S/drawn" && ok "the undrawn map is drawn in the review tree" || no "not drawn"
grep -q "NO REVIEW CHECK OWED" "$T/out" && [ ! -e "$S/snapshot-args" ] && ok "none owed: the gate runs alone" || no "none owed" "$(cat "$T/out")"
wait_state "$(cat "$C/.git/review-trees/current")"
printf 'building-review--c\n' > "$S/owed"; echo "x | PROBLEMS: pool/compounds/c: not current; the units its new elements owe are HIDDEN until it is drawn" > "$S/why"
rc=$(REVIEW_TREE_OK="a test of the hidden refusal" run)
[ "$rc" = 2 ] && grep -q "UNITS HIDDEN" "$T/out" && [ ! -e "$S/snapshot-args" ] && ok "hidden units refused, nothing snapshotted" || no "hidden units" "$(cat "$T/out")"

echo
echo "review-tree: $PASS passed, $FAIL failed"
[ "$FAIL" = 0 ]
