//! What a script can see before a plan review spends a round on it.

use std::path::Path;

use super::super::tests::{feature_at, run};
use super::{
    gm_quotes_missing, missing_red_exit, plan_refusal, refusal, tasks_without_approach,
    uncited_differential, unlabeled_count, unlabeled_figure, unlabeled_unit_figure,
};
use crate::checks::scratch;

/// The first finding's words, or "": the old form of each rule, which stopped at its first.
fn first(found: Vec<((usize, usize), String)>) -> String {
    found
        .into_iter()
        .next()
        .map_or_else(String::new, |(_, t)| t)
}

/// No block's deferral finding excused (`make plan-delta` with no escape and none recorded).
fn never(_: &str) -> bool {
    false
}

/// Each of `words` is in `told`, each miss naming itself and the whole report.
fn holds(told: &str, words: &[&str]) {
    for w in words {
        assert!(told.contains(w), "{w}: {told}");
    }
}

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
        Vec::<(usize, String)>::new()
    );
    let missing = gm_quotes_missing(bad, request);
    assert_eq!(
        missing,
        [(
            bad.find("we either").unwrap(),
            "we either have or don't need tooling".to_owned()
        )]
    );
}

#[test]
fn an_item_4_figure_whose_sentence_carries_no_measurement_is_refused() {
    let head = "### T05 Approach (checklist part A)\n\n";
    let ok = format!("{head}4. **World.** Yes - measured 2026-10-19 (two warm runs): it took `4.4 s`, round 2 of seed 45, at 01:30Z for T10.\n5. **x.** y\n");
    assert_eq!(first(unlabeled_figure(&ok)), "");
    assert_eq!(
        first(unlabeled_figure(&format!(
            "{head}4. **World.** See `make claims-owed F=385` and `dev/run-log/2026-10/x.json`.\n"
        ))),
        ""
    );
    assert_eq!(
        first(unlabeled_figure(
            &ok.replace("5. **x.**", "Then it took 2.5 h.\n5. **x.**")
        )),
        "Then it took 2.5 h."
    );
    assert_ne!(
        first(unlabeled_figure(&format!(
            "{head}4. **World.** It takes `4.4 s` (measured).\n"
        ))),
        ""
    );
    assert_eq!(
        first(unlabeled_figure(&format!(
            "{head}4. **World.** It takes 19 degrees, m:turn-angle.\n"
        ))),
        ""
    );
    assert_eq!(first(unlabeled_figure("no item four\n")), "");
}

#[test]
fn a_figure_with_a_unit_anywhere_needs_a_label() {
    assert!(first(unlabeled_unit_figure(
        "**D3 - x.** The check takes 48 s on a landing.\n"
    ))
    .contains("takes 48 s"));
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
        assert_eq!(first(unlabeled_unit_figure(labeled)), "", "{labeled}");
    }
    assert!(first(unlabeled_unit_figure(
        "**D1 - x.** Women did 31.6% of farm labor in the East.\n"
    ))
    .contains("31.6%"));
    assert!(first(unlabeled_unit_figure(
        "- **X**: the check covers 47% of the lines.\n"
    ))
    .contains("47%"));
    assert!(first(unlabeled_unit_figure("- one item.\n- the cap is 10 GB.\n")).contains("10 GB"));
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
fn a_bundle_approach_block_covers_every_task_its_heading_lists() {
    let dir = scratch("approach-owed-bundle");
    std::fs::write(
        dir.join("tasks.md"),
        "- [ ] T01 a\n- [ ] T02 b\n- [ ] T03 c\n",
    )
    .unwrap();
    assert_eq!(
        tasks_without_approach(&dir, &format!("# Plan\n\n{}", approach("T01, T02", RED))),
        ["T03"]
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
    let told = plan_refusal(&dir, &text, &[], &never);
    assert!(told.contains("open tasks with no") && told.contains("T02"));
    assert_eq!(
        plan_refusal(&dir, "# p\n", &[("plain\n".to_owned(), 4)], &never),
        ""
    );
    assert!(
        plan_refusal(&dir, "# p\n", &[("It takes 48 s.\n".to_owned(), 4)], &never)
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
        Vec::<(usize, String)>::new()
    );
    assert_eq!(
        gm_quotes_missing("the GM ended here\n\n\"another quote\"\n", request),
        Vec::<(usize, String)>::new()
    );
    assert_eq!(
        gm_quotes_missing("\"the GM\" in a quotation is a mention \"x y\"\n", request),
        Vec::<(usize, String)>::new()
    );
    assert_eq!(
        gm_quotes_missing("the GM: \"...\" and on\n", request),
        Vec::<(usize, String)>::new()
    );
    assert_eq!(
        gm_quotes_missing("the GM: \"zzz\" and \"zzz\"\n", request),
        [(9, "zzz".to_owned())]
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

#[test]
fn a_count_needs_a_label_in_its_sentence() {
    let t145 = "- **Approach**: five ported whole; `sources.py` and `attempts.py` cut to thin forwarders (183, 98 and 57 lines) that the importers call.\n";
    assert!(first(unlabeled_count(t145)).contains("57 lines"));
    assert!(refusal(Path::new("/no/such"), t145).contains("a count whose sentence"));
    assert!(first(unlabeled_count(
        "The differential's 1,261 cases differ in two.\n"
    ))
    .contains("1,261 cases"));
    assert!(first(unlabeled_count(
        "- reads the 110 `.py` files under `l7r/`.\n"
    ))
    .contains("110"));
    for fine in [
        "Forwarders of 198, 98 and 66 lines (observed 2026-11-16, method: `wc -l`).\n",
        "Its 1,261 cases, measured 2026-11-16 (the harness).\n",
        "The 1,261 cases differ in none (`run.sh a. b`, observed 2026-11-16, method: the run).\n",
        "The 1,261 cases (`m:t145-cases`).\n",
        "No file over 1,000 lines; at most 10 keys a write.\n",
        "The review ruled 14 decisions and 11 recipes.\n",
        "The span `wc -l 57 lines` is code.\n",
        "```\n57 lines\n```\n",
        "Task T145 and FR-002 on 2026-11-16.\n",
    ] {
        assert_eq!(first(unlabeled_count(fine)), "", "{fine}");
    }
}

#[test]
fn a_differential_count_cites_the_runners_verify_report() {
    // feature 449 T161: the count a plan reports is the one `make diff-run ... VERIFY=1` wrote
    let hand = "- The differential's 109 cases, 0 differing (observed 2026-11-16, method: `t146/harness/driver.py`, `final/results.jsonl`).\n";
    let told = refusal(Path::new("/no/such"), hand);
    assert!(told.contains("cites no verify report"));
    assert!(told.contains("make diff-run CASES=<cases file> VERIFY=1"));
    assert!(told.contains("109 cases"));
    let incremental = "The differential ran 16 cases (measured 2026-11-16 (`make diff-run`, `t161/cases.diff-run/reports/diff-run-incremental-20261116T120000Z.json`)).\n";
    assert!(first(uncited_differential(incremental)).contains("16 cases"));
    for refused in [
        "FR-002's same outputs over 1,261 `cmd` and `sources` cases.\n",
        "Same outputs on 16 Cases.\n",
        "Two differentials, 3 of 16 cases differing.\n",
    ] {
        assert_ne!(first(uncited_differential(refused)), "", "{refused}");
    }
    let cited = "The differential's 16 cases, 0 differing (measured 2026-11-16 (`make diff-run CASES=t161/cases.json VERIFY=1`, `t161/cases.diff-run/reports/diff-run-verify-20261116T120000Z.json`)).\n";
    // a cited, labeled count passes the whole lint
    assert_eq!(refusal(Path::new("/no/such"), cited), "");
    // and so does the refusal's own example, whose cited command holds a period inside its code span
    let example = told
        .split("as in \"")
        .nth(1)
        .unwrap()
        .split("\";")
        .next()
        .unwrap();
    assert_eq!(
        refusal(
            Path::new("/no/such"),
            &format!("The differential's {example}.\n")
        ),
        ""
    );
    for fine in [
        cited,
        "The differential's cases are the harness's.\n",
        "It has 16 cases, none differing (observed 2026-11-16, method: the suite).\n",
        "The differential (T146) rows of 2026-11-16 differ.\n",
        "```\nthe differential's 16 cases\n```\n",
    ] {
        assert_eq!(first(uncited_differential(fine)), "", "{fine}");
    }
}

/// A plan's files past a megabyte (feature 449, found 2026-11-18): `fancy_regex` gives up a word-boundary pattern's search past a million
/// steps, about one a character on an unanchored search, and the `.flatten()` over the error it repeats without advancing here would
/// spin `make plan-delta` without end once a plan.md and plan-done.md together pass 1,000,000 bytes, as 449's did (its twin in
/// `bundle.rs` spun `make decide`). The scan reads to the end, bounded here so that the test cannot spin.
#[test]
fn an_approach_block_past_a_megabyte_of_plan_done_is_found() {
    let dir = scratch("approach-past-limit");
    std::fs::write(dir.join("tasks.md"), "- [ ] T01 a\n- [ ] T02 b\n").unwrap();
    let filler = "plain words of a finished section\n".repeat(40_000);
    std::fs::write(
        dir.join("plan-done.md"),
        format!("{filler}{}", approach("T02", RED)),
    )
    .unwrap();
    let plan = format!(
        "# Plan\n\n**Approach checklist**: docs/approach-checklist.md\n\n{}",
        approach("T01", RED)
    );
    let at = dir.path().to_path_buf();
    let (tx, rx) = std::sync::mpsc::channel();
    let _scan = std::thread::spawn(move || tx.send(tasks_without_approach(&at, &plan)));
    let owed = rx
        .recv_timeout(std::time::Duration::from_secs(20))
        .expect("the scan spun past its bound");
    assert_eq!(owed, Vec::<String>::new());
}

/// The label's three lookaheads are tried at the sentence's start alone: tried at every position, each running to the sentence's end,
/// an unlabeled sentence cost its length squared in steps (a 20,000-character one past the engine's million), which the lifted step limit
/// would have turned from an error into a crawl.
#[test]
fn the_label_search_is_linear_in_its_sentence() {
    // a sentence near a megabyte: the one-pattern label ran out of fancy_regex's backtracking stack here and answered "no label"
    let long = format!("{}12 lines.", "word ".repeat(240_000));
    assert!(!super::has_label(&long));
    assert!(super::has_label(&format!(
        "{long} measured 2026-11-18 (wc -l)"
    )));
    assert!(super::has_label(&format!("{long} m:t194.lines")));
    assert!(!super::has_label(&format!(
        "{long} measured 2026-11-18 without a method"
    )));
}

/// Feature 451 T25: each rule reports every finding of the section, each by its line, where it stopped at its first.
#[test]
fn every_finding_of_a_rule_is_reported_by_its_line() {
    let section =
        "# s\n\n```\nit takes 9 s\n```\n\nIt takes 48 s.\nIt takes 50 s.\n\n- the cap is 10 GB.\n";
    let told = refusal(Path::new("/no/such"), section);
    assert!(told.starts_with("3 findings - every one"), "{told}");
    holds(&told, &["(1) a figure with a unit"]);
    assert!(!told.contains("(2)"));
    for line in [
        "line 7: It takes 48 s.",
        "line 8: It takes 50 s.",
        "line 10: - the cap is 10 GB.",
    ] {
        assert!(told.contains(line), "{line}: {told}");
    }
    assert!(!told.contains("9 s"));
    assert!(refusal(Path::new("/no/such"), "It takes 48 s.\n").starts_with("1 finding - "));
}

/// The units that surprised authors are stated in the refusal (feature 451 T25), and their verdicts are as they were.
#[test]
fn each_refusal_states_its_unit_and_where_the_label_sits() {
    let none = Path::new("/no/such");
    // the unit figure's clause: a label at the sentence's end does not reach the clause before its `;`
    let clause = "It takes 48 s; the other took 3 h, measured 2026-11-20 (the log).\n";
    let told = refusal(none, clause);
    holds(&told, &["line 1: It takes 48 s;", "The unit: the clause"]);
    // and it is cut inside a code span too, which the message says
    let span = "It takes 48 s by `t.sh a. b`, measured 2026-11-20 (log).\n";
    holds(
        &refusal(none, span),
        &[
            "line 1: It takes 48 s by `t.sh a.",
            "even inside a code span",
        ],
    );
    assert!(!told.contains("3 h"), "{told}");
    // the GM quote's paragraph: a bullet list with no blank line and no full stop is one
    let request = scratch("t25-request");
    std::fs::write(request.join("request.md"), "words\n").unwrap();
    let list = "- the GM ruled it\n- the cap \"a word\" stands\n";
    let told = refusal(&request, list);
    holds(
        &told,
        &["line 2: \"a word\"", "a bullet list with no blank line"],
    );
    assert_eq!(
        refusal(
            &request,
            "- the GM ruled it.\n- the cap \"a word\" stands\n"
        ),
        ""
    );
    // item 4 takes the measured form alone: the observed form, fine elsewhere, is refused there and the refusal says so
    let observed = "### T05 Approach\n\n4. **World.** It took 7 tries (observed 2026-11-20, method: the log).\n";
    let told = refusal(none, observed);
    holds(&told, &["line 3:", "do not pass in item 4"]);
    holds(&told, &["an unindented wrapped line starts a new sentence"]);
    assert_eq!(
        refusal(
            none,
            "It took 7 tries (observed 2026-11-20, method: the log).\n"
        ),
        ""
    );
}

/// A label rule's finding is dropped only where an earlier one found the very same span; a clause inside a longer finding stays.
#[test]
fn a_finding_is_merged_only_where_one_label_clears_both() {
    let none = Path::new("/no/such");
    let same = format!("### T05 Approach\n\n4. **World.** It takes 48 s.\n6. **Exits.** {RED}\n");
    let told = refusal(none, &same);
    assert!(told.starts_with("1 finding"));
    holds(&told, &["Approach item 4"]);
    let clauses = format!(
        "### T05 Approach\n\n4. **World.** It takes 48 s; it took 3 h.\n6. **Exits.** {RED}\n"
    );
    let told = refusal(none, &clauses);
    assert!(told.starts_with("3 findings"), "{told}");
    let clause = "line 3: **World.** It takes 48 s;";
    holds(&told, &["Approach item 4", clause, "line 3: it took 3 h."]);
    let reds = format!(
        "{}\n{}",
        approach("T01", "Green."),
        approach("T02", "Green.")
    );
    let told = refusal(none, &reds);
    holds(&told, &["line 1: T01", "line 8: T02"]);
}

/// A finding is placed by its plan.md line in a section that is one slice of the plan and in one joined from several (feature 451
/// T25), and a fenced block before it moves no line.
#[test]
fn a_finding_is_placed_by_its_plan_line() {
    let dir = scratch("t25-lines");
    let plan = "# p\n\n## T01 a\n\nIt takes 48 s.\n\n## T02 b\n\nIt takes 9 s.\n\n## T01 again\n\n```\nx\n```\n\nIt takes 50 s.\n";
    let sections = super::super::sections::task_sections(plan);
    let joined = &sections["T01"];
    assert!(!plan.contains(joined.as_str()));
    let told = super::decide_refusal(
        plan,
        joined,
        &super::decide_findings(&dir, joined),
        Some("the approach gate's words".to_owned()),
    );
    assert!(told.starts_with("3 findings"), "{told}");
    holds(
        &told,
        &["plan.md:5: It takes 48 s.", "plan.md:17: It takes 50 s."],
    );
    holds(&told, &["(2) the approach gate's words"]);
    assert!(!told.contains("9 s"));
    let told = super::decide_refusal(
        plan,
        &sections["T02"],
        &super::decide_findings(&dir, &sections["T02"]),
        None,
    );
    assert!(told.contains("plan.md:9: It takes 9 s."), "{told}");
    // a line not in the plan keeps the place of the line before it (the first line, line 1); the blank line after is line 2
    assert_eq!(super::plan_lines(plan, "## T03 not here\n"), [1, 2]);
    let delta = plan_refusal(
        &dir,
        plan,
        &[(
            "It takes 9 s.\n".to_owned(),
            plan.find("It takes 9").unwrap(),
        )],
        &never,
    );
    assert!(delta.contains("plan.md:9: It takes 9 s."), "{delta}");
}

/// The item-4 rule reads every item 4 of the section, not only the first (feature 451 T25, the coordinator's fold of T27: a
/// re-answered Approach block's unlabeled figure reached the plan review unrefused).
#[test]
fn a_second_approach_blocks_item_4_is_read_too() {
    let first = "### T05 Approach (checklist part A)\n\n4. **World.** Yes - measured 2026-11-20 (the log): 7 of them.\n";
    let second =
        "### T05 Approach (re-answered 2026-11-20T10:00Z)\n\n4. **World.** The ratio is 9.\n";
    let section = format!("{first}\n{second}");
    let found = unlabeled_figure(&section);
    assert_eq!(found.len(), 1, "{found:?}");
    assert_eq!(found[0].1, "**World.** The ratio is 9.");
    let told = refusal(Path::new("/no/such"), &section);
    holds(
        &told,
        &["Approach item 4", "line 7: **World.** The ratio is 9."],
    );
    // a part B block's item 4 is read; a performance checklist's, which prompts and never gates, is not
    let part_b = "### T05 part B (2026-11-20T11:00Z)\n\n4. **A4 again.** It failed 3 times.\n";
    assert_eq!(unlabeled_figure(part_b).len(), 1);
    let perf = "### T05 Performance checklist (prompts, never a gate)\n\n4. **Growth.** An exponent of 1.2.\n";
    assert_eq!(unlabeled_figure(perf), []);
}

/// A block's deferral findings are dropped where its task is excused, and only there (feature 451 T17, D15); the rule's words and the
/// class fix's are in the report.
#[test]
fn a_blocks_deferral_is_excused_by_its_task() {
    let dir = scratch("t17-excused");
    std::fs::write(dir.join("tasks.md"), "- [ ] T05 a\n").unwrap();
    let block = "## T05 x\n\n**Found and left?**\n- The wells break.\n- Every writer drops a line; fixed here.\n".to_owned();
    let told = plan_refusal(&dir, &block, &[(block.clone(), 0)], &never);
    holds(
        &told,
        &[
            "2 findings",
            "defers a defect without its form",
            "a fix of a class of defect",
            "plan.md:4: [no reason, no task id, no order] - The wells break.",
        ],
    );
    assert_eq!(
        plan_refusal(&dir, &block, &[(block.clone(), 0)], &|t| t == "T05"),
        ""
    );
    let other = block.replace("T05", "T06");
    assert!(!plan_refusal(&dir, &other, &[(other.clone(), 0)], &|t| t == "T05").is_empty());
    let untitled = "plain\n\n**Found and left?** The wells break.\n".to_owned();
    assert!(
        !plan_refusal(&dir, &untitled, &[(untitled.clone(), 0)], &|t| !t
            .is_empty())
        .is_empty()
    );
}

/// A multiple is a figure with a unit, in a heading as in the Approach (feature 449 T203): T202's heading carried "704x its SOUND
/// derived budget" and passed, the heading read and the multiple no figure to any rule.
#[test]
fn a_multiple_needs_a_label_in_a_heading_as_in_the_approach() {
    let none = Path::new("/no/such");
    let t202 = "### T202 (T198: today's placer 704x its SOUND derived budget)\n\n- **Approach**: rebuilt.\n";
    let found = first(unlabeled_unit_figure(t202));
    assert!(found.contains("704x"), "{found}");
    let told = refusal(none, t202);
    holds(&told, &["line 1: ### T202", "a figure with a unit"]);
    let range = first(unlabeled_unit_figure(
        "- **Approach**: 100x-4,400x over its budget.\n",
    ));
    assert!(range.contains("4,400x"), "{range}");
    let item4 = first(unlabeled_figure(
        "### T05 Approach\n\n4. **World.** It ran 704x its budget.\n",
    ));
    assert!(item4.contains("704x"), "{item4}");
    for fine in [
        "### T202 (T198: 704x its budget, measured 2026-11-19 (`make budget-sheets`))\n",
        "### T05 (a stage lands at up to 2x its budget; past 2x, two SOUNDs)\n",
        "### T05 (the 2x rule)\n",
        "### T05 (a 3x3 grid, `0x1F`)\n",
        "```\n# 704x in a fence\n```\n",
    ] {
        assert_eq!(first(unlabeled_unit_figure(fine)), "", "{fine}");
    }
}

/// A count spelled as a word is a figure (feature 449 T203): T209's "moved five captions a few pixels" passed unlabeled.
#[test]
fn a_count_spelled_as_a_word_needs_a_label() {
    let t209 = "- **Approach**: a way's caption now stands the usual gap off its stroke too, which moved five captions a few pixels.\n";
    let found = first(unlabeled_count(t209));
    assert!(found.contains("five captions"), "{found}");
    // item 4's any-number rule names by the words more than it counts by them, so it leaves them to the counted nouns
    let item4 = first(unlabeled_figure(
        "### T05 Approach\n\n4. **World.** Yes: the three checks are the two places.\n",
    ));
    assert_eq!(item4, "");
    let counted = first(unlabeled_count("4. **World.** Six files moved.\n"));
    assert!(counted.contains("Six files"), "{counted}");
    for fine in [
        "It moved five captions (observed 2026-11-19, method: the picture diff).\n",
        "At most ten keys a write.\n",
        "The one caption moved.\n",
        "Fivefold the captions.\n",
    ] {
        assert_eq!(first(unlabeled_count(fine)), "", "{fine}");
    }
}
