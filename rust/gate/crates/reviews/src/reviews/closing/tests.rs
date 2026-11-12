//! The closing check's reasons on scratch trees: every branch and raise (feature 449 T127). The same answers as
//! `scripts/gates/close_check.py` are the differential's (`scratchpad/t127/diff.py`); these pin the branches.

use std::path::{Path, PathBuf};

use serde_json::json;

use super::super::tests::{dir, put, sh};
use super::{carries, fix_hold, open_fixes, reasons, Tools};

/// An `impl_check.py` stand-in under `scripts/record/` with `body` after the argument check.
fn impl_check(root: &Path, body: &str) {
    put(
        root,
        "scripts/record/impl_check.py",
        &format!("import json, sys\nassert sys.argv[1] == '--missing-json'\n{body}\n"),
    );
}

const OWES: &str = "print(json.dumps([[a.rsplit('/', 1)[-1] + ' owes'] for a in sys.argv[2:]]))";

fn ask(root: &Path, python: &str, dirs: &[&str]) -> Result<Vec<Vec<String>>, String> {
    let tools = Tools { tree: root, python };
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
    impl_check(&d, OWES);
    put(
        &d,
        "specs/100-x/spec.md",
        "Carried: SC-001 -> 101 a\nCarried: SC-002 -> 0101 b\nCarried: SC-003 -> 103 c\n",
    );
    put(&d, "specs/101-y/measurements.json", r#"{"a": 1}"#);
    put(&d, "specs/102-z/report.md", "r");
    let got = ask(&d, "python3", &["101-y", "102-z"]).unwrap();
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
        let n = ask(&d, "python3", &["101-y"]).unwrap()[0].len();
        assert_eq!((text, n), (text, owed + 1));
    }
    std::fs::write(d.join("specs/101-y/measurements.json"), b"\xff").unwrap();
    assert_eq!(ask(&d, "python3", &["101-y"]).unwrap()[0].len(), 3);
    // what `set()` cannot take raises
    for text in ["[[1]]", "[{}]", "null", "true", "5"] {
        put(&d, "specs/101-y/measurements.json", text);
        let raised = ask(&d, "python3", &["101-y"]).unwrap_err();
        assert_eq!((text, &raised[..9]), (text, "TypeError"));
    }
}

#[test]
fn a_feature_s_number_is_read_as_python_s_int_reads_it() {
    let d = dir("closing-numbers");
    impl_check(&d, "print(json.dumps([[] for a in sys.argv[2:]]))");
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
        let got = ask(&d, "python3", &[name]).unwrap();
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
        assert_eq!(ask(&d, "python3", &[name]).is_ok(), ok, "{name}");
    }
    assert_eq!(super::py_int_text(" -007 ").unwrap(), "-7");
    assert_eq!(super::py_int_text("-0").unwrap(), "0");
}

#[test]
fn a_feature_closed_before_the_check_is_not_asked() {
    let d = dir("closing-old");
    impl_check(&d, OWES);
    put(
        &d,
        "scripts/gates/closed-before-375.txt",
        "050-old\n051-older\n",
    );
    assert_eq!(
        ask(&d, "python3", &["050-old", "052-new"]).unwrap()[0],
        Vec::<String>::new()
    );
    // nothing to ask, no process
    assert_eq!(
        ask(&d, "/no/such/python", &["050-old"]).unwrap(),
        [Vec::<String>::new()]
    );
    assert_eq!(
        ask(&d, "/no/such/python", &[]).unwrap(),
        Vec::<Vec<String>>::new()
    );
    std::fs::write(d.join("scripts/gates/closed-before-375.txt"), b"\xff\n").unwrap();
    assert!(ask(&d, "python3", &["052-new"])
        .unwrap_err()
        .starts_with("UnicodeDecodeError"));
    sh(&d, "chmod 000 scripts/gates/closed-before-375.txt");
    let unreadable = ask(&d, "python3", &["052-new"]);
    sh(&d, "chmod 644 scripts/gates/closed-before-375.txt");
    assert!(unreadable.unwrap_err().starts_with("OSError"));
}

#[test]
fn what_the_python_raised_fails_after_the_directories_before_it_are_asked() {
    let d = dir("closing-raise");
    impl_check(&d, "open(sys.argv[2].rsplit('/specs/', 1)[0] + '/asked', 'w').write(' '.join(sys.argv[2:]))\nprint(json.dumps([[] for a in sys.argv[2:]]))");
    put(&d, "specs/200-a/report.md", "");
    // a number that is no number raises on the report's line, the first directory still put to the implementation check
    let got = ask(&d, "python3", &["200-a", "x-b", "201-c"]).unwrap_err();
    assert!(got.starts_with("ValueError: invalid literal"), "{got}");
    let asked = std::fs::read_to_string(d.join("asked")).unwrap_or_default();
    assert!(asked.ends_with("specs/200-a"), "{asked}");
    // a carry read that fails after the report's line
    std::fs::create_dir_all(d.join("specs/300-s/spec.md")).unwrap();
    assert!(ask(&d, "python3", &["200-a"])
        .unwrap_err()
        .starts_with("OSError"));
}

#[test]
fn the_implementation_check_failing_fails_the_closing_check() {
    let d = dir("closing-impl");
    put(&d, "specs/200-a/report.md", "");
    impl_check(&d, "raise SystemExit(3)");
    assert!(ask(&d, "python3", &["200-a"])
        .unwrap_err()
        .contains("exited 3"));
    // what it said on stderr is captured and carried in the error, its traceback first (the coordinator's ruling on T127)
    impl_check(&d, "raise ValueError('the claims door is shut')");
    let raised = ask(&d, "python3", &["200-a"]).unwrap_err();
    assert!(raised.starts_with("Traceback (most recent call last):\n"));
    assert!(raised.contains("ValueError: the claims door is shut\nimpl_check.missing raised"));
    // a warning on success is handed back beside the answer, for the caller to place
    impl_check(
        &d,
        "sys.stderr.write('a warning\\n')\nprint(json.dumps([[] for a in sys.argv[2:]]))",
    );
    let tools = Tools {
        tree: &d,
        python: "python3",
    };
    let found = reasons(&tools, &d.join("specs"), &[d.join("specs/200-a")]).unwrap();
    assert_eq!(
        (found.each, found.said.as_str()),
        (vec![vec![]], "a warning\n")
    );
    // a later directory's raise: what impl_check said for the earlier ones comes first
    put(&d, "specs/x-b/x", "");
    let raised = reasons(
        &tools,
        &d.join("specs"),
        &[d.join("specs/200-a"), d.join("specs/x-b")],
    )
    .err()
    .unwrap_or_default();
    assert!(raised.starts_with("a warning\nValueError: invalid literal"));
    impl_check(&d, "print('not json')");
    assert!(ask(&d, "python3", &["200-a"])
        .unwrap_err()
        .starts_with("impl_check.py --missing-json:"));
    impl_check(&d, "print('[]')");
    assert!(ask(&d, "python3", &["200-a"])
        .unwrap_err()
        .contains("0 answers for 1"));
    assert!(ask(&d, "/no/such/python", &["200-a"])
        .unwrap_err()
        .starts_with("OSError"));
}

#[test]
fn an_open_tooling_fix_holds_the_feature_until_settled() {
    let d = dir("closing-fixes");
    impl_check(&d, "print(json.dumps([[] for a in sys.argv[2:]]))");
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
    let got = ask(&d, "python3", &["200-a"]).unwrap();
    assert_eq!(got[0].len(), 1);
    assert!(
        got[0][0].starts_with("the round arbiter's tooling fix is open")
            && got[0][0].contains("    t1: newer\n    3: [\"a\"]\n")
            && got[0][0].contains("make arbiter-fix-declined")
    );
}
