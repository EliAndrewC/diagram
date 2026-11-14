//! A plan's sections and blocks, and a typo told from a change.

use super::{
    blocks, decides_nothing, distance, lands_open_appended, stem, task_sections, typo_only,
    wording_only,
};

#[test]
fn typo_scale_rules() {
    assert!(typo_only("a b c d", "a b c d"));
    assert!(!typo_only(
        "teh cat sat on teh mat wiht ahat",
        "the cat sat on the mat with a hat"
    ));
    assert!(typo_only("teh rule", "the rule") && !typo_only("two gates", "ten gates"));
    assert!(!typo_only("wing 2", "wing 3") && !typo_only("the dog", "the cat"));
    assert!(!typo_only("a b", "a b c"));
    assert_eq!(
        (distance("ab", "ba"), distance("kitten", "sitting")),
        (1, 3)
    );
}

#[test]
fn a_task_s_own_heading_wins_its_section_over_a_mention() {
    let plan = "# plan\n\n## T04 to T10 - T48, T47's patch\n\numbrella\n\n## T10 - the split\n\n### T10 Decisions\n\nD74\n\n## T11 - the close\n";
    let sec = task_sections(plan);
    assert!(
        sec["T10"].starts_with("## T10 - the split")
            && sec["T10"].contains("D74")
            && !sec["T10"].contains("umbrella")
    );
    assert!(sec["T04"].starts_with("## T04 to T10"));
    assert!(sec["T48"].starts_with("## T04 to T10") && sec["T11"].starts_with("## T11"));
}

#[test]
fn every_block_a_task_s_own_headings_open_is_its_section() {
    let text = "# plan\n\n## T24, T26 - an umbrella\n\n### T26 Approach (checklist part A)\n\n1. a\n\n### T26 Decisions\n\n- **D1** x\n\n### T26 Approach (re-answered 2026-10-24T13:22Z)\n\n1. b\n\n### T26 Decisions (2026-10-24)\n\n- **D131** y\n\n## T07 - the knot\n\n### T07 Approach (checklist part A)\n\n1. c\n\n### T07 Decisions\n\n- **D126** z\n\n## T08 next\n";
    let secs = task_sections(text);
    let t26 = &secs["T26"];
    assert!(
        t26.contains("part A")
            && t26.contains("**D1**")
            && t26.contains("re-answered")
            && t26.contains("**D131**")
    );
    assert!(
        t26.find("part A") < t26.find("D131")
            && !t26.contains("an umbrella")
            && !t26.contains("T07")
    );
    assert!(
        secs["T07"].starts_with("## T07") && secs["T07"].matches("### T07 Approach").count() == 1
    );
}

#[test]
fn a_repeated_heading_is_numbered_and_the_text_before_the_first_is_the_preamble() {
    let got = blocks("# t\n\n## A\n\nx\n\n## A\n\ny\n");
    let keys: Vec<&str> = got.iter().map(|(k, ..)| k.as_str()).collect();
    assert_eq!(keys, ["preamble", "## A", "## A#2"]);
    assert_eq!(got[0].1, "# t\n\n");
    assert_eq!(blocks("no heading")[0].1, "no heading");
}

#[test]
fn a_wording_only_section() {
    let sec = "## T05 - x\n\n### T05 Decisions\n\n**Wording only.** a comment.\n\n## next\n\n**D1 - elsewhere.** z\n";
    assert!(wording_only(sec));
    assert!(!wording_only(
        "## T05 - x\n\n**Wording only.** not under a Decisions heading\n"
    ));
    assert!(!wording_only(
        "### T05 Decisions\n\n**Wording only.** x\n\n**D10 - a rule.** z\n"
    ));
}

#[test]
fn a_heading_s_stem_and_the_lands_open_line() {
    assert_eq!(
        stem("### T19 Approach (2026-10-31T04:00Z)"),
        "### T19 Approach"
    );
    assert_eq!(
        stem("### T19 Approach (checklist part A)#2"),
        "### T19 Approach"
    );
    let body = "**Lands open**: T02, T03\n";
    assert_eq!(
        lands_open_appended(body, "**Lands open**: T02, T03, T09\n"),
        body
    );
    assert_eq!(
        lands_open_appended(body, "**Lands open**: T03, T02\n"),
        "**Lands open**: T03, T02\n"
    );
    assert_eq!(
        lands_open_appended(body, "**Lands open**: T02\n"),
        "**Lands open**: T02\n"
    );
    assert_eq!(
        lands_open_appended(body, "**Lands open**: T02, T03, T03\n"),
        "**Lands open**: T02, T03, T03\n"
    );
    assert_eq!(lands_open_appended("none", "x"), "x");
}

fn approach(item6: &str, item2: &str, item9: &str) -> String {
    let items = [
        "The goal, in the world.** n/a".to_owned(),
        format!("The constraints.** {item2}"),
        "Where each comes from.** FR-001.".to_owned(),
        "Do they describe the world here?** Yes.".to_owned(),
        "The order.** n/a.".to_owned(),
        format!("The exits.** {item6}"),
        "The search smell.** None.".to_owned(),
        "The budget.** One landing.".to_owned(),
        format!("Done, measured.** {item9}"),
        "Before moving a constant.** n/a.".to_owned(),
        "Before fitting things into room.** n/a.".to_owned(),
    ];
    let numbered: Vec<String> = items
        .iter()
        .enumerate()
        .map(|(i, t)| format!("{}. **{t}", i + 1))
        .collect();
    format!(
        "### T01 Approach (checklist part A)\n\n{}\n",
        numbered.join("\n")
    )
}

#[test]
fn an_approach_block_of_template_wording_and_ids_decides_nothing() {
    let template = super::template_answers()[&6].clone();
    // the wording the approach gate read from `task-add.py`'s source until feature 449 T135, byte for byte
    assert_eq!(
        template,
        format!(
            "Green: <the measurement that lands it>. {}",
            crate::plan::template::RED_EXIT
        )
    );
    let (key, plan) = (
        "### T01 Approach (checklist part A)",
        "**D1 - a rule.** x\n",
    );
    let nine = "Its tests red without D1.";
    assert!(decides_nothing(
        key,
        &approach(&template, "D1; FR-001.", nine),
        plan,
        ""
    ));
    assert!(!decides_nothing(
        key,
        &approach(&template, "D1; the lanes keep 9 ft.", nine),
        plan,
        ""
    ));
    assert!(!decides_nothing(
        key,
        &approach(&template, "D1; FR-001.", "select 9 of the 11 failures."),
        plan,
        ""
    ));
    assert!(!decides_nothing(
        key,
        &approach(
            "Green: landed. Red: the failing tests recorded.",
            "D1; FR-001.",
            nine
        ),
        plan,
        ""
    ));
    assert!(!decides_nothing(
        key,
        &approach(&template, "D7.", nine),
        plan,
        ""
    ));
    assert!(!decides_nothing(
        key,
        "### T01 Approach\n\nno items\n",
        plan,
        ""
    ));
    assert!(decides_nothing(
        key,
        &approach(&template, "D1; FR-001.", "Its tests red without D<n>."),
        plan,
        ""
    ));
    assert!(!decides_nothing("## other", "x", plan, ""));
}
