#!/usr/bin/env bash
# The build side of feature 130 - what a CodeBuild build does once the dispatcher started it.
# Both buildspecs (check.yml, merge.yml) run THIS script; MODE decides the only difference, which
# is whether the merge result is pushed to main. Nothing about what the gate CHECKS lives here - the
# build runs `make $MAKE_TARGET` exactly as the laptop does.
#
#   wait-go   park until go/<build-id> appears (<= PARK_TIMEOUT_S, FR-036) - a dead dispatcher can
#             cost at most that; the dispatcher stops this build outright when its local reference
#             check fails, so a build that reaches "merge" was released on purpose
#   merge     merge the LATEST origin/main into the mailbox commit; a conflict fails in seconds
#   gate      make $MAKE_TARGET in the skill directory (done | done FULL=1 | an expensive operation)
#   record    on green: verified/<tree>.json (scope-tagged, FR-027), artifacts (perf-log, reports)
#   push      merge mode only: fast-forward push HEAD:main; a rejection means main moved - fail, no retry (R3)
set -euo pipefail
trap 'echo "run.sh: FAILED at line $LINENO (exit $?)"' ERR   # a silent set -e exit cost a build to diagnose (4483c680)
: "${MODE:?check|merge}" "${GIT_SHA:?}" "${MAILBOX:?}" "${CI_BUCKET:?}" "${GITHUB_REPO:?}" "${GITHUB_TOKEN:?}"
MAKE_TARGET=${MAKE_TARGET:-done}
CI_SCOPE=${CI_SCOPE:-reference}
PARK_TIMEOUT_S=${PARK_TIMEOUT_S:-120}
BUILD_UUID=${CODEBUILD_BUILD_ID##*:}
SKILL=.claude/skills/diagram

echo "== fetch: $GITHUB_REPO @ $MAILBOX ($GIT_SHA), mode=$MODE target='$MAKE_TARGET' scope=$CI_SCOPE"
# the buildspec's install phase already cloned once (to fetch this script); reuse it - a blob:none
# clone of this repository measured ~56 s on the first real build, and paying it twice is waste
# THE CACHE ARRIVES BEFORE THE SOURCE (feature 175). CodeBuild restores its S3 cache during
# DOWNLOAD_SOURCE, and the cached paths live under `repo/.claude/skills/diagram/.gencache/` - so on any
# build after the first, `repo/` ALREADY EXISTS holding nothing but the generation cache. `mv bootstrap
# repo` then moves bootstrap INSIDE it as `repo/bootstrap` instead of renaming, and `cd repo` lands in a
# directory with no `.git`: build a48b730d died at the next git call with exit 128, one billed minute.
# So the restored cache is set aside, the clone proceeds exactly as before, and the cache is laid back
# down on top of the checkout. `cp -a` rather than `mv` for the return leg because the tree it merges
# into already exists.
# MOVE THE WHOLE DIRECTORY, never `repo/*`: the cached tree's top entry is `.claude`, and a glob does
# not match a leading dot. The first draft of this used `mv repo/* "$tmp"/` and silently dropped the
# entire cache while looking like it had preserved it - caught by a local simulation rather than by
# another billed build, which is the only reason it is not a fifth failed dispatch.
# FEATURE 177: THE TEST IS "IS THERE A REAL REPOSITORY HERE?", NOT "IS THERE A .git?". It used to be
# `[ ! -d repo/.git ]`, which was right only while the cache held nothing under `.git`. Feature 177
# puts the hooks-test freshness state there (`repo/.git/gate-green-hooks`,
# `repo/.git/hooks-test/**`), so a restored cache now CREATES `repo/.git` - the old test would see a
# directory, skip the set-aside, and `mv bootstrap repo` would move bootstrap INSIDE it. That is
# build a48b730d exactly, one billed minute, and it would have come back the moment the cache paths
# widened. `HEAD` is the file every real git directory has and a cache of stamps can never have.
restored=""
if [ -d repo ] && [ ! -e repo/.git/HEAD ]; then mv repo .cache-restore && restored=1; fi
if [ -d bootstrap/.git ]; then mv bootstrap repo; else git clone -q --filter=blob:none --no-checkout "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPO}" repo; fi
if [ -n "$restored" ]; then cp -a .cache-restore/. repo/ && rm -rf .cache-restore && echo "== cache: generation cache laid over the checkout"; fi
cd repo
# THE BUILD DOES NOT CHECK OUT WHAT NO GATE PHASE READS (feature 177). Measured: HEAD is 465.8 MB
# over 2,102 files and 441 MB of it is 91 generated artifacts; materializing them cost 43 s of a
# 154 s build, every build. The patterns are DERIVED from one file with the evidence for each beside
# it - buildspec/sparse-excludes.txt - never written here, because three consumers read that roster
# and a second copy is how a roster goes stale.
#
# SPARSE-CHECKOUT TOUCHES THE WORKING TREE ONLY. The index and every tree written from it stay
# complete, so the merge below and the `git push HEAD:main` at the end carry every path tracked at
# the merge base - demonstrated before this shipped (specs/177 R9), including across a merge that
# CHANGED an excluded path, where the pushed tree carried the updated content and the worktree stayed
# sparse. That property is what makes this safe on the merge project; nothing else would be.
if [ -f buildspec/sparse-excludes.txt ]; then
  set -- '/*'
  while IFS= read -r pat; do
    # `producer:` lines are METADATA the roster's guard reads, not patterns. Without this case the
    # loop passes `!producer: l7r/...` to git as an exclusion - which git accepts silently, matching
    # nothing, so the roster would look applied and the real patterns would still work. A defect that
    # cannot fail is the kind this project pays for later, so it is skipped here and pinned by
    # `tests/tooling/ci/test_sparse_checkout.py`.
    case "$pat" in ''|'#'*|producer:*) continue ;; esac
    set -- "$@" "!$pat"
  done < buildspec/sparse-excludes.txt
  git sparse-checkout set --no-cone "$@" && echo "== sparse: excluding $(( $# - 1 )) pattern(s) no gate phase reads"
fi
git checkout -q -- . 2>/dev/null || true
git config user.name "gm-assistant-ci"; git config user.email "ci@gm-assistant.invalid"
git fetch -q origin "refs/heads/${MAILBOX}:refs/remotes/origin/${MAILBOX}"
tip=$(git rev-parse "origin/${MAILBOX}")
[ "$tip" = "$GIT_SHA" ] || { echo "REFUSED: GIT_SHA $GIT_SHA is not the tip of $MAILBOX ($tip)"; exit 1; }
git checkout -q --detach "$GIT_SHA"

echo "== wait-go: polling s3://$CI_BUCKET/go/$BUILD_UUID (<= ${PARK_TIMEOUT_S}s)"
waited=0
until aws s3api head-object --bucket "$CI_BUCKET" --key "go/$BUILD_UUID" >/dev/null 2>&1; do
  if [ "$waited" -ge "$PARK_TIMEOUT_S" ]; then echo "aborted: no go signal after ${PARK_TIMEOUT_S}s (the dispatcher is gone)"; exit 1; fi
  sleep 2; waited=$((waited+2))
done
# the service role may not hold s3:DeleteObject (build 4483c680 died here, silently); the dispatcher deletes a leftover signal itself
aws s3 rm --quiet "s3://$CI_BUCKET/go/$BUILD_UUID" 2>/dev/null || echo "(go signal not deleted - the dispatcher cleans it up)"
echo "== go received after ${waited}s"

# STOCK-IMAGE BOOTSTRAP. The custom image (Dockerfile.ci, `make ci-image`) is an OPTIMIZATION the
# operator enables from a terminal; until it exists - and whenever the dispatcher finds no image
# marker - the build runs on aws/codebuild/standard and installs what the gate needs here: Python
# 3.14 through uv (prebuilt, seconds), the two pinned lockfiles, resvg from its release tarball,
# and the DejaVu faces. Measured in timings.md beside the image's provisioning time.
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info[:2] == (3, 14) else 1)' 2>/dev/null || ! command -v resvg >/dev/null; then
  echo "== bootstrap (stock image): python 3.14 via uv, lockfiles, resvg, fonts"
  t0=$(date +%s)
  curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1; export PATH="$HOME/.local/bin:$PATH"
  uv venv -q --python 3.14 /tmp/venv && . /tmp/venv/bin/activate
  uv pip install -q -r "$SKILL/requirements.txt" -r "$SKILL/requirements-dev.txt"
  curl -sSL "https://github.com/linebender/resvg/releases/download/v0.46.0/resvg-linux-x86_64.tar.gz" | tar -xz -C /usr/local/bin resvg
  (apt-get install -y -qq fonts-dejavu-core fonts-dejavu-extra >/dev/null 2>&1 || (apt-get update -qq >/dev/null && apt-get install -y -qq fonts-dejavu-core fonts-dejavu-extra >/dev/null))
  echo "== bootstrap done in $(( $(date +%s) - t0 ))s: $(python3 --version), resvg $(resvg --version)"
fi

echo "== merge: origin/main -> $MAILBOX"
main_sha=$(git rev-parse origin/main)
git merge --no-edit origin/main || { echo "CONFLICT: the mailbox commit does not merge with the latest main - merge main locally, resolve, commit, re-run"; exit 1; }
tree=$(git rev-parse 'HEAD^{tree}')
echo "== merged main $main_sha; tree $tree"

echo "== gate: make $MAKE_TARGET  (nproc $(nproc))"
cd "$SKILL"
export SPECIFY_FEATURE="${SPECIFY_FEATURE:-}"
if [ -z "$SPECIFY_FEATURE" ]; then SPECIFY_FEATURE=$(ls -d ../../../specs/[0-9]*/ 2>/dev/null | sort | tail -1 | xargs -r basename); export SPECIFY_FEATURE; fi
t0=$(date +%s)
set +e
# shellcheck disable=SC2086
make --no-print-directory $MAKE_TARGET </dev/null
rc=$?
set -e
echo "== gate exit $rc after $(( $(date +%s) - t0 ))s"
cd ../../..

# artifacts: perf snapshots (a FULL run took both bookends in-build) and any operation report
if ls "$SKILL"/dev/perf-log/*.json >/dev/null 2>&1; then
  for f in $(git status --porcelain --untracked-files=all -- "$SKILL/dev/perf-log" | awk '{print $2}'); do
    aws s3 cp --quiet "$f" "s3://$CI_BUCKET/artifacts/$BUILD_UUID/perf-log/$(basename "$f")"
  done
fi
if [ -d "$SKILL/dev/ci-report" ]; then aws s3 cp --quiet --recursive "$SKILL/dev/ci-report" "s3://$CI_BUCKET/artifacts/$BUILD_UUID/report/"; fi

[ "$rc" -eq 0 ] || { echo "== gate RED - no record, nothing pushed"; exit "$rc"; }

# THE RECORD IS KEYED BY THE ENGINE CONTENT the gate tested (a hash over the engine paths' blobs in
# the merge tree - the same function the dispatcher looks up with), not by the whole tree: a docs
# change after a green build must not throw the verification away (GM 2026-08-25).
key=$(cd "$SKILL" && make --no-print-directory engine-key REF=HEAD)
echo "== record: verified/$key.json ($CI_SCOPE; tree $tree)"
printf '{"tree":"%s","engine_key":"%s","build_id":"%s","project":"%s","scope":"%s","utc":"%s","main":"%s","work":"%s","target":"%s"}\n' \
  "$tree" "$key" "$CODEBUILD_BUILD_ID" "$MODE" "$CI_SCOPE" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$main_sha" "$GIT_SHA" "$MAKE_TARGET" > /tmp/verified.json
# THE RECORD IS THE SKIP-VERIFIED OPTIMIZATION, NOT THE VERDICT: a merge whose gate passed lands even
# when the bucket refuses the write (build 347249b6 failed here under a bucket policy whose
# NotPrincipal did not match the assumed-role session - the policy is now condition-form).
aws s3 cp --quiet /tmp/verified.json "s3://$CI_BUCKET/verified/$key.json" || echo "(verified record NOT written - the bucket policy refused this principal; the next merge of this tree will run a build instead of SKIP-VERIFIED)"

if [ "$MODE" = merge ]; then
  echo "== push: HEAD -> main (fast-forward only)"
  git push origin HEAD:main || { echo "main moved; re-run (the push was not a fast-forward - nothing landed)"; exit 1; }
  git push -q origin --delete "$MAILBOX" || echo "(mailbox $MAILBOX not deleted - harmless)"
  echo "== landed $(git rev-parse HEAD) on main"
fi
echo "== done"
