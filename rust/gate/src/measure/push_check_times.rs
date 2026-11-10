//! What the push's checks cost, each timed as the push runs it (feature 383, SC-001; feature 449 T77, from `push_check_times.py`).
//!
//! Feature 383 was asked for on a measurement taken by hand (2026-10-13: the push's checks about 24 s, each timed alone in a clone); its success
//! criterion is the same measurement repeated. The rows are the Rust push's own table (`push::CHECKS`), so a row the push adds is timed; the
//! Python's table was its own list of the commands of a shell line since gone (`ask:449-T77-scope`, an FR-002 ruled case). Each command runs N
//! times (the first warms what a cache keeps, the last is the one reported) and nothing here refuses: a check's exit is printed beside its time.

use std::fmt::Write as _;
use std::path::Path;
use std::process::{Command, Stdio};
use std::time::Instant;

use serde_json::{json, Value};

use super::reply;
use crate::plan::pretty;

/// A row's name and its command; none when the clone does not have what the row needs.
pub(crate) type Timed = (String, Option<Command>);

/// Each command's last run: its wall time in hundredths of a second, its exit; a row with no command is skipped and named.
pub(crate) fn measure(rows: Vec<Timed>, runs: usize) -> Vec<Value> {
    let mut out = Vec::new();
    for (check, command) in rows {
        let Some(mut command) = command else {
            out.push(json!({"check": check, "skipped": "not in this clone"}));
            continue;
        };
        command
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .stdin(Stdio::null());
        let (mut wall, mut code) = (0.0, 0);
        for _ in 0..runs.max(1) {
            let start = Instant::now();
            code = command.status().ok().and_then(|s| s.code()).unwrap_or(-1);
            wall = start.elapsed().as_secs_f64();
        }
        out.push(json!({"check": check, "wall_s": hundredths(wall), "exit": code}));
    }
    out
}

fn hundredths(x: f64) -> f64 {
    (x * 100.0).round() / 100.0
}

/// The one-minute load average, from the file every Linux keeps it in.
pub(crate) fn load(text: &str) -> f64 {
    text.split_whitespace()
        .next()
        .and_then(|w| w.parse().ok())
        .unwrap_or(0.0)
}

pub(crate) fn report(rows: &[Value], load_now: f64) -> (String, f64) {
    let mut out = String::new();
    let mut total = 0.0;
    for r in rows {
        let check = r["check"].as_str().unwrap_or("");
        match r.get("wall_s").and_then(Value::as_f64) {
            Some(wall) => {
                total += wall;
                let _ = writeln!(out, "{wall:6.2} s  exit {}  {check}", r["exit"]);
            }
            None => {
                let _ = writeln!(
                    out,
                    "     -    {check} ({})",
                    r["skipped"].as_str().unwrap_or("")
                );
            }
        }
    }
    let total = hundredths(total);
    let _ = writeln!(out, "{total:6.2} s  in all, load {load_now:.1}");
    (out, total)
}

fn flag<'a>(args: &'a [String], name: &str) -> Option<&'a str> {
    args.windows(2)
        .find(|w| w[0] == name)
        .map(|w| w[1].as_str())
}

/// `l7r-gate measure push-check-times [--root <clone>] [--runs N] [--json <out>]`.
pub(crate) fn cli(args: &[String], root: &Path, tree: &Path) -> crate::Reply {
    let Ok(at) = std::fs::canonicalize(flag(args, "--root").map_or(root, Path::new)) else {
        return reply(
            String::new(),
            "push-check-times: no such clone\n".to_owned(),
            2,
        );
    };
    let runs = flag(args, "--runs")
        .and_then(|n| n.parse().ok())
        .unwrap_or(2);
    let rows = measure(crate::push::timing_rows(tree, &at), runs);
    let load_now = load(&std::fs::read_to_string("/proc/loadavg").unwrap_or_default());
    let (out, total) = report(&rows, load_now);
    if let Some(file) = flag(args, "--json") {
        let kept =
            json!({"total_s": total, "load": (load_now * 10.0).round() / 10.0, "rows": rows});
        if let Err(why) = std::fs::write(file, pretty(&kept)) {
            return reply(out, format!("push-check-times: {file}: {why}\n"), 1);
        }
    }
    reply(out, String::new(), 0)
}

#[cfg(test)]
mod tests;
