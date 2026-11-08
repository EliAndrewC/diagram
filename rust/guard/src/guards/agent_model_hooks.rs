//! `agent-model-hooks` (feature 252; ported from the shell of the same name, feature 449 T041): AN AD-HOC AGENT DISPATCH NAMES ITS MODEL, OR IS
//! REFUSED. A dispatch of a type with no file under `.claude/agents/` runs on the session's model; feature 251's census found 72 such runs, 62 of them
//! on Fable. Which model fits is a decision only the caller can make, so this is a refusal and not a default (the GM, 2026-09-19: *"have the hook
//! reject it with a message saying that the caller has to specify a model and then reiterating the rules"*). A fork is recorded: the harness ignores
//! a model on it. There is no escape: the compliant dispatch is always available and is one field.

use std::path::{Path, PathBuf};

use crate::protocol::{Answer, Event, Guard};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "agent-model-hooks",
    events: &["PreToolUse"],
    matcher: "Agent",
    decide,
};

/// The rule the refusal states, in one place (tests/hooks/test-agent-model-hooks.sh holds the root `CLAUDE.md` to its two clauses).
const RULE: &str = include_str!("agent_model_rule.txt");

/// The tree whose `.claude/agents/` says what is pinned: the session's clone, else the work tree `cwd` stands in, else `tree`'s scripts directory.
fn root_of(event: &Event, session: &Session, tree: &Path) -> PathBuf {
    if let Some(clone) = session.clone_dir().filter(|c| c.is_dir()) {
        return clone.to_path_buf();
    }
    let cwd = Some(field(&event.input, "cwd"))
        .filter(|c| !c.is_empty())
        .unwrap_or(".");
    let said = ask(
        Path::new("."),
        "git",
        &["-C", cwd, "rev-parse", "--show-toplevel"],
        "",
    );
    if said.ok() {
        return PathBuf::from(said.out.trim());
    }
    tree.join("scripts")
}

pub(crate) fn judge(event: &Event, session: &Session, tree: &Path) -> Vec<Answer> {
    if event.tool() != "Agent" {
        return Vec::new();
    }
    let input = event.input.get("tool_input");
    let given = |key: &str| input.map_or("", |t| field(t, key));
    let kind = Some(given("subagent_type"))
        .filter(|k| !k.is_empty())
        .unwrap_or("general-purpose");
    let model = given("model");
    let note = |detail: &str, rule: &str| {
        log::fire(
            "agent-model",
            "permitted",
            detail,
            rule,
            &event.input,
            session,
        );
    };
    if kind == "fork" {
        note(
            "a fork runs on its parent's model; a model on it is ignored",
            "fork-inherits",
        );
        return Vec::new();
    }
    if !model.is_empty() {
        note(&format!("{kind} on {model}"), "model-named");
        return Vec::new();
    }
    if root_of(event, session, tree)
        .join(".claude/agents")
        .join(format!("{kind}.md"))
        .is_file()
    {
        note(&format!("{kind} pins its tier in its file"), "pinned-type");
        return Vec::new();
    }
    log::fire(
        "agent-model",
        "blocked",
        &format!("{kind} dispatched with no model"),
        "no-model",
        &event.input,
        session,
    );
    vec![Answer::Refuse(format!(
        "\n\u{1b}[1mBLOCKED: this `{kind}` agent names no model, so it would run on the SESSION's model.\u{1b}[0m\n{RULE}\n(rust/guard/src/guards/agent_model_hooks.rs; feature 252, the GM 2026-09-19)"
    ))]
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    let tree = std::env::var("L7R_GUARD_TREE").map_or(here, PathBuf::from);
    judge(event, session, &tree)
}

#[cfg(test)]
mod tests;
