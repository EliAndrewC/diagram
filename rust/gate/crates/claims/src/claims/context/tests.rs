//! A Rust unit's bundle context (feature 449 T165): the first bundle's callees and constants, a distance claim's two calls down, a
//! CANNOT-TELL's chase, and how a name resolves - its own file, its crate, a path's module or type - on a scratch crate.

use std::path::Path;

use super::{named, rust_context, Tables, CHASE_CHARS};
use crate::claims::units::{rust_units, Unit};
use crate::record::testkit::put;

const LIB: &str = "use course::TWO;
pub const GAP: f64 = 12.0;
pub fn reach(x: f64) -> f64 {
    let b = Brook::new();
    b.lay();
    helper(x) + GAP + course::drawn(x) + crate::dup() + SOME!(x) + std::f64::consts::PI + reach(x)
}
fn helper(x: f64) -> f64 {
    x * TWO + GAP
}
pub struct Brook {
    w: f64,
}
impl Brook {
    pub fn new() -> Self {
        Brook { w: WIDTH }
    }
    pub fn lay(&self) {
        Self::new();
        Brook::new();
        Other::new();
    }
}
pub const WIDTH: f64 = 3.0;
";

fn tree(tag: &str) -> l7r_guard::shared::tempdir::TempDir {
    let root = crate::checks::scratch(tag);
    put(&root, "rust/eng/src/lib.rs", LIB);
    put(&root, "rust/eng/src/course.rs", "pub fn drawn(x: f64) -> f64 {\n    deeper(x)\n}\nfn deeper(x: f64) -> f64 {\n    x + DEEP\n}\npub const DEEP: f64 = 4.0;\npub const TWO: f64 = 2.0;\n");
    put(
        &root,
        "rust/eng/src/other.rs",
        "pub fn drawn(x: f64) -> f64 {\n    x\n}\n",
    );
    put(
        &root,
        "rust/eng/src/a.rs",
        "pub fn dup() -> f64 {\n    1.0\n}\n",
    );
    put(
        &root,
        "rust/eng/src/b.rs",
        "pub fn dup() -> f64 {\n    2.0\n}\n",
    );
    put(&root, "rust/eng/target/x.rs", "pub fn helper() {}\n");
    put(&root, "rust/eng/src/tests.rs", "pub fn only_a_test() {}\n");
    put(&root, "rust/eng/src/user.rs", "use crate::{course::drawn, other};\npub fn user(x: f64) -> f64 {\n    let deeper = |v: f64| v;\n    deeper(x) + drawn(x) + helper(x) + only_a_test()\n}\n");
    put(
        &root,
        "rust/eng/src/glob.rs",
        "use super::*;\npub fn g() -> f64 {\n    helper(1.0) + WIDTH\n}\n",
    );
    let long = "x".repeat(CHASE_CHARS);
    put(
        &root,
        "rust/far/src/lib.rs",
        &format!("pub fn far_away() {{}}\npub fn huge() -> &'static str {{\n    \"{long}\"\n}}\n"),
    );
    put(&root, "rust/gate/src/lib.rs", "pub fn far_away() {}\n");
    put(&root, "rust/Cargo.toml", "[workspace]\n");
    root
}

fn unit(root: &Path, qual: &str) -> (Unit, String) {
    let path = "rust/eng/src/lib.rs";
    let u = rust_units(LIB, path)
        .1
        .into_iter()
        .find(|u| u.qualname == qual)
        .unwrap();
    let src = super::items(LIB, 0, "", false)
        .into_iter()
        .find(|i| i.0 == qual)
        .unwrap()
        .5;
    assert!(root.join(path).is_file());
    (u, src)
}

#[test]
fn a_first_bundle_carries_its_file_s_callees_then_every_constant_it_reads() {
    let root = tree("claims-context-first");
    let (u, src) = unit(&root, "reach");
    let got = rust_context(&mut Tables::default(), &root, &u, &src, false, &[]);
    assert_eq!(
        got,
        vec![
            "rust/eng/src/lib.rs::Brook.new",
            "rust/eng/src/lib.rs::helper",
            "rust/eng/src/lib.rs::GAP",
        ]
    );
    // a method: `Self::new` is its own type's, a type the crate lacks is no one's
    let (u, src) = unit(&root, "Brook.lay");
    let got = rust_context(&mut Tables::default(), &root, &u, &src, false, &[]);
    assert_eq!(got, vec!["rust/eng/src/lib.rs::Brook.new"]);
}

#[test]
fn a_distance_claim_carries_what_it_turns_on_two_calls_down() {
    let root = tree("claims-context-direct");
    let (u, src) = unit(&root, "reach");
    let got = rust_context(&mut Tables::default(), &root, &u, &src, true, &[]);
    assert_eq!(
        got,
        vec![
            "rust/eng/src/lib.rs::Brook.new",
            "rust/eng/src/lib.rs::helper",
            "rust/eng/src/lib.rs::GAP",
            "rust/eng/src/course.rs::drawn",
            "rust/eng/src/lib.rs::WIDTH",
            "rust/eng/src/course.rs::TWO",
            "rust/eng/src/course.rs::deeper",
            "rust/eng/src/course.rs::DEEP",
        ]
    );
}

#[test]
fn a_cannot_tell_s_chase_follows_what_its_note_names_within_its_budget() {
    // `drawn` and `dup` are each defined twice in the crate, so every definition is carried, as `defined_in` does; `huge` passes the
    // budget, so the chase stops there, before `drawn`'s own `deeper`
    let root = tree("claims-context-chase");
    let (u, src) = unit(&root, "reach");
    let asked: Vec<String> = ["drawn", "dup", "far_away", "TWO", "TWO", "nothing", "huge"]
        .iter()
        .map(|s| (*s).to_owned())
        .collect();
    let got = rust_context(&mut Tables::default(), &root, &u, &src, false, &asked);
    assert_eq!(
        got[3..],
        [
            "rust/eng/src/course.rs::drawn",
            "rust/eng/src/other.rs::drawn",
            "rust/eng/src/a.rs::dup",
            "rust/eng/src/b.rs::dup",
            "rust/far/src/lib.rs::far_away",
            "rust/eng/src/course.rs::TWO",
        ]
    );
}

#[test]
fn names_are_read_from_the_tokens() {
    // `0..BINS` reads `BINS` (a range is no field access), and `..T::d()` (a struct's rest) calls `T.d`; a one-letter type (`S`,
    // `T`) reads as a constant, as Python's `isupper` reads it, and no constant of the crate is named so
    let got =
        named("fn f() { x.lay(); a::B::c(); GAP; vec![X]; M!(Y); crate::g(); f(); 'a: loop {} for _ in 0..BINS {} S { ..T::d() }; }");
    let names: Vec<(&str, bool, Option<&str>)> = got
        .iter()
        .map(|(n, c, q)| (n.as_str(), *c, q.as_deref()))
        .collect();
    assert_eq!(
        names,
        vec![
            ("B", false, Some("a")),
            ("c", true, Some("B")),
            ("GAP", false, None),
            ("X", false, None),
            ("Y", false, None),
            ("g", true, Some("crate")),
            ("f", true, None),
            ("BINS", false, None),
            ("S", false, None),
            ("T", false, None),
            ("d", true, Some("T")),
        ]
    );
}

#[test]
fn a_bare_name_resolves_only_where_the_file_defines_or_imports_it() {
    let root = tree("claims-context-imports");
    let mut t = Tables::default();
    let user = "pub fn user(x: f64) -> f64 {\n    let deeper = |v: f64| v;\n    deeper(x) + drawn(x) + helper(x) + only_a_test()\n}";
    // `drawn` is imported from `course` (one of two definitions); the closure `deeper`, the unimported `helper` and a test file's
    // function are no item's
    assert_eq!(
        t.refs(&root, "rust/eng/src/user.rs", user, "user"),
        vec!["rust/eng/src/course.rs::drawn"]
    );
    // a glob import brings in what its module defines
    let g = "pub fn g() -> f64 {\n    helper(1.0) + WIDTH\n}";
    assert_eq!(
        t.refs(&root, "rust/eng/src/glob.rs", g, "g"),
        vec!["rust/eng/src/lib.rs::helper", "rust/eng/src/lib.rs::WIDTH"]
    );
}
