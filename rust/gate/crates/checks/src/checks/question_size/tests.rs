//! A question's prose, and the questions a change touches.

use super::super::tests::{based, commit, put, repo};
use super::{changed, cli, cli_with, every, is_question, question_of, size, CAP};

const Q: &str = "research/questions/0001-a-question.html";

#[test]
fn a_question_s_size_is_its_prose_and_a_money_mark_counts_as_its_words() {
    let dir = repo("size");
    put(
        &dir,
        Q,
        "<span class=\"money\" data-amount=\"20\">20 mon</span> and é",
    );
    assert_eq!(size(&dir.join(Q)), "20 mon and é".len());
}

#[test]
fn only_questions_count_and_a_companion_names_its_question() {
    assert!(is_question(Q) && is_question("research/questions/0001-a.drawing.html"));
    assert!(
        !is_question("research/questions/x.html")
            && !is_question("research/sources/0001-a.html")
            && !is_question("research/questions/0001-a.notes.html")
    );
    assert_eq!(
        question_of("research/questions/0001-a.notes.html"),
        "research/questions/0001-a.html"
    );
    assert_eq!(
        question_of("research/questions/0001-a.originals.html"),
        "research/questions/0001-a.html"
    );
    assert_eq!(question_of(Q), Q);
}

#[test]
fn only_a_changed_question_over_the_cap_refuses_and_a_moved_one_changed_nothing() {
    let dir = repo("changed");
    let long = "x".repeat(CAP + 1);
    put(&dir, Q, &long);
    put(&dir, "research/questions/0002-old.html", "y");
    commit(&dir);
    based(&dir);
    assert_eq!(cli(&[], &dir).code, 0);
    put(&dir, "research/questions/0003-moved.html", &long);
    assert_eq!(changed(&dir), Vec::<String>::new());
    put(
        &dir,
        "research/questions/0002-old.html",
        &format!("{long}!"),
    );
    let refused = cli(&[], &dir);
    assert_eq!(refused.code, 1);
    assert!(refused
        .stderr
        .contains("0002-old.html is 20,002 bytes of prose, over the 20,000 cap"));
    put(&dir, "research/questions/0001-a-question.notes.html", "z");
    assert!(changed(&dir).iter().any(|q| q == Q));
}

/// 449 T385: `make static` runs `--all`, so a question over the cap is caught whoever touched it, where the delta check
/// passed 0059 and 0009 over the cap because no change of the day touched them.
#[test]
fn every_question_over_the_cap_refuses_with_all_though_no_change_touched_it() {
    let dir = repo("all");
    put(&dir, Q, &"x".repeat(CAP + 1));
    put(&dir, "research/questions/0002-b.drawing.html", "y");
    commit(&dir);
    based(&dir);
    assert_eq!(cli(&[], &dir).code, 0);
    let refused = cli(&["--all".to_owned()], &dir);
    assert_eq!(refused.code, 1);
    assert!(refused
        .stderr
        .contains("0001-a-question.html is 20,001 bytes of prose, over the 20,000 cap"));
    assert!(refused.stderr.contains("make question-sizes"));
    put(&dir, Q, "x");
    assert_eq!(cli(&["--all".to_owned()], &dir).code, 0);
}

#[test]
fn the_report_is_largest_first_and_every_question_is_found() {
    let dir = repo("report");
    put(&dir, Q, &"x".repeat(CAP + 1));
    put(&dir, "research/questions/0002-b.html", &"x".repeat(CAP + 2));
    put(&dir, "research/questions/0003-c.notes.html", "n");
    assert_eq!(every(&dir).len(), 2);
    let out = cli(&["--report".to_owned()], &dir).stdout;
    assert!(
        out.starts_with(" 20,002  research/questions/0002-b.html\n 20,001  ")
            && out.ends_with("2 question(s) over 20,000 bytes of prose\n")
    );
}

fn real() -> std::path::PathBuf {
    std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../..")
}

/// FR-008's one end-to-end test (ask:449-T167-realtree): every question page of the live research record found, and the first split
/// page under the cap; its time grows with the record, held by SC-003's suite total, not the bar.
#[test]
fn every_question_page_of_the_record_is_found_and_the_cap_admits_the_first_split_under_it() {
    let found = every(&real());
    assert!(found.len() > 400 && found.iter().all(|q| q.starts_with("research/questions/")));
    let split = found
        .iter()
        .find(|q| q.contains("/0115-servants-in-a-samurai-household"))
        .unwrap();
    assert!(size(&real().join(split)) <= CAP);
}

/// A page near the cap, its padding a block with no claim-bearing token, and a block that carries "mostly".
fn near_cap(body: &str) -> String {
    let pad = format!("<p>{}</p>\n", "word ".repeat((CAP - 120) / 5));
    format!("<h2 id=\"q\">Q</h2>\n{pad}{body}\n")
}

const KEPT: &str = "<li><strong>Old weirs.</strong><br>The intake works up to 1590 were mostly small, of timber frames packed with stone.</li>";
const CUT: &str = "<li><strong>Old weirs.</strong><br>The intake works up to 1590 were small.</li>";

/// 451 T184: a size edit that drops a claim-bearing token is refused, naming the split; the escape stands aside on a reason.
#[test]
fn a_size_edit_that_drops_a_claim_is_refused_and_names_the_split() {
    let dir = repo("size-edit");
    put(&dir, Q, &near_cap(KEPT));
    commit(&dir);
    based(&dir);
    put(&dir, Q, &near_cap(CUT));
    let refused = cli_with(&[], &dir, None);
    assert_eq!(refused.code, 1);
    assert!(
        refused.stderr.contains("is a SIZE EDIT") && refused.stderr.contains("qualifier `mostly`")
    );
    assert!(
        refused.stderr.contains("make reserve KIND=question")
            && refused.stderr.contains("size-limits.json")
    );
    assert_eq!(cli_with(&[], &dir, Some("ok")).code, 1);
    let stood = cli_with(&[], &dir, Some("a restated source correction"));
    assert_eq!(stood.code, 0);
    assert!(stood
        .stdout
        .contains("SIZE_EDIT_OK: a restated source correction"));
    assert_eq!(cli(&["--all".to_owned()], &dir).code, 0);
}

#[test]
fn a_split_whose_section_stands_on_the_moved_pointer_s_page_passes_a_plain_link_does_not_and_a_small_page_is_no_size_edit(
) {
    let dir = repo("split");
    put(&dir, Q, &near_cap(KEPT));
    put(&dir, "research/questions/0002-small.html", KEPT);
    commit(&dir);
    based(&dir);
    put(
        &dir,
        Q,
        &near_cap("<p>The old weirs are <a href=\"0003-old-weirs.html\">their own page</a>.</p>"),
    );
    assert_eq!(cli_with(&[], &dir, None).code, 1);
    put(
        &dir,
        "research/questions/0003-old-weirs.html",
        &format!("<h2 id=\"w\">W</h2>\n{KEPT}\n"),
    );
    let plain = cli_with(&[], &dir, None);
    // A plain link is no split's pointer: the triage would owe the moved block as removed.
    assert_eq!(plain.code, 1);
    assert!(plain
        .stderr
        .contains(r#"<a class="moved" href="NNNN-<slug>.html">"#));
    put(
        &dir,
        Q,
        &near_cap(
            "<p>The old weirs are <a class=\"moved\" href=\"0003-old-weirs.html\">their own page</a>.</p>",
        ),
    );
    assert_eq!(cli_with(&[], &dir, None).code, 0);
    put(&dir, "research/questions/0002-small.html", CUT);
    assert_eq!(cli_with(&[], &dir, None).code, 0);
}

#[test]
fn base_names_the_revision_a_delta_run_diffs_against() {
    let dir = repo("base");
    put(&dir, Q, &near_cap(KEPT));
    commit(&dir);
    put(&dir, Q, &near_cap(CUT));
    commit(&dir);
    based(&dir);
    assert_eq!(cli_with(&[], &dir, None).code, 0);
    let args = ["--base".to_owned(), "HEAD~1".to_owned()];
    assert_eq!(cli_with(&args, &dir, None).code, 1);
}

/// 451 T184: a page's own limit is read only with the size-exception check's verdict, and only above the cap.
#[test]
fn a_page_limit_needs_its_verdict_and_raises_the_cap_for_that_page_alone() {
    let dir = repo("limits");
    let big = "x".repeat(CAP + 10);
    put(&dir, Q, &big);
    commit(&dir);
    based(&dir);
    let all = ["--all".to_owned()];
    assert!(cli(&all, &dir).stderr.contains("over the 20,000 cap"));
    let entry = |limit: usize, verdict: &str| {
        format!("{{\"pages\": {{\"{Q}\": {{\"limit\": {limit}, \"date\": \"2026-11-23\", \"verdict\": \"{verdict}\", \"ledger\": \"dev/review-ledger.md row\"}}}}}}")
    };
    put(
        &dir,
        "research/size-limits.json",
        &entry(CAP + 100, "SPLITTABLE"),
    );
    assert!(cli(&all, &dir)
        .stderr
        .contains("carries no size-exception verdict"));
    put(
        &dir,
        "research/size-limits.json",
        &entry(CAP, "INDIVISIBLE - one argument"),
    );
    assert!(cli(&all, &dir)
        .stderr
        .contains("is not above the 20000 cap"));
    put(&dir, "research/size-limits.json", "{");
    assert!(cli(&all, &dir).stderr.contains("does not parse"));
    put(
        &dir,
        "research/size-limits.json",
        &entry(CAP + 5, "INDIVISIBLE - one argument"),
    );
    assert!(cli(&all, &dir)
        .stderr
        .contains("over the 20,005 limit recorded for it"));
    assert!(cli(&["--report".to_owned()], &dir)
        .stdout
        .contains(" 20,010  "));
    put(
        &dir,
        "research/size-limits.json",
        &entry(CAP + 100, "INDIVISIBLE - one argument"),
    );
    assert_eq!(cli(&all, &dir).code, 0);
    assert!(cli(&["--report".to_owned()], &dir)
        .stdout
        .starts_with("0 question(s)"));
}
