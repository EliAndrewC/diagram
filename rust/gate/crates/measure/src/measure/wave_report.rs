//! A wave's cost, through `check-wave` against the last wave launched by hand (feature 383 amendment 7, FR-046; feature 449 T76, from
//! `wave_report.py`): each agent's first request's cache read and write, then the main session's notification wakes and the context they re-read.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use super::{commas, median, reply};

const WAVE_N: usize = 4;
static TOOL_USE_ID: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"<tool-use-id>(\S+?)</tool-use-id>").unwrap_or_else(|e| unreachable!("{e}"))
});

fn records(path: &Path) -> Vec<Value> {
    let text = String::from_utf8_lossy(&std::fs::read(path).unwrap_or_default()).into_owned();
    text.lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        .filter(Value::is_object)
        .collect()
}

fn text(v: &Value, key: &str) -> String {
    v[key].as_str().unwrap_or_default().to_owned()
}

fn number(v: &Value) -> i64 {
    v.as_i64().unwrap_or(0)
}

/// One agent's first request.
#[derive(Clone, Debug, PartialEq, Eq)]
struct Row {
    kind: String,
    t: String,
    read: i64,
    written: i64,
}

fn meta(agent: &Path) -> Value {
    serde_json::from_str(
        &std::fs::read_to_string(agent.with_extension("meta.json")).unwrap_or_default(),
    )
    .unwrap_or_default()
}

fn agents(paths: &[PathBuf]) -> Vec<Row> {
    let mut out: Vec<Row> = paths
        .iter()
        .filter_map(|p| {
            let recs = records(p);
            let first = recs
                .iter()
                .find(|r| r["type"] == "assistant" && !r["message"]["usage"].is_null())?;
            let u = &first["message"]["usage"];
            let kind = meta(p)["agentType"].as_str().unwrap_or("?").to_owned();
            Some(Row {
                kind,
                t: text(first, "timestamp"),
                read: number(&u["cache_read_input_tokens"]),
                written: number(&u["cache_creation_input_tokens"]),
            })
        })
        .collect();
    out.sort_by(|a, b| a.t.cmp(&b.t));
    out
}

fn user_text(content: &Value) -> String {
    match content {
        Value::String(s) => s.clone(),
        Value::Array(a) => a
            .iter()
            .map(|b| b["text"].as_str().unwrap_or_default())
            .collect(),
        _ => String::new(),
    }
}

/// The main session's turns a task notification started, each with the context its first request re-read.
fn wakes(main: &Path, ids: Option<&BTreeSet<String>>, start: &str, end: &str) -> Vec<i64> {
    let recs: Vec<Value> = records(main)
        .into_iter()
        .filter(|r| r["type"] == "user" || r["type"] == "assistant")
        .collect();
    let mut out = Vec::new();
    for (i, r) in recs.iter().enumerate() {
        let body = if r["type"] == "user" {
            user_text(&r["message"]["content"])
        } else {
            String::new()
        };
        if !body.trim_start().starts_with("<task-notification>") {
            continue;
        }
        let hit = if let Some(wanted) = ids {
            TOOL_USE_ID
                .captures_iter(&body)
                .flatten()
                .any(|c| wanted.contains(&c[1]))
        } else {
            let at = text(r, "timestamp");
            start <= at.as_str() && at.as_str() <= end
        };
        if hit {
            let usage = recs[i + 1..]
                .iter()
                .find(|x| x["type"] == "assistant")
                .map(|x| &x["message"]["usage"]);
            out.push(usage.map_or(0, |u| {
                number(&u["cache_read_input_tokens"]) + number(&u["cache_creation_input_tokens"])
            }));
        }
    }
    out
}

/// A message's launches, by agent type.
type Launches = Vec<(String, Vec<String>)>;

/// The last message before `before` that launched `WAVE_N` or more Agent calls of one type.
fn last_hand_wave(main: &Path, before: &str) -> Option<(String, Vec<String>)> {
    let mut messages: Vec<(String, Launches)> = Vec::new();
    for r in records(main)
        .iter()
        .filter(|r| r["type"] == "assistant" && text(r, "timestamp").as_str() < before)
    {
        let m = &r["message"];
        let id = m["id"]
            .as_str()
            .map_or_else(|| text(r, "uuid"), str::to_owned);
        let at = messages
            .iter()
            .position(|(k, _)| *k == id)
            .unwrap_or_else(|| {
                messages.push((id, Vec::new()));
                messages.len() - 1
            });
        for b in m["content"].as_array().map_or(&[][..], Vec::as_slice) {
            if b["type"] == "tool_use" && (b["name"] == "Agent" || b["name"] == "Task") {
                let kind = b["input"]["subagent_type"]
                    .as_str()
                    .filter(|s| !s.is_empty())
                    .unwrap_or("general-purpose")
                    .to_owned();
                let kinds = &mut messages[at].1;
                let slot = kinds
                    .iter()
                    .position(|(k, _)| *k == kind)
                    .unwrap_or_else(|| {
                        kinds.push((kind, Vec::new()));
                        kinds.len() - 1
                    });
                kinds[slot].1.push(text(b, "id"));
            }
        }
    }
    messages
        .into_iter()
        .flat_map(|(_, kinds)| kinds)
        .filter(|(_, ids)| ids.len() >= WAVE_N)
        .next_back()
}

fn table(rows: &[Row]) -> Vec<String> {
    rows.iter()
        .map(|a| {
            format!(
                "  {}  {:<22} read {:>7}  written {:>7}",
                a.t.get(11..23).unwrap_or_default(),
                a.kind,
                commas(a.read),
                commas(a.written)
            )
        })
        .collect()
}

#[expect(
    clippy::cast_precision_loss,
    reason = "token counts, far inside f64's exact range"
)]
fn wake_line(ws: &[i64]) -> String {
    let mut line = format!("  main-session wakes: {}", ws.len());
    if !ws.is_empty() {
        let mut v: Vec<f64> = ws.iter().map(|w| *w as f64).collect();
        let _ = write!(
            line,
            ", median context re-read {}k",
            super::ratchet::round_even(median(&mut v) / 1000.0)
        );
    }
    line
}

fn children(dir: &Path, want: impl Fn(&str) -> bool) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| want(&e.file_name().to_string_lossy()))
        .map(|e| e.path())
        .collect();
    out.sort();
    out
}

fn agent_files(dir: &Path) -> Vec<PathBuf> {
    children(dir, |n| {
        n.starts_with("agent-") && crate::checks::has_ext(n, "jsonl")
    })
}

fn modified(p: &Path) -> std::time::SystemTime {
    std::fs::metadata(p)
        .and_then(|m| m.modified())
        .unwrap_or(std::time::UNIX_EPOCH)
}

/// Every other session of the project, newest first.
fn other_sessions(projects: &Path, main: &Path) -> Vec<PathBuf> {
    let mut all: Vec<PathBuf> = children(projects, |n| n.starts_with("-diagram"))
        .iter()
        .flat_map(|d| children(d, |n| crate::checks::has_ext(n, "jsonl")))
        .filter(|p| p != main)
        .collect();
    all.sort_by_key(|p| std::cmp::Reverse(modified(p)));
    all
}

fn hand_section(mains: &[PathBuf], first_t: &str) -> Vec<String> {
    for m in mains {
        let Some((kind, ids)) = last_hand_wave(m, first_t) else {
            continue;
        };
        let by_call: BTreeMap<String, PathBuf> =
            agent_files(&m.with_extension("").join("subagents"))
                .into_iter()
                .filter_map(|p| {
                    Some((
                        meta(&p)["toolUseId"]
                            .as_str()
                            .filter(|s| !s.is_empty())?
                            .to_owned(),
                        p,
                    ))
                })
                .collect();
        let found: Vec<PathBuf> = ids.iter().filter_map(|i| by_call.get(i).cloned()).collect();
        let set: BTreeSet<String> = ids.iter().cloned().collect();
        let parent = m
            .parent()
            .and_then(Path::file_name)
            .unwrap_or_default()
            .to_string_lossy();
        let stem = m.file_stem().unwrap_or_default().to_string_lossy();
        let mut lines = vec![format!(
            "LAST HAND-LAUNCHED WAVE: {} {kind} in one message ({parent}/{stem})",
            ids.len()
        )];
        lines.extend(table(&agents(&found)));
        lines.push(wake_line(&wakes(m, Some(&set), "", "")));
        return lines;
    }
    vec![format!("no hand-launched wave of {WAVE_N}+ before it")]
}

fn report(run: &Path) -> String {
    let session = run.ancestors().nth(3).unwrap_or(run);
    let main = session.parent().map_or_else(PathBuf::new, |p| {
        p.join(format!(
            "{}.jsonl",
            session.file_name().unwrap_or_default().to_string_lossy()
        ))
    });
    let rows = agents(&agent_files(run));
    let Some(first) = rows.first() else {
        return format!(
            "wave-report: {} has no agent with a request yet",
            run.display()
        );
    };
    let mut lines = vec![format!(
        "WORKFLOW RUN {} ({}): {} agent(s)",
        run.file_name().unwrap_or_default().to_string_lossy(),
        session.file_name().unwrap_or_default().to_string_lossy(),
        rows.len()
    )];
    lines.extend(table(&rows));
    let last = rows
        .iter()
        .map(|a| a.t.clone())
        .chain(
            records(&run.join("journal.jsonl"))
                .iter()
                .filter(|r| r["type"] == "result")
                .map(|r| text(r, "timestamp")),
        )
        .max()
        .unwrap_or_default();
    let end = format!("{}~", last.get(..19).unwrap_or(&last));
    lines.push(wake_line(&wakes(&main, None, &first.t, &end)));
    let projects = session.parent().and_then(Path::parent).unwrap_or(session);
    let mut mains = vec![main.clone()];
    mains.extend(other_sessions(projects, &main));
    lines.extend(hand_section(&mains, &first.t));
    lines.join("\n")
}

fn newest_run(root: &Path) -> Option<PathBuf> {
    let name = root.file_name()?.to_string_lossy().into_owned();
    let parent = root.parent()?;
    let projects = children(parent, |n| n.starts_with(&name));
    let runs = projects
        .iter()
        .flat_map(|p| children(p, |_| true))
        .flat_map(|s| children(&s.join("subagents/workflows"), |n| n.starts_with("wf_")));
    runs.filter(|p| p.is_dir()).max_by_key(|p| modified(p))
}

/// `l7r-gate measure wave-report [--run D] [--root D]`.
#[must_use]
pub fn cli(args: &[String], home: &Path) -> crate::Reply {
    let flag = |name: &str| {
        args.windows(2)
            .find(|w| w[0] == name)
            .map(|w| PathBuf::from(&w[1]))
    };
    let root = flag("--root").unwrap_or_else(|| home.join(".claude/projects/-diagram"));
    let Some(run) = flag("--run").or_else(|| newest_run(&root)) else {
        return reply(
            format!("wave-report: no workflow run under {}\n", root.display()),
            String::new(),
            1,
        );
    };
    reply(report(&run) + "\n", String::new(), 0)
}

#[cfg(test)]
mod tests;
