//! The commands' other paths: the coverage, the accept, the counter-only clear with no merge base, a bundle's own files missing, a
//! triage every claim of which is owed in full, the helpers with nothing to carry.

use std::collections::HashMap;
use std::path::Path;

use serde_json::{json, Map, Value};

use super::{backfill, backfill_sections, refingerprint};
use crate::claims::index::{Cur, Row};
use crate::claims::tests::{claims, commit_as_origin, fixture, record_all, write_recorded};
use crate::record::testkit::{git, put};

fn index(root: &Path) -> Value {
    serde_json::from_str(&std::fs::read_to_string(root.join("dev/claims-index.json")).unwrap())
        .unwrap()
}

fn reply(root: &Path, text: &str) -> String {
    let p = root.join("reply.txt");
    std::fs::write(&p, text).unwrap();
    p.to_string_lossy().into_owned()
}

/// The fixture with its procedure's last section claimed, Python-free: the coverage's and the accept's tree (feature 449 T167 split the
/// one test of both, over FR-008's tenth of a second, into three on a tree each; none reads what another wrote).
fn covered(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = fixture(tag);
    let buildings = std::fs::read_to_string(root.join("docs/buildings.md")).unwrap();
    std::fs::write(
        root.join("docs/buildings.md"),
        buildings.replace("No claim here.", "<!-- Research: deep - NONE -->"),
    )
    .unwrap();
    root
}

/// [`covered`], every claim recorded, and `GAP` turned DRIFTED.
fn accepting(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = covered(tag);
    record_all(&root);
    let mut ix = index(&root);
    ix["rust/phases/src/lib.rs::GAP#gap"]["verdict"] = json!("DRIFTED");
    std::fs::write(root.join("dev/claims-index.json"), ix.to_string()).unwrap();
    root
}

#[test]
fn the_coverage_and_the_accept() {
    let root = covered("claims-more-cover");
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
}

/// `make static`'s form check (feature 449 T169): a new crate's unit with no claim is named, with the fix, before the landing.
#[test]
fn the_rust_form_check_names_a_new_crate_s_unclaimed_unit_and_the_fix() {
    let root = covered("claims-more-form");
    let got = claims(&root, &["coverage", "--rust"]);
    assert_eq!(
        (got.code, got.stdout.as_str()),
        (
            0,
            "claims-form: every unit of the Rust crates the claims walk reads carries a claim\n"
        )
    );
    put(
        &root,
        "rust/mode_x/src/lib.rs",
        "//! A new engine crate.\n\npub fn f() {}\n",
    );
    // a tooling crate is not walked, so its unit owes nothing
    put(&root, "rust/gate/src/lib.rs", "pub fn g() {}\n");
    let got = claims(&root, &["coverage", "--rust"]);
    assert_eq!(got.code, 1);
    assert!(
        got.stdout
            .starts_with("rust/mode_x/src/lib.rs:3 f: no claim - add a `Research:` claim"),
        "{}",
        got.stdout
    );
    assert!(!got.stdout.contains("rust/gate/"));
    assert!(got
        .stdout
        .contains("claims-form: 1 problem(s) in the Rust crates the claims walk reads"));
    assert!(got
        .stdout
        .contains("`//!     <label> - NONE: <why it decides nothing physical>`"));
    put(
        &root,
        "rust/mode_x/src/lib.rs",
        "//! A new engine crate.\n//!\n//! Research:\n//!     the crate - NONE: decides nothing physical\n\npub fn f() {}\n",
    );
    assert_eq!(claims(&root, &["coverage", "--rust"]).code, 0);
}

#[test]
fn an_accept_records_in_step_or_keeps_a_known_drift_and_refuses_what_it_cannot_name() {
    let root = accepting("claims-more-accept");
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
}

#[test]
fn a_recorded_tree_owes_nothing_and_an_unparsable_claim_is_no_unit() {
    let root = accepting("claims-more-recorded");
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

/// A recorded tree on `origin/main` whose Rust engine then changed (the Python units the counter-only clear read, and its test, left
/// with the engine's Python, feature 449 T158; the Rust clear is `counters`' test).
fn countered(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = fixture(tag);
    // the recording written as `record_all` writes it, pinned by `the_recorded_rust_units_are_what_record_all_writes` (feature 449 T167)
    write_recorded(&root, "{}", "{}");
    commit_as_origin(&root, "recorded");
    let lib = std::fs::read_to_string(root.join("rust/phases/src/lib.rs")).unwrap();
    std::fs::write(
        root.join("rust/phases/src/lib.rs"),
        lib.replace("let y = 3.25;", "let y = 3.5;"),
    )
    .unwrap();
    root
}

#[test]
fn with_no_merge_base_nothing_is_cleared_and_no_figure_named() {
    let root = countered("claims-more-counter-bare");
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
}

/// The second half of the lost files' test, on a tree of its own (feature 449 T167: the two read nothing of each other's, and took over
/// FR-008's tenth of a second together).
#[test]
fn a_bundle_missing_its_blocks_records_and_a_triage_reply_naming_nothing_owes_the_forced() {
    let root = fixture("claims-more-files-blocks");
    let b = root.join("b");
    let o = b.to_string_lossy().into_owned();
    let r = reply(
        &root,
        "VERDICT rust/phases/src/lib.rs::GAP#gap IN-STEP - fine\n",
    );
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
    let r = reply(&root, "NONE\n");
    let got = claims(&root, &["triaged", "--bundle", &o, "--reply", &r]);
    assert!(got.stdout.ends_with("claims-triaged: 1 of 2 sent on to impl-drift (0 named by the reply, 1 cx.owed in full: a removed block's words could not be shown); the rest cleared\n"));
}

#[test]
fn a_triage_with_nothing_to_show_owes_every_claim_in_full() {
    let root = fixture("claims-more-forced");
    record_all(&root);
    let lib = std::fs::read_to_string(root.join("rust/phases/src/lib.rs")).unwrap();
    let lib = lib
        .replace("let y = 3.25;", "let y = 3.5;")
        .replace("a[1] + 42", "a[1] + 43")
        .replace("pub const GAP: f64 = 12.0;", "pub const GAP: f64 = 12.5;")
        .replace("    1\n}", "    2\n}");
    std::fs::write(root.join("rust/phases/src/lib.rs"), lib).unwrap();
    commit_as_origin(&root, "all at once");
    let got = claims(&root, &["triage"]);
    assert!(got
        .stdout
        .starts_with("claims-triage: all 4 claim(s) are cx.owed in full"));
    assert!(l7r_gate_core::record::bundle::default_root()
        .join("claims-triage/triage.json")
        .is_file());
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
    assert_eq!(refingerprint(&mut idx, &old, &new), ["k"]);
    assert_eq!(idx["k"], json!({"code": "b", "core": "d"}));
    // an UNCLAIMED row holds its unit's core as its code: carried by its unit's, where it is the old one (feature 449 T166)
    let mut idx: Map<String, Value> = Map::new();
    idx.insert(
        "u#a decision".into(),
        json!({"code": "c", "core": "c", "verdict": "UNCLAIMED"}),
    );
    idx.insert(
        "v#a decision".into(),
        json!({"code": "x", "core": "x", "verdict": "UNCLAIMED"}),
    );
    idx.insert("u#not unclaimed".into(), json!({"code": "c"}));
    let unit = |core: &str| (String::new(), core.to_owned());
    let old = HashMap::from([("u".to_owned(), unit("c")), ("v".to_owned(), unit("c"))]);
    let new = HashMap::from([("u".to_owned(), unit("d")), ("v".to_owned(), unit("d"))]);
    assert_eq!(refingerprint(&mut idx, &old, &new), ["u#a decision"]);
    assert_eq!(
        idx["u#a decision"],
        json!({"code": "d", "core": "d", "verdict": "UNCLAIMED"})
    );
    // a relabel answered since its check: its code holds the claim as recorded, carried by that text
    let at = |core: &str| crate::claims::units::sha(&format!("{core}\x1fthen said"));
    let mut idx: Map<String, Value> = Map::new();
    idx.insert(
        "k#x".into(),
        json!({"code": at("c"), "core": "c", "claim": "then said", "verdict": "MISLABELED"}),
    );
    idx.insert(
        "j#x".into(),
        json!({"code": "changed", "core": "c", "claim": "then said"}),
    );
    let old = HashMap::from([
        ("k#x".to_owned(), ("now-old".to_owned(), "c".to_owned())),
        ("j#x".to_owned(), ("now-old".to_owned(), "c".to_owned())),
    ]);
    let new = HashMap::from([
        ("k#x".to_owned(), ("now-new".to_owned(), "d".to_owned())),
        ("j#x".to_owned(), ("now-new".to_owned(), "d".to_owned())),
    ]);
    assert_eq!(refingerprint(&mut idx, &old, &new), ["k#x"]);
    assert_eq!(idx["k#x"]["code"], at("d"));
    assert_eq!(idx["j#x"]["code"], "changed");
}
