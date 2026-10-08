"""Site selection for `tools/cache_audit.py`.

`cache_audit` is a by-hand driver, and since 2026-09-02 it is under the 100% rule like everything
else (GM: *"a new tool absolutely should silently owe one hundred percent coverage the day it
lands"*). Its SITE SELECTION was always testable - pure logic over an AST, and getting it wrong is
what made a 3-trial run take 19 attempts and eleven minutes while auditing the cache exactly three
times. The orchestration below it is tested by stubbing the four subprocess seams (`gens`,
`executed_lines`, `sweep`, `snapshot`) and pointing `HERE` at a temporary tree, because a test that
let this module run for real would mutate the engine's own source.

Both filters below exist because a mutation that changes no byte tests NOTHING about the cache, and
before 2026-08-17 such a trial printed the same `[OK ]` as a real one.
"""

import ast
import json
import os
import pathlib
import subprocess
from typing import Any

import pytest

from l7r.diagram.tools import cache_audit

pytestmark = pytest.mark.tooling

# line 1: a default argument (15) - evaluated at DEFINITION time, so its line is always "executed"
# line 2: a body literal in a function the maps DO call
# line 5/6: a function the maps never call
SRC = "def used(a, b=15):\n    return a * 3\n\n\ndef never_called():\n    return 99 * 7\n"
EXECUTED = {1, 2, 5}  # both `def` lines run at import; only `used`'s body actually runs


def test_numeric_sites_skips_default_argument_literals():
    """A default's literal sits on the `def` line, which coverage always reports as executed even
    when nothing ever calls the function - so `covered` alone cannot see that it is inert. And when
    every caller passes the argument explicitly, perturbing it moves nothing at all. That pair is
    where most of the eleven minutes went."""
    values = [ast.literal_eval(s[3]) for s in cache_audit.numeric_sites(SRC, EXECUTED)]
    assert 15 not in values, "a default-argument literal was offered as a mutation site"


def test_numeric_sites_skips_a_line_the_maps_never_execute():
    """A literal in a function no audited map calls cannot change an artifact, so mutating it is a
    guaranteed-wasted sweep pair. It is also provably safe to exclude: with the artifacts identical,
    a cached sweep and a fresh sweep agree no matter what the key does."""
    sites = cache_audit.numeric_sites(SRC, EXECUTED)
    assert [s[0] for s in sites] == [2], f"expected only the executed body literal on line 2, got {sites}"


def test_numeric_sites_still_finds_the_literal_that_matters():
    """The filters must not be so eager that nothing survives - an empty candidate pool is the same
    silent no-op in the other direction."""
    sites = cache_audit.numeric_sites(SRC, EXECUTED)
    assert len(sites) == 1 and ast.literal_eval(sites[0][3]) == 3
    lineno, col, end_col, text = sites[0]
    assert SRC.splitlines()[lineno - 1][col:end_col] == text


# ---------------------------------------------------------------------------------------------
# Feature 174: the orchestration, with every subprocess seam stubbed and HERE redirected.
# ---------------------------------------------------------------------------------------------

_MUTABLE = "def draw(x):\n    return x * 7\n"


@pytest.fixture
def _tree(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    """A fake skill root with one mutable engine file, so `main` can rewrite source safely."""
    rel = os.path.join(cache_audit.ENGINE, "settlement", "geom.py")
    (tmp_path / os.path.dirname(rel)).mkdir(parents=True)
    (tmp_path / rel).write_text(_MUTABLE)
    monkeypatch.setattr(cache_audit, "HERE", str(tmp_path))
    monkeypatch.setattr(cache_audit, "gens", lambda _all: ["pool/hamlets/x/x.gen.py"])
    monkeypatch.setattr(cache_audit, "executed_lines", lambda _paths: {rel: {1, 2}})
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a[0] if a else [], 0, "", ""))
    return tmp_path


def test_mutate_nudges_an_int_by_one_and_a_float_by_a_half() -> None:
    """The perturbation has to be big enough to move an artifact and small enough not to break
    generation - and it must respect the literal's type, or a float site becomes an int and the
    mutation is testing the type change rather than the value."""
    src = "a = 7\nb = 2.5\n"
    assert cache_audit.mutate(src, (1, 4, 5, "7")) == "a = 8\nb = 2.5\n"
    assert cache_audit.mutate(src, (2, 4, 7, "2.5")) == "a = 7\nb = 3.0\n"


def test_sweep_treats_a_TIMEOUT_as_a_failed_trial_rather_than_waiting_it_out(monkeypatch: pytest.MonkeyPatch) -> None:
    """ "a hung audit looks exactly like a slow one" - a perturbed literal can put a placer into a far
    longer search, so the sweep is bounded and a timeout is False, not an exception."""
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: subprocess.CompletedProcess([], 0, "", ""))
    assert cache_audit.sweep(["a.gen.py"], use_cache=True) is True

    def slow(*_a: Any, **_kw: Any) -> Any:
        raise subprocess.TimeoutExpired("regen", 60)

    monkeypatch.setattr(subprocess, "run", slow)
    assert cache_audit.sweep(["a.gen.py"], use_cache=True) is False


def test_sweep_passes_no_cache_only_when_asked(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[list[str]] = []
    monkeypatch.setattr(subprocess, "run", lambda cmd, **k: (seen.append(cmd), subprocess.CompletedProcess(cmd, 0, "", ""))[1])
    cache_audit.sweep(["a.gen.py"], use_cache=True)
    cache_audit.sweep(["a.gen.py"], use_cache=False)
    assert "--no-cache" not in seen[0] and "--no-cache" in seen[1]


def test_snapshot_reads_the_json_and_svg_but_never_the_png(tmp_path: pathlib.Path) -> None:
    """ "the PNG is a pure function of the SVG" - comparing it too would double the bytes and add no
    information, and a render-time nondeterminism would look like a cache failure."""
    gen = tmp_path / "m.gen.py"
    gen.write_text("x")
    for suffix, body in ((".json", b"J"), (".svg", b"S"), (".png", b"P")):
        (tmp_path / f"m{suffix}").write_bytes(body)
    snap = cache_audit.snapshot([str(gen)], str(tmp_path / "where"))
    assert snap == {"m.json": b"J", "m.svg": b"S"}


def test_a_census_that_finds_NO_mutable_literal_refuses_rather_than_reporting_health(_tree: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """ "A census that silently returns nothing is indistinguishable from a clean bill of health" -
    the exact shape this tool's own vacuous trials had."""
    monkeypatch.setattr(cache_audit, "executed_lines", lambda _paths: {})
    assert cache_audit.main([]) == 1
    out = capsys.readouterr().out
    assert "REFUSING" in out and "no mutable literal" in out


def _snapshots(*answers: dict[str, bytes]) -> Any:
    """Stub `snapshot`, answering the calls in order: clean, then (with_cache, without) per trial."""
    seq = list(answers)

    def fake(_paths: list[str], _where: str) -> dict[str, bytes]:
        return seq.pop(0) if seq else {}

    return fake


def test_a_trial_whose_sweeps_AGREE_is_OK_and_the_source_is_restored(_tree: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The healthy case: the mutation moved an artifact (so it tested something) and the cached and
    fresh sweeps produced the same bytes. The engine file must come back byte-identical - a tool that
    left the source mutated would be worse than no tool."""
    rel = os.path.join(cache_audit.ENGINE, "settlement", "geom.py")
    monkeypatch.setattr(cache_audit, "snapshot", _snapshots({"m.json": b"CLEAN"}, {"m.json": b"MOVED"}, {"m.json": b"MOVED"}))
    assert cache_audit.main(["--trials", "1"]) == 0
    out = capsys.readouterr().out
    assert "[OK ]" in out and "moved 1 of 1 artifacts" in out
    assert (_tree / rel).read_text() == _MUTABLE, "the engine source is restored exactly"
    assert "dirty after restore" in out


def test_a_trial_whose_sweeps_DISAGREE_is_a_STALE_finding_and_fails_the_run(_tree: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The whole point of the tool: the cached sweep served different bytes from the fresh one."""
    monkeypatch.setattr(cache_audit, "snapshot", _snapshots({"m.json": b"CLEAN"}, {"m.json": b"CACHED"}, {"m.json": b"FRESH"}))
    assert cache_audit.main(["--trials", "1"]) == 1
    out = capsys.readouterr().out
    assert "[STALE]" in out and "CACHE SERVED STALE ARTIFACTS" in out
    assert "the cache is serving stale maps" in out


def test_a_mutation_that_moved_NOTHING_is_not_counted_as_a_trial(_tree: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Measured on this tool's first run: 2 of 3 trials were vacuous and printed an identical `[OK ]`,
    so a run of three had audited one. A mutation that moves no artifact tested nothing about the
    cache - the sweeps agreed because there was nothing to disagree about - so it is a skip."""
    monkeypatch.setattr(cache_audit, "snapshot", _snapshots({"m.json": b"SAME"}, {"m.json": b"SAME"}, {"m.json": b"SAME"}))
    assert cache_audit.main(["--trials", "1"]) == 0
    out = capsys.readouterr().out
    assert "[----]" in out and "moved nothing, so it tested nothing" in out
    assert "0 mutation(s) audited" in out and "1 vacuous" in out
    assert "only 0 of 1 requested trials moved an artifact" in out, "and the shortfall is a finding, stated"


def test_a_mutation_that_moved_nothing_but_STILL_disagrees_is_never_swallowed(_tree: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The comment at that branch says `differing` is checked FIRST for exactly this reason. Two
    sweeps that disagree while moving nothing is a genuine finding, and the vacuous skip must not
    eat it."""
    monkeypatch.setattr(cache_audit, "snapshot", _snapshots({"m.json": b"SAME"}, {"m.json": b"SAME"}, {"m.json": b"OTHER"}))
    assert cache_audit.main(["--trials", "1"]) == 1
    assert "[STALE]" in capsys.readouterr().out


def test_a_sweep_that_FAILS_is_skipped_rather_than_reported_as_a_cache_finding(_tree: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """ "The mutation broke generation (or hung it) - not a cache finding." A site can land anywhere
    in the engine, so this is routine rather than rare, and reporting it as STALE would cry wolf."""
    monkeypatch.setattr(cache_audit, "sweep", lambda _p, use_cache: False)
    monkeypatch.setattr(cache_audit, "snapshot", _snapshots({}, {}, {}))
    assert cache_audit.main(["--trials", "1"]) == 0
    assert "[skip]" in capsys.readouterr().out


def test_a_mutation_that_does_not_PARSE_is_skipped_and_the_file_restored(_tree: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The perturbation is textual, so it can in principle produce something that will not compile;
    the file is put back before the next trial rather than left broken."""
    rel = os.path.join(cache_audit.ENGINE, "settlement", "geom.py")
    monkeypatch.setattr(cache_audit, "mutate", lambda _src, _site: "def draw(x:\n")
    assert cache_audit.main(["--trials", "1"]) == 0
    assert (_tree / rel).read_text() == _MUTABLE


def test_EVERY_file_a_trial_touched_is_restored_not_just_the_last(_tree: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The `finally` restores from `originals`, which accumulates. Restoring only the last file was
    the shape that would leave an earlier engine file mutated after a multi-trial run."""
    rel_a = os.path.join(cache_audit.ENGINE, "settlement", "geom.py")
    rel_b = os.path.join(cache_audit.ENGINE, "waterfields", "comb.py")
    (_tree / os.path.dirname(rel_b)).mkdir(parents=True, exist_ok=True)
    (_tree / rel_b).write_text(_MUTABLE)
    monkeypatch.setattr(cache_audit, "executed_lines", lambda _paths: {rel_a: {1, 2}, rel_b: {1, 2}})
    monkeypatch.setattr(cache_audit, "snapshot", _snapshots({"m.json": b"C"}, {"m.json": b"A"}, {"m.json": b"A"}, {"m.json": b"B"}, {"m.json": b"B"}))
    cache_audit.main(["--trials", "2"])
    assert (_tree / rel_a).read_text() == _MUTABLE and (_tree / rel_b).read_text() == _MUTABLE


def test_numeric_sites_skips_a_literal_too_small_or_too_LARGE_to_perturb_usefully() -> None:
    """The band is `1 < |value| < 10000`. Below it, nudging 0 or 1 by one is a structural change
    rather than a perturbation (a count becoming a flag); above it, the literals are seeds, masks and
    canvas sizes where +1 either does nothing visible or breaks generation outright."""
    src = "def used(a):\n    return a * 0 + 1 + 5 + 99999 + 0x9AD1\n"
    found = {text for _ln, _c, _e, text in cache_audit.numeric_sites(src, {1, 2})}
    assert found == {"5"}, f"only the literal inside the band: {found}"


def test_executed_lines_measures_the_ENGINE_TREES_and_answers_EMPTY_when_coverage_fails(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Two things at once. The membership rule is stated at BOTH ends on purpose - `--source` names
    the trees (because `--include` is ignored whenever the config sets `source`, which once left the
    census offering 1,460 candidates from `check_village`, whose literals cannot move an artifact at
    all) and the RESULT is filtered by the same rule, where no config can reach it. And a coverage
    run that produced nothing answers {} rather than raising."""
    monkeypatch.setattr(cache_audit, "HERE", str(tmp_path))
    seen: list[list[str]] = []

    def no_json(cmd: list[str], **_kw: Any) -> Any:
        seen.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(subprocess, "run", no_json)
    assert cache_audit.executed_lines(["a.gen.py"]) == {}, "no coverage json - empty, not an exception"
    src_flag = next(a for a in seen[0] if a.startswith("--source="))
    for tree in cache_audit.ENGINE_TREES:
        assert os.path.join(cache_audit.ENGINE, tree) in src_flag, f"{tree} is measured"
    captured: dict[str, Any] = {}

    def record_env(cmd: list[str], **kw: Any) -> Any:
        captured.update(kw.get("env") or {})
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(subprocess, "run", record_env)
    cache_audit.executed_lines(["a.gen.py"])
    assert captured.get("DIAGRAM_SKIP_RENDER") == "1", "rendering is skipped - the audit compares .json and .svg only"
    assert "cache-audit-cov-" in captured.get("COVERAGE_FILE", ""), "and a repo .coverage is never clobbered"

    def with_json(cmd: list[str], **_kw: Any) -> Any:
        if "-o" in cmd:
            out = cmd[cmd.index("-o") + 1]
            inside = os.path.join(str(tmp_path), cache_audit.ENGINE, "settlement", "geom.py")
            outside = os.path.join(str(tmp_path), cache_audit.ENGINE, "check_village", "x.py")
            pathlib.Path(out).write_text(json.dumps({"files": {inside: {"executed_lines": [3, 4]}, outside: {"executed_lines": [9]}}}))
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(subprocess, "run", with_json)
    got = cache_audit.executed_lines(["a.gen.py"])
    assert got == {os.path.join(cache_audit.ENGINE, "settlement", "geom.py"): {3, 4}}, got
    assert not any("check_village" in k for k in got), "filtered at the RESULT end too, where no config can reach"


def test_gens_takes_the_LIVE_scripted_maps_and_the_subset_unless_all_is_asked(monkeypatch: pytest.MonkeyPatch) -> None:
    """A frozen map is never regenerated, so it has no cache to audit; a compound gen has no
    manifest. The default is the two-map subset (sawada the biggest, inashiro the cheapest)."""
    seen: dict[str, Any] = {}

    def fake_gens(trees: Any, kinds: Any, skill_dir: str) -> list[str]:
        seen.update(trees=trees, kinds=kinds)
        return ["p/sawada/sawada.gen.py", "p/inashiro/inashiro.gen.py", "p/other/other.gen.py"]

    monkeypatch.setattr(cache_audit.poolmaps, "gens", fake_gens)
    subset = cache_audit.gens(False)
    assert [os.path.basename(g) for g in subset] == ["sawada.gen.py", "inashiro.gen.py"]
    assert seen["kinds"] == {"scripted"} and seen["trees"] == (cache_audit.poolmaps.LIVE_TREE,)
    assert len(cache_audit.gens(True)) == 3, "--all takes the whole live scripted pool"
