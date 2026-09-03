"""Feature 177 FR-005/FR-006/FR-006a/FR-006c - what a remote build does not check out.

THE ROSTER IS THE RISK, not the mechanism. `git sparse-checkout` is well understood; a hand-kept list
of "things nothing reads" is not, because it is true on the day it is written and silently false
afterwards. A test that starts reading an excluded path would not fail in the build - it would SKIP,
or find nothing, or count zero, which is this repository's named worst case ("a check that never runs
looks exactly like a check that passes"). So the list lives in one file and this module guards it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.tooling

HERE = Path(__file__).resolve().parents[3]
REPO = HERE.parents[2]
ROSTER = REPO / "buildspec" / "sparse-excludes.txt"
BUILDSPECS = [REPO / "buildspec" / name for name in ("check.yml", "merge.yml")]


def entries(text: str) -> list[tuple[str, list[str]]]:
    """The roster's live patterns, each with its declared PRODUCERS.

    A producer is the module that WRITES an excluded artifact, and it necessarily names the path it
    writes to - `tools/placement_stages.py` defaults `--out` to the very directory the build stops
    checking out. That is not rot, and the first version of the rot check below failed on it within a
    minute. Producers are DECLARED here rather than the scan being quietly narrowed to `tests/`,
    because a reader hiding in an engine module is exactly what this check exists to catch, and
    because a declared exemption can be checked for staleness while a narrowed scan cannot."""
    out: list[tuple[str, list[str]]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("producer:"):
            assert out, "a producer: line must follow the pattern it belongs to"
            out[-1][1].append(line.removeprefix("producer:").strip())
            continue
        out.append((line, []))
    return out


def patterns(text: str) -> list[str]:
    return [p for p, _producers in entries(text)]


def needle(pattern: str) -> re.Pattern[str]:
    """A regex matching how source code would REFER to something under `pattern`.

    Lifted to module level and given a plain string rather than reading the tree, so the rot check
    below can be driven with a planted reference (constitution X, the GM's feature-146 doctrine: an
    inner function that is hard to test gets lifted out). The needle keeps the trailing slash of the
    owning directory on purpose - `make placement-stages` in a docstring is a COMMAND, not a path, and
    a needle without the slash would fire on it."""
    body = pattern.lstrip("/").rstrip("/")
    parts = body.split("/")
    if "*" in parts[-1]:  # a file glob: <dir>/<glob>
        directory, glob = parts[-2], parts[-1]
        return re.compile(re.escape(directory) + r"/[^\s\"']*" + re.escape(glob.lstrip("*")))
    return re.compile(re.escape(parts[-1]) + "/")


def rot_violations(pats: list[tuple[str, list[str]]], sources: dict[str, str]) -> list[str]:
    """Every (file, pattern) where source code refers to a path the build will not check out, other
    than a declared producer of that path."""
    return [f"{name} refers to {p}, which the remote build does not check out" for p, producers in pats for name, text in sources.items() if name not in producers and needle(p).search(text)]


def _sources() -> dict[str, str]:
    out = {}
    for base in (HERE / "l7r", HERE / "tests"):
        for f in base.rglob("*.py"):
            if f.resolve() == Path(__file__).resolve():
                continue
            out[str(f.relative_to(HERE))] = f.read_text(encoding="utf-8", errors="ignore")
    return out


def test_the_roster_exists_and_every_pattern_is_anchored() -> None:
    pats = patterns(ROSTER.read_text(encoding="utf-8"))
    assert pats, "an empty roster excludes nothing while looking configured"
    for p in pats:
        assert p.startswith("/"), f"{p!r} must be anchored at the repository root, or it matches at any depth"
        assert ".claude/skills/diagram/" in p, f"{p!r} is outside the skill; widen deliberately, not by accident"


def test_nothing_the_gate_runs_reads_an_excluded_path() -> None:
    """FR-006c. The exclusion is only sound while it is true, and it is exactly the kind of claim that
    rots without anyone touching it."""
    bad = rot_violations(entries(ROSTER.read_text(encoding="utf-8")), _sources())
    assert not bad, "the sparse exclusions have rotted:\n  " + "\n  ".join(bad)


def test_every_declared_producer_still_exists_and_still_names_its_output() -> None:
    """A declared exemption is a claim, and a stale one silently widens the guard's blind spot. If a
    producer is renamed or stops writing there, the declaration must go with it."""
    sources = _sources()
    for pattern, producers in entries(ROSTER.read_text(encoding="utf-8")):
        for name in producers:
            assert name in sources, f"{name} is declared a producer of {pattern} but does not exist"
            assert needle(pattern).search(sources[name]), f"{name} no longer writes to {pattern}; drop the producer: line"


def test_the_rot_check_FIRES_on_a_planted_reference() -> None:
    """Proven, not assumed - the roster guard is worthless if it cannot see a real reference, and its
    negative form passes green either way."""
    pats = [("/.claude/skills/diagram/wip/*.html", []), ("/.claude/skills/diagram/dev/placement-stages/", ["writer.py"])]
    assert rot_violations(pats, {"clean.py": "open('pool/hamlets/inashiro/inashiro.json')"}) == []
    planted = {"reader.py": "PAGE = 'wip/kuwabata-grid.html'"}
    assert len(rot_violations(pats, planted)) == 1
    planted2 = {"reader.py": "OUT = os.path.join(SKILL, 'dev', 'placement-stages/', 'hamlet-placement.html')"}
    assert len(rot_violations(pats, planted2)) == 1
    # ...the DECLARED producer of that same path is not a violation, and nothing else gets the pass
    assert rot_violations(pats, {"writer.py": "OUT = 'placement-stages/'"}) == []
    # ...and the shape that must NOT fire: the make target named in prose, which is how
    # tests/tools/test_placement_stages.py legitimately mentions it.
    assert rot_violations(pats, {"doc.py": '"""run by `make placement-stages`."""'}) == []


def test_the_build_reads_the_roster_rather_than_carrying_its_own_copy() -> None:
    """Three consumers, one source. A second copy of a roster is how the copies disagree."""
    run_sh = (REPO / "buildspec" / "run.sh").read_text(encoding="utf-8")
    assert "buildspec/sparse-excludes.txt" in run_sh, "run.sh must read the roster"
    assert "sparse-checkout set --no-cone" in run_sh
    # The shell and this module must agree on what a live pattern IS. They did not at first: the
    # loop skipped blanks and comments only, so a `producer:` line went to git as `!producer: ...`,
    # which git accepts and matches nothing - the roster would look applied while carrying a pattern
    # that can never fail. Caught by running the loop by hand, not by a test, which is why there is
    # now a test.
    assert "producer:*) continue" in run_sh, "run.sh must skip producer: metadata, not pass it to git as a pattern"
    for p in patterns(ROSTER.read_text(encoding="utf-8")):
        assert p not in run_sh, f"{p!r} is inlined in run.sh as well as declared in the roster"


def test_both_buildspecs_stop_materializing_head_and_fetch_the_roster() -> None:
    """The 43 s INSTALL was the CHECKOUT, not the fetch, so the clone takes nothing at all and
    `run.sh` checks out what survives the roster. Simulated end to end 2026-09-03: 0.9 s to clone and
    31.5 s to sparse-checkout, against 66 s for the full clone this replaces."""
    for spec in BUILDSPECS:
        text = spec.read_text(encoding="utf-8")
        assert "--no-checkout" in text, f"{spec.name}: the clone must not materialize HEAD"
        assert "buildspec/sparse-excludes.txt" in text, f"{spec.name}: run.sh needs the roster before it can check anything out"


def test_only_three_places_reach_a_bundles_render() -> None:
    """THE CENSUS THAT MAKES THE ROSTER'S EVIDENCE AFFIRMATIVE, pinned so it stays true.

    FR-006 refuses an exclusion whose evidence is "no reader was found". What promotes this roster
    past that bar is that render access has ONE API - `poolmaps.MapBundle.path()` - so the readers can
    be ENUMERATED rather than searched for. If a fourth call site appears, the roster's evidence has
    to be re-taken, and that is what this test says."""
    sites = sorted(name for name, text in _sources().items() if re.search(r'\.path\("\.(svg|png|html)"\)', text))
    assert sites == [
        "l7r/diagram/pipeline/pool_index.py",  # existence probes only; a missing render reads "render not synced"
        "tests/pipeline/test_poolmaps.py",  # asserts the path STRING, on a tmp fixture pool
        "tests/test_villages.py",  # the raster/viewBox agreement - hamlets tier, real pool, renders RETAINED
    ], f"a new reader of a bundle render appeared: {sites} - re-take the roster's evidence before trusting it"
