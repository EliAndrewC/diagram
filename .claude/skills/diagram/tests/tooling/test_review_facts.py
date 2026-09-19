"""`scripts/_review_facts.py` (feature 255, FR-005): a settlement review's opening measurements in one call.

WHAT THESE PROVE. A map is found by its folder or by its stem; a missing artifact is SAID to be missing; the
inventory counts every manifest key; the delta names a new key, a gone key and a key whose content moved, against a
snapshot's main side when one is given and against a git ref otherwise (a fake `git` stands in - no repository is
made); labels are counted with their markup gone; the notes' headings and the "Settled by the GM" section come back
verbatim, and a notes file without one says so. Nothing here is a verdict, and the tests assert none is printed.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import types

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_review_facts", REPO / "scripts" / "_review_facts.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rf = _load()

BEFORE = {"meta": {"ftpx": 1.0, "view": [0, 0, 9, 9]}, "houses": [1, 2], "wells": [1], "sties": [1]}
AFTER = {"meta": {"ftpx": 1.0, "view": [0, 0, 9, 9], "seed": 7}, "houses": [1, 2], "wells": [2], "duck_pens": [1, 2, 3]}
SVG = '<svg><text x="1">Kuwabata</text><text><tspan>fish</tspan> pond</text><text>fish pond</text><text> </text></svg>'
NOTES = "# Kuwabata\n\ntext\n\n## Settled by the GM\n\n- the sties stay on the dike\n- no label on the gate\n\n## Review log\n\nlater\n"


def _map(tmp_path: pathlib.Path) -> pathlib.Path:
    folder = tmp_path / "pool" / "hamlets" / "kuwabata"
    folder.mkdir(parents=True)
    (folder / "kuwabata.json").write_text(json.dumps(AFTER), encoding="utf-8")
    (folder / "kuwabata.svg").write_text(SVG, encoding="utf-8")
    (folder / "kuwabata.notes.md").write_text(NOTES, encoding="utf-8")
    return folder


def _git(shown: str | None, top: str):  # noqa: ANN202
    def run(cmd, **_kw):  # noqa: ANN001, ANN202
        if "rev-parse" in cmd:
            return types.SimpleNamespace(returncode=0 if top else 1, stdout=top)
        return types.SimpleNamespace(returncode=0 if shown is not None else 1, stdout=shown or "")

    return run


def test_locate_takes_a_folder_or_a_stem(tmp_path: pathlib.Path) -> None:
    folder = _map(tmp_path)
    assert rf.locate(str(folder)) == (folder, "kuwabata")
    assert rf.locate(str(folder / "kuwabata")) == (folder, "kuwabata")


def test_the_pieces() -> None:
    assert rf.count([1, 2]) == "2" and rf.count({"a": 1}) == "1" and rf.count(7) == "7"
    inv = rf.inventory(AFTER)
    assert inv[0] == "  meta: ftpx=1.0, seed=7" and any(line.split() == ["duck_pens", "3"] for line in inv)
    moved = "\n".join(rf.delta(BEFORE, AFTER))
    assert "duck_pens" in moved and "NEW" in moved and "sties" in moved and "GONE" in moved
    assert "wells" in moved and "content moved" in moved and "houses" not in moved
    assert rf.delta(AFTER, AFTER) == ["  nothing moved: the two manifests are equal"]
    assert rf.labels(SVG) == ["    2 x fish pond", "    1 x Kuwabata"] and rf.labels("<svg/>") == ["  none"]
    got = rf.notes(NOTES)
    assert "  ## Review log" in got and "  - the sties stay on the dike" in got and "  later" not in got
    assert rf.notes("# only a title\n")[-1] == "  -- no 'Settled by the GM' section"


def test_report_against_a_ref_a_snapshot_and_nothing(tmp_path: pathlib.Path) -> None:
    folder = _map(tmp_path)
    text = rf.report(str(folder), "HEAD", "", 0.0, run=_git(json.dumps(BEFORE), str(tmp_path)))
    assert "DELTA against HEAD" in text and "content moved" in text and "picture    kuwabata.png" in text and "MISSING" in text
    assert "verdict" in text.splitlines()[0] and "PASS" not in text and "FAIL" not in text
    assert "no manifest at main" in rf.report(str(folder), "main", "", 0.0, run=_git(None, str(tmp_path)))
    assert "not a repository" in rf.report(str(folder), "main", "", 0.0, run=_git(None, ""))
    snap = tmp_path / "snap"
    (snap / "main").mkdir(parents=True)
    (snap / "main" / "kuwabata.json").write_text(json.dumps(BEFORE), encoding="utf-8")
    assert "DELTA against the snapshot's main side" in rf.report(str(folder), "HEAD", str(snap), 0.0)
    (folder / "kuwabata.json").unlink()
    (folder / "kuwabata.notes.md").unlink()
    assert "no manifest, so no inventory" in rf.report(str(folder), "HEAD", "", 0.0)


def test_a_map_with_no_render_and_no_notes(tmp_path: pathlib.Path) -> None:
    folder = _map(tmp_path)
    (folder / "kuwabata.svg").unlink()
    (folder / "kuwabata.notes.md").unlink()
    text = rf.report(str(folder), "HEAD", "", 0.0, run=_git(None, ""))
    assert "render MISSING" in text and "itself a finding" in text


def test_main(tmp_path: pathlib.Path, capsys) -> None:  # noqa: ANN001
    folder = _map(tmp_path)
    assert rf.main([str(folder)]) == 0
    assert "review-facts: kuwabata" in capsys.readouterr().out
    assert rf.main([str(tmp_path / "pool" / "absent" / "x")]) == 2
    assert "no such map folder" in capsys.readouterr().err
