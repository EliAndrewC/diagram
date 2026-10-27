"""`tools/perf_share.py` (feature 438): a module's share of each stage's time and its callers, read from the kept raw profiles,
a stage with none profiled then and said so."""

import cProfile
from pathlib import Path

import pytest

from l7r.diagram.tools import perf_share as ps


def _profile(path: Path) -> str:
    """A real cProfile of a caller outside a module calling into it, dumped to `path`."""
    from l7r.diagram.settlement._geom import primitives as prim

    def outside() -> float:
        return sum(prim.seg_dist(float(i), 1.0, (0.0, 0.0), (10.0, 0.0)) for i in range(2000))

    prof = cProfile.Profile()
    prof.enable()
    outside()
    prof.disable()
    prof.dump_stats(str(path))
    return str(path)


def test_a_stage_reads_its_total_the_modules_share_the_hotspots_and_the_callers(tmp_path: Path) -> None:
    lines = ps.share(_profile(tmp_path / "x-seed25-hh40-web.prof"), ps.MODULE)
    assert lines[0].startswith("  profiled ") and "primitives.py self" in lines[0] and "%" in lines[0]
    assert "largest self time in the stage:" in lines[1] and lines[2].strip().endswith(")")
    callers = lines[lines.index(next(ln for ln in lines if ln.startswith("  callers of"))) + 1 :]
    assert any("seg_dist" in ln and "<genexpr>" in ln and "calls" in ln for ln in callers), "the outside caller, not seg_dist calling seg_closest"
    assert not any("seg_closest" in ln and "primitives.py" in ln.split("from")[-1] for ln in callers), "the module calling itself is not a caller"
    assert ps.share(_profile(tmp_path / "y.prof"), "no/such/module.py")[-1].strip() == "none"


def test_a_kept_profile_is_found_by_name_then_by_seed_size_and_stage(tmp_path: Path) -> None:
    for name in ("20261027T000000Z-seed25-hh40-web.prof", "20261027T010000Z-seed25-hh40-web.prof", "20261027T020000Z-seed25-web.prof", "20261027T030000Z-seed25-hh20-web.prof"):
        (tmp_path / name).write_text("")
    assert ps.kept("web", 25, 40, [], str(tmp_path)).endswith("20261027T010000Z-seed25-hh40-web.prof"), "the newest of the seed and size"
    assert ps.kept("web", 25, 40, ["old-seed25-web.prof"], str(tmp_path)) == "old-seed25-web.prof", "a named profile first"
    assert ps.kept("field", 25, 40, ["old-seed25-web.prof"], str(tmp_path)) is None


def test_main_reads_kept_profiles_profiles_a_missing_stage_and_names_a_refusal(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    named = _profile(tmp_path / "a-seed25-web.prof")
    made: list[str] = []

    def profile(seed: int, stage: str, top: int, households: int | None) -> tuple[str, str]:
        made.append(stage)
        if stage == "hinterland":
            raise ValueError("the roll refused")
        return "", _profile(tmp_path / f"b-seed{seed}-hh{households}-{stage}.prof")

    monkeypatch.setattr(ps.perf_profile, "RAW_DIR", str(tmp_path / "none"))
    assert ps.main(["--stages", "web,field,hinterland", "--profiles", named], profile=profile) == 0
    out = capsys.readouterr().out
    assert "a-seed25-web.prof" in out and made == ["field", "hinterland"], "web read from its kept profile, the others profiled"
    assert "no kept profile - profiling it now" in out and "not profiled - ValueError: the roll refused" in out
    assert "across 2 stage(s)" in out and "upper bound" in out
