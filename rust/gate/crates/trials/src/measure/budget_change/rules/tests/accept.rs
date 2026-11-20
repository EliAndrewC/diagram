//! A rebuilt phase accepted (`make budget-accept`): its audit, its run, its sizes and every budget check, on a scratch table
//! (feature 449 T134; split from `rules/tests.rs` by T226).

use l7r_gate_core::checks::scratch;
use serde_json::json;

use super::{args, edit, put, run, table, tree};

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
    assert_eq!(accept("within.txt", &json!({"20": {"ops": 90}, "40": {"ops": 100}}), &[]).stderr, "budget-accept: the newest run, 20261110T000000Z-x.json, has no count at 80 households for `seat` - run `make work-budget`, which counts it at 40 and 80 households; a stage is never accepted at 0 operations, a count its counters missed\n");
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
    // nothing counted is no count, never an accepted 0 (feature 449 T226)
    assert!(accept("within.txt", &per(0, 0, 0), &[])
        .stderr
        .contains("has no count at 40 households for `seat`"));
    edit(&d, |t| t["stages"]["seat"]["per_thing"] = json!(1.0));
    assert_eq!(accept("within.txt", &per(1, 1, 1), &[]).stdout, "budget-accept: `seat` accepted at its counted operations at 40 and 80 households, logged in dev/work-budget-changes.jsonl\n");
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
    assert_eq!(run(&d, &["accept", "seat", "within.txt"]).stderr, "budget-accept: no `make work-budget` run counts `seat` - run `make work-budget`, which counts it at 40 and 80 households, first\n");
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
fn a_form_is_accepted_on_the_newest_run_by_its_own_name() {
    let d = scratch("bc-accept-form");
    tree(&d);
    put(&d, "within.txt", b"WITHIN\n");
    assert_eq!(run(&d, &["accept", "field.polder", "within.txt"]).stderr, "budget-accept: no `make work-budget` run counts `field.polder` - run `make work-budget`, which counts it at 10 and 20 households, first\n");
    put(
        &d,
        "dev/work-budget/20261110T000000Z-x-rust-a.json",
        json!({"summary": {"stages": {"field.polder": {"per": {"10": {"ops": 5}, "20": {"ops": 5}}}}}})
            .to_string()
            .as_bytes(),
    );
    assert_eq!(run(&d, &["accept", "field.polder", "within.txt"]).code, 0);
    for (sizes, code) in [
        (json!(["10", 20.0]), 0),
        // one size is a sentence of one
        (json!([10]), 0),
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

/// The run of 2026-11-20 (feature 449 T226): a Python-era `-spec` run held the stage's name at 0 operations, the newest run -
/// the Rust driver's, `<stamp>-rust-<engine>.json` - held the form's counts under its own name, and the accept read the first,
/// recorded 0 at 10 and 20 households, and said it had accepted at 40 and 80.
#[test]
fn the_newest_run_holds_a_forms_counts_at_its_own_sizes() {
    let d = scratch("bc-accept-newest");
    tree(&d);
    put(&d, "within.txt", b"WITHIN\n");
    edit(&d, |t| {
        t["stages"]["field.polder"]["items_at_20"] = json!(6);
    });
    let zeros = json!({"10": {"calls": 0.0, "ops": 0.0}, "20": {"calls": 0.0, "ops": 0.0}, "40": {"ops": 0.0}, "80": {"ops": 0.0}});
    put(
        &d,
        "dev/work-budget/20261106T073003Z-ab150ef58e21-spec.json",
        json!({"summary": {"stages": {"field": {"per": zeros}}}})
            .to_string()
            .as_bytes(),
    );
    let newest = "20261120T053709Z-rust-e111c32c6.json";
    let rust = |per: serde_json::Value| {
        put(
            &d,
            &format!("dev/work-budget/{newest}"),
            json!({"meta": {"driver": "rust"}, "summary": {"stages": {"field.polder": {"per": per}}}})
                .to_string()
                .as_bytes(),
        );
    };
    rust(json!({"10": {"ops": 5, "rolled": 4}, "20": {"ops": 6, "rolled": 4}}));
    let done = run(&d, &["accept", "field.polder", "within.txt"]);
    assert_eq!(
        table(&d)["stages"]["field.polder"]["accepted"],
        json!({"10": 5.0, "20": 6.0})
    );
    assert_eq!(done.stdout, "budget-accept: `field.polder` accepted at its counted operations at 10 and 20 households, logged in dev/work-budget-changes.jsonl\n");
    let row = std::fs::read_to_string(d.join("dev/work-budget-changes.jsonl")).unwrap();
    assert!(
        row.trim_end()
            .ends_with(&format!("\"run\": \"{newest}\"}}")),
        "{row}"
    );
    // a size the newest run holds no count at - none, no `ops`, or 0 operations - is refused, never recorded as 0
    for per in [
        json!({"20": {"ops": 6}}),
        json!({"10": {"rolled": 4}, "20": {"ops": 6}}),
        json!({"10": {"ops": 0, "rolled": 4}, "20": {"ops": 6}}),
    ] {
        rust(per);
        assert_eq!(run(&d, &["accept", "field.polder", "within.txt"]).stderr, format!("budget-accept: the newest run, {newest}, has no count at 10 households for `field.polder` - run `make work-budget`, which counts it at 10 and 20 households; a stage is never accepted at 0 operations, a count its counters missed\n"));
    }
    assert_eq!(
        table(&d)["stages"]["field.polder"]["accepted"],
        json!({"10": 5.0, "20": 6.0})
    );
    // a roll that is no mapping is Python's AttributeError
    rust(json!({"10": [1], "20": {"ops": 6}}));
    assert_eq!(run(&d, &["accept", "field.polder", "within.txt"]).code, 1);
    // a newer run that does not count the stage is the newest run, and counts nothing for it
    put(
        &d,
        "dev/work-budget/20261121T000000Z-rust-f.json",
        br#"{"summary": {"stages": {"field": {"per": {}}}}}"#,
    );
    assert_eq!(run(&d, &["accept", "field.polder", "within.txt"]).stderr, "budget-accept: no `make work-budget` run counts `field.polder` - run `make work-budget`, which counts it at 10 and 20 households, first\n");
}

/// An audit verdict is kept in the repository, beside its stage's derivation (feature 449 T226: one was recorded as a path under a
/// session's temporary directory).
#[test]
fn an_audit_outside_the_repository_is_refused() {
    let d = scratch("bc-accept-audit");
    tree(&d);
    put(&d, "within.txt", b"WITHIN\n");
    put(
        &d,
        "dev/work-budget/20261120T053709Z-rust-e.json",
        json!({"summary": {"stages": {"field.polder": {"per": {"10": {"ops": 5}, "20": {"ops": 5}}}}}})
            .to_string()
            .as_bytes(),
    );
    // the Python-era form of a form's run, which today's accept reads, so that the refusal below is the audit's own
    put(
        &d,
        "dev/work-budget/20261106T000000Z-x-spec.json",
        json!({"summary": {"stages": {"field": {"per": {"10": {"ops": 5}, "20": {"ops": 5}}}}}})
            .to_string()
            .as_bytes(),
    );
    let tmp = scratch("bc-accept-audit-tmp");
    let outside = tmp.join("T226-audit-verdict.txt");
    put(&tmp, "T226-audit-verdict.txt", b"WITHIN\n");
    put(&d, "specs/x/phases/field_polder.audit-2.txt", b"WITHIN\n");
    put(&d, "specs/x/phases/field_polder.audit-x.txt", b"WITHIN\n");
    let refusal = |audit: &str| {
        format!("budget-accept: {audit} is outside the repository - an audit verdict belongs beside the stage's derivation, as specs/444-work-budget-program/phases/waterward.audit-4.txt is: save it as specs/x/phases/field_polder.audit-3.txt and pass that\n")
    };
    let o = outside.to_string_lossy().into_owned();
    assert_eq!(run(&d, &["accept", "field.polder", &o]).stderr, refusal(&o));
    let up = format!(
        "specs/../../{}/T226-audit-verdict.txt",
        tmp.file_name().unwrap().to_string_lossy()
    );
    assert_eq!(
        run(&d, &["accept", "field.polder", &up]).stderr,
        refusal(&up)
    );
    assert!(table(&d)["stages"]["field.polder"]
        .get("accepted")
        .is_none());
    // a stage with no derivation is told only where
    edit(&d, |t| {
        t["stages"]["field.polder"]
            .as_object_mut()
            .unwrap()
            .remove("derivation");
    });
    assert_eq!(run(&d, &["accept", "field.polder", &o]).stderr, format!("budget-accept: {o} is outside the repository - an audit verdict belongs beside the stage's derivation, as specs/444-work-budget-program/phases/waterward.audit-4.txt is\n"));
    // an absolute path inside the repository is recorded relative to it
    let inside = d.join("specs/./x/../x/phases/field_polder.audit-2.txt");
    assert_eq!(
        run(&d, &["accept", "field.polder", &inside.to_string_lossy()]).code,
        0
    );
    assert_eq!(
        table(&d)["stages"]["field.polder"]["audit"],
        json!("specs/x/phases/field_polder.audit-2.txt")
    );
}

/// A stage accepted on a newest run whose roll at a held size is `per`: its reply, the table's `accepted` beside it.
fn accepted_on(tag: &str, per: &serde_json::Value) -> (crate::Reply, serde_json::Value) {
    let d = scratch(tag);
    tree(&d);
    put(&d, "within.txt", b"WITHIN\n");
    put(
        &d,
        "dev/work-budget/20261120T000000Z-rust-e.json",
        json!({"summary": {"stages": {"web": {"per": per}}}})
            .to_string()
            .as_bytes(),
    );
    let got = run(&d, &["accept", "web", "within.txt"]);
    (got, table(&d)["stages"]["web"]["accepted"].clone())
}

const NO_COUNT_AT_40: &str = "budget-accept: the newest run, 20261120T000000Z-rust-e.json, has no count at 40 households for `web` - run `make work-budget`, which counts it at 40 and 80 households; a stage is never accepted at 0 operations, a count its counters missed\n";

/// 0 operations at a size is no count, never an accepted 0 (feature 449 T226: the comb stage and the form were both recorded so).
#[test]
fn nothing_counted_is_never_accepted_as_0() {
    let (got, accepted) = accepted_on(
        "bc-accept-zero",
        &json!({"20": {"ops": 0}, "40": {"ops": 0}, "80": {"ops": 0}}),
    );
    assert_eq!(accepted, json!(null), "{got:?}");
    assert_eq!(got.stderr, NO_COUNT_AT_40);
}

/// A roll at a size with no `ops` is refused with the fix, not failed as Python's `KeyError`.
#[test]
fn a_roll_with_no_count_is_refused_with_the_fix() {
    let (got, accepted) = accepted_on(
        "bc-accept-no-ops",
        &json!({"20": {"ops": 50}, "40": {"rolled": 4}, "80": {"ops": 50}}),
    );
    assert_eq!(accepted, json!(null), "{got:?}");
    assert_eq!(got.stderr, NO_COUNT_AT_40);
}
