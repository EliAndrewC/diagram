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
//! THE WRAP-UP BAND (451 T417, [`band`]): from the cap to [`WRAP_UP_CEILING_TOKENS`] (340k, a GUESS knob) a builder may still run its
//! stop point's own steps - the stop point's make targets, git status and diff, a read, the one plan review's dispatch - each recorded,
//! rule `wrap-up`; anything else is refused naming what is still allowed. Past the ceiling, the one exit below alone.
//!
//! THE ONE EXIT: a Write, Edit or Read of `<git common dir>/l7r-handoffs/<task>-<agent_id>.md` (`<agent_id>.md` where the call's line
//! carries no task) - any file there whose name ends `<agent_id>.md`, or that the builder's brief names there (451 T352, [`named`]:
//! `<task>-build.md`, `done-pending-<task>.md`), the refusal then naming the brief's file - so the refusal and the Write agree even where the task the event
//! log's chain reads moves between them, and no two builders share a file. The Read is let through so a handoff once written can be
//! overwritten (the Write tool refuses a file it has not read). A Write there passed the live guard chain from a background builder
//! (observed 2026-11-20, method: this task's builder writing `.git/l7r-handoffs/probe-<its id>.md` in its clone, then removing it).
//! The git dir, the task's starts and the permit are the SESSION's clone's (`shared::session`'s resolve, as `clone_sync_hooks` routes
//! an edit), the call's cwd's tree only where that resolves no work tree (451 T60): a builder whose shell was reset to the mirror wrote
//! its handoff in the mirror's `.git` (2026-11-21, T10's and T55's).
//!
//! The escape (FR-012): `CONTEXT_OK="<reason>"` in a Bash command, recorded; or, for any tool, the session's per-agent permit
//! `make context-ok AID= WHY=` (D9: the guard-edit permit's store, keyed `<clone>/context-cap:<agent id>`, an hour), each call it
//! lets through recorded. A call outside any clone passes.
//!
//! A BUILDER RESUMED (D10, 451 T13): a `SendMessage` whose `to` is a builder (its meta `agent-<to>.meta.json` beside its transcript, its
//! `agentType` no defined agent) is refused where that builder is past the cap, or its task - D2's chain: its brief's `T<n>`, else its
//! FIRST log line's task (`by` or `aid`), else the `task-starts.jsonl` entry in force at its dispatch (the Agent call's log line by the
//! meta's `toolUseId`, else its first line, else its transcript's first row) - has an `end` line, `landed` true, after that dispatch,
//! or is ticked; the refusal names a fresh dispatch with the handoff. No task found passes, recorded `resume, no task`, under the cap
//! only. Its escape: `CONTEXT_OK="<reason>"` in the `SendMessage`'s `summary`. Measured 2026-11-20 (the session transcript's `SendMessage`
//! rows): a `SendMessage`'s input is `{to, summary, message}`, `to` the agent id; the builder's own log lines carry `by`, its
//! `SubagentStart` and its Agent call's `PostToolUse` `aid` (grep of the clone's 451 log).

use std::fs::File;
use std::io::{BufRead as _, BufReader};
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use serde_json::{json, Value};

use crate::guards::event_log_hooks::read::read_jsonl;
use crate::guards::event_log_hooks::{common_git_dir, filed_at};
use crate::guards::guard_file_hooks::permit_reason;
use crate::protocol::{Answer, Event, Guard};
use crate::shared::context::{context, own_transcript};
#[cfg(test)]
use crate::shared::context::{usage_of, TAIL_BYTES};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log::fire;
use crate::shared::session::Session;
use crate::shared::speckit::tasks::{all_text, archived};
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "context-cap-hooks",
    events: &["PreToolUse"],
    matcher: "*",
    decide,
};

/// The context, in tokens, past which a builder's next tool call is refused: the shared crate's [`crate::shared::context::CAP_TOKENS`]
/// (moved there by 451 T193, whose idle check tells a capped builder's wake from a stalled one's).
pub const CONTEXT_CAP_TOKENS: u64 = crate::shared::context::CAP_TOKENS;

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
    /// Refused, naming the handoff file; `code` where its brief makes it a code builder (451 T237, [`split`]).
    Refused {
        agent: String,
        tokens: u64,
        handoff: PathBuf,
        code: bool,
    },
    /// A code builder's dispatch of a claims agent (451 T237, [`split`]).
    Split(Split),
    /// In the wrap-up band (451 T417, [`band`]): a stop point's step, let through, what it is recorded.
    Band(String),
    /// In the wrap-up band: anything else, refused, naming what and the handoff.
    BandRefused {
        agent: String,
        tokens: u64,
        handoff: PathBuf,
        what: String,
    },
    /// Past the cap, let through by the session's `make context-ok` permit for this agent, its reason.
    Permitted(String),
    /// A resume of a builder whose task none of D2's rungs finds: passed, recorded.
    ResumeNoTask(String),
    /// A resume of an agent with no meta file beside its transcript: passed, recorded.
    ResumeNoMeta(String),
    /// A resume refused (D10): the agent and why it is stale.
    Resume {
        agent: String,
        stale: Stale,
        handoff: PathBuf,
    },
}

/// Why a resumed builder is stale.
#[derive(Debug, PartialEq, Eq)]
enum Stale {
    /// Past the cap, its context.
    PastCap(u64),
    /// Its task landed since its dispatch, or is ticked.
    Landed(String),
}

/// The time a permit is judged at: `L7R_PERMIT_NOW` (the guard-edit permit's seam), else the clock.
fn now(env: &dyn Fn(&str) -> Option<String>) -> f64 {
    env("L7R_PERMIT_NOW")
        .and_then(|n| n.parse().ok())
        .unwrap_or_else(|| {
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .map_or(0.0, |d| d.as_secs_f64())
        })
}

/// D9's permit key, the "file" `make context-ok` grants: `<the clone's top level>/context-cap:<agent id>`. The top level, not a bare
/// key: the permit store is found by `git -C <its parent> rev-parse --absolute-git-dir`, which a bare key would run from `/`.
fn permit_key(tree: &Path, agent: &str) -> String {
    format!("{}/context-cap:{agent}", tree.display())
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
    let clone = || session.clone_dir().map(Path::to_path_buf);
    match judge(&event.input, here, env, CONTEXT_CAP_TOKENS, &clone) {
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
            code,
        }) => {
            log("blocked", &format!("{agent}: {tokens} tokens"), "past-cap");
            vec![Answer::Refuse(refusal(tokens, &handoff, code))]
        }
        Some(Said::Band(what)) => {
            log("passed", &what, "wrap-up");
            Vec::new()
        }
        Some(Said::BandRefused {
            agent,
            tokens,
            handoff,
            what,
        }) => {
            log(
                "blocked",
                &format!("{agent}: {tokens} tokens: {what}"),
                "wrap-up-refused",
            );
            vec![Answer::Refuse(band_refusal(tokens, &handoff, &what))]
        }
        Some(Said::Split(Split::Refused(kind))) => {
            log("blocked", &kind, "builder-split");
            vec![Answer::Refuse(split::refusal(&kind))]
        }
        Some(Said::Split(Split::Escaped(why))) => {
            log("escaped", &why, "split-ok");
            Vec::new()
        }
        Some(Said::Split(Split::NoReason(text))) => {
            log("blocked", "SPLIT_OK with no reason", "SPLIT_OK-no-reason");
            vec![Answer::Refuse(text)]
        }
        Some(Said::Permitted(why)) => {
            log("escaped", &why, "context-ok-permit");
            Vec::new()
        }
        Some(Said::ResumeNoTask(agent)) => {
            log(
                "passed",
                &format!("resume, no task: {agent}"),
                "resume-no-task",
            );
            Vec::new()
        }
        Some(Said::ResumeNoMeta(agent)) => {
            log(
                "passed",
                &format!("resume, no meta file: {agent}"),
                "resume-no-meta",
            );
            Vec::new()
        }
        Some(Said::Resume {
            agent,
            stale,
            handoff,
        }) => {
            let (detail, rule) = match &stale {
                Stale::PastCap(n) => (format!("resume {agent}: {n} tokens"), "resume-past-cap"),
                Stale::Landed(t) => (format!("resume {agent}: {t} landed"), "resume-landed"),
            };
            log("blocked", &detail, rule);
            vec![Answer::Refuse(resume_refusal(&agent, &stale, &handoff))]
        }
    }
}

/// The verdict on one hook input against the cap `cap`: None to pass it silently. A `SendMessage` is judged as a resume (D10) once its
/// sender's own cap lets it through: a builder past its cap is refused its `SendMessage` as any other call. A code builder's dispatch
/// of a claims agent is judged by the split (451 T237) once the cap lets it through. `clone` is the session's clone, asked only past
/// the cap or on a resume of a builder (451 T60, [`seat`]).
fn judge(
    input: &Value,
    here: &Path,
    env: &dyn Fn(&str) -> Option<String>,
    cap: u64,
    clone: &dyn Fn() -> Option<PathBuf>,
) -> Option<Said> {
    let own = own_cap(input, here, env, cap, clone);
    if matches!(
        own,
        Some(Said::Refused { .. } | Said::BandRefused { .. } | Said::NoReason(_))
    ) {
        return own;
    }
    // THE SPLIT (451 T237): a claims agent's dispatch, named before anything is read, from a code builder
    if let Some((kind, text)) = split::dispatch(input) {
        if builder_tree(input, here).is_some()
            && own_transcript(field(input, "transcript_path"), field(input, "agent_id"))
                .is_some_and(|t| split::code_builder(&t))
        {
            return Some(Said::Split(split::judge(kind, &text)));
        }
    }
    if field(input, "tool_name") != "SendMessage" {
        return own;
    }
    resume(input, here, env, cap, clone)
}

/// The working tree of a builder's call (D8): None for the main session (no `agent_id`), an id no path can take, a call in no tree,
/// or a defined agent (its type names a file of the tree's `.claude/agents/`, a stat and no read).
fn builder_tree(input: &Value, here: &Path) -> Option<PathBuf> {
    if !plain(field(input, "agent_id")) {
        return None;
    }
    let tree = tree_of(&match field(input, "cwd") {
        "" => here.to_path_buf(),
        c => PathBuf::from(c),
    })?;
    let kind = field(input, "agent_type");
    let defined = plain(kind)
        && tree
            .join(".claude/agents")
            .join(format!("{kind}.md"))
            .is_file();
    (!defined).then_some(tree)
}

/// The verdict on a call against its own builder's cap (D8, D9).
fn own_cap(
    input: &Value,
    here: &Path,
    env: &dyn Fn(&str) -> Option<String>,
    cap: u64,
    clone: &dyn Fn() -> Option<PathBuf>,
) -> Option<Said> {
    // THE MAIN SESSION, AN ID NO PATH CAN TAKE AND A DEFINED AGENT (D8): every call of the main thread ends here, nothing read
    let tree = builder_tree(input, here)?;
    let agent = field(input, "agent_id");
    let own = own_transcript(field(input, "transcript_path"), agent)?;
    let tokens = context(&own)?;
    if tokens <= cap {
        return None;
    }
    // ITS HANDOFF, ITS TASK AND ITS PERMIT IN THE SESSION'S CLONE, whatever tree its shell stands in (451 T60, [`seat`])
    let home = seat(clone(), &tree);
    let (root, _, _, task) = filed_at(&with_cwd(input, &home), here, env)?;
    let dir = common_git_dir(&root).join(HANDOFFS);
    // THE FILES ITS BRIEF NAMES there (451 T352, [`named`]): the exit takes them, and the refusal names the first
    let brief = split::brief(&own);
    let briefed = named::named(&brief, &dir);
    let handoff = briefed.first().cloned().unwrap_or_else(|| {
        dir.join(task.map_or_else(|| format!("{agent}.md"), |t| format!("{t}-{agent}.md")))
    });
    let tool = field(input, "tool_name");
    let ti = input.get("tool_input").unwrap_or(&Value::Null);
    let file = field(ti, "file_path");
    if ["Write", "Edit", "Read"].contains(&tool)
        && (is_handoff(file, &dir, agent) || in_dir_named(file, &briefed))
    {
        return Some(Said::Handoff(file.to_owned()));
    }
    // D9'S PERMIT: `make context-ok AID= WHY=`, the session's grant for this one agent, an hour (the guard-edit permit's store)
    let granted = permit_reason(&permit_key(&home, agent), now(env));
    if !granted.is_empty() {
        return Some(Said::Permitted(granted));
    }
    if tool == "Bash" {
        match escape_or_refuse(field(ti, "command"), TOKEN) {
            Escape::Escaped(why) => return Some(Said::Escaped(why)),
            Escape::Refused(text) => return Some(Said::NoReason(text)),
            Escape::None => {}
        }
    }
    // THE WRAP-UP BAND (451 T417, [`band`]): from the cap to the ceiling, the stop point's own steps
    if tokens <= cap + (band::CEILING_TOKENS - CONTEXT_CAP_TOKENS) {
        let home_dir = env("HOME").unwrap_or_default();
        let at = band::At {
            cwd: Some(field(input, "cwd")).filter(|c| !c.is_empty()),
            home: &home_dir,
            handoff: &|p: &str| is_handoff(p, &dir, agent) || in_dir_named(p, &briefed),
        };
        return Some(match band::judge(tool, ti, &at) {
            band::Band::Allowed(what) => Said::Band(what),
            band::Band::Refused(what) => Said::BandRefused {
                agent: agent.to_owned(),
                tokens,
                handoff,
                what,
            },
        });
    }
    Some(Said::Refused {
        agent: agent.to_owned(),
        tokens,
        handoff,
        code: split::is_code(&brief),
    })
}

/// D10: the verdict on a `SendMessage` resuming the agent `to` - refused where it is a builder past the cap, or whose task (D2's chain)
/// has landed since its dispatch or is ticked; passed where nothing names it a builder, or anything it needs will not read.
fn resume(
    input: &Value,
    here: &Path,
    env: &dyn Fn(&str) -> Option<String>,
    cap: u64,
    clone: &dyn Fn() -> Option<PathBuf>,
) -> Option<Said> {
    let ti = input.get("tool_input")?;
    let to = field(ti, "to");
    if !plain(to) {
        return None;
    }
    let tree = tree_of(&match field(input, "cwd") {
        "" => here.to_path_buf(),
        c => PathBuf::from(c),
    })?;
    // ITS META, beside its transcript: none (or none that reads), no telling a builder from a defined agent - passed, recorded
    let session = field(input, "transcript_path");
    let own = own_transcript(session, to)?;
    let Some(meta) = std::fs::read_to_string(own.with_extension("meta.json"))
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
    else {
        return Some(Said::ResumeNoMeta(to.to_owned()));
    };
    let kind = field(&meta, "agentType");
    if plain(kind)
        && tree
            .join(".claude/agents")
            .join(format!("{kind}.md"))
            .is_file()
    {
        return None;
    }
    let past = context(&own).filter(|&n| n > cap);
    let home = seat(clone(), &tree);
    // its feature and log, as the agent's own line is filed; never that line's task, whose last rung is the latest start (D10)
    let probe = json!({"hook_event_name": "PreToolUse", "agent_id": to, "transcript_path": session, "cwd": home});
    let (task, landed) = filed_at(&probe, here, env).map_or((None, false), |(root, f, log, _)| {
        task_landed(&root, &f, &log, &meta, to, &own)
    });
    let stale = match (past, &task) {
        (Some(n), _) => Stale::PastCap(n),
        (None, Some(t)) if landed => Stale::Landed(t.clone()),
        (None, Some(_)) => return None,
        (None, None) => return Some(Said::ResumeNoTask(to.to_owned())),
    };
    match escape_or_refuse(field(ti, "summary"), TOKEN) {
        Escape::Escaped(why) => Some(Said::Escaped(why)),
        Escape::Refused(text) => Some(Said::NoReason(text)),
        Escape::None => Some(Said::Resume {
            agent: to.to_owned(),
            stale,
            handoff: handoff_of(&home, task.as_deref(), to, &split::brief(&own)),
        }),
    }
}

/// A resumed builder's task by D2's chain - its brief's `T<n>`, else its FIRST log line's task, else the start in force at its
/// dispatch - and whether it has landed since that dispatch (an `end` line, `landed` true, naming it) or is ticked.
fn task_landed(
    root: &Path,
    feature: &str,
    log: &Path,
    meta: &Value,
    agent: &str,
    own: &Path,
) -> (Option<String>, bool) {
    let lines = read_jsonl(log).unwrap_or_default();
    // the builder's own lines carry `by`, its SubagentStart and its Agent call's PostToolUse `aid`
    let first = lines
        .iter()
        .find(|l| text(l, "by") == agent || text(l, "aid") == agent);
    let call = field(meta, "toolUseId");
    let dispatch = lines
        .iter()
        .find(|l| {
            !call.is_empty()
                && text(l, "ev") == "PreToolUse"
                && text(l, "tool") == "Agent"
                && text(l, "id") == call
        })
        .or(first)
        .map(|l| stamp(text(l, "t")))
        .filter(|t| !t.is_empty())
        .or_else(|| first_timestamp(own));
    let in_force = || {
        let d = dispatch.as_deref()?;
        // a start and its `make task-unstart` read as no start (451 T359)
        crate::shared::speckit::marks::starts_text(&common_git_dir(root))
            .lines()
            .filter_map(|l| serde_json::from_str::<Value>(l.trim()).ok())
            .filter(|e| {
                text(e, "feature") == feature
                    && !text(e, "task").is_empty()
                    && stamp(text(e, "utc")).as_str() <= d
                    // this tree's start, not another worktree's builder's (451 T254); a row naming no tree is from before
                    && e.get("tree").and_then(Value::as_str).is_none_or(|t| {
                        crate::shared::speckit::marks::same_tree(Path::new(t), root)
                    })
            })
            .next_back()
            .map(|e| text(&e, "task").to_owned())
    };
    let Some(task) = task_named(field(meta, "description"))
        .or_else(|| {
            first
                .map(|l| text(l, "task"))
                .filter(|t| !t.is_empty())
                .map(str::to_owned)
        })
        .or_else(in_force)
    else {
        return (None, false);
    };
    let since = |l: &&Value| {
        dispatch
            .as_deref()
            .is_some_and(|d| stamp(text(l, "t")).as_str() > d)
    };
    let landed = lines.iter().filter(since).any(|l| {
        text(l, "ev") == "Phase"
            && text(l, "step") == "end"
            && l.get("landed") == Some(&Value::Bool(true))
            && l.get("tasks")
                .and_then(Value::as_array)
                .is_some_and(|ts| ts.iter().any(|t| t.as_str() == Some(task.as_str())))
    }) || all_text(&root.join("specs").join(feature))
        .is_ok_and(|t| archived(&t, &task));
    (Some(task), landed)
}

fn text<'a>(line: &'a Value, k: &str) -> &'a str {
    line.get(k).and_then(Value::as_str).unwrap_or("")
}

/// A time as one form compares (`static_runs_hooks`' rule): `task-starts.jsonl`'s `utc` is to the second, a log line's `t` and a
/// transcript row's `timestamp` to the millisecond.
fn stamp(t: &str) -> String {
    match t.strip_suffix('Z') {
        Some(head) if !head.contains('.') => format!("{head}.000Z"),
        _ => t.to_owned(),
    }
}

/// The first `timestamp` among a transcript's first rows: the dispatch where the log holds none.
fn first_timestamp(own: &Path) -> Option<String> {
    BufReader::new(File::open(own).ok()?)
        .lines()
        .take(16)
        .map_while(Result::ok)
        .filter_map(|l| serde_json::from_str::<Value>(&l).ok())
        .map(|r| stamp(text(&r, "timestamp")))
        .find(|t| !t.is_empty())
}

/// The first `T<n>` (a letter after it allowed) a brief's description names.
fn task_named(description: &str) -> Option<String> {
    description
        .split(|c: char| !c.is_ascii_alphanumeric())
        .find(|w| {
            w.strip_prefix('T').is_some_and(|rest| {
                let digits = rest.trim_end_matches(|c: char| c.is_ascii_lowercase());
                !digits.is_empty()
                    && digits.chars().all(|c| c.is_ascii_digit())
                    && rest.len() - digits.len() <= 1
            })
        })
        .map(str::to_owned)
}

/// The handoff a resumed builder's refusal names: a file its brief names there that is written (451 T352, [`named`]), else one it
/// wrote ending `<agent>.md`, else the brief's first, else the one the cap would name.
fn handoff_of(tree: &Path, task: Option<&str>, agent: &str, brief: &str) -> PathBuf {
    let dir = common_git_dir(tree).join(HANDOFFS);
    let briefed = named::named(brief, &dir);
    let mine = format!("{agent}.md");
    briefed
        .iter()
        .find(|p| p.is_file())
        .cloned()
        .or_else(|| {
            std::fs::read_dir(&dir).ok().and_then(|es| {
                es.filter_map(Result::ok)
                    .map(|e| e.path())
                    .filter(|p| {
                        p.file_name()
                            .is_some_and(|n| n.to_string_lossy().ends_with(&mine))
                    })
                    .max()
            })
        })
        .or_else(|| briefed.first().cloned())
        .unwrap_or_else(|| dir.join(task.map_or_else(|| mine.clone(), |t| format!("{t}-{mine}"))))
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

/// The tree a builder's handoff, its task's starts and its permit are read in (451 T60): the session's clone (`shared::session`'s
/// resolve - the claim map, else the session's name - as `clone_sync_hooks` routes an edit) where it is a work tree, else `tree`,
/// the one the call's cwd stands in. WHY: a builder whose shell was reset to the mirror was named its handoff under the MIRROR's `.git`,
/// and wrote it there (2026-11-21: T10's and T55's handoffs at /diagram/.git/l7r-handoffs/, the mirror being no workspace), its
/// task looked up in the mirror's starts, not the clone's, and its `make context-ok` permit, keyed by the clone, unseen.
fn seat(clone: Option<PathBuf>, tree: &Path) -> PathBuf {
    clone.filter(|c| c.join(".git").exists()).map_or_else(
        || tree.to_path_buf(),
        |c| std::fs::canonicalize(&c).unwrap_or(c),
    )
}

/// `input` with its `cwd` the tree `home`, so its line's feature, log and task are read where its handoff is written.
fn with_cwd(input: &Value, home: &Path) -> Value {
    let mut at = input.clone();
    if let Some(o) = at.as_object_mut() {
        o.insert("cwd".to_owned(), json!(home));
    }
    at
}

/// Whether `file` is this agent's handoff: in `dir`, its name ending `<agent>.md`.
fn is_handoff(file: &str, dir: &Path, agent: &str) -> bool {
    let p = Path::new(file);
    p.file_name()
        .is_some_and(|n| n.to_string_lossy().ends_with(&format!("{agent}.md")))
        && p.parent().is_some_and(|d| real(d) == real(dir))
}

/// Whether `file` is one of `briefed` (451 T352): its name one of theirs, in their directory, compared by its real path.
fn in_dir_named(file: &str, briefed: &[PathBuf]) -> bool {
    let p = Path::new(file);
    briefed.iter().any(|b| {
        p.file_name() == b.file_name()
            && p.parent()
                .zip(b.parent())
                .is_some_and(|(d, e)| real(d) == real(e))
    })
}

fn real(d: &Path) -> PathBuf {
    std::fs::canonicalize(d).unwrap_or_else(|_| d.to_path_buf())
}

/// The refusal: the context against the cap, the handoff file, the next step, the escape. 451 T177 (message-check): the why is one
/// clause; its figures (10 s per 1,000 output tokens under 200k, 23 s over 700k) and its spec line (451 FR-006) are this module's.
/// A code builder's (`code`, 451 T237) also names the split: it hands off at its stop point, the claims round not its own.
fn refusal(tokens: u64, handoff: &Path, code: bool) -> String {
    let path = handoff.display();
    let split = if code {
        "\n     A code builder hands off at its STOP POINT and does not run the claims round: say what of it is left."
    } else {
        ""
    };
    format!(
        "\n\u{1b}[1mBLOCKED: this builder's context is {tokens} tokens, past the cap of {CONTEXT_CAP_TOKENS}.\u{1b}[0m\n\n\
Long contexts slow model calls, so the task goes on in a fresh builder:\n\n\
  1. Write the handoff file - what is done, what is left, the files touched and the next command - with the Write tool,\n\
     the one call this guard lets through:\n\n       {path}{split}\n\n\
  2. Stop, and reply with that path; the main session dispatches a fresh builder from it.\n\n\
Escape: {TOKEN}=\"<reason>\" (two words or more) in a Bash command, recorded in the guard log.\n"
    )
}

/// The wrap-up band's refusal (451 T417, [`band`]): where the builder stands, what was refused, what it may still run, the handoff.
fn band_refusal(tokens: u64, handoff: &Path, what: &str) -> String {
    let path = handoff.display();
    let ceiling = band::CEILING_TOKENS;
    let make = band::MAKE.join(", ");
    format!(
        "\n\u{1b}[1mBLOCKED: this builder's context is {tokens} tokens, past the cap of {CONTEXT_CAP_TOKENS}: in its wrap-up band, up to {ceiling}, it only finishes its stop point.\u{1b}[0m\n\n\
Refused: {what}.\n\
Still allowed: make {make}; git status or git diff; a Read or Grep (head, tail, grep in Bash); cd and export;\n\
the one plan review `make decide` or `make plan-delta` prints (spec-fidelity, its prompt opening MODE 4: PLAN REVIEW);\n\
and the handoff's Write:\n\n       {path}\n\n\
Code or a fix still owed goes in the handoff, for a fresh builder. Past {ceiling} only the handoff's Write is let through.\n\n\
Escape: {TOKEN}=\"<reason>\" (two words or more) in a Bash command, recorded in the guard log.\n"
    )
}

/// A resume's refusal (D10): why the builder is stale, the fresh dispatch with its handoff, the escape and the permit after it.
fn resume_refusal(agent: &str, stale: &Stale, handoff: &Path) -> String {
    let path = handoff.display();
    let (why, brief) = match stale {
        Stale::PastCap(n) => (
            format!("its context is {n} tokens, past the cap of {CONTEXT_CAP_TOKENS}"),
            "its handoff file as the brief",
        ),
        Stale::Landed(t) => (
            format!("its task {t} has landed or is ticked"),
            "the next task's brief (with its handoff file, if it wrote one)",
        ),
    };
    let written = if handoff.is_file() {
        String::new()
    } else {
        format!(
            "\n     The file is not written yet: to have it written, resume {agent} once with {TOKEN}=\"<reason>\" in the\n     \
SendMessage's summary, telling it to write that file and stop (its cap lets that Write through at any size).\n"
        )
    };
    format!(
        "\n\u{1b}[1mBLOCKED: resuming builder {agent}: {why}.\u{1b}[0m\n\n\
Dispatch a fresh builder (the Agent tool) with {brief}:\n\n       {path}\n{written}\n\
Escape: {TOKEN}=\"<reason>\" (two words or more) in the SendMessage's summary.\n\
Even resumed, a builder past the cap may run only its stop point's steps and its handoff up to {ceiling} tokens,\n\
and only its handoff past that, unless the session grants it an hour: make context-ok AID={agent} WHY=\"<reason>\"\n",
        ceiling = band::CEILING_TOKENS
    )
}

mod band;
mod named;
mod split;

/// The wrap-up band's ceiling (451 T417, [`band::CEILING_TOKENS`], a GUESS knob).
pub const WRAP_UP_CEILING_TOKENS: u64 = band::CEILING_TOKENS;

use split::Split;

#[cfg(test)]
mod tests;
