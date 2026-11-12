//! Python's door to the claims tools (`l7r-gate claims-door`, `scripts/claims_door.py`; `ask:449-T82-claims`): what `impl_check.py` reads
//! of the port, a door caller at the phase-3 close. Feature 449 T121 took the verbs only `land.py` and `replay_owing.py` asked
//! (`backfill_sections`, `git_diff`, `scope_split`, `file_left`, `flight_live`, `CLAIMS_FEATURE_DIR`): both are Rust, asking the claims in
//! process. One process a run, no logic of its own, deleted with its last caller.

use std::io::{BufRead, Write};
use std::path::Path;

use serde_json::{json, Map, Value};

use super::index::{current, load_map, Cur, QUESTIONS};
use super::scope::Reader;
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
            let due = super::owed_at(&root, &object(args, 1), &object(args, 2))?;
            Ok(json!(due
                .into_iter()
                .map(|(k, w)| json!([k, w]))
                .collect::<Vec<_>>()))
        }
        "load_index" | "load_store" => Ok(Value::Object(load_map(&root)?)),
        "constants" => Ok(json!({"QUESTIONS": QUESTIONS,
                                 "INDEX": super::index::INDEX, "STORE": super::index::STORE})),
        other => Err(format!("claims-door: no verb {other}")),
    }
}

/// The door's loop: until stdin closes.
pub fn serve(input: &mut dyn BufRead, output: &mut dyn Write) -> Reply {
    serve_with(input, output, &answer)
}

#[cfg(test)]
mod tests;
