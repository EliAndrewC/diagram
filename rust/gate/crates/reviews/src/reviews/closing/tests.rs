//! The closing check's reasons on scratch trees: every branch and raise (feature 449 T127). The same answers as
//! `scripts/gates/close_check.py` are the differential's (`scratchpad/t127/diff.py`); these pin the branches. The implementation check
//! is a function handed in since feature 449 T132 (`claims::impl_check`, whose own tests hold its answers), so these hand in stand-ins.

use std::path::{Path, PathBuf};

use serde_json::json;

use super::super::tests::{dir, put, sh};
use super::{carries, fix_hold, open_fixes, reasons, Tools};

/// Each directory owes one item, named after it.
#[expect(clippy::unnecessary_wraps, reason = "an `ImplCheck`")]
fn owes(dirs: &[&Path]) -> Result<Vec<Vec<String>>, String> {
    Ok(dirs
        .iter()
        .map(|d| vec![format!("{} owes", super::name(d))])
        .collect())
}

/// Nothing owed, and the directories asked written to `asked` at their repository.
#[expect(clippy::unnecessary_wraps, reason = "an `ImplCheck`")]
fn none(dirs: &[&Path]) -> Result<Vec<Vec<String>>, String> {
    let names: Vec<String> = dirs.iter().map(|d| d.display().to_string()).collect();
    if let Some(root) = dirs.first().and_then(|d| d.parent()).and_then(Path::parent) {
        std::fs::write(root.join("asked"), names.join(" ")).unwrap();
    }
    Ok(vec![Vec::new(); dirs.len()])
}

fn raises(_: &[&Path]) -> Result<Vec<Vec<String>>, String> {
    Err("ValueError: the claims are unreadable".to_owned())
}

fn ask(
    root: &Path,
    impl_check: super::ImplCheck,
    dirs: &[&str],
) -> Result<Vec<Vec<String>>, String> {
    let tools = Tools {
        tree: root,
        impl_check,
    };
    let dirs: Vec<PathBuf> = dirs.iter().map(|d| root.join("specs").join(d)).collect();
    reasons(&tools, &root.join("specs"), &dirs).map(|found| found.each)
}

#[test]
fn the_carries_are_read_from_every_spec_in_order() {
    let d = dir("closing-carries");
    put(
        &d,
        "specs/.hid/spec.md",
        "`Carried: SC-001 -> 7 hidden.key`\n",
    );
    put(
        &d,
        "specs/200-a/spec.md",
        "Carried: SC-002 -> 0300 k-1 and Carried:SC-3 ->9 x\n",
    );
    put(&d, "specs/201-b/notes.md", "Carried: SC-004 -> 1 never\n");
    put(&d, "specs/file", "");
    let got = carries(&d.join("specs")).unwrap();
    assert_eq!(
        got,
        [
            (".hid", "SC-001", "7", "hidden.key"),
            ("200-a", "SC-002", "0300", "k-1"),
            ("200-a", "SC-3", "9", "x"),
        ]
        .map(|(a, b, c, e)| (a.to_owned(), b.to_owned(), c.to_owned(), e.to_owned()))
    );
    assert_eq!(carries(&d.join("none")).unwrap(), []);
    // a spec.md that cannot be read raises, as `read_text` did
    std::fs::create_dir_all(d.join("specs/202-c/spec.md")).unwrap();
    assert!(carries(&d.join("specs"))
        .unwrap_err()
        .starts_with("OSError"));
}

#[test]
fn a_feature_owes_its_report_its_carried_keys_and_its_implementation_check() {
    let d = dir("closing-reasons");
    put(
        &d,
        "specs/100-x/spec.md",
        "Carried: SC-001 -> 101 a\nCarried: SC-002 -> 0101 b\nCarried: SC-003 -> 103 c\n",
    );
    put(&d, "specs/101-y/measurements.json", r#"{"a": 1}"#);
    put(&d, "specs/102-z/report.md", "r");
    let got = ask(&d, owes, &["101-y", "102-z"]).unwrap();
    assert_eq!(
        got,
        [
            vec![
                "101-y has no report.md - `make feature-report F=101 WRITE=1` writes it (FR-009)"
                    .to_owned(),
                "100-x's SC-002 is carried here and `b` is not in 101-y/measurements.json (FR-014)"
                    .to_owned(),
                "101-y owes".to_owned(),
            ],
            vec!["102-z owes".to_owned()],
        ]
    );
    // measurements.json read as `set()` reads it: a list's strings, a string's characters; broken, unreadable or not UTF-8 is none
    for (text, owed) in [
        (r#"["a", "b", 1, null]"#, 0),
        (r#""ab""#, 0),
        ("{broken", 2),
        ("[NaN", 2),
        // Python's own `json.dump` writes a float that is no number bare; a string holding the words is a string
        (
            r#"{"a": NaN, "b": [-Infinity, Infinity], "c\\": 1, "d\"NaN": "Infinity \" NaN"}"#,
            0,
        ),
    ] {
        put(&d, "specs/101-y/measurements.json", text);
        put(&d, "specs/101-y/report.md", "");
        let n = ask(&d, owes, &["101-y"]).unwrap()[0].len();
        assert_eq!((text, n), (text, owed + 1));
    }
    std::fs::write(d.join("specs/101-y/measurements.json"), b"\xff").unwrap();
    assert_eq!(ask(&d, owes, &["101-y"]).unwrap()[0].len(), 3);
    // what `set()` cannot take raises
    for text in ["[[1]]", "[{}]", "null", "true", "5"] {
        put(&d, "specs/101-y/measurements.json", text);
        let raised = ask(&d, owes, &["101-y"]).unwrap_err();
        assert_eq!((text, &raised[..9]), (text, "TypeError"));
    }
}

#[test]
fn a_feature_s_number_is_read_as_python_s_int_reads_it() {
    let d = dir("closing-numbers");
    for (name, f) in [
        ("0200-a", "200"),
        ("000-z", "0"),
        ("+5-x", "5"),
        ("1_0-x", "10"),
        (
            "99999999999999999999999999999999999999999-x",
            "99999999999999999999999999999999999999999",
        ),
    ] {
        put(&d, &format!("specs/{name}/x"), "");
        let got = ask(&d, none, &[name]).unwrap();
        assert_eq!(
            got[0][0],
            format!(
                "{name} has no report.md - `make feature-report F={f} WRITE=1` writes it (FR-009)"
            )
        );
    }
    // `-5-x` splits to an empty number, `-0` is no sign
    for (name, ok) in [
        ("-5-x", false),
        ("1__0-x", false),
        ("_1-x", false),
        ("1_-x", false),
        ("٣-x", false),
    ] {
        put(&d, &format!("specs/{name}/x"), "");
        assert_eq!(ask(&d, none, &[name]).is_ok(), ok, "{name}");
    }
    assert_eq!(super::py_int_text(" -007 ").unwrap(), "-7");
    assert_eq!(super::py_int_text("-0").unwrap(), "0");
}

#[test]
fn a_feature_closed_before_the_check_is_not_asked() {
    let d = dir("closing-old");
    put(
        &d,
        "scripts/gates/closed-before-375.txt",
        "050-old\n051-older\n",
    );
    assert_eq!(
        ask(&d, owes, &["050-old", "052-new"]).unwrap()[0],
        Vec::<String>::new()
    );
    // nothing to ask, the check not asked
    assert_eq!(
        ask(&d, raises, &["050-old"]).unwrap(),
        [Vec::<String>::new()]
    );
    assert_eq!(ask(&d, raises, &[]).unwrap(), Vec::<Vec<String>>::new());
    std::fs::write(d.join("scripts/gates/closed-before-375.txt"), b"\xff\n").unwrap();
    assert!(ask(&d, owes, &["052-new"])
        .unwrap_err()
        .starts_with("UnicodeDecodeError"));
    sh(&d, "chmod 000 scripts/gates/closed-before-375.txt");
    let unreadable = ask(&d, owes, &["052-new"]);
    sh(&d, "chmod 644 scripts/gates/closed-before-375.txt");
    assert!(unreadable.unwrap_err().starts_with("OSError"));
}

#[test]
fn what_the_python_raised_fails_after_the_directories_before_it_are_asked() {
    let d = dir("closing-raise");
    put(&d, "specs/200-a/report.md", "");
    // a number that is no number raises on the report's line, the first directory still put to the implementation check
    let got = ask(&d, none, &["200-a", "x-b", "201-c"]).unwrap_err();
    assert!(got.starts_with("ValueError: invalid literal"), "{got}");
    let asked = std::fs::read_to_string(d.join("asked")).unwrap_or_default();
    assert!(asked.ends_with("specs/200-a"), "{asked}");
    // a carry read that fails after the report's line
    std::fs::create_dir_all(d.join("specs/300-s/spec.md")).unwrap();
    assert!(ask(&d, none, &["200-a"])
        .unwrap_err()
        .starts_with("OSError"));
}

#[test]
fn the_implementation_check_failing_fails_the_closing_check() {
    let d = dir("closing-impl");
    put(&d, "specs/200-a/report.md", "");
    // what it raised, then the closing check's own last line, as the by-path run's traceback came above its words (T127)
    assert_eq!(
        ask(&d, raises, &["200-a"]).unwrap_err(),
        "ValueError: the claims are unreadable\nimpl_check.missing raised"
    );
    // a later directory's raise comes after the implementation check of the earlier ones, whose own raise wins
    put(&d, "specs/x-b/x", "");
    assert!(ask(&d, raises, &["200-a", "x-b"])
        .unwrap_err()
        .starts_with("ValueError: the claims are unreadable"));
}

#[test]
fn an_open_tooling_fix_holds_the_feature_until_settled() {
    let d = dir("closing-fixes");
    put(&d, "specs/200-a/report.md", "");
    assert_eq!(fix_hold(&d.join("specs/200-a")), "");
    put(
        &d,
        "specs/200-a/arbiter.jsonl",
        &format!(
            "x\n{}\n{}\n{}\n{}\n{}\n{}\n",
            json!({"trigger": "t1", "fix": "open", "tooling_fix": "one"}),
            json!({"trigger": "t1", "fix": "open", "tooling_fix": "newer"}),
            json!({"trigger": "t2", "fix": "open", "tooling_fix": "two"}),
            json!({"trigger": 3, "fix": "open", "tooling_fix": ["a"]}),
            json!({"fix_of": "t2", "status": "done"}),
            json!({"fix_of": null, "status": "declined"})
        ),
    );
    assert_eq!(
        open_fixes(&d.join("specs/200-a")),
        [("t1", "newer"), ("3", "[\"a\"]")].map(|(a, b)| (a.to_owned(), b.to_owned()))
    );
    let got = ask(&d, none, &["200-a"]).unwrap();
    assert_eq!(got[0].len(), 1);
    assert!(
        got[0][0].starts_with("the round arbiter's tooling fix is open")
            && got[0][0].contains("    t1: newer\n    3: [\"a\"]\n")
            && got[0][0].contains("make arbiter-fix-declined")
    );
}
