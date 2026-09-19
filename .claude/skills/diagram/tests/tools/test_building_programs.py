"""`make building-programs` renders each declared type's required-items table into `programs.md` (feature 254)."""

from __future__ import annotations

import os

from l7r.diagram.buildings import types as bt
from l7r.diagram.tools import building_programs as bp

SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_render_lists_every_item_with_its_label_band_class_and_why() -> None:
    shrine = bt.by_tier("country-shrines")
    assert shrine is not None
    table = bp.render(shrine)
    assert "| `sanctuary` |" in table and "4-10 by 4-10 ft" in table and "| accurate |" in table
    assert "under `one roof`: 2100-3600 sq ft" in table and "under `one roof`: absent" in table
    assert "optional, a knob" in table and shrine.notes in table
    magi = bt.by_tier("magistracies")
    assert magi is not None and "| `shrine` |" in bp.render(magi) and "40-1150 sq ft" in bp.render(magi) and "| presence |" in bp.render(magi)


def test_apply_rewrites_marked_blocks_and_names_the_tiers_without_one() -> None:
    types = bt.load_types()
    text = "# x\n\nprose\n\n<!-- types.json:magistracies -->\nold\n<!-- /types.json:magistracies -->\n\nmore\n"
    new, missing = bp.apply(text, types)
    assert "old" not in new and bp.render(types[0]) in new and new.startswith("# x\n\nprose\n\n<!-- types.json:magistracies -->\n") and new.endswith("\n<!-- /types.json:magistracies -->\n\nmore\n")
    assert missing == ["country-shrines"]
    both = text + "\n<!-- types.json:country-shrines -->\n\n<!-- /types.json:country-shrines -->\n"
    new, missing = bp.apply(both, types)
    assert missing == [] and all(bp.render(t) in new for t in types)


def test_main_writes_checks_and_reports(tmp_path, capsys) -> None:
    path = tmp_path / "programs.md"
    path.write_text("<!-- types.json:magistracies -->\nx\n<!-- /types.json:magistracies -->\n<!-- types.json:country-shrines -->\ny\n<!-- /types.json:country-shrines -->\n")
    assert bp.main(["--check", "--path", str(path)]) == 1 and "STALE" in capsys.readouterr().err
    assert bp.main(["--path", str(path)]) == 0 and "wrote" in capsys.readouterr().out
    assert bp.main(["--check", "--path", str(path)]) == 0 and "is current" in capsys.readouterr().out
    path.write_text("nothing marked\n")
    assert bp.main(["--path", str(path)]) == 1 and "no `<!-- types.json:<tier> -->` block" in capsys.readouterr().err


def test_the_real_catalog_is_current() -> None:
    with open(bp.PROGRAMS, encoding="utf-8") as fh:
        text = fh.read()
    new, missing = bp.apply(text, bt.load_types())
    assert missing == [] and new == text, "buildings/programs.md is stale - run `make building-programs`"
