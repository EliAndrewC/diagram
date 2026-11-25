//! `research-switch-hooks` (feature 451 T244, the GM 2026-11-25: "I would like to essentially defer all of it until at least tomorrow
//! ... will our current procedures end up inadvertently kicking off a bunch of research tasks"): WHILE THE RESEARCH SWITCH IS `deferred`
//! (`dev/switches.json`, read by `shared::switches`), NO SEARCH PASS AND NO PAGE SESSION STARTS UNASKED. A `research-pass` dispatch (a
//! `check-wave` unit too, which `workflow_hooks` puts through the Agent hooks) and a `make page-session` invocation are refused, naming
//! the switch; `RESEARCH_OK="<reason>"` in the prompt or the command lets one through, recorded. While `open` the guard is silent.

use std::path::Path;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{self, escape_or_refuse, Escape};
use crate::shared::log;
use crate::shared::make::targets;
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::switches::{research, Research};

/// The guard.
pub const GUARD: Guard = Guard {
    name: "research-switch-hooks",
    events: &["PreToolUse"],
    matcher: "Agent|Bash",
    decide,
};

const TOKEN: &str = "RESEARCH_OK";

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let root = session
        .clone_dir()
        .map_or_else(|| session.main().to_path_buf(), Path::to_path_buf);
    judge(event, session, &root)
}

/// What starts research here: `research-pass` (an Agent dispatch) or `page-session` (a make target), with the text an escape is read
/// from; None for anything else.
fn starts(event: &Event) -> Option<(&'static str, &str)> {
    let input = event.input.get("tool_input")?;
    match event.tool() {
        "Agent" if field(input, "subagent_type") == "research-pass" => {
            Some(("a research-pass dispatch", field(input, "prompt")))
        }
        "Bash" => {
            let cmd = field(input, "command");
            (cmd.contains("page-session") && targets(cmd).contains("page-session"))
                .then_some(("make page-session", cmd))
        }
        _ => None,
    }
}

/// The escape: a command's by the shell's rule, a prompt's by its token and reason alone (a prompt is prose, whose apostrophes the
/// shell's quote-stripping would read as quotes).
fn escaped(event: &Event, text: &str) -> Escape {
    let (escape, place) = if event.tool() == "Bash" {
        (escape_or_refuse(text, TOKEN), "command")
    } else if !text.contains(TOKEN) {
        (Escape::None, "prompt")
    } else {
        let why = escape::reason(text, TOKEN);
        if escape::enough(&why) {
            (Escape::Escaped(why), "prompt")
        } else {
            (Escape::Refused(String::new()), "prompt")
        }
    };
    // the bare token's refusal is this guard's own, short and naming where the reason goes (message-check's BREVITY cut, 2026-11-25)
    match escape {
        Escape::Refused(_) => Escape::Refused(format!(
            "BLOCKED: {TOKEN} with no reason given. Put one, two words or more, in the {place}:\n  {TOKEN}: <why this runs while research is deferred>\n"
        )),
        other => other,
    }
}

pub(crate) fn judge(event: &Event, session: &Session, root: &Path) -> Vec<Answer> {
    let Some((what, text)) = starts(event) else {
        return Vec::new();
    };
    let switch = research(root);
    if !switch.deferred() {
        return Vec::new();
    }
    match escaped(event, text) {
        Escape::Escaped(why) => {
            log::fire(
                "research-switch",
                "escaped",
                &why,
                "research-deferred",
                &event.input,
                session,
            );
            Vec::new()
        }
        Escape::Refused(text) => {
            log::fire(
                "research-switch",
                "blocked",
                what,
                "RESEARCH_OK-no-reason",
                &event.input,
                session,
            );
            vec![Answer::Refuse(text)]
        }
        Escape::None => {
            log::fire(
                "research-switch",
                "blocked",
                what,
                "research-deferred",
                &event.input,
                session,
            );
            vec![Answer::Refuse(refusal(what, &switch))]
        }
    }
}

fn refusal(what: &str, switch: &Research) -> String {
    let who = if switch.who.is_empty() {
        "?"
    } else {
        &switch.who
    };
    format!(
        "\n\u{1b}[1mBLOCKED: {what} - research is DEFERRED\u{1b}[0m (make switches; since {} by {who}: {}).\n\n\
Instead: draw the decision as a best guess labeled UNRESEARCHED; make research-backlog lists it for later.\n\
A physical task's boxes take `deferred: UNRESEARCHED` on their line.\n\
To reopen, once the GM turns to research: make research-open REASON=\"<the GM's words>\".\n\
To run this one anyway: RESEARCH_OK=\"<why, two words or more>\" in the {}.\n",
        switch.utc,
        switch.why,
        if what.starts_with("make") {
            "command"
        } else {
            "prompt"
        }
    )
}

#[cfg(test)]
mod tests;
