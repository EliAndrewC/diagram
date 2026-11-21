//! Writing a plan review's verdict (feature 243; feature 449 T066, from `plan_gate.py`). A verdict is derived from its rulings, kept per
//! block, and declined unless the caller declares itself the reviewer: nothing distinguishes the shells, so the declaration is recorded
//! rather than proven.

use std::collections::BTreeSet;
use std::path::Path;

use l7r_shared::guards::house_style_hooks::americanize_json;
use serde_json::{json, Map, Value};

use super::approach::{checklist, owe};
use super::history::{keep, History};
use super::sections::{
    block_digest, blocks, digest, heading_text, leading_task, re, task_sections, typo_only, TASK_ID,
};
use super::status::{block_status, reviewed_blocks, text_of, RECORD, REMOVED};
use super::{pretty, today};

const REVIEWER: &str = "spec-fidelity";
const ACCEPTS: [&str; 2] = ["accept", "process-fault"];

/// Why a recording was declined (exit 2) or refused (exit 1).
#[derive(Debug, PartialEq, Eq)]
pub(super) enum Stop {
    Declined(String),
    Refused(String),
}

fn refused<T>(why: impl Into<String>) -> Result<T, Stop> {
    Err(Stop::Refused(why.into()))
}

fn decision_id(d: &Value) -> &str {
    text_of(d, "id").unwrap_or("?")
}

/// CLEAR unless a narrowing decision stands ruled NOT LEGITIMATE; refuses a malformed decision.
pub(super) fn derive_verdict(decisions: &[Value]) -> Result<&'static str, Stop> {
    for d in decisions {
        let class = d.get("class").unwrap_or(&Value::Null);
        let ruling = d.get("ruling").unwrap_or(&Value::Null);
        if class != "within" && class != "narrowing" {
            return refused(format!(
                "decision {}: class must be one of ('within', 'narrowing'), not {}",
                decision_id(d),
                crate::checks::py_repr(class)
            ));
        }
        if class == "narrowing" && ruling != "LEGITIMATE" && ruling != "NOT LEGITIMATE" {
            return refused(format!("decision {}: a narrowing decision needs a ruling from ('LEGITIMATE', 'NOT LEGITIMATE')", decision_id(d)));
        }
        if class == "within" && !ruling.is_null() {
            return refused(format!(
                "decision {}: a decision within what was asked carries no ruling",
                decision_id(d)
            ));
        }
        if text_of(d, "id").is_none_or(str::is_empty)
            || text_of(d, "summary").is_none_or(str::is_empty)
        {
            return refused("every decision needs an id and a summary");
        }
    }
    Ok(
        if decisions
            .iter()
            .any(|d| d.get("ruling").is_some_and(|r| r == "NOT LEGITIMATE"))
        {
            "BLOCKED"
        } else {
            "CLEAR"
        },
    )
}

/// Each decision in the house style (feature 385 T88), every string at any depth as a JSON record takes it (`americanize_json`), keys as
/// written. WHY the id too (feature 449 T242): an id is prose nothing matches on (`status.rs` names a BLOCKED one, the arbiter's bundle
/// prints it), and spec-fidelity's British form of 'behavior' in one, written as given, turned `make quick` red three times on
/// 2026-11-20; a class, ruling or digest has no word the correction reaches.
fn house_style(decisions: Option<&Value>) -> Option<Vec<Value>> {
    Some(
        decisions?
            .as_array()?
            .iter()
            .map(americanize_json)
            .collect(),
    )
}

fn read_json(path: &Path) -> Value {
    serde_json::from_str(&std::fs::read_to_string(path).unwrap_or_default()).unwrap_or(json!({}))
}

fn feature_name(spec_dir: &Path) -> String {
    spec_dir
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned()
}

/// A record from before amendment 11 converted (D63): each block under its verdict, task entries without their text, no copy of the plan.
pub(super) fn slim_record(review: &Value) -> Value {
    let mut out: Map<String, Value> = review
        .as_object()
        .into_iter()
        .flatten()
        .filter(|(k, _)| *k != "plan_text")
        .map(|(k, v)| (k.clone(), v.clone()))
        .collect();
    if !out.contains_key("blocks") && text_of(review, "plan_text").is_some() {
        let when = review.get("reviewed").cloned().unwrap_or(json!(""));
        let converted: Map<String, Value> = reviewed_blocks(review)
            .into_iter()
            .map(|(k, e)| {
                (
                    k,
                    json!({"sha256": e["sha256"], "verdict": e["verdict"], "reviewed": when}),
                )
            })
            .collect();
        out.insert("blocks".to_owned(), Value::Object(converted));
    }
    if let Some(tasks) = out.get_mut("tasks").and_then(Value::as_object_mut) {
        for entry in tasks.values_mut().filter_map(Value::as_object_mut) {
            entry.remove("section_text");
        }
    }
    Value::Object(out)
}

fn starting_record(spec_dir: &Path) -> Value {
    let path = spec_dir.join(RECORD);
    if path.is_file() {
        slim_record(&read_json(&path))
    } else {
        json!({"feature": feature_name(spec_dir)})
    }
}

/// A decision preflight's verdict on one task's section (feature 375 FR-003(a), plan D3/D19), kept under `tasks.<id>`.
pub(super) fn record_task(
    spec_dir: &Path,
    task: &str,
    review: &Value,
    declared: &str,
    when: Option<&str>,
) -> Result<Value, Stop> {
    if declared != REVIEWER {
        return Err(Stop::Declined(format!(
            "declined: only the `{REVIEWER}` subagent records a decision preflight (AS={REVIEWER})"
        )));
    }
    let plan = std::fs::read_to_string(spec_dir.join("plan.md")).unwrap_or_default();
    let Some(section) = task_sections(&plan).remove(task) else {
        return refused(format!("plan.md has no section naming {task} - a task's decisions go under a heading that names it"));
    };
    let sha = text_of(review, "section_sha256")
        .filter(|s| !s.is_empty())
        .or(text_of(review, "plan_sha256"))
        .unwrap_or("");
    if sha != digest(section.as_bytes()) {
        return refused(format!("section_sha256 does not match {task}'s section - it changed while it was being reviewed"));
    }
    let Some(decisions) = house_style(review.get("decisions")) else {
        return refused("decisions must be a list");
    };
    let verdict = derive_verdict(&decisions)?;
    let day = when.map_or_else(today, str::to_owned);
    let mut out = starting_record(spec_dir);
    let entry = json!({"section_sha256": sha, "reviewed": day, "declared": declared, "decisions": decisions, "verdict": verdict});
    out.as_object_mut().into_iter().for_each(|o| {
        let tasks = o.entry("tasks").or_insert(json!({}));
        tasks[task] = entry.clone();
    });
    let _ = std::fs::write(spec_dir.join(RECORD), pretty(&out));
    // ...AND A CLEAR SECTION IS ITS BLOCKS' REVIEW TOO (the GM 2026-10-24): the reviewer read every block of the section
    if verdict == "CLEAR" {
        let inside: Map<String, Value> = blocks(&plan)
            .into_iter()
            .filter(|(_, b, _)| !b.trim().is_empty() && section.contains(b.trim()))
            .map(|(k, b, _)| (k, Value::from(block_digest(&b))))
            .collect();
        let named = json!({"blocks": inside, "decisions": decisions});
        record_blocks(spec_dir, &named, declared, when)?;
    }
    Ok(entry)
}

/// A whole plan's verdict: a verdict per block, and no copy of the plan.
pub(super) fn record(
    spec_dir: &Path,
    review: &Value,
    declared: &str,
    when: Option<&str>,
) -> Result<Value, Stop> {
    if declared != REVIEWER {
        return Err(Stop::Declined(format!("declined: only the `{REVIEWER}` subagent records a plan review (AS={REVIEWER}). Nothing distinguishes the shells, so this is a declaration, recorded - not a proof.")));
    }
    let Ok(bytes) = std::fs::read(spec_dir.join("plan.md")) else {
        return refused(format!(
            "{} has no plan.md to have reviewed",
            feature_name(spec_dir)
        ));
    };
    if text_of(review, "plan_sha256") != Some(digest(&bytes).as_str()) {
        return refused("plan_sha256 does not match plan.md - the plan changed while it was being reviewed (P1), so this review is of a plan that no longer exists; review it again");
    }
    let Some(decisions) = house_style(review.get("decisions")) else {
        return refused(
            "decisions must be a list (empty when the spec settles everything the plan decides)",
        );
    };
    let verdict = derive_verdict(&decisions)?;
    if let Some(said) = review
        .get("verdict")
        .filter(|v| !v.is_null() && *v != verdict)
    {
        return refused(format!(
            "the input says {} but its rulings make it {verdict} (P2)",
            said.as_str().unwrap_or("")
        ));
    }
    let path = spec_dir.join(RECORD);
    let earlier = if path.is_file() {
        read_json(&path)
    } else {
        json!({})
    };
    let kept = slim_record(&json!({"tasks": earlier.get("tasks").cloned().unwrap_or(json!({}))}));
    let day = when.map_or_else(today, str::to_owned);
    let text = String::from_utf8_lossy(&bytes);
    let per_block: Map<String, Value> = blocks(&text)
        .into_iter()
        .map(|(k, b, _)| {
            (
                k,
                json!({"sha256": block_digest(&b), "verdict": verdict, "reviewed": day}),
            )
        })
        .collect();
    let mut out = Map::new();
    out.insert("feature".to_owned(), Value::from(feature_name(spec_dir)));
    out.insert("plan_sha256".to_owned(), review["plan_sha256"].clone());
    if kept["tasks"].as_object().is_some_and(|t| !t.is_empty()) {
        out.insert("tasks".to_owned(), kept["tasks"].clone());
    }
    out.insert("blocks".to_owned(), Value::Object(per_block));
    out.insert("reviewed".to_owned(), Value::from(day));
    out.insert("declared".to_owned(), Value::from(declared));
    out.insert("decisions".to_owned(), Value::Array(decisions));
    out.insert("verdict".to_owned(), Value::from(verdict));
    let out = Value::Object(out);
    let _ = std::fs::write(path, pretty(&out));
    Ok(out)
}

/// (task, block key) for each task's Decisions block re-reviewed after an earlier CLEAR on it, changed by more than a typo (D9).
fn redecided_tasks(
    plan: &Path,
    before: &Value,
    named: &Map<String, Value>,
) -> Vec<(String, String)> {
    let history = History::new(plan, "HEAD");
    let text = std::fs::read_to_string(plan).unwrap_or_default();
    let bodies = blocks(&text);
    let decisions = re(r"^#{2,4}\s+(T\d+[a-z]?)\s+Decisions\b");
    let re_answered = re(r"^#{2,4}\s+(T\d+[a-z]?)\s+Approach\b.*re-answered");
    let answered: BTreeSet<String> = named
        .keys()
        .filter_map(|k| {
            re_answered
                .captures(k)
                .ok()
                .flatten()
                .map(|c| c[1].to_owned())
        })
        .collect();
    let mut out = Vec::new();
    for (key, sha) in named {
        let Some(task) = decisions
            .captures(key)
            .ok()
            .flatten()
            .map(|c| c[1].to_owned())
        else {
            continue;
        };
        let prior = before.get(key).unwrap_or(&Value::Null);
        let was = text_of(prior, "sha256");
        if answered.contains(&task)
            || text_of(prior, "verdict") != Some("CLEAR")
            || was.is_none()
            || was == sha.as_str()
        {
            continue;
        }
        let body = bodies
            .iter()
            .find(|(k, ..)| k == key)
            .map_or("", |(_, b, _)| b.as_str());
        if history
            .block(key, was.unwrap_or(""))
            .is_none_or(|old| !typo_only(&old, body))
        {
            out.push((task, key.clone()));
        }
    }
    out
}

/// Each named block is in plan.md at the digest the review read.
fn check_named(named: &Map<String, Value>, now: &[(String, String, usize)]) -> Result<(), Stop> {
    for (key, sha) in named {
        if key.starts_with(REMOVED) && sha == "removed" {
            continue;
        }
        let Some((_, body, _)) = now.iter().find(|(k, ..)| k == key) else {
            return refused(format!(
                "plan.md has no block {}",
                crate::checks::py_repr(&Value::from(key.as_str()))
            ));
        };
        if block_digest(body) != sha.as_str().unwrap_or("") {
            let short: String = sha.as_str().unwrap_or("").chars().take(12).collect();
            return refused(format!(
                "{} changed while it was being reviewed - its digest is not {short}",
                crate::checks::py_repr(&Value::from(key.as_str()))
            ));
        }
    }
    Ok(())
}

/// A review of changed blocks (D61): the verdict its decisions derive is each named block's. The return holds what is owed afterwards.
pub(super) fn record_blocks(
    spec_dir: &Path,
    review: &Value,
    declared: &str,
    when: Option<&str>,
) -> Result<Value, Stop> {
    if declared != REVIEWER {
        return Err(Stop::Declined(format!(
            "declined: only the `{REVIEWER}` subagent records a plan review (AS={REVIEWER})"
        )));
    }
    let Some(named) = review
        .get("blocks")
        .and_then(Value::as_object)
        .filter(|n| !n.is_empty())
    else {
        return refused("blocks must name each block reviewed: {\"<heading line>\": \"<sha256>\"}");
    };
    let plan = spec_dir.join("plan.md");
    let text = std::fs::read_to_string(&plan).unwrap_or_default();
    let now = blocks(&text);
    check_named(named, &now)?;
    let Some(decisions) = house_style(review.get("decisions")) else {
        return refused("decisions must be a list (empty when the blocks decide nothing)");
    };
    let verdict = derive_verdict(&decisions)?;
    let mut out = starting_record(spec_dir);
    let day = when.map_or_else(today, str::to_owned);
    let redecided = redecided_tasks(&plan, out.get("blocks").unwrap_or(&json!({})), named);
    let map = out
        .as_object_mut()
        .unwrap_or_else(|| unreachable!("a record is an object"));
    let per_block = map
        .entry("blocks")
        .or_insert(json!({}))
        .as_object_mut()
        .unwrap_or_else(|| unreachable!("blocks is an object"));
    for (key, sha) in named {
        if let Some(gone) = key.strip_prefix(REMOVED) {
            if verdict == "CLEAR" {
                per_block.shift_remove(gone);
            }
        } else {
            per_block.insert(
                key.clone(),
                json!({"sha256": sha, "verdict": verdict, "reviewed": day, "declared": declared}),
            );
        }
    }
    let mut sorted: Vec<&String> = named.keys().collect();
    sorted.sort();
    let row =
        json!({"reviewed": day, "blocks": sorted, "verdict": verdict, "decisions": decisions});
    map.entry("block_reviews")
        .or_insert(json!([]))
        .as_array_mut()
        .unwrap_or_else(|| unreachable!("a list"))
        .push(row);
    let pairs: Vec<(String, String)> = now
        .iter()
        .filter(|(k, ..)| named.contains_key(k))
        .map(|(_, b, _)| (block_digest(b), b.clone()))
        .collect();
    keep(&plan, &pairs);
    let _ = std::fs::write(spec_dir.join(RECORD), pretty(&out));
    let root = spec_dir
        .parent()
        .and_then(Path::parent)
        .unwrap_or(Path::new("."));
    let owed: Vec<String> = if checklist(root).is_some() {
        redecided
            .iter()
            .map(|(t, key)| {
                owe(
                    root,
                    &feature_name(spec_dir),
                    t,
                    &format!("re-decided:{key}"),
                    "A",
                    None,
                )
            })
            .collect()
    } else {
        Vec::new()
    };
    let mut got = json!({"verdict": verdict, "blocks": sorted, "decisions": decisions});
    if !owed.is_empty() {
        got["approach_owed"] = json!(owed);
    }
    Ok(got)
}

/// What an accept recorded (feature 451 T92): the blocks recorded CLEAR, the tasks whose verdict it now is, and whether its question was
/// the whole plan.
#[derive(Debug, Default, PartialEq, Eq)]
pub struct Accepted {
    pub blocks: Vec<String>,
    pub tasks: Vec<String>,
    pub whole: bool,
}

/// The tasks a plan round's question names (feature 451 T92), read from its trigger alone and never from its prose (T33's ask names T49
/// to T51, filed, not asked about): a round trigger's `#<task>`, the task whose rounds the review-round guard counts
/// (`review_round_hooks`), or the task ids of an ask's subject (`ask:451-T79-third-plan-round`, `ask:427-plan-T07-T11`).
fn named_tasks(trigger: &str) -> Vec<String> {
    let words = trigger
        .strip_prefix("round:spec-fidelity|plan:")
        .map_or_else(
            || trigger.strip_prefix("ask:").unwrap_or(trigger),
            |unit| {
                unit.split_once('#')
                    .map_or("", |(_, t)| t.split('@').next().unwrap_or(""))
            },
        );
    let mut named: Vec<String> = Vec::new();
    for id in TASK_ID.find_iter(words).map_while(Result::ok) {
        if !named.iter().any(|t| t == id.as_str()) {
            named.push(id.as_str().to_owned());
        }
    }
    named
}

/// The offsets of `task`'s section in `plan`, as `task_sections` joins it: each heading whose title opens with the id, to the next heading
/// at its level or above; or, with none, the first heading that names it.
fn section_spans(plan: &str, task: &str) -> Vec<(usize, usize)> {
    let heads: Vec<(usize, usize, String)> = l7r_shared::plan_text::HEAD
        .captures_iter(plan)
        .map_while(Result::ok)
        .map(|c| {
            let at = c.get(0).map_or(0, |g| g.start());
            let level = c.get(1).map_or(0, |g| g.as_str().len());
            (at, level, c.get(2).map_or("", |g| g.as_str()).to_owned())
        })
        .collect();
    let span = |i: usize| {
        let (at, level, _) = &heads[i];
        let end = heads[i + 1..]
            .iter()
            .find(|(_, lv, _)| lv <= level)
            .map_or(plan.len(), |(a, ..)| *a);
        (*at, end)
    };
    let own: Vec<(usize, usize)> = (0..heads.len())
        .filter(|i| leading_task(heads[*i].2.trim()) == Some(task))
        .map(span)
        .collect();
    if !own.is_empty() {
        return own;
    }
    (0..heads.len())
        .find(|i| {
            TASK_ID
                .find_iter(&heads[*i].2)
                .map_while(Result::ok)
                .any(|m| m.as_str() == task)
        })
        .map(span)
        .into_iter()
        .collect()
}

/// (the named tasks with a section in plan.md, whether the question is the whole plan's), or None where it names only archived sections.
fn accept_scope(spec_dir: &Path, trigger: &str, text: &str) -> Option<(Vec<String>, bool)> {
    let done = std::fs::read_to_string(spec_dir.join("plan-done.md")).unwrap_or_default();
    let named = named_tasks(trigger);
    let sections = task_sections(text);
    let tasks: Vec<String> = named
        .iter()
        .filter(|t| sections.contains_key(*t))
        .cloned()
        .collect();
    let whole = named.is_empty()
        || (tasks.is_empty() && named.iter().all(|t| !task_sections(&done).contains_key(t)));
    (whole || !tasks.is_empty()).then_some((tasks, whole))
}

/// Each accepted task's verdict CLEAR at its section's digest, the reviewer's entry kept beside it as `accepted_over`.
fn write_task_verdicts(
    map: &mut Map<String, Value>,
    tasks: &[String],
    text: &str,
    decision: &Value,
    day: &str,
) {
    let sections = task_sections(text);
    let verdicts = map
        .entry("tasks")
        .or_insert(json!({}))
        .as_object_mut()
        .unwrap_or_else(|| unreachable!("tasks is an object"));
    for t in tasks {
        let mut entry = json!({"section_sha256": digest(sections[t].as_bytes()), "reviewed": day, "declared": "round-arbiter", "decisions": [decision], "verdict": "CLEAR"});
        // the reviewer's own entry kept beside the accept (an accept over an accept carries the reviewer's forward)
        let over = verdicts.get(t).cloned().and_then(|p| {
            if text_of(&p, "declared") == Some("round-arbiter") {
                p.get("accepted_over").cloned()
            } else {
                Some(p)
            }
        });
        if let Some(over) = over {
            entry["accepted_over"] = over;
        }
        verdicts.insert(t.clone(), entry);
    }
}

/// Past the plan-round cap (feature 385 T16), the round arbiter's accept on the plan round stands as the plan's verdict, recorded CLEAR
/// at each block's digest now - but only for the blocks its question names (feature 451 T92): a question that names tasks (its trigger,
/// [`named_tasks`]) clears the owed or BLOCKED blocks inside those tasks' sections and records each task's verdict CLEAR, declared
/// `round-arbiter`, at its section's digest - the verdict the tick, the push, `plan decided` and the builder-stop guard read - the
/// reviewer's entry kept beside it as `accepted_over`. A question naming no task, or only tasks with no section anywhere (judged by the
/// plan-stage review, as `plan decided` reads them), is the whole plan's: every owed or BLOCKED block. One naming only archived sections
/// (`plan-done.md`) records nothing. WHY: measured 2026-11-21 (plan-review.json's history), `ask:451-T79-third-plan-round` recorded 28
/// blocks CLEAR for a question about T79's section alone - 24 untouched templates, T76's and T77's changed blocks - and left T79's task
/// verdict BLOCKED; T33's, T46's and T67's accepts likewise. Only a ruling the feature's `arbiter.jsonl` records counts.
pub(super) fn arbiter_accept(
    spec_dir: &Path,
    trigger: &str,
    when: Option<&str>,
) -> Result<Accepted, Stop> {
    let lines = std::fs::read_to_string(spec_dir.join("arbiter.jsonl")).unwrap_or_default();
    let rows: Vec<Value> = lines
        .lines()
        .filter(|l| !l.trim().is_empty())
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect();
    let same = |r: &&Value| text_of(r, "trigger") == Some(trigger);
    if !trigger.starts_with("round:spec-fidelity|plan:")
        && !rows
            .iter()
            .filter(same)
            .any(|r| text_of(r, "review") == Some("plan"))
    {
        return refused(format!("{trigger} is not a plan review's round trigger, nor an ask about the plan review (REVIEW=plan)"));
    }
    if !rows
        .iter()
        .filter(same)
        .any(|r| text_of(r, "ruling").is_some_and(|x| ACCEPTS.contains(&x)))
    {
        return Err(Stop::Declined(format!("declined: {}'s arbiter.jsonl holds no accept on {trigger} - only the round arbiter's ruling stands as a verdict", feature_name(spec_dir))));
    }
    let plan = spec_dir.join("plan.md");
    let text = std::fs::read_to_string(&plan).unwrap_or_default();
    let Some((tasks, whole)) = accept_scope(spec_dir, trigger, &text) else {
        return Ok(Accepted::default());
    };
    let spans: Vec<(usize, usize)> = tasks.iter().flat_map(|t| section_spans(&text, t)).collect();
    let asked =
        |at: usize, len: usize| whole || spans.iter().any(|(lo, hi)| *lo <= at && at + len <= *hi);
    let mut out = starting_record(spec_dir);
    let (owed_keys, blocked) = block_status(&out, &text, &BTreeSet::new(), None, "");
    let cleared: Vec<(String, String)> = blocks(&text)
        .into_iter()
        .filter(|(k, b, at)| (owed_keys.contains(k) || blocked.contains(k)) && asked(*at, b.len()))
        .map(|(k, b, _)| (k, b))
        .collect();
    keep(
        &plan,
        &cleared
            .iter()
            .map(|(_, b)| (block_digest(b), b.clone()))
            .collect::<Vec<_>>(),
    );
    let day = when.map_or_else(today, str::to_owned);
    let map = out
        .as_object_mut()
        .unwrap_or_else(|| unreachable!("a record is an object"));
    let per_block = map
        .entry("blocks")
        .or_insert(json!({}))
        .as_object_mut()
        .unwrap_or_else(|| unreachable!("blocks is an object"));
    for (key, body) in &cleared {
        per_block.insert(key.clone(), json!({"sha256": block_digest(body), "verdict": "CLEAR", "reviewed": day, "declared": "round-arbiter"}));
    }
    // a block the plan no longer has goes with the question that names its task, or with the whole plan's
    for key in owed_keys.iter().filter_map(|k| k.strip_prefix(REMOVED)) {
        if whole || leading_task(&heading_text(key)).is_some_and(|t| tasks.iter().any(|x| x == t)) {
            per_block.shift_remove(key);
        }
    }
    let mut sorted: Vec<String> = cleared.into_iter().map(|(k, _)| k).collect();
    sorted.sort();
    let summary = if whole {
        "the round arbiter accepted the plan as it stands".to_owned()
    } else {
        format!(
            "the round arbiter accepted {}'s section as it stands",
            tasks.join(" and ")
        )
    };
    let decision = json!({"id": trigger, "class": "within", "summary": summary});
    let mut row = json!({"reviewed": day, "blocks": sorted, "verdict": "CLEAR", "declared": "round-arbiter", "decisions": [decision]});
    if !whole {
        row["tasks"] = json!(tasks);
    }
    map.entry("block_reviews")
        .or_insert(json!([]))
        .as_array_mut()
        .unwrap_or_else(|| unreachable!("a list"))
        .push(row);
    write_task_verdicts(map, &tasks, &text, &decision, &day);
    let _ = std::fs::write(spec_dir.join(RECORD), pretty(&out));
    Ok(Accepted {
        blocks: sorted,
        tasks,
        whole,
    })
}

#[cfg(test)]
mod tests;
