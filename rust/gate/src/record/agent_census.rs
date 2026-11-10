//! What each subagent check has cost, read from the session transcripts (feature 251, FR-001; feature 449 T79, from `agent_census.py`).
//!
//! The GM asked on 2026-09-19 whether the subagent checks could cost fewer tokens "without a loss of quality with different levels of models involved",
//! and the first step was to measure which agents the tokens go to. Claude Code writes one transcript per subagent run at
//! `~/.claude/projects/<project>/<session>/subagents/agent-<id>.jsonl`, with `agent-<id>.meta.json` beside it naming the agent type.
//!
//! The fold over a run's records is `model_trial::fold_usage`, the one implementation (`ask:449-T77-replays`). The dispatch's own `model` field is an
//! OVERRIDE and absent on most runs, so the model a run used is read from the assistant records, never from the meta.

use std::cmp::Reverse;
use std::path::{Path, PathBuf};

use serde_json::{json, Map, Value};

use super::{first_chars, py_lines, reply};
use crate::cohort::{int, text, truthy};
use crate::logs::py_dumps;
use crate::measure::model_trial::{children, fold_usage, named};
use crate::measure::subagent_cache::commas;
use crate::Reply;

/// Agent types with no file under `.claude/agents/`: a dispatch of one inherits the session's model unless it names one, which the ad-hoc block reports (spec FR-010).
const BUILTIN: [&str; 7] = [
    "general-purpose",
    "claude",
    "Explore",
    "Plan",
    "fork",
    "claude-code-guide",
    "statusline-setup",
];
const USAGE: &str = "usage: l7r-gate record agent-census [--root DIR] [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--json FILE] [--record FILE]\n";

/// A Counter in insertion order.
type Counts = Vec<(String, i64)>;

#[derive(Default)]
struct Row {
    agent: String,
    runs: i64,
    turns: i64,
    fresh: i64,
    cached: i64,
    output: i64,
    thinking: i64,
    models: Counts,
}

#[derive(Default)]
struct Adhoc {
    agent: String,
    runs: i64,
    no_model: i64,
    inherited: Counts,
}

fn tally(counts: &mut Counts, key: &str) {
    match counts.iter_mut().find(|(k, _)| k == key) {
        Some(hit) => hit.1 += 1,
        None => counts.push((key.to_owned(), 1)),
    }
}

/// `Counter.most_common()`: by count, ties in insertion order.
fn most_common(counts: &mut Counts) {
    counts.sort_by_key(|c| Reverse(c.1));
}

fn entry<T>(list: &mut Vec<T>, same: impl Fn(&T) -> bool, make: impl FnOnce() -> T) -> &mut T {
    let at = list.iter().position(same).unwrap_or_else(|| {
        list.push(make());
        list.len() - 1
    });
    &mut list[at]
}

/// `(meta, folded usage)` of one subagent transcript; a line that is not JSON is skipped. Split as Python's `splitlines` splits, so a raw U+2028 inside a record costs that record, as it did.
fn read_run(transcript: &Path) -> (Value, Value) {
    let meta = std::fs::read_to_string(transcript.with_extension("").with_extension("meta.json"))
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok())
        .unwrap_or_else(|| json!({}));
    let bytes = std::fs::read(transcript).unwrap_or_default();
    let body = String::from_utf8_lossy(&bytes);
    let records: Vec<Value> = py_lines(&body)
        .into_iter()
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect();
    (meta, fold_usage(&records))
}

/// Every subagent transcript of this repository's sessions: the mirror's project and its clones'.
fn transcripts(root: &Path) -> Vec<PathBuf> {
    let mut found = Vec::new();
    for project in children(root) {
        if !project
            .file_name()
            .is_some_and(|n| n == "-diagram" || n.to_string_lossy().starts_with("-diagram-"))
        {
            continue;
        }
        for session in children(&project) {
            found.extend(
                children(&session.join("subagents"))
                    .into_iter()
                    .filter(|p| named(p, "agent-", ".jsonl")),
            );
        }
    }
    found
}

/// `(one row per agent type, one row per ad-hoc type)`, `since` inclusive and `until` exclusive against each run's first timestamp; `until` is what makes a recorded census re-runnable, since the transcripts only grow.
fn rows(runs: &[(Value, Value)], since: &str, until: &str) -> (Vec<Row>, Vec<Adhoc>) {
    let (mut table, mut adhoc): (Vec<Row>, Vec<Adhoc>) = (Vec::new(), Vec::new());
    for (meta, usage) in runs {
        let started = usage["started"].as_str().unwrap_or("");
        let prefix = |bound: &str| first_chars(started, bound.chars().count());
        if !since.is_empty() && prefix(since).as_str() < since {
            continue;
        }
        if !until.is_empty() && prefix(until).as_str() >= until {
            continue;
        }
        let kind = if truthy(&meta["agentType"]) {
            text(meta, "agentType")
        } else {
            "unknown".to_owned()
        };
        let model = usage["model"].as_str().unwrap_or("");
        let row = entry(
            &mut table,
            |r| r.agent == kind,
            || Row {
                agent: kind.clone(),
                ..Row::default()
            },
        );
        row.runs += 1;
        row.turns += int(&usage["turns"]);
        row.fresh += int(&usage["fresh"]);
        row.cached += int(&usage["cached"]);
        row.output += int(&usage["output"]);
        row.thinking += int(&usage["thinking"]);
        tally(&mut row.models, model);
        if BUILTIN.contains(&kind.as_str()) {
            let ad = entry(
                &mut adhoc,
                |a| a.agent == kind,
                || Adhoc {
                    agent: kind.clone(),
                    ..Adhoc::default()
                },
            );
            ad.runs += 1;
            if !truthy(&meta["model"]) || text(meta, "model").to_lowercase() == "inherit" {
                ad.no_model += 1;
                tally(&mut ad.inherited, model);
            }
        }
    }
    table.sort_by_key(|r| Reverse(r.fresh + r.cached));
    table.iter_mut().for_each(|r| most_common(&mut r.models));
    adhoc.sort_by_key(|a| Reverse(a.runs));
    adhoc.iter_mut().for_each(|a| most_common(&mut a.inherited));
    (table, adhoc)
}

/// `round(a / b)`: Python's half-to-even, for a count over a positive count.
fn rounded(a: i64, b: i64) -> i64 {
    let (q, r) = (a / b, a % b);
    q + i64::from(2 * r > b || (2 * r == b && q % 2 == 1))
}

fn joined(counts: &Counts) -> String {
    let shown: Vec<String> = counts.iter().map(|(m, c)| format!("{m} x{c}")).collect();
    shown.join(", ")
}

/// The census as text: totals per agent type, per-run means, the models used, the ad-hoc block.
fn render(table: &[Row], adhoc: &[Adhoc]) -> String {
    let head = format!(
        "{:<22}{:>6}{:>8}{:>14}{:>16}{:>12}{:>11}{:>12}{:>10}  models",
        "agent",
        "runs",
        "turns",
        "fresh in",
        "cached in",
        "output",
        "thinking",
        "in/run",
        "out/run"
    );
    let rule = "-".repeat(head.chars().count());
    let mut lines = vec![head, rule];
    for r in table {
        let runs = r.runs.max(1);
        lines.push(format!(
            "{:<22}{:>6}{:>8}{:>14}{:>16}{:>12}{:>11}{:>12}{:>10}  {}",
            r.agent,
            r.runs,
            commas(r.turns),
            commas(r.fresh),
            commas(r.cached),
            commas(r.output),
            commas(r.thinking),
            commas(rounded(r.fresh + r.cached, runs)),
            commas(rounded(r.output, runs)),
            joined(&r.models)
        ));
    }
    if !adhoc.is_empty() {
        lines.push(String::new());
        lines.push("ad-hoc agents (no file pins their model) - runs dispatched with no model, and what they ran on:".to_owned());
        for ad in adhoc {
            let ran = joined(&ad.inherited);
            lines.push(format!(
                "  {:<20}{:>5} runs, {:>4} with no model: {}",
                ad.agent,
                ad.runs,
                ad.no_model,
                if ran.is_empty() { "-" } else { &ran }
            ));
        }
    }
    lines.join("\n")
}

fn counts_json(counts: &Counts) -> Value {
    Value::Object(counts.iter().map(|(k, v)| (k.clone(), json!(v))).collect())
}

/// The rows as `--json` writes them.
fn rows_json(since: &str, table: &[Row], adhoc: &[Adhoc]) -> Value {
    let agents: Vec<Value> = table.iter().map(|r| json!({"agent": r.agent, "runs": r.runs, "turns": r.turns, "fresh": r.fresh, "cached": r.cached, "output": r.output, "thinking": r.thinking, "models": counts_json(&r.models)})).collect();
    let ad: Vec<Value> = adhoc.iter().map(|a| json!({"agent": a.agent, "runs": a.runs, "no_model": a.no_model, "inherited": counts_json(&a.inherited)})).collect();
    json!({"since": since, "agents": agents, "adhoc": ad})
}

/// The census in the `measurements.json` shape `make figures` re-runs: one keyed value per figure.
fn figures(table: &[Row], adhoc: &[Adhoc], command: &str) -> Map<String, Value> {
    let mut out = Map::new();
    let mut add = |key: String, value: i64| {
        out.insert(key, json!({"value": value, "command": command}));
    };
    for r in table {
        let runs = r.runs.max(1);
        add(format!("census.{}.runs", r.agent), r.runs);
        add(
            format!("census.{}.turns_per_run", r.agent),
            rounded(r.turns, runs),
        );
        add(
            format!("census.{}.input_per_run", r.agent),
            rounded(r.fresh + r.cached, runs),
        );
        add(
            format!("census.{}.output_per_run", r.agent),
            rounded(r.output, runs),
        );
    }
    for ad in adhoc {
        add(format!("census.adhoc.{}.no_model", ad.agent), ad.no_model);
        let fable = ad
            .inherited
            .iter()
            .filter(|(m, _)| m.contains("fable"))
            .map(|(_, c)| c)
            .sum();
        add(format!("census.adhoc.{}.on_fable", ad.agent), fable);
    }
    out
}

/// What was asked for: every flag `agent_census.py` took.
struct Asked {
    root: String,
    since: String,
    until: String,
    json: String,
    record: String,
}

/// The flags as `--name value` or `--name=value`, or `None` for anything else.
fn parse(args: &[String], root: String) -> Option<Asked> {
    let mut asked = Asked {
        root,
        since: String::new(),
        until: String::new(),
        json: String::new(),
        record: String::new(),
    };
    let mut words = args.iter();
    while let Some(word) = words.next() {
        let (name, inline) = word
            .split_once('=')
            .map_or((word.as_str(), None), |(n, v)| (n, Some(v)));
        let slot = match name {
            "--root" => &mut asked.root,
            "--since" => &mut asked.since,
            "--until" => &mut asked.until,
            "--json" => &mut asked.json,
            "--record" => &mut asked.record,
            _ => return None,
        };
        let value = inline.or_else(|| {
            words
                .next()
                .map(String::as_str)
                .filter(|v| !v.starts_with('-'))
        })?;
        value.clone_into(slot);
    }
    Some(asked)
}

/// Merge the census into a `measurements.json`, replacing its earlier `census.` figures.
fn record_into(path: &Path, fresh: Map<String, Value>) -> Result<(), String> {
    let mut kept: Value = if path.is_file() {
        let body = std::fs::read_to_string(path).map_err(|e| e.to_string())?;
        serde_json::from_str(&body).map_err(|e| e.to_string())?
    } else {
        json!({})
    };
    let map = kept.as_object_mut().ok_or("not a JSON object")?;
    map.retain(|k, _| !k.starts_with("census."));
    map.extend(fresh);
    std::fs::write(path, py_dumps(&kept, 1, true) + "\n").map_err(|e| e.to_string())
}

/// `record agent-census [--root DIR] [--since D] [--until D] [--json FILE] [--record FILE]`.
pub(crate) fn cli(args: &[String], home: &Path) -> Reply {
    let default_root = home.join(".claude/projects").display().to_string();
    let Some(asked) = parse(args, default_root) else {
        return reply(String::new(), USAGE.to_owned(), 2);
    };
    let runs: Vec<(Value, Value)> = transcripts(Path::new(&asked.root))
        .iter()
        .map(|t| read_run(t))
        .collect();
    let (table, adhoc) = rows(&runs, &asked.since, &asked.until);
    let out = render(&table, &adhoc) + "\n";
    let mut failed = Vec::new();
    if !asked.json.is_empty() {
        let body = py_dumps(&rows_json(&asked.since, &table, &adhoc), 1, true) + "\n";
        if let Err(why) = std::fs::write(&asked.json, body) {
            failed.push(format!("agent-census: {}: {why}\n", asked.json));
        }
    }
    if !asked.record.is_empty() {
        let command = if asked.until.is_empty() {
            String::new()
        } else {
            format!(
                "scripts/gates/l7r-gate.sh record agent-census --until {} --record {}",
                asked.until, asked.record
            )
        };
        if let Err(why) = record_into(Path::new(&asked.record), figures(&table, &adhoc, &command)) {
            failed.push(format!("agent-census: {}: {why}\n", asked.record));
        }
    }
    let code = i32::from(!failed.is_empty());
    reply(out, failed.concat(), code)
}

#[cfg(test)]
mod tests;
