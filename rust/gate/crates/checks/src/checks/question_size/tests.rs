//! A question's prose, and the questions a change touches.

use super::super::tests::{based, commit, put, repo};
use super::{changed, cli, every, is_question, question_of, size, CAP};

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
