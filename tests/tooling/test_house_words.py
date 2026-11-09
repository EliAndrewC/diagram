"""The house-style word table is one table (feature 449 T036 decision (c)): `hm_house.py` until its last Python caller goes."""

from __future__ import annotations

import importlib.util
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]


def test_the_rust_guards_word_table_is_the_decisions() -> None:
    """The guard's table is data generated from `hm_house.py`; the two stay one table. `l7r-gate check house-style-delta` compiles the same file in."""
    spec = importlib.util.spec_from_file_location("hm_house", REPO / "scripts/hooks/lib/hm_house.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rows = (REPO / "rust/guard/src/guards/house_style_words.tsv").read_text(encoding="utf-8").splitlines()
    assert [tuple(r.split("\t")) for r in rows] == list(mod.PAIRS.items())
