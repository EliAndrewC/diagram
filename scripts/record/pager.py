"""Print a long report through a pager when it goes to a terminal, as git does.

WHY (the GM 2026-10-27): `make claims-report` wrote about 128 KB at once, and under the laptop's rootless podman a
`podman exec -it` connection is dropped when the terminal falls behind a burst of output (`/host-scripts/launch-container.sh`
records the measurement), so the report "crashed" the tab mid-line. A pager writes one screen at a time. A pipe or a file
still gets the whole text, unpaged, and `NO_PAGER=1` turns it off.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from typing import TextIO


def page(text: str, out: TextIO | None = None) -> None:
    """`text` through `$PAGER` (default `less -FRSX`: quit if it fits, keep color, chop long lines) when `out` is a terminal
    and the text is longer than one screen; otherwise printed whole."""
    out = out if out is not None else sys.stdout
    rows = shutil.get_terminal_size().lines
    pager = os.environ.get("PAGER") or "less -FRSX"
    if os.environ.get("NO_PAGER") or not out.isatty() or text.count("\n") + 1 < rows or not shutil.which(pager.split()[0]):
        print(text, file=out)
        return
    out.flush()
    subprocess.run(pager, shell=True, input=text + "\n", text=True, check=False)
