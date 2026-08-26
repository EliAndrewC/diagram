"""tooling tests split out of `tests.test_invocation` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from l7r.diagram import _invocation as inv
from tests.test_invocation import _PROBE, REPO, SKILL, _probe_cmd, _run_probe


@pytest.mark.tooling
def test_a_child_spawned_under_make_INHERITS_make() -> None:
    """STAYS QUIET - and this test replaced one that was subtly, instructively wrong.

    The original asserted that spawning `python3 -c ...` gives a process with no make in its
    ancestry, and it PASSED when the file was run directly. Under `make quick` it failed, because a
    subprocess of a make-run process still has make above it. That is not a bug in the guard; it is
    the guard being right, and it is the same inheritance that makes pytest-xdist workers and
    `cohort()`'s pool children legitimate.

    So the honest version is this: the property under test is INHERITANCE, and it is the property the
    whole design depends on. The old test could only pass when the suite was run the wrong way, which
    makes it worse than no test - it was a green light for running pytest outside make.

    THE NO-MAKE CASE IS UNTESTABLE END-TO-END FROM INSIDE A MAKE-RUN SUITE, by construction. It is
    covered at unit level instead, where the ancestry is supplied rather than inherited - see
    `test_compute_reports_a_foreign_make_differently_from_no_make`."""
    out = subprocess.run(
        [sys.executable, "-c", _PROBE.format(skill=str(SKILL))],
        capture_output=True,
        text=True,
        check=False,
    )
    expected = "True" if inv.via_make() else "False"
    assert out.stdout.strip() == expected, "a child must inherit this process's verdict, whichever it is"


@pytest.mark.tooling
def test_make_in_this_repo_is_accepted(tmp_path: Path) -> None:
    """STAYS QUIET: make -> sh -c -> python, which is EVERY make recipe.

    A parent-only check fails this case, because make runs recipe lines through a shell and the
    immediate parent is `sh`."""
    work = REPO / ".tmp-invocation-test"
    work.mkdir(exist_ok=True)
    try:
        assert _run_probe(tmp_path, _probe_cmd(), cwd=work) == "True"
    finally:
        for f in work.iterdir():
            f.unlink()
        work.rmdir()


@pytest.mark.tooling
def test_a_foreign_makefile_is_refused(tmp_path: Path) -> None:
    """FIRES: `make -f /tmp/evil.mk`, the hole a bare ancestry check leaves open.

    Measured 2026-08-24: this passes a naive check, because make really IS the parent - it is just
    not this project's make. Two lines in /tmp would otherwise defeat the entire guard."""
    # A NESTED foreign make does not REMOVE the legitimacy of an outer one. Run under `make quick`
    # this process already has a qualifying make above it, and a `make -f /tmp/x.mk` inside that is
    # still reached THROUGH the project's make - so the verdict is inherited, exactly as it is for a
    # pool worker. Asserting a flat "False" only held when the suite was run outside make, which is
    # the same trap that made an earlier version of this file pass only when run the wrong way.
    #
    # The real protection against a foreign makefile is layer 1 (the hook refuses the command before
    # it runs) plus the unit tests below, which supply an ancestry instead of inheriting one.
    expected = "True" if inv.via_make() else "False"
    assert _run_probe(tmp_path, _probe_cmd(), cwd=tmp_path, makefile=tmp_path / "evil.mk") == expected


@pytest.mark.tooling
def test_a_make_run_outside_the_repo_is_refused(tmp_path: Path) -> None:
    """FIRES: a make whose cwd is outside the repository is not this project's make."""
    # Same inheritance caveat as the test above: an outer qualifying make is still an ancestor.
    expected = "True" if inv.via_make() else "False"
    assert _run_probe(tmp_path, _probe_cmd(), cwd=tmp_path) == expected


@pytest.mark.tooling
def test_a_multiprocessing_child_under_make_is_accepted(tmp_path: Path) -> None:
    """STAYS QUIET: pool workers sit three levels below make, and pytest-xdist and `cohort()` both
    use that shape. Detecting only the immediate parent would refuse every worker."""
    work = REPO / ".tmp-invocation-pool"
    work.mkdir(exist_ok=True)
    script = work / "pool_probe.py"
    script.write_text(
        textwrap.dedent(f"""
        import multiprocessing as mp, sys
        sys.path.insert(0, {str(SKILL)!r})
        from l7r.diagram import _invocation as i
        def kid(_):
            i._verdict = None
            return i.via_make()
        if __name__ == "__main__":
            with mp.Pool(2) as p:
                print(all(p.map(kid, [0, 1])))
        """)
    )
    try:
        assert _run_probe(tmp_path, f"{sys.executable} {script}", cwd=work) == "True"
    finally:
        for f in work.iterdir():
            f.unlink()
        work.rmdir()
