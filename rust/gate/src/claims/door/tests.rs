//! Each verb of the door Python's callers reach the claims tools through.

use serde_json::{json, Value};

use super::serve;
use crate::claims::tests::{fixture, py_units};
use crate::record::testkit::put;

fn ask(lines: &[Value]) -> Vec<Value> {
    let input: String = lines.iter().map(|l| format!("{l}\n\n")).collect();
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
        json!({"verb": "backfill_sections", "args": [r, {}, {}]}),
        json!({"verb": "scope_split", "args": [r, "  DRIFTED        l7r/diagram/m.py::read#x - y\n", ["l7r/diagram/m.py"], ["l7r/diagram/m.py"]]}),
        json!({"verb": "git_diff", "args": [r, "l7r/diagram/s.py"]}),
        json!({"verb": "file_left", "args": [r, "T1", []]}),
        json!({"verb": "flight_live", "args": [r]}),
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
    assert_eq!(got[4]["ok"], json!([0, {}, {}]));
    assert_eq!(
        got[5]["ok"][0],
        json!(["DRIFTED        l7r/diagram/m.py::read#x - y"])
    );
    assert_eq!(got[6]["ok"], "");
    assert_eq!(got[7]["ok"], 0);
    assert_eq!(got[8]["ok"], json!([]));
    assert_eq!(got[9]["ok"]["QUESTIONS"], "research/questions");
    assert!(got[10]["error"].as_str().unwrap().contains("no verb nope"));
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
