//! A Rust unit's core holds the constants it reads (feature 449 T166): a changed constant moves every reader's core, a constant moved
//! between files moves none, a unit reading none keeps the core it had, and the walk without reads is the fingerprint before T166.

use super::{core, values};
use crate::claims::context::Tables;
use crate::claims::units::{all_rust_units, rust_core, Unit};
use crate::record::testkit::put;

const LIB: &str = "use crate::far::FAR;
/// Research: the gap - NONE: plumbing
pub const GAP: f64 = 12.0;
/// Research: the reach - NONE: plumbing
pub fn reach(x: f64) -> f64 {
    x + GAP + FAR + Thing::INNER + GAP
}
/// Research: the twice - NONE: plumbing
pub const TWICE: f64 = GAP * 2.0;
/// Research: no reads - NONE: plumbing
pub fn plain(x: f64) -> f64 {
    x * 2.0
}
pub struct Thing;
impl Thing {
    pub const INNER: u32 = 3;
}
";

fn cores(root: &std::path::Path, reads: bool) -> std::collections::HashMap<String, String> {
    all_rust_units(root, "", reads)
        .unwrap()
        .into_iter()
        .map(|(u, _): (Unit, _)| (u.qualname, u.core))
        .collect()
}

#[test]
fn a_units_core_holds_the_value_of_each_constant_it_reads() {
    let root = crate::checks::scratch("claims-reads");
    put(&root, "rust/eng/src/lib.rs", LIB);
    put(&root, "rust/eng/src/far.rs", "pub const FAR: f64 = 1.5;\n");
    let mut tables = Tables::default();
    let body = "pub fn reach(x: f64) -> f64 {\n    x + GAP + FAR + Thing::INNER + GAP\n}";
    let got = values(&mut tables, &root, "rust/eng/src/lib.rs", "reach", body);
    let names: Vec<&str> = got
        .split('\x1e')
        .map(|v| v.split('=').next().unwrap())
        .collect();
    // sorted, once each, keyed by the constant's own name (an associated one by its type's), never by its file
    assert_eq!(names, ["FAR", "GAP", "Thing.INNER"]);
    assert_eq!(core(body, ""), rust_core(body));
    assert_ne!(core(body, &got), rust_core(body));

    let before = cores(&root, true);
    let old = cores(&root, false);
    // a unit that reads no constant keeps the core it had before T166; a reader's moves
    assert_eq!(before["plain"], old["plain"]);
    assert_eq!(before["GAP"], old["GAP"]);
    assert_ne!(before["reach"], old["reach"]);
    assert_ne!(before["TWICE"], old["TWICE"]);

    // a constant's value changed: each reader owes, the rest do not
    put(
        &root,
        "rust/eng/src/far.rs",
        "pub const FAR: f64 = 2.5; // moved\n",
    );
    let after = cores(&root, true);
    assert_ne!(after["reach"], before["reach"]);
    assert_eq!(after["TWICE"], before["TWICE"]);
    assert_eq!(after["plain"], before["plain"]);

    // its type or visibility changed, or it moved to another file: no reader owes (the Python dumps the value alone, by name)
    put(&root, "rust/eng/src/far.rs", "const FAR: f32 = 2.5;\n");
    assert_eq!(cores(&root, true)["reach"], after["reach"]);
    std::fs::remove_file(root.join("rust/eng/src/far.rs")).unwrap();
    put(
        &root,
        "rust/eng/src/moved.rs",
        "pub const FAR: f64 = 2.5;\n",
    );
    let lib = LIB.replace("use crate::far::FAR;", "use crate::moved::FAR;");
    put(&root, "rust/eng/src/lib.rs", &lib);
    assert_eq!(cores(&root, true)["reach"], after["reach"]);

    // a constant reading another holds that one's value, one level
    let lib = lib.replace("GAP: f64 = 12.0", "GAP: f64 = 13.0");
    put(&root, "rust/eng/src/lib.rs", &lib);
    assert_ne!(cores(&root, true)["TWICE"], before["TWICE"]);
}

#[test]
fn a_rows_reads_are_set_dropped_or_left() {
    let mut row = serde_json::Map::new();
    super::stamp(&mut row, Some("r"));
    assert_eq!(row["reads"], "r");
    super::stamp(&mut row, None);
    assert_eq!(row["reads"], "r");
    super::stamp(&mut row, Some(""));
    assert!(row.get("reads").is_none());
}

/// Every claim of `root` recorded IN-STEP as a check records it, in process: under the fingerprint before T166 (`reads` off: no
/// constant reads, as rows were before the migration), or the current one with the body and the reads a check records.
fn recorded(root: &std::path::Path, reads: bool) -> serde_json::Value {
    let mut pairs = all_rust_units(root, "", reads).unwrap();
    for (doc, tops) in crate::claims::units::PROCEDURES {
        let text = std::fs::read_to_string(root.join(doc)).unwrap_or_default();
        pairs.extend(
            crate::claims::units::doc_units(&text, doc, tops)
                .into_iter()
                .map(|u| (u, Vec::new())),
        );
    }
    let cur = crate::claims::index::rows_of(pairs, &root.join("research/questions")).unwrap();
    let mut out = serde_json::Map::new();
    for r in cur.iter() {
        let mut row = serde_json::json!({"code": r.code, "core": r.unit.core, "research": r.research,
            "claim": r.claim.normalized(), "verdict": "IN-STEP"});
        if reads {
            row["body"] = serde_json::json!(crate::claims::index::body_of(root, &r.unit).unwrap());
            if !r.unit.reads.is_empty() {
                row["reads"] = serde_json::json!(r.unit.reads);
            }
        }
        out.insert(r.key.clone(), row);
    }
    serde_json::Value::Object(out)
}

fn no_python(tag: &str) -> l7r_shared::tempdir::TempDir {
    crate::claims::tests::fixture_with(tag, &|root| {
        std::fs::remove_file(root.join("l7r/diagram/m.py")).unwrap();
    })
}

const READER: &str = "rust/phases/src/lib.rs::reach#reach";

/// The migration (feature 449 T166): a row recorded before T166 - its code the old scheme's, no reads - is carried to the new one with
/// its reads, the run recorded, and nothing is owed.
#[test]
fn the_migration_carries_an_unchanged_reader_owing_nothing() {
    use crate::claims::tests::claims;
    let root = no_python("claims-reads-migrate");
    let path = root.join("dev/claims-index.json");
    put(
        &root,
        "dev/claims-index.json",
        &recorded(&root, false).to_string(),
    );
    let got = claims(&root, &["refingerprint"]);
    assert!(got
        .stdout
        .starts_with("claims-refingerprint: 1 claim row(s)"));
    let ix: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(&path).unwrap()).unwrap();
    assert_eq!(ix[READER]["reads"], recorded(&root, true)[READER]["reads"]);
    assert!(root.join(super::MIGRATIONS).is_file());
    assert_eq!(
        claims(&root, &["owed"]).stdout.lines().last(),
        Some("claims-owed: no claim is owed")
    );
}

/// A constant a checked unit reads changed: the unit is owed, though its own text - its row's body - is unchanged (feature 449 T166).
#[test]
fn a_changed_constant_owes_each_reader() {
    use crate::claims::tests::claims;
    let root = no_python("claims-reads-owed");
    put(
        &root,
        "dev/claims-index.json",
        &recorded(&root, true).to_string(),
    );
    let lib = std::fs::read_to_string(root.join("rust/phases/src/lib.rs")).unwrap();
    put(
        &root,
        "rust/phases/src/lib.rs",
        &lib.replace("GAP: f64 = 12.0", "GAP: f64 = 13.0"),
    );
    let got = claims(&root, &["owed"]).stdout;
    assert!(got.contains(&format!("code triage      {READER}")));
}
