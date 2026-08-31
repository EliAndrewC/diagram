"""The ~1,000-line bar, proven to fire (feature 173, constitution Principle X clause 13).

Every rule here was written by DELETING the rule from `check-file-scale.py` and watching the test go
red - the project's standing requirement for a guard, and the reason clause 13 sat unenforced for two
weeks with `make audit` reporting five files while ten were over.

No `tooling` marker: this reads files and calls functions, it does not run make, git or a coverage
subprocess, so it belongs in the quick tier like any other unit test.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[5]
_spec = importlib.util.spec_from_file_location("check_file_scale", REPO / "scripts" / "check-file-scale.py")
assert _spec and _spec.loader
cfs = importlib.util.module_from_spec(_spec)
sys.modules["check_file_scale"] = cfs
_spec.loader.exec_module(cfs)

LINE = "x = 1\n"


def _tree(tmp_path: pathlib.Path, files: dict[str, str]) -> pathlib.Path:
    """Relative paths as written - `__pycache__` is a real directory name, so no separator tricks."""
    for name, body in files.items():
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    return tmp_path


def test_the_bar_is_1000_and_1000_itself_passes(tmp_path: pathlib.Path) -> None:
    """1,000 passes, 1,001 fails - the GM said 'over one thousand lines', so 1,000 is not over."""
    root = _tree(tmp_path, {"edge.py": LINE * 1000, "over.py": LINE * 1001})
    over, justified, scanned = cfs.run(str(root))
    assert [p.name for p, _ in over] == ["over.py"]
    assert justified == [] and scanned == 2


def test_raw_lines_are_counted_not_statements(tmp_path: pathlib.Path) -> None:
    """Clause 13's unit is RAW lines because the cost is tokens - blanks and comments count."""
    root = _tree(tmp_path, {"padded.py": ("# comment\n" * 500) + ("\n" * 501)})
    over, _, _ = cfs.run(str(root))
    assert [p.name for p, _ in over] == ["padded.py"], "1,001 lines of comment and blank is still 1,001 lines"


def test_a_justified_file_passes_and_is_reported_separately(tmp_path: pathlib.Path) -> None:
    reason = "an ordered registry whose row order IS the execution contract"
    root = _tree(tmp_path, {"reg.py": f"# {cfs.MARKER} {reason}\n" + LINE * 1001})
    over, justified, _ = cfs.run(str(root))
    assert over == []
    assert [(p.name, why) for p, _, why in justified] == [("reg.py", reason)]


def test_a_marker_with_no_real_reason_still_fails(tmp_path: pathlib.Path) -> None:
    """Feature 170's rule, applied to a file annotation: an escape must SAY WHY.

    The floor is 40 characters rather than that guard's eight, because a whole-file exemption is
    argued rather than tokenized. This is the assertion that keeps the carve-out from being free.
    """
    root = _tree(tmp_path, {"lazy.py": f"# {cfs.MARKER} ordered data\n" + LINE * 1001})
    over, justified, _ = cfs.run(str(root))
    assert [p.name for p, _ in over] == ["lazy.py"] and justified == []


def test_the_marker_must_be_in_the_header_not_buried(tmp_path: pathlib.Path) -> None:
    """A justification a reader meets on line 900 is not a justification they meet at all."""
    reason = "an ordered registry whose row order IS the execution contract"
    body = LINE * (cfs.HEADER_LINES + 1) + f"# {cfs.MARKER} {reason}\n" + LINE * 1000
    root = _tree(tmp_path, {"buried.py": body})
    over, justified, _ = cfs.run(str(root))
    assert [p.name for p, _ in over] == ["buried.py"] and justified == []


def test_the_four_exclusions_are_not_scanned(tmp_path: pathlib.Path) -> None:
    """The frozen exhibits, other sessions' clones, and the feature record are out of scope.

    Three `legacy-hand-authored-pool` gens are over the bar and MUST stay untouched (feature 161
    froze them); `specs/` holds fourteen retired one-shot splitters kept as history.
    """
    big = LINE * 1001
    root = _tree(
        tmp_path,
        {
            "legacy-hand-authored-pool/towns/x/x.gen.py": big,
            ".clones/peer/thing.py": big,
            "specs/024-human-scale-files/split_package.py": big,
            "__pycache__/cached.py": big,
            "live.py": big,
        },
    )
    over, _, scanned = cfs.run(str(root))
    assert [p.name for p, _ in over] == ["live.py"], "only the live file is judged"
    assert scanned == 1


def test_scanning_zero_files_fails_loudly(tmp_path: pathlib.Path, capsys) -> None:
    """Wrong root beats silent success - check-duplicate-defs.py's recorded lesson, inherited."""
    assert cfs.main([str(tmp_path)]) == 1
    assert "ZERO files" in capsys.readouterr().err


def test_the_refusal_prints_the_procedure(tmp_path: pathlib.Path, capsys) -> None:
    """The GM asked for a message that explains what the clone must do. This is that assertion."""
    root = _tree(tmp_path, {"over.py": LINE * 1001})
    assert cfs.main([str(root)]) == 1
    err = capsys.readouterr().err
    for expected in (
        "clause 13",  # the rule
        "DIRECTORY-MODULE",  # the prescribed shape
        "CLAUDE.md",  # the index
        "look here when",  # the index format
        "structures/",  # a named exemplar that exists
        "ORDERED DATA",  # carve-out one
        "DERIVED ROSTER",  # carve-out two
        "hamletgen/ways.py",  # the GM's own worked example
    ):
        assert expected in err, f"the refusal must name {expected!r}"


def test_the_refusal_states_no_duration(tmp_path: pathlib.Path) -> None:
    """Feature 171's rule: no guard message says how long a command takes - it goes stale."""
    import re

    assert not re.search(r"\b\d+(\.\d+)?\s*(s|sec|second|min|minute)s?\b", cfs.GUIDANCE)


def test_the_selftest_passes() -> None:
    """A checker that cannot prove it still bites is the failure mode the guard exists to prevent."""
    assert cfs.selftest() == 0


def test_the_repository_itself_is_under_the_bar() -> None:
    """The rule holds on this tree - the half of feature 173 that was the actual work.

    NOTE WHERE THIS RUNS. Everything in `tests/tooling/` is marked `tooling` by location and is
    skipped while the tooling hash is unchanged, so this assertion does NOT run on a gate whose only
    change was engine code. That is fine, and it is not the enforcement: `make lint` runs
    `check-file-scale.py` over the whole tree on EVERY gate and every push, unconditionally. This
    exists to fail with the offending filenames for someone running the suite alone, and to prove
    the checker still agrees with the tree at the moment the checker itself changes.
    """
    over, _, scanned = cfs.run(str(REPO))
    assert scanned > 100, "the scan found almost nothing - wrong root?"
    assert over == [], "over the bar: " + ", ".join(f"{p} ({n})" for p, n in over)
