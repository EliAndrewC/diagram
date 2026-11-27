//! The repairs' writer (feature 461 T15): data-model.md's line, the ids counting up, an entry filed once.

use l7r_gate_core::ci::fixtures::scratch;

use super::{file, path, read, Entry};

fn entry(batch: &str, ejected: &[&str]) -> Entry {
    Entry {
        feature: "461-landing-lane".to_owned(),
        tasks: vec!["T13".to_owned()],
        kind: "fix".to_owned(),
        ejected: ejected.iter().map(|s| (*s).to_owned()).collect(),
        batch: batch.to_owned(),
        why: "red".to_owned(),
        units: vec!["rust/gate/crates/land test".to_owned()],
        attempt: "/c/l7r-lane/attempts/461-7-2.log".to_owned(),
    }
}

#[test]
fn an_entry_is_data_model_s_line_its_id_one_past_the_highest_and_the_same_changes_filed_once() {
    let dir = scratch("lane-repairs");
    let common = dir.path();
    assert_eq!(
        file(common, "2026-11-28T03:12:09Z", &entry("461-7", &["aaa"])),
        Ok("r1".to_owned())
    );
    let lines = read(common);
    assert_eq!(
        lines[0],
        serde_json::json!({"utc": "2026-11-28T03:12:09Z", "repair": "r1", "feature": "461-landing-lane", "tasks": ["T13"],
            "kind": "fix", "ejected": ["aaa"], "batch": "461-7", "why": "red", "units": ["rust/gate/crates/land test"],
            "attempt": "/c/l7r-lane/attempts/461-7-2.log"})
    );
    // the same batch's entry for the same changes, in any order: its id, nothing written
    assert_eq!(
        file(common, "t", &entry("461-7", &["aaa"])),
        Ok("r1".to_owned())
    );
    // another batch, another set: new ids; an id the writer did not form is passed over in the count
    std::fs::write(
        path(common),
        format!(
            "{}{}\n",
            std::fs::read_to_string(path(common)).unwrap(),
            r#"{"repair": "x9"}"#
        ),
    )
    .unwrap();
    assert_eq!(
        file(common, "t", &entry("461-8", &["aaa"])),
        Ok("r2".to_owned())
    );
    assert_eq!(
        file(common, "t", &entry("461-7", &["bbb", "aaa"])),
        Ok("r3".to_owned())
    );
    assert_eq!(
        file(common, "t", &entry("461-7", &["aaa", "bbb"])),
        Ok("r3".to_owned())
    );
    assert_eq!(read(common).len(), 4);
}

#[test]
fn a_file_that_cannot_be_written_is_an_error_naming_it() {
    let dir = scratch("lane-repairs-err");
    std::fs::write(dir.path().join("l7r-lane"), "").unwrap();
    let err = file(dir.path(), "t", &entry("461-7", &["aaa"])).unwrap_err();
    assert!(err.contains("l7r-lane/repairs.jsonl"), "{err}");
}
