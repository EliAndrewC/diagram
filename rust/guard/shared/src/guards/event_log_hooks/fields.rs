//! A line's fields beyond its base: a tool call's own (moved here from `event_log_hooks.rs` by feature 451 T04, which would have passed
//! the 1,000-line file cap), and a background run's (451 T04, FR-002, plan D3, research R2) - `bg` on a backgrounded call's
//! `PostToolUse`, `inflight` on every `Stop` and `SubagentStop`, and what a completion notice gives its `BgEnd` line - and a Bash
//! call's write targets, `writes` on its end's line (451 T93, [`bash_writes`]).

use std::collections::HashMap;
use std::path::Path;
use std::sync::LazyLock;
use std::time::{Duration, Instant};

use fancy_regex::Regex;
use serde_json::{Map, Value};

use crate::context::{call_of, Call};

use super::{
    digest, first_group, heading_only, make_target, or_empty, re, text_of, truthy, EDIT_TOOLS,
    MANIFEST, TASK, UNIT,
};

pattern!(TOOL_USE, r"<tool-use-id>([^<]+)</tool-use-id>");
pattern!(TASK_ID, r"<task-id>([^<]+)</task-id>");
pattern!(STATUS, r"<status>([^<]+)</status>");
pattern!(SUMMARY, r"<summary>([^<]*)</summary>");
pattern!(EXIT_CODE, r"exit code (-?\d+)");
pattern!(BLOCKS_LINE, r"(?m)^Blocks:[ \t]*(\S[^\n]*?)[ \t]*$");
pattern!(BLOCKS_ENV, r#"\bL7R_BLOCKS=(?:"([^"]*)"|'([^']*)'|(\S+))"#);

/// The task a command's own `T=` names, a heredoc's body left out (it is text written to a file, 451 T53): the one reading the
/// line's `own_t` (451 T286) and the static-runs guard's refusal of a bare `make closing-checks` (451 T451) share.
#[must_use]
pub fn own_task(command: &str) -> Option<String> {
    first_group(&TASK, &crate::shape::strip_heredocs(command))
}

/// A dispatch brief's or a page brief's BLOCKS CLUE (451 T243, the GM 2026-11-25: "to the extent that we can pass that kind of context
/// clues to our tooling when the data is collected ... that will make it easier"): its line `Blocks: <feature> T<n>`, `Blocks: T<n>`
/// or `Blocks: none` - the task whose next step waits on this work, or none - as written. The task time breakdown books by it.
#[must_use]
pub fn blocks_line(text: &str) -> Option<String> {
    first_group(&BLOCKS_LINE, text)
}

/// A command's clue, `L7R_BLOCKS=<feature>:T<n>` (or quoted, `"451 T5"`, or `none`), its `:` read as a space.
fn blocks_env(command: &str) -> Option<String> {
    let c = BLOCKS_ENV.captures(command).ok().flatten()?;
    let v = (1..=3).find_map(|i| c.get(i))?.as_str();
    Some(v.replace(':', " ").trim().to_owned())
}

/// The fields a tool's own call adds to its line.
pub(super) fn tool_fields(
    out: &mut Map<String, Value>,
    tool: &str,
    ti: &Map<String, Value>,
    payload: &Value,
) {
    if tool == "Bash" {
        let command = text_of(ti.get("command"));
        // EVERY TARGET, where the call runs more than one (feature 451 T14): `make` is the first alone, so `make rust-test CRATE=x &&
        // make static` logged no `static` and `static_runs_hooks` would not have counted it; `makes` lists them all, first included
        let mut all: Vec<String> = Vec::new();
        for t in crate::make::invoked(&command) {
            if !all.contains(&t) {
                all.push(t);
            }
        }
        let target = all.first().cloned().unwrap_or_default();
        out.extend(blocks_env(&command).map(|b| ("blocks".to_owned(), Value::from(b))));
        // A CLOSING RUN'S OWN `T=` (451 T286): the static-run count reads such a run by the line its script writes under that task as it
        // launches `make static`, and a closing run with none by this call's own line, filed under its own task
        if all.iter().any(|t| t == "closing-checks") && own_task(&command).is_some() {
            out.insert("own_t".into(), Value::Bool(true));
        }
        if all.len() > 1 {
            out.insert("makes".into(), Value::from(all));
        }
        if !target.is_empty() {
            if ["tick", "task-start", "decide", "land"].contains(&target.as_str()) {
                // a `T=` inside a heredoc's body is text written to a file, not this call's (451 T53)
                if let Some(task) = own_task(&command) {
                    out.insert("make".into(), Value::from(target.clone()));
                    out.insert("task".into(), Value::from(task));
                    return;
                }
            }
            out.insert("make".into(), Value::from(target));
        }
    } else if EDIT_TOOLS.contains(&tool) {
        let path = ti
            .get("file_path")
            .filter(|v| truthy(v))
            .or_else(|| ti.get("notebook_path").filter(|v| truthy(v)));
        out.insert("path".into(), or_empty(path));
        if tool == "Edit" {
            out.insert(
                "old".into(),
                Value::from(digest(&text_of(ti.get("old_string")))),
            );
            let new = text_of(ti.get("new_string"));
            out.insert("new".into(), Value::from(digest(&new)));
            if heading_only(&new) {
                out.insert("heading".into(), Value::Bool(true));
            }
        } else if tool == "Write" {
            out.insert(
                "new".into(),
                Value::from(digest(&text_of(ti.get("content")))),
            );
        }
    } else if tool == "Agent" {
        out.insert(
            "agent".into(),
            ti.get("subagent_type")
                .filter(|v| truthy(v))
                .cloned()
                .unwrap_or_else(|| Value::from("general-purpose")),
        );
        let prompt = text_of(ti.get("prompt"));
        out.extend(blocks_line(&prompt).map(|b| ("blocks".to_owned(), Value::from(b))));
        if let Some(m) = first_group(&MANIFEST, &prompt) {
            out.insert("manifest".into(), Value::from(m));
        }
        if let Some(u) = first_group(&UNIT, &prompt) {
            out.insert(
                "unit".into(),
                Value::from(u.trim_end_matches([',', ';', '.'])),
            );
        }
        if prompt.contains("REVIEW_ROUNDS_OK=") {
            out.insert("waiver".into(), Value::from(1));
        }
        if let Some(aid) = payload
            .get("tool_response")
            .and_then(|r| r.get("agentId"))
            .filter(|v| truthy(v))
        {
            out.insert("aid".into(), aid.clone());
        }
    }
}

/// A background run's fields on its event's line (D3): a backgrounded call's `PostToolUse` carries `bg`, the `backgroundTaskId` its
/// `tool_response` names (the id the run's notice and a stop's `background_tasks` name it by); a `Stop` or `SubagentStop` carries
/// `inflight`, each run of its `background_tasks` as `{id, type}` and a shell's make target, so a wait after the stop is booked to the
/// runs it waited on (T09). An empty list is written - nothing in flight is a fact the reader books by - and a payload with no list
/// (a harness before the field) writes none.
pub(super) fn run_fields(out: &mut Map<String, Value>, ev: &str, payload: &Value) {
    if matches!(ev, "PostToolUse" | "PostToolUseFailure") {
        bash_writes(out, payload);
    }
    if ev == "PostToolUse" {
        if let Some(bg) = payload
            .get("tool_response")
            .and_then(|r| r.get("backgroundTaskId"))
            .filter(|v| truthy(v))
        {
            out.insert("bg".into(), bg.clone());
        }
    } else if ev == "Stop" || ev == "SubagentStop" {
        if let Some(tasks) = payload.get("background_tasks").and_then(Value::as_array) {
            let runs = tasks
                .iter()
                .map(|r| {
                    let mut run = Map::new();
                    run.insert("id".into(), or_empty(r.get("id")));
                    run.insert("type".into(), or_empty(r.get("type")));
                    let target = make_target(&text_of(r.get("command")));
                    if !target.is_empty() {
                        run.insert("make".into(), Value::from(target));
                    }
                    Value::Object(run)
                })
                .collect();
            out.insert("inflight".into(), Value::Array(runs));
        }
    }
}

/// A Bash call's WRITE TARGETS on its end's line (feature 451 T93): `writes`, the files `shared::tree`'s walk (`walk_judged`, the tree
/// guards' walk) says the command wrote - a redirect, `sed -i` or `perl -pi`'s files, a file tool's (`cp`, `mv`, `tee`, `touch`, `rm`
/// and the rest), `dd of=` - each an absolute path, once, in the walk's order. Left out: a program that only reads (`how` "read"), a
/// target the walk cannot place, and a path that is a directory once the call has ended (a `make`, a `git` subcommand or a Python
/// program writes where the shell stands, a directory, and `mkdir` makes one: no file a reader can match). A call naming none writes
/// no field. Written on `PostToolUse` and `PostToolUseFailure` (a `sed -i F && make rust-test` red at its test still wrote F), never
/// on the start: a start is a call that may be refused (8,370 Bash starts and 8,224 ends in 451's log since 2026-11-20T20:00Z, measured
/// 2026-11-21, a Python count), so only an end says the command ran, and one line a call keeps the log's growth to one field. A
/// backgrounded call's end comes at its launch, before its command has run: its writes are named all the same (the walk reads the
/// command, not the disk), and a directory it has yet to make is named as a path, which names no file a reader can match.
///
/// A PYTHON PROGRAM (451 T96): the walk places a heredoc's or a `-c` program's write where the shell stands, a directory, so its files
/// were named nowhere - T84's `p='...plan/status.rs'; s=open(p).read() ... open(p,'w').write(s)` programs among them. After that
/// target come the files its literals name (`shared::tree::program`, make-only's reader of a guard file a program writes), resolved
/// where it runs, each an existing regular file at the call's end, with the reader's two fail-open choices, gate-write's: a literal
/// only read (`open(L)`, `Path(L).read_text()`) names nothing, and neither does one joined onto a base the program computes. WHY THE
/// OPEN SIDE: a name too many sets the caller's own file apart in the closing checks (a wrong green) and lists a file a program only
/// read for a landing to commit; a name too few costs a saving. WHY A FILE ON DISK: a literal naming none (`'w'`, `'utf-8'`, a word
/// of the text it edits) is no write a reader can match; a backgrounded program's file not yet written is missed, a saving lost.
///
/// WHY: T86's closing checks set aside the dirty files another task's lines name, and a Bash line named none - the Edit and Write
/// lines named 127 of the 796 files 2026-11-21's landings changed, measured 2026-11-21 (T86's `/tmp/t86/recall.py`). Its reader is
/// `scripts/gates/closing-checks.sh`, an exact path match, never a prefix: a `make` at the clone's root would claim the whole clone.
/// No walk is reused: every guard that walks (main-tree, gm-tree, make-only, readme, gate-write) runs on `PreToolUse` alone, and each
/// hook event is its own process, so none has walked when this line is written (observed 2026-11-21, method: each guard's `events`).
/// WHAT IT COSTS: 3.89 ms a Bash call's end (median; p90 7.32, max 19.04), the hook alone at 2.98 ms before, measured 2026-11-21
/// (`/tmp/t93/cost.py`: 600 of the night's commands through the binary `--only event-log-hooks PostToolUse` before and after, 3 runs
/// each) - nearly all the walk's first use in a process, its patterns compiled (3.2-8.6 ms a first walk, 9-57 us a second, measured
/// 2026-11-21, a scratch binary over `shared::tree`), which every Bash start already pays in main-tree; the walk itself is 69 us
/// (median, p99 1.76 ms over 9,637 commands, measured the same way). The start was priced and not taken (the session's builder, T93).
fn bash_writes(out: &mut Map<String, Value>, payload: &Value) {
    if text_of(payload.get("tool_name")) != "Bash" {
        return;
    }
    let command = text_of(payload.pointer("/tool_input/command"));
    if command.trim().is_empty() {
        return;
    }
    let cwd = text_of(payload.get("cwd"));
    let home = crate::env::opt("HOME").unwrap_or_default();
    let walk = crate::tree::walk_judged(
        &command,
        Some(cwd.as_str()).filter(|c| !c.is_empty()),
        "",
        &home,
    );
    let mut paths: Vec<String> = Vec::new();
    for t in walk.targets.into_iter().filter(|t| t.how != "read") {
        // a Python program's own files after where it stands (451 T96): its literals, resolved where it runs, each a file on disk
        let named = t
            .program
            .as_deref()
            .zip(t.path.as_deref().filter(|d| d.starts_with('/')))
            .map(|(body, dir)| {
                crate::tree::program::all_program_names(body, Some(dir), true, true, &|p| {
                    Path::new(p).is_file()
                })
            })
            .unwrap_or_default();
        for path in t.path.into_iter().chain(named) {
            if path.starts_with('/') && !paths.contains(&path) && !Path::new(&path).is_dir() {
                paths.push(path);
            }
        }
    }
    if !paths.is_empty() {
        out.insert("writes".into(), Value::from(paths));
    }
}

/// How long a stop waits for its agent's reply to reach the transcript (feature 451 T59): Claude Code writes a transcript's rows on a
/// timer, so at `SubagentStop` the reply's row is often not yet on disk - 60 of the 83 stops that carried a `tok` left out exactly that
/// call (its every row; `ctx` one call stale beside it), the reply stamped 15-52 ms before the stop, measured 2026-11-21 (each stop of the
/// clone's 451 log against its agent's transcript) - and it lands while the hook still runs: 7 of 12 stops off disk at the hook's start,
/// each landing 5.8-89.2 ms in, the other 5 on disk already, measured 2026-11-21 (a `claude -p` session's `SubagentStop` hook polling the
/// file every 5 ms). Ten times the probe's latest; past it, what is on disk is written, as before.
const REPLY_WAIT: Duration = Duration::from_millis(1000);
/// How often the wait looks again: each look reads only the bytes appended since the last.
const REPLY_POLL: Duration = Duration::from_millis(5);

/// An agent's cost on its `SubagentStop` line (feature 451 T07, plan D6, research R2): `tok`, its transcript's `in`, `cached`, `created`
/// and `out` tokens, each model call once, the top level of its usage - the builder's own iterations - and beside it `adv`, the same four
/// of its advisor calls' own iterations, which no top level holds ([`advisor_of`], 451 T69), zero where it called none; one call's
/// streamed reply is several `assistant` rows of one `message.id`, the last holding the whole output, so the last row of an id stands
/// for it (a sum over rows read the T202 builder's output 1,317,955 tokens against its 481,878, 723 rows of 305 ids, measured 2026-11-20 (a Python scan of its 50 MB transcript)); `ctx`, its last call's context. Both are
/// read by `context_cap_hooks`' row reader, the whole file for `tok` (a stop is cumulative: a resumed agent's file holds every leg, and
/// the reader keeps the last line per `aid`), once the payload's `last_assistant_message` is on disk ([`REPLY_WAIT`], T59). The
/// transcript is the payload's `agent_transcript_path`, else the one beside the session's; none readable, or no call in it, writes
/// neither field: the hook never refuses.
pub(super) fn agent_cost(out: &mut Map<String, Value>, payload: &Value) {
    agent_cost_within(out, payload, REPLY_WAIT);
}

/// [`agent_cost`], waiting at most `wait` for the reply.
pub(super) fn agent_cost_within(out: &mut Map<String, Value>, payload: &Value, wait: Duration) {
    use crate::context::{context, own_transcript};
    use std::io::Read as _;
    let own = text_of(payload.get("agent_transcript_path"));
    let path = if own.is_empty() {
        own_transcript(
            &text_of(payload.get("transcript_path")),
            &text_of(payload.get("agent_id")),
        )
    } else {
        Some(own.into())
    };
    let Some(mut file) = path.as_ref().and_then(|p| std::fs::File::open(p).ok()) else {
        return;
    };
    let said = text_of(payload.get("last_assistant_message"));
    let said = said.trim();
    let start = Instant::now();
    let mut tally = Tally::default();
    // the bytes read past the last whole row
    let mut rest: Vec<u8> = Vec::new();
    let mut chunk = vec![0; 1 << 16];
    loop {
        // what was appended since the last look, a chunk at a time: a 50 MB transcript is streamed, never held whole
        while let Ok(n @ 1..) = file.read(&mut chunk) {
            rest.extend_from_slice(&chunk[..n]);
            // the last newline is looked for in the new bytes alone, so a row longer than a chunk is not scanned again each chunk
            let Some(i) = chunk[..n].iter().rposition(|&b| b == b'\n') else {
                continue;
            };
            let whole = rest.len() - n + i + 1;
            for row in rest[..whole].split(|&b| b == b'\n') {
                tally.row(row);
            }
            rest.drain(..whole);
        }
        if said.is_empty() || tally.replied(said) || start.elapsed() >= wait {
            break;
        }
        std::thread::sleep(REPLY_POLL);
    }
    // a last row with no newline counts, as a split of the file read it
    tally.row(&rest);
    if tally
        .calls
        .iter()
        .all(|c| c.input + c.cached + c.created + c.out == 0)
    {
        return;
    }
    out.insert("tok".into(), summed(&tally.calls));
    out.insert("adv".into(), summed(&tally.adv));
    if let Some(ctx) = path.as_deref().and_then(context) {
        out.insert("ctx".into(), Value::from(ctx));
    }
}

/// `calls`' `in`, `cached`, `created` and `out` tokens, each summed.
fn summed(calls: &[Call]) -> Value {
    let n = |f: fn(&Call) -> u64| calls.iter().map(f).sum::<u64>();
    serde_json::json!({"in": n(|c| c.input), "cached": n(|c| c.cached), "created": n(|c| c.created), "out": n(|c| c.out)})
}

/// An `assistant` row's advisor calls (451 T69): its `usage.iterations` of type `advisor_message`, summed. On a row carrying an advisor
/// call the iterations are the builder's own call, the advisor's (its `model` named) and the builder's own again, and the top level,
/// [`call_of`]'s, sums the builder's two alone, so `tok` left out 82,254,728 input and 6,504,729 output tokens of the session's subagent
/// transcripts (588 calls over 2,722 rows, every row of one call carrying the same iterations), measured 2026-11-21 (`/tmp/t69/rows.py`,
/// the iterations summed one row per `message.id`). Only a row naming the type is parsed again, so a transcript with no advisor call is
/// read as before.
fn advisor_of(row: &[u8]) -> Call {
    const NEEDLE: &[u8] = b"advisor_message";
    let parsed = row
        .windows(NEEDLE.len())
        .any(|w| w == NEEDLE)
        .then(|| serde_json::from_slice::<Value>(row).ok())
        .flatten();
    parsed
        .as_ref()
        .and_then(|v| v.pointer("/message/usage/iterations"))
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter(|i| i.get("type").and_then(Value::as_str) == Some("advisor_message"))
        .fold(Call::default(), |a, i| {
            let n = |k: &str| i.get(k).and_then(Value::as_u64).unwrap_or(0);
            Call {
                input: a.input + n("input_tokens"),
                cached: a.cached + n("cache_read_input_tokens"),
                created: a.created + n("cache_creation_input_tokens"),
                out: a.out + n("output_tokens"),
                ..a
            }
        })
}

/// What an agent's transcript rows have shown so far: each model call once, its advisor calls' iterations beside it (`adv`, one a call,
/// 451 T69), and the last `assistant` row since the last `user` row - the reply, once it is on disk.
#[derive(Default)]
struct Tally {
    calls: Vec<Call>,
    adv: Vec<Call>,
    at: HashMap<String, usize>,
    last: Vec<u8>,
}

impl Tally {
    fn row(&mut self, row: &[u8]) {
        // a `user` row (a prompt, a tool's result) as Claude Code writes it: what came before it answers no later prompt
        const USER: &[u8] = br#""type":"user""#;
        if let Some(c) = call_of(row) {
            self.last = row.to_vec();
            let adv = advisor_of(row);
            // a row naming no id is a call of its own
            if let Some(&i) = self.at.get(&c.id).filter(|_| !c.id.is_empty()) {
                self.calls[i] = c;
                self.adv[i] = adv;
            } else {
                self.at.insert(c.id.clone(), self.calls.len());
                self.calls.push(c);
                self.adv.push(adv);
            }
        } else if row.windows(USER.len()).any(|w| w == USER) {
            self.last.clear();
        }
    }

    /// Whether the last row is the reply: a `text` block the agent's last message ends with (a reply of several blocks is their text
    /// joined; the probe's 12 were one block each, equal).
    fn replied(&self, said: &str) -> bool {
        let Ok(row) = serde_json::from_slice::<Value>(&self.last) else {
            return false;
        };
        row.pointer("/message/content")
            .and_then(Value::as_array)
            .is_some_and(|blocks| {
                blocks.iter().any(|b| {
                    let text = text_of(b.get("text"));
                    let text = text.trim();
                    !text.is_empty() && said.ends_with(text)
                })
            })
    }
}

/// What a completion notice gives its `BgEnd` line (D3): `id` (the launching call's `<tool-use-id>`), `bg` (its `<task-id>`),
/// `status` and `exit` - the LAST `exit code N` of its summary, the quoted description before it being free text; none where the run
/// was stopped or its session ended. None for a prompt that is no notice (one the GM typed, quoting one, is his), a notice naming no
/// launching call (a Monitor's event), and an AGENT's notice, whose `SubagentStop` is its end: an agent's notice names its launching
/// call's tool-use id too, 3,801 of the 3,986 agent notices beside all 1,992 shells' (measured 2026-11-20 (the `-diagram` and clone
/// transcripts' enqueued notices, tallied by summary and by a `<tool-use-id>` before any `<result>`)), so the id does not tell them apart -
/// the summary's `Agent "` does, and the writer also drops a notice whose launch line is an Agent call. Every other notice with an id
/// ends a background run the session can wait on and writes its end: a shell's, a workflow's (46 in the same count), a Monitor's stream
/// ended or stopped (128). Only the tags before a `<result>` are read: an agent's result is free text and can quote another notice.
pub(super) fn notice_end(prompt: &str) -> Option<Map<String, Value>> {
    let body = prompt.trim_start().strip_prefix("<task-notification>")?;
    let head = body.split("<result>").next().unwrap_or(body);
    let head = head.split("</task-notification>").next().unwrap_or(head);
    let id = first_group(&TOOL_USE, head)?;
    let summary = first_group(&SUMMARY, head).unwrap_or_default();
    if summary.starts_with("Agent \"") {
        return None;
    }
    let mut out = Map::new();
    out.insert("id".into(), Value::from(id));
    for (key, p) in [("bg", &TASK_ID), ("status", &STATUS)] {
        if let Some(v) = first_group(p, head) {
            out.insert(key.into(), Value::from(v));
        }
    }
    let code = EXIT_CODE
        .captures_iter(&summary)
        .map_while(Result::ok)
        .last()
        .and_then(|c| c.get(1).and_then(|m| m.as_str().parse::<i64>().ok()));
    if let Some(code) = code {
        out.insert("exit".into(), Value::from(code));
    }
    Some(out)
}
