//! `l7r-gate checks-door`: the Python callers' one door to the check state and the arbiter (feature 449 T86, `ask:449-T86-door`). One long-lived process a Python run: each line on stdin is `{"verb": .., "args": [..]}`, each
//! line on stdout `{"ok": ..}` or `{"error": ".."}`, so a run's reads follow its own writes in order (FR-006). It forwards and holds no logic of its own: the writes (`record_answer`, `trip`, `keep_batches`) are the same Rust
//! the guards call, under the same locks. `l7r-gate checks-close` is what `make check-closed` runs.

use std::io::{BufRead, Write};
use std::path::{Path, PathBuf};

use l7r_guard::shared::checks;
use l7r_guard::shared::checks::{arbiter as core, handle, reply, rounds};
use serde_json::{json, Value};

use crate::Reply;
pub use l7r_gate_core::checks_door::*;

fn arg(args: &[Value], i: usize) -> &str {
    args.get(i).and_then(Value::as_str).unwrap_or("")
}

fn path_arg(args: &[Value], i: usize) -> PathBuf {
    PathBuf::from(arg(args, i))
}

fn path_json(p: Option<PathBuf>) -> Value {
    p.map_or(Value::Null, |d| json!(d.to_string_lossy()))
}

fn strings(v: Option<&Value>) -> Vec<String> {
    v.and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|s| s.as_str().map(str::to_owned))
        .collect()
}

fn triple(b: &(String, String, String)) -> Value {
    json!([b.0, b.1, b.2])
}

/// One verb's answer.
fn answer(verb: &str, args: &[Value]) -> Result<Value, String> {
    Ok(match verb {
        "load" => checks::load(Path::new(arg(args, 0))),
        "state_path" => path_json(checks::state_path(arg(args, 0))),
        "_blocks" => Value::Array(reply::blocks(arg(args, 0)).iter().map(triple).collect()),
        "_reply_of" => json!(reply::reply_of(arg(args, 0), arg(args, 1))),
        "ROUND_CAP" => json!(rounds::ROUND_CAP),
        "PAGE_CHECKS" => json!(rounds::PAGE_CHECKS),
        "subject_of_path" => json!(rounds::subject_of_path(arg(args, 0))),
        "notes_of_manifest" => json!(rounds::notes_of_manifest(arg(args, 0))),
        "subjects_of_manifest" => json!(rounds::subjects_of_manifest(arg(args, 0))),
        "feature_dir" => path_json(core::feature_dir(&path_arg(args, 0), arg(args, 1))),
        "unit_of" => json!(core::unit_of(arg(args, 0))),
        "owed" => Value::Object(core::owed(&path_arg(args, 0))),
        "aside" => json!(core::aside(&path_arg(args, 0))),
        "rulings" => Value::Object(core::rulings(&path_arg(args, 0), arg(args, 1))),
        "_round_no" => json!(core::round_no(arg(args, 0))),
        "batch_triggers" => json!(core::batch_triggers(
            &path_arg(args, 0),
            &strings(args.get(1))
        )),
        "reversal" => json!(core::reversal(
            args.first()
                .and_then(Value::as_array)
                .map_or(&[][..], Vec::as_slice),
            arg(args, 1),
            arg(args, 2),
            arg(args, 3)
        )),
        "fix_hold" => json!(crate::arbiter::fix_hold(Path::new(arg(args, 0)))),
        "record_answer" => {
            rounds::record_answer(&path_arg(args, 0), arg(args, 1), &strings(args.get(2)));
            Value::Null
        }
        "trip" => json!(core::try_trip(
            &path_arg(args, 0),
            arg(args, 1),
            arg(args, 2),
            arg(args, 3),
            arg(args, 4),
            args.get(5).unwrap_or(&Value::Null),
            arg(args, 6),
        )?),
        "keep_batches" => {
            keep_batches(&path_arg(args, 0), args.get(1).unwrap_or(&Value::Null))?;
            Value::Null
        }
        // the reviews' port (T89, `ask:449-T89-reviews`): `tick-task.py`'s hold and `review_snapshot.py`'s owed units
        "review_hold" => json!(crate::reviews::checkpoint::hold(&path_arg(args, 0), None)),
        "review_owed" => {
            let (desc, units, problems) = crate::reviews::owed::owed(&path_arg(args, 0), true);
            let units: Vec<Value> = units
                .iter()
                .map(|u| json!({"slug": u.slug(), "check": u.check, "subject": u.subject, "on": u.on, "occasion": u.occasion}))
                .collect();
            json!([desc, units, problems])
        }
        other => return Err(format!("checks-door: no verb {other}")),
    })
}

/// The door's loop: until stdin closes.
pub fn serve(input: &mut dyn BufRead, output: &mut dyn Write) -> Reply {
    serve_with(input, output, &answer)
}

/// `make check-closed SUBJECT= REASON= [AGENT=]`.
#[must_use]
pub fn close_cli(args: &[String]) -> Reply {
    if !matches!(args.len(), 2 | 3) {
        return Reply {
            stdout: String::new(),
            stderr: "usage: l7r-gate checks-close <subject> <reason> [agent]\n".to_owned(),
            code: 2,
        };
    }
    let root = std::env::current_dir().unwrap_or_default();
    let (code, stdout, stderr) = handle::close(
        &root,
        &args[0],
        &args[1],
        checks::now(),
        args.get(2).map_or("", String::as_str),
    );
    Reply {
        stdout,
        stderr,
        code,
    }
}

#[cfg(test)]
mod tests;
