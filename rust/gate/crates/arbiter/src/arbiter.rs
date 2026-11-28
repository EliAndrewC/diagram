//! `l7r-gate arbiter`: the round arbiter's rulings and tripwires from the shell and the make targets (feature 449 T86, from `scripts/hooks/lib/hm_arbiter.py`'s `main`, `record_ruling` and `record_batch`), and the verdict
//! reads the review gate asks. `arbiter.jsonl` is appended here alone; a ruling that lifts a hold is `pop_owed` under the same lock `trip` takes, so the guards and this command never race. The checkpoint's close and a unit's content key
//! are the reviews' port, in-process (T89), and so is a ruling's `for_gm` question, `gm_review.question` until feature 449 T91 ported it.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::checks;
use l7r_shared::checks::arbiter as core;
use l7r_shared::env::Rooted;
use l7r_shared::guards::house_style_hooks::americanize_json;
use l7r_shared::log::civil;
use l7r_shared::pyjson;
use l7r_shared::sha256;
use serde_json::{json, Map, Value};

use crate::Reply;

/// Rulings a round trigger takes, the two closing ones among them.
const RULINGS: [&str; 3] = ["continue", "accept", "process-fault"];
/// The hourly step-back's two rulings (feature 383 FR-010).
const HOUR_RULINGS: [&str; 2] = ["continue", "change-route"];
/// The reviews an ask may be about, its ruling then standing as that review's verdict (feature 409).
const REVIEWS: [&str; 2] = ["spec", "plan"];
const ROUND_ARBITER: &str = "round-arbiter";

fn re(pattern: &str) -> Regex {
    l7r_shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static FAITHFUL_NOT: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)NOT\s+\**FAITHFUL"));
static FAITHFUL_REVIEW: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?i)status|verdict|round|spec-fidelity"));
static HANDS_THE_GM: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)the GM'?s (to decide|call|question|decision)|for the GM to|held for the GM|the GM (must|should) decide|GM'?s choice",
    )
});
static HOUR_TRIGGER: LazyLock<Regex> = LazyLock::new(|| re(r"^hour:([^@]+)@"));
static ASK_SUBJECT: LazyLock<Regex> = LazyLock::new(|| re(r"^[\w.-]+$"));
static ASK_HINT: LazyLock<Regex> = LazyLock::new(|| re(r"^\d+-(spec|plan)-"));
static ASK_WORDS: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?i)spec-fidelity|plan review|spec review"));

/// Why a ruling or a fix is refused: `PermissionError` (declined: only the round arbiter records one) or `ValueError` (refused).
#[derive(Debug)]
pub enum Stop {
    Declined(String),
    Refused(String),
}

impl Stop {
    fn reply(&self, prefix: &str) -> Reply {
        match self {
            Self::Declined(why) => fail(format!("{prefix}: {why}\n"), 2),
            Self::Refused(why) => fail(format!("{prefix}: refused - {why}\n"), 1),
        }
    }
}

fn fail(stderr: String, code: i32) -> Reply {
    Reply {
        stdout: String::new(),
        stderr,
        code,
    }
}

fn ok(stdout: String) -> Reply {
    Reply {
        stdout,
        stderr: String::new(),
        code: 0,
    }
}

fn text<'a>(v: &'a Value, k: &str) -> &'a str {
    v.get(k).and_then(Value::as_str).unwrap_or("")
}

fn py_str(v: Option<&Value>) -> String {
    match v {
        None | Some(Value::Null) => String::new(),
        Some(Value::String(s)) => s.clone(),
        Some(other) => other.to_string(),
    }
}

fn utc_now() -> String {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (y, mo, d, h, mi, s) = civil(secs);
    format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z")
}

fn root_dir() -> PathBuf {
    std::env::current_dir().unwrap_or_default()
}

/// `hm_arbiter.accept_answers`: an accept on a round cap answers that check's units on its subject at today's words.
fn accept_answers(root: &Path, unit: &str, result: &str) -> Result<Vec<String>, Stop> {
    let (check, subject) = unit.split_once('|').unwrap_or((unit, ""));
    let (kind, name) = subject.split_once(':').unwrap_or((subject, ""));
    if !matches!(kind, "modal" | "q") || check.is_empty() || name.is_empty() {
        return Ok(Vec::new());
    }
    let checks_named: &[&str] = if check == "modal-research" {
        &["modal-accuracy", "modal-references", "modal-gaps"]
    } else {
        std::slice::from_ref(&check)
    };
    let mut done = Vec::new();
    for c in checks_named {
        done.extend(answer_units(root, c, result, kind, name)?);
    }
    Ok(done)
}

/// `record_owed.answer` on `kind=name` or `q=name`, the Rust port called directly.
#[cfg(not(test))]
fn answer_units(
    root: &Path,
    check: &str,
    result: &str,
    kind: &str,
    name: &str,
) -> Result<Vec<String>, Stop> {
    use crate::record::owed::{answer, Named};
    let named = Named {
        q: if kind == "modal" { "" } else { name },
        notes: "",
        key: "",
        kind: if kind == "modal" { name } else { "" },
    };
    answer(root, check, result, "", &named, "")
        .map_err(|why| Stop::Refused(format!("record-owed said: {why}")))
}

/// The test double for `answer_units`: `.fake-answer` in the root says what `record_owed.answer` would (`ok`, `none`, `fail`).
#[cfg(test)]
fn answer_units(
    root: &Path,
    check: &str,
    _result: &str,
    _kind: &str,
    _name: &str,
) -> Result<Vec<String>, Stop> {
    match std::fs::read_to_string(root.join(".fake-answer"))
        .unwrap_or_default()
        .trim()
    {
        "ok" => Ok(vec![format!("u:{check}")]),
        "fail" => Err(Stop::Refused("record-owed said: no engine here".to_owned())),
        _ => Ok(Vec::new()),
    }
}

/// A ruling's `for_gm`, written owed escalation-check in the feature's `gm-review.jsonl` with the ruling's own time: the GM-review queue's
/// one writer, called in process (feature 449 T91, `ask:449-T82-claims`; the Python's `gm_review.question` by `python3 -c` before). Its
/// refusal leaves the ruling recorded and the question not, as the Python's raise did.
fn gm_question(d: &Path, question: &str, source: &str, when: &str) -> Result<(), Stop> {
    crate::reviews::gm_review::question(d, question, source, Some(when))
        .map(|_| ())
        .map_err(|why| Stop::Refused(format!("gm-review said: {why}")))
}

/// sha256 of what a review of feature `d`'s spec judged: spec.md above its Review history, title and body.
#[must_use]
pub fn spec_body_sha(d: &Path) -> String {
    let body = std::fs::read_to_string(d.join("spec.md")).unwrap_or_default();
    let top = body.split("\n## Review history").next().unwrap_or("");
    let (head, rest) = top.split_once("\n## ").unwrap_or((top, ""));
    let sep = if top.contains("\n## ") { "\n## " } else { "" };
    let first = head.split('\n').next().unwrap_or("");
    sha256::hex(format!("{first}{sep}{rest}").as_bytes())
}

/// The arbiter's accept or process-fault that stands for feature `d`'s spec verdict, or "" (`hm_arbiter.spec_ruled`).
#[must_use]
pub fn spec_ruled(d: &Path) -> String {
    let want = format!(
        "round:spec-fidelity|{}#",
        d.file_name()
            .map_or_else(String::new, |n| n.to_string_lossy().into_owned())
    );
    let sha = spec_body_sha(d);
    for line in std::fs::read_to_string(d.join("arbiter.jsonl"))
        .unwrap_or_default()
        .lines()
    {
        let Ok(r) = serde_json::from_str::<Value>(line) else {
            continue;
        };
        let review = text(&r, "trigger").starts_with(&want) || text(&r, "review") == "spec";
        if review
            && matches!(text(&r, "ruling"), "accept" | "process-fault")
            && text(&r, "spec_sha") == sha
        {
            return text(&r, "trigger").to_owned();
        }
    }
    String::new()
}

/// Why feature `d`'s spec carries its fidelity verdict, or "" (`hm_arbiter.spec_verdict`).
#[must_use]
pub fn spec_verdict(d: &Path) -> String {
    let body = std::fs::read_to_string(d.join("spec.md")).unwrap_or_default();
    let line_says = body.lines().any(|ln| {
        ln.contains("FAITHFUL")
            && !FAITHFUL_NOT.is_match(ln).unwrap_or(false)
            && FAITHFUL_REVIEW.is_match(ln).unwrap_or(false)
    });
    if line_says {
        return "FAITHFUL".to_owned();
    }
    spec_ruled(d)
}

fn bare_unit(unit: &str) -> &str {
    unit.split_once('|').map_or(unit, |(_, u)| u)
}

/// The arbiter's accept or process-fault on a round of review unit `unit` standing for its verdict, or "" (`hm_arbiter.unit_ruled`).
#[must_use]
pub fn unit_ruled(d: &Path, unit: &str, content: &str) -> String {
    if content.is_empty() {
        return String::new();
    }
    for line in std::fs::read_to_string(d.join("arbiter.jsonl"))
        .unwrap_or_default()
        .lines()
    {
        let Ok(r) = serde_json::from_str::<Value>(line) else {
            continue;
        };
        if bare_unit(text(&r, "unit")) == bare_unit(unit)
            && text(&r, "trigger").starts_with("round:")
            && matches!(text(&r, "ruling"), "accept" | "process-fault")
            && text(&r, "content_key") == content
        {
            return text(&r, "trigger").to_owned();
        }
    }
    String::new()
}

fn unit_content_key(root: &Path, unit: &str) -> String {
    crate::reviews::prereq::unit_content_key(root, bare_unit(unit))
}

fn row_unit(trig: &Value, trigger: &str) -> String {
    let unit = text(trig, "unit");
    if unit.is_empty() {
        core::unit_of(trigger)
    } else {
        unit.to_owned()
    }
}

/// A tooling fix's `fix_minutes`, checked, or why it fails.
fn fix_measure(ruling: &Value) -> Result<Value, Stop> {
    let how = || {
        Stop::Refused("a `tooling_fix` names `fix_minutes`, the cost it measured this hour (feature 385 T119)".to_owned())
    };
    let minutes = match ruling.get("fix_minutes") {
        Some(Value::Number(n)) => n.as_f64().ok_or_else(how)?,
        Some(Value::String(s)) => s.trim().parse::<f64>().map_err(|_| how())?,
        _ => return Err(how()),
    };
    if minutes < 0.0 {
        return Err(how());
    }
    Ok(json!(minutes))
}

/// `hm_arbiter.rekeys`: the same ruling may be recorded again only to carry the sheet's content key a round row was written without.
fn rekeys(prior: &Value, trigger: &str, ruling: &Value) -> bool {
    trigger.starts_with("round:")
        && !trigger.starts_with("round:spec-fidelity|")
        && text(prior, "content_key").is_empty()
        && prior.get("ruling") == ruling.get("ruling")
}

fn hands_the_gm(body: &str) -> bool {
    HANDS_THE_GM.is_match(body).unwrap_or(false)
}

fn validate_ruling(
    ruling: &Value,
    hour: bool,
    batch: bool,
) -> Result<(String, String, Option<Value>), Stop> {
    let allowed: &[&str] = if hour { &HOUR_RULINGS } else { &RULINGS };
    let word = text(ruling, "ruling");
    if !allowed.contains(&word) || py_str(ruling.get("why")).trim().is_empty() {
        return Err(Stop::Refused(format!(
            "a ruling is one of {} with a `why`",
            tuple(allowed)
        )));
    }
    if hour && word == "change-route" && py_str(ruling.get("what")).trim().is_empty() {
        return Err(Stop::Refused("a `change-route` ruling names in `what` the loop or the unresearched number and the route to take".to_owned()));
    }
    let fix = py_str(ruling.get("tooling_fix")).trim().to_owned();
    let fix_on = if batch {
        py_str(ruling.get("tooling_fix_on"))
    } else {
        String::new()
    };
    if word == "process-fault" && fix.is_empty() && fix_on.is_empty() {
        return Err(Stop::Refused("a `process-fault` ruling names its fault as `tooling_fix` - one sentence: the tool and the change".to_owned()));
    }
    let measure = if fix.is_empty() {
        None
    } else {
        Some(fix_measure(ruling)?)
    };
    Ok((fix, fix_on, measure))
}

fn tuple(words: &[&str]) -> String {
    let items: Vec<String> = words.iter().map(|w| format!("'{w}'")).collect();
    format!("({})", items.join(", "))
}

fn insert_opt(row: &mut Map<String, Value>, key: &str, value: Option<Value>) {
    if let Some(v) = value {
        row.insert(key.to_owned(), v);
    }
}

/// The ruling's row, its keys in the order `arbiter.jsonl` has always carried them.
#[expect(
    clippy::too_many_arguments,
    reason = "the row's parts, the locals of the ruling it records"
)]
fn build_row(
    root: &Path,
    d: &Path,
    trigger: &str,
    trig: &Value,
    ruling: &Value,
    fix: &str,
    fix_on: &str,
    measure: Option<Value>,
    when: &str,
) -> Map<String, Value> {
    let kind = trig
        .get("kind")
        .cloned()
        .unwrap_or_else(|| json!(trigger.split(':').next().unwrap_or("")));
    let mut row = Map::new();
    row.insert("trigger".to_owned(), json!(trigger));
    row.insert("kind".to_owned(), kind);
    row.insert("unit".to_owned(), json!(row_unit(trig, trigger)));
    insert_opt(&mut row, "dispatches", trig.get("dispatches").cloned());
    // a red gate's landing tasks (461 T84), which owe its part B once the owed row is gone
    insert_opt(&mut row, "tasks", trig.get("tasks").cloned());
    if let Some(detail) = trig.get("detail").filter(|v| !checks::falsy(Some(v))) {
        row.insert("asked".to_owned(), detail.clone());
    }
    row.insert(
        "ruling".to_owned(),
        ruling.get("ruling").cloned().unwrap_or(Value::Null),
    );
    row.insert(
        "why".to_owned(),
        ruling.get("why").cloned().unwrap_or(Value::Null),
    );
    row.insert(
        "what".to_owned(),
        ruling.get("what").cloned().unwrap_or_else(|| json!("")),
    );
    row.insert("utc".to_owned(), json!(when));
    if !fix.is_empty() {
        row.insert("tooling_fix".to_owned(), json!(fix));
        row.insert("fix".to_owned(), json!("open"));
        insert_opt(&mut row, "fix_minutes", measure);
    } else if !fix_on.is_empty() {
        row.insert("tooling_fix_on".to_owned(), json!(fix_on));
    }
    let review = text(trig, "review");
    if REVIEWS.contains(&review) || review.starts_with("claims:") {
        row.insert("review".to_owned(), json!(review));
    }
    if trigger.starts_with("round:spec-fidelity|") || review == "spec" {
        row.insert("spec_sha".to_owned(), json!(spec_body_sha(d)));
    }
    if trigger.starts_with("round:") && !trigger.starts_with("round:spec-fidelity|") {
        let ck = unit_content_key(root, &row_unit(trig, trigger));
        if !ck.is_empty() {
            row.insert("content_key".to_owned(), json!(ck));
        }
    }
    row
}

fn append_jsonl(path: &Path, row: &Value) -> Result<(), Stop> {
    use std::io::Write as _;
    let line = pyjson::dumps(row, None, false) + "\n";
    std::fs::OpenOptions::new()
        .append(true)
        .create(true)
        .open(path)
        .and_then(|mut f| f.write_all(line.as_bytes()))
        .map_err(|e| Stop::Refused(e.to_string()))
}

/// `hm_arbiter.record_ruling`: binding, one per trigger.
///
/// # Errors
///
/// A declined or refused ruling.
pub fn record_ruling(
    root: &Rooted,
    trigger: &str,
    ruling: &Value,
    declared: &str,
    now: Option<&str>,
    batch: bool,
) -> Result<Value, Stop> {
    ruling_at(root, trigger, ruling, declared, now, batch).map(|(row, _)| row)
}

/// [`record_ruling`], and the feature it was filed in: its trigger's, resolved once ([`home::resolve`], feature 451 T179), which the
/// plan's accept is applied in.
fn ruling_at(
    root: &Rooted,
    trigger: &str,
    ruling: &Value,
    declared: &str,
    now: Option<&str>,
    batch: bool,
) -> Result<(Value, PathBuf), Stop> {
    if declared != ROUND_ARBITER {
        return Err(Stop::Declined("declined: only the `round-arbiter` subagent records a ruling (AS=round-arbiter) - a declaration, recorded, not a proof".to_owned()));
    }
    let d = home::resolve(root, trigger).map_err(Stop::Refused)?;
    if let Some(prior) = home::ruled_in(&d).get(trigger) {
        if !rekeys(prior, trigger, ruling)
            || unit_content_key(root, &core::unit_of(trigger)).is_empty()
        {
            return Err(Stop::Refused(format!("{trigger} is already ruled - one ruling per trigger, binding; the session neither re-asks nor overrules")));
        }
    }
    let batched = core::batch_triggers_in(root, &[], root.reader());
    let others: Vec<&String> = batched.iter().filter(|t| *t != trigger).collect();
    let with_trigger = core::batch_triggers(root, &[trigger.to_owned()]);
    if !batch && with_trigger.iter().any(|t| t == trigger) && !others.is_empty() {
        return Err(Stop::Refused(format!(
            "{} other round trigger(s) are owed with it - rule them together, ONE ruling: make arbiter-bundle BATCH=1, then make arbiter-ruled BATCH=1 FILE=<its JSON> AS=round-arbiter (FR-017)",
            others.len()
        )));
    }
    if let Some(why) = bundle::unowed_red_gate(root, trigger) {
        return Err(Stop::Refused(why));
    }
    let hour = trigger.starts_with("hour:");
    let (fix, fix_on, measure) = validate_ruling(ruling, hour, batch)?;
    let when = now.map_or_else(utc_now, str::to_owned);
    let trig = core::owed(root)
        .get(trigger)
        .cloned()
        .unwrap_or_else(|| json!({}));
    let mut row = build_row(
        root, &d, trigger, &trig, ruling, &fix, &fix_on, measure, &when,
    );
    let for_gm = py_str(ruling.get("for_gm")).trim().to_owned();
    if !for_gm.is_empty() {
        row.insert("for_gm".to_owned(), json!(for_gm));
    } else if hands_the_gm(&format!(
        "{} {}",
        py_str(row.get("why")),
        py_str(row.get("what"))
    )) {
        return Err(Stop::Refused("this ruling hands the GM a decision in its `why` or `what` - put the question in `for_gm` instead, the one door to him: it is written owed escalation-check and reaches him only if kept (feature 432, FR-003)".to_owned()));
    }
    let _ = std::fs::create_dir_all(&d);
    let value = Value::Object(row);
    append_jsonl(&d.join("arbiter.jsonl"), &value)?;
    if !for_gm.is_empty() {
        gm_question(&d, &for_gm, trigger, &when)?;
    }
    if hour {
        crate::reviews::checkpoint::close_checkpoint(root, trigger);
    }
    if text(&value, "ruling") == "accept" && text(&value, "kind") == "round" {
        accept_answers(
            root,
            text(&value, "unit"),
            &format!("accepted by the round arbiter ({trigger})"),
        )?;
    }
    home::pop_everywhere(root, trigger, &home::name_of(&d)).map_err(Stop::Refused)?;
    Ok((value, d))
}

fn batch_plan(ruling: &Value, triggers: &[String]) -> Result<Vec<(String, Value)>, Stop> {
    let exceptions = ruling
        .get("exceptions")
        .cloned()
        .unwrap_or_else(|| json!({}));
    let exception_of = |t: &str| exceptions.get(t).filter(|v| !v.is_null());
    let mut base = ruling.as_object().cloned().unwrap_or_default();
    for k in ["triggers", "exceptions", "tooling_fix"] {
        base.shift_remove(k);
    }
    let fix = py_str(ruling.get("tooling_fix")).trim().to_owned();
    let under: Vec<&String> = triggers
        .iter()
        .filter(|t| exception_of(t).is_none())
        .collect();
    let free: Vec<&String> = triggers
        .iter()
        .filter(|t| exception_of(t).is_some_and(|e| py_str(e.get("tooling_fix")).trim().is_empty()))
        .collect();
    if !fix.is_empty() && under.is_empty() && free.is_empty() {
        return Err(Stop::Refused("every trigger is an exception with its own `tooling_fix` - where does the batch's fix go? Fold it into one of them, or leave the batch's out".to_owned()));
    }
    let holder = if fix.is_empty() {
        String::new()
    } else {
        under
            .first()
            .or(free.first())
            .map_or_else(String::new, |t| (*t).clone())
    };
    let mut plan = Vec::new();
    for t in triggers {
        let mut one: Map<String, Value> = exception_of(t)
            .and_then(Value::as_object)
            .cloned()
            .unwrap_or_else(|| base.clone());
        if *t == holder {
            one.insert("tooling_fix".to_owned(), json!(fix));
            if let Some(m) = ruling.get("fix_minutes") {
                one.insert("fix_minutes".to_owned(), m.clone());
            }
        } else if !fix.is_empty() && exception_of(t).is_none() {
            one.insert("tooling_fix_on".to_owned(), json!(holder));
        }
        plan.push((t.clone(), Value::Object(one)));
    }
    Ok(plan)
}

/// `hm_arbiter.record_batch`: ONE ruling for a batch of round triggers (FR-017), every row checked before any is written.
///
/// # Errors
///
/// A declined or refused batch.
pub fn record_batch(
    root: &Rooted,
    ruling: &Value,
    declared: &str,
    now: Option<&str>,
) -> Result<Vec<Value>, Stop> {
    batch_at(root, ruling, declared, now).map(|rows| rows.into_iter().map(|(r, _)| r).collect())
}

/// [`record_batch`], each row with the feature it was filed in; a trigger whose feature does not resolve refuses the batch before
/// any row is written (feature 451 T179).
fn batch_at(
    root: &Rooted,
    ruling: &Value,
    declared: &str,
    now: Option<&str>,
) -> Result<Vec<(Value, PathBuf)>, Stop> {
    let triggers: Vec<String> = ruling
        .get("triggers")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .map(|t| py_str(Some(t)))
        .collect();
    if triggers.is_empty() {
        return Err(Stop::Refused(
            "a batch ruling names its `triggers` - every trigger its bundle carried".to_owned(),
        ));
    }
    let mut twice: Vec<&String> = triggers
        .iter()
        .filter(|t| triggers.iter().filter(|x| x == t).count() > 1)
        .collect();
    twice.sort();
    twice.dedup();
    if !twice.is_empty() {
        return Err(Stop::Refused(format!(
            "a trigger is named twice: {}",
            join_refs(&twice)
        )));
    }
    let exceptions = ruling
        .get("exceptions")
        .and_then(Value::as_object)
        .cloned()
        .unwrap_or_default();
    let mut stray: Vec<&String> = exceptions
        .keys()
        .filter(|k| !triggers.contains(k))
        .collect();
    stray.sort();
    if !stray.is_empty() {
        return Err(Stop::Refused(format!(
            "an exception names a trigger the batch does not carry: {}",
            join_refs(&stray)
        )));
    }
    if declared != ROUND_ARBITER {
        return Err(Stop::Declined("declined: only the `round-arbiter` subagent records a ruling (AS=round-arbiter) - a declaration, recorded, not a proof".to_owned()));
    }
    let mut done: Vec<&String> = Vec::new();
    for t in &triggers {
        let d = home::resolve(root, t).map_err(|why| Stop::Refused(format!("{t}: {why}")))?;
        if home::ruled_in(&d).contains_key(t) {
            done.push(t);
        }
    }
    done.sort();
    if !done.is_empty() {
        return Err(Stop::Refused(format!(
            "already ruled: {} - one ruling per trigger, binding",
            join_refs(&done)
        )));
    }
    if let Some(why) = triggers
        .iter()
        .find_map(|t| bundle::unowed_red_gate(root, t))
    {
        return Err(Stop::Refused(why));
    }
    let plan = batch_plan(ruling, &triggers)?;
    for (t, one) in &plan {
        if !RULINGS.contains(&text(one, "ruling")) || py_str(one.get("why")).trim().is_empty() {
            return Err(Stop::Refused(format!(
                "{t}: a ruling is one of {} with a `why`",
                tuple(&RULINGS)
            )));
        }
        if text(one, "ruling") == "process-fault"
            && py_str(one.get("tooling_fix")).trim().is_empty()
            && py_str(one.get("tooling_fix_on")).is_empty()
        {
            return Err(Stop::Refused(format!("{t}: a `process-fault` ruling names its fault as `tooling_fix` (the batch's, or its own)")));
        }
    }
    let mut rows = Vec::new();
    for (t, one) in plan {
        rows.push(ruling_at(root, &t, &one, declared, now, true)?);
    }
    Ok(rows)
}

fn join_refs(v: &[&String]) -> String {
    v.iter().map(|s| s.as_str()).collect::<Vec<_>>().join(", ")
}

pub mod bundle;
mod commands;
mod fixes;
mod home;
pub use crate::reviews::closing::{fix_hold, open_fixes};
use fixes::{fix_home, nit_answers, settle_fix, Landing};

/// A string as Python's `repr` quotes it (`{old!r}` in `nit_answers`): single quotes unless the text has one and no double quote.
fn py_repr(s: &str) -> String {
    let quote = if s.contains('\'') && !s.contains('"') {
        '"'
    } else {
        '\''
    };
    let mut out = String::with_capacity(s.len() + 2);
    out.push(quote);
    for c in s.chars() {
        match c {
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\t' => out.push_str("\\t"),
            '\r' => out.push_str("\\r"),
            c if c == quote => {
                out.push('\\');
                out.push(c);
            }
            c => out.push(c),
        }
    }
    out.push(quote);
    out
}

fn load_ruling(path: &str) -> Result<Value, Stop> {
    let body = std::fs::read_to_string(path).map_err(|e| Stop::Refused(e.to_string()))?;
    let parsed: Value = serde_json::from_str(&body).map_err(|e| Stop::Refused(e.to_string()))?;
    // every string as a JSON record takes it, a straight-quoted word too: arbiter.jsonl is no prose file to the delta check (449 T242)
    Ok(americanize_json(&parsed))
}

/// `l7r-gate arbiter <verb>`: what `make arbiter-*`, `make done`'s first step and the review gate run.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    cli_in(args, &Rooted::process(root_dir()))
}

#[cfg(test)]
use commands::owed_line;
use commands::{ask_cli, fix_cli, nit_cli, ruled_batch_cli, ruled_cli};

fn cli_in(args: &[String], root: &Rooted) -> Reply {
    let verb = args.first().map_or("", String::as_str);
    match (verb, args.len()) {
        ("ruled", 5) if args[3] == "--as" => ruled_cli(root, &args[1], &args[2], &args[4]),
        ("ruled-batch", 4) if args[2] == "--as" => ruled_batch_cli(root, &args[1], &args[3]),
        ("gate-held", 1) => {
            let why = core::refusal(&core::blocking_in(root, "", true, root.reader()), None);
            if why.is_empty() {
                ok(String::new())
            } else {
                fail(format!("make done: refused - {why}\n"), 1)
            }
        }
        ("spec-verdict", 2) => Reply { code: i32::from(spec_verdict(Path::new(&args[1])).is_empty()), stdout: String::new(), stderr: String::new() },
        ("spec-ruled", 2) => Reply { code: i32::from(spec_ruled(Path::new(&args[1])).is_empty()), stdout: String::new(), stderr: String::new() },
        ("unit-ruled", 3) => Reply { code: i32::from(core::feature_dir_in(root, "", root.reader()).is_none_or(|d| unit_ruled(&d, &args[1], &args[2]).is_empty())), stdout: String::new(), stderr: String::new() },
        ("ask", 3 | 4) => ask_cli(root, &args[1..]),
        ("fix", n) if n >= 4 && matches!(args[1].as_str(), "done" | "declined") => fix_cli(root, &args[1..]),
        ("nit", 4) => nit_cli(root, &args[1..]),
        ("bundle", _) => bundle::cli(&args[1..]),
        _ => fail("usage: hm_arbiter.py ruled <trigger> <json> --as round-arbiter | fix done|declined <trigger> <note> [<test>] [--landing <task> --files <paths> [--feature <f>]] | nit <trigger> <old> <new>\n".to_owned(), 2),
    }
}

#[cfg(test)]
mod tests;
