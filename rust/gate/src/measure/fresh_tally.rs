//! How often a seed nobody has used fails, by settlement form and by cause (feature 417 T01; feature 449 T76, from `fresh_tally.py`). The fixed
//! cohort passes because it is the landing gate; the real failure rate is on seeds the generator was never tuned on.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::Path;

use serde_json::Value;

use super::reply;
use crate::cohort::{int, percent, text, truthy};

const FRESH_BASE: i64 = 10_000;

fn is_fresh_seed(rec: &Value, seed: &Value) -> bool {
    let whole = truthy(&rec["fresh"]) || int(&rec["first_seed"]) >= FRESH_BASE;
    !(901..907).contains(&int(&seed["seed"])) && (whole || truthy(&seed["fresh"]))
}

fn load(log: &Path) -> Vec<Value> {
    let mut names: Vec<_> = std::fs::read_dir(log)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| {
            p.extension().is_some_and(|x| x == "json")
                && p.file_name().is_some_and(|n| n != "features.json")
        })
        .collect();
    names.sort();
    names
        .iter()
        .filter_map(|p| serde_json::from_str(&std::fs::read_to_string(p).ok()?).ok())
        .collect()
}

fn failed(seed: &Value) -> bool {
    truthy(&seed["failures"]) || (seed.get("verdict").is_some() && seed["verdict"] != "pass")
}

/// A failure's cause without its count: `lane_knots 2` and `lane_knots` are one cause.
fn cause(name: &Value) -> String {
    let text = name.as_str().map_or_else(
        || {
            name.get("check").map_or_else(
                || name.to_string(),
                |c| c.as_str().map_or_else(|| c.to_string(), str::to_owned),
            )
        },
        str::to_owned,
    );
    text.split(' ').next().unwrap_or_default().to_owned()
}

/// Each fresh seed once per engine commit, from the latest record that rolled it.
fn pooled<'a>(
    records: &'a [Value],
    commit: &str,
    since: &str,
) -> BTreeMap<(String, i64), &'a Value> {
    let mut sorted: Vec<&Value> = records.iter().collect();
    sorted.sort_by_key(|r| r["utc"].as_str().unwrap_or_default().to_owned());
    let mut out = BTreeMap::new();
    for rec in sorted {
        let at = rec["commit"].as_str().unwrap_or_default();
        if !at.starts_with(commit)
            || (!since.is_empty() && rec["utc"].as_str().unwrap_or_default() < since)
        {
            continue;
        }
        for seed in rec["seeds"].as_array().map_or(&[][..], Vec::as_slice) {
            if is_fresh_seed(rec, seed) {
                out.insert((at.to_owned(), int(&seed["seed"])), seed);
            }
        }
    }
    out
}

fn pct(a: usize, b: usize) -> String {
    if b == 0 {
        "-".to_owned()
    } else {
        format!("{:.0}%", percent(a, b))
    }
}

fn render(seeds: &[&Value]) -> String {
    let mut forms: Vec<(String, usize, usize)> = Vec::new();
    let mut causes: BTreeMap<String, usize> = BTreeMap::new();
    for s in seeds {
        let form = if truthy(&s["form"]) {
            text(s, "form")
        } else {
            "?".to_owned()
        };
        let at = forms.iter().position(|f| f.0 == form).unwrap_or_else(|| {
            forms.push((form, 0, 0));
            forms.len() - 1
        });
        forms[at].2 += 1;
        if failed(s) {
            forms[at].1 += 1;
            let names: BTreeSet<String> = match s["failures"].as_array().filter(|a| !a.is_empty()) {
                Some(list) => list.iter().map(cause).collect(),
                None => BTreeSet::from([format!("verdict {}", text(s, "verdict"))
                    .split(' ')
                    .next()
                    .unwrap_or_default()
                    .to_owned()]),
            };
            for name in names {
                *causes.entry(name).or_default() += 1;
            }
        }
    }
    forms.sort_by_key(|f| std::cmp::Reverse(f.2));
    let bad = seeds.iter().filter(|s| failed(s)).count();
    let mut out = format!(
        "fresh seeds: {bad} of {} failed ({})\n\nby form:\n",
        seeds.len(),
        pct(bad, seeds.len())
    );
    for (form, n, m) in &forms {
        let _ = writeln!(out, "  {form:11} {n} of {m} ({})", pct(*n, *m));
    }
    out += "\nby cause (a seed may fail more than one):\n";
    let mut named: Vec<(String, usize)> = causes.into_iter().collect();
    named.sort_by_key(|c| std::cmp::Reverse(c.1));
    if named.is_empty() {
        out += "  none\n";
    }
    for (name, n) in named {
        let _ = writeln!(out, "  {n:5}  {name}");
    }
    out
}

/// `l7r-gate measure fresh-tally [--log D] [--commit SHA] [--since UTC]`.
pub(crate) fn cli(args: &[String], root: &Path) -> crate::Reply {
    let flag = |name: &str| {
        args.windows(2)
            .find(|w| w[0] == name)
            .map(|w| w[1].as_str())
    };
    let log = flag("--log").map_or_else(|| root.join("dev/cohort-log"), std::path::PathBuf::from);
    let records = load(&log);
    let pool = pooled(
        &records,
        flag("--commit").unwrap_or(""),
        flag("--since").unwrap_or(""),
    );
    let seeds: Vec<&Value> = pool.into_values().collect();
    reply(render(&seeds), String::new(), 0)
}

#[cfg(test)]
mod tests;
