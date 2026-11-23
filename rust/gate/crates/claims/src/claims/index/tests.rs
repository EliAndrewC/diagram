//! What a tree owes: each reason a claim is owed, the moved rows, the live rows, a unit's source span and body.

use std::collections::HashMap;
use std::rc::Rc;

use serde_json::{json, Map, Value};

use super::{
    body_of, claim_rewritten, live_rows, load_map, owed, page_blocks, relabel_answered,
    relabeled_only, research_fp, source_span, truthy, Cur, PageMemo, Row,
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
        reads: String::new(),
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
    // a Rust unit's constant reads recorded on its row (feature 449 T166): the body the same, a value it reads changed is code
    // changed, not a relabel; the same reads, or a row recorded before T166 with none, is the relabel it was
    let mut reading = r.clone();
    let mut u = (*reading.unit).clone();
    u.reads = "now".into();
    reading.unit = std::rc::Rc::new(u);
    let same = json!({"code": "old", "body": body, "claim": reading.claim.normalized(), "verdict": "IN-STEP", "research": ""});
    let mut moved = same.clone();
    moved["reads"] = json!("then");
    let mut kept = same.clone();
    kept["reads"] = json!("now");
    assert!(!relabeled_only(&moved, &reading, &root).unwrap());
    assert!(relabeled_only(&kept, &reading, &root).unwrap());
    assert!(relabeled_only(&same, &reading, &root).unwrap());
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

/// 0027 as `off_the_dike`'s account cites it, a page its backing never names.
const DIKES: &str = "research/questions/0027-polder-dikes.drawing.html";

#[test]
fn an_edit_of_a_page_a_claim_cites_only_in_its_account_owes_the_claim() {
    // 449 T249: off_the_dike's claims cited 0027 in their accounts, backed by 0019 and 0081 alone; an edit of 0027 owed no claim
    let page = |text: &str| format!("<h2 id=\"polder-dikes\">Polder dikes</h2>\n<p>{text}</p>\n");
    let root = crate::claims::tests::fixture_with("claims-index-cited", &|r| {
        put(r, DIKES, &page("The dike is 12 ft broad."));
    });
    let q = root.join("research/questions");
    let mut u = unit(
        "rust/phases/src/driver/polder.rs",
        "off_the_dike",
        "function",
        (1, 1),
        &[],
    );
    let line = format!("straight at the widest - research/questions/0001-gap.html: the village off its dike; {DIKES}: the face pushed out");
    u.claims = vec![parse_claim(&line).unwrap()];
    let cur = super::rows_of(vec![(u.clone(), Vec::new())], &q).unwrap();
    let row = cur.iter().next().unwrap().clone();
    let mut memo = PageMemo::default();
    let gap = page_blocks("0001-gap.html", &q, &mut memo).unwrap().clone();
    let dikes = page_blocks("0027-polder-dikes.drawing.html", &q, &mut memo)
        .unwrap()
        .clone();
    let rest = format!("0027-polder-dikes.drawing.html:{}", dikes.1[0].0);
    let was = json!({"code": row.code, "research": row.research, "pages": {"0001-gap.html": gap.0, "0027-polder-dikes.drawing.html": dikes.0}, "rests": [rest]});
    let index = obj(&json!({row.key.clone(): was}));
    let store = obj(&json!({gap.0.clone(): [], dikes.0.clone(): []}));
    let before = owed(&cur, &index, Some(&q), Some(&store)).unwrap();
    assert!(before.is_empty(), "{before:?}");
    put(&root, DIKES, &page("The dike is 20 ft broad."));
    let cur = super::rows_of(vec![(u, Vec::new())], &q).unwrap();
    let due = owed(&cur, &index, Some(&q), Some(&store)).unwrap();
    let why: Vec<&str> = due.iter().map(|(_, w)| w.as_str()).collect();
    assert_eq!(why, ["rests changed"]);
}

const MAG: &str = "research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html";
const WELLS: &str = "research/questions/0196-communal-wells-ido.drawing.html";
/// The 12 claims 451 T192's sample named: label, class, drawing page, the item named.
const SAMPLE: [(&str, &str, &str, &str); 12] = [
    (
        "divider gate on the axis",
        "GUESS",
        MAG,
        "middle-gate-behind-hall",
    ),
    (
        "well curb size about 4 ft",
        "GUESS",
        WELLS,
        "curb-s-exact-size",
    ),
    (
        "well gear about three in four by the water's depth",
        "GUESS",
        WELLS,
        "about-three-wells-four",
    ),
    (
        "well depth by the ground",
        "GUESS",
        WELLS,
        "valley-shallow-upland-deep",
    ),
    (
        "an indoor well hangs its pulley from the beams",
        "GUESS",
        WELLS,
        "well-indoors-kitchen-s",
    ),
    (
        "a roof over about one well in three",
        "GUESS",
        WELLS,
        "roof-one-well-in-three",
    ),
    (
        "posting wealth knob",
        "GUESS",
        MAG,
        "poor-office-drawn-poor",
    ),
    (
        "no well at a hilltop shrine",
        "GUESS",
        WELLS,
        "hilltop-shrine-no-well",
    ),
    (
        "water depth from the landform",
        "GUESS",
        WELLS,
        "valley-shallow-upland-deep",
    ),
    (
        "an indoor well's gear",
        "GUESS",
        WELLS,
        "well-indoors-kitchen-s",
    ),
    (
        "the middle gate beside the office hall",
        "DEVIATION",
        MAG,
        "middle-gate-beside-hall",
    ),
    (
        "water depth from the landform",
        "GUESS",
        WELLS,
        "valley-shallow-upland-deep",
    ),
];

/// Feature 451 T204: the 12 claims 451 T192's sample named (10 doc sections, 2 Rust items; GUESS or DEVIATION on the drawing pages of
/// 0090 and 0196), each recorded before it named its item, so the stored claim holds its class word: naming the item, the class kept,
/// owes nothing, where all 12 owed `code changed`; the class changed with the naming, or the account, still owes.
#[test]
fn naming_the_item_of_a_classed_claim_owes_nothing() {
    let root = fixture("claims-index-relabel");
    let q = root.join("research/questions");
    let u = unit("rust/phases/src/lib.rs", "GAP", "constant", (10, 10), &[]);
    let body = body_of(&root, &u).unwrap();
    let key = "rust/phases/src/lib.rs::GAP#gap";
    let was_of = |line: &str| json!({"code": "old", "body": body, "claim": parse_claim(line).unwrap().normalized(), "verdict": "IN-STEP", "research": ""});
    let owes = |claim_row: &Row, was: &Value| {
        let mut cur = Cur::default();
        cur.insert(claim_row.clone());
        owed(&cur, &obj(&json!({key: was.clone()})), Some(&q), None).unwrap()
    };
    // a doc section's claim (10 of the 12) stores no body and no claim: its code is the claim alone
    let section = unit("docs/buildings.md", "Wells", "section", (1, 1), &[]);
    let section_was =
        |line: &str| json!({"code": section.code(&parse_claim(line).unwrap()), "research": ""});
    for (label, class, page, id) in SAMPLE {
        let before = format!("{label} - {class} {page}: as drawn");
        let named = format!("{label} - {class} {page}#{id}: as drawn");
        let was = was_of(&before);
        let named_row = row(key, u.clone(), &named, "");
        assert!(relabeled_only(&was, &named_row, &root).unwrap(), "{label}");
        assert!(owes(&named_row, &was).is_empty(), "{label}");
        let doc = row(key, section.clone(), &named, "");
        assert!(owes(&doc, &section_was(&before)).is_empty(), "{label}");
    }
    let before = format!("gear - GUESS {WELLS}: as drawn");
    let was = was_of(&before);
    for changed in [
        format!("gear - DEVIATION {WELLS}#x: as drawn"),
        format!("gear - {WELLS}#x: as drawn"),
        format!("gear - GUESS {WELLS}#x: drawn otherwise"),
    ] {
        let named_row = row(key, u.clone(), &changed, "");
        let relabel = relabeled_only(&was, &named_row, &root).unwrap();
        assert!(!relabel, "{changed}");
        assert_eq!(owes(&named_row, &was).len(), 1, "{changed}");
        let doc = row(key, section.clone(), &changed, "");
        assert_eq!(owes(&doc, &section_was(&before)).len(), 1, "{changed}");
    }
}
