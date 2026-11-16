//! The kept pages that are one work with another (feature 449 T147; the scores the Python's formulas give these texts, observed 2026-11-16,
//! method: `uncited.py`'s `body_grams`, `boilerplate` and `overlap` as written, run on the same texts in the interpreter).

use serde_json::json;

use super::*;
use crate::testkit::W;

const NAV: &str = "Site navigation: home about contact search\n";

fn words(head: &str, n: usize) -> String {
    let w: Vec<String> = (0..n).map(|i| format!("{head}{i}")).collect();
    format!("{NAV}{head}\n{}\n", w.join(" "))
}

/// `words("alpha", 400)` with every thirtieth word another.
fn changed() -> String {
    words("alpha", 400)
        .split(' ')
        .enumerate()
        .map(|(i, x)| {
            if i % 30 == 0 {
                format!("zq{i}xw")
            } else {
                x.to_owned()
            }
        })
        .collect::<Vec<_>>()
        .join(" ")
}

fn world(tag: &str) -> W {
    let w = W::new(tag);
    w.put(
        "research/sources/010-works-cited/0050-t-cited.html",
        "<p>https://h.org/c1 and (https://h.org/c2). and https://zh.wikipedia.org/wiki/x</p>",
    );
    w.page("https://h.org/c1", &words("alpha", 400), "fetch");
    w.page("https://h.org/c2", &words("beta", 300), "fetch");
    w.page("https://h.org/k2", &words("alpha", 400), "fetch");
    w.page("https://h.org/k5", &changed(), "fetch");
    w.page("https://other.org/k3", &words("gamma", 300), "fetch");
    w.page("https://other.org/k4", &words("gamma", 300), "fetch");
    let kept: Vec<serde_json::Value> = [
        "https://zh.wikipedia.org/zh-tw/x",
        "https://h.org/k2",
        "https://other.org/k3",
        "https://other.org/k4",
        "https://h.org/k5",
        "https://other.org/k6",
    ]
    .iter()
    .map(|u| json!({"url": norm(u), "raw": u}))
    .collect();
    w.lines(KEPT, &kept);
    w.uncited("0101-k3-entry.html", "<p>https://other.org/k3</p>");
    w.uncited("0100-k4-entry.html", "<p>https://other.org/k4</p>");
    w
}

#[test]
fn grams_fingerprints_and_overlap() {
    assert_eq!(fingerprint(None), "");
    assert_eq!(fingerprint(Some(&"a ".repeat(400))), "");
    let long = "x".repeat(1200);
    assert_eq!(
        fingerprint(Some(&long)),
        l7r_guard::shared::sha1::hex("x".repeat(1000).as_bytes())
    );
    assert_eq!(body_grams(Some("abc")).len(), 0);
    assert_eq!(body_grams(Some("ab  cd")), grams_of("ab cd", 10));
    assert_eq!(body_grams(None).len(), 0);
    let (a, b) = (grams_of("abcdef", 99), grams_of("bcdefg", 99));
    assert!((overlap(&a, &b) - 0.5).abs() < 1e-9);
    assert!(overlap(&a, &Grams::new()).abs() < 1e-9);
    let docs = [&a, &a, &a, &b];
    assert_eq!(boilerplate(&docs), grams_of("bcdef", 99));
    assert!(boilerplate(&[&a, &a, &b]).is_empty());
    let docs = [&a, &a, &a, &a];
    assert_eq!(boilerplate(&docs), a);
}

#[test]
fn the_duplicates_and_why() {
    let w = world("dupes");
    let found = duplicate_works(w.root()).unwrap();
    let shown: Vec<String> = found
        .iter()
        .map(|(r, k, why)| format!("{r} | {k} | {why}"))
        .collect();
    assert_eq!(
        shown,
        [
            "https://zh.wikipedia.org/zh-tw/x | t-cited | same URL or text",
            "https://h.org/k2 | t-cited | similar 1.00",
            "https://other.org/k4 | https://other.org/k3 | same URL or text",
            "https://h.org/k5 | t-cited | similar 0.82",
        ]
    );
    let dry = dedupe(w.root(), true).unwrap();
    assert_eq!(
        dry,
        [
            "https://zh.wikipedia.org/zh-tw/x -> t-cited",
            "https://h.org/k2 -> t-cited (similar 1.00)",
            "k4-entry -> k3-entry",
            "https://h.org/k5 ~ t-cited (similar 0.82 - read both; `make uncited DO=merge KEY= INTO=` if one work)",
        ]
    );
    assert_eq!(w.read(KEPT).lines().count(), 6);
    assert_eq!(dedupe(w.root(), false).unwrap(), dry);
    let kept = w.read(KEPT);
    assert_eq!(kept.lines().count(), 3, "{kept}");
    assert!(!w
        .root()
        .join("research/sources/040-uncited-works/0100-k4-entry.html")
        .exists());
    assert_eq!(w.read(crate::NOT_KEPT).lines().count(), 3);
}

#[test]
fn a_kept_list_that_will_not_read_is_refused() {
    let w = world("dupes-bad");
    w.lines(KEPT, &[json!({"url": "a"})]);
    assert_eq!(duplicate_works(w.root()).unwrap_err().kind, "KeyError");
    w.lines(KEPT, &[json!({"raw": "a"})]);
    assert_eq!(duplicate_works(w.root()).unwrap_err().kind, "KeyError");
    assert!(dedupe(w.root(), true).is_err());
    std::fs::write(
        w.root()
            .join("research/sources/010-works-cited/0040-bad.html"),
        [0xff],
    )
    .unwrap();
    assert!(duplicate_works(w.root()).is_err());
}

#[test]
fn a_merge_or_a_move_that_fails_is_the_dedupes_error() {
    let w = world("dupes-fail");
    // k4's entry names k3's page as its target, whose own entry is gone: the merge has no target
    std::fs::remove_file(
        w.root()
            .join("research/sources/040-uncited-works/0101-k3-entry.html"),
    )
    .unwrap();
    assert_eq!(dedupe(w.root(), false).unwrap_err().kind, "ValueError");
    let w = world("dupes-fail2");
    w.lines(
        KEPT,
        &[
            json!({"url": "h.org/k2", "raw": "https://h.org/k2"}),
            json!({"url": "h.org/k2", "raw": "https://h.org/k2"}),
        ],
    );
    // the second line of one page: its move finds the page already gone from the list
    assert_eq!(dedupe(w.root(), false).unwrap_err().kind, "ValueError");
}
