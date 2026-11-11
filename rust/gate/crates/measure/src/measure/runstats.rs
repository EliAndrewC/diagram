//! When a gate's failures happened and what the machine was doing around it, for the run log (feature 449 T76, from `runstats.py`).
//!
//! WHY (GM 2026-10-03): whether streaming a gate's failures as they occur would let a session start fixing early depends on how long a failed
//! gate runs after its first failure, which nothing recorded. The host figures come with them so an outlier can be told from a real slowdown.
//! Every figure is one read of a small `/proc` or `/sys` file, and a figure the host does not expose is left out, never guessed.

use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use serde_json::{json, Map, Value};

use super::reply;

const START: &str = "gate-stats-start.json";
const FAILURES: &str = "gate-failures";
const PHASES: &str = "gate-phases";
const PHASES_PRE: &str = "gate-phases-pre";
/// Where the gate's selection plugin writes what this run selected.
const RESULT: &str = "gate-baseline/result.json";
/// A run record keeps the first 20 failed test ids: enough to read a gate by, small in the log.
const FAILED_NAMES_KEPT: usize = 20;
const USAGE: &str = "    runstats start <dir>          snapshot the host at the gate's start; clear the failure marks\n    runstats fail <dir> <phase>   mark a phase that failed, at the moment it finished\n    runstats end <dir>            print the run-log fields as JSON (empty object on no start)\n    runstats phase <dir> <name> <seconds>      a phase of THIS gate run and how long it took (feature 415, FR-005)\n    runstats phase-pre <dir> <name> <seconds>  the same, for a phase run before `start` (the preflight); `start` keeps it\n";

/// Where the host's figures are read from, so a test can give it another host.
struct Host {
    proc: PathBuf,
    sys: PathBuf,
}

fn read(path: &Path) -> Option<String> {
    std::fs::read_to_string(path).ok()
}

fn sorted_children(dir: &Path, wanted: impl Fn(&str) -> bool) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| wanted(&e.file_name().to_string_lossy()))
        .map(|e| e.path())
        .collect();
    out.sort();
    out
}

fn load(proc: &Path) -> Value {
    read(&proc.join("loadavg"))
        .and_then(|t| {
            t.split_whitespace()
                .next()
                .and_then(|w| w.parse::<f64>().ok())
        })
        .map_or(Value::Null, Value::from)
}

fn mem_avail_mb(proc: &Path) -> Value {
    let text = read(&proc.join("meminfo")).unwrap_or_default();
    let kib = text
        .lines()
        .find_map(|l| l.strip_prefix("MemAvailable:"))
        .and_then(|r| r.split_whitespace().next())
        .and_then(|w| w.parse::<i64>().ok());
    kib.map_or(Value::Null, |k| Value::from(k / 1024))
}

/// The `some` total (microseconds) of each pressure-stall file, plus io's `full`.
fn stall_us(proc: &Path) -> Map<String, Value> {
    let mut out = Map::new();
    for kind in ["cpu", "io", "memory"] {
        for line in read(&proc.join("pressure").join(kind))
            .unwrap_or_default()
            .lines()
        {
            let (head, rest) = line.split_once(' ').unwrap_or((line, ""));
            let total = rest
                .split_whitespace()
                .find_map(|f| f.strip_prefix("total="))
                .and_then(|v| v.parse::<i64>().ok());
            if let (Some(total), true) = (total, head == "some" || (kind == "io" && head == "full"))
            {
                out.insert(
                    if head == "some" {
                        kind.to_owned()
                    } else {
                        "io_full".to_owned()
                    },
                    Value::from(total),
                );
            }
        }
    }
    out
}

/// One hwmon's temperatures, keyed by label.
fn temperatures(hw: &Path) -> Vec<(String, f64)> {
    let inputs = sorted_children(hw, |n| n.starts_with("temp") && n.ends_with("_input"));
    inputs
        .iter()
        .filter_map(|inp| {
            let raw = read(inp)?;
            let digits = raw.trim();
            let bare = digits.strip_prefix('-').unwrap_or(digits);
            if bare.is_empty() || !bare.chars().all(|c| c.is_ascii_digit()) {
                return None;
            }
            let name = inp
                .file_name()?
                .to_string_lossy()
                .replace("_input", "_label");
            let label = read(&inp.with_file_name(name))
                .unwrap_or_default()
                .trim()
                .to_owned();
            digits.parse::<f64>().ok().map(|v| (label, v / 1000.0))
        })
        .collect()
}

/// The coretemp package sensor, or the hottest coretemp sensor when none is labeled package.
fn cpu_temp_c(sys: &Path) -> Value {
    for hw in sorted_children(&sys.join("class/hwmon"), |n| n.starts_with("hwmon")) {
        if read(&hw.join("name")).unwrap_or_default().trim() != "coretemp" {
            continue;
        }
        let temps = temperatures(&hw);
        let package: Vec<f64> = temps
            .iter()
            .filter(|(k, _)| k.starts_with("Package"))
            .map(|(_, v)| *v)
            .collect();
        let pool: Vec<f64> = if package.is_empty() {
            temps.iter().map(|(_, v)| *v).collect()
        } else {
            package
        };
        if let Some(most) = pool.into_iter().reduce(f64::max) {
            return Value::from(most);
        }
    }
    Value::Null
}

/// Thermal-throttle time so far: core time summed over CPUs, package time from its busiest CPU.
fn throttle_ms(sys: &Path) -> Map<String, Value> {
    let (mut core, mut package, mut seen) = (0_i64, 0_i64, false);
    for cpu in sorted_children(&sys.join("devices/system/cpu"), |n| {
        n.strip_prefix("cpu")
            .is_some_and(|r| r.starts_with(|c: char| c.is_ascii_digit()))
    }) {
        let t = cpu.join("thermal_throttle");
        let number = |name: &str| read(&t.join(name)).and_then(|v| v.trim().parse::<i64>().ok());
        if let Some(c) = number("core_throttle_total_time_ms") {
            core += c;
            seen = true;
        }
        if let Some(p) = number("package_throttle_total_time_ms") {
            package = package.max(p);
            seen = true;
        }
    }
    if seen {
        Map::from_iter([
            ("core".to_owned(), Value::from(core)),
            ("package".to_owned(), Value::from(package)),
        ])
    } else {
        Map::new()
    }
}

fn now() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0.0, |d| d.as_secs_f64())
}

fn snapshot(h: &Host, t: f64) -> Value {
    json!({"t": t, "load": load(&h.proc), "mem_avail_mb": mem_avail_mb(&h.proc), "stall_us": stall_us(&h.proc), "cpu_temp_c": cpu_temp_c(&h.sys), "throttle_ms": throttle_ms(&h.sys)})
}

/// Python's `round(x, 1)`.
fn tenth(x: f64) -> f64 {
    format!("{x:.1}").parse().unwrap_or(x)
}

/// Python's `format(x, 'g')`.
fn general(x: f64) -> String {
    if x == 0.0 {
        return "0".to_owned();
    }
    let sci = format!("{x:.5e}");
    let (mantissa, exp) = sci.split_once('e').unwrap_or((&sci, "0"));
    let exp: i32 = exp.parse().unwrap_or(0);
    let trim = |s: String| {
        if s.contains('.') {
            s.trim_end_matches('0').trim_end_matches('.').to_owned()
        } else {
            s
        }
    };
    if (-4..6).contains(&exp) {
        trim(format!("{x:.*}", usize::try_from(5 - exp).unwrap_or(0)))
    } else {
        format!(
            "{}e{}{:02}",
            trim(mantissa.to_owned()),
            if exp < 0 { '-' } else { '+' },
            exp.abs()
        )
    }
}

fn append(path: &Path, text: &str) {
    use std::io::Write as _;
    if let Ok(mut f) = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(path)
    {
        let _ = f.write_all(text.as_bytes());
    }
}

fn start(dir: &Path, h: &Host) {
    let _ = std::fs::write(dir.join(START), snapshot(h, now()).to_string());
    let pre = read(&dir.join(PHASES_PRE)).unwrap_or_default();
    let _ = std::fs::write(dir.join(PHASES), pre);
    let _ = std::fs::remove_file(dir.join(PHASES_PRE));
    let _ = std::fs::remove_file(dir.join(FAILURES));
}

/// Every failure moment, how many tests failed and their ids. A test phase's own end mark is dropped when its tests left marks.
fn failure_marks(dir: &Path) -> (Vec<f64>, usize, Vec<String>) {
    let (mut tests, mut phases, mut names): (Vec<f64>, Vec<(f64, String)>, Vec<String>) =
        (Vec::new(), Vec::new(), Vec::new());
    for line in read(&dir.join(FAILURES)).unwrap_or_default().lines() {
        let (stamp, rest) = line.split_once(' ').unwrap_or((line, ""));
        let Ok(moment) = stamp.parse::<f64>() else {
            continue;
        };
        let (kind, node) = rest.split_once(' ').unwrap_or((rest, ""));
        match kind {
            "uncovered" => {
                names.push(format!("uncovered {node}"));
                phases.push((moment, "phase:coverage".to_owned()));
            }
            "test" => {
                tests.push(moment);
                if !node.is_empty() {
                    names.push(node.to_owned());
                }
            }
            _ => phases.push((moment, kind.to_owned())),
        }
    }
    let count = tests.len();
    let had_tests = count > 0;
    let mut moments = tests;
    moments.extend(
        phases
            .into_iter()
            .filter(|(_, k)| !(had_tests && (k == "phase:test-full" || k == "phase:test")))
            .map(|(m, _)| m),
    );
    (moments, count, names)
}

fn delta(before: &Value, after: &Value, scale: f64) -> Map<String, Value> {
    before
        .as_object()
        .into_iter()
        .flatten()
        .filter_map(|(k, b)| {
            Some((
                k.clone(),
                Value::from(tenth((after.get(k)?.as_f64()? - b.as_f64()?) / scale)),
            ))
        })
        .collect()
}

#[expect(
    clippy::cast_possible_truncation,
    reason = "Python's int() of a rounded millisecond count"
)]
fn whole_numbers(values: Map<String, Value>) -> Map<String, Value> {
    values
        .into_iter()
        .map(|(k, v)| (k, Value::from(v.as_f64().unwrap_or(0.0) as i64)))
        .collect()
}

fn host_fields(s: &Value, e: &Value) -> Map<String, Value> {
    let mut host = Map::new();
    for key in ["load", "mem_avail_mb", "cpu_temp_c"] {
        if !s[key].is_null() && !e[key].is_null() {
            host.insert(key.to_owned(), json!([s[key], e[key]]));
        }
    }
    let stall = delta(&s["stall_us"], &e["stall_us"], 1e6);
    if !stall.is_empty() {
        host.insert("stall_s".to_owned(), Value::Object(stall));
    }
    let throttle = delta(&s["throttle_ms"], &e["throttle_ms"], 1.0);
    if !throttle.is_empty() {
        host.insert(
            "throttle_ms".to_owned(),
            Value::Object(whole_numbers(throttle)),
        );
    }
    host
}

/// The plan's mode and reason and the tests selected and collected, from this run's selection result only.
fn this_runs_plan(dir: &Path, since: f64) -> Map<String, Value> {
    let path = dir.join(RESULT);
    let fresh = std::fs::metadata(&path)
        .and_then(|m| m.modified())
        .ok()
        .and_then(|m| m.duration_since(UNIX_EPOCH).ok())
        .is_some_and(|d| d.as_secs_f64() >= since);
    let result: Value = if fresh {
        serde_json::from_str(&read(&path).unwrap_or_default()).unwrap_or(Value::Null)
    } else {
        Value::Null
    };
    let mut out = Map::new();
    for k in ["mode", "reason"] {
        if result[k].is_string() {
            out.insert(format!("plan_{k}"), result[k].clone());
        }
    }
    for k in ["selected", "collected"] {
        match &result[k] {
            Value::Array(a) => drop(out.insert(k.to_owned(), Value::from(a.len()))),
            Value::Number(n) if n.is_i64() => drop(out.insert(k.to_owned(), result[k].clone())),
            _ => {}
        }
    }
    out
}

fn phases_of(dir: &Path) -> Map<String, Value> {
    let mut totals: BTreeMap<String, f64> = BTreeMap::new();
    let mut order: Vec<String> = Vec::new();
    for line in read(&dir.join(PHASES)).unwrap_or_default().lines() {
        let (name, secs) = line.split_once(' ').unwrap_or((line, ""));
        let Ok(s) = secs.parse::<f64>() else {
            continue;
        };
        if !totals.contains_key(name) {
            order.push(name.to_owned());
        }
        let now = tenth(totals.get(name).copied().unwrap_or(0.0) + s);
        totals.insert(name.to_owned(), now);
    }
    order
        .into_iter()
        .map(|k| {
            let v = totals[&k];
            (k, Value::from(v))
        })
        .collect()
}

fn end(dir: &Path, h: &Host) -> Value {
    let Some(raw) = read(&dir.join(START)).filter(|r| !r.is_empty()) else {
        return json!({});
    };
    let s: Value = serde_json::from_str(&raw).unwrap_or_default();
    let e = snapshot(h, now());
    let mut out = Map::new();
    let (moments, failed, names) = failure_marks(dir);
    let began = s["t"].as_f64().unwrap_or(0.0);
    if !moments.is_empty() {
        out.insert(
            "first_failure_s".to_owned(),
            Value::from(tenth(
                moments.iter().copied().fold(f64::INFINITY, f64::min) - began,
            )),
        );
        out.insert(
            "last_failure_s".to_owned(),
            Value::from(tenth(
                moments.iter().copied().fold(f64::NEG_INFINITY, f64::max) - began,
            )),
        );
    }
    if failed > 0 {
        out.insert("failed_tests".to_owned(), Value::from(failed));
    }
    if !names.is_empty() {
        out.insert(
            "failed_names".to_owned(),
            json!(names.iter().take(FAILED_NAMES_KEPT).collect::<Vec<_>>()),
        );
    }
    let host = host_fields(&s, &e);
    if !host.is_empty() {
        out.insert("host".to_owned(), Value::Object(host));
    }
    let phases = phases_of(dir);
    if !phases.is_empty() {
        out.insert("phases".to_owned(), Value::Object(phases));
    }
    out.extend(this_runs_plan(dir, began));
    Value::Object(out)
}

fn run(args: &[String], h: &Host) -> crate::Reply {
    let words: Vec<&str> = args.iter().map(String::as_str).collect();
    match words.as_slice() {
        ["start", dir, ..] => start(Path::new(dir), h),
        ["fail", dir, phase, ..] => append(
            &Path::new(dir).join(FAILURES),
            &format!("{:.3} phase:{phase}\n", now()),
        ),
        [kind @ ("phase" | "phase-pre"), dir, name, seconds, ..] => {
            let Ok(s) = seconds.parse::<f64>() else {
                return reply(String::new(), String::new(), 1);
            };
            let mut line = String::new();
            let _ = writeln!(line, "{name} {}", general(s));
            append(
                &Path::new(dir).join(if *kind == "phase" { PHASES } else { PHASES_PRE }),
                &line,
            );
        }
        ["end", dir, ..] => {
            return reply(format!("{}\n", end(Path::new(dir), h)), String::new(), 0)
        }
        _ => return reply(String::new(), USAGE.to_owned(), 2),
    }
    reply(String::new(), String::new(), 0)
}

/// `l7r-gate measure runstats ...`.
#[must_use]
pub fn cli(args: &[String]) -> crate::Reply {
    run(
        args,
        &Host {
            proc: PathBuf::from("/proc"),
            sys: PathBuf::from("/sys"),
        },
    )
}

#[cfg(test)]
mod tests;
