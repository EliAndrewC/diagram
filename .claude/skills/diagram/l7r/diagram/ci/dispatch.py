"""The dispatch sequence, and the AWS boundary behind a small protocol.

THE SEQUENCE (FR-033..FR-037, the GM's five arrows), the same for every remote target:

    0. conditions          free   delta, feature (merge only), state, verified record  -> refuse / skip
    1. lint+format+types   ~5 s   fail -> stop, NOTHING has touched AWS
    2. push mailbox, start_build (the build PARKS at wait-go)          provisioning overlaps step 3
    3. make reference      ~26 s  fail -> stop_build(OUR id), state failed-gate, no go signal
    4. put go/<build-id>          the build proceeds: merge main, gate, record, (merge: push main)
    5. stream the log; exit with the build's status; run-log entry with minutes and cost

EVERYTHING EXTERNAL IS INJECTED - `sh` for git/make, `client` for AWS, `sleep` for the clock - so
the suite drives the whole sequence against SAVED responses (Principle X's fixture rule, never a
transport mock) and can assert the two things that matter most: that no `start_build` happens on a
refusal, and that `stop_build` is only ever called with the id this dispatcher got back.

WHY THE BUILDSPEC TRAVELS WITH THE CALL. The projects were created with `NO_SOURCE` and a
placeholder inline buildspec. Rather than editing the projects (a state nobody can review), the
dispatcher passes the repository's own `buildspec/<mode>.yml` as `buildspecOverride`, so the build
runs whatever the tree under test says - reviewable in a diff, like every other guard here.
"""

from __future__ import annotations

import math
import os
import subprocess
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from l7r.diagram import switches
from l7r.diagram.ci import config, decision, door, features, imagecheck, runlog, state
from l7r.diagram.ci.delta import compute_delta, engine_key

ShResult = tuple[int, str]
Sh = Callable[[list[str], Path, Mapping[str, str] | None], ShResult]


class AwsClient(Protocol):
    def start_build(self, **kw: Any) -> dict[str, Any]: ...
    def batch_get_builds(self, ids: list[str]) -> dict[str, Any]: ...
    def stop_build(self, id: str) -> dict[str, Any]: ...
    def get_log_events(self, group: str, stream: str, token: str | None) -> dict[str, Any]: ...
    def put_object(self, bucket: str, key: str, body: bytes) -> None: ...
    def get_object(self, bucket: str, key: str) -> bytes | None: ...
    def list_prefix(self, bucket: str, prefix: str) -> list[str]: ...
    def delete_object(self, bucket: str, key: str) -> None: ...


def registered_operation(target: str | None) -> str | None:
    """The REGISTERED name of an operation target, or None when there is no operation (feature 177).

    **This exists so `cache_location` cannot be keyed on a free-form string.** `__main__.py` validates
    only `a.target.split()[0]` against `_invocation.OPERATIONS` and then passes the WHOLE target on as
    `ctx.operation`, arguments and all - `make_target` returns it verbatim as `MAKE_TARGET` because
    `run.sh` word-splits it on purpose. So `cohort SEEDS=8` and `cohort SEEDS=9` are both legal and
    distinct, and a cache location built from `ctx.operation` would grow one S3 object per argument
    spelling: the GM's named failure (*"uploading many megabytes worth of content to Amazon S3 on
    every run and then never cleaning it up"*), reintroduced by the fix for a different defect. The
    head is drawn from the registry instead, so the value can only be one of a finite set of names.

    An unregistered head returns None - the run then shares the scope's location, exactly as it did
    before. That is the safe direction: `__main__` has already refused an unregistered target before
    any dispatch, so this branch is reachable only from a caller that built a Context by hand, and
    the worst it can do is decline to partition."""
    if not target:
        return None
    from l7r.diagram._invocation import OPERATIONS

    head = target.split()[0]
    return head if head in {name for name, _cost in OPERATIONS.values()} else None


def cache_location(bucket: str, project: str, scope: str, operation: str | None = None) -> str:
    """Where CodeBuild keeps the generation cache for this project, scope and operation (175, 177).

    **THE OBJECT COUNT IS BOUNDED BY CONSTRUCTION, and that is the whole point of this function.**
    CodeBuild writes one archive per cache `location`, so keying on (project, scope) means the cache
    can ever hold `2 projects x {full, reference}` = FOUR objects, no matter how many builds, commits
    or branches run through it. The GM named the opposite as the failure to avoid: *"if we were
    uploading many megabytes worth of content to Amazon S3 on every run and then never cleaning it
    up, then that would be bad."* A location containing the commit SHA would do exactly that - one
    object per commit, for ever - so it is forbidden by spec FR-005 and asserted against in
    `tests/tooling/ci/test_cache.py`.

    **The scope is in the key rather than shared** because the two scopes want different contents: a
    reference build reads the roll cache (`make reference` calls `rollcache.report`) while a FULL
    build neither reads nor writes it (`rollcache.bypassed()` is true under `L7R_TESTS_FULL=1` and
    `obtain` returns before storing). Sharing one location would have a reference build's `rolls/`
    ride along in every FULL restore, unread - 54 MB on the laptop that measured it.

    **THE OPERATION IS IN THE KEY TOO (feature 177), and it must be the REGISTERED name.** Measured
    2026-09-03: the green reference gate and both `TARGET=tripwire` builds of 2026-08-31 all wrote to
    `cache/gm-assistant-check/reference`, because an operation's `ctx.scope` stays `reference` and
    only `CI_SCOPE` becomes `operation` - so a tripwire's cache overwrote the gate's and the bucket
    held ONE cache object where 175's D2 expected up to four. The blast radius is performance alone:
    the gencache key is content-derived (175's A2), so a foreign entry can only MISS, never serve a
    wrong answer. The ceiling stays finite - `projects x (scopes + registered expensive operations)` -
    because `registered_operation` will not pass anything the registry does not name; see its
    docstring for why keying on the raw target would not.

    A lifecycle rule on the bucket expires these; see `specs/175-warm-the-remote-build/` D3 and
    feature 177's D6, which took `verified/` out of the catch-all's reach. The bucket is the CI bucket
    that already holds the mailbox and go-signals, so there is one bucket, one policy, and one place
    to look."""
    return f"{bucket}/cache/{project}/{scope}" + (f"/{operation}" if operation else "")


class AccessDenied(Exception):
    """An AWS AccessDeniedException, with the operation it named."""

    def __init__(self, operation: str, message: str) -> None:
        super().__init__(message)
        self.operation = operation


def default_sh(args: list[str], cwd: Path, env: Mapping[str, str] | None) -> ShResult:
    merged = dict(os.environ)
    if env:
        merged.update(env)
    p = subprocess.run(args, cwd=str(cwd), env=merged, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


class Boto3Client:  # pragma: no cover - the real transport; its response SHAPES are what tests/tooling/ci/fixtures/ record
    """The real boundary. Constructed only by `__main__`, never by a test."""

    def __init__(self, secrets: config.Secrets) -> None:
        import boto3  # local: the suite never imports it, and the build image does not carry it
        import botocore.exceptions

        self._errors = botocore.exceptions
        ses = boto3.Session(aws_access_key_id=secrets.access_key_id, aws_secret_access_key=secrets.secret_access_key, region_name=secrets.region)
        self._cb = ses.client("codebuild")
        self._logs = ses.client("logs")
        self._s3 = ses.client("s3")

    def _wrap(self, fn: Callable[[], Any], operation: str) -> Any:
        try:
            return fn()
        except self._errors.ClientError as e:  # pragma: no cover - the real transport; the shape is fixture-tested
            if e.response.get("Error", {}).get("Code") == "AccessDeniedException":
                raise AccessDenied(operation, str(e)) from e
            raise

    def start_build(self, **kw: Any) -> dict[str, Any]:
        return dict(self._wrap(lambda: self._cb.start_build(**kw), "codebuild:StartBuild"))

    def batch_get_builds(self, ids: list[str]) -> dict[str, Any]:
        return dict(self._cb.batch_get_builds(ids=ids))

    def stop_build(self, id: str) -> dict[str, Any]:
        return dict(self._cb.stop_build(id=id))

    def get_log_events(self, group: str, stream: str, token: str | None) -> dict[str, Any]:
        kw: dict[str, Any] = {"logGroupName": group, "logStreamName": stream, "startFromHead": True}
        if token:
            kw["nextToken"] = token
        try:
            return dict(self._logs.get_log_events(**kw))
        except self._errors.ClientError as e:  # pragma: no cover - the stream does not exist until the build starts writing
            if e.response.get("Error", {}).get("Code") == "ResourceNotFoundException":
                return {"events": [], "nextForwardToken": token}
            raise

    def put_object(self, bucket: str, key: str, body: bytes) -> None:
        self._wrap(lambda: self._s3.put_object(Bucket=bucket, Key=key, Body=body), "s3:PutObject")

    def get_object(self, bucket: str, key: str) -> bytes | None:
        try:
            return bytes(self._s3.get_object(Bucket=bucket, Key=key)["Body"].read())
        except self._errors.ClientError as e:  # pragma: no cover - the miss is the common case and is fixture-tested
            if e.response.get("Error", {}).get("Code") in ("NoSuchKey", "404"):
                return None
            raise

    def list_prefix(self, bucket: str, prefix: str) -> list[str]:
        r = self._s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        return [str(o["Key"]) for o in r.get("Contents", [])]

    def delete_object(self, bucket: str, key: str) -> None:
        self._s3.delete_object(Bucket=bucket, Key=key)


@dataclass
class Context:
    root: Path
    skill: Path
    mode: str  # merge | check | measure | image
    scope: str = "reference"  # reference | full
    operation: str | None = None  # ci-check TARGET=<expensive op>
    compute: str = config.COMPUTE_TYPE  # ci-check COMPUTE=BUILD_GENERAL1_2XLARGE: the scaling measurement (T028)
    no_go: bool = False  # ci-check NO_GO=1: never release the parked build - proves FR-036's self-abort, costs the park ceiling
    secrets: config.Secrets | None = None
    client: AwsClient | None = None
    sh: Sh = default_sh
    sleep: Callable[[float], None] = time.sleep
    out: Callable[[str], None] = print
    stream_poll_s: float = config.STREAM_POLL_S
    events: list[str] = field(default_factory=list)  # what happened, in order - the audit and the tests read it


@dataclass
class Outcome:
    rc: int
    verdict: str
    build_id: str = ""
    result: str = ""
    minutes: float = 0.0


def clone_name(root: Path) -> str:
    return root.name


def mailbox(root: Path) -> str:
    return config.MAILBOX_PREFIX + clone_name(root)


def make_target(ctx: Context) -> str:
    """What a remote build actually RUNS.

    THIS RETURNS `soak`, NOT `done` (GM 2026-09-05), and that is the whole point of the change: a
    remote run now does the tier the laptop SKIPPED instead of repeating the tier it just finished.

    WHAT IT USED TO DO, and why that stopped being worth paying for. It returned `done` - the same
    command the local gate runs - on the theory that the remote merges the LATEST main in first, so it
    tests a tree nobody has tested. That property was real and is now vestigial: `sync-in` merges main
    into every clone on every message, so the trees are almost always identical, and condition 5
    (`tree-not-already-verified`) correctly declines to spend money when they are. The record is
    unambiguous - **every `ci-merge` since the local short-circuit landed on 2026-08-25 has been
    SKIP-VERIFIED, four for four, and the six paid ones all predate it.**

    Feature 174 then closed the other half by accident: making the coverage floors unconditional meant
    `COV_FLOORS=1` on a plain `make done`, and that same switch sets `L7R_TESTS_FULL` and turns every
    deselection off - so the four-seed cohort meant to be the wide, farmed-out tier began rolling on
    every local gate. Between them, a remote build had nothing left to add.

    WHAT IS GIVEN UP, stated rather than discovered later: the remote is no longer a MERGE QUEUE. It
    does not re-run the gate against your-work-merged-with-latest-main, so a conflict that is textually
    clean but semantically broken is no longer caught by a machine before it lands. That was the
    original purpose of this whole route (feature 130). It is accepted because it has never once fired,
    and because the alternative - keeping a paid route alive for a property that has not triggered in
    ten days of daily merges - is the thing this project calls a guess dressed as a finding.

    DECLINED, and why: running BOTH (`done` then `soak`) would restore the merge-queue property and
    was rejected because it reintroduces exactly the duplication this change exists to remove, at
    roughly double the cost, for a property measured at zero firings. Pointing the remote at
    `done FULL=1` was rejected for a stronger reason - since feature 174 it runs the same tests as
    `done`, adding only the perf bookends.

    The soak suite is EMPTY today and `make soak` REFUSES rather than reporting a vacuously green
    build, so this cannot quietly become a no-op. Remote is off; `tests/soak/CLAUDE.md` carries the
    membership rule and the honest statement of when the tier earns its keep.
    """
    if ctx.operation:
        return ctx.operation
    # The scope still selects, so a FULL soak stays available the moment the suite has anything in it.
    return "soak FULL=1" if ctx.scope == "full" else "soak"


def would_be_tree(ctx: Context) -> tuple[str | None, str]:
    """The tree the merge would produce (R2), or None with the conflict text."""
    rc, out = ctx.sh(["git", "merge-tree", "--write-tree", "origin/main", "HEAD"], ctx.root, None)
    if rc != 0:
        return None, out.strip()
    return out.strip().splitlines()[0].strip(), ""


def verified_lookup(ctx: Context, tree: str | None) -> decision.VerifiedRecord | None:
    """By the ENGINE KEY of the would-be tree (delta.engine_key), never by the whole tree."""
    if tree is None or ctx.client is None or ctx.secrets is None:
        return None
    body = ctx.client.get_object(ctx.secrets.ci_bucket, f"verified/{engine_key(ctx.root, tree)}.json")
    if body is None:
        return None
    import json

    d = json.loads(body.decode("utf-8"))
    return decision.VerifiedRecord(tree=str(d.get("tree", tree)), build_id=str(d.get("build_id", "?")), scope=str(d.get("scope", "reference")), utc=str(d.get("utc", "")))


def remote_off_reason(skill: Path) -> str | None:
    """None while remote is on; otherwise the text the `remote-enabled` condition carries (feature 132)."""
    sw = switches.read(skill)
    if not sw.remote_off:
        return None
    a = sw.remote
    return f"remote is OFF since {a.utc} by {a.who or '?'}: {a.why} - nothing dispatches; `make ci-on REASON=...` releases it"


def billed_minutes(build: dict[str, Any]) -> float:
    """CodeBuild bills every phase from PROVISIONING on, rounded up to the minute."""
    secs = sum(int(p.get("durationInSeconds", 0)) for p in build.get("phases", []) if p.get("phaseType") not in ("SUBMITTED", "QUEUED", "COMPLETED"))
    return float(max(1, math.ceil(secs / 60))) if secs else 0.0


def status_text(ctx: Context) -> tuple[str, decision.DispatchDecision]:
    """`make ci-status`: the whole picture, no AWS call unless a lookup is possible and the route is GATED."""
    ctx.sh(["git", "fetch", "-q", "origin"], ctx.root, None)
    delta = compute_delta(ctx.root)
    st = state.read(ctx.root)
    now = state.current_hash(ctx.root)
    feat = features.feature_status(ctx.root, features.active_feature(ctx.root))
    tree, conflict = would_be_tree(ctx)
    verified = verified_lookup(ctx, tree) if delta.route == "GATED" else None
    # A GREEN LOCAL `make done` VOUCHES FOR THE ENGINE CONTENT IT TESTED (GM 2026-08-25, superseding
    # the spec's edge case "a green local done still dispatches"). The remote reference-scope gate
    # is the same `make done`; what it adds is the merge with the LATEST main - and when main has
    # no engine changes since the merge base, the would-be merge's engine key equals what the local
    # gate just tested, so a build would re-prove a verdict already in hand. A build runs only when
    # main moved on engine paths (the genuine "second check is invalid" case), or for FULL / an
    # operation, which the laptop is not asked to run.
    if verified is None and tree is not None and st is not None and st.event == state.GREEN and st.target == "done" and st.engine_key and st.engine_key == engine_key(ctx.root, tree):
        verified = decision.VerifiedRecord(tree=tree, build_id=f"local:make-done@{st.commit}", scope="reference", utc=st.utc)
    d = decision.decide(
        delta,
        st,
        now,
        verified,
        None,
        ctx.mode if ctx.mode in (decision.MERGE, decision.CHECK) else decision.CHECK,
        feat,
        ctx.scope,
        runlog.month_to_date(ctx.skill),
        ctx.operation,
        remote_off_reason(ctx.skill),
        ctx.mode == decision.MEASURE,
    )
    text = decision.render(d, ctx.mode, ctx.scope)
    head = [f"delta: merge-base {delta.base[:12]}, {len(delta.files)} file(s), route {delta.route}", f"state: {state.describe(st, now)}"]
    head.append(
        f"would-be tree: {tree[:12]}, engine key {engine_key(ctx.root, tree)[:12]} (what a verified record is keyed by)"
        if tree
        else f"would-be tree: MERGE CONFLICT with origin/main - merge main locally, resolve, commit:\n  {conflict[:400]}"
    )
    return "\n".join(head) + "\n" + text, d


def run(ctx: Context) -> Outcome:
    """The five arrows. Returns the exit status the make target exits with."""
    t0 = time.time()
    assert ctx.client is not None and ctx.secrets is not None, "run() needs a client and secrets (status_text() does not)"
    text, d = status_text(ctx)
    ctx.out(text)
    tree, conflict = would_be_tree(ctx)
    if tree is None:
        ctx.out("ci: REFUSED - the merge with the latest main conflicts locally; nothing dispatched (a paid build would only have told you the same)")
        return Outcome(rc=1, verdict="REFUSE(merge-conflict)")
    if ctx.scope == "full":
        ok, why = door.check(ctx.root, ctx.skill)
        ctx.out(f"ci: FULL scope - {why}")
        if not ok:
            return Outcome(rc=1, verdict="REFUSE(full-not-authorized)")
    if not d.dispatches:
        ctx.out(f"ci: {d.verdict} - nothing dispatched" if not d.skip_verified else "ci: SKIP-VERIFIED - no build; the caller pushes directly")
        if d.skip_verified:
            rec = next(c for c in d.conditions if c.name == "tree-not-already-verified")
            runlog.write_remote(ctx.skill, f"ci-{ctx.mode}", ctx.scope, int(time.time() - t0), "skip-verified", rec.why.split(" by ")[-1].split(" ")[0], 0.0, rec.why)
        return Outcome(rc=0 if d.skip_verified else 1, verdict=d.verdict)

    # 1. the cheap local checks - nothing about AWS has happened yet (FR-033)
    rc, out = ctx.sh(["make", "--no-print-directory", "lint", "format", "typecheck"], ctx.skill, None)
    ctx.events.append(f"lint:{rc}")
    if rc != 0:
        ctx.out(out)
        ctx.out("ci: lint/format/types FAILED locally - nothing dispatched")
        return Outcome(rc=1, verdict="REFUSE(lint)")
    ctx.out("ci: lint, format, types clean - starting the build (parked) while the reference check runs locally")

    # 2. mailbox + start, parked
    box = mailbox(ctx.root)
    rc, out = ctx.sh(
        ["git", "push", "-q", "--force", f"https://github.com/{config.GITHUB_REPO}", f"HEAD:refs/heads/{box}"],
        ctx.root,
        {"GIT_ASKPASS": str(ctx.root / "scripts" / "git-askpass-token.sh"), "GITHUB_TOKEN": ctx.secrets.github_pat, "GIT_TERMINAL_PROMPT": "0"},
    )
    ctx.events.append(f"push:{rc}")
    if rc != 0:
        ctx.out(out)
        ctx.out(f"ci: could not push the mailbox branch {box} to GitHub - nothing dispatched")
        return Outcome(rc=1, verdict="REFUSE(mailbox-push)")
    rc, sha = ctx.sh(["git", "rev-parse", "HEAD"], ctx.root, None)
    project = config.PROJECT_MERGE if ctx.mode == decision.MERGE else config.PROJECT_CHECK
    spec_path = ctx.root / "buildspec" / f"{ctx.mode}.yml"
    env = [
        {"name": "GIT_SHA", "value": sha.strip(), "type": "PLAINTEXT"},
        {"name": "MAILBOX", "value": box, "type": "PLAINTEXT"},
        {"name": "MAKE_TARGET", "value": make_target(ctx), "type": "PLAINTEXT"},
        {"name": "CI_MODE", "value": ctx.mode, "type": "PLAINTEXT"},
        {"name": "CI_SCOPE", "value": "operation" if ctx.operation else ctx.scope, "type": "PLAINTEXT"},
        {"name": "COMPUTE_TYPE", "value": ctx.compute, "type": "PLAINTEXT"},
        {"name": "PARK_TIMEOUT_S", "value": str(config.PARK_TIMEOUT_S), "type": "PLAINTEXT"},
        # the build's perf-gate pairs bookends by feature number: it must be THIS feature, not the highest specs/ dir
        {"name": "SPECIFY_FEATURE", "value": features.active_feature(ctx.root) or "", "type": "PLAINTEXT"},
    ]
    # THE CUSTOM IMAGE IS USED ONLY ONCE IT EXISTS: `make ci-image` writes image/latest.txt to the
    # bucket when the push to ECR succeeds. Without it the build runs on the stock image and
    # bootstraps (buildspec/run.sh) - slower, measured, never blocked on a step only a terminal can
    # take. Measured the hard way: the first real dispatch (build 6913a24d, 2026-08-25) carried an
    # unconditional override and died in PROVISIONING with "manifest unknown" - one billed minute.
    image_kw: dict[str, Any] = {}
    marker = ctx.client.get_object(ctx.secrets.ci_bucket, "image/latest.txt")
    if marker is not None:
        image_kw = {"imageOverride": f"{ctx.secrets.ecr_image}:latest", "imagePullCredentialsTypeOverride": "SERVICE_ROLE"}
    ctx.events.append("image:custom" if image_kw else "image:stock")
    # IS THE PUSHED IMAGE STILL BUILT FROM THIS TREE'S RECIPE? (feature 175). A stale image cost three
    # days of a broken gated push route in 2026-08, and nothing could say so: the image is a DERIVED
    # ARTIFACT in ECR with no link back to the files it came from. The marker already records the
    # commit it was built at, so the answer is one `git diff` over the recipe and the lockfiles.
    # WARNS, never refuses - see `imagecheck` for why a block would be worse than the disease.
    if marker is not None:
        built_at = imagecheck.marker_commit(marker.decode("utf-8", "replace"))
        if built_at:
            rc, changed = ctx.sh(["git", "diff", "--name-only", built_at, "HEAD", "--", *imagecheck.IMAGE_INPUTS], ctx.root, None)
            line = imagecheck.staleness_line(imagecheck.stale_inputs(changed.split())) if rc == 0 else None
            if line:
                ctx.out(f"ci: {line}")
                ctx.events.append("image:stale")
    # THE CACHE TRAVELS WITH THE CALL, for the same reason the buildspec does (feature 175): a cache
    # configured on the PROJECT is state nobody can review, while an override is reviewable in a diff.
    op_key = registered_operation(ctx.operation)
    cache_kw: dict[str, Any] = {"cacheOverride": {"type": "S3", "location": cache_location(ctx.secrets.ci_bucket, project, ctx.scope, op_key)}}
    ctx.events.append(f"cache:{ctx.scope}" + (f"/{op_key}" if op_key else ""))
    try:
        started = ctx.client.start_build(
            projectName=project,
            buildspecOverride=spec_path.read_text(encoding="utf-8"),
            environmentVariablesOverride=env,
            computeTypeOverride=ctx.compute,
            **image_kw,
            **cache_kw,
        )
    except AccessDenied as e:
        ctx.events.append("start_build:denied")
        if "StartBuild" in e.operation or "StartBuild" in str(e):
            ctx.out("ci: REFUSED - the monthly hard stop has TRIPPED (FR-021): IAM policy gm-assistant-ci-circuit-breaker is attached to user gm-assistant-ci and denies codebuild:StartBuild.")
            ctx.out("    To re-enable (admin key): aws iam detach-user-policy --user-name gm-assistant-ci --policy-arn arn:aws:iam::130071571821:policy/gm-assistant-ci-circuit-breaker")
            return Outcome(rc=1, verdict="REFUSE(breaker-tripped)")
        ctx.out(f"ci: AWS refused {e.operation}: {e}")  # pragma: no cover - a different denial, reported as itself
        return Outcome(rc=1, verdict="REFUSE(aws-denied)")  # pragma: no cover
    build_id = str(started["build"]["id"])
    ctx.events.append(f"start_build:{build_id}")
    ctx.out(f"ci: build {build_id} started on {project} / {ctx.compute} (parked at wait-go, {config.PARK_TIMEOUT_S} s ceiling)")

    # 3. the reference settlement(s), locally - `make reference` runs every tier's reference map
    rc, out = ctx.sh(["make", "--no-print-directory", "reference"], ctx.skill, None)
    ctx.events.append(f"reference:{rc}")
    if rc != 0:
        ctx.out(out)
        ctx.client.stop_build(build_id)
        ctx.events.append(f"stop_build:{build_id}")
        state.write(ctx.root, state.FAILED, f"ci-{ctx.mode}")
        b = ctx.client.batch_get_builds([build_id])["builds"][0]
        mins = billed_minutes(b)
        rate = config.RATES.get(ctx.compute, config.RATE_PER_MIN)
        runlog.write_remote(
            ctx.skill, f"ci-{ctx.mode}", ctx.scope, int(time.time() - t0), "aborted-local-reference", build_id, mins, "reference settlement red locally; parked build stopped", rate, ctx.compute
        )
        ctx.out(f"ci: reference settlement RED locally - build {build_id} stopped ({mins:.0f} billed min, ~${mins * rate:.2f})")
        return Outcome(rc=1, verdict="ABORTED(local-reference)", build_id=build_id, result="aborted-local-reference", minutes=mins)

    # 4. release - unless this run exists to prove that a build nobody releases aborts itself (FR-036)
    if ctx.no_go:
        ctx.events.append("go:withheld")
        ctx.out(f"ci: NO_GO=1 - the go signal is WITHHELD; the build must abort itself after {config.PARK_TIMEOUT_S} s")
    else:
        ctx.client.put_object(ctx.secrets.ci_bucket, f"go/{build_id.split(':')[-1]}", b"go")  # the build polls go/<uuid> - the id's project prefix is not part of the key
        ctx.events.append("go")
        ctx.out("ci: reference settlement clean - build released")

    # 5. stream, then settle
    build = stream(ctx, build_id)
    result = str(build.get("buildStatus", "?"))
    mins = billed_minutes(build)
    ok = result == "SUCCEEDED"
    # a build that died before wait-go (provisioning, a clone failure) never consumed its signal
    if ctx.client.get_object(ctx.secrets.ci_bucket, f"go/{build_id.split(':')[-1]}") is not None:
        ctx.client.delete_object(ctx.secrets.ci_bucket, f"go/{build_id.split(':')[-1]}")
        ctx.events.append("go:cleaned")
    if not ok:
        state.write(ctx.root, state.FAILED, f"ci-{ctx.mode}")
    fetched = fetch_artifacts(ctx, build_id)
    rate = config.RATES.get(ctx.compute, config.RATE_PER_MIN)
    runlog.write_remote(ctx.skill, f"ci-{ctx.mode}", "operation" if ctx.operation else ctx.scope, int(time.time() - t0), result, build_id, mins, make_target(ctx), rate, ctx.compute)
    ctx.out(f"ci: build {build_id} {result} - {mins:.0f} billed min on {ctx.compute}, ~${mins * rate:.2f}" + (f"; {len(fetched)} artifact file(s) fetched" if fetched else ""))
    return Outcome(rc=0 if ok else 1, verdict="DISPATCHED", build_id=build_id, result=result, minutes=mins)


def stream(ctx: Context, build_id: str) -> dict[str, Any]:
    """Poll the build and print its log as it is written (R5). Returns the final build record."""
    assert ctx.client is not None and ctx.secrets is not None
    token: str | None = None
    phase = ""
    while True:
        build = dict(ctx.client.batch_get_builds([build_id])["builds"][0])
        cur = str(build.get("currentPhase", ""))
        if cur != phase:
            ctx.out(f"ci: [{cur}]")
            phase = cur
        logs = build.get("logs", {}) or {}
        stream_name = str(logs.get("streamName") or build_id.split(":")[-1])
        group = str(logs.get("groupName") or ctx.secrets.log_group)
        page = ctx.client.get_log_events(group, stream_name, token)
        for ev in page.get("events", []):
            ctx.out("  | " + str(ev.get("message", "")).rstrip("\n"))
        token = str(page.get("nextForwardToken") or token or "") or None
        if build.get("buildStatus") != "IN_PROGRESS":
            # DRAIN: the build is over but CloudWatch may hold more pages than the one just read - the
            # first real failure (build 93af6342) showed a log that jumped from wait-go to POST_BUILD
            # with the failing command's output missing, because the poll returned as soon as the
            # status was terminal. A page with no events means the stream is exhausted.
            for _ in range(50):
                page = ctx.client.get_log_events(group, stream_name, token)
                events = page.get("events", [])
                for ev in events:
                    ctx.out("  | " + str(ev.get("message", "")).rstrip("\n"))
                token = str(page.get("nextForwardToken") or token or "") or None
                if not events:
                    break
            return build
        ctx.sleep(ctx.stream_poll_s)


def fetch_artifacts(ctx: Context, build_id: str) -> list[Path]:
    """FULL perf snapshots go to dev/perf-log/; an operation's report to dev/ci-artifacts/<uuid>/."""
    assert ctx.client is not None and ctx.secrets is not None
    uuid = build_id.split(":")[-1]
    prefix = f"artifacts/{uuid}/"
    got: list[Path] = []
    for key in ctx.client.list_prefix(ctx.secrets.ci_bucket, prefix):
        rel = key[len(prefix) :]
        if not rel:
            continue
        dest = ctx.skill / "dev" / "perf-log" / rel.split("/", 1)[1] if rel.startswith("perf-log/") and "/" in rel else ctx.skill / "dev" / "ci-artifacts" / uuid / rel
        body = ctx.client.get_object(ctx.secrets.ci_bucket, key)
        if body is None:
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(body)
        got.append(dest)
    return got


def run_image(ctx: Context) -> Outcome:
    """`make ci-image`: one build on the check project that docker-builds Dockerfile.ci and pushes it to ECR."""
    t0 = time.time()
    assert ctx.client is not None and ctx.secrets is not None
    rc, sha = ctx.sh(["git", "rev-parse", "HEAD"], ctx.root, None)
    box = mailbox(ctx.root)
    rc, out = ctx.sh(
        ["git", "push", "-q", "--force", f"https://github.com/{config.GITHUB_REPO}", f"HEAD:refs/heads/{box}"],
        ctx.root,
        {"GIT_ASKPASS": str(ctx.root / "scripts" / "git-askpass-token.sh"), "GITHUB_TOKEN": ctx.secrets.github_pat, "GIT_TERMINAL_PROMPT": "0"},
    )
    if rc != 0:
        ctx.out(out)
        return Outcome(rc=1, verdict="REFUSE(mailbox-push)")
    started = ctx.client.start_build(
        projectName=config.PROJECT_CHECK,
        buildspecOverride=(ctx.root / "buildspec" / "image.yml").read_text(encoding="utf-8"),
        environmentVariablesOverride=[{"name": "GIT_SHA", "value": sha.strip(), "type": "PLAINTEXT"}, {"name": "MAILBOX", "value": box, "type": "PLAINTEXT"}],
        computeTypeOverride="BUILD_GENERAL1_MEDIUM",
        privilegedModeOverride=True,
    )
    build_id = str(started["build"]["id"])
    ctx.events.append(f"start_build:{build_id}")
    build = stream(ctx, build_id)
    result = str(build.get("buildStatus", "?"))
    mins = billed_minutes(build)
    runlog.write_remote(ctx.skill, "ci-image", "image", int(time.time() - t0), result, build_id, mins, "Dockerfile.ci -> ECR")
    ctx.out(f"ci-image: build {build_id} {result} - {mins:.0f} billed min")
    return Outcome(rc=0 if result == "SUCCEEDED" else 1, verdict="DISPATCHED", build_id=build_id, result=result, minutes=mins)
