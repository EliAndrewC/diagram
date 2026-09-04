"""The constants and the secrets - the ONLY module that knows the AWS account's names.

THE ONE RATE CONSTANT. `RATE_PER_MIN` is what every cost line in the audit is computed from, and it
is mirrored in exactly one other place: the `gm-assistant-ci-monthly-alert` Lambda's `RATE_PER_MIN`
environment variable (the live 20%-steps email). Change the compute type and both move together -
`tests/tooling/ci/test_config.py` pins the value so the change is deliberate.

WHERE THE SECRETS COME FROM. `development-secrets.ini` is gitignored and lives at the repository
root; a `.example` beside it names every key. Resolution order: `$DIAGRAM_SECRETS`, the working
tree's root, the main tree's root (a clone's grandparent), and finally gm-assistant's
`webapp/development-secrets.ini` under the /host-l7r-repo mount (gm-assistant is /host-l7r-repo/gm-assistant since 2026-08-25) - the file the AWS session
wrote the keys into on 2026-08-24, so a container that has it needs nothing copied.
"""

from __future__ import annotations

import configparser
import os
from dataclasses import dataclass
from pathlib import Path

# BUILD_GENERAL1_LARGE: 8 vCPU / 15 GB, $0.02 per build-minute, billed from PROVISIONING to end.
# CHOSEN BY MEASUREMENT (feature 179, GM 2026-09-04: "lock in the eight CPUs going forward"), from
# feature 178's three-row comparison - ONE commit, run sequentially, all green:
#     4 vCPU  BUILD_GENERAL1_MEDIUM   913 s  16 billed min  $0.16
#     8 vCPU  BUILD_GENERAL1_LARGE    553 s  10 billed min  $0.20   <- this one
#    36 vCPU  BUILD_GENERAL1_XLARGE   418 s   7 billed min  $0.56
# 2.8x cheaper for 1.32x the time. 4 vCPU was REJECTED on evidence, not on price: it saves only $0.04
# more and is where kuwabata's GEN_TIME_BUDGETS entry tripped on two of three attempts, because those
# are CPU-SECOND budgets and CPU seconds rise on a slower core - flaky, which in a merge gate is worse
# than slow. And 36 cores never earned its price: 4.5x the cores of the 4-vCPU row for 2.18x the
# speed, because the suite does not parallelise past 8 workers (see the CPU_COUNT comment below).
# Superseded: BUILD_GENERAL1_XLARGE at $0.08, chosen 2026-08-24 against 2xlarge (feature 130, T028).
RATE_PER_MIN = 0.02
COMPUTE_TYPE = "BUILD_GENERAL1_LARGE"
# Per-minute rates by compute type (us-east-1 Linux on-demand price list, 2026-08): the knob
# `make ci-check COMPUTE=BUILD_GENERAL1_2XLARGE` exists to MEASURE whether a workload scales - the
# default stays the constant above until a number says otherwise. It is how the table above was
# taken, which is the argument for keeping it.
RATES = {"BUILD_GENERAL1_XLARGE": 0.08, "BUILD_GENERAL1_2XLARGE": 0.20, "BUILD_GENERAL1_LARGE": 0.02, "BUILD_GENERAL1_MEDIUM": 0.01}
PROJECT_MERGE = "gm-assistant-merge"  # concurrency 1 - the merge queue
PROJECT_CHECK = "gm-assistant-check"  # concurrency 3 - the iteration check
GITHUB_REPO = "EliAndrewC/diagram"
MAILBOX_PREFIX = "session/"
# FR-036: a parked build aborts itself after this long with no go signal - the most a dead
# dispatcher can cost (~$0.04 at the rate above). The build polls every 2 s; the dispatcher's
# reference check takes ~26 s, so the ceiling is generous without being open-ended.
PARK_TIMEOUT_S = 120
PARK_POLL_S = 2
# R5: the log is streamed by polling inside ONE process the session backgrounded - the sanctioned
# shape - at a cadence that costs nothing noticeable.
STREAM_POLL_S = 10
# Estimates printed BEFORE dispatch (FR-014). Replaced by measurement as timings.md fills in.
# `reference` is MEASURED on this compute type: dev/run-log/20260904T001453005229-3306563.json,
# build 545da8e1, scope reference, 569 s elapsed, 10 billed minutes, $0.20 (feature 179).
# `full` and `operation` are UNMEASURED PLACEHOLDERS carried from feature 130 and have never been
# calibrated against anything - they are not XLARGE figures to be scaled, and scaling a placeholder
# by a real ratio would dress a guess as a derivation. They move when a run measures them.
# VISIBLE ARTIFACT OF THAT, left deliberately: `full` (8.0) now reads LOWER than the measured
# `reference` (10.0), which cannot be true - feature 177 measured the FULL scope at 1:1 with
# reference. It is not corrected here because correcting it means inventing a number for a scope no
# run on this compute type has measured, and an invented estimate is what this comment exists to
# prevent. The next FULL remote run supplies it.
ESTIMATE_MINUTES = {"reference": 10.0, "full": 8.0, "operation": 10.0}

SECRETS_EXAMPLE = """# development-secrets.ini - gitignored; copy this file, drop the .example, fill the values.
[aws]
region = us-east-1
access_key_id =
secret_access_key =
account_id =
ci_bucket = gm-assistant-ci-130071571821
ecr_image = 130071571821.dkr.ecr.us-east-1.amazonaws.com/gm-assistant-ci
log_group = /aws/codebuild/gm-assistant

[github]
codebuild_pat =
"""


@dataclass(frozen=True)
class Secrets:
    region: str
    access_key_id: str
    secret_access_key: str
    ci_bucket: str
    ecr_image: str
    log_group: str
    github_pat: str
    path: str


def candidate_paths(root: Path) -> list[Path]:
    out: list[Path] = []
    env = os.environ.get("DIAGRAM_SECRETS")
    if env:
        out.append(Path(env))
    out.append(root / "development-secrets.ini")
    if root.parent.name == ".clones":
        out.append(root.parent.parent / "development-secrets.ini")
    out.append(Path("/host-l7r-repo/gm-assistant/webapp/development-secrets.ini"))
    return out


def load_secrets(root: Path) -> Secrets:
    """The first readable candidate wins. A missing file is an error naming every place looked."""
    for path in candidate_paths(root):
        if not path.is_file():
            continue
        cp = configparser.ConfigParser()
        cp.read(path)
        aws = cp["aws"] if cp.has_section("aws") else {}
        gh = cp["github"] if cp.has_section("github") else {}
        return Secrets(
            region=aws.get("region", "us-east-1"),
            access_key_id=aws.get("access_key_id", ""),
            secret_access_key=aws.get("secret_access_key", ""),
            ci_bucket=aws.get("ci_bucket", ""),
            ecr_image=aws.get("ecr_image", ""),
            log_group=aws.get("log_group", "/aws/codebuild/gm-assistant"),
            github_pat=gh.get("codebuild_pat", ""),
            path=str(path),
        )
    looked = "\n  ".join(str(p) for p in candidate_paths(root))
    raise FileNotFoundError(f"no development-secrets.ini found; looked in:\n  {looked}\n(copy development-secrets.ini.example at the repository root and fill the [aws] and [github] keys)")
