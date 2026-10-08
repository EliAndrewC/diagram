#!/usr/bin/env bash
# _layout_carry.sh <tree> - carry what a tree kept at the old project location to the root (feature 329, FR-008).
#
# WHY. Feature 329 moved the project from `` to the repository root with `git mv`. A merge or a
# fast-forward moves TRACKED files only: every gitignored artifact a clone or the mirror had built there - the roll
# cache `.gencache/`, the renders beside each pool map, the built record site, testmon's database, coverage data -
# stays behind at the old place, where nothing reads it. Left there, the first gate after the move runs cold (the roll
# cache alone is about two minutes, `sync-with-main.sh` seed_roll_cache), and 600 MB sits in a directory a session
# might read as live.
#
# WHAT. Only when the tree is on the new layout (`l7r/` tracked at the root) and the old directory still exists: every
# file still there - by then each is untracked or ignored - moves to the same path under the root. Where the root
# already holds that path (9 clones held a `.ruff_cache` at both places on the day), a CACHE's old copy is invalidated:
# deleted, because the root's copy is the one the tools now write and a cache rebuilds on demand. Any other colliding
# file moves beside its twin as `<name>.pre-329` and is reported - never deleted, never overwriting. Bytecode is removed,
# not carried (a stale `__pycache__` dir is an importable namespace package - check-stale-dirs.py). So the old directory
# always goes (FR-008). Idempotent: a second run, or a tree that never had the old layout, does nothing.
#
# Called by sync-with-main.sh after a clone's pull and after the mirror's fast-forward. `--selftest` proves it.
set -uo pipefail

OLD_REL=".claude/skills/""diagram"   # split so the old-layout check does not find this file naming it

carry() {
  local tree="$1" old moved=0 dropped=0 renamed=0 f rel dest
  old="$tree/$OLD_REL"
  [ -d "$old" ] || return 0
  git -C "$tree" ls-files --error-unmatch l7r >/dev/null 2>&1 || return 0   # still on the old layout: nothing to do
  find "$old" -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
  while IFS= read -r -d '' f; do
    rel="${f#"$old"/}"
    dest="$tree/$rel"
    if [ -e "$dest" ] || [ -L "$dest" ]; then
      case "/$rel" in
        */.ruff_cache/*|*/.pytest_cache/*|*/.mypy_cache/*|*/.gencache/*|*/.coverage*|*/.testmondata*)
          rm -f "$f"; dropped=$((dropped + 1)); continue ;;
      esac
      dest="$dest.pre-329"; n=1
      while [ -e "$dest" ] || [ -L "$dest" ]; do n=$((n + 1)); dest="$tree/$rel.pre-329.$n"; done
      renamed=$((renamed + 1))
    fi
    mkdir -p "$(dirname "$dest")" && mv "$f" "$dest" && moved=$((moved + 1))
  done < <(find "$old" \( -type f -o -type l \) -print0)
  find "$old" -depth -type d -empty -delete 2>/dev/null
  rmdir "$tree/.claude/skills" 2>/dev/null || true   # only if the speckit skills are gone too, which they never are
  [ "$((moved + dropped))" -gt 0 ] && echo "layout-carry: moved $moved file(s) from $OLD_REL to the root (feature 329), dropped $dropped stale cache file(s) the root already had"
  [ "$renamed" -gt 0 ] && echo "layout-carry: $renamed file(s) collided with a root file and were kept beside it as <name>.pre-329 - compare and keep one: find $tree -name '*.pre-329'"
  [ -d "$old" ] && echo "layout-carry: $old is still there - see the line above" >&2
  return 0
}

selftest() {
  local t; t="$(mktemp -d)"; trap 'rm -rf "$t"' RETURN
  git -C "$t" init -q && mkdir -p "$t/l7r" && echo x > "$t/l7r/a.py" && git -C "$t" add l7r && git -C "$t" -c user.email=t@t -c user.name=t commit -qm a
  mkdir -p "$t/$OLD_REL/.gencache/r" "$t/$OLD_REL/l7r/__pycache__" "$t/$OLD_REL/pool/h/m"
  echo cache > "$t/$OLD_REL/.gencache/r/k.json"; echo pyc > "$t/$OLD_REL/l7r/__pycache__/a.pyc"
  echo render > "$t/$OLD_REL/pool/h/m/m.svg"; echo old > "$t/$OLD_REL/l7r/a.py"
  carry "$t" >/dev/null
  [ "$(cat "$t/.gencache/r/k.json")" = cache ] || { echo "selftest: the cache was not carried"; return 1; }
  [ "$(cat "$t/pool/h/m/m.svg")" = render ] || { echo "selftest: the render was not carried"; return 1; }
  [ "$(cat "$t/l7r/a.py")" = x ] || { echo "selftest: a root file was overwritten"; return 1; }
  [ "$(cat "$t/l7r/a.py.pre-329")" = old ] || { echo "selftest: the colliding file was not kept beside its twin"; return 1; }
  [ ! -e "$t/l7r/__pycache__" ] || { echo "selftest: bytecode was carried"; return 1; }
  [ ! -e "$t/$OLD_REL" ] || { echo "selftest: the old directory was not removed"; return 1; }
  mkdir -p "$t/$OLD_REL/.ruff_cache" && echo stale > "$t/$OLD_REL/.ruff_cache/x" && mkdir -p "$t/.ruff_cache" && echo live > "$t/.ruff_cache/x"
  carry "$t" >/dev/null
  [ "$(cat "$t/.ruff_cache/x")" = live ] && [ ! -e "$t/$OLD_REL" ] || { echo "selftest: a colliding cache was not invalidated"; return 1; }
  carry "$t" >/dev/null || { echo "selftest: a second run failed"; return 1; }
  echo "layout-carry selftest: ok"
}

case "${1:-}" in
  --selftest) selftest ;;
  "") echo "usage: _layout_carry.sh <tree> | --selftest" >&2; exit 2 ;;
  *) carry "$1" ;;
esac
