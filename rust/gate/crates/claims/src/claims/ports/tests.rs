//! A claim carried across a port (feature 449 T166, Q10): the map's form, each claim's fate, the carry of the index and the deferred
//! list, and the push's refusal of a claim on a deleted unit no port carried - on rows built in memory; the commands end to end are
//! `ports::flow`'s tests.

use std::collections::{HashMap, HashSet};
use std::rc::Rc;

use serde_json::{json, Map, Value};

use super::{
    carry, carry_deferred, fate, load, save_deferred, say, unported, Before, Fate, Port, Ports,
    Rekeyed, PORTS,
};
use crate::claims::commands::Out;
use crate::claims::grammar::parse_claim;
use crate::claims::index::{Cur, Index, Row};
use crate::claims::units::rust_units;
use crate::record::testkit::put;

/// The page a research claim points to, built from parts so the test holds no pointer of its own.
fn page() -> String {
    ["research", "questions", "0001-gap.html"].join("/")
}

fn span_line() -> String {
    format!("span - {}: 12 ft", page())
}

/// The port: a constant carrying the Python's research claim, a function its NONE claim, one more reading another claim.
fn port_src() -> String {
    format!("/// Research: {}\npub const SPAN: f64 = 12.0;\n/// Research: helper - NONE: plumbing\npub fn helper() {{}}\n/// Research: other - NONE: a different claim\npub fn other() {{}}\n", span_line())
}

fn cur() -> Cur {
    let mut cur = Cur::default();
    for u in rust_units(&port_src(), "rust/mode_a/src/lib.rs").1 {
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

fn norm(line: &str) -> String {
    parse_claim(line).unwrap().normalized()
}

fn port(to: &str) -> Port {
    Port {
        to: to.to_owned(),
        by: "449 T999".to_owned(),
    }
}

fn ports() -> Ports {
    Ports::from([
        (
            "l7r/diagram/m.py::SPAN".to_owned(),
            port("rust/mode_a/src/lib.rs::SPAN"),
        ),
        (
            "l7r/diagram/m.py::helper".to_owned(),
            port("rust/mode_a/src/lib.rs::helper"),
        ),
        (
            "l7r/diagram/m.py::tool".to_owned(),
            port("rust/gate/src/lib.rs::tool"),
        ),
        (
            "l7r/diagram/m.py::lost".to_owned(),
            port("rust/mode_a/src/lib.rs::other"),
        ),
    ])
}

#[test]
fn the_map_is_read_with_its_form_held() {
    let root = crate::checks::scratch("claims-ports-load");
    assert!(load(&root).unwrap().is_empty());
    put(&root, PORTS, "{\"why\": \"w\", \"ports\": {\"l7r/diagram/m.py::SPAN\": {\"to\": \"rust/mode_a/src/lib.rs::SPAN\", \"by\": \"449 T999\"}}}");
    assert_eq!(
        load(&root).unwrap()["l7r/diagram/m.py::SPAN"],
        port("rust/mode_a/src/lib.rs::SPAN")
    );
    put(&root, PORTS, "{\"why\": \"w\"}");
    assert!(load(&root).unwrap().is_empty());
    for bad in [
        "{\"ports\": {\"docs/x.md::A\": {\"to\": \"r::A\", \"by\": \"t\"}}}",
        "{\"ports\": {\"m.py::A\": {\"to\": \"nothing\", \"by\": \"t\"}}}",
        "{\"ports\": {\"m.py::A\": {\"to\": \"r::A\", \"by\": \" \"}}}",
    ] {
        put(&root, PORTS, bad);
        assert!(load(&root).unwrap_err().contains("is not of the form"));
    }
    put(&root, PORTS, "{");
    assert!(load(&root).unwrap_err().contains("JSONDecodeError"));
}

#[test]
fn each_claim_meets_its_fate() {
    let cur = cur();
    let p = ports();
    let span = span_line();
    let at = |k: &str, text: Option<&str>| {
        fate(
            k,
            &p[k.rsplit_once('#').unwrap().0],
            &cur,
            text.map(norm).as_deref(),
        )
    };
    assert_eq!(
        at("l7r/diagram/m.py::SPAN#span", Some(&span)),
        Fate::Carried("rust/mode_a/src/lib.rs::SPAN#span".to_owned())
    );
    let why = format!("{:?}", at("l7r/diagram/m.py::SPAN#span", None));
    assert!(why.contains("its claim's text is in neither its index row nor the merge base"));
    let why = format!(
        "{:?}",
        at("l7r/diagram/m.py::SPAN#span", Some("span - NONE: plumbing"))
    );
    assert!(why.contains("carries the label `span` but reads"),);
    let why = format!(
        "{:?}",
        at("l7r/diagram/m.py::lost#lost", Some("lost - NONE: x"))
    );
    assert!(why.contains("carries no claim `lost`: carry the Python's `Research:` line onto it as it stands (`/// Research: lost - NONE: x`)"), );
    // a NONE claim ported into a tooling crate is dropped (ask:449-T148-claims); one citing research there is a new ask
    assert_eq!(
        at("l7r/diagram/m.py::tool#tool", Some("tool - NONE: plumbing")),
        Fate::Dropped
    );
    let why = format!("{:?}", at("l7r/diagram/m.py::tool#tool", Some(&span)));
    assert!(
        why.contains("a tooling crate the claims walk prunes, and it cites research: a new ask")
    );
    let nowhere = port("rust/mode_a/src/lib.rs::gone");
    let why = format!(
        "{:?}",
        fate("l7r/diagram/m.py::x#x", &nowhere, &cur, Some("x - NONE"))
    );
    assert!(why.contains("which is no unit the claims walk reads"));
}

fn index() -> Index {
    json!({
        "l7r/diagram/m.py::SPAN#span": {"verdict": "IN-STEP", "code": "py", "note": "checked", "pages": {"0001-gap.html": "fp"}},
        "l7r/diagram/m.py::helper#helper": {"verdict": "DRIFTED", "code": "py", "claim": norm("helper - NONE: plumbing")},
        "l7r/diagram/m.py::tool#tool": {"verdict": "IN-STEP", "code": "py", "claim": norm("tool - NONE: plumbing")},
        "l7r/diagram/m.py::lost#lost": {"verdict": "IN-STEP", "code": "py", "claim": norm("lost - NONE: x")},
        "l7r/diagram/m.py::lost#a decision": {"verdict": "UNCLAIMED", "code": "py"},
        "l7r/diagram/m.py::kept#kept": {"verdict": "IN-STEP", "code": "py"},
        "rust/mode_a/src/lib.rs::SPAN#span": {"verdict": "IN-STEP", "code": "checked-already"},
    })
    .as_object()
    .unwrap()
    .clone()
}

#[test]
fn the_carry_rekeys_drops_and_leaves_each_row() {
    let cur = cur();
    let mut idx = index();
    idx.shift_remove("rust/mode_a/src/lib.rs::SPAN#span");
    let mut asked = Vec::new();
    let span = norm(&span_line());
    let done = carry(&cur, &mut idx, &ports(), &mut |k: &str| {
        asked.push(k.to_owned());
        Some(span.clone())
    });
    // the row without its text read it from the base; its verdict, note and pages kept, its old key recorded
    assert_eq!(asked, ["l7r/diagram/m.py::SPAN#span"]);
    assert_eq!(
        done.carried,
        [
            "l7r/diagram/m.py::SPAN#span",
            "l7r/diagram/m.py::helper#helper"
        ]
    );
    assert_eq!(done.dropped, ["l7r/diagram/m.py::tool#tool"]);
    assert_eq!(done.stuck.len(), 1);
    assert!(done.stuck[0].starts_with("unported: l7r/diagram/m.py::lost#lost"));
    let row = &idx["rust/mode_a/src/lib.rs::SPAN#span"];
    assert_eq!(
        (
            row["verdict"].as_str(),
            row["note"].as_str(),
            row["code"].as_str()
        ),
        (Some("IN-STEP"), Some("checked"), Some("py"))
    );
    assert_eq!(row["pages"], json!({"0001-gap.html": "fp"}));
    assert_eq!(row["ported"], "l7r/diagram/m.py::SPAN#span");
    assert_eq!(
        idx["rust/mode_a/src/lib.rs::helper#helper"]["ported"],
        "l7r/diagram/m.py::helper#helper"
    );
    for gone in ["l7r/diagram/m.py::SPAN#span", "l7r/diagram/m.py::tool#tool"] {
        assert!(!idx.contains_key(gone));
    }
    // left: the stuck row, an UNCLAIMED row, an unmapped unit's
    for left in [
        "l7r/diagram/m.py::lost#lost",
        "l7r/diagram/m.py::lost#a decision",
        "l7r/diagram/m.py::kept#kept",
    ] {
        assert!(idx.contains_key(left));
    }
    // a row the port's own check already wrote stands, and the old one goes
    let mut idx = index();
    let done = carry(&cur, &mut idx, &ports(), &mut |_: &str| {
        Some(norm(&span_line()))
    });
    assert_eq!(done.carried.len(), 2);
    assert_eq!(
        idx["rust/mode_a/src/lib.rs::SPAN#span"],
        json!({"verdict": "IN-STEP", "code": "checked-already"})
    );
}

#[test]
fn what_rekey_says_and_its_exit() {
    let mut o = Out::default();
    assert_eq!(say(&Rekeyed::default(), &mut o), 0);
    assert_eq!(o.out, "");
    let done = Rekeyed {
        carried: vec!["a".into()],
        dropped: vec![],
        stuck: vec!["unported: b - why".into()],
    };
    assert_eq!(say(&done, &mut o), 1);
    assert_eq!(o.out, "claims-rekey: 1 claim row(s) carried to their port (dev/claims-ports.json), each owed a full check of its new code (ported); 0 dropped, a claim of NONE research ported into a tooling crate (ask:449-T148-claims)\nclaims-rekey: unported: b - why\n");
}

#[test]
fn the_deferred_list_follows_its_units() {
    let root = crate::checks::scratch("claims-ports-deferred");
    let mut d = json!({"why": "w", "units": ["l7r/diagram/m.py::SPAN", "l7r/diagram/m.py::tool", "l7r/diagram/x.py::f"],
        "keys": ["l7r/diagram/m.py::helper#helper"]});
    assert!(carry_deferred(&mut d, &ports(), &cur()));
    assert_eq!(
        d,
        json!({"why": "w", "units": ["rust/mode_a/src/lib.rs::SPAN", "l7r/diagram/x.py::f"],
        "keys": ["rust/mode_a/src/lib.rs::helper#helper"]})
    );
    assert!(!carry_deferred(&mut d, &ports(), &cur()));
    assert!(!carry_deferred(&mut json!({"why": "w"}), &ports(), &cur()));
    std::fs::create_dir_all(root.join("dev")).unwrap();
    save_deferred(&root, &d).unwrap();
    // written as the list is kept: `json.dumps(indent=1)`, its keys in their order
    assert_eq!(
        std::fs::read_to_string(root.join("dev/claims-deferred.json")).unwrap(),
        "{\n \"why\": \"w\",\n \"units\": [\n  \"rust/mode_a/src/lib.rs::SPAN\",\n  \"l7r/diagram/x.py::f\"\n ],\n \"keys\": [\n  \"rust/mode_a/src/lib.rs::helper#helper\"\n ]\n}\n"
    );
    assert!(save_deferred(&root.join("no/such"), &d).is_err());
}

#[test]
fn the_push_refuses_a_claim_on_a_deleted_unit_no_port_carried() {
    let cur = cur();
    let base = index();
    let uids: HashSet<String> = base
        .keys()
        .map(|k| k.rsplit_once('#').unwrap().0.to_owned())
        .collect();
    let texts = HashMap::from([("l7r/diagram/m.py::SPAN#span".to_owned(), norm(&span_line()))]);
    let before = Before {
        index: &base,
        uids: &uids,
        texts: &texts,
    };
    let unmapped = Ports::new();
    let mut all_gone = |_: &str| true;
    let got = unported(&cur, &base, &before, &unmapped, &mut all_gone);
    // every claimed row of a deleted `.py` unit, its UNCLAIMED row and the Rust row aside
    assert_eq!(got.len(), 5, "{got:?}");
    assert!(got[0].starts_with("unported: l7r/diagram/m.py::SPAN#span - its unit l7r/diagram/m.py::SPAN is deleted, and dev/claims-ports.json maps it to no unit: if it was ported, add `\"l7r/diagram/m.py::SPAN\": {\"to\": \"rust/<crate>/src/<file>.rs::<item>\", \"by\": \"<feature> <task>\"}` under its `ports`"), "{}", got[0]);
    // a unit still in another scope is not deleted
    assert!(unported(&cur, &base, &before, &unmapped, &mut |_: &str| false).is_empty());
    // mapped, not yet carried: rekey; carried or dropped: nothing; stuck: its fix; unmapped: the map's
    let got = unported(&cur, &base, &before, &ports(), &mut all_gone);
    assert_eq!(got.len(), 5, "{got:?}");
    for line in &got[..3] {
        assert!(line.ends_with("its port is mapped but its row not yet carried: `make claims-rekey` (make land runs it)"));
    }
    assert!(got[3].contains("carries no claim `lost`"));
    assert!(got[4].starts_with("unported: l7r/diagram/m.py::kept#kept - its unit"));
    let mut now = index();
    let done = carry(&cur, &mut now, &ports(), &mut |_: &str| {
        Some(norm(&span_line()))
    });
    assert_eq!(done.carried.len(), 2);
    let got = unported(&cur, &now, &before, &ports(), &mut all_gone);
    assert_eq!(got.len(), 2, "{got:?}");
    // a carried row a record already pruned leaves its port's claim owed as new: no carry is left to run
    let mut pruned: Map<String, Value> = now.clone();
    pruned.shift_remove("rust/mode_a/src/lib.rs::helper#helper");
    assert_eq!(
        unported(&cur, &pruned, &before, &ports(), &mut all_gone).len(),
        2
    );
}

/// The claims round's record keeps a carried row's old key on the row it writes, so the push reads its finding against the Python's.
#[test]
fn the_round_records_a_carried_claim_keeping_its_old_key() {
    let key = "rust/mode_a/src/lib.rs::SPAN#span";
    let index =
        json!({key: {"verdict": "IN-STEP", "code": "py", "ported": "l7r/diagram/m.py::SPAN#span"}})
            .as_object()
            .unwrap()
            .clone();
    let units = json!({key: {"code": "rs", "core": "c", "research": "", "uid": "rust/mode_a/src/lib.rs::SPAN"},
        "x.rs::f#f": {"code": "f", "core": "c", "research": "", "uid": "x.rs::f"}})
    .as_object()
    .unwrap()
    .clone();
    let reply = format!("VERDICT {key} IN-STEP - fine [§]\nVERDICT x.rs::f#f IN-STEP - fine [§]");
    let (new, _) = crate::claims::reply::record(&index, &units, &reply, "2026-11-17", &Map::new());
    assert_eq!(
        (new[key]["ported"].as_str(), new[key]["code"].as_str()),
        (Some("l7r/diagram/m.py::SPAN#span"), Some("rs"))
    );
    assert!(new["x.rs::f#f"].get("ported").is_none());
}
