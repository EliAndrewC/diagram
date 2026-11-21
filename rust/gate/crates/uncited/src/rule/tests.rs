//! The rule (feature 449 T147; the URL forms' verdicts `uncited.py`'s, observed 2026-11-16, method: its `SEARCH`, `API`, `_SHELL` and
//! `urlsplit` run on the same URLs in the interpreter; the rest the port's answers on hand-made input, the T147 differential holding them).

use serde_json::json;

use super::*;
use crate::testkit::{long, W};

#[test]
fn a_url_a_fetch_can_be_aimed_at() {
    for (u, want) in [
        ("https://e.org/p", true),
        ("https://user@e.org:80/p", true),
        ("http://[::1]/p", false),
        ("http://[a.b]/p", false),
        ("http://[bad/p", false),
        ("https://localhost/p", false),
        ("https://kotobank.jp/word/${enc}", false),
        ("https://e.org/a b", false),
        ("https://e.org/[^x]", false),
        ("not a url", false),
    ] {
        assert_eq!(wellformed(u), want, "{u}");
    }
    for (u, want) in [
        ("https://duckduckgo.com/?q=x", true),
        ("https://www.google.co.jp/search?q=x", true),
        (
            "https://e.org/w/index.php?search=x&title=Special:Search",
            true,
        ),
        ("https://e.org/wiki/Category:X", true),
        ("https://ja.wikipedia.org/wiki/カテゴリ:X", true),
        ("https://e.org/RESULTS", true),
        ("https://e.org/resultsx", false),
        ("https://e.org/api/v1", true),
        ("https://e.org/data.json", true),
        ("https://e.org/data.jsonl", false),
        ("https://e.org/page", false),
    ] {
        assert_eq!(no_substance(u), want, "{u}");
    }
}

#[test]
fn a_failed_fetchs_access_state() {
    let got = |s: Option<i64>| l7r_gate_archive::fetch::Fetched {
        status: s,
        ..Default::default()
    };
    assert_eq!(
        [401, 402, 403, 406, 429, 451, 404, 410, 500].map(|s| access_of(&got(Some(s)))),
        [
            "paywalled",
            "paywalled",
            "bot-refused",
            "bot-refused",
            "bot-refused",
            "bot-refused",
            "gone",
            "gone",
            "down"
        ]
    );
    assert_eq!(access_of(&got(None)), "down");
    assert_eq!(digest(" a \n b "), l7r_shared::sha256::hex(b"a b"));
}

#[test]
fn the_rule_rules_what_needs_no_agent() {
    let w = W::new("rule");
    // a cited page's saved text, and two set pages saving the same body
    w.page("https://e.org/a", "the cited body", "fetch");
    w.page("https://x.org/same-as-cited", " the  cited\nbody ", "fetch");
    w.page("https://x.org/one", &long("one body", 5), "fetch");
    w.page("https://x.org/two", &long("one body", 5), "fetch");
    w.page("https://x.org/blank", "   ", "fetch");
    let urls: Vec<String> = [
        "https://x.org/search?q=1",
        "https://x.org/${u}",
        "https://x.org/no-text",
        "https://x.org/blank",
        "https://x.org/same-as-cited",
        "https://x.org/one",
        "https://x.org/two",
    ]
    .iter()
    .map(|u| (*u).to_owned())
    .collect();
    assert_eq!(
        rule(w.root(), &urls).unwrap(),
        json!({"no-substance": 1, "duplicate": 2})
    );
    let lines: Vec<serde_json::Value> = w
        .read(NOT_KEPT_PATH)
        .lines()
        .map(|l| serde_json::from_str(l).unwrap())
        .collect();
    let notes: Vec<&str> = lines.iter().map(|l| l["note"].as_str().unwrap()).collect();
    assert_eq!(
        notes,
        [
            "a search, listing, API or raw URL",
            "a malformed URL no route can fetch (a fragment, or a shell variable)",
            "the same text as a cited page",
            "the same text as https://x.org/one"
        ]
    );
    assert_eq!(lines[1]["access"], "gone");
    assert!(needs_fetch(w.home(), "https://x.org/no-text").unwrap());
    assert!(needs_fetch(w.home(), "https://x.org/one").unwrap());
    w.page("https://x.org/long", &long("x", 200), "fetch");
    assert!(!needs_fetch(w.home(), "https://x.org/long").unwrap());
    let bad = l7r_gate_research::pages::entry_dir(w.home(), "https://x.org/one").join("text.txt");
    std::fs::write(&bad, [0xff]).unwrap();
    assert!(needs_fetch(w.home(), "https://x.org/one").is_err());
    assert!(rule(w.root(), &["https://x.org/one".to_owned()]).is_err());
    std::fs::write(
        w.root()
            .join("research/sources/010-works-cited/0040-bad.html"),
        [0xff],
    )
    .unwrap();
    assert!(rule(w.root(), &[]).is_err());
}

const NOT_KEPT_PATH: &str = crate::NOT_KEPT;
