//! `record merge-answers <queue-clone> <root>` (feature 449 T87): a queue's check answers brought home at a pull (`scripts/pages/pull-queue.sh`), the one writer of the answer store besides `record owed`. A unit this clone never answered is copied; one both answered keeps every fingerprint either answered and the newer record, written by atomic rename. Replaces that script's `jq` merge.

use std::cmp::Ordering;
use std::path::{Path, PathBuf};

use l7r_guard::shared::pyjson;
use serde_json::{json, Map, Value};

use crate::Reply;

/// `.answered // []` of a record: null and false are the alternative.
fn alternative_list(rec: &Map<String, Value>) -> Option<Vec<Value>> {
    match rec.get("answered") {
        None | Some(Value::Null | Value::Bool(false)) => Some(Vec::new()),
        Some(Value::Array(items)) => Some(items.clone()),
        Some(_) => None,
    }
}

/// `.utc // ""`.
fn utc_of(rec: &Map<String, Value>) -> Value {
    match rec.get("utc") {
        None | Some(Value::Null | Value::Bool(false)) => json!(""),
        Some(other) => other.clone(),
    }
}

/// jq's `>` across the types a record's `utc` can be: strings by text, numbers by value, everything else by its type's rank.
fn jq_greater(a: &Value, b: &Value) -> bool {
    match (a, b) {
        (Value::String(x), Value::String(y)) => x > y,
        (Value::Number(x), Value::Number(y)) => {
            x.as_f64().unwrap_or(0.0) > y.as_f64().unwrap_or(0.0)
        }
        _ => type_rank(a) > type_rank(b),
    }
}

/// jq's type order: null, false, true, number, string, array, object.
fn type_rank(value: &Value) -> u8 {
    match value {
        Value::Null => 0,
        Value::Bool(false) => 1,
        Value::Bool(true) => 2,
        Value::Number(_) => 3,
        Value::String(_) => 4,
        Value::Array(_) => 5,
        Value::Object(_) => 6,
    }
}

/// jq's order over the values of an `answered` list, for `unique`.
fn jq_order(a: &Value, b: &Value) -> Ordering {
    match (a, b) {
        (Value::String(x), Value::String(y)) => x.cmp(y),
        (Value::Number(x), Value::Number(y)) => x
            .as_f64()
            .partial_cmp(&y.as_f64())
            .unwrap_or(Ordering::Equal),
        _ => type_rank(a).cmp(&type_rank(b)),
    }
}

/// The merged record: `$m` with `answered` the unique union, and, where the queue's record is newer, its `fingerprint`, `result` and `utc`.
fn merged(mine: &Map<String, Value>, queue: &Map<String, Value>) -> Option<Map<String, Value>> {
    let mut all = alternative_list(mine)?;
    all.extend(alternative_list(queue)?);
    all.sort_by(jq_order);
    all.dedup_by(|a, b| jq_order(a, b) == Ordering::Equal && a == b);
    let mut out = mine.clone();
    out.insert("answered".to_owned(), Value::Array(all));
    if jq_greater(&utc_of(queue), &utc_of(mine)) {
        for key in ["fingerprint", "result", "utc"] {
            out.insert(
                key.to_owned(),
                queue.get(key).cloned().unwrap_or(Value::Null),
            );
        }
    }
    Some(out)
}

fn read_map(path: &Path) -> Option<Map<String, Value>> {
    let text = std::fs::read_to_string(path).ok()?;
    serde_json::from_str::<Value>(&text)
        .ok()?
        .as_object()
        .cloned()
}

/// The queue's store files, in file-name order, as the shell's glob lists them.
fn queue_files(store: &Path) -> Vec<PathBuf> {
    let mut files: Vec<PathBuf> = std::fs::read_dir(store)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| p.extension().is_some_and(|x| x == "json"))
        .collect();
    files.sort();
    files
}

/// One queue file's fate. A file jq cannot merge (not an object, a bad `answered`) leaves `$m` as it was and an empty `$m.tmp`, as the shell left it.
fn merge_one(source: &Path, target: &Path) -> std::io::Result<()> {
    if !target.is_file() {
        std::fs::copy(source, target)?;
        return Ok(());
    }
    let tmp = PathBuf::from(format!("{}.tmp", target.display()));
    let parsed = read_map(target)
        .zip(read_map(source))
        .and_then(|(m, q)| merged(&m, &q));
    let Some(out) = parsed else {
        std::fs::write(&tmp, "")?;
        return Ok(());
    };
    let body = pyjson::dumps(&Value::Object(out), Some(2), false) + "\n";
    std::fs::write(&tmp, body)?;
    std::fs::rename(&tmp, target)
}

/// Merge every record of the queue clone's store into `root`'s.
pub(super) fn cli(args: &[String]) -> Reply {
    let (Some(queue), Some(root)) = (args.first(), args.get(1)) else {
        return Reply {
            stdout: String::new(),
            stderr: "usage: l7r-gate record merge-answers <queue-clone> <root>\n".to_owned(),
            code: 2,
        };
    };
    let from = Path::new(queue).join(".git/record-checks");
    if !from.is_dir() {
        return Reply {
            stdout: String::new(),
            stderr: String::new(),
            code: 0,
        };
    }
    let to = Path::new(root).join(".git/record-checks");
    if let Err(why) = std::fs::create_dir_all(&to) {
        return Reply {
            stdout: String::new(),
            stderr: format!("merge-answers: {why}\n"),
            code: 1,
        };
    }
    let failed: Vec<String> = queue_files(&from)
        .iter()
        .filter_map(|f| {
            let name = f.file_name()?;
            merge_one(f, &to.join(name))
                .err()
                .map(|e| format!("merge-answers: {}: {e}\n", name.to_string_lossy()))
        })
        .collect();
    Reply {
        stdout: String::new(),
        stderr: failed.concat(),
        code: i32::from(!failed.is_empty()),
    }
}
