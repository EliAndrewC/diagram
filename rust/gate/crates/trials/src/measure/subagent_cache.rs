//! What subagents write to the prompt cache fresh, and what they could have read from it (feature 383 amendment 6, FR-036; feature 449 T76, from
//! `subagent_cache.py`). A prompt is cached as a prefix, so what every dispatch of a check shares is read from the cache only while nothing
//! that differs comes before it: this asks of the transcripts where each type's tokens are written against read.

use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use super::reply;

const RATE_WRITE: f64 = 1.25;
const RATE_READ: f64 = 0.1;
const RATE_INPUT: f64 = 1.0;
const RATE_OUTPUT: f64 = 5.0;
/// A dispatch this soon after one of its type in the same session finds that one's prefix cached.
const WINDOW_S: f64 = 300.0;
/// A manifest line counts toward repeated text from this length: shorter ones are headings and separators.
const LINE_MIN: usize = 40;

static NUMBERS: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"[0-9]+").unwrap_or_else(|e| unreachable!("{e}")));
static WORDS: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"[a-z][a-z-]*").unwrap_or_else(|e| unreachable!("{e}")));

/// One subagent run.
struct Run {
    kind: String,
    session: String,
    start: String,
    calls: Vec<Value>,
    manifest: String,
    description: String,
}

fn body_text(body: &Value) -> String {
    match body {
        Value::String(s) => s.clone(),
        Value::Array(a) => a
            .iter()
            .map(|b| b["text"].as_str().unwrap_or_default())
            .collect(),
        _ => String::new(),
    }
}

/// A general-purpose launch's family: its description's first two words, numbers dropped.
fn family(description: &str) -> String {
    let bare = NUMBERS
        .replace_all(&description.to_lowercase(), " ")
        .into_owned();
    let words: Vec<String> = WORDS
        .find_iter(&bare)
        .flatten()
        .take(2)
        .map(|m| m.as_str().to_owned())
        .collect();
    if words.is_empty() {
        "?".to_owned()
    } else {
        words.join(" ")
    }
}

fn run_of(path: &Path) -> Option<Run> {
    let name = path.file_name()?.to_string_lossy();
    let meta_path = path.with_file_name(format!("{}.meta.json", name.strip_suffix(".jsonl")?));
    let info: Value = serde_json::from_str(&std::fs::read_to_string(meta_path).ok()?).ok()?;
    let text = String::from_utf8_lossy(&std::fs::read(path).ok()?).into_owned();
    let (mut start, mut calls, mut seen, mut manifest, mut pending) = (
        String::new(),
        Vec::new(),
        BTreeSet::new(),
        String::new(),
        BTreeSet::new(),
    );
    for d in text
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        .filter(Value::is_object)
    {
        if start.is_empty() {
            d["timestamp"]
                .as_str()
                .unwrap_or_default()
                .clone_into(&mut start);
        }
        let m = &d["message"];
        let rid = d["requestId"]
            .as_str()
            .or(m["id"].as_str())
            .unwrap_or_default()
            .to_owned();
        if truthy_object(&m["usage"]) && seen.insert(rid) {
            calls.push(m["usage"].clone());
        }
        for b in m["content"]
            .as_array()
            .map_or(&[][..], Vec::as_slice)
            .iter()
            .filter(|b| b.is_object())
        {
            if b["type"] == "tool_use"
                && b["name"] == "Read"
                && b["input"]["file_path"]
                    .as_str()
                    .is_some_and(|f| f.ends_with("MANIFEST.md"))
            {
                pending.insert(b["id"].to_string());
            }
            if b["type"] == "tool_result"
                && pending.contains(&b["tool_use_id"].to_string())
                && manifest.is_empty()
            {
                manifest = body_text(&b["content"]);
            }
        }
    }
    if calls.is_empty() || start.is_empty() {
        return None;
    }
    let kind = info["agentType"]
        .as_str()
        .filter(|s| !s.is_empty())
        .unwrap_or("?")
        .to_owned();
    let session = path
        .parent()?
        .parent()?
        .file_name()?
        .to_string_lossy()
        .into_owned();
    Some(Run {
        kind,
        session,
        start,
        calls,
        manifest,
        description: info["description"].as_str().unwrap_or_default().to_owned(),
    })
}

fn truthy_object(v: &Value) -> bool {
    v.as_object().is_some_and(|o| !o.is_empty())
}

fn runs(root: &Path, since: &str) -> Vec<Run> {
    let mut files: Vec<PathBuf> = std::fs::read_dir(root)
        .into_iter()
        .flatten()
        .flatten()
        .flat_map(|s| {
            std::fs::read_dir(s.path().join("subagents"))
                .into_iter()
                .flatten()
                .flatten()
                .map(|e| e.path())
                .collect::<Vec<_>>()
        })
        .filter(|p| {
            let n = p.file_name().unwrap_or_default().to_string_lossy();
            n.starts_with("agent-") && n.ends_with(".jsonl")
        })
        .collect();
    files.sort();
    let mut out: Vec<Run> = files
        .iter()
        .filter_map(|f| run_of(f))
        .filter(|r| r.start.as_str() >= since)
        .collect();
    out.sort_by(|a, b| a.start.cmp(&b.start));
    out
}

/// Seconds since the epoch of an ISO time with its zone.
#[must_use]
pub fn at(stamp: &str) -> f64 {
    let digits: Vec<f64> = stamp
        .split(|c: char| !c.is_ascii_digit() && c != '.')
        .filter(|s| !s.is_empty())
        .filter_map(|s| s.parse().ok())
        .collect();
    if digits.len() < 6 {
        return 0.0;
    }
    #[expect(clippy::cast_possible_truncation, reason = "a calendar's parts, small")]
    let (year, month, day) = (digits[0] as i64, digits[1] as i64, digits[2] as i64);
    let (shifted_year, shifted_month) = if month <= 2 {
        (year - 1, month + 9)
    } else {
        (year, month - 3)
    };
    let era = shifted_year.div_euclid(400);
    let year_of_era = shifted_year - era * 400;
    let day_of_year = (153 * shifted_month + 2) / 5 + day - 1;
    let day_of_era = year_of_era * 365 + year_of_era / 4 - year_of_era / 100 + day_of_year;
    #[expect(
        clippy::cast_precision_loss,
        reason = "days since the epoch, far inside f64's exact range"
    )]
    let days = (era * 146_097 + day_of_era - 719_468) as f64;
    days * 86_400.0 + digits[3] * 3600.0 + digits[4] * 60.0 + digits[5]
}

/// Per type, the runs made under the window after one of their type in the same session.
fn back_to_back(rs: &[Run]) -> HashMap<String, Vec<&Run>> {
    let mut last: HashMap<(String, String), f64> = HashMap::new();
    let mut out: HashMap<String, Vec<&Run>> = HashMap::new();
    for r in rs {
        let key = (r.session.clone(), r.kind.clone());
        let t = at(&r.start);
        if last.get(&key).is_some_and(|prev| t - prev < WINDOW_S) {
            out.entry(r.kind.clone()).or_default().push(r);
        }
        last.insert(key, t);
    }
    out
}

fn long_lines(text: &str) -> BTreeSet<String> {
    text.lines()
        .map(|raw| {
            let head: String = raw.chars().take(12).collect();
            if head.contains('\t') {
                raw.split_once('\t').map_or(raw, |(_, r)| r).trim()
            } else {
                raw.trim()
            }
        })
        .filter(|l| l.chars().count() >= LINE_MIN)
        .map(str::to_owned)
        .collect()
}

/// Characters of the lines at least 80% of the manifests hold.
fn repeated(manifests: &[&str]) -> usize {
    if manifests.len() < 2 {
        return 0;
    }
    let mut counts: BTreeMap<String, usize> = BTreeMap::new();
    for m in manifests {
        for line in long_lines(m) {
            *counts.entry(line).or_default() += 1;
        }
    }
    #[expect(clippy::cast_precision_loss, reason = "a count of manifests")]
    let need = 0.8 * manifests.len() as f64;
    #[expect(clippy::cast_precision_loss, reason = "a count of manifests")]
    counts
        .iter()
        .filter(|(_, n)| **n as f64 >= need)
        .map(|(l, _)| l.chars().count())
        .sum()
}

fn field(calls: &[Value], key: &str) -> i64 {
    calls.iter().map(|c| c[key].as_i64().unwrap_or(0)).sum()
}

/// (written, read, output, units).
#[expect(
    clippy::cast_precision_loss,
    reason = "token counts, far inside f64's exact range"
)]
fn spend(rs: &[&Run]) -> (i64, i64, i64, f64) {
    let (mut write, mut read, mut input, mut output) = (0, 0, 0, 0);
    for r in rs {
        write += field(&r.calls, "cache_creation_input_tokens");
        read += field(&r.calls, "cache_read_input_tokens");
        input += field(&r.calls, "input_tokens");
        output += field(&r.calls, "output_tokens");
    }
    (
        write,
        read,
        output,
        write as f64 * RATE_WRITE
            + read as f64 * RATE_READ
            + input as f64 * RATE_INPUT
            + output as f64 * RATE_OUTPUT,
    )
}

fn first_call(rs: &[&Run], key: &str) -> i64 {
    if rs.is_empty() {
        return 0;
    }
    let total: i64 = rs
        .iter()
        .map(|r| r.calls[0][key].as_i64().unwrap_or(0))
        .sum();
    total.div_euclid(i64::try_from(rs.len()).unwrap_or(1))
}

#[must_use]
pub fn commas(n: i64) -> String {
    let digits = n.abs().to_string();
    let mut out = String::new();
    for (i, c) in digits.chars().enumerate() {
        if i > 0 && (digits.len() - i) % 3 == 0 {
            out.push(',');
        }
        out.push(c);
    }
    if n < 0 {
        format!("-{out}")
    } else {
        out
    }
}

#[expect(
    clippy::cast_possible_truncation,
    reason = "a whole number of units for display"
)]
fn report(rs: &[Run]) -> String {
    let pairs = back_to_back(rs);
    let mut by: Vec<(String, Vec<&Run>)> = Vec::new();
    for r in rs {
        let at_ = by
            .iter()
            .position(|(k, _)| *k == r.kind)
            .unwrap_or_else(|| {
                by.push((r.kind.clone(), Vec::new()));
                by.len() - 1
            });
        by[at_].1.push(r);
    }
    by.sort_by(|a, b| spend(&b.1).3.total_cmp(&spend(&a.1).3));
    let mut out = format!(
        "{:24} {:>5} {:>4} {:>9} {:>9} {:>9} {:>10}\n",
        "type", "runs", "b2b", "1st read", "1st write", "repeated", "units/run"
    );
    for (kind, krs) in &by {
        let empty = Vec::new();
        let p = pairs.get(kind).unwrap_or(&empty);
        let manifests: Vec<&str> = krs
            .iter()
            .map(|r| r.manifest.as_str())
            .filter(|m| !m.is_empty())
            .collect();
        #[expect(clippy::cast_precision_loss, reason = "a count of runs")]
        let per = spend(krs).3 / krs.len() as f64;
        let cut: String = kind.chars().take(24).collect();
        let _ = writeln!(
            out,
            "{cut:24} {:>5} {:>4} {:>9} {:>9} {:>9} {:>10.0}",
            krs.len(),
            p.len(),
            first_call(p, "cache_read_input_tokens"),
            first_call(p, "cache_creation_input_tokens"),
            repeated(&manifests),
            per
        );
    }
    let every: Vec<&Run> = rs.iter().collect();
    let (write, read, output, units) = spend(&every);
    let _ = writeln!(out, "\nall: {} runs; written {}, read {}, output {} tokens = {} base-input units (a write {RATE_WRITE}x, a read {RATE_READ}x, output {RATE_OUTPUT:.1}x: the 5-minute tier)", rs.len(), commas(write), commas(read), commas(output), commas(units.round() as i64));
    out + "b2b = dispatches under 5 minutes after one of their type in the same session; '1st write' is what such a one still wrote fresh (a defined agent: ~2.5-3.5k - its prompt and the environment block). 'repeated' = characters in 80% of its manifests: that text belongs in the agent's file (CLAUDE.md, the review checks)."
}

/// (family, launches, launches since `recent`, last date, an example), most since `recent` first.
fn families(rs: &[Run], recent: &str) -> Vec<(String, usize, usize, String, String)> {
    let mut out: Vec<(String, usize, usize, String, String)> = Vec::new();
    for r in rs
        .iter()
        .filter(|r| r.kind == "general-purpose" || r.kind == "?")
    {
        let name = family(&r.description);
        let at_ = out.iter().position(|e| e.0 == name).unwrap_or_else(|| {
            out.push((name, 0, 0, String::new(), r.description.clone()));
            out.len() - 1
        });
        out[at_].1 += 1;
        out[at_].2 += usize::from(r.start.as_str() >= recent);
        let day: String = r.start.chars().take(10).collect();
        if day > out[at_].3 {
            out[at_].3 = day;
        }
    }
    out.sort_by_key(|e| (std::cmp::Reverse(e.2), std::cmp::Reverse(e.1)));
    out
}

/// `l7r-gate measure subagent-cache [--since D] [--root D] [--families RECENT]`.
pub fn cli(args: &[String], home: &Path, today: &str) -> crate::Reply {
    let flag = |name: &str| {
        args.windows(2)
            .find(|w| w[0] == name)
            .map(|w| w[1].as_str())
    };
    let since = flag("--since").unwrap_or(today);
    let root = flag("--root").map_or_else(|| home.join(".claude/projects/-diagram"), PathBuf::from);
    let rs = runs(&root, since);
    if rs.is_empty() {
        return reply(
            format!(
                "subagent-cache: no subagent runs under {} since {since}\n",
                root.display()
            ),
            String::new(),
            0,
        );
    }
    if let Some(recent) = flag("--families") {
        let mut out = format!("subagent-cache: general-purpose launches since {since} by family (launches | since {recent} | last | e.g.)\n\n");
        for (name, n, fresh, last, example) in families(&rs, recent) {
            let short: String = example.chars().take(60).collect();
            let _ = writeln!(out, "{n:5} {fresh:5} {last}  {name:28} {short}");
        }
        return reply(out, String::new(), 0);
    }
    reply(
        format!(
            "subagent-cache: subagent runs since {since}\n\n{}\n",
            report(&rs)
        ),
        String::new(),
        0,
    )
}

#[cfg(test)]
mod tests;
