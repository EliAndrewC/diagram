//! The remote run-log entry (FR-020) and month-to-date spend, from local records only (from `ci/runlog.py`): Cost Explorer costs money per call. An entry has the shape of the Makefile's `LOGRUN`, plus `where`, `build_id`,
//! `minutes` and `cost_usd`.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use l7r_guard::shared::log::civil;
use serde_json::{json, Value};

use super::config;
use crate::codeid::stated;

pub(crate) const RUN_LOG: &str = "dev/run-log";
pub(crate) const BYPASS_LOG: &str = "dev/bypass-log";
const WOULD_HAVE: &str = "would-have-dispatched";

/// One clock read: (seconds, the microseconds of that same second), so that a stamp sorts in write order (feature 217).
fn now() -> (u64, u32) {
    let d = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default();
    (d.as_secs(), d.subsec_micros())
}

fn month(secs: u64) -> String {
    let (y, mo, ..) = civil(secs);
    format!("{y:04}-{mo:02}")
}

pub(crate) fn utc_of(secs: u64) -> String {
    let (y, mo, d, h, mi, s) = civil(secs);
    format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z")
}

fn stamp(secs: u64, micros: u32) -> String {
    let (y, mo, d, h, mi, s) = civil(secs);
    format!("{y:04}{mo:02}{d:02}T{h:02}{mi:02}{s:02}{micros:06}")
}

fn walk(dir: &Path, into: &mut Vec<PathBuf>) {
    for entry in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        let path = entry.path();
        if path.is_dir() {
            walk(&path, into);
        } else if path.extension().is_some_and(|e| e == "json") {
            into.push(path);
        }
    }
}

/// Every entry of a log, oldest first, sorted by name (the write-order stamp), so that month folders and anything written flat interleave.
pub(crate) fn log_files(root: &Path, log: &str) -> Vec<PathBuf> {
    let mut files = Vec::new();
    walk(&root.join(log), &mut files);
    files.sort_by_key(|p| p.file_name().map(std::ffi::OsStr::to_os_string));
    files
}

fn short_head(root: &Path) -> String {
    let done = std::process::Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["rev-parse", "--short", "HEAD"])
        .output();
    let out = done.map(|o| o.stdout).unwrap_or_default();
    String::from_utf8_lossy(&out).trim().to_owned()
}

fn hundredths(value: f64, places: i32) -> f64 {
    let scale = 10_f64.powi(places);
    // an empty sum is -0.0 in Rust, which would print as `$-0.00`; adding zero makes it plain
    (value * scale).round() / scale + 0.0
}

fn store(root: &Path, entry: &Value) -> Result<PathBuf, String> {
    let (secs, micros) = now();
    let dir = root.join(RUN_LOG).join(month(secs));
    stated(std::fs::create_dir_all(&dir), RUN_LOG)?;
    let path = dir.join(format!(
        "{}-{}.json",
        stamp(secs, micros),
        std::process::id()
    ));
    let body = stated(
        serde_json::to_string_pretty(entry).map_err(std::io::Error::other),
        RUN_LOG,
    )?;
    stated(std::fs::write(&path, format!("{body}\n")), RUN_LOG)?;
    Ok(path)
}

/// What a finished or settled remote run records.
pub(crate) struct Remote<'a> {
    pub target: &'a str,
    pub scope: &'a str,
    pub seconds: u64,
    pub result: &'a str,
    pub build_id: &'a str,
    pub minutes: f64,
    pub reason: &'a str,
    pub rate: f64,
    pub compute: &'a str,
}

pub(crate) fn write_remote(root: &Path, r: &Remote<'_>) -> Result<PathBuf, String> {
    store(
        root,
        &json!({"utc": utc_of(now().0), "target": r.target, "scope": r.scope, "seconds": r.seconds, "result": r.result, "commit": short_head(root), "where": "codebuild", "build_id": r.build_id, "minutes": hundredths(r.minutes, 2), "cost_usd": hundredths(r.minutes * r.rate, 4), "compute": r.compute, "reason": r.reason}),
    )
}

/// With remote off, every attempt that would have started a paid run is recorded and never counted as spend (feature 133 FR-004).
pub(crate) fn write_would_have(
    root: &Path,
    target: &str,
    scope: &str,
    minutes: f64,
    reason: &str,
) -> Result<PathBuf, String> {
    store(
        root,
        &json!({"utc": utc_of(now().0), "target": target, "scope": scope, "seconds": 0, "result": WOULD_HAVE, "commit": short_head(root), "where": WOULD_HAVE, "build_id": "", "minutes": hundredths(minutes, 2), "cost_usd": hundredths(minutes * config::RATE_PER_MIN, 4), "compute": config::COMPUTE_TYPE, "reason": reason}),
    )
}

fn entries(root: &Path, place: &str) -> Vec<Value> {
    log_files(root, RUN_LOG)
        .iter()
        .filter_map(|f| {
            serde_json::from_str::<Value>(&std::fs::read_to_string(f).unwrap_or_default()).ok()
        })
        .filter(|r| r["where"] == place)
        .collect()
}

fn text<'a>(row: &'a Value, key: &str) -> &'a str {
    row[key].as_str().unwrap_or_default()
}

fn number(row: &Value, key: &str) -> f64 {
    row[key].as_f64().unwrap_or(0.0)
}

fn in_month(row: &Value, month_text: &str) -> bool {
    text(row, "utc").starts_with(month_text)
}

/// The month-to-date spend of `month_text`, or of this month.
pub(crate) fn month_to_date(root: &Path, month_text: Option<&str>) -> f64 {
    let current = month(now().0);
    let wanted = month_text.unwrap_or(&current);
    hundredths(
        entries(root, "codebuild")
            .iter()
            .filter(|r| in_month(r, wanted))
            .map(|r| number(r, "cost_usd"))
            .sum(),
        4,
    )
}

fn last(rows: &[Value]) -> &[Value] {
    &rows[rows.len().saturating_sub(15)..]
}

fn would_have_report(root: &Path) -> String {
    let rows = entries(root, WOULD_HAVE);
    let mut out = "\x1b[1mWould have dispatched\x1b[0m (remote off; dev/run-log/, where=would-have-dispatched) - audited at the period's end, never counted as spend".to_owned();
    for r in last(&rows) {
        let reason: String = text(r, "reason").chars().take(70).collect();
        let _ = write!(
            out,
            "\n  {}  {:<16} {:<9} ~{:>4.0} min  ~${:>5.2}  {reason}",
            text(r, "utc"),
            text(r, "target"),
            text(r, "scope"),
            number(r, "minutes"),
            number(r, "cost_usd")
        );
    }
    if rows.is_empty() {
        out.push_str("\n  (none)");
    } else {
        let spared: f64 = rows.iter().map(|r| number(r, "cost_usd")).sum();
        let _ = write!(
            out,
            "\n  {} attempt(s), ~${spared:.2} not spent",
            rows.len()
        );
    }
    out
}

/// The audit's "Remote spend" block.
pub(crate) fn remote_spend_report(root: &Path) -> String {
    let rows = entries(root, "codebuild");
    let mut out = "\x1b[1mRemote spend\x1b[0m (dev/run-log/, where=codebuild)".to_owned();
    for r in last(&rows) {
        let _ = write!(
            out,
            "\n  {}  {:<9} {:>5.1} min  ${:>5.2}  {:<24} {}",
            text(r, "utc"),
            text(r, "scope"),
            number(r, "minutes"),
            number(r, "cost_usd"),
            text(r, "result"),
            text(r, "build_id")
        );
    }
    if rows.is_empty() {
        out.push_str("\n  (no remote runs yet)");
    }
    let current = month(now().0);
    let _ = write!(
        out,
        "\n  month-to-date: ${:.2} over {} run(s) this month\n{}",
        month_to_date(root, None),
        rows.iter().filter(|r| in_month(r, &current)).count(),
        would_have_report(root)
    );
    out
}

#[cfg(test)]
mod tests;
