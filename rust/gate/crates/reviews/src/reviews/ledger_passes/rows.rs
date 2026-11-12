//! The rows a pass owes: the one to add by hand (`row_for`), the one a session's end writes from the agent's own reply (`filled_row`),
//! and a plan review's, which records itself (`plan_review_rows`, feature 385 T72).

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::guards::event_log_hooks::verdict_of;
use l7r_guard::shared::checks::reply::{py_lines, reply_of};
use l7r_guard::shared::ledger::cost::transcript;
use l7r_guard::shared::py_text::{strip, SPACE_CLASS};
use serde_json::Value;

use super::{field, required, row_of, text, Pass};
use crate::record::bundle::head;

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static BUNDLE: LazyLock<Regex> =
    LazyLock::new(|| re(&format!(r"/tmp/l7r-check/([^/{SPACE_CLASS}]+)/")));
/// A PLAN REVIEW RECORDS ITSELF (feature 385 T72, plan D92): its agent runs `make plan-verdict`, whose line its reply quotes
const PLAN_REVIEW: &str = "MODE 4: PLAN REVIEW";
/// ...the target's own line quoted, or the call the agent says it ran (T74's first review wrote "I recorded T74 as BLOCKED ... with
/// `make plan-verdict F=385 ...`" and quoted no line)
static PLAN_RECORDED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"\b(?:CLEAR|BLOCKED|NOT-REVIEWABLE) recorded for\b|make plan-verdict\b[^\n]*\b(?:recorded|stored)\b|\b(?:recorded|stored)\b[^\n]*make plan-verdict\b|make plan-verdict F=\d+",
    )
});
const PLAN_WHERE: &str = "the plan-verdict record (make plan-verdict)";
static PLAN_FEATURE: LazyLock<Regex> = LazyLock::new(|| re(r"feature (\d{3}-[\w-]+)"));
static PLAN_TASK: LazyLock<Regex> = LazyLock::new(|| re(r"\btask (T\d+[a-z]?)\b"));
const CLEAN: [&str; 6] = [
    "clean",
    "PASS",
    "IN-STEP",
    "FAITHFUL",
    "INTRO-OK",
    "NO-INTRO-NEEDED",
];

fn group(pattern: &Regex, text: &str) -> Option<String> {
    pattern
        .captures(text)
        .ok()
        .flatten()
        .and_then(|c| c.get(1))
        .map(|m| m.as_str().to_owned())
}

/// The agent's newest transcript, none for a pass with no agent.
fn transcript_of(p: &Pass, root: &Path) -> Option<std::path::PathBuf> {
    Some(text(p, "agent"))
        .filter(|a| !a.is_empty())
        .and_then(|a| transcript(a, root))
}

/// The row to add: what was measured filled in, the judgment cells left for the session (`?`) (`row_for`). A pass reaching it has
/// its check, wall and tokens (the log's filter and `unanswered` read them first).
#[must_use]
pub fn row_for(p: &Pass) -> String {
    let subject = text(p, "subject");
    let mut cells = vec![
        field(p, "date").unwrap_or("?").to_owned(),
        text(p, "check").to_owned(),
        if subject.is_empty() { "?" } else { subject }.to_owned(),
    ];
    cells.extend(std::iter::repeat_n("?".to_owned(), 5));
    cells.extend([text(p, "wall").to_owned(), text(p, "tokens").to_owned()]);
    row_of(&cells)
}

/// The session directory the pass's agent ran under, "" where it has no transcript (`_session_of`).
#[must_use]
pub fn session_of(p: &Pass, root: &Path) -> String {
    transcript_of(p, root)
        .and_then(|t| {
            t.parent()?
                .parent()?
                .file_name()
                .map(|n| n.to_string_lossy().into_owned())
        })
        .unwrap_or_default()
}

/// The row a headless page session's pass gets at the session's end, from the record alone: its verdict and first line from the
/// agent's own reply, `nothing` where the reply is clean, and the acted-on cell naming where the session recorded what it applied or
/// filed (`filled_row`). Page sessions wrote no ledger rows - 124 passes of 343's and 368's sessions were owed at landing
/// (2026-10-11) - and their own record of each check is the brief's checks file.
///
/// # Errors
///
/// Where the pass has no check, wall or tokens (the Python's `KeyError`).
pub fn filled_row(p: &Pass, place: &str, root: &Path) -> Result<String, String> {
    let reply = transcript_of(p, root)
        .map(|t| reply_of(&t.to_string_lossy(), ""))
        .unwrap_or_default();
    let said = verdict_of(&reply);
    let verdict = if said.is_empty() {
        "see reply".to_owned()
    } else {
        said
    };
    let first = py_lines(&reply)
        .into_iter()
        .find(|ln| {
            let lead = ln.trim_start_matches(l7r_guard::shared::py_text::is_space);
            !strip(ln).is_empty() && !lead.starts_with('#') && !lead.starts_with("```")
        })
        .map_or("", |ln| ln.trim_matches([' ', '-', '*', '#']));
    let first = if first.is_empty() { "-" } else { first };
    let subject = text(p, "subject");
    let place_cell = group(&BUNDLE, subject)
        .unwrap_or_else(|| head(if subject.is_empty() { "?" } else { subject }, 80).to_owned());
    let clean = CLEAN.contains(&verdict.as_str());
    let cells = [
        field(p, "date").unwrap_or("?").to_owned(),
        required(p, "check")?.to_owned(),
        place_cell,
        verdict,
        head(first, 110).to_owned(),
        if clean { "nothing" } else { "judgment" }.to_owned(),
        "-".to_owned(),
        format!("applied or filed as {place} records"),
        required(p, "wall")?.to_owned(),
        required(p, "tokens")?.to_owned(),
    ];
    Ok(row_of(&cells))
}

/// `a == b` of a JSON value read with `.get` and the pass's date: none and null equal, a string its own text.
fn same(value: Option<&Value>, date: Option<&str>) -> bool {
    match (value, date) {
        (None | Some(Value::Null), None) => true,
        (Some(Value::String(s)), Some(d)) => s == d,
        _ => false,
    }
}

/// `x.get(key)` on what the Python called `.get` on: an object's field, none where it lacks one, the raise where it is no object.
fn get<'a>(value: &'a Value, key: &str) -> Result<Option<&'a Value>, String> {
    value
        .as_object()
        .map(|m| m.get(key))
        .ok_or_else(|| format!("AttributeError: {value} has no attribute 'get'"))
}

/// `x or {}`: a falsy value read as an empty object.
fn or_empty(value: Option<&Value>) -> Value {
    value
        .filter(|v| !l7r_guard::shared::checks::falsy(Some(v)))
        .cloned()
        .unwrap_or_else(|| Value::Object(serde_json::Map::new()))
}

/// The pass's feature's `plan-review.json` holds a verdict for its task (or, for a block review, a block) dated the pass's day - the
/// record itself, where the reply's words vary (T78's second review wrote only "I recorded it") (`in_the_record`).
///
/// # Errors
///
/// Where the record's shape made the Python raise (a `.get` on no object).
pub fn in_the_record(p: &Pass, repo: &Path) -> Result<bool, String> {
    let subject = text(p, "subject");
    let Some(feature) = group(&PLAN_FEATURE, subject) else {
        return Ok(false);
    };
    let path = repo.join("specs").join(feature).join("plan-review.json");
    let Some(rec) = std::fs::read_to_string(&path)
        .ok()
        .filter(|_| path.is_file())
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
    else {
        return Ok(false);
    };
    let date = field(p, "date");
    if let Some(task) = group(&PLAN_TASK, subject) {
        let tasks = or_empty(get(&rec, "tasks")?);
        let entry = get(&tasks, &task)?
            .cloned()
            .unwrap_or_else(|| Value::Object(serde_json::Map::new()));
        return Ok(same(get(&entry, "reviewed")?, date));
    }
    let blocks = or_empty(get(&rec, "blocks")?);
    let values = blocks
        .as_object()
        .ok_or_else(|| "AttributeError: blocks have no attribute 'values'".to_owned())?;
    Ok(values
        .values()
        .any(|b| b.as_object().is_some_and(|m| same(m.get("reviewed"), date))))
}

/// The row of each owed plan review whose reply shows `make plan-verdict` recorded it (81 hand-written on 2026-10-18; the plan review
/// asked that a pass that recorded nothing get no row naming a record) (`plan_review_rows`).
///
/// # Errors
///
/// Where `in_the_record` or `filled_row` raises.
pub fn plan_review_rows(owed: &[Pass], root: &Path, repo: &Path) -> Result<Vec<String>, String> {
    let mut out = Vec::new();
    for p in owed {
        if !text(p, "subject").starts_with(PLAN_REVIEW) {
            continue;
        }
        let quoted = transcript_of(p, root).is_some_and(|t| {
            PLAN_RECORDED
                .is_match(&reply_of(&t.to_string_lossy(), ""))
                .unwrap_or(false)
        });
        if quoted || in_the_record(p, repo)? {
            out.push(filled_row(p, PLAN_WHERE, root)?);
        }
    }
    Ok(out)
}

#[cfg(test)]
mod tests;
