//! `escalation-hooks` (the GM 2026-09-12; features 375, 429, 432; ported from the shell of the same name and `lib/hm_gm_question.py`, feature 449 T044): FINDINGS DO NOT REACH THE GM UNTIL AN
//! INDEPENDENT CHECK HAS FILTERED THEM. A review agent's dispatch arms a requirement and an `escalation-check` dispatch disarms it; the turn may not close between (once per armed review, never a loop).
//! A question or offer in the final message with no review behind it owes the filter too (feature 429), and a question kept for the GM is named the turn it is kept (feature 432). `ESCALATION_OK` with
//! a reason in the dispatch prompt is the escape.
//!
//! THE SESSION'S OWN REVIEWS, ONCE EACH, AFTER THEY RETURN (451 T183; the GM 2026-11-23, request.md "Stop hooks that keep the session
//! busy"): a sub-agent's dispatch (its payload's `agent_id`) neither arms nor disarms - a builder's own building-review is the builder's
//! to dispose, and armed the session's turn three times on 2026-11-23 with findings it never relays; a review the session dispatched
//! is `out` until its `SubagentStop` (an agent the session dispatched, `spawnDepth` 1, of the armed type), and a Stop while it is out
//! passes, since its return wakes the session; then the turn is refused once for it.

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
use crate::shared::ledger;
use crate::shared::log::{self, civil};
use crate::shared::session::Session;
use crate::shared::sha1;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "escalation-hooks",
    events: &["PreToolUse", "SubagentStop", "Stop"],
    matcher: "Agent",
    decide,
};

/// The agents whose findings reach the GM: a short, stated roster, so a new reviewer is a deliberate addition.
const REVIEW_AGENTS: [&str; 3] = ["settlement-review", "building-review", "size-audit"];
const FILTER: &str = "escalation-check";
/// CONVENTION: how much of a transcript is read at a time from its end, as `hm_gm_question.py` read it.
const CHUNK: u64 = 1 << 20;

const TOLD_AT_DISPATCH: &str = "A review is running, so its findings will need the escalation-check filter before any of them reach the GM: dispatch `escalation-check` with your DRAFT writeup as the prompt, and it returns keep/cut/rewrite per item with the norms it could not verify. The GM asked for this after three findings reached them that no project norm supported (2026-09-12). If you will relay nothing, say so with ESCALATION_OK=\"<reason>\".";

fn re(pattern: &str) -> Regex {
    crate::shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static FENCE: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)```.*?```"));
static CODE: LazyLock<Regex> = LazyLock::new(|| re(r"`[^`\n]*`"));
static QUOTED: LazyLock<Regex> =
    LazyLock::new(|| re("\"[^\"\\n]*\"|\u{201c}[^\u{201d}\\n]*\u{201d}"));
/// An ask in a question's own words. `which` only as the interrogative (451 T235): `which of them give wrong answers`, `which would
/// mean` and `which one clone holds` were 18 of the 30 statements on the corpus of 2026-10-26..11-25's firings, and no true ask.
static ASK: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)\b(should I|shall I|do you want|would you (like|prefer|rather)|want me to|which (one |of (these|those|them|the two) )?(do you|would you|should I|shall I)|or should (I|we)|do you agree|is that (ok|okay|right|what you)|can you confirm|let me know (whether|which)|say (go|the word|yes)|approve or decline)\b",
    )
});
/// A decision STATED to be the GM's: an ask, unless its clause says no such thing waits (`NEGATED`) or it names a measure (`MEASURED`,
/// `NAMED`) - 451 T235: "Nothing is waiting on you.", "442 minutes of waiting on you", "**Waiting on you** is still reported".
static STATED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)\b(your call|for you to (decide|approve|choose|pick|confirm|rule)|ask (of )?you|needs your (words?|approval|decision|ruling|go-ahead|call|answer)|waiting (on|for) (you|your)|yours to (decide|call|choose))\b",
    )
});
/// The text before a stated ask, when its clause negates it: a `nothing`-like subject, or a `not` within two words of it, with no
/// exceptive between (`This can't land without your call.`, `Nothing is left but your call.` stay asks; spec-fidelity, 2026-11-25).
static NEGATED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)(\b(nothing|none|nobody|neither|no one)\b((?!\b(but|except|without|until|unless|besides|than)\b)[^.;:!?,])*|\b(not|never|\w+n['\u{2019}]t)\s+((?!(but|except|without|until|unless|besides|than)\b)\w+\s+){0,2})$",
    )
});
/// The text after a negated stated ask that excepts it back in its clause (`Nothing else needs your decision except the budget.`); past
/// a comma it is a new clause (`Nothing is waiting on you, but the page session is still running.` stays a statement).
static EXCEPTED: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?i)^[^.;:!?,]*\b(but|except|besides|other than|apart from)\b"));
static MEASURED: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)\b(of|spent)\s+$"));
/// `Waiting on you` opening its sentence as a measure's name: the subject of `is`/`was` (`**Waiting on you** is still reported`), or a
/// table cell with no `:` in it (`| Waiting for you to answer | 0.5 |`). With a colon (`**Waiting on you:** the command`) it is a label,
/// and with neither (`Waiting on your go-ahead to land it.`) an ask.
static SENTENCE_START: LazyLock<Regex> = LazyLock::new(|| re(r"(^|[.!?]\s+)[\s*_|#>\d.-]*$"));
static NAME_OF: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)^[*_]*\s+(is|was|were)\b"));
static CELL: LazyLock<Regex> = LazyLock::new(|| re(r"\|\s*$"));
static LABEL: LazyLock<Regex> = LazyLock::new(|| re(r"^[^.|]*:"));
/// `what's waiting on you` as one item of a list of contents (451 T272: `a morning handoff file in the repo: what landed, what's open,
/// what was measured, what's waiting on you.`, a table row refused three times on 2026-11-25) names a kind of content, no decision:
/// the `what` clause follows a list's `,` `;` `:` or `and`/`or`, and its own clause ends there or goes on to a sibling `what`. Naming
/// the thing that waits is still an ask (`what's waiting on you: the budget`, `what's waiting on you is the split`, `what's waiting
/// on your budget answer`, `what's waiting on you (the budget)`), and so is the clause with no list before it (`Here is what's
/// waiting on you.`).
static LISTED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)([,;:]\s*((and|or)\s+)?|\b(and|or)\s+)what(['\u{2019}]s|\s+is|\s+was|\s+were)\s+(still\s+)?$",
    )
});
static LIST_GOES_ON: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?i)^[*_]*\s*([.|]|$|,?\s*((and|or)\s+)?what\b)"));
/// A FIGURE of the time spent waiting on the GM (451 T299: `485 minutes of blocking were waiting on you, 27% of the window's blocking.`,
/// a task time breakdown's line of 2026-11-26) is a measurement: a count of minutes, hours or a share is the subject of `was`/`were`
/// before it (never `is`/`are`: `Two hours of review are waiting on you.` is work put to him), and its clause ends after it or goes on to another figure. A count of things that wait (`3 questions were waiting on
/// you`), a duration something has waited (`has been 40 minutes waiting on you`) and the thing that waits named after it (`: the
/// budget's words`, `, the budget answer`) are still asks.
static FIGURE: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)\b\d[\d.,]*\s*(%|(percent|minutes?|mins?|hours?|hrs?|seconds?|days?)\b)(\s+of\s+[^.;:!?,]*)?\s+(was|were)\s+$",
    )
});
static FIGURE_ENDS: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?i)^[*_]*\s*([.;|)]|$|,\s+(about\s+)?\d)"));
/// `waiting on you` as a category of a breakdown set apart from the others (451 T299: `Blocking minutes, with waiting on you kept
/// separate:`, 2026-11-26): `with` before it and the setting apart after it.
static WITH: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)\bwith\s+$"));
static SET_APART: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)^\s+(kept|counted|reported|shown|listed|left|held)\s+(separate(ly)?|apart|aside|out)\b",
    )
});
/// A report of an ask's own WORDING (451 T282: `"For you to confirm" does ask you for a confirmation, so the hook was right`,
/// 2026-11-26): a quoted or backticked phrase is the subject of `does`/`did ask you`. Read before the spans are blanked, since the span
/// is what tells it from the session's own `I do ask you`.
static DESCRIBED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        "(?i)(`[^`\\n]*`|\"[^\"\\n]*\"|\u{201c}[^\u{201d}\\n]*\u{201d})\\s+(does|did)\\s+ask\\s+(of\\s+)?you\\b",
    )
});
/// A check described by the question it asks (451 T299: `It asks: is a pool tree free, and does the queue hold a task ...?`,
/// 2026-11-26): the line's last sentence runs from `asks:` / `asks whether` / `asks if` to its `?` and names no `you` or `your`. A
/// reported question that is put to him (`The review asks: are the wider banks acceptable to you?`) and a question of the session's
/// own before or after it (`What do you make of the check? It asks: is a tree free?`, `... asks whether a tree is free. Can I hand it
/// over?`) are still asks: the line's one `?` is the reported question's.
static REPORTED: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?i)^[^?]*\basks(:|\s+(whether|if)\b)((?!\b(you|your)\b)[^.!?])*\?$"));
/// A CHECKLIST'S OWN QUESTIONS, listed (451 T299: `3. What do you expect to save?` under `It has six questions that a performance
/// change answers in its plan:`, 2026-11-26): an item of a list of two or more whose every item is a question, under a lead-in ending
/// `:` that names a checklist, or questions something `has`, `asks`, `holds`, `lists`, `poses`, `carries` or `answers`, and names
/// neither the GM nor the session (`OWN`). Never every list: `Two questions for you:`, `Open questions:` and `I have two questions:`
/// put their items to him, and an item in a question's own words (`ASK`, `STATED`) fires wherever it stands.
static ITEM: LazyLock<Regex> = LazyLock::new(|| re(r"^(\d+[.)]|[-*])\s+\S"));
static CHECKLIST: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)\b(checklist\b|(has|asks|holds|lists|poses|carries|answers)\b[^.?!]*\bquestions\b)[^.?!]*:$",
    )
});
static OWN: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)\b(you|your|I|my|me|we|our)\b"));
static OFFER: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)\b(if you('d| would)? (want|like|prefer|rather)|if you agree|let me know if|happy to|say so and I'll|easy to (revert|reverse|undo)|I can (also |easily )?(revert|reverse|undo|switch|change|restore|raise|add|drop|re-?run|put (it|them) back))\b",
    )
});
/// `Say if ...` opening a sentence (451 T235); `I can't say if it helps` is none.
static SAY_IF: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)(^|[.!?:]\s+)[\s*_-]*say if\b"));
static ADDRESSED: LazyLock<Regex> = LazyLock::new(|| re(r"\b(you|your|I)\b"));

/// Does a stated decision in `s` put something to the GM?
fn stated_ask(s: &str) -> bool {
    STATED.find_iter(s).map_while(Result::ok).any(|m| {
        let (before, after) = (&s[..m.start()], &s[m.end()..]);
        let words = m.as_str().to_lowercase();
        let named = words.starts_with("waiting")
            && matches_any(&SENTENCE_START, before)
            && (matches_any(&NAME_OF, after)
                || (matches_any(&CELL, before) && !matches_any(&LABEL, after)));
        let you = words.starts_with("waiting") && words.ends_with("you");
        let listed = you && matches_any(&LISTED, before) && matches_any(&LIST_GOES_ON, after);
        let figure = you && matches_any(&FIGURE, before) && matches_any(&FIGURE_ENDS, after);
        let apart = you && matches_any(&WITH, before) && matches_any(&SET_APART, after);
        let negated = matches_any(&NEGATED, before) && !matches_any(&EXCEPTED, after);
        !(named || listed || figure || apart || negated || matches_any(&MEASURED, before))
    })
}

fn matches_any(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

fn blank(pattern: &Regex, text: &str) -> String {
    let (mut out, mut from) = (String::new(), 0);
    for m in pattern.find_iter(text).map_while(Result::ok) {
        out.push_str(&text[from..m.start()]);
        from = m.end();
    }
    out + &text[from..]
}

fn short(line: &str) -> String {
    line.chars().take(200).collect()
}

/// Is line `at` one of a checklist's own questions (`CHECKLIST`)?
fn checklist_item(lines: &[String], at: usize) -> bool {
    let item = |l: &String| matches_any(&ITEM, l);
    let Some(first) = (0..=at).rev().take_while(|i| item(&lines[*i])).last() else {
        return false;
    };
    let block: Vec<&String> = lines[first..].iter().take_while(|l| item(l)).collect();
    let lead = lines[..first].iter().rev().find(|l| !l.is_empty());
    block.len() > 1
        && block.iter().all(|l| l.ends_with('?'))
        && lead.is_some_and(|l| matches_any(&CHECKLIST, l) && !matches_any(&OWN, l))
}

/// (the lines that ASK the reader, the lines that only OFFER): an ask wins over an offer on the same line.
pub(crate) fn classify(text: &str) -> (Vec<String>, Vec<String>) {
    let (mut asks, mut offers) = (Vec::new(), Vec::new());
    let body = blank(&FENCE, text);
    let lines: Vec<String> = lines_kept(&body)
        .into_iter()
        .map(|raw| blank(&QUOTED, &blank(&CODE, &blank(&DESCRIBED, raw.trim()))))
        .collect();
    for (at, s) in lines.iter().enumerate() {
        if s.starts_with('>') {
            continue;
        }
        let offer = matches_any(&OFFER, s) || matches_any(&SAY_IF, s);
        let question = !offer
            && s.ends_with('?')
            && matches_any(&ADDRESSED, s)
            && !matches_any(&REPORTED, s)
            && !checklist_item(&lines, at);
        if matches_any(&ASK, s) || stated_ask(s) || question {
            asks.push(short(s));
        } else if offer {
            offers.push(short(s));
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
    // the session's, so a linked worktree of the clone keeps it in the common git dir (451 T441)
    crate::guards::event_log_hooks::common_git_dir(clone).join("escalation-state.json")
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

/// The clone's review ledger, read as `open(path).read()` reads it; none where it is missing or not UTF-8 (the Python's raise).
fn ledger_text(clone: &Path) -> Option<String> {
    std::fs::read_to_string(clone.join("dev/review-ledger.md")).ok()
}

/// How many measured rows the ledger holds when a review is dispatched; "0" where it cannot be read. The lint is `shared::ledger`, in
/// process since feature 449 T83 (`ask:449-T83-scope`), where it was `ledger_lint.py` by path (T044 decision (b)).
fn ledger_count(clone: &Path) -> String {
    ledger_text(clone).map_or_else(
        || "0".to_owned(),
        |t| ledger::measured_rows(&t).len().to_string(),
    )
}

/// Whether the review's own rows written since it was dispatched dispose of every finding.
fn all_disposed(clone: &Path, agent: &str, rows: &str) -> bool {
    ledger_text(clone).is_some_and(|t| ledger::disposed_since(&t, agent, rows))
}

fn arm(clone: &Path, agent: &str) {
    write_fields(
        clone,
        &[
            ("ledger_rows", ledger_count(clone)),
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

/// A review the session dispatched has returned: no longer `out` (451 T183).
fn returned(event: &Event, clone: &Path) {
    let input = &event.input;
    let state = read_state(clone);
    let (armed, id) = (get(&state, "armed_by"), field(input, "agent_id"));
    if armed.is_empty() || field(input, "agent_type") != armed || get(&state, "out").is_empty() {
        return;
    }
    let dir = match field(input, "agent_transcript_path") {
        "" => Path::new(field(input, "transcript_path"))
            .with_extension("")
            .join("subagents"),
        own => Path::new(own)
            .parent()
            .map(Path::to_path_buf)
            .unwrap_or_default(),
    };
    if crate::shared::guards::set_down_hooks::session_dispatched(&dir, id) {
        write_fields(clone, &[("out", String::new())]);
    }
}

fn pretool(event: &Event, session: &Session, clone: &Path) -> Vec<Answer> {
    // a sub-agent's own dispatch is its own to filter (451 T183)
    if event.tool() != "Agent" || !field(&event.input, "agent_id").is_empty() {
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
    arm(clone, kind);
    let at = get(&read_state(clone), "armed_at");
    write_fields(clone, &[("out", at)]);
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
        return refuse_stop(event, session, "offer-unfiltered", format!("OFFER UNFILTERED: your final message offers a decision back to the GM and no escalation-check has read it:\n  {line}\nAn offer is fine, and is not a question, but only for a decision that might otherwise have been floated as one.\nDispatch `escalation-check` with the draft as its prompt: it keeps the significant offers and cuts the routine.\nIf the line offers him nothing, go on and say nothing of this to him."));
    }
    refuse_stop(event, session, "question-unfiltered", format!("QUESTION UNFILTERED: your final message puts something to the GM and no escalation-check has read it:\n  {line}\nDispatch `escalation-check` with the draft as its prompt and send what it keeps. A question the record or the\nresearch answers is not his (root CLAUDE.md, \"Research\"); his are taste and genuine forks.\nIf the line puts nothing to him, go on and say nothing of this to him."))
}

fn stop(event: &Event, session: &Session, clone: &Path) -> Vec<Answer> {
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
    if all_disposed(clone, &armed, &get(&state, "ledger_rows")) {
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
    // still out: its return wakes the session, and the turn that relays it is the one refused (451 T183)
    if get(&state, "told") == key || get(&state, "out") == key {
        return Vec::new();
    }
    write_fields(clone, &[("told", key)]);
    refuse_stop(event, session, "findings-unfiltered", format!("FINDINGS UNFILTERED: {armed} returned and no escalation-check has read what you are about to tell the GM.\nDispatch `escalation-check` with your draft as the prompt - it cuts the items that name no norm,\nthe ones the record already answers, and your own process narrative (\"a bug, then I fixed it\").\nRelaying nothing from this review? Write its ledger row with every finding disposed (fixed, verified, accepted,\nfiled as a row - feature 375), or re-dispatch with ESCALATION_OK=\"<reason>\"."))
}

pub(crate) fn judge(event: &Event, session: &Session, here: &Path) -> Vec<Answer> {
    let Some(clone) = top_of(here) else {
        return Vec::new();
    };
    if event.name == "Stop" {
        stop(event, session, &clone)
    } else if event.name == "SubagentStop" {
        returned(event, &clone);
        Vec::new()
    } else {
        pretool(event, session, &clone)
    }
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    judge(event, session, &here)
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
                arm(Path::new(path), agent);
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
