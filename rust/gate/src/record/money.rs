//! Every amount of money in the record a built era could convert, and whether it is marked (feature 413, plan D6; feature 449 T79, from `money_candidates.py`).
//!
//! Every amount listed is owed a decision: marked, or named in the feature's `backfill.md` with the reason it is passed over. The order decides nothing: the GM
//! withdrew the 25-year default (#14, 2026-10-24).

use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};
use serde_json::Value;

use super::reply;
use crate::Reply;
use l7r_guard::shared::html_text::unescape;

const QUESTIONS: &str = "research/questions";
const TABLE: &str = "research/assets/money-conversions.json";
const BACKFILL: &str = "specs/413-money-tooltip-on-the-record/backfill.md";
/// The period's other Japanese coin words, listed whether or not a built era's row has a unit for them (the plan review of 2026-10-24).
const COINS_ALSO: [&str; 10] = [
    "mon", "monme", "kanmon", "ryo", "bu", "shu", "koban", "yen", "sen", "rin",
];
/// Each Chinese coin word the scanner finds, and the coin it is marked in.
const CHINA_WORDS: [(&str, &str); 15] = [
    ("tael", "tael"),
    ("taels", "tael"),
    ("mace", "tael"),
    ("candareen", "tael"),
    ("candareens", "tael"),
    ("cash", "cash"),
    ("wen", "cash"),
    ("string", "cash"),
    ("strings", "cash"),
    ("guan", "cash"),
    ("tiao", "cash"),
    ("diao", "cash"),
    ("dollar", "dollar"),
    ("dollars", "dollar"),
    ("cent", "dollar"),
];
const CENTS: (&str, &str) = ("cents", "dollar");
const NUMBER: &str = r"\d[\d,]*(?:\.\d+)?(?:\s*-\s*\d[\d,]*(?:\.\d+)?)?";
const DOLLAR: &str = r"\d[\d,]*(?:\.\d+)?(?:\s*-\s*\$?\d[\d,]*(?:\.\d+)?)?";
fn compiled(p: &str) -> Regex {
    Regex::new(p).unwrap_or_else(|e| unreachable!("{e}"))
}

static MACRON: LazyLock<Regex> = LazyLock::new(|| compiled(r"\b(?:ryō|shū)(?![\w])"));
static COMMENT: LazyLock<Regex> = LazyLock::new(|| compiled(r"(?s)<!--.*?-->"));
static BLOCK: LazyLock<Regex> = LazyLock::new(|| {
    compiled(
        r"(?s)<(p|li|blockquote|td|dd|h[1-4])\b([^>]*)>(.*?)(?:</\1>|(?=<(?:p|li|blockquote|td|dd|h[1-4])\b)|\z)",
    )
});
static HEADING: LazyLock<Regex> = LazyLock::new(|| compiled(r"(?s)<h[12][^>]*>(.*?)</h[12]>"));
static TAG: LazyLock<Regex> = LazyLock::new(|| compiled(r"<[^>]+>"));
static MARKED: LazyLock<Regex> =
    LazyLock::new(|| compiled(r#"(?s)<span class="money"[^>]*>(.*?)</span>"#));
static YEAR: LazyLock<Regex> = LazyLock::new(|| compiled(r"(?<!\d)(1[0-9]{3})(?!\d)"));
static NOTE_MARK: LazyLock<Regex> = LazyLock::new(|| compiled(r#"data-note="([^"]+)""#));
static AREA_BEFORE: LazyLock<Regex> = LazyLock::new(|| compiled(r"\d\s+(?:cho|chō|tan|se)\s+$"));
static ROW: LazyLock<Regex> =
    LazyLock::new(|| compiled(r"^-\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*$"));
static SPACES: LazyLock<Regex> = LazyLock::new(|| compiled(r"\s+"));

fn plain(markup: &str) -> String {
    let bare = TAG.replace_all(markup, "");
    let text = unescape(&bare);
    let flat = SPACES.replace_all(&text, " ");
    MACRON
        .replace_all(flat.trim(), |c: &Captures| {
            c[0].replace('ō', "o").replace('ū', "u")
        })
        .into_owned()
}

fn years_in(text: &str) -> Vec<i64> {
    YEAR.captures_iter(text)
        .flatten()
        .filter_map(|c| c[1].parse().ok())
        .collect()
}

/// `{era id: (first year, last year, its coins)}`.
fn eras(root: &Path) -> BTreeMap<String, (i64, i64, BTreeSet<String>)> {
    let table: Value = std::fs::read_to_string(root.join(TABLE))
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok())
        .unwrap_or(Value::Null);
    let mut out = BTreeMap::new();
    for (id, row) in table["eras"].as_object().into_iter().flatten() {
        let ys = years_in(row["years"].as_str().unwrap_or(""));
        if let (Some(lo), Some(hi)) = (ys.iter().min(), ys.iter().max()) {
            let units = row["units"]
                .as_object()
                .into_iter()
                .flatten()
                .map(|(k, _)| k.clone())
                .collect();
            out.insert(id.clone(), (*lo, *hi, units));
        }
    }
    out
}

fn no_comments(text: &str) -> String {
    COMMENT.replace_all(text, "").into_owned()
}

/// `{note key: the years named by the body blocks of the page that cite it}`.
fn cited_years(page: &Path) -> HashMap<String, Vec<i64>> {
    let text = no_comments(&std::fs::read_to_string(page).unwrap_or_default());
    let mut out: HashMap<String, Vec<i64>> = HashMap::new();
    for block in BLOCK.captures_iter(&text).flatten() {
        let years = years_in(&plain(&block[3]));
        for key in NOTE_MARK.captures_iter(&block[3]).flatten() {
            out.entry(key[1].to_owned()).or_default().extend(&years);
        }
    }
    out
}

/// One unmarked amount.
#[derive(Debug, PartialEq, Eq, Clone)]
pub(crate) struct Amount {
    stem: String,
    text: String,
    years: Vec<i64>,
    near: String,
    gap: Option<i64>,
    context: String,
}

fn coin_of(found: &str) -> String {
    if found.starts_with('$') {
        return "dollar".to_owned();
    }
    let word = found.rsplit(char::is_whitespace).next().unwrap_or(found);
    CHINA_WORDS
        .iter()
        .chain([&CENTS])
        .find(|(w, _)| *w == word)
        .map_or(word, |(_, c)| c)
        .to_owned()
}

fn amount_pattern(known: &BTreeMap<String, (i64, i64, BTreeSet<String>)>) -> Regex {
    let mut coins: BTreeSet<String> = COINS_ALSO.iter().map(|c| (*c).to_owned()).collect();
    coins.extend(
        CHINA_WORDS
            .iter()
            .chain([&CENTS])
            .map(|(w, _)| (*w).to_owned()),
    );
    coins.extend(known.values().flat_map(|e| e.2.iter().cloned()));
    let mut list: Vec<String> = coins.into_iter().collect();
    list.sort_by_key(|c| std::cmp::Reverse(c.chars().count()));
    let joined: Vec<String> = list
        .iter()
        .map(|c| fancy_regex::escape(c).into_owned())
        .collect();
    compiled(&format!(
        r"(?<![\w.]){NUMBER}\s+(?:{})(?![\w])|(?<![\w$])\${DOLLAR}",
        joined.join("|")
    ))
}

/// Characters of `text` before byte `at`, at most `n` of them, as a slice.
fn before(text: &str, at: usize, n: usize) -> &str {
    let start = text[..at]
        .char_indices()
        .rev()
        .nth(n - 1)
        .map_or(0, |(i, _)| i);
    &text[start..at]
}

fn after(text: &str, at: usize, n: usize) -> &str {
    let end = text[at..]
        .char_indices()
        .nth(n)
        .map_or(text.len(), |(i, _)| at + i);
    &text[at..end]
}

/// One fragment's unmarked amounts.
fn scan(
    name: &str,
    folder: &Path,
    pattern: &Regex,
    known: &BTreeMap<String, (i64, i64, BTreeSet<String>)>,
) -> Vec<Amount> {
    let text = no_comments(&std::fs::read_to_string(folder.join(name)).unwrap_or_default());
    let stem = name.strip_suffix(".html").unwrap_or(name);
    let page_years = HEADING
        .captures(&text)
        .ok()
        .flatten()
        .map_or_else(Vec::new, |h| years_in(&plain(&h[1])));
    let cited = name
        .strip_suffix(".notes.html")
        .map_or_else(HashMap::new, |base| {
            cited_years(&folder.join(format!("{base}.html")))
        });
    let mut out = Vec::new();
    for block in BLOCK.captures_iter(&text).flatten() {
        let raw = &block[3];
        let note = NOTE_MARK.captures(&block[2]).ok().flatten();
        let mut marked: HashMap<String, usize> = HashMap::new();
        for span in MARKED.captures_iter(raw).flatten() {
            for x in pattern.find_iter(&plain(&span[1])).flatten() {
                *marked.entry(x.as_str().to_owned()).or_insert(0) += 1;
            }
        }
        let flat = plain(raw);
        let mut years = years_in(&flat);
        if years.is_empty() {
            years = note
                .as_ref()
                .and_then(|n| cited.get(&n[1]))
                .cloned()
                .unwrap_or_default();
        }
        if years.is_empty() {
            years.clone_from(&page_years);
        }
        for m in pattern.find_iter(&flat).flatten() {
            let found = m.as_str();
            if found.ends_with(" bu")
                && AREA_BEFORE
                    .is_match(before(&flat, m.start(), 16))
                    .unwrap_or(false)
            {
                continue;
            }
            if let Some(left) = marked.get_mut(found).filter(|n| **n > 0) {
                *left -= 1;
                continue;
            }
            let coin = coin_of(found);
            let best = known
                .iter()
                .filter(|(_, e)| e.2.contains(&coin))
                .flat_map(|(id, e)| {
                    years
                        .iter()
                        .map(move |y| ((e.0 - y).max(y - e.1).max(0), id))
                })
                .min();
            let context = format!(
                "{}[[{found}]]{}",
                before(&flat, m.start(), 240),
                after(&flat, m.end(), 60)
            );
            out.push(Amount {
                stem: stem.to_owned(),
                text: found.to_owned(),
                years: years.clone(),
                near: best.map_or_else(String::new, |b| b.1.clone()),
                gap: best.map(|b| b.0),
                context,
            });
        }
    }
    out
}

/// Every unmarked amount in a coin of these money systems, nearest a built era first.
pub(crate) fn amounts(root: &Path) -> Vec<Amount> {
    let known = eras(root);
    let pattern = amount_pattern(&known);
    let folder = root.join(QUESTIONS);
    let mut names: Vec<String> = std::fs::read_dir(&folder)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .collect();
    names.retain(|n| crate::checks::has_ext(n, "html") && !n.ends_with(".originals.html"));
    names.sort();
    let mut out: Vec<Amount> = names
        .iter()
        .flat_map(|n| scan(n, &folder, &pattern, &known))
        .collect();
    out.sort_by(|a, b| {
        (a.gap.is_none(), a.gap.unwrap_or(0), &a.stem).cmp(&(
            b.gap.is_none(),
            b.gap.unwrap_or(0),
            &b.stem,
        ))
    });
    out
}

fn passed_over(root: &Path) -> BTreeSet<(String, String)> {
    let text = std::fs::read_to_string(root.join(BACKFILL)).unwrap_or_default();
    super::py_lines(&text)
        .iter()
        .filter_map(|l| ROW.captures(l).ok().flatten())
        .map(|c| (c[1].to_owned(), c[2].to_owned()))
        .collect()
}

fn is_named(a: &Amount, named: &BTreeSet<(String, String)>) -> bool {
    named.contains(&(a.stem.clone(), a.text.clone()))
        || named.contains(&(a.stem.clone(), "*".to_owned()))
}

/// `record money-candidates [--check] [--all] [--stem S] [--context]`.
pub(crate) fn cli(args: &[String], root: &Path) -> Reply {
    let has = |n: &str| args.iter().any(|a| a == n);
    let stem = args
        .windows(2)
        .find(|w| w[0] == "--stem")
        .map_or("", |w| w[1].as_str());
    let named = passed_over(root);
    let found: Vec<Amount> = amounts(root)
        .into_iter()
        .filter(|a| a.stem.starts_with(stem))
        .collect();
    let owed = found.iter().filter(|a| !is_named(a, &named)).count();
    let mut out = String::new();
    for a in found
        .iter()
        .filter(|a| has("--all") || !is_named(a, &named))
    {
        let shown: Vec<String> = a.years.iter().take(4).map(i64::to_string).collect();
        let years = if shown.is_empty() {
            "no year".to_owned()
        } else {
            shown.join(",")
        };
        let where_at = a.gap.map_or_else(
            || "no year or no era".to_owned(),
            |g| format!("{g} yr from {}", a.near),
        );
        let tag = if is_named(a, &named) {
            " [passed over]"
        } else {
            ""
        };
        let _ = writeln!(out, "{where_at:<28} {} | {} | {years}{tag}", a.stem, a.text);
        if has("--context") {
            let _ = writeln!(out, "    {}", a.context);
        }
    }
    if has("--check") && owed > 0 {
        return reply(out, format!("money-candidates: {owed} amount(s) neither marked nor named in {BACKFILL} - mark each (feature 413, record/money.py) or add `- <stem> | <amount> | <reason>` to it\n"), 1);
    }
    let _ = writeln!(out, "money-candidates: {owed} amount(s) owed a decision");
    reply(out, String::new(), 0)
}

#[cfg(test)]
mod tests;
