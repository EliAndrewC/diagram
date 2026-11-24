//! Each command end to end on the fixture: what is owed, a bundle and its reply recorded, the triage and its reply, the backfills, the
//! accept, the report and the gate.

use std::path::Path;

use serde_json::{json, Value};

use super::{backfill_sections, path_text};
use crate::claims::tests::{claims, commit_as_origin, fixture, record_all};
use crate::record::testkit::put;

fn index(root: &Path) -> Value {
    serde_json::from_str(&std::fs::read_to_string(root.join("dev/claims-index.json")).unwrap())
        .unwrap()
}

fn reply(root: &Path, text: &str) -> String {
    let p = root.join("reply.txt");
    std::fs::write(&p, text).unwrap();
    p.to_string_lossy().into_owned()
}

/// A second Rust file beside the fixture's: a claimed table, a helper whose account departs, an inherited plumbing unit, and a module
/// doc (the `.py` half these stood in, feature 449 T158).
fn owed_units(root: &Path) {
    put(
        root,
        "rust/phases/src/owed.rs",
        "//! Research:\n//!     plumbing - NONE\n\n/// Research: table - research/questions/0001-gap.html: 12 ft\npub const TABLE: u32 = 12;\n\n/// Research: help - GUESS: 3 households, stricter than the page\npub fn assist() -> u32 {\n    TABLE\n}\n\npub fn plumb() {}\n",
    );
}

#[test]
fn what_is_owed_then_bundled_then_recorded() {
    let root = fixture("claims-cmd-owed");
    owed_units(&root);
    let got = claims(&root, &["owed"]);
    assert_eq!(got.code, 0);
    for want in [
        "claims-form: docs/buildings.md:14 Deep: no claim - add a `<!-- Research: <label> - <backing> -->` comment - the gate's test_claims_coverage fails on it",
        "claims-label: rust/phases/src/owed.rs::assist#help - its account says the code departs",
        "new              rust/phases/src/owed.rs::TABLE#table",
        "claims-owed: rust/phases/src/owed.rs::plumb is new and carries only its module's NONE",
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
}

/// The test's second half (feature 449 T167: the two took over FR-008's tenth of a second together, and the second reads only the
/// bundle of `owed.rs`'s units, which it makes on a fixture of its own): those units bundled, the reply recorded, reported.
#[test]
fn a_bundle_of_units_is_recorded_and_reported() {
    let root = fixture("claims-cmd-recorded");
    owed_units(&root);
    let out = root.join("b");
    let o = out.to_string_lossy().into_owned();
    let got = claims(
        &root,
        &[
            "bundle",
            "--units",
            "rust/phases/src/owed.rs::TABLE#table,rust/phases/src/owed.rs::assist#help",
            "--out",
            &o,
        ],
    );
    assert_eq!(got.code, 0, "{}", got.stderr);
    let manifest = std::fs::read_to_string(out.join("MANIFEST.md")).unwrap();
    assert!(
        manifest.contains("## UNIT rust/phases/src/owed.rs::assist")
            && manifest.contains("```rust\n"),
    );
    record_and_report(&root, &out);
}

/// Feature 451 T218: a reply that says the pages are silent is not recorded until the record's nearest pages for its words are in
/// the bundle - the line is held, the page named with the command that adds it, and the same line recorded once it was read.
#[test]
fn a_silent_finding_is_held_until_the_record_s_nearest_pages_are_bundled() {
    let root = fixture("claims-cmd-silent");
    owed_units(&root);
    let page = "0003-households.html";
    put(
        &root,
        &format!("research/questions/{page}"),
        "<h1>Households</h1>\n<p>A hamlet's helper serves three households.</p>\n",
    );
    let key = "rust/phases/src/owed.rs::assist#help";
    let (out, wide) = (root.join("b"), root.join("b2"));
    let (o, w) = (
        out.to_string_lossy().into_owned(),
        wide.to_string_lossy().into_owned(),
    );
    assert_eq!(
        claims(&root, &["bundle", "--units", key, "--out", &o]).code,
        0
    );
    let r = reply(
        &root,
        &format!(
            "VERDICT {key} NEEDS-RESEARCH - no page says how many households a helper serves [§]\n"
        ),
    );
    let got = claims(&root, &["record", "--bundle", &o, "--reply", &r]);
    assert_eq!(got.code, 3, "{}", got.stderr);
    assert!(
        got.stderr.contains(&format!("claims-checked: HELD line - it says the pages are silent, and the record's nearest pages for its words are not in the bundle ({page}")),
        "{}",
        got.stderr
    );
    assert!(got
        .stderr
        .contains(&format!("make claims-bundle UNITS=\"{key}\" PAGES=\"")));
    assert!(
        got.stdout.contains("claims-checked: 0 of 1 recorded"),
        "{}",
        got.stdout
    );
    let pages = got
        .stderr
        .split("PAGES=\"")
        .nth(1)
        .unwrap()
        .split('"')
        .next()
        .unwrap()
        .to_owned();
    assert_eq!(
        claims(
            &root,
            &["bundle", "--units", key, "--out", &w, "--pages", &pages]
        )
        .code,
        0
    );
    let got = claims(&root, &["record", "--bundle", &w, "--reply", &r]);
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(
        got.stdout.contains("claims-checked: 1 of 1 recorded"),
        "{}",
        got.stdout
    );
}

/// The second half: the bundle's reply recorded in each form, then reported with and without the deferred.
fn record_and_report(root: &Path, out: &Path) {
    let root = root.to_path_buf();
    let o = out.to_string_lossy().into_owned();
    let units: Value =
        serde_json::from_str(&std::fs::read_to_string(out.join("units.json")).unwrap()).unwrap();
    assert_eq!(
        units["rust/phases/src/owed.rs::TABLE#table"]["uid"],
        "rust/phases/src/owed.rs::TABLE"
    );
    let r = reply(&root, "VERDICT `rust/phases/src/owed.rs::TABLE#table` DRIFTED - [outside the change] see research/questions/0001-...-gap.html; fix: code; effect: a finding contradicted [§1, §9]\nVERDICT rust/phases/src/owed.rs::assist#help - IN-STEP: fine [§]\nVERDICT nope#x IN-STEP - x\nVERDICT broken\nVERDICT rust/phases/src/owed.rs::assist#help IN-STEP - research/questions/0099-none.html\nUNCLAIMED rust/phases/src/owed.rs::TABLE - a decision\nUNCLAIMED no.py::x - refused\n");
    let got = claims(&root, &["record", "--bundle", &o, "--reply", &r]);
    assert_eq!(got.code, 3, "{}", got.stderr);
    assert!(got.stdout.contains("claims-checked: UNCLAIMED rust/phases/src/owed.rs::TABLE - a decision: write a claim for it, then check it"), "{}", got.stdout);
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
    assert_eq!(
        ix["rust/phases/src/owed.rs::TABLE#table"]["verdict"],
        "DRIFTED"
    );
    assert_eq!(ix["rust/phases/src/owed.rs::TABLE#table"]["outside"], true);
    assert_eq!(
        ix["rust/phases/src/owed.rs::TABLE#a decision"]["verdict"],
        "UNCLAIMED"
    );
    let got = claims(&root, &["report"]);
    assert!(
        got.stdout
            .starts_with("claims: 9 in scope; IN-STEP 1, DRIFTED 1, UNCLAIMED 1; owed 7"),
        "{}",
        got.stdout
    );
    std::fs::write(
        root.join("dev/claims-deferred.json"),
        "{\"units\": [\"rust/phases/src/owed.rs::TABLE\"]}",
    )
    .unwrap();
    let got = claims(&root, &["report"]);
    assert!(got
        .stdout
        .contains("(2 DEFERRED findings not listed: make claims-report ALL=1 lists them)"),);
    let got = claims(&root, &["report", "--all"]);
    assert!(got.stdout.contains(
        "  DEFERRED       rust/phases/src/owed.rs::TABLE#table - see research/questions/0001-gap.html"
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
}

/// The refusals' second half, on a tree of its own every claim of which is recorded (feature 449 T167: the two halves read nothing of
/// each other's, and took over FR-008's tenth of a second together).
#[test]
fn a_re_check_is_refused_on_a_page_or_a_context_it_cannot_name() {
    let root = fixture("claims-cmd-refuse-recheck");
    record_all(&root);
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

/// The backfills' tree: the fixture, every claim recorded (feature 449 T167 split the test of the backfills, the
/// rekey and the refingerprint, over FR-008's tenth of a second, into three, each on a tree of its own or none).
fn backfilled(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = fixture(tag);
    record_all(&root);
    root
}

#[test]
fn the_backfills_rekey_and_refingerprint() {
    let root = backfilled("claims-cmd-backfill");
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
}

#[test]
fn a_moved_unit_is_rekeyed_and_a_star_change_refingerprinted() {
    let root = backfilled("claims-cmd-rekey");
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
    // `reach` reads `GAP`: its row put back at the fingerprint before the constants' reads (feature 449 T166)
    let reach = "rust/phases/src/lib.rs::reach#reach";
    let before = super::codes(&crate::claims::scope::all_units(&root, false).unwrap());
    let mut ix = index(&root);
    ix[reach]["code"] = json!(before[reach].0);
    std::fs::write(root.join("dev/claims-index.json"), ix.to_string()).unwrap();
    let got = claims(&root, &["refingerprint"]);
    assert_eq!(got.stdout, "claims-refingerprint: 1 claim row(s) carried to the current fingerprint (a `.py` unit's star re-exports, 417 T54; a Rust unit's constant reads, 449 T166), their code otherwise unchanged\n");
    // the migration is recorded, one row a run that carries any (feature 449 T166)
    let log = std::fs::read_to_string(root.join(crate::claims::reads::MIGRATIONS)).unwrap();
    let row: Value = serde_json::from_str(log.lines().next().unwrap()).unwrap();
    assert_eq!(row["rows"], 1);
    assert_eq!(row["keys"][0], reach);
}

#[test]
fn a_section_claim_s_old_code_is_backfilled_to_its_own_line() {
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
    let root = recorded("claims-cmd-triage");
    let page = root.join("research/questions/0001-gap.html");
    std::fs::write(&page, "<h2 id=\"gap\">The gap</h2>\n<p class=\"intro\">Why.</p>\n<p>The gap is 12 ft.</p>\n<p>A second block.</p>\n<p>A third, new.</p>\n").unwrap();
    let got = claims(&root, &["triage"]);
    assert!(got
        .stdout
        .contains("claim(s) cleared without a triage - a page each cites moved"),);
    let got = claims(&root, &["triage-owed"]);
    assert_eq!(got.stdout, "0\n");
}

/// The triage's tree: every claim recorded on `origin/main`, then two Rust claims' code and a procedure
/// section changed (feature 449 T167 split the triage's test, over FR-008's tenth of a second, into three on a tree each).
fn recorded(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = fixture(tag);
    record_all(&root);
    commit_as_origin(&root, "recorded");
    root
}

/// [`recorded`] with three Rust claims' code and a procedure section changed: a list item rewritten in words the `wall height` claim
/// repeats, and the walls' own sentence in words no claim does (feature 451 T191: the `walls` claim cleared by the tool).
fn changed(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = recorded(tag);
    let lib = std::fs::read_to_string(root.join("rust/phases/src/lib.rs")).unwrap();
    std::fs::write(
        root.join("rust/phases/src/lib.rs"),
        lib.replace("let y = 3.25;", "let y = 3.5;")
            .replace("a[1] + 42", "a[1] + 43")
            .replace("GAP: f64 = 12.0", "GAP: f64 = 12.5"),
    )
    .unwrap();
    let buildings = std::fs::read_to_string(root.join("docs/buildings.md")).unwrap();
    std::fs::write(
        root.join("docs/buildings.md"),
        buildings
            .replace("Walls stand.", "Walls stand tall.")
            .replace("  continued\n", "  continued to wall height 12 ft\n"),
    )
    .unwrap();
    root
}

/// The triage bundle of [`changed`], at `t/`.
fn triaged(root: &Path) -> String {
    let t = root.join("t");
    let to = t.to_string_lossy().into_owned();
    let got = claims(root, &["triage", "--out", &to]);
    assert!(got
        .stdout
        .contains("claims-triage: 4 claim(s); dispatch the `claims-triage` agent"));
    assert!(got
        .stdout
        .contains("claims-triage: 1 claim(s) cleared by the tool"));
    assert_eq!(
        index(root)["docs/buildings.md::Walls#walls"]["cleared"],
        crate::claims::triage::TOOL_CLEARED
    );
    let manifest = std::fs::read_to_string(t.join("MANIFEST.md")).unwrap_or_default();
    assert!(
        manifest.contains("(a procedure section; the claims' own lines did not change)")
            && manifest.contains("```diff"),
    );
    to
}

#[test]
fn a_change_of_code_or_a_section_owes_a_triage_bundled_for_its_agent() {
    let root = changed("claims-cmd-triage-owed");
    let got = claims(&root, &["owed"]);
    assert!(got.stdout.contains("code triage") && got.stdout.contains("section triage"),);
    triaged(&root);
}

#[test]
fn the_triage_s_reply_sends_on_what_it_names_and_refuses_the_rest() {
    let root = changed("claims-cmd-triaged");
    let to = triaged(&root);
    let r = reply(
        &root,
        "TOUCHES `docs/buildings.md::Walls#wall height` - it bears\n",
    );
    let got = claims(&root, &["triaged", "--bundle", &to, "--reply", &r]);
    assert!(got
        .stdout
        .contains("claims-triaged: touched: docs/buildings.md::Walls#wall height - it bears"));
    assert!(got
        .stdout
        .contains("sent on to impl-drift (1 named by the reply"),);
    let empty = reply(&root, "");
    assert_eq!(
        claims(&root, &["triaged", "--bundle", &to, "--reply", &empty]).code,
        2
    );
    assert_eq!(
        index(&root)["docs/buildings.md::Walls#wall height"]["triage"],
        "touched"
    );
}

/// A reply line the triage cannot read refuses the whole reply, the line and the form named, and the index is left as it was: never
/// a claim cleared because its TOUCHES line wore a bullet, bold or a non-ASCII dash (feature 451 T195, gap audit item 3).
#[test]
fn a_triage_reply_the_parser_cannot_read_is_refused_and_clears_nothing() {
    let root = changed("claims-cmd-triaged-closed");
    let to = triaged(&root);
    let before = std::fs::read_to_string(root.join(crate::claims::index::INDEX)).unwrap();
    let key = "docs/buildings.md::Walls#wall height";
    for (text, says) in [
        (
            format!("- TOUCHES `{key}` - it bears\n"),
            "line 1: `- TOUCHES",
        ),
        (
            format!("**TOUCHES** `{key}` - it bears\n"),
            "line 1: `**TOUCHES**",
        ),
        (
            format!("TOUCHES {key} \u{2013} it bears\n"),
            "is not in the form",
        ),
        (
            format!("TOUCHES {key} \u{2013} it bears - more\n"),
            "is not a claim of this triage",
        ),
        (
            format!("TOUCHES `{key}` - it bears\nTOUCHES nope#x - stray\n"),
            "`nope#x` is not a claim of this triage",
        ),
        (
            format!("Here is the triage.\nTOUCHES `{key}` - it bears\n"),
            "line 1: `Here is the triage.`",
        ),
        (
            format!("NONE\nTOUCHES `{key}` - it bears\n"),
            "`NONE` stands beside",
        ),
    ] {
        let r = reply(&root, &text);
        let got = claims(&root, &["triaged", "--bundle", &to, "--reply", &r]);
        assert!(
            got.code == 2
                && got.stderr.contains(says)
                && got.stderr.contains("TOUCHES <key> - <which block")
        );
        assert_eq!(
            std::fs::read_to_string(root.join(crate::claims::index::INDEX)).unwrap(),
            before
        );
    }
    let none = reply(&root, "NONE\n");
    assert_eq!(
        claims(&root, &["triaged", "--bundle", &to, "--reply", &none]).code,
        0
    );
}

/// A claim the triage cleared under a build holding other builders' uncommitted code carries that build, and a landing alone owes it
/// again, naming the files; a clean build stamps no row, and outside a landing the clear stands (feature 451 T197, gap audit item 9).
#[test]
fn a_triage_clear_by_a_mixed_build_is_owed_again_in_a_landing_alone() {
    use l7r_gate_core::build::with;
    let root = changed("claims-cmd-triaged-build");
    let to = triaged(&root);
    let key = "docs/buildings.md::Walls#wall height";
    let r = reply(&root, "NONE\n");
    let out = std::process::Command::new("git")
        .arg("-C")
        .arg(&root)
        .args(["rev-parse", "HEAD:docs/buildings.md"])
        .output()
        .unwrap();
    let blob = String::from_utf8_lossy(&out.stdout).trim().to_owned();
    // a file as landed, one deleted then and absent now, and one other builder's
    let mixed = format!("{{\"commit\": \"c1\", \"dirty\": {{\"docs/buildings.md\": \"{blob}\", \"rust/gone.rs\": \"deleted\", \"rust/gate/x.rs\": \"b7\"}}}}");
    let mixed = mixed.as_str();
    assert_eq!(
        with(Some(mixed), false, || claims(
            &root,
            &["triaged", "--bundle", &to, "--reply", &r]
        ))
        .code,
        0
    );
    assert_eq!(index(&root)[key]["build"]["dirty"]["rust/gate/x.rs"], "b7");
    assert!(!with(None, false, || claims(&root, &["owed"]))
        .stdout
        .contains(key));
    let got = with(None, true, || claims(&root, &["owed"]));
    assert!(got.stdout.contains(key) && got.stdout.contains("rust/gate/x.rs"));
    let root = changed("claims-cmd-triaged-clean");
    let to = triaged(&root);
    let r = reply(&root, "NONE\n");
    let clean = "{\"commit\": \"c1\", \"dirty\": {}}";
    assert_eq!(
        with(Some(clean), false, || claims(
            &root,
            &["triaged", "--bundle", &to, "--reply", &r]
        ))
        .code,
        0
    );
    assert!(index(&root)[key].get("build").is_none());
}

/// Feature 451 T191's replay: what `claims triage` would do, read only - each claim owed a triage and its fate, then the counts - and
/// nothing of the index written.
#[test]
fn the_triage_replay_names_each_claim_s_fate_and_writes_nothing() {
    let root = changed("claims-cmd-replay");
    let before = std::fs::read_to_string(root.join("dev/claims-index.json")).unwrap();
    let to = root.join("r").to_string_lossy().into_owned();
    let got = claims(&root, &["triage-replay", "--out", &to]);
    for want in [
        "docs/buildings.md::Walls#walls\tsection triage\tcleared by the tool\n",
        "docs/buildings.md::Walls#wall height\tsection triage\tsent\n",
        "claims-triage-replay: 5 claim(s) owed a triage: 1 cleared by the tool, 4 sent\n",
    ] {
        assert!(got.stdout.contains(want), "{want}\n----\n{}", got.stdout);
    }
    assert_eq!(
        std::fs::read_to_string(root.join("dev/claims-index.json")).unwrap(),
        before
    );
    // a page move alone (feature 432) and a section whose removed block the history no longer shows (forced)
    let root = recorded("claims-cmd-replay-forced");
    let page = root.join("research/questions/0001-gap.html");
    std::fs::write(&page, "<h2 id=\"gap\">The gap</h2>\n<p class=\"intro\">Why.</p>\n<p>The gap is 12 ft.</p>\n<p>A second block.</p>\n<p>A third, new.</p>\n").unwrap();
    let b = std::fs::read_to_string(root.join("docs/buildings.md")).unwrap();
    std::fs::write(
        root.join("docs/buildings.md"),
        b.replace("Walls stand.\n", ""),
    )
    .unwrap();
    let ix = index(&root);
    let section = ix["docs/buildings.md::Walls#walls"]["section"]
        .as_str()
        .unwrap()
        .to_owned();
    let store_path = root.join("dev/claims-pages.json");
    let mut store: Value =
        serde_json::from_str(&std::fs::read_to_string(&store_path).unwrap()).unwrap();
    store[&section].as_array_mut().unwrap().push(json!("lost"));
    std::fs::write(&store_path, store.to_string()).unwrap();
    let got = claims(&root, &["triage-replay", "--out", &to]);
    assert!(
        got.stdout.contains("\tcleared, feature 432\n")
            && got.stdout.contains("\tsection triage\tforced\n"),
        "{}",
        got.stdout
    );
}

/// Feature 451 T191: a triage the tool clears whole dispatches nothing, and owes nothing after; a small one whose bundle cannot be
/// written says nothing of a skip.
#[test]
fn a_triage_the_tool_clears_whole_dispatches_nothing() {
    let root = recorded("claims-cmd-tool-clears");
    let b = std::fs::read_to_string(root.join("docs/buildings.md")).unwrap();
    std::fs::write(
        root.join("docs/buildings.md"),
        b.replace("Walls stand.\n", "**Walls** `stand`.\n"),
    )
    .unwrap();
    let to = root.join("t").to_string_lossy().into_owned();
    let got = claims(&root, &["triage", "--out", &to]);
    assert!(
        got.stdout
            .contains("claims-triage: 2 claim(s) cleared by the tool")
            && !got.stdout.contains("dispatch"),
        "{}",
        got.stdout
    );
    assert_eq!(claims(&root, &["triage-owed"]).stdout, "0\n");
    let mut o = super::Out::default();
    let code =
        super::small_triage(&root, &["no#such".to_owned()], "/proc/no/such/dir", &mut o).unwrap();
    assert_ne!(code, 0);
    assert!(!o.out.contains("the skip is in"));
}

#[test]
fn a_small_triage_goes_straight_to_impl_drift_and_a_bare_one_to_its_full_check() {
    let root = recorded("claims-cmd-small");
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
}

/// The path helper's own cases, apart from the triage they sat in (feature 449 T167): they read no tree.
#[test]
fn a_path_reads_as_python_s_normpath_reads_it() {
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

mod landing;
