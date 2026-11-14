//! The anchored edits: each its own write, a stale or doubled anchor skipped, a wrapped one found, the payload's two shapes and what
//! the Python refused or raised.

use std::path::Path;

use l7r_gate_core::ci::fixtures::scratch;

use super::{cli, reindent, selftest, Reply};

fn run(args: &[&str], stdin: &str, dir: &Path) -> Reply {
    let args: Vec<String> = args.iter().map(|s| (*s).to_owned()).collect();
    cli(&args, &mut stdin.as_bytes(), dir)
}

#[test]
fn the_selftest_passes_and_the_command_applies_each_edit_alone() {
    let dir = scratch("patch-cli");
    assert_eq!(
        run(&["--selftest"], "", &dir).stdout,
        "_patch selftest ok\n"
    );
    let f = dir.join("x.md");
    let path = f.to_str().unwrap();
    std::fs::write(&f, "one two\r\nthree\n").unwrap();
    let said = run(
        &[path],
        r#"[["one   two", "ONE"], {"anchor": "gone", "replacement": "x"}, ["three", "3"]]"#,
        &dir,
    );
    assert_eq!(
        (said.code, said.stdout.as_str()),
        (
            1,
            "applied: one two\nSKIPPED (0 matches): gone\napplied: three\n"
        )
    );
    assert_eq!(std::fs::read_to_string(&f).unwrap(), "ONE\n3\n");
    let one = run(&[path], r#"{"anchor": "ONE", "replacement": "1"}"#, &dir);
    assert_eq!((one.code, one.stdout.as_str()), (0, "applied: ONE\n"));
    assert_eq!(run(&[path], "[]", &dir).stdout, "\n");
    // an empty anchor matches everywhere, so it is skipped
    assert!(run(&[path], r#"[["", "x"]]"#, &dir)
        .stdout
        .starts_with("SKIPPED (5 matches)"));
    // a long anchor's label is its first sixty characters
    let long = "w".repeat(70);
    assert!(run(&[path], &format!("[[\"{long}\", \"x\"]]"), &dir)
        .stdout
        .ends_with(&format!("{}\n", "w".repeat(60))));
}

#[test]
fn what_the_python_refused_or_raised() {
    let dir = scratch("patch-refusals");
    let f = dir.join("x.md");
    let path = f.to_str().unwrap();
    std::fs::write(&f, "alpha\n").unwrap();
    assert_eq!(run(&[], "[]", &dir).code, 2);
    assert_eq!(run(&[path, "extra"], "[]", &dir).code, 2);
    let object = run(&[path], r#"[{"anchor": "a"}]"#, &dir);
    assert_eq!(
        (object.code, object.stderr.as_str()),
        (
            1,
            "_patch: an edit object carries exactly `anchor` and `replacement`: {'anchor': 'a'}\n"
        )
    );
    let shape = run(&[path], r#"["alpha"]"#, &dir);
    assert!(
        shape.code == 1
            && shape.stderr.contains("an edit is [anchor, replacement]")
            && shape.stderr.contains(": 'alpha'")
    );
    assert_eq!(run(&[path], "[[1, 2]]", &dir).code, 1);
    assert!(run(&[path], "not json", &dir).stderr.contains("Traceback"));
    // a value that is not text raises where the Python's did: the anchor at once, the replacement only when it would be written
    let anchor = run(
        &[path],
        r#"[["alpha", "beta"], {"anchor": 3, "replacement": "x"}]"#,
        &dir,
    );
    assert_eq!(anchor.code, 1);
    assert_eq!(std::fs::read_to_string(&f).unwrap(), "beta\n");
    let skipped = run(
        &[path],
        r#"[{"anchor": "nowhere", "replacement": null}]"#,
        &dir,
    );
    assert_eq!((skipped.code, skipped.stderr.as_str()), (1, ""));
    assert!(run(
        &[path],
        r#"[{"anchor": "beta", "replacement": null}]"#,
        &dir
    )
    .stderr
    .contains("Traceback"));
    assert!(run(
        &[dir.join("none").to_str().unwrap()],
        r#"[["a", "b"]]"#,
        &dir
    )
    .stderr
    .contains("Traceback"));
    std::fs::write(&f, [0xff]).unwrap();
    assert_eq!(run(&[path], r#"[["a", "b"]]"#, &dir).code, 1);
    // a file that cannot be written
    std::fs::create_dir(dir.join("ro")).unwrap();
    std::fs::write(dir.join("ro/f.md"), "alpha\n").unwrap();
    let mode = |m: &str| {
        std::process::Command::new("chmod")
            .arg(m)
            .arg(dir.join("ro/f.md"))
            .status()
            .unwrap()
    };
    mode("444");
    let ro = run(
        &[dir.join("ro/f.md").to_str().unwrap()],
        r#"[["alpha", "b"]]"#,
        &dir,
    );
    mode("644");
    assert_eq!(ro.code, 1);
    // the selftest's own failure is named: a directory where its file goes
    let blocked = scratch("patch-selftest-blocked");
    std::fs::create_dir(blocked.join("x.md")).unwrap();
    assert!(selftest(&blocked).is_err());
    assert!(run(&["--selftest"], "", &blocked)
        .stderr
        .contains("Traceback"));
}

#[test]
fn a_self_test_case_that_fails_names_itself_and_stdin_must_be_text() {
    let dir = scratch("patch-case");
    let f = dir.join("x.md");
    let failed = super::case(&f, "the case", "a\n", &[("a", "b")], ("c\n", 0)).unwrap_err();
    assert_eq!(
        failed,
        "_patch selftest: the case: \"b\\n\" with 0 skipped ([\"applied: a\"])"
    );
    let args = vec![f.to_string_lossy().into_owned()];
    let bad = cli(&args, &mut &[0xff_u8][..], &dir);
    assert!(bad.code == 1 && bad.stderr.contains("UnicodeDecodeError"));
}

#[test]
fn continuation_lines_take_the_match_s_indent() {
    assert_eq!(reindent("a\nb", ""), "a\nb");
    assert_eq!(reindent("a", "  "), "a");
    assert_eq!(reindent("a\nb\n\n\tc", "  "), "a\n  b\n\n\tc");
}
