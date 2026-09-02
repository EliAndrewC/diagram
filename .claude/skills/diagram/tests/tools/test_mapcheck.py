"""The tripwire's expected-failure pin (feature 133 T91, the GM's waiver)."""

import json
import os
import subprocess
import sys
from typing import Any

import pytest

from l7r.diagram.tools import mapcheck as mc


def test_tripwire_verdict_reads_the_pin_like_the_cohort_baseline(monkeypatch):
    monkeypatch.setattr(mc, "TRIPWIRE_EXPECTED", {33: frozenset({"village_windbreak_is_continuous"})})
    assert mc.tripwire_verdict(41, []) == ("ok", False)
    mark, bad = mc.tripwire_verdict(33, ["village_windbreak_is_continuous[belt]"])
    assert not bad and "expected" in mark
    mark, bad = mc.tripwire_verdict(33, ["village_windbreak_is_continuous", "lanes_form_one_network"])
    assert bad and "REGRESSION" in mark and "lanes_form_one_network" in mark
    mark, bad = mc.tripwire_verdict(33, [])
    assert bad and "STALE PIN" in mark, "a pinned seed that comes up clean must make someone drop the pin"
    mark, bad = mc.tripwire_verdict(41, ["a", "b", "c", "d"])
    assert bad and mark == "a, b, c"


# ---- feature 174: the state machine, under the GM's 2026-09-02 all-code rule --------------------
# `mapcheck` picks its OWN scope from how the last run went, and that is the whole reason `make maps`
# has no second command: "the earlier two-command version relied on the session choosing right, and
# it did not". So the state machine is what these tests pin.


pytestmark = pytest.mark.tooling


@pytest.fixture
def _bench(tmp_path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """mapcheck with its state file redirected, its gen list stubbed, and `regen` never really run."""
    state = tmp_path / "state.json"
    monkeypatch.setattr(mc, "STATE", str(state))
    monkeypatch.setattr(mc, "TIERS", {"hamlets": "inashiro"})
    monkeypatch.setattr(mc, "_live_gens", lambda _tier: ["pool/hamlets/inashiro/inashiro.gen.py", "pool/hamlets/sawada/sawada.gen.py"])
    monkeypatch.setattr(mc, "_tripwire", lambda: [])
    runs: list[tuple[list[str], bool]] = []

    def fake_run(gens: list[str], stop_early: bool) -> tuple[bool, list[str]]:
        runs.append((list(gens), stop_early))
        return True, []

    monkeypatch.setattr(mc, "_run", fake_run)
    from l7r.diagram import switches

    monkeypatch.setattr(switches, "read", lambda _root: type("S", (), {"scope_locked": False})())
    return {"state": state, "runs": runs, "monkeypatch": monkeypatch}


def test_after_a_FAILED_run_it_does_the_reference_map_ALONE_and_stops_at_the_first_problem(_bench) -> None:
    """ "after a failed run it does the reference hamlet alone (~1 min) and stops at the first
    problem" - the narrow mode only pays if it really stops before the rest, which is what
    `stop_early` carries."""
    _bench["state"].write_text(json.dumps({"ok": False, "failed": ["sawada"]}))
    assert mc.main([]) == 0
    gens, stop_early = _bench["runs"][0]
    assert len(gens) == 1 and "inashiro" in gens[0], "the reference map alone, and it is first"
    assert stop_early is True


def test_after_a_CLEAN_run_it_does_the_whole_tier_and_reports_every_failure_together(_bench) -> None:
    _bench["state"].write_text(json.dumps({"ok": True, "failed": []}))
    assert mc.main([]) == 0
    gens, stop_early = _bench["runs"][0]
    assert len(gens) == 2 and stop_early is False, "the whole tier, in one batch"


def test_a_clean_reference_map_EARNS_the_tripwire_and_then_the_rest_of_the_tier(_bench) -> None:
    """The sequential cost the GM priced and accepted: a reference run that passes costs ~1 min
    before the wide one starts, and one that FAILS saves the wide run entirely."""
    assert mc.main([]) == 0, "no previous run -> recovering"
    assert [len(g) for g, _ in _bench["runs"]] == [1, 1], "reference first, then the remaining gen"


def test_a_failing_TRIPWIRE_stops_the_run_and_names_the_command_that_shows_the_whole_set(_bench, capsys) -> None:
    """ "the reference map is clean but the tier is not" - and the message hands over the next
    command rather than leaving the reader to find it."""
    _bench["monkeypatch"].setattr(mc, "_tripwire", lambda: ["seed 21"])
    assert mc.main([]) == 1
    out = capsys.readouterr().out
    assert "tripwire FAILED" in out and "cohort_audit --count 48" in out
    assert len(_bench["runs"]) == 1, "the rest of the tier was never paid for"


def test_the_SCOPE_LOCK_overrides_the_state_machine_and_refuses_an_explicit_all(_bench, capsys) -> None:
    """ "says what you mean when you know better" is exactly the override the GM asked to close. A
    locked scope means the reference map alone, never the widening - and `--scope all` is REFUSED
    rather than quietly honoured."""
    from l7r.diagram import switches

    _bench["monkeypatch"].setattr(switches, "read", lambda _root: type("S", (), {"scope_locked": True})())
    _bench["monkeypatch"].setattr(switches, "locked_out", lambda _why: True)
    assert mc.main(["--scope", "all"]) == 1, "refused, not honoured"
    assert _bench["runs"] == [], "and nothing was rolled"

    assert mc.main([]) == 0
    assert "LOCKED to the reference settlement" in capsys.readouterr().out
    assert [len(g) for g, _ in _bench["runs"]] == [1], "the reference map alone, no widening"


def test_the_verdict_is_SAVED_so_the_next_run_can_choose_its_own_scope(_bench) -> None:
    """The state file is the state machine's whole memory; a run that did not write it would make
    the next one guess."""
    assert mc.main([]) == 0
    saved = json.loads(_bench["state"].read_text())
    assert saved["ok"] is True and "utc" in saved


def test_a_state_file_that_cannot_be_read_is_treated_as_NO_previous_run(_bench, capsys) -> None:
    _bench["state"].write_text("{not json at all")
    assert mc.main([]) == 0
    assert "no previous run" in capsys.readouterr().out


def test_run_collects_every_FAIL_line_and_falls_back_to_the_gen_name_on_a_bare_nonzero_exit(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    """A generator that failed without printing a FAIL line still has to be named, or the summary
    reports a clean run over a broken map."""

    def proc(returncode: int, out: str) -> Any:
        return subprocess.CompletedProcess([], returncode, out, "")

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: proc(1, "sawada FAIL something\n"))
    ok, failed = mc._run(["pool/hamlets/sawada/sawada.gen.py"], stop_early=True)
    assert ok is False and failed == ["sawada"]

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: proc(2, "it died silently\n"))
    ok2, failed2 = mc._run(["pool/hamlets/x/x.gen.py"], stop_early=False)
    assert ok2 is False and failed2 == ["x.gen.py"], "named from the gen when nothing said FAIL"

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: proc(0, "REGENERATED x\n"))
    assert mc._run(["pool/hamlets/x/x.gen.py"], stop_early=False) == (True, [])


def test_live_gens_ASKS_classify_rather_than_reading_a_list_and_puts_the_reference_FIRST(monkeypatch: pytest.MonkeyPatch) -> None:
    """Raw membership goes stale silently: Kuwabata was converted on 2026-08-27 and left in the
    frozen list, so `regen.py` regenerated it happily while this sweep - the one behind `make maps` -
    never rolled it at all. So the kind is ASKED, and the reference sorts first so a narrow run is a
    prefix of a wide one."""
    from l7r.diagram.pipeline import poolmaps

    def bundle(stem: str, kind: str, tier: str = "hamlets") -> Any:
        return type("B", (), {"stem": stem, "kind": kind, "tier": tier, "gen": f"{mc.SKILL}/pool/{tier}/{stem}/{stem}.gen.py"})()

    monkeypatch.setattr(mc, "TIERS", {"hamlets": "inashiro"})
    monkeypatch.setattr(
        poolmaps,
        "bundles",
        lambda trees, skill_dir: [bundle("sawada", "scripted"), bundle("frozen_one", "legacy"), bundle("inashiro", "scripted"), bundle("elsewhere", "scripted", tier="towns")],
    )
    gens = mc._live_gens("hamlets")
    assert [os.path.basename(g) for g in gens] == ["inashiro.gen.py", "sawada.gen.py"]
    assert not any("frozen" in g for g in gens), "a legacy map is not here at all"
    assert not any("elsewhere" in g for g in gens), "and neither is another tier's"


def test_the_tripwire_rolls_its_seeds_and_returns_only_the_BAD_ones(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    """It answers the one question a clean reference map leaves open: is the tier clean too. A seed
    whose failure is pinned as expected is printed but NOT returned - that is the waiver working."""
    from l7r.diagram import hamletgen as hg

    monkeypatch.setattr(mc, "TRIPWIRE_SEEDS", (21, 33))
    monkeypatch.setattr(mc, "TRIPWIRE_EXPECTED", {33: frozenset({"village_windbreak_is_continuous"})})
    reports = {21: [], 33: ["village_windbreak_is_continuous[3]"]}
    monkeypatch.setattr(hg, "generate", lambda spec, out_base, render: type("R", (), {"failures": reports[spec.seed]})())
    assert mc._tripwire() == [], "one clean, one pinned - neither is a finding"
    assert "tripwire seed 21: ok" in capsys.readouterr().out

    monkeypatch.setattr(hg, "generate", lambda spec, out_base, render: type("R", (), {"failures": ["something_new[1]"]})())
    assert mc._tripwire() == ["seed21", "seed33"], "an unpinned failure on either seed is"


def test_a_tier_with_no_live_gens_is_skipped_and_a_failure_stops_the_remaining_tiers(_bench) -> None:
    """Two loop controls at once. An empty tier is not an error - the town tier has no scripted gens
    yet - and a tier that fails stops the sweep rather than paying for the next one."""
    _bench["monkeypatch"].setattr(mc, "TIERS", {"empty": "", "hamlets": "inashiro"})
    _bench["monkeypatch"].setattr(mc, "_live_gens", lambda tier: [] if tier == "empty" else ["pool/hamlets/inashiro/inashiro.gen.py"])
    assert mc.main([]) == 0

    _bench["monkeypatch"].setattr(mc, "TIERS", {"a": "x", "b": "y"})
    _bench["monkeypatch"].setattr(mc, "_live_gens", lambda _tier: ["pool/hamlets/x/x.gen.py"])
    _bench["monkeypatch"].setattr(mc, "_run", lambda gens, stop_early: (False, ["x"]))
    _bench["runs"].clear()
    assert mc.main([]) == 1


def test_a_failure_in_the_WIDE_run_after_a_clean_reference_stops_the_sweep(_bench) -> None:
    """The second `break`: the reference and the tripwire both passed, and the rest of the tier did
    not. It must stop rather than roll the next tier on top of a known failure."""
    calls: list[list[str]] = []

    def run(gens: list[str], stop_early: bool) -> tuple[bool, list[str]]:
        calls.append(list(gens))
        return (True, []) if len(calls) == 1 else (False, ["sawada"])

    _bench["monkeypatch"].setattr(mc, "TIERS", {"hamlets": "inashiro", "towns": "t"})
    _bench["monkeypatch"].setattr(mc, "_run", run)
    assert mc.main([]) == 1
    assert len(calls) == 2, "the reference, then the rest - and then it stopped"


def test_the_skill_root_is_put_on_sys_path_when_it_is_not_already_there(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run as a script by `make maps`, where the skill root is not on the path."""
    import importlib
    from pathlib import Path

    monkeypatch.setattr(sys, "path", [p for p in sys.path if Path(p).resolve() != Path(mc.SKILL).resolve()])
    reloaded = importlib.reload(mc)
    assert Path(reloaded.SKILL).resolve() in [Path(p).resolve() for p in sys.path]
