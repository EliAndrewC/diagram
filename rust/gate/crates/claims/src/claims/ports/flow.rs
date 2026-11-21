//! A port's cut end to end (feature 449 T166, Q10) on a scratch repository through the commands: the push refuses a claim on a deleted
//! `.py` unit no port carried; the map declared, `claims rekey` carries each row onto its port, owed a full check; the claims round
//! checks it and the push passes. Each test makes one or two command calls on an index written as a check would have recorded it, so
//! each runs in about a tenth of a second (feature 449 T99's bound).

use serde_json::{json, Map, Value};

use super::PORTS;
use crate::claims::index::rows_of;
use crate::claims::tests::{claims, fixture_with, py_units};
use crate::claims::units::{all_rust_units, doc_units, from_json, Pair, PROCEDURES};
use crate::record::testkit::{git, put};

/// The page a research claim points to, built from parts so the test holds no pointer of its own.
fn span_line() -> String {
    let page = ["research", "questions", "0001-gap.html"].join("/");
    format!("span - {page}: 12 ft")
}

const HELPER: &str = "helper - NONE: plumbing";
const SPAN: &str = "l7r/diagram/m.py::SPAN#span";
const NEW_SPAN: &str = "rust/mode_a/src/lib.rs::SPAN#span";
const NEW_HELPER: &str = "rust/mode_a/src/lib.rs::helper#helper";

fn index(root: &std::path::Path) -> Value {
    serde_json::from_str(&std::fs::read_to_string(root.join("dev/claims-index.json")).unwrap())
        .unwrap()
}

/// Every claim of the tree recorded IN-STEP as a check records it, written in process (no command, no runner): the Rust and the
/// procedures read here, the Python's `SPAN` and `helper` as the stub answers them (`core-<qualname>`) while `python` holds.
fn recorded(root: &std::path::Path, python: bool) -> Map<String, Value> {
    let mut pairs: Vec<Pair> = all_rust_units(root, "", true).unwrap();
    for (doc, tops) in PROCEDURES {
        if let Ok(text) = std::fs::read_to_string(root.join(doc)) {
            pairs.extend(
                doc_units(&text, doc, tops)
                    .into_iter()
                    .map(|u| (u, Vec::new())),
            );
        }
    }
    let span = span_line();
    if python {
        for (q, line) in [("SPAN", span.as_str()), ("helper", HELPER)] {
            pairs.push(from_json(
                &json!({"path": "l7r/diagram/m.py", "qualname": q, "kind": "function",
                "claims": [line], "core": format!("core-{q}")}),
            ));
        }
    }
    let cur = rows_of(pairs, &root.join("research/questions")).unwrap();
    cur.iter()
        .map(|r| {
            let row = json!({"code": r.code, "research": r.research, "claim": r.claim.normalized(), "verdict": "IN-STEP"});
            (r.key.clone(), row)
        })
        .collect()
}

/// A tree whose Python units `SPAN` and `helper`, checked at its merge base (the base as `at_base` leaves it, the tree and its rows),
/// are ported to `rust/mode_a` and deleted.
fn cut(
    tag: &str,
    at_base: &dyn Fn(&std::path::Path, &mut Map<String, Value>),
) -> l7r_shared::tempdir::TempDir {
    let span = span_line();
    let root = fixture_with(tag, &|root| {
        py_units(
            root,
            &[
                ("SPAN", "function", &[span.as_str()], false),
                ("helper", "function", &[HELPER], false),
            ],
            &[],
        );
        let mut rows = recorded(root, true);
        at_base(root, &mut rows);
        // the merge base's Python half answered from the kept answers, as a run that read it before would be (no runner started)
        let answer: Value =
            serde_json::from_str(&std::fs::read_to_string(root.join("l7r/py-units.json")).unwrap())
                .unwrap();
        crate::claims::scope::keep_answer(root, root, true, true, answer);
        put(
            root,
            "dev/claims-index.json",
            &Value::Object(rows).to_string(),
        );
        put(
            root,
            "dev/claims-deferred.json",
            "{\"why\": \"w\", \"units\": [\"l7r/diagram/m.py::helper\"]}\n",
        );
    });
    put(&root, "rust/mode_a/src/lib.rs", &format!("/// Research: {span}\npub const SPAN: f64 = 12.0;\n/// Research: {HELPER}\npub fn helper() {{}}\n"));
    // the Python deleted: the tree holds no `.py` file, so its Python half is asked nothing
    std::fs::remove_file(root.join("l7r/diagram/m.py")).unwrap();
    root
}

fn map(root: &std::path::Path) {
    put(
        root,
        PORTS,
        &json!({"why": "w", "ports": {
            "l7r/diagram/m.py::SPAN": {"to": "rust/mode_a/src/lib.rs::SPAN", "by": "449 T999"},
            "l7r/diagram/m.py::helper": {"to": "rust/mode_a/src/lib.rs::helper", "by": "449 T999"},
        }})
        .to_string(),
    );
}

/// The index as `rekey` leaves it: each Python row re-keyed onto its port, its code the Python's, its old key recorded.
fn carried(root: &std::path::Path) {
    let mut rows = index(root).as_object().unwrap().clone();
    for (old, new) in [
        (SPAN, NEW_SPAN),
        ("l7r/diagram/m.py::helper#helper", NEW_HELPER),
    ] {
        let mut row = rows.shift_remove(old).unwrap();
        row["ported"] = json!(old);
        rows.insert(new.to_owned(), row);
    }
    put(
        root,
        "dev/claims-index.json",
        &Value::Object(rows).to_string(),
    );
}

/// What the push's claims gate reads of the tree, in process: (its refusals, the introduced, the pre-existing).
fn push(root: &std::path::Path) -> (Vec<String>, Vec<String>, Vec<String>) {
    let mut reader = crate::claims::scope::Reader::new(root, root);
    let pairs = crate::claims::scope::all_units(&mut reader, root, false, true).unwrap();
    let at = crate::claims::carry::Reading {
        cur: rows_of(pairs, &root.join("research/questions")).unwrap(),
        index: index(root).as_object().unwrap().clone(),
    };
    let (refuse, intro, pre, _) = crate::claims::carry::classified(&mut reader, root, &at).unwrap();
    (refuse, intro, pre)
}

#[test]
fn an_unmapped_deletion_is_refused_with_its_fix() {
    let root = cut("claims-ports-unmapped", &|_, _| {});
    let refuse = push(&root).0;
    assert!(refuse.iter().any(|l| l.starts_with("unported: l7r/diagram/m.py::SPAN#span - its unit l7r/diagram/m.py::SPAN is deleted, and dev/claims-ports.json maps it to no unit")));
}

#[test]
fn the_map_carries_each_row_onto_its_port() {
    let root = cut("claims-ports-carry", &|_, _| {});
    map(&root);
    let got = claims(&root, &["rekey"]);
    assert_eq!(got.code, 0);
    assert!(got
        .stdout
        .contains("claims-rekey: 2 claim row(s) carried to their port"));
    let ix = index(&root);
    assert_eq!(ix[NEW_SPAN]["ported"], SPAN);
    assert!(ix.get(SPAN).is_none());
    assert_eq!(
        std::fs::read_to_string(root.join("dev/claims-deferred.json")).unwrap(),
        "{\n \"why\": \"w\",\n \"units\": [\n  \"rust/mode_a/src/lib.rs::helper\"\n ]\n}\n"
    );
}

#[test]
fn a_carried_row_is_owed_a_full_check() {
    let root = cut("claims-ports-owed", &|_, _| {});
    map(&root);
    carried(&root);
    let got = claims(&root, &["owed"]);
    assert!(got.stdout.contains(&format!(
        "ported           {NEW_SPAN}\nported           {NEW_HELPER}\n"
    )));
}

#[test]
fn a_carried_row_owes_no_triage_a_triage_could_clear() {
    let root = cut("claims-ports-triage", &|_, _| {});
    map(&root);
    carried(&root);
    assert_eq!(
        claims(&root, &["triage"]).stdout,
        "claims-triage: no claim is owed a triage\n"
    );
}

#[test]
fn a_row_without_its_text_reads_it_from_the_merge_base() {
    let root = cut("claims-ports-base", &|_, rows| {
        rows[SPAN].as_object_mut().unwrap().remove("claim");
    });
    map(&root);
    // and a tree with no deferred list carries none
    std::fs::remove_file(root.join("dev/claims-deferred.json")).unwrap();
    let got = claims(&root, &["rekey"]);
    assert_eq!(got.code, 0);
    assert_eq!(index(&root)[NEW_SPAN]["ported"], SPAN);
}

#[test]
fn a_row_whose_text_nothing_holds_is_left_with_its_fix() {
    // its row recorded without the text, and the merge base's Python reading no such claim
    let root = cut("claims-ports-nobase", &|root, rows| {
        rows[SPAN].as_object_mut().unwrap().remove("claim");
        py_units(root, &[("helper", "function", &[HELPER], false)], &[]);
    });
    map(&root);
    let got = claims(&root, &["rekey"]);
    assert_eq!(got.code, 1);
    assert!(got.stdout.contains("unported: l7r/diagram/m.py::SPAN#span - its claim's text is in neither its index row nor the merge base"));
}

#[test]
fn a_carried_finding_reads_as_pre_existing_and_its_claim_owes_a_check() {
    let root = cut("claims-ports-gate", &|_, rows| {
        rows[SPAN]["verdict"] = json!("DRIFTED");
    });
    map(&root);
    carried(&root);
    let (refuse, _, pre) = push(&root);
    assert!(!refuse.iter().any(|l| l.starts_with("unported")));
    assert!(refuse.contains(&format!("owed (ported): {NEW_SPAN}")));
    assert!(pre
        .iter()
        .any(|l| l.starts_with("DRIFTED") && l.contains(NEW_SPAN)));
}

#[test]
fn a_port_checked_by_its_round_lands() {
    let root = cut("claims-ports-checked", &|_, _| {});
    map(&root);
    // the index as the round leaves it: every claim recorded at its code now, the ported rows keeping their old key
    let mut rows = recorded(&root, false);
    rows[NEW_SPAN]["ported"] = json!(SPAN);
    put(
        &root,
        "dev/claims-index.json",
        &Value::Object(rows).to_string(),
    );
    assert_eq!(push(&root), (Vec::new(), Vec::new(), Vec::new()));
}

#[test]
fn a_second_rekey_finds_nothing_left_to_carry() {
    let root = cut("claims-ports-again", &|_, _| {});
    map(&root);
    carried(&root);
    // the deferred list as it was left
    put(
        &root,
        "dev/claims-deferred.json",
        "{\"why\": \"w\", \"units\": [\"rust/mode_a/src/lib.rs::helper\"]}\n",
    );
    let again = claims(&root, &["rekey"]);
    assert_eq!(
        again.stdout,
        "claims-rekey: 0 claim row(s) carried to the file their unit moved to\n"
    );
}

#[test]
fn a_tree_with_no_commit_has_no_base_to_read() {
    let root = crate::checks::scratch("claims-ports-nohead");
    git(&root, &["init", "-q"]);
    let mut reader = crate::claims::scope::Reader::new(&root, &root);
    assert!(super::base_texts(&mut reader, &root).unwrap().is_empty());
}

/// The map retiring both deleted units (feature 449 T184, `ask:449-T184-elongated-retired`, `ask:449-T184-elongated-retired-2`), with
/// no port, each naming its own claim's row as the finding against it.
fn retire(root: &std::path::Path) {
    let page = ["research", "questions", "0001-gap.html"].join("/");
    let entry = |finding: &str| json!({"by": "449 T999", "page": page, "why": "the page overrules its rule", "finding": finding});
    put(
        root,
        PORTS,
        &json!({"why": "w", "retired": {"l7r/diagram/m.py::SPAN": entry(SPAN), "l7r/diagram/m.py::helper": entry("l7r/diagram/m.py::helper#helper")}})
            .to_string(),
    );
}

#[test]
fn a_retired_claim_found_drifted_is_dropped_by_rekey_and_lands() {
    let root = cut("claims-ports-retired", &|_, rows| {
        for k in [SPAN, "l7r/diagram/m.py::helper#helper"] {
            rows[k]["verdict"] = json!("DRIFTED");
        }
    });
    retire(&root);
    assert!(push(&root).0.iter().any(|l| l
        .starts_with(&format!("unported: {SPAN} - its unit is retired"))
        && l.ends_with("`make claims-rekey` (make land runs it)")));
    let got = claims(&root, &["rekey"]);
    assert_eq!(got.code, 0, "{}", got.stdout);
    assert!(got.stdout.contains("claims-rekey: 2 claim row(s) of a retired unit dropped (dev/claims-ports.json's `retired`), its rule overruled by research/questions/0001-gap.html"), "{}", got.stdout);
    let ix = index(&root);
    assert!(ix.get(SPAN).is_none() && ix.get("l7r/diagram/m.py::helper#helper").is_none());
    assert_eq!(
        std::fs::read_to_string(root.join("dev/claims-deferred.json")).unwrap(),
        "{\n \"why\": \"w\",\n \"units\": []\n}\n"
    );
    assert!(!push(&root).0.iter().any(|l| l.starts_with("unported")));
}

#[test]
fn a_retired_claim_found_in_step_is_refused_at_the_push() {
    let root = cut("claims-ports-retired-instep", &|_, _| {});
    retire(&root);
    assert_eq!(claims(&root, &["rekey"]).code, 0);
    let refuse = push(&root).0;
    assert!(refuse.iter().any(|l| l.starts_with(&format!(
        "unported: {SPAN} - dev/claims-ports.json retires its unit"
    )) && l
        .contains("reads IN-STEP at the merge base: retire only a claim whose claims round found the research against it")),);
}

/// The map naming the deleted `m.py` rebuilt (feature 449 T152, `ask:449-T152-rebuilt-claims`) by the phase task `449 T999`, whose
/// block names it on its `old-code:` line, as the module `rust/mode_a/src/lib.rs`, from its derivation.
fn rebuild(root: &std::path::Path) {
    let derivation = "specs/449-x/derivations/T999-m.md";
    put(root, derivation, "# the derivation\n");
    put(root, "specs/449-x/tasks.md", &format!("# Tasks\n\n- [ ] T999 phase: m - rebuilt\n      derivation: {derivation}\n      old-code: l7r/diagram/*.py\n"));
    put(
        root,
        PORTS,
        &json!({"why": "w", "rebuilt": {"l7r/diagram/m.py": {"by": "449 T999", "as": "rust/mode_a/src/lib.rs", "derivation": derivation}}})
            .to_string(),
    );
}

#[test]
fn a_rebuilt_files_claims_go_once_its_module_is_checked_and_rekey_drops_them() {
    let root = cut("claims-ports-rebuilt", &|_, _| {});
    rebuild(&root);
    // the rebuilt module's own claims new, so owed: the old claims wait on them
    let refuse = push(&root).0;
    assert!(refuse.iter().any(|l| l.starts_with("unported: 2 claim(s) of l7r/diagram/m.py, rebuilt by 449 T999 as rust/mode_a/src/lib.rs - 2 claim(s) of the rebuilt code still owed")), "{refuse:?}");
    // the round checks the rebuilt module; the old rows still stand
    let mut rows = index(&root).as_object().unwrap().clone();
    rows.extend(recorded(&root, false));
    put(
        &root,
        "dev/claims-index.json",
        &Value::Object(rows).to_string(),
    );
    let refuse = push(&root).0;
    assert_eq!(refuse, ["unported: 2 claim row(s) of l7r/diagram/m.py, rebuilt by 449 T999 (specs/449-x/derivations/T999-m.md), not yet dropped: `make claims-rekey` (make land runs it)"]);
    let got = claims(&root, &["rekey"]);
    assert_eq!(got.code, 0, "{}", got.stdout);
    assert!(got.stdout.contains("claims-rekey: 2 claim row(s) of a rebuilt file dropped (dev/claims-ports.json's `rebuilt`), its job rebuilt from specs/449-x/derivations/T999-m.md"), "{}", got.stdout);
    assert!(index(&root).get(SPAN).is_none());
    assert_eq!(
        std::fs::read_to_string(root.join("dev/claims-deferred.json")).unwrap(),
        "{\n \"why\": \"w\",\n \"units\": []\n}\n"
    );
    assert_eq!(push(&root), (Vec::new(), Vec::new(), Vec::new()));
}
