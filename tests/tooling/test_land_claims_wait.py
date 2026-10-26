"""The landing's claims wait ends when nothing can arrive (feature 426, D1): an introduced finding stops it at once with its cure,
an owed claim waits only while a claims check is in flight, and a stale mark is no check in flight."""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

from tests._scripts import script


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, script(name))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


land = _load("land")
flight = _load("claims_flight")

INTRODUCED = "\nCLAIMS GATE: research claims owed a check\n  introduced: DRIFTED        l7r/x.py::f#a claim - known (417 T32): it\n"
OWED = "\nCLAIMS GATE\n  claims-gate: owed (code changed): l7r/x.py::g#b\n"


def test_an_introduced_finding_stops_the_wait_at_once_naming_its_cure_and_what_else_is_owed() -> None:
    got = land.claims_cure(INTRODUCED + OWED, in_flight=["/tmp/l7r-check/claims-owed"])
    assert "no check in flight can cure" in got and "l7r/x.py::f#a claim" in got, "even with a check in flight"
    assert "make arbiter-ask" in got and "also owed:" in got and "make land again" in got


def test_an_owed_claim_waits_only_while_a_check_is_in_flight() -> None:
    assert land.claims_cure(OWED, in_flight=["/tmp/b"]) == "", "a check in flight may answer it: wait"
    got = land.claims_cure(OWED, in_flight=[])
    assert "none is in flight" in got and "make claims-bundle OWED=1" in got and "make claims-checked" in got


def test_a_mark_is_live_until_cleared_and_stale_past_the_landing_s_wait(tmp_path: pathlib.Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    bundle = tmp_path / "bundle"
    assert flight.live(tmp_path) == []
    flight.mark(tmp_path, bundle)
    assert flight.live(tmp_path) == [str(bundle.resolve())]
    assert flight.live(tmp_path, now=10**12) == [], "past MAX_AGE_S a mark is stale"
    flight.clear(tmp_path, bundle)
    assert flight.live(tmp_path) == []
    assert flight.MAX_AGE_S == land.CLAIMS_WAIT_S, "a mark is stale exactly when the landing would have stopped waiting"
