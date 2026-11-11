//! Runtime ratchets: a target that gets slower fails, instead of getting slower quietly (feature 171; feature 449 T75, from `ratchet.py`).
//!
//! WHY (GM 2026-08-30, on `make done`'s median going 35 s -> 148 s in three days): "I could have sworn that we had some code in place that
//! detected when we had our unit tests start to take longer." The table is `dev/ratchets.json`, one row per target, each pinned baseline with
//! its written reason. Four properties are load-bearing: the GM's numbers are hard ceilings the mechanism sits under; the baseline is pinned,
//! not rolling; what is compared differs by target and regime; a new target is a row, not a mechanism.

use std::path::Path;
use std::time::Instant;

use serde_json::Value;

use super::reply;

const USAGE_LOG_TOOL: &str = "ratchet"; // the `usage_log` name
const TABLE: &str = "dev/ratchets.json";
#[cfg(not(test))]
const CALIBRATION_N: u64 = 300_000_000;
#[cfg(test)]
const CALIBRATION_N: u64 = 1000;

/// One row of the table.
#[derive(Clone, Debug, Default)]
pub struct Ratchet {
    pub baseline: i64,
    pub reason: String,
    pub hard_ceiling: Option<i64>,
    pub hard_at_or_below: Option<i64>,
    pub compare: String,
    pub armed: bool,
    pub baseline_cold: Option<i64>,
    pub calibration_s: Option<f64>,
    pub calibration_reason: String,
    pub reason_cold: String,
    pub min_class_runs: i64,
}

fn row(v: &Value) -> Ratchet {
    let text = |k: &str| v[k].as_str().unwrap_or_default().to_owned();
    Ratchet {
        baseline: v["baseline"].as_i64().unwrap_or(0),
        reason: text("reason"),
        hard_ceiling: v["hard_ceiling"].as_i64(),
        hard_at_or_below: v["hard_at_or_below"].as_i64(),
        compare: text("compare"),
        armed: v["armed"].as_bool().unwrap_or(true),
        baseline_cold: v["baseline_cold"].as_i64(),
        calibration_s: v["calibration_s"].as_f64(),
        calibration_reason: text("calibration_reason"),
        reason_cold: text("reason_cold"),
        min_class_runs: v["min_class_runs"].as_i64().unwrap_or(5),
    }
}

/// The row for `target`, if the table holds one.
pub fn find(root: &Path, target: &str) -> Option<Ratchet> {
    let data: Value =
        serde_json::from_str(&std::fs::read_to_string(root.join(TABLE)).ok()?).ok()?;
    data.get(target).map(row)
}

/// FR-004: the ceiling for a target with no GM-stated number in force, never above the GM's where one is given.
#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_precision_loss,
    reason = "Python's int(baseline * 1.3) of a small count of seconds"
)]
#[must_use]
pub fn derive_ceiling(baseline: i64, hard: Option<i64>) -> i64 {
    let grown = (baseline + 4).max((baseline as f64 * 1.3) as i64);
    hard.map_or(grown, |h| h.min(grown))
}

/// The ceiling in force, and what is compared against it: at or below `hard_at_or_below` the GM's number and the run.
#[must_use]
pub fn ceiling_for(r: &Ratchet) -> (i64, String) {
    if let (Some(ceiling), Some(at)) = (r.hard_ceiling, r.hard_at_or_below) {
        if r.baseline <= at {
            return (ceiling, "run".to_owned());
        }
    }
    (derive_ceiling(r.baseline, None), r.compare.clone())
}

/// One roll-cache class's ceiling: an unknown class takes the stricter warm one.
#[must_use]
pub fn ceiling_for_class(r: &Ratchet, cache: Option<&str>) -> (i64, String) {
    match (cache, r.baseline_cold) {
        (Some("cold"), Some(cold)) => (derive_ceiling(cold, None), r.compare.clone()),
        _ => ceiling_for(r),
    }
}

fn spin(n: u64) -> f64 {
    let began = Instant::now();
    let mut s: u64 = 0;
    for i in 0..n {
        s = s.wrapping_add(std::hint::black_box(i).wrapping_mul(i));
    }
    std::hint::black_box(s);
    began.elapsed().as_secs_f64()
}

/// The slowest of `workers` loops run at once.
fn round_of(workers: usize, n: u64) -> f64 {
    std::thread::scope(|s| {
        let running: Vec<_> = (0..workers).map(|_| s.spawn(move || spin(n))).collect();
        running
            .into_iter()
            .map(|t| t.join().unwrap_or(0.0))
            .fold(0.0, f64::max)
    })
}

/// The best of `rounds` rounds' slowest loop.
pub fn best_round(workers: usize, rounds: usize, run: &dyn Fn(usize) -> f64) -> f64 {
    (0..rounds)
        .map(|_| run(workers))
        .fold(f64::INFINITY, f64::min)
}

/// How much slower the host runs now than when the loop was pinned; never below 1, so a run is never held to a tighter bar than the GM's.
pub fn slowdown(r: &Ratchet, workers: usize, rounds: usize, run: &dyn Fn(usize) -> f64) -> f64 {
    r.calibration_s.map_or(1.0, |pinned| {
        (best_round(workers, rounds, run) / pinned).max(1.0)
    })
}

/// Python's `round`: to the nearest integer, a tie to the even one.
#[expect(clippy::cast_possible_truncation, reason = "seconds, far inside i64")]
#[must_use]
pub fn round_even(x: f64) -> i64 {
    let down = x.floor();
    let diff = x - down;
    let up = (diff - 0.5).abs() < f64::EPSILON && (down as i64) % 2 != 0 || diff > 0.5;
    (if up { down + 1.0 } else { down }) as i64
}

/// What a verdict is asked about.
#[derive(Clone, Copy, Default)]
pub struct Asked<'a> {
    pub seconds: Option<i64>,
    pub median: Option<i64>,
    pub cache: Option<&'a str>,
    pub scope: Option<&'a str>,
    pub class_runs: Option<i64>,
}

/// The message of a run over its ceiling: what, against what, and the only way the baseline moves.
fn over(
    target: &str,
    r: &Ratchet,
    a: Asked<'_>,
    (measured, raw, slow): (i64, i64, f64),
    ceiling: i64,
    mode: &str,
) -> String {
    let net = if measured == raw {
        String::new()
    } else {
        format!(" ({raw}s raw, net of the host's {slow:.2}x slowdown)")
    };
    let what = if mode == "run" {
        "this run"
    } else {
        "the median of recent green runs"
    };
    let klass = a
        .cache
        .map_or_else(String::new, |c| format!(" ({c} roll cache)"));
    let base = match (a.cache, r.baseline_cold) {
        (Some("cold"), Some(cold)) => cold,
        _ => r.baseline,
    };
    format!(
        "\n\x1b[1m{target} is at {measured}s{net}, at or over its {ceiling}s ceiling{klass}.\x1b[0m\nMeasured on {what}, against a pinned baseline of {base}s.\nSTOP and find out what got slower - that is the point of this failing rather than you\nnoticing in three days' time. `make audit` shows the history; `make durations` shows where\nthe suite's time goes.\nIf the new time is legitimate and permanent, move the pinned baseline in dev/ratchets.json\nWITH a written reason - that is the only way it ever moves (feature 171, FR-003/FR-010).\n"
    )
}

/// (ok, message): a target with no row, an unarmed row or nothing measured is silent.
#[expect(
    clippy::cast_precision_loss,
    reason = "seconds, far inside f64's exact range"
)]
#[must_use]
pub fn verdict(target: &str, r: Option<&Ratchet>, a: Asked<'_>, slow: f64) -> (bool, String) {
    let Some(r) = r.filter(|r| r.armed) else {
        return (true, String::new());
    };
    let (ceiling, mut mode) = ceiling_for_class(r, a.cache);
    if a.class_runs.is_some_and(|n| n < r.min_class_runs) && a.scope == Some("reference") {
        "run".clone_into(&mut mode); // judge THIS run: never "pass for lack of evidence"
    }
    let Some(raw) = (if mode == "run" { a.seconds } else { a.median }) else {
        return (true, String::new());
    };
    let measured = if slow > 1.0 && mode == "run" {
        round_even(raw as f64 / slow)
    } else {
        raw
    };
    if measured >= ceiling {
        // a class median is printed and does not refuse (`ask:449-T75-gatecost-class`: the Python's make done never reached one, and timings gate nothing new)
        let refuses = !(mode == "median" && a.cache.is_some());
        return (
            !refuses,
            over(target, r, a, (measured, raw, slow), ceiling, &mode),
        );
    }
    if r.calibration_s.is_none() || mode != "run" {
        return (true, String::new());
    }
    let says = if raw >= ceiling {
        format!("{target}: {raw}s raw, {measured}s net of the host's {slow:.2}x slowdown - under its {ceiling}s ceiling")
    } else {
        format!("{target}: {raw}s, under its {ceiling}s ceiling (the host's slowdown not measured: asked only at the ceiling)")
    };
    (true, says)
}

fn digits(words: &[String], at: usize) -> Option<i64> {
    words
        .get(at)
        .filter(|w| !w.is_empty() && w.chars().all(|c| c.is_ascii_digit()))
        .and_then(|w| w.parse().ok())
}

fn workers_of(setting: Option<String>) -> usize {
    setting.and_then(|w| w.parse().ok()).unwrap_or(6)
}

/// `l7r-gate measure ratchet <target> <seconds> [median] [cache] [scope] [class_runs] | --calibrate [workers]`.
#[must_use]
pub fn cli(args: &[String], root: &Path) -> crate::Reply {
    let workers = workers_of(std::env::var("XDIST_WORKERS").ok());
    decide(args, root, workers, &|w| round_of(w, CALIBRATION_N))
}

fn decide(
    args: &[String],
    root: &Path,
    workers: usize,
    run: &dyn Fn(usize) -> f64,
) -> crate::Reply {
    if args.first().is_some_and(|a| a == "--calibrate") {
        return reply(
            format!(
                "{:.3}\n",
                best_round(
                    digits(args, 1)
                        .and_then(|n| usize::try_from(n).ok())
                        .unwrap_or(workers),
                    5,
                    run
                )
            ),
            String::new(),
            0,
        );
    }
    let target = args.first().map_or("", String::as_str);
    let a = Asked {
        seconds: digits(args, 1),
        median: digits(args, 2),
        cache: args
            .get(3)
            .map(String::as_str)
            .filter(|c| *c == "warm" || *c == "cold"),
        scope: args.get(4).map(String::as_str).filter(|s| !s.is_empty()),
        class_runs: digits(args, 5),
    };
    let r = find(root, target);
    // the loop runs only for a run at or over the ceiling: a run under it is judged as it always was, at no cost
    let slow = match (&r, a.seconds) {
        (Some(row), Some(s))
            if row.calibration_s.is_some() && s >= row.hard_ceiling.unwrap_or(i64::MAX) =>
        {
            slowdown(row, workers, 5, run)
        }
        _ => 1.0,
    };
    let (ok, message) = verdict(target, r.as_ref(), a, slow);
    crate::stamp::record_for(root, USAGE_LOG_TOOL, if ok { "passed" } else { "refused" });
    if !ok {
        return reply(String::new(), message + "\n", 1);
    }
    reply(
        if message.is_empty() {
            message
        } else {
            message + "\n"
        },
        String::new(),
        0,
    )
}

#[cfg(test)]
mod tests;
