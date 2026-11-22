//! The driver's lines to the record, through a stand-in for the driver.

use serde_json::{json, Value};

use super::{budget_at, cli, exponent, forms, over, parse, run_file, table};

const LINES: &str = "4\t10\tfield\t100\n4\t10\tfield\tcells\t7\n25\t10\tfield\t200\n4\t40\tfield\t4000\n4\t20\tfield\t1000\n4\t80\tfield\t16000\n4\t40\tsink\t50\nnot a budget line\n";

/// The polder form's lines: a stage at its own sizes, and one counted at a size its entry does not name.
const FORM: &str = "4\t10\tward.polder\t100\n4\t20\tward.polder\t300\n4\t10\tfield.polder\t50\n";

fn budgets() -> Value {
    json!({"field": {"per_thing": 10, "items_at_40": 100, "status": "accepted", "accepted": {"40": 3900}}, "sink": {"per_thing": null, "items_at_40": 5}, "ward.polder": {"per_thing": 1, "items_at_10": 50, "items_at_20": 100, "sizes": [10, 20], "status": "accepted", "accepted": {"10": 120, "20": 320}}})
}

#[test]
fn a_form_stands_in_its_own_table_at_its_own_sizes_out_of_the_whole_roll() {
    // feature 449 T226: the polder's stages were counted by no `make work-budget`, so its audit bundle carried no counts
    let (counts, _) = parse(&(LINES.to_owned() + FORM)).unwrap();
    let t = table(&counts, &budgets());
    assert_eq!(t.len(), 5);
    assert_eq!(t[4], "| **the whole roll** | 150 | 1,000 | 4,050 | 16,000 | 2.00 | 1,000 | - | 4.0x | through the cut |");
    let f = forms(&counts, &budgets());
    assert_eq!(
        f[0],
        "| stage | ops at each size (budget, accepted) | exponent | ratio | status |"
    );
    assert_eq!(f[1], "|---|---|---|---|---|");
    assert_eq!(
        f[2],
        "| ward.polder | 100 @10 (50 budget, 120 accepted); 300 @20 (100 budget, 320 accepted) | 1.58 | 3.0x | accepted |"
    );
    assert_eq!(
        f[3],
        "| field.polder | 50 @10 (- budget, - accepted); 0 @20 (- budget, - accepted) | - | - | unbudgeted |"
    );
    assert!(forms(&parse(LINES).unwrap().0, &budgets()).is_empty());
}

#[test]
fn the_means_and_the_counters_come_off_the_lines() {
    let (counts, rolls) = parse(LINES).unwrap();
    assert_eq!(counts[0].0, "field");
    assert_eq!(counts[1].0, "sink");
    assert_eq!(counts[0].1[&10], (150, 2));
    assert_eq!(
        rolls[&(4, 10)]["field"],
        json!({"total": 100, "ops": {"cells": 7}})
    );
}

#[test]
fn a_line_that_does_not_parse_is_refused() {
    assert!(parse("x\t10\tfield\t1\n")
        .unwrap_err()
        .contains("does not parse"));
    assert!(parse("4\t10\tfield\tcells\tmany\n")
        .unwrap_err()
        .contains("does not parse"));
    assert!(parse("4\t10\tfield\tcells\t7\n")
        .unwrap_err()
        .contains("before its stage"));
}

#[test]
fn a_budget_needs_both_its_factors() {
    assert_eq!(
        budget_at(&json!({"per_thing": 2, "items_at_40": 3}), 40),
        Some(6.0)
    );
    assert_eq!(
        budget_at(&json!({"per_thing": null, "items_at_40": 3}), 40),
        None
    );
    assert_eq!(budget_at(&json!({"per_thing": 2}), 40), None);
}

#[test]
fn the_exponent_is_the_growth_from_20_to_80() {
    assert_eq!(exponent(&[0, 100, 0, 1600]), "2.00");
    assert_eq!(exponent(&[0, 0, 0, 1600]), "-");
    assert_eq!(exponent(&[0, 100, 0, 0]), "-");
}

#[test]
fn the_table_keeps_its_ratio_and_status_last() {
    let (counts, _) = parse(LINES).unwrap();
    let t = table(&counts, &budgets());
    assert_eq!(t[1], "|---|---|---|---|---|---|---|---|---|---|");
    assert_eq!(
        t[2],
        "| field | 150 | 1,000 | 4,000 | 16,000 | 2.00 | 1,000 | 3,900 | 4.0x | accepted |"
    );
    assert_eq!(
        t[3],
        "| sink | 0 | 0 | 50 | 0 | - | - | - | - | unbudgeted |"
    );
    assert_eq!(t[4], "| **the whole roll** | 150 | 1,000 | 4,050 | 16,000 | 2.00 | 1,000 | - | 4.0x | through the cut |");
    assert_eq!(over(&t), ["field"]);
}

#[test]
fn a_roll_with_no_budget_shows_none() {
    let (counts, _) = parse("4\t40\tsink\t50\n").unwrap();
    let t = table(&counts, &json!({}));
    assert_eq!(
        t[3],
        "| **the whole roll** | 0 | 0 | 50 | 0 | - | 0 | - | - | through the cut |"
    );
    assert!(over(&t).is_empty());
}

#[test]
fn the_run_file_sorts_its_keys() {
    let (counts, rolls) = parse(LINES).unwrap();
    let got = run_file(&counts, &rolls, "T", "abc", "k");
    assert_eq!(
        got.as_object().unwrap().keys().collect::<Vec<_>>(),
        ["meta", "rows", "summary"]
    );
    assert_eq!(got["meta"]["driver"], "rust");
    assert_eq!(got["rows"][0]["households"], 10);
    assert_eq!(
        got["summary"]["stages"]["field"]["per"]["10"],
        json!({"ops": 150, "rolled": 2})
    );
    assert_eq!(got["rows"][0]["stages"]["field"]["ops"]["cells"], 7);
}

fn world(tag: &str, body: &str) -> l7r_shared::tempdir::TempDir {
    let root = crate::checks::scratch(tag);
    std::fs::create_dir_all(root.join("scripts/gates")).unwrap();
    std::fs::create_dir_all(root.join("dev/work-budget")).unwrap();
    crate::write_executable(&root.join("scripts/gates/l7r-gate.sh"), body);
    std::fs::write(
        root.join("dev/work-budget.json"),
        json!({"stages": budgets()}).to_string(),
    )
    .unwrap();
    root
}

fn git_init(root: &std::path::Path) {
    let done = std::process::Command::new("git")
        .args(["init", "-q"])
        .current_dir(root)
        .output()
        .unwrap();
    assert!(done.status.success());
}

fn driver() -> String {
    let esc = |s: &str| s.replace('\t', "\\t").replace('\n', "\\n");
    format!("#!/bin/sh\n[ \"$HAMLET_FEATURES\" = counters ] && [ \"$1\" = rust ] || exit 9\n[ \"$HAMLET_ARGS\" = --budget ] && printf '{}' && exit 0\n[ \"$HAMLET_ARGS\" = '--budget polder' ] && printf '{}' && exit 0\nexit 8\n", esc(LINES), esc(FORM))
}

#[test]
fn a_run_prints_the_table_and_writes_nothing_unasked() {
    let root = world("wb-print", &driver());
    let got = cli(&[], &root);
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(got.stdout.contains("| field | 150 |"));
    assert!(got.stdout.contains("| ward.polder | 100 @10 "));
    assert!(got.stdout.contains(
        "past twice the budget at 40, a form's at its largest size (the audit's leeway, 444 FR-022): field, ward.polder"
    ));
    assert!(!root.join("dev/work-budget.md").exists());
}

#[test]
fn write_replaces_the_record_and_files_the_run() {
    let root = world("wb-write", &driver());
    // the run is keyed on the tree's code, which git lists: outside a repository the write fails before it counts (feature 449 T259)
    assert!(cli(&["--write".to_owned()], &root).stderr.contains("git"));
    git_init(&root);
    std::fs::create_dir_all(root.join("rust/phases/src")).unwrap();
    std::fs::write(root.join("rust/phases/src/a.rs"), "fn a() {}\n").unwrap();
    let got = cli(&["--write".to_owned()], &root);
    assert_eq!(got.code, 0, "{}", got.stderr);
    let page = std::fs::read_to_string(root.join("dev/work-budget.md")).unwrap();
    assert!(page.starts_with("# The work budget - the standing record (feature 443)\n"));
    assert!(
        page.contains("| field | 150 |") && page.contains("through the cut |\n\nThe polder form")
    );
    assert!(page.ends_with("| unbudgeted |\n"));
    // no form counted, no form table
    let bare = world(
        "wb-bare",
        &format!(
            "#!/bin/sh\n[ \"$HAMLET_ARGS\" = --budget ] || exit 0\nprintf '{}'\n",
            LINES.replace('\t', "\\t").replace('\n', "\\n")
        ),
    );
    git_init(&bare);
    assert_eq!(cli(&["--write".to_owned()], &bare).code, 0);
    let page = std::fs::read_to_string(bare.join("dev/work-budget.md")).unwrap();
    assert!(page.ends_with("through the cut |\n") && !page.contains("polder"));
    let filed: Vec<_> = std::fs::read_dir(root.join("dev/work-budget"))
        .unwrap()
        .flatten()
        .collect();
    assert_eq!(filed.len(), 1);
    assert!(filed[0].file_name().to_string_lossy().contains("-rust-"));
    // the run carries the key of the code it counted, the ratchet's key of the same reads
    let run: Value =
        serde_json::from_str(&std::fs::read_to_string(filed[0].path()).unwrap()).unwrap();
    assert_eq!(
        run["meta"]["code"],
        super::code_key(&root).unwrap().as_str()
    );
    assert_ne!(
        super::code_key(&root).unwrap(),
        super::code_key(&bare).unwrap()
    );
    assert!(got.stdout.contains("written"));
    std::fs::remove_dir_all(root.join("dev/work-budget")).unwrap();
    assert_eq!(cli(&["--write".to_owned()], &root).code, 1);
    std::fs::remove_dir_all(root.join("dev")).unwrap();
    std::fs::create_dir(root.join("dev")).unwrap();
    assert!(cli(&[], &root).stderr.contains("does not read"));
}

#[test]
fn a_failed_driver_is_reported() {
    let root = world("wb-fail", "#!/bin/sh\necho out; echo err >&2; exit 3\n");
    let got = cli(&[], &root);
    assert_eq!(got.code, 1);
    assert_eq!(
        got.stderr,
        "work-budget: the driver's budget run `--budget` failed:\nout\nerr\n\n"
    );
    std::fs::remove_file(root.join("scripts/gates/l7r-gate.sh")).unwrap();
    assert!(cli(&[], &root)
        .stderr
        .starts_with("work-budget: the driver's budget run failed:"));
    let bad = world("wb-bad", "#!/bin/sh\nprintf 'x\\t1\\tf\\t1\\n'\n");
    assert!(cli(&[], &bad).stderr.contains("does not parse"));
}
