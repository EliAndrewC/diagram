"""Feature 209: `make glossary` writes research/assets/glossary.js from interactive/glossary.py; `--check` tells a stale one."""

from __future__ import annotations

import pathlib

from l7r.diagram.interactive.glossary import GLOSSARY, record_glossary_js
from l7r.diagram.tools import glossary_asset


def test_write_then_check_is_in_sync_and_an_edit_or_an_absence_is_stale(tmp_path: pathlib.Path, capsys: object) -> None:
    target = tmp_path / "glossary.js"
    assert glossary_asset.main(["--check", "--path", str(target)]) == 1, "no file yet: stale"
    assert glossary_asset.main(["--path", str(target)]) == 0
    assert target.read_text(encoding="utf-8") == record_glossary_js()
    assert glossary_asset.main(["--check", "--path", str(target)]) == 0
    target.write_text(target.read_text(encoding="utf-8") + "\n// a hand edit", encoding="utf-8")
    assert glossary_asset.main(["--check", "--path", str(target)]) == 1


def test_the_derivation_carries_every_term_with_its_variants_longest_first() -> None:
    js = record_glossary_js()
    assert js.startswith("// DERIVED FILE") and js.rstrip().endswith("];")
    for term, (_variants, definition) in GLOSSARY.items():
        assert f'"term": "{term}"' in js and definition in js.replace('\\"', '"'), term
    assert '"variants": [\n   "fengshui back grove",' in js, "longest variant first, so the wrap prefers it"
