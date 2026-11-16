//! The verdicts (feature 449 T145; each expected value `quote_verbatim.py`'s `_verdict`, `judge_note` and `report` on the same input, 2026-11-16).

use serde_json::{json, Map, Value};

use super::{differences, find_in_order, judge_note, nearest, report, round3, unmarked, verdict};
use crate::verbatim::fetch::Got;

const VERDICTS: &str = r#"[["The dike was nine feet wide.", "x The dike was nine feet wide. y", {"quotation": "VERBATIM"}], ["The dike was ... three feet deep", "The dike was nine feet wide. The pond was three feet deep!", {"quotation": "VERBATIM"}], ["people[1][2] lived", "people lived", {"quotation": "NOT-ON-PAGE", "similarity": 0.8}], ["人宿、町", "人宿[1][2][3]、町", {"quotation": "DIFFERS", "page_text": "人宿[1][2][3]、町", "differences": ["quoted '' / page '[1][2][3]'"], "similarity": 1.0, "only_reference_markers": true}], ["The dike was nine feet wyde", "Long text. The dike was nine feet wide. More.", {"quotation": "DIFFERS", "page_text": "The dike was nine feet wide", "differences": ["quoted 'y' / page 'i'"], "similarity": 0.963, "only_reference_markers": false}], ["nothing alike at all here", "zzzz qqqq", {"quotation": "NOT-ON-PAGE", "similarity": 0.0}], ["", "page", {"quotation": "NOT-ON-PAGE", "similarity": 0.0}], ["a … b", "a x b", {"quotation": "VERBATIM"}], ["Tail & end marker", "Tail & end [1] marker", {"quotation": "DIFFERS", "page_text": "Tail & end [1] marker", "differences": ["quoted '' / page '[1] '"], "similarity": 1.0, "only_reference_markers": true}], ["abc", "", {"quotation": "NOT-ON-PAGE", "similarity": 0.0}], ["one two", "one [note 3] two", {"quotation": "DIFFERS", "page_text": "one [note 3] two", "differences": ["quoted '' / page '[note 3] '"], "similarity": 1.0, "only_reference_markers": true}]]"#;

#[test]
fn each_verdict_is_the_pythons() {
    let cases: Value = serde_json::from_str(VERDICTS).unwrap();
    for c in cases.as_array().unwrap() {
        let got = Value::Object(verdict(c[0].as_str().unwrap(), c[1].as_str().unwrap()));
        assert_eq!(got, c[2], "{c}");
    }
}

#[test]
fn the_nearest_stretch_and_its_differences() {
    assert_eq!(
        nearest(
            &"".chars().collect::<Vec<_>>(),
            &"x".chars().collect::<Vec<_>>()
        ),
        (0.0, Vec::new())
    );
    assert_eq!(
        nearest(
            &"abc".chars().collect::<Vec<_>>(),
            &"xyz".chars().collect::<Vec<_>>()
        ),
        (0.0, Vec::new())
    );
    let (r, t) = nearest(
        &"the dike".chars().collect::<Vec<_>>(),
        &"a the dikes b".chars().collect::<Vec<_>>(),
    );
    assert!((r - 1.0).abs() < 1e-12);
    assert_eq!(t.iter().collect::<String>(), "the dike");
    assert_eq!(
        differences(
            &"abcd".chars().collect::<Vec<_>>(),
            &"abXd e".chars().collect::<Vec<_>>()
        ),
        vec!["quoted 'c' / page 'X'", "quoted '' / page ' e'"]
            .into_iter()
            .map(str::to_owned)
            .collect::<Vec<_>>()
    );
    assert_eq!(find_in_order(&[], &"a".chars().collect::<Vec<_>>()), None);
    assert_eq!(
        find_in_order(
            &[
                "b".chars().collect::<Vec<_>>(),
                "d".chars().collect::<Vec<_>>()
            ],
            &"abcd".chars().collect::<Vec<_>>()
        ),
        Some((1, 4))
    );
    assert_eq!(
        find_in_order(
            &[
                "d".chars().collect::<Vec<_>>(),
                "b".chars().collect::<Vec<_>>()
            ],
            &"abcd".chars().collect::<Vec<_>>()
        ),
        None
    );
    assert_eq!(
        find_in_order(
            &["abcde".chars().collect::<Vec<_>>()],
            &"abcd".chars().collect::<Vec<_>>()
        ),
        None
    );
    assert_eq!(
        unmarked("a[1] b[note 2]c"),
        ("a bc".chars().collect::<Vec<_>>(), vec![0, 4, 5, 14])
    );
    assert!((round3(0.0625) - 0.062).abs() < f64::EPSILON);
    assert!((round3(0.0005) - 0.001).abs() < f64::EPSILON);
    assert!((round3(0.12345) - 0.123).abs() < f64::EPSILON);
    assert!((round3(0.874_999_9) - 0.875).abs() < f64::EPSILON);
    assert!((round3(1.0) - 1.0).abs() < f64::EPSILON);
    assert!((round3(0.85049) - 0.85).abs() < f64::EPSILON);
}

const TABLE: &str = r#"{"u/live": {"state": "FETCHED", "text": "The dike was nine feet wide. Tail & end [1] marker."}, "u/arch": {"state": "FETCHED", "text": "the archived text of a pdf", "archived": "2026-10-02", "live": false}, "u/arch-live": {"state": "FETCHED", "text": "the archived text of a pdf", "archived": "2026-10-02", "live": true}, "u/archblank": {"state": "FETCHED", "text": "The dike was nine feet wide.", "archived": ""}, "u/dead": {"state": "UNFETCHABLE", "why": "gone"}, "u/pdf": {"state": "NOT-CHECKED", "why": "a PDF"}, "own": {"state": "OWN", "why": "a link into this project, not a public page"}}"#;
const NOTES: &str = r#"[{"id": "fn-1", "key": "a", "links": ["u/live"], "class": "citation", "passages": [{"quote": "The dike was nine feet wide.", "original": "", "language": ""}]}, {"id": "fn-2", "key": "b", "links": ["u/live"], "class": "citation", "passages": [{"quote": "Tail & end marker.", "original": "", "language": ""}]}, {"id": "fn-3", "key": "c", "links": ["u/live"], "class": "citation", "passages": [{"quote": "q", "original": "nothing like it anywhere at all", "language": "ja", "more": ["x"]}]}, {"id": "fn-4", "key": "d", "links": ["u/live", "u/dead"], "class": "citation", "passages": [{"quote": "nowhere to be found in it", "original": "", "language": ""}]}, {"id": "fn-5", "key": "e", "links": ["u/dead"], "class": "citation", "passages": [{"quote": "x", "original": "", "language": ""}]}, {"id": "fn-6", "key": "f", "links": ["u/pdf"], "class": "citation", "passages": [{"quote": "x", "original": "", "language": ""}]}, {"id": "fn-7", "key": "g", "links": ["u/arch"], "class": "citation", "passages": [{"quote": "archived text", "original": "", "language": ""}]}, {"id": "fn-8", "key": "h", "links": ["u/arch"], "class": "citation", "passages": [{"quote": "not in the capture", "original": "", "language": ""}]}, {"id": "fn-9", "key": "i", "links": ["u/arch-live"], "class": "citation", "passages": [{"quote": "archived text", "original": "", "language": ""}]}, {"id": "fn-10", "key": "j", "links": ["own"], "class": "citation", "passages": [{"quote": "x", "original": "", "language": ""}]}, {"id": "fn-11", "key": "k", "links": ["u/live"], "class": "citation", "passages": []}, {"id": "fn-12", "key": "l", "links": ["u/archblank", "u/live"], "class": "citation", "passages": [{"quote": "The dike was nine feet wide.", "original": "", "language": ""}]}, {"id": "fn-13", "key": "m", "links": ["u/live"], "class": "citation", "passages": [{"quote": "The dike was nine feet wyde.", "original": "", "language": ""}]}, {"id": "fn-14", "key": "n", "links": [], "class": "absence", "passages": []}]"#;
const REPORT: &str = r#"[{"id": "fn-1", "key": "a", "links": ["u/live"], "class": "citation", "passages": [{"quote": "The dike was nine feet wide.", "original": "", "language": "", "matched": "quote", "quotation": "VERBATIM"}], "readability": "READABLE", "assertion": "said one"}, {"id": "fn-2", "key": "b", "links": ["u/live"], "class": "citation", "passages": [{"quote": "Tail & end marker.", "original": "", "language": "", "matched": "quote", "quotation": "DIFFERS", "page_text": "Tail & end [1] marker.", "differences": ["quoted '' / page '[1] '"], "similarity": 1.0, "only_reference_markers": true}], "readability": "READABLE", "assertion": ""}, {"id": "fn-3", "key": "c", "links": ["u/live"], "class": "citation", "passages": [{"quote": "q", "original": "nothing like it anywhere at all", "language": "ja", "more": ["x"], "matched": "original", "quotation": "NOT-ON-PAGE", "similarity": 0.407}], "readability": "NOT-READABLE (the page was read and does not carry the passage as quoted)", "assertion": ""}, {"id": "fn-4", "key": "d", "links": ["u/live", "u/dead"], "class": "citation", "passages": [{"quote": "nowhere to be found in it", "original": "", "language": "", "matched": "quote", "quotation": "NOT-CHECKED", "why": "not on the pages read; it may be on u/dead, which could not be read here"}], "readability": "-", "assertion": ""}, {"id": "fn-5", "key": "e", "links": ["u/dead"], "class": "citation", "passages": [{"quote": "x", "original": "", "language": "", "matched": "quote", "quotation": "UNFETCHABLE", "why": "gone"}], "readability": "-", "assertion": ""}, {"id": "fn-6", "key": "f", "links": ["u/pdf"], "class": "citation", "passages": [{"quote": "x", "original": "", "language": "", "matched": "quote", "quotation": "NOT-CHECKED", "why": "a PDF"}], "readability": "-", "assertion": ""}, {"id": "fn-7", "key": "g", "links": ["u/arch"], "class": "citation", "passages": [{"quote": "archived text", "original": "", "language": "", "matched": "quote", "quotation": "VERBATIM", "archived": "2026-10-02"}], "readability": "-", "assertion": ""}, {"id": "fn-8", "key": "h", "links": ["u/arch"], "class": "citation", "passages": [{"quote": "not in the capture", "original": "", "language": "", "matched": "quote", "quotation": "NOT-CHECKED", "why": "not found verbatim in the archived text of 2026-10-02 - check by hand"}], "readability": "-", "assertion": ""}, {"id": "fn-9", "key": "i", "links": ["u/arch-live"], "class": "citation", "passages": [{"quote": "archived text", "original": "", "language": "", "matched": "quote", "quotation": "VERBATIM", "archived": "2026-10-02"}], "readability": "READABLE", "assertion": ""}, {"id": "fn-10", "key": "j", "links": ["own"], "class": "citation", "passages": [{"quote": "x", "original": "", "language": "", "matched": "quote", "quotation": "NOT-CHECKED", "why": "a link into this project, not a public page"}], "readability": "NOT-READABLE (the link is this project's own page)", "assertion": ""}, {"id": "fn-11", "key": "k", "links": ["u/live"], "class": "citation", "passages": [], "readability": "-", "assertion": ""}, {"id": "fn-12", "key": "l", "links": ["u/archblank", "u/live"], "class": "citation", "passages": [{"quote": "The dike was nine feet wide.", "original": "", "language": "", "matched": "quote", "quotation": "VERBATIM"}], "readability": "READABLE", "assertion": ""}, {"id": "fn-13", "key": "m", "links": ["u/live"], "class": "citation", "passages": [{"quote": "The dike was nine feet wyde.", "original": "", "language": "", "matched": "quote", "quotation": "DIFFERS", "page_text": "The dike was nine feet wide.", "differences": ["quoted 'y' / page 'i'"], "similarity": 0.964, "only_reference_markers": false}], "readability": "NOT-READABLE (the page was read and does not carry the passage as quoted)", "assertion": ""}, {"id": "fn-14", "key": "n", "links": [], "class": "absence", "passages": [], "readability": "-", "assertion": "said none"}]"#;

fn got_of(v: &Value) -> Got {
    let s = |k: &str| v.get(k).and_then(Value::as_str).map(str::to_owned);
    Got {
        state: s("state").unwrap_or_default(),
        text: s("text").unwrap_or_default(),
        why: s("why").unwrap_or_default(),
        cached: None,
        archived: s("archived"),
        live: v.get("live").and_then(Value::as_bool).unwrap_or(false),
        blocked: false,
    }
}

#[test]
fn every_readability_and_every_passage_verdict() {
    let table: Value = serde_json::from_str(TABLE).unwrap();
    let notes: Vec<Map<String, Value>> = serde_json::from_str(NOTES).unwrap();
    let claims = json!({"fn-1": "said one", "fn-14": "said none"});
    let mut get = |u: &str| got_of(&table[u]);
    let out = report(&notes, claims.as_object().unwrap(), &mut get);
    let want: Value = serde_json::from_str(REPORT).unwrap();
    for (got, want) in out.iter().zip(want.as_array().unwrap()) {
        assert_eq!(&Value::Object(got.clone()), want);
    }
    assert_eq!(out.len(), want.as_array().unwrap().len());
    let note = notes[0].clone();
    assert_eq!(judge_note(&note, &mut get)["readability"], "READABLE");
}
