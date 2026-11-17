//! The entry-headings check, its self-test and the audit's list of silences (feature 449 T149; the words `check-entry-headings.py`'s).
//! Every pointer a case must not resolve is built from parts, so the research-pointer check reads no fixture here.

use super::{broken, cli, silent_listing, unresolved};

/// The reply alone; whether it is recorded is held by the cases that name it.
fn cli_(args: &[String], root: &std::path::Path) -> l7r_gate_core::Reply {
    cli(args, root).0
}
use l7r_gate_core::checks::scratch;
use l7r_gate_core::record::testkit::put;

const Q: &str = "research/questions";

fn real_page() -> String {
    format!("{Q}/0023-the-dike-pond-hamlet-its-houses-boats-and-manure-jars.html")
}

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

/// A tree holding the whole registry, every kind written from `entry`.
fn engine(tag: &str, entry: &str) -> l7r_guard::shared::tempdir::TempDir {
    let root = scratch(tag);
    crate::testkit::hamlet(&root, entry);
    root
}

#[test]
fn an_entry_resolves_or_names_what_it_misses() {
    let root = scratch("registry-unresolved");
    put(&root, &format!("{Q}/0001-a.html"), "<h2>A</h2>");
    let gone = format!("{Q}/{}-gone.html", "0002");
    assert!(unresolved(&root, &format!("{Q}/0001-a.html")).is_empty());
    assert_eq!(
        unresolved(&root, &format!("{Q}/0001-a.html, {gone}")),
        [gone.clone()]
    );
    assert_eq!(unresolved(&root, "no file named"), ["no file named"]);
    // a tree with no engine has nothing to be right or wrong about
    assert!(broken(&root).unwrap().is_empty());
}

#[test]
fn the_check_names_every_broken_entry_and_passes_a_silence() {
    let gone = format!("{Q}/{}-gone.html", "0002");
    let root = engine("registry-broken", &gone);
    let silence = format!(
        "research/contents.json#fields ({} - recorded as silent)",
        "no dedicated entry"
    );
    put(
        &root,
        &crate::about::modal_rel(&crate::kinds::HAMLET_REGISTRY, "fallow"),
        &crate::testkit::modal("fallow", &silence),
    );
    let bad = broken(&root).unwrap();
    assert_eq!(
        (bad.len(), bad[0].as_str()),
        (60, format!("alder: Entry names {gone}").as_str())
    );
    let said = cli_(&args(&[&root.to_string_lossy()]), &root);
    assert_eq!(said.code, 1);
    assert!(said.stderr.starts_with(
        "a class entry names a research question the record does not hold:\n  alder: Entry names "
    ));
    assert!(said.stderr.ends_with(
        "as `research/contents.json#<section> (no dedicated entry - recorded as silent)`.\n"
    ));
    let listed = silent_listing(&root).unwrap();
    assert_eq!(listed, format!("  fallow                 {silence}\n  1 of 61 entries name no section; the other 60 must RESOLVE, checked at the gate and the push.\n"));
    let good = engine("registry-good", &real_page());
    put(&good, &real_page(), "<h2>Q</h2>");
    assert_eq!(cli_(&args(&[&good.to_string_lossy()]), &good).code, 0);
    // a registry that does not load fails, as the Python's import did
    std::fs::remove_file(good.join(crate::about::modal_rel(
        &crate::kinds::HAMLET_REGISTRY,
        "byre",
    )))
    .unwrap();
    let failed = cli_(&args(&[&good.to_string_lossy()]), &good);
    assert_eq!(
        (failed.code, failed.stderr.as_str()),
        (
            1,
            "ValueError: Byre: the explanation is the docstring, and there is none\n"
        )
    );
    assert!(silent_listing(&good).is_err());
}

#[test]
fn the_self_test_bites() {
    let bare = scratch("registry-selftest-bare");
    let said = cli_(&args(&["--selftest"]), &bare);
    assert_eq!((said.code, said.stdout.as_str()), (0, "check-entry-headings selftest ok (form only - no diagram skill in this tree to resolve against)\n"));
    let root = engine("registry-selftest", &real_page());
    let blind = cli_(&args(&["--selftest"]), &root);
    assert_eq!((blind.code, blind.stderr.as_str()), (1, "AssertionError: the checker cannot see a question that exists - its matching surface is dead\n"));
    put(&root, &real_page(), "<h2>Q</h2>");
    assert_eq!(
        cli_(&args(&["--selftest"]), &root).stdout,
        "check-entry-headings selftest ok\n"
    );
    std::fs::remove_file(root.join(crate::about::modal_rel(
        &crate::kinds::HAMLET_REGISTRY,
        "byre",
    )))
    .unwrap();
    assert_eq!(
        cli(&args(&["--selftest"]), &root),
        (cli_(&args(&["--selftest"]), &root), false)
    );
    assert!(!cli(&args(&[&root.to_string_lossy()]), &root).1);
    let bare_run = cli(&args(&["--selftest"]), &bare);
    assert!(bare_run.1);
}
