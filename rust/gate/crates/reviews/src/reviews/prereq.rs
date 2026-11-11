//! May a settlement-review be dispatched now? Feature 240's decisions (ported from `scripts/reviews/review_prereq.py`, feature 449
//! T89). Before a review is dispatched, four things are asked of the RECORD, each decidable without reading a word of prose: FR-003
//! every finding the map's last verdict raised is dispositioned; FR-004 a review of FIXES does not overlap an unfinished gate; FR-005
//! every map the review will read is current with the engine and whole; FR-006 a measured figure the dispatch quotes resolves to a
//! record. And the reviewer's two calls: the paired gate's state, and the verdict record, the review's last act.
//!
//! `l7r-gate reviews prereq <check|accept|recorded|gate-state|verdict|named|content-key> --clone DIR [...]`. The generation cache's
//! key comparison is `gencache.is_current`, asked of `scripts/bundle_door.py` (`ask:449-T89-reviews`), started only when `check`
//! has a map to ask about and from the clone's own scripts, so a fixture clone's stub answers.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Map, Value};

use super::owed::{owed, pool_map_names, TREES};
use super::{py_path, reply};
use crate::cohort::truthy;
use crate::record::args::{parse_with, Parsed, Spec};
use crate::record::bundle::door::Runner;
use crate::record::bundle::{head, py_repr, py_str};
use crate::Reply;

const VERDICTS: [&str; 3] = ["PASS", "NEEDS-WORK", "NOT-REVIEWABLE"];
const ARTIFACTS: [&str; 4] = [".json", ".svg", ".png", ".html"];
const GATE_TARGETS: [&str; 4] = ["done", "verify", "maps", "test-full"];
const NR: &str = "NOT-REVIEWABLE";

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static BACKTICKS: LazyLock<Regex> = LazyLock::new(|| re(r"`[^`\n]*`"));
static KEY: LazyLock<Regex> = LazyLock::new(|| re(r"\bm:([a-z0-9][a-z0-9-]*)\b"));
/// Feature 239's dated one-shot label, as this tool reads it (case-sensitive, unlike the spec lint's).
static ONE_SHOT: LazyLock<Regex> = LazyLock::new(|| re(r"\bobserved \d{4}-\d{2}-\d{2}\b"));
static NUMBER: LazyLock<Regex> = LazyLock::new(|| re(r"-?\d[\d,]*(?:\.\d+)?"));
static PARAGRAPH: LazyLock<Regex> = LazyLock::new(|| re(r"\n\s*\n"));
static UNIT: LazyLock<Regex> = LazyLock::new(|| re(r"\bUNIT:\s*([a-z][a-z0-9-]*)"));
static UNIT_SNAPSHOT: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"review-snapshot/((?:settlement-review|building-review|glyph-check|size-audit|fix-check)--[a-z0-9-]+)",
    )
});

/// `_read_json`: the file's JSON, or None where it is unreadable or not JSON.
fn read_json(path: &Path) -> Option<Value> {
    serde_json::from_str(&std::fs::read_to_string(path).ok()?).ok()
}

fn get<'a>(v: &'a Value, k: &str) -> Option<&'a Value> {
    v.as_object().and_then(|m| m.get(k))
}

fn text_of(v: &Value, k: &str, default: &str) -> String {
    get(v, k).map_or(default.to_owned(), py_str)
}

fn is(v: &Value, k: &str) -> bool {
    get(v, k).is_some_and(truthy)
}

fn verdict_dir(clone: &Path) -> PathBuf {
    clone.join(".git").join("review-verdicts")
}

fn disposition_dir(clone: &Path) -> PathBuf {
    clone.join(".git").join("review-dispositions")
}

/// The map's most recent verdict record, or None when no review has recorded one.
fn latest_verdict(clone: &Path, name: &str) -> Option<Value> {
    let rec = read_json(&verdict_dir(clone).join(format!("{name}.json")))?;
    let known = get(&rec, "verdict")
        .and_then(Value::as_str)
        .is_some_and(|v| VERDICTS.contains(&v));
    (rec.is_object() && known).then_some(rec)
}

/// The engine key a verdict's findings answer to: the one it carried from, on a NOT-REVIEWABLE verdict that carried some.
fn round_key(verdict: &Value) -> String {
    if get(verdict, "verdict") == Some(&json!(NR)) && is(verdict, "carried_from") {
        text_of(verdict, "carried_from", "")
    } else {
        text_of(verdict, "engine_key", "")
    }
}

/// The items of a JSON list (`list(x)`), none for anything else.
fn items(v: Option<&Value>) -> &[Value] {
    v.and_then(Value::as_array).map_or(&[], Vec::as_slice)
}

/// Finding ids `make review-accept` dispositioned for the verdict whose engine key is `key` (FR-003; feature 261).
fn accepted_ids(clone: &Path, name: &str, key: &str) -> BTreeSet<String> {
    let rec =
        read_json(&disposition_dir(clone).join(format!("{name}.json"))).unwrap_or(Value::Null);
    items(get(&rec, "accepted"))
        .iter()
        .filter(|i| {
            i.is_object()
                && is(i, "finding")
                && text_of(i, "reason", "").split_whitespace().count() >= 2
                && (key.is_empty() || (is(i, "round") && key.starts_with(&text_of(i, "round", ""))))
        })
        .map(|i| text_of(i, "finding", ""))
        .collect()
}

/// Every entry of every feature's `measurements.json`, each carrying its own key.
fn measurement_records(clone: &Path) -> Vec<Value> {
    let mut files: Vec<PathBuf> = std::fs::read_dir(clone.join("specs"))
        .map(|rd| {
            rd.filter_map(Result::ok)
                .map(|e| e.path().join("measurements.json"))
                .filter(|p| p.exists())
                .collect()
        })
        .unwrap_or_default();
    files.sort();
    let mut out = Vec::new();
    for path in files {
        if let Some(Value::Object(data)) = read_json(&path) {
            for (key, entry) in data {
                if let Value::Object(mut e) = entry {
                    e.insert("key".to_owned(), json!(key));
                    out.push(Value::Object(e));
                }
            }
        }
    }
    out
}

/// The findings a verdict leaves to be dispositioned: its own, or a NOT-REVIEWABLE verdict's carried ones (and its own where a red
/// gate downgraded a concluded review, feature 280).
fn raised_findings(verdict: &Value) -> Vec<Value> {
    let own: Vec<Value> = if get(verdict, "verdict") == Some(&json!(NR)) {
        let mut own = items(get(verdict, "carried")).to_vec();
        if is(verdict, "concluded") {
            own.extend_from_slice(items(get(verdict, "findings")));
        }
        own
    } else {
        items(get(verdict, "findings")).to_vec()
    };
    own.into_iter().filter(Value::is_object).collect()
}

/// The ids of the findings the map's last verdict raised that nothing verifies and nothing accepted (FR-003).
fn unverified_findings(clone: &Path, name: &str, records: &[Value]) -> Vec<String> {
    let Some(verdict) = latest_verdict(clone, name) else {
        return Vec::new();
    };
    let raised = raised_findings(&verdict);
    if raised.is_empty() {
        return Vec::new();
    }
    let key = round_key(&verdict);
    let strict = is(&verdict, "strict");
    let mut done: BTreeSet<String> = records
        .iter()
        .filter(|r| {
            is(r, "verifies")
                && get(r, "subject") == Some(&json!(name))
                && is(r, "quantity")
                && is(r, "source")
                && (!strict || {
                    let answers = text_of(r, "answers", "");
                    answers.chars().count() >= 12 && key.starts_with(&text_of(r, "answers", "None"))
                })
        })
        .map(|r| text_of(r, "verifies", ""))
        .collect();
    done.extend(accepted_ids(clone, name, &key));
    raised
        .iter()
        .map(|f| text_of(f, "id", "None"))
        .filter(|id| !done.contains(id))
        .collect()
}

/// The `answers` a record must carry for this map's last verdict, when that verdict is strict.
fn answers_hint(clone: &Path, name: &str) -> String {
    let verdict = latest_verdict(clone, name).unwrap_or(Value::Null);
    let key = round_key(&verdict);
    if is(&verdict, "strict") && !key.is_empty() {
        format!(" and \"answers\": \"{}\"", head(&key, 12))
    } else {
        String::new()
    }
}

fn has_findings(clone: &Path, name: &str) -> bool {
    latest_verdict(clone, name)
        .is_some_and(|v| get(&v, "verdict") != Some(&json!(NR)) && is(&v, "findings"))
}

/// The pool generator of a map: the first `pool/*/<name>/<name>.gen.py`.
fn gen_of(skill: &Path, name: &str) -> Option<PathBuf> {
    let pool = skill.join("pool");
    let mut hits: Vec<PathBuf> = std::fs::read_dir(&pool)
        .map(|rd| {
            rd.filter_map(Result::ok)
                .map(|e| {
                    pool.join(e.file_name())
                        .join(name)
                        .join(format!("{name}.gen.py"))
                })
                .filter(|p| p.exists())
                .collect()
        })
        .unwrap_or_default();
    hits.sort();
    hits.into_iter().next()
}

/// The generation cache's key comparison for a generator's path.
pub type Current<'a> = dyn FnMut(&str) -> bool + 'a;

fn same_bytes(a: &Path, b: &Path) -> bool {
    std::fs::read(a).ok() == std::fs::read(b).ok()
}

/// Each map whose generator's key has moved, or whose artifacts are not all where the reviewer will read them, with the reason (FR-005).
fn stale_maps(
    skill: &Path,
    names: &[String],
    current: &mut Current,
    prompt: &str,
    snapshot_of: &BTreeMap<String, String>,
) -> Vec<String> {
    let mut out = Vec::new();
    let snapshots = skill.join(".git").join("review-snapshot");
    for name in names {
        let Some(gen) = gen_of(skill, name) else {
            out.push(format!("{name}: no pool generator by that name"));
            continue;
        };
        let parent = gen.parent().unwrap_or(skill).to_path_buf();
        let snap = snapshot_of.get(name).unwrap_or(name);
        let in_snapshot = prompt.contains(&format!("review-snapshot/{snap}"));
        let at = if in_snapshot {
            snapshots.join(snap).join("clone")
        } else {
            parent.clone()
        };
        let file = |dir: &Path, ext: &str| dir.join(format!("{name}{ext}"));
        let sheet = !file(&parent, ".json").exists() && file(&parent, ".svg").is_file();
        let missing: Vec<&str> = ARTIFACTS
            .iter()
            .copied()
            .filter(|ext| !(file(&at, ext).is_file() || (sheet && *ext == ".json")))
            .collect();
        let rel = gen
            .strip_prefix(skill)
            .unwrap_or(&gen)
            .to_string_lossy()
            .into_owned();
        let older = in_snapshot
            && missing.is_empty()
            && [".json", ".svg"].iter().any(|ext| {
                file(&parent, ext).is_file() && !same_bytes(&file(&at, ext), &file(&parent, ext))
            });
        let gone = missing.join(" ");
        if !current(&gen.to_string_lossy()) {
            out.push(format!("{name}: its generation key has moved - the map on disk is not what the engine draws now - `make map GEN={rel}`"));
        } else if older {
            out.push(format!("{name}: the review snapshot the dispatch names is of an older map than the pool's - re-take it (`make verify`), or run `make map GEN={rel}` and dispatch against the pool folder without naming the snapshot"));
        } else if !missing.is_empty() && in_snapshot {
            out.push(format!("{name}: the review snapshot the dispatch names lacks {gone} - re-take it (`make verify`), or run `make map GEN={rel}` and dispatch against the pool folder without naming the snapshot"));
        } else if !missing.is_empty() {
            out.push(format!("{name}: its pool folder lacks {gone} - a reviewer would read an incomplete map - `make map GEN={rel}`"));
        }
    }
    out
}

fn number(text: &str) -> Option<f64> {
    let m = NUMBER.find(text).ok().flatten()?;
    m.as_str().replace(',', "").parse().ok()
}

/// The one definition of a figure (feature 239 spec D4), asked of the spec lint by command as the Python asked it (`check spec-lint
/// --figure-pattern`, whose run the tool-usage log records), Python's `\w` (which holds every numeric character) read as `\w\p{N}`.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn figure_pattern(tree: &Path) -> Result<Regex, String> {
    let done = Command::new(tree.join("scripts/gates/l7r-gate.sh"))
        .args(["check", "spec-lint", "--figure-pattern"])
        .output()
        .map_err(|e| e.to_string())?;
    if !done.status.success() {
        return Err(String::from_utf8_lossy(&done.stderr).into_owned());
    }
    let pattern = String::from_utf8_lossy(&done.stdout)
        .trim()
        .replace(r"\w", r"\w\p{N}");
    Regex::new(&pattern).map_err(|e| e.to_string())
}

/// Each measured figure in the dispatch that no record backs, by feature 239's convention (FR-006): the spec lint's own pattern.
fn unresolved_figures(prompt: &str, records: &[Value], figure: &Regex) -> Vec<String> {
    let by_key: BTreeMap<String, &Value> = records
        .iter()
        .map(|r| (text_of(r, "key", "None"), r))
        .collect();
    let mut out = Vec::new();
    for para in PARAGRAPH.split(prompt).filter_map(Result::ok) {
        if ONE_SHOT.is_match(para).unwrap_or(false) && para.to_lowercase().contains("method") {
            continue;
        }
        let values: Vec<Option<f64>> = KEY
            .captures_iter(para)
            .filter_map(Result::ok)
            .filter_map(|c| {
                by_key
                    .get(&c[1])
                    .map(|r| number(&text_of(r, "value", "None")))
            })
            .collect();
        let bare = BACKTICKS.replace_all(para, " ");
        for m in figure.find_iter(&bare).filter_map(Result::ok) {
            let n = number(m.as_str());
            let backed = n.is_some_and(|n| {
                values
                    .iter()
                    .flatten()
                    .any(|v| (v - n).abs() <= 0.051_f64.max(v.abs() * 0.005))
            });
            if !backed {
                out.push(m.as_str().trim().to_owned());
            }
        }
    }
    out
}

/// The owed units a dispatch asks a review of (feature 294): its `UNIT:` lines and snapshot folders, else the maps it names.
fn units_named(prompt: &str, pool: &[String]) -> Vec<String> {
    let mut units: BTreeSet<String> = BTreeSet::new();
    for re in [&*UNIT, &*UNIT_SNAPSHOT] {
        units.extend(
            re.captures_iter(prompt)
                .filter_map(Result::ok)
                .map(|c| c[1].to_owned()),
        );
    }
    if units.is_empty() {
        maps_named(prompt, pool)
    } else {
        units.into_iter().collect()
    }
}

/// The maps a dispatch asks a review of (feature 248 FR-001): by their snapshot directory when the prompt names one, else by name.
fn maps_named(prompt: &str, pool: &[String]) -> Vec<String> {
    let names: BTreeSet<&String> = pool.iter().collect();
    let hit = |pattern: String| re(&pattern).is_match(prompt).unwrap_or(false);
    let by_snapshot: Vec<String> = names
        .iter()
        .filter(|n| {
            hit(format!(
                "review-snapshot/{}(?![A-Za-z0-9_-])",
                fancy_regex::escape(n)
            ))
        })
        .map(|n| (*n).clone())
        .collect();
    if !by_snapshot.is_empty() {
        return by_snapshot;
    }
    names
        .iter()
        .filter(|n| {
            hit(format!(
                "(?i)(?<![A-Za-z0-9_-]){}(?![A-Za-z0-9_-])",
                fancy_regex::escape(n)
            ))
        })
        .map(|n| (*n).clone())
        .collect()
}

/// Each owed unit's slug -> the map or sheet it is reviewed on (feature 294).
fn unit_maps(clone: &Path) -> BTreeMap<String, String> {
    owed(clone, true)
        .1
        .into_iter()
        .map(|u| (u.slug(), u.on))
        .collect()
}

/// Every reason this dispatch should not run, in the order a session would fix them. Empty means go.
fn check(
    clone: &Path,
    names: &[String],
    prompt: &str,
    gate_green: bool,
    current: &mut Current,
) -> Result<Vec<String>, String> {
    let records = measurement_records(clone);
    let mut problems = Vec::new();
    for name in names {
        let ids = unverified_findings(clone, name, &records);
        if !ids.is_empty() {
            problems.push(format!(
                "FR-003 {name}: finding(s) {} from its last review have no record verifying them - add a measurements.json entry with \
                 \"verifies\", \"subject\": \"{name}\"{}, or `make review-accept MAP={name} FINDING=<id> REASON=\"...\"` for one deliberately left",
                ids.join(", "),
                answers_hint(clone, name)
            ));
        }
    }
    if names.iter().any(|n| has_findings(clone, n)) && !gate_green {
        problems.push("FR-004 this is a review of FIXES, and the gate is not green for this engine key - run `make done` first".to_owned());
    }
    let on = unit_maps(clone);
    let mut snapshot_of = BTreeMap::new();
    let mut maps = BTreeSet::new();
    for n in names {
        let map = on.get(n).unwrap_or(n);
        if on.get(n).is_some_and(|m| !m.is_empty()) {
            snapshot_of.insert(map.clone(), n.clone());
        }
        if !map.is_empty() {
            maps.insert(map.clone());
        }
    }
    let maps: Vec<String> = maps.into_iter().collect();
    problems.extend(
        stale_maps(clone, &maps, current, prompt, &snapshot_of)
            .into_iter()
            .map(|p| format!("FR-005 {p}")),
    );
    let figure = figure_pattern(&crate::record::repo::tree_of(clone))?;
    let figures = unresolved_figures(prompt, &records, &figure);
    if !figures.is_empty() {
        problems.push(format!(
            "FR-006 figure(s) quoted with no record behind them: {} - cite the `m:` key or record it",
            figures.join("; ")
        ));
    }
    Ok(problems)
}

/// Record a finding deliberately left as it is (FR-003): the refusal, or None when recorded.
fn accept(clone: &Path, name: &str, finding: &str, reason: &str) -> Option<String> {
    if reason.split_whitespace().count() < 2 || reason.trim().chars().count() < 8 {
        return Some("an acceptance needs a REASON of at least two words and eight characters - it is what a later audit reads".to_owned());
    }
    let verdict = latest_verdict(clone, name).unwrap_or(Value::Null);
    let raised: BTreeSet<String> = raised_findings(&verdict)
        .iter()
        .map(|f| text_of(f, "id", "None"))
        .collect();
    if !raised.contains(finding) {
        let listed = raised.iter().cloned().collect::<Vec<_>>().join(", ");
        let listed = if listed.is_empty() {
            "none".to_owned()
        } else {
            listed
        };
        return Some(format!(
            "{name}'s last verdict raised no finding {} (it raised: {listed})",
            py_repr(finding)
        ));
    }
    let path = disposition_dir(clone).join(format!("{name}.json"));
    let _ = std::fs::create_dir_all(disposition_dir(clone));
    let rec = read_json(&path).unwrap_or(Value::Null);
    let key = head(&round_key(&verdict), 12).to_owned();
    let mut kept: Vec<Value> = items(get(&rec, "accepted"))
        .iter()
        .filter(|i| {
            i.is_object()
                && !(get(i, "finding") == Some(&json!(finding))
                    && get(i, "round") == Some(&json!(key)))
        })
        .cloned()
        .collect();
    kept.push(json!({"finding": finding, "round": key, "reason": reason.trim()}));
    let _ = super::write_json(&path, &json!({"map": name, "accepted": kept}));
    None
}

/// Has every one of these maps a PASS or NEEDS-WORK verdict for THIS engine key? (FR-002)
fn recorded(clone: &Path, names: &[String], key: &str) -> bool {
    if names.is_empty() || key.is_empty() {
        return false;
    }
    names.iter().all(|name| {
        latest_verdict(clone, name).is_some_and(|v| {
            get(&v, "verdict") != Some(&json!(NR)) && text_of(&v, "engine_key", "") == key
        })
    })
}

/// `green` (a green gate has seen this engine content), `running` (a gate target is live in this clone) or `red`.
fn gate_state(clone: &Path) -> &'static str {
    let fresh = Command::new(clone.join("scripts/gates/l7r-gate.sh"))
        .args(["stamp", "--fresh", "diagram"])
        .current_dir(clone)
        .output()
        .is_ok_and(|o| o.status.success());
    if fresh {
        return "green";
    }
    let live = Command::new("bash")
        .arg(clone.join("scripts/hooks/finished-run-hooks.sh"))
        .arg("live")
        .arg(clone)
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).into_owned())
        .unwrap_or_default();
    let running = live
        .lines()
        .filter(|l| !l.trim().is_empty())
        .filter_map(|l| l.split_whitespace().last())
        .any(|t| GATE_TARGETS.contains(&t));
    if running {
        "running"
    } else {
        "red"
    }
}

/// The map or sheet an owed review unit is judged on, or "" where the unit is not owed now.
fn unit_sheet(clone: &Path, unit: &str) -> String {
    owed(clone, true)
        .1
        .into_iter()
        .find(|u| u.slug() == unit)
        .map(|u| u.on)
        .unwrap_or_default()
}

fn dirs_in(dir: &Path) -> Vec<String> {
    std::fs::read_dir(dir)
        .map(|rd| {
            rd.filter_map(Result::ok)
                .map(|e| e.file_name().to_string_lossy().into_owned())
                .collect()
        })
        .unwrap_or_default()
}

/// A hash of what a review of `sheet` read: its drawing and its notes, wherever its folder is in the pool trees; "" with none.
#[must_use]
pub fn content_key(clone: &Path, sheet: &str) -> String {
    if sheet.is_empty() {
        return String::new();
    }
    let folder = TREES.iter().find_map(|tree| {
        let base = clone.join(tree);
        dirs_in(&base)
            .into_iter()
            .map(|c| base.join(c).join(sheet))
            .find(|d| d.is_dir())
    });
    let Some(folder) = folder else {
        return String::new();
    };
    let mut data = Vec::new();
    for name in [format!("{sheet}.svg"), format!("{sheet}.notes.md")] {
        data.extend_from_slice(name.as_bytes());
        data.push(0);
        data.extend(std::fs::read(folder.join(&name)).unwrap_or_default());
        data.push(0);
    }
    l7r_guard::shared::sha256::hex(&data)[..16].to_owned()
}

/// A unit's content key, its sheet looked up (`content-key`): what the review gate and the round arbiter ask.
#[must_use]
pub fn unit_content_key(clone: &Path, unit: &str) -> String {
    content_key(clone, &unit_sheet(clone, unit))
}

/// Write the map's verdict record, the review's last act (FR-001): `(what was recorded, the record)`.
fn write_verdict(
    clone: &Path,
    name: &str,
    verdict: &str,
    mut findings: Vec<Map<String, Value>>,
    state: &str,
) -> (String, Value) {
    let pairing = read_json(&clone.join(".git").join("pairing-state.json")).unwrap_or(Value::Null);
    let key = if pairing.is_object() {
        text_of(&pairing, "review_dispatch_key", "")
    } else {
        String::new()
    };
    for (i, f) in findings.iter_mut().enumerate() {
        f.entry("id")
            .or_insert_with(|| json!(format!("F{}", i + 1)));
    }
    let mut rec = Map::new();
    rec.insert("map".to_owned(), json!(name));
    rec.insert("unit".to_owned(), json!(name));
    rec.insert("engine_key".to_owned(), json!(key));
    rec.insert("verdict".to_owned(), json!(verdict));
    rec.insert("gate".to_owned(), json!(state));
    rec.insert(
        "findings".to_owned(),
        Value::Array(findings.into_iter().map(Value::Object).collect()),
    );
    rec.insert("strict".to_owned(), json!(true));
    let ck = unit_content_key(clone, name);
    if !ck.is_empty() {
        rec.insert("content_key".to_owned(), json!(ck));
    }
    if verdict != NR && state == "red" {
        rec.insert("verdict".to_owned(), json!(NR));
        rec.insert("concluded".to_owned(), json!(verdict));
        rec.insert(
            "why".to_owned(),
            json!("the paired gate was red when the verdict was written"),
        );
    }
    if rec["verdict"] == json!(NR) {
        if let Some(prior) = latest_verdict(clone, name) {
            rec.insert("carried".to_owned(), Value::Array(raised_findings(&prior)));
            rec.insert(
                "carried_from".to_owned(),
                json!(text_of(&prior, "engine_key", "")),
            );
        }
    }
    let _ = std::fs::create_dir_all(verdict_dir(clone));
    let rec = Value::Object(rec);
    let _ = super::write_json(&verdict_dir(clone).join(format!("{name}.json")), &rec);
    (text_of(&rec, "verdict", ""), rec)
}

const COMMANDS: [&str; 7] = [
    "check",
    "accept",
    "recorded",
    "gate-state",
    "verdict",
    "named",
    "content-key",
];

fn usage(why: &str) -> Reply {
    reply(
        String::new(),
        format!("l7r-gate reviews prereq: {why}\n"),
        2,
    )
}

fn read_prompt(file: &str) -> Result<String, Reply> {
    std::fs::read_to_string(py_path(file))
        .map(|t| crate::record::repo::universal(&t))
        .map_err(|e| {
            reply(
                String::new(),
                format!("l7r-gate reviews prereq: {file}: {e}\n"),
                1,
            )
        })
}

/// `review_prereq.py`'s command line.
pub fn cli(args: &[String]) -> Reply {
    let specs = [
        Spec::value("--verdict"),
        Spec::value("--findings-file"),
        Spec::value("--key"),
        Spec::value("--clone"),
        Spec::value("--maps"),
        Spec::value("--prompt-file"),
        Spec::value("--gate-green"),
        Spec::value("--map"),
        Spec::value("--unit"),
        Spec::value("--finding"),
        Spec::value("--reason"),
    ];
    let p = match parse_with(args, &specs, 1) {
        Ok(p) => p,
        Err(why) => return usage(&why),
    };
    let Some(command) = p.positional.first().map(String::as_str) else {
        return usage("the following arguments are required: command, --clone");
    };
    if !COMMANDS.contains(&command) {
        return usage(&format!(
            "argument command: invalid choice: {}",
            py_repr(command)
        ));
    }
    if !p.has("--clone") {
        return usage("the following arguments are required: --clone");
    }
    let green = p.text("--gate-green", "no");
    if !matches!(green, "yes" | "no") {
        return usage(&format!(
            "argument --gate-green: invalid choice: {}",
            py_repr(green)
        ));
    }
    run(command, &p)
}

fn run(command: &str, p: &Parsed) -> Reply {
    let clone = py_path(p.text("--clone", ""));
    let map = p.last_of(&["--map", "--unit"], "").to_owned();
    match command {
        "content-key" => reply(unit_content_key(&clone, &map) + "\n", String::new(), 0),
        "gate-state" => reply(format!("{}\n", gate_state(&clone)), String::new(), 0),
        "verdict" => verdict_cli(&clone, &map, p),
        "recorded" => {
            let maps: Vec<String> = p
                .text("--maps", "")
                .split_whitespace()
                .map(str::to_owned)
                .collect();
            reply(
                String::new(),
                String::new(),
                i32::from(!recorded(&clone, &maps, p.text("--key", ""))),
            )
        }
        "named" => {
            let maps = p.text("--maps", "");
            let pool: Vec<String> = if maps.is_empty() {
                pool_map_names(&clone)
            } else {
                maps.split_whitespace().map(str::to_owned).collect()
            };
            match read_prompt(p.text("--prompt-file", "")) {
                Ok(prompt) => reply(
                    units_named(&prompt, &pool)
                        .iter()
                        .map(|n| n.clone() + "\n")
                        .collect(),
                    String::new(),
                    0,
                ),
                Err(r) => r,
            }
        }
        "accept" => {
            let (finding, reason) = (p.text("--finding", ""), p.text("--reason", ""));
            accept(&clone, &map, finding, reason).map_or_else(
                || reply(format!("accepted {finding} on {map}\n"), String::new(), 0),
                |r| reply(r + "\n", String::new(), 1),
            )
        }
        _ => check_cli(&clone, p),
    }
}

fn verdict_cli(clone: &Path, map: &str, p: &Parsed) -> Reply {
    let file = p.text("--findings-file", "");
    let findings = if file.is_empty() {
        Some(Value::Array(Vec::new()))
    } else {
        read_json(&py_path(file))
    };
    let Some(Value::Array(findings)) = findings else {
        return reply(
            "--findings-file must hold a JSON list of {id, severity, what}\n".to_owned(),
            String::new(),
            2,
        );
    };
    let verdict = p.text("--verdict", "");
    // the gate's state is read before the verdict is judged, as the Python's argument order read it (its stamp check is recorded)
    let state = gate_state(clone);
    if !VERDICTS.contains(&verdict) {
        return reply(
            String::new(),
            format!(
                "l7r-gate reviews prereq: verdict must be one of {}\n",
                VERDICTS.join(", ")
            ),
            1,
        );
    }
    let findings = findings
        .into_iter()
        .filter_map(|f| match f {
            Value::Object(m) => Some(m),
            _ => None,
        })
        .collect();
    let (got, rec) = write_verdict(clone, map, verdict, findings, state);
    let key = text_of(&rec, "engine_key", "");
    let key = if key.is_empty() {
        "NONE - no dispatch recorded".to_owned()
    } else {
        key
    };
    reply(
        format!(
            "recorded {got} for {map} (engine key {key}, gate {})\n",
            text_of(&rec, "gate", "")
        ),
        String::new(),
        0,
    )
}

fn check_cli(clone: &Path, p: &Parsed) -> Reply {
    let prompt = match read_prompt(p.text("--prompt-file", "")) {
        Ok(t) => t,
        Err(r) => return r,
    };
    let maps: Vec<String> = p
        .text("--maps", "")
        .split_whitespace()
        .map(str::to_owned)
        .collect();
    let mut runner = Runner::new(clone);
    let mut failed: Option<String> = None;
    let mut current = |gen: &str| match runner.ask("is_current", &json!([gen])) {
        Ok(v) => v.as_bool().unwrap_or(false),
        Err(why) => {
            failed.get_or_insert(why);
            false
        }
    };
    let problems = check(
        clone,
        &maps,
        &prompt,
        p.text("--gate-green", "no") == "yes",
        &mut current,
    );
    let problems = match (problems, failed) {
        (Ok(p), None) => p,
        (Err(why), _) | (_, Some(why)) => return reply(String::new(), why, 1),
    };
    let mut out = String::new();
    for line in &problems {
        let _ = writeln!(out, "{line}");
    }
    reply(out, String::new(), i32::from(!problems.is_empty()))
}

#[cfg(test)]
mod tests;
