//! `escalation-hooks` (the GM 2026-09-12; features 375, 429, 432; ported from the shell of the same name and `lib/hm_gm_question.py`, feature 449 T044): FINDINGS DO NOT REACH THE GM UNTIL AN
//! INDEPENDENT CHECK HAS FILTERED THEM. A review agent's dispatch arms a requirement and an `escalation-check` dispatch disarms it; the turn may not close between (once per armed review, never a loop).
//! A question or offer in the final message with no review behind it owes the filter too (feature 429), and a question kept for the GM is named the turn it is kept (feature 432). `ESCALATION_OK` with
//! a reason in the dispatch prompt is the escape.

use std::collections::BTreeSet;
use std::fs::File;
use std::io::{self, Read, Seek, SeekFrom};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;
use std::time::{SystemTime, UNIX_EPOCH};

use fancy_regex::Regex;
use serde_json::{Map, Value};

use crate::guards::agent_prefix_hooks::lines_kept;
use crate::protocol::{Answer, Event, Guard, Reply};
use crate::shared::log::{self, civil};
use crate::shared::session::Session;
use crate::shared::sha1;
use crate::shared::state::field;
use crate::shared::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "escalation-hooks",
    events: &["PreToolUse", "Stop"],
    matcher: "Agent",
    decide,
};

/// The agents whose findings reach the GM: a short, stated roster, so a new reviewer is a deliberate addition.
const REVIEW_AGENTS: [&str; 3] = ["settlement-review", "building-review", "size-audit"];
const FILTER: &str = "escalation-check";
/// CONVENTION: how much of a transcript is read at a time from its end, as `hm_gm_question.py` read it.
const CHUNK: u64 = 1 << 20;

/// `scripts/reviews/ledger_lint.py`, by path: it has its own callers and stays for its phase (T044 decision (b)).
const COUNT_CODE: &str = "import sys; sys.path.insert(0, sys.argv[1]); import ledger_lint as l; print(len(l.measured_rows(open(sys.argv[2]).read())))";
const DISPOSED_CODE: &str = r#"import sys; sys.path.insert(0, sys.argv[1]); import ledger_lint as l
rows = [dict(zip(l.COLUMNS, c)) for _n, c in l.measured_rows(open(sys.argv[2]).read())[int(sys.argv[4] or 0):] if len(c) == len(l.COLUMNS)]
mine = [r for r in rows if r["check"] == sys.argv[3]]
sys.exit(0 if mine and all(l.disposed(r) is True for r in mine) else 1)"#;

const TOLD_AT_DISPATCH: &str = "A review is running, so its findings will need the escalation-check filter before any of them reach the GM: dispatch `escalation-check` with your DRAFT writeup as the prompt, and it returns keep/cut/rewrite per item with the norms it could not verify. The GM asked for this after three findings reached them that no project norm supported (2026-09-12). If you will relay nothing, say so with ESCALATION_OK=\"<reason>\".";

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static FENCE: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)```.*?```"));
static CODE: LazyLock<Regex> = LazyLock::new(|| re(r"`[^`\n]*`"));
static QUOTED: LazyLock<Regex> =
    LazyLock::new(|| re("\"[^\"\\n]*\"|\u{201c}[^\u{201d}\\n]*\u{201d}"));
static ASK: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)\b(should I|shall I|do you want|would you (like|prefer|rather)|want me to|which (one|of|would|do you)|your call|or should (I|we)|do you agree|is that (ok|okay|right|what you)|can you confirm|let me know (whether|which)|say (go|the word|yes)|for you to (decide|approve|choose|pick|confirm|rule)|approve or decline|ask (of )?you|needs your (words|approval|decision|ruling|go-ahead|call|answer)|waiting (on|for) (you|your)|yours to (decide|call|choose))\b",
    )
});
static OFFER: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)\b(if you('d| would)? (want|like|prefer|rather)|let me know if|happy to|say so and I'll|easy to (revert|reverse|undo)|I can (also |easily )?(revert|reverse|undo|switch|change|restore|raise|add|drop|re-?run|put (it|them) back))\b",
    )
});
static ADDRESSED: LazyLock<Regex> = LazyLock::new(|| re(r"\b(you|your|I)\b"));

/// What this guard needs from outside the call.
pub(crate) struct Ctx<'a> {
    pub(crate) tree: PathBuf,
    pub(crate) python: &'a str,
    pub(crate) count_code: &'a str,
    pub(crate) disposed_code: &'a str,
}

fn matches_any(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

fn blank(pattern: &Regex, text: &str) -> String {
    let (mut out, mut from) = (String::new(), 0);
    for m in pattern.find_iter(text).flatten() {
        out.push_str(&text[from..m.start()]);
        from = m.end();
    }
    out + &text[from..]
}

fn short(line: &str) -> String {
    line.chars().take(200).collect()
}

/// (the lines that ASK the reader, the lines that only OFFER): an ask wins over an offer on the same line.
pub(crate) fn classify(text: &str) -> (Vec<String>, Vec<String>) {
    let (mut asks, mut offers) = (Vec::new(), Vec::new());
    let body = blank(&FENCE, text);
    for raw in lines_kept(&body) {
        let line = raw.trim();
        if line.starts_with('>') {
            continue;
        }
        let s = blank(&QUOTED, &blank(&CODE, line));
        if matches_any(&ASK, &s)
            || (!matches_any(&OFFER, &s) && s.ends_with('?') && matches_any(&ADDRESSED, &s))
        {
            asks.push(short(&s));
        } else if matches_any(&OFFER, &s) {
            offers.push(short(&s));
        }
    }
    (asks, offers)
}

/// The transcript's records, last first, read from the end (a main transcript runs to hundreds of MB), until `visit` says stop.
fn backward(path: &str, visit: &mut dyn FnMut(&Value) -> bool) -> io::Result<()> {
    let mut file = File::open(path)?;
    let mut pos = file.seek(SeekFrom::End(0))?;
    let mut tail: Vec<u8> = Vec::new();
    while pos > 0 {
        let step = CHUNK.min(pos);
        pos -= step;
        file.seek(SeekFrom::Start(pos))?;
        let mut piece = vec![0; usize::try_from(step).unwrap_or(0)];
        file.read_exact(&mut piece)?;
        piece.append(&mut tail);
        let mut parts: Vec<&[u8]> = piece.split(|b| *b == b'\n').collect();
        let first = parts.remove(0);
        for raw in parts.iter().rev() {
            if let Ok(rec) = serde_json::from_slice::<Value>(raw) {
                if visit(&rec) {
                    return Ok(());
                }
            }
        }
        tail = first.to_vec();
    }
    if let Ok(rec) = serde_json::from_slice::<Value>(&tail) {
        visit(&rec);
    }
    Ok(())
}

fn is_gm_message(rec: &Value) -> bool {
    if field(rec, "type") != "user"
        || rec
            .get("isMeta")
            .is_some_and(|m| !m.is_null() && *m != Value::Bool(false))
    {
        return false;
    }
    match rec.pointer("/message/content") {
        Some(Value::String(c)) => !c.starts_with('<'),
        Some(Value::Array(c)) => c.iter().any(|x| field(x, "type") == "text"),
        _ => false,
    }
}

/// Was `escalation-check` dispatched after the GM's last message? True when the transcript cannot be read: never refuse on one the hook cannot see.
fn filtered_since_gm(path: &str) -> bool {
    let mut seen = false;
    let read = backward(path, &mut |rec| {
        if is_gm_message(rec) {
            return true;
        }
        let blocks = rec.pointer("/message/content").and_then(Value::as_array);
        let filter = field(rec, "type") == "assistant"
            && blocks.into_iter().flatten().any(|x| {
                field(x, "type") == "tool_use"
                    && ["Agent", "Task"].contains(&field(x, "name"))
                    && x.pointer("/input/subagent_type").and_then(Value::as_str) == Some(FILTER)
            });
        seen = filter;
        filter
    });
    seen || read.is_err()
}

fn gm_last_at(path: &str) -> String {
    let mut at = String::new();
    let _ = backward(path, &mut |rec| {
        if is_gm_message(rec) {
            at = field(rec, "timestamp").chars().take(19).collect();
            return true;
        }
        false
    });
    at
}

fn said_since_gm(path: &str) -> String {
    let mut out = Vec::new();
    let _ = backward(path, &mut |rec| {
        if is_gm_message(rec) {
            return true;
        }
        if field(rec, "type") == "assistant" {
            let blocks = rec.pointer("/message/content").and_then(Value::as_array);
            out.extend(
                blocks
                    .into_iter()
                    .flatten()
                    .filter(|x| field(x, "type") == "text")
                    .map(|x| field(x, "text").to_owned()),
            );
        }
        false
    });
    out.join("\n")
}

/// Each spec's `gm-review.jsonl`, with its feature number, in order.
fn review_files(clone: &Path) -> Vec<(u64, PathBuf)> {
    let dirs = std::fs::read_dir(clone.join("specs"))
        .into_iter()
        .flatten()
        .filter_map(Result::ok);
    let mut out: Vec<(u64, PathBuf)> = dirs
        .filter_map(|d| {
            let name = d.file_name().to_string_lossy().into_owned();
            let number = name.split('-').next()?.parse().ok()?;
            let file = d.path().join("gm-review.jsonl");
            file.is_file().then_some((number, file))
        })
        .collect();
    out.sort();
    out
}

/// Every open question `escalation-check` kept, as (`NNN#row`, its row).
fn kept_rows(clone: &Path) -> Vec<(String, Value)> {
    let mut out = Vec::new();
    for (number, file) in review_files(clone) {
        let text = std::fs::read_to_string(file).unwrap_or_default();
        for (i, line) in text.lines().enumerate() {
            let Ok(row) = serde_json::from_str::<Value>(line) else {
                continue;
            };
            if field(&row, "kind") == "question"
                && field(&row, "status") == "kept"
                && row.get("reviewed").is_none()
            {
                out.push((format!("{number}#{i}"), row));
            }
        }
    }
    out
}

/// The kept questions since the GM's last message that the final message, or anything said since his last, does not name.
pub(crate) fn unnamed(clone: &Path, input: &Value) -> Vec<String> {
    let path = field(input, "transcript_path");
    let since = gm_last_at(path);
    if since.is_empty() {
        return Vec::new();
    }
    let said = format!(
        "{}\n{}",
        field(input, "last_assistant_message"),
        said_since_gm(path)
    );
    kept_rows(clone)
        .into_iter()
        .filter(|(id, row)| {
            let kept: String = field(row, "kept").chars().take(19).collect();
            kept >= since && !said.contains(id.as_str())
        })
        .map(|(id, row)| format!("{id}: {}", field(&row, "question")))
        .collect()
}

/// `ask<TAB>line` or `offer<TAB>line` when the turn owes the filter, or None.
pub(crate) fn judge_ask(input: &Value, clone: &Path) -> Option<(&'static str, String)> {
    let (asks, offers) = classify(field(input, "last_assistant_message"));
    let cwd_given = field(input, "cwd");
    let kept: BTreeSet<String> = kept_rows(if cwd_given.is_empty() {
        clone
    } else {
        Path::new(cwd_given)
    })
    .into_iter()
    .map(|(id, _)| id)
    .collect();
    let asks: Vec<String> = asks
        .into_iter()
        .filter(|a| !kept.iter().any(|k| a.contains(k.as_str())))
        .collect();
    if (asks.is_empty() && offers.is_empty()) || filtered_since_gm(field(input, "transcript_path"))
    {
        return None;
    }
    asks.into_iter()
        .next()
        .map(|a| ("ask", a))
        .or_else(|| offers.into_iter().next().map(|o| ("offer", o)))
}

fn state_path(clone: &Path) -> PathBuf {
    clone.join(".git/escalation-state.json")
}

fn read_state(clone: &Path) -> Map<String, Value> {
    std::fs::read_to_string(state_path(clone))
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok())
        .unwrap_or_default()
}

fn get(state: &Map<String, Value>, key: &str) -> String {
    state
        .get(key)
        .and_then(Value::as_str)
        .unwrap_or("")
        .to_owned()
}

fn write_fields(clone: &Path, fields: &[(&str, String)]) {
    let mut state = read_state(clone);
    for (k, v) in fields {
        state.insert((*k).to_owned(), Value::String(v.clone()));
    }
    let path = state_path(clone);
    let tmp = path.with_extension("json.tmp");
    if std::fs::write(&tmp, Value::Object(state).to_string()).is_ok() {
        let _ = std::fs::rename(tmp, path);
    }
}

fn now_stamp() -> String {
    let secs = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (y, mo, d, h, mi, s) = civil(secs);
    format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z")
}

fn reviews_dir(ctx: &Ctx) -> String {
    ctx.tree
        .join("scripts/reviews")
        .to_string_lossy()
        .into_owned()
}

fn ledger_path(clone: &Path) -> String {
    clone
        .join("dev/review-ledger.md")
        .to_string_lossy()
        .into_owned()
}

fn ledger_count(clone: &Path, ctx: &Ctx) -> String {
    let said = ask(
        clone,
        ctx.python,
        &["-c", ctx.count_code, &reviews_dir(ctx), &ledger_path(clone)],
        "",
    );
    if said.ok() {
        said.out.trim().to_owned()
    } else {
        "0".to_owned()
    }
}

fn all_disposed(clone: &Path, agent: &str, rows: &str, ctx: &Ctx) -> bool {
    ask(
        clone,
        ctx.python,
        &[
            "-c",
            ctx.disposed_code,
            &reviews_dir(ctx),
            &ledger_path(clone),
            agent,
            rows,
        ],
        "",
    )
    .ok()
}

fn arm(clone: &Path, agent: &str, ctx: &Ctx) {
    write_fields(
        clone,
        &[
            ("ledger_rows", ledger_count(clone, ctx)),
            ("armed_by", agent.to_owned()),
            ("armed_at", now_stamp()),
            ("told", String::new()),
        ],
    );
}

fn disarm(clone: &Path) {
    write_fields(
        clone,
        &[("armed_by", String::new()), ("told", String::new())],
    );
}

fn top_of(here: &Path) -> Option<PathBuf> {
    here.ancestors()
        .find(|a| a.join(".git").exists())
        .map(Path::to_path_buf)
}

fn message_key(input: &Value) -> String {
    sha1::hex(field(input, "last_assistant_message").as_bytes())
}

fn pretool(event: &Event, session: &Session, clone: &Path, ctx: &Ctx) -> Vec<Answer> {
    if event.tool() != "Agent" {
        return Vec::new();
    }
    let null = Value::Null;
    let input = event.input.get("tool_input").unwrap_or(&null);
    let (kind, prompt) = (field(input, "subagent_type"), field(input, "prompt"));
    let fire =
        |what: &str, rule: &str| log::fire("escalation", what, kind, rule, &event.input, session);
    if kind == FILTER {
        disarm(clone);
        fire("permitted", "filter-ran");
        return Vec::new();
    }
    if !REVIEW_AGENTS.contains(&kind) {
        return Vec::new();
    }
    if prompt.contains("ESCALATION_OK") {
        fire("escaped", "escalation-ok");
        disarm(clone);
        return Vec::new();
    }
    arm(clone, kind, ctx);
    fire("armed", "review-dispatched");
    vec![Answer::Notice(TOLD_AT_DISPATCH.to_owned())]
}

fn refuse_stop(event: &Event, session: &Session, rule: &str, text: String) -> Vec<Answer> {
    log::fire("escalation", "blocked", "stop", rule, &event.input, session);
    vec![Answer::Refuse(text)]
}

/// A question with no review behind it is filtered too, refused once per message.
fn ask_unfiltered(event: &Event, session: &Session, clone: &Path) -> Vec<Answer> {
    let Some((what, line)) = judge_ask(&event.input, clone) else {
        return Vec::new();
    };
    let key = message_key(&event.input);
    if get(&read_state(clone), "asked_told") == key {
        return Vec::new();
    }
    write_fields(clone, &[("asked_told", key)]);
    if what == "offer" {
        return refuse_stop(event, session, "offer-unfiltered", format!("OFFER UNFILTERED: your final message offers a decision back to the GM and no escalation-check has read it:\n  {line}\nAn offer is fine, and is not a question, but only for a decision that might otherwise have been floated as one.\nDispatch `escalation-check` with the draft as its prompt: it keeps the significant offers and cuts the routine."));
    }
    refuse_stop(event, session, "question-unfiltered", format!("QUESTION UNFILTERED: your final message puts something to the GM and no escalation-check has read it:\n  {line}\nDispatch `escalation-check` with the draft as its prompt and send what it keeps. A question the record or the\nresearch answers is not his (root CLAUDE.md, \"Research\"); his are taste and genuine forks."))
}

fn stop(event: &Event, session: &Session, clone: &Path, ctx: &Ctx) -> Vec<Answer> {
    let missing = unnamed(clone, &event.input);
    if !missing.is_empty() {
        let key = message_key(&event.input);
        if get(&read_state(clone), "kept_told") != key {
            write_fields(clone, &[("kept_told", key)]);
            let listed: Vec<String> = missing.iter().map(|m| format!("  {m}")).collect();
            return refuse_stop(event, session, "kept-unnamed", format!("QUESTION KEPT, NOT NAMED: escalation-check kept these for the GM this turn, and your final message does not name them:\n{}\nPut each to him in the final message by its id (\"<feature>#<row>\", as listed above) with the question - a kept question is his decision now.", listed.join("\n")));
        }
    }
    let state = read_state(clone);
    let armed = get(&state, "armed_by");
    if armed.is_empty() {
        return ask_unfiltered(event, session, clone);
    }
    if all_disposed(clone, &armed, &get(&state, "ledger_rows"), ctx) {
        disarm(clone);
        log::fire(
            "escalation",
            "permitted",
            &armed,
            "findings-disposed",
            &event.input,
            session,
        );
        return Vec::new();
    }
    let key = get(&state, "armed_at");
    if get(&state, "told") == key {
        return Vec::new();
    }
    write_fields(clone, &[("told", key)]);
    refuse_stop(event, session, "findings-unfiltered", format!("FINDINGS UNFILTERED: {armed} returned and no escalation-check has read what you are about to tell the GM.\nDispatch `escalation-check` with your draft as the prompt - it cuts the items that name no norm,\nthe ones the record already answers, and your own process narrative (\"a bug, then I fixed it\").\nRelaying nothing from this review? Write its ledger row with every finding disposed (fixed, verified, accepted,\nfiled as a row - feature 375), or re-dispatch with ESCALATION_OK=\"<reason>\"."))
}

pub(crate) fn judge(event: &Event, session: &Session, here: &Path, ctx: &Ctx) -> Vec<Answer> {
    let Some(clone) = top_of(here) else {
        return Vec::new();
    };
    if event.name == "Stop" {
        stop(event, session, &clone, ctx)
    } else {
        pretool(event, session, &clone, ctx)
    }
}

fn context(here: &Path) -> Ctx<'static> {
    let tree = std::env::var("L7R_GUARD_TREE").map_or_else(|_| here.to_path_buf(), PathBuf::from);
    Ctx {
        tree,
        python: "python3",
        count_code: COUNT_CODE,
        disposed_code: DISPOSED_CODE,
    }
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    judge(event, session, &here, &context(&here))
}

/// The guard's entries that are no hook event: `state`, and the fixture-only `arm` and `disarm` seams.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let here = std::env::current_dir().unwrap_or_default();
    run_cli(args, &here)
}

fn run_cli(args: &[String], here: &Path) -> Reply {
    let say = |stdout: String, stderr: String, code: i32| Reply {
        stdout,
        stderr,
        code,
    };
    let arg = |i: usize| args.get(i).map_or("", String::as_str);
    match arg(0) {
        "state" => {
            let at = if arg(1).is_empty() {
                here
            } else {
                Path::new(arg(1))
            };
            let clone = top_of(at);
            let state = clone.as_deref().map(read_state).unwrap_or_default();
            let shown = clone.map_or("<none>".to_owned(), |c| c.display().to_string());
            say(
                format!(
                    "clone     {shown}\narmed by  {}\narmed at  {}\ntold      {}",
                    get(&state, "armed_by"),
                    get(&state, "armed_at"),
                    get(&state, "told")
                ),
                String::new(),
                0,
            )
        }
        "arm" | "disarm" => {
            let path = arg(1);
            if !(path.contains("/test-") || path.contains("/tmp.") || path.starts_with("/tmp/")) {
                return say(
                    String::new(),
                    format!(
                        "escalation-hooks: {} is a test seam and takes a fixture path",
                        arg(0)
                    ),
                    2,
                );
            }
            if arg(0) == "arm" {
                let agent = if arg(2).is_empty() {
                    "settlement-review"
                } else {
                    arg(2)
                };
                arm(Path::new(path), agent, &context(here));
            } else {
                disarm(Path::new(path));
            }
            say(String::new(), String::new(), 0)
        }
        _ => say(String::new(), String::new(), 0),
    }
}

#[cfg(test)]
mod tests;
