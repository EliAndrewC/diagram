//! A reply read and recorded: the verdict forms, the rests, the foreign rests dropped, the elided names restored.

use serde_json::{json, Map, Value};

use super::{outside_tag, parse_reply, record, rests_of, unelide};

fn obj(v: Value) -> Map<String, Value> {
    v.as_object().unwrap().clone()
}

#[test]
fn a_reply_is_read_in_each_form() {
    let (v, u) = parse_reply("`VERDICT a::b#c IN-STEP - the colour [§1]`\nVERDICT `d::e#f` - DRIFTED: off\nUNCLAIMED a::b - a choice\nnoise");
    assert_eq!(
        v["a::b#c"],
        ("IN-STEP".to_owned(), "the color [§1]".to_owned())
    );
    assert_eq!(v["d::e#f"].0, "DRIFTED");
    assert_eq!(u, vec![("a::b".to_owned(), "a choice".to_owned())]);
    assert_eq!(
        outside_tag("  [outside the change] x "),
        (true, "x".to_owned())
    );
    assert_eq!(outside_tag("x"), (false, "x".to_owned()));
    let stems = vec![
        "0236-shrine-home-plot".to_owned(),
        "0300-a".to_owned(),
        "0300-b".to_owned(),
    ];
    assert_eq!(
        unelide(
            "see 0236-...-home-plot.drawing.html and 0300-..b.html and 0999-...x.html",
            &stems
        ),
        "see 0236-shrine-home-plot.drawing.html and 0300-..b.html and 0999-...x.html"
    );
    let numbered = obj(json!({"§1": "p.html:d1", "§2": "q.html:d2"}));
    assert_eq!(
        rests_of("note [§2, §1, §9]", &numbered),
        (
            "note".to_owned(),
            Some(vec!["p.html:d1".to_owned(), "q.html:d2".to_owned()])
        )
    );
    assert_eq!(
        rests_of("note [§]", &numbered),
        ("note".to_owned(), Some(Vec::new()))
    );
    assert_eq!(rests_of("note", &numbered), ("note".to_owned(), None));
}

#[test]
fn a_reply_writes_its_rows() {
    let index =
        obj(json!({"a::u#old": {"verdict": "UNCLAIMED"}, "z::v#k": {"verdict": "IN-STEP"}}));
    let units = obj(json!({
        "a::u#c": {"code": "1", "core": "c1", "body": "b", "claim": "c", "research": "r", "uid": "a::u", "pages": {"p.html": "f"}, "section": "s"},
        "a::u#d": {"code": "2", "core": "c1", "research": "", "uid": "a::u", "pages": {"p.html": "f"}},
        "a::u#e": {"code": "3", "core": "c1", "research": "", "uid": "a::u"},
    }));
    let numbered = obj(json!({"§1": "p.html:d1", "§2": "q.html:d2"}));
    let text = "VERDICT a::u#c DRIFTED - [outside the change] off [§1]\nVERDICT a::u#d IN-STEP - fine [§2]\nVERDICT gone#x IN-STEP - no\nUNCLAIMED a::u - [outside the change] new one\nUNCLAIMED b::x - no";
    let (out, msgs) = record(&index, &units, text, "2026-11-11", &numbered);
    assert!(!out.contains_key("a::u#old") && out.contains_key("z::v#k"));
    assert_eq!(out["a::u#c"]["outside"], true);
    assert_eq!(out["a::u#c"]["rests"], json!(["p.html:d1"]));
    assert_eq!(out["a::u#c"]["section"], "s");
    assert!(out["a::u#d"].get("rests").is_none());
    assert_eq!(out["a::u#new one"]["outside"], true);
    assert_eq!(
        msgs,
        vec![
            "refused: `gone#x` is not a unit of this bundle",
            "`a::u#d`: rests on q.html, a page it does not cite - dropped (was the reply judged against another bundle's numbering?)",
            "no verdict for `a::u#e` - it stays owed",
            "UNCLAIMED a::u - new one: write a claim for it, then check it",
            "refused: UNCLAIMED `b::x` is not a unit of this bundle",
        ]
    );
    let (out, _) = record(
        &index,
        &units,
        "VERDICT a::u#c IN-STEP - [outside the change] fine [§1, §2]\nUNCLAIMED a::u - plain",
        "d",
        &numbered,
    );
    assert!(out["a::u#c"].get("outside").is_none());
    assert_eq!(out["a::u#c"]["rests"], json!(["p.html:d1"]));
    assert!(out["a::u#plain"].get("outside").is_none());
}
