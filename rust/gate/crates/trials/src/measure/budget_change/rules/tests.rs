//! Each budget rule's refusal and its pin, on a scratch table (feature 449 T134; the same rules its differential ran against
//! `budget_change.py` over the real table, the 444 arbiter log and its derivations, 0 differing).
#![expect(
    clippy::float_cmp,
    reason = "figures Python computes exactly, compared as it compares them"
)]

use std::path::Path;

use l7r_gate_core::checks::scratch;
use serde_json::json;

use super::super::tests::{put, run, table, tree};
use super::{accepted_by, growth, py_sum, stem, today_at_40, truthy};

const SEAT: [&str; 6] = [
    "set",
    "seat",
    "2",
    "0.1",
    "specs/x/phases/seat.derivation.md",
    "specs/x/phases/seat.verdict-1.txt",
];
const ITEMS: [&str; 6] = [
    "--items-at-20",
    "1",
    "--items-at-40",
    "2",
    "--items-at-80",
    "3",
];

fn args<'a>(head: &[&'a str], tail: &[&'a str]) -> Vec<&'a str> {
    head.iter().chain(tail).copied().collect()
}

fn err(root: &Path, a: &[&str]) -> String {
    let got = run(root, a);
    assert_eq!(got.code, 1, "{a:?}: {got:?}");
    got.stderr
}

fn edit(root: &Path, f: impl FnOnce(&mut serde_json::Value)) {
    let mut t = table(root);
    f(&mut t);
    put(root, "dev/work-budget.json", t.to_string().as_bytes());
}

#[test]
fn the_figures_python_computed() {
    assert_eq!(growth(10.0, 40.0, 4.0), 1.0);
    assert_eq!(growth(0.0, 40.0, 4.0), 0.0);
    assert_eq!(growth(10.0, 0.0, 4.0), 0.0);
    // compensated, as CPython's sum() adds floats
    assert_eq!(py_sum(&[1e16, 1.0, -1e16]), 1.0,);
    assert_eq!(py_sum(&[0.1, 1e100, -1e100]), 0.1);
    assert_eq!(py_sum(&[]), 0.0);
    assert_eq!(stem("a/b/web_greenfield.derivation.md"), "web_greenfield");
    assert_eq!(stem("a/notes.md"), "notes.md");
    for (v, want) in [
        (json!(null), false),
        (json!(true), true),
        (json!(false), false),
        (json!(0), false),
        (json!(0.5), true),
        (json!(""), false),
        (json!([0]), true),
        (json!({}), false),
    ] {
        assert_eq!(truthy(&v), want, "{v}");
    }
}

#[test]
fn an_accept_names_the_stage_or_its_form() {
    let d = scratch("bc-accepted-by");
    put(
        &d,
        "specs/x/arbiter.jsonl",
        b"{\"trigger\": \"ask:p\", \"ruling\": \"accept\", \"what\": \"pin polder now\"}\n",
    );
    assert!(accepted_by(
        &d,
        "specs/x/phases/polder.derivation.md",
        "field.polder",
        "ask:p"
    )
    .unwrap());
    assert!(!accepted_by(
        &d,
        "specs/x/phases/polder.derivation.md",
        "field.dike",
        "ask:p"
    )
    .unwrap());
    // a derivation with no feature above it is Python's IndexError
    assert!(accepted_by(Path::new("/"), "x", "web", "ask:p").is_err(),);
    put(
        &d,
        "dev/work-budget/a.json",
        br#"{"summary": {"stages": {"seat": {"per": {"40": [1]}}}}}"#,
    );
    assert_eq!(today_at_40(&d, "seat"), None);
    put(
        &d,
        "dev/work-budget/b.json",
        br#"{"summary": {"stages": {"seat": {"per": {"40": {"ops": "12"}}}}}}"#,
    );
    assert_eq!(today_at_40(&d, "seat"), Some(12.0));
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "one scenario's steps in the order each builds on the last"
)]
fn a_first_budget_is_set_only_from_a_sound_verdict() {
    let d = scratch("bc-first");
    tree(&d);
    assert_eq!(err(&d, &args(&SEAT, &[])), "budget-set: no items at 20, 40, 80 households - a budget is per thing x the derivation's own items at each size: ITEMS_AT_20= ITEMS_AT_40= ITEMS_AT_80= (feature 444 D2)\n");
    assert_eq!(err(&d, &args(&["set", "nosuch", "1", "1", "d", "v"], &[])), "budget-set: no stage `nosuch` in dev/work-budget.json - the stages are: web, seat, field, field.polder\n");
    assert_eq!(
        err(
            &d,
            &args(&["set", "seat", "1", "1", "nope.md", "v"], &ITEMS)
        ),
        "budget-set: no derivation at nope.md\n"
    );
    let loose = err(
        &d,
        &args(
            &[
                "set",
                "seat",
                "1",
                "1",
                "specs/x/phases/seat.derivation.md",
                "specs/x/phases/loose.txt",
            ],
            &ITEMS,
        ),
    );
    assert_eq!(loose, "budget-set: the verdict at specs/x/phases/loose.txt reads LOOSE, not SOUND - a first budget is set only from a SOUND MODE BUDGET verdict (`make work-budget-bundle MODE=budget PHASE=seat DERIVATION=specs/x/phases/seat.derivation.md`)\n");
    assert!(err(
        &d,
        &args(
            &[
                "set",
                "seat",
                "1",
                "1",
                "specs/x/phases/seat.derivation.md",
                "none.txt"
            ],
            &ITEMS
        )
    )
    .contains("reads nothing, not SOUND"));
    assert_eq!(
        err(&d, &args(&SEAT, &["--lower"])),
        "budget-set: `seat` has no budget to lower - a first one is set without LOWER\n"
    );
    assert_eq!(
        err(&d, &args(&SEAT, &["--lower", "--raise"])),
        "budget-set: RAISE=1 and LOWER=1 together - a re-pin is one or the other\n"
    );
    assert_eq!(err(&d, &args(&SEAT, &["--raise"])), "budget-set: `seat` is unbudgeted - RAISE=1 raises a budgeted stage, before its acceptance (feature 444 FR-022)\n");
    // above today's count at 40 (50 in the newest run), and past S6's growth cap
    let above = err(
        &d,
        &args(
            &[
                "set",
                "seat",
                "100",
                "0.1",
                "specs/x/phases/seat.derivation.md",
                "specs/x/phases/seat.verdict-1.txt",
            ],
            &ITEMS,
        ),
    );
    assert_eq!(above, "budget-set: `seat`'s budget at 40 households, 200, is above what the stage counts today, 50 (the newest `make work-budget` run) - a budget the stage already meets is no target (ask:444-budget-standard). Re-derive at the typical case, or name why: REASON=\"<why this stage needs more than it does today>\"\n");
    let fast = err(
        &d,
        &args(
            &SEAT,
            &[
                "--items-at-20",
                "1",
                "--items-at-40",
                "10",
                "--items-at-80",
                "100",
            ],
        ),
    );
    assert_eq!(fast, "budget-set: `seat`'s budget grows at an exponent of 3.32 from 20 to 80 households, past rubric S6's 1.15 (n log n at most) - re-derive it, or name why its n is bounded: GROWTH_REASON=\"<why>\"\n");
    let set = run(
        &d,
        &args(
            &[
                "set",
                "seat",
                "100",
                "0.1",
                "specs/x/phases/seat.derivation.md",
                "specs/x/phases/seat.verdict-1.txt",
            ],
            &[
                "--items-at-20",
                "1",
                "--items-at-40",
                "10",
                "--items-at-80",
                "100",
                "--reason",
                "  room  ",
                "--growth-reason",
                " bounded ",
            ],
        ),
    );
    assert_eq!(set.code, 0, "{set:?}");
    assert_eq!(
        table(&d)["stages"]["seat"],
        json!({"status": "budgeted", "per_thing": 100.0, "exponent": 0.1, "derivation": "specs/x/phases/seat.derivation.md", "verdict": "specs/x/phases/seat.verdict-1.txt", "items_at_20": 1, "items_at_40": 10, "items_at_80": 100, "reason": "room", "growth_reason": "bounded"})
    );
    assert_eq!(
        err(&d, &args(&SEAT, &ITEMS)),
        "budget-set: `seat` is budgeted already - a change needs the GM's words: make budget-change PHASE=seat TO=<per thing> WORDS=\"<the GM's words>\"; a lowering re-pins with LOWER=1\n"
    );
    put(&d, "specs/x/phases/bad.derivation.md", b"\xff");
    edit(&d, |t| {
        t["stages"]["seat"] = json!({"status": "unbudgeted"});
    });
    assert_eq!(
        err(
            &d,
            &args(
                &[
                    "set",
                    "seat",
                    "1",
                    "1",
                    "specs/x/phases/bad.derivation.md",
                    "specs/x/phases/seat.verdict-1.txt"
                ],
                &ITEMS
            )
        )
        .lines()
        .count(),
        1
    );
    put(&d, "dev/work-budget/20261109T000000Z-z.json", b"{");
    // a run that does not read counts nothing today
    assert_eq!(run(&d, &args(&SEAT, &ITEMS)).code, 0,);
}

#[test]
fn a_form_is_budgeted_at_its_bounded_n() {
    let d = scratch("bc-form");
    tree(&d);
    edit(&d, |t| {
        t["stages"]
            .as_object_mut()
            .unwrap()
            .shift_remove("field.polder");
    });
    let set = run(
        &d,
        &[
            "set",
            "field.polder",
            "2",
            "0.3",
            "specs/x/phases/polder.derivation.md",
            "specs/x/phases/seat.verdict-1.txt",
            "--items-at-10",
            "4",
            "--items-at-20",
            "6",
        ],
    );
    assert_eq!(set.code, 0, "{set:?}");
    assert_eq!(
        table(&d)["stages"]["field.polder"]["sizes"],
        json!([10, 20])
    );
    assert_eq!(
        err(&d, &["set", "other.form", "1", "1", "d", "v"])
            .lines()
            .count(),
        1
    );
    // a form's raise is judged at its top size, its bounded n
    put(
        &d,
        "specs/x/phases/polder.derivation.md",
        b"a bounded n: households 10-20\n## Work the first derivation missed\n- the dike\n",
    );
    let raised = run(
        &d,
        &[
            "set",
            "field.polder",
            "3",
            "0.3",
            "specs/x/phases/polder.derivation.md",
            "specs/x/phases/seat.verdict-1.txt",
            "--raise",
            "--items-at-10",
            "4",
            "--items-at-20",
            "6",
            "--growth-reason",
            "g",
        ],
    );
    assert_eq!(raised.code, 0, "{raised:?}");
    assert_eq!(
        table(&d)["stages"]["field.polder"]["first"],
        json!({"10": 8.0, "20": 12.0})
    );
}

#[test]
fn the_arbiters_accept_pins_a_first_budget() {
    let d = scratch("bc-arbiter");
    tree(&d);
    let log = "\nnot json\n{\"trigger\": \"ask:a\", \"ruling\": \"accept\", \"what\": \"pin seat on this\"}\n{\"trigger\": \"ask:b\", \"ruling\": \"accept\", \"what\": null}\n{\"trigger\": \"ask:seat_greenfield-3\", \"ruling\": \"accept\"}\n{\"trigger\": \"ask:c\", \"ruling\": \"continue\", \"what\": \"seat\"}\n";
    put(&d, "specs/x/arbiter.jsonl", log.as_bytes());
    put(&d, "specs/x/phases/seat_greenfield.derivation.md", b"x\n");
    put(
        &d,
        "specs/x/phases/seat_greenfield.verdict-1.txt",
        b"SOUND\n",
    );
    put(
        &d,
        "specs/x/phases/seat_greenfield.verdict-2.txt",
        b"LOOSE\n",
    );
    let pin = |trigger: &str, spread: &str, derivation: &str| {
        edit(&d, |t| {
            t["stages"]["seat"] = json!({"status": "unbudgeted"});
        });
        run(
            &d,
            &args(
                &[
                    "set",
                    "seat",
                    "1",
                    "0.1",
                    derivation,
                    "",
                    "--arbiter",
                    trigger,
                    "--spread",
                    spread,
                ],
                &ITEMS,
            ),
        )
    };
    assert_eq!(
        pin(
            "ask:a",
            "100-200 at 40",
            "specs/x/phases/seat.derivation.md"
        )
        .code,
        0
    );
    let pinned = &table(&d)["stages"]["seat"];
    assert_eq!(
        (
            pinned["verdict"].clone(),
            pinned["pinned_on"].clone(),
            pinned["rounds"].clone(),
            pinned["spread"].clone()
        ),
        (
            json!("ask:a"),
            json!("accept"),
            json!(1),
            json!("100-200 at 40")
        )
    );
    assert_eq!(
        pinned["derivation_sha"],
        json!("0c8ba7112d299243d989dfbb1e7effa7c887262265078c3070c2f673d04f2e13")
    );
    assert_eq!(
        pin(
            "ask:seat_greenfield-3",
            " 1,000-2,000 at 40 ",
            "specs/x/phases/seat_greenfield.derivation.md"
        )
        .code,
        0
    );
    assert_eq!(table(&d)["stages"]["seat"]["rounds"], json!(2));
    assert_eq!(pin("ask:a", "100 at 40", "specs/x/phases/seat.derivation.md").stderr, "budget-set: an accept-pinned budget records its totals' spread across the rounds, for the program target: SPREAD=\"<low>-<high> at <households>\" (feature 444 FR-013)\n");
    for trigger in ["ask:b", "ask:c", "ask:none"] {
        assert_eq!(
            pin(trigger, "1-2 at 40", "specs/x/phases/seat.derivation.md").stderr,
            format!("budget-set: the round arbiter's log holds no accept at {trigger} naming `seat` - an accept pins a first budget only as the arbiter gave it (feature 444 FR-013)\n")
        );
    }
    put(&d, "specs/x/arbiter.jsonl", b"[1]\n");
    assert_eq!(
        pin("ask:a", "1-2 at 40", "specs/x/phases/seat.derivation.md").code,
        1
    );
    std::fs::remove_file(d.join("specs/x/arbiter.jsonl")).unwrap();
    assert!(
        pin("ask:a", "1-2 at 40", "specs/x/phases/seat.derivation.md")
            .stderr
            .contains("holds no accept")
    );
    put(&d, "top.md", b"x\n");
    // the log beside a derivation at the root is the root's parent's
    assert!(pin("ask:a", "1-2 at 40", "top.md")
        .stderr
        .contains("holds no accept"),);
}

#[test]
fn a_lowering_never_raises() {
    let d = scratch("bc-lower");
    tree(&d);
    let web = [
        "set",
        "web",
        "5",
        "0.1",
        "specs/x/phases/web.derivation.md",
        "specs/x/phases/web.verdict-1.txt",
        "--lower",
    ];
    let rise = err(
        &d,
        &args(
            &web,
            &[
                "--items-at-20",
                "30",
                "--items-at-40",
                "10",
                "--items-at-80",
                "30",
            ],
        ),
    );
    assert_eq!(rise, "budget-set: `web` would rise at 20, 80 households (150 against 100, 150 against 100) - a raise needs the GM's words: make budget-change PHASE=web TO=<per thing> WORDS=\"<the GM's words>\"\n");
    let lowered = run(
        &d,
        &args(
            &web,
            &[
                "--items-at-20",
                "10",
                "--items-at-40",
                "10",
                "--items-at-80",
                "10",
            ],
        ),
    );
    assert_eq!(lowered.code, 0, "{lowered:?}");
    let log = std::fs::read_to_string(d.join("dev/work-budget-changes.jsonl")).unwrap();
    assert!(log.lines().last().unwrap().ends_with("\"what\": \"lowered\", \"phase\": \"web\", \"from\": {\"20\": 100.0, \"40\": 100.0, \"80\": 100.0}, \"to\": {\"20\": 50.0, \"40\": 50.0, \"80\": 50.0}, \"verdict\": \"specs/x/phases/web.verdict-1.txt\"}"), "{log}");
    edit(&d, |t| {
        t["stages"]["web"]
            .as_object_mut()
            .unwrap()
            .shift_remove("items_at_80");
    });
    // a budget short of its items is Python's KeyError
    assert_eq!(
        run(
            &d,
            &args(
                &web,
                &[
                    "--items-at-20",
                    "1",
                    "--items-at-40",
                    "1",
                    "--items-at-80",
                    "1"
                ]
            )
        )
        .code,
        1,
    );
}

#[test]
fn a_raise_names_its_missed_work_and_its_second_sound() {
    let d = scratch("bc-raise");
    tree(&d);
    put(&d, "specs/x/phases/web_r.derivation.md", b"# r\n## Work the first derivation missed\n\n- the ribbon\n-   \n- the  crossings \n\n## After\n- not this\n");
    put(&d, "specs/x/phases/sound2.txt", b"SOUND\n");
    let raise = |pt: &str, extra: &[&str]| {
        run(
            &d,
            &args(
                &[
                    "set",
                    "web",
                    pt,
                    "0.1",
                    "specs/x/phases/web_r.derivation.md",
                    "specs/x/phases/seat.verdict-1.txt",
                    "--raise",
                    "--items-at-20",
                    "10",
                    "--items-at-40",
                    "10",
                    "--items-at-80",
                    "10",
                    "--reason",
                    "r",
                ],
                extra,
            ),
        )
    };
    assert_eq!(raise("10", &[]).stderr, "budget-set: `web`'s re-derived budget at 40, 100, is no raise on 100 - a lowering re-pins with LOWER=1\n");
    assert_eq!(raise("101", &[]).stderr, "budget-set: `web`'s re-derived budget at 40, 1,010, is past 10 times its first, 100 - an order of magnitude needs the GM's words (feature 444 FR-022): make budget-change PHASE=web TO=<per thing> DERIVATION= VERDICT= WORDS=\"<the GM's words>\"\n");
    let past_twice = "budget-set: `web`'s re-derived budget at 40, 300, is 3.0 times its first, 100 - past 2 times a raise needs a second SOUND, from an independent MODE BUDGET dispatch of the same bundle blind to the first: SECOND=<its verdict file>";
    assert_eq!(raise("30", &[]).stderr, format!("{past_twice}\n"));
    assert_eq!(
        raise("30", &["--second", "specs/x/phases/seat.verdict-1.txt"]).stderr,
        format!("{past_twice}\n")
    );
    assert_eq!(
        raise("30", &["--second", "specs/x/phases/loose.txt"]).stderr,
        format!("{past_twice} (specs/x/phases/loose.txt reads LOOSE)\n")
    );
    assert_eq!(
        raise("30", &["--second", "none.txt"]).stderr,
        format!("{past_twice} (none.txt reads nothing)\n")
    );
    assert_eq!(
        raise("30", &["--second", "specs/x/phases/sound2.txt"]).code,
        0
    );
    let pinned = &table(&d)["stages"]["web"];
    assert_eq!(
        (pinned["first"].clone(), pinned["second"].clone()),
        (
            json!({"20": 100.0, "40": 100.0, "80": 100.0}),
            json!("specs/x/phases/sound2.txt")
        )
    );
    let log = std::fs::read_to_string(d.join("dev/work-budget-changes.jsonl")).unwrap();
    assert!(log.lines().last().unwrap().ends_with("\"verdict\": \"specs/x/phases/seat.verdict-1.txt\", \"missed\": [\"the ribbon\", \"the  crossings\"]}"), "{log}");
    // the first figure stands across raises, read as Python's truth reads it
    assert_eq!(raise("15", &[]).code, 1, "15 is no raise on 300");
    assert!(raise("400", &["--second", "specs/x/phases/sound2.txt"])
        .stderr
        .contains("is past 10 times its first, 100"));
    assert_eq!(
        raise("90", &["--second", "specs/x/phases/sound2.txt"]).code,
        0
    );
    assert_eq!(
        table(&d)["stages"]["web"]["first"],
        json!({"20": 100.0, "40": 100.0, "80": 100.0})
    );
    edit(&d, |t| t["stages"]["web"]["first"] = json!({"40": 0}));
    // a first of 0 is falsy: the standing budget is the first
    assert_eq!(raise("95", &[]).code, 0,);
    edit(&d, |t| t["stages"]["web"]["first"] = json!({"40": "2000"}));
    assert_eq!(raise("100", &[]).code, 0);
    edit(&d, |t| t["stages"]["web"]["first"] = json!([1]));
    // a first that is no mapping is Python's AttributeError
    assert_eq!(raise("700", &[]).code, 1,);
    put(&d, "specs/x/phases/web_r.derivation.md", b"\xff");
    assert_eq!(raise("700", &[]).code, 1);
    std::fs::remove_file(d.join("specs/x/phases/web_r.derivation.md")).unwrap();
    assert!(raise("700", &[])
        .stderr
        .contains("names no work its first derivation missed"));
    assert_eq!(run(&d, &args(&["set", "field", "2", "0.1", "specs/x/phases/web.derivation.md", "v", "--raise"], &ITEMS)).stderr, "budget-set: `field` is accepted - RAISE=1 raises a budgeted stage, before its acceptance (feature 444 FR-022)\n");
}

#[test]
fn a_change_takes_the_gms_words_and_repoints() {
    let d = scratch("bc-change");
    tree(&d);
    let change = |extra: &[&str]| {
        run(
            &d,
            &args(&["change", "web", "4", "--words", "the GM said so"], extra),
        )
    };
    assert_eq!(
        change(&["--derivation", "specs/x/phases/web.derivation.md"]).stderr,
        "budget-change: re-pointing a stage names both its DERIVATION= and its VERDICT=\n"
    );
    assert_eq!(
        change(&["--derivation", "nope.md", "--verdict", "v"]).stderr,
        "budget-change: no derivation at nope.md\n"
    );
    assert_eq!(
        change(&["--derivation", "specs/x/phases/web.derivation.md", "--verdict", "specs/x/phases/loose.txt"]).stderr,
        "budget-change: specs/x/phases/loose.txt is no SOUND verdict - a stage is re-pointed only at a derivation its verdict judged SOUND\n"
    );
    assert_eq!(
        change(&[
            "--derivation",
            "specs/x/phases/web.derivation.md",
            "--verdict",
            "specs/x/phases/seat.verdict-1.txt",
            "--exponent",
            "0.7",
            "--items-at-40",
            "7",
            "--items-at-20",
            "5",
            "--items-at-40",
            "8"
        ])
        .code,
        0
    );
    assert_eq!(
        table(&d)["stages"]["web"],
        json!({"status": "budgeted", "per_thing": 4.0, "exponent": 0.7, "derivation": "specs/x/phases/web.derivation.md", "verdict": "specs/x/phases/seat.verdict-1.txt", "items_at_20": 5, "items_at_40": 8, "items_at_80": 10})
    );
    let log = std::fs::read_to_string(d.join("dev/work-budget-changes.jsonl")).unwrap();
    assert!(log.lines().last().unwrap().ends_with("\"what\": \"stage\", \"phase\": \"web\", \"from\": {\"per_thing\": 10.0, \"exponent\": 0.1, \"items_at_20\": 10, \"items_at_40\": 10}, \"to\": {\"per_thing\": 4.0, \"exponent\": 0.7, \"items_at_20\": 5, \"items_at_40\": 8}, \"words\": \"the GM said so\"}"), "{log}");
    assert_eq!(run(&d, &["change", "seat", "1", "--words", "a b c"]).stderr, "budget-change: `seat` has no budget yet - a first one is set from a SOUND verdict: make budget-set PHASE=seat PER_THING= EXPONENT= DERIVATION= VERDICT=\n");
    assert!(run(&d, &["change", "nosuch", "1", "--words", "a b c"])
        .stderr
        .starts_with("budget-change: no stage `nosuch`"));
    edit(&d, |t| {
        t["stages"]["web"]
            .as_object_mut()
            .unwrap()
            .shift_remove("exponent");
    });
    // a stage with no exponent is Python's KeyError
    assert_eq!(run(&d, &["change", "web", "1", "--words", "a b c"]).code, 1,);
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "one scenario's steps in the order each builds on the last"
)]
fn a_phase_is_accepted_on_its_audit_within_its_budget() {
    let d = scratch("bc-accept");
    tree(&d);
    edit(
        &d,
        |t| t["stages"]["seat"] = json!({"status": "budgeted", "per_thing": 10.0, "exponent": 0.1, "derivation": "specs/x/phases/seat_greenfield.derivation.md", "items_at_20": 10, "items_at_40": 10, "items_at_80": 10}),
    );
    put(&d, "within.txt", b"WITHIN\n");
    put(&d, "leeway.txt", b"LEEWAY\n");
    let accept = |audit: &str, per: &serde_json::Value, extra: &[&str]| {
        put(
            &d,
            "dev/work-budget/20261110T000000Z-x.json",
            json!({"summary": {"stages": {"seat": {"per": per}}}})
                .to_string()
                .as_bytes(),
        );
        run(&d, &args(&["accept", "seat", audit], extra))
    };
    let per =
        |a: i64, b: i64, c: i64| json!({"20": {"ops": a}, "40": {"ops": b}, "80": {"ops": c}});
    assert_eq!(accept("loose.txt", &per(100, 100, 100), &[]).stderr, "budget-accept: loose.txt reads nothing, not WITHIN or LEEWAY - a phase is accepted on its MODE AUDIT's WITHIN, or LEEWAY at up to 2 times its budget (`make work-budget-bundle MODE=audit PHASE=seat`)\n");
    assert_eq!(
        accept("within.txt", &per(90, 101, 100), &[]).stderr,
        "budget-accept: `seat`: 101 counted operations at 40 households, 1.01 times its budget 100 - over it, a phase is accepted on the MODE AUDIT's LEEWAY - rebuild it again, raise the budget on a SOUND re-derivation naming the work it missed (`make budget-set RAISE=1`, FR-022), or with the GM's words (`make budget-change`, FR-006)\n"
    );
    assert!(accept("leeway.txt", &per(90, 201, 100), &[])
        .stderr
        .contains("2.01 times its budget 100, past the leeway's 2 times - rebuild"));
    assert_eq!(accept("within.txt", &json!({"20": {"ops": 90}, "40": {"ops": 100}}), &[]).stderr, "budget-accept: the newest run has no roll at 80 households for `seat` - run `make work-budget` at every size\n");
    assert_eq!(accept("within.txt", &per(10, 50, 100), &[]).stderr, "budget-accept: `seat` grows at an exponent of 1.66 from 20 to 80 households, past its budget's 0.00 (rubric S6, FR-005) - rebuild it again, or raise the budget with the GM's words\n");
    let none_at_20 = accept(
        "within.txt",
        &json!({"40": {"ops": 50}, "80": {"ops": 100}}),
        &[],
    );
    // no roll at 20 grows at nothing
    assert_eq!(none_at_20.code, 0,);
    assert_eq!(
        accept(
            "within.txt",
            &json!({"20": {}, "40": {"ops": 50}, "80": {"ops": 100}}),
            &[]
        )
        .code,
        0
    );
    assert_eq!(
        accept(
            "within.txt",
            &json!({"20": [1], "40": {"ops": 50}, "80": {"ops": 100}}),
            &[]
        )
        .code,
        1
    );
    assert_eq!(
        accept(
            "within.txt",
            &json!({"20": {"x": 1}, "40": {"ops": 50}, "80": {"ops": 100}}),
            &[]
        )
        .code,
        0
    );
    assert_eq!(accept("within.txt", &json!([1]), &[]).code, 1);
    assert_eq!(
        accept(
            "within.txt",
            &json!({"20": {"ops": 1}, "40": {"x": 1}, "80": {"ops": 1}}),
            &[]
        )
        .code,
        1
    );
    assert_eq!(accept("leeway.txt", &per(100, 150, 100), &[]).code, 0);
    let row = std::fs::read_to_string(d.join("dev/work-budget-changes.jsonl")).unwrap();
    assert!(row.lines().last().unwrap().ends_with("\"what\": \"accepted\", \"phase\": \"seat\", \"accepted\": {\"40\": 150.0, \"80\": 100.0}, \"audit\": \"leeway.txt\", \"run\": \"20261110T000000Z-x.json\"}"), "{row}");
    // the raise's caps: twice the first on one SOUND, ten times it on two
    edit(&d, |t| {
        t["stages"]["seat"]["first"] = json!({"40": 10, "80": 100});
    });
    assert_eq!(accept("within.txt", &per(100, 100, 100), &[]).stderr, "budget-accept: `seat`: 100 counted operations at 40 households, past 2 times its first budget 10 - past twice the first, its raise owes a second, independent SOUND (`make budget-set RAISE=1 SECOND=`) or the GM's words (FR-022)\n");
    edit(&d, |t| t["stages"]["seat"]["second"] = json!("x"));
    assert_eq!(accept("within.txt", &per(100, 100, 100), &[]).code, 0);
    edit(&d, |t| {
        t["stages"]["seat"]["first"] = json!({"40": 5, "80": 100});
    });
    assert_eq!(accept("within.txt", &per(100, 100, 100), &[]).stderr, "budget-accept: `seat`: 100 counted operations at 40 households, past 10 times its first budget 5 - an order of magnitude needs the GM's words (`make budget-change`, FR-022)\n");
    // a budget of nothing over which anything counts is Python's ZeroDivisionError
    edit(
        &d,
        |t| t["stages"]["seat"] = json!({"status": "budgeted", "per_thing": 0.0, "items_at_20": 1, "items_at_40": 1, "items_at_80": 1}),
    );
    assert_eq!(accept("within.txt", &per(1, 1, 1), &[]).code, 1);
    assert_eq!(accept("within.txt", &per(0, 0, 0), &[]).code, 0);
    assert_eq!(run(&d, &["accept", "seat", "within.txt"]).stdout, "budget-accept: `seat` accepted at its counted operations at 40 and 80 households, logged in dev/work-budget-changes.jsonl\n");
    edit(&d, |t| {
        t["stages"]["seat"] = json!({"status": "unbudgeted"});
    });
    assert_eq!(
        run(&d, &["accept", "seat", "within.txt"]).stderr,
        "budget-accept: `seat` has no budget to be accepted against\n"
    );
    assert!(run(&d, &["accept", "nosuch", "within.txt"])
        .stderr
        .starts_with("budget-accept: no stage `nosuch`"));
    std::fs::remove_dir_all(d.join("dev/work-budget")).unwrap();
    edit(
        &d,
        |t| t["stages"]["seat"] = json!({"status": "budgeted", "per_thing": 1.0, "items_at_20": 1, "items_at_40": 1, "items_at_80": 1}),
    );
    assert_eq!(run(&d, &["accept", "seat", "within.txt"]).stderr, "budget-accept: no `make work-budget` run counts `seat` - run `make work-budget` (all of 10,20,40,80) first\n");
}

#[test]
fn the_arbiters_accept_stands_in_for_a_within_never_a_leeway() {
    let d = scratch("bc-accept-arbiter");
    tree(&d);
    put(
        &d,
        "specs/x/arbiter.jsonl",
        b"{\"trigger\": \"ask:a\", \"ruling\": \"accept\", \"what\": \"accept web\"}\n",
    );
    put(&d, "dev/work-budget/20261110T000000Z-x.json", json!({"summary": {"stages": {"web": {"per": {"20": {"ops": 100}, "40": {"ops": 100}, "80": {"ops": 100}}}}}}).to_string().as_bytes());
    assert_eq!(run(&d, &["accept", "web", "x", "--arbiter", "ask:none"]).stderr, "budget-accept: the round arbiter's log holds no accept at ask:none naming `web` - a phase is accepted on its MODE AUDIT's WITHIN or that accept\n");
    assert_eq!(
        run(&d, &["accept", "web", "x", "--arbiter", "ask:a"]).code,
        0
    );
    assert_eq!(table(&d)["stages"]["web"]["accept"], json!("ask:a"));
    let row = std::fs::read_to_string(d.join("dev/work-budget-changes.jsonl")).unwrap();
    assert!(row.trim_end().ends_with("\"accept\": \"ask:a\"}"));
    put(&d, "dev/work-budget/20261111T000000Z-x.json", json!({"summary": {"stages": {"web": {"per": {"20": {"ops": 100}, "40": {"ops": 101}, "80": {"ops": 100}}}}}}).to_string().as_bytes());
    assert!(run(&d, &["accept", "web", "x", "--arbiter", "ask:a"])
        .stderr
        .contains("1.01 times its budget 100 - over it"));
}

#[test]
fn a_form_is_accepted_on_its_own_spec_run() {
    let d = scratch("bc-accept-form");
    tree(&d);
    put(&d, "within.txt", b"WITHIN\n");
    assert_eq!(run(&d, &["accept", "field.polder", "within.txt"]).stderr, "budget-accept: no `make work-budget SPEC=` run counts `field.polder` - run it with the form's spec at its sizes (10, 20) first\n");
    put(
        &d,
        "dev/work-budget/20261110T000000Z-x-spec.json",
        json!({"summary": {"stages": {"field": {"per": {"10": {"ops": 5}, "20": {"ops": 5}}}}}})
            .to_string()
            .as_bytes(),
    );
    assert_eq!(run(&d, &["accept", "field.polder", "within.txt"]).code, 0);
    for (sizes, code) in [
        (json!(["10", 20.0]), 0),
        (json!({"10": 1}), 1),
        (json!([]), 1),
    ] {
        edit(&d, |t| t["stages"]["field.polder"]["sizes"] = sizes.clone());
        assert_eq!(
            run(&d, &["accept", "field.polder", "within.txt"]).code,
            code,
        );
    }
}

#[test]
fn the_program_and_a_broken_table() {
    let d = scratch("bc-program");
    tree(&d);
    assert_eq!(
        run(&d, &["program", "1", "1", "--words", ""]).stderr,
        "budget-program: no WORDS - the program's budget is set only with the GM's own words\n"
    );
    edit(&d, |t| t["program"] = json!([1]));
    assert_eq!(run(&d, &["program", "1", "1", "--words", "w"]).code, 1);
    for (text, args) in [
        ("{", &["program", "1", "1", "--words", "w"][..]),
        ("[]", &["program", "1", "1", "--words", "w"]),
        ("{}", &["accept", "web", "x"]),
        ("{\"stages\": []}", &["change", "web", "1", "--words", "w"]),
        ("{\"stages\": {\"web\": 5}}", &["accept", "web", "x"]),
        (
            "{\"stages\": {\"web\": {}}}",
            &["change", "web", "1", "--words", "w"],
        ),
        (
            "{\"stages\": {\"web\": {}}}",
            &["set", "web", "1", "1", "d", "v"],
        ),
    ] {
        put(&d, "dev/work-budget.json", text.as_bytes());
        assert_eq!(run(&d, args).code, 1, "{text} {args:?}");
    }
    put(
        &d,
        "dev/work-budget.json",
        b"{\"stages\": {\"web\": null, \"seat\": {\"status\": \"unbudgeted\"}}}",
    );
    assert!(run(&d, &["change", "web", "1", "--words", "w"])
        .stderr
        .starts_with("budget-change: no stage `web`"));
    // the program's sum reads every stage; one with no figure is Python's raise after the pin
    put(&d, "dev/work-budget.json", b"{\"stages\": {\"seat\": {\"status\": \"unbudgeted\"}, \"web\": {\"status\": \"budgeted\", \"items_at_40\": 1}}}");
    assert_eq!(run(&d, &args(&SEAT, &ITEMS)).code, 1);
    put(
        &d,
        "dev/work-budget.json",
        b"{\"stages\": {\"seat\": {\"status\": \"unbudgeted\"}, \"zzz\": null}}",
    );
    assert_eq!(run(&d, &args(&SEAT, &ITEMS)).code, 1);
    put(&d, "dev/work-budget.json", b"{\"stages\": {\"seat\": {\"status\": \"unbudgeted\"}, \"other\": {\"status\": \"unbudgeted\"}}}");
    assert!(run(&d, &args(&SEAT, &ITEMS))
        .stdout
        .ends_with("; 1 stage(s) not yet budgeted\n"));
    put(
        &d,
        "dev/work-budget.json",
        b"{\"stages\": {\"seat\": {\"status\": \"unbudgeted\"}}, \"program\": {}}",
    );
    std::fs::remove_file(d.join("dev/work-budget-changes.jsonl")).unwrap();
    std::fs::create_dir_all(d.join("dev/work-budget-changes.jsonl")).unwrap();
    // a log that cannot be opened is Python's raise
    assert_eq!(run(&d, &["program", "1", "1", "--words", "w"]).code, 1,);
}
