//! A task's TURNS (model calls) and TOKENS (feature 451 T512; the GM's fifth process-reviewer message, 2026-11-27, kept in
//! `specs/449-rust-codebase/port-talk-gm-goal.md`: token cost "just as important as task throughput"), read back from the
//! transcripts the report already reads - no new writer.
//!
//! AN AGENT's calls are its transcript's message ids over the read-back (`spent::Tokens`), all under the task its lines name, a
//! builder (an agent no review kind claims, `book::review_cat`) apart from a review agent. THE MAIN SESSION's calls are its own
//! transcript's, each booked to the task its NEXT own event-log line names - the line its call produced, as `book` books a model
//! turn by the tool its call is - where that line names one itself; a line carrying only the session's `make task-start` mark
//! (`fallback`) books the call to no task, since an orchestrating session's mark stays on one task while it dispatches others (it
//! was T312 while it dispatched T512, 2026-11-27). A session call after a landed task's own table ends (its carry) is the second
//! tier's, not the task's.

use std::collections::{HashMap, HashSet};

use super::super::events::{get, is, or_s, t_of, Event};
use super::super::where_time::columns::spent::Tok;
use super::super::where_time::columns::Agent;
use super::book::{review_cat, Key};

/// A task's model calls and their tokens, by who made them.
#[derive(Debug, Default, Clone, Copy, PartialEq)]
pub struct Turns {
    /// Its builders' model calls.
    pub builders: usize,
    /// Its review agents' model calls.
    pub agents: usize,
    /// The main session's model calls booked to it.
    pub session: usize,
    /// The builders' tokens.
    pub builders_tok: Tok,
    /// The review agents' tokens.
    pub agents_tok: Tok,
    /// The session's tokens booked to it.
    pub session_tok: Tok,
}

impl Turns {
    /// Every call.
    #[must_use]
    pub fn calls(&self) -> usize {
        self.builders + self.agents + self.session
    }

    /// Every call's tokens.
    #[must_use]
    pub fn tok(&self) -> Tok {
        self.builders_tok
            .plus(self.agents_tok)
            .plus(self.session_tok)
    }
}

/// What the transcripts gave: agent id -> calls, agent id -> tokens, session id -> its calls' (time, tokens).
pub struct Read<'a> {
    /// Each agent's calls.
    pub calls: &'a HashMap<String, usize>,
    /// Each agent's tokens.
    pub tokens: &'a HashMap<String, Tok>,
    /// Each session's own calls.
    pub session: &'a HashMap<String, Vec<(f64, Tok)>>,
    /// The page sessions' ids, whose transcripts are no main session's.
    pub paged: &'a HashSet<String>,
}

/// Each key's turns, and the session's calls booked to no task with their tokens: `ends` is where a landed task's own table ends.
#[must_use]
#[expect(clippy::implicit_hasher, reason = "the report's own maps, one hasher")]
pub fn of(
    stream: &[Event],
    agents: &[Agent],
    read: &Read,
    ends: &HashMap<Key, f64>,
) -> (HashMap<Key, Turns>, (usize, Tok)) {
    let mut out: HashMap<Key, Turns> = HashMap::new();
    let mut feature: HashMap<String, String> = HashMap::new();
    // a session's own lines, each (time, the task it names itself, else none)
    let mut own: HashMap<String, Vec<(f64, Option<Key>)>> = HashMap::new();
    for e in stream {
        let aid = or_s(e, "aid");
        if !aid.is_empty() {
            feature.entry(aid).or_insert_with(|| or_s(e, "feature"));
        }
        if or_s(e, "by").is_empty() && !is(e, "ev", "BgEnd") {
            let task = or_s(e, "task");
            let named = (get(e, "fallback").as_bool() != Some(true) && !task.is_empty())
                .then(|| (or_s(e, "feature"), task));
            own.entry(or_s(e, "sid"))
                .or_default()
                .push((t_of(e).unwrap_or(0.0), named));
        }
    }
    for a in agents {
        let key = (
            feature.get(&a.aid).cloned().unwrap_or_default(),
            if a.task.is_empty() {
                "-".to_owned()
            } else {
                a.task.clone()
            },
        );
        let t = out.entry(key).or_default();
        let (n, tok) = (
            read.calls.get(&a.aid).copied().unwrap_or(0),
            read.tokens.get(&a.aid).copied().unwrap_or_default(),
        );
        if review_cat(&a.kind).is_none() {
            t.builders += n;
            t.builders_tok = t.builders_tok.plus(tok);
        } else {
            t.agents += n;
            t.agents_tok = t.agents_tok.plus(tok);
        }
    }
    let mut unbooked = (0, Tok::default());
    for (sid, rows) in read
        .session
        .iter()
        .filter(|(sid, _)| !read.paged.contains(*sid))
    {
        let lines = own.get(sid).map_or(&[][..], Vec::as_slice);
        for (at, tok) in rows {
            // the first own line at or after the call: the line the call produced
            let i = lines.partition_point(|(t, _)| t < at);
            let key = lines.get(i).and_then(|(_, k)| k.clone());
            match key.filter(|k| ends.get(k).is_none_or(|end| at <= end)) {
                Some(k) => {
                    let t = out.entry(k).or_default();
                    t.session += 1;
                    t.session_tok = t.session_tok.plus(*tok);
                }
                None => unbooked = (unbooked.0 + 1, unbooked.1.plus(*tok)),
            }
        }
    }
    (out, unbooked)
}
