//! Each form over a record of its own, and the walk of a tree.

use super::super::tests::{commit, put, repo};
use super::{cli, exempt};

fn record(dir: &std::path::Path) {
    put(dir, "research/questions/0412-a.html", "x");
    put(
        dir,
        "research/contents.json",
        r#"{"sections": [{"id": "water"}]}"#,
    );
    put(
        dir,
        "research/moved-303.json",
        r#"{"pages": {"water": "water"}, "numbers": {"water 120": "0412"}}"#,
    );
}

fn run(dir: &std::path::Path) -> super::Outcome {
    cli(&[dir.display().to_string()])
}

#[test]
fn the_self_test_passes() {
    assert!(cli(&["--selftest".to_owned()])
        .stdout
        .contains("selftest ok"));
}

#[test]
fn a_tree_with_no_record_has_no_pointers_to_be_wrong_about() {
    assert_eq!(run(&repo("norec")).code, 0);
}

#[test]
fn a_bad_pointer_is_named_with_its_file_and_line() {
    let dir = repo("bad");
    record(&dir);
    put(
        &dir,
        "docs/a.md",
        "first\nsee research/questions/0499-gone.html\n",
    );
    commit(&dir);
    let refused = run(&dir);
    assert_eq!(refused.code, 1);
    assert!(refused
        .stderr
        .contains("docs/a.md:2: `research/questions/0499-gone.html` - no such question file"));
}

#[test]
fn a_fixture_names_its_own_record_refusal_data_is_data_and_a_landed_spec_keeps_history() {
    let dir = repo("kinds");
    record(&dir);
    put(&dir, "tests/x.py", "research/questions/0499-made-up.html\n");
    put(&dir, "tests/tooling/test_attempts.py", "research/water/\n");
    put(&dir, "specs/1-x/a.md", "PAGE=water SECTION=121\n");
    commit(&dir);
    assert_eq!(run(&dir).code, 0);
    put(&dir, "tests/y.py", "research/water/\n");
    commit(&dir);
    assert!(run(&dir).stderr.contains("tests/y.py:1:"));
}

#[test]
fn quotations_source_blocks_and_exempt_files_are_not_read() {
    let dir = repo("quoted");
    record(&dir);
    put(&dir, "docs/a.md", "the GM: *\"a research/citations directory in research/water/\"*\n<!-- SOURCE: GM NOTES\nresearch/water/\n<!-- END SOURCE -->\nclean\n");
    put(&dir, "specs/1-x/request.md", "research/water/\n");
    put(&dir, "tests/hooks/fixtures/x.json", "research/water/\n");
    put(&dir, "x/research/site/a.html", "research/water/\n");
    std::fs::write(dir.join("binary.bin"), [0xff, 0xfe]).unwrap();
    commit(&dir);
    assert_eq!(run(&dir).stderr, "");
    assert!(exempt("a/b/plan-review.json") && exempt("x.png"));
}

#[test]
fn a_long_list_is_cut_at_sixty() {
    let dir = repo("many");
    record(&dir);
    put(&dir, "docs/a.md", &"research/water/\n".repeat(61));
    commit(&dir);
    assert!(run(&dir).stderr.ends_with("  ... and 1 more\n"));
}

#[test]
fn a_line_with_no_pointer_but_an_old_number_is_still_asked() {
    let dir = repo("number");
    record(&dir);
    put(&dir, "docs/a.md", "see water 120 there, and a glued xwater 120 is not one\nresearch/water not/120x PAGE=nothing\n");
    commit(&dir);
    let refused = run(&dir);
    assert!(refused
        .stderr
        .contains("docs/a.md:1: `water 120` - a question's old page and number; it is now 0412"));
    assert_eq!(refused.stderr.matches("docs/a.md:1:").count(), 1);
}

#[test]
fn every_pointer_in_the_repository_resolves_to_a_fragment() {
    let real = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let done = cli(&[real.display().to_string()]);
    assert_eq!((done.code, done.stderr.as_str()), (0, ""));
}

#[test]
fn a_record_with_no_moved_files_has_no_old_names_to_refuse() {
    let dir = repo("nomap");
    put(&dir, "research/questions/0412-a.html", "x");
    put(&dir, "research/contents.json", r#"{"sections": []}"#);
    put(
        &dir,
        "docs/a.md",
        "see research/questions/0412-a.html and water 120\n",
    );
    commit(&dir);
    assert_eq!(run(&dir).code, 0);
}

#[test]
fn a_full_rendering_page_is_found_and_an_unknown_one_names_the_contents() {
    let dir = repo("rendering");
    record(&dir);
    put(
        &dir,
        "research/moved-303.json",
        r#"{"pages": {"rendering/roads": "roads"}}"#,
    );
    let mapping = super::Mapping::new(&dir.join("research"));
    assert_eq!(
        mapping.section_of("rendering/roads"),
        "research/contents.json#roads"
    );
    assert_eq!(
        mapping.section_of("nowhere"),
        "a section of research/contents.json"
    );
}

#[test]
fn a_self_test_row_with_the_wrong_verdict_is_named() {
    let (forms, mapping) = super::own_record();
    let rows = [
        ("research/water/", false, false, false, ""),
        ("clean", false, false, false, "something"),
    ];
    assert_eq!(
        super::wrong_rows(&rows, &forms, &mapping),
        ["research/water/", "clean"]
    );
}
