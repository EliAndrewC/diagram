#!/usr/bin/env bash
# land-alone.sh <feature> "<T1 [T2 ...]>" - A TASK LANDS ON ITS OWN (feature 451 T88). `make land` runs this when work is uncommitted in
# the clone (`rust/gate/crates/land/src/land/alone.rs`): the landing runs whole - `make land` again, every refusal and gate of it - in the
# clone's persistent landing worktree, checked out at the clone's HEAD (the task's own commit on the last landed tip), apart from the
# other tasks' unfinished work; then the clone takes the landed tip, its uncommitted work kept.
#
# WHY (measured 2026-11-21, T88's plan section): builders ran three at once 26% of the night's 580 minutes because a landing refused any
# uncommitted file, so tasks landed in batches. Of the three ways: a gate in the clone holds every other builder's writes while it runs
# (gate_write_hooks; 1.12 edits a builder-minute, a 31 s median gate) and judges their half-done files; a set-aside of those files takes
# them from under builders still editing them; judging the task's files alone pushes a tree nobody judged. The worktree's cost: its gate
# reuses the clone's kept results (the keys are the files' contents: a fresh worktree's `make static` 114 s with them, 2,321 s without),
# its own target directory (~/.cache/l7r-cargo-target/<clone>-land) built once and kept, and its disk.
#
# Steps, each refusing with what to do: (1) the landing tasks' own files still uncommitted - an edit line filed under the task names them
# - refused, named; files no task's edit names stay in the clone, listed, not landed; (2) one landing alone at a time (a lock); (3) the
# worktree created, or reset to the clone's HEAD (it is the tool's: nobody's work lives there); (4) the clone's kept check results and
# suite results seeded where newer (`cp -u`); (5) the landing in the worktree (`L7R_LAND_ALONE=1`: its tree is the landing, its `end` line
# its own); (6) the clone takes the landed tip: HEAD moved, each changed file the clone holds no work in written
# from the tip, each one it does merged three ways with its uncommitted edit kept on top; a conflict moves nothing and says so.
# Exit: the landing's own code (0 landed, 3 landed with other sessions' edits merged, 2 refused), 6 refused before it ran (the clone's
# landing writes that one's `end` line and exits 2), 4 landed but the clone could not take the tip (it says how to).
set -u
F=${1:?usage: land-alone.sh <feature> "<tasks>"}
T=${2:?usage: land-alone.sh <feature> "<tasks>"}
ROOT=$(git rev-parse --show-toplevel) || exit 2
COMMON=$(git -C "$ROOT" rev-parse --path-format=absolute --git-common-dir) || exit 2
WT=${LAND_ALONE_TREE:-$(dirname "$ROOT")/$(basename "$ROOT")-land}
MAKE=${LAND_ALONE_MAKE:-make}
say() { printf 'land-alone: %s\n' "$*"; }
die() { printf 'land-alone: refused - nothing landed: %s\n' "$*" >&2; exit 6; }
t0=${EPOCHREALTIME/,/.}
lap() { local t=${EPOCHREALTIME/,/.}; awk -v a="$t0" -v b="$t" 'BEGIN { printf "%.1f", b - a }'; t0=$t; }

# (1) the landing tasks' own files: those an edit line filed under one of them names, newer than the file's last commit
split=$(python3 -I - "$ROOT" "${L7R_EVENTS_DIR:-$COMMON/l7r-events}" "$F" "$T" <<'PY'
import datetime, glob, json, os, subprocess, sys, time
root, events, feature, tasks = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].replace(',', ' ').split()
git = lambda *a: subprocess.run(['git', '-C', root, *a], capture_output=True, text=True, check=True).stdout
dirty, recs, i = set(), git('status', '--porcelain=v1', '-z', '-uall').split('\0'), 0
while i < len(recs):
    r, i = recs[i], i + 1
    if len(r) > 3:
        dirty.add(r[3:])
        i += r[0] in 'RC'
since, last, at = time.time() - 7 * 86400, {}, 0
for l in git('log', '--since=7.days', '--format=@%ct', '--name-only').splitlines():
    if l.startswith('@'):
        at = int(l[1:])
    elif l:
        last.setdefault(l, at)
pre, own, named = root.rstrip('/') + '/', set(), set()
for p in sorted(glob.glob(os.path.join(events, '*.jsonl'))):
    stem = os.path.basename(p)[:-6]
    for l in open(p, errors='replace'):
        if '"PostToolUse"' not in l or '"cat":"edit"' not in l:
            continue
        try:
            d = json.loads(l)
        except ValueError:
            continue
        rel = d.get('path', '')[len(pre):] if d.get('path', '').startswith(pre) else ''
        if d.get('fallback') or not d.get('task') or rel not in dirty:
            continue
        if datetime.datetime.fromisoformat(d['t'].replace('Z', '+00:00')).timestamp() < last.get(rel, since):
            continue
        named.add(rel)
        if d['task'] in tasks and (stem == feature or stem.startswith(feature + '-')):
            own.add(rel)
for r in sorted(own):
    print('own\t' + r)
for r in sorted(dirty - named):
    print('unnamed\t' + r)
PY
) || die "the event log could not be read (above)"
own=$(printf '%s\n' "$split" | sed -n 's/^own\t//p')
[ -z "$own" ] || die "$T's own edits are uncommitted - commit them, then land again: git -C $ROOT commit -m \"<what>\" -- $(printf '%s ' $own)"
unnamed=$(printf '%s\n' "$split" | sed -n 's/^unnamed\t//p')
[ -z "$unnamed" ] || say "left uncommitted in the clone, not landed (no task's edit names them; a shell write is named by none): $(printf '%s ' $unnamed | cut -c1-600)"

# (2) one landing alone at a time
exec 9>"$COMMON/land-alone.lock"
flock -n 9 || die "another landing alone holds $COMMON/land-alone.lock - land this after it"

# (3) the worktree at the clone's HEAD
head=$(git -C "$ROOT" rev-parse HEAD) || exit 2
if [ -e "$WT/.git" ]; then
  git -C "$WT" reset -q --hard && git -C "$WT" clean -fdq && git -C "$WT" checkout -q --detach "$head" \
    || die "the landing worktree $WT could not be moved to $head (above)"
else
  git -C "$ROOT" worktree add -q --detach "$WT" "$head" || die "the landing worktree $WT could not be added (above)"
fi
say "worktree $WT at ${head:0:10} ($(lap) s)"

# (4) the clone's kept results, where newer: a crate's or suite's result is keyed by its inputs' contents, so the clone's builders'
# closing checks on the task's own files serve the landing (measured 2026-11-21: every crate's lint, test, format and dead reused)
gd=$(git -C "$WT" rev-parse --absolute-git-dir) || exit 2
for d in rust-checks hooks-test; do
  [ -d "$COMMON/$d" ] && mkdir -p "$gd/$d" && cp -a -u "$COMMON/$d/." "$gd/$d/"
done
[ -f "$COMMON/approach-owed.json" ] && cp -a "$COMMON/approach-owed.json" "$gd/"
say "kept results seeded ($(lap) s)"

# (5) the landing, whole, in the worktree
( cd "$WT" && L7R_LAND_ALONE=1 SYNC_BACKUP=off $MAKE --no-print-directory land F="$F" T="$T" NOTE="${LAND_NOTE:-}" \
    BOXES="${LAND_BOXES:-}" COVER_OK="${COVER_OK:-}" )
rc=$?
say "the landing in the worktree exited $rc ($(lap) s)"
[ "$rc" = 0 ] || [ "$rc" = 3 ] || exit "$rc"

# (6) the clone takes the landed tip
tip=$(git -C "$WT" rev-parse HEAD) || exit 4
if python3 -I - "$ROOT" "$tip" <<'PY'
import os, subprocess, sys
root, tip = sys.argv[1:3]
def git(*a, inp=None, ok=(0,)):
    r = subprocess.run(['git', '-C', root, *a], capture_output=True, input=inp)
    if r.returncode not in ok:
        sys.exit(f"land-alone: git {' '.join(a)}: {r.stderr.decode(errors='replace').strip()}")
    return r
old = git('rev-parse', 'HEAD').stdout.decode().strip()
# the tip, or - the clone committed since the landing began - a merge of the two, made without touching the tree
if git('merge-base', '--is-ancestor', old, tip, ok=(0, 1)).returncode == 0:
    new = tip
else:
    r = git('merge-tree', '--write-tree', old, tip, ok=(0, 1))
    if r.returncode:
        sys.exit('land-alone: the clone\'s commits since the landing began conflict with the landed tip')
    tree = r.stdout.decode().split('\n')[0]
    new = git('commit-tree', tree, '-p', old, '-p', tip, '-m', f'Merge the landed {tip[:10]} into the clone (land-alone, 451 T88)').stdout.decode().strip()
changed = [p for p in git('diff', '--no-renames', '--name-only', '-z', old, new).stdout.decode().split('\0') if p]
recs, dirty, i = git('status', '--porcelain=v1', '-z', '-uall').stdout.decode().split('\0'), set(), 0
while i < len(recs):
    r, i = recs[i], i + 1
    if len(r) > 3:
        dirty.add(r[3:])
        i += r[0] in 'RC'
show = lambda c, p: git('show', f'{c}:{p}', ok=(0, 128)).stdout
here = lambda p: open(os.path.join(root, p), 'rb').read() if os.path.isfile(os.path.join(root, p)) else b''
def merged(p, ours):
    tmp = [os.path.join(root, '.git', f'land-alone-{k}') for k in ('ours', 'base', 'theirs')]
    for t, b in zip(tmp, (ours, show(old, p), show(new, p))):
        open(t, 'wb').write(b)
    r = subprocess.run(['git', 'merge-file', '-p', *tmp], capture_output=True)
    for t in tmp:
        os.remove(t)
    if r.returncode:
        sys.exit(f'land-alone: {p} - the landing\'s change and the clone\'s uncommitted edit conflict')
    return r.stdout
# every merge first, so a conflict moves nothing
held = {p: (here(p), merged(p, here(p))) for p in changed if p in dirty}
git('update-ref', '-m', f'land-alone: take {new[:10]}', 'HEAD', new, old)
if changed:
    git('reset', '-q', '--', *changed)
gone = [p for p in changed if p not in held and git('cat-file', '-e', f'{new}:{p}', ok=(0, 1, 128)).returncode]
for p in gone:
    if os.path.lexists(os.path.join(root, p)):
        os.remove(os.path.join(root, p))
put = [p for p in changed if p not in held and p not in gone]
if put:
    git('checkout-index', '-f', '--', *put)
for p, (ours, out) in held.items():
    if here(p) != ours:  # a builder wrote it since it was read: merged again from what it holds now
        out = merged(p, here(p))
    os.makedirs(os.path.dirname(os.path.join(root, p)) or root, exist_ok=True)
    t = os.path.join(root, p + '.land-alone')
    open(t, 'wb').write(out)
    os.replace(t, os.path.join(root, p))
print(f'land-alone: {len(changed)} file(s) moved to {new[:10]}, {len(held)} of them merged with the clone\'s uncommitted edits')
PY
then
  say "the clone took ${tip:0:10}, its uncommitted work kept ($(lap) s)"
  exit "$rc"
fi
printf 'land-alone: landed %s; the clone could not take %s (above) - its uncommitted work is untouched: once it is committed, git -C %s merge %s\n' "$T" "${tip:0:10}" "$ROOT" "${tip:0:10}" >&2
exit 4
