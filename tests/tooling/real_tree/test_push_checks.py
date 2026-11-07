"""THE REAL TREE's half of `tests/tooling/test_push_checks.py`: each whole-tree push check answers the same in this process as alone, on the real tree.

Moved here by feature 444 T36 (the GM 2026-11-07: "any single test which takes even 100 milliseconds is fairly suspect"; then "please
proceed with all 3 of those things"): it checks a TOOL's behavior over the whole repository, and a scan of the whole repository reads
every file, so the gate's recorded reads selected it for every edit, a Rust one included. It is the tool's property, not the edited
file's: `tests/tooling/real_tree/` runs when the gate plans full (any `scripts/`, gate-configuration or tooling change - the tool's
own) and on `FULL=1`, never for an engine or a Rust increment (`pool_readers.rust_readers`, `tests/CLAUDE.md`).
"""

from __future__ import annotations

import pytest

from tests.tooling.test_push_checks import ROOT, WHOLE_TREE, _alone, _inside


@pytest.mark.parametrize("name,rel,argv", [(c[0], c[1], c[2]) for c in WHOLE_TREE], ids=[c[0] for c in WHOLE_TREE])
def test_each_check_in_this_process_gives_what_it_gives_alone(name: str, rel: str, argv: tuple[str, ...], capfd: pytest.CaptureFixture[str]) -> None:
    path = ROOT / "scripts" / rel
    args = [a.replace("{root}", str(ROOT)) for a in argv]
    assert _inside(path, args, ROOT, capfd) == _alone(path, args, ROOT), name
