# `l7r/diagram/ci/` - the CodeBuild dispatcher (feature 130)

**Load this when:** a remote run refused and you want to know why, you are changing when a paid
run may start, or you are touching the buildspecs. The usage-level answer is one command:
`make ci-status` prints every condition and its reason, free, with no AWS call on a DIRECT route.

Every remote run costs money (`RATE_PER_MIN` = **$0.08 per build-minute** on `BUILD_GENERAL1_XLARGE`,
in [`config.py`](config.py) - mirrored in exactly one other place, the `gm-assistant-ci-monthly-alert`
Lambda's `RATE_PER_MIN` environment variable; change both together). So the GM's rule for this
package is stricter than for any other: *"all of the situations in which we absolutely, positively
do not want to run anything on AWS"* come first, and the speedup second.

## The modules

| module | what it is for |
|---|---|
| [`config.py`](config.py) | the constants (rate, project names, park timeout, estimates) and `load_secrets()` - the ONLY module that knows the account's names; secrets resolve from `$DIAGRAM_SECRETS`, the tree's root, main's root, then gm-assistant's `webapp/development-secrets.ini` |
| [`delta.py`](delta.py) | the Delta: what OUR commits changed since the merge base with `origin/main` (R1), and `is_engine()` - **the one list** of engine paths (FR-008): `l7r/**/*.py`, `tests/**`, `pool/*.gen.py`, `pool/*.json` - the code the tests exercise, and nothing that merely shapes how the gate runs (GM 2026-08-25); `tests/ci/test_delta.py` pins every path kind. Also `engine_key()`, the verification key |
| [`state.py`](state.py) | the VerificationState in `.git/verification-state.json`: the last local check, its target, and the content hash of the engine's Python at that moment (gate-stamp's hash, imported not reimplemented) |
| [`features.py`](features.py) | FR-011: the gated merge needs a named feature (`SPECIFY_FEATURE` / `.specify/feature.json`) with no open task and a FAITHFUL spec |
| [`decision.py`](decision.py) | `decide()`: every condition evaluated and printed even after one fails; the verdict is the first failure, SKIP-VERIFIED, or DISPATCH. FR-027's scope rule lives here |
| [`door.py`](door.py) | the build-side FULL door (R11): only a committed `permitted` entry whose commit is an ancestor of HEAD and not of `origin/main` opens the full scope; never an environment variable |
| [`runlog.py`](runlog.py) | the remote run-log entry (`where: codebuild`, build id, minutes, cost) and month-to-date spend summed from LOCAL entries (never Cost Explorer) |
| [`dispatch.py`](dispatch.py) | the sequence, and the boto3 boundary behind a small protocol - every external call injected so the suite drives it against RECORDED responses (`tests/ci/fixtures/`) |
| [`__main__.py`](__main__.py) | `status | check | merge | image | state | door | remote-spend`, `assert_via_make` at the top |

## The five conditions, and the GM's words each rests on

1. **route-is-gated** - our delta touches engine code. *"if we make any updates that are only outside
   of the diagram skill, then we do not want to run anything on AWS ... even if the diagram
   documentation was touched, but not the code itself, then we should not rerun the tests."* The
   delta is what THIS clone's commits changed, *"paying careful attention to make sure it is
   actually our work and not the result of what we have merged from main into our branch."*
2. **feature-complete** (merge only) - a named spec-kit feature with no open task and a FAITHFUL
   spec. *"I don't think we want things to land on Maine if the feature is incomplete ... Anything
   involving the diagram skill is sufficiently complicated to require a spec kid feature."*
3. **green-local-since-edit** - the last recorded verification is a green local target against
   exactly this code. *"make done could check whether the last thing that was run was an
   unsuccessful make done, in which case it should just short circuit immediately and refuse to
   run without even dispatching to AWS."* A source edit after the green run also refuses (the
   Assumptions reading in the spec: the green run vouched for different code).
4. **tree-not-already-verified** - a green build already verified the ENGINE CONTENT the merge
   would produce, so no second build. *"we can keep track of whether the commit hash that will land
   on main has already had a successful remote run ... This saves both time and money."* Keyed by
   the engine key (`delta.engine_key`: a hash over the engine paths' blobs in the merge tree),
   not by the commit and - since 2026-08-25 - not by the whole tree either: a docs edit after a
   green build keeps the verification (the first day's tree key threw one away, $0.64).
   And a green LOCAL `make done` on exactly this engine content counts too, when main adds no
   engine content to the merge (GM 2026-08-25): the remote reference gate is the same `make done`
   plus the merge, so with nothing new from main it would only re-prove a verdict in hand. A build
   runs when main moved on engine paths since your merge base, or for FULL / an operation.
5. **breaker-not-tripped** - the monthly hard stop's deny policy; discovered at `start_build`,
   reported with the detach command (FR-021).

## The sequence (every remote target)

    conditions -> lint/format/types locally -> push mailbox, start_build (build PARKS at wait-go)
      -> make reference locally -> red: stop_build(OUR id) | green: put go/<id> -> stream -> record

The build parks for at most `PARK_TIMEOUT_S` (120 s, ~$0.16) if the dispatcher dies (FR-036). A
started build that is stopped costs its partial minute; a queued one costs nothing. Only the id
this dispatcher got back is ever stopped - nothing on the AWS side is shared between sessions;
the merge project's single slot serializes merges, and the local ritual lock is the only shared
local state.

## What travels to the build, and how

The projects hold a placeholder buildspec. The dispatcher passes the repository's own
[`buildspec/<mode>.yml`](../../../../../buildspec/) as `buildspecOverride`, so the build runs
whatever the tree under test says - reviewable in a diff. Both YAMLs call
[`buildspec/run.sh`](../../../../../buildspec/run.sh); `MODE` (check | merge) is the only
difference: merge fast-forward-pushes the verified result to GitHub `main` and deletes the mailbox.
The custom image (`Dockerfile.ci`, `make ci-image`) is used once its marker `image/latest.txt`
exists in the bucket; until then the build bootstraps Python 3.14 + resvg on the stock image
(measured in `timings.md`).

## The threat model

Same shape as feature 127's: **a session that wants the paid run and should not have it**, and
that can present any of these as diligence -

- dispatching a docs-only or merged-in-from-main delta (condition 1 - the delta is computed, never declared);
- merging an unfinished feature because the gate is green (condition 2);
- `make done` again straight after a red one, with an edit in between (condition 3, the GM's
  named case);
- answering the FULL prompt from inside a build via an environment variable (the door reads only a
  committed entry - a forgery is a tracked-file diff);
- a session answering its own prompt through a pseudo-terminal: `spec-fidelity` ruled this an
  EXCEPTION on 2026-08-25, and the GM authorized it in their own words later that day. A session
  that answers MUST record in the reason that it did, quoting the authorization - the entry is
  how `make audit` tells a session's answer from the GM's (the reviewer's aside: an actor field).

## The `verified/` write path (R8, FR-016) - closed 2026-08-25

The bucket policy in [`buildspec/verified-deny-policy.json`](../../../../../buildspec/verified-deny-policy.json)
denies `s3:PutObject` under `verified/` to every principal except `gm-assistant-codebuild-role`.
Applied with the admin key on 2026-08-25 and verified: the session key gets `AccessDenied` there and
still writes `go/`. Only a build can write a verified record.
