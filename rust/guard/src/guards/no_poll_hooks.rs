//! `no-poll-hooks` (features 165, 212, 227, 295; ported from `scripts/hooks/no-poll-hooks.sh`, feature 449 T009): A WAIT THE
//! HARNESS CAN TRACK IS NOT POLLED. A loop that sleeps is refused, but the one permitted wait - watching a file - is backgrounded,
//! given a proof of life and a 90-minute ceiling; a disguised `sleep` is refused; a process pattern that matches its own command is
//! bracketed (a make wait scoped to this tree) or refused; a backgrounded periodic report is sent to a cron. `POLL_OK` and `CRON_OK`
//! with a reason stand it aside. The refusals' words are the shell's; the reasons stand in its comments, kept in git history.
//!
//! Plan T009's decisions: (a) `hm_shape.py`'s wait half is `shared::wait`; (b) the cron's minute is local, asked of `date +%M` on
//! that branch alone; (c) a command's own process pattern is compiled by `fancy-regex`.

use std::path::PathBuf;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log::fire;
use crate::shared::session::Session;
use crate::shared::shape::{strip_heredocs, strip_quotes};
use crate::shared::state::field;
use crate::shared::tool::ask;
use crate::shared::wait::{
    add_ceiling, bracket_pattern, cron_for, file_watching_loop, file_watching_wait, periodic,
    poll_reason, proof_of_life, scope_make_waits, self_matching, sleep_in_loop, WAIT_CEILING_S,
};

/// The guard.
pub const GUARD: Guard = Guard {
    name: "no-poll-hooks",
    events: &["PreToolUse"],
    matcher: "Bash",
    decide,
};

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("a guard's own pattern: {e}"))
}

static LOOP_WORD: LazyLock<Regex> =
    LazyLock::new(|| re(r"(^|[;&|[:space:]])(while|until|for)[[:space:]]"));
static SLEEP_RE: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(^|[;&|(]|[[:space:]]|\bdo\b|\bthen\b)[\\]?((command|env|busybox)[[:space:]]+)?(/(bin|usr/bin)/)?sleep[[:space:]]+[0-9.]",
    )
});
static DISGUISED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(^|[;&|(]|[[:space:]])([\\]|(command|env|busybox)[[:space:]]+|/(bin|usr/bin)/)sleep[[:space:]]+[0-9.]",
    )
});
static PGREP_F: LazyLock<Regex> =
    LazyLock::new(|| re(r"\b(pgrep|pkill)\b[^|;&]*[[:space:]]-[a-zA-Z]*f"));

/// `grep -E`'s reading: a pattern matched against each line alone.
fn grep(p: &Regex, text: &str) -> bool {
    text.split('\n').any(|l| p.is_match(l).unwrap_or(false))
}

/// What one decision reads: the event, its command, the sanitized form, the tree's helpers and the local minute's source.
pub(crate) struct Ctx<'a> {
    pub event: &'a Event,
    pub session: &'a Session,
    pub cmd: String,
    pub scan: String,
    pub lib: PathBuf,
    /// The local minute of the hour, for the periodic report's cron (`date +%M`, T009 decision (b)).
    pub minute: fn() -> u64,
}

impl Ctx<'_> {
    fn log(&self, kind: &str, rule: &str) {
        let shown: String = self.cmd.chars().take(200).collect();
        fire(
            "no-poll",
            kind,
            &shown,
            rule,
            &self.event.input,
            self.session,
        );
    }

    fn helper(&self, name: &str) -> String {
        self.lib.join(name).to_string_lossy().into_owned()
    }

    /// The call with its command (and, where asked, its backgrounding) replaced, and what it is told.
    fn rewrite(&self, command: Option<&str>, background: bool, said: &str) -> Vec<Answer> {
        let mut ti = self
            .event
            .input
            .get("tool_input")
            .cloned()
            .unwrap_or(Value::Null);
        if let Some(c) = command {
            ti["command"] = Value::String(c.to_owned());
        }
        if background {
            ti["run_in_background"] = Value::Bool(true);
        }
        vec![Answer::Rewrite(ti), Answer::Notice(said.to_owned())]
    }
}

/// The local minute of the hour (`date +%M`), 0 where it cannot be read.
fn local_minute() -> u64 {
    ask(std::path::Path::new("/"), "date", &["+%M"], "")
        .out
        .trim()
        .parse()
        .unwrap_or(0)
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let tree = std::env::var("L7R_GUARD_TREE").map_or_else(
        |_| std::env::current_dir().unwrap_or_default(),
        PathBuf::from,
    );
    let cmd = event
        .input
        .get("tool_input")
        .map_or("", |t| field(t, "command"))
        .to_owned();
    if cmd.is_empty() {
        return Vec::new();
    }
    // the sanitized command is never empty for a command that is not: the stripping inserts as it removes
    let scan = strip_quotes(&strip_heredocs(&cmd));
    judge(&Ctx {
        event,
        session,
        cmd,
        scan,
        lib: tree.join("scripts/hooks/lib"),
        minute: local_minute,
    })
}

pub(crate) fn judge(cx: &Ctx) -> Vec<Answer> {
    let ti = cx
        .event
        .input
        .get("tool_input")
        .cloned()
        .unwrap_or(Value::Null);
    if crate::shared::wait::background(&ti) {
        match escape_or_refuse(&cx.cmd, "CRON_OK") {
            Escape::Refused(text) => {
                cx.log("blocked", "CRON_OK-no-reason");
                return vec![Answer::Refuse(text)];
            }
            Escape::Escaped(why) => fire(
                "no-poll",
                "escaped",
                &why,
                "cron-ok",
                &cx.event.input,
                cx.session,
            ),
            Escape::None => {
                if let Some(period) = periodic(&ti, field(&cx.event.input, "cwd")) {
                    cx.log("blocked", "periodic-report");
                    let why = Some(poll_reason(&cx.cmd))
                        .filter(|w| !w.is_empty())
                        .unwrap_or_else(|| "the periodic report".to_owned());
                    return vec![Answer::Refuse(periodic_refusal(
                        &cron_for(period, (cx.minute)()),
                        &format!("{why}: check the state once and report it"),
                    ))];
                }
            }
        }
    }
    match escape_or_refuse(&cx.cmd, "POLL_OK") {
        Escape::Refused(text) => {
            cx.log("blocked", "POLL_OK-no-reason");
            return vec![Answer::Refuse(text)];
        }
        Escape::Escaped(why) => {
            fire(
                "no-poll",
                "escaped",
                &why,
                "poll-ok",
                &cx.event.input,
                cx.session,
            );
            if let Some(done) = bracket_self_match(cx, "escaped-self-match", ESCAPED_BRACKET) {
                return done;
            }
            return add_ceiling(&cx.cmd, WAIT_CEILING_S).map_or_else(Vec::new, |ceiled| {
                cx.log("rewrote", "escaped-ceiling");
                cx.rewrite(Some(&ceiled), false, ESCAPED_CEILING)
            });
        }
        Escape::None => {}
    }
    if grep(&LOOP_WORD, &cx.scan) && grep(&SLEEP_RE, &cx.scan) && sleep_in_loop(&cx.scan) {
        if file_watching_loop(&cx.cmd) {
            return file_wait(cx, &ti);
        }
        return block(
            cx,
            "this is a busy-wait loop (a loop containing `sleep`).",
            BUSY_WAIT,
            "busy-wait-loop",
        );
    }
    if grep(&DISGUISED, &cx.scan) {
        return block(
            cx,
            "`sleep` was invoked in a form that evades the harness's foreground-sleep block.",
            DISGUISED_WHY,
            "disguised-sleep",
        );
    }
    bracket_self_match(cx, "self-match", BRACKETED).unwrap_or_default()
}

/// The permitted wait - a file watched - made safe: backgrounded, given a proof of life and a ceiling.
fn file_wait(cx: &Ctx, ti: &Value) -> Vec<Answer> {
    let proof = proof_of_life(&cx.cmd, &cx.helper("writer-alive.sh"));
    if let Some(refused) = refuse_self_match(cx, proof.as_deref().unwrap_or(&cx.cmd)) {
        return refused;
    }
    let ceil = add_ceiling(proof.as_deref().unwrap_or(&cx.cmd), WAIT_CEILING_S);
    let bg = file_watching_wait(ti);
    if proof.is_none() && ceil.is_none() && bg {
        cx.log("permitted", "detached-file-wait");
        return Vec::new();
    }
    let rule = if !bg {
        "backgrounded-file-wait"
    } else if proof.is_some() {
        "proof-of-life"
    } else {
        "wait-ceiling"
    };
    cx.log("rewrote", rule);
    let mut said = Vec::new();
    if !bg {
        said.push(BACKGROUNDED);
    }
    if proof.is_some() {
        said.push(PROOF);
    }
    if ceil.is_some() {
        said.push(CEILING);
    }
    said.push("A wait on a process or a network call is still refused.");
    cx.rewrite(ceil.as_deref().or(proof.as_deref()), true, &said.join(" "))
}

/// A refusal naming what to do instead.
fn block(cx: &Ctx, reason: &str, alternative: &str, rule: &str) -> Vec<Answer> {
    cx.log("blocked", rule);
    vec![Answer::Refuse(format!(
        "BLOCKED (no-poll): {reason}\n{alternative}\n\nDo this instead: run the work with run_in_background and act on the completion \
notification; the harness\nre-invokes you. For EXTERNAL state the harness cannot see (a port, a remote queue), put POLL_OK and what \
you\nare waiting for in the command."
    ))]
}

/// A process pattern that matches `cmd`'s own text refused: the waiting shell finds itself and the wait never ends.
fn refuse_self_match(cx: &Ctx, cmd: &str) -> Option<Vec<Answer>> {
    let hit = self_matching(cmd).into_iter().next()?;
    cx.log("blocked", "self-match-launch");
    Some(vec![Answer::Refuse(format!(
        "BLOCKED (no-poll): the process pattern {hit} matches this command's own text - it launches, or names, what it\nwaits for - \
so the waiting shell finds itself and the wait never ends (2026-09-30: four hours past a finished roll).\nWait on the launched \
process by its PID (`cmd > log 2>&1 & pid=$!; until ! kill -0 $pid; do sleep 10; done`), or on\nits log with run_in_background, \
or on a make run with `scripts/hooks/lib/own-make.sh <target>`."
    ))])
}

/// A `pgrep -f`/`pkill -f` pattern bracketed so it cannot find its own shell, a make wait scoped to this tree, a ceiling added -
/// the rewrite, or a refusal, or None where the command has no such pattern to fix.
fn bracket_self_match(cx: &Ctx, rule: &str, context: &str) -> Option<Vec<Answer>> {
    if !grep(&PGREP_F, &cx.scan) {
        return None;
    }
    let scoped = scope_make_waits(&cx.cmd, &cx.helper("own-make.sh"));
    let fixed = bracket_pattern(scoped.as_deref().unwrap_or(&cx.cmd)).or(scoped);
    if let Some(refused) = refuse_self_match(cx, fixed.as_deref().unwrap_or(&cx.cmd)) {
        return Some(refused);
    }
    let mut fixed = fixed?;
    let mut context = context.to_owned();
    if let Some(ceiled) = add_ceiling(&fixed, WAIT_CEILING_S) {
        fixed = ceiled;
        context += " A ceiling was added to the loop: past 90 minutes it prints WAIT TIMED OUT and exits 4, so a wait that can never end still wakes you.";
    }
    let rule = if fixed.contains("own-make.sh") {
        SCOPED.clone_into(&mut context);
        format!("{rule}-scoped")
    } else {
        rule.to_owned()
    };
    cx.log("rewrote", &rule);
    Some(cx.rewrite(Some(&fixed), false, &context))
}

fn periodic_refusal(cron: &str, prompt: &str) -> String {
    format!(
        "BLOCKED (no-poll): a periodic report kept as a backgrounded watcher loses its schedule when its exit lands while\nthe session \
cannot run (2026-09-30: twice across a usage-limit window, about two hours of reports each). A cron\nkeeps the schedule by \
itself:\n\n  CronCreate(cron=\"{cron}\", recurring=true, prompt=\"{prompt}\")\n\nPut in the prompt what one report checks. (It fires \
while the session is idle and lasts 7 days.) A wait for an\nevent - a file, a finished queue - stays a backgrounded watcher. Escape: \
CRON_OK=\"<reason>\".\n"
    )
}

const BUSY_WAIT: &str = "Waiting in a loop burns wall-clock at full model-turn cost and, for anything the harness tracks, it
is pure waste: a backgrounded Bash command notifies you the moment it exits.";
const DISGUISED_WHY: &str = "The harness blocks foreground `sleep` on purpose; `command sleep`, `/bin/sleep` and `env sleep`
are the same thing wearing a hat. Whatever you were about to wait for, there is a better signal for
it - a completion notification for harness-tracked work, or POLL_OK for genuinely external state.";
const BRACKETED: &str = "The process-match pattern was bracketed for you: a literal pattern is an argument of the command line being \
searched, so it always finds the searching shell itself and the wait never ends. Corrected rather than refused - the refusal used to \
cost a round trip to say the same thing.";
const ESCAPED_BRACKET: &str = "POLL_OK permitted this wait, and its process-match pattern was bracketed for you: a literal pattern is \
an argument of the command line being searched, so it always finds the searching shell itself and the loop never ends (2026-09-08: an \
escaped waiter on a detached page-check looped for hours on a gate that finished in 7 s). The escape decides whether you may wait; it \
does not make the pattern correct.";
const ESCAPED_CEILING: &str = "POLL_OK permitted this wait, and a ceiling was added to its loop: past 90 minutes it prints WAIT TIMED \
OUT and exits 4, so a wait that can never end still wakes you (2026-09-30: four hours lost to one that never ended).";
const SCOPED: &str = "A wait on a make run was scoped to this working tree (own-make.sh <target>): pgrep searches the whole host, and \
other sessions' runs of the same target held a waiter open for six hours after its own run had ended. A harness-tracked run \
(run_in_background) needs no waiter at all.";
const BACKGROUNDED: &str = "This file-watching wait was BACKGROUNDED for you (run_in_background): in the foreground it would have held \
the whole turn at model-turn cost. Its output - including whatever follows the loop - arrives as a completion notification, so spend \
the turn on the next thing.";
const PROOF: &str = "A PROOF-OF-LIFE check was added to the loop: `writer-alive.sh <the file you are watching>`, which asks the kernel \
whether anything still holds that file open and when it was last written. Without it the wait outlives its producer - a detached run \
that is killed (this container OOM-kills them) stops writing, the pattern never appears, and the loop runs until somebody notices. \
When the loop ends, read what the log DOES have: if the helper printed a line, the run is gone and the log is truncated, not finished.";
const CEILING: &str = "A CEILING was added to the loop: past 90 minutes it prints WAIT TIMED OUT and exits 4, so a wait whose line \
never comes still ends and wakes you (2026-09-30: four hours lost to a wait that could not end).";

#[cfg(test)]
mod tests;
