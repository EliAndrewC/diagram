//! A Mode A stage's first budget, per pool sheet, and its counts compared per sheet (feature 449 T201).

use l7r_gate_core::checks::scratch;

use super::super::tests::{put, run, table, tree};

/// A pool-sheet derivation, as the bundle passes it (its form is `work_budget_bundle`'s tests').
const POOL: &str = "# d

## Contract
- Sizes: pool sheets: alpha-sheet, beta-sheet

## The count, factor by factor
| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | N = 10, 20 | the captions | 10 to 20 |

## Totals
- at alpha-sheet: 10 x 24 = 240
- at beta-sheet: 20 x 24 = 480
- all sheets: 240 + 480 = 720
";

const D: &str = "specs/y/derivations/placer.md";
const V: &str = "specs/y/derivations/placer.verdict-1.txt";

fn pool_tree(name: &str) -> l7r_gate_core::checks::TempDir {
    let d = scratch(name);
    tree(&d);
    put(&d, D, POOL.as_bytes());
    put(&d, V, b"SOUND - fine\n");
    d
}

fn set(d: &std::path::Path, extra: &[&str]) -> crate::Reply {
    let mut args = vec!["set", "placer", "", "", D, V];
    args.extend(extra);
    run(d, &args)
}

#[test]
fn a_pool_sheet_stage_is_budgeted_per_sheet_from_its_totals() {
    let d = pool_tree("bc-sheets-set");
    let got = set(&d, &[]);
    assert_eq!(
        (got.code, got.stdout.as_str()),
        (0, "budget-set: `placer` budgeted per sheet: alpha-sheet 240; beta-sheet 480; all sheets 720\n"),
    );
    let t = table(&d);
    assert_eq!(
        t["sheet_stages"]["placer"]["sheets"]["beta-sheet"]["budget"],
        480.0
    );
    assert_eq!(
        t["sheet_stages"]["placer"]["sheets"]["alpha-sheet"]["items"],
        10.0
    );
    assert_eq!(t["sheet_stages"]["placer"]["all_sheets"], 720.0);
    assert_eq!(t["sheet_stages"]["placer"]["verdict"], V);
    // the roll's stages untouched
    assert!(t["stages"].get("placer").is_none());
    // a second pin is a change, not built for a pool-sheet stage
    assert!(set(&d, &[])
        .stderr
        .contains("`placer` is budgeted per sheet already"));
}

#[test]
fn a_pool_sheet_pin_takes_no_hamlet_argument_and_no_hamlet_stage() {
    let d = pool_tree("bc-sheets-refused");
    for (extra, named) in [
        (vec!["--items-at-40", "5"], "--items-at-40"),
        (vec!["--reason", "x"], "--reason"),
        (vec!["--lower"], "--lower"),
    ] {
        let got = set(&d, &extra);
        assert_eq!(got.code, 1);
        assert!(got
            .stderr
            .contains(&format!("so `{named}` - a hamlet stage's - is not taken")));
    }
    let per = run(&d, &["set", "placer", "3", "", D, V]);
    assert!(per.stderr.contains("so `PER_THING`"), "{per:?}");
    let exp = run(&d, &["set", "placer", "", "1.0", D, V]);
    assert!(exp.stderr.contains("so `EXPONENT`"), "{exp:?}");
    let hamlet = run(&d, &["set", "seat", "", "", D, V]);
    assert_eq!(hamlet.stderr, "budget-set: `seat` is a hamlet stage of dev/work-budget.json, sized by households - its derivation cannot size pool sheets\n");
    // a form of a roll's stage is the roll's
    assert!(run(&d, &["set", "seat.wide", "", "", D, V])
        .stderr
        .contains("`seat.wide` is a hamlet stage"));
    put(&d, V, b"LOOSE\n");
    assert!(set(&d, &[]).stderr.contains("reads LOOSE, not SOUND"));
    put(&d, V, b"");
    assert!(set(&d, &[]).stderr.contains("reads nothing, not SOUND"));
    put(&d, V, b"SOUND\n");
    put(&d, D, POOL.replace("- all sheets", "- sum").as_bytes());
    assert!(set(&d, &[]).stderr.contains("Totals do not read per sheet"));
    put(&d, D, POOL.as_bytes());
    let mut t = table(&d);
    t["sheet_stages"] = serde_json::json!([]);
    put(&d, "dev/work-budget.json", t.to_string().as_bytes());
    assert_eq!(set(&d, &[]).code, 1);
}

#[test]
fn counts_are_compared_per_sheet() {
    let d = pool_tree("bc-sheets-compare");
    assert_eq!(
        run(&d, &["sheets", "placer", "alpha-sheet=1"]).stderr,
        "budget-sheets: no pool-sheet stage `placer` in dev/work-budget.json - set it first: make budget-set PHASE=placer DERIVATION=<its derivation> VERDICT=<its SOUND verdict>\n"
    );
    assert_eq!(set(&d, &[]).code, 0);
    let got = run(&d, &["sheets", "placer", "alpha-sheet=2400 beta-sheet=480"]);
    assert_eq!(
        got.stdout,
        "budget-sheets: | sheet | counted | budget | ratio |\n|---|---|---|---|\n| alpha-sheet | 2,400 | 240 | 10.0x |\n| beta-sheet | 480 | 480 | 1.0x |\n| **the sheets given** | 2,880 | 720 | 4.0x |\npast twice the budget (the audit's leeway, 444 FR-022): alpha-sheet\n"
    );
    let some = run(&d, &["sheets", "placer", "beta-sheet=100"]);
    assert!(some.stdout.contains("not counted: alpha-sheet"), "{some:?}");
    for (bad, why) in [
        ("alpha-sheet", "`alpha-sheet` is no count"),
        ("alpha-sheet=x", "`alpha-sheet=x` is no count"),
        (
            "gamma=1",
            "`gamma` is no sheet of `placer` - its sheets are: alpha-sheet, beta-sheet",
        ),
    ] {
        let r = run(&d, &["sheets", "placer", bad]);
        assert_eq!(r.code, 1);
        assert!(r.stderr.contains(why), "{r:?}");
    }
    // a budget of nothing has no ratio
    let mut t = table(&d);
    t["sheet_stages"]["placer"]["sheets"]["beta-sheet"]["budget"] = serde_json::json!(0);
    put(&d, "dev/work-budget.json", t.to_string().as_bytes());
    assert!(run(&d, &["sheets", "placer", "beta-sheet=1"])
        .stdout
        .contains("| beta-sheet | 1 | 0 | - |"));
    t["sheet_stages"]["placer"]["sheets"] = serde_json::json!([]);
    put(&d, "dev/work-budget.json", t.to_string().as_bytes());
    assert_eq!(run(&d, &["sheets", "placer", "beta-sheet=1"]).code, 1);
}
