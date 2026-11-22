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

/// A pool-sheet re-derivation of `placer`: the same sheets, beta-sheet raised, the work the first one missed named.
const RAISED: &str = "# d

## Contract
- Sizes: pool sheets: alpha-sheet, beta-sheet

## The count, factor by factor
| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | N = 10, 20 | the captions | 10 to 20 |

## Totals
- at alpha-sheet: 10 x 24 = 240
- at beta-sheet: 20 x 48 = 960
- all sheets: 240 + 960 = 1200

## Work the first derivation missed
- the leader's second bend
";

const D2: &str = "specs/y/derivations/placer-r.md";
const V2: &str = "specs/y/derivations/placer-r.verdict-1.txt";

/// The red case of 449 T243: a pool-sheet raise on a SOUND re-derivation, refused at HEAD as not built.
#[test]
fn a_pool_sheet_stage_is_raised_on_a_sound_re_derivation() {
    let d = pool_tree("bc-sheets-raise");
    assert_eq!(set(&d, &[]).code, 0);
    put(&d, D2, RAISED.as_bytes());
    put(&d, V2, b"SOUND - the bend\n");
    let raise = |extra: &[&str]| {
        let mut args = vec!["set", "placer", "", "", D2, V2, "--raise"];
        args.extend(extra);
        run(&d, &args)
    };
    let got = raise(&[]);
    let want = "budget-set: `placer` raised per sheet: alpha-sheet 240; beta-sheet 960; all sheets 1,200\n";
    assert_eq!((got.code, got.stdout.as_str()), (0, want), "{got:?}");
    let t = table(&d);
    let st = &t["sheet_stages"]["placer"];
    assert_eq!(st["sheets"]["beta-sheet"]["budget"], 960.0);
    assert_eq!(st["first"]["beta-sheet"], 480.0);
    assert_eq!(st["first"]["all sheets"], 720.0);
    assert_eq!(st["derivation"], D2);
    let log = std::fs::read_to_string(d.join("dev/work-budget-changes.jsonl")).unwrap();
    let last = log.lines().last().unwrap();
    let has = last.contains("\"what\": \"raised\"")
        && last.contains("\"missed\": [\"the leader's second bend\"]");
    assert!(has, "{last}");
    // the same figures again are no raise, judged on the sheets together
    let again = raise(&[]);
    let said = "budget-set: `placer`'s re-derived budget on all sheets, 1,200, is no raise on 1,200 - a lowering re-pins with LOWER=1\n";
    assert_eq!(again.stderr, said);
    // past twice a sheet's first, a second SOUND; the first figure stands across raises
    put(
        &d,
        D2,
        RAISED
            .replace("20 x 48 = 960", "20 x 60 = 1200")
            .replace("240 + 960 = 1200", "240 + 1200 = 1440")
            .as_bytes(),
    );
    let twice = raise(&[]);
    assert!(twice.stderr.contains("on beta-sheet, 1,200, is 2.5 times its first, 480 - past 2 times a raise needs a second SOUND"), "{twice:?}");
    put(&d, "specs/y/derivations/second.txt", b"SOUND\n");
    let second = raise(&["--second", "specs/y/derivations/second.txt"]);
    assert_eq!(second.code, 0, "{second:?}");
    let first = table(&d)["sheet_stages"]["placer"]["first"]["beta-sheet"].clone();
    assert_eq!(first, 480.0);
    // past ten times the first, the GM's words
    put(
        &d,
        D2,
        RAISED
            .replace("20 x 48 = 960", "20 x 300 = 6000")
            .replace("240 + 960 = 1200", "240 + 6000 = 6240")
            .as_bytes(),
    );
    let ten = raise(&["--second", "specs/y/derivations/second.txt"]);
    assert!(ten.stderr.contains("on beta-sheet, 6,000, is past 10 times its first, 480 - an order of magnitude needs the GM's words"), "{ten:?}");
    // a raise with a second SOUND is accepted on a LEEWAY past twice its first (1,300 on a first of 480), within ten times it
    let audit = "specs/y/derivations/placer.audit-1.txt";
    put(&d, audit, b"LEEWAY\n");
    let leeway = run(
        &d,
        &[
            "accept",
            "placer",
            audit,
            "--counts",
            "alpha-sheet=1 beta-sheet=1300",
        ],
    );
    assert_eq!(leeway.code, 0, "{leeway:?}");
}

#[test]
fn a_pool_sheet_raise_owes_what_a_hamlet_raise_owes() {
    let d = pool_tree("bc-sheets-raise-refused");
    let early = run(&d, &["set", "placer", "", "", D, V, "--raise"]);
    let has = early.stderr.contains("no pool-sheet stage `placer`");
    assert!(has, "{early:?}");
    assert_eq!(set(&d, &[]).code, 0);
    // no missed work named: the leeway's, at acceptance
    let unnamed = run(&d, &["set", "placer", "", "", D, V, "--raise"]);
    let has = unnamed
        .stderr
        .contains("names no work its first derivation missed");
    assert!(has, "{unnamed:?}");
    put(&d, D2, RAISED.as_bytes());
    put(&d, V2, b"LOOSE\n");
    let loose = run(&d, &["set", "placer", "", "", D2, V2, "--raise"]);
    assert!(loose.stderr.contains("reads LOOSE, not SOUND"), "{loose:?}");
    put(&d, V2, b"SOUND\n");
    let both = run(&d, &["set", "placer", "", "", D2, V2, "--raise", "--lower"]);
    assert!(both.stderr.contains("so `--lower`"), "{both:?}");
    // a sheet the stage holds and the re-derivation drops (renamed away)
    put(
        &d,
        D2,
        RAISED.replace("alpha-sheet", "gamma-sheet").as_bytes(),
    );
    let dropped = run(&d, &["set", "placer", "", "", D2, V2, "--raise"]);
    let has = dropped.stderr.contains("names no budget for alpha-sheet");
    assert!(has, "{dropped:?}");
}

#[test]
fn a_pool_sheet_stage_changes_with_the_gms_words() {
    let d = pool_tree("bc-sheets-change");
    assert_eq!(set(&d, &[]).code, 0);
    let change = |to: &str, extra: &[&str]| {
        let mut args = vec!["change", "placer", to];
        args.extend(extra);
        run(&d, &args)
    };
    assert!(change("beta-sheet=900", &[]).stderr.contains("no WORDS"));
    let got = change("beta-sheet=900", &["--words", "make it nine hundred"]);
    let want = "budget-change: `placer` changed per sheet: alpha-sheet 240; beta-sheet 900; all sheets 1,140, logged in dev/work-budget-changes.jsonl with the GM's words\n";
    assert_eq!((got.code, got.stdout.as_str()), (0, want), "{got:?}");
    let log = std::fs::read_to_string(d.join("dev/work-budget-changes.jsonl")).unwrap();
    let last = log.lines().last().unwrap();
    let has = last.contains("\"what\": \"sheets\"")
        && last.contains("\"words\": \"make it nine hundred\"");
    assert!(has, "{last}");
    // re-pointed at a SOUND derivation, its Totals the figures
    put(&d, D2, RAISED.as_bytes());
    put(&d, V2, b"SOUND\n");
    let repoint = change(
        "",
        &["--words", "w w w", "--derivation", D2, "--verdict", V2],
    );
    assert_eq!(repoint.code, 0, "{repoint:?}");
    let t = table(&d);
    assert_eq!(
        t["sheet_stages"]["placer"]["sheets"]["beta-sheet"]["budget"],
        960.0
    );
    assert_eq!(t["sheet_stages"]["placer"]["verdict"], V2);
    for (to, extra, why) in [
        ("", vec!["--words", "w w w"], "names its figures"),
        (
            "gamma=1",
            vec!["--words", "w w w"],
            "`gamma` is no sheet of `placer`",
        ),
        ("beta-sheet", vec!["--words", "w w w"], "is no figure"),
        (
            "beta-sheet=1",
            vec!["--words", "w w w", "--derivation", D2],
            "names both its DERIVATION= and its VERDICT=",
        ),
        (
            "beta-sheet=1",
            vec!["--words", "w w w", "--exponent", "1.0"],
            "so `EXPONENT`",
        ),
    ] {
        let r = change(to, &extra);
        assert_eq!(r.code, 1, "{to} {extra:?}: {r:?}");
        assert!(r.stderr.contains(why), "{why}: {r:?}");
    }
}

#[test]
fn a_pool_sheet_stage_is_accepted_on_its_audit_and_its_counts() {
    let d = pool_tree("bc-sheets-accept");
    assert_eq!(set(&d, &[]).code, 0);
    put(&d, "specs/y/derivations/placer.audit-1.txt", b"WITHIN\n");
    put(&d, "specs/y/derivations/placer.audit-2.txt", b"LEEWAY\n");
    let accept =
        |audit: &str, counts: &str| run(&d, &["accept", "placer", audit, "--counts", counts]);
    let a1 = "specs/y/derivations/placer.audit-1.txt";
    let a2 = "specs/y/derivations/placer.audit-2.txt";
    let none = run(&d, &["accept", "placer", a1]);
    assert!(none.stderr.contains("COUNTS="), "{none:?}");
    let short = accept(a1, "alpha-sheet=200");
    assert!(short.stderr.contains("no count on beta-sheet"), "{short:?}");
    let over = accept(a1, "alpha-sheet=200 beta-sheet=500");
    assert!(over.stderr.contains("`placer`: 500 counted operations on beta-sheet, 1.04 times its budget 480 - over it, a phase is accepted on the MODE AUDIT's LEEWAY"), "{over:?}");
    let past = accept(a2, "alpha-sheet=200 beta-sheet=1000");
    let has = past.stderr.contains("past the leeway's 2 times");
    assert!(has, "{past:?}");
    let got = accept(a2, "alpha-sheet=200 beta-sheet=500");
    let want = "budget-accept: `placer` accepted at its counted operations on alpha-sheet and beta-sheet, logged in dev/work-budget-changes.jsonl\n";
    assert_eq!((got.code, got.stdout.as_str()), (0, want), "{got:?}");
    let t = table(&d);
    assert_eq!(t["sheet_stages"]["placer"]["status"], "accepted");
    assert_eq!(t["sheet_stages"]["placer"]["accepted"]["beta-sheet"], 500.0);
    // accepted, it raises no more
    put(&d, D2, RAISED.as_bytes());
    put(&d, V2, b"SOUND\n");
    let raise = run(&d, &["set", "placer", "", "", D2, V2, "--raise"]);
    let has = raise
        .stderr
        .contains("`placer` is accepted - RAISE=1 raises a budgeted stage");
    assert!(has, "{raise:?}");
    let outside = accept("../x.txt", "alpha-sheet=1 beta-sheet=1");
    let has = outside.stderr.contains("is outside the repository");
    assert!(has, "{outside:?}");
}

#[test]
fn a_pool_sheet_stage_s_paths_refuse_what_they_cannot_take() {
    let d = pool_tree("bc-sheets-paths");
    assert_eq!(set(&d, &[]).code, 0);
    refuses_a_hamlet_argument_and_an_unread_re_point(&d);
    raises_only_on_what_it_reads(&d);
    accepts_only_what_it_can_take(&d);
}

/// A hamlet stage's accept takes no COUNTS, SECOND= is a raise's, and a re-point whose Totals do not read is refused.
fn refuses_a_hamlet_argument_and_an_unread_re_point(d: &std::path::Path) {
    let hamlet = run(d, &["accept", "seat", "a.txt", "--counts", "x=1"]);
    let has = hamlet.stderr.contains("COUNTS= is a pool-sheet stage's");
    assert!(has, "{hamlet:?}");
    let lone = set(d, &["--second", V]);
    let has = lone.stderr.contains("SECOND= is a raise's second SOUND");
    assert!(has, "{lone:?}");
    put(d, D2, b"# nothing\n");
    put(d, V2, b"SOUND\n");
    let args = [
        "change",
        "placer",
        "",
        "--words",
        "w w w",
        "--derivation",
        D2,
        "--verdict",
        V2,
    ];
    let unread = run(d, &args);
    let has = unread.stderr.contains("Totals do not read per sheet");
    assert!(has, "{unread:?}");
}

/// A raise names the work its first derivation missed and reads its Totals per sheet; it may add a sheet, its own figure its first.
fn raises_only_on_what_it_reads(d: &std::path::Path) {
    let raise = ["set", "placer", "", "", D2, V2, "--raise"];
    let sized = "# d\n## Contract\n- Sizes: pool sheets: alpha-sheet, beta-sheet\n";
    put(d, D2, sized.as_bytes());
    let raise_unread = run(d, &raise);
    let has = raise_unread
        .stderr
        .contains("names no work its first derivation missed");
    assert!(has, "{raise_unread:?}");
    let missed = format!("{sized}## Work the first derivation missed\n- a thing\n");
    put(d, D2, missed.as_bytes());
    let raise_unread = run(d, &raise);
    let has = raise_unread.stderr.contains("Totals do not read per sheet");
    assert!(has, "{raise_unread:?}");
    let all = "- at gamma-sheet: 5 x 10 = 50\n- all sheets: 240 + 960 + 50 = 1250";
    let added = RAISED
        .replace(
            "alpha-sheet, beta-sheet",
            "alpha-sheet, beta-sheet, gamma-sheet",
        )
        .replace("N = 10, 20", "N = 10, 20, 5")
        .replace("- all sheets: 240 + 960 = 1200", all);
    put(d, D2, added.as_bytes());
    let got = run(d, &raise);
    assert_eq!(got.code, 0, "{got:?}");
    let gamma = table(d)["sheet_stages"]["placer"]["first"]["gamma-sheet"].clone();
    assert_eq!(gamma, 50.0);
}

/// An accept: a bad count, a stage not budgeted, the arbiter's accept in the audit's place.
fn accepts_only_what_it_can_take(d: &std::path::Path) {
    let audit = "specs/y/derivations/placer.audit-1.txt";
    put(d, audit, b"UNCOUNTED\n");
    let bad = run(d, &["accept", "placer", audit, "--counts", "alpha-sheet"]);
    assert!(bad.stderr.contains("reads UNCOUNTED"), "{bad:?}");
    put(d, audit, b"WITHIN\n");
    let bad = run(d, &["accept", "placer", audit, "--counts", "alpha-sheet"]);
    assert!(bad.stderr.contains("`alpha-sheet` is no count"), "{bad:?}");
    let ruling = b"{\"trigger\": \"ask:placer-x\", \"ruling\": \"accept\", \"what\": \"placer\"}\n";
    put(d, "specs/y/arbiter.jsonl", ruling);
    // the arbiter accepts no sheet over its budget, even within twice it: LEEWAY is the MODE AUDIT's alone (444 FR-006)
    let over = "alpha-sheet=1 beta-sheet=961 gamma-sheet=1";
    let ruled_over = run(
        d,
        &[
            "accept",
            "placer",
            audit,
            "--counts",
            over,
            "--arbiter",
            "ask:placer-x",
        ],
    );
    let refused = ruled_over.stderr.contains("961 counted operations on beta-sheet, 1.00 times its budget 960 - over it, a phase is accepted on the MODE AUDIT's LEEWAY");
    assert!(refused, "{ruled_over:?}");
    let counts = "alpha-sheet=1 beta-sheet=1 gamma-sheet=1";
    let ruled = run(
        d,
        &[
            "accept",
            "placer",
            audit,
            "--counts",
            counts,
            "--arbiter",
            "ask:placer-x",
        ],
    );
    assert_eq!(ruled.code, 0, "{ruled:?}");
    let accept = table(d)["sheet_stages"]["placer"]["accept"].clone();
    assert_eq!(accept, "ask:placer-x");
    let mut t = table(d);
    t["sheet_stages"]["placer"]["status"] = serde_json::json!("unbudgeted");
    put(d, "dev/work-budget.json", t.to_string().as_bytes());
    let none = run(d, &["accept", "placer", audit, "--counts", counts]);
    let has = none.stderr.contains("has no budget to be accepted against");
    assert!(has, "{none:?}");
}
