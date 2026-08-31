"""Feature 175 - the generation cache that travels between builds.

`tooling` tree: these read the buildspecs and the dispatcher source, so they run at the gate and in
the full run, and in `make quick` only while the tooling has changed (tests/CLAUDE.md).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from l7r.diagram.ci import config
from l7r.diagram.ci.dispatch import cache_location

pytestmark = pytest.mark.tooling

HERE = Path(__file__).resolve().parents[3]
BUILDSPECS = [HERE.parents[2] / "buildspec" / name for name in ("check.yml", "merge.yml")]


def _cache_paths(text: str) -> list[str]:
    """The `paths:` entries of the buildspec's top-level `cache:` block."""
    block = re.search(r"^cache:\n((?:[ \t].*\n|\n)+)", text, re.M)
    assert block, "the buildspec declares no top-level cache: block"
    return re.findall(r"^\s*-\s*'([^']+)'", block.group(1), re.M)


def test_the_cache_location_cannot_grow_with_the_number_of_builds() -> None:
    """FR-005, the GM's named failure: *"if we were uploading many megabytes worth of content to
    Amazon S3 on every run and then never cleaning it up, then that would be bad."*

    CodeBuild writes one archive per cache location, so the object count is exactly the number of
    distinct locations this function can return. Keyed on (project, scope) that is FOUR, whatever the
    commit is - which is why the commit SHA must never reach it."""
    projects = (config.PROJECT_CHECK, config.PROJECT_MERGE)
    scopes = ("reference", "full")
    locations = {cache_location("bkt", p, s) for p in projects for s in scopes}
    assert len(locations) == 4, "one location per (project, scope) and no more"

    # ...and the SAME inputs give the SAME location on every build - the property that bounds it.
    assert cache_location("bkt", config.PROJECT_CHECK, "full") == cache_location("bkt", config.PROJECT_CHECK, "full")


def test_the_cache_location_never_carries_a_commit_sha() -> None:
    """The failure mode FR-005 forbids by name: a SHA in the location is one S3 object per commit,
    for ever. Asserted rather than trusted, because it is a one-word edit away at any time."""
    sha = "b137a2193c3d4e5f60718293a4b5c6d7e8f90123"
    loc = cache_location("bkt", config.PROJECT_CHECK, "full")
    assert sha not in loc and sha[:12] not in loc
    assert not re.search(r"\b[0-9a-f]{7,}\b", loc), f"{loc!r} looks like it carries a hex id"


def test_the_two_buildspecs_cache_exactly_the_same_paths() -> None:
    """They are separate files because each is passed whole as `buildspecOverride`, so nothing makes
    them agree except this test. A drift would cache different things for the check and merge
    projects and be invisible until someone compared two builds by hand."""
    check, merge = (_cache_paths(p.read_text(encoding="utf-8")) for p in BUILDSPECS)
    assert check == merge, "check.yml and merge.yml must cache the same paths"
    assert check, "the cache block lists no paths, which caches nothing while looking configured"


@pytest.mark.parametrize("spec", BUILDSPECS, ids=lambda p: p.name)
def test_the_raster_and_the_page_are_NOT_cached(spec: Path) -> None:
    """FR-003 and FR-008, and the reason each is a defect rather than a saving.

    `.png`: a gate-built entry HAS none (the regen child runs `DIAGRAM_SKIP_RENDER=1`), and
    `gencache.load()` DELETES a standing output its entry lacks. Seeding a container with a raster no
    remote roll produces re-creates the 2026-08-17 defect - four maps shipped a PNG from the previous
    roll beside a current `.json` and `.svg`, matching mtimes, past two review rounds.

    `.html`: ~65 MB across five maps and settled as unread by the gate - no test in `tests/` or
    `tests/full/` reads a pool map's page, `pool_index` links it only `if os.path.exists(...)`, and
    `render_cache`'s missing-render check looks at `.svg` and `.png` only."""
    paths = _cache_paths(spec.read_text(encoding="utf-8"))
    assert not [p for p in paths if p.endswith(".png") or "*.png" in p], "a gate-built entry has no .png; caching one re-creates the stale-raster defect"
    assert not [p for p in paths if p.endswith(".html") or "*.html" in p], "the .html is ~65 MB and no gate test reads a pool map's page"


@pytest.mark.parametrize("spec", BUILDSPECS, ids=lambda p: p.name)
def test_the_cached_paths_are_what_a_HIT_needs(spec: Path) -> None:
    """FR-002: the set is derived from what `gate_obtain` proves it needs (research R3) - the
    manifest the gate judges, the `.svg` the z-order audit reads, and the coverage data without which
    a hit cannot happen at all. A cache missing any of these would restore and still MISS."""
    paths = _cache_paths(spec.read_text(encoding="utf-8"))
    joined = "\n".join(paths)
    assert "*.json" in joined, "the manifest is what the gate judges"
    assert "*.svg" in joined, "_channels_under_plots reads the svg"
    assert "coverage." in joined, "without the coverage data gate_obtain cannot HIT at all"
    assert all(p.startswith("repo/.claude/skills/diagram/.gencache/") for p in paths), f"a path escapes the gencache: {paths}"


def test_the_dispatcher_passes_the_cache_to_start_build() -> None:
    """A static test, because the alternative is a live paid build. The cache is useless unless the
    override actually reaches `start_build` - a `cache:` block in a buildspec does nothing on its own
    when the PROJECT has no cache configured, which is exactly our case (the projects were created
    NO_SOURCE with a placeholder)."""
    src = (HERE / "l7r" / "diagram" / "ci" / "dispatch.py").read_text(encoding="utf-8")
    call = re.search(r"started = ctx\.client\.start_build\((.*?)\)\n", src, re.S)
    assert call, "the start_build call moved; this test guards its kwargs"
    assert "cache_kw" in call.group(1), "start_build must receive the cacheOverride"
    assert "cacheOverride" in src and "cache_location(" in src
