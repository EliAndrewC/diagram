//! The source archive, as the record build sees it (`record/archive.py`, feature 309; ported by feature 449 T144). The GM, 2026-10-02:
//! download a copy of every source the record cites into the PRIVATE `EliAndrewC/diagram-research`. WHAT IS CITED is derived, never listed:
//! every URL in a registry entry, its comments included, and every URL a footnote links, its comments excluded. THE MANIFEST is one JSON
//! file per URL, `research/archive/<id[:2]>/<id>.json`. A cited URL's id is the guard's `shared::cited_url` (FR-003).

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
pub use l7r_guard::shared::cited_url::{clean, url_id};
use l7r_guard::shared::html_text::escape;
use l7r_guard::shared::py_text::is_space;
use l7r_guard::shared::pyjson::{py_str, truthy};
use serde_json::{Map, Value};

use crate::record::questions::QUESTIONS;
use crate::record::store;
use crate::{drop_all, re, Error, Result, SPACE_CLASS};

/// Where the manifest lives, under the record.
pub const ARCHIVE_DIR: &str = "archive";
/// The FR-012 match of the GM's downloaded files to the keys they copy, beside the manifest.
pub const GM_COPIES: &str = "gm-copies.json";
/// A row's file, sharded by the id's first two hex digits so no directory lists more than a few hundred (the GM, 2026-10-02).
pub const ROW_GLOB: &str = "[0-9a-f][0-9a-f]/[0-9a-f]*.json";
/// The archive repository: PRIVATE, so its links open for the GM and no one else.
pub const REPO: &str = "https://github.com/EliAndrewC/diagram-research";
/// A capture that could not be pushed counts as covered for this long (plan D5: the page cache's week).
pub const PENDING_DAYS: i64 = 7;
/// The outcomes that hold a copy, and every outcome a row can carry (spec FR-001).
pub const ARCHIVED: [&str; 3] = ["archived", "archived-earlier-snapshot", "archived-gm-copy"];
pub const OUTCOMES: [&str; 6] = [
    "archived",
    "archived-earlier-snapshot",
    "archived-gm-copy",
    "partial",
    "unreachable",
    "pending-upload",
];

static COMMENT: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<!--.*?-->"));
static URL: LazyLock<Regex> = LazyLock::new(|| re(&format!(r#"https?://[^{SPACE_CLASS}<>"']+"#)));
static ENTRY_HEAD: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?s)<h3 id="([a-z0-9][a-z0-9-]*)">.*?</h3>"#));

/// Every URL in `markup`, in order and once each - those inside HTML comments only where `comments` is set.
#[must_use]
pub fn urls_in(markup: &str, comments: bool) -> Vec<String> {
    let text = if comments {
        markup.to_owned()
    } else {
        drop_all(&COMMENT, markup)
    };
    let mut out: Vec<String> = Vec::new();
    for m in URL.find_iter(&text).map_while(std::result::Result::ok) {
        let url = clean(m.as_str());
        if !out.contains(&url) {
            out.push(url);
        }
    }
    out
}

/// Who cites one URL: the registry keys and the notes files.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct Cited {
    pub keys: Vec<String>,
    pub notes: Vec<String>,
}

/// Each registry entry's key and body, as `_ENTRY.findall` reads the assembled registry: the body runs past the heading's whitespace to
/// the next `<h3 id=`, `<h2 id=`, `</main>` or, with `to_end`, the end (`sources._ENTRY_BLOCK` stops short of an entry no terminator
/// follows).
pub(crate) fn entry_bodies(registry: &str, to_end: bool) -> Vec<(String, &str)> {
    let mut out = Vec::new();
    let mut pos = 0;
    while let Some(c) = ENTRY_HEAD.captures_from_pos(registry, pos).ok().flatten() {
        let head = c.get(0).map_or(pos..pos, |m| m.start()..m.end());
        let rest = &registry[head.end..];
        let start = head.end + (rest.len() - rest.trim_start_matches(is_space).len());
        let tail = &registry[start..];
        // THE NEAREST TERMINATOR, FOUND IN ONE PASS (feature 449 T146): the minimum of three `find`s scanned to the registry's end for
        // `</main>` on every entry - 8.7 s of `cited` on the real registry (5.5 MB, 3,726 URLs; observed 2026-11-16, method: a timing
        // probe over the archive crate's tests), where the first `<` that opens a terminator ends the entry and costs only its length
        let Some(end) = tail
            .match_indices('<')
            .map(|(i, _)| i)
            .find(|&i| {
                ["<h3 id=", "<h2 id=", "</main>"]
                    .iter()
                    .any(|t| tail[i..].starts_with(t))
            })
            .map(|n| start + n)
            .or(to_end.then_some(registry.len()))
        else {
            break;
        };
        out.push((c[1].to_owned(), &registry[start..end]));
        pos = end;
    }
    out
}

/// The files `glob(<dir>/<pattern>)` finds for a pattern of one `*` in the name, sorted as `sorted(glob(...))`.
fn glob_names(dir: &Path, keep: impl Fn(&str) -> bool) -> Vec<String> {
    let mut out: Vec<String> = std::fs::read_dir(dir)
        .map(|d| {
            d.flatten()
                .map(|e| e.file_name().to_string_lossy().into_owned())
                .filter(|n| !n.starts_with('.') && keep(n))
                .collect()
        })
        .unwrap_or_default();
    out.sort();
    out
}

/// Every URL the record cites (spec FR-001), registry entries first, then the footnotes' own links.
///
/// # Errors
/// The registry's refusal ([`store::registry_html`]).
pub fn cited(research_dir: &Path) -> Result<Vec<(String, Cited)>> {
    let mut out: Vec<(String, Cited)> = Vec::new();
    let mut add = |url: String, key: Option<&str>, note: Option<&str>| {
        let at = if let Some(i) = out.iter().position(|(u, _)| *u == url) {
            i
        } else {
            out.push((url, Cited::default()));
            out.len() - 1
        };
        if let Some(k) = key {
            out[at].1.keys.push(k.to_owned());
        }
        if let Some(n) = note {
            out[at].1.notes.push(n.to_owned());
        }
    };
    let registry = store::registry_html(research_dir)?;
    for (key, body) in entry_bodies(&registry, true) {
        for url in urls_in(body, true) {
            add(url, Some(&key), None);
        }
    }
    let qdir = research_dir.join(QUESTIONS);
    for name in glob_names(&qdir, |n| n.ends_with(".notes.html")) {
        let text = crate::read(&qdir.join(&name)).unwrap_or_default();
        for url in urls_in(&text, false) {
            add(url, None, Some(&name));
        }
    }
    Ok(out)
}

/// A row's file name, as `[0-9a-f]*.json` matches one.
fn row_name(name: &str) -> bool {
    Path::new(name).extension().is_some_and(|e| e == "json")
        && name.starts_with(|c: char| matches!(c, '0'..='9' | 'a'..='f'))
}

/// The manifest: id to row, in file order; empty where the record has no `archive/`.
///
/// # Errors
/// A row that is not JSON (`JSONDecodeError`, the library's words).
pub fn load(research_dir: &Path) -> Result<Map<String, Value>> {
    let root = research_dir.join(ARCHIVE_DIR);
    let mut rows = Map::new();
    for shard in glob_names(&root, |n| {
        n.len() == 2 && n.chars().all(|c| matches!(c, '0'..='9' | 'a'..='f'))
    }) {
        let dir = root.join(&shard);
        if !dir.is_dir() {
            continue;
        }
        for name in glob_names(&dir, row_name) {
            let text = crate::read(&dir.join(&name)).unwrap_or_default();
            let row = crate::json(&text).map_err(|e| Error::new("JSONDecodeError", e))?;
            rows.insert(name[..name.len() - 5].to_owned(), row);
        }
    }
    Ok(rows)
}

/// Days since 1970-01-01 of a civil date.
fn days(y: i64, m: i64, d: i64) -> i64 {
    let y = if m <= 2 { y - 1 } else { y };
    let era = y.div_euclid(400);
    let yoe = y - era * 400;
    let doy = (153 * (m + if m > 2 { -3 } else { 9 }) + 2) / 5 + d - 1;
    era * 146_097 + yoe * 365 + yoe / 4 - yoe / 100 + doy - 719_468
}

/// `date.fromisoformat` of `YYYY-MM-DD`, as days.
fn iso_day(text: &str) -> Result<i64> {
    let bad = || {
        Error::new(
            "ValueError",
            format!(
                "Invalid isoformat string: {}",
                l7r_guard::shared::py_text::repr(text)
            ),
        )
    };
    let parts: Vec<&str> = text.split('-').collect();
    let ok = parts.len() == 3
        && [4, 2, 2]
            .iter()
            .zip(&parts)
            .all(|(n, p)| p.len() == *n && p.bytes().all(|b| b.is_ascii_digit()));
    if !ok {
        return Err(bad());
    }
    let n: Vec<i64> = parts.iter().map(|p| p.parse().unwrap_or(0)).collect();
    let (y, m, d) = (n[0], n[1], n[2]);
    let range = |what: String| Err(Error::new("ValueError", what));
    if y < 1 {
        return range(format!("year must be in 1..9999, not {y}"));
    }
    if !(1..=12).contains(&m) {
        return range(format!("month must be in 1..12, not {m}"));
    }
    let leap = y % 4 == 0 && (y % 100 != 0 || y % 400 == 0);
    let last = [
        31,
        if leap { 29 } else { 28 },
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ][usize::try_from(m - 1).unwrap_or(0)];
    if !(1..=last).contains(&d) {
        return range(format!(
            "day {d} must be in range 1..{last} for month {m} in year {y}"
        ));
    }
    Ok(days(n[0], n[1], n[2]))
}

/// Today's date in UTC, `YYYY-MM-DD`.
#[must_use]
pub fn today_utc() -> String {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| i64::try_from(d.as_secs()).unwrap_or(0));
    let z = secs.div_euclid(86_400) + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z - era * 146_097;
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let day_of_year = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * day_of_year + 2) / 153;
    let d = day_of_year - (153 * mp + 2) / 5 + 1;
    let m = if mp < 10 { mp + 3 } else { mp - 9 };
    let y = yoe + era * 400 + i64::from(m <= 2);
    format!("{y:04}-{m:02}-{d:02}")
}

fn first10(v: &Value) -> String {
    py_str(v).chars().take(10).collect()
}

/// A row answers for its URL: any outcome but a pending upload older than `PENDING_DAYS`; `today` is `YYYY-MM-DD`.
///
/// # Errors
/// A pending row with no capture date, or a date that does not parse.
pub fn covered(row: &Value, today: &str) -> Result<bool> {
    let outcome = row.get("outcome");
    if outcome != Some(&Value::from("pending-upload")) {
        return Ok(outcome
            .and_then(Value::as_str)
            .is_some_and(|o| OUTCOMES.contains(&o)));
    }
    let captured = row
        .get("captured")
        .ok_or_else(|| Error::new("KeyError", "'captured'"))?;
    Ok(iso_day(today)? - iso_day(&first10(captured))? <= PENDING_DAYS)
}

/// One refusal per cited URL with no covering row (spec FR-007), each naming the command that archives it; a record with no `archive/`
/// has nothing to hold it to.
///
/// # Errors
/// The registry's, the manifest's or a row's refusal.
pub fn refusals(research_dir: &Path, today: Option<&str>) -> Result<Vec<String>> {
    if !research_dir.join(ARCHIVE_DIR).is_dir() {
        return Ok(Vec::new());
    }
    let today = today.map_or_else(today_utc, str::to_owned);
    let rows = load(research_dir)?;
    let mut out = Vec::new();
    for (url, who) in cited(research_dir)? {
        let row = rows.get(&url_id(&url));
        let fine = match row {
            Some(r) => covered(r, &today)?,
            None => false,
        };
        if fine {
            continue;
        }
        let place = if who.keys.is_empty() {
            who.notes.join(", ")
        } else {
            who.keys.join(", ")
        };
        let state = row.map_or_else(
            || "no archived copy".to_owned(),
            |r| {
                format!(
                    "its upload pending since {}",
                    r.get("captured").map_or_else(String::new, first10)
                )
            },
        );
        out.push(format!(
            "archive: {url} ({place}) has {state} - `make archive URL='{url}'` archives it (feature 309)"
        ));
    }
    Ok(out)
}

/// Where a row's copy opens in the archive repository.
#[must_use]
pub fn copy_link(row: &Value) -> String {
    format!(
        "{REPO}/tree/main/{}",
        row.get("path").map_or_else(String::new, py_str)
    )
}

/// The archived-copy line under a registry entry's citation line, for every URL the entry cites (spec FR-010): a link to each copy with
/// its capture date, the GM's downloaded copy where there is one, or a note that no copy could be archived; "" where none applies.
#[must_use]
pub fn entry_line(entry: &str, rows: &Map<String, Value>) -> String {
    let mut parts: Vec<String> = Vec::new();
    let mut gm_seen: Vec<String> = Vec::new();
    for url in urls_in(entry, true) {
        let Some(row) = rows.get(&url_id(&url)) else {
            continue;
        };
        let date = row.get("captured").map_or_else(String::new, first10);
        let outcome = row.get("outcome").and_then(Value::as_str).unwrap_or("");
        let holds =
            ARCHIVED.contains(&outcome) || outcome == "partial" || outcome == "pending-upload";
        if holds && row.get("path").is_some_and(truthy) {
            let label = if outcome == "partial" {
                "partial copy"
            } else {
                "copy"
            };
            parts.push(format!(
                r#"<a href="{}" target="_blank" rel="noopener">archived {label}, {date}</a>"#,
                escape(&copy_link(row), true)
            ));
        } else {
            let reason = row
                .get("reason")
                .map_or_else(|| "unreachable".to_owned(), py_str);
            parts.push(format!(
                "no copy could be archived ({}, {date})",
                escape(&reason, true)
            ));
        }
        for gm in row
            .get("gm_copies")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
        {
            let gm = py_str(gm);
            if gm_seen.contains(&gm) {
                continue;
            }
            parts.push(format!(
                r#"<a href="{}/blob/main/{}" target="_blank" rel="noopener">the GM's downloaded copy</a>"#,
                escape(REPO, true),
                escape(&gm, true)
            ));
            gm_seen.push(gm);
        }
    }
    if parts.is_empty() {
        return String::new();
    }
    format!(
        "<p class=\"archived\"><em>Archived:</em> {} (private)</p>\n",
        parts.join("; ")
    )
}

#[cfg(test)]
mod tests;
