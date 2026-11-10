//! `l7r-gate arbiter`: the round arbiter's rulings and tripwires from the shell and the make targets (feature 449 T86, from `scripts/hooks/lib/hm_arbiter.py`'s `main`, `record_ruling` and `record_batch`), and the verdict
//! reads the review gate asks. `arbiter.jsonl` is appended here alone; a ruling that lifts a hold is `pop_owed` under the same lock `trip` takes, so the guards and this command never race. The modules still Python - `gm_review`,
//! `checkpoint`, `record_owed`, `claims` and `review_prereq` - are asked by path on these rare branches, never on a plain Bash call or Edit (the T065 clause).

use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::guards::house_style_hooks::americanize;
use l7r_guard::shared::checks;
use l7r_guard::shared::checks::arbiter as core;
use l7r_guard::shared::log::civil;
use l7r_guard::shared::pyjson;
use l7r_guard::shared::sha256;
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
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
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

/// `python3 -c code args...`, a module the five named modules call by path until its own port; the stdout, stripped, where it succeeded.
fn py(code: &str, args: &[&str]) -> Option<String> {
    let mut full = vec!["-c", code];
    full.extend_from_slice(args);
    let done = std::process::Command::new("python3")
        .args(&full)
        .output()
        .ok()?;
    done.status
        .success()
        .then(|| String::from_utf8_lossy(&done.stdout).trim().to_owned())
}

const REPO_ANSWER: &str = r"import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1] + '/scripts/record')
import record_owed
root, check, result, kind, name = Path(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]
print(json.dumps(record_owed.answer(root, check, result, kind=name) if kind == 'modal' else record_owed.answer(root, check, result, q=name)))";

const GM_QUESTION: &str = r"import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import gm_review
gm_review.question(Path(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5])";

const CLOSE_CHECKPOINT: &str = r"import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1] + '/scripts/reviews')
import checkpoint
checkpoint.close_checkpoint(Path(sys.argv[2]), sys.argv[3])";

/// The tree the running binary's scripts live in: `L7R_GUARD_TREE` from the wrapper, else the root.
fn tree_of(root: &Path) -> PathBuf {
    std::env::var("L7R_GATE_TREE")
        .or_else(|_| std::env::var("L7R_GUARD_TREE"))
        .map_or_else(|_| root.to_path_buf(), PathBuf::from)
}

fn scripts(root: &Path) -> PathBuf {
    tree_of(root).join("scripts")
}

/// `hm_arbiter.accept_answers`: an accept on a round cap answers that check's units on its subject at today's words.
fn accept_answers(root: &Path, unit: &str, result: &str) -> Vec<String> {
    let (check, subject) = unit.split_once('|').unwrap_or((unit, ""));
    let (kind, name) = subject.split_once(':').unwrap_or((subject, ""));
    if !matches!(kind, "modal" | "q") || check.is_empty() || name.is_empty() {
        return Vec::new();
    }
    let checks_named: &[&str] = if check == "modal-research" {
        &["modal-accuracy", "modal-references", "modal-gaps"]
    } else {
        std::slice::from_ref(&check)
    };
    let tree = tree_of(root);
    let mut done = Vec::new();
    for c in checks_named {
        let said = py(
            REPO_ANSWER,
            &[
                &tree.to_string_lossy(),
                &root.to_string_lossy(),
                c,
                result,
                kind,
                name,
            ],
        );
        if let Some(rows) = said.and_then(|t| serde_json::from_str::<Vec<String>>(&t).ok()) {
            done.extend(rows);
        }
    }
    done
}

fn gm_question(root: &Path, d: &Path, question: &str, source: &str, when: &str) {
    let tree = scripts(root);
    let _ = py(
        GM_QUESTION,
        &[
            &tree.to_string_lossy(),
            &d.to_string_lossy(),
            question,
            source,
            when,
        ],
    );
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
    let script = scripts(root).join("reviews/review_prereq.py");
    let done = std::process::Command::new("python3")
        .arg(&script)
        .args([
            "content-key",
            "--clone",
            &root.to_string_lossy(),
            "--map",
            bare_unit(unit),
        ])
        .output();
    match done {
        Ok(o) if o.status.success() => String::from_utf8_lossy(&o.stdout).trim().to_owned(),
        _ => String::new(),
    }
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
    root: &Path,
    trigger: &str,
    ruling: &Value,
    declared: &str,
    now: Option<&str>,
    batch: bool,
) -> Result<Value, Stop> {
    if declared != ROUND_ARBITER {
        return Err(Stop::Declined("declined: only the `round-arbiter` subagent records a ruling (AS=round-arbiter) - a declaration, recorded, not a proof".to_owned()));
    }
    if let Some(prior) = core::rulings(root, trigger).get(trigger) {
        if !(rekeys(prior, trigger, ruling)
            && !unit_content_key(root, &core::unit_of(trigger)).is_empty())
        {
            return Err(Stop::Refused(format!("{trigger} is already ruled - one ruling per trigger, binding; the session neither re-asks nor overrules")));
        }
    }
    let batched = core::batch_triggers(root, &[]);
    let others: Vec<&String> = batched.iter().filter(|t| *t != trigger).collect();
    let with_trigger = core::batch_triggers(root, &[trigger.to_owned()]);
    if !batch && with_trigger.iter().any(|t| t == trigger) && !others.is_empty() {
        return Err(Stop::Refused(format!(
            "{} other round trigger(s) are owed with it - rule them together, ONE ruling: make arbiter-bundle BATCH=1, then make arbiter-ruled BATCH=1 FILE=<its JSON> AS=round-arbiter (FR-017)",
            others.len()
        )));
    }
    let hour = trigger.starts_with("hour:");
    let (fix, fix_on, measure) = validate_ruling(ruling, hour, batch)?;
    let d = core::feature_dir(root, trigger).ok_or_else(|| {
        Stop::Refused(
            "no active feature (.specify/feature.json) to record the ruling in".to_owned(),
        )
    })?;
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
        gm_question(root, &d, &for_gm, trigger, &when);
    }
    if hour {
        let _ = py(
            CLOSE_CHECKPOINT,
            &[
                &tree_of(root).to_string_lossy(),
                &root.to_string_lossy(),
                trigger,
            ],
        );
    }
    if text(&value, "ruling") == "accept" && text(&value, "kind") == "round" {
        accept_answers(
            root,
            text(&value, "unit"),
            &format!("accepted by the round arbiter ({trigger})"),
        );
    }
    core::pop_owed(&checks::common_dir(root), trigger).map_err(Stop::Refused)?;
    Ok(value)
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
    root: &Path,
    ruling: &Value,
    declared: &str,
    now: Option<&str>,
) -> Result<Vec<Value>, Stop> {
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
    let ruled = core::rulings(root, "");
    let mut done: Vec<&String> = triggers.iter().filter(|t| ruled.contains_key(*t)).collect();
    done.sort();
    if !done.is_empty() {
        return Err(Stop::Refused(format!(
            "already ruled: {} - one ruling per trigger, binding",
            join_refs(&done)
        )));
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
        rows.push(record_ruling(root, &t, &one, declared, now, true)?);
    }
    Ok(rows)
}

fn join_refs(v: &[&String]) -> String {
    v.iter().map(|s| s.as_str()).collect::<Vec<_>>().join(", ")
}

mod fixes;
pub use fixes::{fix_hold, open_fixes};
use fixes::{fix_home, nit_answers, settle_fix};

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

fn house_styled(value: &Value) -> Value {
    match value {
        Value::String(s) => Value::String(americanize(s)),
        Value::Array(items) => Value::Array(items.iter().map(house_styled).collect()),
        Value::Object(map) => Value::Object(
            map.iter()
                .map(|(k, v)| (k.clone(), house_styled(v)))
                .collect(),
        ),
        other => other.clone(),
    }
}

fn load_ruling(path: &str) -> Result<Value, Stop> {
    let body = std::fs::read_to_string(path).map_err(|e| Stop::Refused(e.to_string()))?;
    let parsed: Value = serde_json::from_str(&body).map_err(|e| Stop::Refused(e.to_string()))?;
    Ok(house_styled(&parsed))
}

fn feature_label(root: &Path) -> String {
    core::feature_dir(root, "").map_or_else(
        || "none".to_owned(),
        |d| {
            d.file_name()
                .map_or_else(String::new, |n| n.to_string_lossy().into_owned())
        },
    )
}

fn ruled_cli(root: &Path, trigger: &str, file: &str, who: &str) -> Reply {
    let row =
        match load_ruling(file).and_then(|r| record_ruling(root, trigger, &r, who, None, false)) {
            Ok(r) => r,
            Err(stop) => return stop.reply("arbiter-ruled"),
        };
    let t = text(&row, "trigger");
    let mut out = format!("arbiter-ruled: {t} - {} (binding; recorded in arbiter.jsonl; a for_gm question goes to escalation-check: make gm-review)\n", text(&row, "ruling"));
    let owed = crate::plan::approach_ruled(root, t);
    let plan_review = t.starts_with("round:spec-fidelity|plan:") || text(&row, "review") == "plan";
    if plan_review && matches!(text(&row, "ruling"), "accept" | "process-fault") {
        if let Some(d) = core::feature_dir(root, t) {
            match crate::plan::arbiter_accept_listed(&d, t) {
                Ok(named) => out.push_str(&format!("arbiter-ruled: {} plan block(s) recorded CLEAR - the accept is the plan's verdict\n", named.len())),
                Err(e) => return Reply { stdout: out, stderr: format!("{e}\n"), code: 1 },
            }
        }
    }
    let claims_review = text(&row, "review");
    if let Some(keys) = claims_review
        .strip_prefix("claims:")
        .filter(|_| text(&row, "ruling") == "accept")
    {
        out.push_str(&claims_accept(root, keys, t));
    }
    if let Some(o) = owed {
        out.push_str(&o);
        out.push('\n');
    }
    ok(out)
}

fn claims_accept(root: &Path, keys: &str, trigger: &str) -> String {
    let script = scripts(root).join("record/claims.py");
    let done = std::process::Command::new("python3")
        .arg(&script)
        .args([
            "--root",
            &root.to_string_lossy(),
            "accept",
            "--keys",
            keys,
            "--trigger",
            trigger,
        ])
        .output();
    let mut all = String::new();
    if let Ok(o) = done {
        all.push_str(&String::from_utf8_lossy(&o.stdout));
        all.push_str(&String::from_utf8_lossy(&o.stderr));
    }
    format!("{}\n", all.trim())
}

fn ruled_batch_cli(root: &Path, file: &str, who: &str) -> Reply {
    let rows = match load_ruling(file).and_then(|r| record_batch(root, &r, who, None)) {
        Ok(r) => r,
        Err(stop) => return stop.reply("arbiter-ruled"),
    };
    let mut out = String::new();
    for row in &rows {
        let t = text(row, "trigger");
        out.push_str(&format!("arbiter-ruled: {t} - {}\n", text(row, "ruling")));
        if let Some(o) = crate::plan::approach_ruled(root, t) {
            out.push_str(&o);
            out.push('\n');
        }
    }
    out.push_str(&format!("arbiter-ruled: the batch's {} triggers recorded (binding; each in arbiter.jsonl; a for_gm question goes to escalation-check: make gm-review)\n", rows.len()));
    ok(out)
}

fn ask_cli(root: &Path, args: &[String]) -> Reply {
    let (subject, why) = (args[0].trim(), args[1].trim());
    let review = args.get(2).map_or("", |r| r.trim());
    if !ASK_SUBJECT.is_match(subject).unwrap_or(false)
        || why.split_whitespace().count() < 2
        || why.chars().count() < 8
    {
        return fail("arbiter-ask: SUBJECT is one short id (letters, digits, . _ -) and WHY the question, two words or more\n".to_owned(), 2);
    }
    if !review.is_empty()
        && !REVIEWS.contains(&review)
        && !(review.starts_with("claims:") && review.len() > "claims:".len())
    {
        return fail(format!("arbiter-ask: REVIEW= is spec, plan or claims:<key>;<key> (the review whose verdict the ruling stands as), or left out - not {}\n", py_repr(review)), 2);
    }
    let trigger = format!("ask:{subject}");
    if core::rulings(root, &trigger).contains_key(&trigger) {
        return fail(format!("arbiter-ask: {trigger} is already ruled - one ruling per trigger, binding; ask a new SUBJECT for a new question\n"), 1);
    }
    let stands = if review.is_empty() {
        String::new()
    } else {
        format!("(REVIEW={review}: an accept stands as the {review} review's verdict)")
    };
    let detail = format!("{why} {stands}");
    let _ = core::trip(
        root,
        &trigger,
        "ask",
        "",
        detail.trim(),
        &Value::Null,
        review,
    );
    let mut out = format!("arbiter-ask: {trigger} recorded - the round arbiter rules on it, not the GM (its ruling reaches him only as a kept for_gm question, feature 432); dispatch `round-arbiter` with the MANIFEST below\n");
    if !stands.is_empty() {
        out.push_str(&format!("arbiter-ask: {stands}\n"));
    } else if ASK_HINT.is_match(subject).unwrap_or(false)
        || ASK_WORDS.is_match(why).unwrap_or(false)
    {
        out.push_str("arbiter-ask: hint - if this asks about a spec or plan review, ask it with REVIEW=spec or REVIEW=plan, so an accept stands as its verdict (feature 409)\n");
    }
    ok(out)
}

fn fix_cli(root: &Path, args: &[String]) -> Reply {
    let status = args[0].as_str();
    let ids: Vec<&str> = args[1].split_whitespace().collect();
    let note = &args[2];
    let test = args.get(3).map_or("", String::as_str);
    let label = format!("arbiter-fix-{status}");
    let unknown: Vec<&str> = ids
        .iter()
        .copied()
        .filter(|i| fix_home(root, i).is_none())
        .collect();
    if !unknown.is_empty() || ids.is_empty() {
        let found: Vec<String> = core::spec_dirs(root, "")
            .iter()
            .flat_map(|f| open_fixes(f).into_iter().map(|(t, _)| t))
            .collect();
        let open_now = if found.is_empty() {
            "none".to_owned()
        } else {
            found.join(", ")
        };
        let wanted = if unknown.is_empty() {
            "(no ID)".to_owned()
        } else {
            unknown.join(", ")
        };
        return fail(format!("{label}: refused - no open tooling fix: {wanted}; searched the active feature ({}), the feature an hour trigger names, and every feature; open now: {open_now}\n", feature_label(root)), 1);
    }
    for id in &ids {
        if let Err(stop) = settle_fix(root, id, status, note, test) {
            return match stop {
                Stop::Declined(why) | Stop::Refused(why) => {
                    fail(format!("{label}: refused - {why}\n"), 1)
                }
            };
        }
    }
    let tail = if status == "declined" {
        " - each a question owed escalation-check (make gm-review)"
    } else {
        ""
    };
    ok(format!(
        "{label}: {} fix(es) settled - {}{tail}\n",
        ids.len(),
        ids.join(", ")
    ))
}

fn nit_cli(root: &Path, args: &[String]) -> Reply {
    match nit_answers(root, &args[0], &args[1], &args[2]) {
        Err(Stop::Declined(why) | Stop::Refused(why)) => {
            fail(format!("arbiter-nit: refused - {why}\n"), 1)
        }
        Ok(done) => {
            let listed = if done.is_empty() {
                "none owed".to_owned()
            } else {
                done.join(", ")
            };
            ok(format!(
                "arbiter-nit: {} unit(s) answered at today's words - {listed}\n",
                done.len()
            ))
        }
    }
}

/// `l7r-gate arbiter <verb>`: what `make arbiter-*`, `make done`'s first step and the review gate run.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    cli_in(args, &root_dir())
}

fn cli_in(args: &[String], root: &Path) -> Reply {
    let verb = args.first().map_or("", String::as_str);
    match (verb, args.len()) {
        ("ruled", 5) if args[3] == "--as" => ruled_cli(root, &args[1], &args[2], &args[4]),
        ("ruled-batch", 4) if args[2] == "--as" => ruled_batch_cli(root, &args[1], &args[3]),
        ("gate-held", 1) => {
            let why = core::refusal(&core::blocking(root, "", true), None);
            if why.is_empty() {
                ok(String::new())
            } else {
                fail(format!("make done: refused - {why}\n"), 1)
            }
        }
        ("spec-verdict", 2) => Reply { code: i32::from(spec_verdict(Path::new(&args[1])).is_empty()), stdout: String::new(), stderr: String::new() },
        ("spec-ruled", 2) => Reply { code: i32::from(spec_ruled(Path::new(&args[1])).is_empty()), stdout: String::new(), stderr: String::new() },
        ("unit-ruled", 3) => Reply { code: i32::from(core::feature_dir(root, "").is_none_or(|d| unit_ruled(&d, &args[1], &args[2]).is_empty())), stdout: String::new(), stderr: String::new() },
        ("ask", 3 | 4) => ask_cli(root, &args[1..]),
        ("fix", 4 | 5) if matches!(args[1].as_str(), "done" | "declined") => fix_cli(root, &args[1..]),
        ("nit", 4) => nit_cli(root, &args[1..]),
        _ => fail("usage: hm_arbiter.py ruled <trigger> <json> --as round-arbiter | fix done|declined <trigger> <note> [<test>] | nit <trigger> <old> <new>\n".to_owned(), 2),
    }
}

#[cfg(test)]
mod tests;
