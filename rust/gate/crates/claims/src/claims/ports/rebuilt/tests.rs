//! A rebuilt file (feature 449 T152, `ask:449-T152-rebuilt-claims`): the entry's form and its tie to its phase task, the push's
//! refusals, and `claims rekey`'s drop - on rows built in memory; the commands end to end are `ports::flow`'s tests.

use std::collections::{BTreeMap, HashMap, HashSet};
use std::rc::Rc;

use serde_json::{json, Value};

use super::super::{
    carry, carry_deferred, load, say, unported, Before, Map as PortMap, Port, Ports, PORTS,
};
use super::{glob_match, of, refusals, under, Rebuilt};
use crate::claims::commands::Out;
use crate::claims::index::{Cur, Index, Row};
use crate::claims::units::rust_units;
use crate::record::testkit::put;

const FILE: &str = "l7r/diagram/m.py";
const DERIVATION: &str = "specs/9001-x/derivations/T01-m.md";
const NEW: &str = "rust/mode_a/src/m";
const OLD_A: &str = "l7r/diagram/m.py::A#a rule";
const OLD_B: &str = "l7r/diagram/m.py::B#b rule";

/// The phase task's block: `old-code:` naming `words`, and `derivation:` the line `derivation` where given.
fn tasks(old_code: &str, derivation: Option<&str>) -> String {
    let line = derivation.map_or(String::new(), |d| format!("      derivation: {d}\n"));
    format!("# Tasks\n\n- [x] T010 another task\n      old-code: {FILE}\n- [ ] T01 phase: m - rebuilt from its derivation\n      research: rendering\n{line}      old-code: {old_code} rust/x.rs\n- [ ] T02 the next\n      old-code: elsewhere.py\n")
}

/// A tree holding the derivation, the rebuilt module and the task `T01`'s block with `old_code` and `derivation`.
fn tree(tag: &str, old_code: &str, derivation: Option<&str>) -> l7r_shared::tempdir::TempDir {
    let root = crate::checks::scratch(tag);
    put(&root, DERIVATION, "# the derivation\n");
    put(&root, &format!("{NEW}.rs"), "pub fn f() {}\n");
    put(&root, &format!("{NEW}/parts.rs"), "pub fn g() {}\n");
    put(&root, "specs/9001-x/tasks.md", &tasks(old_code, derivation));
    root
}

fn entry(by: &str, to: &Value, derivation: &str) -> String {
    json!({"why": "w", "rebuilt": {FILE: {"by": by, "as": to, "derivation": derivation}}})
        .to_string()
}

fn rebuilt(present: bool) -> Rebuilt {
    Rebuilt {
        by: "9001 T01".to_owned(),
        to: vec![format!("{NEW}.rs"), format!("{NEW}/")],
        derivation: DERIVATION.to_owned(),
        present,
    }
}

fn map(present: bool) -> PortMap {
    PortMap {
        rebuilt: [(FILE.to_owned(), rebuilt(present))].into(),
        ..PortMap::default()
    }
}

#[test]
fn an_entry_tied_to_its_task_is_read() {
    let root = tree("claims-rebuilt-load", "l7r/diagram/*.py", Some(DERIVATION));
    let to = json!([format!("{NEW}.rs"), format!("{NEW}/")]);
    put(&root, PORTS, &entry("9001 T01", &to, DERIVATION));
    assert_eq!(load(&root).unwrap(), map(false));
    // `as` one path; the file named literally; the file still in the tree
    put(
        &root,
        "specs/9001-x/tasks.md",
        &tasks(FILE, Some(DERIVATION)),
    );
    put(&root, PORTS, &entry("9001 T01", &json!(NEW), DERIVATION));
    put(&root, FILE, "x = 1\n");
    let got = load(&root).unwrap().rebuilt;
    assert_eq!(got[FILE].to, [NEW]);
    assert!(got[FILE].present);
    // the archived tasks are read too
    put(&root, "specs/9001-x/tasks.md", "# Tasks\n");
    put(
        &root,
        "specs/9001-x/tasks-done.md",
        &tasks(FILE, Some(DERIVATION)),
    );
    assert!(load(&root).is_ok());
}

/// `load`'s refusal at `root` with `PORTS` holding `doc`.
fn refused(root: &std::path::Path, doc: &str) -> String {
    put(root, PORTS, doc);
    load(root).unwrap_err()
}

#[test]
fn an_entry_not_of_its_form_is_refused() {
    let root = tree("claims-rebuilt-form", FILE, Some(DERIVATION));
    let to = json!(NEW);
    for bad in [
        json!({"rebuilt": {"l7r/diagram/m.md": {"by": "9001 T01", "as": to, "derivation": DERIVATION}}}),
        json!({"rebuilt": {"l7r/diagram/m.py::A.py": {"by": "9001 T01", "as": to, "derivation": DERIVATION}}}),
        json!({"rebuilt": {FILE: {"by": "T01", "as": to, "derivation": DERIVATION}}}),
        json!({"rebuilt": {FILE: {"by": "9001 T01", "derivation": DERIVATION}}}),
        json!({"rebuilt": {FILE: {"by": "9001 T01", "as": [], "derivation": DERIVATION}}}),
        json!({"rebuilt": {FILE: {"by": "9001 T01", "as": [NEW, 3], "derivation": DERIVATION}}}),
        json!({"rebuilt": {FILE: {"by": "9001 T01", "as": "../x", "derivation": DERIVATION}}}),
        json!({"rebuilt": {FILE: {"by": "9001 T01", "as": "/abs", "derivation": DERIVATION}}}),
        json!({"rebuilt": {FILE: {"by": "9001 T01", "as": to, "derivation": " "}}}),
    ] {
        assert!(refused(&root, &bad.to_string()).contains(&format!(
            "the rebuilt entry `{}` is not of the form",
            bad["rebuilt"].as_object().unwrap().keys().next().unwrap()
        )));
    }
}

#[test]
fn an_as_or_a_derivation_not_in_the_tree_is_refused() {
    let root = tree("claims-rebuilt-paths", FILE, Some(DERIVATION));
    // RED: `as` names no path of the tree
    let why = refused(
        &root,
        &entry("9001 T01", &json!([NEW, "rust/gone/"]), DERIVATION),
    );
    assert!(why.contains("names `as` rust/gone/, which is no file or directory in the tree"));
    // RED: the derivation is no file of the tree
    let why = refused(
        &root,
        &entry("9001 T01", &json!(NEW), "specs/9001-x/derivations/T09.md"),
    );
    assert!(why.contains(
        "names the derivation specs/9001-x/derivations/T09.md, which is no file in the tree"
    ));
}

#[test]
fn a_file_not_on_its_tasks_old_code_line_is_refused() {
    // RED: the task's `old-code:` names another file (the task before it names this one, which does not count)
    let root = tree(
        "claims-rebuilt-oldcode",
        "l7r/diagram/other.py l7r/x/*.py",
        Some(DERIVATION),
    );
    let why = refused(&root, &entry("9001 T01", &json!(NEW), DERIVATION));
    assert!(why.contains(&format!("the rebuilt entry `{FILE}` is not on 9001 T01's `old-code:` line, literally or by a glob")), "{why}");
    // RED: `by` names no task of the feature, a feature with no directory, or a tree with no specs
    // a task the feature lacks, and a feature with no directory
    for by in ["9001 T03", "9002 T01"] {
        let why = refused(&root, &entry(by, &json!(NEW), DERIVATION));
        assert!(why.contains(&format!(
            "is rebuilt by {by}, which is no task of its feature's tasks.md or tasks-done.md"
        )));
    }
    // a task id that only opens another's (T0 of T01) is no match
    let why = refused(&root, &entry("9001 T0", &json!(NEW), DERIVATION));
    assert!(why.contains("is rebuilt by 9001 T0, which is no task"));
    std::fs::remove_dir_all(root.join("specs")).unwrap();
    let why = refused(
        &root,
        &entry("9001 T01", &json!(NEW), "rust/mode_a/src/m.rs"),
    );
    assert!(why.contains("which is no task"), "{why}");
}

#[test]
fn a_derivation_other_than_its_tasks_is_refused() {
    // RED: the task's `derivation:` line names another derivation
    let root = tree(
        "claims-rebuilt-derivation",
        FILE,
        Some("specs/9001-x/derivations/T00-old.md"),
    );
    let why = refused(&root, &entry("9001 T01", &json!(NEW), DERIVATION));
    assert!(why.contains(&format!("names the derivation {DERIVATION}, but 9001 T01's block reads specs/9001-x/derivations/T00-old.md")), "{why}");
    // RED: the task's block has no `derivation:` line at all
    put(&root, "specs/9001-x/tasks.md", &tasks(FILE, None));
    let why = refused(&root, &entry("9001 T01", &json!(NEW), DERIVATION));
    assert!(why.contains("but 9001 T01's block has no `derivation:` line"));
}

#[test]
fn a_glob_matches_as_path_glob_would() {
    for (pat, path, want) in [
        (
            "l7r/diagram/labels/*.py",
            "l7r/diagram/labels/placer.py",
            true,
        ),
        (
            "l7r/diagram/labels/*.py",
            "l7r/diagram/labels/x/placer.py",
            false,
        ),
        (
            "l7r/diagram/labels/*.py",
            "l7r/diagram/labels/placer.rs",
            false,
        ),
        (
            "l7r/diagram/compound*.py",
            "l7r/diagram/compound_view.py",
            true,
        ),
        ("l7r/diagram/m?.py", "l7r/diagram/m1.py", true),
        ("l7r/diagram/m?.py", "l7r/diagram/m.py", false),
        ("l7r/**/m.py", "l7r/diagram/x/m.py", true),
        ("l7r/**/m.py", "l7r/m.py", true),
        ("l7r/**", "l7r/a/b.py", true),
        (FILE, FILE, true),
        ("l7r/diagram", FILE, false),
        (FILE, "l7r/diagram", false),
    ] {
        assert_eq!(glob_match(pat, path), want, "{pat} {path}");
    }
}

#[test]
fn as_covers_the_paths_at_and_under_it() {
    let to = rebuilt(false).to;
    assert!(under("rust/mode_a/src/m.rs::f#rule", &to));
    assert!(under("rust/mode_a/src/m/parts.rs::g#rule", &to));
    assert!(under(
        "rust/mode_a/src/m/deep/x.rs::g#rule",
        &[NEW.to_owned()]
    ));
    assert!(!under("rust/mode_a/src/m_other.rs::f#rule", &to));
    assert!(!under("rust/mode_a/src/mx/parts.rs::f#rule", &to));
    assert_eq!(
        of(&map(false).rebuilt, "l7r/diagram/m.py::A"),
        Some(&rebuilt(false))
    );
    assert_eq!(of(&map(false).rebuilt, "l7r/diagram/n.py::A"), None);
}

/// The merge base's rows of two units of the rebuilt file, an UNCLAIMED decision beside them.
fn base() -> Index {
    json!({
        OLD_A: {"verdict": "IN-STEP", "code": "py", "claim": "a rule - NONE: x"},
        OLD_B: {"verdict": "DRIFTED", "code": "py", "claim": "b rule - NONE: y"},
        "l7r/diagram/m.py::B#a decision": {"verdict": "UNCLAIMED", "code": "py"},
    })
    .as_object()
    .unwrap()
    .clone()
}

/// The tree's rows: the rebuilt module's own claims.
fn cur() -> Cur {
    let mut cur = Cur::default();
    let src = "/// Research: c rule - NONE: the rebuilt code's own\npub fn f() {}\n";
    for u in rust_units(src, "rust/mode_a/src/m.rs").1 {
        let u = Rc::new(u);
        for c in &u.claims {
            cur.insert(Row {
                key: u.key(c),
                code: u.code(c),
                unit: u.clone(),
                claim: c.clone(),
                research: String::new(),
            });
        }
    }
    cur
}

/// No claim text from the merge base: the rows here hold their own, but the one the precedence test strips.
fn no_text(_: &str) -> Option<String> {
    None
}

/// What the push says of the rebuilt file's claims, `owed` the tree's owed keys and `now` its index.
fn push(map: &PortMap, owed: &[String], now: &Index) -> Vec<String> {
    let base = base();
    let uids: HashSet<String> = base
        .keys()
        .map(|k| k.rsplit_once('#').unwrap().0.to_owned())
        .collect();
    let texts = HashMap::new();
    let before = Before {
        index: &base,
        uids: &uids,
        texts: &texts,
        owed,
    };
    unported(&cur(), now, &before, map, &mut |_: &str| true)
}

#[test]
fn a_file_not_listed_is_refused_naming_rebuilt() {
    // RED: no entry for the file
    let got = push(&PortMap::default(), &[], &Index::new());
    assert_eq!(got.len(), 2);
    assert!(got[0].starts_with(&format!("unported: {OLD_A} - its unit l7r/diagram/m.py::A is deleted, and dev/claims-ports.json maps it to no unit")));
    assert!(got[0].contains("name the file under `rebuilt` (`\"<path>.py\": {\"by\": \"<feature> <task>\", \"as\": \"<the Rust module doing its job now>\", \"derivation\": \"<the task's derivation>\"}`, the file on that task's `old-code:` line, ask:449-T152-rebuilt-claims)"), "{}", got[0]);
}

#[test]
fn an_owed_claim_under_as_is_refused() {
    // RED: the rebuilt code's own claim still owed (one owed elsewhere does not count)
    let owed = [
        "rust/mode_a/src/m.rs::f#c rule".to_owned(),
        "rust/other.rs::g#x".to_owned(),
    ];
    assert_eq!(
        push(&map(false), &owed, &Index::new()),
        ["unported: 2 claim(s) of l7r/diagram/m.py, rebuilt by 9001 T01 as rust/mode_a/src/m.rs, rust/mode_a/src/m/ - 1 claim(s) of the rebuilt code still owed (first rust/mode_a/src/m.rs::f#c rule): its old claims go only once the code doing its job now is checked - `make claims-owed`, then the claims round (ask:449-T152-rebuilt-claims)"]
    );
    // and with nothing owed under `as`, none
    assert!(push(&map(false), &owed[1..], &Index::new()).is_empty());
}

#[test]
fn a_listed_file_still_present_is_refused() {
    // RED: the file still in the tree; its units' claims wait on it, not on the owed
    let owed = ["rust/mode_a/src/m.rs::f#c rule".to_owned()];
    assert_eq!(
        push(&map(true), &owed, &Index::new()),
        ["unported: l7r/diagram/m.py - rebuilt (9001 T01) but still present: dev/claims-ports.json's `rebuilt` names a file deleted once 9001 T01 rebuilt its job as rust/mode_a/src/m.rs, rust/mode_a/src/m/; delete the file, or take it out of `rebuilt`"]
    );
    // and a present file whose claims the push does not reach (none stranded) is refused alone
    assert_eq!(
        refusals(&map(true).rebuilt, &BTreeMap::new(), &[], &str::is_empty).len(),
        1
    );
    // a stranded file with no entry (never reached by `unported`) is passed over
    let stranded = BTreeMap::from([("l7r/diagram/n.py".to_owned(), vec!["k".to_owned()])]);
    assert!(refusals(&map(false).rebuilt, &stranded, &[], &str::is_empty).is_empty());
}

#[test]
fn a_listed_file_whose_rebuilt_module_is_all_checked_passes_once_its_rows_drop() {
    // its rows still in the index: `make claims-rekey`
    let mut now = base();
    assert_eq!(
        push(&map(false), &[], &now),
        [format!("unported: 2 claim row(s) of {FILE}, rebuilt by 9001 T01 ({DERIVATION}), not yet dropped: `make claims-rekey` (make land runs it)")]
    );
    // the carry drops both claims' rows and keeps the UNCLAIMED one
    let done = carry(&cur(), &mut now, &map(false), &mut no_text);
    assert_eq!(done.rebuilt, [OLD_A, OLD_B]);
    assert_eq!(done.rebuilt_derivations, [DERIVATION.to_owned()].into());
    assert!(now.contains_key("l7r/diagram/m.py::B#a decision") && now.len() == 1);
    // GREEN: the push lets them go
    assert!(push(&map(false), &[], &now).is_empty());
    // what rekey says of it: the count and the derivation
    let mut o = Out::default();
    assert_eq!(say(&done, &mut o), 0);
    assert_eq!(o.out, format!("claims-rekey: 2 claim row(s) of a rebuilt file dropped (dev/claims-ports.json's `rebuilt`), its job rebuilt from {DERIVATION}, the rebuilt code's own claims each checked fresh (ask:449-T152-rebuilt-claims)\n"));
    // the deferred list drops its units and keys; a present file's are kept
    let mut d = json!({"why": "w", "units": ["l7r/diagram/m.py::A", "l7r/diagram/x.py::f"], "keys": [OLD_B]});
    assert!(!carry_deferred(&mut d.clone(), &map(true), &cur()));
    assert!(carry_deferred(&mut d, &map(false), &cur()));
    assert_eq!(
        d,
        json!({"why": "w", "units": ["l7r/diagram/x.py::f"], "keys": []})
    );
    // a present file's rows are not dropped
    let mut kept = base();
    assert!(carry(&cur(), &mut kept, &map(true), &mut no_text)
        .rebuilt
        .is_empty());
    assert_eq!(kept.len(), 3);
}

#[test]
fn a_unit_with_its_own_port_is_carried_there_not_dropped() {
    // condition 2: `A` is ported; only `B` goes with the rebuilt file
    let mut map = map(false);
    let ports: Ports = [(
        "l7r/diagram/m.py::A".to_owned(),
        Port {
            to: "rust/mode_a/src/m.rs::f".to_owned(),
            by: "9001 T00".to_owned(),
            ..Port::default()
        },
    )]
    .into();
    map.ports = ports;
    let mut now = base();
    // its row without its text, so the port's carry asks the merge base for it
    now[OLD_A].as_object_mut().unwrap().remove("claim");
    let done = carry(&cur(), &mut now, &map, &mut no_text);
    assert_eq!(done.rebuilt, [OLD_B]);
    assert_eq!(done.stuck.len(), 1, "{:?}", done.stuck);
    assert!(done.stuck[0].starts_with(&format!(
        "unported: {OLD_A} - its claim's text is in neither its index row nor the merge base"
    )));
    let mut d = json!({"units": ["l7r/diagram/m.py::A", "l7r/diagram/m.py::B"]});
    assert!(carry_deferred(&mut d, &map, &cur()));
    assert_eq!(d, json!({"units": ["rust/mode_a/src/m.rs::f"]}));
}
