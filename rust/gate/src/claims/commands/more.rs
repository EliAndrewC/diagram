//! The commands' other paths: the coverage, the accept, the counter-only clear, the stale figures, a bundle's own files missing, a
//! triage every claim of which is owed in full, the helpers with nothing to carry.

use std::collections::HashMap;
use std::path::Path;

use serde_json::{json, Map, Value};

use super::{backfill, backfill_sections, refingerprint};
use crate::claims::index::{Cur, Row};
use crate::claims::tests::{claims, fixture, py_units, record_all};
use crate::record::testkit::{commit, git, put};

fn index(root: &Path) -> Value {
    serde_json::from_str(&std::fs::read_to_string(root.join("dev/claims-index.json")).unwrap())
        .unwrap()
}

fn reply(root: &Path, text: &str) -> String {
    let p = root.join("reply.txt");
    std::fs::write(&p, text).unwrap();
    p.to_string_lossy().into_owned()
}

#[test]
fn the_coverage_and_the_accept() {
    let root = fixture("claims-more-cover");
    let buildings = std::fs::read_to_string(root.join("docs/buildings.md")).unwrap();
    std::fs::write(
        root.join("docs/buildings.md"),
        buildings.replace("No claim here.", "<!-- Research: deep - NONE -->"),
    )
    .unwrap();
    let got = claims(&root, &["coverage"]);
    assert_eq!(
        (got.code, got.stdout.as_str()),
        (0, "claims-coverage: every unit carries a claim\n")
    );
    let got = claims(&root, &["coverage", "--path", "rust/"]);
    assert_eq!(
        got.stdout,
        "claims-coverage: every unit under rust/ carries a claim\n"
    );
    put(
        &root,
        "rust/phases/src/bad.rs",
        "/// Research: broken\npub fn b() {}\n",
    );
    let got = claims(&root, &["coverage"]);
    assert_eq!(got.code, 1);
    assert!(got.stdout.starts_with("rust/phases/src/bad.rs:2 b: `broken` has no `<label> - <backing>`\nclaims-coverage: 1 problem(s). The form: a claim is one line"));
    std::fs::remove_file(root.join("rust/phases/src/bad.rs")).unwrap();
    record_all(&root);
    let mut ix = index(&root);
    ix["rust/phases/src/lib.rs::GAP#gap"]["verdict"] = json!("DRIFTED");
    std::fs::write(root.join("dev/claims-index.json"), ix.to_string()).unwrap();
    let got = claims(
        &root,
        &[
            "accept",
            "--keys",
            "rust/phases/src/lib.rs::GAP#gap;docs/buildings.md::Walls#walls",
            "--trigger",
            "ask:t",
        ],
    );
    assert_eq!(got.stdout.lines().last(), Some("claims-accept: 1 claim(s) recorded IN-STEP and 1 kept DRIFTED (a known drift) on ask:t's accept"));
    let ix = index(&root);
    assert!(ix["rust/phases/src/lib.rs::GAP#gap"]["note"]
        .as_str()
        .unwrap()
        .ends_with("a known drift accepted by the round arbiter (ask:t) to land as filed"));
    assert_eq!(
        ix["docs/buildings.md::Walls#walls"]["note"],
        "accepted by the round arbiter (ask:t), binding"
    );
    let got = claims(&root, &["accept", "--keys", "nope#x", "--trigger", "t"]);
    assert_eq!(
        (got.code, got.stderr.as_str()),
        (2, "claims-accept: no such claim: nope#x\n")
    );
    let got = claims(&root, &["accept", "--keys", " ; ", "--trigger", "t"]);
    assert_eq!(got.stderr, "claims-accept: no such claim: (none named)\n");
    let got = claims(&root, &["owed"]);
    assert_eq!(got.stdout, "claims-owed: no claim is owed\n");
    let got = claims(&root, &["bundle", "--units", ""]);
    assert_eq!(
        got.stderr,
        "claims-bundle: no such claim(s): (none selected)\n"
    );
    assert_eq!(
        claims(&root, &["rekey"]).stdout,
        "claims-rekey: 0 claim row(s) carried to the file their unit moved to\n"
    );
    assert!(claims(&root, &["refingerprint"])
        .stdout
        .starts_with("claims-refingerprint: 0 claim row(s)"));
    let b = std::fs::read_to_string(root.join("docs/buildings.md")).unwrap();
    std::fs::write(
        root.join("docs/buildings.md"),
        b + "\n## Tick\n<!-- Research: tick` - NONE -->\n",
    )
    .unwrap();
    let got = claims(
        &root,
        &[
            "accept",
            "--keys",
            "docs/buildings.md::Tick#tick`",
            "--trigger",
            "t",
        ],
    );
    assert!(got.stdout.starts_with(
        "claims-accept: refused: `docs/buildings.md::Tick#tick` is not a unit of this bundle\n"
    ));
}

#[test]
fn a_counter_only_change_is_cleared_and_a_stale_figure_named() {
    let root = fixture("claims-more-counter");
    py_units(
        &root,
        &[],
        &[
            ("helper", "function", &["help - NONE"], false),
            ("other", "function", &["other - NONE"], false),
            ("Table", "constant", &["table - NONE"], false),
        ],
    );
    record_all(&root);
    commit(&root, "recorded");
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    let mut ix = index(&root);
    for (k, only) in [
        ("l7r/diagram/m.py::helper#help", true),
        ("l7r/diagram/m.py::other#other", false),
    ] {
        ix[k]["code"] = json!("old");
        ix[k]["counter_only"] = json!(only);
    }
    ix["l7r/diagram/m.py::Table#table"]["code"] = json!("old");
    std::fs::write(root.join("dev/claims-index.json"), ix.to_string()).unwrap();
    let lib = std::fs::read_to_string(root.join("rust/phases/src/lib.rs")).unwrap();
    std::fs::write(
        root.join("rust/phases/src/lib.rs"),
        lib.replace("let y = 3.25;", "let y = 3.5;"),
    )
    .unwrap();
    put(&root, "l7r/diagram/m.py", "GAP = 13\n");
    let got = claims(&root, &["owed"]);
    assert!(got.stdout.starts_with("claims-owed: 1 claim(s) cleared without a triage - their units only gained counter blocks (feature 446, FR-003)\n"));
    assert!(got.stdout.contains("\nstale figure: the stub's\n"));
    let ix = index(&root);
    assert_eq!(
        ix["l7r/diagram/m.py::helper#help"]["cleared"],
        "counter-only (feature 446)"
    );
    assert!(ix["l7r/diagram/m.py::other#other"].get("cleared").is_none());
    git(&root, &["update-ref", "-d", "refs/remotes/origin/main"]);
    let got = claims(&root, &["owed"]);
    assert!(!got.stdout.contains("cleared") && !got.stdout.contains("stale figure"));
}

#[test]
fn a_bundle_that_lost_its_files_fails_as_the_python_did() {
    let root = fixture("claims-more-files");
    let b = root.join("b");
    let o = b.to_string_lossy().into_owned();
    let r = reply(
        &root,
        "VERDICT rust/phases/src/lib.rs::GAP#gap IN-STEP - fine\n",
    );
    let got = claims(&root, &["record", "--bundle", &o, "--reply", &r]);
    assert!(got.code == 1 && got.stderr.contains("FileNotFoundError"));
    put(&root, "b/units.json", "{");
    assert!(claims(&root, &["record", "--bundle", &o, "--reply", &r])
        .stderr
        .contains("JSONDecodeError"));
    put(&root, "b/units.json", "[]");
    let got = claims(&root, &["record", "--bundle", &o, "--reply", &r]);
    assert_eq!(got.code, 3);
    assert!(got.stdout.contains("claims-checked: 0 of 0 recorded"));
    claims(
        &root,
        &[
            "bundle",
            "--units",
            "rust/phases/src/lib.rs::GAP#gap",
            "--out",
            &o,
        ],
    );
    std::fs::remove_file(b.join("blocks.json")).unwrap();
    let got = claims(&root, &["record", "--bundle", &o, "--reply", &r]);
    assert!(got.stdout.contains("claims-checked: 1 of 1 recorded"));
    put(&root, "b/triage.json", "{\"units\": {\"rust/phases/src/lib.rs::GAP#gap\": {\"research\": \"r\", \"pages\": {}}, \"rust/phases/src/lib.rs::reach#reach\": {\"research\": \"r\", \"pages\": {}}}, \"snapshots\": {}, \"forced\": [\"rust/phases/src/lib.rs::reach#reach\", 3]}");
    let r = reply(&root, "nothing named\n");
    let got = claims(&root, &["triaged", "--bundle", &o, "--reply", &r]);
    assert!(got.stdout.ends_with("claims-triaged: 1 of 2 sent on to impl-drift (0 named by the reply, 1 cx.owed in full: a removed block's words could not be shown); the rest cleared\n"));
}

#[test]
fn a_triage_with_nothing_to_show_owes_every_claim_in_full() {
    let root = fixture("claims-more-forced");
    py_units(&root, &[], &[]);
    record_all(&root);
    let lib = std::fs::read_to_string(root.join("rust/phases/src/lib.rs")).unwrap();
    let lib = lib
        .replace("let y = 3.25;", "let y = 3.5;")
        .replace("a[1] + 42", "a[1] + 43")
        .replace("pub const GAP: f64 = 12.0;", "pub const GAP: f64 = 12.5;")
        .replace("    1\n}", "    2\n}");
    std::fs::write(root.join("rust/phases/src/lib.rs"), lib).unwrap();
    commit(&root, "all at once");
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    let got = claims(&root, &["triage"]);
    assert!(got
        .stdout
        .starts_with("claims-triage: all 4 claim(s) are cx.owed in full"));
    assert!(std::path::Path::new("/tmp/l7r-check/claims-triage/triage.json").is_file());
}

#[test]
fn the_helpers_carry_nothing_they_cannot_name() {
    let root = fixture("claims-more-helpers");
    let mut cur = Cur::default();
    let unit = std::rc::Rc::new(
        crate::claims::units::rust_units(crate::claims::tests::LIB, "rust/phases/src/lib.rs")
            .1
            .remove(0),
    );
    let claim = unit.claims[0].clone();
    let row = Row {
        key: "k".into(),
        code: unit.code(&claim),
        unit: unit.clone(),
        claim: claim.clone(),
        research: String::new(),
    };
    cur.insert(row.clone());
    cur.insert(row);
    assert_eq!(cur.len(), 1);
    let mut idx: Map<String, Value> = Map::new();
    idx.insert("k".into(), json!("not an object"));
    let mut store = Map::new();
    assert_eq!(
        backfill(&cur, &mut idx, &root.join("research/questions"), &mut store).unwrap(),
        0
    );
    assert_eq!(backfill_sections(&cur, &mut idx, &mut store), 0);
    let mut idx: Map<String, Value> = Map::new();
    idx.insert("k".into(), json!({"code": "a", "core": "c"}));
    idx.insert("j".into(), json!({"code": "a"}));
    idx.insert("z".into(), json!({"code": "a"}));
    let old = HashMap::from([
        ("k".to_owned(), ("a".to_owned(), "c".to_owned())),
        ("j".to_owned(), ("a".to_owned(), "c".to_owned())),
    ]);
    let new = HashMap::from([
        ("k".to_owned(), ("b".to_owned(), "d".to_owned())),
        ("j".to_owned(), ("a".to_owned(), "c".to_owned())),
    ]);
    assert_eq!(refingerprint(&mut idx, &old, &new), 1);
    assert_eq!(idx["k"], json!({"code": "b", "core": "d"}));
}
