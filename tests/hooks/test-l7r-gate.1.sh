#!/usr/bin/env bash
# test-l7r-gate.1.sh - the first shard of l7r-gate.sh's suite (feature 451 T21 split it by its case groups, plan D17): the stamp, the
# wrapper's no-build seam, the run's fresh binary, and the Mode A and hamlet launchers; .2 is the browser and the archive, .3 the embedder.
# Tests for l7r-gate stamp (rust/gate/crates/tree/src/stamp.rs) - the push-time "a green gate saw exactly this code" guard.
# Run: tests/hooks/test-l7r-gate.<k>.sh, k 1 to 3   (exit 0 = all green). Runs under `make hooks-test`, a job a shard.
#
# THE CASE THAT MOTIVATED THIS FILE (2026-08-25): a session ran `make hooks-test` (RED), then
# `git commit; sync-with-main.sh done` chained with ';', and the push LANDED - the only code that
# had changed was under scripts/, which the stamp did not cover. A guard-script change must now
# carry a green `make hooks-test` stamp exactly as engine Python must carry a green `make done`.
set -uo pipefail
# the suite's own builds start incremental: a session that exported CARGO_INCREMENTAL=0 (the work-around before 451 T142)
# would otherwise hand it to every stub, and the stale-unit case's "one retry, incremental" read the session's value
unset CARGO_INCREMENTAL
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAMP="$HERE/../../scripts/gates/l7r-gate.sh"  # the Rust gate (a .py file's id its blob id since 449 T247 deleted codeid.py)
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
FAILED=0
check() { # label expected-rc actual-rc
  if [ "$2" = "$3" ]; then printf 'ok    %s (rc=%s)\n' "$1" "$3"; else printf 'FAIL  %s (expected rc=%s, got rc=%s)\n      out: %s\n' "$1" "$2" "$3" "${OUT:-}"; FAILED=1; fi
}

"$STAMP" stamp --selftest; check "selftest: the hash still bites" 0 $?

# ---- fixture: a repo with a remote main, a clone, and one commit per area -----------------------
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
MAIN=$TMP/main; git init -q -b main "$MAIN"
mkdir -p "$MAIN/scripts/hooks/lib" "$MAIN"
echo 'echo guard' > "$MAIN/scripts/hooks/x-hooks.sh"; echo 'x = 1' > "$MAIN/m.py"; echo doc > "$MAIN/README.md"
git -C "$MAIN" add -A; git -C "$MAIN" commit -qm base
W=$TMP/clone; git clone -q "$MAIN" "$W"

# a docs-only change needs no stamp
echo more >> "$W/README.md"; git -C "$W" commit -qam docs
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "docs-only change: no stamp needed" 0 $?

# a tests-only change needs no stamp either (feature 132 FR-024, the GM's ruling): tests/ is outside the diagram area
mkdir -p "$W/tests"; echo 'def test_x(): pass' > "$W/tests/test_x.py"; git -C "$W" add -A; git -C "$W" commit -qm tests
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "tests-only change: no stamp needed (FR-024)" 0 $?
mkdir -p "$W/l7r/diagram/ci"; echo 'x = 1' > "$W/l7r/diagram/ci/decision.py"; git -C "$W" add -A; git -C "$W" commit -qm ci
# GUARD_EDIT_OK: feature 178 FR-001 INVERTS this case, and only this half of the GM's FR-025 ruling.
# FR-025 (GM 2026-08-25) answered TWO questions at once - does a ci-only change owe a paid BUILD, and
# does it owe a local GATE - and said no to both. The paid half STANDS: `delta.is_engine` still
# excludes `ci/`, so a ci-only delta still routes DIRECT and still starts no build. The local half is
# superseded, because since 2026-09-02 the coverage floor MEASURES `l7r/diagram/ci/` (174's derived
# `source = ["l7r"]`), and feature 177 found `make done` answering "already verified" on a delta that
# rewrote four ci modules. A surface that owes 100% coverage must be able to re-open the gate that
# enforces it. GM 2026-09-03: *"I think a short-circuit for 'measured but engine' is best."*
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "ci-only change NOW needs a stamp (178 FR-001 supersedes FR-025's local half)" 1 $?
# ...and then REMOVE it, restoring the fixture exactly as the cases below found it. Under FR-001 the
# ci file is diagram-area content, so leaving it behind (as this case did while ci/ was excluded)
# hands every later case an unstamped diagram change and they fail on that instead of on what they
# test. Stamping instead of reverting is NOT equivalent: it leaves a stamp, and the "refusal must name
# the diagram area" case asserts the exact refusal, which changes from "no green gate recorded at all"
# to "ran against DIFFERENT code".
rm -f "$W/l7r/diagram/ci/decision.py"; git -C "$W" add -A; git -C "$W" commit -qm un-ci

# a guard-script change with NO hooks stamp is refused - THE motivating case
echo 'echo changed' > "$W/scripts/hooks/x-hooks.sh"; git -C "$W" commit -qam guard
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "scripts/ change, no hooks stamp -> refused" 1 $?
case $OUT in *"hooks: no green gate"*"make hooks-test"*) : ;; *) echo "FAIL  refusal must name the hooks area and make hooks-test: $OUT"; FAILED=1 ;; esac

# a hooks stamp written against the code being pushed admits it...
( cd "$W" && "$STAMP" stamp --write hooks )
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "scripts/ change, matching hooks stamp -> allowed" 0 $?
# ...and a stale one (the guard edited again after the green run) does not
echo 'echo edited again' > "$W/scripts/hooks/x-hooks.sh"; git -C "$W" commit -qam guard2
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "scripts/ edited after the stamp -> refused" 1 $?
case $OUT in *"DIFFERENT code"*) : ;; *) echo "FAIL  stale-stamp refusal must say the code differs: $OUT"; FAILED=1 ;; esac

# the hooks stamp does not vouch for engine Python, and vice versa
( cd "$W" && "$STAMP" stamp --write hooks )
echo 'x = 2' > "$W/m.py"; git -C "$W" commit -qam engine
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "engine Python change, only a hooks stamp -> refused" 1 $?
case $OUT in *"diagram: no green gate"*) : ;; *) echo "FAIL  refusal must name the diagram area: $OUT"; FAILED=1 ;; esac
( cd "$W" && "$STAMP" stamp --write diagram )
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "both areas stamped -> allowed" 0 $?

# THE PAGE AREA (feature 188): an asset edit owes `make page-check`, and nothing else - not the full gate.
mkdir -p "$W/l7r/diagram/interactive/assets"
echo 'a.q { color: red; }' > "$W/l7r/diagram/interactive/assets/page.css"; git -C "$W" add -A; git -C "$W" commit -qm css
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "asset edit, no page stamp -> refused" 1 $?
case $OUT in *"page: no green gate"*"make page-check"*) : ;; *) echo "FAIL  refusal must name the page area and make page-check: $OUT"; FAILED=1 ;; esac
case $OUT in *"diagram:"*) echo "FAIL  an asset edit must NOT demand a diagram (full gate) stamp: $OUT"; FAILED=1 ;; *) : ;; esac
# the short-circuit exit of make done writes `diagram` and not `page` - so re-stamping diagram does not admit the asset
( cd "$W" && "$STAMP" stamp --write diagram )
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "asset edit + a diagram stamp (the short-circuit's) -> still refused" 1 $?
( cd "$W" && "$STAMP" stamp --write page )
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "asset edit, matching page stamp -> allowed" 0 $?
echo 'a.q { color: blue; }' > "$W/l7r/diagram/interactive/assets/page.css"; git -C "$W" commit -qam css2
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "asset edited after the page stamp -> refused" 1 $?
case $OUT in *"page: the last green gate ran against DIFFERENT code"*) : ;; *) echo "FAIL  stale page stamp must say the code differs: $OUT"; FAILED=1 ;; esac
( cd "$W" && "$STAMP" stamp --write page )

# THE REGISTRY'S DOCSTRINGS ARE PAGE PROSE (feature 189): a docstring edit owes `page` - and `diagram` too since 449 T247, a `.py`
# file's id its blob id (the registry's Python, the feature's subject, left with 449 T149 and T158);
# a code edit in the same file owes both. The new file is stamped in both areas first, so only the EDIT is judged.
mkdir -p "$W/l7r/diagram/interactive/classes"
printf 'class Farmhouse:\n    """What: a house.\n\n    Why: people.\n\n    Note: read.\n    """\n\n    key = "farmhouse"\n' > "$W/l7r/diagram/interactive/classes/homestead.py"
git -C "$W" add -A; git -C "$W" commit -qm registry; ( cd "$W" && "$STAMP" stamp --write diagram && "$STAMP" stamp --write page )
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "registry file stamped in both areas -> allowed" 0 $?
printf 'class Farmhouse:\n    """What: a thatched house.\n\n    Why: people.\n\n    Note: read.\n    """\n\n    key = "farmhouse"\n' > "$W/l7r/diagram/interactive/classes/homestead.py"
git -C "$W" commit -qam prose
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "a DOCSTRING edit in the registry -> refused (page)" 1 $?
case $OUT in *"page: the last green gate ran against DIFFERENT code"*) : ;; *) echo "FAIL  the docstring edit must stale the page stamp: $OUT"; FAILED=1 ;; esac
case $OUT in *"diagram: the last green gate ran against DIFFERENT code"*) : ;; *) echo "FAIL  a .py docstring edit re-opens the gate since 449 T247: $OUT"; FAILED=1 ;; esac
( cd "$W" && "$STAMP" stamp --write diagram && "$STAMP" stamp --write page )
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "page-check re-stamped -> the prose edit lands" 0 $?
printf 'class Farmhouse:\n    """What: a thatched house.\n\n    Why: people.\n\n    Note: read.\n    """\n\n    key = "farm house"\n' > "$W/l7r/diagram/interactive/classes/homestead.py"
git -C "$W" commit -qam code
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "a CODE edit in the registry -> refused" 1 $?
case $OUT in *"diagram: the last green gate ran against DIFFERENT code"*"page: the last green gate ran against DIFFERENT code"*) : ;; *) echo "FAIL  a code edit must owe BOTH stamps: $OUT"; FAILED=1 ;; esac
( cd "$W" && "$STAMP" stamp --write diagram && "$STAMP" stamp --write page )

# a comment added AFTER the green run is not "different code" (GM 2026-08-26): the stamp hashes a .rs file's comment-free
# tokens, so only a token that runs re-opens the gate; a .py file's docstring-stripped AST left with codeid.py (449 T247)
mkdir -p "$W/rust/x"; printf 'fn f() -> i32 {\n    2\n}\n' > "$W/rust/x/m.rs"; git -C "$W" add -A; git -C "$W" commit -qm rs
( cd "$W" && "$STAMP" stamp --write diagram )
printf '// see research/contents.json#water\nfn f() -> i32 {\n    2 // unchanged\n}\n' > "$W/rust/x/m.rs"; git -C "$W" commit -qam why
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "a .rs comment edit after the stamp -> still allowed" 0 $?
printf '"""why this is 2"""\nx = 2\n' > "$W/m.py"; git -C "$W" commit -qam why-py
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "a .py docstring edit after the stamp -> refused since 449 T247" 1 $?
echo 'x = 3' > "$W/m.py"; git -C "$W" commit -qam engine3
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "code edit after the stamp -> refused" 1 $?
( cd "$W" && "$STAMP" stamp --write diagram )

# --fresh: the stamp matches the current guard scripts -> 0 (make done skips hooks-test); an edit -> 1
( cd "$W" && "$STAMP" stamp --write hooks )
( cd "$W" && "$STAMP" stamp --fresh hooks ); check "--fresh hooks right after the stamp -> 0" 0 $?
echo 'echo edited once more' > "$W/scripts/hooks/x-hooks.sh"
( cd "$W" && "$STAMP" stamp --fresh hooks ); check "--fresh hooks after a guard edit -> 1" 1 $?
echo 'x = 4' > "$W/m.py"
( cd "$W" && "$STAMP" stamp --fresh diagram ); check "--fresh diagram after an engine edit -> 1" 1 $?
git -C "$W" commit -qam guard3

# a .py under scripts/ is a hooks-area file too, at any depth (as codeid.py was, until 449 T247)
echo 'y = 1' > "$W/scripts/hooks/lib/helper.py"; git -C "$W" add -A; git -C "$W" commit -qm helper
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "new scripts/*.py, stamp predates it -> refused" 1 $?

# A GIT WORKTREE: `.git` is a FILE there, not a directory (feature 161, 2026-08-30). This is not a
# curiosity - constitution Principle XIII MANDATES a detached worktree for the regression baseline,
# so `make done` in the tree the procedure tells you to create used to crash write_stamp with
# `NotADirectoryError: .../.git/gate-green-hooks`, once per area. The gate ran and passed; only the
# recording failed, noisily but non-fatally, which is the shape that gets scrolled past.
WT="$W-worktree"
rm -rf "$WT"
git -C "$W" worktree add --detach -q "$WT" HEAD
[ -f "$WT/.git" ] || { echo "FAIL  a worktree's .git should be a FILE - the fixture no longer reproduces the trap"; FAILED=1; }
COMMON=$(git -C "$WT" rev-parse --git-common-dir)
case $COMMON in /*) : ;; *) COMMON="$WT/$COMMON" ;; esac
# DELETE any stamp an earlier case left behind, or the "it landed" assertion below passes on the
# unfixed script by finding someone else's file - a check that cannot fail is not a check.
rm -f "$COMMON/gate-green-hooks"
( cd "$WT" && "$STAMP" stamp --write hooks ); check "--write inside a worktree (.git is a FILE) -> 0, no crash" 0 $?
[ -f "$COMMON/gate-green-hooks" ]; check "the worktree's stamp lands in the shared git dir" 0 $?
( cd "$WT" && "$STAMP" stamp --fresh hooks ); check "--fresh inside a worktree reads the stamp it just wrote" 0 $?
git -C "$W" worktree remove --force "$WT"

# ---- the wrapper's no-build seam (feature 449 T143): `guard_log` runs `log guard` from a hook, which must never wait on a build -----------
printf '#!/usr/bin/env bash\necho build >> "%s/cargo.calls"; exit 101\n' "$TMP" > "$TMP/cargo"; chmod +x "$TMP/cargo"
OUT=$(L7R_GATE_TARGET="$TMP/no-target" L7R_GATE_CARGO="$TMP/cargo" L7R_GATE_STALE_OK=1 L7R_GATE_NO_BUILD=1 "$STAMP" --version 2>&1)
check "no binary, L7R_GATE_NO_BUILD -> refused" 1 $?
[ ! -e "$TMP/cargo.calls" ]; check "no binary, L7R_GATE_NO_BUILD -> no build tried" 0 $?
case $OUT in *"L7R_GATE_NO_BUILD builds none"*) : ;; *) echo "FAIL  the no-build refusal says why: $OUT"; FAILED=1 ;; esac

# ---- the run's fresh binary (feature 449 T205): `make hooks-test` names the fresh binary once (L7R_GATE_PRINT_FRESH=1) and exports it as
# L7R_GATE_FRESH; a call whose binary is that one skips the walk of its sources - no build though they are newer - and writes their roots
# to the read recorder's log as `c-tree` lines; any other binary walks and builds as before ------------------------------------------------
FT="$TMP/fresh-target"; mkdir -p "$FT/tool"; printf '#!/usr/bin/env bash\necho "stub $*"\n' > "$FT/tool/l7r-gate"; chmod +x "$FT/tool/l7r-gate"
OUT=$(L7R_GATE_TARGET="$FT" L7R_GATE_CARGO="$TMP/cargo" L7R_GATE_PRINT_FRESH=1 "$STAMP" 2>&1); check "print-fresh: a fresh binary is named" 0 $?
[ "$OUT" = "$FT/tool/l7r-gate" ]; check "print-fresh: ...by its path ($OUT)" 0 $?
touch -d '2000-01-01' "$FT/tool/l7r-gate"; rm -f "$TMP/cargo.calls"
OUT=$(L7R_GATE_TARGET="$FT" L7R_GATE_CARGO="$TMP/cargo" L7R_GATE_FRESH="$FT/tool/l7r-gate" L7R_TEST_DEP_LOG="$TMP/dep.log" L7R_TEST_DEP_FILE=s.sh "$STAMP" a b 2>&1)
check "fresh: the named binary runs" 0 $?
[ "$OUT" = "stub a b" ] && [ ! -e "$TMP/cargo.calls" ]; check "fresh: no walk, no build, though the sources are newer ($OUT)" 0 $?
TOPDIR=$(cd "$HERE/../.." && pwd)
[ "$(grep "$(printf '\tc-tree\t')" "$TMP/dep.log")" = "$(printf 's.sh\tc-tree\t%s\n' "$TOPDIR/rust/gate" "$TOPDIR/rust/guard" "$TOPDIR/rust/Cargo.toml" "$TOPDIR/rust/Cargo.lock" "$TOPDIR/.cargo/config.toml")" ]
check "fresh: the sources' roots in the recorder's log" 0 $?
OUT=$(L7R_GATE_TARGET="$FT" L7R_GATE_CARGO="$TMP/cargo" L7R_GATE_FRESH="$TMP/elsewhere/l7r-gate" "$STAMP" a b 2>&1); check "another binary: walked, and the stale one built (the fake cargo fails)" 1 $?
[ -s "$TMP/cargo.calls" ]; check "another binary: the build was tried" 0 $?
OUT=$(L7R_GATE_TARGET="$FT" L7R_GATE_CARGO="$TMP/cargo" L7R_GATE_PRINT_FRESH=1 "$STAMP" 2>&1); check "print-fresh: a stale binary whose build failed is not named" 1 $?

# ---- a neighbor's uncompiling file (feature 451 T41): builders share a clone, so one builder's guard or gate-crate edit that does not
# compile fails every other builder's gate command (measured 2026-11-20, a scratch clone). The refusal names the file from the tree's root
# and what to do when it is not yours, and nothing runs on the binary built before it: a verdict must come from the code it judges --------
NT="$TMP/neighbor-target"; mkdir -p "$NT/tool"; printf '#!/usr/bin/env bash\necho "stub $*"\n' > "$NT/tool/l7r-gate"; chmod +x "$NT/tool/l7r-gate"
touch -d '2000-01-01' "$NT/tool/l7r-gate"; OLD=$(stat -c %Y "$NT/tool/l7r-gate")
cat > "$TMP/cargo-broken" <<'EOF'
#!/usr/bin/env bash
# cargo's own form: a path relative to the workspace (rust/), twice for one file, and once absolute
printf 'error: this file contains an unclosed delimiter\n  --> guard/src/shared.rs:36:18\n   |\n' >&2
printf 'error[E0308]: mismatched types\n  --> guard/src/shared.rs:40:2\n' >&2
printf 'error[E0425]: cannot find value\n  --> /abs/rust/gate/crates/owed/src/lib.rs:19:18\n' >&2
printf 'error: could not compile `l7r_guard` (lib) due to 2 previous errors\n' >&2
exit 101
EOF
chmod +x "$TMP/cargo-broken"
OUT=$(L7R_GATE_TARGET="$NT" L7R_GATE_CARGO="$TMP/cargo-broken" "$STAMP" plan decide 451 T41 2>&1); check "a neighbor's uncompiling file: refused" 1 $?
case $OUT in *"stub "*) echo "FAIL  the binary built before the edit ran: $OUT"; FAILED=1 ;; esac
case $OUT in *"--> guard/src/shared.rs:36:18"*) : ;; *) echo "FAIL  cargo's own report still shown: $OUT"; FAILED=1 ;; esac
case $OUT in *"l7r-gate: rust/guard/src/shared.rs, /abs/rust/gate/crates/owed/src/lib.rs do not compile, so l7r-gate is not built and no command runs on the one built before them"*) : ;;
  *) echo "FAIL  the refusal names each file once, from the tree's root: $OUT"; FAILED=1 ;; esac
case $OUT in *"l7r-gate: yours? fix what cargo names above. Not yours? another builder in this tree is mid-edit: leave it alone and re-run once it compiles"*) : ;;
  *) echo "FAIL  the refusal says what to do with a neighbor's file: $OUT"; FAILED=1 ;; esac
[ "$(stat -c %Y "$NT/tool/l7r-gate")" = "$OLD" ]; check "a neighbor's uncompiling file: the old binary is not stamped fresh" 0 $?
OUT=$(L7R_GATE_TARGET="$NT" L7R_GATE_CARGO="$TMP/cargo-broken" L7R_GATE_PRINT_FRESH=1 "$STAMP" 2>&1); check "a neighbor's uncompiling file: print-fresh names no binary" 1 $?
OUT=$(L7R_GATE_TARGET="$NT" L7R_GATE_CARGO="$TMP/cargo" "$STAMP" a b 2>&1); check "a failure with no file named: refused" 1 $?
case $OUT in *"l7r-gate: the build failed - fix what cargo names above"*) : ;; *) echo "FAIL  a build that names no file keeps its line: $OUT"; FAILED=1 ;; esac
rm -f "$TMP/broken.calls"
printf '#!/usr/bin/env bash\necho "inc=${CARGO_INCREMENTAL:-}" >> "%s/broken.calls"\nexec "%s/cargo-broken" "$@"\n' "$TMP" "$TMP" > "$TMP/cargo-broken-count"; chmod +x "$TMP/cargo-broken-count"
OUT=$(L7R_GATE_TARGET="$NT" L7R_GATE_CARGO="$TMP/cargo-broken-count" "$STAMP" a b 2>&1); check "a compile error: refused" 1 $?
[ "$(wc -l < "$TMP/broken.calls")" = 1 ]; check "a compile error: built once, no stale-state retry" 0 $?

# ---- a stale incremental unit (feature 451 T142): rust-lld's `undefined hidden symbol` from one crate's reused codegen unit failed the tool's
# link at every incremental build (2026-11-22, l7r_gate_task's unit ads6op1mfn3gc3gvm7k1udw55, an object dated 11-21 12:01 reused into the
# rebuilds of 23:53, 00:14 and 00:15). The launcher drops that crate's incremental session and fingerprint - the ones the linker names, no
# other - rebuilds once incrementally, and says so; a second failure is refused; a link error that names no unit retries non-incrementally.
ST="$TMP/stale-target"; mkdir -p "$ST/tool/incremental/l7r_gate_task-0y4ovoj4hibk7/s-hoe0p69tod-0jsk9kw-4f39" \
  "$ST/tool/incremental/l7r_gate_task-2g61if4ng5haz/s-hobf59uo49-1lkybly-03og" "$ST/tool/.fingerprint/l7r_gate_task-faf2a19073b9305a" \
  "$ST/tool/.fingerprint/l7r_gate_task-295557feace9901b" "$ST/tool/incremental/l7r_shared-1abc/s-x-y"
touch "$ST/tool/incremental/l7r_gate_task-0y4ovoj4hibk7/s-hoe0p69tod-0jsk9kw-4f39/ads6op1mfn3gc3gvm7k1udw55.o" \
  "$ST/tool/incremental/l7r_gate_task-0y4ovoj4hibk7/s-hoe0p69tod-0jsk9kw.lock" \
  "$ST/tool/incremental/l7r_gate_task-2g61if4ng5haz/s-hobf59uo49-1lkybly-03og/other.o" "$ST/tool/incremental/l7r_shared-1abc/s-x-y/ads6op1mfn3gc3gvm7k1udw55.o"
cat > "$TMP/cargo-stale" <<'EOF'
#!/usr/bin/env bash
# the first call fails as rustc's stale unit does; every later call builds (or, with STALE_TWICE, fails the same way again)
n=$(( $(cat "$STALE_CALLS" 2>/dev/null | wc -l) + 1 )); echo "call=$n inc=${CARGO_INCREMENTAL:-} $*" >> "$STALE_CALLS"
if [ "$n" = 1 ] || [ -n "${STALE_TWICE:-}" ]; then
  printf 'error: linking with `cc` failed: exit status: 1\n  = note: "cc" "-m64" "<a thousand words of link line>"\n' >&2
  if [ -n "${STALE_NO_UNIT:-}" ]; then printf '  = note: rust-lld: error: undefined hidden symbol: anon.0482a95c.1.llvm.177\n' >&2; else
  printf '  = note: rust-lld: error: undefined hidden symbol: anon.0482a95c9a0d52167fa52cfa0685df68.1.llvm.17705557342783902695\n' >&2
  printf '          >>> referenced by ads6op1mfn3gc3gvm7k1udw55\n          >>>               l7r_gate_task-faf2a19073b9305a.ads6op1mfn3gc3gvm7k1udw55.rcgu.o:(try_fold) in archive /x/libl7r_gate_task-faf2a19073b9305a.rlib\n' >&2
  printf '          >>> referenced by ads6op1mfn3gc3gvm7k1udw55\n          >>>               l7r_gate_task-faf2a19073b9305a.ads6op1mfn3gc3gvm7k1udw55.rcgu.o:(try_fold) in archive /x/libl7r_gate_task-faf2a19073b9305a.rlib\n' >&2; fi
  printf 'error: could not compile `l7r_gate` (bin "l7r-gate") due to 1 previous error\n' >&2; exit 101
fi
printf '#!/usr/bin/env bash\necho "stub $*"\n' > "$CARGO_TARGET_DIR/tool/l7r-gate"; chmod +x "$CARGO_TARGET_DIR/tool/l7r-gate"
EOF
chmod +x "$TMP/cargo-stale"; export STALE_CALLS="$TMP/stale.calls"
OUT=$(L7R_GATE_TARGET="$ST" L7R_GATE_CARGO="$TMP/cargo-stale" "$STAMP" a b 2>&1); check "a stale unit: dropped, rebuilt, and the command runs" 0 $?
case $OUT in *"stub a b"*) : ;; *) echo "FAIL  the rebuilt binary ran: $OUT"; FAILED=1 ;; esac
[ "$(wc -l < "$STALE_CALLS")" = 2 ] && grep -q '^call=2 inc= ' "$STALE_CALLS"; check "a stale unit: one retry, incremental" 0 $?
[ ! -e "$ST/tool/incremental/l7r_gate_task-0y4ovoj4hibk7" ] && [ ! -e "$ST/tool/.fingerprint/l7r_gate_task-faf2a19073b9305a" ]
check "a stale unit: the session holding the unit and its crate's fingerprint dropped" 0 $?
[ -e "$ST/tool/incremental/l7r_gate_task-2g61if4ng5haz/s-hobf59uo49-1lkybly-03og/other.o" ] && [ -d "$ST/tool/.fingerprint/l7r_gate_task-295557feace9901b" ] \
  && [ -e "$ST/tool/incremental/l7r_shared-1abc/s-x-y/ads6op1mfn3gc3gvm7k1udw55.o" ]
check "a stale unit: the crate's other sessions, its other fingerprints and another crate's unit of that name kept" 0 $?
case $OUT in *"l7r-gate: the link failed on stale incremental state (rust-lld: undefined hidden symbol, referenced from l7r_gate_task's unit ads6op1mfn3gc3gvm7k1udw55): dropped tool/incremental/l7r_gate_task-0y4ovoj4hibk7 and tool/.fingerprint/l7r_gate_task-faf2a19073b9305a, rebuilding once (feature 451 T142)"*) : ;;
  *) echo "FAIL  the retry says what it dropped: $OUT"; FAILED=1 ;; esac
case $OUT in *"thousand words"*) echo "FAIL  a retried link's command line is not dumped: $OUT"; FAILED=1 ;; esac
case $OUT in *"rebuilt and linked"*) : ;; *) echo "FAIL  the retry says it linked: $OUT"; FAILED=1 ;; esac
rm -f "$STALE_CALLS" "$ST/tool/l7r-gate"; mkdir -p "$ST/tool/incremental/l7r_gate_task-0y4ovoj4hibk7/s-a-b"; touch "$ST/tool/incremental/l7r_gate_task-0y4ovoj4hibk7/s-a-b/ads6op1mfn3gc3gvm7k1udw55.o"
OUT=$(STALE_TWICE=1 L7R_GATE_TARGET="$ST" L7R_GATE_CARGO="$TMP/cargo-stale" "$STAMP" a b 2>&1); check "a stale unit that survives the retry: refused" 1 $?
[ "$(wc -l < "$STALE_CALLS")" = 2 ]; check "a stale unit that survives the retry: one retry, no loop" 0 $?
case $OUT in *"stub "*) echo "FAIL  nothing runs on a failed retry: $OUT"; FAILED=1 ;; esac
case $OUT in *"l7r-gate: the rebuild after dropping the stale state failed too"*) : ;; *) echo "FAIL  the second failure says so: $OUT"; FAILED=1 ;; esac
rm -f "$STALE_CALLS"
OUT=$(STALE_NO_UNIT=1 L7R_GATE_TARGET="$ST" L7R_GATE_CARGO="$TMP/cargo-stale" "$STAMP" a b 2>&1); check "a link error naming no unit: rebuilt non-incrementally" 0 $?
grep -q '^call=2 inc=0 ' "$STALE_CALLS"; check "a link error naming no unit: the retry is CARGO_INCREMENTAL=0" 0 $?
case $OUT in *"names no unit to drop, rebuilding once with CARGO_INCREMENTAL=0"*) : ;; *) echo "FAIL  the non-incremental retry says so: $OUT"; FAILED=1 ;; esac
unset STALE_CALLS

# ---- the Mode A engine through the launcher (feature 449 T168): `l7r-gate.sh mode-a` builds and runs `l7r-mode-a`, its own program, and
# `make building-programs CHECK=1`'s form of it finds the real page current ------------------------------------------------------------
OUT=$("$STAMP" mode-a --version); check "mode-a: the launcher runs l7r-mode-a" 0 $?
OUT=$(cd "$HERE/../.." && "$STAMP" mode-a building-programs --check); check "mode-a building-programs --check: the real page" 0 $?
case $OUT in "building-programs: docs/building-programs.md is current") : ;; *) echo "FAIL  the check's line: $OUT"; FAILED=1 ;; esac

# ---- the hamlet driver through the launcher (feature 449 T221): `l7r-gate.sh hamlet` is the tool build of `rust/phases`' `hamlet`, the
# binary the generation cache identifies the hamlets' engine by; `rust hamlet ...` (the counting runs) stays `l7r-rust`'s ------------------
HT="$TMP/hamlet-target"; mkdir -p "$HT/tool"
for b in hamlet l7r-rust; do printf '#!/usr/bin/env bash\necho "%s $*"\n' "$b" > "$HT/tool/$b"; chmod +x "$HT/tool/$b"; touch -d '2100-01-01' "$HT/tool/$b"; done
OUT=$(L7R_GATE_TARGET="$HT" L7R_GATE_CARGO="$TMP/cargo" L7R_GATE_PRINT_FRESH=1 "$STAMP" hamlet 2>&1); check "hamlet: the launcher names its tool build" 0 $?
[ "$OUT" = "$HT/tool/hamlet" ]; check "hamlet: ...by its path ($OUT)" 0 $?
OUT=$(L7R_GATE_TARGET="$HT" L7R_GATE_CARGO="$TMP/cargo" "$STAMP" rust hamlet --crate x 2>&1)
[ "$OUT" = "l7r-rust hamlet --crate x" ]; check "rust hamlet: the Rust checks' runner, not the hamlet arm ($OUT)" 0 $?

echo -----
if [ "$FAILED" -eq 0 ]; then echo "all gate-stamp tests passed (shard 1)"; exit 0; else echo "SOME TESTS FAILED"; exit 1; fi
