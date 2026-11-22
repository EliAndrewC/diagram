//! The push's ratchet on fixture trees: a fake `l7r-gate.sh` answers each counting run from the figures a test gives it.

use std::fmt::Write as _;
use std::path::Path;
use std::process::Command;

use serde_json::{json, Value};

use super::cli;

/// The driver's lines for one stage at each (size, ops), on each of `seeds`.
fn rolled(stage: &str, at: &[(i64, i64)], seeds: &[i64]) -> String {
    at.iter().fold(String::new(), |mut out, (h, ops)| {
        for seed in seeds {
            let _ = write!(
                out,
                "{seed}\t{h}\t{stage}\t{ops}\n{seed}\t{h}\t{stage}\tcells@x\t{ops}\n"
            );
        }
        out
    })
}

/// The driver's lines for one stage at each (size, ops), on all four of its seeds.
fn lines(stage: &str, at: &[(i64, i64)]) -> String {
    rolled(stage, at, &[4, 25, 39, 47])
}

/// A git tree with the table, the pool sheets and a fake wrapper answering `--budget`, `--budget polder` and the sheet counts.
fn world(
    tag: &str,
    table: &Value,
    comb: &str,
    polder: &str,
    totals: &str,
) -> l7r_shared::tempdir::TempDir {
    let root = l7r_gate_core::checks::scratch(tag);
    std::fs::create_dir_all(root.join("scripts/gates")).unwrap();
    std::fs::create_dir_all(root.join("dev")).unwrap();
    std::fs::create_dir_all(root.join("rust/phases/src")).unwrap();
    std::fs::create_dir_all(root.join("pool/magistracies/hand")).unwrap();
    std::fs::create_dir_all(root.join("pool/magistracies/made")).unwrap();
    std::fs::write(root.join("rust/phases/src/a.rs"), "fn a() {}\n").unwrap();
    std::fs::write(root.join("pool/magistracies/hand/hand.svg"), "<svg/>\n").unwrap();
    std::fs::write(
        root.join("pool/magistracies/made/made.compound.json"),
        "{}\n",
    )
    .unwrap();
    std::fs::write(root.join("pool/magistracies/made/made.svg"), "<svg/>\n").unwrap();
    std::fs::write(root.join("dev/work-budget.json"), table.to_string()).unwrap();
    let quote = |t: &str| t.replace('\t', "\\t").replace('\n', "\\n");
    let script = format!(
        "#!/bin/sh\n[ \"$1 $2 $3\" = \"rust hamlet --crate\" ] && [ \"$HAMLET_FEATURES\" = counters ] || exit 9\necho \"$HAMLET_ARGS\" >> \"$0.calls\"\ncase \"$HAMLET_ARGS\" in\n  '--budget') printf '{}' ;;\n  '--budget polder') printf '{}' ;;\n  *-counts*) [ \"$HAMLET_BIN $HAMLET_DEV\" = 'l7r-mode-a 1' ] || exit 8; {totals} ;;\n  'counts pool') [ \"$HAMLET_BIN $HAMLET_DEV ${{4##*/rust/}}\" = 'l7r-pool 1 gate/crates/pool' ] || exit 6; echo '{{\"total\": 30}}' ;;\n  'counts legacy-hand-authored-pool') echo '{{\"total\": 12}}' ;;\n  *) exit 7 ;;\nesac\n",
        quote(comb),
        quote(polder)
    );
    crate::write_executable(&root.join("scripts/gates/l7r-gate.sh"), &script);
    for args in [
        &["init", "-q"][..],
        &["config", "user.email", "t@t"],
        &["config", "user.name", "t"],
    ] {
        assert!(Command::new("git")
            .arg("-C")
            .arg(&*root)
            .args(args)
            .status()
            .unwrap()
            .success());
    }
    std::fs::write(root.join(".gitignore"), "*.calls\n").unwrap();
    root
}

/// The sheet totals: the placer's on each sheet, the compound generator's.
fn totals(placer_hand: i64, placer_made: i64, compound: i64) -> String {
    format!(
        "case \"$HAMLET_ARGS\" in 'caption-counts pool/magistracies/hand/hand.svg') echo '{{\"total\": {placer_hand}}}'; echo 'rust-checks: hamlet clean on 1 crate(s)' ;; 'caption-counts pool/magistracies/made/made.compound.json') echo '{{\"total\": {placer_made}}}' ;; 'compound-counts pool/magistracies/made/made.compound.json') echo '{{\"total\": {compound}}}' ;; *) echo '{{\"total\": 1}}' ;; esac"
    )
}

fn table() -> Value {
    json!({
        "stages": {
            "field": {"status": "accepted", "per_thing": 1.0, "items_at_40": 100, "items_at_80": 150, "accepted": {"40": 120.0, "80": 160.0}},
            "waterward": {"status": "accepted", "per_thing": 1.0, "items_at_40": 1, "items_at_80": 1, "accepted": {"40": 0.0, "80": 0.0}},
            "waterward.polder": {"status": "accepted", "per_thing": 1.0, "items_at_10": 50, "items_at_20": 60, "sizes": [10, 20], "accepted": {"10": 70.0, "20": 80.0}},
            "seat": {"status": "budgeted", "per_thing": 1.0, "items_at_40": 1, "items_at_80": 1}
        },
        "sheet_stages": {
            "placer": {"status": "budgeted", "sheets": {"hand": {"budget": 100.0}, "made": {"budget": 50.0}}},
            "compound": {"status": "budgeted", "sheets": {"made": {"budget": 40.0}}},
            "pipeline": {"status": "budgeted", "sheets": {"pool": {"budget": 20.0}, "legacy-hand-authored-pool": {"budget": 12.0}}}
        }
    })
}

fn comb(field40: i64) -> String {
    lines("field", &[(40, field40), (80, 150)]) + &lines("seat", &[(40, 9_999_999)])
}

fn polder() -> String {
    lines("waterward.polder", &[(10, 60), (20, 75)])
}

fn calls(root: &Path) -> String {
    std::fs::read_to_string(root.join("scripts/gates/l7r-gate.sh.calls")).unwrap_or_default()
}

fn route(root: &Path, r: &str) -> crate::Reply {
    cli(&[r.to_owned()], root)
}

/// THE DEFECT T224 FIXED: the review printed "suspended" and passed a push with an accepted stage over its figure. Red first on that
/// recipe, observed 2026-11-19: `make work-budget-review ROUTE=GATED` on a tree whose one accepted stage, field, stood at 10 against a
/// count of tens of thousands printed "suspended" and exited 0.
#[test]
fn an_accepted_stage_over_its_figure_is_refused_with_the_fix() {
    let root = world(
        "wbr-over",
        &table(),
        &comb(130),
        &polder(),
        &totals(90, 40, 30),
    );
    let got = route(&root, "GATED");
    assert_eq!(got.code, 1, "{}", got.stdout);
    assert!(got.stderr.contains("REFUSED"));
    assert!(got
        .stderr
        .contains("field: 130 counted operations at 40 households, over its accepted 120"));
    // 130 is within twice its budget of 100: the accepted figure alone refuses it
    assert!(!got.stderr.contains("past twice its budget"));
    assert!(
        got.stderr.contains("make budget-change PHASE=<stage>")
            && got.stderr.contains("no round-arbiter accept")
    );
}

#[test]
fn every_held_stage_within_passes_printing_its_counts_and_what_it_could_not_count() {
    let root = world(
        "wbr-within",
        &table(),
        &comb(110),
        &polder(),
        &totals(90, 40, 30),
    );
    let got = route(&root, "GATED-LOCAL");
    assert_eq!(got.code, 0, "{}", got.stderr);
    let out = &got.stdout;
    assert!(out.contains("every held stage within its figures (the hamlet stages re-counted, the pool-sheet stages re-counted)"));
    assert!(out.contains("  field: 110 at 40 (1.10x its budget 100; accepted 120); 150 at 80 (1.00x its budget 150; accepted 160)"));
    assert!(out.contains("  waterward.polder: 60 at 10 (1.20x its budget 50; accepted 70); 75 at 20 (1.25x its budget 60; accepted 80)"));
    assert!(out.contains("  waterward: not counted - the driver runs it on a polder alone"));
    assert!(out.contains("  placer: hand 90 (0.90x its budget 100); made 40 (0.80x its budget 50)"));
    assert!(out.contains("  compound: made 30 (0.75x its budget 40)"));
    // T220, red first: the pipeline was printed `UNCOUNTED pipeline: budgeted per sheet (2), but nothing counts it` until the pool walk
    // was built; each tree is counted by `l7r-pool counts <tree>`, the whole stage since T221 (no "counted:" part named)
    assert!(out.contains("  pipeline: pool 30 (1.50x its budget 20); legacy-hand-authored-pool 12 (1.00x its budget 12)\n"));
    assert!(!out.contains("UNCOUNTED"));
    assert!(!out.contains("seat"), "a stage only budgeted is not held");
    // the counts are kept: the same code is not counted again, and a move of what a run reads re-counts that run alone
    let before = calls(&root);
    assert_eq!(before.lines().count(), 7, "{before}");
    let again = route(&root, "GATED");
    assert!(again.stdout.contains("(the hamlet stages kept (their code unmoved), the pool-sheet stages kept (their code and sheets unmoved))"));
    assert_eq!(calls(&root), before);
    std::fs::write(root.join("rust/phases/src/a.rs"), "fn a() { let _ = 1; }\n").unwrap();
    let moved = route(&root, "GATED");
    assert!(moved
        .stdout
        .contains("the hamlet stages re-counted, the pool-sheet stages kept"));
    assert_eq!(calls(&root).lines().count(), 9);
    // a sheet added to the table is counted, not read from the counts kept before it
    let mut t = table();
    t["sheet_stages"]["compound"]["sheets"]["hand"] = json!({"budget": 1000.0});
    std::fs::write(root.join("dev/work-budget.json"), t.to_string()).unwrap();
    std::fs::write(root.join("scripts/gates/l7r-gate.sh.calls"), "").unwrap();
    let added = route(&root, "GATED");
    assert!(added
        .stdout
        .contains("the hamlet stages kept (their code unmoved), the pool-sheet stages re-counted"));
    assert!(calls(&root).contains("compound-counts pool/magistracies/hand/hand.svg"));
}

#[test]
fn a_sheet_past_twice_its_budget_is_refused() {
    let root = world(
        "wbr-sheet",
        &table(),
        &comb(110),
        &polder(),
        &totals(201, 40, 81),
    );
    let got = route(&root, "GATED");
    assert_eq!(got.code, 1);
    assert!(got
        .stderr
        .contains("placer on hand: 201 counted operations, past twice its budget (200)"));
    assert!(got
        .stderr
        .contains("compound on made: 81 counted operations, past twice its budget (80)"));
}

#[test]
fn past_twice_the_budget_refuses_where_no_accepted_figure_is_kept() {
    let mut t = table();
    t["stages"]["field"]["accepted"] = json!({});
    let root = world("wbr-twice", &t, &comb(201), &polder(), &totals(1, 1, 1));
    let got = route(&root, "GATED");
    assert!(got
        .stderr
        .contains("field: 201 counted operations at 40 households, past twice its budget (200)"));
    t["stages"]["field"] = json!({"status": "accepted"});
    // a counted pool-sheet stage the table does not budget is not asked for
    t["sheet_stages"]
        .as_object_mut()
        .unwrap()
        .remove("compound");
    let root = world("wbr-none", &t, &comb(1), &polder(), &totals(1, 1, 1));
    assert!(route(&root, "GATED")
        .stderr
        .contains("field: accepted with no accepted figure and no budget at 40 households"));
}

#[test]
fn what_cannot_be_held_refuses_rather_than_passes() {
    let mut t = table();
    t["stages"]["hem"] = json!({"status": "accepted", "accepted": {"40": 1.0, "80": 1.0}});
    t["sheet_stages"]["placer"]["sheets"]["gone"] = json!({"budget": 1.0});
    let root = world(
        "wbr-missing",
        &t,
        &lines("field", &[(40, 1)]),
        &polder(),
        &totals(1, 1, 1),
    );
    let got = route(&root, "GATED");
    assert_eq!(got.code, 1);
    assert!(got
        .stderr
        .contains("hem: accepted, but no counting run counts it"));
    assert!(got
        .stderr
        .contains("field: the counting run rolled no field at 80 households"));
    assert!(got
        .stderr
        .contains("placer on gone: no count - the pool holds no gone.compound.json or gone.svg"));
}

#[test]
fn nothing_is_held_on_a_direct_push_or_with_nothing_accepted() {
    let root = world("wbr-direct", &table(), "", "", "exit 5");
    let got = route(&root, "DIRECT");
    assert_eq!((got.code, got.stdout.as_str()), (0, "work-budget-review: the push carries no engine code (route DIRECT) - nothing to hold\n"));
    assert_eq!(calls(&root), "");
    // a bare run, no ROUTE, holds as a GATED push does
    assert!(route(&root, "").stderr.contains("on rust/mode_a failed"));
    let root = world(
        "wbr-empty",
        &json!({"stages": {"seat": {"status": "budgeted"}}}),
        "",
        "",
        "exit 5",
    );
    assert!(route(&root, "GATED").stdout.contains("nothing to hold"));
}

#[test]
fn a_failed_run_or_an_unreadable_table_is_an_error() {
    let root = world("wbr-fail", &table(), &comb(1), &polder(), "exit 5");
    let got = route(&root, "GATED");
    assert_eq!(got.code, 1);
    assert!(got.stderr.contains(
        "the counting run `caption-counts pool/magistracies/hand/hand.svg` on rust/mode_a failed"
    ));
    let root = world("wbr-total", &table(), &comb(1), &polder(), "echo '{}'");
    assert!(route(&root, "GATED").stderr.contains("printed no total"));
    let root = world("wbr-parse", &table(), "4\t40\tfield\tmany\n", "", "exit 5");
    assert!(route(&root, "GATED")
        .stderr
        .contains("a driver line does not parse"));
    std::fs::write(root.join("dev/work-budget.json"), "not json").unwrap();
    assert!(route(&root, "GATED").stderr.contains("does not read"));
    std::fs::remove_file(root.join("scripts/gates/l7r-gate.sh")).unwrap();
    std::fs::write(root.join("dev/work-budget.json"), table().to_string()).unwrap();
    assert!(route(&root, "GATED").stderr.contains("did not start"));
    let bare = l7r_gate_core::checks::scratch("wbr-bare");
    std::fs::create_dir_all(bare.join("dev")).unwrap();
    std::fs::write(bare.join("dev/work-budget.json"), table().to_string()).unwrap();
    assert_eq!(route(&bare, "GATED").code, 1);
}

/// The hamlet stages alone, or the pool-sheet stages alone: the other group is not counted.
#[test]
fn a_table_with_one_group_counts_that_group_alone() {
    let mut t = table();
    t.as_object_mut().unwrap().remove("sheet_stages");
    let root = world("wbr-hamlets", &t, &comb(110), &polder(), "exit 5");
    let got = route(&root, "GATED");
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(got.stdout.contains("(the hamlet stages re-counted):"));
    let mut t = table();
    t.as_object_mut().unwrap().remove("stages");
    let root = world("wbr-sheets", &t, "", "", &totals(1, 1, 1));
    let got = route(&root, "GATED");
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(got.stdout.contains("(the pool-sheet stages re-counted):"));
}

/// A size where fewer seeds rolled than the driver tries says so: a refused roll prints nothing, so its mean reads cheaper.
#[test]
fn a_size_where_a_seed_did_not_roll_says_how_many_rolled() {
    let comb = rolled("field", &[(40, 110)], &[4, 25]) + &lines("field", &[(80, 150)]);
    let root = world("wbr-seeds", &table(), &comb, &polder(), &totals(1, 1, 1));
    let got = route(&root, "GATED");
    assert!(got
        .stdout
        .contains("110 at 40 (1.10x its budget 100; accepted 120; 2 of 4 seeds rolled)"));
}

#[test]
fn a_ratio_to_no_budget_is_a_dash() {
    assert_eq!(super::ratio(5, 0.0), "-");
    assert_eq!(super::ratio(5, 4.0), "1.25x");
}

/// The pipeline (feature 449 T220): held to twice its budget on each tree; a sheet the table names that is no pool tree is refused with
/// the trees named; and its count, which moves with the folders' entries, is counted again when a render appears, though no tracked
/// file moved.
#[test]
fn the_pipeline_is_held_per_tree_and_recounted_when_a_folder_gains_a_render() {
    let mut t = table();
    t["sheet_stages"]["pipeline"]["sheets"] =
        json!({"pool": {"budget": 10.0}, "pool-typo": {"budget": 5.0}});
    // a stage budgeted per sheet that no counter reaches is printed UNCOUNTED, never passed in silence
    t["sheet_stages"]["render"] =
        json!({"status": "budgeted", "sheets": {"pool": {"budget": 1.0}}});
    let root = world("wbr-pipeline", &t, &comb(110), &polder(), &totals(1, 1, 1));
    let got = route(&root, "GATED");
    assert_eq!(got.code, 1);
    assert!(got
        .stderr
        .contains("pipeline on pool: 30 counted operations, past twice its budget (20)"));
    assert!(got.stderr.contains("pipeline on pool-typo: no count - no pool tree is named pool-typo (the trees are pool and legacy-hand-authored-pool;"));
    assert!(got
        .stderr
        .contains("  UNCOUNTED render: budgeted per sheet (1), but nothing counts it"));
    let counted = |root: &Path| calls(root).lines().filter(|l| *l == "counts pool").count();
    assert_eq!(counted(&root), 1);
    let _ = route(&root, "GATED");
    // kept while nothing moved
    assert_eq!(counted(&root), 1);
    std::fs::write(root.join("pool/magistracies/hand/hand.png"), "png").unwrap();
    let _ = route(&root, "GATED");
    // a render the tree's key does not see re-counts it
    assert_eq!(counted(&root), 2);
}

#[test]
fn an_accepted_sheet_over_its_accepted_figure_is_refused() {
    // 449 T243: a pool-sheet stage accepted (`make budget-accept COUNTS=`) is held on each sheet to its accepted figure, as a
    // hamlet stage is at its sizes
    let mut t = table();
    t["sheet_stages"]["placer"]["status"] = json!("accepted");
    t["sheet_stages"]["placer"]["accepted"] = json!({"hand": 90.0, "made": 50.0});
    let root = world(
        "wbr-sheet-accepted",
        &t,
        &comb(110),
        &polder(),
        &totals(91, 40, 40),
    );
    let got = route(&root, "GATED");
    let held = got
        .stderr
        .contains("placer on hand: 91 counted operations, over its accepted 90");
    assert_eq!(got.code, 1);
    assert!(held, "{got:?}");
    let within = world(
        "wbr-sheet-accepted-within",
        &t,
        &comb(110),
        &polder(),
        &totals(90, 40, 40),
    );
    assert_eq!(route(&within, "GATED").code, 0);
}
