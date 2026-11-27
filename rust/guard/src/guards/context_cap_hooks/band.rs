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
//! `cd`, `pushd` or `export` (every brief's own `cd <tree> && export ...` prefix), `make` of the stop point's targets only ([`MAKE`]), `git
//! status` or `git diff` (`git -C <path>` read past, `--output` refused: it writes), or `head`, `tail` or `grep` (a read, as the
//! Read and Grep tools are, and the pipe that keeps a long output out of the context), its every redirect landing under `/tmp` (the
//! session's scratchpad is `/tmp/claude-<uid>/...`) or in the handoff the cap's exit allows (451 T427: `tail -n 0 x > rust/a.rs`
//! wrote a source file the band refuses as a Write; where it lands is the shared walk's, `shared::tree::walk`, a redirect it
//! cannot place refused; a `>& FILE` and a `cd`'s redirect are placed as any other, 451 T460); the one plan review - an Agent call of
//! `spec-fidelity` whose prompt opens `MODE 4: PLAN REVIEW`, as `make decide` and `make plan-delta` print it (a later round is
//! another such dispatch: `review_round_hooks` passes a MODE 4 plan review untouched). The handoff's own Write is the cap's
//! exit, judged before the band. Everything else - an Edit or Write of any other file, any other dispatch, any other make target or
//! program, a resume - is refused, the refusal saying what is still allowed. `make plan-delta` is in [`MAKE`] though the task line
//! does not list it: it is the plan review's own command in every code builder's STOP POINT, and T325's was the step refused.

use serde_json::Value;

use crate::shared::make::invoked;
use crate::shared::spelled::{command_at, name_of};
use crate::shared::state::field;
use crate::shared::tree::{command_head, commands, shown, walk};

/// The hard ceiling of the band, in tokens: past it every call but the handoff's is refused, as below the band's start it is not.
/// A GUESS knob (451 T417: "a GUESS knob, say 340k"): 40k over the cap is about ten mechanical turns of a builder near 300k; what
/// would move it is the falsifier of `dev/audits/builders-context-cap.md`.
pub const CEILING_TOKENS: u64 = 340_000;

/// The make targets of a stop point: the decision and its review, the claims triage and its list, filing and withdrawing a task found,
/// the first tier's checks, and (461 T43) the hand-in, `make builder-done`, which a fix or a closing half runs last.
pub(super) const MAKE: [&str; 9] = [
    "decide",
    "plan-delta",
    "plan-verdict",
    "claims-triage",
    "claims-owed",
    "task-add",
    "task-withdraw",
    "builder-checks",
    "builder-done",
];

/// The programs a band command may run but `make` and `git`: the brief's own prefix (`pushd` as `cd`) and the reads.
const PLAIN: [&str; 6] = ["cd", "pushd", "export", "head", "tail", "grep"];

/// The plan review's agent and its prompt's opening.
const REVIEW: (&str, &str) = ("spec-fidelity", "MODE 4: PLAN REVIEW");

/// Where a call stands, for its redirects (451 T427): its cwd, the home `~` names, and whether a path is the handoff the cap's exit
/// allows.
pub(super) struct At<'a> {
    pub cwd: Option<&'a str>,
    pub home: &'a str,
    pub handoff: &'a dyn Fn(&str) -> bool,
}

/// Where a redirect may land in the band but the handoff: `/tmp`, the scratchpad's parent.
const SCRATCH: &str = "/tmp/";

/// What the band says of one call.
#[derive(Debug, PartialEq, Eq)]
pub(super) enum Band {
    /// A stop point's step: let through, what it is recorded.
    Allowed(String),
    /// Anything else: refused, naming what.
    Refused(String),
}

/// The band's verdict on a call of `tool` with `ti`.
pub(super) fn judge(tool: &str, ti: &Value, at: &At) -> Band {
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
        "Bash" => bash(field(ti, "command"), at),
        "Write" => Band::Refused(format!("a Write of {}", field(ti, "file_path"))),
        "Edit" => Band::Refused(format!("an Edit of {}", field(ti, "file_path"))),
        _ => Band::Refused(format!("a {tool} call")),
    }
}

/// A Bash command: each simple command one the band runs, every make target it invokes a stop point's, and every redirect landing
/// under `/tmp` or in the handoff.
fn bash(cmd: &str, at: &At) -> Band {
    let cmds = commands(cmd);
    if cmds.is_empty() {
        return Band::Refused("an empty command".to_owned());
    }
    for c in &cmds {
        let head = command_head(c);
        let words: Vec<&str> = head.split_whitespace().collect();
        let at = command_at(&words);
        let program = words.get(at).map_or("", |w| name_of(w));
        // a `>& FILE` and a `cd`'s redirect are judged by place below, the walk reading both (451 T433, T436; T460)
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
    if let Some(what) = redirect(cmd, at) {
        return Band::Refused(what);
    }
    Band::Allowed(shown(&command_head(&cmds.join("; "))))
}

/// The first redirect of `cmd` landing neither under `/tmp` nor in the handoff, named for the refusal (451 T427); `2>&1` and
/// `> /dev/null` are no write the walk reports.
fn redirect(cmd: &str, at: &At) -> Option<String> {
    let found = walk(cmd, at.cwd, "", at.home).targets;
    let t = found.into_iter().filter(|t| t.redirect).find(|t| {
        !t.path
            .as_deref()
            .is_some_and(|p| p.starts_with(SCRATCH) || (at.handoff)(p))
    })?;
    let place = t
        .path
        .unwrap_or_else(|| "a place the guard cannot resolve".to_owned());
    Some(format!(
        "a redirect writing {place} (in the band a redirect lands only under /tmp or in the handoff)"
    ))
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
