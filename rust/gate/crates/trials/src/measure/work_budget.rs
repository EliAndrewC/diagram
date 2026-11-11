//! `make work-budget` on the Rust driver (feature 443; feature 444 amendment 11; feature 449 T77, from `work_budget_rust.py`).
//!
//! The driver's `hamlet --budget`, built with the counters on, counts the stages it runs. Each stage's mean counted operations at 10/20/40/80
//! households is set against its budget in `dev/work-budget.json` - per thing times the derivation's items at that size - and against an
//! accepted stage's accepted figure. `--write` replaces `dev/work-budget.md`, the standing record `work_budget_view.py` reads by header name.

use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::path::Path;
use std::process::Command;

use serde_json::{json, Map, Value};

use super::{commas, reply, text_err};
use crate::plan::pretty;

const SIZES: [i64; 4] = [10, 20, 40, 80];

/// A stage's (mean operations, rolled seeds) at each size.
type PerSize = BTreeMap<i64, (i64, i64)>;
/// Each stage in the order the driver first named it.
type Counts = Vec<(String, PerSize)>;
/// Each roll's stages, their totals and counters, by (seed, households).
type Rolls = BTreeMap<(i64, i64), Map<String, Value>>;

fn number(cell: &str, line: &str) -> Result<i64, String> {
    cell.parse()
        .map_err(|_| format!("work-budget: a driver line does not parse: {line}"))
}

/// The driver's `--budget` lines: `seed size stage ops` for a roll's stage, `seed size stage key n` for one of its counters.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn parse(stdout: &str) -> Result<(Counts, Rolls), String> {
    let mut totals: Vec<(String, BTreeMap<i64, Vec<i64>>)> = Vec::new();
    let mut rolls = Rolls::new();
    for line in stdout.lines() {
        let cells: Vec<&str> = line.split('\t').collect();
        match cells[..] {
            [seed, size, stage, ops] => {
                let (seed, size, ops) =
                    (number(seed, line)?, number(size, line)?, number(ops, line)?);
                let at = totals
                    .iter()
                    .position(|(s, _)| s == stage)
                    .unwrap_or_else(|| {
                        totals.push((stage.to_owned(), BTreeMap::new()));
                        totals.len() - 1
                    });
                totals[at].1.entry(size).or_default().push(ops);
                rolls
                    .entry((seed, size))
                    .or_default()
                    .entry(stage)
                    .or_insert_with(|| json!({"total": ops, "ops": {}}));
            }
            [seed, size, stage, key, n] => {
                let (seed, size, n) = (number(seed, line)?, number(size, line)?, number(n, line)?);
                let counters = rolls.get_mut(&(seed, size)).and_then(|r| r.get_mut(stage));
                let counters = counters
                    .ok_or_else(|| format!("work-budget: a counter before its stage: {line}"))?;
                counters["ops"][key] = json!(n);
            }
            _ => {}
        }
    }
    let counts = totals
        .into_iter()
        .map(|(stage, per)| {
            let means = per.into_iter().map(|(size, v)| {
                let rolled = i64::try_from(v.len()).unwrap_or(1);
                (size, (v.iter().sum::<i64>() / rolled, rolled))
            });
            (stage, means.collect())
        })
        .collect();
    Ok((counts, rolls))
}

/// The stage's budget at `size`: per thing times the derivation's items there, none unset.
#[must_use]
pub fn budget_at(st: &Value, size: i64) -> Option<f64> {
    Some(st.get("per_thing")?.as_f64()? * st.get(format!("items_at_{size}"))?.as_f64()?)
}

/// The measured growth from 20 to 80 households, the record's exponent column.
#[expect(
    clippy::cast_precision_loss,
    reason = "counted operations, far inside f64's exact range"
)]
#[must_use]
pub fn exponent(ops: &[i64]) -> String {
    if ops[1] != 0 && ops[3] != 0 {
        format!("{:.2}", (ops[3] as f64 / ops[1] as f64).ln() / 4f64.ln())
    } else {
        "-".to_owned()
    }
}

#[expect(
    clippy::cast_possible_truncation,
    reason = "a budget's size, far inside i64"
)]
fn whole(x: f64) -> String {
    commas(format!("{x:.0}").parse::<f64>().unwrap_or(0.0) as i64)
}

fn or_dash(x: Option<f64>) -> String {
    x.filter(|v| *v != 0.0)
        .map_or_else(|| "-".to_owned(), whole)
}

#[expect(
    clippy::cast_precision_loss,
    reason = "counted operations, far inside f64's exact range"
)]
fn ratio(ops: i64, budget: f64) -> String {
    if budget != 0.0 && ops != 0 {
        format!("{:.1}x", ops as f64 / budget)
    } else {
        "-".to_owned()
    }
}

fn cells_of(ops: &[i64]) -> Vec<String> {
    ops.iter()
        .map(|n| commas(*n))
        .chain([exponent(ops)])
        .collect()
}

/// The record's table: `work_budget_view.py` reads it by header name and takes each row's last cell as its status and the one before as its
/// ratio, so those two stay last.
#[must_use]
pub fn table(counts: &Counts, budgets: &Value) -> Vec<String> {
    let mut rows = vec![
        "| stage | ops @10 | ops @20 | ops @40 | ops @80 | exponent | budget @40 | accepted @40 | ratio | status |".to_owned(),
        format!("|{}", "---|".repeat(10)),
    ];
    let mut all = [0i64; 4];
    let mut all_budget = 0.0;
    for (stage, per) in counts {
        let st = &budgets[stage];
        let ops: Vec<i64> = SIZES
            .iter()
            .map(|s| per.get(s).map_or(0, |p| p.0))
            .collect();
        for (sum, n) in all.iter_mut().zip(&ops) {
            *sum += n;
        }
        let b40 = budget_at(st, 40);
        all_budget += b40.unwrap_or(0.0);
        let mut cells = vec![stage.clone()];
        cells.extend(cells_of(&ops));
        cells.push(or_dash(b40));
        cells.push(or_dash(st["accepted"]["40"].as_f64()));
        cells.push(ratio(ops[2], b40.unwrap_or(0.0)));
        cells.push(st["status"].as_str().unwrap_or("unbudgeted").to_owned());
        rows.push(format!("| {} |", cells.join(" | ")));
    }
    let mut cells = vec!["**the whole roll**".to_owned()];
    cells.extend(cells_of(&all));
    let shown = if all_budget == 0.0 {
        "0".to_owned()
    } else {
        whole(all_budget)
    };
    cells.extend([
        shown,
        "-".to_owned(),
        ratio(all[2], all_budget),
        "through the cut".to_owned(),
    ]);
    rows.push(format!("| {} |", cells.join(" | ")));
    rows
}

/// The stages past twice their budget at 40, read off the table as the Python's reading was.
#[must_use]
pub fn over(lines: &[String]) -> Vec<String> {
    lines[2..lines.len() - 1]
        .iter()
        .filter_map(|row| {
            let cells: Vec<&str> = row.trim_matches(['|', ' ']).split(" | ").collect();
            let times: f64 = cells[cells.len() - 2].strip_suffix('x')?.parse().ok()?;
            (times > 2.0).then(|| cells[0].to_owned())
        })
        .collect()
}

/// Every object's keys in sorted order, Python's `sort_keys`.
fn sorted(v: &Value) -> Value {
    match v {
        Value::Object(m) => {
            let by_key: BTreeMap<&String, Value> = m.iter().map(|(k, x)| (k, sorted(x))).collect();
            Value::Object(by_key.into_iter().map(|(k, x)| (k.clone(), x)).collect())
        }
        Value::Array(a) => Value::Array(a.iter().map(sorted).collect()),
        other => other.clone(),
    }
}

/// The run's JSON in the deleted roll's shape: `work_budget_view.moved` reads `summary.stages.<stage>.per.<size>.ops`, the audit bundle
/// `rows[].stages.<stage>.ops` (each counter).
#[must_use]
pub fn run_file(counts: &Counts, rolls: &Rolls, when: &str, head: &str) -> Value {
    let stage_of = |per: &PerSize| {
        let sizes: Map<String, Value> = per
            .iter()
            .map(|(s, (n, r))| (s.to_string(), json!({"ops": n, "rolled": r})))
            .collect();
        json!({"per": sizes})
    };
    let stages: Map<String, Value> = counts
        .iter()
        .map(|(k, per)| (k.clone(), stage_of(per)))
        .collect();
    let rows: Vec<Value> = rolls
        .iter()
        .map(|((seed, size), st)| json!({"seed": seed, "households": size, "stages": st}))
        .collect();
    sorted(
        &json!({"meta": {"when": when, "engine": head, "driver": "rust"}, "rows": rows, "summary": {"stages": stages}}),
    )
}

fn now() -> String {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (y, mo, d, h, mi, s) = l7r_guard::shared::log::civil(secs);
    format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z")
}

fn write(root: &Path, lines: &[String], counts: &Counts, rolls: &Rolls) -> Result<String, String> {
    let head = crate::cohort::git(root, &["rev-parse", "--short", "HEAD"])
        .1
        .trim()
        .to_owned();
    let when = now();
    let page = format!(
        "# The work budget - the standing record (feature 443)\n\nLoad this file when: you need what each stage of the hamlet roll costs in counted operations, against its budget.\n\nGenerated by `make work-budget` at {when} on engine {head} from the Rust driver (`hamlet --budget`, counters on), seeds 4, 25, 39, 47, the reference spec; each figure the mean over the seeds that rolled that size. Only the stages through the cut run (feature 444 amendment 11); the parked stages' last Python counts are in this file's git history. Budgets come from `dev/work-budget.json` (`make budget-set`).\n\n{}\n",
        lines.join("\n")
    );
    std::fs::write(root.join("dev/work-budget.md"), page).map_err(text_err)?;
    let stamp = when.replace(['-', ':'], "");
    let run = format!("dev/work-budget/{stamp}-rust-{head}.json");
    std::fs::write(
        root.join(&run),
        pretty(&run_file(counts, rolls, &when, &head)),
    )
    .map_err(text_err)?;
    Ok(format!(
        "work-budget: dev/work-budget.md and {run} written\n"
    ))
}

fn run(args: &[String], root: &Path) -> Result<String, String> {
    let file = root.join("dev/work-budget.json");
    let budgets: Value = std::fs::read_to_string(&file)
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok())
        .ok_or_else(|| format!("work-budget: {} does not read", file.display()))?;
    let done = Command::new(root.join("scripts/gates/l7r-gate.sh"))
        .args(["rust", "hamlet", "--crate"])
        .arg(root.join("rust/phases"))
        .env("HAMLET_ARGS", "--budget")
        .env("HAMLET_FEATURES", "counters")
        .output()
        .map_err(|e| format!("work-budget: the driver's budget run failed:\n{e}"))?;
    let stdout = String::from_utf8_lossy(&done.stdout);
    if !done.status.success() {
        return Err(format!(
            "work-budget: the driver's budget run failed:\n{stdout}{}",
            String::from_utf8_lossy(&done.stderr)
        ));
    }
    let (counts, rolls) = parse(&stdout)?;
    let lines = table(&counts, &budgets["stages"]);
    let mut out = lines.join("\n") + "\n";
    let past = over(&lines);
    if !past.is_empty() {
        let _ = writeln!(
            out,
            "work-budget: past twice the budget at 40 (the audit's leeway, 444 FR-022): {}",
            past.join(", ")
        );
    }
    if args.iter().any(|a| a == "--write") {
        out += &write(root, &lines, &counts, &rolls)?;
    }
    Ok(out)
}

/// `l7r-gate measure work-budget [--write]`.
#[must_use]
pub fn cli(args: &[String], root: &Path) -> crate::Reply {
    match run(args, root) {
        Ok(out) => reply(out, String::new(), 0),
        Err(why) => reply(String::new(), why + "\n", 1),
    }
}

#[cfg(test)]
mod tests;
