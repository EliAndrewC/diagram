"""`scripts/record/claims.py` on the Rust phases: the kept parse keyed on the `.rs` claims, a Rust unit's bundle and constants, and
the unclaimed decisions naming a claimed constant (feature 444 T16).

Split out of `test_claims_index.py` (feature 444 T36, measured 2026-11-07): the incremental gate selects a test MODULE for a Rust
edit when its source names `.rs` (`pool_readers.rust_readers`), and these four were the only Rust cases of a module that costs
48.7 s; there, every Rust edit paid for the claims gate's fixture repositories.
"""

from __future__ import annotations

import pathlib

import pytest

from tests.tooling.test_claims_index import _tree, cx


def test_the_kept_parse_is_keyed_on_the_rust_phases_too(tmp_path: pathlib.Path) -> None:
    """An edited `.rs` claim moves the kept parse's key, as an edited Python one does (found 2026-10-31, feature 444 T16: keyed on
    the Python alone, a Rust claim's fix was read from the stale parse); a file under `target/` does not."""
    skill = _tree(tmp_path)
    (skill / "rust" / "phases" / "src").mkdir(parents=True)
    rs = skill / "rust" / "phases" / "src" / "a.rs"
    rs.write_text("/// Research:\n///     a - GUESS: the record silent\npub const A: u32 = 1;\n")
    cl = cx.engine(skill)
    before = cx.parse_key(skill, cl).hexdigest()
    rs.write_text("/// Research:\n///     a - GUESS: the record silent, 0014 says so\npub const A: u32 = 1;\n")
    assert cx.parse_key(skill, cl).hexdigest() != before, "a Rust claim's edit moves the key"
    moved = cx.parse_key(skill, cl).hexdigest()
    (skill / "rust" / "phases" / "target").mkdir()
    (skill / "rust" / "phases" / "target" / "b.rs").write_text("// built\n")
    assert cx.parse_key(skill, cl).hexdigest() == moved, "a build's target is not a source"


def test_a_rust_unit_is_bundled_with_rust_context() -> None:
    """Feature 444 T16's claims round: a `WITH=` unit in a `.rs` file was parsed as Python, and every Rust bundle carrying one
    refused. A Rust item is read by the Rust reader's item scan, and its fence says rust."""
    root = pathlib.Path(__file__).resolve().parents[2]
    src = cx.context_source(root, "rust/phases/src/water_frame.rs::KnobIn")
    assert src.startswith(("type KnobIn", "pub type KnobIn")) and src.rstrip().endswith(";")
    assert "fn quarter_deg" in cx.context_source(root, "rust/phases/src/water_frame.rs::quarter_deg")
    with pytest.raises(ValueError, match="no `nothing`"):
        cx.context_source(root, "rust/phases/src/water_frame.rs::nothing")


def test_a_rust_unit_carries_the_constants_it_names(tmp_path: pathlib.Path) -> None:
    """Feature 444 T16's fifth claims wave: nine CANNOT-TELLs asked for a constant of the unit's own file the bundle did not show."""
    (tmp_path / "x.rs").write_text("pub const BAND: f64 = 14.0;\nconst UNUSED: u8 = 1;\npub fn f() -> f64 {\n    BAND * 2.0\n}\n", encoding="utf-8")
    src = cx.context_source(tmp_path, "x.rs::f")
    assert cx.rust_constants(tmp_path, "x.rs", src) == ["x.rs::BAND"]
    assert cx.rust_constants(tmp_path, "x.rs", "fn g() {}") == []


def test_an_unclaimed_decision_naming_a_claimed_constant_is_not_opened() -> None:
    """The round arbiter's fix on ask:444-T16-claims-rounds: seven of round five's nine UNCLAIMED named a constant of the unit's
    own file whose own claim stood IN-STEP; each is that constant's, not a finding. One naming a constant still open stays."""
    rows = {
        "x.rs::RING_FT#the ring": {"verdict": "IN-STEP"},
        "x.rs::POND_FT#the pond": {"verdict": "MISLABELED"},
        "x.rs::polder#the ring canal at RING_FT": {"verdict": "UNCLAIMED"},
        "x.rs::polder#the pond's size POND_FT": {"verdict": "UNCLAIMED"},
        "x.rs::polder#a decision naming nothing": {"verdict": "UNCLAIMED"},
        "y.rs::polder#the ring at RING_FT": {"verdict": "UNCLAIMED"},
    }
    keys = [k for _v, k, _n in cx.open_findings(rows, frozenset())]
    assert "x.rs::polder#the ring canal at RING_FT" not in keys
    assert {"x.rs::POND_FT#the pond", "x.rs::polder#the pond's size POND_FT", "x.rs::polder#a decision naming nothing", "y.rs::polder#the ring at RING_FT"} <= set(keys)
