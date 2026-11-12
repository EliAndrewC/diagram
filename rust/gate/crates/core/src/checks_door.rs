//! A door's loop (feature 449 T86, from `checks_door.rs`, split out by T92): each line on stdin is `{"verb": .., "args": [..]}`, each line on stdout
//! `{"ok": ..}` or `{"error": ".."}`; and the modal batches `report` names, kept for the dispatch guard.

use std::io::{BufRead, Write};
use std::path::Path;

use l7r_guard::shared::checks;
use l7r_guard::shared::pyjson;
use serde_json::{json, Value};

use crate::Reply;

const BATCHES: &str = "modal-batches.json";

/// `record_owed.keep_batches`: the batches `report` names, kept for the dispatch guard, by atomic rename.
///
/// # Errors
///
/// The text of the write or the rename that failed.
pub fn keep_batches(root: &Path, batches: &Value) -> Result<(), String> {
    let common = checks::common_dir(root);
    let body = pyjson::dumps(
        &json!({"utc": checks::now(), "batches": batches}),
        None,
        true,
    ) + "\n";
    let path = common.join(BATCHES);
    let tmp = path.with_extension(format!("{}.tmp", std::process::id()));
    std::fs::write(&tmp, body).map_err(|e| e.to_string())?;
    std::fs::rename(&tmp, &path).map_err(|e| e.to_string())
}

/// A door's verbs: each verb and its arguments to its JSON answer.
pub type Verbs = dyn Fn(&str, &[Value]) -> Result<Value, String>;

/// One request line's reply line, under the door's own verbs.
fn reply_line(line: &str, answer: &Verbs) -> String {
    let parsed: Result<Value, String> = serde_json::from_str(line).map_err(|e| e.to_string());
    let said = parsed.and_then(|req| {
        let args = req
            .get("args")
            .and_then(Value::as_array)
            .cloned()
            .unwrap_or_default();
        answer(req.get("verb").and_then(Value::as_str).unwrap_or(""), &args)
    });
    let shaped = said.map_or_else(|e| json!({"error": e}), |v| json!({"ok": v}));
    pyjson::dumps(&shaped, None, false) + "\n"
}

/// A door's loop over its verbs (`owed-door`; `checks-door` and `claims-door` left with feature 449 T132).
pub fn serve_with(input: &mut dyn BufRead, output: &mut dyn Write, answer: &Verbs) -> Reply {
    let mut line = String::new();
    loop {
        line.clear();
        if input.read_line(&mut line).unwrap_or(0) == 0 {
            return Reply {
                stdout: String::new(),
                stderr: String::new(),
                code: 0,
            };
        }
        if line.trim().is_empty() {
            continue;
        }
        if output
            .write_all(reply_line(&line, answer).as_bytes())
            .and_then(|()| output.flush())
            .is_err()
        {
            return Reply {
                stdout: String::new(),
                stderr: String::new(),
                code: 0,
            };
        }
    }
}

#[cfg(test)]
mod tests;
