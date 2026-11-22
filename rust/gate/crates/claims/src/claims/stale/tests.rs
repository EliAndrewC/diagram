//! The stale-figure check on Rust (feature 449 T165): the figures of a value as Python writes them, a changed constant's pages named,
//! and the check end to end on a scratch repository - a `.rs` constant changed names its page, a `.py` change asks nothing (feature 449 T158).
//! The question paths are built from their parts, so no fixture holds a research pointer of its own.

use super::{figures, rust_stale, Page};
use crate::claims::tests::{claims, fixture};
use crate::record::testkit::{commit, git, put};

const Q: &str = "research/questions/";

fn page(name: &str, text: &str) -> Page {
    (format!("{Q}{name}"), name.to_owned(), text.to_owned())
}

/// The line the check prints for page `name` stating 23, `INSET` having been 23.0 in `path`.
fn line(name: &str, path: &str) -> String {
    format!("stale figure: {Q}{name} states 23 (INSET was 23.0 in {path}) - reword it, or check it still holds")
}

fn source(value: &str, pointer: &str) -> String {
    format!("/// The inset.\n///\n/// Research:\n///     the inset - {pointer}: kept in\npub const INSET: f64 = {value};\n\n/// Research: nothing - NONE\npub const PLAIN: u32 = 7;\n")
}

#[test]
fn a_value_s_figures_are_python_s() {
    assert_eq!(figures("43_560.0"), vec!["43560"]);
    assert_eq!(
        figures("[0.35f64, 2.5, 1.0, 0, 1, 8u32]"),
        vec!["0.35", "2.5", "8"]
    );
    assert_eq!(figures("-3.0 * 1.5e-3 + 2E+2"), vec!["0.0015", "200", "3"]);
    assert_eq!(
        figures("0x10 + 0b11 + 0o7 + 0x1f32"),
        vec!["16", "3", "7", "7986"]
    );
    assert_eq!(figures("(X.0, 0..5, \"77\") // 99"), vec!["5"]);
    assert_eq!(
        figures("1e40 + 1e400 + 0.0 + 0x + 007"),
        vec!["10000000000000000303786028427003666890752", "7", "inf"]
    );
    assert_eq!(
        figures("999999999999999999999999999999999999999999 + 01"),
        vec!["999999999999999999999999999999999999999999"]
    );
}

#[test]
fn a_changed_constant_names_the_pages_still_stating_its_old_figure() {
    let ptr = format!("{Q}0022-inset.drawing.html");
    let pages = [
        page(
            "0022-inset.drawing.html",
            "<p>The pond stands 23 ft in.</p>",
        ),
        page("0023-other.drawing.html", "<p>See 0022-inset: 23 ft.</p>"),
        page("0024-far.drawing.html", "<p>23 ft, unlinked.</p>"),
        page(
            "0025-near.drawing.html",
            "<p>0022-inset, but 123 or 23.5 or 2.23.</p>",
        ),
    ];
    let got = rust_stale(
        "rust/phases/src/x.rs",
        &source("23.0", &ptr),
        &source("24.0", &ptr),
        &pages,
    );
    assert_eq!(
        got,
        vec![
            line("0022-inset.drawing.html", "rust/phases/src/x.rs"),
            line("0023-other.drawing.html", "rust/phases/src/x.rs"),
        ]
    );
    // formatting alone is no change; a doc's change alone is; a constant gone, or one whose docs hold no claim, names nothing
    let spaced = source("23.0", &ptr).replace("= 23.0;", "=\n    23.0 /* the same */;");
    assert!(rust_stale("x.rs", &source("23.0", &ptr), &spaced, &pages).is_empty());
    let reworded = source("23.0", &ptr).replace("kept in", "kept further in");
    assert_eq!(
        rust_stale("x.rs", &source("23.0", &ptr), &reworded, &pages).len(),
        2
    );
    assert!(rust_stale("x.rs", &source("23.0", &ptr), "pub fn f() {}\n", &pages).is_empty());
    let bare = "pub const INSET: f64 = 23.0;\npub const INSET: f64 = 22.0;\n";
    assert!(rust_stale("x.rs", bare, "pub const INSET: f64 = 24.0;\n", &pages).is_empty());
    assert!(
        super::value_of("pub const A: bool = 1 >= 2 && 3 <= 4 && 5 != 6 || 7 == 8 => 9;")
            .is_some_and(|v| v.starts_with("1 >= 2"))
    );
    assert!(super::value_of("pub struct S;").is_none());
}

#[test]
fn the_check_runs_on_a_rust_change_and_reads_no_python() {
    let root = fixture("claims-stale-rs");
    let ptr = format!("{Q}0003-inset.drawing.html");
    put(&root, &ptr, "<p>The inset is 23 ft.</p>\n");
    put(&root, "rust/engine/src/lib.rs", &source("23.0", &ptr));
    put(&root, "rust/gate/src/inset.rs", &source("23.0", &ptr));
    commit(&root, "the inset");
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    // a crate new under `rust/` is walked; the gate's own crate is not; a file new since the base has no old figure; a page that is
    // not UTF-8 is read as the Python reads it, `errors="replace"`; a `.py` change is read no more
    put(&root, "rust/engine/src/lib.rs", &source("24.0", &ptr));
    put(&root, "rust/gate/src/inset.rs", &source("24.0", &ptr));
    put(&root, "rust/engine/src/new.rs", &source("25.0", &ptr));
    let mut bytes = vec![0xffu8];
    bytes.extend(b" after 0003-inset: 23 ft");
    std::fs::write(root.join(format!("{Q}0004-link.drawing.html")), bytes).unwrap();
    put(&root, "l7r/diagram/m.py", "GAP = 13\n");
    let got = claims(&root, &["owed"]);
    assert_eq!(got.code, 0, "{}", got.stderr);
    let lines: Vec<&str> = got
        .stdout
        .lines()
        .filter(|l| l.starts_with("stale figure"))
        .collect();
    assert_eq!(
        lines,
        vec![
            line("0003-inset.drawing.html", "rust/engine/src/lib.rs"),
            line("0004-link.drawing.html", "rust/engine/src/lib.rs"),
        ]
    );
}

#[test]
fn a_page_that_cannot_be_read_fails_the_check_saying_which() {
    let root = crate::checks::scratch("claims-stale-pages");
    assert_eq!(super::drawing_pages(&root), Ok(Vec::new()));
    std::fs::create_dir_all(root.join(format!("{Q}0009-dir.drawing.html"))).unwrap();
    let got = super::drawing_pages(&root).unwrap_err();
    assert!(got.starts_with("0009-dir.drawing.html: "), "{got}");
}
