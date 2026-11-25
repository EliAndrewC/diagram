//! The research backlog (feature 451 T236): every UNRESEARCHED claim and page item, by the code file it belongs to.

use std::path::Path;

use l7r_gate_core::record::testkit::put;

use super::{backlog_cli, Scope};
use crate::claims::tests::fixture_with;

const SEAT: &str = "//! The seat.
//!
//! Research:
//!     plumbing - NONE

/// Research: the fence's height - UNRESEARCHED: 4 ft
pub fn fence() -> f64 {
    4.0
}

/// Research: the tree - UNRESEARCHED research/questions/0003-tree.drawing.html#tree: one tree
pub fn tree() {}
";

const TREE: &str = r#"<h2 id="tree">The tree</h2>
<ul><li>A tree beside the shrine, UNRESEARCHED.<span class="item" data-item="tree" data-label="UNRESEARCHED" data-guess="The tree: not yet searched"></span></li>
<li>A gate, UNRESEARCHED.<span class="item" data-item="gate" data-label="UNRESEARCHED"></span></li>
<li>A wall, a GUESS.<span class="item" data-item="wall" data-label="GUESS"></span></li></ul>
"#;

fn tree(root: &Path) {
    put(
        root,
        "dev/work-budget.json",
        r#"{"stages": {"seat": {}, "field.polder": {}, "labels": {}}}"#,
    );
    // a stage's name is matched only in the stages' crate: Mode A's `labels/` is no stage's
    put(
        root,
        "rust/mode_a/src/labels/place.rs",
        "/// Research: a label's offset - UNRESEARCHED: 4 ft\npub fn place() {}\n",
    );
    put(root, "rust/phases/src/seat.rs", SEAT);
    // a stage's own module: `seat/` beside `seat.rs`; the driver, holding every `stage_<name>`, shared by every stage
    put(
        root,
        "rust/phases/src/seat/fords.rs",
        "/// Research: the ford's length - UNRESEARCHED: 60 ft\npub fn gapped() {}\n",
    );
    put(
        root,
        "rust/phases/src/driver.rs",
        "/// Research: the grave - UNRESEARCHED: 13 ft\npub fn stage_seat() {}\n",
    );
    put(root, "research/questions/0003-tree.drawing.html", TREE);
}

fn run(root: &Path, more: &[&str]) -> crate::Reply {
    let mut args = vec!["--root".to_owned(), root.to_string_lossy().into_owned()];
    args.extend(more.iter().map(|a| (*a).to_owned()));
    backlog_cli(&args)
}

#[test]
fn every_unresearched_claim_and_item_is_listed_by_its_code_file() {
    let root = fixture_with("claims-backlog", &tree);
    let got = run(&root, &[]);
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert_eq!(
        got.stdout,
        "research-backlog: 5 UNRESEARCHED claim(s), 2 UNRESEARCHED page item(s) - not yet searched, a guess drawn meanwhile: \
work a stage's own at its end (feature 451 T236; make research-backlog STAGE=<stage or path glob>)
research/questions/0003-tree.drawing.html (no claim names the item)
  item   research/questions/0003-tree.drawing.html#gate - A gate, UNRESEARCHED.
rust/mode_a/src/labels/place.rs
  claim  rust/mode_a/src/labels/place.rs::place#a label's offset - 4 ft
rust/phases/src/driver.rs
  claim  rust/phases/src/driver.rs::stage_seat#the grave - 13 ft
rust/phases/src/seat.rs
  claim  rust/phases/src/seat.rs::fence#the fence's height - 4 ft
  claim  rust/phases/src/seat.rs::tree#the tree - one tree
  item   research/questions/0003-tree.drawing.html#tree - The tree: not yet searched
rust/phases/src/seat/fords.rs
  claim  rust/phases/src/seat/fords.rs::gapped#the ford's length - 60 ft
"
    );
    // the claims are claims-report's own UNRESEARCHED list
    let report = crate::claims::tests::claims(&root, &["report"]);
    assert!(
        report
            .stdout
            .contains("UNRESEARCHED claims (the open research): 5"),
        "{}",
        report.stdout
    );
}

#[test]
fn a_stage_or_a_path_glob_narrows_it_and_anything_else_is_refused() {
    let root = fixture_with("claims-backlog-stage", &tree);
    let stage = run(&root, &["--stage", "seat"]);
    assert!(
        stage.stdout.starts_with(
            "research-backlog: 4 UNRESEARCHED claim(s), 1 UNRESEARCHED page item(s) in stage seat"
        ),
        "{}",
        stage.stdout
    );
    // the stage's own module, and the driver every stage shares, marked so
    assert!(!stage.stdout.contains("#gate"), "{}", stage.stdout);
    let shared = "rust/phases/src/driver.rs (shared: no stage's own module - its stage's entries among them)\n  claim  rust/phases/src/driver.rs::stage_seat#the grave";
    assert!(stage.stdout.contains(shared), "{}", stage.stdout);
    // Mode A's `labels/` is not the stage `labels`
    let labels = run(&root, &["--stage", "labels"]);
    assert!(!labels.stdout.contains("mode_a"), "{}", labels.stdout);
    assert!(
        stage.stdout.contains("seat/fords.rs::gapped"),
        "{}",
        stage.stdout
    );
    // a form's stage is its stage's code; a stage with no module of its own lists the shared driver alone
    let form = run(&root, &["--stage", "field.polder"]);
    assert!(form.stdout.starts_with("research-backlog: 1 UNRESEARCHED claim(s), 0 UNRESEARCHED page item(s) in stage field.polder"), "{}", form.stdout);
    let glob = run(&root, &["--stage", "research/questions/*.html"]);
    assert!(glob.stdout.starts_with("research-backlog: 0 UNRESEARCHED claim(s), 2 UNRESEARCHED page item(s) in research/questions/*.html"), "{}", glob.stdout);
    let prefix = run(&root, &["--stage", "rust/phases/**"]);
    assert!(
        prefix
            .stdout
            .contains(", 1 UNRESEARCHED page item(s) in rust/phases/**"),
        "{}",
        prefix.stdout
    );
    let none = run(&root, &["--stage", "nowhere"]);
    assert_eq!(none.code, 2);
    assert!(none.stderr.contains("STAGE=nowhere names no stage of dev/work-budget.json's and is no path glob: give a stage (`STAGE=seat`) or a path glob (`STAGE='rust/phases/src/seat*'`)"), "{}", none.stderr);
    assert_eq!(run(&root, &["--bogus"]).code, 2);
    // with no work budget, no name is a stage
    std::fs::remove_file(root.join("dev/work-budget.json")).unwrap();
    assert_eq!(run(&root, &["--stage", "seat"]).code, 2);
    assert!(Scope::Glob("rust/*/src/seat.rs".to_owned()).holds("rust/phases/src/seat.rs"));
    assert!(!Scope::Glob("rust/*.rs".to_owned()).holds("rust/phases/src/seat.rs"));
    assert!(Scope::Glob("rust/phases/src/sea?.rs".to_owned()).holds("rust/phases/src/seat.rs"));
}

#[test]
fn an_unreadable_source_is_reported() {
    let root = fixture_with("claims-backlog-broken", &tree);
    std::fs::write(root.join("rust/phases/src/bad.rs"), [0xffu8, 0xfe]).unwrap();
    let got = run(&root, &[]);
    assert_eq!(got.code, 1);
    assert!(
        got.stderr
            .starts_with("research-backlog: the claims could not be read"),
        "{}",
        got.stderr
    );
}
