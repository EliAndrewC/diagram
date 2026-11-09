//! The bar, its carve-out, and the directory ceiling.

use std::path::Path;

use super::super::scratch;
use super::super::tests::{commit, put, repo};
use super::{
    cli, crowded, dir_counts, raw_lines, run, DIR_GUIDANCE, GUIDANCE, HEADER_LINES, MARKER,
    MAX_LINES,
};

fn lines(n: usize) -> String {
    "x = 1\n".repeat(n)
}

fn ask(args: &[&str]) -> super::Outcome {
    cli(&args.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>())
}

#[test]
fn the_bar_is_a_thousand_raw_lines_and_a_thousand_itself_passes() {
    let dir = scratch("bar");
    put(&dir, "edge.py", &lines(MAX_LINES));
    put(&dir, "big.rs", &lines(MAX_LINES + 1));
    let scan = run(&dir);
    assert_eq!(
        (scan.over.len(), scan.over[0].0.as_str(), scan.scanned),
        (1, "big.rs", 2)
    );
    assert_eq!(raw_lines(b"a\nb"), 2);
    assert_eq!(raw_lines(b"\n\n"), 2);
    assert_eq!(raw_lines(b""), 0);
}

#[test]
fn a_justified_file_passes_and_a_bare_or_buried_marker_does_not() {
    let dir = scratch("marker");
    put(
        &dir,
        "ok.py",
        &format!(
            "# {MARKER} an ordered registry whose row order is the execution contract\n{}",
            lines(MAX_LINES + 1)
        ),
    );
    put(
        &dir,
        "thin.py",
        &format!("# {MARKER} ordered\n{}", lines(MAX_LINES + 1)),
    );
    put(
        &dir,
        "late.py",
        &format!(
            "{}# {MARKER} an ordered registry whose rows are the contract\n{}",
            lines(HEADER_LINES + 1),
            lines(MAX_LINES)
        ),
    );
    let scan = run(&dir);
    assert_eq!(
        scan.justified
            .iter()
            .map(|(p, ..)| p.as_str())
            .collect::<Vec<_>>(),
        ["ok.py"]
    );
    assert_eq!(
        scan.over
            .iter()
            .map(|(p, _)| p.as_str())
            .collect::<Vec<_>>(),
        ["late.py", "thin.py"]
    );
    let listed = ask(&["--list", &dir.display().to_string()]);
    assert!(
        listed.stdout.contains("JUSTIFIED: an ordered")
            && listed.stdout.contains("(ceiling 5,000)")
    );
}

#[test]
fn the_excluded_trees_are_not_scanned() {
    let dir = repo("skip");
    for rel in [
        "legacy-hand-authored-pool/a.py",
        ".clones/b.py",
        "specs/c.py",
        "x/__pycache__/d.py",
        "node_modules/e.py",
    ] {
        put(&dir, rel, &lines(MAX_LINES + 1));
    }
    put(&dir, "ok.py", "x = 1\n");
    put(&dir, "note.txt", &lines(MAX_LINES + 1));
    commit(&dir);
    assert_eq!(run(&dir).over, Vec::new());
    assert_eq!(run(&dir).scanned, 1);
}

#[test]
fn a_deleted_file_still_in_the_index_is_not_read() {
    let dir = repo("deleted");
    put(&dir, "gone.py", "x = 1\n");
    put(&dir, "kept.py", "x = 1\n");
    commit(&dir);
    std::fs::remove_file(dir.join("gone.py")).unwrap();
    assert_eq!(run(&dir).scanned, 1);
}

#[test]
fn scanning_nothing_fails_loudly_and_a_refusal_prints_the_procedure() {
    let dir = scratch("zero");
    let empty = ask(&[&dir.display().to_string()]);
    assert_eq!(empty.code, 1);
    assert!(empty.stderr.contains("scanned ZERO files"));
    put(&dir, "big.py", &lines(MAX_LINES + 2));
    let refused = ask(&[&dir.display().to_string()]);
    assert!(
        refused.stderr.contains("1 file(s) past the 1,000-line bar")
            && refused.stderr.contains("(+2)")
            && refused.stderr.contains("big.py")
            && refused.stderr.contains("Principle X clause 13")
    );
}

#[test]
fn the_refusal_says_split_to_about_two_thirds_never_trim_and_states_no_duration() {
    assert!(
        GUIDANCE.contains("NEVER TRIM IT TO JUST UNDER THE BAR")
            && GUIDANCE.contains("about 666 lines each")
            && GUIDANCE.contains("re-exporting every name importers used")
    );
    for text in [GUIDANCE, DIR_GUIDANCE] {
        assert!(!text.contains(" minutes") && !text.contains(" seconds"));
    }
}

#[test]
fn the_ceiling_fires_past_the_limit_and_counts_each_file_in_its_own_directory() {
    let dir = scratch("dirs");
    for (name, n) in [
        ("full", 3),
        ("over", 4),
        ("over/deep", 1),
        (".clones/x", 9),
        (".git", 9),
    ] {
        for i in 0..n {
            put(&dir, &format!("{name}/{i}.json"), "{}");
        }
    }
    put(&dir, "top.json", "{}");
    assert_eq!(crowded(&dir, 3), [("over".to_owned(), 4)]);
    let counts = dir_counts(&dir);
    assert_eq!(
        (
            counts["."],
            counts["over/deep"],
            counts.contains_key(".clones/x")
        ),
        (1, 1, false)
    );
}

#[test]
fn a_crowded_directory_fails_the_check() {
    let dir = repo("crowded");
    put(&dir, "a.py", "x = 1\n");
    for i in 0..=super::MAX_DIR_FILES {
        std::fs::create_dir_all(dir.join("full")).unwrap();
        std::fs::write(dir.join("full").join(i.to_string()), "").unwrap();
    }
    let refused = ask(&[&dir.display().to_string()]);
    assert_eq!(refused.code, 1);
    assert!(
        refused
            .stderr
            .contains("1 director(ies) past the 5,000-file ceiling")
            && refused.stderr.contains("(+1)  full/")
    );
    assert_eq!(ask(&["--list", &dir.display().to_string()]).code, 0);
}

#[test]
fn the_repository_itself_is_under_the_bar_and_a_relative_root_prints_relative_paths() {
    let real = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    assert_eq!(run(&real).over, Vec::new());
    assert_eq!(crowded(&real, super::MAX_DIR_FILES), Vec::new());
    assert!(ask(&["--selftest"]).stdout.contains("selftest ok"));
    let listed = ask(&["--list"]);
    assert_eq!(listed.code, 0);
    assert!(listed.stdout.contains("JUSTIFIED") || listed.stdout.contains("every one of"));
    assert_eq!(ask(&[]).code, 0);
}

#[test]
fn several_over_the_bar_list_largest_first_and_a_path_is_shown_from_its_root() {
    let dir = repo("order");
    put(&dir, "small.py", &lines(MAX_LINES + 1));
    put(&dir, "large.py", &lines(MAX_LINES + 2));
    put(
        &dir,
        "a.py",
        &format!(
            "# {MARKER} an ordered registry whose row order is the execution contract\n{}",
            lines(MAX_LINES + 1)
        ),
    );
    put(
        &dir,
        "b.py",
        &format!(
            "# {MARKER} an ordered registry whose row order is the execution contract\n{}",
            lines(MAX_LINES + 2)
        ),
    );
    commit(&dir);
    let root = dir.display().to_string();
    let refused = ask(&[&root]);
    assert!(refused.stderr.find("large.py").unwrap() < refused.stderr.find("small.py").unwrap());
    let listed = ask(&["--list", &root]).stdout;
    assert!(listed.find("b.py").unwrap() < listed.find("a.py").unwrap());
    assert_eq!(super::shown_path(".", "a.py"), "a.py");
    assert_eq!(super::shown_path("/x", "a.py"), "/x/a.py");
    for name in ["one", "two"] {
        for i in 0..4 {
            put(&dir, &format!("{name}/{i}.json"), "{}");
        }
    }
    assert_eq!(crowded(&dir, 3).len(), 3);
}
