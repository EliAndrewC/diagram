//! What a tree owes: each reason a claim is owed, the moved rows, the live rows, a unit's source span and body.

use std::collections::HashMap;
use std::rc::Rc;

use serde_json::{json, Map, Value};

use super::{
    body_of, claim_rewritten, live_rows, load_map, owed, page_blocks, relabel_answered,
    research_fp, source_span, truthy, Cur, PageMemo, Row,
};
use crate::claims::grammar::parse_claim;
use crate::claims::tests::fixture;
use crate::claims::units::Unit;
use crate::record::testkit::put;

fn unit(path: &str, qual: &str, kind: &str, lines: (usize, usize), blocks: &[&str]) -> Unit {
    Unit {
        path: path.into(),
        qualname: qual.into(),
        kind: kind.into(),
        lineno: lines.0,
        end_lineno: lines.1,
        claims: Vec::new(),
        inherited: false,
        core: "core".into(),
        errors: Vec::new(),
        names: Vec::new(),
        blocks: blocks.iter().map(|b| (*b).to_owned()).collect(),
    }
}

fn row(key: &str, u: Unit, line: &str, research: &str) -> Row {
    let claim = parse_claim(line).unwrap();
    Row {
        key: key.into(),
        code: u.code(&claim),
        unit: Rc::new(u),
        claim,
        research: research.into(),
    }
}

fn obj(v: &Value) -> Map<String, Value> {
    v.as_object().unwrap().clone()
}

#[test]
fn python_truth_and_the_files() {
    for (v, t) in [
        (json!(null), false),
        (json!(false), false),
        (json!(0), false),
        (json!(1.5), true),
        (json!(""), false),
        (json!([1]), true),
        (json!({}), false),
    ] {
        assert_eq!(truthy(Some(&v)), t, "{v}");
    }
    assert!(!truthy(None));
    let root = fixture("claims-index-files");
    assert!(load_map(&root.join("nope.json")).unwrap().is_empty());
    put(&root, "x.json", "[]");
    assert!(load_map(&root.join("x.json")).is_err());
    put(&root, "y.json", "{");
    assert!(load_map(&root.join("y.json"))
        .unwrap_err()
        .contains("JSONDecodeError"));
    let mut memo = HashMap::new();
    let q = root.join("research/questions");
    assert_eq!(research_fp(&[], &q, &mut memo).unwrap(), "");
    let fp = research_fp(
        &[
            "research/questions/0001-gap.html".into(),
            "research/questions/0009-x.html".into(),
        ],
        &q,
        &mut memo,
    )
    .unwrap();
    assert_eq!(fp.len(), 16);
    assert_eq!(memo["0009-x.html"], "missing");
    let mut pm = PageMemo::default();
    assert_eq!(
        page_blocks("0009-x.html", &q, &mut pm).unwrap().0,
        "missing"
    );
    assert_eq!(
        page_blocks("0001-gap.html", &q, &mut pm).unwrap().1.len(),
        2
    );
    assert_eq!(pm.snapshots().len(), 2);
    std::fs::write(q.join("0003-bad.html"), [0xff_u8]).unwrap();
    assert!(page_blocks("0003-bad.html", &q, &mut pm).is_err());
}

#[test]
fn a_unit_is_shown_with_its_comments_and_its_body_fingerprinted() {
    let root = fixture("claims-index-span");
    put(&root, "m.py", "# a comment\n@dec\nclass K:\n    x = 1\n    def m(self):\n        pass\n    y = 2\n\nC = 3\n\"\"\"Research: c - NONE\"\"\"\nmore\n\nD = 4\n");
    let (first, text) = source_span(&root, &unit("m.py", "K", "class", (3, 7), &[]))
        .unwrap()
        .unwrap();
    assert_eq!(
        (first, text.as_str()),
        (1, "# a comment\n@dec\nclass K:\n    x = 1")
    );
    let (_, text) = source_span(&root, &unit("m.py", "C", "constant", (9, 9), &[]))
        .unwrap()
        .unwrap();
    assert_eq!(text, "C = 3\n\"\"\"Research: c - NONE\"\"\"\nmore");
    assert!(
        source_span(&root, &unit("gone.py", "C", "constant", (9, 9), &[]))
            .unwrap()
            .is_none()
    );
    assert!(source_span(&root, &unit("m.py", "K", "class", (99, 100), &[])).is_err());
    assert!(source_span(&root, &unit("m.py", "K", "function", (50, 50), &[])).is_err());
    assert_eq!(
        body_of(&root, &unit("gone.py", "C", "constant", (9, 9), &[])).unwrap(),
        ""
    );
    assert_eq!(
        body_of(&root, &unit("m.py", "C", "constant", (9, 9), &[]))
            .unwrap()
            .len(),
        16
    );
    std::fs::write(root.join("bad.py"), [0xff_u8]).unwrap();
    assert!(body_of(&root, &unit("bad.py", "C", "constant", (1, 1), &[])).is_err());
}

#[test]
fn each_reason_a_claim_is_owed() {
    let root = fixture("claims-index-owed");
    let q = root.join("research/questions");
    let page = "research/questions/0001-gap.html";
    let r = research_fp(&[page.into()], &q, &mut HashMap::new()).unwrap();
    let mut cur = Cur::default();
    let mk = |k: &str, kind: &str, blocks: &[&str], line: &str, research: &str| {
        row(
            &format!(
                "rust/phases/src/lib.rs::{k}#{}",
                line.split(" - ").next().unwrap()
            ),
            unit("rust/phases/src/lib.rs", k, kind, (10, 10), blocks),
            line,
            research,
        )
    };
    let rows = [
        mk("new", "function", &[], "new - NONE", ""),
        mk("code", "function", &[], "code - NONE", ""),
        mk("ctri", "function", &[], "ctri - NONE", ""),
        mk("touch", "function", &[], "touch - NONE", ""),
        mk("sect", "function", &["b"], "sect - NONE", ""),
        mk("resfull", "function", &[], &format!("resfull - {page}"), &r),
        mk("rests", "function", &[], &format!("rests - {page}"), &r),
        mk("tri", "function", &[], &format!("tri - {page}"), &r),
        mk("ok", "function", &[], "ok - NONE", ""),
    ];
    let code = |k: &str| {
        rows.iter()
            .find(|x| x.key.contains(&format!("::{k}#")))
            .unwrap()
            .code
            .clone()
    };
    let blocks = page_blocks("0001-gap.html", &q, &mut PageMemo::default())
        .unwrap()
        .clone();
    let index = json!({
        "rust/phases/src/lib.rs::code#code": {"code": "x", "claim": "something else"},
        "rust/phases/src/lib.rs::ctri#ctri": {"code": "x", "claim": "ctri - NONE"},
        "rust/phases/src/lib.rs::touch#touch": {"code": code("touch"), "triage": "touched"},
        "rust/phases/src/lib.rs::sect#sect": {"code": code("sect"), "section": "other"},
        "rust/phases/src/lib.rs::resfull#resfull": {"code": code("resfull"), "research": "old"},
        "rust/phases/src/lib.rs::rests#rests": {"code": code("rests"), "research": "old", "pages": {"0001-gap.html": blocks.0}, "rests": ["0001-gap.html:gone"]},
        "rust/phases/src/lib.rs::tri#tri": {"code": code("tri"), "research": "old", "pages": {"0001-gap.html": blocks.0}, "rests": [format!("0001-gap.html:{}", blocks.1[0].0)]},
        "rust/phases/src/lib.rs::ok#ok": {"code": code("ok"), "research": ""},
    });
    for r in rows {
        cur.insert(r);
    }
    let store = obj(&json!({blocks.0.clone(): []}));
    let due = owed(&cur, &obj(&index), Some(&q), Some(&store)).unwrap();
    let got: HashMap<String, String> = due
        .into_iter()
        .map(|(k, w)| {
            (
                k.split("::")
                    .nth(1)
                    .unwrap()
                    .split('#')
                    .next()
                    .unwrap()
                    .to_owned(),
                w,
            )
        })
        .collect();
    for (k, w) in [
        ("new", "new"),
        ("code", "code changed"),
        ("ctri", "code triage"),
        ("touch", "triage touched"),
        ("sect", "section triage"),
        ("resfull", "research changed"),
        ("rests", "rests changed"),
        ("tri", "triage"),
    ] {
        assert_eq!(got.get(k).map(String::as_str), Some(w), "{k}");
    }
    assert!(!got.contains_key("ok"));
    let none = owed(&cur, &obj(&index), None, None).unwrap();
    assert!(none
        .iter()
        .any(|(k, w)| k.contains("::tri#") && w == "research changed"));
    let live = live_rows(
        &cur,
        &obj(
            &json!({"rust/phases/src/lib.rs::ok#ok": {}, "rust/phases/src/lib.rs::ok#u": {"verdict": "UNCLAIMED"}, "gone::x#y": {"verdict": "UNCLAIMED"}, "gone::x#z": {}}),
        ),
    );
    assert_eq!(live.len(), 2);
    assert!(
        claim_rewritten(&json!({"claim": "a"}), "b")
            && !claim_rewritten(&json!({"claim": null}), "b")
            && !claim_rewritten(&json!({}), "b")
    );
}

#[test]
fn a_relabel_alone_owes_nothing_and_answers_its_mislabel() {
    let root = fixture("claims-index-relabel");
    let q = root.join("research/questions");
    let u = unit("rust/phases/src/lib.rs", "GAP", "constant", (10, 10), &[]);
    let body = body_of(&root, &u).unwrap();
    let r = row(
        "rust/phases/src/lib.rs::GAP#gap",
        u,
        "gap - NONE: relabeled",
        "",
    );
    let mut cur = Cur::default();
    cur.insert(r.clone());
    let was = json!({"code": "old", "body": body, "claim": "gap - NONE: before", "verdict": "MISLABELED", "research": ""});
    assert!(owed(
        &cur,
        &obj(&json!({r.key.clone(): was.clone()})),
        Some(&q),
        None
    )
    .unwrap()
    .is_empty());
    assert!(relabel_answered(&was, &r, &root).unwrap());
    let in_step = json!({"code": "old", "body": body, "claim": r.claim.normalized(), "verdict": "IN-STEP", "research": ""});
    assert!(!relabel_answered(&in_step, &r, &root).unwrap());
    assert!(
        owed(
            &cur,
            &obj(&json!({r.key.clone(): {"code": "old", "body": "other"}})),
            Some(&q),
            None
        )
        .unwrap()
        .len()
            == 1
    );
    assert_eq!(
        owed(&cur, &obj(&json!({r.key.clone(): {}})), Some(&q), None).unwrap()[0].1,
        "new"
    );
}

#[test]
fn a_key_with_no_unit_moves_nowhere_and_a_page_with_no_rests_is_triaged() {
    let root = fixture("claims-index-more");
    let q = root.join("research/questions");
    let mut cur = Cur::default();
    let r = row(
        "nocolon",
        unit("a.rs", "x", "function", (1, 1), &[]),
        "x - research/questions/0001-gap.html",
        "new",
    );
    cur.insert(r.clone());
    assert!(super::moved(&cur, &obj(&json!({"a.rs::x#x": {"code": r.code}}))).is_empty());
    let blocks = page_blocks("0001-gap.html", &q, &mut PageMemo::default())
        .unwrap()
        .clone();
    let was = json!({"code": r.code, "research": "old", "pages": {"0001-gap.html": blocks.0}});
    let store = obj(&json!({blocks.0.clone(): []}));
    let due = owed(&cur, &obj(&json!({"nocolon": was})), Some(&q), Some(&store)).unwrap();
    assert_eq!(due[0].1, "triage");
}
