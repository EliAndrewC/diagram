//! The record's money, on a scratch record.

use std::path::{Path, PathBuf};

use super::{amounts, cli, coin_of, plain};

fn words(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn put(root: &Path, name: &str, text: &str) {
    let path = root.join(name);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn record(tag: &str) -> PathBuf {
    let root = crate::checks::scratch(tag);
    put(
        &root,
        "research/assets/money-conversions.json",
        r#"{"eras": {"edo": {"years": "1600-1650", "units": {"ryo": 1, "koku": 1}}, "none": {"years": "unknown", "units": {}}}}"#,
    );
    root
}

const Q: &str = "research/questions/0001-a.html";

#[test]
fn text_is_plain_with_entities_read_and_macrons_dropped() {
    assert_eq!(
        plain("<b>1 ryō</b>  &amp; 2 shū &#x27;x&#39; &bogus; &frac12 &#xFFFFFFFF; &path"),
        "1 ryo & 2 shu 'x' &bogus; \u{bd} &#xFFFFFFFF; &path"
    );
    assert_eq!(plain("&apos a"), "&apos a");
    assert_eq!(plain("&apos;"), "'");
}

#[test]
fn a_coin_is_its_word_its_chinese_coin_or_the_dollar() {
    assert_eq!(coin_of("$1.50"), "dollar");
    assert_eq!(coin_of("3 taels"), "tael");
    assert_eq!(coin_of("3 cents"), "dollar");
    assert_eq!(coin_of("3 ryo"), "ryo");
}

#[test]
fn an_amount_is_found_with_its_years_and_nearest_era() {
    let root = record("mon-find");
    put(&root, Q, "<!-- 9 ryo --><h1>Head 1620</h1><p>In 1700 it cost 2,000 ryo.</p><p>Then 5 ryo and $3 and 4 foo.</p>");
    let found = amounts(&root);
    let shown: Vec<(&str, Option<i64>, &str)> = found
        .iter()
        .map(|a| (a.text.as_str(), a.gap, a.near.as_str()))
        .collect();
    assert_eq!(
        shown,
        [
            ("5 ryo", Some(0), "edo"),
            ("2,000 ryo", Some(50), "edo"),
            ("$3", None, "")
        ]
    );
    assert!(found[1].context.contains("[[2,000 ryo]]."));
    assert_eq!(found[0].years, [1620]);
}

#[test]
fn a_marked_amount_is_not_owed_and_each_mark_covers_one() {
    let root = record("mon-marked");
    put(
        &root,
        Q,
        r#"<p><span class="money" x="1">3 ryo</span> and 3 ryo in 1610.</p>"#,
    );
    assert_eq!(amounts(&root).len(), 1);
}

#[test]
fn a_bu_after_an_area_is_land_and_a_note_takes_its_citers_years() {
    let root = record("mon-note");
    put(
        &root,
        Q,
        "<p>2 cho 4 tan 15 bu of land.</p><p>the fee was 2 bu.</p>",
    );
    assert_eq!(
        amounts(&root)
            .iter()
            .map(|a| a.text.as_str())
            .collect::<Vec<_>>(),
        ["2 bu"]
    );
    put(
        &root,
        "research/questions/0002-b.html",
        r#"<p data-x="1">in 1630 <a data-note="n1">x</a></p>"#,
    );
    put(
        &root,
        "research/questions/0002-b.notes.html",
        r#"<p data-note="n1">it was 7 ryo</p><p>unkeyed 8 ryo</p>"#,
    );
    put(
        &root,
        "research/questions/0002-b.originals.html",
        "<p>9 ryo</p>",
    );
    put(&root, "research/questions/skip.txt", "<p>9 ryo</p>");
    let all = amounts(&root);
    let noted = all.iter().find(|a| a.text == "7 ryo").unwrap();
    assert_eq!((noted.years.as_slice(), noted.gap), (&[1630][..], Some(0)));
    assert!(all.iter().any(|a| a.text == "8 ryo" && a.years.is_empty()));
    assert!(!all.iter().any(|a| a.text == "9 ryo"));
}

#[test]
fn the_list_the_check_and_the_passed_over() {
    let root = record("mon-cli");
    put(&root, Q, "<p>In 1610 it cost 5 ryo.</p>");
    put(&root, "research/questions/0002-b.html", "<p>6 ryo.</p>");
    let ask = |w: &[&str]| cli(&words(w), &root);
    assert!(ask(&[]).stdout.contains("0 yr from edo"));
    assert!(ask(&[])
        .stdout
        .ends_with("money-candidates: 2 amount(s) owed a decision\n"));
    let check = ask(&["--check"]);
    assert_eq!(check.code, 1);
    assert!(check
        .stderr
        .contains("2 amount(s) neither marked nor named"));
    assert!(ask(&["--stem", "0002"])
        .stdout
        .contains("no year or no era"));
    put(
        &root,
        "specs/413-money-tooltip-on-the-record/backfill.md",
        "- 0001-a | 5 ryo | a reason\n- 0002-b | * | all of them\nnot a row\n",
    );
    assert_eq!(ask(&["--check"]).code, 0);
    let all = ask(&["--all", "--context", "--stem", "0001"]);
    assert!(
        all.stdout
            .contains("| 1610 [passed over]\n    In 1610 it cost [[5 ryo]].\n"),
        "{}",
        all.stdout
    );
}

#[test]
fn a_missing_record_has_nothing_owed() {
    let root = crate::checks::scratch("mon-none");
    assert_eq!(
        cli(&[], &root).stdout,
        "money-candidates: 0 amount(s) owed a decision\n"
    );
}

#[test]
fn the_context_is_at_most_its_two_windows() {
    let root = record("mon-long");
    put(
        &root,
        Q,
        &format!("<p>{} 5 ryo {}</p>", "x".repeat(300), "y".repeat(100)),
    );
    let found = amounts(&root);
    assert_eq!(found[0].context.chars().count(), 240 + 9 + 60);
}
