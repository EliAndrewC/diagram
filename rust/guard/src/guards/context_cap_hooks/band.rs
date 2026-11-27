//! THE WRAP-UP BAND (feature 451 T417, the GM 2026-11-27: "Does it make sense to enforce such an abrupt cutoff?  Like I understand
//! wanting to hand off to a new builder, but if our builders are prevented from even finishing their handoff, then is that really the
//! most efficient thing to do?"): from the cap to [`CEILING_TOKENS`] a builder may run only its stop point's own steps; past the
//! ceiling the cap is as it was. WHY: on 2026-11-26/27 three of about 35 builders reached the cap - T315's (308k) could not dispatch
//! its plan review's second round, T325's (310k) could not run `make plan-delta`, `make claims-triage` or file the task it had found,
//! and in both the coordinating session did those steps; T359's closing half (311k) had two code fixes owed, which a fresh builder
//! rightly took. The cap's 300k (`docs/process-decisions.md`, "The builders' context cap stays at 300k") priced NEW work, never a
//! builder with a few mechanical commands left; the band lets those through and still sends code to a fresh builder.
//!
//! WHAT IS LET THROUGH (each recorded, rule `wrap-up`, so the turns a builder spends here are counted): a Read or Grep; a Bash
//! command every one of whose simple commands (`shared::tree::commands`, so a quoted `make decide` or a heredoc's line is none) is
//! `cd` or `export` (every brief's own `cd <tree> && export ...` prefix), `make` of the stop point's targets only ([`MAKE`]), `git
//! status` or `git diff` (`git -C <path>` read past, `--output` refused: it writes), or `head`, `tail` or `grep` (a read, as the
//! Read and Grep tools are, and the pipe that keeps a long output out of the context); the one plan review - an Agent call of
//! `spec-fidelity` whose prompt opens `MODE 4: PLAN REVIEW`, as `make decide` and `make plan-delta` print it (a later round is
//! another such dispatch: `review_round_hooks` passes a MODE 4 plan review untouched). The handoff's own Write is the cap's
//! exit, judged before the band. Everything else - an Edit or Write of any other file, any other dispatch, any other make target or
//! program, a resume - is refused, the refusal saying what is still allowed. `make plan-delta` is in [`MAKE`] though the task line
//! does not list it: it is the plan review's own command in every code builder's STOP POINT, and T325's was the step refused.

use serde_json::Value;

use crate::shared::make::invoked;
use crate::shared::spelled::{command_at, name_of};
use crate::shared::state::field;
use crate::shared::tree::{command_head, commands, shown};

/// The hard ceiling of the band, in tokens: past it every call but the handoff's is refused, as below the band's start it is not.
/// A GUESS knob (451 T417: "a GUESS knob, say 340k"): 40k over the cap is about ten mechanical turns of a builder near 300k; what
/// would move it is the falsifier of `dev/audits/builders-context-cap.md`.
pub const CEILING_TOKENS: u64 = 340_000;

/// The make targets of a stop point: the decision and its review, the claims triage and its list, filing and withdrawing a task found,
/// the first tier's checks.
pub(super) const MAKE: [&str; 8] = [
    "decide",
    "plan-delta",
    "plan-verdict",
    "claims-triage",
    "claims-owed",
    "task-add",
    "task-withdraw",
    "builder-checks",
];

/// The programs a band command may run but `make` and `git`: the brief's own prefix and the reads.
const PLAIN: [&str; 5] = ["cd", "export", "head", "tail", "grep"];

/// The plan review's agent and its prompt's opening.
const REVIEW: (&str, &str) = ("spec-fidelity", "MODE 4: PLAN REVIEW");

/// What the band says of one call.
#[derive(Debug, PartialEq, Eq)]
pub(super) enum Band {
    /// A stop point's step: let through, what it is recorded.
    Allowed(String),
    /// Anything else: refused, naming what.
    Refused(String),
}

/// The band's verdict on a call of `tool` with `ti`.
pub(super) fn judge(tool: &str, ti: &Value) -> Band {
    match tool {
        "Read" | "Grep" => Band::Allowed(tool.to_owned()),
        "Agent" | "Task" => {
            let kind = field(ti, "subagent_type");
            if kind == REVIEW.0 && field(ti, "prompt").trim_start().starts_with(REVIEW.1) {
                Band::Allowed("the plan review's dispatch".to_owned())
            } else {
                Band::Refused(format!("a dispatch of `{kind}`"))
            }
        }
        "Bash" => bash(field(ti, "command")),
        "Write" => Band::Refused(format!("a Write of {}", field(ti, "file_path"))),
        "Edit" => Band::Refused(format!("an Edit of {}", field(ti, "file_path"))),
        _ => Band::Refused(format!("a {tool} call")),
    }
}

/// A Bash command: each simple command one the band runs, and every make target it invokes a stop point's.
fn bash(cmd: &str) -> Band {
    let cmds = commands(cmd);
    if cmds.is_empty() {
        return Band::Refused("an empty command".to_owned());
    }
    for c in &cmds {
        let head = command_head(c);
        let words: Vec<&str> = head.split_whitespace().collect();
        let at = command_at(&words);
        let program = words.get(at).map_or("", |w| name_of(w));
        let ok = match program {
            // `make`, its targets judged below; none, a command of `VAR=value` words alone
            "make" | "" => true,
            "git" => git_reads(&words[at + 1..]),
            p => PLAIN.contains(&p),
        };
        if !ok {
            return Band::Refused(format!("`{}`", shown(&head)));
        }
    }
    let goals = invoked(cmd);
    if let Some(goal) = goals.iter().find(|g| !MAKE.contains(&g.as_str())) {
        return Band::Refused(format!("make {goal}"));
    }
    Band::Allowed(shown(&command_head(&cmds.join("; "))))
}

/// `git`'s words after it: `-C <path>`, `-c <k=v>` and `--no-pager` read past, then `status` or `diff`, no `--output`.
fn git_reads(rest: &[&str]) -> bool {
    let mut at = 0;
    while let Some(w) = rest.get(at) {
        match *w {
            "-C" | "-c" => at += 2,
            "--no-pager" => at += 1,
            _ => break,
        }
    }
    rest.get(at)
        .is_some_and(|sub| ["status", "diff"].contains(sub))
        && !rest.iter().any(|w| w.starts_with("--output"))
}

#[cfg(test)]
mod tests;
