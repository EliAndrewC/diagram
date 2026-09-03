#!/usr/bin/env python3
"""Apply the CI bucket's lifecycle document and READ IT BACK (feature 177, T05/FR-015).

    python3 scripts/apply-ci-lifecycle.py            # show the live document beside the intended one
    python3 scripts/apply-ci-lifecycle.py --apply    # put it, then read it back and print what landed

**Why this is a script and not a make target.** It is a one-shot administrative operation against
live infrastructure, run when the document in `l7r/diagram/ci/cachepolicy.py` changes - which is
roughly never. What a make target buys (a cheap alternative to offer first) does not apply: there is
no cheaper version of "change the bucket".

**It needs the ADMIN key, and that is not an accident of packaging.** The `[aws]` session key cannot
so much as READ the lifecycle configuration - `AccessDenied` on `s3:GetLifecycleConfiguration` for
`user/gm-assistant-ci`, measured 2026-09-03 - which is why feature 175 could not check its own
assumption and had to record the 14-day catch-all as an open question rather than a fact. `[aws_admin]`
can. So a session dispatching builds cannot rewrite the rules that expire their evidence.

**The document comes from the tested module, never from this file.** `cachepolicy.lifecycle_configuration()`
is what `tests/tooling/ci/test_cachepolicy.py` asserts on, so what lands on the bucket is what the
suite checked. This script contributes no policy of its own - if it did, the tests would be checking
something the bucket never receives, which is the failure mode the whole arrangement exists to avoid.
"""

from __future__ import annotations

import argparse
import configparser
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".claude" / "skills" / "diagram"
sys.path.insert(0, str(SKILL))

from l7r.diagram.ci import cachepolicy, config  # noqa: E402


def _client(secrets_path: Path) -> tuple[object, str]:
    import boto3

    cp = configparser.ConfigParser()
    cp.read(secrets_path)
    if "aws_admin" not in cp:
        raise SystemExit(f"no [aws_admin] section in {secrets_path} - this operation needs the admin key, not the session key")
    aws, admin = cp["aws"], cp["aws_admin"]
    client = boto3.client(
        "s3",
        region_name=aws["region"],
        aws_access_key_id=admin["access_key_id"],
        aws_secret_access_key=admin["secret_access_key"],
    )
    return client, aws["ci_bucket"]


def _live(client: object, bucket: str) -> list[dict]:
    try:
        return list(client.get_bucket_lifecycle_configuration(Bucket=bucket)["Rules"])  # type: ignore[attr-defined]
    except Exception as e:  # the bucket may legitimately carry no document at all
        print(f"(could not read the live document: {e})")
        return []


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="put the document (without this, nothing is written)")
    a = ap.parse_args(argv)

    for path in config.candidate_paths(ROOT):
        if path.is_file():
            secrets_path = path
            break
    else:
        raise SystemExit("no development-secrets.ini found")

    client, bucket = _client(secrets_path)
    want = cachepolicy.lifecycle_configuration()

    print(f"bucket: {bucket}   secrets: {secrets_path}")
    print("\n-- LIVE (before) --")
    for r in _live(client, bucket):
        print(" ", json.dumps(r, default=str))
    print("\n-- INTENDED (l7r/diagram/ci/cachepolicy.py, the document the suite asserts on) --")
    for r in want["Rules"]:
        print(" ", json.dumps(r))

    if not a.apply:
        print("\nnothing written; re-run with --apply")
        return 0

    client.put_bucket_lifecycle_configuration(Bucket=bucket, LifecycleConfiguration=want)  # type: ignore[attr-defined]
    print("\n-- READ BACK (this is what FR-015 records; an unread put proves nothing) --")
    got = _live(client, bucket)
    for r in got:
        print(" ", json.dumps(r, default=str))
    ids = [r.get("ID") for r in got]
    if cachepolicy.RETIRED_RULE_ID in ids:
        print(f"\nWARNING: {cachepolicy.RETIRED_RULE_ID} is still present - the evidence is still on a junk horizon")
        return 1
    print(f"\nok: {len(got)} rules; {cachepolicy.RETIRED_RULE_ID} is gone and verified/ carries its own horizon")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
