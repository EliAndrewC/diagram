//! `no-branch-hooks` (ported from the shell of the same name, feature 449 T021): THIS PROJECT DOES NOT USE FEATURE BRANCHES, spec-kit
//! work included (GM 2026-07-27). Isolation already comes from the session clone, so a branch is a second axis that buys nothing, and
//! it broke the stop-work push for a whole session. This is the backstop for a branch made by hand; `NO_BRANCH_OK` with a reason is the
//! escape (a throwaway bisect, another session's work), and another repository under `/host-l7r-repo` is not this guard's business.

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "no-branch-hooks",
    events: &["PreToolUse"],
    matcher: "Bash",
    decide,
};

const CREATES: [&str; 6] = [
    "git checkout -b",
    "git checkout -B",
    "git switch -c",
    "git switch -C",
    "git switch --create",
    "git checkout --branch",
];

const REFUSAL: &str = "BLOCKED (no-branch): this project does not use feature branches - not even for spec-kit.

Isolation already comes from your session CLONE (.clones/<session-name>); a branch on top of it is a
second axis of isolation that buys nothing. It also broke the stop-work procedure for a whole session:
sync-with-main.sh pushed the local ref NAMED main instead of HEAD, so work committed on a branch was
rejected as non-fast-forward while every diagnostic reported it strictly ahead.

Do this instead:
  - Ordinary work: just commit on main inside your clone. That is what sync-with-main.sh done expects.
  - Spec-kit: export SPECIFY_FEATURE=NNN-slug   (common.sh get_current_branch() returns it ahead of
    git, so check_feature_branch() in setup-plan.sh / setup-tasks.sh passes with no branch at all).
    Branch creation is already off - .specify/extensions.yml, before_specify, enabled: false.

If you genuinely need a branch (a throwaway bisect, recovering another session's work), put
NO_BRANCH_OK in the command with a note saying why.

(rust/guard/src/guards/no_branch_hooks.rs; GM 2026-07-27)";

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let cmd = event
        .input
        .get("tool_input")
        .map_or("", |t| field(t, "command"));
    if cmd.is_empty() {
        return Vec::new();
    }
    let shown: String = cmd.chars().take(200).collect();
    match escape_or_refuse(cmd, "NO_BRANCH_OK") {
        Escape::Escaped(why) => {
            log::fire(
                "no-branch",
                "escaped",
                &why,
                "no-branch-ok",
                &event.input,
                session,
            );
            return Vec::new();
        }
        Escape::Refused(text) => {
            log::fire(
                "no-branch",
                "blocked",
                &shown,
                "NO_BRANCH_OK-no-reason",
                &event.input,
                session,
            );
            return vec![Answer::Refuse(text)];
        }
        Escape::None => {}
    }
    if !CREATES.iter().any(|c| cmd.contains(c)) || cmd.contains("/host-l7r-repo") {
        return Vec::new();
    }
    log::fire(
        "no-branch",
        "blocked",
        &shown,
        "branch-creation",
        &event.input,
        session,
    );
    vec![Answer::Refuse(REFUSAL.to_owned())]
}

#[cfg(test)]
mod tests;
