//! A task's TURNS (model calls) and TOKENS (feature 451 T512; the GM's fifth process-reviewer message, 2026-11-27, kept in
//! `specs/449-rust-codebase/port-talk-gm-goal.md`: token cost "just as important as task throughput"), read back from the
//! transcripts the report already reads - no new writer.
//!
//! AN AGENT's calls are its transcript's message ids over the read-back (`spent::Tokens`), all under the task its lines name, a
//! builder (an agent no review kind claims, `book::review_cat`) apart from a review agent. THE MAIN SESSION's calls are its own
//! transcript's, each booked to the first task its own tool calls NAME (451 T513): the `names` its `PreToolUse` line carries (the
//! writer's `event_log_hooks::session_names` - every `T=` a command gives, a done ref it names, a dispatch's description, marker or
//! `Blocks:` line), else for a line written before that field the same function over the transcript's own tool call; the line's log
//! is the task's feature. The `task` a session line is filed under is never read: an orchestrating session's lines carry its
//! `make task-start` mark while it dispatches others (T312's while it dispatched T512, 2026-11-27). WHY the call's own tool ids and
//! not, as T512 read it, the next own line by time: the session shares its id with every pool tree's check runs, whose `Phase` lines
//! carry no `by`, so 192 of the session's 1,267 calls from 2026-11-27T04:30Z were booked to a builder's `Phase` line (observed
//! 2026-11-27, method: the session transcript's calls joined to the next no-`by` line of the 451, 461, 462 and `_unassigned` logs, a
//! script). A session call after a landed task's own table ends (its carry) is the second tier's, not the task's. The calls booked
//! to no task are counted from the window's start only (the read-back before it carries a landed task's time, never the unbooked
//! figure), by why: a reply (no tool call), tool calls naming no task, a task named with no line to file it, past its task's carry.

use std::collections::{HashMap, HashSet};

use super::super::events::{get, is, or_s, Event};
use super::super::where_time::columns::spent::{Call, Tok};
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
    /// The two summed (a bundle's tasks', 451 T514).
    #[must_use]
    pub fn plus(self, o: &Self) -> Self {
        Self {
            builders: self.builders + o.builders,
            agents: self.agents + o.agents,
            session: self.session + o.session,
            builders_tok: self.builders_tok.plus(o.builders_tok),
            agents_tok: self.agents_tok.plus(o.agents_tok),
            session_tok: self.session_tok.plus(o.session_tok),
        }
    }

    /// Every call's tokens.
    #[must_use]
    pub fn tok(&self) -> Tok {
        self.builders_tok
            .plus(self.agents_tok)
            .plus(self.session_tok)
    }
}

/// What the transcripts gave: agent id -> calls, agent id -> tokens, session id -> its calls.
pub struct Read<'a> {
    /// Each agent's calls.
    pub calls: &'a HashMap<String, usize>,
    /// Each agent's tokens.
    pub tokens: &'a HashMap<String, Tok>,
    /// Each session's own calls.
    pub session: &'a HashMap<String, Vec<Call>>,
    /// The page sessions' ids, whose transcripts are no main session's.
    pub paged: &'a HashSet<String>,
}

/// The main session's calls booked to no task inside the window: their count and tokens, and the count by why (451 T513).
#[derive(Debug, Default, Clone, Copy, PartialEq)]
pub struct Unbooked {
    /// Every one.
    pub calls: usize,
    /// Their tokens.
    pub tok: Tok,
    /// A reply or a thought: no tool call.
    pub replies: usize,
    /// Tool calls naming no task.
    pub unnamed: usize,
    /// A task named, but no own line of the call to file it under a feature.
    pub unlogged: usize,
    /// After its task's own table ended: the second tier's.
    pub carried: usize,
}

/// Each key's turns, and the session's calls booked to no task from `lo` on: `ends` is where a landed task's own table ends.
#[must_use]
#[expect(clippy::implicit_hasher, reason = "the report's own maps, one hasher")]
pub fn of(
    stream: &[Event],
    agents: &[Agent],
    read: &Read,
    (ends, lo): (&HashMap<Key, f64>, f64),
) -> (HashMap<Key, Turns>, Unbooked) {
    let mut out: HashMap<Key, Turns> = HashMap::new();
    let mut feature: HashMap<String, String> = HashMap::new();
    // the session's own tool lines by tool-use id: (the line's feature, the tasks it names, none for a line before the field)
    let mut own: HashMap<String, (String, Option<Vec<String>>)> = HashMap::new();
    for e in stream {
        let aid = or_s(e, "aid");
        if !aid.is_empty() {
            feature.entry(aid).or_insert_with(|| or_s(e, "feature"));
        }
        if or_s(e, "by").is_empty() && is(e, "ev", "PreToolUse") {
            let names = get(e, "names").as_array().map(|a| {
                a.iter()
                    .filter_map(|v| v.as_str().map(str::to_owned))
                    .collect()
            });
            own.insert(or_s(e, "id"), (or_s(e, "feature"), names));
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
    let mut unbooked = Unbooked::default();
    for call in read
        .session
        .iter()
        .filter(|(sid, _)| !read.paged.contains(*sid))
        .flat_map(|(_, calls)| calls)
    {
        // the first tool call naming a task: its line's names, else (a line before the field) the transcript's
        let named = call.uses.iter().find_map(|(id, said)| {
            let line = own.get(id);
            let names = line.and_then(|(_, n)| n.as_ref()).unwrap_or(said);
            let task = names.first()?;
            Some(line.map(|(f, _)| (f.clone(), task.clone())))
        });
        let why = match named {
            Some(Some(k)) if ends.get(&k).is_none_or(|end| call.at <= *end) => {
                let t = out.entry(k).or_default();
                t.session += 1;
                t.session_tok = t.session_tok.plus(call.tok);
                continue;
            }
            Some(Some(_)) => &mut unbooked.carried,
            Some(None) => &mut unbooked.unlogged,
            None if call.uses.is_empty() => &mut unbooked.replies,
            None => &mut unbooked.unnamed,
        };
        if call.at >= lo {
            *why += 1;
            unbooked.calls += 1;
            unbooked.tok = unbooked.tok.plus(call.tok);
        }
    }
    (out, unbooked)
}
