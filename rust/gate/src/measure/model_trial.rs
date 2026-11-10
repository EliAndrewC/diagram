//! A review check re-run on another model against a RECORDED run with known findings (feature 383 amendment 3, plan D24; feature 449 T77, from
//! `model_trial.py`). Feature 251's seeded-run method, kept as a tool so the next trial is a command, not an archaeology.
//!
//! `prepare` builds a clone at the last commit of this clone's history before the recorded run, copies the CURRENT agent files in with the tested
//! model written into the tested agent's copy, and rewrites the prompt's clone paths. A prompt naming a path outside the repository that no longer
//! exists is reported MISSING: such a case is not a fair re-run. A run is `claude -p --agent <name>` in that clone with every hook off.

mod case;
mod runs;

use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Value};

use super::{at, reply};
use crate::cohort::{int, text, truthy};

const SIGNALS: [&str; 16] = [
    "FAITHFUL",
    "CHANGES REQUIRED",
    "CLEAR",
    "BLOCKED",
    "NOT-REVIEWABLE",
    "IN-STEP",
    "DRIFTED",
    "NEEDS-RESEARCH",
    "MISLABELED",
    "CANNOT-TELL",
    "UNCLAIMED",
    "PASS",
    "FAIL",
    "OK",
    "ISSUE",
    "FINDING",
];
const SONNET: &str = "claude-sonnet-5-5";

fn compiled(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static WORDS: LazyLock<Vec<(&str, Regex)>> = LazyLock::new(|| {
    SIGNALS
        .iter()
        .map(|s| (*s, compiled(&format!(r"\b{}\b", fancy_regex::escape(s)))))
        .collect()
});
static OUTSIDE: LazyLock<Regex> =
    LazyLock::new(|| compiled(r#"(?:/tmp/|/diagram/\.clones/[\w-]+/\.git/)[^\s`'")]+"#));
static REFLOG: LazyLock<Regex> = LazyLock::new(|| compiled(r"@\{(\d+)\}"));

/// Where a trial looks and what it starts.
pub(crate) struct Trial {
    /// This clone.
    pub clone: PathBuf,
    /// `~/.claude/projects`.
    pub projects: PathBuf,
    /// The program a run is.
    pub claude: String,
}

/// The recorded run: its agent, prompt, final reply, start and records.
pub(crate) struct Run {
    pub agent: String,
    pub prompt: String,
    pub reply: String,
    pub started: String,
    pub records: Vec<Value>,
}

pub(crate) fn text_of(content: &Value) -> String {
    match content {
        Value::String(s) => s.clone(),
        Value::Array(blocks) => blocks
            .iter()
            .filter(|b| b["type"] == "text")
            .map(|b| b["text"].as_str().unwrap_or(""))
            .collect(),
        _ => String::new(),
    }
}

pub(crate) fn records_of(transcript: &Path) -> Vec<Value> {
    String::from_utf8_lossy(&std::fs::read(transcript).unwrap_or_default())
        .lines()
        .filter(|l| l.trim_start().starts_with('{'))
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect()
}

pub(crate) fn read(transcript: &Path) -> Run {
    let records = records_of(transcript);
    let of_kind = |kind: &str, r: &Value| r["type"] == kind;
    let prompt = records
        .iter()
        .find(|r| of_kind("user", r))
        .map_or_else(String::new, |r| text_of(&r["message"]["content"]));
    let reply = records
        .iter()
        .rev()
        .filter(|r| of_kind("assistant", r))
        .map(|r| text_of(&r["message"]["content"]))
        .find(|t| !t.is_empty());
    let meta: Value = std::fs::read_to_string(transcript.with_extension("meta.json"))
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok())
        .unwrap_or_else(|| json!({}));
    let started = records
        .iter()
        .find_map(|r| r["timestamp"].as_str().filter(|s| !s.is_empty()))
        .unwrap_or("")
        .to_owned();
    Run {
        agent: meta["agentType"].as_str().unwrap_or("").to_owned(),
        prompt,
        reply: reply.unwrap_or_default(),
        started,
        records,
    }
}

pub(crate) fn signature(reply: &str) -> String {
    let counted = WORDS
        .iter()
        .map(|(s, re)| (*s, re.find_iter(reply).flatten().count()));
    counted
        .filter(|(_, n)| *n > 0)
        .map(|(s, n)| format!("{s}={n}"))
        .collect::<Vec<_>>()
        .join(" ")
}

/// Paths a prompt names that no checkout holds, each once: a bundle under `/tmp/`, and a clone's git directory (the review snapshots under
/// `<clone>/.git/review-snapshot/`, which hold the renders a glyph or building review judges).
pub(crate) fn outside_paths(prompt: &str) -> Vec<String> {
    let mut found: Vec<String> = OUTSIDE
        .find_iter(prompt)
        .flatten()
        .map(|m| {
            m.as_str()
                .trim_end_matches(['.', ',', ')', ':', ';', '`', '\'', '"'])
                .to_owned()
        })
        .collect();
    found.sort();
    found.dedup();
    found
}

/// The newest file's time under `root`, or `root`'s own when it holds none.
pub(crate) fn newest(root: &Path) -> f64 {
    let stamp = |p: &Path| {
        let modified = std::fs::metadata(p).and_then(|m| m.modified()).ok();
        modified
            .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
            .map_or(0.0, |d| d.as_secs_f64())
    };
    let (mut best, mut todo): (Option<f64>, _) = (None, vec![root.to_path_buf()]);
    while let Some(at) = todo.pop() {
        for path in std::fs::read_dir(&at)
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.path())
        {
            if path.is_dir() {
                todo.push(path);
            } else {
                best = Some(best.map_or(stamp(&path), |b| b.max(stamp(&path))));
            }
        }
    }
    best.unwrap_or_else(|| stamp(root))
}

/// The folder a path's freshness is judged by: the path if a directory, else its parent.
pub(crate) fn bundle_root(src: &Path) -> &Path {
    if src.is_dir() {
        src
    } else {
        src.parent().unwrap_or(src)
    }
}

/// Every path outside the repository the prompt names exists and was not written after the run started.
pub(crate) fn replayable(run: &Run) -> bool {
    let started = at(&run.started);
    outside_paths(&run.prompt).iter().all(|p| {
        let src = Path::new(p);
        src.exists() && newest(bundle_root(src)) <= started
    })
}

pub(crate) fn children(dir: &Path) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .collect();
    out.sort();
    out
}

pub(crate) fn named(path: &Path, starts: &str, ends: &str) -> bool {
    path.file_name()
        .and_then(|n| n.to_str())
        .is_some_and(|n| n.starts_with(starts) && n.ends_with(ends))
}

impl Trial {
    /// The recorded runs of a check, newest first, with their verdict words.
    fn catalog(&self, agent: &str, since: &str, only_replayable: bool) -> String {
        let mut rows = Vec::new();
        let sessions = children(&self.projects)
            .into_iter()
            .filter(|p| named(p, "-diagram", ""))
            .flat_map(|p| children(&p));
        for meta in sessions
            .flat_map(|s| children(&s.join("subagents")))
            .filter(|p| named(p, "agent-", ".meta.json"))
        {
            let parsed: Value = std::fs::read_to_string(&meta)
                .ok()
                .and_then(|t| serde_json::from_str(&t).ok())
                .unwrap_or_else(|| json!({}));
            let t = meta.with_file_name(
                meta.file_name()
                    .unwrap_or_default()
                    .to_string_lossy()
                    .replace(".meta.json", ".jsonl"),
            );
            if parsed["agentType"] != agent || !t.is_file() {
                continue;
            }
            let run = read(&t);
            let day: String = run.started.chars().take(10).collect();
            if !run.reply.is_empty()
                && day.as_str() >= since
                && (!only_replayable || replayable(&run))
            {
                rows.push((t, run));
            }
        }
        rows.sort_by(|a, b| b.1.started.cmp(&a.1.started));
        let mut out = String::new();
        for (t, run) in rows {
            let flat: String = run
                .prompt
                .split_whitespace()
                .collect::<Vec<_>>()
                .join(" ")
                .chars()
                .take(200)
                .collect();
            let _ = writeln!(
                out,
                "{}  {}\n    prompt={} reply={}  {}\n    {flat}",
                run.started.chars().take(16).collect::<String>(),
                t.display(),
                run.prompt.chars().count(),
                run.reply.chars().count(),
                signature(&run.reply)
            );
        }
        out
    }
}

/// One run's totals: usage folded per message id as the per-field maximum (R2 of feature 383), then summed; `started` is the run's first timestamp, of any
/// record. The one fold: `record agent-census` calls this (`ask:449-T77-replays`).
pub(crate) fn fold_usage(records: &[Value]) -> Value {
    let mut per: BTreeMap<String, [i64; 4]> = BTreeMap::new();
    let mut models: Vec<(String, i64)> = Vec::new();
    for record in records.iter().filter(|r| r["type"] == "assistant") {
        let message = &record["message"];
        let usage = &message["usage"];
        if !usage.is_object() || !truthy(&message["id"]) {
            continue;
        }
        let row = [
            int(&usage["input_tokens"]) + int(&usage["cache_creation_input_tokens"]),
            int(&usage["cache_read_input_tokens"]),
            int(&usage["output_tokens"]),
            int(&usage["output_tokens_details"]["thinking_tokens"]),
        ];
        let id = text(message, "id");
        if !per.contains_key(&id) {
            let model = message["model"]
                .as_str()
                .filter(|m| !m.is_empty())
                .unwrap_or("unknown")
                .to_owned();
            match models.iter_mut().find(|(m, _)| *m == model) {
                Some(found) => found.1 += 1,
                None => models.push((model, 1)),
            }
        }
        let kept = per.entry(id).or_insert([0; 4]);
        for (old, new) in kept.iter_mut().zip(row) {
            *old = (*old).max(new);
        }
    }
    let sum = |i: usize| per.values().map(|r| r[i]).sum::<i64>();
    let top = models.iter().fold(None::<&(String, i64)>, |best, m| {
        if best.is_none_or(|b| m.1 > b.1) {
            Some(m)
        } else {
            best
        }
    });
    let started = records
        .iter()
        .find(|r| truthy(&r["timestamp"]))
        .map_or_else(String::new, |r| text(r, "timestamp"));
    json!({"fresh": sum(0), "cached": sum(1), "output": sum(2), "thinking": sum(3), "turns": per.len(), "model": top.map_or("none", |m| m.0.as_str()), "started": started})
}

/// `model_trial`'s words after its subcommand: the flags with a value, the bare flags and the positional words.
pub(crate) struct Words<'a> {
    pub plain: Vec<&'a str>,
    pub valued: BTreeMap<&'a str, &'a str>,
    pub bare: Vec<&'a str>,
}

impl Words<'_> {
    fn get(&self, name: &str) -> Option<&str> {
        self.valued.get(name).copied()
    }

    fn number(&self, name: &str, default: usize) -> usize {
        self.get(name)
            .and_then(|n| n.parse().ok())
            .unwrap_or(default)
    }

    fn has(&self, name: &str) -> bool {
        self.bare.contains(&name)
    }
}

pub(crate) fn words(args: &[String]) -> Words<'_> {
    const VALUED: [&str; 6] = [
        "--since",
        "--model",
        "--omit-claude-md",
        "--at",
        "--runs",
        "--parallel",
    ];
    let mut out = Words {
        plain: Vec::new(),
        valued: BTreeMap::new(),
        bare: Vec::new(),
    };
    let mut rest = args.iter().map(String::as_str);
    while let Some(word) = rest.next() {
        if VALUED.contains(&word) {
            out.valued.insert(word, rest.next().unwrap_or(""));
        } else if word.starts_with("--") {
            out.bare.push(word);
        } else {
            out.plain.push(word);
        }
    }
    out
}

const USAGE: &str =
    "usage: l7r-gate measure model-trial catalog <agent> [--since D] [--replayable] | prepare <transcript> <out> [--model M] [--head] [--omit-claude-md yes|no] [--as-subagent] [--at C] | run <out> [--runs N] | usage <out> | run-all <root> [--runs N] [--parallel N] | snapshot <out> | collect <out>\n";

impl Trial {
    fn dispatch(&self, verb: &str, w: &Words) -> Result<(String, i32), String> {
        let first = Path::new(w.plain[0]);
        match verb {
            "catalog" => Ok((
                self.catalog(
                    w.plain[0],
                    w.get("--since").unwrap_or(""),
                    w.has("--replayable"),
                ),
                0,
            )),
            "prepare" if w.plain.len() == 2 => {
                self.prepare(first, Path::new(w.plain[1]), &case::Asked::from_words(w))
            }
            "run" => self.run_case(first, w.number("--runs", 3)).map(|o| (o, 0)),
            "usage" => runs::usage(first).map(|o| (o, 0)),
            "run-all" => self
                .run_all(first, w.number("--runs", 3), w.number("--parallel", 6))
                .map(|o| (o, 0)),
            "snapshot" => self.snapshot(first),
            "collect" => Ok(self.collect(first)),
            _ => Err(USAGE.trim_end().to_owned()),
        }
    }
}

/// `l7r-gate measure model-trial ...`.
pub(crate) fn cli(args: &[String], trial: &Trial) -> crate::Reply {
    let Some(verb) = args.first() else {
        return reply(String::new(), USAGE.to_owned(), 2);
    };
    let w = words(&args[1..]);
    if w.plain.is_empty() {
        return reply(String::new(), USAGE.to_owned(), 2);
    }
    match trial.dispatch(verb, &w) {
        Ok((out, code)) => reply(out, String::new(), code),
        Err(why) => reply(String::new(), why + "\n", 2),
    }
}

/// `model-trial` as the live command finds things.
pub(crate) fn live(home: &Path, clone: &Path) -> Trial {
    Trial {
        clone: clone.to_owned(),
        projects: home.join(".claude/projects"),
        claude: "claude".to_owned(),
    }
}

#[cfg(test)]
mod tests;
