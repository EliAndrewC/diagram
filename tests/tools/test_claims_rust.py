"""`tools/claims_rust.py` (feature 444 T17, `dev/rust-tooling.md` "research claims"): the Rust phases' doc comments read into the
same claims units the Python reader writes - an item's own `Research:` section, else its file's `//!` module doc's, inherited; a
doc-comment edit leaves a unit's core alone, a change to what runs moves it."""

from __future__ import annotations

import pathlib

from l7r.diagram.tools import claims_rust as cr

SRC = '''//! The field phase.
//!
//! Research:
//!     the comb - CONVENTION: the module's claim, inherited

/// The comb's cut.
///
/// Research:
///     a basin's area - research/questions/0005-rice-paddies-and-their-plots-suiden.html: the plots
#[must_use]
#[expect(clippy::cast_possible_truncation, reason = "a count")]
pub fn cut(n: u64) -> u32 {
    let brace = '{';
    let s = "a } in a string // and a comment marker";
    /* a } in a block comment */
    if n > 0 { n as u32 + u32::from(brace == '{') + s.len() as u32 } else { 0 }
}

pub struct Basin {
    area: u64,
}

impl Basin {
    /// The basin's area.
    pub fn area(&self) -> u64 {
        self.area
    }
}

impl Default for Basin {
    fn default() -> Self {
        Basin { area: 0 }
    }
}

pub const LIMIT: u64 = 100;

/// Research: not a claim
pub fn broken() {}

mod helpers;

pub(crate) const fn twice(x: u64) -> u64 {
    x * 2
}
'''


def _units(src: str = SRC) -> dict[str, object]:
    errors, units = cr.rust_units(src, "rust/phases/src/field.rs")
    return {"errors": errors, **{u.qualname: u for u in units}}


def test_each_item_and_impl_method_is_a_unit_with_its_span_and_kind() -> None:
    got = _units()
    names = [k for k in got if k != "errors"]
    assert names == ["cut", "Basin", "Basin.area", "Basin.default", "LIMIT", "broken", "twice"], "mod helpers; is no unit"
    cut, area = got["cut"], got["Basin.area"]
    assert cut.kind == "function" and area.kind == "method" and got["Basin"].kind == "class" and got["LIMIT"].kind == "constant"  # type: ignore[attr-defined]
    assert SRC.splitlines()[cut.lineno - 1].startswith("pub fn cut") and SRC.splitlines()[cut.end_lineno - 1] == "}"  # type: ignore[attr-defined]
    assert SRC.splitlines()[area.lineno - 1].strip().startswith("pub fn area")  # type: ignore[attr-defined]


def test_an_own_claim_stands_and_the_rest_inherit_the_module_doc() -> None:
    got = _units()
    cut, basin = got["cut"], got["Basin"]
    assert not cut.inherited and cut.claims[0].pointers == ("research/questions/0005-rice-paddies-and-their-plots-suiden.html",)  # type: ignore[attr-defined]
    assert basin.inherited and basin.claims[0].backing == "CONVENTION"  # type: ignore[attr-defined]
    assert got["broken"].errors and not got["broken"].claims, "a section that does not parse is an error, not inherited"  # type: ignore[attr-defined]
    assert got["errors"] == []


def test_a_doc_comment_edit_keeps_the_core_and_a_code_edit_moves_it() -> None:
    before = _units()["cut"].core  # type: ignore[attr-defined]
    assert _units(SRC.replace("/// The comb's cut.", "/// The comb's cut, re-derived."))["cut"].core == before  # type: ignore[attr-defined]
    assert _units(SRC.replace("let brace = '{';", "let brace = '}';"))["cut"].core != before  # type: ignore[attr-defined]


def test_a_file_with_no_module_doc_leaves_an_unclaimed_unit_unclaimed() -> None:
    errors, units = cr.rust_units("fn f() {}\nfn g() -> u8 { 1 }\n// trailing\n", "x.rs")
    assert errors == [] and [(u.qualname, u.claims) for u in units] == [("f", []), ("g", [])]


def test_every_rust_source_under_rust_is_read_and_target_pruned(tmp_path: pathlib.Path) -> None:
    assert cr.all_rust_units(tmp_path) == []
    src = tmp_path / "rust" / "phases" / "src"
    src.mkdir(parents=True)
    (src / "field.rs").write_text(SRC)
    (tmp_path / "rust" / "phases" / "target" / "debug").mkdir(parents=True)
    (tmp_path / "rust" / "phases" / "target" / "debug" / "out.rs").write_text("fn generated() {}\n")
    got = cr.all_rust_units(tmp_path, "pre/")
    assert {u.path for u, _e in got} == {"pre/rust/phases/src/field.rs"} and len(got) == 7


def test_an_unterminated_item_runs_to_the_end_of_the_file() -> None:
    _errors, units = cr.rust_units('fn open() {\n    let s = "x\n', "x.rs")
    assert [u.qualname for u in units] == ["open"]
    _errors, units = cr.rust_units("fn c() { let c = '\\''; /* open comment\n", "x.rs")
    assert [u.qualname for u in units] == ["c"]


def test_the_claims_index_reads_the_rust_units_beside_the_python(tmp_path: pathlib.Path) -> None:
    """`claims.all_units` - the index, its gate, the bundles and the triage downstream - takes the Rust units as it takes Python's."""
    from l7r.diagram.tools import claims  # noqa: PLC0415

    src = tmp_path / "rust" / "phases" / "src"
    src.mkdir(parents=True)
    (src / "field.rs").write_text(SRC)
    got = [u.qualname for u, _e in claims.all_units(tmp_path) if u.path.endswith(".rs")]
    assert got == ["cut", "Basin", "Basin.area", "Basin.default", "LIMIT", "broken", "twice"]


def test_a_doc_comment_cut_off_by_another_line_is_not_the_next_item_s() -> None:
    _errors, units = cr.rust_units("/// Research: orphan - CONVENTION\nuse std::fmt;\nfn f() {}\n", "x.rs")
    assert [(u.qualname, u.claims) for u in units] == [("f", [])]


def test_a_rust_step_on_the_placement_page_shows_its_doc_and_its_claims(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """`dev/rust-tooling.md` "the placement-stages page": a `Steps:` name `<file>.rs::<item>` read through the doc-comment reader."""
    from l7r.diagram.tools import placement_stages as ps  # noqa: PLC0415

    src = tmp_path / "rust" / "phases" / "src"
    src.mkdir(parents=True)
    (src / "field.rs").write_text(SRC)
    monkeypatch.setattr(ps, "REPO", str(tmp_path))
    name, paras = ps.step_doc("rust/phases/src/field.rs::Basin.area")
    assert name == "area" and paras == ["The basin's area."]
    research = ps.research_of(ps.resolve_step("rust/phases/src/field.rs::cut"))
    assert [r["label"] for r in research] == ["a basin's area"] and research[0]["verdict"] == "unchecked"
    try:
        cr.resolve(tmp_path, "rust/phases/src/field.rs::nothing")
    except LookupError:
        pass
    else:
        raise AssertionError("an item the file does not hold")
