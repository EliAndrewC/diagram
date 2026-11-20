#!/usr/bin/env bash
# Tests for l7r-gate stamp (rust/gate/crates/tree/src/stamp.rs) - the push-time "a green gate saw exactly this code" guard.
# Run: tests/hooks/test-l7r-gate.sh   (exit 0 = all green). Runs under `make hooks-test`.
#
# THE CASE THAT MOTIVATED THIS FILE (2026-08-25): a session ran `make hooks-test` (RED), then
# `git commit; sync-with-main.sh done` chained with ';', and the push LANDED - the only code that
# had changed was under scripts/, which the stamp did not cover. A guard-script change must now
# carry a green `make hooks-test` stamp exactly as engine Python must carry a green `make done`.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAMP="$HERE/../../scripts/gates/l7r-gate.sh"  # the Rust gate; its ids of .py files come from codeid.py
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

# THE REGISTRY'S DOCSTRINGS ARE PAGE PROSE (feature 189): a docstring edit owes `page` and NOT `diagram`;
# a code edit in the same file owes both. The new file is stamped in both areas first, so only the EDIT is judged.
mkdir -p "$W/l7r/diagram/interactive/classes"
printf 'class Farmhouse:\n    """What: a house.\n\n    Why: people.\n\n    Note: read.\n    """\n\n    key = "farmhouse"\n' > "$W/l7r/diagram/interactive/classes/homestead.py"
git -C "$W" add -A; git -C "$W" commit -qm registry; ( cd "$W" && "$STAMP" stamp --write diagram && "$STAMP" stamp --write page )
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "registry file stamped in both areas -> allowed" 0 $?
printf 'class Farmhouse:\n    """What: a thatched house.\n\n    Why: people.\n\n    Note: read.\n    """\n\n    key = "farmhouse"\n' > "$W/l7r/diagram/interactive/classes/homestead.py"
git -C "$W" commit -qam prose
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "a DOCSTRING edit in the registry -> refused (page)" 1 $?
case $OUT in *"page: the last green gate ran against DIFFERENT code"*) : ;; *) echo "FAIL  the docstring edit must stale the page stamp: $OUT"; FAILED=1 ;; esac
case $OUT in *"diagram:"*) echo "FAIL  a docstring edit must NOT re-open the gate (diagram stays semantic): $OUT"; FAILED=1 ;; *) : ;; esac
( cd "$W" && "$STAMP" stamp --write page )
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "page-check re-stamped -> the prose edit lands" 0 $?
printf 'class Farmhouse:\n    """What: a thatched house.\n\n    Why: people.\n\n    Note: read.\n    """\n\n    key = "farm house"\n' > "$W/l7r/diagram/interactive/classes/homestead.py"
git -C "$W" commit -qam code
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "a CODE edit in the registry -> refused" 1 $?
case $OUT in *"diagram: the last green gate ran against DIFFERENT code"*"page: the last green gate ran against DIFFERENT code"*) : ;; *) echo "FAIL  a code edit must owe BOTH stamps: $OUT"; FAILED=1 ;; esac
( cd "$W" && "$STAMP" stamp --write diagram && "$STAMP" stamp --write page )

# a comment or docstring added AFTER the green run is not "different code" (GM 2026-08-26): the stamp
# hashes the docstring-stripped AST of each .py, so only a token that runs re-opens the gate
printf '"""why this is 2"""\n# see research/contents.json#water\nx = 2  # unchanged\n' > "$W/m.py"; git -C "$W" commit -qam why
OUT=$(cd "$W" && "$STAMP" stamp --check origin/main 2>&1); check "comment/docstring edit after the stamp -> still allowed" 0 $?
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

# a .py under scripts/ is a hooks-area file too, at any depth (codeid.py lives there)
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

# ---- the browser and the archive end to end, through the launcher (feature 449 T146, `ask:449-T80-order`: "the browser sits behind one
# seam ... with one end-to-end test") ------------------------------------------------------------------------------------------------
# The production wiring the crates' own tests replace - `record archive`'s real command line, its store over the archive's home, the
# push's credential through the launcher's `github-token`, the browser started as `l7r-gate.sh browser serve` on the pinned Chromium -
# run here as a session runs it: a page on a loopback server archived whole into a working copy cloned from a local bare repository
# (never GitHub), the secrets file empty, the GM's folder absent. About two seconds.
A=$TMP/archive; R=$A/repo; mkdir -p "$R/research/sources/010-works-cited" "$R/research/questions" "$A/site"; git init -q "$R"
printf '<main>\n' > "$R/research/sources/_front.html"; printf '</main>\n' > "$R/research/sources/_tail.html"
printf '<h2 id="works-cited">Works cited</h2>\n' > "$R/research/sources/010-works-cited.html"
printf '{"domains": []}\n' > "$R/research/blocked-domains.json"; printf '{"patterns": []}\n' > "$R/research/banned-citations.json"
printf '<!DOCTYPE html><html><body><p>an archived page</p></body></html>' > "$A/site/page.html"
git init -q --bare -b main "$A/remote.git"; git clone -q "$A/remote.git" "$A/seed" 2>/dev/null
echo seed > "$A/seed/README"; git -C "$A/seed" add -A; git -C "$A/seed" commit -qm seed; git -C "$A/seed" push -q origin HEAD:main
mkdir -p "$A/home"; git clone -q "$A/remote.git" "$A/home/source-archive"; : > "$A/no-secrets.ini"
# never the internet (feature 449 T146): a request past loopback - a Wayback lookup on a page that failed, say - meets a dead proxy
# and fails at once, so the suite needs no network and sends nothing out; loopback itself is exempt
export http_proxy=http://127.0.0.1:9 https_proxy=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 HTTPS_PROXY=http://127.0.0.1:9 \
  all_proxy=http://127.0.0.1:9 ALL_PROXY=http://127.0.0.1:9 no_proxy=127.0.0.1,localhost NO_PROXY=127.0.0.1,localhost
PORT=$(python3 -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])')
(cd "$A/site" && exec python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1) & SRV=$!
for _ in $(seq 50); do python3 -c "import urllib.request as u; u.urlopen('http://127.0.0.1:$PORT/page.html', timeout=1)" 2>/dev/null && break; sleep 0.1; done
arch() { (cd "$R" && L7R_SOURCES_HOME="$A/home" DIAGRAM_SECRETS="$A/no-secrets.ini" L7R_GM_SOURCES="$A/gm" "$STAMP" record archive "$@" 2>&1); }
OUT=$(arch url "http://127.0.0.1:$PORT/page.html" --key e2e-key); check "record archive url: a page archived end to end" 0 $?
case $OUT in "archive: archived - http://127.0.0.1:$PORT/page.html"*"diagram-research/tree/main/"*) : ;; *) echo "FAIL  the archived line: $OUT"; FAILED=1 ;; esac
LOG=$(git -C "$A/remote.git" log -1 --format=%s --name-only)
case $LOG in "archived: http://127.0.0.1:$PORT/page.html"*page.mhtml*served.html*text.txt*) : ;; *) echo "FAIL  the capture pushed whole: $LOG"; FAILED=1 ;; esac
grep -q '"route": "archive"' "$R/research/source-attempts.jsonl"; check "the attempt logged" 0 $?
grep -q '"keys": \[' "$R"/research/archive/*/*.json; check "the manifest row written" 0 $?
OUT=$(arch backfill --workers 1); check "record archive backfill: nothing owed, the push and the coverage" 0 $?
case $OUT in *"0 cited URL(s) owed a copy"*"archive coverage: 0 cited URL(s)"*) : ;; *) echo "FAIL  the backfill's lines: $OUT"; FAILED=1 ;; esac
OUT=$(arch gm-copies); check "record archive gm-copies: no table, no copies" 0 $?
# The uncited filter's production wiring end to end (feature 449 T147, phase 4's S3b): `record uncited fetch`'s lanes on the real browser
# (the archive's `start_browser`), each line printed as it goes - the ledger names two long pages on the loopback server and the fetch
# reads both into the page cache. The lane meeting a blocked page mid-way (the round arbiter's `ask:449-T146-browser`, which this case
# held while the Python's lane ran) is held by the `uncited` crate's own test, `fetch::tests`, since the set never holds a blocked page.
for n in 1 2; do printf '<!DOCTYPE html><html><body><p>%s</p></body></html>' "$(printf 'a long page %s, ' "$n" | head -c 15; printf 'words %.0s' $(seq 120))" > "$A/site/long$n.html"; done
printf '{"url": "127.0.0.1:%s/long1.html", "raw": "http://127.0.0.1:%s/long1.html"}\n{"url": "127.0.0.1:%s/long2.html", "raw": "http://127.0.0.1:%s/long2.html"}\n' \
  "$PORT" "$PORT" "$PORT" "$PORT" > "$A/home/sources-consulted.jsonl"
OUT=$(cd "$R" && L7R_SOURCES_HOME="$A/home" DIAGRAM_SECRETS="$A/no-secrets.ini" "$STAMP" record uncited fetch --workers 1 2>&1)
check "record uncited fetch: the lanes on the real browser" 0 $?
case $OUT in "uncited: fetching 2 page(s) in up to 1 lane(s)
read                   http://127.0.0.1:$PORT/long1.html
read                   http://127.0.0.1:$PORT/long2.html
uncited: {\"read\": 2, \"unreadable\": 0, \"error\": 0}") : ;; *) echo "FAIL  the fetch's lines: $OUT"; FAILED=1 ;; esac
grep -q '"route": "uncited-fetch"' "$R/research/source-attempts.jsonl"; check "the fetch's attempts logged" 0 $?
# a cited page read, archived in process (`record sources outcome`, where it ran `archive_ops.py urls`): the production browser and store
printf '<!DOCTYPE html><html><body><p>a cited page</p></body></html>' > "$A/site/cited.html"
OUT=$(cd "$R" && L7R_SOURCES_HOME="$A/home" DIAGRAM_SECRETS="$A/no-secrets.ini" "$STAMP" record sources outcome "http://127.0.0.1:$PORT/cited.html" cited:e2e-key 2>&1)
check "record sources outcome cited: the page archived in process" 0 $?
case $OUT in *"archive: archived - http://127.0.0.1:$PORT/cited.html"*) : ;; *) echo "FAIL  the cited read's archiving: $OUT"; FAILED=1 ;; esac
# `record downloads ingest` ends with the archive's inbox in process (where it ran `archive_ops.py inbox`): a synced list, one GM download
mkdir -p "$A/gm"; printf '# Downloads\n' > "$R/research/to-download.md"; git -C "$R" add -A; git -C "$R" -c user.name=t -c user.email=t@t commit -qm list
(cd "$R" && L7R_GM_SOURCES="$A/gm" "$STAMP" record downloads sync >/dev/null 2>&1); printf 'a download\n' > "$A/gm/e2e.txt"
OUT=$(cd "$R" && L7R_SOURCES_HOME="$A/home" DIAGRAM_SECRETS="$A/no-secrets.ini" L7R_GM_SOURCES="$A/gm" "$STAMP" record downloads ingest --keep "" --drop "" --mark "" 2>&1)
check "record downloads ingest: the inbox in process" 0 $?
case $OUT in *"archive: 0 inbox file(s) archived, pushed and removed from $A/gm"*"WAITING e2e.txt: a new download"*) : ;; *) echo "FAIL  the ingest's inbox: $OUT"; FAILED=1 ;; esac
kill "$SRV" 2>/dev/null; wait "$SRV" 2>/dev/null

# ---- the embedder and the research search end to end, through the launcher (feature 449 T138, `ask:449-phase4-slices` Q11: "a Rust
# embedder runs the same BGE-M3 weights ... against the stored index") ----------------------------------------------------------------
# The one case that runs the real model: `l7r-gate.sh embed serve` on the model fastembed fetched into the mirror's model cache and the
# pinned ONNX Runtime, a vector checked bit for bit against `semantic_index.py`'s own (fastembed 0.9.1, observed 2026-11-16: the first
# four floats of "the largest single paddy field" embedded alone); then `record semantic build`, `find` and `record search` on their
# production wiring - the embedder started as a program, the shards committed and pushed to a local bare repository (never GitHub). With
# no model in the cache it fails, as T146's case fails with no Chromium. About ten seconds and 2 GB, the model held once at a time.
TOP=$(git -C "$HERE" rev-parse --show-toplevel)
case $TOP in */.clones/*) MIRROR=${TOP%/.clones/*} ;; *) MIRROR=$TOP ;; esac
CACHE=${L7R_MODEL_CACHE:-$MIRROR/.specify/model-cache}
VEC=$(printf '["the largest single paddy field"]\n' | "$STAMP" embed serve --cache "$CACHE" | python3 -c '
import sys
b = sys.stdin.buffer
print(b.readline().decode().strip(), b.readline().decode().strip(), b.read(16).hex())')
check "embed serve: the real model answers" 0 $?
[ "$VEC" = "ready ok 1 1024 8e9418bda1ce6d3c0af225bdf860b7bc" ]; check "embed serve: the Python's vector, bit for bit ($VEC)" 0 $?
S=$TMP/semantic; mkdir -p "$S/repo/research/questions" "$S/home"; git init -q "$S/repo"; ln -s "$CACHE" "$S/home/model-cache"
printf '<h2>Paddies</h2><p>A single paddy was a tan or two, about a thousand square meters.</p>\n' > "$S/repo/research/questions/0001-paddies.html"
git init -q --bare -b main "$S/remote.git"; git clone -q "$S/remote.git" "$S/home/source-archive" 2>/dev/null
mkdir -p "$S/home/source-archive/ab/abc/20260101T000000Z"; printf 'Thatched roofs were renewed every twenty years.\n' > "$S/home/source-archive/ab/abc/20260101T000000Z/text.txt"
git -C "$S/home/source-archive" -c user.name=t -c user.email=t@t commit -q --allow-empty -m seed; git -C "$S/home/source-archive" push -q origin HEAD:main
sem() { (cd "$S/repo" && L7R_SOURCES_HOME="$S/home" DIAGRAM_SECRETS="$A/no-secrets.ini" GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t "$STAMP" record "$@" 2>&1); }
OUT=$(sem semantic build); check "record semantic build: embedded, committed and pushed" 0 $?
case $OUT in "semantic-index: ab - 1 passages, 1 embedded
semantic-index: record-00 - 1 passages, 1 embedded
semantic-index: 2 shard(s) written
semantic-index: committed and pushed") : ;; *) echo "FAIL  the build's lines: $OUT"; FAILED=1 ;; esac
case $(git -C "$S/remote.git" log -1 --format=%s main) in "the semantic index (Xenova/bge-m3-int8): 2 shard(s) - ab, record-00") : ;; *) echo "FAIL  the shards pushed"; FAILED=1 ;; esac
OUT=$(sem semantic find "how often was thatch replaced" --k 1); check "record semantic find: the nearest passage" 0 $?
case $OUT in 0.*"  ab/abc/20260101T000000Z/text.txt [0:48]"*"Thatched roofs were renewed every twenty years."*) : ;; *) echo "FAIL  the find's line: $OUT"; FAILED=1 ;; esac
OUT=$(sem search --q "田の広さ" --terms "paddy"); check "record search: the meaning and the text search" 0 $?
case $OUT in "research-search: 1 question(s), 1 term set(s) - 2 of 2 source(s)"*" 1. record 0001  [index+text]"*) : ;; *) echo "FAIL  the search's lines: $OUT"; FAILED=1 ;; esac

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
if [ "$FAILED" -eq 0 ]; then echo "all gate-stamp tests passed"; exit 0; else echo "SOME TESTS FAILED"; exit 1; fi
