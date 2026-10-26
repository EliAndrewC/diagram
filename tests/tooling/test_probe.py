"""`make probe` (feature 426, D5): every seed beside HEAD's verdict, each moved manifest field, HEAD's block rolled once."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

from tests._scripts import script


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, script(name))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


probe = _load("probe")


def test_every_seed_is_printed_beside_head_s_and_a_new_failing_check_is_worse() -> None:
    head = {1: [], 2: ["lane_knots[2]"], 3: ["a[1]"], 4: [], 5: ["b[1]"]}
    now = {1: [], 2: ["lane_knots[2]"], 3: [], 4: ["c[1]"], 5: ["b[3]"], 6: []}
    lines, worse = probe.compare(head, now)
    got = {int(ln.split()[0]): ln for ln in lines}
    assert "same pass" in got[1] and "same failure" in got[2] and "FIXED" in got[3] and "NEW FAILURE" in got[4]
    assert "changed failure" in got[5] and "new seed" in got[6], "the seed being worked on shows whether it moved"
    assert worse == 1
    assert probe.mark([], None) == "not rolled" and probe.mark(["a[1]"], ["a[1]", "z[1]"]) == "NEW FAILURE"


def test_a_manifest_s_moved_fields_are_listed_by_path_points_as_drawn() -> None:
    old = {"lanes": [{"pts": [[1.04, 2.0]], "w": 3}], "meta": {"x": 1}, "houses": [1, 2]}
    new = {"lanes": [{"pts": [[1.0, 2.0]], "w": 5}], "meta": {"x": 1, "y": 2}, "houses": [1, 2, 3]}
    assert probe.manifest_diff(old, new) == ["houses", "lanes[0].w", "meta.y"], "a 0.04 shift is not drawn"
    assert probe.manifest_diff(1, 2) == ["(the manifest)"]


def test_a_cohort_s_record_is_read_from_the_clone_and_its_verdicts_kept(tmp_path: pathlib.Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    rec = tmp_path / "dev" / "cohort-log" / "r.json"
    rec.parent.mkdir(parents=True)
    rec.write_text(json.dumps({"seeds": [{"seed": 3, "failures": ["b[1]", "a[2]"]}]}), encoding="utf-8")
    got = probe.record_of("...\nrecord committed (fail): dev/cohort-log/r.json\n", tmp_path)
    assert probe.verdicts(got) == {3: ["a[2]", "b[1]"]}
    with pytest.raises(SystemExit, match="wrote no record"):
        probe.record_of("nothing", tmp_path)


class _Make:
    """`run` standing in for git and make: cohorts write a record whose failing seeds are `failing`; counts HEAD's rolls."""

    def __init__(self, root: pathlib.Path, failing: dict[str, list[int]]) -> None:
        self.root, self.failing, self.rolls, self.n = root, failing, [], 0

    def __call__(self, cmd: list[str], cwd: pathlib.Path) -> tuple[int, str]:
        if cmd[0] == "git":
            return subprocess.run(cmd, capture_output=True, text=True, check=False).returncode, subprocess.run(cmd, capture_output=True, text=True, check=False).stdout
        if "cohort" in cmd:
            who = "head" if cwd.name == "head" else "now"
            self.rolls.append(who)
            seed = next((int(a[5:]) for a in cmd if a.startswith("SEED=")), 1)
            self.n += 1
            rec = self.root / "dev" / "cohort-log" / f"{self.n}.json"
            rec.parent.mkdir(parents=True, exist_ok=True)
            bad = self.failing.get(who, [])
            rec.write_text(json.dumps({"seeds": [{"seed": s, "failures": ["c[1]"] if s in bad else []} for s in (seed, seed + 1)]}), encoding="utf-8")
            return 0, f"record committed (pass): dev/cohort-log/{self.n}.json"
        return 0, ""


def _repo(tmp_path: pathlib.Path) -> pathlib.Path:
    root = tmp_path / "clone"
    root.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    for k, v in (("user.email", "t@t"), ("user.name", "t")):
        subprocess.run(["git", "-C", str(root), "config", k, v], check=True)
    gen = root / "pool" / "hamlets" / "a" / "a.gen.py"
    gen.parent.mkdir(parents=True)
    gen.write_text("x = 1\n", encoding="utf-8")
    (gen.parent / "a.json").write_text(json.dumps({"lanes": [1]}), encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "m"], check=True)
    return root


def test_head_is_rolled_once_per_engine_key_and_the_probe_is_red_on_a_worse_seed(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    root = _repo(tmp_path)
    fake = _Make(root, {"now": [2]})
    monkeypatch.setattr(probe, "run", fake)
    cg = type("CG", (), {"fresh_seed": staticmethod(lambda r, ref: 700), "cohort_known": type("K", (), {"engine_key": staticmethod(lambda r, ref: "k1")})})
    monkeypatch.setattr(probe, "_cohort_gate", lambda: cg)
    assert probe.main(["--root", str(root)]) == 1, "seed 2 fails now and passed at HEAD"
    out = capsys.readouterr().out
    assert "NEW FAILURE" in out and "the pool against HEAD:" in out and "a: unchanged" in out
    assert fake.rolls.count("head") == 2, "HEAD's landing cohort and fresh block, rolled once"
    fake.rolls.clear()
    fake.failing = {}
    assert probe.main(["--root", str(root), "--exitfirst"]) == 0
    assert "head" not in fake.rolls, "the second probe at one HEAD reads the stored verdicts"
