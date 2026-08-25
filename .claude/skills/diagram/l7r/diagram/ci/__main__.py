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

from l7r.diagram.ci import config, decision, dispatch, door, runlog, state  # noqa: E402


def _roots() -> tuple[Path, Path]:
    root = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip())
    return root, root / ".claude" / "skills" / "diagram"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="l7r.diagram.ci", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["status", "check", "merge", "image", "state", "door", "remote-spend", "engine-key"])
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
        if len(a.args) != 2:
            ap.error("state needs EVENT TARGET")
        st = state.write(root, a.args[0], a.args[1])
        print(f"verification-state: {st.event} ({st.target}) recorded")
        return 0
    if a.command == "door":
        ok, why = door.check(root, skill)
        print(f"bypass-audit: {why}")
        return 0 if ok else 1
    if a.command == "engine-key":
        from l7r.diagram.ci.delta import engine_key

        print(engine_key(root, a.args[0] if a.args else "HEAD"))
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
    if a.command == "status":
        if a.route:
            from l7r.diagram.ci.delta import compute_delta

            ctx.sh(["git", "fetch", "-q", "origin"], root, None)
            print(compute_delta(root).route)
            return 0
        try:
            ctx.secrets = config.load_secrets(root)
            ctx.client = dispatch.Boto3Client(ctx.secrets)
        except (FileNotFoundError, ImportError) as e:  # a status with no credentials is still useful
            print(f"(no AWS lookup: {e})")
        text, _d = dispatch.status_text(ctx)
        print(text)
        print(runlog.remote_spend_report(skill))
        return 0

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
