//! Which cohort seeds found which failure, and how few would have found them all (feature 375 amendment 8, FR-038; feature 449 T068, from
//! `cohort_seeds.py`). A fresh record's seeds are never rolled twice, so they say nothing about how few fixed seeds suffice: they are reported
//! as what they are, a failure rate on seeds the generator was never tuned on.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::Path;

use serde::Serialize as _;
use serde_json::{json, Value};

use super::{int, percent, seeds_of, text, truthy};

const PINNED: std::ops::Range<i64> = 901..907;
const FRESH_BASE: i64 = 10_000;

/// A JSON file as Python's `json.dumps(indent=1, ensure_ascii=False)` writes it, the form these records are kept in.
#[must_use]
pub fn dumped(v: &Value) -> String {
    let mut buf = Vec::new();
    let mut ser = serde_json::Serializer::with_formatter(
        &mut buf,
        serde_json::ser::PrettyFormatter::with_indent(b" "),
    );
    let _ = v.serialize(&mut ser);
    String::from_utf8_lossy(&buf).into_owned() + "\n"
}

fn is_fresh(rec: &Value) -> bool {
    truthy(&rec["fresh"]) || int(&rec["first_seed"]) >= FRESH_BASE
}

fn fresh_seeds(rec: &Value) -> Vec<&Value> {
    let whole = is_fresh(rec);
    seeds_of(rec)
        .iter()
        .filter(|s| !PINNED.contains(&int(&s["seed"])) && (whole || truthy(&s["fresh"])))
        .collect()
}

fn fresh_rate(rec: &Value) -> Value {
    let rolled = fresh_seeds(rec);
    let bad: Vec<i64> = rolled
        .iter()
        .filter(|s| {
            truthy(&s["failures"]) || (s.get("verdict").is_some() && s["verdict"] != "pass")
        })
        .map(|s| int(&s["seed"]))
        .collect();
    let first = rolled
        .iter()
        .map(|s| int(&s["seed"]))
        .min()
        .unwrap_or_default();
    let or_mark = |k: &str| {
        if rec.get(k).is_some() {
            rec[k].clone()
        } else {
            Value::from("?")
        }
    };
    json!({"utc": or_mark("utc"), "commit": or_mark("commit"), "first_seed": first, "failed": bad.len(), "rolled": rolled.len(), "seeds": bad})
}

fn change_of(rec: &Value, known: &Value) -> String {
    let feature = if truthy(&rec["feature"]) {
        text(rec, "feature")
    } else {
        known[text(rec, "commit")]
            .as_str()
            .unwrap_or_default()
            .to_owned()
    };
    if feature.is_empty() {
        format!(
            "unattributed ({})",
            if rec.get("commit").is_some() {
                text(rec, "commit")
            } else {
                "?".to_owned()
            }
        )
    } else {
        format!("feature {feature}")
    }
}

#[derive(Default)]
struct Found {
    seeds: BTreeSet<i64>,
    changes: BTreeSet<String>,
}

fn summary(records: &[Value], known: &Value) -> Value {
    let mut failures: BTreeMap<String, Found> = BTreeMap::new();
    let mut changes: BTreeSet<String> = BTreeSet::new();
    let fresh: Vec<Value> = records
        .iter()
        .filter(|r| !fresh_seeds(r).is_empty())
        .map(fresh_rate)
        .collect();
    for rec in records.iter().filter(|r| !is_fresh(r)) {
        let change = change_of(rec, known);
        changes.insert(change.clone());
        for s in seeds_of(rec).iter().filter(|x| !truthy(&x["fresh"])) {
            for f in s["failures"].as_array().map_or(&[][..], Vec::as_slice) {
                let name = f
                    .as_str()
                    .unwrap_or_default()
                    .split('[')
                    .next()
                    .unwrap_or_default()
                    .to_owned();
                let entry = failures.entry(name).or_default();
                entry.seeds.insert(int(&s["seed"]));
                entry.changes.insert(change.clone());
            }
        }
    }
    let fewest = failures
        .values()
        .filter_map(|e| {
            e.seeds
                .iter()
                .copied()
                .filter(|x| !PINNED.contains(x))
                .min()
        })
        .max()
        .unwrap_or(0);
    let only: Vec<&String> = failures
        .iter()
        .filter(|(_, v)| v.seeds.iter().all(|x| PINNED.contains(x)))
        .map(|(k, _)| k)
        .collect();
    let listed: serde_json::Map<String, Value> = failures
        .iter()
        .map(|(k, v)| (k.clone(), json!({"seeds": v.seeds, "changes": v.changes})))
        .collect();
    json!({"records": records.len(), "changes": changes, "failures": listed, "fewest first seeds finding every failure": fewest, "failures only a pinned seed found": only, "fresh": fresh})
}

fn joined(v: &Value) -> String {
    v.as_array().map_or_else(String::new, |a| {
        a.iter()
            .map(|x| x.as_str().map_or_else(|| x.to_string(), str::to_owned))
            .collect::<Vec<_>>()
            .join(", ")
    })
}

fn count(v: &Value) -> usize {
    usize::try_from(v.as_u64().unwrap_or(0)).unwrap_or(0)
}

fn render_fresh(out: &mut String, fresh: &[Value]) {
    let _ = writeln!(
        out,
        "fresh seeds (feature 386 - a rate on seeds never tuned on, never a refusal): {} record(s)",
        fresh.len()
    );
    for f in fresh {
        let _ = write!(
            out,
            "  {} {} from {}: {} of {} failed ({:.0}%)",
            text(f, "utc"),
            text(f, "commit"),
            f["first_seed"],
            f["failed"],
            f["rolled"],
            percent(count(&f["failed"]), count(&f["rolled"]))
        );
        if truthy(&f["seeds"]) {
            let _ = write!(out, " - seeds {}", joined(&f["seeds"]));
        }
        out.push('\n');
    }
    if !fresh.is_empty() {
        let (k, n): (usize, usize) = fresh.iter().fold((0, 0), |(k, n), f| {
            (k + count(&f["failed"]), n + count(&f["rolled"]))
        });
        let _ = writeln!(out, "  pooled: {k} of {n} failed ({:.0}%)", percent(k, n));
    }
}

fn render(s: &Value) -> String {
    let changes = joined(&s["changes"]);
    let mut out = format!(
        "cohort seeds: {} record(s) over {} change(s): {}\n",
        s["records"],
        s["changes"].as_array().map_or(0, Vec::len),
        if changes.is_empty() { "none" } else { &changes }
    );
    let failures = s["failures"].as_object().cloned().unwrap_or_default();
    for (name, f) in &failures {
        let _ = writeln!(
            out,
            "  {name}: seeds {} - on {}",
            joined(&f["seeds"]),
            joined(&f["changes"])
        );
    }
    if failures.is_empty() {
        out += "  no failures recorded\n";
    }
    let _ = write!(
        out,
        "the fewest first seeds that find every failure: {}",
        s["fewest first seeds finding every failure"]
    );
    let only = "failures only a pinned seed found";
    if truthy(&s[only]) {
        let _ = write!(out, " (and the pinned rows for {})", joined(&s[only]));
    }
    out.push('\n');
    render_fresh(&mut out, s["fresh"].as_array().map_or(&[], Vec::as_slice));
    out
}

fn load(log: &Path) -> (Vec<Value>, Value) {
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
    let recs = names
        .iter()
        .filter_map(|p| serde_json::from_str(&std::fs::read_to_string(p).unwrap_or_default()).ok())
        .collect();
    let known = serde_json::from_str(
        &std::fs::read_to_string(log.join("features.json")).unwrap_or_default(),
    )
    .unwrap_or(json!({}));
    (recs, known)
}

/// `l7r-gate cohort seeds [--log L] [--record FILE --key KEY]`.
pub fn cli(words: &[&str], root: &Path) -> crate::Reply {
    let flag = |name: &str| words.windows(2).find(|w| w[0] == name).map(|w| w[1]);
    let log = flag("--log").map_or_else(|| root.join("dev/cohort-log"), std::path::PathBuf::from);
    let (recs, known) = load(&log);
    let s = summary(&recs, &known);
    let stdout = render(&s);
    let Some(record) = flag("--record") else {
        return crate::Reply {
            stdout,
            stderr: String::new(),
            code: 0,
        };
    };
    let Some(key) = flag("--key") else {
        return crate::Reply {
            stdout,
            stderr: "cohort_seeds: --record needs --key\n".to_owned(),
            code: 2,
        };
    };
    let mut data: Value =
        serde_json::from_str(&std::fs::read_to_string(record).unwrap_or_default())
            .unwrap_or(json!({}));
    if data.get(key).is_none() {
        data[key] = json!({});
    }
    data[key]["value"] = s;
    let _ = std::fs::write(record, dumped(&data));
    crate::Reply {
        stdout,
        stderr: String::new(),
        code: 0,
    }
}
