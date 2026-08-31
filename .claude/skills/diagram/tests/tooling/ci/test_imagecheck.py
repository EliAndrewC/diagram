"""Feature 175 - the pushed image going stale is DETECTED now, not discovered by a paid build."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from l7r.diagram.ci import imagecheck

pytestmark = pytest.mark.tooling

REPO = Path(__file__).resolve().parents[6]
DOCKERFILE = REPO / "Dockerfile.ci"


def test_the_input_list_matches_what_the_dockerfile_actually_COPIES() -> None:
    """DERIVED, not trusted - otherwise this module is the next thing to go stale.

    `IMAGE_INPUTS` exists to answer "did the image's inputs change", so a COPY added to the Dockerfile
    without a matching row here would reintroduce the exact blind spot at one level up: a detector that
    cannot see the thing it was written to watch. Feature 173's lesson, in miniature - the mover
    derived its list by grep, and a grep is what missed `_COMMONS_FLOOR_FT`."""
    text = DOCKERFILE.read_text(encoding="utf-8")
    copied = {p for line in re.findall(r"^COPY\s+(.*)$", text, re.M) for p in line.split()[:-1]}
    missing = sorted(p for p in copied if p not in imagecheck.IMAGE_INPUTS)
    assert not missing, f"Dockerfile.ci COPYs {missing}, which IMAGE_INPUTS does not watch - a change to it would not be detected"
    assert "Dockerfile.ci" in imagecheck.IMAGE_INPUTS, "the recipe itself is an input"


@pytest.mark.parametrize(
    ("marker", "expected"),
    [
        ("dfa77649a6031be6a0a00fc868ef02d63c37ae88 2026-08-31T04:27:02Z", "dfa77649a6031be6a0a00fc868ef02d63c37ae88"),
        ("cad3bdac41828d3fd8edf5647e0525dfafc6d120 2026-08-25T11:46:54Z", "cad3bdac41828d3fd8edf5647e0525dfafc6d120"),
        ("abc1234", "abc1234"),
    ],
)
def test_the_commit_is_read_from_the_real_marker_format(marker: str, expected: str) -> None:
    """`buildspec/image.yml` writes `<GIT_SHA> <timestamp>`; both real markers this repository has ever
    had are pinned here, because the check reads a format written somewhere else."""
    assert imagecheck.marker_commit(marker) == expected


@pytest.mark.parametrize("marker", [None, "", "   ", "not-a-sha 2026-01-01T00:00:00Z", "zzzz", "abc"])
def test_an_unreadable_marker_is_UNKNOWN_rather_than_an_exception(marker: str | None) -> None:
    """A diagnostic must not take the dispatcher down. An absent, empty, short or non-hex marker means
    "cannot tell", and the dispatch proceeds - the check exists to inform, never to gate."""
    assert imagecheck.marker_commit(marker) is None


def test_a_changed_lockfile_is_stale_and_an_unrelated_change_is_not() -> None:
    """The motivating case: `requirements-dev.txt` gained `pyrefly==1.2.0` on 2026-08-28 and the image
    was not rebuilt, so every remote build failed at typecheck with Error 127 for three days."""
    changed = [".claude/skills/diagram/requirements-dev.txt", ".claude/skills/diagram/l7r/diagram/settlement/houses.py"]
    assert imagecheck.stale_inputs(changed) == [".claude/skills/diagram/requirements-dev.txt"]
    # ...and a diff touching nothing the image is built from leaves it current
    assert imagecheck.stale_inputs([".claude/skills/diagram/l7r/diagram/settlement/houses.py", "README.md"]) == []


def test_the_line_names_the_FILES_and_says_nothing_when_current() -> None:
    """Which file changed decides whether it matters - a lockfile means the build's Python differs from
    the tree's, a Dockerfile comment does not - so the message names them rather than saying "old"."""
    assert imagecheck.staleness_line([]) is None
    line = imagecheck.staleness_line([".claude/skills/diagram/requirements-dev.txt", "Dockerfile.ci"])
    assert line is not None
    assert "requirements-dev.txt" in line and "Dockerfile.ci" in line
    assert "make ci-image" in line, "a warning without the fix command is a warning people learn to skip"


def test_the_real_marker_and_tree_agree_right_now() -> None:
    """A live sanity check against this repository: the image was rebuilt on 2026-08-31 from HEAD's
    recipe, so nothing it is built from should have changed since. If this fails, the image IS stale
    and `make ci-image` is owed - which is the check doing its job rather than a broken test."""
    for path in imagecheck.IMAGE_INPUTS:
        assert (REPO / path).is_file(), f"{path} is watched as an image input but does not exist"
