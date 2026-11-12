//! The command line and the Python readings it keeps (`float()`, `int()`, a verdict's word, a figure's format), on a scratch table
//! (feature 449 T134; the rules themselves are `rules/tests.rs`).
#![expect(
    clippy::float_cmp,
    reason = "figures Python computes exactly, compared as it compares them"
)]

use std::path::Path;

use l7r_gate_core::checks::scratch;
use serde_json::json;

use super::{as_float, cli, fixed, py_float_text, py_int_of, py_int_text, py_repr, verdict_of};

pub(super) const TABLE: &str = r#"{
 "program": {"ops_at_40": 100, "exponent": 0.5},
 "stages": {
  "web": {"status": "budgeted", "per_thing": 10.0, "exponent": 0.1, "derivation": "specs/x/phases/web.derivation.md", "verdict": "specs/x/phases/web.verdict-1.txt", "items_at_20": 10, "items_at_40": 10, "items_at_80": 10, "pinned_on": "accept", "derivation_sha": "x", "rounds": 2, "spread": "1-2 at 40"},
  "seat": {"status": "unbudgeted"},
  "field": {"status": "accepted", "per_thing": 1.0, "exponent": 0.0, "derivation": "specs/x/phases/field.derivation.md", "verdict": "v", "items_at_20": 100, "items_at_40": 100, "items_at_80": 100, "accepted": {"40": 90, "80": 90}},
  "field.polder": {"status": "budgeted", "per_thing": 1.0, "exponent": 0.0, "derivation": "specs/x/phases/polder.derivation.md", "verdict": "v", "items_at_10": 5, "items_at_20": 5, "sizes": [10, 20]}
 }
}"#;

pub(super) const DERIVATION: &str = "# d\n\n## Totals\n- at 20: 1 = 1\n";

pub(super) fn put(root: &Path, rel: &str, data: &[u8]) {
    let p = root.join(rel);
    std::fs::create_dir_all(p.parent().unwrap()).unwrap();
    std::fs::write(p, data).unwrap();
}

/// A table, a log, two derivations and their verdicts, a run.
pub(super) fn tree(root: &Path) {
    put(root, "dev/work-budget.json", TABLE.as_bytes());
    put(root, "dev/work-budget-changes.jsonl", b"{\"old\": 1}\n");
    put(
        root,
        "specs/x/phases/web.derivation.md",
        DERIVATION.as_bytes(),
    );
    put(
        root,
        "specs/x/phases/seat.derivation.md",
        DERIVATION.as_bytes(),
    );
    put(
        root,
        "specs/x/phases/polder.derivation.md",
        b"a bounded n: households 10-20\n",
    );
    put(root, "specs/x/phases/seat.verdict-1.txt", b"SOUND - fine\n");
    put(root, "specs/x/phases/web.verdict-1.txt", b"SOUND\n");
    put(root, "specs/x/phases/loose.txt", b"LOOSE\n");
    put(
        root,
        "dev/work-budget/20261101T000000Z-a.json",
        br#"{"summary": {"stages": {"seat": {"per": {"40": {"ops": 50}}}}}}"#,
    );
}

pub(super) fn run(root: &Path, args: &[&str]) -> crate::Reply {
    let mut all = vec!["--root".to_owned(), root.to_string_lossy().into_owned()];
    all.extend(args.iter().map(|a| (*a).to_owned()));
    cli(&all, Path::new("/nowhere"))
}

pub(super) fn table(root: &Path) -> serde_json::Value {
    serde_json::from_str(&std::fs::read_to_string(root.join("dev/work-budget.json")).unwrap())
        .unwrap()
}

#[test]
fn pythons_numbers_are_read_as_python_reads_them() {
    for (text, want) in [
        (" 7 ", Some(7.0)),
        ("1_0", Some(10.0)),
        ("+2.5", Some(2.5)),
        ("1.", Some(1.0)),
        (".5", Some(0.5)),
        ("1e3", Some(1000.0)),
        ("", None),
        ("abc", None),
        ("1__0", None),
        ("_1", None),
        ("1_", None),
    ] {
        assert_eq!(py_float_text(text), want, "{text:?}");
    }
    for (text, want) in [
        (" 5", Some(5)),
        ("+5", Some(5)),
        ("-1", Some(-1)),
        ("5_0", Some(50)),
        ("1.0", None),
        ("x5", None),
        ("", None),
        ("-", None),
    ] {
        assert_eq!(py_int_text(text), want, "{text:?}");
    }
    assert_eq!(as_float(Some(&json!(2))).unwrap(), 2.0);
    assert_eq!(as_float(Some(&json!(true))).unwrap(), 1.0);
    assert_eq!(as_float(Some(&json!("3"))).unwrap(), 3.0);
    assert!(as_float(Some(&json!("x"))).is_err());
    assert!(as_float(Some(&json!([1]))).is_err());
    assert!(as_float(None).is_err());
    let big: serde_json::Value = serde_json::from_str("1e300").unwrap();
    assert_eq!(as_float(Some(&big)).unwrap(), 1e300);
    for (v, want) in [
        (json!(10), Ok(10)),
        (json!(10.7), Ok(10)),
        (json!("20"), Ok(20)),
        (json!(true), Ok(1)),
    ] {
        assert_eq!(py_int_of(&v), want);
    }
    assert!(py_int_of(&json!("x")).is_err());
    assert!(py_int_of(&json!(null)).is_err());
    assert!(py_int_of(&json!(f64::MAX)).is_ok());
}

#[test]
fn figures_are_formatted_as_python_formats_them() {
    assert_eq!(fixed(1_234_567.5, 0, true), "1,234,568");
    assert_eq!(fixed(2.5, 0, true), "2");
    assert_eq!(fixed(-1234.4, 0, true), "-1,234");
    assert_eq!(fixed(0.125, 2, false), "0.12");
    assert_eq!(fixed(1234.25, 1, true), "1,234.2");
    assert_eq!(fixed(f64::NAN, 2, false), "nan");
    assert_eq!(fixed(f64::INFINITY, 0, true), "inf");
}

#[test]
fn a_verdicts_word_is_its_first_lines_first_word() {
    let d = scratch("bc-verdict");
    for (text, want) in [
        ("**sound**: yes\n", "SOUND"),
        ("\r\n\nLOOSE - x\r\n", "LOOSE"),
        ("", ""),
        ("  \n", ""),
        ("\x1cWITHIN\n", "WITHIN"),
        ("stra\u{df}e\n", "STRASSE"),
    ] {
        put(&d, "v.txt", text.as_bytes());
        assert_eq!(verdict_of(&d.join("v.txt")).unwrap(), want, "{text:?}");
    }
    assert_eq!(verdict_of(&d.join("none.txt")).unwrap(), "");
    // a directory is Python's OSError, read as no verdict
    assert_eq!(verdict_of(&d).unwrap(), "",);
    put(&d, "v.txt", b"\xff");
    // no UTF-8 is Python's UnicodeDecodeError, raised
    assert!(verdict_of(&d.join("v.txt")).is_err(),);
}

#[test]
fn the_command_line_is_argparses() {
    let d = scratch("bc-args");
    tree(&d);
    for args in [
        &[][..],
        &["nosuch"],
        &["set"],
        &["set", "a", "1", "1", "d"],
        &["set", "a", "1", "1", "d", "v", "extra"],
        &["change", "web", "x", "--words", "a b c"],
        &["change", "web", "1", "--exponent", "y", "--words", "a b c"],
        &["program", "1.5", "1", "--words", "w"],
        &["program", "10", "z", "--words", "w"],
        &["set", "web", "1", "1", "d", "v", "--items-at-20", "1.0"],
        &["set", "web", "1", "1", "d", "v", "--items-at", "5"],
        &["set", "web", "1", "1", "d", "v", "--lower=1"],
        &[
            "change",
            "web",
            "1",
            "--items-at-20",
            "x",
            "--words",
            "a b c",
        ],
        &["accept", "web"],
    ] {
        let got = run(&d, args);
        assert_eq!((got.code, got.stdout.as_str()), (2, ""),);
    }
    assert_eq!(cli(&["--root".to_owned()], Path::new(".")).code, 2);
    assert_eq!(
        cli(
            &["--rot=x".to_owned(), "program".to_owned()],
            Path::new(".")
        )
        .code,
        2
    );
    assert_eq!(
        cli(
            &["--bogus".to_owned(), "program".to_owned()],
            Path::new(".")
        )
        .code,
        2
    );
    // `--root=` and a prefix of it, as argparse takes them
    let prefixed = cli(
        &[
            format!("--ro={}", d.display()),
            "program".to_owned(),
            "5".to_owned(),
            "0.5".to_owned(),
            "--words".to_owned(),
            "the GM's words".to_owned(),
        ],
        Path::new("."),
    );
    assert_eq!(prefixed.stdout, "budget-program: the program's budget set to 5 operations at 40 households, exponent 0.5, logged in dev/work-budget-changes.jsonl\n");
    // a figure Python's float() refuses after argparse took it is its ValueError, the exit 1 of a traceback
    for pt in ["", "abc", "1e", "infx"] {
        let got = run(
            &d,
            &[
                "set",
                "seat",
                pt,
                "0.1",
                "specs/x/phases/seat.derivation.md",
                "specs/x/phases/seat.verdict-1.txt",
            ],
        );
        assert_eq!((got.code, got.stdout.as_str()), (1, ""), "{pt:?}");
    }
    let got = run(
        &d,
        &[
            "set",
            "seat",
            "1",
            "x",
            "specs/x/phases/seat.derivation.md",
            "specs/x/phases/seat.verdict-1.txt",
        ],
    );
    assert_eq!(got.code, 1);
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "one scenario's steps in the order each builds on the last"
)]
fn each_verb_reports_as_the_python_did() {
    let d = scratch("bc-verbs");
    tree(&d);
    let set = run(
        &d,
        &[
            "set",
            "seat",
            "2",
            "0.1",
            "specs/x/phases/seat.derivation.md",
            "specs/x/phases/seat.verdict-1.txt",
            "--items-at-20",
            "1",
            "--items-at-40",
            "2",
            "--items-at-80",
            "3",
        ],
    );
    assert_eq!(set.stdout, "budget-set: `seat` budgeted at 2 per thing, exponent 0.1\nbudget-set: the program at 40 households: 204 operations, 5 a household against the design's few thousand (4,000 at most, request.md)\n");
    let lowered = run(
        &d,
        &[
            "set",
            "seat",
            "1",
            "0.1",
            "specs/x/phases/seat.derivation.md",
            "specs/x/phases/seat.verdict-1.txt",
            "--lower",
            "--items-at-20",
            "1",
            "--items-at-40",
            "2",
            "--items-at-80",
            "3",
        ],
    );
    assert!(lowered
        .stdout
        .starts_with("budget-set: `seat` lowered to 1 per thing"),);
    let refused = run(
        &d,
        &[
            "set",
            "seat",
            "1",
            "0.1",
            "specs/x/phases/seat.derivation.md",
            "specs/x/phases/seat.verdict-1.txt",
            "--raise",
        ],
    );
    assert_eq!(refused.stderr, "budget-set: specs/x/phases/seat.derivation.md names no work its first derivation missed - a raise without the GM's words counts each item under `## Work the first derivation missed` (feature 444 FR-022); a figure that is only an estimate off is the leeway's, at acceptance\n");
    let changed = run(&d, &["change", "web", "12", "--words", "the GM's words"]);
    assert_eq!(changed.stdout, "budget-change: `web` changed to 12.0 per thing, logged in dev/work-budget-changes.jsonl with the GM's words\n");
    let no_words = run(&d, &["change", "web", "12", "--words", "  "]);
    assert_eq!(
        (no_words.code, no_words.stderr.as_str()),
        (
            1,
            "budget-change: no WORDS - a budget changes only with the GM's own words\n"
        )
    );
    put(&d, "audit.txt", b"WITHIN\n");
    let accepted = run(&d, &["accept", "seat", "audit.txt"]);
    assert_eq!(accepted.stderr, "budget-accept: `seat`: 50 counted operations at 40 households, 25.00 times its budget 2, past the leeway's 2 times - rebuild it again, raise the budget on a SOUND re-derivation naming the work it missed (`make budget-set RAISE=1`, FR-022), or with the GM's words (`make budget-change`, FR-006)\n");
    put(&d, "dev/work-budget/20261102T000000Z-b.json", br#"{"summary": {"stages": {"seat": {"per": {"20": {"ops": 1}, "40": {"ops": 2}, "80": {"ops": 3}}}}}}"#);
    let accepted = run(&d, &["accept", "seat", "audit.txt"]);
    assert_eq!(accepted.stdout, "budget-accept: `seat` accepted at its counted operations at 40 and 80 households, logged in dev/work-budget-changes.jsonl\n");
    assert_eq!(
        table(&d)["stages"]["seat"]["accepted"],
        json!({"40": 2.0, "80": 3.0})
    );
    let program = run(&d, &["program", " 1_000 ", " 2 ", "--words", "w w w"]);
    assert_eq!(program.stdout, "budget-program: the program's budget set to 1000 operations at 40 households, exponent 2.0, logged in dev/work-budget-changes.jsonl\n");
    let log = std::fs::read_to_string(d.join("dev/work-budget-changes.jsonl")).unwrap();
    assert_eq!(log.lines().count(), 5, "{log}");
    assert!(log.lines().last().unwrap().contains("\"what\": \"program\", \"from\": {\"ops_at_40\": 100, \"exponent\": 0.5}, \"to\": {\"ops_at_40\": 1000, \"exponent\": 2.0}, \"words\": \"w w w\"}"));
    // the table as the Python writes it: one-space indent, ASCII escapes, a trailing newline
    let text = std::fs::read_to_string(d.join("dev/work-budget.json")).unwrap();
    assert!(
        text.starts_with("{\n \"program\": {\n  \"ops_at_40\": 1000,\n  \"exponent\": 2.0\n },\n")
            && text.ends_with("}\n"),
    );
    {
        use std::os::unix::fs::PermissionsExt;
        std::fs::set_permissions(
            d.join("dev/work-budget.json"),
            std::fs::Permissions::from_mode(0o444),
        )
        .unwrap();
        let unwritable = run(&d, &["program", "1", "1", "--words", "w"]);
        assert!(
            unwritable.code == 1
                && unwritable
                    .stderr
                    .contains("work-budget.json: Permission denied"),
        );
    }
    std::fs::remove_file(d.join("dev/work-budget.json")).unwrap();
    assert_eq!(run(&d, &["program", "1", "1", "--words", "w"]).code, 1);
}

#[test]
fn a_non_finite_figure_is_taken_and_written_as_python_wrote_it() {
    for (text, want) in [
        ("inf", f64::INFINITY),
        ("-Infinity", f64::NEG_INFINITY),
        ("+INF", f64::INFINITY),
        ("1e999", f64::INFINITY),
    ] {
        assert_eq!(py_float_text(text), Some(want), "{text}");
    }
    assert!(py_float_text(" nan ").unwrap().is_nan());
    assert_eq!(py_repr(f64::INFINITY), "inf");
    assert_eq!(py_repr(f64::NEG_INFINITY), "-inf");
    assert_eq!(py_repr(f64::NAN), "nan");
    assert_eq!(py_repr(2.0), "2.0");
    let d = scratch("bc-nonfinite");
    tree(&d);
    let changed = run(
        &d,
        &[
            "change",
            "web",
            "inf",
            "--exponent",
            "nan",
            "--words",
            "the GM's words",
        ],
    );
    assert_eq!(changed.stdout, "budget-change: `web` changed to inf per thing, logged in dev/work-budget-changes.jsonl with the GM's words\n");
    let text = std::fs::read_to_string(d.join("dev/work-budget.json")).unwrap();
    assert!(text.contains("\"per_thing\": Infinity,\n   \"exponent\": NaN,"),);
    let log = std::fs::read_to_string(d.join("dev/work-budget-changes.jsonl")).unwrap();
    assert!(log.trim_end().ends_with(
        "\"to\": {\"per_thing\": Infinity, \"exponent\": NaN}, \"words\": \"the GM's words\"}"
    ),);
    // read back as Python's json read it: every verb goes on over it
    let program = run(&d, &["program", "1", "-0.5e999", "--words", "w w w"]);
    assert_eq!(program.code, 2,);
    let program = run(&d, &["program", "1", "1e999", "--words", "w w w"]);
    assert_eq!(program.stdout, "budget-program: the program's budget set to 1 operations at 40 households, exponent inf, logged in dev/work-budget-changes.jsonl\n");
    let set = run(
        &d,
        &[
            "set",
            "seat",
            "inf",
            "0.1",
            "specs/x/phases/seat.derivation.md",
            "specs/x/phases/seat.verdict-1.txt",
            "--items-at-20",
            "1",
            "--items-at-40",
            "2",
            "--items-at-80",
            "3",
            "--reason",
            "r",
        ],
    );
    assert_eq!(set.stdout, "budget-set: `seat` budgeted at inf per thing, exponent 0.1\nbudget-set: the program at 40 households: inf operations, inf a household against the design's few thousand (4,000 at most, request.md)\n");
    let text = std::fs::read_to_string(d.join("dev/work-budget.json")).unwrap();
    assert!(text.contains("\"program\": {\n  \"ops_at_40\": 1,\n  \"exponent\": Infinity\n }"),);
    let lowered = run(
        &d,
        &[
            "set",
            "web",
            "nan",
            "0.1",
            "specs/x/phases/web.derivation.md",
            "specs/x/phases/web.verdict-1.txt",
            "--lower",
            "--items-at-20",
            "1",
            "--items-at-40",
            "1",
            "--items-at-80",
            "1",
        ],
    );
    assert_eq!(lowered.code, 0,);
}
