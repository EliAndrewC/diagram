//! What a script can see before a plan review spends a round on it.

use std::path::Path;

use super::super::tests::{feature_at, run};
use super::{
    gm_quotes_missing, missing_red_exit, plan_refusal, refusal, tasks_without_approach,
    unlabeled_figure, unlabeled_unit_figure,
};
use crate::checks::scratch;

const RED: &str = "Green: landed. Red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.";

fn approach(task: &str, item6: &str) -> String {
    format!("### {task} Approach (checklist part A)\n\n1. **The goal, in the world.** n/a\n2. **The constraints.** D1; FR-001.\n6. **The exits.** {item6}\n7. **The search smell.** None.\n")
}

#[test]
fn a_section_quoting_the_gm_with_words_not_in_the_request_is_refused() {
    let request = "> Please make sure to implement any obvious performance / tooling / process improvements along the way.\n";
    let ok = "The GM, 2026-10-18: \"implement any obvious ... tooling ... improvements\"; done.\n";
    let bad = "As the GM's words have it: \"we either have or don't need tooling\". And \"this\" is no attribution.\n";
    let mention = "a `\"the GM\"` mention, and WHY=\"awaiting the GM on it\" - no quote of his.\n";
    assert_eq!(
        gm_quotes_missing(&format!("{ok}{mention}"), request),
        Vec::<String>::new()
    );
    let missing = gm_quotes_missing(bad, request);
    assert_eq!(missing, ["we either have or don't need tooling"]);
}

#[test]
fn an_item_4_figure_whose_sentence_carries_no_measurement_is_refused() {
    let head = "### T05 Approach (checklist part A)\n\n";
    let ok = format!("{head}4. **World.** Yes - measured 2026-10-19 (two warm runs): it took `4.4 s`, round 2 of seed 45, at 01:30Z for T10.\n5. **x.** y\n");
    assert_eq!(unlabeled_figure(&ok), "");
    assert_eq!(
        unlabeled_figure(&format!(
            "{head}4. **World.** See `make claims-owed F=385` and `dev/run-log/2026-10/x.json`.\n"
        )),
        ""
    );
    assert_eq!(
        unlabeled_figure(&ok.replace("5. **x.**", "Then it took 2.5 h.\n5. **x.**")),
        "Then it took 2.5 h."
    );
    assert_ne!(
        unlabeled_figure(&format!(
            "{head}4. **World.** It takes `4.4 s` (measured).\n"
        )),
        ""
    );
    assert_eq!(
        unlabeled_figure(&format!(
            "{head}4. **World.** It takes 19 degrees, m:turn-angle.\n"
        )),
        ""
    );
    assert_eq!(unlabeled_figure("no item four\n"), "");
}

#[test]
fn a_figure_with_a_unit_anywhere_needs_a_label() {
    assert!(
        unlabeled_unit_figure("**D3 - x.** The check takes 48 s on a landing.\n")
            .contains("takes 48 s")
    );
    for labeled in [
        "**D3 - x.** It takes 48 s, measured 2026-10-24 (feature 415 T03).\n",
        "**D3 - x.** It takes 48 s (observed 2026-10-24, method: the run log).\n",
        "**D3 - x.** It takes 48 s (`m:cover-time`).\n",
        "**D3 - x.** Run `sleep 48 s` in a span.\n",
        "**D1 - x.** Women did 31.6% of farm labor in the East, ATTESTED ONLY FOR 1921-25.\n",
        "**D1 - x.** A tan is 0.35 x 11 m, so 3.9 m2, this project's arithmetic.\n",
        "- **X**: ruff, 100% coverage of the new module the day it lands.\n",
        "**D1 - x.** The default, observed 2026-10-26, method: the memory watch, read the shared cap at\n9.3 of 10 GB.\n",
        "```\nit takes 48 s\n```\n",
    ] {
        assert_eq!(unlabeled_unit_figure(labeled), "", "{labeled}");
    }
    assert!(
        unlabeled_unit_figure("**D1 - x.** Women did 31.6% of farm labor in the East.\n")
            .contains("31.6%")
    );
    assert!(unlabeled_unit_figure("- **X**: the check covers 47% of the lines.\n").contains("47%"));
    assert!(unlabeled_unit_figure("- one item.\n- the cap is 10 GB.\n").contains("10 GB"));
}

#[test]
fn an_approach_block_without_the_red_exit_is_refused() {
    assert_eq!(missing_red_exit(&approach("T01", RED)), "");
    assert_eq!(missing_red_exit(&approach("T01", "Green: landed.")), "T01");
    assert_eq!(
        missing_red_exit("### T01 Approach\n\n1. no item six\n"),
        "T01"
    );
    assert!(
        refusal(Path::new("/no/such"), &approach("T01", "Green: landed."))
            .contains("make arbiter-ask")
    );
    assert_eq!(missing_red_exit(&approach("T01", "Green: landed. Red: rebuilt again, or raised with the GM's words (`make budget-change`).")), "");
}

#[test]
fn each_open_task_owes_an_approach_block_once_the_plan_holds_one() {
    let dir = scratch("approach-owed");
    std::fs::write(
        dir.join("tasks.md"),
        "- [ ] T01 a\n- [ ] T02 b\n- [x] T03 c\n",
    )
    .unwrap();
    assert_eq!(
        tasks_without_approach(&dir, &format!("# Plan\n\n{}", approach("T01", RED))),
        ["T02"]
    );
    assert_eq!(
        tasks_without_approach(&dir, "# Plan\n\n## Decisions\n"),
        Vec::<String>::new()
    );
    assert_eq!(
        tasks_without_approach(
            &dir,
            "# Plan\n\n**Approach checklist**: docs/approach-checklist.md\n"
        ),
        ["T01", "T02"]
    );
}

#[test]
fn plan_delta_writes_no_bundle_while_a_block_refuses() {
    let root = scratch("plan-delta-lint");
    let plan = format!(
        "# Plan\n\n## Decisions\n\n**D1 - x.** The check takes 48 s on a landing.\n\n{}",
        approach("T01", RED)
    );
    let dir = feature_at(&root, Some(&plan), None, "999-x");
    std::fs::write(dir.join("tasks.md"), "- [ ] T01 a\n").unwrap();
    let got = run(&root, &["delta", "999"]);
    assert_eq!(got.code, 1);
    assert!(got.stderr.contains("no bundle written") && got.stderr.contains("48 s"));
}

#[test]
fn each_refusal_is_named_in_its_own_words() {
    let dir = scratch("refusals");
    std::fs::write(dir.join("request.md"), "words\n").unwrap();
    assert!(refusal(&dir, "the GM said \"nothing like this\".\n").contains("add the GM's words"));
    assert!(refusal(&dir, "4. **World.** It takes 19 degrees.\n").contains("Approach item 4"));
    assert!(refusal(&dir, "It takes 48 s.\n").contains("a figure with a unit"));
    assert_eq!(refusal(&dir, "plain\n"), "");
    std::fs::write(dir.join("tasks.md"), "- [ ] T02 b\n").unwrap();
    let text = format!("# p\n\n{}", approach("T01", RED));
    let told = plan_refusal(&dir, &text, &[]);
    assert!(told.contains("open tasks with no") && told.contains("T02"));
    assert_eq!(plan_refusal(&dir, "# p\n", &["plain\n".to_owned()]), "");
    assert!(
        plan_refusal(&dir, "# p\n", &["It takes 48 s.\n".to_owned()])
            .contains("a figure with a unit")
    );
}

#[test]
fn a_quote_read_across_a_sentence_end_stops_there() {
    let request = "one two three\n";
    assert_eq!(
        gm_quotes_missing(
            "the GM ended here. Then \"another quote\" stands.\n",
            request
        ),
        Vec::<String>::new()
    );
    assert_eq!(
        gm_quotes_missing("the GM ended here\n\n\"another quote\"\n", request),
        Vec::<String>::new()
    );
    assert_eq!(
        gm_quotes_missing("\"the GM\" in a quotation is a mention \"x y\"\n", request),
        Vec::<String>::new()
    );
    assert_eq!(
        gm_quotes_missing("the GM: \"...\" and on\n", request),
        Vec::<String>::new()
    );
    assert_eq!(
        gm_quotes_missing("the GM: \"zzz\" and \"zzz\"\n", request),
        ["zzz"]
    );
}

#[test]
fn an_approach_block_ends_at_the_next_heading() {
    let text = format!(
        "{}\n## Next\n\n6. make arbiter-ask\n",
        approach("T01", "Green: landed.")
    );
    assert_eq!(missing_red_exit(&text), "T01");
}
