//! What was spent beside the critical path (feature 451 T10, plan D7; FR-005): each agent's minutes and tokens under its task, their
//! sum apart from the wall clock, and the rework - refused landings and plan re-rounds.
//!
//! WHY. The 2026-11-19 retrospective split the day's wall clock from the agent-minutes spent beside it (the spec's Why); the critical path
//! (`where_time::tables`) books each second once, and the agents ran in parallel with it and with each other, so their minutes are a
//! sum apart, never a share of it.
//!
//! THE AGENTS are [`Flight`](super::Flight)'s, read once with the waits' spans (T09): the feature's own, their lines from every log. An
//! agent goes to the task its lines name (its launch's brief, D6) where the command books by start, else - by tick - to the mark at its
//! first start, as every gap is. Read by the task its first start fell in, as the walk before this one did, 12 of the window's agents
//! sat under no task and T18's 14 beside a task row of 0 minutes, measured 2026-11-21 (`make where-time F=451
//! SINCE=2026-11-20T04:33:00Z UNTIL=2026-11-21T04:10:44Z` before this task, `/tmp/t10/wt-before.log`).
//!
//! THE MINUTES are an agent's spans inside the window ([`clip`]): the agent lines are read from every log whole, so a span is cut to
//! SINCE and UNTIL, and an agent started twice with no stop between - two spans to one stop - counts its seconds once. Uncut, one agent
//! of the window started 18 min before SINCE read 26 min where its window held 9, measured 2026-11-21 (the command over the window above,
//! before and after the clip, `/tmp/t10/wt-after2.log` and `wt-after3.log`).
//!
//! THE TOKENS are read from each agent's transcript (`<projects>/*/<sid>/subagents/agent-<aid>.jsonl`), each `message.id` once, its rows
//! inside the window - D6's sum, read after the fact - and only where there is none from its last stop's `tok`: the stop's sum was
//! short of the transcript's rows timestamped at or before the stop on 16 of the 17 stops that carried one (by 1,005 output tokens of
//! 6,329 on `a8348bf9fb2e13438`), and 17 of the window's 279 stops carried one, measured 2026-11-21 (`/tmp/t10/scripts/m2.py` over the
//! 451 log and the transcripts, the window above).
//!
//! THE REWORK. A refused landing is a landing `end` line whose `landed` is false, never read from its code: a push that went out with a
//! later raise, or exit 3 with its ticks standing, is a landing (D7); a landing of several tasks is one refusal, counted under each. A
//! plan re-round is a task's `spec-fidelity` or `spec-fidelity-verify` agent after its first (D7), each agent once, a resume no new
//! round; agents naming no task are no task's re-round.

use std::collections::HashMap;
use std::path::Path;

use serde_json::Value;

use super::super::super::events::{fixed, get, hhmm, is, or_s, ts, Event};
use super::super::task_at;
use super::Agent;

/// An agent's tokens (D6's `tok`): fresh input, cache read, cache written, and output.
#[derive(Debug, Clone, Copy, Default, PartialEq)]
pub struct Tok {
    /// Input not read from the cache.
    pub fresh: f64,
    /// Input read from the cache.
    pub cached: f64,
    /// Input written to the cache.
    pub created: f64,
    /// Output.
    pub out: f64,
}

impl Tok {
    /// A stop's `tok` (`in`, `cached`, `created`, `out`), none where it is no object.
    #[must_use]
    pub fn of(v: &Value) -> Option<Self> {
        let n = |k: &str| v.get(k).and_then(Value::as_f64).unwrap_or(0.0);
        v.as_object().map(|_| Self {
            fresh: n("in"),
            cached: n("cached"),
            created: n("created"),
            out: n("out"),
        })
    }

    /// A transcript row's `message.usage`.
    fn of_usage(u: &Value) -> Self {
        let n = |k: &str| u.get(k).and_then(Value::as_f64).unwrap_or(0.0);
        Self {
            fresh: n("input_tokens"),
            cached: n("cache_read_input_tokens"),
            created: n("cache_creation_input_tokens"),
            out: n("output_tokens"),
        }
    }

    /// Every input token, cached or not.
    #[must_use]
    pub fn input(&self) -> f64 {
        self.fresh + self.cached + self.created
    }

    fn plus(self, o: Self) -> Self {
        Self {
            fresh: self.fresh + o.fresh,
            cached: self.cached + o.cached,
            created: self.created + o.created,
            out: self.out + o.out,
        }
    }
}

/// The agents' transcripts' usage rows, each agent's by message id, the first row of an id kept (a message is written once per block).
#[derive(Debug, Default)]
pub struct Tokens {
    by_aid: HashMap<String, HashMap<String, Tok>>,
}

impl Tokens {
    /// The rows of `text`, `path`'s, inside `window`, where `path` is a subagent's transcript (`subagents/agent-<aid>.jsonl`).
    pub fn read(&mut self, path: &Path, text: &str, (lo, hi): (f64, f64)) {
        let name = path
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or_default();
        let Some(aid) = name
            .strip_prefix("agent-")
            .and_then(|n| n.strip_suffix(".jsonl"))
        else {
            return;
        };
        let msgs = self.by_aid.entry(aid.to_owned()).or_default();
        for line in text.lines().filter(|l| l.contains("\"usage\"")) {
            let Ok(row) = serde_json::from_str::<Value>(line) else {
                continue;
            };
            let (Some(id), Some(u), Some(Ok(at))) = (
                row.pointer("/message/id").and_then(Value::as_str),
                row.pointer("/message/usage"),
                row.get("timestamp").and_then(Value::as_str).map(ts),
            ) else {
                continue;
            };
            if (lo..=hi).contains(&at) {
                msgs.entry(id.to_owned())
                    .or_insert_with(|| Tok::of_usage(u));
            }
        }
    }

    /// agent id -> its tokens, an agent with no row inside the window left out.
    #[must_use]
    pub fn sums(self) -> HashMap<String, Tok> {
        self.by_aid
            .into_iter()
            .filter(|(_, m)| !m.is_empty())
            .map(|(aid, m)| (aid, m.into_values().fold(Tok::default(), Tok::plus)))
            .collect()
    }
}

/// One agent under its task.
#[derive(Debug, Clone, PartialEq)]
pub struct Row {
    /// The task it is booked to.
    pub task: String,
    /// Its id.
    pub aid: String,
    /// Its kind.
    pub kind: String,
    /// Its first start.
    pub t0: f64,
    /// Its spans' seconds.
    pub secs: f64,
    /// Its tokens, none where neither its transcript nor a stop counted them.
    pub tok: Option<Tok>,
}

/// `agents` cut to the window `(lo, hi)`: each span cut to it, the overlapping ones merged - an agent started twice with no stop between
/// holds two spans to that one stop, its seconds counted once - and an agent with no span inside the window dropped.
pub fn clip(agents: &mut Vec<Agent>, (lo, hi): (f64, f64)) {
    for a in agents.iter_mut() {
        let cut = a
            .spans
            .iter()
            .map(|&(x, y)| (x.max(lo), y.min(hi)))
            .filter(|(x, y)| y >= x)
            .collect();
        a.spans = super::union(cut);
    }
    agents.retain(|a| !a.spans.is_empty());
}

/// Each agent of `agents` under its task: the one its lines name where `named` (the command's booking by start), else the mark at its
/// first start; its tokens its transcript's (`tokens`), else its last stop's.
#[must_use]
#[expect(clippy::implicit_hasher, reason = "the map `read_subagents` makes")]
pub fn rows(
    agents: &[Agent],
    tokens: &HashMap<String, Tok>,
    starts: &[(f64, String)],
    named: bool,
) -> Vec<Row> {
    agents
        .iter()
        .map(|a| {
            let t0 = a.spans.first().map_or(0.0, |s| s.0);
            Row {
                task: if named && !a.task.is_empty() {
                    a.task.clone()
                } else {
                    task_at(starts, t0)
                },
                aid: a.aid.clone(),
                kind: a.kind.clone(),
                t0,
                secs: a.spans.iter().fold(0.0, |s, (x, y)| s + y - x),
                tok: tokens.get(&a.aid).copied().or(a.tok),
            }
        })
        .collect()
}

/// The tasks of each refused landing: a landing `end` line (`src` land, `step` end) at or before `until` whose `landed` is false, its
/// `tasks`, else its `task`, else `-`.
#[must_use]
pub fn refused(aside: &[Event], until: &str) -> Vec<Vec<String>> {
    let mut out = Vec::new();
    for e in aside {
        if !(is(e, "ev", "Phase") && is(e, "src", "land") && is(e, "step", "end"))
            || get(e, "landed").as_bool() != Some(false)
            || (!until.is_empty() && or_s(e, "t").as_str() > until)
        {
            continue;
        }
        let mut tasks: Vec<String> = get(e, "tasks")
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(|t| t.as_str().map(str::to_owned))
            .collect();
        if tasks.is_empty() {
            let task = or_s(e, "task");
            tasks.push(if task.is_empty() {
                "-".to_owned()
            } else {
                task
            });
        }
        out.push(tasks);
    }
    out
}

/// `n` thousand, one place.
fn k(n: f64) -> String {
    fixed(n / 1000.0, 1)
}

/// `n word`, plural but for one.
fn count(n: usize, word: &str) -> String {
    format!("{n} {word}{}", if n == 1 { "" } else { "s" })
}

/// The tasks' agents and rework (one row a task of `order`, then `all`), each agent under its task, and the line setting their sum beside
/// the critical path's `critical` seconds.
#[must_use]
pub fn render(rows: &[Row], refused: &[Vec<String>], order: &[&String], critical: f64) -> String {
    let mut lines = vec![
        "| task | agents | agent minutes | k tokens in | k tokens out | refused landings | plan re-rounds | by kind (count) |".to_owned(),
        "|---|---|---|---|---|---|---|---|".to_owned(),
    ];
    let toks = |rs: &[&Row]| {
        let got: Vec<Tok> = rs.iter().filter_map(|r| r.tok).collect();
        if got.is_empty() {
            ("-".to_owned(), "-".to_owned())
        } else {
            let t = got.into_iter().fold(Tok::default(), Tok::plus);
            (k(t.input()), k(t.out))
        }
    };
    let mut rerounds = 0;
    for task in order {
        let mine: Vec<&Row> = rows.iter().filter(|r| &r.task == *task).collect();
        let landings = refused.iter().filter(|ts| ts.contains(task)).count();
        if mine.is_empty() && landings == 0 {
            continue;
        }
        let reviews = mine
            .iter()
            .filter(|r| r.kind.starts_with("spec-fidelity"))
            .count();
        let again = if task.as_str() == "-" {
            0
        } else {
            reviews.saturating_sub(1)
        };
        rerounds += again;
        let mut kinds = super::super::super::events::Tally::default();
        for r in &mine {
            kinds.add(&r.kind, 1.0);
        }
        let kinds = kinds
            .most_common()
            .iter()
            .map(|(n, c)| format!("{n} {c}"))
            .collect::<Vec<_>>()
            .join(", ");
        let (tin, tout) = toks(&mine);
        lines.push(format!(
            "| {task} | {} | {} | {tin} | {tout} | {landings} | {again} | {kinds} |",
            mine.len(),
            fixed(mine.iter().fold(0.0, |a, r| a + r.secs) / 60.0, 0)
        ));
    }
    let all: Vec<&Row> = rows.iter().filter(|r| order.contains(&&r.task)).collect();
    let secs = all.iter().fold(0.0, |a, r| a + r.secs);
    let (tin, tout) = toks(&all);
    lines.push(format!(
        "| all | {} | {} | {tin} | {tout} | {} | {rerounds} | |",
        all.len(),
        fixed(secs / 60.0, 0),
        refused.len()
    ));
    lines.extend(
        [
            "",
            "| task | agent | kind | from (UTC) | minutes | k tokens in | k tokens out |",
            "|---|---|---|---|---|---|---|",
        ]
        .map(String::from),
    );
    for task in order {
        for r in all.iter().filter(|r| &r.task == *task) {
            let (tin, tout) = r.tok.map_or(("-".to_owned(), "-".to_owned()), |t| {
                (k(t.input()), k(t.out))
            });
            lines.push(format!(
                "| {task} | {} | {} | {} | {} | {tin} | {tout} |",
                r.aid,
                r.kind,
                hhmm(r.t0),
                fixed(r.secs / 60.0, 0)
            ));
        }
    }
    lines.push(String::new());
    lines.push(format!(
        "the critical path: {} min of wall clock; beside it, the agents' own minutes summed: {} min over {}, {}k tokens in and {}k out \
         ({} with no count); rework: {}, {} (feature 451 T10, D7)",
        fixed(critical / 60.0, 0),
        fixed(secs / 60.0, 0),
        count(all.len(), "agent"),
        if tin == "-" { "0.0".to_owned() } else { tin },
        if tout == "-" { "0.0".to_owned() } else { tout },
        all.iter().filter(|r| r.tok.is_none()).count(),
        count(refused.len(), "refused landing"),
        count(rerounds, "plan re-round")
    ));
    lines.join("\n")
}
