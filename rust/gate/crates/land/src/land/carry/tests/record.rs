//! A carry's plan review record merged beside the merged plan (451 T495): the verdict on the text the plan holds is kept, though the
//! clone's git config defines the record's driver - which, given no plan, gives a same-day tie to the incoming side.

use serde_json::{json, Value};

use super::{carried, commit, git, trees, REVIEW};

const PLAN: &str = "specs/451-x/plan.md";
const KEY: &str = "### T5 Approach (checklist part A)";
const STUB: &str = "### T5 Approach (checklist part A)\n\n1. **The goal, in the world.** <the place as it should be>\n";
const FILLED: &str = "### T5 Approach (checklist part A)\n\n1. **The goal, in the world.** The ticks refuse only what is owed.\n";

fn plan(block: &str) -> String {
    format!("# Plan\n\n{block}")
}

/// A record whose one block entry is a verdict on `block`'s text.
fn record(block: &str, verdict: &str) -> String {
    let sha = l7r_shared::sha256::hex(block.as_bytes());
    let v = json!({"blocks": {KEY: {"sha256": sha, "verdict": verdict, "reviewed": "2026-11-27"}}});
    serde_json::to_string_pretty(&v).unwrap() + "\n"
}

#[test]
fn a_carry_keeps_the_verdict_on_the_text_the_merged_plan_holds() {
    // RED FIRST (451 T495, 2026-11-27): before the pick's driver was failed, this carry is clean and the record holds the builder's
    // BLOCKED on the stub - the driver here, `cp %B %A`, takes the incoming side, as the real one does a same-day tie - T310's
    // carry, cec429b447, over the clone's CLEAR on T475's filled Approach
    let (_dir, root, builder) = trees("carry-record-held");
    git(&root, &["config", "merge.plan-review.driver", "cp %B %A"]);
    commit(
        &root,
        "the stub",
        &[
            (
                ".gitattributes",
                "specs/*/plan-review.json merge=plan-review\n",
            ),
            (PLAN, &plan(STUB)),
        ],
    );
    git(&builder, &["merge", "-q", "--ff-only", "main"]);
    commit(
        &builder,
        "T6: code, its tree's review of T5's stub",
        &[
            ("rust/six.rs", "fn six() {}\n"),
            (REVIEW, &record(STUB, "BLOCKED")),
        ],
    );
    commit(
        &root,
        "T5 filled and reviewed",
        &[(PLAN, &plan(FILLED)), (REVIEW, &record(FILLED, "CLEAR"))],
    );
    let (code, out, err) = carried(&root, &builder);
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    let got: Value =
        serde_json::from_str(&std::fs::read_to_string(root.join(REVIEW)).unwrap()).unwrap();
    assert_eq!(got["blocks"][KEY]["verdict"], "CLEAR", "{out}");
    assert_eq!(
        std::fs::read_to_string(root.join(PLAN)).unwrap(),
        plan(FILLED)
    );
}

#[test]
fn a_plan_both_sides_changed_is_merged_first_and_its_text_decides_the_record() {
    // the builder adds T6's section after T5's stub as the clone fills it: plan.md stops too, merged by section in the same pass,
    // each side's verdict on T5's block as that side's plan held it (a blank line before the next heading)
    let (_dir, root, builder) = trees("carry-record-both");
    commit(&root, "the stub", &[(PLAN, &plan(STUB))]);
    git(&builder, &["merge", "-q", "--ff-only", "main"]);
    let six = "### T6 (six)\n\n- **Approach**: six.\n";
    commit(
        &builder,
        "T6",
        &[
            ("rust/six.rs", "fn six() {}\n"),
            (PLAN, &format!("{}\n{six}", plan(STUB))),
            (REVIEW, &record(&format!("{STUB}\n"), "BLOCKED")),
        ],
    );
    commit(
        &root,
        "T5 filled and reviewed",
        &[
            (PLAN, &format!("{}\n", plan(FILLED))),
            (REVIEW, &record(&format!("{FILLED}\n"), "CLEAR")),
        ],
    );
    let (code, out, err) = carried(&root, &builder);
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    assert!(out.contains("plan.md (by section)"), "{out}");
    let got: Value =
        serde_json::from_str(&std::fs::read_to_string(root.join(REVIEW)).unwrap()).unwrap();
    assert_eq!(got["blocks"][KEY]["verdict"], "CLEAR", "{out}");
}
