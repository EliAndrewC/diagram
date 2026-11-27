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
//! 451 log and the transcripts, the window above). An agent's advisor calls are counted apart, in their own columns (451 T69): a row
//! carrying one sums the builder's own two iterations at its top level, and the advisor's own iteration, `advisor_message` in
//! `usage.iterations`, is in no top level, so the window's agents' advisor tokens were in no column ([`Adv`]); a stop's `adv` stands
//! for them where its transcript has no row, and a stop written before T69 carries none, its agent's advisor tokens uncounted.
//!
//! THE REWORK. A refused landing is a landing `end` line whose `landed` is false, never read from its code: a push that went out with a
//! later raise, or exit 3 with its ticks standing, is a landing (D7); a landing of several tasks is one refusal, counted under each. A
//! plan re-round is a later round of one review on one subject ([`rerounds`], feature 451 T11): a `spec-fidelity` dispatch inside the
//! window whose key in the feature report's rounds table (`feature_report::tables::round_key`: its agent and the subject its MANIFEST
//! names) a dispatch before it in the feature's log holds, inside the window or before SINCE - a second round run inside the window is
//! rework done inside it, its first round before SINCE or not (T11's plan review, 2026-11-21) - booked to the task its line names, else
//! the mark. T10 counted a task's every `spec-fidelity` agent
//! after its first - its block-bundle reviews and any other review launched under it - 68 in its window against the table's 23 rounds
//! past the first, about 3x (T10's plan review, 2026-11-21); by the table's key the window reads 23, measured 2026-11-21 (`make where-time
//! F=451 SINCE=2026-11-20T04:33:00Z UNTIL=2026-11-21T04:10:44Z`, T11's plan section). A `spec-fidelity-verify` round is the review hook's
//! routing of a later `spec-fidelity` dispatch, logged under the name dispatched: the 451 log holds no `spec-fidelity-verify` dispatch
//! among its 108 `spec-fidelity` ones, measured 2026-11-21 (its `PreToolUse` Agent lines counted by `agent`).

use std::collections::HashMap;
use std::path::Path;

use serde_json::Value;

use super::super::super::events::{fixed, get, hhmm, is, or_s, t_of, ts, Event, Raised};
use super::super::super::feature_report::tables::round_key;
use super::super::task_at;
use super::Agent;

/// An agent's tokens (D6's `tok`): fresh input, cache read, cache written, and output - its own model calls', the top level of each
/// call's usage - and apart from them its advisor calls' (451 T69).
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
    /// Its advisor calls' own iterations, none where they were not counted: a stop written before T69 carries no `adv`.
    pub adv: Option<Adv>,
}

/// An agent's advisor calls' tokens (451 T69): the `advisor_message` iterations of its rows' `usage.iterations`, which no top level
/// holds - an advisor call's row sums the builder's own two iterations, before and after it, at its top level - every input token,
/// cached or not, and output. The 2,722 advisor iterations of the session's subagent transcripts read none from the cache and wrote none
/// to it, measured 2026-11-21 (`/tmp/t69/rows.py`), so the input is one figure.
#[derive(Debug, Clone, Copy, Default, PartialEq)]
pub struct Adv {
    /// Every input token.
    pub input: f64,
    /// Output.
    pub out: f64,
}

impl Tok {
    /// A stop's `tok` (`in`, `cached`, `created`, `out`) and its `adv` (the same four, the advisor's, 451 T69), none where `tok` is no
    /// object; its advisor tokens none where `adv` is none.
    #[must_use]
    pub fn of(v: &Value, adv: &Value) -> Option<Self> {
        let n = |v: &Value, k: &str| v.get(k).and_then(Value::as_f64).unwrap_or(0.0);
        v.as_object().map(|_| Self {
            fresh: n(v, "in"),
            cached: n(v, "cached"),
            created: n(v, "created"),
            out: n(v, "out"),
            adv: adv.as_object().map(|_| Adv {
                input: n(adv, "in") + n(adv, "cached") + n(adv, "created"),
                out: n(adv, "out"),
            }),
        })
    }

    /// A transcript row's `message.usage`: its top level, and its `advisor_message` iterations apart (451 T69).
    fn of_usage(u: &Value) -> Self {
        let n = |v: &Value, k: &str| v.get(k).and_then(Value::as_f64).unwrap_or(0.0);
        let adv = u
            .get("iterations")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
            .filter(|i| i.get("type").and_then(Value::as_str) == Some("advisor_message"))
            .fold(Adv::default(), |a, i| Adv {
                input: a.input
                    + n(i, "input_tokens")
                    + n(i, "cache_read_input_tokens")
                    + n(i, "cache_creation_input_tokens"),
                out: a.out + n(i, "output_tokens"),
            });
        Self {
            fresh: n(u, "input_tokens"),
            cached: n(u, "cache_read_input_tokens"),
            created: n(u, "cache_creation_input_tokens"),
            out: n(u, "output_tokens"),
            adv: Some(adv),
        }
    }

    /// Every input token, cached or not.
    #[must_use]
    pub fn input(&self) -> f64 {
        self.fresh + self.cached + self.created
    }

    /// The two summed, their advisor tokens the sum of those counted.
    #[must_use]
    pub fn plus(self, o: Self) -> Self {
        let adv = match (self.adv, o.adv) {
            (Some(a), Some(b)) => Some(Adv {
                input: a.input + b.input,
                out: a.out + b.out,
            }),
            (a, b) => a.or(b),
        };
        Self {
            fresh: self.fresh + o.fresh,
            cached: self.cached + o.cached,
            created: self.created + o.created,
            out: self.out + o.out,
            adv,
        }
    }
}

/// The agents' transcripts' usage rows, each agent's by message id, the first row of an id kept (a message is written once per block:
/// a message id's first row and its last carried the same usage on each of the 305 ids of a builder's transcript, measured 2026-11-27,
/// 451 T512); and a main session's own transcript's rows (`<sid>.jsonl`), each with its time (451 T512).
#[derive(Debug, Default)]
pub struct Tokens {
    by_aid: HashMap<String, HashMap<String, Tok>>,
    by_sid: HashMap<String, HashMap<String, (f64, Tok)>>,
}

/// A transcript's usage rows inside the window: (message id, time, tokens).
fn usage_rows(text: &str, (lo, hi): (f64, f64)) -> Vec<(String, f64, Tok)> {
    let mut out = Vec::new();
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
            out.push((id.to_owned(), at, Tok::of_usage(u)));
        }
    }
    out
}

impl Tokens {
    /// The rows of `text`, `path`'s, inside `window`: a subagent's transcript (`subagents/agent-<aid>.jsonl`) under its agent, a
    /// session's own (`<sid>.jsonl`) under its session.
    pub fn read(&mut self, path: &Path, text: &str, window: (f64, f64)) {
        let name = path
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or_default();
        let Some(stem) = name.strip_suffix(".jsonl") else {
            return;
        };
        if let Some(aid) = stem.strip_prefix("agent-") {
            let msgs = self.by_aid.entry(aid.to_owned()).or_default();
            for (id, _, tok) in usage_rows(text, window) {
                msgs.entry(id).or_insert(tok);
            }
        } else {
            let msgs = self.by_sid.entry(stem.to_owned()).or_default();
            for (id, at, tok) in usage_rows(text, window) {
                msgs.entry(id).or_insert((at, tok));
            }
        }
    }

    /// agent id -> its model calls inside the window, each message id once (451 T512).
    #[must_use]
    pub fn calls(&self) -> HashMap<String, usize> {
        self.by_aid
            .iter()
            .map(|(aid, m)| (aid.clone(), m.len()))
            .collect()
    }

    /// session id -> its own model calls inside the window, each (time, tokens), in time order (451 T512).
    #[must_use]
    pub fn session(&self) -> HashMap<String, Vec<(f64, Tok)>> {
        self.by_sid
            .iter()
            .map(|(sid, m)| {
                let mut rows: Vec<(f64, Tok)> = m.values().copied().collect();
                rows.sort_by(|a, b| a.0.total_cmp(&b.0));
                (sid.clone(), rows)
            })
            .collect()
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
                task: task_of(&a.task, t0, starts, named),
                aid: a.aid.clone(),
                kind: a.kind.clone(),
                t0,
                secs: a.spans.iter().fold(0.0, |s, (x, y)| s + y - x),
                tok: tokens.get(&a.aid).copied().or(a.tok),
            }
        })
        .collect()
}

/// The task a line is booked to: the one it names where `named` (the command's booking by start), else the mark at `t0`.
fn task_of(task: &str, t0: f64, starts: &[(f64, String)], named: bool) -> String {
    if named && !task.is_empty() {
        task.to_owned()
    } else {
        task_at(starts, t0)
    }
}

/// Each plan re-round inside the window, `since` to `until`: a `spec-fidelity` dispatch whose rounds-table key ([`round_key`]) a dispatch
/// before it in `log` holds - the feature's log from its first line, so a round before SINCE is an earlier round (T11's plan review,
/// 2026-11-21) - its time and the task its line names ("" none), in time order. A dispatch is inside the window as `load_all` cuts one:
/// its time's text at or after `since`, at or before `until`.
///
/// # Errors
///
/// A dispatch's time the reader cannot read.
pub fn rerounds(log: &[Event], (since, until): (&str, &str)) -> Result<Vec<(f64, String)>, Raised> {
    let mut found = Vec::new();
    for e in log {
        let Some(key) = round_key(e).filter(|(agent, _)| agent.starts_with("spec-fidelity")) else {
            continue;
        };
        let t = or_s(e, "t");
        if until.is_empty() || t.as_str() <= until {
            found.push((t_of(e)?, t.as_str() >= since, key, or_s(e, "task")));
        }
    }
    found.sort_by(|a, b| a.0.total_cmp(&b.0));
    let mut seen = std::collections::HashSet::new();
    Ok(found
        .into_iter()
        .filter_map(|(t, inside, key, task)| (!seen.insert(key) && inside).then_some((t, task)))
        .collect())
}

/// The task each re-round of `found` ([`rerounds`]) is booked to, as an agent is ([`rows`]).
#[must_use]
pub fn booked(found: &[(f64, String)], starts: &[(f64, String)], named: bool) -> Vec<String> {
    found
        .iter()
        .map(|(t, task)| task_of(task, *t, starts, named))
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

/// (in, out) in thousands, "-" each where none was counted.
fn pair(t: Option<(f64, f64)>) -> (String, String) {
    t.map_or(("-".to_owned(), "-".to_owned()), |(i, o)| (k(i), k(o)))
}

/// A sum's figure, "0.0" where none was counted.
fn zero(n: String) -> String {
    if n == "-" {
        "0.0".to_owned()
    } else {
        n
    }
}

/// `n word`, plural but for one.
fn count(n: usize, word: &str) -> String {
    format!("{n} {word}{}", if n == 1 { "" } else { "s" })
}

/// The tasks' agents and rework - the refused landings and the plan re-rounds, each re-round's task - (one row a task of `order`, then
/// `all`), each agent under its task where `each` (`make feature-report` leaves that list to `make where-time`, T11), and the line
/// setting their sum beside the critical path's `critical` seconds.
#[must_use]
pub fn render(
    rows: &[Row],
    (refused, rerounds): (&[Vec<String>], &[String]),
    order: &[&String],
    critical: f64,
    each: bool,
) -> String {
    let mut lines = vec![
        "| task | agents | agent minutes | k tokens in | k tokens out | k advisor in | k advisor out | refused landings | plan re-rounds | \
         by kind (count) |"
            .to_owned(),
        "|---|---|---|---|---|---|---|---|---|---|".to_owned(),
    ];
    // (in, out) of the rows' own calls, then of their advisor calls (451 T69), each "-" where none was counted
    let toks = |rs: &[&Row]| {
        let t = rs.iter().filter_map(|r| r.tok).reduce(Tok::plus);
        (
            pair(t.map(|t| (t.input(), t.out))),
            pair(t.and_then(|t| t.adv).map(|a| (a.input, a.out))),
        )
    };
    for task in order {
        let mine: Vec<&Row> = rows.iter().filter(|r| &r.task == *task).collect();
        let landings = refused.iter().filter(|ts| ts.contains(task)).count();
        let again = rerounds.iter().filter(|t| t == task).count();
        if mine.is_empty() && landings == 0 && again == 0 {
            continue;
        }
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
        let ((tin, tout), (ain, aout)) = toks(&mine);
        lines.push(format!(
            "| {task} | {} | {} | {tin} | {tout} | {ain} | {aout} | {landings} | {again} | {kinds} |",
            mine.len(),
            fixed(mine.iter().fold(0.0, |a, r| a + r.secs) / 60.0, 0)
        ));
    }
    let all: Vec<&Row> = rows.iter().filter(|r| order.contains(&&r.task)).collect();
    let secs = all.iter().fold(0.0, |a, r| a + r.secs);
    let ((tin, tout), (ain, aout)) = toks(&all);
    lines.push(format!(
        "| all | {} | {} | {tin} | {tout} | {ain} | {aout} | {} | {} | |",
        all.len(),
        fixed(secs / 60.0, 0),
        refused.len(),
        rerounds.len()
    ));
    if each {
        lines.extend(
            [
                "",
                "| task | agent | kind | from (UTC) | minutes | k tokens in | k tokens out | k advisor in | k advisor out |",
                "|---|---|---|---|---|---|---|---|---|",
            ]
            .map(String::from),
        );
    }
    for task in order.iter().filter(|_| each) {
        for r in all.iter().filter(|r| &r.task == *task) {
            let ((tin, tout), (ain, aout)) = toks(&[*r]);
            lines.push(format!(
                "| {task} | {} | {} | {} | {} | {tin} | {tout} | {ain} | {aout} |",
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
         ({} with no count), the advisor's own {}k in and {}k out beside them ({} with no count); rework: {}, {} (feature 451 T10, D7)",
        fixed(critical / 60.0, 0),
        fixed(secs / 60.0, 0),
        count(all.len(), "agent"),
        zero(tin),
        zero(tout),
        all.iter().filter(|r| r.tok.is_none()).count(),
        zero(ain),
        zero(aout),
        all.iter().filter(|r| r.tok.and_then(|t| t.adv).is_none()).count(),
        count(refused.len(), "refused landing"),
        count(rerounds.len(), "plan re-round")
    ));
    lines.join("\n")
}
