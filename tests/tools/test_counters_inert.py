"""`make counters-inert` (feature 443 T02, D5): two rolls compared, the first differing key named - its subprocess stubbed (the
real check is `make counters-inert`, which `make done` runs)."""

import json
import subprocess

import pytest

from l7r.diagram.tools import counters_inert as ci


def test_first_difference_names_the_key_path() -> None:
    assert ci.first_difference({"a": [1, 2]}, {"a": [1, 2]}) is None
    assert ci.first_difference({"a": [1, 2]}, {"a": [1, 3]}) == "a[1]"
    assert ci.first_difference({"a": [1]}, {"a": [1, 2]}) == "a (length 1 against 2)"
    assert ci.first_difference({"a": 1}, {"b": 1}) == "a"
    assert ci.first_difference({"m": {"x": 1}}, {"m": {"x": 2}}) == "m.x"
    assert ci.first_difference({"m": {"x": 1}}, {"m": {"y": 1}}) == "m.x"
    assert ci.first_difference(1, "1") == "(the top)" and ci.first_difference(1, 2) == "(the top)"


def _runner(manifests: dict[bool, object]):  # type: ignore[no-untyped-def]
    seen: list[list[str]] = []

    def run(cmd, cwd=None, env=None, check=False):  # type: ignore[no-untyped-def]
        seen.append(cmd)
        with open(cmd[-1], "w") as fh:
            fh.write(json.dumps(manifests["-O" in cmd], sort_keys=True))
        return subprocess.CompletedProcess(cmd, 0)

    return run, seen


def test_identical_rolls_pass_and_a_counter_that_writes_the_manifest_refuses(capsys: pytest.CaptureFixture[str]) -> None:
    run, seen = _runner({False: {"houses": [1, 2]}, True: {"houses": [1, 2]}})
    assert ci.main(["--seed", "4", "--households", "10"], runner=run) == 0
    assert "identical" in capsys.readouterr().out
    assert ["-O" in c for c in seen] == [False, True] and seen[0][-3:-1] == ["4", "10"]
    bad, _ = _runner({False: {"houses": [1, 2], "meta": {"ops": 9}}, True: {"houses": [1, 2], "meta": {}}})
    assert ci.main([], runner=bad) == 1
    err = capsys.readouterr().err
    assert "REFUSED" in err and "meta.ops" in err and "__debug__" in err


def test_bytes_that_differ_with_equal_values_are_named() -> None:
    def run(cmd, cwd=None, env=None, check=False):  # type: ignore[no-untyped-def]
        with open(cmd[-1], "w") as fh:
            fh.write('{"a": 1}' if "-O" in cmd else '{"a":1}')
        return subprocess.CompletedProcess(cmd, 0)

    assert ci.compare(25, 15, run) == "(the bytes differ, the values do not)"
