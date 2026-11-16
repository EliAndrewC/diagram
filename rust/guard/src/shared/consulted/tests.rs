//! The sources-consulted ledger (feature 449 T145; each expected value `sources.py`'s on the same input, 2026-11-16).

use std::os::unix::fs::PermissionsExt as _;
use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{
    append, by_key, check, context, earlier, get, home, line, locked, norm, now, read, read_lines,
    repo_root, show, text, unquote, valid_outcome, VARS,
};
use crate::shared::tempdir::TempDir;

const LIST: &str = r#"{"domains": [{"domain": "bad.example", "reason": "machine text", "approved": {"date": "2026-10-02", "words": "block it"}}]}"#;

fn set(name: &str, value: &str) {
    VARS.with(|v| v.borrow_mut().insert(name.to_owned(), value.to_owned()));
}

fn clear() {
    VARS.with(|v| v.borrow_mut().clear());
}

/// A scratch record holding the blocked list.
fn record(d: &Path) -> PathBuf {
    let r = d.join("research");
    std::fs::create_dir_all(&r).unwrap();
    std::fs::write(r.join("blocked-domains.json"), LIST).unwrap();
    r
}

#[test]
fn a_url_is_normalized_as_the_measurement_did() {
    assert_eq!(unquote("plain"), "plain");
    assert_eq!(unquote("a%20b%zz%E6%9D%B1é%"), "a b%zz東é%");
    assert_eq!(unquote("%ff%41"), "\u{fffd}A");
    assert_eq!(norm(" <https://www.Example.org/A/#x>. "), "example.org/a");
    assert_eq!(
        norm("http://ja.m.wikipedia.org/wiki/East_Asia/"),
        "ja.wikipedia.org/wiki/East_Asia"
    );
    assert_eq!(norm("https://m.Wikipedia.org"), "wikipedia.org");
    assert_eq!(norm("https://EN.wikipedia.org"), "en.wikipedia.org");
    assert_eq!(
        norm("https://EN.wikipedia.ORG/wiki/%E6%9D%B1"),
        "en.wikipedia.org/wiki/東"
    );
}

#[test]
fn the_ledger_lives_under_the_mirror() {
    clear();
    let d = TempDir::new("consulted-home");
    std::fs::create_dir_all(d.join("m/.clones/c/.git")).unwrap();
    std::fs::create_dir_all(d.join("m/.clones/c/sub")).unwrap();
    let root = repo_root(Some(&d.join("m/.clones/c/sub")));
    assert!(root.ends_with("m/.clones/c"));
    assert_eq!(
        home(&root),
        root.parent().unwrap().parent().unwrap().join(".specify")
    );
    assert_eq!(home(Path::new("/x/y")), Path::new("/x/y/.specify"));
    assert_eq!(repo_root(Some(Path::new("/"))), Path::new("/"));
    assert!(repo_root(None).is_absolute());
    set("L7R_SOURCES_HOME", "/elsewhere");
    assert_eq!(home(&root), Path::new("/elsewhere"));
    clear();
}

#[test]
fn a_line_carries_its_context() {
    clear();
    let d = TempDir::new("consulted-ctx");
    let root = d.join("clone-x");
    std::fs::create_dir_all(root.join(".specify")).unwrap();
    let got = |root: &Path| context(root).map(Value::Object);
    assert_eq!(
        got(&root).unwrap(),
        json!({"feature": "", "clone": "clone-x", "session": ""})
    );
    let pointer = root.join(".specify/feature.json");
    std::fs::write(&pointer, r#"{"feature_directory": "specs/312-uncited"}"#).unwrap();
    set("CLAUDE_CODE_SESSION_ID", "abc");
    assert_eq!(got(&root).unwrap()["feature"], "312");
    assert_eq!(got(&root).unwrap()["session"], "abc");
    set("L7R_PAGE_SESSION", "page");
    assert_eq!(got(&root).unwrap()["session"], "page");
    std::fs::write(&pointer, "{").unwrap();
    assert_eq!(got(&root).unwrap()["feature"], "");
    std::fs::write(&pointer, "{}").unwrap();
    assert_eq!(got(&root).unwrap()["feature"], "");
    std::fs::write(&pointer, "[1]").unwrap();
    assert_eq!(got(&root).unwrap_err().kind, "AttributeError");
    std::fs::write(&pointer, r#"{"feature_directory": 5}"#).unwrap();
    assert_eq!(got(&root).unwrap_err().kind, "TypeError");
    std::fs::write(&pointer, b"\xff").unwrap();
    assert_eq!(got(&root).unwrap_err().kind, "UnicodeDecodeError");
    std::fs::write(&pointer, "{}").unwrap();
    std::fs::set_permissions(&pointer, std::fs::Permissions::from_mode(0o000)).unwrap();
    assert_eq!(got(&root).unwrap_err().kind, "OSError");
    std::fs::set_permissions(&pointer, std::fs::Permissions::from_mode(0o644)).unwrap();
    set("SPECIFY_FEATURE", "288-sources");
    assert_eq!(got(&root).unwrap()["feature"], "288");
    clear();
}

#[test]
fn the_lock_is_taken_or_refused() {
    let d = TempDir::new("consulted-lock");
    let held = locked(&d, 1.0).unwrap();
    let late = locked(&d, 0.05).unwrap_err();
    assert_eq!(late.kind, "TimeoutError");
    assert_eq!(
        late.message,
        format!(
            "could not take {} within 0.05s",
            d.join("sources-consulted.lock").display()
        )
    );
    drop(held);
    drop(locked(&d, f64::NAN).unwrap());
    std::fs::write(d.join("file"), "").unwrap();
    assert_eq!(
        locked(&d.join("file/sub"), 1.0).unwrap_err().kind,
        "OSError"
    );
}

#[test]
fn the_ledger_is_appended_and_read() {
    clear();
    let d = TempDir::new("consulted-append");
    let rec = record(&d);
    assert!(append(&d, &[], &rec).is_ok());
    let ctx = context(&d).unwrap();
    let row = line(&ctx, "https://www.a.org/p", "pending", &["0012".to_owned()]);
    assert_eq!(
        row.as_object().unwrap().keys().collect::<Vec<_>>(),
        [
            "url",
            "raw",
            "utc",
            "feature",
            "clone",
            "session",
            "questions",
            "outcome"
        ]
    );
    append(&d, &[row.clone()], &rec).unwrap();
    let blocked = line(&ctx, "https://bad.example/x", "pending", &[]);
    let refused = append(&d, &[blocked], &rec).unwrap_err();
    assert_eq!(refused.kind, "Blocked");
    assert!(refused
        .message
        .starts_with("a sources-consulted ledger line refused: https://bad.example/x"));
    assert!(append(&d, &[json!({"raw": "", "url": "bad.example/y"})], &rec).is_err());
    assert_eq!(
        append(&d, &[json!(3)], &rec).unwrap_err().kind,
        "AttributeError"
    );
    assert!(check("https://a.org", "x", &rec).is_ok());
    std::fs::write(d.join("sources-consulted.jsonl"), b"").unwrap();
    std::fs::create_dir_all(d.join("dir/sources-consulted.jsonl")).unwrap();
    assert_eq!(
        append(&d.join("dir"), &[row], &rec).unwrap_err().kind,
        "OSError"
    );
    std::fs::write(
        d.join("sources-consulted.jsonl"),
        "{\"url\": \"a.org/p\"}\nnot json\n5\n",
    )
    .unwrap();
    assert_eq!(read(&d).unwrap(), vec![json!({"url": "a.org/p"}), json!(5)]);
    assert!(read(&d.join("none")).unwrap().is_empty());
    std::fs::write(d.join("bad.jsonl"), b"\xff\n").unwrap();
    assert_eq!(
        read_lines(&d.join("bad.jsonl")).unwrap_err().kind,
        "UnicodeDecodeError"
    );
    std::fs::set_permissions(d.join("bad.jsonl"), std::fs::Permissions::from_mode(0o000)).unwrap();
    assert_eq!(
        read_lines(&d.join("bad.jsonl")).unwrap_err().kind,
        "OSError"
    );
    assert_eq!(
        earlier(&d, "http://a.org/p/").unwrap_err().kind,
        "AttributeError"
    );
    std::fs::write(d.join("sources-consulted.jsonl"), "{\"url\": \"a.org/p\", \"outcome\": \"cited:k-1\"}\n{\"url\": \"b\", \"outcome\": \"pending\"}\n").unwrap();
    assert_eq!(earlier(&d, "http://a.org/p/").unwrap().len(), 1);
    assert_eq!(by_key(&d, "^k-").unwrap().len(), 1);
    assert!(by_key(&d, "^z").unwrap().is_empty());
    assert_eq!(by_key(&d, "(").unwrap_err().kind, "PatternError");
    std::fs::write(d.join("sources-consulted.jsonl"), "[]\n").unwrap();
    assert_eq!(by_key(&d, "x").unwrap_err().kind, "AttributeError");
}

#[test]
fn an_outcome_is_one_of_the_five() {
    for good in [
        "cited:a-1",
        " pending ",
        "rejected: off topic",
        "nothing-found",
        "unreadable",
    ] {
        assert!(valid_outcome(good), "{good}");
    }
    for bad in ["cited:A", "rejected:", "rejected:  ", "found", "pendingx"] {
        assert!(!valid_outcome(bad), "{bad}");
    }
    let t = now();
    assert!(t.ends_with("+00:00") && t.len() == 25);
}

#[test]
fn a_line_is_shown_as_its_reader_wants_it() {
    let row = json!({"utc": "2026-10-02T12:00:00+00:00", "feature": "312", "clone": "c", "session": "0123456789", "reads": 3,
                     "outcome": "pending", "questions": ["0012", "0013"]});
    assert_eq!(
        show(&row).unwrap(),
        "  2026-10-02  f312 c s:01234567 x3  pending  q: 0012; 0013"
    );
    assert_eq!(show(&json!({})).unwrap(), "    -  ");
    assert_eq!(
        show(&json!({"questions": "ab", "reads": true})).unwrap(),
        "    -    q: a; b"
    );
    let long = "q".repeat(300);
    assert_eq!(show(&json!({"questions": [long]})).unwrap().len(), 252);
    for (bad, kind) in [
        (json!(1), "AttributeError"),
        (json!({"clone": 5}), "TypeError"),
        (json!({"session": 5}), "TypeError"),
        (json!({"reads": "2"}), "TypeError"),
        (json!({"questions": [1]}), "TypeError"),
        (json!({"questions": 3}), "TypeError"),
        (json!({"utc": 3}), "TypeError"),
    ] {
        assert_eq!(show(&bad).unwrap_err().kind, kind, "{bad}");
    }
    assert_eq!(get(&json!({"a": 1}), "a").unwrap(), Some(&json!(1)));
    assert_eq!(text(&json!("s"), "x").unwrap(), "s");
}
