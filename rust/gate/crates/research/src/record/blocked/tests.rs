//! Blocked domains and banned citations (feature 449 T144; each expected value `blocked.py`'s on the same record, 2026-11-16).

use super::{banned, blocked, check, domains, patterns, refusals};
use crate::fixture::{put, record};

#[test]
fn a_url_is_blocked_banned_or_neither() {
    let dir = record();
    assert_eq!(domains(&dir).unwrap()[0].matches, "grokipedia.com");
    assert_eq!(
        banned("https://banned.example.org/x", &dir)
            .unwrap()
            .unwrap()
            .approved,
        "2026-10-03: ban it"
    );
    assert!(banned("https://ok.org", &dir).unwrap().is_none());
    assert_eq!(
        blocked("https://www.grokipedia.com/a", &dir)
            .unwrap()
            .unwrap()
            .reason,
        "machine text"
    );
    assert!(check("https://ok.org", "this fetch", &dir).is_ok());
    let e = check("https://grokipedia.com/x", "this fetch", &dir).unwrap_err();
    assert_eq!(e.kind, "Blocked");
    assert_eq!(
        e.message,
        "this fetch refused: https://grokipedia.com/x is on the blocked list (blocked-domains.json: grokipedia.com - machine text; approved 2026-10-02: block it). Find the same fact on another page; a blocked site is never read, cited or recorded."
    );
    assert_eq!(
        refusals(&dir).unwrap(),
        ["banned citation: https://grokipedia.com/page/X (work-grok) is on blocked-domains.json (grokipedia.com - machine text) - cite the fact from another source, or state its absence (feature 312)"]
    );
    put(
        &dir,
        "sources/010-works-cited/0040-ban.html",
        "<h3 id=\"work-ban\"><code>ban</code></h3>\n<p>https://banned.example.org/q</p>\n",
    );
    assert!(refusals(&dir).unwrap()[1].starts_with("banned citation: https://banned.example.org/q (work-ban) is on banned-citations.json (banned\\.example\\.org/ - forbidden)"));
}

#[test]
fn what_the_lists_refuse() {
    let dir = record();
    let place = dir
        .join("banned-citations.json")
        .to_string_lossy()
        .into_owned();
    put(&dir, "banned-citations.json", "{\"patterns\": [{\"pattern\": \"(\", \"reason\": \"r\", \"approved\": {\"date\": \"d\", \"words\": \"w\"}}]}");
    let e = banned("https://x.org", &dir).unwrap_err();
    assert!(
        e.message
            .starts_with(&format!("{place}: pattern '(' does not compile (")),
        "{}",
        e.message
    );
    // a blocked domain answers before the patterns are read
    assert!(banned("https://grokipedia.com/x", &dir).unwrap().is_some());
    put(
        &dir,
        "banned-citations.json",
        "{\"patterns\": [{\"pattern\": \"x\", \"reason\": \"r\"}]}",
    );
    assert_eq!(
        patterns(&dir).unwrap_err().message,
        format!("{place}: {{'pattern': 'x', 'reason': 'r'}} carries no approval - every entry names the GM's approval as \"approved\": {{\"date\": \"YYYY-MM-DD\", \"words\": \"<the GM's words>\"}}")
    );
    put(&dir, "blocked-domains.json", "nope");
    assert_eq!(
        blocked("https://x.org", &dir).unwrap_err().kind,
        "JSONDecodeError"
    );
    assert_eq!(refusals(&dir).unwrap_err().kind, "JSONDecodeError");
    std::fs::remove_dir_all(dir.join("sources")).unwrap();
    assert_eq!(refusals(&dir).unwrap_err().kind, "RecordError");
}
