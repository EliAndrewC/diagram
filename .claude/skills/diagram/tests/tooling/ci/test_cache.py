"""Feature 175 - the generation cache that travels between builds.

`tooling` tree: these read the buildspecs and the dispatcher source, so they run at the gate and in
the full run, and in `make quick` only while the tooling has changed (tests/CLAUDE.md).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from l7r.diagram._invocation import OPERATIONS
from l7r.diagram.ci import config
from l7r.diagram.ci.dispatch import cache_location, registered_operation

pytestmark = pytest.mark.tooling

HERE = Path(__file__).resolve().parents[3]
REPO = HERE.parents[2]
BUILDSPECS = [REPO / "buildspec" / name for name in ("check.yml", "merge.yml")]
# Feature 177: the two paths that carry the `hooks-test` freshness state between builds. Named once,
# here, because three files have to agree about them - both buildspecs and `run.sh`'s restore.
FRESHNESS_PATHS = ["repo/.git/gate-green-hooks", "repo/.git/hooks-test/**/*"]


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

    # FEATURE 177: THE TEST NOW VARIES THE OPERATION DIMENSION, because the version above did not and
    # therefore could not have caught the fix that added one. It enumerated projects x scopes and
    # asserted `len(locations) == 4`, so a fourth parameter with a default leaves it green while the
    # property it names is gone - which is the shape of every guard this project has had to repair.
    ops = sorted({name for name, cost in OPERATIONS.values() if cost == "expensive"})
    every = {cache_location("bkt", p, s, o) for p in projects for s in scopes for o in [None, *ops]}
    assert len(every) == len(projects) * len(scopes) * (1 + len(ops)), "one location per (project, scope, registered operation)"
    assert len(every) < 200, f"the ceiling is finite and small; it is {len(every)}"


def test_an_operation_does_not_overwrite_the_gates_cache() -> None:
    """FEATURE 177, FR-018, MEASURED: on 2026-08-31 the green reference gate and both
    `TARGET=tripwire` builds all reported
    `location = gm-assistant-ci-.../cache/gm-assistant-check/reference`, and the bucket held ONE cache
    object where 175's D2 expected four - an operation's `ctx.scope` stays `reference` and only
    `CI_SCOPE` becomes `operation`, so the two clobbered each other. Performance only: the gencache key
    is content-derived, so a foreign entry can only MISS."""
    gate = cache_location("bkt", config.PROJECT_CHECK, "reference")
    trip = cache_location("bkt", config.PROJECT_CHECK, "reference", "tripwire")
    assert gate != trip, "an operation must not write to the gate's cache object"
    assert trip.startswith(gate + "/"), "and it should be legible as a child of it, not an unrelated key"


def test_the_operation_in_the_key_is_the_REGISTERED_name_not_the_raw_target() -> None:
    """FR-018a, and the reason the bound survives the fix. `__main__.py` validates only
    `a.target.split()[0]` and passes the WHOLE string on as `ctx.operation`, so keying on it would give
    one S3 object per argument spelling - the GM's named failure, reintroduced by the fix for a
    different defect."""
    assert registered_operation("tripwire") == "tripwire"
    assert registered_operation("cohort SEEDS=8") == registered_operation("cohort SEEDS=9") == "cohort"
    assert registered_operation(None) is None and registered_operation("") is None
    assert registered_operation("not-a-registered-operation") is None, "an unregistered head declines to partition rather than inventing a key"


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
    # FEATURE 177: THE INVARIANT IS WIDENED AND STILL CLOSED. This used to be
    # `all(p.startswith(".gencache/"))`, which was right until the freshness state had to travel too -
    # and then it forbade the change outright. The fix is NOT "and `.git` is allowed": it is an exact
    # set. Anything else in the cache is a deliberate decision that belongs in a diff, not a path
    # that slipped in behind a prefix test.
    extra = [p for p in paths if not p.startswith("repo/.claude/skills/diagram/.gencache/")]
    assert extra == FRESHNESS_PATHS, f"the cache carries the gencache set plus exactly the freshness state; found {extra}"


def test_the_restore_cannot_be_fooled_by_a_cache_that_contains_a_dot_git() -> None:
    """FR-004, and the failure it prevents is one this repository has already PAID for.

    CodeBuild restores its S3 cache during DOWNLOAD_SOURCE, before the install phase clones - so on
    any build after the first, `repo/` already exists holding nothing but cached paths. `run.sh` sets
    it aside and lays it back over the checkout. It used to detect that with `[ ! -d repo/.git ]`,
    which is exactly wrong once the cache carries `repo/.git/hooks-test/**`: the directory exists, the
    set-aside is skipped, and `mv bootstrap repo` moves bootstrap INSIDE the restored tree, leaving
    `cd repo` somewhere with no `.git`. That is build a48b730d - exit 128, one billed minute - and
    widening the cache would have brought it straight back."""
    run_sh = (REPO / "buildspec" / "run.sh").read_text(encoding="utf-8")
    # A MENTION IS NOT AN INVOCATION - this project's oldest guard lesson, and this test tripped over
    # it within a minute of being written: the note explaining WHY the old form was wrong quotes the
    # old form, so a whole-file substring search fails on correct code. Only executable lines count.
    code = "\n".join(ln for ln in run_sh.splitlines() if not ln.lstrip().startswith("#"))
    assert "[ ! -e repo/.git/HEAD ]" in code, "the restore must ask whether a real repository is there, not whether a .git exists"
    assert "[ ! -d repo/.git ]" not in code, "the directory test is the a48b730d failure once .git paths are cached"


def test_the_freshness_state_is_content_keyed_so_a_changed_guard_still_runs() -> None:
    """FR-002. The whole safety argument for FR-001 is that neither stamp encodes anything but file
    CONTENT, so a build can only skip a suite whose inputs are byte-identical to the ones that last
    went green. Asserted against the code rather than taken from the spec's A2."""
    stamp = (REPO / "scripts" / "gate-stamp.py").read_text(encoding="utf-8")
    assert '"hooks": ("scripts", ("*.sh", "*.py"))' in stamp, "the hooks area is derived from the files themselves"
    assert "GATE_RECIPE" in stamp, "the stamp is salted, so a change to what the gate MEANS retires every record"
    makefile = (HERE / "Makefile").read_text(encoding="utf-8")
    assert "sha256sum" in makefile and "_hookdeps.py" in makefile, "the per-suite stamp is a hash of that suite's derived dependency set"


def test_only_a_BUILD_can_write_the_freshness_state_a_build_restores() -> None:
    """FR-003, checked rather than argued - in the one package whose whole job is refusing to take the
    dispatcher's word for anything.

    The property that makes FR-001 safe is that a remote gate skips only what a REMOTE gate proved. It
    holds because of where the cache comes from: CodeBuild populates its own cache location in
    POST_BUILD, and the dispatcher never writes there. If the dispatcher ever uploaded to the cache
    prefix, a laptop's stamp could reach a build and vouch for a suite no build ever ran."""
    src = (HERE / "l7r" / "diagram" / "ci" / "dispatch.py").read_text(encoding="utf-8")
    # every put the dispatcher makes, and what it targets
    puts = re.findall(r"put_object\(\s*[^,]+,\s*([^,]+),", src)
    assert puts, "the dispatcher does write to S3; this test is about WHERE"
    for target in puts:
        assert "cache" not in target, f"the dispatcher must never write into the cache location: {target}"
    assert "cache_location" in src, "it names the location for start_build only"
    assert "put_object" not in src.split("def cache_location")[1].split("\ndef ")[0], "cache_location computes a key; it does not upload"


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
