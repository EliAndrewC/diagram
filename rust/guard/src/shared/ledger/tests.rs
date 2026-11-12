//! The lint over hand-made tables: every refusal, every disposition and the rows the table reader skips.

use super::{cell, disposed, disposed_since, measured_rows, problems, COLUMNS, MEASURED_HEADING};

const GOOD: &str = "| 2026-10-12 | glyph-check | privy | PASS | reads | nothing | - | fixed | 412 s | 3100k in (2900k cached) / 4.2k out |";

fn table(rows: &[&str]) -> String {
    format!(
        "# Ledger\n\n| an older table | x |\n\n{MEASURED_HEADING}\n\n| date | check | x |\n|---|---|\n| - | - |\n{}\n## Next\n| 2026 | after |\n",
        rows.join("\n")
    )
}

fn row(cells: [&str; 10]) -> Vec<String> {
    cells.iter().map(|c| (*c).to_owned()).collect()
}

#[test]
fn the_rows_under_the_heading_are_read_by_line() {
    let text = table(&[GOOD, "not a row", "|no space |"]);
    let rows = measured_rows(&text);
    assert_eq!(rows.len(), 1);
    assert_eq!(rows[0].0, 10);
    assert_eq!(cell(&rows[0].1, "wall"), "412 s");
    assert_eq!(cell(&rows[0].1, "no such column"), "");
    assert!(measured_rows("| 2026 | x |\n").is_empty());
    assert_eq!(COLUMNS.len(), 10);
    assert!(problems(&text).is_empty());
}

#[test]
fn a_row_short_of_a_cell_is_named_with_what_it_lacks() {
    let text = table(&[
        "| 2026-10-12 | glyph-check | short |",
        "| 2026-10-01 | no-check | s | v | f | odd | maybe | x | ~7 min | lots |",
        "| 2026-10-12 | glyph-check | s | v | f | nothing | - | thought about it | 1 s | it's \"quoted\" |",
    ]);
    let got = problems(&text);
    assert_eq!(got.len(), 7);
    assert!(got[0].starts_with("line 10: 3 cells, the table has 10 (date | check |"));
    assert_eq!(
        got[1],
        "line 11: check 'no-check' is none of the checks this ledger logs"
    );
    assert_eq!(
        got[2],
        "line 11: class 'odd' - one of geometric, judgment, nothing, paperwork"
    );
    assert_eq!(got[3], "line 11: author missed? 'maybe' - yes, no or -");
    assert_eq!(
        got[4],
        "line 11: the cost cells are not `make review-cost AGENT=<id>`'s ('~7 min' | 'lots')"
    );
    assert!(got[5].starts_with("line 12: acted on 'thought about it' - say fixed"));
    assert!(got[6].ends_with("('1 s' | 'it\\'s \"quoted\"')"));
}

#[test]
fn a_rows_disposition_is_read_from_its_words() {
    let r = |finding: &str, verdict: &str, acted: &str| {
        disposed(&row([
            "d", "c", "s", verdict, finding, "k", "-", acted, "w", "t",
        ]))
    };
    assert_eq!(r("-", "PASS", "-"), Some(true));
    assert_eq!(r("a bug", "PASS", ""), Some(false));
    assert_eq!(r("-", "PASS", "left for the GM"), Some(false));
    assert_eq!(r("", "FAIL", "Nothing"), Some(true));
    assert_eq!(r("a bug", "PASS: fine", "nothing"), Some(true));
    assert_eq!(r("a bug", "FAIL", "nothing"), Some(false));
    assert_eq!(r("a bug", "FAIL", "Fixed it"), Some(true));
    assert_eq!(r("a bug", "FAIL", "pondered"), None);
}

#[test]
fn a_reviews_rows_since_its_dispatch_are_all_disposed_or_not() {
    let fixed = "| 2026-10-12 | settlement-review | s | v | f | judgment | no | fixed | 1 s | 1k in (0k cached) / 1.0k out |";
    let held = "| 2026-10-12 | settlement-review | s | v | f | judgment | no | held for the GM | 1 s | 1k in (0k cached) / 1.0k out |";
    let text = table(&[GOOD, held, fixed, "| short |"]);
    assert!(disposed_since(&text, "settlement-review", "2"));
    assert!(!disposed_since(&text, "settlement-review", ""));
    assert!(!disposed_since(&text, "settlement-review", "3"));
    assert!(!disposed_since(&text, "glyph-check", "1"));
    assert!(disposed_since(&text, "glyph-check", "-9"));
    assert!(!disposed_since(&text, "glyph-check", "-1"));
    assert!(!disposed_since(&text, "glyph-check", "x"));
    assert!(!disposed_since(
        &table(&[GOOD, fixed, held]),
        "settlement-review",
        "0"
    ));
}
