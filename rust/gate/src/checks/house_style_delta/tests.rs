//! What this change wrote, and what it did not.

use super::super::tests::{based, commit, put, repo};
use super::{british, cli, exempt_path, findings, inside_a_name};

fn base(tag: &str) -> std::path::PathBuf {
    let dir = repo(tag);
    put(&dir, "base.md", "the pre-existing colour stays here\n");
    commit(&dir);
    based(&dir);
    dir
}

#[test]
fn a_word_this_change_wrote_is_named_with_its_line_and_an_untracked_file_is_scanned() {
    let dir = base("wrote");
    put(
        &dir,
        "base.md",
        "the pre-existing colour stays here\nan added behaviour line\n",
    );
    put(&dir, "new.md", "a fresh centre here\n");
    let got = findings(&dir);
    assert_eq!(
        got,
        [
            "base.md:2: 'behaviour' - CLAUDE.md: American spellings, project-wide",
            "new.md:1: 'centre' - CLAUDE.md: American spellings, project-wide"
        ]
    );
    let refused = cli(&[dir.display().to_string()]);
    assert_eq!(refused.code, 1);
    assert!(refused.stdout.contains("2 British spelling(s)"));
}

#[test]
fn a_quotation_a_code_span_and_a_straight_quote_in_prose_are_someone_else_s() {
    let dir = base("quoted");
    put(&dir, "a.md", "<blockquote>\nthe colour there\n</blockquote>\nnames `colour` here\nsaid \"colour\" once\n");
    assert_eq!(findings(&dir), Vec::<String>::new());
    put(&dir, "b.py", "s = \"colour\"\n");
    assert_eq!(findings(&dir).len(), 1);
}

#[test]
fn a_moved_line_is_not_flagged_but_a_changed_one_owes_the_fix() {
    let dir = repo("moved");
    put(
        &dir,
        "a.md",
        "one line of colour text here\nanother line of neighbour text\n",
    );
    commit(&dir);
    based(&dir);
    put(&dir, "a.md", "another line of neighbour text\n");
    put(&dir, "b.md", "one line of colour text here\n");
    assert_eq!(findings(&dir), Vec::<String>::new());
    put(&dir, "b.md", "one line of colour text there\n");
    assert_eq!(findings(&dir).len(), 1);
}

#[test]
fn a_whole_file_only_moved_is_nothing_this_change_wrote() {
    let dir = repo("whole");
    put(&dir, "a.md", "one line of colour text here\n");
    commit(&dir);
    based(&dir);
    std::fs::rename(dir.join("a.md"), dir.join("b.md")).unwrap();
    assert_eq!(findings(&dir), Vec::<String>::new());
}

#[test]
fn a_line_the_base_already_held_and_a_short_one_copied_are_told_apart() {
    let dir = base("copied");
    put(&dir, "copy.md", "the pre-existing colour stays here\n");
    put(&dir, "short.md", "a colour\n");
    let got = findings(&dir);
    assert_eq!(got.len(), 1);
    assert!(got[0].starts_with("short.md:1:"));
}

#[test]
fn a_british_word_inside_a_proper_name_is_not_reported() {
    let line = "by Mary Neighbour Parent and";
    let at = line.find("Neighbour").unwrap();
    assert!(inside_a_name(line, at, at + 9));
    let opens = "Neighbour Parent";
    assert!(!inside_a_name(opens, 0, 9));
    let lower = "the neighbour Parent";
    assert!(!inside_a_name(lower, 4, 13));
    let dir = base("name");
    put(&dir, "a.md", "compiled by Mary Neighbour Parent in 1900\n");
    assert_eq!(findings(&dir), Vec::<String>::new());
}

#[test]
fn what_is_exempt_by_its_path() {
    for path in [
        "CLAUDE.md",
        "specs/236-x/request.md",
        "tests/hooks/fixtures/x.txt",
        "x/.clones/y.md",
        "specs/412-x/measure/a_cells_by_address.txt",
    ] {
        assert!(exempt_path(path), "{path}");
    }
    for path in ["docs/a.md", "specs/412-x/a_cells_by_address.txt"] {
        assert!(!exempt_path(path), "{path}");
    }
    let dir = base("exempt");
    put(
        &dir,
        "specs/236-x/request.md",
        "a colour of ours here today\n",
    );
    put(&dir, "big.md", &"x".repeat(2_000_001));
    assert_eq!(findings(&dir), Vec::<String>::new());
    assert_eq!(cli(&[dir.display().to_string()]).code, 0);
}

#[test]
fn the_word_table_is_the_guard_s_own_and_the_self_test_passes() {
    assert!(british().contains(&"colour") && british().contains(&"centre"));
    assert!(cli(&["--selftest".to_owned()])
        .stdout
        .contains("selftest ok"));
}

#[test]
fn a_staged_move_is_nothing_this_change_wrote_and_no_base_reads_the_worktree() {
    let dir = repo("staged");
    put(&dir, "a.md", "one line of colour text here\n");
    commit(&dir);
    based(&dir);
    std::fs::copy(dir.join("a.md"), dir.join("b.md")).unwrap();
    assert!(std::process::Command::new("git")
        .arg("-C")
        .arg(&dir)
        .args(["add", "-A"])
        .status()
        .unwrap()
        .success());
    assert_eq!(findings(&dir), Vec::<String>::new());
    let none = repo("nobase");
    put(&none, "a.md", "one line of plain text here\n");
    commit(&none);
    put(&none, "b.md", "a line of colour text here\n");
    assert_eq!(findings(&none).len(), 1);
}
