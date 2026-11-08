//! `agent-prefix-hooks` (feature 383 amendment 6, FR-034; ported from the shell of the same name and `lib/hm_agent_prefix.py`, feature 449 T042): A LARGE
//! BLOCK AN AGENT PROMPT REPEATS FROM AN EARLIER DISPATCH OF ITS TYPE IS REFUSED, WHEREVER IT SITS. Only a subagent's system prompt - its agent file - is
//! reused across launches (research R16); the launch prompt has no cache breakpoint, so a repeated block is written fresh every time. A prompt identical
//! to an earlier one as a whole passes (R14). And a 4th launch of one type within seconds goes through the `check-wave` workflow (amendment 7, FR-045).
//! Escapes, in the prompt with a reason: `AGENT_PREFIX_OK` (a repeated block), `WAVE_OK` (a hand-launched wave).

use std::collections::{BTreeMap, HashMap};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;
use std::time::{SystemTime, UNIX_EPOCH};

use fancy_regex::Regex;
use serde_json::{json, Value};

use crate::guards::workflow_hooks::WAVE_JOBS;
use crate::protocol::{Answer, Event, Guard};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::sha256;
use crate::shared::state::field;
use crate::shared::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "agent-prefix-hooks",
    events: &["PreToolUse"],
    matcher: "Agent",
    decide,
};

/// CONVENTION: the block that matters, ~500 tokens, where a cached prefix starts to count against the ~2.5k a dispatch writes regardless (research R13). A number to move.
const SHARED: usize = 2000;
/// CONVENTION: how much of a prompt is compared and kept.
const CAP: usize = 65536;
/// CONVENTION: the session's last dispatches that passed, kept.
const KEEP: usize = 30;
/// CONVENTION: this many launches of one type inside `WAVE_S` seconds is the most that goes by hand (feature 383 amendment 7, plan D46). Design numbers to move.
const WAVE_N: usize = 3;
const WAVE_S: f64 = 10.0;

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static WAVE_ESCAPE: LazyLock<Regex> = LazyLock::new(|| re(r#"WAVE_OK\s*[=:]\s*["']?\S+\s+\S+"#));
static ESCAPE: LazyLock<Regex> = LazyLock::new(|| re(r#"AGENT_PREFIX_OK\s*[=:]\s*["']?\S+\s+\S+"#));

fn matches(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

/// `str.splitlines(keepends=True)`.
pub(crate) fn lines_kept(text: &str) -> Vec<&str> {
    let (mut out, mut start) = (Vec::new(), 0);
    let mut chars = text.char_indices().peekable();
    while let Some((at, c)) = chars.next() {
        let mut end = at + c.len_utf8();
        if c == '\r' && chars.peek().is_some_and(|(_, n)| *n == '\n') {
            chars.next();
            end += 1;
        }
        if matches!(
            c,
            '\n' | '\r'
                | '\x0b'
                | '\x0c'
                | '\x1c'
                | '\x1d'
                | '\x1e'
                | '\u{85}'
                | '\u{2028}'
                | '\u{2029}'
        ) {
            out.push(&text[start..end]);
            start = end;
        }
    }
    if start < text.len() {
        out.push(&text[start..]);
    }
    out
}

fn width(line: &str) -> usize {
    line.chars().count()
}

/// (characters, start offset in `new`) of each maximal run of consecutive identical lines both texts hold that reaches `least` characters, in the order they start.
fn shared_runs(new: &str, old: &str, least: usize) -> Vec<(usize, usize)> {
    let (nl, ol) = (lines_kept(new), lines_kept(old));
    let mut wherever: HashMap<&str, Vec<usize>> = HashMap::new();
    for (j, line) in ol.iter().enumerate() {
        wherever.entry(line).or_default().push(j);
    }
    let mut offsets = Vec::with_capacity(nl.len());
    let mut pos = 0;
    for line in &nl {
        offsets.push(pos);
        pos += width(line);
    }
    let mut best: BTreeMap<usize, usize> = BTreeMap::new();
    let mut run: HashMap<usize, (usize, usize)> = HashMap::new();
    for (i, line) in nl.iter().enumerate() {
        let mut next = HashMap::new();
        for j in wherever.get(line).into_iter().flatten() {
            let (size, start) = j
                .checked_sub(1)
                .and_then(|p| run.get(&p).copied())
                .unwrap_or((0, i));
            let grown = size + width(line);
            next.insert(*j, (grown, start));
            let slot = best.entry(start).or_insert(0);
            *slot = (*slot).max(grown);
        }
        run = next;
    }
    best.into_iter()
        .filter(|(_, size)| *size >= least)
        .map(|(start, size)| (size, offsets[start]))
        .collect()
}

/// The first block of `SHARED`+ characters `new` repeats from `old`, wherever it sits; none when the two prompts are identical as a whole.
fn finding(new: &str, old: &str) -> Option<(usize, usize)> {
    let new: String = new.chars().take(CAP).collect();
    let old: String = old.chars().take(CAP).collect();
    if new == old {
        return None;
    }
    shared_runs(&new, &old, SHARED).first().copied()
}

fn store(git_dir: &Path, session: &str) -> PathBuf {
    let name = sha256::hex(session.as_bytes());
    git_dir
        .join("l7r-agent-prompts")
        .join(format!("{}.jsonl", &name[..16]))
}

/// Every row kept for the session; none when the file is unreadable or holds a line that is not JSON.
fn all_rows(git_dir: &Path, session: &str) -> Vec<Value> {
    let Ok(text) = std::fs::read_to_string(store(git_dir, session)) else {
        return Vec::new();
    };
    text.lines()
        .filter(|l| !l.trim().is_empty())
        .map(serde_json::from_str)
        .collect::<Result<_, _>>()
        .unwrap_or_default()
}

/// Would a launch of `kind` at `now` be past the hand-launched wave?
fn waved(rows: &[Value], kind: &str, now: f64) -> bool {
    let near = |r: &&Value| {
        let age = now - r.get("t").and_then(Value::as_f64).unwrap_or(0.0);
        field(r, "key").split('|').next() == Some(kind) && (0.0..WAVE_S).contains(&age)
    };
    rows.iter().filter(near).count() >= WAVE_N
}

fn remember(git_dir: &Path, session: &str, key: &str, prompt: &str, now: f64) {
    let path = store(git_dir, session);
    if let Some(dir) = path.parent() {
        let _ = std::fs::create_dir_all(dir);
    }
    let text = std::fs::read_to_string(&path).unwrap_or_default();
    let mut rows: Vec<String> = text
        .lines()
        .filter(|l| !l.trim().is_empty())
        .map(str::to_owned)
        .collect();
    let kept: String = prompt.chars().take(CAP).collect();
    rows.push(json!({"key": key, "prompt": kept, "t": now}).to_string());
    let from = rows.len().saturating_sub(KEEP);
    let _ = std::fs::write(&path, rows[from..].join("\n") + "\n");
}

/// What the decider said.
#[derive(Debug, PartialEq, Eq)]
pub(crate) enum Said {
    Pass,
    Escaped,
    Wave(String),
    Repeat(String),
}

pub(crate) fn verdict(event: &Event, git_dir: &Path, now: f64, wave_unit: bool) -> Said {
    let null = Value::Null;
    let ti = event.input.get("tool_input").unwrap_or(&null);
    if event.tool() != "Agent" {
        return Said::Pass;
    }
    let (prompt, session) = (field(ti, "prompt"), field(&event.input, "session_id"));
    let kind = Some(field(ti, "subagent_type"))
        .filter(|k| !k.is_empty())
        .unwrap_or("general-purpose");
    let key = format!("{kind}|{}", field(ti, "model"));
    let rows = all_rows(git_dir, session);
    if !wave_unit && !matches(&WAVE_ESCAPE, prompt) && waved(&rows, kind, now) {
        return Said::Wave(kind.to_owned());
    }
    let escaped = matches(&ESCAPE, prompt);
    let same_key = rows.iter().rev().filter(|r| field(r, "key") == key);
    for old in same_key {
        let Some((size, start)) = finding(prompt, field(old, "prompt")) else {
            continue;
        };
        if escaped {
            remember(git_dir, session, &key, prompt, now);
            return Said::Escaped;
        }
        let tail: String = prompt.chars().skip(start).collect();
        let head: String = tail.chars().take(70).collect();
        let first = if tail.trim().is_empty() {
            ""
        } else {
            lines_kept(&head)
                .first()
                .map_or("", |l| l.trim_end_matches(['\n', '\r']))
        };
        return Said::Repeat(format!("{size} characters of this prompt repeat an earlier `{kind}` dispatch's, from character {start}: `{first}`"));
    }
    remember(git_dir, session, &key, prompt, now);
    Said::Pass
}

fn bold(line: &str) -> String {
    format!("\n\u{1b}[1mBLOCKED: {line}\u{1b}[0m\n")
}

const TRAILER: &str = "(rust/guard/src/guards/agent_prefix_hooks.rs; feature 383 amendment 6; `make subagent-cache` measures it)";

fn wave_text(kind: &str) -> String {
    let way = if WAVE_JOBS.contains(&kind) {
        format!("  Workflow({{name: \"check-wave\", args: {{agentType: \"{kind}\", units: [{{label: \"<unit>\", prompt: \"<its prompt>\"}}, ...]}}}})\nTwo or three of a type stay plain Agent calls. If this batch must stay hand-launched: WAVE_OK: <reason> in the prompt.\n")
    } else {
        format!("`{kind}` is not one of check-wave's authorized jobs, so that route is closed to it: send at most three now and the\nrest in the next message, or, if this batch must go together: WAVE_OK: <reason> in the prompt.\n")
    };
    format!(
        "{}Every agent launched by hand wakes the main session when it finishes, and each wake re-reads its whole context\n(5,544 wakes a month, a median 405k tokens each - feature 383 research R20). A workflow staggers the launches by itself\nand wakes the session once, and its guard holds each unit to every check this one would have:\n{way}{TRAILER}",
        bold(&format!("a 4th `{kind}` launch within seconds - a wave goes through the check-wave workflow."))
    )
}

fn repeat_text(line: &str) -> String {
    format!(
        "{}Only a subagent's system prompt - its agent file - is reused across launches: its first message, the launch\nprompt included, has no cache breakpoint, so a block the prompts repeat is written fresh on every dispatch WHEREVER it\nsits (feature 383 research R16). Move the shared text into the agent file (.claude/agents/<name>.md) - a new defined\nagent if this is a general-purpose job that recurs - and let the prompt carry only what is particular to the unit.\nIf this shape is right here: AGENT_PREFIX_OK: <reason> in the prompt.\n{TRAILER}",
        bold(&format!("{line}."))
    )
}

pub(crate) fn judge(
    event: &Event,
    session: &Session,
    git_dir: &Path,
    now: f64,
    wave_unit: bool,
    headless: bool,
) -> Vec<Answer> {
    let fire = |kind: &str, detail: &str, rule: &str| {
        log::fire("agent-prefix", kind, detail, rule, &event.input, session);
    };
    match verdict(event, git_dir, now, wave_unit) {
        Said::Pass => Vec::new(),
        Said::Escaped => {
            fire(
                "escaped",
                "a shared block after a differing part, with a reason",
                "escape",
            );
            Vec::new()
        }
        // A headless session has no route but hand launches, and each returns inside its turn (feature 390, the round arbiter's fix).
        Said::Wave(kind) if headless => {
            fire(
                "escaped",
                &format!("a headless page session's {kind} wave (no Workflow tool)"),
                "escape",
            );
            Vec::new()
        }
        Said::Wave(kind) => {
            fire(
                "blocked",
                &format!("a 4th {kind} launch within seconds"),
                "wave",
            );
            vec![Answer::Refuse(wave_text(&kind))]
        }
        Said::Repeat(line) => {
            fire("blocked", &line, "repeated-block");
            vec![Answer::Refuse(repeat_text(&line))]
        }
    }
}

/// The suite's clock, a wave's own unit, a headless session.
fn switches(env: &dyn Fn(&str) -> Option<String>) -> (Option<f64>, bool, bool) {
    (
        env("L7R_AGENT_NOW").and_then(|c| c.parse().ok()),
        env("L7R_WAVE_UNIT").as_deref() == Some("1"),
        env("L7R_DISPATCHER").is_some_and(|v| !v.is_empty()),
    )
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let cwd = Some(field(&event.input, "cwd"))
        .filter(|c| !c.is_empty())
        .unwrap_or(".");
    let said = ask(
        Path::new("."),
        "git",
        &[
            "-C",
            cwd,
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        ],
        "",
    );
    if !said.ok() {
        return Vec::new();
    }
    let (clock, wave_unit, headless) = switches(&|k| std::env::var(k).ok());
    let now = clock.unwrap_or_else(|| {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map_or(0.0, |d| d.as_secs_f64())
    });
    judge(
        event,
        session,
        Path::new(said.out.trim()),
        now,
        wave_unit,
        headless,
    )
}

#[cfg(test)]
mod tests;
