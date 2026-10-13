"""`scripts/measure/cohort_known.py` (feature 374, the round arbiter's tooling fix on ask:w155-cohort-seed10): a failing
cohort seed an open found row already lists is named with that row, so the session goes there before probing."""

from __future__ import annotations

import importlib.util
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_cohort_known", REPO / "scripts/measure/cohort_known.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_seeds_a_row_lists_are_read_from_its_words() -> None:
    ck = _load()
    assert ck.seeds_named("re-dealt seats move a refusal into the cohort (seeds 7, 2, 10, 8 under routes B-D)") == {7, 2, 10, 8}
    assert ck.seeds_named("Inashiro and valley seed 18 and 22 when ...") == {18, 22}
    assert ck.seeds_named("no seed named, 40 households") == set()


def test_a_failing_seed_an_open_row_lists_is_named_and_a_closed_row_is_not(tmp_path: pathlib.Path) -> None:
    ck = _load()
    audit = tmp_path / "specs/328-match-the-research/audit"
    audit.mkdir(parents=True)
    rows = [
        {"key": "settle#re-deal", "tier": "E4", "fix": "the web carries a re-deal", "found": "seeds 7, 2, 10, 8 under routes B-D"},
        {"key": "closed#row", "tier": "E1", "fix": "x", "found": "seed 10 once"},
    ]
    (audit / "found-wave149.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    (audit / "waves.json").write_text(json.dumps({"closed#row": "150"}))
    logs = tmp_path / "dev/cohort-log"
    logs.mkdir(parents=True)
    record = {"seeds": [{"seed": 10, "verdict": "fail"}, {"seed": 3, "verdict": "fail"}, {"seed": 7, "verdict": "pass"}]}
    (logs / "20261013T125506Z-x.json").write_text(json.dumps(record))
    (logs / "features.json").write_text("{}")  # the feature index beside the records sorts after them
    said = ck.known(tmp_path, ck.newest(tmp_path))
    assert said == ["cohort: seed 10 is named by an open found row - settle#re-deal (E4); go to that row before probing"]
    assert ck.main(["--root", str(tmp_path)]) == 0
    assert ck.newest(tmp_path / "nowhere") is None
