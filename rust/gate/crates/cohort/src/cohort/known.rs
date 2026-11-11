//! The cohort's failing seeds an open found row already names, and each seed's standing against main's engine (feature 374, the round
//! arbiter's tooling fix on `ask:w155-cohort-seed10`; feature 449 T068, from `cohort_known.py`).
//!
//! A seed that newly fails is often one a found row has already measured failing for the same reason; and a count like 59/60 hid two
//! failing seeds and a changed denominator (feature 385 T03), so a failing seed is read against its baseline, not by a total.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use super::room;
use super::{int, newest_first, records, seeds_of, text, truthy, Repo, ENGINE_PATHS};

const AUDIT: &str = "specs/328-match-the-research/audit";
static SEEDS: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)\bseeds?\s+((?:\d+(?:\s*,\s*|\s+and\s+|\s*,\s*and\s+)?)+)")
        .unwrap_or_else(|e| unreachable!("{e}"))
});
static NUMBER: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\d+").unwrap_or_else(|e| unreachable!("{e}")));

/// Every seed number a row's words list after "seed" or "seeds".
pub(super) fn seeds_named(words: &str) -> BTreeSet<i64> {
    SEEDS
        .captures_iter(words)
        .flatten()
        .flat_map(|c| {
            NUMBER
                .find_iter(&c[1])
                .flatten()
                .filter_map(|m| m.as_str().parse().ok())
                .collect::<Vec<i64>>()
        })
        .collect()
}

fn failing_seeds(record: &Value) -> Vec<i64> {
    seeds_of(record)
        .iter()
        .filter(|s| s["verdict"] != "pass")
        .map(|s| int(&s["seed"]))
        .collect()
}

fn open_rows(root: &Path) -> Vec<Value> {
    let audit = root.join(AUDIT);
    let closed: Value = serde_json::from_str(
        &std::fs::read_to_string(audit.join("waves.json")).unwrap_or_default(),
    )
    .unwrap_or_default();
    let mut names: Vec<_> = std::fs::read_dir(&audit)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| {
            p.file_name().is_some_and(|n| {
                n.to_string_lossy().starts_with("found-") && n.to_string_lossy().ends_with(".jsonl")
            })
        })
        .collect();
    names.sort();
    names
        .iter()
        .flat_map(|p| {
            std::fs::read_to_string(p)
                .unwrap_or_default()
                .lines()
                .filter_map(|l| serde_json::from_str::<Value>(l).ok())
                .collect::<Vec<_>>()
        })
        .filter(|r| truthy(&r["key"]) && closed.get(text(r, "key")).is_none())
        .collect()
}

fn known(root: &Path, record: &Value) -> Vec<String> {
    let word = |r: &Value, k: &str| {
        if truthy(&r[k]) {
            text(r, k)
        } else {
            String::new()
        }
    };
    let rows: Vec<(Value, BTreeSet<i64>)> = open_rows(root)
        .into_iter()
        .map(|r| {
            let named = seeds_named(&format!("{} {}", word(&r, "fix"), word(&r, "found")));
            (r, named)
        })
        .collect();
    let mut out = Vec::new();
    for seed in failing_seeds(record) {
        for (r, named) in &rows {
            if named.contains(&seed) {
                let tier = if r.get("tier").is_some() {
                    text(r, "tier")
                } else {
                    "?".to_owned()
                };
                out.push(format!("cohort: seed {seed} is named by an open found row - {} ({tier}); go to that row before probing", text(r, "key")));
            }
        }
    }
    out
}

/// Each seed's baseline: its entry in the newest earlier record, rolled at the same household count on main's engine.
pub fn baselines<'r>(
    record: &Value,
    earlier: &'r [Value],
    ok: &dyn Fn(&str) -> bool,
) -> BTreeMap<i64, &'r Value> {
    let mut out = BTreeMap::new();
    for r in newest_first(earlier) {
        if text(r, "utc") >= text(record, "utc")
            || r["households"] != record["households"]
            || !truthy(&r["commit"])
            || truthy(&r["engine_diff"])
            || !ok(&text(r, "commit"))
        {
            continue;
        }
        for b in seeds_of(r) {
            out.entry(int(&b["seed"])).or_insert(b);
        }
    }
    out
}

fn failures_of(x: &Value) -> Vec<String> {
    x["failures"].as_array().map_or_else(Vec::new, |a| {
        a.iter()
            .map(|f| f.as_str().map_or_else(|| f.to_string(), str::to_owned))
            .collect()
    })
}

/// `rule count, ...` sorted by rule, else the failures' names.
fn rules_of(x: &Value) -> String {
    let counts: BTreeMap<&String, &Value> = x["counts"]
        .as_object()
        .map_or_else(BTreeMap::new, |o| o.iter().collect());
    if counts.is_empty() {
        failures_of(x).join(", ")
    } else {
        counts
            .iter()
            .map(|(k, v)| format!("{k} {v}"))
            .collect::<Vec<_>>()
            .join(", ")
    }
}

/// Did a rule's count go up, or a rule appear, against the baseline?
fn worsened(x: &Value, b: &Value) -> bool {
    let up = b["counts"].is_object()
        && x["counts"].as_object().is_some_and(|o| {
            o.iter()
                .any(|(k, v)| v.as_f64().unwrap_or(0.0) > b["counts"][k].as_f64().unwrap_or(0.0))
        });
    let before = failures_of(b);
    up || failures_of(x).iter().any(|f| !before.contains(f))
}

/// One line per seed that fails now or failed at its baseline.
#[must_use]
pub fn standing(record: &Value, base: &BTreeMap<i64, &Value>) -> Vec<String> {
    let mut out = Vec::new();
    for x in seeds_of(record).iter().filter(|y| !truthy(&y["fresh"])) {
        let n = int(&x["seed"]);
        let now_bad = x["verdict"] != "pass";
        let rules = rules_of(x);
        let Some(b) = base.get(&n) else {
            if now_bad {
                out.push(format!("cohort: seed {n} fails ({rules}) with NO BASELINE on main's engine - roll one: git worktree add --detach /tmp/base origin/main && make -C /tmp/base cohort N=1 SEED={n}"));
            }
            continue;
        };
        let was_bad = b["verdict"] != "pass";
        let was = rules_of(b);
        if !now_bad && was_bad {
            out.push(format!("cohort: seed {n} FIXED (was: {was})"));
        } else if now_bad && !was_bad {
            out.push(format!("cohort: seed {n} NEWLY FAILING ({rules})"));
        } else if now_bad {
            out.push(format!(
                "cohort: seed {n} {} ({rules}; was: {was})",
                if worsened(x, b) {
                    "WORSENED"
                } else {
                    "PRE-EXISTING"
                }
            ));
        }
    }
    out
}

/// The seeds `record` fails that passed in the newest earlier record on main rolling the same seed and households.
pub(super) fn newly_failing(
    record: &Value,
    earlier: &[Value],
    on_main: &dyn Fn(&str) -> bool,
) -> Vec<i64> {
    let sorted = newest_first(earlier);
    let mut out = Vec::new();
    for s in seeds_of(record).iter().filter(|s| s["verdict"] != "pass") {
        for r in &sorted {
            if text(r, "utc") >= text(record, "utc") || r["households"] != record["households"] {
                continue;
            }
            let Some(base) = seeds_of(r).iter().find(|b| b["seed"] == s["seed"]) else {
                continue;
            };
            if !truthy(&r["commit"]) || truthy(&r["engine_diff"]) || !on_main(&text(r, "commit")) {
                continue;
            }
            if base["verdict"] == "pass" {
                out.push(int(&s["seed"]));
            }
            break;
        }
    }
    out
}

/// A seed newly failing owes the active task's part B, a fit failure printing the room table beside it (405 T113).
fn approach_owed(repo: &Repo<'_>, recs: &[Value]) -> String {
    let Some((last, earlier)) = recs.split_last() else {
        return String::new();
    };
    let seeds = newly_failing(last, earlier, &|c| repo.same_engine(c));
    if seeds.is_empty() {
        return String::new();
    }
    let listed = seeds
        .iter()
        .map(i64::to_string)
        .collect::<Vec<_>>()
        .join(", ");
    let trigger = format!(
        "cohort@{}: seed(s) {listed} newly failing",
        text(last, "utc")
    );
    let Some(mut owed) = crate::plan::owe_in_flight(repo.root, &trigger, "B") else {
        return String::new();
    };
    let fit = seeds_of(last).iter().any(|r| {
        seeds.contains(&int(&r["seed"]))
            && room::is_fit(r["failures"].as_array().map_or(&[], Vec::as_slice))
    });
    if fit {
        let _ = write!(owed, "\n{}", room::table(repo.root));
    }
    owed
}

/// Mark the newest record rolled over an uncommitted engine diff with that tree's engine key, so it is never read as its commit's baseline.
fn stamp(repo: &Repo<'_>) -> String {
    let log = repo.root.join("dev/cohort-log");
    let mut names: Vec<_> = std::fs::read_dir(&log)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| {
            p.file_name().is_some_and(|n| {
                n.to_string_lossy()
                    .starts_with(|c: char| c.is_ascii_digit())
                    && n.to_string_lossy().ends_with(".json")
            })
        })
        .collect();
    names.sort();
    let Some(newest) = names.last() else {
        return String::new();
    };
    let now = repo.engine_key(None);
    if now == repo.engine_key(Some("HEAD")) {
        return String::new();
    }
    let digest: String = now.chars().take(16).collect();
    let Ok(mut rec) =
        serde_json::from_str::<Value>(&std::fs::read_to_string(newest).unwrap_or_default())
    else {
        return String::new();
    };
    rec["engine_diff"] = Value::String(digest.clone());
    let _ = std::fs::write(newest, crate::cohort::seeds::dumped(&rec));
    digest
}

fn say(stdout: String) -> crate::Reply {
    crate::Reply {
        stdout,
        stderr: String::new(),
        code: 0,
    }
}

/// `l7r-gate cohort known [--root R] [--stamp]`.
pub fn cli(words: &[&str], repo: &Repo<'_>) -> crate::Reply {
    let root = words
        .windows(2)
        .find(|w| w[0] == "--root")
        .map(|w| Path::new(w[1]));
    let here = root.map(|r| Repo::new(r, repo.python));
    let repo = here.as_ref().unwrap_or(repo);
    if words.contains(&"--stamp") {
        let digest = stamp(repo);
        return say(if digest.is_empty() {
            String::new()
        } else {
            format!("cohort: rolled over an uncommitted engine diff ({digest}) - recorded so, never read as {ENGINE_PATHS:?} at its commit\n")
        });
    }
    let recs = records(repo.root);
    repo.prime_records(&recs);
    let mut out = String::new();
    if let Some((last, earlier)) = recs.split_last() {
        for line in known(repo.root, last).into_iter().chain(standing(
            last,
            &baselines(last, earlier, &|c| repo.same_engine(c)),
        )) {
            let _ = writeln!(out, "{line}");
        }
    }
    let owed = approach_owed(repo, &recs);
    if !owed.is_empty() {
        let _ = writeln!(out, "{owed}");
    }
    say(out)
}
