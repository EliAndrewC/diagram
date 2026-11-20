#!/usr/bin/env bash
# test-l7r-gate.3.sh - the third shard of l7r-gate.sh's suite (feature 451 T21 split it by its case groups, plan D17): the embedder and
# the research search end to end, through the launcher - its own fixture: the empty secrets file and the dead proxy the archive
# group left it before the split are made here.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAMP="$HERE/../../scripts/gates/l7r-gate.sh"  # the Rust gate; its ids of .py files come from codeid.py
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
FAILED=0
check() { # label expected-rc actual-rc
  if [ "$2" = "$3" ]; then printf 'ok    %s (rc=%s)\n' "$1" "$3"; else printf 'FAIL  %s (expected rc=%s, got rc=%s)\n      out: %s\n' "$1" "$2" "$3" "${OUT:-}"; FAILED=1; fi
}

export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t

# never the internet (feature 449 T146): a request past loopback - a Wayback lookup on a page that failed, say - meets a dead proxy
# and fails at once, so the suite needs no network and sends nothing out; loopback itself is exempt
export http_proxy=http://127.0.0.1:9 https_proxy=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 HTTPS_PROXY=http://127.0.0.1:9 \
  all_proxy=http://127.0.0.1:9 ALL_PROXY=http://127.0.0.1:9 no_proxy=127.0.0.1,localhost NO_PROXY=127.0.0.1,localhost

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
S=$TMP/semantic; mkdir -p "$S/repo/research/questions" "$S/home"; git init -q "$S/repo"; ln -s "$CACHE" "$S/home/model-cache"; : > "$S/no-secrets.ini"
printf '<h2>Paddies</h2><p>A single paddy was a tan or two, about a thousand square meters.</p>\n' > "$S/repo/research/questions/0001-paddies.html"
git init -q --bare -b main "$S/remote.git"; git clone -q "$S/remote.git" "$S/home/source-archive" 2>/dev/null
mkdir -p "$S/home/source-archive/ab/abc/20260101T000000Z"; printf 'Thatched roofs were renewed every twenty years.\n' > "$S/home/source-archive/ab/abc/20260101T000000Z/text.txt"
git -C "$S/home/source-archive" -c user.name=t -c user.email=t@t commit -q --allow-empty -m seed; git -C "$S/home/source-archive" push -q origin HEAD:main
sem() { (cd "$S/repo" && L7R_SOURCES_HOME="$S/home" DIAGRAM_SECRETS="$S/no-secrets.ini" GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t "$STAMP" record "$@" 2>&1); }
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

echo -----
if [ "$FAILED" -eq 0 ]; then echo "all gate-stamp tests passed (shard 3)"; exit 0; else echo "SOME TESTS FAILED"; exit 1; fi
