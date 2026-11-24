//! `agent-model-hooks` (feature 252; ported from the shell of the same name, feature 449 T041): AN AD-HOC AGENT DISPATCH STATES ITS MODEL, OR IS
//! REFUSED. A dispatch of a type with no file under `.claude/agents/` and no `model` runs on the session's model; feature 251's census found 72 such
//! runs, 62 of them on Fable. Which model fits is a decision only the caller can make, so this is a refusal and not a default (the GM, 2026-09-19:
//! *"have the hook reject it with a message saying that the caller has to specify a model and then reiterating the rules"*). A fork is recorded: the
//! harness ignores a model on it. There is no escape: a compliant dispatch is always available.
//!
//! THE TWO COMPLIANT DISPATCHES (feature 451 T216, the GM 2026-11-24: *"that ruling from before is something that I still want with regards to
//! enforcing that Sonnet should be used to read, fetch, translate, or extract. But then instead of Opus for anything that judges, I'd like it to be
//! inheriting the parent session model for anything that judges."*): reading work NAMES `sonnet` (or `haiku`); judging or building work names NO
//! model and carries a line of its prompt, `SESSION_MODEL: <what it judges or builds>`, so it inherits the session's model and follows the GM when
//! they switch it. WHY a line of the prompt and not its first line or the description: both of those are read for the task a dispatch serves
//! (`set_down_hooks/builders.rs`, `check_bundle_hooks/own.rs`). WHY the line is owed at all: an unmarked dispatch with no model is the omission
//! the 2026-09-19 ruling refuses - reading work drifting onto the expensive model. WHY any other named model is refused (`opus`, `fable`, the
//! session's own included): a name does not follow the next switch, which is what the GM asked for; the allowed names are a list, so a model alias
//! the harness adds later is refused until someone decides its tier. WHY haiku is second to sonnet (measured, feature 251 R7): sonnet extracted a
//! table exactly as an opus reader had, haiku misread its columns - the message keeps only the rule that follows from it, and names
//! neither this file nor the rulings' dates (message-check, 451 T216: a reader of the refusal acts on none of them). A DEFINED type passes whatever it names: its file pins its tier, and it is
//! judged before the model is read.
//!
//! THE LINE PASSES ONLY ON A TYPE MEASURED TO INHERIT (feature 451 T217): a built-in type's own definition can set a model, and the harness then
//! runs that one whatever the prompt says - so a marked `Explore` was recorded `session-model` while it ran Opus under a Fable session. The types
//! are a list of what was measured (`INHERITS`), not a deny list of what was found pinned: a built-in nobody probed (`web-fetch`,
//! `claude-code-guide`, `statusline-setup`) and one the harness adds later are refused until someone measures them. Any refusal of an unlisted
//! type prints its own message with the two routes that work for it - name `sonnet` to read, dispatch `general-purpose` to judge or build - and
//! never the rule's "re-send the SAME dispatch" with the line, which would be refused a second time.

use std::path::{Path, PathBuf};

use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::enough;
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

/// The rule the refusal states, in one place (tests/hooks/test-agent-model-hooks.sh holds the root `CLAUDE.md` to its two clauses and its line).
const RULE: &str = include_str!("agent_model_rule.txt");

/// The models an ad-hoc dispatch may NAME: the reading tiers. Anything else named is refused (see the module's WHY).
pub(crate) const READING: [&str; 2] = ["sonnet", "haiku"];

/// The ad-hoc types whose model-less dispatch runs on the SESSION's model - the only ones the `SESSION_MODEL:` line passes on. MEASURED 2026-11-24
/// on a Fable 5.2 session (feature 451 T217's task line), each probe agent asked to state its own model: `general-purpose`, `Plan` and `claude`
/// with no `model` ran Fable 5.2; `Explore` with no `model` ran Opus 5.5 (its built-in definition's) and with `model: sonnet` ran Sonnet 5.5, so
/// it is not here. Matched exactly, as the harness names them. A type joins this list by the same probe, its date beside it.
pub(crate) const INHERITS: [&str; 3] = ["general-purpose", "Plan", "claude"];

/// `INHERITS` as a refusal says it: `` `general-purpose`, `Plan` and `claude` ``.
pub(crate) fn inheriting() -> String {
    let [head @ .., last] = INHERITS;
    format!("`{}` and `{last}`", head.join("`, `"))
}

/// The marker's token (`workflow_hooks` reads the same token in a script's `agent()` call).
const MARKER: &str = "SESSION_MODEL";

/// The prompt's `SESSION_MODEL: <reason>` line: a line of its own, so a sentence that mentions the token is not the decision.
static MARKED: LazyLock<Regex> = LazyLock::new(|| {
    crate::shared::regex::build(r"(?m)^[ \t]*SESSION_MODEL:[ \t]*(.*)$")
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// Is `why` a reason - the escapes' floor cleared, and not the refusal's own `<what it judges or builds ...>` placeholder pasted back, which
/// decides nothing and would put the template in the audit log?
pub(crate) fn decided(why: &str) -> bool {
    enough(why) && !why.starts_with('<')
}

/// The reason on the prompt's `SESSION_MODEL:` line where it clears the escapes' floor (two words, eight characters), else None.
fn session_model(prompt: &str) -> Option<String> {
    MARKED
        .captures_iter(prompt)
        .map_while(Result::ok)
        .filter_map(|c| c.get(1).map(|g| g.as_str().trim().to_owned()))
        .find(|why| decided(why))
}

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
    if root_of(event, session, tree)
        .join(".claude/agents")
        .join(format!("{kind}.md"))
        .is_file()
    {
        note(&format!("{kind} pins its tier in its file"), "pinned-type");
        return Vec::new();
    }
    if READING.contains(&model) {
        note(&format!("{kind} on {model}"), "model-named");
        return Vec::new();
    }
    if !INHERITS.contains(&kind) {
        // Its own definition may set its model (451 T217): the line, and an omitted model, decide nothing here.
        let (detail, rule) = if !model.is_empty() {
            (format!("{kind} on {model}"), "judging-model-named")
        } else if session_model(given("prompt")).is_some() {
            (
                format!("{kind} marked {MARKER}, a type not measured to inherit"),
                "type-not-inheriting",
            )
        } else {
            (
                format!("{kind} dispatched with no model and no {MARKER} line"),
                "no-model",
            )
        };
        log::fire(
            "agent-model",
            "blocked",
            &detail,
            rule,
            &event.input,
            session,
        );
        return vec![Answer::Refuse(format!(
            "\n\u{1b}[1mBLOCKED: this `{kind}` agent would not run on the session's model - only {} inherit it.\u{1b}[0m\n  - to read, fetch, translate or extract, re-send it with\n        model: \"sonnet\"\n  - for anything that judges or builds, dispatch `general-purpose` instead, with NO `model` and a prompt\n    line of its own (not the first):\n        {MARKER}: <what it judges or builds, two words or more>\n",
            inheriting()
        ))];
    }
    let (detail, rule, head) = if model.is_empty() {
        if let Some(why) = session_model(given("prompt")) {
            note(
                &format!("{kind} on the session's model: {why}"),
                "session-model",
            );
            return Vec::new();
        }
        (
            format!("{kind} dispatched with no model and no {MARKER} line"),
            "no-model",
            format!("this `{kind}` agent names no model and carries no `{MARKER}:` line, so nobody decided what it runs on."),
        )
    } else {
        (
            format!("{kind} on {model}"),
            "judging-model-named",
            format!("this `{kind}` agent names `{model}`, which would not follow the session's model when the GM switches it - omit `model`, unless it only reads."),
        )
    };
    log::fire(
        "agent-model",
        "blocked",
        &detail,
        rule,
        &event.input,
        session,
    );
    vec![Answer::Refuse(format!(
        "\n\u{1b}[1mBLOCKED: {head}\u{1b}[0m\n{RULE}"
    ))]
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    let tree = std::env::var("L7R_GUARD_TREE").map_or(here, PathBuf::from);
    judge(event, session, &tree)
}

#[cfg(test)]
mod tests;
