//! The door's command lines: every form `usage_log.py` and `hm_escape.py reason-ok` took, and every refusal argparse made.

use std::path::Path;

use super::{escape_cli, goals_cli, record_cli};

fn words(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn repo(tag: &str) -> l7r_guard::shared::tempdir::TempDir {
    let root = crate::checks::scratch(tag);
    assert!(std::process::Command::new("git")
        .arg("-C")
        .arg(&root)
        .args(["init", "-q"])
        .status()
        .unwrap()
        .success());
    root
}

fn lines(root: &Path) -> Vec<String> {
    std::fs::read_to_string(root.join(".git/tool-usage.jsonl"))
        .unwrap_or_default()
        .lines()
        .map(str::to_owned)
        .collect()
}

#[test]
fn a_record_in_every_form_argparse_took_lands_one_line() {
    let root = repo("usage-forms");
    let other = repo("usage-other");
    let forms = [
        &["--tool", "a", "--kind", "step", "--outcome", "changed"][..],
        &["--outcome=passed", "--kind=check", "--tool=b"],
        &["--to", "c", "--k", "hook", "--out", "-1"],
        &[
            "--tool",
            "d",
            "--kind",
            "target",
            "--outcome",
            "ran",
            "--root",
            "",
        ],
        &[
            "--tool",
            "e",
            "--kind",
            "target",
            "--outcome",
            "ran",
            "--root",
            "/nonexistent/x",
        ],
        &[
            "--tool",
            "f",
            "--kind",
            "step",
            "--outcome",
            "x",
            "--tool",
            "g",
        ],
    ];
    for form in forms {
        let said = record_cli(&words(form), &root);
        assert_eq!(
            (said.code, said.stdout.as_str(), said.stderr.as_str()),
            (0, "", "")
        );
    }
    let said = record_cli(
        &words(&["--tool", "h", "--kind", "step", "--outcome", "y", "--root"]),
        &root,
    );
    assert_eq!(said.code, 2);
    let said = record_cli(
        &words(&[
            "--tool",
            "h",
            "--kind",
            "step",
            "--outcome",
            "y",
            "--root",
            &other.to_string_lossy(),
        ]),
        &root,
    );
    assert_eq!(said.code, 0);
    let mine = lines(&root);
    assert_eq!(mine.len(), 5, "{mine:?}");
    for (line, want) in mine.iter().zip([
        "\"tool\": \"a\", \"kind\": \"step\", \"outcome\": \"changed\"",
        "\"tool\": \"b\", \"kind\": \"check\", \"outcome\": \"passed\"",
        "\"tool\": \"c\", \"kind\": \"hook\", \"outcome\": \"-1\"",
        "\"tool\": \"d\", \"kind\": \"target\", \"outcome\": \"ran\"",
        "\"tool\": \"g\", \"kind\": \"step\", \"outcome\": \"x\"",
    ]) {
        assert!(line.contains(want), "{line}");
    }
    assert_eq!(lines(&other).len(), 1);
}

#[test]
fn argparse_refusals_are_exit_two_and_help_is_zero() {
    let root = repo("usage-refused");
    for form in [
        &[][..],
        &["--tool", "a", "--kind", "nope", "--outcome", "x"],
        &["--tool", "a", "--outcome", "x"],
        &["--tool", "a", "--kind", "step", "--outcome", "--root"],
        &["--tool", "a", "--kind", "step", "--outcome", "x", "extra"],
        &[
            "--tool",
            "a",
            "--kind",
            "step",
            "--outcome",
            "x",
            "--bogus",
            "y",
        ],
        &["--o", "x"],
        &["--", "x"],
        &["-x"],
    ] {
        let said = record_cli(&words(form), &root);
        assert_eq!((said.code, said.stdout.as_str()), (2, ""), "{form:?}");
        assert!(said.stderr.starts_with("l7r-gate log usage: error: "));
    }
    assert!(lines(&root).is_empty());
    for form in [&["-h"][..], &["--help"], &["--he"], &["--tool", "a", "-h"]] {
        let said = record_cli(&words(form), &root);
        assert_eq!(said.code, 0);
        assert!(said.stdout.starts_with("usage: l7r-gate log usage"));
    }
}

#[test]
fn goals_are_each_recorded_ran_and_none_is_nothing() {
    let root = repo("usage-goals");
    assert_eq!(goals_cli(&words(&["help", "done"]), &root).code, 0);
    assert_eq!(goals_cli(&[], &root).code, 0);
    let mine = lines(&root);
    assert_eq!(mine.len(), 2);
    assert!(mine[1].contains("\"tool\": \"done\", \"kind\": \"target\", \"outcome\": \"ran\""));
    let nowhere = crate::checks::scratch("usage-nowhere");
    assert_eq!(goals_cli(&words(&["x"]), &nowhere).code, 0);
}

/// A stdin whose every read fails.
struct Broken;

impl std::io::Read for Broken {
    fn read(&mut self, _: &mut [u8]) -> std::io::Result<usize> {
        Err(std::io::Error::other("gone"))
    }
}

#[test]
fn the_reason_floor_reads_stdin_as_python_stripped_it() {
    let ok = |text: &[u8]| escape_cli(&words(&["reason-ok"]), &mut &text[..]).code;
    assert_eq!(ok(b"CI is down\n"), 0);
    assert_eq!(ok(b"  read-only  \n"), 0);
    assert_eq!(ok(b"required\n"), 1);
    assert_eq!(ok(b""), 1);
    assert_eq!(ok(b"\x1cabcd\x1cefgh\x1c"), 0);
    // a byte UTF-8 cannot take is one character each, as `surrogateescape` reads it: `\xff\xfe` is two of the eight
    assert_eq!(ok(b"ab \xff cdefgh"), 0);
    assert_eq!(ok(b"ab \xe2\x82"), 1);
    assert_eq!(ok(b"abcde \xff\xfe"), 0);
    assert_eq!(ok(b"abcd \xff\xfe"), 1);
    assert_eq!(escape_cli(&[], &mut &b""[..]).code, 2);
    // a stdin that cannot be read fails, as the Python's read raised
    let gone = escape_cli(&words(&["reason-ok"]), &mut Broken);
    assert_eq!((gone.code, gone.stdout.as_str()), (1, ""));
}
