//! `context-cap-hooks` (feature 451 T12, FR-006, plan D8 and D9; research R2, R3): A BUILDER PAST THE CONTEXT CAP WRITES ITS HANDOFF
//! AND STOPS. WHY: a builder's model calls slow as its context grows - 10 s per 1,000 output tokens under 200k tokens, 23 s over 700k
//! (measured 2026-11-19, 3,280 builder calls by context size, the spec's User Story 2) - and T152 and T221 each passed 1.3 million. The
//! approved route is "a fresh builder per stage, with a handoff file": past [`CONTEXT_CAP_TOKENS`] every tool call of a builder is
//! refused but its handoff's Write, the refusal naming the file and the next step.
//!
//! WHO IS A BUILDER (D8): a payload with `agent_id` - present only inside a subagent, absent on the main thread (the schema's own
//! words) - whose `agent_type` names no `.claude/agents/<agent_type>.md` in the clone. Measured 2026-11-20 (the payloads pinned in
//! `context_cap_hooks/payloads.json`, captured from Claude Code 2.1.325 by a `PreToolUse` hook writing its stdin): a builder's call carries
//! `agent_type` `general-purpose`, a defined agent's its own name, the main session's neither key. The main session and a defined agent
//! return before any file is read, so a review agent finishing is never held.
//!
//! ITS CONTEXT (D9): its own transcript, `<transcript_path without .jsonl>/subagents/agent-<agent_id>.jsonl` (the payload's
//! `transcript_path` is the SESSION's, R2 - the same capture), read backwards to the last `assistant` row with a `message.usage`:
//! `input_tokens + cache_read_input_tokens + cache_creation_input_tokens`. Only an `assistant` row: a `user` row holding an Agent
//! call's result carries that child's `usage` (the same capture: 2 such rows), and a row of zero (a synthetic message) is no model call.
//! Any failure to read - no file, no such row within [`TAIL_BYTES`] - passes: a guard that cannot see the context does not guess it.
//!
//! THE ONE EXIT: a Write, Edit or Read of `<git common dir>/l7r-handoffs/<task>-<agent_id>.md` (`<agent_id>.md` where the call's line
//! carries no task) - any file there whose name ends `<agent_id>.md`, so the refusal and the Write agree even where the task the event
//! log's chain reads moves between them, and no two builders share a file. The Read is let through so a handoff once written can be
//! overwritten (the Write tool refuses a file it has not read). A Write there passed the live guard chain from a background builder
//! (observed 2026-11-20, method: this task's builder writing `.git/l7r-handoffs/probe-<its id>.md` in its clone, then removing it).
//!
//! The escape (FR-012): `CONTEXT_OK="<reason>"` in a Bash command, recorded. A call outside any clone passes.

use std::fs::File;
use std::io::{Read as _, Seek, SeekFrom};
use std::path::{Path, PathBuf};

use serde_json::Value;

use crate::guards::event_log_hooks::{common_git_dir, filed_at};
use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log::fire;
use crate::shared::session::Session;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "context-cap-hooks",
    events: &["PreToolUse"],
    matcher: "*",
    decide,
};

/// The context, in tokens, past which a builder's next tool call is refused: GUESS, 300,000 (spec FR-006) - between the window's two
/// figures, a 400k cap saving about 44 minutes and a 200k one about 95 (an estimate from a correlation, User Story 2); retuned from
/// FR-004's per-agent token data (T22).
pub const CONTEXT_CAP_TOKENS: u64 = 300_000;

/// How far back the transcript is read for its last model call: 16 MiB. A transcript row is one tool call's result at most, and the
/// largest builder transcript of the window, 50 MB, was scanned whole in 0.07 s (research R2); a last call further back than this is
/// no call the guard can see, and passes.
const TAIL_BYTES: u64 = 16 << 20;

/// The bytes read a step, backwards.
const CHUNK: u64 = 64 << 10;

const TOKEN: &str = "CONTEXT_OK";

/// The handoffs' directory under the clone's common git dir.
const HANDOFFS: &str = "l7r-handoffs";

/// What the guard says of a builder's call past the cap.
#[derive(Debug, PartialEq, Eq)]
enum Said {
    /// The handoff's own Write, Edit or Read: passed, recorded.
    Handoff(String),
    /// Escaped by `CONTEXT_OK` and its reason.
    Escaped(String),
    /// `CONTEXT_OK` with no reason: the escape's own refusal.
    NoReason(String),
    /// Refused, naming the handoff file.
    Refused {
        agent: String,
        tokens: u64,
        handoff: PathBuf,
    },
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    answer(event, session, &here, &|k| std::env::var(k).ok())
}

/// The answers to one call, its environment read through `env`, and each firing recorded.
fn answer(
    event: &Event,
    session: &Session,
    here: &Path,
    env: &dyn Fn(&str) -> Option<String>,
) -> Vec<Answer> {
    let log = |kind: &str, detail: &str, rule: &str| {
        fire("context-cap", kind, detail, rule, &event.input, session);
    };
    match judge(&event.input, here, env, CONTEXT_CAP_TOKENS) {
        None => Vec::new(),
        Some(Said::Handoff(path)) => {
            log("passed", &path, "handoff");
            Vec::new()
        }
        Some(Said::Escaped(why)) => {
            log("escaped", &why, "context-ok");
            Vec::new()
        }
        Some(Said::NoReason(text)) => {
            log(
                "blocked",
                "CONTEXT_OK with no reason",
                "CONTEXT_OK-no-reason",
            );
            vec![Answer::Refuse(text)]
        }
        Some(Said::Refused {
            agent,
            tokens,
            handoff,
        }) => {
            log("blocked", &format!("{agent}: {tokens} tokens"), "past-cap");
            vec![Answer::Refuse(refusal(tokens, &handoff))]
        }
    }
}

/// The verdict on one hook input against the cap `cap`: None to pass it silently.
fn judge(
    input: &Value,
    here: &Path,
    env: &dyn Fn(&str) -> Option<String>,
    cap: u64,
) -> Option<Said> {
    // THE MAIN SESSION, AND AN ID NO PATH CAN TAKE: every call of the main thread ends here, nothing read
    let agent = field(input, "agent_id");
    if !plain(agent) {
        return None;
    }
    let cwd = match field(input, "cwd") {
        "" => here.to_path_buf(),
        c => PathBuf::from(c),
    };
    let tree = tree_of(&cwd)?;
    // A DEFINED AGENT (D8): its type names a file of the clone's `.claude/agents/`, a stat and no read
    let kind = field(input, "agent_type");
    if plain(kind)
        && tree
            .join(".claude/agents")
            .join(format!("{kind}.md"))
            .is_file()
    {
        return None;
    }
    let tokens = context(&own_transcript(field(input, "transcript_path"), agent)?)?;
    if tokens <= cap {
        return None;
    }
    let (root, _, _, task) = filed_at(input, here, env)?;
    let dir = common_git_dir(&root).join(HANDOFFS);
    let handoff =
        dir.join(task.map_or_else(|| format!("{agent}.md"), |t| format!("{t}-{agent}.md")));
    let tool = field(input, "tool_name");
    let ti = input.get("tool_input").unwrap_or(&Value::Null);
    if ["Write", "Edit", "Read"].contains(&tool) && is_handoff(field(ti, "file_path"), &dir, agent)
    {
        return Some(Said::Handoff(field(ti, "file_path").to_owned()));
    }
    if tool == "Bash" {
        match escape_or_refuse(field(ti, "command"), TOKEN) {
            Escape::Escaped(why) => return Some(Said::Escaped(why)),
            Escape::Refused(text) => return Some(Said::NoReason(text)),
            Escape::None => {}
        }
    }
    Some(Said::Refused {
        agent: agent.to_owned(),
        tokens,
        handoff,
    })
}

/// A name safe to join into a path: letters, digits, `-` and `_`, and not empty.
fn plain(name: &str) -> bool {
    !name.is_empty()
        && name
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || c == '-' || c == '_')
}

/// The working tree holding `cwd`, walked up to its `.git` (`event_log_hooks::clone_root`'s walk).
fn tree_of(cwd: &Path) -> Option<PathBuf> {
    let p = std::fs::canonicalize(cwd).unwrap_or_else(|_| cwd.to_path_buf());
    p.ancestors()
        .find(|d| d.join(".git").exists())
        .map(Path::to_path_buf)
}

/// The subagent's own transcript, derived from the session's (D9; R2).
fn own_transcript(session_transcript: &str, agent: &str) -> Option<PathBuf> {
    let stem = session_transcript.strip_suffix(".jsonl")?;
    Some(
        Path::new(stem)
            .join("subagents")
            .join(format!("agent-{agent}.jsonl")),
    )
}

/// The context of a transcript's last model call: its last `assistant` row's `usage`, read backwards in [`CHUNK`]s at most
/// [`TAIL_BYTES`] deep; None where none is found.
fn context(path: &Path) -> Option<u64> {
    let mut f = File::open(path).ok()?;
    let mut pos = f.metadata().ok()?.len();
    // the bytes from `pos` to the end of what is not yet scanned
    let mut buf: Vec<u8> = Vec::new();
    let mut read = 0;
    loop {
        // each line after a newline in `buf` is whole: scanned from the last back
        while let Some(i) = buf.iter().rposition(|&b| b == b'\n') {
            let line = buf.split_off(i + 1);
            buf.pop();
            if let Some(n) = usage_of(&line) {
                return Some(n);
            }
        }
        if pos == 0 {
            return usage_of(&buf);
        }
        if read >= TAIL_BYTES {
            return None;
        }
        let step = CHUNK.min(pos);
        pos -= step;
        f.seek(SeekFrom::Start(pos)).ok()?;
        let mut chunk = vec![0; usize::try_from(step).ok()?];
        f.read_exact(&mut chunk).ok()?;
        chunk.extend_from_slice(&buf);
        buf = chunk;
        read += step;
    }
}

/// The context one transcript row reports: an `assistant` row's `message.usage` summed, None for any other row or a sum of zero.
fn usage_of(line: &[u8]) -> Option<u64> {
    const NEEDLE: &[u8] = b"\"usage\"";
    if !line.windows(NEEDLE.len()).any(|w| w == NEEDLE) {
        return None;
    }
    let row: Value = serde_json::from_slice(line).ok()?;
    if row.get("type").and_then(Value::as_str) != Some("assistant") {
        return None;
    }
    let usage = row.get("message")?.get("usage")?;
    let n = |k: &str| usage.get(k).and_then(Value::as_u64).unwrap_or(0);
    let sum = n("input_tokens") + n("cache_read_input_tokens") + n("cache_creation_input_tokens");
    (sum > 0).then_some(sum)
}

/// Whether `file` is this agent's handoff: in `dir`, its name ending `<agent>.md`.
fn is_handoff(file: &str, dir: &Path, agent: &str) -> bool {
    let p = Path::new(file);
    let real = |d: &Path| std::fs::canonicalize(d).unwrap_or_else(|_| d.to_path_buf());
    p.file_name()
        .is_some_and(|n| n.to_string_lossy().ends_with(&format!("{agent}.md")))
        && p.parent().is_some_and(|d| real(d) == real(dir))
}

/// The refusal: the context against the cap, the handoff file, the next step, the escape.
fn refusal(tokens: u64, handoff: &Path) -> String {
    let path = handoff.display();
    format!(
        "\n\u{1b}[1mBLOCKED: this builder's context is {tokens} tokens, past the cap of {CONTEXT_CAP_TOKENS} (feature 451 FR-006).\u{1b}[0m\n\n\
A builder's model calls slow as its context grows (10 s per 1,000 output tokens under 200k, 23 s over 700k), so a long task\n\
goes on in a fresh builder. The next step:\n\n\
  1. Write the handoff file - what is done, what is left, the files touched and the next command - with the Write tool,\n\
     the one call this guard lets through:\n\n       {path}\n\n\
  2. Stop, and reply with that path. The main session dispatches a fresh builder with the file as its brief.\n\n\
Escape: {TOKEN}=\"<reason>\" in a Bash command, recorded in the guard log.\n"
    )
}

#[cfg(test)]
mod tests;
