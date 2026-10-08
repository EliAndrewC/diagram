#!/usr/bin/env python3
"""Feature 330, T03 (plan D3): settle the existing open features by rewriting each one's status line with its
evidence. Run once from the clone root; kept as the record. The evidence behind each line is in audit.md, section C.

    settle.py [--dry-run]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SETTLE = {
    "007-packing-audit-hardening": "Done (2026-07-13): T001-T012 landed in e6450f5f2 with the task list itself (`pack_audit` top-N vacant rectangles and the region grid, Ochiba's SE consolidation); the boxes were never ticked (feature 330 audit)",
    "008-mode-a-composition": "Done (2026-07-15): both phases shipped in 6da94c18f - the perimeter-first placer (`compound.py` `place`) and the composition check (`pack_audit` `perimeter_hugging_pct`); `docs/buildings.md` \"Composition\" (feature 330 audit)",
    "010-land-use-overlay-grounding": "Done (2026-07-19): landed with the spec in ff0b34d5b - the overlay knob and its topographic and economic terms (`settlement/fields/landuse.py`) (feature 330 audit)",
    "012-in-field-paddy-features": "Done (2026-07-19): the in-field features landed in 6f4c9333c (`settlement/fields/features.py`, the field ponds, rocks and graves) (feature 330 audit)",
    "015-punishment-execution-grounds": "Done (2026-07-25): f78e4e533; only the stop-work task was left unticked (feature 330 audit)",
    "016-minami-provincial-city": "Done (2026-07-26): T14-T16 landed in 614696beb, the map at its specified population in 6a0ce606c; Minami is now a frozen exhibit (feature 330 audit)",
    "017-overlap-matrix": "Done (2026-07-26): T008 fixed in 81deedca4, \"all eleven matrix defects cleared\"; `_MATRIX_OUTSTANDING` is empty (feature 330 audit)",
    "019-capital-skeleton-castle": "Withdrawn (the GM, 2026-10-07: Shiro Daika's hand pass dropped, `docs/migration-plan.md`): the engine half landed (8eb15b41a, the capital tier runs); the hand map, its checks (deleted with the battery by feature 166) and the byte-identity task (retired by the 2026-08-16 freeze) are withdrawn (feature 330 audit)",
    "021-capital-housing": "Withdrawn (the GM, 2026-10-07: Shiro Daika's hand pass dropped, `docs/migration-plan.md`): US1 landed (d5a99e619); the rest was the hand map's fabric and its checks (feature 330 audit)",
    "112-fields-package": "Done (2026-08-16): 745a067ae and the decompositions after it; only bookkeeping tasks were left unticked (feature 330 audit)",
    "114-structures-package": "Done (2026-08-16): 92656dfca; only the final gate and stop-work were left unticked (feature 330 audit)",
    "115-civic-grounds-package": "Done (2026-08-16): 2389749ea and 4885c99d5; the open tasks are bookkeeping, or moot since wip/ was retired (T004) (feature 330 audit)",
    "118-rolling-package": "Done (2026-08-17): 7ad4e23c5 and 0bcf81548; only the gate and stop-work were left unticked (feature 330 audit)",
    "119-l7r-diagram-namespace": "Done (2026-08-17): three landings, 0280ec9c0, 948682a5a, 2e2d609b6; only stop-work was left unticked (feature 330 audit)",
    "125-lanes-do-not-break": "Done (2026-08-18): a44013da0, e42cd4210, d305556aa - the spec is the write-up of work that shipped (feature 330 audit)",
    "126-derived-lanes-and-form": "Done (2026-08-23): 9fcb6b0d2 and 7b448f78a; FR-003 superseded by feature 128 (its spec, \"Supersedes ... FR-003, in full\"), the settlement forms switched back on by 291; the task list was never maintained (feature 330 audit)",
    "130-codebuild-merge-gate": "Done (2026-08-25): the merge gate shipped (b3bb3782d and the commits before it); T063, the first FULL run, withdrawn by the GM's remote-off ruling (`dev/switches.json`, 2026-09-05) (feature 330 audit)",
    "131-split-diagram-repo": "Done (2026-08-25): the split landed (5c38ebc4a, 0773b970a); only the report task was left unticked (feature 330 audit)",
    "139-remaining-test-failures": "Done (2026-08-30): the whole inventory left by retirement, as this spec counts it - the check battery deleted (e20ca2623), the tripwire list empty (feature 330 audit)",
    "155-mains-red-floor": "Done (2026-08-29): main's red floor closed (84e75096b) and the coverage question answered by the GM through feature 174 (feature 330 audit)",
    "175-warm-the-remote-build": "Done (2026-08-31): the cache travels with the build, MEASURED in c09942435; its owed measurement taken by feature 177 (feature 330 audit)",
    "275-village-burial-ground": "Withdrawn (the GM, 2026-09-28, recorded in this feature's request.md; 969885309): the work is filed as feature 350 (feature 330 audit)",
}

_STATUS = re.compile(r"^(\*\*Status\*\*:?|\*\*Status:\*\*)[^\n]*$", re.M)


def main(argv: list[str]) -> int:
    dry = "--dry-run" in argv
    for name, status in SETTLE.items():
        d = ROOT / "specs" / name
        spec = d / "spec.md"
        line = f"**Status**: {status}"
        if spec.is_file():
            text = spec.read_text()
            if _STATUS.search(text):
                text = _STATUS.sub(lambda _m: line, text, count=1)
            else:  # a spec with no status line: the line goes after the title
                head, _, rest = text.partition("\n")
                text = f"{head}\n\n{line}\n{rest}"
        else:  # no spec.md (275: a request withdrawn before a spec was written) - the status alone
            text = f"# Feature Specification: {name.split('-', 1)[1].replace('-', ' ')}\n\n{line}\n\nThe GM's words and the withdrawal are in [`request.md`](request.md).\n"
        if not dry:
            spec.write_text(text)
        print(f"{name}: {status[:70]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
