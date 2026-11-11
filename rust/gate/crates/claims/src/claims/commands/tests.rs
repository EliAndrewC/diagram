//! Each command end to end on the fixture: what is owed, a bundle and its reply recorded, the triage and its reply, the backfills, the
//! accept, the report and the gate.

use std::path::Path;

use serde_json::{json, Value};

use super::{backfill_sections, path_text};
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
fn what_is_owed_then_bundled_then_recorded() {
    let root = fixture("claims-cmd-owed");
    py_units(
        &root,
        &[(
            "TABLE",
            "constant",
            &["table - research/questions/0001-gap.html: 12 ft"],
            false,
        )],
        &[
            (
                "helper",
                "function",
                &["help - GUESS: 3 households, stricter than the page"],
                false,
            ),
            ("plumb", "function", &["plumbing - NONE"], true),
        ],
    );
    let got = claims(&root, &["owed"]);
    assert_eq!(got.code, 0);
    for want in [
        "claims-form: l7r/diagram/m.py module docstring: a module error - the gate's test_claims_coverage fails on it",
        "claims-label: l7r/diagram/m.py::helper#help - its account says the code departs",
        "new              l7r/diagram/m.py::TABLE#table",
        "claims-owed: l7r/diagram/m.py::plumb is new and carries only its module's NONE",
        "owe impl-drift; bundle per file",
    ] {
        assert!(got.stdout.contains(want), "{want}\n{}", got.stdout);
    }
    let out = root.join("b");
    let o = out.to_string_lossy().into_owned();
    let got = claims(
        &root,
        &[
            "bundle",
            "--module",
            "lib.rs",
            "--out",
            &o,
            "--with",
            "rust/phases/src/lib.rs::helper,rust/phases/src/lib.rs::helper",
            "--pages",
            "research/questions/0002-other.drawing.html",
        ],
    );
    assert_eq!(got.code, 0, "{}", got.stderr);
    let manifest = std::fs::read_to_string(out.join("MANIFEST.md")).unwrap();
    for want in [
        "## UNIT rust/phases/src/lib.rs::GAP (constant, rust/phases/src/lib.rs:10)",
        "## CONTEXT rust/phases/src/lib.rs::helper",
        "- `questions/0002-other.drawing.html.txt` - Other",
        "```rust",
    ] {
        assert!(manifest.contains(want), "{want}\n{manifest}");
    }
    let got = claims(
        &root,
        &[
            "bundle",
            "--units",
            "l7r/diagram/m.py::TABLE#table,l7r/diagram/m.py::helper#help",
            "--out",
            &o,
        ],
    );
    assert_eq!(got.code, 0, "{}", got.stderr);
    let manifest = std::fs::read_to_string(out.join("MANIFEST.md")).unwrap();
    assert!(
        manifest.contains("## CONTEXT l7r/diagram/m.py::helper")
            && manifest.contains("```python\ndef GAP(): pass"),
    );
    record_and_report(&root, &out);
}

/// The second half: the bundle's reply recorded in each form, then reported with and without the deferred.
fn record_and_report(root: &Path, out: &Path) {
    let root = root.to_path_buf();
    let o = out.to_string_lossy().into_owned();
    let units: Value =
        serde_json::from_str(&std::fs::read_to_string(out.join("units.json")).unwrap()).unwrap();
    assert_eq!(
        units["l7r/diagram/m.py::TABLE#table"]["uid"],
        "l7r/diagram/m.py::TABLE"
    );
    let r = reply(&root, "VERDICT `l7r/diagram/m.py::TABLE#table` DRIFTED - [outside the change] see research/questions/0001-...-gap.html [§1, §9]\nVERDICT l7r/diagram/m.py::helper#help - IN-STEP: fine [§]\nVERDICT nope#x IN-STEP - x\nVERDICT broken\nVERDICT l7r/diagram/m.py::helper#help IN-STEP - research/questions/0099-none.html\nUNCLAIMED l7r/diagram/m.py::TABLE - a decision\nUNCLAIMED no.py::x - refused\n");
    let got = claims(&root, &["record", "--bundle", &o, "--reply", &r]);
    assert_eq!(got.code, 3, "{}", got.stderr);
    assert!(got.stdout.contains("claims-checked: UNCLAIMED l7r/diagram/m.py::TABLE - a decision: write a claim for it, then check it"), "{}", got.stdout);
    assert!(got
        .stdout
        .contains("claims-checked: refused: UNCLAIMED `no.py::x` is not a unit of this bundle"));
    assert!(got.stdout.contains("claims-checked: 2 of 2 recorded"));
    assert!(
        got.stderr
            .contains("REFUSED line - no verdict it can read: VERDICT broken")
            && got.stderr.contains("not a claim of this bundle")
            && got.stderr.contains("no such question file")
    );
    let ix = index(&root);
    assert_eq!(ix["l7r/diagram/m.py::TABLE#table"]["verdict"], "DRIFTED");
    assert_eq!(ix["l7r/diagram/m.py::TABLE#table"]["outside"], true);
    assert_eq!(
        ix["l7r/diagram/m.py::TABLE#a decision"]["verdict"],
        "UNCLAIMED"
    );
    let got = claims(&root, &["report"]);
    assert!(got
        .stdout
        .starts_with("claims: 9 in scope; IN-STEP 1, DRIFTED 1, UNCLAIMED 1; owed 7"),);
    std::fs::write(
        root.join("dev/claims-deferred.json"),
        "{\"units\": [\"l7r/diagram/m.py::TABLE\"]}",
    )
    .unwrap();
    let got = claims(&root, &["report"]);
    assert!(got
        .stdout
        .contains("(2 DEFERRED findings not listed: make claims-report ALL=1 lists them)"),);
    let got = claims(&root, &["report", "--all"]);
    assert!(got.stdout.contains(
        "  DEFERRED       l7r/diagram/m.py::TABLE#table - see research/questions/0001-gap.html"
    ),);
    let empty = reply(&root, "  \n");
    let got = claims(&root, &["record", "--bundle", &o, "--reply", &empty]);
    assert_eq!(
        (
            got.code,
            got.stderr
                .contains("claims-checked: refused - no reply text")
        ),
        (2, true)
    );
}

#[test]
fn a_bundle_is_refused_on_what_it_cannot_name() {
    let root = fixture("claims-cmd-refuse");
    let got = claims(&root, &["bundle", "--units", "nope#x"]);
    assert_eq!(
        (got.code, got.stderr.as_str()),
        (2, "claims-bundle: no such claim(s): nope#x\n")
    );
    record_all(&root);
    let got = claims(&root, &["bundle", "--owed"]);
    assert_eq!(
        (got.code, got.stderr.as_str()),
        (2, "claims-bundle: no such claim(s): (none selected)\n")
    );
    let got = claims(
        &root,
        &[
            "bundle",
            "--module",
            "rust/phases/src/lib.rs",
            "--reason",
            "one",
        ],
    );
    assert_eq!(got.code, 3);
    assert!(got
        .stderr
        .contains("of these claims are not owed (first: rust/phases/src/lib.rs::GAP#gap)"));
    let o = root.join("b2").to_string_lossy().into_owned();
    let got = claims(
        &root,
        &[
            "bundle",
            "--units",
            "rust/phases/src/lib.rs::GAP#gap",
            "--reason",
            "a re check",
            "--out",
            &o,
            "--pages",
            "0099-none.html",
        ],
    );
    assert_eq!(got.code, 1);
    assert!(got
        .stderr
        .contains("PAGES: no question file 0099-none.html"));
    let got = claims(
        &root,
        &[
            "bundle",
            "--units",
            "rust/phases/src/lib.rs::GAP#gap",
            "--reason",
            "a re check",
            "--out",
            &o,
            "--with",
            "rust/phases/src/lib.rs::NOPE",
        ],
    );
    assert!(got.stderr.contains("no `NOPE` in rust/phases/src/lib.rs"));
    let got = claims(
        &root,
        &[
            "bundle",
            "--units",
            "docs/buildings.md::Walls#walls",
            "--reason",
            "a re check",
        ],
    );
    assert_eq!(got.code, 0);
    let manifest = l7r_gate_core::record::bundle::default_root()
        .join("claims-docs-buildings-md-walls-walls/MANIFEST.md");
    assert!(got.stdout.starts_with(&manifest.display().to_string()));
    assert!(got
        .stdout
        .contains("claims-bundle: re-check of 1 claim(s) not owed, because: a re check"));
}

#[test]
fn the_backfills_rekey_and_refingerprint() {
    let root = fixture("claims-cmd-backfill");
    py_units(
        &root,
        &[("TABLE", "constant", &["table - NONE"], false)],
        &[],
    );
    record_all(&root);
    let mut ix = index(&root);
    let key = "rust/phases/src/lib.rs::GAP#gap";
    ix[key].as_object_mut().unwrap().remove("pages");
    let walls = "docs/buildings.md::Walls#walls";
    ix[walls].as_object_mut().unwrap().remove("section");
    std::fs::write(root.join("dev/claims-index.json"), ix.to_string()).unwrap();
    let got = claims(&root, &["backfill"]);
    assert_eq!(
        got.stdout,
        "claims-backfill: 1 row(s) given the pages they were checked at\n"
    );
    let got = claims(&root, &["backfill-sections"]);
    assert_eq!(got.stdout, "claims-backfill-sections: 0 section claim(s) re-keyed to their own line; none owed by it\n");
    let src = std::fs::read_to_string(root.join("rust/phases/src/lib.rs")).unwrap();
    let start = src.find("pub fn helper").unwrap();
    std::fs::write(
        root.join("rust/phases/src/lib.rs"),
        [&src[..start], &src[start + 32..]].concat(),
    )
    .unwrap();
    put(
        &root,
        "rust/phases/src/moved.rs",
        "//! Research:\n//!     plumbing - NONE\n\npub fn helper() -> u32 {\n    1\n}\n",
    );
    let got = claims(&root, &["rekey"]);
    assert_eq!(
        got.stdout,
        "claims-rekey: 1 claim row(s) carried to the file their unit moved to\n"
    );
    assert!(index(&root)["rust/phases/src/moved.rs::helper#plumbing"].is_object());
    let mut ix = index(&root);
    ix["l7r/diagram/m.py::TABLE#table"]["code"] = json!(crate::claims::units::sha(
        "core-TABLE-nostar\x1ftable - NONE"
    ));
    std::fs::write(root.join("dev/claims-index.json"), ix.to_string()).unwrap();
    let got = claims(&root, &["refingerprint"]);
    assert_eq!(got.stdout, "claims-refingerprint: 1 claim row(s) carried to the fingerprint the star re-exports give, their code otherwise unchanged\n");
    let mut cur = crate::claims::index::Cur::default();
    let mut store = serde_json::Map::new();
    let mut idx = serde_json::Map::new();
    assert_eq!(backfill_sections(&cur, &mut idx, &mut store), 0);
    let unit = std::rc::Rc::new(
        crate::claims::units::doc_units(crate::claims::tests::BUILDINGS, "docs/buildings.md", None)
            .remove(0),
    );
    let claim = unit.claims[0].clone();
    let old = crate::claims::units::sha(&format!("{}\x1f{}", unit.core, claim.normalized()));
    cur.insert(crate::claims::index::Row {
        key: "k".into(),
        code: unit.code(&claim),
        unit,
        claim,
        research: String::new(),
    });
    idx.insert("k".into(), json!({"code": old}));
    assert_eq!(backfill_sections(&cur, &mut idx, &mut store), 1);
    assert_eq!(store.len(), 1);
}

#[test]
fn the_triage_clears_what_a_page_move_alone_owes_and_bundles_the_rest() {
    let root = fixture("claims-cmd-triage");
    py_units(&root, &[], &[]);
    record_all(&root);
    commit(&root, "recorded");
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    let page = root.join("research/questions/0001-gap.html");
    std::fs::write(&page, "<h2 id=\"gap\">The gap</h2>\n<p class=\"intro\">Why.</p>\n<p>The gap is 12 ft.</p>\n<p>A second block.</p>\n<p>A third, new.</p>\n").unwrap();
    let got = claims(&root, &["triage"]);
    assert!(got
        .stdout
        .contains("claim(s) cleared without a triage - a page each cites moved"),);
    let got = claims(&root, &["triage-owed"]);
    assert_eq!(got.stdout, "0\n");
    let lib = std::fs::read_to_string(root.join("rust/phases/src/lib.rs")).unwrap();
    std::fs::write(
        root.join("rust/phases/src/lib.rs"),
        lib.replace("let y = 3.25;", "let y = 3.5;")
            .replace("a[1] + 42", "a[1] + 43"),
    )
    .unwrap();
    let buildings = std::fs::read_to_string(root.join("docs/buildings.md")).unwrap();
    std::fs::write(
        root.join("docs/buildings.md"),
        buildings.replace("Walls stand.", "Walls stand tall."),
    )
    .unwrap();
    let got = claims(&root, &["owed"]);
    assert!(got.stdout.contains("code triage") && got.stdout.contains("section triage"),);
    let t = root.join("t");
    let to = t.to_string_lossy().into_owned();
    let got = claims(&root, &["triage", "--out", &to]);
    assert!(got
        .stdout
        .contains("claims-triage: 4 claim(s); dispatch the `claims-triage` agent"));
    let manifest = std::fs::read_to_string(t.join("MANIFEST.md")).unwrap_or_default();
    assert!(
        manifest.contains("(a procedure section; the claims' own lines did not change)")
            && manifest.contains("```diff"),
    );
    let r = reply(
        &root,
        "TOUCHES `docs/buildings.md::Walls#walls` - it bears\nTOUCHES nope#x - refused\n",
    );
    let got = claims(&root, &["triaged", "--bundle", &to, "--reply", &r]);
    assert!(
        got.stdout
            .contains("claims-triaged: touched: docs/buildings.md::Walls#walls - it bears")
            && got
                .stdout
                .contains("claims-triaged: refused: `nope#x` is not a claim of this triage"),
    );
    assert!(got
        .stdout
        .contains("sent on to impl-drift (1 named by the reply"),);
    let empty = reply(&root, "");
    assert_eq!(
        claims(&root, &["triaged", "--bundle", &to, "--reply", &empty]).code,
        2
    );
    assert_eq!(
        index(&root)["docs/buildings.md::Walls#walls"]["triage"],
        "touched"
    );
}

#[test]
fn a_small_triage_goes_straight_to_impl_drift_and_a_bare_one_to_its_full_check() {
    let root = fixture("claims-cmd-small");
    py_units(&root, &[], &[]);
    record_all(&root);
    commit(&root, "recorded");
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    let lib = std::fs::read_to_string(root.join("rust/phases/src/lib.rs")).unwrap();
    std::fs::write(
        root.join("rust/phases/src/lib.rs"),
        lib.replace("let y = 3.25;", "let y = 3.5;"),
    )
    .unwrap();
    let o = root.join("s").to_string_lossy().into_owned();
    let got = claims(&root, &["triage", "--out", "/proc/no/such/dir"]);
    assert_eq!(got.code, 1);
    let got = claims(&root, &["triage", "--out", &o]);
    assert!(got.stdout.contains(
        "claims-triage: a claims triage of 1 claim(s), at most 3, goes straight to impl-drift"
    ),);
    assert!(
        std::fs::read_to_string(root.join("dev/claims-triage-skips.jsonl"))
            .unwrap()
            .contains("\"claims\": 1")
    );
    assert_eq!(path_text("a//b/./c/"), "a/b/c");
    assert_eq!(
        (
            path_text(""),
            path_text("/"),
            path_text("//x"),
            path_text(".")
        ),
        (
            ".".to_owned(),
            "/".to_owned(),
            "//x".to_owned(),
            ".".to_owned()
        )
    );
}
