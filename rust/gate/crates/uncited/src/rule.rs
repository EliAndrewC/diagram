//! THE RULE (feature 312 FR-007): the verdicts that need no judgment, with no agent - a search, listing, API or raw URL (`no-substance`);
//! a page whose text is the same as one already judged or cited (`duplicate`); a URL no route can fetch (`unreadable`).

use std::collections::{HashMap, HashSet};
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_archive::fetch::Fetched;
use l7r_shared::consulted;
use serde_json::json;

use crate::lists::{line, not_kept};
use crate::set::registry_norms;
use crate::{py, squeeze, strip, text_of, Result, SHELL_CHARS};

/// The no-substance rule: `prep.md`'s two regexes, measured over the ledger 2026-10-02, and the forms the plan review found they missed -
/// 44 `MediaWiki` search pages (`index.php?search=...&title=Special:...`) and a wiki category listing.
static SEARCH: LazyLock<Regex> = LazyLock::new(|| {
    py(concat!(
        r"(?i)duckduckgo|google\.[a-z.]+/search|bing\.com/search|baidu\.com/s\?|search\?|/search/|advancedsearch",
        r"|[?&](q|query|keyword|kw|wd|search)=|/results?\b|/wiki/(?:Category|Special|特別|特殊|Kategorie):|/wiki/カテゴリ:|/wiki/Category%3A"
    ))
});
static API: LazyLock<Regex> =
    LazyLock::new(|| py(r"(?i)/api/|api\.php|action=raw|output=json|\.json\b"));
/// Not a URL at all: a shell fragment the ledger's seed took from a command line (`https://kotobank.jp/word/${enc}`, `...?title=$(python3`,
/// `.../wiki/$u`, a regex `[^` - observed 2026-10-02).
static SHELL: LazyLock<Regex> = LazyLock::new(|| py(r"[$`{}\s]|\[\^"));

/// A URL a fetch can be aimed at: it parses, has a dotted host, and is no shell fragment.
#[must_use]
pub fn wellformed(url: &str) -> bool {
    let Ok(parts) = l7r_gate_research::verbatim::fetch::urlsplit(url) else {
        return false;
    };
    // `.hostname`: the netloc after its last `@`, the bracketed host's inside or the part before the port
    let info = parts[1]
        .rsplit_once('@')
        .map_or(parts[1].as_str(), |(_, h)| h);
    let host = match info.split_once('[') {
        Some((_, rest)) => rest.split(']').next().unwrap_or_default(),
        None => info.split(':').next().unwrap_or_default(),
    };
    host.contains('.') && !SHELL.is_match(url).unwrap_or(false)
}

/// A search, listing, API or raw URL.
#[must_use]
pub fn no_substance(url: &str) -> bool {
    SEARCH.is_match(url).unwrap_or(false) || API.is_match(url).unwrap_or(false)
}

/// A failed fetch's access state (feature 313's vocabulary).
#[must_use]
pub fn access_of(got: &Fetched) -> &'static str {
    match got.status {
        Some(401 | 402) => "paywalled",
        Some(403 | 406 | 429 | 451) => "bot-refused",
        Some(404 | 410) => "gone",
        _ => "down",
    }
}

/// `sha256` of a text, its whitespace squeezed and stripped.
#[must_use]
pub fn digest(text: &str) -> String {
    l7r_shared::sha256::hex(strip(&squeeze(text)).as_bytes())
}

/// The verdicts no agent is needed for: no-substance by URL; duplicate by the text of a cited page or of a page earlier in the set.
/// Returns the counts `make uncited DO=rule` prints.
///
/// # Errors
/// The registry, the cache or the not-kept list.
pub fn rule(root: &Path, urls: &[String]) -> Result<serde_json::Value> {
    let home = consulted::home(root);
    let mut cited = HashSet::new();
    for u in registry_norms(root)? {
        if let Some(t) = text_of(&home, &format!("https://{u}"))?.filter(|t| !t.is_empty()) {
            cited.insert(digest(&t));
        }
    }
    let mut seen: HashMap<String, String> = HashMap::new();
    let mut out = Vec::new();
    let (mut substance, mut duplicate) = (0, 0);
    for u in urls {
        if no_substance(u) {
            out.push(line(
                u,
                &["no-substance".to_owned()],
                "rule",
                "a search, listing, API or raw URL",
                "",
            )?);
            substance += 1;
            continue;
        }
        if !wellformed(u) {
            out.push(line(
                u,
                &["unreadable".to_owned()],
                "rule",
                "a malformed URL no route can fetch (a fragment, or a shell variable)",
                "gone",
            )?);
            continue;
        }
        let Some(t) = text_of(&home, u)?.filter(|t| !strip(t).is_empty()) else {
            continue;
        };
        let d = digest(&t);
        if cited.contains(&d) {
            out.push(line(
                u,
                &["duplicate".to_owned()],
                "rule",
                "the same text as a cited page",
                "",
            )?);
            duplicate += 1;
        } else if let Some(first) = seen.get(&d) {
            out.push(line(
                u,
                &["duplicate".to_owned()],
                "rule",
                &format!("the same text as {first}"),
                "",
            )?);
            duplicate += 1;
        } else {
            seen.insert(d, u.clone());
        }
    }
    not_kept(root, &out)?;
    Ok(json!({"no-substance": substance, "duplicate": duplicate}))
}

/// No saved text, or a shell of one.
///
/// # Errors
/// The cache's read.
pub fn needs_fetch(home: &Path, url: &str) -> Result<bool> {
    Ok(text_of(home, url)?.is_none_or(|t| crate::chars(strip(&t)) < SHELL_CHARS))
}

#[cfg(test)]
mod tests;
