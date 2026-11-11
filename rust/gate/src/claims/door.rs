//! Python's door to the claims tools (`l7r-gate claims-door`, `scripts/claims_door.py`; `ask:449-T82-claims`): what `land.py` and
//! `replay_owing.py` read of the port until T83, and `impl_check.py`, a door caller at the phase-3 close. One process a run, no logic of
//! its own, deleted with its last caller.

use std::io::{BufRead, Write};
use std::path::Path;

use serde_json::{json, Map, Value};

use super::index::{current, load_map, owed, Cur, QUESTIONS};
use super::scope::Reader;
use super::seam::{file_left, git_diff, split, CLAIMS_FEATURE_DIR};
use crate::checks_door::serve_with;
use crate::Reply;

fn text(args: &[Value], i: usize) -> String {
    args.get(i)
        .and_then(Value::as_str)
        .unwrap_or_default()
        .to_owned()
}

fn object(args: &[Value], i: usize) -> Map<String, Value> {
    args.get(i)
        .and_then(Value::as_object)
        .cloned()
        .unwrap_or_default()
}

fn strings(args: &[Value], i: usize) -> Vec<String> {
    args.get(i)
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .map(|v| v.as_str().unwrap_or_default().to_owned())
        .collect()
}

fn reader(root: &Path) -> Reader {
    Reader::new(&crate::record::repo::tree_of(root), root)
}

fn read(root: &Path) -> Result<Cur, String> {
    current(&mut reader(root), root, &root.join(QUESTIONS))
}

/// The rows of `current`, each with what a caller reads of its unit and claim.
fn rows_json(cur: &Cur) -> Value {
    let mut out = Map::new();
    for r in cur.iter() {
        let u = &r.unit;
        out.insert(
            r.key.clone(),
            json!({
                "key": r.key, "uid": r.uid(), "code": r.code, "research": r.research,
                "claim": {"label": r.claim.label, "backing": r.claim.backing, "pointers": r.claim.pointers, "account": r.claim.account, "line": r.claim.line},
                "unit": {"path": u.path, "qualname": u.qualname, "kind": u.kind, "lineno": u.lineno, "end_lineno": u.end_lineno,
                         "inherited": u.inherited, "core": u.core, "line_keyed": u.line_keyed()},
            }),
        );
    }
    Value::Object(out)
}

fn answer(verb: &str, args: &[Value]) -> Result<Value, String> {
    let root = Path::new(&text(args, 0)).to_path_buf();
    match verb {
        "current" => Ok(rows_json(&read(&root)?)),
        "owed" => {
            let cur = read(&root)?;
            let (index, store) = (object(args, 1), object(args, 2));
            let due = owed(&cur, &index, Some(&root.join(QUESTIONS)), Some(&store))?;
            Ok(json!(due
                .into_iter()
                .map(|(k, w)| json!([k, w]))
                .collect::<Vec<_>>()))
        }
        "load_index" | "load_store" => Ok(Value::Object(load_map(&root)?)),
        "backfill_sections" => {
            let cur = read(&root)?;
            let (mut index, mut store) = (object(args, 1), object(args, 2));
            let n = super::commands::backfill_sections(&cur, &mut index, &mut store);
            Ok(json!([n, index, store]))
        }
        "scope_split" => {
            let (own, left) = split(
                &mut reader(&root),
                &root,
                &text(args, 1),
                &strings(args, 2),
                &strings(args, 3),
            )?;
            Ok(json!([own, left]))
        }
        "git_diff" => Ok(json!(git_diff(&root, &text(args, 1)))),
        "file_left" => Ok(json!(file_left(&root, &text(args, 1), &strings(args, 2))?)),
        "flight_live" => Ok(json!(super::flight::live(&root, super::flight::now()))),
        "constants" => Ok(
            json!({"CLAIMS_FEATURE_DIR": CLAIMS_FEATURE_DIR, "QUESTIONS": QUESTIONS,
                                 "INDEX": super::index::INDEX, "STORE": super::index::STORE}),
        ),
        other => Err(format!("claims-door: no verb {other}")),
    }
}

/// The door's loop: until stdin closes.
pub fn serve(input: &mut dyn BufRead, output: &mut dyn Write) -> Reply {
    serve_with(input, output, &answer)
}

#[cfg(test)]
mod tests;
