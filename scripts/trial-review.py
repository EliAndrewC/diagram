#!/usr/bin/env python3
"""`make trial-review F=<n>` - the bundle and the dispatch of a trial's ONE review (feature 442).

A trial (`make trial`, feature 438) is reviewed once, when its brief is Done and its evidence fixed. Its research files record
each measurement's output beside its figure, so the review CHECKS each figure against the output recorded beside it and re-runs a
command only where an output is missing or disagrees - trial 441's review re-ran every profile to re-derive figures its research
already held (about 3 of its 5.6 minutes).

The bundle (`/tmp/l7r-check/trial-review-<NNN>/`) holds the brief, `request.md`, every `research/*.md` and a `MANIFEST.md`; the
dispatch is printed for spec-fidelity, MODE 2.
"""

from __future__ import annotations

import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
CHECK_DIR = pathlib.Path("/tmp/l7r-check")

INSTRUCTION = (
    "Each figure in the brief and its research is recorded with the command that measured it and its output: CHECK each figure "
    "against the output recorded beside it, and re-run a command only where an output is missing or disagrees with its figure."
)


def bundle(feature: pathlib.Path, out: pathlib.Path) -> pathlib.Path:
    """Copy the trial's brief, request and research into `out` and write its MANIFEST; the MANIFEST's path."""
    if out.exists():
        shutil.rmtree(out)
    (out / "research").mkdir(parents=True)
    names = ["spec.md", "request.md"]
    for name in names:
        if (feature / name).is_file():
            shutil.copy(feature / name, out / name)
    research = sorted((feature / "research").glob("*.md")) if (feature / "research").is_dir() else []
    for f in research:
        shutil.copy(f, out / "research" / f.name)
    files = [n for n in names if (out / n).is_file()] + [f"research/{f.name}" for f in research]
    (out / "MANIFEST.md").write_text(
        f"# The one review of trial {feature.name}\n\nThe brief (`spec.md`, **Form**: trial) with its evidence fixed, and the GM's words "
        f"(`request.md`).\n\n{INSTRUCTION}\n\nJudge whether the brief and its verdict do what the GM asked, and whether the verdict is "
        "the branch of the brief's own rule its measurement took.\n\n## Files\n\n" + "".join(f"- `{n}`\n" for n in files),
        encoding="utf-8",
    )
    return out / "MANIFEST.md"


def main(argv: list[str]) -> int:
    if len(argv) != 1 or not argv[0].strip().isdigit():
        print("make trial-review: F=<feature number> is required - e.g. make trial-review F=441", file=sys.stderr)
        return 2
    n = f"{int(argv[0]):03d}"
    found = sorted((ROOT / "specs").glob(f"{n}-*"))
    if not found or not (found[0] / "spec.md").is_file() or "**Form**: trial" not in (found[0] / "spec.md").read_text(encoding="utf-8"):
        print(f"make trial-review: specs/{n}-* is no trial brief (**Form**: trial) - an ordinary spec takes its review from spec-fidelity's MODE 2 as before", file=sys.stderr)
        return 2
    manifest = bundle(found[0], CHECK_DIR / f"trial-review-{n}")
    print(f"MODE 2: SPECIFICATION REVIEW of trial {found[0].name} - its one review: read {manifest} and the files beside it. {INSTRUCTION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
