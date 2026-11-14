//! Feature 238's reader reports parsed as the Python parsed them: both item shapes, the tiers and the markers, the census's refusals,
//! its per-page form, and the shares.

use std::fmt::Write as _;
use std::path::Path;

use l7r_gate_core::record::testkit::put;

use super::{carries_marker, census, confidence, items, page_of, shares, REPORTS, STATED_ITEMS};

fn words(w: &[&str]) -> Vec<String> {
    w.iter().map(|s| (*s).to_owned()).collect()
}

/// A labeled report of `n` items, every third bare and HIGH, the rest marked, one hedged item near the start.
fn labeled(n: usize, caravan: bool) -> String {
    let mut text = String::from(concat!(
        "# Inventory\n\n# rese",
        "arch/water.html - sections\n"
    ));
    for i in 1..=n {
        let (mark, tier) = match i % 3 {
            0 => ("no marker", "HIGH"),
            1 => ("marker: `(unsourced)`", "MEDIUM"),
            _ => ("(unsourced)", "LOW"),
        };
        let (mark, tier) = match i {
            3 if caravan => ("no marker - the Caravan Inn", "MEDIUM-HIGH"),
            6 => ("no marker", "LOW-MEDIUM"),
            _ => (mark, tier),
        };
        let _ = writeln!(text, "**W{i}.** row - {mark} - figure - **{tier}**");
    }
    text
}

fn reports(root: &Path, caravan: bool, stray: bool) {
    for (i, (name, n)) in STATED_ITEMS.iter().enumerate() {
        let mut text = labeled(*n, caravan && i == 3);
        if stray && i == 1 {
            text = text.replacen("**HIGH**", "**HIGH-HIGH**", 1);
        }
        put(root, &format!("{REPORTS}/{name}"), &text);
    }
    std::fs::create_dir_all(root.join("specs/242-cite-the-unfootnoted-assertions")).unwrap();
}

#[test]
fn the_two_shapes_of_item() {
    let blocks = items("intro\n**W1.** a **HIGH**\nmore\n**W2*** b\n**x** not\n");
    assert_eq!(
        blocks,
        ["**W1.** a **HIGH**\nmore", "**W2*** b\n**x** not\n"]
    );
    let numbered = "# p.html\n1. one **HIGH**\n   on\n\n2. two **LOW**\n# head\n3. three\n---\n4. four **MEDIUM**\n";
    assert_eq!(
        items(numbered),
        [
            "1. one **HIGH**    on",
            "2. two **LOW**",
            "4. four **MEDIUM**"
        ]
    );
    assert_eq!(
        items("1. last **LOW**\n   tail"),
        ["1. last **LOW**    tail"]
    );
    assert!(items("").is_empty());
}

#[test]
fn tiers_markers_and_pages() {
    assert_eq!(confidence("**HIGH** x"), "HIGH");
    assert_eq!(confidence("**HIGH-MEDIUM**"), "MEDIUM-HIGH");
    assert_eq!(confidence("**LOW-LOW**"), "LOW-LOW");
    assert_eq!(confidence("**HIGHER** **LOW**"), "LOW");
    assert_eq!(confidence("none"), "unlabeled");
    assert!(!carries_marker("No Marker here, unsourced"));
    assert!(!carries_marker("marker:  none"));
    assert!(!carries_marker("marker: no"));
    assert!(carries_marker("marker: `x`"));
    assert!(carries_marker("x (unsourced)"));
    assert!(carries_marker("this is a guess"));
    assert!(carries_marker("they are a guess"));
    assert!(!carries_marker("plain"));
    assert_eq!(
        page_of(concat!(
            "# /a/rese",
            "arch/cities/x.html\n## b.html - 3\ntext"
        )),
        "b.html"
    );
    assert_eq!(page_of("# no page\n"), "");
}

#[test]
fn the_census_reproduces_the_stated_totals_and_records() {
    let root = crate::checks::scratch("spec-census");
    reports(&root, true, false);
    put(&root, &format!("{REPORTS}/notes.txt"), "**W1.** **HIGH**\n");
    let mut out = String::new();
    assert_eq!(census(&words(&["--record"]), &root, &mut out), Ok(0));
    assert!(out.starts_with("report                                         items  marked  bare\nhomesteads-buildings-and-the-hamlet-pages.md     168     112    56\n"));
    assert!(out.contains("TOTAL                                            695     464   231\n\nbare by the readers' own marker counts (211 marked): 484\n"));
    assert!(out.contains("WORK LIST: 462 to 209 items\n"));
    assert!(out.contains("tiers: HIGH 226, MEDIUM-HIGH 1, MEDIUM 0, LOW-MEDIUM 4, LOW 0\n"));
    assert!(out.contains("hedged with a compound label: 5 of the 695 inventoried, 5 of the 231 bare, at most 4 on the work list"));
    let rec = root.join("specs/242-cite-the-unfootnoted-assertions/measurements.json");
    assert!(out.ends_with(&format!("\nrecorded to {}\n", rec.display())));
    let written: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(&rec).unwrap()).unwrap();
    assert_eq!(written["worklist-high"]["value"], 209);
    assert_eq!(written["marker-classifier-disagreement"]["value"], 253);
    assert_eq!(
        written["inventory-items"]["command"],
        "scripts/gates/l7r-gate.sh measure spec 242 inventory-census --record"
    );
    let mut plain = String::new();
    assert_eq!(census(&[], &root, &mut plain), Ok(0));
    assert!(!plain.contains("recorded to"));
}

#[test]
fn the_census_refuses_what_it_cannot_believe() {
    let root = crate::checks::scratch("spec-census-refuse");
    let mut out = String::new();
    assert_eq!(
        census(&[], &root, &mut out),
        Err("KeyError: 'religion-vegetation-and-urban-features.md'".to_owned())
    );
    reports(&root, false, true);
    let mut out = String::new();
    assert_eq!(census(&[], &root, &mut out), Ok(1));
    assert!(out.ends_with(
        "UNRECOGNIZED confidence tier(s) ['HIGH-HIGH'] - the printed composition would drop them\n"
    ));
    put(
        &root,
        &format!("{REPORTS}/the-city-pages.md"),
        &labeled(5, false),
    );
    let mut out = String::new();
    assert_eq!(census(&[], &root, &mut out), Ok(1));
    assert_eq!(
        out,
        "PARSE DISAGREES with the report's own total: the-city-pages.md 5 != 203\n"
    );
    put(&root, &format!("{REPORTS}/zz.md"), "");
    std::fs::write(root.join(REPORTS).join("bad.md"), b"\xff").unwrap();
    assert!(census(&[], &root, &mut String::new())
        .unwrap_err()
        .starts_with("UnicodeDecodeError"));
}

#[test]
fn bare_items_per_page() {
    let root = crate::checks::scratch("spec-per-page");
    put(
        &root,
        &format!("{REPORTS}/a.md"),
        concat!("# rese", "arch/b.html\n**W1.** x **HIGH**\n**W2.** y (unsourced) **LOW**\n# c.html\n**W3.** z **LOW**\n**W4.** w **LOW**\n"),
    );
    put(&root, &format!("{REPORTS}/b.md"), "**W1.** none **LOW**\n");
    let mut out = String::new();
    assert_eq!(
        census(&words(&["--per-page", "--record"]), &root, &mut out),
        Ok(0)
    );
    assert_eq!(out, "    2  c.html\n    1  b.html\n    1  \n    4  TOTAL\n");
    put(
        &root,
        &format!("{REPORTS}/b.md"),
        "1. short **LOW**\n   joined\n",
    );
    assert_eq!(
        census(&words(&["--per-page"]), &root, &mut String::new()),
        Err("ValueError: substring not found".to_owned())
    );
}

#[test]
fn the_shares_are_derived_and_recorded() {
    let root = crate::checks::scratch("spec-shares");
    let mut out = String::new();
    assert_eq!(
        shares(&[], &root, &mut out),
        Err("ZeroDivisionError: division by zero".to_owned())
    );
    reports(&root, true, false);
    let mut out = String::new();
    assert_eq!(shares(&words(&["--record"]), &root, &mut out), Ok(0));
    assert!(out.starts_with("695 inventoried items, 231 carrying no marker\n  HIGH          226\n  MEDIUM-HIGH     1\n  MEDIUM        232\n"));
    assert!(out.contains("  urban-features-share     14.8%\n  high-share               32.5%\n  high-share-with-hedged   32.7%\n  unmarked-share           33.2%\n"));
    let rec = root.join("specs/238-unfootnoted-assertions-researched/measurements.json");
    assert!(out.ends_with(&format!("\nrecorded to {}\n", rec.display())));
    let written: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(&rec).unwrap()).unwrap();
    assert_eq!(written["high-share"]["value"], 32.5);
    assert_eq!(
        written["urban-features-share"]["note"],
        "urban-features.html's 103 items as a share of all 695"
    );
    let mut plain = String::new();
    assert_eq!(shares(&[], &root, &mut plain), Ok(0));
    assert!(!plain.contains("recorded to"));
    std::fs::write(&rec, "[]").unwrap();
    assert!(shares(&words(&["--record"]), &root, &mut String::new())
        .unwrap_err()
        .starts_with("TypeError"));
}
