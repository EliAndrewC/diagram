//! `l7r-gate measure sampler report` (`make sampler-report`, feature 451 T274): the samples of a window as one table, a row for
//! every count of pool trees held, so the builder count is read straight from it - anonymous memory median, 95th percentile and
//! peak against `memory.max`, the samples over the margin, the memory and CPU stall, the load against the cores, the most
//! `rustc` processes and the OOM kills.
//!
//! - THE SOURCE is the clone's samples (`mem-samples.1.jsonl` then `mem-samples.jsonl`), or each `--log <file>`: a file of the
//!   sampler's JSON lines, or one of the hand loop's of 2026-11-26 (`<utc> anon=.. cur=.. mem_some_us=.. load=.. [peak=..]
//!   [oom_kill=..] [rustc=..] [builders=..]`, `dev/measurements/2026-11-26/builder-count/mem-samples-*.log`), a table a file.
//! - THE WINDOW is `--since`/`--until`, ISO UTC, compared as text with each sample's `utc`.
//! - THE FIGURES: the median is the middle sample (the mean of the middle two), the 95th percentile the nearest rank (the
//!   sample at `ceil(0.95 n)`), which reproduce the figures recorded for the kept logs. A stall and the OOM kills are counters
//!   since the cgroup began, so a row's are the sum of the rises between one sample and the next, booked to the later sample's
//!   row; a pair more than [`GAP_S`] apart (the sampler was not running) or whose counter fell (the cgroup was made again) is
//!   booked to no row and counted as a gap.
//! - HELD IS NOT AT WORK: a row's count is the pool trees a task holds by the registry at the sample (`builders=` in a hand log,
//!   `?` where the log has none); a held tree's builder may be reading or idle, so a row is "at most N builders at work".
//! - AGAINST `memory.peak`: the cgroup's own peak is of `memory.current`, page cache included, so the report sets the sampled
//!   `cur` peak beside it - a sampled peak over the cgroup's is a broken report - and says how far `memory.peak` rose in the
//!   window, which is what the samples can have missed between two of them.

use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use serde_json::{Map, Value};

use super::{reply, Env, DIR, FILE, KEPT};
use crate::Reply;

/// The seconds between two samples past which the pair is a gap. GUESS: twelve of the default interval, so a late sample under
/// load is no gap and a stopped sampler is.
pub const GAP_S: f64 = 120.0;

const GIB: f64 = 1_073_741_824.0;

/// One line of either form as the sampler's fields: the hand loop's `load` is `load1` and its `builders` the count held.
fn fields(line: &str) -> Option<Map<String, Value>> {
    if line.starts_with('{') {
        let mut row = serde_json::from_str::<Value>(line)
            .ok()?
            .as_object()?
            .clone();
        let held = row.get("held").and_then(Value::as_array).map(Vec::len);
        row.insert("held_n".to_owned(), Value::from(held));
        return Some(row);
    }
    let mut words = line.split_whitespace();
    let mut row = Map::new();
    row.insert("utc".to_owned(), Value::from(words.next()?));
    for (key, value) in words.filter_map(|w| w.split_once('=')) {
        let name = match key {
            "load" => "load1",
            "builders" => "held_n",
            k => k,
        };
        let whole = value.parse::<u64>().map(Value::from);
        row.insert(
            name.to_owned(),
            Value::from(
                whole
                    .or_else(|_| value.parse::<f64>().map(Value::from))
                    .ok(),
            ),
        );
    }
    Some(row)
}

/// A sample as the report reads it: its time, its bucket and its numbers.
struct Sample {
    utc: String,
    at: f64,
    held: Option<u64>,
    row: Map<String, Value>,
}

impl Sample {
    fn num(&self, key: &str) -> Option<f64> {
        self.row.get(key).and_then(Value::as_f64)
    }
}

/// The samples of `text` inside the window, and the lines that are none (no time, or no `anon`).
fn samples(text: &str, since: &str, until: &str) -> (Vec<Sample>, usize) {
    let mut skipped = 0;
    let mut out = Vec::new();
    for line in text.lines().filter(|l| !l.trim().is_empty()) {
        let read = fields(line).and_then(|row| {
            let utc = row.get("utc")?.as_str()?.to_owned();
            let at = l7r_shared::checks::arbiter::epoch(&utc);
            row.get("anon")?.as_f64()?;
            (at > 0.0).then(|| Sample {
                held: row.get("held_n").and_then(Value::as_u64),
                utc,
                at,
                row,
            })
        });
        match read {
            Some(s) if s.utc.as_str() >= since && (until.is_empty() || s.utc.as_str() <= until) => {
                out.push(s);
            }
            Some(_) => {}
            None => skipped += 1,
        }
    }
    out.sort_by(|a, b| a.at.total_cmp(&b.at));
    (out, skipped)
}

/// One row of the table: the samples of one count of held trees.
#[derive(Default)]
struct Bucket {
    anon: Vec<f64>,
    load: Vec<f64>,
    over: usize,
    rustc: Option<f64>,
    stall: BTreeMap<&'static str, f64>,
}

const COUNTERS: [&str; 4] = ["mem_some_us", "mem_full_us", "cpu_some_us", "oom_kill"];

impl Bucket {
    fn take(&mut self, s: &Sample, margin: f64) {
        let anon = s.num("anon").unwrap_or(0.0);
        self.anon.push(anon);
        self.over += usize::from(anon > margin * GIB);
        self.load.extend(s.num("load1"));
        self.rustc = s
            .num("rustc")
            .map(|r| r.max(self.rustc.unwrap_or(0.0)))
            .or(self.rustc);
    }
}

fn median(sorted: &[f64]) -> f64 {
    let n = sorted.len();
    if n % 2 == 1 {
        sorted[n / 2]
    } else {
        f64::midpoint(sorted[n / 2 - 1], sorted[n / 2])
    }
}

/// The nearest-rank 95th percentile: the sample at `ceil(0.95 n)`.
fn p95(sorted: &[f64]) -> f64 {
    sorted[(sorted.len() * 95).div_ceil(100) - 1]
}

/// `median / 95th / max` of `values` over `unit`, `-` for none.
fn three(values: &[f64], unit: f64, places: usize) -> String {
    let mut sorted = values.to_vec();
    sorted.sort_by(f64::total_cmp);
    if sorted.is_empty() {
        return "-".to_owned();
    }
    let show = |v: f64| format!("{:.places$}", v / unit);
    format!(
        "{} / {} / {}",
        show(median(&sorted)),
        show(p95(&sorted)),
        show(sorted[sorted.len() - 1])
    )
}

fn opt(value: Option<f64>, unit: f64, places: usize) -> String {
    value.map_or_else(|| "-".to_owned(), |v| format!("{:.places$}", v / unit))
}

/// THE TABLE over `list`, named `source`: the head line, a row for all and for each count held, then the lines beneath.
fn table(source: &str, window: &[Sample], skipped: usize, env: &Env) -> String {
    let mut out = String::new();
    let (Some(first), Some(last)) = (window.first(), window.last()) else {
        let _ = writeln!(
            out,
            "sampler-report: {source} - no sample in the window ({skipped} lines that are none)"
        );
        return out;
    };
    let live_max = super::read(&env.cgroup.join("memory.max"))
        .trim()
        .parse::<f64>()
        .ok();
    let max = last.num("max").or(live_max);
    #[expect(clippy::cast_precision_loss, reason = "a count of cores")]
    let cores = last.num("cores").unwrap_or(env.cores as f64);
    let mut all = Bucket::default();
    let mut rows: BTreeMap<Option<u64>, Bucket> = BTreeMap::new();
    let mut gaps = 0;
    let mut before: Option<&Sample> = None;
    for s in window {
        all.take(s, env.margin_gib);
        let row = rows.entry(s.held).or_default();
        row.take(s, env.margin_gib);
        if let Some(b) = before {
            let rises: Vec<(&str, f64)> = COUNTERS
                .iter()
                .filter_map(|k| Some((*k, s.num(k)? - b.num(k)?)))
                .collect();
            if s.at - b.at > GAP_S || rises.iter().any(|(_, r)| *r < 0.0) {
                gaps += 1;
            } else {
                for (key, rise) in rises {
                    *all.stall.entry(key).or_default() += rise;
                    *row.stall.entry(key).or_default() += rise;
                }
            }
        }
        before = Some(s);
    }
    let _ = writeln!(
        out,
        "sampler-report: {source} - {} samples, {} to {} ({:.1} minutes); memory.max {} GiB, {cores:.0} cores, margin {} GiB (L7R_MEM_MARGIN_GIB, a GUESS knob)",
        window.len(),
        first.utc,
        last.utc,
        (last.at - first.at) / 60.0,
        opt(max, GIB, 2),
        env.margin_gib
    );
    let _ = writeln!(out, "  held | samples | anon GiB median / 95th / peak | peak of max | over margin | mem stall s some / full | cpu stall s | load median / 95th / max | max over cores | rustc max | OOM kills");
    let mut line = |label: String, b: &Bucket| {
        let peak = b.anon.iter().copied().fold(0.0, f64::max);
        let top = b.load.iter().copied().fold(0.0, f64::max);
        let stall = |k: &str| opt(b.stall.get(k).copied(), 1e6, 1);
        let _ = writeln!(
            out,
            "  {label:>4} | {:>7} | {} | {} | {} | {} / {} | {} | {} | {:.1}x | {} | {}",
            b.anon.len(),
            three(&b.anon, GIB, 2),
            max.map_or_else(|| "-".to_owned(), |m| format!("{:.0}%", 100.0 * peak / m)),
            b.over,
            stall("mem_some_us"),
            stall("mem_full_us"),
            stall("cpu_some_us"),
            three(&b.load, 1.0, 1),
            top / cores,
            opt(b.rustc, 1.0, 0),
            opt(b.stall.get("oom_kill").copied(), 1.0, 0)
        );
    };
    line("all".to_owned(), &all);
    for (held, b) in &rows {
        line(held.map_or_else(|| "?".to_owned(), |n| n.to_string()), b);
    }
    let cur = window
        .iter()
        .filter_map(|s| s.num("cur"))
        .fold(0.0, f64::max);
    match (first.num("peak"), last.num("peak")) {
        (Some(was), Some(is)) => {
            let verdict = if cur <= is {
                "agree"
            } else {
                "DISAGREE: a sampled figure over the cgroup's own peak is a broken report"
            };
            let _ = writeln!(out, "  memory.current: sampled peak {:.2} GiB; the cgroup's memory.peak {:.2} GiB at the last sample, risen {:.2} GiB in the window - {verdict}", cur / GIB, is / GIB, (is - was) / GIB);
        }
        _ => {
            let _ = writeln!(
                out,
                "  memory.current: sampled peak {:.2} GiB; no memory.peak in these samples",
                cur / GIB
            );
        }
    }
    let _ = writeln!(out, "  gaps: {gaps} (two samples more than {GAP_S:.0} s apart, or a counter that fell: the stall and OOM kills across one are in no row); lines that are no sample: {skipped}");
    let _ = writeln!(out, "  held = the pool trees a task holds at the sample (a hand log's builders=, ? where it has none); a held tree's builder may be idle, so a row is at most that many at work");
    out
}

/// `report [--since <ISO UTC>] [--until <ISO UTC>] [--log <file>]...`: the clone's samples, or each log, as its table.
pub(super) fn cli(args: &[String], env: &Env) -> Reply {
    let flag = |name: &str| {
        args.iter()
            .position(|a| a == name)
            .and_then(|i| args.get(i + 1))
            .cloned()
            .unwrap_or_default()
    };
    let (since, until) = (flag("--since"), flag("--until"));
    let logs: Vec<PathBuf> = args
        .iter()
        .zip(args.iter().skip(1))
        .filter(|(f, _)| *f == "--log")
        .flat_map(|(_, v)| v.split_whitespace().map(PathBuf::from).collect::<Vec<_>>())
        .collect();
    let mut out = String::new();
    if logs.is_empty() {
        let dir = env.common.join(DIR);
        let text = format!(
            "{}{}",
            super::read(&dir.join(KEPT)),
            super::read(&dir.join(FILE))
        );
        let (list, skipped) = samples(&text, &since, &until);
        out.push_str(&table(
            &dir.join(FILE).to_string_lossy(),
            &list,
            skipped,
            env,
        ));
    }
    let mut missing = String::new();
    for log in &logs {
        if !log.is_file() {
            let _ = writeln!(missing, "sampler-report: {} is no file", log.display());
            continue;
        }
        let (list, skipped) = samples(&super::read(log), &since, &until);
        out.push_str(&table(&name(log), &list, skipped, env));
    }
    Reply {
        stdout: out,
        ..reply(missing.clone(), i32::from(!missing.is_empty()) * 2)
    }
}

fn name(path: &Path) -> String {
    path.file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned()
}
