"""The docstring-blind code id on Rust (feature 444 T17, `dev/rust-tooling.md` "the docstring-blind code id"): a comment or doc
comment edit to a `.rs` file is wording - its id unchanged, as a docstring edit is - and any change to what runs moves it."""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "gates"))
import codeid  # noqa: E402

pytestmark = pytest.mark.tooling

BASE = b'''/// The field.
///
/// Research: a claim (research/questions/0005-x.html).
pub fn field<'a>(s: &'a str) -> usize {
    // count the plots
    let q = '"'; let t = '\\''; /* a /* nested */ block */
    let u = "a // not a comment /* nor this */";
    let r = r#"raw "quoted" // kept"#;
    s.len() + u.len() + r.len() + q.len_utf8() + t.len_utf8()
}
'''


def sid(src: bytes) -> bytes:
    return codeid.semantic_bytes(src, "rust/phases/src/field.rs")


@pytest.mark.parametrize(
    "edit",
    [
        BASE.replace(b"/// The field.", b"/// The comb field, re-derived."),
        BASE.replace(b"Research: a claim", b"Research: another claim"),
        BASE.replace(b"// count the plots", b"// count every plot"),
        BASE.replace(b"/* a /* nested */ block */", b"/* other */"),
        BASE.replace(b"    s.len()", b"\n        s.len()"),
    ],
    ids=["doc", "claim", "line comment", "nested block", "whitespace"],
)
def test_wording_leaves_the_id_alone(edit: bytes) -> None:
    assert edit != BASE and sid(edit) == sid(BASE)


@pytest.mark.parametrize(
    "edit",
    [
        BASE.replace(b"s.len() + u.len()", b"s.len() - u.len()"),
        BASE.replace(b"not a comment", b"not a remark"),
        BASE.replace(b'"quoted"', b'"cited"'),
        BASE.replace(b"'\"'", b"'x'"),
        BASE.replace(b"<'a>", b"<'b>").replace(b"&'a", b"&'b"),
    ],
    ids=["operator", "string with //", "raw string", "char", "lifetime"],
)
def test_what_runs_moves_the_id(edit: bytes) -> None:
    assert edit != BASE and sid(edit) != sid(BASE)


def test_a_file_that_is_not_utf8_is_its_bytes_and_other_files_are_unchanged() -> None:
    assert codeid.semantic_bytes(b"\xff\xfe", "x.rs") == b"\xff\xfe"
    assert codeid.semantic_bytes(b"a = 1\n", "Cargo.toml") == b"a = 1\n"
    assert codeid.rust_tokens(b'let s = "unterminated').endswith(b'"unterminated')


def test_the_gate_stamp_reads_a_rust_file_by_its_tokens() -> None:
    """`gate-stamp.py content_id` (the push stamp, the engine key): a `.rs` wording edit keeps its id, as a `.py` one does."""
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("gate_stamp", REPO / "scripts" / "gates" / "gate-stamp.py")
    assert spec and spec.loader
    gs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gs)
    edit = BASE.replace(b"// count the plots", b"// count every plot")
    assert gs.content_id(edit, "rust/phases/src/field.rs") == gs.content_id(BASE, "rust/phases/src/field.rs")
    assert gs.content_id(edit, "rust/phases/Cargo.toml") != gs.content_id(BASE, "rust/phases/Cargo.toml"), "a manifest: its bytes"
