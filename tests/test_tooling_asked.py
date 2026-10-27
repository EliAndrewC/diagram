"""`tests/conftest.py` `tooling_asked`: a run that names the tooling tests runs them, whatever the tooling hash says."""

from tests.conftest import tooling_asked


def test_a_run_asks_for_the_tooling_tests_by_marker_file_or_tree() -> None:
    assert tooling_asked("tooling", [])
    assert tooling_asked("", ["tests/tooling/test_land_claims_wait.py"])
    assert tooling_asked("", ["tests/x/test_y.py::test_z"])
    assert tooling_asked("", ["tests/tooling"]) and tooling_asked("", ["tests/tooling/"]), "the tree itself (feature 417 T54: exit 5 at make land)"
    assert not tooling_asked("", ["tests/hamletgen/"]), "another tree leaves the skip to the hash"
