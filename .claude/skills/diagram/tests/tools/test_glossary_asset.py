"""Features 209 and 301: `make glossary` assembles the glossary; the record's script is derived from it on request."""

from __future__ import annotations

import pathlib

from l7r.diagram.interactive.glossary import GLOSSARY, record_glossary_js
from l7r.diagram.tools import glossary_asset


def test_the_script_is_written_where_it_is_told_and_the_check_reads_only_the_json(tmp_path: pathlib.Path) -> None:
    """Feature 301: the script is built into the site, never committed - so `--check` holds the committed JSON alone,
    and `--path` writes the script on request."""
    target = tmp_path / "glossary.js"
    assert glossary_asset.main(["--check"]) == 0, "the committed JSON is in sync"
    assert glossary_asset.main(["--path", str(target)]) == 0
    assert target.read_text(encoding="utf-8") == record_glossary_js()


def test_the_derivation_carries_every_term_with_its_variants_longest_first() -> None:
    js = record_glossary_js()
    assert js.startswith("// DERIVED FILE") and js.rstrip().endswith("];")
    for term, (_variants, definition) in GLOSSARY.items():
        assert f'"term": "{term}"' in js and definition in js.replace('\\"', '"'), term
    assert '"variants": [\n   "fengshui back grove",' in js, "longest variant first, so the wrap prefers it"
