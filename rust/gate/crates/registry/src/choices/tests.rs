//! The title card's choices and their modals, as `choices.py` lists them (feature 449 T149; expected values the Python's).

use serde_json::{json, Map, Value};

use super::{applies, made, modal, modal_file, modal_key, not_choices, registry_for, table, TABLE};
use l7r_gate_core::checks::scratch;
use l7r_gate_core::record::testkit::put;

fn meta(v: &Value) -> Map<String, Value> {
    v.as_object().unwrap().clone()
}

const MODAL: &str = "About: a value.\nName: N\nCovers: c\nSources: not recorded\nEntry: research/questions/x.html\n";

#[test]
fn each_recorded_choice_is_listed_with_its_value_and_its_modal() {
    let root = scratch("registry-choices");
    assert_eq!(table(&root).unwrap_err().kind, "OSError");
    put(&root, TABLE, "{bad");
    assert_eq!(not_choices(&root).unwrap_err().kind, "JSONDecodeError");
    put(&root, TABLE, "{}");
    assert_eq!(table(&root).unwrap_err().kind, "KeyError");
    assert!(not_choices(&root).unwrap().is_empty());
    put(&root, TABLE, &json!({
        "not_choices": {"seed": "a roll, not a choice"},
        "choices": [
            {"key": "form", "name": "How", "values": {"row": "in a row"}},
            {"key": "row_side", "name": "Side", "when": "[form=row]", "values": {"one": "one side"}},
            {"key": "drift", "name": "Drift", "degree": true, "values": {"0": "square"}},
            {"key": "unset", "name": "Unset", "values": {}},
            {"key": "bad", "name": "Bad", "when": "[Bad=x]", "values": {}}
        ]
    }).to_string());
    assert_eq!(not_choices(&root).unwrap()["seed"], "a roll, not a choice");
    put(
        &root,
        "l7r/diagram/interactive/assets/modals/choice/form--row.md",
        MODAL,
    );
    put(
        &root,
        "l7r/diagram/interactive/assets/modals/choice/drift.md",
        MODAL,
    );
    let got = made(
        &root,
        &meta(&json!({"form": "row", "row_side": "two", "drift": -4, "unset": null})),
    )
    .unwrap();
    assert_eq!(
        got,
        [
            json!({"name": "How", "value": "in a row", "k": "choice:form=row"}),
            json!({"name": "Side", "value": "two", "k": ""}),
            json!({"name": "Drift", "value": "-4 degrees", "k": "choice:drift"}),
        ]
    );
    // a choice its settlement did not make is not listed
    assert_eq!(
        made(&root, &meta(&json!({"form": "dot", "row_side": "one"})))
            .unwrap()
            .len(),
        1
    );
    let reg = registry_for(&root, &meta(&json!({"form": "row", "drift": 0}))).unwrap();
    let keys: Vec<&str> = reg.iter().map(|f| f.key.as_str()).collect();
    assert_eq!(keys, ["choice:form=row", "choice:drift"]);
    assert!(made(&root, &meta(&json!({"bad": 1}))).is_err());
    assert!(registry_for(&root, &meta(&json!({"bad": 1}))).is_err());
    assert!(registry_for(&root, &meta(&json!({"row_side": 1})))
        .unwrap()
        .is_empty());
    let entries = table(&root).unwrap();
    assert!(
        applies(&entries[0], &Map::new()).unwrap() && !applies(&entries[1], &Map::new()).unwrap()
    );
    assert_eq!(modal_key(&entries[2], "5"), "choice:drift");
    assert!(modal_file(&root, &entries[0], "x").ends_with("modals/choice/form--x.md"));
    assert!(modal(&root, &entries[0], "x").unwrap().is_none());
    // a modal file refused or unreadable fails the card, as the Python's raised
    put(
        &root,
        "l7r/diagram/interactive/assets/modals/choice/form--x.md",
        "Name: no About\n",
    );
    assert_eq!(
        modal(&root, &entries[0], "x").unwrap_err().message,
        "form--x.md: the docstring has no About: section"
    );
    std::fs::write(
        root.join("l7r/diagram/interactive/assets/modals/choice/form--x.md"),
        [0xff],
    )
    .unwrap();
    assert_eq!(modal(&root, &entries[0], "x").unwrap_err().kind, "OSError");
    // a key the table lists twice keeps one modal under its key
    put(
        &root,
        TABLE,
        &json!({"choices": [{"key": "form", "values": {}}, {"key": "form", "values": {}}]})
            .to_string(),
    );
    let twice = registry_for(&root, &meta(&json!({"form": "row"}))).unwrap();
    assert_eq!(twice.len(), 1);
}
