//! Each verb of the door Python's callers reach the claims tools through.

use serde_json::{json, Value};

use super::serve;
use crate::claims::tests::{fixture, py_units};
use crate::record::testkit::put;

fn ask(lines: &[Value]) -> Vec<Value> {
    let input: String = lines.iter().fold(String::new(), |mut acc, l| {
        acc.push_str(&l.to_string());
        acc.push_str("\n\n");
        acc
    });
    let mut out = Vec::new();
    let done = serve(&mut input.as_bytes(), &mut out);
    assert_eq!(done.code, 0);
    String::from_utf8(out)
        .unwrap()
        .lines()
        .map(|l| serde_json::from_str(l).unwrap())
        .collect()
}

#[test]
fn each_verb_answers() {
    let root = fixture("claims-door");
    py_units(
        &root,
        &[],
        &[("helper", "function", &["help - GUESS: 3 households"], false)],
    );
    put(&root, "dev/claims-index.json", "{}\n");
    put(&root, "dev/claims-pages.json", "{\"x\": []}\n");
    put(&root, "l7r/diagram/s.py", "{\"own\": [1, 1]}\n");
    let r = root.to_string_lossy().into_owned();
    let got = ask(&[
        json!({"verb": "current", "args": [r]}),
        json!({"verb": "owed", "args": [r, {}, {}]}),
        json!({"verb": "load_index", "args": [root.join("dev/claims-index.json")]}),
        json!({"verb": "load_store", "args": [root.join("dev/claims-pages.json")]}),
        json!({"verb": "constants", "args": []}),
        json!({"verb": "nope", "args": [r]}),
    ]);
    let row = &got[0]["ok"]["l7r/diagram/m.py::helper#help"];
    assert_eq!(
        (
            row["claim"]["backing"].as_str(),
            row["unit"]["line_keyed"].as_bool()
        ),
        (Some("GUESS"), Some(false))
    );
    assert!(got[1]["ok"]
        .as_array()
        .unwrap()
        .iter()
        .any(|r| r[1] == "new"));
    assert_eq!(got[2]["ok"], json!({}));
    assert_eq!(got[3]["ok"], json!({"x": []}));
    assert_eq!(got[4]["ok"]["QUESTIONS"], "research/questions");
    assert!(got[4]["ok"].get("CLAIMS_FEATURE_DIR").is_none());
    assert!(got[5]["error"].as_str().unwrap().contains("no verb nope"));
    // the verbs that left with feature 449 T121: `land.py` and `replay_owing.py` asked them, and both are Rust
    let gone = ask(&[
        json!({"verb": "backfill_sections", "args": [r, {}, {}]}),
        json!({"verb": "git_diff", "args": [r, "l7r/diagram/s.py"]}),
        json!({"verb": "scope_split", "args": [r, "", [], []]}),
        json!({"verb": "file_left", "args": [r, "T1", []]}),
        json!({"verb": "flight_live", "args": [r]}),
    ]);
    // ...which the Rust land asks in process
    assert_eq!(
        crate::claims::scope_split(
            &root,
            "  DRIFTED        l7r/diagram/m.py::read#x - y\n",
            &["l7r/diagram/m.py".to_owned()],
            &["l7r/diagram/m.py".to_owned()]
        )
        .unwrap()
        .0,
        vec!["DRIFTED        l7r/diagram/m.py::read#x - y"]
    );
    assert_eq!(crate::claims::flight_live(&root), Ok(Vec::new()));
    assert!(gone.iter().all(|g| g["error"].is_string()));
    put(&root, "dev/claims-index.json", "{");
    let bad = ask(&[
        json!({"verb": "load_index", "args": [root.join("dev/claims-index.json")]}),
        json!({"verb": "owed", "args": [r, {}, {}]}),
    ]);
    assert!(bad[0]["error"].is_string());
    let mut closed = Closed;
    assert_eq!(
        serve(&mut "{\"verb\": \"constants\"}\n".as_bytes(), &mut closed).code,
        0
    );
    assert!(std::io::Write::flush(&mut closed).is_ok());
}

struct Closed;

impl std::io::Write for Closed {
    fn write(&mut self, _: &[u8]) -> std::io::Result<usize> {
        Err(std::io::Error::other("closed"))
    }

    fn flush(&mut self) -> std::io::Result<()> {
        Ok(())
    }
}

/// The replay's migration, asked in process since feature 449 T121 (`l7r-gate replay-owing`), as the door's `backfill_sections` answered.
#[test]
fn the_backfill_is_asked_in_process() {
    let root = fixture("claims-backfill-at");
    py_units(
        &root,
        &[],
        &[("helper", "function", &["help - GUESS: 3 households"], false)],
    );
    let (mut index, mut store) = (serde_json::Map::new(), serde_json::Map::new());
    assert_eq!(
        crate::claims::backfill_at(&root, &mut index, &mut store),
        Ok(0)
    );
}
