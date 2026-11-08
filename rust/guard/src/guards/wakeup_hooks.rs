//! `wakeup-hooks` (feature 263; ported from the shell of the same name, feature 449 T038): A TIMED WAKEUP CANNOT OUTLIVE ITS PURPOSE (the GM,
//! 2026-09-26: *"It needs to be literally impossible for them to do the wrong thing."*). A `ScheduleWakeup` outside a live `/loop` is refused; a turn
//! cannot end with one pending, every turn end, naming `CronDelete <id>`. The transcript tells a wakeup from a reminder the GM asked for and a live
//! loop from a stopped one. No escape. The call fails closed on an unreadable transcript, the turn end open, because without the transcript it
//! cannot tell a wakeup from a reminder.

use std::collections::HashSet;
use std::fs::File;
use std::io::{self, BufRead, BufReader};

use serde_json::Value;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "wakeup-hooks",
    events: &["PreToolUse", "Stop"],
    matcher: "ScheduleWakeup",
    decide,
};

const SENTINEL: &str = "<<autonomous-loop-dynamic>>";

/// What the transcript says: every `ScheduleWakeup` prompt, and whether a loop is live.
#[derive(Default)]
struct Seen {
    prompts: HashSet<String>,
    live: bool,
}

/// A loop's own wakeup: its prompt is the loop input prefixed with `/loop `, or the autonomous sentinel.
fn is_loop_prompt(text: &str) -> bool {
    let t = text.trim();
    t.starts_with("/loop ") || t == "/loop" || t == SENTINEL
}

fn set(v: Option<&Value>) -> bool {
    v.is_some_and(|x| !x.is_null() && *x != Value::Bool(false))
}

fn absorb_block(b: &Value, seen: &mut Seen) {
    if field(b, "type") != "tool_use" {
        return;
    }
    let null = Value::Null;
    let inp = b.get("input").unwrap_or(&null);
    match field(b, "name") {
        "ScheduleWakeup" if set(inp.get("stop")) => seen.live = false,
        "ScheduleWakeup" if !field(inp, "prompt").is_empty() => {
            seen.prompts.insert(field(inp, "prompt").to_owned());
        }
        "Skill" if field(inp, "skill") == "loop" => seen.live = true,
        _ => {}
    }
}

fn says_loop(content: Option<&Value>) -> bool {
    const COMMAND: &str = "<command-name>/loop</command-name>";
    match content {
        Some(Value::String(t)) => t.contains(COMMAND),
        Some(Value::Array(blocks)) => blocks.iter().any(|b| field(b, "text").contains(COMMAND)),
        _ => false,
    }
}

fn absorb(r: &Value, seen: &mut Seen) -> io::Result<()> {
    if !r.is_object() {
        return Err(io::Error::other("a transcript line that is not an entry"));
    }
    let content = r.get("message").and_then(|m| m.get("content"));
    if field(r, "type") == "user" && says_loop(content) {
        seen.live = true;
    }
    for b in content.and_then(Value::as_array).into_iter().flatten() {
        absorb_block(b, seen);
    }
    Ok(())
}

fn read(path: &str) -> io::Result<Seen> {
    let mut seen = Seen::default();
    for line in BufReader::new(File::open(path)?).lines() {
        let line = line?;
        if !line.contains("/loop") && !line.contains("ScheduleWakeup") && !line.contains("\"loop\"")
        {
            continue;
        }
        if let Ok(r) = serde_json::from_str::<Value>(&line) {
            absorb(&r, &mut seen)?;
        }
    }
    Ok(seen)
}

const OWN_PROMPT: &str = "BLOCKED: a live /loop paces itself with its OWN prompt - \"/loop <the loop input>\" - and this wakeup carries\nsomething else, which makes it a fallback timer riding on the loop (feature 263). Re-arm with the loop prompt.";
const OUTSIDE: &str = "BLOCKED: ScheduleWakeup outside /loop (feature 263).

ScheduleWakeup is the /loop pacing tool. Outside a loop it is a fallback timer, and a fallback outlives
its purpose: on 2026-09-26 one stayed pending after the work it guarded had landed, and the GM's tab
showed the hourglass instead of waiting-for-you. You do not need one:
  - background work (a shell, an agent, a workflow) wakes this session by itself when it finishes;
  - a stalled agent is reported by agent-stall-hooks.sh;
  - a reminder the GM asked for (\"remind me at 3pm\") is CronCreate's job, not this tool's.
There is no escape: a case that seems to need one is a process question for the round arbiter first
(make arbiter-ask SUBJECT=<id> WHY=\"<the case>\"), not a token.";
const UNREADABLE: &str = "BLOCKED: ScheduleWakeup, and this guard could not establish that the session is running a live /loop\n(its transcript was unreadable, or the check itself failed - REFUSE unreadable). Outside a loop, background work wakes\nthe session by itself; a reminder the GM asked for is CronCreate's job. (feature 263)";

fn refuse(rule: &str, text: &str, event: &Event, session: &Session) -> Vec<Answer> {
    log::fire(
        "wakeup",
        "blocked",
        "ScheduleWakeup",
        rule,
        &event.input,
        session,
    );
    vec![Answer::Refuse(text.to_owned())]
}

fn pretool(event: &Event, session: &Session) -> Vec<Answer> {
    if event.tool() != "ScheduleWakeup" && !event.tool().is_empty() {
        return Vec::new();
    }
    let null = Value::Null;
    let input = event.input.get("tool_input").unwrap_or(&null);
    let ending = set(input.get("stop"));
    let Ok(seen) = read(field(&event.input, "transcript_path")) else {
        return if ending {
            Vec::new()
        } else {
            refuse("unreadable", UNREADABLE, event, session)
        };
    };
    if event.tool().is_empty() {
        return Vec::new();
    }
    if ending || (seen.live && is_loop_prompt(field(input, "prompt"))) {
        return Vec::new();
    }
    if seen.live {
        refuse("not-the-loop-prompt", OWN_PROMPT, event, session)
    } else {
        refuse("outside-loop", OUTSIDE, event, session)
    }
}

/// One line of the block for a pending cron, or None when it is no stale wakeup.
fn stale_line(cron: &Value, seen: &Seen) -> Option<String> {
    let (id, prompt) = (field(cron, "id"), field(cron, "prompt"));
    if id.is_empty() || !seen.prompts.contains(prompt) || (seen.live && is_loop_prompt(prompt)) {
        return None;
    }
    let short: String = prompt.chars().take(80).collect();
    let shown = short.replace('\n', " ").replace('|', "/");
    Some(format!(
        "    CronDelete {id}      ({}: {shown})",
        field(cron, "schedule")
    ))
}

fn stop(event: &Event, session: &Session) -> Vec<Answer> {
    let Ok(seen) = read(field(&event.input, "transcript_path")) else {
        return Vec::new();
    };
    let crons = event.input.get("session_crons").and_then(Value::as_array);
    let lines: Vec<String> = crons
        .into_iter()
        .flatten()
        .filter_map(|c| stale_line(c, &seen))
        .collect();
    if lines.is_empty() {
        return Vec::new();
    }
    log::fire(
        "wakeup",
        "blocked",
        "stop",
        "stale-wakeup",
        &event.input,
        session,
    );
    vec![Answer::Refuse(format!(
        "A WAKEUP WOULD OUTLIVE THIS TURN (feature 263): a ScheduleWakeup is still pending outside /loop.\nIt keeps the GM's tab on the hourglass and brings this session back for nothing. Cancel it:\n{}\nBackground work wakes this session by itself when it finishes; nothing needs a timer.",
        lines.join("\n")
    ))]
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    if event.name == "Stop" {
        stop(event, session)
    } else {
        pretool(event, session)
    }
}

#[cfg(test)]
mod tests;
