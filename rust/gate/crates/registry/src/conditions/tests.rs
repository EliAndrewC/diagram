//! A modal item's knob conditions, as `conditions.py` reads, shows and checks them (feature 449 T149; expected values the Python's).

use serde_json::{json, Map, Value};

use super::{
    check, entry_conditions, holds, knob_table, knobs, label, shown, shown_entry, split,
    strip_entry, Cond,
};
use l7r_gate_core::checks::scratch;
use l7r_gate_core::record::testkit::put;

fn meta(v: &Value) -> Map<String, Value> {
    v.as_object().unwrap().clone()
}

fn cond(pairs: &[(&str, &[&str])]) -> Cond {
    pairs
        .iter()
        .map(|(k, vs)| {
            (
                (*k).to_owned(),
                vs.iter().map(|v| (*v).to_owned()).collect(),
            )
        })
        .collect()
}

#[test]
fn an_item_s_conditions_open_it() {
    assert_eq!(split("plain").unwrap(), (None, "plain".to_owned()));
    assert_eq!(
        split("[a=x|y] [b=z]rest").unwrap(),
        (
            Some(cond(&[("a", &["x", "y"]), ("b", &["z"])])),
            "rest".to_owned()
        )
    );
    let e = split("[A=x] text").unwrap_err();
    assert_eq!(e.message, "a modal condition is written [knob=value] or [knob=value|value], lower case: '[A=x] text' (dev/modals.md M22)");
    assert!(split("[a=b] [c d=e]").is_err());
    assert_eq!(
        label(&cond(&[("a", &["x", "y"]), ("b", &["z"])])),
        "(only where a is x or y and b is z)"
    );
}

#[test]
fn an_entry_s_paths_carry_their_own() {
    let entry = "research/questions/a.html [k=v], research/questions/b.html; research/questions/a.html [k=w] [j=q]";
    let got = entry_conditions(entry).unwrap();
    assert_eq!(
        got,
        [(
            "research/questions/a.html".to_owned(),
            cond(&[("k", &["w"]), ("j", &["q"])])
        )]
    );
    assert_eq!(
        strip_entry(entry),
        "research/questions/a.html, research/questions/b.html; research/questions/a.html"
    );
    let m = meta(&json!({"k": "w", "j": "q"}));
    assert_eq!(
        shown_entry(entry, &m).unwrap(),
        "research/questions/a.html, research/questions/b.html, research/questions/a.html"
    );
    assert_eq!(
        shown_entry(entry, &meta(&json!({}))).unwrap(),
        "research/questions/b.html"
    );
    assert_eq!(shown_entry(" , ", &m).unwrap(), "");
}

#[test]
fn a_map_shows_what_its_knobs_meet() {
    let m = meta(&json!({"form": "linear", "n": 2, "f": 1.5, "t": true, "z": null}));
    assert!(holds(None, &m));
    assert!(holds(
        Some(&cond(&[
            ("form", &["linear", "x"]),
            ("n", &["2"]),
            ("f", &["1.5"]),
            ("t", &["True"]),
            ("z", &["None"])
        ])),
        &m
    ));
    // a knob the map records no value for reads as "", as `str(meta.get(knob, ""))` read it
    assert!(holds(
        Some(&cond(&[("missing", &[""])])),
        &meta(&json!({"other": 1}))
    ));
    assert!(!holds(Some(&cond(&[("form", &["nucleated"])])), &m));
    let items = [
        "[form=linear] a".to_owned(),
        "[form=other] b".to_owned(),
        "c".to_owned(),
    ];
    assert_eq!(shown(&items, &m).unwrap(), ["a", "c"]);
    assert!(shown(&["[X=1] bad".to_owned()], &m).is_err());
}

#[test]
fn the_knobs_are_the_registry_s_and_the_choices_and_a_condition_is_checked_against_them() {
    let root = scratch("registry-knobs");
    assert_eq!(knob_table(&root).unwrap_err().kind, "OSError");
    put(&root, super::KNOBS_FILE, "{not json");
    assert_eq!(knob_table(&root).unwrap_err().kind, "JSONDecodeError");
    put(&root, super::KNOBS_FILE, "{\"other\": 1}");
    assert_eq!(knob_table(&root).unwrap_err().message, "knobs");
    put(
        &root,
        super::KNOBS_FILE,
        "{\"knobs\": {\"form\": {\"forms\": [\"a\", \"b\"]}, \"bare\": {}}}",
    );
    assert_eq!(knob_table(&root).unwrap().len(), 2);
    assert!(knobs(&root).is_err());
    put(&root, crate::choices::TABLE, "{\"choices\": [{\"key\": \"form\", \"values\": {\"b\": \"B\", \"c\": \"C\"}}, {\"key\": \"weather\", \"values\": {\"wet\": \"W\"}}, {\"key\": \"bare\"}]}");
    let known = knobs(&root).unwrap();
    assert_eq!(
        known,
        [
            ("form".to_owned(), vec![json!("a"), json!("b"), json!("c")]),
            ("bare".to_owned(), vec![]),
            ("weather".to_owned(), vec![json!("wet")]),
        ]
    );
    assert!(check(&root, "K", &[None, Some(cond(&[("form", &["a", "c"])]))]).is_ok());
    assert_eq!(
        check(&root, "K", &[Some(cond(&[("nope", &["a"])]))]).unwrap_err().message,
        "K: [nope=...] names no registered knob - one of ['bare', 'form', 'weather'] (dev/modals.md M22)"
    );
    assert_eq!(
        check(&root, "K", &[Some(cond(&[("form", &["a", "x", "y"])]))])
            .unwrap_err()
            .message,
        "K: [form=a|x|y]: ['x', 'y'] not among form's forms ['a', 'b', 'c'] (dev/modals.md M22)"
    );
    std::fs::remove_file(root.join(super::KNOBS_FILE)).unwrap();
    assert!(check(&root, "K", &[]).is_err());
}
