"""`python3 -m l7r.diagram.tools.pack_audit` - the entry point the package must keep.

Feature 173 split `pack_audit.py` into this package, and a package is only runnable as `-m` if it
has a `__main__.py`: the `if __name__` guard that used to sit at the bottom of the monolith would
otherwise belong to `report.py`'s module, which nothing invokes by that path. Without this file
`make pack-audit` breaks and `tests/test_operations_registry.py` reports the registry row as naming
a module that is gone - which is how it was caught.

THE make-ONLY GUARD MOVES WITH IT (feature 127). It sat inside the block that was removed, and a
split that quietly dropped it would leave this operation runnable by a bare interpreter - the one
thing the whole guard exists to prevent.
"""

from __future__ import annotations

from l7r.diagram._invocation import guard

from .report import main

# REFUSE unless invoked through this project's make (feature 127). At the TOP of the
# entry point, never in a loop - the determination reads /proc and is cached per process.
guard("l7r.diagram.tools.pack_audit")
raise SystemExit(main())
