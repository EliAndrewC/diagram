//! What each review check yields for its cost (feature 375 amendment 8, FR-037; feature 449 T76, from `review_yield.py`): each check's passes, what
//! became of its findings, its hours and findings acted on per hour, read from the review ledger's measured rows.

use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Map, Value};

use super::reply;

const DISMISSED: [&str; 11] = [
    "verified",
    "accepted",
    "spec accepted",
    "plan accepted",
    "declined",
    "no change",
    "no-change",
    "none",
    "nothing",
    "answered",
    "left",
];
const DEFERRED: [&str; 3] = ["put to the gm", "left for", "not applied"];
/// FR-037 counts a finding filed as acted on, whatever the cell opens with.
const FILED: [&str; 3] = ["filed", "carried", "follow-up"];
const NOT_AN_ACT: [&str; 3] = ["", "-", "re-dispatched"];
const COLUMNS: [&str; 11] = [
    "passes",
    "with a finding",
    "acted on",
    "dismissed",
    "deferred",
    "not acted on",
    "author missed",
    "hours",
    "k tokens out",
    "features",
    "acted on per hour",
];

fn compiled(p: &str) -> Regex {
    Regex::new(p).unwrap_or_else(|e| unreachable!("{e}"))
}

static WALL: LazyLock<Regex> = LazyLock::new(|| compiled(r"(\d+(?:\.\d+)?)\s*s\b"));
static OUT: LazyLock<Regex> = LazyLock::new(|| compiled(r"/\s*([\d.]+)\s*k\s+out"));
static FEATURE: LazyLock<Regex> = LazyLock::new(|| compiled(r"\b(\d{3})\b"));
static ROW: LazyLock<Regex> = LazyLock::new(|| compiled(r"^\| 20\d\d-\d\d-\d\d \|"));

fn number_in(re: &Regex, text: &str) -> Option<f64> {
    re.captures(text).ok()??.get(1)?.as_str().parse().ok()
}

/// The measured rows from `since` on, each its ten cells; a row with another count, or no wall time, is not one.
fn rows(text: &str, since: &str) -> Vec<Vec<String>> {
    text.lines()
        .filter(|l| ROW.is_match(l).unwrap_or(false))
        .map(|l| {
            l.trim()
                .trim_matches('|')
                .split('|')
                .map(|c| c.trim().to_owned())
                .collect::<Vec<_>>()
        })
        .filter(|c| c.len() == 10 && c[0].as_str() >= since && number_in(&WALL, &c[8]).is_some())
        .collect()
}

fn has_finding(c: &[String]) -> bool {
    !["nothing", "-", ""].contains(&c[5].to_lowercase().as_str())
        && !c[4].starts_with("- ")
        && c[4] != "-"
        && !c[4].is_empty()
}

/// What became of a finding, from its free-text "acted on" cell.
fn outcome(acted: &str) -> &'static str {
    let a = acted.trim().to_lowercase();
    if NOT_AN_ACT.contains(&a.split(';').next().unwrap_or_default().trim()) {
        "not acted on"
    } else if DEFERRED.iter().any(|d| a.starts_with(d)) {
        if FILED.iter().any(|w| a.contains(w)) {
            "acted on"
        } else {
            "deferred"
        }
    } else if DISMISSED.iter().any(|d| a.starts_with(d)) {
        "dismissed"
    } else {
        "acted on"
    }
}

/// One check's running totals.
#[derive(Default)]
struct Tally {
    counts: [i64; 7],
    hours: f64,
    k_out: f64,
    features: BTreeSet<String>,
}

const COUNT_NAMES: [&str; 7] = [
    "passes",
    "with a finding",
    "acted on",
    "dismissed",
    "deferred",
    "not acted on",
    "author missed",
];

fn bump(t: &mut Tally, name: &str) {
    if let Some(i) = COUNT_NAMES.iter().position(|n| *n == name) {
        t.counts[i] += 1;
    }
}

fn rounded(x: f64, places: usize) -> f64 {
    format!("{x:.places$}").parse().unwrap_or(x)
}

fn tally_row(t: &Tally) -> Value {
    let mut row = Map::new();
    for (name, n) in COUNT_NAMES.iter().zip(t.counts) {
        row.insert((*name).to_owned(), json!(n));
    }
    row.insert("hours".to_owned(), json!(rounded(t.hours, 2)));
    row.insert("k tokens out".to_owned(), json!(rounded(t.k_out, 1)));
    row.insert("features".to_owned(), json!(t.features.len()));
    #[expect(
        clippy::cast_precision_loss,
        reason = "a count of findings, far inside f64's exact range"
    )]
    let per = if t.hours > 0.0 {
        rounded(t.counts[2] as f64 / t.hours, 1)
    } else {
        0.0
    };
    row.insert("acted on per hour".to_owned(), json!(per));
    Value::Object(row)
}

/// Each check's row, in the order the checks first appear.
fn table(rs: &[Vec<String>]) -> Vec<(String, Value)> {
    let mut order: Vec<(String, Tally)> = Vec::new();
    for c in rs {
        let at = order
            .iter()
            .position(|(k, _)| *k == c[1])
            .unwrap_or_else(|| {
                order.push((c[1].clone(), Tally::default()));
                order.len() - 1
            });
        let r = &mut order[at].1;
        bump(r, "passes");
        if has_finding(c) {
            bump(r, "with a finding");
            bump(r, outcome(&c[7]));
        }
        if c[6].to_lowercase().starts_with("yes") {
            bump(r, "author missed");
        }
        r.hours += number_in(&WALL, &c[8]).unwrap_or(0.0) / 3600.0;
        r.k_out += number_in(&OUT, &c[9]).unwrap_or(0.0);
        r.features.extend(
            FEATURE
                .captures_iter(&c[2])
                .flatten()
                .map(|m| m[1].to_owned()),
        );
    }
    order.into_iter().map(|(k, t)| (k, tally_row(&t))).collect()
}

fn render(t: &[(String, Value)], since: &str, n: usize) -> String {
    let mut sorted: Vec<&(String, Value)> = t.iter().collect();
    sorted.sort_by(|a, b| {
        b.1["hours"]
            .as_f64()
            .unwrap_or(0.0)
            .total_cmp(&a.1["hours"].as_f64().unwrap_or(0.0))
    });
    let mut out = format!(
        "review yield since {since}: {n} measured rows\n\n| check | {} |\n{}|\n",
        COLUMNS.join(" | "),
        "|---".repeat(COLUMNS.len() + 1)
    );
    for (check, r) in sorted {
        let _ = writeln!(
            out,
            "| {check} | {} |",
            COLUMNS
                .iter()
                .map(|c| r[*c].to_string())
                .collect::<Vec<_>>()
                .join(" | ")
        );
    }
    out
}

/// `l7r-gate measure review-yield [--since D] [--ledger F] [--record F --key K]`.
pub(crate) fn cli(args: &[String], root: &Path) -> crate::Reply {
    let flag = |name: &str| {
        args.windows(2)
            .find(|w| w[0] == name)
            .map(|w| w[1].as_str())
    };
    let since = flag("--since").unwrap_or("2026-09-26");
    let ledger = flag("--ledger").map_or_else(
        || root.join("dev/review-ledger.md"),
        std::path::PathBuf::from,
    );
    let rs = rows(&std::fs::read_to_string(ledger).unwrap_or_default(), since);
    let t = table(&rs);
    let stdout = render(&t, since, rs.len());
    let Some(record) = flag("--record") else {
        return reply(stdout, String::new(), 0);
    };
    let Some(key) = flag("--key") else {
        return reply(stdout, "review_yield: --record needs --key\n".to_owned(), 2);
    };
    let mut data: Value =
        serde_json::from_str(&std::fs::read_to_string(record).unwrap_or_default())
            .unwrap_or(json!({}));
    if data.get(key).is_none() {
        data[key] = json!({});
    }
    let by: Map<String, Value> = t.into_iter().collect();
    data[key]["value"] = json!({"since": since, "rows": rs.len(), "by check": by});
    let _ = std::fs::write(record, crate::cohort::seeds::dumped(&data));
    reply(stdout, String::new(), 0)
}

#[cfg(test)]
mod tests;
