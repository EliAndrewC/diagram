//! What a wait between turns was waiting on (feature 451 T09, plan D3; FR-002): the runs in flight - a background Bash run, an agent,
//! a monitor - and each second of the wait booked to one of them.
//!
//! WHY. The critical path booked every second between a `Stop` and the next prompt that was not the GM's as "waiting on work", 866 of
//! the window's 1,354 minutes, measured 2026-11-21 (`make where-time F=451 SINCE=2026-11-20T04:33:00Z UNTIL=2026-11-21T03:07:24Z`):
//! the session had handed the work to a background run and waited for its notice. D3: the wait is booked to the runs its `Stop` names
//! `inflight`, else - a `Stop` written before the field - to the session's own runs whose span holds it.
//!
//! SEVERAL IN FLIGHT. The wall clock books each second once, and D3 names no rule for several runs, so each second goes to ONE run, by
//! rank, the latest started breaking a tie: a Bash run whose bucket is a named column first, in [`PRECEDENCE`]'s order (land, gate, tests,
//! review, docs, spec-kit step) - the session's own landing is what it waits on before a builder's - then an agent, then a Bash run no
//! named column claims (`background run`: most are the session's poll-waits on its builders, T08's 709 minutes of them), then a monitor,
//! which watches another run and is named on nearly every `Stop` (the `shzmgedar` monitor). A Bash run's second is split into compile and
//! a landing's gate as a call's is ([`Split`]); an agent's goes to the column a foreground wait on it has (`waiting: <its kind>`, so a
//! builder is `other subagent` and a `spec-fidelity` plan review). A second no run holds stays waiting on work.

use std::collections::HashMap;

use super::super::super::events::{get, is, or_s, t_of, Event, Raised};
use super::{Runs, Split, PRECEDENCE};

/// What the critical path books a wait's seconds to that no run holds.
pub const UNBOOKED: &str = "waiting on work";

/// One run a wait can be booked to.
#[derive(Debug, Default)]
struct Flier {
    sid: String,
    /// A subagent's own run, which the session's wait is not on unless its `Stop` names it.
    theirs: bool,
    t0: f64,
    t1: f64,
    rank: usize,
    bucket: String,
    kind: &'static str,
    split: Split,
}

/// The window's background runs and agents, by the id a `Stop`'s `inflight` names them by: a shell's background task id, an agent's id.
#[derive(Debug, Default)]
pub struct Flight {
    fliers: Vec<Flier>,
    by_id: HashMap<String, Vec<usize>>,
}

/// The rank of an agent; a Bash run of a named column ranks by its place in [`PRECEDENCE`], before it.
const AGENT: usize = PRECEDENCE.len();
/// The rank of a Bash run no named column claims, and of a monitor, last.
const OTHER: usize = AGENT + 1;
const MONITOR: usize = AGENT + 2;

/// The window's [`Flight`]: every background run of `runs`, and every span of an agent of `agents` - its `SubagentStart` and
/// `SubagentStop` lines from EVERY feature's log (`events::lines_of`), since they are filed by the active feature as the turn lines are:
/// of the main session's since 2026-11-20T04:33Z, 75 starts and 61 stops sat in 449's log, and 9 of the 115 agents a `Stop` named in
/// flight had their start only there, measured 2026-11-21 (`/tmp/t09/scripts/agents.py` over both logs). A resumed agent starts again
/// under its id (31 did), so each start opens a span to the first stop after it, else to `end`; a line two logs hold is read once. An
/// agent is this feature's only where a line of `stream` (the feature's own log) names it - its launch's `aid` or its own calls' `by`:
/// read from every log, the 449 agents the session ran over two hours of 2026-11-20 (08:32-09:35Z, 10:42-11:46Z, between 451's turns)
/// were booked to 451's waits, observed 2026-11-21, method: `/tmp/t09/scripts/idle.py` and `held.py` over both logs.
///
/// # Errors
///
/// An agent line's time the reader cannot read.
pub fn flight(runs: &Runs, agents: &[Event], stream: &[Event], end: f64) -> Result<Flight, Raised> {
    let mine: std::collections::HashSet<String> = stream
        .iter()
        .flat_map(|e| [or_s(e, "aid"), or_s(e, "by")])
        .collect();
    let mut f = Flight::default();
    for r in runs.runs.iter().filter(|r| r.bg) {
        let named = PRECEDENCE
            .iter()
            .position(|b| *b == r.bucket && *b != "other");
        f.by_id
            .entry(r.bg_id.clone())
            .or_default()
            .push(f.fliers.len());
        f.fliers.push(Flier {
            sid: r.sid.clone(),
            theirs: !r.by.is_empty(),
            t0: r.t0,
            t1: r.t1,
            rank: named.unwrap_or(OTHER),
            bucket: named.map_or("background run", |_| r.bucket).to_owned(),
            kind: "shell",
            split: Split {
                compile: r.compile.clone(),
                gate: r.gate.clone(),
            },
        });
    }
    let mut seen = std::collections::HashSet::new();
    let mut lines: Vec<(f64, &Event)> = Vec::new();
    for e in agents.iter().filter(|e| mine.contains(&or_s(e, "aid"))) {
        if seen.insert((or_s(e, "aid"), or_s(e, "ev"), or_s(e, "t"))) {
            lines.push((t_of(e)?, e));
        }
    }
    lines.sort_by(|a, b| a.0.total_cmp(&b.0));
    // aid -> its kind, from the first start that names one: a resumed agent's start may name none
    let mut kinds: HashMap<String, String> = HashMap::new();
    for (_, e) in &lines {
        let kind = or_s(e, "agent");
        if is(e, "ev", "SubagentStart") && !kind.is_empty() {
            kinds.entry(or_s(e, "aid")).or_insert(kind);
        }
    }
    for (i, (t0, e)) in lines.iter().enumerate() {
        if !is(e, "ev", "SubagentStart") {
            continue;
        }
        let aid = or_s(e, "aid");
        let stop = lines[i..]
            .iter()
            .find(|(_, x)| is(x, "ev", "SubagentStop") && or_s(x, "aid") == aid);
        let kind = kinds.get(&aid).map_or("?", String::as_str);
        f.by_id.entry(aid.clone()).or_default().push(f.fliers.len());
        f.fliers.push(Flier {
            sid: or_s(e, "sid"),
            t0: *t0,
            t1: stop.map_or(end, |(t, _)| *t),
            rank: AGENT,
            bucket: super::super::bucket(&format!("waiting: {kind}")).to_owned(),
            kind: "agent",
            ..Flier::default()
        });
    }
    Ok(f)
}

impl Flight {
    /// The wait `[lo, hi]` of session `sid`, opened by the `Stop` `opener`, as (column, what held it - `shell`, `agent`, `monitor`, or
    /// empty for none - seconds), each second once (the module's doc).
    #[must_use]
    pub fn book(
        &self,
        sid: &str,
        opener: Option<&Event>,
        lo: f64,
        hi: f64,
    ) -> Vec<(String, &'static str, f64)> {
        let monitor = Flier {
            t0: lo,
            t1: hi,
            rank: MONITOR,
            bucket: "background run".to_owned(),
            kind: "monitor",
            ..Flier::default()
        };
        let named = opener.and_then(|e| get(e, "inflight").as_array());
        let cands: Vec<&Flier> = match named {
            Some(list) => list
                .iter()
                .flat_map(|x| {
                    let id = x
                        .get("id")
                        .and_then(serde_json::Value::as_str)
                        .unwrap_or("");
                    match self.by_id.get(id) {
                        Some(all) => all.iter().map(|&i| &self.fliers[i]).collect(),
                        None => (x.get("type").and_then(serde_json::Value::as_str)
                            == Some("monitor"))
                        .then_some(vec![&monitor])
                        .unwrap_or_default(),
                    }
                })
                .collect(),
            None => self
                .fliers
                .iter()
                .filter(|c| c.sid == sid && !c.theirs)
                .collect(),
        };
        let mut cuts = vec![lo, hi];
        for c in &cands {
            cuts.extend([c.t0, c.t1].into_iter().filter(|t| lo < *t && *t < hi));
        }
        cuts.sort_by(f64::total_cmp);
        cuts.dedup();
        let mut out = Vec::new();
        for w in cuts.windows(2) {
            let (x, y) = (w[0], w[1]);
            let best = cands
                .iter()
                .filter(|c| c.t0 <= x && y <= c.t1)
                .min_by(|a, b| a.rank.cmp(&b.rank).then(b.t0.total_cmp(&a.t0)));
            let Some(c) = best else {
                out.push((UNBOOKED.to_owned(), "", y - x));
                continue;
            };
            let compile = super::overlap(&c.split.compile, x, y);
            let gate = super::overlap(&c.split.gate, x, y);
            for (col, s) in [("compile", compile), ("gate", gate)] {
                if s > 0.0 {
                    out.push((col.to_owned(), c.kind, s));
                }
            }
            out.push((c.bucket.clone(), c.kind, y - x - compile - gate));
        }
        out
    }
}

#[cfg(test)]
mod tests;
