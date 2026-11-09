//! The detector over a tree of its own.

use super::super::tests::{commit, put, repo};
use super::{cases, cli, command_shapes, tracked_check};

fn owned(args: &[&str]) -> Vec<String> {
    args.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn every_content_case_and_command_shape_holds() {
    assert_eq!(cases().len(), 12);
    assert_eq!(command_shapes(), Vec::<&str>::new());
    assert!(cli(&owned(&["--selftest"]))
        .stdout
        .contains("12 content cases + 4 command shapes"));
}

fn triple() -> String {
    format!(
        "{} HEAD\nmine\n{}\ntheirs\n{} other\n",
        "<".repeat(7),
        "=".repeat(7),
        ">".repeat(7)
    )
}

#[test]
fn a_tracked_conflict_is_named_and_a_clean_tree_counted() {
    let dir = repo("tracked");
    put(&dir, "a.md", "clean\n");
    commit(&dir);
    let root = dir.display().to_string();
    assert_eq!(
        tracked_check(&root).stdout,
        "conflict-markers: none in 1 tracked file(s)\n"
    );
    put(&dir, "b.md", &triple());
    std::fs::write(dir.join("c.bin"), [0xff, 0xfe]).unwrap();
    commit(&dir);
    let refused = tracked_check(&root);
    assert_eq!(refused.code, 1);
    assert!(
        refused.stderr.contains(&format!("  {root}/b.md\n"))
            && refused.stderr.contains("CONFLICT MARKERS IN TRACKED FILES")
    );
}

#[test]
fn the_list_names_each_declaring_file() {
    let dir = repo("list");
    let root = dir.display().to_string();
    assert!(cli(&owned(&["--list", &root]))
        .stdout
        .contains("0 file(s) declare CONFLICT_MARKERS_OK - none"));
    put(
        &dir,
        "a.md",
        &format!(
            "# CONFLICT_MARKERS_OK: a fixture that must hold one\n{}",
            triple()
        ),
    );
    put(&dir, "b.md", "nothing\n");
    commit(&dir);
    let out = cli(&owned(&["--list", &root])).stdout;
    assert!(
        out.starts_with("  a.md: a fixture that must hold one\n")
            && out.ends_with("  1 file(s) declare CONFLICT_MARKERS_OK\n")
    );
    assert_eq!(cli(&[]).code, 2);
    assert_eq!(cli(&owned(&["--tracked", &root])).code, 0);
}

#[test]
fn a_row_with_the_wrong_verdict_is_named() {
    let wrong = [("wrong", "plain".to_owned(), true)];
    assert_eq!(super::wrong_cases(&wrong), ["wrong"]);
    let shape = [("echo".to_owned(), "/".to_owned(), true, "a shape")];
    assert_eq!(super::wrong_shapes(&shape), ["a shape"]);
}
