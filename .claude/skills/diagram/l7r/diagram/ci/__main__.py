"""`python3 -m l7r.diagram.ci <subcommand>` - reached ONLY through `make ci-*` (feature 127).

status [--route]        free: the delta, route, state, verified lookup, month-to-date spend
check  [--full] [--target OP]   the iteration check on gm-assistant-check
merge  [--full]         the merge action's gated route on gm-assistant-merge (sync-with-main.sh calls it)
image                   rebuild the build image (the Makefile prompts first)
state EVENT TARGET      record a verification event (the Makefile calls it after quick/reference/test-file/done)
door                    the build-side FULL door: exit 0 if this tree carries a permitted entry
remote-spend            the audit's "Remote spend" block
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from l7r.diagram._invocation import assert_via_make

# REFUSE unless invoked through this project's make - at the TOP, before any argument is read, so
# a bare `python3 -m l7r.diagram.ci merge` cannot get as far as a network call.
assert_via_make("l7r.diagram.ci", "ci-status  (free)  |  make ci-check  |  make ci-merge  (paid; called by sync-with-main.sh)")

from l7r.diagram import switches  # noqa: E402
from l7r.diagram.ci import config, decision, dispatch, door, runlog, state  # noqa: E402


def _roots() -> tuple[Path, Path]:
    root = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip())
    return root, root / ".claude" / "skills" / "diagram"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="l7r.diagram.ci", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "command", choices=["status", "check", "merge", "image", "state", "door", "remote-spend", "engine-key", "verified-done", "remote-ok", "tooling-green", "tooling-fresh", "cov-scope"]
    )
    ap.add_argument("args", nargs="*")
    ap.add_argument("--full", action="store_true", help="the full sweep (the Makefile has already run the local prompt)")
    ap.add_argument("--target", default=None, help="ci-check only: an expensive operation to run remotely instead of the gate")
    ap.add_argument("--route", action="store_true", help="status only: print just DIRECT or GATED")
    ap.add_argument("--compute", default=config.COMPUTE_TYPE, choices=sorted(config.RATES), help="check only: the compute type, for the scaling measurement (T028)")
    ap.add_argument("--no-go", action="store_true", help="check only: withhold the go signal so the parked build aborts itself (the FR-036 measurement)")
    a = ap.parse_args(argv)
    root, skill = _roots()
    scope = "full" if a.full else "reference"

    if a.command == "state":
        if len(a.args) not in (2, 3) or (len(a.args) == 3 and a.args[2] != "reused"):
            ap.error("state needs EVENT TARGET [reused]")
        st = state.write(root, a.args[0], a.args[1], reused=len(a.args) == 3)
        print(f"verification-state: {st.event} ({st.target}) recorded")
        return 0
    if a.command == "remote-ok":
        # the Makefile's REMOTE_OK line (ci-check, ci-image): the switch's refusal, plus the trail entry
        what = a.args[0] if a.args else "ci-check"
        if switches.check(skill, "remote", what):
            return 0
        est = decision.estimate("reference", 0.0, "image" if what.startswith("ci-image") else (None if what == "ci-check" else "operation"))
        runlog.write_would_have(skill, what, "operation" if what != "ci-check" else "reference", est.minutes, f"remote off: `make {what}` attempted and refused")
        print(f"(recorded as would-have-dispatched, ~{est.minutes:.0f} build-min ~${est.cost_usd:.2f} - `make ci-status` lists these; the period's audit reads them)", file=sys.stderr)
        return 1
    if a.command == "cov-scope":  # the pytest words that trace only the changed engine modules (delta.coverage_scope); nothing changed -> no tracing
        from l7r.diagram.ci.delta import coverage_scope

        mods = coverage_scope(root)
        print(" ".join(["-o", "addopts=--cov=" + mods[0], *[f"--cov={m}" for m in mods[1:]]]) if mods else "-o addopts= --no-cov")
        return 0
    if a.command == "tooling-fresh":  # exit 0 when the tooling is unchanged since the last record - the Makefile then skips collecting tests/tooling
        rec = state.read(root)
        return 0 if rec is not None and rec.tooling and rec.tooling == state.tooling_hash(root) else 1
    if a.command == "tooling-green":
        print(f"tooling: recorded green for {state.record_tooling(root)[:12]} - `make quick` skips the tooling tests until the tooling changes")
        return 0
    if a.command == "verified-done":
        ok, why = state.already_verified(root)
        print(f"make done: {why}")
        return 0 if ok else 1
    if a.command == "door":
        ok, why = door.check(root, skill)
        print(f"bypass-audit: {why}")
        return 0 if ok else 1
    if a.command == "engine-key":
        from l7r.diagram.ci.delta import engine_key, engine_key_worktree

        # `engine-key worktree` is what the gate/review PAIRING keys on (feature 149): the content a gate
        # would verify and a review would look at is the working tree's, not HEAD's. Same formula either
        # way - the guard must not carry a second definition of "the same content".
        print(engine_key_worktree(root) if a.args and a.args[0] == "worktree" else engine_key(root, a.args[0] if a.args else "HEAD"))
        return 0
    if a.command == "remote-spend":
        print(runlog.remote_spend_report(skill))
        return 0

    if a.target:
        # ONLY AN EXPENSIVE OPERATION MAY RUN REMOTELY (FR-010, fourth request): the registry decides,
        # so `cohort` dispatches and a cheap/read-only diagnostic is refused before any AWS call.
        from l7r.diagram._invocation import OPERATIONS

        costs = {target: cost for _mod, (target, cost) in OPERATIONS.items()}
        head = a.target.split()[0]
        if costs.get(head) != "expensive":
            print(
                f"ci-check: REFUSED - TARGET={head!r} is {costs.get(head, 'not a registered operation')}; only an EXPENSIVE operation runs remotely (cohort, cache-audit, regressions, ...). Run it locally."
            )
            return 1
    ctx = dispatch.Context(
        root=root,
        skill=skill,
        mode=a.command if a.command != "status" else decision.CHECK,
        scope=scope,
        operation=a.target,
        no_go=a.no_go and a.command == "check",
        compute=a.compute if a.command == "check" else config.COMPUTE_TYPE,
    )
    # REMOTE OFF (feature 132): read BEFORE any credential is loaded or any client is built, so that
    # with the switch thrown no AWS call is even possible. `status` still answers (without a
    # lookup); `check` and `image` refuse outright; `merge` becomes LOCAL-GATED - it writes the
    # verdict the push procedure reads, and that verdict is SKIP-VERIFIED only when a green local
    # `make done` vouches for exactly the engine content the merge would produce.
    remote_off = switches.read(skill).remote_off
    if a.command == "status":
        if a.route:
            from l7r.diagram.ci.delta import compute_delta

            ctx.sh(["git", "fetch", "-q", "origin"], root, None)
            route = compute_delta(root).route
            print("GATED-LOCAL" if route == "GATED" and remote_off else route)
            return 0
        if not remote_off:
            try:
                ctx.secrets = config.load_secrets(root)
                ctx.client = dispatch.Boto3Client(ctx.secrets)
            except (FileNotFoundError, ImportError) as e:  # a status with no credentials is still useful
                print(f"(no AWS lookup: {e})")
        text, _d = dispatch.status_text(ctx)
        print(text)
        print(runlog.remote_spend_report(skill))
        return 0
    if remote_off:
        # THE WOULD-HAVE-DISPATCHED TRAIL (feature 133 FR-004): a refused paid target, or a merge that
        # would have DISPATCHED, leaves an auditable run-log entry with the estimate - so remote-off
        # never hides how often the tooling was about to spend money. Audited at the period's end.
        if a.command != "merge":
            switches.check(skill, "remote", f"ci-{a.command}")
            est = decision.estimate(scope, 0.0, a.target or ("image" if a.command == "image" else None))
            runlog.write_would_have(skill, f"ci-{a.command}", "operation" if a.target or a.command == "image" else scope, est.minutes, f"remote off: `make ci-{a.command}` attempted and refused")
            print(f"(recorded as would-have-dispatched, ~{est.minutes:.0f} build-min ~${est.cost_usd:.2f} - `make ci-status` lists these; the period's audit reads them)", file=sys.stderr)
            return 1
        text, d = dispatch.status_text(ctx)
        print(text)
        (root / ".git" / "ci-verdict").write_text(d.verdict + "\n", encoding="utf-8")
        if d.skip_verified:
            print("ci-merge: LOCAL-GATED (remote off) - a green local `make done` vouches for this engine content; the caller pushes directly, no build")
            return 0
        if d.verdict == "REFUSE(remote-enabled)":  # every other condition passed: with remote on this would have been a paid build
            runlog.write_would_have(skill, "ci-merge", scope, d.estimate.minutes, "remote off: the gated merge would have DISPATCHED (no green local `make done` on the merged engine content)")
            print(f"(recorded as would-have-dispatched, ~{d.estimate.minutes:.0f} build-min ~${d.estimate.cost_usd:.2f})")
        print(f"ci-merge: LOCAL-GATED (remote off) - {d.verdict}: nothing landed. With remote off the merge needs a green local `make done` on the")
        print("  merged engine content: `git pull --no-rebase origin main` (if main moved), then `make done`, then `scripts/sync-with-main.sh done` again.")
        return 1

    ctx.secrets = config.load_secrets(root)
    ctx.client = dispatch.Boto3Client(ctx.secrets)
    if a.command == "image":
        return dispatch.run_image(ctx).rc
    if a.target and a.command != "check":
        ap.error("--target is for ci-check only")
    out = dispatch.run(ctx)
    # sync-with-main.sh reads the verdict: SKIP-VERIFIED means "push directly", DISPATCHED means "the build landed it"
    (root / ".git" / "ci-verdict").write_text(out.verdict + "\n", encoding="utf-8")
    return out.rc


if __name__ == "__main__":
    sys.exit(main())
