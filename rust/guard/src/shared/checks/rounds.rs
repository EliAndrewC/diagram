//! A record check's round on a page or pop-up (feature 375 FR-003(b)(c), FR-010; from `hm_checks.py`): a dispatch recorded and counted, launched and returned, and an edit while its checks run refused.

use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Map, Value};

use super::arbiter;
use super::fixloop;
use super::pages::subject_blocks;
use super::reply;
use super::{array_mut, falsy, git_stdout, map_mut, name_of, text};
use crate::shared::sha1;
use crate::shared::sha256;

/// The checks whose subject is a question page or a pop-up, and so freeze it while they run.
pub const PAGE_CHECKS: [&str; 10] = [
    "quote-check",
    "record-format",
    "source-reader",
    "intro-check",
    "record-style",
    "translation-check",
    "entry-drift",
    "modal-form",
    "modal-research",
    "modal-depiction",
];
/// Rounds a check may have on one subject in one feature before the round arbiter rules (FR-010).
pub const ROUND_CAP: u64 = 2;
/// A check silent this long is reported stale and may be closed by hand.
const STALE_S: f64 = 90.0 * 60.0;
/// A dispatch recorded at `PreToolUse` and never launched stops counting after this.
const PENDING_S: f64 = 120.0;
/// A `check-wave` unit's dispatch waits longer for its agent: a long wave queues behind the workflow's cap (a design number to move).
const WAVE_PENDING_S: f64 = 30.0 * 60.0;
/// The answers one `modal-research` dispatch is recorded as.
const RESEARCH_UNITS: [&str; 3] = ["modal-accuracy", "modal-references", "modal-gaps"];
/// How much of a dropped block's words a later block must carry to be that block back.
const SIMILAR: f64 = 0.6;

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static UNIT: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^unit: (\S+?):(\S.*?) \S+$"));
static UNIT_FP: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^unit: (\S+?:\S.*?) (\S+)$"));
static Q: LazyLock<Regex> = LazyLock::new(|| re(r"^\b(\d{4})(?:[.#-]|$)"));
static PAGE: LazyLock<Regex> = LazyLock::new(|| re(r"research/questions/(\d{4})-[^/]*\.html$"));
static NOTES_PAGE: LazyLock<Regex> =
    LazyLock::new(|| re(r"research/questions/(\d{4})-[^/]*\.notes\.html$"));
static NOTES: LazyLock<Regex> =
    LazyLock::new(|| re(r"ONLY the notes (.+?) and the blocks that carry them"));
static MODAL: LazyLock<Regex> =
    LazyLock::new(|| re(r"interactive/assets/modals/((?:sheet|hamlet|choice)/[^/]+)\.md$"));
static SOURCE_BUNDLE: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^# Check bundle - source \S+"));
static UNIT_NOTE: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^unit: [\w-]+:\d{4}(?:\.drawing)?#(\S+) \S+$"));
static BATCH: LazyLock<Regex> = LazyLock::new(|| re(r"^batch-\d+$"));
static OWED_LINE: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^owed: (.+)$"));
static UNIT_LINE: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^unit: "));
static SENTENCE: LazyLock<Regex> = LazyLock::new(|| re(r"(?<=[.!?])\s+"));
static WORD: LazyLock<Regex> = LazyLock::new(|| re(r"[a-z0-9]+"));
static APPLY: LazyLock<Regex> =
    LazyLock::new(|| re(r#"\bmake\b[^;&|]*\bapply-edits\b[^;&|]*\bFROM=("[^"]+"|'[^']+'|\S+)"#));
static GEN: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"\.(svg|json|jsonl|png|webp)$|^specs/|^dev/(run-log|perf-log|bypass-log|idle-log)/|^pool/.*\.notes\.md$",
    )
});
static SAFE_NAME: LazyLock<Regex> = LazyLock::new(|| re(r"[^A-Za-z0-9_-]"));

/// `0105.drawing#note` -> `q:0105`; `sheet/bath` -> `modal:sheet/bath`; "" for a tail that names neither.
#[must_use]
pub fn subject_of_unit(tail: &str) -> String {
    let q = Q.captures(tail).ok().flatten().map(|c| c[1].to_owned());
    if tail.contains('/') && q.is_none() {
        return format!("modal:{tail}");
    }
    q.map_or_else(String::new, |n| format!("q:{n}"))
}

/// The subjects a bundle's `unit:` lines name, sorted.
#[must_use]
pub fn subjects_of_manifest(text_of: &str) -> Vec<String> {
    let set: BTreeSet<String> = UNIT
        .captures_iter(text_of)
        .flatten()
        .map(|c| subject_of_unit(&c[2]))
        .filter(|s| !s.is_empty())
        .collect();
    set.into_iter().collect()
}

/// The subject a file belongs to: a question's page, drawing page or notes; a pop-up's `.md` file.
#[must_use]
pub fn subject_of_path(path: &str) -> String {
    let p = path.replace(std::path::MAIN_SEPARATOR, "/");
    if let Some(c) = PAGE
        .captures(&p)
        .ok()
        .flatten()
        .or_else(|| NOTES_PAGE.captures(&p).ok().flatten())
    {
        return format!("q:{}", &c[1]);
    }
    MODAL
        .captures(&p)
        .ok()
        .flatten()
        .map_or_else(String::new, |c| format!("modal:{}", &c[1]))
}

/// The notes a note-scoped bundle reads; empty for a bundle of the whole page. A source's bundle reads the notes its `unit:` lines name.
#[must_use]
pub fn notes_of_manifest(text_of: &str) -> BTreeSet<String> {
    let named: BTreeSet<String> = NOTES
        .captures_iter(text_of)
        .flatten()
        .flat_map(|c| {
            c[1].split(',')
                .map(|n| n.trim().to_owned())
                .collect::<Vec<_>>()
        })
        .filter(|n| !n.is_empty())
        .collect();
    if !named.is_empty() || !SOURCE_BUNDLE.is_match(text_of).unwrap_or(false) {
        return named;
    }
    UNIT_NOTE
        .captures_iter(text_of)
        .flatten()
        .map(|c| c[1].to_owned())
        .collect()
}

fn t_of(d: &Value) -> f64 {
    d.get("t").and_then(Value::as_f64).unwrap_or(0.0)
}

/// `d.get(key)` as a float, `Value::as_f64` on a string reading as 0, for `float(d.get(key, 0))`.
fn wave_of(d: &Value) -> bool {
    !falsy(d.get("wave"))
}

fn live(d: &Value, now: f64) -> bool {
    text(d, "state") != "pending"
        || now - t_of(d)
            < if wave_of(d) {
                WAVE_PENDING_S
            } else {
                PENDING_S
            }
}

fn dispatches(state: &Value) -> Vec<&Value> {
    state
        .get("dispatches")
        .and_then(Value::as_object)
        .into_iter()
        .flat_map(Map::values)
        .collect()
}

fn subjects_of(d: &Value) -> Vec<String> {
    d.get("subjects")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|v| v.as_str().map(str::to_owned))
        .collect()
}

fn has_subject(d: &Value, subject: &str) -> bool {
    subjects_of(d).iter().any(|s| s == subject)
}

/// `dispatches` on `subject` still running or pending, and live.
#[must_use]
pub fn running<'a>(state: &'a Value, subject: &str, now: f64) -> Vec<&'a Value> {
    dispatches(state)
        .into_iter()
        .filter(|d| {
            has_subject(d, subject)
                && matches!(text(d, "state"), "running" | "pending")
                && live(d, now)
        })
        .collect()
}

/// The dispatches of the subject's current round: dispatched and not yet answered.
#[must_use]
pub fn open_round<'a>(state: &'a Value, subject: &str, now: f64) -> Vec<&'a Value> {
    dispatches(state)
        .into_iter()
        .filter(|d| has_subject(d, subject) && text(d, "state") != "answered" && live(d, now))
        .collect()
}

fn collapsed(t: &str) -> String {
    t.split_whitespace().collect::<Vec<_>>().join(" ")
}

/// A workflow dispatch's key: its collapsed prompt's sha256, 16 hex digits.
#[must_use]
pub fn wave_key(t: &str) -> String {
    sha256::hex(collapsed(t).as_bytes())
        .chars()
        .take(16)
        .collect()
}

/// A workflow agent's task text, whitespace collapsed: its first user messages, each after the harness's frame line.
fn task_texts(transcript: &str) -> Vec<String> {
    let mut out = Vec::new();
    let Some(lines) = reply::read_lossy(Path::new(transcript)) else {
        return out;
    };
    for raw in reply::py_lines(&lines) {
        let Ok(line) = serde_json::from_str::<Value>(raw) else {
            continue;
        };
        let msg = line.get("message").unwrap_or(&Value::Null);
        if text(msg, "role") != "user" {
            continue;
        }
        let content = message_text(msg.get("content"));
        let tail = content
            .rsplit_once("The computed task text follows:")
            .map_or(content.as_str(), |(_, t)| t);
        out.push(collapsed(tail));
        if out.len() >= 3 {
            break;
        }
    }
    out
}

fn message_text(content: Option<&Value>) -> String {
    match content {
        Some(Value::String(s)) => s.clone(),
        Some(Value::Array(parts)) => parts
            .iter()
            .filter(|p| p.is_object())
            .map(|p| p.get("text").and_then(Value::as_str).unwrap_or(""))
            .collect::<Vec<_>>()
            .join(" "),
        _ => String::new(),
    }
}

fn prefix_hash(t: &str, n: usize) -> String {
    let prefix: String = t.chars().take(n).collect();
    sha256::hex(prefix.as_bytes()).chars().take(16).collect()
}

/// A workflow agent no `PostToolUse` gave an id to: matched to the wave dispatch its task text begins with, and launched there.
pub fn pair_wave(state: &mut Value, agent_id: &str, transcript: &str) {
    if agent_id.is_empty() || dispatches(state).iter().any(|d| text(d, "aid") == agent_id) {
        return;
    }
    let texts = task_texts(transcript);
    let ds = map_mut(state, "dispatches");
    let mut hits: Vec<(String, u64, bool, f64)> = ds
        .iter()
        .filter(|(_, d)| {
            !falsy(d.get("wave"))
                && texts.iter().any(|t| {
                    prefix_hash(
                        t,
                        usize::try_from(d.get("wave_len").and_then(Value::as_u64).unwrap_or(0))
                            .unwrap_or(0),
                    ) == text(d, "wave")
                })
        })
        .map(|(id, d)| {
            (
                id.clone(),
                d.get("wave_len").and_then(Value::as_u64).unwrap_or(0),
                text(d, "state") != "pending",
                t_of(d),
            )
        })
        .collect();
    hits.sort_by(|a, b| b.1.cmp(&a.1).then(a.2.cmp(&b.2)).then(a.3.total_cmp(&b.3)));
    for (tid, ..) in hits {
        let d = &mut ds[&tid];
        if text(d, "state") == "pending"
            || (text(d, "state") == "returned" && falsy(d.get("reply")))
        {
            d["aid"] = json!(agent_id);
            d["state"] = json!("running");
            return;
        }
    }
}

/// A refused `check-wave` run's dispatches go: it launches nothing, so none of them may freeze a page.
pub fn drop_run(cwd: &str, prefix: &str) {
    let Some(path) = super::state_path(cwd).filter(|p| p.is_file()) else {
        return;
    };
    let Some(held) = super::locked(&path) else {
        return;
    };
    let mut state = super::load(&path);
    if let Some(ds) = state.get_mut("dispatches").and_then(Value::as_object_mut) {
        ds.retain(|t, _| !t.starts_with(prefix));
    }
    let _ = super::save(&path, &state);
    drop(held);
}

fn notes_list(d: &Value) -> Vec<String> {
    d.get("notes")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|v| v.as_str().map(str::to_owned))
        .collect()
}

fn disjoint_wave(
    state: &Value,
    check: &str,
    subject: &str,
    notes: &BTreeSet<String>,
    now: f64,
) -> bool {
    let flying: Vec<&Value> = open_round(state, subject, now)
        .into_iter()
        .filter(|d| text(d, "check") == check)
        .collect();
    !notes.is_empty()
        && !flying.is_empty()
        && flying.iter().all(|d| {
            let n = notes_list(d);
            !n.is_empty() && n.iter().all(|x| !notes.contains(x))
        })
}

fn fresh_reading(state: &Value, unit: &str, notes: &BTreeSet<String>) -> bool {
    let read = state
        .get("notes_read")
        .and_then(|m| m.get(unit))
        .and_then(Value::as_array)
        .map(|a| {
            a.iter()
                .filter_map(|v| v.as_str().map(str::to_owned))
                .collect::<Vec<_>>()
        });
    let (check, subject) = unit.split_once('|').unwrap_or((unit, ""));
    let flying: Vec<String> = dispatches(state)
        .into_iter()
        .filter(|d| {
            text(d, "check") == check
                && has_subject(d, subject)
                && matches!(text(d, "state"), "pending" | "running")
        })
        .flat_map(|d| {
            let n = notes_list(d);
            if n.is_empty() {
                vec!["*".to_owned()]
            } else {
                n
            }
        })
        .collect();
    let read = match read {
        None if !flying.is_empty() => Some(flying),
        Some(mut r) => {
            r.extend(flying);
            Some(r)
        }
        None => None,
    };
    !notes.is_empty()
        && read.is_some_and(|r| !r.iter().any(|x| x == "*") && r.iter().all(|x| !notes.contains(x)))
}

/// A subject's visible sentences, whitespace-normalized (`hm_checks.sentences`).
#[must_use]
pub fn sentences(blocks: &[String]) -> Vec<String> {
    let mut out = Vec::new();
    for b in blocks {
        let flat = collapsed(b);
        let mut last = 0;
        for m in SENTENCE.find_iter(&flat).flatten() {
            out.push(flat[last..m.start()].to_owned());
            last = m.end();
        }
        out.push(flat[last..].to_owned());
    }
    out.retain(|s| !s.is_empty());
    out
}

fn sentence_key(s: &str) -> String {
    sha1::hex(s.as_bytes()).chars().take(12).collect()
}

fn first_look(state: &Value, unit: &str, current: &[String]) -> bool {
    let seen: BTreeSet<String> = state
        .get("seen")
        .and_then(|m| m.get(unit))
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|v| v.as_str().map(str::to_owned))
        .collect();
    if seen.is_empty() {
        return false;
    }
    let unseen: Vec<&String> = current
        .iter()
        .filter(|s| !seen.contains(&sentence_key(s)))
        .collect();
    let own = state
        .get("own_edits")
        .and_then(|m| m.get(unit))
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .map(|n| collapsed(n.as_str().unwrap_or("")))
        .collect::<Vec<_>>()
        .join(" ");
    !unseen.is_empty() && !unseen.iter().any(|s| own.contains(s.as_str()))
}

/// The bundle a split bundle's `batch-N/MANIFEST.md` belongs to, or "".
#[must_use]
pub fn batch_root(manifest: &str) -> String {
    let parent = Path::new(manifest)
        .parent()
        .unwrap_or_else(|| Path::new(""));
    if BATCH.is_match(&name_of(parent)).unwrap_or(false) {
        parent
            .parent()
            .map_or_else(String::new, |p| p.to_string_lossy().into_owned())
    } else {
        String::new()
    }
}

/// The batch a round is counted in: the `origin/main` the clone stands on.
#[must_use]
pub fn batch_of(root: Option<&Path>) -> String {
    root.map_or_else(String::new, |r| {
        git_stdout(r, &["rev-parse", "origin/main"])
    })
}

fn new_cause(state: &Value, unit: &str, batch: &str) -> bool {
    let seen = state
        .get("round_batch")
        .and_then(|m| m.get(unit))
        .and_then(Value::as_str)
        .unwrap_or("");
    !seen.is_empty() && !batch.is_empty() && seen != batch
}

/// Whether the record store says every unit the bundle carries on `subject` is answered at its fingerprint; else the fingerprint of the first that is not.
fn moved_since_answer(root: &Path, text_of: &str, subject: &str) -> String {
    let store = record_store(root, std::env::var("RECORD_CHECKS_DIR").ok().as_deref());
    UNIT_FP
        .captures_iter(text_of)
        .flatten()
        .find(|c| {
            let slug = &c[1];
            let tail = slug.split_once(':').map_or("", |(_, t)| t);
            subject_of_unit(tail) == subject && !answered(&store, slug, &c[2])
        })
        .map_or_else(String::new, |c| c[2].to_owned())
}

/// Where the answer records live: `RECORD_CHECKS_DIR` (a test's throwaway store), else the clone's git dir.
fn record_store(root: &Path, given: Option<&str>) -> std::path::PathBuf {
    if let Some(dir) = given.filter(|d| !d.is_empty()) {
        return dir.into();
    }
    let common = git_stdout(root, &["rev-parse", "--git-common-dir"]);
    let path = Path::new(if common.is_empty() { ".git" } else { &common });
    root.join(path).join("record-checks")
}

/// `urllib.parse.quote(slug, safe="")`.
fn quoted(slug: &str) -> String {
    slug.bytes()
        .map(|b| {
            if b.is_ascii_alphanumeric() || b"_.-~".contains(&b) {
                char::from(b).to_string()
            } else {
                format!("%{b:02X}")
            }
        })
        .collect()
}

fn answered(store: &Path, slug: &str, fp: &str) -> bool {
    let rec: Value = std::fs::read_to_string(store.join(format!("{}.json", quoted(slug))))
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok())
        .unwrap_or(Value::Null);
    fp == text(&rec, "fingerprint")
        || rec
            .get("answered")
            .and_then(Value::as_array)
            .is_some_and(|a| a.iter().any(|x| x.as_str() == Some(fp)))
}

/// What a dispatch needs beyond the state: the clone, and the escapes taken.
pub struct Dispatch<'a> {
    pub tid: &'a str,
    pub check: &'a str,
    pub manifest: &'a str,
    pub text: &'a str,
    pub now: f64,
    pub root: Option<&'a Path>,
    pub freeze_ok: bool,
    pub arbiter_ok: bool,
}

/// One subject's verdicts before the dispatch counts: whether it is a sibling batch, and the words its check reads now.
struct SubjectView {
    sibling: BTreeMap<String, bool>,
    current: BTreeMap<String, Vec<String>>,
}

fn view(
    state: &Value,
    ask: &Dispatch,
    subjects: &[String],
    notes: &BTreeSet<String>,
) -> SubjectView {
    let current = ask.root.map_or_else(BTreeMap::new, |root| {
        subjects
            .iter()
            .map(|s| (s.clone(), sentences(&subject_blocks(root, s))))
            .collect()
    });
    let root_of = batch_root(ask.manifest);
    let sibling = subjects
        .iter()
        .map(|s| {
            let same_batch = !root_of.is_empty()
                && open_round(state, s, ask.now).iter().any(|d| {
                    text(d, "check") == ask.check && batch_root(text(d, "manifest")) == root_of
                });
            (
                s.clone(),
                same_batch || disjoint_wave(state, ask.check, s, notes, ask.now),
            )
        })
        .collect();
    SubjectView { sibling, current }
}

fn repeat(
    state: &Value,
    unit: &str,
    notes: &BTreeSet<String>,
    cur: &[String],
    sibling: bool,
) -> bool {
    !sibling && !fresh_reading(state, unit, notes) && !first_look(state, unit, cur)
}

fn cap_refusal(state: &mut Value, ask: &Dispatch, root: &Path, s: &str, n: u64) -> String {
    let unit = format!("{}|{s}", ask.check);
    let prefix = format!("round:{unit}@");
    let shut = arbiter::closed(root, &prefix, None);
    let moved = if shut.is_empty() {
        String::new()
    } else {
        moved_since_answer(root, ask.text, s)
    };
    if !shut.is_empty() && moved.is_empty() {
        return format!("the round arbiter closed {unit} ({shut}) - what is left is filed; the session does not re-ask (FR-011)");
    }
    let base_has_moved = map_mut(state, "rebased")
        .get(&unit)
        .is_some_and(|b| text(b, "fp") == moved);
    if !moved.is_empty() && !base_has_moved {
        map_mut(state, "rebased").insert(unit.clone(), json!({"fp": moved, "n": n}));
    }
    let batch = batch_of(Some(root));
    if new_cause(state, &unit, &batch) && open_round(state, s, ask.now).is_empty() {
        map_mut(state, "rebased").insert(unit.clone(), json!({"fp": batch, "n": n, "cause": true}));
        map_mut(state, "round_batch").insert(unit.clone(), json!(batch));
    }
    let rebased = state
        .get("rebased")
        .and_then(|b| b.get(&unit))
        .cloned()
        .unwrap_or(Value::Null);
    let cause = !falsy(rebased.get("cause"));
    let n0 = if !shut.is_empty() || cause {
        rebased.get("n").and_then(Value::as_u64).unwrap_or(0)
    } else {
        0
    };
    let cap = n0 + ROUND_CAP + arbiter::continues(root, &prefix, n0);
    if n >= cap {
        let _ = arbiter::trip(
            root,
            &format!("round:{unit}@{}", n + 1),
            "round",
            &unit,
            &format!("round {} of {} on {s}", n + 1, ask.check),
            &json!(ask.now),
            "",
        );
        return format!(
            "round {} of `{}` on {s} in this feature passes its cap of {cap} - {}",
            n + 1,
            ask.check,
            arbiter::refusal(&[format!("round:{unit}@{}", n + 1)], Some(root))
        );
    }
    String::new()
}

/// `hm_checks.dispatch`: record a check's dispatch, or say why it is refused.
pub fn dispatch(state: &mut Value, ask: &Dispatch) -> String {
    let subjects = if PAGE_CHECKS.contains(&ask.check) {
        subjects_of_manifest(ask.text)
    } else {
        Vec::new()
    };
    let notes = notes_of_manifest(ask.text);
    if let Some(root) = ask.root.filter(|_| !ask.arbiter_ok) {
        let held = arbiter::blocking(root, "", false);
        if !held.is_empty() {
            return arbiter::refusal(&held, None);
        }
        let loop_held = fixloop::hold(state, root, ask.check, ask.text, ask.now);
        if !loop_held.is_empty() {
            return loop_held;
        }
    }
    let v = view(state, ask, &subjects, &notes);
    for s in &subjects {
        let check_ok = ask.freeze_ok || v.sibling[s];
        let same = !check_ok
            && open_round(state, s, ask.now)
                .iter()
                .any(|d| text(d, "check") == ask.check && text(d, "state") != "pending");
        if same
            && running(state, s, ask.now)
                .iter()
                .any(|d| text(d, "state") == "running")
        {
            return format!(
                "`{}` is already in {s}'s round and that round has a check still running - all of a round's checks return, their edits go in in one pass, then the page is checked once (feature 375 FR-003c)",
                ask.check
            );
        }
        let unit = format!("{}|{s}", ask.check);
        let n = map_mut(state, "rounds")
            .get(&unit)
            .and_then(Value::as_u64)
            .unwrap_or(0);
        if let Some(root) = ask.root.filter(|_| !ask.arbiter_ok) {
            let cur = v.current.get(s).map_or(&[][..], Vec::as_slice);
            if repeat(state, &unit, &notes, cur, v.sibling[s]) {
                let why = cap_refusal(state, ask, root, s, n);
                if !why.is_empty() {
                    return why;
                }
            }
        }
    }
    let (counted, marks) = counted_and_marks(state, ask, &subjects, &notes, &v);
    let mut row = Map::new();
    row.insert("check".to_owned(), json!(ask.check));
    row.insert("subjects".to_owned(), json!(subjects));
    row.insert("manifest".to_owned(), json!(ask.manifest));
    row.insert("t".to_owned(), json!(ask.now));
    row.insert("state".to_owned(), json!("pending"));
    row.insert("counted".to_owned(), json!(counted));
    row.insert("marks".to_owned(), marks);
    let owed: Vec<String> = OWED_LINE
        .captures_iter(ask.text)
        .flatten()
        .map(|c| c[1].to_owned())
        .collect();
    row.insert("owed".to_owned(), json!(owed));
    row.insert("notes".to_owned(), json!(notes.iter().collect::<Vec<_>>()));
    let quote_notes = if ask.check == "quote-check" {
        json!(fixloop::notes_of(ask.text))
    } else {
        json!({})
    };
    row.insert("quote_notes".to_owned(), quote_notes);
    row.insert(
        "prewrite".to_owned(),
        json!(ask.check == "source-reader" && !UNIT_LINE.is_match(ask.text).unwrap_or(false)),
    );
    map_mut(state, "dispatches").insert(ask.tid.to_owned(), Value::Object(row));
    String::new()
}

fn counted_and_marks(
    state: &mut Value,
    ask: &Dispatch,
    subjects: &[String],
    notes: &BTreeSet<String>,
    v: &SubjectView,
) -> (Vec<String>, Value) {
    let mut counted = Vec::new();
    let mut fresh = Vec::new();
    let mut seen = Map::new();
    let mut read = Map::new();
    for s in subjects {
        if open_round(state, s, ask.now).is_empty() {
            fresh.push(s.clone());
        }
        let unit = format!("{}|{s}", ask.check);
        let cur = v.current.get(s).map_or(&[][..], Vec::as_slice);
        if repeat(state, &unit, notes, cur, v.sibling[s]) {
            counted.push(unit.clone());
        }
        map_mut(state, "round_batch").insert(unit.clone(), json!(batch_of(ask.root)));
        if let Some(words) = v.current.get(s) {
            let keys: BTreeSet<String> = words.iter().map(|x| sentence_key(x)).collect();
            seen.insert(unit.clone(), json!(keys));
        }
        let names: BTreeSet<String> = if notes.is_empty() {
            BTreeSet::from(["*".to_owned()])
        } else {
            notes.clone()
        };
        read.insert(unit, json!(names));
    }
    (counted, json!({"fresh": fresh, "seen": seen, "read": read}))
}

fn extend_unique(list: &mut Vec<Value>, keys: Option<&Value>) {
    let items: Vec<Value> = keys.and_then(Value::as_array).cloned().unwrap_or_default();
    for k in items {
        if !list.contains(&k) {
            list.push(k);
        }
    }
}

/// What a launched dispatch's reading marks: its fresh rounds' edits reset, its seen sentences, its notes read - once.
fn apply_marks(state: &mut Value, d: &mut Map<String, Value>) {
    let marks = d.shift_remove("marks").unwrap_or(Value::Null);
    for s in marks
        .get("fresh")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(Value::as_str)
    {
        map_mut(state, "edits").insert(s.to_owned(), json!([]));
    }
    for (unit, keys) in marks
        .get("seen")
        .and_then(Value::as_object)
        .into_iter()
        .flatten()
    {
        extend_unique(array_mut(map_mut(state, "seen"), unit), Some(keys));
    }
    for (unit, keys) in marks
        .get("read")
        .and_then(Value::as_object)
        .into_iter()
        .flatten()
    {
        extend_unique(array_mut(map_mut(state, "notes_read"), unit), Some(keys));
    }
}

/// A dispatch's launch. A foreground check has already returned by its `PostToolUse`, so its reply is taken here from the tool's response.
pub fn launched(
    state: &mut Value,
    tid: &str,
    agent_id: &str,
    background: bool,
    reply_text: &str,
    keep: Option<&Path>,
) {
    let Some(mut d) = state
        .get("dispatches")
        .and_then(|m| m.get(tid))
        .and_then(Value::as_object)
        .cloned()
    else {
        return;
    };
    d.insert("aid".to_owned(), json!(agent_id));
    d.insert("state".to_owned(), json!("running"));
    apply_marks(state, &mut d);
    map_mut(state, "dispatches").insert(tid.to_owned(), Value::Object(d));
    if !background {
        returned(state, agent_id, reply_text, keep);
    }
}

fn safe_tid(tid: &str) -> String {
    SAFE_NAME.replace_all(tid, "_").into_owned()
}

fn keep_reply(keep: &Path, tid: &str, reply_text: &str) -> Option<String> {
    let _ = std::fs::create_dir_all(keep);
    let file = keep.join(format!("{}.md", safe_tid(tid)));
    std::fs::write(&file, reply_text).ok()?;
    Some(file.to_string_lossy().into_owned())
}

/// A check's return: its state, its EDIT blocks on its subjects, and (with `keep`) its reply kept for the round arbiter.
pub fn returned(state: &mut Value, agent_id: &str, reply_text: &str, keep: Option<&Path>) {
    let tids: Vec<String> = state
        .get("dispatches")
        .and_then(Value::as_object)
        .map(|m| m.keys().cloned().collect())
        .unwrap_or_default();
    for tid in tids {
        let mut d = state["dispatches"][&tid].clone();
        let mine = text(&d, "aid") == agent_id;
        if mine && keep.is_some() && !reply_text.is_empty() && falsy(d.get("reply")) {
            if let Some(kept) = keep.and_then(|k| keep_reply(k, &tid, reply_text)) {
                d["reply"] = json!(kept);
            }
        }
        if mine && !reply_text.trim().is_empty() && falsy(d.get("rounded")) {
            let counted: Vec<String> = d
                .get("counted")
                .and_then(Value::as_array)
                .into_iter()
                .flatten()
                .filter_map(|v| v.as_str().map(str::to_owned))
                .collect();
            for unit in counted {
                let rounds = map_mut(state, "rounds");
                let n = rounds.get(&unit).and_then(Value::as_u64).unwrap_or(0);
                rounds.insert(unit, json!(n + 1));
            }
            fixloop::returned(state, &d, reply_text);
            d["rounded"] = json!(true);
        }
        if mine && text(&d, "state") == "running" {
            d["state"] = json!("returned");
            for (path, old, new) in reply::blocks(reply_text) {
                for s in subjects_of(&d) {
                    array_mut(map_mut(state, "edits"), &s).push(json!([path, old, new]));
                    let unit = format!("{}|{s}", text(&d, "check"));
                    array_mut(map_mut(state, "own_edits"), &unit).push(json!(new));
                }
            }
        }
        state["dispatches"][&tid] = d;
    }
}

fn answer_names(check: &str) -> Vec<String> {
    let mut names = vec![check.to_owned()];
    if RESEARCH_UNITS.contains(&check) {
        names.push("modal-research".to_owned());
    }
    names
}

/// Close the dispatches of `check` on any of `subjects`; how many closed.
pub fn answered_count(state: &mut Value, check: &str, subjects: &[String]) -> usize {
    let names = answer_names(check);
    let mut n = 0;
    if let Some(ds) = state.get_mut("dispatches").and_then(Value::as_object_mut) {
        for d in ds.values_mut() {
            let name_hit = names.iter().any(|x| x == text(d, "check"))
                || text(d, "check") == "*"
                || check == "*";
            let overlap = subjects_of(d).iter().any(|s| subjects.contains(s));
            if name_hit && overlap && text(d, "state") != "answered" {
                d["state"] = json!("answered");
                n += 1;
            }
        }
    }
    n
}

/// Called by `record_owed.answer` through the door: the units it answered close their subjects' dispatches of that check.
pub fn record_answer(root: &Path, check: &str, slugs: &[String]) {
    let Some(path) = super::state_path(&root.to_string_lossy()).filter(|p| p.is_file()) else {
        return;
    };
    let Some(held) = super::locked(&path) else {
        return;
    };
    let mut state = super::load(&path);
    let subjects: BTreeSet<String> = slugs
        .iter()
        .map(|slug| subject_of_unit(slug.rsplit_once(':').map_or(slug.as_str(), |(_, t)| t)))
        .filter(|s| !s.is_empty())
        .collect();
    let subjects: Vec<String> = subjects.into_iter().collect();
    if answered_count(&mut state, check, &subjects) > 0 {
        let _ = super::save(&path, &state);
    }
    drop(held);
}

mod freeze;
pub use freeze::{
    apply_refusal, changed_lines, close_dispatches, dispatches_since, edit_refusal, oscillation,
    window_start, Closed,
};

#[cfg(test)]
mod tests;
