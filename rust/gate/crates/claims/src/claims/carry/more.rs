//! The carry's other paths: the known drifts' every source, the target and the filed rows with nothing to read, a tree with no merge
//! base or no commit, a relabel that answered its verdict, an introduced finding at the push with no feature to file into.

use std::rc::Rc;

use serde_json::{json, Map, Value};

use super::{
    canon, classified, filed, known_drifts, record_known, target, touches_engine, Reading,
};
use crate::claims::grammar::parse_claim;
use crate::claims::index::{body_of, Cur, Row};
use crate::claims::scope::Reader;
use crate::claims::tests::{claims, fixture, record_all};
use crate::claims::units::rust_units;
use crate::record::testkit::{commit, git, put};

fn row_of(key: &str, line: &str) -> Row {
    let unit = Rc::new(
        rust_units(crate::claims::tests::LIB, "rust/phases/src/lib.rs")
            .1
            .remove(1),
    );
    let claim = parse_claim(line).unwrap();
    Row {
        key: key.into(),
        code: unit.code(&claim),
        unit,
        claim,
        research: String::new(),
    }
}

#[test]
fn the_known_drifts_come_from_a_named_open_task_or_an_accept() {
    let root = fixture("claims-carry-known");
    put(
        &root,
        "specs/405-a/tasks.md",
        "- [ ] T01 fix reach here\n- [ ] T02 another thing\n",
    );
    let mut cur = Cur::default();
    for (k, line) in [
        ("x.rs::reach#named", "named - NONE: until feature 405 T01"),
        ("a#other", "other - NONE: until feature 405 T02"),
        ("a#accepted-named", "x - NONE: until feature 405 T02"),
        ("a#nospec", "y - NONE: until feature 406 T01"),
        ("a#accepted", "z - NONE"),
        ("a#instep", "w - NONE: feature 405 T01"),
    ] {
        cur.insert(row_of(k, line));
    }
    let accepted = "a known drift accepted by the round arbiter";
    let index: Map<String, Value> = json!({
        "x.rs::reach#named": {"verdict": "DRIFTED"}, "a#other": {"verdict": "DRIFTED"}, "a#accepted-named": {"verdict": "DRIFTED", "note": accepted},
        "a#nospec": {"verdict": "DRIFTED"}, "a#accepted": {"verdict": "DRIFTED", "note": accepted}, "a#instep": {"verdict": "IN-STEP"},
        "gone#x": {"verdict": "DRIFTED", "note": accepted},
    })
    .as_object()
    .unwrap()
    .clone();
    let known = known_drifts(&cur, &index, &root).unwrap();
    assert_eq!(
        known.get("x.rs::reach#named").map(String::as_str),
        Some("405 T01")
    );
    assert_eq!(
        known.get("a#accepted-named").map(String::as_str),
        Some("accepted by the round arbiter")
    );
    assert_eq!(
        known.get("a#accepted").map(String::as_str),
        Some("accepted by the round arbiter")
    );
    assert!(
        !known.contains_key("a#other")
            && !known.contains_key("a#nospec")
            && !known.contains_key("gone#x")
    );
    assert!(known_drifts(&Cur::default(), &Map::new(), &root)
        .unwrap()
        .is_empty());
}

#[test]
fn a_tree_with_nothing_to_read_reads_nothing() {
    assert!(filed(None).unwrap().is_empty());
    assert_eq!(
        canon(std::path::Path::new("/no/such/place")),
        std::path::PathBuf::new()
    );
    let root = fixture("claims-carry-bare");
    put(&root, "specs/405-claims/tasks.md", "- [x] T01 done\n");
    put(
        &root,
        "specs/405-claims/claims-carried.jsonl",
        "{\"task\": \"T01\", \"keys\": [\"k\"]}\n",
    );
    assert!(target(&root).unwrap().is_none());
    git(&root, &["update-ref", "-d", "refs/remotes/origin/main"]);
    assert!(!touches_engine(&root).unwrap());
    put(&root, "specs/406-x/tasks.md", "- [ ] T01 open\n");
    put(
        &root,
        "specs/406-x/claims-carried.jsonl",
        "{\"task\": \"T09\", \"keys\": [\"k\"]}\n{\"task\": \"T01\"}\n",
    );
    put(
        &root,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/406-x\"}",
    );
    assert!(filed(target(&root).unwrap().as_deref()).unwrap().is_empty());
    let mut reader = Reader::new(&root, &root);
    let at = Reading {
        cur: Cur::default(),
        index: Map::new(),
    };
    let (owed, intro, pre, carried) = classified(&mut reader, &root, &at).unwrap();
    assert!(owed.is_empty() && intro.is_empty() && pre.is_empty() && carried.is_empty());
    let empty = crate::checks::scratch("claims-carry-empty");
    git(&empty, &["init", "-q"]);
    let mut bare = Reader::new(&empty, &empty);
    assert!(classified(&mut bare, &empty, &at).unwrap().0.is_empty());
    put(&root, "dev/claims-index.json", "[1]");
    commit(&root, "a list for an index");
    assert!(classified(&mut reader, &root, &at)
        .unwrap_err()
        .starts_with("AttributeError"));
    put(&root, "dev/claims-index.json", "{");
    commit(&root, "a broken index");
    assert!(classified(&mut reader, &root, &at)
        .unwrap_err()
        .contains("JSONDecodeError"));
}

#[test]
fn an_introduced_finding_refuses_and_an_answered_relabel_does_not() {
    let root = fixture("claims-carry-intro");
    put(&root, "specs/405-claims/tasks.md", "- [x] T01 done\n");
    crate::claims::tests::py_units(&root, &[], &[]);
    record_all(&root);
    commit(&root, "recorded");
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    let lib = std::fs::read_to_string(root.join("rust/phases/src/lib.rs")).unwrap();
    std::fs::write(
        root.join("rust/phases/src/lib.rs"),
        lib.replace("a[1] + 42", "a[1] + 43")
            .replace("within GAP", "within GAP, relabeled"),
    )
    .unwrap();
    let o = root.join("b").to_string_lossy().into_owned();
    claims(
        &root,
        &[
            "bundle",
            "--units",
            "rust/phases/src/lib.rs::Thing.m#method guess",
            "--out",
            &o,
            "--reason",
            "a re check",
        ],
    );
    let r = root.join("r.txt");
    std::fs::write(
        &r,
        "VERDICT rust/phases/src/lib.rs::Thing.m#method guess DRIFTED - off\n",
    )
    .unwrap();
    claims(
        &root,
        &["record", "--bundle", &o, "--reply", &r.to_string_lossy()],
    );
    let mut reader = Reader::new(&root, &root);
    let cur = crate::claims::index::current(&mut reader, &root, &root.join("research/questions"))
        .unwrap();
    let reach = cur.get("rust/phases/src/lib.rs::reach#reach").unwrap();
    let mut ix = crate::claims::index::load_map(&root.join("dev/claims-index.json")).unwrap();
    ix.insert("gone.rs::x#y".to_owned(), json!({"verdict": "UNCLAIMED"}));
    ix["rust/phases/src/lib.rs::reach#reach"] = json!({"verdict": "MISLABELED", "code": "old", "body": body_of(&root, &reach.unit).unwrap(), "claim": "before", "research": reach.research});
    std::fs::write(
        root.join("dev/claims-index.json"),
        Value::Object(ix).to_string(),
    )
    .unwrap();
    let got = claims(&root, &["gate"]);
    assert_eq!(got.code, 0);
    assert!(got.stdout.contains("claims-gate: introduced: DRIFTED        rust/phases/src/lib.rs::Thing.m#method guess - off"));
    assert!(!got.stdout.contains("reach#reach"));
    put(
        &root,
        "dev/switches.json",
        "{\"claims\": {\"state\": \"clean\"}}",
    );
    let got = claims(&root, &["gate"]);
    assert!(got
        .stdout
        .contains("claims-gate: REFUSED introduced: DRIFTED"));
    let at = Reading {
        cur,
        index: Map::new(),
    };
    put(
        &root,
        "dev/claims-index.json",
        "{\"rust/phases/src/lib.rs::reach#reach\": {\"verdict\": \"DRIFTED\", \"code\": \"x\"}}",
    );
    let _ = record_known(&mut reader, &root, &at).unwrap();
}

#[test]
fn a_tree_with_no_claims_feature_files_into_the_active_one_and_a_dotted_unit_is_named() {
    let root = fixture("claims-carry-noclaims");
    put(&root, "specs/406-x/tasks.md", "- [ ] T01 fix reach now\n");
    put(
        &root,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/406-x\"}",
    );
    assert!(target(&root).unwrap().unwrap().ends_with("specs/406-x"));
    let mut cur = Cur::default();
    cur.insert(row_of(
        "x.rs::Thing.reach#d",
        "d - NONE: until feature 406 T01",
    ));
    let index: Map<String, Value> = json!({"x.rs::Thing.reach#d": {"verdict": "DRIFTED"}})
        .as_object()
        .unwrap()
        .clone();
    assert_eq!(
        known_drifts(&cur, &index, &root).unwrap()["x.rs::Thing.reach#d"],
        "406 T01"
    );
}
