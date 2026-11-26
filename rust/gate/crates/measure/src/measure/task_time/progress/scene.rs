//! Who is running, read from the lines (feature 451 T293; the rule and its measurement are `progress`'s doc): each agent's start,
//! stop and last own line, who dispatched it, each session's latest `Stop` and the calls open at this moment.

use std::collections::{HashMap, HashSet};

use serde_json::Value;

use super::super::super::events::{get, is, or_s, t_of, Event, Raised};
use super::super::book::{actor, review_cat};
use super::iso_of;

/// What the lines say of one agent.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct Seen {
    /// Its kind, `?` where no start names one.
    pub kind: String,
    /// The task its lines name.
    pub task: String,
    /// Its log's feature.
    pub feature: String,
    /// Its session.
    pub sid: String,
    /// Its first line read.
    pub t0: f64,
    /// Its stop, where one was kept (the reader keeps the first, 451 T324).
    pub stop: Option<f64>,
    /// Its last own line.
    pub last: f64,
    /// Its own lines run on after its stop.
    pub resumed: bool,
    /// The agent that dispatched it, "" for a session.
    pub parent: String,
    /// Its stop's context.
    pub ctx: Option<u64>,
}

impl Seen {
    /// Whether it is a builder: no review kind's agent.
    pub fn builder(&self) -> bool {
        review_cat(&self.kind).is_none()
    }

    /// Its task as a reader names it (`451 T293`), `no task` where its lines name none.
    pub fn name(&self) -> String {
        if self.task.is_empty() {
            "no task".to_owned()
        } else {
            format!("{} {}", number(&self.feature), self.task)
        }
    }
}

/// A feature's number: `451` of `451-time-retro`.
pub fn number(feature: &str) -> &str {
    feature.split('-').next().unwrap_or(feature)
}

/// Whose line it is: an agent's own start and stop are its own, every other line its actor's.
pub fn who(e: &Event) -> String {
    if is(e, "ev", "SubagentStart") || is(e, "ev", "SubagentStop") {
        or_s(e, "aid")
    } else {
        actor(e)
    }
}

/// A call open at `now`, closed there: the line its end would write, made for the booking and never written.
pub fn closed(pre: &Event, now: f64) -> Event {
    let mut e = pre.clone();
    e.insert("ev".to_owned(), Value::String("PostToolUse".to_owned()));
    e.insert("t".to_owned(), Value::String(iso_of(now)));
    e
}

/// The agents, the sessions' latest stops and the open calls.
#[derive(Debug, Default)]
pub struct Scene {
    /// Each agent by id.
    pub seen: HashMap<String, Seen>,
    /// The agents in the order first met.
    pub order: Vec<String>,
    /// session -> its latest `Stop`: when, and the ids it names in flight (None: a `Stop` written before the field).
    stops: HashMap<String, (f64, Option<HashSet<String>>)>,
    /// The calls open now: each actor's `PreToolUse` with no end, begun no earlier than its last call that ended and after its
    /// last stop - an earlier one with no end was refused by a guard and never ran.
    pub open: Vec<Event>,
}

impl Scene {
    /// The scene of `stream`, in time order.
    ///
    /// # Errors
    ///
    /// A line's time the reader cannot read.
    pub fn of(stream: &[Event]) -> Result<Self, Raised> {
        let mut s = Self::default();
        let ended: HashSet<String> = stream
            .iter()
            .filter(|e| is(e, "ev", "PostToolUse") || is(e, "ev", "PostToolUseFailure"))
            .map(|e| or_s(e, "id"))
            .collect();
        // actor -> (its last call that ended began, its last stop or prompt)
        let mut bar: HashMap<String, (f64, f64)> = HashMap::new();
        let mut pending: Vec<(f64, &Event)> = Vec::new();
        let mut parents: HashMap<String, String> = HashMap::new();
        for e in stream {
            let (t, ev, me) = (t_of(e)?, or_s(e, "ev"), who(e));
            let agent = !me.starts_with("s:");
            if agent {
                if !s.seen.contains_key(&me) {
                    s.order.push(me.clone());
                }
                let a = s.seen.entry(me.clone()).or_insert_with(|| Seen {
                    kind: "?".to_owned(),
                    feature: or_s(e, "feature"),
                    sid: or_s(e, "sid"),
                    t0: t,
                    last: t,
                    ..Seen::default()
                });
                if a.task.is_empty() {
                    a.task = or_s(e, "task");
                }
                if ev == "SubagentStart" && a.kind == "?" && !or_s(e, "agent").is_empty() {
                    a.kind = or_s(e, "agent");
                }
                if ev == "SubagentStop" {
                    a.stop = Some(t);
                    a.ctx = get(e, "ctx").as_u64();
                } else if ev != "SubagentStart" {
                    a.resumed |= a.stop.is_some();
                }
                a.last = a.last.max(t);
            }
            match ev.as_str() {
                "PreToolUse" if ended.contains(&or_s(e, "id")) => bar.entry(me).or_default().0 = t,
                "PreToolUse" => pending.push((t, e)),
                "Stop" => {
                    let named = get(e, "inflight").as_array().map(|l| {
                        l.iter()
                            .filter_map(|x| x.get("id").and_then(Value::as_str))
                            .map(str::to_owned)
                            .collect()
                    });
                    s.stops.insert(or_s(e, "sid"), (t, named));
                    bar.entry(me).or_default().1 = t;
                }
                "SubagentStop" | "UserPromptSubmit" => bar.entry(me).or_default().1 = t,
                "PostToolUse" if is(e, "tool", "Agent") => {
                    // the launch's line names the agent it started
                    let kid = or_s(e, "aid");
                    if agent && !kid.is_empty() {
                        parents.insert(kid, me);
                    }
                }
                _ => {}
            }
        }
        for (kid, parent) in parents {
            if let Some(a) = s.seen.get_mut(&kid) {
                a.parent = parent;
            }
        }
        s.open = pending
            .into_iter()
            .filter(|(t, e)| {
                let (done, stop) = bar.get(&actor(e)).copied().unwrap_or_default();
                *t >= done && *t > stop
            })
            .map(|(_, e)| e.clone())
            .collect();
        Ok(s)
    }

    /// Whether `id` of session `sid`, last heard from at `at`, is in flight by the session's latest `Stop`: named on it, or heard
    /// from after it; true where no `Stop` can say.
    pub fn in_flight(&self, sid: &str, id: &str, at: f64) -> bool {
        match self.stops.get(sid) {
            Some((t, Some(named))) => named.contains(id) || at > *t,
            _ => true,
        }
    }

    /// Whether agent `aid` is running now (`progress`'s doc): no stop, or resumed after it, and in flight.
    pub fn running(&self, aid: &str) -> bool {
        self.seen
            .get(aid)
            .is_some_and(|a| (a.stop.is_none() || a.resumed) && self.in_flight(&a.sid, aid, a.last))
    }

    /// `mine` and every agent they dispatched, and those dispatched.
    pub fn family(&self, mine: &[String]) -> HashSet<String> {
        let mut out: HashSet<String> = mine.iter().cloned().collect();
        loop {
            let more: Vec<String> = self
                .seen
                .iter()
                .filter(|(aid, a)| out.contains(&a.parent) && !out.contains(*aid))
                .map(|(aid, _)| aid.clone())
                .collect();
            if more.is_empty() {
                return out;
            }
            out.extend(more);
        }
    }
}
