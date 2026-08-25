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
: "${MODE:?check|merge}" "${GIT_SHA:?}" "${MAILBOX:?}" "${CI_BUCKET:?}" "${GITHUB_REPO:?}" "${GITHUB_TOKEN:?}"
MAKE_TARGET=${MAKE_TARGET:-done}
CI_SCOPE=${CI_SCOPE:-reference}
PARK_TIMEOUT_S=${PARK_TIMEOUT_S:-120}
BUILD_UUID=${CODEBUILD_BUILD_ID##*:}
SKILL=.claude/skills/diagram

echo "== fetch: $GITHUB_REPO @ $MAILBOX ($GIT_SHA), mode=$MODE target='$MAKE_TARGET' scope=$CI_SCOPE"
git clone -q --filter=blob:none "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPO}" repo
cd repo
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
aws s3 rm -q "s3://$CI_BUCKET/go/$BUILD_UUID"
echo "== go received after ${waited}s"

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
    aws s3 cp -q "$f" "s3://$CI_BUCKET/artifacts/$BUILD_UUID/perf-log/$(basename "$f")"
  done
fi
if [ -d "$SKILL/dev/ci-report" ]; then aws s3 cp -q --recursive "$SKILL/dev/ci-report" "s3://$CI_BUCKET/artifacts/$BUILD_UUID/report/"; fi

[ "$rc" -eq 0 ] || { echo "== gate RED - no record, nothing pushed"; exit "$rc"; }

echo "== record: verified/$tree.json ($CI_SCOPE)"
printf '{"tree":"%s","build_id":"%s","project":"%s","scope":"%s","utc":"%s","main":"%s","work":"%s","target":"%s"}\n' \
  "$tree" "$CODEBUILD_BUILD_ID" "$MODE" "$CI_SCOPE" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$main_sha" "$GIT_SHA" "$MAKE_TARGET" > /tmp/verified.json
aws s3 cp -q /tmp/verified.json "s3://$CI_BUCKET/verified/$tree.json"

if [ "$MODE" = merge ]; then
  echo "== push: HEAD -> main (fast-forward only)"
  git push origin HEAD:main || { echo "main moved; re-run (the push was not a fast-forward - nothing landed)"; exit 1; }
  git push -q origin --delete "$MAILBOX" || echo "(mailbox $MAILBOX not deleted - harmless)"
  echo "== landed $(git rev-parse HEAD) on main"
fi
echo "== done"
