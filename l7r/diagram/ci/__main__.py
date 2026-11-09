"""`python3 -m l7r.diagram.ci incremental ...` - the incremental gate, reached only through make (feature 207). Every other subcommand
is the Rust gate's since feature 449 T064 (`l7r-gate ci`); this goes with `incremental.py` in T071."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from l7r.diagram._invocation import assert_via_make

# REFUSE unless invoked through this project's make - at the TOP, before any argument is read.
assert_via_make("l7r.diagram.ci", "ci-status  (free)")


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args[:1] != ["incremental"]:
        print("usage: python3 -m l7r.diagram.ci incremental <plan|mode|merge|carry|save-baseline|...>", file=sys.stderr)
        return 2
    from l7r.diagram.ci import incremental

    root = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip())
    return incremental.main(args[1:], root, root)


if __name__ == "__main__":
    sys.exit(main())
