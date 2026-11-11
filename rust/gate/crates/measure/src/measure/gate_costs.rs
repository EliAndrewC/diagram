//! What a gate run costs here, read from the run records (feature 415 T04; feature 449 T75, from `gate_costs.py`).
//!
//! WHY (the GM, 2026-10-24: "First measure the fixed cost and the per-test cost on a few real landings, so the change rests on numbers rather
//! than a second guess"): the table of runs, a least-squares fit of the test phase on the selected count, and how the selection grows.

use std::fmt::Write as _;
use std::path::Path;

use serde_json::Value;

use super::{json_files, reply};

const USAGE_LOG_TOOL: &str = "gate_costs"; // the `usage_log` name

/// The `make done` run records with `phases`, oldest first.
fn records(root: &Path, since: &str) -> Vec<Value> {
    let mut out: Vec<Value> = std::fs::read_dir(root.join("dev/run-log"))
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| e.path().is_dir())
        .flat_map(|e| json_files(&e.path()))
        .filter_map(|p| {
            serde_json::from_str::<Value>(&std::fs::read_to_string(p).unwrap_or_default()).ok()
        })
        .filter(|r| {
            (r["target"] == "done" || r["target"] == "idle-done")
                && r.get("phases").is_some()
                && r["utc"].as_str().unwrap_or_default() >= since
        })
        .collect();
    out.sort_by_key(|r| r["utc"].as_str().unwrap_or_default().to_owned());
    out
}

/// (fixed, per test) by least squares; none under two distinct x.
#[expect(
    clippy::cast_precision_loss,
    reason = "a count of runs, far inside f64's exact range"
)]
fn fit(points: &[(f64, f64)]) -> Option<(f64, f64)> {
    let first = points.first()?.0;
    if points
        .iter()
        .all(|(x, _)| (*x - first).abs() < f64::EPSILON)
    {
        return None;
    }
    let n = points.len() as f64;
    let mx = points.iter().map(|p| p.0).sum::<f64>() / n;
    let my = points.iter().map(|p| p.1).sum::<f64>() / n;
    let slope = points.iter().map(|(x, y)| (x - mx) * (y - my)).sum::<f64>()
        / points.iter().map(|(x, _)| (x - mx).powi(2)).sum::<f64>();
    Some((my - slope * mx, slope))
}

/// (utc, runs since the last full, selected) for each incremental run.
fn growth(recs: &[Value]) -> Vec<(String, i64, i64)> {
    let mut since_full = 0;
    let mut out = Vec::new();
    for r in recs {
        if r["plan_mode"] == "full" {
            since_full = 0;
        } else if r["plan_mode"] == "incremental" {
            since_full += 1;
            out.push((
                r["utc"].as_str().unwrap_or_default().to_owned(),
                since_full,
                r["selected"].as_i64().unwrap_or(0),
            ));
        }
    }
    out
}

/// A value as Python's `format(value, '>N')` prints it; absent is empty.
fn cell(v: &Value) -> String {
    match v {
        Value::Null => String::new(),
        Value::String(s) => s.clone(),
        other => other.to_string(),
    }
}

fn table(green: &[Value]) -> String {
    let mut out = format!(
        "{:20} {:11} {:>8} {:>9} {:>8} {:>8} {:>7} {:>5}\n",
        "utc", "mode", "selected", "collected", "pytest_s", "floors_s", "total_s", "load"
    );
    for r in green {
        let _ = writeln!(
            out,
            "{:20} {:11} {:>8} {:>9} {:>8} {:>8} {:>7} {:>5}",
            cell(&r["utc"]),
            cell(&r["plan_mode"]),
            cell(&r["selected"]),
            cell(&r["collected"]),
            cell(&r["phases"]["pytest"]),
            cell(&r["phases"]["floors"]),
            cell(&r["seconds"]),
            cell(&r["host"]["load"][0])
        );
    }
    out
}

#[expect(
    clippy::cast_precision_loss,
    reason = "a test count, far inside f64's exact range"
)]
fn points(green: &[Value]) -> Vec<(f64, f64)> {
    green
        .iter()
        .filter_map(|r| {
            Some((
                r["selected"].as_i64()? as f64,
                r["phases"]["pytest"].as_f64()?,
            ))
        })
        .collect()
}

/// `l7r-gate measure gate-costs [--since <utc>]`; `L7R_ROOT` is read by the caller as the root.
#[must_use]
pub fn cli(args: &[String], root: &Path) -> crate::Reply {
    let since = args
        .windows(2)
        .find(|w| w[0] == "--since")
        .map_or("", |w| w[1].as_str());
    let green: Vec<Value> = records(root, since)
        .into_iter()
        .filter(|r| r["result"] == "green" && !r["plan_mode"].is_null())
        .collect();
    let mut out = table(&green);
    let pts = points(&green);
    let what = fit(&pts).map_or_else(
        || "too few distinct selections to fit".to_owned(),
        |(fixed, per)| {
            format!(
                "test phase = {fixed:.1} s fixed + {:.2} ms per selected test",
                per * 1000.0
            )
        },
    );
    let _ = writeln!(out, "fit over {} run(s): {what}", pts.len());
    for (utc, n, selected) in growth(&green) {
        let _ = writeln!(
            out,
            "growth: {utc} - incremental run {n} since the last full, {selected} test(s) selected"
        );
    }
    crate::stamp::record_for(root, USAGE_LOG_TOOL, "passed");
    reply(out, String::new(), 0)
}

#[cfg(test)]
mod tests;
