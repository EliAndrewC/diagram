//! A claim carried across a port (feature 449 T166, Q10): the map's form, each claim's fate, the carry of the index and the deferred
//! list, and the push's refusal of a claim on a deleted unit no port carried - on rows built in memory; the commands end to end are
//! `ports::flow`'s tests.

use std::collections::{HashMap, HashSet};
use std::rc::Rc;

use serde_json::{json, Map, Value};

use super::{
    carry, carry_deferred, fate, load, save_deferred, say, unported, Before, Fate, Map as PortMap,
    Port, Ports, Rekeyed, Retired, PORTS,
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
        ..Port::default()
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
    assert_eq!(load(&root).unwrap(), PortMap::default());
    put(&root, PORTS, "{\"why\": \"w\", \"ports\": {\"l7r/diagram/m.py::SPAN\": {\"to\": \"rust/mode_a/src/lib.rs::SPAN\", \"by\": \"449 T999\"}}}");
    assert_eq!(
        load(&root).unwrap().ports["l7r/diagram/m.py::SPAN"],
        port("rust/mode_a/src/lib.rs::SPAN")
    );
    put(&root, PORTS, "{\"why\": \"w\"}");
    assert_eq!(load(&root).unwrap(), PortMap::default());
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
    let done = carry(&cur, &mut idx, &PortMap::from(ports()), &mut |k: &str| {
        asked.push(k.to_owned());
        Some(span.clone())
    });
    // the rows without their text read it from the base - the unmapped `kept` too, which rule C reads (its research holds the file, so
    // the NONE claim `lost` stays stuck); its verdict, note and pages kept, its old key recorded
    assert_eq!(
        asked,
        ["l7r/diagram/m.py::SPAN#span", "l7r/diagram/m.py::kept#kept"]
    );
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
    let done = carry(&cur, &mut idx, &PortMap::from(ports()), &mut |_: &str| {
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
        ..Rekeyed::default()
    };
    assert_eq!(say(&done, &mut o), 1);
    assert_eq!(o.out, "claims-rekey: 1 claim row(s) carried to their port (dev/claims-ports.json), each owed a full check of its new code (ported); 0 dropped, a claim of NONE research ported into a tooling crate (ask:449-T148-claims)\nclaims-rekey: unported: b - why\n");
}

#[test]
fn the_deferred_list_follows_its_units() {
    let root = crate::checks::scratch("claims-ports-deferred");
    let mut d = json!({"why": "w", "units": ["l7r/diagram/m.py::SPAN", "l7r/diagram/m.py::tool", "l7r/diagram/x.py::f"],
        "keys": ["l7r/diagram/m.py::helper#helper"]});
    assert!(carry_deferred(&mut d, &PortMap::from(ports()), &cur()));
    assert_eq!(
        d,
        json!({"why": "w", "units": ["rust/mode_a/src/lib.rs::SPAN", "l7r/diagram/x.py::f"],
        "keys": ["rust/mode_a/src/lib.rs::helper#helper"]})
    );
    assert!(!carry_deferred(&mut d, &PortMap::from(ports()), &cur()));
    assert!(!carry_deferred(
        &mut json!({"why": "w"}),
        &PortMap::from(ports()),
        &cur()
    ));
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
        owed: &[],
    };
    let unmapped = PortMap::default();
    let mut all_gone = |_: &str| true;
    let got = unported(&cur, &base, &before, &unmapped, &mut all_gone);
    // every claimed row of a deleted `.py` unit, its UNCLAIMED row and the Rust row aside
    assert_eq!(got.len(), 5, "{got:?}");
    assert!(got[0].starts_with("unported: l7r/diagram/m.py::SPAN#span - its unit l7r/diagram/m.py::SPAN is deleted, and dev/claims-ports.json maps it to no unit: if it was ported, add `\"l7r/diagram/m.py::SPAN\": {\"to\": \"rust/<crate>/src/<file>.rs::<item>\", \"by\": \"<feature> <task>\"}` under its `ports`"), "{}", got[0]);
    // a unit still in another scope is not deleted
    assert!(unported(&cur, &base, &before, &unmapped, &mut |_: &str| false).is_empty());
    // mapped, not yet carried: rekey; carried or dropped: nothing; stuck: its fix; unmapped: the map's
    let got = unported(&cur, &base, &before, &PortMap::from(ports()), &mut all_gone);
    assert_eq!(got.len(), 5, "{got:?}");
    for line in &got[..3] {
        assert!(line.ends_with("its port is mapped but its row not yet carried: `make claims-rekey` (make land runs it)"));
    }
    assert!(got[3].contains("carries no claim `lost`"));
    assert!(got[4].starts_with("unported: l7r/diagram/m.py::kept#kept - its unit"));
    let mut now = index();
    let done = carry(&cur, &mut now, &PortMap::from(ports()), &mut |_: &str| {
        Some(norm(&span_line()))
    });
    assert_eq!(done.carried.len(), 2);
    let got = unported(&cur, &now, &before, &PortMap::from(ports()), &mut all_gone);
    assert_eq!(got.len(), 2, "{got:?}");
    // a carried row a record already pruned leaves its port's claim owed as new: no carry is left to run
    let mut pruned: Map<String, Value> = now.clone();
    pruned.shift_remove("rust/mode_a/src/lib.rs::helper#helper");
    assert_eq!(
        unported(
            &cur,
            &pruned,
            &before,
            &PortMap::from(ports()),
            &mut all_gone
        )
        .len(),
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

// A retired unit (feature 449 T184, `ask:449-T184-elongated-retired`, `ask:449-T184-elongated-retired-2`): a `.py` unit deleted because
// the research overruled its rule, the claims round's finding against it named under `finding`.

const OLD: &str = "l7r/diagram/m.py::OLD";
const OLD_KEY: &str = "l7r/diagram/m.py::OLD#old ratio";
/// The finding against the rule: a twin's claim of the same label.
const FINDING: &str = "rust/mode_a/src/old.rs::subjects#old ratio";

fn retired_map() -> PortMap {
    PortMap {
        ports: ports(),
        retired: [(
            OLD.to_owned(),
            Retired {
                by: "449 T999".to_owned(),
                page: page(),
                why: "the page overrules it".to_owned(),
                finding: FINDING.to_owned(),
            },
        )]
        .into(),
        ..PortMap::default()
    }
}

/// The merge base's rows of the retired unit, its own claim IN-STEP beside an UNCLAIMED decision on it, and its finding's row at
/// `finding` reading `verdict` (none where `finding` is `None`).
fn retired_base(finding: Option<&str>, verdict: &str) -> Index {
    let mut base = json!({
        OLD_KEY: {"verdict": "IN-STEP", "code": "py", "claim": norm("old ratio - CONVENTION: 3 to 1")},
        "l7r/diagram/m.py::OLD#a decision": {"verdict": "UNCLAIMED", "code": "py"},
    })
    .as_object()
    .unwrap()
    .clone();
    if let Some(key) = finding {
        base.insert(key.to_owned(), json!({"verdict": verdict, "code": "rs"}));
    }
    base
}

fn base_uids(base: &Index) -> HashSet<String> {
    base.keys()
        .map(|k| k.rsplit_once('#').unwrap().0.to_owned())
        .collect()
}

#[test]
fn a_retired_entry_is_read_with_its_form_held() {
    let root = crate::checks::scratch("claims-ports-retired-load");
    put(&root, &page(), "<p>the page</p>");
    let entry = |uid: &str, page: &str| {
        json!({"why": "w", "ports": {"l7r/diagram/m.py::SPAN": {"to": "rust/mode_a/src/lib.rs::SPAN", "by": "449 T999"}},
            "retired": {uid: {"by": "449 T999", "page": page, "why": "the page overrules it", "finding": FINDING}}})
        .to_string()
    };
    put(&root, PORTS, &entry(OLD, &page()));
    let map = load(&root).unwrap();
    assert_eq!(map.ports.len(), 1);
    assert_eq!(map.retired, retired_map().retired);
    // RED: the page is no file in the tree
    put(
        &root,
        PORTS,
        &entry(OLD, "research/questions/0999-none.html"),
    );
    let why = load(&root).unwrap_err();
    assert!(why.contains(
        "names the page research/questions/0999-none.html, which is no file in the tree"
    ));
    // RED: the unit is also under `ports`
    put(&root, PORTS, &entry("l7r/diagram/m.py::SPAN", &page()));
    let why = load(&root).unwrap_err();
    assert!(why.contains("is both retired and under `ports`"));
    // the form: a `.py` unit, a task, a page under research/questions/, a reason, a finding
    for bad in [
        json!({"retired": {"docs/x.md::A": {"by": "t", "page": page(), "why": "w", "finding": FINDING}}}),
        json!({"retired": {OLD: {"by": " ", "page": page(), "why": "w", "finding": FINDING}}}),
        json!({"retired": {OLD: {"by": "t", "page": page(), "why": "", "finding": FINDING}}}),
        json!({"retired": {OLD: {"by": "t", "page": "docs/x.html", "why": "w", "finding": FINDING}}}),
        json!({"retired": {OLD: {"by": "t", "page": "research/questions/0001-gap.md", "why": "w", "finding": FINDING}}}),
        json!({"retired": {OLD: {"by": "t", "page": "research/questions/../x.html", "why": "w", "finding": FINDING}}}),
        json!({"retired": {OLD: "a page"}}),
        // RED: no `finding`, or one that is no `<path>::<qualname>#<label>` key
        json!({"retired": {OLD: {"by": "t", "page": page(), "why": "w"}}}),
        json!({"retired": {OLD: {"by": "t", "page": page(), "why": "w", "finding": "rust/x.rs::f"}}}),
        json!({"retired": {OLD: {"by": "t", "page": page(), "why": "w", "finding": "x#label"}}}),
        json!({"retired": {OLD: {"by": "t", "page": page(), "why": "w", "finding": "::f#label"}}}),
        json!({"retired": {OLD: {"by": "t", "page": page(), "why": "w", "finding": "rust/x.rs::#label"}}}),
        json!({"retired": {OLD: {"by": "t", "page": page(), "why": "w", "finding": "rust/x.rs::f#"}}}),
    ] {
        put(&root, PORTS, &bad.to_string());
        assert!(load(&root)
            .unwrap_err()
            .contains("is not of the form \"<path>.py::<qualname>\": {\"by\": \"<feature> <task>\", \"page\": \"research/questions/<file>.html\", \"why\": \"<one line>\", \"finding\": \"<path>::<qualname>#<label>\"}"));
    }
}

#[test]
fn a_retired_unit_still_in_the_tree_is_refused() {
    // RED: its claim still in the tree (a unit of `cur`), with no merge-base row at all
    let mut cur = cur();
    let (unit, _) = crate::claims::units::from_json(
        &json!({"path": "l7r/diagram/m.py", "qualname": "OLD", "kind": "function", "claims": ["old ratio - CONVENTION: 3 to 1"], "core": "c"}),
    );
    let unit = Rc::new(unit);
    for c in &unit.claims {
        cur.insert(Row {
            key: unit.key(c),
            code: unit.code(c),
            unit: unit.clone(),
            claim: c.clone(),
            research: String::new(),
        });
    }
    let base = retired_base(Some(FINDING), "MISLABELED");
    let uids = base_uids(&base);
    let texts = HashMap::new();
    let before = Before {
        index: &base,
        uids: &uids,
        texts: &texts,
        owed: &[],
    };
    // `gone` is asked only of a retired unit whose claims the tree no longer holds
    let mut asked = Vec::new();
    let mut gone = |u: &str| {
        asked.push(u.to_owned());
        u != OLD
    };
    let still = "unported: l7r/diagram/m.py::OLD - retired but still present: dev/claims-ports.json's `retired` names a unit deleted because the research overruled its rule; delete the unit, or take it out of `retired`";
    let got = unported(&cur, &base, &before, &retired_map(), &mut gone);
    assert_eq!(got, [still]);
    let empty = Index::new();
    let nobase = Before {
        index: &empty,
        uids: &uids,
        texts: &texts,
        owed: &[],
    };
    assert_eq!(
        unported(&cur, &base, &nobase, &retired_map(), &mut gone),
        [still]
    );
    // RED: its claims gone, the unit itself still in another scope
    let got = unported(&self::cur(), &base, &before, &retired_map(), &mut gone);
    assert_eq!(got, [still]);
    assert_eq!(asked, [OLD]);
}

/// What the push says of the retired claim, its unit gone and `map` read, on the merge base `base`.
fn retired_push(base: &Index, map: &PortMap) -> Vec<String> {
    let uids = base_uids(base);
    let texts = HashMap::new();
    let before = Before {
        index: base,
        uids: &uids,
        texts: &texts,
        owed: &[],
    };
    unported(&cur(), &Index::new(), &before, map, &mut |_: &str| true)
}

fn new_ask(finding: &str, why: &str) -> Vec<String> {
    vec![format!("unported: {OLD_KEY} - dev/claims-ports.json retires its unit (449 T999, {}), but its `finding` {finding} {why}: retire only a claim whose claims round found the research against it: name that finding's key under `finding`; else a new ask (`make arbiter-ask`) (ask:449-T184-elongated-retired-2)", page())]
}

#[test]
fn a_retirement_whose_finding_is_not_in_the_merge_base_is_a_new_ask() {
    // RED: the finding names no row of the merge base's index
    assert_eq!(
        retired_push(&retired_base(None, ""), &retired_map()),
        new_ask(FINDING, "is no key of the merge base's index")
    );
}

#[test]
fn a_retirement_whose_finding_reads_in_step_is_a_new_ask() {
    // RED: the finding's row reads IN-STEP, or holds no verdict
    assert_eq!(
        retired_push(&retired_base(Some(FINDING), "IN-STEP"), &retired_map()),
        new_ask(FINDING, "reads IN-STEP at the merge base")
    );
    assert_eq!(
        retired_push(&retired_base(Some(FINDING), ""), &retired_map()),
        new_ask(FINDING, "reads no verdict at the merge base")
    );
}

#[test]
fn a_retirement_whose_finding_names_another_label_is_a_new_ask() {
    // RED: the finding is a DRIFTED row of the merge base, but of another claim than the retired one
    let other = "rust/mode_a/src/old.rs::subjects#another rule";
    let mut map = retired_map();
    map.retired.get_mut(OLD).unwrap().finding = other.to_owned();
    assert_eq!(
        retired_push(&retired_base(Some(other), "DRIFTED"), &map),
        new_ask(other, "names the label `another rule`, not `old ratio`")
    );
}

#[test]
fn a_retired_claim_in_step_whose_finding_is_mislabeled_passes_and_its_row_drops() {
    // the retired unit's own row reads IN-STEP; its finding, the same label on the twin, MISLABELED
    let cur = cur();
    let base = retired_base(Some(FINDING), "MISLABELED");
    let uids = base_uids(&base);
    let texts = HashMap::new();
    let before = Before {
        index: &base,
        uids: &uids,
        texts: &texts,
        owed: &[],
    };
    let mut gone = |_: &str| true;
    // its row still in the index: `make claims-rekey`
    let mut now = base.clone();
    assert_eq!(
        unported(&cur, &now, &before, &retired_map(), &mut gone),
        [format!("unported: {OLD_KEY} - its unit is retired ({}) but its row not yet dropped: `make claims-rekey` (make land runs it)", page())]
    );
    // the carry drops the claim's row and keeps the UNCLAIMED one, a ported unit's row carried beside it as before
    now.insert(
        "l7r/diagram/m.py::SPAN#span".to_owned(),
        json!({"verdict": "IN-STEP", "code": "py"}),
    );
    let done = carry(&cur, &mut now, &retired_map(), &mut |_: &str| {
        Some(norm(&span_line()))
    });
    assert_eq!(done.retired, [OLD_KEY]);
    assert_eq!(done.retired_pages, [page()].into());
    assert_eq!(done.carried, ["l7r/diagram/m.py::SPAN#span"]);
    assert!(done.stuck.is_empty());
    assert!(!now.contains_key(OLD_KEY));
    assert!(now.contains_key("l7r/diagram/m.py::OLD#a decision"));
    // and the push lets it go
    assert!(unported(&cur, &now, &before, &retired_map(), &mut gone).is_empty());
    // what rekey says of it
    let mut o = Out::default();
    assert_eq!(say(&done, &mut o), 0);
    assert_eq!(o.out, format!("claims-rekey: 1 claim row(s) carried to their port (dev/claims-ports.json), each owed a full check of its new code (ported); 0 dropped, a claim of NONE research ported into a tooling crate (ask:449-T148-claims)\nclaims-rekey: 1 claim row(s) of a retired unit dropped (dev/claims-ports.json's `retired`), its rule overruled by {} (ask:449-T184-elongated-retired)\n", page()));
    // the deferred list drops its unit and its keys, and a unit still claimed keeps them
    let mut d = json!({"why": "w", "units": [OLD, "l7r/diagram/x.py::f"], "keys": [OLD_KEY]});
    assert!(carry_deferred(&mut d, &retired_map(), &cur));
    assert_eq!(
        d,
        json!({"why": "w", "units": ["l7r/diagram/x.py::f"], "keys": []})
    );
    assert!(!carry_deferred(&mut d, &retired_map(), &cur));
}

// Three more outcomes of a port (feature 449 T212, `ask:449-T212-stranded-claims`): a relabeled claim (A), a split unit (B) and a NONE
// claim left behind in a file a port's cut deleted (C).

const FIXED: &str = "rust/mode_a/src/lib.rs::FIXED#ratio";
const RATIO: &str = "l7r/diagram/n.py::RATIO#ratio";

/// The ports: a constant carrying a corrected claim (A), and the three units of the first source (B, C).
fn cur_of(extra: &[(&str, &str)]) -> Cur {
    let mut cur = cur();
    let fixed = "/// Research: ratio - GUESS: no page gives it; the sanctuary may stray 3 ft\npub const FIXED: f64 = 3.0;\n";
    let mut sources = vec![(fixed.to_owned(), "rust/mode_a/src/lib.rs".to_owned())];
    sources.extend(
        extra
            .iter()
            .map(|(src, at)| ((*src).to_owned(), (*at).to_owned())),
    );
    for (src, at) in sources {
        for u in rust_units(&src, &at).1 {
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
    }
    cur
}

fn relabeled(to: &str) -> Port {
    Port {
        relabeled: true,
        ..port(to)
    }
}

/// The Python row MISLABELED at the merge base, and its correction checked on its port.
fn relabel_index(verdict: &str, checked: bool) -> Index {
    let mut idx = json!({
        RATIO: {"verdict": verdict, "code": "py", "claim": norm("ratio - NONE: an audit tolerance")},
    })
    .as_object()
    .unwrap()
    .clone();
    if checked {
        idx.insert(
            FIXED.to_owned(),
            json!({"verdict": "IN-STEP", "code": "rs"}),
        );
    }
    idx
}

#[test]
fn a_relabeled_claim_goes_only_mislabeled_with_its_correction_checked() {
    let cur = cur_of(&[]);
    let text = norm("ratio - NONE: an audit tolerance");
    let at = |p: &Port, idx: &Index, verdict: &str| {
        format!(
            "{:?}",
            super::settle(RATIO, p, &cur, idx, verdict, Some(&text))
        )
    };
    let fixed = relabeled("rust/mode_a/src/lib.rs::FIXED");
    assert_eq!(
        at(&fixed, &relabel_index("MISLABELED", true), "MISLABELED"),
        format!("{:?}", Fate::Relabeled(FIXED.to_owned()))
    );
    // each gate: no flag, a verdict not MISLABELED, the correction unchecked, no target carrying the label
    let plain = port("rust/mode_a/src/lib.rs::FIXED");
    assert!(at(&plain, &relabel_index("MISLABELED", true), "MISLABELED")
        .contains("carries the label `ratio` but reads"));
    assert!(at(&fixed, &relabel_index("IN-STEP", true), "IN-STEP")
        .contains("reads IN-STEP, where only MISLABELED lets it go: a new ask"));
    assert!(at(&fixed, &relabel_index("MISLABELED", true), "").contains("reads no verdict"));
    assert!(
        at(&fixed, &relabel_index("MISLABELED", false), "MISLABELED")
            .contains("has no checked row")
    );
    let elsewhere = relabeled("rust/mode_a/src/lib.rs::helper");
    assert!(
        at(&elsewhere, &relabel_index("MISLABELED", true), "MISLABELED")
            .contains("carries a claim `ratio`: a new ask")
    );
    // a relabeled port that carries the claim word for word carries it
    let span = relabeled("rust/mode_a/src/lib.rs::SPAN");
    assert_eq!(
        super::settle(
            SPAN,
            &span,
            &cur,
            &Index::new(),
            "IN-STEP",
            Some(&norm(&span_line()))
        ),
        Fate::Carried(NEW_SPAN.to_owned())
    );
    // rekey drops the row, not carried, the correction's own row untouched; the push refuses it until then, and not after
    let map = PortMap::from(Ports::from([("l7r/diagram/n.py::RATIO".to_owned(), fixed)]));
    let base = relabel_index("MISLABELED", true);
    let uids: HashSet<String> = HashSet::from(["l7r/diagram/n.py::RATIO".to_owned()]);
    let texts = HashMap::new();
    let before = Before {
        index: &base,
        uids: &uids,
        texts: &texts,
        owed: &[],
    };
    let got = unported(&cur, &base, &before, &map, &mut |_: &str| true);
    assert_eq!(got.len(), 1);
    assert!(got[0].ends_with("its row not yet carried: `make claims-rekey` (make land runs it)"));
    let mut idx = base.clone();
    let done = carry(&cur, &mut idx, &map, &mut base_text);
    assert_eq!(
        (done.relabeled.as_slice(), done.carried.len()),
        ([RATIO.to_owned()].as_slice(), 0)
    );
    assert_eq!(
        idx,
        relabel_index("MISLABELED", true)
            .into_iter()
            .filter(|(k, _)| k == FIXED)
            .collect()
    );
    assert!(unported(&cur, &idx, &before, &map, &mut |_: &str| true).is_empty());
    let mut o = Out::default();
    assert_eq!(say(&done, &mut o), 0);
    assert!(o
        .out
        .contains("1 claim row(s) of a `relabeled` port dropped, not carried"));
}

#[test]
fn a_split_unit_s_claims_go_each_to_the_target_carrying_its_text() {
    let root = crate::checks::scratch("claims-ports-split");
    put(&root, PORTS, "{\"ports\": {\"l7r/diagram/m.py::both\": {\"to\": [\"rust/mode_a/src/lib.rs::SPAN\", \"rust/mode_a/src/lib.rs::helper\"], \"by\": \"449 T999\", \"relabeled\": false}}}");
    let both = load(&root).unwrap().ports["l7r/diagram/m.py::both"].clone();
    assert_eq!(
        (both.targets(), both.relabeled),
        (
            vec![
                "rust/mode_a/src/lib.rs::SPAN",
                "rust/mode_a/src/lib.rs::helper"
            ],
            false
        )
    );
    for bad in [
        "{\"ports\": {\"m.py::A\": {\"to\": [], \"by\": \"t\"}}}",
        "{\"ports\": {\"m.py::A\": {\"to\": [\"r::A\", \"nothing\"], \"by\": \"t\"}}}",
        "{\"ports\": {\"m.py::A\": {\"to\": \"r::A\", \"by\": \"t\", \"relabeled\": \"yes\"}}}",
    ] {
        put(&root, PORTS, bad);
        assert!(load(&root).unwrap_err().contains("(or a list of them)"));
    }
    let cur = cur();
    let at = |k: &str, line: &str| fate(k, &both, &cur, Some(&norm(line)));
    assert_eq!(
        at("l7r/diagram/m.py::both#span", &span_line()),
        Fate::Carried(NEW_SPAN.to_owned())
    );
    assert_eq!(
        at("l7r/diagram/m.py::both#helper", HELPER),
        Fate::Carried(NEW_HELPER.to_owned())
    );
    let why = format!("{:?}", at("l7r/diagram/m.py::both#lost", "lost - NONE: x"));
    assert!(why.contains("is on none of its targets (rust/mode_a/src/lib.rs::SPAN, rust/mode_a/src/lib.rs::helper): a new ask"));
}

const HELPER: &str = "helper - NONE: plumbing";
const NEW_SPAN: &str = "rust/mode_a/src/lib.rs::SPAN#span";
const NEW_HELPER: &str = "rust/mode_a/src/lib.rs::helper#helper";
const SPAN: &str = "l7r/diagram/m.py::SPAN#span";

/// The rows of a deleted file `c.py`: one claim carried, a NONE claim its port does not carry, a NONE claim on an unmapped unit, and
/// (`cited`) a claim citing research on an unmapped unit.
fn left_behind(cited: bool) -> Index {
    let mut idx = json!({
        "l7r/diagram/c.py::SPAN#span": {"verdict": "IN-STEP", "code": "py", "claim": norm(&span_line())},
        "l7r/diagram/c.py::rx#its salts": {"verdict": "IN-STEP", "code": "py", "claim": norm("its salts - NONE: 5 (regex group range)")},
        "l7r/diagram/c.py::memo#its cache size": {"verdict": "IN-STEP", "code": "py"},
        "l7r/diagram/d.py::memo#its cache size": {"verdict": "IN-STEP", "code": "py", "claim": norm("its cache size - NONE: 8")},
    })
    .as_object()
    .unwrap()
    .clone();
    if cited {
        idx.insert("l7r/diagram/c.py::cited#cited".to_owned(), json!({"verdict": "IN-STEP", "code": "py", "claim": norm(&span_line().replace("span", "cited"))}));
    }
    idx
}

/// The merge base's text of a row recorded before the index held it: `c.py`'s unmapped `memo`.
fn base_text(key: &str) -> Option<String> {
    key.ends_with("c.py::memo#its cache size")
        .then(|| norm("its cache size - NONE: 8"))
}

fn cut() -> PortMap {
    PortMap::from(Ports::from([
        (
            "l7r/diagram/c.py::SPAN".to_owned(),
            port("rust/mode_a/src/lib.rs::SPAN"),
        ),
        (
            "l7r/diagram/c.py::rx".to_owned(),
            port("rust/mode_a/src/lib.rs::helper"),
        ),
    ]))
}

#[test]
fn a_none_claim_left_behind_goes_only_with_its_whole_file() {
    let cur = cur_of(&[]);
    let (rx, memo) = (
        "l7r/diagram/c.py::rx#its salts",
        "l7r/diagram/c.py::memo#its cache size",
    );
    // every other claim of the deleted file carried: its two NONE claims go, ported or not; `d.py`, in no port's cut, keeps its own
    let mut idx = left_behind(false);
    let done = carry(&cur, &mut idx, &cut(), &mut base_text);
    assert_eq!(
        (done.carried.len(), done.orphaned.clone(), done.stuck.len()),
        (1, vec![rx.to_owned(), memo.to_owned()], 0)
    );
    assert_eq!(
        idx.keys().cloned().collect::<Vec<_>>(),
        ["l7r/diagram/d.py::memo#its cache size", NEW_SPAN]
    );
    let mut o = Out::default();
    assert_eq!(say(&done, &mut o), 0);
    assert!(o.out.contains(
        "2 claim row(s) of NONE research dropped, left on no unit in a file a port's cut deleted"
    ));
    // a claim citing research left behind holds the whole file: nothing of it goes, the NONE claim's port left stuck
    let mut idx = left_behind(true);
    let done = carry(&cur, &mut idx, &cut(), &mut base_text);
    assert_eq!(
        (done.carried.len(), done.orphaned.len(), done.stuck.len()),
        (1, 0, 1)
    );
    assert!(idx.contains_key(rx) && idx.contains_key(memo));
    // a NONE claim its port's target carries under its own label is a relabel, A's and not C's: unflagged it stays stuck, and holds
    // the file's other NONE claims
    let mut idx = left_behind(false);
    idx.insert(
        "l7r/diagram/c.py::RATIO#ratio".to_owned(),
        json!({"verdict": "MISLABELED", "code": "py", "claim": norm("ratio - NONE: an audit tolerance")}),
    );
    let mut relabel = cut();
    relabel.ports.insert(
        "l7r/diagram/c.py::RATIO".to_owned(),
        port("rust/mode_a/src/lib.rs::FIXED"),
    );
    let done = carry(&cur, &mut idx, &relabel, &mut base_text);
    assert_eq!((done.orphaned.len(), done.stuck.len()), (0, 2), "{done:?}");
    // a file still in the tree is no deleted file
    let still = cur_of(&[(
        "/// Research: kept - NONE: x\npub fn kept() {}\n",
        "l7r/diagram/c.py",
    )]);
    let mut idx = left_behind(false);
    assert!(carry(&still, &mut idx, &cut(), &mut base_text)
        .orphaned
        .is_empty());
    // the push: refused until rekey drops them, then not; a file held by research refuses each claim left behind
    let base = left_behind(false);
    let uids: HashSet<String> = base
        .keys()
        .map(|k| k.rsplit_once('#').unwrap().0.to_owned())
        .collect();
    // the merge base's text of the row the index holds none for
    let texts = HashMap::from([(memo.to_owned(), base_text(memo).unwrap())]);
    let before = Before {
        index: &base,
        uids: &uids,
        texts: &texts,
        owed: &[],
    };
    let got = unported(&cur, &base, &before, &cut(), &mut |_: &str| true);
    assert_eq!(got.len(), 4, "{got:?}");
    assert!(got[..3]
        .iter()
        .all(|l| l.ends_with("`make claims-rekey` (make land runs it)")));
    assert!(got[3].starts_with("unported: l7r/diagram/d.py::memo#its cache size - its unit"));
    let mut now = base.clone();
    carry(&cur, &mut now, &cut(), &mut base_text);
    assert_eq!(
        unported(&cur, &now, &before, &cut(), &mut |_: &str| true).len(),
        1
    );
    let held = left_behind(true);
    let uids: HashSet<String> = held
        .keys()
        .map(|k| k.rsplit_once('#').unwrap().0.to_owned())
        .collect();
    let before = Before {
        index: &held,
        uids: &uids,
        texts: &texts,
        owed: &[],
    };
    let got = unported(&cur, &held, &before, &cut(), &mut |_: &str| true);
    assert_eq!(got.len(), 5, "{got:?}");
    assert!(got.iter().any(|l| l
        .contains("rx#its salts - rust/mode_a/src/lib.rs::helper carries no claim `its salts`")));
}
