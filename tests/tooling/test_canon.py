"""`scripts/record/canon.py` (feature 250 D16): the canon searched for every term at once.

WHAT THESE PROVE. `make canon` reports every term's hits with the heading each sits under, caps a term's rows,
says so when a term has none, and refuses an empty TERMS. (Its guard, `canon-read-hooks.sh`, was retired by the GM
2026-11-07: "you can remove that hook that blocks you".)
"""

from __future__ import annotations

import importlib.util
import pathlib

from tests._scripts import script

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, script(name))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


canon = _load("_canon")


def test_every_term_is_answered_with_its_heading(tmp_path, capsys) -> None:
    f = tmp_path / "budgets.md"
    f.write_text("# Roads\nThe Imperial road is kept by the treasury.\n## Cities\nMerchants are a quarter.\n" + "road\n" * 20, encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("Imperial road", encoding="utf-8")
    files = canon.canon_files((tmp_path, tmp_path / "missing"))
    assert files == [f], "CLAUDE.md is not canon, and a missing root is skipped"
    assert canon.main(["Imperial road|merchant|ogre"], files=files) == 0
    out = capsys.readouterr().out
    assert "== Imperial road: 1 hit(s)" in out and "[Roads] The Imperial road is kept" in out
    assert "[Cities] Merchants are a quarter." in out and "== ogre: 0 hit(s)" in out
    assert canon.main(["road"], files=files) == 0
    assert "the first 15 shown" in capsys.readouterr().out
    assert canon.main([" | "], files=files) == 2
    assert "every term of the claim" in capsys.readouterr().err
