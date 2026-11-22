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

/// A tree holding both registries, every kind written from `entry`: the check reads the Mode A kinds too (feature 449 T164).
fn engine(tag: &str, entry: &str) -> l7r_shared::tempdir::TempDir {
    let root = scratch(tag);
    crate::testkit::modals(&root, entry);
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
    // every kind of both registries but the one silence: 61 hamlet and 100 sheet kinds, the hamlet's by their bare key as before (feature 449 T164)
    assert_eq!(
        (bad.len(), bad[0].as_str()),
        (160, format!("alder: Entry names {gone}").as_str())
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
    // the hamlet's block as it was before T164, then the Mode A kinds' own (feature 449 T164)
    assert_eq!(listed, format!("  fallow                 {silence}\n  1 of 61 entries name no section; the other 60 must RESOLVE, checked at the gate and the push.\n  0 of 100 Mode A entries name no section; the other 100 must RESOLVE, checked at the gate and the push.\n"));
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

/// A Mode A kind is checked as a hamlet kind is (feature 449 T164: the Python read the hamlet's `CLASSES` alone): one sheet kind's broken
/// `Entry:` is named `sheet/<slug>`, apart from the hamlet kind of the same key (named by its bare key, as before), and a sheet kind's
/// declared silence passes in a block of its own.
#[test]
fn a_sheet_kind_is_checked_and_named_apart_from_the_hamlet_kind_of_its_key() {
    let root = engine("registry-sheet", &real_page());
    put(&root, &real_page(), "<h2>Q</h2>");
    assert!(broken(&root).unwrap().is_empty());
    let gone = format!("{Q}/{}-gone.html", "0002");
    put(
        &root,
        &crate::about::modal_rel(&crate::kinds::SHEET_REGISTRY, "well"),
        &crate::testkit::modal("well", &gone),
    );
    assert_eq!(
        broken(&root).unwrap(),
        [format!("sheet/well: Entry names {gone}")]
    );
    let said = cli_(&args(&[&root.to_string_lossy()]), &root);
    assert!(said.code == 1 && said.stderr.contains("\n  sheet/well: Entry names "));
    // the hamlet's well broken too: named by its bare key, as before T164, and first
    put(
        &root,
        &crate::about::modal_rel(&crate::kinds::HAMLET_REGISTRY, "well"),
        &crate::testkit::modal("well", &gone),
    );
    assert_eq!(
        broken(&root).unwrap(),
        [
            format!("well: Entry names {gone}"),
            format!("sheet/well: Entry names {gone}")
        ]
    );
    put(
        &root,
        &crate::about::modal_rel(&crate::kinds::HAMLET_REGISTRY, "well"),
        &crate::testkit::modal("well", &real_page()),
    );
    let silence = format!(
        "research/contents.json#compounds ({} - recorded as silent)",
        "no dedicated entry"
    );
    put(
        &root,
        &crate::about::modal_rel(&crate::kinds::SHEET_REGISTRY, "well"),
        &crate::testkit::modal("well", &silence),
    );
    assert_eq!(cli_(&args(&[&root.to_string_lossy()]), &root).code, 0);
    assert!(silent_listing(&root).unwrap().starts_with(&format!(
        "  0 of 61 entries name no section; the other 61 must RESOLVE, checked at the gate and the push.\n  sheet/well                    {silence}\n  1 of 100 Mode A entries "
    )));
    // a sheet kind's file missing fails the run, as a hamlet kind's does
    std::fs::remove_file(root.join(crate::about::modal_rel(
        &crate::kinds::SHEET_REGISTRY,
        "well",
    )))
    .unwrap();
    assert_eq!(cli_(&args(&[&root.to_string_lossy()]), &root).code, 1);
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
