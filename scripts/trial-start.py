#!/usr/bin/env python3
"""`make trial SLUG=<slug>` - start a TRIAL: claim a feature number and write its trial brief (feature 438).

A trial is a question a measurement answers, asked before any decision to build (docs/spec-kit-and-reviews.md, "The trial
form"). Its `spec.md` is the brief `.specify/templates/trial-template.md` gives (`**Form**: trial`): measured first, reviewed
once when the evidence is fixed and the status turns Done. The review gate passes a running trial's pushes with no verdict
while they change no engine code on net (`scripts/gates/review-gate.sh`).

WHY (feature 437): the array geometry trial's spec took three review rounds and a round-arbiter ruling - about 12 minutes of
reviewer time - because it was reviewed while the trial's evidence changed beside it.

The number is claimed by `scripts/claim-feature.py`, the same lock and numbering as `make claim`.
"""

from __future__ import annotations

import datetime
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
TEMPLATE = ROOT / ".specify" / "templates" / "trial-template.md"
REQUEST = "# Feature {n} - the GM's request, verbatim\n\n> [the GM's words, verbatim]\n"


def brief(directory: pathlib.Path, today: str, template: pathlib.Path = TEMPLATE, approved: str = "") -> None:
    """Write the trial brief and the request stub into a claimed feature `directory` - its approval line carrying `approved`
    (the GM's words, verbatim) when given, so the approval guard passes the brief's first commit (feature 440 T05)."""
    n = str(int(directory.name.split("-")[0]))
    text = template.read_text(encoding="utf-8").replace("[DATE]", today).replace("[N]", n)
    if approved.strip():
        text = text.replace('"[his words, verbatim]"', '"' + approved.strip().replace('"', "'") + '"')
    directory.joinpath("spec.md").write_text(text, encoding="utf-8")
    if not directory.joinpath("request.md").exists():
        directory.joinpath("request.md").write_text(REQUEST.format(n=n), encoding="utf-8")


def main(argv: list[str], approved: str | None = None) -> int:
    approved = os.environ.get("TRIAL_APPROVED", "") if approved is None else approved
    if len(argv) != 1 or not argv[0].strip():
        print("make trial: SLUG=<kebab-slug> is required - e.g. make trial SLUG=fewer-seat-candidates", file=sys.stderr)
        return 2
    got = subprocess.run([sys.executable, str(HERE / "claim-feature.py"), "--", argv[0]], capture_output=True, text=True, cwd=ROOT)
    sys.stderr.write(got.stderr)
    if got.returncode != 0:
        return got.returncode
    name = got.stdout.strip().splitlines()[-1]
    brief(ROOT / "specs" / name, datetime.date.today().isoformat(), approved=approved)
    print(name)
    print(f"trial: specs/{name}/spec.md is the brief (**Form**: trial) - fill its question, rule and request.md; measure first; one review when Done", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
