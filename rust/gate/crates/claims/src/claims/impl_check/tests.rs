//! The implementation check on a scratch repository: its fixture's claims cite question 0001's findings page through a Rust unit and a
//! procedure section (feature 449 T132; every form the Python had, each raise it raised).

use std::path::Path;

use serde_json::{json, Value};

use super::{cli, missing_each, py_int, shown};
use crate::claims::tests::{fixture, record_all};
use crate::record::testkit::{commit, put};

const SPEC: &str = "# x\n\n**Affects**: hamlet, Research Record\n";

fn ask(root: &Path, args: &[&str]) -> crate::Reply {
    cli(
        &args.iter().map(|a| (*a).to_owned()).collect::<Vec<_>>(),
        root,
    )
}

/// A feature `NNN-x` tagged `research record`, its commit changing question 0001's findings page under `subject`.
fn feature(root: &Path, n: &str, subject: &str) -> std::path::PathBuf {
    put(root, &format!("specs/{n}-x/spec.md"), SPEC);
    commit(root, "the spec");
    let page = format!("research/{}/0001-gap.html", "questions");
    let body = std::fs::read_to_string(root.join(&page)).unwrap();
    put(root, &page, &format!("{body}<p>More.</p>\n"));
    commit(root, subject);
    root.join(format!("specs/{n}-x"))
}

#[test]
fn a_research_feature_owes_each_question_its_claims_or_its_line() {
    let root = fixture("impl-check");
    let d = feature(&root, "500", "Feature 500: the gap");
    let r = root.to_string_lossy().into_owned();
    // every claim citing 0001 is new to the index, so owed its check
    let got = ask(&root, &["500"]);
    assert_eq!(got.code, 1, "{}{}", got.stdout, got.stderr);
    assert!(got.stdout.starts_with(
        "impl-check: 500-x changed 1 question(s): 0001\n  0001: 3 claim(s) cite it, 3 owed the check\n      -              "
    ));
    assert!(got.stdout.ends_with("  (owed)\nimpl-check: 1 missing\n"));
    // the closing check's question, in process and in command form, prefixed with the feature
    let each = missing_each(&[&d, &root.join("specs/500-x")]).unwrap();
    assert_eq!(each.len(), 2);
    assert!(each[0][0]
        .starts_with("500-x owes its implementation check (feature 378): 0001: 3 claim(s)"));
    let json_form = ask(&root, &["--missing-json", &d.to_string_lossy()]);
    assert_eq!(
        serde_json::from_str::<Value>(&json_form.stdout).unwrap(),
        json!(each[..1])
    );
    assert_eq!(ask(&root, &["--missing-json"]).stdout, "[]\n");
    // each claim recorded IN-STEP: nothing owed, its verdict shown
    record_all(&root);
    let done = ask(&root, &[&d.to_string_lossy()]);
    assert_eq!(done.code, 0, "{}{}", done.stdout, done.stderr);
    assert!(done.stdout.contains("\n      IN-STEP        "));
    assert!(done.stdout.ends_with("impl-check: nothing missing\n"));
    // an index row with no verdict is shown as none
    put(&root, "dev/claims-index.json", "{\"x\": {}}\n");
    assert_eq!(ask(&root, &["500"]).code, 1);
    // an index row that is no object raises, as `v.get` did
    put(&root, "dev/claims-index.json", "{\"a\": 3}\n");
    let bad = ask(&root, &["500"]);
    assert_eq!((bad.code, bad.stdout.as_str()), (1, ""));
    assert!(bad.stderr.contains("AttributeError: 'int' object"));
    // a broken index raises too, and so does the closing check's question
    put(&root, "dev/claims-index.json", "{");
    assert!(ask(&root, &["500"]).stderr.contains("JSONDecodeError"));
    assert!(missing_each(&[&d]).is_err());
    let raised = ask(&root, &["--missing-json", &d.to_string_lossy()]);
    assert_eq!((raised.code, raised.stdout.as_str()), (1, ""));
    // a directory with no feature in it owes nothing
    assert_eq!(ask(&root, &["--missing-json", &r]).stdout, "[[]]\n");
}

#[test]
fn a_question_no_code_decides_is_closed_by_its_searched_line() {
    let root = fixture("impl-check-none");
    // a subject in the `NNN:` form with leading zeros, the claims citing 0001 moved to another page so none cites it
    let d = feature(&root, "501", "0501: the gap");
    for rel in ["rust/phases/src/lib.rs", "docs/buildings.md"] {
        let text = std::fs::read_to_string(root.join(rel)).unwrap();
        put(&root, rel, &text.replace("0001-gap", "0002-other"));
    }
    let got = ask(&root, &["501"]);
    assert_eq!(got.code, 1);
    assert!(got
        .stdout
        .contains("  0001: no claim cites it, and implementation-check.md has no line for it\n"));
    put(
        &root,
        "specs/501-x/implementation-check.md",
        "- 0001: no code implements it - not built\r\n",
    );
    let said = ask(&root, &["501"]);
    assert!(said.stdout.contains(
        "  0001: no code implements it - not built  (says nothing of what was searched)\n"
    ));
    assert_eq!(said.code, 1);
    put(
        &root,
        "specs/501-x/implementation-check.md",
        "- 0001: no code implements it - not built\n- 0001: no code implements it - not built; searched: the grep\n",
    );
    let ok = ask(&root, &[&d.to_string_lossy()]);
    assert_eq!(ok.code, 0, "{}{}", ok.stdout, ok.stderr);
    assert!(ok
        .stdout
        .contains("  0001: no code implements it - not built; searched: the grep\n"));
}

#[test]
fn what_owes_nothing_and_what_cannot_be_read() {
    let root = fixture("impl-check-forms");
    // with no argument, the Python's usage line
    let usage = ask(&root, &[]);
    assert_eq!((usage.code, usage.stdout.as_str()), (2, ""));
    assert!(usage.stderr.starts_with("impl_check.py <feature dir>"));
    // a number no directory has is the word as a path: untagged
    assert_eq!(
        ask(&root, &["777"]).stdout,
        "impl-check: 777 is not tagged `research record` - nothing is owed\n"
    );
    assert_eq!(ask(&root, &["-5"]).code, 0);
    assert_eq!(
        ask(&root, &[""]).stdout,
        "impl-check:  is not tagged `research record` - nothing is owed\n"
    );
    // a word that is no number and no directory raises
    let bad = ask(&root, &["nope"]);
    assert_eq!((bad.code, bad.stdout.as_str()), (1, ""));
    assert!(bad.stderr.contains("invalid literal for int()"));
    // a spec with no `**Affects**` line is untagged
    put(&root, "specs/503-x/spec.md", "# x\n");
    assert!(ask(&root, &["503"]).stdout.contains("503-x is not tagged"));
    // a tagged feature whose commits changed no findings page owes nothing
    put(&root, "specs/502-x/spec.md", SPEC);
    commit(&root, "502: a spec only");
    assert_eq!(
        ask(&root, &["502"]).stdout,
        "impl-check: 502-x's commits changed no question's findings - nothing is owed\n"
    );
    // a tagged directory whose name is no number raises
    put(&root, "specs/abc-x/spec.md", SPEC);
    assert!(ask(&root, &[&root.join("specs/abc-x").to_string_lossy()])
        .stderr
        .contains("ValueError"));
    // a path with no grandparent
    assert_eq!(
        missing_each(&[Path::new("/")]),
        Err("IndexError: 1".to_owned())
    );
}

#[test]
fn a_verdict_is_printed_as_the_python_formatted_it() {
    let shows = |v: Value| shown(&v);
    assert_eq!(shows(json!("DRIFTED")), Ok("DRIFTED".to_owned()));
    for falsy in [
        json!(""),
        json!(null),
        json!(false),
        json!(0),
        json!([]),
        json!({}),
    ] {
        assert_eq!(shows(falsy), Ok("-".to_owned()));
    }
    assert_eq!(shows(json!(true)), Ok("1".to_owned()));
    assert_eq!(shows(json!(2.5)), Ok("2.5".to_owned()));
    assert!(shows(json!([1])).unwrap_err().contains("list"));
    assert!(shows(json!({"a": 1})).unwrap_err().contains("dict"));
    assert_eq!(py_int(" +1_2 "), Ok(12));
    assert!(py_int("1__2").is_err());
    assert!(py_int("_1").is_err());
    assert!(py_int("99999999999999999999999999999999999999999").is_err());
    assert_eq!(
        [json!(null), json!(1.5), json!("s"), json!([]), json!({})]
            .iter()
            .map(super::py_type)
            .collect::<Vec<_>>(),
        ["'NoneType'", "'float'", "'str'", "'list'", "'dict'"]
    );
    assert_eq!(super::py_type(&json!(true)), "'bool'");
}
