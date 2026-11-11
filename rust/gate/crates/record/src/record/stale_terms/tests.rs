//! The cases of the stale-value search, and every way of asking.

use std::path::{Path, PathBuf};

use super::{
    all_found, cli, criteria_left_behind, dirs_cli, read_dir, render, stale_candidates, tokens,
    watched_lines, Files,
};

fn files(list: &[(&str, &str)]) -> Files {
    list.iter()
        .map(|(n, t)| ((*n).to_owned(), (*t).to_owned()))
        .collect()
}

fn words(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

const OLD: &str = "the `tier` runs on Sonnet here\n";
const NEW: &str = "the `tier` runs on Opus here\n";

#[test]
fn a_line_naming_the_subject_with_the_old_value_is_a_candidate() {
    let old = files(&[("spec.md", OLD), ("plan.md", "keep `tier` on Sonnet\n")]);
    let new = files(&[("spec.md", NEW), ("plan.md", "keep `tier` on Sonnet\n")]);
    let found = stale_candidates(&old, &new);
    assert_eq!(found.len(), 1);
    assert_eq!(
        (
            found[0].file.as_str(),
            found[0].line,
            found[0].subject.as_str()
        ),
        ("plan.md", 1, "tier")
    );
    assert_eq!(found[0].old_values, ["sonnet"]);
    assert!(render(&found).contains("plan.md:1  `tier` still with sonnet\n      keep `tier` on Sonnet\n      (changed in spec.md to: the `tier` runs on Opus here)"));
}

#[test]
fn no_subject_no_value_or_a_pure_insertion_yields_nothing() {
    let one = |a: &str, b: &str| {
        stale_candidates(
            &files(&[("s.md", a)]),
            &files(&[("s.md", b), ("p.md", "`tier` Sonnet\n")]),
        )
    };
    assert!(one("no ticks on Sonnet\n", "no ticks on Opus\n").is_empty());
    assert!(one("`tier` the\n", "`tier` was\n").is_empty());
    assert!(one("`tier` only\n", "`tier` only\nanother line\n").is_empty());
    assert!(stale_candidates(&files(&[]), &files(&[("s.md", NEW)])).is_empty());
}

#[test]
fn skipped_files_and_history_and_verify_notes_keep_their_old_values() {
    assert!(watched_lines("request.md", "x\n").is_empty());
    assert!(watched_lines("measure/a.md", "x\n").is_empty());
    let text = "a\n## Review history\nb\n## Next\nc\n      verify: d\n";
    assert_eq!(
        watched_lines("s.md", text)
            .iter()
            .map(|l| l.1)
            .collect::<Vec<_>>(),
        ["a", "## Next", "c"]
    );
    let old = files(&[("request.md", OLD)]);
    let new = files(&[("request.md", NEW), ("p.md", "`tier` Sonnet\n")]);
    assert!(stale_candidates(&old, &new).is_empty());
}

#[test]
fn a_line_rewritten_from_one_naming_the_subject_was_revisited_on_purpose() {
    let old = files(&[("s.md", OLD), ("p.md", "about `tier` before\n")]);
    let new = files(&[("s.md", NEW), ("p.md", "about `tier` on Sonnet now\n")]);
    assert!(stale_candidates(&old, &new).is_empty());
    let fresh = files(&[("s.md", OLD), ("p.md", "about nothing\n")]);
    assert_eq!(stale_candidates(&fresh, &new).len(), 1);
}

#[test]
fn a_subjects_own_words_are_no_old_value_and_each_line_is_named_once() {
    let old = files(&[(
        "s.md",
        "the `tier list` x-value Sonnet\nthe `tier list` Haiku here\n",
    )]);
    let new = files(&[
        (
            "s.md",
            "the `tier list` x-value Opus\nthe `tier list` Fable here\n",
        ),
        ("p.md", "`tier list` Sonnet Haiku\n"),
    ]);
    let found = stale_candidates(&old, &new);
    assert_eq!(found.len(), 1);
    assert_eq!(found[0].old_values, ["sonnet"]);
    assert!(!tokens("the Sonnet").contains("the"));
}

const SPEC_A: &str =
    "- **FR-001**: must do one\n  and more\n- **SC-001** (FR-001, FR-002): holds\n";
const SPEC_B: &str =
    "- **FR-001**: must do two\n  and more\n- **SC-001** (FR-001, FR-002): holds\n";

#[test]
fn a_criterion_citing_a_rewritten_requirement_and_left_untouched_is_named() {
    let found = criteria_left_behind(
        &files(&[("spec.md", SPEC_A)]),
        &files(&[("spec.md", SPEC_B)]),
    );
    assert_eq!(found.len(), 1);
    assert_eq!(found[0].old_values, ["FR-001"]);
    let shown = render(&found);
    assert!(shown.contains("spec.md:3  `SC-001` cites FR-001, which the change rewrote - the criterion was not touched"), "{shown}");
    let touched = "- **FR-001**: must do two\n- **SC-001** (FR-001): holds, changed\n";
    assert!(criteria_left_behind(
        &files(&[("spec.md", SPEC_A)]),
        &files(&[("spec.md", touched)])
    )
    .is_empty());
    assert!(criteria_left_behind(
        &files(&[("plan.md", SPEC_A)]),
        &files(&[("plan.md", SPEC_B)])
    )
    .is_empty());
    assert!(criteria_left_behind(&files(&[]), &files(&[("spec.md", SPEC_B)])).is_empty());
    let unrelated = "- **FR-001**: must do one\n- **SC-001** (FR-009): holds\n";
    assert!(criteria_left_behind(
        &files(&[("spec.md", unrelated)]),
        &files(&[("spec.md", unrelated)])
    )
    .is_empty());
}

fn lines(one: impl Fn(usize) -> String) -> String {
    (0..30).map(one).collect::<Vec<_>>().join("\n") + "\n"
}

#[test]
fn the_report_says_none_and_trims_past_twenty_five() {
    assert!(render(&[]).starts_with("stale-terms: no candidate"));
    let old = lines(|i| format!("`s{i}` value{i}x"));
    let new = lines(|i| format!("`s{i}` other{i}y"));
    let also = lines(|i| format!("`s{i}` value{i}x again"));
    let found = all_found(
        &files(&[("a.md", &old)]),
        &files(&[("a.md", &new), ("b.md", &also)]),
    );
    assert_eq!(found.len(), 30);
    assert!(render(&found).ends_with("... and 5 more"));
}

fn write(root: &Path, name: &str, text: &[u8]) {
    let path = root.join(name);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

#[test]
fn a_directory_is_read_as_text_alone() {
    let d = crate::checks::scratch("stale-read");
    write(&d, "deep/a.md", b"x");
    write(&d, "__pycache__/b.md", b"y");
    write(&d, "bin.dat", &[0xff, 0xfe]);
    write(&d, "big.md", &vec![b'x'; 1_000_001]);
    assert_eq!(read_dir(&d).keys().collect::<Vec<_>>(), ["deep/a.md"]);
}

fn clone(tag: &str) -> PathBuf {
    let root = crate::checks::scratch(tag);
    for args in [
        &["init", "-q"][..],
        &["config", "user.email", "t@t"],
        &["config", "user.name", "t"],
    ] {
        assert!(std::process::Command::new("git")
            .arg("-C")
            .arg(&root)
            .args(args)
            .status()
            .unwrap()
            .success());
    }
    write(&root, "specs/449-x/spec.md", OLD.as_bytes());
    write(&root, "specs/449-x/plan.md", b"keep `tier` on Sonnet\n");
    write(&root, "specs/449-x/raw.dat", &[0xff]);
    for args in [&["add", "-A"][..], &["commit", "-qm", "a"]] {
        assert!(std::process::Command::new("git")
            .arg("-C")
            .arg(&root)
            .args(args)
            .status()
            .unwrap()
            .success());
    }
    write(&root, "specs/449-x/spec.md", NEW.as_bytes());
    root
}

#[test]
fn a_ref_a_snapshot_and_their_absence_are_each_answered() {
    let root = clone("stale-cli");
    let there = root.display().to_string();
    let got = cli(&words(&["449", "--clone", &there, "--against", "HEAD"]));
    assert_eq!(got.code, 1, "{}", got.stderr);
    assert!(got.stdout.contains("plan.md:1"));
    let got = cli(&words(&["449-x", "--clone", &there]));
    assert!(got.code == 2 && got.stderr.contains("no snapshot of 449-x"));
    write(
        &root,
        ".git/review-round/449-x/snapshot/spec.md",
        NEW.as_bytes(),
    );
    let got = cli(&words(&["449", "--clone", &there]));
    assert!(got.code == 0 && got.stdout.starts_with("stale-terms: no candidate"));
    assert_eq!(cli(&words(&["zzz", "--clone", &there])).code, 2);
    assert_eq!(cli(&[]).code, 2);
    assert_eq!(cli(&words(&["--clone", &there])).code, 2);
    assert_eq!(cli(&words(&["449", "--clone", "/nonexistent/c"])).code, 2);
}

#[test]
fn the_guards_question_gives_the_count_and_the_report_or_nothing() {
    let root = crate::checks::scratch("stale-dirs");
    write(&root, "old/s.md", OLD.as_bytes());
    write(&root, "old/p.md", b"keep `tier` on Sonnet\n");
    write(&root, "new/s.md", NEW.as_bytes());
    write(&root, "new/p.md", b"keep `tier` on Sonnet\n");
    let (old, new) = (
        root.join("old").display().to_string(),
        root.join("new").display().to_string(),
    );
    let got = dirs_cli(&words(&[&old, &new]));
    assert!(
        got.stdout.starts_with("1\nstale-terms: 1 candidate(s)"),
        "{}",
        got.stdout
    );
    assert_eq!(dirs_cli(&words(&[&new, &new])).stdout, "");
    assert_eq!(dirs_cli(&[]).code, 2);
}
