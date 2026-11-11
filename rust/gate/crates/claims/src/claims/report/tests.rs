//! The report's counts and lists, the form problems, and each way `classify` reads a finding against the merge base.

use std::collections::{HashMap, HashSet};
use std::rc::Rc;

use serde_json::{json, Map, Value};

use super::{
    base_tree, classify, coverage, delta_form_problems, names_claimed, open_findings, report,
    verdict_of, Base,
};
use crate::claims::grammar::parse_claim;
use crate::claims::index::{research_fp, Cur, Row};
use crate::claims::tests::fixture;
use crate::claims::units::{Pair, Unit};
use crate::record::testkit::{commit, git, put};

fn unit(qual: &str, claims: &[&str], errors: &[&str]) -> Unit {
    Unit {
        path: "a.rs".into(),
        qualname: qual.into(),
        kind: "function".into(),
        lineno: 1,
        end_lineno: 1,
        claims: claims.iter().map(|c| parse_claim(c).unwrap()).collect(),
        inherited: false,
        core: format!("core-{qual}"),
        errors: errors.iter().map(|e| (*e).to_owned()).collect(),
        names: Vec::new(),
        blocks: Vec::new(),
    }
}

fn obj(v: &Value) -> Map<String, Value> {
    v.as_object().unwrap().clone()
}

#[test]
fn the_form_problems_and_the_verdicts() {
    let pairs: Vec<Pair> = vec![
        (unit("a", &[], &["bad"]), vec!["module".into()]),
        (unit("b", &[], &[]), vec!["module".into()]),
        (
            unit("c", &["c - research/questions/0009-x.html"], &[]),
            Vec::new(),
        ),
        (
            Unit {
                kind: "section".into(),
                ..unit("d", &[], &[])
            },
            Vec::new(),
        ),
    ];
    let got = coverage(&pairs, &HashSet::new());
    assert_eq!(got.len(), 5);
    assert_eq!(got[0], "a.rs module docstring: module");
    assert_eq!(got[1], "a.rs:1 a: bad");
    assert!(
        got[2].ends_with("no claim - add a `Research:` claim (own, or in its module docstring)")
    );
    assert!(got[3].contains("names no question file"));
    assert!(got[4].ends_with("a `<!-- Research: <label> - <backing> -->` comment"));
    assert!(verdict_of(&json!({})).unwrap_err().contains("KeyError"));
    assert!(verdict_of(&json!({"verdict": 3}))
        .unwrap_err()
        .contains("TypeError"));
    let rows = obj(
        &json!({"a.rs::K_ONE#x": {"verdict": "IN-STEP"}, "a.rs::f#uses K_ONE": {"verdict": "UNCLAIMED"}, "a.rs::K_TWO#x": {"verdict": "DRIFTED"}, "a.rs::K_TWO#y": {"verdict": "UNCLAIMED"}}),
    );
    let open = open_findings(&rows, &HashSet::new()).unwrap();
    assert_eq!(
        open.iter().map(|o| o.1.as_str()).collect::<Vec<_>>(),
        vec!["a.rs::K_TWO#x", "a.rs::K_TWO#y"]
    );
    assert!(names_claimed(
        "a.rs::f#uses K_ONE",
        &HashSet::from([("a.rs".to_owned(), "K_ONE".to_owned())])
    ));
    assert!(open_findings(&obj(&json!({"x": {}})), &HashSet::new()).is_err());
}

#[test]
fn the_report_counts_and_lists_the_open_research() {
    let root = fixture("claims-report-list");
    let mut cur = Cur::default();
    for (q, line) in [("a", "a - UNRESEARCHED"), ("b", "b - NONE")] {
        let u = Rc::new(unit(q, &[line], &[]));
        let claim = u.claims[0].clone();
        cur.insert(Row {
            key: u.key(&claim),
            code: u.code(&claim),
            unit: u,
            claim,
            research: String::new(),
        });
    }
    let q = root.join("research/questions");
    let text = report(&cur, &Map::new(), &q, &Map::new(), &HashSet::new(), false).unwrap();
    assert_eq!(text, "claims: 2 in scope; no verdicts yet; owed 2\nUNRESEARCHED claims (the open research): 1\n  a.rs::a#a");
    let index = obj(&json!({"a.rs::a#a": {"verdict": 5}}));
    assert!(report(&cur, &index, &q, &Map::new(), &HashSet::new(), false).is_err());
    assert!(report(&cur, &index, &q, &Map::new(), &HashSet::new(), true).is_err());
}

#[test]
fn a_form_problem_in_a_changed_file_refuses_and_the_base_tree_is_read() {
    let root = fixture("claims-report-delta");
    let pairs: Vec<Pair> = vec![(unit("a", &[], &["bad"]), Vec::new())];
    assert!(delta_form_problems(&root, &pairs).is_empty());
    put(&root, "a.rs", "x\n");
    commit(&root, "a");
    let got = delta_form_problems(&root, &pairs);
    assert_eq!(got.len(), 1);
    assert!(got[0].starts_with("a.rs:1 a: bad - the claims grammar: a claim is one line"));
    let into = crate::checks::scratch("claims-report-base");
    base_tree("git", &root, "HEAD", &into).unwrap();
    assert!(
        into.join("research/questions/0001-gap.html").is_file()
            && into.join("l7r/diagram/hamletgen").is_dir()
    );
    let fake = into.join("fake-git");
    crate::write_executable(
        &fake,
        "#!/bin/sh\ncase \"$3\" in cat-file) exit 0;; esac\necho 'fatal: no' >&2\nexit 128\n",
    );
    let err = base_tree(&fake.to_string_lossy(), &root, "HEAD", &into).unwrap_err();
    assert_eq!(
        err,
        "RuntimeError: claims: the base tree could not be read at HEAD: fatal: no"
    );
    let none = crate::checks::scratch("claims-report-none");
    git(&none, &["init", "-q"]);
    base_tree("git", &none, "HEAD", &none).unwrap();
}

/// The rows and the index `classify` is asked about: (root, rows, index).
fn classify_rows() -> (l7r_guard::shared::tempdir::TempDir, Cur, Map<String, Value>) {
    let root = fixture("claims-report-classify");
    let q = root.join("research/questions");
    let (same_page, moved_page) = (
        "research/questions/0001-gap.html",
        "research/questions/0002-other.drawing.html",
    );
    let mut cur = Cur::default();
    let mut add = |name: &str, page: &str| {
        let u = Rc::new(unit(name, &[&format!("{name} - {page}")], &[]));
        let claim = u.claims[0].clone();
        let research = research_fp(&claim.pointers, &q, &mut HashMap::new()).unwrap();
        cur.insert(Row {
            key: u.key(&claim),
            code: u.code(&claim),
            unit: u,
            claim,
            research,
        });
    };
    for name in [
        "pre", "carry", "out", "same", "moved", "newcode", "stays", "deferred", "answered", "fine",
    ] {
        add(name, same_page);
    }
    for name in ["resmoved", "resonly"] {
        add(name, moved_page);
    }
    let mut index = Map::new();
    for name in [
        "pre", "carry", "out", "same", "moved", "newcode", "resmoved", "resonly", "stays",
        "deferred", "answered",
    ] {
        index.insert(format!("a.rs::{name}#{name}"), json!({"verdict": "DRIFTED", "note": "n", "core": format!("core-{name}"), "claim": "c"}));
    }
    index.insert("a.rs::fine#fine".into(), json!({"verdict": "IN-STEP"}));
    index.insert(
        "a.rs::fine#an unclaimed".into(),
        json!({"verdict": "UNCLAIMED", "core": "core-fine", "outside": true}),
    );
    index.insert(
        "a.rs::fine#plain unclaimed".into(),
        json!({"verdict": "UNCLAIMED", "core": "core-fine"}),
    );
    index["a.rs::out#out"]["outside"] = json!(true);
    index["a.rs::moved#moved"]["core"] = json!("core-gone");
    (root, cur, index)
}

#[test]
fn each_way_a_finding_is_read_against_the_base() {
    let (root, cur, index) = classify_rows();
    let q = root.join("research/questions");
    let code = cur.get("a.rs::carry#carry").unwrap().code.clone();
    let base_index = obj(&json!({
        "a.rs::pre#pre": {"verdict": "MISLABELED"},
        "a.rs::carry#carry": {"verdict": "IN-STEP", "code": code},
        "a.rs::out#out": {"verdict": "IN-STEP", "claim": "c"},
        "a.rs::same#same": {"verdict": "IN-STEP", "code": "different"},
    }));
    let cores: HashMap<String, String> = [
        ("newcode", "other"),
        ("resmoved", "core-resmoved"),
        ("stays", "core-stays"),
        ("gone", "core-gone"),
        ("fine", "core-fine"),
    ]
    .iter()
    .map(|(u, c)| (format!("a.rs::{u}"), (*c).to_owned()))
    .collect();
    let base_q = crate::checks::scratch("claims-report-baseq");
    std::fs::copy(q.join("0001-gap.html"), base_q.join("0001-gap.html")).unwrap();
    put(
        &base_q,
        "0002-other.drawing.html",
        "<h2 id=\"other\">Old</h2>\n<p>Old.</p>\n",
    );
    let (deferred, answered) = (
        HashSet::from(["a.rs::deferred".to_owned()]),
        HashSet::from(["a.rs::answered#answered".to_owned()]),
    );
    let base = Base {
        index: &base_index,
        cores: &cores,
        qdir: &base_q,
        deferred: &deferred,
        answered: &answered,
    };
    let (intro, pre, carried) = classify(&cur, &index, &base).unwrap();
    let keys = |v: &[String]| {
        v.iter()
            .map(|l| crate::claims::carry::key_of(l))
            .collect::<Vec<_>>()
    };
    let carried_keys: Vec<&str> = carried.iter().map(|(k, _)| k.as_str()).collect();
    assert_eq!(
        carried_keys,
        vec![
            "a.rs::carry#carry",
            "a.rs::fine#an unclaimed",
            "a.rs::out#out",
            "a.rs::resmoved#resmoved"
        ]
    );
    assert_eq!(
        keys(&intro),
        vec![
            "a.rs::newcode#newcode",
            "a.rs::resonly#resonly",
            "a.rs::same#same"
        ]
    );
    assert_eq!(
        keys(&pre),
        vec![
            "a.rs::fine#plain unclaimed",
            "a.rs::moved#moved",
            "a.rs::pre#pre",
            "a.rs::stays#stays"
        ]
    );
    let same_q = Base { qdir: &q, ..base };
    let (_, pre2, _) = classify(&cur, &index, &same_q).unwrap();
    assert!(keys(&pre2).contains(&"a.rs::resmoved#resmoved".to_owned()));
    let bad = obj(&json!({"a.rs::fine#fine": {}}));
    assert!(classify(&cur, &bad, &same_q).is_err());
}
