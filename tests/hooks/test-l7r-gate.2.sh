#!/usr/bin/env bash
# test-l7r-gate.2.sh - the second shard of l7r-gate.sh's suite (feature 451 T21 split it by its case groups, plan D17): the browser and
# the archive end to end, through the launcher - its own fixture, as every shard's is.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAMP="$HERE/../../scripts/gates/l7r-gate.sh"  # the Rust gate (a .py file's id its blob id since 449 T247 deleted codeid.py)
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
FAILED=0
check() { # label expected-rc actual-rc
  if [ "$2" = "$3" ]; then printf 'ok    %s (rc=%s)\n' "$1" "$3"; else printf 'FAIL  %s (expected rc=%s, got rc=%s)\n      out: %s\n' "$1" "$2" "$3" "${OUT:-}"; FAILED=1; fi
}

export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t

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

echo -----
if [ "$FAILED" -eq 0 ]; then echo "all gate-stamp tests passed (shard 2)"; exit 0; else echo "SOME TESTS FAILED"; exit 1; fi
