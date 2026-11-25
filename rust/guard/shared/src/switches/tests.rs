//! The research switch's reader on each shape of the file (451 T244).

use serde_json::json;

use super::{research, research_of, FILE};

#[test]
fn a_thrown_entry_reads_with_its_reason() {
    let r = research_of(Some(
        &json!({"research": {"state": "deferred", "why": "the GM", "who": "E", "utc": "t"}}),
    ));
    assert!(r.deferred());
    assert_eq!(
        (r.why.as_str(), r.who.as_str(), r.utc.as_str()),
        ("the GM", "E", "t")
    );
    assert!(!research_of(Some(&json!({"research": {"state": "open"}}))).deferred());
}

#[test]
fn missing_and_malformed_read_open() {
    let none = research_of(Some(&json!({"claims": {"state": "report"}})));
    assert_eq!((none.state.as_str(), none.why.as_str()), ("open", ""));
    for bad in [
        json!({"research": {"state": "later"}}),
        json!({"research": "deferred"}),
    ] {
        let r = research_of(Some(&bad));
        assert!(!r.deferred());
        assert!(r.why.contains("MALFORMED"), "{}", r.why);
    }
    assert!(research_of(Some(&json!([]))).why.contains("MALFORMED"));
    assert!(research_of(None).why.contains("MALFORMED"));
}

#[test]
fn read_from_a_tree() {
    let dir = crate::tempdir::TempDir::new("switches");
    assert_eq!(research(dir.path()).state, "open");
    std::fs::create_dir_all(dir.path().join("dev")).unwrap();
    std::fs::write(dir.path().join(FILE), "not json").unwrap();
    assert!(research(dir.path()).why.contains("MALFORMED"));
    std::fs::write(
        dir.path().join(FILE),
        r#"{"research": {"state": "deferred"}}"#,
    )
    .unwrap();
    assert!(research(dir.path()).deferred());
}
