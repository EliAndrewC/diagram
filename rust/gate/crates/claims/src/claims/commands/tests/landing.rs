//! A landing alone and the answers a mixed build gave (feature 451 T223, `ask:mixed-build-241-claims`): each read at its answer
//! before, triaged again by the landing's build, and owed impl-drift only where the index's history holds no answer before.

use l7r_gate_core::build::with;
use serde_json::Value;

use super::{changed, index, recorded, reply};
use crate::claims::tests::{claims, commit_as_origin};
use crate::claims::triage::TOOL_CLEARED;

const MIXED: &str = "{\"commit\": \"c1\", \"dirty\": {\"rust/gate/x.rs\": \"b7\"}}";
const WALLS: &str = "docs/buildings.md::Walls#walls";
const HEIGHT: &str = "docs/buildings.md::Walls#wall height";

/// [`changed`] with every claim its change owes cleared by a build holding another builder's file: the tool's clear of the walls'
/// claim and a `NONE` reply for the four sent on.
fn mixed_clears(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = changed(tag);
    let to = root.join("t").to_string_lossy().into_owned();
    let r = reply(&root, "NONE\n");
    with(Some(MIXED), false, || {
        assert_eq!(claims(&root, &["triage", "--out", &to]).code, 0);
        let got = claims(&root, &["triaged", "--bundle", &to, "--reply", &r]);
        assert_eq!(got.code, 0, "{}", got.stderr);
    });
    for key in [WALLS, HEIGHT] {
        assert_eq!(index(&root)[key]["build"]["dirty"]["rust/gate/x.rs"], "b7");
    }
    root
}

fn text(root: &std::path::Path) -> String {
    std::fs::read_to_string(root.join("dev/claims-index.json")).unwrap()
}

/// The landing's build triages a mixed build's clears again from the answer before them: listed as owed a triage with the build's
/// files named, the tool's clear made again and recorded clean, the rest bundled for the agent, and what the agent names sent on.
#[test]
fn a_mixed_build_s_clears_are_triaged_again_by_the_landing_s_build() {
    let root = mixed_clears("claims-landing-retriage");
    let before = text(&root);
    assert!(with(None, false, || claims(&root, &["owed"]))
        .stdout
        .contains("claims-owed: no claim is owed"));
    let got = with(None, true, || claims(&root, &["owed"])).stdout;
    for want in [
        format!("section triage   {WALLS}\n"),
        format!("section triage   {HEIGHT}\n"),
        "claims-owed: 5 of the owed claims were last answered by an l7r-gate built with other builders' uncommitted code (rust/gate/x.rs), not this landing's".to_owned(),
        "claims-owed: 5 claim(s) owe only a TRIAGE".to_owned(),
    ] {
        assert!(got.contains(&want), "{want}\n----\n{got}");
    }
    assert!(!got.contains("owe impl-drift"), "{got}");
    // the push's gate refuses them as owed a triage, and names the landing's own triage as the route
    let got = with(None, true, || claims(&root, &["gate"]));
    assert_eq!(got.code, 1);
    assert!(got.stdout.contains(&format!(
        "claims-gate: REFUSED owed (section triage): {HEIGHT}\n"
    )));
    assert!(got.stdout.contains("claims-gate: 5 of the owed claims were last answered by an l7r-gate built with other builders' uncommitted code (rust/gate/x.rs), not this landing's: that answer is withdrawn and each is owed what this build finds since its answer before it - `L7R_LAND_ALONE=1 make claims-triage` clears again"), "{}", got.stdout);
    assert_eq!(text(&root), before);
    // the mixed answers committed: the walk passes the commit that holds them and reads the one before
    commit_as_origin(&root, "the mixed answers");
    let to = root.join("t2").to_string_lossy().into_owned();
    let got = with(None, true, || claims(&root, &["triage", "--out", &to])).stdout;
    for want in [
        "claims-triage: 5 claim(s) were last answered by an l7r-gate built with other builders' uncommitted code",
        "claims-triage: 1 claim(s) cleared by the tool",
        "claims-triage: 4 claim(s); dispatch the `claims-triage` agent",
    ] {
        assert!(got.contains(want), "{want}\n----\n{got}");
    }
    let now = index(&root);
    assert_eq!(now[WALLS]["cleared"], TOOL_CLEARED);
    assert!(now[WALLS].get("build").is_none() && now[HEIGHT].get("build").is_none());
    // the claim sent to the agent stands withdrawn: owed its triage in any run, the landing's or not
    assert!(with(None, false, || claims(&root, &["owed"]))
        .stdout
        .contains(&format!("section triage   {HEIGHT}\n")));
    let r = reply(&root, &format!("TOUCHES {HEIGHT} - the list item\n"));
    let got = with(None, true, || {
        claims(&root, &["triaged", "--bundle", &to, "--reply", &r])
    });
    assert_eq!(got.code, 0, "{}", got.stderr);
    let got = with(None, true, || claims(&root, &["owed"])).stdout;
    assert!(
        got.contains(&format!("triage touched   {HEIGHT}\n")),
        "{got}"
    );
    assert!(
        got.contains("claims-owed: 1 claim(s) in 1 file(s) owe impl-drift")
            && !got.contains("last answered")
    );
}

/// A mixed answer with the tree back where the answer before it judged it owes nothing: the landing's build finds no change to triage.
#[test]
fn a_mixed_clear_of_a_change_since_put_back_owes_nothing() {
    let root = mixed_clears("claims-landing-put-back");
    crate::record::testkit::git(
        &root,
        &[
            "checkout",
            "-q",
            "HEAD",
            "--",
            "docs/buildings.md",
            "rust/phases/src/lib.rs",
        ],
    );
    let got = with(None, true, || claims(&root, &["owed"])).stdout;
    assert!(got.contains("claims-owed: no claim is owed"), "{got}");
    // the landing's first pass writes the withdrawal: no row keeps the mixed stamp, and nothing is owed in any run
    assert!(index(&root)[WALLS].get("build").is_some());
    let got = with(None, true, || claims(&root, &["rekey"])).stdout;
    assert!(got.contains("claims-rekey: 5 claim row(s) a mixed build last answered written at their answer before it"), "{got}");
    let rows = index(&root);
    assert!(rows
        .as_object()
        .unwrap()
        .values()
        .all(|r| r.get("build").is_none()));
    assert!(with(None, false, || claims(&root, &["owed"]))
        .stdout
        .contains("claims-owed: no claim is owed"));
    assert!(!with(None, true, || claims(&root, &["rekey"]))
        .stdout
        .contains("a mixed build"));
}

/// A mixed answer the index's history holds no answer before - the newest commit of the index has no row of the claim - is owed
/// impl-drift, the build's files named, and stays as recorded.
#[test]
fn a_mixed_clear_with_no_answer_before_it_owes_impl_drift() {
    let root = mixed_clears("claims-landing-no-base");
    let full = text(&root);
    let mut rows: Value = serde_json::from_str(&full).unwrap();
    rows.as_object_mut().unwrap().shift_remove(HEIGHT);
    std::fs::write(root.join("dev/claims-index.json"), rows.to_string()).unwrap();
    commit_as_origin(&root, "no row of the wall height");
    std::fs::write(root.join("dev/claims-index.json"), &full).unwrap();
    let got = with(None, true, || claims(&root, &["owed"])).stdout;
    assert!(
        got.contains("the index's history holds no earlier answer of it by a clean build to triage again from: re-judge it here (451 T197, T223) docs/buildings.md::Walls#wall height\n"),
        "{got}"
    );
    assert!(
        got.contains("rust/gate/x.rs")
            && got.contains("claims-owed: 1 claim(s) in 1 file(s) owe impl-drift")
    );
    assert!(
        got.contains("claims-owed: 4 of the owed claims were last answered"),
        "{got}"
    );
}

/// The page-move clear (feature 432) stamps its build as every clear does: a build holding uncommitted code is recorded on the row, and
/// a clean build's clear drops the stamp an earlier answer left.
#[test]
fn a_page_move_clear_stamps_or_drops_its_build() {
    let root = recorded("claims-landing-page-move");
    let page = root.join("research/questions/0001-gap.html");
    let body = "<h2 id=\"gap\">The gap</h2>\n<p class=\"intro\">Why.</p>\n<p>The gap is 12 ft.</p>\n<p>A second block.</p>\n";
    let stamped = |more: &str, build: Option<&str>| {
        std::fs::write(&page, format!("{body}{more}")).unwrap();
        let got = with(build, false, || claims(&root, &["triage"])).stdout;
        assert!(got.contains("claim(s) cleared without a triage"), "{got}");
        let rows = index(&root);
        let rows = rows.as_object().unwrap();
        let cleared = |r: &&Value| r["cleared"] == crate::claims::triage::CLEARED;
        assert!(rows.values().any(|r| cleared(&r)));
        rows.values()
            .filter(cleared)
            .filter(|r| r.get("build").is_some())
            .count()
    };
    assert!(stamped("<p>A third, new.</p>\n", Some(MIXED)) > 0);
    assert_eq!(stamped("<p>A third, new.</p>\n<p>A fourth.</p>\n", None), 0);
}
